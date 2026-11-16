"""Product-week economics and comparable trends, independent of I/O and AI."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from adsreport.io.models import ProductWeek


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def ratio(
    numerator: Decimal, denominator: Decimal, scale: Decimal = Decimal(1)
) -> Decimal | None:
    if not all(v.is_finite() for v in (numerator, denominator, scale)):
        raise ValueError("Ratios require finite values.")
    if denominator == 0:
        return None
    return numerator / denominator * scale


@dataclass(frozen=True)
class ProductMetrics:
    asin: str
    week: date
    lifecycle_phase: str
    launch_start_date: date
    values: dict[str, Decimal | None]
    undefined_reasons: dict[str, str]


def calculate_week(
    row: ProductWeek, vat_rate: Decimal, history: Sequence[ProductWeek]
) -> ProductMetrics:
    """Round EUR components once and derive ratios from aggregated numerators."""
    if not vat_rate.is_finite() or not Decimal(0) <= vat_rate <= Decimal(1):
        raise ValueError("VAT rate must be finite and between zero and one.")
    retail, ads, cost, stock = row.retail, row.ads, row.cost, row.inventory
    units = Decimal(retail.units)
    net = money(retail.gross_sales / (1 + vat_rate))
    price = ratio(retail.gross_sales, units)
    referral_unit = max(
        cost.referral_minimum_eur, money((price or Decimal(0)) * cost.referral_fee_rate)
    )
    product_cost = money(units * cost.unit_product_cost)
    amazon_fees = money(units * (referral_unit + cost.fba_fee_per_unit))
    logistics = money(units * cost.logistics_storage_per_unit)
    returns = money(units * cost.return_rate * cost.loss_per_return)
    before = net - product_cost - amazon_fees - logistics - returns
    after = before - ads.spend
    values: dict[str, Decimal | None] = {
        "ad_spend_eur": ads.spend,
        "ad_sales_eur": ads.ad_sales,
        "promoted_ad_sales_eur": ads.promoted_sales,
        "total_sales_gross_eur": retail.gross_sales,
        "net_revenue_eur": net,
        "product_cost_eur": product_cost,
        "amazon_fees_eur": amazon_fees,
        "logistics_storage_eur": logistics,
        "returns_cost_eur": returns,
        "contribution_before_ads_eur": before,
        "contribution_after_ads_eur": after,
        "contribution_margin_after_ads_pct": ratio(after, net, Decimal(100)),
        "acos_pct": ratio(ads.spend, ads.ad_sales, Decimal(100)),
        "roas_ratio": ratio(ads.ad_sales, ads.spend),
        "tacos_pct": ratio(ads.spend, net, Decimal(100)),
        "break_even_acos_pct": ratio(before, net, Decimal(100)),
        "price_gross_eur": price,
        "impressions": Decimal(ads.impressions),
        "clicks": Decimal(ads.clicks),
        "purchases": Decimal(ads.purchases),
        "ad_units": Decimal(ads.ad_units),
        "retail_units": units,
        "sessions": Decimal(retail.sessions),
        "ctr_pct": ratio(Decimal(ads.clicks), Decimal(ads.impressions), Decimal(100)),
        "cpc_eur": ratio(ads.spend, Decimal(ads.clicks)),
        "ad_cvr_pct": ratio(Decimal(ads.purchases), Decimal(ads.clicks), Decimal(100)),
        "retail_unit_session_pct": ratio(units, Decimal(retail.sessions), Decimal(100)),
        "stock_units": Decimal(stock.units_available),
        "inbound_units": Decimal(stock.inbound_units),
        "organic_share_proxy_pct": None,
        "stock_coverage_days": None,
    }
    reasons = {
        name: "zero denominator" for name, value in values.items() if value is None
    }
    if ads.promoted_sales is None:
        reasons["promoted_ad_sales_eur"] = "promoted-SKU sales unavailable"
        reasons["organic_share_proxy_pct"] = "promoted-SKU sales unavailable"
    elif net > 0 and ads.promoted_sales <= net:
        values["organic_share_proxy_pct"] = (net - ads.promoted_sales) / net * 100
        reasons.pop("organic_share_proxy_pct", None)
    elif net > 0:
        reasons["organic_share_proxy_pct"] = "attribution residual outside zero to one"
    trailing = [
        r
        for r in history
        if r.retail.asin == retail.asin
        and timedelta(0) <= retail.week - r.retail.week <= timedelta(weeks=3)
    ]
    if len(trailing) == 4 and {r.retail.week for r in trailing} == {
        retail.week - timedelta(weeks=i) for i in range(4)
    }:
        daily_units = Decimal(sum(r.retail.units for r in trailing)) / 28
        values["stock_coverage_days"] = ratio(
            Decimal(stock.units_available), daily_units
        )
        if daily_units:
            reasons.pop("stock_coverage_days", None)
    else:
        reasons["stock_coverage_days"] = "four consecutive weekly observations required"
    return ProductMetrics(
        retail.asin,
        retail.week,
        cost.lifecycle_phase,
        cost.launch_start_date,
        values,
        reasons,
    )


def calculate_report(
    rows: Sequence[ProductWeek], vat_rate: Decimal
) -> list[ProductMetrics]:
    """Keep missing weeks explicit and calculate changes only for adjacent weeks."""
    history: list[ProductWeek] = []
    prior: dict[str, ProductMetrics] = {}
    results: list[ProductMetrics] = []
    for row in sorted(rows, key=lambda r: (r.retail.asin, r.retail.week)):
        history = [*history[-3:], row]
        current = calculate_week(row, vat_rate, history)
        previous = prior.get(current.asin)
        for name in (
            "ad_spend_eur",
            "ad_sales_eur",
            "net_revenue_eur",
            "impressions",
            "clicks",
            "ad_cvr_pct",
            "acos_pct",
        ):
            key = name + ("_wow_pp" if name == "acos_pct" else "_wow_pct")
            value = current.values[name]
            current.values[key] = None
            if previous is None or current.week - previous.week != timedelta(weeks=1):
                current.undefined_reasons[key] = "no adjacent prior week"
                continue
            baseline = previous.values[name]
            if (
                value is None
                or baseline is None
                or (baseline == 0 and name != "acos_pct")
            ):
                current.undefined_reasons[key] = (
                    "prior or current value undefined, or zero baseline"
                )
                continue
            if name == "acos_pct":
                current.values[key] = value - baseline
            else:
                current.values[key] = (value - baseline) / baseline * 100
        prior[current.asin] = current
        results.append(current)
    return results
