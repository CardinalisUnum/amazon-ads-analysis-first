# Build specification

Owner decisions in decisions.md supersede older defaults below. The application is pending.

## 5. Architecture

```
data/sample/            generated CSVs (SAMPLE), committed for reproducibility
config/
  settings.yaml         marketplace, VAT rate, schedule, model ID, output toggles
  thresholds.yaml       rule thresholds (each marked ASSUMPTION)
  column_map.yaml       Amazon column names → internal names (old + new console names)
src/adsreport/
  cli.py                `adsreport generate-sample | run | approve | deliver`
  io/loader.py          read + map columns + validate schema
  kpi/engine.py         pure functions, no I/O
  rules/engine.py       pure functions, returns Flag objects with severity + evidence
  ai/commentary.py      one batched Gemini call → pydantic objects
  guard/numbers.py      rejects any number not in the allowed set
  ai/fallback.py        deterministic template commentary
  render/charts.py      matplotlib → SVG/PNG
  render/xlsx.py        XlsxWriter workbook
  render/html.py        Jinja2 → HTML
  render/pdf.py         WeasyPrint (local-only fetcher)
  render/pptx.py        python-pptx deck
  runlog.py             append-only JSONL run records
  approval.py           DRAFT → APPROVED state, with approver + timestamp
templates/              HTML/CSS templates
tests/                  unit, property, golden-file, end-to-end
docs/                   PROCESS.md, ASSUMPTIONS.md, LIMITS.md, decisions.md, loom-script.md
.github/workflows/      ci.yml, weekly-report.yml
```

### 5.1 Data flow (one weekly run)

1. **Load:** read the Advertised Product report, total sales, costs and inventory CSVs. Map column names. Validate the schema. On any error, fail loudly.
2. **Compute:** KPIs per product per week, plus week-over-week (WoW) deltas.
3. **Flag:** apply the rules (§6) and produce a severity-sorted priority list.
4. **Comment:** make one Gemini call with only the computed facts. Validate the structured output, then run the number guard. If the call fails, the schema is invalid, or the guard rejects it, use the template for that product and record why.
5. **Render:** produce XLSX, HTML, PDF and PPTX from the **same** in-memory report object. Every output is stamped `DRAFT · SAMPLE DATA`.
6. **Log:** append a run record (§7.3).
7. **Gate:** the `deliver` job waits for approval in the `client-delivery` environment. Once approved, outputs are re-stamped `APPROVED by <user> at <timestamp>` and delivered (artifact plus the chosen alert channel).

### 5.2 Input schema

**Amazon Sponsored Products Advertised Product report.** Classic console columns include: Date, Campaign Name, Ad Group Name, Advertised SKU, Advertised ASIN, Impressions, Clicks, Click-Thru Rate (CTR), Cost Per Click (CPC), Spend, 7 Day Total Sales, Total Advertising Cost of Sales (ACoS), Total Return on Advertising Spend (RoAS), 7 Day Total Orders (#), 7 Day Total Units (#). Sellers' Sponsored Products use a 7-day attribution window.

**VERIFY at P0:** Amazon has renamed some columns in its newer report builder (e.g. "Purchases" and "Sales (promoted)" style names). `column_map.yaml` must accept both old and new names for every field, and the README must say which version the sample mimics.

**Supporting inputs** (synthetic, as in an agency's own data room):
- `total_sales.csv`: week, ASIN, total ordered sales (gross, incl. VAT), units, sessions. Mimics a Business Report; **VERIFY** the real column names and document them.
- `costs.csv`: ASIN, unit product cost, Amazon referral fee %, FBA fee per unit, logistics per unit, return rate %, lifecycle phase (launch / growth / maturity), launch start date.
- `inventory.csv`: week, ASIN, units available, inbound units.

**Net revenue:** amazon.de with 19% German VAT, so `net_revenue = gross_sales / 1.19`. This is an **ASSUMPTION** (confirm the VAT treatment with the owner and record it in ASSUMPTIONS.md).

### 5.3 Sample data spec

- Real LEGO catalog references with simulated independent retailer performance, **10 products**, **8 weeks**, EUR, amazon.de.
- Seeded random generator, so the same seed gives byte-identical CSVs.
- **Each product must deliberately trigger a known story**, so the demo shows every rule:
  - 2 healthy maturity products
  - 1 launch product inside its window (ACoS above break-even, but OK)
  - 1 launch product **past** its window and still above break-even
  - 1 growth product with ACoS above break-even
  - 1 product whose ACoS falls while total sales and impressions fall ("efficiency illusion")
  - 1 product scaling ad spend with under 14 days of stock coverage
  - 1 product whose conversion drops while clicks are stable (weak detail page)
  - 1 product with a spend spike and no extra sales
  - 1 product with negative contribution after ads
- Keep an `expected_flags.yaml` mapping product → expected rule IDs. **A test asserts the engine finds exactly these.**

---

## 6. Rules engine (initial set; all thresholds are ASSUMPTIONS in `thresholds.yaml`)

| ID | Rule | Default threshold | Severity |
|---|---|---|---|
| R1 | Growth or maturity product with ACoS > break-even ACoS | strict `>` | High |
| R2 | Launch product past its launch window with ACoS > break-even | window = 8 weeks | High |
| R3 | ACoS improved WoW, but total sales **and** impressions fell ("efficiency illusion") | ACoS −5 pp, sales −10%, impressions −10% | Medium |
| R4 | Ad spend up WoW while stock coverage < N days | spend +10%, coverage < 14 days | High |
| R5 | Conversion rate fell WoW while clicks stayed stable (likely detail-page issue) | CVR −20% relative, clicks ±10% | Medium |
| R6 | Spend spike without a matching sales rise | spend +30%, ad sales +5% or less | Medium |
| R7 | Contribution after ads negative | < 0 € | High |
| R8 | Organic share falling for 3 consecutive weeks | strictly decreasing | Low |
| R9 | Maturity product with ACoS not "well below" break-even | ACoS > 0.8 × break-even | Low |

Each Flag records: rule ID, product, week, severity, the exact metric values that triggered it, the threshold, and a one-line plain-English reason. **Rules never recommend bid, price or listing changes as decisions**; they point to what a person should review.

Stock coverage = `units_available / avg_daily_units_last_4_weeks`. If the average daily units is 0, report coverage as undefined, never as infinity or an error.

---

## 7. AI commentary, guard, approval, run log

### 7.1 Commentary (one call per run)
- Input: only the computed facts for flagged products (top N by severity, all ten sample products, prioritised by severity), as JSON.
- Output schema (pydantic), per product: `asin`, `what_happened`, `likely_cause`, `planned_change_to_review`, `target_and_review_date`, `confidence` (low / medium / high).
- Prompt rules: English; use only the numbers provided; say "unknown" rather than guess; never recommend automatic bid, price, delisting or refund decisions; frame actions as "review with the Ads manager"; at most 70 words per field.
- Handle `429` / quota errors with **one** retry after the server's retry delay, then fall back to the template. **Never** fail the whole run because of the AI.

### 7.2 Number guard
- Extract every numeric token from the AI text (integers, decimals with `.` or `,`, percentages, € amounts, "x" multipliers, dates).
- The allowed set = every value the engine computed for that product (raw plus display-rounded to 0, 1 and 2 decimals), plus the dates in the report. Bind claims to metric, product, week, unit and direction.
- Any number outside the allowed set → reject that product's AI text, use the template, and log `guard_rejected` with the offending tokens.
- Tests: an injected hallucinated number is rejected; legitimate rounded numbers pass; and a test proves the template path is used.

### 7.3 Run log (`runs/run-log.jsonl`, append-only)
Fields: `run_id`, `trigger` (schedule / manual / test_failure), `started_at`, `finished_at`, `status` (success / failure), `failed_step`, `products`, `flags_by_severity`, `ai_used` (true/false), `guard_rejections`, `outputs` (file names + SHA-256), `approval` (pending / approved_by / approved_at), `git_sha`.
**Success rate** = successful scheduled runs ÷ all scheduled runs, excluding `test_failure`. Shown in the README.

### 7.4 Approval gate
- `weekly-report.yml`: job `build` (schedule + `workflow_dispatch`) → uploads the DRAFT outputs as an artifact → job `deliver` with `environment: client-delivery` (required reviewer = owner) → on approval, re-stamps the outputs as APPROVED, appends approval data to the run log, and sends the delivery notice.
- If the repo is ever made private on the Free plan, required reviewers stop working. Document this in LIMITS.md, with a `workflow_dispatch` approval fallback.

### 7.5 Scheduling facts to document in LIMITS.md
- Scheduled workflows can be delayed during busy periods, especially at the top of the hour. Schedule at an off-minute, e.g. `17 1 * * 1` (Monday 09:17 Manila).
- In a public repo, scheduled workflows are automatically disabled after 60 days with no repository activity. The run-log commit counts as activity; verify this at P7 and document it.

---

## 8. Outputs and visual standard

One report object → four renderers. **The figures must be identical across all four** (an automated test compares them).

| Output | Must contain |
|---|---|
| **XLSX** | Sheet 1 "Summary": KPI tiles (spend, ad sales, total sales, TACoS, contribution after ads) with WoW deltas. Sheet 2 "Priorities": flags sorted by severity, with conditional formatting. Sheet 3 "Products": full KPI table, frozen header, number formats. Sheet 4 "Charts": native Excel charts (TACoS trend, contribution after ads by product, ACoS vs break-even). Sheet 5 "Commentary". Sheet 6 "Run info": run ID, DRAFT/APPROVED status, SAMPLE DATA, assumptions link. |
| **HTML** | Header with status badges (DRAFT/APPROVED, SAMPLE DATA). KPI tiles. A priority list with severity chips. Charts (SVG). Per-product cards: KPIs, flags, commentary (labelled "AI-drafted, guard-checked" or "template"). Footer: assumptions, data source, run ID. |
| **PDF** | Same HTML, rendered with print CSS: A4, page numbers, no cut-off tables or charts. |
| **PPTX** | 5 slides: (1) title + status, (2) KPI overview, (3) top priorities, (4) product highlights with charts, (5) review items + approval status. |

Visual rules: one colour palette shared across outputs; severity colours paired with text labels (never colour alone); readable at 100% zoom; no chart without axis labels and units; € and % formatted consistently (pick the German or English number format at the interview and apply it everywhere).

---

## 9. Quality gates (run before claiming any task is done)

```
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src/
uv run pytest --cov=src/adsreport --cov-report=term-missing
uv run adsreport generate-sample --seed 42
uv run adsreport run --input data/sample --out out/ --no-ai     # deterministic path
uv run adsreport run --input data/sample --out out/             # AI path (needs GEMINI_API_KEY)
```

Required test types:
- **Unit:** every KPI formula, including the 33.6% worked example and divide-by-zero cases (0 spend, 0 sales, 0 units).
- **Property (hypothesis):** e.g. ACoS × ROAS = 100 when both are defined; contribution after ads = contribution before ads − ad spend.
- **Rules:** `expected_flags.yaml` matches exactly.
- **Guard:** rejects invented numbers and accepts legitimate rounding.
- **Golden file:** the deterministic `--no-ai` run produces the same KPI table each time (snapshot).
- **Cross-output:** values in the XLSX, HTML text and PPTX text match the report object.
- **End-to-end:** generate sample → run → all 4 files exist, are non-empty, open without error, and carry the SAMPLE DATA marker.

---
