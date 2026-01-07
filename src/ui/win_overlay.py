"""
Native Windows overlay bar (no Qt/Tk).

Shows a pill-shaped, always-on-top, borderless window near the top or bottom of the
current monitor work area (above the taskbar). It renders a status text and an
audio level visualization (RMS-driven bars).

Design goals:
- No "fake loop" animation: bars only change when audio level changes.
- Fully rounded corners (pill): window region uses radius = height / 2.
- Lightweight: avoid noisy logging and avoid repainting when nothing changed.
"""

from __future__ import annotations

import math
import queue
import threading
import time
import traceback
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import struct

try:
    import win32api  # type: ignore
    import win32con  # type: ignore
    import win32gui  # type: ignore
except Exception:  # pragma: no cover - optional on non-Windows
    win32api = None
    win32con = None
    win32gui = None

try:
    from PIL import Image, ImageSequence  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Image = None
    ImageSequence = None


@dataclass
class _Update:
    kind: str
    text: Optional[str] = None
    level: Optional[float] = None
    visible: Optional[bool] = None
    mode: Optional[str] = None
    opacity: Optional[float] = None
    pending_count: Optional[int] = None


class WinOverlayBar:
    def __init__(self, position: str = "bottom", opacity: float = 0.5) -> None:
        if win32gui is None or win32con is None or win32api is None:
            raise RuntimeError("pywin32 no disponible para overlay nativo")
        self.position = position if position in ("top", "bottom") else "bottom"
        self.opacity = float(opacity)
        self._q: "queue.SimpleQueue[_Update]" = queue.SimpleQueue()
        self._thread: Optional[threading.Thread] = None
        self._hwnd: Optional[int] = None
        self._running = threading.Event()
        self._ready = threading.Event()
        self._last_error: Optional[str] = None

        self._text = "Recording..."  # legacy; not drawn anymore
        self._mode = "bars"  # "bars" | "loader" | "error"
        self._error_message = ""  # message to show in error mode
        self._level = 0.0  # displayed level in [0..1]
        self._target_level = 0.0
        self._visible = False
        self._loader_phase = 0.0
        self._loader_error_logged = False
        # Prefer built-in spinner; GIF frames are optional fallback.
        self._loader_frames = []
        self._loader_frame_delay = 0.08  # fallback fps if GIF lacks duration
        # Pending jobs count (shown as badge when > 0)
        self._pending_count = 0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        print("[win_overlay] Iniciando thread...")
        self._running.set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=1.5)
        if not self._ready.is_set():
            err = self._last_error or "No se pudo inicializar overlay (timeout)"
            print(f"[win_overlay] ERROR: {err}")
            raise RuntimeError(err)

    def stop(self) -> None:
        if not self._thread:
            return
        self._q.put(_Update(kind="quit"))
        self._running.clear()
        if self._thread.is_alive():
            self._thread.join(timeout=1.5)

    def show(self, text: str) -> None:
        self.start()
        self._q.put(_Update(kind="show", text=text, visible=True))

    def hide(self) -> None:
        if not self._ready.is_set():
            return
        self._q.put(_Update(kind="hide", visible=False))

    def set_text(self, text: str) -> None:
        self.start()
        self._q.put(_Update(kind="text", text=text))

    def set_level(self, rms: float) -> None:
        if not self._ready.is_set():
            return
        self._q.put(_Update(kind="level", level=float(rms)))

    def set_mode(self, mode: str) -> None:
        self.start()
        normalized = (mode or "").strip().lower()
        if normalized not in ("bars", "loader", "error"):
            normalized = "bars"
        self._q.put(_Update(kind="mode", mode=normalized))

    def show_error(self, message: str) -> None:
        """Show error overlay - persistent until user clicks to dismiss."""
        self.start()
        self._error_message = message
        self._q.put(_Update(kind="mode", mode="error"))
        self._q.put(_Update(kind="text", text=message))
        self._q.put(_Update(kind="show", visible=True))

    def set_opacity(self, opacity: float) -> None:
        if not self._ready.is_set():
            return
        self.opacity = float(opacity)
        self._q.put(_Update(kind="opacity", opacity=float(opacity)))

    def set_pending_count(self, count: int) -> None:
        """Set the number of pending jobs (shown as badge)."""
        if not self._ready.is_set():
            self._pending_count = count
            return
        self._q.put(_Update(kind="pending", pending_count=int(count)))

    @staticmethod
    def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
        return max(min_value, min(float(value), max_value))

    @classmethod
    def _rms_to_display_level(cls, rms: float) -> float:
        """
        Convert float32 RMS in [0..1] to a visually useful 0..1 value.

        This uses a dBFS mapping so that quiet input still shows, without needing
        any fake oscillation.
        """
        rms = max(0.0, float(rms))
        db = 20.0 * math.log10(rms + 1e-6)  # ~[-120, 0]
        # Map [-55dB..-12dB] to [0..1] (keeps quiet speech from pegging the meter)
        return cls._clamp((db + 55.0) / 43.0)

    def _initial_rect(self):
        assert win32api is not None and win32gui is not None and win32con is not None
        try:
            x, y = win32api.GetCursorPos()
            mon = win32api.MonitorFromPoint((x, y), win32con.MONITOR_DEFAULTTONEAREST)
            info = win32api.GetMonitorInfo(mon)
            left, top, right, bottom = info.get("Work") or info.get("Monitor")
        except Exception:
            try:
                left, top, right, bottom = win32gui.SystemParametersInfo(win32con.SPI_GETWORKAREA)
            except Exception:
                left, top = 0, 0
                right = int(win32api.GetSystemMetrics(win32con.SM_CXSCREEN))
                bottom = int(win32api.GetSystemMetrics(win32con.SM_CYSCREEN))

        work_w = int(right - left)
        # Error mode needs wider window for text
        if self._mode == "error":
            width = min(375, work_w - 40)
            height = 36
        else:
            width = 135
            height = 27
        x = int(left + (work_w - width) // 2)
        y = int(bottom - height - 20) if self.position == "bottom" else int(top + 40)
        return x, y, width, height

    def _apply_window_region(self, hwnd: int, width: int, height: int) -> None:
        assert win32gui is not None
        ellipse = max(1, int(height))  # radius = height/2 => ellipse = height
        try:
            region = win32gui.CreateRoundRectRgn(0, 0, int(width) + 1, int(height) + 1, ellipse, ellipse)
            win32gui.SetWindowRgn(hwnd, region, True)
        except Exception:
            pass

    def _position_window(self, hwnd: int) -> None:
        assert win32con is not None and win32gui is not None
        x, y, w, h = self._initial_rect()
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            x,
            y,
            w,
            h,
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW,
        )
        self._apply_window_region(hwnd, w, h)

    def _run(self) -> None:
        assert win32gui is not None and win32con is not None and win32api is not None
        try:
            class_name = f"WhisperCheapOverlayBar_{int(time.time() * 1000)}"

            left, top, width, height = self._initial_rect()

            def wndproc(hwnd, msg, wparam, lparam):  # noqa: ANN001
                if msg == win32con.WM_PAINT:
                    self._on_paint(hwnd)
                    return 0
                if msg == win32con.WM_LBUTTONDOWN:
                    # Click to dismiss error overlay
                    if self._mode == "error" and self._visible:
                        self._mode = "bars"
                        self._error_message = ""
                        self._q.put(_Update(kind="hide", visible=False))
                    return 0
                if msg == win32con.WM_DESTROY:
                    win32gui.PostQuitMessage(0)
                    return 0
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

            wc = win32gui.WNDCLASS()
            wc.hInstance = win32api.GetModuleHandle(None)
            wc.lpszClassName = class_name
            wc.lpfnWndProc = wndproc
            wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
            win32gui.RegisterClass(wc)

            ex_style = win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_LAYERED
            style = win32con.WS_POPUP
            hwnd = win32gui.CreateWindowEx(
                ex_style,
                class_name,
                "WhisperCheapOverlay",
                style,
                left,
                top,
                width,
                height,
                0,
                0,
                wc.hInstance,
                None,
            )
            self._hwnd = hwnd
            self._apply_window_region(hwnd, width, height)

            try:
                alpha = max(40, min(int(self.opacity * 255), 255))
                win32gui.SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)
            except Exception:
                pass

            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            win32gui.UpdateWindow(hwnd)

            self._ready.set()

            last_t = time.time()
            while self._running.is_set():
                win32gui.PumpWaitingMessages()
                self._drain_updates()
                now = time.time()
                dt = max(0.0, min(now - last_t, 0.1))
                last_t = now

                if self._visible and self._hwnd:
                    needs_repaint = False

                    # Animate loader phase (for spinner in loader mode or badge spinner)
                    if self._mode == "loader" or self._pending_count > 0:
                        self._loader_phase = (self._loader_phase + (dt * 2.0)) % 1.0  # ~2 rps
                        needs_repaint = True

                    # Animate bars level
                    if self._mode == "bars":
                        target = self._target_level
                        if abs(self._level - target) > 0.001:
                            # Attack/release smoothing for a "fluid" feel.
                            attack = 0.050
                            release = 0.140
                            tau = attack if target > self._level else release
                            alpha = 1.0 - math.exp(-dt / max(0.001, tau))
                            self._level = (self._level * (1.0 - alpha)) + (target * alpha)
                            needs_repaint = True
                        else:
                            self._level = target

                    if needs_repaint:
                        try:
                            win32gui.InvalidateRect(self._hwnd, None, False)
                        except Exception:
                            pass

                time.sleep(0.016)  # ~60fps tick for smoothing/loader
        except Exception:
            self._last_error = traceback.format_exc()
            self._ready.set()
            self._running.clear()
        finally:
            self._hwnd = None
            self._running.clear()

    def _drain_updates(self) -> None:
        hwnd = self._hwnd
        if not hwnd or win32gui is None or win32con is None:
            return

        dirty = False
        try:
            while True:
                upd = self._q.get_nowait()

                if upd.kind == "quit":
                    try:
                        win32gui.DestroyWindow(hwnd)
                    except Exception:
                        pass
                    return

                if upd.text is not None:
                    self._text = upd.text
                    dirty = True

                if upd.level is not None:
                    self._target_level = self._rms_to_display_level(upd.level)
                    if self._mode == "bars":
                        dirty = True

                if upd.mode is not None:
                    old_mode = self._mode
                    self._mode = upd.mode if upd.mode in ("bars", "loader", "error") else "bars"
                    dirty = True
                    # Reposition window when switching to/from error mode (different size)
                    if (old_mode == "error") != (self._mode == "error") and self._visible:
                        self._position_window(hwnd)

                if upd.visible is not None:
                    self._visible = bool(upd.visible)
                    if self._visible:
                        try:
                            self._position_window(hwnd)
                            win32gui.ShowWindow(hwnd, win32con.SW_SHOWNA)
                            win32gui.BringWindowToTop(hwnd)
                            win32gui.UpdateWindow(hwnd)
                        except Exception:
                            pass
                    else:
                        try:
                            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                        except Exception:
                            pass
                    dirty = True

                if upd.opacity is not None:
                    try:
                        assert win32gui is not None and win32con is not None and win32api is not None
                        alpha = max(40, min(int(float(upd.opacity) * 255), 255))
                        win32gui.SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)
                    except Exception:
                        pass

                if upd.pending_count is not None:
                    self._pending_count = int(upd.pending_count)
                    dirty = True
        except queue.Empty:
            pass
        except Exception:
            pass

        if dirty and self._visible:
            try:
                win32gui.InvalidateRect(hwnd, None, True)
            except Exception:
                pass

    def _load_loader_frames(self):
        # We keep the method for potential future use; currently we rely on the built-in spinner.
        if Image is None or ImageSequence is None:
            return []
        path = Path(__file__).resolve().parent.parent / "resources" / "loader.gif"
        if not path.exists():
            return []
        frames = []
        try:
            with Image.open(path) as img:
                delay = img.info.get("duration", 80)
                self._loader_frame_delay = max(0.02, delay / 1000.0)
                for frame in ImageSequence.Iterator(img):
                    rgba = frame.convert("RGBA")
                    rgb = rgba.convert("RGB")
                    w, h = rgb.size
                    data = rgb.tobytes("raw", "BGR")
                    bmi = {
                        "bmiHeader": (
                            40,
                            w,
                            -h,
                            1,
                            24,
                            win32con.BI_RGB,
                            0,
                            0,
                            0,
                            0,
                            0,
                        ),
                        "bmiColors": [],
                    }
                    frames.append({"w": w, "h": h, "data": data, "bmi": bmi})
        except Exception:
            return []
        return frames

    def _on_paint(self, hwnd: int) -> None:
        assert win32gui is not None and win32con is not None and win32api is not None
        hdc, paint_struct = win32gui.BeginPaint(hwnd)
        try:
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            w = int(right - left)
            h = int(bottom - top)

            pad = 2
            border_width = 1
            # Use regions for a cleaner pill border (less clipping artifacts than RoundRect pens).
            pill_rgn = win32gui.CreateRoundRectRgn(0, 0, w + 1, h + 1, h, h)
            try:
                bg_brush = win32gui.CreateSolidBrush(win32api.RGB(18, 18, 18))
                green_brush = win32gui.CreateSolidBrush(win32api.RGB(0, 255, 136))
                try:
                    win32gui.FillRgn(hdc, pill_rgn, bg_brush)
                    win32gui.FrameRgn(hdc, pill_rgn, green_brush, border_width, border_width)
                finally:
                    win32gui.DeleteObject(bg_brush)
                    win32gui.DeleteObject(green_brush)
            finally:
                win32gui.DeleteObject(pill_rgn)
            if self._mode == "error":
                # Error mode: red background with white text, click X to dismiss
                red_brush = win32gui.CreateSolidBrush(win32api.RGB(180, 40, 40))
                white_brush = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 255))
                try:
                    # Draw red pill background
                    error_rgn = win32gui.CreateRoundRectRgn(0, 0, w + 1, h + 1, h, h)
                    try:
                        win32gui.FillRgn(hdc, error_rgn, red_brush)
                    finally:
                        win32gui.DeleteObject(error_rgn)

                    # Draw X button on the right
                    x_size = 9
                    x_margin = 9
                    x_cx = w - x_margin - x_size // 2
                    x_cy = h // 2
                    white_pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(255, 255, 255))
                    old_pen = win32gui.SelectObject(hdc, white_pen)
                    try:
                        win32gui.MoveToEx(hdc, x_cx - x_size // 2, x_cy - x_size // 2)
                        win32gui.LineTo(hdc, x_cx + x_size // 2, x_cy + x_size // 2)
                        win32gui.MoveToEx(hdc, x_cx + x_size // 2, x_cy - x_size // 2)
                        win32gui.LineTo(hdc, x_cx - x_size // 2, x_cy + x_size // 2)
                    finally:
                        win32gui.SelectObject(hdc, old_pen)
                        win32gui.DeleteObject(white_pen)

                    # Draw error text (use system default font - CreateFont not available in win32gui)
                    old_bk = win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
                    old_color = win32gui.SetTextColor(hdc, win32api.RGB(255, 255, 255))
                    try:
                        # Use system default GUI font (safe, always available)
                        sys_font = win32gui.GetStockObject(win32con.DEFAULT_GUI_FONT)
                        old_font = win32gui.SelectObject(hdc, sys_font)
                        try:
                            text_rect = (pad + 8, 0, w - x_margin - x_size - 8, h)
                            msg = self._error_message or "Error"
                            win32gui.DrawText(
                                hdc, msg, -1, text_rect,
                                win32con.DT_LEFT | win32con.DT_VCENTER | win32con.DT_SINGLELINE | win32con.DT_END_ELLIPSIS
                            )
                        finally:
                            win32gui.SelectObject(hdc, old_font)
                            # Don't delete stock objects
                    finally:
                        win32gui.SetBkMode(hdc, old_bk)
                        win32gui.SetTextColor(hdc, old_color)
                finally:
                    win32gui.DeleteObject(red_brush)
                    win32gui.DeleteObject(white_brush)
            elif self._mode == "loader":
                # Simple spinner: head-only arcs (no track) to avoid stray lines.
                cx = w // 2
                cy = h // 2
                ring_r = max(4, min(w, h) // 4)

                head_angle = (self._loader_phase * 2.0 * math.pi)

                def _arc_segment(start_ang: float, sweep_deg: float, width: int, gray: int):
                    pen = win32gui.CreatePen(win32con.PS_SOLID, max(1, width), win32api.RGB(gray, gray, gray))
                    old_pen_local = win32gui.SelectObject(hdc, pen)
                    try:
                        # Approximate short arc by two lines (sufficient for small spinner).
                        a1 = start_ang
                        a2 = start_ang + math.radians(sweep_deg * 0.5)
                        a3 = start_ang + math.radians(sweep_deg)
                        pts = []
                        for a in (a1, a2, a3):
                            pts.append((cx + int(math.cos(a) * ring_r), cy + int(math.sin(a) * ring_r)))
                        win32gui.MoveToEx(hdc, pts[0][0], pts[0][1])
                        win32gui.LineTo(hdc, pts[1][0], pts[1][1])
                        win32gui.LineTo(hdc, pts[2][0], pts[2][1])
                    finally:
                        win32gui.SelectObject(hdc, old_pen_local)
                        win32gui.DeleteObject(pen)

                _arc_segment(head_angle, 60, 3, 220)
                _arc_segment(head_angle - math.radians(18), 48, 2, 170)
                _arc_segment(head_angle - math.radians(36), 36, 1, 120)
            else:
                # Bars: centered, no text
                wave_y_center = h // 2
                wave_height = int(h * 0.9)
                bar_count = 14
                base_bar_width = 3
                base_gap = 1
                avail_w = max(1, w - (pad * 2))
                total_w_base = (bar_count * base_bar_width) + ((bar_count - 1) * base_gap)
                scale = min(1.2, max(1.0, avail_w / total_w_base))
                bar_width = max(2, int(round(base_bar_width * scale)))
                gap = max(1, int(round(base_gap * scale)))
                total_w = (bar_count * bar_width) + ((bar_count - 1) * gap)
                start_x = pad + max(0, (avail_w - total_w) // 2)

                level = self._clamp(self._level)
                # Higher gamma => small speech stays smaller (less "pegged").
                strength = level ** 1.25
                min_h = 2
                max_h = max(min_h + 1, wave_height)
                center = (bar_count - 1) / 2.0
                denom = max(1.0, center)
                min_diameter = max(3, bar_width + 1)

                green_brush = win32gui.CreateSolidBrush(win32api.RGB(0, 255, 136))
                null_pen3 = win32gui.GetStockObject(win32con.NULL_PEN)
                old_pen3 = win32gui.SelectObject(hdc, null_pen3)
                old_brush3 = win32gui.SelectObject(hdc, green_brush)
                try:
                    for i in range(bar_count):
                        x = int(start_x + i * (bar_width + gap))
                        shape = 1.0 - (abs(i - center) / denom)
                        weight = 0.20 + (0.80 * shape)
                        if strength < 0.05:
                            diameter = min_diameter
                            y_top = int(wave_y_center - diameter // 2)
                            y_bottom = int(wave_y_center + diameter // 2)
                            win32gui.Ellipse(hdc, x, y_top, x + diameter, y_bottom)
                        else:
                            bar_h = int(min_h + (max_h - min_h) * strength * weight)
                            bar_h = max(min_diameter, min(max_h, bar_h))
                            y_top = int(wave_y_center - bar_h // 2)
                            y_bottom = int(wave_y_center + bar_h // 2)
                            win32gui.RoundRect(hdc, x, y_top, x + bar_width, y_bottom, bar_width, bar_width)
                finally:
                    win32gui.SelectObject(hdc, old_pen3)
                    win32gui.SelectObject(hdc, old_brush3)
                    win32gui.DeleteObject(green_brush)

            # Draw pending count badge (for both bars and loader modes)
            if self._pending_count > 0 and self._mode in ("bars", "loader"):
                self._draw_pending_badge(hdc, w, h, self._pending_count)
        finally:
            win32gui.EndPaint(hwnd, paint_struct)

    def _draw_pending_badge(self, hdc: int, w: int, h: int, count: int) -> None:
        """Draw a small badge showing pending job count as dots."""
        assert win32gui is not None and win32con is not None and win32api is not None

        # Badge position: right side of the bar
        badge_x = w - 18
        badge_cy = h // 2

        # Draw small spinner (rotating arc segments)
        spinner_r = 4
        spinner_angle = self._loader_phase * 2.0 * math.pi

        # Draw spinner arcs with varying brightness
        for i, (sweep, width, gray) in enumerate([(60, 2, 255), (45, 2, 180), (30, 1, 120)]):
            ang = spinner_angle - (i * 0.25)
            pen = win32gui.CreatePen(win32con.PS_SOLID, width, win32api.RGB(gray, gray, gray))
            old_pen = win32gui.SelectObject(hdc, pen)
            try:
                # Draw arc as connected line segments
                steps = 4
                for j in range(steps):
                    a1 = ang + math.radians(sweep * j / steps)
                    a2 = ang + math.radians(sweep * (j + 1) / steps)
                    x1 = badge_x + int(math.cos(a1) * spinner_r)
                    y1 = badge_cy + int(math.sin(a1) * spinner_r)
                    x2 = badge_x + int(math.cos(a2) * spinner_r)
                    y2 = badge_cy + int(math.sin(a2) * spinner_r)
                    win32gui.MoveToEx(hdc, x1, y1)
                    win32gui.LineTo(hdc, x2, y2)
            finally:
                win32gui.SelectObject(hdc, old_pen)
                win32gui.DeleteObject(pen)

        # Draw count as dots (simpler than text, no font needed)
        dot_count = min(count, 3)  # Max 3 dots
        dot_r = 2
        dot_spacing = 4
        dots_start_x = badge_x + spinner_r + 3

        white_brush = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 255))
        null_pen = win32gui.GetStockObject(win32con.NULL_PEN)
        old_pen = win32gui.SelectObject(hdc, null_pen)
        old_brush = win32gui.SelectObject(hdc, white_brush)
        try:
            for i in range(dot_count):
                dx = dots_start_x + i * dot_spacing
                win32gui.Ellipse(hdc, dx - dot_r, badge_cy - dot_r, dx + dot_r, badge_cy + dot_r)
        finally:
            win32gui.SelectObject(hdc, old_pen)
            win32gui.SelectObject(hdc, old_brush)
            win32gui.DeleteObject(white_brush)
