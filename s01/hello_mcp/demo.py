"""s01 / hello_mcp — minimal MCP server + client, capability audit, N x M counter.

Lesson mapping: Section 1, Lessons 1-4.
What it does:
  1. In-process JSON-RPC 2.0: initialize handshake, tools/list, tools/call
  2. Tools that actually compute: add, word_count
  3. capability_audit: which perceive/change needs exist as tools today
  4. nxm_counts: bespoke N*M vs standard N+M integrations
"""

from __future__ import annotations

import json

PROTOCOL_VERSION = "2025-03-26"
SERVER_INFO = {"name": "hello-mcp", "version": "1.0.0"}

TOOL_DEFS = [
    {
        "name": "add",
        "description": "Add two numbers and return their sum.",
        "inputSchema": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
    {
        "name": "word_count",
        "description": "Count the whitespace-separated words in a text string.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]


def make_request(req_id, method, params=None):
    """Build a JSON-RPC 2.0 request dict with jsonrpc/id/method/params keys."""
    return {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}


def make_result(req_id, result):
    """Build a JSON-RPC 2.0 success response dict for the given request id."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id, code, message):
    """Build a JSON-RPC 2.0 error response dict with a structured error object."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _tool_add(args):
    return {"sum": args["a"] + args["b"]}


def _tool_word_count(args):
    text = args["text"]
    words = text.split() if text.strip() else []
    return {"count": len(words), "text": text}


_TOOL_HANDLERS = {"add": _tool_add, "word_count": _tool_word_count}


class HelloMCPServer:
    """Minimal MCP server speaking JSON-RPC 2.0 dicts in-process."""

    def __init__(self):
        self.name = SERVER_INFO["name"]
        self.version = SERVER_INFO["version"]
        self.initialized = False

    def handle(self, request):
        """Dispatch one JSON-RPC request dict and return the response dict."""
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return make_error((request or {}).get("id") if isinstance(request, dict) else None,
                              -32600, "Invalid Request: jsonrpc must be '2.0'")
        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params") or {}
        if method == "initialize":
            return make_result(req_id, self.initialize(params))
        if method == "notifications/initialized":
            self.initialized = True
            return None
        if method == "tools/list":
            return make_result(req_id, {"tools": list(TOOL_DEFS)})
        if method == "tools/call":
            return self._call_tool(req_id, params)
        if method == "ping":
            return make_result(req_id, {})
        return make_error(req_id, -32601, f"Method not found: {method}")

    def initialize(self, params=None):
        """Perform the initialize handshake and return the server's result dict."""
        params = params or {}
        self.initialized = True
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": dict(SERVER_INFO),
            "clientProtocolVersion": params.get("protocolVersion"),
        }

    def list_tools(self):
        """Return the list of tool definition dicts this server exposes."""
        return list(TOOL_DEFS)

    def call_tool(self, name, args):
        """Call a tool by name with an args dict and return its result dict."""
        resp = self._call_tool(0, {"name": name, "arguments": args or {}})
        if "error" in resp:
            raise ValueError(resp["error"]["message"])
        return resp["result"]["structured"]

    def _call_tool(self, req_id, params):
        name = params.get("name")
        args = params.get("arguments") or {}
        handler = _TOOL_HANDLERS.get(name)
        if handler is None:
            return make_error(req_id, -32602, f"Unknown tool: {name}")
        try:
            structured = handler(args)
        except KeyError as exc:
            return make_error(req_id, -32602, f"Missing argument: {exc}")
        except Exception as exc:  # structured error, never a raw leak
            return make_error(req_id, -32603, f"Tool error: {type(exc).__name__}")
        text = json.dumps(structured, sort_keys=True)
        return make_result(req_id, {
            "content": [{"type": "text", "text": text}],
            "structured": structured,
            "isError": False,
        })


class HelloMCPClient:
    """In-process MCP client: initialize handshake, tools/list, tools/call."""

    def __init__(self, server=None):
        self.server = server or HelloMCPServer()
        self._next_id = 1
        self.handshake = None

    def _send(self, method, params=None):
        req = make_request(self._next_id, method, params)
        self._next_id += 1
        return self.server.handle(req)

    def initialize(self):
        """Send initialize with client info and return the server's handshake result dict."""
        resp = self._send("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "hello-client", "version": "1.0.0"},
        })
        self.handshake = resp["result"]
        self.server.handle({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        return self.handshake

    def list_tools(self):
        """Return the list of tool definition dicts from tools/list."""
        resp = self._send("tools/list", {})
        return resp["result"]["tools"]

    def call_tool(self, name, args):
        """Call a tool via tools/call and return its structured result dict."""
        resp = self._send("tools/call", {"name": name, "arguments": args})
        if "error" in resp:
            raise ValueError(resp["error"]["message"])
        return resp["result"]["structured"]


def capability_audit(use_case):
    """Audit a use case: return perceive/change lists plus covered/missing vs available tools.

    use_case keys: "perceive" (list), "change" (list),
    "available_tools" (list; alias "tools" also accepted).
    Returns dict with perceive, change, available_tools (sorted), covered,
    missing, total_needed, covered_count. Order follows perceive then change.
    """
    use_case = use_case or {}
    perceive = list(use_case.get("perceive") or [])
    change = list(use_case.get("change") or [])
    raw_tools = use_case.get("available_tools", use_case.get("tools") or [])
    tools = set(raw_tools)
    needed = perceive + change
    covered = [item for item in needed if item in tools]
    missing = [item for item in needed if item not in tools]
    return {
        "perceive": perceive,
        "change": change,
        "available_tools": sorted(tools),
        "covered": covered,
        "missing": missing,
        "total_needed": len(needed),
        "covered_count": len(covered),
    }


def nxm_counts(n_apps, m_tools):
    """Return (bespoke, standard) integration counts: (n_apps*m_tools, n_apps+m_tools)."""
    return (n_apps * m_tools, n_apps + m_tools)


# Fixture from Lesson 3: an invoice-support agent.
USE_CASE_FIXTURE = {
    "perceive": ["read_invoice", "read_account"],
    "change": ["file_report", "update_ticket"],
    "available_tools": ["read_invoice", "update_ticket"],
}


def main():
    client = HelloMCPClient()
    handshake = client.initialize()
    assert handshake["protocolVersion"] == PROTOCOL_VERSION
    assert handshake["serverInfo"]["name"] == "hello-mcp"
    print("hello_mcp: initialize handshake")
    print(f"  protocolVersion: {handshake['protocolVersion']}")
    print(f"  server: {handshake['serverInfo']['name']} {handshake['serverInfo']['version']}")
    print(f"  capabilities: {sorted(handshake['capabilities'].keys())}")

    tools = client.list_tools()
    names = [t["name"] for t in tools]
    assert names == ["add", "word_count"], names
    print(f"  tools/list: {names}")

    result = client.call_tool("add", {"a": 19, "b": 23})
    assert result == {"sum": 42}, result
    print(f"  tools/call add(a=19, b=23) -> sum={result['sum']}")

    wc = client.call_tool("word_count", {"text": "agents need hands not just words"})
    assert wc["count"] == 6, wc
    print(f"  tools/call word_count('agents need hands not just words') -> count={wc['count']}")

    audit = capability_audit(USE_CASE_FIXTURE)
    assert audit["covered"] == ["read_invoice", "update_ticket"], audit
    assert audit["missing"] == ["read_account", "file_report"], audit
    print("capability audit (invoice-support use case):")
    print(f"  perceive: {audit['perceive']}")
    print(f"  change:   {audit['change']}")
    print(f"  covered ({audit['covered_count']}/{audit['total_needed']}): {audit['covered']}")
    print(f"  missing:  {audit['missing']}")

    bespoke, standard = nxm_counts(5, 3)
    assert (bespoke, standard) == (15, 8), (bespoke, standard)
    print(f"N x M example: 5 apps x 3 tools -> bespoke={bespoke} (5x3=15) vs standard={standard} (5+3=8)")

    print("hello_mcp demo: OK")


if __name__ == "__main__":
    main()
