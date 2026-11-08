"""Catalog demo claims checked against source records and delivered artifacts."""
from dataclasses import replace
import json
from pathlib import Path

from openpyxl import load_workbook
import pandas as pd

from excel_cleaner.io import read_csv
from excel_cleaner.transforms import CleaningConfig, clean
from scripts.generate_catalog_demo import SIMILAR_SKUS, TARGET, catalog_rules, source_catalog


def test_catalog_source_and_default_rules_preserve_all_records():
    source = read_csv((TARGET / "catalogo_originale.csv").read_bytes(), separator=";")
    pd.testing.assert_frame_equal(source, source_catalog())
    assert source.shape == (200, 8)
    assert source.sku.nunique() == 190
    assert source.duplicated().sum() == 6
    assert source.isna().sum().sum() == 7
    assert source.loc[72, "note"] == "N/A"
    result = clean(source, CleaningConfig())
    pd.testing.assert_frame_equal(result.data, source)
    assert result.modified_rows == result.removed_rows == 0


def test_catalog_rules_keep_uncertain_records_and_source_references():
    source = read_csv((TARGET / "catalogo_originale.csv").read_bytes(), separator=";")
    original = source.copy(deep=True)
    result = clean(source, catalog_rules())
    pd.testing.assert_frame_equal(source, original)
    assert result.data.shape == (194, 8)
    assert result.removed_rows == 6 and result.modified_rows == 200
    assert result.data.iloc[0].tolist() == [
        "000001", "Tazza Aurora Modello 001", "Cucina", 1234.56, 1, "2026-02-01", "00101", "Record sintetico",
    ]
    for sku in SIMILAR_SKUS:
        pair = result.data[result.data.sku == sku]
        assert len(pair) == 2 and pair.iloc[0].equals(pair.iloc[1])
    for number, column, value in [(18, "prezzo_eur", "da verificare"), (88, "prezzo_eur", "12,3,4"),
                                  (148, "prezzo_eur", "N/D"), (62, "disponibilita", "in arrivo"),
                                  (45, "aggiornato_il", "31/02/2026"), (145, "aggiornato_il", "data da confermare")]:
        assert result.data.loc[result.data.sku == f"{number:06d}", column].iloc[0] == value
        assert ((result.issues.row == number + 1) & (result.issues.column == column)).any()
    assert result.data.isna().equals(source.iloc[result.data.index].isna())
    removed = result.changes[result.changes.operation == "drop_exact_duplicate"]
    assert removed.row.tolist() == [192, 193, 194, 195, 196, 197]
    assert not result.changes.column.isin(["sku", "codice_fornitore"]).any()
    assert all(result.integrity.values())


def test_catalog_reapplying_original_is_stable_and_conversions_are_idempotent():
    source = source_catalog()
    first, second = clean(source, catalog_rules()), clean(source, catalog_rules())
    pd.testing.assert_frame_equal(first.data, second.data)
    pd.testing.assert_frame_equal(first.changes, second.changes)
    # Re-importing cleaned output changes the source used for deduplication.
    # Test conversion idempotence separately, without authorizing new deletion.
    repeated = clean(first.data, replace(catalog_rules(), drop_duplicates=False, confirm_duplicates=False))
    pd.testing.assert_frame_equal(repeated.data, first.data)
    assert repeated.modified_rows == repeated.removed_rows == 0


def test_delivered_catalog_csv_workbook_and_portfolio_agree():
    source = read_csv((TARGET / "catalogo_originale.csv").read_bytes(), separator=";")
    result = clean(source, catalog_rules())
    summary = json.loads((TARGET / "summary.json").read_text(encoding="utf-8"))
    csv = read_csv((TARGET / "catalogo_pulito.csv").read_bytes(), separator=";")
    assert csv.shape == (194, 8)
    assert csv.iloc[0].prezzo_eur == "1234.56" and csv.iloc[0].sku == "000001"
    book = load_workbook(TARGET / "catalogo_report.xlsx", data_only=False)
    try:
        assert book.sheetnames == ["Cleaned_Data", "Issues", "Change_Log", "Metadata"]
        assert list(book["Cleaned_Data"].values) == [tuple(result.data.columns), *result.data.itertuples(index=False, name=None)]
        assert book["Cleaned_Data"]["A2"].data_type == book["Cleaned_Data"]["G2"].data_type == "s"
        assert all(cell.data_type != "f" for sheet in book for row in sheet for cell in row)
        assert book["Change_Log"].max_row - 1 == summary["change_events"] == len(result.changes)
        assert book["Issues"].max_row - 1 == summary["issue_events"] == len(result.issues)
        metadata = dict(list(book["Metadata"].values)[1:])
        assert metadata["removed_rows"] == 6
        assert json.loads(metadata["configuration_json"]) == summary["configuration"]
        assert json.loads(metadata["ingestion_json"])["sha256"] == summary["input_sha256"]
    finally:
        book.close()
    assert summary["input_rows"] == 200 and summary["output_rows"] == 194
    assert summary["missing_output_cells"] == 7 and summary["similar_sku_groups_kept"] == 4
    html = (TARGET / "index.html").read_text(encoding="utf-8")
    assert "{{" not in html
    assert "dati interamente sintetici" in html
