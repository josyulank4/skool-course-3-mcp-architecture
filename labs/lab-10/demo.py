"""s10 / testing — unit + contract + integration + adversarial, one gate.

Lesson mapping: Section 10, Lessons 39-42 (unit tests, contract tests,
integration with real and mock clients, adversarial + regression suites).
What it does:
  1. unit suite for a ticket-priority handler, with a planted-bug variant
     that fails exactly one named test
  2. contract tests: declared-vs-implemented capabilities and error-shape
     classes; a tightened schema field is classified "breaking"
  3. mock-client abuse sequences answered with structured errors
  4. adversarial fixtures refused by a defended pipeline, plus a golden
     regression gate — the full gate green on the good server
"""

from __future__ import annotations
_PRIORITY_MAP = {
    "urgent": "P1", "critical": "P1",
    "high": "P2",
    "normal": "P3", "medium": "P3",
    "low": "P4",
}

def normalize_ticket_priority(raw) -> str:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def broken_normalize(raw) -> str:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

UNIT_CASES = [
    ("urgent_maps_to_p1", "urgent", "P1"),
    ("critical_maps_to_p1", "critical", "P1"),
    ("high_maps_to_p2", "high", "P2"),
    ("medium_maps_to_p3", "medium", "P3"),
    ("low_maps_to_p4", "low", "P4"),
    ("blank_defaults_to_p3", "", "P3"),
]

def unit_test_suite(handler) -> tuple[int, int, list[str]]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

ERROR_CLASSES = {"caller_fixable", "retryable", "fatal"}

BASELINE_SCHEMA = {
    "type": "object",
    "properties": {
        "priority": {"type": "string",
                     "enum": ["urgent", "critical", "high", "normal",
                              "medium", "low"]},
        "ticket_id": {"type": "string"},
    },
    "required": ["priority"],
}

class SampleServer:
    """A minimal in-process server with a declared surface, an implemented
    surface, and structured errors. drifted=True tightens the declared
    priority enum (drops "urgent") — a breaking contract change."""
    def __init__(self, drifted: bool = False, handler=None):
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def _error(self, cls: str, message: str) -> dict:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def _call_normalize(self, args: dict) -> dict:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def call_tool(self, name: str, args) -> dict:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")

    def handle_message(self, message) -> dict:
        """TODO — implement this function.
        Watch the lab video: this function is built step by step,
        then diff your version against the lab finish tag."""
        raise NotImplementedError("your turn — see the lab video")


def make_server(drifted: bool = False) -> SampleServer:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def _schema_tightened(baseline: dict, current: dict) -> list[str]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def contract_test(server) -> list[str]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def run_abuse(server) -> dict:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

_INSTRUCTION_MARKERS = (
    "ignore your instructions", "ignore previous instructions",
    "refund everything", "send all", "exfiltrate",
    "you are now", "system prompt",
)

def adversarial_fixtures() -> list[dict]:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

def defended_pipeline(output) -> bool:
    """TODO — implement this function.
    Watch the lab video: this function is built step by step,
    then diff your version against the lab finish tag."""
    raise NotImplementedError("your turn — see the lab video")

GOLDEN_CONVERSATION = [
    ("urgent", "P1"), ("critical", "P1"), ("high", "P2"),
    ("normal", "P3"), ("low", "P4"), ("low", "P4"),
]

def regression_gate(handler) -> bool:
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
