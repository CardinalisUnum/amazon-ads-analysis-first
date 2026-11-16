"""Numerical draft output, shared foundation for later rules and renderers."""

import csv
import hashlib
import io
import json
from collections.abc import Callable, Mapping
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from adsreport.ai.commentary import generate_commentary
from adsreport.artifacts import publish_bundle
from adsreport.config import Configuration
from adsreport.io.loader import InputError, load_inputs
from adsreport.kpi.engine import ProductMetrics, calculate_report
from adsreport.periods import latest_mature_week
from adsreport.render.charts import render_charts
from adsreport.render.html import render_html
from adsreport.render.model import ReportView, make_view, view_manifest
from adsreport.render.pdf import render_pdf
from adsreport.render.pptx import render_pptx
from adsreport.render.xlsx import render_xlsx
from adsreport.rules.engine import evaluate_rules
from adsreport.runlog import RunIdentity


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
    folder: Path,
    destination: Path,
    config_dir: Path,
    config: Configuration,
    *,
    no_ai: bool = True,
    run: RunIdentity | None = None,
    on_stage: Callable[[str], None] | None = None,
) -> Path:
    def mark(name: str) -> None:
        if on_stage is not None:
            on_stage(name)

    mark("load")
    loaded = load_inputs(folder, config_dir / "column_map.yaml")
    if loaded.manifest.vat_rate != Decimal(str(config.settings.vat_rate)):
        raise InputError("Manifest and configured VAT rates differ.")
    latest = None
    if run is not None:
        latest = latest_mature_week(
            run.started_at,
            config.settings.attribution_days,
            config.settings.reporting_latency_days,
        )
        if loaded.manifest.report_week > latest:
            raise InputError(
                "Report week is not mature after attribution and latency. "
                "Choose an older week."
            )
    mark("compute")
    results = calculate_report(loaded.rows, loaded.manifest.vat_rate)
    mark("rules")
    analysis = evaluate_rules(
        results,
        config.thresholds,
        loaded.manifest.report_week,
        config.settings.priority_products,
    )
    mark("commentary")
    commentary = generate_commentary(
        results,
        analysis,
        no_ai=no_ai,
        model=config.settings.gemini_model,
        limit=config.settings.commentary_products,
    )
    config_hashes = {
        "validated_configuration": hashlib.sha256(
            config.model_dump_json().encode()
        ).hexdigest(),
        "normalized_column_map": loaded.column_map_hash,
    }
    report: dict[str, object] = {
        "data_label": loaded.manifest.data_label,
        "status": "DRAFT",
        "stage": "outputs",
        "analysis": analysis.model_dump(mode="json"),
        "commentary": commentary.model_dump(mode="json"),
        "marketplace": loaded.manifest.marketplace,
        "currency": loaded.manifest.currency,
        "vat_rate": str(loaded.manifest.vat_rate),
        "report_week": loaded.manifest.report_week.isoformat(),
        "source_hashes": loaded.source_hashes,
        "config_hashes": config_hashes,
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
    if run is not None:
        report["run"] = run.model_dump(mode="json")
        report["maturity"] = {
            "latest_mature_week": str(latest),
            "fixed_sample_period": True,
            "attribution_days": config.settings.attribution_days,
            "latency_days": config.settings.reporting_latency_days,
        }
    mark("render")
    view = make_view(
        results,
        analysis,
        commentary,
        loaded.source_hashes,
        config_hashes,
        {r.asin: r.model_dump() for r in loaded.catalog},
        json.dumps(report, sort_keys=True),
    )
    view = replace(view, run=run)
    report["presentation"] = view_manifest(view)
    files = render_bundle(view, report, kpi_csv(results))
    mark("publish")
    return publish_bundle(destination, files)


def render_bundle(
    view: ReportView,
    report: Mapping[str, object],
    csv_content: bytes,
    *,
    charts: dict[str, bytes] | None = None,
    extra: dict[str, bytes] | None = None,
) -> dict[str, bytes]:
    status = "APPROVED" if view.stamp.approved_at is not None else "DRAFT"
    if report["status"] != status:
        raise ValueError("Report and presentation status differ.")
    charts = render_charts(view) if charts is None else charts
    html = render_html(view, charts)
    files = {
        **charts,
        "SAMPLE_report.html": html,
        "SAMPLE_report.pdf": render_pdf(html),
        "SAMPLE_report.xlsx": render_xlsx(view),
        "SAMPLE_report.pptx": render_pptx(view),
        "SAMPLE_kpis.csv": csv_content,
        "report.json": (json.dumps(report, indent=2, allow_nan=False) + "\n").encode(
            "utf-8"
        ),
    }
    if extra:
        files.update(extra)
    files["artifacts.json"] = (
        json.dumps(
            {
                "report_id": view.report_id,
                "status": status,
                "data_label": "SAMPLE DATA",
                "sha256": {
                    name: hashlib.sha256(content).hexdigest()
                    for name, content in files.items()
                },
            },
            indent=2,
        )
        + "\n"
    ).encode()
    return files
