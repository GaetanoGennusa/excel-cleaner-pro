"""Transparent heuristic profiling; suggestions never delete records."""
import re
import pandas as pd

ISSUE_COLUMNS = ["row", "column", "issue", "value"]


def missing(value: object) -> bool:
    return value is None or bool(pd.isna(value))


def profile_data(frame: pd.DataFrame) -> dict:
    normalized = frame.map(lambda v: " ".join(v.split()).casefold() if isinstance(v, str) else v)
    exact = frame.duplicated(keep="first")
    possible = normalized.duplicated(keep=False) & ~frame.duplicated(keep=False)
    issues = []
    column_info = []
    for column in frame:
        series = frame[column]
        column_info.append({"column": column, "dtype": str(series.dtype), "nulls": int(series.isna().sum()),
                            "types": ", ".join(sorted({type(v).__name__ for v in series if not missing(v)}))})
        for position, value in enumerate(series, 2):
            issue = None
            if missing(value):
                issue = "Valore mancante (non compilato automaticamente)"
            elif isinstance(value, str):
                if value and not value.strip():
                    issue = "Testo composto da soli spazi"
                elif value.lstrip().startswith(("=", "+", "-", "@")):
                    issue = "Testo simile a formula; esportazione protetta"
                elif re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", value.strip()):
                    parts = value.strip().split("/")
                    if 1 <= int(parts[0]) <= 12 and 1 <= int(parts[1]) <= 12:
                        issue = "Data ambigua: scegliere un formato esplicito"
            if issue:
                issues.append({"row": position, "column": column, "issue": issue, "value": value})
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) >= 4:
            q1, q3 = numeric.quantile([.25, .75])
            iqr = q3 - q1
            if iqr > 0:
                for position, value in enumerate(series, 2):
                    if isinstance(value, (int, float)) and not missing(value) and (value < q1 - 1.5 * iqr or value > q3 + 1.5 * iqr):
                        issues.append({"row": position, "column": column, "issue": "Possibile anomalia numerica (IQR, solo segnalazione)", "value": value})
    for position in range(len(frame)):
        if exact.iloc[position] or possible.iloc[position]:
            issues.append({"row": position + 2, "column": "*", "issue": "Duplicato esatto" if exact.iloc[position] else "Possibile duplicato (spazi/case)", "value": ""})
    return {"rows": len(frame), "columns": len(frame.columns), "nulls": int(frame.isna().sum().sum()),
            "duplicates": int(exact.sum()), "possible_duplicates": int(possible.sum()),
            "column_info": pd.DataFrame(column_info), "issues": pd.DataFrame(issues, columns=ISSUE_COLUMNS)}
