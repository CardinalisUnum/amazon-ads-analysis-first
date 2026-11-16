import json
from pathlib import Path

import pytest

from adsreport.cli import main


def test_numerical_cli_matches_committed_snapshot(tmp_path: Path) -> None:
    output = tmp_path / "draft"
    args = ["run", "--input", "data/sample", "--out", str(output), "--no-ai"]
    assert main(args) == 0
    assert main(args) == 0
    assert (output / "SAMPLE_kpis.csv").read_bytes() == Path(
        "tests/golden/SAMPLE_kpis.csv"
    ).read_bytes()
    report = json.loads((output / "report.json").read_text())
    assert report["status"] == "DRAFT" and report["data_label"] == "SAMPLE DATA"
    assert len(report["products"]) == 80
    assert report["stage"] == "rules"
    assert len(report["analysis"]["flags"]) == 10
    assert len(report["analysis"]["priorities"]) == 6
    assert report["analysis"]["report_week"] == report["report_week"]


def test_report_failure_is_visible_and_publishes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "draft"
    assert (
        main(
            [
                "run",
                "--input",
                str(tmp_path / "missing"),
                "--out",
                str(output),
                "--no-ai",
            ]
        )
        == 2
    )
    assert not output.exists()
    assert "input/output error" in capsys.readouterr().err


def test_ai_path_remains_pending(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["run"]) == 2
    assert "--no-ai" in capsys.readouterr().err
