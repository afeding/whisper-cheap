"""
Settings UI section builders.

Section builder functions for General, Audio, Overlay, Post-Processing, History, and About.
Each function builds a complete section widget for the settings window.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QWidget, QFrame, QLabel, QPushButton, QLineEdit, QComboBox,
        QCheckBox, QRadioButton, QSlider, QVBoxLayout, QHBoxLayout,
        QScrollArea, QButtonGroup
    )
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    QWidget = None  # type: ignore

if TYPE_CHECKING:
    from src.ui.settings_pyqt6 import SettingsWindow

from src.ui.settings_style import COLORS, ROW_SPACING, LABEL_WIDTH, INPUT_HEIGHT
from src.ui.settings_helpers import build_card, create_row


# =============================================================================
# SECTION BUILDERS
# =============================================================================

def build_general_section(window: "SettingsWindow") -> QWidget:
    """Build General settings section."""
    section = QWidget()
    layout = QVBoxLayout(section)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)

    card = build_card(section, "General Settings")
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
    window.widgets["hotkey"] = hotkey_entry
    hotkey_layout.addWidget(hotkey_entry)

    capture_btn = QPushButton("RECORD")
    capture_btn.setProperty("primary", True)
    capture_btn.setFixedSize(120, INPUT_HEIGHT)
    capture_btn.clicked.connect(window._start_hotkey_capture)
    window.widgets["hotkey_btn"] = capture_btn
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

    mode_group = QButtonGroup(window)
    rb_ptt = QRadioButton("Push-to-Talk")
    rb_toggle = QRadioButton("Toggle")
    mode_group.addButton(rb_ptt, 0)
    mode_group.addButton(rb_toggle, 1)
    rb_ptt.toggled.connect(lambda: window._auto_save())
    rb_toggle.toggled.connect(lambda: window._auto_save())
    window.widgets["activation_mode"] = mode_group
    window.widgets["rb_ptt"] = rb_ptt
    window.widgets["rb_toggle"] = rb_toggle

    mode_layout.addWidget(rb_ptt)
    mode_layout.addSpacing(16)
    mode_layout.addWidget(rb_toggle)
    mode_layout.addStretch()

    content_layout.addWidget(mode_row)

    # Start on boot
    cb_boot = QCheckBox("Start on Windows boot")
    cb_boot.stateChanged.connect(lambda: window._auto_save())
    window.widgets["start_on_boot"] = cb_boot
    content_layout.addWidget(cb_boot)

    # Clipboard policy
    clip_combo = QComboBox()
    clip_combo.addItems(["dont_modify", "copy_to_clipboard"])
    clip_combo.setFixedHeight(INPUT_HEIGHT)
    clip_combo.setMinimumWidth(260)
    clip_combo.currentTextChanged.connect(lambda: window._auto_save())
    window.widgets["clipboard_policy"] = clip_combo

    clip_row = create_row("Clipboard", clip_combo)
    content_layout.addWidget(clip_row)

    card_layout.addWidget(content)
    layout.addWidget(card)
    layout.addStretch()

    return section


def build_audio_section(window: "SettingsWindow") -> QWidget:
    """Build Audio settings section."""
    section = QWidget()
    layout = QVBoxLayout(section)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)

    card = build_card(section, "Audio Settings")
    card_layout = card.layout()

    content = QFrame()
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(ROW_SPACING)

    # Microphone combo
    device_combo = QComboBox()
    device_combo.setFixedHeight(INPUT_HEIGHT)
    device_combo.setMinimumWidth(420)
    device_combo.currentTextChanged.connect(lambda: window._auto_save())
    window.widgets["device_id"] = device_combo

    device_row = create_row("Microphone", device_combo)
    content_layout.addWidget(device_row)

    # Hidden vars
    window.hidden_vars["use_vad"] = False
    window.hidden_vars["vad_threshold"] = 0.5
    window.hidden_vars["mute_while_recording"] = False
    window.hidden_vars["chunk_size"] = 4096

    card_layout.addWidget(content)
    layout.addWidget(card)
    layout.addStretch()

    return section


def build_overlay_section(window: "SettingsWindow") -> QWidget:
    """Build Overlay settings section."""
    section = QWidget()
    layout = QVBoxLayout(section)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)

    card = build_card(section, "Overlay Settings")
    card_layout = card.layout()

    content = QFrame()
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(ROW_SPACING)

    # Enable overlay
    cb_enabled = QCheckBox("Show overlay")
    cb_enabled.stateChanged.connect(lambda: window._auto_save())
    window.widgets["overlay_enabled"] = cb_enabled
    content_layout.addWidget(cb_enabled)

    # Position
    pos_combo = QComboBox()
    pos_combo.addItems(["bottom", "top"])
    pos_combo.setFixedHeight(INPUT_HEIGHT)
    pos_combo.setMinimumWidth(260)
    pos_combo.currentTextChanged.connect(lambda: window._auto_save())
    window.widgets["overlay_position"] = pos_combo

    pos_row = create_row("Position", pos_combo)
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
    opacity_slider.valueChanged.connect(lambda: window._auto_save())
    window.widgets["overlay_opacity"] = opacity_slider

    opacity_value = QLabel("85%")
    opacity_value.setStyleSheet(f"color: {COLORS['label_secondary']};")
    opacity_value.setFixedWidth(50)
    window.widgets["overlay_opacity_label"] = opacity_value
    opacity_slider.valueChanged.connect(lambda v: opacity_value.setText(f"{v}%"))

    opacity_layout.addWidget(opacity_slider)
    opacity_layout.addWidget(opacity_value)

    opacity_row = create_row("Opacity", opacity_container)
    content_layout.addWidget(opacity_row)

    card_layout.addWidget(content)
    layout.addWidget(card)
    layout.addStretch()

    return section


def build_post_section(window: "SettingsWindow") -> QWidget:
    """Build Post-Processing settings section."""
    section = QWidget()
    layout = QVBoxLayout(section)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)

    card = build_card(section, "AI Post-Processing")
    card_layout = card.layout()

    content = QFrame()
    content_layout = QVBoxLayout(content)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(ROW_SPACING)

    # Enable AI
    cb_pp = QCheckBox("Enable AI post-processing")
    cb_pp.stateChanged.connect(lambda: window._auto_save())
    window.widgets["pp_enabled"] = cb_pp
    content_layout.addWidget(cb_pp)

    # API Key
    api_entry = QLineEdit()
    api_entry.setEchoMode(QLineEdit.EchoMode.Password)
    api_entry.setFixedHeight(INPUT_HEIGHT)
    api_entry.setMinimumWidth(420)
    api_entry.textChanged.connect(lambda: window._auto_save())
    window.widgets["pp_api_key"] = api_entry

    api_row = create_row("API Key", api_entry)
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
    search_entry.textChanged.connect(window._filter_models)
    window.widgets["model_search"] = search_entry
    filter_layout.addWidget(search_entry)

    reset_btn = QPushButton("RESET")
    reset_btn.setFixedSize(100, 40)
    reset_btn.clicked.connect(window._reset_models)
    filter_layout.addWidget(reset_btn)

    refresh_btn = QPushButton("REFRESH")
    refresh_btn.setFixedSize(100, 40)
    refresh_btn.clicked.connect(window._refresh_models_async)
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
    window.widgets["model_list_container"] = model_list

    content_layout.addWidget(model_scroll)

    # Status label
    status_label = QLabel("Model list: default")
    status_label.setStyleSheet(f"color: {COLORS['label_tertiary']}; font-size: 11px;")
    window.widgets["model_status"] = status_label
    content_layout.addWidget(status_label)

    # Test connection row
    test_row = QFrame()
    test_layout = QHBoxLayout(test_row)
    test_layout.setContentsMargins(0, 0, 0, 0)
    test_layout.setSpacing(12)

    test_btn = QPushButton("TEST CONNECTION")
    test_btn.setFixedSize(160, 44)
    test_btn.clicked.connect(window._test_llm_connection)
    test_layout.addWidget(test_btn)

    test_status = QLabel("")
    test_status.setStyleSheet(f"color: {COLORS['label_secondary']}; font-size: 11px;")
    window.widgets["test_status"] = test_status
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
    window.widgets["add_model"] = add_entry
    add_layout.addWidget(add_entry)

    add_btn = QPushButton("+ ADD MODEL")
    add_btn.setProperty("primary", True)
    add_btn.setFixedSize(140, 44)
    add_btn.clicked.connect(window._add_model)
    add_layout.addWidget(add_btn)
    add_layout.addStretch()

    content_layout.addWidget(add_row)

    card_layout.addWidget(content)
    layout.addWidget(card)
    layout.addStretch()

    return section


def build_history_section(window: "SettingsWindow") -> QWidget:
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
    open_btn.clicked.connect(window._open_recordings_folder)
    toolbar_layout.addWidget(open_btn)

    refresh_btn = QPushButton("REFRESH")
    refresh_btn.setProperty("primary", True)
    refresh_btn.setFixedSize(140, 44)
    refresh_btn.clicked.connect(window._refresh_history)
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
    window.widgets["history_container"] = history_widget

    layout.addWidget(history_scroll, 1)

    return section


def build_about_section(window: "SettingsWindow") -> QWidget:
    """Build About section."""
    section = QWidget()
    layout = QVBoxLayout(section)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)

    card = build_card(section, "About")
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
    data_btn.clicked.connect(window._open_app_data_folder)
    btn_layout.addWidget(data_btn)

    rec_btn = QPushButton("OPEN RECORDINGS")
    rec_btn.setProperty("primary", True)
    rec_btn.setFixedSize(220, INPUT_HEIGHT)
    rec_btn.clicked.connect(window._open_recordings_folder)
    btn_layout.addWidget(rec_btn)
    btn_layout.addStretch()

    content_layout.addWidget(btn_row)

    card_layout.addWidget(content)
    layout.addWidget(card)
    layout.addStretch()

    return section
