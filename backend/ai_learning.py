"""
AI Learning Engine for Thai2Drive
----------------------------------
Pure-analytics layer — zero LLM cost.

Responsibilities:
  • Record every question attempt with timing data
  • SM-2 spaced repetition scheduling
  • Category weakness detection
  • Exam readiness score calculation
  • Personalized coaching messages (template-based)
  • Adaptive (smart) practice queue

Collections used:
  ai_attempts     – every individual answer event
  ai_srs_cards    – per-user per-question SRS state
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from math import ceil
from typing import Optional

logger = logging.getLogger("ai_learning")

# ─── Constants ────────────────────────────────────────────────────────────────
# SRS intervals in days
_INTERVAL_NEW_CORRECT = 1       # first correct: review in 1 day
_INTERVAL_2ND_CORRECT = 3       # second correct: 3 days
_INTERVAL_3RD_CORRECT = 7       # third: 1 week
_INTERVAL_AFTER_4TH   = 14     # stable: 2 weeks
_INTERVAL_WRONG       = 1       # always review wrong in 1 day
_INTERVAL_WRONG_FAST  = 0.007   # ~10 min, expressed as fraction of a day

_SRS_EF_START  = 2.5
_SRS_EF_MIN    = 1.3
_SRS_EF_DROP   = 0.2  # subtracted from EF on wrong answer

# Exam readiness thresholds
_READY_EXCELLENT = 85
_READY_GOOD      = 70
_READY_FAIR      = 55

# Coaching templates — keyed by language
_COACHING = {
    "no": {
        "weak_cat":    "Du sliter mest med: {}. Fokuser litt ekstra der.",
        "good_cat":    "Sterk kategori: {}. Bra jobbet!",
        "low_acc":     "Nøyaktigheten din er {:.0f}%. Prøv å repetera de feilede spørsmålene.",
        "mid_acc":     "Du er på {} %. Øv litt til på svake kategorier, så klarer du teorien.",
        "high_acc":    "Imponerende! {} % nøyaktighet. Du er nesten eksamensmoden!",
        "exam_ready":  "🎉 Du er eksamensmoden! {} % nøyaktighet. Lykke til på teorien!",
        "srs_due":     "Du har {} spørsmål klare for spaced-repetition. Ta dem nå!",
        "keep_going":  "Fortsett å øve! Regelmessig praksis er nøkkelen til suksess.",
        "improving":   "Bra fremgang! Du forbedrer deg jevnt.",
        "streak":      "🔥 {} dager på rad! Hold momentum!",
        "new_user":    "Velkommen! Start med å svare på noen spørsmål for å se læringsanalysen din.",
    },
    "th": {
        "weak_cat":    "คุณยังอ่อนในหมวด: {} ลองฝึกเพิ่มในหมวดนั้น",
        "good_cat":    "หมวดที่แข็งแกร่ง: {} ทำได้ดีมาก!",
        "low_acc":     "ความแม่นยำของคุณ {:.0f}% ลองทบทวนคำถามที่ตอบผิด",
        "mid_acc":     "คุณทำได้ {}% แล้ว! ฝึกหมวดที่อ่อนอีกสักหน่อย",
        "high_acc":    "ยอดเยี่ยม! {}% ความแม่นยำ ใกล้พร้อมสอบแล้ว!",
        "exam_ready":  "🎉 พร้อมสอบแล้ว! {}% ความแม่นยำ โชคดีนะ!",
        "srs_due":     "มี {} คำถามรอการทบทวน ทำเลย!",
        "keep_going":  "สู้ต่อไป! การฝึกสม่ำเสมอคือกุญแจสู่ความสำเร็จ",
        "improving":   "พัฒนาขึ้นเรื่อยๆ ทำต่อไปนะ!",
        "streak":      "🔥 {} วันติดต่อกัน! ยอดเยี่ยม!",
        "new_user":    "ยินดีต้อนรับ! เริ่มตอบคำถามเพื่อดูการวิเคราะห์การเรียนรู้ของคุณ",
    },
    "en": {
        "weak_cat":    "You struggle most with: {}. Focus extra practice there.",
        "good_cat":    "Strong category: {}. Great work!",
        "low_acc":     "Your accuracy is {:.0f}%. Try reviewing the questions you got wrong.",
        "mid_acc":     "You're at {}%. A bit more practice on weak categories and you'll nail it.",
        "high_acc":    "Impressive! {}% accuracy. You're almost exam-ready!",
        "exam_ready":  "🎉 You're exam-ready! {}% accuracy. Good luck!",
        "srs_due":     "You have {} questions ready for spaced repetition. Do them now!",
        "keep_going":  "Keep going! Regular practice is the key to success.",
        "improving":   "Great progress! You're improving steadily.",
        "streak":      "🔥 {} day streak! Keep the momentum!",
        "new_user":    "Welcome! Start answering questions to see your learning insights.",
    },
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _lang(lang: str) -> dict:
    return _COACHING.get(lang, _COACHING["en"])


# ─── SM-2 Core ────────────────────────────────────────────────────────────────

def sm2_update(card: dict, is_correct: bool) -> dict:
    """
    Apply SM-2 update to an SRS card dict.
    Returns a new dict with updated fields.
    """
    ef    = card.get("ease_factor", _SRS_EF_START)
    reps  = card.get("repetitions", 0)
    inter = card.get("interval", 0)

    if is_correct:
        if reps == 0:
            inter = _INTERVAL_NEW_CORRECT
        elif reps == 1:
            inter = _INTERVAL_2ND_CORRECT
        elif reps == 2:
            inter = _INTERVAL_3RD_CORRECT
        elif reps >= 3:
            inter = _INTERVAL_AFTER_4TH
        else:
            inter = ceil(inter * ef)
        reps += 1
    else:
        ef    = max(_SRS_EF_MIN, ef - _SRS_EF_DROP)
        reps  = 0
        inter = _INTERVAL_WRONG

    next_review = _now() + timedelta(days=inter)
    return {
        **card,
        "ease_factor":   ef,
        "repetitions":   reps,
        "interval":      inter,
        "next_review":   next_review.isoformat(),
        "last_review":   _now().isoformat(),
    }


# ─── Attempt Recording ────────────────────────────────────────────────────────

async def record_attempt(
    db,
    device_id: str,
    question_id: str,
    is_correct: bool,
    time_taken_ms: int,
    category: str,
    mode: str,
    difficulty: str = "medium",
) -> dict:
    """
    Persist a single question attempt and update the SRS card.
    Returns the updated SRS card.
    """
    now = _now()

    # 1. Log the attempt
    attempt_doc = {
        "device_id":    device_id,
        "question_id":  question_id,
        "is_correct":   is_correct,
        "time_taken_ms": time_taken_ms,
        "category":     category,
        "difficulty":   difficulty,
        "mode":         mode,
        "timestamp":    now.isoformat(),
    }
    await db.ai_attempts.insert_one(attempt_doc)

    # 2. Update SRS card
    card = await db.ai_srs_cards.find_one(
        {"device_id": device_id, "question_id": question_id}, {"_id": 0}
    ) or {
        "device_id":   device_id,
        "question_id": question_id,
        "category":    category,
        "ease_factor": _SRS_EF_START,
        "repetitions": 0,
        "interval":    0,
        "next_review": now.isoformat(),
        "last_review": None,
    }

    updated = sm2_update(card, is_correct)

    await db.ai_srs_cards.update_one(
        {"device_id": device_id, "question_id": question_id},
        {"$set": updated},
        upsert=True,
    )

    return updated


# ─── Analytics ────────────────────────────────────────────────────────────────

async def get_category_stats(db, device_id: str) -> list[dict]:
    """Return per-category accuracy stats from ai_attempts."""
    pipeline = [
        {"$match": {"device_id": device_id}},
        {"$group": {
            "_id":     "$category",
            "total":   {"$sum": 1},
            "correct": {"$sum": {"$cond": ["$is_correct", 1, 0]}},
            "avg_time":{"$avg": "$time_taken_ms"},
        }},
        {"$project": {
            "_id":      0,
            "category": "$_id",
            "total":    1,
            "correct":  1,
            "avg_time": 1,
            "accuracy": {"$cond": [
                {"$gt": ["$total", 0]},
                {"$multiply": [{"$divide": ["$correct", "$total"]}, 100]},
                0,
            ]},
        }},
        {"$sort": {"accuracy": 1}},
    ]
    return await db.ai_attempts.aggregate(pipeline).to_list(50)


async def get_recent_accuracy(db, device_id: str, n: int = 30) -> float:
    """Accuracy over the last n attempts."""
    docs = await db.ai_attempts.find(
        {"device_id": device_id},
        {"is_correct": 1}
    ).sort("timestamp", -1).limit(n).to_list(n)

    if not docs:
        return 0.0
    return sum(1 for d in docs if d["is_correct"]) / len(docs) * 100


async def get_total_attempts(db, device_id: str) -> int:
    return await db.ai_attempts.count_documents({"device_id": device_id})


async def get_srs_due_count(db, device_id: str) -> int:
    now = _now().isoformat()
    return await db.ai_srs_cards.count_documents({
        "device_id":   device_id,
        "next_review": {"$lte": now},
    })


async def get_improvement_trend(db, device_id: str) -> str:
    """
    Compare last 10 vs previous 10 attempts.
    Returns 'improving', 'declining', or 'stable'.
    """
    docs = await db.ai_attempts.find(
        {"device_id": device_id}, {"is_correct": 1}
    ).sort("timestamp", -1).limit(20).to_list(20)

    if len(docs) < 10:
        return "stable"

    recent   = sum(1 for d in docs[:10]  if d["is_correct"]) / 10 * 100
    previous = sum(1 for d in docs[10:] if d["is_correct"]) / len(docs[10:]) * 100

    delta = recent - previous
    if delta >= 8:
        return "improving"
    if delta <= -8:
        return "declining"
    return "stable"


def compute_exam_readiness(
    recent_accuracy: float,
    total_attempts: int,
    category_stats: list[dict],
    all_categories: list[str],
) -> int:
    """
    Compute a 0-100 exam readiness score.
    Weights:
      50% – recent accuracy (last 30 questions)
      30% – category coverage (how many categories you've practiced with ≥5 correct)
      20% – volume factor (min(total/80, 1))
    """
    # Volume factor (0-1)
    volume_factor = min(total_attempts / 80, 1.0)

    # Category coverage (0-1)
    if all_categories:
        cat_accuracy = {s["category"]: s["accuracy"] for s in category_stats}
        covered = sum(
            1 for cat in all_categories
            if cat_accuracy.get(cat, 0) >= 60
        )
        coverage_factor = covered / len(all_categories)
    else:
        coverage_factor = 0.0

    # Weighted score
    score = (
        recent_accuracy * 0.50
        + coverage_factor * 100 * 0.30
        + volume_factor  * 100 * 0.20
    )
    return max(0, min(100, round(score)))


# ─── Coaching Messages ────────────────────────────────────────────────────────

def build_coaching_messages(
    lang: str,
    total_attempts: int,
    recent_accuracy: float,
    category_stats: list[dict],
    srs_due: int,
    trend: str,
    streak: int = 0,
) -> list[str]:
    """Generate 2-4 personalized coaching messages. No LLM cost."""
    T = _lang(lang)
    msgs: list[str] = []

    if total_attempts < 5:
        msgs.append(T["new_user"])
        return msgs

    # Accuracy-based message
    acc = round(recent_accuracy)
    if recent_accuracy >= _READY_EXCELLENT:
        msgs.append(T["exam_ready"].format(acc))
    elif recent_accuracy >= _READY_GOOD:
        msgs.append(T["high_acc"].format(acc))
    elif recent_accuracy >= _READY_FAIR:
        msgs.append(T["mid_acc"].format(acc))
    else:
        msgs.append(T["low_acc"].format(recent_accuracy))

    # Weak/strong category
    if category_stats:
        weak = [s for s in category_stats if s["total"] >= 3 and s["accuracy"] < 60]
        strong = [s for s in reversed(category_stats) if s["total"] >= 3 and s["accuracy"] >= 80]

        if weak:
            msgs.append(T["weak_cat"].format(weak[0]["category"]))
        if strong:
            msgs.append(T["good_cat"].format(strong[0]["category"]))

    # SRS
    if srs_due >= 3:
        msgs.append(T["srs_due"].format(srs_due))

    # Trend
    if trend == "improving":
        msgs.append(T["improving"])

    # Streak
    if streak >= 3:
        msgs.append(T["streak"].format(streak))

    # Always keep_going if nothing else
    if len(msgs) < 2:
        msgs.append(T["keep_going"])

    return msgs[:4]  # max 4 messages


# ─── Smart Practice Queue ─────────────────────────────────────────────────────

async def get_smart_practice_ids(
    db,
    device_id: str,
    count: int = 10,
    exclude_ids: Optional[list[str]] = None,
) -> list[str]:
    """
    Build an ordered list of question IDs for a smart practice session:
      1. SRS cards due now (highest priority)
      2. Questions from weak categories (accuracy < 60%, ≥ 3 attempts)
      3. Questions not yet seen
    Returns up to `count` question IDs.
    """
    exclude = set(exclude_ids or [])
    result: list[str] = []

    # 1. SRS due
    now_str = _now().isoformat()
    due_cards = await db.ai_srs_cards.find(
        {"device_id": device_id, "next_review": {"$lte": now_str}},
        {"question_id": 1}
    ).sort("next_review", 1).limit(count).to_list(count)

    for c in due_cards:
        qid = c["question_id"]
        if qid not in exclude and len(result) < count:
            result.append(qid)
            exclude.add(qid)

    if len(result) >= count:
        return result

    # 2. Weak categories
    cat_stats = await get_category_stats(db, device_id)
    weak_cats = [s["category"] for s in cat_stats if s["total"] >= 3 and s["accuracy"] < 60]

    if weak_cats:
        # Get question IDs from weak categories, excluding already-selected
        seen_ids = [c["question_id"] for c in await db.ai_srs_cards.find(
            {"device_id": device_id}, {"question_id": 1}
        ).to_list(5000)]

        for cat in weak_cats[:3]:  # max 3 weak categories
            needed = count - len(result)
            if needed <= 0:
                break
            qs = await db.questions.aggregate([
                {"$match": {
                    "category": cat,
                    "id": {"$nin": list(exclude)},
                    "bildeUrl": {"$exists": True, "$nin": [None, ""]},
                }},
                {"$sample": {"size": needed}},
                {"$project": {"id": 1}},
            ]).to_list(needed)
            for q in qs:
                qid = q.get("id") or str(q.get("_id", ""))
                if qid and qid not in exclude and len(result) < count:
                    result.append(qid)
                    exclude.add(qid)

    if len(result) >= count:
        return result

    # 3. Random unseen questions
    needed = count - len(result)
    seen_qids = [c["question_id"] for c in await db.ai_srs_cards.find(
        {"device_id": device_id}, {"question_id": 1}
    ).to_list(5000)]

    unseen = await db.questions.aggregate([
        {"$match": {
            "id": {"$nin": seen_qids + list(exclude)},
            "bildeUrl": {"$exists": True, "$nin": [None, ""]},
        }},
        {"$sample": {"size": needed}},
        {"$project": {"id": 1}},
    ]).to_list(needed)

    for q in unseen:
        qid = q.get("id") or str(q.get("_id", ""))
        if qid and qid not in exclude and len(result) < count:
            result.append(qid)

    return result


# ─── Full Dashboard ───────────────────────────────────────────────────────────

async def get_dashboard(db, device_id: str, lang: str = "no", streak: int = 0) -> dict:
    """
    Compile all AI learning data for the dashboard endpoint.
    """
    # Fetch all categories from questions collection for coverage calculation
    cat_docs = await db.questions.distinct("category")
    all_categories = [c for c in cat_docs if c]

    total_attempts    = await get_total_attempts(db, device_id)
    recent_accuracy   = await get_recent_accuracy(db, device_id)
    category_stats    = await get_category_stats(db, device_id)
    srs_due           = await get_srs_due_count(db, device_id)
    trend             = await get_improvement_trend(db, device_id)
    exam_readiness    = compute_exam_readiness(
        recent_accuracy, total_attempts, category_stats, all_categories
    )
    coaching          = build_coaching_messages(
        lang, total_attempts, recent_accuracy, category_stats, srs_due, trend, streak
    )

    # Derive weakest / strongest (min 3 attempts for validity)
    valid_cats  = [s for s in category_stats if s["total"] >= 3]
    weakest     = valid_cats[0]["category"]   if valid_cats else None
    strongest   = valid_cats[-1]["category"]  if valid_cats else None

    return {
        "exam_readiness":   exam_readiness,
        "total_attempts":   total_attempts,
        "recent_accuracy":  round(recent_accuracy, 1),
        "trend":            trend,
        "weakest_category": weakest,
        "strongest_category": strongest,
        "category_stats":   category_stats,
        "srs_due_count":    srs_due,
        "coaching_messages": coaching,
        "all_categories":   all_categories,
    }
