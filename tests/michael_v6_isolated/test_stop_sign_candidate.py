"""Test-only version binding; no approval or production services are involved."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("v6_stop_policy", ROOT / "backend/michael_v6_policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
FIXTURE = Path(__file__).with_name("stop_sign_candidate_v1.json")
DIGEST = "b8cf89e2042c5deb7557078be09240ab5c60c46f35b49ec360f4dabf7e40d5ba"


class StopSignCandidateTest(unittest.TestCase):
    def test_version_answer_binding_and_no_cross_actor_access(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(fixture["status"], "test_only_thai_review_pending")
        q = fixture["question"]
        self.assertEqual(policy._content_digest(q), DIGEST)
        self.assertEqual(q["correctOptionId"], "B")
        for lang in ("no", "th", "en"):
            for option in q["options"]:
                self.assertEqual(policy.assess_exact_answer(q, lang, option["text"][lang]),
                                 "correct" if option["id"] == "B" else "incorrect")
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "test-signing-key-not-for-production-0001"}, clear=True):
            self.assertIsNone(policy.issue_delivery_token(q))
            # The allowlist exists solely in this test process, not in application configuration.
            with patch.dict(policy.APPROVED_CONTENT_DIGESTS, {q["id"]: DIGEST}, clear=True):
                token = policy.issue_delivery_token(q)
                self.assertTrue(policy.verify_delivery_token(token, q["id"], q))
                binding = policy.issue_verified_actor_binding(token, q["id"], q, "synthetic-alice")
                self.assertTrue(policy.verify_actor_binding(binding, token, "synthetic-alice"))
                self.assertFalse(policy.verify_actor_binding(binding, token, "synthetic-bob"))
                for lang in ("no", "th", "en"):
                    modified = copy.deepcopy(q)
                    modified["options"][1]["text"][lang] += " changed"
                    self.assertFalse(policy.verify_delivery_token(token, q["id"], modified))
                self.assertFalse(policy.verify_delivery_token(token, "another-id", q))
        self.assertNotIn(q["id"], policy.APPROVED_CONTENT_DIGESTS)


if __name__ == "__main__":
    unittest.main()
