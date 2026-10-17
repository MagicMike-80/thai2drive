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
        self.assertIn("TRAFIKKREGLENE § 7 NR. 2", prompts["no"])
        self.assertIn("Du må ALDRI si", prompts["no"])
        self.assertIn("กฎจราจรนอร์เวย์ § 7 ข้อ 2", prompts["th"])
        self.assertIn("ห้ามบอก", prompts["th"])
        self.assertIn("NORWEGIAN TRAFFIC RULES SECTION 7(2)", prompts["en"])
        self.assertIn("NEVER claim", prompts["en"])

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
        self.assertIn("only in Norwegian", calls[0][-1]["content"])

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

    def test_thai_guard_rejects_non_latin_foreign_script(self):
        self.assertFalse(self.tc._reply_matches_language_script("ให้ทาง обычный ครับ", "th"))
        self.assertTrue(self.tc._reply_matches_language_script("ให้ทางก่อนครับ 50", "th"))

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

    def test_bus_guard_preserves_seventy_zone_and_second_question(self):
        reply = "I 70-sone må bussen vike for deg. I byen er grensen 50 km/t hvis ikke annet er skiltet."
        self.assertEqual(self.tc._apply_bus_rule_definition_fail_safe("Buss fra holdeplass i 70-sone. Og fartsgrensen i byen?", reply, "no"), reply)

    def test_incomplete_provider_reply_is_regenerated_with_larger_budget(self):
        cut = types.SimpleNamespace(choices=[types.SimpleNamespace(finish_reason="length",message=types.SimpleNamespace(content="Day 1..."))])
        complete = types.SimpleNamespace(choices=[types.SimpleNamespace(finish_reason="stop",message=types.SimpleNamespace(content="Day 1. Day 2. Day 3."))])
        mock = AsyncMock(side_effect=[cut,complete])
        with patch.object(self.tc,"LLM_ATTEMPTS",[{"provider":"deepseek","model":"test","api_key":"test"}]), patch.object(self.tc.litellm,"acompletion",mock,create=True):
            self.assertIs(asyncio.run(self.tc._completion_with_fallback([])), complete)
        self.assertGreater(mock.await_args_list[1].kwargs["max_tokens"], mock.await_args_list[0].kwargs["max_tokens"])

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

    def test_final_contract_preserves_all_parts_and_verified_plan(self):
        instruction = self.tc._complete_request_contract({"summary":"Week 1: yielding"}, {"weak_topic":{"name":"right-of-way", "accuracy":30}})
        for text in ("Answer every explicit question", "Week 1: yielding", '"accuracy": 30', "self-report", "summarize that plan"):
            self.assertIn(text, instruction)


if __name__ == "__main__":
    unittest.main()
