"""
add_video.py — insert a single learning video directly into MongoDB.
Run: python backend/scripts/add_video.py

Edit VIDEO below, then run. No admin JWT needed — writes directly to DB.
Topic tags MUST match _dangerLabel() labels exactly (see server.py docstring).
"""

import asyncio
import os
import re
import uuid
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

# ─────────────────────────────────────────────────────────────
#  EDIT THIS SECTION BEFORE RUNNING
# ─────────────────────────────────────────────────────────────
VIDEO = {
    # ── YouTube ──────────────────────────────────────────────
    "youtube_url": "https://www.youtube.com/watch?v=REPLACE_ME",
    "duration_seconds": 0,          # seconds — 0 = not shown

    # ── Titles ───────────────────────────────────────────────
    "title_no": "Bremselengde og reaksjonstid — slik påvirker farten stoppestansen",
    "title_th": "ระยะเบรกและเวลาตอบสนอง — ความเร็วส่งผลอย่างไร",
    "title_en": "",

    # ── Topic matching (must match _dangerLabel() output exactly) ──
    "topic_tags": ["Bremsing", "Reaksjonstid", "Fartsgrense"],

    # ── Sign linking (leave empty if not sign-specific) ──────
    "sign_ids": [],
    "sign_groups": [],

    # ── Curriculum linking ────────────────────────────────────
    "studybook_section_ids": [],

    # ── Se → Forstå → Velg context (shown in video card) ─────
    "see_context":        "Se fartskiltet og merk deg veitype og trafikkforhold",
    "understand_context": "Høyere fart = lengre reaksjons- og bremselengde — eksponentielt",
    "choose_context":     "Velg en fart som gir deg tid til å stoppe innen synlig strekning",

    # ── Instructor summary ────────────────────────────────────
    "instructor_summary_no": "Mange tror bremselengden øker lineært med farten — den øker kvadratisk. Fra 50 til 100 km/t er ikke stansen dobbel, men fire ganger lengre.",
    "instructor_summary_th": "หลายคนคิดว่าระยะเบรกเพิ่มขึ้นตามความเร็วแบบตรงๆ แต่จริงๆ แล้วมันเพิ่มขึ้นแบบยกกำลังสอง",
    "instructor_summary_en": "",

    # ── Language of the video ─────────────────────────────────
    "language": "th",              # th, no, en
    "active": True,
}
# ─────────────────────────────────────────────────────────────

MONGO_URL = os.environ.get(
    "MONGO_URL",
    "mongodb+srv://norge-quiz-app:m2iD3VNMnbxL7LIm@cluster0.mecy7qw.mongodb.net/thai2drive?retryWrites=true&w=majority",
)
DB_NAME = "thai2drive"


def _extract_youtube_id(url: str) -> str:
    for pat in [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return ''


async def main():
    if 'REPLACE_ME' in VIDEO['youtube_url']:
        print("❌  Edit the youtube_url in this script before running.")
        return

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    yt_id = _extract_youtube_id(VIDEO['youtube_url'])
    doc = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "title_no": "", "title_th": "", "title_en": "",
        "youtube_url": "", "thumbnail_url": "", "duration_seconds": 0,
        "language": "no",
        "topic_tags": [], "sign_ids": [], "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "", "understand_context": "", "choose_context": "",
        "instructor_summary_no": "", "instructor_summary_th": "", "instructor_summary_en": "",
        "active": True,
        **VIDEO,
    }
    if not doc.get("thumbnail_url") and yt_id:
        doc["thumbnail_url"] = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"

    result = await db.learning_videos.insert_one(doc)
    print(f"✅  Inserted video — _id: {result.inserted_id}")
    print(f"    Title (no): {doc['title_no']}")
    print(f"    YouTube ID: {yt_id}")
    print(f"    Topic tags: {doc['topic_tags']}")
    print(f"\nVerify with: GET /api/videos/for-topic?tags=Bremsing,Reaksjonstid")

    client.close()


asyncio.run(main())
