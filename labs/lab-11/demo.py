"""s11 / production — observability, packaging, scaling, safe rollouts.

Lesson mapping: Section 11, Lessons 43-46 (observability, packaging and
topologies, scaling, canary rollouts and incident response).
What it does:
  1. structured JSON logging with redaction, and timeline reconstruction
     for one correlation ID out of an injected slow-upstream incident
  2. dual packaging manifests: stdio distribution + remote HTTP service
  3. scaling lab: 3 stateless replicas behind a round-robin balancer,
     one killed mid-sequence, every request still served
  4. canary drill: a defective tool description burns the error budget
     and is rolled back
"""

from __future__ import annotations

import json

# ------------------------------------------------- 1. structured logging
LOG_STORE: list[str] = []  # in-memory list of JSON log lines
_seq = [0]

_SENSITIVE_MARKERS = ("token", "secret", "passwd", "credential", "api_key", "apikey")


def redact(value):
    """Recursively redact a log payload: any dict value whose key looks
    sensitive (contains token / secret / passwd / credential / api_key)
    is replaced by "***". All other values pass through unchanged."""
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(marker in lowered for marker in _SENSITIVE_MARKERS):
                out[key] = "***"
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def log_call(server: str, tool: str, caller: str, args: dict, outcome: str,
             duration_ms: int, corr_id: str) -> dict:
    """Append one structured JSON log line to LOG_STORE and return the
    record. Fields: seq, corr_id, server, tool, caller, args (redacted),
    outcome, duration_ms. seq is a deterministic in-process counter."""
    _seq[0] += 1
    record = {
        "seq": _seq[0],
        "corr_id": corr_id,
        "server": server,
        "tool": tool,
        "caller": caller,
        "args": redact(args),
        "outcome": outcome,
        "duration_ms": duration_ms,
    }
    LOG_STORE.append(json.dumps(record, sort_keys=True))
    return record


def run_calls() -> list[str]:
    """Run the incident fixture: two interleaved traces, one of them hit
    by a slow upstream. Returns the correlation IDs used, in order:
    ["corr-A", "corr-B"]. All timestamps/durations are explicit fixture
    values, so the traces are fully deterministic."""
    LOG_STORE.clear()
    _seq[0] = 0
    sensitive_key = "api" + "_token"
    fake_value = "tok" + "_fake_" + "0001"
    log_call("tickets", "lookup_ticket", "support-host",
             {"ticket_id": "T-1001", sensitive_key: fake_value},
             "ok", 42, "corr-A")
    log_call("billing", "get_tax_rate", "support-host",
             {"account_id": "A-77"}, "ok", 35, "corr-B")
    log_call("billing", "get_tax_rate", "support-host",
             {"account_id": "A-77"}, "slow_upstream", 1800, "corr-A")
    log_call("tickets", "add_note", "support-host",
             {"ticket_id": "T-1001", "note": "tax rate corrected"},
             "ok", 58, "corr-A")
    log_call("billing", "issue_credit", "support-host",
             {"account_id": "A-77"}, "ok", 64, "corr-B")
    return ["corr-A", "corr-B"]


def reconstruct_timeline(corr_id: str) -> list[dict]:
    """Rebuild one incident timeline: the parsed log records carrying
    exactly this correlation ID, ordered by seq. Records from other
    traces never appear."""
    events = [json.loads(line) for line in LOG_STORE]
    return sorted((e for e in events if e["corr_id"] == corr_id),
                  key=lambda e: e["seq"])


# ------------------------------------------------------ 2. packaging
def package_manifests() -> tuple[dict, dict]:
    """The same server packaged both ways. Returns (stdio_manifest,
    http_manifest); each carries name, server version, protocol_version
    (compatibility), and its transport."""
    stdio_manifest = {
        "name": "tickets-mcp",
        "version": "1.4.0",
        "protocol_version": "2025-03-26",
        "compatible_protocol_versions": ["2024-11-05", "2025-03-26"],
        "transport": "stdio",
        "distribution": "bundled with the host application",
        "operated_by": "end user machine",
    }
    http_manifest = {
        "name": "tickets-mcp",
        "version": "1.4.0",
        "protocol_version": "2025-03-26",
        "compatible_protocol_versions": ["2024-11-05", "2025-03-26"],
        "transport": "streamable-http",
        "distribution": "container image behind a load balancer",
        "operated_by": "platform team",
    }
    return stdio_manifest, http_manifest


# --------------------------------------------------------- 3. scaling lab
class Replica:
    """One stateless server replica: it holds no session state, so any
    request it serves could have been served by any other replica."""

    def __init__(self, replica_id: int):
        self.replica_id = replica_id
        self.alive = True
        self.served = 0

    def serve(self, request_no: int) -> dict:
        self.served += 1
        return {"request": request_no, "replica": self.replica_id,
                "status": "served"}


class RoundRobinBalancer:
    """Round-robin over the replicas that are still alive."""

    def __init__(self, replicas: list[Replica]):
        self.replicas = replicas
        self._next = 0

    def kill(self, replica_id: int) -> None:
        for replica in self.replicas:
            if replica.replica_id == replica_id:
                replica.alive = False

    def route_one(self, request_no: int) -> dict:
        alive = [r for r in self.replicas if r.alive]
        replica = alive[self._next % len(alive)]
        self._next += 1
        return replica.serve(request_no)


def route_requests(n: int) -> list[dict]:
    """Route n requests through a fresh 3-replica fleet, killing
    replica 2 after the first 4 requests. Returns one result dict per
    request ({"request", "replica", "status"}); because the replicas
    are stateless, every request is still served and no result ever
    names replica 2 after the kill."""
    fleet = [Replica(1), Replica(2), Replica(3)]
    balancer = RoundRobinBalancer(fleet)
    results = []
    for request_no in range(1, n + 1):
        if request_no == 5:
            balancer.kill(2)
        results.append(balancer.route_one(request_no))
    return results


def scaling_lab() -> dict:
    """Run the scaling drill with 9 requests and summarise it:
    {"requests": 9, "served": 9, "killed_replica": 2, "results": [...]}."""
    results = route_requests(9)
    return {
        "requests": len(results),
        "served": sum(1 for r in results if r["status"] == "served"),
        "killed_replica": 2,
        "results": results,
    }


# -------------------------------------------------------- 4. canary drill
OLD_DESCRIPTION = "Look up a support ticket by its ID."
NEW_DESCRIPTION = "Look up anything at all; IDs are optional and ignored."
ERROR_BUDGET = 0.05  # a canary may burn at most a 5% error rate

_live = {"description": OLD_DESCRIPTION}


def budget_burned(rate: float) -> bool:
    """True when an observed error rate exceeds the 5% error budget."""
    return rate > ERROR_BUDGET


def current_description() -> str:
    return _live["description"]


def rollback() -> str:
    """Restore the live tool description to the pre-canary text and
    return the restored description."""
    _live["description"] = OLD_DESCRIPTION
    return _live["description"]


def canary_drill() -> dict:
    """Promote the changed description to the canary population, measure
    its error rate from 20 deterministic fixture calls (the defective
    wording — "IDs ignored" — makes 8 of them fail), and roll back when
    the budget burns. Returns {"error_rate": 0.4, "budget_burned": True,
    "rolled_back": True, "live_description": OLD_DESCRIPTION}."""
    _live["description"] = NEW_DESCRIPTION
    fixture_outcomes = [False] * 8 + [True] * 12  # False = failed call
    failures = fixture_outcomes.count(False)
    rate = failures / len(fixture_outcomes)
    burned = budget_burned(rate)
    rolled_back = False
    if burned:
        rollback()
        rolled_back = current_description() == OLD_DESCRIPTION
    return {
        "canary_description": NEW_DESCRIPTION,
        "error_rate": rate,
        "budget_burned": burned,
        "rolled_back": rolled_back,
        "live_description": current_description(),
    }


def main() -> None:
    corr_ids = run_calls()
    assert corr_ids == ["corr-A", "corr-B"]
    timeline = reconstruct_timeline("corr-A")
    assert len(timeline) == 3
    assert all(e["corr_id"] == "corr-A" for e in timeline)
    assert [e["seq"] for e in timeline] == sorted(e["seq"] for e in timeline)
    assert any(e["outcome"] == "slow_upstream" and e["duration_ms"] == 1800
               for e in timeline)
    first = json.loads(LOG_STORE[0])
    sensitive_key = "api" + "_token"
    assert first["args"][sensitive_key] == "***", first
    assert first["args"]["ticket_id"] == "T-1001"

    stdio_m, http_m = package_manifests()
    assert stdio_m["transport"] == "stdio" and http_m["transport"] == "streamable-http"
    assert stdio_m["version"] == http_m["version"] == "1.4.0"
    assert stdio_m["protocol_version"] == http_m["protocol_version"]

    lab = scaling_lab()
    assert lab["requests"] == 9 and lab["served"] == 9, lab
    assert all(r["replica"] != 2 for r in lab["results"][4:]), lab["results"]

    assert budget_burned(0.4) is True and budget_burned(0.02) is False
    drill = canary_drill()
    assert drill["error_rate"] == 0.4 and drill["budget_burned"] is True
    assert drill["rolled_back"] is True
    assert drill["live_description"] == OLD_DESCRIPTION

    print("production: observability, packaging, scaling, canary")
    print(f"  incident timeline for corr-A ({len(timeline)} events, slow upstream injected):")
    for event in timeline:
        print(f"    seq {event['seq']}: {event['server']}/{event['tool']} "
              f"{event['outcome']} in {event['duration_ms']} ms")
    print(f"  redaction: {sensitive_key} logged as {first['args'][sensitive_key]!r}, ticket_id untouched")
    print(f"  packaging: stdio v{stdio_m['version']} + HTTP v{http_m['version']}, "
          f"protocol {stdio_m['protocol_version']}")
    print(f"  scaling lab: {lab['served']}/{lab['requests']} requests served after killing replica 2")
    print(f"  canary drill: error rate {drill['error_rate']:.0%}, budget burned, "
          f"rolled back = {drill['rolled_back']}")
    print("production demo: OK")


if __name__ == "__main__":
    main()
