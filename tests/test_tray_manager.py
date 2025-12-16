import unittest

from src.ui.tray import TrayManager


class FakeIcon:
    def __init__(self, name, icon, title, menu):
        self.name = name
        self.icon = icon
        self.title = title
        self.menu = menu
        self.stopped = False

    def run_detached(self):
        return None

    def stop(self):
        self.stopped = True


class FakeMenuItem:
    def __init__(self, title, action):
        self.title = title
        self.action = action


class FakeMenu:
    def __init__(self, *items):
        self.items = items


class FakePystray:
    def __init__(self):
        self.Icon = lambda name, icon, title, menu: FakeIcon(name, icon, title, menu)
        self.MenuItem = FakeMenuItem
        self.Menu = FakeMenu


class TrayManagerTests(unittest.TestCase):
    def test_set_state_updates_icon(self):
        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        fake = FakePystray()
        tm = TrayManager(pystray_module=fake)
        tm.start()
        prev_icon = tm._icon.icon
        tm.set_state("recording")
        self.assertIsNotNone(tm._icon)
        self.assertIsNot(prev_icon, tm._icon.icon)
        tm.stop()
        self.assertTrue(tm._icon is None or getattr(tm._icon, "stopped", True))


if __name__ == "__main__":
    unittest.main()
