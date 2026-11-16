"""Structured selections from the supplied facts, followed by rendered notes."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Unit = Literal["EUR", "percent", "percentage_points", "ratio", "count", "units", "days"]
Direction = Literal["level", "up", "down", "flat"]
Review = Literal[
    "routine_review",
    "profitability",
    "launch_window",
    "sales_and_reach",
    "inventory",
    "conversion",
    "spend_and_sales",
    "organic_share",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Claim(StrictModel):
    metric: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=128)
    unit: Unit
    direction: Direction


class Draft(StrictModel):
    asin: str = Field(min_length=1, max_length=30)
    week: date
    what_happened: list[Claim] = Field(min_length=1, max_length=3)
    likely_cause: Literal["unknown"]
    planned_change_to_review: Review
    target_and_review_date: Literal["unknown"]
    confidence: Literal["low"]


class DraftBatch(StrictModel):
    products: list[Draft] = Field(min_length=1, max_length=10)


class Note(StrictModel):
    asin: str
    week: date
    data_label: Literal["SAMPLE DATA"] = "SAMPLE DATA"
    label: Literal["AI-drafted, guard-checked", "template"]
    reason: str
    what_happened: str
    likely_cause: str = "Unknown. These observations do not establish a cause."
    planned_change_to_review: str
    target_and_review_date: str = (
        "Unknown. Agree a target and review date with the Ads manager."
    )
    confidence: Literal["low"] = "low"
    claims: tuple[Claim, ...] = ()
    guard_issues: tuple[str, ...] = ()
    rejected_numeric_tokens: tuple[str, ...] = ()


class Commentary(StrictModel):
    notes: tuple[Note, ...]
    request_status: str
    attempts: int = 0
    model: str | None = None
    prompt_sha256: str
    ai_used: bool = False
    guard_rejections: int = 0
    provider_error_status: int | None = None
