"""Streamlit UI; uploads live only in session memory, never in a global cache."""
import hashlib

import pandas as pd
import streamlit as st

from excel_cleaner.config import PREVIEW_ROWS
from excel_cleaner.export import export_csv, export_xlsx
from excel_cleaner.io import InputError, excel_sheets, read_csv, read_excel
from excel_cleaner.profile import profile_data
from excel_cleaner.transforms import CleaningConfig, clean

st.set_page_config(page_title="Excel Cleaner Pro", page_icon="📊", layout="wide")
st.title("Excel Cleaner Pro")
st.caption("Pulizia controllata di Excel e CSV · File elaborati sul tuo computer · Nessuna telemetria")
st.caption("Percorso: carica → controlla i dati → scegli le regole → verifica le modifiche → scarica il report.")


def clear_dataset() -> None:
    for key in ["original", "result", "undo", "source_key", "report", "csv_export", "profile", "loaded_name"]:
        st.session_state.pop(key, None)
    # Rules use dataset-specific widget keys; a new upload starts conservative.
    st.session_state["rules_version"] = st.session_state.get("rules_version", 0) + 1


with st.sidebar:
    st.header("Impostazioni")
    st.caption("10 MB/file · 50.000 righe · 200 colonne · 500.000 celle. XLSX espanso: 80 MB.")
    encoding = st.selectbox("Codifica CSV", ["utf-8-sig", "utf-8", "cp1252", "latin-1", "utf-16"])
    separator_label = st.selectbox("Separatore CSV", ["Punto e virgola ;", "Virgola ,", "Tab", "Barra |"])
    separator = {"Punto e virgola ;": ";", "Virgola ,": ",", "Tab": "\t", "Barra |": "|"}[separator_label]
    st.info("Le impostazioni CSV sono esplicite: una preview errata richiede di cambiare codifica o separatore e ricaricare.")
    st.caption("I file originali restano invariati. Nessuna correzione automatica dei valori dubbi.")
    if st.button("Cancella dati della sessione", use_container_width=True):
        clear_dataset()
        st.session_state["upload_version"] = st.session_state.get("upload_version", 0) + 1
        st.rerun()

st.header("1 · Upload")
uploaded = st.file_uploader("Scegli un file .xlsx o .csv", type=["xlsx", "csv"], key=f"upload_{st.session_state.get('upload_version', 0)}")
sheet = None
source_key = None
if uploaded is not None:
    try:
        raw = uploaded.getvalue()
        if uploaded.name.lower().endswith(".xlsx"):
            sheet = st.selectbox("Foglio Excel", excel_sheets(raw))
        source_key = (hashlib.sha256(raw).hexdigest(), uploaded.name, sheet, encoding, separator)
        if st.session_state.get("source_key") != source_key and "original" in st.session_state:
            clear_dataset()
            st.info("Sorgente o impostazioni cambiate: carica nuovamente il dataset.")
        if st.button("Carica dataset", type="primary"):
            with st.spinner("Lettura e profilazione…"):
                frame = read_excel(raw, sheet) if sheet is not None else read_csv(raw, encoding, separator)
                clear_dataset()
                st.session_state.original = frame
                st.session_state.profile = profile_data(frame)
                st.session_state.source_key = source_key
                st.session_state.loaded_name = uploaded.name
    except (InputError, ValueError) as exc:
        clear_dataset()
        st.error(str(exc))
elif "original" in st.session_state and "source_key" in st.session_state:
    # Removing the upload also removes the parsed copy and exports.
    clear_dataset()

if "original" not in st.session_state:
    st.info("Carica un dataset per visualizzare profilo, regole, anteprima ed esportazioni.")
    st.stop()

original = st.session_state.original
profile = st.session_state.profile
if st.session_state.get("loaded_name"):
    st.text(f"Sorgente attiva: {st.session_state.loaded_name}")
st.header("2 · Data Overview")
metrics = st.columns(5)
for box, label, value in zip(metrics, ["Righe", "Colonne", "Valori nulli", "Duplicati esatti extra", "Possibili duplicati"],
                             [profile["rows"], profile["columns"], profile["nulls"], profile["duplicates"], profile["possible_duplicates"]]):
    box.metric(label, value)
st.caption("Possibili duplicati: righe uguali dopo confronto di spazi e maiuscole/minuscole; non è un confronto fuzzy. Anomalie numeriche: IQR sui valori già numerici. Intestazioni vuote/duplicate ricevono nomi distinti in importazione.")
st.dataframe(original.head(PREVIEW_ROWS), use_container_width=True)
with st.expander("Tipologie delle colonne e anomalie della sorgente"):
    st.dataframe(profile["column_info"], use_container_width=True)
    st.dataframe(profile["issues"].head(1000), use_container_width=True)
    st.caption("Anteprima anomalie limitata a 1.000 elementi; il report Excel include tutte le segnalazioni.")

st.header("3 · Cleaning Rules")
st.caption("Ogni applicazione riparte dalla sorgente. Le date diventano testo ISO YYYY-MM-DD. I valori non validi rimangono e vengono segnalati.")
rules_version = st.session_state.get("rules_version", 0)
with st.form(f"rules_{rules_version}"):
    left, right = st.columns(2)
    trim = left.checkbox("Rimuovi spazi esterni e comprimi spazi interni", value=False)
    headers = right.checkbox("Standardizza intestazioni (minuscole e underscore)", value=False)
    columns = list(original.columns)
    case_cols = st.multiselect("Colonne da normalizzare come testo", columns)
    case_mode = st.selectbox("Maiuscole/minuscole", ["lower", "upper", "title"])
    st.caption("lower: tutto minuscolo · upper: tutto maiuscolo · title: iniziale maiuscola per ogni parola.")
    st.caption("Conversioni per colonna: lascia 'Nessuna' per identificativi e codici. Numeri con zeri iniziali e oltre 15 cifre significative sono protetti.")
    number_columns, date_columns = {}, {}
    with st.expander("Numeri e date: formato esplicito per ogni colonna"):
        for position, column in enumerate(columns):
            a, b = st.columns(2)
            numeric = a.selectbox(f"{column} · numero", ["Nessuna", "Italiano (1.234,56)", "Internazionale (1,234.56)"], key=f"n_{rules_version}_{position}")
            date_format = b.selectbox(f"{column} · data", ["Nessuna", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"], key=f"d_{rules_version}_{position}")
            if numeric != "Nessuna":
                number_columns[column] = "it" if numeric.startswith("Italiano") else "international"
            if date_format != "Nessuna":
                date_columns[column] = date_format
    drop_duplicates = st.checkbox("Rimuovi duplicati esatti presenti nella sorgente", value=False)
    confirmed = st.checkbox("Confermo la rimozione delle copie esatte, mantenendo la prima riga", value=False)
    apply = st.form_submit_button("Applica e mostra anteprima", type="primary")

if apply:
    try:
        with st.status("Applicazione regole e verifiche…", expanded=False) as status:
            candidate = clean(original, CleaningConfig(trim, headers, {c: case_mode for c in case_cols}, number_columns, date_columns, drop_duplicates, confirmed))
            st.session_state.undo = st.session_state.get("result")
            st.session_state.result = candidate
            st.session_state.pop("report", None)
            st.session_state.pop("csv_export", None)
            status.update(label="Pulizia e controlli completati", state="complete")
    except ValueError as exc:
        st.error(str(exc))
        if "result" in st.session_state:
            st.info("Le nuove regole non sono state applicate. È ancora visibile l'ultima versione riuscita, con la sua configurazione.")

st.header("4 · Preview Changes")
controls = st.columns(2)
if controls[0].button("Annulla ultima applicazione", disabled="result" not in st.session_state or "undo" not in st.session_state):
    previous = st.session_state.pop("undo", None)
    if previous is None:
        st.session_state.pop("result", None)
    else:
        st.session_state.result = previous
    st.session_state.pop("report", None)
    st.session_state.pop("csv_export", None)
    st.rerun()
if controls[1].button("Ripristina dati originali"):
    for key in ["result", "undo", "report", "csv_export"]:
        st.session_state.pop(key, None)
    st.rerun()

result = st.session_state.get("result")
if result is None:
    st.info("Scegli le regole e applicale per generare una versione esportabile, anche senza trasformazioni.")
    st.stop()

a, b = st.columns(2)
a.subheader("Prima")
a.dataframe(original.head(PREVIEW_ROWS), use_container_width=True)
b.subheader("Dopo")
b.dataframe(result.data.head(PREVIEW_ROWS), use_container_width=True)
st.caption(f"Preview: prime {PREVIEW_ROWS} righe. Righe con celle modificate: {result.modified_rows} · Righe eliminate: {result.removed_rows} · Eventi di modifica: {len(result.changes)}. Le intestazioni non contano come righe dati modificate.")
st.success("Controlli di integrità superati")
st.json(result.integrity)
with st.expander("Configurazione dell'ultima applicazione riuscita"):
    st.json(result.config)
issues_tab, log_tab = st.tabs(["Anomalie della sorgente e conversioni", "Log operazioni"])
issues_tab.dataframe(result.issues.head(1000), use_container_width=True)
log_tab.dataframe(result.changes.head(1000), use_container_width=True)
st.caption("Riferimenti di riga: posizione nella sorgente, intestazione = 1. Report completi nell'Excel. Modifiche ed eliminazioni sono contate separatamente.")

st.header("5 · Export")
st.warning("Apri solo contenuti attendibili in Excel. XLSX esportato: formule salvate come testo. CSV: apostrofo aggiunto ai testi simili a formula; Excel può comunque reinterpretare date e codici. Preferisci XLSX per gli identificativi.")
if st.button("Prepara esportazioni"):
    st.session_state.csv_export = export_csv(result.data)
    try:
        with st.spinner("Generazione report in memoria…"):
            st.session_state.report = export_xlsx(result)
    except (ValueError, TypeError) as exc:
        st.session_state.pop("report", None)
        st.error(f"Esportazione non riuscita: {exc}")
a, b = st.columns(2)
if "report" in st.session_state:
    a.download_button("Scarica report Excel", st.session_state.report, "excel_cleaner_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
if "csv_export" in st.session_state:
    b.download_button("Scarica dati CSV (UTF-8, ;)", st.session_state.csv_export, "cleaned_data.csv", "text/csv", use_container_width=True)
    st.caption("Excel: Cleaned_Data, Issues, Change_Log e Metadata (timestamp UTC, configurazione e controlli). Il CSV contiene solo i dati.")
