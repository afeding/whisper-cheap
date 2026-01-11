"""
Background chunk transcription manager.

Transcribes audio chunks incrementally while recording continues.
Results are accumulated in FIFO order and concatenated at the end.
"""
from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_RATE = 16_000


@dataclass
class ChunkJob:
    """A single chunk to transcribe."""
    audio: np.ndarray
    index: int
    timestamp: float


@dataclass
class ChunkResult:
    """Result of transcribing a chunk."""
    index: int
    text: str
    duration_sec: float
    processing_time_ms: float


class ChunkTranscriber:
    """
    Manages background transcription of audio chunks.

    Thread-safe: chunks can be submitted from audio callback thread.
    Results are available via get_results() after stopping.

    Usage:
        transcriber = ChunkTranscriber(transcription_manager)
        transcriber.start()

        # During recording, submit chunks:
        transcriber.submit_chunk(audio, index)

        # When done:
        transcriber.stop()  # waits for pending chunks
        final_text = transcriber.get_merged_text()
    """

    def __init__(
        self,
        transcription_manager: Any,
        model_id: str = "parakeet-v3-int8",
        on_chunk_done: Optional[Callable[[ChunkResult], None]] = None,
    ):
        self.transcription_manager = transcription_manager
        self.model_id = model_id
        self.on_chunk_done = on_chunk_done

        self._queue: queue.Queue[Optional[ChunkJob]] = queue.Queue()
        self._results: Dict[int, ChunkResult] = {}
        self._results_lock = threading.Lock()

        self._worker: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False

    def start(self) -> None:
        """Start the background worker thread."""
        if self._is_running:
            return

        self._stop_event.clear()
        self._results.clear()
        self._is_running = True

        self._worker = threading.Thread(
            target=self._worker_loop,
            name="ChunkTranscriberWorker",
            daemon=True,
        )
        self._worker.start()
        logger.info("[chunk_transcriber] Worker started")

    def stop(self, timeout: float = 30.0) -> None:
        """
        Stop the worker and wait for pending chunks.

        Args:
            timeout: Max seconds to wait for pending work.
        """
        if not self._is_running:
            return

        logger.info("[chunk_transcriber] Stopping...")
        self._stop_event.set()
        self._queue.put(None)  # Sentinel

        if self._worker:
            self._worker.join(timeout=timeout)
            if self._worker.is_alive():
                logger.warning("[chunk_transcriber] Worker didn't stop in time")

        self._is_running = False
        logger.info(f"[chunk_transcriber] Stopped with {len(self._results)} results")

    def submit_chunk(self, audio: np.ndarray, index: int) -> None:
        """
        Submit a chunk for background transcription.
        Thread-safe: can be called from audio callback.
        """
        if not self._is_running:
            logger.warning("[chunk_transcriber] Not running, ignoring chunk")
            return

        job = ChunkJob(
            audio=audio.copy(),  # Copy to avoid buffer reuse issues
            index=index,
            timestamp=time.time(),
        )
        self._queue.put(job)
        duration = len(audio) / DEFAULT_SAMPLE_RATE
        logger.info(f"[chunk_transcriber] Submitted chunk {index} ({duration:.1f}s)")

    def get_results(self) -> List[ChunkResult]:
        """Get all results in index order."""
        with self._results_lock:
            sorted_indices = sorted(self._results.keys())
            return [self._results[i] for i in sorted_indices]

    def get_merged_text(self, separator: str = " ") -> str:
        """Get all transcribed text merged in order."""
        results = self.get_results()
        texts = [r.text.strip() for r in results if r.text and r.text.strip()]
        return separator.join(texts)

    @property
    def pending_count(self) -> int:
        """Number of chunks waiting to be processed."""
        return self._queue.qsize()

    @property
    def completed_count(self) -> int:
        """Number of chunks that have been transcribed."""
        with self._results_lock:
            return len(self._results)

    def _worker_loop(self) -> None:
        """Background worker that transcribes chunks."""
        logger.debug("[chunk_transcriber] Worker loop started")

        while not self._stop_event.is_set():
            try:
                job = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if job is None:  # Sentinel
                break

            self._process_chunk(job)

        # Drain remaining queue
        while not self._queue.empty():
            try:
                job = self._queue.get_nowait()
                if job is not None:
                    self._process_chunk(job)
            except queue.Empty:
                break

        logger.debug("[chunk_transcriber] Worker loop ended")

    def _process_chunk(self, job: ChunkJob) -> None:
        """Transcribe a single chunk."""
        start_time = time.perf_counter()

        try:
            duration_sec = len(job.audio) / DEFAULT_SAMPLE_RATE
            logger.info(f"[chunk_transcriber] Processing chunk {job.index} ({duration_sec:.1f}s)")

            # Transcribe
            result = self.transcription_manager.transcribe(job.audio, model_id=self.model_id)
            text = result.get("text", "") if isinstance(result, dict) else str(result)

            processing_time = (time.perf_counter() - start_time) * 1000

            chunk_result = ChunkResult(
                index=job.index,
                text=text,
                duration_sec=duration_sec,
                processing_time_ms=processing_time,
            )

            # Store result
            with self._results_lock:
                self._results[job.index] = chunk_result

            logger.info(
                f"[chunk_transcriber] Chunk {job.index} done: "
                f"'{text[:50]}{'...' if len(text) > 50 else ''}' "
                f"in {processing_time:.0f}ms"
            )

            # Notify callback
            if self.on_chunk_done:
                try:
                    self.on_chunk_done(chunk_result)
                except Exception as e:
                    logger.error(f"[chunk_transcriber] Error in callback: {e}")

        except Exception as e:
            logger.exception(f"[chunk_transcriber] Error processing chunk {job.index}: {e}")
            # Store empty result to maintain ordering
            with self._results_lock:
                self._results[job.index] = ChunkResult(
                    index=job.index,
                    text="",
                    duration_sec=0,
                    processing_time_ms=0,
                )
