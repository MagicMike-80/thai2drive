"""Add 5 more images to existing questions in MongoDB."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

UPDATES = [
    {
        "match": {"explanation.no": {"$regex": "farlig gods"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/4bd47d04_Screenshot_20260418_001534.jpg",
        "label": "Farlig last (tankbil)"
    },
    {
        "match": {"question.no": {"$regex": "privat.*velseskj.*ring"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/9zoe6e32_Screenshot_20260418_001625.jpg",
        "label": "Privat øvelseskjøring (L-merke)"
    },
    {
        "match": {"question.no": {"$regex": "riktig.*anta.*skiltet"}, "explanation.no": {"$regex": "forkj.*rsvei"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/p3vlt7di_Screenshot_20260418_001603.jpg",
        "label": "Forkjørsvei-skilt (diamant)"
    },
    {
        "match": {"question.no": {"$regex": "kantlinjen.*stiplet"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/5wpcoc9b_Screenshot_20260418_001743.jpg",
        "label": "Stiplet kantlinje (vei)"
    },
    {
        "match": {"question.no": {"$regex": "Hvor langt er 3 sekunders"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/u3yvajv6_Screenshot_20260418_001638.jpg",
        "label": "3 sekunders avstand (motorvei)"
    },
]

async def update():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    updated = 0
    for u in UPDATES:
        result = await db.questions.update_one(u["match"], {"$set": {"bildeUrl": u["bildeUrl"]}})
        if result.modified_count > 0:
            print(f"  OK {u['label']}")
            updated += 1
        else:
            print(f"  SKIP {u['label']}")

    print(f"\nUpdated: {updated}/5")
    with_images = await db.questions.count_documents({"bildeUrl": {"$ne": None}})
    total = await db.questions.count_documents({})
    print(f"Questions with images: {with_images}/{total}")
    client.close()

asyncio.run(update())
