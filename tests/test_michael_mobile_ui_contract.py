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

    def test_topics_are_in_a_toggleable_sidebar(self):
        self.assertIn('id="teacherSidebarToggle"', WEBAPP)
        self.assertIn('id="teacherSidebarBackdrop"', WEBAPP)
        self.assertIn("function toggleTeacherSidebar()", WEBAPP)
        self.assertIn("function closeTeacherSidebar()", WEBAPP)
        self.assertIn(".teacher-suggestions {", WEBAPP)
        self.assertIn("display:none !important", WEBAPP)
        self.assertIn(".teacher-side-panel .tsp-btn { color:#F8FAFC !important; }", WEBAPP)
        self.assertEqual(WEBAPP.count('data-tsp-btn="'), 6)
        self.assertIn("closeTeacherSidebar(); teacherSend(msg);", WEBAPP)
        self.assertIn("#app.teacher-mode .flag-bg { display:none; }", WEBAPP)

    def test_new_learner_text_has_all_three_languages(self):
        for key in (
            "teacher_role",
            "teacher_experience",
            "teacher_meta",
            "teacher_online_badge",
            "teacher_send",
            "teacher_placeholder",
            "teacher_topics_open",
            "teacher_topics_close",
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
        self.assertIn("height:72px; max-height:72px; min-height:72px", WEBAPP)
        self.assertIn(".teacher-avatar { width:48px; height:48px", WEBAPP)
        self.assertIn("teacher-meta-line", WEBAPP)
        self.assertIn("teacher-meta-wrap", WEBAPP)
        self.assertIn("teacher-online-badge", WEBAPP)
        header = WEBAPP[WEBAPP.index('<!-- Chat header -->'):WEBAPP.index('<!-- Message list -->')]
        self.assertLess(header.index('class="teacher-avatar"'), header.index('class="teacher-header-info"'))

    def test_teacher_chat_is_a_centered_overflow_safe_reading_column(self):
        self.assertIn("width:min(760px,100%)", WEBAPP)
        self.assertGreaterEqual(WEBAPP.count("margin-inline:auto"), 3)
        self.assertIn("max-width:100%; overflow-x:clip", WEBAPP)
        self.assertIn("top:72px; bottom:0; left:0", WEBAPP)
        self.assertIn("inset:72px 0 0", WEBAPP)
        inputbar = WEBAPP[WEBAPP.index(".teacher-inputbar {"):WEBAPP.index(".teacher-input {")]
        self.assertIn("flex-shrink:0", inputbar)
        self.assertNotIn("position:fixed", inputbar)

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

    def test_sign_cards_and_linked_terms_are_compact_safe_detail_controls(self):
        self.assertIn(".tm-sign-image { display:block; width:90px; max-width:90px; height:90px; max-height:90px", WEBAPP)
        self.assertIn("function _getTeacherSign(signId)", WEBAPP)
        self.assertIn("'/api/signs/' + encodeURIComponent(id)", WEBAPP)
        self.assertIn("function _teacherLinkSignName(container, sign)", WEBAPP)
        self.assertIn("document.createTreeWalker", WEBAPP)
        self.assertIn("button.textContent = text.slice(index, index + needle.length)", WEBAPP)
        self.assertIn("await _teacherLinkSignReferences(assistantBubble, data.sign_ids || [])", WEBAPP)
        linker = WEBAPP[
            WEBAPP.index("function _teacherLinkSignName(container, sign)"):
            WEBAPP.index("async function _teacherLinkSignReferences")
        ]
        self.assertNotIn("innerHTML", linker)
        self.assertIn("!_teacherIsWordChar(text.charAt(index - 1))", linker)
        self.assertIn("openSignDetail(sign)", linker)

    def test_sign_card_requires_active_language_name_and_uses_approved_alias(self):
        append_cards = WEBAPP[
            WEBAPP.index("async function _teacherAppendSignCards(signIds, bubble)"):
            WEBAPP.index("function _teacherAppendSignActions(sign)")
        ]
        self.assertIn("return sign && _teacherSignValue(sign, 'name');", append_cards)
        aliases = WEBAPP[
            WEBAPP.index("var _teacherSignAliases = {"):
            WEBAPP.index("async function _getTeacherSign(signId)")
        ]
        self.assertIn("'vikepliktskiltet'", aliases)
        self.assertEqual(aliases.count("'vikepliktsskiltet'"), 1)

    def test_sign_response_has_two_progressive_actions(self):
        actions = WEBAPP[WEBAPP.index("function _teacherAppendSignActions(sign)"):WEBAPP.index("function _teacherShowTyping()")]
        self.assertIn("t('teacher_show_example')", actions)
        self.assertIn("t('teacher_show_example_prompt')", actions)
        self.assertIn("teacherSend(t('teacher_show_example_prompt'), t('teacher_show_example'))", actions)
        self.assertIn("t('teacher_test_me')", actions)
        self.assertIn("practiceSignFromChat(sign.id)", actions)
        self.assertNotIn("t('practice_similar')", actions)
        self.assertNotIn("t('practice_this_sign')", actions)
        self.assertNotIn("t('ask_ai')", actions)
        self.assertNotIn("t('read_more')", actions)
        self.assertNotIn("t('see_similar')", actions)
        self.assertNotIn("t('ask_more')", actions)
        self.assertIn(".tm-sign-actions-row { grid-template-columns:1fr; }", WEBAPP)
        self.assertIn("no:'Spør Michael...'", WEBAPP)

        for key in ("teacher_show_example", "teacher_show_example_prompt", "teacher_test_me"):
            match = re.search(rf"{key}:\s*\{{([^}}]+)\}}", WEBAPP)
            self.assertIsNotNone(match, key)
            value = match.group(1)
            self.assertIn("th:", value)
            self.assertIn("no:", value)
            self.assertIn("en:", value)

    def test_teacher_mode_bottom_nav_is_reduced_to_three_items(self):
        self.assertIn("#app.teacher-mode #bottomNav .bn-tab { display:none; }", WEBAPP)
        self.assertIn("#app.teacher-mode #bottomNav #bnCats", WEBAPP)
        self.assertIn("#app.teacher-mode #bottomNav #bnHistory", WEBAPP)
        self.assertIn("#app.teacher-mode #bottomNav #bnTeacher", WEBAPP)


if __name__ == "__main__":
    unittest.main()
