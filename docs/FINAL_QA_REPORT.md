# Excel Cleaner Pro — revisione finale

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
