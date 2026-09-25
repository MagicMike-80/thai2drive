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
            deps = [d.call.__name__ for d in getattr(route, "dependant", None).dependencies] if getattr(route, "dependant", None) else []
            if "require_active_premium" in deps:
                gated.add((sorted(route.methods)[0], route.path))
        self.assertEqual(gated, {("GET", "/api/ai/explanation/{question_id}"),
                                 ("GET", "/api/ai/smart-practice/{device_id}"),
                                 ("GET", "/api/ai/dashboard/{device_id}"),
                                 ("POST", "/api/teacher/chat")})


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
