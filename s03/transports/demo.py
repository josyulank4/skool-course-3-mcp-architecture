"""s03 / transports — one server, two transports: stdio and Streamable HTTP.

Lesson mapping: Section 3, Lessons 9-12.
What it does:
  1. ONE server implementation (tools: echo, add) with a JSON-RPC 2.0 handle()
  2. stdio: this file re-invoked as a subprocess speaking NDJSON on stdin/stdout
  3. HTTP: ThreadingHTTPServer on an ephemeral localhost port, POST JSON-RPC
  4. anatomy_inspector + concurrent round_trip_trace (3 threaded calls, id check)
Logging goes to stderr only — stdout belongs to the protocol on stdio.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROTOCOL_VERSION = "2025-03-26"
SERVER_INFO = {"name": "transports-sample", "version": "1.0.0"}
METHODS = ["initialize", "tools/list", "tools/call", "ping"]

TOOL_DEFS = [
    {
        "name": "echo",
        "description": "Echo a message back unchanged.",
        "inputSchema": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
    },
    {
        "name": "add",
        "description": "Add two numbers and return their sum.",
        "inputSchema": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    },
]


def log(*args):
    """Write a log line to stderr only (stdout is the protocol channel)."""
    print(*args, file=sys.stderr)


def make_request(req_id, method, params=None):
    """Build a JSON-RPC 2.0 request dict with jsonrpc/id/method/params keys."""
    return {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}


def make_result(req_id, result):
    """Build a JSON-RPC 2.0 success response dict for the given request id."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id, code, message):
    """Build a JSON-RPC 2.0 error response dict with a structured error object."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


class TransportServer:
    """The single server implementation shared by both transports."""

    def __init__(self):
        self.name = SERVER_INFO["name"]
        self.version = SERVER_INFO["version"]

    def initialize(self, params=None):
        """Return the initialize handshake result dict."""
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": dict(SERVER_INFO),
        }

    def list_tools(self):
        """Return the list of tool definition dicts (echo, add)."""
        return list(TOOL_DEFS)

    def call_tool(self, name, args):
        """Call a tool by name and return its structured result dict."""
        args = args or {}
        if name == "echo":
            return {"echo": args["message"]}
        if name == "add":
            return {"sum": args["a"] + args["b"]}
        raise ValueError(f"Unknown tool: {name}")

    def handle(self, request):
        """Dispatch one JSON-RPC request dict and return the response dict."""
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            bad_id = request.get("id") if isinstance(request, dict) else None
            return make_error(bad_id, -32600, "Invalid Request: jsonrpc must be '2.0'")
        method = request.get("method")
        req_id = request.get("id")
        params = request.get("params") or {}
        if method == "initialize":
            return make_result(req_id, self.initialize(params))
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return make_result(req_id, {"tools": self.list_tools()})
        if method == "tools/call":
            try:
                structured = self.call_tool(params.get("name"), params.get("arguments") or {})
            except ValueError as exc:
                return make_error(req_id, -32602, str(exc))
            except KeyError as exc:
                return make_error(req_id, -32602, f"Missing argument: {exc}")
            return make_result(req_id, {
                "content": [{"type": "text", "text": json.dumps(structured, sort_keys=True)}],
                "structured": structured, "isError": False})
        if method == "ping":
            return make_result(req_id, {})
        return make_error(req_id, -32601, f"Method not found: {method}")


# ------------------------------------------------------------ stdio mode
def run_stdio_server():
    """Serve newline-delimited JSON-RPC on stdin/stdout; log to stderr only."""
    server = TransportServer()
    log("[stdio-server] ready")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            log("[stdio-server] ignoring non-JSON line")
            continue
        response = server.handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
    log("[stdio-server] stdin closed, exiting")
    return 0


def stdio_session(requests, timeout=15):
    """Run one stdio session: spawn this file with --stdio-server, send requests, return responses.

    requests is a list of JSON-RPC request dicts. Returns the list of response
    dicts in send order (notifications produce no response and are skipped).
    The subprocess is always terminated before returning.
    """
    proc = subprocess.Popen(
        [sys.executable, __file__, "--stdio-server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )
    try:
        payload = "".join(json.dumps(r) + "\n" for r in requests)
        out, _err = proc.communicate(input=payload, timeout=timeout)
    finally:
        if proc.poll() is None:
            proc.kill()
    responses = [json.loads(line) for line in out.splitlines() if line.strip()]
    return responses


def call_stdio(requests, timeout=15):
    """Alias-style helper: see stdio_session — returns the stdio response dicts in order."""
    return stdio_session(requests, timeout=timeout)


# ------------------------------------------------------------- HTTP mode
def _make_handler(server):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 - BaseHTTPRequestHandler API
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                request = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                body = json.dumps(make_error(None, -32700, "Parse error")).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            response = server.handle(request)
            body = json.dumps(response if response is not None else {}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):  # silence default access log
            log("[http-server] " + (fmt % args))

    return Handler


def start_http_server(server=None):
    """Start the HTTP transport on port 0; return (httpd, thread, base_url)."""
    server = server or TransportServer()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _make_handler(server))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    return httpd, thread, f"http://127.0.0.1:{port}"


def stop_http_server(httpd, thread=None):
    """Shut an HTTP server from start_http_server down cleanly."""
    httpd.shutdown()
    httpd.server_close()
    if thread is not None:
        thread.join(timeout=5)


def http_call(base_url, request, timeout=10):
    """POST one JSON-RPC request dict to base_url and return the response dict."""
    data = json.dumps(request).encode("utf-8")
    req = urllib.request.Request(
        base_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_session(base_url, requests, timeout=10):
    """POST each request dict in order and return the list of response dicts."""
    return [http_call(base_url, r, timeout=timeout) for r in requests]


# ------------------------------------------------------- inspector/trace
def anatomy_inspector(server):
    """Inspect a TransportServer and return its full exposed-surface dict.

    Returns {"name": str, "version": str, "tools": [tool names],
    "tool_count": int, "methods": [JSON-RPC methods], "capabilities": sorted
    capability names from initialize, "transports": ["stdio", "http"]}.
    """
    init = server.initialize()
    tools = server.list_tools()
    return {
        "name": init["serverInfo"]["name"],
        "version": init["serverInfo"]["version"],
        "tools": [t["name"] for t in tools],
        "tool_count": len(tools),
        "methods": list(METHODS),
        "capabilities": sorted(init["capabilities"].keys()),
        "transports": ["stdio", "http"],
    }


def round_trip_trace(target, timeout=10):
    """Make 3 concurrent add calls and return their correlated trace entries.

    target is either an http base_url string (calls go over HTTP) or a
    TransportServer (calls go through its handle() in-process). Three calls
    with ids 101, 102, 103 run on a thread pool; returns a list of
    {"id": int, "tool": "add", "result": {"sum": int}} sorted by id.
    """
    jobs = [(101, {"a": 1, "b": 2}), (102, {"a": 10, "b": 20}), (103, {"a": 100, "b": 200})]

    def one(job):
        req_id, args = job
        request = make_request(req_id, "tools/call", {"name": "add", "arguments": args})
        if isinstance(target, str):
            resp = http_call(target, request, timeout=timeout)
        else:
            resp = target.handle(request)
        assert resp["id"] == req_id, (resp, req_id)
        return {"id": resp["id"], "tool": "add", "result": resp["result"]["structured"]}

    with ThreadPoolExecutor(max_workers=3) as pool:
        entries = list(pool.map(one, jobs))
    entries.sort(key=lambda e: e["id"])
    assert [e["result"] for e in entries] == [{"sum": 3}, {"sum": 30}, {"sum": 300}], entries
    return entries


def main():
    server = TransportServer()

    anatomy = anatomy_inspector(server)
    assert anatomy["tools"] == ["echo", "add"], anatomy
    print("transports: anatomy of the one server")
    print(f"  server: {anatomy['name']} {anatomy['version']}")
    print(f"  tools: {anatomy['tools']}  methods: {anatomy['methods']}")
    print(f"  capabilities: {anatomy['capabilities']}  transports: {anatomy['transports']}")

    # (a) stdio transport
    stdio_requests = [
        make_request(1, "initialize", {"protocolVersion": PROTOCOL_VERSION,
                                       "capabilities": {}, "clientInfo": {"name": "demo", "version": "1.0.0"}}),
        make_request(2, "tools/list", {}),
        make_request(3, "tools/call", {"name": "echo", "arguments": {"message": "hello over stdio"}}),
        make_request(4, "tools/call", {"name": "add", "arguments": {"a": 7, "b": 8}}),
    ]
    stdio_responses = stdio_session(stdio_requests)
    assert [r["id"] for r in stdio_responses] == [1, 2, 3, 4], stdio_responses
    assert stdio_responses[3]["result"]["structured"] == {"sum": 15}
    print("stdio transport (subprocess, NDJSON on stdin/stdout):")
    print(f"  initialize -> server {stdio_responses[0]['result']['serverInfo']['name']}")
    print(f"  tools/list -> {[t['name'] for t in stdio_responses[1]['result']['tools']]}")
    print(f"  echo -> {stdio_responses[2]['result']['structured']}")
    print(f"  add(7, 8) -> {stdio_responses[3]['result']['structured']}")

    # (b) HTTP transport — same server, same calls
    httpd, thread, base_url = start_http_server(server)
    try:
        http_responses = http_session(base_url, stdio_requests)
        assert [r["id"] for r in http_responses] == [1, 2, 3, 4], http_responses
        assert http_responses[3]["result"]["structured"] == {"sum": 15}
        print(f"HTTP transport (ThreadingHTTPServer at {base_url}):")
        print(f"  initialize -> server {http_responses[0]['result']['serverInfo']['name']}")
        print(f"  tools/list -> {[t['name'] for t in http_responses[1]['result']['tools']]}")
        print(f"  echo -> {http_responses[2]['result']['structured']}")
        print(f"  add(7, 8) -> {http_responses[3]['result']['structured']}")
        same = [r["result"] for r in stdio_responses] == [r["result"] for r in http_responses]
        print(f"  stdio and HTTP results identical: {same}")
        assert same

        trace = round_trip_trace(base_url)
        print("concurrent round-trip trace (3 threaded HTTP calls):")
        for entry in trace:
            print(f"  id={entry['id']} tool={entry['tool']} result={entry['result']}")
    finally:
        stop_http_server(httpd, thread)
    print("HTTP server shut down cleanly")

    print("transports demo: OK")


if __name__ == "__main__":
    if "--stdio-server" in sys.argv:
        sys.exit(run_stdio_server())
    main()
