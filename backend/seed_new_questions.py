"""Seed 10 new exam-style questions into MongoDB (v2 schema)."""
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
            "no": "Hva betyr gult blinkende lys i et trafikklys?",
            "th": "ไฟเหลืองกระพริบในสัญญาณไฟจราจรหมายถึงอะไร?",
            "en": "What does a flashing yellow light in a traffic light mean?",
        },
        "options": [
            {"id": "A", "text": {"no": "Stopp", "th": "หยุด", "en": "Stop"}},
            {"id": "B", "text": {"no": "Kjør", "th": "ขับต่อ", "en": "Drive"}},
            {"id": "C", "text": {"no": "Vær spesielt oppmerksom og kjør forsiktig", "th": "ระวังเป็นพิเศษและขับอย่างระมัดระวัง", "en": "Be extra careful and drive cautiously"}},
            {"id": "D", "text": {"no": "Du har forkjørsrett", "th": "คุณมีสิทธิ์ไปก่อน", "en": "You have right of way"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Gult blinkende lys betyr at du skal være ekstra oppmerksom og følge skilting og vikeplikt.",
            "th": "ไฟเหลืองกระพริบหมายถึงให้ระวังเป็นพิเศษและปฏิบัติตามป้ายจราจร",
            "en": "Flashing yellow means be extra careful and follow signs and right of way rules.",
        },
        "bildeUrl": None, "category": "Road Rules", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hvem har vikeplikt i et kryss uten skilt?",
            "th": "ใครต้องให้ทางที่สี่แยกที่ไม่มีป้าย?",
            "en": "Who must yield at an intersection without signs?",
        },
        "options": [
            {"id": "A", "text": {"no": "Den som kommer fra høyre", "th": "คนที่มาจากขวา", "en": "The one coming from the right"}},
            {"id": "B", "text": {"no": "Den som kjører rett frem", "th": "คนที่ขับตรง", "en": "The one driving straight"}},
            {"id": "C", "text": {"no": "Den som er først i krysset", "th": "คนที่ถึงสี่แยกก่อน", "en": "The one who arrives first"}},
            {"id": "D", "text": {"no": "Den som kjører fortest", "th": "คนที่ขับเร็วที่สุด", "en": "The one driving fastest"}},
        ],
        "correctOptionId": "A",
        "explanation": {
            "no": "Høyre-regelen gjelder når det ikke er skilt eller lys.",
            "th": "หากไม่มีป้ายหรือไฟจราจร ให้ใช้กฎให้ทางขวา",
            "en": "The right-hand rule applies when there are no signs or lights.",
        },
        "bildeUrl": None, "category": "Right of Way", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva betyr dette skiltet? (Forkjørsvei)",
            "th": "ป้ายนี้หมายถึงอะไร? (ทางหลัก)",
            "en": "What does this sign mean? (Priority road)",
        },
        "options": [
            {"id": "A", "text": {"no": "Du må stoppe", "th": "ต้องหยุด", "en": "You must stop"}},
            {"id": "B", "text": {"no": "Du har forkjørsrett", "th": "คุณมีสิทธิ์ไปก่อน", "en": "You have right of way"}},
            {"id": "C", "text": {"no": "Veien er stengt", "th": "ถนนปิด", "en": "Road is closed"}},
            {"id": "D", "text": {"no": "Parkering er forbudt", "th": "ห้ามจอดรถ", "en": "Parking is forbidden"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Skiltet betyr at du har forkjørsrett i forhold til kryssende trafikk.",
            "th": "ป้ายนี้หมายถึงคุณมีสิทธิ์ไปก่อนในทางแยก",
            "en": "The sign means you have priority over crossing traffic.",
        },
        "bildeUrl": None, "category": "Traffic Signs", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hvor langt er 3 sekunders avstand i 80 km/t?",
            "th": "ระยะ 3 วินาทีที่ความเร็ว 80 กม./ชม. คือเท่าไหร่?",
            "en": "How far is a 3-second distance at 80 km/h?",
        },
        "options": [
            {"id": "A", "text": {"no": "44 meter", "th": "44 เมตร", "en": "44 meters"}},
            {"id": "B", "text": {"no": "66 meter", "th": "66 เมตร", "en": "66 meters"}},
            {"id": "C", "text": {"no": "88 meter", "th": "88 เมตร", "en": "88 meters"}},
            {"id": "D", "text": {"no": "22 meter", "th": "22 เมตร", "en": "22 meters"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "80 km/t ≈ 22 m/s → 3 sekunder = ca. 66 meter.",
            "th": "ความเร็ว 80 กม./ชม. ประมาณ 22 เมตร/วินาที → 3 วินาที ≈ 66 เมตร",
            "en": "80 km/h ≈ 22 m/s → 3 seconds = approx. 66 meters.",
        },
        "bildeUrl": None, "category": "Safety", "difficulty": "medium", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hvem må vente når det er hindring i veien?",
            "th": "ใครต้องรอเมื่อมีสิ่งกีดขวางบนถนน?",
            "en": "Who must wait when there is an obstacle on the road?",
        },
        "options": [
            {"id": "A", "text": {"no": "Den som har størst bil", "th": "คนที่มีรถใหญ่กว่า", "en": "The one with the largest car"}},
            {"id": "B", "text": {"no": "Den som har hindringen på sin side", "th": "ฝั่งที่มีสิ่งกีดขวาง", "en": "The one with the obstacle on their side"}},
            {"id": "C", "text": {"no": "Den som kjører fortest", "th": "คนที่ขับเร็วที่สุด", "en": "The one driving fastest"}},
            {"id": "D", "text": {"no": "Begge må alltid stoppe", "th": "ทั้งสองต้องหยุดเสมอ", "en": "Both must always stop"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Den som har hindringen på sin side må vike.",
            "th": "ฝั่งที่มีสิ่งกีดขวางต้องเป็นฝ่ายให้ทาง",
            "en": "The one with the obstacle on their side must yield.",
        },
        "bildeUrl": None, "category": "Right of Way", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva betyr rødt lys?",
            "th": "ไฟแดงหมายถึงอะไร?",
            "en": "What does a red light mean?",
        },
        "options": [
            {"id": "A", "text": {"no": "Kjør forsiktig", "th": "ขับระวัง", "en": "Drive carefully"}},
            {"id": "B", "text": {"no": "Stopp", "th": "หยุด", "en": "Stop"}},
            {"id": "C", "text": {"no": "Du kan kjøre hvis det er klart", "th": "ขับได้ถ้าปลอดภัย", "en": "You can drive if clear"}},
            {"id": "D", "text": {"no": "Vent bare hvis andre kommer", "th": "รอเฉพาะเมื่อมีรถอื่น", "en": "Wait only if others come"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Rødt lys betyr full stopp før stopplinje.",
            "th": "ไฟแดงหมายถึงต้องหยุดรถ",
            "en": "Red light means full stop before the stop line.",
        },
        "bildeUrl": None, "category": "Road Rules", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hvem bestemmer når trafikklys og politi gir motstridende signaler?",
            "th": "ใครมีอำนาจสูงสุดเมื่อสัญญาณไฟจราจรและตำรวจขัดแย้งกัน?",
            "en": "Who has authority when traffic lights and police give conflicting signals?",
        },
        "options": [
            {"id": "A", "text": {"no": "Trafikklyset", "th": "ไฟจราจร", "en": "The traffic light"}},
            {"id": "B", "text": {"no": "Skiltet", "th": "ป้ายจราจร", "en": "The sign"}},
            {"id": "C", "text": {"no": "Politiet", "th": "ตำรวจ", "en": "The police"}},
            {"id": "D", "text": {"no": "Sjåføren selv", "th": "คนขับเอง", "en": "The driver"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Politiets signaler gjelder over trafikklys og skilt.",
            "th": "สัญญาณของตำรวจมีความสำคัญสูงสุด",
            "en": "Police signals override traffic lights and signs.",
        },
        "bildeUrl": None, "category": "Road Rules", "difficulty": "medium", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva betyr dette skiltet? (Parkering forbudt)",
            "th": "ป้ายนี้หมายถึงอะไร? (ห้ามจอดรถ)",
            "en": "What does this sign mean? (No parking)",
        },
        "options": [
            {"id": "A", "text": {"no": "Parkering tillatt", "th": "จอดรถได้", "en": "Parking allowed"}},
            {"id": "B", "text": {"no": "Parkering forbudt", "th": "ห้ามจอดรถ", "en": "No parking"}},
            {"id": "C", "text": {"no": "Stans forbudt", "th": "ห้ามหยุดรถ", "en": "No stopping"}},
            {"id": "D", "text": {"no": "Kun for beboere", "th": "สำหรับผู้อยู่อาศัยเท่านั้น", "en": "Residents only"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Skiltet betyr at parkering ikke er tillatt.",
            "th": "ป้ายนี้หมายถึงห้ามจอดรถ",
            "en": "The sign means parking is not allowed.",
        },
        "bildeUrl": None, "category": "Traffic Signs", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Når er det lov å bruke mobiltelefon under kjøring?",
            "th": "เมื่อไหร่ที่ใช้โทรศัพท์ขณะขับรถได้?",
            "en": "When is it allowed to use a mobile phone while driving?",
        },
        "options": [
            {"id": "A", "text": {"no": "Når du kjører sakte", "th": "เมื่อขับช้า", "en": "When driving slowly"}},
            {"id": "B", "text": {"no": "Når du bruker håndholdt", "th": "เมื่อถือโทรศัพท์", "en": "When using handheld"}},
            {"id": "C", "text": {"no": "Når du bruker handsfree", "th": "เมื่อใช้แฮนด์ฟรี", "en": "When using handsfree"}},
            {"id": "D", "text": {"no": "Når det ikke er trafikk", "th": "เมื่อไม่มีรถอื่น", "en": "When there is no traffic"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Du kan kun bruke mobil hvis det er handsfree.",
            "th": "ใช้โทรศัพท์ได้เฉพาะแบบแฮนด์ฟรีเท่านั้น",
            "en": "You may only use a phone if it is handsfree.",
        },
        "bildeUrl": None, "category": "Safety", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva er maksimal fartsgrense i tettbygd strøk hvis ikke annet er skiltet?",
            "th": "ความเร็วสูงสุดในเขตเมืองคือเท่าไหร่ถ้าไม่มีป้ายบอก?",
            "en": "What is the maximum speed limit in built-up areas if not otherwise signed?",
        },
        "options": [
            {"id": "A", "text": {"no": "30 km/t", "th": "30 กม./ชม.", "en": "30 km/h"}},
            {"id": "B", "text": {"no": "40 km/t", "th": "40 กม./ชม.", "en": "40 km/h"}},
            {"id": "C", "text": {"no": "50 km/t", "th": "50 กม./ชม.", "en": "50 km/h"}},
            {"id": "D", "text": {"no": "60 km/t", "th": "60 กม./ชม.", "en": "60 km/h"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Standard fartsgrense i tettbygd strøk er 50 km/t.",
            "th": "ความเร็วสูงสุดในเขตเมืองคือ 50 กม./ชม.",
            "en": "Standard speed limit in built-up areas is 50 km/h.",
        },
        "bildeUrl": None, "category": "Speed Limits", "difficulty": "easy", "active": True, "schema_version": 2,
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
