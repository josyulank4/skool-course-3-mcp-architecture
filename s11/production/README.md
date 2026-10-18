# production (s11)

**Section 11 — Observability and Production Deployment · Lessons 43–46**

Structured logging and tracing, dual packaging, a stateless scaling lab,
and a canary rollback drill.

## Run

```bash
python demo.py
```

## What it does

1. **Structured logging + tracing**: `log_call` appends JSON lines to the
   in-memory `LOG_STORE` with redaction; `run_calls` injects a slow
   upstream into one trace, and `reconstruct_timeline` rebuilds exactly
   that trace from its correlation ID.
2. **Dual packaging**: `package_manifests` describes the same server as
   a stdio distribution and as a remote HTTP service, with version and
   protocol-compatibility fields.
3. **Scaling lab**: 3 stateless replicas behind a round-robin balancer;
   replica 2 is killed mid-sequence and every request is still served.
4. **Canary drill**: a defective tool description is promoted to the
   canary population, burns the error budget on fixture calls, and is
   rolled back.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 43 — Observability | `log_call` / `redact` / `run_calls` / `reconstruct_timeline` (corr-A incident) |
| 44 — Packaging, Versioning, Topologies | `package_manifests`: stdio + streamable-http, version + protocol fields |
| 45 — Scaling | `route_requests` / `scaling_lab`: replica 2 killed, 9/9 requests served |
| 46 — Safe Rollouts, Monitoring, Incident Response | `canary_drill` + `budget_burned` + `rollback` |

## Key functions

- `log_call(server, tool, caller, args, outcome, duration_ms, corr_id)`
  → the record dict, also appended to `LOG_STORE` as a JSON line.
  `redact` replaces any value whose key contains `token`, `secret`,
  `passwd`, `credential`, or `api_key` with `"***"` (recursively);
  other values pass through unchanged.
- `run_calls()` → `["corr-A", "corr-B"]`; leaves 5 log lines in
  `LOG_STORE`. `reconstruct_timeline("corr-A")` → exactly 3 records,
  ordered by `seq`, all with `corr_id == "corr-A"`, including the
  injected slow call (`outcome == "slow_upstream"`,
  `duration_ms == 1800`). The first line's redacted argument shows
  `"***"` while its `ticket_id` stays visible.
- `package_manifests()` → `(stdio_manifest, http_manifest)`; both have
  `version == "1.4.0"` and `protocol_version == "2025-03-26"` plus a
  `compatible_protocol_versions` list; transports are `"stdio"` and
  `"streamable-http"`.
- `route_requests(n)` → list of `n` dicts `{"request", "replica",
  "status"}`, replica 2 killed after request 4; every status is
  `"served"` and no result from request 5 onward names replica 2.
  `scaling_lab()` → `{"requests": 9, "served": 9, "killed_replica": 2,
  "results": route_requests(9)}` in effect.
- `budget_burned(rate)` → `rate > 0.05`. `canary_drill()` →
  `{"error_rate": 0.4, "budget_burned": True, "rolled_back": True,
  "live_description": OLD_DESCRIPTION, ...}` (8 failures in 20 fixture
  calls). `rollback()` restores and returns `OLD_DESCRIPTION`.
