"""Seeded sample exports with deliberately reviewable product stories."""

import csv
import hashlib
import io
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import yaml

from adsreport.artifacts import publish_bundle

FIRST_WEEK = date(2026, 9, 7)
REPORT_WEEK = FIRST_WEEK + timedelta(weeks=7)
CENT = Decimal("0.01")


@dataclass(frozen=True)
class Product:
    set_number: str
    name: str
    slug: str
    gross_price: str
    story: str
    phase: str
    expected_flags: tuple[str, ...] = ()


# Prices and scenarios are synthetic retailer assumptions. Sources identify sets.
PRODUCTS = (
    Product(
        "10696",
        "Medium Creative Brick Box",
        "lego-medium-creative-brick-box",
        "29.99",
        "healthy",
        "maturity",
    ),
    Product(
        "10698",
        "Large Creative Brick Box",
        "lego-large-creative-brick-box",
        "49.99",
        "healthy",
        "maturity",
    ),
    Product(
        "11034", "Creative Pets", "creative-pets", "29.99", "launch_inside", "launch"
    ),
    Product(
        "11035",
        "Creative Houses",
        "creative-houses",
        "54.99",
        "launch_expired",
        "launch",
        ("R2",),
    ),
    Product(
        "11036",
        "Creative Vehicles",
        "creative-vehicles",
        "54.99",
        "above_break_even",
        "growth",
        ("R1",),
    ),
    Product(
        "11037",
        "Creative Space Planets",
        "creative-space-planets",
        "29.99",
        "efficiency_illusion",
        "growth",
        ("R3", "R8"),
    ),
    Product(
        "11039",
        "Creative Food Friends",
        "creative-food-friends",
        "9.99",
        "negative_contribution",
        "growth",
        ("R1", "R7"),
    ),
    Product(
        "11040",
        "Magical Transparent Box",
        "magical-transparent-box",
        "29.99",
        "conversion_drop",
        "growth",
        ("R5",),
    ),
    Product(
        "11041",
        "Creative Dinosaurs",
        "creative-dinosaurs",
        "29.99",
        "spend_spike",
        "maturity",
        ("R6", "R9"),
    ),
    Product(
        "11042",
        "Creative Happy Box",
        "creative-happy-box",
        "49.99",
        "low_stock",
        "growth",
        ("R4",),
    ),
)


def _money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def _split(total: int, weights: list[int]) -> list[int]:
    """Allocate integer counts or cents while preserving the exact total."""
    if total == 0:
        return [0] * len(weights)
    denominator = sum(weights)
    portions = [total * weight // denominator for weight in weights]
    order = sorted(
        range(len(weights)),
        key=lambda i: (total * weights[i]) % denominator,
        reverse=True,
    )
    for i in order[: total - sum(portions)]:
        portions[i] += 1
    return portions


def _csv(rows: list[dict[str, str | int]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _activity(
    product: Product, week: int, base_units: int
) -> tuple[int, int, int, int, Decimal]:
    """Return units, ad purchases, clicks, impressions and target ACoS ratio."""
    units = base_units
    paid_share = Decimal("0.35")
    acos = Decimal("0.18")
    if product.story == "launch_inside" and week < 4:
        units = 0
    if product.story in {"launch_inside", "launch_expired", "above_break_even"}:
        acos = Decimal("0.60")
    if product.story == "negative_contribution":
        paid_share, acos = Decimal("0.65"), Decimal("0.70")
    if product.story == "efficiency_illusion" and week >= 4:
        paid_share = Decimal("0.20") + Decimal("0.04") * (week - 3)
        if week == 7:
            units = base_units * 3 // 4
            acos = Decimal("0.10")
    if product.story == "low_stock" and week == 7:
        units = base_units * 6 // 5
        acos = Decimal("0.24")
    if product.story == "conversion_drop" and week == 7:
        paid_share = Decimal("0.20")
    if product.story == "spend_spike" and week == 7:
        acos = Decimal("0.30")
    purchases = round(units * paid_share)
    clicks = round(Decimal(purchases) / Decimal("0.12"))
    if product.story == "conversion_drop" and week == 7:
        clicks = round(round(base_units * Decimal("0.35")) / Decimal("0.12"))
    impressions = clicks * 50
    if product.story == "efficiency_illusion" and week == 7:
        impressions = impressions * 4 // 5
    return units, purchases, clicks, impressions, acos


def generate_sample(destination: Path, seed: int, vat_rate: Decimal) -> Path:
    """Publish a complete sample directory, or verify an identical existing copy.

    Stage the whole bundle beside the destination and rename it into place.
    Existing different content is preserved and requires another output path.
    """
    if not vat_rate.is_finite() or vat_rate != Decimal("0.19"):
        raise ValueError("The approved sample scenarios require VAT rate 0.19.")
    rng = random.Random(seed)
    ads: list[dict[str, str | int]] = []
    retail: list[dict[str, str | int]] = []
    costs: list[dict[str, str | int]] = []
    inventory: list[dict[str, str | int]] = []
    catalog: list[dict[str, str | int]] = []
    expected: dict[str, list[str]] = {}
    for index, product in enumerate(PRODUCTS, start=1):
        asin, sku = f"SAMPLE{index:04d}", f"SAMPLE-{product.set_number}"
        price = Decimal(product.gross_price)
        net_price = price / (1 + vat_rate)
        base_units = rng.randint(80, 140)
        launch_date = date(2026, 8, 3)
        if product.story == "launch_inside":
            launch_date = date(2026, 10, 5)
        catalog.append(
            {
                "asin": asin,
                "sku": sku,
                "brand": "LEGO",
                "set_number": product.set_number,
                "product_name": product.name,
                "story": product.story,
                "source_url": f"https://www.lego.com/en-de/product/{product.slug}-{product.set_number}",
                "source_checked_on": "2026-11-16",
                "data_label": "SAMPLE DATA",
            }
        )
        costs.append(
            {
                "asin": asin,
                "unit_product_cost": _money(net_price * Decimal("0.34")),
                "referral_fee_rate": "0.15",
                "referral_minimum_eur": "0.30",
                "fba_fee_per_unit": _money(
                    max(Decimal("2.50"), price * Decimal("0.07"))
                ),
                "logistics_storage_per_unit": "0.20",
                "return_rate": "0.04",
                "loss_per_return": _money(net_price / 2),
                "lifecycle_phase": product.phase,
                "launch_start_date": launch_date.isoformat(),
            }
        )
        expected[asin] = list(product.expected_flags)
        for week in range(8):
            start = FIRST_WEEK + timedelta(weeks=week)
            units, purchases, clicks, impressions, acos = _activity(
                product, week, base_units
            )
            ad_sales = Decimal(_money(net_price * purchases))
            spend = Decimal(_money(ad_sales * acos))
            retail.append(
                {
                    "week": start.isoformat(),
                    "asin": asin,
                    "gross_sales": _money(price * units),
                    "units": units,
                    "sessions": units * 6,
                }
            )
            inventory.append(
                {
                    "week": start.isoformat(),
                    "asin": asin,
                    "units_available": 5
                    if product.story == "low_stock" and week == 7
                    else units * 5,
                    "inbound_units": units * 2,
                }
            )
            weights = [rng.randint(8, 12) for _ in range(14)]
            orders = _split(purchases, weights)
            click_counts = _split(clicks, weights)
            impression_counts = _split(impressions, weights)
            sales_cents = _split(int(ad_sales * 100), orders)
            spend_cents = _split(int(spend * 100), click_counts)
            for slot in range(14):
                row_spend = Decimal(spend_cents[slot]) / 100
                row_sales = Decimal(sales_cents[slot]) / 100
                count_clicks, count_impressions = (
                    click_counts[slot],
                    impression_counts[slot],
                )
                ads.append(
                    {
                        "Date": (start + timedelta(days=slot // 2)).isoformat(),
                        "Campaign Name": f"SAMPLE campaign {slot % 2 + 1}",
                        "Ad Group Name": "SAMPLE product group",
                        "Advertised SKU": sku,
                        "Advertised ASIN": asin,
                        "Currency": "EUR",
                        "Impressions": count_impressions,
                        "Clicks": count_clicks,
                        "Click-Thru Rate (CTR)": _money(
                            Decimal(count_clicks) * 100 / count_impressions
                        )
                        + "%"
                        if count_impressions
                        else "",
                        "Cost Per Click (CPC)": _money(row_spend / count_clicks)
                        if count_clicks
                        else "",
                        "Spend": _money(row_spend),
                        "7 Day Total Sales": _money(row_sales),
                        "7 Day Advertised SKU Sales": _money(row_sales),
                        "7 Day Other SKU Sales": "0.00",
                        "Total Advertising Cost of Sales (ACoS)": _money(
                            row_spend * 100 / row_sales
                        )
                        + "%"
                        if row_sales
                        else "",
                        "Total Return on Advertising Spend (RoAS)": _money(
                            row_sales / row_spend
                        )
                        if row_spend
                        else "",
                        "7 Day Total Orders (#)": orders[slot],
                        "7 Day Total Units (#)": orders[slot],
                    }
                )
    files = {
        "SAMPLE_ads.csv": _csv(ads),
        "SAMPLE_total_sales.csv": _csv(retail),
        "SAMPLE_costs.csv": _csv(costs),
        "SAMPLE_inventory.csv": _csv(inventory),
        "SAMPLE_catalog.csv": _csv(catalog),
        "expected_flags.yaml": yaml.safe_dump(
            {
                "data_label": "SAMPLE DATA",
                "report_week": REPORT_WEEK.isoformat(),
                "scope": "latest sample week only",
                "products": expected,
            },
            sort_keys=False,
        ).encode("utf-8"),
    }
    manifest = {
        "data_label": "SAMPLE DATA",
        "schema_version": 1,
        "seed": seed,
        "marketplace": "amazon.de",
        "currency": "EUR",
        "vat_rate": str(vat_rate),
        "retail_tax_basis": "gross_including_vat",
        "ads_tax_basis": "net_excluding_vat",
        "first_week": FIRST_WEEK.isoformat(),
        "report_week": REPORT_WEEK.isoformat(),
        "weeks": 8,
        "products": 10,
        "reporting_timezone": "Europe/Berlin",
        "ads_format": "English classic daily seller Sponsored Products",
        "retail_format": "normalized weekly child-item export adapter",
        "attribution_assumption": (
            "zero halo, one unit per purchase, matched sample periods"
        ),
        "files": {
            name: hashlib.sha256(content).hexdigest() for name, content in files.items()
        },
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    return publish_bundle(destination, files)
