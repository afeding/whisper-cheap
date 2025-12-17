"""
System tray manager using pystray.

Provides:
- TrayManager: create tray icon with menu (Settings, Cancel, Quit)
- set_state: update icon according to state ("idle", "recording", "transcribing", "formatting")
- start/stop controls

Icons:
- Tries to load PNGs from src/resources/icons; if missing, generates solid color icons.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import pystray
except ImportError:  # pragma: no cover - optional dependency
    pystray = None

try:
    from PIL import Image, ImageColor, ImageDraw
except ImportError:  # pragma: no cover - optional dependency
    Image = None
    ImageColor = None
    ImageDraw = None


STATE_COLORS = {
    "idle": "#9e9e9e",
    "recording": "#e53935",
    "transcribing": "#fb8c00",
    "formatting": "#1e88e5",
}


class TrayManager:
    def __init__(
        self,
        icons_dir: Path | str = "src/resources/icons",
        on_settings: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None,
        pystray_module=None,
    ) -> None:
        self.icons_dir = Path(icons_dir)
        self.on_settings = on_settings
        self.on_cancel = on_cancel
        self.on_quit = on_quit
        self._pystray = pystray_module or pystray
        self._icon = None
        self._thread: Optional[threading.Thread] = None
        self._state = "idle"

    def start(self):
        if self._pystray is None:
            raise RuntimeError("pystray is not available")
        if self._icon is not None:
            logger.warning("[tray] start() called but icon already exists")
            return

        logger.info("[tray] Starting tray icon...")
        image = self._load_icon_for_state(self._state)
        menu = self._build_menu()
        self._icon = self._pystray.Icon("WhisperCheap", image, "Whisper Cheap", menu)

        # run in background - creates an internal NON-DAEMON thread
        logger.debug("[tray] Calling Icon.run_detached()...")
        self._icon.run_detached()
        logger.info("[tray] Tray icon started successfully")

    # Maximum time to wait for tray icon to stop (seconds)
    STOP_TIMEOUT = 2.0

    def stop(self):
        """
        Stop the tray icon with timeout to prevent blocking shutdown.

        pystray.Icon.run_detached() creates an internal NON-DAEMON thread.
        If Icon.stop() doesn't terminate it quickly, we continue anyway
        to avoid blocking the entire application shutdown.
        """
        if not self._icon:
            logger.debug("[tray] stop() called but icon is None, nothing to stop")
            return

        logger.info("[tray] Stopping tray icon...")
        old_icon = self._icon
        self._icon = None  # Clear reference immediately

        # Call stop() in a separate thread with timeout
        stop_completed = threading.Event()

        def _do_stop():
            try:
                old_icon.stop()
                stop_completed.set()
            except Exception as e:
                logger.error(f"[tray] Exception during Icon.stop(): {e}")
                stop_completed.set()

        stop_thread = threading.Thread(target=_do_stop, daemon=True)
        stop_thread.start()

        # Wait with timeout
        if stop_completed.wait(timeout=self.STOP_TIMEOUT):
            logger.info("[tray] Tray icon stopped successfully")
        else:
            logger.warning(f"[tray] Icon.stop() did not complete in {self.STOP_TIMEOUT}s, continuing anyway")

    def set_state(self, state: str):
        self._state = state
        if self._icon is None:
            return
        image = self._load_icon_for_state(state)
        try:
            self._icon.icon = image
        except Exception:
            pass

    def _build_menu(self):
        if self._pystray is None:
            return None
        items = []
        if self.on_settings:
            items.append(self._pystray.MenuItem("Settings", lambda: self.on_settings()))
        if self.on_cancel:
            items.append(self._pystray.MenuItem("Cancel", lambda: self.on_cancel()))
        if self.on_quit:
            items.append(self._pystray.MenuItem("Quit", lambda: self._safe_call(self.on_quit)))
        return self._pystray.Menu(*items) if items else None

    def _load_icon_for_state(self, state: str):
        if Image is None:
            # Fallback placeholder object when Pillow is unavailable (e.g., headless tests)
            return state
        filename = self.icons_dir / f"{state}.png"
        if filename.exists():
            try:
                img = Image.open(filename)
                # Ensure it's in RGBA and reasonably sized for tray
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                # Scale to 64x64 if too large (for tray compatibility)
                if img.size[0] > 128:
                    img.thumbnail((64, 64), Image.Resampling.LANCZOS)
                return img
            except Exception:
                pass
        # fallback: generate rounded icon with state color
        color = STATE_COLORS.get(state, "#9e9e9e")
        size = (64, 64)
        color_rgba = ImageColor.getcolor(color, "RGBA")

        # Create base colored circle
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = 4
        draw.ellipse(
            (margin, margin, size[0] - margin, size[1] - margin),
            fill=color_rgba
        )
        return img

    def _safe_call(self, fn):
        try:
            return fn()
        except SystemExit:
            return None
        except Exception:
            return None
