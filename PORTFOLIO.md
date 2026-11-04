# Excel Cleaner Pro

A local Python application for cleaning small Excel and CSV datasets with explicit rules, before/after review and an auditable handover.

## The problem

Spreadsheet exports often contain extra spaces, inconsistent names, mixed number formats, exact duplicate rows and dates that need interpretation. Editing them manually can make it difficult to explain what changed or to preserve identifiers such as `001`.

Excel Cleaner Pro makes the cleaning choices visible. Users choose the columns and formats to transform, inspect the result and download a report of unresolved values and recorded changes. Source files remain unchanged. Missing values are not invented and uncertain matches are not deleted.

## A reproducible synthetic example

The demonstration uses invented records only; it is not a client case study.

- [Original CSV](demo/10_before.csv): four rows, padded names, Italian amounts, ambiguous dates, an exact duplicate and invalid values.
- [Cleaned CSV](demo/10_after.csv): three rows after the explicitly confirmed duplicate removal.
- [Downloadable Excel report](demo/10_report.xlsx): `Cleaned_Data`, `Issues`, `Change_Log` and `Metadata`.
- [Walk-through for non-programmers](demo/QUICKSTART.md).

With the agreed Italian format, `1.234,56` becomes the numeric value `1234.56`; the explicitly selected day/month/year format turns `01/02/2025` into `2025-02-01`. The identifier `001` is preserved. The text `unknown` and the impossible date `31/02/2025` remain visible for a decision. These are demonstration outcomes, not claims about time savings or financial results.

## What the application does

- Reads CSV and one selected XLSX sheet, with explicit CSV encoding and separator settings.
- Profiles missing values, column types, exact duplicates and possible duplicates based on spaces and text case.
- Applies optional whitespace cleanup, consistent headings and text case, explicit Italian/international number conversion and date normalization.
- Requires confirmation before removing exact source duplicates; keeps the first copy.
- Shows before/after previews, issues and operation logs; supports one-step undo and reset.
- Produces protected XLSX/CSV exports, with a UTC timestamp, settings and integrity metadata in the XLSX report. Processing is local, without paid AI APIs or mandatory cloud accounts.

## Implementation and verification

Python 3.12+, pandas, openpyxl and Streamlit; pytest and Streamlit AppTest for automated checks. The interface and the ingestion, profiling, transformation, validation and export modules are separated. Synthetic fixtures cover preservation and error cases. Consult the [final QA report](docs/FINAL_QA_REPORT.md) for the latest results and remaining checks; the [initial verification](docs/VERIFICATION.md) is preserved as a historical record.

Automated checks do not replace manual use in a real browser, a visual inspection of the workbook in Excel or LibreOffice, or acceptance checks for a specific client dataset. The project is presented as a portfolio application, not as a certified or universally reliable commercial product.

### Genuine interface evidence

These are screenshots of the running application with synthetic data, captured in a real headless Chromium browser, not mockups:

- [Upload screen](demo/screenshots-dark/01_upload.png).
- [Data overview](demo/screenshots-dark/02_overview.png).
- [Before/after preview and checks](demo/screenshots-dark/03_preview.png).
- [Export controls](demo/screenshots-dark/04_export.png).
- [Phone-width rules](demo/screenshots-dark/05_mobile_rules.png) and [tablet-width preview](demo/screenshots-dark/09_tablet_preview.png).
- [Screenshot provenance and scope](demo/screenshots-dark/README.md).

The current interface is dark with an emerald accent, a sticky progress bar and sidebar navigation, and adapts to tablet and phone widths. It uses only local fonts and assets. The [final QA report](docs/FINAL_QA_REPORT.md) records 49 passing tests and 31 real-browser steps. Those steps cover date-format selection through the interface, animated and reduced-motion modes, changing the source within one session, and the full flow at tablet and phone widths. No external requests were made during the verified run.

The browser scenario applies whitespace cleanup, title case, Italian amounts, the day/month/year date format and confirmed exact deduplication. [The workbook actually downloaded in the browser](demo/qa_report.xlsx) and [its CSV](demo/qa_cleaned.csv) contain three rows: `001` kept as text, `1234.56`, `2025-02-01`, and `unknown` and `31/02/2025` kept and reported. The workbook was also opened read-only in Microsoft Excel, which reads the same values and no formula cells. A visual inspection of the workbook in Excel has not yet been done. Earlier interface versions and their evidence remain available as history: [light redesign](demo/screenshots-redesign/README.md) and the [first screenshots](demo/screenshots/README.md).

## A narrowly scoped service

**Excel & CSV Data Cleaning**: one CSV or XLSX file, one selected worksheet, up to 1,000 data rows and 20 columns, agreed supported transformations, an Excel report and one limited revision against the original requirements. Proposed delivery: two working days after the input and requirements have been reviewed, subject to availability and complexity. An experimental price of **EUR 25–40** is a hypothesis to validate, not a researched market rate or guaranteed income.

See the [Fiverr draft](docs/FIVERR_OFFER_EN.md) and [customizable Upwork proposal](docs/UPWORK_PROPOSAL_EN.md). These are unpublished drafts.

## Boundaries

No VBA/macros, advanced financial analysis, damaged-file repair, recovery of lost zeros/formulas/charts, preservation of workbook layout, OCR, fuzzy merging, enrichment or external system integration. Ambiguous dates require a chosen format. Financial amounts use ordinary numeric conversion, not an accounting-grade decimal calculation engine. Files containing confidential data require an agreed handling and deletion process outside this demonstration.

The application's technical limits are broader than the proposed service scope: 10 MB, 50,000 rows, 200 columns and 500,000 cells per selected dataset, with an 80 MB expanded XLSX limit. A valid file within those limits still needs review. Exact deliverables and acceptance criteria must be agreed before accepting work.
