# Prova guidata per chi non conosce Python

L'app funziona sul computer: non serve Excel per usarla. Excel o LibreOffice servono per verificare il file finale con il programma che userà il destinatario. I dati di questa cartella sono tutti inventati.

## Aprire l'app su Windows

Se il progetto è già installato su questo computer, aprire la cartella `Excel-AI-Automation` in VS Code, scegliere **Terminale → Nuovo terminale** e incollare:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Aprire `http://127.0.0.1:8501` nel browser. Tenere aperto il terminale; per fermare l'app premere `Ctrl+C`. Se il comando non trova Python o la cartella `.venv`, seguire prima l'[installazione nel README](../README.md). Non copiare l'ambiente virtuale da un altro PC.

## Una prova di pochi minuti

1. Nella barra laterale scegliere codifica `utf-8-sig` e separatore **Punto e virgola ;**.
2. In Upload selezionare [10_before.csv](10_before.csv) dalla cartella demo e premere **Carica dataset**. Si devono vedere quattro righe e quattro colonne.
3. In Cleaning Rules attivare la rimozione degli spazi. Scegliere `name` tra le colonne di testo e modalità `title`.
4. Espandere le impostazioni per colonna: per `amount` scegliere numero italiano; per `date` scegliere `%d/%m/%Y`. Lasciare `code` senza conversioni.
5. Selezionare la rimozione dei duplicati esatti e la relativa conferma; premere **Applica e mostra anteprima**.
6. Controllare tre righe in uscita: codice `001` conservato, importo `1234.56`, data `2025-02-01`. `unknown` e `31/02/2025` devono restare visibili, con segnalazioni. Le anomalie includono anche osservazioni sulla sorgente.
7. Provare **Annulla ultima applicazione**, poi riapplicare le regole. **Ripristina dati originali** elimina il risultato senza cambiare il file originale.
8. In Export premere **Prepara esportazioni**, poi scaricare il report Excel. Controllare i fogli `Cleaned_Data`, `Issues`, `Change_Log`, `Metadata`. Confrontarlo con [il report sintetico incluso](10_report.xlsx) e [il CSV dopo pulizia](10_after.csv).

Il CSV scaricato usa `;` e numeri con punto decimale. Per evitare che Excel reinterpreti codici o date, preferire il report XLSX; se si importa un CSV, impostare le colonne dei codici come testo. Non abilitare macro o contenuti attivi provenienti da file sconosciuti.

## Screenshot autentici per il portfolio

Sono ora disponibili [screenshot autentici della UI](screenshots/README.md) e un [report realmente scaricato dal browser](browser_report.xlsx). In questo scenario browser le date sono intenzionalmente lasciate invariate; il report `10_report.xlsx` applica anche la conversione data. L'apertura manuale in Excel/LibreOffice e la scelta del formato data nel browser restano da verificare.

Se non sono disponibili acquisizioni automatiche verificate, crearli manualmente dopo questa prova:

1. Usare soltanto `10_before.csv`; nascondere notifiche, nomi utente, percorsi personali e altre finestre.
2. Con **Win+Maiusc+S**, acquisire l'overview con quattro righe.
3. Acquisire le regole scelte e il confronto prima/dopo con tre righe.
4. Acquisire anomalie e log; infine i fogli del report aperto davvero in Excel/LibreOffice.
5. Salvare immagini leggibili, senza ricostruzioni grafiche dei risultati. Aggiungere la didascalia «Synthetic demonstration — no client data».

Se un passaggio non riesce, annotarlo nella [checklist manuale](../docs/MANUAL_QA.md). Non presentarlo come superato. Screenshot e report illustrano capacità del software, non recensioni, lavori di clienti o risultati di vendita.
