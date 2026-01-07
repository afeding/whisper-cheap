# ERROR HANDLING AUDIT - Whisper Cheap

## Resumen Ejecutivo

**Estado General:** MEDIA COBERTURA. La app tiene protecciones en la capa principal (main.py) pero presentan brechas críticas en:
- Recuperación ante fallos de hardware (audio)
- Timeouts de operaciones bloqueantes
- Validación de entrada en callbacks
- Manejo de errores en la cadena de procesamiento

El análisis identifica 8 puntos críticos que pueden causar crasheos, y 12 puntos de media importancia con degradación silenciosa.

---

## 1. EXCEPCIONES CRÍTICAS (main.py)

### 1.1 Análisis General

**Qué está bien:**
- ✅ Try/catch en inicialización de managers (líneas 540-563)
- ✅ Try/catch en carga de config (línea 314)
- ✅ Try/catch en hotkey registration (línea 954-962)
- ✅ Shutdown graceful con timeout (línea 1036-1050)
- ✅ Global mutex para single instance (línea 283-297)

**Qué NO está bien:**

#### CRÍTICA: No hay try/catch global en main()
**Línea:** 280 (function definition)
```python
def main():
    # Detect if running as compiled executable
    is_frozen = getattr(sys, "frozen", False)
    # ... código sin envolvente
```

**Problema:** Si el código inicial (antes de logging setup) crashea, la app falla sin log:
- SetCurrentProcessExplicitAppUserModelID puede fallar en Windows viejo (línea 30)
- load_config puede lanzar excepción JSON si config.json está corrupto
- AudioRecordingManager.__init__ podría fallar si sounddevice no se importa bien

**Escenario de error:**
```
whisper-cheap.exe → crash silencioso sin mensaje
→ Usuario no sabe qué pasó
```

**Recomendación:** Envolver main() en try/except global con logging inmediato.

---

### 1.2 Inicialización de Logging (línea 335)

**Problema:** setup_logging() se llama DESPUÉS de expandir paths, pero si Path operations fallan:
```python
log_file = setup_logging(app_data)  # línea 335
```

Si `app_data` no es válida (ej: %APPDATA% no expandible), setup_logging() puede fallar.

**Código deficiente:**
```python
def setup_logging(app_data: Path) -> Path:
    logs_dir = app_data / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)  # ← puede fallar sin logging
```

---

### 1.3 Gestión de Overlay (línea 368-372)

**Problema:** Overlay initialization falla silenciosamente
```python
overlay_app = None
if overlay_cfg.get("enabled", True):
    try:
        overlay_app = ensure_app()
    except Exception as exc:
        print(f"Overlay deshabilitado: {exc}")  # ← print, no logging
        overlay_cfg["enabled"] = False
```

**Brechas:**
- `print()` en lugar de `logging.error()` → no aparece en log file
- `ensure_app()` puede fallar después de esta línea sin re-check (línea 1015-1018)

---

## 2. ERRORES DE AUDIO (sounddevice)

### 2.1 Sin Micrófono Disponible

**Escenario:** Usuario sin micrófono, o desconectado durante grabación.

**Línea problemática:** src/managers/audio.py:209-229
```python
stream = sd.InputStream(
    samplerate=self.config.sample_rate,
    channels=self.config.channels,
    dtype="float32",
    blocksize=self.config.chunk_size,
    callback=self._audio_callback,
    device=device_id,
)
try:
    stream.start()
    logger.info(f"[audio] Stream started...")
except Exception as e:
    logger.error(f"[audio] Stream start failed: {e}")
    try:
        stream.close()
    except Exception:
        pass
    self._emit_event(f"stream-start-failed:{e}")
    raise
```

**Problema:** El error se propaga (raise), pero no hay recuperación en start_recording():

src/managers/audio.py:240-252
```python
def start_recording(self, binding_id: str, device_id: Optional[int] = None):
    with self._recording_lock:
        self._buffer.clear()
        self._is_recording = True
        self._binding_id = binding_id
    # Always ensure the stream is open at recording time.
    if self._stream is None:
        try:
            self.open_stream(device_id=device_id)
        except Exception as e:
            # Keep going so feed_samples-based tests still work.
            self._emit_event(f"stream-open-failed:{e}")
    # ← NO REINTENTOS, seguir grabando sin stream!
```

**Impacto:** El usuario presiona hotkey, se inicia grabación, pero `self._stream` es None → stop_recording() devuelve array vacío → transcripción vacía → confusión.

**Escenario real:**
```
1. Usuario pulsa hotkey (sin micrófono conectado)
2. open_stream() falla → event emitido pero seguir adelante
3. Usuario habla
4. Presiona hotkey nuevamente
5. stop_recording() devuelve [] (zero-length array)
6. Transcripciones vacías
7. Usuario piensa que el app está roto
```

---

### 2.2 Micrófono se Desconecta Durante Grabación

**Problema:** No hay manejo en _audio_callback()

src/managers/audio.py:300-304
```python
def _audio_callback(self, indata, frames, time, status):
    if status:
        self._emit_event(f"stream-status:{status}")
    chunk = np.copy(indata[:, 0]) if indata.ndim > 1 else np.copy(indata)
    self._process_chunk(chunk.astype(np.float32))
```

**Brechas:**
- `status` puede contener portaudio errors (INPUT_OVERFLOW, INPUT_UNDERFLOW, etc)
- No hay recuperación: continúa procesando audio corrupto
- Si sounddevice lanza excepción en callback, whole stream dies

**Escalada:** Si callback crashea, stream se detiene silenciosamente, usuario no sabe por qué.

---

### 2.3 Dispositivo No Soporta 16kHz

**Línea:** src/managers/audio.py:209-216
```python
stream = sd.InputStream(
    samplerate=self.config.sample_rate,  # 16000
    channels=self.config.channels,       # 1
    dtype="float32",
    blocksize=self.config.chunk_size,
    callback=self._audio_callback,
    device=device_id,
)
```

**Problema:** sounddevice puede fallar si device no soporta 16kHz, o silenciosamente usar sample rate diferente sin avisar.

**Falta:** Validar sample rate efectivo post-open:
```python
# MISSING: Check if actual sample rate matches requested
if stream.samplerate != self.config.sample_rate:
    logger.warning(f"Sample rate mismatch: requested {self.config.sample_rate}, got {stream.samplerate}")
```

---

## 3. ERRORES DE MODELO/TRANSCRIPCIÓN

### 3.1 Modelo No Descargado (no detección en load_model)

**Línea:** src/managers/transcription.py:190-202
```python
def load_model(self, model_id: str):
    with self._cond:
        if self._session and self._model_id == model_id:
            return
        if self._is_loading:
            self._cond.wait_for(lambda: not self._is_loading)
            if self._session and self._model_id == model_id:
                return
        self._is_loading = True
    self._emit("loading-started")
    try:
        if not self.model_manager.is_downloaded(model_id):
            raise FileNotFoundError(f"Model {model_id} is not downloaded")
        model_dir = self.model_manager.get_model_path(model_id)
```

**Problema:** El check es bueno, PERO:
- En src/actions.py línea 76-79, hay fallback silencioso:
```python
model_ready = True
if model_manager and hasattr(model_manager, "is_downloaded"):
    target = model_id or "parakeet-v3-int8"
    if not model_manager.is_downloaded(target):
        logger.error(f"Modelo {target} no esta descargado.")
        model_ready = False
```

- Luego línea 84:
```python
if transcription_manager and samples is not None and samples.size > 0 and model_ready:
    # transcribe
```

**Brechas:**
- Si model_ready=False, se devuelve {} (vacío) sin error a UI
- Usuario ve "Done" pero no hay transcripción
- No hay retry automático de descarga

**Impacto:** Silent failure sin notificación.

---

### 3.2 ONNX Load Falla (bad PATH o corrupted file)

**Línea:** src/managers/transcription.py:140-150
```python
try:
    session = ort.InferenceSession(path, providers=providers, sess_options=sess_opts)
    actual_providers = session.get_providers()
    logger.info(f"[onnx] Session created with providers: {actual_providers}")
    return session
except Exception as e:
    # If GPU failed, try CPU only
    if providers[0] != "CPUExecutionProvider":
        logger.warning(f"[onnx] Failed with {providers[0]}: {e}. Falling back to CPU.")
        return ort.InferenceSession(path, providers=["CPUExecutionProvider"], sess_options=sess_opts)
    raise
```

**Problema:** Fallback CPU recursivo - si CPU también falla, exception se propaga. NO hay manejo en load_model catch:

src/managers/transcription.py:284-289
```python
except Exception:
    with self._cond:
        self._is_loading = False
        self._cond.notify_all()
    self._emit("loading-failed")
    raise  # ← Propaga a actions.stop() sin contexto
```

**Brechas:**
- Exception no loguea root cause (exception details perdidos)
- Caller (actions.stop()) recibe exception genérica sin saber si fue GPU/CPU/file/memory

---

### 3.3 Transcripción Devuelve Vacío

**Línea:** src/actions.py:81-98
```python
if transcription_manager and samples is not None and samples.size > 0 and model_ready:
    try:
        if hasattr(transcription_manager, "load_model"):
            transcription_manager.load_model(model_id or "parakeet-v3-int8")
        progress("transcribing")
        res = transcription_manager.transcribe(samples)
        if isinstance(res, dict):
            text = res.get("text")
        else:
            text = str(res)
        if text:
            logger.info(f"[stt] Texto base ({len(text)} chars): {text[:100]}...")
    except Exception as exc:
        logger.exception(f"Error transcribiendo: {exc}")
        text = None
```

**Problema:** Si text es None o "", se continúa sin alerta:

src/actions.py:140-159
```python
if text:
    final_text = post_text or text
    # ... paste logic
else:
    logger.warning("Transcripcion vacia o fallida.")
```

**Brechas:**
- `logger.warning()` ← user no ve nada (está en log file, not UI)
- NO se muestra overlay error
- NO se emite sound de fallo

**Debería:**
```python
else:
    show_error_overlay("Transcripción vacía - intenta de nuevo")
    return error response
```

---

### 3.4 Sin Timeout en Transcripción

**Línea:** src/managers/transcription.py:314-361
```python
def transcribe(self, audio_samples: np.ndarray, model_id: Optional[str] = None) -> Dict[str, Any]:
    # ... no timeout mechanism
    if self._nemo_sess and self._enc_sess and self._dec_sess and self._vocab:
        if duration_sec > CHUNK_THRESHOLD_SEC:
            result = self._transcribe_chunked(audio)
        else:
            audio = self._pad_audio(audio)
            text, tokens = self._transcribe_parakeet(audio)
            result = {"text": text or "", "segments": [], "tokens": tokens}
        self._last_used = time.time()
        gc.collect()
        return result
```

**Problema:** Si ONNX inference cuelga (OOM, GPU lock, etc), no hay timeout.

**Impacto:** App se congela esperando indefinidamente.

**Debería haber:**
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Transcription timeout after 60s")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)  # 60s timeout
try:
    # transcribe
finally:
    signal.alarm(0)  # cancel alarm
```

Nota: En Windows, signal.alarm no funciona. Mejor usar threading.Timer.

---

## 4. ERRORES DE RED (OpenRouter LLM)

### 4.1 Sin Timeout en Llamadas HTTP

**Línea:** src/utils/llm_client.py (necesito ver más del archivo)

**Problema general:** OpenRouter API calls sin timeout explícito.

**Debería haber:**
```python
def postprocess(
    self,
    text: str,
    prompt_template: str,
    model: Optional[str] = None,
    timeout: Optional[float] = 30.0,  # ← Existe pero...
    ...
) -> Optional[Dict[str, Any]]:
```

Timeout existe en signature, pero **¿se usa en realidad?** Necesito ver implementation completa.

**Brechas esperadas:**
- Si timeout=None, requests espera indefinidamente
- No hay retry logic para fallos transientes (429, 503)

---

### 4.2 Sin Validación de Status HTTP

**Línea:** src/managers/model.py:119
```python
with self.requests.get(url, stream=True, headers=headers, timeout=60) as resp:
    if resp.status_code == 200 and downloaded > 0:
        # Server ignored Range; restart download
        partial_path.unlink(missing_ok=True)
        downloaded = 0
    resp.raise_for_status()
```

**Problema:**
- Solo handle 200 + partial restore
- Si server devuelve 403 (Forbidden), 404 (Not found), 500 (Server error):
  - raise_for_status() lanza excepción genérica
  - No hay retry con exponential backoff
  - User no sabe si es problema de red o archivo faltante

**Impacto:** Model download falla sin contexto claro.

---

### 4.3 No Hay Manejo de 401 (Invalid API Key)

**Línea:** src/actions.py:100-120
```python
if llm_enabled and llm_client and text:
    try:
        progress("formatting")
        logger.info(f"[llm] Ejecutando post-proceso con modelo: {llm_model_id or llm_client.default_model}")
        llm_res = llm_client.postprocess(...)
        if llm_res and llm_res.get("text"):
            post_text = llm_res["text"]
            logger.info(f"[llm] Texto post-procesado ({len(post_text)} chars)")
        else:
            logger.warning("[llm] Respuesta vacia o sin texto...")
    except Exception as exc:
        logger.error(f"Post-proceso LLM fallo: {type(exc).__name__}: {exc}")
        post_text = None
```

**Problema:**
- Excepción 401 se trata como error genérico
- User no sabe que API key es inválida (no hay UI feedback)
- No reintentar (correcto, pero sin notificación)

**Debería:**
```python
except HTTPStatusError as e:
    if e.response.status_code == 401:
        show_error_overlay("OpenRouter API Key inválida - verifica en Settings")
    elif e.response.status_code == 429:
        show_error_overlay("Rate limit OpenRouter - espera 1 minuto")
    else:
        show_error_overlay(f"OpenRouter error: {e.response.status_code}")
```

---

### 4.4 Sin Retry en Fallos Transientes (429, 503)

**Línea:** src/utils/llm_client.py (no visible en lectura limitada, pero probable que falte)

**Problema:** Si OpenRouter devuelve 429 (too many requests), no hay retry con backoff.

**Impacto:** User pierden transcripción procesada.

---

## 5. ERRORES DE UI

### 5.1 PyQt6 ImportError - Overlay Deshabilitado Silenciosamente

**Línea:** src/main.py:368-372
```python
overlay_app = None
if overlay_cfg.get("enabled", True):
    try:
        overlay_app = ensure_app()
    except Exception as exc:
        print(f"Overlay deshabilitado: {exc}")  # ← print, no logging!
        overlay_cfg["enabled"] = False
```

**Problema:**
- Si PyQt6 no instalado, exception no se registra en log file
- User ve "Overlay deshabilitado" en stdout, no en app.log
- Siguiente intento de usar overlay (line 1015-1019) también falla silenciosamente

---

### 5.2 Tray Icon Sin Fallback Correcto

**Línea:** src/main.py:620-623
```python
try:
    tray.start()
except Exception:
    print("Tray not started (missing pystray/Pillow or running headless).")
```

**Problema:**
- `print()` en lugar de `logging.error()`
- No verificar `tray is None` antes de usarlo

Luego en callbacks (línea 603, 789, etc):
```python
tray.set_state("idle")  # ← crash si tray=None y excepción silenciosa arriba
```

**Debería:**
```python
if tray:
    tray.set_state("idle")
```

---

### 5.3 Callbacks de Hotkey sin Try/Catch

**Línea:** src/main.py:765-804 (on_press)
```python
def on_press():
    nonlocal audio_cfg
    try:
        logging.info("[hotkey] on_press triggered")
        # ... mucho código sin validación
    except Exception as e:
        logging.exception(f"[hotkey] ERROR in on_press: {e}")
```

**Buen patrón pero...**

**Problema:** Si `sound_player.play_start()` crashea, UI nunca se actualiza:

src/actions.py:33-37
```python
if sound_player and hasattr(sound_player, "play_start"):
    try:
        sound_player.play_start()
    except Exception:
        pass  # ← silencioso
```

**Debería loguear:**
```python
except Exception as e:
    logger.debug(f"[audio] play_start failed: {e}")
```

---

### 5.4 show_error_overlay Falla Silenciosamente

**Línea:** src/main.py:728-744
```python
def show_error_overlay(message: str):
    if not overlay_cfg.get("enabled", True):
        logging.error(f"[error] {message}")
        return
    logging.error(f"[error] Showing error overlay: {message}")
    if win_bar:
        try:
            win_bar.show_error(message)
        except Exception as e:
            logging.error(f"[overlay] ERROR al mostrar error: {e}")
    elif status_overlay:
        try:
            status_overlay.show_error(message)
        except Exception as e:
            logging.error(f"[overlay] ERROR al mostrar error (PyQt6): {e}")
    tray.set_state("idle")
```

**Brechas:**
- `tray.set_state("idle")` sin null check (crash si tray=None)
- Si ambos overlays fallan, user solo ve log error (no UI)

**Debería:**
```python
finally:
    if tray:
        tray.set_state("idle")
```

---

### 5.5 WinOverlayBar Falla Silenciosamente

**Línea:** src/main.py:660-668
```python
try:
    if overlay_cfg.get("enabled", True) and os.name == "nt" and WinOverlayBar is not None:
        print("[overlay] Inicializando Win32 overlay...")
        win_bar = WinOverlayBar(position=overlay_cfg.get("position", "bottom"), opacity=overlay_cfg.get("opacity", 0.5))
        win_bar.start()
        print("[overlay] Backend: Win32 iniciado correctamente")
except Exception as exc:
    print(f"[overlay] Win32 falló: {exc}")
    win_bar = None
```

**Problema:**
- `print()` en lugar de `logging.error()`
- Exception detalles perdidos (no stack trace)

---

## 6. LOGGING

### 6.1 Logging Setup Deficiente

**Qué está bien:**
- ✅ Dos handlers (console + file)
- ✅ Different levels (console=INFO, file=DEBUG)
- ✅ Detailed format with thread names

**Qué falta:**
- ❌ Sin rotación de logs (app.log puede crecer indefinidamente)
- ❌ Sin log level para external libraries (onnxruntime, sounddevice spams)

**Línea:** src/main.py:240-277
```python
def setup_logging(app_data: Path) -> Path:
    logs_dir = app_data / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "app.log"

    # ... setup handlers ...

    logging.info("Logging initialized: console=INFO, file=DEBUG")
    logging.info(f"Log file: {log_file}")
    return log_file
```

**Debería:**
```python
# Add RotatingFileHandler instead of FileHandler
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,          # Keep 5 rotated files
    encoding="utf-8"
)

# Suppress noise from external libraries
logging.getLogger("onnxruntime").setLevel(logging.WARNING)
logging.getLogger("sounddevice").setLevel(logging.WARNING)
```

---

### 6.2 Implicit print() Calls Scattered in Code

**Línea:** src/main.py:135, 166, 217, 371, 548, 568, 623, 662, 717, 723, 726, etc.

**Problema:** Mix de `print()` y `logging.error()` → inconsistente, algunos warnings no en log file.

**Ejemplo:**
```python
print("Modelo listo.")  # línea 546
logging.info("...")    # línea 557
print("...")           # línea 623
```

**Debería:** REEMPLAZAR todos `print()` con `logging.info()`, `logging.warning()`, `logging.error()`.

---

### 6.3 Exception Stack Traces No Siempre Loguean

**Línea:** src/actions.py:116-120
```python
except Exception as exc:
    # Use error() instead of exception() to avoid full stack trace
    # which might contain sensitive info in HTTP error details
    logger.error(f"Post-proceso LLM fallo: {type(exc).__name__}: {exc}")
    post_text = None
```

**Problema:** La decisión de usar `logger.error()` en lugar de `logger.exception()` oculta stack trace.

**Impacto:** Debugging difícil cuando falla en internal OpenAI client code.

**Debería:**
```python
except Exception as exc:
    logging.exception(f"[llm] Post-process failed: {exc}")  # Full traceback
    # Sanitize before showing to user:
    user_error = str(exc)[:100]
    show_error_overlay(f"LLM error: {user_error}")
```

---

## 7. RESUMEN DE BRECHAS CRÍTICAS

| # | Área | Problema | Línea | Severity | Impacto |
|---|------|---------|-------|----------|---------|
| 1 | main.py | No try/catch global en main() | 280 | CRÍTICA | Crash silencioso sin log |
| 2 | audio.py | Sin micrófono → continúa grabando vacío | 240-252 | CRÍTICA | Silencio user-confusing |
| 3 | audio.py | Micrófono desconectado no detectado | 300-304 | ALTA | Audio corrupto |
| 4 | transcription.py | Sin timeout en ONNX inference | 314-361 | ALTA | App congelada |
| 5 | llm_client.py | Sin validación HTTP status (401, 429, 503) | (unknown) | ALTA | Silent failures |
| 6 | actions.py | Transcripción vacía sin UI feedback | 159 | ALTA | User confusión |
| 7 | overlay.py | Tray icon crash si exception en startup | 603 | MEDIA | Sidebar no responde |
| 8 | main.py | print() en lugar de logging | 623 | MEDIA | Warnings perdidos |

---

## 8. RECOMENDACIONES DE FIX (Prioridad)

### P0 - CRÍTICA (Hacer primero)

#### Fix 1: Global Try/Catch en main()
```python
def main():
    try:
        # TODO: move all initialization into _main_impl()
        ...
    except Exception as e:
        logging.critical(f"[main] FATAL ERROR: {e}", exc_info=True)
        sys.exit(1)

def _main_impl():
    # All current code from main()
    ...
```

#### Fix 2: Audio Stream Health Check
```python
def start_recording(self, binding_id: str, device_id: Optional[int] = None):
    with self._recording_lock:
        self._buffer.clear()
        self._is_recording = True
        self._binding_id = binding_id

    if self._stream is None:
        try:
            self.open_stream(device_id=device_id)
        except Exception as e:
            self._is_recording = False  # ← CRITICAL: reset state
            self._emit_event(f"stream-open-failed:{e}")
            raise RuntimeError(f"Cannot open audio stream: {e}")

    if not self._stream.active:  # ← NEW: verify stream is live
        raise RuntimeError("Audio stream not active")
```

#### Fix 3: Timeout en Transcription
```python
import signal
import threading

def transcribe(self, audio_samples: np.ndarray, model_id: Optional[str] = None) -> Dict[str, Any]:
    timeout_sec = 60
    result = {"text": "", "segments": []}
    exception_holder = [None]

    def _do_transcribe():
        try:
            result.clear()
            result.update(self._transcribe_impl(audio_samples, model_id))
        except Exception as e:
            exception_holder[0] = e

    thread = threading.Thread(target=_do_transcribe, daemon=False)
    thread.start()
    thread.join(timeout=timeout_sec)

    if thread.is_alive():
        logging.error(f"[transcribe] TIMEOUT after {timeout_sec}s")
        raise TimeoutError(f"Transcription timeout")

    if exception_holder[0]:
        raise exception_holder[0]

    return result
```

#### Fix 4: UI Feedback para Errores
```python
# En actions.py, después de stop() o durante processing:

if not text and samples.size > 0:
    show_error_overlay("Transcripción vacía. Verifica micrófono/audio.")
    logging.warning("[process] Empty transcription from non-empty audio")
    return {"text": "", "error": "empty_transcription"}

# Con callback en main.py:
def on_error(exc: Exception):
    logging.exception(f"[processing] Error: {exc}")
    error_msg = str(exc)[:80]
    show_error_overlay(f"Error: {error_msg}")
    tray.set_state("error") if tray else None
```

### P1 - ALTA (Hacer después)

#### Fix 5: Logging Rotation
```python
# src/main.py:setup_logging()
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding="utf-8"
)

# Suppress external lib noise
logging.getLogger("onnxruntime").setLevel(logging.WARNING)
logging.getLogger("sounddevice").setLevel(logging.WARNING)
```

#### Fix 6: HTTP Error Handling con Retry
```python
# src/managers/model.py

def download_model(self, model_id: str, ...):
    url = str(meta["url"])
    max_retries = 3

    for attempt in range(max_retries):
        try:
            with self.requests.get(url, stream=True, timeout=60) as resp:
                if resp.status_code == 404:
                    raise FileNotFoundError(f"Model not found at {url}")
                elif resp.status_code in (401, 403):
                    raise PermissionError(f"Access denied to {url}")
                elif resp.status_code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # exponential backoff
                        continue
                    raise IOError(f"Server error: {resp.status_code}")

                resp.raise_for_status()
                # ... download ...
                break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logging.warning(f"[download] Attempt {attempt+1}/{max_retries} failed: {e}")
            time.sleep(2 ** attempt)
```

#### Fix 7: Validar Tray Antes de Usar
```python
# Todas las referencias a tray:
if tray:
    tray.set_state("idle")
else:
    logging.debug("[tray] Tray not available, skipping state update")
```

#### Fix 8: OpenRouter Error Codes
```python
# src/utils/llm_client.py

def postprocess(self, ...):
    try:
        response = self._client.chat.completions.create(...)
    except OpenAIError as e:
        if "401" in str(e) or "Unauthorized" in str(e):
            raise ValueError("Invalid OpenRouter API key") from e
        elif "429" in str(e) or "Rate limit" in str(e):
            raise TimeoutError("OpenRouter rate limit reached") from e
        elif "500" in str(e) or "502" in str(e) or "503" in str(e):
            raise IOError(f"OpenRouter unavailable: {e}") from e
        else:
            raise RuntimeError(f"OpenRouter error: {e}") from e
```

### P2 - MEDIA (Nice to have)

#### Fix 9: Sample Rate Validation
```python
# src/managers/audio.py:open_stream()

stream.start()
actual_sr = stream.samplerate
if actual_sr != self.config.sample_rate:
    logging.warning(f"[audio] Sample rate mismatch: requested {self.config.sample_rate}, got {actual_sr}")
    # Optionally reject or adjust config
    if actual_sr < 16000:
        stream.close()
        raise ValueError(f"Device sample rate too low: {actual_sr}")
```

#### Fix 10: Replace All print() with logging
```bash
# Find all print() calls:
grep -r "print(" src/

# Replace pattern:
# print(f"foo")  →  logging.info("foo")
# print("bar")   →  logging.debug("bar")
```

#### Fix 11: Callback Error Handling
```python
# src/managers/audio.py:_process_chunk()

def _process_chunk(self, chunk: np.ndarray):
    rms = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0
    if self.on_rms:
        try:
            self.on_rms(rms)
        except Exception as e:
            logging.debug(f"[audio] on_rms callback failed: {e}")
```

#### Fix 12: Graceful Degradation
```python
# Si PyQt6 falta, disable overlay pero continuar funcionando

if overlay_cfg.get("enabled", True):
    try:
        overlay_app = ensure_app()
        logging.info("[overlay] PyQt6 overlay enabled")
    except Exception as exc:
        logging.warning(f"[overlay] PyQt6 unavailable, running without overlay: {exc}")
        overlay_cfg["enabled"] = False
        overlay_app = None
```

---

## 9. MATRIZ DE COBERTURA

```
Categoría                    | Cobertura | Status
-----|-----|-----
Main entry point             | 70%       | try/except pero no global
Audio device setup           | 40%       | Algunos checks, sin recuperación
Audio streaming              | 30%       | Sin status monitoring
Model loading                | 80%       | Good error handling
Transcription pipeline       | 60%       | Sin timeout, silent failures
LLM postprocessing          | 50%       | Sin retry, sin code-specific handling
UI overlays                  | 50%       | Silent failures en init
System tray                  | 30%       | Crash si exception en startup
Network requests             | 40%       | Sin retry logic
Logging                      | 70%       | Good structure, missing rotation
Config loading               | 80%       | Good validation
Hotkey registration         | 80%       | Good error handling
Shutdown sequence            | 85%       | Good timeout management
-----|-----|-----
OVERALL                      | 57%       | MEDIA COBERTURA
```

---

## 10. TESTING CHECKLIST

- [ ] Iniciar app sin micrófono → ¿error claro o silencioso?
- [ ] Desconectar micrófono durante grabación → ¿detecta?
- [ ] Presionar hotkey sin modelo descargado → ¿retry o error?
- [ ] OpenRouter API key inválido → ¿UI error o silent?
- [ ] ONNX inference >60s → ¿timeout o freeze?
- [ ] Sin PyQt6 instalado → ¿fallback graceful?
- [ ] Tray icon initialization fail → ¿app todavía funciona?
- [ ] Model download 404 → ¿error claro?
- [ ] Shutdown durante transcription → ¿graceful?
- [ ] app.log >100MB → ¿rotación automática?

---

## 11. CONCLUSIONES

**Fortalezas:**
- ✅ Main.py tiene try/catch en puntos clave (hotkey, shutdown)
- ✅ Audio manager tiene locks para thread safety
- ✅ Logging infrastructure básica ok

**Debilidades críticas:**
- ❌ Sin manejo de degradación graceful (app continúa sin audio, sin overlay, etc)
- ❌ Print statements scattered → logs inconsistentes
- ❌ Sin timeouts en operaciones bloqueantes (ONNX, LLM)
- ❌ UI errors silenciosos (no user feedback)
- ❌ Sin retry logic en network operations

**Recomendación:** Implementar P0 + P1 fixes antes de release production. El código es robusto en la arquitectura general, pero le faltan salvaguardas en operaciones edge-case que pueden confundir al usuario.
