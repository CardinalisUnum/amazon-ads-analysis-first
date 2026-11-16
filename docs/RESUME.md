# Resume this checkpoint

P3 is complete. The owner approved P2 flags and assumptions and authorized P3 on 2026-11-16. **P4 requires owner approval before implementation.** Hosted CI P1-5 remains open.

## Copyable continuation request

Read AGENTS.md, docs/STATUS.md, docs/decisions.md, docs/INPUT-CONTRACT.md and this file. Verify the Git branch and remote state, run the quality gates below, then continue only at the phase the owner has approved. At every phase gate update the full tracker and evidence, commit and push, then pause for approval. Preserve the configured owner Git author identity and do not add assistant co-author trailers.

## Current verified state

- P0 and P2 are complete. P1 is 5/6 with hosted CI externally blocked. All six P3 tasks are complete.
- Numerical CLI run --no-ai emits DRAFT SAMPLE DATA CSV/JSON for 80 product-weeks.
- 83 tests pass, including 200 examples for each of two properties. Total coverage is 98%; KPI engine coverage is 100%.
- A separate Windows checkout passes all 83 tests. Numerical CSV and JSON are byte-identical across checkouts.
- docs/evidence/P3-REPORT.md, p3-local.txt and p3-checkout.txt contain the evidence.
- Production rules, AI commentary/guard, four visual outputs and delivery remain P4-P7 work.
- The project remains public. GitHub account restriction still blocks hosted CI; never mark P1-5 complete without a real green run.

## Entry points and data contracts

- src/adsreport/io/loader.py load_inputs(folder, column_map) returns LoadedInput with manifest, typed ProductWeek rows, source hashes and normalized mapping fingerprint.
- src/adsreport/io/models.py defines source records. Inputs use exact Decimal amounts. InputError identifies unsupported or ambiguous input.
- src/adsreport/kpi/engine.py calculate_report(rows, vat_rate) returns ProductMetrics in ASIN/week order. Each has asin, week, lifecycle_phase, launch_start_date, values and undefined_reasons.
- src/adsreport/pipeline.py run_numerical_draft loads, calculates and publishes the current two-file numerical bundle. Extend this normal path for P4.
- src/adsreport/artifacts.py publish_bundle preserves existing different content and publishes a fully staged new directory. Sample generation reuses it.
- data/sample/expected_flags.yaml applies only to report week 2026-10-26. All sample identities, costs and scenarios were approved at the P2 gate.
- tests/golden/SAMPLE_kpis.csv is the deterministic 80-row snapshot. Keep it stable unless a documented calculation change requires updating it.

Metric keys needed by P4 include acos_pct, break_even_acos_pct, contribution_after_ads_eur, organic_share_proxy_pct, stock_coverage_days, ad_spend_eur_wow_pct, ad_sales_eur_wow_pct, net_revenue_eur_wow_pct, impressions_wow_pct, clicks_wow_pct, ad_cvr_pct_wow_pct and acos_pct_wow_pp. Optional/undefined values are None. JSON encodes Decimal values as strings; calculate rules on typed values before serialization.

## Next phase after approval

1. Record the owner's P4 approval.
2. Implement R1-R9 as pure rule evaluation using ProductMetrics and config.thresholds.
3. Each flag carries rule ID, product, week, severity, values, threshold and a plain-English reason. Human reviewers make commercial decisions.
4. R8 requires three declines over four consecutive comparable weeks. Missing/invalid metrics skip dependent rules with a clear reason. Test launch and threshold equality boundaries explicitly.
5. Sort by severity deterministically, retain every flag and derive a deduplicated product priority list.
6. Integrate flags into the existing run --no-ai report path. Exact-match the final sample week against expected_flags.yaml. Keep numerical CSV values unchanged.
7. Unit-test each rule, serialization, ordering and review-safe wording. Run gates, update evidence/tracker/handoff, commit/push and stop for P5 approval.

## Reproduce verification

From the repository root with uv installed:

uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest --cov=src/adsreport --cov-report=term-missing --hypothesis-show-statistics
uv run adsreport generate-sample --seed 42
uv run adsreport run --input data/sample --out out/review-p3 --no-ai

Choose a fresh output path if existing content differs. Identical content is verified without rewriting. Local bootstrap uv is .tools/bootstrap/bin/uv.exe. Local Windows environment uses UV_CACHE_DIR resolved to .tools/p1-cache and UV_PYTHON_INSTALL_DIR to .tools/python. A fresh clone can use an installed uv and the committed Python version.

## Open conditions and limits

The standard-library CSV/Pydantic loader replaces the initially proposed pandas implementation, preserving Decimal precision without an unused production dependency. English numeric exports and normalized product-week retail inputs are supported. See INPUT-CONTRACT.md for tax, rounding, grain, completeness and missing-value conventions.

Windows native PDF libraries remain unavailable. Establish supported native dependencies before P6 rendering claims. No scheduled runs, delivery approvals, alert receipts or measured review-time savings have been established yet.

Keep .env, .tools, generated out directories and original private handovers out of Git. The Gemini key shared in chat must be rotated before unattended setup, saving its replacement privately. Credentials must never appear in logs.

## Persistence

Origin is https://github.com/CardinalisUnum/amazon-ads-analysis-first.git, branch main. Git operations using the credential helper require escalation in this Windows sandbox. Verify local/remote SHA and clean status after every push. All necessary code, samples, snapshots, test evidence and this handoff belong in the checkpoint. Generated drafts are reproducible with the command above.
