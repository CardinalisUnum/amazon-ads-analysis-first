# Resume this checkpoint

P4 is implemented and verified with 122 passing local tests. Final clean-checkout verification and phase report are in progress. The owner approved P4 on 2026-11-16 and requested a pushed handoff. Stop for approval before P5. P1-5 remains open due GitHub's account restriction.

Read AGENTS.md, docs/STATUS.md, docs/decisions.md, docs/INPUT-CONTRACT.md and docs/RULES.md first.

## Implemented

- src/adsreport/rules/engine.py evaluates R1-R9 for a requested report week. It returns typed RuleReport with every flag, skipped-rule reasons and priorities.
- Flags contain exact Decimal/date evidence and thresholds. Pydantic JSON round trips are tested.
- Top products are deduplicated, sorted by highest severity and retain all rule IDs. settings.priority_products defaults to six.
- The normal run --no-ai pipeline attaches analysis to report.json and sets stage to rules. The 80-row numerical CSV remains unchanged.
- 122 tests pass. Total coverage is 98%, with 100% KPI and rules engine coverage. See docs/evidence/p4-local.txt.
- docs/evidence/SAMPLE-p4-analysis.json captures the actual ten sample flags across seven products and six priorities.
- No application dependency was added.

## Finish the phase

1. Run a clean Git checkout with Windows line-ending conversion and verify all tests and both draft bytes.
2. Finish docs/evidence/P4-REPORT.md, STATUS.md and this continuation file.
3. Scan the publication set, commit and push, verify remote SHA and clean working tree.
4. Show the full phase table and ask the owner for P5 approval. Do not begin P5 without it.

## Reproduce

uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest --cov=src/adsreport --cov-report=term-missing --hypothesis-show-statistics
uv run adsreport run --input data/sample --out out/review-p4 --no-ai

Use a new output directory if its content differs. Bootstrap uv is .tools/bootstrap/bin/uv.exe locally. Resolve UV_CACHE_DIR to .tools/p1-cache and UV_PYTHON_INSTALL_DIR to .tools/python if needed. A fresh clone can use installed uv and the committed Python version.

## After P5 approval

Implement schema-validated Gemini commentary, fact-bound number checking, labelled deterministic templates and one quota retry followed by fallback. Preserve deterministic KPIs and rule evidence. Read docs/SPEC.md and decisions.md before implementation. The sample has ten products, while the display priorities default to six. Commentary must cover all ten products.

Runtime Gemini dependencies are not yet installed in the app. P0 evidence records google-genai 3.3.0, interactions.create with structured response_format, and successful gemini-3.5-flash-lite access. Recheck current free quota with the owner's unbilled project before claiming live P5 verification. The chat-shared key must be rotated before unattended setup and stored privately.

Never generate target numbers or dates without provided facts. Binding must include product, week, metric, unit and direction. A number present in another metric is insufficient. Fall back for the affected product and record why. Real model calls must remain synthetic and Free Tier.

## Other blockers

Hosted CI P1-5 is still open. Existing account billing restriction prevents runner steps. Windows PDF-native dependencies are absent and must be established before P6. Approval, delivery, scheduled run history, alert receipts and measured human review savings remain future acceptance checks.

The repository is public. Preserve the configured owner Git author identity and no assistant co-author trailers. Keep .env, .tools, generated out directories and original private handovers outside Git. Verify local/remote SHA after pushing. Updated code, sample fixtures, evidence and this handoff must be included at every checkpoint.
