import unittest

from src.utils.clipboard import ClipboardManager
from src.utils.paste import (
    ClipboardPolicy,
    PasteMethod,
    paste_text,
)


class FakeClipboardBackend:
    def __init__(self):
        self.value = ""

    def copy(self, text):
        self.value = text

    def paste(self):
        return self.value


class FakeSender:
    def __init__(self):
        self.calls = []

    def __call__(self, method):
        self.calls.append(method)


class FakeKeyboard:
    def __init__(self):
        self.written = ""

    def write(self, text):
        self.written += text


class PasteClipboardTests(unittest.TestCase):
    def setUp(self):
        self.fake_backend = FakeClipboardBackend()
        self.clip = ClipboardManager(self.fake_backend)
        self.sender = FakeSender()
        self.keyboard = FakeKeyboard()

    def test_dont_modify_restores_clipboard(self):
        self.fake_backend.copy("original")
        paste_text(
            "new text",
            method=PasteMethod.CTRL_V,
            policy=ClipboardPolicy.DONT_MODIFY,
            clipboard=self.clip,
            send_key_combo=self.sender,
            keyboard_module=self.keyboard,
            delay_seconds=0,
        )
        self.assertEqual(self.fake_backend.paste(), "original")
        self.assertIn(PasteMethod.CTRL_V, self.sender.calls)

    def test_copy_to_clipboard_keeps_new_content(self):
        self.fake_backend.copy("original")
        paste_text(
            "keep",
            method=PasteMethod.SHIFT_INSERT,
            policy=ClipboardPolicy.COPY_TO_CLIPBOARD,
            clipboard=self.clip,
            send_key_combo=self.sender,
            keyboard_module=self.keyboard,
            delay_seconds=0,
        )
        self.assertEqual(self.fake_backend.paste(), "keep")
        self.assertIn(PasteMethod.SHIFT_INSERT, self.sender.calls)

    def test_direct_method_uses_keyboard_write(self):
        paste_text(
            "typed",
            method=PasteMethod.DIRECT,
            policy=ClipboardPolicy.COPY_TO_CLIPBOARD,
            clipboard=self.clip,
            send_key_combo=self.sender,
            keyboard_module=self.keyboard,
            delay_seconds=0,
        )
        self.assertEqual(self.keyboard.written, "typed")

    def test_none_method_does_nothing(self):
        self.fake_backend.copy("orig")
        paste_text(
            "text",
            method=PasteMethod.NONE,
            policy=ClipboardPolicy.DONT_MODIFY,
            clipboard=self.clip,
            send_key_combo=self.sender,
            keyboard_module=self.keyboard,
            delay_seconds=0,
        )
        self.assertEqual(self.fake_backend.paste(), "orig")
        self.assertEqual(self.sender.calls, [])


if __name__ == "__main__":
    unittest.main()
