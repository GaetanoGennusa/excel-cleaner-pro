---
name: excel-data-processing
description: Implement conservative Excel and CSV ingestion, profiling, explicit conversions and auditable export in Excel Cleaner Pro.
---

Read `AGENTS.md` and the affected engine modules. Treat headers and CSV cells as text on ingestion; only empty fields are missing, never infer NA/N/A or numeric identifiers. Reject inconsistent CSV records and oversized expanded XLSX archives. Read formulas as literal text; never evaluate them. Excel numeric cells may already have lost leading zeros: disclose that limitation.

All cleaning options start disabled. Work on copies. Use per-column locale and strict date formats; preserve ambiguous dates until the user chooses a format. Protect leading-zero strings, integers longer than 15 digits and invalid or nonfinite values. Keep invalid source values with issues, never fill or silently discard. Only remove exact duplicates after a second explicit confirmation. Possible duplicates are suggestions only.

Track source row positions through transformations and deletion. Report cell changes, affected rows, removed rows, configuration, UTC timestamp and integrity checks. Neutralize formula-like CSV text and force XLSX text cell types including headers and logs. Keep uploads in session memory, provide undo/reset, and avoid disk caches. Test preservation, idempotence and export round trips before stating completion.
