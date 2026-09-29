"""
dashboard.py — elevfremdrift for dashboardet (GET /api/dashboard/progress, GET /api/user/dashboard).

Betalende:  full visning — quiz per kategori, Studiebok per kapittel, skiltmestring, rekke.
Gratis:     begrenset visning — samlet quiz-score og samlet lesefremdrift; resten er låst
            (`locked`) og `upgrade.show_button` er true, så webappen viser oppgraderingsknappen.

Sikkerhet: svaret bygges FELT FOR FELT fra tall og id-er. Identiteten kommer ALLTID fra JWT
(`current_user["sub"]`) i ruten som kaller denne modulen — aldri fra en fri user_id/device_id i
URL-en. Brukerdokumentet (e-post, passordhash, Stripe/RevenueCat-id, tokens) spres aldri inn i
svaret uendret, og ingen andre brukeres data leses.

Språk: modulen selv sender bare tall og nøkler (kategorinøkkel, skilt-id). All tekst ligger i
webappens UI-ordbok (th = kun thai, norsk fagord i parentes).
"""

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Set

MASTERY_MIN_ANSWERS = 3      # et skilt regnes som mestret ved minst 3 svar ...
MASTERY_MIN_ACCURACY = 0.8   # ... og minst 80 % riktige
MAX_ATTEMPTS = 500           # de nyeste forsøkene som telles
_SIGN_IMG = re.compile(r"/sign-images/([^/]+?)(?:\.(?:jpe?g|png))?$", re.I)

LOCKED_FOR_FREE = ["quiz_by_category", "studybook_chapters", "signs"]


def compute_streak(days: Iterable[Any], today: Optional[date] = None) -> int:
    """Antall sammenhengende dager med aktivitet, telt bakover fra i dag (eller i går)."""
    today = today or datetime.now(timezone.utc).date()
    have: Set[date] = set()
    for d in days:
        if isinstance(d, datetime):
            have.add(d.date())
        elif isinstance(d, str) and len(d) >= 10:
            try:
                have.add(date.fromisoformat(d[:10]))
            except ValueError:
                pass
    cur = today if today in have else today - timedelta(days=1)
    n = 0
    while cur in have:
        n += 1
        cur -= timedelta(days=1)
    return n


def _pct(correct: int, total: int) -> int:
    return int(round(correct * 100 / total)) if total else 0


def sign_ids_of_question(q: dict, catalog_ids: Set[str]) -> Set[str]:
    """Skilt-id-ene et spørsmål handler om (kun id-er som finnes i skiltkatalogen)."""
    found: Set[str] = set()
    for key in ("sign_id", "traffic_sign_id"):
        if q.get(key):
            found.add(str(q[key]).strip())
    ids = q.get("sign_ids")
    if isinstance(ids, list):
        found.update(str(i).strip() for i in ids if i)
    if not found:
        m = _SIGN_IMG.search(str(q.get("bildeUrl") or q.get("image_url") or ""))
        if m:
            found.add(m.group(1).replace("%2F", "/"))
    return {i for i in found if i in catalog_ids}


async def recent_attempts(db, identities: List[dict]) -> List[dict]:
    cursor = db.quiz_attempts.find({"$or": identities}, {"_id": 0}).sort("completed_at", -1)
    return await cursor.to_list(MAX_ATTEMPTS)


async def studybook_progress(db, user_id: str, detailed: bool) -> Dict[str, Any]:
    chapters = await db.studiebok_chapters.find({}, {"_id": 0, "order": 1, "screens": 1}).sort("order", 1).to_list(200)
    doc = await db.user_studybook_progress.find_one({"user_id": user_id}, {"_id": 0}) or {}
    read_screens = set(doc.get("screens") or [])
    read_chapters = {int(c) for c in (doc.get("chapters") or []) if isinstance(c, int)}

    per_chapter = []
    total_units = read_units = 0
    for ch in chapters:
        order = ch.get("order")
        ids = [s.get("id") for s in (ch.get("screens") or []) if isinstance(s, dict) and s.get("id")]
        if ids:
            total, done = len(ids), sum(1 for i in ids if i in read_screens)
        else:  # eldre kapittel uten skjermer: ett steg
            total, done = 1, 1 if order in read_chapters else 0
        total_units += total
        read_units += done
        per_chapter.append({"chapter": order, "read": done, "total": total, "percent": _pct(done, total)})

    out: Dict[str, Any] = {
        "chapters_total": len(chapters),
        "chapters_started": sum(1 for c in per_chapter if c["read"]),
        "chapters_completed": sum(1 for c in per_chapter if c["total"] and c["read"] == c["total"]),
        "steps_total": total_units,
        "steps_read": read_units,
        "percent": _pct(read_units, total_units),
    }
    if detailed:
        out["chapters"] = per_chapter
    return out


async def sign_mastery(db, attempts: List[dict], catalog_ids: Set[str]) -> Dict[str, Any]:
    answered: Dict[str, List[bool]] = {}
    qids: Set[str] = set()
    for a in attempts:
        for qa in a.get("questions_answered") or []:
            if isinstance(qa, dict) and qa.get("question_id") and isinstance(qa.get("is_correct"), bool):
                qids.add(str(qa["question_id"]))
    sign_of: Dict[str, Set[str]] = {}
    if qids:
        async for q in db.questions.find({"id": {"$in": list(qids)}}, {"_id": 0, "id": 1, "sign_id": 1, "sign_ids": 1,
                                                                        "traffic_sign_id": 1, "bildeUrl": 1, "image_url": 1}):
            s = sign_ids_of_question(q, catalog_ids)
            if s:
                sign_of[q["id"]] = s
    for a in attempts:
        for qa in a.get("questions_answered") or []:
            if isinstance(qa, dict) and isinstance(qa.get("is_correct"), bool):
                for sid in sign_of.get(str(qa.get("question_id")), ()):
                    answered.setdefault(sid, []).append(qa["is_correct"])
    mastered = [s for s, r in answered.items()
                if len(r) >= MASTERY_MIN_ANSWERS and sum(r) / len(r) >= MASTERY_MIN_ACCURACY]
    weak = sorted((s for s, r in answered.items() if len(r) >= MASTERY_MIN_ANSWERS and s not in mastered),
                  key=lambda s: sum(answered[s]) / len(answered[s]))[:5]
    return {
        "catalog_total": len(catalog_ids),
        "practiced": len(answered),
        "mastered": len(mastered),
        "percent": _pct(len(mastered), len(catalog_ids)),
        "weak_sign_ids": weak,
    }


async def build_dashboard(db, user: dict, is_premium: bool, catalog_ids: Set[str]) -> Dict[str, Any]:
    """Bygger svaret for GET /api/dashboard/progress. `user` er brukerdokumentet fra databasen
    for den innloggede brukeren — kun id og device_id leses, aldri fra en URL-parameter."""
    user_id = str(user.get("id") or "")
    identities = [{"user_id": user_id}]
    if user.get("device_id"):
        identities.append({"device_id": str(user["device_id"])})

    attempts = await recent_attempts(db, identities)
    total_q = sum(int(a.get("total_questions") or 0) for a in attempts)
    correct = sum(int(a.get("correct_answers") or 0) for a in attempts)
    quiz: Dict[str, Any] = {
        "attempts": len(attempts),
        "answered": total_q,
        "correct": correct,
        "accuracy": _pct(correct, total_q),
        "exams_passed": sum(1 for a in attempts if a.get("mode") == "exam" and a.get("passed") is True),
        "last_activity": (attempts[0].get("completed_at") if attempts else None),
    }
    payload: Dict[str, Any] = {
        "tier": "premium" if is_premium else "free",
        "streak_days": compute_streak(a.get("completed_at") for a in attempts),
        "quiz": quiz,
        "studybook": await studybook_progress(db, user_id, detailed=is_premium),
    }
    if is_premium:
        cats: Dict[str, List[int]] = {}
        for a in attempts:
            key = a.get("category")
            if key and a.get("total_questions"):
                row = cats.setdefault(str(key), [0, 0])
                row[0] += int(a.get("total_questions") or 0)
                row[1] += int(a.get("correct_answers") or 0)
        quiz["by_category"] = sorted(
            ({"category": k, "answered": v[0], "correct": v[1], "percent": _pct(v[1], v[0])} for k, v in cats.items()),
            key=lambda r: r["percent"],
        )
        payload["signs"] = await sign_mastery(db, attempts, catalog_ids)
        payload["locked"] = []
        payload["upgrade"] = {"show_button": False}
    else:
        payload["signs"] = None
        payload["locked"] = list(LOCKED_FOR_FREE)
        payload["upgrade"] = {"show_button": True, "gate": "upgrade"}
    return payload
