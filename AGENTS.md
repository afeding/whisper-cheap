# Repository Guidelines

These notes help new contributors work on Whisper Cheap quickly on Windows/PowerShell.

## Project Structure & Module Organization
- `src/main.py`: runtime wiring (config load, managers, hotkeys, tray).
- `src/actions.py`: start/stop/cancel glue with dependency injection.
- `src/managers/`: audio capture, model download/extraction, transcription, history, hotkeys.
- `src/ui/`: tray icon, overlays, settings windows (classic + Qt variant).
- `src/utils/`: clipboard/paste helpers and LLM client; avoid GUI/hardware side effects here.
- `src/resources/`: icons + model placeholders; `config.json` controls paths (defaults to `%APPDATA%`); `.data/` and `dist/` hold generated artifacts; `tests/` mirrors managers/UI.

## Build, Test, and Development Commands
Use PowerShell from repo root:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main            # launch tray + hotkey flow
python -m unittest discover -s tests -v
pyinstaller build_config.spec # produces dist/WhisperCheap.exe
```
Run commands after activating the venv; PyInstaller must be installed globally or in the venv.

## Coding Style & Naming Conventions
- Follow PEP8 with 4-space indents; prefer type hints and explicit returns.
- Keep side effects out of module import time; inject managers (see `actions.py`) instead of globals.
- File and module names use `snake_case`; classes `CamelCase`; tests `test_<area>.py`; config keys lower snake.
- Use lightweight logging via `print` for runtime hints; avoid noisy logs inside audio/transcription loops.

## Testing Guidelines
- Tests use `unittest`; mirror runtime modules with `Test*` classes and `test_` methods.
- Mock hardware/network pieces: follow `tests/test_audio_manager.py` (custom VAD) and patch `requests` for `ModelManager`.
- Keep tests headless (no real tray/overlay); prefer fakes/stubs over sleeps.
- Aim for coverage on failure paths: download resumes, empty audio buffers, VAD thresholds, clipboard policies.

## Commit & Pull Request Guidelines
- Use imperative, scoped subjects (e.g., `feat: add modern settings overlay`, `fix: guard empty audio buffer`); keep body to motivation + testing notes.
- PRs should include: summary, how to reproduce or test commands, screenshots/gifs for UI changes, mention of config/model impacts, and any known limitations.
- Avoid committing large model artifacts or local `.data/` outputs; keep `config.json` changes minimal and documented.

## Security & Configuration Tips
- Never commit API keys (OpenRouter, etc.); load them via env vars referenced in `config.json`.
- Downloads occur at runtime; verify model URLs and checksum logic before adjusting `MODELS` in `src/managers/model.py`.
- Keep generated paths under `%APPDATA%\whisper-cheap` or `.data/` for local experiments; do not assume elevated permissions.
