"""
AI Learning Routes — Thai2Drive
---------------------------------
All endpoints are prefixed /api/ai/* when mounted in server.py.

Endpoints:
  POST  /ai/attempt                    – record a question attempt
  GET   /ai/dashboard/{device_id}      – full learning analytics
  GET   /ai/explanation/{question_id}  – get/generate AI explanation
  GET   /ai/smart-practice/{device_id} – adaptive question queue
  GET   /ai/coaching/{device_id}       – coaching messages only (lightweight)
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import ai_learning
import ai_explanations

logger = logging.getLogger("ai_routes")

# ─── DB (own connection, same pattern as support_chat.py) ─────────────────────
# Fail-soft: manglende MONGO_URL skal logges, ikke drepe importen av server.py.
_mongo_url = os.environ.get("MONGO_URL")
if not _mongo_url:
    logger.critical("MONGO_URL mangler — AI-rutene får ingen databasetilgang.")
    _mongo_url = "mongodb://127.0.0.1:27017"
_mongo = AsyncIOMotorClient(_mongo_url)
_db    = _mongo[os.environ.get("DB_NAME") or "thai2drive"]

ai_router = APIRouter()


# ─── Models ───────────────────────────────────────────────────────────────────

class AttemptRequest(BaseModel):
    device_id:     str
    question_id:   str
    is_correct:    bool
    time_taken_ms: int = 0
    category:      str = ""
    mode:          str = "practice"
    difficulty:    str = "medium"


# ─── Endpoints ────────────────────────────────────────────────────────────────

@ai_router.post("/ai/attempt")
async def record_attempt(req: AttemptRequest):
    """
    Record a single question attempt and update SRS schedule.
    Called from the quiz screen after every answer check.
    """
    try:
        card = await ai_learning.record_attempt(
            db           = _db,
            device_id    = req.device_id,
            question_id  = req.question_id,
            is_correct   = req.is_correct,
            time_taken_ms= req.time_taken_ms,
            category     = req.category,
            mode         = req.mode,
            difficulty   = req.difficulty,
        )
        return {"ok": True, "srs_next_review": card.get("next_review")}
    except Exception as e:
        logger.error("record_attempt error: %s", e)
        # Non-fatal — quiz should never break because of analytics
        return {"ok": False, "error": str(e)[:120]}


@ai_router.get("/ai/dashboard/{device_id}")
async def get_dashboard(
    device_id: str,
    lang:   str = Query(default="no"),
    streak: int = Query(default=0),
):
    """
    Full AI learning dashboard for a user.
    Returns exam readiness, category stats, coaching messages, SRS info.
    """
    try:
        data = await ai_learning.get_dashboard(_db, device_id, lang, streak)
        return data
    except Exception as e:
        logger.error("get_dashboard error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/ai/explanation/{question_id}")
async def get_explanation(
    question_id: str,
    lang: str = Query(default="no"),
):
    """
    Get (or generate and cache) a structured AI explanation for a question.
    Fetches the question from MongoDB, then calls LLM if not cached.
    """
    # Load question from DB
    question = await _db.questions.find_one({"id": question_id}, {"_id": 0})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Normalize to v2 schema if needed
    from server import normalize_question
    question_data = normalize_question(dict(question))

    try:
        explanation = await ai_explanations.get_explanation(
            db            = _db,
            question_id   = question_id,
            question_data = question_data,
            lang          = lang,
        )
        return {
            "question_id": question_id,
            "lang":        lang,
            "explanation": explanation,
            "is_fallback": explanation.get("_fallback", False),
        }
    except Exception as e:
        logger.error("get_explanation error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/ai/smart-practice/{device_id}")
async def get_smart_practice(
    device_id: str,
    count: int = Query(default=10, le=30),
):
    """
    Return an ordered list of question IDs for a smart practice session.
    Priority: SRS due → weak categories → unseen questions.
    """
    try:
        ids = await ai_learning.get_smart_practice_ids(_db, device_id, count)

        if not ids:
            # fallback: random questions
            qs = await _db.questions.aggregate([
                {"$match": {"bildeUrl": {"$exists": True, "$nin": [None, ""]}}},
                {"$sample": {"size": count}},
                {"$project": {"id": 1}},
            ]).to_list(count)
            ids = [q.get("id") or str(q.get("_id", "")) for q in qs]

        # Fetch the full question objects (sorted by ids order)
        qs_docs = await _db.questions.find(
            {"id": {"$in": ids}},
            {"_id": 0}
        ).to_list(count)

        from server import normalize_question
        qs_by_id = {q.get("id"): normalize_question(q) for q in qs_docs}

        # Return in the smart order
        ordered = [qs_by_id[i] for i in ids if i in qs_by_id]

        srs_count = await _db.ai_srs_cards.count_documents({
            "device_id":   device_id,
            "next_review": {"$lte": ai_learning._now().isoformat()},
        })

        return {
            "questions":       ordered,
            "srs_due_count":   srs_count,
            "total_in_queue":  len(ordered),
        }
    except Exception as e:
        logger.error("get_smart_practice error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@ai_router.get("/ai/coaching/{device_id}")
async def get_coaching(
    device_id: str,
    lang:   str = Query(default="no"),
    streak: int = Query(default=0),
):
    """
    Lightweight endpoint — returns coaching messages only.
    Used by the home screen CoachBanner without the full dashboard load.
    """
    try:
        # All five queries are independent — run concurrently.
        # Sequential baseline: ~5 × 20 ms = ~100 ms.
        # Parallel: ~20 ms (slowest single query).
        total, acc, cats, srs_due, trend = await asyncio.gather(
            ai_learning.get_total_attempts(_db, device_id),
            ai_learning.get_recent_accuracy(_db, device_id),
            ai_learning.get_category_stats(_db, device_id),
            ai_learning.get_srs_due_count(_db, device_id),
            ai_learning.get_improvement_trend(_db, device_id),
        )

        msgs = ai_learning.build_coaching_messages(lang, total, acc, cats, srs_due, trend, streak)
        return {
            "messages":       msgs,
            "srs_due_count":  srs_due,
            "total_attempts": total,
        }
    except Exception as e:
        logger.error("get_coaching error: %s", e)
        return {"messages": [], "srs_due_count": 0, "total_attempts": 0}
