"""Rule bank (trafikkreglene § 7) — offline, no LLM, no BASE_URL."""
import json
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.tests.test_teacher_chat_fallback import _load_teacher_chat

tc = _load_teacher_chat()


class RulebankTests(unittest.TestCase):
    def test_file_loads_with_all_s7_rules(self):
        data = json.loads((BACKEND_DIR / "regelbank.json").read_text(encoding="utf-8"))
        for key in tc._RULEBANK_S7_KEYS:
            for lang in ("no", "th", "en"):
                self.assertTrue(data["regler"][key]["fakta"][lang], (key, lang))

    def test_prompt_contains_all_rules_and_not_old_ban(self):
        for lang in ("no", "th", "en"):
            prompt = tc._build_system_prompt(lang)
            for key in tc._RULEBANK_S7_KEYS:
                self.assertIn(tc._RULEBANK["regler"][key]["fakta"][lang], prompt)
            self.assertNotIn("Ikke påstå at møtende trafikk", prompt)

    def test_left_turn_correct_answer_passes_guard(self):
        ok = "Når du svinger til venstre, får du den møtende bilen på din høyre side, så du har vikeplikt."
        self.assertEqual(tc._rulebank_violations(ok, "no"), [])

    def test_oncoming_priority_claim_is_caught(self):
        bad = "Når du svinger til venstre, har møtende vikeplikt for deg."
        self.assertTrue(tc._rulebank_violations(bad, "no"))

    def test_speed_limit_30_default_is_caught(self):
        examples = {
            "no": ("I boligområde er fartsgrensen 30 km/t.", "30 km/t er vanlig i boligområde."),
            "th": ("ย่านที่พัก ความเร็วคือ 30 กม./ชม.", "30 กม./ชม. เป็นความเร็วทั่วไป"),
            "en": ("In a residential area the limit is 30 km/h.", "30 km/h is the default limit."),
        }
        for lang, replies in examples.items():
            for reply in replies:
                with self.subTest(lang=lang, reply=reply):
                    self.assertTrue(tc._rulebank_violations(reply, lang))

    def test_speed_patterns_do_not_reject_approved_facts(self):
        for lang in ("no", "th", "en"):
            reply = tc._RULEBANK["regler"]["fartsgrense_tettbygd"]["fakta"][lang]
            with self.subTest(lang=lang):
                self.assertEqual(tc._rulebank_violations(reply, lang), [])

    def test_bus_learning_rule_is_not_presented_as_law(self):
        bus = tc._RULEBANK["regler"]["bussregelen"]
        for lang in ("no", "th", "en"):
            self.assertNotIn("70", bus["fakta"][lang])           # law text never mentions 70
            self.assertIn("70", bus["laeringsregel"][lang])      # learning rule does

    def test_master_context_keeps_bus_rule_with_correct_number(self):
        ctx = tc._master_document_context()
        self.assertIn("Bussregelen", ctx)          # no longer filtered out
        self.assertIn("§7 nr. 5", ctx)             # bus rule is nr. 5 (fixed in master docs 2026-10-10)
        self.assertNotIn("bussregel (§7 nr. 4)", ctx)

    def test_prompt_contains_s7_nr4_text_from_rulebank(self):
        self.assertIn("bensinstasjon", tc._build_system_prompt("no").lower())

    def test_missing_rulebank_is_fail_soft(self):
        from unittest import mock
        with mock.patch.object(Path, "read_text", side_effect=OSError("missing")):
            data = tc._load_rulebank()
        self.assertEqual(data["regler"], {})
        self.assertEqual(tc._rulebank_prompt("no") != "", bool(tc._RULEBANK["regler"]))


    def test_invalid_rulebank_is_fail_soft(self):
        for content in ("{", "[]", '{"regler": []}', '{"regler": {"bad": {}}, "forbudte_pastander": {}}'):
            with self.subTest(content=content), patch.object(Path, "read_text", return_value=content):
                self.assertEqual(tc._load_rulebank(), {"regler": {}, "forbudte_pastander": {}})

    def test_unavailable_bank_has_empty_prompt(self):
        with patch.object(tc, "_RULEBANK", {"regler": {}, "forbudte_pastander": {}}):
            self.assertEqual(tc._rulebank_prompt("no"), "")

    def test_unknown_language_has_no_visible_fallback(self):
        self.assertEqual(tc._rulebank_prompt("xx"), "")
        self.assertEqual(tc._rulebank_safe_reply("venstresving", "xx"), "")

    def test_invalid_regex_does_not_crash(self):
        with patch.object(tc, "_RULEBANK", {"forbudte_pastander": {"no": ["["]}}):
            self.assertEqual(tc._rulebank_violations("test", "no"), [])

    def test_guard_keeps_valid_reply_without_llm_call(self):
        with patch.object(tc, "_completion_with_fallback", new_callable=AsyncMock) as llm:
            reply = asyncio.run(tc._guard_rule_claims("Du har vikeplikt.", [], "venstresving", "no"))
            self.assertEqual(reply, "Du har vikeplikt.")
            llm.assert_not_awaited()

    def test_guard_retries_once_then_uses_approved_fact(self):
        bad = "Når du svinger til venstre, har møtende vikeplikt for deg."
        for retry in (bad, "Du har vikeplikt for møtende.", RuntimeError("offline")):
            with self.subTest(retry=retry):
                llm = AsyncMock(side_effect=retry) if isinstance(retry, Exception) else AsyncMock(
                    return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=retry))]))
                messages = [{"role": "system", "content": tc._rulebank_prompt("no")}]
                with patch.object(tc, "_completion_with_fallback", llm):
                    reply = asyncio.run(tc._guard_rule_claims(bad, messages, "venstresving", "no"))
                llm.assert_awaited_once()
                expected = retry if retry == "Du har vikeplikt for møtende." else tc._RULEBANK["regler"]["venstresving"]["fakta"]["no"]
                self.assertEqual(reply, expected)
                self.assertEqual(len(messages), 1)

    def test_final_left_turn_fallback_uses_ssot(self):
        for lang in ("no", "th", "en"):
            self.assertEqual(tc._apply_section_7_2_fail_safe("Do I yield to oncoming traffic when turning left?", "bad", lang),
                             tc._RULEBANK["regler"]["venstresving"]["fakta"][lang])

    def test_teaching_tool_definitions_resolve_offline(self):
        for lang in ("no", "th", "en"):
            for query in ("kongen og tjeneren", "HAV"):
                result = asyncio.run(tc.resolve_traffic_concept(query, lang, db=None))
                self.assertTrue(result["definition"], (query, lang))

    def test_guard_is_connected_before_empty_response_check(self):
        import inspect
        source = inspect.getsource(tc.teacher_chat)
        self.assertLess(source.index("await _guard_rule_claims(reply_text, messages, user_msg, lang)"),
                        source.index('error_str = "LiteLLM: empty response"'))


if __name__ == "__main__":
    unittest.main()
