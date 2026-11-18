"""Local, isolated checks of decisions made from verified quiz outcomes."""
import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "michael_v6_policy", Path(__file__).resolve().parents[1] / "michael_v6_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class GuidanceDecisionTest(unittest.TestCase):
    def test_outcomes_and_verified_repeated_incorrect_answer(self):
        self.assertEqual(policy.next_action("correct", verified_hint_level=2), "confirm")
        self.assertEqual(policy.next_action("incorrect", verified_hint_level=1), "hint")
        self.assertEqual(policy.next_action("incorrect", verified_hint_level=2), "alternative")
        self.assertEqual(policy.next_action("unknown", verified_hint_level=2), "clarify")
        self.assertEqual(policy.next_action("incorrect", answer_requested=True), "explain")
        self.assertEqual(policy.next_action("unknown", needs_explanation=True), "explain")

    def test_invalid_or_absent_level_does_not_raise_or_escalate(self):
        for level in (None, True, "2", -1, 3):
            with self.subTest(level=level):
                self.assertEqual(policy.next_action("incorrect", verified_hint_level=level), "hint")


if __name__ == "__main__":
    unittest.main()
