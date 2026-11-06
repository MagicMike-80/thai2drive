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

PATCHED_RIGHT_OF_WAY_QUESTION = {
    "id": "e6b65e32-719d-4df5-bf69-ccae66e49746",
    "question": {
        "no": "Du kjører bil A og skal svinge til høyre i krysset. Bil B kommer fra høyre og skal rett fram. Hva gjelder for vikeplikten?",
        "th": "คุณขับรถ A และกำลังจะเลี้ยวขวาที่ทางแยก รถ B มาจากทางขวาและจะตรงไป กฎการให้ทางเป็นอย่างไร?",
        "en": "You are driving car A and turning right at the intersection. Car B is coming from the right and going straight. What applies regarding right of way?",
    },
    "options": [
        {
            "id": "A",
            "text": {
                "no": "Jeg har vikeplikt for bil B fordi bil B kommer fra høyre (høyreregelen)",
                "th": "ฉันต้องให้ทางแก่รถ B เพราะรถ B มาจากทางขวา (กฎให้ทางขวา)",
                "en": "I must yield to car B because car B is coming from the right (right-hand rule)",
            },
        },
        {
            "id": "B",
            "text": {
                "no": "Bil B har vikeplikt for meg fordi jeg skal svinge til høyre",
                "th": "รถ B ต้องให้ทางแก่ฉันเพราะฉันกำลังจะเลี้ยวขวา",
                "en": "Car B must yield to me because I am turning right",
            },
        },
        {
            "id": "C",
            "text": {
                "no": "Jeg har forkjørsrett fordi jeg kommer først inn i krysset",
                "th": "ฉันมีสิทธิ์ไปก่อนเพราะมาถึงทางแยกก่อน",
                "en": "I have the right of way because I arrived at the intersection first",
            },
        },
        {
            "id": "D",
            "text": {
                "no": "Bil B har vikeplikt fordi veien jeg kjører på har bedre standard",
                "th": "รถ B ต้องให้ทางเพราะถนนที่ฉันขับมีมาตรฐานดีกว่า",
                "en": "Car B must yield because the road I am driving on has better standard",
            },
        },
    ],
    "correctOptionId": "A",
    "explanation": {
        "no": "I et kryss uten skilt gjelder alltid høyreregelen (trafikkreglene § 7 nr. 1). Siden bil B kommer fra din høyre side, har du vikeplikt for bil B. Husk: Veistandard eller veibredde gir aldri forkjørsrett med mindre veien er skiltet med forkjørsveiskilt!",
        "th": "ในทางแยกที่ไม่มีป้ายจราจร จะใช้กฎให้ทางขวาเสมอ (กฎจราจรมาตรา 7 ข้อ 1) เนื่องจากรถ B มาจากทางขวามือของคุณ คุณจึงต้องให้ทางแก่รถ B จำไว้ว่า: ขนาดหรือมาตรฐานถนนไม่เคยให้สิทธิ์ไปก่อน เว้นแต่จะมีป้ายทางเอกกำกับไว้!",
        "en": "In an intersection without signs, the right-hand rule always applies (Traffic Rules § 7 no. 1). Since car B comes from your right, you must yield to car B. Remember: Road standard or width never gives right of way unless marked with a priority road sign!",
    },
    "law_reference": "Trafikkreglene § 7 nr. 1",
    "learning_area_id": "right_of_way",
    "category": "Right of Way",
    "validated": True,
}

def build_master_quiz_operations(payload_path: Optional[Path] = None) -> list[UpdateOne]:
    """Bygger idempotente UpdateOne operasjoner for de 239 Master Quiz-spørsmålene + rettelser."""
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

    # Korrigering for vikeplikt T-kryss (§ 7 nr. 1)
    row_fix = dict(PATCHED_RIGHT_OF_WAY_QUESTION)
    row_id = row_fix.pop("id")
    operations.append(
        UpdateOne(
            {"id": row_id},
            {"$set": row_fix},
            upsert=False,
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
