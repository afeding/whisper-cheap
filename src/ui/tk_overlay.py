"""
Overlay simple con tkinter (fallback cuando Win32/PyQt6 fallan).
"""
import tkinter as tk
from tkinter import font as tkfont
import threading
import time


class TkOverlay:
    """Barra de estado simple usando tkinter (built-in, sin deps adicionales)."""

    def __init__(self):
        self.root = None
        self.label = None
        self._thread = None
        self._ready = threading.Event()

    def start(self):
        """Inicializa el overlay en un thread separado."""
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            # Esperar hasta que la ventana esté lista (máx 2s)
            if not self._ready.wait(timeout=2.0):
                raise RuntimeError("TkOverlay no pudo inicializarse en 2s")

    def _run(self):
        """Event loop de tkinter (corre en thread separado)."""
        try:
            self.root = tk.Tk()
            self.root.overrideredirect(True)  # Sin bordes
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', 0.9)

            # Posicionar en bottom-center
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            bar_w, bar_h = 300, 50
            x = (screen_w - bar_w) // 2
            y = screen_h - bar_h - 80
            self.root.geometry(f"{bar_w}x{bar_h}+{x}+{y}")

            # Label con texto
            self.label = tk.Label(
                self.root,
                text="",
                bg="#1e1e1e",
                fg="white",
                font=tkfont.Font(size=14, weight="bold")
            )
            self.label.pack(expand=True, fill=tk.BOTH)

            self.root.withdraw()  # Ocultar inicialmente
            self._ready.set()  # Señalar que está listo

            self.root.mainloop()
        except Exception as e:
            print(f"[tk_overlay] Error en _run(): {e}")
            self._ready.set()  # Evitar deadlock

    def show(self, text: str):
        """Muestra el overlay con el texto especificado."""
        if self.root:
            self.root.after(0, lambda: self._show_impl(text))

    def _show_impl(self, text: str):
        """Implementación interna de show (corre en thread de tkinter)."""
        self.label.config(text=text)
        self.root.deiconify()

    def hide(self):
        """Oculta el overlay."""
        if self.root:
            self.root.after(0, self.root.withdraw)

    def destroy(self):
        """Destruye el overlay."""
        if self.root:
            self.root.after(0, self.root.destroy)
