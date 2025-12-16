"""
Settings UI helper utilities and functions.

Config I/O, LLM constants, and UI builder functions for settings window.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    QWidget = None  # type: ignore
    QFrame = None  # type: ignore

from src.ui.settings_style import CARD_PADDING_H, CARD_PADDING_V, LABEL_WIDTH

# =============================================================================
# LLM CONSTANTS
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

MAX_MODELS_SHOWN: int = 50
DEFAULT_MODELS_PATH: Path = Path(__file__).resolve().parent.parent / "resources" / "models_default.json"

# =============================================================================
# CONFIG I/O
# =============================================================================

def load_config(path: Path) -> Dict[str, Any]:
    """Load config from JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(path: Path, data: Dict[str, Any]) -> None:
    """Save config to JSON file."""
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_default_models(path: Path, fallback: List[str]) -> List[str]:
    """Load default models from JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(x) for x in data if x]
    except Exception:
        pass
    return list(fallback)


# =============================================================================
# UI BUILDER FUNCTIONS
# =============================================================================

def build_card(parent: QWidget, title: str) -> QFrame:
    """
    Create card container with title and accent bar.

    Args:
        parent: Parent widget
        title: Card title (will be uppercased)

    Returns:
        QFrame configured as a card with title
    """
    if not PYQT6_AVAILABLE:
        raise RuntimeError("PyQt6 is not available")

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


def create_row(
    label_text: str,
    widget: QWidget,
    label_width: int = LABEL_WIDTH
) -> QFrame:
    """
    Create standardized input row with label and widget.

    Args:
        label_text: Label text
        widget: Input widget
        label_width: Fixed width for label column (default: LABEL_WIDTH)

    Returns:
        QFrame containing label and widget in horizontal layout
    """
    if not PYQT6_AVAILABLE:
        raise RuntimeError("PyQt6 is not available")

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
