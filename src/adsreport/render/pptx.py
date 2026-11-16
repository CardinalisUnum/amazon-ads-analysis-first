"""Five-slide editable review deck with native charts and full notes."""

import io
import re
import zipfile
from datetime import datetime
from typing import cast

from pptx import Presentation
from pptx.chart.data import ChartData as OfficeChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.shapes.graphfrm import GraphicFrame
from pptx.slide import Slide
from pptx.util import Inches, Pt

from adsreport.guard.numbers import METRICS
from adsreport.kpi.summary import HEADLINES
from adsreport.render.charts import ChartData, chart_data
from adsreport.render.model import DISCLOSURE, GRAY, NAVY, TEAL, ReportView, display


def stable_package(data: bytes) -> bytes:
    """Normalize OOXML metadata, including the chart data workbooks."""
    stable = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(data)) as source,
        zipfile.ZipFile(stable, "w") as target,
    ):
        for entry in source.infolist():
            content = source.read(entry.filename)
            if entry.filename.endswith(".xlsx"):
                content = stable_package(content)
            if entry.filename == "docProps/core.xml":
                content = re.sub(
                    rb"(<dcterms:(?:created|modified)[^>]*>)[^<]+",
                    rb"\g<1>2000-01-01T00:00:00Z",
                    content,
                )
            entry.date_time = (2000, 1, 1, 0, 0, 0)
            target.writestr(entry, content)
    return stable.getvalue()


def render_pptx(view: ReportView) -> bytes:
    if any(c.metrics.asin.startswith("=") for c in view.cards):
        raise ValueError("Product identifier cannot be a spreadsheet formula.")
    deck = Presentation()
    deck.slide_width = Inches(13.333)
    deck.slide_height = Inches(7.5)
    deck.core_properties.author = "Patrick Jaso"
    deck.core_properties.last_modified_by = "Patrick Jaso"
    deck.core_properties.title = "Weekly Amazon Ads review - SAMPLE DATA"
    deck.core_properties.created = datetime(2000, 1, 1)
    deck.core_properties.modified = datetime(2000, 1, 1)

    def text(
        slide: Slide,
        content: str,
        x: float,
        y: float,
        width: float,
        height: float,
        size: int = 18,
        color: str = NAVY,
        bold: bool = False,
    ) -> None:
        frame = slide.shapes.add_textbox(
            Inches(x), Inches(y), Inches(width), Inches(height)
        ).text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = 0
        frame.text = content
        for paragraph in frame.paragraphs:
            paragraph.font.name = "Arial"
            paragraph.font.size = Pt(size)
            paragraph.font.bold = bold
            paragraph.font.color.rgb = RGBColor.from_string(color)

    def slide(title: str) -> Slide:
        item = deck.slides.add_slide(deck.slide_layouts[6])
        text(item, title, 0.65, 0.45, 12, 0.7, 32, bold=True)
        text(item, f"SAMPLE DATA | {view.stamp.text}", 0.65, 6.7, 12, 0.3, 11, GRAY)
        text(item, view.report_id, 0.65, 7.02, 12, 0.25, 9, GRAY)
        return cast(Slide, item)

    def table(
        item: Slide,
        rows: list[list[str]],
        widths: list[float],
        y: float,
        height: float,
        size: int = 16,
    ) -> None:
        grid = item.shapes.add_table(
            len(rows),
            len(widths),
            Inches(0.65),
            Inches(y),
            Inches(sum(widths)),
            Inches(height),
        ).table
        for index, width in enumerate(widths):
            grid.columns[index].width = Inches(width)
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                cell = grid.cell(r, c)
                cell.text = value
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.margin_top = cell.margin_bottom = Inches(0.07)
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor.from_string(
                    NAVY if r == 0 else "FFFFFF"
                )
                for p in cell.text_frame.paragraphs:
                    p.font.name = "Arial"
                    p.font.size = Pt(size)
                    p.font.bold = r == 0
                    p.font.color.rgb = RGBColor.from_string(
                        "FFFFFF" if r == 0 else NAVY
                    )

    def chart(
        item: Slide,
        data: ChartData,
        x: float,
        y: float,
        width: float,
        height: float,
        line: bool = False,
    ) -> None:
        source = OfficeChartData()
        source.categories = data.categories
        for label, values in data.series:
            source.add_series(label, values)
        frame = cast(
            GraphicFrame,
            item.shapes.add_chart(
                XL_CHART_TYPE.LINE_MARKERS if line else XL_CHART_TYPE.COLUMN_CLUSTERED,
                Inches(x),
                Inches(y),
                Inches(width),
                Inches(height),
                source,
            ),
        )
        plot = frame.chart
        plot.has_title = True
        plot.chart_title.text_frame.text = data.title
        for p in plot.chart_title.text_frame.paragraphs:
            p.font.name = "Arial"
            p.font.size = Pt(16)
        plot.category_axis.has_title = True
        plot.category_axis.axis_title.text_frame.text = data.category_label
        plot.value_axis.has_title = True
        plot.value_axis.axis_title.text_frame.text = data.unit
        plot.category_axis.tick_labels.font.size = Pt(10)
        plot.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        plot.value_axis.tick_labels.font.size = Pt(11)
        if line:
            plot.value_axis.minimum_scale = 0
        plot.category_axis.axis_title.text_frame.paragraphs[0].font.size = Pt(11)
        plot.value_axis.axis_title.text_frame.paragraphs[0].font.size = Pt(11)
        plot.has_legend = len(data.series) > 1
        if plot.has_legend:
            plot.legend.position = XL_LEGEND_POSITION.TOP
            plot.legend.include_in_layout = True
            plot.legend.font.size = Pt(11)
        for index, series in enumerate(plot.series):
            color = RGBColor.from_string(TEAL if index == 0 else NAVY)
            series.format.line.color.rgb = color
            if not line:
                series.invert_if_negative = False
                series.format.fill.solid()
                series.format.fill.fore_color.rgb = color

    first = deck.slides.add_slide(deck.slide_layouts[6])
    text(first, "SAMPLE DATA", 0.7, 0.8, 12, 0.5, 18, TEAL, True)
    text(first, "Weekly Amazon Ads\nreview", 0.7, 1.65, 11.8, 2.0, 44, bold=True)
    text(
        first,
        f"amazon.de | EUR\nWeek beginning {view.report_week} (Europe/Berlin)",
        0.7,
        3.9,
        12,
        1.1,
        24,
    )
    text(first, view.stamp.text, 0.7, 5.3, 12, 0.55, 18, bold=True)
    text(first, DISCLOSURE, 0.7, 6.2, 12, 0.7, 14, GRAY)
    text(first, view.report_id, 0.7, 7.02, 12, 0.25, 9, GRAY)
    data = chart_data(view)
    second = slide("Portfolio results")
    rows = [["Metric", "Current week", "Change vs prior"]] + [
        [
            METRICS[m][0],
            display(m, view.current.values[m]),
            view.delta(m).removesuffix(" vs prior week"),
        ]
        for m in HEADLINES
    ]
    table(second, rows, [3.3, 2.1, 2.0], 1.55, 3.9, 16)
    chart(second, data["tacos"], 8.2, 1.5, 4.5, 3.95, True)
    text(
        second,
        "TACoS uses ad spend / net retail revenue. Total sales includes VAT. "
        "Monetary changes are EUR; TACoS change is percentage points.",
        0.65,
        5.8,
        12,
        0.7,
        15,
        GRAY,
    )
    third = slide("Products for review")
    rows = [["Product / sample ASIN", "Severity", "Rules", "Review focus"]] + [
        [
            c.name + "\n" + c.metrics.asin,
            c.flags[0].severity.title(),
            ", ".join(f.rule_id for f in c.flags),
            c.note.planned_change_to_review,
        ]
        for c in view.priorities
    ]
    if len(rows) == 1:
        rows.append(["No rule flags", "", "", "Continue routine human review."])
    table(third, rows, [3.5, 1.1, 1.3, 6.1], 1.4, 4.9, 14)
    fourth = slide("Product economics")
    chart(fourth, data["contribution"], 0.6, 1.5, 6.1, 4.8)
    chart(fourth, data["acos"], 6.85, 1.5, 5.9, 4.8)
    fifth = slide("Review items and approval")
    selected = view.priorities[:2] or view.cards[:2]
    for index, card in enumerate(selected):
        y = 1.45 + index * 1.9
        text(
            fifth, f"{card.name} ({card.metrics.asin})", 0.7, y, 12, 0.45, 21, bold=True
        )
        text(
            fifth,
            card.note.what_happened + "\n" + card.note.planned_change_to_review,
            0.7,
            y + 0.5,
            12,
            0.85,
            17,
        )
        text(
            fifth,
            f"{card.note.label} | {card.note.reason}",
            0.7,
            y + 1.38,
            12,
            0.35,
            12,
            GRAY,
        )
    text(
        fifth,
        "Human review and delivery approval remain required. Causes, targets "
        "and review dates are unknown. Full product commentary and source "
        "references are in the speaker notes.",
        0.7,
        5.45,
        12,
        0.9,
        17,
    )
    notes = fifth.notes_slide.notes_text_frame
    if notes is None:
        raise ValueError("PowerPoint notes placeholder is unavailable.")
    notes.text = "\n\n".join(
        f"{c.name} | {c.metrics.asin} | SKU {c.sku} | LEGO set {c.set_number}\n"
        f"{c.note.label} | {c.note.reason}\n{c.note.what_happened}\n"
        f"{c.note.likely_cause}\n{c.note.planned_change_to_review}\n"
        f"{c.note.target_and_review_date}\nConfidence: {c.note.confidence}\n"
        f"Catalog: {c.source_url}"
        for c in view.cards
    )
    first.notes_slide.notes_text_frame.text = (
        DISCLOSURE + "\nCatalog references describe identity only. "
        "All financial performance and stock are simulated."
    )
    stream = io.BytesIO()
    deck.save(stream)
    return stable_package(stream.getvalue())
