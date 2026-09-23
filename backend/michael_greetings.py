"""Michael's opening messages.

Calm, dry and short (master document 2): no emojis, no false praise, one question at most.
Each language is written on its own and never falls back to another (language purity).
The first message to a new student says plainly that Michael is an AI teacher.

Selection is stable per student and day (crc32, not random), so a page reload does not
flip the greeting and tests stay deterministic.
"""
from __future__ import annotations

import re
import zlib
from datetime import datetime, timedelta, timezone
from typing import Optional

# {navn} is replaced with a name suffix (", Nok" / " คุณNok") or with nothing.
# {streak} and {topic} are only used in the groups that receive them.
GREETINGS = {
    "no": {
        "new": [
            "Hei{navn}. Jeg er Michaels AI-trafikklærer, bygget på hans 16 år med undervisning i Oslo. Hva vil du at vi skal øve på i dag?",
            "Hei{navn}. Jeg er en AI-trafikklærer laget etter Michael, som har undervist i Oslo i 16 år. Hva vil du at vi skal øve på i dag?",
            "Velkommen{navn}. Jeg er Michaels AI-assistent og bygger på erfaringen hans som trafikklærer. Hva vil du at vi skal øve på i dag?",
            "Hei{navn}. Jeg er AI-læreren til Michael, trafikklærer i Oslo med 16 års erfaring. Hva vil du at vi skal øve på i dag?",
        ],
        "morning": [
            "God morgen{navn}. En rask runde før dagen starter?",
            "God morgen{navn}. Hva vil du øve på?",
            "Morgen{navn}. Vi tar det rolig. Hva starter vi med?",
            "God morgen{navn}. Vikeplikt, skilt eller noe annet i dag?",
        ],
        "day": [
            "Hei{navn}. Hva vil du øve på nå?",
            "Hei{navn}. Skal vi ta en økt? Si hva du vil starte med.",
            "God dag{navn}. Hva tar vi i dag?",
            "Hei{navn}. Vi tar én ting av gangen. Hva først?",
            "Hei{navn}. Spør meg om hva som helst innen trafikk.",
        ],
        "evening": [
            "God kveld{navn}. Øver du sent i dag? Bra.",
            "God kveld{navn}. Kveldsøkt. Hva tar vi?",
            "Hei{navn}. Litt kveldsrepetisjon? Si hva du vil øve på.",
            "God kveld{navn}. Vi tar det rolig. Hva vil du starte med?",
        ],
        "comeback": [
            "Lenge siden sist{navn}. Skal vi ta en rolig repetisjon?",
            "Velkommen tilbake{navn}. Vi tar det i ditt tempo. Hva vil du repetere?",
            "Det er en stund siden sist{navn}. Vil du begynne med en kort repetisjon?",
            "Velkommen tilbake{navn}. Ingen stress. Hva vil du ta først?",
        ],
        "streak": [
            "Du har {streak} riktige svar på rad{navn}. Hva vil du fortsette med?",
            "{streak} riktige på rad{navn}. Hva tar vi nå?",
        ],
        "streak_topic": [
            "Du har {streak} riktige svar på rad{navn}. {topic} har vært litt vrient i det siste. Skal vi ta det, eller fortsette med noe annet?",
            "{streak} riktige på rad{navn}. {topic} har gått litt tregt. Vil du ta det nå, eller noe annet?",
        ],
        "weak_topic": [
            "Hei{navn}. Jeg ser at du har hatt noen feil på {topic} i det siste. Skal vi ta det sammen, eller vil du noe annet i dag?",
            "Hei{navn}. {topic} har vært vrient i det siste. Vil du ta det først, eller noe annet?",
            "Hei{navn}. Historikken din viser noen feil på {topic}. Skal vi gå gjennom det rolig?",
        ],
    },
    "th": {
        "new": [
            "สวัสดีครับ{navn} ผมเป็นผู้ช่วยครูสอนขับรถที่เป็นปัญญาประดิษฐ์ของไมเคิล สร้างจากประสบการณ์สอน 16 ปีในออสโลของเขา วันนี้อยากให้เราฝึกเรื่องอะไรดีครับ?",
            "สวัสดีครับ{navn} ผมเป็นครูสอนขับรถที่เป็นปัญญาประดิษฐ์ สร้างตามแบบไมเคิล ครูสอนขับรถในออสโลที่มีประสบการณ์ 16 ปี วันนี้อยากให้เราฝึกเรื่องอะไรดีครับ?",
            "ยินดีต้อนรับครับ{navn} ผมเป็นผู้ช่วยที่เป็นปัญญาประดิษฐ์ของไมเคิล ครูสอนขับรถในออสโล วันนี้อยากให้เราฝึกเรื่องอะไรดีครับ?",
            "สวัสดีครับ{navn} ผมคือครูปัญญาประดิษฐ์ของไมเคิล ครูสอนขับรถในออสโลที่มีประสบการณ์ 16 ปี วันนี้อยากให้เราฝึกเรื่องอะไรดีครับ?",
        ],
        "morning": [
            "สวัสดีตอนเช้าครับ{navn} มาฝึกกันสักรอบก่อนเริ่มวันไหมครับ?",
            "อรุณสวัสดิ์ครับ{navn} วันนี้อยากเริ่มด้วยเรื่องอะไรดีครับ?",
            "สวัสดีตอนเช้าครับ{navn} ค่อย ๆ ไปทีละเรื่องนะครับ อยากเริ่มเรื่องไหนก่อนครับ?",
            "สวัสดีตอนเช้าครับ{navn} การให้ทาง ป้ายจราจร หรือเรื่องอื่นดีครับ?",
        ],
        "day": [
            "สวัสดีครับ{navn} วันนี้อยากฝึกเรื่องอะไรดีครับ?",
            "สวัสดีครับ{navn} มาเริ่มกันเลยครับ อยากถามเรื่องอะไรก่อนครับ?",
            "สวัสดีครับ{navn} ทีละเรื่องนะครับ อยากเริ่มเรื่องไหนก่อนครับ?",
            "สวัสดีครับ{navn} ถามผมได้ทุกเรื่องเกี่ยวกับการจราจรครับ",
        ],
        "evening": [
            "สวัสดีตอนเย็นครับ{navn} ฝึกตอนเย็นแบบนี้ดีครับ อยากเริ่มเรื่องอะไรครับ?",
            "สวัสดีตอนค่ำครับ{navn} ค่อย ๆ ทบทวนกันครับ อยากเริ่มเรื่องไหนครับ?",
            "สวัสดีตอนเย็นครับ{navn} ไม่ต้องรีบครับ อยากฝึกเรื่องอะไรก่อนครับ?",
            "สวัสดีตอนเย็นครับ{navn} วันนี้อยากถามอะไรผมครับ?",
        ],
        "comeback": [
            "ไม่ได้คุยกันนานเลยครับ{navn} มาทบทวนกันช้า ๆ ไหมครับ?",
            "ยินดีต้อนรับกลับมาครับ{navn} ไปตามจังหวะของคุณเลยครับ อยากทบทวนเรื่องอะไรครับ?",
            "ห่างหายไปสักพักนะครับ{navn} เริ่มจากทบทวนสั้น ๆ ไหมครับ?",
            "ยินดีต้อนรับกลับมาครับ{navn} ไม่ต้องรีบครับ อยากเริ่มเรื่องไหนก่อนครับ?",
        ],
        "streak": [
            "ตอนนี้คุณตอบถูกติดต่อกัน {streak} ข้อแล้วครับ{navn} อยากทำต่อเรื่องอะไรครับ?",
            "ตอบถูกติดต่อกัน {streak} ข้อแล้วครับ{navn} ต่อด้วยเรื่องอะไรดีครับ?",
        ],
        "streak_topic": [
            "ตอนนี้คุณตอบถูกติดต่อกัน {streak} ข้อแล้วครับ{navn} ผมเห็นว่าเรื่อง{topic}ยังยากอยู่บ้าง อยากคุยเรื่องนี้ หรือทำต่อเรื่องอื่นดีครับ?",
            "ตอบถูกติดต่อกัน {streak} ข้อแล้วครับ{navn} เรื่อง{topic}ยังค่อนข้างช้าอยู่ อยากทบทวนตอนนี้ หรือเรื่องอื่นครับ?",
        ],
        "weak_topic": [
            "สวัสดีครับ{navn} ผมเห็นว่าคุณพลาดเรื่อง{topic}อยู่บ้างครับ อยากทบทวนเรื่องนี้ด้วยกัน หรือมีเรื่องอื่นอยากถามไหมครับ?",
            "สวัสดีครับ{navn} เรื่อง{topic}ยังยากอยู่บ้างครับ อยากเริ่มที่เรื่องนี้ก่อน หรือเรื่องอื่นครับ?",
            "สวัสดีครับ{navn} ประวัติของคุณมีข้อผิดพลาดเรื่อง{topic}อยู่บ้าง มาทบทวนกันช้า ๆ ไหมครับ?",
        ],
    },
    "en": {
        "new": [
            "Hi{navn}. I'm Michael's AI driving teacher, built on his 16 years of teaching in Oslo. What would you like to practise today?",
            "Hi{navn}. I'm an AI teacher modelled on Michael, who has taught in Oslo for 16 years. What would you like to practise today?",
            "Welcome{navn}. I'm Michael's AI assistant and I build on his experience as a driving instructor. What would you like to practise today?",
            "Hi{navn}. I'm the AI teacher behind Michael's 16 years of teaching in Oslo. What would you like to practise today?",
        ],
        "morning": [
            "Good morning{navn}. A quick round before the day starts?",
            "Good morning{navn}. What would you like to practise?",
            "Morning{navn}. We'll take it easy. Where do we start?",
            "Good morning{navn}. Give way, signs, or something else today?",
        ],
        "day": [
            "Hi{navn}. What would you like to practise now?",
            "Hi{navn}. Shall we do a session? Tell me where to start.",
            "Hello{navn}. What are we doing today?",
            "Hi{navn}. One thing at a time. What first?",
            "Hi{navn}. Ask me anything about driving theory.",
        ],
        "evening": [
            "Good evening{navn}. Practising late today? Good.",
            "Good evening{navn}. An evening session. What are we doing?",
            "Hi{navn}. A bit of evening revision? Tell me what to practise.",
            "Good evening{navn}. We'll take it easy. Where do you want to start?",
        ],
        "comeback": [
            "It's been a while{navn}. Shall we do a calm revision?",
            "Welcome back{navn}. We'll go at your pace. What would you like to revise?",
            "It's been a while since last time{navn}. Want to start with a short revision?",
            "Welcome back{navn}. No stress. What first?",
        ],
        "streak": [
            "You're on a {streak}-answer correct streak{navn}. What would you like to continue with?",
            "{streak} correct in a row{navn}. What next?",
        ],
        "streak_topic": [
            "You're on a {streak}-answer correct streak{navn}. {topic} has been a bit tricky lately. Shall we take it, or continue with something else?",
            "{streak} correct in a row{navn}. {topic} has been slow. Do it now, or something else?",
        ],
        "weak_topic": [
            "Hi{navn}. I see you've had a few mistakes on {topic} lately. Shall we go through it together, or is there something else today?",
            "Hi{navn}. {topic} has been tricky lately. Want to start there, or somewhere else?",
            "Hi{navn}. Your history shows a few mistakes on {topic}. Shall we go through it calmly?",
        ],
    },
}

_NAME_OK = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ฀-๿'\-]{1,24}$")


def safe_first_name(user_doc: Optional[dict]) -> Optional[str]:
    """First name from the user record, or None if missing or not a plain name (e.g. an e-mail)."""
    if not isinstance(user_doc, dict):
        return None
    raw = str(user_doc.get("full_name") or user_doc.get("name") or "").strip()
    if not raw or "@" in raw:
        return None
    first = raw.split()[0]
    return first if _NAME_OK.match(first) else None


def oslo_now(now_utc: Optional[datetime] = None) -> datetime:
    """Current time in Oslo; falls back to a fixed +1h/+2h offset if tzdata is missing."""
    now_utc = now_utc or datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        return now_utc.astimezone(ZoneInfo("Europe/Oslo"))
    except Exception:
        # Rough CET/CEST: DST is roughly the end of March to the end of October.
        offset = 2 if 3 < now_utc.month < 10 else 1
        return now_utc.astimezone(timezone(timedelta(hours=offset)))


def days_since(last_session_at: Optional[datetime], now_utc: Optional[datetime] = None) -> Optional[int]:
    if not isinstance(last_session_at, datetime):
        return None
    now_utc = now_utc or datetime.now(timezone.utc)
    if last_session_at.tzinfo is None:
        last_session_at = last_session_at.replace(tzinfo=timezone.utc)
    return max(0, (now_utc - last_session_at).days)


def _time_group(hour: int) -> str:
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 18:
        return "day"
    return "evening"


def _stable_index(seed: str, size: int) -> int:
    return zlib.crc32(seed.encode("utf-8")) % size


def pick_welcome(
    lang: str,
    *,
    first_name: Optional[str] = None,
    is_returning: bool = False,
    days_since_last: Optional[int] = None,
    hour: int = 12,
    streak: int = 0,
    topic: Optional[str] = None,
    seed: str = "",
) -> str:
    """Choose one greeting. Priority: streak > weak topic > comeback > time of day > new student."""
    if lang not in GREETINGS:
        raise ValueError("Unsupported language")
    groups = GREETINGS[lang]

    if streak and streak >= 1:
        group = "streak_topic" if topic else "streak"
    elif topic:
        group = "weak_topic"
    elif is_returning and days_since_last is not None and days_since_last > 7:
        group = "comeback"
    elif is_returning:
        group = _time_group(hour)
    else:
        group = "new"

    templates = groups[group]
    template = templates[_stable_index(f"{seed}:{group}:{lang}", len(templates))]
    if first_name:
        navn = f" คุณ{first_name}" if lang == "th" else f", {first_name}"
    else:
        navn = ""
    return template.format(navn=navn, streak=streak, topic=topic or "")
