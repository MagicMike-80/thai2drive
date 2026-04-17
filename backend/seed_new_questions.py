"""Seed 3 questions using the NEW nested schema."""
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
            "no": "Du har stanset for å slippe syklisten over. Hva må du være oppmerksom på?",
            "th": "คุณจอดรถให้จักรยานข้ามแล้ว สิ่งที่ต้องระวังคืออะไร?",
            "en": "You have stopped to let the cyclist cross. What must you be aware of?",
        },
        "options": [
            {
                "id": "A",
                "text": {
                    "no": "Jeg må være oppmerksom på at trafikken imot også stanser for syklistene",
                    "th": "ต้องระวังว่ารถสวนทางก็หยุดให้จักรยานด้วย",
                    "en": "I must be aware that oncoming traffic also stops for the cyclists",
                },
            },
            {
                "id": "B",
                "text": {
                    "no": "Jeg må vente til syklisten har kommet helt over gaten",
                    "th": "ต้องรอจนกว่าจักรยานจะข้ามไปหมด",
                    "en": "I must wait until the cyclist has completely crossed the street",
                },
            },
            {
                "id": "C",
                "text": {
                    "no": "Jeg må sjekke om det er trafikk bak meg",
                    "th": "ต้องตรวจสอบว่ามีรถข้างหลังหรือไม่",
                    "en": "I must check if there is traffic behind me",
                },
            },
            {
                "id": "D",
                "text": {
                    "no": "Jeg må se til begge sider om det kommer flere inn mot gangfeltet før jeg kjører",
                    "th": "ต้องมองทั้งสองด้านว่ามีคนจะเข้าทางม้าลายอีกหรือไม่ก่อนขับ",
                    "en": "I must look both ways to see if more are entering the crossing before driving",
                },
            },
        ],
        "correctOptionId": "D",
        "explanation": {
            "no": "Du må alltid forsikre deg om at ingen flere syklister eller fotgjengere er på vei inn i gangfeltet før du kjører videre.",
            "th": "คุณต้องดูให้แน่ใจว่าไม่มีจักรยานหรือคนเดินถนนคนอื่นกำลังจะข้ามก่อนที่จะขับต่อ",
            "en": "You must always make sure no more cyclists or pedestrians are entering the crossing before driving on.",
        },
        "bildeUrl": None,
        "category": "Right of Way",
        "difficulty": "easy",
        "active": True,
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva er riktig?",
            "th": "ข้อใดถูกต้อง?",
            "en": "What is correct?",
        },
        "options": [
            {
                "id": "A",
                "text": {
                    "no": "Det er 23 km til Drøbak",
                    "th": "ระยะทางไป Drøbak 23 กม.",
                    "en": "It is 23 km to Drøbak",
                },
            },
            {
                "id": "B",
                "text": {
                    "no": "Det er 285 km til Lierbyen",
                    "th": "ระยะทางไป Lierbyen 285 กม.",
                    "en": "It is 285 km to Lierbyen",
                },
            },
            {
                "id": "C",
                "text": {
                    "no": "Det er 500 meter til Kjellstad",
                    "th": "ระยะทางไป Kjellstad 500 เมตร",
                    "en": "It is 500 meters to Kjellstad",
                },
            },
            {
                "id": "D",
                "text": {
                    "no": "Fylkesvei 285 går til Lierbyen",
                    "th": "ถนนหมายเลข 285 ไปยัง Lierbyen",
                    "en": "County road 285 goes to Lierbyen",
                },
            },
        ],
        "correctOptionId": "D",
        "explanation": {
            "no": "Tallet 285 viser fylkesvei-nummer, ikke avstand. Skiltet viser hvilken vei som fører til Lierbyen.",
            "th": "เลข 285 คือหมายเลขถนน ไม่ใช่ระยะทาง ป้ายบอกเส้นทางไป Lierbyen",
            "en": "The number 285 shows the county road number, not distance. The sign shows which road leads to Lierbyen.",
        },
        "bildeUrl": None,
        "category": "Traffic Signs",
        "difficulty": "medium",
        "active": True,
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Du kjører i 70 km/t og ligger 35 meter bak bilen foran. Er dette sikker avstand?",
            "th": "คุณขับ 70 กม./ชม. อยู่ห่างรถคันหน้า 35 เมตร ระยะนี้ปลอดภัยหรือไม่?",
            "en": "You are driving at 70 km/h and are 35 meters behind the car ahead. Is this a safe distance?",
        },
        "options": [
            {
                "id": "A",
                "text": {
                    "no": "Ja, men sikten forover blir redusert",
                    "th": "ใช่ แต่ทัศนวิสัยจะลดลง",
                    "en": "Yes, but forward visibility is reduced",
                },
            },
            {
                "id": "B",
                "text": {
                    "no": "Nei, sikker avstand i denne hastigheten er cirka 60 meter",
                    "th": "ไม่ ระยะปลอดภัยที่ความเร็วนี้ประมาณ 60 เมตร",
                    "en": "No, safe distance at this speed is about 60 meters",
                },
            },
            {
                "id": "C",
                "text": {
                    "no": "Ja, fordi bremselengden på tørt føre i 70 km/t blir cirka 24 meter",
                    "th": "ใช่ เพราะระยะเบรกบนถนนแห้งที่ 70 กม./ชม. ประมาณ 24 เมตร",
                    "en": "Yes, because braking distance on dry road at 70 km/h is about 24 meters",
                },
            },
            {
                "id": "D",
                "text": {
                    "no": "Nei, i 70 km/t bør du ha minst 100 meters avstand",
                    "th": "ไม่ ที่ 70 กม./ชม. ควรห่างอย่างน้อย 100 เมตร",
                    "en": "No, at 70 km/h you should have at least 100 meters distance",
                },
            },
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Ved 70 km/t bør du ha ca. 60 meter avstand for å ha god reaksjonstid og stopplengde.",
            "th": "ที่ความเร็ว 70 กม./ชม. ควรมีระยะห่างประมาณ 60 เมตรเพื่อความปลอดภัย",
            "en": "At 70 km/h you should have about 60 meters distance for good reaction time and stopping distance.",
        },
        "bildeUrl": None,
        "category": "Safety",
        "difficulty": "medium",
        "active": True,
        "schema_version": 2,
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
