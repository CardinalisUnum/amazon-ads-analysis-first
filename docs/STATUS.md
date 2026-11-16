# Completion tracker

Updated 2026-11-16. P3 complete and verified. P4 awaits owner approval. Hosted CI P1-5 remains open.

| Phase | Weight | Complete | Progress | Bar |
|---|---:|---:|---:|---|
| P0 Kickoff | 5% | 5/5 | 100.0% | `████████████████████` |
| P1 Scaffold | 8% | 5/6 | 83.3% | `█████████████████░░░` |
| P2 Sample data | 10% | 5/5 | 100.0% | `████████████████████` |
| P3 Loader and KPIs | 15% | 6/6 | 100.0% | `████████████████████` |
| P4 Rules | 12% | 0/5 | 0.0% | `░░░░░░░░░░░░░░░░░░░░` |
| P5 Commentary and guard | 15% | 0/6 | 0.0% | `░░░░░░░░░░░░░░░░░░░░` |
| P6 Outputs | 15% | 0/6 | 0.0% | `░░░░░░░░░░░░░░░░░░░░` |
| P7 Operations and approval | 10% | 0/6 | 0.0% | `░░░░░░░░░░░░░░░░░░░░` |
| P8 Docs and demo | 5% | 0/5 | 0.0% | `░░░░░░░░░░░░░░░░░░░░` |
| P9 Independent audit | 5% | 0/6 | 0.0% | `░░░░░░░░░░░░░░░░░░░░` |
| **Overall** | **100%** | **21/56** | **36.7% weighted** | `███████░░░░░░░░░░░░░` |

Bars round to the nearest 5%. Numeric percentages are exact to one decimal place.

| ID | Task | Acceptance | Status and evidence |
|---|---|---|---|
| P0-1 | Read this file; list any contradictions or unclear points | List sent to the owner | Complete. Assessment sent to owner and recorded in decisions.md. |
| P0-2 | Run the Owner Interview §11.1 | All 10 answers recorded in `docs/decisions.md` | Complete. Interview decisions recorded in decisions.md. |
| P0-3 | Triple-check the stack (§4): versions, Python 3.13 support, pandas 3 + pandera compatibility, WeasyPrint system deps | Version table with source URLs and dates in `docs/decisions.md` | Complete. Exact versions installed on Python 3.13, pandas/Pandera probe executed, native PDF requirement diagnosed. See evidence/p0-stack.json and decisions.md. PDF rendering itself remains P6. |
| P0-4 | Verify the Gemini model ID with free quota + the current `google-genai` call shape + structured output; run a 5-line smoke script | Script output pasted; model ID in config | Complete. google-genai structured response parsed using owner-supplied Free Tier key. See evidence/p0-gemini.json and config/model.yaml. Billing status is owner-attested. |
| P0-5 | Verify Amazon Advertised Product report column names (old + new) | `column_map.yaml` draft with sources | Complete. Sourced column-map draft in config/column_map.yaml. Real localized export compatibility remains untested. |
| P1-1 | `uv init`, `pyproject.toml`, `uv.lock`, src layout per §5 | `uv sync --locked` succeeds | Complete. uv.lock, src package and successful uv sync --locked in evidence/p1-local.txt. |
| P1-2 | ruff + mypy strict + pytest + coverage config | All gates run (0 tests is OK) | Complete. Lint, format, strict mypy and 21 configuration/CLI tests pass. See evidence/p1-local.txt. |
| P1-3 | `.gitignore`, `.env.example`, LICENSE (owner chooses), README skeleton | Files present; no secrets | Complete. MIT license, ignore rules, example environment and development quickstart committed. |
| P1-4 | CLI skeleton (`generate-sample`, `run`, `approve`, `deliver`) | `--help` output pasted | Complete. Installed adsreport --help exposes all four commands. See evidence/p1-local.txt. |
| P1-5 | `ci.yml`: lint, types, tests on push/PR; actions SHA-pinned; least-privilege permissions | Green CI run URL | Blocked. Hosted job cannot start due provider account restriction. Local workflow validation passed. See evidence/P1-REPORT.md. |
| P1-6 | Config loading (`settings.yaml`, `thresholds.yaml`) via pydantic | Invalid config fails with a clear error (test) | Complete. Settings and threshold models reject malformed, missing and invalid config through CLI and direct loader tests. |
| P2-1 | Generator for ads, total sales, costs, inventory (10 products × 8 weeks, seeded) | Same seed → identical files (test) | Complete. CLI generates 10 products across 8 weeks. Seeds 0, 42 and 2026 pass byte-reproducibility tests. See evidence/p2-local.txt. |
| P2-2 | Engineer the 10 product stories from §5.3 | Each story visible in the data | Complete. Independent fixture arithmetic verifies all ten stories and exact final-week R1-R9 flags. See P2-SAMPLE-REVIEW.md and tests/test_sample.py. |
| P2-3 | `expected_flags.yaml` | Reviewed by owner | Complete. Owner approved expected_flags.yaml and its review table on 2026-11-16. |
| P2-4 | SAMPLE marker in file names, headers or metadata | Test asserts the marker | Complete. All seven sample files have SAMPLE naming or metadata markers, asserted by tests. |
| P2-5 | Data realism check: plausible CPC, CTR, CVR, prices, fees for a toy-like category on amazon.de; every assumption logged in ASSUMPTIONS.md | Owner approves the ranges | Complete. Owner approved sample assumptions and ranges on 2026-11-16. See decisions.md. |
| P3-1 | Loader: column mapping (old + new names) + schema validation | Bad or missing columns fail clearly (tests) | Complete. Typed loader, aliases, hashes, grain and join validation pass tests/test_loader.py. See INPUT-CONTRACT.md. |
| P3-2 | KPI functions per §2.4 (pure, no I/O) | Unit tests pass | Complete. Every KPI verified against independent arithmetic; pure Decimal engine has 100% coverage. See evidence/p3-local.txt. |
| P3-3 | The 8.44 / 25.13 → 33.6% worked example | Test pass | Complete. The published 8.44 / 25.13 example returns 33.6% to one decimal in test_published_worked_example. |
| P3-4 | Zero and edge cases (0 spend, 0 sales, 0 units, missing weeks) | Tests pass; no `inf` or `NaN` leaks into outputs | Complete. Zero denominators, missing weeks, organic residual limits and stock coverage are tested with explicit undefined reasons. |
| P3-5 | Property tests (hypothesis) | Pass with ≥ 200 examples | Complete. Both Hypothesis identities pass 200 examples each; statistics captured in evidence/p3-local.txt. |
| P3-6 | Golden-file snapshot of the KPI table (`--no-ai`) | Snapshot committed and test passes | Complete. --no-ai CLI matches the committed 80-row golden CSV. CSV and JSON drafts match across checkouts. See evidence/p3-checkout.txt. |
| P4-1 | Implement R1–R9 (§6), thresholds from config | Unit test per rule | Pending |
| P4-2 | Flag object with evidence (values, threshold, reason) | Serialises to JSON (test) | Pending |
| P4-3 | Severity sort and top-N priority list | Test | Pending |
| P4-4 | `expected_flags.yaml` exact-match test | Pass | Pending |
| P4-5 | Wording check: no rule text recommends bid, price, delisting or refund decisions | Test scans flag text | Pending |
| P5-1 | Commentary schema (pydantic) + prompt per §7.1 | Prompt file committed and reviewed | Pending |
| P5-2 | One batched Gemini call with structured output (verified API shape) | Real call succeeds; output parsed | Pending |
| P5-3 | Number guard per §7.2 | Rejection and acceptance tests pass | Pending |
| P5-4 | Template fallback (deterministic) | `--no-ai` path fully works | Pending |
| P5-5 | Error handling: quota/429 → one retry → fallback; never fails the run | Test with a mocked 429 | Pending |
| P5-6 | Label each comment "AI-drafted, guard-checked" or "template", and why | Visible in outputs (test) | Pending |
| P6-1 | Chart module (matplotlib → SVG + PNG), shared palette | Charts render; labels and units present | Pending |
| P6-2 | XLSX per §8 with native charts + conditional formatting | Opens cleanly in Excel; screenshots | Pending |
| P6-3 | HTML per §8 (Jinja2, autoescape) | Screenshot; no external network requests | Pending |
| P6-4 | PDF from the HTML (WeasyPrint, local-only fetcher) | A4, no cut-off content; screenshots of every page | Pending |
| P6-5 | PPTX 5 slides per §8 | Opens cleanly; screenshots | Pending |
| P6-6 | Cross-output consistency test + DRAFT/APPROVED + SAMPLE stamps | Test passes | Pending |
| P7-1 | `weekly-report.yml`: schedule (off-minute cron) + `workflow_dispatch`, `build` job uploads artifacts | Manual run green | Pending |
| P7-2 | Run log JSONL committed per run + success-rate calculation | Log entries visible; rate in README | Pending |
| P7-3 | `client-delivery` environment with required reviewer; `deliver` job waits for approval | Screenshot of the waiting and approved states | Pending |
| P7-4 | Failure alerts through both email and Discord | Alert received (screenshot) | Pending |
| P7-5 | Injected failure test, labelled `test_failure`, excluded from the success rate | Log + alert evidence | Pending |
| P7-6 | First **unattended** scheduled run succeeds (temporarily schedule a near-future run if needed, then restore the weekly cron) | Run URL showing the `schedule` trigger | Pending |
| P8-1 | README: what it does, a 60-second quickstart, architecture diagram, screenshots, run history (real dates and counts), success rate, measured time saved | Owner approves | Pending |
| P8-2 | PROCESS.md: the weekly Ads-review process as an analyst does it, including exceptions (this is the "expert know-how written down") | Owner approves | Pending |
| P8-3 | ASSUMPTIONS.md (every threshold and data assumption, "to confirm with your Ads manager") + LIMITS.md (free-tier, schedule delay, 60-day rule, sample data, no live API) | Complete | Pending |
| P8-4 | Time-saved measurement: owner's stopwatch time on the manual analysis vs. review time with the report | Real numbers in the README | Pending |
| P8-5 | Loom script (3 minutes): problem → run → flags → guard → approval → outputs → limits | Script in `docs/loom-script.md` | Pending |
| P9-1 | Fresh clone → run every quality gate (§9) | Outputs pasted | Pending |
| P9-2 | Hand-recalculate all KPIs for 3 random products | Match within rounding; worksheet attached | Pending |
| P9-3 | Promise check: every clause in §1.1 is demonstrably true | Clause-by-clause table | Pending |
| P9-4 | Audit sample labels, catalog provenance, secrets, controls and docs | Findings table (severity: blocker / major / minor) | Pending |
| P9-5 | Builder fixes all blockers and majors; auditor re-verifies | Zero open blockers or majors | Pending |
| P9-6 | Tag `v1.0.0`, release notes, final completion table at 100% | Release URL | Pending |
