"""
Tests for /api/documents/upload endpoint and PDF text extraction (TASK-009).
"""
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from backend.document_routes import (
        document_router,
        extract_text_from_pdf_bytes,
        MAX_DOCUMENT_SIZE_BYTES,
        MAX_EXTRACTED_CHARS,
    )
except ImportError:
    from document_routes import (
        document_router,
        extract_text_from_pdf_bytes,
        MAX_DOCUMENT_SIZE_BYTES,
        MAX_EXTRACTED_CHARS,
    )

import pypdf

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
        self.assertIn("Vikeplikt gjelder fra hoeyre", data["extracted_text"])
        self.assertEqual(data["character_count"], len(data["extracted_text"]))

    def test_reject_invalid_file_extension(self):
        """Uploading non-PDF files must be rejected with 400 Bad Request."""
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
        writer = pypdf.PdfWriter()
        # Mocking extract_text return via mock page
        class MockPage:
            def extract_text(self):
                return long_text

        class MockReader:
            pages = [MockPage()]

        with patch("pypdf.PdfReader", return_value=MockReader()):
            extracted = extract_text_from_pdf_bytes(b"%PDF-mock", max_chars=4000)
            self.assertEqual(len(extracted), 4003)  # 4000 + "..."
            self.assertTrue(extracted.endswith("..."))

    def test_document_router_mounted_in_server_app(self):
        """The document_router must be registered on /api/documents/upload in server.py."""
        try:
            import server
        except ImportError:
            import backend.server as server

        routes = [route.path for route in server.app.routes]
        self.assertIn("/api/documents/upload", routes)


if __name__ == "__main__":
    unittest.main()
