"""
Lightweight recording window using CustomTkinter/Tk as a fallback when PyQt overlay is unavailable.

Shows a small, always-on-top bar at bottom/top with status text and an RMS level bar.
Runs its own Tk loop in a background thread; state updates are queued to avoid cross-thread calls.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Optional

try:
    import customtkinter as ctk
except ImportError:  # pragma: no cover - optional
    ctk = None

try:
    import tkinter as tk
except ImportError:  # pragma: no cover - optional
    tk = None


@dataclass
class _Msg:
    kind: str
    value: object | None = None


class MiniRecorderWindow:
    def __init__(self, position: str = "bottom", opacity: float = 0.9) -> None:
        if tk is None:
            raise RuntimeError("Tkinter no disponible para ventana de grabacion")
        self.position = position
        self.opacity = opacity
        self._q: queue.SimpleQueue[_Msg] = queue.SimpleQueue()
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._started = threading.Event()

    def _start_thread(self):
        if self._thread and self._thread.is_alive():
            return
        self._running.set()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        # Wait a short time so the UI is ready to receive messages.
        self._started.wait(timeout=1.0)

    def _loop(self):
        root = None
        use_ctk = ctk is not None
        if use_ctk:
            try:
                ctk.set_appearance_mode("dark")
                root = ctk.CTk()
            except Exception:
                use_ctk = False
        if root is None:
            root = tk.Tk()
        root.withdraw()
        root.overrideredirect(True)
        try:
            root.attributes("-topmost", True)
            root.attributes("-alpha", self.opacity)
        except Exception:
            pass

        width, height = 380, 90
        margin = 24

        def place():
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            x = int((sw - width) / 2)
            y = margin if self.position == "top" else sh - height - margin
            root.geometry(f"{width}x{height}+{x}+{y}")

        bg = "#111111"
        text_color = "#ffffff"
        accent = "#00ff88"

        container = ctk.CTkFrame(root, fg_color=bg, corner_radius=12) if use_ctk else tk.Frame(root, bg=bg, bd=0, highlightthickness=0)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        LabelCls = ctk.CTkLabel if use_ctk else tk.Label
        self._label = LabelCls(container, text="Grabando...", text_color=text_color if use_ctk else text_color, fg_color="transparent" if use_ctk else bg, font=("JetBrains Mono", 13, "bold") if use_ctk else ("Segoe UI", 11, "bold"))
        self._label.pack(fill="x")

        if use_ctk:
            self._bar = ctk.CTkProgressBar(container, height=10, fg_color="#1f1f1f", progress_color=accent)
            self._bar.pack(fill="x", pady=(12, 0))
            self._bar.set(0)
        else:
            self._bar_canvas = tk.Canvas(container, height=12, bg="#1f1f1f", highlightthickness=0, bd=0)
            self._bar_canvas.pack(fill="x", pady=(12, 0))
            self._bar_rect = self._bar_canvas.create_rectangle(0, 0, 0, 12, fill=accent, outline=accent)

        self._started.set()

        def pump():
            while True:
                try:
                    msg = self._q.get_nowait()
                except Exception:
                    break
                if msg.kind == "state":
                    try:
                        self._label.configure(text=str(msg.value))
                    except Exception:
                        pass
                elif msg.kind == "level":
                    val = float(msg.value) if msg.value is not None else 0.0
                    val = max(0.0, min(val, 1.0))
                    if use_ctk:
                        try:
                            self._bar.set(val)
                        except Exception:
                            pass
                    else:
                        try:
                            total = max(60, int(self._bar_canvas.winfo_width()) or 200)
                            self._bar_canvas.coords(self._bar_rect, 0, 0, int(total * val), 12)
                        except Exception:
                            pass
                elif msg.kind == "visible":
                    try:
                        place()
                        if msg.value:
                            root.deiconify()
                        else:
                            root.withdraw()
                    except Exception:
                        pass
                elif msg.kind == "quit":
                    try:
                        root.destroy()
                    except Exception:
                        pass
                    self._running.clear()
                    return
            if self._running.is_set():
                root.after(50, pump)

        place()
        root.after(50, pump)
        try:
            root.mainloop()
        finally:
            self._running.clear()

    # ---- Public API ----
    def show(self, text: str):
        self._start_thread()
        self._q.put(_Msg("state", text))
        self._q.put(_Msg("visible", True))

    def update_level(self, rms: float):
        if not self._started.is_set():
            return
        self._q.put(_Msg("level", float(rms)))

    def hide(self):
        if not self._started.is_set():
            return
        self._q.put(_Msg("visible", False))

    def stop(self):
        if not self._started.is_set():
            return
        self._q.put(_Msg("quit", None))
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
