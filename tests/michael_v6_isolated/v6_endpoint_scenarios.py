"""Prepared synthetic endpoint scenarios, not runnable without safe bootstrap.

The caller supplies already-imported, fully isolated modules. This module never
imports the app, loads credentials, or contacts a real service by itself.
"""
import copy
import asyncio
import os
import sys
import types
import unittest
import uuid
from unittest.mock import patch


def synthetic_question():
    return {
        "id": "v6-synthetic-only", "active": True,
        "question": {"no": "Hvilken farge er angitt?", "en": "Which colour is named?",
                     "th": "สีใดที่ระบุไว้?"},
        "options": [
            {"id": "A", "text": {"no": "Blå", "en": "Blue", "th": "สีน้ำเงิน"}},
            {"id": "B", "text": {"no": "Rød", "en": "Red", "th": "สีแดง"}},
            {"id": "C", "text": {"no": "Hvit", "en": "White", "th": "สีขาว"}},
            {"id": "D", "text": {"no": "Svart", "en": "Black", "th": "สีดำ"}},
        ],
        "correctOptionId": "A",
        "explanation": {"no": "Eksempel på forklaring.", "en": "Example explanation.",
                        "th": "ตัวอย่างคำอธิบาย"},
    }


class Cursor:
    def __init__(self, items):
        self.items = items
        self.maximum = None

    def limit(self, maximum):
        self.maximum = maximum
        return self

    async def to_list(self, length):
        return copy.deepcopy(self.items[:min(length, self.maximum)])


class Questions:
    def __init__(self, rows):
        self.rows = rows
        self.queries = []

    def find(self, query):
        self.queries.append(query)
        parts = query.get("$and") if isinstance(query, dict) else None
        if not isinstance(parts, list) or len(parts) != 2:
            raise AssertionError("Availability filter must be conjoined with question id")
        allowed, identifier = parts
        if allowed != {"active": {"$ne": False}, "id": {"$nin": ["v6-held"]}}:
            raise AssertionError("Unexpected synthetic availability filter")
        if set(identifier) != {"id"}:
            raise AssertionError("Unexpected question-id query")
        return Cursor([row for row in self.rows if row.get("id") == identifier["id"]
                       and row.get("active") is not False and row.get("id") != "v6-held"])


class Users:
    def find(self, query, projection):
        if projection != {"_id": 0, "password_hash": 0}:
            raise AssertionError("Unexpected synthetic user projection")
        return Cursor([{"id": query["id"], "synthetic_premium": query["id"] == "synthetic-user"}])


class SyntheticProgress:
    """In-memory test double; it does not prove Mongo atomicity."""
    def __init__(self):
        self.records = {}

    async def record_answer(self, scope, event_id, answer, verdict):
        key = tuple(scope[name] for name in ("principal", "delivery_session", "language", "question_id"))
        record = self.records.setdefault(key, {"level": 0, "events": {}})
        if event_id in record["events"]:
            old_answer, old_level, old_verdict = record["events"][event_id]
            return (old_level, old_verdict) if old_answer == answer else None
        level = record["level"]
        level = min(2, level + 1) if verdict == "incorrect" else 0 if verdict == "correct" else level
        record["level"] = level
        record["events"][event_id] = (answer, level, verdict)
        return level, verdict


def run_suite(tc, policy, mongo_client_class=None):
    """Run synthetic endpoint tests after the separate isolation gate passes."""
    import httpx
    from fastapi import FastAPI

    class EndpointScenarios(unittest.IsolatedAsyncioTestCase):
        async def asyncSetUp(self):
            self.question = synthetic_question()
            self.questions = Questions([copy.deepcopy(self.question)])
            self.server = types.ModuleType("server")
            self.server.AVAILABLE_QUESTION_FILTER = {
                "active": {"$ne": False}, "id": {"$nin": ["v6-held"]}}
            self.server.JWT_SECRET = "synthetic-signing-config"
            self.server.verify_token = lambda credential: (
                {"sub": "synthetic-user"} if credential == "synthetic-bearer" else
                {"sub": "other-user"} if credential == "other-bearer" else None)
            self.server._user_has_active_premium = lambda user: user.get("synthetic_premium") is True
            async def synthetic_usage(user, device):
                return {"synthetic": True}
            self.server._get_access_usage = synthetic_usage
            self.server._access_policy_payload = lambda user, usage: {"can_answer": user.get("synthetic_premium") is True}
            self.env = patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "synthetic-only-key-never-used-in-production",
                "MICHAEL_V6_PROGRESS_KEY": "synthetic-progress-key-never-production", "MICHAEL_V6_ENABLED": "1",
                "MICHAEL_V6_PREMIUM_PILOT": "1"}, clear=True)
            self.env.start()
            self.server_patch = patch.dict(sys.modules, {"server": self.server})
            self.server_patch.start()
            if mongo_client_class is None:
                raise RuntimeError("A verified loopback test MongoDB is required")
            self.mongo = mongo_client_class("mongodb://127.0.0.1:27017/?directConnection=true",
                                            serverSelectionTimeoutMS=3000)
            await self.mongo.admin.command("ping")
            self.collection = self.mongo["michael_v6_synthetic"]["test_" + uuid.uuid4().hex]
            self.db_patch = patch.object(tc, "_db", {"questions": self.questions, "users": Users(),
                                                      "michael_v6_guidance": self.collection})
            self.db_patch.start()
            self.extra_patches = [patch.object(tc, "_v6_access_authorizer", None),
                patch.object(tc, "_v6_text_delivery_authorizer", None),
                patch.object(tc, "_v6_guidance_store", None),
                patch.object(tc, "_v6_semantic_judge", None),
                # The fixture is synthetic; this test does not certify content review.
                patch.object(tc, "_v6_content_ready", lambda *args: True),
                patch.object(policy, "APPROVED_GUIDANCE", {"synthetic-test-only": True})]
            for item in self.extra_patches:
                item.start()
            self.approvals_patch = patch.object(policy, "APPROVED_CONTENT_DIGESTS", {
                self.question["id"]: policy._content_digest(self.question)})
            self.approvals_patch.start()
            self.assertTrue(tc._v6_initialize_premium_pilot())
            self.store = tc._v6_guidance_store
            self.token = policy.issue_delivery_token(self.question)
            self.assertTrue(self.token)
            self.actor_binding = policy.issue_verified_actor_binding(
                self.token, self.question["id"], self.question, "synthetic-user")
            self.assertTrue(self.actor_binding)
            app = FastAPI()
            app.include_router(tc.teacher_router, prefix="/api")
            self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://synthetic.invalid")

        async def asyncTearDown(self):
            await self.client.aclose()
            self.mongo.close()
            self.approvals_patch.stop()
            for item in reversed(self.extra_patches):
                item.stop()
            self.db_patch.stop()
            self.server_patch.stop()
            self.env.stop()

        async def call(self, lang, intent, answer=None, *, bearer="synthetic-bearer", **changes):
            payload = {"session_id": policy.delivery_session_id(self.token, lang), "mode": "v6_quiz_pilot",
                       "message": answer or "synthetic", "language": lang,
                       "v6_question_id": self.question["id"], "v6_delivery_token": self.token,
                       "v6_actor_binding": self.actor_binding, "v6_intent": intent, "v6_answer_text": answer,
                       "v6_event_id": "synthetic-event-default-0001"}
            payload.update(changes)
            headers = {"Authorization": "Bearer " + bearer} if bearer is not None else {}
            response = await self.client.post("/api/teacher/chat", json=payload, headers=headers)
            self.assertEqual(response.status_code, 200)
            return response.json()

        async def test_six_paths_all_languages(self):
            for lang in ("no", "th", "en"):
                right = self.question["options"][0]["text"][lang]
                wrong = self.question["options"][1]["text"][lang]
                with self.subTest(language=lang):
                    delivery = await self.client.post("/api/teacher/v6/text/start", json={"language": lang},
                        headers={"Authorization": "Bearer synthetic-bearer"})
                    self.assertEqual(delivery.status_code, 200)
                    body = delivery.json()
                    self.assertTrue(body["ready"])
                    self.assertEqual(body["question"], self.question["question"][lang])
                    self.token, self.actor_binding = body["delivery_token"], body["actor_binding"]
                    start = await self.call(lang, "start")
                    self.assertCountEqual(start["suggestions"][1:],
                                          [option["text"][lang] for option in self.question["options"]])
                    existing_ids = {row["_id"] async for row in self.collection.find({})}
                    incorrect = await self.call(lang, "answer", wrong)
                    self.assertEqual(incorrect["suggestions"][0]["v6_feedback"], "incorrect")
                    expected_hint = {"no": "prøv et annet alternativ", "en": "try another option",
                                     "th": "ลองดูสถานการณ์อีกครั้ง"}
                    self.assertIn(expected_hint[lang], incorrect["reply"])
                    for _ in range(4):
                        self.assertTrue((await self.call(lang, "answer", wrong))["suggestions"])
                    records = [row async for row in self.collection.find({}) if row["_id"] not in existing_ids]
                    self.assertEqual(len(records), 1)
                    record = records[0]
                    self.assertEqual(len(record["events"]), 1)
                    self.assertEqual(record["level"], 1)
                    correct = await self.call(lang, "answer", right, v6_event_id="synthetic-correct-event-0002")
                    self.assertEqual(correct["suggestions"][0]["v6_feedback"], "correct")
                    confirmation = {"no": "Det er riktig.", "en": "That is correct.", "th": "ถูกต้องครับ"}
                    self.assertEqual(correct["reply"], confirmation[lang])
                    record = await self.collection.find_one({"_id": record["_id"]})
                    self.assertEqual(record["level"], 0)
                    self.assertEqual(len(record["events"]), 2)
                    self.assertEqual(len(correct["suggestions"]), 1)
                    self.assertTrue((await self.call(lang, "hint"))["suggestions"])
                    self.assertTrue((await self.call(lang, "alternative"))["suggestions"])
                    explained = await self.call(lang, "explain")
                    self.assertIn(right, explained["reply"])
                    self.assertIn(self.question["explanation"][lang], explained["reply"])
                    unknown = await self.call(lang, "answer", "ambiguous synthetic response", v6_event_id="synthetic-unknown-event-0003")
                    self.assertTrue(unknown["suggestions"])

        async def test_missing_forged_stale_and_ambiguous_questions_fail_closed(self):
            for lang in ("no", "th", "en"):
                with self.subTest(language=lang):
                    missing = await self.call(lang, "explain", v6_question_id="missing")
                    forged = await self.call(lang, "explain", v6_delivery_token="forged")
                    self.assertEqual(missing["suggestions"][0]["v6_feedback"], "unavailable")
                    self.assertEqual(forged["suggestions"][0]["v6_feedback"], "unavailable")
                    self.assertNotIn(self.question["options"][0]["text"][lang], forged["reply"])
                    old = copy.deepcopy(self.question)
                    self.questions.rows[0]["correctOptionId"] = "B"
                    changed = await self.call(lang, "explain")
                    self.assertEqual(changed["suggestions"][0]["v6_feedback"], "unavailable")
                    self.assertNotIn(old["options"][0]["text"][lang], changed["reply"])
                    self.questions.rows = [copy.deepcopy(old), copy.deepcopy(old)]
                    duplicate = await self.call(lang, "explain")
                    self.assertEqual(duplicate["suggestions"][0]["v6_feedback"], "unavailable")
                    self.questions.rows = [old]

        async def test_unverified_or_different_user_is_denied(self):
            for lang in ("no", "th", "en"):
                for bearer in (None, "invalid-bearer", "other-bearer"):
                    response = await self.call(lang, "explain", bearer=bearer)
                    self.assertEqual(response["suggestions"][0]["v6_feedback"], "unavailable")
                    self.assertNotIn(self.question["options"][0]["text"][lang], response["reply"])
                wrong_session = await self.call(lang, "answer", self.question["options"][0]["text"][lang],
                                                session_id="another-students-session")
                self.assertEqual(wrong_session["suggestions"][0]["v6_feedback"], "unavailable")
            self.assertEqual(await self.collection.count_documents({}), 0)

        async def test_revoked_access_denied_before_delivery_and_after_delivery(self):
            headers = {"Authorization": "Bearer other-bearer"}
            response = await self.client.post("/api/teacher/v6/text/start", json={"language": "no"}, headers=headers)
            self.assertFalse(response.json()["ready"])
            self.server._user_has_active_premium = lambda user: False
            response = await self.call("no", "answer", self.question["options"][0]["text"]["no"])
            self.assertEqual(response["suggestions"][0]["v6_feedback"], "unavailable")
            response = await self.call("no", "explain")
            self.assertEqual(response["suggestions"][0]["v6_feedback"], "unavailable")
            self.assertEqual(await self.collection.count_documents({}), 0)

        async def test_pilot_initialization_fails_closed(self):
            os.environ["MICHAEL_V6_PREMIUM_PILOT"] = "0"
            self.assertFalse(tc._v6_initialize_premium_pilot())
            self.assertIsNone(tc._v6_guidance_store)
            self.assertFalse(tc._v6_globally_ready(policy))
            os.environ["MICHAEL_V6_PREMIUM_PILOT"] = "1"
            os.environ["MICHAEL_V6_PROGRESS_KEY"] = os.environ["MICHAEL_V6_SIGNING_KEY"]
            self.assertFalse(tc._v6_initialize_premium_pilot())
            self.assertIsNone(tc._v6_access_authorizer)

        async def test_atomic_concurrent_retries_and_student_isolation(self):
            scope = {"principal": "synthetic-user", "delivery_session": "synthetic-session",
                     "language": "no", "question_id": "synthetic-question"}
            async def write():
                return await self.store.record_answer(scope, "synthetic-event-concurrent-001", "synthetic", "incorrect")
            results = await asyncio.gather(*(write() for _ in range(12)))
            self.assertEqual(results, [(1, "incorrect")] * 12)
            self.assertIsNone(await self.store.record_answer(scope, "synthetic-event-concurrent-001", "changed", "incorrect"))
            other = dict(scope, principal="another-synthetic-user")
            self.assertEqual(await self.store.record_answer(other, "synthetic-event-concurrent-001", "synthetic", "incorrect"), (1, "incorrect"))
            rows = await self.collection.find({}).to_list(10)
            self.assertEqual(len(rows), 2)
            self.assertEqual([len(row["events"]) for row in rows], [1, 1])
            self.assertEqual(len({row["actor_marker"] for row in rows}), 2)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(EndpointScenarios)
    return unittest.TextTestRunner(verbosity=2).run(suite)
