# Excel Cleaner Pro — project standards

Local Python 3.12+ / pandas / openpyxl / Streamlit application. No remote document processing, telemetry, paid APIs, or persistence of uploads. All fixtures must be synthetic.

## Layout and commands
- `excel_cleaner/`: typed ingestion, profile, transformations, validation and export; no Streamlit imports.
- `app.py`: session-based interface. `tests/`: pytest and Streamlit AppTest. `demo/`: synthetic portfolio examples.
- Windows: `py -3.12 -m venv .venv`, `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
- Start: `.\.venv\Scripts\python.exe -m streamlit run app.py`.
- Verify: `.\.venv\Scripts\python.exe -m pytest -q`; demo: `.\.venv\Scripts\python.exe -m scripts.generate_demo`.

## Invariants
Never mutate input frames. Default rules must preserve values and row count. No automatic ambiguous date parsing, NA-token interpretation, or identifier conversion. Invalid values remain visible as issues. Removing exact duplicate rows requires explicit confirmation. Log cell changes with source row positions (header is row 1), rule, before and after. Export metadata must identify settings, UTC time and actual checks. Formula-like strings must never become executable formulas. Reject malformed/oversize inputs rather than skipping records. Do not silently truncate output.

Keep dependencies minimal, modules small, functions typed, tests on observable invariants. Do not claim commercial readiness from automated checks alone. No destructive commands, global installs, or publishing.

## Local skills
`.agents/skills/excel-data-processing/SKILL.md` and `.agents/skills/excel-quality-assurance/SKILL.md` contain domain guidance. New skills are not assumed loaded in an existing conversation: explicitly read their SKILL.md before applying them; future sessions may discover them. Invoke by name when available, otherwise read the file directly. Do not download third-party skills.
