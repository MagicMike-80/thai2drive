import re
import unittest
from pathlib import Path


WEBAPP = (Path(__file__).resolve().parents[1] / "backend" / "webapp.py").read_text(encoding="utf-8")
SERVER = (Path(__file__).resolve().parents[1] / "backend" / "server.py").read_text(encoding="utf-8")


class MichaelMediaCardsContractTests(unittest.TestCase):
    def test_media_cards_render_in_chat_and_quiz_coach(self):
        self.assertIn("function _teacherAppendMediaCards(mediaItems, container)", WEBAPP)
        self.assertIn("_teacherAppendMediaCards(data.media || [], assistantBubble)", WEBAPP)
        self.assertIn("_teacherAppendMediaCards((data && data.media) || [], container)", WEBAPP)
        self.assertIn("function _renderQuizCoachResponse(container, data)", WEBAPP)
        self.assertIn("return data;", WEBAPP)

    def test_image_cards_use_safe_dom_and_mobile_layout(self):
        start = WEBAPP.index("function _buildTeacherMediaCard(media)")
        end = WEBAPP.index("function _teacherAppendMediaCards", start)
        card = WEBAPP[start:end]
        self.assertIn("image.src = media.url", card)
        self.assertIn("title.textContent = media.title", card)
        self.assertIn("caption.textContent = media.caption", card)
        self.assertNotIn("innerHTML", card)
        self.assertIn(".tm-media-card.intersection_image .tm-media-image { object-fit:cover; }", WEBAPP)
        media_css = WEBAPP[WEBAPP.index(".tm-media-strip {"):WEBAPP.index(".tm-media-card {")]
        self.assertIn("grid-template-columns:1fr", media_css)
        self.assertNotIn("repeat(2", media_css)
        self.assertIn("max-width:100%", media_css)

    def test_video_card_has_three_language_label_and_opens_player(self):
        match = re.search(r"teacher_video_explanation:\s*\{([^}]+)\}", WEBAPP)
        self.assertIsNotNone(match)
        values = match.group(1)
        self.assertIn("th:'ดูวิดีโอคำอธิบาย'", values)
        self.assertIn("no:'Se videoforklaring'", values)
        self.assertIn("en:'Watch video explanation'", values)
        self.assertIn("button.onclick = function() { _openTeacherMediaVideo(media); };", WEBAPP)
        self.assertIn('id="vpYoutube"', WEBAPP)
        self.assertIn("youtubeFrame.src = 'https://www.youtube.com/embed/'", WEBAPP)
        self.assertIn(".vp-player-wrap iframe[hidden] { display:none; }", WEBAPP)
        self.assertIn("track.kind = 'subtitles'", WEBAPP)
        self.assertIn("track.default = item.lang === appLang", WEBAPP)
        self.assertIn("vid.muted = !!(v.audio_language && v.audio_language !== appLang)", WEBAPP)
        self.assertIn("subtitle_tracks:Array.isArray(media.subtitle_tracks)", WEBAPP)

    def test_public_asset_route_serves_webvtt_with_browser_safe_mime(self):
        self.assertIn('\".vtt\": \"text/vtt\"', SERVER)

    def test_public_asset_route_uses_byte_ranges_for_mp4(self):
        self.assertIn('if ext in {\".mp3\", \".mp4\",', SERVER)
        self.assertIn("return _range_file_response(file_path, request, media_type, asset_headers)", SERVER)

    def test_tts_has_selected_language_browser_fallback(self):
        self.assertIn("function _consumeTtsFallback()", WEBAPP)
        self.assertIn("utterance.lang = localeForLangKey(pending.lang)", WEBAPP)
        self.assertIn("window.speechSynthesis.speak(utterance)", WEBAPP)
        self.assertIn("if (_consumeTtsFallback()) return", WEBAPP)

    def test_media_is_bounded_validated_and_does_not_duplicate_sign_card(self):
        self.assertIn("mediaItems.slice(0, 2)", WEBAPP)
        self.assertIn("_teacherMediaSafeUrl(media.url)", WEBAPP)
        self.assertIn("['sign','intersection_image','image','video','podcast','audio','document'].indexOf(media.type)", WEBAPP)
        self.assertIn("mediaSignIds.indexOf(signId) === -1", WEBAPP)

    def test_sign_media_is_compact_and_opens_authoritative_sign_detail(self):
        self.assertIn(".tm-media-card.sign .tm-media-visual", WEBAPP)
        self.assertIn("width:80px; height:80px; min-height:48px", WEBAPP)
        self.assertIn("max-width:80px", WEBAPP)
        self.assertIn("max-height:80px", WEBAPP)
        card = WEBAPP[WEBAPP.index("function _buildTeacherMediaCard(media)"):WEBAPP.index("function _teacherAppendMediaCards")]
        self.assertIn("media.type === 'sign' ? 'button' : 'article'", card)
        self.assertIn("_openTeacherSignDetailById(media.sign_id)", card)
        self.assertIn("card.setAttribute('aria-label', media.title)", card)
        self.assertIn("if (media.type === 'sign') card.hidden = true", card)

    def test_michael_answer_typography_reads_like_prose(self):
        self.assertIn("font-size:1.06rem; line-height:1.72; letter-spacing:0", WEBAPP)
        self.assertIn("max-width:52ch; margin-bottom:1.05em", WEBAPP)
        self.assertIn("letter-spacing:0; text-transform:none", WEBAPP)
        self.assertIn("font-size:1.08rem; line-height:1.72", WEBAPP)

    def test_podcast_card_uses_safe_dom_and_localized_payload(self):
        card = WEBAPP[WEBAPP.index("function _buildTeacherMediaCard(media)"):WEBAPP.index("function _teacherAppendMediaCards")]
        self.assertIn("if (media.type === 'podcast' || media.type === 'audio')", card)
        self.assertIn("if (media.type === 'document')", card)
        self.assertIn("audio.controls = true", card)
        self.assertIn("audio.preload = 'none'", card)
        self.assertIn("audio.src = media.url", card)
        self.assertIn("podcastTitle.textContent = media.title", card)
        self.assertIn("podcastCaption.textContent = media.caption", card)
        self.assertNotIn("innerHTML", card)

    def test_new_assistant_answer_scrolls_to_start_after_all_media_paths(self):
        helper_start = WEBAPP.index("function _teacherScrollToAnswerStart(bubble)")
        helper_end = WEBAPP.index("function _teacherTextOnlyReply", helper_start)
        helper = WEBAPP[helper_start:helper_end]
        self.assertIn("answerRow.offsetTop - 12", helper)
        self.assertNotIn("scrollIntoView", helper)

        send_start = WEBAPP.index("async function teacherSend(")
        send_end = WEBAPP.index("function toggleSound", send_start)
        send = WEBAPP[send_start:send_end]
        cards = send.index("await _teacherAppendSignCards(fallbackSignIds, assistantBubble)")
        chips = send.index("_teacherAppendChips(data.suggestions || [])")
        scroll = send.index("_teacherScrollToAnswerStart(assistantBubble)")
        self.assertLess(cards, chips)
        self.assertLess(chips, scroll)
        self.assertIn("_teacherAppendChips(data.suggestions || [])", send)
        self.assertNotIn("_teacherAppendSignActions(signForActions)", send)
        self.assertNotIn("fetchVideoForTopic('Bremsing')", send)
        self.assertIn("_teacherScrollToAnswerStart(assistantBubble)", send)
        self.assertNotIn("action.classList.add('show')", WEBAPP)
        self.assertIn("_teacherScrollToAnswerStart(errorBubble)", send)
        self.assertNotIn("bubble.appendChild(wrap);\n        msgs.scrollTop = msgs.scrollHeight", send)

        append_start = WEBAPP.index("function _teacherAppendBubble(role, text)")
        append_end = WEBAPP.index("function _teacherScrollToAnswerStart", append_start)
        append = WEBAPP[append_start:append_end]
        self.assertIn("if (role === 'user')", append)
        self.assertNotIn("if (_teacherHasUserMsg) {\n    msgs.scrollTop = msgs.scrollHeight", append)

        chips_start = WEBAPP.index("function _teacherAppendChips(chips)")
        chips_end = WEBAPP.index("async function teacherSend(", chips_start)
        chips = WEBAPP[chips_start:chips_end]
        self.assertIn("msgs.appendChild(row)", chips)
        self.assertNotIn("msgs.scrollTop = msgs.scrollHeight", chips)


    def test_teacher_chat_ui_contract_sends_conversation_id_and_quiz_coach_mode(self):
        self.assertIn("mode:'quiz_coach'", WEBAPP)
        self.assertIn("conversation_id:_quizCoachConversationId || _quizCoachSessionId", WEBAPP)
        self.assertIn("conversation_id: activeConversationId || activeSessionId", WEBAPP)

    def test_exam_mode_ui_contract_hides_instant_feedback_and_allows_navigation(self):
        # 1. Verification of selectAns in exam mode
        select_ans_start = WEBAPP.index("async function selectAns(")
        select_ans_end = WEBAPP.index("var correct = currentCorrect;", select_ans_start)
        select_ans_body = WEBAPP[select_ans_start:select_ans_end]

        self.assertIn("if (isExamMode) {", select_ans_body)
        self.assertIn("examAnswers[qIdx] = picked.toUpperCase();", select_ans_body)
        self.assertIn("b.classList.add('selected');", select_ans_body)
        # Ensure that immediate feedback, correct/wrong classes and sounds are after the exam mode return
        exam_block = select_ans_body[select_ans_body.index("if (isExamMode) {"):]
        self.assertIn("return;", exam_block)
        self.assertNotIn("b.classList.add('correct')", exam_block)
        self.assertNotIn("b.classList.add('wrong')", exam_block)
        self.assertNotIn("playSound", exam_block)

        # 2. Score badge is hidden during exam
        self.assertIn("scoreBadge.style.display = isExamMode ? 'none' : 'flex'", WEBAPP)

        # 3. Navigation controls and options preserved across questions
        self.assertIn("function prevQ()", WEBAPP)
        self.assertIn("q._shuffledOpts", WEBAPP)
        self.assertIn("exam-nav-row", WEBAPP)
        self.assertIn("q-prev-mobile", WEBAPP)

    def test_exam_end_screen_debrief_and_michael_quiz_coach_links(self):
        # 1. Debrief generation on end screen
        self.assertIn("function showEnd()", WEBAPP)
        self.assertIn("endExamErrorsContainer", WEBAPP)
        self.assertIn("exam-error-card", WEBAPP)
        self.assertIn("consultMichaelFromExamQuestion", WEBAPP)
        self.assertIn("consultMichaelFromExam()", WEBAPP)

        # 2. Both exam debrief entrypoints trigger Michael with mode 'quiz_coach'
        self.assertIn("teacherSend(prompt, display, 'quiz_coach')", WEBAPP)
        self.assertIn("<quiz_context>", WEBAPP)
        self.assertIn("Student answer:", WEBAPP)
        self.assertIn("Correct answer:", WEBAPP)

        # 3. teacherSend attaches customMode to chatPayload.mode
        send_start = WEBAPP.index("async function teacherSend(")
        send_end = WEBAPP.index("function toggleSound", send_start)
        send_body = WEBAPP[send_start:send_end]
        self.assertIn("chatPayload.mode = customMode;", send_body)

    def test_exam_ui_translations_100_percent_isolated(self):
        self.assertIn("var TR = UI;", WEBAPP)
        for key in [
            'prev', 'exam_finish', 'exam_errors_heading', 'exam_all_correct',
            'exam_your_answer', 'exam_correct_answer', 'exam_unanswered', 'ask_michael_ai'
        ]:
            pattern = rf"{key}\s*:\s*\{{([^\r\n]+)\}}"
            match = re.search(pattern, WEBAPP)
            self.assertIsNotNone(match, f"Translation key '{key}' missing from UI/TR")
            val_str = match.group(1)
            self.assertIn("th:", val_str, f"Thai translation missing for '{key}'")
            self.assertIn("no:", val_str, f"Norwegian translation missing for '{key}'")
            self.assertIn("en:", val_str, f"English translation missing for '{key}'")


if __name__ == "__main__":
    unittest.main()

