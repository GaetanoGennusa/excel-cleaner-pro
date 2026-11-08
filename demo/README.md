# Dimostrazione Excel Cleaner Pro

L'interfaccia attuale (tema scuro) è documentata nelle [schermate reali](screenshots-dark/README.md), con il [report scaricato dal browser](qa_report.xlsx) e il [CSV](qa_cleaned.csv) dell'ultima verifica. Le schermate e i file delle versioni precedenti restano come storico: [variante chiara premium](screenshots-premium/README.md), [restyling chiaro](screenshots-redesign/README.md) con [report](ui_report.xlsx), e [prime schermate](screenshots/README.md).

Tutti i dati di questa cartella sono inventati. Non rappresentano clienti, persone o transazioni reali.

La demo principale per il portfolio è ora il [catalogo prodotti](product_catalog/README.md): 200 righe sintetiche, pagina HTML locale, report, confronto e video autentico. [Apri la pagina](product_catalog/index.html). Il relativo generatore è separato: `.\.venv\Scripts\python.exe -m scripts.generate_catalog_demo`. I file numerati qui sotto restano casi minimi utili per prove mirate.

Rigenera i file dalla radice del progetto con `.\.venv\Scripts\python.exe -m scripts.generate_demo`.

| File | Caso dimostrato |
| --- | --- |
| 01_duplicates.csv | Righe duplicate esatte |
| 02_nulls.csv | Valori mancanti conservati |
| 03_ambiguous_dates.csv | Date ambigue e data impossibile |
| 04_italian_amounts.csv | Importi italiani |
| 05_leading_zero_codes.csv | Codici con zeri iniziali |
| 06_international_amounts.csv | Importi internazionali |
| 07_untrusted_text.csv | Testi simili a formule, da trattare come dati |
| 08_malformed.csv | CSV volutamente non valido |
| 09_empty.csv | File vuoto, da rifiutare |
| 10_before.csv / 10_after.csv | Esempio riproducibile prima e dopo |
| 10_report.xlsx | Dati puliti, anomalie e tracciabilità |
| 11_cp1252.csv | Testo Windows con caratteri accentati |

Per provare il flusso completo carica `10_before.csv`, seleziona separatore `;`, rimozione spazi, nomi in formato titolo, numeri italiani per `amount` e formato `%d/%m/%Y` per `date`. Conferma esplicitamente la rimozione dei duplicati esatti. Il report generato conserva `unknown` e la data impossibile e li segnala come anomalie: non inventa correzioni.

Il cliente può confrontare i dati originali con il risultato, vedere quali valori richiedono una decisione e ricevere un file Excel con le operazioni documentate. La dimostrazione non attesta accuratezza su dataset reali né sostituisce la verifica dei requisiti del cliente.

I file con testi simili a formule sono deliberatamente non attendibili: usa l'applicazione per verificarli ed esportarli; non aprirli direttamente in un foglio di calcolo.

La [guida per non tecnici](QUICKSTART.md) illustra l'avvio e la prova. Storico del 2 novembre: [screenshot](screenshots/README.md), [report scaricato dal browser](browser_report.xlsx) e [CSV del browser](browser_cleaned.csv) documentano uno scenario senza conversione data. Il generatore demo rigenera i file numerati, senza sovrascrivere le prove browser.
