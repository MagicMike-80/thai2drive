"""
seed_podcasts_v2.py — legg til 4 nye podcaster i learning_podcasts.
Trygt å kjøre på nytt — hopper over eksisterende (by file_path).
Kjør: cd thai2drive/backend && python scripts/seed_podcasts_v2.py
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
    # ── NORSK ──────────────────────────────────────────────────────────────────
    {
        "file_path": "/public_assets/podcast_vikeplikt_regler.mp3",
        "title_no": "Gjør Michaels vikepliktsregler mer intuitive",
        "title_th": "ทำให้กฎการให้ทางของไมเคิลเข้าใจง่ายขึ้น",
        "title_en": "Making Michael's right-of-way rules more intuitive",
        "topic_tags": ["Vikeplikt", "Høyreregel", "Kryss"],
        "sign_ids": [],
        "sign_groups": [3, 4],
        "studybook_section_ids": [],
        "see_context": "Du nærmer deg et kryss uten skilt.",
        "understand_context": "Hvem har vikeplikt når ingen skilt forteller deg det?",
        "choose_context": "Bruk høyreregelen og avkjøringsregelen riktig.",
        "instructor_summary_no": "Vikeplikt føles tilfeldig — til du forstår systemet bak. Michael gjør reglene om til refleks, ikke pugg.",
        "instructor_summary_th": "การให้ทางรู้สึกสุ่มเสี่ยง — จนกว่าคุณจะเข้าใจระบบ ไมเคิลเปลี่ยนกฎให้กลายเป็นสัญชาตญาณ ไม่ใช่การท่องจำ",
        "instructor_summary_en": "Right-of-way feels random — until you understand the system. Michael turns the rules into reflex, not memorization.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_kan_ai_erstatte.m4a",
        "title_no": "Kan AI erstatte kjørelæreren?",
        "title_th": "AI สามารถแทนที่ครูสอนขับรถได้ไหม?",
        "title_en": "Can AI replace the driving instructor?",
        "topic_tags": ["AI og læring", "Kjøreopplæring", "Fremtid"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "En ny type læringsplattform for førerprøven.",
        "understand_context": "Hva kan AI gjøre bedre enn en menneskelig kjørelærer — og hva kan den ikke?",
        "choose_context": "Velg riktig læringsmetode for deg.",
        "instructor_summary_no": "AI kan gi ubegrenset tålmodighet og tilpasset forklaring. Michael diskuterer grensene — og mulighetene.",
        "instructor_summary_th": "AI มีความอดทนไม่จำกัดและสามารถอธิบายได้เป็นรายบุคคล ไมเคิลพูดถึงขีดจำกัด — และโอกาส",
        "instructor_summary_en": "AI can offer unlimited patience and personalized explanations. Michael discusses the limits — and the possibilities.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_veien_til_lappen.m4a",
        "title_no": "Veien fra thailandsk til norsk førerkort",
        "title_th": "เส้นทางจากใบขับขี่ไทยสู่ใบขับขี่นอร์เวย์",
        "title_en": "The road from Thai to Norwegian driving licence",
        "topic_tags": ["Førerprøve", "Thai i Norge", "Oppstart"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "Du er ny i Norge med thailandsk førerkort.",
        "understand_context": "Hva er forskjellen mellom det du allerede kan og det norsk lov krever?",
        "choose_context": "Lag din personlige læringsplan for norsk førerprøve.",
        "instructor_summary_no": "Mange thaier i Norge har kjøreerfaring — men ikke norsk kompetanse. Michael viser nøyaktig hva du mangler og hva du allerede kan.",
        "instructor_summary_th": "คนไทยในนอร์เวย์หลายคนมีประสบการณ์ขับรถ — แต่ไม่มีความรู้กฎจราจรนอร์เวย์ ไมเคิลแสดงให้เห็นว่าคุณขาดอะไรและมีอะไรอยู่แล้ว",
        "instructor_summary_en": "Many Thais in Norway have driving experience — but lack Norwegian competence. Michael shows exactly what you're missing and what you already have.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    # ── THAI ───────────────────────────────────────────────────────────────────
    {
        "file_path": "/public_assets/podcast_th_trafikkregler.m4a",
        "title_no": "Norske trafikkregler på thai — hjelper det eller skaper det risiko?",
        "title_th": "กฎจราจรนอร์เวย์ภาษาไทย — ช่วยหรือเสี่ยง?",
        "title_en": "Norwegian traffic rules in Thai — does it help or create risk?",
        "topic_tags": ["Thai i Norge", "Trafikkregler", "Tospråklig læring"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "Du lærer norske trafikkregler på ditt eget morsmål.",
        "understand_context": "Er det tryggere å forstå reglene på thai eller norsk?",
        "choose_context": "Finn din beste læringsmåte.",
        "instructor_summary_no": "Første podcast på thai! Diskuterer om morsmålsbasert læring faktisk gir bedre forståelse — eller skaper forvirring i praksis.",
        "instructor_summary_th": "พอดแคสต์ภาษาไทยอันแรก! พูดคุยว่าการเรียนด้วยภาษาแม่ให้ความเข้าใจดีกว่าหรือสร้างความสับสนในทางปฏิบัติ",
        "instructor_summary_en": "First Thai-language podcast! Discusses whether mother-tongue learning actually gives better understanding — or creates confusion in practice.",
        "duration_seconds": 0,
        "language": "th",
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
