"""One optional structured request, bounded retry, product-local fallback."""

import hashlib
import json
import math
import os
import time
from collections import Counter
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import ValidationError

from adsreport.ai.fallback import REVIEWS, allowed_reviews, template_note
from adsreport.ai.models import Commentary, Draft, DraftBatch, Note, StrictModel
from adsreport.guard.numbers import (
    METRICS,
    NUMBER,
    check_draft,
    direction,
    render_claim,
    rounded_values,
)
from adsreport.kpi.engine import ProductMetrics
from adsreport.rules.engine import RuleReport

PROMPT = Path(__file__).with_name("prompt.txt")
FREE_MODEL = "gemini-3.5-flash-lite"


class Envelope(StrictModel):
    # Validate entries separately so one malformed product cannot erase good notes.
    products: list[object]


class ProviderFailure(Exception):
    def __init__(self, code: int, retry_after: float = 1.0) -> None:
        super().__init__("Commentary service unavailable")
        self.code = code
        self.retry_after = retry_after


def response_schema() -> object:
    """Keep serving grammar small. Full field bounds still run locally."""
    local_only = {
        "title",
        "description",
        "format",
        "minLength",
        "maxLength",
        "minItems",
        "maxItems",
    }

    def simplify(value: object) -> object:
        if isinstance(value, dict):
            return {k: simplify(v) for k, v in value.items() if k not in local_only}
        if isinstance(value, list):
            return [simplify(v) for v in value]
        return value

    return simplify(DraftBatch.model_json_schema())


def retry_delay(error: Exception) -> float:
    """Honor Retry-After or Google RetryInfo without retaining provider messages."""
    delays = [1.0]
    response = getattr(error, "response", None)
    header = response.headers.get("Retry-After") if response is not None else None
    if header:
        try:
            delays.append(float(header))
        except ValueError:
            try:
                delays.append(
                    (parsedate_to_datetime(header) - datetime.now(UTC)).total_seconds()
                )
            except (ValueError, TypeError, OverflowError):
                pass
    details = getattr(error, "details", getattr(error, "body", None))
    if isinstance(details, dict):
        body = details.get("error", details)
        if isinstance(body, dict):
            items = body.get("details", [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and str(item.get("@type", "")).endswith(
                        "RetryInfo"
                    ):
                        try:
                            delays.append(
                                float(str(item.get("retryDelay", "")).removesuffix("s"))
                            )
                        except ValueError:
                            pass
    return max(d for d in delays if math.isfinite(d))


def request_gemini(prompt: str, model: str, key: str) -> str:
    try:
        with genai.Client(
            api_key=key,
            http_options=types.HttpOptions(
                timeout=60_000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        ) as client:
            reply = client.interactions.create(
                model=model,
                input=prompt,
                store=False,
                automatic_continuation=False,
                timeout=60.0,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": response_schema(),
                },
            )
            output = getattr(reply, "output_text", None)
            if not isinstance(output, str):
                raise ValueError("Missing structured response")
            return output
    except Exception as exc:
        # Interactions exposes status_code/body, legacy SDK errors use code/details.
        # Read the public attributes rather than importing private SDK error classes.
        code = getattr(exc, "status_code", getattr(exc, "code", None))
        if isinstance(code, int):
            raise ProviderFailure(code, retry_delay(exc)) from None
        raise


def credentials(env_file: Path) -> tuple[str, bool]:
    settings = {
        name: os.environ[name]
        for name in (
            "GEMINI_API_KEY",
            "GEMINI_FREE_TIER_CONFIRMED",
        )
        if name in os.environ
    }
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() in {
                "GEMINI_API_KEY",
                "GEMINI_FREE_TIER_CONFIRMED",
            }:
                settings.setdefault(name.strip(), value.strip().strip("\"'"))
    return settings.get("GEMINI_API_KEY", ""), settings.get(
        "GEMINI_FREE_TIER_CONFIRMED", ""
    ).lower() == "true"


def build_prompt(
    products: Sequence[ProductMetrics], analysis: RuleReport, text: str
) -> str:
    payload = []
    for product in products:
        flags = [f for f in analysis.flags if f.asin == product.asin]
        facts = [
            {
                "metric": metric,
                "label": METRICS[metric][0],
                "unit": METRICS[metric][1],
                "direction": direction(metric, value),
                "allowed_display": [str(v) for v in sorted(rounded_values(value))],
            }
            for metric, value in product.values.items()
            if metric in METRICS and value is not None and value.is_finite()
        ]
        payload.append(
            {
                "asin": product.asin,
                "week": product.week.isoformat(),
                "facts": facts,
                "flags": [f.model_dump(mode="json") for f in flags],
                "allowed_reviews": allowed_reviews(flags),
            }
        )
    return text + "\n" + json.dumps({"data_label": "SAMPLE DATA", "products": payload})


def generate_commentary(
    records: Sequence[ProductMetrics],
    analysis: RuleReport,
    *,
    no_ai: bool,
    model: str = FREE_MODEL,
    limit: int = 10,
    env_file: Path = Path(".env"),
    request: Callable[[str, str, str], str] = request_gemini,
    sleep: Callable[[float], None] = time.sleep,
) -> Commentary:
    products = sorted(
        (r for r in records if r.week == analysis.report_week), key=lambda r: r.asin
    )
    flags = {p.asin: [f for f in analysis.flags if f.asin == p.asin] for p in products}
    text = PROMPT.read_text(encoding="utf-8")
    prompt_hash = hashlib.sha256(text.encode()).hexdigest()
    attempts = 0
    provider_error_status: int | None = None

    def batch_fallback(reason: str) -> Commentary:
        return Commentary(
            notes=tuple(template_note(p, flags[p.asin], reason) for p in products),
            request_status=reason,
            attempts=attempts,
            model=model if attempts else None,
            prompt_sha256=prompt_hash,
            provider_error_status=provider_error_status,
        )

    if no_ai:
        return batch_fallback("no_ai")
    if model != FREE_MODEL:
        return batch_fallback("model_not_free_verified")
    try:
        key, confirmed = credentials(env_file)
    except OSError:
        return batch_fallback("credentials_unreadable")
    if not key:
        return batch_fallback("missing_key")
    if not confirmed:
        return batch_fallback("free_tier_unconfirmed")
    ranked_asins = list(dict.fromkeys(f.asin for f in analysis.flags))
    ranked = sorted(
        products,
        key=lambda p: (
            ranked_asins.index(p.asin) if p.asin in ranked_asins else len(ranked_asins),
            p.asin,
        ),
    )
    selected = ranked[:limit]
    prompt = build_prompt(selected, analysis, text)
    for attempt in range(2):
        attempts += 1
        try:
            raw = request(prompt, model, key)
            break
        except ProviderFailure as exc:
            provider_error_status = exc.code
            if exc.code == 429 and attempt == 0:
                if not math.isfinite(exc.retry_after):
                    return batch_fallback("quota_retry_invalid")
                remaining = max(0, exc.retry_after)
                while remaining:
                    pause = min(remaining, 60)
                    sleep(pause)
                    remaining -= pause
                continue
            return batch_fallback(
                "quota_exhausted" if exc.code == 429 else "service_error"
            )
        except Exception:
            # Optional external boundary: never retain exception text or credentials.
            return batch_fallback("service_error")
    try:
        entries = Envelope.model_validate_json(raw).products
    except ValidationError:
        return batch_fallback("schema_invalid")
    by_asin: dict[str, object] = {}
    identifiers = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("asin"), str):
            return batch_fallback("schema_invalid")
        identifiers.append(entry["asin"])
        by_asin[entry["asin"]] = entry
    counts = Counter(identifiers)
    if set(identifiers) - {p.asin for p in selected}:
        return batch_fallback("unexpected_product")
    notes = []
    rejections = 0
    for product in products:
        asin = product.asin
        if counts[asin] != 1:
            reason = "duplicate_product" if counts[asin] else "missing_product"
            if product not in selected:
                reason = "product_limit"
            notes.append(template_note(product, flags[asin], reason))
            continue
        try:
            draft = Draft.model_validate(by_asin[asin])
        except ValidationError:
            notes.append(template_note(product, flags[asin], "schema_invalid"))
            continue
        issues = check_draft(draft, product)
        if draft.planned_change_to_review not in allowed_reviews(flags[asin]):
            issues += ("unsupported_review",)
        if issues:
            rejections += 1
            tokens = tuple(
                dict.fromkeys(
                    token
                    for claim in draft.what_happened
                    for token in NUMBER.findall(claim.value)
                )
            )
            notes.append(
                template_note(product, flags[asin], "guard_rejected", issues, tokens)
            )
            continue
        notes.append(
            Note(
                asin=asin,
                week=product.week,
                label="AI-drafted, guard-checked",
                reason="validated_fact_selections",
                what_happened=" ".join(render_claim(c) for c in draft.what_happened),
                planned_change_to_review=REVIEWS[draft.planned_change_to_review],
                claims=tuple(draft.what_happened),
            )
        )
    return Commentary(
        notes=tuple(notes),
        request_status="parsed_response",
        attempts=attempts,
        model=model,
        prompt_sha256=prompt_hash,
        ai_used=any(n.label == "AI-drafted, guard-checked" for n in notes),
        guard_rejections=rejections,
    )
