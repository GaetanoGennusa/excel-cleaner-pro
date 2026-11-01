"""Data-integrity gaps identified during the second technical review."""
from io import BytesIO
from zipfile import ZipFile
import re

import pandas as pd
import pytest
from openpyxl import Workbook

from excel_cleaner.io import read_csv, read_excel, InputError
from excel_cleaner.transforms import CleaningConfig, clean


def test_tiny_decimal_is_not_silently_turned_into_zero():
    value = "0." + "0" * 400 + "1"
    result = clean(pd.DataFrame({"amount": [value]}), CleaningConfig(number_columns={"amount": "international"}))
    assert result.data.iloc[0, 0] == value
    assert len(result.issues) > 0
    assert result.modified_rows == 0


def test_underreported_excel_dimensions_do_not_hide_source_data():
    original = BytesIO()
    workbook = Workbook()
    workbook.active.append(["code", "name"])
    workbook.active.append(["001", "Synthetic"])
    workbook.save(original)
    workbook.close()
    changed = BytesIO()
    with ZipFile(BytesIO(original.getvalue())) as source, ZipFile(changed, "w") as target:
        for member in source.infolist():
            content = source.read(member.filename)
            if member.filename == "xl/worksheets/sheet1.xml":
                content = re.sub(rb'<dimension ref="[^"]+"', b'<dimension ref="A1:A1"', content)
            target.writestr(member.filename, content)
    frame = read_excel(changed.getvalue(), "Sheet")
    assert frame.shape == (1, 2)
    assert frame.iloc[0].tolist() == ["001", "Synthetic"]


@pytest.mark.parametrize("encoding,separator", [("utf-16", "\t"), ("utf-8", "|"), ("utf-8-sig", ",")])
def test_remaining_supported_csv_settings_and_literal_null_tokens(encoding, separator):
    text = separator.join(["code", "note"]) + "\n" + separator.join(["001", "NA"]) + "\n" + separator.join(["002", "null"]) + "\n"
    frame = read_csv(text.encode(encoding), encoding=encoding, separator=separator)
    assert frame["code"].tolist() == ["001", "002"]
    assert frame["note"].tolist() == ["NA", "null"]


def test_deduplication_never_drops_rows_only_made_equal_by_cleaning():
    source = pd.DataFrame({"name": [" A ", "A", " A "]})
    result = clean(source, CleaningConfig(trim=True, drop_duplicates=True, confirm_duplicates=True))
    assert result.data["name"].tolist() == ["A", "A"]
    assert result.modified_rows == 2
    assert result.removed_rows == 1
    assert result.changes["row"].tolist() == [2, 4, 4]
    assert result.changes["operation"].tolist() == ["trim", "trim", "drop_exact_duplicate"]
    assert source["name"].tolist() == [" A ", "A", " A "]


@pytest.mark.parametrize("constraint", ["MAX_FILE_BYTES", "MAX_COLUMNS", "MAX_CELLS", "MAX_EXPANDED_BYTES"])
def test_each_resource_limit_rejects_instead_of_truncating(monkeypatch, constraint):
    from excel_cleaner import io
    monkeypatch.setattr(io, constraint, 1)
    if constraint == "MAX_EXPANDED_BYTES":
        buffer = BytesIO()
        workbook = Workbook()
        workbook.active.append(["code", "name"])
        workbook.save(buffer)
        workbook.close()
        data = buffer.getvalue()
        with pytest.raises(InputError):
            read_excel(data, "Sheet")
    else:
        with pytest.raises(InputError):
            read_csv(b"code,name\n001,Synthetic\n")
