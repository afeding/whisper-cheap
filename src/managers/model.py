"""
Model management for Whisper Cheap (Parakeet V3).

Responsibilities:
- Catalog metadata
- Resumable download of model archives
- Extraction with atomic rename (.extracting -> final)
- Validation helpers
- Cleanup of partial/extracting artifacts
"""

from __future__ import annotations

import hashlib
import logging
import os
import tarfile
from pathlib import Path
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:  # pragma: no cover - handled via injection
    requests = None


MODELS: Dict[str, Dict[str, object]] = {
    "parakeet-v3-int8": {
        "id": "parakeet-v3-int8",
        "name": "Parakeet V3 INT8",
        "url": "https://blob.handy.computer/parakeet-v3-int8.tar.gz",
        "size_mb": 478,
        "is_directory": True,
        "extract_to": "parakeet-tdt-0.6b-v3-int8",
        # SHA256 of the .tar.gz archive (None = skip validation)
        "sha256": None,
    }
}


def _default_base_dir() -> Path:
    # Use APPDATA on Windows; fallback to home.
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / "whisper-cheap" / "models"
    return Path.home() / ".whisper-cheap" / "models"


def _compute_sha256(file_path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


class ModelManager:
    def __init__(
        self,
        base_dir: Path | str | None = None,
        requests_module=None,
        on_event: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.base_dir = Path(base_dir) if base_dir else _default_base_dir()
        self.requests = requests_module or requests
        self.on_event = on_event
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_id: str) -> Path:
        meta = MODELS[model_id]
        target = meta.get("extract_to") or model_id
        return self.base_dir / str(target)

    def get_archive_path(self, model_id: str) -> Path:
        url = str(MODELS[model_id]["url"])
        filename = url.split("/")[-1]
        return self.base_dir / filename

    def is_downloaded(self, model_id: str) -> bool:
        model_path = self.get_model_path(model_id)
        return model_path.exists() and model_path.is_dir() and not model_path.name.endswith(
            ".extracting"
        )

    def has_partial(self, model_id: str) -> bool:
        return self.get_partial_path(model_id).exists()

    def get_partial_path(self, model_id: str) -> Path:
        archive_path = self.get_archive_path(model_id)
        return archive_path.with_suffix(archive_path.suffix + ".partial")

    def download_model(
        self,
        model_id: str,
        progress_callback: Optional[Callable[[int, Optional[int]], None]] = None,
        chunk_size: int = 8192,
    ) -> Path:
        """
        Download model archive with resume support.
        Returns path to the downloaded archive.
        """
        if self.requests is None:
            raise RuntimeError("requests is not available; cannot download model")
        meta = MODELS[model_id]
        url = str(meta["url"])
        archive_path = self.get_archive_path(model_id)
        partial_path = self.get_partial_path(model_id)

        self._emit("download-started")
        downloaded = partial_path.stat().st_size if partial_path.exists() else 0
        headers = {"Range": f"bytes={downloaded}-"} if downloaded > 0 else {}

        with self.requests.get(url, stream=True, headers=headers, timeout=60) as resp:
            if resp.status_code == 200 and downloaded > 0:
                # Server ignored Range; restart download
                partial_path.unlink(missing_ok=True)
                downloaded = 0
            resp.raise_for_status()
            expected_size = resp.headers.get("Content-Length")
            total = int(expected_size) + downloaded if expected_size else None
            partial_path.parent.mkdir(parents=True, exist_ok=True)
            with open(partial_path, "ab") as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            try:
                                progress_callback(downloaded, total)
                            except Exception:
                                pass

        if total is not None and downloaded != total:
            raise IOError(f"Incomplete download: expected {total} bytes, got {downloaded}")
        partial_path.rename(archive_path)

        # Validate checksum if available
        expected_sha256 = meta.get("sha256")
        if expected_sha256:
            self._emit("checksum-validating")
            actual_sha256 = _compute_sha256(archive_path)
            if actual_sha256 != expected_sha256:
                archive_path.unlink(missing_ok=True)
                raise IOError(
                    f"Checksum mismatch for {model_id}: "
                    f"expected {expected_sha256[:16]}..., got {actual_sha256[:16]}..."
                )
            logger.info(f"[model] Checksum verified for {model_id}")
        else:
            logger.warning(f"[model] No checksum available for {model_id}, skipping validation")

        self._emit("download-completed")
        return archive_path

    def extract_model(self, model_id: str) -> Path:
        """
        Extracts the model archive to a directory. Returns the final model path.
        """
        archive_path = self.get_archive_path(model_id)
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        target_dir = self.get_model_path(model_id)
        extracting_dir = target_dir.parent / f"{target_dir.name}.extracting"

        if extracting_dir.exists():
            # Clean previous failed extraction
            self._remove_path(extracting_dir)
        extracting_dir.mkdir(parents=True, exist_ok=True)

        self._emit("extraction-started")
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                # filter="data" for safer extraction on newer Python versions
                tar.extractall(extracting_dir, filter="data")

            nested_target = extracting_dir / target_dir.name
            source_dir = nested_target if nested_target.exists() else extracting_dir

            if target_dir.exists():
                self._remove_path(target_dir)
            source_dir.rename(target_dir)
            if extracting_dir.exists() and extracting_dir != target_dir:
                # Clean up wrapper dir if still present
                self._remove_path(extracting_dir)

            # Cleanup archive and any partials
            archive_path.unlink(missing_ok=True)
            self.get_partial_path(model_id).unlink(missing_ok=True)
            self._emit("extraction-completed")
        except Exception:
            self._emit("extraction-failed")
            raise
        return target_dir

    def cleanup_orphans(self):
        """
        Remove orphaned .partial archives and .extracting directories.
        """
        for path in self.base_dir.glob("*.partial"):
            path.unlink(missing_ok=True)
        for path in self.base_dir.glob("*.extracting"):
            self._remove_path(path)

    def _remove_path(self, path: Path):
        if path.is_file():
            path.unlink(missing_ok=True)
            return
        if path.is_dir():
            for child in path.iterdir():
                self._remove_path(child)
            path.rmdir()

    def _emit(self, name: str):
        if self.on_event:
            try:
                self.on_event(name)
            except Exception:
                pass
