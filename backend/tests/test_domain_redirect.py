"""Canonical www-to-apex redirect contract."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


client = TestClient(server.app, follow_redirects=False)


def test_www_get_redirects_to_apex_and_preserves_path_and_query():
    response = client.get(
        "/some/page?checkout=success&session_id=cs_test_123",
        headers={"host": "www.thai2drive.no:8443", "x-forwarded-proto": "https"},
    )

    assert response.status_code == 301
    assert response.headers["location"] == (
        "https://thai2drive.no/some/page?checkout=success&session_id=cs_test_123"
    )


def test_www_api_get_is_not_redirected():
    for host in ("www.thai2drive.no", "thai2drive.no"):
        response = client.get(
            "/api/web/version",
            headers={"host": host, "x-forwarded-proto": "https", "authorization": "Bearer x"},
        )
        assert response.status_code != 301
        assert "location" not in response.headers


def test_stripe_return_urls_are_apex():
    assert server._public_site_url() == "https://thai2drive.no"
    assert server._safe_return_url(
        "https://www.thai2drive.no/api/web?checkout=success&session_id={CHECKOUT_SESSION_ID}", "/x"
    ) == "https://thai2drive.no/api/web?checkout=success&session_id={CHECKOUT_SESSION_ID}"
    assert server._safe_return_url(None, "/x") == "https://thai2drive.no/x"


def test_www_head_redirects_permanently_and_preserves_query():
    response = client.head(
        "/some/page?probe=head",
        headers={"host": "www.thai2drive.no", "x-forwarded-proto": "https"},
    )

    assert response.status_code == 301
    assert response.headers["location"] == "https://thai2drive.no/some/page?probe=head"


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
