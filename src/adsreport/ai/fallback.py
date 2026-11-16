"""Deterministic notes from measured facts and existing rule flags."""

from decimal import ROUND_HALF_UP, Decimal

from adsreport.ai.models import Claim, Note, Review
from adsreport.guard.numbers import METRICS, direction, render_claim
from adsreport.kpi.engine import ProductMetrics
from adsreport.rules.engine import Flag

REVIEWS: dict[Review, str] = {
    "routine_review": "Review routine performance with the Ads manager.",
    "profitability": "Review product economics and ad efficiency with the Ads manager.",
    "launch_window": "Review launch age and launch economics with the Ads manager.",
    "sales_and_reach": "Review the sales and reach decline with the Ads manager.",
    "inventory": "Review stock availability and the spend trend with the Ads manager.",
    "conversion": "Review conversion and detail-page health with the Ads manager.",
    "spend_and_sales": "Review spend and attributed-sales trends with the Ads manager.",
    "organic_share": "Review the organic-share proxy limits with the Ads manager.",
}
RULE_REVIEWS: dict[str, Review] = {
    "R1": "profitability",
    "R2": "launch_window",
    "R3": "sales_and_reach",
    "R4": "inventory",
    "R5": "conversion",
    "R6": "spend_and_sales",
    "R7": "profitability",
    "R8": "organic_share",
    "R9": "profitability",
}


def allowed_reviews(flags: list[Flag]) -> list[Review]:
    return list(dict.fromkeys(RULE_REVIEWS[f.rule_id] for f in flags)) or [
        "routine_review"
    ]


def template_note(
    product: ProductMetrics,
    flags: list[Flag],
    reason: str,
    issues: tuple[str, ...] = (),
    rejected_tokens: tuple[str, ...] = (),
) -> Note:
    claims = tuple(
        Claim(
            metric=metric,
            value=str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            unit=METRICS[metric][1],
            direction=direction(metric, value),
        )
        for metric in ("ad_spend_eur", "acos_pct", "contribution_after_ads_eur")
        if (value := product.values.get(metric)) is not None and value.is_finite()
    )
    text = " ".join(render_claim(c) for c in claims)
    if not text:
        text = "The selected metrics are unavailable. Review the input evidence."
    return Note(
        asin=product.asin,
        week=product.week,
        label="template",
        reason=reason,
        what_happened=text,
        planned_change_to_review=REVIEWS[allowed_reviews(flags)[0]],
        claims=claims,
        guard_issues=issues,
        rejected_numeric_tokens=rejected_tokens,
    )
