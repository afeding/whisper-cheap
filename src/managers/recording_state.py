"""
Thread-safe recording state machine with worker thread for processing.

States:
- IDLE: Ready to record
- RECORDING: Currently recording audio
- STOPPING: Transitioning from recording to processing
- PROCESSING: Transcribing/LLM/pasting (async)

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
    IDLE = auto()
    RECORDING = auto()
    STOPPING = auto()  # Brief transition state
    PROCESSING = auto()


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


class RecordingStateMachine:
    """
    Thread-safe state machine for recording workflow.

    Key features:
    - All state transitions are protected by a lock
    - Processing happens in a dedicated worker thread (not hotkey thread)
    - Debounce prevents rapid state changes
    - Detailed logging for debugging
    """

    # Minimum time between state changes (ms)
    DEBOUNCE_MS = 150

    def __init__(self):
        self._lock = threading.RLock()
        self._state = State.IDLE
        self._last_transition_time = 0.0
        self._show_level = False

        # Worker thread for async processing
        self._job_queue: queue.Queue[Optional[ProcessingJob]] = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_worker = threading.Event()

        # Callbacks
        self._on_state_change: Optional[Callable[[State, State], None]] = None

        logger.info("[state] RecordingStateMachine initialized")

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

    def stop_worker(self) -> None:
        """Stop the background worker thread."""
        logger.info("[state] Stopping worker thread...")
        self._stop_worker.set()
        self._job_queue.put(None)  # Sentinel to wake up worker
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)
            if self._worker_thread.is_alive():
                logger.warning("[state] Worker thread did not stop cleanly")
        logger.info("[state] Worker thread stopped")

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
        """Whether we're recording or processing (can't start new recording)."""
        with self._lock:
            return self._state in (State.RECORDING, State.STOPPING, State.PROCESSING)

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

        # Validate transition
        valid_transitions = {
            State.IDLE: {State.RECORDING},
            State.RECORDING: {State.STOPPING, State.IDLE},  # IDLE for cancel
            State.STOPPING: {State.PROCESSING, State.IDLE},  # IDLE if no audio
            State.PROCESSING: {State.IDLE},
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

            if not self._transition(State.STOPPING, "hotkey release"):
                return False

        # Queue the job for the worker thread (outside lock to avoid deadlock)
        logger.debug("[state] Queueing processing job")
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
        """Process a single recording job."""
        logger.info("[worker] Starting job processing")
        start_time = time.time()

        try:
            # Transition to PROCESSING
            with self._lock:
                if self._state == State.STOPPING:
                    self._transition(State.PROCESSING, "worker started")
                else:
                    logger.warning(
                        f"[worker] Unexpected state {self._state.name}, expected STOPPING"
                    )

            # Import here to avoid circular imports
            from src import actions

            progress = job.on_progress or (lambda *_: None)

            # Stop recording and get audio
            logger.info("[worker] Stopping audio capture...")
            samples = None
            if job.audio_manager:
                samples = job.audio_manager.stop_recording(job.binding_id)
                if samples is not None:
                    logger.info(f"[worker] Audio captured: shape={getattr(samples, 'shape', None)}")
                else:
                    logger.warning("[worker] No audio samples returned")

            # Check if we have audio to process
            if samples is None or getattr(samples, "size", 0) == 0:
                logger.warning("[worker] No audio captured, nothing to transcribe")
                with self._lock:
                    self._transition(State.IDLE, "no audio")
                progress("done")
                if job.on_complete:
                    job.on_complete({"text": None, "audio": None})
                return

            # Transcribe
            text = None
            if job.transcription_manager:
                logger.info("[worker] Starting transcription...")
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
                        logger.info(f"[worker] Transcription complete: {len(text)} chars")
                        logger.debug(f"[worker] Text: {text[:200]}...")
                    else:
                        logger.warning("[worker] Transcription returned empty text")
                except Exception as e:
                    logger.exception(f"[worker] Transcription error: {e}")

            # Post-process with LLM
            post_text = None
            if job.llm_enabled and job.llm_client and text:
                logger.info(f"[worker] Starting LLM post-processing with {job.llm_model_id}...")
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
                        logger.info(f"[worker] LLM post-processing complete: {len(post_text)} chars")
                    else:
                        logger.warning("[worker] LLM returned empty response")
                except Exception as e:
                    logger.exception(f"[worker] LLM error: {e}")

            # Save to history
            fname = None
            timestamp = None
            if job.history_manager and samples is not None:
                import numpy as np
                timestamp = int(time.time())
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
                logger.info(f"[worker] Saved to history: {fname}")

            # Paste result
            final_text = post_text or text
            if final_text:
                logger.info("[worker] Pasting result...")
                progress("pasting")
                try:
                    from src.utils.paste import ClipboardPolicy, PasteMethod, paste_text
                    pm = PasteMethod(job.paste_method) if job.paste_method else PasteMethod.CTRL_V
                    policy = ClipboardPolicy(job.clipboard_policy) if job.clipboard_policy else ClipboardPolicy.DONT_MODIFY
                    paste_text(final_text, method=pm, policy=policy)
                    logger.info("[worker] Paste complete")
                except Exception as e:
                    logger.exception(f"[worker] Paste error: {e}")
                    # Fallback to clipboard
                    try:
                        from src.utils.clipboard import ClipboardManager
                        ClipboardManager().set_text(final_text)
                        logger.info("[worker] Fallback: copied to clipboard")
                    except Exception as clip_err:
                        logger.error(f"[worker] Clipboard fallback failed: {clip_err}")

            # Play end sound
            if job.sound_player and hasattr(job.sound_player, "play_end"):
                try:
                    job.sound_player.play_end()
                except Exception:
                    pass

            # Done
            elapsed = time.time() - start_time
            logger.info(f"[worker] Job complete in {elapsed:.2f}s")
            progress("done")

            result = {
                "audio": samples,
                "text": final_text,
                "file_name": fname,
                "timestamp": timestamp,
            }

            if job.on_complete:
                job.on_complete(result)

        except Exception as e:
            logger.exception(f"[worker] Job failed: {e}")
            if job.on_error:
                job.on_error(e)

        finally:
            # Always return to IDLE
            with self._lock:
                if self._state != State.IDLE:
                    self._transition(State.IDLE, "job finished")


# Singleton instance for convenience
_default_state_machine: Optional[RecordingStateMachine] = None


def get_state_machine() -> RecordingStateMachine:
    """Get the default state machine instance."""
    global _default_state_machine
    if _default_state_machine is None:
        _default_state_machine = RecordingStateMachine()
    return _default_state_machine
