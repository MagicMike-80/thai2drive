"""Prepared synthetic endpoint scenarios, not runnable without safe bootstrap.

The caller supplies already-imported, fully isolated modules. This module never
imports the app, loads credentials, or contacts a real service by itself.
"""
import copy
import ast
import asyncio
import json
import os
from pathlib import Path
import sys
import types
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo
import secrets
from unittest.mock import patch


def synthetic_question():
    return {
        "id": "v6-synthetic-only", "active": True,
        "question": {"no": "Du ser en blå sirkel. Hvilken farge har sirkelen?",
                     "en": "You see a blue circle. What colour is the circle?",
                     "th": "คุณเห็นวงกลมสีน้ำเงิน วงกลมนี้มีสีอะไร?"},
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


def run_suite(tc, policy, mongo_client_class=None):
    """Run synthetic endpoint tests after the separate isolation gate passes."""
    import httpx
    import jwt
    from fastapi import APIRouter, Depends, FastAPI, HTTPException
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from backend.webapp import webapp_router

    # Execute the exact checked-out auth and policy handlers with their FastAPI
    # decorators. Leave unrelated server startup integrations outside this gate.
    server_path = Path(__file__).resolve().parents[2] / "backend/server.py"
    names = {"create_token", "verify_token", "get_current_user", "get_me", "_auth_user_payload",
             "_access_expires_at", "_user_trial_days_left", "_user_premium_status", "_paid_premium_active",
             "_user_has_active_trial", "_parse_iso_utc", "_user_has_active_premium", "_get_access_usage",
             "_access_scope", "_oslo_day_key", "_access_policy_payload"}
    nodes = [node for node in ast.parse(server_path.read_bytes()).body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    if {node.name for node in nodes} != names or len(nodes) != len(names):
        raise RuntimeError("Cannot load unique auth and access handlers from server.py")
    auth_code = compile(ast.Module(body=nodes, type_ignores=[]), str(server_path), "exec")

    class EndpointScenarios(unittest.IsolatedAsyncioTestCase):
        async def asyncSetUp(self):
            self.question = synthetic_question()
            self.server = types.ModuleType("server")
            self.server.AVAILABLE_QUESTION_FILTER = {
                "active": {"$ne": False}, "id": {"$nin": ["v6-held"]}}
            self.server.__dict__.update(jwt=jwt, JWT_SECRET=secrets.token_hex(32), JWT_ALGORITHM="HS256",
                JWT_EXPIRE_HOURS=1, ACCESS_OSLO_TZ=ZoneInfo("Europe/Oslo"),
                ACCESS_GUEST_TOTAL_LIMIT=5, ACCESS_REGISTERED_DAILY_LIMIT=10,
                datetime=datetime, timezone=timezone, timedelta=timedelta, Optional=Optional,
                HTTPAuthorizationCredentials=HTTPAuthorizationCredentials, HTTPException=HTTPException,
                Depends=Depends, security=HTTPBearer(auto_error=False), api_router=APIRouter())
            exec(auth_code, self.server.__dict__)
            self.bearer = self.server.create_token("synthetic-user", "student@example.invalid")
            self.other_bearer = self.server.create_token("other-user", "other@example.invalid")
            self.headers = {"Authorization": "Bearer " + self.bearer}
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
            test_db = self.mongo["michael_v6_synthetic_" + uuid.uuid4().hex]
            self.server.db = test_db
            self.questions = test_db.questions
            self.users = test_db.users
            self.collection = test_db.michael_v6_guidance
            await self.questions.insert_one(dict(self.question))
            await self.users.insert_many([{"id": "synthetic-user", "email": "student@example.invalid", "is_premium": True},
                                          {"id": "other-user", "email": "other@example.invalid", "is_premium": True}])
            self.db_patch = patch.object(tc, "_db", test_db)
            self.db_patch.start()
            self.confirmation = {"no": "Riktig, svaret er blått.", "en": "Correct, the answer is blue.",
                                 "th": "ถูกต้องครับ คำตอบคือสีน้ำเงิน"}
            self.hints = {"no": "Se på fargen som er nevnt i oppgaven.",
                          "en": "Look at the colour named in the question.",
                          "th": "ลองดูสีที่ระบุไว้ในโจทย์ครับ"}
            self.alternatives = {"no": "Sammenlign fargene en om gangen.",
                                 "en": "Compare the colours one by one.",
                                 "th": "ลองเปรียบเทียบสีทีละตัวเลือกครับ"}
            self.right_phrases = {"no": "Sirkelen er blå", "en": "The circle is blue", "th": "วงกลมนี้เป็นสีน้ำเงิน"}
            self.wrong_phrases = {"no": "Sirkelen er rød", "en": "The circle is red", "th": "วงกลมนี้เป็นสีแดง"}
            self.first_prompt = {"no": "Hvilket ord beskriver sirkelen i første setning?",
                                 "en": "Which word describes the circle in the first sentence?",
                                 "th": "คำใดในประโยคแรกบอกสีของวงกลม?"}
            guidance = {"question_digest": policy._content_digest(self.question), "reviewer": "synthetic-test-only",
                "approval_reference": "synthetic-test-only", "reviewed_at": "2026-01-01T00:00:00Z",
                "reviewed_languages": ["no", "th", "en"], "confirmation": self.confirmation,
                "answer_phrases": {lang: {"A": [self.right_phrases[lang]], "B": [self.wrong_phrases[lang]]}
                                   for lang in self.confirmation},
                "prompts": {lang: {"hint": self.first_prompt[lang], "alternative": self.alternatives[lang]}
                            for lang in self.confirmation},
                "options": {lang: {option["id"]: {"hint": self.hints[lang], "alternative": self.alternatives[lang]}
                                   for option in self.question["options"] if option["id"] != self.question["correctOptionId"]}
                            for lang in ("no", "th", "en")}}
            self.extra_patches = [patch.object(tc, "_v6_access_authorizer", None),
                patch.object(tc, "_v6_text_delivery_authorizer", None),
                patch.object(tc, "_v6_guidance_store", None),
                patch.object(tc, "_v6_semantic_judge", None),
                # The review record is synthetic; no actual content is approved.
                patch.object(policy, "APPROVED_GUIDANCE", {self.question["id"]: guidance})]
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
            app.include_router(webapp_router)
            app.include_router(self.server.api_router, prefix="/api")
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

        async def call(self, lang, intent, answer=None, *, bearer="current-student", **changes):
            payload = {"session_id": policy.delivery_session_id(self.token, lang), "mode": "v6_quiz_pilot",
                       "message": answer or "synthetic", "language": lang,
                       "v6_question_id": self.question["id"], "v6_delivery_token": self.token,
                       "v6_actor_binding": self.actor_binding, "v6_intent": intent, "v6_answer_text": answer,
                       "v6_event_id": "synthetic-event-default-0001"}
            payload.update(changes)
            headers = self.headers if bearer == "current-student" else ({"Authorization": "Bearer " + bearer} if bearer else {})
            response = await self.client.post("/api/teacher/chat", json=payload, headers=headers)
            self.assertEqual(response.status_code, 200)
            return response.json()

        async def exercise_browser_delivery(self, lang):
            # The driver lives in a separate network namespace. Its only way
            # into this ASGI app is a bounded set of synthetic HTTP requests.
            previous = {row["_id"] async for row in self.collection.find({}, {"_id": 1})}
            print("V6 " + json.dumps({"language": lang, "bearer": self.bearer, "question": self.question["question"][lang],
                "wrong": self.question["options"][1]["text"][lang], "wrongPhrase": self.wrong_phrases[lang],
                "rightPhrase": self.right_phrases[lang], "firstPrompt": self.first_prompt[lang],
                "hint": self.hints[lang], "alternative": self.alternatives[lang], "confirmation": self.confirmation[lang]}), flush=True)
            page_path = f"/{lang}/app"
            status_path = f"/api/teacher/v6/status?language={lang}"
            allowed = {("GET", page_path), ("GET", status_path), ("GET", "/api/auth/me"),
                       ("POST", "/api/teacher/v6/text/start"), ("POST", "/api/teacher/chat")}
            for _ in range(24):
                line = sys.stdin.buffer.readline(16385)
                self.assertTrue(line.endswith(b"\n") and len(line) <= 16384, "Incomplete browser request")
                request = json.loads(line)
                if request == {"finished": lang}:
                    break
                method, path = request["method"], request["path"]
                self.assertIn((method, path), allowed)
                headers = {}
                if path != page_path:
                    self.assertEqual(request["authorization"], self.headers["Authorization"])
                    headers["Authorization"] = request["authorization"]
                response = await self.client.request(method, path, headers=headers, json=request.get("body"))
                self.assertEqual(response.status_code, 200, path)
                print("V6 " + json.dumps({"status": response.status_code, "type": response.headers["content-type"],
                                          "body": response.text}, ensure_ascii=False), flush=True)
            else:
                self.fail("Browser did not complete the delivery within the request limit")
            records = [r async for r in self.collection.find({}) if r["_id"] not in previous]
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["level"], 0)
            self.assertEqual([(e["verdict"], e["level"]) for e in records[0]["events"]],
                             [("unknown", 0), ("incorrect", 1), ("incorrect", 2), ("correct", 0)])
            print(f"Chromium and MongoDB passed for {lang}", file=sys.stderr, flush=True)

        async def test_six_paths_all_languages(self):
            for lang in ("no", "th", "en"):
                right = self.question["options"][0]["text"][lang]
                wrong = self.question["options"][1]["text"][lang]
                with self.subTest(language=lang):
                    await self.exercise_browser_delivery(lang)
                    delivery = await self.client.post("/api/teacher/v6/text/start", json={"language": lang},
                        headers=self.headers)
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
                    self.assertEqual(incorrect["reply"], self.hints[lang])
                    for _ in range(4):
                        self.assertTrue((await self.call(lang, "answer", wrong))["suggestions"])
                    records = [row async for row in self.collection.find({}) if row["_id"] not in existing_ids]
                    self.assertEqual(len(records), 1)
                    record = records[0]
                    self.assertEqual(len(record["events"]), 1)
                    self.assertEqual(record["level"], 1)
                    second_wrong = await self.call(lang, "answer", wrong, v6_event_id="synthetic-second-wrong-0002")
                    self.assertEqual(second_wrong["suggestions"][0]["v6_feedback"], "incorrect")
                    self.assertEqual(second_wrong["reply"], self.alternatives[lang])
                    correct = await self.call(lang, "answer", right, v6_event_id="synthetic-correct-event-0002")
                    self.assertEqual(correct["suggestions"][0]["v6_feedback"], "correct")
                    self.assertEqual(correct["reply"], self.confirmation[lang])
                    record = await self.collection.find_one({"_id": record["_id"]})
                    self.assertEqual(record["level"], 0)
                    self.assertEqual(len(record["events"]), 3)
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
                    await self.questions.update_one({"id": old["id"]}, {"$set": {"correctOptionId": "B"}})
                    changed = await self.call(lang, "explain")
                    self.assertEqual(changed["suggestions"][0]["v6_feedback"], "unavailable")
                    self.assertNotIn(old["options"][0]["text"][lang], changed["reply"])
                    await self.questions.replace_one({"id": old["id"]}, dict(old))
                    inserted = await self.questions.insert_one(dict(old))
                    duplicate = await self.call(lang, "explain")
                    self.assertEqual(duplicate["suggestions"][0]["v6_feedback"], "unavailable")
                    await self.questions.delete_one({"_id": inserted.inserted_id})

        async def test_unverified_or_different_user_is_denied(self):
            for lang in ("no", "th", "en"):
                expired = jwt.encode({"sub": "synthetic-user", "exp": 1}, self.server.JWT_SECRET, algorithm="HS256")
                for bearer in (None, "invalid-bearer", expired, self.other_bearer):
                    response = await self.call(lang, "explain", bearer=bearer)
                    self.assertEqual(response["suggestions"][0]["v6_feedback"], "unavailable")
                    self.assertNotIn(self.question["options"][0]["text"][lang], response["reply"])
                wrong_session = await self.call(lang, "answer", self.question["options"][0]["text"][lang],
                                                session_id="another-students-session")
                self.assertEqual(wrong_session["suggestions"][0]["v6_feedback"], "unavailable")
            self.assertEqual(await self.collection.count_documents({}), 0)

        async def test_revoked_access_denied_before_delivery_and_after_delivery(self):
            await self.users.update_one({"id": "other-user"}, {"$set": {"is_premium": False}})
            headers = {"Authorization": "Bearer " + self.other_bearer}
            response = await self.client.post("/api/teacher/v6/text/start", json={"language": "no"}, headers=headers)
            self.assertFalse(response.json()["ready"])
            await self.users.update_one({"id": "synthetic-user"}, {"$set": {"is_premium": False}})
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

        async def test_stale_or_missing_guidance_blocks_delivery_and_fasit(self):
            review = policy.APPROVED_GUIDANCE[self.question["id"]]
            for bad_digest in ("0" * 64, None):
                if bad_digest is None:
                    policy.APPROVED_GUIDANCE.pop(self.question["id"], None)
                else:
                    review["question_digest"] = bad_digest
                delivery = await self.client.post("/api/teacher/v6/text/start", json={"language": "no"},
                    headers=self.headers)
                self.assertFalse(delivery.json()["ready"])
                response = await self.call("no", "explain")
                self.assertEqual(response["suggestions"][0]["v6_feedback"], "unavailable")
                self.assertNotIn(self.question["options"][0]["text"]["no"], response["reply"])
            self.assertEqual(await self.collection.count_documents({}), 0)

        async def test_unapproved_stop_sign_cannot_be_issued(self):
            draft = json.loads(Path(__file__).with_name("stop_sign_candidate_v1.json").read_text(encoding="utf-8"))
            self.assertEqual(draft["status"], "test_only_thai_review_pending")
            candidate = draft["question"]
            self.assertNotIn(candidate["id"], policy.APPROVED_CONTENT_DIGESTS)
            self.assertIsNone(policy.issue_delivery_token(candidate))
            await self.questions.replace_one({"id": self.question["id"]}, dict(candidate))
            response = await self.client.post("/api/teacher/v6/text/start", json={"language": "th"},
                headers=self.headers)
            self.assertFalse(response.json()["ready"])
            self.assertEqual(await self.collection.count_documents({}), 0)

        async def test_existing_quiz_coach_without_context_does_not_use_v6(self):
            async def empty_history(*args):
                return []
            async def empty_plan(*args):
                return {}
            async def unexpected_v6(*args):
                raise AssertionError("Existing coach was routed to V6")
            with patch.object(tc, "_load_session_history", empty_history), \
                 patch.object(tc, "_load_study_plan", empty_plan), \
                 patch.object(tc, "_v6_quiz_pilot", unexpected_v6):
                for lang in ("no", "th", "en"):
                    response = await self.client.post("/api/teacher/chat", json={
                        "message": "synthetic", "language": lang, "mode": "quiz_coach"})
                    self.assertEqual(response.status_code, 200)
                    body = response.json()
                    self.assertEqual(body["mode"], "quiz_coach")
                    self.assertEqual(body["reply"], tc._V4_COPY[lang]["quiz_missing"])
            self.assertEqual(await self.collection.count_documents({}), 0)

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
