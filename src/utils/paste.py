"""
Paste utilities for Whisper Cheap.

Supports:
- Ctrl+V
- Shift+Insert
- Direct keyboard write
- None (no paste)

Clipboard policies:
- dont_modify: guarda y restaura el contenido previo.
- copy_to_clipboard: deja el texto pegado en el portapapeles.

All key-sending operations are injectable for testing and to avoid real key
events in automated runs.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Callable, Optional

try:
    import keyboard  # type: ignore
except ImportError:  # pragma: no cover - optional at runtime
    keyboard = None

try:
    import win32api  # type: ignore
    import win32con  # type: ignore
except ImportError:  # pragma: no cover - optional at runtime
    win32api = None
    win32con = None

from src.utils.clipboard import ClipboardManager


class PasteMethod(str, Enum):
    NONE = "none"
    CTRL_V = "ctrl_v"
    SHIFT_INSERT = "shift_insert"
    DIRECT = "direct"


class ClipboardPolicy(str, Enum):
    DONT_MODIFY = "dont_modify"
    COPY_TO_CLIPBOARD = "copy_to_clipboard"


def _send_ctrl_v():
    if win32api is None or win32con is None:
        raise RuntimeError("pywin32 is required for Ctrl+V paste")
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord("V"), 0, 0, 0)
    win32api.keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)


def _send_shift_insert():
    if win32api is None or win32con is None:
        raise RuntimeError("pywin32 is required for Shift+Insert paste")
    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
    win32api.keybd_event(win32con.VK_INSERT, 0, 0, 0)
    win32api.keybd_event(win32con.VK_INSERT, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)


def paste_text(
    text: str,
    method: PasteMethod = PasteMethod.CTRL_V,
    policy: ClipboardPolicy = ClipboardPolicy.DONT_MODIFY,
    clipboard: Optional[ClipboardManager] = None,
    delay_seconds: float = 0.05,
    send_key_combo: Optional[Callable[[PasteMethod], None]] = None,
    keyboard_module=None,
) -> None:
    """
    Perform paste according to method and clipboard policy.
    send_key_combo: optional callable receiving the PasteMethod for Ctrl+V / Shift+Insert.
    keyboard_module: optional keyboard-like object with .write for direct mode.
    """
    cb = clipboard or ClipboardManager()
    sender = send_key_combo
    if sender is None:
        sender = _default_sender
    kb = keyboard_module or keyboard

    if policy == ClipboardPolicy.DONT_MODIFY:
        cb.save_current()
        cb.set_text(text)
        time.sleep(delay_seconds)
        _perform_paste_action(text, method, sender, kb, delay_seconds)
        time.sleep(delay_seconds)
        cb.restore()
    elif policy == ClipboardPolicy.COPY_TO_CLIPBOARD:
        cb.set_text(text)
        time.sleep(delay_seconds)
        _perform_paste_action(text, method, sender, kb, delay_seconds)
    else:
        # Unknown policy -> do nothing
        return


def _default_sender(method: PasteMethod):
    if method == PasteMethod.CTRL_V:
        _send_ctrl_v()
    elif method == PasteMethod.SHIFT_INSERT:
        _send_shift_insert()


def _perform_paste_action(
    text: str,
    method: PasteMethod,
    sender: Callable[[PasteMethod], None],
    kb,
    delay_seconds: float,
):
    if method == PasteMethod.NONE:
        return
    if method == PasteMethod.DIRECT:
        if kb is None:
            raise RuntimeError("keyboard module not available for direct paste")
        kb.write(text)
        return
    sender(method)
    time.sleep(delay_seconds)
