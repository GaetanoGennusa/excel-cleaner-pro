"""Explicit transformations with cell-level audit and conservative failure handling."""
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
import math
import re

import pandas as pd

from .io import unique_headers
from .profile import ISSUE_COLUMNS, missing, profile_data
from .review import annotate_issues
from .validation import integrity_checks

CHANGE_COLUMNS = ["row", "column", "operation", "before", "after"]


@dataclass
class CleaningConfig:
    trim: bool = False
    headers: bool = False
    case_columns: dict[str, str] = field(default_factory=dict)
    number_columns: dict[str, str] = field(default_factory=dict)
    date_columns: dict[str, str] = field(default_factory=dict)
    drop_duplicates: bool = False
    confirm_duplicates: bool = False


@dataclass
class CleaningResult:
    data: pd.DataFrame
    issues: pd.DataFrame
    changes: pd.DataFrame
    integrity: dict[str, bool]
    modified_rows: int
    removed_rows: int
    config: dict
    timestamp: str


def _number(value: object, locale: str) -> object:
    if not isinstance(value, str):
        return value
    text = value.strip()
    text = re.sub(r"^(?:€|EUR|\$|USD)\s*|\s*(?:€|EUR|\$|USD)$", "", text).strip()
    decimal, thousands = (",", ".") if locale == "it" else (".", ",")
    signless = text.lstrip("+-")
    if re.match(r"0\d", signless):
        raise ValueError("Codice con zero iniziale conservato")
    d, t = re.escape(decimal), re.escape(thousands)
    if not re.fullmatch(rf"[+-]?(?:\d+|[1-9]\d{{0,2}}(?:{t}\d{{3}})+)(?:{d}\d+)?", text):
        raise ValueError("Numero non valido per il formato selezionato")
    canonical = text.replace(thousands, "").replace(decimal, ".")
    if len(canonical.lstrip("+-").replace(".", "").lstrip("0")) > 15:
        raise ValueError("Oltre 15 cifre significative: conservato per evitare perdita di precisione Excel")
    number = Decimal(canonical)
    converted = int(number) if number == number.to_integral_value() else float(number)
    if not math.isfinite(converted):
        raise ValueError("Valore non finito conservato")
    if number != 0 and converted == 0:
        raise ValueError("Numero troppo piccolo per una conversione senza azzeramento: valore conservato")
    return converted


def _date(value: object, fmt: str) -> object:
    if isinstance(value, datetime):
        if value.time() != datetime.min.time() or value.tzinfo is not None:
            raise ValueError("Data con orario o fuso: conservata per non perdere informazioni")
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        raise ValueError("Data non testuale conservata")
    text = value.strip()
    # ISO output is accepted to keep transformations idempotent.
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return date.fromisoformat(text).isoformat()
    try:
        parsed = datetime.strptime(text, fmt)
    except ValueError as exc:
        if "out of range" in str(exc):
            raise ValueError("Data inesistente: giorno o mese fuori intervallo") from exc
        raise ValueError("La data non corrisponde al formato scelto") from exc
    if parsed.strftime(fmt) != text:
        raise ValueError("La data non corrisponde esattamente al formato scelto")
    return parsed.date().isoformat()


def clean(frame: pd.DataFrame, config: CleaningConfig) -> CleaningResult:
    if not frame.columns.is_unique:
        raise ValueError("Le intestazioni devono essere univoche prima della pulizia.")
    if config.drop_duplicates and not config.confirm_duplicates:
        raise ValueError("Confermare esplicitamente la rimozione dei duplicati esatti.")
    selected = set(config.case_columns) | set(config.number_columns) | set(config.date_columns)
    if not selected.issubset(frame.columns):
        raise ValueError("Una colonna selezionata non esiste nel dataset.")
    conflicts = sorted(set(config.number_columns) & set(config.date_columns), key=str)
    if conflicts:
        names = ", ".join(f"«{c}»" for c in conflicts)
        raise ValueError(f"Colonna {names}: scegli un formato numero oppure un formato data, non entrambi.")
    if any(v not in {"it", "international"} for v in config.number_columns.values()):
        raise ValueError("Formato numerico sconosciuto.")
    if any(v not in {"lower", "upper", "title"} for v in config.case_columns.values()):
        raise ValueError("Normalizzazione testo sconosciuta.")
    if any(v not in {"%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"} for v in config.date_columns.values()):
        raise ValueError("Formato data non supportato.")
    output = frame.copy(deep=True)
    changes, conversion_issues = [], []
    affected: set[int] = set()
    for column_position, column in enumerate(frame.columns):
        values = []
        for position, original in enumerate(frame[column]):
            current = original
            operations = []
            if not missing(current):
                if config.trim and isinstance(current, str):
                    operations.append(("trim", lambda v: " ".join(v.split())))
                if column in config.case_columns and isinstance(current, str):
                    mode = config.case_columns[column]
                    operations.append((mode, lambda v, m=mode: getattr(v, m)() if isinstance(v, str) else v))
                if column in config.number_columns:
                    operations.append(("number", lambda v: _number(v, config.number_columns[column])))
                if column in config.date_columns:
                    operations.append(("date", lambda v: _date(v, config.date_columns[column])))
            for operation, transform in operations:
                before = current
                try:
                    after = transform(current)
                    if type(before) is not type(after) or before != after:
                        changes.append({"row": position + 2, "column": column, "operation": operation, "before": before, "after": after})
                        affected.add(position)
                    current = after
                except (ValueError, TypeError, OverflowError) as exc:
                    conversion_issues.append({"row": position + 2, "column": column, "issue": str(exc), "value": current})
            values.append(current)
        # Preserve untouched dtypes; mixed conversion columns must not coerce identifiers.
        if any(c["column"] == column for c in changes):
            output[column] = pd.Series(values, index=output.index, dtype=object)
    if config.headers:
        headers = unique_headers([re.sub(r"[^\w]+", "_", str(c).strip().casefold()).strip("_") for c in output.columns])
        for before, after in zip(output.columns, headers):
            if before != after:
                changes.append({"row": 1, "column": before, "operation": "header", "before": before, "after": after})
        output.columns = headers
    # Determine duplicates from the original values: normalization must not make
    # merely similar source records eligible for deletion.
    removed = 0
    if config.drop_duplicates:
        duplicate_mask = frame.duplicated(keep="first").to_numpy()
        for position, duplicate in enumerate(duplicate_mask):
            if duplicate:
                changes.append({"row": position + 2, "column": "*", "operation": "drop_exact_duplicate", "before": "exact source row", "after": "removed"})
        removed = int(duplicate_mask.sum())
        output = output.iloc[~duplicate_mask].copy()
    # Profile the source so issue row references always match audit/source positions.
    issues = pd.concat([profile_data(frame)["issues"], pd.DataFrame(conversion_issues, columns=ISSUE_COLUMNS)], ignore_index=True)
    change_log = pd.DataFrame(changes, columns=CHANGE_COLUMNS)
    issues = annotate_issues(issues, change_log, config.date_columns)
    integrity = integrity_checks(frame, output, removed, config.drop_duplicates and config.confirm_duplicates)
    if not all(integrity.values()):
        raise ValueError("Controlli di integrità falliti: esportazione bloccata.")
    return CleaningResult(output, issues, change_log, integrity,
                          len(affected), removed, asdict(config), datetime.now(timezone.utc).isoformat())
