# Sample data assumptions

SAMPLE DATA. This document describes an invented independent retailer. The product names and set numbers come from official LEGO pages linked in P2-SAMPLE-REVIEW.md. Commercial performance and procurement costs are synthetic. Owner review of these ranges is pending at the P2 gate.

## Dataset and tax basis

- Ten products, eight Monday-Sunday periods from September 7 through November 1, 2026, EUR and amazon.de. These are fixed sample business periods. Generating these files does not establish execution history for those dates.
- Retail input is normalized from a hypothetical child-item export per period. Its week field comes from period metadata. The ads input mimics the classic English daily seller Sponsored Products report, with two campaign rows per product-day.
- Sample ASINs begin SAMPLE and have no lookup relationship to real Amazon listings. Seller SKUs begin SAMPLE-. Manufacturer set numbers are separate catalog identifiers.
- Retail gross revenue includes 19% VAT. Ad-attributed revenue is tax-exclusive. All modeled cost amounts and ad spend are net costs to the retailer. Preserve additive amounts before computing ratios.
- Scenario expectations use the approved 19% VAT setting and default config/thresholds.yaml. The generator checks this fixed sample tax basis. Changed tax assumptions need a revised scenario fixture.
- Zero halo sales, one unit per attributed purchase, fixed product prices and matched sample periods simplify reconciliation. An organic-share residual is interpretable here by construction. Live account exports require attribution and timing qualification.

## Commercial assumptions

| Quantity | Sample assumption |
|---|---|
| Gross selling price | EUR 9.99-54.99. Retailer assumptions, independent of current catalog shop pricing. |
| Units | Seeded base of 80-140 per active product-week. Low-stock scenario scales latest units by 1.2. Declining-sales scenario scales latest units by 0.75. |
| Landed cost | 34% of unrounded net unit selling price, rounded to cents. Includes acquisition and inbound freight. |
| Referral fee | 15% of gross unit price, EUR 0.30 minimum per unit. Round the per-unit fee to cents. Confirm category and fee basis before any real deployment. |
| Fulfilment | Greater of EUR 2.50 and 7% of gross unit price, rounded to cents. A hypothetical per-unit fee pending actual size and weight data. |
| Storage/logistics | Additional EUR 0.20 per sold unit, excluding the costs already included in landed cost and fulfilment. |
| Returns | 4% expected return rate multiplied by incremental euro loss per return. Loss equals half the net unit price, rounded to cents. Avoid an additional refund deduction from sample revenue. |
| Sessions | Six sessions per retail unit. All zero before the simulated new listing launches. |
| Normal ad conversion | Approximately 12% purchases per click, subject to integer rounding. The conversion-drop story deliberately lowers it. |
| Normal ad share | Approximately 35% of retail units. The declining-organic and negative-contribution stories vary this share. |
| Availability | Five current-week unit volumes on hand, except the low-stock case, which has five units. Inbound stock is recorded separately. Snapshots assume replenishment and provide no inventory-movement ledger. |

These are scenario-design assumptions. They have no empirical calibration to an actual LEGO retailer or Amazon advertising account. The fixture tests establish arithmetic consistency and intended rule conditions.

## Lifecycle and expected flags

The simulated retailer lists Creative Pets on October 5, 2026. It has four prelaunch weeks with zero activity and stays inside the eight-week launch window in the review week. Other launch/growth products use August 3 as their listing start. A retailer listing launch is independent of a manufacturer's product release date.

The expected-flags file applies only to the latest sample week, October 26-November 1. It expects both healthy maturity products and the in-window launch to have no flags. It covers every rule R1-R9 across the remaining products. Production-engine verification completed in P4 with exact-match and boundary tests.

All configurable rule thresholds in config/thresholds.yaml remain assumptions for the reviewing Ads manager. A changed threshold needs a new review of the expected fixture. R8 requires three declines over four consecutive comparable weeks.

## Rounding and reproducibility

Money uses decimal arithmetic with half-up cent rounding. Unit and click counts use nearest-integer rounding. Integer allocation preserves exact weekly counts and euro cents across the fourteen campaign-day rows. Recompute ratios from summed amounts. Undefined zero-denominator source rates are blank.

Seed 42 produces the committed sample. The same seed in the pinned Python environment produces byte-identical files. A manifest records SHA-256 hashes of every companion file. The manifest omits execution timestamps so that regeneration remains deterministic. Actual execution records are in runs/run-log.jsonl, separately from the simulated sample periods.

## References

- [Amazon seller report definitions](https://advertising.amazon.com/help/GYNVHW8R4QPYUS9H)
- [Amazon attribution and VAT](https://advertising.amazon.com/help/GX7KDKHMWQYMJ385)
- [Amazon Germany pricing and variable fulfilment fees](https://sell.amazon.de/preisgestaltung?lang=en-GB)
- [Product catalog references](P2-SAMPLE-REVIEW.md)
