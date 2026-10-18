"""s02 / fundamentals — discovery, three roles, primitive sorter, handshake.

Lesson mapping: Section 2, Lessons 5-8.
What it does:
  1. Sample server: 2 tools, 2 resources, 1 prompt over JSON-RPC 2.0
  2. discover(): list all three primitive sets exactly as a client sees them
  3. three_role_trace(): who owns each decision, host -> client -> server
  4. classify_primitive(): tool / resource / prompt by who decides
  5. handshake_capture(): negotiated intersection of client/server caps
"""

from __future__ import annotations

import json

SUPPORTED_VERSIONS = ["2024-11-05", "2025-03-26", "2025-06-18"]

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
        "name": "greet",
        "description": "Build a greeting string for a name.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
]

RESOURCE_DEFS = [
    {"uri": "notes://welcome", "name": "Welcome Notes", "mimeType": "text/plain"},
    {"uri": "data://server-config", "name": "Server Config", "mimeType": "application/json"},
]

RESOURCE_CONTENTS = {
    "notes://welcome": "Welcome to the fundamentals sample server.",
    "data://server-config": '{"region": "local", "mode": "demo"}',
}

PROMPT_DEFS = [
    {
        "name": "daily_brief",
        "description": "Build a daily briefing prompt for a topic.",
        "arguments": [{"name": "topic", "description": "Briefing topic", "required": True}],
    }
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


class FundamentalsServer:
    """Sample MCP server exposing 2 tools, 2 resources, and 1 prompt."""

    def __init__(self):
        self.name = "fundamentals-sample"
        self.version = "1.0.0"

    def handle(self, request):
        """Dispatch one JSON-RPC request dict and return the response dict."""
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return make_error(None, -32600, "Invalid Request: jsonrpc must be '2.0'")
        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params") or {}
        if method == "initialize":
            return make_result(req_id, {
                "protocolVersion": SUPPORTED_VERSIONS[-1],
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "serverInfo": {"name": self.name, "version": self.version},
            })
        if method == "tools/list":
            return make_result(req_id, {"tools": list(TOOL_DEFS)})
        if method == "resources/list":
            return make_result(req_id, {"resources": list(RESOURCE_DEFS)})
        if method == "resources/read":
            uri = params.get("uri")
            if uri not in RESOURCE_CONTENTS:
                return make_error(req_id, -32602, f"Unknown resource: {uri}")
            mime = next(r["mimeType"] for r in RESOURCE_DEFS if r["uri"] == uri)
            return make_result(req_id, {"contents": [
                {"uri": uri, "mimeType": mime, "text": RESOURCE_CONTENTS[uri]}]})
        if method == "prompts/list":
            return make_result(req_id, {"prompts": list(PROMPT_DEFS)})
        if method == "prompts/get":
            if params.get("name") != "daily_brief":
                return make_error(req_id, -32602, f"Unknown prompt: {params.get('name')}")
            topic = (params.get("arguments") or {}).get("topic", "general")
            return make_result(req_id, {"description": PROMPT_DEFS[0]["description"],
                                        "messages": [{"role": "user", "content": {
                                            "type": "text",
                                            "text": f"Prepare a daily brief on {topic}."}}]})
        if method == "tools/call":
            return self._call_tool(req_id, params)
        if method == "ping":
            return make_result(req_id, {})
        return make_error(req_id, -32601, f"Method not found: {method}")

    def _call_tool(self, req_id, params):
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == "add":
            structured = {"sum": args["a"] + args["b"]}
        elif name == "greet":
            structured = {"greeting": f"Hello, {args['name']}!"}
        else:
            return make_error(req_id, -32602, f"Unknown tool: {name}")
        return make_result(req_id, {
            "content": [{"type": "text", "text": json.dumps(structured, sort_keys=True)}],
            "structured": structured, "isError": False})


class FundamentalsClient:
    """In-process MCP client used by discover() and the demo."""

    def __init__(self, server=None):
        self.server = server or FundamentalsServer()
        self._next_id = 1

    def _send(self, method, params=None):
        req = make_request(self._next_id, method, params)
        self._next_id += 1
        return self.server.handle(req)

    def request(self, method, params=None):
        """Send one JSON-RPC method and return its result dict (raises on error)."""
        resp = self._send(method, params)
        if resp and "error" in resp:
            raise ValueError(resp["error"]["message"])
        return resp["result"] if resp else {}

    def initialize(self):
        """Perform the initialize handshake and return the server's result dict."""
        return self.request("initialize", {
            "protocolVersion": SUPPORTED_VERSIONS[-1], "capabilities": {},
            "clientInfo": {"name": "fundamentals-client", "version": "1.0.0"}})

    def list_tools(self):
        """Return the tool definition dicts from tools/list."""
        return self.request("tools/list", {})["tools"]

    def list_resources(self):
        """Return the resource definition dicts from resources/list."""
        return self.request("resources/list", {})["resources"]

    def list_prompts(self):
        """Return the prompt definition dicts from prompts/list."""
        return self.request("prompts/list", {})["prompts"]

    def call_tool(self, name, args):
        """Call a tool via tools/call and return its structured result dict."""
        return self.request("tools/call", {"name": name, "arguments": args})["structured"]


def discover(client):
    """List all primitives: return tools (names), resources (URIs), prompts (names), counts.

    Accepts a FundamentalsClient (or any object with list_tools/list_resources/
    list_prompts). Returns {"tools": [...], "resources": [...], "prompts": [...],
    "counts": {"tools": int, "resources": int, "prompts": int}} in server order.
    """
    tools = client.list_tools()
    resources = client.list_resources()
    prompts = client.list_prompts()
    tool_names = [t["name"] for t in tools]
    resource_uris = [r["uri"] for r in resources]
    prompt_names = [p["name"] for p in prompts]
    return {
        "tools": tool_names,
        "resources": resource_uris,
        "prompts": prompt_names,
        "counts": {"tools": len(tool_names), "resources": len(resource_uris),
                   "prompts": len(prompt_names)},
    }


def three_role_trace(request):
    """Trace one request through host, client, server as (component, decision) tuples.

    request is a dict like {"user_text": str, "tool": str}. The returned list
    always starts with a host step, then a client step, then a server step,
    then client and host return steps (5 steps total).
    """
    request = request or {}
    tool = request.get("tool", "add")
    user_text = request.get("user_text", "")
    return [
        ("host", f"owns the user experience and trust decision for request: {user_text!r}"),
        ("client", f"negotiates the session and routes the {tool} call to the server"),
        ("server", f"executes tool {tool} and returns a structured result"),
        ("client", "validates the response id and passes the result to the host"),
        ("host", "presents the result to the user and owns the final answer"),
    ]


_WHO_TO_PRIMITIVE = {
    "model": "tool",
    "application": "resource",
    "app": "resource",
    "host": "resource",
    "user": "prompt",
}


def classify_primitive(capability):
    """Classify a capability as "tool"|"resource"|"prompt" by who decides.

    Reads the first present of capability["who_decides"], ["decided_by"],
    ["control"], ["controller"], lowercased: model -> tool,
    application/app/host -> resource, user -> prompt.
    Raises ValueError when no decider field is present or recognised.
    """
    capability = capability or {}
    who = None
    for key in ("who_decides", "decided_by", "control", "controller"):
        if capability.get(key):
            who = str(capability[key]).strip().lower()
            break
    if who not in _WHO_TO_PRIMITIVE:
        raise ValueError(f"Cannot classify capability without a recognised decider: {capability!r}")
    return _WHO_TO_PRIMITIVE[who]


def _caps_of(side):
    """Normalise a caps dict into (versions list, capability-names set)."""
    side = side or {}
    versions = side.get("protocol_versions") or side.get("protocolVersions") or []
    if isinstance(versions, str):
        versions = [versions]
    caps = side.get("capabilities") or {}
    if isinstance(caps, dict):
        names = set(caps.keys())
    elif isinstance(caps, (list, tuple, set)):
        names = set(caps)
    else:
        names = set()
    return list(versions), names


def handshake_capture(client_caps, server_caps):
    """Capture a handshake: return the negotiated intersection of two cap dicts.

    Each side is {"protocol_versions": [...], "capabilities": {...} or [...]}.
    The negotiated protocol version is the highest (lexicographic max, which
    orders ISO dates correctly) version present on both sides, or None.
    Returns {"protocol_version": str|None, "capabilities": sorted list of
    shared capability names, "client_capabilities": sorted list,
    "server_capabilities": sorted list, "common_versions": sorted list}.
    """
    client_versions, client_names = _caps_of(client_caps)
    server_versions, server_names = _caps_of(server_caps)
    common_versions = sorted(set(client_versions) & set(server_versions))
    negotiated = common_versions[-1] if common_versions else None
    shared = sorted(client_names & server_names)
    return {
        "protocol_version": negotiated,
        "capabilities": shared,
        "client_capabilities": sorted(client_names),
        "server_capabilities": sorted(server_names),
        "common_versions": common_versions,
    }


SAMPLE_CAPABILITIES = [
    {"name": "run_report", "who_decides": "model"},
    {"name": "account_record", "who_decides": "application"},
    {"name": "weekly_review_template", "who_decides": "user"},
]

CLIENT_CAPS_FIXTURE = {
    "protocol_versions": ["2024-11-05", "2025-03-26", "2025-06-18"],
    "capabilities": {"sampling": {}, "roots": {}, "tools": {}},
}
SERVER_CAPS_FIXTURE = {
    "protocol_versions": ["2025-03-26", "2025-06-18"],
    "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
}


def main():
    client = FundamentalsClient()
    init = client.initialize()
    print(f"fundamentals: sample server {init['serverInfo']['name']} "
          f"protocol {init['protocolVersion']}")

    found = discover(client)
    assert found["counts"] == {"tools": 2, "resources": 2, "prompts": 1}, found
    print("discovery (as a client sees it):")
    print(f"  tools:     {found['tools']}")
    print(f"  resources: {found['resources']}")
    print(f"  prompts:   {found['prompts']}")
    print(f"  counts:    tools={found['counts']['tools']} "
          f"resources={found['counts']['resources']} prompts={found['counts']['prompts']}")

    result = client.call_tool("greet", {"name": "MCP learner"})
    assert result == {"greeting": "Hello, MCP learner!"}, result
    print(f"  tools/call greet(name='MCP learner') -> {result['greeting']}")

    trace = three_role_trace({"user_text": "Greet the learner", "tool": "greet"})
    assert [step[0] for step in trace[:3]] == ["host", "client", "server"], trace
    print("three-role trace:")
    for component, decision in trace:
        print(f"  {component:>6}: {decision}")

    print("primitive sorter (who decides):")
    for cap in SAMPLE_CAPABILITIES:
        kind = classify_primitive(cap)
        print(f"  {cap['name']}: who_decides={cap['who_decides']} -> {kind}")
    assert [classify_primitive(c) for c in SAMPLE_CAPABILITIES] == ["tool", "resource", "prompt"]

    negotiated = handshake_capture(CLIENT_CAPS_FIXTURE, SERVER_CAPS_FIXTURE)
    assert negotiated["protocol_version"] == "2025-06-18", negotiated
    assert negotiated["capabilities"] == ["tools"], negotiated
    print("handshake capture:")
    print(f"  common versions: {negotiated['common_versions']}")
    print(f"  negotiated protocolVersion: {negotiated['protocol_version']}")
    print(f"  shared capabilities: {negotiated['capabilities']}")
    print(f"  client capabilities: {negotiated['client_capabilities']}")
    print(f"  server capabilities: {negotiated['server_capabilities']}")

    print("fundamentals demo: OK")


if __name__ == "__main__":
    main()
