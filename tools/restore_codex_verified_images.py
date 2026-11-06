import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import dns.resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '1.1.1.1']

import pymongo
import json
from pymongo import UpdateOne
from seed_master_quiz import seed_master_quiz_sync

MONGO_URI = "mongodb+srv://norge-quiz-app:m2iD3VNMnbxL7LIm@cluster0.mecy7qw.mongodb.net/thai2drive?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_URI)
db = client["thai2drive"]

# 1. Seed master quiz payload (239 questions from thai2drive_master_quiz_production_payload.json)
res1 = seed_master_quiz_sync(db.questions)
print("Master Quiz Seed:", res1)

# 2. Link verified 191 images from commit 6dcb974
t2d_path = BACKEND_DIR / "content_packs" / "t2d_verified_191_images.json"
with open(t2d_path, "r", encoding="utf-8") as f:
    t2d_links = json.load(f)

ops = []
for item in t2d_links:
    qid = item.get("id")
    url = item.get("bildeUrl")
    if qid and url:
        ops.append(UpdateOne({"id": qid}, {"$set": {"bildeUrl": url, "active": True}}))

if ops:
    res2 = db.questions.bulk_write(ops, ordered=False)
    print(f"T2D Verified Links: matched={res2.matched_count}, modified={res2.modified_count}")

# 3. Final summary
total = db.questions.count_documents({})
with_img = db.questions.count_documents({"bildeUrl": {"$exists": True, "$ne": ""}})
print(f"DONE: MongoDB has {total} total questions, {with_img} with genuine verified images.")
