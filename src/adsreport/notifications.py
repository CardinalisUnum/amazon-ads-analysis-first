"""Explicit provider acknowledgements, without treating them as human receipts."""

import json
import re
import smtplib
import ssl
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import UTC, datetime
from email.message import EmailMessage
from pathlib import Path

from adsreport.environment import read_environment

NAMES = (
    "NOTIFY_ENABLED",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "SMTP_FROM",
    "SMTP_TO",
    "DISCORD_WEBHOOK_URL",
)
EMAIL_FIELDS = ("SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM", "SMTP_TO")


class NotificationConfigError(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> None:
        return None


def settings() -> dict[str, str]:
    return read_environment(NAMES)


def readiness(values: dict[str, str]) -> dict[str, bool]:
    return {
        "enabled": values.get("NOTIFY_ENABLED", "").lower() == "true",
        "email": all(values.get(k) for k in EMAIL_FIELDS),
        "discord": bool(values.get("DISCORD_WEBHOOK_URL")),
    }


def send_email(
    values: dict[str, str], subject: str, text: str, archive: bytes | None
) -> str | None:
    if not all(values.get(k) for k in EMAIL_FIELDS):
        raise NotificationConfigError("Email settings are incomplete.")
    port = int(values.get("SMTP_PORT", "587"))
    if port not in (465, 587):
        raise NotificationConfigError("SMTP must use TLS on port 465 or 587.")
    for key in ("SMTP_FROM", "SMTP_TO"):
        if not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", values[key]):
            raise NotificationConfigError(
                "Use a plain sender and recipient email address."
            )
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = values["SMTP_FROM"]
    message["To"] = values["SMTP_TO"]
    message.set_content(text)
    if archive is not None:
        message.add_attachment(
            archive,
            maintype="application",
            subtype="zip",
            filename="SAMPLE-approved.zip",
        )
    context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(
            values["SMTP_HOST"], port, timeout=20, context=context
        ) as client:
            client.login(values["SMTP_USERNAME"], values["SMTP_PASSWORD"])
            refused = client.send_message(message)
    else:
        with smtplib.SMTP(values["SMTP_HOST"], port, timeout=20) as client:
            client.ehlo()
            client.starttls(context=context)
            client.ehlo()
            client.login(values["SMTP_USERNAME"], values["SMTP_PASSWORD"])
            refused = client.send_message(message)
    if refused:
        raise smtplib.SMTPRecipientsRefused(refused)
    return None


def send_discord(
    values: dict[str, str], subject: str, text: str, archive: bytes | None
) -> str:
    parsed = urllib.parse.urlsplit(values.get("DISCORD_WEBHOOK_URL", ""))
    if (
        parsed.scheme != "https"
        or parsed.netloc != "discord.com"
        or not re.fullmatch(r"/api/webhooks/[0-9]+/[A-Za-z0-9_-]+", parsed.path)
    ):
        raise NotificationConfigError("Use an official HTTPS Discord webhook URL.")
    url = urllib.parse.urlunsplit(
        ("https", "discord.com", parsed.path, "wait=true", "")
    )
    payload = json.dumps(
        {"content": subject + "\n" + text, "allowed_mentions": {"parse": []}}
    ).encode()
    if len(payload) > 1900:
        raise NotificationConfigError("Notification message is too long.")
    headers = {"Content-Type": "application/json", "User-Agent": "adsreport/0.1"}
    body = payload
    if archive is not None:
        boundary = "adsreport-" + uuid.uuid4().hex
        body = (
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="payload_json"'
                "\r\nContent-Type: application/json\r\n\r\n"
            ).encode()
            + payload
            + (
                f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="files[0]"; '
                'filename="SAMPLE-approved.zip"\r\n'
                "Content-Type: application/zip\r\n\r\n"
            ).encode()
            + archive
            + f"\r\n--{boundary}--\r\n".encode()
        )
        headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.build_opener(NoRedirect()).open(
        request, timeout=20
    ) as response:
        result = json.loads(response.read(100_000))
    identifier = result.get("id") if isinstance(result, dict) else None
    if not isinstance(identifier, str) or not identifier.isdigit():
        raise RuntimeError("Provider acknowledgement could not be verified.")
    return identifier


def save_receipt(path: Path, receipt: dict[str, object]) -> None:
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def notify(
    subject: str,
    text: str,
    archive: bytes | None,
    receipt_path: Path,
    *,
    retry_uncertain: bool = False,
) -> dict[str, str]:
    values = settings()
    ready = readiness(values)
    if archive is not None and len(archive) > 8_000_000:
        raise ValueError("Approved archive exceeds the notification size limit.")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt = (
        json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt_path.exists()
        else {}
    )
    states = {}
    for channel, sender in (("email", send_email), ("discord", send_discord)):
        previous = receipt.get(channel, {})
        state = previous.get("state")
        if state == "accepted":
            states[channel] = "accepted"
            continue
        if state in {"sending", "uncertain"} and not retry_uncertain:
            states[channel] = "uncertain"
            continue
        if not ready["enabled"]:
            states[channel] = "disabled"
            continue
        if not ready[channel]:
            states[channel] = "not_configured"
            continue
        receipt[channel] = {
            "state": "sending",
            "attempted_at": datetime.now(UTC).isoformat(),
        }
        save_receipt(receipt_path, receipt)
        outcome: dict[str, object]
        try:
            identifier = sender(values, subject, text, archive)
            outcome = {
                "state": "accepted",
                "provider_id": identifier,
                "acknowledged_at": datetime.now(UTC).isoformat(),
            }
        except (NotificationConfigError, smtplib.SMTPRecipientsRefused) as exc:
            outcome = {"state": "failed", "error_type": type(exc).__name__}
        except smtplib.SMTPResponseException as exc:
            # Authentication or DATA rejection is safe to retry. A failed QUIT
            # can follow accepted DATA, so other SMTP responses stay uncertain.
            safe = isinstance(
                exc,
                (
                    smtplib.SMTPAuthenticationError,
                    smtplib.SMTPDataError,
                    smtplib.SMTPSenderRefused,
                ),
            )
            outcome = {
                "state": "failed" if safe else "uncertain",
                "error_type": type(exc).__name__,
                "status_code": exc.smtp_code,
            }
        except urllib.error.HTTPError as exc:
            outcome = {
                "state": "failed" if exc.code < 500 else "uncertain",
                "error_type": "HTTPError",
                "status_code": exc.code,
            }
        except Exception as exc:
            # A transport interruption can happen after external acceptance.
            outcome = {"state": "uncertain", "error_type": type(exc).__name__}
        receipt[channel] = outcome
        save_receipt(receipt_path, receipt)
        states[channel] = str(outcome["state"])
    return states
