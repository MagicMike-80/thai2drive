"""
AI Explanation Generator for Thai2Drive
-----------------------------------------
Generates structured, pedagogically rich explanations for quiz questions.
Results are cached in MongoDB (ai_explanations collection) — the LLM is
called ONCE per question per language, then served from cache forever.

Explanation structure (all fields returned):
  why_correct            – why the correct answer is right
  why_wrong              – dict {optId: reason} for each wrong option
  important_rule         – the Norwegian traffic rule behind the question
  real_traffic_situation – a concrete traffic scene where this matters
  common_mistake         – what students most often confuse
  exam_tip               – what to look for in this type of exam question
  memory_rule            – a mnemonic or mental shortcut
  is_math                – True for speed/braking/reaction distance questions
  formula_explanation    – step-by-step formula breakdown (is_math only)
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone

import litellm

litellm.suppress_debug_info = True

logger = logging.getLogger("ai_explanations")

LLM_KEY   = os.environ.get("ANTHROPIC_API_KEY", "").strip()
LLM_MODEL = os.environ.get("EXPLAIN_LLM_MODEL", "claude-haiku-4-5-20251001")

# ─── Math question detection ──────────────────────────────────────────────────

_MATH_KEYWORDS = [
    "bremseavstand", "bremselengde", "reaksjonsavstand", "stoppeavstand",
    "km/t", "km/h", "meter per sekund", "fartsøkning", "fart",
    "braking distance", "reaction time", "stopping distance", "speed",
    "ระยะเบรก", "ระยะหยุด", "ความเร็ว",
]

def is_math_question(q_text_no: str, q_text_en: str = "") -> bool:
    combined = (q_text_no + " " + q_text_en).lower()
    return any(kw in combined for kw in _MATH_KEYWORDS)


# ─── Prompt builder ───────────────────────────────────────────────────────────

def _build_prompt(question_data: dict, lang: str) -> tuple[str, str]:
    """Return (system_prompt, user_message) for the explanation call."""
    lang_name = {"no": "Norwegian (Bokmål)", "th": "Thai", "en": "English"}.get(lang, "Norwegian")

    # Unpack question fields
    q_no = question_data.get("question", {}).get("no", "")
    q_en = question_data.get("question", {}).get("en", "") or q_no

    options = question_data.get("options", [])
    correct_id = question_data.get("correctOptionId", "A")

    opts_formatted = []
    for opt in options:
        oid   = opt.get("id", "")
        otext = opt.get("text", {}).get("no", "") or opt.get("text", {}).get("en", "")
        mark  = " ✓ CORRECT" if oid == correct_id else ""
        opts_formatted.append(f"  {oid}. {otext}{mark}")
    opts_str = "\n".join(opts_formatted)

    existing_expl = (
        question_data.get("explanation", {}).get("no", "")
        or question_data.get("explanation", {}).get("en", "")
    )

    is_math = is_math_question(q_no, q_en)

    system = f"""You are an expert Norwegian driving theory instructor who teaches in {lang_name}.

Your task: generate a pedagogically rich, structured explanation for a Norwegian driving theory question.

RULES:
- Answer entirely in {lang_name}
- Be precise and practical — write like a real driving instructor
- Keep each field concise (1-3 sentences max, except formula_explanation)
- Do NOT repeat the question text in your answer
- Output ONLY valid JSON — no markdown, no code fences, nothing else

JSON format to return:
{{
  "why_correct": "<Clear reason why the correct answer is right>",
  "why_wrong": {{
    "<optId>": "<Why this option is wrong — one sentence>",
    ... (only for WRONG options)
  }},
  "important_rule": "<The specific Norwegian traffic law or rule behind this>",
  "real_traffic_situation": "<A concrete 1-2 sentence real-life traffic scenario>",
  "common_mistake": "<The most common error students make on this type of question>",
  "exam_tip": "<Specific tip for recognizing and answering this question type in an exam>",
  "memory_rule": "<A short mnemonic or memory trick — or empty string if none applies>",
  "is_math": {"true" if is_math else "false"},
  "formula_explanation": "<Step-by-step calculation with units — ONLY if is_math is true, else empty string>"
}}"""

    user = f"""Question: {q_no}

Options:
{opts_str}

Existing explanation hint (do not copy verbatim, use as context only):
{existing_expl}

Generate the JSON explanation now."""

    return system, user


# ─── LLM call ─────────────────────────────────────────────────────────────────

_FALLBACK_EXPLANATION = {
    "why_correct":            "",
    "why_wrong":              {},
    "important_rule":         "",
    "real_traffic_situation": "",
    "common_mistake":         "",
    "exam_tip":               "",
    "memory_rule":            "",
    "is_math":                False,
    "formula_explanation":    "",
    "_fallback":              True,
}


async def _generate_via_llm(question_data: dict, lang: str) -> dict:
    """Call the LLM and parse the JSON response. Returns fallback on any error."""
    if not LLM_KEY:
        logger.warning("ai_explanations: ANTHROPIC_API_KEY not configured — returning fallback")
        return {**_FALLBACK_EXPLANATION, "_error": "api_key_missing"}

    system, user = _build_prompt(question_data, lang)

    try:
        resp = await litellm.acompletion(
            model    = LLM_MODEL,
            messages = [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens = 800,
            api_key    = LLM_KEY,
        )
        raw = (resp.choices[0].message.content or "").strip()

        # Strip any accidental markdown fences
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$",       "", raw)

        data = json.loads(raw)
        return data

    except json.JSONDecodeError as e:
        logger.error("ai_explanations: JSON parse failed: %s", e)
        return {**_FALLBACK_EXPLANATION, "_error": "json_parse_failed"}
    except Exception as e:
        logger.error("ai_explanations: LLM call failed: %s", e)
        return {**_FALLBACK_EXPLANATION, "_error": str(e)[:200]}


# ─── Public API ───────────────────────────────────────────────────────────────

async def get_explanation(
    db,
    question_id: str,
    question_data: dict,
    lang: str = "no",
) -> dict:
    """
    Return a cached explanation, or generate + cache it if missing.

    question_data: normalized question dict (v2 schema with 'question', 'options',
                   'correctOptionId', 'explanation' keys).
    """
    lang = lang if lang in ("no", "th", "en") else "no"

    # Check cache
    cached = await db.ai_explanations.find_one(
        {"question_id": question_id, "lang": lang},
        {"_id": 0},
    )
    if cached:
        logger.debug("ai_explanations: cache hit qid=%s lang=%s", question_id, lang)
        return cached.get("explanation", _FALLBACK_EXPLANATION)

    # Generate
    logger.info("ai_explanations: generating qid=%s lang=%s model=%s", question_id, lang, LLM_MODEL)
    explanation = await _generate_via_llm(question_data, lang)

    # Cache (even fallbacks — mark with _fallback=True so client can decide)
    cache_doc = {
        "question_id":  question_id,
        "lang":         lang,
        "explanation":  explanation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model":        LLM_MODEL,
    }
    try:
        await db.ai_explanations.update_one(
            {"question_id": question_id, "lang": lang},
            {"$set": cache_doc},
            upsert=True,
        )
    except Exception as e:
        logger.warning("ai_explanations: cache write failed: %s", e)

    return explanation


async def invalidate_cache(db, question_id: str) -> int:
    """Delete all cached explanations for a question (e.g. after content update)."""
    result = await db.ai_explanations.delete_many({"question_id": question_id})
    return result.deleted_count
