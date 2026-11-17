# Builder test readiness — November 17, 2026

This is builder verification, separate from P9's independent release audit. [Gmail setup is bookmarked](GMAIL-SETUP.md) and deferred at the owner's request. Local tests need neither actual email/Discord sends nor the exposed Gemini key.

**Final result:** 237 passed, 96% overall coverage. Ruff lint/format, strict mypy (38 source files), actionlint, and normal CLI readiness checks pass. Fifteen operational regression cases were added.

## Test coverage by behavior

| Area | Cases checked | Evidence |
|---|---|---|
| Inputs and KPIs | Columns, grain, joins, formulas, zero/undefined values, 200-example properties and unchanged 80-row golden CSV | `test_loader.py`, `test_kpi.py`, `test_pipeline.py` |
| Nine rules | Equality/lifecycle/history boundaries, exact fixture flags, evidence/priority ordering and review-only wording | `test_rules.py`, `test_sample.py` |
| Commentary/guard | Product/week/metric/unit/direction binding, unsupported values, permitted rounding, service/schema/quota fallback and bounded retry | `test_commentary.py` |
| Four outputs | Shared financial values, sample labels, workbook/deck structure, PDF text/pages, blocked resource fetches and no partial publication | `test_outputs.py`, P6–P8 package/visual evidence |
| Approval | Hash/file-set checks, stale version rejection, preserved facts/draft, no financial/AI recalculation, idempotent event, nested destination rejection and reviewer identity | `test_operations.py` |
| Delivery | Exact ZIP, draft/test/stale rejection, nested outbox rejection, corrupt archive, disabled/missing/partial channels, accepted-channel skip and explicit uncertain retry | `test_operations.py` |
| Crash safety | No send before durable sending state; interrupted acknowledgement persistence leaves uncertainty without automatically resending email | `test_operations.py` |
| Review and history | Owner/environment substitutions, reruns, trigger labels, injected-failure exclusion, incomplete starts, immutable IDs and full maturity intervals/DST | `test_operations.py` |
| Entry points/publication | Help/config/doctor/sample verification, lint/format/types/workflows, private settings kept private, links and publication scan | `evidence/readiness-20261117-entrypoints.txt` and final checkpoint |

The full-suite execution is in [readiness test output](evidence/readiness-20261117-tests.txt). Module setup and function calls use isolated logs. Genuine `runs/run-log.jsonl` must remain byte-identical across testing. Test approvals never count as actual owner approval.

## Findings reproduced and fixed

| Severity | Failure and impact | Fix | Regression |
|---|---|---|---|
| Major | Choosing `draft/approved` added a directory to the frozen draft and invalidated its exact file set. | Reject output equal to or beneath the resolved draft before writing. [approval.py:111](../src/adsreport/approval.py#L111). | `test_nested_approval_output_preserves_draft` |
| Major | An outbox beneath an approved report could create private files inside the frozen bundle. | Require the resolved archive directory outside the approved report, including a parent outbox whose digest-named child would equal the report itself. [delivery.py:31](../src/adsreport/delivery.py#L31). | `test_nested_delivery_outbox_preserves_approved_bundle` |
| Minor | Symbol-only reviewer values such as `...` and `_@-` were accepted. | Require an ASCII letter or digit within the existing character allowlist. [report.py:59](../src/adsreport/report.py#L59). | `test_approval_rejects_empty_reviewer_identity` |

Before fixes, four regression cases failed and whitespace alone already passed via the existing stamp check. After fixes, all five passed. Added crash/transport/reviewer tests guard existing behavior; they do not prove real receipt. No financial calculation, rule threshold or sample data changed.

## Remaining external acceptance

- The last observed GitHub account lock prevents hosted jobs from starting. Provider state was not re-probed or repeatedly dispatched during this local pass.
- Gmail is deferred and Discord is absent. Live authentication, failure-alert receipts and approved attachments need deliberate private setup and actual receipt evidence.
- Rotate the chat-exposed Gemini key before unattended use. Historical requests and fallback tests do not prove current quota.
- Human approval, documentation sign-off, timed review effort and an unattended schedule remain open.
- P9 requires a separate reviewer, independent arithmetic and promise audit. This pass cannot certify its own independence or create a release tag.

The local app runs offline. Strict acceptance remains 41/56 tasks, 82.3% weighted. Local hardening does not replace missing external evidence. See [owner actions](OWNER-ACTIONS.md) and [audit handoff](AUDIT-HANDOFF.md).
