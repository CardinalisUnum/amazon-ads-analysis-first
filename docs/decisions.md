# Owner decisions

Recorded 2026-11-16 from the owner interview and subsequent approvals.

| Topic | Decision |
|---|---|
| Acceptance | A fully working PoC with real execution history and verified KPIs calculated on labelled sample data. Show measured operational impact. |
| Target | November 19, 2026 around 18:00 Asia/Manila. Owner review/recording availability has no fixed daily allocation yet. Reserve time before delivery. |
| Repository | CardinalisUnum/amazon-ads-analysis-first. Owner approved publication after P1 review. Repository is now public. Original private handovers remain outside Git. |
| Review | CardinalisUnum is the planned delivery reviewer. Required-reviewer Environment configuration needs the public repository for GitHub Free. |
| Scope | All four outputs and P0-P9 remain in scope. Both email and Discord need failure-alert and approved-notice demonstrations. |
| Market | amazon.de, EUR. One SKU per child ASIN in the sample. |
| Schedule | Monday 09:17 Manila, cron 17 1 * * 1. Report the latest mature Monday-Sunday week in Europe/Berlin, allowing attribution latency. |
| Catalog | Real LEGO catalog names and set IDs with simulated independent retailer ad, retail, stock and cost data. No affiliation claim. No brand logos. |
| Presentation | English EUR number formatting, navy/teal palette with text severity labels. Approved kickoff defaults. |
| License | MIT. Approved explicitly in kickoff defaults. |
| Model | Candidate gemini-3.5-flash-lite, standard free text requests, billing unlinked. Owner supplied a key described as free. Actual access and schema parse need a successful request. |
| AI scope | Short notes for all ten products. Detailed priority explanations for flagged products. Fallback notes labelled with reason. |
| VAT | Retail sample explicitly includes 19% VAT. Convert it to net once. Amazon ad-attributed sales already exclude VAT. Print the TACoS denominator. |
| Costs | Explicit landed cost, referral fee, fulfilment, storage/logistics and return loss. Record return rate and incremental euro loss per return. |
| R8 | Three consecutive weekly decreases over four comparable periods. Explicitly approved default. |
| Baseline | No stopwatch baseline supplied. Measure manual and assisted review of the same task in P8. |
| Phase gates | Stop at every phase, give evidence/progress bars, commit and push, then request approval. Applies to all agents. |

## Findings resolved by these decisions

- The original fictional-brand instruction is superseded by the owner's real-catalog request.
- Current total attributed Sales and Sales (promoted) have separate meanings and columns.
- Organic share inferred from these exports is a proxy with attribution limitations.
- A numeric allowlist cannot catch a correct number assigned to the wrong KPI. Bind claims to named facts and test metric swaps.
- Four formats include PDF in consistency checks.
- Ensure the ten sample stories cover R8 and R9 too. Multiple flags may apply to the same product.
- Approval metadata changes file hashes. Retain both versions and rerender only frozen content with approved status.

## Sources read 2026-11-16

- [Amazon report definitions](https://advertising.amazon.com/help/GYNVHW8R4QPYUS9H)
- [Amazon attribution and tax conventions](https://advertising.amazon.com/help/GX7KDKHMWQYMJ385)
- [Sales and Traffic schema](https://github.com/amzn/selling-partner-api-models/blob/main/schemas/reports/sellerSalesAndTrafficReport.json)
- [Agency worked example](https://growald-agency.de/blog-amazon-kennzahlen.html)
- [Gemini pricing](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite)
- [Gemini structured outputs](https://aistudio.google.com/docs/structured-output)
- [GitHub review environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [WeasyPrint system requirements](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)
- [WeasyPrint security advisories](https://github.com/Kozea/WeasyPrint/security/advisories)

## Dependency verification

Exact versions and Python requirement strings fetched from official PyPI JSON are in `evidence/p0-package-metadata.json`. Python 3.13.18 executes locally. Package installation and native PDF rendering are tracked separately in `STATUS.md` and the P0 evidence. Choose explicit DataFrame validation for the initial small schema, using pandas and Pydantic. Pandera is evaluated only in the compatibility probe, with no requirement to include it in the application.

| Package | Verified metadata version | Python constraint | Official release |
|---|---|---|---|
| uv | 0.13.8 | >=3.8 | [PyPI](https://pypi.org/project/uv/0.13.8/) |
| pandas | 3.1.1 | >=3.11 | [PyPI](https://pypi.org/project/pandas/3.1.1/) |
| pydantic | 2.14.3 | >=3.10 | [PyPI](https://pypi.org/project/pydantic/2.14.3/) |
| PyYAML | 6.0.3 | >=3.8 | [PyPI](https://pypi.org/project/PyYAML/6.0.3/) |
| google-genai | 3.3.0 | >=3.11 | [PyPI](https://pypi.org/project/google-genai/3.3.0/) |
| matplotlib | 3.11.2 | >=3.11 | [PyPI](https://pypi.org/project/matplotlib/3.11.2/) |
| XlsxWriter | 3.3.1 | >=3.8 | [PyPI](https://pypi.org/project/XlsxWriter/3.3.1/) |
| Jinja2 | 3.1.6 | >=3.7 | [PyPI](https://pypi.org/project/Jinja2/3.1.6/) |
| WeasyPrint | 70.0 | >=3.10 | [PyPI](https://pypi.org/project/WeasyPrint/70.0/) |
| python-pptx | 1.0.2 | >=3.8 | [PyPI](https://pypi.org/project/python-pptx/1.0.2/) |
| pytest | 9.2.0 | >=3.10 | [PyPI](https://pypi.org/project/pytest/9.2.0/) |
| pytest-cov | 7.1.0 | >=3.9 | [PyPI](https://pypi.org/project/pytest-cov/7.1.0/) |
| hypothesis | 6.170.15 | >=3.11 | [PyPI](https://pypi.org/project/hypothesis/6.170.15/) |
| ruff | 0.17.5 | >=3.7 | [PyPI](https://pypi.org/project/ruff/0.17.5/) |
| mypy | 2.4.1 | >=3.10 | [PyPI](https://pypi.org/project/mypy/2.4.1/) |
| pandera | 0.36.0 | >=3.10 | [PyPI](https://pypi.org/project/pandera/0.36.0/) |

WeasyPrint 70.0 requires Pango >=1.44 and Python >=3.10. The release fixes the EPS interpreter issue in GHSA-r543-q48m-4c9j. Keep the restricted local URL fetcher and test local resources in P6. Local Windows Pango availability and runner-native installation need separate execution evidence.

## Executed P0 checks

Python 3.13.18 installed all pinned probe packages. pandas 3.1.1 and Pandera 0.36.0 validated a frame together. Copy-on-write and default str dtype were exercised. The SDK parsed a real structured response from gemini-3.5-flash-lite. See evidence/p0-stack.json and evidence/p0-gemini.json. Billing-unlinked status relies on the owner describing this as a Free Tier key, with no billing-admin access tested here.

WeasyPrint imports fail locally with OSError because native libraries are unavailable. Installation instructions specify Pango >=1.44. This is a verified environment requirement, with successful PDF generation still required in P6. Establish Ubuntu runner support with native packages before counting that renderer as complete. Windows uv venv also encountered access denied for temporary/cache writes. The P0 probe used standard venv and pip, and P1 still requires successful uv locked install evidence.

## P1 approval

On 2026-11-16 the owner said “Okay then continue building the product” following the P0 report and P1 approval request. P1 is authorized. Pause before P2.


## P1 implementation decisions

A fresh workspace-owned UV_CACHE_DIR at .tools/p1-cache resolved the earlier Windows cache failure. The project uses uv 0.13.8, Python 3.13.18, Hatchling and src layout. uv sync --locked succeeds locally.

Only Pydantic and PyYAML are application dependencies at this phase. Add analysis and rendering libraries when their implementation phases need them. The P0 probe remains a separate environment.

| Dependency | Need | Maintenance and license source |
|---|---|---|
| hatchling 1.33.0 | Standard wheel/editable build backend | [PyPA project, MIT](https://pypi.org/project/hatchling/1.33.0/) |
| pydantic 2.14.3 | Strict structured settings and threshold validation | [Project metadata, MIT](https://pypi.org/project/pydantic/2.14.3/) |
| PyYAML 6.0.3 | Safe loading of owner-visible YAML configuration | [Project metadata, MIT](https://pypi.org/project/PyYAML/6.0.3/) |
| types-PyYAML 6.0.12.20261113 | Type stubs for strict mypy checks | [Typeshed stubs, Apache-2.0](https://pypi.org/project/types-PyYAML/6.0.12.20261113/) |
| pytest 9.2.0 | Configuration and CLI behavior checks | [pytest project, MIT](https://pypi.org/project/pytest/9.2.0/) |
| pytest-cov 7.1.0 | Coverage reporting at quality gates | [Project metadata, MIT](https://pypi.org/project/pytest-cov/7.1.0/) |
| ruff 0.17.5 | Lint and format checks | [Astral project, MIT](https://pypi.org/project/ruff/0.17.5/) |
| mypy 2.4.1 | Strict static checking of src | [Project metadata, MIT](https://pypi.org/project/mypy/2.4.1/) |

Source metadata was read on 2026-11-16. Commit-SHA action references were verified in P0. CI has contents:read permission, a ten-minute timeout and no API credentials. It runs on pushes, pull requests and manual dispatch.

The earlier tracker had corrupted Unicode progress bars and a stale P0 subtotal despite five completed task rows. P1 repairs the encoding and derives phase totals from the task statuses.

## Publication approval

On 2026-11-16 the owner approved making the reviewed repository public and requested commits under the configured owner author identity with no assistant-authorship tags. Existing commits use Patrick Jaso and have no co-author trailers. Shared handoff filenames support agent continuation and carry no claim of project authorship.

The owner-approved public-repository recovery was performed. CI still ended before job creation. P1-5 remains open. The owner can authorize P2 while this external account condition is resolved. No paid service or spending-limit change was enabled.

## P2 approval

On 2026-11-16 the owner approved P2 while P1-5 remains open and required self-testing, verification, and review for unnecessary code before publication. Pause for owner review of sample assumptions and expected flags before P3.

The P2 generator uses a fixed sample period and the approved 19% VAT convention, preserving reproducibility over time. It refuses other sample VAT settings because the expected-story fixture is tied to that approved basis. Normal report processing in P3 can validate its own declared input tax basis. Generated directories are staged and published atomically. Existing different content requires a new output path, preserving prior files.

P2 catalog identities are sourced from official English-language German LEGO pages read on 2026-11-16. Simulated costs use 34% of net price for landed cost, 15% referral with a EUR 0.30 minimum, modelled fulfilment of max(EUR 2.50, 7% gross price), EUR 0.20 additional logistics/storage, and a 4% return rate with half net price as incremental loss per return. These and observed advertising ranges require owner review in the P2 gate.
