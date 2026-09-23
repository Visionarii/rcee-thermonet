"""Controllo dell'ambiente: computer, browser sul portale, OCR su un'immagine di prova.

Il risultato va in dati/diagnostica.txt, che non contiene dati personali.
"""

import time
from datetime import datetime

from playwright.sync_api import sync_playwright

from . import ocr
from .browser import apri_chrome
from .config import DATI, URL_PORTALE, cartella
from .sistema import info_sistema


def prova_browser(headless: bool) -> tuple[bool, list[str]]:
    inizio = time.monotonic()
    try:
        with sync_playwright() as p:
            contesto, nome = apri_chrome(p, cartella("chrome"), headless)
            try:
                pagina = contesto.pages[0] if contesto.pages else contesto.new_page()
                risposta = pagina.goto(URL_PORTALE, wait_until="domcontentloaded", timeout=60_000)
                stato = risposta.status if risposta else None
                titolo = pagina.title()
                agente = pagina.evaluate("navigator.userAgent")
            finally:
                contesto.close()
    except Exception as errore:  # la diagnostica riporta l'errore invece di fermarsi
        return False, [f"ERRORE: {errore}"]
    versione = next(
        (parte for parte in agente.split() if parte.startswith(("Chrome/", "HeadlessChrome/"))), agente
    )
    return stato is not None and stato < 400, [
        f"Browser: {nome} ({versione})",
        f"Portale: {URL_PORTALE}",
        f"Risposta: HTTP {stato}, titolo «{titolo}»",
        f"Tempo totale: {time.monotonic() - inizio:.1f} s",
    ]


def prova_ocr() -> tuple[bool, list[str]]:
    try:
        eseguibile = ocr.trova_llama_server()
    except FileNotFoundError as errore:
        return False, [f"ERRORE: {errore}"]
    if eseguibile is None:
        return False, ["llama-server non trovato. Esegui prima: uv run rcee installa-ocr"]
    modello, mmproj = ocr.percorsi_modello()
    if not (modello.is_file() and mmproj.is_file()):
        return False, ["Modello non scaricato. Esegui prima: uv run rcee installa-ocr"]
    log = cartella("log") / "llama-server.log"
    righe = [f"llama-server: {eseguibile}", f"Versione: {ocr.versione_llama(eseguibile)}"]
    try:
        with ocr.ServerOCR(eseguibile, modello, mmproj, log) as server:
            inizio = time.monotonic()
            testo = server.leggi(ocr.immagine_prova())
            secondi = time.monotonic() - inizio
    except Exception as errore:  # idem: si riporta, con il log di llama-server
        return False, righe + [f"ERRORE: {errore}", f"Log: {log}"]
    mancanti = ocr.valori_mancanti(testo, ocr.VALORI_PROVA)
    return not mancanti, righe + [
        f"Caricamento del modello: {server.secondi_avvio:.1f} s",
        f"Lettura dell'immagine di prova: {secondi:.1f} s",
        "Valori letti: tutti" if not mancanti else f"Valori NON letti: {', '.join(mancanti)}",
        "Testo letto:",
        *(f"    {riga}" for riga in testo.strip().splitlines()[:12]),
    ]


def esegui(headless: bool = False) -> int:
    DATI.mkdir(parents=True, exist_ok=True)
    prove = {
        "BROWSER E PORTALE": prova_browser(headless),
        "OCR": prova_ocr(),
    }
    righe = [f"DIAGNOSTICA rcee-thermonet, {datetime.now():%d/%m/%Y %H:%M}", "", "== COMPUTER =="]
    righe += [f"{voce}: {valore}" for voce, valore in info_sistema(DATI).items()]
    for titolo, (riuscita, dettagli) in prove.items():
        righe += ["", f"== {titolo}: {'OK' if riuscita else 'PROBLEMA'} ==", *dettagli]
    tutto_ok = all(riuscita for riuscita, _ in prove.values())
    righe += ["", "ESITO: tutto a posto" if tutto_ok else "ESITO: ci sono problemi, vedi sopra"]
    testo = "\n".join(righe)
    rapporto = DATI / "diagnostica.txt"
    rapporto.write_text(testo + "\n", encoding="utf-8")
    print(testo)
    print(f"\nRapporto salvato in: {rapporto}")
    return 0 if tutto_ok else 1
