# transports (s03)

**Section 3 — Architecture: Roles, Servers, and Transports · Lessons 9–12**

One server implementation (tools: `echo`, `add`) served two ways — as a
stdio subprocess and behind Streamable-HTTP-style POST JSON-RPC — plus an
anatomy inspector and a concurrent round-trip tracer.

## How to run

```bash
python demo.py
```

Standard library only; network use is localhost only (ephemeral port).
Runs end to end, shuts both servers down cleanly, and ends with
`transports demo: OK`. Stdio server mode (used internally by the demo):

```bash
python demo.py --stdio-server   # NDJSON JSON-RPC on stdin/stdout, logs on stderr
```

## What it does

1. **One server, two transports**: `TransportServer.handle()` is the single
   implementation. Stdio re-invokes this file as a subprocess via
   `[sys.executable, __file__, "--stdio-server"]` speaking
   newline-delimited JSON-RPC (logging to stderr only); HTTP serves the
   same handler via `ThreadingHTTPServer` on port 0 accepting POSTs.
2. **Anatomy inspector** (`anatomy_inspector`): the full exposed surface —
   name, tools, methods, capabilities, transports.
3. **Round-trip tracer** (`round_trip_trace`): 3 concurrent threaded calls,
   results correlated to requests by message id and asserted.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| Lesson 9 — Separation of Concerns and Server Anatomy | `anatomy_inspector` produces the server's full exposed-surface report |
| Lesson 10 — The stdio Transport: Local, Simple, Process-Bound | Stdio subprocess session; stdout is protocol-only, logging goes to stderr |
| Lesson 11 — Streamable HTTP: Remote, Stateless, Scalable | Same server behind HTTP POST JSON-RPC on an ephemeral localhost port; results compared line-by-line with stdio |
| Lesson 12 — Sessions, Concurrency, and a Full Round-Trip | `round_trip_trace` runs 3 concurrent calls and reconstructs results from message ids |

## Key functions

- `make_request(req_id, method, params=None)` — returns a JSON-RPC 2.0 request dict with `jsonrpc="2.0"`, the given id, method, and params (default `{}`).
- `make_result(req_id, result)` — returns a JSON-RPC 2.0 success response dict `{"jsonrpc": "2.0", "id": req_id, "result": result}`.
- `make_error(req_id, code, message)` — returns a JSON-RPC 2.0 error response dict with `error: {"code": code, "message": message}`.
- `log(*args)` — writes a log line to stderr only; never writes to stdout.
- `TransportServer.initialize(params=None)` — returns the handshake result dict with protocol version `2025-03-26`, tools capability, and serverInfo `transports-sample 1.0.0`.
- `TransportServer.list_tools()` — returns the 2 tool definition dicts, named `echo` and `add`, in that order.
- `TransportServer.call_tool(name, args)` — returns the structured result dict (`echo` returns `{"echo": message}`, `add` returns `{"sum": a + b}`); raises `ValueError` for an unknown tool.
- `TransportServer.handle(request)` — dispatches `initialize`, `tools/list`, `tools/call`, and `ping` request dicts and returns the response dict (`None` for the initialized notification).
- `run_stdio_server()` — serves newline-delimited JSON-RPC on stdin/stdout until stdin closes, logging to stderr only, and returns 0.
- `stdio_session(requests, timeout=15)` — spawns this file with `--stdio-server`, sends the request dicts, returns the response dicts in send order, and always terminates the subprocess.
- `call_stdio(requests, timeout=15)` — same behaviour as `stdio_session`: returns the stdio response dicts in order.
- `start_http_server(server=None)` — starts a `ThreadingHTTPServer` on `127.0.0.1` port 0 and returns `(httpd, thread, base_url)` with an ephemeral port.
- `stop_http_server(httpd, thread=None)` — shuts the HTTP server down and closes it, joining its thread with a 5-second timeout.
- `http_call(base_url, request, timeout=10)` — POSTs one JSON-RPC request dict to `base_url` and returns the decoded response dict.
- `http_session(base_url, requests, timeout=10)` — POSTs each request dict in order and returns the list of response dicts.
- `anatomy_inspector(server)` — returns `{"name", "version", "tools": ["echo", "add"], "tool_count": 2, "methods": ["initialize", "tools/list", "tools/call", "ping"], "capabilities": ["tools"], "transports": ["stdio", "http"]}` for the sample server.
- `round_trip_trace(target, timeout=10)` — runs 3 concurrent `add` calls (ids 101, 102, 103) over HTTP when `target` is a base-URL string, or in-process when it is a `TransportServer`; returns entries `{"id", "tool": "add", "result": {"sum": ...}}` sorted by id with sums 3, 30, 300.
