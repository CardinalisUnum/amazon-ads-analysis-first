import hashlib
import io
import json
import zipfile
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree as ET

import openpyxl
import pytest
from pptx import Presentation
from pypdf import PdfReader

from adsreport.ai.commentary import generate_commentary
from adsreport.cli import main
from adsreport.config import load_config
from adsreport.io.loader import load_inputs
from adsreport.kpi.engine import ProductMetrics, calculate_report
from adsreport.kpi.summary import HEADLINES, summarize
from adsreport.render.charts import chart_data, render_charts
from adsreport.render.html import render_html
from adsreport.render.model import Stamp, display, make_view
from adsreport.render.pdf import render_pdf
from adsreport.render.pptx import render_pptx
from adsreport.render.xlsx import render_xlsx
from adsreport.rules.engine import evaluate_rules


@pytest.fixture(scope="module")
def view():
    loaded = load_inputs(Path("data/sample"), Path("config/column_map.yaml"))
    records = calculate_report(loaded.rows, loaded.manifest.vat_rate)
    analysis = evaluate_rules(
        records, load_config(Path("config")).thresholds, loaded.manifest.report_week
    )
    commentary = generate_commentary(records, analysis, no_ai=True)
    return make_view(
        records,
        analysis,
        commentary,
        loaded.source_hashes,
        {},
        {r.asin: r.model_dump() for r in loaded.catalog},
        "test-sample",
    )


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    output = tmp_path_factory.mktemp("reports") / "draft"
    assert main(["run", "--out", str(output), "--no-ai"]) == 0
    return output


def test_portfolio_uses_sums_and_differences():
    def product(asin, week, spend, net):
        return ProductMetrics(
            asin,
            week,
            "maturity",
            date(2025, 1, 1),
            {
                "ad_spend_eur": Decimal(spend),
                "net_revenue_eur": Decimal(net),
                "ad_sales_eur": Decimal("20"),
                "total_sales_gross_eur": Decimal("119"),
                "contribution_after_ads_eur": Decimal("-5"),
            },
            {},
        )

    previous = date(2026, 10, 19)
    current = date(2026, 10, 26)
    records = [
        product("A", previous, "10", "100"),
        product("B", previous, "10", "900"),
        product("A", current, "20", "100"),
        product("B", current, "10", "900"),
    ]
    summaries = summarize(records)
    assert summaries[-1].values["tacos_pct"] == 3
    assert summaries[-1].deltas["tacos_pct"] == 1
    assert summaries[-1].deltas["ad_spend_eur"] == 10
    assert summaries[-1].deltas["contribution_after_ads_eur"] == 0
    assert summarize(records[:-1])[-1].deltas["ad_spend_eur"] is None
    gap = [
        replace(r, week=date(2026, 11, 2)) if r.week == current else r for r in records
    ]
    assert summarize(gap)[-1].deltas["tacos_pct"] is None
    zero = product("A", current, "10", "0")
    assert summarize([zero])[0].values["tacos_pct"] is None
    missing = replace(zero, values=zero.values | {"ad_spend_eur": None})
    assert summarize([missing])[0].values["ad_spend_eur"] is None


def test_bundle_fingerprints_and_four_formats(bundle):
    manifest = json.loads((bundle / "artifacts.json").read_text())
    assert manifest["status"] == "DRAFT" and manifest["data_label"] == "SAMPLE DATA"
    assert set(manifest["sha256"]) == {p.name for p in bundle.iterdir()} - {
        "artifacts.json"
    }
    for name, digest in manifest["sha256"].items():
        assert hashlib.sha256((bundle / name).read_bytes()).hexdigest() == digest
    assert all(
        (bundle / ("SAMPLE_report." + suffix)).stat().st_size > 1000
        for suffix in ("xlsx", "html", "pdf", "pptx")
    )


def test_headlines_match_in_all_four_outputs(bundle):
    report = json.loads((bundle / "report.json").read_text())
    week = next(
        w
        for w in report["presentation"]["portfolio"]
        if w["week"] == report["report_week"]
    )
    html = (bundle / "SAMPLE_report.html").read_text(encoding="utf-8")
    pdf = PdfReader(bundle / "SAMPLE_report.pdf")
    pdf_text = "\n".join(p.extract_text() for p in pdf.pages)
    deck = Presentation(bundle / "SAMPLE_report.pptx")
    ppt_text = "\n".join(
        shape.text
        if shape.has_text_frame
        else "\n".join(c.text for r in shape.table.rows for c in r.cells)
        if shape.has_table
        else ""
        for slide in deck.slides
        for shape in slide.shapes
    )
    workbook = openpyxl.load_workbook(bundle / "SAMPLE_report.xlsx", data_only=True)
    for index, metric in enumerate(HEADLINES):
        value = Decimal(week["values"][metric])
        label = display(metric, value)
        assert label in html and label in pdf_text and label in ppt_text
        assert Decimal(
            str(workbook["Summary"].cell(7, 2 + index * 4).value)
        ) == pytest.approx(value)
        assert (
            display(
                metric, Decimal(str(workbook["Summary"].cell(7, 2 + index * 4).value))
            )
            == label
        )
    identity = report["presentation"]["report_id"]
    for text in (html, pdf_text, ppt_text):
        assert identity in text and "DRAFT" in text and "SAMPLE DATA" in text
    assert workbook.sheetnames == [
        "Summary",
        "Priorities",
        "Products",
        "Charts",
        "Commentary",
        "Run info",
    ]
    assert workbook["Products"].freeze_panes == "F6"
    assert len(deck.slides) == 5
    assert all(
        abs(float(p.mediabox.width) - 595.2756) < 0.01
        and abs(float(p.mediabox.height) - 841.8898) < 0.01
        for p in pdf.pages
    )
    assert all(
        "SAMPLE DATA" in p.extract_text() and "Page " in p.extract_text()
        for p in pdf.pages
    )


def test_full_product_values_and_commentary_preserved(bundle):
    report = json.loads((bundle / "report.json").read_text())
    book = openpyxl.load_workbook(bundle / "SAMPLE_report.xlsx", data_only=True)
    for row, product in enumerate(report["products"], 6):
        assert book["Products"].cell(row, 3).value == product["asin"]
        for col, (metric, value) in enumerate(product["values"].items(), 8):
            actual = book["Products"].cell(row, col).value
            assert (
                actual == "N/A"
                if value is None
                else Decimal(str(actual)) == pytest.approx(Decimal(value))
            )
            if value is not None:
                assert display(metric, Decimal(str(actual))) == display(
                    metric, Decimal(value)
                )
    html = (bundle / "SAMPLE_report.html").read_text(encoding="utf-8")
    deck = Presentation(bundle / "SAMPLE_report.pptx")
    notes = deck.slides[4].notes_slide.notes_text_frame.text
    for row, note in enumerate(report["commentary"]["notes"], 6):
        assert book["Commentary"].cell(row, 4).value == note["label"]
        for field in (
            "what_happened",
            "likely_cause",
            "planned_change_to_review",
            "target_and_review_date",
        ):
            assert note[field] in html and note[field] in notes
        assert note["asin"] in notes and note["reason"] in notes


def test_native_chart_series_equal_shared_data(bundle, view):
    expected = chart_data(view)
    deck = Presentation(bundle / "SAMPLE_report.pptx")
    charts = [s.chart for slide in deck.slides for s in slide.shapes if s.has_chart]
    assert len(charts) == 3
    for chart, data in zip(charts, expected.values(), strict=True):
        assert tuple(c.label for c in chart.plots[0].categories) == data.categories
        for series, (_, values) in zip(chart.series, data.series, strict=True):
            assert series.values == pytest.approx(values)
    with zipfile.ZipFile(bundle / "SAMPLE_report.xlsx") as archive:
        paths = [
            n
            for n in archive.namelist()
            if n.startswith("xl/charts/chart") and n.endswith(".xml")
        ]
        assert len(paths) == 4
        xml = [ET.fromstring(archive.read(n)) for n in paths]
        ns = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
        series_values = [
            tuple(
                float(v.text)
                for v in series.findall(".//c:val/c:numRef/c:numCache/c:pt/c:v", ns)
            )
            for root in xml
            for series in root.findall(".//c:ser", ns)
        ]
        for data in expected.values():
            for _, values in data.series:
                assert any(actual == pytest.approx(values) for actual in series_values)


def test_autoescape_and_self_contained_resources(view):
    card = replace(view.cards[0], name='<script>alert("bad")</script>')
    changed = replace(view, cards=(card, *view.cards[1:]))
    html = render_html(changed, render_charts(changed)).decode()
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert html.count("<svg") == 3
    assert "<script src=" not in html and '<link rel="stylesheet"' not in html
    with pytest.raises(ValueError, match="blocked resource"):
        render_pdf(b'<img src="https://example.invalid/private.png">')


def test_renderer_failure_publishes_nothing(tmp_path, monkeypatch):
    def fail(_):
        raise ValueError("injected renderer failure")

    monkeypatch.setattr("adsreport.pipeline.render_xlsx", fail)
    output = tmp_path / "failed"
    assert main(["run", "--out", str(output), "--no-ai"]) == 2
    assert not output.exists()


def test_approval_display_is_consistent_but_not_an_approval_action(view):
    approved = replace(
        view, stamp=Stamp("Test reviewer", datetime(2026, 11, 16, 12, tzinfo=UTC))
    )
    html = render_html(approved, render_charts(approved))
    assert approved.stamp.text in html.decode()
    pdf = PdfReader(io.BytesIO(render_pdf(html)))
    assert "APPROVED by Test reviewer" in pdf.pages[0].extract_text()
    workbook = openpyxl.load_workbook(io.BytesIO(render_xlsx(approved)), data_only=True)
    assert workbook["Run info"]["C7"].value == approved.stamp.text
    deck = Presentation(io.BytesIO(render_pptx(approved)))
    assert any(
        approved.stamp.text in shape.text
        for slide in deck.slides
        for shape in slide.shapes
        if shape.has_text_frame
    )
    assert approved.report_id == view.report_id
    with pytest.raises(ValueError):
        Stamp("incomplete", None)
    with pytest.raises(ValueError):
        Stamp("reviewer", datetime(2026, 11, 16))


def test_no_flags_and_undefined_values_render_explicitly(view):
    cards = tuple(
        replace(
            c,
            flags=(),
            source_url="",
            metrics=replace(
                c.metrics,
                values=c.metrics.values
                | {
                    "acos_pct": None,
                    "break_even_acos_pct": None,
                    "contribution_after_ads_eur": None,
                },
            ),
        )
        for c in view.cards
    )
    weeks = tuple(
        replace(
            w,
            values=w.values | {m: None for m in HEADLINES},
            deltas={m: None for m in HEADLINES},
        )
        if w.week == view.report_week
        else w
        for w in view.portfolio
    )
    empty = replace(
        view,
        cards=cards,
        portfolio=weeks,
        analysis=view.analysis.model_copy(update={"flags": (), "priorities": ()}),
    )
    html = render_html(empty, render_charts(empty))
    assert "No rule flags" in html.decode() and "N/A" in html.decode()
    assert "N/A" in PdfReader(io.BytesIO(render_pdf(html))).pages[0].extract_text()
    book = openpyxl.load_workbook(io.BytesIO(render_xlsx(empty)), data_only=True)
    assert book["Summary"]["B7"].value == "N/A"
    assert len(Presentation(io.BytesIO(render_pptx(empty))).slides) == 5


def test_missing_pdf_native_dependency_is_actionable(monkeypatch):
    import builtins

    original = builtins.__import__

    def missing(name, *args, **kwargs):
        if name == "weasyprint":
            raise OSError("injected missing DLL")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing)
    with pytest.raises(ValueError, match="PDF native libraries are missing"):
        render_pdf(b"<p>SAMPLE DATA</p>")


def test_office_strings_cannot_become_formulas(view):
    card = replace(view.cards[0], name='=HYPERLINK("https://example.invalid","bad")')
    changed = replace(view, cards=(card, *view.cards[1:]))
    book = openpyxl.load_workbook(io.BytesIO(render_xlsx(changed)))
    assert book["Products"]["B6"].data_type == "s"
    assert book["Products"]["B6"].value == card.name
    bad = replace(card, metrics=replace(card.metrics, asin="=1+1"))
    with pytest.raises(ValueError, match="identifier cannot be a spreadsheet formula"):
        render_pptx(replace(view, cards=(bad, *view.cards[1:])))


def test_real_ai_note_replay_renders_labels_without_network(view):
    from adsreport.ai.models import Commentary
    from adsreport.guard.numbers import check_claim

    evidence = json.loads(Path("docs/evidence/p5-gemini.json").read_text())
    commentary = Commentary.model_validate(evidence["commentary"]).model_copy(
        update={"request_status": "replayed_real_response", "attempts": 0}
    )
    notes = {n.asin: n for n in commentary.notes}
    cards = tuple(replace(c, note=notes[c.metrics.asin]) for c in view.cards)
    for c in cards:
        assert all(check_claim(claim, c.metrics) == () for claim in c.note.claims)
    replay = replace(view, cards=cards, commentary=commentary)
    html = render_html(replay, render_charts(replay))
    label = "AI-drafted, guard-checked"
    assert label in html.decode()
    assert label in PdfReader(io.BytesIO(render_pdf(html))).pages[2].extract_text()
    book = openpyxl.load_workbook(io.BytesIO(render_xlsx(replay)), data_only=True)
    assert book["Commentary"]["D6"].value == label
    deck = Presentation(io.BytesIO(render_pptx(replay)))
    assert label in deck.slides[4].notes_slide.notes_text_frame.text
