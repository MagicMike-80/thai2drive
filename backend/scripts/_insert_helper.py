"""
Reusable helper for inserting a new image question and auto-logging coverage.

Example:
    from scripts._insert_helper import insert_image_question

    insert_image_question(
        image_path="/tmp/signs/foo.jpg",
        question_no="...", question_en="...", question_th="...",
        options=[("A","..","..",".."), ("B",...), ("C",...), ("D",...)],
        correct="B",
        explanation_no="...", explanation_en="...", explanation_th="...",
        category="Traffic Signs",
        difficulty="medium",
        note="Added skilt 118 Sidevind",
    )
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(Path(__file__).parent))
from _img_utils import image_to_base64  # noqa: E402
from coverage import log_coverage  # noqa: E402


def insert_image_question(
    *,
    image_path: str,
    question_no: str,
    question_en: str,
    question_th: str,
    options: list[tuple[str, str, str, str]],  # (id, no, en, th)
    correct: str,
    explanation_no: str,
    explanation_en: str,
    explanation_th: str,
    category: str,
    difficulty: str = "medium",
    note: str = "",
    audit_verdict: str | None = None,
    audit_image_identification: str | None = None,
    max_dim: int = 600,
    quality: int = 80,
) -> str:
    client = MongoClient(os.getenv("MONGO_URL"))
    db = client[os.getenv("DB_NAME")]

    bilde = image_to_base64(image_path, max_dim=max_dim, quality=quality)

    doc = {
        "id": str(uuid.uuid4()),
        "question": {"no": question_no, "en": question_en, "th": question_th},
        "options": [
            {"id": oid, "text": {"no": n, "en": e, "th": t}}
            for oid, n, e, t in options
        ],
        "correctOptionId": correct,
        "explanation": {
            "no": explanation_no,
            "en": explanation_en,
            "th": explanation_th,
        },
        "bildeUrl": bilde,
        "category": category,
        "difficulty": difficulty,
        "active": True,
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc),
    }
    if audit_verdict:
        doc["audit_verdict"] = audit_verdict
    if audit_image_identification:
        doc["audit_image_identification"] = audit_image_identification

    db.questions.insert_one(doc)
    print(f"✓ Inserted {doc['id']} ({category} / {difficulty}, img {len(bilde)//1024} KB)")
    # Always log coverage after insert
    log_coverage(note or f"Inserted {category} question")
    return doc["id"]
