"""Remove only GridFS chunks whose parent file does not exist.

Dry-run is the default. Apply mode requires the verified full-backup manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient


def verify_backup(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    collection_dir = manifest_path.parent / "collections"
    errors = []
    for item in manifest.get("collections", []):
        path = collection_dir / f"{item['name']}.bson"
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            errors.append(item["name"])
    if errors or len(manifest.get("collections", [])) != 43 or manifest.get("total_documents") != 6594:
        raise RuntimeError(f"Backup verification failed: {errors or 'manifest totals'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-manifest", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.apply and not args.backup_manifest:
        parser.error("--apply requires --backup-manifest")
    if args.backup_manifest:
        verify_backup(args.backup_manifest)

    db = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    valid_file_ids = set(db.fs.files.distinct("_id"))
    orphans = list(db.fs.chunks.find({"files_id": {"$nin": list(valid_file_ids)}}, {"_id": 1, "files_id": 1, "n": 1, "data": 1}))
    orphan_bytes = sum(len(row.get("data", b"")) for row in orphans)
    if len(orphans) != 423 or orphan_bytes < 100 * 1024 * 1024:
        raise RuntimeError(f"Unexpected orphan baseline: count={len(orphans)}, bytes={orphan_bytes}")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "before": {"fs_files": db.fs.files.count_documents({}), "fs_chunks": db.fs.chunks.count_documents({})},
        "orphans": {
            "count": len(orphans),
            "logical_bytes": orphan_bytes,
            "logical_mb": round(orphan_bytes / 1048576, 3),
            "chunk_ids": [str(row["_id"]) for row in orphans],
        },
        "backup_manifest": str(args.backup_manifest) if args.backup_manifest else None,
    }
    if args.apply:
        result = db.fs.chunks.delete_many({"_id": {"$in": [row["_id"] for row in orphans]}})
        if result.deleted_count != len(orphans):
            raise RuntimeError(f"Expected {len(orphans)} deletions, got {result.deleted_count}")
        remaining_orphans = db.fs.chunks.count_documents({"files_id": {"$nin": list(valid_file_ids)}})
        if remaining_orphans:
            raise RuntimeError(f"Post-delete orphan validation failed: {remaining_orphans}")
        stats = db.command("dbStats", scale=1048576)
        report["after"] = {
            "fs_files": db.fs.files.count_documents({}),
            "fs_chunks": db.fs.chunks.count_documents({}),
            "remaining_orphans": remaining_orphans,
            "database_logical_mb": stats.get("dataSize"),
            "database_storage_mb": stats.get("storageSize"),
        }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("mode", "before", "orphans") if key in report} | ({"after": report["after"]} if "after" in report else {}), indent=2))


if __name__ == "__main__":
    main()
