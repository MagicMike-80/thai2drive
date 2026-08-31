import re
import unittest
from pathlib import Path


WEBAPP = (Path(__file__).resolve().parents[1] / "backend" / "webapp.py").read_text(encoding="utf-8")


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

    def test_media_is_bounded_validated_and_does_not_duplicate_sign_card(self):
        self.assertIn("mediaItems.slice(0, 2)", WEBAPP)
        self.assertIn("_teacherMediaSafeUrl(media.url)", WEBAPP)
        self.assertIn("['sign','intersection_image','video','podcast'].indexOf(media.type)", WEBAPP)
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
        self.assertIn("if (media.type === 'podcast')", card)
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
        scroll = send.index("_teacherScrollToAnswerStart(assistantBubble)")
        suggestions = send.index("_teacherAppendChips(data.suggestions || [])", scroll)
        self.assertLess(cards, scroll)
        self.assertLess(scroll, suggestions)
        self.assertIn("_teacherScrollToAnswerStart(bubble)", send)
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


if __name__ == "__main__":
    unittest.main()
