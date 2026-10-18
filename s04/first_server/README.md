# first_server (s04)

**Section 4 — Building Your First MCP Server · Lessons 13–17**

A minimal honest MCP server — metadata, capability declaration, a
JSON-Schema-validated `word_count` tool, a live handshake lab, and the
five-mistake hunt — in plain Python, standard library only.

## How to run

```bash
python demo.py
```

Runs in-process, prints verifiable result lines, and ends with
`first_server demo: OK`.

## What it does

1. **Server scaffold** (`build_server`): metadata + declared capabilities;
   `initialize()` echoes exactly what was declared.
2. **Declaration checker** (`check_declaration`): compares declared
   capabilities against actually implemented handlers. The bundled
   over-declaring fixture yields exactly 1 mismatch (`resources`); the
   corrected server yields 0.
3. **Validated tool + adversarial set** (`validate_args`): missing field,
   wrong type, extra-long string, and non-object inputs all produce clean
   structured errors — none raise.
4. **Handshake lab** (`handshake_lab`): negotiates with full client
   capabilities and with stripped capabilities, and returns both sessions.
5. **Mistake hunt** (`find_mistakes`): the broken config contains all 5
   planted first-server mistakes; the fixed config contains 0.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| Lesson 13 — The Minimal Server and Project Setup | `build_server` scaffold: metadata, capabilities, one tool handler, `handle()` transport-facing dispatch |
| Lesson 14 — Metadata and Capability Declaration | `check_declaration` verifies the declaration against implemented handlers (1 mismatch, then 0) |
| Lesson 15 — Your First Tool: JSON Schema Inputs | `word_count` tool with `validate_args` against the adversarial argument set |
| Lesson 16 — The Initialization Handshake, Live | `handshake_lab` negotiates full vs stripped client capabilities and returns both dicts |
| Lesson 17 — Testing with the Inspector — and First-Server Mistakes | `find_mistakes` finds the 5 planted mistakes in the broken config and 0 in the fixed config |

## Key functions

- `make_request(req_id, method, params=None)` — returns a JSON-RPC 2.0 request dict with `jsonrpc="2.0"`, the given id, method, and params (default `{}`).
- `make_result(req_id, result)` — returns a JSON-RPC 2.0 success response dict `{"jsonrpc": "2.0", "id": req_id, "result": result}`.
- `make_error(req_id, code, message)` — returns a JSON-RPC 2.0 error response dict with `error: {"code": code, "message": message}`.
- `build_server(metadata, capabilities, implemented=None)` — returns a `FirstServer` with the given metadata dict and declared-capabilities dict; when `implemented` is `None` every declared capability is implemented, otherwise only the listed capability names have handlers.
- `FirstServer.initialize(params=None)` — returns the initialize result dict echoing the declared capabilities and serverInfo (name, version, description from metadata), with the highest supported protocol version the client offered.
- `FirstServer.list_tools()` — returns `[word_count tool definition]` when tools are implemented, otherwise `[]`.
- `FirstServer.call_tool(name, args)` — returns `(structured_result, [])` on success (e.g. `word_count` returns `({"count": 4}, [])` for `"the quick brown fox"`) or `(None, errors)` with `validate_args` errors on invalid input.
- `FirstServer.handle(request)` — dispatches `initialize`, `tools/list`, `tools/call`, and `ping` request dicts and returns the response dict, with validation failures as structured `-32602` errors.
- `check_declaration(server)` — returns the sorted list of capability-name strings declared in `server.capabilities` but absent from `server.implemented`; the over-declaring fixture returns exactly `["resources"]` and an honest server returns `[]`.
- `validate_args(schema, args)` — returns a list of structured error dicts `{"field", "code", "message"}` (codes include `missing_required`, `wrong_type`, `too_long`, `not_an_object`); returns `[]` when valid and never raises for any `args` value.
- `negotiate(client_caps, server_caps=None)` — returns `{"protocol_version": highest common version or None, "capabilities": sorted shared names, "client_capabilities": sorted, "server_capabilities": sorted}` against the demo server caps by default.
- `handshake_lab(full_caps, stripped_caps, server_caps=None)` — returns `{"full": negotiate(full_caps), "stripped": negotiate(stripped_caps)}`; the bundled fixtures negotiate `2025-06-18` (full) and `2025-03-26` (stripped).
- `find_mistakes(server_config)` — returns the planted mistake ids present in the config, as a sublist of `["stdout_printing", "unimplemented_capability", "human_only_description", "accept_anything_schema", "raw_exception_leak"]` in that order; the bundled broken config returns all 5 and the fixed config returns `[]`.
