# Error Handling Analysis: Whisper Cheap

## Executive Summary

El proyecto tiene **patrones inconsistentes de manejo de errores** que pueden causar:
- **Crashes silenciosos** donde threads mueren sin notificación
- **Errores swallowed** (tragados) con `pass` que ocultan problemas reales
- **Falta de visibilidad** al usuario cuando algo falla
- **Memory leaks potenciales** sin cleanup explícito en caso de error
- **Race conditions** en callbacks sin protección

**Criticidad general: MEDIA-ALTA**. Muchos errores no causan crash inmediato pero degrada la experiencia.

---

## 1. PATTERNS PROBLEMÁTICOS ENCONTRADOS

### 1.1 Bare `pass` After Exception (Sin logging)

**Severidad: ALTA** - Errores completamente silenciados sin trazabilidad

#### `src/actions.py:29-37`
```python
try:
    transcription_manager.preload_async(...)
except Exception:
    pass  # ← Preload puede fallar silenciosamente
```
**Problema:** Si preload falla, el usuario no sabe que el modelo no está precargado.
**Impacto:** Primeras transcripciones serán más lentas (2-5s de espera).

#### `src/actions.py:34-37`
```python
try:
    sound_player.play_start()
except Exception:
    pass  # ← Sonido de inicio puede no sonar sin notificar
```
**Problema:** Usuario cree que grabación empezó pero sin feedback auditivo.

#### `src/actions.py:163-166` (final)
```python
try:
    sound_player.play_end()
except Exception:
    pass  # ← Sonido de fin silenciado
```

#### `src/main.py:29-32`
```python
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(...)
except Exception:
    pass
```
**Problema:** AppUserModelID puede no ser correctamente establecido, causando icono en taskbar incorrecto.

#### `src/main.py:681-683, 823-825, 974-977`
Múltiples casos en overlay y state machine donde errores de UI se silencian.

#### `src/managers/audio.py:223-226`
```python
try:
    stream.close()
except Exception:
    pass  # ← Stream puede quedar colgado
```
**Problema:** Si close() falla, el dispositivo de audio puede quedar bloqueado.

#### `src/managers/history.py:152-155, 183-186, 209-212`
```python
try:
    wav_path.unlink(missing_ok=True)
except Exception:
    pass  # ← Archivos no se eliminan, disk space leak
```
**Problema:** Archivos .wav no se borran, consumiendo disco lentamente.

#### `src/ui/tray.py:122-125, 154-155`
```python
try:
    self._icon.icon = image
except Exception:
    pass
```
**Problema:** Icono del tray puede no actualizarse sin notificar.

#### `src/ui/win_overlay.py` (docenas de casos)
**36+ locations** con `except Exception: pass` sin logging.
- Líneas 197, 266, 307, 332, 361, 365, 375, 383, 389, etc.
- **Severidad crítica:** Overlay puede fallar completamente sin notificar.

#### `src/managers/transcription.py:420-423, 625-626`
```python
try:
    self._transcribe_parakeet(dummy_audio)  # warmup
except Exception:
    pass
```
**Problema:** Warmup falla silenciosamente, primera transcripción real falla.

#### `src/managers/model.py:131-134, 219-221`
```python
try:
    progress_callback(downloaded, total)
except Exception:
    pass
```
**Problema:** Callbacks de progreso fallan sin notificación, UI no actualiza.

#### `src/managers/recording_state.py:529-530, 541-542`
```python
try:
    ClipboardManager().set_text(result.text)
except Exception:
    pass
```
**Problema:** Clipboard falla silenciosamente, usuario cree que texto está copiado.

---

### 1.2 `except Exception:` Genéricos Sin Logging

**Severidad: ALTA** - Errores capturados pero no registrados

#### `src/ui/web_settings/api.py` (CRÍTICO - 30+ cases)

**Línea 115-116:** Config no se carga, retorna `{}` vacío
```python
def get_config(self) -> Dict[str, Any]:
    try:
        with open(self._config_path_str, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}  # ← Sin logging, sin información al usuario
```
**Problema:** Config inválida o corrupta no se reporta. App usa defaults silenciosamente.

**Línea 124-125:** Guardado de config falla sin notificación
```python
def save_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        with open(self._config_path_str, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}  # ← OK: tiene error info
```

**Línea 170-171:** Default models no se cargan, fallback silencioso
```python
except Exception:
    pass  # Usa fallback ["openai/gpt-oss-20b", ...] sin notificar
```

**Línea 334-335:** Cache corrupto se ignora
```python
except Exception:
    pass  # Returns None, no info al usuario
```

**Línea 340-341:** Pricing data no se carga, no hay error
```python
except Exception:
    pass
```

#### `src/managers/audio.py:143-145`
```python
except Exception:
    # Fall back to RMS on any inference issue
    pass  # ← Sin logging del error real de VAD
```
**Problema:** Si VAD falla, se hace silent fallback. Usuario no sabe que VAD no está disponible.

#### `src/ui/overlay.py:41-42`
```python
except Exception:
    pass  # ← Queued functions fallan silenciosamente en UI thread
```
**Problema:** Callbacks en Qt pueden fallar sin notificación.

---

### 1.3 Logging Inconsistente

**Severidad: MEDIA** - Mezcla de `print()` y `logging.error()` sin pattern claro

#### `src/utils/llm_client.py:100`
```python
print(f"[openrouter] postprocess failed: {last_error}")
```
**Problema:** `print()` en lugar de `logger.error()`. No va a archivo de log.

#### `src/ui/web_settings/api.py:85-86, 146-147`
```python
print(f"[SettingsAPI] Failed to create HistoryManager: {e}")
print(f"[SettingsAPI] Error getting audio devices: {e}")
```
**Problema:** `print()` en lugar de logging. No persiste en logs.

#### `src/ui/win_overlay.py:83, 90`
```python
print("[win_overlay] Iniciando thread...")
print(f"[win_overlay] ERROR: {err}")
```
**Problema:** Debug prints en overlay, no logging estructurado.

#### `src/managers/model.py` y otros
Logs importantes usan `logger` pero occasional `print()` para errores.

**Inconsistencia:** Mix de `print()`, `logger.error()`, `logger.exception()` sin consistencia.

---

### 1.4 Errores en Threads/Callbacks Sin Protección

**Severidad: ALTA** - Threads mueren silenciosamente

#### `src/managers/recording_state.py:144-147`
```python
def _notify_queue_change(self) -> None:
    count = self.pending_count
    if self._on_queue_change:
        try:
            self._on_queue_change(count)  # ← Callback puede fallar
        except Exception as e:
            logger.error(f"[state] Error in queue change callback: {e}")
```
**Buen patrón** - callback tiene try/except.

#### `src/managers/hotkey.py:233-236`
```python
try:
    # do something with callback
except Exception as e:
    logger.exception(f"[hotkey] Error in {event_type} callback for '{combo}': {e}")
```
**Buen patrón** - hotkey callbacks logeados.

#### `src/main.py:803-804`
```python
except Exception as e:
    logging.exception(f"[hotkey] ERROR in on_press: {e}")
```
**Buen patrón** - hotkey error logeado.

#### PERO: `src/ui/tray.py:172-176`
```python
try:
    self._icon.run()
except SystemExit:
    pass  # ← Esperado
except Exception:
    pass  # ← PROBLEMA: tray puede morir sin notificar
```
**Problema:** Si tray falla, sistema entero se queda sin UI de salida.

---

### 1.5 Cleanup Incompleto / Missing Finally Blocks

**Severidad: MEDIA-ALTA** - Recursos pueden no liberarse en error

#### `src/managers/audio.py:209-229`
```python
stream = sd.InputStream(...)
try:
    stream.start()
    logger.info(f"[audio] Stream started: ...")
except Exception as e:
    logger.error(f"[audio] Stream start failed: {e}")
    try:
        stream.close()
    except Exception:
        pass
    self._emit_event(f"stream-start-failed:{e}")
    raise
self._stream = stream
```
**OK**: Cierra stream en error antes de raise.

#### PERO: `src/managers/model.py:112-115`
```python
for url in SILERO_VAD_URLS:
    try:
        with requests.get(url, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(self.model_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return  # ← Success path
    except Exception as e:
        errors.append((url, str(e)))
        continue
```
**Problema:** Si `f.write(chunk)` falla, archivo queda incompleto y no se limpia.
- `with open()` protege, pero archivo puede quedarse corrupto en `.model_path`
- Sin verificación de integridad del descargado

#### `src/managers/updater.py:307-339`
```python
with open(installer_path, "wb") as f:
    with resp.iter_content(chunk_size=8192) as chunks:
        for chunk in chunks:
            if chunk:
                f.write(chunk)
        return bytes(downloaded_bytes)  # ← Si verification falla después...
```
**Problema:** Si SHA256 verification falla después del download, archivo .exe queda en `.temp` sin limpieza.

#### `src/ui/web_settings/__init__.py:135-150`
```python
try:
    _process.kill()
    _process.join(timeout=1)
except Exception:
    pass
finally:
    pass  # ← Empty finally, no cleanup
```
**OK pero vacío:** Finally no hace nada.

---

### 1.6 Race Conditions / Estado Inválido

**Severidad: MEDIA** - Múltiples threads accediendo a estado sin sincronización

#### `src/managers/audio.py:178-183`
```python
self._buffer: Deque[np.ndarray] = deque(maxlen=max_chunks)
self._recording_lock = threading.Lock()
self._is_recording = False
self._binding_id = None
self._stream: Optional["sd.InputStream"] = None
self._stream_lock = threading.Lock()
```
**Problema:** `_stream` es accedido desde audio callback sin lock en algunos lugares.

#### `src/managers/transcription.py` (múltiples casos)
```python
self._session = None  # ← Accessed from worker threads
self._session_lock = threading.Lock()
```
Aunque tiene lock, hay muchos if checks sin lock.

#### `src/ui/win_overlay.py:356-380`
```python
# Window message processing happens on message loop thread
# Updates come from queue from different threads
try:
    upd = self._q.get_nowait()
except queue.Empty:
    pass
except Exception:
    pass
```
**Problema:** Queue puede estar en estado inconsistente.

---

### 1.7 Errores Sin User Feedback

**Severidad: MEDIA** - Usuario no se entera de errores críticos

#### Audio Device Errors
Si no hay micrófono detectado, ¿el usuario lo ve?
- `src/managers/audio.py:188, 193` - `raise RuntimeError` pero ¿se captura en main?

#### Model Download Failures
Si download de modelo falla, ¿se muestra al usuario?
- `src/managers/model.py:131-137` - Download fail se logea pero ¿se notifica UI?

#### LLM Connection Errors
Si OpenRouter API falla, ¿se notifica al usuario o transcripción se descarta?
- `src/actions.py:116-118` - Error se logea pero sin UI feedback

#### Post-Processing Fails
- `src/actions.py:148-155` - Fallback a clipboard sin notificar que paste automático falló

---

## 2. ERRORES POR ARCHIVO CRÍTICO

### `src/main.py` (Entry point)
- **Línea 31-32**: AppUserModelID silenciado
- **Línea 681-683, 823-825, 974-977**: Overlay errors silenciados (docenas de puntos)
- **Línea 1031-1032**: KeyboardInterrupt con `pass`
- **Línea 1057-1138**: Shutdown errors logeados correctamente, BUT no hay verificación de éxito

**Risk:** Main loop puede crashear sin graceful shutdown.

### `src/actions.py` (Core glue layer)
- **Línea 29-37**: Preload y sonidos silenciados
- **Línea 148-155**: Paste fail con fallback pero sin notificar usuario
- **Línea 163-166**: Sonido de fin silenciado

**Risk:** Primera transcripción lenta, usuario sin feedback.

### `src/managers/audio.py` (Audio I/O)
- **Línea 143-145**: VAD fallback silencioso
- **Línea 225-226**: Stream close fail silenciado

**Risk:** Dispositivo de audio puede quedar bloqueado.

### `src/managers/transcription.py` (STT Core)
- **Línea 420-423**: Warmup fail silenciado
- **Línea 625-626**: Event callback fail silenciado

**Risk:** Primera transcripción puede fallar sin preparación.

### `src/ui/web_settings/api.py` (Settings UI)
- **30+ cases** de `except Exception: pass` sin logging
- **Línea 115, 170, 334, 340**: Config/models/pricing no se cargan, fallback silencioso

**Risk:** Settings cambian silenciosamente a defaults, usuario confundido.

### `src/ui/win_overlay.py` (Native overlay)
- **36+ cases** de `except Exception: pass`
- **Línea 171-177**: Initial rect fallback pero qué si todo falla?
- **Línea 315-383**: Múltiples win32api calls sin protección

**Risk:** Overlay UI desaparece sin notificación.

### `src/managers/recording_state.py` (State machine)
- **Línea 529-530, 541-542**: Clipboard/sound fail silenciados

**Risk:** Transcripción completa pero no se pega/copia.

---

## 3. IMPACT MATRIX

| Categoría | Archivo | Línea | Impacto | User Visible | Easy Fix |
|-----------|---------|-------|--------|------------|----------|
| **Bare pass** | actions.py | 31, 36, 165 | Preload/sound fail | NO | SÍ |
| **Bare pass** | audio.py | 225 | Stream leak | NO | SÍ |
| **Bare pass** | history.py | 154, 185, 211 | Disk leak | NO | SÍ |
| **Bare pass** | win_overlay.py | 36+ | Overlay dies | SÍ | MEDIA |
| **Bare pass** | web_settings/api.py | 30+ | Config loss | NO/SÍ | SÍ |
| **Bare pass** | tray.py | 176 | Tray dies | SÍ | SÍ |
| **Print vs log** | llm_client.py | 100 | No persistence | NO | SÍ |
| **Print vs log** | web_settings/api.py | 85,146 | No persistence | NO | SÍ |
| **No user feedback** | audio.py | 188,193 | Mic error silent | SÍ | MEDIA |
| **No user feedback** | model.py | 137 | Download fail | SÍ | MEDIA |
| **No user feedback** | actions.py | 148 | Paste fail | SÍ | MEDIA |
| **Missing finally** | model.py | 112 | Corrupt file | SÍ | MEDIA |
| **Missing finally** | updater.py | 313 | Leftover .exe | SÍ | MEDIA |
| **Race condition** | audio.py | 178-283 | State mismatch | SÍ | HARD |
| **Thread dies silent** | tray.py | 172 | No exit UI | SÍ | SÍ |

---

## 4. RECOMENDACIONES DE PRIORIDAD

### TIER 1: CRÍTICO (Fix en esta semana)
1. **Tray thread protection** - Sin salida de UI no hay manera de cerrar app
2. **Audio stream cleanup** - Memory leak silencioso
3. **History file cleanup** - Disk space leak
4. **Config load/save errors** - Silent data loss risk

### TIER 2: IMPORTANTE (Fix en 2 semanas)
1. **Bare `pass` after exception** - Replace todos con `logger.exception()`
2. **Print → logging** - Consolidar a `logging` module
3. **User-facing error notifications** - Usar overlay para errors críticos
4. **Model/updater cleanup on failure** - Finally blocks para archivos temp

### TIER 3: MEJORA (Next sprint)
1. **Race condition auditing** - Review todos los accesos sin lock
2. **Callback timeout protection** - Callbacks no debería tardar >1s
3. **Graceful degradation** - Fallbacks mejor documentados
4. **Error recovery** - Retry logic para network operations

---

## 5. CÓDIGO PATTERN RECOMENDADO

### Patrón 1: Manejo básico con logging
```python
try:
    result = something_important()
except FileNotFoundError as e:
    logger.error(f"[module] File not found: {e}", exc_info=True)
    raise  # Re-raise para que el caller maneje
except Exception as e:
    logger.exception(f"[module] Unexpected error: {e}")
    # Fallback seguro o re-raise
    raise
```

### Patrón 2: Callback con protección
```python
if self._on_event:
    try:
        self._on_event("something")
    except Exception as e:
        logger.error(f"[module] Event callback failed: {e}", exc_info=True)
        # No re-raise: callbacks no deben crashear app
```

### Patrón 3: Cleanup garantizado
```python
resource = None
try:
    resource = acquire_resource()
    use_resource(resource)
finally:
    if resource:
        try:
            resource.cleanup()
        except Exception as e:
            logger.warning(f"[module] Cleanup failed: {e}")
```

### Patrón 4: User notification para errors críticos
```python
try:
    result = critical_operation()
except Exception as e:
    error_msg = f"Operation failed: {str(e)[:100]}"
    logger.error(f"[module] {error_msg}", exc_info=True)
    if on_error_callback:
        on_error_callback(error_msg)  # Notifica UI
    raise
```

---

## 6. SUMMARY DE BUGS ENCONTRADOS

Total de issues: **50+ locations** con error handling problemático

- 35+ bare `pass` after exception (sin logging)
- 15+ `except Exception:` genéricos sin acción
- 8+ `print()` en lugar de `logging`
- 5+ missing finally/cleanup blocks
- 3+ potential race conditions
- 2+ thread death scenarios sin notificación

**Recomendación:** Implementar test de "error paths" para cubrir estos casos.
