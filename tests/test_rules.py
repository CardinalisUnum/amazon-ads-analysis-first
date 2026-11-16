import json
import re
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from adsreport.config import Thresholds, load_config
from adsreport.io.loader import load_inputs
from adsreport.kpi.engine import ProductMetrics, calculate_report
from adsreport.rules.engine import Flag, evaluate_rules, prioritize

WEEK = date(2026, 10, 26)


@pytest.fixture
def thresholds() -> Thresholds:
    return load_config(Path("config")).thresholds


def record(phase: str = "growth", **updates: Decimal | None) -> ProductMetrics:
    values: dict[str, Decimal | None] = {
        "acos_pct": Decimal(20),
        "break_even_acos_pct": Decimal(30),
        "contribution_after_ads_eur": Decimal(200),
        "organic_share_proxy_pct": Decimal(50),
        "stock_coverage_days": Decimal(35),
        "acos_pct_wow_pp": Decimal(0),
        "net_revenue_eur_wow_pct": Decimal(0),
        "impressions_wow_pct": Decimal(0),
        "ad_spend_eur_wow_pct": Decimal(0),
        "ad_cvr_pct_wow_pct": Decimal(0),
        "clicks_wow_pct": Decimal(0),
        "ad_sales_eur_wow_pct": Decimal(0),
    }
    values.update(updates)
    return ProductMetrics("SAMPLE-TEST", WEEK, phase, date(2026, 8, 3), values, {})


def history(
    row: ProductMetrics, shares: tuple[str, ...] = ("50", "50", "50", "50")
) -> list[ProductMetrics]:
    return [
        replace(
            row,
            week=row.week - timedelta(weeks=len(shares) - 1 - i),
            values={**row.values, "organic_share_proxy_pct": Decimal(share)},
        )
        for i, share in enumerate(shares)
    ]


@pytest.mark.parametrize(
    ("rule", "phase", "updates", "shares"),
    [
        ("R1", "growth", {"acos_pct": Decimal(31)}, ("50",) * 4),
        ("R2", "launch", {"acos_pct": Decimal(31)}, ("50",) * 4),
        (
            "R3",
            "growth",
            {
                "acos_pct_wow_pp": Decimal(-5),
                "net_revenue_eur_wow_pct": Decimal(-10),
                "impressions_wow_pct": Decimal(-10),
            },
            ("50",) * 4,
        ),
        (
            "R4",
            "growth",
            {
                "ad_spend_eur_wow_pct": Decimal(10),
                "stock_coverage_days": Decimal("13.99"),
            },
            ("50",) * 4,
        ),
        (
            "R5",
            "growth",
            {"ad_cvr_pct_wow_pct": Decimal(-20), "clicks_wow_pct": Decimal(10)},
            ("50",) * 4,
        ),
        (
            "R6",
            "growth",
            {"ad_spend_eur_wow_pct": Decimal(30), "ad_sales_eur_wow_pct": Decimal(5)},
            ("50",) * 4,
        ),
        ("R7", "growth", {"contribution_after_ads_eur": Decimal("-0.01")}, ("50",) * 4),
        ("R8", "growth", {}, ("70", "60", "50", "40")),
        ("R9", "maturity", {"acos_pct": Decimal("24.01")}, ("50",) * 4),
    ],
)
def test_each_rule_has_evidence_and_serializes(
    thresholds: Thresholds,
    rule: str,
    phase: str,
    updates: dict[str, Decimal],
    shares: tuple[str, ...],
) -> None:
    result = evaluate_rules(history(record(phase, **updates), shares), thresholds, WEEK)
    assert [flag.rule_id for flag in result.flags] == [rule]
    flag = result.flags[0]
    assert flag.evidence and flag.thresholds and flag.reason
    assert Flag.model_validate_json(flag.model_dump_json()) == flag
    assert json.loads(flag.model_dump_json())["asin"] == "SAMPLE-TEST"


@pytest.mark.parametrize(
    ("rule", "phase", "updates"),
    [
        ("R1", "growth", {"acos_pct": Decimal(30)}),
        (
            "R3",
            "growth",
            {
                "acos_pct_wow_pp": Decimal("-4.99"),
                "net_revenue_eur_wow_pct": Decimal(-10),
                "impressions_wow_pct": Decimal(-10),
            },
        ),
        (
            "R3",
            "growth",
            {
                "acos_pct_wow_pp": Decimal(-5),
                "net_revenue_eur_wow_pct": Decimal("-9.99"),
                "impressions_wow_pct": Decimal(-10),
            },
        ),
        (
            "R3",
            "growth",
            {
                "acos_pct_wow_pp": Decimal(-5),
                "net_revenue_eur_wow_pct": Decimal(-10),
                "impressions_wow_pct": Decimal("-9.99"),
            },
        ),
        (
            "R4",
            "growth",
            {"ad_spend_eur_wow_pct": Decimal(10), "stock_coverage_days": Decimal(14)},
        ),
        (
            "R4",
            "growth",
            {
                "ad_spend_eur_wow_pct": Decimal("9.99"),
                "stock_coverage_days": Decimal(10),
            },
        ),
        ("R5", "growth", {"ad_cvr_pct_wow_pct": Decimal("-19.99")}),
        (
            "R5",
            "growth",
            {"ad_cvr_pct_wow_pct": Decimal(-20), "clicks_wow_pct": Decimal("10.01")},
        ),
        (
            "R5",
            "growth",
            {"ad_cvr_pct_wow_pct": Decimal(-20), "clicks_wow_pct": Decimal("-10.01")},
        ),
        (
            "R6",
            "growth",
            {
                "ad_spend_eur_wow_pct": Decimal("29.99"),
                "ad_sales_eur_wow_pct": Decimal(5),
            },
        ),
        (
            "R6",
            "growth",
            {
                "ad_spend_eur_wow_pct": Decimal(30),
                "ad_sales_eur_wow_pct": Decimal("5.01"),
            },
        ),
        ("R7", "growth", {"contribution_after_ads_eur": Decimal(0)}),
        ("R9", "maturity", {"acos_pct": Decimal(24)}),
        ("R9", "growth", {"acos_pct": Decimal("24.01")}),
    ],
)
def test_threshold_boundaries_do_not_false_flag(
    thresholds: Thresholds, rule: str, phase: str, updates: dict[str, Decimal]
) -> None:
    result = evaluate_rules(history(record(phase, **updates)), thresholds, WEEK)
    assert rule not in {f.rule_id for f in result.flags}


@pytest.mark.parametrize(("days", "expected"), [(55, False), (56, False), (57, True)])
def test_launch_expiry_uses_week_end(
    thresholds: Thresholds, days: int, expected: bool
) -> None:
    row = replace(
        record("launch", acos_pct=Decimal(40)),
        launch_start_date=WEEK + timedelta(days=6 - days),
    )
    result = evaluate_rules(history(row), thresholds, WEEK)
    assert ("R2" in {f.rule_id for f in result.flags}) is expected
    assert "R1" not in {f.rule_id for f in result.flags}


@pytest.mark.parametrize("bad", [None, Decimal("NaN"), Decimal("Infinity")])
def test_missing_or_nonfinite_evidence_is_skipped(
    thresholds: Thresholds, bad: Decimal | None
) -> None:
    result = evaluate_rules(history(record(acos_pct=bad)), thresholds, WEEK)
    assert not result.flags
    assert any(s.rule_id == "R1" and "acos_pct" in s.reason for s in result.skipped)


def test_unknown_spend_change_is_not_inferred_from_zero(thresholds: Thresholds) -> None:
    row = record(ad_spend_eur_wow_pct=None, stock_coverage_days=Decimal(0))
    result = evaluate_rules(history(row), thresholds, WEEK)
    assert not result.flags
    assert {s.rule_id for s in result.skipped} == {"R4", "R6"}


@pytest.mark.parametrize("shares", [("70", "60", "50", "50"), ("70", "50", "60", "40")])
def test_organic_history_requires_strict_decreases(
    thresholds: Thresholds, shares: tuple[str, ...]
) -> None:
    assert not evaluate_rules(history(record(), shares), thresholds, WEEK).flags


def test_organic_history_cannot_bridge_gaps_or_undefined_values(
    thresholds: Thresholds,
) -> None:
    rows = history(record(), ("70", "60", "50", "40"))
    for altered in [
        rows[1:],
        [rows[0], rows[2], rows[3]],
        [
            replace(
                rows[0], values={**rows[0].values, "organic_share_proxy_pct": None}
            ),
            *rows[1:],
        ],
    ]:
        result = evaluate_rules(altered, thresholds, WEEK)
        assert "R8" not in {f.rule_id for f in result.flags}
        assert any(s.rule_id == "R8" and s.week == WEEK for s in result.skipped)


def test_config_changes_are_applied(thresholds: Thresholds) -> None:
    row = record(ad_spend_eur_wow_pct=Decimal(10), stock_coverage_days=Decimal(10))
    assert "R4" in {
        f.rule_id for f in evaluate_rules(history(row), thresholds, WEEK).flags
    }
    strict_stock = thresholds.model_copy(update={"stock_coverage_days": 7.0})
    assert not evaluate_rules(history(row), strict_stock, WEEK).flags
    shorter_history = thresholds.model_copy(update={"organic_decline_transitions": 2})
    assert "R8" in {
        f.rule_id
        for f in evaluate_rules(
            history(record(), ("70", "60", "50")), shorter_history, WEEK
        ).flags
    }


def test_priority_order_deduplicates_products_and_keeps_all_rules(
    thresholds: Thresholds,
) -> None:
    low = replace(record("maturity", acos_pct=Decimal(25)), asin="SAMPLE-A")
    high = replace(
        record(acos_pct=Decimal(40), contribution_after_ads_eur=Decimal(-10)),
        asin="SAMPLE-Z",
    )
    records = [*history(low), *history(high)]
    result = evaluate_rules(records, thresholds, WEEK, priority_limit=1)
    assert len(result.flags) == 3 and len(result.priorities) == 1
    assert result.priorities[0].asin == "SAMPLE-Z"
    assert result.priorities[0].rule_ids == ("R1", "R7")
    assert prioritize(list(reversed(result.flags)), 2) == prioritize(result.flags, 2)
    assert (
        evaluate_rules(list(reversed(records)), thresholds, WEEK, priority_limit=1)
        == result
    )


def test_invalid_rule_requests_fail(thresholds: Thresholds) -> None:
    rows = history(record())
    with pytest.raises(ValueError, match="unique"):
        evaluate_rules([*rows, rows[0]], thresholds, WEEK)
    with pytest.raises(ValueError, match="no KPI records"):
        evaluate_rules(rows, thresholds, WEEK + timedelta(weeks=1))
    with pytest.raises(ValueError, match="positive"):
        evaluate_rules(rows, thresholds, WEEK, priority_limit=0)


def test_sample_expected_flags_match_exactly_and_wording_stays_review_safe(
    thresholds: Thresholds,
) -> None:
    loaded = load_inputs(Path("data/sample"), Path("config/column_map.yaml"))
    result = evaluate_rules(
        calculate_report(loaded.rows, loaded.manifest.vat_rate),
        thresholds,
        loaded.manifest.report_week,
    )
    expected = yaml.safe_load(Path("data/sample/expected_flags.yaml").read_text())
    actual = {asin: [] for asin in expected["products"]}
    for flag in result.flags:
        actual[flag.asin].append(flag.rule_id)
        assert "review" in flag.reason.lower()
        assert not re.search(
            r"\b(increase|decrease|raise|lower|pause|stop|change|adjust)\s+(the\s+)?(bids?|prices?|budgets?)\b|\b(delist|refund)\b",
            flag.reason,
            re.I,
        )
    assert {asin: sorted(ids) for asin, ids in actual.items()} == expected["products"]
    assert len(result.flags) == 10 and len(result.priorities) == 6
    assert not result.skipped


def test_zero_stock_and_expired_launch_at_break_even(thresholds: Thresholds) -> None:
    low_stock = record(ad_spend_eur_wow_pct=Decimal(10), stock_coverage_days=Decimal(0))
    assert {
        f.rule_id for f in evaluate_rules(history(low_stock), thresholds, WEEK).flags
    } == {"R4"}
    at_break_even = record("launch", acos_pct=Decimal(30))
    assert not evaluate_rules(history(at_break_even), thresholds, WEEK).flags


def test_all_applicable_rules_disclose_missing_evidence(thresholds: Thresholds) -> None:
    original = record("maturity")
    missing = replace(original, values={name: None for name in original.values})
    # Set the history's organic values missing as well.
    rows = [
        replace(r, values={name: None for name in r.values}) for r in history(missing)
    ]
    first = evaluate_rules(rows, thresholds, WEEK)
    second = evaluate_rules(
        [replace(r, lifecycle_phase="launch") for r in rows], thresholds, WEEK
    )
    assert not first.flags and not second.flags
    assert {s.rule_id for s in (*first.skipped, *second.skipped)} == {
        f"R{i}" for i in range(1, 10)
    }
