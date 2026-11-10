"""Formula-safe exports; openpyxl uses temporary local XML while writing XLSX."""
import csv
from datetime import date, datetime
from io import BytesIO, StringIO
import json
import math
import re

import pandas as pd
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .profile import missing
from .review import summary_it
from .transforms import CleaningResult


def safe_csv_text(value: object) -> object:
    if isinstance(value, str) and (value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n"))):
        return "'" + value
    return value


def export_csv(frame: pd.DataFrame, separator: str = ";") -> bytes:
    if separator not in {";", ",", "\t", "|"}:
        raise ValueError("Separatore CSV non supportato.")
    buffer = StringIO(newline="")
    writer = csv.writer(buffer, delimiter=separator, quoting=csv.QUOTE_ALL)
    writer.writerow([safe_csv_text(str(c)) for c in frame.columns])
    for row in frame.itertuples(index=False, name=None):
        writer.writerow(["" if missing(v) else safe_csv_text(v) for v in row])
    return buffer.getvalue().encode("utf-8-sig")


def _excel_value(value: object) -> object:
    if missing(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, datetime) and value.tzinfo:
        return value.isoformat()
    if isinstance(value, int) and not isinstance(value, bool) and len(str(abs(value))) > 15:
        return str(value)
    if isinstance(value, str):
        if len(value) > 32767:
            raise ValueError("Una cella supera 32.767 caratteri: Excel non può conservarla. Usare CSV.")
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", value):
            raise ValueError("Caratteri di controllo non compatibili con Excel. Usare CSV.")
    return value


def export_xlsx(result: CleaningResult) -> bytes:
    if not all(result.integrity.values()):
        raise ValueError("Esportazione bloccata: integrità non verificata.")
    summary = summary_it(len(result.data), result.removed_rows, result.modified_rows, len(result.changes),
                         result.issues, result.integrity, result.config)
    metadata = [
        ["riepilogo", summary],
        ["timestamp_utc", result.timestamp],
        ["configuration_json", json.dumps(result.config, ensure_ascii=False, sort_keys=True)],
        ["ingestion_json", json.dumps(result.data.attrs.get("ingestion", {}), ensure_ascii=False, sort_keys=True)],
        ["integrity_checks_json", json.dumps(result.integrity, sort_keys=True)],
        ["modified_rows", result.modified_rows],
        ["removed_rows", result.removed_rows],
        ["row_reference", "Source row position, header=1. Issues describe original input; status and note say whether each one was resolved by the selected rules or still needs review. Duplicates removed only if identical in source."],
        ["export_protection", "All XLSX strings are literal text; native integers over 15 digits exported as text for precision. CSV prefixes risky text with apostrophe. Formatting/macros/formulas not preserved."],
    ]
    tables = [("Cleaned_Data", [list(result.data.columns), *result.data.itertuples(index=False, name=None)]),
              ("Issues", [list(result.issues.columns), *result.issues.itertuples(index=False, name=None)]),
              ("Change_Log", [list(result.changes.columns), *result.changes.itertuples(index=False, name=None)]),
              ("Metadata", [["key", "value"], *metadata])]
    for _, rows in tables:
        if len(rows) > 1_048_576:
            raise ValueError("Il report supera il limite di righe Excel. Ridurre il dataset o le trasformazioni.")
        for position, row in enumerate(rows):
            rows[position] = [_excel_value(value) for value in row]
    workbook = Workbook(write_only=True)
    for name, rows in tables:
        sheet = workbook.create_sheet(name)
        sheet.freeze_panes = "A2"
        if rows and rows[0]:
            sheet.auto_filter.ref = f"A1:{get_column_letter(len(rows[0]))}{len(rows)}"
            for position in range(len(rows[0])):
                width = min(55, max(14, max(len(str(row[position] if row[position] is not None else "")) for row in rows[:100]) + 2))
                sheet.column_dimensions[get_column_letter(position + 1)].width = width
            if name == "Metadata":
                sheet.column_dimensions["B"].width = 88
        for row_position, row in enumerate(rows):
            if name == "Metadata" and row_position > 0:
                lines = sum(max(1, math.ceil(len(part) / 72)) for part in str(row[1]).split("\n"))
                sheet.row_dimensions[row_position + 1].height = min(409, max(18, lines * 16))
            cells = []
            for column_position, value in enumerate(row):
                cell = WriteOnlyCell(sheet, value)
                if isinstance(cell.value, str):
                    cell.data_type = "s"
                if row_position == 0:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="137C66")
                elif name == "Metadata":
                    cell.alignment = Alignment(vertical="top", wrap_text=column_position == 1)
                cells.append(cell)
            sheet.append(cells)
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    return buffer.getvalue()
