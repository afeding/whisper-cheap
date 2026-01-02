"""
Transcription management for Whisper Cheap (Parakeet V3).

Responsibilities:
- Load ONNX model (with events and loading guard)
- (Optional) async preload
- Transcription pipeline stub (pads/normalizes audio, calls session)
- Custom word replacement
- Unload after inactivity (opt-in via `unload_timeout_seconds`)
"""

from __future__ import annotations

import logging
import re
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, List

import numpy as np

logger = logging.getLogger(__name__)

try:
    import onnxruntime as ort
    logger.debug(f"[transcription] onnxruntime loaded: {ort.__version__}")
except ImportError as e:  # pragma: no cover - handled at runtime
    logger.error(f"[transcription] Failed to import onnxruntime: {e}")
    ort = None
except Exception as e:
    logger.error(f"[transcription] Unexpected error importing onnxruntime: {type(e).__name__}: {e}")
    ort = None

try:
    import librosa  # type: ignore
except ImportError:  # pragma: no cover - optional for mel extraction
    librosa = None

from src.managers.model import ModelManager


DEFAULT_SAMPLE_RATE = 16_000
BLANK_TOKEN = "<blk>"
START_TOKEN = "<|startoftranscript|>"
SUBSAMPLING = 8  # from model config
WINDOW_SIZE = 0.01  # seconds per step before subsampling
DURATION_HEAD = 5  # last logits reserved for duration; ignore
MAX_TOKENS_PER_STEP = 10
SPACE_RE = re.compile(r"\A\s|\s\B|(\s)\b")


class TranscriptionManager:
    def __init__(
        self,
        model_manager: ModelManager,
        provider: str = "CPUExecutionProvider",
        on_event: Optional[Callable[[str], None]] = None,
        session_factory: Optional[Callable[..., Any]] = None,
        unload_timeout_seconds: Optional[int] = None,
    ) -> None:
        self.model_manager = model_manager
        self.provider = provider
        self.on_event = on_event
        self.session_factory = session_factory or (lambda path: ort.InferenceSession(path, providers=[provider])) if ort else None

        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._session: Optional[Any] = None  # legacy single-session path
        self._model_id: Optional[str] = None
        self._is_loading = False
        self.unload_timeout_seconds = unload_timeout_seconds
        self._last_used: Optional[float] = None
        # Parakeet components
        self._nemo_sess: Optional[Any] = None
        self._enc_sess: Optional[Any] = None
        self._dec_sess: Optional[Any] = None
        self._vocab: Optional[List[str]] = None
        self._blank_id: Optional[int] = None
        self._start_id: Optional[int] = None
        self._vocab_size: int = 0

    # -------- Model loading --------
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
            if self.session_factory is None:
                raise RuntimeError("onnxruntime is not available")

            def candidate_onnx_files():
                preferred = ["nemo128.onnx", "encoder-model.int8.onnx", "encoder.onnx", "model.onnx"]
                ordered = []
                for name in preferred:
                    p = model_dir / name
                    if p.exists() and not p.name.startswith("._"):
                        ordered.append(p)
                for p in model_dir.glob("*.onnx"):
                    if p.name.startswith("._"):
                        continue
                    if p in ordered:
                        continue
                    # Skip decoder-only models; we don't wire them here.
                    if "decoder" in p.name:
                        continue
                    ordered.append(p)
                return ordered

            candidates = []
            model_path = model_dir / "model.onnx"
            if model_path.exists() and not model_path.name.startswith("._"):
                candidates.append(model_path)
            for p in candidate_onnx_files():
                if p not in candidates:
                    candidates.append(p)

            if not candidates:
                raise FileNotFoundError(f"Model file not found in {model_dir}")

            # Try to load full Parakeet pipeline if available
            nemo_path = model_dir / "nemo128.onnx"
            enc_path = model_dir / "encoder-model.int8.onnx"
            dec_path = model_dir / "decoder_joint-model.int8.onnx"
            vocab_path = model_dir / "vocab.txt"

            last_error = None
            if nemo_path.exists() and enc_path.exists() and dec_path.exists():
                try:
                    nemo_sess = self.session_factory(str(nemo_path))
                    enc_sess = self.session_factory(str(enc_path))
                    dec_sess = self.session_factory(str(dec_path))
                    vocab = self._load_vocab(vocab_path)
                    self._nemo_sess = nemo_sess
                    self._enc_sess = enc_sess
                    self._dec_sess = dec_sess
                    self._vocab = vocab
                    self._blank_id = self._find_token_id(BLANK_TOKEN, vocab)
                    self._start_id = self._find_token_id(START_TOKEN, vocab)
                    self._vocab_size = len(vocab)
                except Exception as e:
                    last_error = e
                    self._nemo_sess = self._enc_sess = self._dec_sess = None
                    self._vocab = None
                    self._blank_id = self._start_id = None

            session = None
            if self._nemo_sess and self._enc_sess and self._dec_sess:
                session = "parakeet-pipeline"
            else:
                # Fallback: load any single ONNX
                for path in candidates:
                    try:
                        session = self.session_factory(str(path))
                        break
                    except Exception as e:
                        last_error = e
                        continue

            if session is None:
                raise RuntimeError(f"Failed to load Parakeet pipeline: {last_error}")

            with self._cond:
                self._session = session  # may be string sentinel
                self._model_id = model_id
                self._is_loading = False
                self._cond.notify_all()
            self._emit("loading-completed")
        except Exception:
            with self._cond:
                self._is_loading = False
                self._cond.notify_all()
            self._emit("loading-failed")
            raise

    def preload_async(self, model_id: str):
        thread = threading.Thread(target=self.load_model, args=(model_id,), daemon=True)
        thread.start()
        return thread

    def unload_model(self):
        with self._cond:
            self._session = None
            self._model_id = None
        self._emit("unloaded")

    # -------- Transcription --------
    def transcribe(self, audio_samples: np.ndarray, model_id: Optional[str] = None) -> Dict[str, Any]:
        if audio_samples is None:
            raise ValueError("audio_samples is required")
        audio = np.asarray(audio_samples, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio[:, 0]
        audio = self._pad_audio(audio)
        audio = self._normalize_audio(audio)

        # Parakeet pipeline path
        if self._nemo_sess and self._enc_sess and self._dec_sess and self._vocab:
            text, tokens = self._transcribe_parakeet(audio)
            self._last_used = time.time()
            return {"text": text or "", "segments": [], "tokens": tokens}

        with self._cond:
            if self._session is None or (model_id and self._model_id != model_id):
                target_id = model_id or self._model_id
                if target_id is None:
                    raise RuntimeError("Model is not loaded")
            session = self._session
        if session is None:
            raise RuntimeError("Model session not available")

        feed = self._prepare_input(session, audio)
        outputs = session.run(None, feed)
        text = None
        if outputs:
            first = outputs[0]
            if isinstance(first, (list, tuple)) and first:
                text = str(first[0])
            else:
                text = str(first)

        self._last_used = time.time()
        return {"text": text or "", "segments": [], "tokens": None}

    # -------- Custom words --------
    def apply_custom_words(self, text: str, custom_words: Dict[str, str]) -> str:
        output = text
        for src, dst in custom_words.items():
            output = output.replace(src, dst)
        return output

    # -------- Helpers --------
    def warmup(self) -> None:
        """Run a dummy transcription to warm up ONNX kernels (JIT compilation)."""
        if not (self._nemo_sess and self._enc_sess and self._dec_sess):
            return
        dummy_audio = np.zeros(int(0.5 * DEFAULT_SAMPLE_RATE), dtype=np.float32)
        try:
            self._transcribe_parakeet(dummy_audio)
        except Exception:
            pass

    def should_unload(self) -> bool:
        if self.unload_timeout_seconds is None or self.unload_timeout_seconds <= 0:
            return False
        if self._last_used is None:
            return False
        return (time.time() - self._last_used) >= self.unload_timeout_seconds

    def _pad_audio(self, audio: np.ndarray) -> np.ndarray:
        min_len = int(1.25 * DEFAULT_SAMPLE_RATE)
        if audio.size >= min_len:
            return audio
        pad_width = min_len - audio.size
        return np.pad(audio, (0, pad_width), mode="constant")

    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        max_abs = float(np.max(np.abs(audio))) if audio.size else 0.0
        if max_abs > 1.0e-6 and max_abs > 1.0:
            audio = audio / max_abs
        return audio.astype(np.float32)

    def _prepare_input(self, session, audio: np.ndarray):
        """
        Inspect session inputs to decide waveform vs log-mel.
        If input rank <= 2 -> waveform.
        If input rank >= 3 or second dim ~ n_mels -> generate log-mel.
        """
        inputs = getattr(session, "get_inputs", lambda: [])() or []
        names = {getattr(inp, "name", f"in{i}"): inp for i, inp in enumerate(inputs)}
        # Nemo-style frontend: raw waveforms + lengths
        if "waveforms" in names:
            feed = {"waveforms": audio[np.newaxis, :].astype(np.float32)}
            for len_name in ("waveforms_lens", "length", "input_lengths"):
                if len_name in names:
                    feed[len_name] = np.array([audio.shape[-1]], dtype=np.int64)
                    break
            return feed
        # Common Parakeet signature: audio_signal (float32 [B, T]) + length ([B])
        if "audio_signal" in names:
            meta = names["audio_signal"]
            shape = getattr(meta, "shape", None)
            # If model expects 3D ([B,1,T]), add channel dimension
            if shape and len(shape) >= 3:
                feed = {"audio_signal": audio[np.newaxis, np.newaxis, :].astype(np.float32)}
            else:
                feed = {"audio_signal": audio[np.newaxis, :].astype(np.float32)}
            for len_name in ("length", "audio_signal_length", "input_lengths"):
                if len_name in names:
                    feed[len_name] = np.array([audio.shape[-1]], dtype=np.int64)
                    break
            return feed

        input_meta = inputs[0] if inputs else None
        shape = getattr(input_meta, "shape", None)
        name = getattr(input_meta, "name", "input")

        needs_mel = False
        if shape:
            # e.g., [batch, frames, n_mels] or [batch, 1, samples]
            if len(shape) >= 3:
                needs_mel = True
            elif len(shape) == 2 and (shape[1] in (80, 64, 128)):
                needs_mel = True

        if needs_mel:
            mel = self._log_mel(audio, sample_rate=DEFAULT_SAMPLE_RATE)
            # Expect shape (frames, n_mels); add batch dimension
            mel_in = mel[np.newaxis, :, :]
            return {name: mel_in.astype(np.float32)}
        else:
            # Waveform path: add batch
            wav_in = audio[np.newaxis, :]
            return {name: wav_in.astype(np.float32)}

    def _log_mel(
        self,
        audio: np.ndarray,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        n_fft: int = 400,
        hop_length: int = 160,
        win_length: int = 400,
        n_mels: int = 80,
        fmin: int = 20,
        fmax: int = 8000,
    ) -> np.ndarray:
        if librosa is None:
            raise RuntimeError("librosa is required for mel extraction")
        mel = librosa.feature.melspectrogram(
            y=audio,
            sr=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            win_length=win_length,
            n_mels=n_mels,
            fmin=fmin,
            fmax=fmax,
            center=True,
        )
        log_mel = librosa.power_to_db(mel, ref=np.max)
        return log_mel.T  # shape: (frames, n_mels)

    def _emit(self, name: str):
        if self.on_event:
            try:
                self.on_event(name)
            except Exception:
                pass

    # -------- Parakeet pipeline --------
    def _load_vocab(self, path: Path) -> List[str]:
        if not path.exists():
            raise FileNotFoundError(f"Vocab file not found: {path}")
        entries = []
        max_idx = -1
        blank = None
        for line_num, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            # Split by any whitespace, expect at least 2 parts (token, index)
            parts = line.strip().split()
            if len(parts) < 2:
                logger.warning(f"[vocab] Skipping malformed line {line_num}: '{line[:50]}'")
                continue
            tok = parts[0]
            try:
                idx = int(parts[-1])  # Use last part as index (more robust)
            except ValueError:
                logger.warning(f"[vocab] Invalid index on line {line_num}: '{line[:50]}'")
                continue
            entries.append((idx, tok))
            if tok == BLANK_TOKEN:
                blank = idx
            max_idx = max(max_idx, idx)
        if not entries:
            raise ValueError(f"Vocab file is empty or has no valid entries: {path}")
        vocab = [""] * (max_idx + 1)
        for idx, tok in entries:
            vocab[idx] = tok
        self._blank_id = blank if blank is not None else self._find_token_id(BLANK_TOKEN, vocab)
        self._vocab_size = len(vocab)
        return vocab

    def _find_token_id(self, token: str, vocab: List[str]) -> Optional[int]:
        try:
            return vocab.index(token)
        except ValueError:
            return None

    def _transcribe_parakeet(self, audio: np.ndarray):
        if not (self._nemo_sess and self._enc_sess and self._dec_sess and self._vocab):
            raise RuntimeError("Parakeet pipeline not initialized")

        import time as _time
        t0 = _time.perf_counter()

        vocab = self._vocab
        blank_id = self._blank_id if self._blank_id is not None else len(vocab) - 1
        start_id = self._start_id if self._start_id is not None else None

        audio_duration = len(audio) / DEFAULT_SAMPLE_RATE
        logger.info(f"[parakeet] Starting transcription: {audio_duration:.2f}s audio, {len(audio)} samples")

        # 1) Feature extraction
        t1 = _time.perf_counter()
        feats, feats_len = self._run_nemo(audio)
        t2 = _time.perf_counter()
        logger.debug(f"[parakeet] Nemo features: {feats.shape}, took {(t2-t1)*1000:.1f}ms")

        # 2) Encoder
        enc_out, enc_len = self._run_encoder(feats, feats_len)
        t3 = _time.perf_counter()
        logger.debug(f"[parakeet] Encoder: {enc_out.shape}, took {(t3-t2)*1000:.1f}ms")

        # 3) Greedy RNNT decode using decoder_joint
        text, tokens = self._rnnt_greedy(enc_out, enc_len, blank_id, start_id)
        t4 = _time.perf_counter()

        total_ms = (t4 - t0) * 1000
        rtf = total_ms / (audio_duration * 1000) if audio_duration > 0 else 0
        logger.info(f"[parakeet] Decoded {len(tokens)} tokens -> {len(text)} chars in {total_ms:.0f}ms (RTF={rtf:.2f})")

        return text, tokens

    def _run_nemo(self, audio: np.ndarray):
        assert self._nemo_sess is not None
        feed = {"waveforms": audio[np.newaxis, :].astype(np.float32), "waveforms_lens": np.array([audio.shape[-1]], dtype=np.int64)}
        outputs = self._nemo_sess.run(None, feed)
        feats = outputs[0]  # shape (1, 128, T)
        feats_len = outputs[1] if len(outputs) > 1 else np.array([feats.shape[-1]], dtype=np.int64)
        return feats, feats_len

    def _run_encoder(self, feats: np.ndarray, feats_len: np.ndarray):
        assert self._enc_sess is not None
        feed = {"audio_signal": feats.astype(np.float32), "length": feats_len.astype(np.int64)}
        outputs = self._enc_sess.run(None, feed)
        enc = outputs[0]  # shape (1, 1024, T)
        enc_len = outputs[1] if len(outputs) > 1 else np.array([enc.shape[-1]], dtype=np.int64)
        # Transpose to (B, T, 1024) for convenience
        enc = np.transpose(enc, (0, 2, 1))
        return enc, enc_len

    def _rnnt_greedy(self, encoder_out: np.ndarray, encoder_len: np.ndarray, blank_id: int, start_id: Optional[int]) -> List[int]:
        """
        Greedy RNNT decode step-by-step (per Handy/transcribe-rs):
        - use encoder step-by-step
        - feed last emitted token (start with blank)
        - ignore duration head (last logits)
        - update predictor states only on emit
        """
        assert self._dec_sess is not None
        # encoder_out: (1, T, 1024)
        enc = encoder_out[0]
        T = int(encoder_len[0])
        state1 = np.zeros((2, 1, 640), dtype=np.float32)
        state2 = np.zeros((2, 1, 640), dtype=np.float32)
        tokens: List[int] = []
        timestamps: List[float] = []
        last_token = blank_id  # start with blank as in Handy

        for t in range(T):
            enc_step = enc[t].reshape(1, 1024, 1).astype(np.float32)  # (1,1024,1)
            emitted = 0
            for _ in range(MAX_TOKENS_PER_STEP):
                tgt = np.array([[last_token]], dtype=np.int32)
                tgt_len = np.array([1], dtype=np.int32)
                feed = {
                    "encoder_outputs": enc_step,
                    "targets": tgt,
                    "target_length": tgt_len,
                    "input_states_1": state1,
                    "input_states_2": state2,
                }
                out = self._dec_sess.run(None, feed)
                logits = out[0]
                new_state1 = out[2] if len(out) > 2 else state1
                new_state2 = out[3] if len(out) > 3 else state2

                # Handle possible shapes: (1, T_tar, T_enc, V) or (1, T_enc, T_tar, V) or (1, T_tar, V)
                if logits.ndim == 4:
                    if logits.shape[2] >= 1:
                        logvec = logits[0, 0, -1, :]
                    else:
                        logvec = logits[0, -1, -1, :]
                elif logits.ndim == 3:
                    logvec = logits[0, -1, :]
                else:
                    logvec = logits.reshape(-1)

                vocab_logits = logvec[: self._vocab_size] if self._vocab_size else logvec
                token = int(np.argmax(vocab_logits))
                if token < 0 or token >= self._vocab_size:
                    token = blank_id

                if token != blank_id:
                    tokens.append(token)
                    timestamps.append(t * WINDOW_SIZE * SUBSAMPLING)
                    state1, state2 = new_state1, new_state2  # advance states only on emit
                    last_token = token
                    emitted += 1
                else:
                    # Blank: advance encoder frame
                    break
                if emitted >= MAX_TOKENS_PER_STEP:
                    break
            # next encoder frame
        text = self._tokens_to_text(tokens, self._vocab or [])
        if not text:
            logger.warning(f"[parakeet] Empty text from tokens (len={len(tokens)}): {tokens[:20]}")
        return text, tokens

    def _tokens_to_text(self, tokens: List[int], vocab: List[str]) -> str:
        pieces = []
        for tid in tokens:
            if tid < 0 or tid >= len(vocab):
                continue
            tok = vocab[tid]
            if tok == BLANK_TOKEN or tok.startswith("<|") or tok.startswith("<") and tok.endswith(">"):
                continue
            tok = tok.replace("▁", " ")
            pieces.append(tok)
        text = "".join(pieces)
        text = SPACE_RE.sub(lambda m: "" if m.group(1) is None else " ", text).strip()
        return text
