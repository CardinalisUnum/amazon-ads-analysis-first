# Owner setup and acceptance checklist

The local reporting app is ready. **No notification account or working Gemini quota is needed to generate all four reports.** The remaining items below concern optional AI, hosted automation, delivery and release evidence.

## Run it now

Open PowerShell in the repository and run:

```powershell
./Start-Report.ps1
```

It verifies the locked environment and local PDF support, creates a fresh DRAFT, logs the real runtime, and opens the HTML. Its default is offline templates. The printed `reports/<run-id>/draft` directory contains Excel, HTML, PDF, PowerPoint and their evidence. Use `./Start-Report.ps1 -UseAI` only after private key rotation; provider problems safely select labelled templates. No report is approved or sent by this launcher.

On a fresh Windows checkout: install free [uv](https://docs.astral.sh/uv/getting-started/installation/), run `uv sync --locked`, then `uv run python scripts/setup_windows_pdf.py` once before the launcher. If local PowerShell policy blocks a script, use `uv run adsreport run --no-ai --open` instead of changing machine policy.

## Consolidated owner-dependent items

| Priority | What needs you | Completion evidence | Blocks local reports? |
|---|---|---|---|
| 1 | Resolve the existing GitHub account lock in Settings → Billing & licensing, or contact GitHub Support. Keep the free-only requirement; do not raise spending just to clear this PoC. | A CI run actually starts and passes. | No |
| 2 | Rotate the Gemini key shared in chat. Save its replacement only in ignored `.env`, from an unbilled Free Tier project. | Private replacement configured, then a real normal run with `parsed_response`, accepted notes and recorded source identity. | No |
| 3 | Gmail sender selected. Choose a test recipient and privately fill the sender address and application password in `.env`; the six SMTP fields are documented in `.env.example`. | A test alert and approved ZIP actually arrive. | No |
| 4 | Create a webhook for your chosen Discord test channel; save its URL privately. | A test alert and approved ZIP actually appear in that channel. | No |
| 5 | After local tests, copy private configuration into the right GitHub secrets and enable the two documented variables. | Manual workflow builds, uploads a draft and visibly waits for you. | No |
| 6 | Review that exact draft and approve its `client-delivery` gate. Verify both messages and their attachment hashes. | Genuine waiting/approval state and two receipt records; sanitize screenshots before publication. | No |
| 7 | Let a genuine scheduled run complete after runner access is restored. A developer may temporarily use a near-future schedule for this verification, then restore Monday 09:17 Manila. | Actions run URL with event `schedule`, successful build and reviewable artifact. | No |
| 8 | Review README and PROCESS; measure manual versus assisted review with a stopwatch using [measurement instructions](REVIEW-EFFORT.md). | Your approval and actual timed results, with date/scope. | No |
| 9 | Ask Claude or another reviewer to perform the separate [independent audit](AUDIT-HANDOFF.md). | Findings, arithmetic worksheet, fixes rechecked and release approval. | No |

Do not paste keys, SMTP credentials, email addresses or webhooks into public issues, this repository or chat. Share setup status only. Existing screenshots of failed CI indicate an account restriction, not a demonstrated code failure. Do not ignore future failures after runners unlock: then inspect the failed step.

## Recommended free email route

For this small PoC, use an existing personal Gmail account **if it offers app passwords**, with 2-Step Verification enabled, `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, your complete sender address for username/from, a generated app password for `SMTP_PASSWORD`, and your chosen test mailbox for `SMTP_TO`. Keep `NOTIFY_ENABLED=false` until ready to send a deliberate test, then set it to true. These are ordinary low-volume messages within the account's limits; no paid mail API is needed. Availability depends on the account and its policies. Google documents that app passwords require 2-Step Verification and may be unavailable under organizational/security policies. Never use your main Google password. Sources: [Google app passwords](https://support.google.com/accounts/answer/185833), [Gmail SMTP settings](https://developers.google.com/workspace/gmail/imap/imap-smtp).

This app currently implements SMTP application-credential login, not Microsoft OAuth. If you want Outlook as the **sending** account and it requires OAuth, choose a supported sender for the PoC or request the OAuth adapter before delivery. Outlook can still receive the test messages. No claim is made that an ordinary Outlook password will work.

For Discord: Server Settings → Integrations → Webhooks → create/copy the webhook and choose its channel; permissions depend on your server role. Use only a test channel you control. [Official webhook instructions](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

## Private GitHub settings after account recovery

Repository settings → Secrets and variables → Actions: add `GEMINI_API_KEY` only after rotation; add SMTP fields and `DISCORD_WEBHOOK_URL` for build-failure alerts. Set repository variables `GEMINI_FREE_TIER_CONFIRMED=true` only for an unbilled project and `NOTIFY_ENABLED=true` when ready. Under Environments → `client-delivery`, configure SMTP/webhook secrets for approved delivery. The required reviewer and main-branch restriction are already configured; do not remove them. The names are in `.env.example`, and [OPERATIONS](OPERATIONS.md) explains scope, identities and retries.

Never use real confidential seller exports with the public workflow until private storage/access controls are redesigned and reviewed. Current public artifacts and logs are intentionally simulated.
