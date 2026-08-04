"""Rett skrivefeilen "vikeplykt" -> "vikeplikt" i allerede importerte spørsmål.

seed_vikeplikt_questions.py er rettet i koden, men rader som ble importert før
rettelsen har fortsatt gammel tekst. Dette skriptet retter dem.

Kjører som dry-run som standard — den skriver ingenting før du sender --apply.

    cd backend && python scripts/fix_vikeplykt_typo.py            # vis hva som ville blitt endret
    cd backend && python scripts/fix_vikeplykt_typo.py --apply    # utfør endringen

Krever MONGO_URL og DB_NAME i miljøet, som resten av backend-skriptene.
"""

import argparse
import asyncio
import os
import re

from motor.motor_asyncio import AsyncIOMotorClient

TYPO = "vikeplykt"
FIX = "vikeplikt"

# Felt som kan inneholde brødtekst på norsk. LocalizedText lagres som nøstede
# dokumenter, så vi treffer både flate felt og .no-varianten.
CANDIDATE_FIELDS = [
    "explanation",
    "explanation.no",
    "question",
    "question.no",
    "text",
    "text.no",
]


def _replace_typo(value):
    """Bytt ut skrivefeilen med riktig ordform, uansett store/små bokstaver."""
    if not isinstance(value, str) or TYPO not in value.lower():
        return None
    return re.sub(TYPO, FIX, value, flags=re.IGNORECASE)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="utfør endringen (uten denne: dry-run)")
    args = parser.parse_args()

    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        raise SystemExit("MONGO_URL og DB_NAME må være satt.")

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    query = {"$or": [{f: {"$regex": TYPO, "$options": "i"}} for f in CANDIDATE_FIELDS]}
    docs = await db.questions.find(query).to_list(1000)

    if not docs:
        print(f"Fant ingen rader med «{TYPO}». Ingenting å gjøre.")
        return

    print(f"Fant {len(docs)} rad(er) med «{TYPO}».\n")
    changed = 0
    for doc in docs:
        updates = {}
        for field in CANDIDATE_FIELDS:
            parts = field.split(".")
            value = doc
            for part in parts:
                value = value.get(part) if isinstance(value, dict) else None
            fixed = _replace_typo(value)
            if fixed is not None:
                updates[field] = fixed
                print(f"  {doc.get('id')}  {field}")
                print(f"    før:  {value}")
                print(f"    etter: {fixed}")
        if updates and args.apply:
            await db.questions.update_one({"_id": doc["_id"]}, {"$set": updates})
            changed += 1

    if args.apply:
        print(f"\nOppdaterte {changed} rad(er).")
    else:
        print("\nDry-run — ingenting er skrevet. Kjør på nytt med --apply for å utføre.")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
