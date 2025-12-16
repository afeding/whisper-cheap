import unittest

from src.managers.hotkey import HotkeyManager


class FakeKeyboard:
    def __init__(self):
        self._callbacks = {}
        self._next_id = 1

    def add_hotkey(self, combo, callback, suppress=False, trigger_on_release=False):
        hid = self._next_id
        self._next_id += 1
        self._callbacks[hid] = callback
        return hid

    def remove_hotkey(self, hid):
        self._callbacks.pop(hid, None)

    def trigger_hotkey(self, hid, suppress=False):
        cb = self._callbacks.get(hid)
        if cb:
            cb()


class HotkeyManagerTests(unittest.TestCase):
    def test_press_and_release_callbacks(self):
        fake_kb = FakeKeyboard()
        manager = HotkeyManager(keyboard_module=fake_kb)
        events = []

        manager.register_hotkey(
            "ctrl+shift+space", on_press_callback=lambda: events.append("press"), on_release_callback=lambda: events.append("release")
        )
        manager.simulate_press("ctrl+shift+space")
        manager.simulate_release("ctrl+shift+space")

        self.assertIn("press", events)
        self.assertIn("release", events)
        self.assertEqual(len(events), 2)

    def test_unregister(self):
        fake_kb = FakeKeyboard()
        manager = HotkeyManager(keyboard_module=fake_kb)
        events = []
        manager.register_hotkey("ctrl+space", on_press_callback=lambda: events.append("press"))
        manager.unregister_hotkey("ctrl+space")
        manager.simulate_press("ctrl+space")
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
