# Resume this checkpoint

Current phase P3. Owner approved P2 flags and assumptions and authorized P3 on 2026-11-16. Pause for approval before P4. Hosted CI P1-5 remains open.

Read AGENTS.md, decisions.md, STATUS.md and SPEC.md first.

## Implemented at this checkpoint

- P2 sample generator and owner-approved seven-file sample remain unchanged.
- P3 typed CSV loader, input schemas, Decimal KPI engine, numerical draft pipeline and CLI run --no-ai are implemented.
- The loader captures source bytes once, verifies declared hashes, aggregates ads before joining retail, and preserves complete-export retail-only products.
- Baseline tests currently pass 81 cases. Both Hypothesis properties pass 200 generated examples. Earlier coverage run showed 98% on the KPI engine.
- tests/golden/SAMPLE_kpis.csv captures the 80-row deterministic numerical output.
- The shared artifacts.py publisher is used by sample generation and numerical reports. Existing different output content is preserved.
- Column-map internal date key is now day, accepting Date and date aliases.
- The reporting, rules and AI commentary layers are still future phases. The current run command emits a DRAFT numerical CSV and JSON only.

## Finish this phase

1. Run all quality gates and capture docs/evidence/p3-local.txt.
2. Review remaining error handling and verify a clean checkout preserves golden bytes. New test snapshots use LF in .gitattributes.
3. Update README, assumptions, the P3 report and all six P3 task evidence entries.
4. Scan the publication set for credentials/unintended files, commit and push. Verify remote SHA.
5. Present the full phase progress table and ask the owner for P4 approval.

## Commands

From the repository root, use installed uv. Local bootstrap is .tools/bootstrap/bin/uv.exe. Set UV_CACHE_DIR to the absolute .tools/p1-cache path and UV_PYTHON_INSTALL_DIR to .tools/python if needed.

uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest --cov=src/adsreport --cov-report=term-missing --hypothesis-show-statistics
uv run adsreport run --input data/sample --out out/p3-final --no-ai

Choose a fresh --out path if existing content differs. The pipeline is deterministic and can verify identical existing output.

## Important continuation details

Input needs manifest.json plus ads.csv, total_sales.csv, costs.csv and inventory.csv, accepting SAMPLE_ prefixes. The manifest declares the sample label, date range and tax bases. The loader accepts canonical internal fields and configured English Amazon aliases. Raw multiweek retail exports without product-week metadata need a normalized adapter.

The model uses net retail revenue rounded to cents, per-unit referral minimum/rounding and per-week expected return costs. All source data is synthetic. Live API connections remain out of scope.

The project is public. Use the configured owner Git author identity and no assistant co-author trailers. Keep .env, .tools and private original handovers out of Git. The supplied Gemini key must be rotated before unattended setup.

Git credential helper operations require escalation in this Windows sandbox. Always commit/push an accurate resume checkpoint before returning control, and verify remote SHA.
