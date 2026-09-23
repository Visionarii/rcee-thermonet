# Installazione sul PC Windows

I comandi si scrivono nel Terminale: tasto Windows, scrivi "Terminale", Invio.
Si apre PowerShell.

## 1. Programmi di base (una volta sola)

```
winget install --id Git.Git -e
winget install --id astral-sh.uv -e
```

Se Google Chrome non c'è: `winget install --id Google.Chrome -e`.
Se winget chiede di accettare i termini delle sue fonti, rispondi `Y`.
Poi chiudi il Terminale e riaprilo, così vede i programmi appena installati.

## 2. Scarica il progetto (una volta sola)

```
cd $HOME
git clone https://github.com/Visionarii/rcee-thermonet.git
cd rcee-thermonet
```

Il repository è privato, quindi Git chiede di accedere a GitHub. Se il PC lo usano
anche altre persone, non usare il tuo account: crea su GitHub un token di sola
lettura valido solo per questo repository (Settings, Developer settings,
Fine-grained tokens, permesso "Contents: Read-only") e incollalo quando Git lo chiede.

## 3. Installa il resto

```
uv sync
uv run rcee installa-ocr
```

Il secondo comando scarica llama.cpp (18 MB) e il modello OCR (circa 1,8 GB):
la prima volta ci vuole qualche minuto.

## 4. Diagnostica

```
uv run rcee diagnostica
```

Si apre Chrome sul portale e si richiude da solo, poi l'OCR legge un'immagine di prova.
Alla fine manda il file `dati\diagnostica.txt`: contiene solo i dati del computer
e i tempi, nessun dato dei clienti.

## 5. Registrazione di una pratica (con Vale)

```
uv run rcee registra
```

1. Si apre Chrome sul portale: Vale fa il login, poi torna al Terminale e preme Invio.
   Il login non viene registrato.
2. Si riapre Chrome già dentro il portale, con accanto una finestra che scrive il codice.
   Vale inserisce una pratica vera dall'inizio alla fine, come fa sempre, poi chiude Chrome.
3. Se durante la registrazione il portale chiede di nuovo la password, non scriverla:
   chiudi Chrome e avvisa.

Il file finisce in `dati\registrazioni\`. Contiene i clic e i valori scritti
(codice catasto e numeri), non la password.

## Aggiornare

Quando c'è una versione nuova:

```
cd $HOME\rcee-thermonet
git pull
uv sync
```
