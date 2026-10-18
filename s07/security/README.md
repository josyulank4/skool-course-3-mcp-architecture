# security (s07)

**Section 7 — Security: Authentication, Permissions, and Sandboxing · Lessons 27–31**

Tool output is input to a reasoning engine that can act — so the trust
boundary moved. This demo drills the four defenses in code: treat tool
output as data, check scoped tokens in server code, gate destructive
calls behind a human, and run the checklist. Every record and token is
an obvious fixture, built at runtime; there are no real secrets here.

## Run

```bash
python demo.py
```

## What it does

1. **Injection drill**: `POISONED_RECORD` is a ticket whose note tells
   the reader to refund everything. The naive client obeys the note;
   the defended client decides from structured fields only.
2. **Token auth**: fixture tokens carry scopes and an expiry and are
   verified (format + signature + expiry + scope) in server code.
   Time is an explicit `now` integer — no wall clock, fully
   deterministic.
3. **Approval + least privilege**: destructive tools pause for an
   approver callback; `guarded_call` denies any call whose token scopes
   lack the tool's required scope, whatever the prompt said.
4. **Checklist**: the hardened config passes all items; the lax config
   fails five named items.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 27 — Injection Through Tool Outputs | `POISONED_RECORD`, `naive_client` vs `defended_client` |
| 28 — Poisoning & the Confused Deputy | scope checks in server code (`guarded_call`), not in the prompt |
| 29 — Authentication: Tokens | `make_token`, `parse_token`, `auth_check` (valid/expired/scoped cases) |
| 30 — Least Privilege & Human Approval | `approval_gate`, `TOOL_REQUIRED_SCOPE`, `guarded_call` |
| 31 — Sandboxing, Audit & the Checklist | `security_checklist`, `HARDENED_CONFIG` vs `LAX_CONFIG` |

## Key functions

- `naive_client(POISONED_RECORD)` — returns `"refund"`: it obeys the
  instruction planted in the record's `note`.
- `defended_client(POISONED_RECORD)` — returns `"escalate"`: the note is
  data; a refund would require `refund_approved` plus a verified double
  charge in the record's structured fields.
- `make_token(scopes, expires_at)` — deterministic fixture token of the
  form `demo.<comma-joined sorted scopes>.<expires_at>.<8-hex signature>`;
  the same inputs always build the same string.
- `auth_check(token, required_scope, now)` — returns `(bool, reason)`:
  - valid: `auth_check(make_token(["read"], 2000), "read", 1000) == (True, "ok")`
  - expired (inclusive): `now == 2000` gives `(False, "expired")`
  - under-scoped: a read token checked for `"write"` gives
    `(False, "missing scope: write")`
  - over-scoped: a token carrying a scope outside `("read", "write")`,
    e.g. `"admin"`, gives `(False, "unknown scope: admin")`
  - forged or malformed strings give `(False, "malformed token")`
- `approval_gate(tool, args, approver)` — returns `"executed"` for
  non-destructive tools; for the destructive set
  (`delete_customer`, `issue_refund`, `purge_records`) it calls
  `approver(tool, args)`: `True -> "approved"`, `False -> "denied"`,
  and no approver at all -> `"denied"`.
- `guarded_call(token_scopes, tool)` — `True` only when the tool is
  known and its required scope (from `TOOL_REQUIRED_SCOPE`: read tools
  need `"read"`, write tools need `"write"`) is in `token_scopes`;
  unknown tools return `False`.
- `security_checklist(config)` — returns 7 `(item, passed)` tuples in
  this order: token authentication enabled; scope enforcement on every
  call; approval gate for destructive tools; tool output treated as
  untrusted data; audit logging enabled; sandbox filesystem roots
  bounded; tokens sent in headers only. `HARDENED_CONFIG` passes all 7;
  `LAX_CONFIG` passes 2 and fails 5. Missing keys count as failed.
- `handle_message(msg, token, now)` — JSON-RPC 2.0; `tools/call` runs
  `auth_check` in server code and returns error code `-32001` with the
  refusal reason when the check fails.
