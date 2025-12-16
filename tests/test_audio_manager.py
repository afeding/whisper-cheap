import numpy as np
import unittest
from pathlib import Path

from src.managers.audio import AudioRecordingManager, RecordingConfig


class AudioManagerMockTests(unittest.TestCase):
    def setUp(self):
        config = RecordingConfig(always_on_stream=True, vad_threshold=0.1)
        self.events = []
        self.manager = AudioRecordingManager(
            config=config,
            model_dir=Path("src/resources/models"),
            on_event=self.events.append,
        )
        # Replace VAD with simple threshold to avoid ONNX dependency during tests
        class SimpleVAD:
            def is_speech(self, chunk, threshold):
                rms = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0
                return rms >= threshold
        self.manager.vad = SimpleVAD()

    def test_start_stop_collects_audio(self):
        tone = np.ones(512, dtype=np.float32) * 0.5
        self.manager.start_recording(binding_id="test")
        self.manager.feed_samples(tone)
        out = self.manager.stop_recording(binding_id="test")
        self.assertGreater(out.size, 0)
        self.assertAlmostEqual(float(out.mean()), 0.5, places=2)
        self.assertIn("recording-started", self.events)
        self.assertIn("recording-stopped", self.events)

    def test_cancel_clears_buffer(self):
        tone = np.ones(256, dtype=np.float32) * 0.3
        self.manager.start_recording(binding_id="test")
        self.manager.feed_samples(tone)
        self.manager.cancel()
        out = self.manager.stop_recording(binding_id="test")
        self.assertEqual(out.size, 0)
        self.assertIn("recording-cancelled", self.events)

    def test_stop_with_wrong_binding_is_ignored(self):
        self.manager.start_recording(binding_id="test")
        out = self.manager.stop_recording(binding_id="other")
        self.assertEqual(out.size, 0)
        self.assertIn("recording-stop-ignored", self.events)


if __name__ == "__main__":
    unittest.main()
