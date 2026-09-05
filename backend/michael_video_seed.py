"""One-time, validated publication of Michael's bundled MP4 lesson catalog."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

try:
    from michael_video_import import (
        VIDEO_SPECS,
        learning_video_document,
        michael_material_document,
    )
except ImportError:  # package-style imports used by local tests
    from backend.michael_video_import import (
        VIDEO_SPECS,
        learning_video_document,
        michael_material_document,
    )


MIGRATION_ID = "michael_video_patch_a_2026_09_05_v1"
SUPPORTED_LANGUAGES = ("no", "th", "en")


def _validate_bundle(asset_root: Path) -> None:
    """Fail before touching MongoDB if any customer-facing asset is incomplete."""
    ids: set[str] = set()
    material_ids: set[str] = set()
    for spec in VIDEO_SPECS:
        if spec.video_id in ids or spec.material_id in material_ids:
            raise RuntimeError(f"Duplicate Michael video identity: {spec.slug}")
        ids.add(spec.video_id)
        material_ids.add(spec.material_id)
        for lang in SUPPORTED_LANGUAGES:
            if not str(spec.titles.get(lang, "")).strip():
                raise RuntimeError(f"Missing {lang} title for {spec.slug}")
            if not str(spec.captions.get(lang, "")).strip():
                raise RuntimeError(f"Missing {lang} caption for {spec.slug}")
        required = (
            asset_root / spec.asset_name,
            asset_root / "thumbs" / spec.thumbnail_name,
            asset_root / "subtitles" / spec.subtitle_name,
        )
        for path in required:
            if not path.is_file() or path.stat().st_size <= 0:
                raise RuntimeError(f"Missing Michael video asset: {path.name}")


async def seed_michael_video_catalog(db, asset_root: Path | None = None) -> dict:
    """Publish once, snapshot matching records first, and never delete content."""
    asset_root = asset_root or Path(__file__).resolve().parent / "public_assets"
    _validate_bundle(asset_root)

    migrations = db["content_migrations"]
    completed = await migrations.find_one({"_id": MIGRATION_ID, "status": "complete"})
    if completed:
        return {"status": "already-complete", "videos": len(VIDEO_SPECS)}

    video_ids = [spec.video_id for spec in VIDEO_SPECS]
    material_ids = [spec.material_id for spec in VIDEO_SPECS]
    old_videos = await db["learning_videos"].find({"id": {"$in": video_ids}}).to_list(length=100)
    old_materials = await db["michael_materials"].find({"id": {"$in": material_ids}}).to_list(length=100)
    now = datetime.now(timezone.utc)

    await db["content_migration_snapshots"].update_one(
        {"_id": MIGRATION_ID},
        {"$setOnInsert": {
            "created_at": now,
            "learning_videos": old_videos,
            "michael_materials": old_materials,
        }},
        upsert=True,
    )

    for spec in VIDEO_SPECS:
        video = learning_video_document(spec, publish=True)
        material = michael_material_document(spec, publish=True)
        await db["learning_videos"].update_one(
            {"id": video["id"]},
            {"$set": {**video, "updated_at": now}, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        await db["michael_materials"].update_one(
            {"id": material["id"]},
            {"$set": {**material, "updated_at": now}, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )

    await migrations.update_one(
        {"_id": MIGRATION_ID},
        {"$set": {
            "status": "complete",
            "completed_at": datetime.now(timezone.utc),
            "video_count": len(VIDEO_SPECS),
        }},
        upsert=True,
    )
    return {"status": "published", "videos": len(VIDEO_SPECS)}
