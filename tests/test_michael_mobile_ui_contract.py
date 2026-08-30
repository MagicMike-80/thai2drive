import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEBAPP = (ROOT / "backend" / "webapp.py").read_text(encoding="utf-8")


class MichaelMobileUiContractTests(unittest.TestCase):
    def test_real_michael_portrait_is_packaged_and_used(self):
        portrait = ROOT / "backend" / "public_assets" / "michael_profile.jpg"
        self.assertTrue(portrait.is_file())
        self.assertGreater(portrait.stat().st_size, 10_000)
        self.assertGreaterEqual(WEBAPP.count("/api/assets/michael_profile.jpg"), 6)

    def test_mobile_topics_are_collapsible_and_touch_friendly(self):
        self.assertIn('id="teacherMoreBtn"', WEBAPP)
        self.assertIn("function toggleTeacherTopics()", WEBAPP)
        self.assertIn("min-height:50px", WEBAPP)
        self.assertIn("teacher-suggestions:not(.expanded)", WEBAPP)
        self.assertIn("#app.teacher-mode .flag-bg { display:none; }", WEBAPP)

    def test_new_learner_text_has_all_three_languages(self):
        for key in (
            "teacher_role",
            "teacher_experience",
            "teacher_meta",
            "teacher_online_badge",
            "teacher_send",
            "teacher_placeholder",
            "practice_similar",
            "teacher_more_topics",
            "teacher_fewer_topics",
        ):
            match = re.search(rf"{key}:\s*\{{([^}}]+)\}}", WEBAPP)
            self.assertIsNotNone(match, key)
            value = match.group(1)
            self.assertIn("th:", value)
            self.assertIn("no:", value)
            self.assertIn("en:", value)

    def test_teacher_chat_contract_remains_in_place(self):
        self.assertIn("/api/teacher/chat", WEBAPP)
        self.assertIn("function _teacherAppendBubble(role, text)", WEBAPP)
        self.assertIn("function _teacherShowTyping()", WEBAPP)

    def test_second_teacher_audio_replaces_previous_audio(self):
        self.assertIn("var _teacherActiveText = '';", WEBAPP)
        self.assertIn("var _teacherAudioToken = 0;", WEBAPP)
        self.assertIn("_teacherTtsPlaying && _teacherActiveText === clean", WEBAPP)
        self.assertIn("var playToken = ++_teacherAudioToken;", WEBAPP)
        self.assertIn("playToken === _teacherAudioToken", WEBAPP)

    def test_contextual_mobile_topics_show_three_before_expansion(self):
        self.assertIn("index >= 3 ? ' mobile-extra' : ''", WEBAPP)
        self.assertIn("chips.length > 3", WEBAPP)
        self.assertIn(".tm-chips .tm-chip-btn.mobile-extra { display:none; }", WEBAPP)
        self.assertIn(".tm-chips.expanded .tm-chip-btn.mobile-extra", WEBAPP)
        self.assertIn("toggle.setAttribute('aria-expanded'", WEBAPP)

    def test_mobile_teacher_header_is_compact(self):
        self.assertIn("height:90px; max-height:90px; min-height:90px", WEBAPP)
        self.assertIn(".teacher-avatar { width:64px; height:64px", WEBAPP)
        self.assertIn("teacher-meta-line", WEBAPP)
        self.assertIn("teacher-meta-wrap", WEBAPP)
        self.assertIn("teacher-online-badge", WEBAPP)
        header = WEBAPP[WEBAPP.index('<!-- Chat header -->'):WEBAPP.index('<!-- Message list -->')]
        self.assertLess(header.index('class="teacher-avatar"'), header.index('class="teacher-header-info"'))

    def test_teacher_actions_and_input_have_clear_hierarchy(self):
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", WEBAPP)
        self.assertIn(".tm-chips .tm-chip-btn:first-of-type", WEBAPP)
        self.assertIn("min-height:56px", WEBAPP)
        self.assertIn('data-key="teacher_send"', WEBAPP)

    def test_sign_cards_use_structured_sign_ids_and_selected_language(self):
        self.assertIn("function _buildTeacherSignCard(sign)", WEBAPP)
        self.assertIn("function _teacherAppendSignCards(signIds, bubble)", WEBAPP)
        self.assertIn("_teacherSignValue(sign, 'explanation')", WEBAPP)
        self.assertIn("_teacherSignValue(sign, 'driver_action') || _teacherSignValue(sign, 'explanation')", WEBAPP)
        self.assertIn("data.sign_ids || []", WEBAPP)
        self.assertIn("answerRow.offsetTop", WEBAPP)
        card = WEBAPP[WEBAPP.index("function _buildTeacherSignCard(sign)"):WEBAPP.index("async function _teacherAppendSignCards")]
        self.assertNotIn("name_no", card)
        self.assertNotIn("tm-sign-actions", card)
        self.assertNotIn("sign_card_tip", card)

    def test_sign_response_has_only_similar_practice_action(self):
        actions = WEBAPP[WEBAPP.index("function _teacherAppendSignActions(sign)"):WEBAPP.index("function _teacherShowTyping()")]
        self.assertIn("t('practice_similar')", actions)
        self.assertNotIn("t('practice_this_sign')", actions)
        self.assertNotIn("t('ask_ai')", actions)
        self.assertNotIn("t('read_more')", actions)
        self.assertNotIn("t('see_similar')", actions)
        self.assertNotIn("t('ask_more')", actions)
        self.assertIn(".tm-sign-actions-row { grid-template-columns:1fr; }", WEBAPP)
        self.assertIn("no:'Spør Michael...'", WEBAPP)

    def test_teacher_mode_bottom_nav_is_reduced_to_three_items(self):
        self.assertIn("#app.teacher-mode #bottomNav .bn-tab { display:none; }", WEBAPP)
        self.assertIn("#app.teacher-mode #bottomNav #bnCats", WEBAPP)
        self.assertIn("#app.teacher-mode #bottomNav #bnHistory", WEBAPP)
        self.assertIn("#app.teacher-mode #bottomNav #bnTeacher", WEBAPP)


if __name__ == "__main__":
    unittest.main()
