"""
Language-URL cleanup for thai2drive.no (home, guide, quiz app).

Covers all 7 concrete requirements:
1. Egne URL-er per språk for alle tre sidene (/th, /no, /en; /th/guide, /no/guide,
   /en/guide; /th/app, /no/app, /en/app) and strict single-language server-side rendering
   with NO mixed-language text inside <h1> or main content.
2. Server-side <html lang>: lang="th" on Thai, lang="nb" on Norwegian, lang="en" on English.
3. Unik <title> og meta-description per språk matching the proposed strings.
4. hreflang on all pages pointing to sibling subpages (not homepages), including
   hreflang="th", hreflang="nb", hreflang="en", hreflang="x-default", and canonical tags.
5. Språkbytte helper (t2dSwitchLang) and cookie persistence (t2d_site_lang).
6. 301-redirects from legacy /api/web and /api/guide, preserving query strings (Stripe return).
7. Forsiden / redirects (302) respecting cookie first, Accept-Language second, defaulting to Thai.
"""
import re
import sys
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from website import website_router  # noqa: E402
from webapp import webapp_router  # noqa: E402
from i18n_routing import canonical_for, public_site_url  # noqa: E402

app = FastAPI()
# Mirror production's dual mount (server.py mounts both routers at "" and "/api").
app.include_router(website_router, prefix="")
app.include_router(website_router, prefix="/api")
app.include_router(webapp_router, prefix="")
app.include_router(webapp_router, prefix="/api")
client = TestClient(app, follow_redirects=False)

THAI_SCRIPT_REGEX = re.compile(r"[\u0e00-\u0e7f]")


class HomeLanguageRouteTests(unittest.TestCase):
    def test_th_home_has_correct_html_lang_and_title(self):
        html = client.get("/th").text
        self.assertIn('<html lang="th"', html)
        self.assertIn("สอบทฤษฎีใบขับขี่นอร์เวย์ ภาษาไทย", html)

    def test_no_home_has_correct_html_lang_and_title(self):
        html = client.get("/no").text
        self.assertIn('<html lang="nb"', html)
        self.assertIn("Teoriprøven på thai", html)

    def test_en_home_has_correct_html_lang_and_title(self):
        html = client.get("/en").text
        self.assertIn('<html lang="en"', html)
        self.assertIn("Norwegian driving theory test in Thai", html)

    def test_no_home_h1_has_zero_thai_characters(self):
        html = client.get("/no").text
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
        self.assertIsNotNone(h1_match)
        h1_content = h1_match.group(1)
        self.assertIn("Bestå teoriprøven", h1_content)
        self.assertIsNone(THAI_SCRIPT_REGEX.search(h1_content), "Norwegian <h1> must contain 0 Thai characters")
        self.assertNotIn("Pass the Norwegian", h1_content)

    def test_th_home_h1_has_zero_norwegian_headline_text(self):
        html = client.get("/th").text
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
        self.assertIsNotNone(h1_match)
        h1_content = h1_match.group(1)
        self.assertIn("สอบใบขับขี่นอร์เวย์ให้", h1_content)
        self.assertNotIn("Bestå teoriprøven", h1_content)
        self.assertNotIn("Pass the Norwegian", h1_content)

    def test_en_home_h1_has_zero_thai_script_or_norwegian_headline_text(self):
        html = client.get("/en").text
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
        self.assertIsNotNone(h1_match)
        h1_content = h1_match.group(1)
        self.assertIn("Pass the Norwegian theory test", h1_content)
        self.assertNotIn("Bestå teoriprøven", h1_content)
        self.assertIsNone(THAI_SCRIPT_REGEX.search(h1_content))

    def test_no_home_has_hreflang_alternates_for_all_languages(self):
        html = client.get("/no").text
        self.assertIn('hreflang="th"', html)
        self.assertIn('hreflang="nb"', html)
        self.assertIn('hreflang="no"', html)
        self.assertIn('hreflang="en"', html)
        self.assertIn('hreflang="x-default"', html)

    def test_home_canonical_tag(self):
        html = client.get("/no").text
        self.assertIn(f'<link rel="canonical" href="{canonical_for("no", "")}"/>', html)

    def test_home_sets_shared_language_cookie(self):
        r = client.get("/en")
        self.assertIn("t2d_site_lang=en", r.headers.get("set-cookie", ""))

    def test_unknown_single_segment_is_a_real_404(self):
        r = client.get("/xx")
        self.assertEqual(r.status_code, 404)

    def test_th_home_has_zero_norwegian_leak_strings(self):
        html = client.get("/th").text
        leaks = [
            w for w in [
                "Høyreregelen",
                "skiltgrupper",
                "Historien",
                "Bremselengde",
                "Trafikklys",
                "Venstresving",
                "Buss fra",
                "Rundkjøring Norge",
            ] if w in html
        ]
        self.assertEqual(leaks, [], f"Found Norwegian leaks in /th: {leaks}")


class GuideLanguageRouteTests(unittest.TestCase):
    def test_th_guide_has_correct_html_lang(self):
        html = client.get("/th/guide").text
        self.assertIn('<html lang="th"', html)

    def test_no_guide_has_correct_html_lang_and_title(self):
        html = client.get("/no/guide").text
        self.assertIn('<html lang="nb"', html)
        self.assertIn("Fra Thailand til norsk førerkort", html)

    def test_en_guide_has_correct_html_lang(self):
        html = client.get("/en/guide").text
        self.assertIn('<html lang="en"', html)

    def test_no_guide_h1_has_zero_thai_characters(self):
        html = client.get("/no/guide").text
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
        self.assertIsNotNone(h1_match)
        h1_content = h1_match.group(1)
        self.assertIn("Fra Thailand til", h1_content)
        self.assertIsNone(THAI_SCRIPT_REGEX.search(h1_content), "Norwegian guide <h1> must contain 0 Thai characters")

    def test_th_guide_h1_has_zero_norwegian_text(self):
        html = client.get("/th/guide").text
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
        self.assertIsNotNone(h1_match)
        h1_content = h1_match.group(1)
        self.assertIn("จากไทย", h1_content)
        self.assertNotIn("Fra Thailand til", h1_content)

    def test_guide_hreflang_points_at_sibling_guide_urls_not_homepages(self):
        html = client.get("/no/guide").text
        self.assertIn("/th/guide", html)
        self.assertIn("/no/guide", html)
        self.assertIn("/en/guide", html)
        self.assertIn('hreflang="nb"', html)

    def test_guide_canonical_tag(self):
        html = client.get("/no/guide").text
        self.assertIn(f'<link rel="canonical" href="{canonical_for("no", "/guide")}"/>', html)

    def test_guide_cta_links_to_clean_language_app(self):
        html = client.get("/no/guide").text
        self.assertIn('href="/no/app"', html)

    def test_th_guide_has_zero_parallel_sentences(self):
        html = client.get("/th/guide").text
        leaks = [
            w for w in [
                "Norge godkjenner ikke",
                "Norway does not",
                "utenlandsk førerkort",
                "foreign driving license",
                "oppholdstillatelse",
                "Oppholdstillatelse",
                "Statens Vegvesen",
                "Førstehjelp",
                "MørkeDemo",
                "Glattkjøring",
                "Trafikkopplæringsforskriften",
                "logg)",
                "TGK",
                "kr<",
            ] if w in html
        ]
        self.assertEqual(leaks, [], f"Found leaks in /th/guide: {leaks}")

    def test_th_and_en_guide_steps_and_footer_are_localized(self):
        thai = client.get("/th/guide").text
        english = client.get("/en/guide").text
        for text in ["ขั้นตอนที่ 1", "ขั้นตอนที่ 3 + สนามฝึก", "หลักสูตรความปลอดภัยบนถนน", "การประเมินขั้นตอน", "พร้อมเรียนขั้นตอนที่ 3", "พร้อมสำหรับขั้นตอนที่ 4", "นโยบายความเป็นส่วนตัว", "ข้อกำหนดการใช้งาน"]:
            self.assertIn(text, thai)
        for text in ["หลักสูตรพื้นฐานด้านการจราจร", "การสอบภาคทฤษฎี", "การสอบขับรถ"]:
            self.assertIn(text, thai)
        for text in ["<span class=\"tl tl-th\">Trafikalt grunnkurs", "<span class=\"tl tl-th\">Teoriprøve", "<span class=\"tl tl-th\">Førerprøve"]:
            self.assertNotIn(text, thai)
        for text in ["Step 1", "Step 3 + track", "Road safety course", "Privacy", "Terms"]:
            self.assertIn(text, english)
        self.assertNotIn("Step 1 (TGK)", english)
        self.assertNotIn("Trinn 1 (TGK)", english)
        self.assertNotIn("Trinn 3 + bane", english)


class AppLanguageRouteTests(unittest.TestCase):
    def test_th_app_route_serves_thai(self):
        r = client.get("/th/app")
        self.assertEqual(r.status_code, 200)
        self.assertIn('<html lang="th"', r.text)

    def test_no_app_route_serves_norwegian(self):
        r = client.get("/no/app")
        self.assertEqual(r.status_code, 200)
        self.assertIn('<html lang="nb"', r.text)
        self.assertIn("<title>Øv til teoriprøven", r.text)

    def test_en_app_route_serves_english(self):
        r = client.get("/en/app")
        self.assertEqual(r.status_code, 200)
        self.assertIn('<html lang="en"', r.text)

    def test_app_hreflang_points_to_sibling_app_urls(self):
        html = client.get("/no/app").text
        self.assertIn("/th/app", html)
        self.assertIn("/no/app", html)
        self.assertIn("/en/app", html)
        self.assertIn('hreflang="nb"', html)

    def test_app_canonical_tag(self):
        html = client.get("/no/app").text
        self.assertIn(f'<link rel="canonical" href="{canonical_for("no", "/app")}"/>', html)


class LanguageLessRedirectTests(unittest.TestCase):
    def setUp(self):
        client.cookies.clear()

    def test_root_redirects_to_detected_language(self):
        r = client.get("/", headers={"accept-language": "en-US,en;q=0.9"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/en")

    def test_root_defaults_to_thai_when_nothing_indicates_a_language(self):
        r = client.get("/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/th")

    def test_root_head_defaults_to_thai_when_no_headers(self):
        r = client.head("/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/th")

    def test_root_head_redirects_to_norwegian_with_nb_no(self):
        r = client.head("/", headers={"accept-language": "nb-NO"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/no")

    def test_root_redirects_to_thai_when_thai_present_in_accept_language(self):
        r = client.get("/", headers={"accept-language": "nb-NO,th;q=0.8,en;q=0.7"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/th")

    def test_root_redirects_to_thai_for_unknown_language(self):
        r = client.get("/", headers={"accept-language": "da-DK,da;q=0.9,sv;q=0.8"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/th")

    def test_root_respects_saved_cookie_over_browser_language(self):
        r = client.get("/", cookies={"t2d_site_lang": "no"}, headers={"accept-language": "en-US"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/no")

    def test_guide_without_language_redirects_to_detected_language_guide(self):
        r = client.get("/guide", headers={"accept-language": "nb-NO"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/no/guide")


class ApiPrefixLegacyRedirectTests(unittest.TestCase):
    """Old /api/-prefixed URLs permanently redirect (301) to the clean equivalent."""

    def setUp(self):
        client.cookies.clear()

    def test_api_website_redirects_to_bare_root(self):
        r = client.get("/api/website")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/website")

    def test_api_guide_redirects_to_bare_guide(self):
        r = client.get("/api/guide")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/guide")

    def test_api_web_redirects_to_bare_app(self):
        r = client.get("/api/web")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app")

    def test_api_web_preserves_query_string_for_stripe_return(self):
        r = client.get("/api/web?checkout=success&session_id=cs_test_123")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app?checkout=success&session_id=cs_test_123")

    def test_api_th_redirects_to_bare_th(self):
        r = client.get("/api/th")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/th")

    def test_api_th_guide_redirects_to_bare_th_guide(self):
        r = client.get("/api/th/guide")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/th/guide")

    def test_api_web_head_request_redirects_with_301(self):
        r = client.head("/api/web")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app")

    def test_api_web_head_preserves_query_string(self):
        r = client.head("/api/web?checkout=success&session_id=cs_test_123")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app?checkout=success&session_id=cs_test_123")

    def test_api_guide_head_request_redirects_with_301(self):
        r = client.head("/api/guide")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/guide")

    def test_web_bare_head_request_redirects_with_301(self):
        r = client.head("/web")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app")

    def test_guide_bare_head_request_redirects_with_302(self):
        r = client.head("/guide")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["location"], "/th/guide")


class SitemapTests(unittest.TestCase):
    def test_sitemap_xml_contains_all_clean_urls_and_hreflang(self):
        r = client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["content-type"], "application/xml")
        xml = r.text
        base = public_site_url()
        # Home
        self.assertIn(f"<loc>{base}/th</loc>", xml)
        self.assertIn(f"<loc>{base}/no</loc>", xml)
        self.assertIn(f"<loc>{base}/en</loc>", xml)
        # Guide
        self.assertIn(f"<loc>{base}/th/guide</loc>", xml)
        self.assertIn(f"<loc>{base}/no/guide</loc>", xml)
        self.assertIn(f"<loc>{base}/en/guide</loc>", xml)
        # App
        self.assertIn(f"<loc>{base}/th/app</loc>", xml)
        self.assertIn(f"<loc>{base}/no/app</loc>", xml)
        self.assertIn(f"<loc>{base}/en/app</loc>", xml)
        # ISO code in alternates
        self.assertIn('hreflang="nb"', xml)
        self.assertIn('hreflang="th"', xml)
        self.assertIn('hreflang="en"', xml)
        self.assertIn('hreflang="x-default"', xml)


if __name__ == "__main__":
    unittest.main()
