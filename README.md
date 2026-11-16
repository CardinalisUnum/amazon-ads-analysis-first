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

The current implementation validates settings and thresholds, generates reproducible sample inputs, and calculates numerical KPI drafts. Approval and delivery return a nonzero status identifying their implementation phase. Rules, commentary and visual reports follow in P4-P6. Scheduled reporting and delivery follow in P7.

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

All financial calculations use Decimal. The tests reproduce the EUR 8.44 / EUR 25.13 = 33.6% break-even example and exercise zero denominators, missing weeks, halo sales and mathematical properties. The AI path remains a later implementation step, so this checkpoint requires --no-ai.

The development checks use no API credentials. For the earlier Gemini account probe, use a dedicated Free Tier project with billing unlinked and store its key in ignored .env. That probe's SDK requirements are recorded separately in docs/evidence/p0-requirements.txt.

## Configuration

Edit config/settings.yaml and config/thresholds.yaml. Run `uv run adsreport --check-config` after edits. Use `uv run adsreport --config path/to/config --check-config` for another directory. All four output formats are required. Thresholds are labelled assumptions for the Ads manager to review.

The sample market is amazon.de, currency EUR, and retail VAT assumption 19%. Reporting periods use Europe/Berlin. The planned Monday 09:17 Manila schedule corresponds to `17 1 * * 1` UTC. Credentials belong in local .env or GitHub Actions secrets.

See [system map](docs/architecture.md) and [build specification](docs/SPEC.md). CI repeats the locked install, lint, format, strict types, tests and CLI checks on Ubuntu. Runtime history for scheduled reports will be populated by genuine executions in P7.
