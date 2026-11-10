"""Issue status, Italian report summary and clearer messages from the manual QA of 10 November 2026."""
from io import BytesIO
from pathlib import Path

from openpyxl import load_workbook
import pandas as pd
import pytest

from excel_cleaner.export import export_xlsx
from excel_cleaner.io import InputError, read_csv
from excel_cleaner.transforms import CleaningConfig, clean

DEMO = Path(__file__).resolve().parents[1] / "demo"
FULL_RULES = CleaningConfig(trim=True, case_columns={"name": "title"}, number_columns={"amount": "it"},
                            date_columns={"date": "%d/%m/%Y"}, drop_duplicates=True, confirm_duplicates=True)


def demo_source() -> pd.DataFrame:
    return read_csv((DEMO / "10_before.csv").read_bytes(), separator=";")


def statuses(result) -> list[tuple]:
    return list(zip(result.issues["row"], result.issues["column"], result.issues["status"]))


def test_issue_status_separates_resolved_from_open_items():
    result = clean(demo_source(), FULL_RULES)
    assert sorted(statuses(result)) == [(2, "date", "Risolto"), (4, "*", "Risolto"),
                                        (5, "amount", "Da verificare"), (5, "date", "Da verificare")]
    assert result.issues["note"].map(bool).all()


def test_without_rules_every_source_issue_stays_open():
    result = clean(demo_source(), CleaningConfig())
    assert set(result.issues["status"]) == {"Da verificare"}
    assert len(result.issues) == 2  # Ambiguous date and exact duplicate, both untouched.


def test_formula_like_text_is_reported_as_protected():
    result = clean(read_csv((DEMO / "07_untrusted_text.csv").read_bytes(), separator=";"), CleaningConfig())
    assert set(result.issues["status"]) == {"Protetto"}


def test_status_does_not_change_cleaned_values_or_counts():
    source = demo_source()
    result = clean(source, FULL_RULES)
    assert result.data["code"].tolist() == ["001", "002", "003"]
    assert result.data.loc[3, "amount"] == "unknown" and result.data.loc[3, "date"] == "31/02/2025"
    assert len(result.changes) == 12 and result.removed_rows == 1


def test_impossible_date_message_is_italian():
    result = clean(pd.DataFrame({"date": ["31/02/2025", "2025/01/01"]}), CleaningConfig(date_columns={"date": "%d/%m/%Y"}))
    assert result.issues["issue"].tolist() == ["Data inesistente: giorno o mese fuori intervallo",
                                               "La data non corrisponde al formato scelto"]
    assert result.data["date"].tolist() == ["31/02/2025", "2025/01/01"]


def test_number_and_date_conflict_names_the_column():
    with pytest.raises(ValueError, match="«date»"):
        clean(pd.DataFrame({"date": ["01/02/2025"]}), CleaningConfig(number_columns={"date": "it"}, date_columns={"date": "%d/%m/%Y"}))


@pytest.mark.parametrize("content", [b"", b"\xef\xbb\xbf", b"\r\n\r\n"])
def test_empty_csv_has_a_specific_message(content):
    with pytest.raises(InputError, match="vuoto"):
        read_csv(content, separator=";")


def test_metadata_starts_with_italian_summary_and_keeps_technical_rows():
    workbook = load_workbook(BytesIO(export_xlsx(clean(demo_source(), FULL_RULES))))
    try:
        rows = list(workbook["Metadata"].values)
        assert rows[1][0] == "riepilogo"
        summary = rows[1][1]
        assert "Righe originali: 4 · righe finali: 3 · duplicati rimossi: 1" in summary
        assert "2 da verificare, 2 risolte, 0 protette" in summary
        assert "date %d/%m/%Y su «date»" in summary and "tutti superati" in summary
        keys = [row[0] for row in rows[1:]]
        assert {"timestamp_utc", "configuration_json", "integrity_checks_json", "removed_rows"}.issubset(keys)
        assert list(workbook["Issues"].values)[0] == ("row", "column", "issue", "value", "status", "note")
        assert all(cell.data_type != "f" for sheet in workbook for row in sheet for cell in row)
    finally:
        workbook.close()
