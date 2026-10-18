# fundamentals (s02)

**Section 2 — Protocol Fundamentals · Lessons 5–8**

Discovery, the three roles, the three primitives, and the initialization
handshake — against one sample server exposing 2 tools, 2 resources, and
1 prompt over a small honest JSON-RPC 2.0 layer.

## How to run

```bash
python demo.py
```

Standard library only. Runs in-process, prints verifiable result lines, and
ends with `fundamentals demo: OK`.

## What it does

1. **Discovery** (`discover`): lists everything the sample server offers —
   tools `add`, `greet`; resources `notes://welcome`,
   `data://server-config`; prompt `daily_brief`.
2. **Three-role trace** (`three_role_trace`): one request followed through
   host → client → server, each step labelled with who owns the decision.
3. **Primitive sorter** (`classify_primitive`): classifies a capability as
   tool / resource / prompt purely from who decides.
4. **Handshake capture** (`handshake_capture`): negotiates the intersection
   of client and server capabilities, picking the highest common protocol
   version.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| Lesson 5 — What MCP Is (and Is Not) | `discover` lists the sample server's tools, resources, and prompts exactly as a client sees them |
| Lesson 6 — Design Philosophy and the Three Roles | `three_role_trace` labels host, client, and server decisions for one request |
| Lesson 7 — The Three Primitives: Tools, Resources, and Prompts | `classify_primitive` sorts capabilities by who decides (model / application / user) |
| Lesson 8 — Lifecycle, Messages, and Versioning | `handshake_capture` negotiates version and capability intersection field by field |

## Key functions

- `make_request(req_id, method, params=None)` — returns a JSON-RPC 2.0 request dict with `jsonrpc="2.0"`, the given id, method, and params (default `{}`).
- `make_result(req_id, result)` — returns a JSON-RPC 2.0 success response dict `{"jsonrpc": "2.0", "id": req_id, "result": result}`.
- `make_error(req_id, code, message)` — returns a JSON-RPC 2.0 error response dict with `error: {"code": code, "message": message}`.
- `FundamentalsServer.handle(request)` — dispatches `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`, and `ping`; returns the response dict.
- `FundamentalsClient.request(method, params=None)` — sends one JSON-RPC method and returns its result dict; raises `ValueError` on a protocol error response.
- `FundamentalsClient.initialize()` — returns the initialize handshake result dict (latest supported protocol version, tools/resources/prompts capabilities).
- `FundamentalsClient.list_tools()` — returns the 2 tool definition dicts (`add`, `greet`).
- `FundamentalsClient.list_resources()` — returns the 2 resource definition dicts (`notes://welcome`, `data://server-config`).
- `FundamentalsClient.list_prompts()` — returns the 1 prompt definition dict (`daily_brief`).
- `FundamentalsClient.call_tool(name, args)` — calls a tool via `tools/call` and returns its structured result dict.
- `discover(client)` — returns `{"tools": [names], "resources": [URIs], "prompts": [names], "counts": {"tools": 2, "resources": 2, "prompts": 1}}` for the sample server, in server order.
- `three_role_trace(request)` — returns a list of 5 `(component, decision)` tuples whose first three components are `"host"`, `"client"`, `"server"` in that order.
- `classify_primitive(capability)` — returns `"tool"` when who-decides is `model`, `"resource"` when it is `application`/`app`/`host`, and `"prompt"` when it is `user`; reads `who_decides`, `decided_by`, `control`, or `controller`; raises `ValueError` otherwise.
- `handshake_capture(client_caps, server_caps)` — returns a dict with `protocol_version` (highest common version string, or `None`), `capabilities` (sorted shared capability names), `client_capabilities`, `server_capabilities`, and `common_versions` (all sorted).
