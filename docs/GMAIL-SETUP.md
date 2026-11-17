# Bookmark: resume Gmail setup here

Saved at the owner's request on November 17, 2026 (Manila/Singapore time). Gmail setup is deferred while local testing and readiness work continue. Selection checkpoint: `68c14a5`.

## Saved position

- Sender choice: existing personal Gmail with app-password support.
- Local defaults: `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587` (STARTTLS).
- Keep `NOTIFY_ENABLED=false` while setup is deferred.
- No message or live Gmail authentication has been performed. Real receipts are still pending.
- Private setup belongs only in ignored `.env` locally and Actions secrets remotely; no credentials or addresses belong in the handoff.

## When the owner resumes

1. Open [Google App Passwords](https://myaccount.google.com/apppasswords), with 2-Step Verification enabled, and create an app password named **Amazon Ads PoC**. [Google instructions](https://support.google.com/accounts/answer/185833?hl=en).
2. Edit the existing local `.env`, preserving the other settings. Fill `SMTP_USERNAME` and `SMTP_FROM` with the Gmail sender, `SMTP_PASSWORD` with the generated app password, and `SMTP_TO` with the intended test recipient. Use the generated password without its display-grouping spaces, not the normal account password. [SMTP server settings](https://developers.google.com/workspace/gmail/imap/imap-smtp).
3. Leave notifications disabled until a deliberate test is arranged. Reply **Gmail configured** with setup status only, never the password.
4. Verify an actual test receipt before counting email delivery as accepted. Configure Discord separately; a successful email is not proof that both channels work. Normal report delivery still requires review of the exact frozen draft and explicit approval.

The local reporting app remains usable with `./Start-Report.ps1` throughout this pause. See [all owner actions](OWNER-ACTIONS.md), [operations](OPERATIONS.md) and [current status](STATUS.md). This bookmark does not pause independent local build/testing work or mark the external acceptance checks complete.
