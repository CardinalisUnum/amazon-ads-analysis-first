# Resume this checkpoint

Current phase P1. The owner approved P1 on 2026-11-16. P2 is awaiting its phase gate.

Read AGENTS.md, decisions.md, STATUS.md, SPEC.md and evidence/P1-REPORT.md first.

## Actual state

- Package, lock, CLI interface, strict configuration validation and CI are implemented.
- Local locked installation, Ruff, strict mypy and 21 tests pass. Coverage is 98%. See evidence/p1-local.txt.
- Workflow schema validation passes actionlint 1.7.12.
- Push and manual GitHub CI both ended at startup with zero jobs because of a provider account restriction. The owner confirmed the account banner in chat.
- Publication review of 34 tracked files found no supplied credential or known private handover/account details. The owner approved publication. Repository is public and free standard runner retry still returned startup_failure. Do not change visibility again.
- P1-5 remains incomplete until a successful hosted CI run is captured.

## Next actions

1. Owner account restriction remains unresolved. Capture a green hosted run after account access is restored.
2. Ask whether the owner approves beginning P2 with P1-5 still explicitly open. Continue only after approval.
3. Update the tracker and report, commit and push all evidence.
4. When P2 is approved, implement the deterministic sample generator. Keep P1-5 open until real hosted CI succeeds.

## Local environment

The uv cache issue was resolved using a fresh workspace-owned directory. In PowerShell set UV_CACHE_DIR to .tools/p1-cache and UV_PYTHON_INSTALL_DIR to .tools/python, both resolved from the repository root. Bootstrap uv is .tools/bootstrap/bin/uv.exe, Python 3.13.18 is under .tools/python, and .venv is the project environment. Standard uv commands work with those paths. A fresh clone can use an installed uv.

The ignored .tools/p0-check environment contains the earlier dependency probes. The app installs only its current dependencies. Later phases add analysis and rendering libraries. Windows Pango is still unavailable. Successful PDF rendering is required in P6.

The local .env contains the supplied Gemini key. It was shared in chat and must be rotated before unattended setup, saving the replacement directly. Never echo or commit keys.

## Git and remote operations

Origin is https://github.com/CardinalisUnum/amazon-ads-analysis-first.git, branch main. Git credential helper operations require escalation in this Windows sandbox. The ignored .tools/check_ci.py can query current-commit Actions status using that helper with credentials retained only in memory. Its code must never print credential responses.

Always update this handoff and push a checkpoint before returning control. Verify remote SHA and working-tree status.
