"""Bounded inputs and literal exports for untrusted synthetic content."""
from io import BytesIO, StringIO
import csv
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook
import pandas as pd
import pytest

from excel_cleaner import io
from excel_cleaner.export import export_csv, export_xlsx
from excel_cleaner.transforms import clean, CleaningConfig


def test_xlsx_entity_declaration_is_rejected():
    source = BytesIO()
    workbook = Workbook()
    workbook.active.append(["code"])
    workbook.active.append(["001"])
    workbook.save(source)
    workbook.close()
    target = BytesIO()
    with ZipFile(BytesIO(source.getvalue())) as original, ZipFile(target, "w") as changed:
        for member in original.infolist():
            content = original.read(member.filename)
            if member.filename == "xl/worksheets/sheet1.xml":
                content = b'<!DOCTYPE worksheet [<!ENTITY payload "synthetic">]>' + content.replace(b">code<", b">&payload;<")
            changed.writestr(member.filename, content)
    with pytest.raises(io.InputError):
        io.read_excel(target.getvalue(), "Sheet")


def test_row_limit_rejects_instead_of_truncating(monkeypatch):
    monkeypatch.setattr(io, "MAX_ROWS", 1)
    with pytest.raises(io.InputError):
        io.read_csv(b"code\n001\n002\n")


def test_header_and_control_prefixes_are_safe_in_both_exports():
    frame = pd.DataFrame({"=header": ["\t=1+1", "\r@x", "\n+cmd", "  -formula"]})
    workbook = load_workbook(BytesIO(export_xlsx(clean(frame, CleaningConfig()))))
    assert workbook["Cleaned_Data"]["A1"].value == "=header"
    assert all(cell.data_type != "f" for sheet in workbook for row in sheet for cell in row)
    rows = list(csv.reader(StringIO(export_csv(frame).decode("utf-8-sig")), delimiter=";"))
    assert all(row[0].startswith("'") for row in rows)


def test_excel_length_limit_does_not_silently_truncate():
    frame = pd.DataFrame({"text": ["A" * 32768]})
    with pytest.raises(ValueError, match="32.767"):
        export_xlsx(clean(frame, CleaningConfig()))
    assert "A" * 32768 in export_csv(frame).decode("utf-8-sig")
