"""
Simple sound cue playback helper for start/end events.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover - optional at runtime
    sd = None

try:
    import librosa  # type: ignore
except Exception:  # pragma: no cover - optional
    librosa = None

try:
    import winsound  # type: ignore
except Exception:  # pragma: no cover - optional
    winsound = None


class SoundPlayer:
    """
    Lightweight sound player that tries to load clips for quick playback with gain,
    and falls back to playsound/winsound if decoding fails.
    """

    def __init__(
        self,
        start_path: Path,
        end_path: Path,
        volume_boost: float = 1.0,
        enabled: bool = True,
    ) -> None:
        self.start_path = Path(start_path)
        self.end_path = Path(end_path)
        self.volume_boost = max(0.1, float(volume_boost or 1.0))
        self.enabled = enabled
        self._cache: Dict[Path, Tuple[np.ndarray, int]] = {}
        self._lock = threading.Lock()

    def preload(self) -> None:
        """
        Preload sound files into cache to avoid delay on first playback.
        Call this at app startup.
        """
        if not librosa:
            return
        for path in (self.start_path, self.end_path):
            if path and path.exists():
                self._get_cached_audio(path)

    def configure(
        self,
        *,
        start_path: Optional[Path] = None,
        end_path: Optional[Path] = None,
        volume_boost: Optional[float] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        """Update settings and clear cache if the waveform needs to be reloaded."""
        should_clear = False
        if start_path and Path(start_path) != self.start_path:
            self.start_path = Path(start_path)
            should_clear = True
        if end_path and Path(end_path) != self.end_path:
            self.end_path = Path(end_path)
            should_clear = True
        if volume_boost is not None:
            new_gain = max(0.1, float(volume_boost or 1.0))
            if new_gain != self.volume_boost:
                self.volume_boost = new_gain
                should_clear = True
        if enabled is not None:
            self.enabled = bool(enabled)
        if should_clear:
            with self._lock:
                self._cache.clear()

    def play_start(self) -> None:
        if self.enabled:
            self._play(self.start_path)

    def play_end(self) -> None:
        if self.enabled:
            self._play(self.end_path)

    # --------- Internal helpers ---------
    def _load_audio(self, path: Path) -> Optional[Tuple[np.ndarray, int]]:
        if not librosa:
            return None
        try:
            data, sr = librosa.load(path, sr=None, mono=True)
            if self.volume_boost != 1.0:
                data = np.clip(data * self.volume_boost, -1.0, 1.0)
            return data, sr
        except Exception:
            return None

    def _play(self, path: Path) -> None:
        if not path or not path.exists():
            return
        data_sr = self._get_cached_audio(path)
        if data_sr and sd is not None:
            data, sr = data_sr
            threading.Thread(target=self._play_array, args=(data, sr), daemon=True).start()
            return
        self._beep_fallback()

    def _get_cached_audio(self, path: Path) -> Optional[Tuple[np.ndarray, int]]:
        with self._lock:
            if path in self._cache:
                return self._cache[path]
        loaded = self._load_audio(path)
        if loaded is None:
            return None
        with self._lock:
            self._cache[path] = loaded
        return loaded

    def _play_array(self, data: np.ndarray, sample_rate: int) -> None:
        try:
            sd.play(data, samplerate=sample_rate, blocking=False)
        except Exception:
            self._beep_fallback()

    def _beep_fallback(self) -> None:
        if winsound:
            try:
                winsound.Beep(880, 160)
            except Exception:
                pass
