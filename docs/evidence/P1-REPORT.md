# P1 gate report

Updated 2026-11-16. The local scaffold is verified. GitHub CI is awaiting a successful hosted run.

| Task | Evidence |
|---|---|
| P1-1 environment | pyproject.toml, uv.lock, src layout, uv sync --locked exit 0 |
| P1-2 quality | Ruff lint and format pass, strict mypy passes, 21 tests pass with 98% coverage |
| P1-3 repository basics | MIT license, .gitignore, .env.example and README development instructions |
| P1-4 CLI | Installed adsreport command exposes generate-sample, run, approve and deliver, plus configuration validation |
| P1-5 CI | Workflow schema validated with actionlint 1.7.12. Push and manual dispatch reached GitHub but started zero jobs because of a provider account restriction. Green-run evidence remains pending. |
| P1-6 configuration | Settings and all nine rules' threshold assumptions loaded through strict Pydantic schemas. Tests cover malformed YAML, unsafe tags, missing files, unknown fields, negative/non-finite values and invalid output selections. |

## Local results

```text
uv sync --locked
Resolved 22 packages
Checked 22 packages

uv run ruff check .
All checks passed!

uv run ruff format --check .
16 files already formatted

uv run mypy --strict src/
Success: no issues found in 4 source files

uv run pytest --cov=src/adsreport --cov-report=term-missing
21 passed
TOTAL coverage 98%

uv run adsreport --check-config
Configuration valid.
```

Full command output is in p1-local.txt. Coverage includes CLI and configuration code. The sample generator, KPI engine, rules, commentary, rendering and delivery are scheduled for their respective phases. The command interfaces return a nonzero exit until their operation is implemented.

## Workflow evidence

- [Push run](https://github.com/CardinalisUnum/amazon-ads-analysis-first/actions/runs/43789455238)
- [Manual recovery attempt](https://github.com/CardinalisUnum/amazon-ads-analysis-first/actions/runs/43789688091)
- Workflow registration is active and repository Actions permissions are enabled.
- Independent schema validation is in p1-workflow-validation.json.

Standard hosted runners in public repositories are free according to [GitHub billing documentation](https://docs.github.com/en/billing/concepts/product-billing/github-actions). The owner approved publication and the repository is now public. The recovery dispatch still ended before jobs. Account-level attention is required to establish a green hosted run.

## Publication review

The 34 tracked files were checked against the supplied credential and known private handover and project-account details. Those values were absent. The original handovers, local .env, probe environments, prior research drafts and generated study-guide output remain outside tracked publication content.

## Next phase

Request owner approval to begin P2 with P1-5 explicitly open while the provider account restriction is resolved. Otherwise keep P1 at this checkpoint. P2 generates ten catalog-linked products across eight sample weeks with deterministic files, expected flags and documented assumptions.

## Public recovery

The owner approved publication. Repository visibility was changed to public, and [public recovery run](https://github.com/CardinalisUnum/amazon-ads-analysis-first/actions/runs/43790137243) still returned startup_failure before jobs. See p1-ci.json. P1 remains 5/6 complete, with overall weighted progress 11.7%. Commit author identity is the configured owner, with no assistant co-author trailers.
