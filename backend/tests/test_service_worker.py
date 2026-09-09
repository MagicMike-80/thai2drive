"""
Offline guard tests for service-worker.js.

Static source assertions — no browser needed. They exist to catch a regression
of the iOS-Safari rule (no SW interception of /api/, Range, or media) and to
pin the shape of the v1.1.0 offline-quiz allowlist. Behavioural coverage lives
in tests/sw_behavior.test.mjs (run with node).

    python -m unittest tests.test_service_worker
    python -m unittest backend.tests.test_service_worker
"""

import re
import unittest
from pathlib import Path

SW = (Path(__file__).resolve().parent.parent / "service-worker.js").read_text(encoding="utf-8")

ALLOWLIST = [
    "/api/questions/random",
    "/api/traffic-signs",
    "/api/categories",
    "/api/glossary",
    "/api/lessons/culture",
]
MEDIA_EXTS = ("mp3", "m4a", "mp4", "wav", "ogg", "aac", "webm")


class IosSafariRuleIntact(unittest.TestCase):
    def test_blanket_api_block_still_present(self):
        self.assertIn("url.pathname.startsWith('/api/')", SW)
        # the blanket block must still be a bare pass-through `return;`
        self.assertRegex(SW, r"startsWith\('/api/'\)[^\n]*\)\s*\{\s*return;")

    def test_range_and_media_passthrough_still_present(self):
        self.assertIn("if (hasRange)", SW)
        self.assertIn("if (isMedia)", SW)
        self.assertRegex(SW, r"MEDIA_RE\s*=\s*/\\\.\(mp3\|m4a\|mp4")


class OfflineAllowlist(unittest.TestCase):
    def test_all_five_public_endpoints_are_listed(self):
        for path in ALLOWLIST:
            self.assertIn(f"'{path}'", SW)

    def test_allowlist_contains_no_media_paths(self):
        block = re.search(r"OFFLINE_API_ALLOWLIST\s*=\s*\[(.*?)\]", SW, re.S).group(1)
        for ext in MEDIA_EXTS:
            self.assertNotIn(f".{ext}", block)

    def test_allowlist_branch_excludes_range_and_media(self):
        self.assertRegex(SW, r"isAllowlistedApi\(url\)\s*&&\s*!hasRange\s*&&\s*!isMedia")

    def test_network_first_falls_back_to_cache(self):
        self.assertIn("function networkFirst(event)", SW)
        self.assertRegex(SW, r"fetch\(event\.request\)[\s\S]*\.catch\(\(\)\s*=>\s*caches\.match\(event\.request,\s*\{\s*ignoreSearch:\s*true")


class CacheVersioning(unittest.TestCase):
    def test_cache_names_bumped_past_v1_0_6(self):
        self.assertIn("thai2drive-offline-v1.1.0", SW)
        self.assertIn("thai2drive-api-v1.1.0", SW)
        self.assertNotIn("v1.0.6", SW)

    def test_activate_keeps_both_caches(self):
        self.assertRegex(SW, r"keep\s*=\s*new Set\(\[CACHE_NAME,\s*API_CACHE_NAME\]\)")


if __name__ == "__main__":
    unittest.main()
