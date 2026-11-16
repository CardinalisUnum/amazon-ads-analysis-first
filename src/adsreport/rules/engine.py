"""Pure review flags, missing-evidence records and deterministic priorities."""

from collections.abc import Mapping, Sequence
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

from adsreport.config import Thresholds
from adsreport.kpi.engine import ProductMetrics

RuleId = Literal["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9"]
Severity = Literal["high", "medium", "low"]
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class Flag(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)
    rule_id: RuleId
    asin: str
    week: date
    severity: Severity
    evidence: dict[str, Decimal | date]
    thresholds: dict[str, Decimal]
    reason: str


class SkippedRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    rule_id: RuleId
    asin: str
    week: date
    reason: str


class Priority(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    asin: str
    week: date
    severity: Severity
    rule_ids: tuple[RuleId, ...]


class RuleReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    report_week: date
    flags: tuple[Flag, ...]
    skipped: tuple[SkippedRule, ...]
    priorities: tuple[Priority, ...]


def _facts(
    row: ProductMetrics,
    rule_id: RuleId,
    names: tuple[str, ...],
    skipped: list[SkippedRule],
) -> dict[str, Decimal] | None:
    evidence: dict[str, Decimal] = {}
    missing: list[str] = []
    for name in names:
        value = row.values.get(name)
        if value is None or not value.is_finite():
            reason = row.undefined_reasons.get(name, "unavailable or nonfinite")
            missing.append(f"{name} ({reason})")
        else:
            evidence[name] = value
    if missing:
        skipped.append(
            SkippedRule(
                rule_id=rule_id, asin=row.asin, week=row.week, reason=", ".join(missing)
            )
        )
        return None
    return evidence


def prioritize(flags: Sequence[Flag], limit: int) -> tuple[Priority, ...]:
    """Rank products once, retaining every rule attached to a selected product."""
    if limit < 1:
        raise ValueError("Priority limit must be positive.")
    ordered = sorted(
        flags, key=lambda f: (SEVERITY_ORDER[f.severity], f.asin, f.week, f.rule_id)
    )
    groups: dict[tuple[str, date], list[Flag]] = {}
    for flag in ordered:
        groups.setdefault((flag.asin, flag.week), []).append(flag)
    return tuple(
        Priority(
            asin=asin,
            week=week,
            severity=items[0].severity,
            rule_ids=tuple(f.rule_id for f in items),
        )
        for (asin, week), items in list(groups.items())[:limit]
    )


def _emit(
    flags: list[Flag],
    row: ProductMetrics,
    rule_id: RuleId,
    severity: Severity,
    evidence: Mapping[str, Decimal | date],
    thresholds: dict[str, Decimal],
    reason: str,
) -> None:
    flags.append(
        Flag(
            rule_id=rule_id,
            asin=row.asin,
            week=row.week,
            severity=severity,
            evidence=dict(evidence),
            thresholds=thresholds,
            reason=reason,
        )
    )


def evaluate_rules(
    records: Sequence[ProductMetrics],
    config: Thresholds,
    report_week: date,
    priority_limit: int = 6,
) -> RuleReport:
    """Evaluate the requested week using explicit thresholds and comparable history."""
    indexed = {(r.asin, r.week): r for r in records}
    if len(indexed) != len(records):
        raise ValueError("Rules require unique product-week KPI records.")
    current = sorted(
        (r for r in records if r.week == report_week), key=lambda r: r.asin
    )
    if not current:
        raise ValueError("The requested report week has no KPI records.")
    flags: list[Flag] = []
    skipped: list[SkippedRule] = []
    for row in current:
        if row.lifecycle_phase in {"growth", "maturity"}:
            facts = _facts(row, "R1", ("acos_pct", "break_even_acos_pct"), skipped)
            if facts is not None and facts["acos_pct"] > facts["break_even_acos_pct"]:
                _emit(
                    flags,
                    row,
                    "R1",
                    "high",
                    dict(facts),
                    {"break_even_acos_pct": facts["break_even_acos_pct"]},
                    (
                        "ACoS exceeds the product break-even benchmark. Review product "
                        "economics and campaign mix."
                    ),
                )

        age_days = (row.week + timedelta(days=6) - row.launch_start_date).days
        if (
            row.lifecycle_phase == "launch"
            and age_days > config.launch_window_weeks * 7
        ):
            facts = _facts(row, "R2", ("acos_pct", "break_even_acos_pct"), skipped)
            if facts is not None and facts["acos_pct"] > facts["break_even_acos_pct"]:
                launch_evidence: dict[str, Decimal | date] = dict(facts)
                launch_evidence.update(
                    {
                        "launch_start_date": row.launch_start_date,
                        "review_week_end": row.week + timedelta(days=6),
                        "launch_age_days": Decimal(age_days),
                    }
                )
                _emit(
                    flags,
                    row,
                    "R2",
                    "high",
                    launch_evidence,
                    {
                        "launch_window_weeks": Decimal(config.launch_window_weeks),
                        "break_even_acos_pct": facts["break_even_acos_pct"],
                    },
                    (
                        "The launch window has passed and ACoS exceeds break-even. "
                        "Review the launch exit criteria."
                    ),
                )

        facts = _facts(
            row,
            "R3",
            ("acos_pct_wow_pp", "net_revenue_eur_wow_pct", "impressions_wow_pct"),
            skipped,
        )
        improvement = Decimal(str(config.acos_improvement_pp))
        sales_drop = Decimal(str(config.sales_drop_fraction)) * 100
        impressions_drop = Decimal(str(config.impressions_drop_fraction)) * 100
        if (
            facts is not None
            and facts["acos_pct_wow_pp"] <= -improvement
            and facts["net_revenue_eur_wow_pct"] <= -sales_drop
            and facts["impressions_wow_pct"] <= -impressions_drop
        ):
            _emit(
                flags,
                row,
                "R3",
                "medium",
                dict(facts),
                {
                    "acos_improvement_pp": improvement,
                    "sales_drop_pct": sales_drop,
                    "impressions_drop_pct": impressions_drop,
                },
                (
                    "ACoS improved while total sales and impressions declined. Review "
                    "the sales and reach trend together."
                ),
            )

        facts = _facts(
            row, "R4", ("ad_spend_eur_wow_pct", "stock_coverage_days"), skipped
        )
        spend_growth = Decimal(str(config.stock_spend_increase_fraction)) * 100
        coverage = Decimal(str(config.stock_coverage_days))
        if (
            facts is not None
            and facts["ad_spend_eur_wow_pct"] >= spend_growth
            and facts["stock_coverage_days"] < coverage
        ):
            _emit(
                flags,
                row,
                "R4",
                "high",
                dict(facts),
                {"spend_increase_pct": spend_growth, "stock_coverage_days": coverage},
                (
                    "Ad spend rose while stock coverage is below the review threshold. "
                    "Review stock and replenishment timing."
                ),
            )

        facts = _facts(row, "R5", ("ad_cvr_pct_wow_pct", "clicks_wow_pct"), skipped)
        cvr_drop = Decimal(str(config.cvr_drop_fraction)) * 100
        stable_clicks = Decimal(str(config.stable_clicks_fraction)) * 100
        if (
            facts is not None
            and facts["ad_cvr_pct_wow_pct"] <= -cvr_drop
            and abs(facts["clicks_wow_pct"]) <= stable_clicks
        ):
            _emit(
                flags,
                row,
                "R5",
                "medium",
                dict(facts),
                {"cvr_drop_pct": cvr_drop, "stable_clicks_pct": stable_clicks},
                (
                    "Ad purchase rate fell while clicks stayed within the stability "
                    "range. Review traffic and offer conditions."
                ),
            )

        facts = _facts(
            row, "R6", ("ad_spend_eur_wow_pct", "ad_sales_eur_wow_pct"), skipped
        )
        spend_spike = Decimal(str(config.spend_spike_fraction)) * 100
        sales_growth = Decimal(str(config.max_ad_sales_growth_fraction)) * 100
        if (
            facts is not None
            and facts["ad_spend_eur_wow_pct"] >= spend_spike
            and facts["ad_sales_eur_wow_pct"] <= sales_growth
        ):
            _emit(
                flags,
                row,
                "R6",
                "medium",
                dict(facts),
                {
                    "spend_increase_pct": spend_spike,
                    "max_ad_sales_growth_pct": sales_growth,
                },
                (
                    "Ad spend increased beyond the spike threshold while attributed "
                    "sales growth stayed limited. Review campaign performance."
                ),
            )

        facts = _facts(row, "R7", ("contribution_after_ads_eur",), skipped)
        if facts is not None and facts["contribution_after_ads_eur"] < 0:
            _emit(
                flags,
                row,
                "R7",
                "high",
                dict(facts),
                {"contribution_after_ads_eur": Decimal(0)},
                (
                    "Contribution after ads is negative. Review the product cost and "
                    "advertising evidence."
                ),
            )

        transitions = config.organic_decline_transitions
        history = [
            indexed.get((row.asin, report_week - timedelta(weeks=i)))
            for i in range(transitions, -1, -1)
        ]
        organic = [
            r.values.get("organic_share_proxy_pct") if r is not None else None
            for r in history
        ]
        if any(value is None or not value.is_finite() for value in organic):
            skipped.append(
                SkippedRule(
                    rule_id="R8",
                    asin=row.asin,
                    week=row.week,
                    reason=(
                        "Organic history needs consecutive weeks with finite values."
                    ),
                )
            )
        else:
            shares = [v for v in organic if v is not None]
            if all(a > b for a, b in zip(shares[:-1], shares[1:], strict=True)):
                history_evidence: dict[str, Decimal | date] = {}
                for i, value in enumerate(shares):
                    observed_week = report_week - timedelta(weeks=transitions - i)
                    history_evidence[f"organic_share_proxy_pct[{observed_week}]"] = (
                        value
                    )
                _emit(
                    flags,
                    row,
                    "R8",
                    "low",
                    history_evidence,
                    {"decline_transitions": Decimal(transitions)},
                    (
                        "Estimated organic share declined across consecutive observed "
                        "weeks. Review the sales mix and attribution limits."
                    ),
                )

        if row.lifecycle_phase == "maturity":
            facts = _facts(row, "R9", ("acos_pct", "break_even_acos_pct"), skipped)
            margin_fraction = Decimal(str(config.maturity_break_even_fraction))
            if (
                facts is not None
                and facts["acos_pct"] > margin_fraction * facts["break_even_acos_pct"]
            ):
                _emit(
                    flags,
                    row,
                    "R9",
                    "low",
                    dict(facts),
                    {
                        "break_even_fraction": margin_fraction,
                        "acos_threshold_pct": margin_fraction
                        * facts["break_even_acos_pct"],
                    },
                    (
                        "Maturity-stage ACoS exceeds the configured margin-buffer "
                        "threshold. Review the remaining contribution headroom."
                    ),
                )

    ordered = tuple(
        sorted(flags, key=lambda f: (SEVERITY_ORDER[f.severity], f.asin, f.rule_id))
    )
    return RuleReport(
        report_week=report_week,
        flags=ordered,
        skipped=tuple(skipped),
        priorities=prioritize(ordered, priority_limit),
    )
