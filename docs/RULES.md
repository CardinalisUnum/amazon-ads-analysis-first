# P4 rule contract

Rules consume typed ProductMetrics from the KPI engine and the owner-approved Thresholds configuration. evaluate_rules evaluates the requested report week and retains historical rows only as supporting evidence. It makes no external calls and mutates no KPI values.

## Comparisons

| Rule | Condition | Severity |
|---|---|---|
| R1 | Growth or maturity ACoS strictly greater than product break-even ACoS | High |
| R2 | Launch age at the report week's Sunday is strictly greater than 8 complete weeks, and ACoS strictly exceeds break-even | High |
| R3 | ACoS change is at most -5 percentage points, net revenue change at most -10%, and impression change at most -10% | Medium |
| R4 | Spend change is at least +10%, with stock coverage strictly below 14 days | High |
| R5 | Ad CVR change is at most -20% relative, with clicks within inclusive -10% to +10% | Medium |
| R6 | Spend change is at least +30%, with attributed sales growth at most +5% | Medium |
| R7 | Contribution after ads is strictly below EUR 0 | High |
| R8 | Estimated organic share strictly decreases through three consecutive transitions, requiring four consecutive observed weeks | Low |
| R9 | Maturity ACoS strictly exceeds 0.8 times product break-even ACoS | Low |

Values above are configurable defaults from thresholds.yaml. R1's break-even benchmark and R7's zero-profit boundary are financial definitions. Monetary rates stay Decimal and configured float values are converted through their decimal text before comparison.

For R2, exactly 56 days at the week end remains at the boundary. Day 57 is past the configured eight-week window. Launch products remain eligible for the other rules, including the negative-contribution rule. An in-window high-ACoS launch avoids R1/R2 but can still need review for other evidence.

## Missing evidence

A missing, undefined or nonfinite metric skips only the dependent rule. The output records the rule ID, product, report week and reason. Missing history never becomes a fabricated zero. Zero is a valid observed value, including zero stock with positive demand.

R8 looks up every required Monday explicitly. Gaps, missing residuals and invalid/nonfinite residuals produce a skipped record. A flat or increasing step prevents the decline flag. Duplicate product-week KPI records and an absent requested report week are invalid rule requests.

## Flag and priority records

A Flag includes rule_id, asin, week, severity, evidence, thresholds and reason. Evidence contains exact Decimal observations and, where relevant, typed dates. JSON serializes monetary/rate values as decimal strings and dates as ISO dates. Round-trip tests preserve the typed record.

Flags sort by severity (high, medium, low), ASIN and rule ID. Priorities are deduplicated by product and week, ordered by the strongest flag. Each priority keeps every rule ID attached to that product, including lower-severity flags. The configurable priority_products default is six. All flags and skipped records remain in the report regardless of that limit.

All reasons describe observations and ask for review. They leave commercial decisions with the human reviewer. A conversion decline is evidence to investigate, with its cause still unproven.

## Normal entry point

```shell
uv run adsreport run --input data/sample --out out/rule-draft --no-ai
```

The JSON stage is rules and includes analysis.report_week, analysis.flags, analysis.skipped and analysis.priorities. Existing product metrics and the numerical CSV retain their P3 format. The sample's exact-match test is scoped to the final week in expected_flags.yaml. Numerical JSON strings should be handled as Decimal when used outside the existing typed pipeline.
