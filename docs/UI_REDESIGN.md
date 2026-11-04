# Tema scuro — 4 novembre 2026 (sera)

> **Versione attuale.** Dopo questa sezione, la verifica finale ha corretto il troncamento delle etichette delle caselle su schermi stretti (`ui/theme.css`) e ha esteso il test browser. Risultati e limiti correnti: [FINAL_QA_REPORT.md](FINAL_QA_REPORT.md). Le sezioni successive sono storiche.

Su richiesta dell'utente il design premium passa a un tema scuro, poi rifinito osservando dal vivo cinque siti di prodotti software con design scuro curato (linear.app, supabase.com, vercel.com, raycast.com, resend.com). Ne sono stati ripresi solo principi generali, non marchi, grafica o colori distintivi. Struttura, animazioni, responsive, testi e motore restano invariati.

Principi applicati:

- **Nero neutro** (`#08090A`) invece di un fondo tinto. Una sola luce d'atmosfera discreta in alto, nessuna trama.
- **Un solo accento**, smeraldo `#2BD6A3`, riservato a pulsante principale, passi completati, stati positivi e collegamenti.
- **Bordi sottili** (bianco 8–15%) e superfici appena più chiare al posto di ombre e aloni.
- **Tipografia**: titoli grandi, peso 600, spaziatura stretta (−3/−4,5%); frase introduttiva in due toni. Caratteri solo di sistema, nessuno scaricato: Inter se installato, Segoe UI Variable su Windows 11, carattere di sistema su macOS.
- **Pulsanti sobri**: tinta piena con raggio 8 px e testo scuro; secondari trasparenti con bordo.
- Testo secondario grigio neutro, con contrasto di almeno 4,5:1 per il testo piccolo. Il grigio più tenue serve solo per elementi decorativi.

**Verifica**: 49 test pytest superati; `scripts.browser_qa` con 10/10 scenari in 3 giri consecutivi, l'ultimo alle `2026-11-04T21:56:20Z`, con download reali riaperti e zero richieste esterne. Schermate a 1440, 900 e 390 px senza scroll orizzontale. Evidenze: [risultati](ui_dark_browser_results.json), [file scaricati](ui_dark_artifact_validation.json), [schermate](../demo/screenshots-dark/README.md). Valgono gli stessi limiti della sezione seguente.

# Design premium e responsive — 4 novembre 2026 (sera)

Evoluzione dello stesso restyling verde petrolio, richiesta dall'utente: aspetto da sito premium, migliore resa su tablet e mobile, animazioni più curate. Motore, testi dei pulsanti e titoli delle sezioni sono invariati.

- **Stile separato** in `ui/theme.css`, caricato da `ui/presentation.py`. Solo font di sistema/Streamlit e icone SVG `data:` interne: nessuna risorsa esterna.
- **Intestazione**: titolo con gradiente, pillole delle caratteristiche e scheda "Esempio di pulizia" con valori sintetici fissi (mai dati caricati), nascosta sotto 1100 px.
- **Barra delle fasi fissa** in alto durante lo scorrimento, con collegamenti che si riempiono. Etichette brevi sotto 1000 px.
- **Responsive**: metriche, confronto prima/dopo e schede di export vanno a capo invece di stringersi. Nessuno scroll orizzontale a 1440, 900 e 390 px.
- **Animazioni**: comparsa morbida delle sezioni, riflesso sui pulsanti principali, sollevamento al passaggio del mouse, evidenza della sezione attiva. Con "riduci animazioni" del sistema sono disattivate.
- Download con icona grafica, regole raggruppate in pannelli (duplicati in tono d'avviso), controlli di integrità in pillole, pulsante "Deploy" nascosto (`client.toolbarMode = "minimal"`).

**Difetto trovato e corretto durante la verifica.** Una regola globale `*` per il movimento ridotto impediva l'apertura dei menu a tendina di Streamlit: il test browser falliva, mentre l'interfaccia precedente passava 3 giri su 3 nelle stesse condizioni. La regola ora vale solo per gli elementi del progetto; `tests/test_presentation.py` impedisce che torni. Anche una freccia testuale nel CSS cambiava il nome accessibile del pulsante di download: sostituita con un'icona grafica.

**Verifica**: 49 test pytest superati; `scripts.browser_qa` con 10/10 scenari in 4 giri consecutivi, l'ultimo alle `2026-11-04T21:38:40Z`, con download reali riaperti e zero richieste esterne. Evidenze: [risultati](ui_premium_browser_results.json), [file scaricati](ui_premium_artifact_validation.json), [schermate](../demo/screenshots-premium/README.md).

Limiti: il test automatico gira con "riduci animazioni". In una prova ripetuta con le animazioni attive, il menu si è aperto troppo tardi per lo script in 1 caso su 6, probabilmente per lo scorrimento morbido in corso. Restano da fare la prova manuale con mouse e tastiera, i browser diversi da Chromium (Firefox, Safari) e l'intero flusso su un telefono reale.

# Dashboard chiara e verde petrolio — 4 novembre 2026

Restyling scelto dall'utente per Excel Cleaner Pro. Layout a schede bianche su fondo chiaro, accento `#126B5A`, navigazione laterale verso le sezioni disponibili, indicatore delle fasi, riepiloghi numerici e confronto prima/dopo più leggibile. Gli screenshot sono acquisizioni della vera app, non immagini generate.

## Cambiamenti

- Identità visiva compatta nella sidebar e impostazioni CSV più ordinate; limiti/privacy in un pannello espandibile.
- Schede Upload, Data Overview, Cleaning Rules, Preview Changes ed Export; navigazione con ancore effettive alle sezioni presenti.
- Regole raggruppate per testo, numeri/date e duplicati. È spiegato che la sola conferma non attiva la rimozione.
- Messaggio esplicito «Nessuna trasformazione selezionata» quando si esporta l'originale. La conferma da sola conta come zero regole e conserva tutte le righe.
- Righe modificate, duplicati rimossi e righe in uscita in riquadri separati. Controlli espressi in linguaggio leggibile; JSON e configurazione restano disponibili nei dettagli tecnici.
- Export con descrizione dei due formati e pulsanti riconoscibili; indicatori e navigazione si adattano alla larghezza disponibile.

Tema nativo in `.streamlit/config.toml`; CSS limitato alle classi definite dal progetto e ai contenitori con `key` esplicita, in `ui/presentation.py`. Nessun dato caricato interpolato nell'HTML. Motore di ingestione, pulizia, validazione ed esportazione invariato. Riferimenti pubblici usati: [tema e colori](https://docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders), [contenitori e classi basate su key](https://docs.streamlit.io/develop/api-reference/layout/st.container).

Richiesto Streamlit **1.66+**, coerente con il runtime verificato 1.66.1 e con `requirements-lock.txt`. Non sono state installate nuove dipendenze né skill di terzi. Font e stile sono locali: alcune icone Material inizialmente tentavano richieste a Google Fonts, rilevate nel browser e rimosse. Il test ora fallisce se l'interfaccia tenta qualsiasi richiesta di risorse esterne.

## Verifica effettiva

- **46 passed in 8.64s**, zero fallimenti: `.\.venv\Scripts\python.exe -m pytest -q`.
- **10 scenari reali browser superati**, Chromium 155.0.8059.12: avvio, CSV/profilo, nuovo link di navigazione alle regole, pulizia con conferma, veri download XLSX/CSV, undo/reset, XLSX/cambio foglio, file vuoti/malformati, limite upload, schermata iniziale stretta.
- Report realmente scaricato riaperto con openpyxl: quattro fogli, tre righe finali, codice `001`, importo numerico `1234.56`, valori dubbi conservati, nessuna formula eseguibile. CSV scaricato verificato.
- **Zero errori di pagina e zero richieste a origini esterne** nello scenario conclusivo. Timestamp: `2026-11-04T20:49:23.416Z` (21:49:23 Europe/Rome).
- Ispezione visiva delle schermate desktop di caricamento, profilo, confronto ed export e della schermata iniziale a 390 × 844. Il test attende anche il vero pulsante Upload per evitare acquisizioni durante il caricamento.
- Nuova regressione AppTest: conferma duplicati selezionata da sola → sorgente integra, zero modifiche/eliminazioni e messaggio esplicito di export originale.

Evidenze: [risultati browser](ui_browser_results.json), [controllo dei download](ui_browser_artifact_validation.json), [schermate del restyling](../demo/screenshots-redesign/README.md), [XLSX scaricato](../demo/ui_report.xlsx), [CSV scaricato](../demo/ui_cleaned.csv). Originali in `outputs/browser-qa-20261104T204903989804Z/`, esclusi da Git. Il precedente aspetto e le verifiche del 2 novembre restano conservati.

Lo scenario browser applica spazi, title case, numeri italiani e deduplica. Lascia le date invariate: rimane da completare la verifica manuale del menu formato data; motore e AppTest della conversione passano. Rimangono inoltre l'apertura grafica in Excel/LibreOffice, l'intero flusso mobile, la sostituzione diretta di sorgenti nella stessa sessione e le altre verifiche elencate in `MANUAL_QA.md`. Nessuna dichiarazione di prontezza commerciale.

## Avvio

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Aprire `http://127.0.0.1:8501`. Per temi rimasti in cache, riavviare il server e ricaricare la pagina; il riavvio svuota i dati di sessione, quindi ricaricare eventuali sorgenti.
