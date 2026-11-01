---
name: excel-quality-assurance
description: Verify Excel Cleaner Pro data preservation, parsing edge cases, change accounting, session UI and safe CSV/XLSX exports using synthetic pytest fixtures.
---

Read `AGENTS.md`, relevant modules and existing tests. Use synthetic data only. Exercise exact/possible duplicates, nulls versus literal NA tokens, ambiguous dates, Italian and international numbers, leading zeros, long identifiers, multiple encodings, malformed/empty input and repeated cleaning.

Check input immutability, default value preservation, row accounting, per-cell logs, affected row counts and explicit duplicate confirmation. Ensure failed conversions retain values and produce issues. Reopen XLSX exports with openpyxl, inspect all sheets for formula cells, verify values, sheet names and metadata. Decode CSV and verify formula neutralization including whitespace and control characters. Test local Streamlit session transitions and defaults with AppTest where feasible.

Execute pytest and fix demonstrated defects. Record actual outcomes; separate browser/Excel manual review from automated verification. Generated synthetic demos should be reproducible and include before/after plus audit reports. Never declare commercial readiness without manual checks.
