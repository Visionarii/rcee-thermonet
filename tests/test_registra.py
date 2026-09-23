import subprocess
import sys
from pathlib import Path

from rcee.registra import comando_codegen


def test_codegen_con_chrome():
    comando = comando_codegen(
        "https://portale/home", Path("s.json"), Path("out.py"), chrome=True
    )
    assert comando[1:4] == ["-m", "playwright", "codegen"]
    assert comando[comando.index("--load-storage") + 1] == "s.json"
    assert comando[comando.index("-o") + 1] == "out.py"
    assert comando[comando.index("--channel") + 1] == "chrome"
    assert comando[-1] == "https://portale/home"


def test_codegen_senza_chrome_usa_chromium():
    assert "--channel" not in comando_codegen("u", Path("s"), Path("o"), chrome=False)


def test_opzioni_esistono_nella_versione_installata():
    aiuto = subprocess.run(
        [sys.executable, "-m", "playwright", "codegen", "--help"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for opzione in ("--target", "--output", "--load-storage", "--channel"):
        assert opzione in aiuto
