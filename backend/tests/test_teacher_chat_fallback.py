import asyncio
import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path


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

    def test_text_matched_sign_is_prioritized_before_general_resources(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("context_parts.insert(0, _format_sign_context(sign, lang))", source)

    def test_explicit_sign_aliases_resolve_in_each_supported_language(self):
        cases = {
            "202_0": ("Forklar vikepliktskiltet", "Explain the give way sign", "อธิบายป้ายให้ทาง", "Vis skilt 202"),
            "204_0": ("Forklar stoppskiltet", "Explain the stop sign", "อธิบายป้ายหยุด", "Vis skilt 204"),
            "208_0": ("Forklar forkjørsvei", "Explain the priority road", "อธิบายถนนสายหลัก"),
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
                "Når du skal svinge til venstre",
            ),
            (
                "th",
                "เมื่อเลี้ยวซ้ายและต้องให้ทางรถสวนทาง นี่คือกฎการให้ทางจากขวาใช่ไหม",
                "ไม่ใช่กฎมือขวา",
                "เมื่อคุณจะเลี้ยวซ้าย",
            ),
            (
                "en",
                "When turning left for oncoming traffic, is this the right-hand rule?",
                "No, this is not the right-hand rule.",
                "When you are turning left",
            ),
        )
        for lang, question, wrong_reply, expected_start in cases:
            with self.subTest(lang=lang):
                corrected = self.module._apply_section_7_2_fail_safe(question, wrong_reply, lang)
                self.assertTrue(corrected.startswith(expected_start))
                self.assertNotIn("Nei", corrected)
                self.assertNotIn("No,", corrected)
                self.assertNotIn("ไม่ใช่", corrected)

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
                self.assertIn("tjeneren", corrected)
                self.assertIn("kongen", corrected)

    def test_section_7_2_full_citation_contains_both_sentences_and_no_sign(self):
        question = "Hva sier paragraf 7 andre ledd?"
        reply = self.module._apply_section_7_2_fail_safe(question, "Feil modelltekst", "no")
        self.assertIn("Kjørende har vikeplikt for kjøretøy som kommer fra høyre.", reply)
        self.assertIn(
            "Det samme gjelder når kjørende som vil svinge til venstre, vil få kjøretøy på sin høyre side.",
            reply,
        )
        sign_ids = self.module._strict_response_sign_ids(
            self.module._explicit_sign_ids_for_message(question),
            self.module._sign_ids_from_reply(reply),
        )
        self.assertEqual(sign_ids, [])

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

    def test_explicit_sign_skips_broader_sign_search(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("if len(matched_sign_ids) < 2 and not explicit_sign_ids:", source)

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
        self.assertIn("system_prompt += _concise_output_instruction(lang)", source)
        self.assertIn("suggestions = []", source)
        self.assertIn("reply_sign_ids = _sign_ids_from_reply(reply_text)", source)
        self.assertIn("][:2]", source)
        self.assertIn('if item.get("type") == "sign"', source)

    def test_new_session_primer_is_language_pure(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn('_primer = {"no": "Klart 😊", "th": "โอเคครับ 😊", "en": "Sure 😊"}', source)
        self.assertIn('_primer.get(lang, _primer["en"])', source)
        self.assertNotIn('"no": "โอเค ครับ 😊"', source)


if __name__ == "__main__":
    unittest.main()
