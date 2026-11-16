"""Self-contained HTML with autoescaped data and trusted local chart SVGs."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

from adsreport.guard.numbers import METRICS
from adsreport.kpi.summary import HEADLINES
from adsreport.render.model import (
    ASSUMPTIONS_URL,
    DISCLOSURE,
    ReportView,
    display,
    flag_evidence,
    flag_thresholds,
)


def render_html(view: ReportView, charts: dict[str, bytes]) -> bytes:
    environment = Environment(
        loader=FileSystemLoader(Path(__file__).with_name("templates")),
        autoescape=select_autoescape(("html",)),
        undefined=StrictUndefined,
    )
    svg = {
        name: Markup("<svg" + charts[f"SAMPLE_{name}.svg"].decode().split("<svg", 1)[1])
        for name in ("tacos", "contribution", "acos")
    }
    # Only program-generated chart bytes are marked safe. All report text escapes.
    return (
        environment.get_template("report.html")
        .render(
            report=view,
            display=display,
            metrics=METRICS,
            headlines=HEADLINES,
            charts=svg,
            disclosure=DISCLOSURE,
            assumptions_url=ASSUMPTIONS_URL,
            flag_evidence=flag_evidence,
            flag_thresholds=flag_thresholds,
        )
        .encode("utf-8")
    )
