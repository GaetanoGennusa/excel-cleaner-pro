"""Check the delivered portfolio artifacts, not only an in-memory export."""
import csv
from pathlib import Path

from openpyxl import load_workbook


def test_delivered_demo_agrees_with_report():
    directory = Path(__file__).resolve().parents[1] / "demo"
    assert len([p for p in directory.glob("*.csv") if "after" not in p.name]) >= 8
    workbook = load_workbook(directory / "10_report.xlsx", data_only=False)
    rows = list(workbook["Cleaned_Data"].values)
    assert len(rows) == 4
    assert rows[1] == ("001", "Ada Test", 1234.56, "2025-02-01")
    assert rows[-1] == ("003", "Carla Sintetica", "unknown", "31/02/2025")
    metadata = dict(list(workbook["Metadata"].values)[1:])
    assert metadata["removed_rows"] == 1
    assert metadata["modified_rows"] == 3
    with (directory / "10_after.csv").open(encoding="utf-8-sig", newline="") as file:
        csv_rows = list(csv.reader(file, delimiter=";"))
    assert len(csv_rows) == len(rows)
    assert csv_rows[1][0] == "001"
    assert all(cell.data_type != "f" for sheet in workbook for row in sheet for cell in row)
    workbook.close()
