# Punto di ripresa — 8 novembre 2026

## Pubblicazione GitHub: stato corrente

L'utente ha richiesto la pubblicazione del progetto e scelto esplicitamente la visibilità **pubblica**. Repository creato e caricato: [GaetanoGennusa/excel-cleaner-pro](https://github.com/GaetanoGennusa/excel-cleaner-pro), `main`, remoto `origin` configurato con tracking. [Procedura e stato](GITHUB_PUBLICATION.md). Nessuna riscrittura della cronologia o modifica dell'identità autore globale; nessuna licenza aggiunta automaticamente. Git Credential Manager autenticato nell'account indicato; non richiedere credenziali nella chat.

L'utente ha visto la pagina portfolio locale e la ritiene visivamente corretta. Restano distinte le prove manuali dell'app e del report, il secondo Windows e i requisiti di un eventuale cliente. La pubblicazione riguarda il repository, non hosting dell'app o GitHub Pages. Le note precedenti che riportano assenza di autorizzazione alla pubblicazione descrivono lo stato storico antecedente alla richiesta GitHub; non rappresentano un blocco per questa pubblicazione già richiesta.

README aggiornato con screenshot reale, collegamento inglese e distinzione tra sorgenti GitHub e demo locale. Nessuna modifica al codice applicativo in questa fase; restano i 54 test e le evidenze già eseguite.

## Catalogo prodotti: ultima consegna

Demo da 200 righe sintetiche in `demo/product_catalog/`. Aprire `index.html` con doppio clic: pagina portfolio con confronto interattivo, download reali e video muto di 38 secondi. Generatore `scripts/generate_catalog_demo.py`; controllo e registrazione `scripts/catalog_browser_qa.py` / `.cjs`. Il motore e l'app sono invariati. `scripts/browser_qa.cjs` espone i propri helper e avvia il flusso generale solo quando eseguito direttamente.

Risultati: 54 test superati; 4 passaggi catalogo + 5 portfolio, tutti superati; i 31 passaggi generali rieseguiti e superati. Il report browser del catalogo è stato aperto in Excel e i quattro fogli ispezionati tramite catture native. [QA e limiti](CATALOG_DEMO_QA.md), [guida demo](../demo/product_catalog/README.md).

Attenzione ai conteggi: 200 righe iniziali, 190 SKU distinti, 6 copie eliminate, 194 righe finali; quattro coppie simili restano. Le 112 Issues includono segnalazioni della sorgente già risolte. Non interpretarle come 112 errori finali. Non deduplicare nuovamente un output ricaricato senza una decisione: le coppie normalizzate diventano esatte nella nuova sorgente.

Prossimo passo: l'utente esplora la pagina e prova il catalogo nell'app. Restano accettazione manuale, altro Windows e definizione dei requisiti prima di incarichi. Nessuna pubblicazione autorizzata o eseguita. Usare `git log -1` e `git status` per verificare il salvataggio corrente.

## Stato più recente

Sul commit `8bcd956`, completata una nuova verifica autonoma. Modifiche: regole testuali in colonne di pari larghezza; Metadata esportato con testo a capo; script ripetibili `scripts/benchmark.py` e `scripts/excel_visual_qa.ps1`. Report e screenshot sintetici aggiornati. Consultare lo stato Git per le modifiche successive al commit; non assumere che siano già committate.

- 50 test superati dopo le modifiche in un ambiente virtuale ricreato offline sullo stesso PC; 44 dipendenze coerenti, avvio Streamlit riuscito. Il nuovo test controlla la rimozione dei temporanei XLSX nei percorsi provati.
- 31 passaggi browser superati dopo le modifiche, con download verificati.
- Quattro fogli ispezionati dall'agente su catture native di Excel 16.0, inclusa la nuova impaginazione Metadata; testi simili a formule verificati separatamente. Nessuna formula eseguibile, nessun salvataggio delle sorgenti.
- Carico del motore fino a 500.000 celle superato in due forme (50.000 × 10 e 2.500 × 200), con scansione di tutti i fogli esportati; picco massimo osservato 347,8 MiB per worker. Circa un minuto di export per i due casi grandi, senza promessa prestazionale.
- Precisata la privacy: openpyxl scrive XML temporanei locali durante l'export. Eliminati a successo, possono restare dopo un crash. Non dichiarare un'elaborazione esclusivamente in RAM.

Evidenze e limiti: prima sezione di [FINAL_QA_REPORT.md](FINAL_QA_REPORT.md), JSON in `docs/verification-20261108/`, catture native in `demo/screenshots-excel/`. `demo/qa_report.xlsx` è il download corrente del browser. La checklist manuale resta riservata all'utente.

## Prossimi passi

1. Accettazione dell'utente con mouse, tastiera e Excel, usando [MANUAL_QA.md](MANUAL_QA.md).
2. Prova su un altro Windows pulito e nel browser effettivamente usato. Il nuovo venv sullo stesso PC non sostituisce questa prova.
3. Registrare il video di 45–60 secondi seguendo [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md), senza dati personali. La resa nativa del report è ora documentata.
4. Personalizzare le bozze dell'offerta mantenendo ambito e limiti; nessuna pubblicazione autorizzata.

---

# Storico — punto di ripresa del 5 novembre 2026

## Stato attuale

Versione consolidata e salvata con un commit locale (vedi `git log -1`). Interfaccia **scura con accento smeraldo**, scelta dall'utente: `ui/theme.css`, `ui/presentation.py`, `.streamlit/config.toml`. Motore `excel_cleaner/` invariato. Nessuna funzionalità aggiunta in questa fase; nessuna pubblicazione o candidatura.

Ultima verifica, il 4 novembre 2026 tra le 23:00 e le 23:58 Europe/Rome:

- **49 test pytest superati**, 0 falliti.
- **Driver browser riscritto: 31 passaggi**, superati in 3 giri consecutivi più un giro finale. Coprono il formato data scelto nell'interfaccia, animazioni attive e movimento ridotto, cambio di file/separatore/codifica/foglio e rimozione nella stessa pagina, tablet e telefono con flusso completo.
- **Report scaricati verificati con openpyxl e aperti in Microsoft Excel 16.0** in sola lettura.

Dettagli, problemi corretti e limiti: [FINAL_QA_REPORT.md](FINAL_QA_REPORT.md), prima sezione.

Correzioni di questa fase:

- **Driver browser**: i menu venivano chiusi da uno scorrimento subito dopo l'apertura quando il controllo era al bordo della finestra. Non è un difetto del motore.
- **Etichette delle caselle**: non sono più troncate su schermi stretti, con un controllo di regressione nel driver.

## Da fare, in ordine

1. Ispezione grafica di `demo/qa_report.xlsx` in Excel con la checklist di [MANUAL_QA.md](MANUAL_QA.md). L'apertura automatica in Excel è stata fatta, l'ispezione visiva no.
2. Prova manuale con mouse e tastiera nel browser usato davvero; poi Firefox o Edge e un telefono reale.
3. Installazione su un Windows pulito e prova con un dataset sintetico vicino ai limiti.
4. Solo dopo: personalizzare le bozze Fiverr/Upwork, che restano non pubblicate.

## Comandi

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.browser_qa
```

Il terzo comando richiede Node, Playwright e Chromium già installati (vedi [BROWSER_QA.md](BROWSER_QA.md)) e la porta 8521 libera. Ambiente virtuale, cache e `outputs/` sono esclusi da Git.

---

# Storico delle sessioni precedenti

Le sezioni seguenti descrivono stati passati e non rappresentano la versione attuale.

## 4 novembre 2026, sera — tema scuro e design premium

Design premium e responsive, poi tema scuro rifinito osservando siti professionali (solo principi, nessun marchio). Note e verifiche di allora in [UI_REDESIGN.md](UI_REDESIGN.md).

## 4 novembre 2026 — restyling chiaro

L'utente ha scelto e ricevuto il restyling **dashboard chiara e professionale, verde petrolio**. Implementato in `app.py`, `.streamlit/config.toml` e `ui/presentation.py`: schede, indicatore delle fasi, ancore reali di navigazione, riepiloghi e avviso di export originale senza regole. Nessuna skill di terzi installata. Motore invariato.

Verifiche attuali: **46 test pytest e 10 scenari browser passati**, zero richieste di risorse esterne nel giro conclusivo. Consultare `docs/UI_REDESIGN.md`. Screenshot aggiornati in `demo/screenshots-redesign/`; report reale del browser in `demo/ui_report.xlsx`. La versione minima Streamlit è ora 1.66, già presente nel runtime/lock verificato. Le verifiche manuali ancora aperte rimangono esplicite nel rapporto.

## Storico della sessione del 2 novembre

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
