# Sito Purple: messa online (circa 15 minuti, meglio da computer)

Il sito legge da solo il calendario ufficiale del campionato da Google Drive ogni 30 minuti.
Risultati, classifica e cambi di orario compaiono senza che nessuno tocchi niente.

## 1. Crea il repository
1. Accedi a github.com e tocca **New repository**.
2. Nome: **purple**. Visibilità: **Public**. Tocca **Create repository**.

## 2. Carica i file del sito
1. Nel repository tocca **uploading an existing file**.
2. Trascina `index.html`, `rivali.html`, `data.json`, `og.png`, `icon.png` e la cartella `scripts`.
3. Tocca **Commit changes**.

## 3. Crea l'aggiornamento automatico
1. Tocca **Add file > Create new file**.
2. Come nome scrivi esattamente: `.github/workflows/aggiorna.yml`
3. Incolla dentro il contenuto del file `aggiorna.yml` e tocca **Commit changes**.

## 4. Accendi il sito
1. Vai su **Settings > Pages**.
2. In "Branch" scegli **main** e **/ (root)**, poi **Save**.
3. Dopo 1-2 minuti il sito è su `https://TUONOME.github.io/purple/`.

## 5. Primo aggiornamento
1. Vai su **Actions**, scegli **Aggiorna calendario** e tocca **Run workflow**.
2. Dopo circa un minuto deve comparire la spunta verde. Da lì in poi gira da solo ogni 30 minuti.

Se compare una X rossa con il messaggio "non è un Excel", il file del campionato su Drive non è condiviso pubblicamente.
Serve che chi lo gestisce lo imposti su "Chiunque abbia il link".

## 6. Anteprima su WhatsApp
Apri `index.html` su GitHub, tocca la matita, sostituisci `TUONOME` con il tuo nome utente nella riga `og:image` e salva.

## 7. Condividi
Apri il link in una finestra in incognito per verificarlo, poi mettilo nella descrizione del gruppo WhatsApp.
Dal telefono si può fare **Aggiungi a schermata Home** per averlo come un'app.
