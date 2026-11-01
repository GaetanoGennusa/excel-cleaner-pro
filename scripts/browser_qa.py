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
            subprocess.run([node, str(root / "scripts/browser_qa.cjs")], cwd=root, env=environment, check=True, timeout=240)
            workbook = load_workbook(output / "downloaded_report.xlsx", data_only=False)
            assert workbook.sheetnames == ["Cleaned_Data", "Issues", "Change_Log", "Metadata"]
            rows = list(workbook["Cleaned_Data"].values)
            assert rows[1] == ("001", "Ada Test", 1234.56, "01/02/2025"), repr(rows[1])
            assert len(rows) == 4
            assert rows[-1][-2:] == ("unknown", "31/02/2025")
            assert all(cell.data_type != "f" for sheet in workbook for row in sheet for cell in row)
            workbook.close()
            csv_data = read_csv((output / "downloaded_data.csv").read_bytes(), separator=";")
            assert len(csv_data) == 3 and csv_data.iloc[0, 0] == "001"
            (output / "artifact_validation.json").write_text(json.dumps({"downloaded_xlsx_reopened": True, "expected_data_and_sheets": True, "no_executable_formulas": True, "csv_rows_and_identifier": True}), encoding="utf-8")
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
