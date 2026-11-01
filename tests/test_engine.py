"""Synthetic regression cases for the public cleaning engine."""
from io import BytesIO, StringIO
import csv
import json
from datetime import datetime

import pandas as pd
import pytest
from openpyxl import load_workbook

from excel_cleaner.io import InputError, read_csv, read_excel, excel_sheets
from excel_cleaner.transforms import CleaningConfig, clean
from excel_cleaner.export import export_xlsx, export_csv


def test_default_preserves_original_and_nulls():
    original = pd.DataFrame({" Code ": ["001", None, "  X  "], "Amount": ["1.234,56", "", "n/a"]})
    snapshot = original.copy(deep=True)
    result = clean(original, CleaningConfig())
    pd.testing.assert_frame_equal(original, snapshot)
    pd.testing.assert_frame_equal(result.data, snapshot)
    assert result.modified_rows == 0
    assert result.removed_rows == 0


def test_trim_changes_rows_without_losing_nulls():
    frame = pd.DataFrame({"name": [" Alice ", None, "Bob"], "code": [" 001 ", "002", "003"]})
    result = clean(frame, CleaningConfig(trim=True))
    assert result.data.loc[0, "name"] == "Alice"
    assert result.data.loc[0, "code"] == "001"
    assert pd.isna(result.data.loc[1, "name"])
    assert result.modified_rows == 1
    assert len(result.data) == 3
    assert len(result.changes) >= 1


def test_exact_duplicates_require_confirmation():
    frame = pd.DataFrame({"code": ["001", "001", "002"], "name": ["A", "A", " A "]})
    with pytest.raises(ValueError):
        clean(frame, CleaningConfig(drop_duplicates=True, confirm_duplicates=False))
    result = clean(frame, CleaningConfig(drop_duplicates=True, confirm_duplicates=True))
    assert len(result.data) == 2
    assert result.removed_rows == 1
    assert result.data["code"].tolist() == ["001", "002"]


def test_possible_duplicates_never_removed_by_default():
    frame = pd.DataFrame({"name": ["Alice", " alice ", "ALICE"]})
    result = clean(frame, CleaningConfig(trim=True))
    assert len(result.data) == 3
    assert result.removed_rows == 0


@pytest.mark.parametrize("locale,values,expected", [
    ("it", ["1.234,56", "12,50", "-42,10"], [1234.56, 12.5, -42.1]),
    ("international", ["1,234.56", "12.50", "-42.10"], [1234.56, 12.5, -42.1]),
])
def test_explicit_numeric_locales(locale, values, expected):
    result = clean(pd.DataFrame({"amount": values}), CleaningConfig(number_columns={"amount": locale}))
    assert result.data["amount"].tolist() == pytest.approx(expected)
    assert result.modified_rows == 3


def test_leading_zero_identifiers_survive_selected_conversion():
    frame = pd.DataFrame({"code": ["00123", "00001", "AB-7"]})
    result = clean(frame, CleaningConfig(number_columns={"code": "it"}))
    assert result.data["code"].tolist() == ["00123", "00001", "AB-7"]
    assert len(result.issues) > 0


def test_failed_conversion_keeps_original_and_reports_issue():
    result = clean(pd.DataFrame({"amount": ["12,30", "not a number"]}), CleaningConfig(number_columns={"amount": "it"}))
    assert result.data.loc[1, "amount"] == "not a number"
    assert len(result.issues) > 0
    assert len(result.data) == 2


def test_italian_currency_and_malformed_grouping():
    frame = pd.DataFrame({"amount": ["€ 1.234,56", "1.23,45"]})
    result = clean(frame, CleaningConfig(number_columns={"amount": "it"}))
    assert result.data.loc[0, "amount"] == pytest.approx(1234.56)
    assert result.data.loc[1, "amount"] == "1.23,45"
    assert len(result.issues) > 0


def test_ambiguous_dates_untouched_until_format_selected():
    frame = pd.DataFrame({"date": ["01/02/2025", "12/11/2025", "impossible"]})
    pd.testing.assert_frame_equal(clean(frame, CleaningConfig()).data, frame)
    result = clean(frame, CleaningConfig(date_columns={"date": "%d/%m/%Y"}))
    assert str(result.data.loc[0, "date"]).startswith("2025-02-01")
    assert str(result.data.loc[1, "date"]).startswith("2025-11-12")
    assert result.data.loc[2, "date"] == "impossible"
    assert len(result.issues) > 0


@pytest.mark.parametrize("encoding", ["utf-8-sig", "cp1252", "latin-1"])
def test_csv_encodings_separators_and_zero_codes(encoding):
    data = "code;city;amount\n001;Città;1.234,56\n002;Forlì;12,50\n".encode(encoding)
    frame = read_csv(data, encoding=encoding, separator=";")
    assert frame.loc[0, "code"] == "001"
    assert frame.loc[1, "city"] == "Forlì"
    assert frame.loc[0, "amount"] == "1.234,56"


@pytest.mark.parametrize("data", [b"", b'code,name\n1,"unterminated\n', b"code,name\n1,A\n2,B,extra\n"])
def test_empty_or_malformed_csv_reports_input_error(data):
    with pytest.raises(InputError):
        read_csv(data)


def test_invalid_excel_reports_input_error():
    with pytest.raises(InputError):
        excel_sheets(b"this is not an xlsx")


def test_excel_sheet_selection_and_zero_codes():
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"code": ["001", "002"]}).to_excel(writer, sheet_name="Customers", index=False)
        pd.DataFrame({"note": ["Synthetic"]}).to_excel(writer, sheet_name="Notes", index=False)
    data = buffer.getvalue()
    assert excel_sheets(data) == ["Customers", "Notes"]
    assert read_excel(data, "Customers")["code"].tolist() == ["001", "002"]
    with pytest.raises(InputError):
        read_excel(data, "Missing")


def test_transformations_are_idempotent():
    frame = pd.DataFrame({" Name ": [" Alice ", "BOB"], "amount": ["1.234,56", "12,50"]})
    config = CleaningConfig(trim=True, case_columns={" Name ": "lower"}, number_columns={"amount": "it"})
    first = clean(frame, config)
    second = clean(first.data, config)
    pd.testing.assert_frame_equal(first.data, second.data)
    assert second.modified_rows == 0


def test_header_standardization_does_not_overwrite_columns():
    frame = pd.DataFrame([["A", "B"]], columns=[" Customer Name ", "customer_name"])
    result = clean(frame, CleaningConfig(headers=True))
    assert len(set(result.data.columns)) == 2
    assert result.data.iloc[0].tolist() == ["A", "B"]
    assert all(str(c).strip() == c for c in result.data.columns)


def test_excel_export_has_required_sheets_and_no_executable_formulas():
    frame = pd.DataFrame({"code": ["001", "002"], "note": ["=1+1", "@SUM(A1)"]})
    result = clean(frame, CleaningConfig())
    workbook = load_workbook(BytesIO(export_xlsx(result)), data_only=False)
    assert {"Cleaned_Data", "Issues", "Change_Log"}.issubset(workbook.sheetnames)
    sheet = workbook["Cleaned_Data"]
    assert sheet.max_row == 3
    assert sheet["A2"].value == "001"
    for worksheet in workbook:
        assert all(cell.data_type != "f" for row in worksheet for cell in row)
    assert workbook["Change_Log"].max_row == 1  # No invented change events.
    metadata = dict(list(workbook["Metadata"].values)[1:])
    assert datetime.fromisoformat(metadata["timestamp_utc"]).tzinfo is not None
    assert json.loads(metadata["configuration_json"])["trim"] is False
    assert all(json.loads(metadata["integrity_checks_json"]).values())


def test_csv_formula_safety_keeps_native_negative_numbers():
    frame = pd.DataFrame({"value": ["=1+1", "+SUM(A1)", "-cmd", "@x", "  =1+1", -3, "001"]})
    rows = list(csv.reader(StringIO(export_csv(frame).decode("utf-8-sig")), delimiter=";"))
    for row in rows[1:6]:
        assert row[0].startswith("'")
    assert rows[6][0] == "-3"
    assert rows[7][0] == "001"
