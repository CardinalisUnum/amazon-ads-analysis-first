# P2 gate report

SAMPLE DATA. The generator is implemented and locally verified. Owner review of expected flags and commercial assumptions is requested before P3. Hosted CI task P1-5 remains open with the known provider account restriction.

## Deliverables

- src/adsreport/sample.py implements the seeded generator using the standard library and the existing PyYAML dependency.
- `uv run adsreport generate-sample --seed 42` reaches the generator through the installed CLI.
- data/sample contains 1,120 daily campaign-product rows, 80 weekly retail rows, 80 inventory snapshots, ten cost records and ten catalog references.
- The seven-file bundle includes five labelled CSVs, expected_flags.yaml and manifest.json. The manifest identifies the reporting periods, seed, tax bases and SHA-256 hashes.
- P2-SAMPLE-REVIEW.md shows the ten product stories with independently recalculated final-week economics and expected rules.
- ASSUMPTIONS.md records the modeled costs, prices, dates, attribution simplifications and threshold conventions.

## Verification evidence

Full output is in p2-local.txt.

```text
uv sync --locked                         exit 0
uv run ruff check .                      All checks passed!
uv run ruff format --check .              21 files already formatted
uv run mypy --strict src/                 no issues in 5 source files
uv run pytest --cov=src/adsreport          32 passed, 98% total coverage
uv run adsreport generate-sample --seed 42 exit 0
uv run adsreport --check-config           Configuration valid.
```

The tests cover seeds 0, 42 and 2026, byte-identical repetition, manifest hashes, committed seed-42 snapshot equivalence, every R1-R9 latest-week scenario, prelaunch zeros, row count consistency, distinct catalog and sample identifiers, changed seed behavior and preservation of an existing output directory. An injected disk-write failure leaves no published partial bundle and cleans its staging directory. Invalid sample VAT settings fail before output creation.

Observed seed-42 active-week ranges are 81-133 retail units, EUR 0.3024-3.3271 CPC, 2.0-2.5% CTR and 6.8493-12.0172% ad purchase rate. These are synthetic fixture observations. Owner review is required before treating the ranges as suitable demo assumptions.

## Self-review

The implementation was reviewed with the backend-code-simplifier guidance. Existing CLI/config code is reused. Decimal money formatting, exact integer allocation and CSV serialization are the only shared generator helpers. No framework, application dependency or speculative feature was added. Sample publication uses staging and preserves existing different content. The changed CLI message now points to the phase tracker for pending operations.

The production KPI engine and rules engine remain P3/P4 tasks. Tests independently recalculate fixture facts to detect unintended flags in this phase. The expected-flags scope is explicitly the final sample week. All catalog identities have official source URLs, while commercial records remain synthetic.

## Owner review requested

Approve the expected flags in P2-SAMPLE-REVIEW.md and the sample ranges in ASSUMPTIONS.md, then approve starting P3. Until that approval, P2-3 and P2-5 stay in review. P2-1, P2-2 and P2-4 are complete. Overall completion is 13 of 56 tasks and 17.7% weighted.
