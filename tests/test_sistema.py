import sys

from rcee.sistema import info_sistema


def test_info_sistema_completa(tmp_path):
    info = info_sistema(tmp_path)
    assert list(info) == [
        "Sistema", "Python", "Processore", "Core", "RAM", "Scheda grafica", "Spazio libero su disco",
    ]
    assert all(info.values())
    if sys.platform in ("win32", "darwin"):
        assert info["Processore"] != "n/d"
