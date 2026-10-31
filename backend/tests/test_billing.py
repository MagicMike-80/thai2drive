"""Offline unit tests for RevenueCat billing integration (billing.py).

Zero network: httpx.AsyncClient is mocked in every test that would otherwise
reach out to the RevenueCat API. Covers: reading REVENUECAT_API_KEY from the
environment, the happy-path premium lookup, the documented fail-soft path on
error, and that no hardcoded sandbox/test key ever leaks into the module.
"""
import asyncio
import importlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import billing  # noqa: E402
import server  # noqa: E402


def _run(coro):
    return asyncio.run(coro)


def _body(response):
    return json.loads(response.body)


def _auth(user_id):
    return "Bearer " + server.create_token(user_id, "billing@example.test")


class TestRevenueCatApiKeyFromEnv(unittest.TestCase):
    """Test 1: REVENUECAT_API_KEY must come from the environment."""

    def setUp(self):
        self._orig_key = billing.REVENUECAT_API_KEY

    def tearDown(self):
        billing.REVENUECAT_API_KEY = self._orig_key

    def test_key_is_read_from_environment_variable(self):
        with mock.patch.dict(os.environ, {"REVENUECAT_API_KEY": "prod_key_from_env_xyz"}):
            importlib.reload(billing)
            try:
                self.assertEqual(billing.REVENUECAT_API_KEY, "prod_key_from_env_xyz")
            finally:
                importlib.reload(billing)  # restore module state for later tests


class TestSuccessfulSubscriptionCheck(unittest.TestCase):
    """Test 2: a 200 OK from RevenueCat must translate into the correct premium status."""

    def setUp(self):
        self._orig_key = billing.REVENUECAT_API_KEY
        billing.REVENUECAT_API_KEY = "fake_prod_key_for_test"

    def tearDown(self):
        billing.REVENUECAT_API_KEY = self._orig_key

    def _mock_client(self, status_code=200, json_data=None):
        mock_response = mock.Mock()
        mock_response.status_code = status_code
        mock_response.json = mock.Mock(return_value=json_data or {})

        mock_client = mock.AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = mock.AsyncMock(return_value=mock_response)
        return mock_client

    def test_premium_true_when_entitlement_has_expiry(self):
        payload = {
            "subscriber": {
                "entitlements": {
                    "premium": {"expires_date": "2027-01-01T00:00:00Z"}
                }
            }
        }
        mock_client = self._mock_client(200, payload)
        with mock.patch.object(billing.httpx, "AsyncClient", return_value=mock_client):
            response = _run(billing.check_user_subscription(app_user_id="user-1", authorization=_auth("user-1")))

        body = _body(response)
        self.assertTrue(body["success"])
        self.assertTrue(body["premium"])
        self.assertIn("premium", body["entitlements"])

    def test_premium_false_when_no_matching_entitlement(self):
        payload = {"subscriber": {"entitlements": {}}}
        mock_client = self._mock_client(200, payload)
        with mock.patch.object(billing.httpx, "AsyncClient", return_value=mock_client):
            response = _run(billing.check_user_subscription(app_user_id="user-2", authorization=_auth("user-2")))

        body = _body(response)
        self.assertTrue(body["success"])
        self.assertFalse(body["premium"])

    def test_non_200_from_revenuecat_reports_failure_without_premium(self):
        mock_client = self._mock_client(404, {})
        with mock.patch.object(billing.httpx, "AsyncClient", return_value=mock_client):
            response = _run(billing.check_user_subscription(app_user_id="user-3", authorization=_auth("user-3")))

        body = _body(response)
        self.assertFalse(body["success"])
        self.assertFalse(body["premium"])
        self.assertEqual(body["status_code"], 404)


    def test_lifetime_entitlement_has_premium_access(self):
        payload = {"subscriber": {"entitlements": {"pro": {
            "expires_date": None, "purchase_date": "2026-01-01T00:00:00Z",
            "product_identifier": "lifetime",
        }}}}
        with mock.patch.object(billing.httpx, "AsyncClient", return_value=self._mock_client(200, payload)):
            response = _run(billing.check_user_subscription(app_user_id="user-life", authorization=_auth("user-life")))
        self.assertTrue(_body(response)["premium"])

    def test_expired_entitlement_does_not_grant_access(self):
        payload = {"subscriber": {"entitlements": {"premium": {
            "expires_date": "2020-01-01T00:00:00Z", "purchase_date": "2019-12-01T00:00:00Z",
        }}}}
        with mock.patch.object(billing.httpx, "AsyncClient", return_value=self._mock_client(200, payload)):
            response = _run(billing.check_user_subscription(app_user_id="user-old", authorization=_auth("user-old")))
        self.assertFalse(_body(response)["premium"])

    def test_lookup_requires_account_owner(self):
        with mock.patch.object(billing.httpx, "AsyncClient", side_effect=AssertionError("must not call RevenueCat")):
            unauthenticated = _run(billing.check_user_subscription(app_user_id="user-1", authorization=None))
            other_user = _run(billing.check_user_subscription(app_user_id="user-1", authorization=_auth("user-2")))
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(other_user.status_code, 403)


class TestFailSoftOnError(unittest.TestCase):
    """Test 3: a network error/exception must hit the documented fail-soft path, not crash."""

    def setUp(self):
        self._orig_key = billing.REVENUECAT_API_KEY
        billing.REVENUECAT_API_KEY = "fake_prod_key_for_test"

    def tearDown(self):
        billing.REVENUECAT_API_KEY = self._orig_key

    def test_network_exception_fails_closed(self):
        mock_client = mock.AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = mock.AsyncMock(side_effect=ConnectionError("RevenueCat unreachable"))

        with mock.patch.object(billing.httpx, "AsyncClient", return_value=mock_client):
            # Must not raise: the endpoint has to handle the exception internally.
            response = _run(billing.check_user_subscription(app_user_id="user-4", authorization=_auth("user-4")))

        body = _body(response)
        self.assertFalse(body["success"])
        self.assertFalse(body["premium"])
        self.assertEqual(response.status_code, 503)


class TestNoHardcodedKeyLeaksWithoutEnvVar(unittest.TestCase):
    """Test 4: with REVENUECAT_API_KEY unset, no hardcoded test/sandbox key is used or exposed."""

    def setUp(self):
        self._orig_key = billing.REVENUECAT_API_KEY

    def tearDown(self):
        billing.REVENUECAT_API_KEY = self._orig_key
        importlib.reload(billing)

    def test_source_has_no_hardcoded_sandbox_key_literal(self):
        source = (BACKEND_DIR / "billing.py").read_text(encoding="utf-8")
        self.assertNotIn("goog_sandbox_testkey_123456", source)
        self.assertNotRegex(
            source,
            r'os\.getenv\(\s*"REVENUECAT_API_KEY"\s*,\s*"[^"]+"\s*\)',
            "REVENUECAT_API_KEY must not fall back to a hardcoded non-empty literal",
        )

    def test_missing_env_var_yields_empty_key_and_sandbox_response(self):
        env_without_key = {k: v for k, v in os.environ.items() if k != "REVENUECAT_API_KEY"}
        with mock.patch.dict(os.environ, env_without_key, clear=True):
            importlib.reload(billing)
            self.assertEqual(billing.REVENUECAT_API_KEY, "")

            # No key configured must never attempt a real network call.
            with mock.patch.object(billing.httpx, "AsyncClient", side_effect=AssertionError("must not call RevenueCat")):
                response = _run(billing.check_user_subscription(app_user_id="user-5", authorization=_auth("user-5")))

        body = _body(response)
        self.assertEqual(response.status_code, 503)
        self.assertFalse(body.get("success"))
        self.assertFalse(body.get("premium"))


if __name__ == "__main__":
    unittest.main()
