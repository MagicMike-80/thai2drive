"""Test-only semantic proposals; no LLM or production feature is enabled."""
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "v6_semantic_policy", Path(__file__).resolve().parents[1] / "michael_v6_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def run_immediate(coro):
    try:
        coro.send(None)
    except StopIteration as done:
        return done.value
    finally:
        coro.close()
    raise AssertionError("Synthetic judge unexpectedly suspended")


def scenario(lang):
    values = {"no": ("Velg blå", "blå", "rød", "Jeg velger blå"),
              "th": ("เลือกสีน้ำเงิน", "สีน้ำเงิน", "สีแดง", "ผมเลือกสีน้ำเงิน"),
              "en": ("Choose blue", "blue", "red", "I choose blue")}[lang]
    question = {"question": {lang: values[0]}, "correctOptionId": "a", "options": [
        {"id": "a", "text": {lang: values[1]}}, {"id": "b", "text": {lang: values[2]}},
    ]}
    return policy.validated_question_content(question, lang), values[3]


class SemanticProposalTest(unittest.TestCase):
    def test_agreement_is_only_a_proposal_for_each_language(self):
        for lang in ("no", "th", "en"):
            validated, answer = scenario(lang)
            calls = []
            async def judge(messages):
                calls.append(messages)
                return json.dumps({"verdict": "correct", "evidence": answer}, ensure_ascii=False)
            with self.subTest(lang=lang):
                self.assertEqual(run_immediate(policy.propose_semantic_assessment(validated, lang, answer, judge)), "correct")
                self.assertEqual(len(calls), 2)
                data = json.loads(calls[0][1]["content"])
                self.assertEqual(data["approved_answer"], validated["correct_text"])
                self.assertEqual(data["student_answer"], answer)

    def test_disagreement_malformed_or_unverifiable_evidence_is_unknown(self):
        validated, answer = scenario("en")
        cases = [
            ['{"verdict":"correct","evidence":"I choose blue"}', '{"verdict":"incorrect","evidence":"I choose blue"}'],
            ['{"verdict":"correct","evidence":"not in learner answer"}'],
            ['{"verdict":"correct","verdict":"incorrect","evidence":"I choose blue"}'],
            ['{"verdict":"correct","evidence":"I choose blue","extra":"x"}'],
            ["not-json"],
        ]
        for results in cases:
            async def judge(messages):
                return results.pop(0)
            with self.subTest(results=list(results)):
                self.assertEqual(run_immediate(policy.propose_semantic_assessment(validated, "en", answer, judge)), "unknown")

    def test_multiple_options_are_unknown_even_when_judge_would_agree(self):
        answers = {"no": "Jeg velger blå eller rød", "th": "เลือกสีน้ำเงินหรือสีแดง", "en": "I choose blue or red"}
        for lang, answer in answers.items():
            validated, _ = scenario(lang)
            calls = []
            async def unreliable_judge(messages):
                calls.append(messages)
                return json.dumps({"verdict": "correct", "evidence": answer}, ensure_ascii=False)
            with self.subTest(language=lang):
                self.assertEqual(run_immediate(policy.propose_semantic_assessment(validated, lang, answer, unreliable_judge)), "unknown")
                self.assertEqual(calls, [])

    def test_missing_context_questions_and_provider_error_fail_closed(self):
        validated, answer = scenario("en")
        async def broken(messages):
            raise RuntimeError("synthetic error")
        self.assertEqual(run_immediate(policy.propose_semantic_assessment(None, "en", answer, broken)), "unknown")
        self.assertEqual(run_immediate(policy.propose_semantic_assessment(validated, "en", answer + "?", broken)), "unknown")
        self.assertEqual(run_immediate(policy.propose_semantic_assessment(validated, "en", answer, broken)), "unknown")


if __name__ == "__main__":
    unittest.main()
