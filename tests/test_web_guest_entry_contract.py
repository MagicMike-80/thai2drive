import re
import unittest
from pathlib import Path
from html.parser import HTMLParser


ROOT = Path(__file__).resolve().parents[1]
WEBAPP = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")


class _BalancedHtmlParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            raise AssertionError(f"Unbalanced HTML near closing </{tag}>")
        self.stack.pop()


class WebGuestEntryContractTests(unittest.TestCase):
    def test_auth_screen_exposes_localized_guest_entry(self):
        self.assertIn('onclick="enterGuest()"', WEBAPP)
        self.assertIn('data-key="auth_guest_btn"', WEBAPP)
        self.assertIn('data-key="auth_guest_hint"', WEBAPP)

        for key in ("auth_guest_btn", "auth_guest_hint"):
            match = re.search(rf"{key}:\s*\{{([^}}]+)\}}", WEBAPP)
            self.assertIsNotNone(match, key)
            values = match.group(1)
            self.assertIn("th:", values)
            self.assertIn("no:", values)
            self.assertIn("en:", values)

    def test_auth_screen_markup_remains_balanced(self):
        start = WEBAPP.index('<!-- ═══ AUTH SCREEN ═══ -->')
        end = WEBAPP.index('<!-- ═══ HOME SCREEN ═══ -->', start)
        parser = _BalancedHtmlParser()
        parser.feed(WEBAPP[start:end])
        self.assertEqual([], parser.stack)

    def test_guest_uses_persistent_random_device_id(self):
        helper = WEBAPP[
            WEBAPP.index("function ensureGuestDeviceId()"):
            WEBAPP.index("async function doLogin()")
        ]
        self.assertIn("_ls.get('t2d_guest_device_id')", helper)
        self.assertIn("window.crypto.randomUUID", helper)
        self.assertIn("window.crypto.getRandomValues", helper)
        self.assertIn("_ls.set('t2d_guest_device_id', guestId)", helper)
        self.assertIn("deviceId = ensureGuestDeviceId();", helper)

    def test_guest_does_not_mint_auth_or_change_access_contract(self):
        guest = WEBAPP[
            WEBAPP.index("function enterGuest()"):
            WEBAPP.index("async function doLogin()")
        ]
        self.assertIn("token = null;", guest)
        self.assertIn("user = null;", guest)
        self.assertIn("enterApp();", guest)
        self.assertNotIn("/api/auth/signup", guest)
        self.assertNotIn("is_premium", guest)

        usage = (ROOT / "backend" / "usage.py").read_text(encoding="utf-8")
        self.assertIn("GUEST_LIFETIME_LIMIT    = 5", usage)
        self.assertIn("REGISTERED_DAILY_LIMIT  = 10", usage)


if __name__ == "__main__":
    unittest.main()
