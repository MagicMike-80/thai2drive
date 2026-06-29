"""
seed_podcasts_v4.py — legg til 5 nye/oppdaterte podcaster (m4a).
Trygt å kjøre på nytt — hopper over eksisterende (by file_path).
Kjør: cd thai2drive/backend && python scripts/seed_podcasts_v4.py
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
        "file_path": "/public_assets/podcast_slik_gjor_ai_instinkt.m4a",
        "title_no": "Slik gjør AI trafikkreglene til instinkt",
        "title_th": "AI ช่วยให้กฎจราจรกลายเป็นสัญชาตญาณได้อย่างไร",
        "title_en": "How AI turns traffic rules into instinct",
        "topic_tags": ["Læring", "AI", "Trafikkregler"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "Du pugger regler men glemmer dem under kjøring.",
        "understand_context": "Kan AI hjelpe hjernen din til å reagere riktig uten å tenke?",
        "choose_context": "Bruk AI-verktøy aktivt i forberedelsen til teoriprøven.",
        "instructor_summary_no": "Michael forklarer hvordan AI-basert repetisjon bygger opp automatiske reaksjoner — slik at du handler riktig i trafikken uten å måtte tenke.",
        "instructor_summary_th": "ไมเคิลอธิบายว่าการทบทวนด้วย AI ช่วยสร้างการตอบสนองอัตโนมัติ — ให้คุณทำถูกต้องบนถนนโดยไม่ต้องคิด",
        "instructor_summary_en": "Michael explains how AI-based repetition builds automatic reactions — so you act correctly in traffic without having to think.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_konge_eller_tjener.m4a",
        "title_no": "Konge eller tjener i trafikken?",
        "title_th": "ราชาหรือผู้รับใช้บนถนน?",
        "title_en": "King or servant in traffic?",
        "topic_tags": ["Vikeplikt", "Atferd", "Trafikkregler"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "Noen sjåfører oppfører seg som om de eier veien.",
        "understand_context": "Hva er egentlig vikepliktreglene — og hvorfor er holdning like viktig som regler?",
        "choose_context": "Velg å være en trygg og hensynsfull sjåfør, ikke en som presser frem.",
        "instructor_summary_no": "Michael tar opp vikepliktreglene og forklarer forskjellen mellom sjåfører som «eier» veien og de som forstår at trafikk er samspill.",
        "instructor_summary_th": "ไมเคิลพูดถึงกฎให้ทางและอธิบายความแตกต่างระหว่างผู้ขับขี่ที่ 'ครองถนน' กับผู้ที่เข้าใจว่าการจราจรคือการร่วมมือกัน",
        "instructor_summary_en": "Michael covers right-of-way rules and explains the difference between drivers who 'own' the road and those who understand that traffic is cooperation.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_ferske_sjaforer.m4a",
        "title_no": "Hvorfor ferske sjåfører er livsfarlige",
        "title_th": "ทำไมผู้ขับขี่มือใหม่ถึงอันตรายถึงชีวิต",
        "title_en": "Why new drivers are dangerously risky",
        "topic_tags": ["Nybegynnere", "Sikkerhet", "Erfaring"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "Du har nettopp fått lappen og kjører alene for første gang.",
        "understand_context": "Hva gjør ferske sjåfører farlige — og hva kan du gjøre for å ikke bli en statistikk?",
        "choose_context": "Vær bevisst på dine begrensninger og kjør defensivt de første månedene.",
        "instructor_summary_no": "Michael forklarer hvorfor ulykkesrisikoen er høyest de første månedene etter at man får lappen — og hvilke grep du kan ta for å overleve den fasen.",
        "instructor_summary_th": "ไมเคิลอธิบายว่าทำไมความเสี่ยงอุบัติเหตุจึงสูงสุดในช่วงไม่กี่เดือนแรกหลังได้ใบขับขี่ — และสิ่งที่คุณทำได้เพื่อผ่านช่วงนั้นได้อย่างปลอดภัย",
        "instructor_summary_en": "Michael explains why accident risk is highest in the first months after getting a license — and what steps you can take to survive that phase.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_kongen_tjeneren.m4a",
        "title_no": "Kongen og tjeneren i trafikken",
        "title_th": "ราชาและผู้รับใช้ในการจราจร",
        "title_en": "The king and the servant in traffic",
        "topic_tags": ["Vikeplikt", "Atferd", "Trafikkregler"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "Trafikken er full av ulike sjåfører med ulike holdninger.",
        "understand_context": "Hva skiller sjåfører som skaper trygg trafikk fra de som skaper fare?",
        "choose_context": "Velg bevisst hvilken type sjåfør du vil være.",
        "instructor_summary_no": "Michael utforsker to arketyper i trafikken — den som alltid vil frem og den som gir plass. Hvem er du, og hvem bør du være?",
        "instructor_summary_th": "ไมเคิลสำรวจสองต้นแบบในการจราจร — ผู้ที่ต้องการไปข้างหน้าเสมอ และผู้ที่ให้ทาง คุณเป็นใคร และควรเป็นใคร?",
        "instructor_summary_en": "Michael explores two archetypes in traffic — the one who always pushes forward and the one who gives way. Who are you, and who should you be?",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
    {
        "file_path": "/public_assets/podcast_veien_til_lappen_del2.m4a",
        "title_no": "Veien fra thailandsk til norsk førerkort — del 2",
        "title_th": "เส้นทางจากใบขับขี่ไทยสู่นอร์เวย์ — ตอนที่ 2",
        "title_en": "The road from Thai to Norwegian driving licence — part 2",
        "topic_tags": ["Teoriprøve", "Praktisk", "Thailand", "Norge"],
        "sign_ids": [],
        "sign_groups": [],
        "studybook_section_ids": [],
        "see_context": "Du har bestått teorien — nå venter den praktiske kjøreprøven.",
        "understand_context": "Hva er de største forskjellene mellom å kjøre i Thailand og i Norge, og hva forventer sensoren?",
        "choose_context": "Forbered deg spesifikt på norske trafikkregler og sensorkrav, ikke bare det du er vant til fra Thailand.",
        "instructor_summary_no": "Michael fortsetter reisen og ser på det praktiske — kjøreteknikk, sensorforventninger og de vanligste feilene thaiboere gjør på den norske kjøreprøven.",
        "instructor_summary_th": "ไมเคิลเดินทางต่อและมองด้านปฏิบัติ — เทคนิคการขับขี่ ความคาดหวังของผู้ตรวจสอบ และข้อผิดพลาดที่พบบ่อยที่สุดของคนไทยในการสอบขับขี่นอร์เวย์",
        "instructor_summary_en": "Michael continues the journey and looks at the practical side — driving technique, examiner expectations, and the most common mistakes Thai people make on the Norwegian driving test.",
        "duration_seconds": 0,
        "language": "no",
        "active": True,
    },
]

# Old mp3 versions replaced by new m4a files
OLD_PATHS_TO_DEACTIVATE = [
    "/public_assets/podcast_ferske_sjaforer.mp3",
    "/public_assets/podcast_kongen_tjeneren.mp3",
]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = skipped = deactivated = 0

    for old_path in OLD_PATHS_TO_DEACTIVATE:
        result = await db.learning_podcasts.update_one(
            {"file_path": old_path},
            {"$set": {"active": False}}
        )
        if result.modified_count:
            print(f"  DEACTIVATED old: {old_path}")
            deactivated += 1

    for p in PODCASTS:
        existing = await db.learning_podcasts.find_one({"file_path": p["file_path"]})
        if existing:
            print(f"  SKIP (already exists): {p['file_path']}")
            skipped += 1
            continue
        doc = {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(), **p}
        await db.learning_podcasts.insert_one(doc)
        print(f"  INSERT: {p['title_no']}")
        inserted += 1

    print(f"\nDone — {inserted} inserted, {skipped} skipped, {deactivated} deactivated.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
