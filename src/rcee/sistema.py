"""Informazioni sul computer, per capire se regge browser e OCR."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

import psutil

_POWERSHELL = ["powershell", "-NoProfile", "-Command"]


def _righe(comando: list[str]) -> list[str]:
    """Righe non vuote dell'output di un comando; lista vuota se il comando fallisce."""
    try:
        uscita = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=60,
            check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [riga.strip() for riga in uscita.splitlines() if riga.strip()]


def nome_processore() -> str:
    if sys.platform == "win32":
        righe = _righe(_POWERSHELL + ["(Get-CimInstance Win32_Processor).Name"])
    elif sys.platform == "darwin":
        righe = _righe(["sysctl", "-n", "machdep.cpu.brand_string"])
    else:
        righe = [platform.processor()]
    return "; ".join(riga for riga in righe if riga) or "n/d"


def nome_scheda_grafica() -> str:
    if sys.platform == "win32":
        righe = _righe(_POWERSHELL + ["(Get-CimInstance Win32_VideoController).Name"])
    elif sys.platform == "darwin":
        righe = [
            riga.split(":", 1)[1].strip()
            for riga in _righe(["system_profiler", "SPDisplaysDataType"])
            if riga.startswith("Chipset Model:")
        ]
    else:
        righe = []
    return "; ".join(righe) or "n/d"


def info_sistema(cartella: Path) -> dict[str, str]:
    """Dati del computer da riportare nella diagnostica (nessun dato personale)."""
    return {
        "Sistema": platform.platform(),
        "Python": platform.python_version(),
        "Processore": nome_processore(),
        "Core": f"{psutil.cpu_count(logical=False) or '?'} fisici, {psutil.cpu_count()} logici",
        "RAM": f"{psutil.virtual_memory().total / 2**30:.1f} GB",
        "Scheda grafica": nome_scheda_grafica(),
        "Spazio libero su disco": f"{shutil.disk_usage(cartella).free / 2**30:.0f} GB",
    }
