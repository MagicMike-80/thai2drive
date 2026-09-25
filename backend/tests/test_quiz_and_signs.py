"""
Offline tests for the quiz engine and the traffic-sign tool (web + backend).

  1. Quiz paywall  - GET /api/questions/random?mode=exam (the full test) needs ACTIVE access,
                     judged from the database, not from the token. Practice stays open.
  2. Language isolation - quiz_language.py + ?lang= filter + the question bank audit.
  3. Sign images  - every image in backend/sign_images answers HTTP 200 (valid JPEG/PNG),
                     every catalog sign resolves to an image, traversal is refused.

In-memory MongoDB (mongomock-motor); no network, no real keys, no production database.

    cd backend && python -m pytest tests/test_quiz_and_signs.py -v
"""

import json
import os
import re
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from unittest.mock import patch

os.environ.setdefault("MONGO_URL", "mongodb://127.0.0.1:1/?serverSelectionTimeoutMS=200")
os.environ.setdefault("DB_NAME", "t2d_quiz_signs_test")

try:
    from fastapi.testclient import TestClient
    from mongomock_motor import AsyncMongoMockClient
    import server
    import ai_routes
    import quiz_language as ql
    _IMPORT_ERROR = None
except Exception as exc:  # missing deps in this environment
    server = ai_routes = ql = None
    _IMPORT_ERROR = exc

BACKEND = Path(__file__).resolve().parent.parent
REPO = BACKEND.parent
SIGN_DIR = BACKEND / "sign_images"


def _iso(days):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def q2(qid, th_q, th_opts, image=True, no_q="Hva betyr skiltet?", en_q="What does the sign mean?"):
    """A v2 question document. th_opts: four Thai option texts."""
    return {
        "id": qid,
        "question": {"no": no_q, "th": th_q, "en": en_q},
        "options": [
            {"id": i, "text": {"no": f"Alternativ {i}", "th": th, "en": f"Option {i}"}}
            for i, th in zip("ABCD", th_opts)
        ],
        "correctOptionId": "A",
        "explanation": {"no": "Forklaring", "th": "คำอธิบาย", "en": "Explanation"},
        "bildeUrl": "/api/sign-images/202_0.jpg" if image else None,
        "category": "Skilt",
        "difficulty": "hard",
    }


CLEAN_TH = ["ให้ทาง", "หยุด", "ห้ามเข้า", "จอดได้"]
CLEAN_TH_PAREN = ["ให้ทาง (vikeplikt)", "หยุด (stopp)", "ห้ามเข้า", "จอดได้"]
DIRTY_TH = ["Holde samme fart", "หยุด", "ห้ามเข้า", "จอดได้"]


# ══════════════════════════════════════════════════════════════════════════════
#  Pure language-isolation rules
# ══════════════════════════════════════════════════════════════════════════════
@unittest.skipIf(ql is None, f"quiz_language not importable here: {_IMPORT_ERROR!r}")
class LanguageIsolationRules(unittest.TestCase):
    def test_thai_only_text_is_clean(self):
        self.assertIsNone(ql.field_violation("ให้ทางแก่รถที่มาจากทางขวา", "th"))

    def test_norwegian_term_in_parentheses_is_allowed(self):
        self.assertIsNone(ql.field_violation("ให้ทาง (vikeplikt) แก่รถทุกคัน", "th"))

    def test_norwegian_or_english_outside_parentheses_is_a_violation(self):
        self.assertIn("latin_outside_parentheses", ql.field_violation("Holde samme fart", "th"))
        self.assertIn("latin_outside_parentheses", ql.field_violation("ขับด้วย fart ต่ำ", "th"))
        self.assertIn("latin_outside_parentheses", ql.field_violation("Speed limit 50", "th"))

    def test_thai_field_without_any_thai_is_a_violation(self):
        self.assertIsNotNone(ql.field_violation("Kjørefelt", "th"))

    def test_units_acronyms_and_numbers_are_neutral(self):
        for text in ("50 กม./ชม.", "ความเร็ว 50 km/t", "ป้าย EU", "เปิด ABS", "30"):
            self.assertIsNone(ql.field_violation(text, "th"), text)

    def test_thai_letters_never_leak_into_norwegian_or_english(self):
        self.assertEqual(ql.field_violation("Du må stoppe ให้ทาง", "no"), "thai_in_no")
        self.assertEqual(ql.field_violation("Stop ให้ทาง", "en"), "thai_in_en")
        self.assertIsNone(ql.field_violation("Du må stoppe", "no"))

    def test_empty_fields_are_not_judged(self):
        self.assertIsNone(ql.field_violation("", "th"))
        self.assertIsNone(ql.field_violation(None, "th"))

    def test_question_level_checks_question_options_and_explanation(self):
        good = q2("g", "ป้ายนี้หมายความว่าอะไร", CLEAN_TH_PAREN)
        self.assertTrue(ql.is_language_isolated(good, "th"))
        bad_opt = q2("b1", "ป้ายนี้หมายความว่าอะไร", DIRTY_TH)
        self.assertEqual(ql.question_violations(bad_opt, "th")[0].split(":")[0], "option A")
        bad_q = q2("b2", "Hva betyr ป้าย", CLEAN_TH)
        self.assertFalse(ql.is_language_isolated(bad_q, "th"))
        bad_expl = q2("b3", "ป้ายนี้หมายความว่าอะไร", CLEAN_TH)
        bad_expl["explanation"]["th"] = "You must stop"
        self.assertTrue(any(v.startswith("explanation") for v in ql.question_violations(bad_expl, "th")))

    def test_filter_is_a_noop_without_a_known_language(self):
        qs = [q2("b", "x", DIRTY_TH)]
        self.assertEqual(ql.filter_isolated(qs, None), qs)
        self.assertEqual(ql.filter_isolated(qs, "xx"), qs)
        self.assertEqual(ql.filter_isolated(qs, "th"), [])


# ══════════════════════════════════════════════════════════════════════════════
#  The question bank itself (the dump the production database was seeded from)
# ══════════════════════════════════════════════════════════════════════════════
@unittest.skipIf(server is None, f"server.py not importable here: {_IMPORT_ERROR!r}")
class QuestionBankLanguageAudit(unittest.TestCase):
    """Ratchet: the share of Thai-mode questions that break isolation may only go DOWN.

    The serving filter (?lang=th) hides every offender from the learner; this test keeps the
    content backlog visible and stops new offenders from being added to the bank.
    """

    MAX_BAD_TH = 106      # measured 106 of 1585 on the current dump
    MAX_BAD_NO_EN = 0     # measured 0: Thai never leaks into no/en

    @classmethod
    def setUpClass(cls):
        raw = json.loads((BACKEND / "scripts" / "image_audit" / "all_questions.json").read_text(encoding="utf-8"))
        cls.bank = [server.normalize_question(q) for q in raw]

    def test_bank_is_loaded(self):
        self.assertGreater(len(self.bank), 1500)

    def test_thai_mode_offenders_do_not_grow(self):
        bad = [q["id"] for q in self.bank if not ql.is_language_isolated(q, "th")]
        print(f"\n[audit] Thai isolation: {len(bad)} of {len(self.bank)} questions break the rule (limit {self.MAX_BAD_TH})")
        self.assertLessEqual(len(bad), self.MAX_BAD_TH, "new Thai-mode language violations were added")

    def test_no_thai_characters_in_norwegian_or_english(self):
        for lang in ("no", "en"):
            bad = [q["id"] for q in self.bank if not ql.is_language_isolated(q, lang)]
            self.assertLessEqual(len(bad), self.MAX_BAD_NO_EN, f"Thai text found in {lang} fields: {bad[:5]}")

    def test_the_filter_leaves_a_large_clean_pool(self):
        clean = ql.filter_isolated(self.bank, "th")
        self.assertGreater(len(clean), len(self.bank) * 0.9)
        with_image = [q for q in clean if q.get("bildeUrl")]  # the quiz only serves questions with an image
        self.assertGreater(len(with_image), 600)


# ══════════════════════════════════════════════════════════════════════════════
#  Routes: paywall and language filter on /api/questions/random
# ══════════════════════════════════════════════════════════════════════════════
@unittest.skipIf(server is None, f"server.py not importable here: {_IMPORT_ERROR!r}")
class QuizRouteBase(unittest.TestCase):
    def setUp(self):
        self._orig_db, self._orig_ai_db = server.db, ai_routes._db
        server.db = AsyncMongoMockClient()["t2d_quiz_signs_test"]
        ai_routes._db = server.db
        self._env = patch.dict(os.environ, {"RAILWAY_ENVIRONMENT": "", "ENVIRONMENT": "", "FREE_PROMO_MODE": ""})
        self._env.start()
        self.client = TestClient(server.app)

    def tearDown(self):
        self._env.stop()
        server.db, ai_routes._db = self._orig_db, self._orig_ai_db

    def run_db(self, coro):
        import asyncio
        return asyncio.new_event_loop().run_until_complete(coro)

    def add_user(self, uid, **fields):
        self.run_db(server.db.users.insert_one({"id": uid, "email": f"{uid}@example.com", "name": uid, **fields}))

    def auth(self, uid, **claims):
        return {"Authorization": f"Bearer {server.create_token(uid, f'{uid}@example.com', **claims)}"}

    def seed_questions(self, n_clean=60, n_dirty=20):
        docs = [q2(f"c{i}", "ป้ายนี้หมายความว่าอะไร", CLEAN_TH_PAREN) for i in range(n_clean)]
        docs += [q2(f"d{i}", "ป้ายนี้หมายความว่าอะไร", DIRTY_TH) for i in range(n_dirty)]
        self.run_db(server.db.questions.insert_many(docs))


class ExamRequiresActiveSubscription(QuizRouteBase):
    """Web: startExam() is gated in the UI; the SERVER must gate it too (a client check is no lock)."""

    EXAM = "/api/questions/random?count=45&has_image=true&mode=exam"

    def setUp(self):
        super().setUp()
        self.seed_questions(60, 0)

    def test_guest_gets_402_register(self):
        r = self.client.get(self.EXAM, headers={"X-Device-ID": "dev-1"})
        self.assertEqual(r.status_code, 402, r.text)
        self.assertEqual(r.json()["detail"]["gate"], "register")

    def test_guest_without_device_id_cannot_bypass_the_legacy_open_path(self):
        r = self.client.get(self.EXAM)
        self.assertEqual(r.status_code, 402, r.text)

    def test_garbage_token_gets_402(self):
        r = self.client.get(self.EXAM, headers={"Authorization": "Bearer garbage"})
        self.assertEqual(r.status_code, 402, r.text)

    def test_registered_free_user_gets_402_upgrade(self):
        self.add_user("free")
        r = self.client.get(self.EXAM, headers=self.auth("free"))
        self.assertEqual(r.status_code, 402, r.text)
        self.assertEqual(r.json()["detail"], {"error": "premium_required", "gate": "upgrade", "tier": "registered"})

    def test_token_claiming_premium_does_not_help_when_database_says_free(self):
        self.add_user("liar")  # e.g. refunded: the DB has no premium, the token still says so
        r = self.client.get(self.EXAM, headers=self.auth("liar", is_premium=True, premium_until=_iso(30)))
        self.assertEqual(r.status_code, 402, r.text)

    def test_expired_subscription_gets_402(self):
        self.add_user("old", is_premium=True, premium_expires_at=_iso(-1))
        r = self.client.get(self.EXAM, headers=self.auth("old", is_premium=True, premium_until=_iso(5)))
        self.assertEqual(r.status_code, 402, r.text)

    def test_active_subscriber_gets_the_full_test(self):
        self.add_user("paid", is_premium=True, premium_expires_at=_iso(30))
        r = self.client.get(self.EXAM, headers=self.auth("paid", is_premium=True, premium_until=_iso(30)))
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(len(r.json()), 45)

    def test_lifetime_and_active_trial_and_admin_get_the_full_test(self):
        self.add_user("life", is_premium=True, premium_lifetime=True)
        self.add_user("trial", trial_expires_at=_iso(3))
        self.add_user("adm", is_admin=True)
        for uid in ("life", "trial", "adm"):
            r = self.client.get(self.EXAM, headers=self.auth(uid))
            self.assertEqual(r.status_code, 200, f"{uid}: {r.status_code} {r.text[:120]}")

    def test_exam_with_category_is_gated_too(self):
        r = self.client.get("/api/questions/random?mode=exam&category=Skilt", headers={"X-Device-ID": "dev-2"})
        self.assertEqual(r.status_code, 402, r.text)

    def test_practice_without_exam_mode_stays_open_for_guests(self):
        r = self.client.get("/api/questions/random?count=5&has_image=true", headers={"X-Device-ID": "dev-3"})
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(len(r.json()), 5)

    def test_blocked_exam_returns_no_questions(self):
        r = self.client.get(self.EXAM, headers={"X-Device-ID": "dev-4"})
        self.assertNotIn("question", json.dumps(r.json()).lower().replace("premium_required", ""))


class WebQuizIsWiredToTheGate(unittest.TestCase):
    """webapp.py: the client gate, the paywall on 402, and the language parameter."""

    @classmethod
    def setUpClass(cls):
        cls.html = (BACKEND / "webapp.py").read_text(encoding="utf-8")

    def test_start_exam_shows_paywall_before_loading(self):
        m = re.search(r"async function startExam\(\) \{(.*?)\n\}", self.html, re.S)
        self.assertIsNotNone(m)
        body = m.group(1)
        self.assertLess(body.index("isPremium()"), body.index("loadQuiz("))
        self.assertIn("showPaywall()", body)

    def test_the_exam_url_is_only_used_by_start_exam(self):
        self.assertEqual(self.html.count("mode=exam"), 1)

    def test_load_quiz_sends_the_active_language(self):
        m = re.search(r"async function loadQuiz\(url\) \{(.*?)showScreen", self.html, re.S)
        self.assertIsNotNone(m)
        self.assertIn("'/api/questions/random'", m.group(1))
        self.assertIn("'lang=' + encodeURIComponent(appLang)", m.group(1))

    def test_402_from_the_server_reaches_the_paywall(self):
        self.assertRegex(self.html, r"402")
        self.assertIn("showPaywall", self.html)


class QuestionsRouteLanguageFilter(QuizRouteBase):
    def setUp(self):
        super().setUp()
        self.seed_questions(60, 30)
        self.add_user("paid", is_premium=True, premium_lifetime=True)  # guests are capped at 5 questions
        self.free = self.auth("paid", is_premium=True, premium_until=_iso(365))

    def ids(self, url, headers=None):
        r = self.client.get(url, headers=headers or self.free)
        self.assertEqual(r.status_code, 200, r.text)
        return [q["id"] for q in r.json()]

    def test_lang_th_never_returns_a_question_with_norwegian_outside_parentheses(self):
        for _ in range(8):
            ids = self.ids("/api/questions/random?count=10&lang=th")
            self.assertTrue(ids)
            self.assertFalse([i for i in ids if i.startswith("d")], ids)

    def test_lang_th_still_fills_the_requested_count(self):
        self.assertEqual(len(self.ids("/api/questions/random?count=10&lang=th")), 10)

    def test_without_lang_nothing_is_filtered(self):
        seen = set()
        for _ in range(20):
            seen |= {i[0] for i in self.ids("/api/questions/random?count=30")}
        self.assertEqual(seen, {"c", "d"})

    def test_lang_no_and_en_keep_thai_free_questions(self):
        self.assertEqual(len(self.ids("/api/questions/random?count=10&lang=no")), 10)
        self.assertEqual(len(self.ids("/api/questions/random?count=10&lang=en")), 10)

    def test_unknown_lang_is_rejected(self):
        r = self.client.get("/api/questions/random?count=5&lang=xx", headers=self.free)
        self.assertEqual(r.status_code, 422)

    def test_exam_for_a_subscriber_is_also_language_clean(self):
        r = self.client.get("/api/questions/random?count=20&has_image=true&mode=exam&lang=th", headers=self.free)
        self.assertEqual(r.status_code, 200, r.text)
        ids = [q["id"] for q in r.json()]
        self.assertTrue(ids)
        self.assertFalse([i for i in ids if i.startswith("d")], ids)

    def test_served_thai_text_has_norwegian_only_inside_parentheses(self):
        r = self.client.get("/api/questions/random?count=10&lang=th", headers=self.free)
        for q in r.json():
            self.assertEqual(ql.question_violations(q, "th"), [], q["id"])


# ══════════════════════════════════════════════════════════════════════════════
#  Traffic-sign tool: every image loads, none is missing
# ══════════════════════════════════════════════════════════════════════════════
def _sign_files():
    return sorted(p for p in SIGN_DIR.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png"))


def _catalog():
    return json.loads((BACKEND / "signs_content.json").read_text(encoding="utf-8"))


# Signs in signs_content.json that have NO image file at all (neither <id>.jpg nor <id>_*.jpg).
# The list may only shrink: add the missing images and delete the id here.
KNOWN_SIGNS_WITHOUT_IMAGE = {"902_0", "904_0", "906_0", "808_42"}


@unittest.skipIf(server is None, f"server.py not importable here: {_IMPORT_ERROR!r}")
class SignImagesServe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(server.app)

    def test_there_are_sign_images(self):
        self.assertGreater(len(_sign_files()), 300)

    def test_every_image_file_returns_200_with_a_real_image(self):
        failures = []
        for p in _sign_files():
            r = self.client.get("/api/sign-images/" + quote(p.name))
            head = r.content[:4]
            magic_ok = head[:3] == b"\xff\xd8\xff" or head == b"\x89PNG"
            if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image/") \
                    or len(r.content) < 200 or not magic_ok:
                failures.append((p.name, r.status_code, len(r.content)))
        self.assertEqual(failures, [], f"{len(failures)} sign images do not load")

    def test_no_image_file_is_empty_or_corrupt(self):
        bad = []
        for p in _sign_files():
            data = p.read_bytes()
            if len(data) < 200:
                bad.append((p.name, "too small"))
            elif p.suffix.lower() in (".jpg", ".jpeg") and not (data[:3] == b"\xff\xd8\xff" and data.rstrip(b"\x00")[-2:] == b"\xff\xd9"):
                bad.append((p.name, "not a complete JPEG"))
        self.assertEqual(bad, [])

    def test_every_catalog_sign_resolves_to_an_image_over_http(self):
        missing = []
        for sign in _catalog():
            r = self.client.get(f"/api/sign-images/{quote(sign['id'])}.jpg")
            if r.status_code != 200:
                missing.append(sign["id"])
        self.assertEqual(set(missing), KNOWN_SIGNS_WITHOUT_IMAGE,
                         "a catalog sign lost its image, or a missing one was fixed (update KNOWN_SIGNS_WITHOUT_IMAGE)")

    def test_signs_stored_under_descriptive_names_resolve_by_id(self):
        """100_1 lives in 100_1_Skarp_sving_til_hoyre.jpg: <id>.jpg must still work."""
        for sign_id in ("100_1", "151", "521.1", "565", "807-10", "369"):
            r = self.client.get(f"/api/sign-images/{sign_id}.jpg")
            self.assertEqual(r.status_code, 200, sign_id)
            self.assertEqual(r.content[:3], b"\xff\xd8\xff", sign_id)

    def test_exact_files_still_win_over_the_prefix_fallback(self):
        r = self.client.get("/api/sign-images/202_0.jpg")
        self.assertEqual(r.content, (SIGN_DIR / "202_0.jpg").read_bytes())

    def test_normalized_sign_gets_an_image_url_that_loads(self):
        for sign_id in ("202_0", "100_1", "565"):
            sign = server._normalize_sign_for_api({"id": sign_id, "group": 1, "name": {"no": "x"}})
            self.assertEqual(sign["image_url"], f"/api/sign-images/{sign_id}.jpg")
            self.assertEqual(self.client.get(sign["image_url"]).status_code, 200)

    def test_a_sign_without_any_image_gets_no_url(self):
        sign = server._normalize_sign_for_api({"id": "902_0", "group": 1, "name": {"no": "x"}})
        self.assertEqual(sign["image_url"], "")

    def test_unknown_images_are_404(self):
        for name in ("nope.jpg", "999999.jpg", "_.jpg", ".jpg", ".gitkeep"):
            self.assertEqual(self.client.get("/api/sign-images/" + name).status_code, 404, name)

    def test_path_traversal_is_refused(self):
        for name in ("..%2Fserver.py", "%2e%2e%2fserver.py", "..%5Cserver.py", "....//server.py",
                     "%2e%2e/%2e%2e/.env", "sub/../../server.py", "/etc/passwd", "*.jpg", "20*.jpg"):
            r = self.client.get("/api/sign-images/" + name)
            self.assertEqual(r.status_code, 404, f"{name}: {r.status_code}")
            self.assertNotIn(b"import ", r.content[:200])

    def test_resolver_never_leaves_the_directory(self):
        for name in ("../server.py", "..", "a/../../server.py", "", "x/y.jpg"):
            self.assertIsNone(server.resolve_sign_image(name), name)
        found = server.resolve_sign_image("100_1.jpg")
        self.assertEqual(found.parent.resolve(), SIGN_DIR.resolve())


@unittest.skipIf(server is None, f"server.py not importable here: {_IMPORT_ERROR!r}")
class SignCatalogRoutes(QuizRouteBase):
    def test_signs_routes_answer_and_group_data_is_complete(self):
        r = self.client.get("/api/signs")
        self.assertEqual(r.status_code, 200, r.text)
        r = self.client.get("/api/traffic-signs")
        self.assertEqual(r.status_code, 200, r.text)
        groups = r.json()
        self.assertTrue(groups)
        self.assertTrue(all({"group", "group_name", "signs"} <= set(g) for g in groups))

    def test_unknown_group_is_404(self):
        self.assertEqual(self.client.get("/api/traffic-signs/9999").status_code, 404)

    def test_catalog_json_is_complete_and_isolated(self):
        cat = _catalog()
        self.assertGreater(len(cat), 300)
        ids = [s["id"] for s in cat]
        self.assertEqual(len(ids), len(set(ids)), "duplicate sign ids")
        thai = re.compile(r"[฀-๿]")
        for s in cat:
            for field in ("name", "explanation"):
                th = (s.get(field) or {}).get("th", "")
                self.assertTrue(th and thai.search(th), f"{s['id']} {field}.th has no Thai")
                for lang in ("no", "en"):
                    self.assertFalse(thai.search((s.get(field) or {}).get(lang, "")), f"{s['id']} {field}.{lang} has Thai")


class LiveTestsAreOptIn(unittest.TestCase):
    """tests/test_thai2drive_api.py calls production; it must be skipped unless T2D_LIVE_TESTS=1."""

    def test_live_module_is_skipped_by_default_and_never_touches_the_network(self):
        import subprocess, sys
        env = {k: v for k, v in os.environ.items() if k != "T2D_LIVE_TESTS"}
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_thai2drive_api.py", "-q", "-p", "no:cacheprovider"],
                           cwd=BACKEND, env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout[-400:])
        self.assertRegex(r.stdout, r"\d+ skipped")
        self.assertNotRegex(r.stdout, r"\d+ (passed|failed)")

    def test_no_default_test_file_hardcodes_the_production_host_without_a_guard(self):
        src = (BACKEND / "tests" / "test_thai2drive_api.py").read_text(encoding="utf-8")
        self.assertIn('T2D_LIVE_TESTS', src)
        self.assertLess(src.index("T2D_LIVE_TESTS"), src.index("thai2drive.no"))


if __name__ == "__main__":
    unittest.main()
