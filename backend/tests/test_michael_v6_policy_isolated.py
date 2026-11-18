"""Offline policy checks only; does not import the application or its services."""
import importlib.util
from pathlib import Path
import sys
import unittest


def deny_external_operations(event, args):
    if event.startswith(("socket.", "subprocess.", "os.system", "os.spawn")):
        raise RuntimeError("External operations are forbidden in this test")


sys.addaudithook(deny_external_operations)
path = Path(__file__).resolve().parents[1] / "michael_v6_policy.py"
spec = importlib.util.spec_from_file_location("isolated_v6_policy", path)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def run_immediate(coroutine):
    """Run only fake coroutines which never suspend or open an event loop."""
    try:
        coroutine.send(None)
    except StopIteration as done:
        return done.value
    finally:
        coroutine.close()
    raise AssertionError("A synthetic dependency unexpectedly suspended")


def question(lang):
    values = {
        "no": ("Stans", "Kjør"),
        "en": ("Stop", "Drive"),
        "th": ("หยุด", "ขับต่อ"),
    }[lang]
    return {"active": True, "correctOptionId": "A", "options": [
        {"id": "A", "text": {lang: values[0]}},
        {"id": "B", "text": {lang: values[1]}},
    ]}


class PolicyTests(unittest.TestCase):
    def test_six_scenarios_in_each_language(self):
        for lang in ("no", "th", "en"):
            q = question(lang)
            correct = q["options"][0]["text"][lang]
            wrong = q["options"][1]["text"][lang]
            scenarios = (
                (correct, {}, "confirm"),
                (wrong, {}, "hint"),
                ("unrecognised response", {}, "clarify"),
                (wrong, {"needs_explanation": True}, "explain"),
                (wrong, {"answer_requested": True}, "explain"),
                ("", {}, "clarify"),
            )
            for answer, kwargs, expected in scenarios:
                with self.subTest(lang=lang, answer=answer, kwargs=kwargs):
                    self.assertEqual(policy.next_action(policy.assess_exact_answer(q, lang, answer), **kwargs), expected)

    def test_rejects_letters_missing_and_ambiguous_data(self):
        for lang in ("no", "th", "en"):
            q = question(lang)
            self.assertEqual(policy.assess_exact_answer(q, lang, "A"), "unknown")
            q["options"][1]["text"][lang] = q["options"][0]["text"][lang]
            self.assertEqual(policy.assess_exact_answer(q, lang, q["options"][0]["text"][lang]), "unknown")
            self.assertEqual(policy.assess_exact_answer({"active": False}, lang, "anything"), "unknown")

    def test_wrong_then_right_and_repeated_wrong(self):
        for lang in ("no", "th", "en"):
            q = question(lang)
            wrong = q["options"][1]["text"][lang]
            correct = q["options"][0]["text"][lang]
            for _ in range(5):
                self.assertEqual(policy.next_action(policy.assess_exact_answer(q, lang, wrong)), "hint")
            self.assertEqual(policy.next_action(policy.assess_exact_answer(q, lang, correct)), "confirm")

    def test_network_guard_is_active(self):
        import socket
        with self.assertRaises(RuntimeError):
            socket.socket()

    def test_stored_question_lookup_and_legacy_schema(self):
        class Cursor:
            def __init__(self, rows):
                self.rows = rows
            def limit(self, count):
                self.count = count
                return self
            async def to_list(self, count):
                return self.rows[:count]

        class Collection:
            def __init__(self, rows):
                self.rows = rows
                self.query = None
            def find(self, query):
                self.query = query
                return Cursor(self.rows)

        availability = {"id": {"$nin": ["held"]}, "active": {"$ne": False}}
        for lang in ("no", "th", "en"):
            q = question(lang)
            q.update({"id": "synthetic", "question": {lang: "Synthetic"}})
            db = Collection([q])
            answer = q["options"][0]["text"][lang]
            assess = lambda collection, value=answer: run_immediate(
                policy.assess_stored_question(collection, availability, "synthetic", lang, value))
            self.assertEqual(assess(db), "correct")
            self.assertEqual(db.query, {"$and": [availability, {"id": "synthetic"}]})
            self.assertEqual(assess(Collection([q, q])), "unknown")
            self.assertEqual(assess(Collection([])), "unknown")
            self.assertEqual(assess(db, "A"), "unknown")
            legacy = {"id": "synthetic", "correct_answer": "B"}
            for letter, value in zip("abcd", ("one", "two", "three", "four")):
                legacy[f"answer_{letter}_{lang}"] = value
            self.assertEqual(assess(Collection([legacy]), "two"), "correct")
            legacy.pop("correct_answer")
            self.assertEqual(assess(Collection([legacy]), "two"), "unknown")

    def test_lookup_error_fails_closed(self):
        class Broken:
            def find(self, query):
                raise RuntimeError("synthetic failure")
        self.assertEqual(run_immediate(policy.assess_stored_question(
            Broken(), {"active": {"$ne": False}}, "synthetic", "en", "Stop")), "unknown")


if __name__ == "__main__":
    unittest.main(verbosity=2)
