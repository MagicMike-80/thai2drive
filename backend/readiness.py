"""
Michaels Exam Mode & Intelligent Klar-Score
--------------------------------------------
Beregner elevens helhetlige eksamensberedskap basert på:
1. Historisk nøyaktighet (siste 100 spørsmål) — vekt 50 %
2. Emnespredning over kritiske kategorier — vekt 30 %
3. Fullførte simulerte prøver (minst 3 beståtte) — vekt 20 %
"""
import os
import logging
from typing import Optional
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("readiness")
router = APIRouter(tags=["readiness"])

# Fallback MongoDB-tilkobling hvis routeren kalles utenfor app.state.db
_mongo_url = os.environ.get("MONGO_URL") or "mongodb://127.0.0.1:27017"
_mongo = AsyncIOMotorClient(_mongo_url)
_db = _mongo[os.environ.get("DB_NAME") or "thai2drive"]


@router.get("/api/user/readiness")
@router.get("/user/readiness")
async def calculate_readiness_score(
    request: Request,
    device_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
):
    """Beregner og returnerer elevens intelligente beredskapsscore."""
    db = getattr(request.app.state, "db", None) if hasattr(request, "app") and hasattr(request.app, "state") else None
    if db is None:
        db = _db

    dev_id = device_id or user_id or "anonymous"

    try:
        # 1. Hent brukerens siste 100 besvarte spørsmål fra quiz_attempts
        attempts_cursor = db["quiz_attempts"].find(
            {"$or": [{"device_id": dev_id}, {"user_id": dev_id}]}
        ).sort("created_at", -1).limit(100)
        attempts = await attempts_cursor.to_list(length=100)
    except Exception as e:
        logger.warning("Feil ved oppslag i quiz_attempts: %s", e)
        attempts = []

    if not attempts:
        return JSONResponse({
            "ready_score": 0,
            "accuracy": 0,
            "topic_coverage": 0,
            "simulations_passed": 0,
            "icon": "🌱",
            "status_no": "🌱 Vi har akkurat startet! Start quizen for å beregne din klar-score.",
            "status_th": "🌱 เริ่มทำข้อสอบเพื่อประเมินความพร้อมครับผม!",
            "status_en": "🌱 We just started! Start the quiz to calculate your readiness score.",
            "advice_no": "Øv på minst 4 forskjellige kategorier for å bygge et solid grunnlag.",
            "advice_th": "ฝึกทำข้อสอบให้ครอบคลุมอย่างน้อย 4 หมวดหมู่นะครับผม",
            "advice_en": "Practice across at least 4 different categories to build a solid foundation."
        })

    total_answers = len(attempts)
    correct_answers = sum(1 for a in attempts if a.get("correct") is True)

    # Historisk nøyaktighet (vekt 50%)
    accuracy = correct_answers / total_answers if total_answers > 0 else 0
    accuracy_score = accuracy * 100.0

    # Emnespredning (vekt 30%)
    categories = [
        a.get("category") or a.get("topic") or a.get("category_id")
        for a in attempts
        if a.get("category") or a.get("topic") or a.get("category_id")
    ]
    unique_categories = set(categories)
    topic_coverage = min(len(unique_categories) / 4.0, 1.0)
    topic_score = topic_coverage * 100.0

    # Eksamenssimuleringer (vekt 20%)
    try:
        simulations_cursor = db["exam_simulations"].find(
            {"$or": [{"device_id": dev_id}, {"user_id": dev_id}], "passed": True}
        )
        passed_simulations = await simulations_cursor.to_list(length=10)
        sim_count = len(passed_simulations)
    except Exception:
        # Fallback: Sjekk om det finnes exam-forsøk i attempts med høy score
        exam_attempts = [a for a in attempts if a.get("quiz_mode") == "exam" and a.get("correct")]
        sim_count = len(exam_attempts) // 38  # 38 riktige per prøve

    simulation_score = min(sim_count / 3.0, 1.0) * 100.0

    # Samlet beredskapsscore
    final_score = int((accuracy_score * 0.5) + (topic_score * 0.3) + (simulation_score * 0.2))

    # Pedagogisk tilbakemelding fra Michael basert på score
    if final_score < 50:
        icon = "🌱"
        status_no = "Vi er godt i gang med treningen! Jeg anbefaler at du øver mer på 'vikeplikt' og 'høyreregelen' for å bygge trygghet."
        status_th = "เรากำลังฝึกฝนกันได้ดีครับผม! แนะนำให้ฝึกทำข้อสอบหมวด 'การให้ทาง' และ 'กฎให้ทางจากขวา' เพิ่มเติมเพื่อสร้างความมั่นใจก่อนครับ"
        status_en = "We are well on our way! I recommend practicing more on right-of-way and priority rules."
        advice_no = "Fokuser på situasjonsbilder og kjernereglene før du tar hele eksamener."
        advice_th = "เน้นดูภาพสถานการณ์และกฎพื้นฐานก่อนทำข้อสอบชุดเต็มครับผม"
        advice_en = "Focus on situation images and core rules before attempting full exams."
    elif final_score < 85:
        icon = "📈"
        status_no = "Meget bra! Du har god grunnforståelse. Gjennomfør 2-3 fullskala eksamener, så er du på et trygt nivå for å bestå."
        status_th = "ทำได้ดีมากครับผม! มีความเข้าใจพื้นฐานที่ดีแล้ว ฝึกทำข้อสอบจำลองเต็มรูปแบบอีก 2-3 ครั้ง ก็พร้อมผ่านฉลุยแล้วครับ"
        status_en = "Very good! You have solid fundamentals. Complete 2-3 full practice exams to reach a safe pass level."
        advice_no = "Hold jevnt tempo og unngå slurvefeil på vikeplikt og bremselengde."
        advice_th = "รักษาความเร็วในการทำและระวังจุดหลอกเรื่องระยะเบรกและการให้ทางครับผม"
        advice_en = "Maintain steady pace and watch out for tricky questions on braking distance and right of way."
    else:
        icon = "👑"
        status_no = "Fantastisk! Scoren din viser at du har ryggmarksrefleksene inne og er helt klar for den ekte teoriprøven hos Statens vegvesen. Kjør på!"
        status_th = "สุดยอดมากครับผม! คะแนนของคุณแสดงว่ามีความพร้อมระดับสูงสำหรับการสอบจริงที่ Statens vegvesen แล้ว มั่นใจและลุยได้เลยครับ!"
        status_en = "Fantastic! Your score shows you are fully ready for the official theory exam at Statens vegvesen. Go for it!"
        advice_no = "Ta en siste repetisjon kvelden før og sov godt før prøvedagen."
        advice_th = "ทบทวนรอบสุดท้ายช่วงค่ำและนอนหลับให้เพียงพอก่อนวันสอบจริงครับผม"
        advice_en = "Do a final review the evening before and get a good night's sleep before test day."

    return JSONResponse({
        "success": True,
        "ready_score": final_score,
        "accuracy": int(accuracy_score),
        "topic_coverage": int(topic_score),
        "simulations_passed": sim_count,
        "categories_practiced": len(unique_categories),
        "total_attempts": total_answers,
        "icon": icon,
        "status_no": f"{icon} {status_no}",
        "status_th": f"{icon} {status_th}",
        "status_en": f"{icon} {status_en}",
        "advice_no": advice_no,
        "advice_th": advice_th,
        "advice_en": advice_en
    })
