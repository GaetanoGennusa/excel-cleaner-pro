"""Session workspace; XLSX export uses short-lived local writer files."""
import hashlib

import streamlit as st

from excel_cleaner.config import PREVIEW_ROWS
from excel_cleaner.export import export_csv, export_xlsx
from excel_cleaner.io import InputError, excel_sheets, read_csv, read_excel
from excel_cleaner.profile import profile_data
from excel_cleaner.review import PROTECTED, RESOLVED, TO_CHECK, status_counts
from excel_cleaner.transforms import CleaningConfig, clean
from ui.presentation import (apply_design, brand, file_badge, hero_badge, hero_chips, hero_demo, hero_lede, integrity_summary,
                             rule_count, tag, workflow)

st.set_page_config(page_title="Excel Cleaner Pro", page_icon="📊", layout="wide")
apply_design()
with st.container(key="hero"):
    hero_text, hero_side = st.columns([1.35, 1], gap="large", vertical_alignment="center")
    with hero_text:
        hero_badge()
        st.title("Excel Cleaner Pro", anchor=False)
        hero_lede()
        hero_chips()
    with hero_side, st.container(key="hero_side"):
        hero_demo()
with st.container(key="workflow_bar"):
    workflow_slot = st.empty()


def clear_dataset() -> None:
    for key in ["original", "result", "undo", "source_key", "report", "csv_export", "profile", "loaded_name"]:
        st.session_state.pop(key, None)
    st.session_state["rules_version"] = st.session_state.get("rules_version", 0) + 1


with st.sidebar:
    brand()
    with st.container(key="sidebar_nav"):
        navigation_slot = st.empty()
    st.subheader("Impostazioni CSV")
    encoding = st.selectbox("Codifica CSV", ["utf-8-sig", "utf-8", "cp1252", "latin-1", "utf-16"])
    separator_label = st.selectbox("Separatore CSV", ["Punto e virgola ;", "Virgola ,", "Tab", "Barra |"])
    separator = {"Punto e virgola ;": ";", "Virgola ,": ",", "Tab": "\t", "Barra |": "|"}[separator_label]
    st.caption("Accenti o colonne errati? Cambia queste impostazioni e carica di nuovo il dataset.")
    with st.expander("Limiti e privacy"):
        st.caption("10 MB/file · 50.000 righe · 200 colonne · 500.000 celle. XLSX espanso: 80 MB.")
        st.write("Gli originali restano nella sessione, senza servizi esterni o telemetria. L'export XLSX usa temporanei locali, rimossi a esportazione riuscita; un arresto anomalo può lasciarne residui.")
    st.divider()
    if st.button("Cancella dati della sessione", width="stretch"):
        clear_dataset()
        st.session_state["upload_version"] = st.session_state.get("upload_version", 0) + 1
        st.rerun()


def update_navigation() -> None:
    links = ["[Carica file](#upload)"]
    if "original" in st.session_state:
        links += ["[Panoramica dati](#overview)", "[Regole di pulizia](#rules)", "[Confronta risultati](#preview)"]
    if "result" in st.session_state:
        links.append("[Scarica report](#export)")
    navigation_slot.markdown("**Il tuo percorso**\n\n" + "\n\n".join(links) + "\n\n---")


with st.container(border=True, key="upload_card"):
    st.header("1 · Carica il file", anchor="upload")
    st.caption("Parti da un file: scegli la sorgente e controlla il contenuto prima di modificarlo.")
    upload_area, guide_area = st.columns([1.7, 1], gap="large")
    with guide_area, st.container(key="upload_guide"):
        st.subheader("Una pulizia trasparente")
        st.markdown("1. **Carica** un Excel o CSV.\n2. **Scegli** le trasformazioni.\n3. **Controlla e scarica** il report.")
        st.caption("Nessun valore inventato. Le righe dubbie restano visibili.")
    with upload_area:
        uploaded = st.file_uploader("Scegli un file .xlsx o .csv", type=["xlsx", "csv"], key=f"upload_{st.session_state.get('upload_version', 0)}")
        st.caption("Massimo 10 MB · Prima riga usata come intestazione")
        sheet = None
        if uploaded is not None:
            try:
                raw = uploaded.getvalue()
                if uploaded.name.lower().endswith(".xlsx"):
                    sheet = st.selectbox("Foglio Excel", excel_sheets(raw))
                source_key = (hashlib.sha256(raw).hexdigest(), uploaded.name, sheet, encoding, separator)
                if st.session_state.get("source_key") != source_key and "original" in st.session_state:
                    clear_dataset()
                    st.info("Sorgente o impostazioni cambiate: carica nuovamente il dataset.")
                if st.button("Carica dataset", type="primary", width="stretch"):
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
            clear_dataset()

update_navigation()
if "original" not in st.session_state:
    workflow_slot.html(workflow(0))
    st.info("Carica un dataset per visualizzare profilo, regole, anteprima ed esportazioni.")
    st.stop()

original = st.session_state.original
profile = st.session_state.profile
with st.container(border=True, key="overview_card"):
    st.header("2 · Panoramica dati", anchor="overview")
    if st.session_state.get("loaded_name"):
        st.text(f"Sorgente attiva: {st.session_state.loaded_name}")
    metrics = st.container(key="overview_metrics").columns(5)
    for box, label, value in zip(metrics, ["Righe", "Colonne", "Valori nulli", "Duplicati esatti extra", "Possibili duplicati"],
                                 [profile["rows"], profile["columns"], profile["nulls"], profile["duplicates"], profile["possible_duplicates"]]):
        box.metric(label, value, border=True)
    st.caption(f"Anteprima della sorgente · prime {PREVIEW_ROWS} righe")
    st.dataframe(original.head(PREVIEW_ROWS), width="stretch")
    with st.expander("Tipologie delle colonne e anomalie della sorgente"):
        st.dataframe(profile["column_info"], width="stretch")
        st.dataframe(profile["issues"].head(1000), width="stretch")
        st.caption("Possibili duplicati: confronto di tutte le colonne dopo normalizzazione spazi/case. Outlier IQR: solo segnalazioni sui valori numerici. Preview anomalie: massimo 1.000; report completo nell'Excel.")
    st.caption("Intestazioni vuote o duplicate ricevono nomi distinti, con mappatura nel report.")

with st.container(border=True, key="rules_card"):
    st.header("3 · Regole di pulizia", anchor="rules")
    st.caption("Attiva soltanto le regole che ti servono. Ogni applicazione riparte dalla sorgente.")
    rules_version = st.session_state.get("rules_version", 0)
    with st.form(f"rules_{rules_version}", border=False):
        text_panel = st.container(key="rules_text")
        text_panel.subheader("Testi e intestazioni")
        left, right = text_panel.columns(2)
        trim = left.checkbox("Rimuovi spazi esterni e comprimi spazi interni", value=False)
        headers = right.checkbox("Standardizza intestazioni (minuscole e underscore)", value=False)
        columns = list(original.columns)
        a, b = text_panel.columns(2)
        case_cols = a.multiselect("Colonne da normalizzare come testo", columns, placeholder="Scegli una o più colonne")
        case_mode = b.selectbox("Maiuscole/minuscole", ["lower", "upper", "title"])
        text_panel.caption("lower: minuscolo · upper: maiuscolo · title: iniziale maiuscola per ogni parola.")
        number_columns, date_columns = {}, {}
        formats_panel = st.container(key="rules_formats")
        formats_panel.subheader("Numeri e date")
        with formats_panel.expander("Numeri e date: formato esplicito per ogni colonna"):
            st.caption("Lascia 'Nessuna' per codici e CAP. Esempio italiano: 1.234,56. Date: %d/%m/%Y = 31/12/2025, %m/%d/%Y = 12/31/2025. Le date convertite diventano YYYY-MM-DD.")
            for position, column in enumerate(columns):
                a, b = st.columns(2)
                numeric = a.selectbox(f"{column} · numero", ["Nessuna", "Italiano (1.234,56)", "Internazionale (1,234.56)"], key=f"n_{rules_version}_{position}")
                date_format = b.selectbox(f"{column} · data", ["Nessuna", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"], key=f"d_{rules_version}_{position}")
                if numeric != "Nessuna":
                    number_columns[column] = "it" if numeric.startswith("Italiano") else "international"
                if date_format != "Nessuna":
                    date_columns[column] = date_format
            st.caption("Zeri iniziali e numeri oltre 15 cifre significative sono protetti. Valori non validi conservati e segnalati.")
        dupes_panel = st.container(key="rules_dupes")
        dupes_panel.subheader("Duplicati esatti")
        drop_duplicates = dupes_panel.checkbox("Rimuovi duplicati esatti presenti nella sorgente", value=False)
        confirmed = dupes_panel.checkbox("Confermo la rimozione delle copie esatte, mantenendo la prima riga", value=False)
        dupes_panel.caption("Per rimuovere le copie servono entrambe le selezioni. La sola conferma non attiva la rimozione. Le righe soltanto simili vengono conservate.")
        apply = st.form_submit_button("Applica e mostra anteprima", type="primary", width="stretch")
    if apply:
        try:
            with st.status("Applicazione regole e verifiche…", expanded=False) as status:
                try:
                    candidate = clean(original, CleaningConfig(trim, headers, {c: case_mode for c in case_cols}, number_columns, date_columns, drop_duplicates, confirmed))
                except ValueError:
                    status.update(label="Regole non applicate: correggi l'impostazione indicata qui sotto", state="error")
                    raise
                st.session_state.undo = st.session_state.get("result")
                st.session_state.result = candidate
                st.session_state.pop("report", None)
                st.session_state.pop("csv_export", None)
                status.update(label="Pulizia e controlli completati", state="complete")
        except ValueError as exc:
            st.error(str(exc))
            if "result" in st.session_state:
                st.info("Le nuove regole non sono state applicate. È ancora visibile l'ultima versione riuscita, con la sua configurazione.")

with st.container(border=True, key="preview_card"):
    st.header("4 · Anteprima modifiche", anchor="preview")
    controls = st.container(horizontal=True, key="preview_actions")
    if controls.button("Annulla ultima applicazione", disabled="result" not in st.session_state or "undo" not in st.session_state):
        previous = st.session_state.pop("undo", None)
        if previous is None:
            st.session_state.pop("result", None)
        else:
            st.session_state.result = previous
        st.session_state.pop("report", None)
        st.session_state.pop("csv_export", None)
        st.rerun()
    if controls.button("Ripristina dati originali"):
        for key in ["result", "undo", "report", "csv_export"]:
            st.session_state.pop(key, None)
        st.rerun()
    result = st.session_state.get("result")
    workflow_slot.html(workflow(3 if result is not None else 2))
    update_navigation()
    if result is None:
        st.info("Scegli le regole e applicale per generare una versione esportabile, anche senza trasformazioni.")
        st.stop()
    selected_rules = rule_count(result.config)
    if selected_rules == 0:
        st.info("Nessuna trasformazione selezionata: stai esportando i dati originali. Per pulirli, attiva le regole qui sopra e premi Applica e mostra anteprima.")
    else:
        st.caption(f"Regole selezionate nell'ultima applicazione: {selected_rules}. Controlla le modifiche effettive e gli eventuali valori rimasti invariati.")
    a, b, c = st.container(key="preview_metrics").columns(3)
    a.metric("Righe con celle modificate", result.modified_rows, border=True)
    b.metric("Duplicati rimossi", result.removed_rows, border=True)
    c.metric("Righe in uscita", len(result.data), border=True)
    a, b = st.container(key="compare").columns(2, gap="medium")
    with a:
        tag("Prima")
    a.dataframe(original.head(PREVIEW_ROWS), width="stretch")
    with b:
        tag("Dopo", after=True)
    b.dataframe(result.data.head(PREVIEW_ROWS), width="stretch")
    st.caption(f"Prime {PREVIEW_ROWS} righe · {len(result.changes)} eventi di modifica. Le intestazioni non contano come righe dati modificate; righe modificate ed eliminate sono contate separatamente.")
    integrity_summary(result.integrity)
    counts = status_counts(result.issues)
    st.caption(f"Segnalazioni: {counts[TO_CHECK]} da verificare · {counts[RESOLVED]} risolte dalle regole · {counts[PROTECTED]} protette all'esportazione.")
    issues_tab, log_tab = st.tabs(["Anomalie della sorgente e conversioni", "Log operazioni"])
    issues_tab.dataframe(result.issues.head(1000), width="stretch")
    log_tab.dataframe(result.changes.head(1000), width="stretch")
    st.caption("Righe riferite alla sorgente, intestazione = 1. Preview limitata a 1.000 eventi; report completi nell'Excel.")
    with st.expander("Dettagli tecnici e configurazione"):
        st.json(result.integrity)
        st.json(result.config)

with st.container(border=True, key="export_card"):
    st.header("5 · Esporta", anchor="export")
    st.write("Porta con te i dati puliti e la traccia di ogni scelta.")
    if st.button("Prepara esportazioni", type="primary"):
        st.session_state.csv_export = export_csv(result.data)
        try:
            with st.spinner("Generazione report…"):
                st.session_state.report = export_xlsx(result)
        except (ValueError, TypeError) as exc:
            st.session_state.pop("report", None)
            st.error(f"Esportazione non riuscita: {exc}")
    a, b = st.container(key="export_options").columns(2, gap="medium")
    with a, st.container(key="export_xlsx"):
        file_badge("xlsx")
        st.markdown("**Report Excel**\n\nDati puliti, segnalazioni con il loro stato, log delle modifiche e metadati con riepilogo in italiano, in quattro fogli. Consigliato per conservare codici e zeri iniziali.")
        if "report" in st.session_state:
            st.download_button("Scarica report Excel", st.session_state.report, "excel_cleaner_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
        else:
            st.caption("Premi Prepara esportazioni per generare il file.")
    with b, st.container(key="export_csv"):
        file_badge("csv")
        st.markdown("**Dati CSV**\n\nSolo la tabella finale, UTF-8 con BOM e separatore `;`. Da importare con il formato delle colonne corretto.")
        if "csv_export" in st.session_state:
            st.download_button("Scarica dati CSV (UTF-8, ;)", st.session_state.csv_export, "cleaned_data.csv", "text/csv", width="stretch")
            workflow_slot.html(workflow(4))
        else:
            st.caption("Premi Prepara esportazioni per generare il file.")
    with st.expander("Aprire i file in modo sicuro"):
        st.write("Apri solo contenuti attendibili in Excel. L'XLSX salva le formule come testo; il CSV aggiunge un apostrofo ai testi simili a formula. Excel può reinterpretare date e codici nei CSV: preferisci XLSX per gli identificativi.")
    st.caption("Il report include Cleaned_Data, Issues, Change_Log e Metadata, con timestamp UTC, configurazione e verifiche effettuate.")

with st.container(key="workspace_footer"):
    st.caption("Elaborazione locale · Nessuna telemetria · Cancella la sessione quando hai terminato")
