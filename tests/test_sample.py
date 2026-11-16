import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest
import yaml

from adsreport.cli import main
from adsreport.sample import generate_sample


def read_csv(folder: Path, name: str) -> list[dict[str, str]]:
    return list(
        csv.DictReader(io.StringIO((folder / name).read_text(encoding="utf-8")))
    )


def bundle(folder: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in folder.iterdir()}


def weekly_facts(folder: Path) -> dict[str, list[dict[str, Decimal]]]:
    """Recalculate scenario evidence independently from the exported rows."""
    costs = {row["asin"]: row for row in read_csv(folder, "SAMPLE_costs.csv")}
    inventory = {
        (row["asin"], row["week"]): row
        for row in read_csv(folder, "SAMPLE_inventory.csv")
    }
    ads: dict[tuple[str, str], dict[str, Decimal]] = defaultdict(
        lambda: defaultdict(Decimal)
    )
    for row in read_csv(folder, "SAMPLE_ads.csv"):
        day = date.fromisoformat(row["Date"])
        week = (day - timedelta(days=day.weekday())).isoformat()
        total = ads[row["Advertised ASIN"], week]
        for metric, column in {
            "spend": "Spend",
            "ad_sales": "7 Day Total Sales",
            "clicks": "Clicks",
            "impressions": "Impressions",
            "purchases": "7 Day Total Orders (#)",
        }.items():
            total[metric] += Decimal(row[column])
    result: dict[str, list[dict[str, Decimal]]] = defaultdict(list)
    for row in read_csv(folder, "SAMPLE_total_sales.csv"):
        asin, week = row["asin"], row["week"]
        cost = costs[asin]
        fact = dict(ads[asin, week])
        units = Decimal(row["units"])
        fact["units"] = units
        result[asin].append(fact)
        if units == 0:
            continue
        gross = Decimal(row["gross_sales"])
        net = gross / Decimal("1.19")
        referral = max(
            Decimal("0.30"),
            (gross / units * Decimal("0.15")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        )
        variable_cost = units * (
            Decimal(cost["unit_product_cost"])
            + referral
            + Decimal(cost["fba_fee_per_unit"])
            + Decimal(cost["logistics_storage_per_unit"])
            + Decimal(cost["return_rate"]) * Decimal(cost["loss_per_return"])
        )
        fact["net"] = net
        fact["break_even"] = (net - variable_cost) / net * 100
        fact["after_ads"] = net - variable_cost - fact["spend"]
        fact["acos"] = fact["spend"] / fact["ad_sales"] * 100
        fact["cvr"] = fact["purchases"] / fact["clicks"]
        fact["organic"] = 1 - fact["ad_sales"] / net
        history = result[asin][-4:]
        daily_units = sum(r["units"] for r in history) / (len(history) * 7)
        fact["coverage"] = (
            Decimal(inventory[asin, week]["units_available"]) / daily_units
        )
    return result


@pytest.mark.parametrize("seed", [0, 42, 2026])
def test_reproducible_sample_and_business_stories(tmp_path: Path, seed: int) -> None:
    first, second = tmp_path / "first", tmp_path / "second"
    generate_sample(first, seed, Decimal("0.19"))
    generate_sample(second, seed, Decimal("0.19"))
    assert bundle(first) == bundle(second)
    assert generate_sample(first, seed, Decimal("0.19")) == first
    manifest = json.loads((first / "manifest.json").read_text())
    assert manifest["products"] == 10 and manifest["weeks"] == 8
    for name, checksum in manifest["files"].items():
        assert hashlib.sha256((first / name).read_bytes()).hexdigest() == checksum
    assert len(read_csv(first, "SAMPLE_ads.csv")) == 1120
    assert len(read_csv(first, "SAMPLE_total_sales.csv")) == 80
    assert len(read_csv(first, "SAMPLE_inventory.csv")) == 80
    assert len(read_csv(first, "SAMPLE_costs.csv")) == 10
    for name, content in bundle(first).items():
        assert "SAMPLE" in name or b"SAMPLE DATA" in content
    catalog = read_csv(first, "SAMPLE_catalog.csv")
    assert len({p["set_number"] for p in catalog}) == 10
    assert all(
        p["source_url"].startswith("https://www.lego.com/en-de/product/")
        for p in catalog
    )
    assert all(
        p["asin"].startswith("SAMPLE") and p["asin"] != p["set_number"] for p in catalog
    )
    expected = yaml.safe_load((first / "expected_flags.yaml").read_text())
    costs = {r["asin"]: r for r in read_csv(first, "SAMPLE_costs.csv")}
    found_rules: set[str] = set()
    facts = weekly_facts(first)
    for asin, history in facts.items():
        current, prior = history[-1], history[-2]
        phase = costs[asin]["lifecycle_phase"]
        expired = date(2026, 11, 1) - date.fromisoformat(
            costs[asin]["launch_start_date"]
        )
        checks = [
            (
                "R1",
                phase in {"growth", "maturity"}
                and current["acos"] > current["break_even"],
            ),
            (
                "R2",
                phase == "launch"
                and expired.days > 56
                and current["acos"] > current["break_even"],
            ),
            (
                "R3",
                prior["acos"] - current["acos"] >= 5
                and current["net"] <= prior["net"] * Decimal("0.9")
                and current["impressions"] <= prior["impressions"] * Decimal("0.9"),
            ),
            (
                "R4",
                current["spend"] >= prior["spend"] * Decimal("1.1")
                and current["coverage"] < 14,
            ),
            (
                "R5",
                current["cvr"] <= prior["cvr"] * Decimal("0.8")
                and Decimal("0.9")
                <= current["clicks"] / prior["clicks"]
                <= Decimal("1.1"),
            ),
            (
                "R6",
                current["spend"] >= prior["spend"] * Decimal("1.3")
                and current["ad_sales"] <= prior["ad_sales"] * Decimal("1.05"),
            ),
            ("R7", current["after_ads"] < 0),
            (
                "R8",
                all(
                    a["organic"] > b["organic"]
                    for a, b in zip(history[-4:-1], history[-3:], strict=True)
                ),
            ),
            (
                "R9",
                phase == "maturity"
                and current["acos"] > current["break_even"] * Decimal("0.8"),
            ),
        ]
        found = {rule for rule, condition in checks if condition}
        assert found == set(expected["products"][asin]), (asin, found)
        found_rules.update(found)
    assert found_rules == {f"R{n}" for n in range(1, 10)}


def test_rows_are_consistent_and_prelaunch_activity_is_zero(tmp_path: Path) -> None:
    generate_sample(tmp_path / "sample", 42, Decimal("0.19"))
    folder = tmp_path / "sample"
    for row in read_csv(folder, "SAMPLE_ads.csv"):
        assert (
            int(row["Impressions"])
            >= int(row["Clicks"])
            >= int(row["7 Day Total Orders (#)"])
        )
        assert Decimal(row["7 Day Total Sales"]) == Decimal(
            row["7 Day Advertised SKU Sales"]
        )
        if row["Advertised ASIN"] == "SAMPLE0003" and row["Date"] < "2026-10-05":
            assert row["Spend"] == "0.00" and row["Clicks"] == "0"
    assert bundle(folder) == bundle(Path("data/sample"))


def test_different_seed_changes_data_and_preserves_existing_output(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "sample"
    generate_sample(folder, 42, Decimal("0.19"))
    original = bundle(folder)
    with pytest.raises(FileExistsError):
        generate_sample(folder, 43, Decimal("0.19"))
    assert bundle(folder) == original
    other = tmp_path / "other"
    generate_sample(other, 43, Decimal("0.19"))
    assert bundle(other)["SAMPLE_ads.csv"] != original["SAMPLE_ads.csv"]


def test_write_failure_does_not_publish_partial_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = Path.write_bytes

    def fail_on_costs(path: Path, data: bytes) -> int:
        if path.name == "SAMPLE_costs.csv":
            raise OSError("Injected disk write failure")
        return original(path, data)

    monkeypatch.setattr(Path, "write_bytes", fail_on_costs)
    with pytest.raises(OSError, match="Injected"):
        generate_sample(tmp_path / "sample", 42, Decimal("0.19"))
    assert list(tmp_path.iterdir()) == []


def test_cli_generates_sample_and_reports_existing_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder = tmp_path / "sample"
    assert main(["generate-sample", "--out", str(folder), "--seed", "42"]) == 0
    assert "SAMPLE DATA ready" in capsys.readouterr().out
    assert main(["generate-sample", "--out", str(folder), "--seed", "43"]) == 2
    assert "different content" in capsys.readouterr().err


@pytest.mark.parametrize("rate", ["NaN", "-0.01", "Infinity", "1.1", "0.20"])
def test_invalid_vat_cannot_generate_output(tmp_path: Path, rate: str) -> None:
    with pytest.raises(ValueError, match="VAT"):
        generate_sample(tmp_path / "sample", 42, Decimal(rate))
    assert list(tmp_path.iterdir()) == []
