"""Unit/integration calls never write public history or send real notifications."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_operations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADSREPORT_RUN_LOG", str(tmp_path / "run-log.jsonl"))
    monkeypatch.setenv("ADSREPORT_OUTBOX", str(tmp_path / "outbox"))
    monkeypatch.setenv("NOTIFY_ENABLED", "false")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
