"""
History management for Whisper Cheap.

Stores transcription metadata in SQLite and saves WAV recordings.
Includes cleanup policies to keep disk usage bounded.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import time
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


SCHEMA_V1 = """
CREATE TABLE IF NOT EXISTS transcription_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    saved BOOLEAN DEFAULT 0,
    title TEXT,
    transcription_text TEXT NOT NULL,
    post_processed_text TEXT,
    post_process_prompt TEXT
);
"""


class HistoryManager:
    def __init__(self, db_path: Path | str, recordings_dir: Path | str) -> None:
        self.db_path = Path(db_path)
        self.recordings_dir = Path(recordings_dir)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        try:
            with self._connect() as conn:
                # Check database integrity first
                result = conn.execute("PRAGMA integrity_check").fetchone()
                if result[0] != "ok":
                    raise sqlite3.DatabaseError(f"Database corrupted: {result[0]}")
                conn.execute(SCHEMA_V1)
                conn.commit()
        except sqlite3.DatabaseError as e:
            # Database is corrupted - backup and recreate
            logger.error(f"[history] Database error: {e}")
            self._handle_corrupted_db()

    def _handle_corrupted_db(self):
        """Backup corrupted database and create fresh one."""
        if self.db_path.exists():
            backup_path = self.db_path.with_suffix(".db.corrupted")
            try:
                # Remove old backup if exists
                backup_path.unlink(missing_ok=True)
                self.db_path.rename(backup_path)
                logger.warning(f"[history] Corrupted DB backed up to: {backup_path.name}")
            except OSError as e:
                logger.error(f"[history] Could not backup corrupted DB: {e}")
                # Try to delete it instead
                try:
                    self.db_path.unlink()
                except OSError:
                    pass

        # Create fresh database
        try:
            with self._connect() as conn:
                conn.execute(SCHEMA_V1)
                conn.commit()
            logger.info("[history] Created fresh database")
        except Exception as e:
            logger.error(f"[history] Failed to create fresh DB: {e}")

    def insert_entry(
        self,
        file_name: str,
        timestamp: int,
        transcription_text: str,
        saved: bool = False,
        title: Optional[str] = None,
        post_processed_text: Optional[str] = None,
        post_process_prompt: Optional[str] = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO transcription_history
                (file_name, timestamp, saved, title, transcription_text, post_processed_text, post_process_prompt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_name,
                    timestamp,
                    int(saved),
                    title,
                    transcription_text,
                    post_processed_text,
                    post_process_prompt,
                ),
            )
            conn.commit()
            entry_id = cur.lastrowid
            logger.info(f"[history] Saved entry #{entry_id}: {file_name}, {len(transcription_text)} chars")
            return entry_id

    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT id, file_name, timestamp, saved, title, transcription_text, post_processed_text, post_process_prompt FROM transcription_history ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {int(limit)}"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        keys = ["id", "file_name", "timestamp", "saved", "title", "transcription_text", "post_processed_text", "post_process_prompt"]
        return [dict(zip(keys, row)) for row in rows]

    def mark_saved(self, entry_id: int, saved: bool = True):
        with self._connect() as conn:
            conn.execute("UPDATE transcription_history SET saved = ? WHERE id = ?", (int(saved), entry_id))
            conn.commit()

    def delete_old(self, policy: str, limit_or_days: int):
        """
        Policies:
        - preserve_limit: keep last N entries (unsaved only), delete older unsaved and their WAVs
        - days: delete older than limit_or_days days (unsaved only)
        - never: do nothing
        """
        policy = policy.lower()
        if policy == "never":
            return
        if policy == "preserve_limit":
            self._delete_preserve_limit(limit_or_days)
        else:
            self._delete_older_than_days(limit_or_days)

    def _delete_preserve_limit(self, limit: int):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, file_name, saved FROM transcription_history ORDER BY timestamp DESC"
            ).fetchall()
            keep_ids = set()
            count_unsaved = 0
            for row in rows:
                rid, fname, saved = row
                if saved:
                    keep_ids.add(rid)
                    continue
                if count_unsaved < limit:
                    keep_ids.add(rid)
                    count_unsaved += 1
            delete_ids = [r[0] for r in rows if r[0] not in keep_ids and r[2] == 0]
            for did in delete_ids:
                self._delete_entry(conn, did)
            conn.commit()

    def _delete_older_than_days(self, days: int):
        cutoff = int(time.time()) - days * 86400
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, file_name FROM transcription_history WHERE timestamp < ? AND saved = 0",
                (cutoff,),
            ).fetchall()
            for rid, fname in rows:
                self._delete_entry(conn, rid)
            conn.commit()

    def _delete_entry(self, conn, entry_id: int):
        row = conn.execute(
            "SELECT file_name FROM transcription_history WHERE id = ?", (entry_id,)
        ).fetchone()
        if row:
            fname = row[0]
            wav_path = self.recordings_dir / fname
            try:
                wav_path.unlink(missing_ok=True)
            except Exception:
                pass
        conn.execute("DELETE FROM transcription_history WHERE id = ?", (entry_id,))

    def save_audio(self, samples: np.ndarray, timestamp: int) -> str:
        """
        Save audio as 16-bit PCM WAV and return file name.

        Raises:
            OSError: If disk is full or write fails
        """
        import shutil

        fname = f"whisper-cheap-{timestamp}.wav"
        path = self.recordings_dir / fname

        # Pre-check disk space (samples * 2 bytes for int16 + WAV header ~44 bytes)
        estimated_size = len(samples) * 2 + 100  # +100 for header margin
        try:
            free_space = shutil.disk_usage(self.recordings_dir).free
            if free_space < estimated_size + 1_000_000:  # +1MB safety margin
                raise OSError(
                    f"Disco casi lleno: {free_space // 1_000_000}MB libres, "
                    f"se necesitan ~{estimated_size // 1_000}KB"
                )
        except OSError as e:
            logger.error(f"[history] Disk space check failed: {e}")
            raise

        # Write WAV file with error handling
        samples_int16 = (samples * 32767).astype(np.int16)
        try:
            with wave.open(str(path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(16000)
                wf.writeframes(samples_int16.tobytes())
        except OSError as e:
            # Clean up partial file on failure
            logger.error(f"[history] Failed to save audio: {e}")
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            raise OSError(f"No se pudo guardar audio (disco lleno?): {e}") from e

        return fname

    def clear_all(self):
        """
        Delete all history entries and their audio files.
        Called at app startup to prevent accumulation.
        """
        with self._connect() as conn:
            conn.execute("DELETE FROM transcription_history")
            conn.commit()

        # Delete all WAV files
        for wav in self.recordings_dir.glob("*.wav"):
            try:
                wav.unlink()
            except Exception:
                pass

        logger.info("[history] Cleared all history and recordings")

    def cleanup_orphans(self):
        """
        Remove WAVs without DB rows and DB rows whose files are missing.
        """
        with self._connect() as conn:
            rows = conn.execute("SELECT id, file_name FROM transcription_history").fetchall()
            existing_files = {p.name for p in self.recordings_dir.glob("*.wav")}
            for rid, fname in rows:
                if fname not in existing_files:
                    conn.execute("DELETE FROM transcription_history WHERE id = ?", (rid,))
            conn.commit()

            # Re-query after commit to get current valid files (avoids race condition)
            valid_files = {
                row[0] for row in conn.execute("SELECT file_name FROM transcription_history").fetchall()
            }

        for wav in self.recordings_dir.glob("*.wav"):
            if wav.name not in valid_files:
                try:
                    wav.unlink()
                except Exception:
                    pass
