"""Read English CSV exports, validate their grain and join product-week records."""

import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import yaml
from pydantic import BaseModel, TypeAdapter, ValidationError

from adsreport.io.models import (
    AdsRow,
    AdTotals,
    CostRow,
    InputManifest,
    InventoryRow,
    LoadedInput,
    ProductWeek,
    RetailRow,
)


class InputError(ValueError):
    """Input cannot support an unambiguous, validated report."""


def _read_csv[Row: BaseModel](
    name: str,
    content: bytes,
    model: type[Row],
    aliases: dict[str, list[str]],
    *,
    allow_empty: bool = False,
) -> list[Row]:
    records: list[Row] = []
    with io.StringIO(content.decode("utf-8-sig"), newline="") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames
        if not headers or len(headers) != len(set(headers)):
            raise InputError(f"{name}: missing or duplicate CSV headers.")
        reader.fieldnames = [header.strip() for header in headers]
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise InputError(f"{name}: duplicate normalized CSV headers.")
        for field, info in model.model_fields.items():
            if info.is_required() and not set([field, *aliases.get(field, [])]) & set(
                reader.fieldnames
            ):
                raise InputError(f"{name}: missing required column {field}.")
        for number, row in enumerate(reader, start=2):
            if None in row or None in row.values():
                raise InputError(f"{name}:{number}: CSV field count mismatch.")
            normalized: dict[str, str] = {}
            for field in model.model_fields:
                names = [field, *aliases.get(field, [])]
                values = {
                    row[name].strip()
                    for name in names
                    if name in row and row[name].strip()
                }
                if len(values) > 1:
                    raise InputError(
                        f"{name}:{number}: conflicting aliases for {field}."
                    )
                if values:
                    normalized[field] = values.pop()
            try:
                records.append(model.model_validate(normalized))
            except ValidationError as exc:
                details = ", ".join(f"{e['loc']}: {e['msg']}" for e in exc.errors())
                raise InputError(f"{name}:{number}: {details}") from exc
    if not records and not allow_empty:
        raise InputError(f"{name}: an empty export cannot establish completeness.")
    return records


def load_inputs(folder: Path, column_map: Path) -> LoadedInput:
    """Preserve exact numeric text, require metadata, and reject ambiguous joins."""
    try:
        manifest_bytes = (folder / "manifest.json").read_bytes()
        manifest = InputManifest.model_validate_json(manifest_bytes.decode("utf-8-sig"))
        aliases = TypeAdapter(dict[str, dict[str, list[str]]]).validate_python(
            yaml.safe_load(column_map.read_text(encoding="utf-8-sig")), strict=True
        )
        if not {"ads", "retail"} <= aliases.keys():
            raise InputError("Column map must contain ads and retail mappings.")
        if (
            manifest.first_week.weekday()
            or manifest.report_week.weekday()
            or manifest.first_week > manifest.report_week
        ):
            raise InputError("Manifest weeks must be ordered Monday dates.")
        paths: dict[str, Path] = {}
        for kind in ("ads", "total_sales", "costs", "inventory"):
            candidates = [
                p
                for p in (folder / f"SAMPLE_{kind}.csv", folder / f"{kind}.csv")
                if p.is_file()
            ]
            if len(candidates) != 1:
                raise InputError(
                    f"Provide exactly one {kind}.csv or SAMPLE_{kind}.csv."
                )
            paths[kind] = candidates[0]
        contents = {p.name: p.read_bytes() for p in paths.values()}
        for name, expected in manifest.files.items():
            if Path(name).name != name or name in {".", ".."}:
                raise InputError(
                    "Manifest file names must stay inside the input directory."
                )
            if name not in contents:
                contents[name] = (folder / name).read_bytes()
            if hashlib.sha256(contents[name]).hexdigest() != expected:
                raise InputError(f"{name}: manifest SHA-256 mismatch.")
        retail = _read_csv(
            paths["total_sales"].name,
            contents[paths["total_sales"].name],
            RetailRow,
            aliases["retail"],
        )
        costs = _read_csv(
            paths["costs"].name, contents[paths["costs"].name], CostRow, {}
        )
        inventory = _read_csv(
            paths["inventory"].name, contents[paths["inventory"].name], InventoryRow, {}
        )
        ads = _read_csv(
            paths["ads"].name,
            contents[paths["ads"].name],
            AdsRow,
            aliases["ads"],
            allow_empty=True,
        )
        costs_by_asin = {r.asin: r for r in costs}
        retail_by_key = {(r.asin, r.week): r for r in retail}
        stock_by_key = {(r.asin, r.week): r for r in inventory}
        if (
            len(costs_by_asin) != len(costs)
            or len(retail_by_key) != len(retail)
            or len(stock_by_key) != len(inventory)
        ):
            raise InputError(
                "Duplicate product cost or product-week retail/inventory records."
            )
        if not any(r.week == manifest.report_week for r in retail):
            raise InputError("The manifest report week has no retail records.")
        grouped: dict[tuple[str, date], list[AdsRow]] = defaultdict(list)
        seen_ads: set[tuple[object, ...]] = set()
        for ad in ads:
            grain = (ad.day, ad.campaign, ad.ad_group, ad.sku, ad.asin)
            if grain in seen_ads:
                raise InputError("Duplicate campaign-product-day ad records.")
            seen_ads.add(grain)
            week = ad.day - timedelta(days=ad.day.weekday())
            if (ad.asin, week) not in retail_by_key:
                raise InputError(
                    f"{ad.asin} {week}: ad activity has no matching retail period."
                )
            if ad.promoted_sales is not None and ad.promoted_sales > ad.ad_sales:
                raise InputError("Promoted sales exceed total attributed sales.")
            if (
                ad.promoted_sales is not None
                and ad.halo_sales is not None
                and abs(ad.promoted_sales + ad.halo_sales - ad.ad_sales)
                > Decimal("0.02")
            ):
                raise InputError(
                    "Promoted and halo sales do not reconcile to total ad sales."
                )
            grouped[ad.asin, week].append(ad)
        joined: list[ProductWeek] = []
        for key, row in sorted(retail_by_key.items()):
            if (
                row.week.weekday()
                or not manifest.first_week <= row.week <= manifest.report_week
            ):
                raise InputError(
                    f"{row.asin}: retail week must be a Monday in the manifest period."
                )
            if row.units == 0 and row.gross_sales != 0:
                raise InputError(
                    f"{row.asin}: positive retail sales require units for costing."
                )
            if row.asin not in costs_by_asin or key not in stock_by_key:
                raise InputError(
                    f"{row.asin} {row.week}: missing cost or inventory record."
                )
            source_ads = grouped[key]
            promoted = [r.promoted_sales for r in source_ads]
            totals = AdTotals(
                spend=sum((r.spend for r in source_ads), start=Decimal(0)),
                ad_sales=sum((r.ad_sales for r in source_ads), start=Decimal(0)),
                promoted_sales=None
                if None in promoted
                else sum((r for r in promoted if r is not None), start=Decimal(0)),
                impressions=sum(r.impressions for r in source_ads),
                clicks=sum(r.clicks for r in source_ads),
                purchases=sum(r.purchases for r in source_ads),
                ad_units=sum(r.ad_units for r in source_ads),
            )
            joined.append(
                ProductWeek(row, costs_by_asin[row.asin], stock_by_key[key], totals)
            )
        hashes = {
            p.name: hashlib.sha256(contents[p.name]).hexdigest() for p in paths.values()
        }
        hashes["manifest.json"] = hashlib.sha256(manifest_bytes).hexdigest()
        return LoadedInput(
            manifest,
            tuple(joined),
            hashes,
            hashlib.sha256(json.dumps(aliases, sort_keys=True).encode()).hexdigest(),
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValidationError,
        yaml.YAMLError,
    ) as exc:
        raise InputError(f"Cannot load report input: {exc}") from exc
