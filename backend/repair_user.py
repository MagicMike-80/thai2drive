"""
Diagnose and repair a user account in MongoDB.

Usage:
  python repair_user.py --email user@example.com [--set-password newpass123]

What it does:
  1. Finds user by email (case-insensitive)
  2. Reports: password_hash, premium status, reset codes, account flags
  3. Optionally sets a new password
  4. Clears old/used reset codes
  5. Restores account to free-tier if premium expired
"""
import asyncio, os, sys, argparse
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

load_dotenv(Path(__file__).parent / '.env')

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]


async def main(email: str, new_password: str | None):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    email = email.strip().lower()

    print(f"\n{'='*60}")
    print(f"  Diagnosing user: {email}")
    print(f"{'='*60}\n")

    # ── Find user ──────────────────────────────────────────────
    user = await db.users.find_one({"email": email})
    if not user:
        # Try case-insensitive
        user = await db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})

    if not user:
        print(f"❌ USER NOT FOUND: {email}")
        print("   → No account with this email exists in the database.")
        client.close()
        return

    print(f"✅ User found")
    print(f"   id           : {user.get('id', 'MISSING')}")
    print(f"   email (db)   : {user.get('email')}")
    print(f"   name         : {user.get('name', '(none)')}")
    print(f"   created_at   : {user.get('created_at', 'unknown')}")
    print()

    # ── Password hash ──────────────────────────────────────────
    has_hash = bool(user.get("password_hash"))
    print(f"  password_hash : {'✅ exists' if has_hash else '❌ MISSING — user cannot log in!'}")
    print()

    # ── Premium status ─────────────────────────────────────────
    is_premium = user.get("is_premium", False)
    is_admin = user.get("is_admin", False)
    premium_expires_at = user.get("premium_expires_at") or user.get("premium_until")
    subscription_status = user.get("subscription_status", "(not set)")

    print(f"  is_premium         : {is_premium}")
    print(f"  is_admin           : {is_admin}")
    print(f"  premium_expires_at : {premium_expires_at or '(not set)'}")
    print(f"  subscription_status: {subscription_status}")

    if is_premium and premium_expires_at:
        try:
            exp = datetime.fromisoformat(str(premium_expires_at).replace("Z", "+00:00"))
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            expired = exp < datetime.now(timezone.utc)
            print(f"  premium expired    : {'⚠️  YES — will be treated as free account' if expired else '✅ No'}")
            if expired and not is_admin:
                print("  → Login is still allowed; user will be treated as free tier automatically.")
        except Exception as e:
            print(f"  ⚠️  Could not parse premium_expires_at: {e}")
    print()

    # ── Reset codes ────────────────────────────────────────────
    resets = await db.password_resets.find({"email": email}).to_list(10)
    print(f"  password_resets docs: {len(resets)}")
    for r in resets:
        used = r.get("used", False)
        expires_at = r.get("expires_at", "?")
        created_at = r.get("created_at", "?")
        try:
            exp_str = str(expires_at).replace("Z", "+00:00")
            exp_dt = datetime.fromisoformat(exp_str)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            expired = exp_dt < datetime.now(timezone.utc)
            status = "USED" if used else ("EXPIRED" if expired else "✅ VALID")
        except Exception:
            status = "unknown"
        print(f"    code=****  expires={expires_at}  used={used}  status={status}")
    print()

    # ── Repair actions ─────────────────────────────────────────
    if new_password:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash(new_password)
        await db.users.update_one(
            {"email": email},
            {"$set": {"password_hash": password_hash}}
        )
        print(f"✅ Password updated for {email}")

    # Clear old reset codes
    del_result = await db.password_resets.delete_many({"email": email, "used": True})
    if del_result.deleted_count:
        print(f"✅ Cleared {del_result.deleted_count} used reset code(s)")

    # Normalise email to lowercase in DB
    if user.get("email") != email:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"email": email}}
        )
        print(f"✅ Email normalised to lowercase: {email}")

    print()
    print("Done. Run again without --set-password to verify the state.")
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnose and repair a Thai2Drive user account")
    parser.add_argument("--email", required=True, help="User email to diagnose")
    parser.add_argument("--set-password", dest="password", default=None, help="Optional: set a new password")
    args = parser.parse_args()
    asyncio.run(main(args.email, args.password))
