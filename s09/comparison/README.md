# comparison (s09)

**Section 9 — MCP vs Function Calling vs Custom APIs · Lessons 36–38**

One capability — ticket lookup — built three ways, then the honest
comparison: integration arithmetic, a decision framework, and a migration
planner.

## Run

```bash
python demo.py
```

## What it does

1. **The triptych** (`function_calling_lookup`, `mcp_lookup`,
   `bespoke_lookup`): the same ticket lookup over a provider-style
   function schema + dispatch table, over a mini MCP server
   (`mcp_handle`: JSON-RPC `tools/list` + `tools/call`), and over a
   hand-rolled `{op, payload}` protocol. All three return the identical
   ticket dict for `T-1001` and `None` for an unknown ID.
2. **Integration counter** (`integration_count`): bespoke and
   per-provider function calling cost **N × M** integrations; MCP costs
   **N + M**. Fixture: 5 surfaces × 3 tools → 15 vs 8.
3. **Decision framework** (`decision_framework`): exotic single
   capability → `bespoke`; one model + one team + ≤5 tools + short
   horizon → `function_calling`; everything else → `mcp`.
4. **Migration planner** (`migration_plan`): facade first, consumers
   migrated one at a time in listed order, retirement criteria last.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 36 — Three Ways to Give a Model Tools | the triptych: function calling / MCP / bespoke ticket lookup |
| 37 — Head-to-Head: The Honest Comparison | `integration_count` (N×M vs N+M); `decision_framework` on three fixture contexts |
| 38 — Hybrids and Migrating to MCP | `migration_plan`: facade first, one consumer at a time, retire criteria last |

## Key functions

- `function_calling_lookup(ticket_id)` / `mcp_lookup(ticket_id)` /
  `bespoke_lookup(ticket_id)` → the ticket dict from the fixture store
  (`T-1001` → the wrong-tax-rate ticket, status `open`, priority `P1`),
  or `None` for an unknown ID. All three always agree.
- `integration_count(approach, n_surfaces, m_tools)` → `n + m` for
  `"mcp"`; `n * m` for `"function_calling"` and `"bespoke"`.
  `integration_count("mcp", 5, 3) == 8`;
  `integration_count("bespoke", 5, 3) == 15`.
- `decision_framework(context)` → `"function_calling"` for
  `CONTEXT_FUNCTION_CALLING` (1 model, 1 team, 3 tools, short horizon),
  `"mcp"` for `CONTEXT_MCP` (3 models, 2 teams, 12 tools, long horizon),
  `"bespoke"` for `CONTEXT_BESPOKE` (`exotic: True`).
- `migration_plan(integration)` → ordered list of step strings: step 1
  builds the MCP facade, one step per consumer follows in the order
  listed in `integration["consumers"]`, and the final step states the
  retirement criteria for the bespoke path. For `SAMPLE_INTEGRATION`
  (3 consumers) the plan has exactly 5 steps.
