"""Safely audit or apply the reviewed production traffic-sign correction.

Dry-run is the default. Database writes require both ``--apply`` and a verified
pre-change backup manifest. Removed documents are copied to a snapshot
collection in the same transaction before the active collection is changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from pymongo import ASCENDING, MongoClient


BACKEND = Path(__file__).resolve().parents[1]
CATALOG_PATH = BACKEND / "signs_content.json"
IMAGE_DIR = BACKEND / "sign_images"
RENAMES = {"521_0": "521_1", "521.1": "521_2", "556_0": "556_1", "556.2": "556_2", "807-10": "807_10"}
REMOVED = {"808_42", "902_0", "904_0", "906_0", "930"}
AUDIO_KEYS = {"audio", "audio_url", "sound_url", "tts"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_backup(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent / "collections"
    errors = []
    for item in manifest.get("collections", []):
        bson_path = root / f"{item['name']}.bson"
        if not bson_path.is_file() or sha256(bson_path) != item["sha256"]:
            errors.append(item["name"])
    if errors or len(manifest.get("collections", [])) != 43 or manifest.get("total_documents") != 6594:
        raise RuntimeError(f"Backup verification failed: {errors or 'unexpected manifest totals'}")
    return manifest


def image_map(catalog: list[dict]) -> dict[str, str]:
    ids = {row["id"] for row in catalog}
    result = {}
    for path in IMAGE_DIR.glob("*.jpg"):
        matches = [sign_id for sign_id in ids if path.stem == sign_id or path.stem.startswith(sign_id + "_")]
        if len(matches) != 1:
            raise RuntimeError(f"Image owner collision for {path.name}: {matches}")
        result[matches[0]] = f"/api/sign-images/{path.name}"
    if set(result) != ids:
        raise RuntimeError(f"Image/catalog mismatch: missing={sorted(ids - set(result))}")
    return result


def compact(doc: dict | None) -> dict | None:
    if doc is None:
        return None
    return {key: value for key, value in doc.items() if key != "_id"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-manifest", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.apply and not args.backup_manifest:
        parser.error("--apply requires --backup-manifest")
    backup = verify_backup(args.backup_manifest) if args.backup_manifest else None

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    images = image_map(catalog)
    if len(catalog) != 311 or len({row["id"] for row in catalog}) != 311:
        raise RuntimeError("Expected exactly 311 unique reviewed catalog records")

    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ["DB_NAME"]
    client = MongoClient(mongo_url)
    db = client[db_name]
    collection = db.traffic_signs
    before = list(collection.find({}))
    by_id = {doc["id"]: doc for doc in before if doc.get("id")}
    legacy = [doc for doc in before if not doc.get("id")]
    if len(before) != 340 or len(by_id) != 316 or len(legacy) != 24:
        raise RuntimeError(f"Unexpected production baseline: total={len(before)}, ids={len(by_id)}, legacy={len(legacy)}")
    if any(AUDIO_KEYS.intersection(doc) for doc in before):
        raise RuntimeError("Unexpected per-sign audio reference found; refusing to migrate")

    reverse_renames = {new: old for old, new in RENAMES.items()}
    changes = []
    updates = []
    for order, row in enumerate(catalog, start=1):
        target_id = row["id"]
        source_id = reverse_renames.get(target_id, target_id)
        source = by_id[source_id]
        values = {
            "id": target_id,
            "group": row["group"],
            "order": source.get("order", order),
            "name": row["name"],
            "image_url": images[target_id],
        }
        delta = {key: {"before": source.get(key), "after": value} for key, value in values.items() if source.get(key) != value}
        if delta:
            changes.append({"source_id": source_id, "target_id": target_id, "fields": delta})
        updates.append((source["_id"], values))

    removed_docs = [by_id[sign_id] for sign_id in sorted(REMOVED)] + legacy
    run_id = datetime.now(timezone.utc).strftime("sign-catalog-%Y%m%dT%H%M%SZ")
    report = {
        "run_id": run_id,
        "mode": "apply" if args.apply else "dry-run",
        "database": db_name,
        "before": {"documents": len(before), "canonical": len(by_id), "legacy": len(legacy)},
        "planned": {"updates": len(changes), "removed": len(removed_docs), "final_documents": 311},
        "removed": [{"id": doc.get("id"), "sign_id": doc.get("sign_id"), "reason": "obsolete_or_no_image" if doc.get("id") else "legacy_schema"} for doc in removed_docs],
        "changes": changes,
        "audio": {"references_before": 0, "contract": "dynamic TTS; no per-sign audio file"},
        "backup": {"manifest": str(args.backup_manifest) if args.backup_manifest else None, "documents": backup.get("total_documents") if backup else None},
    }

    if args.apply:
        snapshots = db.traffic_signs_migration_snapshots
        with client.start_session() as session:
            with session.start_transaction():
                snapshots.insert_many(
                    [{"run_id": run_id, "captured_at": datetime.now(timezone.utc), "source_doc": doc} for doc in before],
                    session=session,
                )
                for object_id, values in updates:
                    result = collection.update_one({"_id": object_id}, {"$set": values}, session=session)
                    if result.matched_count != 1:
                        raise RuntimeError(f"Failed to match source document {object_id}")
                result = collection.delete_many({"_id": {"$in": [doc["_id"] for doc in removed_docs]}}, session=session)
                if result.deleted_count != 29:
                    raise RuntimeError(f"Expected to archive/remove 29 documents, removed {result.deleted_count}")
        collection.create_index([("id", ASCENDING)], unique=True, name="unique_traffic_sign_id")
        after = list(collection.find({}))
        if len(after) != 311 or len({doc.get("id") for doc in after}) != 311:
            raise RuntimeError("Post-write validation failed")
        after_by_id = {doc["id"]: doc for doc in after}
        for row in catalog:
            doc = after_by_id[row["id"]]
            if doc.get("name") != row["name"] or doc.get("image_url") != images[row["id"]]:
                raise RuntimeError(f"Post-write mismatch for {row['id']}")
        report["after"] = {"documents": len(after), "unique_ids": len(after_by_id), "verified_matches": 311}

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("run_id", "mode", "before", "planned")}, ensure_ascii=False, indent=2))
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
