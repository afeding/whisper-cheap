"""
Clipboard management utilities.

Exposes a small manager that can be safely mocked in tests.
"""

from __future__ import annotations

from typing import Optional

try:
    import pyperclip
except ImportError:  # pragma: no cover - handled at runtime
    pyperclip = None


class ClipboardManager:
    def __init__(self, backend=None) -> None:
        self.backend = backend or pyperclip
        self._saved: Optional[str] = None

    def save_current(self):
        if self.backend is None:
            raise RuntimeError("pyperclip is not available")
        try:
            self._saved = self.backend.paste()
        except Exception:
            self._saved = None

    def set_text(self, text: str):
        if self.backend is None:
            raise RuntimeError("pyperclip is not available")
        self.backend.copy(text)

    def restore(self):
        if self._saved is None:
            return
        if self.backend is None:
            raise RuntimeError("pyperclip is not available")
        self.backend.copy(self._saved)
        self._saved = None
