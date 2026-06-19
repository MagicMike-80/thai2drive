"""
setup_admin.py — Opprett eller reparer admin-bruker i MongoDB.
Kjør: python setup_admin.py
"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

mongo_url = os.environ["MONGO_URL"]
db_name   = os.environ["DB_NAME"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_EMAIL    = "admin@thai2drive.com"
ADMIN_PASSWORD = "admin123"

async def main():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    # 1. Legg til i admin_users hvis mangler
    existing = await db.admin_users.find_one({"email": ADMIN_EMAIL})
    if not existing:
        await db.admin_users.insert_one({"email": ADMIN_EMAIL})
        print(f"OK Lagt til {ADMIN_EMAIL} i admin_users")
    else:
        print(f"OK {ADMIN_EMAIL} finnes allerede i admin_users")

    # 2. Opprett eller oppdater bruker i users
    user = await db.users.find_one({"email": ADMIN_EMAIL})
    password_hash = pwd_context.hash(ADMIN_PASSWORD)

    if not user:
        import uuid
        from datetime import datetime, timezone
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": ADMIN_EMAIL,
            "password_hash": password_hash,
            "is_admin": True,
            "is_premium": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        print(f"OK Opprettet bruker {ADMIN_EMAIL} med passord '{ADMIN_PASSWORD}'")
    else:
        await db.users.update_one(
            {"email": ADMIN_EMAIL},
            {"$set": {
                "password_hash": password_hash,
                "is_admin": True,
                "is_premium": True,
            }}
        )
        print(f"OK Oppdatert {ADMIN_EMAIL} — passord og admin-status satt")

    # 3. Bekreft
    user_check = await db.users.find_one({"email": ADMIN_EMAIL}, {"_id": 0, "email": 1, "is_admin": 1})
    print(f"\n-- Resultat: {user_check}")
    print(f"\n-- Logg inn med:")
    print(f"   E-post:  {ADMIN_EMAIL}")
    print(f"   Passord: {ADMIN_PASSWORD}")
    print(f"   URL:     https://www.thai2drive.no/api/admin-panel")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
