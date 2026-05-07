"""
AI Support Chat for Thai2Drive
-------------------------------
POST /api/support/chat – user sends a message, AI responds.
All messages are logged to MongoDB. Important cases trigger an email
notification to the support address defined below (plus a fallback
admin log entry if SMTP is unavailable).
"""
from __future__ import annotations

import os
import re
import uuid
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

logger = logging.getLogger('support_chat')

# ─── MongoDB ────────────────────────────────────────────────────────────
_mongo = AsyncIOMotorClient(os.environ['MONGO_URL'])
_db = _mongo[os.environ.get('DB_NAME', 'thai2drive')]
_chat_col = _db['support_chats']
_escal_col = _db['support_escalations']

# ─── Email config (SMTP) ────────────────────────────────────────────────
# Optional — set these in backend/.env to enable emails:
#   SUPPORT_SMTP_HOST=smtp.gmail.com
#   SUPPORT_SMTP_PORT=587
#   SUPPORT_SMTP_USER=your@gmail.com
#   SUPPORT_SMTP_PASS=app_password_here
#   SUPPORT_EMAIL_TO=lexuz.zxc@gmail.com
SUPPORT_EMAIL_TO = os.environ.get('SUPPORT_EMAIL_TO', 'lexuz.zxc@gmail.com')
_SMTP_HOST = os.environ.get('SUPPORT_SMTP_HOST')
_SMTP_PORT = int(os.environ.get('SUPPORT_SMTP_PORT', '587'))
_SMTP_USER = os.environ.get('SUPPORT_SMTP_USER')
_SMTP_PASS = os.environ.get('SUPPORT_SMTP_PASS')

# ─── LLM (OpenAI) ───────────────────────────────────────────────────────
from openai import AsyncOpenAI  # noqa: E402

LLM_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('EMERGENT_LLM_KEY', '')
LLM_MODEL = 'gpt-4o-mini'  # fast, cheap, multilingual — perfect for support
_openai_client: AsyncOpenAI | None = AsyncOpenAI(api_key=LLM_KEY) if LLM_KEY else None

SYSTEM_PROMPT = """You are the official support assistant for **Thai2Drive**,
a mobile app that helps Thai people in Norway pass the Norwegian driving
theory test. The app has:
- 500+ questions in Thai, Norwegian and English
- A free tier with 10 questions per day (resets daily)
- Premium plans: 199 NOK/month, 399 NOK/3 months, 699 NOK lifetime
- An exam mode (45 questions, 90 min)

Your rules:
1. ONLY help with Thai2Drive-related questions. Politely refuse off-topic requests.
2. Be short, polite, warm.
3. Answer in the SAME language the user wrote in. Support Thai, Norwegian and English.
4. Never promise refunds directly — only say "We'll forward this to our team."
5. Never invent policies. If you don't know, escalate.
6. If the user mentions a complaint, refund, payment problem, crashes, legal issue,
   privacy/data-deletion request, or sounds angry → reassure them and tell them
   the message has been forwarded to the support team.

Common topics you can answer directly (keep answers short):
- **Login issues**: Tell them to try password reset via the app. If that fails,
  they should email the team.
- **Password reset**: The app sends a reset code — check spam folder.
- **Premium not activated**: Ask them to tap "Restore purchase" in the paywall,
  or relaunch the app. If still failing, escalate.
- **Cancel subscription**: Android → Google Play → Subscriptions → Thai2Drive → Cancel.
  iOS → Settings → Apple ID → Subscriptions → Thai2Drive → Cancel.
- **Report wrong question**: Ask them to send a screenshot and the question.
- **Delete account/data**: Send email with subject "Delete account" — full deletion within 30 days.
- **Languages**: Thai, Norwegian, English — switch any time in the app.
- **Use without account**: Yes, no account needed; progress stored only on device.

Keep every reply under 120 words.
"""


# ─── Escalation detection ───────────────────────────────────────────────
# Lightweight keyword + AI-based detection.
_ESCALATION_KEYWORDS = {
    # Money / billing
    'refund', 'pengene tilbake', 'refundering', 'refund me', 'money back',
    'charged twice', 'dobbelt belastet', 'คืนเงิน', 'ขอเงินคืน',
    # Premium activation
    'premium ikke aktivert', 'premium not working', 'premium not activated',
    'premium doesn\'t work', 'ไม่ได้พรีเมียม', 'พรีเมียมไม่ทำงาน', 'betalte men',
    'premium virker ikke',
    # Bugs — serious
    'crash', 'krasjer', 'kræsjer', 'broken', 'ødelagt', 'virker ikke', 'doesn\'t work',
    'can\'t open', 'kommer ikke inn', 'แอปพัง', 'เปิดไม่ได้',
    # Legal / privacy / data deletion (multi-lang)
    'gdpr', 'slett kontoen', 'slett min konto', 'delete my account', 'delete my data',
    'delete account', 'ลบบัญชี', 'ลบข้อมูล',
    'lawsuit', 'saksøke', 'sue', 'rettslig', 'ฟ้อง',
    # Tone
    'scam', 'fraud', 'svindel', 'thieves', 'useless', 'worst', 'terrible', 'horrible',
    'angry', 'furious', 'unacceptable', 'uakseptabelt', 'โกง',
    # Complaint wording
    'complaint', 'klage', 'klager', 'ร้องเรียน',
}

_COMPLAINT_RE = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in _ESCALATION_KEYWORDS) + r')\b',
    re.IGNORECASE
)


def _quick_escalation_check(msg: str) -> tuple[bool, str, str]:
    """Returns (needs_escalation, category, priority). Fast keyword check."""
    low = msg.lower()
    match = _COMPLAINT_RE.search(low)
    if not match:
        return False, 'general', 'low'
    hit = match.group(1).lower()
    # Categorise
    if any(k in hit for k in ('refund', 'money', 'charged', 'pengene', 'คืนเงิน', 'dobbelt')):
        return True, 'billing', 'high'
    if any(k in hit for k in ('premium',)):
        return True, 'premium_activation', 'high'
    if any(k in hit for k in ('crash', 'broken', 'doesn\'t work', 'ødelagt', 'virker ikke', 'krasjer')):
        return True, 'bug_report', 'medium'
    if any(k in hit for k in ('gdpr', 'delete', 'slett', 'privacy', 'lawsuit', 'saksøke')):
        return True, 'legal_privacy', 'high'
    if any(k in hit for k in ('scam', 'fraud', 'svindel', 'angry', 'furious')):
        return True, 'angry_user', 'high'
    if 'complaint' in hit or 'klage' in hit:
        return True, 'complaint', 'medium'
    return True, 'general', 'medium'


# ─── Email sending ──────────────────────────────────────────────────────
def _send_escalation_email(session_id: str, user_message: str,
                            ai_reply: str, category: str, priority: str,
                            conversation: List[dict]) -> tuple[bool, str]:
    """Returns (success, info)."""
    if not (_SMTP_HOST and _SMTP_USER and _SMTP_PASS):
        return False, 'SMTP not configured — logged only'

    subject = f"[Thai2Drive Support] {priority.upper()} – {category}"
    body_lines = [
        f"⚠️  ESCALATED SUPPORT MESSAGE",
        f"",
        f"Priority : {priority.upper()}",
        f"Category : {category}",
        f"Time     : {datetime.now(timezone.utc).isoformat()}",
        f"Session  : {session_id}",
        f"",
        f"──── USER MESSAGE ─────────────────────────",
        user_message,
        f"",
        f"──── AI AUTO-REPLY ──────────────────────────",
        ai_reply,
        f"",
        f"──── CONVERSATION LOG ───────────────────────",
    ]
    for m in conversation[-10:]:
        role = m.get('role', '?')
        content = m.get('content', '')
        body_lines.append(f"[{role}] {content}")
    body_lines.extend([
        f"",
        f"───────────────────────────────────────────",
        f"Reply to the user by finding their address in MongoDB → support_chats collection, filtered by session_id.",
    ])

    msg = MIMEText('\n'.join(body_lines), 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = _SMTP_USER
    msg['To'] = SUPPORT_EMAIL_TO

    # Try up to 3 times — Yahoo / some SMTP servers drop connections sporadically
    import time
    last_err = None
    for attempt in range(1, 4):
        try:
            with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT, timeout=12) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(_SMTP_USER, _SMTP_PASS)
                s.sendmail(_SMTP_USER, [SUPPORT_EMAIL_TO], msg.as_string())
            return True, f'sent (attempt {attempt})'
        except Exception as e:
            last_err = e
            logger.warning('Email send attempt %d failed: %s', attempt, e)
            if attempt < 3:
                time.sleep(1.5 * attempt)

    return False, f'SMTP error after 3 attempts: {last_err}'


# ─── API ────────────────────────────────────────────────────────────────
support_chat_router = APIRouter()


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description='existing session, or blank for new')
    message: str = Field(min_length=1, max_length=2000)
    user_email: Optional[str] = Field(default=None, max_length=200)
    language: Optional[str] = Field(default='no')


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    escalated: bool
    category: str
    priority: str


@support_chat_router.post('/support/chat', response_model=ChatResponse)
async def support_chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or f"s_{uuid.uuid4().hex[:16]}"
    user_msg = req.message.strip()

    # 1) Fast keyword-based escalation check
    escalated, category, priority = _quick_escalation_check(user_msg)

    # 2) Load prior conversation (last 10 messages in this session)
    prior = await _chat_col.find(
        {'session_id': session_id}
    ).sort('ts', 1).to_list(length=20)
    conversation = [{'role': m['role'], 'content': m['content']} for m in prior]

    # 3) Ask LLM
    try:
        if not _openai_client:
            raise RuntimeError('OPENAI_API_KEY not configured')
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation)
        messages.append({"role": "user", "content": user_msg})
        resp = await _openai_client.chat.completions.create(
            model=LLM_MODEL, messages=messages, max_tokens=320
        )
        reply_text = (resp.choices[0].message.content or '').strip()
        if not reply_text:
            reply_text = _fallback_reply(req.language or 'no')
    except Exception as e:
        logger.exception('LLM failed')
        reply_text = _fallback_reply(req.language or 'no')

    # 4) Persist both messages
    now = datetime.now(timezone.utc)
    await _chat_col.insert_many([
        {
            'session_id': session_id,
            'role': 'user',
            'content': user_msg,
            'user_email': req.user_email,
            'language': req.language,
            'ts': now,
            'escalated': escalated,
            'category': category,
            'priority': priority,
        },
        {
            'session_id': session_id,
            'role': 'assistant',
            'content': reply_text,
            'ts': now,
        },
    ])

    # 5) Escalation → DB log always; EMAIL only for HIGH priority with 10-min cooldown
    if escalated:
        conversation_for_email = conversation + [
            {'role': 'user', 'content': user_msg},
            {'role': 'assistant', 'content': reply_text},
        ]

        email_sent = False
        email_info = 'medium/low → db only'

        if priority == 'high':
            # Cooldown: max 1 email per user_email OR session_id per 10 minutes
            from datetime import timedelta
            cutoff = now - timedelta(minutes=10)
            cooldown_filter = {
                'email_sent': True,
                'ts': {'$gte': cutoff},
                '$or': [
                    {'user_email': req.user_email} if req.user_email else {'_none': True},
                    {'session_id': session_id},
                ],
            }
            recent_email = await _escal_col.find_one(cooldown_filter)

            if recent_email:
                email_info = 'cooldown: user already notified in last 10 min'
                logger.info('Skipping email (cooldown) for session=%s', session_id)
            else:
                email_sent, email_info = _send_escalation_email(
                    session_id, user_msg, reply_text, category, priority, conversation_for_email
                )

        await _escal_col.insert_one({
            'session_id': session_id,
            'user_message': user_msg,
            'ai_reply': reply_text,
            'user_email': req.user_email,
            'category': category,
            'priority': priority,
            'ts': now,
            'email_sent': email_sent,
            'email_info': email_info,
            'resolved': False,
        })

    return ChatResponse(
        session_id=session_id,
        reply=reply_text,
        escalated=escalated,
        category=category,
        priority=priority,
    )


def _fallback_reply(lang: str) -> str:
    if lang == 'th':
        return ('ขอโทษค่ะ ระบบไม่สามารถตอบได้ในขณะนี้ '
                'ทีมงานได้รับข้อความของคุณแล้ว และจะติดต่อกลับทางอีเมลที่ลงทะเบียนไว้ค่ะ')
    if lang == 'en':
        return ('Sorry, I cannot answer right now. Your message has been forwarded '
                'to our team — please email support@thai2drive.com if urgent.')
    return ('Beklager, jeg får ikke svart akkurat nå. Meldingen din er videresendt '
            'til supportteamet. Du kan også sende e-post til lexuz.zxc@gmail.com.')


# ─── Admin helpers ──────────────────────────────────────────────────────
@support_chat_router.get('/support/chat/admin/escalations')
async def list_escalations(limit: int = 50):
    """Fallback admin log — readable even if email sending failed."""
    docs = await _escal_col.find().sort('ts', -1).to_list(length=limit)
    for d in docs:
        d['_id'] = str(d['_id'])
        d['ts'] = d['ts'].isoformat() if hasattr(d.get('ts'), 'isoformat') else str(d.get('ts'))
    return {'count': len(docs), 'items': docs}
