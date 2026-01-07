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

import gc
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

# Chunking settings for long audio
CHUNK_THRESHOLD_SEC = 30.0  # Only chunk if audio > 30s
CHUNK_SIZE_SEC = 30.0  # Process in 30s chunks
CHUNK_OVERLAP_SEC = 2.0  # 2s overlap to avoid cutting words

# Timeout for transcription to prevent app freeze
TRANSCRIBE_TIMEOUT_SEC = 120  # 2 minutes max for any transcription


def _get_available_providers() -> list:
    """Get list of available ONNX Runtime providers."""
    if ort is None:
        return []
    try:
        return ort.get_available_providers()
    except Exception:
        return ["CPUExecutionProvider"]


def _resolve_providers(user_provider: str, fallback_to_cpu: bool = True) -> list:
    """
    Resolve user-friendly provider name to ONNX provider list with fallback.

    Args:
        user_provider: "auto", "cpu", "cuda", or full provider name
        fallback_to_cpu: If True, add CPU as fallback when using GPU

    Returns:
        List of provider names in priority order (first = preferred)
    """
    available = _get_available_providers()

    mapping = {
        "cpu": ["CPUExecutionProvider"],
        "cuda": ["CUDAExecutionProvider"],
        "tensorrt": ["TensorrtExecutionProvider"],
    }

    if user_provider == "auto":
        # Auto-detect: prefer CUDA if available
        if "CUDAExecutionProvider" in available:
            providers = ["CUDAExecutionProvider"]
            logger.info("[onnx] Auto-detected CUDA, using GPU acceleration")
        else:
            providers = ["CPUExecutionProvider"]
            logger.info("[onnx] CUDA not available, using CPU")
    elif user_provider.lower() in mapping:
        providers = mapping[user_provider.lower()]
    elif "ExecutionProvider" in user_provider:
        # Full provider name passed directly
        providers = [user_provider]
    else:
        # Unknown, default to CPU
        logger.warning(f"[onnx] Unknown provider '{user_provider}', defaulting to CPU")
        providers = ["CPUExecutionProvider"]

    # Add CPU fallback for GPU providers
    if fallback_to_cpu and providers[0] != "CPUExecutionProvider":
        if "CPUExecutionProvider" not in providers:
            providers.append("CPUExecutionProvider")

    # Filter to only available providers
    final_providers = [p for p in providers if p in available]
    if not final_providers:
        logger.warning("[onnx] No requested providers available, falling back to CPU")
        final_providers = ["CPUExecutionProvider"]

    return final_providers


def _create_onnx_session(path: str, providers: list = None):
    """Create ONNX session with memory-efficient options and provider fallback."""
    if ort is None:
        raise RuntimeError("onnxruntime is not available")

    if providers is None:
        providers = ["CPUExecutionProvider"]

    sess_opts = ort.SessionOptions()
    sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

    # Thread settings - more threads for CPU, less for GPU (GPU handles parallelism internally)
    is_gpu = any("CUDA" in p or "Tensorrt" in p for p in providers)
    if is_gpu:
        sess_opts.inter_op_num_threads = 1
        sess_opts.intra_op_num_threads = 1
    else:
        sess_opts.inter_op_num_threads = 2
        sess_opts.intra_op_num_threads = 2

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


class TranscriptionManager:
    def __init__(
        self,
        model_manager: ModelManager,
        provider: str = "auto",
        fallback_to_cpu: bool = True,
        on_event: Optional[Callable[[str], None]] = None,
        session_factory: Optional[Callable[..., Any]] = None,
        unload_timeout_seconds: Optional[int] = None,
    ) -> None:
        self.model_manager = model_manager
        self.on_event = on_event

        # Resolve provider(s) with fallback
        self._providers = _resolve_providers(provider, fallback_to_cpu)
        self.provider = self._providers[0]  # Primary provider for logging
        logger.info(f"[transcription] Using providers: {self._providers}")

        self.session_factory = session_factory or (lambda path: _create_onnx_session(path, self._providers)) if ort else None

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
            # Liberar sesiones ONNX de Parakeet
            self._nemo_sess = None
            self._enc_sess = None
            self._dec_sess = None
            # Liberar vocabulario y metadata
            self._vocab = None
            self._blank_id = None
            self._start_id = None
            self._vocab_size = 0
            # Reset para evitar should_unload() repetido
            self._last_used = None
        self._emit("unloaded")

    # -------- Transcription --------
    def transcribe(self, audio_samples: np.ndarray, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio samples to text.

        Includes timeout protection to prevent app freeze on very long audio.
        Raises TimeoutError if transcription takes longer than TRANSCRIBE_TIMEOUT_SEC.
        """
        if audio_samples is None:
            raise ValueError("audio_samples is required")

        # Prepare audio outside the timeout-protected block
        audio = np.asarray(audio_samples, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio[:, 0]
        audio = self._normalize_audio(audio)
        duration_sec = len(audio) / DEFAULT_SAMPLE_RATE

        # Run transcription in a thread with timeout
        result_holder = [None]
        exception_holder = [None]

        def _do_transcribe():
            try:
                result_holder[0] = self._transcribe_internal(audio, model_id, duration_sec)
            except Exception as e:
                exception_holder[0] = e

        thread = threading.Thread(target=_do_transcribe, daemon=True, name="TranscribeWorker")
        thread.start()
        thread.join(timeout=TRANSCRIBE_TIMEOUT_SEC)

        if thread.is_alive():
            # Timeout occurred - thread is still running
            logger.error(f"[transcribe] TIMEOUT after {TRANSCRIBE_TIMEOUT_SEC}s for {duration_sec:.1f}s audio")
            raise TimeoutError(f"Transcription timeout (>{TRANSCRIBE_TIMEOUT_SEC}s). Audio was {duration_sec:.1f}s long.")

        if exception_holder[0]:
            raise exception_holder[0]

        return result_holder[0] or {"text": "", "segments": [], "tokens": None}

    def _transcribe_internal(self, audio: np.ndarray, model_id: Optional[str], duration_sec: float) -> Dict[str, Any]:
        """Internal transcription logic, called by transcribe() with timeout protection."""
        # Parakeet pipeline path
        if self._nemo_sess and self._enc_sess and self._dec_sess and self._vocab:
            # Use chunking for long audio (>30s)
            if duration_sec > CHUNK_THRESHOLD_SEC:
                logger.info(f"[transcribe] Long audio ({duration_sec:.1f}s), using chunked processing")
                result = self._transcribe_chunked(audio)
            else:
                # Short audio: process directly
                audio = self._pad_audio(audio)
                text, tokens = self._transcribe_parakeet(audio)
                result = {"text": text or "", "segments": [], "tokens": tokens}

            self._last_used = time.time()
            gc.collect()
            return result

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

    # -------- Chunked transcription --------
    def _transcribe_chunked(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Transcribe long audio by splitting into chunks and merging results.

        This reduces memory pressure and improves stability for long recordings.
        Processing is sequential to reuse ONNX sessions (they're not thread-safe).
        """
        import time as _time
        t_start = _time.perf_counter()

        chunks = self._split_audio_chunks(audio)
        texts = []
        all_tokens = []

        for i, chunk in enumerate(chunks):
            logger.info(f"[chunked] Processing chunk {i+1}/{len(chunks)} ({len(chunk)/DEFAULT_SAMPLE_RATE:.1f}s)")
            t_chunk = _time.perf_counter()

            # Pad chunk if needed
            chunk = self._pad_audio(chunk)

            # Transcribe this chunk
            text, tokens = self._transcribe_parakeet(chunk)
            texts.append(text or "")
            if tokens:
                all_tokens.extend(tokens)

            elapsed = (_time.perf_counter() - t_chunk) * 1000
            logger.debug(f"[chunked] Chunk {i+1} done in {elapsed:.0f}ms: '{text[:50]}...' " if text and len(text) > 50 else f"[chunked] Chunk {i+1} done in {elapsed:.0f}ms")

            # Free memory between chunks
            gc.collect()

        # Merge all transcriptions
        merged_text = self._merge_transcriptions(texts)

        total_time = (_time.perf_counter() - t_start) * 1000
        audio_duration = len(audio) / DEFAULT_SAMPLE_RATE
        rtf = total_time / (audio_duration * 1000) if audio_duration > 0 else 0
        logger.info(f"[chunked] Total: {len(chunks)} chunks, {total_time:.0f}ms (RTF={rtf:.2f})")

        return {"text": merged_text, "segments": [], "tokens": all_tokens}

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

    def _split_audio_chunks(
        self,
        audio: np.ndarray,
        chunk_size_sec: float = CHUNK_SIZE_SEC,
        overlap_sec: float = CHUNK_OVERLAP_SEC,
    ) -> List[np.ndarray]:
        """
        Split audio into overlapping chunks for processing long audio.

        Args:
            audio: Audio samples at DEFAULT_SAMPLE_RATE
            chunk_size_sec: Size of each chunk in seconds
            overlap_sec: Overlap between chunks in seconds

        Returns:
            List of audio chunks (numpy arrays)
        """
        chunk_samples = int(chunk_size_sec * DEFAULT_SAMPLE_RATE)
        overlap_samples = int(overlap_sec * DEFAULT_SAMPLE_RATE)
        step_samples = chunk_samples - overlap_samples

        chunks = []
        start = 0
        total_samples = len(audio)

        while start < total_samples:
            end = min(start + chunk_samples, total_samples)
            chunk = audio[start:end]

            # Pad last chunk if too short (min 1.25s for Parakeet)
            min_samples = int(1.25 * DEFAULT_SAMPLE_RATE)
            if len(chunk) < min_samples:
                chunk = np.pad(chunk, (0, min_samples - len(chunk)), mode="constant")

            chunks.append(chunk)
            start += step_samples

            # Avoid tiny last chunk
            if total_samples - start < min_samples and start < total_samples:
                break

        logger.info(f"[chunking] Split {total_samples/DEFAULT_SAMPLE_RATE:.1f}s audio into {len(chunks)} chunks")
        return chunks

    def _merge_transcriptions(
        self,
        texts: List[str],
        overlap_sec: float = CHUNK_OVERLAP_SEC,
    ) -> str:
        """
        Merge transcriptions from overlapping chunks, removing duplicates.

        Uses a simple heuristic: remove common suffix/prefix in overlap regions.
        """
        if not texts:
            return ""
        if len(texts) == 1:
            return texts[0]

        merged = texts[0]

        for i in range(1, len(texts)):
            current = texts[i]
            if not current:
                continue
            if not merged:
                merged = current
                continue

            # Find overlap by looking for common words
            # Split into words and find longest matching suffix/prefix
            merged_words = merged.split()
            current_words = current.split()

            # Look for overlap in last N words of merged and first N words of current
            # Overlap region corresponds to ~2s of audio, typically 5-15 words
            max_overlap_words = min(20, len(merged_words), len(current_words))
            best_overlap = 0

            for overlap_len in range(1, max_overlap_words + 1):
                suffix = merged_words[-overlap_len:]
                prefix = current_words[:overlap_len]
                if suffix == prefix:
                    best_overlap = overlap_len

            if best_overlap > 0:
                # Remove overlapping words from current
                current_words = current_words[best_overlap:]
                logger.debug(f"[merge] Removed {best_overlap} overlapping words")

            # Join with space
            if current_words:
                merged = merged + " " + " ".join(current_words)

        return merged.strip()

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
        Optimized greedy RNNT decode with label-looping inspired optimizations:
        - Pre-allocated arrays to reduce memory allocations
        - Cached encoder frame reshaping
        - Early termination on long silence
        - Batch-friendly data structures
        """
        assert self._dec_sess is not None

        # encoder_out: (1, T, 1024)
        enc = encoder_out[0]
        T = int(encoder_len[0])

        # Pre-allocate states (avoid repeated allocations)
        state1 = np.zeros((2, 1, 640), dtype=np.float32)
        state2 = np.zeros((2, 1, 640), dtype=np.float32)

        # Pre-allocate reusable arrays
        tgt = np.zeros((1, 1), dtype=np.int32)
        tgt_len = np.array([1], dtype=np.int32)

        tokens: List[int] = []
        last_token = blank_id

        # Label-looping optimization: track consecutive blanks
        consecutive_blanks = 0
        MAX_CONSECUTIVE_BLANKS = 50  # Skip remaining if >50 blanks in a row (silence)

        # Pre-compute encoder frame reshapes (memory layout optimization)
        # This avoids repeated reshape calls in the loop
        enc_frames = enc.reshape(T, 1, 1024, 1).astype(np.float32, copy=False)

        vocab_size = self._vocab_size

        for t in range(T):
            # Use pre-computed frame (zero-copy view)
            enc_step = enc_frames[t]

            emitted = 0
            for _ in range(MAX_TOKENS_PER_STEP):
                # Update target in-place
                tgt[0, 0] = last_token

                # Build feed dict (reuse arrays)
                feed = {
                    "encoder_outputs": enc_step,
                    "targets": tgt,
                    "target_length": tgt_len,
                    "input_states_1": state1,
                    "input_states_2": state2,
                }

                out = self._dec_sess.run(None, feed)
                logits = out[0]

                # Extract logits vector (handle various output shapes)
                if logits.ndim == 4:
                    logvec = logits[0, 0, -1, :vocab_size] if logits.shape[2] >= 1 else logits[0, -1, -1, :vocab_size]
                elif logits.ndim == 3:
                    logvec = logits[0, -1, :vocab_size]
                else:
                    logvec = logits.ravel()[:vocab_size]

                # Argmax (numpy optimized)
                token = int(np.argmax(logvec))

                if token != blank_id and 0 <= token < vocab_size:
                    tokens.append(token)
                    # Update states only on emit
                    if len(out) > 2:
                        state1 = out[2]
                    if len(out) > 3:
                        state2 = out[3]
                    last_token = token
                    emitted += 1
                    consecutive_blanks = 0  # Reset blank counter
                else:
                    # Blank: advance encoder frame
                    consecutive_blanks += 1
                    break

                if emitted >= MAX_TOKENS_PER_STEP:
                    break

            # Early termination: if we've seen many consecutive blanks, likely silence
            # This provides speedup for audio with silence at the end
            if consecutive_blanks >= MAX_CONSECUTIVE_BLANKS:
                remaining = T - t - 1
                if remaining > 10:
                    logger.debug(f"[decoder] Early termination: {consecutive_blanks} consecutive blanks, skipping {remaining} frames")
                break

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
