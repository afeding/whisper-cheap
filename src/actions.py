"""
Core actions glue layer (start/stop/cancel).

Managers are injected so the module does not create global singletons.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from src.managers.audio import AudioRecordingManager

logger = logging.getLogger(__name__)


def start(
    binding_id: str,
    audio_manager: Optional[AudioRecordingManager] = None,
    model_manager: Any = None,
    transcription_manager: Any = None,
    sound_player: Any = None,
    model_id: Optional[str] = None,
    on_state: Optional[Callable[[str], None]] = None,
    device_id: Optional[int] = None,
) -> None:
    """Preload model (if provided) and start recording."""
    if transcription_manager and hasattr(transcription_manager, "preload_async"):
        try:
            transcription_manager.preload_async(model_id or getattr(model_manager, "active_model", None) or "parakeet-v3-int8")
        except Exception:
            pass
    if sound_player and hasattr(sound_player, "play_start"):
        try:
            sound_player.play_start()
        except Exception:
            pass
    if audio_manager:
        audio_manager.start_recording(binding_id, device_id=device_id)
    if on_state:
        on_state("recording")


def stop(
    binding_id: str,
    audio_manager: Optional[AudioRecordingManager] = None,
    transcription_manager: Any = None,
    model_id: Optional[str] = None,
    sound_player: Any = None,
    on_state: Optional[Callable[[str], None]] = None,
    on_progress: Optional[Callable[[str], None]] = None,
    model_manager: Any = None,
    history_manager: Any = None,
    llm_client: Any = None,
    llm_enabled: bool = False,
    llm_model_id: Optional[str] = None,
    llm_providers: Optional[list[str]] = None,
    postprocess_prompt: Optional[str] = None,
    system_prompt: Optional[str] = None,
    paste_method: Optional[str] = None,
    clipboard_policy: Optional[str] = None,
) -> dict:
    """Stop recording, optionally transcribe, postprocess, save, and paste."""
    samples = None
    if audio_manager:
        samples = audio_manager.stop_recording(binding_id)
        logger.info(f"Audio capturado: {getattr(samples, 'shape', None)}")

    text = None
    post_text = None
    timestamp = None
    fname = None
    model_ready = True
    progress = on_progress or (lambda *_: None)
    if model_manager and hasattr(model_manager, "is_downloaded"):
        target = model_id or "parakeet-v3-int8"
        if not model_manager.is_downloaded(target):
            logger.error(f"Modelo {target} no esta descargado.")
            model_ready = False

    if samples is None or getattr(samples, "size", 0) == 0:
        logger.warning("No se capturo audio; nada que transcribir.")

    if transcription_manager and samples is not None and samples.size > 0 and model_ready:
        try:
            if hasattr(transcription_manager, "load_model"):
                transcription_manager.load_model(model_id or "parakeet-v3-int8")
            progress("transcribing")
            res = transcription_manager.transcribe(samples)  # type: ignore[attr-defined]
            if isinstance(res, dict):
                text = res.get("text")
            else:
                text = str(res)
            if text:
                logger.info(f"[stt] Texto base ({len(text)} chars): {text[:100]}...")
        except Exception as exc:
            logger.exception(f"Error transcribiendo: {exc}")
            text = None

        if llm_enabled and llm_client and text:
            try:
                progress("formatting")
                logger.info(f"[llm] Ejecutando post-proceso con modelo: {llm_model_id or llm_client.default_model}")
                llm_res = llm_client.postprocess(
                    text,
                    postprocess_prompt or "${output}",
                    model=llm_model_id or None,
                    system_prompt=system_prompt,
                    providers=llm_providers,
                )
                if llm_res and llm_res.get("text"):
                    post_text = llm_res["text"]
                    logger.info(f"[llm] Texto post-procesado ({len(post_text)} chars)")
                else:
                    logger.warning("[llm] Respuesta vacia o sin texto; se usara la transcripcion original.")
            except Exception as exc:
                logger.exception(f"Post-proceso LLM fallo: {exc}")
                post_text = None
        elif llm_enabled and not llm_client and text:
            logger.warning("Post-proceso LLM omitido: cliente no disponible.")

        if history_manager:
            import numpy as _np
            import time as _time

            timestamp = int(_time.time())
            fname = history_manager.save_audio(_np.asarray(samples, dtype=_np.float32), timestamp)
            history_manager.insert_entry(
                file_name=fname,
                timestamp=timestamp,
                transcription_text=text or "",
                saved=False,
                post_processed_text=post_text,
                post_process_prompt=postprocess_prompt,
            )
            logger.info(f"Audio guardado en: {history_manager.recordings_dir / fname}")

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
        else:
            logger.warning("Transcripcion vacia o fallida.")

    if on_state:
        on_state("idle")
    progress("done")
    if sound_player and hasattr(sound_player, "play_end"):
        try:
            sound_player.play_end()
        except Exception:
            pass

    return {"audio": samples, "text": post_text or text, "file_name": fname, "timestamp": timestamp, "model_ready": model_ready}


def cancel(
    audio_manager: Optional[AudioRecordingManager] = None,
    on_state: Optional[Callable[[str], None]] = None,
) -> None:
    """Cancel current recording."""
    if audio_manager:
        audio_manager.cancel()
    if on_state:
        on_state("idle")
