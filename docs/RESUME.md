# Resume this checkpoint

**Saved owner setup bookmark:** [Resume Gmail setup](GMAIL-SETUP.md). On November 17, 2026 the owner deferred this setup and asked to continue local readiness testing. Keep notifications disabled; do not treat the pause as configured credentials or received messages.

All buildable P7 code and P8 documentation are complete locally, with 237 passing tests (96% overall coverage). Strict acceptance is 41/56 tasks, 82.3% weighted; see STATUS.md for the full phase table. The owner authorized finishing all remaining buildable work without repeated phase questions; see decisions.md. Hosted acceptance remains blocked by the existing account billing lock. No release tag or independent audit is claimed.

Read AGENTS.md, STATUS.md, decisions.md, SPEC.md and OPERATIONS.md first. P6 examples remain frozen DRAFT sample snapshots. Real operational CLI runs create unique reports/<run-id>/draft directories, with real UTC identity and append-only runs/run-log.jsonl events. Unit tests isolate their logs and disable notifications.

Approval captures the exact manifest, preserves the original draft, restores persisted facts without financial or AI recalculation, stamps a new output and records separate approved hashes. Test approvals are blocked from production delivery. Local reviewer identity is self-attested; hosted approval queries actual owner Environment review history. Re-runs of an existing workflow are refused for hosted approval; start a fresh workflow and review its new artifact.

Email and Discord transports are implemented and mock-tested. No private destinations are configured. No actual approval, receipt or unattended success was invented. The Environment is configured for CardinalisUnum/main; actual hosted waiting/approved states remain unverified. See evidence/p7-environment.json and evidence/P7-REPORT.md.

## Current evidence and next work

November 17 builder readiness: 237 tests pass, including fifteen added operational regressions. See TEST-READINESS.md and evidence/readiness-20261117-tests.txt. Approval output and delivery archive targets are rejected inside frozen reports, and reviewer identity requires a letter or digit. CLI help/config/doctor/sample checks, lint, types and workflow validation pass. Real history and frozen examples remain intact. This is builder verification, not P9 independent audit.

- Start-Report.ps1 completed a genuine local offline run at 2026-11-16 15:36 UTC: run 20261116T153601Z-7150091f311b, 6.382 pipeline seconds, ten products, ten flags, thirteen files. Source identity and dirty-tree disclosure are in evidence/p7-local-run.json. Local HTML, Excel, eight-page PDF and five-slide deck are available in reports/<run-id>/draft (ignored). Committed P6 examples remain static review references.
- One actual labelled injected failure is in runs/run-log.jsonl; alerts were disabled. Scheduled evidence is 0/0, unavailable. Neither historical sample weeks nor unit calls were backfilled into operational history.
- Both CI and one manual weekly-report attempt failed before job start with the account-lock annotation. See evidence/p7-hosted-ci.json and p7-manual-hosted.json. Do not rerun repeatedly while that restriction persists.
- Final tests use both session-level isolation for module rendering setup and per-test temporary logs. The full suite leaves genuine history byte-identical. No mocked acceptance is recorded as an actual receipt. SMTP has conservative uncertain-state handling, including failed QUIT after possible DATA acceptance.
- README, PROCESS, LIMITS, OPERATIONS, OWNER-ACTIONS, REVIEW-EFFORT, loom-script and AUDIT-HANDOFF are present. Owner documentation approval, measured effort and P9 are outstanding. Source archives explicitly select publication roots so ignored local checkout files cannot leak through broad environment-template ignore exceptions.

Next executable work is owner-dependent: use OWNER-ACTIONS.md to recover free runner access, privately rotate Gemini credentials, choose/configure email/Discord destinations, and configure Actions secrets. Never copy the exposed key into Actions. Then run one manual workflow, review the exact uploaded draft, obtain genuine owner approval and both receipts, exercise the labelled failure alert, and verify an actual schedule. Restore Monday 09:17 Manila after any temporary verification schedule. Update evidence/status without claiming real merchant impact.

For independent review, give another reviewer AUDIT-HANDOFF.md and the current main SHA. P9 must remain independent of the builder; no v1.0.0 tag until acceptance and audit findings are resolved. The owner selected an existing personal Gmail sender with app-password support. Local non-secret defaults use smtp.gmail.com:587 with notifications disabled. Private sender/recipient fields and application password still need setup; no live authentication or receipt has occurred. No address or credential was requested in chat.


Local commands:

```powershell
./Start-Report.ps1 -NoOpen
# Or with uv installed:
uv run adsreport doctor
uv run adsreport run --no-ai --open
uv run adsreport history
```

Windows native PDF dependencies already exist in ignored .tools/windows-pdf. On a new machine run uv sync --locked and uv run python scripts/setup_windows_pdf.py. Local uv is .tools/bootstrap/bin/uv.exe. Set UV_CACHE_DIR=.tools/p1-cache, UV_PYTHON_INSTALL_DIR=.tools/python and UV_LINK_MODE=copy if using that bootstrap. The app finds native PDF DLLs from the repository root.

Quality gates: uv sync --locked; uv run ruff check .; uv run ruff format --check .; uv run mypy --strict src/; uv run pytest --cov=src/adsreport --cov-report=term-missing. Validate both workflows with actionlint. Final P7 coverage output is evidence/p7-local.txt. Keep numerical and sample golden files unchanged. No original private handover, project IDs, credentials, receipts or generated reports belong in Git.
