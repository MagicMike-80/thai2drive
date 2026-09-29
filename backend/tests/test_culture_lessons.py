"""
Offline unit tests for the "Thailand vs Norge" deck logic (culture_lessons.py).

Pure functions only — no network, no MongoDB, no server import.

    python -m unittest tests.test_culture_lessons          # from backend/
    python -m unittest backend.tests.test_culture_lessons   # from repo root
"""

import unittest

try:
    from culture_lessons import serialize_lesson, lessons_for_lang
except ImportError:  # running from repo root
    from backend.culture_lessons import serialize_lesson, lessons_for_lang


def _lesson(lesson_id, order=1, category="Vikeplikt", **overrides):
    base = {
        "id": lesson_id,
        "order": order,
        "category": category,
        "title_th": "TH-title " + lesson_id,
        "title_no": "NO-title " + lesson_id,
        "thailand_practice_th": "TH practice",
        "norway_rule_th": "TH rule",
        "norway_term_no": "NO term",
        "michaels_tip_th": "TH tip",
        "definition_en": "EN leak attempt",
        "extra_no": "NO leak attempt",
        "active": True,
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    base.update(overrides)
    return base


DECK = [
    _lesson("cl_c", order=3, category="Rundkjøring"),
    _lesson("cl_a", order=1, category="Vikeplikt"),
    _lesson("cl_b", order=2, category="Gangfelt"),
]


class Serialize(unittest.TestCase):
    def test_th_keeps_norwegian_term_and_title_but_no_leaks(self):
        row = serialize_lesson(_lesson("cl_x"), "th")
        self.assertEqual(row["title_no"], "NO-title cl_x")
        self.assertEqual(row["norway_term_no"], "NO term")
        self.assertNotIn("definition_en", row)
        self.assertNotIn("extra_no", row)
        self.assertNotIn("_id", row)
        self.assertNotIn("created_at", row)
        for key in row:
            self.assertFalse(key.endswith("_en"), "EN field leaked: " + key)

    def test_unsupported_lang_returns_none(self):
        self.assertIsNone(serialize_lesson(_lesson("cl_x"), "no"))
        self.assertIsNone(serialize_lesson(_lesson("cl_x"), "en"))


class FailStop(unittest.TestCase):
    def test_missing_required_thai_field_is_dropped(self):
        deck = [_lesson("cl_ok"), _lesson("cl_bad", norway_rule_th="")]
        rows = lessons_for_lang(deck, "th")
        self.assertEqual([r["id"] for r in rows], ["cl_ok"])


class Filtering(unittest.TestCase):
    def test_category_filter_is_case_insensitive(self):
        rows = lessons_for_lang(DECK, "th", category="rundkjøring")
        self.assertEqual([r["id"] for r in rows], ["cl_c"])

    def test_inactive_is_excluded(self):
        deck = DECK + [_lesson("cl_off", order=4, active=False)]
        rows = lessons_for_lang(deck, "th")
        self.assertNotIn("cl_off", [r["id"] for r in rows])

    def test_non_thai_lang_returns_empty(self):
        self.assertEqual(lessons_for_lang(DECK, "no"), [])


class Ordering(unittest.TestCase):
    def test_sorted_by_order(self):
        rows = lessons_for_lang(DECK, "th")
        self.assertEqual([r["id"] for r in rows], ["cl_a", "cl_b", "cl_c"])


if __name__ == "__main__":
    unittest.main()
