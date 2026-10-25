"""Offline tests for the account-bound 30-day Premium campaign."""
import re
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import server

THAI_REGEX = re.compile(r"[\u0e00-\u0e7f]")


class TestCampaignBackend(unittest.TestCase):
    def setUp(self):
        self.account = {
            "id": "synthetic-user-001",
            "email": "learner@example.test",
            "name": "Synthetic Learner",
            "phone": "+4700000000",
            "is_admin": False,
            "is_premium": False,
            "has_premium": False,
            "trial_used": False,
            "trial_expires_at": None,
            "premium_expires_at": None,
        }
        self.mock_db = MagicMock()
        self.mock_campaign_users = MagicMock()
        self.mock_users = MagicMock()
        self.mock_db.campaign_users = self.mock_campaign_users
        self.mock_db.users = self.mock_users
        self.mock_counters = MagicMock()
        self.mock_db.campaign_counters = self.mock_counters
        self.transaction_aborted = False
        test = self
        class Session:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): return False
            async def with_transaction(self, callback):
                try:
                    return await callback(self)
                except Exception:
                    test.transaction_aborted = True
                    raise
        self.session = Session()
        self.mock_db.client.start_session = AsyncMock(return_value=self.session)
        self.mock_counters.update_one = AsyncMock()
        self.mock_counters.find_one_and_update = AsyncMock(return_value={"sequence": 1})
        self.mock_campaign_users.find_one = AsyncMock(return_value=None)
        self.mock_campaign_users.count_documents = AsyncMock(return_value=0)
        self.mock_campaign_users.insert_one = AsyncMock()
        self.mock_campaign_users.delete_one = AsyncMock()
        self.mock_users.find_one = AsyncMock(return_value=self.account)
        self.mock_users.update_one = AsyncMock(return_value=SimpleNamespace(modified_count=1))
        self.db_patcher = patch.object(server, "db", self.mock_db)
        self.db_patcher.start()
        self.previous_override = server.app.dependency_overrides.get(server.get_current_user)

        async def authenticated_test_user():
            return {"sub": self.account["id"]}

        self.auth_override = authenticated_test_user
        server.app.dependency_overrides[server.get_current_user] = self.auth_override
        self.client = TestClient(server.app)

    def tearDown(self):
        if self.previous_override is None:
            server.app.dependency_overrides.pop(server.get_current_user, None)
        else:
            server.app.dependency_overrides[server.get_current_user] = self.previous_override
        self.db_patcher.stop()

    def register(self, language="no", **extra_fields):
        return self.client.post("/api/campaign/register", json={"language": language, **extra_fields})

    def test_campaign_status_is_read_only_and_reports_capacity(self):
        self.mock_campaign_users.count_documents.return_value = 35
        response = self.client.get("/api/campaign/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["remaining"], 15)
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_claim_requires_authentication(self):
        server.app.dependency_overrides.pop(server.get_current_user, None)
        response = self.client.post("/api/campaign/register", json={"language": "no"})
        self.assertEqual(response.status_code, 401)
        self.mock_users.find_one.assert_not_awaited()
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_success_grants_exactly_30_days_to_authenticated_account_only(self):
        response = self.register("no", email="victim@example.test", phone="+4799999999", name="Victim")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["campaign_index"], 1)
        self.assertIn("30 dagers gratis Premium", data["message"])
        self.assertFalse(THAI_REGEX.search(data["message"]))

        self.mock_users.find_one.assert_awaited_once_with(
            {"id": "synthetic-user-001"}, {"_id": 0, "password_hash": 0}, session=self.session
        )
        user_filter, user_update = self.mock_users.update_one.await_args.args
        self.assertEqual(user_filter["id"], "synthetic-user-001")
        self.assertNotIn("email", user_filter)
        self.assertNotIn("phone", user_filter)
        self.assertEqual(user_filter["is_premium"], {"$ne": True})
        self.assertEqual(user_filter["premium_expires_at"], {"$in": [None, ""]})
        self.assertEqual(user_update["$set"]["is_premium"], False)
        self.assertTrue(user_update["$set"]["has_premium"])
        self.assertTrue(user_update["$set"]["trial_used"])

        inserted = self.mock_campaign_users.insert_one.await_args.args[0]
        self.assertEqual(inserted["user_id"], "synthetic-user-001")
        self.assertEqual(inserted["_id"], "free30-2026-10:synthetic-user-001")
        self.assertFalse({"email", "phone", "name", "password"}.intersection(inserted))
        started = datetime.fromisoformat(inserted["trial_started_at"])
        expires = datetime.fromisoformat(inserted["trial_expires_at"])
        self.assertEqual(expires - started, timedelta(days=30))

    def test_response_language_isolated_for_thai_english_and_norwegian(self):
        for language, expected, forbidden in (
            ("th", "ยินดีด้วยครับ", "Congratulations"),
            ("en", "Congratulations", "ยินดีด้วยครับ"),
            ("no", "Gratulerer", "ยินดีด้วยครับ"),
        ):
            with self.subTest(language=language):
                self.mock_campaign_users.count_documents.return_value = 0
                self.mock_campaign_users.insert_one.reset_mock()
                self.mock_users.update_one.return_value = SimpleNamespace(modified_count=1)
                response = self.register(language)
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected, response.json()["message"])
                self.assertNotIn(forbidden, response.json()["message"])

    def test_unknown_language_fails_without_thai_fallback(self):
        response = self.register("de")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"success": False, "error": "unsupported_language"})
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_missing_language_fails_without_thai_fallback(self):
        response = self.client.post("/api/campaign/register", json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"success": False, "error": "unsupported_language"})
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_repeat_claim_is_rejected_for_same_account(self):
        self.mock_campaign_users.find_one.return_value = {"user_id": "synthetic-user-001"}
        response = self.register("en")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "already_registered")
        self.mock_campaign_users.insert_one.assert_not_awaited()
        self.mock_users.update_one.assert_not_awaited()

    def test_paid_or_admin_account_is_never_shortened_or_overwritten(self):
        self.account.update({"is_premium": True, "premium_expires_at": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()})
        response = self.register("en")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "premium_already_active")
        self.mock_users.update_one.assert_not_awaited()
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_used_trial_cannot_be_reset_or_extended(self):
        self.account["trial_used"] = True
        response = self.register("th")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "trial_already_used")
        self.assertTrue(THAI_REGEX.search(response.json()["message"]))
        self.mock_users.update_one.assert_not_awaited()

    def test_active_trial_is_not_extended(self):
        self.account["trial_used"] = True
        self.account["trial_expires_at"] = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
        response = self.register("no")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "premium_already_active")
        self.mock_users.update_one.assert_not_awaited()

    def test_51st_campaign_claim_is_rejected(self):
        self.mock_campaign_users.count_documents.return_value = 50
        response = self.register("en")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "campaign_sold_out")
        self.mock_campaign_users.insert_one.assert_not_awaited()
        self.mock_users.update_one.assert_not_awaited()

    def test_50th_claim_uses_committed_count_not_old_sequence(self):
        self.mock_campaign_users.count_documents.return_value = 49
        self.mock_counters.find_one_and_update.return_value = {"sequence": 999}
        response = self.register("en")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["campaign_index"], 50)
        self.assertEqual(response.json()["remaining_seats"], 0)
        for operation in (self.mock_campaign_users.insert_one, self.mock_users.update_one,
                          self.mock_campaign_users.count_documents,
                          self.mock_counters.find_one_and_update):
            self.assertIs(operation.await_args.kwargs["session"], self.session)

    def test_failed_conditional_account_update_aborts_entire_claim(self):
        self.mock_users.update_one.return_value = SimpleNamespace(modified_count=0)
        response = self.register("no")
        self.assertEqual(response.status_code, 409)
        self.assertTrue(self.transaction_aborted)
        self.mock_campaign_users.delete_one.assert_not_awaited()

    def test_duplicate_insert_aborts_transaction(self):
        self.mock_campaign_users.insert_one.side_effect = server.DuplicateKeyError("duplicate")
        response = self.register("no")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.transaction_aborted)
        self.mock_users.update_one.assert_not_awaited()

    def test_expired_trial_returns_to_free_status_using_synthetic_data(self):
        expired = {
            "trial_used": True,
            "trial_expires_at": (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(),
            "is_premium": False,
            "premium_expires_at": None,
        }
        self.assertFalse(server._user_has_active_trial(expired))
        self.assertEqual(server._user_premium_status(expired), "expired")


class TestCampaignWebUI(unittest.TestCase):
    def test_campaign_modal_requires_login_and_sends_no_client_identity(self):
        import webapp
        html = webapp.WEBAPP_HTML
        self.assertIn("if (!user || !token)", html)
        self.assertIn("openGuestRegistration();", html)
        self.assertIn("'Authorization': 'Bearer ' + token", html)
        self.assertIn("body: JSON.stringify({language: appLang})", html)
        self.assertNotIn('id="campEmail"', html)
        self.assertNotIn('id="campPhone"', html)
        self.assertIn("campaign_login_required:", html)

    def test_practice_test_is_not_described_as_official(self):
        import webapp
        html = webapp.WEBAPP_HTML
        self.assertIn("Start Thai2Drives øvingsprøve", html)
        self.assertIn("Start Thai2Drive practice test", html)
        self.assertNotIn("Start Offisiell Teoriprøve", html)
        self.assertNotIn("Start Official Theory Exam", html)

    def test_sound_toggle_labels_current_state_in_all_languages(self):
        import webapp
        html = webapp.WEBAPP_HTML
        self.assertIn("fc_sound_state_on:     {th:'เปิดเสียงอยู่', no:'Lyd er på', en:'Sound is on'}", html)
        self.assertIn("fc_sound_state_off:    {th:'ปิดเสียงอยู่', no:'Lyd er av', en:'Sound is off'}", html)
        self.assertIn("_flashcardSfxMuted ? 'fc_sound_state_off' : 'fc_sound_state_on'", html)
        self.assertIn("aria-pressed", html)

    def test_campaign_translation_objects_are_complete(self):
        import webapp
        html = webapp.WEBAPP_HTML
        for key in ("campaign_modal_sub", "campaign_login_required", "campaign_language_error"):
            match = re.search(rf"{key}:\s*\{{th:'([^']*)',\s*no:'([^']*)',\s*en:'([^']*)'\}}", html)
            self.assertIsNotNone(match, key)
            self.assertTrue(all(match.groups()), key)


if __name__ == "__main__":
    unittest.main()
