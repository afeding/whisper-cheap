# CRITICAL ERROR HANDLING FIXES

Este documento contiene código listo para implementar los 4 fixes P0 más críticos.

---

## Fix P0.1: Global Try/Catch en main()

**Archivo:** `src/main.py`
**Línea:** 280
**Severidad:** CRÍTICA - Sin esto, crashes en startup no se loguean

### Problema
```python
def main():
    # Sin envolvente global - si algo falla aquí, no hay log
    is_frozen = getattr(sys, "frozen", False)
    # ... 850+ líneas de código sin protección superior
```

### Solución - OPCIÓN A (Minimal, 1 wrap)
```python
def main():
    try:
        _main_impl()
    except Exception as e:
        logging.critical(f"[main] FATAL ERROR during startup: {e}", exc_info=True)
        sys.exit(1)

def _main_impl():
    # TODO: Move all current main() code here
    is_frozen = getattr(sys, "frozen", False)
    # ... rest of current main() code
```

**Ventaja:** Minimal diff, solo wrap el bloque
**Desventaja:** Requiere renaming de función

### Solución - OPCIÓN B (No refactor)
```python
def main():
    try:
        # Setup logging FIRST (so we can log errors)
        is_frozen = getattr(sys, "frozen", False)
        if is_frozen:
            base_dir = Path(sys.executable).parent
            config_dir = Path(os.path.expandvars("%APPDATA%")) / "whisper-cheap"
        else:
            base_dir = Path(__file__).resolve().parent.parent
            config_dir = base_dir

        # Ensure we can log before calling load_config
        try:
            config_path = config_dir / "config.json"
            cfg = load_config(config_path, is_frozen)
            app_data = ... # expand paths
        except Exception as e:
            # Can't load config, use minimal defaults
            app_data = config_dir / ".data"
            logging.error(f"Failed to load config, using defaults: {e}")
            cfg = get_default_config(is_frozen)

        log_file = setup_logging(app_data)

        # NOW continue with rest of main()
        # ... rest of initialization ...

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.critical(f"[main] FATAL ERROR: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # ... shutdown code ...
```

**Ventaja:** Mejor - setup logging antes de otros inits
**Desventaja:** Un poco más de refactoring

### Recomendación
Use OPCIÓN B. Protege tanto config loading como logging setup.

---

## Fix P0.2: Audio Stream Health Check + Recovery

**Archivo:** `src/managers/audio.py`
**Línea:** 240-252 (start_recording)
**Severidad:** CRÍTICA - Sin esto, grabación sin micrófono pasa silenciosa

### Problema Actual
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
            # ← BUG: continue con self._stream = None!
    self._emit_event("recording-started")
```

### Solución
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
            # Reset state before raising
            with self._recording_lock:
                self._is_recording = False
                self._binding_id = None
            # Emit event for monitoring
            self._emit_event(f"stream-open-failed:{e}")
            # NEW: Raise so caller knows stream failed
            raise RuntimeError(f"Cannot start recording: failed to open audio stream: {e}") from e

    # NEW: Verify stream is actually active
    if not self._stream.active:
        with self._recording_lock:
            self._is_recording = False
            self._binding_id = None
        raise RuntimeError("Audio stream not active after open")

    logger.info(f"[audio] Recording started on device {device_id or 'default'}")
    self._emit_event("recording-started")
```

### Cambios Clave
1. **Reset state** si open_stream falla (no dejar _is_recording=True)
2. **Raise exception** en lugar de continuar silenciosamente
3. **Check stream.active** antes de retornar
4. **Caller** (main.py:actions.start()) debe capturar exception y mostrar UI error

### En main.py (on_press)
```python
def on_press():
    try:
        # ... reload config ...
        if not state_machine.try_start_recording():
            return

        show_recording_overlay()
        tray.set_state("recording")

        try:
            actions.start(
                binding_id="main",
                audio_manager=audio_manager,
                # ... otros args
            )
        except RuntimeError as e:
            if "Cannot start recording" in str(e) or "Audio stream" in str(e):
                show_error_overlay(f"No se pudo acceder al micrófono:\n{str(e)[:60]}")
                logging.error(f"[hotkey] Audio error: {e}")
            else:
                raise
    except Exception as e:
        logging.exception(f"[hotkey] ERROR in on_press: {e}")
```

---

## Fix P0.3: Timeout en Transcription

**Archivo:** `src/managers/transcription.py`
**Línea:** 314-361 (transcribe)
**Severidad:** ALTA - Sin timeout, ONNX inference puede colgar forever

### Problema
```python
def transcribe(self, audio_samples: np.ndarray, model_id: Optional[str] = None) -> Dict[str, Any]:
    # ... no timeout mechanism
    if self._nemo_sess and self._enc_sess and self._dec_sess and self._vocab:
        if duration_sec > CHUNK_THRESHOLD_SEC:
            result = self._transcribe_chunked(audio)  # ← puede colgar
        else:
            text, tokens = self._transcribe_parakeet(audio)  # ← puede colgar
    return result
```

### Solución (Windows-compatible)
```python
import threading

# En TranscriptionManager class:
TRANSCRIBE_TIMEOUT_SEC = 60

def transcribe(self, audio_samples: np.ndarray, model_id: Optional[str] = None) -> Dict[str, Any]:
    # Wrap transcription in thread with timeout
    result = {"text": "", "segments": [], "tokens": None}
    exception_holder = [None]

    def _do_transcribe():
        try:
            # All transcription logic here
            if self._nemo_sess and self._enc_sess and self._dec_sess and self._vocab:
                audio = self._normalize_audio(audio_samples)
                duration_sec = len(audio) / DEFAULT_SAMPLE_RATE

                if duration_sec > CHUNK_THRESHOLD_SEC:
                    result_inner = self._transcribe_chunked(audio)
                else:
                    audio = self._pad_audio(audio)
                    text, tokens = self._transcribe_parakeet(audio)
                    result_inner = {"text": text or "", "segments": [], "tokens": tokens}

                result.update(result_inner)
                self._last_used = time.time()
                gc.collect()
            else:
                # Fallback to old session path
                with self._cond:
                    if self._session is None:
                        raise RuntimeError("Model not loaded")
                    session = self._session

                audio = self._normalize_audio(audio_samples)
                feed = self._prepare_input(session, audio)
                outputs = session.run(None, feed)
                text = None
                if outputs:
                    first = outputs[0]
                    if isinstance(first, (list, tuple)) and first:
                        text = str(first[0])
                    else:
                        text = str(first)

                result["text"] = text or ""
                self._last_used = time.time()
        except Exception as e:
            exception_holder[0] = e

    # Run in thread with timeout
    thread = threading.Thread(target=_do_transcribe, daemon=False)
    thread.start()
    thread.join(timeout=self.TRANSCRIBE_TIMEOUT_SEC)

    if thread.is_alive():
        # Timeout occurred
        logging.error(f"[transcribe] TIMEOUT after {self.TRANSCRIBE_TIMEOUT_SEC}s, thread still running")
        # Note: Can't kill thread in Python, but it will be daemon=False
        # so OS will kill it when main process exits
        raise TimeoutError(f"Transcription timeout (>{self.TRANSCRIBE_TIMEOUT_SEC}s)")

    if exception_holder[0]:
        raise exception_holder[0]

    return result
```

### En actions.py (stop)
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
    except TimeoutError:
        logger.error("[transcribe] TIMEOUT - transcription took too long")
        show_error_overlay("Transcripción tardó demasiado (>60s). Intenta de nuevo.")
        text = None
    except Exception as exc:
        logger.exception(f"[transcribe] Error: {exc}")
        text = None
```

### Notas
- Windows no soporta `signal.alarm()`, usar threading en lugar
- Thread quedará "zombie" si timeout ocurre, pero OS lo limpia
- Timeout de 60s es conservador para audio larga (>120 min)
- Para audio muy larga (>10 min), considerar chunked processing

---

## Fix P0.4: UI Feedback para Transcripción Vacía

**Archivo:** `src/main.py` + `src/actions.py`
**Línea:** 159 (actions.py), 895-911 (main.py)
**Severidad:** CRÍTICA - User no sabe qué pasó

### Problema Actual
```python
# actions.py:159
else:
    logger.warning("Transcripcion vacia o fallida.")  # ← Only in log file, not UI!
```

### Solución - Part 1: Detectar en Actions

Modificar `src/actions.py:stop()` para retornar error status:

```python
# Near end of stop() function, línea ~160:

if text:
    final_text = post_text or text
    logger.info(f"[final] Texto listo ({len(final_text)} chars)")
    try:
        from src.utils.paste import ClipboardPolicy, PasteMethod, paste_text

        progress("pasting")
        pm = PasteMethod(paste_method) if paste_method else PasteMethod.CTRL_V
        policy = ClipboardPolicy(clipboard_policy) if clipboard_policy else ClipboardPolicy.DONT_MODIFY
        paste_text(final_text, method=pm, policy=policy)
    except Exception as exc:
        logger.warning(f"No se pudo pegar automaticamente ({exc}). Copiando al portapapeles.")
        try:
            from src.utils.clipboard import ClipboardManager
            ClipboardManager().set_text(final_text)
        except Exception as clip_err:
            logger.error(f"No se pudo copiar al portapapeles ({clip_err}).")
    result = {
        "audio": samples,
        "text": final_text,
        "file_name": fname,
        "timestamp": timestamp,
        "model_ready": model_ready,
        "status": "success"
    }
else:
    logger.warning("Transcripcion vacia o fallida.")
    # NEW: Return error status so caller can show UI
    result = {
        "audio": samples,
        "text": None,
        "file_name": fname,
        "timestamp": timestamp,
        "model_ready": model_ready,
        "status": "empty_transcript",
        "error": "No se detectó audio o voz clara"
    }
```

### Solución - Part 2: Manejar en Main.py

En `src/main.py`, modify callbacks para job completion:

```python
# Around línea 895, en la definición de on_complete:

def on_complete(result: dict):
    text = result.get("text")
    status = result.get("status", "unknown")

    if status == "success":
        logging.info(f"[complete] Transcribed {len(text)} chars")
    elif status == "empty_transcript":
        logging.warning("[complete] Empty transcription")
        error_msg = result.get("error", "Transcripción vacía")
        show_error_overlay(f"⚠️  {error_msg}\n\nVerifica que el micrófono esté activo.")
    else:
        logging.warning(f"[complete] Unknown status: {status}")
        show_error_overlay(f"Procesamiento completó con estado: {status}")
```

### Solución - Part 3: Validar Audio Antes de Transcrribir

En `src/actions.py`, agregar validación de audio:

```python
# Near línea 81, antes de transcribe:

if samples is None or getattr(samples, "size", 0) == 0:
    logger.warning("No se capturo audio; nada que transcribir.")
    return {
        "audio": samples,
        "text": None,
        "file_name": None,
        "timestamp": None,
        "model_ready": model_ready,
        "status": "no_audio",
        "error": "No se capturó audio"
    }

# NEW: Check audio has reasonable length/volume
audio_len_sec = len(samples) / 16000 if samples.size > 0 else 0
if audio_len_sec < 0.5:
    logger.warning(f"Audio muy corto: {audio_len_sec:.2f}s")
    return {
        "audio": samples,
        "text": None,
        "file_name": None,
        "timestamp": None,
        "model_ready": model_ready,
        "status": "short_audio",
        "error": f"Audio muy corto ({audio_len_sec:.1f}s)"
    }

if transcription_manager and samples is not None and samples.size > 0 and model_ready:
    # ... transcribe ...
```

### Resultado
User ahora ve:
- Error overlay si audio vacío
- Error overlay si audio muy corto
- Error overlay si transcripción falló
- Mensaje claro sobre qué hacer next

---

## Fix P0.5 (Bonus): Logging Rotation

**Archivo:** `src/main.py`
**Línea:** 240-277 (setup_logging)
**Severidad:** MEDIA - Sin esto, app.log crece indefinidamente

### Problema
```python
def setup_logging(app_data: Path) -> Path:
    # ...
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    # Sin rotación → app.log puede crecer a >1GB
```

### Solución
```python
def setup_logging(app_data: Path) -> Path:
    logs_dir = app_data / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "app.log"

    # Root logger at DEBUG level
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Clear any existing handlers
    root.handlers.clear()

    # Console handler: INFO+ with concise format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    ))
    root.addHandler(console_handler)

    # File handler: DEBUG+ with detailed format + ROTATION
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,               # Keep 5 rotated files (50MB total)
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)s] [%(threadName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    root.addHandler(file_handler)

    # NEW: Suppress noise from external libraries
    logging.getLogger("onnxruntime").setLevel(logging.WARNING)
    logging.getLogger("sounddevice").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    # PyQt6 libraries are verbose in debug mode
    logging.getLogger("PyQt6").setLevel(logging.WARNING)

    logging.info("Logging initialized: console=INFO, file=DEBUG, rotation=10MB x5")
    logging.info(f"Log file: {log_file}")
    return log_file
```

### Resultado
- app.log nunca crece >50MB
- Automática rotación: app.log.1, app.log.2, etc
- Menos ruido en logs (external libs silenciados)

---

## Checklist de Implementación

- [ ] Fix P0.1: Global try/catch en main() - **IMPLEMENT FIRST**
- [ ] Fix P0.2: Audio stream health check
- [ ] Fix P0.3: Transcription timeout
- [ ] Fix P0.4: UI feedback para empty transcript
- [ ] Fix P0.5: Logging rotation
- [ ] **TEST:** Without microphone - shows error
- [ ] **TEST:** Disconnect microphone during recording - shows error
- [ ] **TEST:** Transcription takes 70s - shows timeout
- [ ] **TEST:** Empty audio - shows error
- [ ] **TEST:** No PyQt6 - app still works without overlay
- [ ] **TEST:** app.log size stays <50MB over 8 hours

---

## Priority Order for Implementation

1. **P0.1 (Global try/catch)** - Takes 10 min, prevents silent crashes
2. **P0.2 (Audio health)** - Takes 15 min, fixes most common bug
3. **P0.4 (UI feedback)** - Takes 20 min, dramatically improves UX
4. **P0.3 (Timeout)** - Takes 25 min, prevents freeze on long audio
5. **P0.5 (Log rotation)** - Takes 10 min, operational improvement

**Total time:** ~80 minutes to implement all 5 critical fixes.
