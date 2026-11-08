"""Record the real catalog workflow and verify the local portfolio, offline."""
from contextlib import ExitStack
from datetime import datetime, timezone
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

from openpyxl import load_workbook

from excel_cleaner.io import read_csv
from scripts.generate_catalog_demo import ROOT, TARGET, catalog_rules, write_portfolio
from excel_cleaner.transforms import clean


def validate(output: Path) -> dict:
    source = read_csv((TARGET / "catalogo_originale.csv").read_bytes(), separator=";")
    expected = clean(source, catalog_rules())
    with BytesIO((output / "app_report.xlsx").read_bytes()) as buffer:
        book = load_workbook(buffer)
        try:
            assert book.sheetnames == ["Cleaned_Data", "Issues", "Change_Log", "Metadata"]
            assert list(book["Cleaned_Data"].values) == [tuple(expected.data.columns), *expected.data.itertuples(index=False, name=None)]
            assert book["Cleaned_Data"]["A2"].data_type == book["Cleaned_Data"]["G2"].data_type == "s"
            assert book["Cleaned_Data"]["D2"].value == 1234.56
            assert book["Cleaned_Data"]["F2"].value == "2026-02-01"
            assert all(cell.data_type != "f" for sheet in book for row in sheet for cell in row)
            metadata = dict(list(book["Metadata"].values)[1:])
            assert json.loads(metadata["configuration_json"]) == expected.config
            assert metadata["removed_rows"] == 6 and metadata["modified_rows"] == 200
            assert book["Change_Log"].max_row == len(expected.changes) + 1
        finally:
            book.close()
    assert (output / "app_data.csv").read_bytes() == (TARGET / "catalogo_pulito.csv").read_bytes()
    return {"downloaded_rows": 194, "duplicates_removed": 6, "modified_source_rows": 200,
            "all_values_match_engine": True, "configuration_matches_ui_choices": True,
            "leading_zero_identifiers_are_text": True, "no_formula_cells": True,
            "downloaded_csv_matches_delivered_csv": True}


def main() -> None:
    runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node"
    node = os.environ.get("ECP_NODE") or shutil.which("node") or str(runtime / "bin/node.exe")
    playwright = Path(os.environ.get("ECP_PLAYWRIGHT", str(runtime / "node_modules/playwright")))
    browser_cache = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".cache"))) / "ms-playwright"
    candidates = sorted(browser_cache.glob("chromium-*/chrome-win64/chrome.exe"))
    chromium = os.environ.get("ECP_CHROMIUM") or (str(candidates[-1]) if candidates else "")
    if not Path(node).is_file() or not playwright.is_dir() or not Path(chromium).is_file():
        raise SystemExit("Existing Node, Playwright and Chromium required; no downloads. See docs/BROWSER_QA.md.")
    for port in [8523, 8524]:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = ROOT / "outputs" / f"catalog-qa-{stamp}"
    output.mkdir(parents=True)
    environment = os.environ.copy()
    environment.update(ECP_PLAYWRIGHT=str(playwright), ECP_CHROMIUM=chromium, ECP_QA_OUTPUT=str(output))
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    processes = []
    with ExitStack() as stack:
        try:
            for name, command in [
                ("streamlit", [sys.executable, "-m", "streamlit", "run", "app.py", "--server.address", "127.0.0.1", "--server.port", "8523"]),
                ("portfolio", [sys.executable, "-m", "http.server", "8524", "--bind", "127.0.0.1", "--directory", str(TARGET)]),
            ]:
                log = stack.enter_context((output / f"{name}.log").open("w", encoding="utf-8"))
                processes.append(subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, creationflags=flags))
            for url in ["http://127.0.0.1:8523/_stcore/health", "http://127.0.0.1:8524/"]:
                for _ in range(60):
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError(f"Local server failed; see {output}")
                    try:
                        with urlopen(url, timeout=1) as response:
                            if response.status == 200:
                                break
                    except (URLError, TimeoutError):
                        pass
                    time.sleep(.25)
                else:
                    raise RuntimeError(f"Server startup timeout: {url}")
            command = [node, str(ROOT / "scripts/catalog_browser_qa.cjs")]
            subprocess.run([*command, "--app"], cwd=ROOT, env=environment, check=True, timeout=180)
            checks = validate(output)
            screenshots = TARGET / "screenshots"
            screenshots.mkdir(exist_ok=True)
            for name in ["overview.png", "preview.png", "issues.png", "export.png"]:
                shutil.copy2(output / name, screenshots / name)
            shutil.copy2(output / "demo_catalogo.webm", TARGET / "demo_catalogo.webm")
            shutil.copy2(output / "app_report.xlsx", TARGET / "catalogo_report_browser.xlsx")
            write_portfolio(TARGET, json.loads((TARGET / "summary.json").read_text(encoding="utf-8")))
            subprocess.run([*command, "--portfolio"], cwd=ROOT, env=environment, check=True, timeout=120)
            for downloaded, original in [("portfolio_source.csv", "catalogo_originale.csv"),
                                         ("portfolio_cleaned.csv", "catalogo_pulito.csv"), ("portfolio_report.xlsx", "catalogo_report.xlsx")]:
                assert (output / downloaded).read_bytes() == (TARGET / original).read_bytes()
            for name in ["portfolio_desktop.png", "portfolio_mobile.png"]:
                shutil.copy2(output / name, screenshots / name)
            evidence = ROOT / "docs/catalog-demo"
            evidence.mkdir(exist_ok=True)
            (output / "artifact_validation.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
            for name in ["app_browser_results.json", "portfolio_browser_results.json", "artifact_validation.json"]:
                shutil.copy2(output / name, evidence / name)
            print(f"Catalog app, recording, downloads and portfolio checks passed. Evidence: {output}")
        finally:
            for process in reversed(processes):
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__":
    main()
