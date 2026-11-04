# Verifica facoltativa con browser reale

Lo script avvia Streamlit su `127.0.0.1:8521` e usa un Chromium **headless reale** con Playwright. Carica solo fixture sintetiche e salva schermate, download, log e un riepilogo JSON in una nuova directory `outputs/browser-qa-<timestamp UTC>/`. Non invia documenti a Internet: le richieste del browser verso host diversi da localhost vengono bloccate, e il test fallisce se ne avviene anche una sola. Al termine server e browser vengono arrestati.

```powershell
.\.venv\Scripts\python.exe -m scripts.browser_qa
```

Node, il pacchetto Node Playwright e Chromium devono essere già installati: lo script non li installa e non modifica il runtime condiviso. Su questo PC trova il runtime esistente e il browser nella cache di Playwright; non è una dipendenza dell'applicazione. Se necessario, impostare i percorsi di installazioni già disponibili:

```powershell
$env:ECP_NODE = 'C:\percorso\node.exe'
$env:ECP_PLAYWRIGHT = 'C:\percorso\node_modules\playwright'
$env:ECP_CHROMIUM = 'C:\percorso\chrome.exe'
.\.venv\Scripts\python.exe -m scripts.browser_qa
```

I percorsi sono esempi da sostituire. Se mancano questi strumenti, usare la [checklist manuale](MANUAL_QA.md) invece di dichiarare superato il test. La porta 8521 deve essere libera. Un giro completo dura circa un minuto.

## Cosa verifica (31 passaggi)

| Gruppo | Contenuto |
| --- | --- |
| Desktop 1440 px, movimento ridotto | Schermata iniziale; upload di `demo/10_before.csv` e profilo; link laterale alle regole; spazi, `title` su `name`, numeri italiani su `amount`, **`%d/%m/%Y` su `date`**, deduplica rifiutata senza conferma e poi confermata; download reali XLSX e CSV; annulla e ripristina |
| Desktop 1440 px, animazioni attive | Gli stessi sei passaggi, con scorrimento morbido e animazioni del tema |
| Stessa sessione, senza ricaricare la pagina | Regola senza formato data; sostituzione con `demo/04_italian_amounts.csv`; cambio separatore; cambio codifica; foglio XLSX Customers → Notes; rimozione del file. Dopo ogni cambio non devono restare profilo, anteprima o pulsanti di download |
| File non validi | CSV vuoto e malformato rifiutati senza export; file oltre 10 MB rifiutato dall'uploader |
| Tablet 900 px e telefono 390 px, animazioni attive | Upload, regole con formato data, anteprima ed export con download. Nessuno scorrimento orizzontale della pagina; etichette delle caselle non troncate |

Dopo il browser, il driver Python riapre con openpyxl **ogni file realmente scaricato** e controlla:

- valori, tipi e assenza di celle formula;
- le anomalie in Issues;
- il Change_Log (conversione della data, rimozione della copia esatta, nessuna modifica dei codici);
- la configurazione in Metadata, compreso il formato data effettivamente applicato.

Verifica anche che senza formato la data ambigua resti invariata e segnalata, e che il report dopo la sostituzione contenga solo il secondo file. L'esito è in `artifact_validation.json`.

## Come interagisce con la pagina

Le interazioni usano i controlli reali, senza scrivere nello stato Streamlit e senza pause fisse né nuovi tentativi. Ogni controllo viene portato a metà finestra; il driver attende che sia fermo per alcuni fotogrammi, poi clicca il menu e l'opzione come una persona.

Il motivo: i menu di Streamlit si richiudono se la pagina scorre subito dopo l'apertura, cosa che succede cliccando un controllo al bordo della finestra. Il driver precedente, che digitava il testo e confermava con Invio, falliva per questo in modo intermittente, e poteva lasciare nel campo un testo non confermato. Per questo il valore applicato è verificato sia con il numero di regole mostrato dopo l'applicazione sia sul file scaricato, non solo con il testo del menu.

## Limiti

Chromium headless con viewport ridotta non equivale a un telefono, a Firefox o Safari, né all'uso con mouse e tastiera di una persona. Nessuno di questi test equivale all'ispezione grafica del file in Microsoft Excel o LibreOffice. Su errore vengono salvati `failure.png` e `failure.txt`; `browser_results.json` elenca solo i passaggi effettivamente completati. La directory `outputs/` è esclusa da Git: le schermate per il portfolio vanno copiate in `demo/screenshots-dark/` dopo la verifica visiva.

Riferimenti API: [upload Playwright](https://playwright.dev/docs/input#upload-files), [download](https://playwright.dev/docs/downloads), [screenshot](https://playwright.dev/docs/api/class-page#page-screenshot).
