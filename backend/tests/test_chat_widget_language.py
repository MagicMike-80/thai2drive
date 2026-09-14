"""Offline unit tests for language isolation in the support chat widget JS (website.py)."""
import re
import unittest
from pathlib import Path


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
        self.assertIn("data.reply || (noReplyMsgs[lang] || noReplyMsgs.no)", self.content)

    def test_escalated_message_has_all_three_languages(self):
        body = self._lang_object_body("escalatedMsgs")
        for lang in ["th", "no", "en"]:
            self.assertIn(f"{lang}:", body, f"escalatedMsgs missing '{lang}' translation")
        self.assertIn("escalatedMsgs[lang] || escalatedMsgs.no", self.content)

    def test_network_error_message_has_all_three_languages(self):
        body = self._lang_object_body("networkErrMsgs")
        for lang in ["th", "no", "en"]:
            self.assertIn(f"{lang}:", body, f"networkErrMsgs missing '{lang}' translation")
        self.assertIn("networkErrMsgs[lang] || networkErrMsgs.no", self.content)

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


if __name__ == "__main__":
    unittest.main()
