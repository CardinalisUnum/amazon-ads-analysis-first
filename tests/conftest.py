"""Unit/integration calls never write public history or send real notifications."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def isolate_module_setup(tmp_path_factory: pytest.TempPathFactory):
    # Module-scoped rendering fixtures run before function-scoped fixtures.
    # Their CLI calls must also stay out of real history and notification paths.
    folder = tmp_path_factory.mktemp("module-operations")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("ADSREPORT_RUN_LOG", str(folder / "run-log.jsonl"))
        patch.setenv("ADSREPORT_OUTBOX", str(folder / "outbox"))
        patch.setenv("NOTIFY_ENABLED", "false")
        patch.delenv("GITHUB_ACTIONS", raising=False)
        yield


@pytest.fixture(autouse=True)
def isolate_operations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADSREPORT_RUN_LOG", str(tmp_path / "run-log.jsonl"))
    monkeypatch.setenv("ADSREPORT_OUTBOX", str(tmp_path / "outbox"))
    monkeypatch.setenv("NOTIFY_ENABLED", "false")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
