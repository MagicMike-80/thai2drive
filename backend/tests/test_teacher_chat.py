import asyncio
import os
import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
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
    def __init__(self, items=None):
        self.items = items or []

    def find(self, *args, **kwargs):
        return _Cursor()

    async def find_one(self, *args, **kwargs):
        query = args[0] if args else {}
        for item in self.items:
            if all(item.get(key) == value for key, value in query.items()):
                return item
        return None

    async def insert_one(self, *args, **kwargs):
        return None

    async def insert_many(self, *args, **kwargs):
        return None


class _Database:
    def __init__(self, collections=None):
        self.collections = collections or {}

    def __getitem__(self, name):
        return self.collections.get(name, _Collection())

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

    def test_missing_thai_formula_never_uses_norwegian_fields(self):
        concept = {
            "formula": {"no": "Norsk formel"},
            "title": {"no": "Norsk tittel"},
            "definition": {"no": "Norsk forklaring"},
        }
        with patch.object(tc, "_match_canonical_concept", return_value=concept):
            reply = _apply_formula_fail_safe("formula", "ขออภัยครับ", "th")
        self.assertNotIn("Norsk", reply)
        self.assertEqual(reply, tc._fallback_reply("th"))

    def test_missing_thai_chips_never_uses_norwegian_chips(self):
        with patch.object(tc, "_match_canonical_concept", return_value={"chips": {"no": ["🚗 Norsk chip"]}}):
            chips = _get_suggestions("", "th", "formula")
        self.assertNotIn("🚗 Norsk chip", chips)
        self.assertEqual(chips, ["❓ ถามต่อ", "📖 เปิดหนังสือเรียน", "📊 สถิติของฉัน"])

    def test_teacher_chat_with_typo_returns_formula_media_and_chips(self):
        req = TeacherChatRequest(
            session_id="test_session_typo_1",
            message="Hva er formelen for raksjonslengder?",
            language="no",
        )
        res = asyncio.run(teacher_chat(req))
        self.assertIsNotNone(res)
        self.assertEqual(res.conversation_id, req.session_id)
        # The offline placeholder has no catalog record or asset and must be hidden.
        self.assertEqual(res.media, [])
        # Verify suggestions
        self.assertIn("🚗 Bremselengde", res.suggestions)
        self.assertIn("📏 Stoppelengde", res.suggestions)
        # Verify formula in reply
        self.assertIn("(fart ÷ 10) × 3", res.reply.lower())


class TestWrongQuizAnswerReplyIsThaiOnly(unittest.TestCase):
    """Simulates a student answering a quiz question wrong in Thai mode and
    prints Michael's full reply so it can be eyeballed for language purity.

    This calls the real /api/teacher/chat endpoint (real LLM call via
    litellm) — it is NOT mocked, since the whole point is to see what the
    model actually says. It requires a working DEEPSEEK_API_KEY /
    OPENROUTER_API_KEY / OPENAI_API_KEY in the environment; without one,
    teacher_chat() falls back to its canned "Michael is unavailable"
    message instead of a real explanation (see assertion below)."""

    def setUp(self):
        self._orig_db = tc._db
        self._orig_chat_col = tc._chat_col
        tc._db = _Database()
        tc._chat_col = _Collection()

    def tearDown(self):
        tc._db = self._orig_db
        tc._chat_col = self._orig_chat_col

    def test_wrong_quiz_answer_reply_is_thai_only(self):
        question_text = "Hva er høyeste tillatte hastighet i tettbebygd strøk hvis ikke annet er skiltet?"
        student_answer = "60 km/t"
        correct_answer = "50 km/t"

        message = (
            "อธิบายว่าทำไมคำตอบของฉันผิด\n\n"
            "<quiz_context>\n"
            "STUDENT ANSWERED INCORRECTLY. EXPLAIN WHY IT IS WRONG.\n"
            "is_correct: false\n"
            f"Question: {question_text}\n"
            f"Student answer: {student_answer}\n"
            f"Correct answer: {correct_answer}\n"
            "</quiz_context>"
        )
        req = TeacherChatRequest(message=message, language="th", device_id="thai-purity-test")
        response = asyncio.run(teacher_chat(req))

        # Windows terminals often default to a cp1252 codepage that cannot encode
        # Thai script; reconfigure stdout to UTF-8 so the reply actually prints
        # instead of crashing with UnicodeEncodeError.
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass

        banner = "=" * 70
        print(f"\n{banner}\nMICHAELS FULLE SVAR (language=th):\n{banner}")
        print(response.reply)
        print(banner)

        has_live_key = bool(
            os.environ.get("DEEPSEEK_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        if not has_live_key:
            self.skipTest(
                "No DEEPSEEK_API_KEY/OPENROUTER_API_KEY/OPENAI_API_KEY in the "
                "environment — teacher_chat() returned its canned fallback "
                "reply above instead of a real model answer. Set one of "
                "those env vars to actually exercise the LLM."
            )

        self.assertTrue(response.reply.strip())
        latin_words = re.findall(r"[A-Za-zÆØÅæøå]{3,}", response.reply)
        self.assertEqual(latin_words, [], f"Fant norske/engelske ord i thai-svaret: {latin_words}")

    def _chat_with_mock_model(self, request, model_reply):
        captured = {}

        async def complete(messages):
            captured["messages"] = messages
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=model_reply))])

        with patch.object(tc, "LLM_KEY", "test-key"), patch.object(
            tc, "_completion_with_fallback", new=complete
        ):
            response = asyncio.run(teacher_chat(request))
        return response, captured["messages"][0]["content"]

    def test_response_media_requires_existing_id_and_localizes_material(self):
        material = {
            "id": "lesson-1", "type": "image", "active": True,
            "approved_for_michael": True, "source_url": "/api/assets/lesson.jpg",
            "title": {"no": "Norsk tittel", "th": "ชื่อภาษาไทย", "en": "English title"},
            "caption": {"no": "Norsk beskrivelse", "th": "คำอธิบายภาษาไทย", "en": "English description"},
        }
        tc._db = _Database({"michael_materials": _Collection([material])})
        candidates = [
            {"id": "lesson-1", "type": "image", "url": "/api/assets/lesson.jpg",
             "title": "Norsk tittel", "caption": "Norsk beskrivelse"},
            {"id": "missing-id", "type": "image", "url": "/api/assets/missing.jpg",
             "title": "Missing", "caption": "Missing"},
        ]

        async def materials(*args, **kwargs):
            return candidates

        async def no_catalog(*args, **kwargs):
            return []

        with patch.object(tc, "_get_relevant_michael_materials", new=materials), patch.object(
            tc, "_get_relevant_catalog_media", new=no_catalog
        ):
            response, _ = self._chat_with_mock_model(
                TeacherChatRequest(message="อธิบายภาพนี้", language="th"), "คำอธิบายสั้น ๆ"
            )
        self.assertEqual([item["id"] for item in response.media], ["lesson-1"])
        self.assertEqual(response.media[0]["title"], "ชื่อภาษาไทย")
        self.assertEqual(response.media[0]["caption"], "คำอธิบายภาษาไทย")

    def test_quiz_coach_uses_wrong_answer_context_and_keeps_explanation(self):
        request = TeacherChatRequest(
            message=(
                "Hvorfor var svaret mitt feil? <quiz_context>"
                "Question: Vikeplikt i kryss; Student answer: Kjør først; "
                "Correct answer: Vikeplikt; Topic: § 7"
                "</quiz_context>"
            ),
            language="no", mode="quiz_coach",
        )
        model_reply = (
            "Det er lett å tro at du kan kjøre først. Valget gjelder ikke fordi bilen "
            "fra høyre har forkjørsrett her. § 7 sier at du må vike. "
            "Hvem ville du sluppet fram i dette krysset?"
        )
        response, prompt = self._chat_with_mock_model(request, model_reply)
        self.assertIn("Student answer: Kjør først", prompt)
        self.assertIn("Correct answer: Vikeplikt", prompt)
        self.assertIn("why that choice does not apply", prompt)
        self.assertIn("at most one targeted", prompt)
        self.assertEqual(response.mode, "quiz_coach")
        self.assertEqual(response.reply, model_reply)
        self.assertNotIn("FINAL OUTPUT CONTRACT", prompt)

    def test_system_prompt_distinguishes_yield_sign_from_stop_sign(self):
        prompts = {lang: tc._build_system_prompt(lang) for lang in ("no", "th", "en")}

        self.assertIn("Skilt 202 betyr IKKE obligatorisk stopp", prompts["no"])
        self.assertIn("Skilt 204 er annerledes", prompts["no"])
        self.assertIn("ป้าย 202 ไม่ได้บังคับให้หยุดทุกครั้ง", prompts["th"])
        self.assertIn("ป้ายหยุดต้องหยุดรถให้สนิททุกครั้ง", prompts["th"])
        self.assertIn("Sign 202 does NOT require a stop every time", prompts["en"])
        self.assertIn("must always come to a complete stop", prompts["en"])

    def test_simplify_uses_simple_junction_example_and_keeps_follow_up(self):
        request = TeacherChatRequest(message="Forklar vikeplikt enklere", language="th", mode="simplify")
        model_reply = "ที่ทางแยกในนอร์เวย์ ให้ดูรถทางขวา. คุณควรหยุดให้รถคันไหนไปก่อน?"
        response, prompt = self._chat_with_mock_model(request, model_reply)
        self.assertIn("seven-year-old rule", prompt)
        self.assertIn("Norwegian road junction", prompt)
        self.assertIn("only in Thai", prompt)
        self.assertEqual(response.reply, model_reply)
        self.assertNotIn("FINAL OUTPUT CONTRACT", prompt)

    def test_quiz_coach_without_answer_details_does_not_assume_wrong_answer(self):
        request = TeacherChatRequest(message="Can you help with this question?", language="en", mode="quiz_coach")
        model_reply = "Which answer did you choose, and what was the correct answer?"
        response, prompt = self._chat_with_mock_model(request, model_reply)
        self.assertIn("only in English", prompt)
        self.assertIn("If the answer details are missing", prompt)
        self.assertIn("(none supplied)", prompt)
        self.assertEqual(response.reply, model_reply)


if __name__ == "__main__":
    unittest.main()
