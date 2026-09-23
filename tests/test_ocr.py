from io import BytesIO

import pytest
from PIL import Image

from rcee import ocr


def test_valori_letti_con_punto_spazi_e_minuscole():
    testo = "Rapporto tipo  1 (gruppi termici)\nfumi 55.0 °C aria 28,0\nO2 3.5 CO2 9,7 CO 104\n98,8 92"
    assert ocr.valori_mancanti(testo, ocr.VALORI_PROVA) == []


def test_valori_mancanti_elencati():
    assert ocr.valori_mancanti(
        "TIPO 1 55,0 28,0 3,5 9,7 98,8 92", ocr.VALORI_PROVA
    ) == ["104"]


def test_immagine_prova_contiene_tutte_le_righe():
    immagine = Image.open(BytesIO(ocr.immagine_prova()))
    assert immagine.format == "PNG"
    assert immagine.height == 60 + 56 * len(ocr.RIGHE_PROVA)
    assert immagine.width > 1000


def test_llama_server_da_variabile(tmp_path, monkeypatch):
    finto = tmp_path / "llama-server"
    finto.write_text("")
    monkeypatch.setenv("RCEE_LLAMA_SERVER", str(finto))
    assert ocr.trova_llama_server() == finto


def test_variabile_su_file_inesistente(tmp_path, monkeypatch):
    monkeypatch.setenv("RCEE_LLAMA_SERVER", str(tmp_path / "manca"))
    with pytest.raises(FileNotFoundError):
        ocr.trova_llama_server()


def test_pacchetto_windows_fissato_con_checksum():
    nome, sha256 = ocr.PACCHETTI_LLAMA[("Windows", "AMD64")]
    assert ocr.VERSIONE_LLAMA in nome
    assert len(sha256) == 64
