# Commentary contract

P5 adds optional, checked fact selection over Python-calculated results. The common pipeline publishes report.json with stage commentary and an unchanged SAMPLE_kpis.csv. Every artifact remains DRAFT and SAMPLE DATA. Four visual formats are P6.

## Data and schema

The request includes only the latest report week's computed metrics, canonical labels, units, directions, display-rounded options, rule flags and allowed review choices. Products are ordered by rule severity, then remaining identifiers. commentary_products limits the AI batch to at most ten. Every latest-week product still receives a note, with a product_limit template when outside the batch. Six priorities do not limit the approved ten-product commentary coverage.

The installed prompt is src/adsreport/ai/prompt.txt. Its SHA-256 is recorded in commentary.prompt_sha256. Python schemas are in ai/models.py. Draft has asin, week, what_happened, likely_cause, planned_change_to_review, target_and_review_date and confidence. what_happened contains one to three distinct claims with metric, value, unit and direction. Causes, targets and review dates are constrained to unknown, and confidence to low. Review choices are mapped to fixed human-review wording and checked against that product's flags.

Gemini receives a smaller JSON schema without metadata, date format or length bounds to avoid a verified serving-complexity error. Local Pydantic validation still enforces every bound and forbids extra fields. A malformed product falls back independently. Invalid outer JSON or unknown identifiers reject the batch. Duplicate and missing identifiers fall back for the affected product.

## Guard and rendering

Each numeric string is validated against its named metric in that product and week. Units are explicit EUR, percent, percentage_points, ratio, count, units or days. Signed week-over-week deltas require up, down or flat matching the computed sign. Level observations require level. A negative contribution is a signed level, not a week-over-week direction claim.

Raw finite values and Decimal ROUND_HALF_UP rounding to zero, one or two places are allowed. Decimal point or comma is accepted without grouping. Dates, currency symbols, exponent notation, numeric prose, NaN and infinity cannot pass as a value. Unknown or undefined metrics fail. Another metric's valid number cannot support the claim. Python owns all labels, so a free-text ACoS/TACoS label swap is unavailable.

Accepted claims become canonical English sentences. The remaining fields use bounded wording requesting review with the Ads manager. No causal inference, financial calculation, automatic action, speculative target or future date comes from the model. The guard checks factual attribution and formatting. It does not certify that the model selected the most useful evidence, establish causation, or replace human approval.

## Outcomes and fallback

Every note records label, reason, product, week, SAMPLE DATA and its structured claims. Labels are AI-drafted, guard-checked or template. Templates show ad spend, ACoS and contribution after ads where available, plus a rule-aligned review item. An unavailable value is omitted rather than invented.

Guard rejection records stable issue codes and extracted numeric tokens. Arbitrary rejected prose, provider exception text, keys and account identifiers are never persisted. Other reasons include no_ai, missing_key, free_tier_unconfirmed, model_not_free_verified, credentials_unreadable, service_error, quota_exhausted, quota_retry_invalid, schema_invalid, duplicate_product, missing_product, unexpected_product and product_limit. request_status=parsed_response confirms parsing, while ai_used and note labels distinguish accepted notes from partial or total fallback.

--no-ai returns deterministic templates before reading credentials or making a request. The default path reads only GEMINI_API_KEY and GEMINI_FREE_TIER_CONFIRMED from the environment and ignored .env, with environment precedence. The configured model must be the free-verified gemini-3.5-flash-lite. The confirmation flag is an operator attestation, not a billing API check.

One standard synchronous request contains the selected products. SDK retries and automatic continuation are disabled. Each attempt has a sixty-second timeout and no tools. On HTTP 429, one application retry waits for Retry-After or Google RetryInfo, using the longer available delay and a one-second default. Wait chunks are at most sixty seconds. A second quota error uses templates. Authentication, network, schema and other service errors use templates immediately. A nonfinite retry delay from an injected adapter is rejected. The numerical run remains usable even when AI fails.

## Verification and limits

The tests exercise legitimate rounding, euro amounts, percentage points, signs, wrong weeks/products, ACoS/TACoS substitution, hallucinated numbers, injected prose/dates, duplicate/missing notes, per-product fallback, schema failure, missing keys and quota recovery/exhaustion. An actual SDK HTTP transport test confirms one HTTP attempt with no hidden retry. Network access and credentials are unnecessary for the test suite.

docs/evidence/p5-gemini.json contains the real successful manual call and notes. Two earlier manual requests failed with schema-complexity errors before simplification. docs/evidence/p5-local.txt captures the final quality gates. docs/evidence/p5-checkout.txt captures reproducibility and packaging checks. These are manual development checks. Genuine unattended run history and measured human review effort remain P7 and P8.

Official sources checked 2026-11-16 are [structured output](https://aistudio.google.com/docs/structured-output), [standard Free Tier pricing](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite), [SDK documentation](https://googleapis.github.io/python-genai/) and [pinned package metadata](https://pypi.org/project/google-genai/3.3.0/). Free quota may change or be exhausted. Free Tier data terms apply, so the P5 check sent simulated performance only. The owner must rotate the key shared in chat before unattended operation.
