import pytest
from playwright.sync_api import Error, sync_playwright

from rcee.esplora import raccogli_voci

PAGINA = """
<nav><a href="/rct/elenco">Rapporti di controllo</a><a href="/richieste?stato=1">Richieste</a></nav>
<ul class="dxm-main"><li class="dxm-item">Nuovo</li><li class="dxm-item">Importa XML</li><li class="dxm-item">3709813</li></ul>
<a href="#ViewID=Impianto_ListView&ObjectKey=12">Impianti</a>
<table class="dxgvTable">
  <tr class="dxgvDataRow"><td><a href="/rct/dettaglio?id=9">Rapporto di ROSSI MARIO</a></td></tr>
</table>
<table><tr><th>Cliente</th></tr><tr><td><a href="/impianto?id=7">BIANCHI ANNA</a></td></tr></table>
"""


@pytest.fixture(scope="module")
def voci():
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Error:
            try:
                browser = p.chromium.launch()
            except Error:
                pytest.skip("nessun browser installato per Playwright")
        pagina = browser.new_page()
        pagina.set_content(PAGINA)
        risultato = raccogli_voci(pagina)
        browser.close()
    return risultato


def test_trova_import_e_menu(voci):
    chiave, menu = voci
    assert "Importa XML" in chiave
    assert "Rapporti di controllo  [/rct/elenco]" in chiave
    assert "Richieste  [/richieste]" in menu
    assert "Nuovo" in menu


def test_niente_dati_dei_clienti(voci):
    tutto = " ".join(voci[0] + voci[1])
    assert "ROSSI" not in tutto
    assert "BIANCHI" not in tutto
    assert "ObjectKey" not in tutto
    assert "?" not in tutto
    assert "3709813" not in tutto
