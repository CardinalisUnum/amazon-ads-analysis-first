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

## P3 approval

On 2026-11-16 the owner approved the P2 expected flags and sample assumptions and authorized P3. P2-3 and P2-5 are complete. P1-5 stays open. Preserve frequent committed/pushed checkpoints and exact resume steps for continuation by another agent. Pause before P4.

P3 uses the standard library CSV reader with typed Pydantic source records and Decimal arithmetic. This replaces the planned pandas DataFrame loader with a smaller explicit implementation that preserves source precision and avoids a production dependency used only for parsing. P0's pandas/Pandera compatibility evidence remains historical verification. Source amounts are captured and hashed from the actual parsed bytes.

Hypothesis 6.170.15 (MPL-2.0, https://pypi.org/project/hypothesis/6.170.15/) is added only to the development group for the required mathematical property tests. Application dependencies remain Pydantic and PyYAML. The shared bundle publisher was extracted from the sample generator for two actual callers, preserving the existing publish/retry behavior.

## P4 approval

On 2026-11-16 the owner approved P4 and requested that the completed phase and exact continuation handoff be pushed for another agent. P5 requires a separate approval. P1-5 stays open.

P4 evaluates only the requested report week and uses historical KPI records for supporting comparisons. Launch age is evaluated at the report week's Sunday, with a strict past-window comparison (day 57 is beyond an eight-week window). Priority selection defaults to six products via priority_products. Every flag is retained independently of that display limit.

All nine rules match the approved final-week sample expectations. Missing or nonfinite observations produce skipped-rule records. Exact Decimal/date evidence is serialized through typed Flag models. P4 adds no dependency and preserves the numerical CSV snapshot.

## P5 approval

On 2026-11-16 the owner said “Continue” after the P4 report and P5 approval request. P5 is authorized. Stop before P6 and push the implementation, tests, evidence and exact handoff. P1-5 remains open.

P5 uses structured metric claims and controlled review choices. Python validates product, week, metric, unit, direction and display rounding, then renders canonical labels. Unsupported causes, targets and review dates remain unknown. This makes numeric attribution enforceable without trusting prose interpretation. All ten latest-week sample products receive commentary independently of the six priority rows.

P5 adds the official google-genai 3.3.0 SDK, pinned to the version already exercised in P0. It supports Python 3.13 and is Apache-2.0 licensed. See [package metadata](https://pypi.org/project/google-genai/3.3.0/) and [official SDK](https://googleapis.github.io/python-genai/), checked 2026-11-16. Transitive dependencies are captured by uv.lock. [Standard model input/output remain free on Free Tier](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite), with quota and provider terms. Billing-unlinked status is owner-attested, not independently verified through billing administration.

The first local live attempt and a diagnostic request both received HTTP 400 for serving-schema complexity. The serving schema now omits descriptive metadata, date format and length bounds, while retaining its object types, required fields and controlled choices. Full constraints still run locally per product. The third live request parsed successfully, and all ten notes passed the guard. Evidence separates this manual verification from future scheduled history.

SDK 3.3.0 Interactions uses status_code/body exceptions distinct from legacy code/details errors. A mocked HTTP transport exposed this during testing. The adapter reads both public attribute shapes, sanitizes the outcome and never persists exception text. A transport test confirms attempts=1 prevents hidden retry. Automatic continuation is disabled, store=false, no tools are supplied, and each network attempt has a sixty-second timeout. A quota response permits one application retry after the provider delay, waited in chunks of at most sixty seconds. Other failures immediately use templates.

The explicit GEMINI_FREE_TIER_CONFIRMED flag records the existing owner confirmation. Unverified models and unconfirmed projects receive templates without a request. The local ignored .env flag was set from the owner's existing Free Tier attestation. No billing setting was changed. A replacement key must be saved privately before unattended operation.

## P6 approval

On 2026-11-16 the owner said “Continue” after the P5 report and P6 approval request. P6 is authorized. Stop before P7. Build and verify all four outputs, then commit and push the implementation, evidence and continuation handoff. P1-5 remains open.

## Remaining-work authorization

After the P6 gate on 2026-11-16, the owner requested “Continue and complete it when you can” and a consolidated list of problems needing owner action before running the app. This authorizes P7 and the remaining buildable documentation/readiness work without repeated phase approval questions. Keep phase checkpoints, self-testing, honest task acceptance, and pushed handoffs. External account configuration, actual human review/receipts, measured owner effort and the independent release audit cannot be invented or counted as complete. No billing/spending changes or paid service is authorized.

The visual direction follows the approved navy and teal palette. Use a white analytical report, dark navy section headings, teal for measured trends and text-backed severity colors. Keep catalog names and sample identifiers together. A spacious overview leads into evidence tables, charts and per-product commentary. Use readable sans-serif type and restrained borders, without decorative motion or external assets. All formats share the same report identity and Python-calculated values. These are static review artifacts rather than an editable financial model.

P6 adds matplotlib 3.11.2 (Matplotlib license), XlsxWriter 3.3.1 (BSD-2-Clause), Jinja2 3.1.6 (BSD-3-Clause), WeasyPrint 70.0 (BSD-3-Clause) and python-pptx 1.0.2 (MIT), following the approved Python renderer specification. Development-only openpyxl 3.1.5 (MIT) and pypdf 7.1.0 (BSD-3-Clause) verify artifacts. Release metadata was checked on 2026-11-16 at each project's official PyPI endpoint. The exact pins and transitive dependencies are in pyproject.toml and uv.lock. Sources are [matplotlib](https://pypi.org/project/matplotlib/3.11.2/), [XlsxWriter](https://pypi.org/project/XlsxWriter/3.3.1/), [Jinja2](https://pypi.org/project/Jinja2/3.1.6/), [WeasyPrint](https://pypi.org/project/weasyprint/70.0/), [python-pptx](https://pypi.org/project/python-pptx/1.0.2/), [openpyxl](https://pypi.org/project/openpyxl/3.1.5/) and [pypdf](https://pypi.org/project/pypdf/7.1.0/).

The missing Windows Pango dependency was resolved locally using checksum-pinned official MSYS2 packages. scripts/setup_windows_pdf.py extracts only DLLs and font configuration to ignored .tools. It changes no billing setting and installs no system application. Pango 1.58.2 renders the PDF successfully. The Ubuntu native-library workflow step is committed but cannot be verified on hosted runners while the account is locked.

Portfolio TACoS is computed from summed spend and net revenue. Week-over-week differences require adjacent weeks and identical product coverage. Monetary changes are EUR, with TACoS changes in percentage points. No financial formula was moved to AI, spreadsheets or templates. Optional catalog metadata is validated and fingerprinted, preserving manufacturer set numbers separately from ASINs/SKUs.

The four renderers share ReportView. A deterministic content ID and per-file artifact manifest support later frozen approval. Packaging timestamps use a documented canonical epoch; actual runtime history is not inferred from file properties. P7 must retain exact artifact bytes/hashes plus real run and reviewer timestamps. P6 only tests approval presentation, without approving or delivering a sample.

Native Excel and PowerPoint opened the generated files. All PDF pages and five slides were rendered and inspected, and desktop/mobile browser checks found no external assets or horizontal page overflow. The full ten-product commentary remains in PPTX speaker notes, with two highlights visible on the last slide. Workbook previews cover bounded views, while automated tests compare all exported numeric rows.

Two normal P6 AI runs used safe service-error fallback. An ordered-batch diagnostic returned HTTP 503. One separate real diagnostic returned structured output. That captured response was guard-checked for ten accepted notes in an explicitly labelled replay, which made no new request. No P6 fresh successful normal-CLI AI claim is made. provider_error_status was added to preserve sanitized numeric HTTP errors for future troubleshooting. P5's successful live batch remains historical evidence. Both offline and replay paths render without changing KPIs.

## P7/P8 local completion and remaining acceptance

The owner authorized completing remaining buildable work. Frozen approval, genuine local history, SMTP/Discord adapters, weekly workflow, owner Environment configuration, launcher and readiness commands are implemented. The free public workflow remains blocked before startup by the account lock. No real receipt, human approval, unattended success or review saving is invented. The consolidated owner actions and separate independent audit handoff are the next work.

Local approval is self-attested and manifest-bound. Hosted approval additionally verifies current run review history; reruns must start a fresh workflow and obtain a new review. Delivery keeps per-channel acknowledgements, preserves uncertainty after possible external acceptance, and requires an explicit potentially duplicating retry. Historical sample reporting dates remain distinct from actual UTC execution. Publication checks exclude unit/setup logs and local tooling from operational history and source distributions. No paid service, billing change or exposed key promotion was performed.

## Gmail sender selection

On 2026-11-16 the owner selected an existing personal Gmail account with app-password support as the SMTP sender. Use smtp.gmail.com:587 with STARTTLS. Sender/recipient addresses and the generated application password must be configured privately. Local non-secret defaults were prepared with notifications disabled; existing private values were preserved. No message, authentication attempt or receipt is claimed from this selection.

## Deferred Gmail setup and readiness checks

On November 17, 2026 the owner asked to bookmark the Gmail setup position and continue testing the remaining system. GMAIL-SETUP.md preserves the exact resumption steps, with links from RESUME and OWNER-ACTIONS. Notifications remain disabled and private destinations are not configured. Continue local checks without credential requests or actual messages. This builder readiness pass does not replace P9 independent review or complete missing external acceptance.

Readiness regression checks found and fixed output paths that could place approval/delivery files inside a frozen bundle, plus symbol-only reviewer names. Resolved approval and archive destinations must preserve frozen directories. Neither the financial engine nor rule thresholds/sample facts were changed. Test approvals stay explicitly labelled and never represent the owner's approval.
