"""
TASK-017 — Student learning memory & motivational coaching for Michael.
-------------------------------------------------------------------------
Unit tests for:
  - fetch_student_learning_memory(): defensive, fail-safe aggregation of a
    student's weak topic, streak, and accuracy from MongoDB.
  - _build_system_prompt(lang, memory=...): additive memory block injected
    into Michael's system prompt.
  - teacher_welcome(): streak-aware motivational greeting, still 100%
    language-isolated (NO / TH / EN), never mixing languages.

Runs fully offline against fake Mongo collections — never touches the
production BASE_URL the rest of this repo's pytest suites hit (see CLAUDE.md).
"""
import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import backend.teacher_chat as tc


class _Cursor:
    def __init__(self, items=None):
        self.items = items or []

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return list(self.items[:length]) if length else list(self.items)


class _RecordingCollection:
    """Fake Mongo collection that returns canned results for aggregate/find/find_one."""

    def __init__(self, aggregate_result=None, find_one_result=None, find_result=None):
        self.aggregate_result = aggregate_result or []
        self.find_one_result = find_one_result
        self.find_result = find_result or []
        self.find_calls = []

    def aggregate(self, pipeline):
        return _Cursor(self.aggregate_result)

    def find(self, filter_=None, *args, **kwargs):
        self.find_calls.append(filter_)
        return _Cursor(self.find_result)

    async def find_one(self, *args, **kwargs):
        return self.find_one_result


class _ExplodingCollection:
    """Fake Mongo collection whose every method raises — simulates a DB outage."""

    def aggregate(self, pipeline):
        raise ConnectionError("simulated Mongo outage")

    async def find_one(self, *args, **kwargs):
        raise ConnectionError("simulated Mongo outage")

    def find(self, *args, **kwargs):
        raise ConnectionError("simulated Mongo outage")


class _Database(dict):
    def __getitem__(self, key):
        return dict.get(self, key) or _RecordingCollection()


class FetchStudentLearningMemoryTests(unittest.TestCase):
    def setUp(self):
        self._orig_db = tc._db
        tc._db = _Database()

    def tearDown(self):
        tc._db = self._orig_db

    def test_returns_none_without_any_identifier(self):
        result = asyncio.run(tc.fetch_student_learning_memory(device_id=None, user_id=None, lang="no"))
        self.assertIsNone(result)

    def test_aggregates_streak_weak_topic_and_accuracy_when_data_exists(self):
        tc._db["quiz_attempts"] = _RecordingCollection(
            aggregate_result=[{"_id": "vikeplikt_regler", "fails": 2, "total": 20, "correct": 15}]
        )
        tc._db["mistakes"] = _RecordingCollection()
        tc._db["users"] = _RecordingCollection(find_one_result={"id": "u1", "current_streak": 4, "best_streak": 9})

        memory = asyncio.run(tc.fetch_student_learning_memory(device_id=None, user_id="u1", lang="no"))

        self.assertIsNotNone(memory)
        self.assertEqual(memory["current_streak"], 4)
        self.assertEqual(memory["best_streak"], 9)
        self.assertEqual(memory["weak_topic"]["name"], "vikeplikt og høyreregelen")
        self.assertEqual(memory["total_attempts"], 20)
        self.assertEqual(memory["accuracy_pct"], 75)

    def test_is_returning_true_when_prior_attempts_exist(self):
        tc._db["quiz_attempts"] = _RecordingCollection(
            aggregate_result=[{"total": 5, "correct": 3}]
        )
        tc._db["mistakes"] = _RecordingCollection()
        tc._db["users"] = _RecordingCollection(find_one_result=None)

        memory = asyncio.run(tc.fetch_student_learning_memory(device_id="d1", user_id=None, lang="no"))

        self.assertTrue(memory["is_returning"])

    def test_is_returning_false_for_brand_new_student_with_no_attempts(self):
        tc._db["quiz_attempts"] = _RecordingCollection(aggregate_result=[])
        tc._db["mistakes"] = _RecordingCollection()
        tc._db["users"] = _RecordingCollection(find_one_result=None)

        memory = asyncio.run(tc.fetch_student_learning_memory(device_id="new-device", user_id=None, lang="no"))

        self.assertFalse(memory["is_returning"])
        self.assertEqual(memory["current_streak"], 0)
        self.assertIsNone(memory["accuracy_pct"])

    def test_db_errors_are_swallowed_and_safe_default_is_returned(self):
        tc._db["quiz_attempts"] = _ExplodingCollection()
        tc._db["mistakes"] = _ExplodingCollection()
        tc._db["users"] = _ExplodingCollection()

        memory = asyncio.run(tc.fetch_student_learning_memory(device_id="d1", user_id=None, lang="no"))

        self.assertIsNotNone(memory)
        self.assertEqual(memory["current_streak"], 0)
        self.assertEqual(memory["best_streak"], 0)
        self.assertIsNone(memory["weak_topic"])
        self.assertFalse(memory["is_returning"])


class SystemPromptMemoryInjectionTests(unittest.TestCase):
    def test_no_memory_block_when_memory_is_none(self):
        prompt = tc._build_system_prompt("no", memory=None)
        self.assertNotIn("STUDENT LEARNING MEMORY", prompt)

    def test_no_memory_block_when_memory_has_no_signal(self):
        empty_memory = {"weak_topic": None, "current_streak": 0, "best_streak": 0, "is_returning": False}
        prompt = tc._build_system_prompt("no", memory=empty_memory)
        self.assertNotIn("STUDENT LEARNING MEMORY", prompt)

    def test_memory_block_appended_with_streak_content_without_removing_existing_sections(self):
        memory = {"weak_topic": None, "current_streak": 5, "best_streak": 9, "is_returning": True}
        prompt = tc._build_system_prompt("no", memory=memory)

        self.assertIn("STUDENT LEARNING MEMORY", prompt)
        self.assertIn("5", prompt)
        # Existing sections must still be intact — memory injection is additive only.
        self.assertIn("SYSTEMINSTRUKSJONER FOR BRUK AV DATABASEN", prompt)
        self.assertIn("CONVERSATION STYLE", prompt)


class WelcomeGreetingLanguageIsolationTests(unittest.TestCase):
    def setUp(self):
        self._orig_db = tc._db
        tc._db = _Database()

    def tearDown(self):
        tc._db = self._orig_db

    def _set_streak_fixture(self, streak=3):
        tc._db["quiz_attempts"] = _RecordingCollection(
            aggregate_result=[{"total": 10, "correct": 8}]
        )
        tc._db["mistakes"] = _RecordingCollection()
        tc._db["users"] = _RecordingCollection(find_one_result={"id": "u1", "current_streak": streak, "best_streak": streak})

    def test_streak_greeting_is_norwegian_only(self):
        self._set_streak_fixture(streak=3)
        result = asyncio.run(tc.teacher_welcome(lang="no", user_id="u1"))

        self.assertIn("3", result["welcome"])
        self.assertNotIn("streak", result["welcome"].lower())
        self.assertFalse(any(ord(ch) > 0x0E00 and ord(ch) < 0x0E7F for ch in result["welcome"]))

    def test_streak_greeting_is_thai_only(self):
        self._set_streak_fixture(streak=3)
        result = asyncio.run(tc.teacher_welcome(lang="th", user_id="u1"))

        self.assertIn("3", result["welcome"])
        self.assertTrue(any(0x0E00 <= ord(ch) <= 0x0E7F for ch in result["welcome"]))
        self.assertNotIn("riktige", result["welcome"].lower())

    def test_streak_greeting_is_english_only(self):
        self._set_streak_fixture(streak=3)
        result = asyncio.run(tc.teacher_welcome(lang="en", user_id="u1"))

        self.assertIn("3", result["welcome"])
        self.assertIn("streak", result["welcome"].lower())
        self.assertFalse(any(0x0E00 <= ord(ch) <= 0x0E7F for ch in result["welcome"]))
        self.assertNotIn("riktige", result["welcome"].lower())

    def test_first_time_student_gets_open_greeting_unchanged(self):
        tc._db["quiz_attempts"] = _RecordingCollection(aggregate_result=[])
        tc._db["mistakes"] = _RecordingCollection()
        tc._db["users"] = _RecordingCollection(find_one_result=None)

        result = asyncio.run(tc.teacher_welcome(lang="no", device_id="brand-new-device"))

        self.assertIn("Hva vil du at vi skal øve på i dag", result["welcome"])
        self.assertIsNone(result["weakness"])


if __name__ == "__main__":
    unittest.main()
