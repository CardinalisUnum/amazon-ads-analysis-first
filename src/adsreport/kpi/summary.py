"""Portfolio totals and comparable-week changes, calculated once in Python."""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from adsreport.kpi.engine import ProductMetrics, ratio

HEADLINES = (
    "ad_spend_eur",
    "ad_sales_eur",
    "total_sales_gross_eur",
    "tacos_pct",
    "contribution_after_ads_eur",
)


@dataclass(frozen=True)
class PortfolioWeek:
    week: date
    values: dict[str, Decimal | None]
    deltas: dict[str, Decimal | None]
    comparison_reason: str


def summarize(records: Sequence[ProductMetrics]) -> tuple[PortfolioWeek, ...]:
    grouped: dict[date, list[ProductMetrics]] = defaultdict(list)
    for record in records:
        grouped[record.week].append(record)
    result: list[PortfolioWeek] = []
    previous_asins: set[str] = set()
    for week, products in sorted(grouped.items()):
        values: dict[str, Decimal | None] = {}
        for metric in (*HEADLINES, "net_revenue_eur"):
            if metric == "tacos_pct":
                continue
            source = [p.values.get(metric) for p in products]
            values[metric] = (
                sum((v for v in source if v is not None), Decimal(0))
                if all(v is not None and v.is_finite() for v in source)
                else None
            )
        spend, net = values["ad_spend_eur"], values["net_revenue_eur"]
        values["tacos_pct"] = (
            ratio(spend, net, Decimal(100))
            if spend is not None and net is not None
            else None
        )
        asins = {p.asin for p in products}
        comparable = bool(
            result
            and result[-1].week == week - timedelta(days=7)
            and asins == previous_asins
        )
        deltas = {}
        for metric in HEADLINES:
            prior = result[-1].values[metric] if comparable else None
            current = values[metric]
            deltas[metric] = (
                current - prior if current is not None and prior is not None else None
            )
        result.append(
            PortfolioWeek(
                week,
                values,
                deltas,
                "Comparable prior week"
                if comparable
                else "Prior week missing or product coverage differs",
            )
        )
        previous_asins = asins
    return tuple(result)
