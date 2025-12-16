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
        QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
        QLineEdit, QComboBox, QCheckBox, QRadioButton, QSlider,
        QVBoxLayout, QHBoxLayout, QScrollArea, QStackedWidget,
        QButtonGroup, QMessageBox, QProgressBar, QSizePolicy
    )
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

try:
    from src.ui.overlay import ensure_app, _get_invoker
except ImportError:
    ensure_app = None
    _get_invoker = None

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import requests
except ImportError:
    requests = None

from src.ui.settings_style import (
    COLORS, WINDOW_MARGIN, SIDEBAR_WIDTH, CARD_PADDING_H,
    CARD_PADDING_V, ROW_SPACING, LABEL_WIDTH, INPUT_HEIGHT, STYLESHEET
)
from src.ui.settings_helpers import (
    load_config, save_config, load_default_models,
    build_card, create_row,
    LLM_SYSTEM_PROMPT, MAX_MODELS_SHOWN, DEFAULT_MODELS_PATH
)
from src.ui.settings_sections import (
    build_general_section, build_audio_section, build_overlay_section,
    build_post_section, build_history_section, build_about_section
)


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
        self.data = load_config(config_path)
        self.history_manager = history_manager

        # Load default models
        self.default_models: List[str] = load_default_models(
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
        app = QApplication.instance()
        if app and QThread.currentThread() == app.thread():
            fn()
        elif _get_invoker:
            # Use thread-safe signal instead of QTimer.singleShot
            invoker = _get_invoker()
            if invoker:
                invoker.invoke.emit(fn)
            else:
                fn()  # Fallback
        else:
            fn()  # Fallback when invoker not available

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
            ("General", build_general_section),
            ("Audio", build_audio_section),
            ("Overlay", build_overlay_section),
            ("Post", build_post_section),
            ("History", build_history_section),
            ("About", build_about_section),
        ]

        for name, builder in sections:
            section = builder(self)
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

            save_config(self.config_path, d)

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
        """Handle window close - fully destroy to prevent timer leaks."""
        global _settings_window
        try:
            self._save_config_silent()

            # Stop any active timers
            if self._save_timer:
                if self._save_timer.isActive():
                    self._save_timer.stop()
                self._save_timer.deleteLater()
                self._save_timer = None

            # Clear widget references
            self.widgets.clear()
            self.hidden_vars.clear()

            # Clear global reference
            _settings_window = None

        except Exception as e:
            print(f"[settings] Cleanup error: {e}")
        finally:
            event.accept()
            # Schedule destruction of the window
            self.deleteLater()


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
