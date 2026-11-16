# Weekly analyst review process

This is the implemented PoC review process. It awaits owner sign-off. Numbers are simulated independent-retailer performance for public LEGO catalog references; findings do not describe LEGO's actual advertising or commercial results.

## 1. Establish the period and evidence

Use the latest complete German reporting week that has finished its seven-day attribution window plus one-day latency allowance. Keep the sample's fixed historical period visibly labelled. Collect the advertised-product export, normalized retail sales, costs/lifecycle and inventory snapshot for the same child-ASIN grain. Preserve originals privately. Confirm currency, VAT basis, attribution, refunds, return cost treatment and marketplace with the Ads manager before interpreting a live business result.

Validate file hashes, column aliases, required fields, dates, nonnegative source amounts, row uniqueness and join coverage. Advertising campaign rows must aggregate before joining retail totals, preventing duplicated revenue. Stop and repair invalid or incomplete inputs rather than filling them with plausible-looking values. A mature week does not guarantee Amazon has finished every late adjustment; record the export cutoff and regenerate a new version if sources change. Current live/localized exports require adapter verification; this PoC ships the English simulated export contract.

## 2. Review portfolio economics first

Check spend, ad sales, net retail revenue, contribution after ads and TACoS together. Ratios use summed numerators/denominators, not averaged product percentages. Confirm that comparable-week deltas use adjacent weeks with the same product coverage. Treat unavailable ratios as unavailable; zero sales are not infinite ACoS. Read undefined-value reasons before drawing conclusions.

Retail gross sales remove the sample's assumed 19% VAT once. Product cost, fees, logistics and expected incremental return loss produce contribution before ads; subtract ad spend for contribution after ads. Break-even ACoS derives from pre-ad contribution and the declared sales basis. Confirm these assumptions against actual merchant costs and taxation before using the output for decisions. See [input contract](INPUT-CONTRACT.md) and [assumptions](ASSUMPTIONS.md).

## 3. Triage all nine rules

Start with high severity, then medium and low, retaining each product's complete rule list. The six-item priority list deduplicates products, not evidence. Inspect the underlying week, observed values and configured thresholds:

- R1/R2: above-break-even advertising in growth/maturity, or a launch past its window. Check lifecycle and margin assumptions before discussing spend.
- R3: improved ACoS alongside declining sales and impressions. Investigate shrinking demand/coverage; improved efficiency alone does not establish a healthy business.
- R4: rising spend with low stock coverage. Check replenishment timing and the four-week sales basis; inbound stock is separate.
- R5: falling conversion with stable clicks. Inspect detail-page, offer and traffic context with the manager. The flag does not establish a cause.
- R6: a spend spike without comparable ad-sales growth. Check campaign events and attribution maturity.
- R7: negative contribution after ads. Reconcile costs, returns and sales before escalating.
- R8: three consecutive organic-share proxy declines across four comparable weeks. This residual is not Amazon's direct organic-attribution measurement.
- R9: maturity advertising near the assumed break-even boundary. Review the safety margin; it is an assumption, not an automatic target.

Healthy and in-window launch products also deserve a quick review. Absence of a flag proves only that these nine configured conditions were not met. Threshold changes require a new report version and a deliberate review of the fixture expectations.

## 4. Check commentary against the evidence

Identify each note's label and reason. AI selects controlled, product/week/metric/unit/direction-bound facts; Python validates values and renders wording. Confirm the note belongs to the displayed product and report week. The guard protects numeric attribution at that boundary; it does not prove a causal explanation or business recommendation. Unknown cause, target and review date remain unknown until agreed with the manager.

When AI is unavailable, proceed with clearly labelled deterministic templates. A successful numerical build with templates is not a successful AI request. Review request status, attempt count, guard rejections and sanitized provider status separately. Never remove fallback labels to make a demonstration appear live.

## 5. Freeze, review and approve

Review the HTML, six-sheet workbook, PDF and five-slide deck as one version. Check the footer identities, sample labels, units, source/configuration hashes, priority evidence and full commentary (including deck speaker notes). Retain the manifest digest printed by `inspect`. If anything needs correction, change the source/configuration and generate a new draft in a new directory; do not edit a generated workbook to create a competing financial calculation.

Only the human reviewer issues the explicit local approval command or approves the hosted Environment gate. Approval preserves the draft and stamps a separate bundle from persisted facts, without another model request or financial recalculation. Reinspect its approved digest before delivery. [OPERATIONS](OPERATIONS.md) contains the commands and the distinction between self-attested local identity and verified GitHub reviewer history.

## 6. Deliver and close the loop

Send only the exact approved archive. Check each channel independently. Provider acceptance does not prove inbox/channel receipt or human review. Verify both attachments and retain sanitized evidence. An uncertain send needs investigation before an explicit retry because a duplicate is possible. Disabled or missing destinations leave delivery incomplete.

Record actual manual/assisted review effort using [REVIEW-EFFORT](REVIEW-EFFORT.md). Discuss proposed investigations with the Ads manager; no bids, budgets, prices, listings, delistings or refunds are changed by this application. Any commercial action and its subsequent business outcome require separate authorization and real merchant evidence.

## Exceptions and ownership

| Exception | Action and owner |
|---|---|
| Missing/invalid source or immature week | Builder/export owner fixes the contract; analyst reviews a new version. |
| Unavailable ratio or incomparable history | Analyst reads the reason and suppresses the unsupported conclusion. |
| Provider quota/authentication/service failure | Templates keep reporting usable; owner resolves private access if desired. |
| Renderer or hash verification failure | Stop approval/delivery; builder investigates and reruns into a new directory. |
| Account-locked runner or missed schedule | Owner resolves account access; developer checks Actions history. Local report generation remains available. |
| Missing receipt or ambiguous send | Owner verifies destination; retry only with the documented duplicate risk. |
| Changed assumptions or cost data | Manager confirms the basis; builder regenerates and obtains new approval. |

Owner sign-off: **pending**. This process does not substitute for the independent release audit.
