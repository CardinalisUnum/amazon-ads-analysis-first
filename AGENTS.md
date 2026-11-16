# Agent entry point

Build an Amazon Ads reporting PoC with deterministic Python KPIs, nine evidence-backed rules, checked AI commentary, four visual outputs and human approval before delivery.

Read `docs/STATUS.md`, `docs/decisions.md`, `docs/SPEC.md` and `docs/RESUME.md` before changing the project. `CLAUDE.md` points to the same handoff.

## Working agreement

- The owner approved phase-by-phase work. At every phase gate, stop, report evidence and the full phase progress table with bars, commit and push, then ask for approval to begin the next phase. Record that approval before proceeding.
- Keep checkpoints small and use Conventional Commits. Push before handing control back. Report any failed push accurately and retry recoverable failures.
- Keep credentials in ignored `.env` locally and Actions secrets remotely. Never publish original private handovers, prospect correspondence, project account IDs or credentials.
- Use public LEGO catalog references with clearly labelled simulated independent retailer performance. Keep manufacturer set numbers distinct from sample ASINs and SKUs. Label sample outputs throughout.
- Use only free services with an unbilled Gemini project. Verify model access with a real call before claiming AI integration.
- All financial calculations belong in Python. Bind commentary claims to product, week, metric and unit. Provide deterministic fallback notes.
- Maintain a frozen report version for approval. Retain draft and approved artifact identities, reviewer identity and timestamp.
- Capture genuine runtime evidence and measured review effort. Label backfills and injected failures. State numerator and denominator for success rates.
- Validate changed behavior and update evidence and documentation with each checkpoint. Independent release audit remains a separate reviewer task.
- Source technical claims from official documentation and execution evidence. Mark untested dependencies and unanswered assumptions explicitly.

## Gates

P0 kickoff and verification → P1 scaffold → P2 sample data → P3 loader/KPIs → P4 rules → P5 commentary/guard → P6 outputs → P7 operations/approval → P8 docs/demo → P9 independent audit/release.

The task definitions and weights are in `docs/STATUS.md`. Current state and next executable steps are in `docs/RESUME.md`.
