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
│   ├── main.py              # Entry point: carga config, inicializa managers, registra hotkeys
│   ├── actions.py           # Capa glue: start/stop/cancel recording
│   ├── managers/            # Lógica de negocio encapsulada
│   │   ├── audio.py         # AudioRecordingManager: sounddevice stream + VAD Silero
│   │   ├── model.py         # ModelManager: descarga/extracción modelos ONNX
│   │   ├── transcription.py # TranscriptionManager: Parakeet V3 pipeline (nemo/encoder/decoder)
│   │   ├── history.py       # HistoryManager: SQLite + almacenamiento audios .wav
│   │   └── hotkey.py        # HotkeyManager: keyboard lib para hotkeys globales
│   ├── ui/
│   │   ├── tray.py          # TrayManager: icono system tray con pystray
│   │   ├── overlay.py       # RecordingOverlay + StatusOverlay (PyQt6 frameless)
│   │   ├── settings_modern.py # Ventana de settings (PyQt6, QTabWidget)
│   │   └── settings_simple.py # Ventana fallback simple
│   ├── utils/
│   │   ├── clipboard.py     # ClipboardManager: pyperclip wrapper
│   │   ├── paste.py         # paste_text: SendInput via pywin32
│   │   └── llm_client.py    # LLMClient: llamadas a OpenRouter
│   └── resources/
│       └── icons/           # (placeholder para iconos del tray)
├── tests/                   # Tests unitarios con pytest + mocks
├── config.json              # Configuración runtime (hotkey, audio, paths, LLM)
├── requirements.txt         # Deps Python
├── build_config.py          # PyInstaller spec
├── IMPLEMENTACION_CHECKLIST.md # Plan de implementación por fases
└── README.md
```

**Archivos de datos (runtime):**
- `.data/` o `%APPDATA%\whisper-cheap\` (configurable en config.json):
  - `models/parakeet-tdt-0.6b-v3-int8/` — archivos ONNX descargados
  - `recordings/` — archivos .wav guardados
  - `history.db` — SQLite con transcripciones

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

### Build standalone .exe
```bash
# PyInstaller (TODO: revisar build_config.py)
pyinstaller build_config.spec
```

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

**Producción:** `%APPDATA%\whisper-cheap\` (PyInstaller debe copiar config.json y adaptarlo).

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

Ver `build_config.spec` para `hiddenimports` y `binaries`.

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
