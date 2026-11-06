"""Back up and remove exactly 15 reviewed, unreferenced GridFS duplicates.

Dry-run by default. No database writes occur until all backups, hashes, and
reference checks pass. Never choose targets dynamically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import gridfs
from bson import ObjectId
from pymongo import MongoClient


# delete ID -> retained byte-identical ID
TARGETS = {
    "6ab36d65ecba151359b4d334": "6ab2908dc080ad60b8554984",
    "6ab36e36ecba151359b4d3c8": "6ab2908dc080ad60b8554984",
    "6ab36d31ecba151359b4d318": "6ab2ebc5ecba151359b4d265",
    "6ab36d52ecba151359b4d326": "6ab2ebc5ecba151359b4d265",
    "6ab36ddcecba151359b4d395": "6ab36dc0ecba151359b4d374",
    "6ab36e0eecba151359b4d3a7": "6ab36dc0ecba151359b4d374",
    "6ab36d81ecba151359b4d354": "6ab2e983ecba151359b4d200",
    "6ab36eb4ecba151359b4d411": "6ab28f4a2472b94fba81a63e",
    "6ab36f1becba151359b4d43f": "6ab28fd32472b94fba81a66e",
    "6ab36e6becba151359b4d3ec": "6ab28efa2472b94fba81a628",
    "6ab36e5aecba151359b4d3d8": "6ab28ea42472b94fba81a613",
    "6ab36f08ecba151359b4d42c": "6ab28fa42472b94fba81a65a",
    "6ab36d96ecba151359b4d364": "6ab36d7cecba151359b4d344",
    "6ab36e23ecba151359b4d3b9": "6ab36dc6ecba151359b4d386",
    "6ab36f28ecba151359b4d456": "6ab2902ac080ad60b8554975",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-db-name", default="")
    parser.add_argument("--backup-dir", type=Path,
                        default=Path("output/gridfs-approved-cleanup"))
    args = parser.parse_args()
    db_name = os.environ.get("DB_NAME", "").strip()
    mongo_url = os.environ.get("MONGO_URL", "").strip()
    if not db_name or not mongo_url:
        raise ValueError("MONGO_URL and DB_NAME are required")
    if args.apply and args.confirm_db_name != db_name:
        raise ValueError("--confirm-db-name must match DB_NAME")
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=15000)
    try:
        db = client[db_name]
        fs = gridfs.GridFS(db)
        target_ids = set(TARGETS)
        references = {media_id: set() for media_id in target_ids}
        for name in db.list_collection_names():
            if name in ("fs.files", "fs.chunks"):
                continue
            for row in db[name].find({}):
                serialized = str(row)
                for media_id in target_ids:
                    if media_id in serialized:
                        references[media_id].add(name)
        used = {key: sorted(value) for key, value in references.items() if value}
        if used:
            raise ValueError(f"target IDs have references: {used}")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = args.backup_dir / stamp
        manifest = []
        for delete_id, keep_id in TARGETS.items():
            doomed = fs.get(ObjectId(delete_id))
            kept = fs.get(ObjectId(keep_id))
            if doomed.filename != kept.filename or doomed.length != kept.length:
                raise ValueError(f"metadata differs for {delete_id}")
            doomed_bytes = doomed.read()
            digest = hashlib.sha256(doomed_bytes).hexdigest()
            if digest != hashlib.sha256(kept.read()).hexdigest():
                raise ValueError(f"bytes differ for {delete_id}")
            if args.apply:
                backup_dir.mkdir(parents=True, exist_ok=True)
                path = backup_dir / f"{delete_id}.bin"
                path.write_bytes(doomed_bytes)
                if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    raise RuntimeError(f"backup failed for {delete_id}")
            manifest.append({"delete_id": delete_id, "keep_id": keep_id,
                             "filename": doomed.filename, "length": doomed.length,
                             "sha256": digest})
        bytes_total = sum(item["length"] for item in manifest)
        print(f"PRECHECK OK database={db_name} targets={len(manifest)} "
              f"bytes={bytes_total} references=0")
        if not args.apply:
            return 0
        manifest_path = backup_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
        for item in manifest:
            fs.delete(ObjectId(item["delete_id"]))
            if db["fs.files"].count_documents({"_id": ObjectId(item["delete_id"])}) != 0:
                raise RuntimeError(f"delete failed for {item['delete_id']}")
        print(f"APPLY OK deleted={len(manifest)} bytes={bytes_total} backup={backup_dir}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
