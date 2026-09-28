"""
quiz_terms.py — Fagordkortet ("📖 ดูคำศัพท์นอร์เวย์") glossary term lookup
--------------------------------------------------------------------------
GET /api/quiz/terms?question_id=<id>&lang=<no|th|en>

Matches a quiz question against the learning_glossary collection and returns
up to 4 relevant Norwegian traffic terms. Fail-stop language purity: a term
is only included if it has a non-empty definition in the requested language —
never a fallback to another language. Per the current UI (webapp.py), this
endpoint is only called with lang=th; no/en are supported by the contract but
unused today.
"""
from __future__ import annotations

import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("quiz_terms")

# ─── MongoDB ─────────────────────────────────────────────────────────────────
# Fail-soft: manglende MONGO_URL skal logges, ikke drepe importen av server.py.
_mongo_url = os.environ.get("MONGO_URL")
if not _mongo_url:
    logger.critical("MONGO_URL mangler — quiz_terms får ingen databasetilgang.")
    _mongo_url = "mongodb://127.0.0.1:27017"
_mongo = AsyncIOMotorClient(_mongo_url)
_db = _mongo[os.environ.get("DB_NAME") or "thai2drive"]

quiz_terms_router = APIRouter()

_GLOSSARY_CACHE: list[dict] = []
_CACHE_LOADED_AT: Optional[datetime] = None

# Which glossary field must be non-empty for a term to qualify for a given lang.
# The returned payload always carries definition_th (see _filter_language_purity) —
# only th is wired up in the UI today, but the purity check is defined for all three
# languages so a future no/en caller degrades safely instead of leaking a fallback.
_LANG_DEFINITION_FIELD = {"no": "definition_no", "th": "definition_th", "en": "definition_en"}


def _term_match_keys(doc: dict) -> dict:
    return {
        "term_key": (doc.get("term_no") or "").strip().lower(),
        "tag_keys": {t.strip().lower() for t in doc.get("topic_tags", []) if t},
    }


async def load_glossary_cache(db) -> None:
    """Load active glossary terms into the module-level cache. Fail-soft:
    on error, leave the previous cache in place (empty cache = endpoint
    answers {"terms": []}, never a 500)."""
    global _GLOSSARY_CACHE, _CACHE_LOADED_AT, _db
    if db is not None:
        _db = db
    try:
        docs = await db.learning_glossary.find({"active": True}, {"_id": 0}).to_list(100)
        for doc in docs:
            doc["_match"] = _term_match_keys(doc)
        _GLOSSARY_CACHE = docs
        _CACHE_LOADED_AT = datetime.now(timezone.utc)
    except Exception as exc:
        logger.error("Glossary cache load failed: %s", exc)


def _match_terms(question: dict, cache: list[dict]) -> list[dict]:
    """Score cache terms against a question's Norwegian text + category.
    Text match (whole word, æøå-safe) = weight 2. Tag match = weight 1.
    Sorted by weight desc, then term_no alphabetically. Capped to 4.
    """
    text = (question.get("question_text_no") or "").lower()
    cat = (question.get("category") or "").strip().lower()

    scored = []
    for doc in cache:
        match = doc.get("_match") or _term_match_keys(doc)
        term_key = match.get("term_key", "")
        tag_keys = match.get("tag_keys", set())

        weight = 0
        if term_key:
            pattern = r"(?<!\w)" + re.escape(term_key) + r"(?!\w)"
            if re.search(pattern, text):
                weight += 2
        if cat and cat in tag_keys:
            weight += 1

        if weight > 0:
            scored.append((weight, doc))

    scored.sort(key=lambda pair: (-pair[0], (pair[1].get("term_no") or "")))
    return [doc for _, doc in scored[:4]]


def _filter_language_purity(terms: list[dict], lang: str) -> list[dict]:
    """Drop any term missing a non-empty definition for `lang` — no fallback.
    The returned shape always carries definition_th only (per the API
    contract); definition_no/_en are never included in the response.
    """
    field = _LANG_DEFINITION_FIELD.get(lang, _LANG_DEFINITION_FIELD["th"])
    result = []
    for doc in terms:
        definition = doc.get(field)
        if not definition or not str(definition).strip():
            continue
        result.append({
            "id": doc.get("id"),
            "term_th": doc.get("term_th", ""),
            "term_no": doc.get("term_no", ""),
            "term_no_latin": doc.get("term_no", ""),
            "definition_th": doc.get("definition_th", ""),
            "topic_tags": doc.get("topic_tags", []),
        })
    return result


def _build_terms_response(question_id: str, question: Optional[dict], cache: list[dict], lang: str) -> dict:
    lang_resolved = lang if lang in _LANG_DEFINITION_FIELD else "th"
    if not question:
        return {"question_id": question_id, "lang": lang_resolved, "terms": []}
    matched = _match_terms(question, cache)
    terms = _filter_language_purity(matched, lang_resolved)
    return {"question_id": question_id, "lang": lang_resolved, "terms": terms}


@quiz_terms_router.get("/quiz/terms")
async def get_quiz_terms(question_id: str = Query(...), lang: str = Query("th")):
    global _GLOSSARY_CACHE, _db
    if not _GLOSSARY_CACHE and _db is not None:
        await load_glossary_cache(_db)
    question = None
    if _db is not None:
        try:
            query = {"$or": [{"id": question_id}]}
            if str(question_id).isdigit():
                query["$or"].append({"id": int(question_id)})
            question = await _db.questions.find_one(query, {"_id": 0})
        except Exception as exc:
            logger.warning("Failed to lookup question %s: %s", question_id, exc)
    response = _build_terms_response(question_id, question, _GLOSSARY_CACHE, lang)

    if response["terms"] and _db is not None:
        try:
            await _db.glossary_lookup_logs.insert_one({
                "id": str(uuid.uuid4()),
                "question_id": question_id,
                "lang": response["lang"],
                "term_ids": [t["id"] for t in response["terms"]],
                "term_count": len(response["terms"]),
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            logger.warning("glossary_lookup_logs insert failed: %s", exc)

    return response
