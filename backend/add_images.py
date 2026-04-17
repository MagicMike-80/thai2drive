"""Add images to existing questions in MongoDB."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

UPDATES = [
    {
        "match": {"question.no": "Hva betyr dette skiltet?", "explanation.no": {"$regex": "sporvogn"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/ong4hk41_Screenshot_20260418_001748.jpg",
        "label": "Holdeplass for sporvogn (foto)"
    },
    {
        "match": {"question.no": "Hva er riktig om dette skiltet?", "explanation.no": {"$regex": "sporvogn"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/onq6ww58_Screenshot_20260418_001754.jpg",
        "label": "Sporvogn-skilt (ikon)"
    },
    {
        "match": {"question.no": "Oppgaven handler om biler som bruker fossilt drivstoff. Hva er riktig?"},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/69oye0n4_Screenshot_20260418_001842.jpg",
        "label": "Fossilt drivstoff (vinter-gate)"
    },
    {
        "match": {"question.no": "Hva viser dette skiltet?", "explanation.no": {"$regex": "tjenester"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/x3p79wdk_Screenshot_20260418_001859.jpg",
        "label": "Epleby service-skilt"
    },
    {
        "match": {"explanation.no": {"$regex": "parkering ikke er tillatt"}},
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/n6tx0uqf_Screenshot_20260418_001827.jpg",
        "label": "Parkering forbudt (P-skilt)"
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
