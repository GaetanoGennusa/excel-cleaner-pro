# Screenshot reali — dimostrazione sintetica

Acquisizioni della vera applicazione Streamlit in Chromium headless 155.0.8059.12, eseguite il 2 novembre 2026 (Europe/Rome) su dati completamente inventati. Nessuna immagine generata, fotomontaggio o interfaccia ricostruita. Le PNG sono copiate integralmente dagli output del driver, senza ritocchi.

| File | Contenuto realmente acquisito |
| --- | --- |
| [01_upload.png](01_upload.png) | Schermata iniziale e caricamento |
| [02_overview.png](02_overview.png) | Dataset sintetico di quattro righe, profilo e regole |
| [03_preview.png](03_preview.png) | Prima/dopo: tre righe dopo deduplica confermata e controlli |
| [04_export.png](04_export.png) | Download e area export della sessione verificata |
| [05_mobile.png](05_mobile.png) | Schermata iniziale a 390 × 844; non certifica tutto il flusso su smartphone |

Configurazione mostrata: compressione spazi, `title` per name, numeri italiani per amount, rimozione confermata dei duplicati esatti. **Nessuna conversione data** nello scenario browser. Le date ambigue restano quindi identiche alla sorgente; sono state convertite nell'altro esempio `10_report.xlsx` con una configurazione diversa, verificata tramite motore e AppTest. La selezione del formato data nel browser richiede ancora verifica manuale.

Il risultato corrisponde a [browser_report.xlsx](../browser_report.xlsx) e [browser_cleaned.csv](../browser_cleaned.csv), scaricati realmente tramite i pulsanti dell'app. Non è stata acquisita un'apertura grafica in Excel/LibreOffice: va fatta manualmente. Non usare queste immagini per dichiarare una verifica nativa del workbook o risultati su dati di clienti.

Evidenze riproducibili: [risultati browser](../../docs/browser_results.json), [validazione dei download](../../docs/browser_artifact_validation.json), [rapporto finale](../../docs/FINAL_QA_REPORT.md) e [istruzioni del driver](../../docs/BROWSER_QA.md).
