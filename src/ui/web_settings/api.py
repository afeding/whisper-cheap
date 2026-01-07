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

# Default prompt template for LLM post-processing
DEFAULT_PROMPT_TEMPLATE = """Improve this voice transcription to make it more readable and natural.

Allowed improvements:
- Add periods, commas, and semicolons where natural
- Separate into paragraphs when the topic changes
- Remove accidentally repeated words (e.g., "and and" → "and")
- Convert spoken lists into bulleted format with dashes (-)
- Paraphrase slightly for clarity if needed
- Adjust vocabulary if it improves understanding

Important limits:
- Keep the original message and meaning
- Do not add information that isn't in the transcription
- If something is confusing or ambiguous, leave it as is
- ALWAYS respond in the same language as the original transcription

Transcription:
${output}"""

def _resource_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent.parent


DEFAULT_MODELS_PATH = _resource_base() / "resources" / "models_default.json"
PRICING_RESOURCE_PATH = _resource_base() / "resources" / "models_pricing.json"


class SettingsAPI:
    """API class exposed to JavaScript via pywebview."""

    def __init__(self, config_path: str | Path, history_manager=None):
        # Store as string (private) to avoid pywebview serialization issues with Path objects
        self._config_path_str = str(config_path)
        self._default_models: Optional[List[str]] = None
        self._update_manager = None  # Lazy-initialized

        # Initialize history_manager from config if not provided
        # (needed when running in subprocess where objects can't be passed)
        # Use private attribute (_) to prevent pywebview from trying to serialize it
        if history_manager is None:
            self._history_manager = self._create_history_manager()
        else:
            self._history_manager = history_manager

    def _create_history_manager(self):
        """Create HistoryManager from config paths."""
        try:
            from src.managers.history import HistoryManager
            app_data = self._get_app_data_dir()
            db_path = app_data / "history.db"
            recordings_dir = app_data / "recordings"
            return HistoryManager(db_path, recordings_dir)
        except Exception as e:
            print(f"[SettingsAPI] Failed to create HistoryManager: {e}")
            return None

    def _get_app_data_dir(self) -> Path:
        config = self.get_config()
        app_data = None
        if config:
            app_data = config.get("paths", {}).get("app_data")
        if not app_data:
            # Match main.py fallback: .data in dev, %APPDATA% when frozen
            is_frozen = getattr(sys, "frozen", False)
            if is_frozen:
                app_data = "%APPDATA%\\whisper-cheap"
            else:
                # Dev mode: .data relative to config.json
                app_data = ".data"
        app_data = os.path.expandvars(str(app_data))
        if not os.path.isabs(app_data):
            app_data = str(Path(self._config_path_str).parent / app_data)
        return Path(app_data)

    # =========================================================================
    # CONFIG
    # =========================================================================

    def get_config(self) -> Dict[str, Any]:
        """Load and return config.json."""
        try:
            with open(self._config_path_str, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save config to JSON file."""
        try:
            with open(self._config_path_str, 'w', encoding='utf-8') as f:
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

    def get_default_prompt_template(self) -> str:
        """Return the default prompt template for LLM post-processing."""
        return DEFAULT_PROMPT_TEMPLATE

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
            cache_path = self._get_app_data_dir() / "models_pricing.json"
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        try:
            if PRICING_RESOURCE_PATH.exists():
                with open(PRICING_RESOURCE_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _save_pricing_cache(self, data: Dict[str, Any]) -> bool:
        """Save pricing cache to file."""
        try:
            cache_path = self._get_app_data_dir() / "models_pricing.json"
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    # =========================================================================
    # HISTORY
    # =========================================================================

    def get_history(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get transcription history with pagination.

        Args:
            limit: Max entries to return
            offset: Skip first N entries

        Returns:
            {entries: [...], has_more: bool, total: int}
        """
        if not self._history_manager:
            return {"entries": [], "has_more": False, "total": 0}

        try:
            # Get all entries for pagination
            all_entries = self._history_manager.get_all()
            total = len(all_entries)

            # Apply pagination
            paginated = all_entries[offset:offset + limit]

            result = []
            for entry in paginated:
                # Build full audio path from file_name
                file_name = entry.get("file_name")
                audio_path = None
                if file_name:
                    audio_path = str(self._history_manager.recordings_dir / file_name)

                result.append({
                    "id": entry.get("id"),
                    "timestamp": entry.get("timestamp"),
                    "text": entry.get("transcription_text", ""),
                    "audio_path": audio_path,
                    "duration": self._get_audio_duration(audio_path)
                })

            return {
                "entries": result,
                "has_more": offset + limit < total,
                "total": total
            }
        except Exception as e:
            print(f"[SettingsAPI] Error getting history: {e}")
            return {"entries": [], "has_more": False, "total": 0}

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
        if not self._history_manager:
            return {"success": False, "error": "History manager not available"}

        try:
            self._history_manager.delete(entry_id)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # FOLDERS
    # =========================================================================

    def open_folder(self, folder_type: str) -> Dict[str, Any]:
        """Open data or recordings folder."""
        # Security: whitelist of allowed folder types to prevent path traversal
        ALLOWED_FOLDER_TYPES = {"data", "recordings", "logs"}
        if folder_type not in ALLOWED_FOLDER_TYPES:
            return {"success": False, "error": f"Invalid folder type: {folder_type}"}

        try:
            config = self.get_config()
            app_data = config.get("paths", {}).get("app_data", ".data")
            app_data = os.path.expandvars(app_data)

            # Resolve relative paths
            if not os.path.isabs(app_data):
                app_data = str(Path(self._config_path_str).parent / app_data)

            if folder_type == "recordings":
                folder = os.path.join(app_data, "recordings")
            elif folder_type == "logs":
                folder = os.path.join(app_data, "logs")
            else:  # folder_type == "data"
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
    # DIAGNOSTICS
    # =========================================================================

    def get_system_info(self) -> Dict[str, Any]:
        """Get system and app diagnostics info."""
        import platform

        # Check dependencies
        def check_dep(module_name: str) -> str:
            try:
                mod = __import__(module_name)
                version = getattr(mod, "__version__", getattr(mod, "version", "installed"))
                return str(version)
            except ImportError as e:
                return f"not installed ({e})"
            except Exception as e:
                return f"error: {type(e).__name__}: {e}"

        app_data = self._get_app_data_dir()
        log_file = app_data / "logs" / "app.log"

        return {
            "platform": sys.platform,
            "platform_version": platform.version(),
            "python_version": sys.version.split()[0],
            "app_data_path": str(app_data),
            "config_path": self._config_path_str,
            "log_file_path": str(log_file),
            "log_file_exists": log_file.exists(),
            "onnxruntime": check_dep("onnxruntime"),
            "sounddevice": check_dep("sounddevice"),
            "pyqt6": check_dep("PyQt6"),
            "keyboard": check_dep("keyboard"),
        }

    def get_logs(self, limit: int = 100) -> List[str]:
        """Get recent log entries from app.log."""
        app_data = self._get_app_data_dir()
        log_file = app_data / "logs" / "app.log"

        if not log_file.exists():
            return ["Log file not found: " + str(log_file)]

        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            # Return last N lines, reversed (newest first)
            return [line.rstrip() for line in lines[-limit:]][::-1]
        except Exception as e:
            return [f"Error reading logs: {e}"]

    def get_log_file_path(self) -> str:
        """Get the path to the log file."""
        app_data = self._get_app_data_dir()
        return str(app_data / "logs" / "app.log")

    def open_log_file(self) -> Dict[str, Any]:
        """Open the log file in the default text editor."""
        log_path = self.get_log_file_path()
        if not os.path.exists(log_path):
            return {"success": False, "error": "Log file not found"}

        try:
            if sys.platform == "win32":
                os.startfile(log_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", log_path], check=True)
            else:
                subprocess.run(["xdg-open", log_path], check=True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_logs_folder(self) -> Dict[str, Any]:
        """Open the logs folder in file explorer."""
        app_data = self._get_app_data_dir()
        logs_folder = app_data / "logs"

        if not logs_folder.exists():
            logs_folder.mkdir(parents=True, exist_ok=True)

        try:
            if sys.platform == "win32":
                os.startfile(str(logs_folder))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(logs_folder)], check=True)
            else:
                subprocess.run(["xdg-open", str(logs_folder)], check=True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_diagnostics(self) -> Dict[str, Any]:
        """Export diagnostics to a text file and return its path."""
        try:
            app_data = self._get_app_data_dir()
            export_path = app_data / f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            sys_info = self.get_system_info()
            logs = self.get_logs(200)

            with open(export_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("WHISPER CHEAP - DIAGNOSTIC REPORT\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 60 + "\n\n")

                f.write("SYSTEM INFO\n")
                f.write("-" * 40 + "\n")
                for key, value in sys_info.items():
                    f.write(f"{key}: {value}\n")

                f.write("\n\nCONFIGURATION\n")
                f.write("-" * 40 + "\n")
                config = self.get_config()
                # Redact sensitive info
                if "post_processing" in config:
                    if "openrouter_api_key" in config["post_processing"]:
                        key = config["post_processing"]["openrouter_api_key"]
                        if key:
                            config["post_processing"]["openrouter_api_key"] = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
                f.write(json.dumps(config, indent=2, ensure_ascii=False))

                f.write("\n\n\nRECENT LOGS (newest first)\n")
                f.write("-" * 40 + "\n")
                for line in logs:
                    f.write(line + "\n")

            # Open the file location
            if sys.platform == "win32":
                subprocess.run(["explorer", "/select,", str(export_path)])

            return {"success": True, "path": str(export_path)}
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

    # =========================================================================
    # UPDATES
    # =========================================================================

    def _get_update_manager(self):
        """Lazy-initialize UpdateManager."""
        if self._update_manager is None:
            try:
                from src.managers.updater import UpdateManager
                app_data = self._get_app_data_dir()
                self._update_manager = UpdateManager(cache_dir=app_data)
            except Exception as e:
                print(f"[SettingsAPI] Failed to init UpdateManager: {e}")
                return None
        return self._update_manager

    def get_app_version(self) -> str:
        """Get current application version."""
        try:
            from src.__version__ import __version__
            return __version__
        except Exception:
            return "unknown"

    def get_update_status(self) -> Dict[str, Any]:
        """
        Get update status from cache (fast, no network request).

        Returns:
            {
                "current_version": "1.0.0",
                "update_available": bool,
                "latest_version": "1.1.0" or None,
                "release_notes": "..." or None,
                "download_size_mb": float or None
            }
        """
        try:
            manager = self._get_update_manager()
            if not manager:
                return {
                    "current_version": self.get_app_version(),
                    "update_available": False,
                    "error": "UpdateManager not available",
                }

            update = manager.get_cached_update()

            return {
                "current_version": manager.current_version,
                "update_available": update is not None,
                "latest_version": update.version if update else None,
                "release_notes": update.release_notes if update else None,
                "download_size_mb": round(update.asset_size / 1024 / 1024, 1) if update and update.asset_size else None,
            }
        except Exception as e:
            return {
                "current_version": self.get_app_version(),
                "update_available": False,
                "error": str(e),
            }

    def check_for_updates(self) -> Dict[str, Any]:
        """
        Force check for updates (makes network request).

        Returns same format as get_update_status.
        """
        try:
            manager = self._get_update_manager()
            if not manager:
                return {
                    "current_version": self.get_app_version(),
                    "update_available": False,
                    "error": "UpdateManager not available",
                }

            update = manager.check_for_updates(force=True)

            return {
                "current_version": manager.current_version,
                "update_available": update is not None,
                "latest_version": update.version if update else None,
                "release_notes": update.release_notes if update else None,
                "download_size_mb": round(update.asset_size / 1024 / 1024, 1) if update and update.asset_size else None,
            }
        except Exception as e:
            return {
                "current_version": self.get_app_version(),
                "update_available": False,
                "error": str(e),
            }

    def download_and_install_update(self) -> Dict[str, Any]:
        """
        Download and install the available update.

        This will exit the application after launching the installer.

        Returns:
            {"success": bool, "error": str or None}
        """
        try:
            manager = self._get_update_manager()
            if not manager:
                return {"success": False, "error": "UpdateManager not available"}

            update = manager.get_cached_update()
            if not update:
                return {"success": False, "error": "No update available"}

            # Download the installer (blocking operation)
            installer_path = manager.download_update(update)

            # Install (this will exit the app)
            manager.install_update(installer_path, silent=True)

            # Should not reach here - install_update calls os._exit(0)
            return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}
