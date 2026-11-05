"""Offline unit tests for the Etappe 1 gap fixes.

1. Michaels 3 forklaringsnivåer (backend/teacher_chat.py)
   - Nivå 1: Enkel thai (100% ren thai, 7-årsregelen, ingen fagord/latinske bokstaver).
   - Nivå 2: Thai med norske fagord i parentes (f.eks. เว้นระยะห่าง (følgeavstand)).
   - Nivå 3: Ren norsk bokmål (eksamensrettet).
   - _reply_matches_language_script med allow_parenthetical_latin for nivå 2.

2. Sikkerhetskontroll Klasse B bildestøtte (backend/webapp.py)
   - 5 moduler med WebP-bilder definert for no/th/en.
   - Bildestier finnes i backend/public_assets/safety_check/.

3. Klikkbare norske fagord i quizen (backend/webapp.py)
   - Modal #qTermModal og container #qTermsWrap finnes i kildekoden.
   - Utheving og modal-oppslag.
"""
import os
import re
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.tests.test_teacher_chat_fallback import _load_teacher_chat


class Etappe1GapsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tc = _load_teacher_chat()
        with open(_REPO_ROOT / "backend" / "webapp.py", "r", encoding="utf-8") as f:
            cls.webapp_content = f.read()

    # ── 1. Michaels 3 forklaringsnivåer ─────────────────────────────────────

    def test_explain_level_1_prompt_rules(self):
        # Nivå 1 skal kreve 100% enkel thai uten latinske bokstaver/norske ord
        with open(_REPO_ROOT / "backend" / "teacher_chat.py", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("EXPLANATION LEVEL 1 (ENKEL THAI / 100% REN THAI)", code)
        self.assertIn("LEVEL 1 OVERRIDE: 100% REN THAI", code)

    def test_explain_level_2_prompt_rules(self):
        # Nivå 2 skal kreve thai med norske fagord i parentes
        with open(_REPO_ROOT / "backend" / "teacher_chat.py", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("EXPLANATION LEVEL 2 (THAI MED NORSKE FAGORD I PARENTES)", code)
        self.assertIn("thai-forklaring (norsk fagord)", code)

    def test_explain_level_3_prompt_rules(self):
        # Nivå 3 skal overstyre til ren norsk bokmål
        with open(_REPO_ROOT / "backend" / "teacher_chat.py", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("EXPLANATION LEVEL 3 (REN NORSK BOKMÅL - EKSAMENSRETTET)", code)
        self.assertIn("LEVEL 3 OVERRIDE: REN NORSK BOKMÅL", code)

    def test_reply_matches_language_script_level2_parenthetical(self):
        # Nivå 2 tillater norske fagord i parentes i thai-svar
        thai_text_with_paren = "คุณต้องเว้นระยะห่าง (følgeavstand) อย่างน้อย 3 วินาที เพื่อความปลอดภัย"
        # Uten flagg skal det feile fordi det inneholder latinske bokstaver
        self.assertFalse(self.tc._reply_matches_language_script(thai_text_with_paren, "th", allow_parenthetical_latin=False))
        # Med allow_parenthetical_latin=True skal det godkjennes
        self.assertTrue(self.tc._reply_matches_language_script(thai_text_with_paren, "th", allow_parenthetical_latin=True))

    def test_reply_matches_language_script_level1_pure_thai(self):
        pure_thai = "คุณต้องอยู่ห่างจากรถคันหน้าอย่างน้อย 3 วินาทีเพื่อให้ปลอดภัย"
        self.assertTrue(self.tc._reply_matches_language_script(pure_thai, "th"))

    def test_reply_matches_language_script_level3_norwegian(self):
        bokmal = "Du må holde minst tre sekunders avstand til bilen foran for å unngå påkjøring bakfra."
        self.assertTrue(self.tc._reply_matches_language_script(bokmal, "no"))

    # ── 2. Sikkerhetskontroll bildekobling ───────────────────────────────────

    def test_safety_check_assets_exist_on_disk(self):
        assets_dir = _REPO_ROOT / "backend" / "public_assets" / "safety_check"
        expected_files = [
            "safety_lights.webp",
            "safety_brakes.webp",
            "safety_tyres.webp",
            "safety_warning_lights.webp",
            "safety_emergency_gear.webp",
        ]
        for fname in expected_files:
            p = assets_dir / fname
            self.assertTrue(p.exists(), f"Missing safety asset {fname} at {p}")
            self.assertGreater(p.stat().st_size, 1000, f"Asset {fname} is too small / corrupt")

    def test_safety_check_rendered_with_images_in_webapp(self):
        # Sjekk at _MS_SAFETY refererer til bildene
        self.assertIn("/api/assets/safety_check/safety_lights.webp", self.webapp_content)
        self.assertIn("/api/assets/safety_check/safety_brakes.webp", self.webapp_content)
        self.assertIn("/api/assets/safety_check/safety_tyres.webp", self.webapp_content)
        self.assertIn("/api/assets/safety_check/safety_warning_lights.webp", self.webapp_content)
        self.assertIn("/api/assets/safety_check/safety_emergency_gear.webp", self.webapp_content)
        # Sjekk at HTML genererer .ms-safety-visual og .ms-safety-img
        self.assertIn('class="ms-safety-visual"', self.webapp_content)
        self.assertIn('class="ms-safety-img"', self.webapp_content)

    # ── 3. Klikkbare norske fagord i quiz ───────────────────────────────────

    def test_quiz_terms_modal_and_markup_present(self):
        # Modal #qTermModal skal finnes
        self.assertIn('id="qTermModal"', self.webapp_content)
        self.assertIn('id="qTermModalTitle"', self.webapp_content)
        self.assertIn('id="qTermModalTh"', self.webapp_content)
        self.assertIn('id="qTermModalDef"', self.webapp_content)
        self.assertIn('id="qTermsWrap"', self.webapp_content)
        self.assertIn("button.className = 'q-term-inline'", self.webapp_content)
        self.assertIn("button.className = 'q-term-chip'", self.webapp_content)
        self.assertIn("button.addEventListener('click'", self.webapp_content)
        self.assertNotIn('onclick="openTermDetailModal(', self.webapp_content)
        self.assertNotIn('qEl.innerHTML = html', self.webapp_content)

    def test_quiz_terms_javascript_handlers_present(self):
        self.assertIn("function openTermDetailModal(", self.webapp_content)
        self.assertIn("function closeTermDetailModal(", self.webapp_content)
        self.assertIn("function speakCurrentTermModal(", self.webapp_content)
        self.assertIn("function askMichaelAboutCurrentTerm(", self.webapp_content)
        self.assertIn("function _findWordInDictionary(", self.webapp_content)


if __name__ == "__main__":
    unittest.main()
