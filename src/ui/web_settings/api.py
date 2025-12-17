"""
Settings API for pywebview.

Exposes Python methods to JavaScript via window.pywebview.api
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# LLM System prompt (from settings_helpers.py)
LLM_SYSTEM_PROMPT = (
    "You are \"Transcription 2.0\": a real-time dictation post-editor.\n\n"
    "Task:\n"
    "- Take the user's raw speech-to-text transcript and return the same content as clean written text.\n\n"
    "Absolute output rules:\n"
    "- Output ONLY the transformed text. No titles, no prefixes, no explanations, no markdown wrappers.\n"
    "- Keep the SAME language as the transcript. Do NOT translate.\n"
    "- Preserve meaning strictly. Do NOT add new ideas, facts, steps, names, or assumptions.\n"
)

DEFAULT_MODELS_PATH = Path(__file__).resolve().parent.parent.parent / "resources" / "models_default.json"
PRICING_CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "resources" / "models_pricing.json"


class SettingsAPI:
    """API class exposed to JavaScript via pywebview."""

    def __init__(self, config_path: str | Path, history_manager=None):
        # Convert string to Path if needed (for multiprocessing serialization)
        self.config_path = Path(config_path) if isinstance(config_path, str) else config_path
        self.history_manager = history_manager
        self._default_models: Optional[List[str]] = None

    # =========================================================================
    # CONFIG
    # =========================================================================

    def get_config(self) -> Dict[str, Any]:
        """Load and return config.json."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save config to JSON file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # AUDIO DEVICES
    # =========================================================================

    def get_audio_devices(self) -> List[Dict[str, Any]]:
        """List available input audio devices."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            result = []
            for i, d in enumerate(devices):
                if d.get("max_input_channels", 0) > 0:
                    result.append({
                        "id": i,
                        "name": d.get("name", f"Device {i}"),
                        "channels": d.get("max_input_channels", 0)
                    })
            return result
        except Exception as e:
            print(f"[SettingsAPI] Error getting audio devices: {e}")
            return []

    # =========================================================================
    # MODELS
    # =========================================================================

    def get_default_models(self) -> List[str]:
        """Load default models from JSON file."""
        if self._default_models is not None:
            return self._default_models

        fallback = [
            "openai/gpt-oss-20b",
            "google/gemini-2.5-flash-lite",
            "mistralai/mistral-small-3.2-24b-instruct"
        ]

        try:
            with open(DEFAULT_MODELS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._default_models = [str(x) for x in data if x]
                    return self._default_models
        except Exception:
            pass

        self._default_models = fallback
        return self._default_models

    def test_llm_connection(self, api_key: str, model: str) -> Dict[str, Any]:
        """Test LLM connection to OpenRouter."""
        if not api_key:
            return {"success": False, "error": "API key is required"}
        if not model:
            return {"success": False, "error": "Model is required"}

        try:
            import requests

            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/whisper-cheap",
                "X-Title": "Whisper Cheap",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": "Hello, this is a test."}
                ],
                "max_tokens": 50
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "success": True,
                    "response": content[:120] if content else "(empty response)",
                    "chars": len(content)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                }

        except requests.Timeout:
            return {"success": False, "error": "Connection timeout (15s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # PRICING
    # =========================================================================

    def get_model_pricing(self, model: str) -> Optional[Dict[str, float]]:
        """Get pricing for a specific model from cache. Returns {input: float, output: float} or None."""
        pricing_data = self._load_pricing_cache()
        if not pricing_data:
            return None

        model_info = pricing_data.get("models", {}).get(model)
        if model_info:
            return {
                "input": model_info.get("input", 0),
                "output": model_info.get("output", 0)
            }
        return None

    def get_all_models_pricing(self) -> Dict[str, Dict[str, float]]:
        """Get pricing for all cached models."""
        pricing_data = self._load_pricing_cache()
        return pricing_data.get("models", {}) if pricing_data else {}

    def fetch_openrouter_pricing(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Fetch all models and pricing from OpenRouter API and cache locally."""
        try:
            import requests

            headers = {
                "HTTP-Referer": "https://github.com/whisper-cheap",
                "X-Title": "Whisper Cheap",
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=15
            )

            if response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}"}

            data = response.json()
            models = data.get("data", [])

            # Extract pricing info
            pricing_dict = {}
            for model in models:
                model_id = model.get("id")
                pricing = model.get("pricing", {})

                # Pricing is in $/token in OpenRouter, convert to $/1M tokens for readability
                input_price = pricing.get("prompt")
                output_price = pricing.get("completion")

                if input_price is not None and output_price is not None:
                    try:
                        input_float = float(input_price)
                        output_float = float(output_price)

                        # Convert $/token to $/1M tokens
                        input_per_m = input_float * 1_000_000
                        output_per_m = output_float * 1_000_000

                        # Format: show value with up to 2 decimals, but handle very small values
                        input_formatted = round(input_per_m, 2) if input_per_m >= 0.01 else f"{input_per_m:.2e}"
                        output_formatted = round(output_per_m, 2) if output_per_m >= 0.01 else f"{output_per_m:.2e}"

                        pricing_dict[model_id] = {
                            "input": input_formatted,
                            "output": output_formatted
                        }
                    except (ValueError, TypeError):
                        pass

            # Save to cache
            cache_data = {
                "models": pricing_dict,
                "last_updated": datetime.utcnow().isoformat()
            }
            self._save_pricing_cache(cache_data)

            return {
                "success": True,
                "models_count": len(pricing_dict),
                "last_updated": cache_data["last_updated"]
            }

        except requests.Timeout:
            return {"success": False, "error": "Connection timeout (15s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _load_pricing_cache(self) -> Optional[Dict[str, Any]]:
        """Load pricing cache from file."""
        try:
            if PRICING_CACHE_PATH.exists():
                with open(PRICING_CACHE_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _save_pricing_cache(self, data: Dict[str, Any]) -> bool:
        """Save pricing cache to file."""
        try:
            PRICING_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(PRICING_CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    # =========================================================================
    # HISTORY
    # =========================================================================

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get transcription history."""
        if not self.history_manager:
            return []

        try:
            entries = self.history_manager.get_all(limit=limit)
            result = []
            for entry in entries:
                result.append({
                    "id": entry.get("id"),
                    "timestamp": entry.get("timestamp"),
                    "text": entry.get("transcription_text", ""),
                    "audio_path": entry.get("audio_path"),
                    "duration": self._get_audio_duration(entry.get("audio_path"))
                })
            return result
        except Exception as e:
            print(f"[SettingsAPI] Error getting history: {e}")
            return []

    def _get_audio_duration(self, audio_path: Optional[str]) -> Optional[float]:
        """Get duration of audio file in seconds."""
        if not audio_path or not os.path.exists(audio_path):
            return None
        try:
            import wave
            with wave.open(audio_path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / rate
        except Exception:
            return None

    def copy_to_clipboard(self, text: str) -> Dict[str, Any]:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def play_audio(self, path: str) -> Dict[str, Any]:
        """Play audio file with system default player."""
        if not path or not os.path.exists(path):
            return {"success": False, "error": "File not found"}

        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=True)
            else:
                subprocess.run(["xdg-open", path], check=True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_history_entry(self, entry_id: int) -> Dict[str, Any]:
        """Delete a history entry."""
        if not self.history_manager:
            return {"success": False, "error": "History manager not available"}

        try:
            self.history_manager.delete(entry_id)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # FOLDERS
    # =========================================================================

    def open_folder(self, folder_type: str) -> Dict[str, Any]:
        """Open data or recordings folder."""
        try:
            config = self.get_config()
            app_data = config.get("paths", {}).get("app_data", ".data")
            app_data = os.path.expandvars(app_data)

            # Resolve relative paths
            if not os.path.isabs(app_data):
                app_data = str(self.config_path.parent / app_data)

            if folder_type == "recordings":
                folder = os.path.join(app_data, "recordings")
            else:
                folder = app_data

            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)

            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", folder], check=True)
            else:
                subprocess.run(["xdg-open", folder], check=True)

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # WINDOW CONTROL
    # =========================================================================

    def close_window(self) -> None:
        """Close the settings window."""
        import webview
        for window in webview.windows:
            window.destroy()
