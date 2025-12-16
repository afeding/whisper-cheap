"""
Settings manager and a minimal SettingsWindow (PyQt6) with core tabs.

Tabs included (lightweight):
- General: hotkey mode (PTT/Toggle), show overlay checkbox.
- Post-processing: enable, API key, model, prompt template, test button (placeholder).
- Overlay: position (top/bottom) and opacity slider.

The UI is intentionally simple to satisfy checklist; real app wiring should
connect signals/slots to running services.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from PyQt6 import QtCore, QtWidgets
except ImportError:  # pragma: no cover - optional dependency
    QtCore = None
    QtWidgets = None


class SettingsManager:
    def __init__(self, path: Path | str = "config.json") -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def update_post_processing(
        self,
        enabled: Optional[bool] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        prompt_template: Optional[str] = None,
    ) -> Dict[str, Any]:
        data = self.load()
        pp = data.setdefault("post_processing", {})
        if enabled is not None:
            pp["enabled"] = enabled
        if api_key is not None:
            pp["openrouter_api_key"] = api_key
        if model is not None:
            pp["model"] = model
        if prompt_template is not None:
            pp["prompt_template"] = prompt_template
        self.save(data)
        return data


class SettingsWindow(QtWidgets.QDialog if QtWidgets else object):
    def __init__(self, manager: SettingsManager):
        if QtWidgets is None:
            raise RuntimeError("PyQt6 is required for SettingsWindow")
        super().__init__()
        self.manager = manager
        self.setWindowTitle("Whisper Cheap Settings")
        self.setMinimumWidth(480)
        self.tabs = QtWidgets.QTabWidget()
        self._init_general_tab()
        self._init_post_tab()
        self._init_overlay_tab()

        btn_save = QtWidgets.QPushButton("Save")
        btn_save.clicked.connect(self._save)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(btn_save)
        self.setLayout(layout)

        self._load_config()

    # ---- Tabs ----
    def _init_general_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        self.hotkey_mode = QtWidgets.QComboBox()
        self.hotkey_mode.addItems(["ptt", "toggle"])
        self.show_overlay = QtWidgets.QCheckBox("Show overlay")
        layout.addRow("Hotkey mode", self.hotkey_mode)
        layout.addRow(self.show_overlay)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "General")

    def _init_post_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        self.pp_enabled = QtWidgets.QCheckBox("Enable LLM post-processing")
        self.api_key = QtWidgets.QLineEdit()
        self.api_key.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.model = QtWidgets.QLineEdit()
        self.prompt = QtWidgets.QPlainTextEdit()
        self.prompt.setPlaceholderText("${output}")
        self.test_btn = QtWidgets.QPushButton("Test")
        # Placeholder: connect to external handler later
        layout.addRow(self.pp_enabled)
        layout.addRow("API Key", self.api_key)
        layout.addRow("Model", self.model)
        layout.addRow("Prompt", self.prompt)
        layout.addRow(self.test_btn)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Post-processing")

    def _init_overlay_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        self.overlay_position = QtWidgets.QComboBox()
        self.overlay_position.addItems(["bottom", "top"])
        self.overlay_opacity = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.overlay_opacity.setRange(50, 100)  # 0.5 - 1.0
        layout.addRow("Position", self.overlay_position)
        layout.addRow("Opacity", self.overlay_opacity)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Overlay")

    # ---- Load/Save ----
    def _load_config(self):
        data = self.manager.load()
        mode = data.get("mode", {})
        pp = data.get("post_processing", {})
        overlay = data.get("overlay", {})

        if mode.get("microphone_mode") in ("ptt", "toggle"):
            self.hotkey_mode.setCurrentText(mode["microphone_mode"])
        self.show_overlay.setChecked(bool(overlay.get("enabled", True)))

        self.pp_enabled.setChecked(bool(pp.get("enabled", False)))
        self.api_key.setText(pp.get("openrouter_api_key", ""))
        self.model.setText(pp.get("model", ""))
        self.prompt.setPlainText(pp.get("prompt_template", "${output}"))

        pos = overlay.get("position", "bottom")
        self.overlay_position.setCurrentText(pos if pos in ("top", "bottom") else "bottom")
        op = overlay.get("opacity", 0.85)
        self.overlay_opacity.setValue(int(op * 100))

    def _save(self):
        data = self.manager.load()
        data.setdefault("mode", {})["microphone_mode"] = self.hotkey_mode.currentText()
        data.setdefault("overlay", {})["enabled"] = self.show_overlay.isChecked()
        data["overlay"]["position"] = self.overlay_position.currentText()
        data["overlay"]["opacity"] = self.overlay_opacity.value() / 100.0
        pp = data.setdefault("post_processing", {})
        pp["enabled"] = self.pp_enabled.isChecked()
        pp["openrouter_api_key"] = self.api_key.text()
        pp["model"] = self.model.text()
        pp["prompt_template"] = self.prompt.toPlainText()
        self.manager.save(data)
