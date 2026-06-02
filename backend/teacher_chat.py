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

from fastapi import APIRouter
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
- Calm, patient, encouraging — like a trusted co-driver sitting beside the student.
- You never judge. You say "La oss se på dette sammen" not "Du tok feil."
- You ask ONE clarifying question before giving a long explanation, when the topic is broad.
- You guide the conversation step by step, like a real instructor in a lesson.

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

# ─── Contextual chip suggestions ─────────────────────────────────────────────
def _get_suggestions(reply: str, lang: str) -> list:
    r = reply.lower()
    # Vikeplikt / right-of-way
    if any(w in r for w in ["vikeplikt", "høyreregel", "forkjørs", "rundkjøring", "stoppskilt",
                              "give way", "right-of-way", "roundabout", "การให้ทาง", "วงเวียน"]):
        if lang == "th":
            return ["🚗 กฎให้ทาง (ขวา)", "🛑 ป้ายให้ทาง", "⭕ วงเวียน", "🔴 ป้ายหยุด"]
        if lang == "en":
            return ["🚗 Right-of-way rule", "🛑 Give Way sign", "⭕ Roundabout", "🔴 Stop sign"]
        return ["🚗 Høyreregelen", "🛑 Vikepliktskilt", "⭕ Rundkjøring", "🔴 Stoppskilt"]
    # Signs / skilt
    if any(w in r for w in ["skilt", "sign", "ป้าย", "trafikkskilt"]):
        if lang == "th":
            return ["🛑 ฝึกกับป้ายนี้", "📖 อ่านเพิ่มเติม", "🚗 ป้ายคล้ายกัน", "❓ ถามต่อ"]
        if lang == "en":
            return ["🛑 Practise this sign", "📖 Read more", "🚗 Similar signs", "❓ Ask more"]
        return ["🛑 Øv på dette skiltet", "📖 Les mer", "🚗 Se lignende skilt", "❓ Spør videre"]
    # Theory test
    if any(w in r for w in ["teoriprøv", "prøv", "สอบ", "theory test", "test"]):
        if lang == "th":
            return ["📝 ข้อผิดพลาดที่พบบ่อย", "📊 ฉันควรฝึกอะไร?", "📖 เปิดหนังสือเรียน"]
        if lang == "en":
            return ["📝 Common mistakes", "📊 What should I practise?", "📖 Open study book"]
        return ["📝 Vanligste feil", "📊 Hva bør jeg øve på?", "📖 Åpne studiebok"]
    # Speed / fartsgrense
    if any(w in r for w in ["fartsgrense", "hastighet", "speed", "ความเร็ว"]):
        if lang == "th":
            return ["🚗 ในเมือง 50 กม/ชม", "🛣️ นอกเมือง 80 กม/ชม", "❓ ถามต่อ"]
        if lang == "en":
            return ["🚗 In town 50 km/h", "🛣️ Outside town 80 km/h", "❓ Ask more"]
        return ["🚗 I tettsted 50 km/t", "🛣️ Utenfor tettsted 80 km/t", "❓ Spør videre"]
    # Default
    if lang == "th":
        return ["❓ ถามต่อ", "📖 เปิดหนังสือเรียน", "📊 สถิติของฉัน"]
    if lang == "en":
        return ["❓ Ask more", "📖 Open study book", "📊 My statistics"]
    return ["❓ Spør videre", "📖 Åpne studiebok", "📊 Min statistikk"]


# ─── API ──────────────────────────────────────────────────────────────────────
teacher_router = APIRouter()


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
