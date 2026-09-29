"""
quiz_readiness.py — «Michaels Exam Mode» klar-score.

Ren, offline-testbar beregning. Ingen DB, ingen nett, ingen miljølesning på
importtid (samme mønster som glossary_match.py / culture_lessons.py).

Scoren er IKKE en enkel prosentlinje. Tre faktorer:

  45 %  feilsvar-trend   — recency-vektet nøyaktighet (ferske feil straffer mer)
  30 %  vikepliktsmestring — nøyaktighet i vikeplikt-kritiske kategorier,
                             skalert etter hvor mange slike svar som finnes
  25 %  tidsbruk/tempo    — median svartid på riktige svar mot et målbånd;
                             for raskt (gjetting) og for tregt straffer begge

Vekt som «frigjøres» når vikeplikt- eller tempo-data mangler, flyttes til
feilsvar-trenden, så summen alltid er 1.

Et `attempt` er et ai_attempts-dokument: ``is_correct`` (bool), ``category``
(str), ``time_taken_ms`` (tall), ``timestamp``. Lista antas nyeste først.
"""

from statistics import median

MIN_ATTEMPTS = 10          # under dette: cold start
TREND_WINDOW = 60          # antall forsøk feilsvar-trenden ser på
TREND_DECAY = 0.96         # vekt for forsøk nr. i = DECAY**i (nyeste = i 0)

# Kategorier som teller som «vikeplikt-kritiske» (normalisert: lowercase/trim).
VIKEPLIKT_CATEGORIES = {
    "vikeplikt", "kryss", "rundkjøring", "rundkjoring",
    "gangfelt", "forkjørsvei", "forkjorsvei", "høyreregelen", "hoyreregelen",
}
VIKEPLIKT_FULL_CONFIDENCE_AT = 8   # antall svar for full vekt på faktoren

# Tempo-bånd i millisekunder (median svartid på RIKTIGE svar).
PACE_GUESS_MS = 3000       # <= dette: ren gjetting → 0
PACE_GOOD_LO_MS = 6000     # målbåndet starter
PACE_GOOD_HI_MS = 20000    # målbåndet slutter
PACE_SLOW_MS = 40000       # >= dette: for nølende → 0
PACE_MIN_SAMPLES = 5       # færre riktige-med-tid enn dette → tempo utelates

W_TREND, W_VIKEPLIKT, W_PACE = 0.45, 0.30, 0.25

READY_GOOD = 50            # under: 🌱  |  under EXCELLENT: 📈  |  ellers: 👑
READY_EXCELLENT = 85


def _norm(s) -> str:
    return (s or "").strip().lower()


def _is_correct(a) -> bool:
    return a.get("is_correct") is True or a.get("correct") is True


def _time_ms(a):
    v = a.get("time_taken_ms")
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)) and v > 0:
        return float(v)
    return None


def _recency_weighted_accuracy(attempts) -> float:
    window = attempts[:TREND_WINDOW]
    num = den = 0.0
    for i, a in enumerate(window):
        w = TREND_DECAY ** i
        den += w
        if _is_correct(a):
            num += w
    return (num / den * 100.0) if den else 0.0


def _vikeplikt(attempts):
    vp = [a for a in attempts if _norm(a.get("category")) in VIKEPLIKT_CATEGORIES]
    n = len(vp)
    if n == 0:
        return 0.0, 0.0, 0
    acc = sum(1 for a in vp if _is_correct(a)) / n * 100.0
    confidence = min(n / VIKEPLIKT_FULL_CONFIDENCE_AT, 1.0)
    return acc, confidence, n


def _pace_band_score(median_ms: float) -> float:
    if median_ms <= PACE_GUESS_MS or median_ms >= PACE_SLOW_MS:
        return 0.0
    if median_ms < PACE_GOOD_LO_MS:
        return (median_ms - PACE_GUESS_MS) / (PACE_GOOD_LO_MS - PACE_GUESS_MS) * 100.0
    if median_ms <= PACE_GOOD_HI_MS:
        return 100.0
    return (PACE_SLOW_MS - median_ms) / (PACE_SLOW_MS - PACE_GOOD_HI_MS) * 100.0


def _pace(attempts):
    times = sorted(
        t for t in (_time_ms(a) for a in attempts if _is_correct(a)) if t is not None
    )
    if len(times) < PACE_MIN_SAMPLES:
        return None, None
    med = median(times)
    score = _pace_band_score(med)
    # Straff ujevnt tempo: bredt spenn (IQR) i forhold til medianen taper toppscore.
    q1 = times[len(times) // 4]
    q3 = times[(len(times) * 3) // 4]
    if med > 0 and (q3 - q1) / med > 1.2:
        score = min(score, 70.0)
    return score, med


def _copy(score: int, cold: bool):
    if cold:
        return ("🌱",
                "Vi har akkurat startet. Ta noen spørsmål, så regner jeg ut klar-scoren din.",
                "เพิ่งเริ่มกันครับผม ลองทำข้อสอบสัก 2-3 ข้อ แล้วผมจะคำนวณคะแนนความพร้อมให้",
                "We just started. Answer a few questions and I will calculate your readiness.",
                "Øv bredt — ta minst 10 spørsmål på tvers av kategorier først.",
                "ฝึกให้หลากหลายก่อน ทำอย่างน้อย 10 ข้อในหลาย ๆ หมวดครับผม",
                "Practice broadly — answer at least 10 questions across categories first.")
    if score < READY_GOOD:
        return ("🌱",
                "Vi er godt i gang. Bruk litt ekstra tid på vikeplikt og kjernereglene før du tar hele prøver.",
                "เรากำลังไปได้ดีครับผม เน้นเรื่องการให้ทางและกฎพื้นฐานเพิ่มอีกนิดก่อนทำข้อสอบชุดเต็ม",
                "We are getting there. Spend extra time on right-of-way and core rules before full exams.",
                "Repetér de feilede spørsmålene, og ikke svar for raskt.",
                "ทบทวนข้อที่ตอบผิด และอย่ารีบตอบเร็วเกินไปครับผม",
                "Review the questions you got wrong, and do not answer too fast.")
    if score < READY_EXCELLENT:
        return ("📈",
                "Meget bra. Grunnforståelsen sitter. Ta 2-3 fulle prøver i jevnt tempo, så er du på et trygt nivå.",
                "ดีมากครับผม พื้นฐานแน่นแล้ว ทำข้อสอบเต็มอีก 2-3 ชุดด้วยจังหวะสม่ำเสมอ ก็พร้อมสอบผ่านแล้ว",
                "Very good. Fundamentals are solid. Do 2-3 full exams at a steady pace to reach a safe level.",
                "Pass på slurvefeil i vikeplikt og bremselengde.",
                "ระวังจุดหลอกเรื่องการให้ทางและระยะเบรกครับผม",
                "Watch out for careless mistakes on right-of-way and braking distance.")
    return ("👑",
            "Fantastisk. Refleksene sitter og tempoet er jevnt. Du er klar for den ekte teoriprøven.",
            "สุดยอดครับผม ตอบได้แม่นและจังหวะนิ่ง พร้อมสำหรับการสอบทฤษฎีจริงแล้ว",
            "Fantastic. Your reflexes are sharp and your pace is steady. You are ready for the real theory exam.",
            "Ta en rolig repetisjon kvelden før og sov godt.",
            "ทบทวนเบา ๆ ตอนค่ำก่อนวันสอบ และนอนให้พอครับผม",
            "Do a calm review the evening before and sleep well.")


def compute_quiz_readiness(attempts, *, now=None):
    """Return the exam-mode readiness dict for a device's ai_attempts (newest first)."""
    attempts = list(attempts or [])
    n_total = len(attempts)
    vp_mastery, vp_conf, vp_n = _vikeplikt(attempts)

    if n_total < MIN_ATTEMPTS:
        icon, s_no, s_th, s_en, a_no, a_th, a_en = _copy(0, cold=True)
        return {
            "ready_score": 0,
            "error_trend": 0.0,
            "vikeplikt_mastery": round(vp_mastery, 1),
            "vikeplikt_attempts": vp_n,
            "pace_score": None,
            "pace_median_s": None,
            "attempts_considered": n_total,
            "cold_start": True,
            "icon": icon,
            "status_no": s_no, "status_th": s_th, "status_en": s_en,
            "advice_no": a_no, "advice_th": a_th, "advice_en": a_en,
        }

    error_trend = _recency_weighted_accuracy(attempts)
    pace_score, pace_med = _pace(attempts)

    vp_w = W_VIKEPLIKT * vp_conf
    pace_w = W_PACE if pace_score is not None else 0.0
    # Alt som ikke ble brukt av vikeplikt/tempo går til feilsvar-trenden.
    trend_w = W_TREND + (W_VIKEPLIKT - vp_w) + (W_PACE - pace_w)
    total_w = trend_w + vp_w + pace_w

    score = (
        error_trend * trend_w
        + vp_mastery * vp_w
        + (pace_score or 0.0) * pace_w
    ) / total_w
    score = max(0, min(100, round(score)))

    icon, s_no, s_th, s_en, a_no, a_th, a_en = _copy(score, cold=False)
    return {
        "ready_score": score,
        "error_trend": round(error_trend, 1),
        "vikeplikt_mastery": round(vp_mastery, 1),
        "vikeplikt_attempts": vp_n,
        "pace_score": round(pace_score, 1) if pace_score is not None else None,
        "pace_median_s": round(pace_med / 1000.0, 1) if pace_med is not None else None,
        "attempts_considered": n_total,
        "cold_start": False,
        "icon": icon,
        "status_no": s_no, "status_th": s_th, "status_en": s_en,
        "advice_no": a_no, "advice_th": a_th, "advice_en": a_en,
    }
