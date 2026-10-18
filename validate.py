"""Validation harness for the Skool Course 3 code repo.

16 numbered checks in the Course 2 style. Each demo runs end-to-end in a
fresh interpreter (so the demo's own assertions execute); key behaviors are
additionally re-verified at the API level against the functions documented
in each demo's README. On a full green run this script writes RESULTS.md
itself (check 16 verifies the docs; the results file is written by main).
Exit code 0 = green.

Usage:
    python validate.py
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# (section dir, package name, success marker)
DEMOS = (
    ("s01/hello_mcp", "hello_mcp", "hello_mcp demo: OK"),
    ("s02/fundamentals", "fundamentals", "fundamentals demo: OK"),
    ("s03/transports", "transports", "transports demo: OK"),
    ("s04/first_server", "first_server", "first_server demo: OK"),
    ("s05/primitives", "primitives", "primitives demo: OK"),
    ("s06/enterprise", "enterprise", "enterprise demo: OK"),
    ("s07/security", "security", "security demo: OK"),
    ("s08/orchestration", "orchestration", "orchestration demo: OK"),
    ("s09/comparison", "comparison", "comparison demo: OK"),
    ("s10/testing", "testing", "testing demo: OK"),
    ("s11/production", "production", "production demo: OK"),
    ("s12/ecosystem", "ecosystem", "ecosystem demo: OK"),
    ("s13/capstone", "capstone", "capstone demo: OK"),
)

results: list[tuple[str, str]] = []


def check(name: str, fn) -> None:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - harness reports the check + error
        results.append((name, f"FAIL: {exc}"))
    else:
        results.append((name, "PASS"))


def run_demo(section: str, marker: str) -> None:
    """Run `python demo.py` inside the demo directory."""
    proc = subprocess.run(
        [sys.executable, "demo.py"],
        cwd=REPO_ROOT / section,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"{section}/demo.py exited {proc.returncode}\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    assert marker in proc.stdout, f"{section} missing marker {marker!r}:\n{proc.stdout}"


def load_demo(section: str, modname: str):
    """Import a demo.py by path (unique module name per demo)."""
    path = REPO_ROOT / section / "demo.py"
    spec = importlib.util.spec_from_file_location(modname, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module  # dataclasses resolve via sys.modules
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- checks
def check_01_structure() -> None:
    assert len(DEMOS) == 13, f"expected 13 demos, listed {len(DEMOS)}"
    for section, _, _ in DEMOS:
        d = REPO_ROOT / section
        assert (d / "demo.py").is_file(), f"missing {section}/demo.py"
        assert (d / "README.md").is_file(), f"missing {section}/README.md"
    for name in ("requirements.txt", ".gitignore", "LICENSE", "README.md",
                 "validate.py"):
        assert (REPO_ROOT / name).is_file(), f"missing root file {name}"


def check_02_s01() -> None:
    run_demo("s01/hello_mcp", "hello_mcp demo: OK")
    m = load_demo("s01/hello_mcp", "s01_hm")
    assert m.nxm_counts(5, 3) == (15, 8), m.nxm_counts(5, 3)
    assert m.nxm_counts(3, 3) == (9, 6)


def check_03_s02() -> None:
    run_demo("s02/fundamentals", "fundamentals demo: OK")
    m = load_demo("s02/fundamentals", "s02_fu")
    assert m.classify_primitive({"who_decides": "model"}) == "tool"
    assert m.classify_primitive({"who_decides": "application"}) == "resource"
    assert m.classify_primitive({"who_decides": "user"}) == "prompt"
    trace = m.three_role_trace({"text": "add 2 and 3"})
    assert len(trace) == 5, trace
    assert [step[0] for step in trace] == [
        "host", "client", "server", "client", "host"], trace


def check_04_s03() -> None:
    run_demo("s03/transports", "transports demo: OK")
    m = load_demo("s03/transports", "s03_tr")
    surface = m.anatomy_inspector(m.TransportServer())
    assert surface["tools"] == ["echo", "add"], surface
    assert set(surface["transports"]) == {"stdio", "http"}, surface


def check_05_s04() -> None:
    run_demo("s04/first_server", "first_server demo: OK")
    m = load_demo("s04/first_server", "s04_fs")
    assert len(m.find_mistakes(m.BROKEN_CONFIG)) == 5
    assert m.find_mistakes(m.FIXED_CONFIG) == []
    assert m.check_declaration(m.OVER_DECLARING_SERVER) == ["resources"]
    assert m.check_declaration(m.CORRECTED_SERVER) == []
    errs = m.validate_args(
        {"type": "object",
         "properties": {"text": {"type": "string", "maxLength": 10}},
         "required": ["text"]},
        {},
    )
    assert [e["code"] for e in errs] == ["missing_required"], errs


def check_06_s05() -> None:
    run_demo("s05/primitives", "primitives demo: OK")
    m = load_demo("s05/primitives", "s05_pr")
    assert m.run_task_suite("monolith") == (2, 4)
    assert m.run_task_suite("toolset") == (4, 4)
    violations = m.boundary_review(m.DEMO_SURFACE)
    names = {v if isinstance(v, str) else v.get("name") for v in violations}
    assert names == {"refund_payment", "weekly_report_playbook"}, names


def check_07_s06() -> None:
    run_demo("s06/enterprise", "enterprise demo: OK")
    m = load_demo("s06/enterprise", "s06_en")
    assert m.http_error_class(404) == ("not_found", "caller-fixable")
    assert m.http_error_class(429) == ("rate_limited", "retryable")
    assert m.http_error_class(500) == ("upstream_error", "fatal")
    scenario = m.run_ticketing_scenario()
    assert scenario["status"] == "resolved", scenario
    assert scenario["quota_used"] == 3 and scenario["quota"] == 6, scenario
    register = {row["tool"]: row for row in m.safety_register()}
    assert register and all(
        row["tier"] in ("read", "write") for row in register.values()
    ), register


def check_08_s07() -> None:
    run_demo("s07/security", "security demo: OK")
    m = load_demo("s07/security", "s07_se")
    assert m.naive_client(m.POISONED_RECORD) == "refund"
    assert m.defended_client(m.POISONED_RECORD) == "escalate"
    tok = m.make_token(["read"], 100)
    assert m.auth_check(tok, "read", 50) == (True, "ok")
    assert m.auth_check(tok, "write", 50) == (False, "missing scope: write")
    assert m.auth_check(tok, "read", 200) == (False, "expired")


def check_09_s08() -> None:
    run_demo("s08/orchestration", "orchestration demo: OK")
    m = load_demo("s08/orchestration", "s08_or")
    registry = m.Registry()
    registry.register("ticketing", m.TicketingServer())
    registry.register("accounts", m.AccountsServer())
    registry.register("billing", m.BillingServer())
    discovered = registry.discover()
    assert set(discovered) == {"ticketing", "accounts", "billing"}, discovered


def check_10_s09() -> None:
    run_demo("s09/comparison", "comparison demo: OK")
    m = load_demo("s09/comparison", "s09_co")
    assert m.integration_count("bespoke", 5, 3) == 15
    assert m.integration_count("function_calling", 5, 3) == 15
    assert m.integration_count("mcp", 5, 3) == 8
    expected = m.mcp_lookup("T-1001")
    assert expected is not None and expected["ticket_id"] == "T-1001"
    assert m.function_calling_lookup("T-1001") == expected
    assert m.bespoke_lookup("T-1001") == expected


def check_11_s10() -> None:
    run_demo("s10/testing", "testing demo: OK")
    m = load_demo("s10/testing", "s10_te")
    assert m.unit_test_suite(m.normalize_ticket_priority) == (6, 0, [])
    assert m.unit_test_suite(m.broken_normalize) == (5, 1, ["urgent_maps_to_p1"])
    assert m.regression_gate(m.normalize_ticket_priority) is True
    assert m.regression_gate(m.broken_normalize) is False


def check_12_s11() -> None:
    run_demo("s11/production", "production demo: OK")
    m = load_demo("s11/production", "s11_pd")
    ids = m.run_calls()
    assert ids == ["corr-A", "corr-B"], ids
    timeline = m.reconstruct_timeline("corr-A")
    assert len(timeline) == 3, timeline
    stdio_manifest, http_manifest = m.package_manifests()
    assert stdio_manifest["transport"] != http_manifest["transport"]


def check_13_s12() -> None:
    run_demo("s12/ecosystem", "ecosystem demo: OK")
    m = load_demo("s12/ecosystem", "s12_ec")
    assert m.classify_connection({"direction": "agent->tool"}) == "mcp"
    assert m.classify_connection({"direction": "agent->agent"}) == "a2a"
    assert m.classify_connection({"direction": "human->app"}) == "neither"


def check_14_s13() -> None:
    run_demo("s13/capstone", "capstone demo: OK")
    m = load_demo("s13/capstone", "s13_ca")
    design = m.fill_template(m.SAMPLE_BRIEF)
    assert m.check_design(design) == (True, [])
    passed, missing = m.check_design({})
    assert passed is False
    assert set(missing) == {"design and scope", "security", "reliability",
                            "testing", "operations", "governance"}, missing
    assert len(m.roadmap_plan(design)) == 5


SECRET_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    r"password\s*=\s*[\"'][^\"']+[\"']",
    r"passwd\s*=\s*[\"'][^\"']+[\"']",
    r"secret\s*=\s*[\"'][^\"']+[\"']",
    r"api[_-]?key\s*=\s*[\"'][^\"']+[\"']",
    r"token\s*=\s*[\"'][^\"']{8,}[\"']",
)]


def check_15_no_secrets() -> None:
    hits = []
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".md", ".txt", ".ini"}:
            continue
        if path.name in {"RESULTS.md"}:
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            if any(p.search(line) for p in SECRET_PATTERNS):
                hits.append(f"{path.relative_to(REPO_ROOT)}:{i}: {line.strip()}")
    assert not hits, "hardcoded secrets found:\n" + "\n".join(hits)


def check_16_docs() -> None:
    """README documents every demo + lesson mapping (RESULTS.md is written
    by main() itself, right after this check passes)."""
    readme = (REPO_ROOT / "README.md").read_text()
    for section, pkg, _ in DEMOS:
        assert pkg in readme, f"README missing demo {pkg}"
        assert section in readme, f"README missing path {section}"
    assert readme.count("Lesson") >= 50, "README lesson mapping looks thin"


# ------------------------------------------------------------- RESULTS.md
def write_results() -> Path:
    ist = timezone(timedelta(hours=5, minutes=30))
    stamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M IST")
    py = sys.version.split()[0]
    failed = [n for n, s in results if s.startswith("FAIL")]
    lines = [
        "# Validation Results — Skool Course 3 Code Repo",
        "",
        "Course: **MCP Architecture: Building Tool-Using AI Systems** (Skool-exclusive)",
        "Repo: `~/workspace/udemy-skool/skool-course-3-mcp-architecture/code-repo/`",
        f"Date of validated run: {stamp}",
        f"Environment: Python {py}, standard library only (matches `requirements.txt`)",
        "",
        "## Command run",
        "",
        "```bash",
        "cd ~/workspace/udemy-skool/skool-course-3-mcp-architecture/code-repo",
        "python validate.py",
        "```",
        "",
        "`validate.py` runs each of the 13 demos end-to-end in a fresh interpreter",
        "(so every demo's own assertions execute), re-verifies key behaviors at the",
        "API level, runs the repo-wide secrets scan, and checks the docs. Exit",
        "code 0 = green. This file was written by the validation run itself.",
        "",
        "## Result: " + ("ALL GREEN" if not failed else "FAILURES PRESENT"),
        "",
        "```",
    ]
    for name, status in results:
        lines.append(f"[{status.split(':')[0]:4s}] {name}")
    if failed:
        lines.append(f"{len(failed)} CHECK(S) FAILED")
    else:
        lines.append(f"ALL CHECKS PASSED ({len(results)}/16 green)")
    lines += ["```", "",
              "Every demo was also run individually during development with",
              "`python demo.py` inside its directory; each ends with its own",
              "`\"<demo> demo: OK\"` marker.",
              "",
              "## What was NOT done",
              "",
              "- No videos built, no uploads, no publishing, no GitHub push —",
              "  code only, per the task.",
              "- No network/API usage anywhere except s03's localhost",
              "  transports (stdio subprocess + ephemeral-port HTTP).",
              "- No real secrets anywhere; s07's tokens are deterministic",
              "  fixtures built by string concatenation at runtime.",
              ""]
    out = REPO_ROOT / "RESULTS.md"
    out.write_text("\n".join(lines))
    return out


def main() -> None:
    checks = [
        ("01 repo structure (13 demos + root files)", check_01_structure),
        ("02 s01 hello_mcp runs + N×M arithmetic", check_02_s01),
        ("03 s02 fundamentals sorter + three-role trace", check_03_s02),
        ("04 s03 transports anatomy inspector", check_04_s03),
        ("05 s04 first_server declaration + mistake hunt", check_05_s04),
        ("06 s05 primitives task suite + boundary review", check_06_s05),
        ("07 s06 enterprise error classes + ticketing quota", check_07_s06),
        ("08 s07 security injection drill + token auth", check_08_s07),
        ("09 s08 orchestration registry discovery", check_09_s08),
        ("10 s09 comparison three-way lookup + counts", check_10_s09),
        ("11 s10 testing unit suites + regression gate", check_11_s10),
        ("12 s11 production timeline + manifests", check_12_s11),
        ("13 s12 ecosystem connection classifier", check_13_s12),
        ("14 s13 capstone design check + roadmap", check_14_s13),
        ("15 no hardcoded secrets", check_15_no_secrets),
        ("16 README documents demos + lesson mapping", check_16_docs),
    ]
    for name, fn in checks:
        check(name, fn)

    results_path = write_results()
    assert results_path.is_file()

    print()
    print("=" * 60)
    for name, status in results:
        print(f"[{status.split(':')[0]:4s}] {name}")
    failed = [n for n, s in results if s.startswith("FAIL")]
    if failed:
        print(f"\n{len(failed)} CHECK(S) FAILED")
        sys.exit(1)
    print(f"\nALL CHECKS PASSED ({len(results)}/16 green)")
    print(f"RESULTS.md written by this run: {results_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
