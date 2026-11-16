# Operations and frozen review

Implementation is locally tested. Hosted execution and real email/Discord receipts remain unverified. See [owner actions](OWNER-ACTIONS.md) and [status](STATUS.md).

## Run locally

From the repository root, `uv run adsreport doctor` checks configuration and renders a small PDF without network calls. AI readiness is only the presence of private credentials and the owner's unbilled-project attestation. It does not prove current quota.

`uv run adsreport run --no-ai --open` creates a unique `reports/<run-id>/draft` directory and opens its HTML. Windows owners can run `./Start-Report.ps1` instead. Use `-NoOpen` for a terminal-only run, or `-UseAI` for optional Gemini. There is no application server or login page: the review interface is the generated local HTML alongside Excel, PDF and PowerPoint.

The fixture is always the labelled eight-week simulation ending November 1, 2026. Run time is real; sample periods are historical. The maturity check waits until the complete German week has ended plus seven full attribution days and one full latency day. It rejects a future/immature input week and records the mature cutoff. It does not fetch a fresh export or silently change the fixture's report week.

## Approve the reviewed version

1. Review all four files, their sample labels, flags, notes, null reasons and source fingerprints.
2. Run `uv run adsreport inspect --report reports/<run-id>/draft`. Retain its `manifest_sha256` outside the bundle as your review reference.
3. Explicitly approve: `uv run adsreport approve --report reports/<run-id>/draft --expect-manifest <draft-sha256> --reviewer "Patrick Jaso"`.
4. The new sibling `draft-approved` contains fourteen files, including `approval.json`. The original thirteen-file draft is retained. The new manifest hashes the approval and all approved artifacts.
5. Inspect the approved directory. Deliver only that returned manifest: `uv run adsreport deliver --report reports/<run-id>/draft-approved --expect-manifest <approved-sha256>`.

Approval validates every captured file hash and the complete file set, then restores the persisted facts. It calls neither the financial engine nor Gemini. Only status, reviewer, approval timestamp and their representations change. It reuses the six frozen chart images. Original and approved manifest identities are both recorded. Changed/missing/unexpected files, links, stale hashes and overwriting the draft are rejected. Rendering dependencies are pinned; source report identity remains the same while approved artifact hashes differ.

Local approval is explicitly **self-attested**, not authenticated identity or a cryptographic signature. Hashes provide version integrity when compared with the separately retained expected digest; they do not protect against a malicious person who can rewrite both files and your reference. Test approvals cannot use the production delivery command. Unit tests use the `test` mechanism and isolated temporary logs. They are never owner acceptance evidence.

## Notification states and retries

Keep `.env` private; `.env.example` names the fields. `NOTIFY_ENABLED=false` disables both transports. Complete email fields and a Discord webhook are separate requirements. SMTP uses TLS on port 465 or STARTTLS on 587. Use a provider-supported application credential, never assume an ordinary account password works. Discord uses its HTTPS webhook endpoint, `wait=true`, a returned message ID and disabled mentions. Redirects are refused. Archives larger than 8 MB are rejected conservatively.

`deliver` packages the exact approved files into a stable ZIP in ignored `reports/outbox/<approved-manifest>/`. Its private archive hash and per-channel receipts survive local retries. An exclusive lock prevents concurrent sends of that release on the same filesystem. Accepted channels are skipped. Explicit rejections may be retried; `sending`, network interruptions and ambiguous responses remain `uncertain` and are skipped unless `--retry-uncertain` is explicitly supplied. That override can duplicate a message. A leftover lock requires checking that no process is active before removing it.

The delivery exit code is 0 only when both providers acknowledge acceptance, 3 for disabled/missing/partial/uncertain channels, and 2 for validation or I/O failures. **Provider acceptance is not human receipt.** SMTP provides no message ID here; Discord returns its message ID. Receipt evidence and inbox screenshots still need the owner. A crash after external acceptance can leave an uncertain outcome; no exactly-once guarantee is made.

Run failures attempt both alert channels, with only run ID, trigger, failed stage and exception class. Raw error text, addresses, keys, webhooks and provider response bodies are excluded from the public log. Alert failure cannot silently turn a failed report into success. `--inject-failure` is deliberately labelled `test_failure`; it does not generate a report.

## Run history and success measures

`runs/run-log.jsonl` is append-only. Start, completion, approval and delivery are separate events. They retain actual UTC time, run identity, source Git SHA, dirty-tree status, trigger, duration, product/flag counts, AI attempt/fallback/guard outcome, output hashes and approval state. Repeating the same immutable approval does not append another approval. Conflicting event IDs fail instead of rewriting history.

`uv run adsreport history` reports successful app-observed scheduled builds divided by all observed scheduled starts, including incomplete starts. Manual runs and `test_failure` are excluded. At kickoff this is **0/0, unavailable**, never 100%. Report generation success does not mean AI success, approval, notification receipt or business impact. Failures before Python starts cannot enter this local measure; inspect GitHub workflow history separately for infrastructure reliability. CI failures are also separate from scheduled report builds.

The workflow merges new events into the current main-branch log through the Contents API with optimistic conflict retries, preserving existing bytes. A failed log write fails the workflow. Only validated log events are published; private receipts/outbox are not uploaded. Platform failures before log initialization remain visible only in Actions. Preserve original history if moving the app to another machine.

## Hosted workflow and human gate

`.github/workflows/weekly-report.yml` schedules `17 1 * * 1` UTC, Monday 09:17 Manila, and permits manual dispatch. Standard public Ubuntu runners, locked dependencies and SHA-pinned actions are used. No paid setting was enabled. GitHub's existing billing lock currently prevents hosted jobs from starting.

Build uploads `SAMPLE-draft` for fourteen days and prints its exact manifest hash in the job summary. Delivery waits for the `client-delivery` Environment, configured with owner `CardinalisUnum` as required reviewer and `main` as allowed branch. Self-review is allowed so the owner can approve a manually initiated run. The application also queries actual run approval history and requires the most recent delivery-environment review to be approved by that owner. Bypassing the environment without this record does not pass application verification. Re-runs with `GITHUB_RUN_ATTEMPT > 1` are refused for approval: start a new workflow run and review its new frozen artifact instead. GitHub does not provide a reviewer timestamp in this response; the recorded timestamp is when the app observed the verified approval.

Before enabling unattended use, configure repository secrets for Gemini and failure alerts, and `client-delivery` environment secrets for approved delivery. Use the names in `.env.example`. Set the non-secret repository variables `GEMINI_FREE_TIER_CONFIRMED=true` only for an unbilled project and `NOTIFY_ENABLED=true` only after destinations are verified. Prefer environment overrides for delivery variables. No exposed chat key was copied into Actions. Review [limits](LIMITS.md) before adding real merchant data to this public repository.

Sources checked November 16, 2026: [GitHub schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [Environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments), [review history API](https://docs.github.com/en/rest/actions/workflow-runs#get-the-review-history-for-a-workflow-run), [artifact retention](https://docs.github.com/en/rest/actions/artifacts), [Discord webhook API](https://docs.discord.com/developers/resources/webhook), [Python SMTP](https://docs.python.org/3/library/smtplib.html).
