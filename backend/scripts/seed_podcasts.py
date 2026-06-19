"""
seed_podcasts.py — insert the 3 existing podcast MP3s into learning_podcasts collection.
Run: python backend/scripts/seed_podcasts.py
Safe to re-run — skips existing entries by file_path.
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "")
if not MONGO_URL:
    # Load from .env in the backend directory
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGO_URL="):
                    MONGO_URL = line.split("=", 1)[1].strip('"').strip("'")
                    break
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not found in environment or .env")
DB_NAME = "thai2drive"

PODCASTS = [
    {
        "file_path": "/public_assets/podcast_kongen_tjeneren.mp3",
        "title_no": "Er du kongen eller tjeneren i trafikken?",
        "title_th": "คุณเป็นราชาหรือคนรับใช้บนท้องถนน?",
        "title_en": "Are you the king or servant in traffic?",
        "topic_tags": ["Vikeplikt", "Avstand og tid", "Sikt og fart"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "",
        "understand_context": "",
        "choose_context": "",
        "instructor_summary_no": "Mange sjåfører tror de eier veien. Michael forklarer hva som skiller kongen fra tjeneren — og hvorfor tjeneren alltid kommer hjem.",
        "instructor_summary_th": "ผู้ขับขี่หลายคนคิดว่าตัวเองเป็นเจ้าของถนน ไมเคิลอธิบายความแตกต่างระหว่างราชาและคนรับใช้ — และทำไมคนรับใช้ถึงกลับบ้านได้เสมอ",
        "instructor_summary_en": "Many drivers think they own the road. Michael explains what separates the king from the servant — and why the servant always makes it home.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_ferske_sjaforer.mp3",
        "title_no": "Hvorfor ferske sjåfører er livsfarlige",
        "title_th": "ทำไมคนขับมือใหม่ถึงอันตรายอย่างยิ่ง",
        "title_en": "Why fresh drivers are extremely dangerous",
        "topic_tags": ["Reaksjonstid", "Sikt og fart", "Tretthet"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "",
        "understand_context": "",
        "choose_context": "",
        "instructor_summary_no": "Nye sjåfører mangler ikke vilje — de mangler automatiserte beslutninger. Michael forklarer det nevrologiske gapet mellom nybegynnere og erfarne sjåfører.",
        "instructor_summary_th": "คนขับมือใหม่ไม่ได้ขาดความตั้งใจ — แต่ขาดการตัดสินใจแบบอัตโนมัติ ไมเคิลอธิบายช่องว่างทางระบบประสาทระหว่างมือใหม่และมืออาชีพ",
        "instructor_summary_en": "New drivers don't lack will — they lack automated decisions. Michael explains the neurological gap between beginners and experienced drivers.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_fortere_enn_du_ser.mp3",
        "title_no": "Du kjører fortere enn du ser",
        "title_th": "คุณขับรถเร็วกว่าที่คุณเห็น",
        "title_en": "You drive faster than you can see",
        "topic_tags": ["Bremsing", "Reaksjonstid", "Fartsgrense", "Sikt og fart"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "",
        "understand_context": "",
        "choose_context": "",
        "instructor_summary_no": "Hjernen behandler ikke fart korrekt. Michael demonstrerer illusjonen som dreper flest i trafikken — og den enkle vanen som bryter den.",
        "instructor_summary_th": "สมองไม่ได้ประมวลผลความเร็วอย่างถูกต้อง ไมเคิลสาธิตภาพลวงตาที่คร่าชีวิตมากที่สุดในการจราจร — และนิสัยง่ายๆ ที่จะทำลายมัน",
        "instructor_summary_en": "The brain doesn't process speed correctly. Michael demonstrates the illusion that kills the most in traffic — and the simple habit that breaks it.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0
    for p in PODCASTS:
        existing = await db.learning_podcasts.find_one({"file_path": p["file_path"]})
        if existing:
            print(f"  SKIP (already exists): {p['file_path']}")
            skipped += 1
            continue
        doc = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            **p,
        }
        await db.learning_podcasts.insert_one(doc)
        print(f"  INSERT: {p['title_no']}")
        inserted += 1
    print(f"\nDone — {inserted} inserted, {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
