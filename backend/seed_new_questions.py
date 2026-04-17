"""Seed 5 new questions with images, mapped from user format to v2 schema."""
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
        "q": {"no": "Du ligger i feltet lengst til høyre og ser dette skiltet. Hvem får vikeplikt?", "th": "คุณอยู่เลนขวาสุดและเห็นป้ายนี้ ใครต้องให้ทาง?", "en": "You are in the far right lane and see this sign. Who must yield?"},
        "opts": [
            {"no": "Du må gi vikeplikt", "th": "คุณต้องให้ทาง", "en": "You must yield"},
            {"no": "De i venstre felt må gi vikeplikt", "th": "รถเลนซ้ายต้องให้ทาง", "en": "Vehicles in the left lane must yield"},
            {"no": "Ingen har vikeplikt", "th": "ไม่มีใครต้องให้ทาง", "en": "No one must yield"},
            {"no": "Alle må stoppe", "th": "ทุกคนต้องหยุด", "en": "Everyone must stop"},
        ],
        "correct": "A",
        "expl": {"no": "Feltet ditt opphører, du må vike for trafikk i de andre feltene.", "th": "เลนของคุณสิ้นสุด คุณต้องให้ทาง", "en": "Your lane ends, you must yield to other traffic"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/bj1n262b_Screenshot_20260418_001120.jpg",
        "cat": "Right of Way", "diff": "medium",
    },
    {
        "q": {"no": "Kan du kjøre inn her?", "th": "คุณสามารถขับเข้าไปได้ไหม?", "en": "Can you drive in here?"},
        "opts": [
            {"no": "Ja", "th": "ได้", "en": "Yes"},
            {"no": "Nei", "th": "ไม่ได้", "en": "No"},
            {"no": "Kun hvis det er kort stopp", "th": "ได้ถ้าหยุดสั้นๆ", "en": "Only for a short stop"},
            {"no": "Kun for beboere", "th": "เฉพาะผู้อยู่อาศัย", "en": "Only for residents"},
        ],
        "correct": "B",
        "expl": {"no": "Skiltet 'Innkjøring forbudt' gjelder alle kjøretøy.", "th": "ป้ายห้ามเข้าใช้กับรถทุกคัน", "en": "No entry sign applies to all vehicles"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/t5ff66u0_Screenshot_20260418_001132.jpg",
        "cat": "Traffic Signs", "diff": "easy",
    },
    {
        "q": {"no": "Kan du stanse i busslomme?", "th": "คุณสามารถหยุดในป้ายรถเมล์ได้ไหม?", "en": "Can you stop in a bus stop bay?"},
        "opts": [
            {"no": "Ja, alltid", "th": "ได้เสมอ", "en": "Yes, always"},
            {"no": "Nei", "th": "ไม่ได้", "en": "No"},
            {"no": "Kun for av- og påstigning", "th": "ได้เฉพาะรับส่ง", "en": "Only for pick up/drop off"},
            {"no": "Kun om natten", "th": "ได้เฉพาะกลางคืน", "en": "Only at night"},
        ],
        "correct": "B",
        "expl": {"no": "Busslommer er reservert for buss.", "th": "ป้ายรถเมล์ใช้สำหรับรถบัสเท่านั้น", "en": "Bus bays are reserved for buses"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/mlebzttq_Screenshot_20260418_001143.jpg",
        "cat": "Road Rules", "diff": "easy",
    },
    {
        "q": {"no": "Utenfor tettbygd strøk er fareskilt vanligvis plassert hvor langt før faren?", "th": "นอกเขตเมือง ป้ายเตือนมักอยู่ห่างจากอันตรายเท่าไหร่?", "en": "Outside urban areas, how far before danger are warning signs usually placed?"},
        "opts": [
            {"no": "50 meter", "th": "50 เมตร", "en": "50 meters"},
            {"no": "100 meter", "th": "100 เมตร", "en": "100 meters"},
            {"no": "150–250 meter", "th": "150–250 เมตร", "en": "150–250 meters"},
            {"no": "500 meter", "th": "500 เมตร", "en": "500 meters"},
        ],
        "correct": "C",
        "expl": {"no": "Vanlig plassering er 150–250 meter før faren.", "th": "โดยปกติอยู่ห่าง 150–250 เมตร", "en": "Usually placed 150–250 meters before danger"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/xooyv9pt_Screenshot_20260418_001152.jpg",
        "cat": "Traffic Signs", "diff": "medium",
    },
    {
        "q": {"no": "Hva er minimumskravet til mønsterdybde for sommerdekk?", "th": "ความลึกดอกยางขั้นต่ำของยางฤดูร้อนคือเท่าไหร่?", "en": "What is the minimum tread depth for summer tires?"},
        "opts": [
            {"no": "1,0 mm", "th": "1.0 มม.", "en": "1.0 mm"},
            {"no": "1,6 mm", "th": "1.6 มม.", "en": "1.6 mm"},
            {"no": "3,0 mm", "th": "3.0 มม.", "en": "3.0 mm"},
            {"no": "5,0 mm", "th": "5.0 มม.", "en": "5.0 mm"},
        ],
        "correct": "B",
        "expl": {"no": "Minimum er 1,6 mm for sommerdekk.", "th": "ขั้นต่ำคือ 1.6 มม.", "en": "Minimum is 1.6 mm"},
        "img": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/jvy3e6d4_Screenshot_20260418_001209.jpg",
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
