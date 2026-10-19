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


if __name__ == "__main__":
    unittest.main()
