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

RESOURCE_TEMPLATES = ("db://customers/{id}", "db://tickets/{id}", "docs://guides/{slug}")

class ResourceStore:
    """Application-controlled reads: templates resolve to stable URIs."""
    def __init__(self) -> None:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def resolve(self, template: str, params: dict) -> str:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def resolve_template(self, template: str, params: dict) -> str:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def read(self, uri: str) -> dict:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def list_resources(self) -> list[str]:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")


STORE = ResourceStore()

_customers = copy.deepcopy(CUSTOMERS)

_tickets = copy.deepcopy(TICKETS)

def reset_state() -> None:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def get_customer(customer_id: int) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def update_ticket(ticket_id: int, status: str) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def search_tickets(query: str) -> list[dict]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

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
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

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
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def run_task_suite(impl) -> tuple[int, int]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

PROMPT_TEMPLATES = {
    "incident_triage": {
        "description": "User-invoked incident triage playbook.",
        "arguments": ["service", "severity", "summary"],
    },
}

def render_prompt(name: str, args: dict) -> list[dict]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

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
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def handle_message(msg: dict) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def main() -> None:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

if __name__ == "__main__":
    main()
