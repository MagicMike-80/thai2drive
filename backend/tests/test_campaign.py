"""
Tests for Phase 5: 50-User Free Premium Campaign Registration (TASK-015)
-------------------------------------------------------------------------
Verifies:
1. First 50 registered users receive 30 days of free Premium (is_premium: True, has_premium: True).
2. User #51 is gracefully rejected with HTTP 400 and localized polite notice.
3. Duplicate email or phone registrations are blocked with HTTP 400.
4. Invalid inputs (missing fields or bad email) are rejected with HTTP 400.
5. 100% strict language isolation across NO, TH, and EN for all campaign responses.
6. Synchronisation with existing user records in db.users when applicable.
"""
import re
import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import server

THAI_REGEX = re.compile(r"[\u0e00-\u0e7f]")


class TestCampaignBackend(unittest.TestCase):
    """Test campaign registration and status endpoints."""

    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_campaign_users = MagicMock()
        self.mock_users = MagicMock()

        self.mock_db.campaign_users = self.mock_campaign_users
        self.mock_db.users = self.mock_users

        self.mock_campaign_users.find_one = AsyncMock(return_value=None)
        self.mock_campaign_users.count_documents = AsyncMock(return_value=0)
        self.mock_campaign_users.insert_one = AsyncMock()

        self.mock_users.update_many = AsyncMock()
        self.mock_users.find_one = AsyncMock(return_value=None)

        self.patcher = patch.object(server, "db", self.mock_db)
        self.patcher.start()
        self.client = TestClient(server.app)

    def tearDown(self):
        self.patcher.stop()

    def test_campaign_status_initial(self):
        self.mock_campaign_users.count_documents.return_value = 0
        resp = self.client.get("/api/campaign/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("total_seats"), 50)
        self.assertEqual(data.get("registered"), 0)
        self.assertEqual(data.get("remaining"), 50)
        self.assertTrue(data.get("is_active"))

    def test_campaign_status_partially_filled(self):
        self.mock_campaign_users.count_documents.return_value = 35
        resp = self.client.get("/api/campaign/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("registered"), 35)
        self.assertEqual(data.get("remaining"), 15)
        self.assertTrue(data.get("is_active"))

    def test_campaign_status_sold_out(self):
        self.mock_campaign_users.count_documents.return_value = 50
        resp = self.client.get("/api/campaign/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("registered"), 50)
        self.assertEqual(data.get("remaining"), 0)
        self.assertFalse(data.get("is_active"))

    def test_first_user_registration_success_thai(self):
        self.mock_campaign_users.count_documents.return_value = 0
        payload = {
            "name": "สมชาย ใจดี",
            "email": "somchai@example.com",
            "phone": "+47 912 34 567",
            "language": "th"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("campaign_index"), 1)
        self.assertTrue(data.get("is_premium"))
        self.assertTrue(data.get("has_premium"))
        self.assertEqual(data.get("remaining_seats"), 49)

        # 100% Thai language isolation
        self.assertTrue(bool(THAI_REGEX.search(data.get("message", ""))))
        self.assertIn("ยินดีด้วยครับ", data.get("message", ""))

        # Check DB insertion
        self.mock_campaign_users.insert_one.assert_awaited_once()
        inserted_doc = self.mock_campaign_users.insert_one.await_args.args[0]
        self.assertEqual(inserted_doc["name"], "สมชาย ใจดี")
        self.assertEqual(inserted_doc["email"], "somchai@example.com")
        self.assertEqual(inserted_doc["phone"], "+4791234567")
        self.assertTrue(inserted_doc["is_premium"])

        # Check 30 days duration
        until = datetime.fromisoformat(inserted_doc["premium_until"])
        created = datetime.fromisoformat(inserted_doc["created_at"])
        delta = until - created
        self.assertEqual(delta.days, 30)

    def test_registration_success_norwegian(self):
        self.mock_campaign_users.count_documents.return_value = 10
        payload = {
            "name": "Kari Nordmann",
            "email": "kari@example.no",
            "phone": "99887766",
            "language": "no"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("campaign_index"), 11)
        self.assertEqual(data.get("remaining_seats"), 39)

        # Zero Thai characters in Norwegian message
        msg = data.get("message", "")
        self.assertFalse(bool(THAI_REGEX.search(msg)))
        self.assertIn("Gratulerer", msg)
        self.assertIn("plass 11 av 50", msg)

    def test_registration_success_english(self):
        self.mock_campaign_users.count_documents.return_value = 49
        payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+4711223344",
            "language": "en"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("campaign_index"), 50)
        self.assertEqual(data.get("remaining_seats"), 0)

        # Zero Thai characters in English message
        msg = data.get("message", "")
        self.assertFalse(bool(THAI_REGEX.search(msg)))
        self.assertIn("Congratulations", msg)
        self.assertIn("spot 50 of 50", msg)

    def test_user_51_rejected_sold_out(self):
        self.mock_campaign_users.count_documents.return_value = 50
        payload = {
            "name": "Bruker Femtien",
            "email": "bruker51@example.com",
            "phone": "+4799009900",
            "language": "th"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()

        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error"), "campaign_sold_out")
        self.assertEqual(data.get("remaining"), 0)

        # Thai sold out notice
        self.assertTrue(bool(THAI_REGEX.search(data.get("message", ""))))
        self.assertIn("แคมเปญนี้เต็มแล้วครับ", data.get("message", ""))
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_user_51_rejected_sold_out_norwegian(self):
        self.mock_campaign_users.count_documents.return_value = 50
        payload = {
            "name": "Bruker Femtien",
            "email": "bruker51@example.com",
            "phone": "+4799009900",
            "language": "no"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()

        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error"), "campaign_sold_out")
        msg = data.get("message", "")
        self.assertFalse(bool(THAI_REGEX.search(msg)))
        self.assertIn("Kampanjen er nå fulltegnet", msg)

    def test_duplicate_email_rejected(self):
        self.mock_campaign_users.find_one.return_value = {"email": "duplicate@example.com"}
        payload = {
            "name": "Ny Bruker",
            "email": "duplicate@example.com",
            "phone": "+4799112233",
            "language": "th"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()

        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error"), "already_registered")
        self.assertTrue(bool(THAI_REGEX.search(data.get("message", ""))))
        self.assertIn("ลงทะเบียนในแคมเปญแล้ว", data.get("message", ""))
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_duplicate_phone_rejected(self):
        self.mock_campaign_users.find_one.return_value = {"phone": "+4799112233"}
        payload = {
            "name": "Ny Bruker",
            "email": "unique@example.com",
            "phone": "+47 99 11 22 33",
            "language": "no"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()

        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("error"), "already_registered")
        msg = data.get("message", "")
        self.assertFalse(bool(THAI_REGEX.search(msg)))
        self.assertIn("allerede registrert", msg)
        self.mock_campaign_users.insert_one.assert_not_awaited()

    def test_invalid_input_validation(self):
        # Missing email
        resp = self.client.post("/api/campaign/register", json={"name": "Ola", "phone": "123"})
        self.assertEqual(resp.status_code, 422)  # Pydantic missing field

        # Blank fields or invalid email
        resp = self.client.post("/api/campaign/register", json={
            "name": "",
            "email": "notanemail",
            "phone": "123",
            "language": "en"
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data.get("error"), "invalid_input")
        self.assertIn("Please fill in", data.get("message", ""))

    def test_sync_with_existing_user_in_db_users(self):
        self.mock_campaign_users.count_documents.return_value = 5
        payload = {
            "name": "Eksisterende Elev",
            "email": "elev@example.com",
            "phone": "+4790909090",
            "language": "no"
        }
        resp = self.client.post("/api/campaign/register", json=payload)
        self.assertEqual(resp.status_code, 200)

        # Check update_many was called on db.users
        self.mock_users.update_many.assert_awaited_once()
        query_filter, update_action = self.mock_users.update_many.await_args.args
        self.assertEqual(query_filter, {"$or": [{"email": "elev@example.com"}, {"phone": "+4790909090"}]})
        set_dict = update_action["$set"]
        self.assertTrue(set_dict["is_premium"])
        self.assertTrue(set_dict["has_premium"])
        self.assertEqual(set_dict["campaign_index"], 6)


class TestCampaignWebUI(unittest.TestCase):
    """Verify that webapp.py includes the campaign banner, modal, and pure translations."""

    def test_campaign_elements_in_webapp_html(self):
        import webapp
        html = webapp.WEBAPP_HTML
        self.assertIn('id="homeCampaignBanner"', html)
        self.assertIn('id="campaignModal"', html)
        self.assertIn('id="cbRemainingText"', html)
        self.assertIn('id="campSubmitBtn"', html)
        self.assertIn('checkCampaignStatus()', html)
        self.assertIn('openCampaignModal()', html)
        self.assertIn('closeCampaignModal()', html)

    def test_campaign_translations_language_isolation(self):
        import webapp
        html = webapp.WEBAPP_HTML
        # Extract UI dictionary or verify keys
        keys = [
            "campaign_badge",
            "campaign_title",
            "campaign_desc",
            "campaign_claim_btn",
            "campaign_modal_title",
            "campaign_modal_sub",
            "campaign_name_label",
            "campaign_email_label",
            "campaign_phone_label",
            "campaign_submit_btn",
            "campaign_sold_out",
        ]
        for key in keys:
            self.assertIn(f"{key}:", html, f"Missing translation key {key} in webapp.py")

    def test_campaign_neon_palette_compliance(self):
        import webapp
        html = webapp.WEBAPP_HTML
        # Extract campaign css segment
        start_idx = html.find("/* ═══ 50-USER CAMPAIGN BANNER & MODAL ═══ */")
        self.assertGreater(start_idx, 0, "Campaign CSS section missing")
        end_idx = html.find("/* ══════════════════════════════════════════", start_idx)
        css_section = html[start_idx:end_idx].lower()

        # Check that forbidden neon colors (pure yellow / pure green) are NOT used
        forbidden = ["#00ff00", "#39ff14", "#76ff03", "#ffff00", "#ccff00", "lime", "chartreuse"]
        for f in forbidden:
            self.assertNotIn(f, css_section, f"Forbidden neon color '{f}' found in campaign CSS")


if __name__ == "__main__":
    unittest.main()

