# CLAUDE.md — Whisper Cheap

Aplicación Windows de voz a texto (STT) con Parakeet V3 ONNX, VAD Silero, hotkeys globales, y post-procesamiento LLM opcional via OpenRouter.

## Role

Ingeniero Python senior especializado en aplicaciones desktop Windows, procesamiento de audio/ML y empaquetado standalone.

## Overview

**Whisper Cheap** es un port Python de Handy (app original en Tauri/Rust) para transcripción de voz local y eficiente en Windows.

**Propósito:**
- Grabar audio mediante hotkey (PTT o toggle)
- Transcribir localmente con Parakeet V3 (ONNX int8 optimizado)
- Post-procesar transcripciones con LLM (OpenRouter) opcionalmente
- Pegar automáticamente el resultado en la app activa
- Historial persistente con SQLite

**Características clave:**
- STT local (CPU) con ONNX Runtime
- VAD (Silero v4) para detección de voz
- System tray + overlays visuales (PyQt6)
- Configuración via JSON + ventana de settings moderna
- Empaquetable a .exe standalone con PyInstaller

**Estado actual:** Fase de implementación completa. Managers, UI y flujo end-to-end funcionando. Tests unitarios implementados.

---

## Structure

```
whisper-cheap/
├── src/
│   ├── __version__.py       # Versión de la app (punto único de verdad)
│   ├── main.py              # Entry point: carga config, inicializa managers, registra hotkeys
│   ├── actions.py           # Capa glue: start/stop/cancel recording
│   ├── managers/            # Lógica de negocio encapsulada
│   │   ├── audio.py         # AudioRecordingManager: sounddevice stream + VAD Silero
│   │   ├── model.py         # ModelManager: descarga/extracción modelos ONNX
│   │   ├── transcription.py # TranscriptionManager: Parakeet V3 pipeline
│   │   ├── history.py       # HistoryManager: SQLite + almacenamiento audios .wav
│   │   ├── hotkey.py        # HotkeyManager: pynput para hotkeys globales
│   │   └── updater.py       # UpdateManager: check/download/install updates via GitHub
│   ├── ui/
│   │   ├── tray.py          # TrayManager: icono system tray con pystray
│   │   ├── overlay.py       # RecordingOverlay + StatusOverlay (PyQt6 frameless)
│   │   ├── win_overlay.py   # WinOverlayBar: overlay nativo Win32
│   │   └── web_settings/    # Ventana de settings (pywebview)
│   │       ├── __init__.py  # open_web_settings(), cleanup
│   │       ├── api.py       # SettingsAPI expuesta a JavaScript
│   │       ├── index.html   # UI HTML/Tailwind
│   │       └── app.js       # Lógica JavaScript
│   ├── utils/
│   │   ├── clipboard.py     # ClipboardManager: pyperclip wrapper
│   │   ├── paste.py         # paste_text: SendInput via pywin32
│   │   └── llm_client.py    # LLMClient: llamadas a OpenRouter
│   └── resources/
│       ├── icons/           # Iconos del tray y app
│       └── sounds/          # Sonidos de inicio/fin de grabación
├── installer/
│   └── WhisperCheap.iss     # Script de Inno Setup
├── tests/                   # Tests unitarios con pytest + mocks
├── config.json              # Configuración runtime (hotkey, audio, paths, LLM)
├── requirements.txt         # Deps Python
├── build_config.spec        # PyInstaller spec
└── README.md
```

**Archivos de datos (runtime):**
- `.data/` o `%APPDATA%\whisper-cheap\` (configurable en config.json):
  - `models/parakeet-tdt-0.6b-v3-int8/` — archivos ONNX descargados
  - `recordings/` — archivos .wav guardados
  - `history.db` — SQLite con transcripciones
  - `update_cache.json` — cache de estado de actualizaciones
  - `logs/app.log` — logs de la aplicación

---

## Stack and Tools

### Lenguaje y Runtime
- **Python 3.10+** (Windows)
- Virtual env (`.venv/`)

### Audio y STT
- **sounddevice** — captura de audio (PortAudio)
- **numpy** — procesamiento arrays de audio
- **onnxruntime** — inferencia ONNX (Silero VAD + Parakeet V3)
- **librosa** — extracción de log-Mel spectrograms (Parakeet)
- **soxr** — resampling de audio (dependencia de librosa)

### UI y Sistema
- **PyQt6** — overlays y ventana de settings
- **pystray + Pillow** — system tray icon
- **keyboard** — hotkeys globales (Windows)
- **pywin32** — SendInput para paste automático
- **pyperclip** — clipboard cross-platform

### Post-procesamiento
- **openai** (client lib) — llamadas a OpenRouter API
- **httpx / requests** — descarga modelos

### Almacenamiento
- **sqlite3** (built-in) — historial de transcripciones

### Testing y Build
- **pytest** — tests unitarios
- **PyInstaller** — empaquetado a .exe standalone

---

## Common Workflows

### Setup inicial del entorno
```bash
# Crear venv
python -m venv .venv

# Activar (PowerShell)
.\.venv\Scripts\Activate.ps1

# Instalar deps
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ejecutar la app
```bash
# Desde raíz del proyecto
python -m src.main
```

**Comportamiento esperado:**
1. Carga `config.json`
2. Descarga modelo Parakeet V3 si no existe
3. Descarga Silero VAD si `use_vad: true`
4. Abre ventana de settings (PyQt6)
5. Registra hotkey global (default: `ctrl+shift+space`)
6. Inicia system tray icon
7. Espera input de usuario

### Flujo de transcripción
1. Usuario presiona hotkey → `actions.start()` → comienza grabación
2. `AudioRecordingManager` captura audio en buffer circular
3. Usuario suelta/re-presiona hotkey → `actions.stop()` → detiene grabación
4. `TranscriptionManager.transcribe()` procesa audio con Parakeet V3
5. (Opcional) `LLMClient.postprocess()` envía a OpenRouter
6. `HistoryManager` guarda audio + transcripción en SQLite
7. `paste_text()` pega resultado en app activa

### Ejecutar tests
```bash
pytest tests/ -v
```

### Build standalone .exe + instalador
```powershell
pyinstaller build_config.spec
```
- Genera `dist/WhisperCheap/WhisperCheap.exe` (modo onedir, portable).
- El instalador real se genera con Inno Setup.

```powershell
ISCC installer/WhisperCheap.iss
```
Si `ISCC` no esta en PATH, usa la ruta completa:
```powershell
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" ".\installer\WhisperCheap.iss"
```
- Instalador final: `dist/installer/WhisperCheapSetup.exe`.

**Troubleshooting "archivo en uso" durante compilación:**
El error común "El proceso no tiene acceso al archivo porque está siendo utilizado por otro proceso" ocurre cuando **Windows Defender** escanea archivos mientras Inno Setup intenta comprimirlos (condición de carrera con `MsMpEng.exe`).

**Soluciones:**
1. **Reintentar** - a veces funciona si Defender ya terminó el escaneo
2. **Añadir exclusión temporal** (recomendado, requiere admin):
   ```powershell
   Add-MpPreference -ExclusionPath "D:\1.SASS\whisper-cheap\dist"
   # Después de compilar:
   Remove-MpPreference -ExclusionPath "D:\1.SASS\whisper-cheap\dist"
   ```
3. **Cerrar** procesos: app/tray y Exploradores en `dist/WhisperCheap`

### Modificar configuración
Edita `config.json` manualmente o usa la ventana de settings (abre automáticamente al iniciar).

**Campos importantes:**
- `hotkey`: combinación de teclas (ej: `"ctrl+shift+space"`)
- `mode.activation_mode`: `"ptt"` (push-to-talk) o `"toggle"`
- `audio.device_id`: `null` = default device, `int` = index específico
- `audio.use_vad`: `true` para Silero VAD, `false` para grabar todo
- `post_processing.enabled`: `true` para activar LLM
- `paths.app_data`: ruta base para modelos/datos (soporta `%APPDATA%`)

---

## Conventions and Style

### Código
- **Type hints** en todas las funciones públicas
- **Docstrings** en clases y funciones principales (Google style)
- **Imports absolutos** desde raíz del proyecto (ej: `from src.managers.audio import ...`)
- **f-strings** para formateo de strings
- **Pathlib** para rutas de archivos (no `os.path`)

### Naming
- **Clases**: `PascalCase` + sufijo `Manager` para gestores (ej: `AudioRecordingManager`)
- **Funciones/métodos**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Privados**: prefijo `_` (ej: `_session`, `_lock`)

### Threading
- Locks explícitos (`threading.Lock`, `threading.Condition`) en managers con estado mutable
- Eventos de cancelación con `threading.Event`
- Threads daemon para mantenimiento (ej: unload de modelos por inactividad)

### Error Handling
- **Graceful degradation**: si falta una librería opcional (ej: `sounddevice`), fallar solo en uso, no en import
- **Try/except** en callbacks de UI (tray, hotkeys) para no crashear la app
- **Print** para logging (TODO: migrar a `logging` module)

### Testing
- Mocks para dependencias externas (sounddevice, onnxruntime, keyboard)
- Tests unitarios por manager, no integración end-to-end
- Fixtures compartidos en `tests/__init__.py` (si necesario)

---

## Important Context

### Arquitectura: Managers desacoplados
Cada manager es una clase autocontenida que recibe sus dependencias en `__init__`. No hay singletons globales.

**Razón:** Facilita testing (inyección de mocks) y permite instanciar múltiples configuraciones si es necesario.

**Ejemplo:** `TranscriptionManager` recibe `ModelManager` como argumento, no lo importa globalmente.

### Audio: siempre 16kHz mono float32
Parakeet V3 requiere audio a 16kHz. `sounddevice` captura a `sample_rate=16000`, `channels=1`, `dtype=float32`.

**No hacer:** conversiones de sample rate en el pipeline caliente. Si el dispositivo no soporta 16kHz nativo, sounddevice resamplea automáticamente.

### VAD Silero: opcional pero recomendado
Si `use_vad: false`, se graba TODO el audio (útil para debug o ambientes silenciosos).

Con VAD activado, solo se bufferean chunks donde `silero_vad.process()` > `vad_threshold`.

**Trade-off:** VAD reduce falsos positivos pero añade ~5ms de latencia por chunk.

### Parakeet V3: pipeline multi-etapa
1. **Preprocessing:** audio → log-Mel spectrogram (librosa)
2. **Encoder ONNX:** mel → encoder_out
3. **Nemo ONNX:** encoder_out → logits por frame
4. **Decoder ONNX:** encoder_out + tokens previos → joint logits
5. **Greedy search:** seleccionar tokens con max probabilidad, colapsando blanks

**Archivos del modelo:**
- `nemo128.onnx` — modelo Nemo (solo necesitamos este para transcripción rápida)
- `encoder-model.int8.onnx` + `decoder_joint-model.int8.onnx` — modelos alternativos (no usados actualmente)
- `vocab.txt` — vocabulario (1 token por línea)
- `config.json` — metadata del modelo

### Config.json: rutas expandibles
`paths.app_data` soporta variables de entorno (ej: `%APPDATA%`). Expandir con `os.path.expandvars()`.

**Default:** `.data/` en raíz del proyecto (para desarrollo).

**Produccion:** `%APPDATA%\whisper-cheap\` (config.json se crea ahi si no existe; no se empaqueta junto al .exe).

### Hotkeys: solo Windows
`keyboard` lib usa hooks de bajo nivel de Windows. **No portable a Linux/macOS**.

**Alternativa (futuro):** `pynput` para cross-platform, pero requiere permisos elevados en macOS.

### Paste automático: SendInput via pywin32
`paste_text()` usa `win32api.SendInput()` para simular `Ctrl+V`. Más confiable que `pyperclip` + sleep + paste.

**Política de clipboard:**
- `DONT_MODIFY`: no toca clipboard, solo SendInput
- `OVERWRITE`: escribe en clipboard y pega
- `APPEND`: añade a clipboard existente

### Post-procesamiento LLM: plantillas con `${output}`
`prompt_template` en config.json puede incluir `${output}` que se reemplaza con la transcripción raw.

**Ejemplo:** `"Corrige errores y formatea: ${output}"`

**Timeout:** 30s para llamadas a OpenRouter (configurable en `LLMClient`).

### PyInstaller: empaquetar ONNX + dependencias nativas
**Crítico:** `onnxruntime` requiere DLLs nativas (CUDA si se usa GPU). PyInstaller debe incluir:
- `onnxruntime/capi/*.dll`
- `sounddevice` + PortAudio DLL
- `PyQt6` Qt libs

**Versión de onnxruntime:** Usar `==1.20.1` (fijada en requirements.txt). Las versiones 1.22+ tienen un bug de regresión que causa "DLL load failed" en apps empaquetadas con PyInstaller en Windows.

Ver `build_config.spec` para `hiddenimports` y `binaries`. El spec usa `collect_all()` y un runtime hook (`hooks/rthook_onnxruntime.py`) para asegurar que los DLLs se incluyan correctamente.

### Tests: mocks para todo lo que toca hardware
- `sounddevice.InputStream` → mock con `.read()` que devuelve arrays numpy
- `onnxruntime.InferenceSession` → mock con `.run()` que devuelve logits ficticios
- `keyboard.add_hotkey` → mock para no registrar hotkeys reales

**Herramientas:** `unittest.mock.patch`, `pytest.fixture`

---

## Key Files Reference

- **src/main.py:58** — `main()`: entry point, inicializa todos los managers
- **src/actions.py:16** — `start()`: inicia grabación + preload modelo
- **src/actions.py:37** — `stop()`: detiene grabación, transcribe, pega
- **src/managers/audio.py:95** — `AudioRecordingManager`: captura + VAD
- **src/managers/transcription.py:76** — `TranscriptionManager.load_model()`: carga ONNX
- **src/managers/transcription.py:200** — `TranscriptionManager.transcribe()`: pipeline Parakeet V3
- **src/managers/model.py** — `ModelManager`: descarga/extracción modelos
- **src/managers/history.py** — `HistoryManager`: SQLite + almacenamiento .wav
- **src/ui/settings_modern.py** — Ventana de settings con tabs (PyQt6)
- **src/utils/paste.py** — `paste_text()`: SendInput para pegar

---

## Tips for Working on This Project

### Añadir un nuevo manager
1. Crear `src/managers/foo.py` con clase `FooManager`
2. Inyectar dependencias en `__init__`, no usar imports globales
3. Registrar en `src/main.py` e inyectar en `actions.py` si necesario
4. Crear `tests/test_foo.py` con mocks

### Cambiar modelo STT
1. Añadir nuevo modelo a `ModelManager.MODELS_REGISTRY`
2. Actualizar `TranscriptionManager` para soportar su formato de salida
3. Actualizar `config.json` → `model.default_model`

### Debuggear audio
- Habilitar logging en `AudioRecordingManager.on_event`
- Verificar `sounddevice.query_devices()` → device_id correcto
- Guardar buffer raw a .wav con `scipy.io.wavfile.write()` para inspeccionar

### Debuggear transcripciones vacías
- Revisar shape de `samples` en `actions.stop()` (debe ser `(N,)` o `(N, 1)`)
- Verificar que vocab.txt tiene `<blk>` y tokens válidos
- Inspeccionar `tokens` devueltos en `TranscriptionManager.transcribe()`
- Probar con audio de ejemplo conocido (ej: grabación de "hola mundo")

### Optimizar build .exe
- Usar `--onefile` solo para distribución final (lento al arrancar)
- Modo `--onedir` más rápido para desarrollo
- Excluir módulos no usados con `--exclude-module` (ej: matplotlib si no se usa)

---

## Versionado y Releases

### Sistema de versiones

**Punto único de verdad:** `src/__version__.py`

```python
__version__ = "1.0.0"
```

Este archivo es importado por:
- `src/main.py` — AppUserModelID de Windows
- `src/managers/updater.py` — comparación de versiones
- `src/ui/web_settings/api.py` — mostrar versión en UI

**También actualizar manualmente:**
- `installer/WhisperCheap.iss` línea 4: `AppVersion=X.Y.Z`

### Sistema de actualizaciones automáticas

La app detecta nuevas versiones via GitHub Releases API y permite actualizar desde Settings → About.

**Archivos involucrados:**
- `src/__version__.py` — versión actual
- `src/managers/updater.py` — `UpdateManager` (check, download, install)
- `src/ui/web_settings/api.py` — métodos expuestos a JS
- `src/ui/web_settings/app.js` — UI de updates

**Configuración del repositorio** (`src/managers/updater.py`):
```python
GITHUB_OWNER = "afeding"  # Tu usuario/org de GitHub
GITHUB_REPO = "whisper-cheap"
INSTALLER_ASSET_NAME = "WhisperCheapSetup.exe"
```

**Flujo de actualización:**
1. App inicia → `check_async()` en background (no bloquea)
2. Cache en `%APPDATA%/whisper-cheap/update_cache.json` (cooldown 6h)
3. Usuario abre Settings → About → ve estado de updates
4. Si hay update → botón "Download and Install"
5. Click → descarga a `%TEMP%`, verifica SHA256, ejecuta `/silent`
6. Inno Setup cierra app, instala sobre versión existente, reinicia

### Checklist para publicar una release

```
□ 1. Actualizar versión
      - src/__version__.py → __version__ = "X.Y.Z"
      - installer/WhisperCheap.iss → AppVersion=X.Y.Z

□ 2. Commit de versión
      git add src/__version__.py installer/WhisperCheap.iss
      git commit -m "chore: bump version to X.Y.Z"

□ 3. Build de la aplicación
      pyinstaller build_config.spec

□ 4. Build del instalador
      # Si ISCC está en PATH:
      ISCC installer/WhisperCheap.iss

      # Si no:
      & "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" ".\installer\WhisperCheap.iss"

      # Output: dist/installer/WhisperCheapSetup.exe

□ 5. Crear tag y push
      git tag vX.Y.Z
      git push origin master --tags

□ 6. Crear GitHub Release
      - Ir a: https://github.com/afeding/whisper-cheap/releases/new
      - Tag: vX.Y.Z
      - Título: vX.Y.Z
      - Descripción: changelog/notas de la versión
      - Adjuntar: dist/installer/WhisperCheapSetup.exe
      - Publicar release

□ 7. Verificar
      - GitHub genera SHA256 automáticamente para el asset
      - La app detectará el update en el próximo check (o forzar con "Check Now")
```

### Troubleshooting de releases

**"El proceso no tiene acceso al archivo" al compilar:**
Windows Defender escanea archivos mientras Inno Setup comprime. Soluciones:
1. Reintentar (a veces el escaneo ya terminó)
2. Añadir exclusión temporal:
   ```powershell
   Add-MpPreference -ExclusionPath "D:\1.SASS\whisper-cheap\dist"
   # Después de compilar:
   Remove-MpPreference -ExclusionPath "D:\1.SASS\whisper-cheap\dist"
   ```

**La app no detecta el update:**
- Verificar que `GITHUB_OWNER` y `GITHUB_REPO` son correctos en `updater.py`
- El asset debe llamarse exactamente `WhisperCheapSetup.exe`
- El tag debe ser formato `vX.Y.Z` (ej: `v1.1.0`)
- Esperar 6h o usar "Check Now" en Settings para bypass del cache

**El instalador no cierra la app anterior:**
- Inno Setup espera a que el proceso termine
- Si la app no cierra, `os._exit(0)` fuerza el cierre
- Verificar que no hay procesos zombie en Task Manager

### Versionado semántico

Usar [SemVer](https://semver.org/):
- **MAJOR** (X.0.0): cambios incompatibles en API/config
- **MINOR** (0.X.0): nuevas funcionalidades retrocompatibles
- **PATCH** (0.0.X): bug fixes retrocompatibles

Ejemplos:
- `1.0.0` → `1.0.1`: fix de bug en transcripción
- `1.0.1` → `1.1.0`: nueva feature (ej: soporte para otro modelo)
- `1.1.0` → `2.0.0`: cambio en estructura de config.json que rompe compatibilidad
