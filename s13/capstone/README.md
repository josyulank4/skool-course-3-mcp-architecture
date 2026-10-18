# capstone (s13)

**Section 13 — Capstone: Your Production MCP Architecture · Lessons 49–50**

The design-studio template, an Appendix A grading gate, and the roadmap
planner that sequences the build.

## Run

```bash
python demo.py
```

## What it does

1. **`STUDIO_TEMPLATE`**: the design-document skeleton — `architecture`,
   `safety_register`, `security_checklist`, `test_plan`, plus
   `reliability`, `operations`, and `governance` sections.
2. **`fill_template(brief)`** completes it for the sample brief: the
   wrong-tax-rate invoice workflow spanning ticketing, the account
   store, and billing configuration (3 servers).
3. **`check_design(design)`** grades against Appendix A's six
   categories; the filled sample passes all six, a stripped design
   fails naming exactly what is missing.
4. **`roadmap_plan(design)`** sequences the build: security gate first
   (before the first write tool), then facades highest-reuse /
   lowest-risk first, consumer migration last.

## Lesson mapping

| Lesson | Used in demo |
|--------|--------------|
| 49 — Capstone Studio | `STUDIO_TEMPLATE` + `fill_template(SAMPLE_BRIEF)`; `check_design` applies the Appendix A rubric |
| 50 — Course Close: Durable Principles and Your Roadmap | `roadmap_plan`: gate before writes, facades before migrations, reuse/risk order |

## Key functions

- `STUDIO_TEMPLATE` → dict with keys `architecture`, `safety_register`,
  `security_checklist`, `test_plan`, `reliability`, `operations`,
  `governance` (all empty in the skeleton).
- `fill_template(brief)` → a completed design dict. For `SAMPLE_BRIEF`
  its `architecture["servers"]` lists, in brief order, the ticketing
  server (reuse 9, risk low, writes), account server (reuse 6, risk
  low, read-only), and billing server (reuse 4, risk high, writes);
  every other section is fully filled.
- `check_design(design)` → `(passed, missing)`, `missing` in Appendix A
  order: `design and scope`, `security`, `reliability`, `testing`,
  `operations`, `governance`. Category mapping: design and scope =
  architecture with servers + safety register; testing = test plan;
  the rest map to their same-named sections, each required non-empty
  with all values truthy. `check_design(fill_template(SAMPLE_BRIEF))
  == (True, [])`; `check_design({}) == (False, all six categories)`;
  deleting `test_plan` and `governance` from the filled design gives
  `(False, ["testing", "governance"])`.
- `roadmap_plan(design)` → ordered `"Step N: ..."` strings. For the
  sample design exactly: Step 1 the security gate, Step 2 the ticketing
  facade, Step 3 the account facade, Step 4 the billing facade,
  Step 5 consumer migration. In general: servers sort by risk
  (low → high) then reuse (high → low); the security-gate step sits
  immediately before the first write-tool server's step; migration is
  always last.
