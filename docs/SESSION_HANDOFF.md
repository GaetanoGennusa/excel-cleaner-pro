# Punto di ripresa — 2 novembre 2026

Excel Cleaner Pro è implementato e verificato. Risultati dell'ultima revisione: **45 test pytest superati** e **9 scenari reali Chromium/Playwright superati**, inclusi download effettivi e riapertura dell'XLSX con openpyxl. Riferimento completo: `docs/FINAL_QA_REPORT.md`. Portfolio, bozze Fiverr/Upwork, guida, sceneggiatura e screenshot autentici sono salvati nel progetto.

## Stato della sessione

L'app è stata avviata su `http://127.0.0.1:8501` e l'utente l'ha provata nel browser. Il file scaricato `D:\Download\excel_cleaner_report.xlsx` è stato controllato in sola lettura: quattro fogli corretti, quattro righe originali, zero modifiche, nessuna formula eseguibile. Le regole erano disattivate; la sola conferma dei duplicati non ne attiva la rimozione. Il risultato coincideva con la demo originale ricalcolata usando quella configurazione.

## Prossimo argomento concordato nella conversazione

L'utente sta valutando un design più curato per l'interfaccia. Sono state trovate e lette online queste skill, **senza installarle o applicarle**:

- Streamlit `developing-with-streamlit`: https://github.com/streamlit/streamlit/blob/develop/lib/streamlit/.agents/skills/developing-with-streamlit/SKILL.md
- Anthropic `frontend-design`: https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md

La prima è pertinente all'implementazione Streamlit, la seconda alla direzione estetica. Nessun nuovo restyling richiesto o eseguito in questa fase. Non scaricare skill di terzi senza rispettare le istruzioni del progetto e il successivo incarico dell'utente.

## Verifiche ancora aperte

- Scelta del formato data nel browser e confronto col download: motore e AppTest passano, l'automazione del menu data non era affidabile.
- Apertura grafica del report in Excel/LibreOffice.
- Sostituzione diretta di file/impostazioni nella stessa sessione e prova su Windows pulito.
- Verifica completa di usabilità mobile e carico massimo. Il caso da 1.000 righe × 20 colonne è coperto dai test.

Il progetto è presentabile per portfolio con limiti dichiarati; non dichiarato commercialmente pronto. Nessuna pubblicazione o invio a piattaforme effettuato.

## Comandi

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m pytest -q
```

Ambiente virtuale, cache e `outputs/` sono esclusi da Git. I materiali sintetici scelti in `demo/` e le evidenze permanenti in `docs/` fanno parte del salvataggio. Il terminale sandbox ha problemi di avvio (`setup refresh had errors`); le operazioni necessarie sono state eseguite tramite escalation autorizzate, senza installazioni globali.
