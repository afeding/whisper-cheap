"""
Simple dark-themed settings window (Tk) without external dependencies.

Shows only the core fields a user typically edits. Closing the window does not
exit the app; it just hides the settings.
"""

from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from typing import Any, Dict


FIELDS = [
    ("Hotkey", "hotkey", "ctrl+shift+space"),
    ("Mode (ptt/toggle)", "activation_mode", "toggle"),
    ("Microphone device id (empty=default)", "device_id", ""),
    ("Chunk size", "chunk_size", "4096"),
    ("Paste method (ctrl_v/shift_insert/direct/none)", "paste_method", "ctrl_v"),
    ("Overlay enabled (true/false)", "overlay_enabled", "true"),
    ("Overlay position (top/bottom)", "overlay_position", "bottom"),
]


class SimpleSettingsWindow:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.data: Dict[str, Any] = self._load()
        self.vars: Dict[str, tk.Variable] = {}
        self.root = tk.Tk()
        self.root.title("Whisper Cheap - Ajustes")
        self.root.geometry("520x520")
        self.root.configure(bg="#1f2126")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self._build()
        self._populate()

    # ----------------- build -----------------
    def _build(self):
        title = tk.Label(self.root, text="Settings", fg="#f5f5f7", bg="#1f2126", font=("Segoe UI", 14, "bold"))
        title.pack(pady=(14, 8))

        frame = tk.Frame(self.root, bg="#1f2126")
        frame.pack(fill="both", expand=True, padx=16, pady=8)

        for label, key, default in FIELDS:
            row = tk.Frame(frame, bg="#1f2126")
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, fg="#c7c9d1", bg="#1f2126", anchor="w", width=32).pack(side="left")
            var = tk.StringVar(value=default)
            entry = tk.Entry(row, textvariable=var, bg="#0f1116", fg="#e4e6eb", insertbackground="#e4e6eb", relief="flat")
            entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(8, 0))
            self.vars[key] = var

        btn = tk.Button(self.root, text="Guardar", bg="#e16dbf", fg="#0f1116", relief="flat", command=self._save)
        btn.pack(pady=12, ipadx=10, ipady=6)

    # ----------------- data -----------------
    def _load(self) -> Dict[str, Any]:
        try:
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _populate(self):
        d = self.data
        mode = d.get("mode", {})
        audio = d.get("audio", {})
        clip = d.get("clipboard", {})
        overlay = d.get("overlay", {})
        self.vars["hotkey"].set(d.get("hotkey", "ctrl+shift+space"))
        self.vars["activation_mode"].set(mode.get("activation_mode", "toggle"))
        dev = audio.get("device_id")
        self.vars["device_id"].set("" if dev is None else str(dev))
        self.vars["chunk_size"].set(str(audio.get("chunk_size", 4096)))
        self.vars["paste_method"].set(clip.get("paste_method", "ctrl_v"))
        self.vars["overlay_enabled"].set("true" if overlay.get("enabled", True) else "false")
        self.vars["overlay_position"].set(overlay.get("position", "bottom"))

    def _save(self):
        d = self.data
        d["hotkey"] = self.vars["hotkey"].get().strip() or "ctrl+shift+space"
        d.setdefault("mode", {})["activation_mode"] = self.vars["activation_mode"].get().strip() or "toggle"

        audio = d.setdefault("audio", {})
        dev = self.vars["device_id"].get().strip()
        audio["device_id"] = None if dev == "" else int(dev) if dev.isdigit() else dev
        try:
            audio["chunk_size"] = int(self.vars["chunk_size"].get())
        except Exception:
            audio["chunk_size"] = 4096
        audio.setdefault("sample_rate", 16000)
        audio.setdefault("channels", 1)
        audio.setdefault("vad_threshold", 0.5)
        audio.setdefault("use_vad", False)
        audio.setdefault("mute_while_recording", False)

        clip = d.setdefault("clipboard", {})
        clip["paste_method"] = self.vars["paste_method"].get().strip() or "ctrl_v"
        clip.setdefault("policy", "dont_modify")

        overlay = d.setdefault("overlay", {})
        overlay["enabled"] = self.vars["overlay_enabled"].get().strip().lower() == "true"
        overlay["position"] = self.vars["overlay_position"].get().strip() or "bottom"
        overlay.setdefault("opacity", 0.85)

        self.config_path.write_text(json.dumps(d, indent=2), encoding="utf-8")
        self.root.destroy()

    def show(self):
        self.root.mainloop()


def open_simple_settings(config_path: Path):
    # Run in a background thread so the main app keeps running
    def _run():
        win = SimpleSettingsWindow(config_path)
        win.show()

    threading.Thread(target=_run, daemon=True).start()
