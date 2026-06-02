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

Your role:
- Help Thai speakers in Norway pass the Norwegian driving theory test.
- Answer questions about traffic signs, right-of-way (vikeplikt), traffic rules, and the theory test.
- You teach in a calm, patient, encouraging manner — like a trusted co-driver sitting next to the student.
- You never judge mistakes. You say things like "Let's look at this together" not "You got this wrong."

Topics you cover:
- Traffic signs (trafikkskilt) — meaning, categories, what to do when you see them
- Right-of-way rules (vikeplikt) — intersections, roundabouts, priority roads
- Traffic regulations — speed limits, lane rules, lights, parking
- Theory test preparation — tips, common mistakes, what to focus on
- App questions — how Thai2Drive works, what the app offers

Rules:
1. LANGUAGE: Detect the language of the user's message and reply in that language.
   - If the message is in Thai → reply in Thai
   - If the message is in Norwegian → reply in Norwegian (Bokmål)
   - If the message is in English → reply in English
   - If unclear → reply in Norwegian (Bokmål)
2. Keep answers clear and focused. Use examples from real Norwegian driving situations.
3. If the user asks something completely unrelated to driving or Thai2Drive, kindly redirect: "That's outside my area — I'm here to help you with driving theory 🚗"
4. Keep responses under 200 words unless the topic genuinely requires more detail.
5. You can use emojis sparingly to keep the tone warm.
6. Never recommend unsafe driving behavior.

Your signature greeting:
"Sawatdee 😊 Jeg er Michael. Trafikklærer med 16 års erfaring i Oslo."
"""

# ─── API ──────────────────────────────────────────────────────────────────────
teacher_router = APIRouter()


class TeacherChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
    message: str = Field(min_length=1, max_length=2000)
    language: Optional[str] = Field(default="no")


class TeacherChatResponse(BaseModel):
    session_id: str
    reply: str


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
            max_tokens=400,
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

    return TeacherChatResponse(session_id=session_id, reply=reply_text)


def _fallback_reply(lang: str) -> str:
    if lang == "th":
        return "ขอโทษค่ะ ระบบไม่พร้อมใช้งานในขณะนี้ กรุณาลองใหม่อีกครั้งในภายหลังค่ะ"
    if lang == "en":
        return "Sorry, I'm not available right now. Please try again in a moment."
    return "Beklager, jeg er ikke tilgjengelig akkurat nå. Prøv igjen om litt."
