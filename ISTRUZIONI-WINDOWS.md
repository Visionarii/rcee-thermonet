# Installazione sul PC Windows

Tempo: circa 20 minuti, quasi tutti di download.
Serve: Windows 10 o 11, internet, circa 3 GB liberi, Google Chrome.

## Come si usa il Terminale

1. Premi il tasto Windows, scrivi **Terminale** (su Windows 10: **PowerShell**) e premi Invio.
   Si apre una finestra con una riga tipo `PS C:\Users\nome>`.
2. Per ogni comando di questa pagina: copialo con l'icona a destra del riquadro,
   clicca nella finestra del Terminale, incolla con **Ctrl+V** e premi **Invio**.
3. Aspetta che ricompaia la riga `PS C:\...>` prima di passare al comando dopo.

## 1. Installa Git e uv (una volta sola)

```powershell
winget install --id Git.Git -e
```

```powershell
winget install --id astral-sh.uv -e
```

- Se chiede di accettare i termini delle fonti, scrivi `Y` e premi Invio.
- Se Windows chiede di consentire all'app di apportare modifiche, rispondi Sì.

Poi **chiudi il Terminale e riaprilo**, e controlla che rispondano con un numero di versione:

```powershell
git --version
```

```powershell
uv --version
```

Se `winget` non viene riconosciuto: scarica Git da https://git-scm.com/download/win
(installa lasciando tutte le scelte proposte) e installa uv con:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Se manca Google Chrome: `winget install --id Google.Chrome -e`

## 2. Scarica il progetto (una volta sola)

```powershell
git clone https://github.com/Visionarii/rcee-thermonet.git
```

```powershell
cd rcee-thermonet
```

Ogni volta che riapri il Terminale, entra prima nella cartella con `cd rcee-thermonet`.

## 3. Installa il resto (una volta sola)

```powershell
uv sync
```

Scarica Python e le librerie: 1-2 minuti.

```powershell
uv run rcee installa-ocr
```

Scarica il programma OCR (18 MB) e il modello (circa 1,8 GB): da pochi minuti a
mezz'ora, secondo la linea. Se Windows chiede di consentire l'accesso alla rete a
`llama-server`, puoi rispondere Annulla: lavora solo dentro il PC.

## 4. Diagnostica

```powershell
uv run rcee diagnostica
```

Si apre Chrome sulla pagina di login del portale e si richiude da solo, poi l'OCR
legge un'immagine di prova. In fondo deve comparire `ESITO: tutto a posto`.

Qualunque sia l'esito, apri il rapporto, seleziona tutto (Ctrl+A), copia (Ctrl+C) e
mandalo. Contiene solo i dati del PC e i tempi, nessun dato dei clienti.

```powershell
notepad dati\diagnostica.txt
```

## 5. Registrazione di una pratica

Da fare due volte, insieme a chi inserisce le pratiche: una tipo 1 e una tipo 2.

```powershell
uv run rcee registra
```

1. Si apre Chrome: fai il login al portale, poi torna al Terminale e premi Invio.
   Il login non viene registrato.
2. Chrome si riapre, con accanto una finestra che scrive codice. Controlla di essere
   già dentro il portale. Se chiede di nuovo la password, **non scriverla**: chiudi
   Chrome e avvisa.
3. Inserisci una pratica vera dall'inizio alla fine, come sempre, poi chiudi Chrome.
4. Apri la cartella con le registrazioni e manda il file appena creato:

```powershell
explorer dati\registrazioni
```

Il file contiene i clic e i valori scritti (codice catasto e numeri), non la
password. Se dentro compare il nome di un cliente, puoi sostituirlo con XXX.

## Aggiornare, quando c'è una versione nuova

```powershell
cd rcee-thermonet
```

```powershell
git pull
```

```powershell
uv sync
```

## Se qualcosa non va

- **"non è riconosciuto come nome di cmdlet"**: chiudi e riapri il Terminale. Se continua,
  il programma non si è installato: ripeti il passo 1.
- **"Failed to spawn: rcee"**: non sei nella cartella del progetto. Scrivi `cd rcee-thermonet`.
- **L'antivirus blocca llama-server**: consenti il programma. È llama.cpp ufficiale,
  scaricato da GitHub e controllato con il suo checksum.
- **"Un criterio di controllo dell'applicazione ha bloccato il file"**: è Smart App Control di
  Windows, che la prima volta blocca i programmi nuovi. Aspetta qualche minuto e riprova,
  oppure scrivi `uv run python -m rcee` al posto di `uv run rcee`.
- **Il progetto sta in un'altra cartella** (per esempio su D:): entra con `cd` seguito dal
  percorso tra virgolette, per esempio `cd "D:\Progetti\rcee-thermonet"`.
- **Qualsiasi altro errore**: copia tutto il testo del Terminale e mandalo.
