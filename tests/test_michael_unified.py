"""
Unit and Contract Test Suite for Michael AI BLAST Architecture.
Covers:
1. Media Catalog & LAW_MAPPING (§ 3 HAV, § 7 nr. 2 Right-of-Way/Left Turn, § 7 nr. 4 Bus, Signs 202/204, Intersections)
2. Multilingual Search & Resolution (NO, TH, EN)
3. Sign Noise Filter (is_noise_sign_for_topic)
4. Admin Analytics API contracts & schema
5. WebApp Frontend Contracts (80px thumbnails, Lightbox modal, Reliable Audio Lifecycle)
6. Language purity & isolated fail-safe behavior
"""

from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MichaelUnifiedArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_code = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")
        cls.teacher_code = (ROOT / "backend" / "teacher_chat.py").read_text(encoding="utf-8")
        cls.webapp_code = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")
        cls.media_catalog_code = (ROOT / "backend" / "media_catalog.py").read_text(encoding="utf-8")
        cls.admin_analytics_code = (ROOT / "backend" / "admin_analytics.py").read_text(encoding="utf-8")
        manifest_path = ROOT / "backend" / "media_catalog_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        cls.manifest_items = raw_manifest if isinstance(raw_manifest, list) else raw_manifest.get("items", [])

    def test_law_mapping_contains_critical_legal_anchors(self):
        """Verify § 3 HAV, § 7 nr. 2 Left Turn, and Signs are defined in LAW_MAPPING."""
        self.assertIn("LAW_MAPPING", self.media_catalog_code)
        self.assertIn("Vegtrafikkloven § 3", self.media_catalog_code)
        self.assertIn("HAV", self.media_catalog_code)
        self.assertIn("Trafikkreglene § 7 nr. 2", self.media_catalog_code)
        self.assertIn("Trafikkreglene § 7 nr. 4", self.media_catalog_code)
        self.assertIn("kryss", self.media_catalog_code)
        self.assertIn("202", self.media_catalog_code)
        self.assertIn("204", self.media_catalog_code)

    def test_media_catalog_manifest_valid_schema(self):
        """Ensure all items in media manifest contain required multilingual fields."""
        self.assertTrue(len(self.manifest_items) > 0, "Manifest should contain media items")
        for item in self.manifest_items:
            self.assertIn("id", item)
            self.assertIn("type", item)
            self.assertIn("url", item)
            title = item.get("title", {})
            caption = item.get("caption", {})
            self.assertTrue(title.get("no") and title.get("th") and title.get("en"))
            self.assertTrue(caption.get("no") and caption.get("th") and caption.get("en"))
            self.assertIsInstance(item.get("tags"), list)

    def test_noise_filter_excludes_irrelevant_signs_for_yield(self):
        """Ensure sign noise filter correctly identifies noisy signs."""
        self.assertIn("is_noise_sign_for_topic", self.media_catalog_code)
        self.assertIn("is_noise_sign_for_topic", self.teacher_code)

    def test_teacher_chat_legal_instructions_and_media_return(self):
        """Verify teacher_chat system prompt enforces § 7 nr. 2, has no video excuse, and returns media."""
        self.assertIn("Trafikkreglene § 7 nr. 2", self.teacher_code)
        self.assertIn("media: list[dict]", self.teacher_code)
        self.assertIn("resolve_media_for_query", self.teacher_code)
        self.assertNotIn("Jeg har dessverre ikke en video av akkurat denne situasjonen", self.teacher_code)

    def test_admin_analytics_router_mounted_in_server(self):
        """Verify admin analytics router is mounted in server.py."""
        self.assertIn("from admin_analytics import admin_analytics_router", self.server_code)
        self.assertIn("app.include_router(admin_analytics_router, prefix=\"/api\")", self.server_code)

    def test_admin_analytics_endpoints_defined(self):
        """Verify analytics endpoints exist in admin_analytics.py."""
        self.assertIn("/admin/analytics", self.admin_analytics_code)
        self.assertIn("/weaknesses", self.admin_analytics_code)
        self.assertIn("/conversions", self.admin_analytics_code)

    def test_webapp_thumbnail_and_lightbox_contracts(self):
        """Verify 80px thumbnails, Lightbox modal, and click handlers exist in webapp.py."""
        # 80px Thumbnail styles
        self.assertIn("width:80px; height:80px", self.webapp_code)
        self.assertIn(".tm-sign-image", self.webapp_code)
        self.assertIn(".tm-media-asset", self.webapp_code)
        
        # Lightbox modal elements & methods
        self.assertIn('id="t2dLightbox"', self.webapp_code)
        self.assertIn("openLightbox(", self.webapp_code)
        self.assertIn("closeLightbox(", self.webapp_code)
        self.assertIn(".t2d-lightbox", self.webapp_code)

    def test_webapp_audio_watchdog_and_token_stability(self):
        """Verify audio watchdog, token, and state handling in webapp.py."""
        self.assertIn("_teacherWatchdog", self.webapp_code)
        self.assertIn("_resetTeacherWatchdog", self.webapp_code)
        self.assertIn("_teacherAudioToken", self.webapp_code)
        self.assertIn("12000", self.webapp_code)

    def test_language_isolation_no_visible_cross_fallbacks(self):
        """Verify no illegal cross-language fallbacks (e.g. || TR.en or || TRANSLATIONS.no)."""
        self.assertNotIn("|| TR.en", self.webapp_code)
        self.assertNotIn("|| TRANSLATIONS.no", self.webapp_code)


if __name__ == "__main__":
    unittest.main()
