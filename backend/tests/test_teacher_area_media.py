"""Selected-area media must expose only explicitly approved learner content."""

import asyncio
import unittest
from unittest.mock import patch

from backend.tests.test_teacher_chat_fallback import _load_teacher_chat


tc = _load_teacher_chat()


class _Cursor:
    def __init__(self, documents):
        self.documents = documents

    async def to_list(self, length=None):
        return self.documents[:length]


class _Collection:
    def __init__(self, documents):
        self.documents = documents
        self.query = None

    def find(self, query):
        self.query = query
        return _Cursor(self.documents)


class _DB:
    def __init__(self, documents):
        self.collection = _Collection(documents)

    def __getitem__(self, name):
        assert name == "media_catalog"
        return self.collection


def _item(media_id="approved", **changes):
    document = {
        "media_id": media_id,
        "type": "video",
        "category": "stoppelengde",
        "learning_area_id": "speed_distance",
        "tags": ["stoppelengde"],
        "media_url": "https://media.example/video.mp4",
        "thumbnail_url": "/api/assets/thumbs/video.jpg",
        "is_active": True,
        "approved_for_michael": True,
        "approved_for_teacher": True,
        "content_language": "neutral",
        "i18n": {
            "no": {"title": "Norsk tittel", "description": "Norsk beskrivelse"},
            "th": {"title": "ชื่อภาษาไทย", "description": "คำอธิบายภาษาไทย"},
            "en": {"title": "English title", "description": "English description"},
        },
        "correct_answer": "PRIVATE-ANSWER",
    }
    document.update(changes)
    return document


class TeacherAreaMediaTests(unittest.TestCase):
    def test_only_exact_active_double_approved_area_is_returned(self):
        database = _DB([
            _item(),
            _item("inactive", is_active=False),
            _item("not_teacher_approved", approved_for_teacher=False),
            _item("not_michael_approved", approved_for_michael=False),
            _item("other_area", learning_area_id="right_of_way"),
        ])
        with patch.object(tc, "_db", database):
            for language, title in (
                ("no", "Norsk tittel"),
                ("th", "ชื่อภาษาไทย"),
                ("en", "English title"),
            ):
                with self.subTest(language=language):
                    result = asyncio.run(tc.teacher_area_media(language, "speed_distance"))
                    self.assertEqual([item["media_id"] for item in result["media"]], ["approved"])
                    self.assertEqual(result["media"][0]["title"], title)
                    self.assertNotIn("PRIVATE-ANSWER", str(result))
                    self.assertEqual(database.collection.query["approved_for_teacher"], True)
                    self.assertEqual(database.collection.query["learning_area_id"], "speed_distance")

    def test_unknown_language_or_area_is_rejected(self):
        for language, area in (("xx", "speed_distance"), ("no", "unknown")):
            with self.subTest(language=language, area=area):
                with self.assertRaises(tc.HTTPException) as raised:
                    asyncio.run(tc.teacher_area_media(language, area))
                self.assertEqual(raised.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
