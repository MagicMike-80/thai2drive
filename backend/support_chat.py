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

load_dotenv()

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

# ─── LLM (LiteLLM → Anthropic) ──────────────────────────────────────────
import litellm  # noqa: E402

litellm.suppress_debug_info = True  # keep Railway logs clean
LLM_KEY = os.environ.get('ANTHROPIC_API_KEY', '').strip()
LLM_MODEL = os.environ.get('SUPPORT_LLM_MODEL', 'claude-haiku-4-5-20251001')  # override via Railway env var if needed

_key_source = 'ANTHROPIC_API_KEY' if LLM_KEY else None

# Fallback to OpenAI if Anthropic key is stale/missing
if not LLM_KEY or LLM_KEY.startswith("sk-ant-api03-dTiG"):
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        LLM_KEY = openai_key
        LLM_MODEL = "gpt-4o-mini"
        _key_source = "OPENAI_API_KEY"
        logger.info("Using OpenAI fallback for Support chat — model=%s", LLM_MODEL)

# ─── Startup diagnostic ──────────────────────────────────────────────────
if LLM_KEY:
    logger.info('Support chat LLM ready — provider=litellm key_source=%s model=%s', _key_source, LLM_MODEL)
else:
    logger.error(
        'Support chat LLM NOT configured — '
        'keys absent. All requests will use fallback.'
    )

SYSTEM_PROMPT = """You are the official support assistant for **Thai2Drive**,
a mobile app that helps Thai people in Norway pass the Norwegian driving
theory test. The app has:
- 500+ questions in Thai, Norwegian and English
- A free tier with 10 questions per day (resets daily)
- Premium plans: 99 NOK/month, 299 NOK/3 months, 699 NOK lifetime
- An exam mode (45 questions, 90 min)

Your rules:
1. ONLY help with Thai2Drive-related questions. Politely refuse off-topic requests.
2. Be short, polite, warm.
3. Support Thai, Norwegian, and English.
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
def _build_escalation_body(session_id: str, user_message: str,
                            ai_reply: str, category: str, priority: str,
                            conversation: List[dict]) -> str:
    """Build plain text body for escalation email (shared by all senders)."""
    lines = [
        "⚠️  ESCALATED SUPPORT MESSAGE",
        "",
        f"Priority : {priority.upper()}",
        f"Category : {category}",
        f"Time     : {datetime.now(timezone.utc).isoformat()}",
        f"Session  : {session_id}",
        "",
        "──── USER MESSAGE ─────────────────────────",
        user_message,
        "",
        "──── AI AUTO-REPLY ──────────────────────────",
        ai_reply,
        "",
        "──── CONVERSATION LOG ───────────────────────",
    ]
    for m in conversation[-10:]:
        role = m.get('role', '?')
        content = m.get('content', '')
        lines.append(f"[{role}] {content}")
    lines.extend([
        "",
        "───────────────────────────────────────────",
        "Reply to the user by finding their address in MongoDB → support_chats collection, filtered by session_id.",
    ])
    return '\n'.join(lines)


def _send_via_sendgrid(subject: str, body_text: str) -> tuple[bool, str]:
    """Send email via SendGrid HTTP API (works on Railway — HTTPS port 443)."""
    import urllib.request
    import urllib.error
    import json as _json

    api_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    if not api_key:
        return False, "SENDGRID_API_KEY not set"

    from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@thai2drive.no").strip()
    from_name = os.environ.get("SENDGRID_FROM_NAME", "Thai2Drive").strip()

    payload = _json.dumps({
        "personalizations": [{"to": [{"email": SUPPORT_EMAIL_TO}]}],
        "from": {"email": from_email, "name": from_name},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body_text}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            logger.info("sendgrid_sent_ok to=%s status=%d",
                         SUPPORT_EMAIL_TO, resp.status)
            return True, "sent"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        logger.error("sendgrid_failed status=%d body=%s", exc.code, body[:300])
        return False, f"SendGrid HTTP {exc.code}: {body[:200]}"
    except Exception as exc:
        logger.error("sendgrid_failed type=%s detail=%s", type(exc).__name__, exc)
        return False, str(exc)


def _send_escalation_email(session_id: str, user_message: str,
                            ai_reply: str, category: str, priority: str,
                            conversation: List[dict]) -> tuple[bool, str]:
    """Returns (success, info). Uses SendGrid HTTPS API first, falls back to SMTP."""
    subject = f"[Thai2Drive Support] {priority.upper()} – {category}"
    body_text = _build_escalation_body(session_id, user_message, ai_reply, category, priority, conversation)

    # Try SendGrid first (works on Railway — HTTPS port 443)
    sendgrid_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    if sendgrid_key:
        sent, info = _send_via_sendgrid(subject, body_text)
        if sent:
            return True, info
        logger.warning("SendGrid failed (%s), falling back to SMTP", info)

    # Fallback to SMTP (blocked on Railway but works from other hosts)
    if not (_SMTP_HOST and _SMTP_USER and _SMTP_PASS):
        return False, 'SMTP not configured — logged only'

    msg = MIMEText(body_text, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = _SMTP_USER
    msg['To'] = SUPPORT_EMAIL_TO

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
            return True, f'sent via SMTP (attempt {attempt})'
        except Exception as e:
            last_err = e
            logger.warning('SMTP email attempt %d failed: %s', attempt, e)
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
        if not LLM_KEY:
            raise RuntimeError('ANTHROPIC_API_KEY not configured')
        lang_map = {'no': 'Norwegian', 'th': 'Thai', 'en': 'English'}
        ui_lang = lang_map.get(req.language or 'no', 'Norwegian')
        lang_rule = (
            f"LANGUAGE RULE — highest priority, overrides all other instructions:\n"
            f"1. Detect the language of the user's CURRENT message.\n"
            f"2. Reply in that detected language.\n"
            f"3. If the message is too short or ambiguous to detect a language, "
            f"reply in {ui_lang} (the user's current UI language).\n"
            f"4. Ignore the language of previous messages when choosing your reply language.\n"
            f"5. Never mix languages within a single reply."
        )
        system_with_lang = lang_rule + "\n\n" + SYSTEM_PROMPT.rstrip()
        messages = [{"role": "system", "content": system_with_lang}]
        messages.extend(conversation)
        messages.append({"role": "user", "content": user_msg})
        resp = await litellm.acompletion(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=320,
            api_key=LLM_KEY,
        )
        reply_text = (resp.choices[0].message.content or '').strip()
        if not reply_text:
            reply_text = _fallback_reply(req.language or 'no')
    except Exception as e:
        logger.error("LiteLLM call failed [%s]: %s", type(e).__name__, e)
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
                'to our team — please email lexuz.zxc@gmail.com if urgent.')
    return ('Beklager, jeg får ikke svart akkurat nå. Meldingen din er videresendt '
            'til supportteamet. Du kan også sende e-post til lexuz.zxc@gmail.com.')


# ─── Diagnostic ─────────────────────────────────────────────────────────
@support_chat_router.get('/support/status')
async def support_status():
    """Diagnostic: verify LLM client configuration in production.
    Does not expose key values — only reports presence and source."""
    return {
        'llm_client_configured': bool(LLM_KEY),
        'llm_key_present': bool(LLM_KEY),
        'llm_key_source': _key_source,
        'provider': 'litellm/anthropic',
        'model': LLM_MODEL,
    }


# ─── Admin helpers ──────────────────────────────────────────────────────
@support_chat_router.get('/support/chat/admin/escalations')
async def list_escalations(limit: int = 50):
    """Fallback admin log — readable even if email sending failed."""
    docs = await _escal_col.find().sort('ts', -1).to_list(length=limit)
    for d in docs:
        d['_id'] = str(d['_id'])
        d['ts'] = d['ts'].isoformat() if hasattr(d.get('ts'), 'isoformat') else str(d.get('ts'))
    return {'count': len(docs), 'items': docs}
