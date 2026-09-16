"""Offline signup campaign checks; no MongoDB or payment provider is contacted."""
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server


@pytest.fixture
def campaign():
    database = MagicMock()
    database.users.find_one = AsyncMock(return_value=None)
    database.users.count_documents = AsyncMock(return_value=0)
    database.users.insert_one = AsyncMock()
    database.campaign_counters.update_one = AsyncMock()
    database.campaign_counters.find_one_and_update = AsyncMock(return_value={"sequence": 1})
    database.admin_users.find_one = AsyncMock(return_value=None)
    database.guest_usage.update_one = AsyncMock()
    with patch.object(server, "db", database), patch.object(
        server, "_migrate_guest_learning_to_user", new_callable=AsyncMock
    ), patch.object(server, "SEGMENT_WRITE_KEY", None):
        yield TestClient(server.app), database


def signup(client, **changes):
    body = {"full_name": "Test Bruker", "email": "test@example.com",
            "phone": "+4790012345", "password": "testpass123"}
    body.update(changes)
    return client.post("/api/auth/signup", json=body)


@pytest.mark.parametrize("missing", ["email", "phone"])
def test_missing_contact_is_400(campaign, missing):
    client, database = campaign
    body = {"full_name": "Test Bruker", "email": "test@example.com",
            "phone": "+4790012345", "password": "testpass123"}
    del body[missing]
    response = client.post("/api/auth/signup", json=body)
    assert response.status_code == 400
    assert response.json()["detail"]["key"] == "auth_invalid_signup"
    assert all(response.json()["detail"][lang] for lang in ("no", "th", "en"))
    database.users.insert_one.assert_not_awaited()


@pytest.mark.parametrize("duplicate", ["email", "phone"])
def test_duplicate_contact_in_mongo_is_400(campaign, duplicate):
    client, database = campaign
    if duplicate == "email":
        with patch.object(server, "_find_user_by_email", new_callable=AsyncMock,
                          return_value={"id": "existing"}):
            response = signup(client)
    else:
        database.users.find_one.return_value = {"id": "existing"}
        with patch.object(server, "_find_user_by_email", new_callable=AsyncMock,
                          return_value=None):
            response = signup(client)
        database.users.find_one.assert_awaited_with({"phone": "+4790012345"})
    assert response.status_code == 400
    assert response.json()["detail"]["key"] == f"{duplicate}_already_registered"
    database.users.insert_one.assert_not_awaited()


@pytest.mark.parametrize("existing,expected", [(49, True), (50, False)])
def test_campaign_boundary(campaign, existing, expected):
    client, database = campaign
    database.users.count_documents.return_value = existing
    database.campaign_counters.find_one_and_update.return_value = {"sequence": existing + 1}
    with patch.object(server, "_find_user_by_email", new_callable=AsyncMock,
                      return_value=None):
        response = signup(client)
    assert response.status_code == 200
    user = database.users.insert_one.await_args.args[0]
    assert user["has_premium"] is expected
    assert response.json()["user"]["has_premium"] is expected
    assert user["full_name"] == "Test Bruker"
    assert user["email"] == "test@example.com"
    assert user["phone"] == "+4790012345"
    if expected:
        expires = datetime.fromisoformat(user["trial_expires_at"])
        duration = expires - datetime.fromisoformat(user["trial_started_at"])
        assert duration.days == 30
        assert response.json()["user"]["premium_status"] == "trialing"
    else:
        assert user["trial_expires_at"] is None
        assert response.json()["user"]["premium_status"] == "none"
