# Verifica facoltativa con browser reale

Lo script avvia Streamlit su `127.0.0.1:8521`, usa un Chromium **headless reale** con Playwright, carica solo fixture sintetiche e salva screenshot, download, log e un riepilogo JSON in una nuova directory `outputs/browser-qa-<timestamp UTC>/`. Non invia documenti a Internet; le richieste browser verso host diversi da localhost sono bloccate. Server e browser vengono arrestati al termine della prova.

```powershell
.\.venv\Scripts\python.exe -m scripts.browser_qa
```

Node, il pacchetto Node Playwright e Chromium devono essere già installati. Lo script non li installa e non modifica il runtime condiviso. Su questo PC trova il runtime Codex e il browser nella cache esistente; non è una dipendenza dell'applicazione. Se necessario, impostare percorsi reali di installazioni già disponibili:

```powershell
$env:ECP_NODE = 'C:\percorso\node.exe'
$env:ECP_PLAYWRIGHT = 'C:\percorso\node_modules\playwright'
$env:ECP_CHROMIUM = 'C:\percorso\chrome.exe'
.\.venv\Scripts\python.exe -m scripts.browser_qa
```

Se mancano, usare la checklist manuale invece di dichiarare il browser test superato. Questi percorsi sono esempi da sostituire, non eseguibili forniti dal progetto. La porta 8521 deve essere libera.

I controlli comprendono upload CSV e XLSX multi-foglio, profilazione, regole esplicite, conferma duplicati, anteprima, veri eventi di download XLSX/CSV, annullamento, ripristino, file non validi e dimensione upload, viewport stretta. Il driver Python riapre l'XLSX realmente scaricato con openpyxl e confronta dati, fogli, identificativi e assenza di formule; verifica anche il CSV scaricato.

Le interazioni usano i controlli effettivi della pagina, senza inserire risultati nello stato Streamlit. I menu di questa versione Streamlit sono combobox ricercabili: il test digita, apre con ArrowDown e conferma con Enter. L'upload non è simulato come nell'AppTest.

Lo scenario corrente applica spazi, case, numeri italiani e deduplica confermata; **non applica conversioni data**. Verifica che `01/02/2025` resti invariata perché la regola non è selezionata. La selezione del formato data non è stata affidabile nell'automazione della combinazione browser/controlli installata: è coperta da un test AppTest dedicato e deve essere provata manualmente nel browser. Il caso XLSX cambia realmente foglio e verifica lo schema risultante. Ogni nuova sorgente è caricata in una sessione fresca; l'invalidazione mediante sostituzione diretta del file senza ricaricare la pagina resta una verifica manuale. Il caso stretto verifica soltanto la schermata iniziale a 390 px, non l'intero flusso su un telefono.

Su errore vengono salvati `failure.png`, `failure.txt` e una diagnosi dei controlli; i passaggi elencati in `browser_results.json` sono solo quelli effettivamente completati. Un esito parziale non certifica i passaggi successivi. Solo dati sintetici in questa directory; è esclusa da Git. Le immagini selezionate per il portfolio vanno copiate in `demo/screenshots/` dopo la verifica visiva.

Riferimenti API usati per il driver: [upload Playwright](https://playwright.dev/docs/input#upload-files), [download ed evento effettivo](https://playwright.dev/docs/downloads), [screenshot della pagina](https://playwright.dev/docs/api/class-page#page-screenshot). Nessuno di questi test equivale all'apertura del file in Microsoft Excel o LibreOffice.
