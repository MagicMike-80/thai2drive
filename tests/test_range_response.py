import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from server import _range_file_response  # noqa: E402


def test_file_response_supports_full_and_range_gets(tmp_path):
    """Verify media ranges without leaving generated files in the repository."""
    test_file = tmp_path / "test_range.mp3"
    test_file.write_bytes(b"\xff\xfb\x90\x00" * 100)
    app = FastAPI()

    @app.get("/test-audio")
    def get_test_audio(request: Request):
        return _range_file_response(test_file, request, "audio/mpeg")

    client = TestClient(app)
    full = client.get("/test-audio")
    partial = client.get("/test-audio", headers={"Range": "bytes=0-100"})

    assert full.status_code == 200
    assert full.headers["content-length"] == "400"
    assert full.headers["accept-ranges"] == "bytes"
    assert partial.status_code == 206
    assert partial.headers["content-range"] == "bytes 0-100/400"
    assert partial.headers["content-length"] == "101"
