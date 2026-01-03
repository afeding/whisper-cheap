"""
Update manager for checking and installing updates via GitHub Releases.

Handles version checking, download with SHA256 verification, and installer execution.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import requests

from src.__version__ import __version__

# GitHub repository info - UPDATE THESE FOR YOUR REPO
GITHUB_OWNER = "afeding"
GITHUB_REPO = "whisper-cheap"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
INSTALLER_ASSET_NAME = "WhisperCheapSetup.exe"

# Cache settings
CHECK_COOLDOWN_SECONDS = 6 * 60 * 60  # 6 hours between automatic checks
REQUEST_TIMEOUT_SECONDS = 10


@dataclass
class UpdateInfo:
    """Information about an available update."""
    version: str
    download_url: str
    release_notes: str
    asset_size: int
    sha256: Optional[str] = None


class UpdateManager:
    """
    Manages checking for and installing updates from GitHub Releases.

    Thread-safe. Check runs async, download/install blocks.
    """

    def __init__(self, cache_dir: Path):
        """
        Initialize UpdateManager.

        Args:
            cache_dir: Directory for storing update cache (typically app_data)
        """
        self._cache_dir = Path(cache_dir)
        self._cache_file = self._cache_dir / "update_cache.json"
        self._lock = threading.Lock()
        self._latest_update: Optional[UpdateInfo] = None
        self._last_check_time: float = 0
        self._checking = False

    @property
    def current_version(self) -> str:
        """Get current application version."""
        return __version__

    def _parse_version(self, tag: str) -> tuple:
        """
        Parse version tag like 'v1.2.3' or '1.2.3' into tuple (1, 2, 3).

        Returns (0, 0, 0) for invalid formats.
        """
        clean = tag.lstrip("vV").strip()
        parts = clean.split(".")
        try:
            return tuple(int(p) for p in parts[:3])
        except (ValueError, TypeError):
            return (0, 0, 0)

    def _is_newer(self, remote_tag: str) -> bool:
        """Check if remote version is newer than current."""
        current = self._parse_version(self.current_version)
        remote = self._parse_version(remote_tag)
        return remote > current

    def _load_cache(self) -> Dict[str, Any]:
        """Load update cache from disk."""
        try:
            if self._cache_file.exists():
                return json.loads(self._cache_file.read_text(encoding="utf-8"))
        except Exception as e:
            logging.debug(f"[updater] Failed to load cache: {e}")
        return {}

    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Save update cache to disk."""
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logging.warning(f"[updater] Failed to save cache: {e}")

    def check_for_updates(self, force: bool = False) -> Optional[UpdateInfo]:
        """
        Check GitHub Releases for updates.

        Args:
            force: Bypass cooldown and check immediately

        Returns:
            UpdateInfo if update available, None otherwise
        """
        with self._lock:
            if self._checking:
                return self._latest_update

            # Check cooldown (unless forced)
            now = time.time()
            if not force and (now - self._last_check_time) < CHECK_COOLDOWN_SECONDS:
                # Return cached result
                cache = self._load_cache()
                if cache.get("update_available"):
                    self._latest_update = UpdateInfo(
                        version=cache["version"],
                        download_url=cache["download_url"],
                        release_notes=cache.get("release_notes", ""),
                        asset_size=cache.get("asset_size", 0),
                        sha256=cache.get("sha256"),
                    )
                return self._latest_update

            self._checking = True

        try:
            logging.info("[updater] Checking for updates...")

            response = requests.get(
                RELEASES_API,
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": f"WhisperCheap/{self.current_version}",
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()

            tag = data.get("tag_name", "")
            if not self._is_newer(tag):
                logging.info(
                    f"[updater] No update available (current={self.current_version}, latest={tag})"
                )
                with self._lock:
                    self._latest_update = None
                    self._last_check_time = time.time()
                    self._save_cache({
                        "update_available": False,
                        "checked_at": time.time(),
                        "latest_tag": tag,
                    })
                return None

            # Find installer asset
            assets = data.get("assets", [])
            installer_asset = None
            for asset in assets:
                if asset.get("name") == INSTALLER_ASSET_NAME:
                    installer_asset = asset
                    break

            if not installer_asset:
                logging.warning(
                    f"[updater] Update {tag} found but no installer asset '{INSTALLER_ASSET_NAME}'"
                )
                return None

            # Extract SHA256 if available (GitHub added this in June 2025)
            sha256 = None
            digest = installer_asset.get("digest")
            if isinstance(digest, dict):
                sha256 = digest.get("sha256")

            update_info = UpdateInfo(
                version=tag.lstrip("vV"),
                download_url=installer_asset.get("browser_download_url", ""),
                release_notes=(data.get("body") or "")[:500],  # Truncate long notes
                asset_size=installer_asset.get("size", 0),
                sha256=sha256,
            )

            logging.info(f"[updater] Update available: {update_info.version}")

            with self._lock:
                self._latest_update = update_info
                self._last_check_time = time.time()
                self._save_cache({
                    "update_available": True,
                    "version": update_info.version,
                    "download_url": update_info.download_url,
                    "release_notes": update_info.release_notes,
                    "asset_size": update_info.asset_size,
                    "sha256": update_info.sha256,
                    "checked_at": time.time(),
                })

            return update_info

        except requests.Timeout:
            logging.warning("[updater] Timeout checking for updates")
            return None
        except requests.RequestException as e:
            logging.warning(f"[updater] Network error checking updates: {e}")
            return None
        except Exception as e:
            logging.error(f"[updater] Error checking updates: {e}")
            return None
        finally:
            with self._lock:
                self._checking = False

    def check_async(
        self,
        callback: Optional[Callable[[Optional[UpdateInfo]], None]] = None,
        force: bool = False,
    ) -> None:
        """
        Check for updates in background thread.

        Args:
            callback: Optional function to call with result
            force: Bypass cooldown
        """
        def _check():
            result = self.check_for_updates(force=force)
            if callback:
                try:
                    callback(result)
                except Exception as e:
                    logging.error(f"[updater] Callback error: {e}")

        thread = threading.Thread(target=_check, daemon=True, name="UpdateChecker")
        thread.start()

    def get_cached_update(self) -> Optional[UpdateInfo]:
        """
        Get cached update info without network request.

        Returns:
            UpdateInfo if cached update exists, None otherwise
        """
        with self._lock:
            if self._latest_update:
                return self._latest_update

        cache = self._load_cache()
        if cache.get("update_available"):
            return UpdateInfo(
                version=cache["version"],
                download_url=cache["download_url"],
                release_notes=cache.get("release_notes", ""),
                asset_size=cache.get("asset_size", 0),
                sha256=cache.get("sha256"),
            )
        return None

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
            ValueError: If SHA256 verification fails
            requests.RequestException: On download failure
            Exception: On other errors
        """
        logging.info(f"[updater] Downloading update {update_info.version}...")

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

        # Verify SHA256 if available
        if update_info.sha256:
            actual_hash = hasher.hexdigest()
            expected_hash = update_info.sha256.lower()
            if actual_hash.lower() != expected_hash:
                # Delete corrupted file
                installer_path.unlink(missing_ok=True)
                raise ValueError(
                    f"SHA256 mismatch: expected {expected_hash[:16]}..., "
                    f"got {actual_hash[:16]}..."
                )
            logging.info("[updater] SHA256 verified successfully")
        else:
            logging.warning("[updater] No SHA256 provided, skipping verification")

        logging.info(f"[updater] Downloaded to {installer_path}")
        return installer_path

    def install_update(self, installer_path: Path, silent: bool = True) -> None:
        """
        Launch the installer and exit the current application.

        Args:
            installer_path: Path to downloaded installer
            silent: Run installer silently (no UI prompts)

        Raises:
            FileNotFoundError: If installer doesn't exist
        """
        if not installer_path.exists():
            raise FileNotFoundError(f"Installer not found: {installer_path}")

        logging.info(f"[updater] Launching installer: {installer_path}")

        # Build command with optional silent flag
        cmd = [str(installer_path)]
        if silent:
            cmd.append("/silent")

        # Launch installer as detached process
        # It will wait for our process to exit before replacing files
        if os.name == "nt":
            # Windows: use CREATE_NEW_PROCESS_GROUP to fully detach
            subprocess.Popen(
                cmd,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
            )
        else:
            # Unix fallback (shouldn't happen for this Windows app)
            subprocess.Popen(cmd, start_new_session=True, close_fds=True)

        # Exit our application so installer can replace files
        logging.info("[updater] Exiting application for update installation...")

        # Use os._exit to force immediate exit without cleanup
        # This is intentional - we want the installer to be able to replace our files
        os._exit(0)

    def clear_cache(self) -> None:
        """Clear the update cache, forcing a fresh check on next call."""
        with self._lock:
            self._latest_update = None
            self._last_check_time = 0

        try:
            if self._cache_file.exists():
                self._cache_file.unlink()
        except Exception as e:
            logging.warning(f"[updater] Failed to clear cache: {e}")
