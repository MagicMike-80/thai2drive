"""One-time MongoDB correction for the railway image and two held questions.

Run from the repository root. The default prints the proposed changes without
writing; pass --apply only after reviewing the three matching records.
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


RAILWAY_QUESTION_ID = "fe7657b8-5755-495b-aefd-56b595c73194"
RAILWAY_IMAGE_URL = "/api/sign-images/135_0.jpg"
HELD_QUESTION_IDS = ("q016", "03e1d9e8-3bfc-4636-8536-fe84ad1506cc")
BACKEND_DIR = Path(__file__).resolve().parents[1]


def patch_questions(collection, *, apply: bool = False) -> list[dict]:
    """Change only the named records; report missing IDs instead of upserting."""
    records = {}
    for question_id in (RAILWAY_QUESTION_ID, *HELD_QUESTION_IDS):
        current = collection.find_one({"id": question_id}, {"_id": 0, "bildeUrl": 1, "active": 1})
        if current is None:
            raise LookupError(f"Question not found: {question_id}")
        records[question_id] = current

    changes = []
    for question_id in (RAILWAY_QUESTION_ID, *HELD_QUESTION_IDS):
        current = records[question_id]
        field = "bildeUrl" if question_id == RAILWAY_QUESTION_ID else "active"
        desired = RAILWAY_IMAGE_URL if field == "bildeUrl" else False
        previous = current.get(field)
        if previous == desired:
            continue
        changes.append({"id": question_id, "field": field, "previous": previous, "new": desired})
        if apply:
            result = collection.update_one(
                {"id": question_id, field: previous}, {"$set": {field: desired}}
            )
            if result.matched_count != 1:
                raise RuntimeError(f"Question changed or disappeared: {question_id}")
    return changes


def verify_questions(collection) -> None:
    """Fail deployment unless all three persisted values match the repair."""
    expected = {RAILWAY_QUESTION_ID: ("bildeUrl", RAILWAY_IMAGE_URL)}
    expected.update({question_id: ("active", False) for question_id in HELD_QUESTION_IDS})
    for question_id, (field, value) in expected.items():
        current = collection.find_one({"id": question_id}, {"_id": 0, field: 1})
        if current is None or current.get(field) != value:
            raise RuntimeError(f"Exam content patch verification failed: {question_id}.{field}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the three reviewed corrections")
    args = parser.parse_args()
    if not (BACKEND_DIR / "sign_images" / "135_0.jpg").is_file():
        raise FileNotFoundError("backend/sign_images/135_0.jpg")
    load_dotenv(BACKEND_DIR / ".env")
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        raise RuntimeError("MONGO_URL and DB_NAME are required; no database was changed")
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    try:
        collection = client[db_name].questions
        changes = patch_questions(collection, apply=args.apply)
        for change in changes:
            print(f"{change['id']}: {change['field']} {change['previous']!r} -> {change['new']!r}")
        print(f"{len(changes)} change(s) {'applied' if args.apply else 'planned (dry run)'}")
        if args.apply:
            verify_questions(collection)
            print("Exam content patch verified: 3/3 records")
    finally:
        client.close()


if __name__ == "__main__":
    main()
