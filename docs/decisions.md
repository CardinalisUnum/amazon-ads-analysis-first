# Owner decisions

Recorded 2026-11-16 from the owner interview and subsequent approvals.

| Topic | Decision |
|---|---|
| Acceptance | A fully working PoC with real execution history and verified KPIs calculated on labelled sample data. Show measured operational impact. |
| Target | November 19, 2026 around 18:00 Asia/Manila. Owner review/recording availability has no fixed daily allocation yet. Reserve time before delivery. |
| Repository | CardinalisUnum/amazon-ads-analysis-first. Keep private during build. Publish sanitized content after owner review. Original private handovers remain outside Git. |
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
