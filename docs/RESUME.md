# Resume this checkpoint

P5 is complete and locally verified with 180 passing tests. The owner authorized P5 on 2026-11-16 by saying “Continue” after the P4 gate. **P6 requires a separate owner approval.** P1-5 remains open because GitHub's account restriction prevents hosted jobs starting.

Read AGENTS.md, docs/STATUS.md, docs/decisions.md, docs/SPEC.md and docs/COMMENTARY.md before changing the project. INPUT-CONTRACT.md and RULES.md document the deterministic core.

## Current verified state

- The normal run pipeline loads and hashes inputs, calculates 80 product-week records, evaluates R1-R9 and attaches commentary for the ten latest-week products.
- report.json has stage commentary, unchanged products and analysis sections, plus commentary metadata and notes. SAMPLE_kpis.csv still matches the P3 golden snapshot exactly.
- --no-ai reads no credentials and makes no network request. It produces byte-reproducible template notes with label and reason.
- The default AI path uses one structured Gemini request. Every metric claim is checked against its product, week, metric, unit, signed direction and allowed display rounding. Python owns the displayed metric labels and review wording. Unknown causes, targets and dates stay unknown.
- A real CLI request produced ten accepted AI-drafted, guard-checked notes, zero templates and zero guard rejections. That local end-to-end run took 6.066 seconds. Two earlier manual requests failed with schema-complexity errors before the serving schema was simplified. See evidence/p5-gemini.json. These are manual checks, not scheduled reliability or measured business savings.
- The official google-genai 3.3.0 runtime dependency is pinned. SDK automatic retries and continuation are disabled. One quota retry honors provider delay, then falls back. Per-product schema/guard failures preserve other accepted notes.
- 180 tests pass, with 100% KPI, rules and number-guard coverage. Final gate results are in evidence/p5-local.txt. A separate Windows checkout and wheel packaging are checked in evidence/p5-checkout.txt.
- P0, P2, P3, P4 and P5 are complete. P1 is 5/6. Overall completion is 32/56 tasks and 63.7% weighted. The phase report is evidence/P5-REPORT.md.

## Next gate

Ask the owner to approve P6 before implementing the four visual outputs. Preserve phase gates. The owner wants another agent to continue from this repository state without reconstructing the conversation.

## Interfaces to reuse

- load_inputs(folder, column_map) returns validated ProductWeek rows, manifest and source fingerprints.
- calculate_report(rows, vat_rate) returns ProductMetrics with Decimal values, dates and undefined reasons. All money calculation stays here in Python.
- evaluate_rules(records, thresholds, report_week, priority_limit=6) returns typed RuleReport with every flag, skipped-rule reasons and deduplicated priorities. The sample has ten flags across seven products, and six priority products.
- generate_commentary(records, analysis, no_ai=..., model=..., limit=...) returns typed Commentary. It contains notes, request_status, attempts, model, prompt_sha256, ai_used and guard_rejections. No renderer should call Gemini again.
- Note fields include asin, week, data_label, label, reason, what_happened, likely_cause, planned_change_to_review, target_and_review_date, confidence, claims, guard_issues and rejected_numeric_tokens. Every renderer must show the source label and fallback reason.
- pipeline.run_numerical_draft(folder, destination, config_dir, config, no_ai=True) remains the callable name for compatibility. The CLI explicitly passes args.no_ai, so its default path can use AI. This function currently publishes the two-file draft and is the place to integrate P6 renderers.
- artifacts.publish_bundle stages the complete byte bundle and refuses to replace different existing content. Preserve this behavior when adding output files.
- JSON serializes financial Decimal values as exact strings, undefined metrics as null with reasons, and dates as ISO strings. The typed objects remain available before serialization.

## Reproduce

```shell
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest --cov=src/adsreport --cov-report=term-missing --hypothesis-show-statistics
uv run adsreport generate-sample --seed 42
uv run adsreport run --input data/sample --out out/review-p5 --no-ai
```

Use a fresh output directory when content differs. Local uv is .tools/bootstrap/bin/uv.exe. Set UV_CACHE_DIR to .tools/p1-cache, UV_PYTHON_INSTALL_DIR to .tools/python and optionally UV_LINK_MODE=copy. A fresh clone can use installed uv and the committed Python version.

The ignored local .env contains the owner's key and GEMINI_FREE_TIER_CONFIRMED=true from the existing owner attestation. On another computer, copy .env.example privately and configure credentials without sending them to chat or Git. Default runs fall back when credentials or confirmation are absent. Billing status has not been independently verified through account administration. Rotate the chat-shared key before unattended operation. All live verification sent simulated performance only.

## P6 work after approval

1. Record approval in decisions.md. Read the appropriate frontend, spreadsheet, PDF and presentation skills for implementation and visual verification. Recheck official library versions and native dependencies before adding only what is needed.
2. Establish native PDF support first. P0 verified WeasyPrint 70.0 imports fail on this Windows environment because Pango/native libraries are missing. Ubuntu CI is still blocked by the GitHub account, so do not rely on it as an available renderer. Obtain a free local runtime and demonstrate PDF generation before counting P6-4 complete.
3. Build a shared navy/teal palette, text severity labels and consistent English EUR formatting. Generate matplotlib SVG/PNG charts with readable units and axes, then reuse those charts.
4. Add XLSX with six specified sheets and native Excel charts, self-contained autoescaped HTML, local-only WeasyPrint PDF with A4 print CSS, and the five-slide PPTX. All four outputs must come from one report object.
5. Compute aggregate KPIs and week-over-week changes in Python using numerator/denominator totals, not average product ratios. Include TACoS denominator, undefined reasons, source provenance, assumptions and runtime identity. P7 will add real approval and run logging, so keep report status DRAFT.
6. Integrate every renderer into the normal run path and the shared staged publication bundle. Both offline and AI modes must produce all four artifacts without recalculating or changing product KPIs, flags or accepted notes.
7. Show DRAFT and SAMPLE DATA throughout. Catalog names and manufacturer set IDs remain distinct from sample ASINs/SKUs. Do not use brand logos or claim LEGO affiliation. Show AI/template labels and fallback reasons in each relevant output.
8. Add meaningful cross-output consistency and local resource/failure tests. Open every output, capture screenshots and inspect every PDF page for clipping. Verify native Excel charts and PPTX at normal viewing size.
9. Update STATUS, SPEC, evidence, assumptions and this handoff. Self-review the diff for unnecessary code and failure paths, run all phase gates, scan the publication set for secrets, commit and push, verify remote SHA and stop for P7 approval.

## External blockers and remaining acceptance

Hosted CI P1-5 remains blocked by the provider account billing lock. The latest pre-P5 verified attempt is linked in evidence/P4-REPORT.md. No green hosted run is claimed, and no spending settings were changed. Repeated push emails may reflect the same account restriction.

Visual outputs and native PDF rendering are P6. Frozen human approval, email/Discord receipts and genuine unattended schedule evidence remain P7. Measured manual versus assisted review time remains P8. P9 requires a separate independent reviewer. Do not count simulated performance as actual business impact.

The repository is public. Preserve the configured owner Git author identity and omit assistant co-author trailers. Keep .env, .tools, out directories and original private handovers outside Git. Commit/push everything needed to resume, verify local/remote SHA and stop at the phase gate.

## Copyable continuation request

Read AGENTS.md and docs/RESUME.md, then verify docs/STATUS.md and Git state. P5 is complete, and P6 awaits my approval. Confirm that approval before implementation. Work through the approved phase, self-test and visually inspect all outputs, update evidence and the full progress table, commit and push the complete handoff, then stop at the next gate.
