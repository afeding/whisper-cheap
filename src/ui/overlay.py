"""
PyQt6 overlay bar with smooth animations and clean design.

RecordingOverlayBar: Professional audio recording overlay with:
- Fluid vertical open/close animation
- Dynamic audio visualization
- Color transitions between states
- Thread-safe API
"""

from __future__ import annotations

import logging
import math
import os
from typing import Optional, List

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRectF, QPointF, QElapsedTimer
    from PyQt6.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush, QFont
    from PyQt6.QtWidgets import QWidget, QApplication
except ImportError:  # pragma: no cover - optional dependency
    QtCore = None
    QtGui = None
    QtWidgets = None
    Qt = None
    pyqtSignal = None
    QTimer = None
    QRectF = None
    QPointF = None
    QElapsedTimer = None
    QPainter = None
    QPainterPath = None
    QColor = None
    QPen = None
    QBrush = None
    QFont = None
    QWidget = None
    QApplication = None

logger = logging.getLogger(__name__)

_APP_INSTANCE: Optional["QApplication"] = None


def ensure_app() -> Optional["QApplication"]:
    """Create or return singleton QApplication."""
    global _APP_INSTANCE
    if QApplication is None:
        return None
    app = QApplication.instance()
    if app is None:
        os.environ.setdefault("QT_QPA_PLATFORM", "windows:darkmode=2" if os.name == "nt" else "")
        app = QApplication([])
        app.setQuitOnLastWindowClosed(False)
    _APP_INSTANCE = app
    return app


# Base class: QWidget if available, otherwise object (will raise on instantiation)
_BaseWidget = QWidget if QWidget is not None else object


class RecordingOverlayBar(_BaseWidget):
    """
    Clean overlay bar with smooth animations.

    Features:
    - Vertical open/close animation (grows/shrinks from center)
    - Dynamic audio bars with organic movement
    - Color transitions: Green (recording) → Orange (AI processing)
    - Thread-safe API
    """

    # Internal signal for thread-safe updates
    _update_signal = pyqtSignal(str, object) if pyqtSignal else None

    # ─────────────────────────────────────────────────────────────────
    # Design Constants
    # ─────────────────────────────────────────────────────────────────

    BAR_COUNT = 24
    BAR_WIDTH = 1.5
    BAR_GAP = 1.5
    BORDER_WIDTH = 1.5

    WINDOW_WIDTH = 145
    WINDOW_HEIGHT = 32

    # Animation (seconds)
    ANIM_DURATION = 0.2

    def __init__(self, position: str = "bottom", opacity: float = 0.95):
        if QWidget is None:
            raise RuntimeError("PyQt6 is required for RecordingOverlayBar")

        self.app = ensure_app()
        if self.app is None:
            raise RuntimeError("QApplication not available")

        super().__init__()

        # Configuration
        self.position = position if position in ("top", "bottom") else "bottom"
        self._base_opacity = 1.0  # Always 100% opacity

        # State
        self._mode = "bars"  # "bars" | "loader" | "error"
        self._level = 0.0
        self._target_level = 0.0
        self._pending_count = 0
        self._error_message = ""
        self._visible = False

        # Animation state
        self._open_progress = 0.0  # 0 = closed, 1 = open
        self._open_target = 0.0
        self._color_progress = 0.0  # 0 = green, 1 = orange
        self._color_target = 0.0
        self._loader_angle = 0.0

        # Pre-computed bar properties (organic movement)
        # Center bars move faster and with more amplitude
        center = (self.BAR_COUNT - 1) / 2.0
        self._bar_phase: List[float] = []
        self._bar_speed: List[float] = []
        self._bar_amp: List[float] = []
        for i in range(self.BAR_COUNT):
            dist = abs(i - center) / center  # 0 at center, 1 at edges
            # Phase: offset each bar
            self._bar_phase.append(i * 1.2 + (i % 4) * 0.8)
            # Speed: MUCH faster, center even faster
            self._bar_speed.append(8.0 - dist * 3.0 + (i % 3) * 1.5)
            # Amplitude: strong variation
            self._bar_amp.append(1.0 - dist * 0.3)

        # Pre-cached colors (avoid creating each frame)
        self._color_bg = QColor(15, 15, 15, 245)
        self._color_green = QColor(0, 230, 118)
        self._color_orange = QColor(255, 152, 0)
        self._color_red = QColor(220, 53, 69)
        self._color_white = QColor(255, 255, 255)
        self._cached_active_color = QColor(self._color_green)
        self._bar_color = QColor(0, 230, 118)  # Reusable for bar drawing

        # Timing with QElapsedTimer (high precision on Windows)
        self._elapsed = QElapsedTimer()
        self._elapsed.start()
        self._last_ms = 0
        self._time_s = 0.0

        # Window setup
        self._setup_window()
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Animation timer (~60fps, use CoarseTimer for better DWM compat)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.setInterval(14)  # Slightly faster to compensate for timer drift

        # Connect signal
        if self._update_signal:
            self._update_signal.connect(self._handle_update, Qt.ConnectionType.QueuedConnection)

    def _setup_window(self):
        """Configure window."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

    def _place_window(self):
        """Position window on screen."""
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        if self.position == "top":
            y = geo.y() + 45
        else:
            y = geo.y() + geo.height() - self.height() - 25
        self.move(x, y)

    # ─────────────────────────────────────────────────────────────────
    # Color Management
    # ─────────────────────────────────────────────────────────────────

    def _update_active_color(self) -> None:
        """Update cached active color based on state."""
        if self._mode == "error":
            self._cached_active_color = self._color_red
        else:
            t = self._color_progress
            t2 = t * t * (3.0 - 2.0 * t)  # smoothstep
            r = int(self._color_green.red() * (1 - t2) + self._color_orange.red() * t2)
            g = int(self._color_green.green() * (1 - t2) + self._color_orange.green() * t2)
            b = int(self._color_green.blue() * (1 - t2) + self._color_orange.blue() * t2)
            self._cached_active_color.setRgb(r, g, b)

    # ─────────────────────────────────────────────────────────────────
    # Public API (thread-safe)
    # ─────────────────────────────────────────────────────────────────

    def start(self) -> None:
        pass

    def stop(self) -> None:
        self._emit_update("stop", None)

    def show(self, text: str = "") -> None:
        self._emit_update("show", True)

    def hide(self) -> None:
        self._emit_update("hide", False)

    def set_text(self, text: str) -> None:
        pass

    def set_level(self, rms: float) -> None:
        self._emit_update("level", float(rms))

    def set_mode(self, mode: str) -> None:
        normalized = (mode or "").strip().lower()
        if normalized not in ("bars", "loader", "error"):
            normalized = "bars"
        self._emit_update("mode", normalized)

    def set_opacity(self, opacity: float) -> None:
        pass  # Opacity fixed at 100%

    def set_pending_count(self, count: int) -> None:
        self._emit_update("pending", int(count))

    def show_error(self, message: str) -> None:
        self._emit_update("error", str(message))

    # ─────────────────────────────────────────────────────────────────
    # Signal handling
    # ─────────────────────────────────────────────────────────────────

    def _emit_update(self, update_type: str, value: object) -> None:
        if self._update_signal:
            self._update_signal.emit(update_type, value)

    def _handle_update(self, update_type: str, value: object) -> None:
        try:
            if update_type == "show":
                self._visible = True
                self._open_target = 1.0
                self._elapsed.restart()
                self._last_ms = 0
                self._place_window()
                self._timer.start()
                self.setWindowOpacity(self._base_opacity)
                super().show()
                self.raise_()

            elif update_type == "hide":
                self._open_target = 0.0

            elif update_type == "level":
                self._target_level = self._rms_to_display(float(value))

            elif update_type == "mode":
                old_mode = self._mode
                self._mode = str(value)

                if self._mode == "loader":
                    self._color_target = 1.0
                elif self._mode == "bars":
                    self._color_target = 0.0

                if self._mode == "error":
                    self.setWindowFlags(
                        Qt.WindowType.FramelessWindowHint
                        | Qt.WindowType.WindowStaysOnTopHint
                        | Qt.WindowType.Tool
                    )
                    self.setFixedSize(380, 40)
                    if self._visible:
                        self._place_window()
                        super().show()
                else:
                    self.setWindowFlags(
                        Qt.WindowType.FramelessWindowHint
                        | Qt.WindowType.WindowStaysOnTopHint
                        | Qt.WindowType.Tool
                        | Qt.WindowType.WindowTransparentForInput
                    )
                    if old_mode == "error":
                        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
                        if self._visible:
                            self._place_window()
                            super().show()

            elif update_type == "pending":
                self._pending_count = int(value)

            elif update_type == "error":
                self._error_message = str(value)
                self._mode = "error"
                self.setFixedSize(380, 40)
                self._visible = True
                self._open_target = 1.0
                self._elapsed.restart()
                self._last_ms = 0
                self._place_window()
                self._timer.start()
                self.setWindowFlags(
                    Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.WindowStaysOnTopHint
                    | Qt.WindowType.Tool
                )
                self.setWindowOpacity(self._base_opacity)
                super().show()
                self.raise_()

            elif update_type == "stop":
                self._timer.stop()
                super().hide()

        except Exception as e:
            logger.error(f"[overlay] Error: {e}")

    # ─────────────────────────────────────────────────────────────────
    # Animation Loop
    # ─────────────────────────────────────────────────────────────────

    def _on_tick(self) -> None:
        # High precision delta time
        now_ms = self._elapsed.elapsed()
        dt = (now_ms - self._last_ms) / 1000.0
        self._last_ms = now_ms
        dt = min(0.05, max(0.001, dt))  # Clamp to avoid jumps
        self._time_s += dt

        changed = False

        # Open/close animation
        if self._open_progress != self._open_target:
            speed = 1.0 / self.ANIM_DURATION
            if self._open_target > self._open_progress:
                self._open_progress = min(1.0, self._open_progress + dt * speed)
            else:
                self._open_progress = max(0.0, self._open_progress - dt * speed)
            changed = True

            if self._open_progress <= 0.001 and self._open_target == 0.0:
                self._visible = False
                self._timer.stop()
                super().hide()
                return

        # Color animation
        if self._color_progress != self._color_target:
            speed = 3.0
            if self._color_target > self._color_progress:
                self._color_progress = min(1.0, self._color_progress + dt * speed)
            else:
                self._color_progress = max(0.0, self._color_progress - dt * speed)
            self._update_active_color()
            changed = True

        # Loader rotation
        if self._mode == "loader":
            self._loader_angle = (self._loader_angle + dt * 360) % 360
            changed = True

        # Audio level - almost instant response
        if self._mode == "bars":
            diff = self._target_level - self._level
            if abs(diff) > 0.001:
                # Very fast attack (25), quick release (15)
                speed = 25.0 if diff > 0 else 15.0
                self._level += diff * min(1.0, dt * speed)
            changed = True  # Bars always animate

        if changed:
            self.update()

    @staticmethod
    def _rms_to_display(rms: float) -> float:
        rms = max(0.0, float(rms))
        db = 20.0 * math.log10(rms + 1e-6)
        return max(0.0, min(1.0, (db + 50.0) / 40.0))

    # ─────────────────────────────────────────────────────────────────
    # Rendering
    # ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cy = h / 2.0

        # Vertical scale with smooth ease
        t = self._open_progress
        scale_y = t * t * (3.0 - 2.0 * t)  # smoothstep
        if scale_y < 0.01:
            painter.end()
            return

        # Pill dimensions
        pill_h = (h - 8) * scale_y
        pill_y = cy - pill_h / 2
        radius = pill_h / 2

        # Draw pill background
        pill_rect = QRectF(4, pill_y, w - 8, pill_h)
        path = QPainterPath()
        path.addRoundedRect(pill_rect, radius, radius)
        painter.fillPath(path, self._color_bg)

        # Draw border
        painter.setPen(QPen(self._cached_active_color, self.BORDER_WIDTH))
        painter.drawPath(path)

        # Content visibility
        if scale_y > 0.4:
            content_alpha = (scale_y - 0.4) / 0.6

            if self._mode == "error":
                self._draw_error(painter, pill_rect, content_alpha)
            elif self._mode == "loader":
                self._draw_loader(painter, pill_rect, content_alpha)
            else:
                self._draw_bars(painter, pill_rect, scale_y, content_alpha)

        painter.end()

    def _draw_bars(self, painter: "QPainter", rect: "QRectF", scale_y: float, alpha: float) -> None:
        """Draw audio bars - fast, reactive, expressive."""
        cx = rect.center().x()
        cy = rect.center().y()

        total_w = self.BAR_COUNT * self.BAR_WIDTH + (self.BAR_COUNT - 1) * self.BAR_GAP
        start_x = cx - total_w / 2

        max_h = rect.height() * 0.85  # Taller bars
        min_h = 2

        level = self._level
        t = self._time_s

        painter.setPen(Qt.PenStyle.NoPen)
        color = self._cached_active_color
        cr, cg, cb = color.red(), color.green(), color.blue()

        center = (self.BAR_COUNT - 1) / 2.0

        for i in range(self.BAR_COUNT):
            x = start_x + i * (self.BAR_WIDTH + self.BAR_GAP)

            # Center-weighted: center = 1.0, edges = 0.35
            dist = abs(i - center) / center
            envelope = 1.0 - dist * 0.65

            # Fast oscillating wave
            wave = math.sin(t * self._bar_speed[i] + self._bar_phase[i]) * self._bar_amp[i]

            if level < 0.03:
                # Idle: just dots
                bar_h = min_h
            else:
                # Active: amplified response
                boosted_level = min(1.0, level * 1.4)  # Boost level for more height
                variation = 0.6 + wave * 0.4
                bar_h = min_h + (max_h - min_h) * boosted_level * envelope * variation

            bar_h = max(min_h, bar_h * scale_y)

            # Draw bar
            self._bar_color.setRgb(cr, cg, cb, int(255 * alpha))
            painter.setBrush(self._bar_color)
            painter.drawRect(QRectF(x, cy - bar_h / 2, self.BAR_WIDTH, bar_h))

    def _draw_loader(self, painter: "QPainter", rect: "QRectF", alpha: float) -> None:
        """Draw spinner."""
        cx, cy = rect.center().x(), rect.center().y()
        radius = rect.height() * 0.28

        color = self._cached_active_color
        angle = self._loader_angle

        # Single smooth arc
        c = QColor(color.red(), color.green(), color.blue(), int(255 * alpha))
        pen = QPen(c, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        arc_rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        painter.drawArc(arc_rect, int(angle * 16), int(90 * 16))

        # Tail with fade
        c2 = QColor(color.red(), color.green(), color.blue(), int(100 * alpha))
        pen2 = QPen(c2, 2.0)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen2)
        painter.drawArc(arc_rect, int((angle - 60) * 16), int(50 * 16))

    def _draw_error(self, painter: "QPainter", rect: "QRectF", alpha: float) -> None:
        """Draw error with X button."""
        cy = rect.center().y()

        c = QColor(255, 255, 255, int(255 * alpha))

        # X button
        x_cx = rect.right() - 16
        pen = QPen(c, 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        s = 5
        painter.drawLine(QPointF(x_cx - s, cy - s), QPointF(x_cx + s, cy + s))
        painter.drawLine(QPointF(x_cx + s, cy - s), QPointF(x_cx - s, cy + s))

        # Text
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(c)
        text_rect = QRectF(rect.left() + 14, rect.top(), rect.width() - 50, rect.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                        self._error_message or "Error")

    def mousePressEvent(self, event) -> None:
        if self._mode == "error":
            self._mode = "bars"
            self._error_message = ""
            self._color_target = 0.0
            self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            self.hide()


# ─────────────────────────────────────────────────────────────────────────────
# Legacy classes
# ─────────────────────────────────────────────────────────────────────────────

class RecordingOverlay:
    """Legacy - use RecordingOverlayBar."""

    def __init__(self, position: str = "bottom", opacity: float = 0.95):
        self._bar = RecordingOverlayBar(position=position, opacity=opacity)

    def show(self):
        self._bar.set_mode("bars")
        self._bar.show()

    def hide(self):
        self._bar.hide()

    def set_text(self, text: str):
        pass

    def update_level(self, rms: float):
        self._bar.set_level(rms)

    def set_opacity(self, opacity: float):
        pass  # Fixed at 100%

    def set_position(self, position: str):
        self._bar.position = position


class StatusOverlay:
    """Legacy - use RecordingOverlayBar."""

    def __init__(self, text: str = "Processing...", position: str = "bottom", opacity: float = 0.95):
        self._bar = RecordingOverlayBar(position=position, opacity=opacity)

    def show(self):
        self._bar.set_mode("loader")
        self._bar.show()

    def hide(self):
        self._bar.hide()

    def set_text(self, text: str):
        pass

    def set_opacity(self, opacity: float):
        pass  # Fixed at 100%

    def set_position(self, position: str):
        self._bar.position = position

    def show_error(self, message: str):
        self._bar.show_error(message)
