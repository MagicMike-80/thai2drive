"""
Tests for Phase 5: «Thailand vs Norge» Micro-lessons & Driving Culture Pedagogy
--------------------------------------------------------------------------------
Verifies:
1. Micro-lessons data completeness and 5+ core topics.
2. 100% strict language isolation (TH / NO / EN).
3. Keyword matching & curriculum context formatting.
4. REST API endpoints (/api/micro-lessons, /api/micro-lessons/{id}, /api/lessons/culture).
5. Michael Chat integration (suggestions, media cards, validation, RAG context).
"""
import re
import sys
import pytest
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import server
from micro_lessons import (
    MICRO_LESSONS,
    get_localized_lessons,
    get_micro_lesson_by_id,
    find_relevant_micro_lesson,
    format_micro_lesson_context,
    get_micro_lesson_media_card,
)
import teacher_chat as tc


THAI_REGEX = re.compile(r"[\u0e00-\u0e7f]")


class TestMicroLessonsDataStructure(unittest.TestCase):
    """Verify that all required lessons and fields are present."""

    def test_has_at_least_5_core_lessons(self):
        self.assertGreaterEqual(len(MICRO_LESSONS), 5)

    def test_core_topics_covered(self):
        topics = {lesson["topic"] for lesson in MICRO_LESSONS}
        expected_topics = {
            "vikeplikt_hoyreregel",
            "fotgjengere_gangfelt",
            "rundkjoring",
            "promillegrense_alkohol",
            "lys_og_blinklys",
        }
        for expected in expected_topics:
            self.assertIn(expected, topics, f"Missing expected core topic: {expected}")

    def test_all_fields_populated_for_all_languages(self):
        required_lang_fields = [
            "title",
            "norway_rule",
            "thailand_habit",
            "content",
            "metafor",
        ]
        for lesson in MICRO_LESSONS:
            lesson_id = lesson.get("id")
            self.assertTrue(lesson_id, "Lesson must have an id")
            self.assertTrue(lesson.get("topic"), f"Lesson {lesson_id} must have a topic")
            self.assertTrue(lesson.get("law_ref"), f"Lesson {lesson_id} must have a law_ref")
            self.assertTrue(lesson.get("keywords"), f"Lesson {lesson_id} must have keywords")

            for field in required_lang_fields:
                for lang in ("no", "th", "en"):
                    key = f"{field}_{lang}"
                    val = lesson.get(key)
                    self.assertTrue(val, f"Lesson {lesson_id} missing {key}")
                    self.assertIsInstance(val, str, f"{key} must be a string")
                    self.assertGreater(len(val.strip()), 5, f"{key} in {lesson_id} is too short")


class TestMicroLessonsLanguageIsolation(unittest.TestCase):
    """Verify 100% language purity across all localized lessons."""

    def test_thai_localization_purity(self):
        lessons = get_localized_lessons(language="th")
        self.assertGreaterEqual(len(lessons), 5)
        for l in lessons:
            # Check title, norway_rule, thailand_habit, content, metafor
            for field in ("title", "norway_rule", "thailand_habit", "content", "metafor"):
                text = l.get(field, "")
                self.assertTrue(text, f"Thai lesson {l.get('id')} has empty field {field}")
                # Must contain Thai characters
                self.assertTrue(
                    bool(THAI_REGEX.search(text)),
                    f"Thai lesson {l.get('id')} field {field} does not contain Thai characters: {text}"
                )
                # Fail-Stop check: No untranslated Norwegian marker phrases
                for no_marker in ("i Norge", "I Norge", "I Thailand", "På glatt", "gangfelt", "stopplikt"):
                    self.assertNotIn(
                        f" {no_marker} ",
                        f" {text} ",
                        f"Language bleed-through: found Norwegian fragment '{no_marker}' in Thai {field}"
                    )

    def test_norwegian_localization_purity(self):
        lessons = get_localized_lessons(language="no")
        self.assertGreaterEqual(len(lessons), 5)
        for l in lessons:
            for field in ("title", "norway_rule", "thailand_habit", "content", "metafor"):
                text = l.get(field, "")
                self.assertTrue(text, f"Norwegian lesson {l.get('id')} has empty field {field}")
                # Zero Thai characters allowed in Norwegian interface
                self.assertFalse(
                    bool(THAI_REGEX.search(text)),
                    f"Language bleed-through: found Thai character in Norwegian {field}: {text}"
                )

    def test_english_localization_purity(self):
        lessons = get_localized_lessons(language="en")
        self.assertGreaterEqual(len(lessons), 5)
        for l in lessons:
            for field in ("title", "norway_rule", "thailand_habit", "content", "metafor"):
                text = l.get(field, "")
                self.assertTrue(text, f"English lesson {l.get('id')} has empty field {field}")
                # Zero Thai characters allowed in English interface
                self.assertFalse(
                    bool(THAI_REGEX.search(text)),
                    f"Language bleed-through: found Thai character in English {field}: {text}"
                )


class TestMicroLessonMatchingAndRAG(unittest.TestCase):
    """Verify intelligent matching of micro-lessons by keyword and RAG context formatting."""

    def test_find_relevant_micro_lesson_thai_queries(self):
        test_cases = [
            ("รถใหญ่คันไหนไปก่อน", "vikeplikt_hoyreregel"),
            ("ทางม้าลายต้องหยุดไหม", "fotgjengere_gangfelt"),
            ("ขับรถในวงเวียนยังไง", "rundkjoring"),
            ("เมาแล้วขับหรือดื่มเบียร์", "promillegrense_alkohol"),
            ("ต้องเปิดไฟหน้ารถตอนกลางวันไหม", "lys_og_blinklys"),
            ("ขับรถบนหิมะถนนลื่น", "vinterkjoring"),
        ]
        for query, expected_topic in test_cases:
            match = find_relevant_micro_lesson(query, language="th")
            self.assertIsNotNone(match, f"Failed to match query: '{query}'")
            self.assertEqual(match["topic"], expected_topic, f"Query '{query}' matched wrong topic")

    def test_find_relevant_micro_lesson_norwegian_queries(self):
        test_cases = [
            ("hva sier høyreregelen", "vikeplikt_hoyreregel"),
            ("må jeg stoppe foran gangfelt", "fotgjengere_gangfelt"),
            ("hvem har vikeplikt i en rundkjøring", "rundkjoring"),
            ("hva er promillegrensen i norge", "promillegrense_alkohol"),
            ("hvorfor må jeg ha kjørelys på dagen", "lys_og_blinklys"),
            ("hva bør jeg tenke på ved vinterkjøring og glatt føre", "vinterkjoring"),
        ]
        for query, expected_topic in test_cases:
            match = find_relevant_micro_lesson(query, language="no")
            self.assertIsNotNone(match, f"Failed to match query: '{query}'")
            self.assertEqual(match["topic"], expected_topic, f"Query '{query}' matched wrong topic")

    def test_format_micro_lesson_context_language_isolation(self):
        lesson = get_micro_lesson_by_id("lesson_1_priority", "th")
        ctx_th = format_micro_lesson_context(lesson, "th")
        self.assertTrue(bool(THAI_REGEX.search(ctx_th)))
        self.assertIn("บทเรียนพิเศษ", ctx_th)
        self.assertIn("กฎหมายนอร์เวย์", ctx_th)

        lesson_no = get_micro_lesson_by_id("lesson_1_priority", "no")
        ctx_no = format_micro_lesson_context(lesson_no, "no")
        self.assertFalse(bool(THAI_REGEX.search(ctx_no)))
        self.assertIn("SPESIALLEKSJON", ctx_no)
        self.assertIn("Lovhjemmel", ctx_no)

        lesson_en = get_micro_lesson_by_id("lesson_1_priority", "en")
        ctx_en = format_micro_lesson_context(lesson_en, "en")
        self.assertFalse(bool(THAI_REGEX.search(ctx_en)))
        self.assertIn("SPECIAL MICRO-LESSON", ctx_en)
        self.assertIn("Norwegian Law", ctx_en)


class TestMicroLessonEndpoints(unittest.TestCase):
    """Verify REST API routes in server.py."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(server.app)

    def test_get_micro_lessons_thai(self):
        resp = self.client.get("/api/micro-lessons?language=th")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("language"), "th")
        self.assertGreaterEqual(data.get("count", 0), 5)
        # Check first lesson has Thai title
        first = data["lessons"][0]
        self.assertTrue(bool(THAI_REGEX.search(first["title"])))

    def test_get_micro_lessons_norwegian(self):
        resp = self.client.get("/api/micro-lessons?language=no")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("language"), "no")
        first = data["lessons"][0]
        self.assertFalse(bool(THAI_REGEX.search(first["title"])))

    def test_get_micro_lessons_filter_topic(self):
        resp = self.client.get("/api/micro-lessons?language=th&topic=vikeplikt_hoyreregel")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("count"), 1)
        self.assertEqual(data["lessons"][0]["topic"], "vikeplikt_hoyreregel")

    def test_get_micro_lesson_detail(self):
        resp = self.client.get("/api/micro-lessons/lesson_2_pedestrians?language=th")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["lesson"]["id"], "lesson_2_pedestrians")
        self.assertTrue(bool(THAI_REGEX.search(data["lesson"]["title"])))

    def test_get_micro_lesson_detail_not_found(self):
        resp = self.client.get("/api/micro-lessons/non_existent_lesson")
        self.assertEqual(resp.status_code, 404)
        data = resp.json()
        self.assertFalse(data.get("success"))

    def test_legacy_culture_lessons_endpoint(self):
        resp = self.client.get("/api/lessons/culture")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertGreaterEqual(data.get("count", 0), 5)


class TestTeacherChatIntegration(unittest.TestCase):
    """Verify integration of micro-lessons with Michael Chat."""

    def test_safe_media_url_accepts_micro_lessons(self):
        self.assertTrue(tc._safe_teacher_response_media_url("/api/micro-lessons/lesson_1_priority"))
        self.assertTrue(tc._safe_teacher_response_media_url("/api/micro-lessons/lesson_2_pedestrians"))
        self.assertFalse(tc._safe_teacher_response_media_url("/api/micro-lessons/../../evil"))

    def test_validate_micro_lesson_media_card(self):
        import asyncio
        card = {
            "id": "micro-lesson:lesson_1_priority",
            "type": "micro_lesson",
            "title": "dummy",
            "caption": "dummy",
            "url": "/api/micro-lessons/lesson_1_priority",
        }
        # Validate in Thai
        validated_th = asyncio.run(tc._validate_teacher_response_media([card], "th"))
        self.assertEqual(len(validated_th), 1)
        self.assertTrue(bool(THAI_REGEX.search(validated_th[0]["title"])))
        self.assertEqual(validated_th[0]["type"], "micro_lesson")

        # Validate in Norwegian
        validated_no = asyncio.run(tc._validate_teacher_response_media([card], "no"))
        self.assertEqual(len(validated_no), 1)
        self.assertFalse(bool(THAI_REGEX.search(validated_no[0]["title"])))

    def test_suggestions_returns_culture_chips_with_language_isolation(self):
        # Thai test
        chips_th = tc._get_suggestions("คำอธิบาย", "th", user_msg="รถใหญ่ในไทยไปก่อน แล้วนอร์เวย์ล่ะ")
        self.assertIn("🇹🇭 vs 🇳🇴 กฎให้ทาง", chips_th)
        for chip in chips_th:
            self.assertTrue(
                bool(THAI_REGEX.search(chip)) or "🇹🇭" in chip or "🇳🇴" in chip,
                f"Chip '{chip}' should be in Thai"
            )

        # Norwegian test
        chips_no = tc._get_suggestions("forklaring", "no", user_msg="Høyreregelen i Norge")
        self.assertIn("🇹🇭 vs 🇳🇴 Vikeplikt", chips_no)
        for chip in chips_no:
            self.assertFalse(
                bool(THAI_REGEX.search(chip)),
                f"Bleed-through: found Thai characters in Norwegian chip: '{chip}'"
            )

        # English test
        chips_en = tc._get_suggestions("explanation", "en", user_msg="Right of way rule in Norway")
        self.assertIn("🇹🇭 vs 🇳🇴 Right-of-Way", chips_en)
        for chip in chips_en:
            self.assertFalse(
                bool(THAI_REGEX.search(chip)),
                f"Bleed-through: found Thai characters in English chip: '{chip}'"
            )

    def test_curriculum_context_injects_micro_lesson(self):
        import asyncio
        from unittest.mock import MagicMock
        with patch.object(tc, "_db") as mock_db:
            mock_col = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_col.find.return_value = mock_cursor
            mock_col.find_one = AsyncMock(return_value=None)
            mock_db.traffic_signs = mock_col
            mock_db.studiebok_chapters = mock_col
            mock_db.learning_videos = mock_col

            ctx_th = asyncio.run(tc._get_curriculum_context("ทางม้าลายในนอร์เวย์หยุดไหม", "th"))
            self.assertIn("บทเรียนพิเศษ", ctx_th)
            self.assertIn("ทางม้าลาย", ctx_th)


if __name__ == "__main__":
    unittest.main()
