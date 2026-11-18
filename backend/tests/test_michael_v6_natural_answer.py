"""Conservative free-text assessment without services or real learner data."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "v6_policy_natural", Path(__file__).resolve().parents[1] / "michael_v6_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class NaturalAnswerTest(unittest.TestCase):
    def test_supported_languages_and_unambiguous_option_text(self):
        options = {
            "no": ("blå bil", "rød bil", "jeg tror det er "),
            "th": ("รถสีน้ำเงิน", "รถสีแดง", "ผมคิดว่า "),
            "en": ("blue car", "red car", "i think it is "),
        }
        question = {"correctOptionId": "1", "options": [
            {"id": "1", "text": {lang: values[0] for lang, values in options.items()}},
            {"id": "2", "text": {lang: values[1] for lang, values in options.items()}},
        ]}
        for lang, (right, wrong, prefix) in options.items():
            with self.subTest(language=lang):
                self.assertEqual(policy.assess_student_answer(question, lang, prefix + right), "correct")
                self.assertEqual(policy.assess_student_answer(question, lang, prefix + wrong), "incorrect")
                self.assertEqual(policy.assess_student_answer(question, lang, right + " or " + wrong), "unknown")
                self.assertEqual(policy.assess_student_answer(question, lang, "not " + right), "unknown")
                self.assertEqual(policy.assess_student_answer(question, lang, "A"), "unknown")

    def test_ambiguous_or_missing_context_is_unknown(self):
        duplicate = {"correctOptionId": "1", "options": [
            {"id": "1", "text": {"en": "stop"}},
            {"id": "2", "text": {"en": "stop"}},
        ]}
        self.assertEqual(policy.assess_student_answer(duplicate, "en", "i think stop"), "unknown")
        self.assertEqual(policy.assess_student_answer(None, "en", "i think stop"), "unknown")


if __name__ == "__main__":
    unittest.main()
