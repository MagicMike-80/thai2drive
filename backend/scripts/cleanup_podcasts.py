"""cleanup_podcasts.py — deaktiver podcasts med døde lydfiler, fiks stier.

Kjør: cd backend && python scripts/cleanup_podcasts.py
"""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "")
if not MONGO_URL:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGO_URL="):
                    MONGO_URL = line.split("=", 1)[1].strip('"').strip("'")
                    break
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not found")

PUBLIC_ASSETS = os.path.join(os.path.dirname(__file__), "..", "public_assets")

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["thai2drive"]
    podcasts = await db.learning_podcasts.find({}).to_list(500)
    print(f"Found {len(podcasts)} total podcast entries")

    deactivated = fixed_path = ok = 0
    for p in podcasts:
        pid = p.get("id", "?")
        title = p.get("title_no") or p.get("title_th") or "(no title)"
        fp = p.get("file_path", "")
        lang = p.get("language", "no")
        active = p.get("active", True)

        if not fp:
            print(f"  [{lang}] {title} — NO file_path, deactivating")
            await db.learning_podcasts.update_one({"id": pid}, {"$set": {"active": False}})
            deactivated += 1
            continue

        # Normalize: strip /api/assets/ or /api/audio/ prefix if present
        clean_fp = fp
        if clean_fp.startswith("/api/assets/"):
            clean_fp = "/public_assets/" + clean_fp[len("/api/assets/"):]
        if clean_fp.startswith("/api/audio/"):
            clean_fp = "/public_assets/" + clean_fp[len("/api/audio/"):]

        # Map to local disk path
        local_path = clean_fp.replace("/public_assets/", "").lstrip("/")
        full_path = os.path.join(PUBLIC_ASSETS, local_path)

        if os.path.isfile(full_path):
            if clean_fp != fp:
                print(f"  FIX [{lang}] {title}: {fp} -> {clean_fp}")
                await db.learning_podcasts.update_one(
                    {"id": pid},
                    {"$set": {"file_path": clean_fp, "active": True}}
                )
                fixed_path += 1
            else:
                ok += 1
        else:
            print(f"  DEACTIVATE [{lang}] {title}: file not found at {clean_fp}")
            await db.learning_podcasts.update_one({"id": pid}, {"$set": {"active": False}})
            deactivated += 1

    print(f"\nDone: {ok} OK, {fixed_path} fixed, {deactivated} deactivated")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
