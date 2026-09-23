"""Percorsi e impostazioni comuni.

Tutto ciò che è locale al computer (profili Chrome, sessioni, modelli, log,
registrazioni) sta in `dati/`, che git ignora: non deve mai finire su GitHub.
"""

import os
from pathlib import Path

_RADICE = Path(__file__).resolve().parents[2]

DATI = Path(os.environ.get("RCEE_DATI", _RADICE / "dati"))
URL_PORTALE = os.environ.get(
    "RCEE_URL_PORTALE", "https://nuovasalentoenergia.thermonet.parsec326.cloud/web"
)


def cartella(nome: str) -> Path:
    """Restituisce una sottocartella di `dati/`, creandola se manca."""
    percorso = DATI / nome
    percorso.mkdir(parents=True, exist_ok=True)
    return percorso
