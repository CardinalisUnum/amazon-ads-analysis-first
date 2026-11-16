"""No prose inference: metric labels and units are owned by Python."""

import re
from decimal import ROUND_HALF_UP, Decimal

from adsreport.ai.models import Claim, Direction, Draft, Unit
from adsreport.kpi.engine import ProductMetrics

# Explicit labels prevent a valid ACoS value being described as TACoS.
METRICS: dict[str, tuple[str, Unit]] = {
    "ad_spend_eur": ("Ad spend", "EUR"),
    "ad_sales_eur": ("Ad-attributed sales", "EUR"),
    "promoted_ad_sales_eur": ("Promoted-product ad sales", "EUR"),
    "total_sales_gross_eur": ("Total sales including VAT", "EUR"),
    "net_revenue_eur": ("Net retail revenue", "EUR"),
    "product_cost_eur": ("Product cost", "EUR"),
    "amazon_fees_eur": ("Amazon fees", "EUR"),
    "logistics_storage_eur": ("Logistics and storage", "EUR"),
    "returns_cost_eur": ("Modelled return loss", "EUR"),
    "contribution_before_ads_eur": ("Contribution before ads", "EUR"),
    "contribution_after_ads_eur": ("Contribution after ads", "EUR"),
    "contribution_margin_after_ads_pct": ("Contribution margin after ads", "percent"),
    "acos_pct": ("ACoS", "percent"),
    "roas_ratio": ("ROAS", "ratio"),
    "tacos_pct": ("TACoS (ad spend / net retail revenue)", "percent"),
    "break_even_acos_pct": ("Break-even ACoS", "percent"),
    "price_gross_eur": ("Unit price including VAT", "EUR"),
    "impressions": ("Impressions", "count"),
    "clicks": ("Clicks", "count"),
    "purchases": ("Ad-attributed purchases", "count"),
    "ad_units": ("Ad-attributed units", "units"),
    "retail_units": ("Retail units", "units"),
    "sessions": ("Sessions", "count"),
    "ctr_pct": ("Click-through rate", "percent"),
    "cpc_eur": ("Cost per click", "EUR"),
    "ad_cvr_pct": ("Ad conversion rate", "percent"),
    "retail_unit_session_pct": ("Retail unit session rate", "percent"),
    "stock_units": ("Available stock", "units"),
    "inbound_units": ("Inbound stock", "units"),
    "organic_share_proxy_pct": ("Organic share proxy", "percent"),
    "stock_coverage_days": ("Stock coverage", "days"),
    "acos_pct_wow_pp": ("Week-over-week ACoS change", "percentage_points"),
}
for _metric in (
    "ad_spend_eur",
    "ad_sales_eur",
    "net_revenue_eur",
    "impressions",
    "clicks",
    "ad_cvr_pct",
):
    METRICS[f"{_metric}_wow_pct"] = (
        f"Week-over-week change in {METRICS[_metric][0].lower()}",
        "percent",
    )

NUMBER = re.compile(r"[+-]?[0-9]+(?:[.,][0-9]+)?")


def rounded_values(value: Decimal) -> set[Decimal]:
    return {value} | {
        value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
        for places in range(3)
    }


def direction(metric: str, value: Decimal) -> Direction:
    if "_wow_" not in metric:
        return "level"
    if value == 0:
        return "flat"
    return "up" if value > 0 else "down"


def check_claim(claim: Claim, product: ProductMetrics) -> tuple[str, ...]:
    value = product.values.get(claim.metric)
    if claim.metric not in METRICS or value is None or not value.is_finite():
        return ("metric_unavailable",)
    issues = []
    if claim.unit != METRICS[claim.metric][1]:
        issues.append("unit_mismatch")
    if claim.direction != direction(claim.metric, value):
        issues.append("direction_mismatch")
    if not NUMBER.fullmatch(claim.value):
        issues.append("numeric_syntax")
    elif Decimal(claim.value.replace(",", ".")) not in rounded_values(value):
        issues.append("unsupported_value")
    return tuple(issues)


def check_draft(draft: Draft, product: ProductMetrics) -> tuple[str, ...]:
    issues = []
    if draft.asin != product.asin:
        issues.append("product_mismatch")
    if draft.week != product.week:
        issues.append("week_mismatch")
    if len({claim.metric for claim in draft.what_happened}) != len(draft.what_happened):
        issues.append("duplicate_metric")
    for claim in draft.what_happened:
        issues.extend(check_claim(claim, product))
    return tuple(dict.fromkeys(issues))


def render_claim(claim: Claim) -> str:
    """Called only after validation, or with Python-created template facts."""
    label, unit = METRICS[claim.metric]
    value = claim.value.replace(",", ".")
    suffix = {
        "EUR": "",
        "percent": "%",
        "percentage_points": " pp",
        "ratio": "x",
        "count": "",
        "units": " units",
        "days": " days",
    }[unit]
    display = f"EUR {value}" if unit == "EUR" else f"{value}{suffix}"
    trend = "" if claim.direction == "level" else f" ({claim.direction})"
    return f"{label}: {display}{trend}."
