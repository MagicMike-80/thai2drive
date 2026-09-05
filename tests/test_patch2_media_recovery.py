from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from backend.streaming_helpers import RangeNotSatisfiable, gridfs_content_type, parse_byte_range
from backend.video_thumbnails import normalize_video_thumbnail_url, thumbnail_url_for_video


ROOT = Path(__file__).resolve().parents[1]
SERVER = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")
SCRIPT_PATH = ROOT / "backend" / "scripts" / "fix_video_thumbnail_paths.py"
SPEC = importlib.util.spec_from_file_location("fix_video_thumbnail_paths", SCRIPT_PATH)
SCRIPT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(SCRIPT)


class LegacyGridOut:
    length = 100


class Patch2MediaRecoveryTests(unittest.TestCase):
    def test_legacy_gridfs_metadata_fails_soft(self):
        self.assertEqual(gridfs_content_type(LegacyGridOut()), "audio/mpeg")
        snake = type("GridOut", (), {"metadata": {"content_type": "audio/mp4"}})()
        camel = type("GridOut", (), {"metadata": {"contentType": "video/mp4"}})()
        self.assertEqual(gridfs_content_type(snake), "audio/mp4")
        self.assertEqual(gridfs_content_type(camel), "video/mp4")

    def test_range_contract(self):
        self.assertIsNone(parse_byte_range("", 100))
        self.assertEqual(parse_byte_range("bytes=0-0", 100), (0, 0))
        self.assertEqual(parse_byte_range("bytes=90-200", 100), (90, 99))
        self.assertEqual(parse_byte_range("bytes=90-", 100), (90, 99))
        self.assertEqual(parse_byte_range("bytes=-10", 100), (90, 99))
        for value in ("bytes=100-", "bytes=20-10", "bytes=-0", "bytes=0-1,4-5"):
            with self.subTest(value=value), self.assertRaises(RangeNotSatisfiable):
                parse_byte_range(value, 100)

    def test_server_route_uses_gridfs_helpers_and_range_headers(self):
        self.assertIn("ct = gridfs_content_type(doc)", SERVER)
        self.assertIn("byte_range = parse_byte_range(range_hdr, total)", SERVER)
        self.assertIn('"Content-Range": f"bytes {start}-{end}/{total}"', SERVER)
        self.assertIn('"Content-Length": str(length)', SERVER)
        self.assertIn("status_code=206", SERVER)
        self.assertIn("status_code=416", SERVER)

    def test_all_30_local_thumbnail_mappings_resolve_to_existing_files(self):
        thumbnail_dir = ROOT / "backend" / "public_assets" / "thumbs"
        files = sorted(thumbnail_dir.glob("thumb_*.jpg"))
        self.assertEqual(len(files), 30)
        for target in files:
            suffix = target.stem.removeprefix("thumb_")
            file_path = f"/public_assets/video_{suffix}.mp4"
            legacy = f"/api/assets/thumbs/thumb_video_{suffix}.jpg"
            corrected = normalize_video_thumbnail_url(legacy, file_path)
            self.assertEqual(corrected, f"/api/assets/thumbs/{target.name}")

    def test_thumbnail_normalizer_preserves_valid_urls(self):
        local = "/api/assets/thumbs/thumb_michaels_gatelogikk.jpg"
        external = "https://img.youtube.com/vi/abcdefghijk/mqdefault.jpg"
        self.assertEqual(normalize_video_thumbnail_url(local, "/public_assets/video_michaels_gatelogikk.mp4"), local)
        self.assertEqual(normalize_video_thumbnail_url(external, "/public_assets/video_x.mp4"), external)
        self.assertEqual(thumbnail_url_for_video("/public_assets/video_michaels_gatelogikk.mp4"), local)

    def test_database_script_only_proposes_exact_legacy_paths(self):
        legacy = {
            "id": "one",
            "file_path": "/public_assets/video_michaels_gatelogikk.mp4",
            "thumbnail_url": "/api/assets/thumbs/thumb_video_michaels_gatelogikk.jpg",
        }
        self.assertEqual(SCRIPT.proposed_update(legacy), "/api/assets/thumbs/thumb_michaels_gatelogikk.jpg")
        self.assertEqual(SCRIPT.proposed_update({**legacy, "thumbnail_url": "https://example.com/thumb.jpg"}), "")


if __name__ == "__main__":
    unittest.main()
