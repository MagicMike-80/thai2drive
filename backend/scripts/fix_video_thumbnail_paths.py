"""Audit or repair legacy learning-video thumbnail paths.

Dry-run is the default. Database writes require ``--apply``, an exact database
name confirmation and a snapshot directory. No document is ever deleted.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.video_thumbnails import normalize_video_thumbnail_url


THUMBNAIL_DIR = ROOT / "backend" / "public_assets" / "thumbs"
LEGACY_PATTERN = re.compile(r"^/api/assets/thumbs/thumb_video_[^/]+[.]jpg$")


def proposed_update(document: dict[str, Any]) -> str:
    current = str(document.get("thumbnail_url") or "").strip()
    if not LEGACY_PATTERN.fullmatch(current):
        return ""
    corrected = normalize_video_thumbnail_url(current, str(document.get("file_path") or ""))
    return corrected if corrected and corrected != current else ""


def target_file(url: str) -> Path:
    candidate = (THUMBNAIL_DIR / Path(url).name).resolve()
    candidate.relative_to(THUMBNAIL_DIR.resolve())
    return candidate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-db", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-db-name", default="")
    parser.add_argument("--snapshot-dir", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    local_files = sorted(THUMBNAIL_DIR.glob("thumb_*.jpg"))
    print(f"LOCAL VALIDATION: thumbnails={len(local_files)}; no database write")
    if not args.audit_db and not args.apply:
        return 0

    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / "backend" / ".env")
    except ImportError:
        pass

    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "thai2drive")
    if not mongo_url:
        raise SystemExit("MONGO_URL is required for database audit/apply")
    if args.apply and args.confirm_db_name != db_name:
        raise SystemExit("--confirm-db-name must exactly match DB_NAME")
    if args.apply and args.snapshot_dir is None:
        raise SystemExit("--snapshot-dir is required with --apply")

    from pymongo import MongoClient
    from bson import json_util

    collection = MongoClient(mongo_url, serverSelectionTimeoutMS=10000)[db_name]["learning_videos"]
    query = {"thumbnail_url": {"$regex": LEGACY_PATTERN.pattern}}
    candidates = list(collection.find(query))
    updates: list[tuple[dict[str, Any], str]] = []
    missing: list[str] = []
    for document in candidates:
        corrected = proposed_update(document)
        if not corrected or not target_file(corrected).is_file():
            missing.append(str(document.get("id") or document.get("_id")))
            continue
        updates.append((document, corrected))

    print(
        f"DATABASE AUDIT: candidates={len(candidates)}, "
        f"safe_updates={len(updates)}, missing_targets={len(missing)}"
    )
    if missing:
        raise SystemExit("fail-stop: one or more corrected thumbnail files are missing")
    if not args.apply:
        print("READ-ONLY AUDIT COMPLETE: no database write")
        return 0

    snapshot_path = args.snapshot_dir / f"video-thumbnails-before-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json_util.dumps(
            {
                "database": db_name,
                "captured_at": datetime.now(timezone.utc),
                "documents": [document for document, _ in updates],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    modified = 0
    for document, corrected in updates:
        result = collection.update_one(
            {"_id": document["_id"], "thumbnail_url": document["thumbnail_url"]},
            {"$set": {"thumbnail_url": corrected, "thumbnail_path_fixed_at": datetime.now(timezone.utc)}},
        )
        modified += int(result.modified_count or 0)
    remaining = collection.count_documents(query)
    if remaining:
        raise RuntimeError(f"post-apply verification failed: {remaining} legacy paths remain")
    print(f"APPLY COMPLETE: modified={modified}, remaining=0, snapshot={snapshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
