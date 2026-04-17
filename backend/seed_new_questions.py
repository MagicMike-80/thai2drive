"""Seed 9 new questions into MongoDB (v2 schema)."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

NEW_QUESTIONS = [
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva betyr dette skiltet?",
            "th": "ป้ายนี้หมายถึงอะไร?",
            "en": "What does this sign mean?",
        },
        "options": [
            {"id": "A", "text": {"no": "Busstopp", "th": "ป้ายรถเมล์", "en": "Bus stop"}},
            {"id": "B", "text": {"no": "Holdeplass for sporvogn", "th": "ป้ายหยุดรถราง", "en": "Tram stop"}},
            {"id": "C", "text": {"no": "Togstasjon", "th": "สถานีรถไฟ", "en": "Train station"}},
            {"id": "D", "text": {"no": "Taxi holdeplass", "th": "จุดจอดแท็กซี่", "en": "Taxi stand"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Skiltet viser holdeplass for sporvogn (trikk).",
            "th": "ป้ายนี้คือป้ายหยุดรถราง",
            "en": "The sign indicates a tram stop.",
        },
        "bildeUrl": None, "category": "Traffic Signs", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva er riktig om dette skiltet?",
            "th": "ข้อใดถูกต้องเกี่ยวกับป้ายนี้?",
            "en": "What is correct about this sign?",
        },
        "options": [
            {"id": "A", "text": {"no": "Du kan parkere her", "th": "จอดรถได้ที่นี่", "en": "You can park here"}},
            {"id": "B", "text": {"no": "Du må stoppe for trikk", "th": "ต้องหยุดให้รถราง", "en": "You must stop for tram"}},
            {"id": "C", "text": {"no": "Dette er holdeplass for sporvogn", "th": "นี่คือจุดจอดรถราง", "en": "This is a tram stop"}},
            {"id": "D", "text": {"no": "Kun busser kan stoppe her", "th": "เฉพาะรถเมล์เท่านั้น", "en": "Only buses can stop here"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Skiltet markerer en holdeplass for sporvogn.",
            "th": "ป้ายนี้แสดงจุดจอดรถราง",
            "en": "The sign marks a tram stop.",
        },
        "bildeUrl": None, "category": "Traffic Signs", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Oppgaven handler om biler som bruker fossilt drivstoff. Hva er riktig?",
            "th": "คำถามนี้เกี่ยวกับรถที่ใช้เชื้อเพลิงฟอสซิล ข้อใดถูกต้อง?",
            "en": "The question is about cars using fossil fuel. What is correct?",
        },
        "options": [
            {"id": "A", "text": {"no": "Fossile biler forurenser ikke", "th": "รถน้ำมันไม่ก่อมลพิษ", "en": "Fossil cars don't pollute"}},
            {"id": "B", "text": {"no": "Fossile biler slipper ut CO₂", "th": "รถน้ำมันปล่อย CO₂", "en": "Fossil cars emit CO₂"}},
            {"id": "C", "text": {"no": "Elbiler slipper ut mest CO₂", "th": "รถไฟฟ้าปล่อย CO₂ มากที่สุด", "en": "Electric cars emit the most CO₂"}},
            {"id": "D", "text": {"no": "Alle biler er like miljøvennlige", "th": "รถทุกคันเป็นมิตรกับสิ่งแวดล้อมเท่ากัน", "en": "All cars are equally eco-friendly"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Biler med fossilt drivstoff slipper ut CO₂ og bidrar til forurensning.",
            "th": "รถที่ใช้น้ำมันปล่อยก๊าซ CO2 และก่อมลพิษ",
            "en": "Cars with fossil fuel emit CO₂ and contribute to pollution.",
        },
        "bildeUrl": None, "category": "Safety", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva viser dette skiltet?",
            "th": "ป้ายนี้แสดงอะไร?",
            "en": "What does this sign show?",
        },
        "options": [
            {"id": "A", "text": {"no": "Avkjøring", "th": "ทางออก", "en": "Exit"}},
            {"id": "B", "text": {"no": "Serviceområde", "th": "พื้นที่บริการ", "en": "Service area"}},
            {"id": "C", "text": {"no": "Informasjon om sted med tjenester", "th": "ข้อมูลสถานที่ที่มีบริการ", "en": "Information about a place with services"}},
            {"id": "D", "text": {"no": "Parkering", "th": "ที่จอดรถ", "en": "Parking"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Skiltet viser at det finnes tjenester (mat, drivstoff, info) i området.",
            "th": "ป้ายนี้แสดงว่ามีบริการต่าง ๆ ในพื้นที่",
            "en": "The sign shows that services (food, fuel, info) are available in the area.",
        },
        "bildeUrl": None, "category": "Traffic Signs", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva betyr dette merket på kjøretøyet?",
            "th": "เครื่องหมายนี้บนรถหมายถึงอะไร?",
            "en": "What does this marking on the vehicle mean?",
        },
        "options": [
            {"id": "A", "text": {"no": "Ny bil", "th": "รถใหม่", "en": "New car"}},
            {"id": "B", "text": {"no": "Lastebil", "th": "รถบรรทุก", "en": "Truck"}},
            {"id": "C", "text": {"no": "Farlig last", "th": "บรรทุกวัตถุอันตราย", "en": "Dangerous cargo"}},
            {"id": "D", "text": {"no": "Elektrisk bil", "th": "รถไฟฟ้า", "en": "Electric car"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Oransje skilt viser at kjøretøyet frakter farlig gods.",
            "th": "ป้ายสีส้มหมายถึงรถขนส่งวัตถุอันตราย",
            "en": "Orange sign indicates the vehicle is carrying dangerous goods.",
        },
        "bildeUrl": None, "category": "Safety", "difficulty": "medium", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva er riktig om privat øvelseskjøring?",
            "th": "ข้อใดถูกต้องเกี่ยวกับการฝึกขับรถส่วนตัว?",
            "en": "What is correct about private practice driving?",
        },
        "options": [
            {"id": "A", "text": {"no": "Du kan kjøre alene", "th": "ขับคนเดียวได้", "en": "You can drive alone"}},
            {"id": "B", "text": {"no": "Du må ha ledsager over 25 år", "th": "ต้องมีผู้ควบคุมอายุเกิน 25 ปี", "en": "You must have a supervisor over 25"}},
            {"id": "C", "text": {"no": "Ledsager må ha hatt førerkort i minst 5 år", "th": "ผู้ควบคุมต้องมีใบขับขี่อย่างน้อย 5 ปี", "en": "Supervisor must have held a license for at least 5 years"}},
            {"id": "D", "text": {"no": "Du trenger ikke L-merke", "th": "ไม่ต้องติดป้าย L", "en": "You don't need an L-sign"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Ledsager må være over 25 år og hatt førerkort i minst 5 år.",
            "th": "ผู้ควบคุมต้องอายุเกิน 25 ปี และมีใบขับขี่อย่างน้อย 5 ปี",
            "en": "The supervisor must be over 25 and have held a license for at least 5 years.",
        },
        "bildeUrl": None, "category": "Road Rules", "difficulty": "medium", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva er riktig å anta etter dette skiltet?",
            "th": "ข้อใดถูกต้องหลังจากเห็นป้ายนี้?",
            "en": "What is correct to assume after this sign?",
        },
        "options": [
            {"id": "A", "text": {"no": "Du har vikeplikt", "th": "คุณต้องให้ทาง", "en": "You must yield"}},
            {"id": "B", "text": {"no": "Du kjører på forkjørsvei", "th": "คุณขับบนถนนหลัก", "en": "You are on a priority road"}},
            {"id": "C", "text": {"no": "Veien slutter", "th": "ถนนสิ้นสุด", "en": "Road ends"}},
            {"id": "D", "text": {"no": "Du må stoppe", "th": "ต้องหยุด", "en": "You must stop"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Skiltet viser forkjørsvei.",
            "th": "ป้ายนี้หมายถึงถนนที่มีสิทธิ์ไปก่อน",
            "en": "The sign indicates a priority road.",
        },
        "bildeUrl": None, "category": "Right of Way", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva betyr det når kantlinjen er stiplet?",
            "th": "เส้นประข้างทางหมายถึงอะไร?",
            "en": "What does a dashed edge line mean?",
        },
        "options": [
            {"id": "A", "text": {"no": "Du må ikke krysse linjen", "th": "ห้ามข้ามเส้น", "en": "You must not cross the line"}},
            {"id": "B", "text": {"no": "Du kan stoppe der", "th": "จอดได้ตรงนั้น", "en": "You can stop there"}},
            {"id": "C", "text": {"no": "Du kan krysse linjen ved behov", "th": "ข้ามเส้นได้เมื่อจำเป็น", "en": "You can cross the line when needed"}},
            {"id": "D", "text": {"no": "Det er enveiskjøring", "th": "เป็นทางเดินรถทางเดียว", "en": "It's a one-way road"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Stiplet kantlinje kan krysses ved behov (f.eks. stopp/parkering).",
            "th": "เส้นประข้างทางสามารถข้ามได้เมื่อจำเป็น",
            "en": "A dashed edge line can be crossed when necessary (e.g. stopping/parking).",
        },
        "bildeUrl": None, "category": "Road Rules", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva varsler dette skiltet?",
            "th": "ป้ายนี้เตือนอะไร?",
            "en": "What does this sign warn about?",
        },
        "options": [
            {"id": "A", "text": {"no": "Glatt vei", "th": "ถนนลื่น", "en": "Slippery road"}},
            {"id": "B", "text": {"no": "Svingete vei", "th": "ถนนคดเคี้ยว", "en": "Winding road"}},
            {"id": "C", "text": {"no": "Glatt kjørebane", "th": "ผิวถนนลื่น", "en": "Slippery road surface"}},
            {"id": "D", "text": {"no": "Farlig sving", "th": "โค้งอันตราย", "en": "Dangerous curve"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Skiltet varsler glatt kjørebane.",
            "th": "ป้ายเตือนถนนลื่น",
            "en": "The sign warns about a slippery road surface.",
        },
        "bildeUrl": None, "category": "Safety", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0
    for q in NEW_QUESTIONS:
        existing = await db.questions.find_one({"question.no": q["question"]["no"]})
        if existing:
            skipped += 1
            continue
        await db.questions.insert_one(q)
        inserted += 1
    print(f"Done! Inserted: {inserted}, Skipped (duplicates): {skipped}")
    total = await db.questions.count_documents({})
    print(f"Total questions in database: {total}")
    client.close()

asyncio.run(seed())
