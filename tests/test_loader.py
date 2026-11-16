import csv
import json
import shutil
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

import pytest

from adsreport.io.loader import InputError, load_inputs

COLUMN_MAP = Path("config/column_map.yaml")


@pytest.fixture
def inputs(tmp_path: Path) -> Path:
    folder = tmp_path / "input"
    shutil.copytree("data/sample", folder)
    manifest = json.loads((folder / "manifest.json").read_text())
    # These mutation tests model an unhashed external export adapter.
    manifest["files"] = {}
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return folder


def edit_csv(
    folder: Path, kind: str, change: Callable[[list[dict[str, str]]], None]
) -> None:
    path = folder / f"SAMPLE_{kind}.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames
        rows = list(reader)
    change(rows)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else headers)
        writer.writeheader()
        writer.writerows(rows)


def test_two_campaigns_do_not_multiply_retail() -> None:
    loaded = load_inputs(Path("data/sample"), COLUMN_MAP)
    assert len(loaded.rows) == 80
    with Path("data/sample/SAMPLE_total_sales.csv").open() as stream:
        source_revenue = sum(Decimal(r["gross_sales"]) for r in csv.DictReader(stream))
    assert sum(r.retail.gross_sales for r in loaded.rows) == source_revenue
    assert len(loaded.source_hashes) == 5
    with Path("data/sample/SAMPLE_ads.csv").open() as stream:
        source_spend = sum(Decimal(r["Spend"]) for r in csv.DictReader(stream))
    assert sum(r.ads.spend for r in loaded.rows) == source_spend


def test_current_aliases_preserve_total_and_promoted_sales(inputs: Path) -> None:
    names = {
        "Spend": "Cost",
        "7 Day Total Sales": "Sales",
        "7 Day Advertised SKU Sales": "Sales (promoted)",
        "7 Day Other SKU Sales": "Sales (halo)",
        "7 Day Total Orders (#)": "Purchases",
        "7 Day Total Units (#)": "Units sold",
    }

    def rename(rows: list[dict[str, str]]) -> None:
        for row in rows:
            for old, new in names.items():
                row[new] = row.pop(old)

    edit_csv(inputs, "ads", rename)
    assert (
        load_inputs(inputs, COLUMN_MAP).rows
        == load_inputs(Path("data/sample"), COLUMN_MAP).rows
    )


@pytest.mark.parametrize("kind", ["ads", "costs", "total_sales", "inventory"])
def test_duplicate_grain_is_rejected(inputs: Path, kind: str) -> None:
    edit_csv(inputs, kind, lambda rows: rows.append(dict(rows[0])))
    with pytest.raises(InputError, match="Duplicate"):
        load_inputs(inputs, COLUMN_MAP)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("Clicks", "-1"),
        ("Clicks", "1.1"),
        ("Clicks", ""),
        ("Spend", "NaN"),
        ("Spend", "Infinity"),
        ("Spend", "-0.01"),
        ("Currency", "USD"),
        ("Date", "09/07/2026"),
    ],
)
def test_bad_ad_values_fail_clearly(inputs: Path, field: str, value: str) -> None:
    edit_csv(inputs, "ads", lambda rows: rows[0].update({field: value}))
    with pytest.raises(InputError, match="SAMPLE_ads.csv:2"):
        load_inputs(inputs, COLUMN_MAP)


def test_missing_header_fails(inputs: Path) -> None:
    def remove(rows: list[dict[str, str]]) -> None:
        for row in rows:
            row.pop("Spend")

    edit_csv(inputs, "ads", remove)
    with pytest.raises(InputError, match="missing required column spend"):
        load_inputs(inputs, COLUMN_MAP)


def test_conflicting_aliases_fail(inputs: Path) -> None:
    def aliases(rows: list[dict[str, str]]) -> None:
        for row in rows:
            row["Cost"] = row["Spend"]
        rows[0]["Cost"] = "999.00"

    edit_csv(inputs, "ads", aliases)
    with pytest.raises(InputError, match="conflicting aliases for spend"):
        load_inputs(inputs, COLUMN_MAP)


def test_empty_complete_ads_export_means_zero_activity(inputs: Path) -> None:
    edit_csv(inputs, "ads", lambda rows: rows.clear())
    loaded = load_inputs(inputs, COLUMN_MAP)
    assert len(loaded.rows) == 80
    assert all(r.ads.spend == 0 and r.ads.clicks == 0 for r in loaded.rows)


def test_missing_optional_promoted_sales_is_explicit(inputs: Path) -> None:
    def remove(rows: list[dict[str, str]]) -> None:
        for row in rows:
            row.pop("7 Day Advertised SKU Sales")

    edit_csv(inputs, "ads", remove)
    assert all(
        r.ads.promoted_sales is None for r in load_inputs(inputs, COLUMN_MAP).rows
    )


def test_hash_mismatch_and_path_escape_are_rejected(inputs: Path) -> None:
    path = inputs / "manifest.json"
    manifest = json.loads(path.read_text())
    for name, message in [
        ("SAMPLE_ads.csv", "SHA-256 mismatch"),
        ("../.env", "inside"),
    ]:
        manifest["files"] = {name: "0" * 64}
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(InputError, match=message):
            load_inputs(inputs, COLUMN_MAP)


@pytest.mark.parametrize("kind", ["costs", "inventory"])
def test_missing_related_record_is_rejected(inputs: Path, kind: str) -> None:
    edit_csv(inputs, kind, lambda rows: rows.pop(0))
    with pytest.raises(InputError, match="missing cost or inventory"):
        load_inputs(inputs, COLUMN_MAP)


def test_extra_column_values_are_rejected(inputs: Path) -> None:
    path = inputs / "SAMPLE_ads.csv"
    lines = path.read_text().splitlines()
    lines[1] += ",extra"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(InputError, match="field count"):
        load_inputs(inputs, COLUMN_MAP)


def test_missing_file_and_ambiguous_file_names_fail(inputs: Path) -> None:
    path = inputs / "SAMPLE_costs.csv"
    other = inputs / "costs.csv"
    shutil.copyfile(path, other)
    with pytest.raises(InputError, match="exactly one costs"):
        load_inputs(inputs, COLUMN_MAP)
    other.unlink()
    path.unlink()
    with pytest.raises(InputError, match="exactly one costs"):
        load_inputs(inputs, COLUMN_MAP)


def test_halo_is_kept_out_of_the_product_residual(inputs: Path) -> None:
    from adsreport.kpi.engine import calculate_report

    def add_halo(rows: list[dict[str, str]]) -> None:
        row = rows[0]
        promoted = Decimal(row["7 Day Advertised SKU Sales"])
        row["7 Day Advertised SKU Sales"] = str(promoted - 1)
        row["7 Day Other SKU Sales"] = "1.00"

    edit_csv(inputs, "ads", add_halo)
    baseline = calculate_report(
        load_inputs(Path("data/sample"), COLUMN_MAP).rows, Decimal("0.19")
    )[0]
    changed = calculate_report(load_inputs(inputs, COLUMN_MAP).rows, Decimal("0.19"))[0]
    assert baseline.values["acos_pct"] == changed.values["acos_pct"]
    assert (
        changed.values["organic_share_proxy_pct"]
        > baseline.values["organic_share_proxy_pct"]
    )


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("Advertised ASIN", "UNKNOWN", "no matching retail"),
        ("7 Day Advertised SKU Sales", "9999", "Promoted sales exceed"),
        ("7 Day Other SKU Sales", "9999", "do not reconcile"),
    ],
)
def test_unreconcilable_ads_fail(
    inputs: Path, column: str, value: str, message: str
) -> None:
    edit_csv(inputs, "ads", lambda rows: rows[0].update({column: value}))
    with pytest.raises(InputError, match=message):
        load_inputs(inputs, COLUMN_MAP)


def test_invalid_unit_costing_is_rejected(inputs: Path) -> None:
    edit_csv(inputs, "total_sales", lambda rows: rows[0].update({"units": "0"}))
    with pytest.raises(InputError, match="positive retail sales require units"):
        load_inputs(inputs, COLUMN_MAP)


def test_requested_report_week_requires_observations(inputs: Path) -> None:
    manifest = json.loads((inputs / "manifest.json").read_text())
    manifest["report_week"] = "2026-11-02"
    (inputs / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(InputError, match="report week has no retail"):
        load_inputs(inputs, COLUMN_MAP)


def test_duplicate_csv_headers_fail(inputs: Path) -> None:
    path = inputs / "SAMPLE_ads.csv"
    text = path.read_text()
    path.write_text(
        text.replace("Currency,Impressions", "Currency,Currency", 1), encoding="utf-8"
    )
    with pytest.raises(InputError, match="duplicate CSV headers"):
        load_inputs(inputs, COLUMN_MAP)
