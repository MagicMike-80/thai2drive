"""
Offline tests for locked admin routes (/api/seed, /api/admin/check), the AI paywall
(premium_gate.require_active_premium) and repo hygiene (frontend/.env not tracked).

In-memory MongoDB (mongomock-motor); no network, no real keys, no production database.

    cd backend && python -m pytest tests/test_route_security.py -v

The route tests are skipped only when server.py's own dependencies are missing.
"""

import json
import os
import re
import subprocess
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:1/?serverSelectionTimeoutMS=200")
os.environ.setdefault("DB_NAME", "t2d_security_test")

try:
    from fastapi.testclient import TestClient
    from mongomock_motor import AsyncMongoMockClient
    import server
    import ai_routes
    _IMPORT_ERROR = None
except Exception as exc:  # missing deps in this environment
    server = ai_routes = None
    _IMPORT_ERROR = exc

BACKEND = Path(__file__).resolve().parent.parent
REPO = BACKEND.parent
SECRET = "bootstrap_unit_test_secret"


def _iso(days):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


@unittest.skipIf(server is None, f"server.py not importable here: {_IMPORT_ERROR!r}")
class SecurityBase(unittest.TestCase):
    def setUp(self):
        self._orig_db, self._orig_ai_db = server.db, ai_routes._db
        server.db = AsyncMongoMockClient()["t2d_security_test"]
        ai_routes._db = server.db
        self._env = patch.dict(os.environ, {"RAILWAY_ENVIRONMENT": "", "ENVIRONMENT": ""})
        self._env.start()
        self.client = TestClient(server.app)

    def tearDown(self):
        self._env.stop()
        server.db, ai_routes._db = self._orig_db, self._orig_ai_db

    def run_db(self, coro):
        import asyncio
        return asyncio.new_event_loop().run_until_complete(coro)

    def add_user(self, uid="u1", **fields):
        self.run_db(server.db.users.insert_one({"id": uid, "email": f"{uid}@example.com", "name": uid, **fields}))

    def make_admin(self, uid="adm"):
        self.add_user(uid, is_admin=True)
        self.run_db(server.db.admin_users.insert_one({"email": f"{uid}@example.com"}))

    def auth(self, uid="u1", **claims):
        return {"Authorization": f"Bearer {server.create_token(uid, f'{uid}@example.com', **claims)}"}

    def questions(self):
        return self.run_db(server.db.questions.count_documents({}))


# ══════════════════════════════════════════════════════════════════════════════
class SeedIsLocked(SecurityBase):
    def test_unauthenticated_seed_is_blocked_and_writes_nothing(self):
        r = self.client.post("/api/seed")
        self.assertIn(r.status_code, (401, 403))
        self.assertEqual(self.questions(), 0)

    def test_garbage_token_is_blocked(self):
        r = self.client.post("/api/seed", headers={"Authorization": "Bearer garbage"})
        self.assertIn(r.status_code, (401, 403))
        self.assertEqual(self.questions(), 0)

    def test_wrong_bootstrap_secret_is_blocked(self):
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", SECRET):
            r = self.client.post("/api/seed", headers={"X-Admin-Secret": "wrong"})
        self.assertIn(r.status_code, (401, 403))
        self.assertEqual(self.questions(), 0)

    def test_unset_secret_never_matches_an_empty_header(self):
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", ""):
            r = self.client.post("/api/seed", headers={"X-Admin-Secret": ""})
        self.assertIn(r.status_code, (401, 403))
        self.assertFalse(server._bootstrap_secret_ok(""))
        self.assertFalse(server._bootstrap_secret_ok("anything"))

    def test_regular_logged_in_user_is_forbidden(self):
        self.add_user()
        r = self.client.post("/api/seed", headers=self.auth("u1", is_premium=True))
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.questions(), 0)

    def test_admin_token_can_seed(self):
        self.make_admin()
        r = self.client.post("/api/seed", headers=self.auth("adm"))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["seeded"])
        self.assertGreater(self.questions(), 0)

    def test_bootstrap_secret_can_seed_and_second_call_is_noop(self):
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", SECRET):
            first = self.client.post("/api/seed", headers={"X-Admin-Secret": SECRET})
            n = self.questions()
            second = self.client.post("/api/seed", headers={"X-Admin-Secret": SECRET})
        self.assertTrue(first.json()["seeded"])
        self.assertFalse(second.json()["seeded"])
        self.assertEqual(self.questions(), n)


class AdminCheckIsLocked(SecurityBase):
    def test_unauthenticated_check_is_blocked(self):
        r = self.client.post("/api/admin/check", json={"email": "admin@thai2drive.com"})
        self.assertIn(r.status_code, (401, 403))

    def test_regular_user_cannot_enumerate_admins(self):
        self.add_user()
        r = self.client.post("/api/admin/check", json={"email": "admin@thai2drive.com"}, headers=self.auth())
        self.assertEqual(r.status_code, 403)

    def test_admin_token_and_secret_get_a_real_answer(self):
        self.make_admin()
        h = self.auth("adm")
        self.assertTrue(self.client.post("/api/admin/check", json={"email": "adm@example.com"}, headers=h).json()["is_admin"])
        self.assertFalse(self.client.post("/api/admin/check", json={"email": "nobody@example.com"}, headers=h).json()["is_admin"])
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", SECRET):
            r = self.client.post("/api/admin/check", json={"email": "adm@example.com"}, headers={"X-Admin-Secret": SECRET})
        self.assertTrue(r.json()["is_admin"])

    def test_admin_add_still_needs_the_secret(self):
        with patch.object(server, "ADMIN_BOOTSTRAP_SECRET", SECRET):
            self.assertEqual(self.client.post("/api/admin/add", json={"email": "x@example.com"}).status_code, 403)
            ok = self.client.post("/api/admin/add", json={"email": "x@example.com"}, headers={"X-Admin-Secret": SECRET})
        self.assertEqual(ok.status_code, 200)


# ══════════════════════════════════════════════════════════════════════════════
class AiRoutesPaywall(SecurityBase):
    """Every AI answer route must reject callers without active access (HTTP 402)."""

    GATED = [
        ("GET", "/api/ai/explanation/q1", None),
        ("GET", "/api/ai/smart-practice/dev1", None),
        ("GET", "/api/ai/dashboard/dev1", None),
        ("POST", "/api/teacher/chat", {}),   # empty body: a caller that passes the gate gets 422, not 402
    ]

    def call(self, method, path, body, headers=None):
        return self.client.request(method, path, json=body, headers=headers or {})

    def assert_all_blocked(self, headers=None, error=None):
        for method, path, body in self.GATED:
            r = self.call(method, path, body, headers)
            self.assertEqual(r.status_code, 402, f"{method} {path}: {r.status_code} {r.text[:120]}")
            if error:
                self.assertEqual(r.json()["detail"]["error"], error, path)

    def assert_all_pass_gate(self, headers):
        for method, path, body in self.GATED:
            r = self.call(method, path, body, headers)
            self.assertNotIn(r.status_code, (401, 402, 403), f"{method} {path}: {r.status_code} {r.text[:120]}")

    # -- blocked -------------------------------------------------------------
    def test_unauthenticated_calls_are_rejected(self):
        self.assert_all_blocked(error="auth_required")

    def test_garbage_and_forged_tokens_are_rejected(self):
        forged = server.jwt.encode({"sub": "u1", "email": "u1@example.com", "is_premium": True,
                                    "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                                   "not-the-real-secret", algorithm=server.JWT_ALGORITHM)
        self.add_user(is_premium=True)
        for token in ("garbage", forged):
            self.assert_all_blocked({"Authorization": f"Bearer {token}"}, error="auth_required")

    def test_registered_free_user_is_rejected(self):
        self.add_user()
        self.assert_all_blocked(self.auth(), error="premium_required")

    def test_expired_paid_subscription_is_rejected(self):
        self.add_user(is_premium=True, premium_expires_at=_iso(-3))
        self.assert_all_blocked(self.auth(is_premium=True, premium_until=_iso(-3)), error="premium_required")

    def test_expired_trial_is_rejected(self):
        self.add_user(trial_expires_at=_iso(-1))
        self.assert_all_blocked(self.auth(), error="premium_required")

    def test_database_revocation_beats_a_stale_premium_token(self):
        self.add_user(is_premium=False)  # refunded or expired after the token was minted
        self.assert_all_blocked(self.auth(is_premium=True, premium_until=_iso(30)), error="premium_required")

    def test_token_for_a_deleted_user_is_rejected(self):
        self.assert_all_blocked(self.auth("ghost", is_premium=True), error="auth_required")

    def test_rejection_detail_matches_the_apps_gate_contract(self):
        self.add_user()
        d = self.call("GET", "/api/ai/explanation/q1", None, self.auth()).json()["detail"]
        self.assertEqual((d["gate"], d["tier"]), ("upgrade", "registered"))
        d = self.call("GET", "/api/ai/explanation/q1", None).json()["detail"]
        self.assertEqual((d["gate"], d["tier"]), ("register", "guest"))

    # -- allowed -------------------------------------------------------------
    def test_paid_subscriber_passes(self):
        self.add_user(is_premium=True, premium_expires_at=_iso(20))
        self.assert_all_pass_gate(self.auth(is_premium=True))

    def test_lifetime_subscriber_passes(self):
        self.add_user(is_premium=True, premium_lifetime=True)
        self.assert_all_pass_gate(self.auth(is_premium=True))

    def test_active_free_week_passes_as_the_app_promises(self):
        self.add_user(trial_expires_at=_iso(3))
        self.assert_all_pass_gate(self.auth())

    def test_admin_passes(self):
        self.add_user("adm", is_admin=True)
        self.assert_all_pass_gate(self.auth("adm"))

    def test_launch_promo_opens_the_gate_for_logged_in_users_only(self):
        self.add_user()
        with patch.object(server, "free_promo_active", return_value=True):
            self.assert_all_pass_gate(self.auth())
            self.assert_all_blocked(error="auth_required")  # guests never get in

    # -- deliberately open ---------------------------------------------------
    def test_attempt_tracking_and_coaching_banner_stay_open_for_guests(self):
        self.assertNotEqual(self.client.post("/api/ai/attempt", json={}).status_code, 402)
        self.assertNotEqual(self.client.get("/api/ai/coaching/dev1").status_code, 402)

    def test_teacher_metadata_routes_stay_open(self):
        for path in ("/api/teacher/topics", "/api/teacher/status"):
            self.assertNotEqual(self.client.get(path).status_code, 402, path)

    # -- wiring --------------------------------------------------------------
    def test_gate_is_declared_on_exactly_the_intended_routes(self):
        gated = set()
        for route in server.app.routes:
            deps = [getattr(d.call, "__name__", type(d.call).__name__) for d in getattr(route, "dependant", None).dependencies] if getattr(route, "dependant", None) else []
            if "require_active_premium" in deps:
                gated.add((sorted(route.methods)[0], route.path))
        self.assertEqual(gated, {("GET", "/api/ai/explanation/{question_id}"),
                                 ("GET", "/api/ai/smart-practice/{device_id}"),
                                 ("GET", "/api/ai/dashboard/{device_id}"),
                                 ("POST", "/api/teacher/chat"),
                                 ("GET", "/api/tts/token")})


# ══════════════════════════════════════════════════════════════════════════════
class TtsPaywall(SecurityBase):
    """ElevenLabs TTS costs money: 401 without login, 402 without active access."""

    URLS = [("GET", "/api/tts?lang=th-TH&text=hei"), ("GET", "/api/tts/stream?lang=th-TH&text=hei"),
            ("POST", "/api/tts"), ("POST", "/api/tts/stream")]

    def call(self, method, url, headers=None, body=None):
        return self.client.request(method, url, headers=headers or {}, json=body)

    @staticmethod
    def with_query(url, suffix):
        """Append '&tt=...' to a URL that already has a query, or '?tt=...' to one that has none."""
        if not suffix:
            return url
        return url + (suffix if "?" in url else "?" + suffix.lstrip("&"))

    def assert_all(self, status, headers=None, suffix=""):
        for method, url in self.URLS:
            u = self.with_query(url, suffix)
            r = self.call(method, u, headers)
            self.assertEqual(r.status_code, status, f"{method} {u[:60]}: {r.status_code} {r.text[:100]}")

    def gate_passed(self, url_suffix, headers=None):
        """No text -> the handler answers 400 AFTER the gate, so no paid provider is ever called."""
        for method, url in (("GET", "/api/tts?lang=th-TH"), ("GET", "/api/tts/stream?lang=th-TH"),
                            ("POST", "/api/tts"), ("POST", "/api/tts/stream")):
            r = self.call(method, self.with_query(url, url_suffix), headers)
            self.assertEqual(r.status_code, 400, f"{method} {url}: {r.status_code} {r.text[:100]}")

    def tts_token(self, uid="u1", **payload):
        return server.jwt.encode({"sub": uid, "scope": "tts",
                                  "exp": datetime.now(timezone.utc) + timedelta(hours=1), **payload},
                                 server._tts_token_key(), algorithm=server.JWT_ALGORITHM)

    # -- 401: no valid identity ------------------------------------------------
    def test_unauthenticated_requests_are_rejected_with_401(self):
        self.assert_all(401)

    def test_garbage_bearer_and_garbage_tt_are_rejected(self):
        self.assert_all(401, {"Authorization": "Bearer garbage"})
        self.assert_all(401, suffix="&tt=garbage")

    def test_forged_tokens_are_rejected(self):
        self.add_user(is_premium=True)
        forged_session = server.jwt.encode({"sub": "u1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                                           "not-the-real-secret", algorithm=server.JWT_ALGORITHM)
        self.assert_all(401, {"Authorization": f"Bearer {forged_session}"})
        forged_tts = server.jwt.encode({"sub": "u1", "scope": "tts", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                                       "not-the-real-secret", algorithm=server.JWT_ALGORITHM)
        self.assert_all(401, suffix=f"&tt={forged_tts}")

    def test_expired_tts_token_is_rejected(self):
        self.add_user(is_premium=True)
        old = self.tts_token(exp=datetime.now(timezone.utc) - timedelta(minutes=1))
        self.assert_all(401, suffix=f"&tt={old}")

    def test_tts_token_with_wrong_scope_is_rejected(self):
        self.add_user(is_premium=True)
        wrong = self.tts_token(scope="other")
        self.assert_all(401, suffix=f"&tt={wrong}")

    def test_a_normal_session_token_is_not_accepted_in_the_tt_slot(self):
        self.add_user(is_premium=True)
        session = server.create_token("u1", "u1@example.com", is_premium=True)
        self.assert_all(401, suffix=f"&tt={session}")

    def test_token_for_a_deleted_user_is_rejected(self):
        self.assert_all(401, suffix=f"&tt={self.tts_token('ghost')}")
        self.assert_all(401, self.auth("ghost", is_premium=True))

    # -- 402: identity ok, no active access ---------------------------------------
    def test_free_user_gets_402_with_bearer_and_with_tt(self):
        self.add_user()
        self.assert_all(402, self.auth())
        self.assert_all(402, suffix=f"&tt={self.tts_token()}")

    def test_expired_subscription_and_expired_trial_get_402(self):
        self.add_user("sub", is_premium=True, premium_expires_at=_iso(-2))
        self.add_user("trial", trial_expires_at=_iso(-1))
        for uid in ("sub", "trial"):
            self.assert_all(402, suffix=f"&tt={self.tts_token(uid)}")

    def test_database_revocation_beats_a_still_valid_tts_token(self):
        self.add_user(is_premium=False)  # refunded after the token was issued
        self.assert_all(402, suffix=f"&tt={self.tts_token()}")

    def test_rejection_detail_matches_the_apps_gate_contract(self):
        self.add_user()
        d = self.call("GET", "/api/tts?text=hei", self.auth()).json()["detail"]
        self.assertEqual((d["error"], d["gate"], d["tier"]), ("premium_required", "upgrade", "registered"))
        d = self.call("GET", "/api/tts?text=hei").json()["detail"]
        self.assertEqual((d["error"], d["gate"]), ("auth_required", "register"))

    # -- allowed --------------------------------------------------------------
    def test_paid_lifetime_trial_and_admin_pass_the_gate(self):
        self.add_user("paid", is_premium=True, premium_expires_at=_iso(20))
        self.add_user("life", is_premium=True, premium_lifetime=True)
        self.add_user("trial", trial_expires_at=_iso(3))
        self.add_user("adm", is_admin=True)
        for uid in ("paid", "life", "trial", "adm"):
            self.gate_passed("", self.auth(uid, is_premium=True))
            self.gate_passed(f"&tt={self.tts_token(uid)}")

    # -- the token route ------------------------------------------------------------
    def test_token_route_is_paywalled(self):
        self.assertEqual(self.client.get("/api/tts/token").status_code, 402)
        self.add_user()
        self.assertEqual(self.client.get("/api/tts/token", headers=self.auth()).status_code, 402)
        self.assertEqual(self.client.get("/api/tts/token", headers={"Authorization": "Bearer garbage"}).status_code, 402)

    def test_issued_token_is_short_lived_bound_to_the_user_and_tts_only(self):
        self.add_user(is_premium=True, premium_lifetime=True)
        r = self.client.get("/api/tts/token", headers=self.auth(is_premium=True))
        self.assertEqual(r.status_code, 200)
        tok = r.json()["token"]
        self.assertEqual(r.json()["expires_in"], 7200)
        self.assertEqual(server.verify_tts_token(tok), "u1")
        exp = server.jwt.decode(tok, server._tts_token_key(), algorithms=[server.JWT_ALGORITHM])["exp"]
        self.assertLessEqual(exp - time.time(), 7200 + 5)
        # can never act as a login
        self.assertIsNone(server.verify_token(tok))
        self.assertEqual(self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {tok}"}).status_code, 401)
        # and never opens the AI paywall
        r = self.client.post("/api/teacher/chat", json={}, headers={"Authorization": f"Bearer {tok}"})
        self.assertEqual(r.status_code, 402)
        # ... while it does open TTS
        self.gate_passed(f"&tt={tok}")

    def test_tts_status_route_stays_open(self):
        self.assertNotIn(self.client.get("/api/tts/status").status_code, (401, 402))

    def test_no_paid_provider_is_called_before_the_gate(self):
        import httpx
        with patch.object(httpx, "AsyncClient", side_effect=AssertionError("provider called")):
            self.assert_all(401)
            self.add_user()
            self.assert_all(402, self.auth())


# ══════════════════════════════════════════════════════════════════════════════
class TtsClientsUseTheToken(unittest.TestCase):
    WEBAPP = (BACKEND / "webapp.py").read_text(encoding="utf-8")
    WEBSITE = (BACKEND / "website.py").read_text(encoding="utf-8")

    def test_webapp_appends_the_tts_token_to_every_audio_url(self):
        i = self.WEBAPP.index("function ttsStreamUrl(text, lang) {")
        body = self.WEBAPP[i:i + 700]
        self.assertIn("'&tt=' + encodeURIComponent(ttsToken)", body)
        self.assertIn("refreshTtsToken()", body)
        # all four audio call sites go through the one builder
        self.assertEqual(self.WEBAPP.count("audio.src = ttsStreamUrl("), 4)
        self.assertNotIn("audio.src = '/api/tts", self.WEBAPP)

    def test_webapp_fetches_the_token_on_entry_and_user_refresh_and_clears_it_on_logout(self):
        self.assertIn("/api/tts/token", self.WEBAPP)
        j = self.WEBAPP.index("function enterApp() {")
        self.assertIn("refreshTtsToken();", self.WEBAPP[j:j + 700])
        k = self.WEBAPP.index("async function refreshCurrentUser() {")
        self.assertIn("refreshTtsToken();", self.WEBAPP[k:k + 400])
        m = self.WEBAPP.index("function logout() {")
        self.assertIn("ttsToken = ''", self.WEBAPP[m:m + 400])

    def test_book_page_uses_the_token(self):
        self.assertIn("'/api/tts?lang=' + langParam + '&text=' + encodeURIComponent(text) + (ttsTok ? '&tt=' + encodeURIComponent(ttsTok) : '')", self.WEBSITE)
        self.assertIn("API+'/tts/token'", self.WEBSITE)

    def test_the_token_route_is_registered_on_app_not_the_already_included_router(self):
        src = (BACKEND / "server.py").read_text(encoding="utf-8")
        self.assertIn('@app.get("/api/tts/token")', src)
        self.assertLess(src.index("app.include_router(api_router)"), src.index('@app.get("/api/tts/token")'))


# ══════════════════════════════════════════════════════════════════════════════
class TtsPlaybackAndDemo(SecurityBase):
    """Paying users get audio (HTTP 200), unpaid are blocked, and landing visitors can hear the demo.

    The synthesis cache is pre-seeded, so no paid provider is ever called (httpx is booby-trapped)."""

    FAKE_MP3 = b"ID3" + b"\x03\x00" + b"\x00" * 400

    def setUp(self):
        super().setUp()
        server._demo_tts_hits.clear()
        self._seeded = []
        import httpx
        self._trap = patch.object(httpx, "AsyncClient", side_effect=AssertionError("paid TTS provider was called"))
        self._trap.start()
        self._keys = patch.dict(os.environ, {"ELEVENLABS_API_KEY": "", "GOOGLE_API_KEY": ""})
        self._keys.start()

    def tearDown(self):
        self._trap.stop()
        self._keys.stop()
        for path in self._seeded:
            try:
                os.remove(path)
            except OSError:
                pass
        server._demo_tts_hits.clear()
        super().tearDown()

    def seed_cache(self, text, lang="th-TH"):
        path = server._tts_cache_path(f"elevenlabs:{server._elevenlabs_model_id()}",
                                      server._elevenlabs_voice_id(lang), lang, text)
        with open(path, "wb") as f:
            f.write(self.FAKE_MP3)
        self._seeded.append(path)

    def tts_token(self, uid="u1"):
        return self.client.get("/api/tts/token", headers=self.auth(uid, is_premium=True)).json()["token"]

    # ── (a) paying users on mobile ──────────────────────────────────────────────────
    def test_paying_user_gets_200_and_audio_with_the_mobile_token_flow(self):
        self.add_user(is_premium=True, premium_lifetime=True)
        self.seed_cache("hei")
        tt = self.tts_token()  # what ttsToken.ts does: GET /api/tts/token with Bearer, then ?tt=
        r = self.client.get(f"/api/tts?lang=th-TH&text=hei&tt={tt}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["content-type"], "audio/mpeg")
        self.assertEqual(r.content, self.FAKE_MP3)

    def test_paying_user_gets_audio_with_bearer_header_too_and_via_post(self):
        self.add_user(is_premium=True, premium_lifetime=True)
        self.seed_cache("hei")
        h = self.auth(is_premium=True)
        self.assertEqual(self.client.get("/api/tts?lang=th-TH&text=hei", headers=h).content, self.FAKE_MP3)
        r = self.client.post("/api/tts", json={"text": "hei", "lang": "th-TH"}, headers=h)
        self.assertEqual((r.status_code, r.content), (200, self.FAKE_MP3))

    def test_free_week_and_admin_users_get_audio(self):
        self.add_user("trial", trial_expires_at=_iso(3))
        self.add_user("adm", is_admin=True)
        self.seed_cache("hei")
        for uid in ("trial", "adm"):
            r = self.client.get(f"/api/tts?lang=th-TH&text=hei&tt={self.tts_token(uid)}")
            self.assertEqual(r.status_code, 200, uid)

    def test_audio_supports_range_requests_like_the_mobile_player(self):
        self.add_user(is_premium=True, premium_lifetime=True)
        self.seed_cache("hei")
        r = self.client.get(f"/api/tts?lang=th-TH&text=hei&tt={self.tts_token()}", headers={"Range": "bytes=0-9"})
        self.assertIn(r.status_code, (200, 206))
        self.assertEqual(r.content, self.FAKE_MP3[:10] if r.status_code == 206 else self.FAKE_MP3)

    # ── (b) unpaid users are blocked, even when the audio is cached ────────────────────
    def test_unpaid_users_are_blocked_even_if_the_audio_is_cached(self):
        self.add_user("free")
        self.seed_cache("hei")
        self.assertEqual(self.client.get("/api/tts?lang=th-TH&text=hei").status_code, 401)
        self.assertEqual(self.client.get("/api/tts?lang=th-TH&text=hei", headers=self.auth("free")).status_code, 402)
        tt = server.jwt.encode({"sub": "free", "scope": "tts", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                               server._tts_token_key(), algorithm=server.JWT_ALGORITHM)
        self.assertEqual(self.client.get(f"/api/tts?lang=th-TH&text=hei&tt={tt}").status_code, 402)

    def test_unpaid_user_cannot_even_obtain_a_tts_token(self):
        self.add_user("free")
        self.assertEqual(self.client.get("/api/tts/token", headers=self.auth("free")).status_code, 402)

    # ── (c) landing page demo ───────────────────────────────────────────────────────────
    def test_visitor_hears_the_demo_without_logging_in(self):
        for slot, phrase in server.DEMO_TTS_PHRASES.items():
            self.seed_cache(phrase)
            r = self.client.get(f"/api/tts/demo?slot={slot}", headers={"X-Forwarded-For": f"10.0.0.{slot}"})
            self.assertEqual(r.status_code, 200, slot)
            self.assertEqual(r.headers["content-type"], "audio/mpeg")
            self.assertEqual(r.content, self.FAKE_MP3)

    def test_visitor_cannot_choose_the_text(self):
        self.seed_cache(server.DEMO_TTS_PHRASES[1])  # only the fixed phrase is cached; anything else would hit the trapped provider
        r = self.client.get("/api/tts/demo?slot=1&text=EVIL%20TEXT&lang=en")
        self.assertEqual((r.status_code, r.content), (200, self.FAKE_MP3))
        r = self.client.post("/api/tts/demo?slot=1", json={"text": "EVIL"})
        self.assertEqual(r.status_code, 405)  # GET only

    def test_unknown_demo_slots_are_rejected(self):
        for slot in ("0", "4", "-1", "99"):
            self.assertEqual(self.client.get(f"/api/tts/demo?slot={slot}").status_code, 400, slot)
        self.assertEqual(self.client.get("/api/tts/demo?slot=abc").status_code, 422)

    def test_demo_is_rate_limited_per_ip(self):
        for phrase in server.DEMO_TTS_PHRASES.values():
            self.seed_cache(phrase)
        ip = {"X-Forwarded-For": "203.0.113.7"}
        codes = [self.client.get(f"/api/tts/demo?slot={(i % 3) + 1}", headers=ip).status_code
                 for i in range(server.DEMO_TTS_MAX_PER_IP + 2)]
        self.assertEqual(codes[:server.DEMO_TTS_MAX_PER_IP], [200] * server.DEMO_TTS_MAX_PER_IP)
        self.assertEqual(codes[server.DEMO_TTS_MAX_PER_IP:], [429, 429])
        r = self.client.get("/api/tts/demo?slot=1", headers=ip)
        self.assertEqual(r.status_code, 429)
        self.assertGreater(int(r.headers["retry-after"]), 0)
        self.assertEqual(r.json()["detail"]["error"], "demo_rate_limited")
        # another visitor is unaffected
        self.assertEqual(self.client.get("/api/tts/demo?slot=1", headers={"X-Forwarded-For": "203.0.113.8"}).status_code, 200)

    def test_repeated_fetches_of_the_same_play_count_once(self):
        """<audio> fetches the same file several times (Range); that must not eat the visitor's allowance."""
        self.seed_cache(server.DEMO_TTS_PHRASES[1])
        ip = {"X-Forwarded-For": "203.0.113.9"}
        for _ in range(server.DEMO_TTS_MAX_PER_IP * 3):
            self.assertEqual(self.client.get("/api/tts/demo?slot=1", headers=ip).status_code, 200)

    def test_allowance_is_restored_after_the_window(self):
        ip = "198.51.100.1"
        now = 1_000_000.0
        for i in range(server.DEMO_TTS_MAX_PER_IP):
            self.assertEqual(server._demo_tts_retry_after(ip, (i % 3) + 1, now + i * 20), 0)
        self.assertGreater(server._demo_tts_retry_after(ip, 1, now + 200), 0)
        later = now + server.DEMO_TTS_WINDOW_SECONDS + 60
        self.assertEqual(server._demo_tts_retry_after(ip, 1, later), 0)

    def test_client_ip_ignores_spoofable_leading_forwarded_for_entries(self):
        class Req:
            def __init__(self, xff, host="127.0.0.1"):
                self.headers = {"x-forwarded-for": xff} if xff else {}
                self.client = type("C", (), {"host": host})()
        self.assertEqual(server._client_ip(Req("1.1.1.1, 2.2.2.2, 9.9.9.9")), "9.9.9.9")
        self.assertEqual(server._client_ip(Req("")), "127.0.0.1")

    def test_a_visitor_spoofing_forwarded_for_does_not_dodge_the_limit(self):
        for phrase in server.DEMO_TTS_PHRASES.values():
            self.seed_cache(phrase)
        codes = [self.client.get(f"/api/tts/demo?slot={(i % 3) + 1}",
                                 headers={"X-Forwarded-For": f"6.6.6.{i}, 203.0.113.50"}).status_code
                 for i in range(server.DEMO_TTS_MAX_PER_IP + 1)]
        self.assertEqual(codes[-1], 429)

    def test_demo_does_not_crash_when_the_audio_cannot_be_produced(self):
        # not cached, no provider keys: a controlled error response, not an unhandled exception
        r = self.client.get("/api/tts/demo?slot=2", headers={"X-Forwarded-For": "192.0.2.44"})
        self.assertIn(r.status_code, (500, 502, 503))
        self.assertIn("detail", r.json())

    def test_the_demo_route_does_not_open_the_paywalled_route(self):
        self.seed_cache("hei")
        self.assertEqual(self.client.get("/api/tts?lang=th-TH&text=hei").status_code, 401)

    def test_demo_phrases_are_short_thai_only_and_in_michaels_polite_male_register(self):
        phrases = list(server.DEMO_TTS_PHRASES.values())
        self.assertEqual(len(phrases), 3)
        self.assertEqual(len(set(phrases)), 3)
        thai, latin = re.compile(r"[\u0e00-\u0e7f]"), re.compile(r"[A-Za-z]")
        for ph in phrases:
            self.assertRegex(ph, thai)
            self.assertIsNone(latin.search(ph), ph)
            self.assertLessEqual(len(ph), 120, "keeps the total ElevenLabs cost tiny")
            self.assertTrue(ph.rstrip().endswith("ครับ"), ph)


# ══════════════════════════════════════════════════════════════════════════════
class LandingPageDemoWiring(unittest.TestCase):
    SRC = (BACKEND / "landing.py").read_text(encoding="utf-8")

    def test_landing_plays_the_fixed_demo_not_free_text(self):
        self.assertIn("'/api/tts/demo?slot=' + _demoSlot", self.SRC)
        self.assertNotIn("/api/tts?lang=th-TH&text=", self.SRC)
        self.assertNotIn("function speakText(", self.SRC)

    def test_demo_button_works_even_if_the_quiz_questions_did_not_load(self):
        i = self.SRC.index("if (ttsBtn) ttsBtn.addEventListener('click', () => {")
        body = self.SRC[i:i + 260]
        self.assertIn("speakDemo();", body)
        self.assertNotIn("if (!q) return;", body)

    def test_failures_reset_the_button_instead_of_crashing(self):
        i = self.SRC.index("function speakDemo() {")
        body = self.SRC[i:i + 1200]
        self.assertIn("_landingAudio.onerror", self.SRC)
        self.assertIn(".play().catch(", body)
        self.assertIn("ttsPlaying = false;", body)

    def test_landing_script_is_valid_javascript(self):
        import shutil
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available")
        import tempfile
        scripts = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", self.SRC, re.S))
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(scripts)
        try:
            r = subprocess.run([node, "--check", f.name], capture_output=True, text=True, timeout=60)
        finally:
            os.remove(f.name)
        self.assertEqual(r.returncode, 0, r.stderr[:300])


# ══════════════════════════════════════════════════════════════════════════════
class BackendTestScriptUsesTokens(unittest.TestCase):
    SRC = (REPO / "backend_test.py").read_text(encoding="utf-8")

    def test_no_hardcoded_admin_password_and_no_production_default(self):
        self.assertNotIn("admin123", self.SRC)
        self.assertIn('os.environ.get("T2D_ADMIN_PASSWORD", "")', self.SRC)
        self.assertIn('os.environ.get("T2D_BASE_URL", "http://127.0.0.1:8000/api")', self.SRC)
        self.assertIn('os.environ.get("T2D_ALLOW_PROD") != "1"', self.SRC)

    def test_script_acquires_jwt_tokens_and_sends_them_to_the_locked_routes(self):
        for needle in ("def acquire_tokens", "self.admin_token = self.login_token", "def admin_auth",
                       "test_locked_routes_reject_unauthenticated", "test_locked_routes_with_valid_token",
                       "test_ai_routes_paywall", "test_tts_paywall", '"X-Admin-Secret": ADMIN_SECRET'):
            self.assertIn(needle, self.SRC, needle)
        self.assertNotIn('("POST", "/seed", "Seed endpoint")', self.SRC)  # /seed is no longer tested open

    def test_script_is_valid_python(self):
        import ast
        ast.parse(self.SRC)


# ══════════════════════════════════════════════════════════════════════════════
class WebappHandlesTheGate(unittest.TestCase):
    SRC = (BACKEND / "webapp.py").read_text(encoding="utf-8")

    def test_main_teacher_chat_sends_the_login_token(self):
        i = self.SRC.index("var chatHeaders = { 'Content-Type': 'application/json' };")
        self.assertIn("chatHeaders.Authorization = 'Bearer ' + token", self.SRC[i:i + 300])
        self.assertIn("headers: chatHeaders", self.SRC[i:i + 500])

    def test_both_chat_calls_open_the_paywall_on_402(self):
        self.assertEqual(self.SRC.count("res.status === 402"), 2)
        j = self.SRC.index("if (res.status === 402) {\n      _teacherHideTyping();".replace("\n", "\r\n" if "\r\n" in self.SRC else "\n"))
        self.assertIn("showPaywall();", self.SRC[j:j + 200])


# ══════════════════════════════════════════════════════════════════════════════
class RepoHygiene(unittest.TestCase):
    def _git(self, *args):
        try:
            return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            self.skipTest("git not available")

    def test_frontend_env_is_not_tracked(self):
        r = self._git("ls-files", "--", "frontend/.env")
        if r.returncode != 0:
            self.skipTest("not a git checkout")
        self.assertEqual(r.stdout.strip(), "")

    def test_gitignore_blocks_env_files_but_allows_examples(self):
        text = (REPO / ".gitignore").read_text(encoding="utf-8")
        lines = {l.strip() for l in text.splitlines()}
        for rule in (".env", ".env.*", "frontend/.env", "!.env.example"):
            self.assertIn(rule, lines, rule)

    def test_example_file_exists_and_holds_no_secrets(self):
        ex = (REPO / "frontend" / ".env.example").read_text(encoding="utf-8")
        self.assertIn("EXPO_PUBLIC_RC_API_KEY=replace_with_public_sdk_key", ex)
        self.assertIsNone(re.search(r"(sk|rk|pk)_(live|test)_[A-Za-z0-9]{8,}|whsec_[A-Za-z0-9]{8,}|(goog|appl)_[A-Za-z0-9]{16,}", ex))


if __name__ == "__main__":
    unittest.main()
