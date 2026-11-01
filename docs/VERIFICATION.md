# Verifica eseguita — 1 novembre 2026

Ambiente: Windows, Python 3.12.14, pandas 2.3.3, openpyxl 3.1.5, Streamlit 1.66.1, pytest 9.2.0. Versioni complete in `requirements-lock.txt`; ambiente virtuale locale `.venv`, nessuna installazione globale.

## Risultati effettivi

Comando dalla radice:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

**33 passed in 3.14s — 0 fallimenti nella suite finale.**

- Ingestione: encoding e separatori espliciti, CSV malformati/vuoti, Excel non valido e selezione fogli, zeri iniziali, righe finali vuote, colonne senza intestazione nei workbook senza dimensioni dichiarate.
- Motore: default conservativi e immutabilità sorgente, nulli, spazi, deduplica confermata, conservazione di righe simili, numeri italiani/internazionali e importi euro, raggruppamenti impropri, conversioni fallite, date ambigue/impossibili, collisioni intestazioni, idempotenza delle trasformazioni testate, conteggio modifiche e ordine anche con indici non monotoni.
- Export: riapertura con openpyxl, fogli e metadati, UTC/configurazione/controlli, CSV con formule e numeri negativi nativi, formule in intestazioni/log/dati, prefissi con spazi e controlli, limite lunghezza celle senza troncamento, round-trip con righe vuote.
- Sicurezza ingestione: entità XML rifiutate grazie a defusedxml; limiti di righe rifiutati invece di troncati.
- UI AppTest: avvio, default senza trasformazioni, applicazione e trim, immutabilità originale, annullamento, ripristino, cancellazione sessione, generazione di reali byte XLSX/CSV in memoria. L'upload è simulato inserendo in sessione un frame già letto: AppTest non esegue il caricamento attraverso il browser.
- Portfolio: file demo consegnati riaperti, conteggi e valori confrontati tra report e CSV. 11 input sintetici, 1 CSV dopo pulizia e 1 report Excel.

Ulteriori comandi eseguiti con esito positivo:

```powershell
.\.venv\Scripts\python.exe -m scripts.generate_demo
.\.venv\Scripts\python.exe -m scripts.smoke_server
```

Smoke server: **HTTP 200, body `ok`** da `127.0.0.1:8519/_stcore/health`; processo arrestato dallo script. Non dimostra il flusso completo nel browser.

Le due skill in `.agents/skills/` sono state lette esplicitamente e validate con `skill-creator/scripts/quick_validate.py`: **Skill is valid!** per entrambe. PyYAML è una dipendenza di sviluppo per quel validatore, non dell'app.

Il primo giro della suite aveva 21 successi e 1 fallimento: un test richiedeva un evento Change_Log anche senza trasformazioni. È stato corretto per aspettarsi il log vuoto e verificare i metadati effettivi, senza inventare eventi nell'app. Le successive verifiche hanno aggiunto casi di regressione fino al risultato finale sopra riportato.

## Verifiche non eseguite e limiti della conclusione

Non eseguiti: revisione grafica in browser reale desktop/mobile, upload/download tramite browser, apertura manuale in Microsoft Excel/LibreOffice, installazione su un secondo Windows pulito, benchmark vicino ai limiti massimi, audit indipendente e test su dati di clienti. La checklist è in `MANUAL_QA.md`; tutte queste attività restano distinte dai test automatici passati.

Il progetto è un'app locale verificabile per portfolio, **non dichiarata pronta per la vendita**. L'idempotenza testata riguarda trasformazioni su uno schema compatibile: le configurazioni del motore fanno riferimento ai nomi di colonna della sorgente; se si riutilizza l'API su dati già rinominati, aggiornare i nomi della configurazione. La UI riparte sempre dall'originale, evitando questo problema.

L'ambiente sandbox del terminale ha restituito `setup refresh had errors`; installazioni locali ed esecuzioni sono riuscite tramite le escalation autorizzate. Nessuna verifica richiesta è stata presentata come eseguita quando non lo era.
