import sqlite3
import tempfile
import time
import wave
from pathlib import Path
import unittest

import numpy as np

from src.managers.history import HistoryManager


class HistoryManagerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        self.db_path = self.base / "history.db"
        self.rec_dir = self.base / "recordings"
        self.hm = HistoryManager(db_path=self.db_path, recordings_dir=self.rec_dir)

    def tearDown(self):
        # Ensure sqlite connection is closed before cleanup
        try:
            self.hm = None
            sqlite3.connect(self.db_path).close()
        except Exception:
            pass
        import gc
        gc.collect()
        self.tempdir.cleanup()

    def test_insert_and_get(self):
        ts = int(time.time())
        self.hm.insert_entry("file.wav", ts, "hello")
        rows = self.hm.get_all()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["transcription_text"], "hello")

    def test_mark_saved(self):
        ts = int(time.time())
        rid = self.hm.insert_entry("file.wav", ts, "hello")
        self.hm.mark_saved(rid, True)
        rows = self.hm.get_all()
        self.assertEqual(rows[0]["saved"], 1)

    def test_save_audio_writes_wav(self):
        ts = int(time.time())
        audio = np.zeros(160, dtype=np.float32)
        fname = self.hm.save_audio(audio, ts)
        wav_path = self.rec_dir / fname
        self.assertTrue(wav_path.exists())
        with wave.open(str(wav_path), "rb") as wf:
            self.assertEqual(wf.getframerate(), 16000)
            self.assertEqual(wf.getnchannels(), 1)

    def test_cleanup_preserve_limit(self):
        ts = int(time.time())
        for i in range(5):
            self.hm.insert_entry(f"f{i}.wav", ts + i, f"text {i}", saved=False)
        self.hm.delete_old(policy="preserve_limit", limit_or_days=2)
        rows = self.hm.get_all()
        self.assertEqual(len(rows), 2)

    def test_cleanup_older_than_days(self):
        now = int(time.time())
        old_ts = now - 10 * 86400
        rid_old = self.hm.insert_entry("old.wav", old_ts, "old", saved=False)
        rid_new = self.hm.insert_entry("new.wav", now, "new", saved=False)
        self.hm.delete_old(policy="days", limit_or_days=7)
        rows = self.hm.get_all()
        ids = [r["id"] for r in rows]
        self.assertIn(rid_new, ids)
        self.assertNotIn(rid_old, ids)

    def test_cleanup_orphans(self):
        # DB row without file -> delete row
        ts = int(time.time())
        self.hm.insert_entry("missing.wav", ts, "text", saved=False)
        self.hm.cleanup_orphans()
        rows = self.hm.get_all()
        self.assertEqual(len(rows), 0)
        # File without DB -> delete file
        stray = self.rec_dir / "stray.wav"
        self.rec_dir.mkdir(parents=True, exist_ok=True)
        stray.write_bytes(b"data")
        self.hm.cleanup_orphans()
        self.assertFalse(stray.exists())


if __name__ == "__main__":
    unittest.main()
