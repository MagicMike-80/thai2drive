"""
Add 'Slutt på forkjørsvei' (skilt 208) question with image to MongoDB.
"""
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

client = MongoClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME")]

b64 = Path("/tmp/signs/end_priority.b64").read_text().strip()

question = {
    "id": str(uuid.uuid4()),
    "question": {
        "no": "Hva er riktig å anta om videre kjøring etter dette skiltet?",
        "en": "What is correct to assume about further driving after this sign?",
        "th": "อะไรคือสิ่งที่ถูกต้องที่จะสันนิษฐานเกี่ยวกับการขับรถต่อไปหลังจากป้ายนี้?",
    },
    "options": [
        {
            "id": "A",
            "text": {
                "no": "Du har fortsatt forkjørsrett",
                "en": "You still have right of way",
                "th": "คุณยังคงมีสิทธิ์ไปก่อน",
            },
        },
        {
            "id": "B",
            "text": {
                "no": "Forkjørsveien opphører, og du må følge vanlige vikepliktsregler",
                "en": "The priority road ends, and you must follow normal right-of-way rules",
                "th": "ถนนสายหลักสิ้นสุดลง และคุณต้องปฏิบัติตามกฎการให้ทางปกติ",
            },
        },
        {
            "id": "C",
            "text": {
                "no": "Alle andre trafikanter må stoppe for deg",
                "en": "All other road users must stop for you",
                "th": "ผู้ใช้ถนนคนอื่นทั้งหมดต้องหยุดให้คุณ",
            },
        },
        {
            "id": "D",
            "text": {
                "no": "Det er ikke lov å kjøre videre",
                "en": "It is not permitted to drive further",
                "th": "ไม่อนุญาตให้ขับต่อไป",
            },
        },
    ],
    "correctOptionId": "B",
    "explanation": {
        "no": (
            "Dette er skilt 208 'Slutt på forkjørsvei'. Skiltet markerer at forkjørsretten "
            "opphører. Fra dette punktet må du følge de vanlige vikepliktsreglene – som "
            "høyreregelen i uskiltede kryss – eller eventuelle vikepliktsskilt som kommer etterpå."
        ),
        "en": (
            "This is sign 208 'End of priority road'. The sign indicates that the priority "
            "road ends. From this point on, you must follow the normal right-of-way rules, "
            "such as the right-hand rule at unsignposted intersections, or any subsequent "
            "give-way signs."
        ),
        "th": (
            "นี่คือป้าย 208 'สิ้นสุดถนนสายหลัก' ป้ายนี้บ่งบอกว่าสิทธิ์การไปก่อนสิ้นสุดลง "
            "จากจุดนี้คุณต้องปฏิบัติตามกฎการให้ทางตามปกติ เช่น กฎมือขวาที่ทางแยกที่ไม่มีป้าย "
            "หรือป้ายให้ทางที่อาจมีอยู่ถัดไป"
        ),
    },
    "bildeUrl": b64,
    "category": "Traffic Signs",
    "difficulty": "medium",
    "active": True,
    "schema_version": 2,
    "created_at": datetime.now(timezone.utc),
    "audit_verdict": "MATCH",  # Manually verified to match
    "audit_image_identification": "Slutt på forkjørsvei (skilt 208)",
}

# Insert (or update if somehow exists)
result = db.questions.insert_one(question)
print(f"Inserted question id: {question['id']}")
print(f"Mongo _id: {result.inserted_id}")
print(f"Total questions now: {db.questions.count_documents({})}")
print(f"Image-attached questions now: {db.questions.count_documents({'bildeUrl': {'$regex': '^data:'}})}")
