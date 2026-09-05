"""Stage Michael learning videos and optionally upsert them into a local DB.

Safe defaults:
  python backend/scripts/import_michael_videos.py

Copies are explicit. Database writes are restricted to localhost and require a
snapshot directory. Publishing is an additional explicit flag.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.michael_video_import import (  # noqa: E402
    ASSET_DIR,
    EXCLUDED_DUPLICATES,
    THUMB_DIR,
    VIDEO_SPECS,
    learning_video_document,
    michael_material_document,
    source_path,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sources(workspace: Path) -> list[dict]:
    inventory = []
    seen_hashes: dict[str, str] = {}
    for spec in VIDEO_SPECS:
        source = source_path(workspace, spec)
        if not source.is_file():
            raise RuntimeError(f"Missing source video: {source}")
        digest = _sha256(source)
        if digest in seen_hashes:
            raise RuntimeError(
                f"Unexpected duplicate: {source.name} equals {seen_hashes[digest]}"
            )
        seen_hashes[digest] = source.name
        inventory.append({
            "id": spec.video_id,
            "source": str(source.relative_to(workspace)),
            "asset": spec.asset_name,
            "sha256": digest,
            "bytes": source.stat().st_size,
            "language": "no",
            "learner_languages": list(spec.learner_languages),
            "category": spec.category,
            "speed_limit": spec.speed_limit,
        })

    for duplicate_name, canonical_name in EXCLUDED_DUPLICATES.items():
        duplicate = workspace / "vikeplit mp4" / duplicate_name
        canonical = workspace / "vikeplit mp4" / canonical_name
        if not duplicate.is_file() or not canonical.is_file():
            raise RuntimeError("Expected duplicate source pair is incomplete")
        if _sha256(duplicate) != _sha256(canonical):
            raise RuntimeError(f"Excluded file is no longer a duplicate: {duplicate_name}")
    return inventory


def _thumbnail(path: Path, category: str, speed_limit: int | None) -> None:
    image = Image.new("RGB", (1280, 720), "#061426")
    draw = ImageDraw.Draw(image)
    accent = "#00E5FF" if category == "vikeplikt" else "#FF8A30"
    draw.rounded_rectangle((42, 42, 1238, 678), radius=42, outline=accent, width=10)
    draw.ellipse((490, 210, 790, 510), fill="#0B2844", outline=accent, width=8)
    draw.polygon(((610, 285), (610, 435), (740, 360)), fill=accent)
    if speed_limit:
        draw.ellipse((1000, 90, 1170, 260), fill="#FFFFFF", outline="#E5484D", width=14)
        draw.text((1060, 145), str(speed_limit), fill="#111827", stroke_width=1)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "JPEG", quality=88, optimize=True)


def _subtitle_text(spec) -> str:
    caption = " ".join(spec.captions["th"].replace("-->", "").split())
    return f"WEBVTT\n\n00:00:00.000 --> 00:00:09.800\n{caption}\n"


def copy_assets(workspace: Path) -> list[str]:
    copied = []
    asset_dir = workspace / ASSET_DIR
    thumb_dir = workspace / THUMB_DIR
    subtitle_dir = asset_dir / "subtitles"
    asset_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir.mkdir(parents=True, exist_ok=True)
    subtitle_dir.mkdir(parents=True, exist_ok=True)
    for spec in VIDEO_SPECS:
        source = source_path(workspace, spec)
        target = asset_dir / spec.asset_name
        if not target.exists() or _sha256(target) != _sha256(source):
            shutil.copy2(source, target)
            copied.append(str(target.relative_to(workspace)))
        thumb = thumb_dir / spec.thumbnail_name
        if not thumb.exists():
            _thumbnail(thumb, spec.category, spec.speed_limit)
            copied.append(str(thumb.relative_to(workspace)))
        subtitle = subtitle_dir / spec.subtitle_name
        subtitle_text = _subtitle_text(spec)
        if not subtitle.exists() or subtitle.read_text(encoding="utf-8") != subtitle_text:
            subtitle.write_text(subtitle_text, encoding="utf-8", newline="\n")
            copied.append(str(subtitle.relative_to(workspace)))
    return copied


def _local_mongo_uri() -> str:
    uri = os.environ.get("MONGO_URL", "").strip()
    allowed = ("mongodb://localhost", "mongodb://127.0.0.1", "mongodb://[::1]")
    if not uri.startswith(allowed):
        raise RuntimeError("Patch A permits only an explicit localhost MONGO_URL")
    return uri


def apply_local_database(database: str, snapshot_dir: Path, publish: bool) -> dict:
    if database not in {"thai2drive_dev", "thai2drive_test"}:
        raise RuntimeError("Database must be thai2drive_dev or thai2drive_test")
    from pymongo import MongoClient

    client = MongoClient(_local_mongo_uri(), serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    db = client[database]
    video_ids = [spec.video_id for spec in VIDEO_SPECS]
    material_ids = [spec.material_id for spec in VIDEO_SPECS]
    snapshot = {
        "database": database,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "learning_videos": list(db.learning_videos.find({"id": {"$in": video_ids}}, {"_id": 0})),
        "michael_materials": list(db.michael_materials.find({"id": {"$in": material_ids}}, {"_id": 0})),
    }
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / f"michael_video_patch_a_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    for spec in VIDEO_SPECS:
        video = learning_video_document(spec, publish=publish)
        material = michael_material_document(spec, publish=publish)
        now = datetime.now(timezone.utc).isoformat()
        video["updated_at"] = now
        material["updated_at"] = now
        db.learning_videos.replace_one({"id": video["id"]}, video, upsert=True)
        db.michael_materials.replace_one({"id": material["id"]}, material, upsert=True)
    return {"videos": len(VIDEO_SPECS), "materials": len(VIDEO_SPECS), "snapshot": str(snapshot_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copy-assets", action="store_true")
    parser.add_argument("--apply-db", action="store_true")
    parser.add_argument("--database", default="")
    parser.add_argument("--snapshot-dir", type=Path)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.publish and not args.apply_db:
        parser.error("--publish requires --apply-db")
    if args.apply_db and (not args.database or args.snapshot_dir is None):
        parser.error("--apply-db requires --database and --snapshot-dir")

    inventory = validate_sources(ROOT)
    result = {
        "mode": "local-apply" if (args.copy_assets or args.apply_db) else "dry-run",
        "unique_videos": len(inventory),
        "excluded_exact_duplicates": EXCLUDED_DUPLICATES,
        "publish": bool(args.publish),
        "inventory": inventory,
    }
    if args.copy_assets:
        result["copied"] = copy_assets(ROOT)
    if args.apply_db:
        result["database"] = apply_local_database(args.database, args.snapshot_dir, args.publish)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
