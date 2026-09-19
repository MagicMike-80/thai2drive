"""
Offline contract and UI tests for Michael Chat PDF upload and document context in webapp.py (TASK-010).
"""
import re
import unittest
from pathlib import Path


class TestMichaelMediaCardsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        webapp_path = Path(__file__).resolve().parent.parent / "webapp.py"
        cls.content = webapp_path.read_text(encoding="utf-8")

    def test_teacher_doc_upload_button_and_input_exist(self):
        """Teacher input bar must contain a file input accepting PDF and a visible trigger button."""
        self.assertIn('id="teacherDocInput"', self.content)
        self.assertIn('type="file"', self.content)
        self.assertIn('accept=".pdf,application/pdf', self.content)
        self.assertIn('onchange="_teacherUploadDoc(this)"', self.content)

        self.assertIn('id="teacherDocBtn"', self.content)
        self.assertIn('class="teacher-doc-btn"', self.content)
        self.assertIn('document.getElementById(\'teacherDocInput\').click()', self.content)
        self.assertIn('data-label-key="teacher_upload_doc"', self.content)

    def test_teacher_doc_badge_elements_exist(self):
        """Teacher screen must have an identifiable dismissable document badge container."""
        self.assertIn('id="teacherDocBadge"', self.content)
        self.assertIn('class="teacher-doc-badge"', self.content)
        self.assertIn('id="teacherDocName"', self.content)
        self.assertIn('id="teacherDocClose"', self.content)
        self.assertIn('onclick="_teacherClearDoc()"', self.content)

    def test_css_conforms_to_dark_mode_and_cyberpunk_palette(self):
        """CSS for document button and badge must use dark mode and allowed cyan/blue accents without yellow/green."""
        match_btn = re.search(r'\.teacher-doc-btn\s*\{([^}]+)\}', self.content)
        self.assertIsNotNone(match_btn, ".teacher-doc-btn CSS rule must be defined")
        btn_body = match_btn.group(1)
        self.assertIn('#60A5FA', btn_body)

        match_badge = re.search(r'\.teacher-doc-badge\s*\{([^}]+)\}', self.content)
        self.assertIsNotNone(match_badge, ".teacher-doc-badge CSS rule must be defined")
        badge_body = match_badge.group(1)
        self.assertIn('#0B1E3B', badge_body)

        # Forbidden neon colors (yellow/green) check
        doc_css_section = btn_body + " " + badge_body
        self.assertNotIn('#FFFF00', doc_css_section)
        self.assertNotIn('#00FF00', doc_css_section)

    def test_javascript_doc_upload_state_and_handlers_defined(self):
        """Global state _teacherUploadedDoc and async functions _teacherUploadDoc and _teacherClearDoc must be defined."""
        self.assertIn('var _teacherUploadedDoc = null;', self.content)

        match_upload = re.search(r'async\s+function\s+_teacherUploadDoc\s*\([^)]*\)\s*\{([\s\S]+?)\n\}', self.content)
        self.assertIsNotNone(match_upload, "_teacherUploadDoc function must be defined")
        upload_body = match_upload.group(1)
        self.assertIn("FormData()", upload_body)
        self.assertIn("/api/documents/upload", upload_body)
        self.assertIn("_teacherUploadedDoc = data", upload_body)
        self.assertIn("teacherDocBadge", upload_body)

        match_clear = re.search(r'function\s+_teacherClearDoc\s*\([^)]*\)\s*\{([\s\S]+?)\n\}', self.content)
        self.assertIsNotNone(match_clear, "_teacherClearDoc function must be defined")
        clear_body = match_clear.group(1)
        self.assertIn("_teacherUploadedDoc = null", clear_body)
        self.assertIn("teacherDocBadge", clear_body)

    def test_chat_payload_includes_document_id_and_context(self):
        """teacherSend must append document_id and document_context from _teacherUploadedDoc into the chat payload."""
        match_send = re.search(r'async\s+function\s+teacherSend\s*\([^)]*\)\s*\{([\s\S]+?)\nfunction\s+', self.content)
        self.assertIsNotNone(match_send, "teacherSend function must be present")
        send_body = match_send.group(1)

        self.assertIn("chatPayload", send_body)
        self.assertIn("_teacherUploadedDoc", send_body)
        self.assertIn("chatPayload.document_id = _teacherUploadedDoc.document_id", send_body)
        self.assertIn("chatPayload.document_context = _teacherUploadedDoc.extracted_text", send_body)
        self.assertIn("/api/teacher/chat", send_body)

    def test_translations_isolation_no_bleed_through(self):
        """Translations for document upload must exist for th, no, en with 100% language isolation."""
        required_keys = [
            "teacher_upload_doc",
            "teacher_doc_chars",
            "teacher_doc_uploading",
            "teacher_doc_error",
            "teacher_doc_remove",
        ]
        for key in required_keys:
            pattern = rf"{key}\s*:\s*\{{([^}}]+)\}}"
            match = re.search(pattern, self.content)
            self.assertIsNotNone(match, f"Translation key {key} must be defined in TR")
            body = match.group(1)
            self.assertIn("th:", body)
            self.assertIn("no:", body)
            self.assertIn("en:", body)

            # Ensure Thai translation contains actual Thai characters and no English/Norwegian fallback
            th_part = re.search(r"th:\s*'([^']+)'", body)
            self.assertIsNotNone(th_part, f"Thai translation for {key} must be defined")
            th_val = th_part.group(1)
            has_thai = any('\u0e00' <= char <= '\u0e7f' for char in th_val)
            self.assertTrue(has_thai, f"Thai text for {key} must contain Thai characters: {th_val}")


if __name__ == "__main__":
    unittest.main()
