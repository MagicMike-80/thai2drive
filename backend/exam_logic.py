"""Exam Simulator domain logic for Thai2Drive.

Defines core Norwegian theory exam rules (Statens vegvesen standard):
- 45 questions per set
- 90 minutes time limit (5400 seconds)
- Maximum 7 errors allowed to pass (at least 38 correct answers)
- 100% language isolation (NO, TH, EN) for Michael AI coaching handoffs
"""

from __future__ import annotations

from typing import Any, Dict, Optional


EXAM_TOTAL_QUESTIONS = 45
EXAM_TIME_LIMIT_SECONDS = 90 * 60  # 5400 seconds
EXAM_MAX_ERRORS = 7
EXAM_PASS_THRESHOLD = 38  # 45 - 7


def evaluate_exam_attempt(
    total_questions: int,
    correct_answers: int,
    duration_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    """Evaluate an exam attempt against official theory test rules.

    A test is passed if and only if errors <= 7 (which equals correct >= 38
    when total is 45).
    """
    safe_total = max(0, int(total_questions))
    safe_correct = max(0, min(int(correct_answers), safe_total))
    errors = max(0, safe_total - safe_correct)

    score_pct = round((safe_correct / safe_total * 100), 1) if safe_total > 0 else 0.0

    # In official rules, you need at least 38 correct out of 45 (<= 7 errors).
    if safe_total == EXAM_TOTAL_QUESTIONS:
        passed = (errors <= EXAM_MAX_ERRORS) and (safe_correct >= EXAM_PASS_THRESHOLD)
    else:
        passed = errors <= EXAM_MAX_ERRORS and safe_correct > 0

    timed_out = False
    if duration_seconds is not None:
        # Give a small 30-second network grace period before marking timed out
        timed_out = duration_seconds > (EXAM_TIME_LIMIT_SECONDS + 30)

    return {
        "passed": passed,
        "errors": errors,
        "max_errors": EXAM_MAX_ERRORS,
        "pass_threshold": EXAM_PASS_THRESHOLD,
        "correct_answers": safe_correct,
        "total_questions": safe_total,
        "score_percentage": score_pct,
        "timed_out": timed_out,
        "duration_seconds": duration_seconds,
    }


def generate_michael_exam_prompt(
    lang: str,
    passed: bool,
    score: int,
    total: int,
    weak_topic: Optional[str] = None,
) -> Dict[str, str]:
    """Generate localized prompt and display message for Michael AI coaching handoff.

    Guarantees 100% language isolation with ZERO cross-language bleed-through.
    """
    norm_lang = (lang or "no").strip().lower()
    if norm_lang not in ("no", "th", "en"):
        norm_lang = "no"

    topic_clean = (weak_topic or "").strip()

    if norm_lang == "th":
        if passed:
            if topic_clean:
                display = f"ฉันสอบจำลองผ่านแล้ว ({score}/{total}) แต่ยังมีข้อสงสัยในหัวข้อ {topic_clean} ช่วยแนะนำหน่อยครับ"
                prompt = (
                    f"ฉันเพิ่งทำข้อสอบจำลองผ่านได้คะแนน {score} จาก {total} ข้อ "
                    f"แต่ยังมีข้อผิดพลาดในหัวข้อ '{topic_clean}' "
                    f"ช่วยอธิบายจุดสำคัญและให้โจทย์สั้น ๆ เพื่อทดสอบความเข้าใจของฉันหน่อย"
                )
            else:
                display = f"ฉันสอบจำลองผ่านแล้ว ({score}/{total})! มีคำแนะนำเพิ่มเติมสำหรับการสอบจริงไหมครับ"
                prompt = (
                    f"ฉันเพิ่งทำข้อสอบจำลองผ่านได้คะแนน {score} จาก {total} ข้อ "
                    f"ช่วยให้คำแนะนำสำคัญก่อนไปสอบจริงที่ Statens vegvesen หน่อย"
                )
        else:
            if topic_clean:
                display = f"ฉันสอบจำลองยังไม่ผ่าน ({score}/{total}) และผิดบ่อยในหัวข้อ {topic_clean} ช่วยสอนหน่อยครับ"
                prompt = (
                    f"ฉันเพิ่งทำข้อสอบจำลองได้คะแนน {score} จาก {total} ข้อ (ยังไม่ผ่าน) "
                    f"และพบว่าทำผิดบ่อยที่สุดในหัวข้อ '{topic_clean}' "
                    f"ช่วยอธิบายหลักการจำง่าย ๆ และตั้งคำถามฝึกปฏิบัติให้ฉันลองตอบหน่อย"
                )
            else:
                display = f"ฉันสอบจำลองยังไม่ผ่าน ({score}/{total}) ควรเริ่มฝึกจากตรงไหนดีครับ"
                prompt = (
                    f"ฉันเพิ่งทำข้อสอบจำลองได้คะแนน {score} จาก {total} ข้อ ซึ่งยังไม่ผ่านเกณฑ์ "
                    f"ช่วยวิเคราะห์และแนะนำวิธีฝึกฝนเพื่อเตรียมสอบรอบถัดไปหน่อย"
                )

    elif norm_lang == "en":
        if passed:
            if topic_clean:
                display = f"I passed the mock exam ({score}/{total}), but need advice on {topic_clean}."
                prompt = (
                    f"I just passed the exam simulation with a score of {score}/{total}. "
                    f"However, I had some mistakes in the topic '{topic_clean}'. "
                    f"Could you explain the core rule and give me a mini-practice question?"
                )
            else:
                display = f"I passed the mock exam ({score}/{total})! Any advice before the official test?"
                prompt = (
                    f"I just passed the exam simulation with a score of {score}/{total}. "
                    f"What key tips should I keep in mind before taking the official theory exam at Statens vegvesen?"
                )
        else:
            if topic_clean:
                display = f"I did not pass the mock exam ({score}/{total}) with mistakes in {topic_clean}. Please help!"
                prompt = (
                    f"I did not pass the exam simulation this time, scoring {score}/{total}. "
                    f"My weakest topic was '{topic_clean}'. "
                    f"Can you explain the rules in simple terms and challenge me with a practice situation?"
                )
            else:
                display = f"I did not pass the mock exam ({score}/{total}). Where should I focus?"
                prompt = (
                    f"I did not pass the exam simulation ({score}/{total} correct, max 7 errors allowed). "
                    f"Can you give me a structured plan on what to practice next?"
                )

    else:  # Norwegian (no)
        if passed:
            if topic_clean:
                display = f"Jeg besto prøven ({score}/{total}), men trenger litt råd om {topic_clean}."
                prompt = (
                    f"Jeg fullførte nettopp eksamenssimulatoren med {score}/{total} riktige (bestått). "
                    f"Jeg fikk likevel noen feil på '{topic_clean}'. "
                    f"Kan du forklare hovedregelen enkelt og gi meg et lite oppfølgingsspørsmål?"
                )
            else:
                display = f"Jeg besto prøven ({score}/{total})! Har du noen tips før den virkelige teoriprøven?"
                prompt = (
                    f"Jeg fullførte nettopp eksamenssimulatoren med {score}/{total} riktige (bestått). "
                    f"Hva er de viktigste rådene dine før jeg drar til Statens vegvesen for den ekte prøven?"
                )
        else:
            if topic_clean:
                display = f"Jeg besto ikke prøven ({score}/{total}) og slet med {topic_clean}. Kan du hjelpe meg?"
                prompt = (
                    f"Jeg besto dessverre ikke eksamenssimulatoren denne gangen ({score}/{total} riktige). "
                    f"Jeg hadde flest feil på '{topic_clean}'. "
                    f"Kan du forklare trafikkreglene for dette og gi meg en praktisk situasjon jeg kan prøve meg på?"
                )
            else:
                display = f"Jeg besto ikke prøven ({score}/{total}). Hva bør jeg øve mest på nå?"
                prompt = (
                    f"Jeg besto dessverre ikke eksamenssimulatoren denne gangen ({score}/{total} riktige, kravet er minst 38). "
                    f"Kan du hjelpe meg å legge opp en plan for hva jeg bør fokusere på?"
                )

    return {
        "lang": norm_lang,
        "display_message": display,
        "chat_prompt": prompt,
    }
