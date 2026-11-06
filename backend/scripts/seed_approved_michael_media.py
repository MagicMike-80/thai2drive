"""Copy already approved Michael videos into the teacher media catalog.

Dry-run by default. The source collection is the approval authority; drafts in
media_catalog are never activated by this script.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from bson import json_util
from pymongo import MongoClient

from backend.media_catalog import normalize_catalog_text, validate_catalog_document


AREA_BY_CATEGORY = {"vikeplikt": "right_of_way", "stoppelengde": "speed_distance"}
EXPECTED_SOURCE_COUNT = 26
FIELDS = ("type", "category", "learning_area_id", "tags", "media_url",
          "thumbnail_url", "is_active", "content_language", "i18n",
          "approved_for_michael", "approved_for_teacher", "source_id")


def catalog_document(source: dict) -> dict:
    if source.get("active") is not True or source.get("approved_for_michael") is not True:
        raise ValueError(f"source is not approved: {source.get('id')}")
    if source.get("type") != "video" or source.get("category") not in AREA_BY_CATEGORY:
        raise ValueError(f"unexpected source type/category: {source.get('id')}")
    language = source.get("language")
    if language != "no":
        raise ValueError(f"unexpected video language: {source.get('id')}")
    item = {
        "media_id": source["id"],
        "type": "video",
        "category": source["category"],
        "learning_area_id": AREA_BY_CATEGORY[source["category"]],
        "tags": list(dict.fromkeys(normalize_catalog_text(tag)
                                   for tag in source["topic_tags"])),
        "media_url": source["source_url"],
        "thumbnail_url": source["thumbnail_url"],
        "is_active": True,
        "content_language": language,
        "i18n": {lang: {"title": source["title"][lang],
                         "description": source["caption"][lang]}
                 for lang in ("no", "th", "en")},
        "approved_for_michael": True,
        "approved_for_teacher": True,
        "source_id": source["source_id"],
    }
    validate_catalog_document(item)
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-db-name", default="")
    parser.add_argument("--snapshot-dir", type=Path,
                        default=Path("output/media-catalog-approved-seed"))
    args = parser.parse_args()
    db_name = os.environ.get("DB_NAME", "").strip()
    mongo_url = os.environ.get("MONGO_URL", "").strip()
    if not db_name or not mongo_url:
        raise ValueError("MONGO_URL and DB_NAME are required")
    if args.apply and args.confirm_db_name != db_name:
        raise ValueError("--confirm-db-name must equal DB_NAME")

    client = MongoClient(mongo_url, serverSelectionTimeoutMS=15000)
    try:
        db = client[db_name]
        sources = list(db["michael_materials"].find(
            {"active": True, "approved_for_michael": True}))
        if len(sources) != EXPECTED_SOURCE_COUNT:
            raise ValueError(f"expected {EXPECTED_SOURCE_COUNT} approved sources, got {len(sources)}")
        documents = [catalog_document(source) for source in sources]
        ids = [item["media_id"] for item in documents]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate source IDs")
        collection = db["media_catalog"]
        previous = list(collection.find({"media_id": {"$in": ids}}))
        by_id = {item["media_id"]: item for item in previous}
        changes = [item for item in documents if any(
            by_id.get(item["media_id"], {}).get(field) != item[field] for field in FIELDS)]
        print(f"DRY RUN database={db_name} approved={len(documents)} existing={len(previous)} "
              f"would_write={len(changes)} areas=right_of_way:12,speed_distance:14")
        if not args.apply:
            return 0
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot = args.snapshot_dir / f"before_{stamp}.json"
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(json_util.dumps({"source_ids": ids, "previous": previous}, indent=2),
                            encoding="utf-8")
        now = datetime.now(timezone.utc)
        for item in changes:
            collection.update_one(
                {"media_id": item["media_id"]},
                {"$set": {**item, "updated_at": now},
                 "$setOnInsert": {"created_at": now}}, upsert=True)
        after = list(collection.find({"media_id": {"$in": ids}}))
        if len(after) != len(ids) or any(
            any(row.get(field) != item[field] for field in FIELDS)
            for item in documents for row in after if row.get("media_id") == item["media_id"]
        ):
            raise RuntimeError("post-write verification failed; inspect snapshot")
        print(f"APPLY OK database={db_name} written={len(changes)} verified={len(after)} "
              f"snapshot={snapshot}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
