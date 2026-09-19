"""
Tests for /api/documents/upload and /api/documents/analyze endpoints (TASK-009 & Fase 4).
Covers PDF text extraction, image uploads (PNG, JPEG, WEBP), AI analysis, and 100% language isolation.
"""
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from backend.document_routes import (
        document_router,
        extract_text_from_pdf_bytes,
        validate_and_process_image_bytes,
        generate_document_ai_analysis,
        MAX_DOCUMENT_SIZE_BYTES,
        MAX_EXTRACTED_CHARS,
    )
except ImportError:
    from document_routes import (
        document_router,
        extract_text_from_pdf_bytes,
        validate_and_process_image_bytes,
        generate_document_ai_analysis,
        MAX_DOCUMENT_SIZE_BYTES,
        MAX_EXTRACTED_CHARS,
    )

try:
    from backend.teacher_chat import teacher_router
    import backend.teacher_chat as tc
except ImportError:
    from teacher_chat import teacher_router
    import teacher_chat as tc

import pypdf
from PIL import Image

# Valid minimal PDF with readable text
VALID_SAMPLE_PDF = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 55 >> stream
BT /F1 18 Tf 10 100 Td (Vikeplikt gjelder fra hoeyre) Tj ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000227 00000 n 
0000000334 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
407
%%EOF
"""


def _create_blank_pdf_bytes() -> bytes:
    """Create a valid PDF with a single blank page and no text."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _create_sample_png_bytes(width: int = 120, height: int = 80) -> bytes:
    """Create a valid PNG image byte stream for testing."""
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _create_sample_jpeg_bytes(width: int = 100, height: int = 100) -> bytes:
    """Create a valid JPEG image byte stream for testing."""
    img = Image.new("RGB", (width, height), color=(0, 120, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _create_sample_webp_bytes(width: int = 90, height: int = 90) -> bytes:
    """Create a valid WEBP image byte stream for testing."""
    img = Image.new("RGB", (width, height), color=(50, 200, 50))
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()


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


class TestDocumentUploadEndpoint(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(document_router, prefix="/api")
        self.client = TestClient(app)

    def test_valid_pdf_upload_extracts_text(self):
        """Uploading a valid PDF must return 200 OK with document_id and extracted text."""
        files = {
            "file": ("notat_vikeplikt.pdf", io.BytesIO(VALID_SAMPLE_PDF), "application/pdf")
        }
        res = self.client.post("/api/documents/upload", files=files)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["document_id"].startswith("doc_"))
        self.assertEqual(data["filename"], "notat_vikeplikt.pdf")
        self.assertEqual(data["file_type"], "pdf")
        self.assertIn("Vikeplikt gjelder fra hoeyre", data["extracted_text"])
        self.assertEqual(data["character_count"], len(data["extracted_text"]))

    def test_valid_png_upload_processes_metadata(self):
        """Uploading a valid PNG image must return 200 OK with file_type='image' and dimensions."""
        png_bytes = _create_sample_png_bytes(140, 95)
        files = {
            "file": ("trafikkskilt_notat.png", io.BytesIO(png_bytes), "image/png")
        }
        res = self.client.post("/api/documents/upload", files=files)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["document_id"].startswith("doc_"))
        self.assertEqual(data["filename"], "trafikkskilt_notat.png")
        self.assertEqual(data["file_type"], "image")
        self.assertIn("140x95px", data["extracted_text"])
        self.assertIn("PNG", data["extracted_text"])

    def test_valid_jpeg_and_webp_upload(self):
        """Uploading JPEG and WEBP images must both return 200 OK with file_type='image'."""
        # JPEG
        jpeg_bytes = _create_sample_jpeg_bytes(120, 120)
        res_jpeg = self.client.post(
            "/api/documents/upload",
            files={"file": ("kryss.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        )
        self.assertEqual(res_jpeg.status_code, 200)
        self.assertEqual(res_jpeg.json()["file_type"], "image")
        self.assertIn("JPEG", res_jpeg.json()["extracted_text"])

        # WEBP
        webp_bytes = _create_sample_webp_bytes(80, 80)
        res_webp = self.client.post(
            "/api/documents/upload",
            files={"file": ("veikart.webp", io.BytesIO(webp_bytes), "image/webp")},
        )
        self.assertEqual(res_webp.status_code, 200)
        self.assertEqual(res_webp.json()["file_type"], "image")
        self.assertIn("WEBP", res_webp.json()["extracted_text"])

    def test_reject_invalid_file_extension(self):
        """Uploading non-PDF / non-image files must be rejected with 400 Bad Request."""
        # Executable
        res_exe = self.client.post(
            "/api/documents/upload",
            files={"file": ("virus.exe", io.BytesIO(b"MZ..."), "application/octet-stream")},
        )
        self.assertEqual(res_exe.status_code, 400)
        self.assertIn("PDF", res_exe.json()["detail"])

        # Plain text file
        res_txt = self.client.post(
            "/api/documents/upload",
            files={"file": ("notat.txt", io.BytesIO(b"Dette er en tekstfil"), "text/plain")},
        )
        self.assertEqual(res_txt.status_code, 400)
        self.assertIn("PDF", res_txt.json()["detail"])

    def test_reject_empty_file(self):
        """Empty file (0 bytes) must be rejected with 400 Bad Request."""
        files = {"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
        res = self.client.post("/api/documents/upload", files=files)

        self.assertEqual(res.status_code, 400)
        self.assertIn("tom", res.json()["detail"].lower())

    def test_reject_oversized_file(self):
        """Files exceeding 10 MB must return 413 Payload Too Large."""
        oversized = b"0" * (MAX_DOCUMENT_SIZE_BYTES + 1024)
        files = {"file": ("huge.pdf", io.BytesIO(oversized), "application/pdf")}
        res = self.client.post("/api/documents/upload", files=files)

        self.assertEqual(res.status_code, 413)
        self.assertIn("for stor", res.json()["detail"].lower())

    def test_corrupt_pdf_fails_gracefully(self):
        """Corrupted PDF bytes must return 400 Bad Request."""
        files = {"file": ("corrupt.pdf", io.BytesIO(b"Not a real PDF stream at all"), "application/pdf")}
        res = self.client.post("/api/documents/upload", files=files)

        self.assertEqual(res.status_code, 400)
        self.assertIn("korrupt", res.json()["detail"].lower())

    def test_corrupt_image_fails_gracefully(self):
        """Corrupted image bytes must return 400 Bad Request."""
        files = {"file": ("corrupt.png", io.BytesIO(b"Not a real PNG header at all"), "image/png")}
        res = self.client.post("/api/documents/upload", files=files)

        self.assertEqual(res.status_code, 400)
        self.assertIn("korrupt", res.json()["detail"].lower())

    def test_blank_page_pdf_without_text_fails(self):
        """PDF with pages but no extractable text must return 400 Bad Request."""
        blank_pdf = _create_blank_pdf_bytes()
        files = {"file": ("blank.pdf", io.BytesIO(blank_pdf), "application/pdf")}
        res = self.client.post("/api/documents/upload", files=files)

        self.assertEqual(res.status_code, 400)
        self.assertIn("ingen lesbar tekst", res.json()["detail"].lower())

    def test_text_truncation_boundary(self):
        """extract_text_from_pdf_bytes must truncate texts longer than max_chars."""
        long_text = "Trafikkregel " * 500  # ~6500 characters
        class MockPage:
            def extract_text(self):
                return long_text

        class MockReader:
            pages = [MockPage()]

        with patch("pypdf.PdfReader", return_value=MockReader()):
            extracted = extract_text_from_pdf_bytes(b"%PDF-mock", max_chars=4000)
            self.assertEqual(len(extracted), 4003)  # 4000 + "..."
            self.assertTrue(extracted.endswith("..."))

    @patch("backend.document_routes._call_michael_llm", new_callable=AsyncMock)
    def test_upload_with_immediate_analysis_th(self, mock_llm):
        """Uploading with analyze=true&language=th returns immediate Thai pedagogical analysis."""
        mock_llm.return_value = (
            "ครูไมเคิลได้ตรวจสอบเอกสารเรียบร้อยแล้วครับ: สิ่งสำคัญคือการปฏิบัติตามกฎการให้ทางอย่างเคร่งครัด "
            "จำกฎราชาและคนรับใช้ไว้นะครับ มีตรงไหนอยากให้ครูช่วยอธิบายเพิ่มไหมครับ?"
        )
        files = {"file": ("notat.pdf", io.BytesIO(VALID_SAMPLE_PDF), "application/pdf")}
        res = self.client.post("/api/documents/upload?analyze=true&language=th", files=files)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data["ai_analysis"])
        # Verify 100% Thai isolation
        has_thai_chars = any("\u0e00" <= c <= "\u0e7f" for c in data["ai_analysis"])
        self.assertTrue(has_thai_chars, "Analysis must contain Thai characters")
        self.assertNotIn("vikeplikt", data["ai_analysis"].lower())

    @patch("backend.document_routes._call_michael_llm", new_callable=AsyncMock)
    def test_upload_with_immediate_analysis_fallback(self, mock_llm):
        """When LLM is unavailable, fallback guarantees 100% Thai isolation."""
        mock_llm.return_value = None
        files = {"file": ("notat.pdf", io.BytesIO(VALID_SAMPLE_PDF), "application/pdf")}
        res = self.client.post("/api/documents/upload?analyze=true&language=th", files=files)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data["ai_analysis"])
        has_thai_chars = any("\u0e00" <= c <= "\u0e7f" for c in data["ai_analysis"])
        self.assertTrue(has_thai_chars)
        self.assertNotIn("vikeplikt", data["ai_analysis"].lower())

    @patch("backend.document_routes._call_michael_llm", new_callable=AsyncMock)
    def test_direct_analyze_endpoint_for_image_no(self, mock_llm):
        """POST /api/documents/analyze with image returns structured analysis in Norwegian."""
        mock_llm.return_value = (
            "Jeg har analysert bildet ditt: Husk 'Kongen og tjeneren' ved vikeplikt. "
            "Kjør alltid etter HAV-regelen (Hensynsfull, Aktpågivende, Varsom)."
        )
        png_bytes = _create_sample_png_bytes(100, 100)
        files = {"file": ("kryss_situasjon.png", io.BytesIO(png_bytes), "image/png")}
        data = {"language": "no"}
        res = self.client.post("/api/documents/analyze", files=files, data=data)

        self.assertEqual(res.status_code, 200)
        resp_data = res.json()
        self.assertEqual(resp_data["file_type"], "image")
        self.assertEqual(resp_data["language"], "no")
        self.assertIn("Kongen og tjeneren", resp_data["analysis"])

    @patch("backend.document_routes._call_michael_llm", new_callable=AsyncMock)
    def test_direct_analyze_text_endpoint_en(self, mock_llm):
        """POST /api/documents/analyze-text with notes returns structured analysis in English."""
        mock_llm.return_value = (
            "Based on your notes: Remember the King and Servant rule for priority. "
            "Traffic approaching from the right has right-of-way."
        )
        payload = {
            "extracted_text": "Priority rules when entering roundabout and yielding to traffic from left.",
            "filename": "roundabout_notes.txt",
            "file_type": "pdf",
            "language": "en"
        }
        res = self.client.post("/api/documents/analyze-text", json=payload)

        self.assertEqual(res.status_code, 200)
        resp_data = res.json()
        self.assertEqual(resp_data["language"], "en")
        self.assertIn("King and Servant", resp_data["analysis"])

    def test_document_router_mounted_in_server_app(self):
        """The document_router must be registered on /api/documents/upload in server.py."""
        try:
            import server
        except ImportError:
            import backend.server as server

        routes = [route.path for route in server.app.routes]
        self.assertIn("/api/documents/upload", routes)
        self.assertIn("/api/documents/analyze", routes)
        self.assertIn("/api/documents/analyze-text", routes)


class TestDocumentUploadChatIntegration(unittest.TestCase):
    """Integration tests connecting /api/documents/upload, images, and /api/teacher/chat (TASK-009 & Fase 4)."""

    def setUp(self):
        self._orig_db = tc._db
        self._orig_chat_col = tc._chat_col
        self._orig_llm_key = tc.LLM_KEY
        tc._db = _Database()
        tc._chat_col = _Collection()
        tc.LLM_KEY = "mock_key_for_test"

        app = FastAPI()
        app.include_router(document_router, prefix="/api")
        app.include_router(teacher_router, prefix="/api")
        self.client = TestClient(app)

    def tearDown(self):
        tc._db = self._orig_db
        tc._chat_col = self._orig_chat_col
        tc.LLM_KEY = self._orig_llm_key

    def test_upload_and_chat_integration_norwegian(self):
        """Upload Norwegian PDF note, send to /api/teacher/chat, verify Michael references student notes."""
        # 1. Upload PDF
        files = {
            "file": ("notater_vikeplikt.pdf", io.BytesIO(VALID_SAMPLE_PDF), "application/pdf")
        }
        res_upload = self.client.post("/api/documents/upload", files=files)
        self.assertEqual(res_upload.status_code, 200)
        upload_data = res_upload.json()
        doc_id = upload_data["document_id"]
        doc_context = upload_data["extracted_text"]
        self.assertIn("Vikeplikt gjelder fra hoeyre", doc_context)

        # 2. Mock LLM completion
        mock_choice = AsyncMock()
        mock_choice.message.content = (
            "Jeg ser i notatet ditt at du har skrevet at 'Vikeplikt gjelder fra hoeyre'. "
            "Det stemmer! Husk 'Kongen og tjeneren': bilen som kommer fra høyre er kongen du må vike for."
        )
        mock_resp = AsyncMock()
        mock_resp.choices = [mock_choice]
        mock_completion = AsyncMock(return_value=mock_resp)

        # 3. Post to /api/teacher/chat with language: "no"
        chat_payload = {
            "message": "Kan du forklare dette notatet mitt om vikeplikt?",
            "language": "no",
            "document_id": doc_id,
            "document_context": doc_context,
        }

        with patch.object(tc, "_completion_with_fallback", mock_completion):
            res_chat = self.client.post("/api/teacher/chat", json=chat_payload)

        self.assertEqual(res_chat.status_code, 200)
        chat_data = res_chat.json()
        self.assertIn("reply", chat_data)
        self.assertIn("session_id", chat_data)

        # Verify prompt injection
        mock_completion.assert_called_once()
        sent_messages = mock_completion.call_args[0][0]
        system_content = sent_messages[0]["content"]
        self.assertIn("<student_document_notes>", system_content)
        self.assertIn("Vikeplikt gjelder fra hoeyre", system_content)
        self.assertIn("RULES FOR STUDENT NOTES:", system_content)

        # Verify Michael's explanation in Norwegian
        reply = chat_data["reply"]
        self.assertIn("notatet ditt", reply)
        self.assertIn("vikeplikt", reply.lower())

    def test_upload_image_and_chat_integration_thai(self):
        """Upload traffic image, send context to /api/teacher/chat with language: 'th', verify 100% Thai isolation."""
        # 1. Upload PNG Image
        png_bytes = _create_sample_png_bytes(150, 100)
        files = {
            "file": ("kryss_situasjon.png", io.BytesIO(png_bytes), "image/png")
        }
        res_upload = self.client.post("/api/documents/upload", files=files)
        self.assertEqual(res_upload.status_code, 200)
        upload_data = res_upload.json()
        doc_id = upload_data["document_id"]
        doc_context = upload_data["extracted_text"]
        self.assertEqual(upload_data["file_type"], "image")
        self.assertIn("150x100px", doc_context)

        # 2. Mock LLM completion in Thai
        mock_choice = AsyncMock()
        mock_choice.message.content = (
            "จากรูปภาพสถานการณ์การจราจรที่คุณส่งมา ให้จำกฎ 'ราชาและคนรับใช้' ครับ "
            "รถที่มาจากทางขวาคือราชาที่เราต้องหยุดให้ทาง มีตรงไหนอยากให้ครูอธิบายเพิ่มไหมครับ?"
        )
        mock_resp = AsyncMock()
        mock_resp.choices = [mock_choice]
        mock_completion = AsyncMock(return_value=mock_resp)

        # 3. Post to /api/teacher/chat with language: 'th'
        chat_payload = {
            "message": "ช่วยอธิบายรูปภาพสถานการณ์นี้หน่อยครับ",
            "language": "th",
            "document_id": doc_id,
            "document_context": doc_context,
        }

        with patch.object(tc, "_completion_with_fallback", mock_completion):
            res_chat = self.client.post("/api/teacher/chat", json=chat_payload)

        self.assertEqual(res_chat.status_code, 200)
        chat_data = res_chat.json()
        self.assertIn("reply", chat_data)

        # Verify prompt injection
        mock_completion.assert_called_once()
        sent_messages = mock_completion.call_args[0][0]
        system_content = sent_messages[0]["content"]
        self.assertIn("<student_document_notes>", system_content)
        self.assertIn("150x100px", system_content)

        # Verify 100% Thai isolation (contains Thai, no Norwegian)
        reply = chat_data["reply"]
        has_thai_chars = any("\u0e00" <= c <= "\u0e7f" for c in reply)
        self.assertTrue(has_thai_chars, "Reply must contain Thai characters")
        self.assertNotIn("vikeplikt", reply.lower())

    def test_upload_and_chat_integration_thai_language_isolation(self):
        """Upload PDF note, send to /api/teacher/chat with language: 'th', verify 100% Thai language isolation."""
        # 1. Upload PDF
        files = {
            "file": ("notat_th.pdf", io.BytesIO(VALID_SAMPLE_PDF), "application/pdf")
        }
        res_upload = self.client.post("/api/documents/upload", files=files)
        self.assertEqual(res_upload.status_code, 200)
        upload_data = res_upload.json()
        doc_id = upload_data["document_id"]
        doc_context = upload_data["extracted_text"]

        # 2. Mock LLM completion with 100% Thai pedagogical response
        mock_choice = AsyncMock()
        mock_choice.message.content = (
            "จากบันทึกของคุณเรื่องกฎการให้ทาง ให้จำกฎ 'ราชาและคนรับใช้' "
            "รถที่มาจากทางขวาคือราชาที่เราต้องหยุดให้ทางครับ มีตรงไหนอยากให้ครูอธิบายเพิ่มไหม?"
        )
        mock_resp = AsyncMock()
        mock_resp.choices = [mock_choice]
        mock_completion = AsyncMock(return_value=mock_resp)

        # 3. Post to /api/teacher/chat with language: "th"
        chat_payload = {
            "message": "ช่วยอธิบายบันทึกนี้เรื่องกฎการให้ทางหน่อยครับ",
            "language": "th",
            "document_id": doc_id,
            "document_context": doc_context,
        }

        with patch.object(tc, "_completion_with_fallback", mock_completion):
            res_chat = self.client.post("/api/teacher/chat", json=chat_payload)

        self.assertEqual(res_chat.status_code, 200)
        chat_data = res_chat.json()
        self.assertIn("reply", chat_data)
        self.assertIn("session_id", chat_data)

        # Verify system prompt has document context
        mock_completion.assert_called_once()
        sent_messages = mock_completion.call_args[0][0]
        system_content = sent_messages[0]["content"]
        self.assertIn("<student_document_notes>", system_content)

        # Verify 100% Thai language isolation (Thai script present, no Norwegian leak)
        reply = chat_data["reply"]
        has_thai_chars = any("\u0e00" <= c <= "\u0e7f" for c in reply)
        self.assertTrue(has_thai_chars, "Reply must contain Thai characters")
        self.assertNotIn("vikeplikt", reply.lower())
        self.assertNotIn("kongen og tjeneren", reply.lower())

    def test_upload_and_chat_integration_english(self):
        """Upload PDF note, send to /api/teacher/chat with language: 'en', verify pedagogical response in English."""
        # 1. Upload PDF
        files = {
            "file": ("notes_priority.pdf", io.BytesIO(VALID_SAMPLE_PDF), "application/pdf")
        }
        res_upload = self.client.post("/api/documents/upload", files=files)
        self.assertEqual(res_upload.status_code, 200)
        upload_data = res_upload.json()
        doc_id = upload_data["document_id"]
        doc_context = upload_data["extracted_text"]

        # 2. Mock LLM completion with English pedagogical response
        mock_choice = AsyncMock()
        mock_choice.message.content = (
            "Based on your uploaded notes, drivers must yield to traffic approaching from the right. "
            "This priority rule applies at all unregulated intersections."
        )
        mock_resp = AsyncMock()
        mock_resp.choices = [mock_choice]
        mock_completion = AsyncMock(return_value=mock_resp)

        # 3. Post to /api/teacher/chat with language: "en"
        chat_payload = {
            "message": "Can you explain my notes about the priority rule?",
            "language": "en",
            "document_id": doc_id,
            "document_context": doc_context,
        }

        with patch.object(tc, "_completion_with_fallback", mock_completion):
            res_chat = self.client.post("/api/teacher/chat", json=chat_payload)

        self.assertEqual(res_chat.status_code, 200)
        chat_data = res_chat.json()
        self.assertIn("reply", chat_data)
        self.assertIn("session_id", chat_data)

        # Verify system prompt has document context
        mock_completion.assert_called_once()
        sent_messages = mock_completion.call_args[0][0]
        system_content = sent_messages[0]["content"]
        self.assertIn("<student_document_notes>", system_content)

        # Verify English pedagogical response
        reply = chat_data["reply"]
        self.assertIn("uploaded notes", reply)
        self.assertIn("yield to traffic", reply)


if __name__ == "__main__":
    unittest.main()
