"""Bounded, strict ingestion without implicit numeric/date conversion."""
import csv
import hashlib
from io import BytesIO, StringIO
from zipfile import ZipFile, BadZipFile

import pandas as pd
from openpyxl import load_workbook

from .config import MAX_FILE_BYTES, MAX_EXPANDED_BYTES, MAX_ROWS, MAX_COLUMNS, MAX_CELLS


class InputError(ValueError):
    """A comprehensible input problem safe to show in the interface."""


def _size(data: bytes) -> None:
    if not data:
        raise InputError("Il file è vuoto.")
    if len(data) > MAX_FILE_BYTES:
        raise InputError("File troppo grande: massimo 10 MB.")


def _shape(rows: int, columns: int) -> None:
    if columns > MAX_COLUMNS or rows > MAX_ROWS or rows * columns > MAX_CELLS:
        raise InputError("Limite superato: 50.000 righe, 200 colonne o 500.000 celle.")


def unique_headers(values: list) -> list[str]:
    """Retain all columns, assigning stable distinct names to repeated/empty headers."""
    result: list[str] = []
    used: set[str] = set()
    reserved = {str(v) for v in values if v is not None and str(v)}
    for position, value in enumerate(values, 1):
        base = str(value) if value is not None and str(value) else f"column_{position}"
        name, suffix = base, 2
        while name in used or (name != base and name in reserved):
            name = f"{base}_{suffix}"
            suffix += 1
        used.add(name)
        result.append(name)
    return result


def read_csv(data: bytes, encoding: str = "utf-8-sig", separator: str = ",") -> pd.DataFrame:
    _size(data)
    if encoding not in {"utf-8-sig", "utf-8", "cp1252", "latin-1", "utf-16"}:
        raise InputError("Codifica non supportata.")
    if separator not in {",", ";", "\t", "|"}:
        raise InputError("Separatore non supportato.")
    try:
        csv.field_size_limit(MAX_FILE_BYTES)
        reader = csv.reader(StringIO(data.decode(encoding), newline=""), delimiter=separator, strict=True)
        headers = next(reader)
        if not headers:
            raise InputError("Intestazione CSV assente.")
        if any("\x00" in value for value in headers):
            raise InputError("Il CSV contiene caratteri NUL nell'intestazione: verificare la codifica.")
        _shape(0, len(headers))
        records = []
        for record in reader:
            if len(record) != len(headers):
                raise InputError(f"Record CSV {reader.line_num}: numero di campi incoerente. Verificare separatore e virgolette.")
            if any("\x00" in cell for cell in record):
                raise InputError("Il CSV contiene caratteri NUL non validi.")
            _shape(len(records) + 1, len(headers))
            records.append([None if value == "" else value for value in record])
        names = unique_headers(headers)
        frame = pd.DataFrame(records, columns=names, dtype=object)
        frame.attrs["ingestion"] = {"format": "csv", "sha256": hashlib.sha256(data).hexdigest(), "encoding": encoding, "separator": separator,
                                    "headers": [{"source": v, "assigned": n} for v, n in zip(headers, names)]}
        return frame
    except InputError:
        raise
    except (UnicodeError, csv.Error, StopIteration) as exc:
        raise InputError("CSV non leggibile: controllare codifica, separatore e virgolette.") from exc


def _workbook(data: bytes):
    _size(data)
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 5000 or sum(e.file_size for e in entries) > MAX_EXPANDED_BYTES:
                raise InputError("Archivio Excel espanso troppo grande (massimo 80 MB / 5.000 elementi).")
        return load_workbook(BytesIO(data), read_only=True, data_only=False, keep_links=False)
    except InputError:
        raise
    except Exception as exc:
        raise InputError("File Excel non valido, danneggiato o protetto. È richiesto un .xlsx non cifrato.") from exc


def excel_sheets(data: bytes) -> list[str]:
    workbook = _workbook(data)
    try:
        return workbook.sheetnames
    finally:
        workbook.close()


def read_excel(data: bytes, sheet: str) -> pd.DataFrame:
    workbook = _workbook(data)
    try:
        if sheet not in workbook.sheetnames:
            raise InputError("Il foglio selezionato non esiste.")
        worksheet = workbook[sheet]
        _shape(max((worksheet.max_row or 1) - 1, 0), worksheet.max_column or 0)
        # Producers may write an underestimated <dimension>; never let it hide
        # rows or columns. Iterate the actual XML, enforcing our bounds below.
        worksheet.reset_dimensions()
        iterator = worksheet.iter_rows(values_only=True)
        headers = list(next(iterator, ()))
        if not headers or all(v is None for v in headers):
            raise InputError("Il foglio Excel è vuoto o non ha un'intestazione nella prima riga.")
        _shape(0, len(headers))
        records = []
        for row in iterator:
            if len(row) > len(headers):
                headers.extend([None] * (len(row) - len(headers)))
            _shape(len(records) + 1, len(headers))
            records.append(row)
        names = unique_headers(list(headers))
        padded = [list(row) + [None] * (len(headers) - len(row)) for row in records]
        frame = pd.DataFrame(padded, columns=names, dtype=object)
        frame.attrs["ingestion"] = {"format": "xlsx", "sha256": hashlib.sha256(data).hexdigest(), "sheet": sheet,
                                    "headers": [{"source": str(v) if v is not None else None, "assigned": n} for v, n in zip(headers, names)]}
        return frame
    except InputError:
        raise
    except Exception as exc:
        raise InputError("Contenuto del foglio non leggibile. Nessun record è stato importato.") from exc
    finally:
        workbook.close()
