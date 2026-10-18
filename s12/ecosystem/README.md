# ecosystem (s12)

**Section 12 — The Future: A2A, the Ecosystem, and Standardization · Lessons 47–48**

Place every connection in an estate by direction, then write the
adopt / build / buy / wait position note with its change triggers.

## Run

```bash
python demo.py
```

## What it does

1. **Protocol map** (`classify_connection`): MCP connects an agent
   *downward* to tools and data; A2A connects agents *sideways* to each
   other; human→app and batch connections are neither.
2. **Position note** (`position_note`): per capability family, a
   deterministic adopt/build/buy/wait decision plus the trigger string
   that would change the answer.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 47 — A2A and MCP: Two Protocols, Two Directions | `classify_connection` over 5 fixture connections (2 mcp, 1 a2a, 2 neither) |
| 48 — Governance, Trust, and Future-Proofing | `position_note` over `SAMPLE_ESTATE`: adopt / buy / build / wait with triggers |

## Key functions

- `classify_connection(description)` → `"a2a"` when
  `from_kind == "agent"` and `to_kind == "agent"`; `"mcp"` when an agent
  connects to `"tool"`/`"tools"`/`"data"`; otherwise `"neither"`
  (human→app, batch sync). A `"direction"` string like `"agent->tool"`
  is accepted in place of the two kind fields. All 5
  `FIXTURE_CONNECTIONS` classify to their recorded `expected` values.
- `position_note(estate)` → `{family: {"decision": ..., "trigger":
  ...}}`. Rules in order: differentiating → `build`; immature standard
  → `wait`; commodity + ≥3 vendors + open standard → `adopt`;
  commodity + ≥3 vendors → `buy`; otherwise → `wait`. For
  `SAMPLE_ESTATE`: file search → `adopt`, payment processing → `buy`,
  ticket triage → `build`, agent memory store → `wait`. Every entry's
  `trigger` is a non-empty string.
