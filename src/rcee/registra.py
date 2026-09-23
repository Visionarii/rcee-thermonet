"""Registrazione di una pratica sul portale con Playwright codegen.

Il login si fa prima, in una finestra che non viene registrata: il file
prodotto contiene solo i clic e i valori scritti durante la pratica.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Error, sync_playwright

from .browser import GOOGLE_CHROME, apri_chrome
from .config import URL_PORTALE, cartella


def comando_codegen(url: str, sessione: Path, uscita: Path, chrome: bool) -> list[str]:
    comando = [
        sys.executable, "-m", "playwright", "codegen",
        "--target", "python", "-o", str(uscita), "--load-storage", str(sessione),
    ]
    if chrome:
        comando += ["--channel", "chrome"]
    return comando + [url]


def esegui() -> int:
    sessione = cartella("sessioni") / "registrazione.json"
    uscita = cartella("registrazioni") / f"pratica-{datetime.now():%Y%m%d-%H%M}.py"

    print("PASSO 1. Si apre Chrome sul portale: fai il login. Questa parte NON viene registrata.")
    try:
        with sync_playwright() as p:
            contesto, nome = apri_chrome(p, cartella("chrome-registrazione"))
            try:
                pagina = contesto.pages[0] if contesto.pages else contesto.new_page()
                pagina.goto(URL_PORTALE)
                input("Quando sei dentro il portale, torna qui e premi Invio... ")
                url = pagina.url
                contesto.storage_state(path=sessione)
            finally:
                contesto.close()
    except Error:
        print("Il browser è stato chiuso prima di premere Invio: rilancia il comando.")
        return 1

    print("\nPASSO 2. Si riapre il browser già dentro il portale: da qui ogni clic viene registrato.")
    print("Inserisci una pratica vera dall'inizio alla fine, poi chiudi la finestra del browser.")
    print("Se ti chiede di nuovo la password, NON scriverla: chiudi la finestra e avvisami.")
    try:
        subprocess.run(comando_codegen(url, sessione, uscita, nome == GOOGLE_CHROME), check=True)
    finally:
        sessione.unlink(missing_ok=True)
    if not uscita.is_file():
        print("Nessuna registrazione salvata.")
        return 1
    print(f"\nRegistrazione salvata in: {uscita}")
    return 0
