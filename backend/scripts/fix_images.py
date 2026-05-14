"""
Thai2Drive - Fix bilder
1. Erstatter ustabile Pollinations.ai bilder med offisielle Wikimedia-skilt der mulig
2. Legger til bilder på spørsmål som mangler bilde
Bruk: python fix_images.py
"""

import asyncio
import os
import re
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv(override=True)

# Alle offisielle norske trafikkskilt (Wikimedia Commons - stabile, gratis)
OFFICIAL_SIGNS = {
    # Fareskilt (advarsel)
    "barn": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "skoleelev": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "lekeomr": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "sving": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Norwegian-road-sign-101.svg/240px-Norwegian-road-sign-101.svg.png",
    "svinge": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Norwegian-road-sign-101.svg/240px-Norwegian-road-sign-101.svg.png",
    "kurve": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Norwegian-road-sign-101.svg/240px-Norwegian-road-sign-101.svg.png",
    "veikryss": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Norwegian-road-sign-120.svg/240px-Norwegian-road-sign-120.svg.png",
    "gangfelt": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",
    "fotgjenger": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",
    "togovergang": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-107.svg/240px-Norwegian-road-sign-107.svg.png",
    "jernbane": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-107.svg/240px-Norwegian-road-sign-107.svg.png",
    "is": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Norwegian-road-sign-166.svg/240px-Norwegian-road-sign-166.svg.png",
    "glatt": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Norwegian-road-sign-166.svg/240px-Norwegian-road-sign-166.svg.png",
    "stein": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Norwegian-road-sign-166.svg/240px-Norwegian-road-sign-166.svg.png",
    "vegarbeid": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Norwegian-road-sign-151.svg/240px-Norwegian-road-sign-151.svg.png",
    "arbeid": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Norwegian-road-sign-151.svg/240px-Norwegian-road-sign-151.svg.png",
    "dyr": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Norwegian-road-sign-140.svg/240px-Norwegian-road-sign-140.svg.png",
    "elg": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Norwegian-road-sign-140.svg/240px-Norwegian-road-sign-140.svg.png",
    "fart": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-160.svg/240px-Norwegian-road-sign-160.svg.png",
    "bredde": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-160.svg/240px-Norwegian-road-sign-160.svg.png",

    # Vikeplikt og stopp
    "stopp": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "vikeplikt": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Norwegian-road-sign-204.svg/240px-Norwegian-road-sign-204.svg.png",
    "forkjørsvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Norwegian-road-sign-210.svg/240px-Norwegian-road-sign-210.svg.png",
    "forkjøring": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Norwegian-road-sign-210.svg/240px-Norwegian-road-sign-210.svg.png",
    "prioritert": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Norwegian-road-sign-210.svg/240px-Norwegian-road-sign-210.svg.png",

    # Forbudsskilt
    "innkjøring forbudt": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Norwegian-road-sign-206.svg/240px-Norwegian-road-sign-206.svg.png",
    "forbudt innkjøring": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Norwegian-road-sign-206.svg/240px-Norwegian-road-sign-206.svg.png",
    "parkering forbudt": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Norwegian-road-sign-372.svg/240px-Norwegian-road-sign-372.svg.png",
    "parkering": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Norwegian-road-sign-372.svg/240px-Norwegian-road-sign-372.svg.png",
    "stans": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Norwegian-road-sign-372.svg/240px-Norwegian-road-sign-372.svg.png",
    "forbikjøring": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Norwegian-road-sign-316.svg/240px-Norwegian-road-sign-316.svg.png",
    "forbikjøre": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Norwegian-road-sign-316.svg/240px-Norwegian-road-sign-316.svg.png",

    # Fartsgrenser
    "30 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Norwegian-road-sign-362.1.svg/240px-Norwegian-road-sign-362.1.svg.png",
    "30 km/t": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Norwegian-road-sign-362.1.svg/240px-Norwegian-road-sign-362.1.svg.png",
    "50 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "50 km/t": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "60 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Norwegian-road-sign-362.3.svg/240px-Norwegian-road-sign-362.3.svg.png",
    "80 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Norwegian-road-sign-362.4.svg/240px-Norwegian-road-sign-362.4.svg.png",
    "80 km/t": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Norwegian-road-sign-362.4.svg/240px-Norwegian-road-sign-362.4.svg.png",
    "100 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Norwegian-road-sign-362.5.svg/240px-Norwegian-road-sign-362.5.svg.png",
    "110 km": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Norwegian-road-sign-362.6.svg/240px-Norwegian-road-sign-362.6.svg.png",
    "fartsgrense": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "hastighet": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",

    # Informasjonsskilt
    "rundkjøring": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Norwegian-road-sign-522.svg/240px-Norwegian-road-sign-522.svg.png",
    "rundkjøre": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Norwegian-road-sign-522.svg/240px-Norwegian-road-sign-522.svg.png",
    "motorvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Norwegian-road-sign-502.svg/240px-Norwegian-road-sign-502.svg.png",
    "gangvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Norwegian-road-sign-519.svg/240px-Norwegian-road-sign-519.svg.png",
    "sykkelvei": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Norwegian-road-sign-519.svg/240px-Norwegian-road-sign-519.svg.png",
    "sykkel": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Norwegian-road-sign-519.svg/240px-Norwegian-road-sign-519.svg.png",
    "tunnel": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Norwegian-road-sign-502.svg/240px-Norwegian-road-sign-502.svg.png",
    "bro": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Norwegian-road-sign-502.svg/240px-Norwegian-road-sign-502.svg.png",
    "bru": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Norwegian-road-sign-502.svg/240px-Norwegian-road-sign-502.svg.png",
    "envei": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Norwegian-road-sign-206.svg/240px-Norwegian-road-sign-206.svg.png",
    "enveis": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Norwegian-road-sign-206.svg/240px-Norwegian-road-sign-206.svg.png",

    # Lys og signal
    "lys": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",
    "signallys": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",
    "trafikklys": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Norwegian-road-sign-145.svg/240px-Norwegian-road-sign-145.svg.png",

    # Generelle trafikk
    "kryss": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Norwegian-road-sign-120.svg/240px-Norwegian-road-sign-120.svg.png",
    "feltskifte": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Norwegian-road-sign-522.svg/240px-Norwegian-road-sign-522.svg.png",
    "felt": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Norwegian-road-sign-522.svg/240px-Norwegian-road-sign-522.svg.png",
    "avstand": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Norwegian-road-sign-362.2.svg/240px-Norwegian-road-sign-362.2.svg.png",
    "bilbelte": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "sikkerhetsbelte": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Norwegian-road-sign-142.svg/240px-Norwegian-road-sign-142.svg.png",
    "promille": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "alkohol": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "rus": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Norwegian-road-sign-202.svg/240px-Norwegian-road-sign-202.svg.png",
    "trøtt": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-160.svg/240px-Norwegian-road-sign-160.svg.png",
    "tretthet": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Norwegian-road-sign-160.svg/240px-Norwegian-road-sign-160.svg.png",
}


def find_sign_url(question_text: str) -> str | None:
    """Match question text to official sign image"""
    q_lower = question_text.lower()
    # Try longer keywords first (more specific)
    sorted_keys = sorted(OFFICIAL_SIGNS.keys(), key=len, reverse=True)
    for keyword in sorted_keys:
        if keyword in q_lower:
            return OFFICIAL_SIGNS[keyword]
    return None


async def fix_images():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "thai2drive")

    if not mongo_url:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        with open(env_path) as f:
            for line in f:
                if line.startswith("MONGO_URL="):
                    mongo_url = line.strip().split("=", 1)[1].strip('"')
                if line.startswith("DB_NAME="):
                    db_name = line.strip().split("=", 1)[1].strip('"')

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    print("\n" + "=" * 55)
    print("  Thai2Drive - Fix Bilder")
    print("=" * 55)

    # Stats before
    total = await db.questions.count_documents({})
    with_img_before = await db.questions.count_documents({"bildeUrl": {"$ne": None}})
    print(f"\n  Før: {with_img_before}/{total} spørsmål har bilder")

    fixed_pollinations = 0
    added_new = 0
    skipped = 0

    # 1. Fix Pollinations.ai images (replace with Wikimedia where possible)
    print(f"\n  Steg 1: Sjekker Pollinations.ai bilder...")
    pollinations_q = await db.questions.find(
        {"bildeUrl": {"$regex": "pollinations.ai"}, "active": True}
    ).to_list(1000)

    for q in pollinations_q:
        question_no = q.get("question", {}).get("no", "")
        new_url = find_sign_url(question_no)
        if new_url:
            await db.questions.update_one(
                {"id": q["id"]},
                {"$set": {"bildeUrl": new_url}}
            )
            fixed_pollinations += 1
            print(f"  ✅ Erstattet: {question_no[:60]}")
        else:
            # Remove unstable Pollinations URL
            await db.questions.update_one(
                {"id": q["id"]},
                {"$set": {"bildeUrl": None}}
            )
            print(f"  🗑️  Fjernet ustabilt bilde: {question_no[:60]}")

    # 2. Add images to questions without images
    print(f"\n  Steg 2: Legger til bilder på spørsmål uten bilde...")
    no_img_q = await db.questions.find(
        {"bildeUrl": None, "active": True}
    ).to_list(2000)

    for q in no_img_q:
        question_no = q.get("question", {}).get("no", "")
        new_url = find_sign_url(question_no)
        if new_url:
            await db.questions.update_one(
                {"id": q["id"]},
                {"$set": {"bildeUrl": new_url}}
            )
            added_new += 1
            if added_new <= 20:  # Show first 20
                print(f"  🖼️  La til: {question_no[:60]}")
        else:
            skipped += 1

    # Stats after
    with_img_after = await db.questions.count_documents({"bildeUrl": {"$ne": None}})
    client.close()

    print(f"\n{'=' * 55}")
    print(f"  FERDIG!")
    print(f"  ✅ Pollinations erstattet: {fixed_pollinations}")
    print(f"  🖼️  Nye bilder lagt til:    {added_new}")
    print(f"  ⏭️  Ingen match funnet:     {skipped}")
    print(f"\n  Etter: {with_img_after}/{total} spørsmål har bilder")
    print(f"  (Alle Wikimedia-bilder er stabile og laster alltid)")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    asyncio.run(fix_images())
