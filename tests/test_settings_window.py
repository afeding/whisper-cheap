import os
import unittest

try:
    from PyQt6 import QtWidgets
except ImportError:
    QtWidgets = None

from src.ui.settings import SettingsManager, SettingsWindow


class SettingsWindowTests(unittest.TestCase):
    def setUp(self):
        if QtWidgets is None:
            self.skipTest("PyQt6 not installed")
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_load_and_save(self):
        manager = SettingsManager(path="config.json")  # uses existing config
        win = SettingsWindow(manager)
        # Toggle overlay and save
        win.show_overlay.setChecked(False)
        win._save()
        data = manager.load()
        self.assertFalse(data.get("overlay", {}).get("enabled"))


if __name__ == "__main__":
    unittest.main()
