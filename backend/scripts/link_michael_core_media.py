"""Safely link Michael's right-rule image after validating bus and sign sources.

Dry-run validates the planned record without opening MongoDB. ``--apply``
requires an exact database-name confirmation and writes a rollback snapshot.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RIGHT_RULE_MATERIAL: dict[str, Any] = {
    "id": "sit_kryss_hoyreregel_7",
    "type": "intersection_image",
    "source_id": "",
    "source_url": "/api/assets/michael_hoyreregel.svg",
    "title": {
        "no": "Høyreregelen i et kryss uten skilt",
        "th": "กฎให้ทางแก่รถจากขวาที่ทางแยกไม่มีป้าย",
        "en": "The right-hand rule at an unsigned intersection",
    },
    "caption": {
        "no": "I et likeverdig kryss der ingen skilt, signaler eller andre regler bestemmer, må du gi vikeplikt til kjøretøy fra høyre.",
        "th": "ที่ทางแยกซึ่งถนนมีลำดับความสำคัญเท่ากัน และไม่มีป้าย สัญญาณไฟ หรือกฎอื่นกำหนดสิทธิ์ทาง คุณต้องให้ทางแก่รถที่มาจากด้านขวา",
        "en": "At an equal-priority intersection where no sign, signal, or other rule decides, you must yield to vehicles approaching from the right.",
    },
    "topic_tags": [
        "7",
        "7_2",
        "vikeplikt",
        "høyreregel",
        "høyreregelen",
        "right-hand rule",
        "การให้ทาง",
    ],
    "sign_ids": [],
    "situation_tags": ["kryss", "uskiltet kryss", "intersection"],
    "active": True,
    "approved_for_michael": True,
    "priority": 10,
}

BUS_VIDEO_ID = "michael_vikeplikt_7_5a_buss"
BUS_MATERIAL_ID = "material_vikeplikt_7_5a_buss"
SIGN_ID = "202_0"
LANGUAGES = ("no", "th", "en")


def _snapshot_dumps(payload: dict[str, Any]) -> str:
    try:
        from bson import json_util
    except ModuleNotFoundError:
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return json_util.dumps(payload, indent=2)


def _snapshot_loads(payload: str) -> dict[str, Any]:
    try:
        from bson import json_util
    except ModuleNotFoundError:
        return json.loads(payload)
    return json_util.loads(payload)


def validate_material(material: dict[str, Any]) -> None:
    if material.get("type") != "intersection_image":
        raise RuntimeError("Right-rule material must be an intersection image")
    if not str(material.get("source_url", "")).startswith("/api/assets/"):
        raise RuntimeError("Right-rule material must use a local API asset")
    for field in ("title", "caption"):
        localized = material.get(field)
        if not isinstance(localized, dict) or any(
            not str(localized.get(language, "")).strip() for language in LANGUAGES
        ):
            raise RuntimeError(f"{field} must be complete for no/th/en")
    if not material.get("active") or not material.get("approved_for_michael"):
        raise RuntimeError("Right-rule material must be active and approved")


def _complete_localized(document: dict[str, Any], *fields: str) -> bool:
    for field in fields:
        localized = document.get(field)
        if not isinstance(localized, dict):
            return False
        if any(not str(localized.get(language, "")).strip() for language in LANGUAGES):
            return False
    return True


def verify_existing_sources(database: Any) -> dict[str, Any]:
    bus_video = database.learning_videos.find_one({"id": BUS_VIDEO_ID, "active": True})
    if not bus_video:
        raise RuntimeError("Active bus video is missing")
    bus_file_path = str(bus_video.get("file_path", "")).replace("\\", "/")
    bus_thumbnail_url = str(bus_video.get("thumbnail_url", ""))
    if bus_file_path != "/public_assets/video_vikeplikt_7_5a_buss.mp4":
        raise RuntimeError("Active bus video has an unexpected file path")
    if bus_thumbnail_url != "/api/assets/thumbs/thumb_vikeplikt_7_5a_buss.jpg":
        raise RuntimeError("Active bus video has an unexpected thumbnail path")
    if not {"no", "th"}.issubset(set(bus_video.get("learner_languages", []))):
        raise RuntimeError("Active bus video is not enabled for no/th learners")
    thai_subtitles = {
        str(track.get("url", ""))
        for track in bus_video.get("subtitle_tracks", [])
        if isinstance(track, dict) and track.get("lang") == "th"
    }
    if "/api/assets/subtitles/video_vikeplikt_7_5a_buss.th.vtt" not in thai_subtitles:
        raise RuntimeError("Active bus video has no approved Thai subtitle track")
    bus_material = database.michael_materials.find_one({
        "id": BUS_MATERIAL_ID,
        "type": "video",
        "active": True,
        "approved_for_michael": True,
    })
    if not bus_material or not _complete_localized(bus_material, "title", "caption"):
        raise RuntimeError("Approved multilingual bus material is missing")
    if bus_material.get("source_id") != BUS_VIDEO_ID:
        raise RuntimeError("Approved bus material is not linked to the active bus video")
    bus_tags = {str(tag).casefold() for tag in bus_material.get("topic_tags", [])}
    if not {"7_5", "bussregelen", "60_km_t"}.issubset(bus_tags):
        raise RuntimeError("Approved bus material is missing the § 7 no. 5 tags")
    for field in ("title", "caption"):
        if any("60" not in str(bus_material[field][language]) for language in LANGUAGES):
            raise RuntimeError("Approved bus material does not state the 60 km/h boundary")
    sign = database.traffic_signs.find_one({"id": SIGN_ID})
    if not sign or not str(sign.get("image_url", "")).startswith("/api/sign-images/"):
        raise RuntimeError("Traffic sign 202 has no API image")
    if not _complete_localized(sign, "name", "explanation", "driver_action"):
        raise RuntimeError("Traffic sign 202 is not complete for no/th/en")
    return {
        "bus_video": BUS_VIDEO_ID,
        "bus_material": BUS_MATERIAL_ID,
        "traffic_sign": SIGN_ID,
    }


def apply_link(database: Any, snapshot_dir: Path) -> dict[str, Any]:
    verify_existing_sources(database)
    existing = database.michael_materials.find_one({"id": RIGHT_RULE_MATERIAL["id"]})
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_path = snapshot_dir / f"michael_core_media_before_{stamp}.json"
    snapshot_path.write_text(
        _snapshot_dumps({
            "material_id": RIGHT_RULE_MATERIAL["id"],
            "existing": existing,
            "rollback": "replace_existing" if existing else "delete_inserted",
        }),
        encoding="utf-8",
    )
    document = {
        **RIGHT_RULE_MATERIAL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    update = {"$set": document}
    if not existing:
        update["$setOnInsert"] = {"created_at": document["updated_at"]}
    result = database.michael_materials.update_one(
        {"id": RIGHT_RULE_MATERIAL["id"]}, update, upsert=True
    )
    linked = database.michael_materials.find_one({
        "id": RIGHT_RULE_MATERIAL["id"],
        "active": True,
        "approved_for_michael": True,
    })
    if not linked:
        raise RuntimeError("Right-rule material was not linked after update")
    return {
        "matched": int(getattr(result, "matched_count", 0) or 0),
        "modified": int(getattr(result, "modified_count", 0) or 0),
        "upserted": bool(getattr(result, "upserted_id", None)),
        "snapshot": str(snapshot_path),
    }


def rollback_link(database: Any, snapshot_path: Path) -> dict[str, Any]:
    payload = _snapshot_loads(snapshot_path.read_text(encoding="utf-8"))
    if payload.get("material_id") != RIGHT_RULE_MATERIAL["id"]:
        raise RuntimeError("Snapshot does not belong to the right-rule material")
    existing = payload.get("existing")
    if existing is None:
        result = database.michael_materials.delete_one({"id": RIGHT_RULE_MATERIAL["id"]})
        return {"rollback": "delete_inserted", "deleted": int(result.deleted_count or 0)}
    result = database.michael_materials.replace_one(
        {"id": RIGHT_RULE_MATERIAL["id"]}, existing, upsert=True
    )
    return {
        "rollback": "replace_existing",
        "matched": int(result.matched_count or 0),
        "modified": int(result.modified_count or 0),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--apply", action="store_true")
    action.add_argument("--rollback-snapshot", type=Path)
    parser.add_argument("--confirm-db-name", default="")
    parser.add_argument("--snapshot-dir", type=Path, default=Path("seed_snapshots"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    validate_material(RIGHT_RULE_MATERIAL)
    if not args.apply and args.rollback_snapshot is None:
        print(json.dumps({"mode": "dry-run", "material": RIGHT_RULE_MATERIAL}))
        return 0

    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    except ImportError:
        pass
    mongo_url = os.environ.get("MONGO_URL", "").strip()
    db_name = os.environ.get("DB_NAME", "").strip()
    if not mongo_url or not db_name:
        raise RuntimeError("MONGO_URL and DB_NAME are required for --apply")
    if args.confirm_db_name != db_name:
        raise RuntimeError("--confirm-db-name must exactly match DB_NAME")

    from pymongo import MongoClient

    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    try:
        database = client[db_name]
        if args.rollback_snapshot is not None:
            result = rollback_link(database, args.rollback_snapshot)
            print(json.dumps({"mode": "rollback", "database": db_name, "result": result}))
        else:
            proof = verify_existing_sources(database)
            result = apply_link(database, args.snapshot_dir)
            print(json.dumps({"mode": "apply", "database": db_name, "proof": proof, "result": result}))
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
