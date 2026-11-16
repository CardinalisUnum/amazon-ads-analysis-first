# Amazon Ads Analysis First

A proof of concept in development for weekly Amazon Ads review. Planned outputs are Excel, HTML, PDF and PowerPoint with Python-calculated product economics, prioritised review flags and checked commentary.

Catalog references use real LEGO products. Seller financial results and stock are simulated and labelled SAMPLE DATA.

Start with [current status](docs/STATUS.md), [resume instructions](docs/RESUME.md), [owner decisions](docs/decisions.md) and [build specification](docs/SPEC.md).

## Development quickstart

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from the repository root. The committed Python version and uv.lock define the environment.

```shell
uv sync --locked
uv run adsreport --help
uv run adsreport --check-config
uv run pytest --cov=src/adsreport --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
```

The current implementation validates inputs, calculates deterministic KPIs, applies all nine review rules and produces checked commentary or deterministic template notes. Approval and delivery return a nonzero status identifying P7. Visual reports follow in P6. Scheduled reporting and delivery follow in P7.

```shell
uv run adsreport generate-sample --seed 42
uv run adsreport generate-sample --seed 2026 --out out/sample-2026
```

The default command verifies the committed seed-42 bundle without rewriting it. A new output directory is published only after every file is staged. Existing different content is preserved, and the command asks for another output path. Use [sample review](docs/P2-SAMPLE-REVIEW.md) to inspect all ten stories and [assumptions](docs/ASSUMPTIONS.md) for costs, dates and attribution limitations.

The sample contains 1,120 daily campaign-product rows, 80 weekly retail rows, 80 inventory snapshots, ten cost records and ten catalog records. File names or metadata carry SAMPLE DATA markers. The ads CSV uses classic English column names. The accompanying manifest identifies tax bases, seed, reporting dates and file hashes.

## Numerical report

```shell
uv run adsreport run --input data/sample --out out/numerical-draft --no-ai
```

This produces SAMPLE_kpis.csv and report.json containing all 80 product-week observations. Both carry DRAFT and SAMPLE DATA labels. JSON preserves exact decimal values as strings, explicit nulls with reasons, source hashes and configuration fingerprints. CSV leaves undefined values blank. The committed golden CSV is checked by the tests.

The loader accepts the configured classic and current English ad-report aliases, verifies source types and declared file hashes, aggregates campaign records first and joins each retail row once. Supply manifest.json and exactly one ads.csv, total_sales.csv, costs.csv and inventory.csv, with optional SAMPLE_ prefixes. Retail inputs use the normalized weekly adapter described in [input contract](docs/INPUT-CONTRACT.md).

report.json includes an analysis section for the manifest report week. It contains every flag with numeric/date evidence and applied thresholds, explicit skipped-rule reasons, and a product priority list. The default priority_products setting is six. A product appears once in that list with all its triggered rule IDs. Every flag remains available even when its product falls outside the displayed priorities. The numerical CSV remains unchanged.

See [rule contract](docs/RULES.md) for exact boundary, lifecycle and history behavior. In the final sample week, the engine finds the approved ten flags across seven products.

All financial calculations use Decimal. The tests reproduce the EUR 8.44 / EUR 25.13 = 33.6% break-even example and exercise zero denominators, missing weeks, halo sales and mathematical properties.

## Checked commentary

Both run modes now include ten latest-week product notes in report.json. --no-ai reads no credential and makes no network request. Its templates are reproducible. The default AI path makes one structured request for all selected products and validates each product separately. It falls back visibly for missing credentials, provider failures, malformed entries or rejected claims. The numerical CSV and rules remain identical in either mode.

To use AI, create a dedicated Google AI Studio Free Tier project with billing unlinked. Save GEMINI_API_KEY and GEMINI_FREE_TIER_CONFIRMED=true in ignored .env, using .env.example as the template. This flag records the operator's attestation. The program cannot independently verify billing status. Rotate any key previously shared in chat before unattended operation.

```shell
uv run adsreport run --input data/sample --out out/ai-draft
```

The verified model is gemini-3.5-flash-lite. Other models fall back until reviewed for free access. One quota retry honors the provider delay. SDK automatic retries and continuation are disabled. Every note carries SAMPLE DATA, either AI-drafted, guard-checked or template, and a reason. Check commentary.request_status and commentary.attempts for the actual service outcome.

The model selects metric facts and a permitted review focus. Python validates each value against that product, week, metric, unit and direction, and owns the rendered labels. Causes, targets and review dates remain unknown. Free-form analysis and causal accuracy are outside this guard's guarantees. See [commentary contract](docs/COMMENTARY.md).

The [P5 evidence](docs/evidence/p5-gemini.json) records a real ten-product batched response with ten accepted notes and no rejections, measured at 6.066 seconds for that local end-to-end run. This manual check provides no scheduled reliability or business time-saving claim. The first serving schema was rejected and simplified before the successful call. Hosted CI remains blocked by the account restriction described in [status](docs/STATUS.md).

## Configuration

Edit config/settings.yaml and config/thresholds.yaml. Run `uv run adsreport --check-config` after edits. Use `uv run adsreport --config path/to/config --check-config` for another directory. All four output formats are required. Thresholds are labelled assumptions for the Ads manager to review.

The sample market is amazon.de, currency EUR, and retail VAT assumption 19%. Reporting periods use Europe/Berlin. The planned Monday 09:17 Manila schedule corresponds to `17 1 * * 1` UTC. Credentials belong in local .env or GitHub Actions secrets.

See [system map](docs/architecture.md) and [build specification](docs/SPEC.md). CI repeats the locked install, lint, format, strict types, tests and CLI checks on Ubuntu. Runtime history for scheduled reports will be populated by genuine executions in P7.
