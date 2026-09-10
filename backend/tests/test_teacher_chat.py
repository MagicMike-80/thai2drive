import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import backend.teacher_chat as tc
from backend.teacher_chat import (
    _match_canonical_concept,
    resolve_traffic_concept,
    _get_suggestions,
    _apply_formula_fail_safe,
    teacher_chat,
    TeacherChatRequest,
)


class _Cursor:
    def __init__(self, items=None):
        self.items = items or []

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return list(self.items)


class _Collection:
    def find(self, *args, **kwargs):
        return _Cursor()

    async def find_one(self, *args, **kwargs):
        return None

    async def insert_one(self, *args, **kwargs):
        return None

    async def insert_many(self, *args, **kwargs):
        return None


class _Database:
    def __getitem__(self, name):
        return _Collection()

    def __getattr__(self, name):
        return _Collection()


class TestTeacherChatConsolidatedResolver(unittest.TestCase):
    """Offline unit tests for consolidated ConceptResolver with typo-tolerance."""

    def setUp(self):
        # Ensure offline mock for mongo
        self._orig_db = tc._db
        self._orig_chat_col = tc._chat_col
        tc._db = _Database()
        tc._chat_col = _Collection()

    def tearDown(self):
        tc._db = self._orig_db
        tc._chat_col = self._orig_chat_col

    def test_fuzzy_matching_typos_resolve_canonical(self):
        cases = [
            ("raksjonslengde", "reaksjonslengde"),
            ("raksjonslengder", "reaksjonslengde"),
            ("reaksjonslende", "reaksjonslengde"),
            ("bremselende", "bremselengde"),
            ("bremslengde", "bremselengde"),
            ("stoppelende", "stoppelengde"),
            ("stopplengde", "stoppelengde"),
            ("vikeplit", "vikeplikt"),
            ("hoyreregel", "vikeplikt"),
            ("rundkjoring", "rundkjøring"),
            ("havaregel", "hav_regelen"),
        ]
        for typo, expected_canonical in cases:
            with self.subTest(typo=typo):
                concept = _match_canonical_concept(typo)
                self.assertIsNotNone(concept, f"Failed to match typo: {typo}")
                self.assertEqual(concept["canonical"], expected_canonical)

    def test_sentence_with_typos_resolves_correct_concept(self):
        sentences = [
            ("Kan du forklare raksjonslengder for meg?", "reaksjonslengde"),
            ("Hva er formelen for bremselende?", "bremselengde"),
            ("Hva betyr vikeplit?", "vikeplikt"),
            ("Hvordan fungerer stoppelende i 80 km/t?", "stoppelengde"),
        ]
        for sentence, expected_canonical in sentences:
            with self.subTest(sentence=sentence):
                concept = _match_canonical_concept(sentence)
                self.assertIsNotNone(concept, f"Failed to match in sentence: {sentence}")
                self.assertEqual(concept["canonical"], expected_canonical)

    def test_resolve_traffic_concept_offline_formula_and_media(self):
        resolved = asyncio.run(resolve_traffic_concept("raksjonslengder", "no", db=None))
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["canonical"], "reaksjonslengde")
        self.assertEqual(resolved["category"], "stoppelengde")
        self.assertIn("(Fart ÷ 10) × 3", resolved["formula"])
        self.assertEqual(resolved["title"], "Reaksjonslengde")
        self.assertTrue(len(resolved["media"]) > 0)
        self.assertEqual(resolved["media"][0]["id"], "vid_stopp_01")
        self.assertEqual(resolved["chips"], ["🚗 Bremselengde", "📏 Stoppelengde", "❓ Spør videre"])

    def test_suggestions_on_typo_never_rolls_over_to_default_buttons(self):
        default_buttons = ["❓ Spør videre", "📖 Åpne studiebok", "📊 Min statistikk"]

        # User asked with typo; suggestions must return contextual speed chips
        chips_no = _get_suggestions(reply="Noe tekst", lang="no", user_msg="Hva er raksjonslengder?")
        self.assertNotEqual(chips_no, default_buttons)
        self.assertIn("🚗 Bremselengde", chips_no)
        self.assertIn("📏 Stoppelengde", chips_no)

        chips_vike = _get_suggestions(reply="Noe tekst", lang="no", user_msg="Hva er vikeplit?")
        self.assertNotEqual(chips_vike, default_buttons)
        self.assertIn("🚗 Høyreregelen", chips_vike)
        self.assertIn("🛑 Vikepliktskilt", chips_vike)

    def test_multilingual_support_thai_and_english(self):
        # Thai test
        resolved_th = asyncio.run(resolve_traffic_concept("ระยะตอบสนอง", "th", db=None))
        self.assertIsNotNone(resolved_th)
        self.assertEqual(resolved_th["canonical"], "reaksjonslengde")
        self.assertEqual(resolved_th["title"], "ระยะตอบสนอง")
        self.assertIn("ความเร็ว ÷ 10", resolved_th["formula"])
        self.assertIn("🚗 ระยะเบรก", resolved_th["chips"])

        # English test
        resolved_en = asyncio.run(resolve_traffic_concept("reaction distance", "en", db=None))
        self.assertIsNotNone(resolved_en)
        self.assertEqual(resolved_en["canonical"], "reaksjonslengde")
        self.assertEqual(resolved_en["title"], "Reaction distance")
        self.assertIn("Speed ÷ 10", resolved_en["formula"])
        self.assertIn("🚗 Braking distance", resolved_en["chips"])

    def test_formula_fail_safe_formats_calculation_on_typo(self):
        # Even if model call fails / returns fallback, formula fail-safe ensures correct math output
        fallback_msg = "Beklager, Michael er ikke tilgjengelig akkurat nå."
        formatted_no = _apply_formula_fail_safe("raksjonslengder", fallback_msg, "no")
        self.assertIn("Reaksjonslengde", formatted_no)
        self.assertIn("(Fart ÷ 10) × 3", formatted_no)
        self.assertIn("15 m", formatted_no)
        self.assertNotIn("Beklager", formatted_no)

        formatted_th = _apply_formula_fail_safe("ระยะตอบสนอง", "ขออภัยครับ", "th")
        self.assertIn("ระยะตอบสนอง", formatted_th)
        self.assertIn("ความเร็ว ÷ 10", formatted_th)
        self.assertNotIn("ขออภัย", formatted_th)

    def test_teacher_chat_with_typo_returns_formula_media_and_chips(self):
        req = TeacherChatRequest(
            session_id="test_session_typo_1",
            message="Hva er formelen for raksjonslengder?",
            language="no",
        )
        res = asyncio.run(teacher_chat(req))
        self.assertIsNotNone(res)
        # Verify media card
        self.assertTrue(len(res.media) > 0)
        self.assertEqual(res.media[0]["id"], "vid_stopp_01")
        # Verify suggestions
        self.assertIn("🚗 Bremselengde", res.suggestions)
        self.assertIn("📏 Stoppelengde", res.suggestions)
        # Verify formula in reply
        self.assertIn("(Fart ÷ 10) × 3", res.reply)


if __name__ == "__main__":
    unittest.main()
