# Limits and outstanding evidence

## Data and business claims

Public LEGO references identify real products. All sales, ads, inventory, costs, performance stories and sample ASINs/SKUs are fictional independent-retailer scenarios. Manufacturer set numbers remain separate. There is no LEGO affiliation or access to its commercial account. The sample is fixed to September–November 2026, not a live seller feed. Runtime timestamps are genuine and separate from sample reporting weeks and canonical document packaging dates.

No live Amazon API, automated export ingestion, localized-export acceptance, production authentication or merchant deployment is supplied. Confirm actual column/tax/attribution definitions, costs and lifecycle against [INPUT-CONTRACT](INPUT-CONTRACT.md) before a real integration. German 19% VAT, fee/return models, thresholds and maturity intervals are assumptions. Organic share is a residual proxy. Flags identify review conditions and do not establish causes. No business uplift, recovered revenue or review-time saving is claimed without actual evidence.

## AI and free services

The pinned Gemini model has historical real-call evidence under an owner-attested unbilled Free Tier project. That is not an independent billing audit or a promise of current free quota. The app requires that attestation and the reviewed model; otherwise it uses templates. Free quotas, availability and data terms can change. No billing link, paid model, paid mail API, private paid runner or spending-limit increase was configured. The key exposed in chat must be rotated privately before unattended operation.

Structured claim validation enforces product/week/metric/unit/direction and supported rounding, not general causal correctness. Output labels disclose templates, accepted AI and rejection reasons. Provider errors remain a separate AI outcome from numerical report success. Each network attempt has a sixty-second timeout; one quota retry waits at most 120 seconds in total. A longer server delay is respected by declining to retry and selecting `quota_retry_deferred`, rather than retrying early or waiting indefinitely. SMTP/Discord attempts each have a twenty-second timeout.

## Hosted reliability

The current GitHub account billing lock prevents jobs from starting, despite the repository being public. Local lint, types, tests and workflow validation pass; hosted CI, the new manual report, actual approval screens and an unattended schedule remain unverified. Do not treat the resulting GitHub failure emails as proof that Python tests failed. Once runner access is restored, inspect all failures normally.

GitHub schedules are best effort: they may be delayed or dropped under load, run from the default branch and can be disabled after sixty days without repository activity in a public repository. Monday 09:17 Manila uses off-minute `17 1 * * 1` UTC; it is not a guaranteed delivery time. Do not depend on history commits alone to prove the schedule is enabled; check Actions after inactivity or account recovery. Artifacts expire after fourteen days under this workflow; retain any needed evidence privately. Sources: [schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [artifact storage](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/storing-and-sharing-data-from-a-workflow).

App-recorded scheduled build success is a named milestone with numerator and denominator. It excludes manual/injected tests, includes incomplete observed starts, and cannot see failures before Python starts. Workflow-level reliability must use actual Actions history; neither is a receipt or business-impact metric. Current scheduled evidence is 0/0, unavailable. Application failure alerts require Python to start; checkout, dependency-install and locked-runner failures remain Actions alerts rather than guaranteed email/Discord messages.

## Review and delivery boundaries

GitHub Environment required reviewers are available for public repositories on the free plan. Making the repository private on that plan can remove the protection. Keep delivery disabled until review controls are revalidated. A manual workflow dispatch alone is **not approval**. The supported local fallback is a separate explicit manifest-bound `approve` command after human review. Do not silently remove the gate. [Environment documentation](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

Local reviewer names are self-attested. Hashes provide version identity against a separately retained digest, not a digital signature or tamper-proof identity database. A malicious actor with write access to both the bundle and external reference can forge a new version. Hosted review-history verification supplements the environment gate, but no hosted waiting/approved state has been observed. Existing workflow re-runs are refused for approval; start and review a new run. No unattended auto-approval is implemented.

Notification tests use mock transports. SMTP and Discord acknowledgement means provider acceptance, not verified human receipt. Local persistent receipts skip accepted channels; uncertain sends require an explicit retry that can duplicate a message. This is not exactly-once external delivery. The current 8 MB archive limit is conservative; mail/provider/server limits and spam filtering still apply. The SMTP adapter supports provider application credentials and TLS, not Microsoft OAuth. Private receipt state must be retained across retries and machines. Fresh workflows are distinct reports and need distinct review.

## Deployment and release

This is a Python CLI plus static report artifacts, not a hosted interactive dashboard. Native PDF libraries and installed fonts affect layout; Ubuntu rendering is not yet exercised on hosted runners. The documented Windows setup downloads SHA-pinned DLL/font packages locally. The build makes no system-wide installation or billing change on the owner's PC.

Public repository/logs/artifacts are acceptable for the simulated demonstration only. Real merchant data requires private storage, access controls, retention/privacy decisions and a separate deployment review. Never commit original handovers, correspondence, credentials, webhook URLs, SMTP addresses or account project IDs. A fresh-checkout test does not replace a separate independent reviewer. P9 and the release tag remain open.
