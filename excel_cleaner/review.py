"""Plain-language review aids: issue status and an Italian report summary."""
from collections.abc import Mapping

import pandas as pd

RESOLVED, PROTECTED, TO_CHECK = "Risolto", "Protetto", "Da verificare"
STATUS_COLUMNS = ["status", "note"]
CASE_NAMES = {"lower": "minuscolo", "upper": "MAIUSCOLO", "title": "Iniziali Maiuscole"}
NUMBER_NAMES = {"it": "numeri italiani (1.234,56)", "international": "numeri internazionali (1,234.56)"}


def _status(issue: str, cell_changes: set[str], removed: bool, date_format: str | None) -> tuple[str, str]:
    if issue.startswith("Data ambigua"):
        if "date" in cell_changes:
            return RESOLVED, f"Convertita con il formato scelto {date_format}"
        return TO_CHECK, "Scegliere il formato della data per questa colonna"
    if issue == "Duplicato esatto":
        if removed:
            return RESOLVED, "Copia rimossa con conferma; resta la prima riga"
        return TO_CHECK, "Copia conservata: rimuoverla solo con conferma"
    if issue.startswith("Testo simile a formula"):
        return PROTECTED, "Esportato come testo, non eseguibile"
    if issue.startswith("Testo composto da soli spazi") and "trim" in cell_changes:
        return RESOLVED, "Spazi rimossi: la cella ora è vuota"
    if issue.startswith("Valore mancante"):
        return TO_CHECK, "Cella vuota conservata, nessun valore inventato"
    if issue.startswith("Possibile duplicato"):
        return TO_CHECK, "Righe simili conservate: decidere se sono la stessa"
    return TO_CHECK, "Valore originale conservato: decidere come correggerlo"


def annotate_issues(issues: pd.DataFrame, changes: pd.DataFrame, date_columns: Mapping[str, str]) -> pd.DataFrame:
    """Return a copy of the issues with a status and a short explanation per row."""
    by_cell: dict[tuple[int, str], set[str]] = {}
    for row, column, operation in zip(changes["row"], changes["column"], changes["operation"]):
        by_cell.setdefault((row, column), set()).add(operation)
    removed = {row for row, operation in zip(changes["row"], changes["operation"]) if operation == "drop_exact_duplicate"}
    statuses = [_status(str(issue), by_cell.get((row, column), set()), row in removed, date_columns.get(column))
                for row, column, issue in zip(issues["row"], issues["column"], issues["issue"])]
    annotated = issues.copy()
    for position, name in enumerate(STATUS_COLUMNS):
        annotated[name] = pd.Series([pair[position] for pair in statuses], index=issues.index, dtype=object)
    return annotated


def status_counts(issues: pd.DataFrame) -> dict[str, int]:
    values = issues["status"].tolist() if "status" in issues else []
    return {name: values.count(name) for name in (TO_CHECK, RESOLVED, PROTECTED)}


def rules_text(config: Mapping) -> str:
    parts = []
    if config.get("trim"):
        parts.append("spazi superflui rimossi")
    if config.get("headers"):
        parts.append("intestazioni standardizzate")
    for column, mode in config.get("case_columns", {}).items():
        parts.append(f"{CASE_NAMES.get(mode, mode)} su «{column}»")
    for column, locale in config.get("number_columns", {}).items():
        parts.append(f"{NUMBER_NAMES.get(locale, locale)} su «{column}»")
    for column, fmt in config.get("date_columns", {}).items():
        parts.append(f"date {fmt} su «{column}»")
    if config.get("drop_duplicates") and config.get("confirm_duplicates"):
        parts.append("duplicati esatti rimossi con conferma")
    return "; ".join(parts) if parts else "nessuna regola: dati originali esportati senza modifiche"


def summary_it(rows_out: int, removed: int, modified: int, changes: int, issues: pd.DataFrame,
               integrity: Mapping[str, bool], config: Mapping) -> str:
    counts = status_counts(issues)
    checks = "tutti superati" if all(integrity.values()) else "NON superati"
    return "\n".join([
        f"Righe originali: {rows_out + removed} · righe finali: {rows_out} · duplicati rimossi: {removed}",
        f"Righe con celle modificate: {modified} · modifiche registrate in Change_Log: {changes}",
        f"Segnalazioni in Issues: {counts[TO_CHECK]} da verificare, {counts[RESOLVED]} risolte, {counts[PROTECTED]} protette",
        f"Regole applicate: {rules_text(config)}",
        f"Controlli di integrità: {checks}",
        "Come leggere il report: Cleaned_Data contiene i dati puliti; Issues elenca le segnalazioni con il loro stato; "
        "Change_Log registra ogni cella modificata (riga, regola, prima, dopo); le righe seguenti di questo foglio "
        "riportano le impostazioni tecniche. Numeri di riga riferiti al file originale, intestazione = riga 1.",
    ])
