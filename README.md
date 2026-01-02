# Whisper Cheap

Dictado rápido en Windows: graba con hotkey, transcribe con Parakeet V3 y mejora el texto con OpenRouter (SDK oficial).

## Requisitos
- Windows + PowerShell
- Python 3.10+
- Micrófono y permisos de audio

## Instalación rápida
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Uso
```powershell
python -m src.main
```
- Hotkey por defecto: `ctrl+shift+space` (toggle). Configurable en `config.json` o desde Settings.
- Se abre la ventana de ajustes moderna al inicio; ahí puedes activar/desactivar post-proceso LLM y elegir modelo.

## Empaquetado e instalador (Windows)
```powershell
pyinstaller build_config.spec
```
- Genera `dist/WhisperCheap/WhisperCheap.exe` (modo onedir). Este .exe es portable.
- El instalador real se genera con Inno Setup.

```powershell
ISCC installer/WhisperCheap.iss
```
Si `ISCC` no esta en PATH, usa la ruta completa:
```powershell
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" ".\installer\WhisperCheap.iss"
```
- Genera el instalador en `dist/installer/WhisperCheapSetup.exe`.
- Si falla con "archivo en uso", cierra la app/tray y cualquier Explorador abierto en `dist/WhisperCheap` (o espera a que termine el antivirus).


## LLM (OpenRouter)
- Se usa el SDK oficial `openrouter` (fallback al cliente `openai` apuntando a https://openrouter.ai/api/v1).
- Prompt de sistema fijo: “Transcription 2.0” (limpieza mínima, no traducción, mantiene tokens técnicos).
- Modelos por defecto (lista limitada y scrolleable en Settings, con add/remove/reset):
  - `openai/gpt-oss-20b` (provider fijo: `groq`)
  - `google/gemini-2.5-flash-lite` (providers: `google-ai-studio`, `google-vertex`)
  - `mistralai/mistral-small-3.2-24b-instruct` (provider: `mistral`)
- Para otros modelos sin provider fijo se usa `provider: {"sort": "throughput", "allow_fallbacks": true}`.
- Test de conexión disponible en Settings (usa el modelo y provider activos).

## Registros y datos
- Config y DB: `%APPDATA%/whisper-cheap` en modo empaquetado; `.data/` en dev.
- Grabaciones WAV y DB en `recordings/` y `history.db` respectivamente.
- Logs: `%APPDATA%/whisper-cheap/logs/app.log` (en dev: `.data/logs/app.log`).

## Apagado y recursos
- Al salir se desregistran hotkeys, se cierra el stream de audio, se descarga el modelo cargado y se limpian huérfanos del historial.

## Próximos pasos sugeridos
- Ejecutar pruebas manuales end-to-end (hotkey → STT → LLM → pegado) y casos edge (audio corto, cancelación, fallos de red).
- Empaquetar con PyInstaller e Inno Setup; validar en VM limpia.
- Añadir README extendido con capturas y notas de modelos/overlays si se publica.
