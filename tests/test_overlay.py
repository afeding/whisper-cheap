import os
import unittest

try:
    from PyQt6 import QtWidgets
except ImportError:
    QtWidgets = None

from src.ui.overlay import RecordingOverlay, StatusOverlay


class OverlayTests(unittest.TestCase):
    def setUp(self):
        if QtWidgets is None:
            self.skipTest("PyQt6 not installed")
        # use offscreen platform to avoid GUI requirement
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def tearDown(self):
        if QtWidgets and QtWidgets.QApplication.instance():
            QtWidgets.QApplication.instance().quit()

    def test_recording_overlay_level(self):
        ov = RecordingOverlay()
        ov.update_level(0.5)
        self.assertEqual(ov.level.value(), 50)

    def test_status_overlay_text(self):
        ov = StatusOverlay("Transcribing...")
        ov.set_text("Formatting...")
        self.assertEqual(ov.label.text(), "Formatting...")


if __name__ == "__main__":
    unittest.main()
