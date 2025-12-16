import tarfile
import tempfile
from pathlib import Path
import unittest

from src.managers.model import ModelManager, MODELS


class FakeResponse:
    def __init__(self, data: bytes, status_code: int = 200, headers=None):
        self.data = data
        self.status_code = status_code
        self.headers = headers or {"Content-Length": str(len(data))}
        self._iterated = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def iter_content(self, chunk_size=8192):
        for i in range(0, len(self.data), chunk_size):
            yield self.data[i : i + chunk_size]

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeRequests:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.calls = []

    def get(self, url, stream=True, headers=None, timeout=None):
        self.calls.append({"url": url, "headers": headers})
        status = 206 if headers and headers.get("Range") else 200
        content_length = len(self.payload)
        # Simulate partial by returning only remaining part if Range is set.
        if headers and headers.get("Range"):
            start = int(headers["Range"].split("=")[1].split("-")[0])
            data = self.payload[start:]
            content_length = len(data)
        else:
            data = self.payload
        return FakeResponse(data=data, status_code=status, headers={"Content-Length": str(content_length)})


class ModelManagerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        # Ensure metadata points to a known filename
        MODELS["parakeet-v3-int8"]["url"] = "https://example.com/parakeet-v3-int8.tar.gz"
        self.manager = ModelManager(base_dir=self.base, requests_module=None)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_is_downloaded_false_then_true(self):
        self.assertFalse(self.manager.is_downloaded("parakeet-v3-int8"))
        target = self.manager.get_model_path("parakeet-v3-int8")
        target.mkdir(parents=True, exist_ok=True)
        self.assertTrue(self.manager.is_downloaded("parakeet-v3-int8"))

    def test_download_and_extract(self):
        # Create a tiny tar.gz archive as payload
        temp_tar = self.base / "tmp.tar.gz"
        content_dir = self.base / "payload"
        content_dir.mkdir()
        (content_dir / "model.onnx").write_text("dummy", encoding="utf-8")
        with tarfile.open(temp_tar, "w:gz") as tar:
            tar.add(content_dir, arcname="parakeet-tdt-0.6b-v3-int8")
        payload = temp_tar.read_bytes()

        fake_requests = FakeRequests(payload)
        mgr = ModelManager(base_dir=self.base, requests_module=fake_requests)

        archive_path = mgr.download_model("parakeet-v3-int8")
        self.assertTrue(archive_path.exists())
        self.assertTrue(fake_requests.calls)

        model_path = mgr.extract_model("parakeet-v3-int8")
        self.assertTrue(model_path.exists())
        self.assertTrue((model_path / "model.onnx").exists())
        self.assertFalse(archive_path.exists())  # removed after extraction

    def test_cleanup_orphans(self):
        # Create orphan partial and extracting
        partial = self.manager.get_partial_path("parakeet-v3-int8")
        partial.parent.mkdir(parents=True, exist_ok=True)
        partial.write_bytes(b"partial")
        extracting_dir = self.manager.get_model_path("parakeet-v3-int8").with_suffix(".extracting")
        extracting_dir.mkdir(parents=True, exist_ok=True)
        (extracting_dir / "tmp").write_text("x", encoding="utf-8")

        self.manager.cleanup_orphans()
        self.assertFalse(partial.exists())
        self.assertFalse(extracting_dir.exists())


if __name__ == "__main__":
    unittest.main()
