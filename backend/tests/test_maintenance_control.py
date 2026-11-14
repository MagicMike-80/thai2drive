"""Local ASGI tests; no production database or account is used."""
import asyncio
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from maintenance_control import OWNER_EMAIL, create_maintenance


class Collection:
    def __init__(self, kind):
        self.kind = kind
        self.doc = None

    async def find_one(self, query, projection=None):
        if self.kind == "settings":
            return self.doc
        if self.kind == "users":
            return {"id": "owner"} if query == {"id": "owner", "email": OWNER_EMAIL} else None
        return {"email": OWNER_EMAIL} if query.get("email") == OWNER_EMAIL else None

    async def update_one(self, query, update, upsert=False):
        if self.doc is None:
            self.doc = {"_id": query["_id"], "events": []}
        self.doc.update(update["$set"])
        self.doc["events"].extend(update["$push"]["events"]["$each"])


class Database:
    def __init__(self):
        self.system_settings = Collection("settings")
        self.users = Collection("users")
        self.admin_users = Collection("admins")


def test_pause_owner_recovery_and_api_enforcement():
    async def run():
        db = Database()
        tokens = {"owner-token": {"sub": "owner", "email": OWNER_EMAIL},
                  "other-admin": {"sub": "other", "email": "admin@example.test"}}
        router, gate = create_maintenance(db, tokens.get)
        app = FastAPI()
        app.middleware("http")(gate)
        app.include_router(router)
        for path in ("/api/questions", "/api/teacher/chat", "/micro-lessons", "/lessons/culture", "/quiz/terms", "/no/flipp-flopp", "/bok", "/api/assets/flipp_flopp_cards.json", "/api/public_assets/flipp_flopp_cards.json", "/assets/flipp_flopp_cards.json", "/public_assets/flipp_flopp_cards.json", "/api/stripe/webhook", "/api/webhooks/revenuecat", "/api/create-checkout-session", "/api/checkout/status", "/api/billing/subscription", "/api/no/app", "/api/th/app", "/api/en/app", "/api/auth/login", "/app", "/admin"):
            app.add_api_route(path, lambda: {"ok": True}, methods=["GET", "POST"])
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            owner = {"Authorization": "Bearer owner-token"}
            other = {"Authorization": "Bearer other-admin"}
            assert (await client.get("/api/questions")).status_code == 200
            assert (await client.post("/api/admin/maintenance", json={"active": True}, headers=owner)).status_code == 400
            assert (await client.post("/api/admin/maintenance", json={"active": True, "confirmed": True})).status_code == 403
            assert (await client.post("/api/admin/maintenance", json={"active": True, "confirmed": True}, headers=other)).status_code == 403
            assert (await client.post("/api/admin/maintenance", json={"active": True, "confirmed": True}, headers=owner)).status_code == 200
            for path in ("/api/questions", "/api/teacher/chat", "/micro-lessons", "/lessons/culture", "/quiz/terms", "/api/assets/flipp_flopp_cards.json", "/api/public_assets/flipp_flopp_cards.json", "/assets/flipp_flopp_cards.json", "/public_assets/flipp_flopp_cards.json"):
                assert (await client.get(path)).status_code == 503
                assert (await client.get(path, headers=other)).status_code == 503
                assert (await client.get(path, headers=owner)).status_code == 200
            assert "location.replace(back)" in (await client.get('/no/flipp-flopp')).text
            assert "location.replace(back)" in (await client.get('/bok')).text
            assert (await client.get('/no/flipp-flopp', headers=other)).status_code == 503
            assert (await client.get('/no/flipp-flopp', headers=owner)).json() == {'ok': True}
            for path in ("/api/stripe/webhook", "/api/webhooks/revenuecat", "/api/create-checkout-session", "/api/checkout/status", "/api/billing/subscription", "/api/no/app", "/api/th/app", "/api/en/app", "/api/auth/login", "/app", "/admin"):
                assert (await client.get(path)).status_code == 200
            assert (await client.post('/api/stripe/webhook')).status_code == 200
            assert (await client.post('/api/webhooks/revenuecat')).status_code == 200
            assert (await client.get("/api/maintenance/status")).json() == {"active": True, "owner": False}
            assert (await client.get("/api/maintenance/status", headers=owner)).json() == {"active": True, "owner": True}
            assert (await client.post("/api/admin/maintenance", json={"active": False}, headers=owner)).status_code == 200
            assert (await client.get("/api/questions")).status_code == 200
            assert [event["active"] for event in db.system_settings.doc["events"]] == [True, False]
    asyncio.run(run())


def test_database_failure_does_not_open_the_gate_or_prevent_recovery_routes():
    async def run():
        db = Database()
        async def fail(*args, **kwargs):
            raise RuntimeError("simulated database failure")
        db.system_settings.find_one = fail
        router, gate = create_maintenance(db, lambda _: None)
        app = FastAPI()
        app.middleware("http")(gate)
        app.include_router(router)
        app.add_api_route("/api/questions", lambda: {"ok": True})
        app.add_api_route("/api/stripe/webhook", lambda: {"ok": True}, methods=["POST"])
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/api/questions")).status_code == 503
            assert (await client.get("/api/maintenance/status")).status_code == 503
            assert (await client.post("/api/stripe/webhook")).status_code == 200
    asyncio.run(run())
