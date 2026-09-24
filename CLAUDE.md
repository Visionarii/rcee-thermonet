# rcee-thermonet: contesto per Claude

Rispondi in italiano, in modo semplice: chi usa questo PC non è un programmatore.

## Cos'è

Automazione dei rapporti RCEE (tipo 1 caldaie, tipo 2 climatizzatori) sul portale
ThermoNET di Nuova Salento Energia (https://nuovasalentoenergia.thermonet.parsec326.cloud/web,
DevExpress XAF, login con utente e password, niente captcha).

Flusso da costruire: il tecnico manda su Telegram la foto del rapportino (dati stampati)
con telefono del cliente e "paga"/"non paga" → OCR in locale → lo script compila la
pratica sul portale e la salva in bozza → anteprima all'operatrice su Telegram → dopo
l'OK chiude la pratica, scarica rapportino e ricevuta → li manda al cliente su WhatsApp Web.

## Stato: fase 1

`uv run rcee diagnostica | installa-ocr | registra | esplora` (vedi README.md).
Sviluppo sul Mac; su Windows si installa e si prova seguendo ISTRUZIONI-WINDOWS.md.

## Scelte già fatte (non riproporre alternative)

- Browser: Playwright con profilo Chrome dedicato in `dati/` (non il profilo dell'utente).
- OCR: PaddleOCR-VL 1.6 servito da llama.cpp build b10964, in locale.
- WhatsApp: WhatsApp Web nel browser, niente WhatsApp Cloud API.
- Niente agenti AI nel cloud sul portale: i dati dei clienti restano sul PC.
- Import XML del portale: esiste, ma la licenza non è attiva; si lavora sulle pagine.

## Regole

- Il repository è pubblico: mai dati di clienti, nomi di persone, password o sessioni.
  Tutto ciò che è locale sta in `dati/`, che git ignora.
- Nelle prove sul portale non premere mai Chiusura, Convalida o Elimina: le pratiche
  vere le chiude una persona. Nelle prove di WhatsApp si usa un numero personale.
- Su questo PC di solito si installa e si prova: i risultati (per esempio il testo di
  `dati\diagnostica.txt`) vanno riportati a chi sviluppa sul Mac. Se serve una
  correzione, commit piccolo e push subito.
