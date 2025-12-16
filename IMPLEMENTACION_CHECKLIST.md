# Checklist de Implementación - Whisper Cheap (Python Port)

**Objetivo:** Puerto de Handy a Python usando Parakeet V3 STT + OpenRouter LLM, empaquetado como instalable standalone para Windows.

---

## 🎯 Fase 0: Setup Inicial del Proyecto

### 0.1 Estructura base
- [x] Crear estructura de carpetas del proyecto:
  ```
  whisper-cheap/
  ├── src/
  │   ├── __init__.py
  │   ├── main.py              # Entry point
  │   ├── managers/            # Gestores principales
  │   │   ├── __init__.py
  │   │   ├── audio.py         # AudioRecordingManager
  │   │   ├── model.py         # ModelManager
  │   │   ├── transcription.py # TranscriptionManager
  │   │   ├── history.py       # HistoryManager
  │   │   └── hotkey.py        # HotkeyManager
  │   ├── ui/                  # Interfaz (tray + overlays)
  │   │   ├── __init__.py
  │   │   ├── tray.py
  │   │   ├── overlay.py
  │   │   └── settings.py
  │   ├── utils/
  │   │   ├── __init__.py
  │   │   ├── clipboard.py
  │   │   ├── paste.py
  │   │   └── llm_client.py
  │   └── resources/
  │       ├── icons/
  │       └── models/
  ├── requirements.txt
  ├── build_config.py          # PyInstaller config
  └── README.md
  ```

### 0.2 Dependencias Python
- [x] Crear `requirements.txt` con dependencias esenciales:
  ```
  sounddevice>=0.4.6        # Captura de audio
  numpy>=1.24.0             # Procesamiento de arrays
  onnxruntime>=1.16.0       # Silero VAD + Parakeet V3
  keyboard>=0.13.5          # Hotkeys globales (Windows)
  pystray>=0.19.5           # System tray icon
  Pillow>=10.0.0            # Iconos del tray
  pyperclip>=1.8.2          # Gestión del clipboard
  pywin32>=306              # SendInput para paste (Windows)
  requests>=2.31.0          # Descarga de modelos
  httpx>=0.25.0             # Cliente HTTP async (alternativa)
  openai>=1.0.0             # Cliente OpenRouter
  sqlite3                   # Historial (built-in)
  PyQt6>=6.6.0              # UI settings window + overlays
  ```

### 0.3 Configuración inicial
- [x] Crear archivo de configuración `config.json` con valores por defecto:
  - Rutas: `%APPDATA%/whisper-cheap/` (modelos, recordings, DB)
  - Hotkey por defecto (ej: `Ctrl+Shift+Space`)
  - Modo PTT por defecto
  - Configuración de audio (device, VAD threshold)
  - Configuración de modelo (Parakeet V3 int8)

---

## 🎤 Fase 1: Captura de Audio + VAD

### 1.1 AudioRecordingManager - Básico
- [x] **Clase base** `AudioRecordingManager` en `src/managers/audio.py`:
  - [x] Listar dispositivos de entrada disponibles (`sounddevice.query_devices()`)
  - [x] Abrir stream de audio a **16 kHz, mono, float32**
  - [x] Buffer circular para acumular samples mientras graba
  - [x] M?todos: `open_stream(device_id)`, `close_stream()`

### 1.2 Integración Silero VAD
- [x] **Descargar Silero VAD v4** ONNX:
  - URL: `https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.onnx`
  - Guardar en `src/resources/models/silero_vad_v4.onnx`
- [x] **Cargar modelo VAD** con `onnxruntime`:
  ```python
  import onnxruntime as ort
  session = ort.InferenceSession("silero_vad_v4.onnx")
  ```
- [x] **Procesar audio en chunks** de 512 samples (32ms @ 16kHz):
  - [x] Pasar cada chunk por VAD para detectar voz
  - [x] Acumular solo chunks con voz detectada (threshold ~0.5)

### 1.3 Grabación PTT
- [x] M?todos de grabaci?n:
  - [x] `start_recording(binding_id)` ? inicia captura y acumulaci?n
  - [x] `stop_recording(binding_id)` ? detiene y retorna `np.ndarray` con samples
  - [x] `cancel()` ? aborta grabaci?n sin retornar audio
### 1.4 Modos de micrófono
- [x] **Always-on mode**: stream abierto al inicio, solo activa grabaci?n al hotkey
- [x] **On-demand mode**: abre/cierra stream con cada hotkey (latencia inicial mayor)
- [x] Configuraci?n en settings

### 1.5 Emisión de niveles de audio
- [x] Calcular RMS de cada chunk en tiempo real
- [x] Emitir se?al/evento para actualizar overlay (fase posterior)

---

## ⌨️ Fase 2: Hotkeys Globales

### 2.1 HotkeyManager - Registro
- [x] **Clase** `HotkeyManager` en `src/managers/hotkey.py`:
  - [x] Usar librer?a `keyboard` (Windows) para hooks globales
  - [x] M?todo `register_hotkey(combo, on_press_callback, on_release_callback)`
  - [x] Soportar m?ltiples bindings (ej: binding principal + cancel)

### 2.2 Modos PTT vs Toggle
- [x] **Push-to-Talk (PTT)**:
  - `on_press` → llamar `actions.start(binding_id)`
  - `on_release` → llamar `actions.stop(binding_id)`
- [x] **Toggle**:
  - `on_press` → alternar estado (si idle→start, si recording→stop)
- [x] Flag en configuraci?n para elegir modo

### 2.3 Acciones mapeadas
- [x] Crear m?dulo `actions.py` con:
  - [x] `start(binding_id)` ? precarga modelo, inicia grabaci?n, cambia tray/overlay
  - [x] `stop(binding_id)` ? detiene grabaci?n, transcribe, post-procesa, pega
  - [x] `cancel()` ? aborta grabaci?n actual, limpia estado

---

## 🤖 Fase 3: Gestión de Modelos (Parakeet V3)

### 3.1 ModelManager - Registro
- [x] **Clase** `ModelManager` en `src/managers/model.py`:
  - [x] Cat?logo de modelos (solo Parakeet V3 int8 por ahora):
    ```python
    MODELS = {
        "parakeet-v3-int8": {
            "id": "parakeet-v3-int8",
            "name": "Parakeet V3 INT8",
            "url": "https://blob.handy.computer/parakeet-v3-int8.tar.gz",
            "size_mb": 478,
            "is_directory": True,
            "extract_to": "parakeet-tdt-0.6b-v3-int8"
        }
    }
    ```
  - [x] M?todo `get_model_path(model_id)` ? `%APPDATA%/whisper-cheap/models/`
  - [x] M?todo `is_downloaded(model_id)` ? verifica directorio existe y no hay `.partial`/`.extracting`

### 3.2 Descarga con reanudación
- [x] **M?todo** `download_model(model_id, progress_callback)`: 
  - [x] Usar `requests` con header `Range: bytes=<partial_size>-`
  - [x] Escribir en archivo `.partial` en modo append
  - [x] Comparar tama?o final con `Content-Length` esperado
  - [x] Emitir eventos de progreso (bytes descargados, %, velocidad)

### 3.3 Extracción de tar.gz
- [x] **M?todo** `extract_model(model_id)`: 
  - [x] Crear carpeta temporal `<extract_to>.extracting`
  - [x] Extraer con `tarfile.open(tar_path).extractall(extracting_dir)`
  - [x] Al completar, renombrar `.extracting` a nombre final
  - [x] Borrar archivo `.tar.gz` y `.partial`
  - [x] Emitir eventos: `extraction-started`, `extraction-completed`, `extraction-failed`

### 3.4 Limpieza de arranque
- [x] Al iniciar app:
  - [x] Buscar archivos `.partial` o `.extracting` hu?rfanos
  - [x] Preguntar al usuario si quiere reanudar/borrar o limpiar autom?ticamente
  - [x] Validar modelos descargados (que existan todos los archivos)

---

## 🗣️ Fase 4: Transcripción (Parakeet V3)

### 4.1 TranscriptionManager - Carga de modelo
- [x] **Clase** `TranscriptionManager` en `src/managers/transcription.py`:
  - [x] M?todo `load_model(model_id)` as?ncrono:
    - [x] Validar que `is_downloaded(model_id) == True`
    - [x] Cargar con `onnxruntime` (o FunASR si usas wrapper):
      ```python
      self.session = ort.InferenceSession(
          f"{model_path}/model.onnx",
          providers=['CPUExecutionProvider']  # o DirectML en Windows
      )
      ```
    - [x] Emitir eventos: `loading-started`, `loading-completed`, `loading-failed`
    - [x] Flag `is_loading` + condvar para serializar cargas

### 4.2 Precarga as?ncrona
- [x] En `actions.start()`: 
  - [x] Si modelo no est? cargado, lanzar `load_model()` en thread/async
  - [x] Continuar con grabaci?n mientras carga en background
  - [x] Al llamar `transcribe()`, esperar a que termine de cargar (condvar/flag)

### 4.3 Pipeline de transcripción
- [x] **M?todo** `transcribe(audio_samples: np.ndarray) -> dict`:
  - [x] **Validar duraci?n m?nima**: si audio <1s, acolchar a 1.25s (rellenar con ceros)
  - [x] **Normalizar audio**: asegurar rango [-1, 1] float32
  - [x] **Preprocesar features** (si usas ONNX raw):
    - [x] Extraer log-Mel spectrogram
    - [x] Pasar por encoder/decoder del modelo
  - [x] **Alternativa**: usar wrapper de FunASR/PaddleSpeech para abstraer pipeline
  - [x] **Retornar**: `{"text": str, "segments": [...]}`

### 4.4 Corrección de palabras personalizadas
- [x] M?todo `apply_custom_words(text: str, custom_words: dict) -> str`:
  - [x] Para cada palabra personalizada en config:
    - [x] Buscar coincidencias con threshold de similitud (ej: Levenshtein ~0.18)
    - [x] Reemplazar por versi?n correcta
  - [x] Ejemplo: "jira" ? "JIRA", "kubernetes" ? "Kubernetes"

### 4.5 Gestión de ciclo de vida
- [x] **Model unload timeout**:
  - [x] Timer que descarga modelo tras X minutos de inactividad
  - [x] Opciones: "Immediately", "5 min", "15 min", "30 min", "Never"
  - [x] Si config = "Immediately", descargar justo después de transcribir

---

## ✨ Fase 5: Post-procesamiento LLM (OpenRouter)

### 5.1 LLM Client
- [x] **Clase** `LLMClient` en `src/utils/llm_client.py`:
  - [x] SDK oficial `openrouter` como camino principal (fallback a cliente `openai` con `base_url=https://openrouter.ai/api/v1` si falta el SDK).
    ```python
    from openrouter import OpenRouter
    client = OpenRouter(
        api_key=config["openrouter_api_key"],
        default_headers={
            "HTTP-Referer": "https://github.com/yourusername/whisper-cheap",
            "X-Title": "Whisper Cheap"
        }
    )
    # Fallback: OpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)
    ```

### 5.2 Post-procesamiento
- [x] **Metodo** `postprocess(text: str, prompt_template: str, model: str) -> str | None`:
  - [x] Valida `api_key`, `model` y `prompt_template` (prompt fijo "Transcription 2.0")
  - [x] Mensajes: `system` + `user` (transcripcion cruda)
  - [x] Llamada OpenRouter con `provider`:
    - Si el modelo tiene providers fijos (ej. `gpt-oss-20b`->`groq`, `gemini-2.5-flash-lite`->`google-ai-studio`/`google-vertex`, `mistral-small-3.2-24b-instruct`->`mistral`), se envia {"only": [...], "allow_fallbacks": true}
    - Si no, se usa {"sort": "throughput", "allow_fallbacks": true}
  - [x] Fallback automatico al cliente OpenAI con extra_body={"provider": ...} si falta el SDK
  - [x] Si falla o respuesta vacia, retornar `None` para usar texto original

### 5.3 Configuracion en Settings
- [x] Toggle "Enable LLM post-processing"
- [x] Campos:
  - API Key (input password)
  - Selector de modelo con lista limitada scrolleable (defaults JSON) + add/remove/reset + filtro rapido
- [x] Boton "Test" para validar configuracion (usa modelo seleccionado y provider rules)

---

## 📋 Fase 6: Clipboard y Pegado

### 6.1 Métodos de pegado
- [x] **Módulo** `src/utils/paste.py`:
  - [x] **Ctrl+V**:
    ```python
    import win32api, win32con
    # SendInput: VK_CONTROL down, VK_V press, VK_CONTROL up
    ```
  - [x] **Shift+Insert**:
    ```python
    # SendInput: VK_SHIFT down, VK_INSERT press, VK_SHIFT up
    ```
  - [x] **Direct** (escribir caracteres):
    ```python
    import keyboard
    keyboard.write(text)
    ```
  - [x] **None**: no pegar, solo guardar en historial

### 6.2 Gestión de clipboard
- [x] **Clase** `ClipboardManager` en `src/utils/clipboard.py`:
  - [x] `save_current()` → guardar contenido actual del clipboard
  - [x] `set_text(text)` → escribir nuevo texto al clipboard
  - [x] `restore()` → restaurar contenido guardado
  - [x] Usar `pyperclip` o `win32clipboard`

### 6.3 Políticas de clipboard
- [x] **DontModify**: guardar → escribir → pegar → restaurar (50ms entre pasos)
- [x] **CopyToClipboard**: escribir → pegar → dejar texto nuevo en clipboard
- [x] Configurar en settings: radio buttons "Don't modify" / "Copy to clipboard"

### 6.4 Delays de seguridad
- [x] Añadir `time.sleep(0.05)` entre escribir clipboard y enviar tecla
- [x] Añadir `time.sleep(0.05)` después de pegar antes de restaurar
- [x] Hacen el pegado más confiable en distintas apps

---

## 💾 Fase 7: Historial y Persistencia

### 7.1 Base de datos SQLite
- [x] **Clase** `HistoryManager` en `src/managers/history.py`:
  - [x] Crear DB en `%APPDATA%/whisper-cheap/history.db`
  - [x] Schema (migraci?n v1):
    ```sql
    CREATE TABLE transcription_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        saved BOOLEAN DEFAULT 0,
        title TEXT,
        transcription_text TEXT NOT NULL,
        post_processed_text TEXT,
        post_process_prompt TEXT
    );
    ```
  - [x] M?todos: `insert_entry()`, `get_all()`, `mark_saved(id)`, `delete_old()`

### 7.2 Guardado de WAV
- [x] **M?todo** `save_audio(samples: np.ndarray, timestamp: int) -> str`:
  - [x] Convertir float32 a int16 PCM:
    ```python
    samples_int16 = (samples * 32767).astype(np.int16)
    ```
  - [x] Guardar con `scipy.io.wavfile` o `wave`:
    ```python
    import wave
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(16000)
        wf.writeframes(samples_int16.tobytes())
    ```
  - [x] Ruta: `%APPDATA%/whisper-cheap/recordings/whisper-cheap-<timestamp>.wav`
  - [x] Retornar nombre de archivo

### 7.3 Retención y limpieza
- [x] **Pol?ticas de retenci?n**:
  - `PreserveLimit`: mantener últimas N entradas (default: 100)
  - `ThreeDays`, `TwoWeeks`, `ThreeMonths`: borrar más antiguas que X días
  - `Never`: no borrar nada
- [x] **M?todo** `cleanup(policy, limit_or_days)`: 
  - [x] No borrar entradas con `saved == True`
  - [x] Borrar WAV + fila de DB de entradas antiguas
- [x] Ejecutar cleanup al arrancar app y opcionalmente cada 24h

---

## 🖼️ Fase 8: UI - System Tray

### 8.1 TrayIcon con pystray
- [x] **Clase** `TrayManager` en `src/ui/tray.py`:
  - [x] Cargar 3 iconos: `idle.png`, `recording.png`, `transcribing.png`
  - [x] Crear menu con opciones:
    - "Settings" → abrir ventana de settings
    - "Cancel" → llamar `actions.cancel()`
    - "Quit" → salir de la app
  - [x] Método `set_state(state)` → cambiar icono según estado

### 8.2 Estados visuales
- [x] **Idle**: icono gris/blanco
- [x] **Recording**: icono rojo + animación (opcional)
- [x] **Transcribing**: icono amarillo/naranja
- [x] **Formatting** (durante LLM): icono azul (opcional)

---

## 🪟 Fase 9: UI - Overlays

### 9.1 Overlay de grabación
- [x] **Clase** `RecordingOverlay` en `src/ui/overlay.py`:
  - [x] Ventana PyQt6 siempre on-top, sin bordes, semi-transparente
  - [x] Mostrar texto "Recording..." + barra de nivel de audio (RMS)
  - [x] Posición configurable: bottom-center, top-center, etc.
  - [x] Método `show()`, `hide()`, `update_level(rms)`

### 9.2 Overlay de transcripción/formatting
- [ ] Ventana similar mostrando "Transcribing..." o "Formatting..."
- [ ] Sin barra de nivel, solo texto
- [ ] Auto-ocultar tras completar

### 9.3 Configuración de overlay
- [x] Toggle "Show overlay" en settings
- [x] Selector de posición (bottom/top)
- [x] Slider de opacidad (0.5 - 1.0)

---

## ⚙️ Fase 10: UI - Settings Window

### 10.1 Ventana principal de Settings
- [x] **Clase** `SettingsWindow` en `src/ui/settings.py`:
  - [x] Usar PyQt6 QDialog con tabs/páginas
  - [x] Cargar config actual desde `config.json`
  - [x] Guardar cambios al hacer clic en "Save"

### 10.2 Tabs/Secciones

#### General
- [x] Hotkey input (texto básico - selector interactivo es muy complejo)
- [x] Radio: Push-to-Talk / Toggle
- [x] Checkbox: Show overlay
- [x] Checkbox: Start on system boot

#### Audio
- [x] Dropdown: seleccionar micrófono (listar dispositivos)
- [x] Checkbox: Use VAD

#### Models
- [x] Dropdown: Unload timeout (Immediately, 5min, 15min, 30min, Never)

#### Post-processing
- [x] Checkbox: Enable LLM post-processing
- [x] Input: OpenRouter API Key (password)
- [x] Input: Model (text, ej: `anthropic/claude-3.5-sonnet`)
- [x] Textarea: Prompt template (con placeholder `${output}`)
- [x] Botón: "Test configuration" (hace request de prueba a OpenRouter)

#### Clipboard/Paste
- [x] Combobox: método de pegado (None / Ctrl+V / Shift+Insert / Direct) - **Implementado en tab General**
- [x] Combobox: política de clipboard (Don't modify / Copy to clipboard) - **Implementado en tab General**

#### History
- [x] Combobox: Retention policy (preserve_limit / 3_days / 7_days / 30_days / never)
- [x] Input: Limit (si preserve_limit) (número, habilitado/deshabilitado dinámicamente)
- [x] Listbox: últimas 50 transcripciones (timestamp, texto, indicador ★ si saved)
- [x] Botón: "Refrescar" para recargar lista
- [x] Botón: "Open recordings folder"

#### About
- [x] Versión de la app (hardcoded 1.0.0)
- [ ] Links: GitHub, documentación - **NO IMPLEMENTADO** (no hay repo público aún)
- [x] Botones: "Open app data folder", "Open recordings folder"

---

## 📦 Fase 11: Empaquetado para Windows

### 11.1 PyInstaller setup
- [x] Crear `build_config.spec` para PyInstaller:
  ```python
  # -*- mode: python ; coding: utf-8 -*-
  a = Analysis(
      ['src/main.py'],
      pathex=[],
      binaries=[],
      datas=[
          ('src/resources', 'resources'),  # iconos, models
      ],
      hiddenimports=['onnxruntime', 'sounddevice', ...],
      hookspath=[],
      hooksconfig={},
      runtime_hooks=[],
      excludes=[],
      win_no_prefer_redirects=False,
      win_private_assemblies=False,
      cipher=None,
      noarchive=False,
  )
  pyz = PYZ(a.pure, a.zipped_data, cipher=None)
  exe = EXE(
      pyz,
      a.scripts,
      a.binaries,
      a.zipfiles,
      a.datas,
      [],
      name='WhisperCheap',
      debug=False,
      bootloader_ignore_signals=False,
      strip=False,
      upx=True,
      upx_exclude=[],
      runtime_tmpdir=None,
      console=False,  # no mostrar consola
      icon='src/resources/icons/app.ico',
  )
  ```

### 11.2 Build del ejecutable
- [x] Comando: `pyinstaller build_config.spec`
- [x] Fix: config.json se busca junto al .exe (no en carpeta temporal de PyInstaller)
- [x] Fix: crear config.json por defecto si no existe
- [ ] Verificar que el `.exe` funciona standalone (sin Python instalado) - **EN PROGRESO**
- [ ] Probar en máquina limpia (VM Windows)

### 11.3 Instalador con Inno Setup
- [ ] Crear script `.iss` para Inno Setup:
  - [ ] Copiar ejecutable a `Program Files\WhisperCheap\`
  - [ ] Crear acceso directo en menú inicio
  - [ ] Opción: iniciar al arrancar Windows (registro/Task Scheduler)
  - [ ] Desinstalador que limpia carpetas de datos
- [ ] Generar instalador `WhisperCheap-Setup.exe`

### 11.4 Descarga de modelo en primer arranque
- [ ] Al iniciar app por primera vez:
  - [ ] Si no hay modelo descargado, mostrar diálogo:
    - "WhisperCheap requires the Parakeet V3 model (~478 MB). Download now?"
  - [ ] Si acepta, iniciar descarga en background
  - [ ] Mostrar progreso en settings window
- [ ] NO incluir modelo en instalador para mantener tamaño pequeño

---

## 🔧 Fase 12: Integración y Testing

### 12.1 Flujo completo end-to-end
- [ ] Probar flujo: hotkey down → grabación → hotkey up → transcripción → post-proceso → pegado
- [ ] Validar todos los estados del tray cambian correctamente
- [ ] Validar overlay se muestra y oculta en momentos correctos

### 12.2 Casos edge
- [ ] Presionar hotkey muy rápido (audio <1s) → debe acolchar
- [ ] Cancelar grabación antes de soltar → debe limpiar estado
- [ ] Cerrar app mientras graba → debe liberar recursos
- [ ] Modelo no descargado → debe mostrar error y no intentar transcribir
- [ ] API OpenRouter falla → debe usar texto original sin error

### 12.3 Limpieza de recursos
- [ ] Al cerrar app:
  - [ ] Detener streams de audio
  - [ ] Descargar modelo de memoria si es grande
  - [ ] Cerrar conexión a DB
  - [ ] Guardar config actual

### 12.4 Logs y debugging
- [ ] Configurar logging a archivo: `%APPDATA%/whisper-cheap/logs/app.log`
- [ ] Niveles: INFO para eventos normales, ERROR para fallos
- [ ] Rotación de logs (max 10 MB, mantener últimos 5)

---

## 🚀 Fase 13: Optimizaciones y Pulido

### 13.1 Performance
- [ ] Medir latencia total (hotkey up → paste): objetivo <3s para audio corto
- [ ] Cachear modelo en memoria si unload timeout != Immediately
- [ ] Usar DirectML provider si disponible en Windows para GPU inference

### 13.2 UX mejoras
- [ ] Sonido de feedback al iniciar/terminar grabación (opcional)
- [ ] Notificación de escritorio al completar (opcional)
- [ ] Atajos de teclado en settings window (Ctrl+S para guardar)

### 13.3 Autostart
- [ ] Registrar en `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- [ ] Opción en settings para habilitar/deshabilitar

### 13.4 Actualizaciones
- [ ] Check for updates al arrancar (opcional):
  - Consultar endpoint de GitHub releases
  - Notificar al usuario si hay versión nueva
  - Link para descargar instalador actualizado

---

## 📚 Fase 14: Documentación

### 14.1 README.md
- [ ] Descripción del proyecto
- [ ] Screenshot del tray + overlay
- [ ] Instrucciones de instalación
- [ ] Configuración básica (hotkey, modelo, OpenRouter)
- [ ] FAQ común

### 14.2 Documentación técnica
- [ ] Arquitectura del código (diagrama de managers)
- [ ] Guía de contribución
- [ ] Cómo agregar soporte para otros modelos STT

### 14.3 Changelog
- [ ] Mantener `CHANGELOG.md` con versiones y cambios

---

## ✅ Criterios de Completitud

Antes de considerar el proyecto "feature-complete":

1. ✅ Usuario puede instalar ejecutable sin dependencias externas
2. ✅ Hotkey funciona globalmente en Windows (PTT y Toggle)
3. ✅ Audio se graba con VAD Silero correctamente
4. ✅ Modelo Parakeet V3 se descarga, carga y transcribe audio en español/inglés
5. ✅ Post-procesamiento LLM opcional funciona con OpenRouter
6. ✅ Pegado funciona en cualquier app (notepad, browser, etc.)
7. ✅ Historial persiste en DB y WAV se guardan
8. ✅ Settings window permite configurar todo sin editar JSON
9. ✅ Tray icon y overlays reflejan estado correctamente
10. ✅ App puede correr al inicio de Windows automáticamente

---

## 🎯 Orden de Implementación Recomendado

**Sprints propuestos** (en orden de prioridad):

1. **Sprint 1 - Core funcional**: Fase 0, 1, 2, 4 (sin UI)
   - Objetivo: grabar audio, transcribir con Parakeet, imprimir resultado en consola

2. **Sprint 2 - Gestión de modelos**: Fase 3
   - Objetivo: descargar y cargar modelo automáticamente

3. **Sprint 3 - Output y persistencia**: Fase 6, 7
   - Objetivo: pegar texto transcrito, guardar historial

4. **Sprint 4 - UI básica**: Fase 8, 9
   - Objetivo: tray icon funcional, overlays visuales

5. **Sprint 5 - Settings y LLM**: Fase 5, 10
   - Objetivo: ventana de configuración completa, post-proceso opcional

6. **Sprint 6 - Packaging**: Fase 11
   - Objetivo: instalador Windows standalone

7. **Sprint 7 - Polish**: Fase 12, 13, 14
   - Objetivo: testing, optimizaciones, documentación

---

---

## 📌 Pendiente

- [ ] GitHub repo público - crear y configurar

**Ultima actualizacion**: 2025-12-14
**Estado**: Core + LLM + settings modernos completos; pendientes empaquetado final, pruebas end-to-end y documentacion
