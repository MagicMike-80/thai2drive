"""Synthetic component composition, not a Mongo or full application test."""
import importlib.util
import json
import os
from pathlib import Path
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


component = load("v6_component_test", ROOT / "tests/michael_v6_isolated/test_v6_session_access.py")
storage = load("v6_storage_test", ROOT / "backend/tests/test_michael_v6_progress_store.py")


class CandidateGuidanceTest(unittest.TestCase):
    def test_delivery_actor_and_idempotent_progress_in_all_languages(self):
        question = json.loads(Path(__file__).with_name("stop_sign_candidate_v1.json").read_text(encoding="utf-8"))["question"]
        policy = component.policy
        collection = storage.FakeCollection()
        store = policy.MongoGuidanceStore(collection)
        async def allow(user, request, session):
            return True
        settings = {"MICHAEL_V6_SIGNING_KEY": "synthetic-signing-key-for-test-123456",
                    "MICHAEL_V6_PROGRESS_KEY": "synthetic-progress-key-for-test-12345"}
        with patch.dict(os.environ, settings, clear=True), \
             patch.dict(policy.APPROVED_CONTENT_DIGESTS, {question["id"]: policy._content_digest(question)}, clear=True), \
             patch.dict(component.namespace, {"_v6_access_authorizer": allow,
                        "_v6_guidance_store": store, "_v6_semantic_judge": None}):
            component.collection.rows = [question]
            token = policy.issue_delivery_token(question)
            binding = policy.issue_verified_actor_binding(token, question["id"], question, "synthetic-user")
            other_binding = policy.issue_verified_actor_binding(token, question["id"], question, "other-user")
            for lang in ("no", "th", "en"):
                session = policy.delivery_session_id(token, lang)
                req = types.SimpleNamespace(v6_question_id=question["id"], v6_delivery_token=token,
                    language=lang, v6_actor_binding=binding, v6_intent="answer", v6_hint_level=2,
                    v6_event_id="synthetic-wrong-event-0001", v6_answer_text=question["options"][0]["text"][lang],
                    message="synthetic")
                def invoke():
                    return component.run_immediate(component.namespace["_v6_quiz_pilot"](req, session, object()))
                self.assertEqual(invoke().suggestions[0]["v6_feedback"], "incorrect")
                self.assertEqual(invoke().suggestions[0]["v6_feedback"], "incorrect")
                req.v6_actor_binding = other_binding
                self.assertEqual(invoke().suggestions[0]["v6_feedback"], "unavailable")
                req.v6_actor_binding = binding
                req.v6_event_id = "synthetic-correct-event-0002"
                req.v6_answer_text = question["options"][1]["text"][lang]
                self.assertEqual(invoke().suggestions[0]["v6_feedback"], "correct")
            self.assertEqual(len(collection.records), 3)
            for record in collection.records.values():
                self.assertEqual(len(record["events"]), 2)
                self.assertEqual(record["level"], 0)


if __name__ == "__main__":
    unittest.main()
