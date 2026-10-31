"""s09 / comparison — one capability, three ways to give a model tools.

Lesson mapping: Section 9, Lessons 36-38 (three ways, head-to-head, hybrids
and migration).
What it does:
  1. ticket lookup built three ways: native function calling, MCP
     (mini JSON-RPC tools/list + tools/call), and a bespoke custom protocol
  2. integration counter: N x M for per-pair approaches vs N + M for MCP
  3. decision framework: function_calling | mcp | bespoke from context
  4. migration planner: facade first, consumers one at a time, retire last
"""

from __future__ import annotations
import json
TICKETS = {
    "T-1001": {"ticket_id": "T-1001", "title": "Invoice shows wrong tax rate",
               "status": "open", "priority": "P1"},
    "T-1002": {"ticket_id": "T-1002", "title": "Password reset loop",
               "status": "pending", "priority": "P3"},
    "T-1003": {"ticket_id": "T-1003", "title": "Export missing rows",
               "status": "closed", "priority": "P2"},
}

def _lookup(ticket_id: str) -> dict | None:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

FUNCTION_SCHEMA = {
    "name": "lookup_ticket",
    "description": "Look up a support ticket by its ID.",
    "parameters": {
        "type": "object",
        "properties": {"ticket_id": {"type": "string"}},
        "required": ["ticket_id"],
    },
}

def _fn_lookup_ticket(ticket_id: str) -> dict | None:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

_FUNCTION_DISPATCH = {"lookup_ticket": _fn_lookup_ticket}

def function_calling_lookup(ticket_id: str) -> dict | None:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

MCP_TOOLS = [
    {
        "name": "lookup_ticket",
        "description": "Look up a support ticket by its ID.",
        "inputSchema": {
            "type": "object",
            "properties": {"ticket_id": {"type": "string"}},
            "required": ["ticket_id"],
        },
    }
]

def mcp_handle(request: dict) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def mcp_lookup(ticket_id: str) -> dict | None:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def bespoke_handle(envelope: dict) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def bespoke_lookup(ticket_id: str) -> dict | None:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def integration_count(approach: str, n_surfaces: int, m_tools: int) -> int:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

CONTEXT_FUNCTION_CALLING = {"models": 1, "teams": 1, "tools": 3,
                            "horizon": "short", "exotic": False}

CONTEXT_MCP = {"models": 3, "teams": 2, "tools": 12,
               "horizon": "long", "exotic": False}

CONTEXT_BESPOKE = {"models": 1, "teams": 1, "tools": 1,
                   "horizon": "short", "exotic": True}

def decision_framework(context: dict) -> str:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

SAMPLE_INTEGRATION = {
    "name": "legacy ticket API client",
    "capability": "ticket lookup",
    "consumers": ["support console", "triage bot", "weekly report job"],
}

def migration_plan(integration: dict) -> list[str]:
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
