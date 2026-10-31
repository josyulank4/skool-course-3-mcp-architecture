# MCP Architecture — Code Repository (Skool Course 3)

**Course:** MCP Architecture: Building Tool-Using AI Systems (Skool-exclusive)
**Companion to:** *MCP Architecture: Building Tool-Using AI Systems* by Naveen Kumar Josyula

This repository is the hands-on half of the course. It contains **13 runnable demos — one per course section** — that implement the Model Context Protocol's mechanics in plain Python: real JSON-RPC 2.0 message handling, initialize handshakes, `tools/list` and `tools/call`, resources, prompts, both transports, security gates, multi-server orchestration, testing suites, and production patterns.

Everything runs on the **Python standard library only**. There is nothing to install, no API key, and no network access beyond a localhost transport demo (s03). These are patterns to copy into your own systems, not a framework to depend on.

## Quickstart

```bash
# 1. Verify the whole repository end to end (16 checks):
python validate.py

# 2. Run any single demo:
cd s01/hello_mcp
python demo.py        # ends with: hello_mcp demo: OK
```

`validate.py` runs every demo in a fresh interpreter, re-verifies key behaviors by importing the demos as libraries, scans the tree for hardcoded secrets, and checks these docs. A green run writes `RESULTS.md`. **Python 3.10+** (on systems where the interpreter is named `python3`, use `python3` everywhere).

## How to study

Watch a section's lessons, then run its demo, then re-run the demo against your own workload (your own systems, your own ticket) before moving on. The checklists and decision functions inside the demos are the durable artifacts.

## Demo map — section by section, tied to lessons

### s01 — `s01/hello_mcp` (hello_mcp) — Section 1: Welcome
A minimal MCP server + client: initialize handshake, tools/list, one tool call end to end, plus the capability audit and the N×M-versus-N+M integration counter.
- Lesson 1 — Welcome: The Protocol That Gives Agents Hands
- Lesson 2 — How to Use This Course and the Code Repository
- Lesson 3 — The Brilliant Prisoner: What Models Can and Cannot Do
- Lesson 4 — The N×M Problem: Why a Standard Had to Exist

### s02 — `s02/fundamentals` (fundamentals) — Section 2: Protocol Fundamentals
Discovery across all three primitives, a host→client→server three-role trace, the who-decides primitive sorter, and a capability-negotiation handshake capture.
- Lesson 5 — What MCP Is (and Is Not)
- Lesson 6 — Design Philosophy and the Three Roles
- Lesson 7 — The Three Primitives: Tools, Resources, and Prompts
- Lesson 8 — Lifecycle, Messages, and Versioning

### s03 — `s03/transports` (transports) — Section 3: Architecture & Transports
One server (`echo`, `add`) served two ways — as a stdio subprocess and as a Streamable HTTP endpoint — with an anatomy inspector and a three-way concurrent round-trip tracer.
- Lesson 9 — Separation of Concerns and Server Anatomy
- Lesson 10 — The stdio Transport: Local, Simple, Process-Bound
- Lesson 11 — Streamable HTTP: Remote, Stateless, Scalable
- Lesson 12 — Sessions, Concurrency, and a Full Round-Trip

### s04 — `s04/first_server` (first_server) — Section 4: Building Your First MCP Server
A buildable first server: metadata and capability declaration (with a checker that catches over-declaring), a JSON-Schema word-count tool with an adversarial input set, a two-way handshake lab, and the five-planted-mistakes hunt.
- Lesson 13 — The Minimal Server and Project Setup
- Lesson 14 — Metadata and Capability Declaration
- Lesson 15 — Your First Tool: JSON Schema Inputs
- Lesson 16 — The Initialization Handshake, Live
- Lesson 17 — Testing with the Inspector — and First-Server Mistakes

### s05 — `s05/primitives` (primitives) — Section 5: The Three Primitives in Depth
Resources with URI templates, a monolith tool refactored into a clean toolset (with a task-suite score comparison), a parameterized incident-triage prompt template, and a boundary review that catches two planted violations.
- Lesson 18 — Three Control Models and Resources in Depth
- Lesson 19 — Tools in Depth
- Lesson 20 — Prompts in Depth
- Lesson 21 — Roots, Sampling, Pagination — and Clean Boundaries

### s06 — `s06/enterprise` (enterprise) — Section 6: Connecting MCP to Enterprise Systems
Database, file-store, and REST wrappers behind one domain facade: traversal and injection guards, HTTP error translation, a read/write safety-tier register, and the wrong-tax-rate ticketing scenario resolved inside a rate-limit quota.
- Lesson 22 — The Adapter Pattern: MCP as a Facade
- Lesson 23 — Wrapping Databases and File Stores
- Lesson 24 — Wrapping REST APIs and SaaS Tools
- Lesson 25 — Upstream Authentication and Safety Tiers
- Lesson 26 — Rate Limits, Quotas, and the Ticketing Scenario

### s07 — `s07/security` (security) — Section 7: Security
The injection drill (a naive client obeys a poisoned record; a defended client refuses), scoped-token authentication with expiry, a human-approval gate for destructive calls, server-side authorization, and the security checklist runner. All credentials are obvious runtime-built fixtures — there are no real secrets in this repo.
- Lesson 27 — The New Attack Surface: Injection Through Tool Outputs
- Lesson 28 — Tool Poisoning, Rug Pulls, and the Confused Deputy
- Lesson 29 — Authentication: OAuth 2.1, Keys, and Tokens
- Lesson 30 — Least-Privilege Authorization and Human Approval
- Lesson 31 — Sandboxing, Audit Logging, and the Security Checklist

### s08 — `s08/orchestration` (orchestration) — Section 8: Multi-Server Orchestration
Three servers (ticketing, accounts, billing) behind a registry: discovery, a tool-name collision fixed by namespacing, a composed three-server workflow with a compensation path, and a failure-isolation drill.
- Lesson 32 — Why One Agent Needs Many Servers: Discovery
- Lesson 33 — Namespacing, Collisions, and Routing
- Lesson 34 — Composing Multi-Server Workflows
- Lesson 35 — Failure Isolation and Configuration Across Environments

### s09 — `s09/comparison` (comparison) — Section 9: MCP vs Function Calling vs Custom APIs
The same ticket-lookup capability built all three ways, the N×M/N+M integration arithmetic, the decision-framework function, and a facade-first migration planner.
- Lesson 36 — Three Ways to Give a Model Tools
- Lesson 37 — Head-to-Head: The Honest Comparison
- Lesson 38 — Hybrids and Migrating to MCP

### s10 — `s10/testing` (testing) — Section 10: Testing and Evaluating MCP Servers
The full test gate as code: unit suites (a planted handler bug fails exactly one named test), contract tests that classify a schema change as breaking, mock-client abuse sequences answered with structured errors, adversarial fixtures, and a regression gate.
- Lesson 39 — Testing MCP Servers Like APIs: Unit Tests
- Lesson 40 — Contract Testing: Schemas and Error Shapes
- Lesson 41 — Integration Testing: Real and Mock Clients
- Lesson 42 — Adversarial Testing and Regression Suites

### s11 — `s11/production` (production) — Section 11: Observability and Production Deployment
Structured audit logging with secret redaction and correlation-ID timeline reconstruction, dual packaging manifests (stdio + HTTP), a three-replica scaling lab that survives a killed replica, and a canary drill with budget-based rollback.
- Lesson 43 — Observability: Logging, Tracing, and Metrics That Matter
- Lesson 44 — Packaging, Versioning, and Deployment Topologies
- Lesson 45 — Scaling: Containers, Pooling, and Secrets
- Lesson 46 — Safe Rollouts, Monitoring, and Incident Response

### s12 — `s12/ecosystem` (ecosystem) — Section 12: The Future
A protocol map that classifies connections as MCP-shaped, A2A-shaped, or neither by direction, and an adopt/build/buy/wait position-note generator with the trigger that would change each answer.
- Lesson 47 — A2A and MCP: Two Protocols, Two Directions
- Lesson 48 — Governance, Trust, and Future-Proofing

### s13 — `s13/capstone` (capstone) — Section 13: Capstone
The design-studio template (architecture, safety register, security checklist, test plan), a filled sample design for the wrong-tax-rate workflow graded against the book's Appendix A production-readiness checklist, and the sequenced roadmap planner.
- Lesson 49 — Capstone Studio: Design Your Production MCP Architecture
- Lesson 50 — Course Close: The Durable Principles and Your Roadmap

## Validation

```bash
python validate.py
```

16 numbered checks: repo structure; each of the 13 demos run end to end plus API-level assertions on its documented key functions; a repo-wide hardcoded-secrets scan; and a documentation check (this README against the demo tree). The run prints `ALL CHECKS PASSED (16/16 green)` and writes `RESULTS.md` with the full record.

## Layout

```text
code-repo/
├── README.md            (this file)
├── validate.py          (16-check validation harness; writes RESULTS.md)
├── RESULTS.md           (written by the validation run)
├── requirements.txt     (intentionally empty — standard library only)
├── LICENSE
└── s01/ … s13/          (one directory per section, each with one demo package:
                          demo.py + README.md — see each demo's README for its
                          key functions and per-lesson detail)
```

## Hands-On Labs (Section 14 — Build It Yourself)

The course's Section 14 turns each section demo into a hands-on lab:
the code is shown step by step, the demo is run for real, and its
actual output is read line by line. Each lab lives in `labs/lab-NN/`
with two git checkpoints:

- **Start** — tag `lab-NN-start`: `demo.py` is a scaffold (docstring,
  imports and data in place; function bodies are TODOs to implement
  along with the video).
- **Finish** — tag `lab-NN`: `demo.py` is the complete working demo,
  identical to the section demo it builds.

| Lab | Title | Builds demo | Tags |
|---|---|---|---|
| 1 | Hello MCP — Run Your First Server | `s01/hello_mcp` | `lab-01-start` / `lab-01` |
| 2 | Fundamentals — Speak the Protocol | `s02/fundamentals` | `lab-02-start` / `lab-02` |
| 3 | Transports — Move JSON-RPC Live | `s03/transports` | `lab-03-start` / `lab-03` |
| 4 | First Server — Build and Call a Tool | `s04/first_server` | `lab-04-start` / `lab-04` |
| 5 | Primitives — Tools, Resources, Prompts | `s05/primitives` | `lab-05-start` / `lab-05` |
| 6 | Enterprise — Survive Error Classes | `s06/enterprise` | `lab-06-start` / `lab-06` |
| 7 | Security — Stop the Injection Drill | `s07/security` | `lab-07-start` / `lab-07` |
| 8 | Orchestration — Survive Partial Failure | `s08/orchestration` | `lab-08-start` / `lab-08` |
| 9 | Comparison — Benchmark Three Approaches | `s09/comparison` | `lab-09-start` / `lab-09` |
| 10 | Testing — Pass the Regression Gate | `s10/testing` | `lab-10-start` / `lab-10` |
| 11 | Production — Run the Canary Rollback | `s11/production` | `lab-11-start` / `lab-11` |
| 12 | Ecosystem — Survey the MCP Landscape | `s12/ecosystem` | `lab-12-start` / `lab-12` |
| 13 | Capstone — Pass the Grading Gate | `s13/capstone` | `lab-13-start` / `lab-13` |

Labs 1, 2, 3, 5 and 12 also carry a `probe_labNN.py` at their finish
tag: the lab's scripted failure drill, run beside the demo it probes.

Worked example — Lab 1, from a fresh clone:

```bash
git checkout lab-01-start   # try implementing the server yourself
git checkout lab-01         # the finished state
cd labs/lab-01 && python3 demo.py
```

Every lab passes the stranger test: from a fresh clone, check out the
lab's finish tag and run its demo — the output matches the lab video's
run exactly (each lab's README lists its expected first and last
output lines).
