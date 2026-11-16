"""Typed frozen report serialization, restoring supplied facts without recalculation."""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from adsreport.ai.models import Commentary
from adsreport.kpi.engine import ProductMetrics
from adsreport.kpi.summary import PortfolioWeek
from adsreport.render.model import ProductCard, ReportView, Stamp
from adsreport.rules.engine import RuleReport
from adsreport.runlog import RunIdentity

Number = Annotated[Decimal, Field(allow_inf_nan=False)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Product(Strict):
    asin: str
    week: date
    lifecycle_phase: str
    launch_start_date: date
    values: dict[str, Number | None]
    undefined_reasons: dict[str, str]


class Portfolio(Strict):
    week: date
    values: dict[str, Number | None]
    deltas: dict[str, Number | None]
    comparison_reason: str


class Catalog(Strict):
    asin: str
    name: str
    sku: str
    set_number: str
    source_url: str


class Presentation(Strict):
    report_id: str
    portfolio: list[Portfolio]
    catalog: list[Catalog]


class Approval(Strict):
    reviewer: Annotated[
        str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9 ._@-]+$")
    ]
    approved_at: AwareDatetime
    draft_manifest_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    mechanism: Literal["local_attestation", "github_environment", "test"]


class ReportDocument(Strict):
    data_label: Literal["SAMPLE DATA"]
    status: Literal["DRAFT", "APPROVED"]
    stage: Literal["outputs"]
    analysis: RuleReport
    commentary: Commentary
    marketplace: Literal["amazon.de"]
    currency: Literal["EUR"]
    vat_rate: Number
    report_week: date
    source_hashes: dict[str, str]
    config_hashes: dict[str, str]
    products: list[Product]
    presentation: Presentation
    run: RunIdentity | None = None
    approval: Approval | None = None
    maturity: dict[str, str | int | bool] | None = None


def restore_view(document: ReportDocument) -> ReportView:
    records = tuple(
        ProductMetrics(
            p.asin,
            p.week,
            p.lifecycle_phase,
            p.launch_start_date,
            p.values,
            p.undefined_reasons,
        )
        for p in document.products
    )
    catalog = {c.asin: c for c in document.presentation.catalog}
    notes = {n.asin: n for n in document.commentary.notes}
    cards = tuple(
        ProductCard(
            p,
            catalog[p.asin].name,
            catalog[p.asin].sku,
            catalog[p.asin].set_number,
            catalog[p.asin].source_url,
            tuple(f for f in document.analysis.flags if f.asin == p.asin),
            notes[p.asin],
        )
        for p in records
        if p.week == document.report_week
    )
    stamp = Stamp()
    if document.status == "APPROVED":
        if document.approval is None:
            raise ValueError("Approved report has no approval record.")
        stamp = Stamp(document.approval.reviewer, document.approval.approved_at)
    elif document.approval is not None:
        raise ValueError("Draft cannot carry an approval stamp.")
    return ReportView(
        document.presentation.report_id,
        document.report_week,
        records,
        cards,
        tuple(
            PortfolioWeek(p.week, p.values, p.deltas, p.comparison_reason)
            for p in document.presentation.portfolio
        ),
        document.analysis,
        document.commentary,
        document.source_hashes,
        document.config_hashes,
        stamp,
        document.run,
    )
