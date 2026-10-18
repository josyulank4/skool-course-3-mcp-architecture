# enterprise (s06)

**Section 6 — Connecting MCP to Enterprise Systems · Lessons 22–26**

An MCP server is a facade: agents see domain concepts (invoice, account,
document) and never meet table names, endpoint shapes, pagination, or
paths. This demo wraps a database, a file store, and a REST API behind
one facade, tiers every tool by safety, and resolves the book's
wrong-tax-rate ticket inside a rate-limit quota.

## Run

```bash
python demo.py
```

## What it does

1. **Database wrapper**: in-memory tables (`customers`, `invoices`,
   `tax_rates`) reachable only through curated tools — exact-id lookup
   and name substring search. There is no query-string surface, so an
   injection-shaped input is just a string that matches nothing.
2. **File-store wrapper**: every name is resolved under a fixed root;
   traversal and absolute escapes are refused.
3. **REST wrapper**: a paginated fake endpoint is flattened into one
   list, and HTTP statuses are translated into one error vocabulary.
4. **Facade + safety register**: domain tool names only; every tool in
   the demo is tiered `read`/`write` with a minimum credential scope and
   an approval flag.
5. **Ticketing scenario**: a token bucket prices each uncached upstream
   read; a cache hit is free. The ticket resolves across all three
   stores using 3 of 6 quota.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 22 — The Adapter Pattern | `EnterpriseFacade`: domain tools only, quirks quarantined behind it |
| 23 — Wrapping Databases & File Stores | `get_invoice` / `find_customer`; `resolve_path` + `FileStore` |
| 24 — Wrapping REST APIs & SaaS | `RestWrapper` / `FakeRestEndpoint`: pagination, `http_error_class` |
| 25 — Upstream Auth & Safety Tiers | `tier_tool`, `safety_register` (scope + approval per tool) |
| 26 — Rate Limits & Ticketing Scenario | `TokenBucket`, `run_ticketing_scenario` with cache |

## Key functions

- `get_invoice(invoice_id)` — returns the invoice dict (id 1001: net
  1000.0, `tax_key == "reduced"`, total 1100.0 in the fresh fixture).
  Non-integer ids raise `ValueError`; unknown integer ids raise
  `KeyError`. There is no string-query path.
- `find_customer(name_query)` — case-insensitive substring match;
  `find_customer("northwind")` returns Northwind Traders and
  `find_customer("' OR 1=1 --")` returns `[]`.
- `update_invoice_tax(invoice_id, tax_key)` — write tool;
  `update_invoice_tax(1001, "standard")` returns tax_rate 0.20 and
  total 1200.0.
- `resolve_path(root, name)` — returns a `pathlib.Path` inside `root`;
  `resolve_path("/srv/demo-files", "../secret.txt")` raises
  `ValueError`, as does any absolute escape.
  `FileStore().read_document("tax-policy.txt")["path"]` is
  `"/srv/demo-files/tax-policy.txt"`.
- `http_error_class(status)` — `404 -> ("not_found", "caller-fixable")`,
  `429 -> ("rate_limited", "retryable")`,
  `500 -> ("upstream_error", "fatal")`.
- `RestWrapper.list_accounts()` — flattens both fake pages and returns
  accounts with ids `["A-1", "A-2", "A-3"]` in order.
  `get_account("A-99")` raises `RestError` with
  `error_class == "not_found"`.
- `EnterpriseFacade.tool_names()` — returns
  `["find_customer", "get_account", "get_invoice", "list_accounts",
  "read_document"]`.
- `tier_tool(name)` — `"read"` for the five facade reads, `"write"` for
  `update_invoice_tax`, `update_ticket_status`, `issue_refund`; unknown
  names raise `KeyError`.
- `safety_register()` — a list of 8 dicts with keys `tool`, `tier`,
  `credential_scope`, `approval_required`; `approval_required` is
  `True` for every write-tier tool and `False` for reads.
- `TokenBucket(capacity, refill_per_tick)` — starts full; `consume()`
  returns `False` when empty and spends nothing; `tick()` refills by
  `refill_per_tick`, capped at capacity.
- `run_ticketing_scenario()` — returns a dict with
  `status == "resolved"`, `correct_tax_rate == 0.20`,
  `correct_total == 1200.0`, `quota_used == 3`, `quota == 6`
  (so `quota_used <= quota`), and a `steps` list whose entries cover the
  DB read, a cache hit, the file read, the REST read, and the fix.
  Repeated calls return the same values (the DB resets first).
- `handle_message(msg)` — JSON-RPC 2.0 for `initialize`, `tools/list`,
  `tools/call` (facade tools only); unknown methods return code `-32601`.
