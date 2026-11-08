# Catalogo prodotti: demo sintetica verificabile

Questa dimostrazione usa 200 righe inventate, relative a 190 SKU distinti. Nessun negozio, cliente, transazione o prezzo reale. È un esempio da portfolio di pulizia e uniformazione di una tabella; non è un catalogo pronto per l'importazione in una specifica piattaforma.

Il progetto e i materiali portfolio sono stati realizzati con l'assistenza di **Claude (Anthropic)** e **Codex (OpenAI)**, su indicazioni dell'autore. L'assistenza riguarda lo sviluppo; la pulizia dei file usa regole Python esplicite e non contatta modelli AI.

Apri **[index.html](index.html)** con un doppio clic per la pagina portfolio locale: confronto interattivo, anomalie selezionate e file scaricabili. Non servono account, server remoto, risorse esterne o installazioni aggiuntive per leggere la pagina. Per elaborare il file nell'app serve l'ambiente Python del progetto.

## File

| File | Contenuto |
| --- | --- |
| [catalogo_originale.csv](catalogo_originale.csv) | Sorgente: 200 righe × 8 colonne, UTF-8 con BOM, separatore `;` |
| [catalogo_pulito.csv](catalogo_pulito.csv) | Risultato: 194 righe; non include il log |
| [catalogo_report.xlsx](catalogo_report.xlsx) | Report generato dal motore: Cleaned_Data, Issues, Change_Log, Metadata |
| [rules.json](rules.json) | Regole usate nella dimostrazione |
| [summary.json](summary.json) | Conteggi e campioni ricavati dall'esecuzione del motore |
| [SERVICE_EN.md](SERVICE_EN.md) | Descrizione inglese del servizio proposto, con limiti reali |

Il video, gli screenshot e `catalogo_report_browser.xlsx`, quando presenti, provengono da una distinta esecuzione reale dell'app tramite browser. Non vengono rigenerati dal solo generatore dei dati. Le relative evidenze sono in `docs/catalog-demo/`.

## Prova nell'app

Avvia dalla radice del progetto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

1. Carica `catalogo_originale.csv`, codifica `utf-8-sig`, separatore punto e virgola; premi **Carica dataset**.
2. Controlla 200 righe, 8 colonne, 6 duplicati esatti extra e 8 righe soltanto simili.
3. Attiva **Rimuovi spazi esterni e comprimi spazi interni**. Lascia disattivata la standardizzazione delle intestazioni: sono già uniformi.
4. Seleziona `nome` e `categoria` come colonne testuali e scegli **title**. Questa scelta è adatta ai nomi sintetici; sui nomi reali va concordata per evitare di alterare marchi o sigle.
5. Nell'espansore numeri/date scegli **Italiano (1.234,56)** per `prezzo_eur` e `disponibilita`; `%d/%m/%Y` per `aggiornato_il`. Lascia **Nessuna** per gli altri campi, soprattutto `sku` e `codice_fornitore`.
6. Seleziona entrambe le caselle per la rimozione confermata delle copie esatte. Applica e controlla l'anteprima.
7. Prepara e scarica le esportazioni. Confronta i valori attesi qui sotto con il report.

## Risultati attesi

- **200 → 194 righe**: eliminate soltanto 6 copie identiche nella sorgente. I 190 SKU distinti restano tutti presenti.
- **Quattro coppie simili conservate**: SKU `000010`, `000050`, `000090`, `000130`, due righe ciascuno. Dopo trim e title le coppie diventano uguali, ma non erano copie esatte nella sorgente. Nessuna decisione commerciale di deduplica per SKU viene automatizzata.
- **7 celle vuote conservate**; `N/A` nella nota dello SKU `000073` resta testo.
- **200 righe con celle modificate**, comprese le 6 poi eliminate. Non equivale a 200 prodotti distinti o a 200 righe finali.
- **1.392 eventi di modifica**, incluse le eliminazioni; **112 segnalazioni** in Issues. Una stessa riga può produrre più eventi. Issues include anomalie della sorgente, comprese date inizialmente ambigue poi normalizzate: non sono 112 errori irrisolti.

| Caso | Prima | Dopo |
| --- | --- | --- |
| SKU `000001` | `000001` | `000001`, testo |
| Fornitore dello stesso prodotto | `00101` | `00101`, testo |
| Nome | Spazi ripetuti e maiuscole | `Tazza Aurora Modello 001` |
| Prezzo | `€ 1.234,56` | Numero `1234.56` |
| Aggiornamento | `01/02/2026` | Testo ISO `2026-02-01`, con formato scelto |

Valori che richiedono una decisione:

| SKU | Campo | Valore conservato |
| --- | --- | --- |
| `000018` | prezzo_eur | `da verificare` |
| `000088` | prezzo_eur | `12,3,4` |
| `000148` | prezzo_eur | `N/D` |
| `000062` | disponibilita | `in arrivo` |
| `000045` | aggiornato_il | `31/02/2026` |
| `000145` | aggiornato_il | `data da confermare` |

Le celle vuote appartengono a prezzo (`000033`, `000133`), disponibilità (`000022`, `000122`), data (`000095`), categoria (`000065`) e nota (`000175`). La necessità di completarle dipende dai requisiti del destinatario, non viene dedotta dall'app.

Il log usa le righe del CSV originale, intestazione = 1. Le sei copie eliminate sono alle righe 192–197. Le varianti simili sono alle righe 198–201, confrontabili con le righe 11, 51, 91 e 131.

## Significato per un cliente

La consegna rende più uniformi i dati e permette di controllare le modifiche. Il cliente vede anche quali campi richiedono ancora una scelta. L'esempio non dimostra tempo risparmiato, correttezza dei prezzi o compatibilità con un gestionale: servono requisiti e prove specifiche.

Non ricaricare automaticamente il CSV pulito attivando di nuovo la deduplica: le quattro coppie normalizzate sono ora esatte nella nuova sorgente e diventerebbero eliminabili. Nell'app, ripetere l'applicazione sulla sorgente originale produce lo stesso risultato. I test verificano separatamente l'idempotenza delle conversioni senza autorizzare nuove eliminazioni.

Per conservare zeri iniziali e tipi preferisci XLSX. In CSV importa codici come testo, numeri con punto decimale e date ISO senza inferenze automatiche. Gli originali non vengono salvati dall'app; l'export XLSX usa temporanei locali, normalmente rimossi a successo, con possibili residui dopo crash.

## Rigenerazione e verifiche

```powershell
.\.venv\Scripts\python.exe -m scripts.generate_catalog_demo
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.catalog_browser_qa
```

Il generatore riscrive soltanto i file di questa demo che gli appartengono; CSV e conteggi sono riproducibili, il timestamp del report cambia. Il controllo browser richiede Node, Playwright, Chromium e il relativo encoder video già disponibili; non scarica dipendenze. Usa solo localhost, ferma i server al termine e registra il flusso reale senza audio. Le pause nel video servono a leggere; nessuna accelerazione dell'elaborazione. Per aggiornare soltanto la pagina dopo aver aggiunto le evidenze: `-m scripts.generate_catalog_demo --page-only`.

La pagina HTML è un caso dimostrativo, non una seconda applicazione di pulizia: confronta campioni reali precomputati. Nessun upload o elaborazione di file utente avviene nella pagina portfolio. La verifica automatica non sostituisce l'accettazione manuale del cliente.
