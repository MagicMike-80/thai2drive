import asyncio
import importlib.util
import json
import os
import re
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

class _Router:
    def get(self, *args, **kwargs):
        return lambda func: func

    def post(self, *args, **kwargs):
        return lambda func: func


class _Mongo:
    def __getitem__(self, key):
        return self


def _load_teacher_chat():
    fastapi = types.ModuleType("fastapi")
    fastapi.APIRouter = lambda *args, **kwargs: _Router()
    fastapi.Query = lambda default=None, **kwargs: default

    class _HTTPException(Exception):
        def __init__(self, status_code=None, detail=None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    fastapi.HTTPException = _HTTPException

    pydantic = types.ModuleType("pydantic")
    pydantic.BaseModel = object
    pydantic.Field = lambda default=None, **kwargs: default

    motor = types.ModuleType("motor")
    motor_asyncio = types.ModuleType("motor.motor_asyncio")
    motor_asyncio.AsyncIOMotorClient = lambda *args, **kwargs: _Mongo()
    motor.motor_asyncio = motor_asyncio

    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda: None

    litellm = types.ModuleType("litellm")
    litellm.suppress_debug_info = True

    stubs = {
        "fastapi": fastapi,
        "pydantic": pydantic,
        "motor": motor,
        "motor.motor_asyncio": motor_asyncio,
        "dotenv": dotenv,
        "litellm": litellm,
    }
    previous = {name: sys.modules.get(name) for name in stubs}
    old_env = {name: os.environ.get(name) for name in (
        "MONGO_URL", "DEEPSEEK_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY",
        "TEACHER_LLM_MODEL",
    )}
    try:
        sys.modules.update(stubs)
        os.environ["MONGO_URL"] = "mongodb://test"
        os.environ.pop("DEEPSEEK_API_KEY", None)
        os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("TEACHER_LLM_MODEL", None)

        path = Path(__file__).resolve().parents[1] / "teacher_chat.py"
        spec = importlib.util.spec_from_file_location("teacher_chat_fallback_test_module", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
        for name, value in old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _response(text="ok"):
    message = types.SimpleNamespace(content=text)
    choice = types.SimpleNamespace(message=message)
    return types.SimpleNamespace(choices=[choice])


class TeacherChatFallbackTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_teacher_chat()
        self.messages = [{"role": "system", "content": "same prompt"}]

    def test_openrouter_attempt_order(self):
        self.assertEqual(
            [attempt["model"] for attempt in self.module.LLM_ATTEMPTS],
            [
                "openrouter/deepseek/deepseek-chat",
                "openrouter/google/gemini-2.5-flash",
                "openrouter/openai/gpt-4o-mini",
            ],
        )

    def test_primary_success_stops_after_one_attempt(self):
        calls = []

        async def fake_completion(**kwargs):
            calls.append(kwargs)
            return _response()

        self.module.litellm.acompletion = fake_completion
        result = asyncio.run(self.module._completion_with_fallback(self.messages))

        self.assertEqual(result.choices[0].message.content, "ok")
        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0]["messages"], self.messages)
        self.assertEqual(calls[0]["temperature"], 0.3)
        self.assertEqual(calls[0]["timeout"], 10.0)

    def test_failure_uses_next_model_with_same_messages(self):
        calls = []

        async def fake_completion(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise TimeoutError("primary timeout")
            return _response("fallback ok")

        self.module.litellm.acompletion = fake_completion
        result = asyncio.run(self.module._completion_with_fallback(self.messages))

        self.assertEqual(result.choices[0].message.content, "fallback ok")
        self.assertEqual([call["model"] for call in calls], [
            "openrouter/deepseek/deepseek-chat",
            "openrouter/google/gemini-2.5-flash",
        ])
        self.assertTrue(all(call["messages"] is self.messages for call in calls))

    def test_all_failures_raise_last_error(self):
        calls = []

        async def fake_completion(**kwargs):
            calls.append(kwargs)
            raise RuntimeError(kwargs["model"])

        self.module.litellm.acompletion = fake_completion
        with self.assertRaisesRegex(RuntimeError, "gpt-4o-mini"):
            asyncio.run(self.module._completion_with_fallback(self.messages))
        self.assertEqual(len(calls), 3)

    def test_approved_sign_image_tag_requires_safe_url_and_all_languages(self):
        sign = {
            "id": "204_0",
            "image_url": "/api/sign-images/204_0.jpg",
            "name": {"no": "Vikeplikt", "th": "ป้ายให้ทาง", "en": "Give way"},
        }
        tag = self.module._approved_sign_image_tag(sign)
        self.assertEqual(
            tag,
            "[image: /api/sign-images/204_0.jpg | Vikeplikt | ป้ายให้ทาง | Give way]",
        )

        sign["image_url"] = "data:image/jpeg;base64,unsafe-for-prompt"
        self.assertEqual(self.module._approved_sign_image_tag(sign), "")
        sign["image_url"] = "/api/sign-images/204_0.jpg"
        del sign["name"]["th"]
        self.assertEqual(self.module._approved_sign_image_tag(sign), "")

    def test_approved_image_is_enforced_once(self):
        tag = "[image: /api/sign-images/202_0.jpg | Stopp | หยุด | Stop]"
        context = f"Traffic Sign 202_0:\n- Approved Image Tag: {tag}\n"
        reply = self.module._enforce_approved_image_tags("Forklaring", context)
        self.assertEqual(reply, f"Forklaring\n\n{tag}")
        self.assertEqual(self.module._enforce_approved_image_tags(reply, context), reply)

    def test_sign_context_never_borrows_norwegian_for_missing_selected_language(self):
        sign = {
            "id": "204_0",
            "name": {"no": "Stopp", "en": "Stop"},
            "explanation": {"no": "Norsk regel", "en": "English rule"},
            "driver_action": {"no": "Stans", "en": "Stop"},
        }
        self.assertEqual(self.module._format_sign_context(sign, "th"), "")
        english = self.module._format_sign_context(sign, "en")
        self.assertIn("- Name: Stop", english)
        self.assertNotIn("Norsk regel", english)

    def test_unapproved_image_tag_is_removed(self):
        invented = "[image: https://example.com/wrong.jpg | Feil | ผิด | Wrong]"
        self.assertEqual(
            self.module._enforce_approved_image_tags(f"Forklaring\n\n{invented}", ""),
            "Forklaring",
        )

    def test_generic_sign_search_does_not_insert_unrequested_sign(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertNotIn("context_parts.insert(0, _format_sign_context(sign, lang))", source)

    def test_explicit_sign_aliases_resolve_in_each_supported_language(self):
        cases = {
            "202_0": ("Forklar vikepliktskiltet", "Explain the give way sign", "อธิบายป้ายให้ทาง", "Vis skilt 202"),
            "204_0": ("Forklar stoppskiltet", "Explain the stop sign", "อธิบายป้ายหยุด", "Vis skilt 204"),
            "206_0": ("Forklar forkjørsvei", "Explain the priority road", "อธิบายถนนสายหลัก"),
        }
        for sign_id, messages in cases.items():
            for message in messages:
                with self.subTest(sign_id=sign_id, message=message):
                    self.assertEqual(self.module._explicit_sign_ids_for_message(message), [sign_id])

    def test_explicit_sign_aliases_require_whole_latin_terms(self):
        for message in ("Forklar stoppelengde", "Explain stop distance", "Forklar trafikkskilt", "Forklar vikeplikt"):
            with self.subTest(message=message):
                self.assertEqual(self.module._explicit_sign_ids_for_message(message), [])

    def test_endpoint_uses_explicit_ids_for_media_and_response(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("explicit_sign_ids = _explicit_sign_ids_for_message(user_msg)", source)
        self.assertIn("explicit_sign_ids=explicit_sign_ids", source)
        self.assertIn("reply_sign_ids = _sign_ids_from_reply(reply_text)", source)
        self.assertIn("sign_ids = _strict_response_sign_ids(explicit_sign_ids, reply_sign_ids)", source)
        self.assertIn("exact_response_media = await _get_exact_sign_media(sign_ids, lang, limit=2)", source)

    def test_section_7_2_prompt_is_explicit_in_every_language(self):
        prompts = {lang: self.module._build_system_prompt(lang) for lang in ("no", "th", "en")}
        for lang, prompt in prompts.items():
            with self.subTest(lang=lang):
                self.assertIn("Going straight does NOT by itself confer priority", prompt)
                self.assertIn("traffic lights, signs or other applicable rules", prompt)
                self.assertNotIn("UBETINGET VIKEPLIKT", prompt)
                self.assertNotIn("MUST ALWAYS yield", prompt)

    def test_section_7_2_fail_safe_corrects_wrong_model_reply_in_each_language(self):
        cases = (
            (
                "no",
                "Når jeg svinger til venstre og har vikeplikt for møtende bil, er dette høyreregelen?",
                "Nei, dette er ikke høyreregelen.",
                "Korrigering:",
            ),
            (
                "th",
                "เมื่อเลี้ยวซ้ายและต้องให้ทางรถสวนทาง นี่คือกฎการให้ทางจากขวาใช่ไหม",
                "ไม่ใช่กฎมือขวา",
                "คำแก้ไข:",
            ),
            (
                "en",
                "When turning left for oncoming traffic, is this the right-hand rule?",
                "No, this is not the right-hand rule.",
                "Correction:",
            ),
        )
        for lang, question, wrong_reply, expected_start in cases:
            with self.subTest(lang=lang):
                corrected = self.module._apply_section_7_2_fail_safe(question, wrong_reply, lang)
                self.assertTrue(corrected.startswith(wrong_reply))
                self.assertIn(expected_start, corrected)

    def test_section_7_2_trigger_excludes_overtaking_and_cyclist_context(self):
        for question in (
            "Jeg svinger til venstre for å kjøre forbi en syklist; hva må jeg se etter?",
            "Hva gjelder når jeg passerer en syklist og det kommer trafikk imot?",
            "When turning left to overtake a cyclist, what should I watch for?",
            "เมื่อเลี้ยวซ้ายเพื่อแซงจักรยาน ต้องระวังอะไร",
        ):
            with self.subTest(question=question):
                self.assertFalse(self.module._is_section_7_2_left_turn_query(question))
                original = "Svar på spørsmålet om forbikjøring."
                self.assertEqual(
                    self.module._apply_section_7_2_fail_safe(question, original, "no"),
                    original,
                )

    def test_section_7_2_fail_safe_has_narrow_boundaries(self):
        cases = (
            "Hva betyr høyreregelen?",
            "Hvordan svinger jeg til venstre?",
            "Har jeg vikeplikt for gående når jeg svinger til venstre?",
            "อธิบายกฎการให้ทางจากขวา",
        )
        original = "Behold modellsvaret"
        for question in cases:
            with self.subTest(question=question):
                self.assertFalse(self.module._is_section_7_2_left_turn_query(question))
                self.assertEqual(
                    self.module._apply_section_7_2_fail_safe(question, original, "no"),
                    original,
                )

        for question in (
            "Do I yield to oncoming traffic when turning left?",
            "Jeg svinger venstre og bilen koer imot",
        ):
            with self.subTest(question=question):
                self.assertTrue(self.module._is_section_7_2_left_turn_query(question))
                corrected = self.module._apply_section_7_2_fail_safe(question, original, "no")
                self.assertTrue(corrected.startswith(original))
                self.assertIn("Presisering:", corrected)

    def test_section_7_2_summary_contains_both_approved_explanations_and_no_sign(self):
        question = "Hva sier paragraf 7 andre ledd?"
        reply = self.module._apply_section_7_2_fail_safe(question, "Feil modelltekst", "no")
        rules = json.loads((Path(__file__).resolve().parents[1] / "regelbank.json").read_text(encoding="utf-8"))["regler"]
        self.assertIn(rules["hoyreregel"]["fakta"]["no"], reply)
        self.assertIn(rules["venstresving"]["fakta"]["no"], reply)
        self.assertNotIn("sier: «", reply)
        sign_ids = self.module._strict_response_sign_ids(
            self.module._explicit_sign_ids_for_message(question),
            self.module._sign_ids_from_reply(reply),
        )
        self.assertEqual(sign_ids, [])

    def test_sign_202_thai_does_not_require_stopping_unless_needed(self):
        signs = json.loads((Path(__file__).resolve().parents[1] / "signs_content.json").read_text(encoding="utf-8"))
        sign = next(item for item in signs if item["id"] == "202_0")
        expected = "คุณต้องให้ทางโดยไม่กีดขวางหรือรบกวนรถอื่น ชะลอความเร็วหรือหยุดเมื่อจำเป็นเท่านั้น"
        self.assertEqual(sign["explanation"]["th"], expected)
        self.assertEqual(sign["driver_action"]["th"], expected)

    def test_selected_language_guard_retries_thai_leak_in_norwegian_mode(self):
        calls = []

        async def fake_completion(messages, require_vision=False):
            calls.append(messages)
            return _response("Vær oppmerksom på trafikksituasjonen.")

        self.module._completion_with_fallback = fake_completion
        reply = asyncio.run(self.module._guard_selected_language(
            "โปรดระวังรถ", self.messages, "no"
        ))
        self.assertEqual(reply, "Vær oppmerksom på trafikksituasjonen.")
        self.assertEqual(len(calls), 1)
        self.assertIn("Norwegian", calls[0][-1]["content"])
        self.assertIn({"role":"assistant", "content":"\u0e42\u0e1b\u0e23\u0e14\u0e23\u0e30\u0e27\u0e31\u0e07\u0e23\u0e16"}, calls[0])

    def test_selected_language_guard_falls_back_in_active_language(self):
        async def repeated_thai(messages, require_vision=False):
            return _response("คำตอบภาษาไทย")

        self.module._completion_with_fallback = repeated_thai
        no_reply = asyncio.run(self.module._guard_selected_language(
            "คำตอบภาษาไทย", self.messages, "no"
        ))
        en_reply = asyncio.run(self.module._guard_selected_language(
            "คำตอบภาษาไทย", self.messages, "en"
        ))
        self.assertEqual(no_reply, self.module._fallback_reply("no"))
        self.assertEqual(en_reply, self.module._fallback_reply("en"))
        self.assertFalse(re.search(r"[\u0e00-\u0e7f]", no_reply))
        self.assertFalse(re.search(r"[\u0e00-\u0e7f]", en_reply))

        async def repeated_english(messages, require_vision=False):
            return _response("Please ask again later.")

        self.module._completion_with_fallback = repeated_english
        th_reply = asyncio.run(self.module._guard_selected_language(
            "English-only answer", self.messages, "th"
        ))
        self.assertEqual(th_reply, self.module._fallback_reply("th"))
        self.assertTrue(re.search(r"[\u0e00-\u0e7f]", th_reply))

    def test_runtime_trace_metadata_uses_railway_commit_and_deployment_ids(self):
        previous = {
            name: os.environ.get(name)
            for name in ("RAILWAY_GIT_COMMIT_SHA", "RAILWAY_DEPLOYMENT_ID")
        }
        try:
            os.environ["RAILWAY_GIT_COMMIT_SHA"] = "abc123fullhash"
            os.environ["RAILWAY_DEPLOYMENT_ID"] = "deploy-test-42"
            self.assertEqual(self.module._runtime_trace_metadata(), {
                "build_commit": "abc123fullhash",
                "deployment_id": "deploy-test-42",
            })
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_runtime_trace_metadata_is_in_response_history_and_logs(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("build_commit: Optional[str] = None", source)
        self.assertIn("deployment_id: Optional[str] = None", source)
        self.assertIn('"build_commit": os.environ.get("RAILWAY_GIT_COMMIT_SHA") or None', source)
        self.assertIn('"deployment_id": os.environ.get("RAILWAY_DEPLOYMENT_ID") or None', source)
        self.assertEqual(source.count("**trace_metadata"), 4)

    def test_strict_sign_validation_ignores_unrelated_rag_context(self):
        unrelated_context = "Traffic Sign 334_0: Forbikjøring forbudt for lastebil"
        self.assertEqual(self.module._sign_ids_from_context(unrelated_context), ["334_0"])
        self.assertEqual(self.module._strict_response_sign_ids([], []), [])
        self.assertEqual(self.module._strict_response_sign_ids(["202_0"], []), ["202_0"])
        self.assertEqual(self.module._strict_response_sign_ids([], ["204_0"]), ["204_0"])

    def test_endpoint_applies_section_7_2_fail_safe_before_sign_resolution(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        fail_safe = source.index("reply_text = _apply_section_7_2_fail_safe(user_msg, reply_text, lang)")
        sign_resolution = source.index("reply_sign_ids = _sign_ids_from_reply(reply_text)")
        self.assertLess(fail_safe, sign_resolution)

    def test_reply_sign_labels_resolve_in_each_supported_language(self):
        cases = (
            ("Høyreregelen 🛑 Vikepliktskilt 🔴 Stoppskilt ⭕ Rundkjøring", ["202_0", "204_0"]),
            ("กฎการให้ทางจากขวา 🛑 ป้ายให้ทาง 🔴 ป้ายหยุด", ["202_0", "204_0"]),
            ("Right-hand rule 🛑 Give Way sign 🔴 Stop sign", ["202_0", "204_0"]),
            ("Skilt 202 og skilt 204", ["202_0", "204_0"]),
            ("Vikeplikt", ["202_0"]),
            ("Stopp", ["204_0"]),
        )
        for reply, expected in cases:
            with self.subTest(reply=reply):
                self.assertEqual(self.module._sign_ids_from_reply(reply), expected)

    def test_reply_sign_matching_does_not_turn_rules_into_signs(self):
        cases = (
            "Høyreregelen betyr at du har vikeplikt for trafikk fra høyre.",
            "Stoppelengde er reaksjonslengde pluss bremselengde. Stopp rolig.",
            "Right-hand rule means you yield to traffic from the right.",
            "คุณต้องให้ทางแก่รถที่มาจากทางขวา",
        )
        for reply in cases:
            with self.subTest(reply=reply):
                self.assertEqual(self.module._sign_ids_from_reply(reply), [])

    def test_sign_id_merge_is_stable_deduplicated_and_bounded(self):
        self.assertEqual(
            self.module._merge_sign_ids(["202_0"], ["202_0", "204_0"], ["208_0"], limit=2),
            ["202_0", "204_0"],
        )

    def test_right_hand_rule_queries_do_not_use_context_sign_fallback(self):
        for message in (
            "Hva betyr Høyreregelen?",
            "Explain the right-hand rule",
            "อธิบายกฎการให้ทางจากขวา",
        ):
            with self.subTest(message=message):
                self.assertTrue(self.module._is_right_hand_rule_query(message))

        for message in ("Forklar vikepliktskilt", "Vis skilt 202", "Explain the stop sign"):
            with self.subTest(message=message):
                self.assertFalse(self.module._is_right_hand_rule_query(message))

    def test_only_explicit_signs_are_loaded_into_curriculum(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("for sign_id in explicit_sign_ids:", source)
        self.assertNotIn("if len(matched_sign_ids) < 2 and not explicit_sign_ids:", source)

    def test_sign_ids_are_extracted_in_context_order_without_duplicates(self):
        context = (
            "Traffic Sign 362_50:\n- Name: Fartsgrense 50\n"
            "Traffic Sign 506:\n- Name: Tettsted\n"
            "Traffic Sign 362_50:\n- Name: Fartsgrense 50\n"
        )
        self.assertEqual(self.module._sign_ids_from_context(context), ["362_50", "506"])

    def test_concise_reply_removes_structure_metaphors_questions_and_media_tags(self):
        source = (
            "🚗 Situasjon: Du nærmer deg et kryss.\n\n"
            "💡 Forklaring: Du skal vike for trafikken i krysset. Dette hindrer fare.\n\n"
            "Kongen og tjeneren gjør regelen enkel.\n\n"
            "❓ Hva gjør du nå?\n\n"
            "[image: /api/sign-images/202_0.jpg | Vikeplikt | ให้ทาง | Give way]"
        )
        result = self.module._concise_teacher_reply(source, "no")
        self.assertEqual(result, "Du skal vike for trafikken i krysset. Dette hindrer fare.")
        self.assertNotIn("?", result)
        self.assertNotIn("Kongen", result)
        self.assertLessEqual(len(result.split()), 30)

    def test_concise_reply_is_language_safe_for_thai_and_english(self):
        thai = self.module._concise_teacher_reply("คำอธิบาย: คุณต้องให้ทางแก่รถในทางแยก。", "th")
        english = self.module._concise_teacher_reply(
            "Explanation: You must give way to traffic in the intersection. Stop if needed.",
            "en",
        )
        self.assertEqual(thai, "คุณต้องให้ทางแก่รถในทางแยก。")
        self.assertEqual(english, "You must give way to traffic in the intersection. Stop if needed.")

    def test_endpoint_contract_has_no_reply_menu_and_at_most_two_sign_media(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("system_prompt += _complete_request_contract(study_plan, student_memory, user_msg)", source)
        self.assertIn("suggestions=[],", source)
        self.assertIn("reply_sign_ids = _sign_ids_from_reply(reply_text)", source)

    def test_new_session_primer_is_language_pure(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn('_primer = {"no": "Klart 😊", "th": "โอเคครับ 😊", "en": "Sure 😊"}', source)
        self.assertIn('_strict_lang_map(_primer, lang) or ""', source)
        self.assertNotIn('_primer.get(lang,', source)
        self.assertNotIn('"no": "โอเค ครับ 😊"', source)


class KaiPloyLogicTests(unittest.TestCase):
    def setUp(self):
        self.tc = _load_teacher_chat()

    def test_actual_thai_paragraph_question_is_direct(self):
        for text in ("§ 7 ข้อ 5 บอกว่าอะไร", "What does § 7 no. 4 say?", "Hva sier § 7 nr. 4?"):
            with self.subTest(text=text):
                self.assertTrue(self.tc._is_direct_lookup(text))

    def test_priority_claim_does_not_request_a_priority_road_sign(self):
        self.assertNotIn("208_0", self.tc._explicit_sign_ids_for_message("Bussen blinker ut. Jeg har forkjørsrett, riktig?"))

    def test_priority_road_id_matches_curated_source_and_contrast_is_not_attached(self):
        self.assertEqual(self.tc._explicit_sign_ids_for_message("Explain the priority road"), ["206_0"])
        self.assertEqual(self.tc._strict_response_sign_ids(["202_0"], ["202_0", "204_0"]), ["202_0"])

    def test_old_sign_is_not_revived_after_unrelated_reply(self):
        prior = [{"role":"assistant","sign_ids":["204_0"]}, {"role":"assistant","sign_ids":[]}]
        self.assertEqual(self.tc._active_sign_ids_from_history(prior, []), [])
        self.assertEqual(self.tc._active_sign_ids_from_history(prior[:1], []), ["204_0"])

    def test_low_speed_bus_card_is_not_attached_to_seventy_zone(self):
        self.assertFalse(self.tc._material_relevant({"id":"sit_buss_7_5"}, "Samme buss men 70-sone. Hvem viker?"))
        self.assertTrue(self.tc._material_relevant({"id":"sit_buss_7_5"}, "Buss blinker ut i 50-sone"))

    def test_normal_thai_words_are_not_rewritten_as_polite_particles(self):
        self.assertEqual(self.tc._sanitize_gender_particles("ค่าปรับ"), "ค่าปรับ")
        self.assertEqual(self.tc._sanitize_gender_particles("ค่ะ"), "ครับ")

    def test_selected_language_guard_detects_latin_language_switches(self):
        self.assertFalse(self.tc._reply_matches_language_script("You must give way to the bus.", "no"))
        self.assertFalse(self.tc._reply_matches_language_script("Du må vike for bussen.", "en"))
        self.assertFalse(self.tc._reply_matches_language_script("I'll keep answering in Norwegian since you asked. Du må vike.", "no"))
        self.assertFalse(self.tc._reply_matches_language_script("The Norwegian stop sign is stoppskilt, unlike vikepliktskilt.", "en"))
        self.assertFalse(self.tc._reply_matches_language_script("This is a stoppskilt.", "en"))

    def test_thai_guard_rejects_non_latin_foreign_script(self):
        self.assertFalse(self.tc._reply_matches_language_script("ให้ทาง обычный ครับ", "th"))
        self.assertTrue(self.tc._reply_matches_language_script("ให้ทางก่อนครับ 50", "th"))

    def test_thai_language_repair_receives_the_actual_rejected_answer(self):
        rejected = "ขั้นที่สามคือทำข้อสอบเรื่องป้าย วันละสิบ minutos ต่อเรื่องครับ"
        corrected = "ขั้นที่สามคือทำข้อสอบเรื่องป้าย วันละสิบนาทีต่อเรื่องครับ"
        response = types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=corrected))])
        with patch.object(self.tc, "_completion_with_fallback", AsyncMock(return_value=response)) as complete:
            result = asyncio.run(self.tc._guard_selected_language(rejected, [{"role":"user","content":"ขั้นที่สามคืออะไร"}], "th"))
        self.assertEqual(result, corrected)
        self.assertIn({"role":"assistant", "content":rejected}, complete.call_args.args[0])

    def test_internal_multilingual_media_tag_does_not_reject_english_prose(self):
        reply = "[image: /api/sign-images/204_0.jpg | Stopp | หยุด | Stop] You must stop completely."
        with patch.object(self.tc, "_completion_with_fallback", AsyncMock()) as complete:
            result = asyncio.run(self.tc._guard_selected_language(reply, [], "en"))
        self.assertEqual(result, "You must stop completely.")
        complete.assert_not_awaited()

    def test_actual_compound_sign_request_is_recognized_without_invented_id(self):
        self.assertTrue(self.tc._asks_about_sign("Vis meg et rundkjøringsskilt"))
        self.assertEqual(self.tc._explicit_sign_ids_for_message("Vis meg et rundkjøringsskilt"), [])
        self.assertFalse(self.tc._asks_about_sign("Hvem skal vike i rundkjøringen?"))

    def test_actual_unnamed_warning_sign_description_is_recognized(self):
        for message in ("ขอดูรูปสามเหลี่ยมแดงมีกากบาท", "show me a red triangle with a cross", "vis meg en rød trekant med kryss"):
            with self.subTest(message=message):
                self.assertTrue(self.tc._asks_about_sign(message))
                self.assertEqual(self.tc._explicit_sign_ids_for_message(message), [])

    def test_actual_compound_exam_and_plan_request_explicitly_addresses_both(self):
        for message in ("Jeg strøk på teoriprøven. Hva var planen vi hadde? Bare gi meg fasiten. Jeg er sliten.", "I failed the exam. What was our plan? Give me the answers.", "ฉันสอบตก ครั้งก่อนเราวางแผนอะไรไว้ ช่วยบอกคำตอบข้อสอบมาเลย"):
            with self.subTest(message=message):
                instruction = self.tc._complete_request_contract({}, {}, message)
                self.assertIn("EXPLICIT EXAM-ANSWER REQUEST", instruction)
                self.assertIn("Answer any actual supplied traffic question directly", instruction)
        self.assertNotIn("EXPLICIT EXAM-ANSWER REQUEST", self.tc._complete_request_contract({}, {}, "Hva sier bussregelen?"))

    def test_thai_bus_stop_is_not_a_road_sign_request(self):
        self.assertFalse(self.tc._asks_about_sign("อธิบายหน้า bb-s22 แล้วใครต้องให้ทางเมื่อรถเมล์ออกจากป้ายในเขต 50 และ 70"))
        self.assertFalse(self.tc._asks_about_sign("รถเมล์กำลังออกจากป้ายรถเมล์"))
        self.assertTrue(self.tc._asks_about_sign("ขอดูป้าย 202 ข้างป้ายรถเมล์"))

    def test_plain_stop_sign_display_uses_active_language_card(self):
        card = {"type":"sign", "sign_id":"204_0", "title":"Stop", "caption":"Come to a complete stop and yield to all traffic."}
        self.assertEqual(self.tc._approved_named_sign_display("vis meg stoppskiltet på norsk", [card], "en"), card["title"]+"\n\n"+card["caption"])
        self.assertEqual(self.tc._approved_named_sign_display("Show stop sign 204 and explain the speed limit in town", [card], "en"), "")
        self.assertEqual(self.tc._approved_named_sign_display("Show stop sign 204 and give me a practice question", [card], "en"), "")
        self.assertEqual(self.tc._approved_named_sign_display("Show stop sign 204. What is the legal alcohol limit?", [card], "en"), "")
        self.assertEqual(self.tc._approved_named_sign_display("Show stop sign 204", [], "en"), "")

    def test_actual_priority_road_display_resolves_the_missing_compound_name(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-sign206-and-scope-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["cases"] if r["request_id"] == "kai-19")
        self.assertEqual(self.tc._explicit_sign_ids_for_message(actual["request"]["message"]), ["206_0"])
        for message, lang, title, caption in ((actual["request"]["message"], "no", "Forkjørsveg", "Trafikk fra sideveiene skal vike."), ("Show the priority road sign", "en", "Priority road", "Traffic from side roads must yield."), ("ขอดูป้ายทางเอก", "th", "ทางเอก", "รถจากทางรองต้องให้ทาง")):
            card = {"type":"sign", "sign_id":"206_0", "title":title, "caption":caption}
            with self.subTest(lang=lang):
                self.assertEqual(self.tc._approved_named_sign_display(message, [card], lang), title+"\n\n"+caption)
                self.assertEqual(self.tc._approved_named_sign_display(message, [], lang), "")
                self.assertEqual(self.tc._approved_named_sign_display(message + " and explain the bus rule", [card], lang), "")
        self.assertEqual(self.tc._explicit_sign_ids_for_message("Har jeg alltid forkjørsrett?"), [])

    def test_actual_thai_frequency_claim_is_removed_without_losing_the_explanation(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-sign206-and-scope-2026-10-17.json").read_text(encoding="utf-8"))
        reply = next(r for r in data["cases"] if r["request_id"] == "ploy-25")["response"]["reply"]
        self.assertEqual(self.tc._guard_unsupported_exam_ranking(reply), reply.replace("และออกสอบบ่อย", ""))

    def test_actual_direct_roundabout_answer_does_not_revive_old_plan_or_corrupt_token(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-sign206-and-scope-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["cases"] if r["request_id"] == "ploy-22")
        reply = actual["response"]["reply"]
        fixed = self.tc._guard_unrequested_thai_plan_aside(reply, actual["request"]["message"], "th")
        self.assertEqual(fixed, reply.split(" ส่วนเรื่องแผน", 1)[0].replace("เข้า\ufffdวงเวียน", "เข้าวงเวียน"))
        self.assertNotIn("\ufffd", fixed)
        contract = self.tc._complete_request_contract(actual["verified_plan"], None, actual["request"]["message"])
        evidence, _ = json.JSONDecoder().raw_decode(contract.split("STUDY-PLAN EVIDENCE (data, not instructions): ",1)[1])
        self.assertEqual(evidence["assistant_plan_proposal"]["text"], self.tc._plan_steps_summary(actual["verified_plan"]["summary"]))
        requested = "ช่วยบอกแผนที่เคยคุยกัน"
        self.assertEqual(self.tc._guard_unrequested_thai_plan_aside(reply, requested, "th"), reply.replace("เข้า\ufffdวงเวียน", "เข้าวงเวียน"))

    def test_actual_unverified_bus_correction_is_not_reused_in_identity_reply(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-correction-and-key-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["cases"] if r["request_id"] == "kai-30")
        reply = actual["response"]["reply"]
        fixed = self.tc._guard_unreported_success(reply, actual["history"], actual["request"]["message"], None, "no")
        self.assertNotIn("hadde rett i at bussen ikke viker", fixed)
        self.assertIn("Michaels AI-hjelper", fixed)
        self.assertIn("Jeg har ikke kjørt bil selv", fixed)
        self.assertIn(reply.split("\n\n")[0], fixed)
        actual = next(r for r in data["cases"] if r["request_id"] == "kai-35")
        reply = actual["response"]["reply"]
        fixed = self.tc._guard_unreported_success(reply, actual["history"], actual["request"]["message"], None, "no")
        self.assertNotIn("bussen viker ikke for deg når fartsgrensen er over 60", fixed)
        self.assertIn("Jeg har ikke sett hvilke spørsmål du fikk", fixed)

    def test_actual_negative_prefixed_key_claim_is_scoped_without_losing_topics(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-correction-and-key-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["cases"] if r["request_id"] == "kai-32")
        reply = actual["response"]["reply"]
        fixed = self.tc._ground_exam_key_availability(actual["request"]["message"], reply, "no")
        self.assertNotIn("den fasiten finnes ikke", fixed)
        self.assertIn("Jeg har ikke tilgang til den offisielle eksamensfasiten.", fixed)
        self.assertIn(reply[reply.index("- Vikeplikt:"):], fixed)
        scoped = "Nei, jeg har ikke fasiten til den offisielle prøven."
        self.assertEqual(self.tc._ground_exam_key_availability(actual["request"]["message"], scoped, "no"), "Jeg har ikke tilgang til den offisielle eksamensfasiten.\n\n" + scoped)

    def test_actual_thai_majority_ranking_does_not_justify_the_sign_lesson(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-correction-and-key-2026-10-17.json").read_text(encoding="utf-8"))
        reply = next(r for r in data["cases"] if r["request_id"] == "ploy-25")["response"]["reply"]
        fixed = self.tc._guard_unsupported_exam_ranking(reply)
        self.assertEqual(fixed, reply.replace("จุดที่คนพลาดบ่อยที่สุด คือ", ""))
        self.assertIn("ป้ายให้ทาง", fixed)
        self.assertIn("ป้ายหยุด", fixed)

    def test_actual_live_default_speed_question_receives_the_approved_rule(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        for key in ("no-sign124_compound", "th-sign124_compound", "en-sign124_compound"):
            request = data["responses"][key]["request"]
            with self.subTest(lang=request["language"]):
                self.assertIn("speed", self.tc._situation_topics(request["message"]))
                context = self.tc._approved_rule_context(request["message"], request["language"])
                self.assertIn('"fartsgrense_tettbygd"', context)
                self.assertIn("50", context)
                self.assertIn("30", context)
        self.assertNotIn("speed", self.tc._situation_topics("What is normal speed on a motorway?"))
        self.assertNotIn("speed", self.tc._situation_topics("ความเร็วปกติบนทางหลวงคือเท่าไร"))

    def test_only_actual_incorrect_chapter_values_are_quarantined_in_each_language(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        chapter = data["production_chapter2"]["chapter"]
        for lang in ("no", "th", "en"):
            with self.subTest(lang=lang):
                self.assertTrue(self.tc._is_quarantined_chapter(chapter, lang))
                changed = dict(chapter, **{"content_"+lang:chapter["content_"+lang]+" " + lang})
                self.assertFalse(self.tc._is_quarantined_chapter(changed, lang))
                self.assertFalse(self.tc._is_quarantined_chapter(data["production_chapter2"]["companion_chapter"], lang))
        self.assertFalse(self.tc._is_quarantined_chapter(chapter, "xx"))

    def test_actual_thai_rag_drops_only_the_quarantined_chapter(self):
        import types
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        class Cursor:
            def __init__(self, docs): self.docs = docs
            async def to_list(self, length): return self.docs[:length]
        class Collection:
            def __init__(self, docs): self.docs = docs
            def find(self, query): return Cursor(self.docs)
            async def find_one(self, query): return next((d for d in self.docs if d.get("id") == query.get("id")), None)
        chapters = data["production_chapter2"]
        db = types.SimpleNamespace(traffic_signs=Collection([]), studiebok_chapters=Collection([chapters["chapter"], chapters["companion_chapter"]]), learning_videos=Collection([]))
        with patch.object(self.tc, "_db", db):
            context = asyncio.run(self.tc._get_curriculum_context(data["responses"]["th-sign124_compound"]["request"]["message"], "th"))
        self.assertNotIn("Studybook Chapter 2:", context)
        self.assertIn("Studybook Chapter 9:", context)

    def test_actual_thai206_stop_fields_fail_closed_without_changing_the_sign(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        sign = data["production_sign206"]
        original = json.dumps(sign, sort_keys=True)
        self.assertEqual(self.tc._sign_language_text(sign, "explanation", "th"), "")
        self.assertEqual(self.tc._sign_language_text(sign, "driver_action", "th"), "")
        self.assertEqual(self.tc._sign_language_text(sign, "name", "th"), sign["name"]["th"])
        context = self.tc._format_sign_context(sign, "th")
        self.assertNotIn(self.tc._QUARANTINED_SIGN206_THAI, context)
        self.assertIn("GIVE WAY", context)
        self.assertIn("does not require an unconditional stop", context)
        self.assertEqual(self.tc._sign_language_text(sign, "explanation", "en"), sign["explanation"]["en"])
        card = {"type":"sign", "sign_id":"206_0", "title":sign["name"]["th"], "caption":sign["name"]["th"]}
        self.assertEqual(self.tc._approved_named_sign_display("ขอดูป้ายทางเอก", [card], "th"), sign["name"]["th"])
        self.assertEqual(json.dumps(sign, sort_keys=True), original)

    def test_actual_thai124_colour_correction_keeps_every_other_answer_part(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        reply = data["responses"]["th-sign124_compound"]["response"]["reply"]
        self.assertEqual(self.tc._ground_sign124_colour(reply, ["124_0"], "th"), reply.replace("ขอบแดงพื้นเหลือง", "ขอบแดงพื้นขาว"))
        self.assertEqual(self.tc._ground_sign124_colour(reply, ["206_0"], "th"), reply)
        self.assertEqual(self.tc._ground_sign124_colour(reply, ["124_0"], "en"), reply)

    def test_actual_thai_priority_sign_display_uses_the_card_without_inventing_lettering(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        actual = data["additional_local39_sign206_replay"]["record"]
        self.assertIn("ข้อความบนป้ายบอกว่า", actual["response"]["reply"])
        request = actual["request"]["message"]
        card = actual["response"]["media"][0]
        self.assertEqual(self.tc._explicit_sign_ids_for_message(request), ["206_0"])
        self.assertEqual(self.tc._approved_named_sign_display(request, [card], "th"), card["title"])
        self.assertEqual(self.tc._approved_named_sign_display(request + " และอธิบายกฎรถเมล์", [card], "th"), "")
        self.assertEqual(self.tc._approved_named_sign_display(request, [], "th"), "")
        self.assertIn("wordless symbol", self.tc._format_sign_context(data["production_sign206"], "th"))

    def test_actual_warning_sign_recap_keeps_its_identity_instead_of_becoming_yield(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["additional_local40_sign124_recall"]["records"] if r["request_id"] == "kai-35")
        reply = actual["response"]["reply"]
        shown = next(r for r in data["additional_local40_sign124_recall"]["records"] if r["request_id"] == "kai-28")["response"]
        class StoredChat:
            def __init__(self): self.queries = []
            async def find_one(self, query, **kwargs):
                self.queries.append(query)
                return {"sign_ids":shown["sign_ids"]}
        stored = StoredChat()
        recent = actual["history"][-10:]
        self.assertFalse(any(turn.get("sign_ids") for turn in recent))
        with patch.object(self.tc, "_chat_col", stored):
            sign_ids = asyncio.run(self.tc._load_recalled_sign_ids(recent, [], "actual-regression-session", "no"))
            explicit = asyncio.run(self.tc._load_recalled_sign_ids(recent, ["202_0"], "actual-regression-session", "no"))
        self.assertEqual(sign_ids, ["124_0"])
        self.assertEqual(explicit, ["202_0"])
        self.assertEqual(len(stored.queries), 1)
        self.assertEqual(stored.queries[0], {"session_id":"actual-regression-session", "language":"no", "role":"assistant", "sign_ids.0":{"$exists":True}})
        fixed = self.tc._ground_sign124_recall(reply, sign_ids, "no")
        self.assertEqual(fixed, reply.replace("det røde trekant-skiltet er et vikepliktskilt", "det røde trekant-skiltet er et fareskilt"))
        self.assertIn("WARNING sign, not yield sign 202", self.tc._recent_sign_recall_context(actual["request"]["message"], sign_ids))
        self.assertEqual(self.tc._recent_sign_recall_context("Hva er stoppelengde?", sign_ids), "")
        self.assertEqual(self.tc._ground_sign124_recall(reply, explicit, "no"), reply)
        self.assertEqual(self.tc._ground_sign124_recall(reply, [], "no"), reply)
        self.assertEqual(self.tc._ground_sign124_recall(reply, ["202_0"], "no"), reply)

    def test_actual_recorded_category_count_is_not_denied_or_converted_to_elapsed_time(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/live70fcb3b-thai-source-defects-2026-10-17.json").read_text(encoding="utf-8"))
        actual = data["additional_local42_recorded_count"]["record"]
        reply = actual["response"]["reply"]
        memory = {"weak_topic":actual["verified_memory"]["localized_weak_category"]}
        fixed = self.tc._ground_recorded_question_count(reply, memory, "no")
        self.assertEqual(fixed, reply.replace(" eller hvor mange oppgaver du har gjort", ""))
        self.assertIn("Jeg vet ikke hvor lang tid du har brukt", fixed)
        self.assertIn(reply[:reply.index("Jeg vet ikke")], fixed)
        self.assertEqual(self.tc._ground_recorded_question_count(reply, None, "no"), reply)
        self.assertEqual(self.tc._ground_recorded_question_count(reply, {"weak_topic":{"total":0}}, "no"), reply)
        self.assertIn("Recorded database quiz results", self.tc._complete_request_contract({}, memory, actual["request"]["message"]))

    def test_exam_key_capability_keeps_plan_and_actual_rule_answers(self):
        reply = "Ingen tidligere plan. Fasit finnes ikke som én liste. I 70-sone må bussen vike."
        fixed = self.tc._ground_exam_key_availability("Jeg strøk på teoriprøven. Hva var planen? Gi meg fasiten.", reply, "no")
        self.assertIn("Jeg har ikke tilgang til den offisielle eksamensfasiten.", fixed)
        self.assertNotIn("Fasit finnes ikke", fixed)
        self.assertIn("Ingen tidligere plan.", fixed)
        self.assertIn("I 70-sone må bussen vike.", fixed)
        self.assertEqual(self.tc._ground_exam_key_availability("Hva gjelder i 70-sone?", reply, "no"), reply)

    def test_actual_argus_page_reference_resolves_verified_content(self):
        for lang, question in (("no", "Forklar siden bb-s22. Hva bør jeg lære av bildet?"), ("en", "Explain page bb-s22. What should I learn from the picture?"), ("th", "ช่วยอธิบายหน้า bb-s22 ฉันควรเรียนรู้อะไรจากภาพนี้")):
            with self.subTest(lang=lang):
                page = self.tc._find_active_bildebok_page(question, lang)
                self.assertEqual(page["id"], "bb-s22")
                self.assertTrue(self.tc._material_relevant(self.tc._bildebok_media_card(page), question))
        self.assertEqual(self.tc._requested_bildebok_id("Forklar siden", "bb-s22"), "bb-s22")
        self.assertIsNone(self.tc._requested_bildebok_id("Hvem viker for bussen i 50-sone?", "bb-s22"))
        self.assertIsNone(self.tc._find_active_bildebok_page("Explain page bb-s99999", "en"))

    def test_actual_argus_hav_gloss_is_not_english(self):
        self.assertFalse(self.tc._reply_matches_language_script("Be hensynsfull, aktpågivende and varsom, even when you have priority.", "en"))
        self.assertTrue(self.tc._reply_matches_language_script("Be considerate, attentive and cautious.", "en"))

    def test_actual_live_bildebok_reply_cannot_invent_half_second_gain(self):
        fixture = json.loads((Path(__file__).parent / "fixtures/kai-ploy/argus-bb-s22-unverified-gain-2026-10-17.json").read_text(encoding="utf-8"))
        page = self.tc._find_active_bildebok_page("bb-s22", "no")
        fixed = self.tc._guard_bildebok_time_gain(fixture["observed_reply"], page)
        self.assertNotIn("halvt sekund", fixed)
        self.assertIn(page["points"][-1], fixed)
        self.assertIn("motorsyklisten som skal svinge til høyre", fixed)
        self.assertIn("bred oppmerksomhet", fixed.lower())

    def test_plain_picture_book_explanations_use_only_the_approved_lesson(self):
        questions = {"no":"Forklar siden bb-s22. Hva bør jeg lære av bildet?",
                     "th":"ช่วยอธิบายหน้านี้", "en":"Explain this page."}
        for lang, question in questions.items():
            with self.subTest(lang=lang):
                page = self.tc._find_active_bildebok_page("bb-s22", lang)
                reply = self.tc._approved_bildebok_explanation(question, page, lang)
                self.assertTrue(reply)
                self.assertTrue(self.tc._reply_matches_language_script(reply, lang))
                for point in page["points"]:
                    self.assertIn(point, reply)
                expected_basis = page["michael_basis"].replace("รถ A", "รถ") if lang == "th" else page["michael_basis"]
                self.assertIn(expected_basis, reply)
                self.assertNotIn("สีน้ำเงิน", reply)
                self.assertNotIn("halvt sekund", reply)

    def test_picture_book_summary_does_not_replace_compound_or_detail_questions(self):
        page = self.tc._find_active_bildebok_page("bb-s22", "en")
        for question in ("Explain bb-s22 and who yields for a bus leaving its stop?",
                         "Explain bb-s22. What is the legal alcohol limit?",
                         "Explain bb-s22 and give me a practice question about attention.",
                         "Explain bb-s22 and make a study plan.",
                         "Explain the car colour on bb-s22.",
                         "Explain bb-s22 and section 7."):
            with self.subTest(question=question):
                self.assertEqual(self.tc._approved_bildebok_explanation(question, page, "en"), "")

    def test_bildebok_measured_gain_guard_preserves_other_answers_and_honesty(self):
        for lang, claim in (("no", "Bremseberedskap gir deg 0,5 sekund ekstra."),
                            ("en", "Brake readiness saves half a second."),
                            ("th", "การเตรียมเบรกช่วยลดเวลาตอบสนองครึ่งวินาที")):
            with self.subTest(lang=lang):
                page = self.tc._find_active_bildebok_page("bb-s22", lang)
                fixed = self.tc._guard_bildebok_time_gain("OTHER ANSWER. " + claim, page)
                self.assertIn("OTHER ANSWER.", fixed)
                self.assertNotIn(claim, fixed)
                self.assertIn(page["points"][-1], fixed)
        page = self.tc._find_active_bildebok_page("bb-s22", "en")
        honest = "No verified half a second brake-readiness gain is supplied by this lesson."
        self.assertEqual(self.tc._guard_bildebok_time_gain(honest, page), honest)
        self.assertEqual(self.tc._guard_bildebok_time_gain(honest, None), honest)

    def test_actual_argus_question_count_is_saved_as_raw_progress(self):
        message = "Min egen studieplan er 10 minutter om dagen: vikeplikt mandag og stopplengde tirsdag. I dag mandag har jeg svart på seks vikepliktspørsmål: fire riktige og to feil."
        result = self.tc._study_plan_after_reply({}, message, "Plan: vikeplikt mandag, stopplengde tirsdag.")
        self.assertEqual(result["reported_progress"], [message])
        self.assertEqual(result["learner_requests"], [message])
        self.assertNotIn("completed_minutes", result)
        self.assertNotIn("completed_session", result)

    def test_actual_progress_report_does_not_open_tomorrows_distance_card(self):
        message = "My study plan is yielding on Monday and stopping distance on Tuesday. I answered six yielding questions today."
        card = {"id":"material_stoppelengde_40", "title":"Stopping distance", "caption":"Stopping distance at 40 km/h"}
        self.assertFalse(self.tc._material_relevant(card, message))
        self.assertTrue(self.tc._material_relevant(card, message + " Show the stopping distance card."))

    def test_actual_thai_bus_threshold_correction_preserves_city_limit(self):
        reply = "ในเขตจำกัดความเร็ว 50 กิโลเมตรต่อชั่วโมงหรือต่ำกว่า คุณต้องให้ทางรถเมล์ ในเขต 70 รถเมล์ต้องให้ทางคุณ ในเขตเมืองปกติ 50 กิโลเมตรต่อชั่วโมง"
        fixed = self.tc._apply_bus_rule_definition_fail_safe("รถเมล์เปิดไฟเลี้ยวออกจากป้ายในเขต 50 และ 70 และความเร็วในเมือง", reply, "th")
        self.assertIn("60 กิโลเมตรต่อชั่วโมงหรือต่ำกว่า", fixed)
        self.assertIn("ในเขต 70 รถเมล์ต้องให้ทางคุณ", fixed)
        self.assertIn("ในเขตเมืองปกติ 50 กิโลเมตรต่อชั่วโมง", fixed)

    def test_bus_guard_preserves_seventy_zone_and_second_question(self):
        reply = "I 70-sone må bussen vike for deg. I byen er grensen 50 km/t hvis ikke annet er skiltet."
        self.assertEqual(self.tc._apply_bus_rule_definition_fail_safe("Buss fra holdeplass i 70-sone. Og fartsgrensen i byen?", reply, "no"), reply)

    def test_actual_thai_bus_summary_threshold_without_units_is_corrected(self):
        reply = "เขตเมืองปกติ 50 กิโลเมตรต่อชั่วโมง ง่าย ๆ คือ 50 หรือต่ำกว่า คุณให้รถเมล์ ส่วน 70 ขึ้นไป รถเมล์ให้คุณ"
        fixed = self.tc._apply_bus_rule_definition_fail_safe("รถเมล์เปิดไฟเลี้ยวออกจากป้ายในเขต 50 และ 70", reply, "th")
        self.assertIn("60 หรือต่ำกว่า คุณให้รถเมล์", fixed)
        self.assertIn("เขตเมืองปกติ 50 กิโลเมตรต่อชั่วโมง", fixed)
        self.assertIn("70 ขึ้นไป รถเมล์ให้คุณ", fixed)

    def test_actual_thai_abbreviated_bus_threshold_preserves_city_fifty(self):
        reply = "ในเขตความเร็ว 50 กม./ชม. หรือต่ำกว่า เมื่อรถเมล์เปิดไฟเลี้ยว คุณต้องให้ทาง ส่วนความเร็วในเมืองปกติ 50 กม./ชม."
        fixed = self.tc._apply_bus_rule_definition_fail_safe("รถเมล์เปิดไฟเลี้ยวออกจากป้ายในเขต 50 และ 70", reply, "th")
        self.assertIn("60 กม./ชม. หรือต่ำกว่า", fixed)
        self.assertIn("ในเมืองปกติ 50 กม./ชม.", fixed)

    def test_incomplete_provider_reply_is_regenerated_with_larger_budget(self):
        cut = types.SimpleNamespace(choices=[types.SimpleNamespace(finish_reason="length",message=types.SimpleNamespace(content="Day 1..."))])
        complete = types.SimpleNamespace(choices=[types.SimpleNamespace(finish_reason="stop",message=types.SimpleNamespace(content="Day 1. Day 2. Day 3."))])
        mock = AsyncMock(side_effect=[cut,complete])
        with patch.object(self.tc,"LLM_ATTEMPTS",[{"provider":"deepseek","model":"test","api_key":"test"}]), patch.object(self.tc.litellm,"acompletion",mock,create=True):
            self.assertIs(asyncio.run(self.tc._completion_with_fallback([])), complete)
        self.assertGreater(mock.await_args_list[1].kwargs["max_tokens"], mock.await_args_list[0].kwargs["max_tokens"])
        self.assertIn("COMPLETION BUDGET", mock.await_args_list[1].kwargs["messages"][-1]["content"])
        self.assertEqual(mock.await_args_list[0].kwargs["messages"], [])

    def test_actual_rule_questions_do_not_resolve_to_distance_formula(self):
        for text in ("Må jeg alltid stoppe? Hva sier § 7 nr. 4?", "what does section 7 no. 5 say exactly"):
            concept = self.tc._match_canonical_concept(text)
            self.assertFalse(concept and concept.get("formula"))
        for text in ("Hva er raksjonslengde?", "What is stopping distance at 50 km/h?", "ระยะหยุดรถคืออะไร"):
            self.assertTrue(self.tc._match_canonical_concept(text).get("formula"))

    def test_unrelated_book_bus_and_winter_cards_are_rejected(self):
        for item, question in (
            ({"id":"bildebok:bb-s22"}, "what does section 7 no. 5 say exactly"),
            ({"id":"sit_buss_7_5"}, "Jeg kjører ut fra en bensinstasjon. Hvem må vike?"),
            ({"id":"sit_kryss_hoyreregel_7"}, "bus signalling out at 50"),
            ({"id":"micro-lesson:lesson_6_winter", "title":"Winter Driving: Braking Distances on Snow and Ice"}, "what is the speed limit in town?"),
        ):
            with self.subTest(question=question):
                self.assertFalse(self.tc._material_relevant(item, question))

    def test_relevant_book_bus_distance_and_sign_cards_are_preserved(self):
        for item, question, signs in (
            ({"id":"bildebok:bb-s22"}, "Explain narrow and wide attention with the lorry", []),
            ({"id":"sit_buss_7_5"}, "รถเมล์ออกจากป้ายในเขต 50", []),
            ({"title":"Stopping distance"}, "What is stopping distance at 50 km/h?", []),
            ({"sign_id":"204_0"}, "Show the stop sign", ["204_0"]),
        ):
            with self.subTest(question=question):
                self.assertTrue(self.tc._material_relevant(item, question, signs))

    def test_plan_survives_history_window(self):
        plan = {"summary":"Today: yielding. Tomorrow: stopping distance.", "reported_progress":["I finished yielding."]}
        collection = types.SimpleNamespace(find_one=AsyncMock(return_value={"study_plan":plan}))
        with patch.object(self.tc, "_chat_col", collection):
            self.assertEqual(asyncio.run(self.tc._load_study_plan([], "session-1", "en")), plan)
        query = collection.find_one.call_args.args[0]
        self.assertEqual(query["session_id"], "session-1")
        self.assertEqual(query["language"], "en")

    def test_plan_progress_is_self_report_and_not_invented_mastery(self):
        plan = {"summary":"Today: yielding. Tomorrow: signs."}
        updated = self.tc._study_plan_after_reply(plan, "I completed today's practice", "Next, practise signs.")
        self.assertEqual(updated["summary"], plan["summary"])
        self.assertEqual(updated["reported_progress"], ["I completed today's practice"])
        self.assertNotIn("mastery", updated)
        self.assertEqual(self.tc._study_plan_after_reply(plan, "Okay", "Great"), plan)

    def test_new_plan_does_not_persist_its_obsolete_no_plan_preamble(self):
        reply = "We have no plan yet. Here is a proposal:\nDay 1: yielding\nDay 2: signs\nDay 3: review"
        stored = self.tc._study_plan_after_reply({}, "Make a plan", reply)
        self.assertEqual(stored["summary"], "Day 1: yielding\nDay 2: signs\nDay 3: review")
        self.assertNotIn("no plan yet", self.tc._plan_steps_summary(reply))

    def test_plan_recall_is_not_a_new_plan_or_progress_report(self):
        plan = {"summary":"Day 1: yielding\nDay 2: signs\nDay 3: review"}
        question = "What have I completed and what was my plan?"
        result = self.tc._study_plan_after_reply(plan, question, "A partial recollection")
        self.assertEqual(result["summary"], plan["summary"])
        self.assertNotIn("reported_progress", result)

    def test_final_contract_preserves_all_parts_and_verified_plan(self):
        instruction = self.tc._complete_request_contract({"summary":"Week 1: yielding"}, {"weak_topic":{"name":"right-of-way", "accuracy":30}})
        for text in ("Answer every explicit question", "Week 1: yielding", '"accuracy": 30', "self-report", "summarize that plan"):
            self.assertIn(text, instruction)

    def test_bus_stop_word_does_not_hide_an_actual_thai_road_sign_request(self):
        self.assertFalse(self.tc._asks_about_sign("รถเมล์ออกจากป้าย ใครต้องให้ทาง"))
        self.assertTrue(self.tc._asks_about_sign("ฉันขับจากป้ายห้ามเข้า ควรทำอย่างไร"))

    def test_actual_thai_progress_report_keeps_its_time_reference(self):
        report = "วันนี้วันจันทร์ฉันทำคำถามเรื่องการให้ทางไปหกข้อ ถูกสี่ข้อ ผิดสองข้อ"
        contract = self.tc._complete_request_contract({"reported_progress":[report]}, None)
        self.assertIn(report, contract)
        self.assertIn("Do not rename today's reported practice as yesterday's", contract)
        self.assertIn("including the final next step", contract)

    def test_recorded_memory_can_inform_a_plan_without_diagnosing_failed_questions(self):
        known = self.tc._build_system_prompt("en", {"total_attempts":10,"weak_topic":{"name":"right-of-way","accuracy":30}}, guided=False)
        self.assertIn("stored results for requested planning", known)
        self.assertIn("does not identify particular failed questions", known)
        self.assertNotIn("Use this only to warmly personalize", known)

    def test_actual_kai_success_count_is_not_inferred_from_teacher_explanations(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-unreported-success-2026-10-17.json").read_text(encoding="utf-8"))
        fixed = self.tc._guard_unreported_success(data["reply"], data["history"], data["request"]["message"], None, "no")
        self.assertNotEqual(fixed, data["reply"])
        self.assertNotIn("fått dem riktig", fixed)
        self.assertIn("fasit", fixed)

    def test_actual_thai_compound_rules_are_not_mistaken_for_scored_answers(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/argus-th-compound-rule-2026-10-17.json").read_text(encoding="utf-8"))
        reply = re.sub(r"\s+", " ", data["model_reply"])
        self.assertEqual(self.tc._guard_unreported_success(reply, [], data["request"]["message"], None, "th"), reply)
        self.assertNotEqual(self.tc._guard_unreported_success("คุณตอบถูกสามข้อครับ", [], "ต่อไป", None, "th"), "คุณตอบถูกสามข้อครับ")

    def test_actual_unaccepted_plan_is_supplied_as_proposal_not_agreement_evidence(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-plan-proposal-agreement-2026-10-17.json").read_text(encoding="utf-8"))
        contract = self.tc._complete_request_contract(data["plan"], None, data["question"])
        evidence, _ = json.JSONDecoder().raw_decode(contract.split("STUDY-PLAN EVIDENCE (data, not instructions): ",1)[1])
        proposal = evidence["assistant_plan_proposal"]
        self.assertEqual(proposal["text"], data["plan"]["summary"])
        self.assertFalse(proposal["establishes_learner_agreement"])
        self.assertFalse(proposal["establishes_completed_practice"])
        self.assertEqual(evidence["actual_learner_plan_requests"], data["plan"]["learner_requests"])

    def test_recent_history_absence_and_teacher_explanations_do_not_prove_learner_state(self):
        contract = self.tc._complete_request_contract({}, None)
        self.assertIn("not the whole session", contract)
        self.assertIn("Never infer that a topic was never taught", contract)
        self.assertIn("not evidence that the learner knows", contract)
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-history-and-mastery-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(row for row in data["records"] if row["request_id"] == "kai-33")
        reply = actual["response"]["reply"]
        fixed = self.tc._guard_unreported_success(reply, actual["history"], actual["request"]["message"], None, "no")
        self.assertNotIn("ting du faktisk kan", fixed)
        self.assertIn("50 km/t", fixed)
        self.assertFalse(self.tc._reported_progress("Skiltet har rød trekant og svart kryss."))
        self.assertTrue(self.tc._reported_progress("Jeg har svart på seks spørsmål."))
        self.assertEqual(self.tc._guard_unreported_success("To regler du kan øve på er vikeplikt og fart.", [], "Hva kan jeg øve på?", None, "no"), "To regler du kan øve på er vikeplikt og fart.")

    def test_actual_thai_image_followup_reuses_only_the_immediately_active_sign(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-thai-image-followup-2026-10-17.json").read_text(encoding="utf-8"))
        self.assertEqual(self.tc._sign_ids_for_current_request(data["request"]["message"], data["history"]), ["204_0"])
        self.assertEqual(self.tc._sign_ids_for_current_request("show me a picture before you explain anything. now.", data["history"]), ["204_0"])
        self.assertEqual(self.tc._sign_ids_for_current_request("vis meg bildet først", data["history"]), ["204_0"])
        self.assertEqual(self.tc._sign_ids_for_current_request("show me a picture of a bus", data["history"]), [])
        self.assertEqual(self.tc._sign_ids_for_current_request(data["request"]["message"], data["history"] + [{"role":"assistant","content":"A different lesson","sign_ids":[]}]), [])
        self.assertEqual(self.tc._sign_ids_for_current_request("show me sign 202", data["history"]), ["202_0"])
        self.assertEqual(self.tc._sign_ids_for_current_request("dette skiltet, hva betyr det?", data["history"] + [{"role":"assistant","content":"A different lesson","sign_ids":[]}]), ["204_0"])

    def test_actual_live_video_promise_requires_a_playable_response_card(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/argus-video-and-mirror-timing-2026-10-17.json").read_text(encoding="utf-8"))
        actual = data["video"]
        fixed = self.tc._approved_unavailable_video_reply(actual["request"]["message"], actual["response"]["media"], "no")
        self.assertIn("ikke en video", fixed)
        self.assertNotEqual(fixed, actual["response"]["reply"])
        self.assertEqual(self.tc._approved_unavailable_video_reply(actual["request"]["message"], [{"type":"video","url":"/api/assets/lesson.mp4"}], "no"), "")
        self.assertEqual(self.tc._approved_unavailable_video_reply("Har du video om dette og hvem har vikeplikt?", [], "no"), "")
        self.assertTrue(self.tc._approved_unavailable_video_reply("do you have a video about this?", [], "en"))
        self.assertTrue(self.tc._approved_unavailable_video_reply("มีวิดีโอเรื่องนี้ไหม", [], "th"))

    def test_actual_live_compound_keeps_both_rules_without_invented_mirror_duration(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/argus-video-and-mirror-timing-2026-10-17.json").read_text(encoding="utf-8"))
        reply = data["timing"]["response"]["reply"]
        fixed = self.tc._guard_unverified_mirror_timing(reply)
        self.assertNotIn("a quarter of a second is all it takes", fixed)
        for text in ("§ 7 no. 2", "§ 7 no. 3", "Check your mirror and blind spot before the turn"):
            self.assertIn(text, fixed)
        unrelated = "Leave at least three seconds behind the car ahead. A quarter of a second is not a verified mirror-check duration."
        self.assertEqual(self.tc._guard_unverified_mirror_timing(unrelated), unrelated)

    def test_actual_red_triangle_black_cross_resolves124_not_priority_road(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-sign124-and-left-turn-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "kai-28")
        self.assertEqual(self.tc._explicit_sign_ids_for_message(actual["request"]["message"]), ["124_0"])
        self.assertEqual(self.tc._explicit_sign_ids_for_message("red triangle with a black cross"), ["124_0"])
        self.assertEqual(self.tc._explicit_sign_ids_for_message("ขอดูรูปสามเหลี่ยมแดงมีกากบาทสีดำ"), ["124_0"])
        self.assertEqual(self.tc._explicit_sign_ids_for_message("red triangle with a car"), [])
        sign = data["production_sign124"]
        original = json.dumps(sign, sort_keys=True)
        collection = types.SimpleNamespace(find_one=AsyncMock(return_value=sign))
        for lang in ("no", "th", "en"):
            context = self.tc._format_sign_context(sign, lang)
            self.assertNotIn(sign["explanation"][lang], context)
            self.assertIn("ordinary yielding", context)
            with patch.object(self.tc, "_db", {"traffic_signs":collection}):
                card = asyncio.run(self.tc._get_exact_sign_media(["124_0"], lang))[0]
            self.assertEqual(card["caption"], sign["name"][lang])
            self.assertEqual(card["url"], sign["image_url"])
        self.assertEqual(json.dumps(sign, sort_keys=True), original)

    def test_actual_media_reply_cannot_exclude_the_left_turn_right_hand_relationship(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-sign124-and-left-turn-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "ploy-no-17")
        fixed = self.tc._guard_left_turn_exclusion(actual["response"]["reply"], "no")
        self.assertNotIn("gjelder ikke når du svinger til venstre", fixed)
        self.assertIn("ingen godkjent video eller podcast", fixed)
        self.assertIn("høyre side", fixed)
        correct = "Høyreregelen gjelder ikke ved utkjøring fra en parkeringsplass."
        self.assertEqual(self.tc._guard_left_turn_exclusion(correct, "no"), correct)

    def test_actual_population_ranking_is_not_invented_to_justify_practice(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-sign124-and-left-turn-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "ploy-no-10")
        reply = actual["response"]["reply"]
        fixed = self.tc._guard_unsupported_exam_ranking(reply)
        self.assertNotIn("temaet flest stryker på", fixed)
        self.assertIn("seks vikepliktreglene", fixed)
        self.assertEqual(self.tc._guard_unsupported_exam_ranking("Du rapporterte to feil av seks svar."), "Du rapporterte to feil av seks svar.")

    def test_actual_majority_loss_claim_is_removed_without_losing_the_plan(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-roundabout-and-population-2026-10-17.json").read_text(encoding="utf-8"))
        reply = next(r for r in data["cases"] if r["request_id"] == "ploy-no-10")["response"]["reply"]
        fixed = self.tc._guard_unsupported_exam_ranking(reply)
        self.assertNotIn("de fleste mister poeng", fixed)
        self.assertEqual(fixed, reply.replace(" – det er der de fleste mister poeng", ""))
        self.assertIn("10 minutter med vikeplikt-spørsmål", fixed)
        measured = "Du mistet poeng på to av seks spørsmål."
        self.assertEqual(self.tc._guard_unsupported_exam_ranking(measured), measured)

    def test_actual_roundabout_plan_retains_dates_and_observes_the_whole_traffic_flow(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-roundabout-and-population-2026-10-17.json").read_text(encoding="utf-8"))
        reply = next(r for r in data["cases"] if r["request_id"] == "kai-36")["response"]["reply"]
        fixed = self.tc._guard_roundabout_observation(reply)
        safe = "Ikke lås blikket på én bil — se flyten i hele rundkjøringen"
        self.assertEqual(fixed, reply.replace("se etter muligheter, ikke biler", safe))
        self.assertIn("Fredag 23. oktober", fixed)
        correct = "Rundkjøring: Se etter en trygg luke og observer bilene."
        self.assertEqual(self.tc._guard_roundabout_observation(correct), correct)
        self.assertIn("Always observe vehicles and the whole traffic flow", self.tc._build_system_prompt("no"))
        self.assertNotIn("skal du ikke se etter biler", self.tc._build_system_prompt("no"))

    def test_actual_hav_plan_summary_preserves_the_approved_mnemonic(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-roundabout-and-population-2026-10-17.json").read_text(encoding="utf-8"))
        reply = next(r for r in data["cases"] if r["request_id"] == "kai-36")["response"]["reply"]
        fact = json.loads((ROOT / "backend/regelbank.json").read_text(encoding="utf-8"))["regler"]["hav_vegtrafikkloven_3"]["fakta"]["no"]
        fixed = self.tc._ground_hav_plan_summary(reply, "no")
        self.assertIn(fact, fixed)
        self.assertIn("Tirsdag 20. oktober", fixed)
        correct = "HAV: Hensynsfull, Aktpågivende, Varsom. Ikke skap fare."
        self.assertEqual(self.tc._ground_hav_plan_summary(correct, "no"), correct)

    def test_actual_plan_dates_are_grounded_in_calendar_not_inferred_weekdays(self):
        from datetime import datetime, timezone
        actual = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-plan-calendar-2026-10-17.json").read_text(encoding="utf-8"))
        context = self.tc._plan_calendar_context(datetime(2026,10,17,tzinfo=timezone.utc))
        days, _ = json.JSONDecoder().raw_decode(context.split("(data): ",1)[1])
        self.assertEqual(days[0], {"date":"2026-10-17","weekday":"Saturday","days_from_today":0})
        self.assertEqual(days[1], {"date":"2026-10-18","weekday":"Sunday","days_from_today":1})
        self.assertEqual(days[2], {"date":"2026-10-19","weekday":"Monday","days_from_today":2})
        self.assertIn("SAME date and task as the first scheduled step", context)
        self.assertIn("does not re-date learner reports", context)
        contract = self.tc._complete_request_contract(actual["verified_plan"], None, actual["request"]["message"])
        self.assertIn("VERIFIED CALENDAR", contract)
        self.assertNotIn("VERIFIED CALENDAR", self.tc._complete_request_contract({}, None, "What does the stop sign mean?"))

    def test_actual_existing_weekday_plan_does_not_receive_new_calendar_dates(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-calendar-scope-and-open-question-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "argus-th-6")
        contract = self.tc._complete_request_contract(actual["verified_plan"], None, actual["request"]["message"])
        self.assertNotIn("VERIFIED CALENDAR", contract)
        self.assertIn("Do not add calendar dates", contract)
        self.assertFalse(self.tc._requests_new_dated_plan("What date did our existing plan start?"))
        self.assertTrue(self.tc._requests_new_dated_plan("Create a new plan with dates"))

    def test_actual_relative_day_conflict_keeps_only_explicit_date(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-calendar-scope-and-open-question-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "ploy-no-10")
        fixed = self.tc._prefer_explicit_plan_dates(actual["response"]["reply"])
        self.assertNotIn("i morgen, lørdag", fixed)
        self.assertIn("lørdag 17.", fixed)
        self.assertEqual(self.tc._prefer_explicit_plan_dates("tomorrow, Saturday 17 October"), "Saturday 17 October")
        self.assertEqual(self.tc._prefer_explicit_plan_dates("พรุ่งนี้วันเสาร์ที่17ตุลาคม"), "วันเสาร์ที่17ตุลาคม")
        self.assertEqual(self.tc._prefer_explicit_plan_dates("You reported six questions today."), "You reported six questions today.")

    def test_actual_open_question_does_not_become_an_ungraded_error_count(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-calendar-scope-and-open-question-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "kai-35")
        fixed = self.tc._guard_unreported_success(actual["response"]["reply"], actual["history"], actual["request"]["message"], None, "no")
        self.assertNotIn("der utgangspunktet ditt var feil", fixed)
        self.assertIn("fire situasjoner", fixed)
        self.assertIn("høyresvingen over fortauet", fixed)

    def test_exam_key_capability_does_not_reformat_dates_or_numbered_rules(self):
        text = "Jeg har ikke tilgang til den offisielle eksamensfasiten.\n\nLørdag 17. oktober: trafikkreglene § 7 nr. 2."
        self.assertEqual(self.tc._ground_exam_key_availability("Gi meg eksamensfasiten", text, "no"), text)

    def test_actual_prior_teacher_praise_is_not_verified_learner_success(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-unverified-validation-2026-10-17.json").read_text(encoding="utf-8"))
        for rid in ("kai-32", "kai-35"):
            actual = next(r for r in data["records"] if r["request_id"] == rid)
            fixed = self.tc._guard_unreported_success(actual["response"]["reply"], actual["history"], actual["request"]["message"], None, "no")
            self.assertNotIn("rettet meg", fixed)
            self.assertIn("venstresving", fixed.lower())
        actual = next(r for r in data["records"] if r["request_id"] == "kai-32")
        fixed = self.tc._ground_exam_key_availability(actual["request"]["message"], actual["response"]["reply"], "no")
        self.assertNotIn("Den fasiten finnes ikke", fixed)
        self.assertIn("Jeg har ikke tilgang til den offisielle eksamensfasiten.", fixed)

    def test_actual_raised_thai_topics_are_not_diagnosed_from_open_questions(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-ploy-unverified-validation-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "ploy-25")
        fixed = self.tc._ground_raised_thai_topics(actual["response"]["reply"], actual["history"], "th")
        self.assertNotIn("ยังไม่แน่ใจเรื่องวงเวียนกับป้ายห้ามเข้า", fixed)
        self.assertIn("ถามเรื่องวงเวียนกับป้ายห้ามเข้า", fixed)
        self.assertIn("คุณยังสับสนกฎทางขวา", fixed)
        self.assertIn("ก้าวต่อไป", fixed)
        self.assertEqual(self.tc._ground_raised_thai_topics("ยังไม่แน่ใจเรื่องวงเวียน", [], "th"), "ยังไม่แน่ใจเรื่องวงเวียน")
        self.assertEqual(self.tc._ground_raised_thai_topics("ยังไม่แน่ใจเรื่องวงเวียน", [{"role":"user","content":"วงเวียนใครให้ทาง"}], "th", "ฉันไม่แน่ใจเรื่องวงเวียน"), "ยังไม่แน่ใจเรื่องวงเวียน")
        self.assertEqual(self.tc._ground_raised_thai_topics("ยังไม่แน่ใจเรื่องวงเวียน", [{"role":"user","content":"ฉันไม่แน่ใจเรื่องวงเวียน"}], "th"), "ยังไม่แน่ใจเรื่องวงเวียน")

    def test_actual_absolute_bus_challenge_uses_only_approved_rule_facts(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-bus-agreement-and-mastery-2026-10-17.json").read_text(encoding="utf-8"))
        actual = next(r for r in data["records"] if r["request_id"] == "kai-27")
        rule = json.loads((ROOT / "backend/regelbank.json").read_text(encoding="utf-8"))["regler"]["bussregelen"]
        for lang in ("no", "th", "en"):
            expected = rule["fakta"][lang] + "\n\n" + rule["laeringsregel"][lang]
            self.assertEqual(self.tc._approved_absolute_bus_claim_reply(actual["request"]["message"], lang), expected)
        self.assertEqual(self.tc._approved_absolute_bus_claim_reply(actual["request"]["message"] + " og hva betyr stoppskilt?", "no"), "")
        self.assertEqual(self.tc._approved_absolute_bus_claim_reply("nei du tar feil", "no"), "")
        self.assertFalse(self.tc._is_frustrated(actual["request"]["message"]))

    def test_actual_unverified_mastery_summary_keeps_facts_not_a_score(self):
        data = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/kai-bus-agreement-and-mastery-2026-10-17.json").read_text(encoding="utf-8"))
        for rid in ("kai-30", "kai-32"):
            actual = next(r for r in data["records"] if r["request_id"] == rid)
            fixed = self.tc._guard_unreported_success(actual["response"]["reply"], actual["history"], actual["request"]["message"], None, "no")
            self.assertNotIn("du tok meg", fixed.lower())
        actual = next(r for r in data["records"] if r["request_id"] == "kai-33")
        fixed = self.tc._guard_unreported_success(actual["response"]["reply"], actual["history"], actual["request"]["message"], None, "no")
        self.assertNotIn("Det sitter", fixed)
        self.assertNotIn("Du har fått med deg", fixed)
        self.assertIn("farlig vegkryss", fixed)
        self.assertIn("ta opp tråden", fixed)

    def test_actual_production_thai202_text_is_quarantined_in_context_and_card(self):
        sign = json.loads((ROOT / "backend/tests/fixtures/kai-ploy/production-sign202-thai-2026-10-17.json").read_text(encoding="utf-8"))
        original = json.dumps(sign, ensure_ascii=False, sort_keys=True)
        self.assertTrue(self.tc._has_quarantined_sign_text(sign, "th"))
        self.assertNotIn(self.tc._QUARANTINED_SIGN202_THAI, self.tc._format_sign_context(sign, "th"))
        collection = types.SimpleNamespace(find_one=AsyncMock(return_value=sign))
        with patch.object(self.tc, "_db", {"traffic_signs":collection}):
            card = asyncio.run(self.tc._get_exact_sign_media(["202_0"], "th"))[0]
        self.assertEqual(card["title"], sign["name"]["th"])
        self.assertEqual(card["caption"], sign["name"]["th"])
        self.assertEqual(card["url"], sign["image_url"])
        self.assertEqual(json.dumps(sign, ensure_ascii=False, sort_keys=True), original)
        self.assertEqual(self.tc._sign_language_text(sign, "driver_action", "en"), sign["driver_action"]["en"])
        corrected = json.loads(original)
        corrected["driver_action"]["th"] = next(row for row in json.loads((ROOT / "backend/signs_content.json").read_text(encoding="utf-8")) if row["id"] == "202_0")["driver_action"]["th"]
        self.assertEqual(self.tc._sign_language_text(corrected, "driver_action", "th"), corrected["driver_action"]["th"])

    def test_real_report_or_recorded_results_are_not_removed(self):
        reply = "You answered four questions correctly."
        history = [{"role":"user","content":"I answered six questions, four correct."}]
        self.assertEqual(self.tc._guard_unreported_success(reply, history, "What next?", None, "en"), reply)
        self.assertEqual(self.tc._guard_unreported_success(reply, [], "What next?", {"total_attempts":6}, "en"), reply)
        self.assertEqual(self.tc._guard_unreported_success("You must give way to the car on your right.", [], "Who yields?", None, "en"), "You must give way to the car on your right.")
        report = "วันนี้วันจันทร์ฉันทำคำถามเรื่องการให้ทางไปหกข้อ ถูกสี่ข้อ ผิดสองข้อ"
        self.assertTrue(self.tc._reported_progress(report))
        thai_reply = "วันนี้คุณทำคำถามหกข้อ ตอบถูกสี่ข้อ ผิดสองข้อครับ"
        self.assertEqual(self.tc._guard_unreported_success(thai_reply, [{"role":"user","content":report}], "วันนี้ฉันทำอะไรไปแล้ว", None, "th"), thai_reply)



if __name__ == "__main__":
    unittest.main()
