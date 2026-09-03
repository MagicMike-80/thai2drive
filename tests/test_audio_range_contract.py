import ast
import re
import tempfile
import unittest
from pathlib import Path
from typing import Optional


SERVER_PATH = Path(__file__).resolve().parents[1] / "backend" / "server.py"


class _Request:
    def __init__(self, range_header=""):
        self.headers = {"range": range_header} if range_header else {}


class _Response:
    def __init__(self, status_code=200, headers=None, **_kwargs):
        self.status_code = status_code
        self.headers = headers or {}


class _FileResponse(_Response):
    def __init__(self, path, media_type=None, headers=None, **kwargs):
        super().__init__(headers=headers, **kwargs)
        self.path = path
        self.media_type = media_type


class _StreamingResponse(_Response):
    def __init__(self, body, status_code=200, media_type=None, headers=None, **kwargs):
        super().__init__(status_code=status_code, headers=headers, **kwargs)
        self.body = body
        self.media_type = media_type


def _load_range_helper():
    tree = ast.parse(SERVER_PATH.read_text(encoding="utf-8"))
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_range_file_response"
    )
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {
        "Path": Path,
        "Request": _Request,
        "Optional": Optional,
        "FileResponse": _FileResponse,
        "StreamingResponse": _StreamingResponse,
        "Response": _Response,
        "re": re,
    }
    exec(compile(module, str(SERVER_PATH), "exec"), namespace)
    return namespace["_range_file_response"]


class AudioRangeContractTests(unittest.TestCase):
    def setUp(self):
        self.helper = _load_range_helper()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.audio_path = Path(self.temp_dir.name) / "audio.mp3"
        self.audio_path.write_bytes(bytes(range(100)))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_full_get_uses_file_response(self):
        response = self.helper(self.audio_path, _Request(), "audio/mpeg")
        self.assertIsInstance(response, _FileResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Accept-Ranges"], "bytes")

    def test_valid_range_returns_exact_partial_content(self):
        response = self.helper(self.audio_path, _Request("bytes=10-19"), "audio/mpeg")
        self.assertIsInstance(response, _StreamingResponse)
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response.headers["Content-Range"], "bytes 10-19/100")
        self.assertEqual(response.headers["Content-Length"], "10")
        self.assertEqual(b"".join(response.body), bytes(range(10, 20)))

    def test_invalid_range_returns_416(self):
        response = self.helper(self.audio_path, _Request("bytes=100-120"), "audio/mpeg")
        self.assertEqual(response.status_code, 416)
        self.assertEqual(response.headers["Content-Range"], "bytes */100")


if __name__ == "__main__":
    unittest.main()
