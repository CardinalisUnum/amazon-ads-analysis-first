"""Validate owner-visible configuration before starting a report."""

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Fraction = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class ConfigError(ValueError):
    """A configuration file is missing, malformed or unsupported."""


class StrictConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class Settings(StrictConfig):
    marketplace: Literal["amazon.de"]
    currency: Literal["EUR"]
    vat_rate: Fraction
    reporting_timezone: Literal["Europe/Berlin"]
    schedule_timezone: Literal["Asia/Manila"]
    schedule_cron_utc: Literal["17 1 * * 1"]
    attribution_days: Annotated[int, Field(ge=7)]
    reporting_latency_days: Annotated[int, Field(ge=1)]
    number_format: Literal["en"]
    sample_label: Literal["SAMPLE DATA"]
    gemini_model: Annotated[str, Field(min_length=1, pattern=r"^gemini-[a-z0-9.-]+$")]
    commentary_products: Annotated[int, Field(ge=1, le=10)]
    output_formats: list[Literal["xlsx", "html", "pdf", "pptx"]] = Field(
        min_length=4, max_length=4
    )


class Thresholds(StrictConfig):
    assumptions: Literal[True]
    launch_window_weeks: Annotated[int, Field(ge=1)]
    acos_improvement_pp: Positive
    sales_drop_fraction: Fraction
    impressions_drop_fraction: Fraction
    stock_spend_increase_fraction: Fraction
    stock_coverage_days: Positive
    cvr_drop_fraction: Fraction
    stable_clicks_fraction: Fraction
    spend_spike_fraction: Positive
    max_ad_sales_growth_fraction: Fraction
    organic_decline_transitions: Annotated[int, Field(ge=1)]
    maturity_break_even_fraction: Fraction


class Configuration(StrictConfig):
    settings: Settings
    thresholds: Thresholds


def load_config(directory: Path) -> Configuration:
    """Read both required YAML files, with actionable errors and safe YAML loading."""
    data: dict[str, object] = {}
    for name in ("settings", "thresholds"):
        path = directory / f"{name}.yaml"
        try:
            value: object = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise ConfigError(f"Cannot read valid YAML from {path}: {exc}") from exc
        if not isinstance(value, dict):
            raise ConfigError(f"{path} must contain a YAML mapping.")
        data[name] = value
    try:
        config = Configuration.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid configuration in {directory}: {exc}") from exc
    if len(set(config.settings.output_formats)) != 4:
        raise ConfigError(
            "output_formats must contain xlsx, html, pdf and pptx once each."
        )
    return config
