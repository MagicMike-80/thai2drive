"""
Add 'Left turn positioning' Traffic Rules question with image.
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

bilde = image_to_base64("/tmp/signs/left_turn_position.jpg", max_dim=600, quality=80)
print(f"Image size (b64): {len(bilde)} chars")

question = {
    "id": str(uuid.uuid4()),
    "question": {
        "no": "Du skal til venstre i dette krysset. Hvordan bør du plassere deg?",
        "en": "You are going to turn left at this intersection. How should you position your vehicle?",
        "th": "คุณจะเลี้ยวซ้ายที่ทางแยกนี้ คุณควรจัดตำแหน่งรถอย่างไร?",
    },
    "options": [
        {"id": "A", "text": {
            "no": "Holde til høyre i kjørefeltet",
            "en": "Stay on the right side of the lane",
            "th": "อยู่ด้านขวาของช่องทาง",
        }},
        {"id": "B", "text": {
            "no": "Plassere deg nær midten av veien",
            "en": "Position yourself close to the center of the road",
            "th": "ขับชิดกลางถนน",
        }},
        {"id": "C", "text": {
            "no": "Stoppe midt i veien",
            "en": "Stop in the middle of the road",
            "th": "หยุดกลางถนน",
        }},
        {"id": "D", "text": {
            "no": "Legge deg i motsatt kjørefelt",
            "en": "Move into the opposite lane",
            "th": "เข้าไปในช่องทางฝั่งตรงข้าม",
        }},
    ],
    "correctOptionId": "B",
    "explanation": {
        "no": (
            "Når du skal svinge til venstre, skal du plassere deg nær midten av veien i ditt "
            "kjørefelt. Dette gjør det tydelig for andre trafikanter hva du har tenkt å gjøre "
            "og gir plass til høyresvingende og andre som skal rett frem."
        ),
        "en": (
            "When turning left, you should position your vehicle close to the center of the "
            "road within your own lane. This clearly communicates your intention to other "
            "road users and leaves room for right-turning and straight-ahead traffic."
        ),
        "th": (
            "เมื่อคุณจะเลี้ยวซ้าย คุณควรขับรถชิดกลางถนนในช่องทางของคุณ เพื่อให้ผู้ใช้ถนน "
            "คนอื่นเข้าใจเจตนาของคุณอย่างชัดเจน และเปิดพื้นที่ให้รถที่จะเลี้ยวขวาและขับตรงไป"
        ),
    },
    "bildeUrl": bilde,
    "category": "Traffic Rules",
    "difficulty": "easy",
    "active": True,
    "schema_version": 2,
    "created_at": datetime.now(timezone.utc),
}

db.questions.insert_one(question)
print(f"Inserted id: {question['id']}")
print(f"Total questions: {db.questions.count_documents({})}")
print(f"Questions with base64 image: {db.questions.count_documents({'bildeUrl': {'$regex': '^data:'}})}")
