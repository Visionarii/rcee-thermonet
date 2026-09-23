# rcee-thermonet

Inserimento automatico dei rapporti RCEE (tipo 1 e tipo 2) su ThermoNET, il portale
di Nuova Salento Energia, a partire dalla foto del rapportino mandata su Telegram.

**Stato: fase 1, preparazione dell'ambiente.**

| Comando | Cosa fa |
|---|---|
| `uv run rcee diagnostica` | Controlla computer, browser sul portale e OCR; scrive `dati/diagnostica.txt` |
| `uv run rcee installa-ocr` | Scarica llama.cpp (su Windows) e il modello PaddleOCR-VL 1.6 (circa 1,8 GB) |
| `uv run rcee registra` | Registra una pratica sul portale con Playwright codegen, login escluso |

Installazione sul PC dell'ufficio: [ISTRUZIONI-WINDOWS.md](ISTRUZIONI-WINDOWS.md).

## Regola sui dati

Nel repository va solo codice. Profili del browser, sessioni, modelli, foto, PDF,
registrazioni e log stanno in `dati/`, che git ignora.

## Sviluppo sul Mac

```
brew install llama.cpp
uv sync
uv run pytest
uv run rcee installa-ocr
uv run rcee diagnostica --headless
```

Senza Google Chrome si usa il Chromium di Playwright: `uv run playwright install chromium`.

La prova su Windows gira anche su GitHub: Actions, "Prova su Windows", Run workflow.
