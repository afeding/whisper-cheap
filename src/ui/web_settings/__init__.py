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
    import json
    import os
    import sys
    from pathlib import Path

    import webview

    LLM_SYSTEM_PROMPT = (
        "You are \"Transcription 2.0\": a real-time dictation post-editor.\n\n"
        "Task:\n"
        "- Take the user's raw speech-to-text transcript and return the same content as clean written text.\n\n"
        "Absolute output rules:\n"
        "- Output ONLY the transformed text. No titles, no prefixes, no explanations, no markdown wrappers.\n"
        "- Keep the SAME language as the transcript. Do NOT translate.\n"
        "- Preserve meaning strictly. Do NOT add new ideas, facts, steps, names, or assumptions.\n"
    )

    class SettingsAPI:
        def __init__(self, config_path_str: str):
            self.config_path_str = config_path_str
            self._default_models = None

        def get_config(self):
            try:
                with open(self.config_path_str, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}

        def save_config(self, data):
            try:
                with open(self.config_path_str, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

        def get_audio_devices(self):
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
            except Exception:
                return []

        def get_default_models(self):
            if self._default_models is not None:
                return self._default_models

            fallback = [
                "openai/gpt-oss-20b",
                "google/gemini-2.5-flash-lite",
                "mistralai/mistral-small-3.2-24b-instruct"
            ]

            try:
                config_dir = Path(self.config_path_str).parent
                models_path = config_dir / "src" / "resources" / "models_default.json"
                with open(str(models_path), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._default_models = [str(x) for x in data if x]
                        return self._default_models
            except Exception:
                pass

            self._default_models = fallback
            return self._default_models

        def test_llm_connection(self, api_key: str, model: str):
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

            except Exception as e:
                return {"success": False, "error": str(e)}

        def get_history(self, limit: int = 20):
            return []

        def copy_to_clipboard(self, text: str):
            try:
                import pyperclip
                pyperclip.copy(text)
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

        def play_audio(self, path: str):
            if not path or not os.path.exists(path):
                return {"success": False, "error": "File not found"}
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

        def open_folder(self, folder_type: str):
            try:
                config = self.get_config()
                app_data = config.get("paths", {}).get("app_data", ".data")
                app_data = os.path.expandvars(app_data)

                if not os.path.isabs(app_data):
                    app_data = str(Path(self.config_path_str).parent / app_data)

                if folder_type == "recordings":
                    folder = os.path.join(app_data, "recordings")
                else:
                    folder = app_data

                if not os.path.exists(folder):
                    os.makedirs(folder, exist_ok=True)

                if sys.platform == "win32":
                    os.startfile(folder)

                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

    # Create and run webview
    api = SettingsAPI(config_path_str)

    window = webview.create_window(
        'Whisper Cheap Settings',
        html_path_str,
        js_api=api,
        width=950,
        height=700,
        min_size=(850, 600),
        background_color='#0a0a0a'
    )

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
