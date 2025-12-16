import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.managers.transcription import TranscriptionManager


class FakeModelManager:
    def __init__(self, base: Path):
        self.base = base

    def is_downloaded(self, model_id: str) -> bool:
        return (self.base / model_id).exists()

    def get_model_path(self, model_id: str) -> Path:
        return self.base / model_id


class FakeSession:
    def __init__(self):
        self.last_input = None

    def run(self, outputs, feeds):
        self.last_input = feeds["input"]
        return [["hello world"]]


class TranscriptionManagerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        self.model_dir = self.base / "parakeet-v3-int8"
        self.model_dir.mkdir(parents=True)
        (self.model_dir / "model.onnx").write_text("dummy", encoding="utf-8")

        self.fake_session = FakeSession()
        self.fake_mm = FakeModelManager(self.base)
        self.events = []
        self.tm = TranscriptionManager(
            model_manager=self.fake_mm,
            session_factory=lambda path: self.fake_session,
            on_event=self.events.append,
            unload_timeout_seconds=1,
        )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_load_and_transcribe(self):
        self.tm.load_model("parakeet-v3-int8")
        audio = np.ones(8000, dtype=np.float32) * 2.0  # will be normalized
        result = self.tm.transcribe(audio)
        self.assertEqual(result["text"], "hello world")
        self.assertTrue(self.fake_session.last_input is not None)
        # normalized to <=1
        self.assertLessEqual(np.max(np.abs(self.fake_session.last_input)), 1.0)
        self.assertIn("loading-started", self.events)
        self.assertIn("loading-completed", self.events)

    def test_pad_audio_min_length(self):
        self.tm.load_model("parakeet-v3-int8")
        short_audio = np.zeros(1000, dtype=np.float32)
        self.tm.transcribe(short_audio)
        fed = self.fake_session.last_input
        self.assertEqual(fed.shape[1], int(1.25 * 16000))

    def test_apply_custom_words(self):
        text = "jira kubernetes"
        updated = self.tm.apply_custom_words(text, {"jira": "JIRA", "kubernetes": "K8s"})
        self.assertEqual(updated, "JIRA K8s")

    def test_unload(self):
        self.tm.load_model("parakeet-v3-int8")
        self.tm.unload_model()
        self.assertIn("unloaded", self.events)
        with self.assertRaises(RuntimeError):
            self.tm.transcribe(np.zeros(10, dtype=np.float32))

    def test_waveform_input_path_without_mel(self):
        # fake session with 2D input -> waveform path
        class WaveformSession(FakeSession):
            def get_inputs(self):
                return [type("Meta", (), {"shape": [None, None], "name": "input"})()]

        tm = TranscriptionManager(
            model_manager=self.fake_mm,
            session_factory=lambda path: WaveformSession(),
            on_event=self.events.append,
        )
        tm.load_model("parakeet-v3-int8")
        audio = np.ones(3200, dtype=np.float32)
        tm.transcribe(audio)
        self.assertEqual(tm._session.last_input.shape[0], 1)  # batch dim

    def test_mel_path_skipped_if_librosa_missing(self):
        # fake session expecting mel; skip if librosa not installed
        try:
            import librosa  # noqa: F401
        except ImportError:
            self.skipTest("librosa not installed")

        class MelSession(FakeSession):
            def get_inputs(self):
                return [type("Meta", (), {"shape": [None, None, 80], "name": "input"})()]

        tm = TranscriptionManager(
            model_manager=self.fake_mm,
            session_factory=lambda path: MelSession(),
            on_event=self.events.append,
        )
        tm.load_model("parakeet-v3-int8")
        audio = np.random.randn(16000).astype(np.float32)
        result = tm.transcribe(audio)
        self.assertEqual(result["text"], "hello world")


if __name__ == "__main__":
    unittest.main()
