"""
Tests for TeacherChatRequest document context extension and pypdf integration (TASK-008).
"""
import asyncio
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pypdf

try:
    from backend.teacher_chat import (
        TeacherChatRequest,
        TeacherChatResponse,
        _format_student_document_context,
        teacher_chat,
    )
    import backend.teacher_chat as tc
except ImportError:
    from teacher_chat import (
        TeacherChatRequest,
        TeacherChatResponse,
        _format_student_document_context,
        teacher_chat,
    )
    import teacher_chat as tc


class _Cursor:
    def __init__(self, items=None):
        self.items = items or []

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return list(self.items)


class _Collection:
    def __init__(self, items=None):
        self.items = items or []

    def find(self, *args, **kwargs):
        return _Cursor()

    async def find_one(self, *args, **kwargs):
        query = args[0] if args else {}
        for item in self.items:
            if all(item.get(key) == value for key, value in query.items()):
                return item
        return None

    async def insert_one(self, *args, **kwargs):
        return None

    async def insert_many(self, *args, **kwargs):
        return None


class _Database:
    def __init__(self, collections=None):
        self.collections = collections or {}

    def __getitem__(self, name):
        return self.collections.get(name, _Collection())

    def __getattr__(self, name):
        return _Collection()


class TestTeacherChatDocumentContext(unittest.TestCase):
    def test_pypdf_dependency_importable_and_usable(self):
        """pypdf must be installed and functional."""
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=100, height=100)
        buf = io.BytesIO()
        writer.write(buf)
        buf.seek(0)
        reader = pypdf.PdfReader(buf)
        self.assertEqual(len(reader.pages), 1)

    def test_teacher_chat_request_accepts_valid_document_fields(self):
        """TeacherChatRequest must accept valid document_id and document_context."""
        req = TeacherChatRequest(
            message="Hva betyr dette notatet?",
            language="no",
            document_id="doc_abc123",
            document_context="Mine notater om vikeplikt og forkjørsvei.",
        )
        self.assertEqual(req.document_id, "doc_abc123")
        self.assertEqual(req.document_context, "Mine notater om vikeplikt og forkjørsvei.")

    def test_teacher_chat_request_backward_compatible_without_document_fields(self):
        """TeacherChatRequest without document_id or document_context must default to None."""
        req = TeacherChatRequest(
            message="Forklar skilt 202",
            language="th",
        )
        self.assertIsNone(req.document_id)
        self.assertIsNone(req.document_context)
        self.assertEqual(req.mode, "normal_chat")

    def test_teacher_chat_request_enforces_document_id_max_length(self):
        """document_id must not exceed 64 characters."""
        with self.assertRaises(ValidationError):
            TeacherChatRequest(
                message="Test",
                language="no",
                document_id="a" * 65,
            )

    def test_teacher_chat_request_enforces_document_context_max_length(self):
        """document_context must not exceed 4000 characters."""
        with self.assertRaises(ValidationError):
            TeacherChatRequest(
                message="Test",
                language="no",
                document_context="x" * 4001,
            )

    def test_format_student_document_context_isolated_xml_block(self):
        """_format_student_document_context must generate isolated XML boundary and correction rules."""
        raw_notes = "   Vikeplikt fra venstre gjelder i Norge.   "
        formatted = _format_student_document_context(raw_notes)

        self.assertIn("<student_document_notes>", formatted)
        self.assertIn("Vikeplikt fra venstre gjelder i Norge.", formatted)
        self.assertIn("</student_document_notes>", formatted)
        self.assertIn("RULES FOR STUDENT NOTES:", formatted)
        self.assertIn("Always correct any factual mistakes", formatted)

    def test_format_student_document_context_empty_when_none_or_blank(self):
        """_format_student_document_context must return empty string for None or whitespace."""
        self.assertEqual(_format_student_document_context(None), "")
        self.assertEqual(_format_student_document_context(""), "")
        self.assertEqual(_format_student_document_context("   \n\t  "), "")


class TestTeacherChatPromptInjection(unittest.TestCase):
    def setUp(self):
        self._orig_db = tc._db
        self._orig_chat_col = tc._chat_col
        tc._db = _Database()
        tc._chat_col = _Collection()

    def tearDown(self):
        tc._db = self._orig_db
        tc._chat_col = self._orig_chat_col

    def test_system_prompt_injects_document_context_when_provided(self):
        mock_choice = AsyncMock()
        mock_choice.message.content = "Hei! Notatene dine nevner vikeplikt. La oss se på reglene sammen."
        mock_resp = AsyncMock()
        mock_resp.choices = [mock_choice]
        mock_completion = AsyncMock(return_value=mock_resp)

        req = TeacherChatRequest(
            message="Kan du forklare notatene mine?",
            language="no",
            document_context="Elevnotater: bil fra venstre har forkjørsrett.",
        )

        with patch.object(tc, "_completion_with_fallback", mock_completion), \
             patch.object(tc, "LLM_KEY", "dummy_key"):
            response = asyncio.run(teacher_chat(req))

        self.assertIsInstance(response, TeacherChatResponse)
        mock_completion.assert_called_once()
        sent_messages = mock_completion.call_args[0][0]
        system_msg = sent_messages[0]["content"]

        self.assertIn("<student_document_notes>", system_msg)
        self.assertIn("Elevnotater: bil fra venstre har forkjørsrett.", system_msg)
        self.assertIn("</student_document_notes>", system_msg)
        self.assertIn("Always correct any factual mistakes", system_msg)

    def test_system_prompt_omits_document_context_when_not_provided(self):
        mock_choice = AsyncMock()
        mock_choice.message.content = "Hei! Hva lurer du på?"
        mock_resp = AsyncMock()
        mock_resp.choices = [mock_choice]
        mock_completion = AsyncMock(return_value=mock_resp)

        req = TeacherChatRequest(
            message="Hva er vikeplikt?",
            language="no",
        )

        with patch.object(tc, "_completion_with_fallback", mock_completion), \
             patch.object(tc, "LLM_KEY", "dummy_key"):
            response = asyncio.run(teacher_chat(req))

        self.assertIsInstance(response, TeacherChatResponse)
        mock_completion.assert_called_once()
        sent_messages = mock_completion.call_args[0][0]
        system_msg = sent_messages[0]["content"]

        self.assertNotIn("<student_document_notes>", system_msg)


if __name__ == "__main__":
    unittest.main()
