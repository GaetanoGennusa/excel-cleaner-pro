# Video catalogo prodotti — registrazione disponibile

Il [video reale](../demo/product_catalog/demo_catalogo.webm) dura **38 secondi**, è muto e mostra il catalogo sintetico nell'app: upload, regole esplicite, anteprima, anomalie, log e download effettivi. Registrato automaticamente in Chromium a 1440 × 1000, movimento ridotto, nessun taglio o accelerazione. Le pause servono a leggere. Non include l'apertura in Excel, documentata separatamente con catture native.

Per presentarlo puoi spiegare: «Questo è un catalogo inventato con 200 righe. Scelgo formati e trasformazioni, conservo i codici e rimuovo soltanto sei copie esatte confermate. Le quattro coppie simili e i valori dubbi restano da valutare. Il report contiene le operazioni e la configurazione.» Il video non ha questa voce fuori campo incorporata.

La [pagina portfolio](../demo/product_catalog/index.html) include il lettore. Procedura di registrazione e verifiche: [CATALOG_DEMO_QA.md](CATALOG_DEMO_QA.md). La scaletta seguente resta una proposta per una futura versione parlata da 45–60 secondi sul caso minimo.

---

# Scaletta precedente — proposta da 45–60 secondi

Obiettivo: mostrare il flusso reale su dati sintetici, con un ritmo calmo e un solo caso. Registrare soltanto ciò che l'app effettivamente esegue. Preparare prima le regole, provare la scaletta e nascondere notifiche o dati personali del desktop.

| Tempo | Schermo reale | Voce proposta |
| --- | --- | --- |
| 0–7 s | Titolo app e `demo/10_before.csv` | «Excel Cleaner Pro pulisce piccoli file Excel e CSV mantenendo visibili le scelte. Qui uso soltanto dati inventati.» |
| 7–16 s | Upload, separatore `;`, Carica dataset, overview | «Questo file contiene spazi superflui, importi italiani, date da interpretare e una riga duplicata.» |
| 16–29 s | Regole già predisposte, conferma duplicati | «Scelgo le colonne da trattare, il formato numerico italiano e giorno, mese, anno. La rimozione dei duplicati richiede una conferma.» |
| 29–42 s | Applica, confronto prima/dopo e anomalie | «L'anteprima mostra il risultato. I codici con zeri iniziali restano intatti. La data impossibile e l'importo sconosciuto non vengono indovinati: restano segnalati.» |
| 42–53 s | Prepara esportazioni, download effettivo, report aperto dopo verifica manuale | «Il report Excel include dati puliti, anomalie, log e configurazione. Il cliente può controllare le modifiche.» |
| 53–60 s | Ritorno al titolo o risultato | «Il servizio proposto copre un file fino a mille righe, con regole concordate e una revisione limitata.» |

Non mostrare l'apertura del report in Excel finché non è stata davvero eseguita e verificata. In alternativa, terminare sul download reale e dichiarare che l'apertura manuale è da completare. Non usare animazioni che simulino risultati o velocità dell'elaborazione. Non mostrare prezzi come risultati economici: l'eventuale fascia sperimentale EUR 25–40 è una proposta da validare.

Per una versione in inglese, mantenere gli stessi passaggi e dichiarare «synthetic demonstration» nel parlato o in una breve didascalia. Esportare il video solo dopo aver controllato leggibilità del testo e assenza di informazioni personali.
