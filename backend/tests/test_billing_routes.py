"""
Offline tests for the payment flow and premium gates (server.py) plus paywall language (webapp.py).

Everything runs against an in-memory MongoDB (mongomock-motor) and a fake Stripe module:
no network, no real keys, no production database.

    cd backend && python -m pytest tests/test_billing_routes.py -v

Skipped only when server.py's own dependencies (or mongomock-motor) are missing.
"""

import hashlib
import hmac
import json
import os
import re
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:1/?serverSelectionTimeoutMS=200")
os.environ.setdefault("DB_NAME", "t2d_billing_test")

try:
    from fastapi.testclient import TestClient
    from mongomock_motor import AsyncMongoMockClient
    import server
    _IMPORT_ERROR = None
except Exception as exc:  # missing deps in this environment
    server = None
    _IMPORT_ERROR = exc

WEBAPP_SRC = (Path(__file__).parent.parent / "webapp.py").read_text(encoding="utf-8")

WEBHOOK_SECRET = "whsec_unit_test_secret"
RC_SECRET = "rc_unit_test_secret"
ADMIN_SECRET = "bootstrap_unit_test_secret"


def _iso(days):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _stripe_headers(payload: bytes, secret=WEBHOOK_SECRET):
    ts = int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return {"stripe-signature": f"t={ts},v1={sig}", "content-type": "application/json"}


class _Obj(dict):
    """dict with attribute access, like a stripe object."""
    __getattr__ = dict.get


@unittest.skipIf(server is None, f"server.py not importable here: {_IMPORT_ERROR!r}")
class BillingBase(unittest.TestCase):
    ENV = {}

    def setUp(self):
        self._orig_db = server.db
        server.db = AsyncMongoMockClient()["t2d_billing_test"]
        server._pricing_cache.update({"ts": 0.0, "data": None})
        keys = ["STRIPE_SECRET_KEY", "STRIPE_API_KEY", "STRIPE_LIVE_SECRET_KEY", "STRIPE_PRIVATE_KEY",
                "STRIPE_WEBHOOK_SECRET", "STRIPE_ENDPOINT_SECRET", "STRIPE_WEBHOOK_SIGNING_SECRET",
                "RC_WEBHOOK_SECRET", "RAILWAY_ENVIRONMENT", "RAILWAY_ENVIRONMENT_NAME", "ENVIRONMENT", "APP_ENV", "ENV"]
        self._env = patch.dict(os.environ, {**{k: "" for k in keys}, **self.ENV})
        self._env.start()
        self.client = TestClient(server.app)

    def tearDown(self):
        self._env.stop()
        server.db = self._orig_db

    # -- helpers --------------------------------------------------------------
    def db_run(self, coro):
        import asyncio
        return asyncio.new_event_loop().run_until_complete(coro)

    def add_user(self, uid="u1", **fields):
        doc = {"id": uid, "email": f"{uid}@example.com", "name": uid, **fields}
        self.db_run(server.db.users.insert_one(dict(doc)))
        return doc

    def get_user(self, uid="u1"):
        return self.db_run(server.db.users.find_one({"id": uid}, {"_id": 0}))

    def token(self, uid="u1", email=None, **claims):
        return server.create_token(uid, email or f"{uid}@example.com", **claims)

    def auth(self, uid="u1", **claims):
        return {"Authorization": f"Bearer {self.token(uid, **claims)}"}


# ══════════════════════════════════════════════════════════════════════════════
class StripeKeyIsolation(BillingBase):
    def test_only_live_secret_keys_are_accepted(self):
        for bad in ("sk_test_abc123", "rk_test_abc", "pk_live_abc", "whsec_abc", "garbage", ""):
            with patch.dict(os.environ, {"STRIPE_SECRET_KEY": bad}):
                self.assertEqual(server._get_live_stripe_secret_key(), "", bad)
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_live_abc123"}):
            self.assertEqual(server._get_live_stripe_secret_key(), "sk_live_abc123")

    def test_test_key_disables_stripe_module(self):
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_abc123"}):
            self.assertIsNone(server._stripe_module())

    def test_pricing_falls_back_and_never_leaks_secrets(self):
        r = self.client.get("/api/pricing")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual([p["amount"] for p in body["plans"]], [199, 399, 699])
        raw = json.dumps(body)
        for forbidden in ("sk_live", "sk_test", "whsec", "stripe_price\":"):
            self.assertNotIn(forbidden, raw)

    def test_checkout_requires_login(self):
        r = self.client.post("/api/create-checkout-session", json={"plan_id": "monthly"})
        self.assertIn(r.status_code, (401, 403))

    def test_checkout_fails_closed_without_live_key(self):
        self.add_user()
        r = self.client.post("/api/create-checkout-session", json={"plan_id": "monthly"}, headers=self.auth())
        self.assertEqual(r.status_code, 503)

    def test_checkout_fails_closed_with_test_key(self):
        self.add_user()
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_abc123"}):
            r = self.client.post("/api/create-checkout-session", json={"plan_id": "monthly"}, headers=self.auth())
        self.assertEqual(r.status_code, 503)

    def test_checkout_status_requires_login(self):
        self.assertIn(self.client.get("/api/checkout/status?session_id=cs_1").status_code, (401, 403))


# ══════════════════════════════════════════════════════════════════════════════
class CheckoutFlow(BillingBase):
    """create-checkout-session with a fake, live Stripe."""

    def _fake_stripe(self, price_live=True, session_live=True, calls=None):
        recurring = {"interval": "month"}

        class Session:
            @staticmethod
            def create(**kwargs):
                if calls is not None:
                    calls.append(kwargs)
                return _Obj(id="cs_live_1", url="https://checkout.stripe.com/c/pay/cs_live_1",
                            livemode=session_live, status="open")

        class Checkout:
            pass
        Checkout.Session = Session
        stripe = _Obj(checkout=Checkout)
        price = _Obj(id="price_live_1", livemode=price_live, recurring=recurring)
        pricing = {"source": "stripe_live", "plans": [{"id": "monthly", "stripe_price": price}]}
        return stripe, pricing

    def _post(self, body, **kw):
        stripe, pricing = self._fake_stripe(**kw)
        with patch.object(server, "_stripe_module", return_value=stripe), \
             patch.object(server, "_get_live_stripe_plan_prices_sync", return_value=pricing):
            return self.client.post("/api/create-checkout-session", json=body, headers=self.auth())

    def test_happy_path_uses_live_price_and_user_metadata(self):
        self.add_user(email="kunde@example.com")
        calls = []
        r = self._post({"plan_id": "monthly", "device_id": "dev-1"}, calls=calls)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["livemode"])
        kw = calls[0]
        self.assertEqual(kw["client_reference_id"], "u1")
        self.assertEqual(kw["metadata"]["user_id"], "u1")
        self.assertEqual(kw["metadata"]["plan_id"], "monthly")
        self.assertEqual(kw["line_items"], [{"price": "price_live_1", "quantity": 1}])
        self.assertFalse(kw["allow_promotion_codes"])

    def test_rejects_non_live_price(self):
        self.add_user()
        self.assertEqual(self._post({"plan_id": "monthly"}, price_live=False).status_code, 400)

    def test_rejects_non_live_session(self):
        self.add_user()
        self.assertEqual(self._post({"plan_id": "monthly"}, session_live=False).status_code, 500)

    def test_rejects_unknown_plan(self):
        self.add_user()
        r = self._post({"plan_id": "lifetime"})  # not in fake pricing
        self.assertIn(r.status_code, (400, 422))
        r = self._post({"plan_id": "free_forever"})
        self.assertIn(r.status_code, (400, 422))

    def test_open_redirect_urls_are_replaced_with_safe_defaults(self):
        self.add_user()
        calls = []
        r = self._post({"plan_id": "monthly", "success_url": "https://evil.example/steal?s={CHECKOUT_SESSION_ID}",
                        "cancel_url": "https://thai2drive.no.evil.example/x"}, calls=calls)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(calls[0]["success_url"].startswith("https://www.thai2drive.no/"))
        self.assertTrue(calls[0]["cancel_url"].startswith("https://www.thai2drive.no/"))

    def test_safe_return_url_rules(self):
        f = "/api/web?x=1"
        base = server._public_site_url() + f
        self.assertEqual(server._safe_return_url(None, f), base)
        self.assertEqual(server._safe_return_url("https://evil.example/a", f), base)
        self.assertEqual(server._safe_return_url("http://thai2drive.no/a", f), base)  # http not allowed in prod
        self.assertEqual(server._safe_return_url("javascript:alert(1)", f), base)
        self.assertEqual(server._safe_return_url("https://www.thai2drive.no/a", f), "https://www.thai2drive.no/a")
        self.assertEqual(server._safe_return_url("http://localhost:8000/a", f), "http://localhost:8000/a")

    def test_checkout_status_rejects_other_users_session(self):
        self.add_user()
        self.add_user("u2")
        sess = _Obj(id="cs_1", livemode=True, metadata={"user_id": "u2", "plan_id": "monthly"},
                    mode="payment", payment_status="paid", status="complete")
        stripe = _Obj(checkout=_Obj(Session=_Obj(retrieve=lambda sid: sess)))
        with patch.object(server, "_stripe_module", return_value=stripe):
            r = self.client.get("/api/checkout/status?session_id=cs_1", headers=self.auth("u1"))
        self.assertEqual(r.status_code, 403)
        self.assertFalse(self.get_user("u2").get("is_premium"))

    def test_checkout_status_rejects_test_mode_session(self):
        self.add_user()
        sess = _Obj(id="cs_1", livemode=False, metadata={"user_id": "u1", "plan_id": "lifetime"},
                    mode="payment", payment_status="paid")
        stripe = _Obj(checkout=_Obj(Session=_Obj(retrieve=lambda sid: sess)))
        with patch.object(server, "_stripe_module", return_value=stripe):
            r = self.client.get("/api/checkout/status?session_id=cs_1", headers=self.auth("u1"))
        self.assertEqual(r.status_code, 400)
        self.assertFalse(self.get_user().get("is_premium"))

    def test_checkout_status_unpaid_session_does_not_activate(self):
        self.add_user()
        sess = _Obj(id="cs_1", livemode=True, metadata={"user_id": "u1", "plan_id": "lifetime"},
                    mode="payment", payment_status="unpaid", status="open")
        stripe = _Obj(checkout=_Obj(Session=_Obj(retrieve=lambda sid: sess)))
        with patch.object(server, "_stripe_module", return_value=stripe):
            r = self.client.get("/api/checkout/status?session_id=cs_1", headers=self.auth("u1"))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["is_premium"])
        self.assertFalse(r.json()["activated"])

    def test_checkout_status_paid_live_session_activates_for_owner(self):
        self.add_user()
        sess = _Obj(id="cs_1", livemode=True, metadata={"user_id": "u1", "plan_id": "lifetime"},
                    mode="payment", payment_status="paid", status="complete", customer="cus_1")
        stripe = _Obj(checkout=_Obj(Session=_Obj(retrieve=lambda sid: sess)))
        with patch.object(server, "_stripe_module", return_value=stripe):
            r = self.client.get("/api/checkout/status?session_id=cs_1", headers=self.auth("u1"))
        self.assertTrue(r.json()["is_premium"])
        self.assertTrue(self.get_user()["premium_lifetime"])


# ══════════════════════════════════════════════════════════════════════════════
class StripeWebhook(BillingBase):
    ENV = {"STRIPE_SECRET_KEY": "sk_live_unit_test", "STRIPE_WEBHOOK_SECRET": WEBHOOK_SECRET}

    def _send(self, event, secret=WEBHOOK_SECRET):
        event = {"object": "event", **event}  # real Stripe events always carry object=event
        payload = json.dumps(event).encode()
        return self.client.post("/api/stripe/webhook", content=payload, headers=_stripe_headers(payload, secret))

    @staticmethod
    def _checkout_event(uid="u1", plan="lifetime", live=True, paid="paid", eid="evt_1", mode="payment"):
        return {"id": eid, "type": "checkout.session.completed", "livemode": live,
                "data": {"object": {"id": "cs_1", "mode": mode, "payment_status": paid, "customer": "cus_1",
                                    "metadata": {"user_id": uid, "plan_id": plan}}}}

    def test_not_configured_returns_503(self):
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": ""}):
            r = self.client.post("/api/stripe/webhook", content=b"{}")
        self.assertEqual(r.status_code, 503)

    def test_missing_or_wrong_signature_is_rejected(self):
        self.add_user()
        payload = json.dumps({"object": "event", **self._checkout_event()}).encode()
        self.assertEqual(self.client.post("/api/stripe/webhook", content=payload).status_code, 400)
        r = self.client.post("/api/stripe/webhook", content=payload, headers=_stripe_headers(payload, "whsec_wrong"))
        self.assertEqual(r.status_code, 400)
        self.assertFalse(self.get_user().get("is_premium"))

    def test_tampered_payload_is_rejected(self):
        self.add_user()
        payload = json.dumps({"object": "event", **self._checkout_event()}).encode()
        headers = _stripe_headers(payload)
        tampered = payload.replace(b"lifetime", b"monthly")
        self.assertEqual(self.client.post("/api/stripe/webhook", content=tampered, headers=headers).status_code, 400)

    def test_paid_live_checkout_grants_lifetime_premium(self):
        self.add_user()
        r = self._send(self._checkout_event())
        self.assertEqual(r.status_code, 200)
        u = self.get_user()
        self.assertTrue(u["is_premium"])
        self.assertTrue(u["premium_lifetime"])
        self.assertEqual(u["premium_source"], "stripe")
        self.assertNotIn("premium_expires_at", u)

    def test_three_month_payment_expires_after_about_90_days(self):
        self.add_user()
        self._send(self._checkout_event(plan="three_months"))
        exp = datetime.fromisoformat(self.get_user()["premium_expires_at"])
        self.assertAlmostEqual((exp - datetime.now(timezone.utc)).days, 89, delta=1)

    def test_unpaid_checkout_does_not_grant_premium(self):
        self.add_user()
        self._send(self._checkout_event(paid="unpaid"))
        self.assertFalse(self.get_user().get("is_premium"))

    def test_test_mode_event_is_ignored_even_with_valid_signature(self):
        self.add_user()
        r = self._send(self._checkout_event(live=False))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("reason"), "test_mode_event")
        self.assertFalse(self.get_user().get("is_premium"))

    def test_unknown_plan_or_user_grants_nothing(self):
        self.add_user()
        self._send(self._checkout_event(plan="platinum", eid="e2"))
        self._send(self._checkout_event(uid="ghost", eid="e3"))
        self.assertFalse(self.get_user().get("is_premium"))

    def test_replayed_event_is_idempotent(self):
        self.add_user()
        self.assertFalse(self._send(self._checkout_event()).json().get("skipped"))
        self.assertTrue(self._send(self._checkout_event()).json().get("skipped"))

    def test_subscription_deleted_revokes_subscriber_but_not_lifetime(self):
        self.add_user("sub", is_premium=True, stripe_subscription_id="sub_1", premium_status="active")
        self.add_user("life", is_premium=True, premium_lifetime=True, stripe_subscription_id="sub_2")
        for uid, sid in (("sub", "sub_1"), ("life", "sub_2")):
            self._send({"id": f"evt_del_{uid}", "type": "customer.subscription.deleted", "livemode": True,
                        "data": {"object": {"id": sid, "customer": "cus", "metadata": {"user_id": uid}}}})
        self.assertFalse(self.get_user("sub")["is_premium"])
        self.assertTrue(self.get_user("life")["is_premium"])


# ══════════════════════════════════════════════════════════════════════════════
class RevenueCatWebhook(BillingBase):
    ENV = {"RC_WEBHOOK_SECRET": RC_SECRET}

    def _send(self, event, secret=RC_SECRET, raw=None):
        headers = {"Authorization": f"Bearer {secret}"} if secret is not None else {}
        body = raw if raw is not None else json.dumps({"event": event}).encode()
        return self.client.post("/api/webhooks/revenuecat", content=body, headers=headers)

    @staticmethod
    def _event(kind="INITIAL_PURCHASE", uid="u1", eid="rc_1", env="PRODUCTION", entitlements=("pro",), days=30):
        ev = {"type": kind, "id": eid, "app_user_id": uid, "product_id": "t2d_monthly",
              "environment": env, "entitlement_ids": list(entitlements)}
        if days is not None:
            ev["expiration_at_ms"] = int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp() * 1000)
        return ev

    def test_not_configured_returns_503(self):
        with patch.dict(os.environ, {"RC_WEBHOOK_SECRET": ""}):
            self.assertEqual(self._send(self._event()).status_code, 503)

    def test_wrong_or_missing_secret_is_rejected(self):
        self.add_user()
        self.assertEqual(self._send(self._event(), secret="nope").status_code, 401)
        self.assertEqual(self._send(self._event(), secret=None).status_code, 401)
        self.assertFalse(self.get_user().get("is_premium"))

    def test_invalid_json_is_400(self):
        self.assertEqual(self._send(None, raw=b"not json").status_code, 400)

    def test_purchase_grants_premium_until_expiry(self):
        self.add_user()
        self.assertEqual(self._send(self._event()).status_code, 200)
        u = self.get_user()
        self.assertTrue(u["is_premium"])
        self.assertEqual(u["premium_source"], "revenuecat")
        self.assertIn("premium_expires_at", u)

    def test_non_premium_entitlement_is_ignored(self):
        self.add_user()
        r = self._send(self._event(entitlements=("other",)))
        self.assertEqual(r.json().get("reason"), "non_premium_entitlement")
        self.assertFalse(self.get_user().get("is_premium"))

    def test_sandbox_event_is_ignored_in_production(self):
        self.add_user()
        with patch.dict(os.environ, {"RAILWAY_ENVIRONMENT": "production"}):
            r = self._send(self._event(env="SANDBOX"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("reason"), "sandbox_event_in_production")
        self.assertFalse(self.get_user().get("is_premium"))

    def test_sandbox_event_is_still_processed_outside_production(self):
        self.add_user()
        self._send(self._event(env="SANDBOX"))
        self.assertTrue(self.get_user()["is_premium"])

    def test_production_event_is_processed_in_production(self):
        self.add_user()
        with patch.dict(os.environ, {"RAILWAY_ENVIRONMENT": "production"}):
            self._send(self._event(env="PRODUCTION"))
        self.assertTrue(self.get_user()["is_premium"])

    def test_unknown_user_is_acknowledged_without_grant(self):
        r = self._send(self._event(uid="ghost"))
        self.assertEqual(r.json().get("reason"), "user_not_found")

    def test_replay_is_idempotent(self):
        self.add_user()
        self._send(self._event())
        self.assertTrue(self._send(self._event()).json().get("skipped"))

    def test_expiration_and_refund_revoke(self):
        for kind in ("EXPIRATION", "REFUND"):
            uid = f"u_{kind}"
            self.add_user(uid, is_premium=True)
            self._send(self._event(kind, uid=uid, eid=f"rc_{kind}", days=None))
            self.assertFalse(self.get_user(uid)["is_premium"], kind)

    def test_cancellation_keeps_access_until_expiry(self):
        self.add_user(is_premium=True)
        self._send(self._event("CANCELLATION", days=10))
        u = self.get_user()
        self.assertTrue(u["is_premium"])
        self.assertEqual(u["premium_status"], "canceled")


# ══════════════════════════════════════════════════════════════════════════════
class PremiumGates(BillingBase):
    """Backend is the source of truth: expired, revoked or forged premium must not pass."""

    def _consume(self, headers, n, device="dev-1"):
        codes = []
        for i in range(n):
            r = self.client.post("/api/access/consume", headers=headers,
                                 json={"device_id": device, "question_id": f"q{i}", "event_id": f"{device}-{i}"})
            codes.append(r.status_code)
        return codes

    def test_paid_premium_active_table(self):
        f = server._paid_premium_active
        self.assertFalse(f(None))
        self.assertFalse(f({"is_premium": False}))
        self.assertTrue(f({"is_premium": True}))                                    # lifetime
        self.assertTrue(f({"is_premium": True, "premium_expires_at": _iso(5)}))
        self.assertFalse(f({"is_premium": True, "premium_expires_at": _iso(-1)}))   # expired
        self.assertFalse(f({"is_premium": True, "premium_expires_at": "garbage"}))  # fail closed

    def test_guest_gets_five_then_402(self):
        codes = self._consume({}, 6)
        self.assertEqual(codes, [200] * 5 + [402])

    def test_registered_free_user_gets_ten_per_day(self):
        self.add_user()
        codes = self._consume(self.auth(is_premium=False), 11)
        self.assertEqual(codes, [200] * 10 + [402])

    def test_expired_premium_is_treated_as_free(self):
        self.add_user(is_premium=True, premium_expires_at=_iso(-2))
        h = self.auth(is_premium=True, premium_until=_iso(-2))
        st = self.client.get("/api/access/status?device_id=d", headers=h).json()
        self.assertEqual(st["tier"], "registered")
        self.assertEqual(self._consume(h, 11, "d")[-1], 402)

    def test_active_premium_is_unlimited(self):
        self.add_user(is_premium=True, premium_expires_at=_iso(20))
        h = self.auth(is_premium=True, premium_until=_iso(20))
        self.assertEqual(self._consume(h, 15), [200] * 15)
        self.assertEqual(self.client.get("/api/access/status?device_id=d", headers=h).json()["tier"], "premium")

    def test_database_revocation_beats_a_stale_premium_token(self):
        self.add_user(is_premium=False)  # refunded/expired after the token was minted
        h = self.auth(is_premium=True, premium_until=_iso(30))
        self.assertEqual(self.client.get("/api/access/status?device_id=d", headers=h).json()["tier"], "registered")

    def test_garbage_and_wrongly_signed_tokens_are_treated_as_guest(self):
        self.add_user(is_premium=True)
        forged = server.jwt.encode({"sub": "u1", "email": "u1@example.com", "is_premium": True,
                                    "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                                   "not-the-real-secret", algorithm=server.JWT_ALGORITHM)
        for token in ("garbage", forged):
            st = self.client.get("/api/access/status?device_id=x", headers={"Authorization": f"Bearer {token}"}).json()
            self.assertEqual(st["tier"], "guest", token[:12])

    def test_auth_me_reflects_expired_premium(self):
        self.add_user(is_premium=True, premium_expires_at=_iso(-1))
        me = self.client.get("/api/auth/me", headers=self.auth(is_premium=True)).json()
        self.assertFalse(me["is_premium"])

    def test_auth_me_rejects_invalid_token(self):
        self.assertEqual(self.client.get("/api/auth/me", headers={"Authorization": "Bearer nope"}).status_code, 401)

    def test_premium_features_flags_follow_tier(self):
        st = self.client.get("/api/access/status?device_id=x").json()
        self.assertFalse(st["features"]["exam_mode"])
        self.assertFalse(st["is_premium"])


# ══════════════════════════════════════════════════════════════════════════════
class AdminBootstrapRoute(BillingBase):
    def test_route_is_closed_without_secret(self):
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", ""):
            r = self.client.get("/api/admin-setup-t2d")
        self.assertEqual(r.status_code, 403)
        self.assertIsNone(self.db_run(server.db.users.find_one({"email": "admin@thai2drive.com"})))

    def test_route_is_closed_with_wrong_secret(self):
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", ADMIN_SECRET):
            r = self.client.get("/api/admin-setup-t2d", headers={"X-Admin-Secret": "wrong"})
        self.assertEqual(r.status_code, 403)
        self.assertIsNone(self.db_run(server.db.admin_users.find_one({"email": "admin@thai2drive.com"})))

    def test_no_default_password_is_ever_set(self):
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", ADMIN_SECRET):
            r = self.client.get("/api/admin-setup-t2d", headers={"X-Admin-Secret": ADMIN_SECRET})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertNotIn("admin123", json.dumps(body))
        self.assertGreaterEqual(len(body["password"]), 16)
        user = self.db_run(server.db.users.find_one({"email": "admin@thai2drive.com"}))
        self.assertTrue(server.pwd_context.verify(body["password"], user["password_hash"]))
        self.assertFalse(server.pwd_context.verify("admin123", user["password_hash"]))

    def test_source_no_longer_contains_the_hardcoded_password(self):
        self.assertNotIn('password = "admin123"', Path(server.__file__).read_text(encoding="utf-8"))


# ══════════════════════════════════════════════════════════════════════════════
class AdminStartupSeeding(BillingBase):
    """Startup must never (re)set a default admin password."""

    def _startup(self, **env):
        with patch.dict(os.environ, {"ADMIN_INITIAL_PASSWORD": "", **env}):
            self.db_run(server.seed_studiebok())

    def _admin(self):
        return self.db_run(server.db.users.find_one({"email": "admin@thai2drive.com"}))

    def test_default_password_is_not_created_on_a_fresh_database(self):
        self._startup()
        self.assertIsNone(self._admin())
        self.assertIsNone(self.db_run(server.db.admin_users.find_one({"email": "admin@thai2drive.com"})))

    def test_existing_default_password_is_disabled_on_startup(self):
        self.db_run(server.db.users.insert_one({
            "id": "adm", "email": "admin@thai2drive.com", "is_admin": True, "is_premium": True,
            "password_hash": server.pwd_context.hash("admin123")}))
        self._startup()
        self.assertFalse(server.pwd_context.verify("admin123", self._admin()["password_hash"]))

    def test_strong_existing_admin_password_is_left_alone(self):
        h = server.pwd_context.hash("a-long-unique-passphrase-42")
        self.db_run(server.db.users.insert_one({"id": "adm", "email": "admin@thai2drive.com", "password_hash": h}))
        self._startup()
        self.assertEqual(self._admin()["password_hash"], h)

    def test_admin_is_created_only_from_a_long_env_password(self):
        self._startup(ADMIN_INITIAL_PASSWORD="short")
        self.assertIsNone(self._admin())
        self._startup(ADMIN_INITIAL_PASSWORD="a-long-initial-passphrase")
        admin = self._admin()
        self.assertTrue(server.pwd_context.verify("a-long-initial-passphrase", admin["password_hash"]))
        self.assertFalse(server.pwd_context.verify("admin123", admin["password_hash"]))

    def test_source_has_no_hardcoded_default_admin_password(self):
        src = Path(server.__file__).read_text(encoding="utf-8")
        self.assertNotIn('password = "admin123"', src)
        self.assertNotIn('admin_password = "admin123"', src)


# ══════════════════════════════════════════════════════════════════════════════
class PaywallLanguage(unittest.TestCase):
    """Static checks of the paywall text: Thai only (Norwegian terms in parentheses), no English leaks."""

    KEY_RE = re.compile(r"^\s*(?P<key>(?:pw_|trial_|promo_|premium_|payment_|checkout_|free_questions)[a-z0-9_]*|upgrade)\s*:\s*"
                        r"\{th:'(?P<th>(?:[^'\\]|\\.)*)',\s*no:'(?P<no>(?:[^'\\]|\\.)*)',\s*en:'(?P<en>(?:[^'\\]|\\.)*)'\}",
                        re.M)
    THAI = re.compile(r"[฀-๿]")
    LATIN = re.compile(r"[A-Za-zÆØÅæøå]")
    PAREN = re.compile(r"\(([^()]*)\)")
    PLACEHOLDER = re.compile(r"\{[a-z]+\}")
    ENGLISH = re.compile(r"\b(the|and|you|your|with|free|unlock|monthly|lifetime|months?|cancel|anytime|buy|restore|"
                         r"purchase|trial|price|pay|once|forever|access|questions)\b", re.I)

    @classmethod
    def entries(cls):
        return {m["key"]: m.groupdict() for m in cls.KEY_RE.finditer(WEBAPP_SRC)}

    def test_all_paywall_keys_are_present(self):
        e = self.entries()
        for k in ("pw_title", "pw_sub", "pw_f1", "pw_f2", "pw_f3", "pw_f4", "pw_f5", "pw_month", "pw_three_months",
                  "pw_lifetime", "pw_lifetime_note", "pw_best_value", "pw_currency", "pw_buy", "pw_restore_purchase",
                  "pw_cancel_anytime", "premium_activated_toast", "payment_unconfirmed_toast",
                  "checkout_unavailable_toast", "trial_ended"):
            self.assertIn(k, e, k)
        self.assertGreaterEqual(len(e), 25)

    def test_thai_text_is_thai_with_latin_only_inside_parentheses(self):
        for k, v in self.entries().items():
            th = self.PLACEHOLDER.sub("", v["th"])
            self.assertTrue(self.THAI.search(th), f"{k}: ingen thai")
            outside = self.PAREN.sub("", th)
            self.assertIsNone(self.LATIN.search(outside), f"{k}: latinske bokstaver utenfor parentes: {v['th']}")
            for term in self.PAREN.findall(th):
                if self.LATIN.search(term):
                    self.assertIsNone(self.THAI.search(term), f"{k}: thai inne i fagord-parentes: {term}")
                    self.assertIsNone(self.ENGLISH.search(term), f"{k}: engelsk i fagord: {term}")

    def test_norwegian_text_has_no_thai_and_no_english_words(self):
        for k, v in self.entries().items():
            self.assertIsNone(self.THAI.search(v["no"]), f"{k}: thai i norsk tekst")
            self.assertIsNone(self.ENGLISH.search(v["no"]), f"{k}: engelsk ord i norsk tekst: {v['no']}")

    def test_placeholders_match_across_languages(self):
        for k, v in self.entries().items():
            sets = {lang: set(self.PLACEHOLDER.findall(v[lang])) for lang in ("th", "no", "en")}
            self.assertEqual(sets["th"], sets["no"], k)
            self.assertEqual(sets["th"], sets["en"], k)

    def test_key_purchase_terms_carry_norwegian_term_in_parentheses(self):
        e = self.entries()
        expected = {"pw_month": "månedlig", "pw_three_months": "3 måneder", "pw_lifetime": "livstid",
                    "pw_lifetime_note": "engangsbetaling", "pw_restore_purchase": "gjenopprett kjøp",
                    "pw_cancel_anytime": "avslutt når som helst", "pw_f5": "trafikkskilt", "pw_f2": "eksamensmodus"}
        for k, term in expected.items():
            self.assertIn(f"({term})", e[k]["th"], k)

    def test_price_is_formatted_per_language_without_nok_or_english(self):
        p = self.entries()["pw_currency"]
        self.assertEqual(p["th"], "โครน (kr)")
        self.assertEqual(p["no"], "kr")
        self.assertIn("pwTerm(t('pw_currency'))", WEBAPP_SRC)
        start = WEBAPP_SRC.index('id="screenPaywall"')
        html = WEBAPP_SRC[start:start + 4000]
        self.assertNotIn("NOK", html)
        fallback = WEBAPP_SRC[WEBAPP_SRC.index("var PREMIUM_PRICING"):][:600]
        self.assertNotIn("NOK", fallback)
        self.assertNotIn("display:", fallback)

    def test_save_percentage_is_computed_not_hardcoded(self):
        e = self.entries()["pw_best_value"]
        for lang in ("th", "no", "en"):
            self.assertIn("{pct}", e[lang])
            self.assertNotIn("34", e[lang])
        self.assertIn("Math.round((1 - m3 / (3 * m1)) * 100)", WEBAPP_SRC)
        # with the fallback prices 199 / 399 the honest number is 33 %, not 34 %
        self.assertEqual(round((1 - 399 / (3 * 199)) * 100), 33)

    def test_premium_toast_has_no_bare_latin_in_thai(self):
        th = self.entries()["premium_activated_toast"]["th"]
        self.assertNotIn("Premium แล้ว", th)
        self.assertIn("(Premium)", th)


if __name__ == "__main__":
    unittest.main()
