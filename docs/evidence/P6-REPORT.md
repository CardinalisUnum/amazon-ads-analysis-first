# P6 gate report

P6 is complete and locally verified. The owner authorized the phase on 2026-11-16. P7 requires another approval. Hosted CI P1-5 remains open.

| Task | Acceptance evidence |
|---|---|
| P6-1 charts | Three deterministic SVG/PNG charts use shared data/palette, units and axis labels. Inline SVG IDs are namespaced. Native Office series are compared against the same data. |
| P6-2 XLSX | Native Excel opened all six sheets and the three Charts-sheet charts without repair. Summary has another native trend chart. Full numeric/date values, frozen identifiers, filters, conditional formatting and commentary are tested. |
| P6-3 HTML | Autoescaped self-contained report checked in Chrome at desktop and 390 pixels. Ten product cards, three charts, no external resources and no horizontal page overflow. |
| P6-4 PDF | Local Pango 1.58.2 setup works. All eight A4 pages were rendered with Poppler and inspected. WeasyPrint 70 URLFetcher blocks external protocols and fails rather than publishing missing resources. |
| P6-5 PPTX | Native PowerPoint opened and rendered five editable slides, including native charts. All ten products' full commentary and catalog references are retained in speaker notes. |
| P6-6 consistency/stamps | Tests compare displayed portfolio figures, every XLSX product value, native chart series, identities, source labels and DRAFT/SAMPLE stamps. Injected APPROVED stamps require reviewer and timezone-aware timestamp. Those tests approve no real report. |

The committed docs/examples bundle has thirteen files with a verified artifact manifest. Its CSV is byte-identical to the P3 golden file. It is an offline DRAFT sample with templates. Twenty-one preview images are in evidence/p6, including every PDF page, every slide, six workbook views and two browser views. Workbook views show bounded opening ranges; tests check the full table values.

## Checks

Final locked install, Ruff, strict mypy, tests, sample generation, configuration, normal offline CLI and wheel build all pass. There are 195 passing tests and 98% total coverage. KPI calculations, portfolio arithmetic, rules and the number guard have 100% coverage including branches. The two existing Hypothesis identities each pass 200 examples. See p6-local.txt.

A separate staged Windows checkout with CRLF conversion verifies all tests and byte-identical output files using the explicitly configured native library directory. The wheel has 36 package/metadata files, including both templates and the AI prompt, without local caches or credentials. See p6-checkout.txt.

The final offline pipeline call took 4.454 seconds after Python imports. It excludes process startup and is not human time saved. p6-offline.json captures that scope and the artifact hashes. The subsequent full gate independently reproduced the same thirteen-file bundle.

## Live service and replay evidence

Two normal P6 AI attempts produced usable templates after service errors. A later ordered-batch diagnostic confirmed HTTP 503. A separate real diagnostic returned structured output, captured in SAMPLE-p6-live-response.json. Its explicit replay passed the guard for all ten notes, with zero rejected products and no new network request. See p6-live.json and p6-ai-replay.json. P5's successful normal-CLI batch remains historical evidence.

This phase does not claim a fresh successful normal-CLI AI run, scheduled reliability or actual business impact. The numeric provider_error_status field now preserves HTTP failures without raw provider text. Model/service availability is not guaranteed, and Free Tier billing-unlinked status remains owner-attested.

## Self-review and resolved issues

- Native PDF libraries were missing. A checksum-pinned, project-local MSYS2 installer resolved the Windows dependency without system installation or paid services.
- WeasyPrint 70 requires the documented URLFetcher API. The renderer now uses it with no allowed external protocols and fatal resource errors.
- Embedded chart-workbook timestamps made repeated PPTX files differ. OOXML packaging metadata is normalized recursively. Actual execution timestamps remain separate evidence.
- Repeated SVG IDs caused collisions in inline HTML. IDs/references are now chart-specific.
- Git text conversion could change committed example bytes on Windows. The reviewed bundle disables conversion, and every manifest hash is verified after checkout.
- PowerPoint chart labels/legend overlapped. Labels were moved below the plot and the legend repositioned. Trend axes begin at zero consistently across formats.
- Long raw evidence crowded Excel rows. Human-readable evidence and thresholds now use canonical units/rounding, while JSON preserves exact values.
- HTML text is autoescaped. XLSX strings cannot become formulas, and formula-like PPTX chart identifiers fail clearly. Missing values, no flags and renderer failure are exercised.

The builder reviewed changed normal/failure paths, publication staging, package contents and the diff. This self-review does not replace P9's independent audit. No financial calculation moved into AI, a template or a spreadsheet formula. There is one shared report object and no new web service/framework.

## Gate

All six P6 tasks are complete. Overall completion is 38/56 tasks and 78.7% weighted. STATUS.md contains the full progress table. RESUME.md documents exact interfaces and P7 steps.

The P6 [hosted run](https://github.com/CardinalisUnum/amazon-ads-analysis-first/actions/runs/43888880338) executed zero runner steps and returned the same account billing-lock annotation. See p6-hosted-ci.json. The Ubuntu native-library step is committed but unverified on a hosted runner. Operations, frozen approval, notification receipts and real scheduled history remain P7. Measured human review savings remain P8. Pause after pushing for P7 approval.
