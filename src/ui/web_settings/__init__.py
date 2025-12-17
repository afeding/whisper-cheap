"""
Web-based settings window using pywebview.

Provides open_web_settings() function to launch the settings UI.
Uses multiprocessing because pywebview requires the main thread.
"""

from __future__ import annotations

import multiprocessing
import sys
import time
from pathlib import Path
from typing import Optional

_process: Optional[multiprocessing.Process] = None


def _run_webview_process(config_path_str: str, html_path_str: str):
    """
    Run webview in a separate process.
    This function runs in its own process with its own main thread.
    """
    import sys
    from pathlib import Path

    import webview

    # Import SettingsAPI from api.py
    sys.path.insert(0, str(Path(__file__).parent))
    from api import SettingsAPI

    # Create and run webview
    api = SettingsAPI(Path(config_path_str))

    window = webview.create_window(
        'Whisper Cheap',
        html_path_str,
        js_api=api,
        width=900,
        height=650,
        min_size=(800, 550),
        background_color='#0a0a0a'
    )

    # Find icon path
    config_dir = Path(config_path_str).parent
    icon_path = config_dir / "src" / "resources" / "icons" / "app.ico"
    icon_str = str(icon_path.absolute()) if icon_path.exists() else None

    def set_window_icon_windows(window_title: str, icon_path: str):
        """Set window icon using Windows API (ctypes).
        pywebview's icon parameter only works on GTK/QT, not Windows."""
        if sys.platform != "win32" or not icon_path:
            return

        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32

            # Constants
            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x00000010
            LR_DEFAULTSIZE = 0x00000040
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1

            # Load icon from file
            icon_handle = user32.LoadImageW(
                None,                           # hInstance
                icon_path,                      # path to .ico file
                IMAGE_ICON,                     # type
                0, 0,                           # cx, cy (0 = use default)
                LR_LOADFROMFILE | LR_DEFAULTSIZE
            )

            if not icon_handle:
                print(f"[Settings] Failed to load icon: {icon_path}")
                return

            # Find window by title
            hwnd = user32.FindWindowW(None, window_title)
            if not hwnd:
                print(f"[Settings] Window not found: {window_title}")
                return

            # Set both small and big icons
            user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, icon_handle)
            user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, icon_handle)
            print(f"[Settings] Icon set successfully: {icon_path}")

        except Exception as e:
            print(f"[Settings] Error setting icon: {e}")

    def on_shown():
        """Called when window is shown. Set icon using Windows API."""
        import time
        time.sleep(0.1)  # Small delay to ensure window is fully created
        if icon_str:
            set_window_icon_windows('Whisper Cheap', icon_str)

    # Register event and start
    window.events.shown += on_shown
    webview.start()


def open_web_settings(config_path: Path, history_manager=None) -> None:
    """
    Open the web-based settings window.

    Args:
        config_path: Path to config.json
        history_manager: Optional HistoryManager instance (not used in subprocess)
    """
    global _process

    # STRATEGY: Always terminate the previous process (if any) before creating a new one.
    # This is simple and avoids is_alive() reliability issues on Windows.
    if _process is not None:
        try:
            # Kill the old process forcefully
            _process.terminate()
            # Wait for it to die
            _process.join(timeout=2)
            # If it's still alive after 2 seconds, force kill it
            if _process.is_alive():
                _process.kill()
                _process.join(timeout=1)
        except Exception:
            pass
        finally:
            _process = None

    html_path = Path(__file__).parent / "index.html"

    # Convert to strings to avoid Path serialization issues
    config_path_str = str(config_path.resolve())
    html_path_str = str(html_path.resolve())

    # Always create a fresh process
    _process = multiprocessing.Process(
        target=_run_webview_process,
        args=(config_path_str, html_path_str),
        daemon=False  # Changed to False so we have more control
    )
    _process.start()
