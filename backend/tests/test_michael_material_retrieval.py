import asyncio
import unittest
from pathlib import Path

from backend.tests.test_teacher_chat_fallback import _load_teacher_chat


class _Cursor:
    def __init__(self, docs):
        self.docs = list(docs)

    async def to_list(self, length=None):
        return self.docs[:length] if length else self.docs


class _Collection:
    def __init__(self, docs):
        self.docs = list(docs)

    def find(self, query):
        def matches(doc):
            for key, value in query.items():
                if isinstance(value, dict) and "$in" in value:
                    if doc.get(key) not in value["$in"]:
                        return False
                elif doc.get(key) != value:
                    return False
            return True
        docs = [
            doc for doc in self.docs
            if matches(doc)
        ]
        return _Cursor(docs)

    async def find_one(self, query):
        for doc in self.docs:
            if all(doc.get(key) == value for key, value in query.items()):
                return doc
        return None


class _Database:
    def __init__(self, materials, videos=None, catalog=None, signs=None):
        self.collections = {
            "michael_materials": _Collection(materials),
            "learning_videos": _Collection(videos or []),
            "media_catalog": _Collection(catalog or []),
            "traffic_signs": _Collection(signs or []),
        }

    def __getitem__(self, name):
        return self.collections[name]


def _material(material_id, material_type="intersection_image", **overrides):
    item = {
        "id": material_id,
        "type": material_type,
        "source_id": "",
        "source_url": f"/api/assets/materials/{material_id}.jpg",
        "title": {"no": "Norsk tittel", "th": "ชื่อภาษาไทย", "en": "English title"},
        "caption": {"no": "Norsk forklaring", "th": "คำอธิบายภาษาไทย", "en": "English explanation"},
        "topic_tags": [],
        "sign_ids": [],
        "situation_tags": [],
        "active": True,
        "approved_for_michael": True,
        "priority": 100,
    }
    item.update(overrides)
    return item


class MichaelMaterialRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_teacher_chat()

    def retrieve(
        self, materials, message, lang="no", sign_ids=None, explicit_sign_ids=None,
        videos=None, extra_context="",
    ):
        self.module._db = _Database(materials, videos)
        return asyncio.run(self.module._get_relevant_michael_materials(
            message,
            lang,
            sign_ids=sign_ids or [],
            explicit_sign_ids=explicit_sign_ids or [],
            extra_context=extra_context,
        ))

    def test_explicit_sign_match_excludes_tag_media_and_returns_only_same_sign(self):
        materials = [
            _material("tag-first", topic_tags=["vikeplikt"], priority=1),
            _material(
                "sign-202",
                "sign",
                source_id="202_0",
                source_url="/api/sign-images/202_0.jpg",
                sign_ids=["202_0"],
                priority=900,
            ),
            _material(
                "sign-204",
                "sign",
                source_id="204_0",
                source_url="/api/sign-images/204_0.jpg",
                sign_ids=["204_0"],
            ),
            _material("video-202", "video", sign_ids=["202_0"], topic_tags=["vikeplikt"]),
            _material("tag-second", topic_tags=["vikeplikt"], priority=2),
        ]
        result = self.retrieve(
            materials,
            "Forklar vikepliktskiltet",
            sign_ids=["202_0"],
            explicit_sign_ids=["202_0"],
        )
        self.assertEqual([item["id"] for item in result], ["sign-202"])
        self.assertEqual(result[0]["sign_id"], "202_0")

    def test_exact_sign_media_uses_authoritative_sign_asset_and_selected_language(self):
        sign = {
            "id": "202_0",
            "image_url": "/api/sign-images/202_0_Vikeplikt.jpg",
            "name": {"no": "Vikeplikt", "th": "ป้ายให้ทาง", "en": "Give way"},
            "explanation": {"no": "Forklaring", "th": "คำอธิบาย", "en": "Explanation"},
            "driver_action": {"no": "Gi fri vei.", "th": "ให้ทาง", "en": "Give way."},
        }
        self.module._db = _Database([], signs=[sign])
        result = asyncio.run(self.module._get_exact_sign_media(["202_0"], "th"))
        self.assertEqual(result[0]["id"], "traffic-sign:202_0")
        self.assertEqual(result[0]["sign_id"], "202_0")
        self.assertEqual(result[0]["url"], "/api/sign-images/202_0_Vikeplikt.jpg")
        self.assertEqual(result[0]["title"], "ป้ายให้ทาง")
        self.assertEqual(result[0]["caption"], "ให้ทาง")

    def test_explicit_sign_with_incomplete_language_or_unsafe_url_is_text_only(self):
        missing_thai = _material(
            "sign-204-missing",
            "sign",
            source_id="204_0",
            source_url="/api/sign-images/204_0.jpg",
            sign_ids=["204_0"],
        )
        missing_thai["caption"]["th"] = ""
        unsafe = _material(
            "sign-204-unsafe",
            "sign",
            source_id="204_0",
            source_url="javascript:alert(1)",
            sign_ids=["204_0"],
        )
        result = self.retrieve(
            [missing_thai, unsafe],
            "อธิบายป้ายหยุด",
            lang="th",
            explicit_sign_ids=["204_0"],
        )
        self.assertEqual(result, [])

    def test_broad_context_sign_match_keeps_existing_ranked_media_flow(self):
        materials = [
            _material("tag-first", topic_tags=["vikeplikt"], priority=1),
            _material(
                "sign-202",
                "sign",
                source_id="202_0",
                source_url="/api/sign-images/202_0.jpg",
                sign_ids=["202_0"],
                priority=900,
            ),
        ]
        result = self.retrieve(materials, "Forklar vikeplikt", sign_ids=["202_0"])
        self.assertEqual([item["id"] for item in result], ["sign-202", "tag-first"])

    def test_thai_query_matches_controlled_topic_alias_and_never_borrows_norwegian(self):
        complete = _material("thai", topic_tags=["vikeplikt"])
        missing_thai = _material("missing-thai", topic_tags=["vikeplikt"])
        missing_thai["caption"]["th"] = ""
        result = self.retrieve([missing_thai, complete], "ช่วยอธิบายการให้ทาง", lang="th")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "thai")
        self.assertEqual(result[0]["title"], "ชื่อภาษาไทย")
        self.assertEqual(result[0]["caption"], "คำอธิบายภาษาไทย")

    def test_norwegian_and_english_return_only_the_selected_language(self):
        material = _material("parking", topic_tags=["parkering"])
        norwegian = self.retrieve([material], "Forklar parkering", lang="no")
        english = self.retrieve([material], "Explain parking", lang="en")
        self.assertEqual(norwegian[0]["title"], "Norsk tittel")
        self.assertEqual(norwegian[0]["caption"], "Norsk forklaring")
        self.assertEqual(english[0]["title"], "English title")
        self.assertEqual(english[0]["caption"], "English explanation")

    def test_inactive_unapproved_unsafe_and_unrelated_materials_are_hidden(self):
        materials = [
            _material("inactive", topic_tags=["stoppelengde"], active=False),
            _material("unapproved", topic_tags=["stoppelengde"], approved_for_michael=False),
            _material("unsafe", topic_tags=["stoppelengde"], source_url="javascript:alert(1)"),
            _material("unrelated", topic_tags=["parkering"]),
        ]
        self.assertEqual(self.retrieve(materials, "Hvordan regner jeg stoppelengde?"), [])

    def test_video_uses_active_source_video_url_not_thumbnail_reference(self):
        material = _material(
            "video-stop",
            "video",
            source_id="video-1",
            source_url="https://img.youtube.com/vi/abcdefghijk/mqdefault.jpg",
            topic_tags=["stoppelengde"],
        )
        videos = [{"id": "video-1", "active": True, "youtube_url": "https://youtu.be/abcdefghijk"}]
        result = self.retrieve([material], "Vis stoppelengde", videos=videos)
        self.assertEqual(result[0]["url"], "https://youtu.be/abcdefghijk")

    def test_video_uses_safe_local_asset_and_honours_learner_language(self):
        material = _material(
            "video-local",
            "video",
            source_id="video-local-1",
            source_url="/api/assets/thumbs/thumb_local.jpg",
            topic_tags=["vikeplikt"],
        )
        videos = [{
            "id": "video-local-1",
            "active": True,
            "youtube_url": "",
            "file_path": "/public_assets/video_local.mp4",
            "learner_languages": ["no"],
        }]
        norwegian = self.retrieve([material], "Forklar vikeplikt", videos=videos)
        thai = self.retrieve([material], "อธิบายการให้ทาง", lang="th", videos=videos)
        self.assertEqual(norwegian[0]["url"], "/api/assets/video_local.mp4")
        self.assertEqual(thai, [])

    def test_video_returns_only_safe_subtitle_tracks_and_audio_language(self):
        material = _material(
            "video-subtitles",
            "video",
            source_id="video-subtitles-1",
            topic_tags=["vikeplikt"],
        )
        videos = [{
            "id": "video-subtitles-1",
            "active": True,
            "file_path": "/public_assets/video_subtitles.mp4",
            "audio_language": "no",
            "learner_languages": ["no", "th"],
            "subtitle_tracks": [
                {"lang": "th", "label": "ไทย", "url": "/api/assets/subtitles/video.th.vtt"},
                {"lang": "xx", "label": "Bad", "url": "/api/assets/subtitles/bad.vtt"},
                {"lang": "en", "label": "Bad URL", "url": "javascript:alert(1)"},
            ],
        }]
        result = self.retrieve([material], "อธิบายการให้ทาง", lang="th", videos=videos)
        self.assertEqual(result[0]["audio_language"], "no")
        self.assertEqual(result[0]["subtitle_tracks"], [{
            "lang": "th",
            "label": "ไทย",
            "url": "/api/assets/subtitles/video.th.vtt",
        }])

    def test_empty_library_is_text_only_and_response_contract_is_additive(self):
        self.assertEqual(self.retrieve([], "vikeplikt"), [])
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("media: list[dict] = Field(default_factory=list)", source)
        self.assertIn("sign_ids: list[str] = Field(default_factory=list)", source)
        self.assertIn("media=media", source)

    def test_catalog_composition_is_bounded_and_exact_sign_stays_exclusive(self):
        approved = [{"id": "approved", "type": "video"}]
        catalog = [{"id": "catalog", "type": "podcast"}]
        self.assertEqual(
            [item["id"] for item in self.module._compose_teacher_media(approved, catalog)],
            ["catalog", "approved"],
        )
        self.assertEqual(
            self.module._compose_teacher_media(approved, catalog, ["204_0"]),
            approved,
        )

    def test_final_response_keeps_approved_video_and_prefers_exact_sign(self):
        video = {"id": "video", "type": "video"}
        correct_sign = {"id": "sign", "type": "sign", "sign_id": "202_0"}
        unrelated_sign = {"id": "other", "type": "sign", "sign_id": "204_0"}
        self.assertEqual(
            self.module._reconcile_teacher_media([video], [], []),
            [video],
        )
        self.assertEqual(
            self.module._reconcile_teacher_media(
                [video, unrelated_sign], ["202_0"], [correct_sign]
            ),
            [correct_sign, video],
        )

    def test_invalid_language_never_queries_catalog(self):
        self.assertEqual(
            asyncio.run(self.module._get_relevant_catalog_media("stoppelengde", "nb")),
            [],
        )

    def test_paragraf_7_and_venstresving_queries_match_the_7_2_tagged_image(self):
        target = _material(
            "sit_vike_venstre_01",
            topic_tags=["7", "7_2", "vikeplikt", "høyreregel", "venstresving", "møtende"],
        )
        unrelated = _material("unrelated", topic_tags=["parkering"])
        for query in ("Hva sier paragraf 7 om dette?", "vikeplikt venstresving i kryss"):
            with self.subTest(query=query):
                result = self.retrieve([unrelated, target], query)
                self.assertEqual([item["id"] for item in result], ["sit_vike_venstre_01"])

    def test_bussregelen_query_matches_7_5_not_generic_7_2_image(self):
        bus_rule = _material(
            "sit_buss_regel_01",
            topic_tags=["7", "7_5", "bussregelen", "vikeplikt_buss"],
        )
        venstresving = _material(
            "sit_vike_venstre_01",
            topic_tags=["7", "7_2", "vikeplikt", "høyreregel", "venstresving"],
        )
        result = self.retrieve([venstresving, bus_rule], "paragraf 7 nr 5 om bussregelen")
        self.assertEqual([item["id"] for item in result], ["sit_buss_regel_01", "sit_vike_venstre_01"])

    def test_catalog_lookup_returns_one_language_pure_exact_tag_match(self):
        catalog = []
        for media_id, language, title in (
            ("no-item", "no", "Norsk"),
            ("th-item", "th", "ไทย"),
        ):
            catalog.append({
                "media_id": media_id,
                "type": "video",
                "category": "stoppelengde",
                "tags": ["stoppelengde"],
                "media_url": "https://media.example/video.mp4",
                "thumbnail_url": "https://media.example/thumb.jpg",
                "is_active": True,
                "content_language": language,
                "i18n": {
                    "no": {"title": "Norsk", "description": "Norsk beskrivelse"},
                    "th": {"title": "ไทย", "description": "คำอธิบาย"},
                    "en": {"title": "English", "description": "Description"},
                },
            })
        self.module._db = _Database([], catalog=catalog)
        result = asyncio.run(
            self.module._get_relevant_catalog_media("Forklar stoppelengde", "no")
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "no-item")
        self.assertEqual(result[0]["title"], "Norsk")
        self.assertNotIn("i18n", result[0])


if __name__ == "__main__":
    unittest.main()
