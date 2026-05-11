"""Normalize all category names to proper Title Case English in MongoDB."""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

# Map everything to canonical English Title Case
CATEGORY_MAP = {
    # English variants
    "traffic signs": "Traffic Signs", "traffic sign": "Traffic Signs",
    "road rules": "Road Rules",
    "right of way": "Right of Way",
    "speed limits": "Speed Limits", "speed limit": "Speed Limits",
    "safety": "Safety",
    "driving conditions": "Driving Conditions", "driving condition": "Driving Conditions",
    "situations": "Situations", "situation": "Situations",
    "traffic rules": "Traffic Rules",
    "road conditions": "Road Conditions", "road condition": "Road Conditions",
    # Norwegian variants → English
    "skilt": "Traffic Signs", "trafikkskilt": "Traffic Signs",
    "trafikkregler": "Road Rules",
    "vikeplikt": "Right of Way",
    "fartsgrenser": "Speed Limits", "fart": "Speed Limits",
    "sikkerhet": "Safety",
    "kjøreforhold": "Driving Conditions", "kjøreteknikk": "Driving Conditions",
    "situasjoner": "Situations",
    "grunnregler": "Traffic Rules",
    "veiforhold": "Road Conditions",
    "lover og regler": "Road Rules",
    "plassering": "Road Rules",
    "risikoforståelse": "Safety",
    "nødsituasjon": "Safety",
    "parkering": "Traffic Rules",
    "miljø": "Driving Conditions",
}

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    all_q = await db.questions.find({}, {"_id": 1, "category": 1}).to_list(10000)
    print(f"Total questions: {len(all_q)}")

    updated = 0
    unknown = set()
    for q in all_q:
        cat = q.get("category", "")
        canonical = CATEGORY_MAP.get(cat.lower())
        if canonical and canonical != cat:
            await db.questions.update_one({"_id": q["_id"]}, {"$set": {"category": canonical}})
            updated += 1
        elif not canonical:
            unknown.add(cat)

    print(f"Updated: {updated} questions")
    if unknown:
        print(f"Unknown categories (not mapped): {unknown}")

    # Verify
    from pymongo import MongoClient
    sync_client = MongoClient(MONGO_URL)
    sync_db = sync_client[DB_NAME]
    cats = sync_db.questions.distinct("category")
    print(f"\nCategories now in DB: {sorted(cats)}")
    sync_client.close()
    client.close()

asyncio.run(main())
