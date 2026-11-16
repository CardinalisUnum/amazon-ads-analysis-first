# Resume this checkpoint

P6 is complete and locally verified. The owner authorized it on 2026-11-16 by saying “Continue” after the P5 gate. **P7 requires a separate owner approval.** Hosted CI P1-5 remains blocked by the GitHub account billing lock. Overall completion is 38/56 tasks and 78.7% weighted.

Read AGENTS.md, docs/STATUS.md, docs/decisions.md, docs/SPEC.md and docs/OUTPUTS.md before changing the project. INPUT-CONTRACT.md, RULES.md and COMMENTARY.md describe the deterministic core.

## Verified state

- Normal run generates XLSX, HTML, PDF, PPTX, three SVG/PNG charts, the unchanged 80-row numerical CSV, report.json and artifacts.json. All normal outputs remain DRAFT and SAMPLE DATA.
- One typed ReportView supplies all four formats. Portfolio totals and comparable-week changes are Python calculations. No renderer or AI recalculates finances.
- The workbook has six sheets and native charts. Native Excel opened it without repair. Native PowerPoint opened/rendered five slides. Full ten-product commentary is retained in speaker notes. The final slide highlights two products.
- Eight A4 PDF pages were rendered and inspected. The HTML was checked at desktop and 390 pixels, with ten cards, three charts, no external resource requests and no page overflow. Twenty-one previews are in docs/evidence/p6.
- docs/examples is the reviewed offline sample bundle with its artifact manifest. These are static DRAFT snapshots, not delivered or approved reports.
- The suite has 195 passing tests. Final gates are in evidence/p6-local.txt. Fresh checkout and packaging results are in evidence/p6-checkout.txt. KPI, rules, number guard and portfolio arithmetic have dedicated tests.
- A local offline pipeline call took 4.454 seconds after Python imports. This excludes process startup and is not human time saved. evidence/p6-offline.json records the scope and artifact hashes.
- P6 normal AI attempts used templates after service errors. One ordered diagnostic confirmed HTTP 503. A separate real diagnostic returned a structured response, captured in evidence/SAMPLE-p6-live-response.json. Its ten-note guard-checked replay is labelled in evidence/p6-ai-replay.json and made no new request. P5 retains a successful real normal-CLI batch. Do not claim the replay or service fallbacks as fresh AI or scheduled successes.
- provider_error_status now preserves a numeric HTTP failure code without provider messages or account identifiers. No service availability guarantee is made.

## Reproduce

```shell
uv sync --locked
# Windows, once
uv run python scripts/setup_windows_pdf.py
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest --cov=src/adsreport --cov-report=term-missing --hypothesis-show-statistics
uv run adsreport generate-sample --seed 42
uv run adsreport run --input data/sample --out out/review-p6 --no-ai
```

Use a fresh output directory when content differs. Local uv is .tools/bootstrap/bin/uv.exe. Set UV_CACHE_DIR to .tools/p1-cache, UV_PYTHON_INSTALL_DIR to .tools/python and optionally UV_LINK_MODE=copy. Windows native DLLs are in .tools/windows-pdf/mingw64/bin. The app finds them from the repo root. From another working directory, set WEASYPRINT_DLL_DIRECTORIES to that absolute path. The fresh-checkout test reuses this verified native installation explicitly. Ubuntu requirements are documented in OUTPUTS.md and the workflow, with hosted execution still blocked.

The ignored .env holds the owner's key and existing Free Tier attestation. Rotate the key shared in chat before unattended operation. On another machine, configure .env.example privately. Missing key/confirmation uses templates. No billing-admin status was independently verified, and no paid service was enabled.

## Interfaces and files

- load_inputs returns typed rows, input fingerprints, manifest, column-map hash and optional validated CatalogRow tuple. Catalog URLs use official LEGO references and are separately fingerprinted.
- calculate_report returns all ProductMetrics. summarize creates PortfolioWeek totals, TACoS and comparable-week differences. Units remain explicit.
- evaluate_rules returns RuleReport with every flag, skipped reasons and six deduplicated priorities by default. The fixture has ten flags across seven products.
- generate_commentary returns typed Commentary with notes, request status, attempts, model, prompt hash, ai_used, guard_rejections and optional provider_error_status. Preserve safe fallback and the one-quota-retry limit.
- render.model.make_view assembles ReportView. presentation.report_id is source/configuration/commentary content identity, not a run ID or approval token. view_manifest serializes portfolio/catalog presentation facts into report.json.
- render_charts produces namespaced SVG/PNG from shared ChartData. HTML autoescapes report text. WeasyPrint 70 URLFetcher disallows every external protocol and stops on resource errors. XLSX uses numeric/date cells and disables string-to-formula conversion. PPTX validates formula-like chart identifiers, retains editable native charts and normalizes OOXML timestamps including embedded workbooks.
- Stamp supports presentation of DRAFT or supplied reviewer/timestamp. P6 tests injected APPROVED display only. No approval command has been implemented or executed.
- pipeline.run_numerical_draft remains its callable name for compatibility. It calculates, assembles and renders, then publishes the complete byte bundle through artifacts.publish_bundle. CLI defaults to optional AI; --no-ai stays deterministic.
- artifacts.json fingerprints every other output. The file set is thirteen files. A renderer failure publishes nothing. The CSV retains the P3 golden format. File packaging dates use a canonical epoch and must not be treated as execution evidence.

## P7 work after approval

1. Record the owner's approval. Recheck current official Actions scheduling, artifacts, Environment reviewer and notification capabilities before implementation.
2. Resolve the external hosted-run blocker with the owner. The P6 push was checked and executed zero runner steps with the same billing-lock annotation. See evidence/p6-hosted-ci.json. Do not change spending settings or claim hosted jobs passed. P7's hosted/manual/unattended acceptance cannot be completed while runners remain locked.
3. Establish private replacement Gemini credentials and email/Discord destinations. Ask for missing setup statuses and destinations, never keys in chat. Both failure and approved-notice demonstrations are required. Capture real receipt evidence without publishing private destinations or webhooks.
4. Add genuine append-only run records with trigger, start/end, status, failed step, product/flag counts, AI/fallback/guard outcome, artifact hashes, Git SHA and approval state. Preserve provider-error codes separately from report success. Label injected failures and any replay/backfill. Scheduled success rate must state numerator/denominator and exclude test_failure.
5. Implement a frozen approval state around the exact manifest and file bytes. Retain draft and approved artifact identities, reviewer identity and timezone-aware timestamp. Verify file hashes before approving/delivering, reject stale/tampered files and do not call Gemini again. Re-stamp only the frozen approved content, preserve the draft, and hash approved artifacts separately.
6. Implement approve/deliver CLI behavior and weekly-report.yml with scheduled/manual build, artifact upload, required-reviewer client-delivery job and approved notices. CardinalisUnum is the planned reviewer. No automatic bid, price, budget, listing, delisting or refund actions.
7. Add email and Discord failure/approved notices using free services and safe secrets. Exercise both destinations, a labelled injected failure and human review. Do not report mere adapter return as a received notification. Bound the optional AI stage to the workflow time budget, honoring a provider retry delay or falling back explicitly rather than letting a long wait exhaust the whole job.
8. Capture a real unattended schedule run. Monday 09:17 Manila is 17 1 * * 1 UTC. A temporary near-future schedule is allowed for verification, then restore Monday. Select the latest mature Germany week for real adapters, while labelling fixed sample periods. Do not fabricate historical runs.
9. Run meaningful quality/failure/tampering tests, inspect outputs, update evidence/status/decisions/this handoff, scan secrets, commit/push, verify remote SHA and stop for P8 approval. P9 remains a separate independent reviewer task.

## Remaining acceptance

P1-5 hosted CI is still open. P7 operations, genuine approval, email/Discord receipts and unattended execution are unimplemented. P8 still needs measured manual versus assisted review effort and owner review of final documentation/demo. P9 needs an independent audit and release. Simulated seller performance is not actual business impact.

The repository is public. Use the configured owner Git identity without assistant co-author trailers. Keep .env, .tools, browser traces, generated out directories and original private handovers out of Git. The reviewed docs/examples bundle and evidence previews are intentional public SAMPLE artifacts.

## Copyable continuation request

Read AGENTS.md and docs/RESUME.md, then verify docs/STATUS.md and Git state. P6 is complete and P7 awaits my approval. Confirm approval before implementing operations. Preserve exact artifacts for approval, capture genuine runtimes/receipts, label failures/replays, update the handoff, commit and push, then stop at the next phase gate.
