# testing (s10)

**Section 10 — Testing and Evaluating MCP Servers · Lessons 39–42**

Four suites as one green gate: unit, contract, integration (mock-client
abuse), and adversarial + regression.

## Run

```bash
python demo.py
```

## What it does

1. **Unit suite** (`unit_test_suite`) for `normalize_ticket_priority`
   (urgent/critical → P1, high → P2, normal/medium → P3, low → P4,
   blank/unknown → P3). The planted-bug variant `broken_normalize`
   mis-maps `"urgent"` to P4 and fails exactly one named test.
2. **Contract tests** (`contract_test`): declared vs implemented tools,
   schema drift against the baseline contract, and live error shapes.
   The good server is clean; tightening the priority enum is a
   `"breaking"` violation.
3. **Mock-client abuse** (`run_abuse`): malformed message, simulated
   mid-call disconnect, and a capability-stripped session — each answered
   with a structured error, never an exception.
4. **Adversarial + regression**: poisoned outputs refused by
   `defended_pipeline`; the golden conversation set replayed by
   `regression_gate`.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 39 — Unit Tests | `unit_test_suite` over 6 cases; `broken_normalize` fails exactly 1 |
| 40 — Contract Testing | `contract_test`: declared-vs-implemented, schema tightening = breaking, error classes |
| 41 — Integration Testing | `run_abuse`: malformed / disconnect / capability-stripped mock-client sequences |
| 42 — Adversarial Testing and Regression | `adversarial_fixtures` + `defended_pipeline`; `regression_gate` golden set |

## Key functions

- `normalize_ticket_priority(raw)` → `"P1"` for urgent/critical, `"P2"`
  for high, `"P3"` for normal/medium/blank/unknown/`None`, `"P4"` for low
  (case-insensitive, whitespace-trimmed).
- `unit_test_suite(handler)` → `(passed, failed, failing_names)`.
  `unit_test_suite(normalize_ticket_priority) == (6, 0, [])`;
  `unit_test_suite(broken_normalize) == (5, 1, ["urgent_maps_to_p1"])`.
- `contract_test(server)` → list of violation strings; `[]` for
  `make_server()`. For `make_server(drifted=True)` (priority enum with
  `"urgent"` removed) the list is non-empty and every schema-drift entry
  starts with `"breaking:"`. Errors must carry `class` in
  `{caller_fixable, retryable, fatal}`.
- `run_abuse(server)` → dict with keys `malformed_message`,
  `mid_call_disconnect`, `capability_stripped`; each value is a dict
  with an `"error"` entry whose `"class"` is in the allowed set
  (malformed → `caller_fixable`, disconnect → `retryable`,
  stripped → `caller_fixable`). It never raises.
- `adversarial_fixtures()` → list of 3 poisoned output dicts.
  `defended_pipeline(output)` → `True` when the output is safe to pass
  onward as data, `False` when refused as instruction-bearing; all 3
  fixtures return `False`, a plain billing note returns `True`.
- `regression_gate(handler)` → `True` for `normalize_ticket_priority`,
  `False` for `broken_normalize`.
