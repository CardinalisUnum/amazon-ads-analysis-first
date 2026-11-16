"""Deterministic labelled charts with shared data for native Office equivalents."""

import io
from dataclasses import dataclass

import matplotlib
from matplotlib.figure import Figure

from adsreport.render.model import NAVY, SEVERITY, TEAL, ReportView

matplotlib.use("Agg")


@dataclass(frozen=True)
class ChartData:
    title: str
    categories: tuple[str, ...]
    series: tuple[tuple[str, tuple[float | None, ...]], ...]
    unit: str
    category_label: str


def chart_data(view: ReportView) -> dict[str, ChartData]:
    def number(value: object) -> float | None:
        return float(str(value)) if value is not None else None

    return {
        "tacos": ChartData(
            "TACoS trend",
            tuple(w.week.strftime("%d %b") for w in view.portfolio),
            (("TACoS", tuple(number(w.values["tacos_pct"]) for w in view.portfolio)),),
            "% of net retail revenue",
            "Week beginning (Europe/Berlin)",
        ),
        "contribution": ChartData(
            "Contribution after ads by product",
            tuple(c.metrics.asin for c in view.cards),
            (
                (
                    "Contribution after ads",
                    tuple(
                        number(c.metrics.values["contribution_after_ads_eur"])
                        for c in view.cards
                    ),
                ),
            ),
            "EUR",
            "Sample ASIN",
        ),
        "acos": ChartData(
            "ACoS and break-even ACoS",
            tuple(c.metrics.asin for c in view.cards),
            tuple(
                (label, tuple(number(c.metrics.values[metric]) for c in view.cards))
                for label, metric in (
                    ("ACoS", "acos_pct"),
                    ("Break-even ACoS", "break_even_acos_pct"),
                )
            ),
            "%",
            "Sample ASIN",
        ),
    }


def render_charts(view: ReportView) -> dict[str, bytes]:
    outputs = {}
    with matplotlib.rc_context(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "svg.hashsalt": "adsreport",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": "#" + NAVY,
            "text.color": "#" + NAVY,
        }
    ):
        for name, data in chart_data(view).items():
            figure = Figure(figsize=(10, 3.4), layout="constrained")
            axes = figure.subplots()
            positions = list(range(len(data.categories)))
            for index, (label, values) in enumerate(data.series):
                y = [float("nan") if v is None else v for v in values]
                if name == "tacos":
                    axes.plot(positions, y, color="#" + TEAL, marker="o", label=label)
                else:
                    width = 0.36 if len(data.series) > 1 else 0.65
                    x = [
                        p + (index - 0.5) * width if len(data.series) > 1 else p
                        for p in positions
                    ]
                    colors = (
                        [
                            "#" + SEVERITY["high"]
                            if v is not None and v < 0
                            else "#" + TEAL
                            for v in values
                        ]
                        if name == "contribution"
                        else "#" + (TEAL if index == 0 else NAVY)
                    )
                    axes.bar(x, y, width=width, label=label, color=colors)
            axes.set_xticks(
                positions,
                data.categories,
                rotation=25 if name != "tacos" else 0,
                ha="right" if name != "tacos" else "center",
            )
            axes.set_ylabel(data.unit)
            axes.set_xlabel(data.category_label)
            axes.set_title(data.title, loc="left", fontweight="bold", pad=14)
            axes.axhline(0, color="#A6B5C0", linewidth=0.6)
            axes.grid(axis="y", alpha=0.15)
            axes.set_axisbelow(True)
            if len(data.series) > 1:
                axes.legend(frameon=False, loc="upper right")
            figure.text(
                0.995, 0.01, "SAMPLE DATA", ha="right", fontsize=8, color="#526579"
            )
            for suffix in ("svg", "png"):
                stream = io.BytesIO()
                metadata = (
                    {"Date": None} if suffix == "svg" else {"Software": "adsreport"}
                )
                figure.savefig(stream, format=suffix, dpi=150, metadata=metadata)
                content = stream.getvalue()
                if suffix == "svg":
                    content = (
                        content.replace(b'id="', f'id="{name}-'.encode())
                        .replace(b'href="#', f'href="#{name}-'.encode())
                        .replace(b"url(#", f"url(#{name}-".encode())
                    )
                outputs[f"SAMPLE_{name}.{suffix}"] = content
    return outputs
