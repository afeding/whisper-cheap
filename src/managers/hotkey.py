"""
Global hotkey management for Whisper Cheap.

Uses low-level keyboard hooks for reliable press/release detection.
The standard keyboard.add_hotkey with trigger_on_release=True is unreliable
for key combinations, so we track key states manually.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable, Dict, Optional, Set

try:
    from pynput.keyboard import Key, KeyCode, Listener
    PYNPUT_AVAILABLE = True
except ImportError:  # pragma: no cover
    PYNPUT_AVAILABLE = False
    Key = None
    KeyCode = None
    Listener = None

logger = logging.getLogger(__name__)


class HotkeyManager:
    """
    Registers global hotkeys with reliable press/release callbacks.

    Uses low-level hooks to track key states manually, which is more
    reliable than keyboard's built-in trigger_on_release for combos.
    """

    # Minimum time combo must be held before triggering (ms)
    COMBO_HOLD_TIME_MS = 50

    # How often to check for stale keys (every N events)
    STALE_CHECK_INTERVAL = 50

    def __init__(self, keyboard_module=None) -> None:
        # keyboard_module param ignored (kept for test compatibility)
        if not PYNPUT_AVAILABLE:
            raise RuntimeError("pynput library is not installed")

        self._listener: Optional[Listener] = None
        self._bindings: Dict[str, dict] = {}
        self._lock = threading.Lock()

        # Track currently pressed keys (normalized names)
        self._pressed_keys: Set[str] = set()
        self._event_counter = 0

    def _key_to_string(self, key) -> str:
        """Convert pynput Key/KeyCode to normalized string."""
        if key is None:
            return ""

        # Special keys (Key enum)
        if isinstance(key, Key):
            KEY_MAP = {
                Key.ctrl_l: "ctrl", Key.ctrl_r: "ctrl",
                Key.shift_l: "shift", Key.shift_r: "shift",
                Key.alt_l: "alt", Key.alt_r: "alt",
                Key.alt_gr: "alt",
                Key.cmd: "windows", Key.cmd_l: "windows", Key.cmd_r: "windows",
                Key.space: "space",
                Key.enter: "enter", Key.tab: "tab", Key.esc: "esc",
                Key.backspace: "backspace", Key.delete: "delete",
                Key.up: "up", Key.down: "down", Key.left: "left", Key.right: "right",
                Key.home: "home", Key.end: "end",
                Key.page_up: "page_up", Key.page_down: "page_down",
                Key.f1: "f1", Key.f2: "f2", Key.f3: "f3", Key.f4: "f4",
                Key.f5: "f5", Key.f6: "f6", Key.f7: "f7", Key.f8: "f8",
                Key.f9: "f9", Key.f10: "f10", Key.f11: "f11", Key.f12: "f12",
            }
            return KEY_MAP.get(key, str(key).lower().replace("key.", ""))

        # Character keys (KeyCode)
        if hasattr(key, 'char') and key.char:
            return key.char.lower()

        # Fallback
        return str(key).lower()

    def _normalize_key(self, key: str) -> str:
        """Normalize key names from config combo strings (e.g., 'ctrl+shift+space')."""
        key = key.lower().strip()
        # Handle common aliases
        aliases = {
            "control": "ctrl",
            "ctl": "ctrl",
            "alt": "alt",
            "menu": "alt",
            "shift": "shift",
            "win": "windows",
            "super": "windows",
            "cmd": "windows",
            "space": "space",
            "spacebar": "space",
            " ": "space",
        }
        return aliases.get(key, key)

    def _parse_combo(self, combo: str) -> Set[str]:
        """Parse a hotkey combo string into a set of normalized key names."""
        parts = combo.lower().replace(" ", "").split("+")
        return {self._normalize_key(p) for p in parts if p}


    def _on_press(self, key) -> bool:
        """Handle key press events from pynput."""
        try:
            key_name = self._key_to_string(key)
            if not key_name:
                return True

            logger.debug(f"[hotkey] Key press: {key} -> '{key_name}'")

            with self._lock:
                if key_name in self._pressed_keys:
                    return True  # Key repeat, ignore

                self._pressed_keys.add(key_name)
                suppress = self._check_combos_on_change()

            return not suppress  # False = suppress, True = allow

        except Exception as e:
            logger.error(f"[hotkey] Error in on_press: {e}")
            return True

    def _on_release(self, key) -> bool:
        """Handle key release events from pynput."""
        try:
            key_name = self._key_to_string(key)
            if not key_name:
                return True

            logger.debug(f"[hotkey] Key release: {key} -> '{key_name}'")

            with self._lock:
                if key_name not in self._pressed_keys:
                    return True  # Release without press, ignore

                self._pressed_keys.discard(key_name)
                suppress = self._check_combos_on_change()

            return not suppress

        except Exception as e:
            logger.error(f"[hotkey] Error in on_release: {e}")
            return True

    def _check_combos_on_change(self) -> bool:
        """
        Check all combos after key state change.
        Must be called with self._lock held.
        Returns True if any combo with suppress=True is active.
        """
        should_suppress = False

        for combo, binding in self._bindings.items():
            required_keys = binding["keys"]
            was_active = binding["active"]
            press_fired = binding.get("press_fired", False)

            is_active = required_keys.issubset(self._pressed_keys)

            if is_active and not was_active:
                # Combo activated
                binding["active"] = True
                binding["press_fired"] = False

                # Cancel old timer
                old_timer = binding.get("timer")
                if old_timer:
                    old_timer.cancel()

                # Start hold timer
                callback = binding.get("on_press")
                if callback:
                    def fire_press(b=binding, c=callback, combo_name=combo):
                        with self._lock:
                            if b.get("active") and not b.get("press_fired"):
                                b["press_fired"] = True
                                logger.info(f"[hotkey] Combo '{combo_name}' PRESS")
                                threading.Thread(
                                    target=self._safe_callback,
                                    args=(c, "press", combo_name),
                                    daemon=True
                                ).start()

                    timer = threading.Timer(self.COMBO_HOLD_TIME_MS / 1000.0, fire_press)
                    timer.daemon = True
                    timer.start()
                    binding["timer"] = timer
                    logger.debug(f"[hotkey] Combo '{combo}' activated")

            elif not is_active and was_active:
                # Combo deactivated
                binding["active"] = False

                # Cancel timer
                timer = binding.get("timer")
                if timer:
                    timer.cancel()
                    binding["timer"] = None

                # Fire release if press was fired
                if press_fired:
                    callback = binding.get("on_release")
                    if callback:
                        logger.info(f"[hotkey] Combo '{combo}' RELEASE")
                        threading.Thread(
                            target=self._safe_callback,
                            args=(callback, "release", combo),
                            daemon=True
                        ).start()
                else:
                    logger.debug(f"[hotkey] Combo '{combo}' released before hold time")

                binding["press_fired"] = False

            # Check if this combo requires suppression
            if is_active and binding.get("suppress", False):
                should_suppress = True

        return should_suppress

    def _safe_callback(self, callback: Callable, event_type: str, combo: str) -> None:
        """Execute callback safely with error handling."""
        try:
            callback()
        except Exception as e:
            logger.exception(f"[hotkey] Error in {event_type} callback for '{combo}': {e}")

    def _ensure_hook(self) -> None:
        """Install the global keyboard listener if not already installed."""
        if self._listener is not None:
            return

        if not PYNPUT_AVAILABLE:
            raise RuntimeError("pynput library is not installed")

        try:
            self._listener = Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self._listener.start()
            logger.info("[hotkey] pynput keyboard listener started")
        except Exception as e:
            logger.error(f"[hotkey] Failed to start listener: {e}")
            raise

    def register_hotkey(
        self,
        combo: str,
        on_press_callback: Optional[Callable[[], None]] = None,
        on_release_callback: Optional[Callable[[], None]] = None,
        suppress: bool = False,  # Suppress hotkey propagation to OS
    ) -> None:
        """
        Register a hotkey with press and/or release callbacks.

        Args:
            combo: Key combination (e.g., "ctrl+shift+space")
            on_press_callback: Called when all keys in combo are pressed
            on_release_callback: Called when any key in combo is released
            suppress: Suppress hotkey propagation to OS (pynput backend only)
        """
        if not PYNPUT_AVAILABLE:
            raise RuntimeError("pynput library is not installed")

        keys = self._parse_combo(combo)
        if not keys:
            raise ValueError(f"Invalid hotkey combo: {combo}")

        with self._lock:
            self._bindings[combo] = {
                "keys": keys,
                "on_press": on_press_callback,
                "on_release": on_release_callback,
                "active": False,
                "suppress": suppress,
            }
            logger.info(f"[hotkey] Registered: '{combo}' -> {keys}")

        self._ensure_hook()

    def unregister_hotkey(self, combo: str) -> None:
        """Unregister a hotkey."""
        with self._lock:
            if combo in self._bindings:
                # Cancel any pending timer
                timer = self._bindings[combo].get("timer")
                if timer:
                    timer.cancel()
                del self._bindings[combo]
                logger.debug(f"[hotkey] Unregistered: '{combo}'")

    def update_hotkey(
        self,
        old_combo: str,
        new_combo: str,
        on_press_callback: Optional[Callable[[], None]] = None,
        on_release_callback: Optional[Callable[[], None]] = None,
    ) -> bool:
        """
        Update an existing hotkey to a new combination.

        If callbacks are None, keeps the existing callbacks.
        Returns True if successful, False if old_combo wasn't registered.
        """
        with self._lock:
            if old_combo not in self._bindings:
                logger.warning(f"[hotkey] Cannot update: '{old_combo}' not registered")
                return False

            # Get existing callbacks if new ones not provided
            old_binding = self._bindings[old_combo]
            press_cb = on_press_callback or old_binding.get("on_press")
            release_cb = on_release_callback or old_binding.get("on_release")

            # Cancel any pending timer on old binding
            timer = old_binding.get("timer")
            if timer:
                timer.cancel()

            # Remove old binding
            del self._bindings[old_combo]

        # Register new binding (outside lock to avoid deadlock with _ensure_hook)
        self.register_hotkey(new_combo, press_cb, release_cb)
        logger.info(f"[hotkey] Updated: '{old_combo}' -> '{new_combo}'")
        return True

    def get_registered_combos(self) -> list:
        """Return list of currently registered hotkey combos."""
        with self._lock:
            return list(self._bindings.keys())

    def unregister_all(self) -> None:
        """Unregister all hotkeys and stop the listener."""
        logger.debug("[hotkey] unregister_all called")

        # Cancel timers and clear bindings
        with self._lock:
            for binding in self._bindings.values():
                timer = binding.get("timer")
                if timer:
                    timer.cancel()
            self._bindings.clear()
            self._pressed_keys.clear()
            logger.debug("[hotkey] Bindings cleared")

        # Stop listener
        if self._listener is not None:
            try:
                import time
                time.sleep(0.05)
                self._listener.stop()
                self._listener = None
                logger.info("[hotkey] Listener stopped")
            except Exception as e:
                logger.error(f"[hotkey] Error stopping listener: {e}")
                self._listener = None

    # --- Testing helpers ---
    def simulate_press(self, combo: str) -> None:
        """Simulate pressing a hotkey (for tests)."""
        with self._lock:
            binding = self._bindings.get(combo)
            if binding and binding.get("on_press"):
                binding["active"] = True
                callback = binding["on_press"]
        if callback:
            self._safe_callback(callback, "press", combo)

    def simulate_release(self, combo: str) -> None:
        """Simulate releasing a hotkey (for tests)."""
        with self._lock:
            binding = self._bindings.get(combo)
            if binding and binding.get("on_release"):
                binding["active"] = False
                callback = binding["on_release"]
        if callback:
            self._safe_callback(callback, "release", combo)
