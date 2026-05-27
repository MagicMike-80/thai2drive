"""
create_indexes.py — MongoDB index management
---------------------------------------------
Run manually to verify or rebuild indexes:
    python create_indexes.py

Also called automatically on every Railway deploy via FastAPI startup event
in server.py. All operations are idempotent — safe to run multiple times.

Indexes are derived from actual query patterns in ai_learning.py.
See inline comments for which function each index covers.
"""
from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING

load_dotenv()
logger = logging.getLogger("create_indexes")


async def create_all_indexes(db) -> dict[str, list[str]]:
    """
    Create all indexes. Returns dict of collection → list of index names created.
    Idempotent: create_index is a no-op if the index already exists.
    """
    created: dict[str, list[str]] = {}

    # ── ai_attempts ────────────────────────────────────────────────────────────
    # Queries:
    #   get_total_attempts  → count_documents({device_id})
    #   get_recent_accuracy → find({device_id}).sort(timestamp,-1).limit(30)
    #   get_improvement_trend → find({device_id}).sort(timestamp,-1).limit(20)
    #   get_category_stats  → aggregate $match {device_id} + $group category
    await db.ai_attempts.create_index(
        [("device_id", ASCENDING), ("timestamp", DESCENDING)],
        background=True,
        name="device_time",
    )
    # category field on the same collection — covered by device_id prefix above
    # but an explicit compound index helps the $group stage in get_category_stats
    await db.ai_attempts.create_index(
        [("device_id", ASCENDING), ("category", ASCENDING)],
        background=True,
        name="device_category",
    )
    created["ai_attempts"] = ["device_time", "device_category"]

    # ── ai_srs_cards ───────────────────────────────────────────────────────────
    # Queries:
    #   record_attempt      → find_one({device_id, question_id}) + update_one upsert
    #   get_srs_due_count   → count_documents({device_id, next_review: {$lte: now}})
    #   get_smart_practice  → find({device_id, next_review: {$lte}}).sort(next_review).limit(N)
    #   get_smart_practice  → find({device_id}).to_list(5000)  — full user card list
    await db.ai_srs_cards.create_index(
        [("device_id", ASCENDING), ("question_id", ASCENDING)],
        unique=True,
        background=True,
        name="device_question_unique",
    )
    await db.ai_srs_cards.create_index(
        [("device_id", ASCENDING), ("next_review", ASCENDING)],
        background=True,
        name="device_review",
    )
    created["ai_srs_cards"] = ["device_question_unique", "device_review"]

    # ── ai_explanations ────────────────────────────────────────────────────────
    # Queries:
    #   get_explanation (ai_explanations.py) → find_one({question_id, lang}) + upsert
    await db.ai_explanations.create_index(
        [("question_id", ASCENDING), ("lang", ASCENDING)],
        unique=True,
        background=True,
        name="question_lang_unique",
    )
    created["ai_explanations"] = ["question_lang_unique"]

    # ── questions ──────────────────────────────────────────────────────────────
    # Queries:
    #   normalize_question / smart-practice → find({id: {$in: ids}})
    #   get_smart_practice  → aggregate $match {id: {$nin: seen}, bildeUrl: ...}
    #   get_dashboard       → distinct("category")
    #   category aggregate  → $match {category: cat, id: {$nin: ...}}
    await db.questions.create_index(
        [("id", ASCENDING)],
        background=True,
        name="question_id",
    )
    await db.questions.create_index(
        [("category", ASCENDING)],
        background=True,
        name="question_category",
    )
    created["questions"] = ["question_id", "question_category"]

    # -- access policy -----------------------------------------------------
    # Queries:
    #   /api/access/status  -> find_one({scope, key})
    #   /api/access/consume -> find_one({event_id}) for idempotent answer usage
    await db.access_usage.create_index(
        [("scope", ASCENDING), ("key", ASCENDING)],
        unique=True,
        background=True,
        name="scope_key_unique",
    )
    await db.access_events.create_index(
        [("event_id", ASCENDING)],
        unique=True,
        background=True,
        name="event_id_unique",
    )
    await db.access_events.create_index(
        [("scope", ASCENDING), ("key", ASCENDING), ("created_at", DESCENDING)],
        background=True,
        name="scope_key_time",
    )
    created["access_usage"] = ["scope_key_unique"]
    created["access_events"] = ["event_id_unique", "scope_key_time"]

    # -- billing -----------------------------------------------------------
    await db.checkout_sessions.create_index(
        [("stripe_session_id", ASCENDING)],
        unique=True,
        background=True,
        name="stripe_session_unique",
    )
    await db.subscriptions.create_index(
        [("user_id", ASCENDING), ("source", ASCENDING)],
        background=True,
        name="user_source",
    )
    await db.subscriptions.create_index(
        [("stripe_subscription_id", ASCENDING)],
        background=True,
        name="stripe_subscription",
    )
    await db.stripe_events.create_index(
        [("event_id", ASCENDING)],
        unique=True,
        background=True,
        name="stripe_event_unique",
    )
    created["checkout_sessions"] = ["stripe_session_unique"]
    created["subscriptions"] = ["user_source", "stripe_subscription"]
    created["stripe_events"] = ["stripe_event_unique"]

    return created


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    mongo_url = os.environ["MONGO_URL"]
    db_name   = os.environ.get("DB_NAME", "thai2drive")

    client = AsyncIOMotorClient(mongo_url)
    db     = client[db_name]

    logger.info("Connecting to %s / %s", mongo_url[:40] + "…", db_name)
    created = await create_all_indexes(db)

    for coll, indexes in created.items():
        logger.info("  %-20s → %s", coll, ", ".join(indexes))

    logger.info("Done. All indexes verified.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
