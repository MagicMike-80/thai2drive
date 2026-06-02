"""
Michael Trafikklærer — AI Chat
--------------------------------
POST /api/teacher/chat  – user sends a message, Michael responds.

Michael is a patient, calm driving instructor with 16 years of experience in Oslo.
He answers questions about traffic signs, right-of-way rules, traffic regulations,
and the Norwegian theory test. He speaks in the language the user writes in.
"""
from __future__ import annotations

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("teacher_chat")

# ─── MongoDB ─────────────────────────────────────────────────────────────────
_mongo = AsyncIOMotorClient(os.environ["MONGO_URL"])
_db = _mongo[os.environ.get("DB_NAME", "thai2drive")]
_chat_col = _db["teacher_chats"]

# ─── LLM (same litellm pattern as support_chat.py) ───────────────────────────
import litellm

litellm.suppress_debug_info = True
LLM_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
LLM_MODEL = os.environ.get("TEACHER_LLM_MODEL", "claude-haiku-4-5-20251001")

if LLM_KEY:
    logger.info("Teacher chat LLM ready — model=%s", LLM_MODEL)
else:
    logger.error("Teacher chat LLM NOT configured — ANTHROPIC_API_KEY absent.")

# ─── System prompt ────────────────────────────────────────────────────────────
MICHAEL_SYSTEM_PROMPT = """You are Michael, a driving instructor with 16 years of experience in Oslo, Norway.

Your teaching style:
- Calm, patient, encouraging — like a trusted driving instructor sitting in the passenger seat.
- You never judge. You say "La oss se på dette sammen" not "Du tok feil."
- You ask ONE clarifying question before giving a long explanation, when the topic is broad.
- You guide the conversation step by step, like a real instructor during a driving lesson.

TEACHING ORDER — always follow this sequence:
1. Start with a real traffic situation (paint the picture first)
2. Ask the student a short question to make them think
3. Explain what actually happens / what the rule means
4. Give practical driving advice (timing, observation, communication)
5. Connect to theory (the official term or rule) — last, not first

NEVER start with a definition. Always start with a situation.

BAD (textbook style — do not do this):
"Stoppelengde er summen av reaksjonsstrekning og bremsestrekning."

GOOD (instructor style — do this):
"Ok 😊

Tenk deg at du kjører i 50 km/t.
Plutselig løper et barn ut i veien.

Stopper bilen med én gang?

Nei.

Først må du oppdage faren.
Deretter bruker hjernen din litt tid på å reagere.
Først etter det begynner bilen å bremse.

Det er tre faser — og til sammen kalles det stoppelengde."

PRACTICAL COACHING LANGUAGE:
Weave these phrases in naturally where they fit:
- "Begynn å planlegge i god tid."
- "Senk farten tidlig, slik at andre forstår hva du har tenkt å gjøre."
- "Se langt fram — ikke bare rett foran deg."
- "Gjør deg forstått for andre trafikanter."
- "Rolig og kontrollert kjøring er trygg kjøring."
- "Gi deg selv tid til å observere situasjonen."

In Thai responses, translate these concepts naturally. Do not force Norwegian phrases into Thai answers.

FORMATTING RULES — follow these exactly:
- Keep paragraphs short: 1–3 sentences maximum per paragraph.
- Separate each paragraph with a blank line.
- When giving practical driving advice, ALWAYS use this exact header on its own line:
  🚗 Praktisk råd:
  (in Thai: 🚗 คำแนะนำ:  — in English: 🚗 Practical tip:)
  Then list each piece of advice on its own line.
  End the advice section with a blank line.
- Section headers (like "Situasjon:", "Forklaring:", "Teori:") go on their own line, followed by a blank line.
- Never write more than 5 lines of continuous text without a paragraph break.

CLARIFYING QUESTION RULE (most important rule):
When the user's message is broad or general (e.g. "vikeplikt", "skilt", "teoriprøven", "trafikkregel", "hjelp"),
do NOT give a full lesson immediately. Instead, ask ONE short clarifying question with 4–5 specific options.

Example — user says "Hjelp med vikeplikt":
Reply:
"Selvfølgelig 😊

Hvilken situasjon gjelder det?

🚗 Høyreregelen
🛑 Vikepliktskilt
🔴 Stoppskilt
⭕ Rundkjøring
🚶 Gangfelt"

Then wait for the student's answer before explaining.

When the question is already specific (e.g. "Hva betyr høyreregelen?"), answer directly and clearly.

TERMINOLOGY RULES:
Always use official Statens vegvesen / Norwegian traffic law terminology:
- teoriprøven (NOT teoriksen, NOT teorieksamen)
- forkjørsvei (NOT prioritetsvei)
- vikeplikt (correct)
- høyreregelen (correct)
- rundkjøring (correct)
- gangfelt (correct)
- stoppskilt, vikepliktskilt (correct)
- fartsgrense (NOT hastighetsbegrensning)
- kjørebane, kjørefelt (correct lane terminology)
- Statens vegvesen (the road authority)

LANGUAGE RULE:
Detect the language of the user's message and reply in that language.
- Norwegian message → reply in Bokmål Norwegian
- Thai message → reply in Thai
- English message → reply in English
- Unclear → reply in Norwegian Bokmål

RESPONSE LENGTH:
- Clarifying questions: max 6 lines
- Direct answers: max 120 words
- Never write walls of text
- Use short paragraphs and line breaks

TOPICS:
- Trafikkskilt — meaning, categories, what to do
- Vikeplikt — all situations
- Trafikkregler — speed, lanes, lights, parking
- Teoriprøven — tips, common mistakes
- Thai2Drive-appen — how it works
- Off-topic requests → "Det er utenfor mitt område — jeg er her for å hjelpe deg med kjørekortteorien 🚗"

Never recommend unsafe driving. Never invent rules."""

# ─── Single source of truth: welcome + topics ────────────────────────────────
MICHAEL_WELCOME = {
    "no": "Sawatdee 😊\n\nJeg er Michael.\n\nTrafikklærer med 16 års erfaring i Oslo.\n\nJeg kan hjelpe deg med skilt, vikeplikt, trafikkregler og teoriprøven.",
    "th": "สวัสดีครับ 😊\n\nผมชื่อไมเคิล\n\nครูสอนขับรถที่มีประสบการณ์ 16 ปีในออสโล\n\nผมสามารถช่วยคุณเรื่องป้ายจราจร การให้ทาง กฎจราจร และการสอบทฤษฎีได้ครับ",
    "en": "Sawatdee 😊\n\nI'm Michael.\n\nDriving instructor with 16 years of experience in Oslo.\n\nI can help you with signs, right-of-way, traffic rules and the theory test.",
}

MICHAEL_TOPICS = {
    "no": [
        {"icon": "🛑", "text": "Forklar et skilt"},
        {"icon": "🚗", "text": "Hjelp med vikeplikt"},
        {"icon": "📖", "text": "Forklar en trafikkregel"},
        {"icon": "📊", "text": "Hva bør jeg øve på?"},
        {"icon": "📝", "text": "Hjelp med teoriprøven"},
        {"icon": "❓", "text": "Spør om Thai2Drive"},
    ],
    "th": [
        {"icon": "🛑", "text": "อธิบายป้ายจราจร"},
        {"icon": "🚗", "text": "ช่วยเรื่องการให้ทาง"},
        {"icon": "📖", "text": "อธิบายกฎจราจร"},
        {"icon": "📊", "text": "ฉันควรฝึกเรื่องอะไร?"},
        {"icon": "📝", "text": "ช่วยเรื่องข้อสอบทฤษฎี"},
        {"icon": "❓", "text": "ถามเกี่ยวกับ Thai2Drive"},
    ],
    "en": [
        {"icon": "🛑", "text": "Explain a sign"},
        {"icon": "🚗", "text": "Help with right-of-way"},
        {"icon": "📖", "text": "Explain a traffic rule"},
        {"icon": "📊", "text": "What should I practise?"},
        {"icon": "📝", "text": "Help with the theory test"},
        {"icon": "❓", "text": "Ask about Thai2Drive"},
    ],
}

# ─── Contextual chip suggestions (multilingual keyword detection) ─────────────
_KW = {
    "vikeplikt": {
        "no": ["vikeplikt", "høyreregel", "forkjørsvei", "rundkjøring", "stoppskilt", "vikepliktskilt"],
        "th": ["การให้ทาง", "วงเวียน", "ป้ายหยุด", "ทางหลัก", "ให้ทาง"],
        "en": ["give way", "right-of-way", "roundabout", "stop sign", "priority road", "yield"],
    },
    "signs": {
        "no": ["skilt", "trafikkskilt", "fareskilt", "forbudsskilt", "påbudsskilt"],
        "th": ["ป้าย", "ป้ายจราจร", "ป้ายเตือน", "ป้ายบังคับ"],
        "en": ["traffic sign", "road sign", "warning sign", "sign means"],
    },
    "theory": {
        "no": ["teoriprøv", "teorieksamen", "prøven", "bestå"],
        "th": ["สอบ", "ข้อสอบ", "ทฤษฎี", "ผ่านการสอบ"],
        "en": ["theory test", "theory exam", "pass the test", "driving test"],
    },
    "speed": {
        "no": ["fartsgrense", "hastighet", "kilometer", "km/t", "stoppelengde"],
        "th": ["ความเร็ว", "กม/ชม", "ระยะหยุด"],
        "en": ["speed limit", "speed", "stopping distance", "km/h"],
    },
}

def _kw_match(reply_lower: str, category: str) -> bool:
    for kws in _KW[category].values():
        if any(w in reply_lower for w in kws):
            return True
    return False

def _get_suggestions(reply: str, lang: str) -> list:
    r = reply.lower()
    if _kw_match(r, "vikeplikt"):
        if lang == "th": return ["🚗 กฎให้ทาง (ขวา)", "🛑 ป้ายให้ทาง", "⭕ วงเวียน", "🔴 ป้ายหยุด"]
        if lang == "en": return ["🚗 Right-of-way rule", "🛑 Give Way sign", "⭕ Roundabout", "🔴 Stop sign"]
        return ["🚗 Høyreregelen", "🛑 Vikepliktskilt", "⭕ Rundkjøring", "🔴 Stoppskilt"]
    if _kw_match(r, "signs"):
        if lang == "th": return ["🛑 ฝึกกับป้ายนี้", "📖 อ่านเพิ่มเติม", "🚗 ป้ายคล้ายกัน", "❓ ถามต่อ"]
        if lang == "en": return ["🛑 Practise this sign", "📖 Read more", "🚗 Similar signs", "❓ Ask more"]
        return ["🛑 Øv på dette skiltet", "📖 Les mer", "🚗 Se lignende skilt", "❓ Spør videre"]
    if _kw_match(r, "theory"):
        if lang == "th": return ["📝 ข้อผิดพลาดที่พบบ่อย", "📊 ฉันควรฝึกอะไร?", "📖 เปิดหนังสือเรียน"]
        if lang == "en": return ["📝 Common mistakes", "📊 What should I practise?", "📖 Open study book"]
        return ["📝 Vanligste feil", "📊 Hva bør jeg øve på?", "📖 Åpne studiebok"]
    if _kw_match(r, "speed"):
        if lang == "th": return ["🚗 ในเมือง 50 กม/ชม", "🛣️ นอกเมือง 80 กม/ชม", "❓ ถามต่อ"]
        if lang == "en": return ["🚗 In town 50 km/h", "🛣️ Outside town 80 km/h", "❓ Ask more"]
        return ["🚗 I tettsted 50 km/t", "🛣️ Utenfor tettsted 80 km/t", "❓ Spør videre"]
    # Default
    if lang == "th": return ["❓ ถามต่อ", "📖 เปิดหนังสือเรียน", "📊 สถิติของฉัน"]
    if lang == "en": return ["❓ Ask more", "📖 Open study book", "📊 My statistics"]
    return ["❓ Spør videre", "📖 Åpne studiebok", "📊 Min statistikk"]


# ─── API ──────────────────────────────────────────────────────────────────────
teacher_router = APIRouter()


@teacher_router.get("/teacher/welcome")
async def teacher_welcome(lang: str = Query(default="no")):
    lang = lang if lang in MICHAEL_WELCOME else "no"
    return {"lang": lang, "welcome": MICHAEL_WELCOME[lang]}

@teacher_router.get("/teacher/topics")
async def teacher_topics(lang: str = Query(default="no")):
    lang = lang if lang in MICHAEL_TOPICS else "no"
    return {"lang": lang, "topics": MICHAEL_TOPICS[lang]}


class TeacherChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
    message: str = Field(min_length=1, max_length=2000)
    language: Optional[str] = Field(default="no")


class TeacherChatResponse(BaseModel):
    session_id: str
    reply: str
    suggestions: list = []


@teacher_router.post("/teacher/chat", response_model=TeacherChatResponse)
async def teacher_chat(req: TeacherChatRequest) -> TeacherChatResponse:
    session_id = req.session_id or f"ts_{uuid.uuid4().hex[:16]}"
    user_msg = req.message.strip()

    # Load prior conversation (last 20 messages in this session)
    prior = await _chat_col.find(
        {"session_id": session_id}
    ).sort("ts", 1).to_list(length=20)
    conversation: List[dict] = [{"role": m["role"], "content": m["content"]} for m in prior]

    # Call LLM
    try:
        if not LLM_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")

        messages = [{"role": "system", "content": MICHAEL_SYSTEM_PROMPT}]
        messages.extend(conversation)
        messages.append({"role": "user", "content": user_msg})

        resp = await litellm.acompletion(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=300,
            api_key=LLM_KEY,
        )
        reply_text = (resp.choices[0].message.content or "").strip()
        if not reply_text:
            reply_text = _fallback_reply(req.language or "no")
    except Exception as e:
        logger.error("Teacher LLM call failed [%s]: %s", type(e).__name__, e)
        reply_text = _fallback_reply(req.language or "no")

    # Persist both messages
    now = datetime.now(timezone.utc)
    await _chat_col.insert_many([
        {
            "session_id": session_id,
            "role": "user",
            "content": user_msg,
            "language": req.language,
            "ts": now,
        },
        {
            "session_id": session_id,
            "role": "assistant",
            "content": reply_text,
            "ts": now,
        },
    ])

    suggestions = _get_suggestions(reply_text, req.language or "no")
    return TeacherChatResponse(session_id=session_id, reply=reply_text, suggestions=suggestions)


def _fallback_reply(lang: str) -> str:
    if lang == "th":
        return "ขอโทษค่ะ ระบบไม่พร้อมใช้งานในขณะนี้ กรุณาลองใหม่อีกครั้งในภายหลังค่ะ"
    if lang == "en":
        return "Sorry, I'm not available right now. Please try again in a moment."
    return "Beklager, jeg er ikke tilgjengelig akkurat nå. Prøv igjen om litt."
