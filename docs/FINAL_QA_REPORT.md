# Excel Cleaner Pro — revisione finale

## Versione attuale — verifica del 4–5 novembre 2026

Questa sezione descrive la versione attuale: interfaccia scura con accento smeraldo (`ui/theme.css`, `.streamlit/config.toml`), motore `excel_cleaner/` invariato rispetto al commit `aca0974`. Le sezioni «Storico» più in basso descrivono versioni precedenti e non vanno lette come stato corrente.

Ambiente: Windows 11, Python 3.12.14, pandas 2.3.3, openpyxl 3.1.5, Streamlit 1.66.1, pytest 9.2.0, Chromium headless 155.0.8059.12 (Playwright già installato), Microsoft Excel 16.0 build 20527. Nessuna nuova dipendenza installata. LibreOffice non è installato.

### Comandi eseguiti e risultati effettivi

| Comando | Risultato |
| --- | --- |
| `.\.venv\Scripts\python.exe -m pytest -q` (inizio) | 49 passed, 0 failed |
| `.\.venv\Scripts\python.exe -m scripts.browser_qa` (inizio, driver precedente) | **Fallito** al 4° scenario: il menu `amount · numero` non si apriva (vedi problema 1) |
| `scripts.browser_qa` con il nuovo driver, dopo le correzioni | 3 giri consecutivi superati, più un giro finale superato: 31 passaggi browser ciascuno, verifiche sui download riuscite |
| Giro finale `scripts.browser_qa` | 31/31 passaggi, 0 errori di pagina, 0 richieste esterne; fine `2026-11-04T23:00:18Z` |
| `.\.venv\Scripts\python.exe -m pytest -q` (fine) | **49 passed, 0 failed** |
| `.\.venv\Scripts\python.exe -m scripts.smoke_server` | HTTP 200 `ok`, solo 127.0.0.1 |
| `.\.venv\Scripts\python.exe -m pip check` | No broken requirements found |

Evidenze del giro finale: [risultati browser](final_browser_results.json), [controllo dei file scaricati](final_artifact_validation.json), [schermate](../demo/screenshots-dark/README.md), [report XLSX scaricato](../demo/qa_report.xlsx), [CSV scaricato](../demo/qa_cleaned.csv). Originali completi in `outputs/browser-qa-20261104T225917762219Z/` (escluso da Git).

### Problemi rilevati e correzioni

1. **Menu chiusi dal test browser (difetto del driver, non dell'app).** Riprodotto: dopo il clic il menu si apriva e si richiudeva da solo in circa 40 ms. Gli eventi registrati mostrano la causa. Il driver cliccava un controllo fuori schermo; Playwright lo portava al bordo della finestra e, appena aperto, il componente dei menu di Streamlit faceva scorrere ancora la pagina, che chiude il menu. Lo stesso accadeva con l'interfaccia precedente, quindi non dipende dal tema né dal motore. Il vecchio metodo (digitare, freccia giù, Invio) poteva inoltre lasciare nel campo un testo non confermato. Correzione nel driver: ogni controllo viene portato a metà finestra, si attende che sia fermo, poi si clicca il menu e l'opzione, come farebbe una persona. Il valore effettivamente applicato è verificato tramite il conteggio delle regole e il file scaricato. Nessuna pausa fissa, nessun nuovo tentativo, nessuna scrittura nello stato Streamlit. Per un utente reale il caso corrisponde a cliccare un menu mezzo nascosto sul bordo della finestra: il menu può richiudersi e basta riaprirlo. È un comportamento del componente Streamlit, non corretto dal progetto.
2. **Etichette delle caselle troncate su tablet e telefono (difetto del design).** A 900 e 390 px, «Rimuovi spazi esterni e comprimi spazi interni» e le altre regole finivano con «…». Streamlit tronca le etichette dei controlli: con il carattere e i riquadri del nuovo tema il testo non ci stava più. Correzione: le etichette delle caselle vanno a capo (`ui/theme.css`). Regressione: il driver fallisce se un'etichetta di casella è troncata su tablet o telefono. Il controllo è fallito sullo stile senza correzione ed è superato dopo.
3. **Aspettative errate del nuovo driver, corrette sul comportamento verificato.** (a) Sostituendo il file, l'app non mostra «Sorgente o impostazioni cambiate» perché l'uploader rimuove prima il file precedente. Profilo, regole e download vengono comunque invalidati, e ora il test verifica proprio questo. Il messaggio resta richiesto per separatore, codifica e foglio. (b) Il numero di righe atteso per `demo/04_italian_amounts.csv` era sbagliato: ora il report è confrontato con il file sorgente letto dal motore.

Nessuna regola del motore è stata modificata. Invarianti confermati nei download: originali intatti, data ambigua invariata senza formato scelto, `001` testuale, nulli non riempiti, eliminazione solo della copia esatta confermata, nessuna cella formula.

### Scenari browser coperti dal giro finale

| Gruppo | Passaggi |
| --- | --- |
| Desktop 1440 px, **movimento ridotto** | schermata iniziale, upload e profilo, link laterale alle regole, regole con formato data esplicito e conferma duplicati, download XLSX e CSV, annulla e ripristina |
| Desktop 1440 px, **animazioni attive** | gli stessi sei passaggi |
| Stessa sessione, senza ricaricare | regola senza formato data, sostituzione del file, cambio separatore, cambio codifica, cambio foglio XLSX, rimozione del file |
| File non validi | CSV vuoto, CSV malformato, file oltre 10 MB |
| Tablet 900 px e telefono 390 px, animazioni attive | schermata iniziale, upload, regole con formato data, anteprima, export con download; nessuno scorrimento orizzontale della pagina; etichette non troncate |

**Formato data (controllo A).** Con spazi, `title` su `name`, numeri italiani su `amount`, `%d/%m/%Y` su `date` e deduplica confermata, i report scaricati in entrambe le modalità di movimento contengono:

- 3 righe dati: `001` testo, importo numerico `1234.56`, data `2025-02-01` derivata da `01/02/2025`;
- `unknown` e `31/02/2025` conservati e presenti in Issues;
- `configuration_json` in Metadata con `date_columns = {"date": "%d/%m/%Y"}`;
- Change_Log con `01/02/2025 → 2025-02-01` alla riga 2, `drop_exact_duplicate` alla riga 4 e nessuna modifica su `code`.

Anche il CSV scaricato ha 3 righe, `001` e `2025-02-01`. Senza formato scelto la data resta `01/02/2025` ed è segnalata come ambigua.

**Animazioni (controllo B).** Menu, link laterale con scorrimento morbido, barra delle fasi, caselle, pulsanti, confronto e download superati con animazioni attive e con movimento ridotto, in 4 giri consecutivi dopo l'ultima correzione. Non è una garanzia assoluta: è l'esito di questi giri automatici.

**Cambio sorgente (controllo C).** Dopo ogni cambio di file, separatore, codifica o foglio, e dopo la rimozione del file, spariscono profilo, anteprima e pulsanti di download, e serve un nuovo «Carica dataset». Il report scaricato dopo la sostituzione contiene soltanto i dati del secondo file.

**Schermi stretti (controllo D).** A 390 e 900 px il flusso completo funziona; le tabelle scorrono al proprio interno, la pagina no. Ispezione visiva delle schermate eseguita. Dettaglio estetico residuo: a 900 px l'etichetta «Maiuscole/minuscole» va a capo a metà parola nella colonna stretta.

### Apertura del report in Excel

| Livello | Esito |
| --- | --- |
| Verifica XML con openpyxl | **Superata** per tutti i report scaricati: fogli, valori, tipi, Issues, Change_Log, Metadata, zero celle formula |
| Apertura nel programma nativo | **Superata**: Microsoft Excel 16.0 (build 20527) ha aperto, in sola lettura e con macro disattivate, il report scaricato dal browser e un report di `demo/07_untrusted_text.csv`. Excel vede quattro fogli, `001` come testo, `1234.56` come numero, `2025-02-01`, `unknown`, `31/02/2025`, zero celle con formula; `=1+1`, `@SUM(A1)` e `+1+2` restano testo. Registro: [excel_native_check.txt](excel_native_check.txt) |
| Ispezione grafica del workbook in Excel | **Non eseguita.** L'esportazione PDF da Excel non si è completata, probabilmente per la stampante predefinita di rete. Non ho cambiato la stampante di Windows né aperto Excel in primo piano. Checklist in [MANUAL_QA.md](MANUAL_QA.md) |

LibreOffice non è installato: nessuna verifica con LibreOffice.

### Controlli non completati

- Ispezione grafica del report in Excel o LibreOffice: leggibilità, larghezze, intestazioni, testo delle formule.
- Uso a mano con mouse e tastiera, focus da tastiera e lettori di schermo: i giri sono automatici.
- Firefox, Safari, Edge e un telefono reale: verificato solo Chromium headless con viewport stretta.
- Installazione su un Windows pulito, carico vicino ai limiti tecnici, tempi e memoria.
- Accettazione su un dataset concordato con un cliente.

### Giudizio

**Portfolio:** presentabile come applicazione locale con evidenze riproducibili. Il flusso completo, compresa la scelta del formato data, è verificato nel browser e sui file scaricati, e il report si apre correttamente in Excel.

**Incarichi commerciali:** non dichiarato commercialmente pronto. Prima di un incarico a pagamento servono l'ispezione grafica del report, una prova manuale nel browser usato davvero e criteri di accettazione concordati. La fascia EUR 25–40 resta un'ipotesi da validare.

### Avvio

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Aprire `http://127.0.0.1:8501`. Arresto con `Ctrl+C`.

---

# Storico — revisione del 4 novembre 2026 (restyling chiaro, versione precedente)

Completato e verificato il restyling chiaro/verde petrolio, con 46 test e 10 scenari browser superati. Dettagli in [UI_REDESIGN.md](UI_REDESIGN.md). Questa versione è stata sostituita dal tema scuro.

# Storico — revisione del 2 novembre 2026

Il testo seguente descrive la versione del 2 novembre e i limiti di allora. Alcuni, come il formato data nel browser e il cambio di sorgente nella stessa sessione, sono stati chiusi nella verifica attuale qui sopra.

Data locale: **2 novembre 2026, Europe/Rome**. Revisione del progetto esistente, senza ricostruzione o pubblicazione. Solo fixture sintetiche; nessun documento inviato a servizi esterni. La prima verifica rimane in `VERIFICATION.md` come registrazione storica.

## Ambiente e risultati automatici

Windows, Python 3.12.14, pandas 2.3.3, openpyxl 3.1.5, Streamlit 1.66.1, pytest 9.2.0; dipendenze già presenti nella `.venv`. Nessuna nuova installazione necessaria in questa revisione.

| Controllo effettivamente eseguito | Risultato |
| --- | --- |
| Suite iniziale `python -m pytest -q` | 33 passed in 5.10s |
| Suite finale dopo correzioni e nuove regressioni | **45 passed in 8.52s; 0 failed** |
| `python -m scripts.smoke_server` | HTTP 200, body `ok`, solo `127.0.0.1` |
| `python -m pip check` | No broken requirements found |
| Servizio proposto: 1.000 righe × 20 colonne | 1.000 righe conservate, 19.000 eventi di modifica, XLSX riaperto e conteggi verificati |
| Test AppTest formato data | Scelta `%d/%m/%Y` realmente recepita dalla UI/backend; ISO nel report, data impossibile e sorgente conservate |

L'intera suite è stata rieseguita dopo le modifiche al prodotto. Ulteriori tentativi sul driver browser hanno riguardato la sua sincronizzazione, senza modificare le regole di pulizia per far passare i test.

## Difetti riprodotti e corretti

1. **Underflow dei decimali:** un valore testuale non nullo estremamente piccolo diventava `0.0`. Ora rimane il testo originale con una segnalazione, senza una modifica inventata. Il nuovo test è fallito sul codice precedente e passato dopo la correzione.
2. **Dimensioni XLSX sottostimate:** un foglio con `<dimension ref="A1:A1">` ma contenuto reale su due colonne/due righe veniva importato come zero righe dati e una colonna. Ora si leggono le dimensioni effettive del contenuto, applicando i limiti durante l'iterazione. Anche questo difetto è stato riprodotto da un test prima della correzione.
3. **Annullamento oltre il livello disponibile:** dopo il ripristino della versione precedente, il pulsante restava attivo e un secondo clic poteva azzerare il risultato. Ora è disabilitato quando non esiste un ulteriore annullamento. Verificato con AppTest.

UI migliorata con un percorso operativo sintetico, nome della sorgente attiva e spiegazioni di `lower`/`upper`/`title`. Nessun restyling dell'architettura o sostituzione di funzioni corrette.

## Funzioni e integrità verificate

CSV: separatori `;`, `,`, tab e `|`, UTF-8/BOM, CP1252, Latin-1 e UTF-16; token letterali `NA` e `null` conservati. File vuoti/malformati rifiutati senza troncamenti. Excel: selezione foglio, intestazioni duplicate/vuote, righe finali vuote, dimensioni assenti o sottostimate. Limiti file/righe/colonne/celle/XLSX espanso verificati mediante fixture controllate con soglie ridotte; non sono un benchmark al carico massimo.

Pulizia: input non mutato, nulli conservati, codici con zeri iniziali protetti, numeri italiani/internazionali, valute ai bordi, separatori impropri, date ambigue/impossibili, collisioni di intestazioni, idempotenza nei casi coperti. Duplicati eliminati solo se identici nella sorgente e confermati; righe rese uguali dalla normalizzazione restano distinte. Un test controlla i riferimenti esatti di riga, la sequenza delle operazioni, le modifiche e le eliminazioni.

Export: riapertura programmatica XLSX con openpyxl, fogli/dati/metadati, timestamp UTC, zeri iniziali, conteggi e formule mantenute come testo. CSV protetto anche per intestazioni e prefissi con spazi/controlli; numeri negativi nativi restano numeri. Test XML ostile e lunghezza celle superati. L'assenza di formule eseguibili non costituisce una certificazione di sicurezza dei fogli di calcolo.

## Browser reale e download

Il driver opzionale usa Node/Playwright e Chromium già installati, senza scaricare eseguibili. Le richieste browser esterne sono bloccate; l'app ascolta su `127.0.0.1:8521`. Evidenze e dettagli dello scenario sono registrati nella sottosezione conclusiva di questo report.

**Esito conclusivo: 9 scenari browser superati**, Chromium 155.0.8059.12. Fine esecuzione: `2026-11-01T23:18:59.325Z`, cioè 2 novembre 2026 alle 00:18:59 in Europe/Rome. Zero errori JavaScript di pagina registrati; nessuna origine esterna richiesta durante lo scenario. Server e browser arrestati al termine.

| Scenario browser reale | Esito |
| --- | --- |
| Avvio e schermata iniziale completamente caricata | Superato |
| Upload CSV e profilazione | Superato |
| Spazi, title case, numeri italiani, conferma obbligatoria duplicati e anteprima | Superato |
| Download effettivo XLSX e CSV tramite pulsanti | Superato |
| Annullamento e ripristino | Superato |
| Upload XLSX e cambio Customers → Notes → Customers, con verifica dello schema | Superato |
| CSV vuoto/BOM e malformato rifiutati | Superato |
| File superiore a 10 MB rifiutato dall'uploader | Superato |
| Schermata iniziale a 390 × 844, titolo entro viewport | Superato; non copre tutto il flusso mobile |

L'XLSX **realmente scaricato** è stato riaperto con openpyxl: quattro fogli corretti, tre righe, codice `001`, importo numerico `1234.56`, date originali conservate perché non selezionate, `unknown` e data impossibile conservati, nessuna cella formula in alcun foglio. Il CSV scaricato ha tre righe dati e codice `001`. Questi controlli sono distinti dai passaggi Playwright e sono tutti superati.

Evidenze permanenti: [browser_results.json](browser_results.json), [browser_artifact_validation.json](browser_artifact_validation.json), [screenshot autentici](../demo/screenshots/README.md), [report scaricato](../demo/browser_report.xlsx), [CSV scaricato](../demo/browser_cleaned.csv). Gli output originali sono in `outputs/browser-qa-20261101T231840185412Z/` (directory esclusa da Git). Le immagini desktop overview/preview e le schermate iniziali desktop/mobile sono state anche ispezionate visivamente; nessuna ricostruzione grafica. Il primo tentativo mobile ridimensionava una sessione desktop con sidebar aperta: la prova conclusiva apre una nuova pagina direttamente nella viewport stretta e attende la schermata completa.

**Limite esplicito:** l'automazione della scelta del formato data non ha confermato stabilmente l'opzione nella combinazione Chromium/React-Aria installata. Non è dichiarata superata. Un primo report scaricato conservava le date originali e il controllo del contenuto l'ha segnalato, evitando un falso positivo basato sul solo testo del controllo. Il caso browser finale lascia intenzionalmente la regola date su Nessuna; la conversione è testata separatamente con motore e AppTest. Il formato data deve essere verificato manualmente nel browser prima di un incarico.

La configurazione predefinita attesa da Playwright puntava inizialmente a una versione Chromium non presente: il driver ora seleziona esplicitamente il browser già disponibile. Altri tentativi hanno richiesto adeguamenti dei selettori e della sincronizzazione upload; non sono stati conteggiati come esecuzioni integralmente riuscite.

## Materiali portfolio e offerta

- `PORTFOLIO.md`: presentazione inglese, problema, flusso, demo e confini reali.
- `docs/FIVERR_OFFER_EN.md`: titolo, pacchetto, requisiti, tempi proposti ed esclusioni.
- `docs/UPWORK_PROPOSAL_EN.md`: candidatura breve con placeholder da personalizzare.
- `docs/DEMO_VIDEO_SCRIPT.md`: sceneggiatura da 45–60 secondi, senza apertura Excel simulata.
- `demo/QUICKSTART.md`: guida per chi non conosce Python.
- `demo/10_before.csv`, `10_after.csv`, `10_report.xlsx`: esempio sintetico completo, più altre fixture di casi limite.

Offerta **Excel & CSV Data Cleaning**: un file, un foglio, fino a 1.000 righe dati e 20 colonne, regole concordate, report con log/anomalie e una revisione limitata agli accordi originali. **EUR 25–40** è un prezzo sperimentale da validare. Due giorni lavorativi sono un tempo proposto dopo revisione dei requisiti e conferma della disponibilità, non una garanzia verificata dal software. Nessuna pubblicazione o candidatura inviata.

## Limiti e verifiche ancora necessarie

- Aprire manualmente XLSX scaricato in Microsoft Excel o LibreOffice: verificare quattro fogli, valori, zeri iniziali, date/testo e assenza di contenuti attivi. Non eseguito graficamente in questa revisione.
- Verificare manualmente la selezione del formato data nel browser, con `01/02/2025 → 2025-02-01`, e verificare la medesima data nel download.
- Provare la sostituzione diretta del file e delle impostazioni CSV nella stessa sessione: il driver usa sessioni nuove per i diversi upload, quindi non certifica questo percorso. Il cambio foglio XLSX viene invece provato nella stessa sessione.
- Installazione su un secondo Windows pulito; uso del browser normalmente impiegato dal destinatario; revisione di leggibilità/focus e scorrimento delle tabelle su schermo stretto.
- Benchmark e memoria vicino ai limiti tecnici massimi non eseguiti; il test da 1.000 × 20 copre l'offerta proposta, non tutti i dataset possibili.
- Nessun audit indipendente, validazione contabile/legale, dato reale di cliente o test esaustivo su ogni tipo di workbook.

Rimangono i limiti documentati: nessuna conservazione di layout, macro, grafici o formule originali; nessun recupero di file corrotti/zeri perduti; niente fuzzy matching o valori inventati. Numeri decimali convertiti in float; per calcoli contabili serve una verifica separata. Le configurazioni API fanno riferimento alle intestazioni della sorgente e vanno aggiornate dopo una rinomina dello schema. La UI riparte sempre dalla sorgente.

**Giudizio:** presentabile come progetto locale da portfolio con evidenze riproducibili e limiti dichiarati. Non dichiarato commercialmente pronto: completare i controlli manuali e concordare criteri di accettazione prima di offrire una consegna a pagamento. La fascia di prezzo non dimostra domanda, clienti o guadagni.

## Avvio e prossimi passi Windows

Dalla cartella del progetto in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Aprire `http://127.0.0.1:8501`, seguire `demo/QUICKSTART.md`, annotare i risultati in `docs/MANUAL_QA.md` e arrestare con Ctrl+C. Su un PC nuovo creare `.venv` e installare `requirements.txt` come spiegato nel README. Per ripetere i test: `.\.venv\Scripts\python.exe -m pytest -q`.

Dopo i controlli, scegliere una piattaforma, verificare i requisiti correnti nel proprio account, personalizzare la bozza relativa, fissare un singolo prezzo/tempo sostenibile, allegare soltanto demo e screenshot sintetici verificati e pubblicare manualmente. La descrizione deve mantenere esclusioni, ambito, revisione e requisiti del cliente; non inserire esperienze o recensioni inventate. Prima di accettare un file reale, concordare autorizzazione, riservatezza, canale di scambio e cancellazione dei documenti.
