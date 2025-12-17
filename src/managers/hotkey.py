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
    import keyboard as kb  # type: ignore
except ImportError:  # pragma: no cover
    kb = None

logger = logging.getLogger(__name__)


class HotkeyManager:
    """
    Registers global hotkeys with reliable press/release callbacks.

    Uses low-level hooks to track key states manually, which is more
    reliable than keyboard's built-in trigger_on_release for combos.
    """

    # Minimum time combo must be held before triggering (ms)
    COMBO_HOLD_TIME_MS = 50

    def __init__(self, keyboard_module=None) -> None:
        self._kb = keyboard_module or kb
        self._bindings: Dict[str, dict] = {}
        self._hook_installed = False
        self._lock = threading.Lock()

        # Track currently pressed keys (normalized names)
        self._pressed_keys: Set[str] = set()

    def _normalize_key(self, key: str) -> str:
        """Normalize key names for consistent comparison."""
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

    def _on_key_event(self, event) -> None:
        """
        Handle all keyboard events.

        This is called for EVERY key press/release in the system.
        We track which keys are pressed and fire callbacks when combos match.
        """
        try:
            raw_name = event.name
            key_name = self._normalize_key(raw_name)
            is_down = event.event_type == "down"

            # Debug: log key events for registered combo keys
            with self._lock:
                all_required_keys = set()
                for binding in self._bindings.values():
                    all_required_keys.update(binding["keys"])

            if key_name in all_required_keys or raw_name.lower() in ("ctrl", "shift", "space", "control"):
                logger.debug(f"[hotkey] Key: '{raw_name}' -> '{key_name}' ({event.event_type})")

            with self._lock:
                was_pressed = key_name in self._pressed_keys

                if is_down:
                    if was_pressed:
                        # Key repeat, ignore
                        return
                    self._pressed_keys.add(key_name)
                else:
                    if not was_pressed:
                        # Release without press, ignore
                        return
                    self._pressed_keys.discard(key_name)

                # Check all registered bindings
                for combo, binding in self._bindings.items():
                    required_keys = binding["keys"]
                    was_active = binding["active"]
                    press_fired = binding.get("press_fired", False)

                    # Check if all required keys are now pressed
                    is_active = required_keys.issubset(self._pressed_keys)

                    if is_active and not was_active:
                        # Combo just activated (all keys pressed)
                        binding["active"] = True
                        binding["press_fired"] = False

                        # Cancel any pending timer
                        old_timer = binding.get("timer")
                        if old_timer:
                            old_timer.cancel()

                        # Start timer to fire press after hold time
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
                            logger.debug(f"[hotkey] Combo '{combo}' activated, timer started ({self.COMBO_HOLD_TIME_MS}ms)")

                    elif not is_active and was_active:
                        # Combo just deactivated (at least one key released)
                        binding["active"] = False

                        # Cancel pending timer if press not fired yet
                        timer = binding.get("timer")
                        if timer:
                            timer.cancel()
                            binding["timer"] = None

                        # Only fire release if press was fired
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
                            logger.debug(f"[hotkey] Combo '{combo}' released before hold time, ignored")

                        binding["press_fired"] = False

        except Exception as e:
            logger.error(f"[hotkey] Error in key event handler: {e}")

    def _safe_callback(self, callback: Callable, event_type: str, combo: str) -> None:
        """Execute callback safely with error handling."""
        try:
            callback()
        except Exception as e:
            logger.exception(f"[hotkey] Error in {event_type} callback for '{combo}': {e}")

    def _ensure_hook(self) -> None:
        """Install the global keyboard hook if not already installed."""
        if self._hook_installed or self._kb is None:
            return

        try:
            self._kb.hook(self._on_key_event)
            self._hook_installed = True
            logger.info("[hotkey] Global keyboard hook installed successfully")
        except Exception as e:
            logger.error(f"[hotkey] Failed to install keyboard hook: {e}")
            raise

    def register_hotkey(
        self,
        combo: str,
        on_press_callback: Optional[Callable[[], None]] = None,
        on_release_callback: Optional[Callable[[], None]] = None,
        suppress: bool = False,  # Not used in hook-based approach, kept for API compat
    ) -> None:
        """
        Register a hotkey with press and/or release callbacks.

        Args:
            combo: Key combination (e.g., "ctrl+shift+space")
            on_press_callback: Called when all keys in combo are pressed
            on_release_callback: Called when any key in combo is released
            suppress: Ignored (kept for API compatibility)
        """
        if self._kb is None:
            raise RuntimeError("keyboard library is not installed")

        keys = self._parse_combo(combo)
        if not keys:
            raise ValueError(f"Invalid hotkey combo: {combo}")

        with self._lock:
            self._bindings[combo] = {
                "keys": keys,
                "on_press": on_press_callback,
                "on_release": on_release_callback,
                "active": False,
            }
            logger.info(f"[hotkey] Registered: '{combo}' -> {keys}")

        self._ensure_hook()

    def unregister_hotkey(self, combo: str) -> None:
        """Unregister a hotkey."""
        with self._lock:
            if combo in self._bindings:
                del self._bindings[combo]
                logger.debug(f"[hotkey] Unregistered: '{combo}'")

    def unregister_all(self) -> None:
        """Unregister all hotkeys and remove the hook."""
        logger.debug("[hotkey] unregister_all called")

        # Cancel all pending timers and clear bindings
        with self._lock:
            for binding in self._bindings.values():
                timer = binding.get("timer")
                if timer:
                    timer.cancel()
            self._bindings.clear()
            self._pressed_keys.clear()
            logger.debug("[hotkey] Bindings and timers cleared")

        # Remove keyboard hook (may block briefly)
        if self._hook_installed and self._kb is not None:
            try:
                # Give pending callbacks time to complete
                import time
                time.sleep(0.05)

                self._kb.unhook_all()
                self._hook_installed = False
                logger.info("[hotkey] All hotkeys unregistered, hook removed")
            except Exception as e:
                logger.error(f"[hotkey] Error removing hook: {e}")
                # Force mark as uninstalled even on error
                self._hook_installed = False

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
