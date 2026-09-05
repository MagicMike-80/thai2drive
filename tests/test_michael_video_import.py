import asyncio
import tempfile
import unittest
from pathlib import Path

from backend.michael_video_import import (
    VIDEO_SPECS,
    learning_video_document,
    michael_material_document,
)
from backend.tests.test_michael_material_retrieval import _material
from backend.tests.test_teacher_chat_fallback import _load_teacher_chat


ROOT = Path(__file__).resolve().parents[1]


class _Collection:
    def __init__(self, docs):
        self.docs = docs

    def find(self, query):
        docs = [
            doc for doc in self.docs
            if all(doc.get(key) == value for key, value in query.items())
        ]
        return _Cursor(docs)

    async def find_one(self, query):
        for doc in self.docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None


class _Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return self.docs[:length] if length else self.docs


class _Database:
    def __init__(self, materials, videos):
        self.collections = {
            "michael_materials": _Collection(materials),
            "learning_videos": _Collection(videos),
        }

    def __getitem__(self, name):
        return self.collections[name]


class MichaelVideoImportTests(unittest.TestCase):
    def test_deploy_bundle_contains_25_complete_unique_video_sets(self):
        asset_root = ROOT / "backend" / "public_assets"
        self.assertEqual(len(VIDEO_SPECS), 25)
        self.assertEqual(len({spec.video_id for spec in VIDEO_SPECS}), 25)
        for spec in VIDEO_SPECS:
            with self.subTest(spec=spec.slug):
                self.assertGreater((asset_root / spec.asset_name).stat().st_size, 0)
                self.assertGreater((asset_root / "thumbs" / spec.thumbnail_name).stat().st_size, 0)
                self.assertGreater((asset_root / "subtitles" / spec.subtitle_name).stat().st_size, 0)

    def test_records_are_language_complete_safe_and_draft_by_default(self):
        self.assertEqual(len(VIDEO_SPECS), 25)
        for spec in VIDEO_SPECS:
            with self.subTest(spec=spec.slug):
                video = learning_video_document(spec)
                material = michael_material_document(spec)
                self.assertRegex(spec.asset_name, r"^video_[a-z0-9_]+\.mp4$")
                self.assertTrue(video["file_path"].startswith("/public_assets/video_"))
                self.assertTrue(video["thumbnail_url"].startswith("/api/assets/thumbs/thumb_"))
                self.assertEqual(video["audio_language"], "no")
                self.assertEqual(video["learner_languages"], ["no", "th"])
                self.assertEqual(video["subtitle_tracks"][0]["lang"], "th")
                self.assertTrue(video["subtitle_tracks"][0]["url"].endswith(".th.vtt"))
                self.assertEqual(set(material["title"]), {"no", "th", "en"})
                self.assertEqual(set(material["caption"]), {"no", "th", "en"})
                self.assertTrue(all(material["title"].values()))
                self.assertTrue(all(material["caption"].values()))
                self.assertFalse(video["active"])
                self.assertFalse(material["active"])
                self.assertFalse(material["approved_for_michael"])

    def test_publish_is_an_explicit_switch(self):
        spec = VIDEO_SPECS[0]
        self.assertTrue(learning_video_document(spec, publish=True)["active"])
        material = michael_material_document(spec, publish=True)
        self.assertTrue(material["active"])
        self.assertTrue(material["approved_for_michael"])

    def test_michael_resolves_local_asset_through_api_route(self):
        module = _load_teacher_chat()
        spec = next(item for item in VIDEO_SPECS if item.slug == "vikeplikt_7_5a_buss")
        material = _material(
            spec.material_id,
            "video",
            source_id=spec.video_id,
            source_url=f"/api/assets/{spec.asset_name}",
            title=spec.titles,
            caption=spec.captions,
            topic_tags=list(spec.topic_tags),
        )
        video = learning_video_document(spec, publish=True)
        module._db = _Database([material], [video])
        result = asyncio.run(module._get_relevant_michael_materials(
            "Forklar bussregelen ved 60 km/t",
            "no",
        ))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], f"/api/assets/{spec.asset_name}")

    def test_all_thai_subtitles_exist_and_bus_rule_uses_60_not_50(self):
        subtitle_dir = ROOT / "backend" / "public_assets" / "subtitles"
        subtitles = [subtitle_dir / spec.subtitle_name for spec in VIDEO_SPECS]
        self.assertTrue(all(path.is_file() for path in subtitles))
        for path in subtitles:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("WEBVTT\n\n"))
            self.assertRegex(text, r"[\u0E00-\u0E7F]")
        bus = (subtitle_dir / "video_vikeplikt_7_5a_buss.th.vtt").read_text(encoding="utf-8")
        self.assertIn("60", bus)
        self.assertNotIn("50", bus)

    def test_local_database_guard_rejects_remote_uri(self):
        from backend.scripts import import_michael_videos as importer

        old_value = importer.os.environ.get("MONGO_URL")
        try:
            importer.os.environ["MONGO_URL"] = "https://database.example.invalid/prod"
            with self.assertRaisesRegex(RuntimeError, "localhost"):
                importer._local_mongo_uri()
        finally:
            if old_value is None:
                importer.os.environ.pop("MONGO_URL", None)
            else:
                importer.os.environ["MONGO_URL"] = old_value


if __name__ == "__main__":
    unittest.main()
