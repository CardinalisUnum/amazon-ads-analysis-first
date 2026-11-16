# P4 gate report

P4 is complete. The owner authorized this phase on 2026-11-16. P5 requires a new approval. Hosted CI task P1-5 remains open because the provider account is locked.

## Acceptance evidence

| Task | Evidence |
|---|---|
| P4-1 R1-R9 | Every rule has individual trigger, boundary and missing-evidence tests. Configuration controls its thresholds. |
| P4-2 flag records | Typed Flag contains product, week, severity, exact Decimal/date observations, thresholds and a review reason. JSON round-trip tests preserve values. |
| P4-3 priorities | Severity ordering is deterministic and independent of input order. Products appear once with all their rule IDs. Top-N limits affect priorities while the full flag list remains available. |
| P4-4 sample match | The final sample week matches every approved product-to-rule expectation exactly, including healthy maturity and in-window launch products. |
| P4-5 wording | Every reason describes evidence and asks for review. Tests scan for directive changes to bids, prices or budgets and for delisting/refund language. |

## Captured results

```text
uv sync --locked                         exit 0, 24 packages checked
uv run ruff check .                      All checks passed!
uv run ruff format --check .              38 files already formatted
uv run mypy --strict src/                 no issues in 14 source files
uv run pytest --cov=src/adsreport          122 passed, 98% total coverage
KPI engine / rules engine coverage        100% each, including branches
Existing Hypothesis identities           200 passing examples each
```

Full output is in p4-local.txt. A separate Windows checkout with core.autocrlf=true passed all 122 tests. CSV and JSON draft files were byte-identical across checkouts, and the P3 numerical CSV snapshot stayed unchanged. See p4-checkout.txt.

The actual sample analysis is committed as SAMPLE-p4-analysis.json. It contains ten flags across seven products and six ranked products. Priorities are SAMPLE0004, SAMPLE0005, SAMPLE0007, SAMPLE0010, SAMPLE0006 and SAMPLE0008. SAMPLE0009 retains R6 and R9 in the full flags list outside the six-product priority selection.

## Design and self-review

No dependency was added. Rule evaluation reuses ProductMetrics and Thresholds. One evidence helper handles unavailable values, and one flag builder consistently binds each observation to its product/week. Comparisons remain explicit and individually testable.

For weekly launch review, age is measured at Sunday. Exactly 56 days stays at the boundary, with day 57 past an eight-week window. The new priority_products setting defaults to six, preserving detailed flags separately. Both choices are documented in RULES.md.

Missing or nonfinite evidence produces an explicit skipped-rule record. Zero remains a valid observation. R8 requires every consecutive week and cannot bridge gaps or flatten unknown values. Duplicate product-week records, missing target weeks and nonpositive priority limits return errors before a draft can be published.

The normal run --no-ai pipeline now emits stage rules with analysis in report.json. Typed calculations occur before serialization. Existing CSV consumers keep the P3 numerical format. The shared publication helper retains its existing idempotency and staged-write behavior.

## Remaining conditions

The [hosted attempt](https://github.com/CardinalisUnum/amazon-ads-analysis-first/actions/runs/43797372963) stopped before runner steps with the provider account lock annotation. No green hosted run is claimed.

AI commentary and its guard/fallback are P5. Four visual formats are P6. Human delivery approval, notifications and genuine scheduled history are P7. The sample analysis continues to carry DRAFT and SAMPLE DATA labels.

All five P4 tasks are complete. Overall completion is 26 of 56 tasks and 48.7% weighted. The continuation handoff contains the implemented interfaces and exact P5 requirements. Pause for owner approval before continuing.
