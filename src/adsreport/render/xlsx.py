"""Six-sheet static workbook with numeric cells and native Excel charts."""

import io
from datetime import datetime

import xlsxwriter  # type: ignore[import-untyped]

from adsreport.guard.numbers import METRICS
from adsreport.kpi.summary import HEADLINES
from adsreport.render.charts import chart_data
from adsreport.render.model import (
    ASSUMPTIONS_URL,
    DISCLOSURE,
    GRAY,
    LIGHT,
    NAVY,
    SEVERITY,
    TEAL,
    ReportView,
    flag_evidence,
    flag_thresholds,
)


def render_xlsx(view: ReportView) -> bytes:
    stream = io.BytesIO()
    book = xlsxwriter.Workbook(
        stream,
        {"in_memory": True, "strings_to_formulas": False, "strings_to_urls": False},
    )
    book.set_properties(
        {
            "title": "Weekly Amazon Ads review - SAMPLE DATA",
            "author": "Patrick Jaso",
            "created": datetime(2000, 1, 1),
            "comments": view.report_id,
        }
    )
    base = {
        "font_name": "Arial",
        "font_size": 11,
        "font_color": NAVY,
        "valign": "vcenter",
    }
    text = book.add_format(base)
    wrapped = book.add_format(base | {"text_wrap": True, "valign": "top"})
    muted = book.add_format(base | {"font_color": GRAY, "font_size": 10})
    title = book.add_format(base | {"font_size": 18, "bold": True})
    header = book.add_format(
        base
        | {"bold": True, "bg_color": NAVY, "font_color": "FFFFFF", "text_wrap": True}
    )
    formats = {
        unit: book.add_format(base | {"num_format": code})
        for unit, code in {
            "EUR": '"EUR "#,##0.00;[Red]"EUR "-#,##0.00',
            "percent": '0.00"%"',
            "percentage_points": '0.00" pp"',
            "ratio": '0.00"x"',
            "count": "#,##0",
            "units": "#,##0",
            "days": '0.00" days"',
        }.items()
    }
    date_format = book.add_format(base | {"num_format": "dd mmm yyyy"})
    sheets = {
        name: book.add_worksheet(name)
        for name in (
            "Summary",
            "Priorities",
            "Products",
            "Charts",
            "Commentary",
            "Run info",
        )
    }
    for name, sheet in sheets.items():
        sheet.hide_gridlines(2)
        sheet.set_default_row(21)
        sheet.set_column("A:A", 3)
        sheet.set_column("B:U", 15, text)
        sheet.set_landscape()
        sheet.set_paper(9)
        sheet.fit_to_pages(1, 0)
        sheet.set_header("&L" + view.stamp.text + "&RSAMPLE DATA")
        sheet.set_footer("&L" + view.report_id + "&RPage &P of &N")
        sheet.write(
            "B2", "Weekly Amazon Ads review" if name == "Summary" else name, title
        )
        sheet.write(
            "B3",
            f"{view.stamp.text} | SAMPLE DATA | Week {view.report_week} "
            "| amazon.de | EUR",
            muted,
        )
        sheet.set_tab_color(TEAL if name == "Summary" else NAVY)
    summary = sheets["Summary"]
    summary.set_column("B:T", 8)
    for index, metric in enumerate(HEADLINES):
        col = 1 + index * 4
        summary.merge_range(5, col, 5, col + 2, METRICS[metric][0], wrapped)
        summary.set_row(5, 36)
        value = view.current.values[metric]
        value_format = book.add_format(
            base
            | {
                "font_size": 20,
                "bold": True,
                "num_format": formats[METRICS[metric][1]].num_format,
            }
        )
        summary.merge_range(
            6,
            col,
            7,
            col + 2,
            float(value) if value is not None else "N/A",
            value_format,
        )
        summary.merge_range(8, col, 9, col + 2, view.delta(metric), wrapped)
    summary.merge_range(
        "B12:T13",
        "TACoS = ad spend / net retail revenue. Total sales includes VAT. "
        "Monetary changes are EUR; TACoS change is percentage points. "
        "Static report snapshot.",
        wrapped,
    )
    summary.merge_range(
        "B15:T16",
        f"{len(view.analysis.flags)} flags across "
        f"{len({f.asin for f in view.analysis.flags})} products. "
        "See Priorities and Commentary for human review.",
        wrapped,
    )

    priorities = sheets["Priorities"]
    headings = [
        "Priority rank",
        "Product",
        "Sample ASIN",
        "Severity",
        "Rule",
        "Evidence and thresholds",
        "Review reason",
    ]
    priorities.write_row(4, 1, headings, header)
    priorities.set_column("C:C", 34)
    priorities.set_column("G:H", 65, wrapped)
    ranks = {p.metrics.asin: i + 1 for i, p in enumerate(view.priorities)}
    cards = {p.metrics.asin: p for p in view.cards}
    for row, flag in enumerate(view.analysis.flags, 5):
        priorities.write_row(
            row,
            1,
            [
                ranks.get(flag.asin, "Outside top priorities"),
                cards[flag.asin].name,
                flag.asin,
                flag.severity.title(),
                flag.rule_id,
                flag_evidence(flag) + "\nThresholds: " + flag_thresholds(flag),
                flag.reason,
            ],
            wrapped,
        )
        priorities.set_row(row, 100)
    for severity, color in SEVERITY.items():
        priorities.conditional_format(
            5,
            4,
            max(5, 4 + len(view.analysis.flags)),
            4,
            {
                "type": "text",
                "criteria": "containing",
                "value": severity.title(),
                "format": book.add_format(
                    base | {"font_color": color, "bold": True, "bg_color": LIGHT}
                ),
            },
        )
    priorities.freeze_panes(5, 4)
    priorities.autofilter(4, 1, max(5, 4 + len(view.analysis.flags)), 7)

    products = sheets["Products"]
    keys = list(view.records[0].values)
    product_headers = [
        "Product",
        "Sample ASIN",
        "Sample SKU",
        "Manufacturer set",
        "Week",
        "Lifecycle",
        *[METRICS[k][0] + " (" + METRICS[k][1] + ")" for k in keys],
        "Unavailable metrics",
    ]
    products.write_row(4, 1, product_headers, header)
    products.set_row(4, 58)
    products.set_column(1, 1, 34)
    products.set_column(2, len(product_headers), 22)
    products.set_column(len(product_headers), len(product_headers), 85, wrapped)
    for row, record in enumerate(view.records, 5):
        card = cards.get(record.asin)
        products.write_row(
            row,
            1,
            [
                card.name if card else record.asin,
                record.asin,
                card.sku if card else "Unavailable",
                card.set_number if card else "Unavailable",
            ],
            text,
        )
        products.write_datetime(
            row, 5, datetime.combine(record.week, datetime.min.time()), date_format
        )
        products.write(row, 6, record.lifecycle_phase, text)
        for col, key in enumerate(keys, 7):
            value = record.values[key]
            products.write(
                row,
                col,
                float(value) if value is not None else "N/A",
                formats[METRICS[key][1]],
            )
        products.write(
            row,
            7 + len(keys),
            "; ".join(f"{k}: {v}" for k, v in record.undefined_reasons.items()),
            wrapped,
        )
        products.set_row(row, 32)
    products.freeze_panes(5, 5)
    products.autofilter(4, 1, 4 + len(view.records), len(product_headers))

    charts = sheets["Charts"]
    for index, (name, data) in enumerate(chart_data(view).items()):
        start = 68 + index * 15
        charts.write_row(
            start,
            1,
            [data.category_label, *[label for label, _ in data.series]],
            header,
        )
        charts.write_column(start + 1, 1, data.categories, text)
        chart = book.add_chart({"type": "line" if name == "tacos" else "column"})
        for series_index, (label, values) in enumerate(data.series):
            col = 2 + series_index
            charts.write_column(start + 1, col, values, text)
            chart.add_series(
                {
                    "name": label,
                    "categories": ["Charts", start + 1, 1, start + len(values), 1],
                    "values": ["Charts", start + 1, col, start + len(values), col],
                    "line": {"color": TEAL if series_index == 0 else NAVY},
                    "fill": {"color": TEAL if series_index == 0 else NAVY},
                }
            )
        chart.set_title({"name": data.title})
        chart.set_x_axis({"name": data.category_label, "num_font": {"rotation": -30}})
        chart.set_y_axis(
            {
                "name": data.unit,
                "major_gridlines": {"visible": True},
                **({"min": 0} if name == "tacos" else {}),
            }
        )
        chart.set_legend(
            {"position": "bottom"} if len(data.series) > 1 else {"none": True}
        )
        chart.set_size({"width": 900, "height": 350})
        chart.set_style(10)
        charts.insert_chart(5 + index * 21, 1, chart)
        if name == "tacos":
            summary_chart = book.add_chart({"type": "line"})
            summary_chart.add_series(
                {
                    "name": "TACoS",
                    "categories": [
                        "Charts",
                        start + 1,
                        1,
                        start + len(data.categories),
                        1,
                    ],
                    "values": ["Charts", start + 1, 2, start + len(data.categories), 2],
                    "line": {"color": TEAL},
                }
            )
            summary_chart.set_title({"name": data.title})
            summary_chart.set_x_axis({"name": data.category_label})
            summary_chart.set_y_axis({"name": data.unit, "min": 0})
            summary_chart.set_legend({"none": True})
            summary_chart.set_size({"width": 900, "height": 340})
            summary.insert_chart("B19", summary_chart)

    commentary = sheets["Commentary"]
    commentary.write_row(
        4,
        1,
        [
            "Product",
            "Sample ASIN",
            "Source",
            "Reason",
            "What happened",
            "Likely cause",
            "Review item",
            "Target and review date",
            "Confidence",
        ],
        header,
    )
    commentary.set_column("B:B", 34)
    commentary.set_column("D:E", 24)
    commentary.set_column("F:I", 50, wrapped)
    for row, card in enumerate(view.cards, 5):
        note = card.note
        commentary.write_row(
            row,
            1,
            [
                card.name,
                note.asin,
                note.label,
                note.reason,
                note.what_happened,
                note.likely_cause,
                note.planned_change_to_review,
                note.target_and_review_date,
                note.confidence,
            ],
            wrapped,
        )
        commentary.set_row(row, 115)
    commentary.freeze_panes(5, 3)
    commentary.autofilter(4, 1, 4 + len(view.cards), 9)

    info = sheets["Run info"]
    info.set_column("B:B", 30)
    info.set_column("C:C", 105, wrapped)
    entries = [
        ("Report ID", view.report_id),
        ("Status", view.stamp.text),
        ("Data label", "SAMPLE DATA"),
        ("Market / currency", "amazon.de / EUR"),
        ("Week beginning", view.report_week.isoformat()),
        ("Scope", DISCLOSURE),
        (
            "Artifact behavior",
            "Static snapshot. Regenerate through Python to update metrics and charts.",
        ),
        ("Assumptions", ASSUMPTIONS_URL),
        ("AI outcome", view.commentary.request_status),
        ("AI attempts", view.commentary.attempts),
        ("Guard rejections", view.commentary.guard_rejections),
        *view.source_hashes.items(),
        *view.config_hashes.items(),
    ]
    for row, (label, entry_value) in enumerate(entries, 5):
        info.write(row, 1, label, text)
        info.write(row, 2, entry_value, wrapped)
        info.set_row(row, 34)
    catalog_start = 6 + len(entries)
    info.write_row(
        catalog_start, 1, ["Sample ASIN", "Official catalog reference"], header
    )
    for row, card in enumerate(view.cards, catalog_start + 1):
        info.write(row, 1, card.metrics.asin, text)
        if card.source_url:
            info.write_url(row, 2, card.source_url, muted, card.source_url)
    book.close()
    return stream.getvalue()
