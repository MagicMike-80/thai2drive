"""
Add 'Bridge with crosswind warning sign (118 Sidevind)' Traffic Signs question with image.
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

bilde = image_to_base64("/tmp/signs/bridge_crosswind.jpg", max_dim=600, quality=80)
print(f"Image size (b64): {len(bilde)} chars")

question = {
    "id": str(uuid.uuid4()),
    "question": {
        "no": "Hva må du være spesielt oppmerksom på når du kjører over denne broen?",
        "en": "What should you be especially aware of when driving over this bridge?",
        "th": "คุณควรระวังอะไรเป็นพิเศษเมื่อขับรถข้ามสะพานนี้?",
    },
    "options": [
        {"id": "A", "text": {
            "no": "Sterk sidevind som kan påvirke kjøretøyet",
            "en": "Strong crosswinds that can affect the vehicle",
            "th": "ลมด้านข้างแรงที่อาจส่งผลต่อรถ",
        }},
        {"id": "B", "text": {
            "no": "At veien er spesielt glatt",
            "en": "That the road is especially slippery",
            "th": "ถนนลื่นเป็นพิเศษ",
        }},
        {"id": "C", "text": {
            "no": "At det er forbikjøringsforbud",
            "en": "That overtaking is prohibited",
            "th": "ห้ามแซง",
        }},
        {"id": "D", "text": {
            "no": "At du må stoppe midt på broen",
            "en": "That you must stop on the bridge",
            "th": "ต้องหยุดบนสะพาน",
        }},
    ],
    "correctOptionId": "A",
    "explanation": {
        "no": (
            "Fareskilt 118 'Sidevind' varsler om fare for sterk sidevind. På broer – og særlig "
            "hengebroer som denne – kan vinden være kraftig og påvirke kjøretøyets stabilitet. "
            "Reduser farten, hold et fastere grep på rattet og vær spesielt oppmerksom hvis du "
            "kjører et lett kjøretøy, en varebil eller har tilhenger."
        ),
        "en": (
            "Warning sign 118 'Crosswind' warns of strong side winds. On bridges – especially "
            "suspension bridges like this – the wind can be powerful and affect vehicle "
            "stability. Reduce speed, grip the steering wheel firmly, and pay extra attention "
            "if you are driving a light vehicle, a van, or towing a trailer."
        ),
        "th": (
            "ป้ายเตือน 118 'ลมด้านข้าง' เตือนว่ามีลมด้านข้างแรง บนสะพาน – โดยเฉพาะสะพานแขวน "
            "เช่นนี้ – ลมอาจแรงและส่งผลต่อความเสถียรของรถ ควรลดความเร็ว จับพวงมาลัยให้แน่น "
            "และระมัดระวังเป็นพิเศษหากคุณขับรถน้ำหนักเบา รถตู้ หรือลากรถพ่วง"
        ),
    },
    "bildeUrl": bilde,
    "category": "Traffic Signs",
    "difficulty": "medium",
    "active": True,
    "schema_version": 2,
    "created_at": datetime.now(timezone.utc),
}

db.questions.insert_one(question)
print(f"Inserted id: {question['id']}")
print(f"Total questions: {db.questions.count_documents({})}")
print(f"Questions with base64 image: {db.questions.count_documents({'bildeUrl': {'$regex': '^data:'}})}")
