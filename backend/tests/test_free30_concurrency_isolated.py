"""Opt-in real Mongo replica-set tests of the actual FREE30 claim function.

No server import, dotenv, network outside loopback, or production fixtures.
Set FREE30_TEST_MONGOD and FREE30_TEST_DBPATH to run; otherwise skipped.
The disposable local database is retained for inspection after shutdown.
"""
import ast
import asyncio
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import unittest
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import AutoReconnect, ConnectionFailure, DuplicateKeyError
from starlette.responses import JSONResponse


def actual_claim_namespace():
    """Compile selected unchanged source nodes, excluding imports/startup/routes."""
    source = Path(__file__).resolve().parents[1] / "server.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    names = {
        "CampaignRegisterRequest", "_CampaignClaimConflict", "_normalize_campaign_lang",
        "register_campaign_user", "get_campaign_status", "_parse_iso_utc",
        "_paid_premium_active", "_user_has_active_trial", "_user_trial_days_left",
        "_user_premium_status", "_user_has_active_premium", "_access_expires_at",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in names:
            node.decorator_list = []
            nodes.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id.startswith("CAMPAIGN_")
            for target in node.targets
        ):
            nodes.append(node)
    namespace = dict(datetime=datetime, timedelta=timedelta, timezone=timezone,
                     Optional=Optional, BaseModel=BaseModel, Depends=Depends,
                     get_current_user=lambda: None, ReturnDocument=ReturnDocument,
                     DuplicateKeyError=DuplicateKeyError, JSONResponse=JSONResponse)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
    return namespace


@unittest.skipUnless(os.environ.get("FREE30_TEST_MONGOD") and os.environ.get("FREE30_TEST_DBPATH"),
                     "opt-in isolated mongod executable/dbpath required")
class Free30RealTransactions(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = actual_claim_namespace()
        cls.dbpath = Path(os.environ["FREE30_TEST_DBPATH"]).resolve()
        # Prevent accidental use of any existing or production database directory.
        if cls.dbpath.exists():
            raise RuntimeError("Use a NEW disposable dbpath for each run")
        if "free30-go-20261025" not in cls.dbpath.parts:
            raise RuntimeError("dbpath must be inside FREE30 evidence directory")
        cls.dbpath.mkdir(parents=True)
        with socket.socket() as available:
            available.bind(("127.0.0.1", 0))
            cls.port = available.getsockname()[1]
        cls.uri = f"mongodb://127.0.0.1:{cls.port}/?replicaSet=free30isolated"
        cls.process = subprocess.Popen(
            [os.environ["FREE30_TEST_MONGOD"], "--dbpath", str(cls.dbpath),
             "--bind_ip", "127.0.0.1", "--port", str(cls.port),
             "--replSet", "free30isolated", "--logpath", str(cls.dbpath / "mongod.log")],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        cls.direct = MongoClient(f"mongodb://127.0.0.1:{cls.port}/?directConnection=true",
                                 serverSelectionTimeoutMS=500)
        deadline = time.monotonic() + 120
        try:
            while True:
                try:
                    cls.direct.admin.command("ping")
                    break
                except ConnectionFailure:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(.1)
            cls.direct.admin.command("replSetInitiate", {
                "_id": "free30isolated", "members": [{"_id": 0, "host": f"127.0.0.1:{cls.port}"}]})
            while not cls.direct.admin.command("hello").get("isWritablePrimary"):
                if time.monotonic() >= deadline:
                    raise RuntimeError("isolated replica set did not elect primary")
                time.sleep(.1)
        except Exception:
            cls.process.terminate()
            cls.process.wait(timeout=10)
            raise
        print(f"ISOLATED_MONGO loopback_only=true replica_set=true port={cls.port}", flush=True)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.direct.admin.command("shutdown", force=True)
        except AutoReconnect:
            pass
        finally:
            cls.direct.close()
            cls.process.wait(timeout=15)

    async def asyncSetUp(self):
        self.client = AsyncIOMotorClient(self.uri, serverSelectionTimeoutMS=2000)
        suffix = hashlib.sha256(self._testMethodName.encode()).hexdigest()[:12]
        self.db = self.client["free30_isolated_" + suffix]
        self.ns["db"] = self.db
        await self.db.users.create_index("id", unique=True)
        await self.db.campaign_users.create_index([("campaign_id", 1), ("user_id", 1)], unique=True)

    async def asyncTearDown(self):
        self.client.close()

    async def account(self, identity, **changes):
        doc = dict(id=identity, email=identity + "@example.test", is_admin=False,
                   is_premium=False, has_premium=False, trial_used=False,
                   trial_started_at=None, trial_expires_at=None, premium_expires_at=None)
        doc.update(changes)
        await self.db.users.insert_one(doc)
        return await self.db.users.find_one({"id": identity})

    async def claim(self, identity, **body):
        request = self.ns["CampaignRegisterRequest"](language="th", **body)
        response = await self.ns["register_campaign_user"](request, {"sub": identity})
        return response.status_code, json.loads(response.body)

    async def test_concurrent_last_seat_never_exceeds_50(self):
        await self.db.campaign_users.insert_many([
            dict(_id=f"free30-2026-10:seed-{n}", campaign_id="free30-2026-10", user_id=f"seed-{n}", campaign_index=n+1)
            for n in range(49)])
        identities = [f"candidate-{n}" for n in range(12)]
        for identity in identities:
            await self.account(identity)
        outcomes = await asyncio.gather(*(self.claim(identity) for identity in identities))
        winners = [body for status, body in outcomes if status == 200]
        self.assertEqual(len(winners), 1)
        self.assertEqual(winners[0]["campaign_index"], 50)
        self.assertEqual(winners[0]["remaining_seats"], 0)
        self.assertTrue(all(status == 200 or body.get("error") == "campaign_sold_out"
                            for status, body in outcomes))
        self.assertEqual(await self.db.campaign_users.count_documents({}), 50)
        self.assertEqual(await self.db.users.count_documents({"trial_used": True}), 1)
        user = await self.db.users.find_one({"trial_used": True})
        self.assertEqual(datetime.fromisoformat(user["trial_expires_at"]) -
                         datetime.fromisoformat(user["trial_started_at"]), timedelta(days=30))
        status = json.loads((await self.ns["get_campaign_status"]()).body)
        self.assertEqual((status["registered"], status["remaining"], status["is_active"]), (50, 0, False))

    async def test_concurrent_duplicate_account_gets_exactly_one_trial(self):
        await self.account("same-account")
        outcomes = await asyncio.gather(*(self.claim("same-account") for _ in range(10)))
        self.assertEqual(sum(status == 200 for status, _ in outcomes), 1)
        self.assertEqual(await self.db.campaign_users.count_documents({}), 1)
        before = await self.db.users.find_one({"id": "same-account"})
        status, body = await self.claim("same-account")
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "premium_already_active")
        self.assertEqual(before, await self.db.users.find_one({"id": "same-account"}))

    async def test_paid_lifetime_admin_and_used_trial_are_untouched(self):
        future = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        cases = {"paid": dict(is_premium=True, premium_expires_at=future),
                 "lifetime": dict(is_premium=True), "admin": dict(is_admin=True),
                 "used": dict(trial_used=True, trial_expires_at=(datetime.now(timezone.utc)-timedelta(days=1)).isoformat())}
        for identity, fields in cases.items():
            before = await self.account(identity, **fields)
            status, _ = await self.claim(identity)
            self.assertEqual(status, 400, identity)
            self.assertEqual(before, await self.db.users.find_one({"id": identity}), identity)
        self.assertEqual(await self.db.campaign_users.count_documents({}), 0)

    async def test_client_identity_cannot_grant_or_disclose_another_account(self):
        await self.account("caller")
        other = await self.account("other-learner")
        status, body = await self.claim("caller", email="other-learner@example.test", user_id="other-learner")
        self.assertEqual(status, 200)
        self.assertEqual(other, await self.db.users.find_one({"id": "other-learner"}))
        self.assertNotIn("other-learner", json.dumps(body))
        claim = await self.db.campaign_users.find_one({})
        self.assertEqual(claim["user_id"], "caller")
        self.assertFalse({"email", "name", "phone", "password"} & set(claim))

    async def test_failed_conditional_update_rolls_back_seat(self):
        before = await self.account("conflict", premium_expires_at=(datetime.now(timezone.utc)+timedelta(days=90)).isoformat())
        status, body = await self.claim("conflict")
        self.assertEqual(status, 409)
        self.assertEqual(body["error"], "trial_already_used")
        self.assertEqual(await self.db.campaign_users.count_documents({}), 0)
        self.assertEqual(before, await self.db.users.find_one({"id": "conflict"}))

    async def test_expired_trial_does_not_remove_paid_entitlement(self):
        past = (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
        future = (datetime.now(timezone.utc)+timedelta(days=90)).isoformat()
        trial_only = dict(trial_used=True, trial_expires_at=past, is_premium=False)
        paid = dict(trial_only, is_premium=True, premium_expires_at=future)
        lifetime = dict(trial_only, is_premium=True)
        self.assertFalse(self.ns["_user_has_active_premium"](trial_only))
        self.assertEqual(self.ns["_user_premium_status"](trial_only), "expired")
        self.assertTrue(trial_only["trial_used"])
        self.assertTrue(self.ns["_user_has_active_premium"](paid))
        self.assertEqual(self.ns["_access_expires_at"](paid), future)
        self.assertTrue(self.ns["_user_has_active_premium"](lifetime))
        self.assertIsNone(self.ns["_access_expires_at"](lifetime))


if __name__ == "__main__":
    unittest.main(verbosity=2)
