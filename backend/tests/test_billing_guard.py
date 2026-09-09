"""
Offline tests for the RevenueCat sandbox-key guard (billing_guard.py) and the
fail-soft behaviour of billing.check_user_subscription.

    python -m unittest tests.test_billing_guard          # from backend/
    python -m unittest backend.tests.test_billing_guard  # from repo root
"""

import asyncio
import json
import unittest
from unittest.mock import patch

try:
    from billing_guard import looks_like_sandbox_key, is_production_env, sandbox_key_status
    import billing
except ImportError:  # running from repo root
    from backend.billing_guard import looks_like_sandbox_key, is_production_env, sandbox_key_status
    from backend import billing


class SandboxKeyDetection(unittest.TestCase):
    def test_placeholder_and_missing_keys_are_sandbox(self):
        for k in ("goog_sandbox_testkey_123456", "", "   ", None, "APPL_sandbox_x"):
            self.assertTrue(looks_like_sandbox_key(k), k)

    def test_real_looking_key_is_not_sandbox(self):
        for k in ("goog_ABCdef123456789", "appl_LiVeKeyZ9", "strp_prod_key_001"):
            self.assertFalse(looks_like_sandbox_key(k), k)


class ProductionEnvDetection(unittest.TestCase):
    def test_known_vars_flag_production(self):
        self.assertTrue(is_production_env({"ENVIRONMENT": "production"}))
        self.assertTrue(is_production_env({"RAILWAY_ENVIRONMENT": "prod"}))
        self.assertTrue(is_production_env({"APP_ENV": "Production"}))

    def test_non_production_or_empty_is_false(self):
        self.assertFalse(is_production_env({}))
        self.assertFalse(is_production_env({"ENVIRONMENT": "staging"}))
        self.assertFalse(is_production_env({"ENV": "dev"}))


class KeyStatusMessage(unittest.TestCase):
    def test_real_key_is_ok_and_silent(self):
        self.assertEqual(sandbox_key_status("goog_realKey123", {}), ("ok", None))

    def test_sandbox_in_production_is_error(self):
        level, msg = sandbox_key_status("goog_sandbox_x", {"ENVIRONMENT": "production"})
        self.assertEqual(level, "error")
        self.assertIn("PRODUKSJON", msg)

    def test_sandbox_outside_production_is_warning(self):
        level, msg = sandbox_key_status("", {})
        self.assertEqual(level, "warn")
        self.assertIn("sandbox", msg.lower())


def _call(**kw):
    resp = asyncio.run(billing.check_user_subscription(**kw))
    return json.loads(bytes(resp.body))


class BillingEndpointFailSoft(unittest.TestCase):
    def test_sandbox_key_short_circuits_without_network(self):
        with patch.object(billing, "REVENUECAT_SANDBOX", True):
            body = _call(app_user_id="u1")
        self.assertFalse(body["premium"])
        self.assertTrue(body["sandbox"])

    def test_provider_outage_grants_temporary_grace_and_never_raises(self):
        with patch.object(billing, "REVENUECAT_SANDBOX", False), \
             patch.object(billing.httpx, "AsyncClient", side_effect=RuntimeError("boom")):
            body = _call(app_user_id="u1")
        self.assertTrue(body["premium"])
        self.assertTrue(body["offline_fallback"])

    def test_missing_app_user_id_is_a_clean_400_not_a_crash(self):
        resp = asyncio.run(billing.check_user_subscription(app_user_id=""))
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
