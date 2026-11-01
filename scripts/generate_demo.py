"""Generate only synthetic fixtures and one reproducible before/after example."""
from pathlib import Path
import pandas as pd

from excel_cleaner.io import read_csv
from excel_cleaner.transforms import CleaningConfig, clean
from excel_cleaner.export import export_csv, export_xlsx


def main() -> None:
    target = Path(__file__).resolve().parents[1] / "demo"
    target.mkdir(exist_ok=True)
    datasets = {
        "01_duplicates.csv": "code;name\n001;Ada Test\n001;Ada Test\n002;Bruno Demo\n",
        "02_nulls.csv": "code;name;amount\n001;;\n002;Finta Persona;12,50\n",
        "03_ambiguous_dates.csv": "code;date\n001;01/02/2025\n002;12/11/2025\n003;31/02/2025\n",
        "04_italian_amounts.csv": "code;amount\n001;1.234,56\n002;12,50\n003;-42,10\n",
        "05_leading_zero_codes.csv": "code;postal_code\n00001;00100\n00002;01000\n",
        "06_international_amounts.csv": "code;amount\n001;1,234.56\n002;12.50\n",
        "07_untrusted_text.csv": "code;note\n001;=1+1\n002;@SUM(A1)\n003;+1+2\n",
        "08_malformed.csv": 'code;name\n001;"Unclosed quote\n',
        "09_empty.csv": "",
        "10_before.csv": "code;name;amount;date\n001;  Ada Test  ;1.234,56;01/02/2025\n002; BRUNO DEMO ;12,50;15/03/2025\n002; BRUNO DEMO ;12,50;15/03/2025\n003;Carla Sintetica;unknown;31/02/2025\n",
    }
    for name, content in datasets.items():
        (target / name).write_bytes(content.encode("utf-8-sig"))
    (target / "11_cp1252.csv").write_bytes("code;city\n001;Città\n002;Forlì\n".encode("cp1252"))
    frame = read_csv((target / "10_before.csv").read_bytes(), separator=";")
    config = CleaningConfig(trim=True, case_columns={"name": "title"}, number_columns={"amount": "it"}, date_columns={"date": "%d/%m/%Y"}, drop_duplicates=True, confirm_duplicates=True)
    result = clean(frame, config)
    (target / "10_after.csv").write_bytes(export_csv(result.data))
    (target / "10_report.xlsx").write_bytes(export_xlsx(result))
    print(f"Synthetic demo files generated in {target}")


if __name__ == "__main__":
    main()
