# P2 sample review

SAMPLE DATA. Independent retailer simulation using official LEGO catalog identities. Financials, stock, lifecycle and advertising are invented. This review covers the final sample week, October 26-November 1, 2026.

| Sample ID | LEGO set and story | ACoS | Break-even | Contribution after ads | Stock days | Expected flags |
|---|---|---:|---:|---:|---:|---|
| SAMPLE0001 | 10696 Medium Creative Brick Box, healthy | 18.0% | 35.4% | EUR 880.80 | 35.0 | None |
| SAMPLE0002 | 10698 Large Creative Brick Box, healthy | 18.0% | 37.3% | EUR 1446.51 | 35.0 | None |
| SAMPLE0003 | 11034 Creative Pets, launch_inside | 60.0% | 35.4% | EUR 395.78 | 35.0 | None |
| SAMPLE0004 | 11035 Creative Houses, launch_expired | 60.0% | 37.4% | EUR 994.55 | 35.0 | R2 |
| SAMPLE0005 | 11036 Creative Vehicles, above_break_even | 60.0% | 37.4% | EUR 671.20 | 35.0 | R1 |
| SAMPLE0006 | 11037 Creative Space Planets, efficiency_illusion | 10.0% | 35.4% | EUR 747.10 | 27.8 | R3, R8 |
| SAMPLE0007 | 11039 Creative Food Friends, negative_contribution | 70.0% | 14.0% | EUR -224.34 | 35.0 | R1, R7 |
| SAMPLE0008 | 11040 Magical Transparent Box, conversion_drop | 18.0% | 35.4% | EUR 793.11 | 35.0 | R5 |
| SAMPLE0009 | 11041 Creative Dinosaurs, spend_spike | 30.0% | 35.4% | EUR 511.44 | 35.0 | R6, R9 |
| SAMPLE0010 | 11042 Creative Happy Box, low_stock | 24.0% | 37.3% | EUR 1575.72 | 0.3 | R4 |

The seed-42 table was independently recalculated from the exported rows in tests/test_sample.py. This fixture calculation checks the sample stories. The production KPI and rules engines are still P3 and P4 deliverables.

## Review decisions requested

- Approve these latest-week expected flags and the ten story assignments.
- Approve the explicit sample ranges and limitations in ASSUMPTIONS.md.
- Authorize P3 after reviewing this checkpoint. P1-5 remains open until hosted CI runs successfully.

## Catalog provenance

Official English-language German catalog pages were read on 2026-11-16. Catalog names and set numbers are verifiable. Retired or sold-out catalog status can coexist with a hypothetical independent retailer holding stock. A sample launch is the retailer listing launch.

- [10696 Medium Creative Brick Box](https://www.lego.com/en-de/product/lego-medium-creative-brick-box-10696)
- [10698 Large Creative Brick Box](https://www.lego.com/en-de/product/lego-large-creative-brick-box-10698)
- [11034 Creative Pets](https://www.lego.com/en-de/product/creative-pets-11034)
- [11035 Creative Houses](https://www.lego.com/en-de/product/creative-houses-11035)
- [11036 Creative Vehicles](https://www.lego.com/en-de/product/creative-vehicles-11036)
- [11037 Creative Space Planets](https://www.lego.com/en-de/product/creative-space-planets-11037)
- [11039 Creative Food Friends](https://www.lego.com/en-de/product/creative-food-friends-11039)
- [11040 Magical Transparent Box](https://www.lego.com/en-de/product/magical-transparent-box-11040)
- [11041 Creative Dinosaurs](https://www.lego.com/en-de/product/creative-dinosaurs-11041)
- [11042 Creative Happy Box](https://www.lego.com/en-de/product/creative-happy-box-11042)
