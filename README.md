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

The current P1 implementation validates settings and thresholds, rejects unsupported configuration, and exposes the four planned command interfaces. Generate-sample, run, approve and deliver return a nonzero status identifying their implementation phase. Report generation begins in P2-P6. Scheduled reporting and delivery follow in P7.

The development checks use no API credentials. For the earlier Gemini account probe, use a dedicated Free Tier project with billing unlinked and store its key in ignored .env. That probe's SDK requirements are recorded separately in docs/evidence/p0-requirements.txt.

## Configuration

Edit config/settings.yaml and config/thresholds.yaml. Run `uv run adsreport --check-config` after edits. Use `uv run adsreport --config path/to/config --check-config` for another directory. All four output formats are required. Thresholds are labelled assumptions for the Ads manager to review.

The sample market is amazon.de, currency EUR, and retail VAT assumption 19%. Reporting periods use Europe/Berlin. The planned Monday 09:17 Manila schedule corresponds to `17 1 * * 1` UTC. Credentials belong in local .env or GitHub Actions secrets.

See [system map](docs/architecture.md) and [build specification](docs/SPEC.md). CI repeats the locked install, lint, format, strict types, tests and CLI checks on Ubuntu. Runtime history for scheduled reports will be populated by genuine executions in P7.
