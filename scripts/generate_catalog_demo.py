"""Reproducible product-catalog demonstration, using the existing engine only."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date
from html import escape
import json
from pathlib import Path

import pandas as pd

from excel_cleaner.export import export_csv, export_xlsx
from excel_cleaner.io import read_csv
from excel_cleaner.profile import profile_data
from excel_cleaner.transforms import CleaningConfig, CleaningResult, clean


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "demo" / "product_catalog"
COLUMNS = ["sku", "nome", "categoria", "prezzo_eur", "disponibilita", "aggiornato_il", "codice_fornitore", "note"]
SIMILAR_SKUS = ["000010", "000050", "000090", "000130"]


def catalog_rules() -> CleaningConfig:
    """The same title-case setting can be selected for both columns in the UI."""
    return CleaningConfig(
        trim=True, case_columns={"nome": "title", "categoria": "title"},
        number_columns={"prezzo_eur": "it", "disponibilita": "it"},
        date_columns={"aggiornato_il": "%d/%m/%Y"},
        drop_duplicates=True, confirm_duplicates=True,
    )


def source_catalog() -> pd.DataFrame:
    """200 records: 190 invented products, six exact copies, four variants.

    Values are deliberate fixtures, not prices/stock from a real store. Missing
    values, malformed prices and ambiguous dates are intentional examples.
    """
    products = [
        ("Tazza Aurora", "Cucina"), ("Quaderno Orizzonte", "Cartoleria"),
        ("Contenitore Linea", "Casa"), ("Borsa Vela", "Accessori"),
        ("Candela Riva", "Casa"), ("Portapenne Arco", "Cartoleria"),
        ("Borraccia Sentiero", "Tempo libero"), ("Ciotola Brina", "Cucina"),
    ]
    records: list[list[object]] = []
    for number in range(1, 191):
        name, category = products[(number - 1) % len(products)]
        name = f"{name} modello {number:03d}"
        name = name.upper() if number % 2 else name.lower()
        name = "  " + name.replace(" ", "  ") + "  "
        category = f" {category.upper() if number % 3 else category.lower()} "
        cents = 123456 if number == 1 else 1290 + (number * 137) % 42000
        whole, fraction = divmod(cents, 100)
        price = f"{whole:,}".replace(",", ".") + f",{fraction:02d}"
        if number == 1 or number % 11 == 0:
            price = "€ " + price
        price = {18: "da verificare", 88: "12,3,4", 148: "N/D"}.get(number, price)
        if number in {33, 133}:
            price = None
        stock: object = str(number % 31)
        if number in {22, 122}:
            stock = None
        elif number == 62:
            stock = "in arrivo"
        updated: object = date(2026, 2, 1 + (number - 1) % 28).strftime("%d/%m/%Y")
        updated = {45: "31/02/2026", 145: "data da confermare", 95: None}.get(number, updated)
        note = "N/A" if number == 73 else None if number == 175 else "Record sintetico"
        records.append([
            f"{number:06d}", name, None if number == 65 else category,
            price, stock, updated, f"{100 + number % 9:05d}", note,
        ])
    for number in [15, 45, 75, 105, 135, 165]:
        records.append(records[number - 1].copy())
    for sku in SIMILAR_SKUS:
        variant = records[int(sku) - 1].copy()
        variant[1] = " " + str(variant[1]).strip().swapcase() + "   "
        records.append(variant)
    return pd.DataFrame(records, columns=COLUMNS, dtype=object)


def make_summary(source: pd.DataFrame, result: CleaningResult) -> dict:
    profile = profile_data(source)
    sample_skus = ["000001", "000010", "000018", "000033", "000045", "000062", "000088", "000095", "000148", "000175"]
    before = source[source.sku.isin(sample_skus)].drop_duplicates("sku")
    after = result.data[result.data.sku.isin(sample_skus)].drop_duplicates("sku")
    # Only JSON scalar types; keep missing cells explicit, not the string 'None'.
    snapshots = {
        "before": before.to_dict(orient="records"),
        "after": after.to_dict(orient="records"),
    }
    review_examples = []
    for number, column in [(18, "prezzo_eur"), (88, "prezzo_eur"), (148, "prezzo_eur"),
                           (62, "disponibilita"), (45, "aggiornato_il"), (145, "aggiornato_il")]:
        issue = result.issues[(result.issues.row == number + 1) & (result.issues.column == column)].iloc[-1]
        review_examples.append({"sku": f"{number:06d}", "column": column, "value": issue["value"], "issue": issue["issue"]})
    return {
        "synthetic": True, "scenario": "Catalogo prodotti dimostrativo",
        "input_rows": len(source), "output_rows": len(result.data),
        "columns": len(source.columns), "distinct_skus": source.sku.nunique(),
        "exact_duplicates_removed": result.removed_rows,
        "source_possible_duplicate_rows": profile["possible_duplicates"],
        "similar_sku_groups_kept": len(SIMILAR_SKUS),
        "similar_skus": SIMILAR_SKUS,
        "missing_input_cells": int(source.isna().sum().sum()),
        "missing_output_cells": int(result.data.isna().sum().sum()),
        "modified_source_rows_including_removed": result.modified_rows,
        "change_events": len(result.changes), "issue_events": len(result.issues),
        "configuration": asdict(catalog_rules()), "integrity": result.integrity,
        "input_sha256": source.attrs["ingestion"]["sha256"],
        "snapshots": snapshots, "review_examples": review_examples,
    }


def write_portfolio(directory: Path, summary: dict) -> None:
    """Generate a buildless page; embedded data also works with a file:// URL."""
    template = (ROOT / "scripts/templates/catalog_portfolio.html").read_text(encoding="utf-8")
    payload = json.dumps(summary, ensure_ascii=False).replace("<", "\\u003c")
    video = ""
    if (directory / "demo_catalogo.webm").is_file():
        video = ('<section class="section" id="video"><div class="section-heading"><span class="eyebrow">Flusso reale</span>'
                 '<h2>Guarda la dimostrazione.</h2><p>Registrazione automatica del browser, senza audio, tagli o accelerazioni. '
                 'Solo dati sintetici.</p></div><video controls preload="none" '
                 'poster="screenshots/preview.png" src="demo_catalogo.webm">'
                 'Scarica il <a href="demo_catalogo.webm">video WebM</a>.</video></section>')
    page = template.replace("{{DEMO_JSON}}", payload).replace("{{VIDEO_SECTION}}", video)
    for key in ["input_rows", "output_rows", "exact_duplicates_removed", "similar_sku_groups_kept", "distinct_skus"]:
        page = page.replace("{{" + key + "}}", escape(str(summary[key])))
    (directory / "index.html").write_text(page, encoding="utf-8")


def generate(directory: Path = TARGET) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    original_bytes = export_csv(source_catalog())
    (directory / "catalogo_originale.csv").write_bytes(original_bytes)
    source = read_csv(original_bytes, separator=";")
    result = clean(source, catalog_rules())
    summary = make_summary(source, result)
    (directory / "catalogo_pulito.csv").write_bytes(export_csv(result.data))
    (directory / "catalogo_report.xlsx").write_bytes(export_xlsx(result))
    (directory / "rules.json").write_text(json.dumps(summary["configuration"], indent=2), encoding="utf-8")
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_portfolio(directory, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-only", action="store_true", help="Refresh page after adding real screenshots/video.")
    args = parser.parse_args()
    if args.page_only:
        write_portfolio(TARGET, json.loads((TARGET / "summary.json").read_text(encoding="utf-8")))
    else:
        summary = generate()
        print(json.dumps({key: value for key, value in summary.items() if key != "snapshots"}, indent=2, ensure_ascii=False))
    print(f"Synthetic catalog demo: {TARGET}")


if __name__ == "__main__":
    main()
