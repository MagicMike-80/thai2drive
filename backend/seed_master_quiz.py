"""Modul for automatisk seeding/upsert av Master Quiz-katalogen til MongoDB."""

import json
import logging
from pathlib import Path
from typing import Any, Optional
from pymongo import UpdateOne

logger = logging.getLogger("master_quiz_seed")

DEFAULT_PAYLOAD_PATH = (
    Path(__file__).resolve().parent
    / "content_packs"
    / "thai2drive_master_quiz_production_payload.json"
)

VALID_AREAS = {
    "right_of_way",
    "lane_positioning",
    "interaction",
    "speed_distance",
    "road_conditions",
    "traffic_signs",
    "other_topics",
}

def build_master_quiz_operations(payload_path: Optional[Path] = None) -> list[UpdateOne]:
    """Bygger idempotente UpdateOne operasjoner for de 239 Master Quiz-spørsmålene."""
    target_path = payload_path or DEFAULT_PAYLOAD_PATH
    if not target_path.is_file():
        logger.warning("Fant ikke payload-fil: %s", target_path)
        return []

    data = json.loads(target_path.read_text(encoding="utf-8")).get("questions", [])
    if not data:
        logger.warning("Ingen spørsmål i payload: %s", target_path)
        return []

    operations = []
    for q in data:
        doc_id = q.get("id")
        if not doc_id:
            continue
        update_fields = {k: v for k, v in q.items() if k != "id"}
        operations.append(
            UpdateOne(
                {"id": doc_id},
                {
                    "$set": update_fields,
                    "$setOnInsert": {"id": doc_id, "created_at": q.get("updated_at")},
                },
                upsert=True,
            )
        )
    return operations

async def seed_master_quiz_collection(
    collection: Any,
    payload_path: Optional[Path] = None,
) -> dict[str, int]:
    """Seeder de 239 Master Quiz-spørsmålene asynkront inn i MongoDB via Motor."""
    operations = build_master_quiz_operations(payload_path)
    if not operations:
        return {"matched": 0, "upserted": 0, "modified": 0, "total": 0}

    res = await collection.bulk_write(operations, ordered=False)
    matched = getattr(res, "matched_count", 0)
    upserted = len(getattr(res, "upserted_ids", {})) or getattr(res, "upserted_count", 0)
    modified = getattr(res, "modified_count", 0)

    logger.info(
        "Master Quiz seeding ferdig: matched=%d, upserted=%d, modified=%d, total=%d",
        matched,
        upserted,
        modified,
        len(operations),
    )
    return {
        "matched": matched,
        "upserted": upserted,
        "modified": modified,
        "total": len(operations),
    }

def seed_master_quiz_sync(
    collection: Any,
    payload_path: Optional[Path] = None,
) -> dict[str, int]:
    """Seeder de 239 Master Quiz-spørsmålene synkront inn i MongoDB via PyMongo."""
    operations = build_master_quiz_operations(payload_path)
    if not operations:
        return {"matched": 0, "upserted": 0, "modified": 0, "total": 0}

    res = collection.bulk_write(operations, ordered=False)
    matched = getattr(res, "matched_count", 0)
    upserted = len(getattr(res, "upserted_ids", {})) or getattr(res, "upserted_count", 0)
    modified = getattr(res, "modified_count", 0)
    return {
        "matched": matched,
        "upserted": upserted,
        "modified": modified,
        "total": len(operations),
    }
