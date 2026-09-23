"""Esplorazione del portale dopo il login: elenca menu e pulsanti senza cliccare nulla.

Serve a scoprire funzioni come l'importazione XML. Nel file finiscono solo voci
di menu e barre dei pulsanti: le righe delle tabelle (dove stanno i clienti) si
saltano sempre, e dagli indirizzi si toglie tutto ciò che segue "?" o "&".
Il portale è fatto con DevExpress (XAF): i suoi menu hanno classi "dxm-", "dxnb".
"""

import re
from datetime import datetime

from playwright.sync_api import Error, Page, sync_playwright

from .browser import apri_chrome
from .config import URL_PORTALE, cartella

PAROLE_CHIAVE = re.compile(
    r"import|xml|tracciat|massiv|carica|upload|trasmission|allegat|esport|export|rct|rapport|bozz",
    re.IGNORECASE,
)
_SOLO_NUMERI = re.compile(r"[\d\s./-]+")

_RACCOGLI = """
() => {
  const elementi = 'a, button, [role=menuitem], [role=button], [role=tab], input[type=button], input[type=submit], li';
  const menu = 'nav, header, [role=navigation], [role=menu], [role=menubar], [role=tablist], '
    + '[class*=menu], [class*=Menu], [class*=nav], [class*=Nav], [class*=toolbar], [class*=Toolbar], '
    + '[class*=dxm-], [class*=dxnb], [class*=dxtc], [class*=dxtv], [id*=Menu], [id*=NavBar]';
  const righeDati = '[class*=dxgv], [class*=DataRow], [role=row], [role=grid]';
  const voci = [];
  for (const el of document.querySelectorAll(elementi)) {
    const tabella = el.closest('table');
    const inDati = !!el.closest(righeDati) || !!(tabella && tabella.querySelector('th'));
    if (inDati) continue;
    const testo = (el.innerText || el.value || el.getAttribute('aria-label') || el.title || '')
      .trim().replace(/\\s+/g, ' ');
    if (!testo || testo.length > 60) continue;
    voci.push({
      testo,
      href: (el.getAttribute('href') || '').split('?')[0].split('&')[0],
      nel_menu: !!el.closest(menu),
    });
  }
  return voci;
}
"""


def raccogli_voci(pagina: Page) -> tuple[list[str], list[str]]:
    """Voci con parole chiave e altre voci di menu della pagina, senza doppioni."""
    chiave: dict[str, None] = {}
    menu: dict[str, None] = {}
    for frame in pagina.frames:
        try:
            voci = frame.evaluate(_RACCOGLI)
        except Error:
            continue  # frame chiuso nel frattempo
        for voce in voci:
            if _SOLO_NUMERI.fullmatch(voce["testo"]):
                continue  # numeri di pratica o di impianto
            href = voce["href"]
            # Nel portale (XAF) i link sono default.aspx#<codice cifrato>: non dicono nulla.
            if "#" in href or href.startswith("javascript"):
                href = ""
            riga = voce["testo"] + (f"  [{href}]" if href else "")
            if PAROLE_CHIAVE.search(voce["testo"]) or PAROLE_CHIAVE.search(href):
                chiave[riga] = None
            elif voce["nel_menu"]:
                menu[riga] = None
    return list(chiave), list(menu)


def esegui() -> int:
    print("Si apre Chrome sul portale: fai il login.")
    print(
        "Lo script non clicca niente: legge solo menu e pulsanti delle pagine che apri tu."
    )
    pagine: dict[str, tuple[list[str], list[str]]] = {}
    try:
        with sync_playwright() as p:
            contesto, _ = apri_chrome(p, cartella("chrome-registrazione"))
            try:
                pagina = contesto.pages[0] if contesto.pages else contesto.new_page()
                pagina.goto(URL_PORTALE, wait_until="commit")
                while True:
                    risposta = input(
                        "\nApri una pagina del portale, poi premi Invio per leggerla "
                        "(scrivi f e Invio per finire): "
                    )
                    if risposta.strip().lower() == "f":
                        break
                    indirizzo = pagina.url.split("?")[0]
                    pagine[indirizzo] = raccogli_voci(pagina)
                    print(
                        f"Letta: {indirizzo} ({len(pagine[indirizzo][0])} voci su import e rapporti)"
                    )
            finally:
                contesto.close()
    except Error:
        print("Il browser è stato chiuso: rilancia il comando e scrivi f per finire.")
        return 1

    righe = [f"ESPLORAZIONE PORTALE, {datetime.now().astimezone():%d/%m/%Y %H:%M}"]
    for indirizzo, (chiave, menu) in pagine.items():
        righe += [
            "",
            f"#### {indirizzo}",
            f"== Voci su import, file e rapporti ({len(chiave)}) ==",
            *chiave,
        ]
        righe += [f"== Altre voci di menu ({len(menu)}) ==", *menu]
    testo = "\n".join(righe)
    uscita = cartella(".") / "esplorazione.txt"
    uscita.write_text(testo + "\n", encoding="utf-8")
    print("\n" + testo)
    print(f"\nSalvato in: {uscita}")
    return 0
