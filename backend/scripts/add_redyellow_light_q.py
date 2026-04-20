"""
Add the 'red+yellow traffic light, go straight' Traffic Rules question provided by the user.
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

bilde = image_to_base64("/tmp/signs/light_redyellow.jpg", max_dim=600, quality=80)
print(f"Image size (b64): {len(bilde)} chars")

question = {
    "id": str(uuid.uuid4()),
    "question": {
        "no": "Du skal kjøre rett fram. Hva gjør du i denne situasjonen?",
        "en": "You are going straight ahead. What do you do in this situation?",
        "th": "คุณกำลังจะขับตรงไป คุณจะทำอย่างไรในสถานการณ์นี้?",
    },
    "options": [
        {"id": "A", "text": {
            "no": "Kjører rett fram hvis det ikke er trafikk",
            "en": "Drive straight if there is no traffic",
            "th": "ขับตรงไปหากไม่มีรถ",
        }},
        {"id": "B", "text": {
            "no": "Stopper før stopplinjen",
            "en": "Stop before the stop line",
            "th": "หยุดก่อนเส้นหยุด",
        }},
        {"id": "C", "text": {
            "no": "Kjører forsiktig gjennom krysset",
            "en": "Drive carefully through the intersection",
            "th": "ขับอย่างระมัดระวังผ่านทางแยก",
        }},
        {"id": "D", "text": {
            "no": "Kjører hvis det ikke er fotgjengere",
            "en": "Drive if there are no pedestrians",
            "th": "ขับได้ถ้าไม่มีคนเดินเท้า",
        }},
    ],
    "correctOptionId": "B",
    "explanation": {
        "no": (
            "Trafikklyset viser rødt (og gult samtidig), som betyr at du skal stå stille og "
            "gjøre deg klar til å kjøre når det blir grønt. Du må stoppe før stopplinjen "
            "uansett om du skal rett fram. Du har ikke lov til å kjøre før lyset er grønt."
        ),
        "en": (
            "The traffic light is showing red (with yellow simultaneously), meaning you must "
            "remain stopped and prepare to drive when the light turns green. You must stop "
            "before the stop line regardless of whether you are going straight. You are not "
            "allowed to drive until the light turns green."
        ),
        "th": (
            "สัญญาณไฟจราจรแสดงสีแดง (พร้อมสีเหลืองในเวลาเดียวกัน) ซึ่งหมายความว่าคุณต้อง "
            "หยุดและเตรียมตัวขับเมื่อไฟเปลี่ยนเป็นสีเขียว คุณต้องหยุดก่อนเส้นหยุด "
            "แม้ว่าคุณจะขับตรงไปก็ตาม ห้ามขับจนกว่าไฟจะเป็นสีเขียว"
        ),
    },
    "bildeUrl": bilde,
    "category": "Traffic Rules",
    "difficulty": "easy",
    "active": True,
    "schema_version": 2,
    "created_at": datetime.now(timezone.utc),
    "audit_verdict": "MATCH",
    "audit_image_identification": "Bygate med trafikklys som viser rødt+gult samtidig, fotgjengerfelt og sone 30",
}

db.questions.insert_one(question)
print(f"Inserted id: {question['id']}")
print(f"Total questions: {db.questions.count_documents({})}")
print(f"Questions with base64 image: {db.questions.count_documents({'bildeUrl': {'$regex': '^data:'}})}")
