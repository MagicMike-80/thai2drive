"""Add admin user to database."""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
ADMIN_EMAIL = "michael.6lee@yahoo.com"

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    existing = await db.admin_users.find_one({"email": ADMIN_EMAIL})
    if existing:
        print(f"Already admin: {ADMIN_EMAIL}")
    else:
        await db.admin_users.insert_one({"email": ADMIN_EMAIL})
        print(f"Added admin: {ADMIN_EMAIL}")

    await db.users.update_one(
        {"email": ADMIN_EMAIL},
        {"$set": {"is_admin": True, "is_premium": True}}
    )
    print("Updated user record: is_admin=True, is_premium=True")
    client.close()

asyncio.run(main())
