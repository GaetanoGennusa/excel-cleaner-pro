# Verifica manuale prima di incarichi commerciali

Checklist di accettazione umana: i risultati dell'automazione successiva sono in [FINAL_QA_REPORT.md](FINAL_QA_REPORT.md). Le caselle qui restano da firmare dall'utente: non sono automaticamente spuntate da pytest o dal browser headless. AppTest non dimostra download effettivi o comportamento nativo di Excel.

Versione attuale: tema scuro, verificata il 4–5 novembre 2026 con 49 test pytest, 31 passaggi browser automatici (formato data, animazioni, cambio sorgente, tablet e telefono) e apertura in Microsoft Excel in sola lettura. Dettagli nella prima sezione di [FINAL_QA_REPORT.md](FINAL_QA_REPORT.md). L'automazione non sostituisce le prove qui sotto; usare l'interfaccia attuale.

## Ispezione grafica del report in Excel o LibreOffice (non ancora eseguita)

File: [demo/qa_report.xlsx](../demo/qa_report.xlsx), scaricato dal browser nell'ultima verifica. Aprirlo in Excel o LibreOffice senza abilitare contenuti o macro.

- [ ] Quattro fogli, in quest'ordine: `Cleaned_Data`, `Issues`, `Change_Log`, `Metadata`. Intestazioni in grassetto su fondo verde, riga 1 bloccata, filtro attivo.
- [ ] `Cleaned_Data`: tre righe dati. `A2` mostra `001` (non `1`), allineato come testo. `C2` è il numero `1234,56` o `1234.56`, secondo le impostazioni locali, allineato a destra. `D2` mostra `2025-02-01`. Riga 4: `003`, `Carla Sintetica`, `unknown`, `31/02/2025`, tutti come testo.
- [ ] `Issues`: righe per la data ambigua (riga 2), il duplicato esatto (riga 4), `unknown` (riga 5, amount) e `31/02/2025` (riga 5, date).
- [ ] `Change_Log`: `01/02/2025 → 2025-02-01` alla riga 2, `drop_exact_duplicate` alla riga 4, nessuna riga per la colonna `code`.
- [ ] `Metadata`: `configuration_json` contiene `"date_columns": {"date": "%d/%m/%Y"}`; `removed_rows` vale 1; il timestamp termina con `+00:00`.
- [ ] Colonne leggibili senza `#####`; nessun avviso di collegamenti esterni o macro all'apertura.
- [ ] Formule: esportare `demo/07_untrusted_text.csv` dall'app e aprire il report. In `Cleaned_Data` `=1+1`, `@SUM(A1)` e `+1+2` devono comparire come testo e non come risultati (`2`, `3`).
- [ ] Salvare uno screenshot reale del workbook aperto, con dati sintetici, e annotare programma e versione nella tabella finale.

## Checklist generale

- [ ] Installazione pulita con Python 3.12 su Windows e avvio solo su 127.0.0.1.
- [ ] Aprire demo/10_before.csv, selezionare UTF-8 BOM e `;`, confrontare 4 righe con la sorgente.
- [ ] Selezionare trim, title per name, numero italiano per amount, `%d/%m/%Y` per date; confermare deduplica. Attesi 3 record, codice 001 invariato, importo 1234.56, data 2025-02-01; unknown e 31/02/2025 conservati e segnalati.
- [ ] Confrontare preview e log; provare conferma assente, undo, reset, cambio file/foglio e cancellazione sessione.
- [ ] Scaricare XLSX e CSV, riaprirli e confrontare valori, righe, quattro fogli, log, metadati, accenti e zeri iniziali. Nel CSV usare importazione guidata come testo per i codici.
- [ ] Aprire demo/07_untrusted_text.csv tramite l'app ed esportare: verificare che le formule siano testo e nessun collegamento o contenuto venga eseguito.
- [ ] Provare demo/08_malformed.csv e 09_empty.csv: errore comprensibile, nessun export residuo.
- [ ] Provare upload xlsx multi-foglio, CSV CP1252, celle vuote, intestazioni ripetute e dataset rappresentativo sintetico vicino ai limiti; annotare tempi e memoria sul PC usato.
- [ ] Browser largo e stretto: leggibilità, focus tastiera, nomi lunghi, tabelle e controlli. I controlli Streamlit possono richiedere scorrimento orizzontale su schermi piccoli.
- [ ] Riavvio app e chiusura browser: nessun file caricato creato nella directory del progetto; download gestiti dall'utente.

Registrare data, versioni, PC, browser, programma Excel, risultati e difetti. Per ogni incarico concordare schema, locale, date, criteri duplicati e output atteso; verificare il risultato con il cliente prima della consegna. Non utilizzare dati di clienti nel portfolio.

## Registrazione dell'accettazione

| Informazione | Da compilare |
| --- | --- |
| Data e verificatore | |
| Windows e versione Python | |
| Browser e versione | |
| Excel/LibreOffice e versione | |
| Formato data selezionato e valore nel download | |
| Esito confronto originale / Cleaned_Data / Change_Log | |
| Screenshot autentici del workbook aperto | |
| Problemi o limitazioni da comunicare | |
| Decisione sull'offerta e ambito consentito | |
