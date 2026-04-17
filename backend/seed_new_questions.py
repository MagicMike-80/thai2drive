"""Seed 4 new questions with images, mapped to v2 schema."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

LETTERS = ["A", "B", "C", "D"]

QUESTIONS = [
    {
        "q": {"no": "Hva slags skilt er dette?", "th": "ป้ายนี้คือป้ายประเภทใด?", "en": "What type of sign is this?"},
        "opts": [
            {"no": "Påbudsskilt", "th": "ป้ายบังคับ", "en": "Mandatory sign"},
            {"no": "Forbudsskilt", "th": "ป้ายห้าม", "en": "Prohibition sign"},
            {"no": "Fareskilt", "th": "ป้ายเตือน", "en": "Warning sign"},
            {"no": "Opplysningsskilt", "th": "ป้ายข้อมูล", "en": "Information sign"},
        ],
        "correct": "A",
        "expl": {"no": "Blå rund skilt viser påbud – her rundkjøring.", "th": "ป้ายวงกลมสีน้ำเงินคือป้ายบังคับ", "en": "Blue circular signs indicate mandatory instructions"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/2mh1jzh5_Screenshot_20260418_001033.jpg",
        "cat": "Traffic Signs", "diff": "easy",
    },
    {
        "q": {"no": "Du kjører på motorvei med flere kjørefelt i samme retning. Hvordan bør du kjøre?", "th": "คุณขับบนมอเตอร์เวย์หลายเลน ควรขับอย่างไร?", "en": "You are driving on a motorway with multiple lanes. How should you drive?"},
        "opts": [
            {"no": "Alltid i venstre felt", "th": "อยู่เลนซ้ายเสมอ", "en": "Always in left lane"},
            {"no": "I høyre felt når det er mulig", "th": "ใช้เลนขวาเมื่อทำได้", "en": "Keep right when possible"},
            {"no": "Midt i veien", "th": "ขับกลางถนน", "en": "Drive in the middle"},
            {"no": "Velg tilfeldig felt", "th": "เลือกเลนตามใจ", "en": "Choose any lane randomly"},
        ],
        "correct": "B",
        "expl": {"no": "Du skal holde til høyre og bruke venstre felt til forbikjøring.", "th": "ควรอยู่เลนขวา ใช้ซ้ายแซง", "en": "Keep right, use left lane for overtaking"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/qhmkgg8s_Screenshot_20260418_001044.jpg",
        "cat": "Road Rules", "diff": "easy",
    },
    {
        "q": {"no": "Hva varsler dette fareskiltet?", "th": "ป้ายเตือนนี้หมายถึงอะไร?", "en": "What does this warning sign indicate?"},
        "opts": [
            {"no": "Kryssende vei fra høyre", "th": "มีทางแยกจากขวา", "en": "Side road from right"},
            {"no": "Farlig sving", "th": "โค้งอันตราย", "en": "Dangerous bend"},
            {"no": "Innsnevring", "th": "ถนนแคบ", "en": "Road narrows"},
            {"no": "Rundkjøring", "th": "วงเวียน", "en": "Roundabout"},
        ],
        "correct": "A",
        "expl": {"no": "Skiltet varsler vei som kommer inn fra høyre.", "th": "เตือนว่ามีถนนมาจากด้านขวา", "en": "Warns of a road joining from the right"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/zv04s9ru_Screenshot_20260418_001053.jpg",
        "cat": "Traffic Signs", "diff": "easy",
    },
    {
        "q": {"no": "Hva må du være særlig oppmerksom på når du kjører i andre nordiske land?", "th": "เมื่อขับในประเทศนอร์ดิกอื่นต้องระวังอะไร?", "en": "What should you be especially aware of when driving in other Nordic countries?"},
        "opts": [
            {"no": "At fartsgrensen alltid er høyere", "th": "ความเร็วสูงกว่าเสมอ", "en": "Speed limits are always higher"},
            {"no": "At trafikkregler kan variere noe", "th": "กฎจราจรอาจต่างกัน", "en": "Traffic rules may vary slightly"},
            {"no": "At det ikke finnes dyr i veien", "th": "ไม่มีสัตว์บนถนน", "en": "No animals on the road"},
            {"no": "At lys ikke er nødvendig", "th": "ไม่ต้องเปิดไฟ", "en": "Lights are not required"},
        ],
        "correct": "B",
        "expl": {"no": "Regler og skilt kan variere noe mellom land.", "th": "กฎและป้ายอาจต่างกันเล็กน้อย", "en": "Rules and signs may vary between countries"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/a1vtqvo0_Screenshot_20260418_001102.jpg",
        "cat": "Safety", "diff": "easy",
    },
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0

    for q in QUESTIONS:
        existing = await db.questions.find_one({"question.no": q["q"]["no"]})
        if existing:
            skipped += 1
            continue
        doc = {
            "id": str(uuid.uuid4()),
            "question": q["q"],
            "options": [{"id": LETTERS[i], "text": q["opts"][i]} for i in range(4)],
            "correctOptionId": q["correct"],
            "explanation": q["expl"],
            "bildeUrl": q["img"],
            "category": q["cat"],
            "difficulty": q["diff"],
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Done! Inserted: {inserted}, Skipped: {skipped}")
    with_images = await db.questions.count_documents({"bildeUrl": {"$ne": None, "$ne": ""}})
    total = await db.questions.count_documents({})
    print(f"Questions with images: {with_images}/{total}")
    client.close()

asyncio.run(seed())
