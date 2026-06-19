"""
Create or upgrade a user in Thai2Drive to Premium for a limited duration (e.g. 1 month).
Usage:
  python create_promo_user.py --email friend@example.com [--password newpass123] [--days 30]
"""
import asyncio
import os
import sys
import argparse
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

load_dotenv(Path(__file__).parent / '.env')

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def main(email: str, password: str | None, days: int):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    email = email.strip().lower()

    # Calculate expiration time
    expire_dt = datetime.now(timezone.utc) + timedelta(days=days)
    expire_iso = expire_dt.isoformat()

    print(f"\n{'='*60}")
    print(f"  Setting Premium access for: {email}")
    print(f"  Duration: {days} days (Expires: {expire_iso})")
    print(f"{'='*60}\n")

    # Check if user exists
    user = await db.users.find_one({"email": email})
    if not user:
        user = await db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})

    if user:
        print(f"✅ Existing user found (id: {user.get('id')})")
        
        # Update existing user to premium
        update_doc = {
            "is_premium": True,
            "premium_expires_at": expire_iso
        }
        
        if password:
            password_hash = pwd_context.hash(password)
            update_doc["password_hash"] = password_hash
            print("   → Password will be updated.")
            
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": update_doc}
        )
        print("🎉 SUCCESS: User upgraded to Premium successfully!")
        if password:
            print(f"   Login: {email}")
            print(f"   Password: {password}")
    else:
        print(f"ℹ️ User not found. Creating a NEW user account.")
        if not password:
            print("❌ ERROR: A password is required when creating a new user account.")
            print("   Use: --password <pass>")
            client.close()
            return
            
        password_hash = pwd_context.hash(password)
        user_id = str(uuid.uuid4())
        
        user_doc = {
            "id": user_id,
            "email": email,
            "name": "Beta Tester",
            "password_hash": password_hash,
            "is_admin": False,
            "is_premium": True,
            "premium_expires_at": expire_iso,
            "device_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        await db.users.insert_one(user_doc)
        print("🎉 SUCCESS: New user created and granted Premium access!")
        print(f"   Login: {email}")
        print(f"   Password: {password}")
        
    client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or upgrade a user to temporary premium")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", default=None, help="Password for the user (required for new accounts)")
    parser.add_argument("--days", type=int, default=30, help="Number of days of premium access (default: 30)")
    args = parser.parse_args()
    asyncio.run(main(args.email, args.password, args.days))
