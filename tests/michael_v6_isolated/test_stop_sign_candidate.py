"""Test-only version binding; no approval or production services are involved."""
import copy
import hashlib
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

    def test_owner_approved_guidance_versions_2026_11_20(self):
        """Pins the guidance text approved on 2026-11-20. The V6 content digest
        covers only the question, so guidance is pinned here separately."""
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        guidance = fixture["guidance_draft"]
        self.assertEqual(guidance["question_digest"], DIGEST)
        self.assertEqual(guidance["options"]["en"]["C"]["alternative"],
                         "Imagine the situation from the perspective of the driver approaching from the left. If that driver has to brake because you pull out, have you given way to that vehicle?")

        def digest(value):
            raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            return hashlib.sha256(raw).hexdigest()

        expected = {
            "no": "0fd141cf3501854279e2f9a0f62f783cd6ea66b6f5fcd2ed0e80d92f3be0f4bf",
            "th": "8de587f96ef73b57dd192e47331f7c2112f746af0f7132e67e53fb582e7cbbd8",
            "en": "5a21862a8c2727be964a25567989d806e14f6a7ffbee82aaffb07df46b8d78fc"
}
        for lang, want in expected.items():
            part = {"prompts": guidance["prompts"][lang], "options": guidance["options"][lang],
                    "confirmation": guidance["confirmation"][lang]}
            self.assertEqual(digest(part), want, lang)
        self.assertEqual(digest(guidance), "7c5d8bcbbcb13dc97856e45394d8249b23499c74bc10a4520a4821c9212291a0")

    def test_registered_version_loses_approval_on_content_or_guidance_change(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        q, guidance = policy._read_stop_sign()
        self.assertEqual(dict(q, id=fixture["question"]["id"]), fixture["question"])
        self.assertEqual(policy.APPROVED_CONTENT_DIGESTS[q["id"]], policy._content_digest(q))
        with patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY":"isolated-owner-review-test-only-12345"}, clear=True):
            token = policy.issue_delivery_token(q)
            self.assertTrue(token)
            for lang in ("no", "th", "en"):
                altered = copy.deepcopy(q)
                altered["explanation"][lang] += "!"
                self.assertFalse(policy.verify_delivery_token(token, q["id"], altered))
                for field in ("prompts", "options", "confirmation"):
                    altered = copy.deepcopy(guidance)
                    if field == "prompts":
                        altered[field][lang]["hint"] += "!"
                    elif field == "options":
                        altered[field][lang]["C"]["alternative"] += "!"
                    else:
                        altered[field][lang] += "!"
                    with patch.dict(policy.APPROVED_GUIDANCE, {q["id"]:altered}):
                        self.assertIsNone(policy.issue_delivery_token(q))
                        self.assertFalse(policy.verify_delivery_token(token, q["id"], q))


if __name__ == "__main__":
    unittest.main()
