"""
seed_podcasts_v3.py — legg til podcast om bremselengde.
Trygt å kjøre på nytt — hopper over eksisterende (by file_path).
Kjør: cd thai2drive/backend && python scripts/seed_podcasts_v3.py
"""

import asyncio, os, uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "")
if not MONGO_URL:
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
        "file_path": "/public_assets/podcast_bremselengde.m4a",
        "title_no": "Bremselengde — derfor hjelper det ikke å bremse hardt",
        "title_th": "ระยะเบรก — ทำไมเหยียบเบรกแรงไม่ช่วย",
        "title_en": "Braking distance — why slamming the brakes doesn't help",
        "topic_tags": ["Bremselengde", "Fart og avstand", "Sikkerhet"],
        "sign_ids": [],
        "sign_groups": [7],
        "studybook_section_ids": [],
        "see_context": "Du kjører og bilen foran stopper plutselig.",
        "understand_context": "Hva bestemmer egentlig bremselengden — og hvorfor rekker du ikke å stoppe selv om du reagerer raskt?",
        "choose_context": "Hold riktig avstand og tilpass farten slik at du alltid rekker å stoppe.",
        "instructor_summary_no": "Bremselengden dobles når farten øker med 40 %. Michael forklarer fysikken bak — og hvordan du bruker det i praksis på veien.",
        "instructor_summary_th": "ระยะเบรกจะเพิ่มขึ้นสองเท่าเมื่อความเร็วเพิ่มขึ้น 40% ไมเคิลอธิบายฟิสิกส์เบื้องหลัง — และนำไปใช้จริงบนถนน",
        "instructor_summary_en": "Braking distance doubles when speed increases by 40%. Michael explains the physics — and how to apply it on the road.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = skipped = 0
    for p in PODCASTS:
        existing = await db.learning_podcasts.find_one({"file_path": p["file_path"]})
        if existing:
            print(f"  SKIP (already exists): {p['file_path']}")
            skipped += 1
            continue
        doc = {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(), **p}
        await db.learning_podcasts.insert_one(doc)
        print(f"  INSERT [{p['language'].upper()}]: {p['title_no']}")
        inserted += 1
    print(f"\nDone — {inserted} inserted, {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
