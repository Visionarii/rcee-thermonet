# rcee-thermonet: contesto per Claude

Rispondi in italiano, in modo semplice: chi usa questo PC non è un programmatore.
Lo sviluppo continua su questo PC Windows di prova (prima era sul Mac): qui si scrive,
si prova e si fa push. Il PC dell'ufficio riceverà solo la versione finita.

## Cos'è

Automazione dei rapporti RCEE (tipo 1 caldaie, tipo 2 climatizzatori e pompe di calore)
sul portale ThermoNET di Nuova Salento Energia. Oggi l'operatrice impiega 8 minuti e
20 secondi a pratica; l'obiettivo è circa 1 minuto di sua attenzione. Volume: 10-30
pratiche al giorno.

## Flusso da costruire (concordato)

1. Il tecnico manda al bot Telegram la foto del rapportino firmato. In didascalia:
   telefono del cliente e "paga" o "non paga" (sul modulo non ci sono). Il bot accetta
   solo gli account Telegram autorizzati (elenco di user ID).
2. Bot e script sono un solo programma su questo PC. Legge la foto con l'OCR: tipo 1 o 2,
   codice catasto, valori, spunte. Se la foto è illeggibile o un valore è fuori
   intervallo, risponde subito al tecnico.
3. Playwright apre il portale col profilo Chrome dedicato, fa il login se serve, compila,
   allega la foto (PDF o JPG, massimo 1 MB) e salva SENZA chiudere.
4. Rilegge dal portale i dati salvati e li manda all'operatrice su Telegram, con il
   ritaglio della foto. Lei risponde OK oppure la correzione ("O2 3,8"): lo script
   corregge la bozza e rimanda l'anteprima.
5. Dopo l'OK chiude la pratica (la chiusura è definitiva). Se il portale segnala
   anomalie si ferma e chiede. Scarica rapportino e ricevuta, li manda al cliente su
   WhatsApp Web col testo fisso, e scrive su Telegram l'esito o il motivo dello stop.

Principi: nel dubbio ci si ferma, non si chiude mai. Se la sessione scade dopo il
salvataggio, si riprende la bozza esistente, non se ne crea una seconda.

## Stato e prossimi passi

Fatto (fase 1): `uv run rcee diagnostica | installa-ocr | registra | esplora`.
Diagnostica su questo PC: tutto a posto (OCR sull'immagine di prova: 27 s).

Mancano, in quest'ordine:
- [ ] Registrazioni con l'operatrice (`uv run rcee registra`): una pratica tipo 1 e una
      tipo 2 fino alla chiusura. Controllare se nel secondo browser si è già dentro il
      portale: se chiede di nuovo la password, il login va escluso in un altro modo
      (pulsante Record dell'Inspector di Playwright).
- [ ] Dall'operatrice: testo esatto del messaggio WhatsApp e della frase che copia
      dall'email del portale; tipo del suo account (Profilo utente: Tecnico o Amministrativo).
- [ ] Dai tecnici: 10-20 foto di rapportini già inseriti (tipo 1 e 2), come arrivano su
      Telegram, e con cosa li stampano (se esiste un file digitale, niente OCR).
      Le foto vanno in `dati\foto-prova\`, mai su GitHub.
- [ ] Lettura delle foto: prova sulle foto vere, confronto campo per campo con i valori
      già sul portale. Misurare i tempi: se troppo lenti, leggere solo le zone utili.
- [ ] Bozza sul portale dalle registrazioni (all'inizio la chiude l'operatrice a mano).
- [ ] Bot Telegram, poi chiusura e download dei PDF, poi WhatsApp Web.
- [ ] Installazione sul PC dell'ufficio: un comando più una lista di controllo; avvio
      all'accesso con l'Utilità di pianificazione (non come servizio: serve Chrome
      visibile), niente sospensione, controllo del portale ogni mattina.

## Cosa sappiamo del portale

- App manutentori: https://nuovasalentoenergia.thermonet.parsec326.cloud/web (Login.aspx),
  ASP.NET WebForms con DevExpress XAF. Login con utente e password, niente captcha.
- Gli id degli elementi contengono una parte che cambia (`v0_NNNN`): cercare gli elementi
  per etichetta visibile o per la fine dell'id (es. `[id$="dviUserName_Edit_I"]`).
- Menu: Catasto impianti, Libretti impianto, RCEE Tipo 1-4, Ricevute RCEE Tipo 1-4,
  Richieste (pagina dopo il login), Portafoglio (bollini), Importazioni > Tracciati RCEE
  ("Importa tracciato": licenza non attiva, non si usa), Help > Guida.
- Allegati: dal rapporto salvato, "Allegati" > "Collega" > "Nuovo"; si può fare anche dopo
  la chiusura.
- La ditta può creare utenti: Tecnico (firma gli RCEE) o Amministrativo (solo caricamento
  dati). Un account dedicato allo script evita conflitti di sessione con l'operatrice.
- Rischio: il login con password vale solo per gli enti senza SPID.

## Valori (dalla trascrizione del video, tipo 1 caldaia a gas)

- Fissi: responsabile = proprietario (se no, stop e chiedere); documentazione
  sì/sì/sì/no; sezione C già compilata; sezione D standard con reflusso = no; l'impianto
  può funzionare = sì. Le spunte vanno comunque confrontate con la foto: se una è diversa,
  stop.
- Onere: se paga, in osservazioni "bollino virtuale 20€"; se non paga, osservazioni vuote.
- Intervalli: fumi 40-250 °C; O2 0-15 %; CO2 0-15 %; rendimento sopra il minimo di legge
  e sotto 105 %; CO sotto qualche migliaio di ppm. Fuori intervallo: stop.
- Tipo 2: 8 temperature per circuito (surriscaldamento, sottoraffreddamento, condensazione,
  evaporazione, ingresso e uscita lato esterno e lato utenze), modalità
  raffrescamento/riscaldamento; intervalli da chiedere ai tecnici.
- Il tipo si riconosce dal titolo stampato: "TIPO 1 (gruppi termici)" o "TIPO 2 (gruppi frigo)".

## Scelte già fatte (non riproporre alternative)

- Browser: Playwright con profilo Chrome dedicato in `dati/` (non il profilo dell'utente).
- OCR: PaddleOCR-VL 1.6 servito da llama.cpp build b10964, in locale.
- WhatsApp: WhatsApp Web nel browser, niente WhatsApp Cloud API. Chrome visibile, pause
  umane, tetto giornaliero di messaggi, stop al primo avviso di WhatsApp. Il controllo
  "nome della chat = responsabile" funziona solo se il numero è salvato in rubrica.
- Niente agenti AI nel cloud sul portale: i dati dei clienti restano sul PC.
- Le foto di Telegram arrivano compresse a 1280 pixel: se l'OCR sbaglia, farle inviare "come file".

## Particolarità di questo PC

- winget non funziona: uv è stato installato con l'installatore ufficiale.
- Smart App Control è attivo: la prima volta blocca `rcee` e `llama-server`. Si aspetta
  qualche minuto, oppure si usa `uv run python -m rcee <comando>`.

## Regole

- Il repository è pubblico: mai dati di clienti, nomi di persone, password o sessioni.
  Tutto ciò che è locale sta in `dati/`, che git ignora.
- Nelle prove sul portale non premere mai Chiusura, Convalida o Elimina: le pratiche vere
  le chiude una persona. Nelle prove di WhatsApp si usa un numero personale.
- Commit piccoli, `uv run pytest` verde prima di ogni push.
