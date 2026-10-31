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
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

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
