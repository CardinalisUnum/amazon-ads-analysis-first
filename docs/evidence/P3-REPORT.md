# P3 gate report

P3 is implemented and locally verified. The owner approved P2 expected flags and assumptions on 2026-11-16. P4 approval is now requested. Hosted CI P1-5 remains open because the provider account is locked.

## Acceptance evidence

| Task | Result and evidence |
|---|---|
| P3-1 loader | Typed validation, classic/current/canonical aliases, input hashes, grain checks and aggregation before joins. tests/test_loader.py covers invalid input and source reconciliation. |
| P3-2 formulas | Pure Decimal calculations for every defined KPI, counts, price, fees, margins and history. Independently specified unit examples verify all formulas. |
| P3-3 33.6% example | EUR 29.90 gross yields EUR 25.13 rounded net, EUR 8.44 contribution before ads and 33.6% break-even ACoS. |
| P3-4 edge cases | Zero spend/sales/units/demand, missing adjacent weeks, unavailable or invalid organic residuals and zero stock with positive demand. Undefined values carry reasons. |
| P3-5 properties | ACoS × ROAS = 100 and contribution after ads = contribution before ads minus spend each pass 200 Hypothesis examples. |
| P3-6 snapshot | The --no-ai normal CLI produces the committed 80-row tests/golden/SAMPLE_kpis.csv. CSV and JSON drafts match byte-for-byte across separate Windows checkouts. |

## Captured checks

```text
uv sync --locked                         exit 0, 24 packages checked
uv run ruff check .                      All checks passed!
uv run ruff format --check .              33 files already formatted
uv run mypy --strict src/                 no issues in 12 source files
uv run pytest --cov=src/adsreport          83 passed, 98% total coverage
KPI engine coverage                      100%, including branches
Hypothesis                               200 passing examples per property
```

Complete output is in p3-local.txt. A separate checkout with core.autocrlf=true passed all 83 tests and reproduced both draft files exactly. See p3-checkout.txt.

## Implementation choices and self-review

The loader uses standard-library CSV and typed Pydantic records with Decimal amounts. This replaces the planned pandas DataFrame loader with a smaller implementation that avoids float conversion and an otherwise unused application dependency. Hypothesis is a development-only dependency.

The sample's existing staged directory publisher was extracted for two actual callers, with its idempotency and write-failure checks retained. Source file hashes are calculated from the captured bytes used for parsing. Configuration fingerprints cover the validated settings and normalized column mapping, preserving portability across line endings.

The failure-path review found no swallowed input or write failure in the changed paths. Bad inputs return a visible nonzero CLI result. Missing data is not filled with invented financial values. Header-only complete ads exports represent zero activity, while missing required files or records fail. A malformed or incomplete bundle produces no draft. The existing publication helper preserves different output content and cleans staged write failures.

An early test contained an incorrect hardcoded retail sum. It was replaced with independent source-CSV reconciliation, which directly verifies that retail revenue is not multiplied by campaign joins. The golden CSV records the documented rounding convention and is checked independently of JSON serialization.

## Scope and limits

This checkpoint emits DRAFT SAMPLE DATA numerical CSV/JSON only. Rules are P4, commentary/guard are P5, four visual report outputs are P6, and approval/delivery/run history are P7. No hosted CI or scheduled run is claimed.

The input contract requires metadata-declared tax bases and reporting periods. Raw date-free multiweek Business Reports need the documented weekly normalization adapter. Source numeric formatting is English. Costs are one current record per ASIN, with a uniform per-week price basis. Monetary and attribution conventions are documented in INPUT-CONTRACT.md.

## Continuation

Read RESUME.md for exact commands and P4 integration points. All six P3 acceptance checks are complete. Overall completion is 21 of 56 tasks and 36.7% weighted, with P1-5 still open. Pause for owner approval before P4.
