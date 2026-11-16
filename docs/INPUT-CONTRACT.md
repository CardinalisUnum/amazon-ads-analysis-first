# P3 input and calculation contract

The current product is a SAMPLE DATA PoC for one German marketplace in EUR. It consumes complete English CSV exports and an explicit metadata manifest. Live Amazon API ingestion is outside v1 scope.

## Source bundle

Provide manifest.json and four CSVs named ads.csv, total_sales.csv, costs.csv and inventory.csv. The SAMPLE_ prefix is also accepted, with exactly one file for each role. The optional catalog and expected-flags companions remain useful fixtures. Required records are validated before output publication.

The manifest declares schema_version 1, SAMPLE DATA label, amazon.de, EUR, the VAT rate, gross retail and net ad tax bases, Europe/Berlin, and the first/report weeks. Weeks are Monday dates. The report week must contain retail observations. File hashes, when supplied, are verified. Every consumed CSV and the manifest are fingerprinted from the same captured bytes used for parsing. Changed source content cannot silently reuse an old fingerprint.

CSV encoding is UTF-8, accepting a BOM. Numeric inputs use an ungrouped period decimal separator. Counts are nonnegative integers. Amounts and rates must be finite and nonnegative, and fractional rates are at most one. Blank required values fail with file, row and field information. Derived source percentages are recomputed from additive counts and amounts.

## Mapping and grain

config/column_map.yaml accepts source aliases and internal canonical names. If several aliases are provided for one field, nonblank text values must agree. Duplicate CSV headers and duplicate source-grain records fail.

- Ads use date, campaign, ad group, SKU and advertised child ASIN as their source key. Aggregate them to child ASIN and Monday reporting week before the retail join. Campaign names must identify source rows unambiguously within the declared grain.
- Keep total attributed Sales and Sales (promoted) separate. The former is the ACoS/ROAS denominator. The latter supports the organic-share proxy. A missing promoted-sales column leaves the proxy undefined. If halo and promoted sales are both supplied, they must reconcile to total sales within EUR 0.02 of display rounding.
- Retail has one row per child ASIN and week, with gross_sales, units and sessions. Raw child-item exports carry their date range in export metadata. Normalize one export per week to this adapter before a multiweek run. Date-free product rows from a combined multiweek export cannot establish weekly totals.
- Costs have one row per child ASIN with unit_product_cost, referral_fee_rate, referral_minimum_eur, fba_fee_per_unit, logistics_storage_per_unit, return_rate, loss_per_return, lifecycle_phase and launch_start_date.
- Inventory has one row per child ASIN and week with units_available and inbound_units. Each retail row needs its cost and inventory records. Positive retail revenue with zero units fails because the per-unit costing basis would be unknown.
- Retail-only products remain in the report with zero ad activity when absent from the supplied complete ads export. An empty ads CSV is accepted only with valid headers. An empty retail/cost/inventory export cannot establish a report.

The validated loader uses the standard library CSV parser and Pydantic models. Exact Decimal amounts avoid a float conversion through DataFrames. This implementation choice replaces the initially proposed pandas loader. It adds no application dependency.

## Financial conventions

Net retail revenue is gross revenue divided by one plus the declared VAT rate, rounded half up to cents per product-week. Source ad amounts retain their original precision. Modelled product, fee, logistics and expected return totals are rounded half up to cents per product-week.

Referral fees use average gross unit price, the configured percentage and per-unit minimum, rounded at the unit level before multiplication. This assumes a uniform selling-price/cost basis within a product-week. Refund processing and transaction-level fee reconciliation need richer inputs in a real deployment.

Expected returns cost is units times expected return rate times incremental euro loss per return. Contribution before ads is net revenue less product, Amazon, logistics/storage and return costs. Contribution after ads subtracts source ad spend. Margin after ads divides the resulting contribution by net retail revenue.

ACoS divides ad spend by total attributed ad sales. ROAS reverses those terms. TACoS uses total net retail revenue. Break-even ACoS divides pre-ad contribution by net retail revenue. Rate fields use a _pct suffix, monetary fields _eur, multiples _ratio and stock coverage _days.

The organic-share proxy is the residual of net retail revenue less promoted-SKU ad sales. It is undefined when the relevant source is absent, net revenue is zero or the residual lies outside zero to one. The sample's matching attribution periods simplify this metric. Actual click-date/order-date differences still require qualification.

## History and undefined values

Stock coverage uses current on-hand units and average daily retail units across four consecutive observed weeks, including the current week. Insufficient history or zero demand produces an undefined value with its reason. Zero stock with positive demand correctly yields zero days. Inbound units remain separate.

Week-over-week changes require an adjacent observed prior week. Missing weeks are preserved as gaps. ACoS changes use percentage points, including a zero baseline. Other relative changes need a defined, nonzero prior value. Undefined values become null in JSON and blank cells in CSV, with reasons available in the report record.

## Draft outputs and continuation

P3 produces only the numerical CSV and JSON foundation. JSON includes lifecycle dates, the exact metric values, undefined reasons, source fingerprints, a fingerprint of the validated configuration and a fingerprint of the normalized column map. Fingerprints of the normalized configuration tolerate line-ending differences across platforms.

The next rules engine should consume ProductMetrics directly, preserve Decimal values, and scope the sample expected-flags check to the manifest report_week. Human approval, rendering and delivery remain their own implementation phases.
