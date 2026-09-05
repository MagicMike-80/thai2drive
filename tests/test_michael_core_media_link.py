import asyncio
import json
import tempfile
import types
import unittest
from pathlib import Path

from backend.scripts.link_michael_core_media import (
    BUS_MATERIAL_ID,
    BUS_VIDEO_ID,
    RIGHT_RULE_MATERIAL,
    SIGN_ID,
    apply_link,
    rollback_link,
    validate_material,
    verify_existing_sources,
)
from backend.tests.test_teacher_chat_fallback import _load_teacher_chat
from backend.tests.test_michael_material_retrieval import _Database as _TeacherDatabase


class _Result:
    matched_count = 0
    modified_count = 0
    upserted_id = "new"
    deleted_count = 1


class _Collection:
    def __init__(self, documents):
        self.documents = {document["id"]: dict(document) for document in documents}

    def find_one(self, query):
        for document in self.documents.values():
            if all(document.get(key) == value for key, value in query.items()):
                return dict(document)
        return None

    def update_one(self, query, update, upsert=False):
        document = self.documents.get(query["id"], {})
        document.update(update.get("$setOnInsert", {}))
        document.update(update["$set"])
        self.documents[query["id"]] = document
        return _Result()

    def delete_one(self, query):
        self.documents.pop(query["id"], None)
        return _Result()

    def replace_one(self, query, document, upsert=False):
        self.documents[query["id"]] = dict(document)
        return _Result()


class _Database:
    def __init__(self):
        localized = {"no": "Norsk", "th": "ไทย", "en": "English"}
        self.learning_videos = _Collection([{
            "id": BUS_VIDEO_ID,
            "active": True,
            "file_path": "/public_assets/video_vikeplikt_7_5a_buss.mp4",
            "thumbnail_url": "/api/assets/thumbs/thumb_vikeplikt_7_5a_buss.jpg",
            "learner_languages": ["no", "th"],
            "subtitle_tracks": [{
                "lang": "th",
                "url": "/api/assets/subtitles/video_vikeplikt_7_5a_buss.th.vtt",
            }],
        }])
        self.michael_materials = _Collection([{
            "id": BUS_MATERIAL_ID,
            "type": "video",
            "active": True,
            "approved_for_michael": True,
            "source_id": BUS_VIDEO_ID,
            "title": {key: f"{value} 60" for key, value in localized.items()},
            "caption": {key: f"{value} 60" for key, value in localized.items()},
            "topic_tags": ["7_5", "bussregelen", "60_km_t"],
        }])
        self.traffic_signs = _Collection([{
            "id": SIGN_ID,
            "image_url": "/api/sign-images/202_0.jpg",
            "name": localized,
            "explanation": localized,
            "driver_action": localized,
        }])


class _AsyncCursor:
    def __init__(self, documents):
        self.documents = [dict(document) for document in documents]

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return self.documents[:length] if length is not None else self.documents


class _AsyncCollection:
    def __init__(self, documents=()):
        self.documents = [dict(document) for document in documents]

    def find(self, query):
        matches = [
            document for document in self.documents
            if all(document.get(key) == value for key, value in query.items())
        ]
        return _AsyncCursor(matches)

    async def find_one(self, query):
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return dict(document)
        return None

    async def insert_one(self, document):
        self.documents.append(dict(document))

    async def insert_many(self, documents):
        self.documents.extend(dict(document) for document in documents)


class _AsyncDatabase:
    def __init__(self):
        self.collections = {
            "michael_materials": _AsyncCollection([RIGHT_RULE_MATERIAL]),
            "learning_videos": _AsyncCollection(),
            "teacher_chat_logs": _AsyncCollection(),
        }

    def __getitem__(self, key):
        return self.collections.setdefault(key, _AsyncCollection())

    def __getattr__(self, key):
        return self[key]


class MichaelCoreMediaLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.teacher = _load_teacher_chat()

    def test_right_rule_material_is_language_complete_and_local(self):
        validate_material(RIGHT_RULE_MATERIAL)
        self.assertEqual(RIGHT_RULE_MATERIAL["source_url"], "/api/assets/michael_hoyreregel.svg")

    def test_all_linked_asset_paths_exist_in_the_deploy_tree(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "backend/media_catalog_manifest.json").read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in manifest["items"]}
        self.assertTrue((root / "backend/public_assets/michael_hoyreregel.svg").is_file())
        self.assertTrue((root / "backend/public_assets/thumbs/thumb_vikeplikt_7_5a_buss.jpg").is_file())
        self.assertTrue((root / "backend/sign_images/202_0.jpg").is_file())
        self.assertEqual(by_id["sit_kryss_hoyreregel_7"]["url"], RIGHT_RULE_MATERIAL["source_url"])
        self.assertEqual(by_id["sit_buss_7_5"]["tags"], ["#7", "#7_5", "#bussregelen", "#vikeplikt_buss"])

    def test_michael_retrieves_right_rule_image_in_all_languages(self):
        self.teacher._db = _TeacherDatabase([RIGHT_RULE_MATERIAL])
        cases = (
            ("no", "Vis meg bilde av høyreregelen", "Høyreregelen"),
            ("th", "ขอภาพกฎให้ทางจากขวา", "กฎให้ทาง"),
            ("en", "Show me the right-hand rule image", "right-hand rule"),
        )
        for language, question, expected_title in cases:
            with self.subTest(language=language):
                result = asyncio.run(self.teacher._get_relevant_michael_materials(question, language))
                self.assertEqual(result[0]["id"], RIGHT_RULE_MATERIAL["id"])
                self.assertIn(expected_title, result[0]["title"])
                self.assertEqual(result[0]["url"], RIGHT_RULE_MATERIAL["source_url"])

    def test_apply_requires_and_preserves_bus_and_sign_links(self):
        database = _Database()
        proof = verify_existing_sources(database)
        self.assertEqual(proof["bus_video"], BUS_VIDEO_ID)
        self.assertEqual(proof["traffic_sign"], SIGN_ID)
        with tempfile.TemporaryDirectory() as directory:
            result = apply_link(database, Path(directory))
            self.assertTrue(Path(result["snapshot"]).exists())
        linked = database.michael_materials.find_one({"id": RIGHT_RULE_MATERIAL["id"]})
        self.assertTrue(linked["active"])
        self.assertTrue(linked["approved_for_michael"])

    def test_snapshot_can_remove_a_newly_inserted_link(self):
        database = _Database()
        with tempfile.TemporaryDirectory() as directory:
            result = apply_link(database, Path(directory))
            rollback = rollback_link(database, Path(result["snapshot"]))
        self.assertEqual(rollback["rollback"], "delete_inserted")
        self.assertIsNone(database.michael_materials.find_one({"id": RIGHT_RULE_MATERIAL["id"]}))

    def test_apply_stops_when_bus_material_is_missing(self):
        database = _Database()
        database.michael_materials = _Collection([])
        with self.assertRaisesRegex(RuntimeError, "bus material"):
            verify_existing_sources(database)

    def test_apply_stops_when_bus_material_points_to_the_wrong_video(self):
        database = _Database()
        database.michael_materials.documents[BUS_MATERIAL_ID]["source_id"] = "wrong-video"
        with self.assertRaisesRegex(RuntimeError, "not linked"):
            verify_existing_sources(database)

    def test_right_rule_explanation_is_complete_and_language_isolated(self):
        cases = (
            ("no", "Kan du forklare høyreregelen?", "Senk farten", "กฎ"),
            ("th", "อธิบายกฎให้ทางจากขวา", "ลดความเร็ว", "Høyreregelen"),
            ("en", "Explain the right-hand rule", "Slow down", "Høyreregelen"),
        )
        for language, question, expected, forbidden in cases:
            with self.subTest(language=language):
                answer = self.teacher._apply_right_rule_definition_fail_safe(
                    question, "truncated", language
                )
                self.assertIn(expected, answer)
                self.assertNotIn(forbidden, answer)
                self.assertTrue(answer.endswith((".", "ครับ")))

    def test_left_turn_specific_answer_is_not_overwritten(self):
        answer = self.teacher._apply_right_rule_definition_fail_safe(
            "Gjelder høyreregelen når jeg svinger til venstre for en møtende bil?",
            "specific-left-turn-answer",
            "no",
        )
        self.assertEqual(answer, "specific-left-turn-answer")

    def test_application_and_exception_questions_are_not_overwritten(self):
        questions = (
            "Gjelder høyreregelen når jeg kjører ut fra en parkeringsplass?",
            "Når gjelder ikke høyreregelen?",
            "Kan du forklare når høyreregelen ikke gjelder?",
            "Show me a video about the right-hand rule",
            "Explain whether the right-hand rule applies when leaving a parking lot",
            "อธิบายว่ากฎให้ทางจากขวาไม่ใช้เมื่อใด",
        )
        for question in questions:
            with self.subTest(question=question):
                answer = self.teacher._apply_right_rule_definition_fail_safe(
                    question, "specific-answer", "no"
                )
                self.assertEqual(answer, "specific-answer")

    def test_unknown_language_fails_stop_without_norwegian_fallback(self):
        answer = self.teacher._apply_right_rule_definition_fail_safe(
            "Forklar høyreregelen", "neutral", "xx"
        )
        self.assertEqual(answer, "neutral")

    def test_teacher_chat_response_contains_complete_reply_and_image_card(self):
        module = self.teacher
        originals = {
            "_db": module._db,
            "_chat_col": module._chat_col,
            "_get_curriculum_context": module._get_curriculum_context,
            "_get_exact_sign_media": module._get_exact_sign_media,
            "_get_relevant_catalog_media": module._get_relevant_catalog_media,
            "_completion_with_fallback": module._completion_with_fallback,
            "TeacherChatResponse": module.TeacherChatResponse,
            "LLM_KEY": module.LLM_KEY,
        }

        async def no_context(*args, **kwargs):
            return ""

        async def no_media(*args, **kwargs):
            return []

        async def truncated_completion(*args, **kwargs):
            message = types.SimpleNamespace(content="Høyreregelen gjelder fra høyre.")
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=message)])

        try:
            module._db = _AsyncDatabase()
            module._chat_col = _AsyncCollection()
            module._get_curriculum_context = no_context
            module._get_exact_sign_media = no_media
            module._get_relevant_catalog_media = no_media
            module._completion_with_fallback = truncated_completion
            module.TeacherChatResponse = lambda **kwargs: types.SimpleNamespace(**kwargs)
            module.LLM_KEY = "test-key"
            request = types.SimpleNamespace(
                session_id=None,
                message="Kan du forklare høyreregelen og vise bilde?",
                language="no",
                device_id=None,
                user_id=None,
            )
            response = asyncio.run(module.teacher_chat(request))
        finally:
            for name, value in originals.items():
                setattr(module, name, value)

        self.assertIn("Senk farten", response.reply)
        self.assertEqual(response.media[0]["id"], RIGHT_RULE_MATERIAL["id"])
        self.assertEqual(response.media[0]["url"], RIGHT_RULE_MATERIAL["source_url"])


if __name__ == "__main__":
    unittest.main()
