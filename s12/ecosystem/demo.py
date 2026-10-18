"""s12 / ecosystem — MCP vs A2A directions, and an adopt/build/buy/wait note.

Lesson mapping: Section 12, Lessons 47-48 (A2A and MCP: two protocols,
two directions; governance, trust, and future-proofing).
What it does:
  1. protocol map: classify each connection in an estate as mcp (agent
     down to tools/data), a2a (agent sideways to agent), or neither
  2. position note: per capability family, adopt / build / buy / wait,
     each with the trigger that would change the answer
"""

from __future__ import annotations

# ------------------------------------------------ 1. protocol map (L47)
# A connection description states who initiates and what kind of thing
# sits on the other end. Documented fixtures (validate.py asserts these):
FIXTURE_CONNECTIONS = [
    {"name": "support agent reads tickets",
     "from_kind": "agent", "to_kind": "tool", "expected": "mcp"},
    {"name": "agent queries the account database",
     "from_kind": "agent", "to_kind": "data", "expected": "mcp"},
    {"name": "triage agent hands a case to the billing agent",
     "from_kind": "agent", "to_kind": "agent", "expected": "a2a"},
    {"name": "analyst opens the reporting app",
     "from_kind": "human", "to_kind": "app", "expected": "neither"},
    {"name": "nightly warehouse sync",
     "from_kind": "batch", "to_kind": "data", "expected": "neither"},
]


def classify_connection(description: dict) -> str:
    """Classify one connection by direction:

    - agent -> agent            -> "a2a"  (agents sideways to each other)
    - agent -> tool or data     -> "mcp"  (an agent down to its tools/data)
    - anything else (a human driving an app, a batch sync, ...) -> "neither"

    The description may use from_kind/to_kind fields or a single
    "direction" string such as "agent->tool".
    """
    from_kind = description.get("from_kind")
    to_kind = description.get("to_kind")
    if from_kind is None and "direction" in description:
        parts = description["direction"].replace(" ", "").split("->")
        if len(parts) == 2:
            from_kind, to_kind = parts
    if from_kind == "agent" and to_kind == "agent":
        return "a2a"
    if from_kind == "agent" and to_kind in ("tool", "tools", "data"):
        return "mcp"
    return "neither"


# --------------------------------------------- 2. position note (L48)
# An estate describes each capability family on four facts. Documented
# fixture (validate.py asserts these decisions):
SAMPLE_ESTATE = {
    "file search": {"commodity": True, "vendors": 6, "differentiating": False,
                    "standard_mature": True, "open_standard": True},
    "payment processing": {"commodity": True, "vendors": 5,
                           "differentiating": False, "standard_mature": True,
                           "open_standard": False},
    "ticket triage (our workflow)": {"commodity": False, "vendors": 1,
                                     "differentiating": True,
                                     "standard_mature": True,
                                     "open_standard": False},
    "agent memory store": {"commodity": False, "vendors": 2,
                           "differentiating": False, "standard_mature": False,
                           "open_standard": False},
}


def position_note(estate: dict) -> dict:
    """Decide adopt / build / buy / wait per capability family.

    Deterministic rules, applied in order:
    1. differentiating capability            -> "build" (it is your edge)
    2. the standard for the family is immature -> "wait"
    3. commodity, many vendors (>= 3), and an open standard exists
                                             -> "adopt" the standard server
    4. commodity with many vendors (>= 3)    -> "buy"
    5. anything else                         -> "wait"

    Returns {family: {"decision": ..., "trigger": ...}} where trigger is
    the change that would flip the decision.
    """
    note = {}
    for family, facts in estate.items():
        if facts.get("differentiating"):
            decision = "build"
            trigger = ("revisit if the capability stops differentiating "
                       "or a vendor matches it")
        elif not facts.get("standard_mature", False):
            decision = "wait"
            trigger = ("revisit when the standard for this family matures "
                       "or two credible vendors ship")
        elif facts.get("commodity") and facts.get("vendors", 0) >= 3 \
                and facts.get("open_standard"):
            decision = "adopt"
            trigger = ("revisit if the open server is abandoned or its "
                       "governance changes")
        elif facts.get("commodity") and facts.get("vendors", 0) >= 3:
            decision = "buy"
            trigger = ("revisit at contract renewal or if an open "
                       "standard server reaches parity")
        else:
            decision = "wait"
            trigger = ("revisit when the vendor field grows to 3+ credible "
                       "options or the need becomes differentiating")
        note[family] = {"decision": decision, "trigger": trigger}
    return note


def main() -> None:
    for conn in FIXTURE_CONNECTIONS:
        assert classify_connection(conn) == conn["expected"], conn["name"]
    assert classify_connection({"direction": "agent->agent"}) == "a2a"
    assert classify_connection({"direction": "agent->data"}) == "mcp"

    note = position_note(SAMPLE_ESTATE)
    assert note["file search"]["decision"] == "adopt"
    assert note["payment processing"]["decision"] == "buy"
    assert note["ticket triage (our workflow)"]["decision"] == "build"
    assert note["agent memory store"]["decision"] == "wait"
    assert all(entry["trigger"] for entry in note.values())

    print("ecosystem: protocol map")
    for conn in FIXTURE_CONNECTIONS:
        print(f"  {classify_connection(conn):>7}  {conn['name']}")
    print("position note (per capability family):")
    for family, entry in note.items():
        print(f"  {entry['decision']:>5}  {family} — trigger: {entry['trigger']}")
    print("ecosystem demo: OK")


if __name__ == "__main__":
    main()
