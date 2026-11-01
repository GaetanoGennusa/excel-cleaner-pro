"""Verify the actual proposed small-service scope with synthetic records."""
from io import BytesIO

import pandas as pd
from openpyxl import load_workbook

from excel_cleaner.export import export_xlsx
from excel_cleaner.transforms import clean, CleaningConfig


def test_one_thousand_rows_twenty_columns_with_complete_audit_export():
    source = pd.DataFrame({"code": [f"{row:05d}" for row in range(1000)],
                           **{f"field_{column}": [f"  Synthetic {row}  " for row in range(1000)] for column in range(1, 20)}})
    result = clean(source, CleaningConfig(trim=True))
    assert result.data.shape == (1000, 20)
    assert result.modified_rows == 1000
    assert len(result.changes) == 19_000
    assert source.iloc[0, 1] == "  Synthetic 0  "
    workbook = load_workbook(BytesIO(export_xlsx(result)), read_only=True)
    assert sum(1 for _ in workbook["Cleaned_Data"].values) == 1001
    assert sum(1 for _ in workbook["Change_Log"].values) == 19_001
    assert workbook["Cleaned_Data"]["A2"].value == "00000"
    workbook.close()
