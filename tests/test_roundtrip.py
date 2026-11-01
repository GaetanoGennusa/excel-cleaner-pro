"""Round-trip invariants including empty trailing rows and reordered indices."""
import pandas as pd
from io import BytesIO
from openpyxl import Workbook

from excel_cleaner.io import read_excel
from excel_cleaner.export import export_xlsx
from excel_cleaner.transforms import clean, CleaningConfig


def test_export_import_preserves_trailing_empty_source_rows():
    source = pd.DataFrame({"code": ["001", None, None], "name": ["Demo", "", None]}, dtype=object)
    exported = export_xlsx(clean(source, CleaningConfig()))
    reopened = read_excel(exported, "Cleaned_Data")
    assert len(reopened) == len(source)
    assert reopened.iloc[0].tolist() == ["001", "Demo"]
    assert reopened.iloc[2].isna().all()


def test_nonmonotonic_source_index_is_preserved():
    source = pd.DataFrame({"name": [" A ", None, "B"]}, index=[9, 2, 6])
    result = clean(source, CleaningConfig(trim=True))
    assert result.data.index.tolist() == [9, 2, 6]
    assert all(result.integrity.values())


def test_dimensionless_xlsx_retains_later_columns_without_headers():
    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet("Data")
    sheet.append(["code"])
    sheet.append(["001", "Extra data"])
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    frame = read_excel(buffer.getvalue(), "Data")
    assert frame.shape == (1, 2)
    assert frame.iloc[0].tolist() == ["001", "Extra data"]
    assert frame.columns.is_unique
