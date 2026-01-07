# Error Handling: Fixes Concretas y Ejemplos

## FIXES POR PRIORIDAD

### TIER 1: CRÍTICO - FIX INMEDIATO

#### 1. Tray Manager Thread Death (src/ui/tray.py:172-176)

**Actual (PELIGROSO):**
```python
def run(self):
    try:
        self._icon.run()  # Blocking loop
    except SystemExit:
        pass  # Expected
    except Exception:  # ← PROBLEMA: Tray muere sin notificar
        pass
```

**Problema:** Si pystray falla, no hay UI de salida. Usuario atrapado.

**Fix mínimo:**
```python
def run(self):
    try:
        self._icon.run()  # Blocking loop
    except SystemExit:
        pass  # Expected
    except Exception as e:
        import logging
        logging.exception(f"[tray] Fatal error in tray loop: {e}")
        # Don't re-raise; keep app running but log it
        raise SystemExit(1)  # Force exit so main thread notices
```

---

#### 2. Audio Stream Resource Leak (src/managers/audio.py:232-238)

**Actual:**
```python
def close_stream(self):
    with self._stream_lock:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()  # ← May fail
            self._stream = None
            self._emit_event("stream-closed")
```

**Fix:**
```python
def close_stream(self):
    with self._stream_lock:
        if self._stream is not None:
            try:
                self._stream.stop()
            except Exception as e:
                logger.warning(f"[audio] Failed to stop stream: {e}")
            try:
                self._stream.close()
            except Exception as e:
                logger.warning(f"[audio] Failed to close stream: {e}")
            finally:
                self._stream = None  # Always clear reference
                self._emit_event("stream-closed")
```

---

#### 3. History File Cleanup (src/managers/history.py:152-155, 183-186, 209-212)

**Actual:**
```python
try:
    wav_path.unlink(missing_ok=True)  # Delete file
except Exception:
    pass  # ← Silenced: disk space leaks
```

**Problem:** Old recording files pile up.

**Fix:**
```python
try:
    wav_path.unlink(missing_ok=True)
except FileNotFoundError:
    pass  # File already gone, OK
except PermissionError as e:
    logger.warning(f"[history] Cannot delete {wav_path}: permission denied")
except Exception as e:
    logger.error(f"[history] Failed to delete {wav_path}: {e}")
    # Note: file is orphaned but DB is updated
```

---

#### 4. Config Load Failures (src/ui/web_settings/api.py:112-116)

**Actual:**
```python
def get_config(self) -> Dict[str, Any]:
    try:
        with open(self._config_path_str, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:  # ← SILENT: Returns {} even if file corrupted
        return {}
```

**Problem:** Config corrupted = app resets to defaults without notifying user.

**Fix:**
```python
def get_config(self) -> Dict[str, Any]:
    try:
        with open(self._config_path_str, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"[api] Config not found, using defaults: {self._config_path_str}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"[api] Config file corrupted at {self._config_path_str}: {e}")
        # Create backup of corrupted file
        try:
            backup_path = f"{self._config_path_str}.corrupted"
            import shutil
            shutil.copy(self._config_path_str, backup_path)
            logger.info(f"[api] Corrupted config backed up to: {backup_path}")
        except Exception:
            pass
        return {}
    except Exception as e:
        logger.error(f"[api] Unexpected error loading config: {e}")
        return {}
```

---

### TIER 2: IMPORTANTE - FIX EN 2 SEMANAS

#### 5. Replace all bare `pass` with logging (Multiple files)

**Pattern to find and fix:**
```python
try:
    # something
except Exception:
    pass  # ← Change to:
```

**Fix template:**
```python
try:
    # something
except SpecificError as e:
    logger.warning(f"[context] {e}")
except Exception as e:
    logger.exception(f"[context] Unexpected error: {e}")
```

**Examples to fix:**

**src/actions.py:29-37** (Preload + Sounds)
```python
# BEFORE
try:
    transcription_manager.preload_async(...)
except Exception:
    pass

# AFTER
try:
    transcription_manager.preload_async(...)
except Exception as e:
    logger.debug(f"[actions] Model preload failed (non-critical): {e}")
    # Preload is optional; transcription will load on-demand
```

**src/audio.py:143-145** (VAD fallback)
```python
# BEFORE
try:
    session = self._get_session()
    # ... inference ...
except Exception:
    pass  # Fall back to RMS

# AFTER
try:
    session = self._get_session()
    # ... inference ...
except Exception as e:
    logger.debug(f"[vad] Inference failed, falling back to RMS: {e}")
    # Fallback is intentional
```

**src/managers/sound.py:104, 131, 138** (Sound playback)
```python
# BEFORE
try:
    play_sound(file)
except Exception:
    pass

# AFTER
try:
    play_sound(file)
except FileNotFoundError:
    logger.debug(f"[sound] Sound file not found: {file}")
except Exception as e:
    logger.warning(f"[sound] Failed to play sound: {e}")
```

---

#### 6. Consolidate logging (print → logger)

**Locations to fix:**
- `src/utils/llm_client.py:100` - `print()` → `logger.error()`
- `src/ui/web_settings/api.py:85, 146` - `print()` → `logger.error()`
- `src/ui/win_overlay.py:83, 90` - `print()` → `logger.debug()` (not error)

**Pattern:**
```python
# BEFORE
print(f"[module] Error: {e}")

# AFTER
logger.error(f"[module] Error: {e}")
```

---

#### 7. User-Facing Error Notifications

**Problem:** When critical operations fail, user doesn't know.

**Examples:**
- Model download fails → Show error overlay
- Audio device not available → Show error dialog
- LLM post-processing times out → Notify user
- Paste fails → Clipboard fallback with message

**Implementation in main.py:**

```python
# Add error display function
def show_error_to_user(message: str):
    """Show error to user via overlay or dialog."""
    logging.error(f"[error] {message}")

    # Try overlay first
    if win_bar:
        try:
            win_bar.show_error(message)
            return
        except Exception:
            pass

    # Fallback: tray notification or console
    if tray:
        try:
            tray.set_state("error")
            # Could also add tooltip
        except Exception:
            pass

    print(f"ERROR: {message}", file=sys.stderr)
```

**Usage in critical paths:**
```python
# In actions.py stop() function
if not model_manager.is_downloaded(target):
    error_msg = f"Model {target} not available. Check settings."
    logger.error(error_msg)
    # Notify user
    if on_error:
        on_error(error_msg)
```

---

#### 8. Model Download Cleanup on Failure (src/managers/model.py:112-137)

**Actual:**
```python
for url in SILERO_VAD_URLS:
    try:
        with requests.get(url, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(self.model_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return
    except Exception as e:
        errors.append((url, str(e)))
        continue  # ← Try next URL but keep corrupted file
```

**Problem:** If write fails mid-stream, partial file stays.

**Fix:**
```python
import tempfile
for url in SILERO_VAD_URLS:
    temp_path = None
    try:
        # Download to temp first
        temp_path = self.model_path.with_suffix('.tmp')
        with requests.get(url, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(temp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        # Move to final location only if complete
        temp_path.replace(self.model_path)
        return
    except Exception as e:
        errors.append((url, str(e)))
        # Clean up temp file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        continue
```

---

#### 9. Updater Installer Cleanup (src/managers/updater.py:307-339)

**Problem:** If SHA256 verification fails, installer .exe is left in temp.

**Fix:**
```python
def install(self, sha256_expected: Optional[str] = None) -> None:
    installer_path = Path(self._temp_installer_path)
    try:
        if not installer_path.exists():
            raise FileNotFoundError(f"Installer not found: {installer_path}")

        # Verify SHA256 before executing
        if sha256_expected:
            actual_sha256 = self._compute_sha256(installer_path)
            if actual_sha256.lower() != sha256_expected.lower():
                raise ValueError(
                    f"SHA256 mismatch. Expected {sha256_expected}, "
                    f"got {actual_sha256}"
                )

        # Execute installer
        subprocess.run([str(installer_path), "/S"], check=True)
    finally:
        # Always clean up installer, even if verification fails
        try:
            installer_path.unlink()
        except Exception as e:
            logger.warning(f"[updater] Could not delete installer: {e}")
```

---

### TIER 3: MEJORA - NEXT SPRINT

#### 10. Race Condition Audit (src/managers/audio.py)

**Current:** Multiple threads access `_stream` without lock in callback.

**Audit points:**
- `_audio_callback` runs on sounddevice thread
- Main thread calls `close_stream()`
- No lock between callback and close

**Fix outline:**
```python
def _audio_callback(self, indata, frames, time, status):
    """Called from audio thread."""
    if status:
        logger.debug(f"[audio] Stream status: {status}")

    # Protect buffer access
    with self._recording_lock:
        if self._is_recording:
            try:
                self._buffer.append(indata.copy())
            except Exception as e:
                logger.error(f"[audio] Buffer error: {e}")

def close_stream(self):
    """Called from main thread."""
    with self._stream_lock:
        if self._stream is not None:
            # Stream lock protects from callback during close
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.warning(f"[audio] Close failed: {e}")
            finally:
                self._stream = None
```

---

#### 11. Callback Timeout Protection

**Problem:** If callback takes >100ms, audio buffer gets starved.

**Implementation:**
```python
import time
from functools import wraps

def _with_timeout(timeout_ms=100):
    """Decorator to timeout callback execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Run in thread with timeout
            result = [None]
            exception = [None]

            def run():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            thread.join(timeout=timeout_ms/1000)

            if thread.is_alive():
                logger.warning(f"[callback] Timeout in {func.__name__}")
                return

            if exception[0]:
                raise exception[0]
            return result[0]
        return wrapper
    return decorator

# Usage:
@_with_timeout(100)
def on_event(name):
    if self._callback:
        self._callback(name)
```

---

#### 12. Error Recovery / Retry Logic

**For network operations:**
```python
def retry_with_backoff(func, max_retries=3, backoff_base=2):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.Timeout:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_base ** attempt
            logger.warning(f"[retry] Timeout, retrying in {wait_time}s...")
            time.sleep(wait_time)
        except requests.ConnectionError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_base ** attempt
            logger.warning(f"[retry] Connection error: {e}, retrying in {wait_time}s...")
            time.sleep(wait_time)

# Usage in updater.py
def _fetch_releases(self):
    return retry_with_backoff(
        lambda: requests.get(self.RELEASES_URL, timeout=10).json(),
        max_retries=3
    )
```

---

## TEST CASES PARA ERROR PATHS

### Unit tests to add:

```python
def test_tray_thread_exception():
    """Tray should log and exit gracefully if thread fails."""
    tray = TrayManager()
    # Mock pystray to raise exception
    with patch('pystray.Icon.run', side_effect=RuntimeError("Mock error")):
        with pytest.raises(SystemExit):
            tray.run()
    # Verify logged
    assert "Fatal error in tray loop" in caplog.text

def test_config_corruption_recovery():
    """API should backup corrupted config and return defaults."""
    api = SettingsAPI(corrupted_json_file)
    config = api.get_config()
    assert config == {}  # Defaults
    assert corrupted_json_file.with_suffix('.corrupted').exists()

def test_stream_close_on_error():
    """Audio manager should close stream even if stop() fails."""
    manager = AudioRecordingManager()
    manager._stream = MagicMock()
    manager._stream.stop.side_effect = RuntimeError("Mock error")

    manager.close_stream()

    # Should still be None
    assert manager._stream is None
    # stop() and close() both called despite error
    manager._stream.stop.assert_called_once()
    manager._stream.close.assert_called_once()

def test_model_download_cleanup_on_failure():
    """Partial downloads should be cleaned up."""
    manager = ModelManager()
    with patch('requests.get', side_effect=ConnectionError("Mock error")):
        with pytest.raises(Exception):
            manager.download_model(url, path)

    # Temp file should not exist
    assert not path.with_suffix('.tmp').exists()

def test_preload_failure_doesnt_crash():
    """Preload exception should be logged, not raised."""
    transcription = TranscriptionManager(model_dir)
    with patch.object(transcription, 'preload_async', side_effect=RuntimeError("Mock")):
        # Should not raise
        actions.start(
            "test",
            transcription_manager=transcription
        )
```

---

## CHECKLIST DE IMPLEMENTACIÓN

- [ ] Fix Tier 1 (crítico)
  - [ ] Tray thread protection
  - [ ] Audio stream cleanup
  - [ ] History file cleanup
  - [ ] Config load errors

- [ ] Fix Tier 2 (importante)
  - [ ] Replace all bare `pass` with logging
  - [ ] Consolidate logging (print → logger)
  - [ ] Add user error notifications
  - [ ] Model/updater cleanup on failure

- [ ] Testing
  - [ ] Add error path tests
  - [ ] Test callback failures
  - [ ] Test resource cleanup
  - [ ] Test thread death scenarios

- [ ] Documentation
  - [ ] Document error handling patterns
  - [ ] Add comments on intentional fallbacks
  - [ ] Create troubleshooting guide
