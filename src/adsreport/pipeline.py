"""Numerical draft output, shared foundation for later rules and renderers."""

import csv
import hashlib
import io
import json
from decimal import Decimal
from pathlib import Path

from adsreport.artifacts import publish_bundle
from adsreport.config import Configuration
from adsreport.io.loader import InputError, load_inputs
from adsreport.kpi.engine import ProductMetrics, calculate_report
from adsreport.rules.engine import evaluate_rules


def kpi_csv(results: list[ProductMetrics]) -> bytes:
    output = io.StringIO(newline="")
    fields = [
        "data_label",
        "status",
        "asin",
        "week",
        "lifecycle_phase",
        *results[0].values,
    ]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for result in results:
        row = {
            "data_label": "SAMPLE DATA",
            "status": "DRAFT",
            "asin": result.asin,
            "week": result.week.isoformat(),
            "lifecycle_phase": result.lifecycle_phase,
        }
        row.update(
            {
                name: str(value) if value is not None else ""
                for name, value in result.values.items()
            }
        )
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


def run_numerical_draft(
    folder: Path, destination: Path, config_dir: Path, config: Configuration
) -> Path:
    loaded = load_inputs(folder, config_dir / "column_map.yaml")
    if loaded.manifest.vat_rate != Decimal(str(config.settings.vat_rate)):
        raise InputError("Manifest and configured VAT rates differ.")
    results = calculate_report(loaded.rows, loaded.manifest.vat_rate)
    analysis = evaluate_rules(
        results,
        config.thresholds,
        loaded.manifest.report_week,
        config.settings.priority_products,
    )
    report = {
        "data_label": loaded.manifest.data_label,
        "status": "DRAFT",
        "stage": "rules",
        "analysis": analysis.model_dump(mode="json"),
        "marketplace": loaded.manifest.marketplace,
        "currency": loaded.manifest.currency,
        "vat_rate": str(loaded.manifest.vat_rate),
        "report_week": loaded.manifest.report_week.isoformat(),
        "source_hashes": loaded.source_hashes,
        "config_hashes": {
            "validated_configuration": hashlib.sha256(
                config.model_dump_json().encode()
            ).hexdigest(),
            "normalized_column_map": loaded.column_map_hash,
        },
        "products": [
            {
                "asin": r.asin,
                "week": r.week.isoformat(),
                "lifecycle_phase": r.lifecycle_phase,
                "launch_start_date": r.launch_start_date.isoformat(),
                "values": {
                    name: str(value) if value is not None else None
                    for name, value in r.values.items()
                },
                "undefined_reasons": r.undefined_reasons,
            }
            for r in results
        ],
    }
    return publish_bundle(
        destination,
        {
            "SAMPLE_kpis.csv": kpi_csv(results),
            "report.json": (
                json.dumps(report, indent=2, allow_nan=False) + "\n"
            ).encode("utf-8"),
        },
    )
