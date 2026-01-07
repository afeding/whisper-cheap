"""
Thread-safe recording state machine with worker thread for processing.

States:
- IDLE: Not recording (but may have jobs processing in background)
- RECORDING: Currently recording audio

Key feature: You can start a new recording while previous recordings are
still being processed. Results are pasted in FIFO order (first recorded,
first pasted) even if later recordings finish processing first.

This module solves the critical bug where hotkey callbacks were blocked
during transcription, causing missed key presses.
"""

from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class State(Enum):
    """Recording state machine states."""
    IDLE = auto()       # Not recording (may have background jobs)
    RECORDING = auto()  # Currently recording audio


@dataclass
class ProcessingJob:
    """Data needed to process a recording."""
    binding_id: str
    audio_manager: Any
    transcription_manager: Any
    sound_player: Any
    model_id: str
    history_manager: Any
    llm_client: Any
    llm_enabled: bool
    llm_model_id: Optional[str]
    llm_providers: Optional[list[str]]
    postprocess_prompt: Optional[str]
    system_prompt: Optional[str]
    paste_method: Optional[str]
    clipboard_policy: Optional[str]
    on_progress: Optional[Callable[[str], None]] = None
    on_complete: Optional[Callable[[dict], None]] = None
    on_error: Optional[Callable[[Exception], None]] = None
    # Sequence ID for FIFO paste ordering (assigned by state machine)
    seq_id: int = 0
    # Audio samples captured (set by state machine before queueing)
    samples: Any = None


@dataclass
class ProcessingResult:
    """Result of processing a job, ready for pasting."""
    seq_id: int
    text: Optional[str]
    file_name: Optional[str]
    timestamp: Optional[int]
    samples: Any = None
    # Status: "success", "empty", "timeout", "error"
    status: str = "success"
    error_message: Optional[str] = None


class RecordingStateMachine:
    """
    Thread-safe state machine for recording workflow with concurrent processing.

    Key features:
    - Recording and processing are decoupled: you can record while processing
    - Jobs are processed in parallel (transcription) but pasted in FIFO order
    - Queue count is exposed for UI (badge showing pending jobs)
    - All state transitions are protected by a lock
    - Debounce prevents rapid state changes
    """

    # Minimum time between state changes (ms)
    DEBOUNCE_MS = 150

    def __init__(self):
        self._lock = threading.RLock()
        self._state = State.IDLE
        self._last_transition_time = 0.0
        self._show_level = False

        # Sequence counter for FIFO ordering
        self._seq_counter = 0

        # Worker thread for async processing
        self._job_queue: queue.Queue[Optional[ProcessingJob]] = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_worker = threading.Event()

        # FIFO paste queue: results wait here until their turn
        self._paste_queue: dict[int, ProcessingResult] = {}
        self._paste_lock = threading.Lock()
        self._next_paste_seq = 1  # Next seq_id to paste

        # Track pending jobs for UI
        self._pending_count = 0
        self._pending_lock = threading.Lock()

        # Callbacks
        self._on_state_change: Optional[Callable[[State, State], None]] = None
        self._on_queue_change: Optional[Callable[[int], None]] = None

        logger.info("[state] RecordingStateMachine initialized (concurrent mode)")

    def start_worker(self) -> None:
        """Start the background worker thread for processing jobs."""
        if self._worker_thread and self._worker_thread.is_alive():
            logger.warning("[state] Worker thread already running")
            return

        self._stop_worker.clear()
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="RecordingWorker",
            daemon=True
        )
        self._worker_thread.start()
        logger.info("[state] Worker thread started")

    def set_on_queue_change(self, callback: Callable[[int], None]) -> None:
        """Set callback for queue count changes. Called with pending count."""
        self._on_queue_change = callback

    @property
    def pending_count(self) -> int:
        """Number of jobs pending (processing or waiting to paste)."""
        with self._pending_lock:
            return self._pending_count

    def _notify_queue_change(self) -> None:
        """Notify listeners of queue count change."""
        count = self.pending_count
        if self._on_queue_change:
            try:
                self._on_queue_change(count)
            except Exception as e:
                logger.error(f"[state] Error in queue change callback: {e}")

    def stop_worker(self) -> None:
        """
        Stop the background worker thread with extended timeout.

        The worker may be processing a transcription + LLM post-processing job,
        which can take up to 30s (typical: 5-20s for transcription, 10-20s for LLM).
        We give it 10s to finish gracefully before giving up.
        """
        logger.info("[state] Stopping worker thread...")

        # Signal worker to stop and wake it up with sentinel
        self._stop_worker.set()
        self._job_queue.put(None)

        if self._worker_thread and self._worker_thread.is_alive():
            logger.debug(f"[state] Worker thread is alive, waiting for it to join (timeout=10.0s)...")
            self._worker_thread.join(timeout=10.0)

            if self._worker_thread.is_alive():
                logger.warning("[state] Worker thread did not stop within 10s timeout")
                logger.warning("[state] Worker may be stuck in transcription or LLM call")
                logger.warning("[state] Note: if this is a daemon thread, it will be killed by sys.exit() at the end")
            else:
                logger.debug("[state] Worker thread joined successfully")
        else:
            logger.debug("[state] Worker thread is not alive or None")

        logger.info("[state] Worker thread stop sequence completed")

    def set_on_state_change(self, callback: Callable[[State, State], None]) -> None:
        """Set callback for state changes. Called with (old_state, new_state)."""
        self._on_state_change = callback

    @property
    def state(self) -> State:
        """Current state (read-only)."""
        with self._lock:
            return self._state

    @property
    def show_level(self) -> bool:
        """Whether to show audio level in UI."""
        with self._lock:
            return self._show_level

    @property
    def is_recording(self) -> bool:
        """Convenience property for recording state."""
        with self._lock:
            return self._state == State.RECORDING

    @property
    def is_busy(self) -> bool:
        """Whether we're currently recording. Processing doesn't block new recordings."""
        with self._lock:
            return self._state == State.RECORDING

    @property
    def has_pending_jobs(self) -> bool:
        """Whether there are jobs being processed or waiting to paste."""
        return self.pending_count > 0

    def _check_debounce(self) -> bool:
        """Check if enough time has passed since last transition."""
        now = time.time() * 1000
        elapsed = now - self._last_transition_time
        if elapsed < self.DEBOUNCE_MS:
            logger.debug(f"[state] Debounce: {elapsed:.0f}ms < {self.DEBOUNCE_MS}ms, ignoring")
            return False
        return True

    def _transition(self, new_state: State, reason: str = "") -> bool:
        """
        Attempt state transition. Returns True if successful.
        Must be called with lock held.
        """
        old_state = self._state

        # Simplified: only IDLE <-> RECORDING transitions
        valid_transitions = {
            State.IDLE: {State.RECORDING},
            State.RECORDING: {State.IDLE},
        }

        if new_state not in valid_transitions.get(old_state, set()):
            logger.warning(
                f"[state] Invalid transition: {old_state.name} -> {new_state.name} ({reason})"
            )
            return False

        self._state = new_state
        self._last_transition_time = time.time() * 1000

        logger.info(f"[state] {old_state.name} -> {new_state.name} ({reason})")

        if self._on_state_change:
            try:
                self._on_state_change(old_state, new_state)
            except Exception as e:
                logger.error(f"[state] Error in state change callback: {e}")

        return True

    def try_start_recording(self) -> bool:
        """
        Attempt to start recording.
        Returns True if recording started, False if not possible.

        Thread-safe: can be called from hotkey callback.
        Note: Can start recording even if previous jobs are still processing.
        """
        with self._lock:
            if not self._check_debounce():
                return False

            if self._state != State.IDLE:
                logger.warning(
                    f"[state] Cannot start recording: current state is {self._state.name}"
                )
                return False

            if self._transition(State.RECORDING, "hotkey press"):
                self._show_level = True
                return True
            return False

    def try_stop_recording(self, job: ProcessingJob) -> bool:
        """
        Attempt to stop recording and queue processing.
        Returns True if stop was initiated, False if not possible.

        Thread-safe: can be called from hotkey callback.
        The actual processing happens in the worker thread.
        Results are pasted in FIFO order.
        """
        with self._lock:
            if not self._check_debounce():
                return False

            if self._state != State.RECORDING:
                logger.warning(
                    f"[state] Cannot stop recording: current state is {self._state.name}"
                )
                return False

            self._show_level = False

            # Capture audio BEFORE transitioning (still in RECORDING state)
            samples = None
            if job.audio_manager:
                samples = job.audio_manager.stop_recording(job.binding_id)
                if samples is not None:
                    logger.info(f"[state] Audio captured: shape={getattr(samples, 'shape', None)}")

            # Assign sequence ID for FIFO ordering
            self._seq_counter += 1
            job.seq_id = self._seq_counter
            job.samples = samples

            # Increment pending count
            with self._pending_lock:
                self._pending_count += 1

            if not self._transition(State.IDLE, "hotkey release"):
                return False

        # Notify UI of queue change
        self._notify_queue_change()

        # Queue the job for the worker thread (outside lock to avoid deadlock)
        logger.debug(f"[state] Queueing job seq={job.seq_id}, pending={self.pending_count}")
        self._job_queue.put(job)
        return True

    def try_cancel(self) -> bool:
        """
        Attempt to cancel current recording.
        Returns True if cancelled, False if nothing to cancel.
        """
        with self._lock:
            if self._state == State.RECORDING:
                self._show_level = False
                return self._transition(State.IDLE, "cancel")
            elif self._state == State.IDLE:
                logger.debug("[state] Nothing to cancel (already IDLE)")
                return False
            else:
                logger.warning(
                    f"[state] Cannot cancel: state is {self._state.name}"
                )
                return False

    def force_idle(self) -> None:
        """
        Force state to IDLE unconditionally.
        Use for error recovery when normal state transitions aren't possible.
        """
        with self._lock:
            old_state = self._state
            self._state = State.IDLE
            self._show_level = False
            if old_state != State.IDLE:
                logger.warning(f"[state] Forced IDLE from {old_state.name}")
                if self._on_state_change:
                    try:
                        self._on_state_change(old_state, State.IDLE)
                    except Exception as e:
                        logger.error(f"[state] Error in state change callback: {e}")

    def toggle(self, job_factory: Callable[[], ProcessingJob]) -> str:
        """
        Toggle recording state (for toggle mode).
        Returns "started", "stopped", or "ignored".

        job_factory is called only if we need to stop (to get fresh config).
        """
        with self._lock:
            current = self._state

        if current == State.IDLE:
            if self.try_start_recording():
                return "started"
            return "ignored"
        elif current == State.RECORDING:
            job = job_factory()
            if self.try_stop_recording(job):
                return "stopped"
            return "ignored"
        else:
            logger.warning(f"[state] Toggle ignored: state is {current.name}")
            return "ignored"

    def _worker_loop(self) -> None:
        """Background worker that processes recordings."""
        logger.info("[worker] Processing worker started")

        while not self._stop_worker.is_set():
            try:
                # Wait for a job with timeout (allows checking stop flag)
                try:
                    job = self._job_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if job is None:  # Sentinel for shutdown
                    logger.debug("[worker] Received shutdown sentinel")
                    break

                self._process_job(job)

            except Exception as e:
                logger.exception(f"[worker] Unexpected error in worker loop: {e}")

        logger.info("[worker] Processing worker stopped")

    def _process_job(self, job: ProcessingJob) -> None:
        """
        Process a single recording job.

        Audio samples are already captured (in job.samples).
        Results are queued for FIFO pasting.
        """
        logger.info(f"[worker] Starting job seq={job.seq_id}")
        start_time = time.time()

        progress = job.on_progress or (lambda *_: None)
        samples = job.samples
        status = "success"
        error_message = None

        try:
            # Check if we have audio to process
            if samples is None or getattr(samples, "size", 0) == 0:
                logger.warning(f"[worker] No audio in job seq={job.seq_id}, skipping")
                result = ProcessingResult(
                    seq_id=job.seq_id,
                    text=None,
                    file_name=None,
                    timestamp=None,
                    status="empty",
                    error_message="No se capturó audio. Mantén presionado el hotkey mientras hablas.",
                )
                self._queue_result_and_paste(result, job)
                return

            # Transcribe
            text = None
            if job.transcription_manager:
                logger.info(f"[worker] Transcribing seq={job.seq_id}...")
                progress("transcribing")
                try:
                    if hasattr(job.transcription_manager, "load_model"):
                        job.transcription_manager.load_model(job.model_id)
                    res = job.transcription_manager.transcribe(samples)
                    if isinstance(res, dict):
                        text = res.get("text")
                    else:
                        text = str(res)
                    if text:
                        logger.info(f"[worker] Transcription complete seq={job.seq_id}: {len(text)} chars")
                    else:
                        logger.warning(f"[worker] Empty transcription seq={job.seq_id}")
                        status = "empty"
                        error_message = "Transcripción vacía. ¿Hablaste lo suficientemente alto?"
                except TimeoutError as e:
                    logger.error(f"[worker] Transcription timeout seq={job.seq_id}: {e}")
                    status = "timeout"
                    error_message = "Timeout: la transcripción tardó demasiado. Intenta con audio más corto."
                except Exception as e:
                    logger.exception(f"[worker] Transcription error seq={job.seq_id}: {e}")
                    status = "error"
                    error_message = f"Error en transcripción: {type(e).__name__}"

            # Post-process with LLM
            post_text = None
            if job.llm_enabled and job.llm_client and text:
                logger.info(f"[worker] LLM processing seq={job.seq_id}...")
                progress("formatting")
                try:
                    llm_res = job.llm_client.postprocess(
                        text,
                        job.postprocess_prompt or "${output}",
                        model=job.llm_model_id,
                        system_prompt=job.system_prompt,
                        providers=job.llm_providers,
                    )
                    if llm_res and llm_res.get("text"):
                        post_text = llm_res["text"]
                        logger.info(f"[worker] LLM complete seq={job.seq_id}: {len(post_text)} chars")
                except Exception as e:
                    # Use error() to avoid stack traces with potential sensitive HTTP details
                    logger.error(f"[worker] LLM error seq={job.seq_id}: {type(e).__name__}: {e}")

            # Save to history
            fname = None
            timestamp = None
            if job.history_manager and samples is not None:
                import numpy as np
                timestamp = int(time.time())
                try:
                    fname = job.history_manager.save_audio(
                        np.asarray(samples, dtype=np.float32), timestamp
                    )
                    job.history_manager.insert_entry(
                        file_name=fname,
                        timestamp=timestamp,
                        transcription_text=text or "",
                        saved=False,
                        post_processed_text=post_text,
                        post_process_prompt=job.postprocess_prompt,
                    )
                except OSError as e:
                    # Disk full or write error - log but don't fail the transcription
                    logger.error(f"[worker] Failed to save audio seq={job.seq_id}: {e}")
                    # Set warning status but keep text (transcription still worked)
                    if status == "success":
                        status = "warning"
                        error_message = f"Audio no guardado: {e}"

            # Create result and queue for FIFO paste
            final_text = post_text or text
            result = ProcessingResult(
                seq_id=job.seq_id,
                text=final_text,
                file_name=fname,
                timestamp=timestamp,
                samples=samples,
                status=status,
                error_message=error_message,
            )

            # Liberar samples del job (ya están en result)
            job.samples = None

            # Add to paste queue and try to paste in order
            self._queue_result_and_paste(result, job)

            elapsed = time.time() - start_time
            logger.info(f"[worker] Job seq={job.seq_id} processed in {elapsed:.2f}s")

        except Exception as e:
            logger.exception(f"[worker] Job seq={job.seq_id} failed: {e}")
            self._complete_job(job, None)
            if job.on_error:
                job.on_error(e)

    def _queue_result_and_paste(self, result: ProcessingResult, job: ProcessingJob) -> None:
        """
        Add result to queue and paste all ready results in FIFO order.

        This ensures that even if job #2 finishes before job #1, we wait
        for job #1 to complete and paste first.
        """
        progress = job.on_progress or (lambda *_: None)

        with self._paste_lock:
            # Add this result to the queue
            self._paste_queue[result.seq_id] = result
            logger.debug(f"[paste] Queued result seq={result.seq_id}, next_paste={self._next_paste_seq}")

            # Try to paste all consecutive ready results
            while self._next_paste_seq in self._paste_queue:
                next_result = self._paste_queue.pop(self._next_paste_seq)
                self._paste_single_result(next_result, job)
                self._next_paste_seq += 1

    def _paste_single_result(self, result: ProcessingResult, job: ProcessingJob) -> None:
        """Paste a single result and update state."""
        progress = job.on_progress or (lambda *_: None)

        if result.text:
            logger.info(f"[paste] Pasting seq={result.seq_id} ({len(result.text)} chars)")
            progress("pasting")
            try:
                from src.utils.paste import ClipboardPolicy, PasteMethod, paste_text
                pm = PasteMethod(job.paste_method) if job.paste_method else PasteMethod.CTRL_V
                policy = ClipboardPolicy(job.clipboard_policy) if job.clipboard_policy else ClipboardPolicy.DONT_MODIFY
                paste_text(result.text, method=pm, policy=policy)
                logger.info(f"[paste] Pasted seq={result.seq_id}")
            except Exception as e:
                logger.exception(f"[paste] Error pasting seq={result.seq_id}: {e}")
                try:
                    from src.utils.clipboard import ClipboardManager
                    ClipboardManager().set_text(result.text)
                except Exception:
                    pass
        else:
            logger.warning(f"[paste] No text for seq={result.seq_id}")

        # Complete this job
        self._complete_job(job, result)

        # Play end sound (only for successfully pasted results)
        if result.text and job.sound_player and hasattr(job.sound_player, "play_end"):
            try:
                job.sound_player.play_end()
            except Exception:
                pass

    def _complete_job(self, job: ProcessingJob, result: Optional[ProcessingResult]) -> None:
        """Mark job as complete, update pending count, notify UI."""
        progress = job.on_progress or (lambda *_: None)

        # Decrement pending count
        with self._pending_lock:
            self._pending_count = max(0, self._pending_count - 1)
            remaining = self._pending_count

        # Notify UI of queue change
        self._notify_queue_change()

        # Only show "done" and call on_complete when ALL jobs are done
        if remaining == 0:
            progress("done")

        if job.on_complete and result:
            job.on_complete({
                "audio": result.samples,
                "text": result.text,
                "file_name": result.file_name,
                "timestamp": result.timestamp,
                "status": result.status,
                "error_message": result.error_message,
            })

        # Liberar samples del result (ya no se necesitan)
        if result:
            result.samples = None

        logger.debug(f"[worker] Job seq={job.seq_id} complete, remaining={remaining}")


# Singleton instance for convenience
_default_state_machine: Optional[RecordingStateMachine] = None


def get_state_machine() -> RecordingStateMachine:
    """Get the default state machine instance."""
    global _default_state_machine
    if _default_state_machine is None:
        _default_state_machine = RecordingStateMachine()
    return _default_state_machine
