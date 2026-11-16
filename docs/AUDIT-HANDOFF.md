# Independent release audit handoff

Role: independent reviewer, separate from the implementation builder. This package is ready for review, not a completed audit or release authorization. Read AGENTS.md, RESUME.md, STATUS.md, decisions.md, SPEC.md, INPUT-CONTRACT.md, RULES.md, COMMENTARY.md, OUTPUTS.md, OPERATIONS.md and LIMITS.md.

The owner authorized finishing remaining buildable work. Do not treat unresolved account access, human approval, notification receipt, scheduled execution or stopwatch results as completed. Do not infer receipt from provider return values, or business impact from simulated financials. Keep credentials/private account details out of Git and screenshots.

## P9 execution

1. Fresh clone main into a separate workspace. Run `uv sync --locked`, documented native PDF setup, lint, formatter check, strict mypy, the full test suite/coverage, CLI help/config/doctor and actionlint on both workflows. Save raw outcomes, environment and exact source SHA. Builder checks are historical evidence, not your independent result.
2. Select three product ASINs independently, record how they were selected and hand-recalculate every applicable KPI from source rows. Retain a worksheet with input references, VAT/tax bases, formula, independent result, report result and rounding tolerance. Include zero/undefined cases separately. Do not import the production financial functions to calculate the expected answer.
3. Build a clause-by-clause promise table against the specification and owner decisions. Distinguish implemented, independently verified, externally blocked and intentionally excluded. Inspect all four formats, numerical/claim consistency, labels, catalog versus sample identities and footprint.
4. Exercise failure/tampering/partial delivery cases. Verify no AI or financial recomputation during approval; draft preservation; exact manifests; local identity disclosure; current owner GitHub review verification; rerun refusal; stale/uncertain channel states; no hidden success after failed logging. Confirm run denominators include incomplete starts and exclude injected tests. Check Python-start failures against Actions history separately.
5. Audit publication contents including nested OOXML packages for secrets, account identifiers, original handovers and private receipts. Review pinned actions/dependencies and free-service assumptions. Actual notifications need owner-provided destinations and sanitized real evidence. Keep mocks explicitly labelled.
6. Report blocker/major/minor findings with file/line, concrete failure sequence, impact, fix and reproduction. Builder fixes blockers/majors; you reverify those changes. Sign off only with zero unresolved blockers/majors and all required external acceptance evidence.

Only then may an authorized maintainer create `v1.0.0` and release notes with actual verification scope. Do not tag merely because local tests pass or to make a completion bar reach 100%.

## Current external blockers

The account lock prevents hosted CI/manual/scheduled execution. Email/Discord destinations and genuine receipts are absent. Gemini key rotation is owner work; the historical real request is not a new availability check. Owner documentation approval and measured review effort remain pending. [OWNER-ACTIONS](OWNER-ACTIONS.md) consolidates these tasks.

## Copyable request for Claude

> Act as the independent P9 reviewer for CardinalisUnum/amazon-ads-analysis-first. Read AGENTS.md and docs/RESUME.md, then follow docs/AUDIT-HANDOFF.md from a fresh checkout. Review the current main commit and preserve all acceptance limits. Do not invent external evidence or change billing/spending. Record findings and independent arithmetic, request owner setup only where required, and commit/push sanitized audit results under my configured Git identity without assistant coauthor tags. Fixes must be reverified before a release tag.
