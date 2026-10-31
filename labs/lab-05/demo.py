"""s05 / primitives — the three primitives in depth.

Lesson mapping: Section 5, Lessons 18-21 (resources, tools, prompts, boundaries).
What it does:
  1. ResourceStore: URI templates -> concrete URIs -> readable content
  2. monolith_do_everything vs a clean toolset, scored on the same task suite
  3. incident_triage prompt template with one embedded resource reference
  4. boundary_review over a surface with exactly two planted violations
  Plus a small honest JSON-RPC 2.0 handler (initialize, tools/list,
  tools/call, resources/list, resources/read, prompts/list, prompts/get).
"""

from __future__ import annotations

import copy
import json

# ------------------------------------------------------------- fixtures
CUSTOMERS = {
    1: {"id": 1, "name": "Northwind Traders", "plan": "enterprise", "region": "eu-west"},
    2: {"id": 2, "name": "Contoso Retail", "plan": "standard", "region": "us-east"},
}

TICKETS = {
    101: {"id": 101, "customer_id": 1, "title": "Billing charged the wrong tax rate",
          "status": "open"},
    102: {"id": 102, "customer_id": 2, "title": "Users cannot login after SSO change",
          "status": "open"},
}

GUIDES = {
    "incident-response": "Acknowledge, classify severity, assign an owner, update hourly.",
    "billing-basics": "Check the account tax region before changing any rate.",
}

# ------------------------------------------------------- 1. resources
RESOURCE_TEMPLATES = ("db://customers/{id}", "db://tickets/{id}", "docs://guides/{slug}")


class ResourceStore:
    """Application-controlled reads: templates resolve to stable URIs."""

    def __init__(self) -> None:
        self._data = {
            "db://customers/1": dict(CUSTOMERS[1]),
            "db://customers/2": dict(CUSTOMERS[2]),
            "db://tickets/101": dict(TICKETS[101]),
            "db://tickets/102": dict(TICKETS[102]),
            "docs://guides/incident-response": {
                "slug": "incident-response", "text": GUIDES["incident-response"]},
            "docs://guides/billing-basics": {
                "slug": "billing-basics", "text": GUIDES["billing-basics"]},
        }

    def resolve(self, template: str, params: dict) -> str:
        """resolve('db://customers/{id}', {'id': 1}) -> 'db://customers/1'."""
        if template not in RESOURCE_TEMPLATES:
            raise ValueError(f"unknown template: {template}")
        uri = template
        for key, value in params.items():
            uri = uri.replace("{" + key + "}", str(value))
        if "{" in uri:
            raise ValueError(f"unresolved template parameters in {uri}")
        return uri

    # Alias named in the plan / lesson language.
    def resolve_template(self, template: str, params: dict) -> str:
        return self.resolve(template, params)

    def read(self, uri: str) -> dict:
        """read('db://customers/1') -> content dict (with its uri attached)."""
        if uri not in self._data:
            raise KeyError(f"no such resource: {uri}")
        content = copy.deepcopy(self._data[uri])
        content["uri"] = uri
        return content

    def list_resources(self) -> list[str]:
        """All concrete resource URIs, sorted."""
        return sorted(self._data)


STORE = ResourceStore()

# ------------------------------------------------------------ 2. tools
# Mutable working copies so update_ticket has real state to change.
_customers = copy.deepcopy(CUSTOMERS)
_tickets = copy.deepcopy(TICKETS)


def reset_state() -> None:
    global _customers, _tickets
    _customers = copy.deepcopy(CUSTOMERS)
    _tickets = copy.deepcopy(TICKETS)


def get_customer(customer_id: int) -> dict:
    if customer_id not in _customers:
        raise KeyError(f"no customer {customer_id}")
    return copy.deepcopy(_customers[customer_id])


def update_ticket(ticket_id: int, status: str) -> dict:
    if ticket_id not in _tickets:
        raise KeyError(f"no ticket {ticket_id}")
    _tickets[ticket_id]["status"] = status
    return copy.deepcopy(_tickets[ticket_id])


def search_tickets(query: str) -> list[dict]:
    q = query.lower()
    return [copy.deepcopy(t) for t in sorted(_tickets.values(), key=lambda t: t["id"])
            if q in t["title"].lower()]


TOOL_FUNCTIONS = {
    "get_customer": get_customer,
    "update_ticket": update_ticket,
    "search_tickets": search_tickets,
}

TOOL_SCHEMAS = {
    "get_customer": {
        "description": "Read one customer by id.",
        "inputSchema": {"type": "object",
                        "properties": {"customer_id": {"type": "integer"}},
                        "required": ["customer_id"]},
    },
    "update_ticket": {
        "description": "Set the status of one ticket.",
        "inputSchema": {"type": "object",
                        "properties": {"ticket_id": {"type": "integer"},
                                       "status": {"type": "string"}},
                        "required": ["ticket_id", "status"]},
    },
    "search_tickets": {
        "description": "Search ticket titles for a word or phrase.",
        "inputSchema": {"type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"]},
    },
}


def monolith_do_everything(action: str, **kw):
    """The pre-refactor fixture: one handler, substring dispatch.

    Its bug is dispatch order: it tests 'customer' first, then 'ticket',
    then 'update' -- so 'update_ticket' is routed to the search branch
    (it contains 'ticket') and 'search_customer_tickets' is routed to the
    customer branch (it contains 'customer'). Both are wrong-branch errors.
    """
    if "customer" in action:
        return get_customer(kw["customer_id"])
    if "ticket" in action or "search" in action:
        return search_tickets(kw.get("query", ""))
    if "update" in action:  # unreachable for update_ticket: 'ticket' matched first
        return update_ticket(kw["ticket_id"], kw["status"])
    raise ValueError(f"unknown action: {action}")


# Fixed task suite. `tool` is the exact toolset call; `action` is the
# natural action label the monolith receives for the same job.
TASKS = [
    {"name": "customer lookup", "tool": "get_customer", "action": "get_customer",
     "args": {"customer_id": 1}, "expected": {"id": 1, "name": "Northwind Traders"}},
    {"name": "tax ticket search", "tool": "search_tickets", "action": "search_tickets",
     "args": {"query": "tax"}, "expected": {"ids": [101]}},
    {"name": "resolve login ticket", "tool": "update_ticket", "action": "update_ticket",
     "args": {"ticket_id": 102, "status": "resolved"},
     "expected": {"id": 102, "status": "resolved"}},
    {"name": "customer ticket search", "tool": "search_tickets",
     "action": "search_customer_tickets",
     "args": {"query": "login"}, "expected": {"ids": [102]}},
]


def _matches(result, expected: dict) -> bool:
    if "ids" in expected:
        return isinstance(result, list) and [r["id"] for r in result] == expected["ids"]
    return isinstance(result, dict) and all(result.get(k) == v for k, v in expected.items())


def run_task_suite(impl) -> tuple[int, int]:
    """run_task_suite('monolith') -> (2, 4); run_task_suite('toolset') -> (4, 4).

    impl may also be the monolith function itself or the TOOL_FUNCTIONS dict.
    State is reset before each run, so runs are repeatable.
    """
    reset_state()
    if impl is monolith_do_everything:
        impl = "monolith"
    elif isinstance(impl, dict):
        impl = "toolset"
    passed = 0
    for task in TASKS:
        try:
            if impl == "monolith":
                result = monolith_do_everything(task["action"], **task["args"])
            elif impl == "toolset":
                result = TOOL_FUNCTIONS[task["tool"]](**task["args"])
            else:
                raise ValueError(f"unknown impl: {impl!r} (use 'monolith' or 'toolset')")
        except Exception:  # noqa: BLE001 - a raised call is a failed task
            result = None
        if result is not None and _matches(result, task["expected"]):
            passed += 1
    return passed, len(TASKS)


# ----------------------------------------------------------- 3. prompts
PROMPT_TEMPLATES = {
    "incident_triage": {
        "description": "User-invoked incident triage playbook.",
        "arguments": ["service", "severity", "summary"],
    },
}


def render_prompt(name: str, args: dict) -> list[dict]:
    """Render a prompt template to a list of message dicts.

    render_prompt('incident_triage', {...}) -> 2 messages: a text message
    carrying the arguments, then a message embedding one resource
    (docs://guides/incident-response).
    """
    if name != "incident_triage":
        raise KeyError(f"no prompt template: {name}")
    service = args.get("service", "general")
    severity = args.get("severity", "medium")
    summary = args.get("summary", "")
    guide = STORE.read("docs://guides/incident-response")
    return [
        {"role": "user",
         "content": {"type": "text",
                     "text": (f"Triage incident for service '{service}' "
                              f"(severity: {severity}). Summary: {summary} "
                              "Classify, assign an owner, and state the next update time.")}},
        {"role": "user",
         "content": {"type": "resource",
                     "resource": {"uri": guide["uri"], "text": guide["text"]}}},
    ]


# -------------------------------------------------- 4. boundary review
DEMO_SURFACE = [
    {"name": "customer_record", "primitive": "resource", "changes_state": False,
     "is_playbook": False},
    {"name": "refund_payment", "primitive": "resource", "changes_state": True,
     "is_playbook": False},
    {"name": "search_tickets", "primitive": "tool", "changes_state": False,
     "is_playbook": False},
    {"name": "update_ticket", "primitive": "tool", "changes_state": True,
     "is_playbook": False},
    {"name": "incident_triage", "primitive": "prompt", "changes_state": False,
     "is_playbook": True},
    {"name": "weekly_report_playbook", "primitive": "tool", "changes_state": False,
     "is_playbook": True},
]


def boundary_review(surface: list[dict]) -> list[dict]:
    """Flag primitive-boundary violations, in surface order.

    Rules: a state-changing capability must not be a resource; a user
    playbook must be a prompt, not buried in a tool. DEMO_SURFACE yields
    exactly 2 violations: refund_payment and weekly_report_playbook.
    """
    violations = []
    for item in surface:
        if item.get("primitive") == "resource" and item.get("changes_state"):
            violations.append({
                "name": item["name"],
                "violation": "state-changing capability exposed as resource",
            })
        elif item.get("is_playbook") and item.get("primitive") != "prompt":
            violations.append({
                "name": item["name"],
                "violation": "user playbook buried as tool",
            })
    return violations


# --------------------------------------------------------- JSON-RPC 2.0
def handle_message(msg: dict) -> dict:
    """One JSON-RPC 2.0 request dict -> one response dict."""
    method = msg.get("method")
    params = msg.get("params") or {}
    req_id = msg.get("id", 1)

    def ok(result):
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def err(code, message):
        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": code, "message": message}}

    try:
        if method == "initialize":
            return ok({"protocolVersion": "2025-06-18",
                       "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                       "serverInfo": {"name": "primitives-demo", "version": "1.0.0"}})
        if method == "tools/list":
            return ok({"tools": [{"name": n, **s} for n, s in TOOL_SCHEMAS.items()]})
        if method == "tools/call":
            fn = TOOL_FUNCTIONS[params["name"]]
            return ok({"content": [{"type": "text",
                                    "text": json.dumps(fn(**params.get("arguments", {})),
                                                         sort_keys=True)}],
                       "isError": False})
        if method == "resources/list":
            return ok({"resources": [{"uri": u} for u in STORE.list_resources()]})
        if method == "resources/read":
            content = STORE.read(params["uri"])
            return ok({"contents": [{"uri": params["uri"], "mimeType": "application/json",
                                     "text": json.dumps(content, sort_keys=True)}]})
        if method == "prompts/list":
            return ok({"prompts": [{"name": n, "description": t["description"],
                                    "arguments": [{"name": a} for a in t["arguments"]]}
                                   for n, t in PROMPT_TEMPLATES.items()]})
        if method == "prompts/get":
            return ok({"messages": render_prompt(params["name"],
                                                 params.get("arguments", {}))})
        return err(-32601, f"method not found: {method}")
    except (KeyError, ValueError) as exc:
        return err(-32602, str(exc))


def main() -> None:
    reset_state()
    print("primitives: resources via URI templates")
    uri = STORE.resolve("db://customers/{id}", {"id": 1})
    print(f"  resolve db://customers/{{id}} id=1 -> {uri}")
    print(f"  read {uri} -> {STORE.read(uri)['name']}")
    print(f"  resources: {STORE.list_resources()}")
    assert uri == "db://customers/1"
    assert STORE.read(uri)["name"] == "Northwind Traders"
    assert STORE.list_resources() == [
        "db://customers/1", "db://customers/2", "db://tickets/101",
        "db://tickets/102", "docs://guides/billing-basics",
        "docs://guides/incident-response",
    ]

    mono = run_task_suite("monolith")
    tool = run_task_suite("toolset")
    print(f"task suite: monolith {mono[0]}/{mono[1]} (wrong-branch errors), "
          f"toolset {tool[0]}/{tool[1]}")
    assert mono == (2, 4), mono
    assert tool == (4, 4), tool

    messages = render_prompt("incident_triage",
                             {"service": "billing", "severity": "high",
                              "summary": "Wrong tax rate charged"})
    print(f"prompt incident_triage: {len(messages)} messages, embedded resource "
          f"{messages[1]['content']['resource']['uri']}")
    assert len(messages) == 2
    assert messages[1]["content"]["resource"]["uri"] == "docs://guides/incident-response"

    violations = boundary_review(DEMO_SURFACE)
    print(f"boundary review: {len(violations)} violations")
    for v in violations:
        print(f"  {v['name']}: {v['violation']}")
    assert [v["name"] for v in violations] == ["refund_payment", "weekly_report_playbook"]

    resp = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": "search_tickets",
                                      "arguments": {"query": "tax"}}})
    print(f"JSON-RPC tools/call search_tickets -> {resp['result']['content'][0]['text']}")
    assert resp["result"]["isError"] is False
    resp = handle_message({"jsonrpc": "2.0", "id": 2, "method": "resources/read",
                           "params": {"uri": "db://customers/2"}})
    assert "Contoso Retail" in resp["result"]["contents"][0]["text"]

    print("primitives demo: OK")


if __name__ == "__main__":
    main()
