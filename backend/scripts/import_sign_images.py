"""
import_sign_images.py — scan the 9-sign-group image folders and update MongoDB sign
documents with the correct image_url.

Strategy: images are served from Railway via /api/sign-images/{filename} after the
static mount is added in server.py. This script builds the URL map and patches
existing signs in MongoDB. New signs (if not yet in DB) are created as stubs.

Run AFTER: adding the /api/sign-images static mount to server.py and deploying.
Then run: python backend/scripts/import_sign_images.py

Folder expected at: C:/Users/Stein Hoang/Telia Sky/Thai2Drive1/9skiltgrupper/
"""

import asyncio
import os
import re
import uuid
from pathlib import Path
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get(
    "MONGO_URL",
    "mongodb+srv://norge-quiz-app:m2iD3VNMnbxL7LIm@cluster0.mecy7qw.mongodb.net/thai2drive?retryWrites=true&w=majority",
)
DB_NAME      = "thai2drive"
SIGN_IMG_DIR = Path(r"C:\Users\Stein Hoang\Telia Sky\Thai2Drive1\9skiltgrupper")
BASE_URL     = "https://thai2drive-production.up.railway.app/api/sign-images"  # update if domain differs

# Map folder name → (group number, Norwegian group name)
FOLDER_GROUP_MAP = {
    "vikeplikt-jpg (1)":   (1, "Vikepliktskilt"),
    "fareskilt-jpg":        (2, "Fareskilt"),
    "forbudsskilt-jpg-png": (3, "Forbudtskilt"),
    "pabudsskilt-jpg (1)":  (4, "Påbudsskilt"),
    "opplysningsskilt-jpg": (5, "Opplysningsskilt"),
    "serviceskilt-jpg":     (6, "Serviceskilt"),
    "vegvisningsskilt-jpg": (7, "Veivisningsskilt"),
    "underskilt-jpg-og-png":(8, "Underskilt"),
    "markeringsskilt-jpg":  (9, "Markeringsskilt"),
}

# Extract sign_id from filename like "100_1 Skarp sving til hoyre.jpg" → "100_1"
# or "202_0.jpg" → "202_0"
def _sign_id(filename: str) -> str:
    m = re.match(r"^(\d+_\d+)", filename)
    return m.group(1) if m else ""

def _name_from_filename(filename: str) -> str:
    stem = Path(filename).stem  # strip extension
    # Strip sign_id prefix and clean up
    name = re.sub(r"^\d+_\d+\s*", "", stem).strip()
    return name if name else stem


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    inserted = 0
    updated  = 0
    skipped  = 0

    for folder_name, (group_num, group_label_no) in FOLDER_GROUP_MAP.items():
        folder = SIGN_IMG_DIR / folder_name
        if not folder.exists():
            print(f"  [skip] folder not found: {folder_name}")
            continue

        files = sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"})
        if not files:
            print(f"  [skip] no images in: {folder_name}")
            continue

        print(f"\nGroup {group_num} — {group_label_no} ({len(files)} images)")

        for img_path in files:
            sign_id = _sign_id(img_path.name)
            if not sign_id:
                print(f"    [skip] can't parse sign_id from: {img_path.name}")
                skipped += 1
                continue

            image_url = f"{BASE_URL}/{img_path.name}"
            name_no   = _name_from_filename(img_path.name) or sign_id

            existing = await db.traffic_signs.find_one({"id": sign_id})
            if existing:
                await db.traffic_signs.update_one(
                    {"id": sign_id},
                    {"$set": {"image_url": image_url}},
                )
                print(f"    updated  {sign_id}  →  {img_path.name}")
                updated += 1
            else:
                doc = {
                    "id":         sign_id,
                    "group":      group_num,
                    "order":      int(sign_id.split("_")[0]) if "_" in sign_id else 0,
                    "name":       {"no": name_no, "th": "", "en": ""},
                    "image_url":  image_url,
                    "explanation":{"no": "", "th": "", "en": ""},
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                await db.traffic_signs.insert_one(doc)
                print(f"    inserted {sign_id}  →  {name_no}")
                inserted += 1

    print(f"\nDone — inserted: {inserted}, updated: {updated}, skipped: {skipped}")
    client.close()


asyncio.run(main())
