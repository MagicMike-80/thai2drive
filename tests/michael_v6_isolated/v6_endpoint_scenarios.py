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


def build_endpoint_case(tc, policy, mongo_client_class=None, *, live_completion=None, observations=None):
    """Run synthetic endpoint tests after the separate isolation gate passes."""
    import httpx
    import jwt
    from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from pydantic import BaseModel
    from backend.webapp import webapp_router

    # Execute the exact checked-out auth and policy handlers with their FastAPI
    # decorators. Leave unrelated server startup integrations outside this gate.
    server_path = Path(__file__).resolve().parents[2] / "backend/server.py"
    names = {"create_token", "verify_token", "get_current_user", "get_me", "_auth_user_payload",
             "_access_expires_at", "_user_trial_days_left", "_user_premium_status", "_paid_premium_active",
             "_user_has_active_trial", "_parse_iso_utc", "_user_has_active_premium", "_get_access_usage",
             "_access_scope", "_oslo_day_key", "_access_policy_payload", "access_consume", "get_optional_user",
             "AccessConsumeRequest", "_consume_registered_quota", "_v6_registered_quota_enabled",
             "_check_guest_access_request", "_consume_guest_quota", "_verified_guest_device", "guest_session",
             "_v6_guest_enabled", "access_status"}
    nodes = [node for node in ast.parse(server_path.read_bytes()).body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in names]
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
                datetime=datetime, timezone=timezone, timedelta=timedelta, Optional=Optional, os=os, uuid=uuid,
                BaseModel=BaseModel, Request=Request,
                HTTPAuthorizationCredentials=HTTPAuthorizationCredentials, HTTPException=HTTPException,
                Depends=Depends, security=HTTPBearer(auto_error=False), api_router=APIRouter())
            exec(auth_code, self.server.__dict__)
            self.bearer = self.server.create_token("synthetic-user", "student@example.invalid")
            self.other_bearer = self.server.create_token("other-user", "other@example.invalid")
            self.headers = {"Authorization": "Bearer " + self.bearer}
            self.env = patch.dict(os.environ, {"MICHAEL_V6_SIGNING_KEY": "synthetic-only-key-never-used-in-production",
                "MICHAEL_V6_PROGRESS_KEY": "synthetic-progress-key-never-production", "MICHAEL_V6_ENABLED": "1",
                "MICHAEL_V6_PREMIUM_PILOT": "1"}, clear=live_completion is None)
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

        async def exercise_browser_delivery(self, lang, tier):
            # The driver lives in a separate network namespace. Its only way
            # into this ASGI app is a bounded set of synthetic HTTP requests.
            previous = {row["_id"] async for row in self.collection.find({}, {"_id": 1})}
            print("V6 " + json.dumps({"language": lang, "tier": tier, "bearer": self.bearer if tier != "guest" else None, "question": self.question["question"][lang],
                "wrong": self.question["options"][1]["text"][lang], "wrongPhrase": self.wrong_phrases[lang],
                "rightPhrase": self.right_phrases[lang], "firstPrompt": self.first_prompt[lang],
                "hint": self.hints[lang], "alternative": self.alternatives[lang], "confirmation": self.confirmation[lang]}), flush=True)
            page_path = f"/{lang}/app"
            status_path = f"/api/teacher/v6/status?language={lang}"
            allowed = {("GET", page_path), ("GET", status_path), ("GET", "/api/auth/me"),
                       ("POST", "/api/teacher/v6/text/start"), ("POST", "/api/teacher/chat")}
            if tier == "guest":
                allowed.add(("POST", "/api/access/guest-session"))
            for _ in range(24):
                line = sys.stdin.buffer.readline(16385)
                self.assertTrue(line.endswith(b"\n") and len(line) <= 16384, "Incomplete browser request")
                request = json.loads(line)
                if request == {"finished": lang}:
                    break
                method, path = request["method"], request["path"]
                self.assertIn((method, path), allowed)
                headers = {}
                if tier == "guest" and path != page_path:
                    self.assertNotIn("authorization", request)
                    headers["X-T2D-Guest-Key"] = request["guestKey"]
                elif path != page_path:
                    self.assertEqual(request["authorization"], self.headers["Authorization"])
                    headers["Authorization"] = request["authorization"]
                response = await self.client.request(method, path, headers=headers, json=request.get("body"))
                self.assertEqual(response.status_code, 200, path)
                if path == "/api/access/guest-session":
                    device = response.json()["device_id"]
                    guest_headers = headers
                if tier == "guest" and path == "/api/teacher/chat":
                    last_chat = request["body"]
                print("V6 " + json.dumps({"status": response.status_code, "type": response.headers["content-type"],
                                          "body": response.text}, ensure_ascii=False), flush=True)
            else:
                self.fail("Browser did not complete the delivery within the request limit")
            records = [r async for r in self.collection.find({}) if r["_id"] not in previous]
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["level"], 0)
            self.assertEqual([(e["verdict"], e["level"]) for e in records[0]["events"]],
                             [("unknown", 0), ("incorrect", 1), ("incorrect", 2), ("correct", 0)])
            if tier == "guest":
                usage_path = "/api/access/status"
                params = {"device_id": device}
                first = await self.client.get(usage_path, params=params, headers=guest_headers)
                self.assertEqual((first.json()["used"], first.json()["remaining"]), (1, 4))
                for wrong_headers in ({}, {"X-T2D-Guest-Key":secrets.token_hex(32)}):
                    foreign = await self.client.get(usage_path, params=params, headers=wrong_headers)
                    self.assertEqual(foreign.status_code, 403)
                    denied = await self.client.post("/api/teacher/chat", json=last_chat, headers=wrong_headers)
                    self.assertEqual(denied.json()["suggestions"][0]["v6_feedback"], "unavailable")
                async def ordinary(i):
                    return await self.client.post("/api/access/consume", headers=guest_headers,
                        json={**params, "event_id": "ordinary-" + str(i), "question_id":"synthetic"})
                answers = await asyncio.gather(*(ordinary(i) for i in range(5)))
                self.assertCountEqual([answer.status_code for answer in answers], [200, 200, 200, 200, 402])
                accepted = next(i for i, answer in enumerate(answers) if answer.status_code == 200)
                self.assertFalse((await ordinary(accepted)).json()["consumed"])
                final = await self.client.get(usage_path, params=params, headers=guest_headers)
                self.assertEqual((final.json()["used"], final.json()["remaining"]), (5, 0))
                new_delivery = await self.client.post("/api/teacher/v6/text/start", json={"language":lang}, headers=guest_headers)
                self.assertFalse(new_delivery.json()["ready"])
            print(f"Chromium and MongoDB passed for {lang} ({tier})", file=sys.stderr, flush=True)

        async def test_six_paths_all_languages(self):
            for lang in ("no", "th", "en"):
                right = self.question["options"][0]["text"][lang]
                wrong = self.question["options"][1]["text"][lang]
                with self.subTest(language=lang):
                    await self.exercise_browser_delivery(lang, "premium")
                    usage = self.server.db.access_usage
                    selector = {"scope": "user", "key": "synthetic-user"}
                    before = await usage.find_one(selector) or {}
                    await self.users.update_one({"id": "synthetic-user"}, {"$set": {"is_premium": False}})
                    with patch.dict(os.environ, {"MICHAEL_V6_REGISTERED_ENABLED": "1"}):
                        await self.exercise_browser_delivery(lang, "registered")
                    after = await usage.find_one(selector)
                    self.assertEqual(after["daily_used"], before.get("daily_used", 0) + 1)
                    with patch.dict(os.environ, {"MICHAEL_V6_GUEST_ENABLED": "1"}):
                        await self.exercise_browser_delivery(lang, "guest")
                    await self.users.update_one({"id": "synthetic-user"}, {"$set": {"is_premium": True}})
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

        async def test_registered_stop_sign_access_and_teaching(self):
            policy.APPROVED_GUIDANCE.clear()
            policy.APPROVED_CONTENT_DIGESTS.clear()
            policy.load_stop_sign_approval()
            bank = await self.questions.find({}).to_list(10)
            pilot = self.server.db[policy.PILOT_COLLECTION]
            for _ in range(2):
                self.assertEqual(await policy.register_stop_sign(self.server.db, tc._reply_matches_language_script),
                                 policy.STOP_SIGN_ID)
            self.assertEqual(await self.questions.find({}).to_list(10), bank)
            self.assertEqual(await pilot.count_documents({}), 1)
            q = await pilot.find_one({"id": policy.STOP_SIGN_ID})
            self.assertIs(q["pilot_open"], False)
            g = policy.APPROVED_GUIDANCE[policy.STOP_SIGN_ID]
            async def ready(headers):
                r = await self.client.post("/api/teacher/v6/text/start", headers=headers, json={"language":"no"})
                return r.json()["ready"]
            with patch.dict(os.environ, {"MICHAEL_V6_REGISTERED_ENABLED":"1", "MICHAEL_V6_GUEST_ENABLED":"1",
                                         "MICHAEL_V6_PILOT_USER_ID":"synthetic-user"}):
                self.assertFalse(await ready(self.headers))
                await pilot.update_one({"_id":policy.STOP_SIGN_ID}, {"$set":{"pilot_open":True}})
                others = {"Authorization":"Bearer " + self.other_bearer}
                self.assertFalse(await ready(others))
                await self.users.update_one({"id":"other-user"}, {"$set":{"is_premium":False}})
                self.assertFalse(await ready(others))
                with patch.dict(os.environ, {"MICHAEL_V6_PILOT_USER_ID":""}):
                    self.assertFalse(await ready(self.headers))
                for tier in ("premium", "registered", "guest"):
                    await self.users.update_one({"id":"synthetic-user"}, {"$set":{"is_premium":tier == "premium"}})
                    headers = self.headers
                    if tier == "guest":
                        headers = {"X-T2D-Guest-Key":secrets.token_hex(32)}
                        guest = await self.client.post("/api/access/guest-session", headers=headers)
                        self.assertEqual(guest.status_code, 200)
                    for lang in ("no", "th", "en"):
                        with self.subTest(tier=tier, lang=lang):
                            delivery = (await self.client.post("/api/teacher/v6/text/start",
                                        json={"language":lang}, headers=headers)).json()
                            if tier == "guest":
                                self.assertFalse(delivery["ready"])
                                continue
                            self.assertTrue(delivery["ready"])
                            self.assertEqual(delivery["question_id"], policy.STOP_SIGN_ID)
                            self.assertEqual(delivery["question"], q["question"][lang])
                            opts = {o["id"]:o["text"][lang] for o in q["options"]}
                            self.assertCountEqual([s[3:] for s in delivery["choices"]], opts.values())
                            async def send(intent, answer=None, event=None):
                                body = {"language":lang,"mode":"v6_quiz_pilot","message":answer or "?",
                                        "session_id":delivery["session_id"],"v6_question_id":delivery["question_id"],
                                        "v6_delivery_token":delivery["delivery_token"],"v6_actor_binding":delivery["actor_binding"],
                                        "v6_intent":intent,"v6_event_id":event or uuid.uuid4().hex,"v6_answer_text":answer}
                                result = await self.client.post("/api/teacher/chat", headers=headers, json=body)
                                self.assertEqual(result.status_code, 200)
                                data = result.json()
                                return data["suggestions"][0]["v6_feedback"], data["reply"]
                            self.assertEqual(await send("alternative"), ("guidance",g["prompts"][lang]["hint"]))
                            self.assertEqual(await send("alternative"), ("guidance",g["prompts"][lang]["alternative"]))
                            hints = g["options"][lang]
                            self.assertEqual(await send("answer",opts["A"]), ("incorrect",hints["A"]["hint"]))
                            self.assertEqual((await send("answer", "?"))[0], "unknown")
                            self.assertEqual(await send("answer",opts["C"]), ("incorrect",hints["C"]["hint"]))
                            retry = uuid.uuid4().hex
                            self.assertEqual(await send("answer",opts["C"],retry), ("incorrect",hints["C"]["alternative"]))
                            self.assertEqual(await send("answer",opts["C"],retry), ("incorrect",hints["C"]["alternative"]))
                            shown = next(s[0] for s in delivery["choices"] if s[3:] == opts["B"])
                            self.assertEqual(await send("answer",shown), ("correct",g["confirmation"][lang] + "\n" + policy.UNDERSTANDING_CHECK[lang]))
                            natural = {"no":"jeg tror ", "en":"I think ", "th":"ผมคิดว่าข้อ "}[lang] + shown
                            self.assertEqual((await send("answer", natural))[0], "correct")
                            with patch.dict(os.environ, {"MICHAEL_V6_PILOT_USER_ID":"other-user"}):
                                self.assertEqual((await send("answer", shown))[0], "unavailable")
                            other_lang = "en" if lang == "no" else "no"
                            self.assertIsNone(policy.delivery_session_id(delivery["delivery_token"], other_lang))
                            await pilot.update_one({"_id":policy.STOP_SIGN_ID}, {"$set":{"pilot_open":False}})
                            self.assertEqual((await send("answer",shown))[0], "unavailable")
                            await pilot.update_one({"_id":policy.STOP_SIGN_ID}, {"$set":{"pilot_open":True}})
                            print(f"Stop sign passed for {lang} ({tier})", file=sys.stderr, flush=True)
            await pilot.update_one({"_id":policy.STOP_SIGN_ID}, {"$set":{"correctOptionId":"C"}})
            with self.assertRaises(ValueError):
                await policy.register_stop_sign(self.server.db, tc._reply_matches_language_script)
            self.assertEqual((await pilot.find_one({"_id":policy.STOP_SIGN_ID}))["correctOptionId"], "C")
            self.assertEqual(await self.questions.find({}).to_list(10), bank)

        async def test_claude_dialogues_through_chat(self):
            policy.APPROVED_GUIDANCE.clear()
            policy.APPROVED_CONTENT_DIGESTS.clear()
            policy.load_stop_sign_approval()
            os.environ["MICHAEL_V6_PILOT_USER_ID"] = "synthetic-user"
            await policy.register_stop_sign(self.server.db, tc._reply_matches_language_script)
            pilot = self.server.db[policy.PILOT_COLLECTION]
            await pilot.update_one({"_id":policy.STOP_SIGN_ID}, {"$set":{"pilot_open":True}})
            self.question = await pilot.find_one({"id": policy.STOP_SIGN_ID})
            guidance = policy.APPROVED_GUIDANCE[policy.STOP_SIGN_ID]
            cases = json.loads(Path(__file__).with_name("stop_sign_dialogues.json").read_text(encoding="utf-8"))
            self.assertEqual((len(cases), sum(len(c["turns"]) for c in cases)), (15, 62))
            extras = {
                "no": ("Hvor skal forhjulene stanse ved den merkede linjen?", "Jeg stopper helt.", "Jeg stanser rett før linjen, lar trafikken fra begge sider passere og kjører når det er trygt."),
                "th": ("ต้องหยุดรถตรงไหนของเส้นหยุดครับ", "ผมจะหยุดรถให้สนิท", "ผมจอดนิ่งชิดหน้าเส้นหยุด รอให้รถที่มาจากทั้งซ้ายและขวาผ่าน แล้วค่อยขับต่อเมื่อปลอดภัย"),
                "en": ("Where exactly at the marked line should my wheels stop?", "I'd bring the car to a full stop.", "I come to a standstill just before the line, let traffic from both sides pass and move off when safe."),
            }
            for lang, sentences in extras.items():
                cases.append({"language":lang, "scenario":6, "turns":[
                    {"text":text, "focus":focus, "grade":grade} for text, focus, grade in
                    zip(sentences, ("line","partial_stop","sequence"), ("unknown","partial","correct"))]})
            for case in cases:
                lang = case["language"]
                delivery = (await self.client.post("/api/teacher/v6/text/start", headers=self.headers,
                            json={"language":lang})).json()
                self.token, self.actor_binding = delivery["delivery_token"], delivery["actor_binding"]
                options = {o["id"]: o["text"][lang] for o in self.question["options"]}
                before = await self.call(lang, "explain")
                self.assertEqual(before["reply"], guidance["prompts"][lang]["hint"])
                for i, turn in enumerate(case["turns"]):
                    with self.subTest(language=lang, scenario=case["scenario"], turn=i):
                        answer = options[turn["option"]] if "option" in turn else turn.get("text")
                        intent = "explain" if turn.get("explain") else "answer"
                        async def classifier(messages):
                            if live_completion:
                                return await live_completion(messages)
                            payload = json.loads(messages[-1]["content"])
                            if "student_answer" in payload:
                                self.assertEqual(payload["student_answer"], answer)
                                content = json.dumps({"verdict":turn["grade"],"evidence":answer})
                            else:
                                self.assertEqual(payload["learner"], answer)
                                content = turn["focus"]
                            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(
                                content=content))])
                        with patch.object(tc, "_completion_with_fallback", side_effect=classifier) as model:
                            event_id = uuid.uuid4().hex
                            result = await self.call(lang, intent, answer, v6_event_id=event_id)
                            grade = turn["grade"]
                            if answer in ("B", "ข้อ B"):
                                grade = "correct" if delivery["choices"][1][3:] == options["B"] else "incorrect"
                            if observations is not None:
                                observations.append(dict(scenario=case["scenario"],language=lang,turn=i+1,learner=answer,
                                    expected=grade,actual=result["suggestions"][0]["v6_feedback"],reply=result["reply"]))
                            self.assertEqual(result["suggestions"][0]["v6_feedback"], grade)
                            self.assertTrue(tc._reply_matches_language_script(result["reply"], lang))
                            if turn.get("focus") and policy.needs_stop_dialogue_model(answer):
                                self.assertGreaterEqual(model.await_count, 1)
                            else:
                                model.assert_not_awaited()
                            if turn["grade"] == "unknown":
                                call_count = model.await_count
                                replay = await self.call(lang, intent, answer, v6_event_id=event_id)
                                self.assertEqual(replay["reply"], result["reply"])
                                self.assertEqual(model.await_count, call_count)
                            if turn["grade"] == "partial":
                                self.assertEqual(result["reply"], guidance["prompts"][lang]["alternative"])
                            if focus := turn.get("focus"):
                                if focus == "line":
                                    self.assertIn(options["B"].split(" " if lang == "th" else ",")[0], result["reply"])
                            focus = turn.get("focus")
                            if focus == "reason":
                                self.assertIn(self.question["explanation"][lang], result["reply"])
                                self.assertEqual(len(result["suggestions"]), 1)
                            if focus == "stopping":
                                level = "alternative" if i == 1 else "hint"
                                self.assertEqual(result["reply"], guidance["options"][lang]["A"][level])
                            if focus == "yielding":
                                self.assertEqual(result["reply"], guidance["options"][lang]["C"]["alternative"])
                            if focus == "comparison":
                                self.assertIn(guidance["prompts"][lang]["alternative"], result["reply"])
                            if focus == "uncertain" and i == 1:
                                self.assertNotEqual(result["reply"], previous)
                            previous = result["reply"]
                async def invalid(messages):
                    return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(
                        content="Invented traffic rule"))])
                with patch.object(tc, "_completion_with_fallback", side_effect=invalid):
                    result = await self.call(lang, "answer", "???", v6_event_id=uuid.uuid4().hex)
                    self.assertEqual(result["suggestions"][0]["v6_feedback"], "unknown")
                    self.assertNotIn("Invented", result["reply"])
                with patch.object(tc, "_completion_with_fallback", side_effect=TimeoutError):
                    result = await self.call(lang, "answer", "???", v6_event_id=uuid.uuid4().hex)
                    self.assertEqual(result["suggestions"][0]["v6_feedback"], "unknown")
                    self.assertTrue(tc._reply_matches_language_script(result["reply"], lang))

            if live_completion:
                with patch.dict(os.environ, {"MICHAEL_V6_ENABLED":"0"}), patch.object(tc, "_chat_col", self.server.db.teacher_chats), patch.object(tc, "_completion_with_fallback", side_effect=live_completion) as model:
                    result = await self.client.post("/api/teacher/chat", json={"language":"no", "mode":"normal_chat",
                        "message":"Jeg synes det er vanskelig å forklare valgene mine når jeg øver. Hvordan kan jeg øve på det?"})
                    self.assertEqual(result.status_code, 200)
                    body = result.json()
                    self.assertNotEqual(body["mode"], "v6_quiz_pilot")
                    self.assertGreater(model.await_count, 0)
                    self.assertTrue(tc._reply_matches_language_script(body["reply"], "no"))
                    observations.append(dict(scenario="V5", language="no", expected="ordinary", actual="ordinary", reply=body["reply"]))

        async def test_natural_lesson_with_authorized_history(self):
            os.environ.update(MICHAEL_V6_NATURAL_DIALOGUE_ENABLED="1", MICHAEL_V6_PILOT_USER_ID="synthetic-user")
            policy.APPROVED_GUIDANCE.clear()
            policy.APPROVED_CONTENT_DIGESTS.clear()
            policy.load_stop_sign_approval()
            await policy.register_stop_sign(self.server.db, tc._reply_matches_language_script)
            pilot = self.server.db[policy.PILOT_COLLECTION]
            await pilot.update_one({"_id":policy.STOP_SIGN_ID}, {"$set":{"pilot_open":True}})
            self.question = await pilot.find_one({"id":policy.STOP_SIGN_ID})
            samples = {
                "no": ["Kan jeg få et hint om det jeg overså?", "Hvor nær streken skal jeg stanse?",
                       "Da ombestemmer jeg meg. Jeg vil stanse helt, men er usikker på hvem som kjører først.",
                       "Jeg gjettet egentlig. Hvorfor er det riktig?", "Kan du forklare det annerledes, sett fra bilen til venstre?"],
                "th": ["ช่วยใบ้หน่อยครับว่าผมพลาดอะไรไป", "ต้องหยุดใกล้เส้นแค่ไหนครับ",
                       "ผมเปลี่ยนใจแล้ว ผมจะหยุดให้สนิท แต่ยังไม่แน่ใจว่าใครไปก่อน",
                       "จริง ๆ แล้วผมเดาครับ ทำไมถึงถูก", "ช่วยอธิบายอีกแบบจากมุมของรถที่มาทางซ้ายได้ไหมครับ"],
                "en": ["Can I have a hint about what I missed?", "How close to the line do I stop?",
                       "I've changed my mind. I'd stop completely, but I'm unsure who goes first.",
                       "I actually guessed. Why is that right?", "Could you explain it another way, from the left driver's point of view?"],
            }
            for lang, words in samples.items():
                start = (await self.client.post("/api/teacher/v6/text/start", headers=self.headers,
                                                json={"language":lang})).json()
                self.assertTrue(start["ready"])
                self.token, self.actor_binding = start["delivery_token"], start["actor_binding"]
                opts = {o["id"]:o["text"][lang] for o in self.question["options"]}
                label = next(s[0] for s in start["choices"] if s[3:] == opts["B"])
                turns = [("answer", opts["A"]), ("hint", words[0]), ("answer", words[1]), ("answer", words[2]),
                         ("answer", label), ("answer", words[3]), ("alternative", words[4])]
                expected_history = []
                for i, (intent, learner) in enumerate(turns):
                    supplied, drafts, checked = [], [], []
                    async def model(messages):
                        system = messages[0]["content"]
                        data = json.loads(messages[-1]["content"])
                        if system.startswith("V6 LESSON WRITER"):
                            supplied.append(data)
                            content = (policy.APPROVED_GUIDANCE[policy.STOP_SIGN_ID]["prompts"][lang]["hint"]
                                       if not live_completion else None)
                        elif system.startswith("V6 LESSON REVIEW"):
                            checked.append(data["draft"])
                            content = "PASS"
                        else:
                            content = {2:"line",3:"partial_stop",5:"reason"}.get(i,"uncertain")
                        if live_completion:
                            output = await live_completion(messages)
                        else:
                            output = types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=content))])
                        if system.startswith("V6 LESSON WRITER"):
                            drafts.append(output.choices[0].message.content.strip())
                        return output
                    event = uuid.uuid4().hex
                    with patch.object(tc, "_completion_with_fallback", side_effect=model) as port:
                        response = await self.call(lang, intent, learner, v6_event_id=event)
                        meta = response["suggestions"][0]
                        self.assertNotEqual(meta["v6_feedback"], "unavailable")
                        self.assertIn(len(supplied), (1, 2))
                        self.assertEqual([(t["learner"],t["teacher"]) for t in supplied[0]["history"]], expected_history)
                        self.assertEqual(supplied[0]["language"], lang)
                        self.assertTrue(tc._reply_matches_language_script(response["reply"], lang))
                        if i in (0,4):
                            self.assertEqual(meta["v6_feedback"], "correct" if i==4 else "incorrect")
                        if i < 4:
                            self.assertIsNone(supplied[0]["approved_explanation"])
                        if meta["v6_reply_source"] == "model":
                            self.assertEqual(response["reply"], checked[-1])
                            self.assertIn(response["reply"], drafts)
                        if observations is not None:
                            observations.append(dict(language=lang, turn=i+1, learner=learner, reply=response["reply"],
                                source=meta["v6_reply_source"], feedback=meta["v6_feedback"], history=len(expected_history)))
                        expected_history.append((learner,response["reply"]))
                        calls = port.await_count
                        replay = await self.call(lang, intent, learner, v6_event_id=event)
                        self.assertEqual(replay, response)
                        self.assertEqual(port.await_count, calls)
                        denied = await self.call(lang, intent, learner, bearer=self.other_bearer, v6_event_id=event)
                        self.assertEqual(denied["suggestions"][0]["v6_feedback"], "unavailable")
                        self.assertEqual(port.await_count, calls)
                original = await pilot.find_one({"_id":policy.STOP_SIGN_ID})
                self.assertEqual(original,self.question)
                self.assertEqual(policy._content_digest(original),policy.STOP_SIGN_DIGEST)
                for failure in ("invalid language", "unsupported rule", "timeout"):
                    async def fail(messages):
                        if failure=="timeout":
                            raise TimeoutError
                        raw = "REJECT" if messages[0]["content"].startswith("V6 LESSON REVIEW") else (
                            "ภาษาไทย" if lang!="th" and failure=="invalid language" else
                            "You must wait twenty minutes." if lang=="th" or failure=="invalid language" else
                            {"no":"Stans bare hvis det kommer en buss.", "en":"Stop only if a bus comes."}[lang])
                        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=raw))])
                    with patch.object(tc,"_completion_with_fallback",side_effect=fail):
                        response = await self.call(lang,"hint",words[0],v6_event_id=uuid.uuid4().hex)
                        self.assertEqual(response["suggestions"][0]["v6_reply_source"],"reviewed_fallback")
                        self.assertTrue(tc._reply_matches_language_script(response["reply"],lang))
                if live_completion:
                    rejected = []
                    async def faulty_writer(messages):
                        if messages[0]["content"].startswith("V6 LESSON REVIEW"):
                            actual = await live_completion(messages)
                            rejected.append(actual.choices[0].message.content.strip())
                            return actual
                        wrong = {"no":"Du kan rulle forbi stopplinjen hvis veien er tom.",
                                 "en":"You can roll past the stop line if the road is empty.",
                                 "th":"ถ้าถนนว่างคุณสามารถขับผ่านเส้นหยุดได้โดยไม่ต้องหยุดรถ"}[lang]
                        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=wrong))])
                    with patch.object(tc,"_completion_with_fallback",side_effect=faulty_writer):
                        response = await self.call(lang,"hint",words[0],v6_event_id=uuid.uuid4().hex)
                    self.assertEqual(response["suggestions"][0]["v6_reply_source"],"reviewed_fallback")
                    self.assertTrue(rejected and all(v=="REJECT" for v in rejected))
                renewed = (await self.client.post("/api/teacher/v6/text/start", headers=self.headers,
                                                  json={"language":lang})).json()
                before = self.actor_binding
                self.actor_binding = renewed["actor_binding"]
                denied = await self.call(lang,"hint",words[0],v6_event_id=uuid.uuid4().hex)
                self.assertEqual(denied["suggestions"][0]["v6_feedback"], "unavailable")
                self.assertNotEqual(before, self.actor_binding)
                self.token = renewed["delivery_token"]
                seen = []
                async def new_session(messages):
                    seen.append(json.loads(messages[-1]["content"])["history"])
                    raise TimeoutError
                with patch.object(tc,"_completion_with_fallback",side_effect=new_session):
                    await self.call(lang,"hint",words[0],v6_event_id=uuid.uuid4().hex)
                self.assertEqual(seen, [[]])
            if live_completion:
                with patch.object(tc,"_chat_col",self.server.db.teacher_chats), patch.object(tc,"_completion_with_fallback",side_effect=live_completion) as port:
                    for tier in ("premium","free","guest"):
                        headers = {} if tier=="guest" else {"Authorization":"Bearer "+self.other_bearer}
                        if tier=="free":
                            await self.users.update_one({"id":"other-user"},{"$set":{"is_premium":False}})
                        access = await self.client.post("/api/teacher/v6/text/start",headers=headers,json={"language":"no"})
                        self.assertFalse(access.json()["ready"])
                        before = port.await_count
                        res = await self.client.post("/api/teacher/chat",headers=headers,json={"language":"no","mode":"normal_chat",
                            "session_id":"synthetic-standard-"+tier,"message":"Hvordan kan jeg øve på å forklare valgene mine?"})
                        self.assertEqual(res.status_code,200)
                        self.assertGreater(port.await_count,before)
                        self.assertNotEqual(res.json()["mode"],"v6_quiz_pilot")
                        self.assertNotEqual(res.json()["reply"],tc._fallback_reply("no"))
                        print("Ordinary chat passed and pilot denied for",tier,file=sys.stderr,flush=True)

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
            guidance = draft["guidance_draft"]
            self.assertEqual(guidance["question_digest"], policy._content_digest(candidate))
            self.assertEqual(guidance["reviewed_languages"], [])
            self.assertNotIn(candidate["id"], policy.APPROVED_CONTENT_DIGESTS)
            self.assertIsNone(policy.issue_delivery_token(candidate))
            await self.questions.replace_one({"id": self.question["id"]}, dict(candidate))
            response = await self.client.post("/api/teacher/v6/text/start", json={"language": "th"},
                headers=self.headers)
            self.assertFalse(response.json()["ready"])
            with patch.dict(policy.APPROVED_CONTENT_DIGESTS, {candidate["id"]: guidance["question_digest"]}), \
                 patch.dict(policy.APPROVED_GUIDANCE, {candidate["id"]: guidance}):
                for language in ("no", "th", "en"):
                    self.assertEqual(set(guidance["options"][language]), {"A", "C"})
                    response = await self.client.post("/api/teacher/v6/text/start", json={"language": language},
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
            # Exercise the last ordinary quiz slot and V6 answers against the
            # same legacy counter. A retry must still work after the limit.
            await self.users.update_one({"id": "synthetic-user"}, {"$set": {"is_premium": False}})
            selector = {"scope": "user", "key": "synthetic-user"}
            inserted = await self.server.db.access_usage.insert_one({
                **selector, "day_key": self.server._oslo_day_key(), "daily_used": 9})
            async def ordinary(event):
                return await self.client.post("/api/access/consume", headers=self.headers, json={
                    "device_id": "synthetic-device", "question_id": "ordinary-question", "event_id": event})
            async def answer():
                return await self.call("en", "answer", self.question["options"][0]["text"]["en"])
            with patch.dict(os.environ, {"MICHAEL_V6_REGISTERED_ENABLED": "1"}):
                regular, guided = await asyncio.gather(ordinary("last-slot"), answer())
                self.assertIn(regular.status_code, (200, 402))
                won_regular = regular.status_code == 200
                self.assertEqual(guided["suggestions"][0]["v6_feedback"], "unavailable" if won_regular else "correct")
                if won_regular:
                    repeated = await ordinary("last-slot")
                    self.assertEqual(repeated.status_code, 200)
                    self.assertFalse(repeated.json()["consumed"])
                else:
                    self.assertEqual((await answer())["suggestions"][0]["v6_feedback"], "correct")
                self.assertEqual((await ordinary("one-too-many")).status_code, 402)
                self.assertEqual((await ordinary("v6:client-supplied")).status_code, 409)
            self.assertEqual(await self.server.db.access_events.count_documents(selector), 1)
            self.assertEqual(await self.server.db.access_usage.count_documents(selector), 1)
            self.assertEqual((await self.server.db.access_usage.find_one({"_id": inserted.inserted_id}))["daily_used"], 10)

    return EndpointScenarios


def run_suite(tc, policy, mongo_client_class=None, *, live_completion=None, observations=None,
              live_test="test_claude_dialogues_through_chat"):
    EndpointScenarios = build_endpoint_case(tc, policy, mongo_client_class, live_completion=live_completion,
                                             observations=observations)
    suite = (unittest.TestSuite([EndpointScenarios(live_test)]) if live_completion
             else unittest.defaultTestLoader.loadTestsFromTestCase(EndpointScenarios))
    return unittest.TextTestRunner(verbosity=2).run(suite)
