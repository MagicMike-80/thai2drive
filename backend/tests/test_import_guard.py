import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.scripts.import_michael_videos import validate_video_spec


class TestImportGuard(unittest.TestCase):
    def test_complete_translation_passes(self):
        spec = SimpleNamespace(
            media_id="michael_test_video",
            title_no="Klar tittel",
            title_th="ชื่อเรื่องภาษาไทย",
            title_en="English title",
        )
        # Should not raise
        validate_video_spec(spec)

    def test_no_needs_translation_raises(self):
        spec = SimpleNamespace(
            media_id="michael_vikeplikt_1",
            title_no="NEEDS_TRANSLATION",
            title_th="ชื่อเรื่อง",
            title_en="Title",
        )
        with self.assertRaises(ValueError) as ctx:
            validate_video_spec(spec)
        self.assertIn("NO translation incomplete: michael_vikeplikt_1", str(ctx.exception))

    def test_th_needs_translation_raises(self):
        spec = SimpleNamespace(
            media_id="michael_vikeplikt_2",
            title_no="Tittel",
            title_th="NEEDS_TRANSLATION",
            title_en="Title",
        )
        with self.assertRaises(ValueError) as ctx:
            validate_video_spec(spec)
        self.assertIn("TH translation required: michael_vikeplikt_2", str(ctx.exception))

    def test_en_needs_translation_raises(self):
        spec = SimpleNamespace(
            media_id="michael_vikeplikt_3",
            title_no="Tittel",
            title_th="ชื่อเรื่อง",
            title_en="NEEDS_TRANSLATION",
        )
        with self.assertRaises(ValueError) as ctx:
            validate_video_spec(spec)
        self.assertIn("EN translation required: michael_vikeplikt_3", str(ctx.exception))

    def test_dict_spec_needs_translation_raises(self):
        spec = {
            "media_id": "michael_dict_1",
            "title_no": "Tittel",
            "title_th": "NEEDS_TRANSLATION",
            "title_en": "Title",
        }
        with self.assertRaises(ValueError) as ctx:
            validate_video_spec(spec)
        self.assertIn("TH translation required: michael_dict_1", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
