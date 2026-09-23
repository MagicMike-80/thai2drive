"""Contract for Michael-skolen UI: modal, king/servant chip, HAV lamps, hint ladder button.

Offline: reads WEBAPP_HTML only (never touches production or the DB).
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import backend.webapp as webapp

HTML = webapp.WEBAPP_HTML


class MichaelSchoolUiContract(unittest.TestCase):
    def test_modal_and_entry_button_exist(self):
        for marker in ("msOpenBtn", "msOverlay", "msTabs", "msBody", "openMichaelSchool()", "closeMichaelSchool()"):
            self.assertIn(marker, HTML)

    def test_all_three_languages_have_content(self):
        for block in ("var _MS = {", "var _MS_CULTURE = {", "var _MS_WORDS = {", "var _MS_GAZE = {"):
            self.assertIn(block, HTML)
        for lang_key in ("  th: {", "  no: {", "  en: {"):
            self.assertIn(lang_key, HTML)

    def test_gaze_routine_has_blind_spot_step(self):
        for term in ("Blindsone", "Blind spot", "จุดบอด"):
            self.assertIn(term, HTML)

    def test_king_servant_chip_and_hav_lamps_wired_into_quiz(self):
        self.assertIn("+ buildKingServantChip(qText)", HTML)
        self.assertIn("html += buildHavLamps(expl);", HTML)
        self.assertIn("html += buildHintButton();", HTML)

    def test_hint_mode_keeps_session_and_marks_hint_request(self):
        self.assertIn("function askMichaelAboutThis(mode)", HTML)
        self.assertIn("reuseHintSession", HTML)
        self.assertIn("THE STUDENT ASKED FOR A HINT.", HTML)

    def test_language_change_resyncs_label_and_clears_hint_state(self):
        self.assertIn("_msOnLangChange();", HTML)
        self.assertIn("function _msResetHint()", HTML)
        self.assertIn("if (!isHint) _msResetHint();", HTML)

    def test_word_of_the_day_has_40_words_from_the_source_document(self):
        for term in ("Reaksjonslengde", "Fjernlys", "Bilbelte", "Rundkjøring", "Mobiltelefon"):
            self.assertGreaterEqual(HTML.count("'" + term + "'"), 3, term)

    def test_unverified_claims_removed(self):
        self.assertNotIn("anbefalt 4 mm", HTML)
        self.assertNotIn("opptil 10 ganger lengre på ren is", HTML)


if __name__ == "__main__":
    unittest.main()
