"""
Etappe 1 — clean per-language entry points and exam-mode language forcing.
Etappe 2 (language cleanup) — /web* now redirects to /app*; /app* serves the
content and gets server-side <html lang>/<title>/meta/hreflang per language.
----------------------------------------------------------------------------
- /app, /app/no, /app/th, /app/en: same SPA, each with a different default
  initial language (still fully overridable by the student's stored
  preference and the flag buttons).
- /web, /web/no, /web/th, /web/en: legacy URLs, now 301 redirects to the
  matching /app* URL with the query string preserved (critical for the
  Stripe checkout return query params).
- Exam mode ("Simulert prøvedag"): question and option TEXT must be pure
  Norwegian regardless of the student's selected UI language — matching the
  real Statens vegvesen theory test. UI chrome (buttons, timer, labels)
  keeps following the student's chosen language; only exam content is forced.

Route tests run through a real FastAPI TestClient (no network, no DB —
webapp.py has no import-time DB dependency). The exam-mode assertions are
text-contract checks on WEBAPP_HTML, matching this repo's existing
convention for verifying embedded JS (see tests/test_neon_design_contract.py,
tests/test_sign_api_contract.py) since there is no JS execution harness for
this file.
"""
import sys
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from webapp import WEBAPP_HTML, webapp_router

app = FastAPI()
# Mirror production's dual mount (server.py mounts webapp_router at both ""
# and "/api") so /api/-prefixed legacy paths correctly redirect to the bare
# clean path instead of 404ing inside this isolated test app.
app.include_router(webapp_router, prefix="")
app.include_router(webapp_router, prefix="/api")
client = TestClient(app, follow_redirects=False)


class LegacyWebRedirectTests(unittest.TestCase):
    def test_web_redirects_permanently_to_app(self):
        r = client.get("/web")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app")

    def test_web_no_redirects_to_app_no(self):
        r = client.get("/web/no")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app/no")

    def test_web_th_redirects_to_app_th(self):
        r = client.get("/web/th")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app/th")

    def test_web_en_redirects_to_app_en(self):
        r = client.get("/web/en")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app/en")

    def test_web_redirect_preserves_query_string_for_stripe_return(self):
        r = client.get("/web?checkout=success&session_id=cs_test_123")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app?checkout=success&session_id=cs_test_123")

    def test_api_web_also_redirects_via_the_api_mount(self):
        r = client.get("/api/web")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app")


class ApiPrefixRedirectsToCleanAppUrlTests(unittest.TestCase):
    """Old /api/app* access permanently redirects to the bare /app* URL."""

    def test_api_app_redirects_to_bare_app(self):
        r = client.get("/api/app")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app")

    def test_api_app_no_redirects_to_bare_app_no(self):
        r = client.get("/api/app/no")
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r.headers["location"], "/app/no")


class LanguageEntryPointRouteTests(unittest.TestCase):
    def test_app_default_route_defaults_to_thai(self):
        html = client.get("/app").text
        self.assertIn("_ls.get('t2d_lang') || 'th'", html)

    def test_app_no_route_defaults_to_norwegian(self):
        html = client.get("/app/no").text
        self.assertIn("_ls.get('t2d_lang') || 'no'", html)

    def test_app_th_route_defaults_to_thai(self):
        html = client.get("/app/th").text
        self.assertIn("_ls.get('t2d_lang') || 'th'", html)

    def test_app_en_route_defaults_to_english(self):
        html = client.get("/app/en").text
        self.assertIn("_ls.get('t2d_lang') || 'en'", html)

    def test_app_no_route_goes_through_same_install_pipeline_as_app(self):
        # Regression guard: the new routes must not be a stripped-down copy —
        # they should carry the same stopping-distance + studybook installers
        # as /app (proven here by the same unique marker /app's own test uses).
        html = client.get("/app/no").text
        self.assertEqual(html.count('id="screenStopping"'), 1)

    def test_app_no_route_has_deploy_version_substituted(self):
        html = client.get("/app/no").text
        self.assertNotIn("__DEPLOY_VERSION__", html)

    def test_app_no_route_has_correct_html_lang(self):
        html = client.get("/app/no").text
        self.assertIn('<html lang="nb"', html)

    def test_app_th_route_has_correct_html_lang(self):
        html = client.get("/app/th").text
        self.assertIn('<html lang="th"', html)

    def test_app_en_route_has_correct_html_lang(self):
        html = client.get("/app/en").text
        self.assertIn('<html lang="en"', html)

    def test_app_no_route_has_norwegian_title_and_description(self):
        html = client.get("/app/no").text
        self.assertIn("<title>Øv til teoriprøven", html)
        self.assertNotIn("<title>Thai2Drive</title>", html)

    def test_app_routes_carry_hreflang_alternates(self):
        html = client.get("/app/no").text
        self.assertIn('hreflang="th"', html)
        self.assertIn('hreflang="no"', html)
        self.assertIn('hreflang="en"', html)
        self.assertIn('hreflang="x-default"', html)

    def test_app_sets_shared_language_cookie(self):
        r = client.get("/app/en")
        self.assertIn("t2d_site_lang=en", r.headers.get("set-cookie", ""))


class ExamModeForcesNorwegianContentTests(unittest.TestCase):
    def test_question_text_picker_is_exam_aware(self):
        self.assertIn("function pickQuestionLang(obj)", WEBAPP_HTML)

    def test_field_picker_is_exam_aware(self):
        self.assertIn("function pickFieldForQuestion(q, base)", WEBAPP_HTML)

    def test_exam_mode_forces_norwegian_suffix_for_fields(self):
        self.assertIn("isExamMode ? 'no' : appLang", WEBAPP_HTML)

    def test_render_question_uses_exam_aware_pickers_for_question_text(self):
        self.assertIn("pickQuestionLang(q.question)", WEBAPP_HTML)
        self.assertIn("pickFieldForQuestion(q, 'question_text')", WEBAPP_HTML)

    def test_render_question_uses_exam_aware_picker_for_abcd_fallback_options(self):
        self.assertIn("pickFieldForQuestion(q, base)", WEBAPP_HTML)

    def test_render_question_uses_exam_aware_picker_for_structured_options(self):
        self.assertIn("pickQuestionLang(o.text)", WEBAPP_HTML)


class AIIdentityAndHumanHandoffTests(unittest.TestCase):
    def test_chat_header_names_michael_as_ai_in_all_three_languages(self):
        self.assertIn("teacher_name:{th:'Michael AI (ครู AI • 24 ชม.)', no:'Michael AI (AI-lærer • 24/7)', en:'Michael AI (AI Teacher • 24/7)'}", WEBAPP_HTML)

    def test_contact_human_button_translations_are_language_isolated(self):
        self.assertIn("contact_human_btn:{th:'ส่งข้อความถึง Michael ตัวจริง', no:'Send melding til Ekte Michael', en:'Send message to Real Michael'}", WEBAPP_HTML)

    def test_contact_human_button_is_not_persistent_in_clean_chat_header(self):
        self.assertNotIn('id="contactHumanBtn"', WEBAPP_HTML)

    def test_contact_human_handler_posts_to_the_new_endpoint(self):
        self.assertIn("function contactHumanMichael()", WEBAPP_HTML)
        self.assertIn("/api/teacher/contact-human", WEBAPP_HTML)


if __name__ == "__main__":
    unittest.main()
