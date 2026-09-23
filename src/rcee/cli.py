"""Comandi: uv run rcee <comando>."""

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    # Il testo letto dall'OCR può contenere qualsiasi carattere: niente crash su console o pipe Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="rcee", description="Automazione dei rapporti RCEE su ThermoNET."
    )
    comandi = parser.add_subparsers(dest="comando", required=True, metavar="comando")
    diagnostica = comandi.add_parser(
        "diagnostica", help="controlla computer, browser sul portale e OCR"
    )
    diagnostica.add_argument(
        "--headless", action="store_true", help="non mostrare la finestra del browser"
    )
    comandi.add_parser(
        "installa-ocr", help="scarica llama.cpp (su Windows) e il modello PaddleOCR-VL"
    )
    comandi.add_parser(
        "registra", help="registra una pratica sul portale, login escluso"
    )
    argomenti = parser.parse_args(argv)

    if argomenti.comando == "diagnostica":
        from .diagnostica import esegui

        return esegui(argomenti.headless)
    if argomenti.comando == "installa-ocr":
        from .ocr import installa

        return installa()
    from .registra import esegui

    return esegui()
