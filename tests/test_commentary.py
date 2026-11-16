import json
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from email.utils import format_datetime
from pathlib import Path
from unittest.mock import Mock

import httpx2
import pytest
from google import genai
from google.genai import errors

from adsreport.ai.commentary import (
    ProviderFailure,
    build_prompt,
    credentials,
    generate_commentary,
    request_gemini,
    retry_delay,
)
from adsreport.ai.fallback import allowed_reviews, template_note
from adsreport.ai.models import Claim, Commentary, Draft
from adsreport.config import load_config
from adsreport.guard.numbers import METRICS, check_claim, check_draft, render_claim
from adsreport.io.loader import load_inputs
from adsreport.kpi.engine import ProductMetrics, calculate_report
from adsreport.rules.engine import RuleReport, evaluate_rules


@pytest.fixture
def sample() -> tuple[list[ProductMetrics], RuleReport]:
    loaded = load_inputs(Path("data/sample"), Path("config/column_map.yaml"))
    results = calculate_report(loaded.rows, loaded.manifest.vat_rate)
    analysis = evaluate_rules(
        results, load_config(Path("config")).thresholds, loaded.manifest.report_week
    )
    return [r for r in results if r.week == analysis.report_week], analysis


@pytest.fixture(autouse=True)
def free_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "adsreport.ai.commentary.credentials", lambda _: ("test-only", True)
    )


def draft_for(product: ProductMetrics, analysis: RuleReport) -> Draft:
    flags = [f for f in analysis.flags if f.asin == product.asin]
    return Draft(
        asin=product.asin,
        week=product.week,
        what_happened=[
            Claim(
                metric="acos_pct",
                value=str(product.values["acos_pct"]),
                unit="percent",
                direction="level",
            )
        ],
        likely_cause="unknown",
        planned_change_to_review=allowed_reviews(flags)[0],
        target_and_review_date="unknown",
        confidence="low",
    )


def response_for(products: list[ProductMetrics], analysis: RuleReport) -> str:
    return json.dumps(
        {"products": [draft_for(p, analysis).model_dump(mode="json") for p in products]}
    )


def test_batched_success_and_fact_only_prompt(
    sample: tuple[list[ProductMetrics], RuleReport],
) -> None:
    products, analysis = sample
    request = Mock(return_value=response_for(products, analysis))
    result = generate_commentary(products, analysis, no_ai=False, request=request)
    assert request.call_count == result.attempts == 1
    assert result.ai_used and result.guard_rejections == 0
    assert len(result.notes) == 10
    assert all(n.label == "AI-drafted, guard-checked" for n in result.notes)
    assert Commentary.model_validate_json(result.model_dump_json()) == result
    payload = json.loads(request.call_args.args[0].splitlines()[-1])
    assert len(payload["products"]) == 10
    assert payload["products"][0]["asin"] == "SAMPLE0004"  # high-priority first
    assert payload["data_label"] == "SAMPLE DATA"
    for product, note in zip(products, result.notes, strict=True):
        assert note.asin == product.asin and note.week == product.week
        assert "ACoS:" in note.what_happened
        for field in (
            note.what_happened,
            note.likely_cause,
            note.planned_change_to_review,
            note.target_and_review_date,
        ):
            assert len(field.split()) <= 70


@pytest.mark.parametrize("value", ["34", "33.6", "33.60", "33,60", "33.6001"])
def test_supported_rounding(value: str) -> None:
    product = ProductMetrics(
        "TEST",
        date(2026, 10, 26),
        "maturity",
        date(2025, 1, 1),
        {"acos_pct": Decimal("33.6001")},
        {},
    )
    assert (
        check_claim(
            Claim(metric="acos_pct", value=value, unit="percent", direction="level"),
            product,
        )
        == ()
    )


@pytest.mark.parametrize(
    ("changes", "issue"),
    [
        ({"value": "99999.99"}, "unsupported_value"),
        ({"value": "33.6%"}, "numeric_syntax"),
        ({"value": "EUR 33.6"}, "numeric_syntax"),
        ({"value": "2026-10-26"}, "numeric_syntax"),
        ({"value": "thirty three"}, "numeric_syntax"),
        ({"value": "NaN"}, "numeric_syntax"),
        ({"value": "1e3"}, "numeric_syntax"),
        ({"value": "1,234.00"}, "numeric_syntax"),
        ({"value": "33.6; change price 10"}, "numeric_syntax"),
        ({"unit": "EUR"}, "unit_mismatch"),
        ({"direction": "down"}, "direction_mismatch"),
        ({"metric": "invented"}, "metric_unavailable"),
        ({"metric": "undefined"}, "metric_unavailable"),
    ],
)
def test_claim_rejections(changes: dict[str, str], issue: str) -> None:
    product = ProductMetrics(
        "TEST",
        date(2026, 10, 26),
        "maturity",
        date(2025, 1, 1),
        {"acos_pct": Decimal("33.6"), "undefined": None},
        {},
    )
    claim = Claim.model_validate(
        {"metric": "acos_pct", "value": "33.6", "unit": "percent", "direction": "level"}
        | changes
    )
    assert issue in check_claim(claim, product)


def test_acos_tacos_swap_and_product_week_binding(
    sample: tuple[list[ProductMetrics], RuleReport],
) -> None:
    products, analysis = sample
    product = products[0]
    draft = draft_for(product, analysis)
    swapped = draft.what_happened[0].model_copy(update={"metric": "tacos_pct"})
    assert "unsupported_value" in check_claim(swapped, product)
    assert "product_mismatch" in check_draft(
        draft.model_copy(update={"asin": products[1].asin}), product
    )
    assert "week_mismatch" in check_draft(
        draft.model_copy(update={"week": date(2026, 10, 19)}), product
    )
    assert "duplicate_metric" in check_draft(
        draft.model_copy(update={"what_happened": draft.what_happened * 2}), product
    )
    assert "unsupported_value" in check_claim(
        draft.what_happened[0].model_copy(
            update={"value": str(products[4].values["acos_pct"])}
        ),
        product,
    )


@pytest.mark.parametrize(
    ("value", "direction", "text"),
    [
        ("-20", "down", "-20% (down)"),
        ("20", "up", "20% (up)"),
        ("0", "flat", "0% (flat)"),
    ],
)
def test_direction_and_signed_delta(value: str, direction: str, text: str) -> None:
    product = ProductMetrics(
        "TEST",
        date(2026, 10, 26),
        "maturity",
        date(2025, 1, 1),
        {"ad_cvr_pct_wow_pct": Decimal(value)},
        {},
    )
    claim = Claim.model_validate(
        {
            "metric": "ad_cvr_pct_wow_pct",
            "value": value,
            "unit": "percent",
            "direction": direction,
        }
    )
    assert check_claim(claim, product) == ()
    assert text in render_claim(claim)
    if value != "0":
        assert "direction_mismatch" in check_claim(
            claim.model_copy(update={"direction": "flat"}), product
        )
        assert "unsupported_value" in check_claim(
            claim.model_copy(update={"value": str(-Decimal(value))}), product
        )


def test_every_metric_has_unit_and_canonical_label(
    sample: tuple[list[ProductMetrics], RuleReport],
) -> None:
    products, _ = sample
    assert set(products[0].values) == set(METRICS)
    for metric, (label, unit) in METRICS.items():
        text = render_claim(
            Claim(metric=metric, value="1.25", unit=unit, direction="level")
        )
        assert text.startswith(label + ": ")


def test_no_ai_never_reads_credentials_or_requests(
    sample: tuple[list[ProductMetrics], RuleReport], monkeypatch: pytest.MonkeyPatch
) -> None:
    products, analysis = sample
    fail = Mock(side_effect=AssertionError("offline path touched credentials/network"))
    monkeypatch.setattr("adsreport.ai.commentary.credentials", fail)
    result = generate_commentary(products, analysis, no_ai=True, request=fail)
    assert result == generate_commentary(products, analysis, no_ai=True, request=fail)
    assert not result.ai_used and result.attempts == 0
    assert all(n.label == "template" and n.reason == "no_ai" for n in result.notes)
    assert result.notes[2].asin == "SAMPLE0003"  # healthy launch still covered
    fail.assert_not_called()


@pytest.mark.parametrize(
    ("key", "confirmed", "reason"),
    [("", True, "missing_key"), ("test", False, "free_tier_unconfirmed")],
)
def test_credential_gates(
    sample: tuple[list[ProductMetrics], RuleReport],
    monkeypatch: pytest.MonkeyPatch,
    key: str,
    confirmed: bool,
    reason: str,
) -> None:
    products, analysis = sample
    monkeypatch.setattr(
        "adsreport.ai.commentary.credentials", lambda _: (key, confirmed)
    )
    request = Mock()
    result = generate_commentary(products, analysis, no_ai=False, request=request)
    assert result.request_status == reason
    request.assert_not_called()


def test_paid_or_unverified_model_never_called(
    sample: tuple[list[ProductMetrics], RuleReport],
) -> None:
    products, analysis = sample
    request = Mock()
    result = generate_commentary(
        products, analysis, no_ai=False, model="unverified", request=request
    )
    assert result.request_status == "model_not_free_verified"
    request.assert_not_called()


@pytest.mark.parametrize(
    ("failure", "attempts", "reason", "delays"),
    [
        (ProviderFailure(429, 2.5), 2, "quota_exhausted", [2.5]),
        (ProviderFailure(429, 120), 2, "quota_exhausted", [60, 60]),
        (ProviderFailure(429, float("inf")), 1, "quota_retry_invalid", []),
        (ProviderFailure(401), 1, "service_error", []),
        (TimeoutError("secret request"), 1, "service_error", []),
        (RuntimeError("secret request"), 1, "service_error", []),
    ],
)
def test_provider_failures_never_fail_report(
    sample: tuple[list[ProductMetrics], RuleReport],
    failure: Exception,
    attempts: int,
    reason: str,
    delays: list[float],
) -> None:
    products, analysis = sample
    request, sleep = Mock(side_effect=failure), Mock()
    result = generate_commentary(
        products, analysis, no_ai=False, request=request, sleep=sleep
    )
    assert request.call_count == result.attempts == attempts
    assert [args.args[0] for args in sleep.call_args_list] == delays
    assert result.request_status == reason
    assert all(n.reason == reason and n.label == "template" for n in result.notes)
    assert "secret" not in result.model_dump_json()


def test_single_quota_retry_can_recover(
    sample: tuple[list[ProductMetrics], RuleReport],
) -> None:
    products, analysis = sample
    request = Mock(
        side_effect=[ProviderFailure(429, 4), response_for(products, analysis)]
    )
    sleep = Mock()
    result = generate_commentary(
        products, analysis, no_ai=False, request=request, sleep=sleep
    )
    assert result.ai_used and result.attempts == 2
    sleep.assert_called_once_with(4)


@pytest.mark.parametrize(
    "raw",
    [
        "not JSON",
        "{}",
        '{"products":{}}',
        '{"products":[null]}',
        '{"products":[{"asin":99}]}',
    ],
)
def test_batch_schema_failure(
    sample: tuple[list[ProductMetrics], RuleReport], raw: str
) -> None:
    products, analysis = sample
    result = generate_commentary(
        products, analysis, no_ai=False, request=Mock(return_value=raw)
    )
    assert result.request_status == "schema_invalid"
    assert len(result.notes) == 10 and not result.ai_used


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ("number", "guard_rejected"),
        ("week", "guard_rejected"),
        ("review", "guard_rejected"),
        ("cause", "schema_invalid"),
        ("target", "schema_invalid"),
        ("duplicate", "duplicate_product"),
        ("missing", "missing_product"),
    ],
)
def test_product_failure_preserves_other_notes(
    sample: tuple[list[ProductMetrics], RuleReport], mutation: str, reason: str
) -> None:
    products, analysis = sample
    payload = json.loads(response_for(products, analysis))
    entry = payload["products"][0]
    if mutation == "number":
        entry["what_happened"][0]["value"] = "99999.99"
    elif mutation == "week":
        entry["week"] = "2026-10-19"
    elif mutation == "review":
        entry["planned_change_to_review"] = "inventory"
    elif mutation == "cause":
        entry["likely_cause"] = "A competitor changed price by EUR 10"
    elif mutation == "target":
        entry["target_and_review_date"] = "2026-11-02"
    elif mutation == "duplicate":
        payload["products"].append(entry)
    else:
        payload["products"].pop(0)
    result = generate_commentary(
        products, analysis, no_ai=False, request=Mock(return_value=json.dumps(payload))
    )
    assert result.notes[0].reason == reason and result.notes[0].label == "template"
    assert all(n.label == "AI-drafted, guard-checked" for n in result.notes[1:])
    if mutation == "number":
        assert result.guard_rejections == 1
        assert result.notes[0].rejected_numeric_tokens == ("99999.99",)


def test_unknown_product_rejects_batch_and_limit_keeps_templates(
    sample: tuple[list[ProductMetrics], RuleReport],
) -> None:
    products, analysis = sample
    raw = response_for(products, analysis).replace("SAMPLE0001", "OTHER")
    result = generate_commentary(
        products, analysis, no_ai=False, request=Mock(return_value=raw)
    )
    assert result.request_status == "unexpected_product"
    # Selected high-priority products are first even when the limit is smaller.
    selected = [p for p in products if p.asin == "SAMPLE0004"]
    result = generate_commentary(
        products,
        analysis,
        no_ai=False,
        limit=1,
        request=Mock(return_value=response_for(selected, analysis)),
    )
    assert sum(n.label == "AI-drafted, guard-checked" for n in result.notes) == 1
    assert sum(n.reason == "product_limit" for n in result.notes) == 9


def test_undefined_template_and_prompt_exclusion(
    sample: tuple[list[ProductMetrics], RuleReport],
) -> None:
    products, analysis = sample
    product = ProductMetrics(
        products[0].asin,
        products[0].week,
        "maturity",
        products[0].launch_start_date,
        {"acos_pct": None},
        {"acos_pct": "no sales"},
    )
    note = template_note(product, [], "no_ai")
    assert "unavailable" in note.what_happened
    payload = json.loads(build_prompt([product], analysis, "prompt").splitlines()[-1])
    assert payload["products"][0]["facts"] == []


def test_credentials_precedence_and_no_evaluation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_FREE_TIER_CONFIRMED", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "GEMINI_API_KEY='local-test'\nGEMINI_FREE_TIER_CONFIRMED=true\nIGNORED=$(exit)\n"
    )
    assert credentials(env_file) == ("local-test", True)
    monkeypatch.setenv("GEMINI_API_KEY", "environment-test")
    assert credentials(env_file) == ("environment-test", True)
    assert credentials(tmp_path / "absent") == ("environment-test", False)


def test_unreadable_credentials_fallback(
    sample: tuple[list[ProductMetrics], RuleReport], monkeypatch: pytest.MonkeyPatch
) -> None:
    products, analysis = sample
    monkeypatch.setattr(
        "adsreport.ai.commentary.credentials", Mock(side_effect=OSError())
    )
    assert (
        generate_commentary(products, analysis, no_ai=False).request_status
        == "credentials_unreadable"
    )


@pytest.mark.parametrize("header", ["2.5", "invalid", "NaN"])
def test_retry_header_and_rpc_info(header: str) -> None:
    error = errors.ClientError(
        429,
        {
            "error": {
                "details": [
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "4s",
                    },
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "invalid",
                    },
                ]
            }
        },
        httpx2.Response(429, headers={"Retry-After": header}),
    )
    assert retry_delay(error) == 4
    future = datetime.now(UTC) + timedelta(seconds=30)
    error = errors.ClientError(
        429, {}, httpx2.Response(429, headers={"Retry-After": format_datetime(future)})
    )
    assert 28 <= retry_delay(error) <= 30


def test_actual_sdk_transport_has_no_hidden_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []
    real_client = genai.Client

    def respond(request: httpx2.Request) -> httpx2.Response:
        calls.append(json.loads(request.content))
        return httpx2.Response(
            429,
            json={"error": {"code": 429, "message": "test quota"}},
            headers={"Retry-After": "7"},
        )

    def client(**kwargs: object) -> genai.Client:
        options = kwargs["http_options"]
        assert options.retry_options.attempts == 1
        options.client_args = {"transport": httpx2.MockTransport(respond)}
        return real_client(**kwargs)

    monkeypatch.setattr("adsreport.ai.commentary.genai.Client", client)
    with pytest.raises(ProviderFailure) as failure:
        request_gemini("SAMPLE DATA", "gemini-3.5-flash-lite", "test-only")
    assert len(calls) == 1
    assert failure.value.code == 429 and failure.value.retry_after == 7
    assert calls[0]["store"] is False
    assert "tools" not in calls[0]


def test_euro_and_percentage_point_rounding() -> None:
    product = ProductMetrics(
        "TEST",
        date(2026, 10, 26),
        "maturity",
        date(2025, 1, 1),
        {
            "contribution_after_ads_eur": Decimal("-8.445"),
            "acos_pct_wow_pp": Decimal("-5.125"),
        },
        {},
    )
    euros = Claim(
        metric="contribution_after_ads_eur",
        value="-8.45",
        unit="EUR",
        direction="level",
    )
    points = Claim(
        metric="acos_pct_wow_pp",
        value="-5.13",
        unit="percentage_points",
        direction="down",
    )
    assert check_claim(euros, product) == check_claim(points, product) == ()
    assert "EUR -8.45" in render_claim(euros)
    assert "-5.13 pp (down)" in render_claim(points)


@pytest.mark.parametrize("output", ['{"products":[]}', None])
def test_sdk_text_response_or_missing_output(
    monkeypatch: pytest.MonkeyPatch,
    output: str | None,
) -> None:
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.interactions.create.return_value.output_text = output
    monkeypatch.setattr(
        "adsreport.ai.commentary.genai.Client", Mock(return_value=client)
    )
    if output is None:
        with pytest.raises(ValueError, match="Missing structured"):
            request_gemini("SAMPLE DATA", "gemini-3.5-flash-lite", "test-only")
    else:
        assert (
            request_gemini("SAMPLE DATA", "gemini-3.5-flash-lite", "test-only")
            == output
        )
    assert (
        client.interactions.create.call_args.kwargs["automatic_continuation"] is False
    )
