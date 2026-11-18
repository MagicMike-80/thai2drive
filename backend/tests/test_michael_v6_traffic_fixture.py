"""Test-only Norwegian right-of-way text reviewed by Michael on 2026-11-18.

This is not a production item or an approval of the source item's image,
translations, provenance or publication. The test does not assert an answer
to any image or unspecified real traffic situation.
"""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "v6_traffic_policy", Path(__file__).resolve().parents[1] / "michael_v6_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ReviewedTrafficTextTest(unittest.TestCase):
    def test_reviewed_norwegian_text_and_uncertainty(self):
        question = {
            "id": "test-only-reviewed-right-of-way",
            "question": {"no": "Du nærmer deg et uregulert kryss uten skilt eller oppmerking. En bil kommer fra høyre. Hva betyr det å overholde vikeplikten i denne situasjonen?"},
            "correctOptionId": "B",
            "options": [
                {"id": "A", "text": {"no": "Blinke med lysene for å vise at du vil kjøre først"}},
                {"id": "B", "text": {"no": "Senke farten og være klar til å stoppe helt slik at bilen fra høyre kan passere først"}},
                {"id": "C", "text": {"no": "Øke farten for å rekke gjennom krysset før den andre bilen"}},
                {"id": "D", "text": {"no": "Stoppe og vente til den andre bilisten vinker deg frem"}},
            ],
        }
        for option in question["options"]:
            verdict = policy.assess_student_answer(question, "no", option["text"]["no"])
            self.assertEqual(verdict, "correct" if option["id"] == "B" else "incorrect")
        self.assertEqual(policy.assess_student_answer(question, "no", "Jeg tror jeg må slippe bilen forbi"), "unknown")
        self.assertEqual(policy.assess_student_answer(question, "no", "B"), "unknown")
        self.assertEqual(policy.next_action("incorrect", verified_hint_level=2), "alternative")
        self.assertEqual(policy.next_action("unknown", verified_hint_level=2), "clarify")


if __name__ == "__main__":
    unittest.main()
