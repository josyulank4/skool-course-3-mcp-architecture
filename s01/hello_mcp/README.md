# hello_mcp (s01)

**Section 1 — Welcome: Why Agents Need a Protocol · Lessons 1–4**

Hello-MCP smoke test: a client connects to a minimal server, performs the
initialize handshake, lists tools, and makes one tool call end to end — plus
the capability audit and the N×M integration counter from the section.

## How to run

```bash
python demo.py
```

Standard library only. Runs in-process, prints verifiable result lines, and
ends with `hello_mcp demo: OK`.

## What it does

1. **Minimal MCP server + client** (`HelloMCPServer` / `HelloMCPClient`):
   a small honest JSON-RPC 2.0 layer (dicts with `jsonrpc`/`id`/`method`/
   `params`) supporting `initialize`, `tools/list`, and `tools/call`.
   Tools actually compute: `add` sums two numbers, `word_count` counts
   whitespace-separated words.
2. **Capability audit** (`capability_audit`): for one use case, lists what
   the agent must perceive and change, and which of those exist as tools.
3. **N×M counter** (`nxm_counts`): bespoke integrations `N*M` versus
   standard-based integrations `N+M` — the demo prints 5×3 = 15 vs 8.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| Lesson 1 — Welcome: The Protocol That Gives Agents Hands | The end-to-end hello: one client, one server, one real tool call |
| Lesson 2 — How to Use This Course and the Code Repository | This runnable smoke test is the repo tour's first check |
| Lesson 3 — The Brilliant Prisoner: What Models Can and Cannot Do | `capability_audit` on the invoice-support use case (perceive/change vs tools) |
| Lesson 4 — The N×M Problem: Why a Standard Had to Exist | `nxm_counts(5, 3)` → bespoke 15 vs standard 8 |

## Key functions

- `make_request(req_id, method, params=None)` — returns a JSON-RPC 2.0 request dict with `jsonrpc="2.0"`, the given id, method, and params (default `{}`).
- `make_result(req_id, result)` — returns a JSON-RPC 2.0 success response dict `{"jsonrpc": "2.0", "id": req_id, "result": result}`.
- `make_error(req_id, code, message)` — returns a JSON-RPC 2.0 error response dict with `error: {"code": code, "message": message}`.
- `HelloMCPServer.handle(request)` — dispatches one JSON-RPC request dict (`initialize`, `tools/list`, `tools/call`, `ping`) and returns the response dict (or `None` for the initialized notification).
- `HelloMCPServer.initialize(params=None)` — returns the handshake result dict with `protocolVersion="2025-03-26"`, tools capability, and serverInfo `hello-mcp 1.0.0`.
- `HelloMCPServer.list_tools()` — returns the two tool definition dicts, named `add` and `word_count`, in that order.
- `HelloMCPServer.call_tool(name, args)` — returns the tool's structured result dict (e.g. `add` with `{"a": 19, "b": 23}` returns `{"sum": 42}`); raises `ValueError` for an unknown tool.
- `HelloMCPClient.initialize()` — sends `initialize`, stores and returns the server's handshake result dict.
- `HelloMCPClient.list_tools()` — returns the tool definition list from `tools/list` (same as the server's).
- `HelloMCPClient.call_tool(name, args)` — calls a tool via `tools/call` and returns its structured result dict.
- `capability_audit(use_case)` — returns a dict with `perceive`, `change`, sorted `available_tools`, `covered` (needed items present as tools, in perceive-then-change order), `missing` (needed items not present, same order), `total_needed`, and `covered_count`.
- `nxm_counts(n_apps, m_tools)` — returns the tuple `(n_apps * m_tools, n_apps + m_tools)`; `nxm_counts(5, 3)` is `(15, 8)`.
