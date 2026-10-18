# primitives (s05)

**Section 5 — The Three Primitives in Depth · Lessons 18–21**

Resources, tools, and prompts are three different control models — who
decides — not three data types. This demo builds each one, refactors a
monolith tool into a clean toolset, and reviews a surface for boundary
violations.

## Run

```bash
python demo.py
```

## What it does

1. **Resource model** (`ResourceStore`): URI templates
   (`db://customers/{id}`, `db://tickets/{id}`, `docs://guides/{slug}`)
   resolve to concrete URIs and read back as content dicts.
2. **Monolith refactor**: `monolith_do_everything` dispatches by substring
   (customer → ticket → update), so `update_ticket` lands in the search
   branch and `search_customer_tickets` lands in the customer branch —
   wrong-branch errors. The clean toolset (`get_customer`, `update_ticket`,
   `search_tickets`, each with a schema in `TOOL_SCHEMAS`) is called by
   exact name. Same fixed suite: monolith **2/4**, toolset **4/4**.
3. **Prompt template** (`render_prompt`): the user-invoked
   `incident_triage` playbook renders to messages with its context
   attached — one embedded resource reference.
4. **Boundary review** (`boundary_review`): `DEMO_SURFACE` plants exactly
   two violations and the reviewer finds exactly those two.
5. **JSON-RPC 2.0** (`handle_message`): `initialize`, `tools/list`,
   `tools/call`, `resources/list`, `resources/read`, `prompts/list`,
   `prompts/get`.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 18 — Resources in Depth | `ResourceStore`: templates, `resolve`, `read`, `list_resources` |
| 19 — Tools in Depth | monolith vs toolset refactor; `run_task_suite` comparison; tool schemas |
| 20 — Prompts in Depth | `render_prompt` incident-triage template with embedded resource |
| 21 — Clean Boundaries | `boundary_review` over `DEMO_SURFACE` (2 planted violations) |

## Key functions

- `ResourceStore.resolve(template, params)` — e.g.
  `resolve("db://customers/{id}", {"id": 1})` returns `"db://customers/1"`;
  unknown templates and unresolved parameters raise `ValueError`.
- `ResourceStore.read(uri)` — `read("db://customers/1")` returns a dict
  with `name == "Northwind Traders"` and `uri == "db://customers/1"`;
  unknown URIs raise `KeyError`.
- `ResourceStore.list_resources()` — returns the sorted list
  `["db://customers/1", "db://customers/2", "db://tickets/101",
  "db://tickets/102", "docs://guides/billing-basics",
  "docs://guides/incident-response"]`.
- `get_customer(customer_id)` — returns the customer dict, e.g. id 1 is
  Northwind Traders; unknown ids raise `KeyError`.
- `update_ticket(ticket_id, status)` — sets and returns the ticket dict
  with the new `status`.
- `search_tickets(query)` — case-insensitive title search;
  `search_tickets("tax")` returns exactly ticket 101.
- `monolith_do_everything(action, **kw)` — substring dispatch; the
  `update` branch is unreachable for `update_ticket`.
- `run_task_suite(impl)` — `run_task_suite("monolith") == (2, 4)` and
  `run_task_suite("toolset") == (4, 4)`; state resets before each run, so
  repeated runs return the same tuples.
- `render_prompt("incident_triage", args)` — returns a list of exactly
  2 message dicts; the first is a text message mentioning the `service`
  argument, the second has `content.type == "resource"` with
  `content.resource.uri == "docs://guides/incident-response"`. Unknown
  prompt names raise `KeyError`.
- `boundary_review(DEMO_SURFACE)` — returns exactly 2 violations, in
  order: `refund_payment` ("state-changing capability exposed as
  resource") and `weekly_report_playbook` ("user playbook buried as
  tool"). A clean surface returns `[]`.
- `handle_message(msg)` — JSON-RPC 2.0 in/out; an unknown method returns
  an `error` with code `-32601`.
