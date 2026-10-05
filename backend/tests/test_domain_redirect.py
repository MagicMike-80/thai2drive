"""Canonical www-to-apex redirect contract."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


client = TestClient(server.app, follow_redirects=False)


def test_www_get_redirects_to_apex_and_preserves_path_and_query():
    response = client.get(
        "/api/web/version?checkout=success&session_id=cs_test_123",
        headers={"host": "www.thai2drive.no:8443", "x-forwarded-proto": "https"},
    )

    assert response.status_code == 301
    assert response.headers["location"] == (
        "https://thai2drive.no/api/web/version?checkout=success&session_id=cs_test_123"
    )


def test_www_head_redirects_permanently_and_preserves_query():
    response = client.head(
        "/api/web/version?probe=head",
        headers={"host": "www.thai2drive.no", "x-forwarded-proto": "https"},
    )

    assert response.status_code == 301
    assert response.headers["location"] == "https://thai2drive.no/api/web/version?probe=head"


def test_non_get_requests_on_www_are_not_redirected():
    response = client.post(
        "/domain-redirect-test-route",
        headers={"host": "www.thai2drive.no", "x-forwarded-proto": "https"},
    )

    assert response.status_code == 404
    assert "location" not in response.headers


def test_stripe_webhook_post_is_not_redirected(monkeypatch):
    monkeypatch.setattr(server, "_stripe_webhook_secret", lambda: "")
    response = client.post(
        "/api/stripe/webhook",
        content=b"{}",
        headers={"host": "www.thai2drive.no", "x-forwarded-proto": "https"},
    )

    assert response.status_code == 503
    assert "location" not in response.headers


def test_apex_requests_are_not_redirected():
    response = client.get(
        "/domain-redirect-test-route",
        headers={"host": "thai2drive.no", "x-forwarded-proto": "https"},
    )

    assert response.status_code == 404
    assert "location" not in response.headers
