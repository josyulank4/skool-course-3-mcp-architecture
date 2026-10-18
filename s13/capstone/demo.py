"""s13 / capstone — design studio template, Appendix A gate, roadmap.

Lesson mapping: Section 13, Lessons 49-50 (capstone studio, durable
principles and your roadmap).
What it does:
  1. STUDIO_TEMPLATE: the design-document skeleton (architecture, safety
     register, security checklist, test plan, reliability, operations,
     governance)
  2. fill_template completes it from a brief — the wrong-tax-rate
     invoice workflow from the book's Introduction
  3. check_design grades a design against Appendix A's six production-
     readiness categories
  4. roadmap_plan sequences the build: highest-reuse / lowest-risk
     server first, facades before migrations, and the security gate
     before the first write tool
"""

from __future__ import annotations

import copy

# ------------------------------------------------------- 1. the template
STUDIO_TEMPLATE = {
    "architecture": {"workflow": "", "servers": [], "transports": {},
                     "primitives": {}},
    "safety_register": [],
    "security_checklist": {},
    "test_plan": {},
    "reliability": {},
    "operations": {},
    "governance": {},
}

APPENDIX_CATEGORIES = [
    "design and scope", "security", "reliability",
    "testing", "operations", "governance",
]

SAMPLE_BRIEF = {
    "workflow": "Resolve wrong-tax-rate invoice tickets end to end",
    "problem": "Customers are charged the wrong tax rate; an engineer "
               "resolves each ticket by hand across three systems.",
    "systems": ["ticketing", "account store", "billing configuration"],
}

# Per-system server designs: reuse score (consumers waiting), risk band,
# and whether the server exposes any write tool.
_SERVER_CATALOG = {
    "ticketing": {"name": "ticketing server", "reuse": 9, "risk": "low",
                  "has_write_tools": True},
    "account store": {"name": "account server", "reuse": 6, "risk": "low",
                      "has_write_tools": False},
    "billing configuration": {"name": "billing server", "reuse": 4,
                              "risk": "high", "has_write_tools": True},
}


def _server_for(system: str) -> dict:
    known = _SERVER_CATALOG.get(system)
    if known is not None:
        return {**known, "facade_over": system}
    return {"name": f"{system} server", "reuse": 1, "risk": "medium",
            "has_write_tools": False, "facade_over": system}


# --------------------------------------------------- 2. fill the template
def fill_template(brief: dict) -> dict:
    """Complete the studio template from a brief. Every section of the
    template is filled, so the result passes check_design in full."""
    design = copy.deepcopy(STUDIO_TEMPLATE)
    servers = [_server_for(system) for system in brief["systems"]]
    design["architecture"] = {
        "workflow": brief["workflow"],
        "servers": servers,
        "transports": {"local hosts": "stdio",
                       "shared services": "streamable-http"},
        "primitives": {
            "tools": "ticket search/update, tax-rate correction, credit issue",
            "resources": "ticket records and account records by URI",
            "prompts": "wrong-tax-rate triage playbook",
        },
    }
    design["safety_register"] = [
        {"tool": "search_tickets", "tier": "read", "approval": "none"},
        {"tool": "read_account", "tier": "read", "approval": "none"},
        {"tool": "correct_tax_rate", "tier": "write",
         "approval": "human approval, idempotency key required"},
        {"tool": "issue_credit", "tier": "write",
         "approval": "human approval, idempotency key required"},
    ]
    design["security_checklist"] = {
        "authentication": True, "least_privilege_scopes": True,
        "approval_gates_on_writes": True, "secrets_never_in_logs": True,
        "sandboxing": True, "audit_log_every_call": True,
        "injection_defenses_on_tool_outputs": True,
    }
    design["test_plan"] = {
        "unit": "every handler: happy path, boundaries, hostile inputs",
        "contract": "schemas and error shapes pinned against the baseline",
        "integration": "real client plus mock-client abuse sequences",
        "adversarial": "poisoned ticket notes must be refused as data",
        "regression": "golden conversation set replays on every change",
    }
    design["reliability"] = {
        "timeouts": "every tool call and upstream call times out",
        "retries": "backoff with idempotency keys on non-idempotent writes",
        "circuit_breakers": "one slow upstream cannot exhaust the server",
        "graceful_degradation": "documented behaviour per dead dependency",
        "health": "liveness signal reflects tool-surface health",
    }
    design["operations"] = {
        "logging": "structured logs with correlation IDs, redacted args",
        "metrics_alerting": "rate, latency, error rate per tool; alerting on spikes",
        "versioning": "versioned releases; clients compatibility-tested",
        "rollout": "canary with error budget and a rollback plan",
        "runbook": "common failures, diagnosis steps, paging owner",
    }
    design["governance"] = {
        "data_classification": "every resource and output classified",
        "pii_handling": "redaction and minimisation documented",
        "compliance_review": "principles documented for regulated data",
        "inventory": "servers registered with owner and deprecation policy",
    }
    return design


# ------------------------------------------- 3. Appendix A design check
def _filled(section) -> bool:
    """A section counts as present when it is a non-empty collection
    whose values are all truthy."""
    if not isinstance(section, (dict, list)) or not section:
        return False
    values = section.values() if isinstance(section, dict) else section
    return all(bool(v) for v in values)


def check_design(design: dict) -> tuple[bool, list[str]]:
    """Grade a design against Appendix A's six categories. Returns
    (passed, missing) with missing in Appendix order. Category mapping:
    "design and scope" needs a non-empty architecture (with servers)
    plus a safety register; "security" the security checklist;
    "testing" the test plan; "reliability", "operations", and
    "governance" their same-named sections — each fully filled."""
    architecture = design.get("architecture", {})
    checks = {
        "design and scope": bool(architecture.get("servers"))
            and _filled(design.get("safety_register")),
        "security": _filled(design.get("security_checklist")),
        "reliability": _filled(design.get("reliability")),
        "testing": _filled(design.get("test_plan")),
        "operations": _filled(design.get("operations")),
        "governance": _filled(design.get("governance")),
    }
    missing = [cat for cat in APPENDIX_CATEGORIES if not checks[cat]]
    return (not missing), missing


# ------------------------------------------------------ 4. roadmap plan
_RISK_RANK = {"low": 0, "medium": 1, "high": 2}


def roadmap_plan(design: dict) -> list[str]:
    """Sequence the build from a checked design. Servers are ordered
    highest-reuse / lowest-risk first; every server is built as a
    facade before any consumer migration; and the security-gate step is
    placed immediately before the step that builds the first server
    carrying a write tool. A final step migrates consumers one at a
    time onto the finished facades."""
    servers = sorted(
        design["architecture"]["servers"],
        key=lambda s: (_RISK_RANK[s["risk"]], -s["reuse"], s["name"]))
    bodies = []
    gate_placed = False
    for server in servers:
        if server["has_write_tools"] and not gate_placed:
            bodies.append("Security gate: pass the Appendix A security "
                          "checklist in full before the first write "
                          "tool ships.")
            gate_placed = True
        bodies.append(
            f"Build the {server['name']} as an MCP facade over the "
            f"{server['facade_over']} (reuse {server['reuse']}, "
            f"risk {server['risk']}).")
    if not gate_placed:
        bodies.append("Security gate: pass the Appendix A security "
                      "checklist in full before any write tool ships.")
    bodies.append("Migrate consumers one at a time onto the facades, "
                  "verify parity per consumer, and register every "
                  "server in the inventory.")
    return [f"Step {i}: {body}" for i, body in enumerate(bodies, start=1)]


def main() -> None:
    design = fill_template(SAMPLE_BRIEF)
    passed, missing = check_design(design)
    assert passed is True and missing == [], missing

    empty_passed, empty_missing = check_design({})
    assert empty_passed is False and empty_missing == APPENDIX_CATEGORIES

    stripped = fill_template(SAMPLE_BRIEF)
    del stripped["test_plan"], stripped["governance"]
    s_passed, s_missing = check_design(stripped)
    assert s_passed is False and s_missing == ["testing", "governance"], s_missing

    plan = roadmap_plan(design)
    gate_idx = next(i for i, s in enumerate(plan) if "Security gate" in s)
    ticketing_idx = next(i for i, s in enumerate(plan) if "ticketing server" in s)
    billing_idx = next(i for i, s in enumerate(plan) if "billing server" in s)
    assert gate_idx < ticketing_idx, plan  # gate before first write tool
    assert ticketing_idx < billing_idx, plan  # highest reuse / lowest risk first
    assert "Migrate consumers" in plan[-1], plan

    print("capstone: design studio for the wrong-tax-rate workflow")
    print(f"  servers: {', '.join(s['name'] for s in design['architecture']['servers'])}")
    print(f"  Appendix A check on the filled design: passed = {passed}, missing = {missing}")
    print(f"  stripped design (no test plan, no governance): missing = {s_missing}")
    print("  roadmap:")
    for step in plan:
        print(f"    {step}")
    print("capstone demo: OK")


if __name__ == "__main__":
    main()
