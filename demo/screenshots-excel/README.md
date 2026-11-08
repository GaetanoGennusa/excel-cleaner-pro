# Report verificato graficamente in Microsoft Excel — 8 novembre 2026

Immagini reali della sola finestra di un'istanza separata di Microsoft Excel 16.0, build 20527, aperta in sola lettura con macro disattivate. Nessun ritocco, screenshot del desktop, uso degli appunti o modifica della stampante. La finestra è stata chiusa senza salvare. L'hash del workbook è rimasto invariato.

Il report ispezionato è il download reale `reduced_report.xlsx` del giro browser `20261108T135920165082Z`, copiato senza modifiche in [qa_report.xlsx](../qa_report.xlsx). Tutti i dati sono sintetici.

| Immagine | Verifica visiva |
| --- | --- |
| [Cleaned_Data](Cleaned_Data.png) | Tre record; `001` testuale, `1234,56` numerico, `2025-02-01`; valori non validi conservati |
| [Issues](Issues.png) | Anomalie della sorgente e conversioni fallite leggibili |
| [Change_Log](Change_Log.png) | Conversioni e rimozione della copia esatta, con righe della sorgente |
| [Metadata](Metadata.png) | Configurazione, impronta sorgente e controlli; testi lunghi a capo |
| [Testi simili a formule](Untrusted_Text.png) | `=1+1`, `@SUM(A1)` e `+1+2` visualizzati come testo, non risultati |

L'ultima immagine riguarda un report separato generato dal motore da `demo/07_untrusted_text.csv`, senza trasformazioni. Non è un secondo download browser. Excel ha confermato `HasFormula = false` su tutti i fogli di entrambi i report. Registri in [docs/verification-20261108](../../docs/verification-20261108/).

Ispezione svolta dall'agente sulle catture native a zoom 100%; non è la firma di accettazione dell'utente. La cattura di una finestra Excel nascosta produceva immagini nere benché l'API rispondesse con successo: quelle immagini sono state scartate. La prova conclusiva usa una finestra visibile. Per ripetere, con Excel installato:

```powershell
powershell.exe -NoProfile -STA -File scripts/excel_visual_qa.ps1 -Visible
```

Lo script non modifica le policy PowerShell: se la policy locale blocca gli script, eseguire il controllo manualmente. Il comando apre temporaneamente una finestra Excel separata. Un'immagine non vuota richiede comunque ispezione visiva.
