# P7 implementation checkpoint

The owner authorized remaining buildable work on November 16, 2026. P7 operations are implemented locally; externally dependent acceptance remains open. This is builder verification, not an independent release audit.

- Frozen approval preserves draft bytes and persisted financial/rule/commentary facts. It produces separate stamped artifact hashes and a reviewer/timestamp/origin record. No new financial or AI calculation runs during approval.
- Run records capture actual UTC lifecycle events and source Git identity. Scheduled rates include incomplete app starts and exclude manual/injected failures. Platform failures before app startup are outside this denominator and must be checked in Actions.
- SMTP/Discord adapters have independent acknowledgement states, local persistent receipts, an exclusive delivery lock, stable archives and explicit handling of ambiguous outcomes. Mock transport tests prove adapter behavior only, not real delivery.
- The weekly/manual workflow uploads the frozen draft and requires an owner environment review. Actual review-history verification provides an additional application check. Re-running an existing workflow cannot reuse its approval for newly built content.
- The GitHub Environment was configured through its API; sanitized evidence is in `p7-environment.json`. Actual waiting/approval states and hosted runner execution remain blocked by the account lock.
- `Start-Report.ps1`, `doctor`, `inspect` and `history` make the local application usable without notification settings or working Gemini quota.

Quality output is in `p7-local.txt`; operational tests cover hash changes, preserved facts, no recalculation, stale approvals, draft/test delivery rejection, exact ZIP contents, channel retries, interrupted sends, secure transports, real-review context checks, append-only history, injected failure handling and maturity cutoffs. Failed development test invocations were corrected before the final gate. Pre-isolation development logs were quarantined in ignored `.tools` and are not published as operational history.

The local launcher produced a genuine thirteen-file draft with ten products and ten flags in 6.382 pipeline seconds, excluding startup/setup/human review. `p7-local-run.json` retains its actual times, source SHA and dirty-tree disclosure. The eight-page PDF, six-sheet workbook and five-slide deck opened through their parsers; the final PDF provenance page was rendered and inspected with no clipped identity. An explicit local injected failure was recorded with both alerts disabled, so receipt acceptance remains open. The public log has only these actual local operations, not unit-test calls.

An additional publication check caught module-scoped rendering fixtures running before function-scoped environment isolation. A session-level isolation fixture now protects those setup calls too. The full suite left genuine history byte-identical. Unpublished development records were quarantined rather than counted as real operational runs. SMTP port handling also accepts a blank optional workflow secret as the documented 587 default and rejects malformed values as configuration failures.

Both the pushed CI run and one registered manual weekly-report dispatch failed before executing jobs with the same account-lock annotation; see `p7-hosted-ci.json` and `p7-manual-hosted.json`. No repeated verification dispatches were made.

## Acceptance still needing external evidence

P1-5: hosted CI success. P7-1: green manual hosted report. P7-3: screenshot of waiting and actual owner-approved environment states. P7-4: real failure alert received in both channels. P7-5: labelled injected failure plus both real alert receipts. P7-6: successful unattended schedule trigger. No such result is claimed from mocks, local execution or existing service responses.

See [operations](../OPERATIONS.md), [owner actions](../OWNER-ACTIONS.md) and [status](../STATUS.md). No release tag is authorized by test completion alone.
