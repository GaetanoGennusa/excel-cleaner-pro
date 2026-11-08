# Pubblicazione del repository su GitHub

Richiesta dell'utente: repository **pubblico**, nome `excel-cleaner-pro`, per il portfolio. La pubblicazione del codice è distinta dall'hosting dell'applicazione o della pagina demo. Nessuna licenza open source viene aggiunta automaticamente: la scelta della licenza resta separata.

## Pubblicazione completata — 8 novembre 2026

Repository: **[GaetanoGennusa/excel-cleaner-pro](https://github.com/GaetanoGennusa/excel-cleaner-pro)**, visibilità pubblica, branch `main`. Accesso tramite Git Credential Manager e creazione mediante API ufficiale GitHub, senza installazioni globali o credenziali nei file. Caricamento con Git e confronto dell'hash locale con `refs/heads/main` remoto riusciti.

L'origine locale è `https://github.com/GaetanoGennusa/excel-cleaner-pro.git`; `main` segue `origin/main`. Per caricare nuovi commit basta `git push`. I passaggi di prima creazione qui sotto sono conservati come riferimento: non creare un altro repository o aggiungere nuovamente `origin`.

Non è stato attivato GitHub Pages né pubblicata l'applicazione Streamlit su un server. La demo interattiva HTML si apre dopo aver scaricato o clonato il progetto. Il riscontro dell'utente sulla demo locale è stato positivo per la verifica visiva; non costituisce accettazione di tutti i controlli manuali o di un dataset cliente.

## Preparazione locale

- Codice, test, documentazione e dati sintetici sono versionati.
- `.venv/`, cache, caricamenti, `outputs/`, `.env` e segreti Streamlit sono esclusi da Git.
- Controllata la cronologia locale: nessun percorso di tali cartelle trovato tra i file storici; nessuna corrispondenza ai formati di credenziali cercati nei blob testuali. Questo controllo non è un audit esaustivo.
- README italiano con screenshot reale e panoramica inglese in `README.en.md`.
- Il file più grande è il video sintetico, circa 3,55 MB. La cronologia conserva gli autori tecnici originali dei commit, senza riscritture.
- La suite locale più recente ha superato 54 test; evidenze browser e native in `docs/CATALOG_DEMO_QA.md`.

## Collegamento e caricamento

Prima serve autenticarsi nel proprio account. Su questo PC Git Credential Manager è già installato:

```powershell
git credential-manager github login --browser
```

Completa l'accesso nel browser. Non inserire password o token nei file del progetto, negli URL remoti o nella chat.

Se crei il repository dall'interfaccia GitHub, scegli `excel-cleaner-pro`, visibilità Public, e lascia disattivate le opzioni che aggiungono README, `.gitignore` o licenza: questi contenuti sono già gestiti nella cronologia locale. Collega poi il repository vuoto con l'URL HTTPS effettivo del tuo account:

```powershell
git remote add origin https://github.com/TUO-ACCOUNT/excel-cleaner-pro.git
git push -u origin main
```

`TUO-ACCOUNT` è un segnaposto. Non aggiungere una seconda origine se esiste già e non usare force push. Dopo il caricamento, confrontare il commit `main` remoto con `git rev-parse HEAD` e verificare la visibilità pubblica e il rendering del README.

Per i successivi aggiornamenti, dalla stessa cartella:

```powershell
git status
git add -- PERCORSI-VERIFICATI
git commit -m "Descrizione delle modifiche"
git push
```

L'identità autore Git va configurata dall'utente con il proprio nome e un'email scelta consapevolmente; i commit storici dell'agente mantengono l'identità tecnica. Non caricare dati reali di clienti per mostrare la demo.

Riferimenti ufficiali: [codice locale su GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github), [creazione repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository).
