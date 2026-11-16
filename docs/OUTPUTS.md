# Visual output contract

P6 publishes XLSX, HTML, PDF and PPTX from one typed ReportView. The normal run retains the numerical CSV, report.json, SVG/PNG charts and artifacts.json. All normal outputs remain DRAFT and SAMPLE DATA. docs/examples is a deterministic offline sample, not an approved or delivered report.

## Native setup

```shell
uv sync --locked
# Windows, once before the report command
uv run python scripts/setup_windows_pdf.py
uv run adsreport run --input data/sample --out out/review --no-ai
```

Windows setup uses Windows tar and official MSYS2 packages pinned in config/windows_pdf_packages.json. It verifies SHA-256 and extracts only DLLs/font configuration into ignored .tools/windows-pdf. No administrator installation is required. The app finds that folder from the repository root. For another working directory, set WEASYPRINT_DLL_DIRECTORIES to the absolute .tools/windows-pdf/mingw64/bin directory. Pango 1.58.2 was exercised here. Native binaries are not distributed in Git. Reviewed pins may need updating if upstream removes old packages.

Ubuntu requires libpango-1.0-0, libpangoft2-1.0-0, libharfbuzz-subset0 and fonts-dejavu-core. The workflow includes that step. Hosted execution remains unverified because of the account lock. Existing Excel and PowerPoint were used for QA only. Neither is needed for generation, and no paid service was added.

## Common data and identity

Portfolio amounts sum the computed product values. TACoS uses total spend / total net retail revenue. Changes require the immediately preceding week with matching product coverage. Monetary changes use EUR and TACoS changes use percentage points. Unavailable values remain N/A. JSON/CSV preserve exact Decimal values. Office stores numeric cells as floating-point values with tested matching display rounding.

Optional catalog.csv or SAMPLE_catalog.csv supplies product_name, asin, sku, set_number and source_url. The loader validates/fingerprints catalog bytes. Catalog URLs must be official LEGO references. Duplicate catalog identifiers/paths and unsafe links fail. Missing catalog metadata uses explicit unavailable fields. Manufacturer set numbers remain distinct from sample ASINs/SKUs. Financial calculations do not depend on catalog identity.

presentation.report_id identifies source/configuration/commentary content. artifacts.json fingerprints every other generated file. A renderer failure publishes nothing, and different existing content is preserved. Binary packaging timestamps use a canonical epoch for replay, including embedded chart workbooks. Those document properties are not execution-time evidence. Actual development timings/timestamps are in evidence JSON. P7 must freeze the exact artifact manifest and bytes for approval, with genuine run identity. The content ID alone is not an approval token.

## Four formats

| Format | Contents |
|---|---|
| XLSX | Six specified sheets. Portfolio results/changes, every flag with evidence/thresholds, all 80 product-week KPI records with numeric/date formats and frozen identifiers, three native charts on Charts plus one Summary trend chart, ten full commentary rows and provenance. This is a static snapshot, not a recalculating financial model. |
| HTML | Autoescaped English report, responsive overview, priority products, three inline SVG charts, ten product cards, rule evidence/thresholds, commentary labels/reasons and provenance. External links are references and load no assets. |
| PDF | The same HTML with A4 print styles. The sample is eight pages. Each page has SAMPLE DATA, identity and pagination. WeasyPrint 70 URLFetcher permits no external protocols and stops on requested network/file resources. |
| PPTX | Five editable slides with title/status, portfolio results, priorities, native charts and review items. Two products are highlighted on the final slide. Full commentary for all ten products and catalog references remain in speaker notes. |

The palette is navy/teal with severity text. Render-only Stamp displays DRAFT or supplied reviewer/timestamp. Both states are tested. Injected approval tests do not approve a published sample. The actual approval action remains P7.

## Verification and service behavior

Cross-format tests compare displayed figures, full XLSX values, native chart series, identities, labels and commentary. Missing values, no flags, noncomparable weeks, resource blocking, missing PDF libraries, autoescaping, formula strings, publication failure and deterministic repeat runs are covered.

Native Excel opened six sheets and three Charts-sheet charts without repair. PowerPoint opened/rendered all five slides. All PDF pages were rendered with Poppler and inspected. Browser checks found ten product cards, three charts, no external resource requests and no page overflow at 390 pixels. Previews are in evidence/p6. Workbook previews show bounded opening ranges, while automated checks cover all exported values.

P6 live AI attempts fell back safely, and an ordered-batch diagnostic returned HTTP 503. A separate diagnostic produced a real structured response, captured in SAMPLE-p6-live-response.json. Its guard-checked replay is labelled in p6-ai-replay.json and is not a fresh live or scheduled run. P5's successful live integration remains recorded. Optional AI service availability is not guaranteed. provider_error_status now records numeric HTTP failures without provider text. No scheduled reliability or business time-saving claim is made.

Sources checked 2026-11-16 are [WeasyPrint installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html), [URLFetcher API](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html#weasyprint.urls.URLFetcher), [MSYS2 Pango](https://packages.msys2.org/packages/mingw-w64-x86_64-pango), [XlsxWriter charts](https://xlsxwriter.readthedocs.io/working_with_charts.html) and [python-pptx](https://python-pptx.readthedocs.io/en/latest/). Package pins and sources are in decisions.md.
