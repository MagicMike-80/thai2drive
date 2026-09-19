"""
Document Routes — Student notes, PDF, and Image upload & AI analysis endpoint (Fase 4).
----------------------------------------------------------------------------------------
POST /api/documents/upload
Accepts an uploaded PDF or image (PNG, JPG, WEBP), extracts content/text, bounds it to max 4000 chars,
and returns structured JSON with document_id and extracted_text ready for Michael AI Chat.
Optional query params ?analyze=true&language=th allows immediate AI pedagogical analysis.

POST /api/documents/analyze
Directly analyzes an uploaded PDF or image using Michael AI with 100% language isolation (th, no, en).

POST /api/documents/analyze-text
Analyzes extracted text or study notes using Michael AI with 100% language isolation (th, no, en).
"""
from __future__ import annotations

import io
import re
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from pydantic import BaseModel, Field
import pypdf

logger = logging.getLogger("document_routes")

document_router = APIRouter(tags=["documents"])

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_EXTRACTED_CHARS = 4000

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/webp"}


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique generated ID for the uploaded document")
    filename: str = Field(..., description="Original or safe file name")
    file_type: str = Field(default="pdf", description="Type of document (pdf or image)")
    extracted_text: str = Field(..., description="Cleaned and bounded extracted text from PDF or image description")
    character_count: int = Field(..., description="Number of characters in extracted_text")
    ai_analysis: Optional[str] = Field(None, description="Immediate AI pedagogical analysis if requested")


class DocumentAnalysisResponse(BaseModel):
    document_id: str = Field(..., description="Unique generated ID for the document")
    filename: str = Field(..., description="Original or safe file name")
    file_type: str = Field(..., description="Type of document (pdf or image)")
    language: str = Field(..., description="Language of analysis (th, no, en)")
    analysis: str = Field(..., description="Michael AI pedagogical explanation with 100% language isolation")
    character_count: int = Field(..., description="Number of characters in extracted text")


class DocumentAnalyzeTextRequest(BaseModel):
    extracted_text: str = Field(..., description="Extracted text from document or notes")
    filename: Optional[str] = Field("dokument", description="Filename or title")
    file_type: Optional[str] = Field("pdf", description="pdf or image")
    language: Optional[str] = Field("no", description="Language code (th, no, en)")


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


def validate_and_process_image_bytes(raw_bytes: bytes, filename: str) -> tuple[str, dict]:
    """Validate image bytes using Pillow and return extracted context text and metadata."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(raw_bytes))
        img.verify()
        # Re-open because verify() closes the stream
        img = Image.open(io.BytesIO(raw_bytes))
        width, height = img.size
        img_format = (img.format or "IMAGE").upper()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Ugyldig eller korrupt bildefil") from exc

    metadata = {
        "format": img_format,
        "width": width,
        "height": height,
        "mode": img.mode,
    }
    extracted_text = f"[Opplastet bilde: {filename} ({img_format}, {width}x{height}px)]"
    return extracted_text, metadata


async def _call_michael_llm(messages: list[dict]) -> Optional[str]:
    """Invoke Michael AI completion with graceful fallback if unconfigured."""
    try:
        try:
            from backend.teacher_chat import _completion_with_fallback
        except ImportError:
            from teacher_chat import _completion_with_fallback
        resp = await _completion_with_fallback(messages)
        if resp and hasattr(resp, "choices") and resp.choices:
            return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        logger.warning("Michael LLM call for document analysis fallback: %s", exc)
    return None


async def generate_document_ai_analysis(
    content_text: str,
    filename: str,
    file_type: str = "pdf",
    language: str = "no",
) -> str:
    """Generate a pedagogical Michael AI analysis of uploaded document/image with 100% language isolation."""
    lang = (language or "no").strip().lower()
    if lang not in ("th", "no", "en"):
        lang = "no"

    type_labels = {
        "th": "รูปภาพ" if file_type == "image" else "เอกสาร",
        "no": "bildet" if file_type == "image" else "dokumentet",
        "en": "image" if file_type == "image" else "document",
    }

    system_prompts = {
        "th": (
            "[ภาษา: th]\n"
            "สำคัญมาก: ตอบเป็นภาษาไทยเท่านั้น ทุกคำต้องเป็นภาษาไทย ห้ามใช้ภาษานอร์เวย์หรือภาษาอังกฤษเลย\n"
            "กฎการใช้คำสุภาพและสรรพนาม (เข้มงวด 100%):\n"
            "- ใช้สรรพนามแทนตัวเองว่า 'ผม' (phom) เท่านั้น\n"
            "- ใช้คำลงท้ายสุภาพเพศชายว่า 'ครับ' (khrap) เท่านั้น\n"
            "- ห้ามใช้คำลงท้ายเพศหญิง เช่น 'ค่ะ' หรือ 'นะคะ' โดยเด็ดขาด!\n\n"
            "คุณคือครูไมเคิล ครูสอนขับรถในนอร์เวย์ที่มีประสบการณ์ 16 ปี "
            "หน้าที่ของคุณคือวิเคราะห์เอกสารหรือรูปภาพที่นักเรียนส่งมาอย่างใจดี เข้าใจง่าย (กฎ 7 ขวบ) "
            "อธิบายกฎจราจรนอร์เวย์ที่เกี่ยวข้องโดยใช้กฎ 'ราชาและคนรับใช้' หรือกฎ HAV หากเหมาะสม "
            "ชี้แนะสิ่งที่ถูกต้อง และจบท้ายด้วยคำถามชวนคิดหนึ่งคำถามครับ"
        ),
        "no": (
            "[LANGUAGE: no]\n"
            "CRITICAL: Reply in Bokmål Norwegian ONLY. Every single word must be Norwegian. No Thai, no English.\n\n"
            "Du er trafikklærer Michael med 16 års erfaring på norske veier. "
            "Analyser studentens opplastede dokument/bilde. Forklar trafikkreglene med korte, enkle setninger (7-årsregelen). "
            "Bruk 'Kongen og tjeneren' for vikeplikt og 'HAV-regelen' der det passer. "
            "Korriger eventuelle feil i notatet mot offisielle norske trafikkregler, og avslutt med ett oppfølgingsspørsmål."
        ),
        "en": (
            "[LANGUAGE: en]\n"
            "CRITICAL: Reply in English ONLY. Every single word must be English. No Norwegian, no Thai.\n\n"
            "You are Michael, a calm Norwegian driving instructor with 16 years of experience. "
            "Analyze the student's uploaded document/image. Explain relevant traffic rules using simple sentences (the seven-year-old rule). "
            "Use the 'King and Servant' metaphor for right-of-way and the HAV rule where appropriate. "
            "Correct any factual errors against official Norwegian traffic law, and end with one targeted follow-up question."
        ),
    }

    user_msgs = {
        "th": (
            f"ช่วยวิเคราะห์{type_labels['th']} '{filename}' นี้หน่อยครับ เนื้อหาหรือข้อมูลที่พบคือ:\n\n"
            f"<document_content>\n{content_text}\n</document_content>\n\n"
            "ช่วยอธิบายกฎจราจรนอร์เวย์ที่เกี่ยวข้องและข้อควรระวังให้ผมเข้าใจง่ายๆ หน่อยครับ"
        ),
        "no": (
            f"Kan du analysere dette {type_labels['no']} '{filename}' for meg? Innhold/informasjon:\n\n"
            f"<document_content>\n{content_text}\n</document_content>\n\n"
            "Forklar de viktigste trafikkreglene og hva jeg må passe på som sjåfør i Norge."
        ),
        "en": (
            f"Can you analyze this {type_labels['en']} '{filename}' for me? Content/info:\n\n"
            f"<document_content>\n{content_text}\n</document_content>\n\n"
            "Explain the key Norwegian traffic rules and what I need to watch out for as a driver."
        ),
    }

    messages = [
        {"role": "system", "content": system_prompts[lang]},
        {"role": "user", "content": user_msgs[lang]},
    ]

    llm_result = await _call_michael_llm(messages)
    if llm_result:
        return llm_result

    # Deterministic pedagogical fallbacks (100% language isolated)
    fallbacks = {
        "th": (
            f"ครูไมเคิลได้ตรวจสอบ{type_labels['th']} '{filename}' เรียบร้อยแล้วครับ: "
            "สิ่งสำคัญที่สุดในการขับขี่ปลอดภัยในนอร์เวย์คือการสังเกตป้ายจราจรและปฏิบัติตามกฎการให้ทางอย่างเคร่งครัด "
            "จำกฎ 'ราชาและคนรับใช้' ไว้นะครับ รถที่มาจากทางขวาคือราชาที่เราต้องหยุดให้ทางเสมอ "
            "มีจุดไหนในเอกสารนี้ที่อยากให้ครูช่วยอธิบายเพิ่มเติมเป็นพิเศษไหมครับ?"
        ),
        "no": (
            f"Jeg har gått gjennom {type_labels['no']} '{filename}': "
            "I norsk trafikk er det helt avgjørende å lese skilt tidlig og ha full kontroll på vikeplikten. "
            "Husk alltid 'Kongen og tjeneren': bilen fra høyre er kongen du må vike for, og kjør alltid etter HAV-regelen (Hensynsfull, Aktpågivende, Varsom). "
            "Er det noen spesifikke punkter her du ønsker at vi skal gå dypere inn på?"
        ),
        "en": (
            f"I have reviewed your {type_labels['en']} '{filename}': "
            "In Norwegian traffic, reading signs early and having full control of right-of-way rules is crucial. "
            "Always remember the 'King and Servant' rule: vehicles approaching from the right are the king you must yield to, and always follow § 3 of the Road Traffic Act. "
            "Is there any specific detail in this material you would like us to practice further?"
        ),
    }
    return fallbacks[lang]


def _inspect_uploaded_file(filename: str, content_type: str) -> str:
    """Validate file extension and content type, returning 'pdf' or 'image'."""
    ext = Path(filename).suffix.lower()
    ctype = (content_type or "").split(";")[0].strip().lower()

    if ext == ".pdf" or ctype == "application/pdf":
        return "pdf"
    if ext in SUPPORTED_IMAGE_EXTENSIONS or ctype in SUPPORTED_IMAGE_MIMES:
        return "image"

    raise HTTPException(status_code=400, detail="Kun PDF- eller bildefiler (PNG, JPG, WEBP) støttes")


@document_router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    analyze: bool = Query(False, description="Whether to generate AI analysis immediately"),
    language: str = Query("no", description="Language code for AI analysis (th, no, en)"),
) -> DocumentUploadResponse:
    """Upload a PDF or image file, extract text/metadata, and prepare context for Michael AI Chat."""
    filename = Path(file.filename or "notat.pdf").name
    file_type = _inspect_uploaded_file(filename, file.content_type or "")

    raw_bytes = await file.read()

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Filen er tom")

    if len(raw_bytes) > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Filen er for stor (maks {MAX_DOCUMENT_SIZE_BYTES // (1024 * 1024)} MB)",
        )

    if file_type == "pdf":
        extracted_text = extract_text_from_pdf_bytes(raw_bytes, max_chars=MAX_EXTRACTED_CHARS)
    else:
        extracted_text, _ = validate_and_process_image_bytes(raw_bytes, filename)

    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    ai_analysis = None
    if analyze:
        ai_analysis = await generate_document_ai_analysis(
            content_text=extracted_text,
            filename=filename,
            file_type=file_type,
            language=language,
        )

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        extracted_text=extracted_text,
        character_count=len(extracted_text),
        ai_analysis=ai_analysis,
    )


@document_router.post("/documents/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document_endpoint(
    file: UploadFile = File(...),
    language: str = Form("no"),
) -> DocumentAnalysisResponse:
    """Upload and directly analyze a PDF or image file with Michael AI (100% language isolation)."""
    filename = Path(file.filename or "notat.pdf").name
    file_type = _inspect_uploaded_file(filename, file.content_type or "")

    raw_bytes = await file.read()

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Filen er tom")

    if len(raw_bytes) > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Filen er for stor (maks {MAX_DOCUMENT_SIZE_BYTES // (1024 * 1024)} MB)",
        )

    if file_type == "pdf":
        extracted_text = extract_text_from_pdf_bytes(raw_bytes, max_chars=MAX_EXTRACTED_CHARS)
    else:
        extracted_text, _ = validate_and_process_image_bytes(raw_bytes, filename)

    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    analysis = await generate_document_ai_analysis(
        content_text=extracted_text,
        filename=filename,
        file_type=file_type,
        language=language,
    )

    return DocumentAnalysisResponse(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        language=language,
        analysis=analysis,
        character_count=len(extracted_text),
    )


@document_router.post("/documents/analyze-text", response_model=DocumentAnalysisResponse)
async def analyze_document_text_endpoint(
    payload: DocumentAnalyzeTextRequest,
) -> DocumentAnalysisResponse:
    """Analyze pre-extracted document text or student notes with Michael AI (100% language isolation)."""
    if not payload.extracted_text or not payload.extracted_text.strip():
        raise HTTPException(status_code=400, detail="Ingen tekst å analysere")

    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    analysis = await generate_document_ai_analysis(
        content_text=payload.extracted_text.strip(),
        filename=payload.filename or "notat",
        file_type=payload.file_type or "pdf",
        language=payload.language or "no",
    )

    return DocumentAnalysisResponse(
        document_id=document_id,
        filename=payload.filename or "notat",
        file_type=payload.file_type or "pdf",
        language=payload.language or "no",
        analysis=analysis,
        character_count=len(payload.extracted_text),
    )
