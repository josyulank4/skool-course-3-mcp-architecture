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

# ------------------------------------------------------- shared fixture
# The one capability every approach implements: look up a support ticket.
TICKETS = {
    "T-1001": {"ticket_id": "T-1001", "title": "Invoice shows wrong tax rate",
               "status": "open", "priority": "P1"},
    "T-1002": {"ticket_id": "T-1002", "title": "Password reset loop",
               "status": "pending", "priority": "P3"},
    "T-1003": {"ticket_id": "T-1003", "title": "Export missing rows",
               "status": "closed", "priority": "P2"},
}


def _lookup(ticket_id: str) -> dict | None:
    """The underlying capability, shared by all three transports of it."""
    row = TICKETS.get(ticket_id)
    return dict(row) if row is not None else None


# ------------------------------------------- 1a. native function calling
# Provider-style declaration: a JSON-schema-flavoured dict the host sends
# with every API call, plus a dispatch table keyed by function name.
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
    return _lookup(ticket_id)


_FUNCTION_DISPATCH = {"lookup_ticket": _fn_lookup_ticket}


def function_calling_lookup(ticket_id: str) -> dict | None:
    """Native function calling: the model emits {name, arguments} in the
    provider's dialect; the host validates against FUNCTION_SCHEMA and
    dispatches. Returns the ticket dict, or None when not found."""
    call = {"name": "lookup_ticket", "arguments": {"ticket_id": ticket_id}}
    required = FUNCTION_SCHEMA["parameters"]["required"]
    for field in required:
        if field not in call["arguments"]:
            raise ValueError(f"missing required argument: {field}")
    handler = _FUNCTION_DISPATCH[call["name"]]
    return handler(**call["arguments"])


# ------------------------------------------------------- 1b. MCP (mini)
# A miniature MCP-shaped server: JSON-RPC 2.0 requests in, responses out.
# tools/list advertises the surface; tools/call invokes one tool.
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
    """Handle one JSON-RPC request dict; always returns a response dict."""
    req_id = request.get("id")
    method = request.get("method")
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}
    if method == "tools/call":
        params = request.get("params", {})
        if params.get("name") != "lookup_ticket":
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602, "message": "unknown tool"}}
        ticket = _lookup(params.get("arguments", {}).get("ticket_id", ""))
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"content": ticket, "isError": ticket is None}}
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": "method not found"}}


def mcp_lookup(ticket_id: str) -> dict | None:
    """MCP lookup: a real tools/list + tools/call round trip through
    mcp_handle. Returns the ticket dict, or None when not found."""
    listing = mcp_handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = [t["name"] for t in listing["result"]["tools"]]
    assert "lookup_ticket" in names, names
    response = mcp_handle({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "lookup_ticket",
                   "arguments": {"ticket_id": ticket_id}},
    })
    return response["result"]["content"]


# ---------------------------------------------------- 1c. bespoke protocol
# A hand-rolled, single-purpose protocol: {op, payload} envelopes that only
# this one consumer understands. Maximum control, zero reuse.
def bespoke_handle(envelope: dict) -> dict:
    if envelope.get("op") != "GET_TICKET":
        return {"ok": False, "error": "unsupported op"}
    ticket = _lookup(envelope.get("payload", {}).get("id", ""))
    return {"ok": ticket is not None, "data": ticket}


def bespoke_lookup(ticket_id: str) -> dict | None:
    """Bespoke lookup over the custom {op, payload} protocol. Returns the
    ticket dict, or None when not found."""
    reply = bespoke_handle({"op": "GET_TICKET", "payload": {"id": ticket_id}})
    return reply["data"] if reply["ok"] else None


# ------------------------------------------------- 2. integration counter
def integration_count(approach: str, n_surfaces: int, m_tools: int) -> int:
    """How many integrations must be built and maintained?

    Model: bespoke integrations and per-provider function calling couple
    every surface to every tool, so the count is N x M. MCP decouples the
    sides through one standard — each surface implements the client side
    once and each tool is built once as a server — so the count is N + M.
    """
    if approach == "mcp":
        return n_surfaces + m_tools
    if approach in ("function_calling", "bespoke"):
        return n_surfaces * m_tools
    raise ValueError(f"unknown approach: {approach}")


# ------------------------------------------------- 3. decision framework
# Documented fixture contexts (validate.py asserts these outcomes).
CONTEXT_FUNCTION_CALLING = {"models": 1, "teams": 1, "tools": 3,
                            "horizon": "short", "exotic": False}
CONTEXT_MCP = {"models": 3, "teams": 2, "tools": 12,
               "horizon": "long", "exotic": False}
CONTEXT_BESPOKE = {"models": 1, "teams": 1, "tools": 1,
                   "horizon": "short", "exotic": True}


def decision_framework(context: dict) -> str:
    """The book's decision framework, as deterministic rules, in order:

    1. An exotic single capability (unusual constraints no standard shape
       fits) -> "bespoke", knowingly.
    2. One model, one team, few tools (<= 5), short horizon
       -> "function_calling" earns its simplicity.
    3. Everything else (multiple models / teams / a growing tool estate /
       a long horizon) -> "mcp", where reuse compounds.
    """
    if context.get("exotic"):
        return "bespoke"
    if (context.get("models", 0) == 1 and context.get("teams", 0) == 1
            and context.get("tools", 0) <= 5
            and context.get("horizon") == "short"):
        return "function_calling"
    return "mcp"


# --------------------------------------------------- 4. migration planner
SAMPLE_INTEGRATION = {
    "name": "legacy ticket API client",
    "capability": "ticket lookup",
    "consumers": ["support console", "triage bot", "weekly report job"],
}


def migration_plan(integration: dict) -> list[str]:
    """Ordered migration steps from a bespoke integration to MCP.

    Invariants: the MCP facade goes in front of the existing integration
    FIRST (wrap, don't rewrite); consumers then move one at a time, in the
    order listed; the retirement criteria for the bespoke path come LAST.
    """
    name = integration["name"]
    capability = integration.get("capability", "the capability")
    steps = [
        f"Step 1: Build an MCP facade in front of {name} exposing "
        f"{capability}; the bespoke path keeps serving all traffic.",
    ]
    for i, consumer in enumerate(integration.get("consumers", []), start=2):
        steps.append(
            f"Step {i}: Migrate consumer '{consumer}' to the MCP facade "
            f"and verify its {capability} results match the bespoke path.")
    steps.append(
        f"Step {len(steps) + 1}: Retire the bespoke path only when every "
        "consumer runs on the facade, result parity has held for a full "
        "release cycle, and no bespoke-path calls appear in the audit log.")
    return steps


def main() -> None:
    expected = TICKETS["T-1001"]
    for lookup in (function_calling_lookup, mcp_lookup, bespoke_lookup):
        assert lookup("T-1001") == expected, lookup.__name__
        assert lookup("T-9999") is None, lookup.__name__

    assert integration_count("bespoke", 5, 3) == 15
    assert integration_count("function_calling", 5, 3) == 15
    assert integration_count("mcp", 5, 3) == 8

    assert decision_framework(CONTEXT_FUNCTION_CALLING) == "function_calling"
    assert decision_framework(CONTEXT_MCP) == "mcp"
    assert decision_framework(CONTEXT_BESPOKE) == "bespoke"

    plan = migration_plan(SAMPLE_INTEGRATION)
    assert "facade" in plan[0].lower()
    assert "Retire" in plan[-1]
    assert len(plan) == 2 + len(SAMPLE_INTEGRATION["consumers"])

    print("comparison: one capability (ticket lookup), three ways")
    print(f"  function calling -> {json.dumps(function_calling_lookup('T-1001'), sort_keys=True)}")
    print(f"  MCP (tools/call) -> {json.dumps(mcp_lookup('T-1001'), sort_keys=True)}")
    print(f"  bespoke protocol -> {json.dumps(bespoke_lookup('T-1001'), sort_keys=True)}")
    print("  all three agree on T-1001; all three return None for T-9999")
    print("integration count, 5 surfaces x 3 tools:")
    print(f"  bespoke / function calling: {integration_count('bespoke', 5, 3)} (N x M)")
    print(f"  MCP:                        {integration_count('mcp', 5, 3)} (N + M)")
    print("decision framework:")
    print(f"  single model/team, few tools, short horizon -> {decision_framework(CONTEXT_FUNCTION_CALLING)}")
    print(f"  3 models, 2 teams, 12 tools, long horizon   -> {decision_framework(CONTEXT_MCP)}")
    print(f"  exotic single capability                    -> {decision_framework(CONTEXT_BESPOKE)}")
    print(f"migration plan for {SAMPLE_INTEGRATION['name']}:")
    for step in plan:
        print(f"  {step}")
    print("comparison demo: OK")


if __name__ == "__main__":
    main()
