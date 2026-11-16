# Resume this checkpoint

Current phase P2, approved by the owner on 2026-11-16 with P1-5 still open. Pause before P3.

Read AGENTS.md, decisions.md, STATUS.md, SPEC.md and evidence/P1-REPORT.md first.

## Actual state

- P2 was authorized with P1-5 still open. Owner approval is required before P3.
- The generator is available through uv run adsreport generate-sample --seed 42.
- The seven committed sample files cover ten real catalog references and eight simulated weeks. See P2-SAMPLE-REVIEW.md and ASSUMPTIONS.md.
- Local locked install, Ruff, strict mypy and 32 tests pass. Total coverage is 98%. See evidence/p2-local.txt.
- Three seeds reproduce byte-identical outputs and verify all intended final-week rules by independent fixture arithmetic. The production KPI and rules engines remain future phases.
- P2-3 expected flags and P2-5 range assumptions await owner review. P2-1, P2-2 and P2-4 are complete.
- P1-5 remains open. Public GitHub CI attempts stopped before jobs due the known account restriction.
- The repository is public with owner approval. Keep the configured owner Git author identity and no assistant co-author tags.

## Next actions

1. Ask the owner to approve the expected flags and assumptions in the P2 review files and approve P3.
2. On approval, mark P2-3 and P2-5 complete, record the approval and implement the P3 loader and deterministic KPI engine.
3. P3 needs input validation, source column mapping, the 33.6% example, edge cases, property tests and a deterministic snapshot.
4. Preserve sample identifiers, tax/fee conventions and exact count aggregation. Test alternative report headers and two campaigns joining to one retail row.
5. Keep P1-5 open until a real hosted CI run succeeds. Do not substitute local evidence for that gate.
6. Commit/push, then stop at the next phase gate.

## Local environment

The uv cache issue was resolved using a fresh workspace-owned directory. In PowerShell set UV_CACHE_DIR to .tools/p1-cache and UV_PYTHON_INSTALL_DIR to .tools/python, both resolved from the repository root. Bootstrap uv is .tools/bootstrap/bin/uv.exe, Python 3.13.18 is under .tools/python, and .venv is the project environment. Standard uv commands work with those paths. A fresh clone can use an installed uv.

The ignored .tools/p0-check environment contains the earlier dependency probes. The app installs only its current dependencies. Later phases add analysis and rendering libraries. Windows Pango is still unavailable. Successful PDF rendering is required in P6.

The local .env contains the supplied Gemini key. It was shared in chat and must be rotated before unattended setup, saving the replacement directly. Never echo or commit keys.

## Git and remote operations

Origin is https://github.com/CardinalisUnum/amazon-ads-analysis-first.git, branch main. Git credential helper operations require escalation in this Windows sandbox. The ignored .tools/check_ci.py can query current-commit Actions status using that helper with credentials retained only in memory. Its code must never print credential responses.

Always update this handoff and push a checkpoint before returning control. Verify remote SHA and working-tree status.
