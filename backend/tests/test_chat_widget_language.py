"""Offline unit tests for language isolation in the support chat widget JS (website.py)."""
import re
import unittest
import sys
from pathlib import Path

BACKEND_DIR = str(Path(__file__).resolve().parent.parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
class TestChatWidgetLanguageIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        website_path = Path(__file__).resolve().parent.parent / "website.py"
        cls.content = website_path.read_text(encoding="utf-8")

    def _lang_object_body(self, var_name):
        match = re.search(rf"const {var_name}\s*=\s*\{{([^}}]+)\}}", self.content)
        self.assertIsNotNone(match, f"'{var_name}' lang object must be defined")
        return match.group(1)

    def test_no_reply_message_has_all_three_languages(self):
        body = self._lang_object_body("noReplyMsgs")
        for lang in ["th", "no", "en"]:
            self.assertIn(f"{lang}:", body, f"noReplyMsgs missing '{lang}' translation")
        self.assertIn("data.reply || (noReplyMsgs[lang] || '')", self.content)

    def test_escalated_message_has_all_three_languages(self):
        body = self._lang_object_body("escalatedMsgs")
        for lang in ["th", "no", "en"]:
            self.assertIn(f"{lang}:", body, f"escalatedMsgs missing '{lang}' translation")
        self.assertIn("escalatedMsgs[lang] || ''", self.content)

    def test_network_error_message_has_all_three_languages(self):
        body = self._lang_object_body("networkErrMsgs")
        for lang in ["th", "no", "en"]:
            self.assertIn(f"{lang}:", body, f"networkErrMsgs missing '{lang}' translation")
        self.assertIn("networkErrMsgs[lang] || ''", self.content)

    def test_no_bare_hardcoded_fallback_strings_remain(self):
        """The three previously-leaking strings must only appear inside a lang object, never as a bare fallback."""
        self.assertNotRegex(
            self.content,
            r"data\.reply\s*\|\|\s*'Beklager, ingen svar",
            "bare Norwegian fallback for no-reply message must not remain",
        )
        self.assertNotRegex(
            self.content,
            r"addMsg\('system',\s*'✓ Meldingen din er videresendt",
            "bare Norwegian escalation message must not remain",
        )
        self.assertNotRegex(
            self.content,
            r"addMsg\('bot',\s*'Beklager, nettverksfeil",
            "bare Norwegian network-error message must not remain",
        )

    def test_catch_block_recomputes_lang_in_its_own_scope(self):
        """`lang` from the try block is out of scope in catch — the catch block must call getLang() itself."""
        match = re.search(r"\}catch\(err\)\{([\s\S]+?)\}finally\{", self.content)
        self.assertIsNotNone(match, "sendMessage's catch block must be present")
        catch_body = match.group(1)
        self.assertIn("const lang = getLang();", catch_body)

    def test_landing_widget_labels_and_quick_questions_are_localized(self):
        from backend.website import _localized_chat_widget_html

        thai = _localized_chat_widget_html("th")
        english = _localized_chat_widget_html("en")
        for html, expected in [
            (thai, ["ยกเลิกการสมัครสมาชิก", "ลืมรหัสผ่าน", "aria-label=\"เปิดแชตช่วยเหลือ\"", "placeholder=\"ถามเกี่ยวกับ Thai2Drive...\""]),
            (english, ["Cancel subscription", "Forgot password", "aria-label=\"Open support chat\"", "placeholder=\"Ask about Thai2Drive...\""]),
        ]:
            for text in expected:
                self.assertIn(text, html)
        self.assertIn('data-q="ช่วยยกเลิกสมาชิก Premium ให้หน่อย"', thai)
        self.assertIn('data-q="How do I cancel my subscription?"', english)
        self.assertNotIn("data-q=\"Hvordan", thai + english)
        self.assertNotIn("__", thai + english)

    def test_thai_quick_questions_use_escalating_complaint_payloads(self):
        from backend.website import _localized_chat_widget_html

        thai = _localized_chat_widget_html("th")
        for payload in [
            "ฉันจ่าย Premium แล้วแต่ยังใช้งานไม่ได้",
            "ช่วยยกเลิกสมาชิก Premium ให้หน่อย",
            "ฉันต้องการลบบัญชีและข้อมูลทั้งหมด",
        ]:
            self.assertIn(f'data-q="{payload}"', thai)

    def test_legacy_pages_render_widget_labels_instead_of_template_tokens(self):
        from backend.website import _page

        html = _page("Support", "<main>Support</main>")
        self.assertIn('aria-label="Åpne supportchat"', html)
        self.assertIn('placeholder="Spør om Thai2Drive..."', html)
        self.assertNotRegex(html, r"__[A-Z_]+__")

    def test_unknown_language_hides_widget_and_never_borrows_norwegian(self):
        from backend.website import _localized_chat_widget_html

        self.assertEqual(_localized_chat_widget_html("unknown"), "")
        for mapping in ("greetings", "noReplyMsgs", "escalatedMsgs", "networkErrMsgs"):
            self.assertNotIn(f"|| {mapping}.no", self.content)

    def test_thai_complaints_escalate_even_when_keywords_touch_thai_text(self):
        from backend.support_chat import _quick_escalation_check

        complaints = [
            "ฉันจ่าย Premium แล้วแต่ยังใช้งานไม่ได้",
            "ช่วยยกเลิกสมาชิก Premium ให้หน่อย",
            "ฉันต้องการลบบัญชีและข้อมูลทั้งหมด",
        ]
        for message in complaints:
            with self.subTest(message=message):
                escalated, _, _ = _quick_escalation_check(message)
                self.assertTrue(escalated)

    def test_ordinary_thai_message_does_not_escalate(self):
        from backend.support_chat import _quick_escalation_check

        self.assertEqual(
            _quick_escalation_check("วันนี้อากาศดี ฉันกำลังฝึกขับรถ"),
            (False, "general", "low"),
        )


if __name__ == "__main__":
    unittest.main()
