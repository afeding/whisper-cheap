"""
Settings UI style constants and QSS stylesheet.

iOS dark mode color system and design tokens for PyQt6 settings window.
"""

from typing import Dict

# =============================================================================
# iOS DARK MODE COLOR SYSTEM
# =============================================================================

COLORS: Dict[str, str] = {
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

WINDOW_MARGIN: int = 28
SIDEBAR_WIDTH: int = 260
CARD_PADDING_H: int = 32
CARD_PADDING_V: int = 24
ROW_SPACING: int = 16
LABEL_WIDTH: int = 180
INPUT_HEIGHT: int = 48

# =============================================================================
# QSS STYLESHEET
# =============================================================================

STYLESHEET: str = """
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
