"""Exercise real FREE30 route functions without loading production configuration."""
import ast
import asyncio
import json
import logging
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from starlette.responses import JSONResponse


def actual_namespace():
    source = Path(__file__).resolve().parents[1] / "server.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    names = {
        "CampaignRegisterRequest", "_CampaignClaimConflict", "_normalize_campaign_lang",
        "register_campaign_user", "_parse_iso_utc", "_paid_premium_active",
        "_user_has_active_trial", "_user_has_active_premium", "_access_expires_at",
        "require_admin", "AdminFree30LookupRequest", "AdminFree30ActivateRequest",
        "_admin_free30_user", "admin_free30_lookup", "admin_free30_activate",
    }
    async def get_current_user():
        raise HTTPException(status_code=401)
    app, router = FastAPI(), APIRouter(prefix="/api")
    async def inline_thread(func, *args):
        return func(*args)
    ns = dict(datetime=datetime, timedelta=timedelta, timezone=timezone, Optional=Optional,
              BaseModel=BaseModel, Field=Field, Depends=Depends, HTTPException=HTTPException,
              HTTPAuthorizationCredentials=HTTPAuthorizationCredentials,
              security=HTTPBearer(auto_error=False), get_current_user=get_current_user,
              ReturnDocument=ReturnDocument, DuplicateKeyError=DuplicateKeyError,
              JSONResponse=JSONResponse, asyncio=SimpleNamespace(to_thread=inline_thread), json=json, logging=logging,
              app=app, api_router=router)
    nodes = [n for n in tree.body if
        (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name in names)
        or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id.startswith("CAMPAIGN_") for t in n.targets))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), ns)
    app.include_router(router)
    return ns


class AdminFree30Tests(unittest.TestCase):
    def setUp(self):
        self.ns = actual_namespace()
        self.user = {"id":"learner-1", "email":"learner@example.test", "is_premium":False, "trial_used":False}
        self.claims = []
        self.db = MagicMock()
        self.db.admin_users.find_one = AsyncMock(return_value={"email":"admin@example.test"})
        async def find_user(query, *args, **kwargs):
            if any(self.user.get(k) != v for k, v in query.items()): return None
            return dict(self.user)
        self.db.users.find_one = AsyncMock(side_effect=find_user)
        async def update_user(query, update, **kwargs):
            self.user.update(update["$set"])
            return SimpleNamespace(modified_count=1)
        self.db.users.update_one = AsyncMock(side_effect=update_user)
        self.db.campaign_counters.update_one = AsyncMock()
        self.db.campaign_counters.find_one_and_update = AsyncMock(return_value={"claim_revision":1})
        self.db.campaign_users.find_one = AsyncMock(side_effect=lambda *a,**k:self.claims[0] if self.claims else None)
        self.db.campaign_users.count_documents = AsyncMock(side_effect=lambda *a,**k:len(self.claims))
        async def insert_claim(doc, **kwargs): self.claims.append(dict(doc))
        self.db.campaign_users.insert_one = AsyncMock(side_effect=insert_claim)
        class Session:
            async def __aenter__(self): return self
            async def __aexit__(self,*args): return False
            async def with_transaction(self,callback): return await callback(self)
        self.db.client.start_session = AsyncMock(return_value=Session())
        self.ns["db"] = self.db
        self.ns["verify_token"] = lambda token: {"sub":"admin-1","email":"admin@example.test"} if token == "synthetic-token" else None
        self.send = MagicMock(return_value=(True,"sent"))
        self.ns["_send_free30_confirmation_sync"] = self.send
        self.headers={"Authorization":"Bearer synthetic-token"}

    @staticmethod
    def finish(coroutine):
        # No sockets, threads, event loop or production services. Every I/O seam
        # above is an immediate synthetic awaitable; unexpected I/O fails the test.
        try:
            coroutine.send(None)
        except StopIteration as result:
            return result.value
        finally:
            coroutine.close()
        raise AssertionError("Unexpected asynchronous I/O in isolated test")

    def request(self,path,body,headers):
        route=next(r for r in self.ns["app"].routes if getattr(r,"path",None)=="/api/admin/free30/"+path)
        self.assertIn(self.ns["require_admin"], [d.call for d in route.dependant.dependencies])
        raw=headers.get("Authorization", "")
        credentials=HTTPAuthorizationCredentials(scheme="Bearer",credentials=raw.removeprefix("Bearer ")) if raw else None
        try:
            admin=self.finish(self.ns["require_admin"](credentials))
            model=self.ns["AdminFree30LookupRequest" if path=="lookup" else "AdminFree30ActivateRequest"](**body)
            response=self.finish(self.ns["admin_free30_"+path](model,admin))
            if isinstance(response,dict): response=JSONResponse(response)
        except HTTPException as error:
            response=JSONResponse({"detail":error.detail},status_code=error.status_code)
        return SimpleNamespace(status_code=response.status_code,text=response.body.decode(),json=lambda:json.loads(response.body))

    def post(self,path,**body):
        return self.request(path,body,self.headers)

    def test_both_routes_require_admin_and_reject_missing_or_invalid_tokens(self):
        for path in ["lookup","activate"]:
            body={"email":self.user["email"],"user_id":self.user["id"]}
            for headers in [{},{"Authorization":"Bearer invalid"}]:
                self.assertEqual(self.request(path,body,headers).status_code,401)
            self.db.admin_users.find_one.return_value=None
            self.assertEqual(self.post(path,**body).status_code,403)
        self.db.users.update_one.assert_not_awaited()

    def test_lookup_normalizes_address_and_returns_only_customer_summary(self):
        self.user["password_hash"]="must-not-leave-db"
        self.user["phone"]="private"
        response=self.post("lookup",email=" LEARNER@EXAMPLE.TEST ")
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.json()["eligible"])
        self.assertNotIn("private",response.text)
        self.assertNotIn("must-not-leave-db",response.text)
        self.db.users.update_one.assert_not_awaited()
        projection=self.db.users.find_one.await_args.args[1]
        self.assertNotIn("password_hash",projection)
        self.assertNotIn("phone",projection)

    def test_missing_account_and_changed_customer_are_not_activated(self):
        self.assertEqual(self.post("lookup",email="missing@example.test").status_code,404)
        self.assertEqual(self.post("activate",email=self.user["email"],user_id="another-user").status_code,409)
        self.db.users.update_one.assert_not_awaited()
        self.send.assert_not_called()

    def test_paid_premium_and_previous_trials_are_ineligible(self):
        for key,value in [("is_premium",True),("trial_used",True),("trial_expires_at","2020-01-01T00:00:00+00:00")]:
            original=dict(self.user);self.user[key]=value
            self.assertFalse(self.post("lookup",email=self.user["email"]).json()["eligible"])
            self.user=original
        self.db.users.update_one.assert_not_awaited()

    def test_capacity_is_rechecked_during_activation(self):
        self.assertTrue(self.post("lookup",email=self.user["email"]).json()["eligible"])
        self.db.campaign_users.count_documents.side_effect=None
        self.db.campaign_users.count_documents.return_value=50
        response=self.post("activate",email=self.user["email"],user_id=self.user["id"])
        self.assertEqual(response.json()["error"],"campaign_sold_out")
        self.db.users.update_one.assert_not_awaited()

    def test_activation_grants_30_days_audits_actor_and_duplicate_cannot_extend(self):
        response=self.post("activate",email=self.user["email"],user_id=self.user["id"])
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.json()["confirmation_email_sent"])
        started=datetime.fromisoformat(self.user["trial_started_at"])
        expires=datetime.fromisoformat(self.user["trial_expires_at"])
        self.assertEqual(expires-started,timedelta(days=30))
        self.assertEqual(self.claims[0]["activated_by_admin"],"admin-1")
        self.assertEqual(self.claims[0]["activation_source"],"admin_email_request")
        self.assertNotIn("stripe_subscription_id",self.user)
        repeated=self.post("activate",email=self.user["email"],user_id=self.user["id"])
        self.assertEqual(repeated.status_code,400)
        self.assertEqual(datetime.fromisoformat(self.user["trial_expires_at"]),expires)
        self.db.users.update_one.assert_awaited_once()
        self.send.assert_called_once_with(self.user["email"],expires.isoformat())

    def test_email_failure_does_not_roll_back_or_hide_grant(self):
        self.send.return_value=(False,"synthetic_failure")
        response=self.post("activate",email=self.user["email"],user_id=self.user["id"])
        self.assertEqual(response.status_code,200)
        self.assertFalse(response.json()["confirmation_email_sent"])
        self.assertTrue(self.ns["_user_has_active_premium"](self.user))

    def test_expired_trial_loses_premium_without_charging(self):
        self.user.update(trial_expires_at=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(),trial_used=True)
        self.assertFalse(self.ns["_user_has_active_premium"](self.user))
        self.assertIsNone(self.ns["_access_expires_at"](self.user))


if __name__ == "__main__": unittest.main()
