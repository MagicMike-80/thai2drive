"""Option-specific feedback must be reviewed and bound to an exact item."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "v6_guidance_policy", Path(__file__).resolve().parents[1] / "michael_v6_policy.py"
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ReviewedGuidanceTest(unittest.TestCase):
    def test_reviewed_paraphrases_require_one_complete_version_bound_match(self):
        q = {"correctOptionId": "A", "options": [{"id": "A", "text": {"en": "Blue"}},
                                                 {"id": "B", "text": {"en": "Red"}}]}
        digest = "a" * 64
        groups = {"A": ["The circle is blue"], "B": ["The circle is red"]}
        guidance = {"question_digest": digest, "reviewer": "test", "approval_reference": "synthetic",
                    "reviewed_at": "2026-01-01T00:00:00Z", "reviewed_languages": ["en"],
                    "answer_phrases": {"en": groups}}
        with patch.object(policy, "APPROVED_GUIDANCE", {"item": guidance}), \
             patch.object(policy, "APPROVED_CONTENT_DIGESTS", {"item": digest}):
            def match(answer, version=digest):
                return policy.reviewed_answer_option("item", version, q, "en", answer)
            self.assertEqual(match(" the circle is BLUE "), "A")
            self.assertEqual(match("The circle is red"), "B")
            self.assertIsNone(match("The circle is blue", "b" * 64))
            for text in ("The circle is not blue", "The circle is blue or red", "The circle is blue?"):
                self.assertIsNone(match(text))
            for conflicting in ("THE CIRCLE IS BLUE", "I choose Blue", "Blue"):
                groups["B"] = [conflicting]
                self.assertIsNone(match("The circle is blue"))

    def test_exact_answer_mapping_and_distinct_reviewed_feedback(self):
        q = {"correctOptionId": "a", "options": [
            {"id": "a", "text": {"en": "Blue"}},
            {"id": "b", "text": {"en": "Red"}},
            {"id": "c", "text": {"en": "White"}},
        ]}
        digest = "a" * 64
        approved = {"synthetic": {"question_digest": digest, "reviewer": "synthetic-reviewer",
                    "approval_reference": "synthetic-evidence", "reviewed_at": "2026-01-01T00:00:00Z",
                    "reviewed_languages": ["en"], "confirmation": {"en": "Yes, the named colour is blue."}, "options": {"en": {
            "b": {"hint": "Look at the red choice.", "alternative": "Compare red with the named colour."},
            "c": {"hint": "Look at the white choice.", "alternative": "Compare white with the named colour."},
        }}}}
        with patch.object(policy, "APPROVED_GUIDANCE", approved), patch.object(policy, "APPROVED_CONTENT_DIGESTS", {"synthetic": digest}):
            red = policy.matched_option_id(q, "en", "I think Red")
            white = policy.matched_option_id(q, "en", "White")
            self.assertEqual((red, white), ("b", "c"))
            self.assertIsNone(policy.matched_option_id(q, "en", "maybe red or white"))
            self.assertEqual(policy.reviewed_option_guidance("synthetic", digest, "en", red, 1), "Look at the red choice.")
            self.assertEqual(policy.reviewed_option_guidance("synthetic", digest, "en", white, 1), "Look at the white choice.")
            self.assertEqual(policy.reviewed_option_guidance("synthetic", digest, "en", red, 2), "Compare red with the named colour.")
            self.assertEqual(policy.reviewed_confirmation("synthetic", digest, "en"), "Yes, the named colour is blue.")
            self.assertIsNone(policy.reviewed_confirmation("synthetic", digest, "th"))
            self.assertIsNone(policy.reviewed_confirmation("synthetic", "b" * 64, "en"))
            self.assertIsNone(policy.reviewed_option_guidance("synthetic", "b" * 64, "en", red, 1))
            self.assertIsNone(policy.reviewed_option_guidance("synthetic", digest, "th", red, 1))
            self.assertIsNone(policy.reviewed_option_guidance("synthetic", digest, "en", red, 0))
            approved["synthetic"]["approval_reference"] = ""
            self.assertIsNone(policy.reviewed_option_guidance("synthetic", digest, "en", red, 1))

    def test_duplicate_or_unapproved_data_never_selects_a_hint(self):
        q = {"correctOptionId": "a", "options": [
            {"id": "a", "text": {"en": "Blue"}}, {"id": "b", "text": {"en": "Blue"}},
        ]}
        self.assertIsNone(policy.matched_option_id(q, "en", "Blue"))
        with patch.object(policy, "APPROVED_GUIDANCE", {}):
            self.assertIsNone(policy.reviewed_option_guidance("synthetic", "digest", "en", "b", 1))

    def test_activation_requires_all_languages_and_every_wrong_option(self):
        langs = ("no", "th", "en")
        digest = "a" * 64
        q = {"question": {lang: "synthetic question" for lang in langs}, "correctOptionId": "a", "options": [
            {"id": "a", "text": {lang: "right" for lang in langs}},
            {"id": "b", "text": {lang: "wrong" for lang in langs}},
        ]}
        guidance = {"question_digest": digest, "reviewer": "synthetic",
                    "approval_reference": "synthetic-only", "reviewed_at": "2026-01-01T00:00:00Z",
                    "reviewed_languages": list(langs), "confirmation": {lang: "confirmed" for lang in langs},
                    "options": {lang: {"b": {"hint": "hint", "alternative": "another hint"}} for lang in langs}}
        with patch.object(policy, "APPROVED_CONTENT_DIGESTS", {"synthetic": digest}), patch.object(policy, "APPROVED_GUIDANCE", {"synthetic": guidance}):
            check = lambda value, lang: isinstance(value, str) and value != "foreign"
            self.assertTrue(policy.reviewed_guidance_covers_question("synthetic", digest, q, check))
            del guidance["options"]["th"]["b"]["alternative"]
            self.assertFalse(policy.reviewed_guidance_covers_question("synthetic", digest, q, check))
            guidance["options"]["th"]["b"]["alternative"] = "another hint"
            q["options"][1]["text"]["th"] = "foreign"
            self.assertFalse(policy.reviewed_guidance_covers_question("synthetic", digest, q, check))
            self.assertFalse(policy.reviewed_guidance_covers_question("synthetic", digest, q, None))


if __name__ == "__main__":
    unittest.main()
