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
        self.assertIn(".tm-media-strip { grid-template-columns:1fr; }", WEBAPP)

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
        self.assertIn("['sign','intersection_image','video'].indexOf(media.type)", WEBAPP)
        self.assertIn("mediaSignIds.indexOf(signId) === -1", WEBAPP)

    def test_sign_media_is_compact_and_opens_authoritative_sign_detail(self):
        self.assertIn(".tm-media-card.sign .tm-media-visual", WEBAPP)
        self.assertIn("width:90px; height:90px; min-height:48px", WEBAPP)
        self.assertIn("max-width:90px", WEBAPP)
        self.assertIn("max-height:90px", WEBAPP)
        card = WEBAPP[WEBAPP.index("function _buildTeacherMediaCard(media)"):WEBAPP.index("function _teacherAppendMediaCards")]
        self.assertIn("media.type === 'sign' ? 'button' : 'article'", card)
        self.assertIn("_openTeacherSignDetailById(media.sign_id)", card)
        self.assertIn("card.setAttribute('aria-label', media.title)", card)


if __name__ == "__main__":
    unittest.main()
