# Verifica manuale prima di incarichi commerciali

Checklist di accettazione umana: i risultati dell'automazione successiva sono in [FINAL_QA_REPORT.md](FINAL_QA_REPORT.md). Le caselle qui restano da firmare dall'utente: non sono automaticamente spuntate da pytest o dal browser headless. AppTest non dimostra download effettivi o comportamento nativo di Excel.

Versione attuale: tema scuro, verificata l'8 novembre 2026 con 50 test pytest, 31 passaggi browser automatici (formato data, animazioni, cambio sorgente, tablet e telefono) e ispezione di catture native in Microsoft Excel. Dettagli nella prima sezione di [FINAL_QA_REPORT.md](FINAL_QA_REPORT.md). L'automazione non sostituisce le prove qui sotto; usare l'interfaccia attuale.

## Ispezione grafica del report in Excel o LibreOffice

**Aggiornamento 8 novembre 2026:** l'agente ha ispezionato catture reali dei quattro fogli in Excel 16.0 e dei testi simili a formule: [evidenze](../demo/screenshots-excel/README.md). Il nuovo ambiente virtuale sullo stesso PC supera 50 test e l'avvio locale. Queste prove non costituiscono accettazione umana né installazione su un altro Windows. Le caselle qui sotto restano riservate alla verifica dell'utente.

File: [demo/qa_report.xlsx](../demo/qa_report.xlsx), scaricato dal browser nell'ultima verifica. Aprirlo in Excel o LibreOffice senza abilitare contenuti o macro.

- [x] Quattro fogli, in quest'ordine: `Cleaned_Data`, `Issues`, `Change_Log`, `Metadata`. Intestazioni in grassetto su fondo verde, riga 1 bloccata, filtro attivo.
- [x] `Cleaned_Data`: tre righe dati. `A2` mostra `001` (non `1`), allineato come testo. `C2` è il numero `1234,56` o `1234.56`, secondo le impostazioni locali, allineato a destra. `D2` mostra `2025-02-01`. Riga 4: `003`, `Carla Sintetica`, `unknown`, `31/02/2025`, tutti come testo.
- [x] `Issues`: righe per la data ambigua (riga 2), il duplicato esatto (riga 4), `unknown` (riga 5, amount) e `31/02/2025` (riga 5, date).
- [x] `Change_Log`: `01/02/2025 → 2025-02-01` alla riga 2, `drop_exact_duplicate` alla riga 4, nessuna riga per la colonna `code`.
- [x] `Metadata`: `configuration_json` contiene `"date_columns": {"date": "%d/%m/%Y"}`; `removed_rows` vale 1; il timestamp termina con `+00:00`.
- [x] Colonne leggibili senza `#####`; nessun avviso di collegamenti esterni o macro all'apertura.
- [x] Formule: esportare `demo/07_untrusted_text.csv` dall'app e aprire il report. In `Cleaned_Data` `=1+1`, `@SUM(A1)` e `+1+2` devono comparire come testo e non come risultati (`2`, `3`).
- [ ] Salvare uno screenshot reale del workbook aperto, con dati sintetici, e annotare programma e versione nella tabella finale.

## Checklist generale

- [ ] Installazione pulita con Python 3.12 su Windows e avvio solo su 127.0.0.1.
- [x] Aprire demo/10_before.csv, selezionare UTF-8 BOM e `;`, confrontare 4 righe con la sorgente.
- [x] Selezionare trim, title per name, numero italiano per amount, `%d/%m/%Y` per date; confermare deduplica. Attesi 3 record, codice 001 invariato, importo 1234.56, data 2025-02-01; unknown e 31/02/2025 conservati e segnalati.
- [ ] Confrontare preview e log; provare conferma assente, undo, reset, cambio file/foglio e cancellazione sessione.
- [ ] Scaricare XLSX e CSV, riaprirli e confrontare valori, righe, quattro fogli, log, metadati, accenti e zeri iniziali. Nel CSV usare importazione guidata come testo per i codici.
- [x] Aprire demo/07_untrusted_text.csv tramite l'app ed esportare: verificare che le formule siano testo e nessun collegamento o contenuto venga eseguito.
- [x] Provare demo/08_malformed.csv e 09_empty.csv: errore comprensibile, nessun export residuo.
- [ ] Provare upload xlsx multi-foglio, CSV CP1252, celle vuote, intestazioni ripetute e dataset rappresentativo sintetico vicino ai limiti; annotare tempi e memoria sul PC usato.
- [ ] Browser largo e stretto: leggibilità, focus tastiera, nomi lunghi, tabelle e controlli. I controlli Streamlit possono richiedere scorrimento orizzontale su schermi piccoli.
- [ ] Riavvio app e chiusura browser: originali non salvati nella directory del progetto; download gestiti dall'utente. Verificare i temporanei locali dell'export XLSX; la rimozione dopo crash non è garantita e non costituisce cancellazione forense.

Registrare data, versioni, PC, browser, programma Excel, risultati e difetti. Per ogni incarico concordare schema, locale, date, criteri duplicati e output atteso; verificare il risultato con il cliente prima della consegna. Non utilizzare dati di clienti nel portfolio.

## Registrazione dell'accettazione

| Informazione | Da compilare |
| --- | --- |
| Data e verificatore | 10 novembre 2026, autore del progetto, guidato passo per passo da Claude Code |
| Windows e versione Python | Windows 11 Home 10.0.26200, Python 3.12.14 (`.venv` del progetto) |
| Browser e versione | Browser integrato di VS Code su `http://127.0.0.1:8501`; versione non annotata. Firefox, Edge, Chrome e telefono reale non provati |
| Excel/LibreOffice e versione | Microsoft Excel desktop, interfaccia italiana; versione esatta non annotata |
| Formato data selezionato e valore nel download | `%d/%m/%Y`; `01/02/2025` → `2025-02-01` in `Cleaned_Data`, `configuration_json` coerente |
| Esito confronto originale / Cleaned_Data / Change_Log | Superato: 4 righe → 3, `001` testo, `1234,56` numero, `unknown` e `31/02/2025` conservati e segnalati; 12 eventi in Change_Log, nessuno su `code`; `removed_rows` = 1, timestamp `+00:00` |
| Screenshot autentici del workbook aperto | Catturati dall'utente durante la sessione e inviati nella conversazione; non salvati nel repository |
| Problemi o limitazioni da comunicare | Nessun errore sui dati. Sette osservazioni di chiarezza, corrette nella stessa giornata: vedi sezione seguente |
| Decisione sull'offerta e ambito consentito | Da decidere dall'utente dopo il ricontrollo rapido delle correzioni |

## Esito del collaudo manuale del 10 novembre 2026

Prove eseguite dall'utente con mouse e tastiera, sulla versione del commit `c650cd3`:

- Caricamento di `demo/10_before.csv` (UTF-8 BOM, `;`): 4 righe, 4 colonne, 0 nulli, 1 duplicato esatto, `001` conservato.
- Regole: spazi, `title` su `name`, numeri italiani su `amount`, `%d/%m/%Y` su `date`, deduplica confermata. Anteprima con 3 righe e anomalie alle righe 2, 4 e 5.
- Senza conferma l'app rifiuta di applicare le regole e mantiene l'ultima versione riuscita.
- Report Excel scaricato e aperto: quattro fogli controllati uno per uno.
- `demo/07_untrusted_text.csv`: `=1+1`, `@SUM(A1)`, `+1+2` restano testo in Excel (Visualizzazione protetta attiva).
- `demo/08_malformed.csv` e `demo/09_empty.csv`: rifiutati, avanzamento riportato al passo 1, nessun download.

Osservazioni emerse e correzioni applicate lo stesso giorno (verificate con test automatici, da ricontrollare brevemente nel browser):

1. Titoli di sezione in inglese → ora «Carica il file», «Panoramica dati», «Regole di pulizia», «Anteprima modifiche», «Esporta»; segnaposto del menu colonne in italiano.
2. Conflitto numero/data senza nome di colonna → il messaggio indica la colonna.
3. Messaggi data in inglese della libreria Python → «Data inesistente: giorno o mese fuori intervallo» e «La data non corrisponde al formato scelto».
4. Dopo un errore il riquadro restava su «Applicazione regole e verifiche…» → ora diventa rosso con «Regole non applicate».
5. File vuoto con messaggio generico → «Il file è vuoto».
6. `Issues` non distingueva problemi risolti e aperti → nuove colonne `status` (Risolto / Da verificare / Protetto) e `note`; conteggio visibile anche nell'anteprima.
7. `Metadata` solo tecnico e in inglese → nuova prima riga `riepilogo` in italiano; le righe tecniche restano invariate.

Non ancora provati: XLSX multi-foglio, CSV CP1252, dataset vicino ai limiti, browser stretto e telefono, sola tastiera, riavvio dell'app, altro PC Windows.
