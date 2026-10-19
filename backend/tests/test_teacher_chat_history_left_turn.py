"""Offline source regressions; real API/model evidence is recorded separately."""
import ast
import asyncio
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("history_fallback_helpers", Path(__file__).with_name("test_teacher_chat_fallback.py"))
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

class HistoryAndLeftTurnTests(unittest.TestCase):
    def setUp(self):
        self.tc = helpers._load_teacher_chat()

    def test_full_session_history_in_order_including_other_language(self):
        records = [{"session_id":"same", "language":"no" if i == 0 else "th", "role":"user" if i % 2 == 0 else "assistant", "content":str(i), "ts":i//2, "_id":i} for i in range(42)]
        records.append({**records[0], "session_id":"other", "content":"unrelated"})
        class Cursor:
            def __init__(self, query):
                self.rows = [r for r in records if all(r.get(k)==v for k,v in query.items())]
            def sort(self, order):
                for key, direction in reversed(order):
                    self.rows.sort(key=lambda r:r[key], reverse=direction < 0)
                return self
            async def to_list(self, length=None):
                return self.rows[:length] if length is not None else self.rows
        class Collection:
            def find(self, query):
                return Cursor(query)
        with patch.object(self.tc, "_chat_col", Collection()):
            actual = asyncio.run(self.tc._load_session_history("same"))
        self.assertEqual([str(i) for i in range(42)], [row["content"] for row in actual])
        messages = self.tc._history_messages(actual)
        self.assertEqual([{"role":r["role"], "content":r["content"]} for r in actual], messages)

    def test_left_turn_rag_includes_oncoming_and_vulnerable_users_all_languages(self):
        questions = {"no":"Jeg skal svinge til venstre. Hvem viker jeg for?", "th":"ผมจะเลี้ยวซ้าย ต้องให้ทางใครบ้าง", "en":"I am turning left. Who must I yield to?"}
        for lang, question in questions.items():
            with self.subTest(lang=lang):
                context = self.tc._approved_rule_context(question, lang)
                facts = json.JSONDecoder().raw_decode(context[context.index("{"):])[0]
                self.assertIn("venstresving", facts)
                self.assertIn("myke_trafikanter_svinging", facts)
                for key in ("venstresving", "myke_trafikanter_svinging"):
                    self.assertTrue(facts[key]["fakta"])
        context = self.tc._approved_rule_context("Forklar § 7 nr. 2", "no")
        self.assertIn('"venstresving"', context)
        self.assertIn('"myke_trafikanter_svinging"', context)

    def test_every_language_prompt_owns_actual_history_without_false_confession(self):
        for lang in ("no", "th", "en"):
            prompt = self.tc._build_system_prompt(lang, guided=False)
            self.assertIn("SESSION HISTORY ACCOUNTABILITY", prompt)
            self.assertIn("Never blame the learner's memory", prompt)
            self.assertIn("Do not confess to a quotation that is absent", prompt)
            self.assertIn("section 7(3)", prompt)

    def test_rejudge_preserves_recorded_seed_history_and_reconstructs_legacy_only(self):
        path = Path(__file__).parents[1] / "scripts/audit_run.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        main = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "main")
        branch = next(node for node in main.body if isinstance(node, ast.If) and ast.unparse(node.test) == "args.responses")
        seed = [{"role":"assistant", "content":"Documented old error"}]
        rows = [{"request_id":"case-1", "history":list(seed), "request":{"message":"Check your old answer"}, "response":{"reply":"I said that; it was wrong"}},
                {"request_id":"case-2", "request":{"message":"And now?"}, "response":{"reply":"Correct rule"}}]
        from types import SimpleNamespace
        namespace = {"args":SimpleNamespace(responses="unused"), "read_rows":lambda path:rows}
        exec(compile(ast.Module(body=branch.body,type_ignores=[]),str(path),"exec"),namespace)
        self.assertEqual(rows[0]["history"], seed)
        self.assertEqual(rows[1]["history"][0], seed[0])
        self.assertEqual(rows[1]["history"][1]["content"], "Check your old answer")


    def test_actual_production_micro_lesson_is_withheld_from_teacher_response(self):
        fixture = json.loads((Path(__file__).parent / "fixtures/kai-ploy/production-micro-lesson-2-2026-10-19.json").read_text(encoding="utf-8"))
        source = fixture["actual_request_response"]["response"]["media"]
        lesson_spec = importlib.util.spec_from_file_location("actual_micro_lessons",Path(__file__).parents[1] / "micro_lessons.py")
        lessons = importlib.util.module_from_spec(lesson_spec)
        lesson_spec.loader.exec_module(lessons)
        import sys
        with patch.dict(sys.modules, {"micro_lessons":lessons}):
            for lang in ("no", "th", "en"):
                with self.subTest(lang=lang):
                    card = lessons.get_micro_lesson_media_card(lessons.get_micro_lesson_by_id("lesson_2_pedestrians",lang),lang)
                    if lang == "th":
                        self.assertEqual(card, source[0])
                    self.assertEqual([],asyncio.run(self.tc._validate_teacher_response_media([card],lang)))

    def test_actual_micro_context_branch_withholds_only_quarantined_lesson(self):
        import sys
        import logging
        lesson_spec = importlib.util.spec_from_file_location("actual_micro_lessons",Path(__file__).parents[1] / "micro_lessons.py")
        lessons = importlib.util.module_from_spec(lesson_spec)
        lesson_spec.loader.exec_module(lessons)
        tree = ast.parse((Path(__file__).parents[1] / "teacher_chat.py").read_text(encoding="utf-8"))
        fn = next(node for node in tree.body if isinstance(node,ast.AsyncFunctionDef) and node.name == "_get_curriculum_context")
        branch = next(node for node in ast.walk(fn) if isinstance(node,ast.Try) and any(isinstance(child,ast.ImportFrom) and child.module == "micro_lessons" and any(alias.name == "format_micro_lesson_context" for alias in child.names) for child in node.body))
        for lang in ("no","th","en"):
            namespace = {"lang":lang,"clean_msg":"คนเดินเท้าและทางม้าลาย","user_msg":"คนเดินเท้าและทางม้าลาย","context_parts":[],"logger":logging.getLogger(__name__),"_is_quarantined_micro_lesson":self.tc._is_quarantined_micro_lesson}
            with patch.dict(sys.modules, {"micro_lessons":lessons}):
                self.assertEqual(lessons.find_relevant_micro_lesson(namespace["user_msg"],lang)["id"],"lesson_2_pedestrians")
                exec(compile(ast.Module(body=[branch],type_ignores=[]),"teacher_chat.py","exec"),namespace)
            self.assertEqual(namespace["context_parts"],[])
            self.assertFalse(self.tc._is_quarantined_micro_lesson({"id":"lesson_1_right_hand"},lang))

    def test_actual_regulation_exception_does_not_generate_false_correction(self):
        data = json.loads((Path(__file__).parent / "fixtures/kai-ploy/actual-history-left-turn-candidate02-2026-10-19.json").read_text(encoding="utf-8"))
        row = next(r for r in data["records"] if r["request_id"] == "ploy-en-18")
        raw = next(c for c in data["model_calls"] if c["request_id"] == "ploy-en-18")["choices"][0]["message"]["content"]
        self.assertIn("not the right-hand rule",raw)
        self.assertEqual(raw,self.tc._apply_section_7_2_fail_safe(row["request"]["message"],raw,"en"))
        regulated = "When turning left, follow the traffic lights, not the right-hand rule."
        fixed = self.tc._apply_section_7_2_fail_safe("I turn left across oncoming traffic",regulated,"en")
        self.assertNotIn("Correction:",fixed)
        mixed = "Skilt styrer trafikken. Høyreregelen gjelder ikke når du svinger til venstre."
        self.assertIn("Korrigering:", self.tc._apply_section_7_2_fail_safe("Jeg svinger til venstre og møter en bil, hvem viker?", mixed, "no"))
        coordinated = "Skilt styrer trafikken, og du har ikke vikeplikt for møtende."
        self.assertIn("Korrigering:", self.tc._apply_section_7_2_fail_safe("Jeg svinger til venstre foran møtende bil i et kryss uten skilt eller lys. Må jeg vike?", coordinated, "no"))
        implicit = "Skilt styrer trafikken. Du har ikke vikeplikt for møtende."
        self.assertIn("Korrigering:", self.tc._apply_section_7_2_fail_safe("Jeg svinger til venstre foran møtende bil i et kryss uten skilt eller lys. Må jeg vike?", implicit, "no"))
        unsafe = "The right-hand rule does not apply when turning left across oncoming traffic."
        self.assertIn("Correction:", self.tc._apply_section_7_2_fail_safe("I turn left across oncoming traffic", unsafe, "en"))

    def test_actual_priority_alias_fetches_verified_rule_and_corrects_wrong_citation(self):
        data = json.loads((Path(__file__).parent / "fixtures/kai-ploy/actual-history-left-turn-candidate02-2026-10-19.json").read_text(encoding="utf-8"))
        row = next(r for r in data["records"] if r["request_id"] == "ploy-en-16")
        self.assertIn('"hoyreregel"',self.tc._approved_rule_context(row["request"]["message"],"en"))
        fixed = self.tc._ground_right_rule_citation(row["response"]["reply"],"en")
        self.assertIn("(Trafikkreglene § 7 no. 2)",fixed)
        self.assertNotIn("(Trafikkreglene § 7 no. 1)",fixed)
        self.assertEqual("Slowing early is section7 no1.",self.tc._ground_right_rule_citation("Slowing early is section7 no1.","en"))

    def test_actual_live_left_example_does_not_reverse_right_hand_duty(self):
        row = json.loads((Path(__file__).parent / "fixtures/kai-ploy/production-a5fe5b0-left-example-2026-10-19.json").read_text(encoding="utf-8"))
        raw = row["response"]["reply"]
        bad_example = ", when coming from the right in an unmarked junction"
        self.assertIn(bad_example, raw)
        self.assertEqual(raw.replace(bad_example, ""), self.tc._ground_right_rule_citation(raw, "en"))
        valid = "You have priority when coming from the right in an unmarked junction."
        self.assertEqual(valid, self.tc._ground_right_rule_citation(valid, "en"))
        self.assertEqual(raw, self.tc._ground_right_rule_citation(raw, "no"))

    def test_actual_unknown_remaining_time_is_not_inferred(self):
        data = json.loads((Path(__file__).parent / "fixtures/kai-ploy/actual-history-left-turn-candidate02-2026-10-19.json").read_text(encoding="utf-8"))
        row = next(r for r in data["records"] if r["request_id"] == "argus-no-5")
        fixed = self.tc._guard_unsupported_practice_claims(row["response"]["reply"],"no")
        self.assertNotIn("bruker resten av økta",fixed)
        self.assertIn("fortsetter med vikeplikt",fixed)
        self.assertIn("ikke hvor lang tid du brukte",fixed)

if __name__ == "__main__":
    unittest.main()
