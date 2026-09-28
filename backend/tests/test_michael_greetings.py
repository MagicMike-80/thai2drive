"""Michael's opening messages: variety, language isolation, AI disclosure, safe names.

Offline: pure functions plus a stubbed memory lookup. Never touches production or the DB.
"""
import asyncio
import re
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import backend.michael_greetings as g
import backend.teacher_chat as tc

THAI = re.compile(r"[฀-๿]")
LATIN = re.compile(r"[A-Za-zÆØÅæøå]")
EMOJI = re.compile("[\U0001F000-\U0001FFFF☀-➿️]")
GROUPS = {"new", "morning", "day", "evening", "comeback", "streak", "streak_topic", "weak_topic"}


class GreetingDataTests(unittest.TestCase):
    def test_every_language_has_every_group_with_variety(self):
        for lang in ("no", "th", "en"):
            self.assertEqual(set(g.GREETINGS[lang]), GROUPS, lang)
            for group, templates in g.GREETINGS[lang].items():
                self.assertGreaterEqual(len(templates), 2, f"{lang}/{group}")
                self.assertEqual(len(templates), len(set(templates)), f"{lang}/{group} duplicates")

    def test_no_emojis_anywhere(self):
        for lang, groups in g.GREETINGS.items():
            for group, templates in groups.items():
                for text in templates:
                    self.assertFalse(EMOJI.search(text), f"{lang}/{group}: {text}")

    def test_language_isolation(self):
        for group, templates in g.GREETINGS["no"].items():
            for text in templates:
                self.assertFalse(THAI.search(text), text)
        for group, templates in g.GREETINGS["en"].items():
            for text in templates:
                self.assertFalse(THAI.search(text), text)
        placeholders = re.compile(r"\{(?:navn|streak|topic)\}")
        for group, templates in g.GREETINGS["th"].items():
            for text in templates:
                self.assertFalse(LATIN.search(placeholders.sub("", text)), text)

    def test_new_student_greeting_discloses_ai_in_every_language(self):
        for text in g.GREETINGS["no"]["new"] + g.GREETINGS["en"]["new"]:
            self.assertIn("AI", text)
        for text in g.GREETINGS["th"]["new"]:
            self.assertIn("ปัญญาประดิษฐ์", text)
        for text in g.GREETINGS["no"]["new"]:
            self.assertIn("Hva vil du at vi skal øve på i dag", text)


def rendered(lang, group):
    """All variants of a group with placeholders filled the way pick_welcome does for a nameless student."""
    return {t.format(navn="", streak=0, topic="") for t in g.GREETINGS[lang][group]}


class PickWelcomeTests(unittest.TestCase):
    def test_priority_streak_then_topic_then_comeback_then_time_then_new(self):
        self.assertIn("5", g.pick_welcome("no", streak=5, topic="skilt", is_returning=True, seed="x"))
        self.assertIn("skilt", g.pick_welcome("no", streak=0, topic="skilt", is_returning=True, seed="x"))
        comeback = g.pick_welcome("no", is_returning=True, days_since_last=20, seed="x")
        self.assertIn(comeback, rendered("no", "comeback"))
        morning = g.pick_welcome("no", is_returning=True, days_since_last=1, hour=8, seed="x")
        self.assertIn(morning, rendered("no", "morning"))
        evening = g.pick_welcome("no", is_returning=True, days_since_last=1, hour=21, seed="x")
        self.assertIn(evening, rendered("no", "evening"))
        self.assertIn(g.pick_welcome("no", seed="x"), rendered("no", "new"))

    def test_stable_per_seed_and_varies_across_days(self):
        first = g.pick_welcome("en", is_returning=True, hour=8, seed="2026-09-23:u1")
        again = g.pick_welcome("en", is_returning=True, hour=8, seed="2026-09-23:u1")
        self.assertEqual(first, again)
        seen = {g.pick_welcome("en", is_returning=True, hour=8, seed=f"2026-09-{d:02d}:u1") for d in range(1, 29)}
        self.assertGreater(len(seen), 1)

    def test_name_suffix_per_language(self):
        self.assertIn(", Nok", g.pick_welcome("no", first_name="Nok", is_returning=True, hour=8, seed="a"))
        self.assertIn(", Nok", g.pick_welcome("en", first_name="Nok", is_returning=True, hour=8, seed="a"))
        self.assertIn("คุณNok", g.pick_welcome("th", first_name="Nok", is_returning=True, hour=8, seed="a"))
        self.assertNotIn("None", g.pick_welcome("no", is_returning=True, hour=8, seed="a"))

    def test_existing_streak_expectations_still_hold(self):
        self.assertIn("streak", g.pick_welcome("en", streak=3, seed="a").lower())
        self.assertNotIn("streak", g.pick_welcome("no", streak=3, seed="a").lower())
        self.assertNotIn("riktige", g.pick_welcome("en", streak=3, seed="a").lower())

    def test_unsupported_language_rejected(self):
        with self.assertRaises(ValueError):
            g.pick_welcome("xx")


class HelperTests(unittest.TestCase):
    def test_safe_first_name(self):
        self.assertEqual(g.safe_first_name({"full_name": "Nok Sudsai"}), "Nok")
        self.assertEqual(g.safe_first_name({"name": "สมชาย ใจดี"}), "สมชาย")
        self.assertIsNone(g.safe_first_name({"name": "nok@example.com"}))
        self.assertIsNone(g.safe_first_name({"name": "<script>alert(1)</script>"}))
        self.assertIsNone(g.safe_first_name({"name": "   "}))
        self.assertIsNone(g.safe_first_name(None))
        self.assertIsNone(g.safe_first_name({"name": "A" * 40}))

    def test_days_since_and_oslo_hour(self):
        now = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)
        self.assertEqual(g.days_since(now - timedelta(days=9, hours=1), now), 9)
        self.assertEqual(g.days_since(now.replace(tzinfo=None) - timedelta(days=2), now), 2)
        self.assertIsNone(g.days_since(None, now))
        self.assertEqual(g.oslo_now(now).hour, 14)  # CEST in September


class WelcomeEndpointTests(unittest.TestCase):
    def _welcome(self, memory, lang="no", **kwargs):
        async def fake_memory(device_id, user_id, language):
            return memory

        with patch.object(tc, "fetch_student_learning_memory", new=fake_memory):
            return asyncio.run(tc.teacher_welcome(lang=lang, device_id=kwargs.get("device_id"), user_id=kwargs.get("user_id")))

    def test_brand_new_visitor_gets_ai_disclosure(self):
        result = self._welcome(None, device_id="new-device")
        self.assertIn("AI", result["welcome"])
        self.assertIn("Hva vil du at vi skal øve på i dag", result["welcome"])
        self.assertIsNone(result["weakness"])

    def test_returning_student_with_name_gets_personal_time_based_greeting(self):
        memory = {
            "is_returning": True, "current_streak": 0, "weak_topic": None,
            "last_session_at": datetime.now(timezone.utc) - timedelta(days=30), "first_name": "Nok",
        }
        result = self._welcome(memory, user_id="u1")
        self.assertIn("Nok", result["welcome"])
        self.assertIn(result["welcome"].replace(", Nok", ""), rendered("no", "comeback"))

    def test_streak_result_keeps_streak_key(self):
        memory = {"is_returning": True, "current_streak": 4, "weak_topic": None, "last_session_at": None}
        result = self._welcome(memory, lang="en", user_id="u1")
        self.assertEqual(result["streak"], 4)
        self.assertIn("streak", result["welcome"].lower())

    def test_thai_welcome_has_no_latin_letters_without_name(self):
        memory = {"is_returning": True, "current_streak": 0, "weak_topic": {"name": "การให้ทาง"}, "last_session_at": None}
        result = self._welcome(memory, lang="th", user_id="u1")
        self.assertTrue(THAI.search(result["welcome"]))
        self.assertFalse(LATIN.search(result["welcome"]))


class AiHonestyAndBadgeTests(unittest.TestCase):
    def test_prompt_forbids_claiming_to_be_human(self):
        for lang in ("no", "th", "en"):
            self.assertIn("AI HONESTY", tc._build_system_prompt(lang))

    def test_static_welcome_texts_disclose_ai(self):
        self.assertIn("AI", tc.MICHAEL_WELCOME["no"])
        self.assertIn("AI", tc.MICHAEL_WELCOME["en"])
        self.assertIn("ปัญญาประดิษฐ์", tc.MICHAEL_WELCOME["th"])

    def test_header_badge_wired_in_webapp(self):
        import backend.webapp as webapp
        html = webapp.WEBAPP_HTML
        self.assertIn('id="teacherAiBadge"', html)
        self.assertIn("aiBadge: 'เอไอ'", html)
        self.assertIn("b.setAttribute('aria-label', L.aiTitle)", html)


if __name__ == "__main__":
    unittest.main()
