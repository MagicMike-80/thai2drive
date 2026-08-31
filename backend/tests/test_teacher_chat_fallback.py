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
            "202_0": ("Forklar vikepliktskiltet", "Explain the give way sign", "อธิบายป้ายให้ทาง"),
            "204_0": ("Forklar stoppskiltet", "Explain the stop sign", "อธิบายป้ายหยุด"),
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
        self.assertIn("sign_ids = (explicit_sign_ids or _sign_ids_from_context(context_str))[:1]", source)

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

    def test_endpoint_contract_has_no_reply_menu_and_only_one_sign_media(self):
        source = (Path(__file__).resolve().parents[1] / "teacher_chat.py").read_text(encoding="utf-8")
        self.assertIn("system_prompt += _concise_output_instruction(lang)", source)
        self.assertIn("suggestions = []", source)
        self.assertIn(")[:1]", source)
        self.assertIn('if item.get("type") == "sign"', source)


if __name__ == "__main__":
    unittest.main()
