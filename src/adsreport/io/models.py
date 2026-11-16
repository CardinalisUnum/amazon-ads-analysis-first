"""Typed source records shared by the loader and pure KPI calculations."""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _count(value: object) -> int:
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ValueError("Counts must be nonnegative whole numbers.")
    return int(str(value))


def _date(value: object) -> date:
    return date.fromisoformat(str(value))


Count = Annotated[int, BeforeValidator(_count)]
Day = Annotated[date, BeforeValidator(_date)]
Amount = Annotated[Decimal, Field(ge=0, allow_inf_nan=False)]
Fraction = Annotated[Decimal, Field(ge=0, le=1, allow_inf_nan=False)]
Identifier = Annotated[str, Field(min_length=1)]


class SourceRow(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)


class AdsRow(SourceRow):
    day: Day
    campaign: Identifier
    ad_group: Identifier
    sku: Identifier
    asin: Identifier
    currency: Literal["EUR"]
    impressions: Count
    clicks: Count
    purchases: Count
    ad_units: Count
    spend: Amount
    ad_sales: Amount
    promoted_sales: Amount | None = None
    halo_sales: Amount | None = None


class RetailRow(SourceRow):
    week: Day
    asin: Identifier
    gross_sales: Amount
    units: Count
    sessions: Count


class CostRow(SourceRow):
    asin: Identifier
    unit_product_cost: Amount
    referral_fee_rate: Fraction
    referral_minimum_eur: Amount
    fba_fee_per_unit: Amount
    logistics_storage_per_unit: Amount
    return_rate: Fraction
    loss_per_return: Amount
    lifecycle_phase: Literal["launch", "growth", "maturity"]
    launch_start_date: Day


class InventoryRow(SourceRow):
    week: Day
    asin: Identifier
    units_available: Count
    inbound_units: Count


class InputManifest(SourceRow):
    data_label: Literal["SAMPLE DATA"]
    schema_version: Literal[1]
    marketplace: Literal["amazon.de"]
    currency: Literal["EUR"]
    vat_rate: Fraction
    retail_tax_basis: Literal["gross_including_vat"]
    ads_tax_basis: Literal["net_excluding_vat"]
    reporting_timezone: Literal["Europe/Berlin"]
    first_week: Day
    report_week: Day
    files: dict[str, str] = Field(default_factory=dict)


class CatalogRow(SourceRow):
    asin: Identifier
    sku: Identifier
    set_number: Annotated[str, Field(min_length=1, max_length=20)]
    product_name: Annotated[str, Field(min_length=1, max_length=120)]
    source_url: Annotated[
        str, Field(pattern=r"^https://www\.lego\.com/[A-Za-z0-9/_-]+$", max_length=300)
    ]


@dataclass(frozen=True)
class AdTotals:
    spend: Decimal = Decimal(0)
    ad_sales: Decimal = Decimal(0)
    promoted_sales: Decimal | None = Decimal(0)
    impressions: int = 0
    clicks: int = 0
    purchases: int = 0
    ad_units: int = 0


@dataclass(frozen=True)
class ProductWeek:
    retail: RetailRow
    cost: CostRow
    inventory: InventoryRow
    ads: AdTotals


@dataclass(frozen=True)
class LoadedInput:
    manifest: InputManifest
    rows: tuple[ProductWeek, ...]
    source_hashes: dict[str, str]
    column_map_hash: str
    catalog: tuple[CatalogRow, ...] = ()
