"""Apertura di Chrome con un profilo dedicato allo script.

Da Chrome 136 non si può pilotare il profilo principale dell'utente: serve un
profilo a parte, che conserva il login al portale e, più avanti, WhatsApp Web.
"""

from pathlib import Path

from playwright.sync_api import BrowserContext, Error, Playwright

GOOGLE_CHROME = "Google Chrome"
CHROMIUM = "Chromium di Playwright"


def apri_chrome(
    p: Playwright, profilo: Path, headless: bool = False
) -> tuple[BrowserContext, str]:
    """Apre il browser sul profilo indicato: Google Chrome se installato, altrimenti Chromium."""
    profilo.mkdir(parents=True, exist_ok=True)
    try:
        contesto = p.chromium.launch_persistent_context(
            profilo, channel="chrome", headless=headless
        )
        return contesto, GOOGLE_CHROME
    except Error as errore:
        if "is not found" not in str(errore):
            raise
    return p.chromium.launch_persistent_context(profilo, headless=headless), CHROMIUM
