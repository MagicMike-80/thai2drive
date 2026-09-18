"""
Document Routes — Student notes and PDF upload endpoint (TASK-009).
-------------------------------------------------------------------
POST /api/documents/upload
Accepts an uploaded PDF, extracts text using pypdf, bounds it to max 4000 chars,
and returns structured JSON with document_id and extracted_text ready for Michael AI Chat.
"""
from __future__ import annotations

import io
import re
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
import pypdf

logger = logging.getLogger("document_routes")

document_router = APIRouter(tags=["documents"])

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_EXTRACTED_CHARS = 4000


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique generated ID for the uploaded document")
    filename: str = Field(..., description="Original or safe file name")
    extracted_text: str = Field(..., description="Cleaned and bounded extracted text from PDF")
    character_count: int = Field(..., description="Number of characters in extracted_text")


def extract_text_from_pdf_bytes(raw_bytes: bytes, max_chars: int = MAX_EXTRACTED_CHARS) -> str:
    """Extract and sanitize text from raw PDF bytes using pypdf."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Ugyldig eller korrupt PDF-fil") from exc

    if not reader.pages:
        raise HTTPException(status_code=400, detail="PDF-filen inneholder ingen sider")

    extracted_pages = []
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(page_text)
        except Exception:
            continue

    raw_text = "\n\n".join(extracted_pages)
    cleaned_text = re.sub(r"[ \t]+", " ", raw_text)
    cleaned_text = re.sub(r"\n\s*\n", "\n\n", cleaned_text).strip()

    if not cleaned_text:
        raise HTTPException(status_code=400, detail="PDF-filen inneholder ingen lesbar tekst")

    if len(cleaned_text) > max_chars:
        cleaned_text = cleaned_text[:max_chars].rstrip() + "..."

    return cleaned_text


@document_router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
) -> DocumentUploadResponse:
    """Upload a PDF file, extract text via pypdf, and prepare context for Michael AI Chat."""
    filename = Path(file.filename or "notat.pdf").name
    ext = Path(filename).suffix.lower()
    content_type = (file.content_type or "").split(";")[0].strip().lower()

    if ext != ".pdf" and content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Kun PDF-filer støttes")

    raw_bytes = await file.read()

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Filen er tom")

    if len(raw_bytes) > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Filen er for stor (maks {MAX_DOCUMENT_SIZE_BYTES // (1024 * 1024)} MB)",
        )

    extracted_text = extract_text_from_pdf_bytes(raw_bytes, max_chars=MAX_EXTRACTED_CHARS)
    document_id = f"doc_{uuid.uuid4().hex[:12]}"

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        extracted_text=extracted_text,
        character_count=len(extracted_text),
    )
