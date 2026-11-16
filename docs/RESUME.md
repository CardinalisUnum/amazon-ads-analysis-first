# Resume this checkpoint

P4 is complete and locally verified with 122 passing tests. The owner authorized P4 on 2026-11-16 and requested this pushed continuation handoff. **P5 requires a separate owner approval.** P1-5 remains open due the GitHub account restriction.

Read AGENTS.md, docs/STATUS.md, docs/decisions.md, docs/INPUT-CONTRACT.md and docs/RULES.md first.

## Current verified state

- src/adsreport/rules/engine.py evaluates R1-R9 for a requested report week. It returns typed RuleReport with every flag, skipped-rule reasons and priorities.
- Flags contain exact Decimal/date evidence and thresholds. Pydantic JSON round trips are tested.
- Top products are deduplicated, sorted by highest severity and retain all rule IDs. settings.priority_products defaults to six.
- The normal run --no-ai pipeline attaches analysis to report.json and sets stage to rules. The 80-row numerical CSV remains unchanged.
- 122 tests pass. Total coverage is 98%, with 100% KPI and rules engine coverage. See docs/evidence/p4-local.txt.
- docs/evidence/SAMPLE-p4-analysis.json captures the actual ten sample flags across seven products and six priorities.
- A separate Windows checkout passed all 122 tests. Both draft files were byte-identical, and the P3 numerical CSV snapshot stayed unchanged. See evidence/p4-checkout.txt.
- P0, P2, P3 and P4 are complete. P1 is 5/6. Overall progress is 26/56 tasks and 48.7% weighted.
- The phase report is docs/evidence/P4-REPORT.md. No application dependency was added.

## Next gate

Ask the owner to approve P5 before implementing commentary. Preserve phase gates. The owner wants to be able to continue through another agent with this same repository state.

## Existing interfaces to reuse

- load_inputs(folder, column_map) returns validated ProductWeek rows, manifest and source fingerprints.
- calculate_report(rows, vat_rate) returns ProductMetrics with typed Decimal values, dates and undefined reasons.
- evaluate_rules(records, thresholds, report_week, priority_limit=6) returns RuleReport with flags, skipped and priorities. It does not mutate metrics.
- Flag fields are rule_id, asin, week, severity, evidence, thresholds and reason. Evidence uses Decimal and date types. JSON represents those as decimal/ISO strings.
- pipeline.run_numerical_draft currently loads, calculates, evaluates rules and publishes the two-file draft. Extend this normal CLI path for P5, preserving run --no-ai.
- artifacts.publish_bundle provides complete staged publication and idempotent identical-output checks.
- report.json has stage rules, all 80 product-week metrics, and analysis for the manifest report_week. The current output CSV is unchanged from P3.

## Reproduce

uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest --cov=src/adsreport --cov-report=term-missing --hypothesis-show-statistics
uv run adsreport run --input data/sample --out out/review-p4 --no-ai

Use a new output directory if its content differs. Bootstrap uv is .tools/bootstrap/bin/uv.exe locally. Resolve UV_CACHE_DIR to .tools/p1-cache and UV_PYTHON_INSTALL_DIR to .tools/python if needed. A fresh clone can use installed uv and the committed Python version.

## P5 work after approval

1. Record approval and recheck current official Gemini pricing, model access and SDK shape.
2. Add only the official google-genai runtime dependency needed for commentary, with a justified pin and updated lock. P0 used google-genai 3.3.0, gemini-3.5-flash-lite and client.interactions.create with response_format and a Pydantic schema. Successful response access used reply.output_text. The app does not yet include this SDK.
3. Define a commentary schema and prompt covering asin, what_happened, likely_cause, planned_change_to_review, target_and_review_date and confidence. Say unknown when cause, targets or review dates are unsupported. Quantitative targets and dates require provided facts.
4. Prepare only the ten latest-week products' computed facts, rule evidence, dates and approved contextual values. The top-six priority display does not limit commentary coverage.
5. Use fact references tied to product, week, metric, unit, sign and direction. Python should own numeric formatting and metric labels. A value existing under another metric cannot validate the claim. Test the explicit ACoS/TACoS swap case, wrong product/week, dates, rounding, percentages and euro amounts.
6. Implement the number guard and deterministic fallback. Labels should identify AI-drafted/guard-checked versus template, with the fallback reason. The --no-ai path must produce templates without reading a key or making a network request.
7. Batch a structured Gemini request, validate the schema and every product claim. One quota retry should honor the provider delay, then fall back. Verify SDK retry defaults so hidden retries do not exceed the intended policy. Redact errors and credentials.
8. Keep accepted product notes if one product fails validation, using a template for the affected product. Whole-call/service/schema failure can fall back for the batch. Preserve the exact KPIs and flags.
9. Unit-test normal and failure paths, run one real synthetic free-tier call, capture labelled evidence, and update SPEC/STATUS/decisions/this handoff. Commit and push, verify remote SHA, then stop for P6 approval.

The P0 account smoke script is scripts/check_gemini.py with separate requirements in docs/evidence/p0-requirements.txt. The local ignored .env holds the owner's key. The key was shared in chat and must be rotated before unattended setup, saving the replacement privately. Use a dedicated unbilled Free Tier project. Never print, commit or send secrets in commentary.

## Other blockers

Hosted CI P1-5 is still open. Existing account billing restriction prevents runner steps. Windows PDF-native dependencies are absent and must be established before P6. Approval, delivery, scheduled run history, alert receipts and measured human review savings remain future acceptance checks.

The repository is public. Preserve the configured owner Git author identity and no assistant co-author trailers. Keep .env, .tools, generated out directories and original private handovers outside Git. Verify local/remote SHA after pushing. Updated code, sample fixtures, evidence and this handoff must be included at every checkpoint.


## Copyable continuation request

Read AGENTS.md and docs/RESUME.md, then verify docs/STATUS.md and Git state. P4 is complete, and P5 is awaiting my approval. Confirm that approval before implementation. Work through the approved phase, self-test and review the diff, update evidence and the full progress table, commit and push everything needed to resume, then stop at the next phase gate.
