"""
Language isolation audit — teacher_chat.py
--------------------------------------------
Unit tests for the Fail-Stop language-purity fixes: no Norwegian-fallback
dict lookups, no raw database category keys leaking into a reply, and no
cross-language conversation context bleeding into a session after the user
switches language.

Runs fully offline against fake Mongo collections — never touches the
production BASE_URL the rest of this repo's pytest suites hit (see CLAUDE.md).
"""
import asyncio
import sys
import unittest
from pathlib import Path

import pydantic

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import backend.teacher_chat as tc
from backend.teacher_chat import TeacherChatRequest


class _Cursor:
    def __init__(self, items=None):
        self.items = items or []

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return list(self.items[:length]) if length else list(self.items)


class _RecordingCollection:
    """Fake Mongo collection that records inserted docs and find() filters."""

    def __init__(self, aggregate_result=None, find_one_result=None, find_result=None):
        self.aggregate_result = aggregate_result or []
        self.find_one_result = find_one_result
        self.find_result = find_result or []
        self.find_calls = []
        self.inserted = []

    def aggregate(self, pipeline):
        return _Cursor(self.aggregate_result)

    def find(self, filter_=None, *args, **kwargs):
        self.find_calls.append(filter_)
        return _Cursor(self.find_result)

    async def find_one(self, *args, **kwargs):
        return self.find_one_result

    async def insert_one(self, doc):
        self.inserted.append(doc)

    async def insert_many(self, docs):
        self.inserted.extend(docs)


class _Database(dict):
    def __getitem__(self, key):
        return dict.get(self, key) or _RecordingCollection()


class StrictLangHelperTests(unittest.TestCase):
    def test_missing_language_returns_none(self):
        self.assertIsNone(tc._strict_lang_map({"no": "Norsk", "en": "English"}, "th"))

    def test_present_language_returns_value(self):
        self.assertEqual(tc._strict_lang_map({"no": "Norsk", "th": "ไทย"}, "th"), "ไทย")

    def test_blank_string_counts_as_missing(self):
        self.assertIsNone(tc._strict_lang_map({"no": "Norsk", "th": "   "}, "th"))

    def test_empty_list_counts_as_missing(self):
        self.assertIsNone(tc._strict_lang_map({"no": ["a"], "th": []}, "th"))

    def test_non_dict_input_returns_none(self):
        self.assertIsNone(tc._strict_lang_map(None, "th"))


class StudentWeaknessNeverLeaksRawKeyTests(unittest.TestCase):
    def setUp(self):
        self._orig_db = tc._db
        tc._db = _Database()

    def tearDown(self):
        tc._db = self._orig_db

    def test_unmapped_category_from_quiz_attempts_returns_none(self):
        tc._db["quiz_attempts"] = _RecordingCollection(
            aggregate_result=[{"_id": "fart_og_bremsing", "fails": 3}]
        )
        tc._db["mistakes"] = _RecordingCollection()
        result = asyncio.run(tc._get_student_weakness(device_id="d1", lang="th"))
        self.assertIsNone(result)

    def test_known_category_is_translated_to_thai(self):
        tc._db["quiz_attempts"] = _RecordingCollection(
            aggregate_result=[{"_id": "vikeplikt_regler", "fails": 2}]
        )
        tc._db["mistakes"] = _RecordingCollection()
        result = asyncio.run(tc._get_student_weakness(device_id="d1", lang="th"))
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "การให้ทางและกฎจากขวา")

    def test_unmapped_category_from_mistake_bank_returns_none(self):
        tc._db["quiz_attempts"] = _RecordingCollection(aggregate_result=[])
        tc._db["mistakes"] = _RecordingCollection(
            find_one_result={"category": "fart_og_bremsing", "active": True}
        )
        result = asyncio.run(tc._get_student_weakness(device_id="d1", lang="en"))
        self.assertIsNone(result)


class TeacherChatRequestLanguageValidationTests(unittest.TestCase):
    def test_optional_chat_fields_preserve_legacy_request(self):
        legacy = TeacherChatRequest(message="hei", language="no", session_id="old-session")
        self.assertIsNone(legacy.conversation_id)
        self.assertEqual(legacy.mode, "normal_chat")
        modern = TeacherChatRequest(
            message="hei", language="no", conversation_id="new-conversation", mode="simplify"
        )
        self.assertEqual(modern.conversation_id, "new-conversation")
        self.assertEqual(modern.mode, "simplify")

    def test_valid_languages_accepted(self):
        for lang in ("no", "th", "en"):
            req = TeacherChatRequest(message="hei", language=lang)
            self.assertEqual(req.language, lang)

    def test_invalid_language_is_rejected(self):
        with self.assertRaises(pydantic.ValidationError):
            TeacherChatRequest(message="hei", language="xx")

    def test_missing_language_is_rejected(self):
        with self.assertRaises(pydantic.ValidationError):
            TeacherChatRequest(message="hei")


class WelcomeAndTopicsRejectInvalidLanguageTests(unittest.TestCase):
    def setUp(self):
        self._orig_db = tc._db
        tc._db = _Database()
        tc._db["quiz_attempts"] = _RecordingCollection()
        tc._db["mistakes"] = _RecordingCollection()

    def tearDown(self):
        tc._db = self._orig_db

    def test_welcome_rejects_invalid_language(self):
        with self.assertRaises(tc.HTTPException):
            asyncio.run(tc.teacher_welcome(lang="xx"))

    def test_topics_rejects_invalid_language(self):
        with self.assertRaises(tc.HTTPException):
            asyncio.run(tc.teacher_topics(lang="xx"))

    def test_welcome_accepts_supported_language(self):
        result = asyncio.run(tc.teacher_welcome(lang="th"))
        self.assertEqual(result["lang"], "th")


class TheoryHelpShortcutLanguagePurityTests(unittest.TestCase):
    """The theory-help shortcut returns before the LLM call, so it's fully testable."""

    def setUp(self):
        self._orig_db = tc._db
        self._orig_chat_col = tc._chat_col
        tc._db = _Database()
        tc._chat_col = _RecordingCollection()

    def tearDown(self):
        tc._db = self._orig_db
        tc._chat_col = self._orig_chat_col

    def test_weak_topic_reply_is_thai_only_and_tags_stored_messages(self):
        tc._db["quiz_attempts"] = _RecordingCollection(
            aggregate_result=[{"_id": "vikeplikt_regler", "fails": 2}]
        )
        tc._db["mistakes"] = _RecordingCollection()
        req = TeacherChatRequest(message="help with the theory test", language="th", device_id="d1")
        response = asyncio.run(tc.teacher_chat(req))

        self.assertIn("การให้ทางและกฎจากขวา", response.reply)
        self.assertNotIn("vikeplikt", response.reply.lower())
        self.assertTrue(tc._chat_col.inserted)
        self.assertTrue(all(doc["language"] == "th" for doc in tc._chat_col.inserted))
        self.assertEqual(response.conversation_id, response.session_id)

    def test_conversation_id_reuses_session_storage_for_new_callers(self):
        req = TeacherChatRequest(
            message="help with the theory test", language="th",
            conversation_id="conversation-123", mode="quiz_coach",
        )
        response = asyncio.run(tc.teacher_chat(req))
        self.assertEqual(response.session_id, "conversation-123")
        self.assertEqual(response.conversation_id, "conversation-123")
        self.assertTrue(all(doc["session_id"] == "conversation-123" for doc in tc._chat_col.inserted))

    def test_unmapped_category_falls_back_to_generic_opener_not_raw_key(self):
        tc._db["quiz_attempts"] = _RecordingCollection(
            aggregate_result=[{"_id": "fart_og_bremsing", "fails": 3}]
        )
        tc._db["mistakes"] = _RecordingCollection()
        req = TeacherChatRequest(message="help with the theory test", language="th", device_id="d1")
        response = asyncio.run(tc.teacher_chat(req))

        self.assertNotIn("fart_og_bremsing", response.reply)
        self.assertNotIn("Fart Og Bremsing", response.reply)

    def test_english_shortcut_reply_has_no_norwegian_or_thai(self):
        tc._db["quiz_attempts"] = _RecordingCollection(aggregate_result=[])
        tc._db["mistakes"] = _RecordingCollection()
        req = TeacherChatRequest(message="what should i practice?", language="en", device_id="d1")
        response = asyncio.run(tc.teacher_chat(req))

        self.assertIn("What would you like us to practice today", response.reply)
        self.assertTrue(all(doc["language"] == "en" for doc in tc._chat_col.inserted))


class ChatHistoryFilteredByLanguageOnDisk(unittest.TestCase):
    """The prior-conversation fetch must scope by language, not just session_id,
    so a language switch never replays the old language's turns into the prompt."""

    def test_history_query_includes_language_filter_in_source(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn('{"session_id": session_id, "language": lang}', source)
        self.assertNotIn(
            'prior = await _chat_col.find(\n        {"session_id": session_id}\n    )',
            source,
        )


if __name__ == "__main__":
    unittest.main()
