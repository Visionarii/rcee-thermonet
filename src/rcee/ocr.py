"""Lettura delle immagini con PaddleOCR-VL servito in locale da llama.cpp.

Su Mac e Windows gira lo stesso programma (llama-server, stessa versione) con
lo stesso file del modello, così le prove fatte sul Mac valgono anche sul PC
dell'ufficio. Le immagini non escono mai dal computer.
"""

import base64
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Self

from PIL import Image, ImageDraw, ImageFont

from .config import cartella

REPO_MODELLO = "PaddlePaddle/PaddleOCR-VL-1.6-GGUF"
FILE_MODELLO = "PaddleOCR-VL-1.6-GGUF.gguf"
FILE_MMPROJ = "PaddleOCR-VL-1.6-GGUF-mmproj.gguf"
SHA256_MODELLO = {
    FILE_MODELLO: "f3ae46ec885050acf4b3d31944431e1fd90d50664fb09126af4a3c050ba14ee8",
    FILE_MMPROJ: "204d757d7610d9b3faab10d506d69e5b244e32bf765e2bab2d0167e65e0a058a",
}

# Build di llama.cpp fissata: la stessa del Mac di sviluppo (brew, build 10964).
VERSIONE_LLAMA = "b10964"
PACCHETTI_LLAMA = {
    ("Windows", "AMD64"): (
        "llama-b10964-bin-win-cpu-x64.zip",
        "917f39c076402c421224824607397af20f53625a60defc20e8dd22446bf4c5d7",
    ),
}
URL_RELEASE_LLAMA = (
    "https://github.com/ggml-org/llama.cpp/releases/download/{versione}/{file}"
)

RIGHE_PROVA = [
    "RAPPORTO DI CONTROLLO DI EFFICIENZA ENERGETICA TIPO 1 (gruppi termici)",
    "Temperatura fumi: 55,0 °C    Temperatura aria comburente: 28,0 °C",
    "O2: 3,5 %    CO2: 9,7 %    CO nei fumi secchi: 104 ppm",
    "Rendimento di combustione: 98,8 %    Rendimento minimo di legge: 92 %",
]
VALORI_PROVA = ["TIPO 1", "55,0", "28,0", "3,5", "9,7", "104", "98,8", "92"]

# Le chiamate al server locale non devono passare da un eventuale proxy aziendale.
_SENZA_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _sha256(percorso: Path) -> str:
    impronta = hashlib.sha256()
    with percorso.open("rb") as file:
        for blocco in iter(lambda: file.read(1 << 20), b""):
            impronta.update(blocco)
    return impronta.hexdigest()


def percorsi_modello() -> tuple[Path, Path]:
    base = cartella("modelli")
    return base / FILE_MODELLO, base / FILE_MMPROJ


def scarica_modello() -> tuple[Path, Path]:
    """Scarica (o ritrova) i due file del modello e ne verifica l'integrità."""
    from huggingface_hub import hf_hub_download

    for nome, atteso in SHA256_MODELLO.items():
        percorso = Path(
            hf_hub_download(REPO_MODELLO, nome, local_dir=cartella("modelli"))
        )
        if _sha256(percorso) != atteso:
            percorso.unlink()
            raise RuntimeError(
                f"{nome}: il file scaricato è corrotto. Rilancia il comando."
            )
    return percorsi_modello()


def trova_llama_server() -> Path | None:
    """Cerca llama-server: variabile RCEE_LLAMA_SERVER, poi dati/llama, poi il PATH."""
    if variabile := os.environ.get("RCEE_LLAMA_SERVER"):
        percorso = Path(variabile)
        if not percorso.is_file():
            raise FileNotFoundError(
                f"RCEE_LLAMA_SERVER punta a un file che non esiste: {percorso}"
            )
        return percorso
    nome = "llama-server.exe" if platform.system() == "Windows" else "llama-server"
    if trovati := sorted(cartella("llama").rglob(nome)):
        return trovati[0]
    nel_path = shutil.which("llama-server")
    return Path(nel_path) if nel_path else None


def installa_llama() -> Path:
    """Restituisce llama-server; su Windows, se manca, scarica la build fissata."""
    if trovato := trova_llama_server():
        return trovato
    sistema = (platform.system(), platform.machine())
    if sistema not in PACCHETTI_LLAMA:
        raise RuntimeError(
            f"llama-server non trovato e nessun pacchetto previsto per {' '.join(sistema)}. "
            "Su Mac: brew install llama.cpp"
        )
    nome, atteso = PACCHETTI_LLAMA[sistema]
    base = cartella("llama")
    archivio = base / nome
    print(f"Scarico {nome} da GitHub (llama.cpp {VERSIONE_LLAMA})...")
    urllib.request.urlretrieve(
        URL_RELEASE_LLAMA.format(versione=VERSIONE_LLAMA, file=nome), archivio
    )
    if _sha256(archivio) != atteso:
        archivio.unlink()
        raise RuntimeError(
            f"{nome}: il file scaricato è corrotto. Rilancia il comando."
        )
    with zipfile.ZipFile(archivio) as contenuto:
        contenuto.extractall(base / VERSIONE_LLAMA)
    archivio.unlink()
    if trovato := trova_llama_server():
        return trovato
    raise RuntimeError(f"llama-server.exe non trovato dentro {nome}")


def versione_llama(eseguibile: Path) -> str:
    try:
        uscita = subprocess.run(
            [str(eseguibile), "--version"],
            capture_output=True,
            text=True,
            errors="replace",
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as errore:
        return f"n/d ({errore})"
    righe = (uscita.stdout + uscita.stderr).strip().splitlines()
    return next(
        (riga for riga in righe if "version" in riga.lower()),
        righe[0] if righe else "n/d",
    )


def installa() -> int:
    eseguibile = installa_llama()
    print(f"llama-server: {eseguibile}")
    print(f"Versione: {versione_llama(eseguibile)}")
    print("Scarico il modello PaddleOCR-VL 1.6 (circa 1,8 GB, solo la prima volta)...")
    modello, _ = scarica_modello()
    print(f"Modello pronto in: {modello.parent}")
    return 0


def _porta_libera() -> int:
    with socket.socket() as prova:
        prova.bind(("127.0.0.1", 0))
        return prova.getsockname()[1]


class ServerOCR:
    """Avvia llama-server con il modello e lo chiude all'uscita: `with ServerOCR(...) as ocr`."""

    def __init__(
        self,
        eseguibile: Path,
        modello: Path,
        mmproj: Path,
        log: Path,
        attesa_max: float = 600,
    ) -> None:
        self.eseguibile = eseguibile
        self.modello = modello
        self.mmproj = mmproj
        self.log = log
        self.attesa_max = attesa_max
        self.secondi_avvio = 0.0

    def __enter__(self) -> Self:
        porta = _porta_libera()
        self.url = f"http://127.0.0.1:{porta}"
        # Contesto e richieste fissati: stessa memoria occupata su ogni computer, una foto alla volta.
        comando = [
            str(self.eseguibile),
            "-m",
            str(self.modello),
            "--mmproj",
            str(self.mmproj),
            "--temp",
            "0",
            "-c",
            "8192",
            "-np",
            "1",
            "--host",
            "127.0.0.1",
            "--port",
            str(porta),
        ]
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self._file_log = self.log.open("w", encoding="utf-8")
        inizio = time.monotonic()
        self._processo = subprocess.Popen(
            comando, stdout=self._file_log, stderr=subprocess.STDOUT
        )
        try:
            self._attendi_pronto()
        except BaseException:
            self.__exit__()
            raise
        self.secondi_avvio = time.monotonic() - inizio
        return self

    def __exit__(self, *_: object) -> None:
        if self._processo.poll() is None:
            self._processo.terminate()
            try:
                self._processo.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self._processo.kill()
                self._processo.wait()
        self._file_log.close()

    def _attendi_pronto(self) -> None:
        scadenza = time.monotonic() + self.attesa_max
        while time.monotonic() < scadenza:
            if self._processo.poll() is not None:
                raise RuntimeError(
                    f"llama-server si è chiuso (codice {self._processo.returncode}). Dettagli in {self.log}"
                )
            try:
                with _SENZA_PROXY.open(f"{self.url}/health", timeout=5) as risposta:
                    if risposta.status == 200:
                        return
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                pass  # non ancora in ascolto, oppure 503 mentre carica il modello
            time.sleep(0.5)
        raise TimeoutError(
            f"llama-server non pronto dopo {self.attesa_max:.0f} s. Dettagli in {self.log}"
        )

    def leggi(
        self,
        immagine: bytes,
        prompt: str = "OCR:",
        tipo: str = "image/png",
        max_token: int = 2048,
    ) -> str:
        """Manda un'immagine al modello e restituisce il testo letto."""
        dati_immagine = base64.b64encode(immagine).decode()
        corpo = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{tipo};base64,{dati_immagine}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "temperature": 0,
            "max_tokens": max_token,
        }
        richiesta = urllib.request.Request(
            f"{self.url}/v1/chat/completions",
            data=json.dumps(corpo).encode(),
            headers={"Content-Type": "application/json"},
        )
        with _SENZA_PROXY.open(richiesta, timeout=900) as risposta:
            return json.load(risposta)["choices"][0]["message"]["content"]


def immagine_prova() -> bytes:
    """PNG con intestazione e valori di un RCEE tipo 1 (testo stampato, non scritto a mano)."""
    carattere = ImageFont.load_default(size=32)
    misura = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    larghezza = (
        int(max(misura.textlength(riga, font=carattere) for riga in RIGHE_PROVA)) + 80
    )
    immagine = Image.new("RGB", (larghezza, 60 + 56 * len(RIGHE_PROVA)), "white")
    disegno = ImageDraw.Draw(immagine)
    for numero, riga in enumerate(RIGHE_PROVA):
        disegno.text((40, 30 + 56 * numero), riga, fill="black", font=carattere)
    buffer = BytesIO()
    immagine.save(buffer, format="PNG")
    return buffer.getvalue()


def _normalizza(testo: str) -> str:
    return " ".join(testo.replace(".", ",").split()).upper()


def valori_mancanti(testo: str, attesi: list[str]) -> list[str]:
    """Valori attesi assenti dal testo; maiuscole, spazi e punto o virgola decimale non contano."""
    letto = _normalizza(testo)
    return [valore for valore in attesi if _normalizza(valore) not in letto]
