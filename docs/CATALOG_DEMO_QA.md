# Demo catalogo prodotti — verifica dell'8 novembre 2026

## Ambito

Nuovo caso da portfolio basato esclusivamente sulle funzioni già presenti. Nessuna modifica al motore, alle regole o all'interfaccia Streamlit. Pagina HTML locale separata in `demo/product_catalog/index.html`, costruita dal generatore Python usando dati derivati dall'esecuzione. Niente hosting, API esterne o download di nuove dipendenze.

Fonte: 200 record interamente sintetici, 8 colonne, 190 SKU distinti. Sei copie esatte eliminate con conferma; quattro coppie soltanto simili conservate. Risultato: 194 righe, sette celle vuote conservate. I valori non convertibili restano presenti. Il log contiene 1.392 eventi e Issues 112 segnalazioni della sorgente/conversioni; non è il conteggio degli errori irrisolti.

## Risultati eseguiti

| Comando o controllo | Esito |
| --- | --- |
| `.\.venv\Scripts\python.exe -m scripts.generate_catalog_demo` | Artefatti generati, conteggi e regole in summary.json e rules.json |
| pytest mirato su `tests/test_catalog_demo.py` | 4 superati |
| `.\.venv\Scripts\python.exe -m pytest -q` | **54 superati in 10,64 s, 0 falliti** |
| `.\.venv\Scripts\python.exe -m scripts.catalog_browser_qa` | **4 passaggi app e 5 passaggi portfolio superati**; 0 errori pagina, 0 richieste esterne |
| `.\.venv\Scripts\python.exe -m scripts.browser_qa` | **31 passaggi generali superati** dopo la modifica di riuso degli helper |
| Download effettivi | Tutti i dati e configurazione del report app confrontati con il risultato del motore; CSV identico al CSV consegnato; file della pagina confrontati byte per byte con quelli presenti |
| Registrazione | WebM, 38,00 s, 1440 × 1000; riproduzione nel browser verificata; quattro fotogrammi a 5/15/25/35 s ispezionati |
| Pagina | Confronto Prima/Dopo/Valori da verificare, navigazione radio da tastiera, download, lettore video, larghezza 390 px senza overflow di pagina, apertura file:// senza server |
| Excel nativo | Report browser aperto read-only in Excel 16.0 build 20527, macro disattivate; 4 fogli, zero formule, filtri, header e blocco righe presenti; catture native ispezionate |

Evidenze: [app](catalog-demo/app_browser_results.json), [pagina](catalog-demo/portfolio_browser_results.json), [download](catalog-demo/artifact_validation.json), [regressione generale](catalog-demo/general_browser_results.json), [Excel](catalog-demo/excel_result.json). Screenshot reali in `demo/product_catalog/screenshots/`; primi intervalli e intestazioni dei quattro fogli sono visibili nelle catture native. Non tutte le 194 righe o i 1.392 eventi sono visualizzati negli screenshot: il confronto automatizzato copre i dati e il conteggio del log.

## Provenienza

- `catalogo_originale.csv`, `catalogo_pulito.csv`, `catalogo_report.xlsx`: prodotti dal generatore che usa il motore Python. Report con timestamp della relativa esecuzione.
- `catalogo_report_browser.xlsx`: effettivamente scaricato dall'app Streamlit durante il giro `catalog-qa-20261108T151223461709Z`; confrontato con l'output atteso e ispezionato in Excel.
- `demo_catalogo.webm`: registrazione dello stesso giro. Nessun montaggio, voce fuori campo o accelerazione. Le attese aggiunte alla registrazione servono alla leggibilità, non alle condizioni di successo dei controlli.
- `screenshots/overview.png`, `preview.png`, `issues.png`, `export.png`: catture dell'app reale, senza ritocchi.
- `screenshots/portfolio_desktop.png`, `portfolio_mobile.png`: pagina locale reale in Chromium. La pagina visualizza campioni precomputati, non esegue una pulizia quando si seleziona Dopo.
- `screenshots/excel_*.png`: catture della sola istanza Excel dedicata, chiusa senza salvare; sorgente invariata.

Il primo tentativo di estrazione dei fotogrammi con il filtro `fps` non era supportato dall'encoder FFmpeg già installato. L'estrazione è riuscita usando quattro posizioni temporali esplicite; il video originale non è stato modificato. La riproduzione del video era già superata nel browser.

## Cosa dimostrano i test aggiunti

Valori originali e regole predefinite conservati; originali non mutati; codici e nulli protetti; rimozione delle sole sei copie fonte alle righe 192–197; conservazione delle quattro coppie simili; valori non validi mantenuti e segnalati. I file consegnati e i dati della pagina concordano con i risultati.

L'app riparte dalla sorgente originale a ogni applicazione. Ripetere la pulizia sulla stessa sorgente dà lo stesso risultato. Le conversioni sono idempotenti quando ripetute senza autorizzare nuove eliminazioni. Ricaricare l'output come nuova sorgente e attivare la deduplica cambierebbe l'insieme delle righe eliminabili: non viene presentato come comportamento idempotente della deduplica.

## Limiti e accettazione

Nessun controllo commerciale sull'unicità SKU, correttezza dei prezzi o scorte, fiscalità, varianti o compatibilità con uno specifico negozio online. La conversione dei decimali usa float e il cambio di maiuscole nei nomi reali richiede accordo. Gli esempi sono inventati, non risultati di clienti. Nessuna promessa di tempo risparmiato, guadagno o accuratezza universale.

Chrome headless a 390 px non equivale a un telefono reale. La nuova pagina non è stata verificata su Firefox, Safari o un secondo Windows. Il video è WebM senza audio; non è stato convertito o provato su piattaforme di annunci. L'accettazione dell'utente resta da registrare in `docs/MANUAL_QA.md`. L'export XLSX usa temporanei locali: possibile residuo dopo crash, come documentato.

La pagina e i file sono salvati localmente. Nessun sito pubblicato, annuncio inviato o cliente contattato.
