"""
Add the 'accident scene' Safety question provided by the user, with image.
"""
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(Path(__file__).parent))
from _img_utils import image_to_base64  # noqa: E402

client = MongoClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME")]

bilde = image_to_base64("/tmp/signs/accident.jpg", max_dim=600, quality=80)
print(f"Image size (b64): {len(bilde)} chars")

question = {
    "id": str(uuid.uuid4()),
    "question": {
        "no": "Du kommer til et ulykkessted, men ser at det er andre til stede og kjører derfor videre uten å stanse. Kan du straffes for dette?",
        "en": "You arrive at an accident scene but see that others are present and continue driving without stopping. Can you be penalized for this?",
        "th": "คุณมาถึงที่เกิดอุบัติเหตุ แต่เห็นว่ามีคนอื่นอยู่แล้วและขับต่อไปโดยไม่หยุด คุณสามารถถูกลงโทษได้หรือไม่?",
    },
    "options": [
        {"id": "A", "text": {
            "no": "Nei, fordi andre allerede er til stede",
            "en": "No, because others are already there",
            "th": "ไม่ เพราะมีคนอื่นอยู่แล้ว",
        }},
        {"id": "B", "text": {
            "no": "Ja, du har plikt til å stanse og hjelpe",
            "en": "Yes, you have a duty to stop and assist",
            "th": "ใช่ คุณมีหน้าที่ต้องหยุดและช่วยเหลือ",
        }},
        {"id": "C", "text": {
            "no": "Nei, hvis du har dårlig tid",
            "en": "No, if you are in a hurry",
            "th": "ไม่ หากคุณรีบ",
        }},
        {"id": "D", "text": {
            "no": "Ja, men bare hvis politiet er til stede",
            "en": "Yes, but only if the police are present",
            "th": "ใช่ แต่เฉพาะเมื่อมีตำรวจอยู่",
        }},
    ],
    "correctOptionId": "B",
    "explanation": {
        "no": (
            "Etter vegtrafikkloven § 12 har alle trafikanter plikt til å stanse og hjelpe "
            "ved trafikkulykker, uavhengig av om andre allerede er til stede. Å kjøre videre "
            "uten å yte den hjelp man kan, er straffbart."
        ),
        "en": (
            "According to the Norwegian Road Traffic Act § 12, all road users have a legal "
            "duty to stop and assist at traffic accidents, regardless of whether others are "
            "already present. Driving past without offering the help you can provide is a "
            "punishable offense."
        ),
        "th": (
            "ตามพระราชบัญญัติจราจรทางบกของนอร์เวย์มาตรา 12 ผู้ใช้ถนนทุกคนมีหน้าที่ตามกฎหมาย "
            "ที่จะต้องหยุดและช่วยเหลือในที่เกิดอุบัติเหตุจราจร ไม่ว่าจะมีคนอื่นอยู่แล้วหรือไม่ "
            "การขับผ่านไปโดยไม่ให้ความช่วยเหลือที่สามารถทำได้ถือเป็นความผิดที่มีโทษ"
        ),
    },
    "bildeUrl": bilde,
    "category": "Safety",
    "difficulty": "medium",
    "active": True,
    "schema_version": 2,
    "created_at": datetime.now(timezone.utc),
    "audit_verdict": "MATCH",
    "audit_image_identification": "Ulykkessted på vei (folk og krasjet bil ved autovern)",
}

result = db.questions.insert_one(question)
print(f"Inserted id: {question['id']}")
print(f"Total questions: {db.questions.count_documents({})}")
print(f"Questions with base64 image: {db.questions.count_documents({'bildeUrl': {'$regex': '^data:'}})}")
