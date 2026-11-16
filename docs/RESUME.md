# Resume this checkpoint

P7 operations are implemented locally with 222 passing tests. The owner authorized finishing all remaining buildable work without repeated phase questions; see decisions.md. Hosted acceptance remains blocked by the existing account billing lock. No release tag or independent audit is claimed.

Read AGENTS.md, STATUS.md, decisions.md, SPEC.md and OPERATIONS.md first. P6 examples remain frozen DRAFT sample snapshots. Real operational CLI runs create unique reports/<run-id>/draft directories, with real UTC identity and append-only runs/run-log.jsonl events. Unit tests isolate their logs and disable notifications.

Approval captures the exact manifest, preserves the original draft, restores persisted facts without financial or AI recalculation, stamps a new output and records separate approved hashes. Test approvals are blocked from production delivery. Local reviewer identity is self-attested; hosted approval queries actual owner Environment review history. Re-runs of an existing workflow are refused for hosted approval; start a fresh workflow and review its new artifact.

Email and Discord transports are implemented and mock-tested. No private destinations are configured. No actual approval, receipt or unattended success was invented. The Environment is configured for CardinalisUnum/main; actual hosted waiting/approved states remain unverified. See evidence/p7-environment.json and evidence/P7-REPORT.md.

Next: capture genuine local offline and injected-failure runs after this implementation commit, finish README/PROCESS/LIMITS/owner setup/demo/auditor handoff, update status against strict acceptance, self-check, commit and push. Keep P9 independent. Rotate the Gemini key privately before unattended use. Never copy the exposed key into Actions.

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
