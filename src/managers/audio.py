"""
Audio recording and VAD management for Whisper Cheap.

Implements:
- AudioRecordingManager: handles stream lifecycle, voice-gated buffering,
  and start/stop/cancel semantics with hotkey bindings.
- Silero VAD helper: lazy download/load of ONNX model and inference wrapper.

Notes:
- Sounddevice is optional at import time; stream opening will fail gracefully
  with a clear error if the library is unavailable.
- For testing, a mock feed path is available via `feed_samples` without an
  actual audio stream.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Deque, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover - handled at runtime
    sd = None

try:
    import onnxruntime as ort
    logger.debug(f"[audio] onnxruntime loaded: {ort.__version__}")
except ImportError as e:  # pragma: no cover - VAD is optional
    logger.error(f"[audio] Failed to import onnxruntime: {e}")
    ort = None
except Exception as e:
    logger.error(f"[audio] Unexpected error importing onnxruntime: {type(e).__name__}: {e}")
    ort = None

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


# Constants
DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_CHANNELS = 1
DEFAULT_CHUNK_SIZE = 512  # 32ms @16k
DEFAULT_VAD_THRESHOLD = 0.5
_MAX_RECORDING_SECONDS = 120  # 2 minutos - protección contra memory leaks
# Pin to tags that still host the ONNX file; upstream removed it from the default branch.
SILERO_VAD_URLS = [
    "https://raw.githubusercontent.com/snakers4/silero-vad/v4.0/files/silero_vad.onnx",
    "https://raw.githubusercontent.com/snakers4/silero-vad/v3.1/files/silero_vad.onnx",
]
SILERO_VAD_FILENAME = "silero_vad_v4.onnx"


class VADNotAvailable(RuntimeError):
    """Raised when VAD is requested but cannot be used."""


@dataclass
class RecordingConfig:
    sample_rate: int = DEFAULT_SAMPLE_RATE
    channels: int = DEFAULT_CHANNELS
    chunk_size: int = DEFAULT_CHUNK_SIZE
    vad_threshold: float = DEFAULT_VAD_THRESHOLD
    always_on_stream: bool = True
    use_vad: bool = True  # if False, record everything
    mute_while_recording: bool = False  # placeholder; to be implemented with pycaw


class SileroVAD:
    """
    Minimal Silero VAD wrapper.

    Falls back to RMS threshold if ONNX runtime or model file is unavailable.
    """

    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir
        self.model_path = self.model_dir / SILERO_VAD_FILENAME
        self._session = None
        self._session_lock = threading.Lock()

    @property
    def available(self) -> bool:
        return bool(ort) and self.model_path.exists()

    def ensure_downloaded(self) -> None:
        if self.model_path.exists():
            return
        if requests is None:
            raise VADNotAvailable("requests is required to download VAD model")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        errors = []
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
                continue
        raise VADNotAvailable(f"Failed to download VAD model from all URLs: {errors}")

    def _load_session(self):
        if not ort:
            raise VADNotAvailable("onnxruntime is not installed")
        if not self.model_path.exists():
            raise VADNotAvailable("VAD model file is missing")
        return ort.InferenceSession(str(self.model_path))

    def _get_session(self):
        with self._session_lock:
            if self._session is None:
                self._session = self._load_session()
            return self._session

    def is_speech(self, chunk: np.ndarray, threshold: float) -> bool:
        """
        Return True if chunk is considered speech.
        Uses Silero VAD if available, otherwise simple RMS threshold.
        """
        if self.available:
            try:
                session = self._get_session()
                # Silero expects shape (batch, 1, samples)
                input_chunk = chunk.astype(np.float32)[np.newaxis, np.newaxis, :]
                outputs = session.run(None, {"input": input_chunk})
                prob = float(outputs[0].squeeze())
                return prob >= threshold
            except Exception:
                # Fall back to RMS on any inference issue
                pass
        rms = float(np.sqrt(np.mean(np.square(chunk.astype(np.float32)))))
        # When Silero isn't available, interpret `threshold` (0..1) as a sensitivity
        # knob rather than a direct RMS threshold (float32 audio RMS is typically << 0.5).
        t = max(0.0, min(float(threshold), 1.0))
        rms_threshold = 0.005 + (0.05 * t)  # ~[0.005..0.055]
        return rms >= rms_threshold


class AudioRecordingManager:
    """
    Manages audio capture and voice-activated recording.
    """

    def __init__(
        self,
        config: Optional[RecordingConfig] = None,
        model_dir: Path | str = Path("src/resources/models"),
        on_rms: Optional[Callable[[float], None]] = None,
        on_event: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.config = config or RecordingConfig()
        self.on_rms = on_rms
        self.on_event = on_event
        self.model_dir = Path(model_dir)
        self.vad = SileroVAD(self.model_dir)
        if sd is None:
            self._emit_event("backend-missing:sounddevice")

        # Límite de chunks para evitar memory leaks (2 min máximo)
        max_chunks = int(
            _MAX_RECORDING_SECONDS * self.config.sample_rate / self.config.chunk_size
        )
        self._buffer: Deque[np.ndarray] = deque(maxlen=max_chunks)
        self._recording_lock = threading.Lock()
        self._is_recording = False
        self._binding_id = None
        self._stream: Optional["sd.InputStream"] = None
        self._stream_lock = threading.Lock()

        # Chunking state (for incremental transcription)
        self._current_chunk: List[np.ndarray] = []
        self._chunk_start_time: float = 0.0
        self._silence_start_time: Optional[float] = None
        self._last_speech_time: float = 0.0
        self._chunk_counter: int = 0
        self._on_chunk_ready: Optional[Callable[[np.ndarray, int], None]] = None

        # Chunking config
        self._chunk_min_duration_sec: float = 3.0  # Never cut before this duration
        self._chunk_silence_threshold_ms: float = 400.0  # Emit chunk after this silence
        self._chunk_max_duration_sec: float = 6.0  # Emit chunk after this IF there's silence

    # --------- Public API ---------
    def list_input_devices(self):
        if sd is None:
            raise RuntimeError("sounddevice is not installed")
        return sd.query_devices()

    def open_stream(self, device_id: Optional[int] = None):
        if sd is None:
            raise RuntimeError("sounddevice is not installed")
        with self._stream_lock:
            if self._stream is not None:
                return

            # Log device info
            try:
                if device_id is not None:
                    device_info = sd.query_devices(device_id)
                    logger.info(f"[audio] Opening stream with device {device_id}: {device_info.get('name', 'unknown')}")
                else:
                    default_device = sd.query_devices(kind='input')
                    logger.info(f"[audio] Opening stream with default device: {default_device.get('name', 'unknown')}")
            except Exception as e:
                logger.warning(f"[audio] Could not query device info: {e}")

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
                logger.info(f"[audio] Stream started: {self.config.sample_rate}Hz, {self.config.channels}ch, chunk={self.config.chunk_size}")
            except Exception as e:
                # Cleanup stream if start() fails to avoid blocking audio device
                logger.error(f"[audio] Stream start failed: {e}")
                try:
                    stream.close()
                except Exception:
                    pass
                self._emit_event(f"stream-start-failed:{e}")
                raise
            self._stream = stream
            self._emit_event("stream-opened")

    def close_stream(self):
        with self._stream_lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
                self._emit_event("stream-closed")

    def start_recording(self, binding_id: str, device_id: Optional[int] = None):
        with self._recording_lock:
            self._buffer.clear()
            self._is_recording = True
            self._binding_id = binding_id

            # Reset chunking state
            self._current_chunk = []
            self._chunk_start_time = time.time()
            self._silence_start_time = None
            self._last_speech_time = time.time()
            self._chunk_counter = 0

        # Always ensure the stream is open at recording time.
        if self._stream is None:
            try:
                self.open_stream(device_id=device_id)
            except Exception as e:
                # Reset recording state before raising
                with self._recording_lock:
                    self._is_recording = False
                    self._binding_id = None
                self._emit_event(f"stream-open-failed:{e}")
                # Raise so caller knows stream failed (no silent empty recordings)
                raise RuntimeError(f"Cannot start recording: failed to open audio stream: {e}") from e

        # Verify stream is actually active
        if self._stream is not None and not self._stream.active:
            with self._recording_lock:
                self._is_recording = False
                self._binding_id = None
            raise RuntimeError("Audio stream not active after open - check microphone connection")

        logger.info(f"[audio] Recording started on device {device_id or 'default'}")
        self._emit_event("recording-started")

    def stop_recording(self, binding_id: str) -> np.ndarray:
        with self._recording_lock:
            if not self._is_recording or binding_id != self._binding_id:
                self._emit_event("recording-stop-ignored")
                logger.warning(f"[audio] Recording stop ignored (recording={self._is_recording}, binding={self._binding_id})")
                return np.array([], dtype=np.float32)
            self._is_recording = False
            self._binding_id = None
            chunk_count = len(self._buffer)
            data = np.concatenate(list(self._buffer)) if self._buffer else np.array([], dtype=np.float32)
            self._buffer.clear()

        # Emit final chunk if there's remaining audio
        if self._current_chunk and self._on_chunk_ready:
            self._emit_current_chunk()

        duration = len(data) / self.config.sample_rate if len(data) > 0 else 0
        logger.info(f"[audio] Recording stopped: {chunk_count} chunks, {len(data)} samples, {duration:.2f}s")

        if not self.config.always_on_stream:
            self.close_stream()
        self._emit_event("recording-stopped")
        return data

    def cancel(self):
        with self._recording_lock:
            self._is_recording = False
            self._binding_id = None
            self._buffer.clear()
        if not self.config.always_on_stream:
            self.close_stream()
        self._emit_event("recording-cancelled")

    def feed_samples(self, samples: np.ndarray):
        """
        Test/helper path: feed samples directly (no audio device needed).
        """
        self._process_chunk(samples.astype(np.float32))

    def ensure_vad_model(self):
        self.vad.ensure_downloaded()

    # --------- Internal helpers ---------
    def _emit_event(self, name: str):
        if self.on_event:
            try:
                self.on_event(name)
            except Exception as e:
                logger.error(f"[audio] Error in event callback '{name}': {e}")

    def _audio_callback(self, indata, frames, time, status):  # pragma: no cover - relies on sounddevice
        if status:
            self._emit_event(f"stream-status:{status}")
        chunk = np.copy(indata[:, 0]) if indata.ndim > 1 else np.copy(indata)
        self._process_chunk(chunk.astype(np.float32))

    def _process_chunk(self, chunk: np.ndarray):
        rms = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0
        if self.on_rms:
            try:
                self.on_rms(rms)
            except Exception:
                pass

        with self._recording_lock:
            if not self._is_recording:
                return

        # Always append to main buffer (fallback for full transcription)
        self._buffer.append(chunk.copy())

        # VAD check
        is_speech = True
        if self.config.use_vad:
            is_speech = self.vad.is_speech(chunk, self.config.vad_threshold)

        # === Chunking logic ===
        now = time.time()

        # Add to current chunk
        self._current_chunk.append(chunk.copy())

        # Track speech/silence
        if is_speech:
            self._last_speech_time = now
            self._silence_start_time = None
        else:
            if self._silence_start_time is None:
                self._silence_start_time = now

        # Calculate durations
        chunk_duration_sec = now - self._chunk_start_time
        silence_duration_ms = 0.0
        if self._silence_start_time is not None:
            silence_duration_ms = (now - self._silence_start_time) * 1000

        # Decide if we should emit the current chunk
        should_emit = False

        # Never cut before minimum duration (prevents cutting short phrases)
        if chunk_duration_sec < self._chunk_min_duration_sec:
            return

        # Only cut if we have speech content in this chunk
        has_speech = self._last_speech_time > self._chunk_start_time
        if not has_speech:
            return

        # Condition 1: Natural pause (prolonged silence after speech)
        if silence_duration_ms >= self._chunk_silence_threshold_ms:
            should_emit = True
            logger.debug(f"[chunking] Emit trigger: pause {silence_duration_ms:.0f}ms")

        # Condition 2: Max duration reached BUT only if there's some silence
        # This prevents cutting in the middle of a word
        if chunk_duration_sec >= self._chunk_max_duration_sec and silence_duration_ms > 50:
            should_emit = True
            logger.debug(f"[chunking] Emit trigger: duration {chunk_duration_sec:.1f}s (silence: {silence_duration_ms:.0f}ms)")

        if should_emit and self._on_chunk_ready:
            self._emit_current_chunk()

    def _emit_current_chunk(self) -> None:
        """Emit the current chunk for background transcription."""
        if not self._current_chunk:
            return

        chunk_audio = np.concatenate(self._current_chunk)
        chunk_index = self._chunk_counter
        duration_sec = len(chunk_audio) / self.config.sample_rate

        # Reset chunking state for next chunk
        self._chunk_counter += 1
        self._current_chunk = []
        self._chunk_start_time = time.time()
        self._silence_start_time = None

        logger.info(f"[chunking] Emitting chunk {chunk_index} ({duration_sec:.1f}s)")

        # Notify callback (must be thread-safe)
        if self._on_chunk_ready:
            try:
                self._on_chunk_ready(chunk_audio, chunk_index)
            except Exception as e:
                logger.error(f"[chunking] Error in on_chunk_ready callback: {e}")
