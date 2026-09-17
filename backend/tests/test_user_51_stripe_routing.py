"""Isolated unit tests for User #51+ non-premium gating and Stripe checkout routing.

Verifies:
1. User #51 and onwards gets `has_premium: False`, `is_premium: False`, and `premium_status: 'none'`.
2. Non-premium user attempting checkout (/api/create-checkout-session) receives a valid live Stripe checkout URL.
3. Error toast and paywall feedback are strictly translated with zero language bleed across 'no', 'th', 'en'.
4. Access quota enforcement (/api/access/consume) returns HTTP 402 with localized upgrade messages.
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import server


@pytest.fixture
def mock_app_context():
    database = MagicMock()
    database.users.find_one = AsyncMock(return_value=None)
    database.users.count_documents = AsyncMock(return_value=50)
    database.users.insert_one = AsyncMock()
    database.campaign_counters.update_one = AsyncMock()
    # Sequence 51 = User #51
    database.campaign_counters.find_one_and_update = AsyncMock(return_value={"sequence": 51})
    database.admin_users.find_one = AsyncMock(return_value=None)
    database.guest_usage.update_one = AsyncMock()
    database.checkout_sessions.update_one = AsyncMock()
    database.access_events.find_one = AsyncMock(return_value=None)
    database.access_events.insert_one = AsyncMock()
    database.access_usage.find_one = AsyncMock(return_value=None)

    with patch.object(server, "db", database), patch.object(
        server, "_migrate_guest_learning_to_user", new_callable=AsyncMock
    ), patch.object(server, "SEGMENT_WRITE_KEY", None):
        yield TestClient(server.app), database


def test_user_51_signup_has_no_premium(mock_app_context):
    """User #51 and beyond must have has_premium=False, is_premium=False, and no free trial."""
    client, database = mock_app_context
    with patch.object(server, "_find_user_by_email", new_callable=AsyncMock, return_value=None):
        res = client.post(
            "/api/auth/signup",
            json={
                "full_name": "Bruker Femtien",
                "email": "bruker51@example.com",
                "phone": "+4790000051",
                "password": "password123",
            },
        )

    assert res.status_code == 200
    data = res.json()
    user = data["user"]
    assert user["has_premium"] is False
    assert user["is_premium"] is False
    assert user["premium_status"] == "none"
    assert user["trial_days_left"] == 0

    inserted_doc = database.users.insert_one.await_args.args[0]
    assert inserted_doc["campaign_index"] == 51
    assert inserted_doc["has_premium"] is False
    assert inserted_doc["is_premium"] is False
    assert inserted_doc["trial_expires_at"] is None


def test_user_51_stripe_checkout_session_success(mock_app_context):
    """Non-premium user #51 calling create-checkout-session receives live Stripe URL."""
    client, database = mock_app_context

    mock_user = {
        "id": "user-51-uuid",
        "email": "bruker51@example.com",
        "full_name": "Bruker Femtien",
        "is_admin": False,
        "is_premium": False,
        "has_premium": False,
    }
    database.users.find_one.return_value = mock_user

    mock_stripe = MagicMock()
    mock_price = MagicMock()
    mock_price.id = "price_monthly_live"
    mock_price.livemode = True

    mock_session = MagicMock()
    mock_session.id = "cs_live_user51_checkout_test"
    mock_session.url = "https://checkout.stripe.com/c/pay/cs_live_user51_checkout_test"
    mock_session.livemode = True
    mock_session.status = "open"

    mock_stripe.checkout.Session.create.return_value = mock_session

    fake_pricing = {
        "source": "stripe_live",
        "plans": [
            {
                "id": "monthly",
                "name": "Månedlig",
                "price": 199,
                "currency": "nok",
                "stripe_price": mock_price,
            }
        ],
    }

    token = server.create_token(
        mock_user["id"],
        mock_user["email"],
        is_premium=False,
    )

    with patch.object(server, "_stripe_module", return_value=mock_stripe), patch.object(
        server, "_get_live_stripe_plan_prices_sync", return_value=fake_pricing
    ):
        res = client.post(
            "/api/create-checkout-session",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "plan_id": "monthly",
                "success_url": "/api/web?checkout=success",
                "cancel_url": "/api/web?checkout=cancel",
            },
        )

    assert res.status_code == 200
    body = res.json()
    assert body["livemode"] is True
    assert body["session_id"] == "cs_live_user51_checkout_test"
    assert body["url"] == "https://checkout.stripe.com/c/pay/cs_live_user51_checkout_test"
    database.checkout_sessions.update_one.assert_awaited_once()


def test_checkout_unavailable_toast_translations_no_language_bleed():
    """Verify webapp.py has checkout_unavailable_toast in no, th, en with strict language purity."""
    webapp_code = (BACKEND_DIR / "webapp.py").read_text(encoding="utf-8")

    # Match checkout_unavailable_toast block
    match = re.search(
        r"checkout_unavailable_toast:\s*\{([^}]+)\}",
        webapp_code,
    )
    assert match is not None, "checkout_unavailable_toast not found in webapp.py"
    toast_block = match.group(1)

    th_match = re.search(r"th:\s*['\"]([^'\"]+)['\"]", toast_block)
    no_match = re.search(r"no:\s*['\"]([^'\"]+)['\"]", toast_block)
    en_match = re.search(r"en:\s*['\"]([^'\"]+)['\"]", toast_block)

    assert th_match and th_match.group(1).strip(), "Missing Thai translation for checkout_unavailable_toast"
    assert no_match and no_match.group(1).strip(), "Missing Norwegian translation for checkout_unavailable_toast"
    assert en_match and en_match.group(1).strip(), "Missing English translation for checkout_unavailable_toast"

    th_text = th_match.group(1)
    no_text = no_match.group(1)
    en_text = en_match.group(1)

    # Thai text must be 100% Thai (zero Latin characters)
    latin_words_in_th = re.findall(r"[A-Za-zÆØÅæøå]{2,}", th_text)
    assert latin_words_in_th == [], f"Found Latin words in Thai checkout toast: {latin_words_in_th}"

    # Norwegian text must match expected text
    assert "ikke tilgjengelig" in no_text.lower()
    # English text must match expected text
    assert "not available" in en_text.lower() or "unavailable" in en_text.lower()


def test_access_consume_402_for_exhausted_quota_with_localized_messages(mock_app_context):
    """When a registered non-premium user runs out of daily questions, consume returns 402."""
    client, database = mock_app_context

    mock_user = {
        "id": "user-51-uuid",
        "email": "bruker51@example.com",
        "full_name": "Bruker Femtien",
        "is_admin": False,
        "is_premium": False,
        "has_premium": False,
    }
    database.users.find_one.return_value = mock_user

    # Simulate exhausted daily quota (daily_used >= 10)
    day_key = server._oslo_day_key()
    database.access_usage.find_one.return_value = {
        "scope": "user",
        "key": "user-51-uuid",
        "day_key": day_key,
        "daily_used": 10,
    }

    token = server.create_token(
        mock_user["id"],
        mock_user["email"],
        is_premium=False,
    )

    res = client.post(
        "/api/access/consume",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_id": "dev-51",
            "question_id": "q123",
            "mode": "practice",
            "category": "vikeplikt",
        },
    )

    assert res.status_code == 402
    detail = res.json()["detail"]
    assert detail["can_answer"] is False
    assert detail["is_premium"] is False
    assert detail["tier"] == "registered"

    # Verify localized messages for all three languages
    messages = detail["message"]
    assert "Premium" in messages["no"]
    assert "Premium" in messages["th"]
    assert "Premium" in messages["en"]

    # Language purity: Thai message must not leak Norwegian words (except the brand 'Premium')
    th_msg_without_brand = messages["th"].replace("Premium", "")
    latin_in_th = re.findall(r"[A-Za-zÆØÅæøå]{3,}", th_msg_without_brand)
    assert latin_in_th == [], f"Found Latin words in Thai 402 message: {latin_in_th}"


def test_webapp_is_premium_contract():
    """Verify webapp.py gates premium tabs, exam mode, and calls showPaywall for non-premium."""
    webapp_code = (BACKEND_DIR / "webapp.py").read_text(encoding="utf-8")

    # Verify isPremium definition exists and checks user.is_premium
    assert "function isPremium()" in webapp_code
    assert "user.is_premium === true" in webapp_code

    # Verify premium tabs are gated
    assert "var premiumTabs = ['history', 'signs', 'bookmarks'];" in webapp_code
    assert "premiumTabs.indexOf(tab) !== -1 && !isPremium()" in webapp_code

    # Verify exam mode is gated
    assert "async function startExam()" in webapp_code
    assert "!isPremium()) { showPaywall(); return; }" in webapp_code

    # Verify paywall buy button triggers create-checkout-session
    assert "async function buyPremium(plan, el)" in webapp_code
    assert "'/api/create-checkout-session'" in webapp_code
    assert "window.location.href = session.url;" in webapp_code
