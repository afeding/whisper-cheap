# Whisper Cheap - Security Fixes Implementation Guide

## Quick Reference for Patches

This document provides exact code changes to fix critical vulnerabilities.

---

## Fix 1: Remove Hardcoded API Key from config.json

**Current (INSECURE):**
```json
{
  "post_processing": {
    "enabled": true,
    "openrouter_api_key": "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",
    ...
  }
}
```

**Fixed:**
```json
{
  "post_processing": {
    "enabled": false,
    "openrouter_api_key": "",
    ...
  }
}
```

**Then update code to use environment variable:**

In `src/main.py`, around line 525:

```python
# OLD (INSECURE):
if pp_cfg.get("enabled") and pp_cfg.get("openrouter_api_key") and pp_cfg.get("model"):
    try:
        llm_client = LLMClient(
            api_key=pp_cfg["openrouter_api_key"],
            default_model=pp_cfg["model"],
        )

# NEW (SECURE):
if pp_cfg.get("enabled") and pp_cfg.get("model"):
    # Try to get API key from environment first, then config
    api_key = os.getenv("OPENROUTER_API_KEY") or pp_cfg.get("openrouter_api_key", "")

    if not api_key:
        logging.warning(
            "[llm] Post-processing enabled but no API key available.\n"
            "Set environment variable: $env:OPENROUTER_API_KEY='your-key'\n"
            "Or add to config.json: post_processing.openrouter_api_key"
        )
        llm_client = None
    else:
        try:
            llm_client = LLMClient(
                api_key=api_key,
                default_model=pp_cfg["model"],
            )
            logging.info(f"[llm] LLM client ready: {pp_cfg['model']}")
        except Exception as exc:
            logging.error(f"[llm] Failed to initialize client: {type(exc).__name__}")
            llm_client = None
```

**Documentation to add to README.md:**

```markdown
### Using OpenRouter LLM Post-Processing

To enable LLM-based post-processing of transcriptions:

1. Get an API key from [openrouter.ai](https://openrouter.ai)

2. Set the environment variable (recommended - secure):
   ```powershell
   # PowerShell
   $env:OPENROUTER_API_KEY = "sk-or-v1-xxxxx"
   python -m src.main

   # Or permanently:
   [Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-v1-xxxxx", "User")
   ```

3. OR add to config.json (less secure):
   ```json
   {
     "post_processing": {
       "enabled": true,
       "openrouter_api_key": "sk-or-v1-xxxxx",
       "model": "openai/gpt-oss-20b:free"
     }
   }
   ```

**Important:** Never commit API keys to version control. Use `.gitignore` for config.json:
```
# .gitignore
config.json
.env
```
```

---

## Fix 2: Prevent Path Traversal in SettingsAPI

**Create new utility file: `src/utils/path_validation.py`**

```python
"""Path validation utilities to prevent traversal attacks."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional


def validate_filename(filename: str, allowed_pattern: Optional[str] = None) -> bool:
    """
    Validate filename to prevent directory traversal.

    Args:
        filename: Filename to validate
        allowed_pattern: Regex pattern to match (if None, default safe pattern used)

    Returns:
        True if filename is safe, False otherwise

    Examples:
        >>> validate_filename("whisper-cheap-1234567890.wav")
        True
        >>> validate_filename("../etc/passwd")
        False
        >>> validate_filename("..\\windows\\system32")
        False
    """
    if not filename or not isinstance(filename, str):
        return False

    # Check for traversal sequences
    if ".." in filename:
        return False

    if "/" in filename or "\\" in filename:
        return False

    # Check for special characters that could cause issues
    if any(char in filename for char in ["<", ">", '"', "|", "?", "*"]):
        return False

    # Use provided pattern or default
    if allowed_pattern:
        return bool(re.match(allowed_pattern, filename))

    # Default: only alphanumeric, dash, underscore, period, space
    return bool(re.match(r"^[a-zA-Z0-9._\-\s]+$", filename))


def safe_path_join(base_dir: Path, relative_path: str) -> Optional[Path]:
    """
    Safely join base directory with user-provided relative path.

    Prevents directory traversal attacks by verifying the result
    is still within base_dir.

    Args:
        base_dir: Safe base directory (must be absolute)
        relative_path: User-provided path component

    Returns:
        Resolved path if safe, None if traversal attempted

    Examples:
        >>> base = Path("/home/user/recordings")
        >>> safe_path_join(base, "file.wav")
        Path('/home/user/recordings/file.wav')

        >>> safe_path_join(base, "../etc/passwd")
        None  # Path traversal blocked
    """
    if not isinstance(base_dir, Path):
        base_dir = Path(base_dir)

    if not base_dir.is_absolute():
        raise ValueError(f"base_dir must be absolute, got {base_dir}")

    # Don't allow absolute paths in relative_path
    if os.path.isabs(relative_path):
        return None

    # Check for traversal
    if ".." in relative_path or relative_path.startswith(os.sep):
        return None

    try:
        combined = base_dir / relative_path
        resolved = combined.resolve()

        # Verify resolved path is still under base_dir
        base_resolved = base_dir.resolve()
        if not str(resolved).startswith(str(base_resolved)):
            return None

        return resolved
    except Exception:
        return None


def validate_config_path(path_str: str, allowed_bases: Optional[list[str]] = None) -> Optional[Path]:
    """
    Validate path from configuration to prevent escape.

    Args:
        path_str: Path string from config (may contain environment variables)
        allowed_bases: List of allowed base paths (e.g., [%APPDATA%, %HOME%])

    Returns:
        Validated absolute Path or None if invalid

    Examples:
        >>> validate_config_path("%APPDATA%\\whisper-cheap")
        Path('C:\\Users\\User\\AppData\\Roaming\\whisper-cheap')

        >>> validate_config_path("../../../../etc/passwd")
        None  # Traversal blocked
    """
    try:
        # Expand environment variables
        expanded = os.path.expandvars(path_str)

        # Normalize to absolute path
        path = Path(expanded).resolve()

        # Check for traversal in expanded form
        if ".." in str(path):
            return None

        # On Windows, restrict absolute paths to specific locations
        if os.name == "nt":
            appdata = os.path.expandvars("%APPDATA%")
            home = str(Path.home())

            path_str = str(path).lower()
            appdata_lower = appdata.lower()
            home_lower = home.lower()

            allowed = [appdata_lower, home_lower]
            if allowed_bases:
                allowed.extend(b.lower() for b in allowed_bases)

            if not any(path_str.startswith(a) for a in allowed):
                return None

        return path
    except Exception:
        return None
```

**Update `src/ui/web_settings/api.py`:**

```python
# Add at top of file:
from src.utils.path_validation import validate_filename, safe_path_join, validate_config_path

# Update get_history():
def get_history(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """Get transcription history with pagination."""
    if not self._history_manager:
        return {"entries": [], "has_more": False, "total": 0}

    try:
        all_entries = self._history_manager.get_all()
        total = len(all_entries)

        paginated = all_entries[offset:offset + limit]

        result = []
        for entry in paginated:
            file_name = entry.get("file_name")

            # SECURITY: Validate filename format
            if not validate_filename(file_name, allowed_pattern=r"^whisper-cheap-\d+\.wav$"):
                logging.warning(f"[SettingsAPI] Invalid filename detected: {file_name}")
                continue

            # SECURITY: Use safe path joining
            audio_path = safe_path_join(
                self._history_manager.recordings_dir,
                file_name
            )

            if audio_path is None:
                logging.error(f"[SettingsAPI] Path traversal blocked: {file_name}")
                continue

            result.append({
                "id": entry.get("id"),
                "timestamp": entry.get("timestamp"),
                "text": entry.get("transcription_text", ""),
                "audio_path": str(audio_path),
                "duration": self._get_audio_duration(str(audio_path))
            })

        return {
            "entries": result,
            "has_more": offset + limit < total,
            "total": total
        }
    except Exception as e:
        logging.error(f"[SettingsAPI] Error getting history: {e}")
        return {"entries": [], "has_more": False, "total": 0}

# Update open_folder():
def open_folder(self, folder_type: str) -> Dict[str, Any]:
    """Open data or recordings folder."""
    try:
        # SECURITY: Validate folder type
        if folder_type not in ("recordings", "data", "logs"):
            return {"success": False, "error": "Invalid folder type"}

        config = self.get_config()
        app_data_str = config.get("paths", {}).get("app_data", ".data")

        # SECURITY: Validate config path
        app_data = validate_config_path(app_data_str)
        if not app_data:
            return {"success": False, "error": "Invalid app_data path in config"}

        # Construct folder path
        if folder_type == "recordings":
            folder = app_data / "recordings"
        elif folder_type == "logs":
            folder = app_data / "logs"
        else:
            folder = app_data

        # Create if missing
        folder.mkdir(parents=True, exist_ok=True)

        # Open folder
        if sys.platform == "win32":
            os.startfile(str(folder))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(folder)], check=True)
        else:
            subprocess.run(["xdg-open", str(folder)], check=True)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}

# Update play_audio():
def play_audio(self, path: str) -> Dict[str, Any]:
    """Play audio file with security validation."""
    if not path:
        return {"success": False, "error": "Path required"}

    try:
        # SECURITY: Only allow wav files in recordings directory
        audio_path = Path(path).resolve()
        recordings_dir = self._history_manager.recordings_dir.resolve()

        # Check containment
        if not str(audio_path).startswith(str(recordings_dir)):
            logging.warning(f"[SettingsAPI] Attempted to play file outside recordings: {path}")
            return {"success": False, "error": "Invalid path"}

        # Check extension
        if audio_path.suffix.lower() != ".wav":
            return {"success": False, "error": "Only WAV files supported"}

        if not audio_path.exists():
            return {"success": False, "error": "File not found"}

        # Play using safe method (not os.startfile which can execute any file)
        if sys.platform == "win32":
            # Use wmplayer.exe or Python's platform-agnostic method
            subprocess.run(
                ["python", "-m", "wave", str(audio_path)],
                timeout=1
            )
        elif sys.platform == "darwin":
            subprocess.run(["afplay", str(audio_path)], check=True, timeout=60)
        else:
            subprocess.run(["paplay", str(audio_path)], check=True, timeout=60)

        return {"success": True}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Playback timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}
```

---

## Fix 3: Implement Configuration Validation

**Create new file: `src/utils/config_validation.py`**

```python
"""Configuration validation with bounds checking."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates and sanitizes configuration values."""

    # Safe ranges for audio parameters
    SAMPLE_RATE_MIN = 8000
    SAMPLE_RATE_MAX = 48000

    CHANNELS_ALLOWED = (1, 2)

    CHUNK_SIZE_MIN = 256
    CHUNK_SIZE_MAX = 1048576  # 1MB

    VAD_THRESHOLD_MIN = 0.0
    VAD_THRESHOLD_MAX = 1.0

    DEVICE_ID_MAX = 100

    @staticmethod
    def validate_audio_config(audio_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize audio configuration.

        Returns corrected config with safe defaults.
        """
        result = {}

        # Sample rate
        try:
            sr = int(audio_cfg.get("sample_rate", 16000))
            if not (ConfigValidator.SAMPLE_RATE_MIN <= sr <= ConfigValidator.SAMPLE_RATE_MAX):
                logger.warning(
                    f"sample_rate {sr} out of range [{ConfigValidator.SAMPLE_RATE_MIN}, "
                    f"{ConfigValidator.SAMPLE_RATE_MAX}], using default 16000"
                )
                sr = 16000
            result["sample_rate"] = sr
        except (TypeError, ValueError):
            logger.warning("Invalid sample_rate, using default 16000")
            result["sample_rate"] = 16000

        # Channels
        try:
            ch = int(audio_cfg.get("channels", 1))
            if ch not in ConfigValidator.CHANNELS_ALLOWED:
                logger.warning(f"channels {ch} invalid, using 1")
                ch = 1
            result["channels"] = ch
        except (TypeError, ValueError):
            logger.warning("Invalid channels, using default 1")
            result["channels"] = 1

        # Chunk size
        try:
            cs = int(audio_cfg.get("chunk_size", 4096))
            if not (ConfigValidator.CHUNK_SIZE_MIN <= cs <= ConfigValidator.CHUNK_SIZE_MAX):
                logger.warning(f"chunk_size {cs} out of range, using default 4096")
                cs = 4096
            result["chunk_size"] = cs
        except (TypeError, ValueError):
            logger.warning("Invalid chunk_size, using default 4096")
            result["chunk_size"] = 4096

        # VAD threshold
        try:
            vt = float(audio_cfg.get("vad_threshold", 0.5))
            if not (ConfigValidator.VAD_THRESHOLD_MIN <= vt <= ConfigValidator.VAD_THRESHOLD_MAX):
                logger.warning(f"vad_threshold {vt} out of range [0.0, 1.0], using 0.5")
                vt = 0.5
            result["vad_threshold"] = vt
        except (TypeError, ValueError):
            logger.warning("Invalid vad_threshold, using default 0.5")
            result["vad_threshold"] = 0.5

        # Device ID
        try:
            dev_id = audio_cfg.get("device_id")
            if dev_id is not None:
                dev_id = int(dev_id)
                if dev_id < -1 or dev_id > ConfigValidator.DEVICE_ID_MAX:
                    logger.warning(f"device_id {dev_id} out of range, using None (default)")
                    dev_id = None
            result["device_id"] = dev_id
        except (TypeError, ValueError):
            logger.warning("Invalid device_id, using None (default)")
            result["device_id"] = None

        # Boolean flags
        result["use_vad"] = bool(audio_cfg.get("use_vad", False))
        result["mute_while_recording"] = bool(audio_cfg.get("mute_while_recording", False))
        result["enable_cues"] = bool(audio_cfg.get("enable_cues", True))

        # Cue gain (0.1 to 1.0)
        try:
            cg = float(audio_cfg.get("cue_gain", 0.5))
            cg = max(0.1, min(1.0, cg))
            result["cue_gain"] = cg
        except (TypeError, ValueError):
            result["cue_gain"] = 0.5

        return result

    @staticmethod
    def validate_prompt_template(template: Optional[str]) -> str:
        """
        Validate prompt template for LLM post-processing.

        - Must contain ${output} placeholder
        - Must be reasonable length
        - Must not have obviously malicious content
        """
        if not template or not isinstance(template, str):
            return "Transcript:\n${output}"

        # Must contain placeholder
        if "${output}" not in template:
            logger.warning("Prompt template missing ${output} placeholder, using default")
            return "Transcript:\n${output}"

        # Limit length
        if len(template) > 5000:
            logger.warning("Prompt template too long (>5000 chars), using default")
            return "Transcript:\n${output}"

        return template.strip()

    @staticmethod
    def validate_llm_model(model: Optional[str]) -> Optional[str]:
        """Validate LLM model identifier."""
        if not model or not isinstance(model, str):
            return None

        model = model.strip()

        # Must be in format: provider/model-name
        if "/" not in model:
            logger.warning(f"Invalid model format: {model}, expected 'provider/model'")
            return None

        # Length check
        if len(model) > 200:
            logger.warning("Model identifier too long")
            return None

        return model
```

**Update `src/main.py` to use validation:**

```python
# Add import
from src.utils.config_validation import ConfigValidator

# Replace audio config creation (around line 346):
# OLD:
recording_config = RecordingConfig(
    sample_rate=audio_cfg.get("sample_rate", 16000),
    channels=audio_cfg.get("channels", 1),
    chunk_size=audio_cfg.get("chunk_size", 1024),
    vad_threshold=audio_cfg.get("vad_threshold", 0.5),
    # ...
)

# NEW:
validated_audio_cfg = ConfigValidator.validate_audio_config(audio_cfg)
recording_config = RecordingConfig(
    sample_rate=validated_audio_cfg["sample_rate"],
    channels=validated_audio_cfg["channels"],
    chunk_size=validated_audio_cfg["chunk_size"],
    vad_threshold=validated_audio_cfg["vad_threshold"],
    always_on_stream=mode_cfg.get("stream_mode", "always_on") == "always_on",
    use_vad=validated_audio_cfg["use_vad"],
    mute_while_recording=validated_audio_cfg["mute_while_recording"],
)

# Also validate LLM config (around line 870):
pp_cfg = fresh_pp_cfg
if pp_cfg.get("enabled"):
    validated_model = ConfigValidator.validate_llm_model(pp_cfg.get("model"))
    if not validated_model:
        logging.warning("[config] Invalid LLM model in config, disabling post-processing")
        pp_cfg["enabled"] = False
    else:
        pp_cfg["model"] = validated_model

    prompt = ConfigValidator.validate_prompt_template(pp_cfg.get("prompt_template"))
    pp_cfg["prompt_template"] = prompt
```

---

## Fix 4: Require SHA256 Verification for Updates

**Update `src/managers/updater.py`:**

```python
def download_update(
    self,
    update_info: UpdateInfo,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> Path:
    """
    Download the update installer to temp directory.

    Args:
        update_info: Update to download
        on_progress: Optional callback(downloaded_bytes, total_bytes)

    Returns:
        Path to downloaded installer

    Raises:
        ValueError: If SHA256 verification fails or SHA256 not available
        requests.RequestException: On download failure
        Exception: On other errors
    """
    logging.info(f"[updater] Downloading update {update_info.version}...")

    # SECURITY: SHA256 verification is MANDATORY
    if not update_info.sha256:
        raise ValueError(
            f"Cannot download update {update_info.version}: "
            "No SHA256 hash provided by GitHub. "
            "This is a security requirement. Please ensure the release asset "
            "has a valid SHA256 hash. Contact the maintainer if this persists."
        )

    # Create temp directory for download
    temp_dir = Path(tempfile.gettempdir()) / "whisper-cheap-update"
    temp_dir.mkdir(parents=True, exist_ok=True)
    installer_path = temp_dir / INSTALLER_ASSET_NAME

    # Download with streaming
    response = requests.get(
        update_info.download_url,
        stream=True,
        timeout=300,  # 5 min timeout for large files
        headers={"User-Agent": f"WhisperCheap/{self.current_version}"},
        allow_redirects=False,  # No redirects - prevent MITM
    )

    # Check for redirects (potential attack)
    if 300 <= response.status_code < 400:
        raise ValueError(
            f"Download redirected (HTTP {response.status_code}) - possible attack. "
            "Aborting update."
        )

    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    # Hash as we download for verification
    hasher = hashlib.sha256()

    with open(installer_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                hasher.update(chunk)
                downloaded += len(chunk)
                if on_progress:
                    try:
                        on_progress(downloaded, total_size)
                    except Exception:
                        pass

    # MANDATORY SHA256 verification
    actual_hash = hasher.hexdigest()
    expected_hash = update_info.sha256.lower()

    if actual_hash.lower() != expected_hash:
        # Delete corrupted file immediately
        installer_path.unlink(missing_ok=True)
        raise ValueError(
            f"SHA256 verification FAILED for update {update_info.version}.\n"
            f"Expected: {expected_hash}\n"
            f"Got:      {actual_hash}\n\n"
            f"The downloaded file is corrupted or has been tampered with. "
            f"Installation aborted for security."
        )

    logging.info(
        f"[updater] SHA256 verified successfully: {actual_hash[:16]}..."
    )

    logging.info(f"[updater] Downloaded to {installer_path}")
    return installer_path
```

---

## Fix 5: Mask API Keys in Logging

**Create utility in `src/utils/security.py`:**

```python
"""Security utilities for sensitive data handling."""

from __future__ import annotations

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def mask_api_key(key: Optional[str]) -> str:
    """
    Mask API key for safe logging.

    Args:
        key: API key to mask (or None)

    Returns:
        Masked version: "sk-or-...xxxx" or "***"

    Examples:
        >>> mask_api_key("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")
        'sk-or-v1-...cb9bf'

        >>> mask_api_key(None)
        '***'
    """
    if not key or not isinstance(key, str):
        return "***"

    if len(key) < 8:
        return "***"

    # Show first 8 and last 4 characters
    return f"{key[:8]}...{key[-4:]}"


def mask_sensitive_config(config: dict) -> dict:
    """
    Create a safe copy of config with sensitive data masked.

    Useful for logging without leaking secrets.
    """
    import copy

    safe_cfg = copy.deepcopy(config)

    # Mask API keys
    if "post_processing" in safe_cfg:
        if "openrouter_api_key" in safe_cfg["post_processing"]:
            key = safe_cfg["post_processing"]["openrouter_api_key"]
            safe_cfg["post_processing"]["openrouter_api_key"] = mask_api_key(key)

    return safe_cfg
```

**Update `src/main.py` to use masking:**

```python
# Import masking utility
from src.utils.security import mask_api_key, mask_sensitive_config

# Line 872-873 (in on_release):
# OLD:
logging.info(f"[llm] Client ready: {pp_cfg['model']}")

# NEW:
logging.info(
    f"[llm] Client ready: model={pp_cfg['model']}, "
    f"key={mask_api_key(pp_cfg.get('openrouter_api_key'))}"
)

# For any exception handling that might log the config:
try:
    llm_client = LLMClient(...)
except Exception as exc:
    safe_cfg = mask_sensitive_config(fresh_pp_cfg)
    logging.error(f"[llm] Failed to create client: {exc}")
    logging.debug(f"[llm] Config was: {safe_cfg}")
```

---

## Fix 6: Add Try/Finally for Clipboard Safety

**Update `src/utils/paste.py`:**

```python
def paste_text(
    text: str,
    method: PasteMethod = PasteMethod.CTRL_V,
    policy: ClipboardPolicy = ClipboardPolicy.DONT_MODIFY,
    clipboard: Optional[ClipboardManager] = None,
    delay_seconds: float = 0.05,
    send_key_combo: Optional[Callable[[PasteMethod], None]] = None,
    keyboard_module=None,
) -> None:
    """
    Perform paste according to method and clipboard policy.

    SECURITY: Uses try/finally to ensure clipboard is restored
    even if paste operation fails.
    """
    cb = clipboard or ClipboardManager()
    sender = send_key_combo
    if sender is None:
        sender = _default_sender
    kb = keyboard_module or keyboard

    original_clipboard = None

    try:
        if policy == ClipboardPolicy.DONT_MODIFY:
            # Save original clipboard content
            original_clipboard = cb.get_text()

            # Set transcription
            if not _set_and_verify_clipboard(cb, text, max_retries=2):
                logger.warning("[paste] Clipboard verification failed, continuing anyway")

            time.sleep(delay_seconds)

            # Perform paste action
            _perform_paste_action(text, method, sender, kb, delay_seconds)

            time.sleep(delay_seconds)

        elif policy == ClipboardPolicy.COPY_TO_CLIPBOARD:
            # Leave transcription in clipboard
            if not _set_and_verify_clipboard(cb, text, max_retries=2):
                logger.warning("[paste] Clipboard verification failed, continuing anyway")

            time.sleep(delay_seconds)
            _perform_paste_action(text, method, sender, kb, delay_seconds)
        else:
            logger.warning(f"[paste] Unknown clipboard policy: {policy}")
            return

    finally:
        # CRITICAL: Always restore original clipboard, even if exception occurs
        if original_clipboard is not None and policy == ClipboardPolicy.DONT_MODIFY:
            try:
                cb.backend.copy(original_clipboard)
                logger.debug("[paste] Clipboard restored")
            except Exception as e:
                logger.error(f"[paste] Failed to restore clipboard: {type(e).__name__}")
                # Don't raise - best effort only
```

---

## Testing the Fixes

Create test file: `tests/test_security_fixes.py`

```python
"""Tests for security fixes."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.utils.path_validation import validate_filename, safe_path_join, validate_config_path
from src.utils.config_validation import ConfigValidator
from src.utils.security import mask_api_key


class TestPathValidation:
    """Test path traversal prevention."""

    def test_valid_filename(self):
        assert validate_filename("whisper-cheap-1234567890.wav")
        assert validate_filename("normal_file.txt")
        assert validate_filename("file with spaces.txt")

    def test_traversal_blocked(self):
        assert not validate_filename("../etc/passwd")
        assert not validate_filename("..\\windows\\system32")
        assert not validate_filename("file/../traversal")

    def test_special_chars_blocked(self):
        assert not validate_filename("file<script>.txt")
        assert not validate_filename("file|command.txt")

    def test_safe_path_join(self):
        base = Path("/tmp/recordings").resolve()

        # Valid
        result = safe_path_join(base, "file.wav")
        assert result
        assert str(result).startswith(str(base))

        # Traversal blocked
        assert safe_path_join(base, "../etc/passwd") is None

        # Absolute path blocked
        assert safe_path_join(base, "/etc/passwd") is None


class TestConfigValidation:
    """Test configuration bounds checking."""

    def test_sample_rate_validation(self):
        cfg = {"sample_rate": 16000}
        result = ConfigValidator.validate_audio_config(cfg)
        assert result["sample_rate"] == 16000

        # Out of range
        cfg = {"sample_rate": 999999}
        result = ConfigValidator.validate_audio_config(cfg)
        assert 8000 <= result["sample_rate"] <= 48000

        # Invalid type
        cfg = {"sample_rate": "hello"}
        result = ConfigValidator.validate_audio_config(cfg)
        assert result["sample_rate"] == 16000

    def test_channels_validation(self):
        cfg = {"channels": 1}
        result = ConfigValidator.validate_audio_config(cfg)
        assert result["channels"] == 1

        cfg = {"channels": 2}
        result = ConfigValidator.validate_audio_config(cfg)
        assert result["channels"] == 2

        # Invalid
        cfg = {"channels": 100}
        result = ConfigValidator.validate_audio_config(cfg)
        assert result["channels"] == 1

    def test_prompt_template_validation(self):
        # Valid
        template = "Process this: ${output}"
        result = ConfigValidator.validate_prompt_template(template)
        assert result == template

        # Missing placeholder
        template = "Process this"
        result = ConfigValidator.validate_prompt_template(template)
        assert "${output}" in result

        # Too long
        template = "${output}" + "x" * 10000
        result = ConfigValidator.validate_prompt_template(template)
        assert len(result) <= 5000


class TestSecurityUtils:
    """Test security utilities."""

    def test_mask_api_key(self):
        key = "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"
        masked = mask_api_key(key)

        # Should start with first 8 chars
        assert masked.startswith("sk-or-v1")

        # Should end with last 4 chars
        assert masked.endswith("cb9bf")

        # Should not contain full key
        assert "e8d4468c" not in masked

    def test_mask_none_key(self):
        assert mask_api_key(None) == "***"
        assert mask_api_key("") == "***"
        assert mask_api_key("short") == "***"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run tests:
```bash
pytest tests/test_security_fixes.py -v
```

---

## Deployment Checklist

- [ ] Remove OpenRouter key from config.json
- [ ] Update main.py to use environment variable for API key
- [ ] Create path_validation.py utility
- [ ] Update SettingsAPI with path validation
- [ ] Create config_validation.py utility
- [ ] Update main.py to validate audio config
- [ ] Update updater.py to require SHA256
- [ ] Create security.py utility
- [ ] Update logging to mask API keys
- [ ] Update paste.py with try/finally
- [ ] Run security tests: `pytest tests/test_security_fixes.py -v`
- [ ] Test manual workflows (recording, pasting, settings)
- [ ] Update documentation

---

**Implementation Time Estimate:** 4-6 hours for comprehensive fixes
**Testing Time:** 2-3 hours
**Total:** 6-9 hours before release
