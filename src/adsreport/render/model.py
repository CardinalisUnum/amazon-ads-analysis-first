"""Presentation data and a content-derived identity, without renderer calculations."""

import hashlib
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

from adsreport.ai.models import Commentary, Note
from adsreport.guard.numbers import METRICS
from adsreport.kpi.engine import ProductMetrics
from adsreport.kpi.summary import PortfolioWeek, summarize
from adsreport.rules.engine import Flag, RuleReport

NAVY = "17324D"
TEAL = "087F8C"
GRAY = "526579"
LIGHT = "EEF4F7"
SEVERITY = {"high": "AC2638", "medium": "926009", "low": "32657D"}
ASSUMPTIONS_URL = "https://github.com/CardinalisUnum/amazon-ads-analysis-first/blob/main/docs/ASSUMPTIONS.md"
DISCLOSURE = (
    "Independent retailer simulation using LEGO catalog references. "
    "No brand affiliation. All performance is SAMPLE DATA."
)


def display(metric: str, value: Decimal | None, *, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    unit = METRICS[metric][1]
    places = Decimal(1) if unit in {"count", "units"} else Decimal("0.01")
    rounded = value.quantize(places, rounding=ROUND_HALF_UP)
    number = format(rounded, ",.0f" if places == 1 else ",.2f")
    if signed and rounded > 0:
        number = "+" + number
    if unit == "EUR":
        return "EUR " + number
    return (
        number
        + {
            "percent": "%",
            "percentage_points": " pp",
            "ratio": "x",
            "days": " days",
            "count": "",
            "units": " units",
        }[unit]
    )


def flag_evidence(flag: Flag) -> str:
    parts = []
    for key, value in flag.evidence.items():
        metric = key.split("[", 1)[0]
        label = METRICS[metric][0] if metric in METRICS else key.replace("_", " ")
        if "[" in key:
            label += " (" + key.split("[", 1)[1].removesuffix("]") + ")"
        if isinstance(value, date):
            rendered = value.isoformat()
        elif metric in METRICS:
            rendered = display(metric, value)
        else:
            rendered = str(value) + (" days" if key.endswith("_days") else "")
        parts.append(label + " " + rendered)
    return "; ".join(parts)


def flag_thresholds(flag: Flag) -> str:
    parts = []
    for key, value in flag.thresholds.items():
        if key in METRICS:
            label = METRICS[key][0]
            rendered = display(key, value)
        else:
            label = key.replace("_", " ")
            suffix = ""
            for ending, unit in (
                ("_pct", "%"),
                ("_pp", " pp"),
                ("_weeks", " weeks"),
                ("_days", " days"),
                ("_fraction", "x"),
                ("_transitions", " transitions"),
            ):
                if key.endswith(ending):
                    label = key.removesuffix(ending).replace("_", " ")
                    suffix = unit
                    break
            rendered = (
                format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")
                + suffix
            )
        parts.append(label + " " + rendered)
    return "; ".join(parts)


@dataclass(frozen=True)
class Stamp:
    approved_by: str | None = None
    approved_at: datetime | None = None

    def __post_init__(self) -> None:
        if (self.approved_by is None) != (self.approved_at is None):
            raise ValueError("Approval display needs reviewer and timestamp together.")
        if self.approved_at is not None and (
            not self.approved_by
            or not self.approved_by.strip()
            or self.approved_at.utcoffset() is None
        ):
            raise ValueError(
                "Approval display needs reviewer and timezone-aware timestamp."
            )

    @property
    def text(self) -> str:
        if self.approved_at is None:
            return "DRAFT"
        return f"APPROVED by {self.approved_by} at {self.approved_at.isoformat()}"


@dataclass(frozen=True)
class ProductCard:
    metrics: ProductMetrics
    name: str
    sku: str
    set_number: str
    source_url: str
    flags: tuple[Flag, ...]
    note: Note


@dataclass(frozen=True)
class ReportView:
    report_id: str
    report_week: date
    records: tuple[ProductMetrics, ...]
    cards: tuple[ProductCard, ...]
    portfolio: tuple[PortfolioWeek, ...]
    analysis: RuleReport
    commentary: Commentary
    source_hashes: dict[str, str]
    config_hashes: dict[str, str]
    stamp: Stamp = Stamp()

    @property
    def current(self) -> PortfolioWeek:
        return next(w for w in self.portfolio if w.week == self.report_week)

    @property
    def priorities(self) -> tuple[ProductCard, ...]:
        by_asin = {p.metrics.asin: p for p in self.cards}
        return tuple(by_asin[p.asin] for p in self.analysis.priorities)

    def delta(self, metric: str) -> str:
        value = self.current.deltas[metric]
        key = "acos_pct_wow_pp" if metric == "tacos_pct" else metric
        return display(key, value, signed=True) + " vs prior week"


def make_view(
    records: list[ProductMetrics],
    analysis: RuleReport,
    commentary: Commentary,
    source_hashes: dict[str, str],
    config_hashes: dict[str, str],
    catalog: dict[str, dict[str, str]],
    identity_payload: str,
) -> ReportView:
    notes = {n.asin: n for n in commentary.notes}
    cards = []
    for metrics in records:
        if metrics.week != analysis.report_week:
            continue
        row = catalog.get(metrics.asin, {})
        cards.append(
            ProductCard(
                metrics,
                row.get("product_name", metrics.asin),
                row.get("sku", "Unavailable"),
                row.get("set_number", "Unavailable"),
                row.get("source_url", ""),
                tuple(f for f in analysis.flags if f.asin == metrics.asin),
                notes[metrics.asin],
            )
        )
    digest = hashlib.sha256(identity_payload.encode()).hexdigest()[:16]
    return ReportView(
        f"SAMPLE-{analysis.report_week:%Y%m%d}-{digest}",
        analysis.report_week,
        tuple(records),
        tuple(cards),
        summarize(records),
        analysis,
        commentary,
        source_hashes,
        config_hashes,
    )


def view_manifest(view: ReportView) -> dict[str, object]:
    """Common facts stored in JSON and represented in each output."""
    return {
        "report_id": view.report_id,
        "portfolio": [
            {
                "week": w.week.isoformat(),
                "values": {
                    k: str(v) if v is not None else None for k, v in w.values.items()
                },
                "deltas": {
                    k: str(v) if v is not None else None for k, v in w.deltas.items()
                },
                "comparison_reason": w.comparison_reason,
            }
            for w in view.portfolio
        ],
        "catalog": [
            {
                "asin": c.metrics.asin,
                "name": c.name,
                "sku": c.sku,
                "set_number": c.set_number,
                "source_url": c.source_url,
            }
            for c in view.cards
        ],
    }
