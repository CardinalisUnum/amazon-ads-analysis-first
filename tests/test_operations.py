"""Operational contracts: exact-version review, interrupted sends and genuine logs."""

import hashlib
import importlib.util
import io
import json
import smtplib
import urllib.error
import zipfile
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from adsreport import notifications, operations
from adsreport.approval import approve_report, freeze
from adsreport.cli import main
from adsreport.delivery import deliver_report
from adsreport.github_review import github_reviewer
from adsreport.periods import latest_mature_week
from adsreport.runlog import (
    append_event,
    event_now,
    exclusive_lock,
    new_run,
    read_events,
    scheduled_rate,
)


@pytest.fixture(scope="module")
def draft():
    # Reviewed P6 snapshot; no new AI, financial or rendering work during loading.
    return freeze(Path("docs/examples"))


@pytest.fixture(scope="module")
def approved(tmp_path_factory, draft):
    destination = tmp_path_factory.mktemp("approved") / "bundle"
    return approve_report(
        Path("docs/examples"),
        destination,
        draft.manifest_sha256,
        "Test Reviewer",
        mechanism="test",
    ), destination


def copy_bundle(bundle, folder):
    folder.mkdir()
    for name, data in bundle.files.items():
        (folder / name).write_bytes(data)
    return folder


def test_approval_preserves_frozen_facts_and_draft(draft, approved):
    result, path = approved
    assert result.manifest_sha256 != draft.manifest_sha256
    assert result.document.approval.mechanism == "test"
    assert result.document.approval.approved_at.utcoffset() is not None
    for field in (
        "products",
        "presentation",
        "analysis",
        "commentary",
        "source_hashes",
    ):
        assert getattr(result.document, field) == getattr(draft.document, field)
    assert freeze(Path("docs/examples")).files == draft.files
    assert (
        result.files["SAMPLE_kpis.csv"].replace(b"APPROVED", b"DRAFT")
        == (draft.files["SAMPLE_kpis.csv"])
    )
    assert len(result.files) == 14
    assert b"APPROVED" in result.files["SAMPLE_report.html"]
    assert (
        approve_report(
            Path("docs/examples"),
            path,
            draft.manifest_sha256,
            "Test Reviewer",
            mechanism="test",
        ).files
        == result.files
    )
    with pytest.raises(ValueError, match="another review"):
        approve_report(Path("docs/examples"), path, draft.manifest_sha256, "Other")


def test_approval_never_recalculates_or_calls_ai(tmp_path, draft, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Approval attempted to regenerate facts or AI")

    for module, name in (
        ("adsreport.pipeline", "generate_commentary"),
        ("adsreport.pipeline", "calculate_report"),
        ("adsreport.pipeline", "evaluate_rules"),
        ("adsreport.render.model", "summarize"),
    ):
        monkeypatch.setattr(module + "." + name, forbidden)
    approve_report(
        Path("docs/examples"),
        tmp_path / "approved",
        draft.manifest_sha256,
        "Test",
        mechanism="test",
    )


@pytest.mark.parametrize("mutation", ["tamper", "extra", "missing", "manifest"])
def test_freeze_refuses_changed_bundle(tmp_path, draft, mutation):
    folder = copy_bundle(draft, tmp_path / "copy")
    if mutation == "tamper":
        (folder / "SAMPLE_report.html").write_bytes(b"changed")
    elif mutation == "extra":
        (folder / "unexpected").write_bytes(b"extra")
    elif mutation == "missing":
        (folder / "SAMPLE_report.pdf").unlink()
    else:
        (folder / "artifacts.json").write_bytes(b"{}")
    with pytest.raises(ValueError):
        freeze(folder, draft.manifest_sha256)


def test_approval_requires_draft_and_new_destination(tmp_path, draft, approved):
    with pytest.raises(ValueError, match="preserve"):
        approve_report(
            Path("docs/examples"), Path("docs/examples"), draft.manifest_sha256, "Test"
        )
    result, path = approved
    with pytest.raises(ValueError, match="Only a DRAFT"):
        approve_report(path, tmp_path / "second", result.manifest_sha256, "Test")


def test_delivery_blocks_draft_test_and_stale_versions(tmp_path, draft, approved):
    result, path = approved
    for folder, digest, reason in (
        (Path("docs/examples"), draft.manifest_sha256, "Only an approved"),
        (path, result.manifest_sha256, "Test approvals"),
        (path, "0" * 64, "Manifest changed"),
    ):
        with pytest.raises(ValueError, match=reason):
            deliver_report(folder, digest, tmp_path / "outbox")


def test_delivery_archive_matches_approved_bytes(tmp_path, approved, monkeypatch):
    bundle, path = approved
    outbox = tmp_path / "outbox"
    sender = MagicMock(return_value={"email": "accepted", "discord": "accepted"})
    monkeypatch.setattr("adsreport.delivery.notify", sender)
    for _ in range(2):
        assert deliver_report(path, bundle.manifest_sha256, outbox, test_mode=True) == {
            "email": "accepted",
            "discord": "accepted",
        }
    archive = (outbox / bundle.manifest_sha256 / "SAMPLE-approved.zip").read_bytes()
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        assert {name: zipped.read(name) for name in zipped.namelist()} == bundle.files
    assert freeze(path).files == bundle.files
    assert sender.call_args.args[2] == archive


def configured(monkeypatch):
    monkeypatch.setattr(
        notifications,
        "settings",
        lambda: {
            "NOTIFY_ENABLED": "true",
            "SMTP_HOST": "smtp.example.test",
            "SMTP_USERNAME": "name",
            "SMTP_PASSWORD": "private-placeholder",
            "SMTP_FROM": "from@example.test",
            "SMTP_TO": "to@example.test",
            "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/1/test-token",
        },
    )


def test_partial_delivery_retry_skips_accepted_channel(tmp_path, monkeypatch):
    configured(monkeypatch)
    email = MagicMock(return_value=None)
    discord = MagicMock(
        side_effect=[urllib.error.HTTPError("redacted", 429, "rate", {}, None), "123"]
    )
    monkeypatch.setattr(notifications, "send_email", email)
    monkeypatch.setattr(notifications, "send_discord", discord)
    receipt = tmp_path / "receipt.json"
    assert notifications.notify("sample", "body", b"zip", receipt) == {
        "email": "accepted",
        "discord": "failed",
    }
    assert notifications.notify("sample", "body", b"zip", receipt) == {
        "email": "accepted",
        "discord": "accepted",
    }
    assert email.call_count == 1
    assert discord.call_count == 2
    assert "private-placeholder" not in receipt.read_text(encoding="utf-8")


@pytest.mark.parametrize("prior", ["sending", "uncertain"])
def test_uncertain_send_requires_explicit_retry(tmp_path, monkeypatch, prior):
    configured(monkeypatch)
    email = MagicMock(return_value=None)
    discord = MagicMock(side_effect=TimeoutError("private URL must not be logged"))
    monkeypatch.setattr(notifications, "send_email", email)
    monkeypatch.setattr(notifications, "send_discord", discord)
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps({"email": {"state": prior}}), encoding="utf-8")
    assert notifications.notify("s", "b", None, receipt) == {
        "email": "uncertain",
        "discord": "uncertain",
    }
    notifications.notify("s", "b", None, receipt)
    assert discord.call_count == 1
    assert email.call_count == 0
    notifications.notify("s", "b", None, receipt, retry_uncertain=True)
    assert email.call_count == 1
    assert discord.call_count == 2
    assert "private URL" not in receipt.read_text(encoding="utf-8")


def test_disabled_and_missing_destinations_do_not_send(tmp_path, monkeypatch):
    sender = MagicMock(side_effect=AssertionError("Network called"))
    monkeypatch.setattr(notifications, "send_email", sender)
    monkeypatch.setattr(notifications, "send_discord", sender)
    monkeypatch.setattr(notifications, "settings", lambda: {})
    assert set(notifications.notify("s", "b", None, tmp_path / "r").values()) == {
        "disabled"
    }
    monkeypatch.setattr(notifications, "settings", lambda: {"NOTIFY_ENABLED": "true"})
    assert set(notifications.notify("s", "b", None, tmp_path / "r").values()) == {
        "not_configured"
    }


def test_smtp_quit_failure_after_possible_acceptance_stays_uncertain(
    tmp_path, monkeypatch
):
    configured(monkeypatch)
    monkeypatch.setattr(
        notifications,
        "send_email",
        MagicMock(side_effect=smtplib.SMTPResponseException(500, b"QUIT failed")),
    )
    monkeypatch.setattr(notifications, "send_discord", MagicMock(return_value="123"))
    assert notifications.notify("s", "b", None, tmp_path / "r") == {
        "email": "uncertain",
        "discord": "accepted",
    }


def test_repeated_approval_records_one_event(approved, draft, monkeypatch):
    result, folder = approved
    monkeypatch.setattr(operations, "approve_report", MagicMock(return_value=result))
    for _ in range(2):
        operations.execute_approval(
            Path("docs/examples"), folder, draft.manifest_sha256, "Test Reviewer"
        )
    assert len(read_events(operations.log_path())) == 1


@pytest.mark.parametrize("port", [465, 587])
def test_smtp_requires_encrypted_transport(monkeypatch, port):
    configured(monkeypatch)
    client = MagicMock()
    client.__enter__.return_value = client
    client.send_message.return_value = {}
    ssl_client, plain = MagicMock(return_value=client), MagicMock(return_value=client)
    monkeypatch.setattr(smtplib, "SMTP_SSL", ssl_client)
    monkeypatch.setattr(smtplib, "SMTP", plain)
    values = notifications.settings() | {"SMTP_PORT": str(port)}
    notifications.send_email(values, "SAMPLE", "body", b"archive")
    assert ssl_client.call_count == (port == 465)
    assert plain.call_count == (port == 587)
    assert client.starttls.call_count == (port == 587)
    assert client.send_message.call_args.args[0].is_multipart()
    client.send_message.return_value = {"to@example.test": (550, b"refused")}
    with pytest.raises(smtplib.SMTPRecipientsRefused):
        notifications.send_email(values, "SAMPLE", "body", None)
    with pytest.raises(ValueError):
        notifications.send_email(values | {"SMTP_PORT": "25"}, "s", "b", None)
    with pytest.raises(notifications.NotificationConfigError):
        notifications.send_email(values | {"SMTP_PORT": "invalid"}, "s", "b", None)
    client.send_message.return_value = {}
    notifications.send_email(values | {"SMTP_PORT": ""}, "s", "b", None)


def test_discord_waits_for_ack_and_blocks_mentions_redirects(monkeypatch):
    configured(monkeypatch)
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = b'{"id":"12345"}'
    opener = MagicMock()
    opener.open.return_value = response
    factory = MagicMock(return_value=opener)
    monkeypatch.setattr(notifications.urllib.request, "build_opener", factory)
    assert (
        notifications.send_discord(
            notifications.settings(), "sample", "body", b"archive"
        )
        == "12345"
    )
    request = opener.open.call_args.args[0]
    assert request.full_url.endswith("?wait=true")
    assert b'"allowed_mentions": {"parse": []}' in request.data
    assert b"application/zip" in request.data
    assert isinstance(factory.call_args.args[0], notifications.NoRedirect)
    for url in ("http://discord.com/api/webhooks/1/a", "https://evil.test/token"):
        with pytest.raises(ValueError):
            notifications.send_discord({"DISCORD_WEBHOOK_URL": url}, "s", "b", None)


def test_log_is_append_only_and_incomplete_runs_count(tmp_path):
    path = tmp_path / "events.jsonl"
    identity = new_run().model_copy(update={"trigger": "schedule"})
    start = event_now(identity, "run_started", "in_progress", 0)
    append_event(path, start)
    append_event(path, start)
    assert len(read_events(path)) == 1
    assert scheduled_rate(read_events(path)) == {
        "successful": 0,
        "scheduled": 1,
        "incomplete": 1,
        "percent": 0,
    }
    with pytest.raises(ValueError, match="rewritten"):
        append_event(path, start.model_copy(update={"status": "failure"}))
    append_event(path, event_now(identity, "run", "success", 0))
    append_event(path, event_now(new_run(test_failure=True), "run", "failure", 0))
    assert scheduled_rate(read_events(path))["percent"] == 100
    with exclusive_lock(path.with_suffix(".lock")), pytest.raises(ValueError):
        append_event(path, start)


def test_failure_is_labelled_and_alert_errors_do_not_hide_cause(monkeypatch):
    monkeypatch.setattr(operations, "notify", MagicMock(side_effect=OSError("private")))
    with pytest.raises(ValueError, match="Injected"):
        operations.execute_run(
            Path("data/sample"), None, Path("config"), no_ai=True, inject_failure=True
        )
    records = read_events(operations.log_path())
    assert [e.event for e in records] == ["run_started", "run"]
    assert records[-1].run.trigger == "test_failure"
    assert records[-1].failed_step == "injected_failure"
    assert records[-1].notifications["email"] == "alert_error"
    assert scheduled_rate(records)["scheduled"] == 0


def test_github_review_requires_real_owner_environment_review(monkeypatch):
    with pytest.raises(ValueError, match="context"):
        github_reviewer()
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_RUN_ID": "123",
        "GITHUB_REPOSITORY": "CardinalisUnum/amazon-ads-analysis-first",
    }.items():
        monkeypatch.setenv(key, value)
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = json.dumps(
        [
            {
                "state": "approved",
                "user": {"login": "CardinalisUnum"},
                "environments": [{"name": "client-delivery"}],
            }
        ]
    ).encode()
    monkeypatch.setattr(
        "adsreport.github_review.urllib.request.urlopen",
        MagicMock(return_value=response),
    )
    assert github_reviewer() == "CardinalisUnum"
    response.read.return_value = b"[]"
    with pytest.raises(ValueError, match="not recorded"):
        github_reviewer()
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    with pytest.raises(ValueError, match="context"):
        github_reviewer()


def test_maturity_waits_full_intervals_and_handles_dst():
    assert latest_mature_week(datetime(2026, 11, 16, 1, 17, tzinfo=UTC), 7, 1) == (
        date(2026, 10, 26)
    )
    assert latest_mature_week(datetime(2026, 11, 16, 23, tzinfo=UTC), 7, 1) == (
        date(2026, 11, 2)
    )
    assert latest_mature_week(datetime(2026, 10, 27, 0, tzinfo=UTC), 7, 1) == (
        date(2026, 10, 12)
    )
    with pytest.raises(ValueError):
        latest_mature_week(datetime(2026, 11, 16), 7, 1)
    with pytest.raises(ValueError):
        latest_mature_week(datetime.now(UTC), -1, 1)


def test_doctor_and_history_are_offline(capsys):
    assert main(["doctor"]) == 0
    assert json.loads(capsys.readouterr().out)["local_reporting_ready"]
    assert main(["history"]) == 0
    assert json.loads(capsys.readouterr().out)["scheduled_rate"]["percent"] is None


def test_cli_delivery_cannot_treat_disabled_as_complete(approved, monkeypatch, capsys):
    bundle, folder = approved
    # Adapter behavior is exercised here without claiming an owner approval or receipt.
    monkeypatch.setattr(
        operations,
        "deliver_report",
        MagicMock(return_value={"email": "disabled", "discord": "disabled"}),
    )
    assert (
        main(
            [
                "deliver",
                "--report",
                str(folder),
                "--expect-manifest",
                bundle.manifest_sha256,
            ]
        )
        == 3
    )
    assert json.loads(capsys.readouterr().out)["human_receipt_verified"] is False


def test_wrong_manifest_is_not_an_approval(tmp_path, draft):
    with pytest.raises(ValueError, match="Manifest changed"):
        approve_report(Path("docs/examples"), tmp_path / "copy", "0" * 64, "Test")
    assert hashlib.sha256(draft.files["artifacts.json"]).hexdigest() == (
        draft.manifest_sha256
    )


def test_history_merge_preserves_existing_bytes_and_rejects_conflicts():
    spec = importlib.util.spec_from_file_location(
        "persist", "scripts/persist_run_log.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    event = event_now(new_run(), "run", "success", 0)
    original = (event.model_dump_json(indent=0).replace("\n", "") + "\n").encode()
    assert module.merge_events(original, [event]) == original
    newer = event_now(new_run(), "run_started", "in_progress", 0)
    assert module.merge_events(original, [event, newer]).startswith(original)
    with pytest.raises(ValueError, match="conflict"):
        module.merge_events(original, [event.model_copy(update={"status": "failure"})])
