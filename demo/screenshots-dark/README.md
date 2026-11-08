# Schermate dell'interfaccia attuale (tema scuro) — 8 novembre 2026

App Streamlit reale in Chromium headless 155.0.8059.12, dati completamente sintetici. Tutte le immagini sono copiate senza ritocchi dal giro `scripts.browser_qa` identificato da `20261108T135920165082Z`. Le schermate desktop usano «riduci animazioni», quindi mostrano lo stato finale delle animazioni; quelle di tablet e telefono hanno le animazioni attive.

| File | Contenuto |
| --- | --- |
| [01_upload.png](01_upload.png) | Desktop 1440 px: intestazione, barra delle fasi e caricamento |
| [02_overview.png](02_overview.png) | Profilo della sorgente `10_before.csv` |
| [03_preview.png](03_preview.png) | Confronto prima/dopo e controlli, dopo spazi, title, numeri italiani, formato data e deduplica confermata |
| [04_export.png](04_export.png) | Export dopo i download reali |
| [05_mobile_upload.png](05_mobile_upload.png) | Telefono 390 × 844: schermata iniziale |
| [05_mobile_rules.png](05_mobile_rules.png) | Telefono: regole con etichette complete |
| [05_mobile_preview.png](05_mobile_preview.png) | Telefono: anteprima |
| [05_mobile_export.png](05_mobile_export.png) | Telefono: export dopo il download |
| [09_tablet_upload.png](09_tablet_upload.png) | Tablet 900 × 1100: schermata iniziale |
| [09_tablet_rules.png](09_tablet_rules.png) | Tablet: regole e formati per colonna |
| [09_tablet_preview.png](09_tablet_preview.png) | Tablet: anteprima |
| [09_tablet_export.png](09_tablet_export.png) | Tablet: export |

Il risultato desktop corrisponde al [report scaricato](../qa_report.xlsx) e al [CSV](../qa_cleaned.csv): tre righe, `001`, `1234.56`, `2025-02-01`, con `unknown` e `31/02/2025` conservati e segnalati. Le viewport strette di Chromium non equivalgono a un telefono reale. Le [catture native di Excel](../screenshots-excel/README.md) sono raccolte separatamente.

Riferimenti: [rapporto QA finale](../../docs/FINAL_QA_REPORT.md), [risultati browser](../../docs/verification-20261108/browser_results.json), [controllo dei file scaricati](../../docs/verification-20261108/artifact_validation.json). Storico: [variante chiara premium](../screenshots-premium/README.md), [restyling chiaro](../screenshots-redesign/README.md), [prime schermate](../screenshots/README.md).
