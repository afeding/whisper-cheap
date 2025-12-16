import json
import tempfile
import unittest
from pathlib import Path

from src.ui.settings import SettingsManager


class SettingsManagerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self.tempdir.name) / "config.json"
        # seed config
        self.path.write_text(json.dumps({"post_processing": {"enabled": False}}, indent=2), encoding="utf-8")
        self.sm = SettingsManager(self.path)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_update_post_processing(self):
        updated = self.sm.update_post_processing(
            enabled=True, api_key="k", model="m", prompt_template="Hi ${output}"
        )
        pp = updated["post_processing"]
        self.assertTrue(pp["enabled"])
        self.assertEqual(pp["openrouter_api_key"], "k")
        self.assertEqual(pp["model"], "m")
        self.assertEqual(pp["prompt_template"], "Hi ${output}")


if __name__ == "__main__":
    unittest.main()
