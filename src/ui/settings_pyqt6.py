"""
PyQt6 Settings Window with iOS Dark Mode Design.

Professional, clean, and trustworthy UI that inspires confidence.
Replaces CustomTkinter implementation with native PyQt6.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

try:
    from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QPixmap, QIcon, QCloseEvent, QKeyEvent
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QFrame, QLabel, QPushButton,
        QLineEdit, QComboBox, QCheckBox, QRadioButton, QSlider,
        QVBoxLayout, QHBoxLayout, QScrollArea, QStackedWidget,
        QButtonGroup, QMessageBox, QProgressBar, QSizePolicy
    )
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

try:
    from src.ui.overlay import ensure_app
except ImportError:
    ensure_app = None

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import requests
except ImportError:
    requests = None


# =============================================================================
# iOS DARK MODE COLOR SYSTEM
# =============================================================================

COLORS = {
    # Backgrounds (iOS semantic)
    "bg_primary": "#080808",
    "bg_secondary": "#0d0d0d",
    "bg_tertiary": "#111111",
    "bg_elevated": "#1a1a1a",

    # Accent (Neon Green - Brand)
    "accent_primary": "#00ff88",
    "accent_hover": "#00ffaa",
    "accent_active": "#00dd77",
    "accent_dim": "#00aa55",

    # Text (iOS labels)
    "label": "#ffffff",
    "label_secondary": "#b0b0b0",
    "label_tertiary": "#707070",
    "label_quaternary": "#505050",

    # Borders
    "separator": "#1f1f1f",
    "border": "#262626",

    # Fill (buttons, inputs)
    "fill_primary": "#0f0f0f",
    "fill_secondary": "#141414",

    # System colors
    "system_red": "#ff453a",
}

# =============================================================================
# SPACING SYSTEM (iOS-Inspired)
# =============================================================================

WINDOW_MARGIN = 28
SIDEBAR_WIDTH = 260
CARD_PADDING_H = 32
CARD_PADDING_V = 24
ROW_SPACING = 16
LABEL_WIDTH = 180
INPUT_HEIGHT = 48

# =============================================================================
# QSS STYLESHEET
# =============================================================================

STYLESHEET = """
/* ===== GLOBAL RESET ===== */
QMainWindow {
    background-color: #080808;
}

QWidget {
    background-color: transparent;
    color: #ffffff;
    font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    font-size: 14px;
}

/* ===== SCROLLBARS (iOS Thin Style) ===== */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.3);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
    border: none;
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.2);
    min-width: 30px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(255, 255, 255, 0.3);
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
    border: none;
    width: 0px;
}

/* ===== QLINEEDIT (Text inputs) ===== */
QLineEdit {
    background-color: #0f0f0f;
    color: #ffffff;
    border: 1px solid #262626;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    font-family: "JetBrains Mono", "Consolas", "Courier New", monospace;
}

QLineEdit:hover {
    border-color: #2a2a2a;
    background-color: #141414;
}

QLineEdit:focus {
    border-color: #00ff88;
    background-color: #0f0f0f;
}

QLineEdit:disabled {
    background-color: #1f1f1f;
    color: #505050;
    border-color: #1f1f1f;
}

QLineEdit[readOnly="true"] {
    background-color: #0a0a0a;
    color: #b0b0b0;
    border-color: #1f1f1f;
}

/* ===== QCOMBOBOX (Dropdowns) ===== */
QComboBox {
    background-color: #0f0f0f;
    color: #ffffff;
    border: 1px solid #262626;
    border-radius: 12px;
    padding: 12px 16px;
    padding-right: 40px;
    font-size: 14px;
    font-family: "JetBrains Mono", "Consolas", "Courier New", monospace;
}

QComboBox:hover {
    border-color: #2a2a2a;
    background-color: #141414;
}

QComboBox:focus {
    border-color: #00ff88;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 40px;
    border: none;
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}

QComboBox::down-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #00ff88;
}

QComboBox QAbstractItemView {
    background-color: #0f0f0f;
    color: #ffffff;
    border: 1px solid #262626;
    border-radius: 8px;
    selection-background-color: rgba(0, 255, 136, 0.15);
    selection-color: #00ff88;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 10px 16px;
    border-radius: 6px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #1a1a1a;
}

QComboBox QAbstractItemView::item:selected {
    background-color: rgba(0, 255, 136, 0.15);
    color: #00ff88;
}

/* ===== QPUSHBUTTON (Buttons) ===== */
QPushButton {
    background-color: #0f0f0f;
    color: #b0b0b0;
    border: 1px solid #262626;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 13px;
    font-weight: bold;
    font-family: "JetBrains Mono", "Consolas", "Courier New", monospace;
}

QPushButton:hover {
    background-color: #1a1a1a;
    color: #ffffff;
    border-color: #2a2a2a;
}

QPushButton:pressed {
    background-color: #0d0d0d;
    color: #b0b0b0;
}

QPushButton:disabled {
    background-color: #1f1f1f;
    color: #505050;
    border-color: #1f1f1f;
}

/* Primary button */
QPushButton[primary="true"] {
    background-color: #00ff88;
    color: #000000;
    border: none;
}

QPushButton[primary="true"]:hover {
    background-color: #00ffaa;
}

QPushButton[primary="true"]:pressed {
    background-color: #00dd77;
}

QPushButton[primary="true"]:disabled {
    background-color: #00aa55;
    color: rgba(0, 0, 0, 0.5);
}

/* Navigation button */
QPushButton[nav="true"] {
    background-color: transparent;
    color: #707070;
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
}

QPushButton[nav="true"]:hover {
    background-color: #1a1a1a;
    color: #b0b0b0;
}

QPushButton[nav="true"][active="true"] {
    background-color: #00ff88;
    color: #000000;
}

QPushButton[nav="true"][active="true"]:hover {
    background-color: #00ffaa;
}

/* Danger button */
QPushButton[danger="true"] {
    background-color: transparent;
    color: #ff453a;
    border: 1px solid #ff453a;
}

QPushButton[danger="true"]:hover {
    background-color: rgba(255, 69, 58, 0.1);
}

QPushButton[danger="true"]:pressed {
    background-color: rgba(255, 69, 58, 0.2);
}

/* ===== QCHECKBOX ===== */
QCheckBox {
    spacing: 12px;
    color: #ffffff;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #262626;
    border-radius: 6px;
    background-color: #0f0f0f;
}

QCheckBox::indicator:hover {
    border-color: #2a2a2a;
    background-color: #141414;
}

QCheckBox::indicator:checked {
    background-color: #00ff88;
    border-color: #00ff88;
}

QCheckBox::indicator:checked:hover {
    background-color: #00ffaa;
    border-color: #00ffaa;
}

QCheckBox::indicator:disabled {
    background-color: #1f1f1f;
    border-color: #1f1f1f;
}

/* ===== QRADIOBUTTON ===== */
QRadioButton {
    spacing: 12px;
    color: #ffffff;
    font-size: 14px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #262626;
    border-radius: 10px;
    background-color: #0f0f0f;
}

QRadioButton::indicator:hover {
    border-color: #2a2a2a;
    background-color: #141414;
}

QRadioButton::indicator:checked {
    background-color: #00ff88;
    border-color: #00ff88;
}

QRadioButton::indicator:checked:hover {
    border-color: #00ffaa;
}

/* ===== QSLIDER ===== */
QSlider::groove:horizontal {
    background: #262626;
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #00ff88;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #00ffaa;
    width: 18px;
    height: 18px;
    margin: -7px 0;
}

QSlider::handle:horizontal:pressed {
    background: #00dd77;
}

QSlider::sub-page:horizontal {
    background: #00ff88;
    border-radius: 2px;
}

/* ===== QPROGRESSBAR ===== */
QProgressBar {
    background-color: #262626;
    border: none;
    border-radius: 2px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #00ff88;
    border-radius: 2px;
}

/* ===== QLABEL ===== */
QLabel {
    color: #ffffff;
    background-color: transparent;
    border: none;
}

/* ===== QFRAME ===== */
QFrame[card="true"] {
    background-color: #0d0d0d;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
}

QFrame[sidebar="true"] {
    background-color: #111111;
    border-radius: 20px;
}

QFrame[divider="true"] {
    background-color: rgba(0, 255, 136, 0.2);
}

QFrame[accentBar="true"] {
    background-color: #00ff88;
    border-radius: 2px;
}

/* ===== QMESSAGEBOX ===== */
QMessageBox {
    background-color: #0d0d0d;
}

QMessageBox QLabel {
    color: #ffffff;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""

# =============================================================================
# LLM SYSTEM PROMPT
# =============================================================================

LLM_SYSTEM_PROMPT = (
    "You are \"Transcription 2.0\": a real-time dictation post-editor.\n\n"
    "Task:\n"
    "- Take the user's raw speech-to-text transcript and return the same content as clean written text.\n\n"
    "Absolute output rules:\n"
    "- Output ONLY the transformed text. No titles, no prefixes, no explanations, no markdown wrappers.\n"
    "- Keep the SAME language as the transcript. Do NOT translate.\n"
    "- Preserve meaning strictly. Do NOT add new ideas, facts, steps, names, or assumptions.\n"
)

# =============================================================================
# DEFAULT MODELS
# =============================================================================

MAX_MODELS_SHOWN = 50
DEFAULT_MODELS_PATH = Path(__file__).resolve().parent.parent / "resources" / "models_default.json"


def _load_config(path: Path) -> Dict[str, Any]:
    """Load config from JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_config(path: Path, data: Dict[str, Any]) -> None:
    """Save config to JSON file."""
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_default_models(path: Path, fallback: List[str]) -> List[str]:
    """Load default models from JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(x) for x in data if x]
    except Exception:
        pass
    return list(fallback)


# =============================================================================
# SETTINGS WINDOW
# =============================================================================

class SettingsWindow(QMainWindow):
    """Settings window with iOS dark mode aesthetic."""

    def __init__(
        self,
        config_path: Path,
        history_manager=None
    ) -> None:
        """
        Initialize settings window.

        Args:
            config_path: Path to config.json
            history_manager: Optional history manager for history section
        """
        if not PYQT6_AVAILABLE:
            raise RuntimeError("PyQt6 is not available")

        # Ensure QApplication exists
        if ensure_app:
            self.app = ensure_app()
        else:
            from PyQt6.QtWidgets import QApplication
            self.app = QApplication.instance()
            if not self.app:
                self.app = QApplication([])

        super().__init__()

        self.config_path = config_path
        self.data = _load_config(config_path)
        self.history_manager = history_manager

        # Load default models
        self.default_models: List[str] = _load_default_models(
            DEFAULT_MODELS_PATH,
            fallback=[
                "openai/gpt-oss-20b",
                "openai/gpt-5-nano",
                "google/gemini-2.5-flash-lite",
                "mistralai/mistral-small-3.2-24b-instruct",
            ]
        )
        self.user_models: List[str] = []
        self.model_options: List[str] = list(self.default_models)
        self.model_all: List[str] = list(self.default_models)
        self.current_model: str = ""

        # Widget storage
        self.widgets: Dict[str, Any] = {}
        self.hidden_vars: Dict[str, Any] = {}
        self.nav_buttons: Dict[str, QPushButton] = {}
        self.section_widgets: Dict[str, QWidget] = {}

        # Image references (prevent GC)
        self._image_refs: Dict[str, Any] = {}

        # Save timer
        self._save_timer: Optional[QTimer] = None

        # Hotkey capture state
        self.capturing_hotkey = False
        self.captured_keys: List[str] = []

        # Setup window
        self._setup_window()
        self._apply_stylesheet()
        self._build_layout()
        self._populate()
        self._show_section("General")

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Whisper Cheap")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)

        # Window icon
        try:
            icon_path = Path(__file__).parent.parent / "resources" / "icons" / "app.ico"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass

    def _apply_stylesheet(self) -> None:
        """Apply QSS stylesheet."""
        self.setStyleSheet(STYLESHEET)

    def _run_on_ui(self, fn: Callable) -> None:
        """Execute function on Qt UI thread safely."""
        if QThread.currentThread() == self.thread():
            fn()
        else:
            QTimer.singleShot(0, fn)

    # =========================================================================
    # LAYOUT BUILDING
    # =========================================================================

    def _build_layout(self) -> None:
        """Build main layout with sidebar and content area."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(WINDOW_MARGIN, WINDOW_MARGIN, WINDOW_MARGIN, WINDOW_MARGIN)
        main_layout.setSpacing(24)

        # Sidebar
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # Content area
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Stacked widget for sections
        self.sections_stack = QStackedWidget()
        content_layout.addWidget(self.sections_stack)

        # Build all sections
        self._build_sections()

        content_scroll.setWidget(content_widget)
        main_layout.addWidget(content_scroll, 1)

    def _build_sidebar(self) -> QFrame:
        """Build sidebar with logo and navigation."""
        sidebar = QFrame()
        sidebar.setProperty("sidebar", True)
        sidebar.setFixedWidth(SIDEBAR_WIDTH)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(24, 28, 24, 24)
        layout.setSpacing(0)

        # Header with logo
        header = self._build_sidebar_header()
        layout.addWidget(header)

        # Divider
        divider = QFrame()
        divider.setProperty("divider", True)
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        layout.addSpacing(24)

        # Navigation
        nav = self._build_navigation()
        layout.addWidget(nav)

        # Spacer
        layout.addStretch()

        return sidebar

    def _build_sidebar_header(self) -> QFrame:
        """Build sidebar header with logo and branding."""
        header = QFrame()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo image
        try:
            logo_path = Path(__file__).parent.parent / "resources" / "icons" / "idle.png"
            if logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                scaled = pixmap.scaled(
                    64, 64,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self._image_refs["logo"] = scaled

                logo_label = QLabel()
                logo_label.setPixmap(scaled)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label)
                layout.addSpacing(16)
        except Exception:
            pass

        # Title
        title = QLabel("WHISPER")
        title.setStyleSheet(f"color: {COLORS['accent_primary']}; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("CHEAP")
        subtitle.setStyleSheet(f"color: {COLORS['label_secondary']}; font-size: 16px; font-weight: bold;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        return header

    def _build_navigation(self) -> QFrame:
        """Build navigation buttons."""
        nav = QFrame()
        layout = QVBoxLayout(nav)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        nav_items = [
            ("General", "  \u2699  GENERAL"),
            ("Audio", "  \u25C9  AUDIO"),
            ("Overlay", "  \u25D0  OVERLAY"),
            ("Post", "  \u2726  AI PROCESS"),
            ("History", "  \u25C8  HISTORY"),
            ("About", "  \u24D8  ABOUT"),
        ]

        for name, label in nav_items:
            btn = QPushButton(label)
            btn.setProperty("nav", True)
            btn.setFixedHeight(48)
            btn.clicked.connect(lambda checked, n=name: self._show_section(n))
            layout.addWidget(btn)
            self.nav_buttons[name] = btn

        return nav

    def _build_sections(self) -> None:
        """Build all content sections."""
        sections = [
            ("General", self._build_general),
            ("Audio", self._build_audio),
            ("Overlay", self._build_overlay),
            ("Post", self._build_post),
            ("History", self._build_history),
            ("About", self._build_about),
        ]

        for name, builder in sections:
            section = builder()
            self.section_widgets[name] = section
            self.sections_stack.addWidget(section)

    def _show_section(self, name: str) -> None:
        """Show section and update nav button states."""
        section = self.section_widgets.get(name)
        if section:
            self.sections_stack.setCurrentWidget(section)

        # Update nav button states
        for sec, btn in self.nav_buttons.items():
            is_active = sec == name
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _build_card(self, parent: QWidget, title: str) -> QFrame:
        """Create card container with title and accent bar."""
        card = QFrame(parent)
        card.setProperty("card", True)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(CARD_PADDING_H, CARD_PADDING_V, CARD_PADDING_H, CARD_PADDING_V)
        layout.setSpacing(20)

        # Title row with accent bar
        title_row = QFrame()
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(14)

        # Accent bar
        accent_bar = QFrame()
        accent_bar.setProperty("accentBar", True)
        accent_bar.setFixedSize(3, 24)
        title_layout.addWidget(accent_bar)

        # Title label
        title_label = QLabel(title.upper())
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        layout.addWidget(title_row)

        return card

    def _create_row(
        self,
        label_text: str,
        widget: QWidget,
        label_width: int = LABEL_WIDTH
    ) -> QFrame:
        """Create standardized input row."""
        row = QFrame()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Label column
        label_col = QFrame()
        label_col.setFixedWidth(label_width)
        label_layout = QHBoxLayout(label_col)
        label_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setStyleSheet("font-size: 15px; font-weight: bold;")
        label_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(label_col)
        layout.addWidget(widget, 1)

        return row

    # =========================================================================
    # SECTION BUILDERS
    # =========================================================================

    def _build_general(self) -> QWidget:
        """Build General settings section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        card = self._build_card(section, "General Settings")
        card_layout = card.layout()

        # Content container
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(ROW_SPACING)

        # Hotkey row
        hotkey_row = QFrame()
        hotkey_layout = QHBoxLayout(hotkey_row)
        hotkey_layout.setContentsMargins(0, 0, 0, 0)
        hotkey_layout.setSpacing(12)

        label_col = QFrame()
        label_col.setFixedWidth(LABEL_WIDTH)
        label_layout = QHBoxLayout(label_col)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Hotkey")
        label.setStyleSheet("font-size: 15px; font-weight: bold;")
        label_layout.addWidget(label)
        hotkey_layout.addWidget(label_col)

        hotkey_entry = QLineEdit()
        hotkey_entry.setReadOnly(True)
        hotkey_entry.setFixedHeight(INPUT_HEIGHT)
        hotkey_entry.setMinimumWidth(260)
        self.widgets["hotkey"] = hotkey_entry
        hotkey_layout.addWidget(hotkey_entry)

        capture_btn = QPushButton("RECORD")
        capture_btn.setProperty("primary", True)
        capture_btn.setFixedSize(120, INPUT_HEIGHT)
        capture_btn.clicked.connect(self._start_hotkey_capture)
        self.widgets["hotkey_btn"] = capture_btn
        hotkey_layout.addWidget(capture_btn)
        hotkey_layout.addStretch()

        content_layout.addWidget(hotkey_row)

        # Mode row
        mode_row = QFrame()
        mode_layout = QHBoxLayout(mode_row)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(12)

        label_col = QFrame()
        label_col.setFixedWidth(LABEL_WIDTH)
        label_layout = QHBoxLayout(label_col)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Mode")
        label.setStyleSheet("font-size: 15px; font-weight: bold;")
        label_layout.addWidget(label)
        mode_layout.addWidget(label_col)

        mode_group = QButtonGroup(self)
        rb_ptt = QRadioButton("Push-to-Talk")
        rb_toggle = QRadioButton("Toggle")
        mode_group.addButton(rb_ptt, 0)
        mode_group.addButton(rb_toggle, 1)
        rb_ptt.toggled.connect(lambda: self._auto_save())
        rb_toggle.toggled.connect(lambda: self._auto_save())
        self.widgets["activation_mode"] = mode_group
        self.widgets["rb_ptt"] = rb_ptt
        self.widgets["rb_toggle"] = rb_toggle

        mode_layout.addWidget(rb_ptt)
        mode_layout.addSpacing(16)
        mode_layout.addWidget(rb_toggle)
        mode_layout.addStretch()

        content_layout.addWidget(mode_row)

        # Start on boot
        cb_boot = QCheckBox("Start on Windows boot")
        cb_boot.stateChanged.connect(lambda: self._auto_save())
        self.widgets["start_on_boot"] = cb_boot
        content_layout.addWidget(cb_boot)

        # Clipboard policy
        clip_combo = QComboBox()
        clip_combo.addItems(["dont_modify", "copy_to_clipboard"])
        clip_combo.setFixedHeight(INPUT_HEIGHT)
        clip_combo.setMinimumWidth(260)
        clip_combo.currentTextChanged.connect(lambda: self._auto_save())
        self.widgets["clipboard_policy"] = clip_combo

        clip_row = self._create_row("Clipboard", clip_combo)
        content_layout.addWidget(clip_row)

        card_layout.addWidget(content)
        layout.addWidget(card)
        layout.addStretch()

        return section

    def _build_audio(self) -> QWidget:
        """Build Audio settings section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        card = self._build_card(section, "Audio Settings")
        card_layout = card.layout()

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(ROW_SPACING)

        # Microphone combo
        device_combo = QComboBox()
        device_combo.setFixedHeight(INPUT_HEIGHT)
        device_combo.setMinimumWidth(420)
        device_combo.currentTextChanged.connect(lambda: self._auto_save())
        self.widgets["device_id"] = device_combo

        device_row = self._create_row("Microphone", device_combo)
        content_layout.addWidget(device_row)

        # Hidden vars
        self.hidden_vars["use_vad"] = False
        self.hidden_vars["vad_threshold"] = 0.5
        self.hidden_vars["mute_while_recording"] = False
        self.hidden_vars["chunk_size"] = 4096

        card_layout.addWidget(content)
        layout.addWidget(card)
        layout.addStretch()

        return section

    def _build_overlay(self) -> QWidget:
        """Build Overlay settings section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        card = self._build_card(section, "Overlay Settings")
        card_layout = card.layout()

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(ROW_SPACING)

        # Enable overlay
        cb_enabled = QCheckBox("Show overlay")
        cb_enabled.stateChanged.connect(lambda: self._auto_save())
        self.widgets["overlay_enabled"] = cb_enabled
        content_layout.addWidget(cb_enabled)

        # Position
        pos_combo = QComboBox()
        pos_combo.addItems(["bottom", "top"])
        pos_combo.setFixedHeight(INPUT_HEIGHT)
        pos_combo.setMinimumWidth(260)
        pos_combo.currentTextChanged.connect(lambda: self._auto_save())
        self.widgets["overlay_position"] = pos_combo

        pos_row = self._create_row("Position", pos_combo)
        content_layout.addWidget(pos_row)

        # Opacity slider
        opacity_container = QFrame()
        opacity_layout = QHBoxLayout(opacity_container)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.setSpacing(12)

        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(50, 100)
        opacity_slider.setValue(85)
        opacity_slider.setFixedWidth(320)
        opacity_slider.valueChanged.connect(lambda: self._auto_save())
        self.widgets["overlay_opacity"] = opacity_slider

        opacity_value = QLabel("85%")
        opacity_value.setStyleSheet(f"color: {COLORS['label_secondary']};")
        opacity_value.setFixedWidth(50)
        self.widgets["overlay_opacity_label"] = opacity_value
        opacity_slider.valueChanged.connect(lambda v: opacity_value.setText(f"{v}%"))

        opacity_layout.addWidget(opacity_slider)
        opacity_layout.addWidget(opacity_value)

        opacity_row = self._create_row("Opacity", opacity_container)
        content_layout.addWidget(opacity_row)

        card_layout.addWidget(content)
        layout.addWidget(card)
        layout.addStretch()

        return section

    def _build_post(self) -> QWidget:
        """Build Post-Processing settings section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        card = self._build_card(section, "AI Post-Processing")
        card_layout = card.layout()

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(ROW_SPACING)

        # Enable AI
        cb_pp = QCheckBox("Enable AI post-processing")
        cb_pp.stateChanged.connect(lambda: self._auto_save())
        self.widgets["pp_enabled"] = cb_pp
        content_layout.addWidget(cb_pp)

        # API Key
        api_entry = QLineEdit()
        api_entry.setEchoMode(QLineEdit.EchoMode.Password)
        api_entry.setFixedHeight(INPUT_HEIGHT)
        api_entry.setMinimumWidth(420)
        api_entry.textChanged.connect(lambda: self._auto_save())
        self.widgets["pp_api_key"] = api_entry

        api_row = self._create_row("API Key", api_entry)
        content_layout.addWidget(api_row)

        # Model label
        model_label = QLabel("Model")
        model_label.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 8px;")
        content_layout.addWidget(model_label)

        # Filter row
        filter_row = QFrame()
        filter_layout = QHBoxLayout(filter_row)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(12)

        search_entry = QLineEdit()
        search_entry.setPlaceholderText("Filter models...")
        search_entry.setFixedHeight(40)
        search_entry.setFixedWidth(240)
        search_entry.textChanged.connect(self._filter_models)
        self.widgets["model_search"] = search_entry
        filter_layout.addWidget(search_entry)

        reset_btn = QPushButton("RESET")
        reset_btn.setFixedSize(100, 40)
        reset_btn.clicked.connect(self._reset_models)
        filter_layout.addWidget(reset_btn)

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setFixedSize(100, 40)
        refresh_btn.clicked.connect(self._refresh_models_async)
        filter_layout.addWidget(refresh_btn)

        filter_layout.addStretch()
        content_layout.addWidget(filter_row)

        # Model list scroll area
        model_scroll = QScrollArea()
        model_scroll.setWidgetResizable(True)
        model_scroll.setFixedHeight(200)
        model_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        model_scroll.setStyleSheet("QScrollArea { background-color: #0f0f0f; border-radius: 12px; border: 1px solid #262626; }")

        model_list = QWidget()
        model_list_layout = QVBoxLayout(model_list)
        model_list_layout.setContentsMargins(4, 4, 4, 4)
        model_list_layout.setSpacing(4)
        model_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        model_scroll.setWidget(model_list)
        self.widgets["model_list_container"] = model_list

        content_layout.addWidget(model_scroll)

        # Status label
        status_label = QLabel("Model list: default")
        status_label.setStyleSheet(f"color: {COLORS['label_tertiary']}; font-size: 11px;")
        self.widgets["model_status"] = status_label
        content_layout.addWidget(status_label)

        # Test connection row
        test_row = QFrame()
        test_layout = QHBoxLayout(test_row)
        test_layout.setContentsMargins(0, 0, 0, 0)
        test_layout.setSpacing(12)

        test_btn = QPushButton("TEST CONNECTION")
        test_btn.setFixedSize(160, 44)
        test_btn.clicked.connect(self._test_llm_connection)
        test_layout.addWidget(test_btn)

        test_status = QLabel("")
        test_status.setStyleSheet(f"color: {COLORS['label_secondary']}; font-size: 11px;")
        self.widgets["test_status"] = test_status
        test_layout.addWidget(test_status, 1)

        content_layout.addWidget(test_row)

        # Add model row
        add_row = QFrame()
        add_layout = QHBoxLayout(add_row)
        add_layout.setContentsMargins(0, 0, 0, 0)
        add_layout.setSpacing(12)

        add_entry = QLineEdit()
        add_entry.setPlaceholderText("vendor/model-name")
        add_entry.setFixedHeight(44)
        add_entry.setMinimumWidth(420)
        self.widgets["add_model"] = add_entry
        add_layout.addWidget(add_entry)

        add_btn = QPushButton("+ ADD MODEL")
        add_btn.setProperty("primary", True)
        add_btn.setFixedSize(140, 44)
        add_btn.clicked.connect(self._add_model)
        add_layout.addWidget(add_btn)
        add_layout.addStretch()

        content_layout.addWidget(add_row)

        card_layout.addWidget(content)
        layout.addWidget(card)
        layout.addStretch()

        return section

    def _build_history(self) -> QWidget:
        """Build History section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Toolbar
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(12)

        title = QLabel("RECENT TRANSCRIPTIONS")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        toolbar_layout.addWidget(title)
        toolbar_layout.addStretch()

        open_btn = QPushButton("OPEN FOLDER")
        open_btn.setFixedSize(140, 44)
        open_btn.clicked.connect(self._open_recordings_folder)
        toolbar_layout.addWidget(open_btn)

        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setProperty("primary", True)
        refresh_btn.setFixedSize(140, 44)
        refresh_btn.clicked.connect(self._refresh_history)
        toolbar_layout.addWidget(refresh_btn)

        layout.addWidget(toolbar)

        # History scroll area
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.setSpacing(12)
        history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        history_scroll.setWidget(history_widget)
        self.widgets["history_container"] = history_widget

        layout.addWidget(history_scroll, 1)

        return section

    def _build_about(self) -> QWidget:
        """Build About section."""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        card = self._build_card(section, "About")
        card_layout = card.layout()

        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        # Title
        title = QLabel("Whisper Cheap")
        title.setStyleSheet(f"color: {COLORS['accent_primary']}; font-size: 28px; font-weight: bold;")
        content_layout.addWidget(title)

        # Version
        version = QLabel("Version 1.0.0")
        version.setStyleSheet(f"color: {COLORS['label_secondary']};")
        content_layout.addWidget(version)

        # Description
        desc = QLabel("Local voice transcription powered by Parakeet V3")
        desc.setStyleSheet(f"color: {COLORS['label_tertiary']};")
        content_layout.addWidget(desc)

        content_layout.addSpacing(20)

        # Action buttons
        btn_row = QFrame()
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(16)

        data_btn = QPushButton("OPEN DATA FOLDER")
        data_btn.setProperty("primary", True)
        data_btn.setFixedSize(220, INPUT_HEIGHT)
        data_btn.clicked.connect(self._open_app_data_folder)
        btn_layout.addWidget(data_btn)

        rec_btn = QPushButton("OPEN RECORDINGS")
        rec_btn.setProperty("primary", True)
        rec_btn.setFixedSize(220, INPUT_HEIGHT)
        rec_btn.clicked.connect(self._open_recordings_folder)
        btn_layout.addWidget(rec_btn)
        btn_layout.addStretch()

        content_layout.addWidget(btn_row)

        card_layout.addWidget(content)
        layout.addWidget(card)
        layout.addStretch()

        return section

    # =========================================================================
    # DATA METHODS
    # =========================================================================

    def _populate(self) -> None:
        """Load config values into widgets."""
        d = self.data
        general = d.get("general", {})
        mode = d.get("mode", {})
        audio = d.get("audio", {})
        clip = d.get("clipboard", {})
        overlay = d.get("overlay", {})
        pp = d.get("post_processing", {})

        # General
        self.widgets["hotkey"].setText(d.get("hotkey", "ctrl+shift+space"))

        activation = mode.get("activation_mode", "toggle")
        if activation == "ptt":
            self.widgets["rb_ptt"].setChecked(True)
        else:
            self.widgets["rb_toggle"].setChecked(True)

        self.widgets["start_on_boot"].setChecked(bool(general.get("start_on_boot", False)))

        policy = clip.get("policy", "dont_modify")
        idx = self.widgets["clipboard_policy"].findText(policy)
        if idx >= 0:
            self.widgets["clipboard_policy"].setCurrentIndex(idx)

        # Audio
        self._refresh_devices()
        device = audio.get("device_id")
        if device is None:
            self.widgets["device_id"].setCurrentText("Default")
        else:
            combo = self.widgets["device_id"]
            for i in range(combo.count()):
                if combo.itemText(i).startswith(str(device)):
                    combo.setCurrentIndex(i)
                    break

        # Hidden vars
        self.hidden_vars["use_vad"] = audio.get("use_vad", False)
        self.hidden_vars["vad_threshold"] = audio.get("vad_threshold", 0.5)
        self.hidden_vars["mute_while_recording"] = audio.get("mute_while_recording", False)
        self.hidden_vars["chunk_size"] = audio.get("chunk_size", 4096)

        # Overlay
        self.widgets["overlay_enabled"].setChecked(bool(overlay.get("enabled", True)))

        pos = overlay.get("position", "bottom")
        idx = self.widgets["overlay_position"].findText(pos)
        if idx >= 0:
            self.widgets["overlay_position"].setCurrentIndex(idx)

        opacity_val = int(overlay.get("opacity", 0.85) * 100)
        self.widgets["overlay_opacity"].setValue(opacity_val)

        # Post-processing
        self.widgets["pp_enabled"].setChecked(bool(pp.get("enabled", False)))
        self.widgets["pp_api_key"].setText(pp.get("openrouter_api_key", ""))
        self.current_model = pp.get("model", "")
        self.user_models = list(pp.get("custom_models", []))

        self._set_model_options(self.user_models + self.default_models)
        self._refresh_history()

    def _refresh_devices(self) -> None:
        """Populate microphone combo with available input devices."""
        devices = ["Default"]
        if sd:
            try:
                devs = sd.query_devices()
                devices += [
                    f"{i}: {d['name']}"
                    for i, d in enumerate(devs)
                    if d.get("max_input_channels", 0) > 0
                ]
            except Exception:
                pass

        combo = self.widgets["device_id"]
        current = combo.currentText()
        combo.clear()
        combo.addItems(devices)

        if current and current in devices:
            combo.setCurrentText(current)
        else:
            combo.setCurrentIndex(0)

    # =========================================================================
    # AUTO-SAVE
    # =========================================================================

    def _auto_save(self) -> None:
        """Trigger debounced auto-save."""
        if self._save_timer and self._save_timer.isActive():
            self._save_timer.stop()

        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_config_silent)
        self._save_timer.start(500)

    def _save_config_silent(self) -> None:
        """Save config without user feedback."""
        try:
            d = self.data

            # General
            d["hotkey"] = self.widgets["hotkey"].text().strip() or "ctrl+shift+space"

            general = d.setdefault("general", {})
            general["start_on_boot"] = self.widgets["start_on_boot"].isChecked()

            # Mode
            mode_group = self.widgets["activation_mode"]
            mode_val = "ptt" if mode_group.button(0).isChecked() else "toggle"
            d.setdefault("mode", {})["activation_mode"] = mode_val

            # Audio
            audio = d.setdefault("audio", {})
            dev_text = self.widgets["device_id"].currentText().strip()
            if dev_text.lower() == "default" or not dev_text:
                audio["device_id"] = None
            elif ":" in dev_text and dev_text.split(":")[0].strip().isdigit():
                audio["device_id"] = int(dev_text.split(":")[0].strip())
            else:
                audio["device_id"] = dev_text

            audio["use_vad"] = self.hidden_vars.get("use_vad", False)
            audio["vad_threshold"] = self.hidden_vars.get("vad_threshold", 0.5)
            audio["mute_while_recording"] = self.hidden_vars.get("mute_while_recording", False)
            audio["chunk_size"] = self.hidden_vars.get("chunk_size", 4096)

            # Clipboard
            clip = d.setdefault("clipboard", {})
            clip["paste_method"] = "ctrl_v"
            clip["policy"] = self.widgets["clipboard_policy"].currentText() or "dont_modify"

            # Overlay
            overlay = d.setdefault("overlay", {})
            overlay["enabled"] = self.widgets["overlay_enabled"].isChecked()
            overlay["position"] = self.widgets["overlay_position"].currentText() or "bottom"
            overlay["opacity"] = self.widgets["overlay_opacity"].value() / 100.0

            # Post-processing
            pp = d.setdefault("post_processing", {})
            pp["enabled"] = self.widgets["pp_enabled"].isChecked()
            pp["openrouter_api_key"] = self.widgets["pp_api_key"].text().strip()
            pp["model"] = self.current_model
            pp["prompt_template"] = "Transcript:\n${output}"
            pp["custom_models"] = list(self.user_models)

            _save_config(self.config_path, d)

        except Exception as e:
            print(f"[settings] Error saving config: {e}")

    # =========================================================================
    # HOTKEY CAPTURE
    # =========================================================================

    def _start_hotkey_capture(self) -> None:
        """Start hotkey capture mode."""
        if self.capturing_hotkey:
            return

        self.capturing_hotkey = True
        self.captured_keys = []
        self.widgets["hotkey"].setText("Press keys...")
        self.widgets["hotkey_btn"].setText("...")
        self.widgets["hotkey_btn"].setProperty("primary", False)
        self.widgets["hotkey_btn"].style().unpolish(self.widgets["hotkey_btn"])
        self.widgets["hotkey_btn"].style().polish(self.widgets["hotkey_btn"])

        self.grabKeyboard()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press during hotkey capture."""
        if not self.capturing_hotkey:
            super().keyPressEvent(event)
            return

        key = event.key()
        key_name = ""

        # Map keys
        if key == Qt.Key.Key_Control:
            key_name = "ctrl"
        elif key == Qt.Key.Key_Shift:
            key_name = "shift"
        elif key == Qt.Key.Key_Alt:
            key_name = "alt"
        elif key == Qt.Key.Key_Meta:
            key_name = "win"
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self._confirm_hotkey()
            return
        elif key == Qt.Key.Key_Escape:
            self._cancel_hotkey_capture()
            return
        else:
            key_name = event.text().lower() if event.text() else ""
            if not key_name:
                # Try to get key name from Qt
                try:
                    from PyQt6.QtCore import QKeyCombination
                    key_name = QKeyCombination(key).key().name.lower().replace("key_", "")
                except Exception:
                    pass

        if key_name and key_name not in self.captured_keys:
            self.captured_keys.append(key_name)

        hotkey_str = "+".join(self.captured_keys)
        self.widgets["hotkey"].setText(hotkey_str)

    def _confirm_hotkey(self) -> None:
        """Confirm captured hotkey."""
        self.capturing_hotkey = False
        self.releaseKeyboard()

        if self.captured_keys:
            hotkey_str = "+".join(self.captured_keys)
            self.widgets["hotkey"].setText(hotkey_str)
            self._auto_save()
        else:
            self.widgets["hotkey"].setText(self.data.get("hotkey", "ctrl+shift+space"))

        self.widgets["hotkey_btn"].setText("RECORD")
        self.widgets["hotkey_btn"].setProperty("primary", True)
        self.widgets["hotkey_btn"].style().unpolish(self.widgets["hotkey_btn"])
        self.widgets["hotkey_btn"].style().polish(self.widgets["hotkey_btn"])

    def _cancel_hotkey_capture(self) -> None:
        """Cancel hotkey capture."""
        self.capturing_hotkey = False
        self.releaseKeyboard()
        self.captured_keys = []
        self.widgets["hotkey"].setText(self.data.get("hotkey", "ctrl+shift+space"))
        self.widgets["hotkey_btn"].setText("RECORD")
        self.widgets["hotkey_btn"].setProperty("primary", True)
        self.widgets["hotkey_btn"].style().unpolish(self.widgets["hotkey_btn"])
        self.widgets["hotkey_btn"].style().polish(self.widgets["hotkey_btn"])

    # =========================================================================
    # MODEL MANAGEMENT
    # =========================================================================

    def _set_model_options(self, options: List[str], status: Optional[str] = None) -> None:
        """Set model options and re-render list."""
        opts = [o for o in options if o]
        if not opts:
            opts = list(self.default_models)

        seen: set = set()
        deduped: List[str] = []
        for o in opts:
            if o not in seen:
                seen.add(o)
                deduped.append(o)

        combined = self.default_models + [m for m in self.user_models if m not in self.default_models]
        self.model_all = combined or list(self.default_models)
        self._filter_models(self.widgets["model_search"].text(), status_override=status)

    def _filter_models(self, query: str = "", status_override: Optional[str] = None) -> None:
        """Filter model list by search query."""
        q = (query or "").strip().lower()
        all_models = self.model_all or list(self.default_models)
        filtered = [m for m in all_models if q in m.lower()] if q else list(all_models)
        filtered = filtered[:MAX_MODELS_SHOWN]
        self.model_options = filtered or list(self.default_models)

        total = len(all_models)
        shown = len(self.model_options)
        summary = status_override or f"Modelos cargados: {total}, mostrando {shown}"
        if q:
            summary += f" (filtro: {q})"
        self.widgets["model_status"].setText(summary)

        self._render_model_list()

    def _render_model_list(self) -> None:
        """Re-render model cards."""
        container = self.widgets["model_list_container"]
        layout = container.layout()

        # Clear existing
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        active = self.current_model

        for model_id in self.model_options:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #0a0a0a; border-radius: 8px; }")

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 8, 6)
            card_layout.setSpacing(8)

            label = QLabel(model_id)
            label.setStyleSheet(f"color: {'#ffffff' if model_id == active else '#707070'}; font-size: 12px;")
            card_layout.addWidget(label, 1)

            select_btn = QPushButton("SELECT" if model_id != active else "SELECTED")
            select_btn.setFixedSize(80, 28)
            if model_id != active:
                select_btn.setProperty("primary", True)
            select_btn.clicked.connect(lambda checked, m=model_id: self._select_model(m))
            card_layout.addWidget(select_btn)

            if model_id in self.user_models:
                del_btn = QPushButton("DELETE")
                del_btn.setProperty("danger", True)
                del_btn.setFixedSize(70, 28)
                del_btn.clicked.connect(lambda checked, m=model_id: self._delete_model(m))
                card_layout.addWidget(del_btn)

            layout.addWidget(card)

    def _select_model(self, model_id: str) -> None:
        """Select a model as active."""
        self.current_model = model_id
        self._auto_save()
        self._render_model_list()

    def _delete_model(self, model_id: str) -> None:
        """Delete a user model."""
        if model_id in self.user_models:
            self.user_models = [m for m in self.user_models if m != model_id]
            if self.current_model == model_id:
                fallback = self.default_models[0] if self.default_models else ""
                self.current_model = fallback
            self._set_model_options(self.user_models + self.default_models, "Modelo eliminado.")
            self._auto_save()

    def _reset_models(self) -> None:
        """Reset to default models."""
        self.user_models = []
        if self.default_models:
            self.current_model = self.default_models[0]
        self._set_model_options(self.default_models, "Lista restaurada.")
        self._auto_save()

    def _refresh_models_async(self) -> None:
        """Refresh models (curated list)."""
        status = f"Modelos cargados: {len(self.default_models)} (lista limitada)"
        self._set_model_options(list(self.default_models), status=status)

    def _add_model(self) -> None:
        """Add a new model."""
        model_id = self.widgets["add_model"].text().strip()
        if not model_id:
            QMessageBox.warning(self, "Modelo vacio", "Introduce el ID del modelo (por ejemplo vendor/model).")
            return

        if model_id in self.default_models or model_id in self.user_models:
            QMessageBox.information(self, "Modelo existente", "Ese modelo ya esta en la lista.")
            return

        # Add without testing for now
        self.user_models.append(model_id)
        self.current_model = model_id
        self._set_model_options(self.user_models + self.default_models, "Modelo agregado.")
        self._auto_save()
        self.widgets["add_model"].setText("")

    def _test_llm_connection(self) -> None:
        """Test OpenRouter connection."""
        key = self.widgets["pp_api_key"].text().strip()
        model = self.current_model.strip()

        if not key:
            QMessageBox.warning(self, "Missing API key", "Agrega tu OpenRouter API key antes de probar.")
            return

        if not model:
            QMessageBox.warning(self, "Missing model", "Selecciona un modelo antes de probar.")
            return

        if requests is None:
            QMessageBox.critical(self, "requests no disponible", "Instala 'requests' para probar la conexion.")
            return

        self.widgets["test_status"].setText("Testing...")

        def worker():
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {key}",
                    "HTTP-Referer": "https://github.com/whisper-cheap/whisper-cheap",
                    "X-Title": "Whisper Cheap",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": LLM_SYSTEM_PROMPT},
                        {"role": "user", "content": "Transcript:\nHello, this is a connectivity test."},
                    ],
                }

                resp = requests.post(url, headers=headers, json=payload, timeout=15)
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

                data = resp.json()
                choices = data.get("choices") if isinstance(data, dict) else None
                text = ""
                if choices and isinstance(choices, list) and choices[0].get("message"):
                    text = choices[0]["message"].get("content") or ""

                status = f"OK ({len(text)} chars)" if text else "Respuesta vacia"
                sample = (text[:120] + "...") if text and len(text) > 120 else text

                self._run_on_ui(lambda: self._on_test_success(status, sample))

            except Exception as exc:
                self._run_on_ui(lambda: self._on_test_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_test_success(self, status: str, sample: str) -> None:
        """Handle successful LLM test."""
        self.widgets["test_status"].setText(status)
        if sample:
            QMessageBox.information(self, "Test exitoso", f"Snippet del LLM:\n{sample}")

    def _on_test_error(self, error: str) -> None:
        """Handle failed LLM test."""
        self.widgets["test_status"].setText("Failed")
        QMessageBox.critical(self, "Test fallido", error)

    # =========================================================================
    # HISTORY
    # =========================================================================

    def _refresh_history(self) -> None:
        """Refresh history cards."""
        container = self.widgets.get("history_container")
        if not container:
            return

        layout = container.layout()

        # Clear existing
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.history_manager:
            empty_label = QLabel("(Historial no disponible)")
            empty_label.setStyleSheet(f"color: {COLORS['label_tertiary']}; padding: 40px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty_label)
            return

        try:
            entries = self.history_manager.get_all(limit=20)
            if not entries:
                empty_label = QLabel("No hay transcripciones todavia.\nGraba algo con el hotkey para comenzar.")
                empty_label.setStyleSheet(f"color: {COLORS['label_tertiary']}; padding: 40px;")
                empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(empty_label)
            else:
                for entry in entries:
                    card = self._create_history_card(entry)
                    layout.addWidget(card)
        except Exception as e:
            error_label = QLabel(f"Error al cargar historial:\n{e}")
            error_label.setStyleSheet(f"color: {COLORS['accent_primary']}; padding: 40px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)

    def _create_history_card(self, entry: Dict[str, Any]) -> QFrame:
        """Create history card widget."""
        card = QFrame()
        card.setProperty("card", True)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        ts = entry.get("timestamp", 0)
        dt_str = datetime.fromtimestamp(ts).strftime("%B %d, %Y at %I:%M %p") if ts else "Unknown date"
        timestamp = QLabel(dt_str)
        timestamp.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(timestamp)
        header_layout.addStretch()

        copy_btn = QPushButton("COPY")
        copy_btn.setFixedSize(60, 32)
        copy_btn.clicked.connect(lambda: self._copy_transcription(entry))
        header_layout.addWidget(copy_btn)

        del_btn = QPushButton("DEL")
        del_btn.setProperty("danger", True)
        del_btn.setFixedSize(50, 32)
        del_btn.clicked.connect(lambda: self._delete_entry(entry))
        header_layout.addWidget(del_btn)

        card_layout.addWidget(header)

        # Text
        text = entry.get("transcription_text", "")
        if text:
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setStyleSheet(f"color: {COLORS['label_tertiary']}; font-style: italic; font-size: 13px;")
            card_layout.addWidget(text_label)

        # Audio player placeholder
        audio_path = entry.get("audio_path", "")
        if audio_path and Path(audio_path).exists():
            player = QFrame()
            player.setStyleSheet(f"background-color: {COLORS['bg_tertiary']}; border-radius: 8px;")
            player.setFixedHeight(48)

            player_layout = QHBoxLayout(player)
            player_layout.setContentsMargins(12, 8, 12, 8)
            player_layout.setSpacing(12)

            play_btn = QPushButton("PLAY")
            play_btn.setProperty("primary", True)
            play_btn.setFixedSize(60, 32)
            play_btn.clicked.connect(lambda: self._play_audio(audio_path))
            player_layout.addWidget(play_btn)

            progress = QProgressBar()
            progress.setFixedHeight(4)
            progress.setValue(0)
            player_layout.addWidget(progress, 1)

            try:
                import wave
                with wave.open(audio_path, 'r') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
                    duration_str = f"0:00 / {int(duration//60)}:{int(duration%60):02d}"
            except Exception:
                duration_str = "0:00 / 0:00"

            duration_label = QLabel(duration_str)
            duration_label.setStyleSheet(f"color: {COLORS['label_tertiary']}; font-size: 9px;")
            player_layout.addWidget(duration_label)

            card_layout.addWidget(player)

        return card

    def _copy_transcription(self, entry: Dict[str, Any]) -> None:
        """Copy transcription to clipboard."""
        text = entry.get("transcription_text", "")
        if text:
            try:
                from PyQt6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
            except Exception:
                pass

    def _delete_entry(self, entry: Dict[str, Any]) -> None:
        """Delete history entry."""
        # TODO: Implement with confirmation
        pass

    def _play_audio(self, audio_path: str) -> None:
        """Play audio file."""
        try:
            if sys.platform == "win32":
                os.startfile(audio_path)
        except Exception:
            pass

    # =========================================================================
    # FOLDER ACTIONS
    # =========================================================================

    def _open_recordings_folder(self) -> None:
        """Open recordings folder."""
        try:
            recordings_path = self.config_path.parent / ".data" / "recordings"
            if not recordings_path.exists():
                paths_config = self.data.get("paths", {})
                app_data = paths_config.get("app_data", ".data")
                app_data = os.path.expandvars(app_data)
                recordings_path = Path(app_data) / "recordings"

            if recordings_path.exists():
                if sys.platform == "win32":
                    os.startfile(str(recordings_path))
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(recordings_path)])
                else:
                    subprocess.run(["xdg-open", str(recordings_path)])
            else:
                QMessageBox.warning(self, "Carpeta no encontrada", f"La carpeta no existe:\n{recordings_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir:\n{e}")

    def _open_app_data_folder(self) -> None:
        """Open app data folder."""
        try:
            paths_config = self.data.get("paths", {})
            app_data = paths_config.get("app_data", ".data")
            app_data = os.path.expandvars(app_data)
            app_data_path = self.config_path.parent / app_data if not Path(app_data).is_absolute() else Path(app_data)

            if app_data_path.exists():
                if sys.platform == "win32":
                    os.startfile(str(app_data_path))
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(app_data_path)])
                else:
                    subprocess.run(["xdg-open", str(app_data_path)])
            else:
                QMessageBox.warning(self, "Carpeta no encontrada", f"La carpeta no existe:\n{app_data_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir:\n{e}")

    # =========================================================================
    # WINDOW EVENTS
    # =========================================================================

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close."""
        try:
            self._save_config_silent()

            if self._save_timer and self._save_timer.isActive():
                self._save_timer.stop()

            self.widgets.clear()
            self.hidden_vars.clear()

        except Exception as e:
            print(f"[settings] Cleanup error: {e}")
        finally:
            event.accept()


# =============================================================================
# PUBLIC API
# =============================================================================

def open_settings_window(config_path: Path, history_manager=None) -> Optional[SettingsWindow]:
    """
    Open settings window (non-blocking).

    Args:
        config_path: Path to config.json
        history_manager: Optional history manager

    Returns:
        SettingsWindow instance or None if PyQt6 not available
    """
    if not PYQT6_AVAILABLE:
        print("[settings] PyQt6 not available")
        return None

    try:
        window = SettingsWindow(config_path, history_manager)
        window.show()
        return window
    except Exception as e:
        print(f"[settings] Failed to open window: {e}")
        return None


# Global reference to keep window alive
_settings_window: Optional[SettingsWindow] = None


def open_modern_settings(config_path: Path, history_manager=None) -> None:
    """
    Open settings window (non-blocking, main thread).

    PyQt6 widgets MUST be created on the main thread where QApplication runs.
    Unlike CustomTkinter, we cannot use threading.Thread for Qt widgets.
    """
    global _settings_window

    if not PYQT6_AVAILABLE:
        print("[settings] PyQt6 not available")
        return

    try:
        # If window exists and is visible, just raise it
        if _settings_window is not None:
            try:
                if _settings_window.isVisible():
                    _settings_window.raise_()
                    _settings_window.activateWindow()
                    return
            except RuntimeError:
                # Window was deleted
                _settings_window = None

        # Create new window on main thread
        _settings_window = SettingsWindow(config_path, history_manager)
        _settings_window.show()

    except Exception as e:
        print(f"[settings] Failed to open window: {e}")
        import traceback
        traceback.print_exc()
