# orchestration (s08)

**Section 8 — Multi-Server Orchestration · Lessons 32–35**

One focused server per system composes into an agent whose tool belt
spans the enterprise — and immediately creates three problems:
discovery, name collisions, and partial failure. This demo solves each
in code, with a three-server support workflow as the running example.

## Run

```bash
python demo.py
```

## What it does

1. **Discovery**: three mini servers (ticketing, accounts, billing)
   register in a `Registry`; `discover()` is everything the host knows
   before the first call.
2. **Namespacing**: ticketing and accounts both expose `search`. A bare
   call is ambiguous and raises; after `namespace()` both are callable
   as `ticketing.search` and `accounts.search`. Routing is mechanical —
   the model never chooses a server.
3. **Composition with compensation**: `compose_workflow` resolves
   ticket 501 across all three servers (read ticket → read account →
   read billing → fix rate → resolve ticket). A failure injected at
   step 4 runs the compensation and rolls the billing write back.
4. **Failure isolation**: killing billing degrades the agent — ticketing
   still reads, billing is reported unavailable — and restarting it
   restores full capability.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 32 — Discovery | `Registry.register` / `Registry.discover`, `build_servers` |
| 33 — Namespacing, Collisions, Routing | `Host.namespace`, `Host.host_call`, `AmbiguousToolError` on bare `search` |
| 34 — Composing Multi-Server Workflows | `compose_workflow` (5 steps), compensation with `fail_at_step=4` |
| 35 — Failure Isolation | `Host.kill_server` / `restart_server`, `Host.agent_status` degradation and recovery |

## Key functions

- `build_servers()` — returns a fresh dict
  `{"ticketing": ..., "accounts": ..., "billing": ...}` with fixture
  state reset (ticket 501 open, billing B-1 tax_rate 0.10).
- `Registry.register(name, server)` and `Registry.discover()` —
  `discover()` returns
  `{"accounts": ["read_account", "search"],
    "billing": ["read_billing", "set_tax_rate"],
    "ticketing": ["read_ticket", "search", "update_ticket"]}`.
- Each server exposes a `tools` dict mapping tool names to callables:
  ticketing `read_ticket` / `update_ticket` / `search`, accounts
  `read_account` / `search`, billing `read_billing` / `set_tax_rate`.
- `Host.namespace()` — returns a dict whose keys are every tool
  prefixed as `"server.tool"` (7 entries) and whose values are
  `(server_name, tool_name)` pairs.
- `Host.host_call(name, **args)` — a namespaced name
  (`"ticketing.search"`) or a unique bare name (`"read_ticket"`)
  dispatches to the owning server. Bare `"search"` raises
  `AmbiguousToolError`; unknown names raise `KeyError`; calls to a down
  server raise `ServerUnavailableError`.
  After namespacing, `host_call("ticketing.search", query="tax")`
  returns ticket 501 and `host_call("accounts.search",
  query="northwind")` returns account A-1.
- `compose_workflow(servers, fail_at_step=None)` — accepts a `Host`, a
  `Registry`, a `{name: server}` dict, or a list of servers; server
  state resets first, so runs are repeatable. On success it returns a
  dict with `status == "resolved"`, `final_tax_rate == 0.20`,
  `ticket_status == "resolved"`, and a 5-entry `steps` list. With
  `fail_at_step=4` it returns `status == "compensated"`,
  `final_tax_rate == 0.10`, `ticket_status == "open"`, and a non-empty
  `compensated_actions` list — the billing write is undone in the
  servers' actual state, not just reported as undone.
- `Host.kill_server(name)` / `Host.restart_server(name)` and
  `Host.agent_status()` — `agent_status()` returns a dict with
  `overall` (`"ok"` or `"degraded"`), `servers` mapping each name to
  `"up"`/`"down"`, and sorted `available_capabilities` /
  `unavailable_capabilities` lists of namespaced tool names. With
  billing killed: `overall == "degraded"`,
  `"ticketing.read_ticket"` is in `available_capabilities`, and
  `"billing.set_tax_rate"` is in `unavailable_capabilities`; after
  `restart_server("billing")`, `overall == "ok"` and
  `unavailable_capabilities == []`.
- Module-level wrappers (`discover`, `namespace`, `host_call`,
  `kill_server`, `restart_server`, `agent_status`, `register`) operate
  on a default host built from `build_servers()`, with the same
  behavior as the `Host` methods above.
- `Host.handle_message(msg)` — JSON-RPC 2.0 for `initialize` and
  `tools/list` (which lists the 7 namespaced tool names); unknown
  methods return code `-32601`.
