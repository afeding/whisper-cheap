"""
PyQt6 overlay windows for recording and status.

- RecordingOverlay: shows "Recording..." and a level bar (RMS).
- StatusOverlay: shows status text ("Transcribing...", "Formatting...").
Both are frameless, always-on-top, semi-transparent, and placeable top/bottom center.
"""

from __future__ import annotations

import os
import threading
from typing import Optional

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    QtCore = None
    QtGui = None
    QtWidgets = None

_APP_LOCK = threading.Lock()


def ensure_app() -> Optional["QtWidgets.QApplication"]:
    """
    Create (or return) a singleton QApplication so overlays can be instantiated.
    The caller is responsible for driving the event loop via processEvents().
    """
    if QtWidgets is None:
        return None
    with _APP_LOCK:
        app = QtWidgets.QApplication.instance()
        if app is None:
            os.environ.setdefault("QT_QPA_PLATFORM", "windows:darkmode=2" if os.name == "nt" else "")
            app = QtWidgets.QApplication([])
            app.setQuitOnLastWindowClosed(False)
        return app


class _BaseOverlay:
    def __init__(self, text: str, position: str = "bottom", opacity: float = 0.5):
        if QtWidgets is None:
            raise RuntimeError("PyQt6 is required for overlays")
        self.app = ensure_app()
        if self.app is None:
            raise RuntimeError("QApplication not available for overlays")
        self.position = position
        self.opacity = opacity
        self.window = QtWidgets.QWidget()
        self.window.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
        )
        self.window.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.window.setWindowOpacity(opacity)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.label = QtWidgets.QLabel(text)
        font = QtGui.QFont()
        font.setPointSize(21)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")

        self.container = QtWidgets.QFrame()
        self.container.setStyleSheet(
            """
            background-color: rgba(0, 0, 0, 160);
            border-radius: 999px;
            """
        )
        self.container_layout = QtWidgets.QVBoxLayout()
        self.container_layout.setContentsMargins(10, 8, 10, 8)
        self.container_layout.addWidget(self.label)
        self.container.setLayout(self.container_layout)

        self.layout.addWidget(self.container)
        self.window.setLayout(self.layout)

    def _run_on_ui(self, fn):
        if QtCore is None:
            return fn()
        if QtCore.QThread.currentThread() == self.window.thread():
            return fn()
        QtCore.QTimer.singleShot(0, fn)

    def _place(self):
        def _place_inner():
            screen = QtWidgets.QApplication.primaryScreen()
            if not screen:
                return
            geo = screen.geometry()
            size = self.window.sizeHint()
            x = geo.x() + (geo.width() - size.width()) // 2
            if self.position == "top":
                y = geo.y() + int(geo.height() * 0.05)
            else:
                y = geo.y() + geo.height() - size.height() - int(geo.height() * 0.05)
            self.window.move(x, y)

        self._run_on_ui(_place_inner)

    def show(self):
        def _show():
            self._place()
            self.window.show()

        self._run_on_ui(_show)

    def hide(self):
        self._run_on_ui(self.window.hide)

    def set_text(self, text: str):
        def _apply():
            self.label.setText(text)
            self._place()

        self._run_on_ui(_apply)

    def set_opacity(self, opacity: float):
        def _apply():
            self.opacity = opacity
            self.window.setWindowOpacity(opacity)

        self._run_on_ui(_apply)

    def set_position(self, position: str):
        def _apply():
            self.position = position
            if self.window.isVisible():
                self._place()

        self._run_on_ui(_apply)


class RecordingOverlay(_BaseOverlay):
    def __init__(self, position: str = "bottom", opacity: float = 0.5):
        super().__init__("Recording...", position=position, opacity=opacity)
        if QtWidgets is None:
            return
        self.level = QtWidgets.QProgressBar()
        self.level.setRange(0, 100)
        self.level.setTextVisible(False)
        self.level.setFixedHeight(14)
        self.level.setStyleSheet(
            """
            QProgressBar {
                background-color: rgba(255, 255, 255, 40);
                border: 0px;
                border-radius: 7px;
            }
            QProgressBar::chunk {
                background-color: rgb(0, 255, 136);
                border-radius: 7px;
            }
            """
        )
        self.container_layout.addWidget(self.level)

    def update_level(self, rms: float):
        # rms expected in [0,1]; clamp to [0,100] percent
        value = max(0, min(int(rms * 100), 100))

        def _apply():
            self.level.setValue(value)

        self._run_on_ui(_apply)


class StatusOverlay(_BaseOverlay):
    def __init__(self, text: str = "Transcribing...", position: str = "bottom", opacity: float = 0.5):
        super().__init__(text, position=position, opacity=opacity)
