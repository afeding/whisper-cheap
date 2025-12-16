"""
Global hotkey management for Whisper Cheap.

Wraps the `keyboard` library to register press/release callbacks for PTT or
toggle bindings. Includes a simulation path for tests without OS hooks.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

try:
    import keyboard as kb  # type: ignore
except ImportError:  # pragma: no cover - handled via injection in tests
    kb = None


HotkeyHandle = Tuple[str, List[Tuple[int, bool]]]


class HotkeyManager:
    """
    Registers global hotkeys with press/release callbacks.
    """

    def __init__(self, keyboard_module=None) -> None:
        # keyboard_module enables injection of a fake implementation in tests.
        self._kb = keyboard_module or kb
        self._bindings: Dict[str, HotkeyHandle] = {}

    def register_hotkey(
        self,
        combo: str,
        on_press_callback: Optional[Callable[[], None]] = None,
        on_release_callback: Optional[Callable[[], None]] = None,
        suppress: bool = False,
    ) -> None:
        if self._kb is None:
            raise RuntimeError("keyboard library is not installed")
        handles: List[int] = []
        if on_press_callback:
            handle_id = self._kb.add_hotkey(
                combo, on_press_callback, suppress=suppress, trigger_on_release=False
            )
            handles.append((handle_id, False))
        if on_release_callback:
            handle_id = self._kb.add_hotkey(
                combo, on_release_callback, suppress=suppress, trigger_on_release=True
            )
            handles.append((handle_id, True))
        self._bindings[combo] = (combo, handles)

    def unregister_hotkey(self, combo: str) -> None:
        if combo not in self._bindings:
            return
        if self._kb is not None:
            _, handles = self._bindings[combo]
            for h, _ in handles:
                try:
                    self._kb.remove_hotkey(h)
                except Exception:
                    pass
        self._bindings.pop(combo, None)

    def unregister_all(self) -> None:
        for combo in list(self._bindings.keys()):
            self.unregister_hotkey(combo)

    # --- Testing helpers (no OS hooks needed) ---
    def simulate_press(self, combo: str) -> None:
        handle = self._bindings.get(combo)
        if not handle:
            return
        _, handles = handle
        if self._kb and hasattr(self._kb, "trigger_hotkey"):
            for h, is_release in handles:
                if is_release:
                    continue
                try:
                    self._kb.trigger_hotkey(h, suppress=False)
                except Exception:
                    pass

    def simulate_release(self, combo: str) -> None:
        handle = self._bindings.get(combo)
        if not handle:
            return
        _, handles = handle
        if self._kb and hasattr(self._kb, "trigger_hotkey"):
            for h, is_release in handles:
                if not is_release:
                    continue
                try:
                    self._kb.trigger_hotkey(h, suppress=False)
                except Exception:
                    pass
