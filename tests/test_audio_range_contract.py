import ast
import asyncio
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
    def __init__(self, content=None, status_code=200, headers=None, **_kwargs):
        self.content = content
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


def _load_static_handlers(static_root):
    tree = ast.parse(SERVER_PATH.read_text(encoding="utf-8"))
    functions = []
    for name in ("_range_file_response", "static_video", "static_image"):
        node = next(item for item in tree.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name)
        node.decorator_list = []
        functions.append(node)
    namespace = {
        "Path": Path,
        "Request": _Request,
        "Optional": Optional,
        "FileResponse": _FileResponse,
        "StreamingResponse": _StreamingResponse,
        "Response": _Response,
        "HTMLResponse": _Response,
        "re": re,
        "_STATIC_MEDIA_DIR": Path(static_root),
    }
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SERVER_PATH), "exec"), namespace)
    return namespace["static_video"], namespace["static_image"]


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


class StaticMediaRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        (root / "videos").mkdir()
        (root / "images").mkdir()
        (root / "videos" / "lesson.mp4").write_bytes(bytes(range(100)))
        (root / "images" / "lesson.jpg").write_bytes(b"jpeg-bytes")
        self.video, self.image = _load_static_handlers(root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_video_route_supports_full_and_range_gets(self):
        full = asyncio.run(self.video("lesson.mp4", _Request()))
        partial = asyncio.run(self.video("lesson.mp4", _Request("bytes=10-19")))
        self.assertIsInstance(full, _FileResponse)
        self.assertEqual(full.media_type, "video/mp4")
        self.assertEqual(partial.status_code, 206)
        self.assertEqual(b"".join(partial.body), bytes(range(10, 20)))

    def test_video_route_rejects_missing_wrong_extension_and_traversal(self):
        for name in ("missing.mp4", "lesson.jpg", "../lesson.mp4"):
            with self.subTest(name=name):
                response = asyncio.run(self.video(name, _Request()))
                self.assertEqual(response.status_code, 404)

    def test_image_route_serves_jpeg_and_rejects_invalid_files(self):
        image = asyncio.run(self.image("lesson.jpg"))
        self.assertIsInstance(image, _FileResponse)
        self.assertEqual(image.media_type, "image/jpeg")
        for name in ("missing.jpg", "lesson.gif", "../lesson.jpg"):
            with self.subTest(name=name):
                response = asyncio.run(self.image(name))
                self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
