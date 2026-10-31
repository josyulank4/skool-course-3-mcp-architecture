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

_SERVER_CATALOG = {
    "ticketing": {"name": "ticketing server", "reuse": 9, "risk": "low",
                  "has_write_tools": True},
    "account store": {"name": "account server", "reuse": 6, "risk": "low",
                      "has_write_tools": False},
    "billing configuration": {"name": "billing server", "reuse": 4,
                              "risk": "high", "has_write_tools": True},
}

def _server_for(system: str) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def fill_template(brief: dict) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _filled(section) -> bool:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def check_design(design: dict) -> tuple[bool, list[str]]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

_RISK_RANK = {"low": 0, "medium": 1, "high": 2}

def roadmap_plan(design: dict) -> list[str]:
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
