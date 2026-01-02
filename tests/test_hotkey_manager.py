import unittest
import time
from unittest.mock import Mock, patch

from pynput.keyboard import Key

from src.managers.hotkey import HotkeyManager


class HotkeyManagerTests(unittest.TestCase):
    @patch('src.managers.hotkey.Listener')
    def test_press_and_release_callbacks(self, mock_listener_class):
        """Test that press and release callbacks are fired correctly."""
        events = []

        # Setup mock listener
        mock_listener = Mock()
        mock_listener_class.return_value = mock_listener

        manager = HotkeyManager()
        manager.register_hotkey(
            "ctrl+shift+space",
            on_press_callback=lambda: events.append("press"),
            on_release_callback=lambda: events.append("release")
        )

        # Get the callbacks that were registered
        on_press_callback = mock_listener_class.call_args.kwargs['on_press']
        on_release_callback = mock_listener_class.call_args.kwargs['on_release']

        # Simulate key sequence: press ctrl, shift, space
        on_press_callback(Key.ctrl)
        on_press_callback(Key.shift)
        on_press_callback(Key.space)

        # Wait for hold timer (50ms)
        time.sleep(0.06)

        # Release space
        on_release_callback(Key.space)

        # Verify callbacks were called
        self.assertIn("press", events)
        self.assertIn("release", events)
        self.assertEqual(len(events), 2)

    @patch('src.managers.hotkey.Listener')
    def test_unregister(self, mock_listener_class):
        """Test that unregistered hotkeys don't trigger callbacks."""
        events = []

        mock_listener = Mock()
        mock_listener_class.return_value = mock_listener

        manager = HotkeyManager()
        manager.register_hotkey("ctrl+space", on_press_callback=lambda: events.append("press"))

        on_press_callback = mock_listener_class.call_args.kwargs['on_press']

        # Unregister the hotkey
        manager.unregister_hotkey("ctrl+space")

        # Try to trigger it (simulate_press won't work since binding is gone)
        on_press_callback(Key.ctrl)
        on_press_callback(Key.space)
        time.sleep(0.06)

        # Should not have triggered anything
        self.assertEqual(events, [])

    @patch('src.managers.hotkey.Listener')
    def test_suppress_parameter(self, mock_listener_class):
        """Test that suppress parameter is stored correctly."""
        mock_listener = Mock()
        mock_listener_class.return_value = mock_listener

        manager = HotkeyManager()
        manager.register_hotkey("ctrl+a", suppress=True)

        # Check that binding has suppress flag
        self.assertTrue(manager._bindings["ctrl+a"]["suppress"])


if __name__ == "__main__":
    unittest.main()
