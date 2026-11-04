# Excel Cleaner Pro

Applicazione locale per pulire e controllare Excel e CSV con regole esplicite, anteprima e tracciabilità. Prototipo da portfolio con test automatici: prima di usarlo per incarichi commerciali occorre completare la verifica manuale descritta in `docs/MANUAL_QA.md`. Nessuna promessa di accuratezza universale o certificazione contabile.

## Requisiti e installazione Windows

L'interfaccia attuale è scura, con accento smeraldo, schede, barra delle fasi e navigazione laterale; si adatta a tablet e telefono. Richiede Streamlit 1.66+ (già indicato in `requirements.txt`). Usa solo caratteri e risorse locali. L'ultima verifica (4–5 novembre 2026) è nel [rapporto QA finale](docs/FINAL_QA_REPORT.md): 49 test automatici, 31 passaggi browser e apertura del report in Microsoft Excel, con [screenshot reali](demo/screenshots-dark/README.md). L'ispezione grafica del report e le prove manuali restano da completare.

Windows 10/11, PowerShell, Python **3.12 o superiore** con pip (consigliato 3.12), almeno 4 GB di RAM disponibili. Installare Python da python.org se `py --version` non funziona. Non serve Excel per eseguire l'app; per la verifica finale di apertura è utile Excel o LibreOffice. Internet serve solo all'installazione delle dipendenze, non all'elaborazione dei file.

Dalla cartella del progetto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Aprire `http://127.0.0.1:8501`. Il comando non richiede di attivare lo script PowerShell dell'ambiente virtuale. Se la `.venv` è già presente su questo computer, basta il comando di avvio. Gli ambienti virtuali non sono portabili: su un altro PC ricrearli. `requirements-lock.txt` registra l'ambiente effettivamente verificato; per riprodurlo su Python 3.12 usare `-r requirements-lock.txt` al posto di `requirements.txt`.

## Utilizzo

Se non conosci Python, segui la [prova guidata in pochi minuti](demo/QUICKSTART.md). Per presentare il progetto consulta [PORTFOLIO.md](PORTFOLIO.md); bozze di offerta e candidatura sono collegate lì. Non sono annunci pubblicati. La verifica più recente è in [FINAL_QA_REPORT.md](docs/FINAL_QA_REPORT.md); `VERIFICATION.md` conserva la prima verifica storica.

1. **Upload**: selezionare `.xlsx` o `.csv`. Per Excel scegliere un foglio; per CSV scegliere esplicitamente codifica e separatore nella barra laterale. Premere **Carica dataset**. La prima riga è sempre l'intestazione.
2. **Data Overview**: controllare preview (100 righe), conteggi, tipi, nulli, duplicati e anomalie. Solo campi CSV vuoti diventano nulli: `NA`, `N/A` e `null` restano testo. Intestazioni vuote o duplicate ricevono nomi distinti, con mappatura in Metadata.
3. **Cleaning Rules**: tutte le regole sono inizialmente disattivate. Selezionare compressione degli spazi, intestazioni, case e, per ciascuna colonna, formato numerico o data. Non selezionare conversioni numeriche per codici e CAP. Per eliminare copie esatte servono selezione e conferma separate.
4. **Preview Changes**: applicare le regole, confrontare prima/dopo e leggere controlli e log. Ogni applicazione riparte dalla sorgente, senza accumulare conversioni. **Annulla ultima applicazione** torna alla precedente versione (un livello); **Ripristina dati originali** cancella il risultato. I controlli delle regole rimangono selezionati e richiedono un nuovo invio.
5. **Export**: preparare e scaricare il report `.xlsx` o i dati CSV UTF-8 con BOM e separatore `;`. Le date convertite sono testo ISO, i numeri esportati nel CSV usano punto decimale. Il CSV non include log e metadati: consegnare anche il report quando serve tracciabilità.

Cambiare file, foglio o impostazioni CSV invalida il risultato corrente. **Cancella dati della sessione** rimuove upload, dati e report dalla sessione applicativa. I file scaricati restano nel PC finché non vengono cancellati dall'utente.

## Conversioni conservative

- Italiano: `1.234,56`, `12,50`, `-42,10`; internazionale: `1,234.56`, `12.50`. Simboli EUR/€ e USD/$ ai bordi sono ammessi, ma non viene eseguita conversione di valuta. Raggruppamenti impropri sono segnalati e conservati.
- Stringhe con zeri iniziali e numeri oltre 15 cifre significative non sono convertiti. La conversione a numero usa float per i decimali: non è un motore contabile a precisione arbitraria.
- Date solo con formato esplicito: giorno/mese/anno, mese/giorno/anno, ISO o giorno-mese-anno. `01/02/2025` resta invariata fino alla scelta; date impossibili rimangono testo con un'anomalia. L'output ISO è accettato nelle applicazioni successive per idempotenza.
- Nulli non riempiti. Nessuna riga dubbia eliminata. I duplicati eliminabili sono righe esattamente uguali **nella sorgente**, mantenendo la prima; la normalizzazione non autorizza ulteriori eliminazioni.
- Possibili duplicati: confronto di tutte le colonne dopo normalizzazione spazi/case; non include fuzzy matching, somiglianza semantica o deduplica basata solo su email/codice. Gli outlier numerici IQR sono indicativi e calcolati su valori nativi numerici; non sono una validazione di dominio.

## Report e integrità

Il report ha quattro fogli: **Cleaned_Data**, **Issues**, **Change_Log**, **Metadata**. Tutte le anomalie e gli eventi sono esportati; la UI ne mostra al massimo 1.000. I riferimenti di riga indicano la posizione nella sorgente, intestazione = 1, anche dopo le eliminazioni. Issues descrive problemi nella sorgente e conversioni fallite: un avviso può rimanere anche se una regola ha corretto il testo.

Change_Log registra per cella regola, prima e dopo; può avere più eventi per la stessa cella. Le righe modificate contano una sola volta le righe con modifiche alle celle, anche se poi eliminate; le eliminazioni sono contate a parte. Cambiare un'intestazione non modifica il conteggio delle righe dati. Metadata contiene timestamp UTC, configurazione, mappatura intestazioni/importazione e risultati reali dei controlli: bilancio delle righe, numero colonne, intestazioni univoche, autorizzazione eliminazioni e ordine. I controlli strutturali non provano che una data o un importo siano corretti per il cliente.

## Sicurezza e privacy

I controlli includono anche la conservazione delle posizioni dei valori nulli nelle righe mantenute. Metadata registra l'impronta SHA-256 del file importato. Date Excel native contenenti anche un orario o un fuso restano inalterate con una segnalazione se selezionate per conversione; l'app non scarta l'orario. Gli interi nativi oltre 15 cifre vengono esportati in XLSX come testo per evitare perdita di precisione.

Il server ascolta soltanto su `127.0.0.1`; non pubblicarlo su rete o Internet senza un progetto separato di autenticazione e sicurezza. Telemetria Streamlit disabilitata. Nessun account, API AI, connessione cloud, cache condivisa o salvataggio dei caricamenti su disco. Elaborazione e download avvengono in memoria; evitare dati riservati su PC condivisi. La cancellazione della sessione non è cancellazione forense della RAM, dei download o della memoria del browser; chiudere app/browser al termine. Non sono implementati cifratura, controllo accessi o gestione multiutente.

Le formule XLSX in ingresso sono lette come testo, mai calcolate. Nell'XLSX esportato tutte le stringhe, incluse intestazioni e log, sono forzate a testo. Il CSV aggiunge un apostrofo a stringhe che possono diventare formule (anche precedute da spazi) e quota tutti i campi. Questo altera volutamente la rappresentazione di tali stringhe nel CSV; non sostituisce l'attenzione nell'aprire file non attendibili. Excel può reinterpretare codici e date di un CSV, anche quotato: usare XLSX o importare le colonne come testo. Non abilitare macro, collegamenti esterni o contenuti attivi di file sconosciuti. L'app non modifica gli originali e non esegue le loro formule.

È inclusa `defusedxml` per la protezione del parsing XML dei file XLSX, come raccomandato dalla [documentazione di sicurezza openpyxl](https://openpyxl.readthedocs.io/en/stable/). Non è una scansione antivirus dei documenti.

## Limiti

- 10 MB/file; 50.000 righe, 200 colonne e 500.000 celle per foglio selezionato; archivio XLSX espanso massimo 80 MB e 5.000 elementi. File con dichiarazioni di dimensioni gonfiate possono essere rifiutati. Elaborazione in memoria: log estesi possono consumare molta RAM; evitare più sessioni contemporanee. Nessun benchmark promette tempi massimi.
- Solo `.xlsx` non cifrato e CSV; niente `.xls`, `.xlsm`, PDF, OCR, cartelle batch o fogli uniti. Fogli vuoti rifiutati; file con sola intestazione accettati.
- Importazione di **valori**, non conservazione del workbook: stili originali, celle unite, grafici, macro, formule, convalide, nomi, formattazione e collegamenti non sono ricostruiti. Codici già memorizzati come numeri in Excel non possono recuperare zeri presenti solo nel formato visivo.
- Encoding supportati: UTF-8/BOM, CP1252, Latin-1 e UTF-16; separatori `;`, `,`, tab e `|`. Nessuna deduzione affidabile della codifica: Latin-1 può decodificare caratteri errati senza errore; verificare la preview.
- CSV con righe di lunghezza incoerente o virgolette aperte rifiutati; nessuna correzione automatica. Assenza di righe vuote intermedie consigliata (vengono rifiutate nel CSV).
- Excel limita celle a 32.767 caratteri e report a 1.048.576 righe; esportazioni oltre tali limiti sono bloccate invece di troncare. Per testi incompatibili resta disponibile CSV. Valori decimali destinati a calcoli contabili richiedono verifica professionale separata.

## Test, demo e skill

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.generate_demo
```

`tests/` verifica invarianti dati, casi limite, esportazioni e flussi UI con Streamlit AppTest. `demo/` contiene 11 input interamente sintetici, esempio prima/dopo e report. [Guida demo](demo/README.md), [servizio in inglese](demo/FREELANCE_SERVICE_EN.md), [verifica manuale](docs/MANUAL_QA.md), [risultati effettivi](docs/VERIFICATION.md).

Le due skill sono in `.agents/skills/`, con frontmatter `name`/`description`. Sono state lette esplicitamente durante lo sviluppo: non si presume l'attivazione automatica in questa sessione. Per un agente che non le scopra, chiedere di leggere il relativo `SKILL.md`; consultare anche `AGENTS.md`. Per il validatore di skill-creator serve PyYAML (`requirements-dev.txt`), non necessario all'app.

## Risoluzione problemi

La verifica opzionale con browser reale si avvia con `.\.venv\Scripts\python.exe -m scripts.browser_qa` quando Node, Playwright e Chromium sono già disponibili. Non viene installato né scaricato un browser. Requisiti, evidenze e ripetizione sono descritti in [BROWSER_QA.md](docs/BROWSER_QA.md). Non è necessaria per il normale avvio dell'app.

- `py` non riconosciuto: installare Python dal sito ufficiale, riaprire il terminale oppure usare il percorso completo dell'interprete Python già installato. Non usare la `.venv` di un altro PC.
- `ModuleNotFoundError`: ripetere l'installazione con **lo stesso** `.venv\Scripts\python.exe` usato per avviare l'app.
- Porta occupata: aggiungere `--server.port 8502`; aprire il nuovo indirizzo locale. Arresto: `Ctrl+C` nel terminale.
- CSV in una sola colonna: cambiare separatore e premere Carica dataset. Accenti errati: provare la codifica corretta confrontando l'originale.
- File rifiutato: controllare limiti, prima riga, protezione/cifratura e formato reale; creare una copia con sole colonne/righe necessarie senza sovrascrivere l'originale.
- Opzioni cambiate ma risultato precedente: premere Applica; il pannello configurazione mostra sempre l'ultima applicazione riuscita.
