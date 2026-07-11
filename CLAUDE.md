# Whisper Cheap

Aplicacion Windows de dictado rapido. Graba audio con hotkey global, transcribe localmente con Parakeet V3 en ONNX y puede limpiar el texto con OpenRouter para pegarlo en la app activa.

## Stack

- Python 3.10+ en Windows.
- Audio/STT: `sounddevice`, `numpy`, Silero VAD ONNX, `onnxruntime==1.20.1`, Parakeet V3 INT8, `librosa`, `scipy`, `soxr`.
- UI/sistema: `PyQt6`, `pywebview`, `pystray`, `Pillow`, overlays Win32/PyQt, `pynput`, `pywin32`, `pyperclip`.
- LLM: cliente `openai` apuntando a `https://openrouter.ai/api/v1`.
- Build: PyInstaller onedir e Inno Setup.
- `web/` es una app Next.js separada para la web/landing; no forma parte del runtime desktop.

## Estructura

```text
src/main.py                     Entry point: config, managers, hotkeys, tray, overlays, shutdown
src/actions.py                  Glue start/stop/cancel con dependencias inyectadas
src/__version__.py              Version de la app
src/managers/audio.py           Captura sounddevice, VAD, buffer y chunking incremental
src/managers/model.py           Descarga y extraccion de Parakeet
src/managers/transcription.py   Pipeline Parakeet ONNX, providers, chunks largos y timeout
src/managers/recording_state.py Maquina de estados y worker secuencial
src/managers/chunk_transcriber.py Transcripcion parcial en background
src/managers/history.py         SQLite, WAV y limpieza de huerfanos
src/managers/hotkey.py          Hotkeys globales con pynput
src/managers/updater.py         GitHub Releases y ejecucion del instalador
src/ui/web_settings/            Settings en pywebview: HTML, JS y API Python
src/ui/tray.py, overlay.py, win_overlay.py Tray y overlays PyQt/Win32
src/utils/llm_client.py         OpenRouter via SDK OpenAI-compatible
src/utils/paste.py              Paste con SendInput y politicas de clipboard
src/resources/                  Iconos, sonidos, defaults LLM y precios cacheados
tests/                          Tests unitarios con mocks de hardware/red/UI
hooks/, installer/, build_config.spec Build PyInstaller/Inno y DLLs ONNX
config.json, web/               Config de desarrollo y sitio Next.js
```

## Flujo desktop

1. `python -m src.main` carga o crea `config.json`.
2. En dev usa la raiz del repo y `.data`; empaquetado usa `%APPDATA%\whisper-cheap`.
3. Inicializa logging, audio, modelo, transcripcion, historial, tray, overlays, settings y updater.
4. Descarga Parakeet si falta y descarga Silero VAD si `audio.use_vad` esta activo.
5. Pre-carga Parakeet y ejecuta warmup para reducir latencia de primera transcripcion.
6. Registra la hotkey de config y revisa cambios de hotkey/modo cada 2 segundos.
7. En `toggle`, una pulsacion inicia grabacion y la siguiente detiene. En `ptt`, press graba y release detiene.
8. Al grabar abre stream de microfono, suena cue opcional y activa `ChunkTranscriber`.
9. Al detener, `RecordingStateMachine` captura samples, vuelve a `IDLE` y encola un `ProcessingJob`.
10. El worker transcribe, llama OpenRouter si procede, guarda WAV/SQLite y pega el texto.
11. El cierre desregistra hotkeys, cierra UI/audio, descarga el modelo y limpia huerfanos.

## Concurrencia y audio

- La hotkey no hace trabajo pesado; solo cambia estado, arranca/detiene audio y encola trabajo.
- `RecordingStateMachine` usa estados `IDLE` y `RECORDING`.
- Hay un worker secuencial: procesa un job cada vez.
- Mientras `pending_count > 0`, `try_start_recording()` rechaza nuevas grabaciones.
- El audio es mono `float32` a 16 kHz; evita resampling extra en el camino caliente.
- El buffer de grabacion esta limitado a 120 s para acotar memoria.
- Con VAD activo se detecta voz para chunking y filtros; si Silero falla, hay fallback por RMS.
- El chunking emite trozos tras pausas naturales para adelantar transcripcion sin cortar frases demasiado pronto.

## STT y LLM

- Modelo desktop por defecto: `parakeet-v3-int8`.
- `ModelManager` descarga `https://blob.handy.computer/parakeet-v3-int8.tar.gz` y extrae a `parakeet-tdt-0.6b-v3-int8`.
- El pipeline preferido usa `nemo128.onnx`, `encoder-model.int8.onnx`, `decoder_joint-model.int8.onnx` y `vocab.txt`.
- ONNX provider admite `auto`, `cpu`, `cuda` o nombre completo; `auto` prefiere CUDA si existe y si no usa CPU.
- Transcripciones mayores de 30 s se parten en chunks de 30 s con 2 s de solape.
- Cada transcripcion tiene timeout de 120 s.
- `post_processing.prompt_template` se envia como system message; la transcripcion va como user message dentro de `<transcription>`.
- Providers LLM especiales: `openai/gpt-oss-20b` usa `groq`; `google/gemini-2.5-flash-lite` usa `google-ai-studio`/`google-vertex`; `mistralai/mistral-small-3.2-24b-instruct` usa `mistral`.
- Modelos sin provider especial usan `provider: {"sort": "throughput", "allow_fallbacks": true}`.

## Config y datos

- En dev, `config.json` vive en la raiz del repo. En exe, vive en `%APPDATA%\whisper-cheap\config.json`.
- `paths.app_data` acepta variables como `%APPDATA%`; rutas relativas se resuelven contra el directorio de config.
- Datos habituales: `.data/models`, `.data/recordings`, `.data/history.db`, `.data/logs/app.log`.
- La API key de OpenRouter se guarda en config desde Settings; no hay variable de entorno obligatoria.
- PyInstaller no empaqueta `config.json` para no meter claves del desarrollador en el exe.
- `HistoryManager` guarda WAV y metadatos, pero `main.py` ejecuta `history_manager.clear_all()` al arrancar.
- Logs rotan a 10 MB x 5 y son la primera fuente para depurar hotkey, audio, STT, LLM y shutdown.

## Comandos

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m src.main
pytest tests/ -v
pyinstaller build_config.spec
ISCC installer/WhisperCheap.iss
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" ".\installer\WhisperCheap.iss"
```

## Build, updates y gotchas

- `src/__version__.py` y `installer/WhisperCheap.iss` deben mantener la misma version.
- PyInstaller genera `dist/WhisperCheap/WhisperCheap.exe`; Inno genera `dist/installer/WhisperCheapSetup.exe`.
- `UpdateManager` mira `https://api.github.com/repos/afeding/whisper-cheap/releases/latest`; el asset debe llamarse `WhisperCheapSetup.exe`.
- El instalador cierra `WhisperCheap.exe`, instala en `{autopf}\Whisper Cheap` y relanza la app.
- El autostart se escribe en `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` solo cuando corre como exe.
- `onnxruntime` esta fijado a `1.20.1`; tocarlo afecta PyInstaller y carga de DLLs.
- `build_config.spec` copia DLLs/PYD de ONNX Runtime a la raiz interna del build para evitar `DLL load failed`.
- Si Inno falla con "archivo en uso", suele ser la app/tray abierta, Explorer dentro de `dist/WhisperCheap` o el antivirus.
- El modelo Parakeet no tiene SHA256 configurado en `MODELS`; si endureces distribucion, anade hash para confiar en la descarga.
- `pynput` es el backend real de hotkeys; no asumas la libreria `keyboard`.
- Settings expone metodos Python a JS via pywebview; evita objetos no serializables.
- `download_and_install_update()` llama `os._exit(0)` para que el instalador pueda reemplazar archivos.
- Los tests mockean hardware/red/UI; para bugs de microfono, hotkeys o paste hace falta prueba manual en Windows.

## Estilo

- Mantén managers desacoplados e inyecta dependencias en `__init__`.
- Usa imports absolutos desde `src` y `pathlib` para rutas nuevas.
- No metas singletons globales nuevos ni bloquees callbacks de hotkey, tray o UI con STT, red o disco pesado.
- No guardes secretos en docs, logs ni artefactos empaquetados.
