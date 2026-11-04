"""Optional real-browser QA using an existing Node/Playwright/Chromium installation.

No dependency or browser is downloaded. Only synthetic fixtures and evidence are
written under outputs/. Streamlit and the headless browser are always stopped.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import os
import shutil
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

from openpyxl import Workbook, load_workbook

from excel_cleaner.io import read_csv


SHEETS = ["Cleaned_Data", "Issues", "Change_Log", "Metadata"]
FULL_RULES = [("001", "Ada Test", 1234.56, "2025-02-01"), ("002", "Bruno Demo", 12.5, "2025-03-15"),
              ("003", "Carla Sintetica", "unknown", "31/02/2025")]


def _open(path: Path) -> dict:
    """Read every sheet of a downloaded report and check it holds no formula cells."""
    workbook = load_workbook(path, data_only=False)
    try:
        assert workbook.sheetnames == SHEETS, workbook.sheetnames
        assert all(cell.data_type != "f" for sheet in workbook for row in sheet for cell in row), "formula cell"
        assert workbook["Cleaned_Data"]["A2"].data_type == "s", "identifier is not text"
        sheets = {name: list(workbook[name].values) for name in SHEETS}
    finally:
        workbook.close()
    sheets["meta"] = {key: value for key, value in sheets["Metadata"][1:]}
    sheets["config"] = json.loads(sheets["meta"]["configuration_json"])
    return sheets


def _has_issue(report: dict, row: int, column: str, value: str, starts: str = "") -> bool:
    return any(r[0] == row and r[1] == column and r[3] == value and str(r[2]).startswith(starts) for r in report["Issues"][1:])


def validate_downloads(output: Path) -> dict:
    """Check the files the browser really downloaded; returns the evidence summary."""
    summary = {}
    for label in ["reduced", "animated"]:
        report = _open(output / f"{label}_report.xlsx")
        assert report["Cleaned_Data"][1:] == FULL_RULES, report["Cleaned_Data"]
        config = report["config"]
        assert config["date_columns"] == {"date": "%d/%m/%Y"} and config["number_columns"] == {"amount": "it"}, config
        assert config["case_columns"] == {"name": "title"} and config["trim"] and config["drop_duplicates"] and config["confirm_duplicates"], config
        log = report["Change_Log"][1:]
        assert (2, "date", "date", "01/02/2025", "2025-02-01") in log, log
        assert (4, "*", "drop_exact_duplicate", "exact source row", "removed") in log, log
        assert not any(r[1] == "code" for r in log), "identifier changed"
        assert report["meta"]["removed_rows"] == 1
        assert _has_issue(report, 5, "amount", "unknown") and _has_issue(report, 5, "date", "31/02/2025")
        data = read_csv((output / f"{label}_data.csv").read_bytes(), separator=";")
        assert len(data) == 3 and data.iloc[0, 0] == "001" and data.iloc[0, 3] == "2025-02-01", data
        summary[label] = {"rows": 3, "code_001_text": True, "amount_1234_56": True, "date_2025_02_01": True,
                          "unknown_and_31_02_kept_and_reported": True, "metadata_date_format": "%d/%m/%Y",
                          "change_log_date_and_duplicate_removal": True, "csv_rows_identifier_date": True}
    report = _open(output / "nodate_report.xlsx")
    assert report["Cleaned_Data"][1][3] == "01/02/2025" and report["config"]["date_columns"] == {}
    assert _has_issue(report, 2, "date", "01/02/2025", "Data ambigua")
    summary["no_date_rule"] = {"ambiguous_date_unchanged": True, "ambiguous_date_reported": True}
    report = _open(output / "switch_report.xlsx")
    second = read_csv((output.parents[1] / "demo/04_italian_amounts.csv").read_bytes(), separator=";")
    expected = [tuple(second.columns), *second.itertuples(index=False, name=None)]
    assert report["Cleaned_Data"] == expected, report["Cleaned_Data"]
    summary["replaced_source"] = {"report_from_second_file_only": True}
    for label in ["tablet", "mobile"]:
        report = _open(output / f"{label}_report.xlsx")
        assert report["Cleaned_Data"][1] == FULL_RULES[0] and len(report["Cleaned_Data"]) == 5, report["Cleaned_Data"]
        assert report["config"]["date_columns"] == {"date": "%d/%m/%Y"}
        summary[label] = {"rows": 4, "date_2025_02_01": True, "amount_1234_56": True}
    summary["all_reports_without_formula_cells"] = True
    return summary


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node"
    node = os.environ.get("ECP_NODE") or shutil.which("node") or str(runtime / "bin/node.exe")
    playwright = Path(os.environ.get("ECP_PLAYWRIGHT", str(runtime / "node_modules/playwright")))
    if not Path(node).exists() or not playwright.exists():
        raise SystemExit("Existing Node and Playwright required. Set ECP_NODE and ECP_PLAYWRIGHT; no automatic installation.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = root / "outputs" / f"browser-qa-{stamp}"
    output.mkdir(parents=True)
    frame = read_csv((root / "demo/10_before.csv").read_bytes(), separator=";")
    fixture = Workbook()
    data = fixture.active
    data.title = "Customers"
    data.append(list(frame.columns))
    for row in frame.itertuples(index=False, name=None):
        data.append(row)
    fixture.create_sheet("Notes").append(["Synthetic notes"])
    fixture.save(output / "multi_sheet.xlsx")
    fixture.close()
    (output / "oversize.csv").write_bytes(b"x" * (10 * 1024 * 1024 + 1))
    environment = os.environ.copy()
    environment.update({"ECP_PLAYWRIGHT": str(playwright), "ECP_QA_OUTPUT": str(output)})
    if "ECP_CHROMIUM" not in environment:
        cache = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".cache"))) / "ms-playwright"
        existing = sorted(cache.glob("chromium-*/chrome-win64/chrome.exe"))
        if existing:
            environment["ECP_CHROMIUM"] = str(existing[-1])
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    with (output / "server.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8521", "--server.address", "127.0.0.1"],
            cwd=root, stdout=log, stderr=subprocess.STDOUT, creationflags=flags,
        )
        try:
            ready = False
            for _ in range(60):
                if process.poll() is not None:
                    raise RuntimeError(f"Streamlit failed: see {output / 'server.log'}")
                try:
                    with urlopen("http://127.0.0.1:8521/_stcore/health", timeout=1) as response:
                        ready = response.status == 200
                except (URLError, TimeoutError):
                    pass
                if ready:
                    break
                time.sleep(.25)
            if not ready:
                raise RuntimeError("Streamlit startup timed out")
            subprocess.run([node, str(root / "scripts/browser_qa.cjs")], cwd=root, env=environment, check=True, timeout=900)
            (output / "artifact_validation.json").write_text(json.dumps(validate_downloads(output), indent=2), encoding="utf-8")
            print(f"Browser QA and downloaded workbook checks passed. Evidence: {output}")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
