"""Bounded synthetic engine benchmarks; each case uses a separate process.

No uploads or third-party data are read. Results are observations on this PC,
not performance guarantees. The largest cases reach 500,000 input cells.
"""
from __future__ import annotations

import argparse
import csv
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from io import BytesIO, StringIO
import json
import platform
from pathlib import Path
import subprocess
import sys
from time import perf_counter

import pandas as pd
from openpyxl import load_workbook

from excel_cleaner.export import export_xlsx
from excel_cleaner.io import InputError, read_csv
from excel_cleaner.transforms import CleaningConfig, clean


CASES = [(1000, 20), (50_000, 10), (2500, 200)]


def peak_memory_mib() -> float | None:
    """OS peak working set for this worker, including Python and its libraries."""
    if sys.platform != "win32":
        return None

    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in [
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage",
            ]
        ]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return round(counters.PeakWorkingSetSize / 1024**2, 1)


def run_case(rows: int, columns: int) -> dict:
    buffer = StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(["code", *[f"field_{i}" for i in range(1, columns)]])
    for row in range(rows):
        writer.writerow([f"{row:06d}", *[
            "" if column == 1 and row % 97 == 0 else f"  Test {row % 101}  "
            for column in range(1, columns)
        ]])
    raw = buffer.getvalue().encode("utf-8-sig")
    durations = {}

    started = perf_counter()
    source = read_csv(raw, separator=";")
    durations["read_csv"] = perf_counter() - started
    original = source.copy(deep=True)
    started = perf_counter()
    unchanged = clean(source, CleaningConfig())
    durations["default_clean_including_profile"] = perf_counter() - started
    pd.testing.assert_frame_equal(source, unchanged.data)
    assert unchanged.modified_rows == unchanged.removed_rows == 0
    del unchanged

    started = perf_counter()
    result = clean(source, CleaningConfig(trim=True))
    durations["trim_including_profile"] = perf_counter() - started
    pd.testing.assert_frame_equal(source, original)
    assert result.data.shape == (rows, columns)
    assert result.modified_rows == rows and result.removed_rows == 0
    assert all(result.integrity.values())
    assert result.data["code"].tolist() == source["code"].tolist()
    assert result.data.isna().equals(source.isna())
    expected_changes = rows * (columns - 1) - len(range(0, rows, 97))
    assert len(result.changes) == expected_changes
    started = perf_counter()
    report = export_xlsx(result)
    durations["export_xlsx"] = perf_counter() - started
    started = perf_counter()
    book = load_workbook(BytesIO(report), read_only=True, data_only=False)
    try:
        assert book.sheetnames == ["Cleaned_Data", "Issues", "Change_Log", "Metadata"]
        counts = {}
        for sheet in book:
            count = 0
            for record in sheet:
                assert all(cell.data_type != "f" for cell in record)
                count += 1
            counts[sheet.title] = count
        assert counts["Cleaned_Data"] == rows + 1
        assert counts["Change_Log"] == expected_changes + 1
        assert book["Cleaned_Data"]["A2"].value == "000000"
    finally:
        book.close()
    durations["reopen_and_scan_all_sheets"] = perf_counter() - started
    return {
        "rows": rows, "columns": columns, "input_cells": rows * columns,
        "input_bytes": len(raw), "xlsx_bytes": len(report),
        "modified_rows": rows, "change_events": expected_changes,
        "seconds": {key: round(value, 3) for key, value in durations.items()},
        "peak_worker_memory_mib": peak_memory_mib(), "checks_passed": True,
    }


def check_limits() -> list[str]:
    cases = {
        "rows_50001": "code\n" + "x\n" * 50_001,
        "columns_201": ";".join(f"c{i}" for i in range(201)) + "\n",
    }
    # 2501 x 200 exceeds cells while remaining below row and column limits.
    cases["cells_500200"] = ";".join(f"c{i}" for i in range(200)) + "\n" + (";".join(["x"] * 200) + "\n") * 2501
    passed = []
    for label, text in cases.items():
        try:
            read_csv(text.encode(), separator=";")
        except InputError:
            passed.append(label)
        else:
            raise AssertionError(f"Oversize fixture accepted: {label}")
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", nargs=2, type=int, metavar=("ROWS", "COLUMNS"))
    parser.add_argument("--output", type=Path, default=Path("outputs/benchmark.json"))
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(run_case(*args.worker)))
        return
    results = []
    for rows, columns in CASES:
        completed = subprocess.run(
            [sys.executable, "-m", "scripts.benchmark", "--worker", str(rows), str(columns)],
            capture_output=True, text=True, check=True, timeout=300,
        )
        result = json.loads(completed.stdout)
        results.append(result)
        print(json.dumps(result), flush=True)
    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "cpu": platform.processor(), "cases": results,
        "oversize_inputs_rejected": check_limits(),
        "scope": "Sequential synthetic CSV engine runs, not browser/Excel timing or a Windows-clean-install test.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Evidence: {args.output}")


if __name__ == "__main__":
    main()
