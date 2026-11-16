from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from adsreport.io.loader import load_inputs
from adsreport.io.models import AdTotals, ProductWeek
from adsreport.kpi.engine import calculate_report, calculate_week, ratio


@pytest.fixture(scope="module")
def row() -> ProductWeek:
    return load_inputs(Path("data/sample"), Path("config/column_map.yaml")).rows[0]


def test_published_worked_example(row: ProductWeek) -> None:
    example = replace(
        row,
        retail=row.retail.model_copy(
            update={"gross_sales": Decimal("29.90"), "units": 1}
        ),
        cost=row.cost.model_copy(
            update={
                "unit_product_cost": Decimal("7.80"),
                "referral_fee_rate": Decimal("0.15"),
                "fba_fee_per_unit": Decimal("3.45"),
                "logistics_storage_per_unit": Decimal("0.40"),
                "return_rate": Decimal("0.04"),
                "loss_per_return": Decimal("13.75"),
            }
        ),
        ads=AdTotals(spend=Decimal("2.51"), ad_sales=Decimal("10.00")),
    )
    facts = calculate_week(example, Decimal("0.19"), [example]).values
    assert facts["net_revenue_eur"] == Decimal("25.13")
    assert facts["contribution_before_ads_eur"] == Decimal("8.44")
    assert facts["contribution_after_ads_eur"] == Decimal("5.93")
    assert facts["break_even_acos_pct"].quantize(Decimal("0.1")) == Decimal("33.6")
    assert facts["acos_pct"] == Decimal("25.1")


@pytest.mark.parametrize(
    ("spend", "sales", "acos", "roas"),
    [
        ("0", "0", None, None),
        ("10", "0", None, Decimal(0)),
        ("0", "10", Decimal(0), None),
        ("10", "20", Decimal(50), Decimal(2)),
    ],
)
def test_zero_ad_denominators(
    row: ProductWeek, spend: str, sales: str, acos: Decimal | None, roas: Decimal | None
) -> None:
    item = replace(row, ads=AdTotals(spend=Decimal(spend), ad_sales=Decimal(sales)))
    facts = calculate_week(item, Decimal("0.19"), [item])
    assert facts.values["acos_pct"] == acos
    assert facts.values["roas_ratio"] == roas
    assert all(v is None or v.is_finite() for v in facts.values.values())


def test_zero_retail_and_zero_demand_remain_undefined(row: ProductWeek) -> None:
    empty = replace(
        row,
        retail=row.retail.model_copy(
            update={"gross_sales": Decimal(0), "units": 0, "sessions": 0}
        ),
        ads=AdTotals(),
    )
    history = [
        replace(
            empty,
            retail=empty.retail.model_copy(
                update={"week": empty.retail.week + timedelta(weeks=i)}
            ),
        )
        for i in range(4)
    ]
    facts = calculate_week(history[-1], Decimal("0.19"), history)
    assert facts.values["stock_coverage_days"] is None
    assert facts.values["break_even_acos_pct"] is None
    assert facts.values["contribution_after_ads_eur"] == 0


def test_missing_week_does_not_create_a_zero_or_wow_change() -> None:
    loaded = load_inputs(Path("data/sample"), Path("config/column_map.yaml"))
    selected = [loaded.rows[i] for i in [0, 1, 3, 4]]
    results = calculate_report(selected, Decimal("0.19"))
    assert len(results) == 4
    assert results[2].values["ad_spend_eur_wow_pct"] is None
    assert results[-1].values["stock_coverage_days"] is None


@pytest.mark.parametrize("promoted", [None, Decimal("999999")])
def test_unusable_organic_proxy_has_reason(
    row: ProductWeek, promoted: Decimal | None
) -> None:
    item = replace(row, ads=replace(row.ads, promoted_sales=promoted))
    result = calculate_week(item, Decimal("0.19"), [item])
    assert result.values["organic_share_proxy_pct"] is None
    assert result.undefined_reasons["organic_share_proxy_pct"]


positive_money = st.decimals(
    min_value=Decimal("0.01"),
    max_value=Decimal("100000"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)


@settings(max_examples=200, derandomize=True, deadline=None)
@given(spend=positive_money, sales=positive_money)
def test_acos_roas_identity(spend: Decimal, sales: Decimal) -> None:
    acos, roas = ratio(spend, sales, Decimal(100)), ratio(sales, spend)
    assert acos is not None and roas is not None
    assert abs(acos * roas - 100) < Decimal("1e-20")


@settings(max_examples=200, derandomize=True, deadline=None)
@given(spend=positive_money)
def test_contribution_identity(row: ProductWeek, spend: Decimal) -> None:
    result = calculate_week(
        replace(row, ads=replace(row.ads, spend=spend)), Decimal("0.19"), [row]
    )
    assert (
        result.values["contribution_before_ads_eur"] - spend
        == result.values["contribution_after_ads_eur"]
    )


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_ratio_inputs_are_rejected(value: str) -> None:
    with pytest.raises(ValueError, match="finite"):
        ratio(Decimal(value), Decimal(1))


def test_invalid_vat_is_rejected(row: ProductWeek) -> None:
    with pytest.raises(ValueError, match="VAT"):
        calculate_week(row, Decimal("NaN"), [row])


def test_zero_stock_is_a_defined_zero_coverage() -> None:
    rows = list(
        load_inputs(Path("data/sample"), Path("config/column_map.yaml")).rows[:4]
    )
    last = rows[-1]
    rows[-1] = replace(
        last, inventory=last.inventory.model_copy(update={"units_available": 0})
    )
    result = calculate_week(rows[-1], Decimal("0.19"), rows)
    assert result.values["stock_coverage_days"] == 0
    assert "stock_coverage_days" not in result.undefined_reasons


def test_zero_baseline_acos_uses_percentage_points(row: ProductWeek) -> None:
    first = replace(row, ads=AdTotals(ad_sales=Decimal(100)))
    second = replace(
        first,
        retail=first.retail.model_copy(
            update={"week": first.retail.week + timedelta(weeks=1)}
        ),
        ads=AdTotals(spend=Decimal(10), ad_sales=Decimal(100)),
    )
    result = calculate_report([first, second], Decimal("0.19"))[-1]
    assert result.values["acos_pct_wow_pp"] == 10
    assert result.values["ad_spend_eur_wow_pct"] is None
