"""Signed Stripe checkout events must grant the purchased plan in MongoDB."""
import hashlib
import hmac
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import server  # noqa: E402


SECRET = "whsec_local_signature_test"


@pytest.mark.parametrize("plan_id,amount,recurring", [
    ("monthly", 9900, SimpleNamespace(interval="month", interval_count=1)),
    ("three_months", 24900, SimpleNamespace(interval="month", interval_count=3)),
    ("lifetime", 69900, None),
])
def test_thai_checkout_uses_verified_amount_and_thai_product_name(plan_id, amount, recurring):
    plan = {"id": plan_id, "amount_minor": amount}
    price = SimpleNamespace(id=f"price_live_{plan_id}", recurring=recurring, tax_behavior="unspecified")
    line = server._checkout_line_item(plan, price, "th")
    assert line["price_data"]["currency"] == "nok"
    assert line["price_data"]["unit_amount"] == amount
    assert not any(c.isascii() and c.isalpha() for c in line["price_data"]["product_data"]["name"])
    assert ("recurring" in line["price_data"]) is (recurring is not None)
    assert server._checkout_line_item(plan, price, "no") == {"price": price.id, "quantity": 1}


def signed_event(client, event):
    event.setdefault("object", "event")
    raw = json.dumps(event, separators=(",", ":")).encode()
    timestamp = str(int(time.time()))
    signature = hmac.new(SECRET.encode(), timestamp.encode() + b"." + raw, hashlib.sha256).hexdigest()
    return client.post("/api/stripe/webhook", content=raw, headers={
        "stripe-signature": f"t={timestamp},v1={signature}",
        "content-type": "application/json",
    })


@pytest.fixture
def webhook_context():
    database = MagicMock()
    database.stripe_events.find_one = AsyncMock(return_value=None)
    database.stripe_events.update_one = AsyncMock()
    database.users.update_one = AsyncMock()
    database.subscriptions.update_one = AsyncMock()
    with patch.object(server, "db", database), patch.object(server, "_stripe_module", return_value=stripe), \
         patch.object(server, "_stripe_webhook_secret", return_value=SECRET):
        yield TestClient(server.app), database


@pytest.mark.parametrize("plan,mode,expected_lifetime,expected_expiry", [
    ("monthly", "subscription", False, False),
    ("three_months", "payment", False, True),
    ("lifetime", "payment", True, False),
])
def test_paid_checkout_grants_exact_plan(webhook_context, plan, mode, expected_lifetime, expected_expiry):
    client, database = webhook_context
    event = {
        "id": f"evt_{plan}", "type": "checkout.session.completed", "livemode": True,
        "data": {"object": {
            "id": f"cs_live_{plan}", "mode": mode, "payment_status": "paid",
            "customer": "cus_live_example", "subscription": "sub_live_example" if mode == "subscription" else None,
            "metadata": {"user_id": "customer-user", "plan_id": plan},
        }},
    }
    response = signed_event(client, event)
    assert response.status_code == 200, response.text
    assert response.json() == {"received": True, "handled": True}
    args, kwargs = database.users.update_one.await_args
    assert args[0] == {"id": "customer-user"}
    update = args[1]
    assert update["$set"]["is_premium"] is True
    assert update["$set"]["premium_plan"] == plan
    assert update["$set"]["premium_source"] == "stripe"
    assert update["$set"].get("premium_lifetime", False) is expected_lifetime
    assert ("premium_expires_at" in update["$set"]) is expected_expiry
    if expected_expiry:
        expiry = datetime.fromisoformat(update["$set"]["premium_expires_at"])
        days_left = (expiry - datetime.now(timezone.utc)).total_seconds() / 86400
        assert 89 < days_left <= 90
    if expected_lifetime:
        assert update["$unset"] == {"premium_expires_at": ""}
    database.subscriptions.update_one.assert_awaited_once()
    assert database.stripe_events.update_one.await_args.args[1]["$set"]["handled"] is True


def test_unpaid_checkout_does_not_grant_access(webhook_context):
    client, database = webhook_context
    event = {"id": "evt_unpaid", "type": "checkout.session.completed", "livemode": True,
             "data": {"object": {"id": "cs_live_unpaid", "mode": "payment", "payment_status": "unpaid",
                                 "metadata": {"user_id": "customer-user", "plan_id": "lifetime"}}}}
    response = signed_event(client, event)
    assert response.status_code == 200
    assert response.json()["handled"] is False
    database.users.update_one.assert_not_awaited()


def test_delayed_payment_grants_only_after_success(webhook_context):
    client, database = webhook_context
    event = {"id": "evt_async", "type": "checkout.session.async_payment_succeeded", "livemode": True,
             "data": {"object": {"id": "cs_live_async", "mode": "payment", "payment_status": "paid",
                                 "metadata": {"user_id": "customer-user", "plan_id": "three_months"}}}}
    response = signed_event(client, event)
    assert response.status_code == 200
    assert response.json()["handled"] is True
    assert database.users.update_one.await_args.args[1]["$set"]["premium_plan"] == "three_months"


def test_signed_test_mode_event_is_rejected(webhook_context):
    client, database = webhook_context
    event = {"id": "evt_test", "type": "checkout.session.completed", "livemode": False,
             "data": {"object": {"id": "cs_test_fake", "mode": "payment", "payment_status": "paid",
                                 "metadata": {"user_id": "customer-user", "plan_id": "lifetime"}}}}
    response = signed_event(client, event)
    assert response.status_code == 400
    database.users.update_one.assert_not_awaited()


def test_recurring_subscription_expiry_is_persisted(webhook_context):
    client, database = webhook_context
    period_end = int(time.time()) + 30 * 86400
    event = {"id": "evt_subscription", "type": "customer.subscription.created", "livemode": True,
             "data": {"object": {"id": "sub_live_example", "status": "active", "customer": "cus_live_example",
                                 "current_period_end": period_end,
                                 "metadata": {"user_id": "customer-user", "plan_id": "monthly"}}}}
    response = signed_event(client, event)
    assert response.status_code == 200
    update = database.users.update_one.await_args.args[1]["$set"]
    assert update["premium_plan"] == "monthly"
    assert update["premium_expires_at"] == datetime.fromtimestamp(period_end, timezone.utc).isoformat()
