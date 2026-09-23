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


class HintClickTests(unittest.TestCase):
    def test_hint_request_detection(self):
        for msg in ("Gi meg et hint", "Give me a hint", "ขอคำใบ้หน่อยครับ"):
            self.assertTrue(tc._is_hint_request(msg), msg)
        self.assertFalse(tc._is_hint_request("Kan du forklare dette spørsmålet for meg?"))

    def test_three_hint_clicks_give_hint_then_answer(self):
        key = tc._quiz_key("Q1 fart 50")
        prior = []
        steps = []
        for _ in range(3):
            attempt = tc._quiz_attempt_number(prior, key) + 1  # hint click bumps the ladder
            text = tc._scaffolding_instruction(attempt, False, "no")
            steps.append("STEP 3" if "STEP 3" in text else "STEP 2" if "STEP 2" in text else "STEP 1")
            prior.append({"role": "user", "quiz_key": key})
        self.assertEqual(steps, ["STEP 2", "STEP 3", "STEP 3"])

    def test_explain_message_jumps_to_answer(self):
        self.assertTrue(any(t in "Kan du forklare dette?".casefold() for t in tc._EXPLICIT_ANSWER_TERMS))
        self.assertFalse(any(t in "Gi meg et hint".casefold() for t in tc._EXPLICIT_ANSWER_TERMS))


# ── Deterministic end-to-end prompt checks (stub LLM, fake Mongo, no network) ──
import types
from unittest.mock import patch


class _Cursor:
    def __init__(self, items=None):
        self.items = items or []

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return list(self.items[:length]) if length else list(self.items)


class _Col:
    def __init__(self):
        self.inserted = []

    def aggregate(self, pipeline):
        return _Cursor()

    def find(self, *args, **kwargs):
        return _Cursor()

    async def find_one(self, *args, **kwargs):
        return None

    async def insert_one(self, doc):
        self.inserted.append(doc)

    async def insert_many(self, docs):
        self.inserted.extend(docs)


class _Db(dict):
    def __getitem__(self, key):
        return dict.get(self, key) or _Col()


def _run_chat(message, language, mode="normal_chat"):
    """Run teacher_chat with a stub LLM; return (response, system_prompt_sent, chat_col)."""
    captured = {}
    chat_col = _Col()

    async def fake_completion(messages, require_vision=False):
        captured["system"] = messages[0]["content"]
        reply = "โอเคครับ" if language == "th" else "Greit."
        return types.SimpleNamespace(
            choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=reply))]
        )

    request = tc.TeacherChatRequest(message=message, language=language, mode=mode)
    with patch.object(tc, "_db", _Db()), patch.object(tc, "_chat_col", chat_col), patch.object(
        tc, "LLM_KEY", "test"
    ), patch.object(tc, "_completion_with_fallback", new=fake_completion):
        response = asyncio.run(tc.teacher_chat(request))
    return response, captured.get("system", ""), chat_col


class DeterministicPromptTests(unittest.TestCase):
    QUIZ = "<quiz_context>Question: fart i tettbygd strøk? Student answer: 60 Correct answer: 50</quiz_context>"

    def test_thai_quiz_help_ends_with_purity_block(self):
        _, system, _ = _run_chat("ช่วยอธิบายว่าทำไมคำตอบนี้ผิด\n" + self.QUIZ, "th")
        self.assertIn("THAI PURITY FOR QUIZ EXPLANATIONS", system)
        self.assertLess(system.index("FINAL MASTER OUTPUT RULES"), system.index("THAI PURITY FOR QUIZ EXPLANATIONS"))

    def test_norwegian_quiz_help_has_no_thai_purity_block(self):
        _, system, _ = _run_chat("Kan du forklare dette?\n" + self.QUIZ, "no")
        self.assertNotIn("THAI PURITY FOR QUIZ EXPLANATIONS", system)

    def test_hint_request_starts_ladder_at_step_2_and_stores_quiz_key(self):
        _, system, col = _run_chat("Gi meg et hint\n" + self.QUIZ, "no")
        self.assertIn("SCAFFOLDING LADDER", system)
        self.assertIn("STEP 2", system)
        user_docs = [d for d in col.inserted if d.get("role") == "user"]
        self.assertTrue(user_docs and user_docs[0].get("quiz_key"))

    def test_explain_request_goes_straight_to_step_3(self):
        _, system, _ = _run_chat("Kan du forklare dette?\n" + self.QUIZ, "no")
        self.assertIn("STEP 3", system)

    def test_warm_tone_reaches_prompt(self):
        _, system, _ = _run_chat("Jeg gruer meg til oppkjøring", "no")
        self.assertIn("TONE REGISTER (WARM)", system)


class PolishReplyTests(unittest.TestCase):
    LEAKED = (
        "Det er helt normalt å føle seg slik.\n\n"
        "(podcast: /public_assets/podcast_ferske_sjaforer.m4a | A | B | C)\n\n"
        "Hør gjerne på denne podcasten.\n\n"
        "Hva er det første du vil øve på?"
    )

    def test_leaked_media_syntax_and_menu_question_removed(self):
        out = tc._polish_teacher_reply(self.LEAKED)
        self.assertNotIn("podcast", out.lower())
        self.assertNotIn("/public_assets/", out)
        self.assertNotIn("Hør gjerne", out)
        self.assertFalse(out.rstrip().endswith("?"))
        self.assertIn("helt normalt", out)

    def test_bold_markup_removed_and_bracket_tags_kept(self):
        out = tc._polish_teacher_reply("A **give way** sign.\n\n[image: https://x/y.jpg | A | B | C]")
        self.assertNotIn("**", out)
        self.assertIn("[image: https://x/y.jpg | A | B | C]", out)

    def test_single_paragraph_question_is_kept(self):
        self.assertEqual(tc._polish_teacher_reply("Hva mener du med det?"), "Hva mener du med det?")

    def test_empty_input_safe(self):
        self.assertEqual(tc._polish_teacher_reply(""), "")
