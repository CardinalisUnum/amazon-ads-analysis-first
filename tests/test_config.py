from pathlib import Path

import pytest
import yaml

from adsreport.cli import main
from adsreport.config import ConfigError, load_config


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    for name in ("settings.yaml", "thresholds.yaml"):
        (tmp_path / name).write_bytes((Path("config") / name).read_bytes())
    return tmp_path


def test_committed_configuration() -> None:
    config = load_config(Path("config"))
    assert config.settings.currency == "EUR"
    assert config.thresholds.organic_decline_transitions == 3


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("vat_rate", -0.19),
        ("vat_rate", float("nan")),
        ("marketplace", "amazon.com"),
        ("attribution_days", "7"),
        ("sample_label", "LIVE DATA"),
        ("unexpected", True),
        ("output_formats", ["xlsx", "xlsx", "pdf", "pptx"]),
    ],
)
def test_invalid_settings_fail(config_dir: Path, field: str, value: object) -> None:
    path = config_dir / "settings.yaml"
    settings = yaml.safe_load(path.read_text())
    settings[field] = value
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(config_dir)


@pytest.mark.parametrize(
    "content", ["[unclosed", "[]", "null", "!!python/object:bad {}"]
)
def test_invalid_yaml_fails(config_dir: Path, content: str) -> None:
    (config_dir / "settings.yaml").write_text(content, encoding="utf-8")
    with pytest.raises(ConfigError, match="settings.yaml"):
        load_config(config_dir)


def test_missing_file_fails(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="settings.yaml"):
        load_config(tmp_path)


def test_invalid_threshold_fails(config_dir: Path) -> None:
    path = config_dir / "thresholds.yaml"
    thresholds = yaml.safe_load(path.read_text())
    thresholds["launch_window_weeks"] = 0
    path.write_text(yaml.safe_dump(thresholds), encoding="utf-8")
    with pytest.raises(ConfigError, match="launch_window_weeks"):
        load_config(config_dir)


def test_cli_reports_invalid_config(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--config", str(tmp_path), "--check-config"]) == 2
    assert "settings.yaml" in capsys.readouterr().err


def test_cli_validates_config(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--check-config"]) == 0
    assert "Configuration valid" in capsys.readouterr().out


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "generate-sample" in capsys.readouterr().out


@pytest.mark.parametrize(
    "args",
    [
        ["approve", "--report", "draft.json"],
        ["deliver", "--report", "draft.json"],
    ],
)
def test_review_commands_require_an_explicit_frozen_version(
    args: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(args) == 2
    assert "expect-manifest" in capsys.readouterr().err
