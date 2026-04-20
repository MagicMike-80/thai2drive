"""
Insert approved questions #2 (Tunnel SOS), #4 (Slippery road), #5 (Rural road overtake)
into MongoDB with their images. Skips #3 (duplicate).
"""
import json
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

# Load proposed questions
proposals = json.loads((Path(__file__).parent / "proposed_questions.json").read_text())
by_slot = {p["slot"]: p for p in proposals}

# Map slot -> image path
IMAGE_PATH = {
    "#2": "/tmp/signs/tunnel_sos.jpg",
    "#4": "/tmp/signs/slippery.jpg",
    "#5": "/tmp/signs/country_road.jpg",
}

# User-approved modifications
# #5: update question text to include "like før bakketoppen"
by_slot["#5"]["proposal"]["question"] = {
    "no": "Du kjører på denne veien og vurderer en forbikjøring like før bakketoppen. Hva er korrekt?",
    "en": "You are driving on this road and considering an overtake just before the hill crest. What is correct?",
    "th": "คุณกำลังขับรถบนถนนเส้นนี้และพิจารณาที่จะแซงก่อนถึงยอดเนินเล็กน้อย ข้อใดถูกต้อง",
}

APPROVED = ["#2", "#4", "#5"]

inserted = []
for slot in APPROVED:
    p = by_slot[slot]
    proposal = p["proposal"]
    img_path = IMAGE_PATH[slot]
    b64 = image_to_base64(img_path, max_dim=600, quality=82)

    doc = {
        "id": str(uuid.uuid4()),
        "question": proposal["question"],
        "options": proposal["options"],
        "correctOptionId": proposal["correctOptionId"],
        "explanation": proposal["explanation"],
        "bildeUrl": b64,
        "category": proposal["category"],
        "difficulty": proposal["difficulty"],
        "active": True,
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc),
        "audit_verdict": "MATCH",
        "audit_image_identification": proposal.get("image_identification", ""),
    }
    db.questions.insert_one(doc)
    inserted.append((slot, doc["id"], proposal.get("category"), proposal.get("difficulty")))
    print(f"✓ Inserted {slot} -> {doc['id'][:8]}... ({proposal.get('category')}, {proposal.get('difficulty')})")

print()
print(f"Total questions now     : {db.questions.count_documents({})}")
print(f"Questions with base64 img: {db.questions.count_documents({'bildeUrl': {'$regex': '^data:'}})}")
print()
print("Inserted:")
for slot, qid, cat, diff in inserted:
    print(f"  {slot}: {qid} [{cat} / {diff}]")
