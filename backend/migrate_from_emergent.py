"""Export all questions from old Emergent API and import to new MongoDB."""
import asyncio, os, requests
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
EMERGENT_BASE = "https://norge-quiz-app.emergent.host"

async def main():
    # Step 1: Fetch all questions from Emergent
    print("Fetching questions from Emergent...")
    r = requests.get(f"{EMERGENT_BASE}/api/questions?limit=2000", timeout=60)
    all_questions = r.json()
    print(f"Fetched {len(all_questions)} questions")

    print(f"\nTotal fetched: {len(all_questions)} questions")
    if not all_questions:
        print("No questions fetched — stopping.")
        return

    # Step 2: Connect to new MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Step 3: Clear old questions and insert new
    existing = await db.questions.count_documents({})
    print(f"Existing questions in new DB: {existing}")
    print("Clearing old questions...")
    await db.questions.delete_many({})

    print("Inserting all questions...")
    # Remove _id if present to avoid conflicts
    for q in all_questions:
        q.pop("_id", None)

    await db.questions.insert_many(all_questions)
    new_count = await db.questions.count_documents({})
    print(f"\nDone! New DB now has {new_count} questions.")
    client.close()

asyncio.run(main())
