"""
Michael conversation-first behaviour: token budget, prompt rules, history window
and active-sign context. Runs fully offline (fake Mongo, no LLM, no BASE_URL).
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


class _SignCol:
    def __init__(self, docs):
        self.docs = docs

    async def find_one(self, query):
        return self.docs.get(query.get("id"))


class _FakeDb:
    def __init__(self, signs):
        self.cols = {"traffic_signs": _SignCol(signs)}

    def __getitem__(self, name):
        return self.cols[name]


_SIGN = {
    "id": "376_2",
    "name": {"no": "Forbudt å parkere med tilhenger", "th": "ก", "en": "No parking trailers"},
    "explanation": {"no": "Tilhengere må ikke parkeres her.", "th": "ก", "en": "No trailers."},
    "driver_action": {"no": "Ikke parker tilhenger.", "th": "ก", "en": "Do not park."},
}


class TokenBudgetTests(unittest.TestCase):
    def test_normal_replies_have_room_to_finish_sentences(self):
        self.assertGreaterEqual(tc._TEACHER_CHAT_MAX_TOKENS, 400)
        self.assertEqual(tc._TEACHER_HISTORY_LIMIT, 10)


class PromptRuleTests(unittest.TestCase):
    def test_conversation_first_rules_in_every_language(self):
        for lang in ("no", "th", "en"):
            prompt = tc._build_system_prompt(lang)
            self.assertIn("CONVERSATION-FIRST RULES", prompt)
            self.assertIn("NEVER invent or guess sign numbers", prompt)
            self.assertIn("ACTIVE SIGN CONTEXT", prompt)

    def test_no_forced_five_step_flow_left_in_base_prompt(self):
        prompt = tc._build_system_prompt("no")
        self.assertNotIn("Kongen og tjeneren', etc.", prompt)
        self.assertNotIn("structured 5-step driving instructor flow", prompt)
        self.assertNotIn("End with a single follow-up check question (Mini-practice)", prompt)


class ActiveSignTests(unittest.TestCase):
    def test_explicit_sign_wins(self):
        prior = [{"role": "assistant", "sign_ids": ["376_2"]}]
        self.assertEqual(tc._active_sign_ids_from_history(prior, ["204_0"]), ["204_0"])

    def test_falls_back_to_latest_turn_with_signs(self):
        prior = [
            {"role": "assistant", "sign_ids": ["202_0"]},
            {"role": "user"},
            {"role": "assistant", "sign_ids": ["376_2"]},
            {"role": "user"},
        ]
        self.assertEqual(tc._active_sign_ids_from_history(prior, []), ["376_2"])

    def test_no_signs_anywhere(self):
        self.assertEqual(tc._active_sign_ids_from_history([{"role": "user"}], []), [])

    def test_active_sign_context_uses_only_db_facts(self):
        original = tc._db
        tc._db = _FakeDb({"376_2": _SIGN})
        try:
            block = asyncio.run(tc._active_sign_context(["376_2", "missing"], "no"))
            empty = asyncio.run(tc._active_sign_context(["missing"], "no"))
        finally:
            tc._db = original
        self.assertIn("ACTIVE SIGN CONTEXT", block)
        self.assertIn("Traffic Sign 376_2", block)
        self.assertIn("Forbudt å parkere med tilhenger", block)
        self.assertEqual(empty, "")


class ThaiQuizPurityTests(unittest.TestCase):
    def test_purity_block_bans_latin_and_overrides_parentheses_rule(self):
        block = tc._thai_quiz_purity_block()
        self.assertIn("Thai script only", block)
        self.assertIn("even in parentheses", block)
        self.assertIn("OVERRIDES", block)


if __name__ == "__main__":
    unittest.main()


class ToneRegisterTests(unittest.TestCase):
    def test_detects_each_register(self):
        self.assertEqual(tc._detect_tone("Jeg gruer meg til oppkjøring, bommer på alt"), "warm")
        self.assertEqual(tc._detect_tone("Kan jeg kjøre 50 i 30 sone?"), "strict")
        self.assertEqual(tc._detect_tone("haha hjernen min består bare av skilter nå"), "dry")
        self.assertEqual(tc._detect_tone("ฉันกังวลเรื่องสอบมาก"), "warm")
        self.assertIsNone(tc._detect_tone("Hva er vikeplikt?"))

    def test_safety_beats_warmth_and_humour(self):
        self.assertEqual(tc._detect_tone("haha jeg kan drikke og kjøre, gruer meg"), "strict")

    def test_instruction_only_when_tone_found(self):
        self.assertEqual(tc._tone_instruction(None, "no"), "")
        self.assertIn("WARM", tc._tone_instruction("warm", "en"))
        self.assertIn("STRICT", tc._tone_instruction("strict", "th"))


class ScaffoldingLadderTests(unittest.TestCase):
    def test_attempt_count_uses_same_question_only(self):
        key = tc._quiz_key("Q1 fart 50")
        other = tc._quiz_key("Q2 promille")
        prior = [
            {"role": "user", "quiz_key": key},
            {"role": "assistant"},
            {"role": "user", "quiz_key": other},
        ]
        self.assertEqual(tc._quiz_attempt_number(prior, key), 2)
        self.assertEqual(tc._quiz_attempt_number([], key), 1)

    def test_ladder_steps(self):
        one = tc._scaffolding_instruction(1, False, "no")
        two = tc._scaffolding_instruction(2, False, "no")
        three = tc._scaffolding_instruction(3, False, "no")
        asked = tc._scaffolding_instruction(1, True, "no")
        self.assertIn("STEP 1", one)
        self.assertIn("Do NOT reveal", one)
        self.assertIn("STEP 2", two)
        self.assertIn("ONE sharp hint", two)
        self.assertIn("STEP 3", three)
        self.assertIn("STEP 3", asked)
