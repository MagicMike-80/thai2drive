"""Classify the existing production media drafts without changing approval flags.

Dry-run is the default. --apply requires the exact production DB name, takes a
small rollback snapshot, and fails if the catalog differs from the reviewed map.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from backend.media_catalog import LEARNING_AREA_IDS


DEFAULT_MAP = Path(__file__).resolve().parents[1] / "media_catalog_area_map.json"


def load_area_map(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    areas = payload.get("areas") if isinstance(payload, dict) else None
    if not isinstance(areas, dict) or not areas:
        raise ValueError("area map must contain a non-empty areas object")
    for media_id, area_id in areas.items():
        if not isinstance(media_id, str) or not media_id.strip():
            raise ValueError("area map has an empty media_id")
        if area_id not in LEARNING_AREA_IDS:
            raise ValueError(f"unsupported learning_area_id for {media_id}")
    return areas


def plan_classification(documents: list[dict], areas: dict[str, str]) -> list[tuple[dict, str]]:
    by_id = {document.get("media_id"): document for document in documents}
    if len(by_id) != len(documents):
        raise ValueError("production media_id values are missing or duplicated")
    if set(by_id) != set(areas):
        raise ValueError(
            f"catalog IDs differ from area map: missing={sorted(set(areas) - set(by_id))}, "
            f"extra={sorted(set(by_id) - set(areas))}"
        )
    changes = []
    for media_id, area_id in sorted(areas.items()):
        document = by_id[media_id]
        current = document.get("learning_area_id")
        if current not in (None, area_id):
            raise ValueError(f"conflicting learning_area_id for {media_id}: {current}")
        if current != area_id:
            changes.append((document, area_id))
    return changes


def snapshot_before(path: Path, documents: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "Restore learning_area_id from these values if classification must be reversed.",
        "rows": [
            {
                "media_id": document["media_id"],
                "learning_area_id": document.get("learning_area_id"),
                "is_active": document.get("is_active"),
                "approved_for_michael": document.get("approved_for_michael"),
                "approved_for_teacher": document.get("approved_for_teacher"),
            }
            for document in sorted(documents, key=lambda item: item["media_id"])
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--area-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-db-name", default="")
    parser.add_argument("--snapshot-dir", type=Path, default=Path("output/media-catalog-classification"))
    args = parser.parse_args()

    areas = load_area_map(args.area_map)
    db_name = os.environ.get("DB_NAME", "").strip()
    mongo_url = os.environ.get("MONGO_URL", "").strip()
    if not db_name or not mongo_url:
        raise ValueError("MONGO_URL and DB_NAME must be set")
    if args.apply and args.confirm_db_name != db_name:
        raise ValueError("--confirm-db-name must exactly match DB_NAME")

    from pymongo import MongoClient

    client = MongoClient(mongo_url, serverSelectionTimeoutMS=15000)
    try:
        collection = client[db_name]["media_catalog"]
        documents = list(collection.find({}, {
            "media_id": 1,
            "learning_area_id": 1,
            "is_active": 1,
            "approved_for_michael": 1,
            "approved_for_teacher": 1,
        }))
        changes = plan_classification(documents, areas)
        if not args.apply:
            print(f"DRY RUN database={db_name} rows={len(documents)} would_classify={len(changes)} no_writes=true")
            return 0

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot_path = args.snapshot_dir / f"before_{stamp}.json"
        snapshot_before(snapshot_path, documents)
        for document, area_id in changes:
            result = collection.update_one(
                {"_id": document["_id"], "learning_area_id": document.get("learning_area_id")},
                {"$set": {"learning_area_id": area_id}},
            )
            if result.matched_count != 1:
                raise RuntimeError(f"concurrent change to {document['media_id']}; stop and inspect snapshot")
        after = list(collection.find({}, {"media_id": 1, "learning_area_id": 1}))
        if {item["media_id"]: item.get("learning_area_id") for item in after} != areas:
            raise RuntimeError("post-write area verification failed; inspect snapshot")
        print(f"APPLY OK database={db_name} classified={len(changes)} rows={len(after)} snapshot={snapshot_path}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
