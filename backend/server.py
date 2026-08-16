from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, UploadFile, File, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse as FastAPIFileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import os
import logging
import hashlib
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uuid
import re
import jwt
import time
import asyncio
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from passlib.context import CryptContext
import usage as usage_mod

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Fail-soft på modulnivå: en manglende miljøvariabel skal ikke drepe prosessen
# under import. Da rekker aldri /api/health å svare, og Railway rapporterer bare
# «1/1 replicas never became healthy» uten å vise hva som mangler.
# Med .get logges den nøyaktige årsaken, appen booter, og /api/health svarer
# 200 med db=disconnected slik at feilen er synlig i stedet for stum.
_boot_log = logging.getLogger("boot")
mongo_url = os.environ.get('MONGO_URL')
_db_name = os.environ.get('DB_NAME')
if not mongo_url:
    _boot_log.critical("MONGO_URL mangler i miljøet — databasen blir utilgjengelig. Sett den i Railway.")
    mongo_url = "mongodb://127.0.0.1:27017"
if not _db_name:
    _boot_log.critical("DB_NAME mangler i miljøet — faller tilbake til 'thai2drive'. Sett den i Railway.")
    _db_name = "thai2drive"
client = AsyncIOMotorClient(mongo_url)
db = client[_db_name]

JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback-secret-change-me')
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 168  # 7 days

# ── Gratisuken («Value before payment») ────────────────────────────────────────
# Prøveperioden styres 100 % i vår egen MongoDB. Stripe/betalingsmuren slår først
# inn når prøveuken er utløpt. Én gratisuke per e-post OG per device_id.
TRIAL_DAYS = 7

# ── Admin bootstrap secret ─────────────────────────────────────────────────────
# Required header: X-Admin-Secret: <value>
# If not set in env → /admin/add is permanently blocked (safe default).
ADMIN_BOOTSTRAP_SECRET = os.environ.get('ADMIN_BOOTSTRAP_SECRET', '')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def normalize_question(q: dict) -> dict:
    """Convert v1 flat schema to v2 nested schema expected by the frontend and dynamically shuffle options."""
    # Create a copy to avoid side-effects on shared memory
    q = dict(q)
    q.pop("_id", None)
    
    # Ensure it's in v2 structure
    if not isinstance(q.get("question"), dict):
        # Convert v1 → v2
        normalized = {
            "id": q.get("id", ""),
            "question": {
                "no": q.get("question_text_no", ""),
                "th": q.get("question_text_th", ""),
                "en": q.get("question_text_en", ""),
            },
            "options": [
                {"id": "A", "text": {"no": q.get("answer_a_no", ""), "th": q.get("answer_a_th", ""), "en": q.get("answer_a_en", "")}},
                {"id": "B", "text": {"no": q.get("answer_b_no", ""), "th": q.get("answer_b_th", ""), "en": q.get("answer_b_en", "")}},
                {"id": "C", "text": {"no": q.get("answer_c_no", ""), "th": q.get("answer_c_th", ""), "en": q.get("answer_c_en", "")}},
                {"id": "D", "text": {"no": q.get("answer_d_no", ""), "th": q.get("answer_d_th", ""), "en": q.get("answer_d_en", "")}},
            ],
            "correctOptionId": q.get("correct_answer", "A"),
            "explanation": {
                "no": q.get("explanation_no", ""),
                "th": q.get("explanation_th", ""),
                "en": q.get("explanation_en", ""),
            },
            "bildeUrl": q.get("bildeUrl") or q.get("image_url") or None,
            "category": q.get("category", ""),
            "difficulty": q.get("difficulty", "medium"),
            "active": q.get("active", True),
            "created_at": q.get("created_at", ""),
        }
    else:
        import copy
        normalized = copy.deepcopy(q)

    # Dynamic option shuffling
    options = normalized.get("options", [])
    correct_id = normalized.get("correctOptionId")
    if options and correct_id:
        items = []
        for o in options:
            is_correct = (o.get("id") == correct_id)
            opt_data = {k: v for k, v in o.items() if k != "id"}
            items.append((opt_data, is_correct))
        
        import random as _random
        _random.shuffle(items)
        
        # Reconstruct options with A, B, C, D IDs
        shuffled_options = []
        letters = ["A", "B", "C", "D"][:len(items)]
        new_correct_id = correct_id
        for letter, (opt_data, is_correct) in zip(letters, items):
            new_opt = {"id": letter}
            new_opt.update(opt_data)
            shuffled_options.append(new_opt)
            if is_correct:
                new_correct_id = letter
        
        normalized["options"] = shuffled_options
        normalized["correctOptionId"] = new_correct_id

    return normalized

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ── Segment analytics ──────────────────────────────────────────────────────────────
import analytics as segment_analytics
SEGMENT_WRITE_KEY = os.environ.get('SEGMENT_WRITE_KEY', '')
if SEGMENT_WRITE_KEY:
    segment_analytics.write_key = SEGMENT_WRITE_KEY
    logger.info("Segment analytics initialized (write_key set)")
else:
    logger.warning("SEGMENT_WRITE_KEY not set — analytics disabled")

PUBLIC_PRICING_FALLBACK = {
    "monthly": {
        "id": "monthly",
        "stripe_product_name": "Thai2Drive Premium",
        "label": {"no": "Månedlig", "th": "รายเดือน", "en": "Monthly"},
        "amount": 199,
        "currency": "NOK",
        "display": "199 kr",
        "period": {"no": "per måned", "th": "ต่อเดือน", "en": "per month"},
    },
    "three_months": {
        "id": "three_months",
        "stripe_product_name": "Thai2Drive 3 Months",
        "label": {"no": "3 måneder", "th": "3 เดือน", "en": "3 months"},
        "amount": 399,
        "currency": "NOK",
        "display": "399 kr",
        "period": {"no": "per 3 måneder", "th": "ต่อ 3 เดือน", "en": "per 3 months"},
    },
    "lifetime": {
        "id": "lifetime",
        "stripe_product_name": "Thai2Drive Lifetime",
        "label": {"no": "Livstid", "th": "ตลอดชีพ", "en": "Lifetime"},
        "amount": 699,
        "currency": "NOK",
        "display": "699 kr",
        "period": {"no": "engangsbetaling", "th": "จ่ายครั้งเดียว", "en": "one-time payment"},
    },
}
_pricing_cache = {"ts": 0.0, "data": None}

ACCESS_GUEST_TOTAL_LIMIT = 5
ACCESS_REGISTERED_DAILY_LIMIT = 10
ACCESS_OSLO_TZ = ZoneInfo("Europe/Oslo")

# ==================== MODELS ====================

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text_no: str
    question_text_th: str
    question_text_en: str
    answer_a_no: str
    answer_b_no: str
    answer_c_no: str
    answer_d_no: str
    answer_a_th: str
    answer_b_th: str
    answer_c_th: str
    answer_d_th: str
    answer_a_en: str
    answer_b_en: str
    answer_c_en: str
    answer_d_en: str
    correct_answer: str
    explanation_no: str
    explanation_th: str
    explanation_en: str
    category: str
    difficulty: str = "medium"
    image_url: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class QuestionCreate(BaseModel):
    question_text_no: str
    question_text_th: str
    question_text_en: str
    answer_a_no: str
    answer_b_no: str
    answer_c_no: str
    answer_d_no: str
    answer_a_th: str
    answer_b_th: str
    answer_c_th: str
    answer_d_th: str
    answer_a_en: str
    answer_b_en: str
    answer_c_en: str
    answer_d_en: str
    correct_answer: str
    explanation_no: str
    explanation_th: str
    explanation_en: str
    category: str
    difficulty: str = "medium"
    image_url: Optional[str] = None

class UserProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    total_questions_answered: int = 0
    correct_answers: int = 0
    questions_by_category: Dict[str, Dict[str, int]] = {}
    last_activity: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    mode: str
    category: Optional[str] = None
    total_questions: int
    correct_answers: int
    score_percentage: float
    passed: Optional[bool] = None
    questions_answered: List[Dict[str, Any]]
    started_at: str
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class QuizAttemptCreate(BaseModel):
    client_attempt_id: Optional[str] = None
    device_id: str
    mode: str
    category: Optional[str] = None
    total_questions: int
    correct_answers: int
    score_percentage: float
    passed: Optional[bool] = None
    questions_answered: List[Dict[str, Any]]
    started_at: str
    completed_at: Optional[str] = None

class Bookmark(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    question_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class BookmarkCreate(BaseModel):
    device_id: str
    question_id: str

class AdminUser(BaseModel):
    email: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AdminCheckRequest(BaseModel):
    email: str

# ==================== AUTH MODELS ====================

class AuthSignup(BaseModel):
    name: Optional[str] = None        # display name (optional)
    email: str
    password: str
    device_id: Optional[str] = None   # carry over guest history

    @validator('email')
    def validate_email(cls, v):
        v = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class AuthLogin(BaseModel):
    email: str
    password: str
    device_id: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        return v.strip().lower()

class ForgotPasswordRequest(BaseModel):
    email: str

    @validator('email')
    def validate_email(cls, v):
        return v.strip().lower()

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

    @validator('email')
    def validate_email(cls, v):
        return v.strip().lower()

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class AccessConsumeRequest(BaseModel):
    device_id: str
    question_id: Optional[str] = None
    mode: Optional[str] = "practice"
    category: Optional[str] = None
    event_id: Optional[str] = None


class CheckoutSessionRequest(BaseModel):
    plan_id: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    device_id: Optional[str] = None

    @validator("plan_id")
    def validate_plan_id(cls, v):
        v = (v or "").strip()
        if v not in ("monthly", "three_months", "lifetime"):
            raise ValueError("Invalid plan")
        return v

# ==================== AUTH HELPERS ====================

def create_token(
    user_id: str,
    email: str,
    is_premium: bool = False,
    premium_until: Optional[str] = None,
    premium_status: str = "none",
) -> str:
    # Tokenet lever i 168 timer (uendret). Men tilgangen kan utløpe før tokenet gjør
    # det — en gratisuke tar slutt, et abonnement går ut. Derfor bærer payloaden sin
    # egen utløpsdato: `premium_until`. usage.premium_is_active() leser den ved hvert
    # kall, så premium-porten stenger i tide uten at brukeren blir logget ut.
    payload = {
        "sub": user_id,
        "email": email,
        "is_premium": is_premium,
        "premium_until": premium_until,   # ISO-8601 UTC, eller None ved livstid/ingen tilgang
        "premium_status": premium_status,  # trialing | active | expired | none
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("is_premium") and payload.get("premium_until"):
            try:
                exp_dt = datetime.fromisoformat(str(payload["premium_until"]).replace("Z", "+00:00"))
                if exp_dt < datetime.now(timezone.utc):
                    payload["is_premium"] = False
                    payload["premium_status"] = "expired"
            except Exception:
                pass
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Returns full user dict from DB, or None. Used by legacy /access/* endpoints."""
    if not credentials:
        return None
    payload = verify_token(credentials.credentials)
    if not payload:
        return None
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
    return user


async def optional_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """Returns decoded JWT payload (with is_premium), or None for guests. Lightweight — no DB hit."""
    if not credentials:
        return None
    return verify_token(credentials.credentials)  # None if expired/invalid


async def _find_user_by_email(email: str, projection: Optional[dict] = None) -> Optional[dict]:
    normalized = (email or "").strip().lower()
    user = await db.users.find_one({"email": normalized}, projection)
    if user:
        return user
    # Legacy safety: some older records may have been saved before strict
    # lowercasing. Auth must still find exactly the same email regardless of case.
    return await db.users.find_one(
        {"email": {"$regex": f"^{re.escape(normalized)}$", "$options": "i"}},
        projection,
    )


def generate_reset_code() -> str:
    import random
    return str(random.randint(100000, 999999))


def _email_hash(email: str) -> str:
    return hashlib.sha256((email or "").strip().lower().encode("utf-8")).hexdigest()[:12]


def _masked_email(email: str) -> str:
    email = (email or "").strip().lower()
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if not local:
        return "***@" + domain
    return local[:1] + "***@" + domain


def _auth_error_key(key: str, no: str, th: str, en: str, status_code: int = 400) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"key": key, "no": no, "th": th, "en": en},
    )


def _smtp_config() -> dict:
    # Prefer RESET_SMTP_* vars; fall back to SUPPORT_SMTP_* vars.
    reset_host = os.environ.get("RESET_SMTP_HOST", "").strip()
    support_host = os.environ.get("SUPPORT_SMTP_HOST", "").strip()
    source = "reset" if reset_host else ("support" if support_host else "none")
    return {
        "source": source,
        "host": (reset_host or support_host),
        "port": int(os.environ.get("RESET_SMTP_PORT") or os.environ.get("SUPPORT_SMTP_PORT") or "587"),
        "user": (os.environ.get("RESET_SMTP_USER") or os.environ.get("SUPPORT_SMTP_USER") or "").strip(),
        "password": (os.environ.get("RESET_SMTP_PASS") or os.environ.get("SUPPORT_SMTP_PASS") or "").strip(),
        "from_email": (os.environ.get("RESET_EMAIL_FROM") or os.environ.get("SUPPORT_SMTP_USER") or "").strip(),
        "from_name": os.environ.get("RESET_EMAIL_FROM_NAME", "Thai2Drive"),
    }


def _send_via_sendgrid(to_email: str, code: str) -> tuple[bool, str]:
    """Send reset email via SendGrid HTTP API (works on Railway — HTTPS port 443)."""
    import urllib.request, json as _json
    _el = logging.getLogger("reset_email")
    api_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    if not api_key:
        return False, "SENDGRID_API_KEY not set"

    from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@thai2drive.no").strip()
    from_name = os.environ.get("SENDGRID_FROM_NAME", "Thai2Drive").strip()
    body_text = (
        "Hei,\n\n"
        f"Tilbakestillingskoden din for Thai2Drive er: {code}\n\n"
        "Koden er gyldig i 15 minutter. Hvis du ikke ba om dette, kan du ignorere denne e-posten.\n\n"
        "Thai2Drive\n\n"
        "สวัสดีครับ/ค่ะ\n\n"
        f"รหัสรีเซ็ตรหัสผ่าน Thai2Drive ของคุณคือ: {code}\n\n"
        "รหัสนี้ใช้ได้ 15 นาที หากคุณไม่ได้ขอรีเซ็ตรหัสผ่าน กรุณาเพิกเฉยต่ออีเมลนี้\n"
    )
    payload = _json.dumps({
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": from_name},
        "subject": "Thai2Drive password reset code",
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
            _el.info("sendgrid_sent_ok to=%s status=%d", _masked_email(to_email), resp.status)
            return True, "sent"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        _el.error("sendgrid_failed status=%d body=%s", exc.code, body[:300])
        return False, f"SendGrid HTTP {exc.code}: {body[:200]}"
    except Exception as exc:
        _el.error("sendgrid_failed type=%s detail=%s", type(exc).__name__, exc)
        return False, str(exc)


def _send_via_resend(to_email: str, code: str) -> tuple[bool, str]:
    """Send reset email using Resend HTTP API."""
    import urllib.request, json as _json
    _el = logging.getLogger("reset_email")
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    if not api_key:
        return False, "RESEND_API_KEY not set"

    from_addr = os.environ.get("RESEND_FROM", "Thai2Drive <onboarding@resend.dev>").strip()
    body_text = (
        "Hei,\n\n"
        f"Tilbakestillingskoden din for Thai2Drive er: {code}\n\n"
        "Koden er gyldig i 15 minutter. Hvis du ikke ba om dette, kan du ignorere denne e-posten.\n\n"
        "Thai2Drive\n\n"
        "สวัสดีครับ/ค่ะ\n\n"
        f"รหัสรีเซ็ตรหัสผ่าน Thai2Drive ของคุณคือ: {code}\n\n"
        "รหัสนี้ใช้ได้ 15 นาที หากคุณไม่ได้ขอรีเซ็ตรหัสผ่าน กรุณาเพิกเฉยต่ออีเมลนี้\n"
    )
    payload = _json.dumps({
        "from": from_addr,
        "to": [to_email],
        "subject": "Thai2Drive password reset code",
        "text": body_text,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            _el.info("resend_sent_ok to=%s status=%d", _masked_email(to_email), resp.status)
            return True, "sent"
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        _el.error("resend_failed status=%d body=%s", exc.code, body[:300])
        return False, f"Resend HTTP {exc.code}: {body[:200]}"
    except Exception as exc:
        _el.error("resend_failed type=%s detail=%s", type(exc).__name__, exc)
        return False, str(exc)


def _send_password_reset_email_sync(to_email: str, code: str) -> tuple[bool, str]:
    _el = logging.getLogger("reset_email")

    # Primary: SendGrid (confirmed working on Railway)
    sendgrid_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    if sendgrid_key:
        _el.info("email_send_attempt method=sendgrid to=%s", _masked_email(to_email))
        return _send_via_sendgrid(to_email, code)

    # Secondary: Resend (may be blocked by Cloudflare on some Railway IPs)
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    if resend_key:
        _el.info("email_send_attempt method=resend to=%s", _masked_email(to_email))
        return _send_via_resend(to_email, code)

    # Fallback: SMTP (only works if outbound port 587 is open — blocked on Railway)
    cfg = _smtp_config()
    _el.info(
        "email_send_attempt method=smtp source=%s host=%s port=%d user=%s",
        cfg["source"],
        cfg["host"] or "(not set)",
        cfg["port"],
        _masked_email(cfg["user"]) if cfg["user"] else "(not set)",
    )

    if not (cfg["host"] and cfg["user"] and cfg["password"]):
        _el.error(
            "send_failed reason=smtp_not_configured source=%s host=%s user=%s pass=%s",
            cfg["source"], bool(cfg["host"]), bool(cfg["user"]), bool(cfg["password"]),
        )
        return False, "SMTP not configured"

    from_email = cfg["from_email"] or cfg["user"]
    body = (
        "Hei,\n\n"
        f"Tilbakestillingskoden din for Thai2Drive er: {code}\n\n"
        "Koden er gyldig i 15 minutter. Hvis du ikke ba om dette, kan du ignorere denne e-posten.\n\n"
        "Thai2Drive\n\n"
        "สวัสดีครับ/ค่ะ\n\n"
        f"รหัสรีเซ็ตรหัสผ่าน Thai2Drive ของคุณคือ: {code}\n\n"
        "รหัสนี้ใช้ได้ 15 นาที หากคุณไม่ได้ขอรีเซ็ตรหัสผ่าน กรุณาเพิกเฉยต่ออีเมลนี้\n"
    )
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Thai2Drive password reset code"
    msg["From"] = f"{cfg['from_name']} <{from_email}>"
    msg["To"] = to_email

    try:
        _el.info("smtp_connect host=%s port=%d", cfg["host"], cfg["port"])
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(cfg["user"], cfg["password"])
            smtp.sendmail(from_email, [to_email], msg.as_string())
        _el.info("smtp_sent_ok host=%s to=%s", cfg["host"], _masked_email(to_email))
        return True, "sent"
    except smtplib.SMTPAuthenticationError as exc:
        code_num = exc.smtp_code if hasattr(exc, "smtp_code") else "?"
        _el.error("send_failed reason=auth_rejected smtp_code=%s host=%s", code_num, cfg["host"])
        return False, f"SMTP auth failed ({code_num})"
    except OSError as exc:
        _el.error("send_failed reason=network_error host=%s detail=%s", cfg["host"], exc)
        return False, f"Network error: {exc}"
    except Exception as exc:
        _el.error("send_failed reason=unexpected type=%s detail=%s", type(exc).__name__, exc)
        return False, str(exc)


async def _send_password_reset_email(to_email: str, code: str) -> tuple[bool, str]:
    return await asyncio.to_thread(_send_password_reset_email_sync, to_email, code)


def _parse_iso_utc(value) -> Optional[datetime]:
    """Tolk en lagret ISO-8601-streng som UTC. Returnerer None hvis den ikke kan tolkes."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _paid_premium_active(user: Optional[dict]) -> bool:
    """Betalt abonnement som fortsatt løper. Gratisuken telles ikke med her."""
    if not user or not user.get("is_premium"):
        return False
    expires_at = user.get("premium_expires_at")
    if expires_at:
        expires = _parse_iso_utc(expires_at)
        if expires is None or expires < datetime.now(timezone.utc):
            return False
    return True


def _user_has_active_trial(user: Optional[dict]) -> bool:
    if not user:
        return False
    expires = _parse_iso_utc(user.get("trial_expires_at"))
    return bool(expires and expires > datetime.now(timezone.utc))


def _user_trial_days_left(user: Optional[dict]) -> int:
    """Hele dager igjen av gratisuken. En påbegynt dag teller som én."""
    expires = _parse_iso_utc((user or {}).get("trial_expires_at"))
    if not expires:
        return 0
    seconds = (expires - datetime.now(timezone.utc)).total_seconds()
    if seconds <= 0:
        return 0
    return int((seconds + 86399) // 86400)


def _user_premium_status(user: Optional[dict]) -> str:
    """Statusen webappen leser: trialing | active | expired | none."""
    if not user:
        return "none"
    if user.get("is_admin") or _paid_premium_active(user):
        return "active"
    if _user_has_active_trial(user):
        return "trialing"
    if user.get("trial_used") or user.get("is_premium") or user.get("premium_expires_at"):
        return "expired"
    return "none"


def _access_expires_at(user: Optional[dict]) -> Optional[str]:
    """Når tilgangen faktisk tar slutt. None = livstid, admin eller ingen tilgang."""
    if not user or user.get("is_admin"):
        return None
    candidates = []
    if _paid_premium_active(user):
        paid = _parse_iso_utc(user.get("premium_expires_at"))
        if paid is None:
            return None  # betalt premium uten utløp = livstid
        candidates.append(paid)
    if _user_has_active_trial(user):
        trial = _parse_iso_utc(user.get("trial_expires_at"))
        if trial:
            candidates.append(trial)
    if not candidates:
        return None
    return max(candidates).isoformat()


def _user_has_active_premium(user: Optional[dict]) -> bool:
    """Full tilgang: admin, betalende kunde ELLER bruker med aktiv gratisuke."""
    if not user:
        return False
    if user.get("is_admin"):
        return True
    return _paid_premium_active(user) or _user_has_active_trial(user)


def _auth_user_payload(user: dict) -> dict:
    """Én felles brukerform for /auth/signup, /auth/login og /auth/me.

    De fire prøveuke-feltene er kontrakten webappen leser (se GRATISUKE i webapp.py):
    premium_status, premium_expires_at, trial_days_left, trial_used.
    """
    return {
        "id": user["id"],
        "name": user.get("name") or "",
        "email": user["email"],
        "is_admin": user.get("is_admin", False),
        "is_premium": _user_has_active_premium(user),
        "premium_status": _user_premium_status(user),
        "premium_expires_at": _access_expires_at(user),
        "trial_days_left": _user_trial_days_left(user),
        "trial_used": bool(user.get("trial_used")),
    }


async def _grant_trial_if_eligible(email: str, device_id: Optional[str], user_id: str) -> Optional[str]:
    """Gi 7 dagers gratisuke — men bare én gang per e-post OG per device_id.

    Returnerer ISO-utløpstidspunktet, eller None hvis kvoten allerede er brukt.
    Ingen kort, ingen Stripe: prøveperioden lever kun i vår egen database.
    """
    email_key = (email or "").strip().lower()
    match = [{"email": email_key}]
    if device_id:
        match.append({"device_id": device_id})
    already = await db.trial_grants.find_one({"$or": match})
    if already:
        return None

    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=TRIAL_DAYS)
    await db.trial_grants.insert_one({
        "email": email_key,
        "device_id": device_id or None,
        "user_id": user_id,
        "granted_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    })
    return expires.isoformat()


def _oslo_day_key(dt: Optional[datetime] = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return dt.astimezone(ACCESS_OSLO_TZ).date().isoformat()

def _access_scope(user: Optional[dict], device_id: str) -> tuple[str, str]:
    if user:
        return "user", user["id"]
    return "guest", device_id

def _access_policy_payload(user: Optional[dict], usage: Optional[dict]) -> dict:
    is_premium = _user_has_active_premium(user)
    is_registered = bool(user)
    tier = "premium" if is_premium else ("registered" if is_registered else "guest")
    today = _oslo_day_key()

    if is_premium:
        used = 0
        limit = None
        remaining = None
        reset_at = None
        can_answer = True
    elif is_registered:
        day = (usage or {}).get("day_key")
        used = int((usage or {}).get("daily_used", 0)) if day == today else 0
        limit = ACCESS_REGISTERED_DAILY_LIMIT
        remaining = max(0, limit - used)
        tomorrow = datetime.now(ACCESS_OSLO_TZ).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        reset_at = tomorrow.astimezone(timezone.utc).isoformat()
        can_answer = remaining > 0
    else:
        used = int((usage or {}).get("total_used", 0))
        limit = ACCESS_GUEST_TOTAL_LIMIT
        remaining = max(0, limit - used)
        reset_at = None
        can_answer = remaining > 0

    return {
        "tier": tier,
        "is_authenticated": is_registered,
        "is_premium": is_premium,
        "can_answer": can_answer,
        "limit": limit,
        "used": used,
        "remaining": remaining,
        "day_key": today if is_registered and not is_premium else None,
        "reset_at": reset_at,
        "features": {
            "unlimited_questions": is_premium,
            "exam_mode": is_premium,
            "ai_explanations": is_premium,
            "weak_topic_training": is_premium,
            "advanced_history": is_premium,
            "full_video_learning": is_premium,
            "daily_free_questions": is_registered and not is_premium,
            "guest_frictionless_start": not is_registered,
        },
        "message": {
            "no": "Fortsett rolig med dagens økt." if can_answer else ("Opprett en gratis konto for 10 spørsmål per dag." if not is_registered else "Dagens gratisøkt er brukt. Fortsett gjerne i morgen, eller gå dypere med Premium."),
            "th": "ฝึกต่ออย่างใจเย็นในวันนี้" if can_answer else ("สร้างบัญชีฟรีเพื่อรับ 10 คำถามต่อวัน" if not is_registered else "ใช้โควต้าฟรีของวันนี้แล้ว กลับมาฝึกต่อพรุ่งนี้ หรือเรียนลึกขึ้นด้วย Premium"),
            "en": "Continue calmly with today's practice." if can_answer else ("Create a free account for 10 questions per day." if not is_registered else "Today's free practice is used. Continue tomorrow, or go deeper with Premium."),
        },
    }

async def _get_access_usage(user: Optional[dict], device_id: str) -> Optional[dict]:
    scope, key = _access_scope(user, device_id)
    return await db.access_usage.find_one({"scope": scope, "key": key}, {"_id": 0})

async def _migrate_guest_learning_to_user(device_id: Optional[str], user_id: str) -> None:
    if not device_id:
        return
    now = datetime.now(timezone.utc).isoformat()
    for collection in (db.quiz_attempts, db.user_progress, db.bookmarks, db.ai_attempts):
        try:
            await collection.update_many(
                {"device_id": device_id, "user_id": {"$exists": False}},
                {"$set": {"user_id": user_id, "migrated_at": now}},
            )
        except Exception:
            pass

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Thai2Drive API - Norway Driving Theory Quiz"}

@api_router.get("/health")
async def health():
    try:
        await db.command("ping")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "degraded", "db": "unreachable", "detail": str(e)}

# App-wide image-only filter: ALL quiz modes (Practice, Exam, Daily Test)
# must ONLY return questions that have an image (bildeUrl present and non-empty).
IMAGE_ONLY_FILTER = {"bildeUrl": {"$exists": True, "$nin": [None, ""]}}

@api_router.get("/questions/debug")
async def debug_questions():
    try:
        count = await db.questions.count_documents({})
        count_with_image = await db.questions.count_documents(IMAGE_ONLY_FILTER)
        sample = await db.questions.find({}, {"_id": 0}).limit(1).to_list(1)
        keys = list(sample[0].keys()) if sample else []
        return {"total": count, "with_image": count_with_image, "sample_keys": keys}
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/questions")
async def get_questions(category: Optional[str] = None, difficulty: Optional[str] = None, limit: int = Query(default=50, le=200)):
    query: dict = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty
    questions = await db.questions.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return [normalize_question(q) for q in questions]

async def _get_exam_questions(
    approved: int,
    x_device_id: str,
    user: Optional[dict],
) -> list:
    """
    Exam/Test mode question selection:
    - 90% hard, 10% medium
    - Prioritise questions the user answered wrong recently (last 10 attempts)
    - All questions must have an image (existing site requirement)
    - Falls back gracefully if there are not enough hard questions
    """
    image_filter = {"bildeUrl": {"$exists": True, "$nin": [None, ""]}}

    # ── Step 1: collect recently-wrong question IDs ───────────────────────
    wrong_ids: list = []
    lookup_key = (user or {}).get("sub") or (user or {}).get("id") or x_device_id
    if lookup_key:
        try:
            wrong_pipeline = [
                {"$match": {"$or": [{"device_id": x_device_id}, {"user_id": lookup_key}]}},
                {"$sort": {"completed_at": -1}},
                {"$limit": 10},
                {"$unwind": "$questions_answered"},
                {"$match": {
                    "questions_answered.user_answer": {"$exists": True},
                    "$expr": {"$ne": [
                        {"$toUpper": "$questions_answered.user_answer"},
                        {"$toUpper": "$questions_answered.correct_answer"},
                    ]},
                }},
                {"$group": {"_id": "$questions_answered.question_id"}},
                {"$limit": int(approved * 0.4)},  # cap at 40 % of slots
            ]
            wrong_docs = await db.quiz_attempts.aggregate(wrong_pipeline).to_list(int(approved * 0.4))
            wrong_ids = [d["_id"] for d in wrong_docs if d.get("_id")]
        except Exception as exc:
            logger.warning("exam: wrong-question lookup failed: %s", exc)

    # ── Step 2: slot sizes ────────────────────────────────────────────────
    wrong_slot  = min(len(wrong_ids), max(0, int(approved * 0.3)))  # up to 30 %
    hard_slot   = max(0, round((approved - wrong_slot) * 0.90))
    medium_slot = max(0, approved - wrong_slot - hard_slot)

    exclude_ids = []  # track fetched IDs to avoid duplicates

    # ── Step 3: wrong questions (any difficulty, prioritised) ─────────────
    wrong_qs: list = []
    if wrong_ids and wrong_slot > 0:
        wrong_qs = await db.questions.aggregate([
            {"$match": {**image_filter, "id": {"$in": wrong_ids}}},
            {"$sample": {"size": wrong_slot}},
            {"$project": {"_id": 0}},
        ]).to_list(wrong_slot)
        exclude_ids = [q.get("id") for q in wrong_qs if q.get("id")]

    # ── Step 4: hard questions ────────────────────────────────────────────
    hard_match: dict = {**image_filter, "difficulty": "hard"}
    if exclude_ids:
        hard_match["id"] = {"$nin": exclude_ids}
    hard_qs = await db.questions.aggregate([
        {"$match": hard_match},
        {"$sample": {"size": hard_slot}},
        {"$project": {"_id": 0}},
    ]).to_list(hard_slot)
    exclude_ids += [q.get("id") for q in hard_qs if q.get("id")]

    # ── Step 5: medium questions ──────────────────────────────────────────
    medium_match: dict = {**image_filter, "difficulty": "medium"}
    if exclude_ids:
        medium_match["id"] = {"$nin": exclude_ids}
    medium_qs = await db.questions.aggregate([
        {"$match": medium_match},
        {"$sample": {"size": medium_slot}},
        {"$project": {"_id": 0}},
    ]).to_list(medium_slot)
    exclude_ids += [q.get("id") for q in medium_qs if q.get("id")]

    # ── Step 6: top up with any difficulty if slots unfilled ──────────────
    total_so_far = len(wrong_qs) + len(hard_qs) + len(medium_qs)
    if total_so_far < approved:
        needed = approved - total_so_far
        topup_match: dict = {**image_filter}
        if exclude_ids:
            topup_match["id"] = {"$nin": exclude_ids}
        topup = await db.questions.aggregate([
            {"$match": topup_match},
            {"$sample": {"size": needed}},
            {"$project": {"_id": 0}},
        ]).to_list(needed)
        medium_qs += topup

    # ── Step 7: combine + shuffle ─────────────────────────────────────────
    import random as _random
    all_qs = wrong_qs + hard_qs + medium_qs
    _random.shuffle(all_qs)
    logger.info(
        "exam_selection total=%d wrong=%d hard=%d medium=%d",
        len(all_qs), len(wrong_qs), len(hard_qs), len(medium_qs),
    )
    return all_qs


@api_router.get("/questions/random")
async def get_random_questions(
    category: Optional[str] = None,
    count: int = Query(default=10, le=200),
    has_image: Optional[bool] = None,
    mode: Optional[str] = Query(default=None),   # "exam" → hard-weighted selection
    x_device_id: str = Header(default="", alias="X-Device-ID"),
    user: Optional[dict] = Depends(optional_auth),
):
    # ── Usage gate ─────────────────────────────────────────────────────────
    track = x_device_id or user is not None
    if track:
        approved = await usage_mod.check_and_consume(db, x_device_id, user, count)
    else:
        approved = count  # legacy: no device_id and no auth → serve freely

    # ── Exam mode: hard-weighted, wrong-question-prioritised ───────────────
    if mode == "exam" and not category:
        questions = await _get_exam_questions(approved, x_device_id, user)
        return [normalize_question(q) for q in questions]

    # ── Normal / category practice: existing random behaviour ─────────────
    pipeline = []
    match_stage: dict = {}
    if category:
        match_stage["category"] = category
    if has_image is True:
        match_stage["bildeUrl"] = {"$exists": True, "$nin": [None, ""]}
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline.append({"$sample": {"size": approved}})
    pipeline.append({"$project": {"_id": 0}})
    questions = await db.questions.aggregate(pipeline).to_list(approved)
    # If category filter with has_image returns nothing, fall back without category
    if not questions and category and has_image:
        pipeline2 = [
            {"$match": {"bildeUrl": {"$exists": True, "$nin": [None, ""]}}},
            {"$sample": {"size": approved}},
            {"$project": {"_id": 0}}
        ]
        questions = await db.questions.aggregate(pipeline2).to_list(approved)
    return [normalize_question(q) for q in questions]

@api_router.get("/questions/{question_id}")
async def get_question(question_id: str):
    question = await db.questions.find_one({"id": question_id}, {"_id": 0})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return normalize_question(question)

@api_router.post("/questions", response_model=Question)
async def create_question(question_data: QuestionCreate):
    question = Question(**question_data.dict())
    doc = question.dict()
    await db.questions.insert_one(doc)
    return question

# ==================== STATISTIKK ====================

def _pricing_payload_from_fallback(source: str = "fallback") -> dict:
    plans = [PUBLIC_PRICING_FALLBACK[k] for k in ("monthly", "three_months", "lifetime")]
    return {"currency": "NOK", "source": source, "plans": plans}


def _format_kr(amount_minor: int, currency: str) -> str:
    if currency.lower() == "nok":
        whole = int(round(amount_minor / 100))
        return f"{whole} kr"
    return f"{amount_minor / 100:.2f} {currency.upper()}"


def _get_live_stripe_secret_key() -> str:
    key = next(
        (
            os.environ.get(name, "").strip()
            for name in ("STRIPE_SECRET_KEY", "STRIPE_API_KEY", "STRIPE_LIVE_SECRET_KEY", "STRIPE_PRIVATE_KEY")
            if os.environ.get(name, "").strip()
        ),
        "",
    )
    # Production billing must never read Stripe test-mode data. If Railway is
    # misconfigured with a test key, fail closed to the public fallback instead
    # of showing test prices or test price IDs.
    return key if key.startswith("sk_live_") else ""


def _stripe_module():
    key = _get_live_stripe_secret_key()
    if not key:
        return None
    import stripe
    stripe.api_key = key
    return stripe


def _stripe_webhook_secret() -> str:
    return next(
        (
            os.environ.get(name, "").strip()
            for name in ("STRIPE_WEBHOOK_SECRET", "STRIPE_ENDPOINT_SECRET", "STRIPE_WEBHOOK_SIGNING_SECRET")
            if os.environ.get(name, "").strip()
        ),
        "",
    )


def _stripe_to_dict(obj: Any) -> dict:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    to_dict_recursive = getattr(obj, "to_dict_recursive", None)
    if callable(to_dict_recursive):
        return to_dict_recursive()
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    try:
        return dict(obj)
    except Exception:
        return {}


def _get_live_stripe_plan_prices_sync() -> Optional[dict]:
    try:
        stripe = _stripe_module()
        if not stripe:
            return None
        prices = stripe.Price.list(active=True, expand=["data.product"], limit=100)
        by_name = {}
        for price in prices.data:
            product = getattr(price, "product", None)
            name = getattr(product, "name", "") if product else ""
            if name:
                by_name[name.strip().lower()] = price

        plans = []
        for plan_id in ("monthly", "three_months", "lifetime"):
            base = dict(PUBLIC_PRICING_FALLBACK[plan_id])
            price = by_name.get(base["stripe_product_name"].lower())
            if price:
                if getattr(price, "livemode", False) is not True:
                    logger.warning("Ignoring non-live Stripe price for %s", base["stripe_product_name"])
                    return None
                amount = int(price.unit_amount or 0)
                currency = (price.currency or "nok").upper()
                expected_minor = int(base["amount"]) * 100
                if currency != "NOK" or amount != expected_minor:
                    logger.error(
                        "Live Stripe price mismatch for %s: expected %s NOK, got %s %s",
                        base["stripe_product_name"],
                        base["amount"],
                        amount / 100,
                        currency,
                    )
                    return None
                base["stripe_price"] = price
                base.update({
                    "amount": int(round(amount / 100)),
                    "amount_minor": amount,
                    "currency": currency,
                    "display": _format_kr(amount, currency),
                    "stripe_price_id": price.id,
                })
            plans.append(base)
        found = sum(1 for p in plans if p.get("stripe_price_id"))
        return {"currency": "NOK", "source": "stripe_live" if found == 3 else "fallback", "plans": plans}
    except Exception as e:
        logger.warning("Stripe pricing lookup failed: %s", e)
        return None


def _fetch_stripe_pricing_sync() -> Optional[dict]:
    data = _get_live_stripe_plan_prices_sync()
    if not data:
        return None
    public_plans = []
    for plan in data.get("plans", []):
        public_plan = dict(plan)
        public_plan.pop("stripe_price", None)
        public_plans.append(public_plan)
    return {**data, "plans": public_plans}


@api_router.get("/pricing")
async def get_public_pricing():
    """Public premium pricing. Secret Stripe keys never leave the backend."""
    now = time.time()
    if _pricing_cache["data"] and now - _pricing_cache["ts"] < 300:
        return _pricing_cache["data"]
    data = await asyncio.to_thread(_fetch_stripe_pricing_sync)
    if not data:
        data = _pricing_payload_from_fallback()
    _pricing_cache.update({"ts": now, "data": data})
    return data


# ==================== STRIPE CHECKOUT ====================

def _public_site_url() -> str:
    raw = (
        os.environ.get("PUBLIC_SITE_URL")
        or os.environ.get("APP_URL")
        or os.environ.get("FRONTEND_URL")
        or "https://www.thai2drive.no"
    ).strip().rstrip("/")
    return raw or "https://www.thai2drive.no"


def _safe_return_url(url: Optional[str], fallback_path: str) -> str:
    from urllib.parse import urlparse

    fallback = _public_site_url() + fallback_path
    if not url:
        return fallback
    parsed = urlparse(url)
    allowed_hosts = {
        "thai2drive.no",
        "www.thai2drive.no",
        "localhost",
        "127.0.0.1",
    }
    if parsed.scheme not in ("https", "http") or parsed.hostname not in allowed_hosts:
        return fallback
    if parsed.scheme != "https" and parsed.hostname not in ("localhost", "127.0.0.1"):
        return fallback
    return url


def _checkout_mode_for_price(plan_id: str, price: Any) -> str:
    recurring = getattr(price, "recurring", None)
    if plan_id == "monthly":
        if not recurring:
            raise HTTPException(status_code=500, detail="Stripe subscription price is not recurring")
        return "subscription"
    if plan_id == "three_months":
        return "subscription" if recurring else "payment"
    if recurring:
        raise HTTPException(status_code=500, detail="Stripe lifetime price must be one-time")
    return "payment"


# ── RevenueCat webhook secret helper ─────────────────────────────────────────

def _rc_webhook_secret() -> str:
    """Reads RC_WEBHOOK_SECRET from env. Set this in Railway."""
    return os.environ.get("RC_WEBHOOK_SECRET", "").strip()


# ── RevenueCat webhook ────────────────────────────────────────────────────────

@app.post("/api/webhooks/revenuecat")
@app.post("/api/rc/webhook")
async def revenuecat_webhook(request: Request):
    """
    Receives RevenueCat server notifications and syncs Premium status to MongoDB.

    Security: RevenueCat sends a shared secret in the Authorization header.
    Set RC_WEBHOOK_SECRET in Railway to the value from:
      RevenueCat → Project settings → Webhooks → Shared secret

    Supported events:
      INITIAL_PURCHASE / RENEWAL / UNCANCELLATION / NON_RENEWING_PURCHASE
        → grant Premium and set premium_expires_at when RevenueCat sends one.
      CANCELLATION / BILLING_ISSUE
        → mark subscription state, but keep access until the entitlement expires.
      EXPIRATION / REFUND
        → revoke Premium.
    """
    import json as _json
    import hmac as _hmac

    rc_secret = _rc_webhook_secret()
    if not rc_secret:
        logger.error("RC_WEBHOOK_SECRET not configured — RevenueCat webhook disabled")
        raise HTTPException(status_code=503, detail="RevenueCat webhook is not configured")

    # ── Signature verification ────────────────────────────────────────────────
    # RevenueCat sends the shared secret as a plain Bearer token in Authorization.
    auth_header = request.headers.get("Authorization", "")
    provided_secret = auth_header.removeprefix("Bearer ").strip()
    if not _hmac.compare_digest(provided_secret, rc_secret):
        logger.warning("rc_webhook: invalid Authorization header — rejected")
        raise HTTPException(status_code=401, detail="Invalid RevenueCat webhook secret")

    payload_bytes = await request.body()
    try:
        event = _json.loads(payload_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_body = event.get("event") or {}
    event_type = event_body.get("type", "")
    event_id = event_body.get("id", "") or str(uuid.uuid4())
    app_user_id = event_body.get("app_user_id", "")
    aliases = event_body.get("aliases", []) or []
    expiry_ts = event_body.get("expiration_at_ms")  # unix ms or None
    product_id = event_body.get("product_id", "mobile")
    entitlement_ids = event_body.get("entitlement_ids") or []
    subscriber_attributes = event_body.get("subscriber_attributes") or {}

    logger.info("rc_webhook received event_type=%s event_id=%s app_user_id=%s",
                event_type, event_id, app_user_id)

    # ── Idempotency guard ─────────────────────────────────────────────────────
    already = await db.rc_events.find_one({"event_id": event_id, "handled": True})
    if already:
        logger.info("rc_webhook: event %s already handled — skipping", event_id)
        return {"received": True, "skipped": True}

    # If RevenueCat includes entitlement IDs, only the Thai2Drive Premium
    # entitlement may affect MongoDB access. Older/test events without this field
    # are allowed through so production does not silently drop valid purchases.
    if entitlement_ids and "pro" not in entitlement_ids:
        now_iso = datetime.now(timezone.utc).isoformat()
        logger.info("rc_webhook: ignored non-premium entitlement event=%s entitlements=%s",
                    event_id, entitlement_ids)
        await db.rc_events.update_one(
            {"event_id": event_id},
            {"$set": {"event_id": event_id, "type": event_type, "handled": False,
                      "ignored": True, "reason": "non_premium_entitlement",
                      "processed_at": now_iso}},
            upsert=True,
        )
        return {"received": True, "handled": False, "reason": "non_premium_entitlement"}

    # ── Resolve user in MongoDB ───────────────────────────────────────────────
    # RevenueCat app_user_id should be the Thai2Drive user_id. Fall back to aliases
    # and subscriber_attributes.$email so existing anonymous RC users can still sync.
    user = None
    if app_user_id:
        user = await db.users.find_one({"id": app_user_id}, {"_id": 0, "id": 1, "email": 1})
    if not user:
        for alias in aliases:
            if "@" in str(alias):
                user = await db.users.find_one(
                    {"email": alias.strip().lower()}, {"_id": 0, "id": 1, "email": 1}
                )
                if user:
                    break
    if not user:
        email_attr = subscriber_attributes.get("$email") or subscriber_attributes.get("email") or {}
        email_value = email_attr.get("value") if isinstance(email_attr, dict) else email_attr
        if email_value and "@" in str(email_value):
            user = await db.users.find_one(
                {"email": str(email_value).strip().lower()}, {"_id": 0, "id": 1, "email": 1}
            )

    now_iso = datetime.now(timezone.utc).isoformat()

    if not user:
        logger.warning("rc_webhook: cannot resolve user for app_user_id=%s aliases=%s event=%s",
                       app_user_id, aliases, event_type)
        await db.rc_events.update_one(
            {"event_id": event_id},
            {"$set": {"event_id": event_id, "type": event_type, "handled": False,
                      "error": "user_not_found", "processed_at": now_iso}},
            upsert=True,
        )
        # Return 200 to stop RC from retrying an event we can never resolve.
        return {"received": True, "handled": False, "reason": "user_not_found"}

    user_id = user["id"]

    # ── Handle event ──────────────────────────────────────────────────────────
    handled = True
    grant_events = {"INITIAL_PURCHASE", "RENEWAL", "UNCANCELLATION", "NON_RENEWING_PURCHASE"}
    pending_events = {"CANCELLATION", "BILLING_ISSUE"}
    revoke_events = {"EXPIRATION", "REFUND"}

    if event_type in grant_events:
        expires_at = None
        if expiry_ts:
            try:
                expires_at = datetime.fromtimestamp(expiry_ts / 1000, tz=timezone.utc)
            except Exception:
                pass

        update: Dict[str, Any] = {
            "is_premium": True,
            "premium_source": "revenuecat",
            "premium_plan": product_id,
            "premium_status": "active",
            "premium_updated_at": now_iso,
        }
        if expires_at:
            update["premium_expires_at"] = expires_at.isoformat()

        mongo_update: Dict[str, Any] = {"$set": update}
        # Lifetime / non-expiring purchase: remove expiry field
        if not expires_at:
            mongo_update["$unset"] = {"premium_expires_at": ""}

        await db.users.update_one({"id": user_id}, mongo_update)
        # Mirror to subscriptions collection (same pattern as Stripe)
        try:
            await db.subscriptions.update_one(
                {"user_id": user_id, "source": "revenuecat"},
                {"$set": {**update, "user_id": user_id, "source": "revenuecat"},
                 "$setOnInsert": {"created_at": now_iso}},
                upsert=True,
            )
        except Exception as exc:
            logger.warning("rc_webhook: subscriptions mirror failed user=%s: %s", user_id, exc)

        logger.info("rc_webhook: granted Premium user=%s event=%s expires=%s",
                    user_id, event_type, expires_at)

    elif event_type in revoke_events:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"is_premium": False, "premium_status": "expired",
                      "premium_updated_at": now_iso}},
        )
        try:
            await db.subscriptions.update_one(
                {"user_id": user_id, "source": "revenuecat"},
                {"$set": {"premium_status": "expired", "expired_at": now_iso}},
            )
        except Exception as exc:
            logger.warning("rc_webhook: subscriptions cancel mirror failed user=%s: %s", user_id, exc)

        logger.info("rc_webhook: revoked Premium user=%s event=%s", user_id, event_type)

    elif event_type in pending_events:
        status = "billing_issue" if event_type == "BILLING_ISSUE" else "canceled"
        update: Dict[str, Any] = {
            "premium_source": "revenuecat",
            "premium_plan": product_id,
            "premium_status": status,
            "premium_updated_at": now_iso,
        }
        if expiry_ts:
            try:
                expires_at = datetime.fromtimestamp(expiry_ts / 1000, tz=timezone.utc)
                update["premium_expires_at"] = expires_at.isoformat()
                update["is_premium"] = expires_at > datetime.now(timezone.utc)
            except Exception:
                pass
        await db.users.update_one({"id": user_id}, {"$set": update})
        try:
            await db.subscriptions.update_one(
                {"user_id": user_id, "source": "revenuecat"},
                {"$set": {**update, "user_id": user_id, "source": "revenuecat"},
                 "$setOnInsert": {"created_at": now_iso}},
                upsert=True,
            )
        except Exception as exc:
            logger.warning("rc_webhook: subscriptions pending mirror failed user=%s: %s", user_id, exc)

        logger.info("rc_webhook: marked Premium pending user=%s event=%s status=%s",
                    user_id, event_type, status)

    else:
        # Informational events (e.g. PRODUCT_CHANGE, TRANSFER) — acknowledge without action
        logger.info("rc_webhook: no action for event_type=%s user=%s", event_type, user_id)
        handled = False

    # ── Log event ─────────────────────────────────────────────────────────────
    await db.rc_events.update_one(
        {"event_id": event_id},
        {"$set": {"event_id": event_id, "type": event_type, "user_id": user_id,
                  "handled": handled, "processed_at": now_iso}},
        upsert=True,
    )

    return {"received": True, "handled": handled}


# ── Premium grant helpers ─────────────────────────────────────────────────────

async def _set_user_premium(
    user_id: str,
    *,
    plan_id: str,
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
    stripe_session_id: Optional[str] = None,
    status: str = "active",
    current_period_end: Optional[int] = None,
    lifetime: bool = False,
    expires_at: Optional[datetime] = None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    update = {
        "is_premium": True,
        "premium_source": "stripe",
        "premium_plan": plan_id,
        "premium_status": status,
        "premium_updated_at": now,
    }
    if stripe_customer_id:
        update["stripe_customer_id"] = stripe_customer_id
    if stripe_subscription_id:
        update["stripe_subscription_id"] = stripe_subscription_id
    if stripe_session_id:
        update["stripe_checkout_session_id"] = stripe_session_id
    if current_period_end:
        update["premium_current_period_end"] = datetime.fromtimestamp(current_period_end, timezone.utc).isoformat()
    if expires_at:
        update["premium_expires_at"] = expires_at.astimezone(timezone.utc).isoformat()
    if lifetime:
        update["premium_lifetime"] = True
        update.pop("premium_expires_at", None)

    mongo_update: Dict[str, Any] = {"$set": update}
    if lifetime:
        mongo_update["$unset"] = {"premium_expires_at": ""}

    await db.users.update_one({"id": user_id}, mongo_update)
    try:
        await db.subscriptions.update_one(
            {"user_id": user_id, "source": "stripe", "stripe_subscription_id": stripe_subscription_id or stripe_session_id or "lifetime"},
            {"$set": {**update, "user_id": user_id, "source": "stripe"}, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
    except Exception as exc:
        logger.warning("Stripe subscription mirror update failed for user %s: %s", user_id, exc)


async def _sync_subscription_deleted(subscription: dict) -> None:
    sub_id = subscription.get("id")
    if not sub_id:
        logger.warning("Stripe subscription.deleted without subscription id")
        return
    user_id = (subscription.get("metadata") or {}).get("user_id")
    if not user_id:
        mirrored = await db.subscriptions.find_one(
            {"source": "stripe", "stripe_subscription_id": str(sub_id)},
            {"_id": 0},
        )
        user_id = mirrored.get("user_id") if mirrored else None
    if not user_id and subscription.get("customer"):
        user = await db.users.find_one({"stripe_customer_id": str(subscription.get("customer"))}, {"_id": 0})
        user_id = user.get("id") if user else None
    if not user_id:
        logger.warning("Stripe subscription.deleted could not resolve user for subscription %s", sub_id)
        return
    now = datetime.now(timezone.utc).isoformat()
    await db.subscriptions.update_one(
        {"user_id": user_id, "source": "stripe", "stripe_subscription_id": sub_id},
        {"$set": {"premium_status": "canceled", "canceled_at": now}},
        upsert=True,
    )
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user and user.get("stripe_subscription_id") and user.get("stripe_subscription_id") != str(sub_id):
        logger.info("Ignoring cancellation for non-current Stripe subscription %s user=%s", sub_id, user_id)
        return
    if user and not user.get("premium_lifetime"):
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"is_premium": False, "premium_status": "canceled", "premium_updated_at": now}},
        )


async def _activate_from_checkout_session(session: dict) -> bool:
    metadata = session.get("metadata") or {}
    user_id = metadata.get("user_id")
    plan_id = metadata.get("plan_id")
    if not user_id or plan_id not in ("monthly", "three_months", "lifetime"):
        return False
    mode = session.get("mode")
    payment_status = session.get("payment_status")
    if mode == "payment" and payment_status != "paid":
        return False
    if mode == "subscription" and payment_status not in ("paid", "no_payment_required"):
        return False

    current_period_end = None
    status = "active"
    subscription_id = session.get("subscription")
    if mode == "subscription":
        # Keep checkout.session.completed webhook handling deterministic. Do not
        # call Stripe again from this path; subscription events can refine status
        # and period data separately.
        status = "active"

    expires_at = None
    if mode == "payment" and plan_id == "three_months":
        expires_at = datetime.now(timezone.utc) + timedelta(days=90)

    await _set_user_premium(
        user_id,
        plan_id=plan_id,
        stripe_customer_id=str(session.get("customer") or ""),
        stripe_subscription_id=str(subscription_id or ""),
        stripe_session_id=str(session.get("id") or ""),
        status=status,
        current_period_end=current_period_end,
        lifetime=(plan_id == "lifetime"),
        expires_at=expires_at,
    )
    return True


@api_router.post("/create-checkout-session")
async def create_checkout_session(data: CheckoutSessionRequest, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({"id": current_user["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stripe = _stripe_module()
    if not stripe:
        raise HTTPException(status_code=503, detail="Live Stripe is not configured")

    pricing = await asyncio.to_thread(_get_live_stripe_plan_prices_sync)
    if not pricing or pricing.get("source") != "stripe_live":
        raise HTTPException(status_code=503, detail="Live Stripe prices are not available")
    plan = next((p for p in pricing["plans"] if p.get("id") == data.plan_id), None)
    if not plan or not plan.get("stripe_price"):
        raise HTTPException(status_code=400, detail="Plan is not available")
    price = plan["stripe_price"]
    if getattr(price, "livemode", False) is not True:
        raise HTTPException(status_code=400, detail="Only live Stripe prices are allowed")

    mode = _checkout_mode_for_price(data.plan_id, price)
    success_url = _safe_return_url(
        data.success_url,
        "/api/web?checkout=success&session_id={CHECKOUT_SESSION_ID}",
    )
    cancel_url = _safe_return_url(data.cancel_url, "/api/web?checkout=cancel")
    metadata = {
        "user_id": user["id"],
        "email": user.get("email", ""),
        "plan_id": data.plan_id,
        "device_id": data.device_id or user.get("device_id") or "",
    }

    session_kwargs = {
        "mode": mode,
        "line_items": [{"price": price.id, "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": user["id"],
        "metadata": metadata,
        "allow_promotion_codes": False,
    }
    if user.get("stripe_customer_id"):
        session_kwargs["customer"] = user.get("stripe_customer_id")
    else:
        session_kwargs["customer_email"] = user.get("email")
    if mode == "subscription":
        session_kwargs["subscription_data"] = {"metadata": metadata}
    else:
        session_kwargs["payment_intent_data"] = {"metadata": metadata}

    session = stripe.checkout.Session.create(**session_kwargs)
    if getattr(session, "livemode", False) is not True:
        raise HTTPException(status_code=500, detail="Stripe returned a non-live checkout session")

    now = datetime.now(timezone.utc).isoformat()
    await db.checkout_sessions.update_one(
        {"stripe_session_id": session.id},
        {"$set": {
            "stripe_session_id": session.id,
            "user_id": user["id"],
            "plan_id": data.plan_id,
            "mode": mode,
            "livemode": True,
            "status": getattr(session, "status", None),
            "created_at": now,
        }},
        upsert=True,
    )
    return {"url": session.url, "session_id": session.id, "livemode": True}


@api_router.get("/checkout/status")
async def checkout_status(session_id: str, current_user: dict = Depends(get_current_user)):
    stripe = _stripe_module()
    if not stripe:
        raise HTTPException(status_code=503, detail="Live Stripe is not configured")
    session = stripe.checkout.Session.retrieve(session_id)
    if getattr(session, "livemode", False) is not True:
        raise HTTPException(status_code=400, detail="Only live Stripe sessions are allowed")
    metadata = getattr(session, "metadata", {}) or {}
    if metadata.get("user_id") != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Checkout session does not belong to this user")
    activated = await _activate_from_checkout_session(dict(session))
    user = await db.users.find_one({"id": current_user["sub"]}, {"_id": 0, "password_hash": 0})
    return {
        "is_premium": bool(user and user.get("is_premium")),
        "activated": activated,
        "payment_status": getattr(session, "payment_status", None),
        "status": getattr(session, "status", None),
    }


@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    stripe = _stripe_module()
    webhook_secret = _stripe_webhook_secret()
    if not stripe or not webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")

    # Signature verified. Parse the raw payload as plain JSON — this is version-safe
    # and avoids all stripe-python SDK object compatibility issues across v3/v4/v5/v15+.
    import json as _json
    event = _json.loads(payload)
    event_id = event.get("id") or ""
    event_type = event.get("type") or "unknown"
    is_live = event.get("livemode") is True
    if not is_live:
        logger.warning("Processing test-mode Stripe event %s type=%s", event_id, event_type)

    # Idempotency guard: skip events already successfully handled to protect against
    # Stripe retries and duplicate deliveries without re-running side effects.
    if event_id:
        already = await db.stripe_events.find_one({"event_id": event_id, "handled": True})
        if already:
            logger.info("Stripe event %s already handled, skipping", event_id)
            return {"received": True, "handled": True, "skipped": True}

    try:
        if event_id:
            existing_event = await db.stripe_events.find_one({"event_id": event_id}, {"_id": 0})
            if existing_event and existing_event.get("handled") is True:
                logger.info("Stripe event %s already handled; acknowledging duplicate", event_id)
                return {"received": True, "handled": True, "duplicate": True}

        data_obj = (event.get("data") or {}).get("object") or {}
        handled = True

        if event_type == "checkout.session.completed":
            await _activate_from_checkout_session(data_obj)
        elif event_type == "customer.subscription.created":
            if data_obj.get("status") in ("active", "trialing"):
                metadata = data_obj.get("metadata") or {}
                user_id = metadata.get("user_id")
                plan_id = metadata.get("plan_id", "monthly")
                if user_id:
                    await _set_user_premium(
                        user_id,
                        plan_id=plan_id,
                        stripe_customer_id=str(data_obj.get("customer") or ""),
                        stripe_subscription_id=str(data_obj.get("id") or ""),
                        status=data_obj.get("status") or "active",
                        current_period_end=data_obj.get("current_period_end"),
                    )
        elif event_type == "customer.subscription.deleted":
            await _sync_subscription_deleted(data_obj)
        elif event_type == "invoice_payment.paid":
            # Newer Stripe API event for invoice-payment objects. Premium activation is
            # handled by checkout.session.completed / subscription events; acknowledge this
            # event so Stripe does not keep retrying an object shape we do not need.
            logger.info("Stripe invoice_payment.paid event %s acknowledged without grant", event_id)
            handled = False
        elif event_type in ("invoice.paid", "invoice.payment_paid"):
            subscription_details = data_obj.get("subscription_details") or {}
            metadata = data_obj.get("metadata") or subscription_details.get("metadata") or {}
            user_id = metadata.get("user_id")
            plan_id = metadata.get("plan_id", "monthly")
            # Renewal fallback: Stripe does not re-populate user metadata on recurring invoices.
            # Look up the user by stripe_customer_id stored at checkout time.
            if not user_id:
                customer_id = str(data_obj.get("customer") or "")
                if customer_id:
                    matched = await db.users.find_one({"stripe_customer_id": customer_id}, {"_id": 0, "id": 1})
                    if matched:
                        user_id = matched["id"]
                        logger.info("Stripe invoice %s: resolved user %s via customer_id %s", event_id, user_id, customer_id)
            if user_id:
                await _set_user_premium(
                    user_id,
                    plan_id=plan_id,
                    stripe_customer_id=str(data_obj.get("customer") or ""),
                    stripe_subscription_id=str(data_obj.get("subscription") or data_obj.get("subscription_id") or ""),
                    status="active",
                    current_period_end=data_obj.get("period_end"),
                )
            else:
                logger.info("Stripe invoice event %s: no user found via metadata or customer_id", event_id)
                handled = False

        await db.stripe_events.update_one(
            {"event_id": event_id},
            {"$set": {"event_id": event_id, "type": event_type, "livemode": is_live, "handled": handled, "processed_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Stripe webhook handling failed for %s: %s", event_type, exc)
        try:
            await db.stripe_events.update_one(
                {"event_id": event_id},
                {"$set": {"event_id": event_id, "type": event_type, "livemode": is_live, "handled": False, "processing_error": str(exc), "processed_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True,
            )
        except Exception as log_exc:
            logger.warning("Stripe webhook error logging failed for %s: %s", event_id, log_exc)
        return {"received": True, "handled": False}

    return {"received": True, "handled": handled}

@api_router.get("/stats/me")
async def get_my_stats(device_id: str):
    """Per-category accuracy for a device, based on quiz_attempts."""
    # Aggregate by category across all attempts
    pipeline = [
        {"$match": {
            "$or": [{"device_id": device_id}, {"user_id": device_id}],
            "total_questions": {"$gt": 0},
            "category": {"$nin": [None, "", "None"]}
        }},
        {"$group": {
            "_id": "$category",
            "attempts":      {"$sum": 1},
            "total_q":       {"$sum": "$total_questions"},
            "total_correct": {"$sum": "$correct_answers"},
        }},
        {"$project": {
            "_id": 0,
            "category":      "$_id",
            "attempts":      1,
            "total_q":       1,
            "total_correct": 1,
            "pct": {"$cond": [
                {"$gt": ["$total_q", 0]},
                {"$multiply": [{"$divide": ["$total_correct", "$total_q"]}, 100]},
                0
            ]},
        }},
        {"$sort": {"pct": 1}},
    ]
    rows = await db.quiz_attempts.aggregate(pipeline).to_list(100)

    # Overall totals
    totals = await db.quiz_attempts.aggregate([
        {"$match": {"$or": [{"device_id": device_id}, {"user_id": device_id}]}},
        {"$group": {
            "_id": None,
            "total_q":       {"$sum": "$total_questions"},
            "total_correct": {"$sum": "$correct_answers"},
            "attempts":      {"$sum": 1},
        }},
    ]).to_list(1)
    overall = totals[0] if totals else {"total_q": 0, "total_correct": 0, "attempts": 0}
    overall.pop("_id", None)
    overall["pct"] = round(overall["total_correct"] / overall["total_q"] * 100, 1) if overall["total_q"] else 0

    return {"overall": overall, "by_category": rows}


# ==================== TRAFIKKSKILT ====================

@api_router.get("/signs")
async def get_signs():
    from signs_data import get_signs_grouped
    return get_signs_grouped()


# ==================== BOK / CHAPTERS ====================

@api_router.get("/chapters")
async def get_chapters():
    """Hent alle kapitler (unik liste med titler)"""
    pipeline = [
        {"$group": {
            "_id": "$chapter_num",
            "chapter_title": {"$first": "$chapter_title"},
            "section_count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    chapters = await db.chapters.aggregate(pipeline).to_list(20)
    return [
        {
            "chapter_num": c["_id"],
            "title": c["chapter_title"],
            "section_count": c["section_count"]
        }
        for c in chapters
    ]

@api_router.get("/chapters/{chapter_num}")
async def get_chapter_sections(chapter_num: int):
    """Hent alle seksjoner i et kapittel"""
    sections = await db.chapters.find(
        {"chapter_num": chapter_num},
        {"_id": 0}
    ).sort("section_num", 1).to_list(200)
    return sections

@api_router.get("/chapters/{chapter_num}/{section_num}")
async def get_section(chapter_num: int, section_num: int):
    """Hent én seksjon"""
    section = await db.chapters.find_one(
        {"chapter_num": chapter_num, "section_num": section_num},
        {"_id": 0}
    )
    if not section:
        raise HTTPException(status_code=404, detail="Seksjon ikke funnet")
    return section

# ==================== END BOK ====================

@api_router.get("/categories")
async def get_categories():
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    cats = await db.questions.aggregate(pipeline).to_list(100)
    return [{"name": c["_id"], "count": c["count"]} for c in cats]

# ==================== ACCESS POLICY ====================

@api_router.get("/access/status")
async def access_status(device_id: str, user: Optional[dict] = Depends(get_optional_user)):
    """Single access-policy contract for web and mobile.

    Backend is the source of truth:
    - guest: 5 total answered questions
    - registered: 10 answered questions per Oslo calendar day
    - premium/admin: unlimited
    """
    usage = await _get_access_usage(user, device_id)
    return _access_policy_payload(user, usage)

@api_router.post("/access/consume")
async def access_consume(data: AccessConsumeRequest, user: Optional[dict] = Depends(get_optional_user)):
    """Consume one question answer if the learner has access.

    This endpoint is intentionally gentle but authoritative. The frontend may
    display counters, but this endpoint owns the quota.
    """
    scope, key = _access_scope(user, data.device_id)
    event_id = data.event_id or str(uuid.uuid4())
    existing_event = await db.access_events.find_one({"event_id": event_id}, {"_id": 0})
    if existing_event:
        usage = await _get_access_usage(user, data.device_id)
        return {**_access_policy_payload(user, usage), "consumed": False, "event_id": event_id}

    usage = await db.access_usage.find_one({"scope": scope, "key": key}, {"_id": 0})
    before = _access_policy_payload(user, usage)
    if not before["can_answer"]:
        raise HTTPException(status_code=402, detail=before)

    is_premium = before["tier"] == "premium"
    now = datetime.now(timezone.utc).isoformat()

    await db.access_events.insert_one({
        "event_id": event_id,
        "scope": scope,
        "key": key,
        "device_id": data.device_id,
        "user_id": user["id"] if user else None,
        "question_id": data.question_id,
        "mode": data.mode,
        "category": data.category,
        "created_at": now,
    })

    if not is_premium:
        update: Dict[str, Any]
        if scope == "user":
            day_key = _oslo_day_key()
            if not usage or usage.get("day_key") != day_key:
                update = {
                    "$set": {
                        "scope": scope,
                        "key": key,
                        "user_id": user["id"] if user else None,
                        "device_id": data.device_id,
                        "day_key": day_key,
                        "daily_used": 1,
                        "updated_at": now,
                    },
                    "$setOnInsert": {"created_at": now},
                }
            else:
                update = {
                    "$set": {"updated_at": now, "device_id": data.device_id},
                    "$inc": {"daily_used": 1},
                    "$setOnInsert": {"created_at": now, "scope": scope, "key": key},
                }
        else:
            update = {
                "$set": {"scope": scope, "key": key, "device_id": data.device_id, "updated_at": now},
                "$inc": {"total_used": 1},
                "$setOnInsert": {"created_at": now},
            }
        await db.access_usage.update_one({"scope": scope, "key": key}, update, upsert=True)

    usage = await _get_access_usage(user, data.device_id)
    return {**_access_policy_payload(user, usage), "consumed": not is_premium, "event_id": event_id}

@api_router.get("/progress/{device_id}")
async def get_user_progress(device_id: str):
    progress = await db.user_progress.find_one({"device_id": device_id}, {"_id": 0})
    if not progress:
        new_progress = UserProgress(device_id=device_id).dict()
        await db.user_progress.insert_one(new_progress)
        new_progress.pop("_id", None)
        return new_progress
    return progress

@api_router.put("/progress/{device_id}")
async def update_user_progress(device_id: str, answered_correct: bool, category: str):
    progress = await db.user_progress.find_one({"device_id": device_id})
    if not progress:
        progress = UserProgress(device_id=device_id).dict()

    progress["total_questions_answered"] = progress.get("total_questions_answered", 0) + 1
    if answered_correct:
        progress["correct_answers"] = progress.get("correct_answers", 0) + 1

    if "questions_by_category" not in progress:
        progress["questions_by_category"] = {}
    if category not in progress["questions_by_category"]:
        progress["questions_by_category"][category] = {"answered": 0, "correct": 0}
    progress["questions_by_category"][category]["answered"] += 1
    if answered_correct:
        progress["questions_by_category"][category]["correct"] += 1

    progress["last_activity"] = datetime.now(timezone.utc).isoformat()

    await db.user_progress.update_one(
        {"device_id": device_id},
        {"$set": progress},
        upsert=True
    )
    progress.pop("_id", None)
    return {"success": True, "progress": progress}

@api_router.post("/quiz-attempts")
async def save_quiz_attempt(attempt_data: QuizAttemptCreate):
    # Build doc from client data — preserve client_attempt_id and client completed_at
    doc = attempt_data.dict(exclude_none=True)
    doc["id"] = doc.pop("client_attempt_id", None) or str(uuid.uuid4())
    if "completed_at" not in doc:
        doc["completed_at"] = datetime.now(timezone.utc).isoformat()
    await db.quiz_attempts.insert_one(doc)
    doc.pop("_id", None)

    # ── Segment track ──
    if SEGMENT_WRITE_KEY:
        user_id = doc.get("user_id") or doc.get("device_id") or "anonymous"
        segment_analytics.track(user_id, "Quiz Attempt Completed", {
            "score": doc.get("score", 0),
            "total": doc.get("total", 0),
            "category": doc.get("category", "unknown"),
            "mode": doc.get("mode", "practice"),
            "attempt_id": doc["id"],
        })

    return doc

@api_router.get("/quiz-attempts/{device_id}")
async def get_quiz_attempts(device_id: str, limit: int = Query(default=20, le=50)):
    attempts = await db.quiz_attempts.find(
        {"$or": [{"device_id": device_id}, {"user_id": device_id}]}, {"_id": 0}
    ).sort("completed_at", -1).limit(limit).to_list(limit)
    return attempts

@api_router.get("/history")
async def get_user_history(
    limit: int = Query(default=20, le=50),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["sub"]
    user_doc = await db.users.find_one({"id": user_id})
    device_id = user_doc.get("device_id") if user_doc else None
    
    query = {"$or": [{"user_id": user_id}]}
    if device_id:
        query["$or"].append({"device_id": device_id})
        
    attempts = await db.quiz_attempts.find(
        query, {"_id": 0}
    ).sort("completed_at", -1).limit(limit).to_list(limit)
    return attempts

@api_router.post("/bookmarks")
async def add_bookmark(bookmark_data: BookmarkCreate):
    existing = await db.bookmarks.find_one({
        "device_id": bookmark_data.device_id,
        "question_id": bookmark_data.question_id
    }, {"_id": 0})
    if existing:
        return existing
    bookmark = Bookmark(**bookmark_data.dict())
    doc = bookmark.dict()
    await db.bookmarks.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.delete("/bookmarks/{device_id}/{question_id}")
async def remove_bookmark(device_id: str, question_id: str):
    result = await db.bookmarks.delete_one({"device_id": device_id, "question_id": question_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"success": True}

@api_router.get("/bookmarks/{device_id}")
async def get_bookmarks(device_id: str):
    bookmarks = await db.bookmarks.find({"device_id": device_id}, {"_id": 0}).to_list(500)
    return bookmarks

@api_router.get("/bookmarked-questions/{device_id}")
async def get_bookmarked_questions(device_id: str):
    bookmarks = await db.bookmarks.find({"device_id": device_id}, {"_id": 0}).to_list(500)
    question_ids = [b["question_id"] for b in bookmarks]
    questions = await db.questions.find({"id": {"$in": question_ids}}, {"_id": 0}).to_list(500)
    return questions

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/signup")
async def signup(data: AuthSignup):
    existing = await _find_user_by_email(data.email)
    if existing:
        raise _auth_error_key(
            "email_already_registered",
            "Denne e-posten er allerede registrert. Logg inn eller tilbakestill passordet.",
            "อีเมลนี้ลงทะเบียนแล้ว กรุณาเข้าสู่ระบบหรือรีเซ็ตรหัสผ่าน",
            "This email is already registered. Log in or reset password.",
            status_code=409,
        )

    password_hash = pwd_context.hash(data.password)
    user_id = str(uuid.uuid4())

    # Check admin whitelist
    admin_entry = await db.admin_users.find_one({"email": data.email})
    is_admin = admin_entry is not None
    is_premium = is_admin  # Admins get auto premium

    # Gratisuken: verdi før betaling. Gis kun til nye registreringer, og kun én gang
    # per e-post/device_id — ellers kan man lage uendelig mange gratiskontoer og
    # tømme AI-læreren for penger.
    trial_expires_at = await _grant_trial_if_eligible(data.email, data.device_id, user_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    user_doc = {
        "id": user_id,
        "email": data.email,
        "name": (data.name or "").strip() or None,
        "password_hash": password_hash,
        "is_admin": is_admin,
        "is_premium": is_premium,
        "device_id": data.device_id or None,
        "trial_started_at": now_iso if trial_expires_at else None,
        "trial_expires_at": trial_expires_at,
        "trial_used": True,
        "created_at": now_iso,
    }
    await db.users.insert_one(user_doc)
    await _migrate_guest_learning_to_user(data.device_id, user_id)

    # Mark guest_usage record as linked so it's not double-counted
    if data.device_id:
        await db.guest_usage.update_one(
            {"device_id": data.device_id},
            {"$set": {"linked_user_id": user_id}},
        )

    # ── Segment track ──
    if SEGMENT_WRITE_KEY:
        segment_analytics.identify(user_id, {"email": data.email, "name": data.name, "is_premium": is_premium, "is_admin": is_admin})
        segment_analytics.track(user_id, "User Signed Up", {"email": data.email, "method": "email", "is_premium": is_premium})

    has_access = _user_has_active_premium(user_doc)
    token = create_token(
        user_id,
        data.email,
        is_premium=has_access,
        premium_until=_access_expires_at(user_doc),
        premium_status=_user_premium_status(user_doc),
    )
    return {
        "token": token,
        "user": _auth_user_payload(user_doc),
    }

@api_router.post("/auth/login")
async def login(data: AuthLogin):
    _invalid = _auth_error_key(
        "invalid_credentials",
        "Ugyldig e-post eller passord",
        "อีเมลหรือรหัสผ่านไม่ถูกต้อง",
        "Invalid email or password",
        status_code=401,
    )
    user = await _find_user_by_email(data.email)
    if not user or user.get("deleted_at") or user.get("disabled"):
        raise _invalid

    password_hash = user.get("password_hash")
    if not password_hash or not pwd_context.verify(data.password, password_hash):
        raise _invalid

    # Re-check admin status on each login
    admin_entry = await db.admin_users.find_one({"email": data.email})
    is_admin = admin_entry is not None
    if is_admin and not user.get("is_premium"):
        await db.users.update_one({"email": data.email}, {"$set": {"is_admin": True, "is_premium": True}})
        user["is_admin"] = True
        user["is_premium"] = True
    await _migrate_guest_learning_to_user(data.device_id, user["id"])

    is_premium_active = _user_has_active_premium(user)
    token = create_token(
        user["id"],
        user["email"],
        is_premium=is_premium_active,
        premium_until=_access_expires_at(user),
        premium_status=_user_premium_status(user),
    )

    # ── Segment track ──
    if SEGMENT_WRITE_KEY:
        segment_analytics.identify(user["id"], {"email": user["email"], "name": user.get("name"), "is_premium": is_premium_active})
        segment_analytics.track(user["id"], "User Logged In", {"email": user["email"]})

    return {
        "token": token,
        "user": _auth_user_payload(user),
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({"id": current_user["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _auth_user_payload(user)

@api_router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    email_id = _email_hash(data.email)
    masked = _masked_email(data.email)
    logger.info("auth.forgot_password.requested email_hash=%s masked=%s", email_id, masked)
    user = await _find_user_by_email(data.email)
    if not user:
        logger.info("auth.forgot_password.user_not_found email_hash=%s", email_id)
        raise _auth_error_key(
            "email_not_registered",
            "Fant ingen konto med denne e-posten.",
            "ไม่พบบัญชีที่ใช้อีเมลนี้",
            "No account was found with this email.",
            status_code=404,
        )
    if user.get("deleted_at") or user.get("disabled"):
        logger.warning("auth.forgot_password.blocked_account email_hash=%s", email_id)
        raise _auth_error_key(
            "account_unavailable",
            "Denne kontoen er ikke tilgjengelig. Kontakt support.",
            "บัญชีนี้ไม่พร้อมใช้งาน กรุณาติดต่อฝ่ายสนับสนุน",
            "This account is not available. Contact support.",
            status_code=403,
        )

    code = generate_reset_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    logger.info("auth.forgot_password.code_generated email_hash=%s", email_id)

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "reset_code": code,
            "reset_expires": expires.isoformat(),
            "reset_requested_at": datetime.now(timezone.utc).isoformat(),
            "reset_email_hash": email_id,
        }},
    )

    sent, info = await _send_password_reset_email(data.email, code)
    if not sent:
        logger.error("auth.forgot_password.email_failed email_hash=%s reason=%s", email_id, info)
        await db.users.update_one(
            {"id": user["id"]},
            {"$unset": {"reset_code": "", "reset_expires": "", "reset_requested_at": "", "reset_email_hash": ""}},
        )
        raise _auth_error_key(
            "reset_email_failed",
            "Kunne ikke sende tilbakestillingskode. Prøv igjen senere eller kontakt support.",
            "ไม่สามารถส่งรหัสรีเซ็ตรหัสผ่านได้ กรุณาลองใหม่ภายหลังหรือติดต่อฝ่ายสนับสนุน",
            "Could not send reset code. Try again later or contact support.",
            status_code=503,
        )

    logger.info("auth.forgot_password.email_sent email_hash=%s", email_id)
    return {"message": "Password reset code sent"}

@api_router.post("/auth/reset-password")
async def reset_password(data: ResetPasswordRequest):
    email_id = _email_hash(data.email)
    user = await _find_user_by_email(data.email)
    if not user or user.get("deleted_at") or user.get("disabled"):
        logger.warning("auth.reset_password.validation_failed email_hash=%s reason=user_unavailable", email_id)
        raise _auth_error_key(
            "invalid_or_expired_reset_code",
            "Ugyldig eller utløpt tilbakestillingskode",
            "รหัสรีเซ็ตรหัสผ่านไม่ถูกต้องหรือหมดอายุแล้ว",
            "Invalid or expired reset code",
            status_code=400,
        )

    reset_code = str(user.get("reset_code") or "")
    reset_expires = user.get("reset_expires")
    if not reset_code or reset_code != str(data.code).strip() or not reset_expires:
        logger.warning("auth.reset_password.validation_failed email_hash=%s reason=code_mismatch_or_missing", email_id)
        raise _auth_error_key(
            "invalid_or_expired_reset_code",
            "Ugyldig eller utløpt tilbakestillingskode",
            "รหัสรีเซ็ตรหัสผ่านไม่ถูกต้องหรือหมดอายุแล้ว",
            "Invalid or expired reset code",
            status_code=400,
        )

    try:
        expires_at = datetime.fromisoformat(str(reset_expires).replace("Z", "+00:00"))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    except Exception:
        logger.warning("auth.reset_password.validation_failed email_hash=%s reason=bad_expiry", email_id)
        expires_at = datetime.min.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        logger.warning("auth.reset_password.validation_failed email_hash=%s reason=expired", email_id)
        raise _auth_error_key(
            "invalid_or_expired_reset_code",
            "Ugyldig eller utløpt tilbakestillingskode",
            "รหัสรีเซ็ตรหัสผ่านไม่ถูกต้องหรือหมดอายุแล้ว",
            "Invalid or expired reset code",
            status_code=400,
        )

    password_hash = pwd_context.hash(data.new_password)
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_hash": password_hash,
                "reset_used_at": datetime.now(timezone.utc).isoformat(),
            },
            "$unset": {
                "reset_code": "",
                "reset_expires": "",
                "reset_requested_at": "",
                "reset_email_hash": "",
            },
        },
    )

    logger.info("auth.reset_password.success email_hash=%s", email_id)
    return {"message": "Password reset successfully"}

# ==================== USAGE / TIER ROUTES ====================

@api_router.get("/usage/status")
async def get_usage_status(
    x_device_id: str = Header(default="", alias="X-Device-ID"),
    user: Optional[dict] = Depends(optional_auth),
):
    """
    Return the caller's current usage tier, remaining questions, streak, etc.
    Used by the mobile app and web app to render usage indicators.
    """
    return await usage_mod.build_usage_status(db, x_device_id, user)


@api_router.post("/auth/link-device")
async def link_device(
    x_device_id: str = Header(default="", alias="X-Device-ID"),
    current_user: dict = Depends(get_current_user),
):
    """
    Associate the caller's guest device_id with their registered account.
    Call this right after login/signup when the client has an existing device_id.
    The guest usage record is marked as linked so it is not double-counted.
    """
    if not x_device_id:
        return {"ok": True, "linked": False, "reason": "no device_id provided"}

    user_id = current_user["sub"]

    # Store the device_id on the user document (idempotent)
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"device_id": x_device_id}},
    )

    # Mark the guest_usage record as linked
    result = await db.guest_usage.update_one(
        {"device_id": x_device_id},
        {"$set": {"linked_user_id": user_id}},
    )

    return {"ok": True, "linked": result.modified_count > 0}


# ==================== ADMIN ROUTES ====================

@api_router.get("/admin-setup-t2d")
async def admin_setup():
    """One-time setup: create/reset admin@thai2drive.com with password admin123."""
    email = "admin@thai2drive.com"
    password = "admin123"
    password_hash = pwd_context.hash(password)
    import uuid as _uuid
    from datetime import datetime, timezone as _tz
    # Ensure admin_users entry
    if not await db.admin_users.find_one({"email": email}):
        await db.admin_users.insert_one({"email": email})
    # Upsert user with correct hash
    existing = await db.users.find_one({"email": email})
    if existing:
        await db.users.update_one({"email": email}, {"$set": {
            "password_hash": password_hash,
            "is_admin": True,
            "is_premium": True,
        }})
    else:
        await db.users.insert_one({
            "id": str(_uuid.uuid4()),
            "email": email,
            "password_hash": password_hash,
            "is_admin": True,
            "is_premium": True,
            "created_at": datetime.now(_tz.utc).isoformat(),
        })
    return {"ok": True, "message": "Admin user ready. Login: admin@thai2drive.com / admin123"}


@api_router.post("/admin/check")
async def check_admin(data: AdminCheckRequest):
    admin = await db.admin_users.find_one({"email": data.email.strip().lower()})
    return {"is_admin": admin is not None}

@api_router.post("/admin/add")
async def add_admin(
    data: AdminCheckRequest,
    x_admin_secret: str = Header(default=''),
):
    """Bootstrap endpoint for adding the first admin.
    Requires X-Admin-Secret header matching ADMIN_BOOTSTRAP_SECRET env var.
    If env var is not set the endpoint always returns 403.
    """
    if not ADMIN_BOOTSTRAP_SECRET or x_admin_secret != ADMIN_BOOTSTRAP_SECRET:
        raise HTTPException(status_code=403, detail="Admin bootstrap secret required")
    email = data.email.strip().lower()
    existing = await db.admin_users.find_one({"email": email})
    if existing:
        return {"message": "Already admin", "email": email}
    admin = AdminUser(email=email)
    await db.admin_users.insert_one(admin.dict())
    # Also update user if exists
    await db.users.update_one({"email": email}, {"$set": {"is_admin": True, "is_premium": True}})
    return {"message": "Admin added", "email": email}

@api_router.post("/seed")
async def seed_database():
    count = await db.questions.count_documents({})
    if count > 0:
        return {"message": f"Database already has {count} questions", "seeded": False}

    sample_questions = [
        # ===== TRAFFIC SIGNS (9 questions) =====
        {
            "question_text_no": "Hva betyr et rødt åttekantet skilt?",
            "question_text_th": "ป้ายแปดเหลี่ยมสีแดงหมายความว่าอะไร?",
            "question_text_en": "What does a red octagonal sign mean?",
            "answer_a_no": "Stopp og gi vikeplikt",
            "answer_b_no": "Fartsgrense 50 km/t",
            "answer_c_no": "Innkjøring forbudt",
            "answer_d_no": "Parkering forbudt",
            "answer_a_th": "หยุดและให้ทาง",
            "answer_b_th": "จำกัดความเร็ว 50 กม./ชม.",
            "answer_c_th": "ห้ามเข้า",
            "answer_d_th": "ห้ามจอด",
            "answer_a_en": "Stop and give way",
            "answer_b_en": "Speed limit 50 km/h",
            "answer_c_en": "No entry",
            "answer_d_en": "No parking",
            "correct_answer": "A",
            "explanation_no": "Det røde åttekantede skiltet betyr stopp. Du må stoppe helt og gi vikeplikt for annen trafikk.",
            "explanation_th": "ป้ายแปดเหลี่ยมสีแดงหมายถึงหยุด คุณต้องหยุดสนิทและให้ทางแก่ยานพาหนะอื่น",
            "explanation_en": "The red octagonal sign means stop. You must come to a complete stop and give way to other traffic.",
            "category": "Traffic Signs",
            "difficulty": "easy",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Norwegian-road-sign-204.0.svg/240px-Norwegian-road-sign-204.0.svg.png"
        },
        {
            "question_text_no": "Hva indikerer et blått skilt med hvit P?",
            "question_text_th": "ป้ายสีน้ำเงินที่มีตัว P สีขาวหมายถึงอะไร?",
            "question_text_en": "What does a blue sign with white P indicate?",
            "answer_a_no": "Politistasjon",
            "answer_b_no": "Parkering tillatt",
            "answer_c_no": "Privat område",
            "answer_d_no": "Bensinstasjon",
            "answer_a_th": "สถานีตำรวจ",
            "answer_b_th": "อนุญาตให้จอดรถ",
            "answer_c_th": "พื้นที่ส่วนบุคคล",
            "answer_d_th": "ปั๊มน้ำมัน",
            "answer_a_en": "Police station",
            "answer_b_en": "Parking allowed",
            "answer_c_en": "Private area",
            "answer_d_en": "Gas station",
            "correct_answer": "B",
            "explanation_no": "Det blå skiltet med hvit P betyr at parkering er tillatt på dette området.",
            "explanation_th": "ป้ายสีน้ำเงินที่มีตัว P สีขาวหมายความว่าอนุญาตให้จอดรถในบริเวณนี้",
            "explanation_en": "The blue sign with white P means parking is allowed in this area.",
            "category": "Traffic Signs",
            "difficulty": "easy",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/NO_road_sign_552.svg/250px-NO_road_sign_552.svg.png"
        },
        {
            "question_text_no": "Hva betyr et trekantet skilt med rød kant?",
            "question_text_th": "ป้ายสามเหลี่ยมขอบแดงหมายความว่าอะไร?",
            "question_text_en": "What does a triangular sign with red border mean?",
            "answer_a_no": "Forbudsskilt",
            "answer_b_no": "Påbudsskilt",
            "answer_c_no": "Varselskilt",
            "answer_d_no": "Opplysningsskilt",
            "answer_a_th": "ป้ายห้าม",
            "answer_b_th": "ป้ายบังคับ",
            "answer_c_th": "ป้ายเตือน",
            "answer_d_th": "ป้ายให้ข้อมูล",
            "answer_a_en": "Prohibition sign",
            "answer_b_en": "Mandatory sign",
            "answer_c_en": "Warning sign",
            "answer_d_en": "Information sign",
            "correct_answer": "C",
            "explanation_no": "Trekantede skilt med rød kant er varselskilt som advarer om fare forut.",
            "explanation_th": "ป้ายสามเหลี่ยมขอบแดงเป็นป้ายเตือนที่เตือนถึงอันตรายข้างหน้า",
            "explanation_en": "Triangular signs with red border are warning signs that alert about danger ahead.",
            "category": "Traffic Signs",
            "difficulty": "easy",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/NO_road_sign_152.svg/250px-NO_road_sign_152.svg.png"
        },
        {
            "question_text_no": "Hva betyr et rundt skilt med rød kant og hvit bakgrunn med et tall?",
            "question_text_th": "ป้ายวงกลมขอบแดงพื้นขาวที่มีตัวเลขหมายความว่าอะไร?",
            "question_text_en": "What does a round sign with red border and white background with a number mean?",
            "answer_a_no": "Anbefalt hastighet",
            "answer_b_no": "Avstand til neste by",
            "answer_c_no": "Fartsgrense",
            "answer_d_no": "Antall felt",
            "answer_a_th": "ความเร็วแนะนำ",
            "answer_b_th": "ระยะทางถึงเมืองถัดไป",
            "answer_c_th": "ขีดจำกัดความเร็ว",
            "answer_d_th": "จำนวนช่องจราจร",
            "answer_a_en": "Recommended speed",
            "answer_b_en": "Distance to next city",
            "answer_c_en": "Speed limit",
            "answer_d_en": "Number of lanes",
            "correct_answer": "C",
            "explanation_no": "Runde skilt med rød kant og hvit bakgrunn med et tall angir fartsgrensen i km/t.",
            "explanation_th": "ป้ายวงกลมขอบแดงพื้นขาวที่มีตัวเลขแสดงขีดจำกัดความเร็วเป็น กม./ชม.",
            "explanation_en": "Round signs with red border and white background with a number indicate the speed limit in km/h.",
            "category": "Traffic Signs",
            "difficulty": "easy",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/NO_road_sign_362.50.svg/250px-NO_road_sign_362.50.svg.png"
        },
        {
            "question_text_no": "Hva betyr et skilt med hvit pil på blå bakgrunn?",
            "question_text_th": "ป้ายลูกศรสีขาวบนพื้นสีน้ำเงินหมายความว่าอะไร?",
            "question_text_en": "What does a white arrow on blue background sign mean?",
            "answer_a_no": "Påbudt kjøreretning",
            "answer_b_no": "Enveistrafikk",
            "answer_c_no": "Motorvei",
            "answer_d_no": "Blindvei",
            "answer_a_th": "ทิศทางบังคับ",
            "answer_b_th": "ทางเดินรถทางเดียว",
            "answer_c_th": "ทางด่วน",
            "answer_d_th": "ถนนตัน",
            "answer_a_en": "Mandatory direction",
            "answer_b_en": "One-way traffic",
            "answer_c_en": "Highway",
            "answer_d_en": "Dead end",
            "correct_answer": "A",
            "explanation_no": "Hvit pil på blå bakgrunn er et påbudsskilt som viser obligatorisk kjøreretning.",
            "explanation_th": "ลูกศรสีขาวบนพื้นสีน้ำเงินเป็นป้ายบังคับที่แสดงทิศทางขับขี่ที่ต้องปฏิบัติตาม",
            "explanation_en": "White arrow on blue background is a mandatory sign showing the required driving direction.",
            "category": "Traffic Signs",
            "difficulty": "medium",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/NO_road_sign_402.1.svg/250px-NO_road_sign_402.1.svg.png"
        },
        {
            "question_text_no": "Hva betyr skiltet med to piler som peker mot hverandre?",
            "question_text_th": "ป้ายที่มีลูกศรสองอันชี้เข้าหากันหมายความว่าอะไร?",
            "question_text_en": "What does the sign with two arrows pointing at each other mean?",
            "answer_a_no": "Vei med møtende trafikk",
            "answer_b_no": "Veien smalner",
            "answer_c_no": "Forbikjøring forbudt",
            "answer_d_no": "Toveis trafikk",
            "answer_a_th": "ถนนมีรถสวนทาง",
            "answer_b_th": "ถนนแคบลง",
            "answer_c_th": "ห้ามแซง",
            "answer_d_th": "การจราจรสองทาง",
            "answer_a_en": "Road with oncoming traffic",
            "answer_b_en": "Road narrows",
            "answer_c_en": "No overtaking",
            "answer_d_en": "Two-way traffic",
            "correct_answer": "D",
            "explanation_no": "Skiltet med to piler som peker mot hverandre varsler om toveis trafikk.",
            "explanation_th": "ป้ายที่มีลูกศรสองอันชี้เข้าหากันเตือนว่ามีการจราจรสองทาง",
            "explanation_en": "The sign with two arrows pointing at each other warns about two-way traffic.",
            "category": "Traffic Signs",
            "difficulty": "medium",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/NO_road_sign_148.svg/250px-NO_road_sign_148.svg.png"
        },
        {
            "question_text_no": "Hva betyr et rundt skilt med rød diagonal stripe over en figur?",
            "question_text_th": "ป้ายวงกลมที่มีเส้นแดงขีดทแยงผ่านสัญลักษณ์หมายความว่าอะไร?",
            "question_text_en": "What does a round sign with red diagonal stripe over a figure mean?",
            "answer_a_no": "Anbefaling",
            "answer_b_no": "Forbudt",
            "answer_c_no": "Advarsel",
            "answer_d_no": "Tillatt med forsiktighet",
            "answer_a_th": "คำแนะนำ",
            "answer_b_th": "ห้าม",
            "answer_c_th": "เตือน",
            "answer_d_th": "อนุญาตด้วยความระมัดระวัง",
            "answer_a_en": "Recommendation",
            "answer_b_en": "Prohibited",
            "answer_c_en": "Warning",
            "answer_d_en": "Allowed with caution",
            "correct_answer": "B",
            "explanation_no": "En rød diagonal stripe over en figur på et rundt skilt betyr at handlingen er forbudt.",
            "explanation_th": "เส้นแดงขีดทแยงผ่านสัญลักษณ์บนป้ายวงกลมหมายความว่าการกระทำนั้นห้าม",
            "explanation_en": "A red diagonal stripe over a figure on a round sign means the action is prohibited.",
            "category": "Traffic Signs",
            "difficulty": "easy",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/NO_road_sign_306.0.svg/250px-NO_road_sign_306.0.svg.png"
        },
        {
            "question_text_no": "Hva betyr et vikeplikt-skilt (nedovervendt trekant)?",
            "question_text_th": "ป้ายให้ทาง (สามเหลี่ยมคว่ำ) หมายความว่าอะไร?",
            "question_text_en": "What does a yield sign (inverted triangle) mean?",
            "answer_a_no": "Du har forkjørsrett",
            "answer_b_no": "Du må stoppe helt",
            "answer_c_no": "Du må gi vikeplikt for kryssende trafikk",
            "answer_d_no": "Farlig sving",
            "answer_a_th": "คุณมีสิทธิ์ไปก่อน",
            "answer_b_th": "คุณต้องหยุดสนิท",
            "answer_c_th": "คุณต้องให้ทางแก่รถที่ตัดผ่าน",
            "answer_d_th": "โค้งอันตราย",
            "answer_a_en": "You have right of way",
            "answer_b_en": "You must stop completely",
            "answer_c_en": "You must yield to crossing traffic",
            "answer_d_en": "Dangerous curve",
            "correct_answer": "C",
            "explanation_no": "Vikeplikt-skiltet (nedovervendt trekant) betyr at du må gi vikeplikt for trafikk på veien du krysser.",
            "explanation_th": "ป้ายให้ทาง (สามเหลี่ยมคว่ำ) หมายความว่าคุณต้องให้ทางแก่รถบนถนนที่คุณจะข้าม",
            "explanation_en": "The yield sign (inverted triangle) means you must give way to traffic on the road you are crossing.",
            "category": "Traffic Signs",
            "difficulty": "easy",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/NO_road_sign_202.svg/250px-NO_road_sign_202.svg.png"
        },
        {
            "question_text_no": "Hva betyr et grønt rektangulært skilt med motorveisymbol?",
            "question_text_th": "ป้ายสี่เหลี่ยมสีเขียวที่มีสัญลักษณ์ทางด่วนหมายความว่าอะไร?",
            "question_text_en": "What does a green rectangular sign with highway symbol mean?",
            "answer_a_no": "Landbruksvei",
            "answer_b_no": "Motorvei begynner",
            "answer_c_no": "Parkering",
            "answer_d_no": "Rasteplass",
            "answer_a_th": "ถนนเกษตร",
            "answer_b_th": "เริ่มทางด่วน",
            "answer_c_th": "ที่จอดรถ",
            "answer_d_th": "จุดพักผ่อน",
            "answer_a_en": "Agricultural road",
            "answer_b_en": "Highway begins",
            "answer_c_en": "Parking",
            "answer_d_en": "Rest area",
            "correct_answer": "B",
            "explanation_no": "Grønt rektangulært skilt med motorveisymbol indikerer at motorveien begynner.",
            "explanation_th": "ป้ายสี่เหลี่ยมสีเขียวที่มีสัญลักษณ์ทางด่วนบ่งบอกว่าทางด่วนเริ่มต้น",
            "explanation_en": "Green rectangular sign with highway symbol indicates the highway begins.",
            "category": "Traffic Signs",
            "difficulty": "medium",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/NO_road_sign_502.svg/250px-NO_road_sign_502.svg.png"
        },
        # ===== ROAD RULES (9 questions) =====
        {
            "question_text_no": "Hva er den generelle fartsgrensen i boligområder i Norge?",
            "question_text_th": "ขีดจำกัดความเร็วทั่วไปในเขตที่อยู่อาศัยในนอร์เวย์คือเท่าไหร่?",
            "question_text_en": "What is the general speed limit in residential areas in Norway?",
            "answer_a_no": "30 km/t",
            "answer_b_no": "50 km/t",
            "answer_c_no": "60 km/t",
            "answer_d_no": "40 km/t",
            "answer_a_th": "30 กม./ชม.",
            "answer_b_th": "50 กม./ชม.",
            "answer_c_th": "60 กม./ชม.",
            "answer_d_th": "40 กม./ชม.",
            "answer_a_en": "30 km/h",
            "answer_b_en": "50 km/h",
            "answer_c_en": "60 km/h",
            "answer_d_en": "40 km/h",
            "correct_answer": "B",
            "explanation_no": "I boligområder uten annen merking er fartsgrensen 50 km/t.",
            "explanation_th": "ในเขตที่อยู่อาศัยที่ไม่มีป้ายระบุอื่น ขีดจำกัดความเร็วคือ 50 กม./ชม.",
            "explanation_en": "In residential areas without other markings, the speed limit is 50 km/h.",
            "category": "Road Rules",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Når må du bruke nærlys på dagtid i Norge?",
            "question_text_th": "เมื่อไหร่ที่คุณต้องเปิดไฟต่ำในเวลากลางวันในนอร์เวย์?",
            "question_text_en": "When must you use low beam lights during daytime in Norway?",
            "answer_a_no": "Bare om vinteren",
            "answer_b_no": "Bare i tunneler",
            "answer_c_no": "Alltid",
            "answer_d_no": "Aldri på dagtid",
            "answer_a_th": "เฉพาะในฤดูหนาว",
            "answer_b_th": "เฉพาะในอุโมงค์",
            "answer_c_th": "ตลอดเวลา",
            "answer_d_th": "ไม่ต้องเปิดในเวลากลางวัน",
            "answer_a_en": "Only in winter",
            "answer_b_en": "Only in tunnels",
            "answer_c_en": "Always",
            "answer_d_en": "Never during daytime",
            "correct_answer": "C",
            "explanation_no": "I Norge er det påbudt å kjøre med lys hele døgnet, hele året.",
            "explanation_th": "ในนอร์เวย์ กฎหมายกำหนดให้เปิดไฟตลอด 24 ชั่วโมง ตลอดทั้งปี",
            "explanation_en": "In Norway, it is mandatory to drive with lights on 24 hours a day, all year round.",
            "category": "Road Rules",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Er det lov å bruke mobiltelefon mens du kjører?",
            "question_text_th": "อนุญาตให้ใช้โทรศัพท์มือถือขณะขับรถหรือไม่?",
            "question_text_en": "Is it allowed to use a mobile phone while driving?",
            "answer_a_no": "Ja, alltid",
            "answer_b_no": "Ja, bare med én hånd på rattet",
            "answer_c_no": "Nei, bare med handsfree",
            "answer_d_no": "Ja, kun i lave hastigheter",
            "answer_a_th": "ได้ ตลอดเวลา",
            "answer_b_th": "ได้ ถ้าจับพวงมาลัยด้วยมือข้างหนึ่ง",
            "answer_c_th": "ไม่ได้ ยกเว้นใช้แฮนด์ฟรี",
            "answer_d_th": "ได้ เฉพาะที่ความเร็วต่ำ",
            "answer_a_en": "Yes, always",
            "answer_b_en": "Yes, with one hand on the wheel",
            "answer_c_en": "No, only with hands-free",
            "answer_d_en": "Yes, only at low speeds",
            "correct_answer": "C",
            "explanation_no": "Det er forbudt å bruke håndholdt mobiltelefon mens du kjører. Bare handsfree er tillatt.",
            "explanation_th": "ห้ามใช้โทรศัพท์มือถือแบบถือด้วยมือขณะขับรถ อนุญาตเฉพาะแฮนด์ฟรีเท่านั้น",
            "explanation_en": "It is forbidden to use a handheld mobile phone while driving. Only hands-free is allowed.",
            "category": "Road Rules",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er minstealderen for å få vanlig førerkort (klasse B) i Norge?",
            "question_text_th": "อายุขั้นต่ำในการได้ใบขับขี่ปกติ (คลาส B) ในนอร์เวย์คือเท่าไหร่?",
            "question_text_en": "What is the minimum age to get a regular driving license (class B) in Norway?",
            "answer_a_no": "16 år",
            "answer_b_no": "17 år",
            "answer_c_no": "18 år",
            "answer_d_no": "21 år",
            "answer_a_th": "16 ปี",
            "answer_b_th": "17 ปี",
            "answer_c_th": "18 ปี",
            "answer_d_th": "21 ปี",
            "answer_a_en": "16 years",
            "answer_b_en": "17 years",
            "answer_c_en": "18 years",
            "answer_d_en": "21 years",
            "correct_answer": "C",
            "explanation_no": "Du må være minst 18 år for å få vanlig førerkort klasse B i Norge.",
            "explanation_th": "คุณต้องมีอายุอย่างน้อย 18 ปีเพื่อรับใบขับขี่คลาส B ปกติในนอร์เวย์",
            "explanation_en": "You must be at least 18 years old to get a regular class B driving license in Norway.",
            "category": "Road Rules",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Når er det påbudt å bruke piggdekk eller vinterdekk i Norge?",
            "question_text_th": "เมื่อไหร่ที่บังคับให้ใช้ยางตะปูหรือยางฤดูหนาวในนอร์เวย์?",
            "question_text_en": "When is it mandatory to use studded or winter tires in Norway?",
            "answer_a_no": "Hele året",
            "answer_b_no": "Fra 1. november til første mandag etter 2. påskedag",
            "answer_c_no": "Bare i desember",
            "answer_d_no": "Det er aldri påbudt",
            "answer_a_th": "ตลอดทั้งปี",
            "answer_b_th": "ตั้งแต่ 1 พ.ย. ถึงวันจันทร์แรกหลังวันอีสเตอร์",
            "answer_c_th": "เฉพาะเดือนธันวาคม",
            "answer_d_th": "ไม่บังคับเลย",
            "answer_a_en": "All year round",
            "answer_b_en": "From Nov 1 to first Monday after Easter",
            "answer_c_en": "Only in December",
            "answer_d_en": "It is never mandatory",
            "correct_answer": "B",
            "explanation_no": "Vinterdekk er påbudt fra 1. november til første mandag etter 2. påskedag når forholdene tilsier det.",
            "explanation_th": "ยางฤดูหนาวบังคับใช้ตั้งแต่ 1 พฤศจิกายน ถึงวันจันทร์แรกหลังวันอีสเตอร์เมื่อสภาพอากาศต้องการ",
            "explanation_en": "Winter tires are mandatory from November 1 to the first Monday after Easter when conditions require it.",
            "category": "Road Rules",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva skal du gjøre når du nærmer deg et gangfelt?",
            "question_text_th": "คุณควรทำอะไรเมื่อเข้าใกล้ทางม้าลาย?",
            "question_text_en": "What should you do when approaching a pedestrian crossing?",
            "answer_a_no": "Øke farten for å passere raskt",
            "answer_b_no": "Bremse ned og være klar til å stoppe",
            "answer_c_no": "Tute for å varsle fotgjengere",
            "answer_d_no": "Bytte fil",
            "answer_a_th": "เร่งความเร็วเพื่อผ่านไปเร็วๆ",
            "answer_b_th": "ชะลอและเตรียมหยุด",
            "answer_c_th": "บีบแตรเพื่อเตือนคนเดินเท้า",
            "answer_d_th": "เปลี่ยนเลน",
            "answer_a_en": "Speed up to pass quickly",
            "answer_b_en": "Slow down and be ready to stop",
            "answer_c_en": "Honk to warn pedestrians",
            "answer_d_en": "Change lanes",
            "correct_answer": "B",
            "explanation_no": "Du må alltid bremse ned og være klar til å stoppe ved gangfelt. Fotgjengere har alltid forkjørsrett.",
            "explanation_th": "คุณต้องชะลอและเตรียมหยุดที่ทางม้าลายเสมอ คนเดินเท้ามีสิทธิ์ไปก่อนเสมอ",
            "explanation_en": "You must always slow down and be ready to stop at a pedestrian crossing. Pedestrians always have the right of way.",
            "category": "Road Rules",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er reglene for parkering i mørke?",
            "question_text_th": "กฎการจอดรถในที่มืดคืออะไร?",
            "question_text_en": "What are the rules for parking in the dark?",
            "answer_a_no": "Du trenger ikke lys",
            "answer_b_no": "Du må ha parkeringslys på",
            "answer_c_no": "Du må alltid ha fjernlys på",
            "answer_d_no": "Du må bruke varselblinklys",
            "answer_a_th": "ไม่ต้องเปิดไฟ",
            "answer_b_th": "ต้องเปิดไฟจอดรถ",
            "answer_c_th": "ต้องเปิดไฟสูงเสมอ",
            "answer_d_th": "ต้องใช้ไฟกะพริบฉุกเฉิน",
            "answer_a_en": "You don't need lights",
            "answer_b_en": "You must have parking lights on",
            "answer_c_en": "You must always have high beams on",
            "answer_d_en": "You must use hazard lights",
            "correct_answer": "B",
            "explanation_no": "Når du parkerer i mørke utenfor opplyste områder, må du ha parkeringslys på.",
            "explanation_th": "เมื่อจอดรถในที่มืดนอกพื้นที่ที่มีไฟส่องสว่าง คุณต้องเปิดไฟจอดรถ",
            "explanation_en": "When parking in the dark outside lit areas, you must have parking lights on.",
            "category": "Road Rules",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva er regelen for bruk av blinklys?",
            "question_text_th": "กฎการใช้ไฟเลี้ยวคืออะไร?",
            "question_text_en": "What is the rule for using turn signals?",
            "answer_a_no": "Bare i kryss",
            "answer_b_no": "Bare ved filskifte",
            "answer_c_no": "Ved alle retningsendringer",
            "answer_d_no": "Bare på motorvei",
            "answer_a_th": "เฉพาะที่ทางแยก",
            "answer_b_th": "เฉพาะเมื่อเปลี่ยนเลน",
            "answer_c_th": "เมื่อเปลี่ยนทิศทางทุกครั้ง",
            "answer_d_th": "เฉพาะบนทางด่วน",
            "answer_a_en": "Only at intersections",
            "answer_b_en": "Only when changing lanes",
            "answer_c_en": "At all direction changes",
            "answer_d_en": "Only on highways",
            "correct_answer": "C",
            "explanation_no": "Du må alltid bruke blinklys ved alle retningsendringer, inkludert svinging, filskifte og parkering.",
            "explanation_th": "คุณต้องใช้ไฟเลี้ยวเมื่อเปลี่ยนทิศทางทุกครั้ง รวมถึงการเลี้ยว เปลี่ยนเลน และจอดรถ",
            "explanation_en": "You must always use turn signals at all direction changes, including turning, lane changes, and parking.",
            "category": "Road Rules",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er reglene for kjøring i rundkjøring?",
            "question_text_th": "กฎการขับขี่ในวงเวียนคืออะไร?",
            "question_text_en": "What are the rules for driving in a roundabout?",
            "answer_a_no": "Gi vikeplikt for trafikk inne i rundkjøringen",
            "answer_b_no": "Trafikk inne i rundkjøringen gir vikeplikt for deg",
            "answer_c_no": "Første bil inn har forkjørsrett",
            "answer_d_no": "Det finnes ingen regler",
            "answer_a_th": "ให้ทางแก่รถในวงเวียน",
            "answer_b_th": "รถในวงเวียนต้องให้ทางคุณ",
            "answer_c_th": "รถที่เข้าก่อนมีสิทธิ์ไปก่อน",
            "answer_d_th": "ไม่มีกฎ",
            "answer_a_en": "Yield to traffic inside the roundabout",
            "answer_b_en": "Traffic inside yields to you",
            "answer_c_en": "First car in has right of way",
            "answer_d_en": "There are no rules",
            "correct_answer": "A",
            "explanation_no": "Du må alltid gi vikeplikt for trafikk som allerede er inne i rundkjøringen.",
            "explanation_th": "คุณต้องให้ทางแก่รถที่อยู่ในวงเวียนแล้วเสมอ",
            "explanation_en": "You must always yield to traffic already inside the roundabout.",
            "category": "Road Rules",
            "difficulty": "easy"
        },
        # ===== RIGHT OF WAY (9 questions) =====
        {
            "question_text_no": "Hvem har vikeplikt i et kryss uten skilt?",
            "question_text_th": "ใครต้องให้ทางในทางแยกที่ไม่มีป้าย?",
            "question_text_en": "Who must give way at an intersection without signs?",
            "answer_a_no": "Trafikk fra venstre gir vikeplikt",
            "answer_b_no": "Trafikk fra høyre gir vikeplikt",
            "answer_c_no": "Den som kommer først",
            "answer_d_no": "Alle må stoppe",
            "answer_a_th": "รถจากทางซ้ายต้องให้ทาง",
            "answer_b_th": "รถจากทางขวาต้องให้ทาง",
            "answer_c_th": "คันที่มาถึงก่อน",
            "answer_d_th": "ทุกคันต้องหยุด",
            "answer_a_en": "Traffic from left gives way",
            "answer_b_en": "Traffic from right gives way",
            "answer_c_en": "Whoever arrives first",
            "answer_d_en": "Everyone must stop",
            "correct_answer": "A",
            "explanation_no": "Høyreregelen gjelder: Du gir vikeplikt for trafikk fra høyre. Trafikk fra venstre gir vikeplikt for deg.",
            "explanation_th": "กฎทางขวามีผล: คุณให้ทางแก่รถจากทางขวา รถจากทางซ้ายต้องให้ทางคุณ",
            "explanation_en": "The right-hand rule applies: You yield to traffic from the right. Traffic from the left yields to you.",
            "category": "Right of Way",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hvem har vikeplikt når du kjører ut av en parkeringsplass?",
            "question_text_th": "ใครต้องให้ทางเมื่อคุณขับออกจากที่จอดรถ?",
            "question_text_en": "Who has right of way when you exit a parking lot?",
            "answer_a_no": "Du har forkjørsrett",
            "answer_b_no": "Trafikk på veien har forkjørsrett",
            "answer_c_no": "Det avhenger av tid på dagen",
            "answer_d_no": "Fotgjengere bare",
            "answer_a_th": "คุณมีสิทธิ์ไปก่อน",
            "answer_b_th": "รถบนถนนมีสิทธิ์ไปก่อน",
            "answer_c_th": "ขึ้นอยู่กับช่วงเวลาของวัน",
            "answer_d_th": "คนเดินเท้าเท่านั้น",
            "answer_a_en": "You have right of way",
            "answer_b_en": "Traffic on the road has right of way",
            "answer_c_en": "It depends on time of day",
            "answer_d_en": "Pedestrians only",
            "correct_answer": "B",
            "explanation_no": "Når du kjører ut av parkeringsplass, må du alltid gi vikeplikt for all trafikk på veien.",
            "explanation_th": "เมื่อขับออกจากที่จอดรถ คุณต้องให้ทางแก่รถบนถนนเสมอ",
            "explanation_en": "When exiting a parking lot, you must always yield to all traffic on the road.",
            "category": "Right of Way",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva betyr forkjørsrett?",
            "question_text_th": "สิทธิ์ในการไปก่อนหมายความว่าอะไร?",
            "question_text_en": "What does right of way mean?",
            "answer_a_no": "Du kan kjøre uten å bremse",
            "answer_b_no": "Andre kjøretøy må gi vikeplikt for deg",
            "answer_c_no": "Du kan ignorere trafikklys",
            "answer_d_no": "Du kan kjøre på fortauet",
            "answer_a_th": "คุณสามารถขับโดยไม่ต้องเบรก",
            "answer_b_th": "ยานพาหนะอื่นต้องให้ทางคุณ",
            "answer_c_th": "คุณสามารถเพิกเฉยต่อสัญญาณไฟจราจร",
            "answer_d_th": "คุณสามารถขับบนทางเท้า",
            "answer_a_en": "You can drive without braking",
            "answer_b_en": "Other vehicles must yield to you",
            "answer_c_en": "You can ignore traffic lights",
            "answer_d_en": "You can drive on the sidewalk",
            "correct_answer": "B",
            "explanation_no": "Forkjørsrett betyr at andre kjøretøy må gi vikeplikt for deg, men du må fortsatt kjøre forsiktig.",
            "explanation_th": "สิทธิ์ในการไปก่อนหมายความว่ายานพาหนะอื่นต้องให้ทางคุณ แต่คุณยังต้องขับอย่างระมัดระวัง",
            "explanation_en": "Right of way means other vehicles must yield to you, but you must still drive carefully.",
            "category": "Right of Way",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hvem har vikeplikt når to biler møtes på en smal vei?",
            "question_text_th": "ใครต้องให้ทางเมื่อรถสองคันพบกันบนถนนแคบ?",
            "question_text_en": "Who has right of way when two cars meet on a narrow road?",
            "answer_a_no": "Den som kjører oppover",
            "answer_b_no": "Den som kjører nedover",
            "answer_c_no": "Den med størst bil",
            "answer_d_no": "Den som blinker først",
            "answer_a_th": "คันที่ขับขึ้นเขา",
            "answer_b_th": "คันที่ขับลงเขา",
            "answer_c_th": "คันที่ใหญ่กว่า",
            "answer_d_th": "คันที่กะพริบไฟก่อน",
            "answer_a_en": "The one driving uphill",
            "answer_b_en": "The one driving downhill",
            "answer_c_en": "The one with the bigger car",
            "answer_d_en": "The one who flashes lights first",
            "correct_answer": "B",
            "explanation_no": "På smale veier har den som kjører nedover normalt vikeplikt fordi det er lettere å stoppe oppover.",
            "explanation_th": "บนถนนแคบ คันที่ขับลงเขาปกติต้องให้ทางเพราะการหยุดเมื่อขับขึ้นเขาง่ายกว่า",
            "explanation_en": "On narrow roads, the one driving downhill normally must yield because it's easier to stop when going uphill.",
            "category": "Right of Way",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Har utrykningskjøretøy med blålys alltid forkjørsrett?",
            "question_text_th": "รถฉุกเฉินที่เปิดไฟน้ำเงินมีสิทธิ์ไปก่อนเสมอหรือไม่?",
            "question_text_en": "Do emergency vehicles with blue lights always have right of way?",
            "answer_a_no": "Nei, aldri",
            "answer_b_no": "Ja, alltid",
            "answer_c_no": "Bare på motorvei",
            "answer_d_no": "Bare i byområder",
            "answer_a_th": "ไม่ ไม่เคย",
            "answer_b_th": "ใช่ เสมอ",
            "answer_c_th": "เฉพาะบนทางด่วน",
            "answer_d_th": "เฉพาะในเขตเมือง",
            "answer_a_en": "No, never",
            "answer_b_en": "Yes, always",
            "answer_c_en": "Only on highways",
            "answer_d_en": "Only in urban areas",
            "correct_answer": "B",
            "explanation_no": "Utrykningskjøretøy med blålys og sirene har alltid forkjørsrett. Du må kjøre til side og stoppe.",
            "explanation_th": "รถฉุกเฉินที่เปิดไฟน้ำเงินและไซเรนมีสิทธิ์ไปก่อนเสมอ คุณต้องหลบไปข้างทางและหยุด",
            "explanation_en": "Emergency vehicles with blue lights and sirens always have right of way. You must pull over and stop.",
            "category": "Right of Way",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hvem har vikeplikt ved T-kryss uten skilt?",
            "question_text_th": "ใครต้องให้ทางที่ทางแยก T ที่ไม่มีป้าย?",
            "question_text_en": "Who has right of way at a T-intersection without signs?",
            "answer_a_no": "Den på gjennomgående vei",
            "answer_b_no": "Den som kommer fra sideveien",
            "answer_c_no": "Høyreregelen gjelder",
            "answer_d_no": "Den som har størst bil",
            "answer_a_th": "รถบนถนนหลัก",
            "answer_b_th": "รถจากถนนแยก",
            "answer_c_th": "ใช้กฎทางขวา",
            "answer_d_th": "รถที่ใหญ่กว่า",
            "answer_a_en": "The one on the main road",
            "answer_b_en": "The one from the side road",
            "answer_c_en": "The right-hand rule applies",
            "answer_d_en": "The one with the bigger car",
            "correct_answer": "C",
            "explanation_no": "Ved T-kryss uten skilt gjelder høyreregelen. Trafikk fra høyre har forkjørsrett.",
            "explanation_th": "ที่ทางแยก T ที่ไม่มีป้าย ใช้กฎทางขวา รถจากทางขวามีสิทธิ์ไปก่อน",
            "explanation_en": "At a T-intersection without signs, the right-hand rule applies. Traffic from the right has right of way.",
            "category": "Right of Way",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hvem har vikeplikt ved avkjøring fra hovedvei?",
            "question_text_th": "ใครต้องให้ทางเมื่อออกจากถนนหลัก?",
            "question_text_en": "Who has right of way when exiting a main road?",
            "answer_a_no": "Du har forkjørsrett når du svinger av",
            "answer_b_no": "Trafikk bak deg har vikeplikt",
            "answer_c_no": "Du gir vikeplikt for gående og syklende",
            "answer_d_no": "Ingen har vikeplikt",
            "answer_a_th": "คุณมีสิทธิ์ไปก่อนเมื่อเลี้ยวออก",
            "answer_b_th": "รถด้านหลังคุณต้องให้ทาง",
            "answer_c_th": "คุณต้องให้ทางแก่คนเดินเท้าและจักรยาน",
            "answer_d_th": "ไม่มีใครต้องให้ทาง",
            "answer_a_en": "You have right of way when turning off",
            "answer_b_en": "Traffic behind you must yield",
            "answer_c_en": "You yield to pedestrians and cyclists",
            "answer_d_en": "Nobody has right of way",
            "correct_answer": "C",
            "explanation_no": "Når du svinger av hovedveien, må du gi vikeplikt for fotgjengere og syklister som krysser.",
            "explanation_th": "เมื่อคุณเลี้ยวออกจากถนนหลัก คุณต้องให้ทางแก่คนเดินเท้าและนักปั่นจักรยานที่ข้ามทาง",
            "explanation_en": "When turning off the main road, you must yield to pedestrians and cyclists crossing.",
            "category": "Right of Way",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva gjør du når trafikklyset er gult?",
            "question_text_th": "คุณทำอะไรเมื่อสัญญาณไฟจราจรเป็นสีเหลือง?",
            "question_text_en": "What do you do when the traffic light is yellow?",
            "answer_a_no": "Øke farten for å rekke grønt",
            "answer_b_no": "Stoppe hvis du kan gjøre det trygt",
            "answer_c_no": "Ignorere det",
            "answer_d_no": "Blinke med lysene",
            "answer_a_th": "เร่งความเร็วเพื่อให้ทันไฟเขียว",
            "answer_b_th": "หยุดถ้าสามารถหยุดได้อย่างปลอดภัย",
            "answer_c_th": "เพิกเฉย",
            "answer_d_th": "กะพริบไฟ",
            "answer_a_en": "Speed up to catch the green",
            "answer_b_en": "Stop if you can do so safely",
            "answer_c_en": "Ignore it",
            "answer_d_en": "Flash your lights",
            "correct_answer": "B",
            "explanation_no": "Gult lys betyr at du skal stoppe hvis du kan gjøre det trygt. Hvis du allerede er i krysset, fullfør passeringen.",
            "explanation_th": "ไฟเหลืองหมายความว่าคุณควรหยุดถ้าสามารถหยุดได้อย่างปลอดภัย ถ้าอยู่ในทางแยกแล้ว ให้ขับผ่านต่อไป",
            "explanation_en": "Yellow light means you should stop if you can do so safely. If already in the intersection, complete the crossing.",
            "category": "Right of Way",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hvem har vikeplikt i en rundkjøring?",
            "question_text_th": "ใครต้องให้ทางในวงเวียน?",
            "question_text_en": "Who has right of way in a roundabout?",
            "answer_a_no": "Den som kjører inn i rundkjøringen",
            "answer_b_no": "Den som allerede er inne i rundkjøringen",
            "answer_c_no": "Den største bilen",
            "answer_d_no": "Den som blinker",
            "answer_a_th": "คันที่เข้าวงเวียน",
            "answer_b_th": "คันที่อยู่ในวงเวียนแล้ว",
            "answer_c_th": "รถที่ใหญ่ที่สุด",
            "answer_d_th": "คันที่เปิดไฟเลี้ยว",
            "answer_a_en": "The one entering the roundabout",
            "answer_b_en": "The one already in the roundabout",
            "answer_c_en": "The biggest car",
            "answer_d_en": "The one signaling",
            "correct_answer": "B",
            "explanation_no": "Trafikk som allerede er inne i rundkjøringen har forkjørsrett. Du som kjører inn må gi vikeplikt.",
            "explanation_th": "รถที่อยู่ในวงเวียนแล้วมีสิทธิ์ไปก่อน คุณที่จะเข้าวงเวียนต้องให้ทาง",
            "explanation_en": "Traffic already in the roundabout has right of way. You entering must yield.",
            "category": "Right of Way",
            "difficulty": "easy"
        },
        # ===== SPEED LIMITS (9 questions) =====
        {
            "question_text_no": "Hva er fartsgrensen på motorvei i Norge?",
            "question_text_th": "ขีดจำกัดความเร็วบนทางด่วนในนอร์เวย์คือเท่าไหร่?",
            "question_text_en": "What is the speed limit on highways in Norway?",
            "answer_a_no": "100 km/t",
            "answer_b_no": "110 km/t",
            "answer_c_no": "120 km/t",
            "answer_d_no": "90 km/t",
            "answer_a_th": "100 กม./ชม.",
            "answer_b_th": "110 กม./ชม.",
            "answer_c_th": "120 กม./ชม.",
            "answer_d_th": "90 กม./ชม.",
            "answer_a_en": "100 km/h",
            "answer_b_en": "110 km/h",
            "answer_c_en": "120 km/h",
            "answer_d_en": "90 km/h",
            "correct_answer": "B",
            "explanation_no": "Standard fartsgrense på motorvei i Norge er 110 km/t, men kan variere basert på skilting.",
            "explanation_th": "ขีดจำกัดความเร็วมาตรฐานบนทางด่วนในนอร์เวย์คือ 110 กม./ชม. แต่อาจแตกต่างกันตามป้าย",
            "explanation_en": "Standard speed limit on highways in Norway is 110 km/h, but may vary based on signage.",
            "category": "Speed Limits",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er fartsgrensen i en 30-sone?",
            "question_text_th": "ขีดจำกัดความเร็วในโซน 30 คือเท่าไหร่?",
            "question_text_en": "What is the speed limit in a 30-zone?",
            "answer_a_no": "40 km/t",
            "answer_b_no": "30 km/t",
            "answer_c_no": "20 km/t",
            "answer_d_no": "50 km/t",
            "answer_a_th": "40 กม./ชม.",
            "answer_b_th": "30 กม./ชม.",
            "answer_c_th": "20 กม./ชม.",
            "answer_d_th": "50 กม./ชม.",
            "answer_a_en": "40 km/h",
            "answer_b_en": "30 km/h",
            "answer_c_en": "20 km/h",
            "answer_d_en": "50 km/h",
            "correct_answer": "B",
            "explanation_no": "I en 30-sone er fartsgrensen 30 km/t. Disse sonene er vanlige nær skoler.",
            "explanation_th": "ในโซน 30 ขีดจำกัดความเร็วคือ 30 กม./ชม. โซนเหล่านี้พบได้ทั่วไปใกล้โรงเรียน",
            "explanation_en": "In a 30-zone, the speed limit is 30 km/h. These zones are common near schools.",
            "category": "Speed Limits",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er fartsgrensen på vanlige landeveier utenfor tettbygd strøk?",
            "question_text_th": "ขีดจำกัดความเร็วบนถนนชนบททั่วไปนอกเขตเมืองคือเท่าไหร่?",
            "question_text_en": "What is the speed limit on regular country roads outside urban areas?",
            "answer_a_no": "60 km/t",
            "answer_b_no": "70 km/t",
            "answer_c_no": "80 km/t",
            "answer_d_no": "90 km/t",
            "answer_a_th": "60 กม./ชม.",
            "answer_b_th": "70 กม./ชม.",
            "answer_c_th": "80 กม./ชม.",
            "answer_d_th": "90 กม./ชม.",
            "answer_a_en": "60 km/h",
            "answer_b_en": "70 km/h",
            "answer_c_en": "80 km/h",
            "answer_d_en": "90 km/h",
            "correct_answer": "C",
            "explanation_no": "Fartsgrensen på vanlige landeveier utenfor tettbygd strøk er 80 km/t.",
            "explanation_th": "ขีดจำกัดความเร็วบนถนนชนบททั่วไปนอกเขตเมืองคือ 80 กม./ชม.",
            "explanation_en": "The speed limit on regular country roads outside urban areas is 80 km/h.",
            "category": "Speed Limits",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva skjer hvis du kjører 20 km/t over fartsgrensen?",
            "question_text_th": "จะเกิดอะไรขึ้นถ้าคุณขับเร็วเกิน 20 กม./ชม.?",
            "question_text_en": "What happens if you drive 20 km/h over the speed limit?",
            "answer_a_no": "Ingen konsekvens",
            "answer_b_no": "Bare en advarsel",
            "answer_c_no": "Bot og prikkbelastning",
            "answer_d_no": "Fengsel",
            "answer_a_th": "ไม่มีผลอะไร",
            "answer_b_th": "แค่คำเตือน",
            "answer_c_th": "ค่าปรับและหักคะแนน",
            "answer_d_th": "จำคุก",
            "answer_a_en": "No consequence",
            "answer_b_en": "Just a warning",
            "answer_c_en": "Fine and penalty points",
            "answer_d_en": "Prison",
            "correct_answer": "C",
            "explanation_no": "Å kjøre 20 km/t over fartsgrensen resulterer i bot og prikkbelastning på førerkortet.",
            "explanation_th": "การขับเร็วเกิน 20 กม./ชม. จะถูกปรับและหักคะแนนจากใบขับขี่",
            "explanation_en": "Driving 20 km/h over the speed limit results in a fine and penalty points on your license.",
            "category": "Speed Limits",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva er fartsgrensen forbi en skole i skoletiden?",
            "question_text_th": "ขีดจำกัดความเร็วผ่านโรงเรียนในช่วงเวลาเรียนคือเท่าไหร่?",
            "question_text_en": "What is the speed limit past a school during school hours?",
            "answer_a_no": "20 km/t",
            "answer_b_no": "30 km/t",
            "answer_c_no": "40 km/t",
            "answer_d_no": "50 km/t",
            "answer_a_th": "20 กม./ชม.",
            "answer_b_th": "30 กม./ชม.",
            "answer_c_th": "40 กม./ชม.",
            "answer_d_th": "50 กม./ชม.",
            "answer_a_en": "20 km/h",
            "answer_b_en": "30 km/h",
            "answer_c_en": "40 km/h",
            "answer_d_en": "50 km/h",
            "correct_answer": "B",
            "explanation_no": "Ved skoler er det vanligvis 30-sone for å beskytte barn.",
            "explanation_th": "บริเวณโรงเรียนโดยปกติจะเป็นโซน 30 เพื่อความปลอดภัยของเด็ก",
            "explanation_en": "Near schools there is usually a 30-zone to protect children.",
            "category": "Speed Limits",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Kan du miste førerkortet for fartsovertredelse?",
            "question_text_th": "คุณสามารถถูกยึดใบขับขี่จากการขับเร็วเกินได้หรือไม่?",
            "question_text_en": "Can you lose your license for speeding?",
            "answer_a_no": "Nei, aldri",
            "answer_b_no": "Ja, ved grove overtredelser",
            "answer_c_no": "Bare ved gjentatte overtredelser",
            "answer_d_no": "Bare i 30-soner",
            "answer_a_th": "ไม่ ไม่เคย",
            "answer_b_th": "ใช่ เมื่อทำผิดร้ายแรง",
            "answer_c_th": "เฉพาะเมื่อทำผิดซ้ำ",
            "answer_d_th": "เฉพาะในโซน 30",
            "answer_a_en": "No, never",
            "answer_b_en": "Yes, for serious violations",
            "answer_c_en": "Only for repeated violations",
            "answer_d_en": "Only in 30-zones",
            "correct_answer": "B",
            "explanation_no": "Ja, du kan miste førerkortet ved grove fartsovertredelser, for eksempel å kjøre over 30 km/t over grensen.",
            "explanation_th": "ใช่ คุณสามารถถูกยึดใบขับขี่เมื่อทำผิดร้ายแรง เช่น ขับเร็วเกินกว่า 30 กม./ชม.",
            "explanation_en": "Yes, you can lose your license for serious speeding violations, such as driving over 30 km/h above the limit.",
            "category": "Speed Limits",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva er fartsgrensen i gatetun?",
            "question_text_th": "ขีดจำกัดความเร็วในซอยที่อยู่อาศัยคือเท่าไหร่?",
            "question_text_en": "What is the speed limit in residential streets (gatetun)?",
            "answer_a_no": "Gangfart (ca. 5-7 km/t)",
            "answer_b_no": "20 km/t",
            "answer_c_no": "30 km/t",
            "answer_d_no": "50 km/t",
            "answer_a_th": "ความเร็วเดินเท้า (ประมาณ 5-7 กม./ชม.)",
            "answer_b_th": "20 กม./ชม.",
            "answer_c_th": "30 กม./ชม.",
            "answer_d_th": "50 กม./ชม.",
            "answer_a_en": "Walking speed (approx. 5-7 km/h)",
            "answer_b_en": "20 km/h",
            "answer_c_en": "30 km/h",
            "answer_d_en": "50 km/h",
            "correct_answer": "A",
            "explanation_no": "I gatetun er fartsgrensen gangfart, som er ca. 5-7 km/t. Fotgjengere har forkjørsrett.",
            "explanation_th": "ในซอยที่อยู่อาศัย ขีดจำกัดความเร็วคือความเร็วเดินเท้า ประมาณ 5-7 กม./ชม. คนเดินเท้ามีสิทธิ์ไปก่อน",
            "explanation_en": "In residential streets (gatetun), the speed limit is walking speed, about 5-7 km/h. Pedestrians have right of way.",
            "category": "Speed Limits",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva er fartsgrensen i tunneler uten skilting?",
            "question_text_th": "ขีดจำกัดความเร็วในอุโมงค์ที่ไม่มีป้ายคือเท่าไหร่?",
            "question_text_en": "What is the speed limit in tunnels without signs?",
            "answer_a_no": "60 km/t",
            "answer_b_no": "70 km/t",
            "answer_c_no": "80 km/t",
            "answer_d_no": "Samme som veien utenfor",
            "answer_a_th": "60 กม./ชม.",
            "answer_b_th": "70 กม./ชม.",
            "answer_c_th": "80 กม./ชม.",
            "answer_d_th": "เท่ากับถนนด้านนอก",
            "answer_a_en": "60 km/h",
            "answer_b_en": "70 km/h",
            "answer_c_en": "80 km/h",
            "answer_d_en": "Same as the road outside",
            "correct_answer": "D",
            "explanation_no": "Hvis det ikke er egne skilt i tunnelen, gjelder den generelle fartsgrensen for veien.",
            "explanation_th": "ถ้าไม่มีป้ายเฉพาะในอุโมงค์ จะใช้ขีดจำกัดความเร็วทั่วไปของถนน",
            "explanation_en": "If there are no specific signs in the tunnel, the general speed limit for the road applies.",
            "category": "Speed Limits",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva er anbefalt hastighet i fotgjengersoner?",
            "question_text_th": "ความเร็วที่แนะนำในเขตคนเดินเท้าคือเท่าไหร่?",
            "question_text_en": "What is the recommended speed in pedestrian zones?",
            "answer_a_no": "Gangfart",
            "answer_b_no": "15 km/t",
            "answer_c_no": "30 km/t",
            "answer_d_no": "Kjøring er forbudt",
            "answer_a_th": "ความเร็วเดินเท้า",
            "answer_b_th": "15 กม./ชม.",
            "answer_c_th": "30 กม./ชม.",
            "answer_d_th": "ห้ามขับรถ",
            "answer_a_en": "Walking speed",
            "answer_b_en": "15 km/h",
            "answer_c_en": "30 km/h",
            "answer_d_en": "Driving is forbidden",
            "correct_answer": "A",
            "explanation_no": "I fotgjengersoner bør du kjøre i gangfart og gi forkjørsrett til alle fotgjengere.",
            "explanation_th": "ในเขตคนเดินเท้า คุณควรขับด้วยความเร็วเดินเท้าและให้สิทธิ์ไปก่อนแก่คนเดินเท้าทุกคน",
            "explanation_en": "In pedestrian zones, you should drive at walking speed and give right of way to all pedestrians.",
            "category": "Speed Limits",
            "difficulty": "easy"
        },
        # ===== SAFETY (9 questions) =====
        {
            "question_text_no": "Hva er den lovlige promillegrensen for førere i Norge?",
            "question_text_th": "ขีดจำกัดแอลกอฮอล์ในเลือดที่ถูกกฎหมายสำหรับคนขับในนอร์เวย์คือเท่าไหร่?",
            "question_text_en": "What is the legal blood alcohol limit for drivers in Norway?",
            "answer_a_no": "0.5 promille",
            "answer_b_no": "0.2 promille",
            "answer_c_no": "0.0 promille",
            "answer_d_no": "0.8 promille",
            "answer_a_th": "0.5‰",
            "answer_b_th": "0.2‰",
            "answer_c_th": "0.0‰",
            "answer_d_th": "0.8‰",
            "answer_a_en": "0.5‰",
            "answer_b_en": "0.2‰",
            "answer_c_en": "0.0‰",
            "answer_d_en": "0.8‰",
            "correct_answer": "B",
            "explanation_no": "I Norge er promillegrensen 0.2. Dette er en av de strengeste grensene i Europa.",
            "explanation_th": "ในนอร์เวย์ ขีดจำกัดแอลกอฮอล์ในเลือดคือ 0.2‰ ซึ่งเป็นหนึ่งในขีดจำกัดที่เข้มงวดที่สุดในยุโรป",
            "explanation_en": "In Norway, the blood alcohol limit is 0.2‰. This is one of the strictest limits in Europe.",
            "category": "Safety",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hvem må bruke bilbelte?",
            "question_text_th": "ใครต้องคาดเข็มขัดนิรภัย?",
            "question_text_en": "Who must wear a seatbelt?",
            "answer_a_no": "Bare sjåføren",
            "answer_b_no": "Alle passasjerer foran",
            "answer_c_no": "Alle i bilen",
            "answer_d_no": "Bare på motorvei",
            "answer_a_th": "เฉพาะคนขับ",
            "answer_b_th": "ผู้โดยสารด้านหน้าทุกคน",
            "answer_c_th": "ทุกคนในรถ",
            "answer_d_th": "เฉพาะบนทางด่วน",
            "answer_a_en": "Only the driver",
            "answer_b_en": "All front passengers",
            "answer_c_en": "Everyone in the car",
            "answer_d_en": "Only on highways",
            "correct_answer": "C",
            "explanation_no": "I Norge er det påbudt for alle i bilen å bruke bilbelte, uansett hvor de sitter.",
            "explanation_th": "ในนอร์เวย์ ทุกคนในรถต้องคาดเข็มขัดนิรภัย ไม่ว่าจะนั่งที่ไหน",
            "explanation_en": "In Norway, everyone in the car must wear a seatbelt, regardless of where they sit.",
            "category": "Safety",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva bør du gjøre hvis du er involvert i en ulykke?",
            "question_text_th": "คุณควรทำอะไรถ้าเกิดอุบัติเหตุ?",
            "question_text_en": "What should you do if you are involved in an accident?",
            "answer_a_no": "Kjøre videre",
            "answer_b_no": "Stoppe, sikre stedet og gi førstehjelp",
            "answer_c_no": "Ringe bare forsikringsselskapet",
            "answer_d_no": "Vente i bilen",
            "answer_a_th": "ขับต่อไป",
            "answer_b_th": "หยุด รักษาความปลอดภัยบริเวณ และให้การปฐมพยาบาล",
            "answer_c_th": "โทรบริษัทประกันเท่านั้น",
            "answer_d_th": "รอในรถ",
            "answer_a_en": "Drive away",
            "answer_b_en": "Stop, secure the area and provide first aid",
            "answer_c_en": "Only call the insurance company",
            "answer_d_en": "Wait in the car",
            "correct_answer": "B",
            "explanation_no": "Ved ulykker skal du stoppe, sikre ulykkesstedet, gi førstehjelp og ringe 113 ved behov.",
            "explanation_th": "เมื่อเกิดอุบัติเหตุ คุณต้องหยุด รักษาความปลอดภัยบริเวณ ให้การปฐมพยาบาล และโทร 113 ถ้าจำเป็น",
            "explanation_en": "In case of accidents, you must stop, secure the scene, provide first aid and call 113 if needed.",
            "category": "Safety",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er sikkerhetssavstanden ved 80 km/t?",
            "question_text_th": "ระยะห่างที่ปลอดภัยที่ 80 กม./ชม. คือเท่าไหร่?",
            "question_text_en": "What is the safe following distance at 80 km/h?",
            "answer_a_no": "Ca. 1 sekund",
            "answer_b_no": "Ca. 2 sekunder",
            "answer_c_no": "Ca. 3 sekunder",
            "answer_d_no": "Ca. 5 sekunder",
            "answer_a_th": "ประมาณ 1 วินาที",
            "answer_b_th": "ประมาณ 2 วินาที",
            "answer_c_th": "ประมาณ 3 วินาที",
            "answer_d_th": "ประมาณ 5 วินาที",
            "answer_a_en": "About 1 second",
            "answer_b_en": "About 2 seconds",
            "answer_c_en": "About 3 seconds",
            "answer_d_en": "About 5 seconds",
            "correct_answer": "C",
            "explanation_no": "Ved 80 km/t bør du ha minst 3 sekunders avstand til bilen foran. Det tilsvarer ca. 65 meter.",
            "explanation_th": "ที่ 80 กม./ชม. คุณควรมีระยะห่างอย่างน้อย 3 วินาทีจากรถคันหน้า เท่ากับประมาณ 65 เมตร",
            "explanation_en": "At 80 km/h you should have at least 3 seconds distance to the car in front. That's about 65 meters.",
            "category": "Safety",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva bør du gjøre ved aquaplaning?",
            "question_text_th": "คุณควรทำอะไรเมื่อรถลื่นไถลบนน้ำ?",
            "question_text_en": "What should you do during aquaplaning?",
            "answer_a_no": "Bremse hardt",
            "answer_b_no": "Svinge brått",
            "answer_c_no": "Slippe gasspedalen og holde rattet rett",
            "answer_d_no": "Øke farten",
            "answer_a_th": "เบรกอย่างแรง",
            "answer_b_th": "หักพวงมาลัยทันที",
            "answer_c_th": "ปล่อมคันเร่งและจับพวงมาลัยตรง",
            "answer_d_th": "เร่งความเร็ว",
            "answer_a_en": "Brake hard",
            "answer_b_en": "Swerve sharply",
            "answer_c_en": "Release the gas and keep the wheel straight",
            "answer_d_en": "Increase speed",
            "correct_answer": "C",
            "explanation_no": "Ved aquaplaning skal du slippe gasspedalen forsiktig og holde rattet rett til du får kontroll igjen.",
            "explanation_th": "เมื่อรถลื่นไถลบนน้ำ ให้ปล่อยคันเร่งอย่างนุ่มนวลและจับพวงมาลัยตรงจนกว่าจะควบคุมรถได้",
            "explanation_en": "During aquaplaning, gently release the gas and keep the wheel straight until you regain control.",
            "category": "Safety",
            "difficulty": "hard"
        },
        {
            "question_text_no": "Hva er viktig ved kjøring i mørke?",
            "question_text_th": "สิ่งที่สำคัญเมื่อขับรถในที่มืดคืออะไร?",
            "question_text_en": "What is important when driving in the dark?",
            "answer_a_no": "Kjøre raskere for å komme hjem fortere",
            "answer_b_no": "Redusere farten og øke oppmerksomheten",
            "answer_c_no": "Bruke bare parkeringslys",
            "answer_d_no": "Følge bilen foran tett",
            "answer_a_th": "ขับเร็วขึ้นเพื่อกลับบ้านเร็วขึ้น",
            "answer_b_th": "ลดความเร็วและเพิ่มความระมัดระวัง",
            "answer_c_th": "ใช้แค่ไฟจอดรถ",
            "answer_d_th": "ขับตามรถคันหน้าอย่างใกล้ชิด",
            "answer_a_en": "Drive faster to get home sooner",
            "answer_b_en": "Reduce speed and increase attention",
            "answer_c_en": "Use only parking lights",
            "answer_d_en": "Follow the car ahead closely",
            "correct_answer": "B",
            "explanation_no": "I mørke er det viktig å redusere farten, øke oppmerksomheten og bruke riktige lys.",
            "explanation_th": "ในที่มืด สิ่งสำคัญคือลดความเร็ว เพิ่มความระมัดระวัง และใช้ไฟที่ถูกต้อง",
            "explanation_en": "In the dark, it's important to reduce speed, increase attention and use the correct lights.",
            "category": "Safety",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er reglene for barnesikring i bil?",
            "question_text_th": "กฎการใช้ที่นั่งเด็กในรถยนต์คืออะไร?",
            "question_text_en": "What are the rules for child safety seats in cars?",
            "answer_a_no": "Barn under 135 cm må bruke godkjent barnesete",
            "answer_b_no": "Bare barn under 3 år trenger barnesete",
            "answer_c_no": "Barnesete er valgfritt",
            "answer_d_no": "Bare i forsetet",
            "answer_a_th": "เด็กที่สูงต่ำกว่า 135 ซม. ต้องใช้ที่นั่งเด็กที่ได้รับอนุมัติ",
            "answer_b_th": "เฉพาะเด็กอายุต่ำกว่า 3 ปีเท่านั้น",
            "answer_c_th": "ที่นั่งเด็กเป็นทางเลือก",
            "answer_d_th": "เฉพาะเบาะหน้า",
            "answer_a_en": "Children under 135 cm must use approved child seat",
            "answer_b_en": "Only children under 3 need a child seat",
            "answer_c_en": "Child seats are optional",
            "answer_d_en": "Only in the front seat",
            "correct_answer": "A",
            "explanation_no": "Barn under 135 cm høyde må bruke godkjent barnesete tilpasset barnets størrelse og vekt.",
            "explanation_th": "เด็กที่สูงต่ำกว่า 135 ซม. ต้องใช้ที่นั่งเด็กที่ได้รับอนุมัติตามขนาดและน้ำหนักของเด็ก",
            "explanation_en": "Children under 135 cm height must use an approved child seat appropriate for their size and weight.",
            "category": "Safety",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hva er nødnummeret i Norge?",
            "question_text_th": "หมายเลขฉุกเฉินในนอร์เวย์คืออะไร?",
            "question_text_en": "What is the emergency number in Norway?",
            "answer_a_no": "110 - Brann, 112 - Politi, 113 - Ambulanse",
            "answer_b_no": "911",
            "answer_c_no": "999",
            "answer_d_no": "112 for alt",
            "answer_a_th": "110 - ดับเพลิง, 112 - ตำรวจ, 113 - รถพยาบาล",
            "answer_b_th": "911",
            "answer_c_th": "999",
            "answer_d_th": "112 สำหรับทุกอย่าง",
            "answer_a_en": "110 - Fire, 112 - Police, 113 - Ambulance",
            "answer_b_en": "911",
            "answer_c_en": "999",
            "answer_d_en": "112 for everything",
            "correct_answer": "A",
            "explanation_no": "I Norge er nødnumrene 110 for brann, 112 for politi og 113 for ambulanse.",
            "explanation_th": "ในนอร์เวย์ หมายเลขฉุกเฉินคือ 110 สำหรับดับเพลิง 112 สำหรับตำรวจ และ 113 สำหรับรถพยาบาล",
            "explanation_en": "In Norway, the emergency numbers are 110 for fire, 112 for police and 113 for ambulance.",
            "category": "Safety",
            "difficulty": "easy"
        },
        {
            "question_text_no": "Hva er den viktigste regelen ved kjøring i glatte veier?",
            "question_text_th": "กฎที่สำคัญที่สุดเมื่อขับรถบนถนนลื่นคืออะไร?",
            "question_text_en": "What is the most important rule when driving on slippery roads?",
            "answer_a_no": "Bruk piggdekk og kjør normalt",
            "answer_b_no": "Reduser farten og øk avstanden",
            "answer_c_no": "Brems hardt i svinger",
            "answer_d_no": "Kjør i midten av veien",
            "answer_a_th": "ใช้ยางตะปูและขับตามปกติ",
            "answer_b_th": "ลดความเร็วและเพิ่มระยะห่าง",
            "answer_c_th": "เบรกแรงในทางโค้ง",
            "answer_d_th": "ขับตรงกลางถนน",
            "answer_a_en": "Use studded tires and drive normally",
            "answer_b_en": "Reduce speed and increase distance",
            "answer_c_en": "Brake hard in curves",
            "answer_d_en": "Drive in the middle of the road",
            "correct_answer": "B",
            "explanation_no": "På glatte veier er det viktigst å redusere farten og øke avstanden til bilen foran.",
            "explanation_th": "บนถนนลื่น สิ่งที่สำคัญที่สุดคือลดความเร็วและเพิ่มระยะห่างจากรถคันหน้า",
            "explanation_en": "On slippery roads, the most important thing is to reduce speed and increase distance to the car ahead.",
            "category": "Safety",
            "difficulty": "easy"
        },
    ]

    normalized_questions = []
    for q in sample_questions:
        qid = str(uuid.uuid4())
        created = datetime.now(timezone.utc).isoformat()
        norm = {
            "id": qid,
            "question": {
                "no": q.get("question_text_no", ""),
                "th": q.get("question_text_th", ""),
                "en": q.get("question_text_en", ""),
            },
            "options": [
                {"id": "A", "text": {"no": q.get("answer_a_no", ""), "th": q.get("answer_a_th", ""), "en": q.get("answer_a_en", "")}},
                {"id": "B", "text": {"no": q.get("answer_b_no", ""), "th": q.get("answer_b_th", ""), "en": q.get("answer_b_en", "")}},
                {"id": "C", "text": {"no": q.get("answer_c_no", ""), "th": q.get("answer_c_th", ""), "en": q.get("answer_c_en", "")}},
                {"id": "D", "text": {"no": q.get("answer_d_no", ""), "th": q.get("answer_d_th", ""), "en": q.get("answer_d_en", "")}},
            ],
            "correctOptionId": q.get("correct_answer", "A"),
            "explanation": {
                "no": q.get("explanation_no", ""),
                "th": q.get("explanation_th", ""),
                "en": q.get("explanation_en", ""),
            },
            "bildeUrl": q.get("image_url") or q.get("bildeUrl") or None,
            "category": q.get("category", ""),
            "difficulty": q.get("difficulty", "medium"),
            "active": q.get("active", True),
            "created_at": created,
        }
        normalized_questions.append(norm)

    await db.questions.insert_many(normalized_questions)
    return {"message": f"Seeded {len(normalized_questions)} questions", "seeded": True}

# ==================== ADMIN PANEL ENDPOINTS ====================

async def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Auth dependency that requires the JWT user to have is_admin=true in DB."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    email = payload.get("email")
    admin_entry = await db.admin_users.find_one({"email": email})
    if not admin_entry:
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


@api_router.get("/admin/questions")
async def admin_list_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    has_image: Optional[bool] = None,
    active: Optional[bool] = None,
    search: Optional[str] = None,
    verdict: Optional[str] = None,  # MATCH / MISMATCH
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    _: dict = Depends(require_admin),
):
    """Admin: list all questions with filters. Returns full content including bildeUrl."""
    query: dict = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty
    if active is True:
        # Include both active=true and missing/undefined (legacy = active)
        query["$and"] = [{"$or": [{"active": True}, {"active": {"$exists": False}}]}]
    elif active is False:
        query["active"] = False
    if has_image is True:
        query["bildeUrl"] = {"$exists": True, "$nin": [None, ""]}
    elif has_image is False:
        query["$or"] = [{"bildeUrl": {"$exists": False}}, {"bildeUrl": ""}, {"bildeUrl": None}]
    if verdict:
        query["audit_verdict"] = verdict
    if search:
        rx = {"$regex": search, "$options": "i"}
        query["$or"] = (query.get("$or") or []) + [
            {"question.no": rx},
            {"explanation.no": rx},
            {"id": rx},
        ]

    total = await db.questions.count_documents(query)
    # Exclude bildeUrl from list — too large for pagination performance.
    # The detail view loads bildeUrl via GET /admin/questions/{id}
    cursor = db.questions.find(
        query,
        {"_id": 0, "bildeUrl": 0, "bildeUrl_original_backup": 0}
    ).sort("created_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(limit)
    # Add lightweight has_image flag using a parallel count query
    ids = [q["id"] for q in items if "id" in q]
    img_ids = set()
    if ids:
        async for r in db.questions.find(
            {"id": {"$in": ids}, "bildeUrl": {"$exists": True, "$nin": [None, ""]}},
            {"_id": 0, "id": 1}
        ):
            img_ids.add(r["id"])
    for q in items:
        q["has_image"] = q.get("id") in img_ids
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@api_router.get("/admin/stats")
async def admin_stats(_: dict = Depends(require_admin)):
    """Admin: database overview statistics."""
    total = await db.questions.count_documents({"active": True})
    with_img = await db.questions.count_documents(
        {"active": True, "bildeUrl": {"$exists": True, "$nin": [None, ""]}}
    )
    by_cat_cursor = db.questions.aggregate([
        {"$match": {"active": True}},
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "with_image": {"$sum": {"$cond": [
                {"$and": [
                    {"$ne": [{"$ifNull": ["$bildeUrl", ""]}, ""]},
                    {"$ne": ["$bildeUrl", None]}
                ]}, 1, 0
            ]}}
        }},
        {"$sort": {"count": -1}},
    ])
    by_cat = [c async for c in by_cat_cursor]
    by_diff_cursor = db.questions.aggregate([
        {"$match": {"active": True}},
        {"$group": {"_id": "$difficulty", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ])
    by_diff = [d async for d in by_diff_cursor]
    coverage_pct = round(with_img / total * 100, 1) if total else 0
    return {
        "total": total,
        "with_image": with_img,
        "coverage_pct": coverage_pct,
        "by_category": by_cat,
        "by_difficulty": by_diff,
    }


@api_router.delete("/admin/questions/{question_id}")
async def admin_delete_question(question_id: str, _: dict = Depends(require_admin)):
    """Admin: soft-delete a question (set active=false)."""
    r = await db.questions.update_one({"id": question_id}, {"$set": {"active": False}})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"ok": True}


@api_router.delete("/admin/questions/{question_id}/permanent")
async def admin_permanently_delete_question(question_id: str, _: dict = Depends(require_admin)):
    """Admin: permanently delete a question from the database."""
    r = await db.questions.delete_one({"id": question_id})
    if r.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"ok": True, "id": question_id}


@api_router.post("/admin/questions")
async def admin_create_question(data: dict, _: dict = Depends(require_admin)):
    """Admin: create a new question from scratch. Returns the full created document."""
    # Validate required fields
    required = ["question", "options", "correctOptionId", "explanation", "category"]
    for k in required:
        if k not in data or data[k] in (None, ""):
            raise HTTPException(status_code=400, detail=f"Missing field: {k}")
    if not isinstance(data.get("options"), list) or len(data["options"]) != 4:
        raise HTTPException(status_code=400, detail="Exactly 4 options required")
    if data["correctOptionId"] not in ["A", "B", "C", "D"]:
        raise HTTPException(status_code=400, detail="correctOptionId must be A/B/C/D")

    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "question": data["question"],
        "options": data["options"],
        "correctOptionId": data["correctOptionId"],
        "explanation": data["explanation"],
        "category": data["category"],
        "difficulty": data.get("difficulty", "medium"),
        "bildeUrl": data.get("bildeUrl", ""),
        "active": data.get("active", True),
        "schema_version": 2,
        "created_at": now,
    }
    await db.questions.insert_one(doc)
    result = await db.questions.find_one({"id": doc["id"]}, {"_id": 0, "bildeUrl_original_backup": 0})
    return result


@api_router.patch("/admin/questions/{question_id}")
async def admin_update_question(
    question_id: str,
    patch: dict,
    _: dict = Depends(require_admin),
):
    """Admin: partial update of question fields."""
    patch.pop("_id", None)
    patch.pop("id", None)
    if not patch:
        raise HTTPException(status_code=400, detail="Empty patch")
    r = await db.questions.update_one({"id": question_id}, {"$set": patch})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="Question not found")
    q = await db.questions.find_one({"id": question_id}, {"_id": 0, "bildeUrl_original_backup": 0})
    return q


@api_router.post("/admin/questions/{question_id}/image")
async def admin_upload_image(
    question_id: str,
    file: UploadFile = File(...),
    _: dict = Depends(require_admin),
):
    """Admin: upload a new image for a question (stored as Base64 data URI in bildeUrl).
    Resizes to max 600px, JPEG quality 82, to keep DB payload small."""
    import base64
    import io
    try:
        from PIL import Image
    except ImportError:
        raise HTTPException(status_code=500, detail="Pillow not installed on server")

    # Size check (max 10 MB raw)
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB)")
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not decode image: {e}")

    if max(img.size) > 600:
        ratio = 600 / max(img.size)
        img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.LANCZOS)
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    data_uri = "data:image/jpeg;base64," + b64

    q = await db.questions.find_one({"id": question_id})
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    prev = q.get("bildeUrl", "")
    await db.questions.update_one(
        {"id": question_id},
        {"$set": {
            "bildeUrl": data_uri,
            "bildeUrl_original_backup": prev if prev else q.get("bildeUrl_original_backup"),
        }},
    )
    return {
        "ok": True,
        "id": question_id,
        "bildeUrl": data_uri,
        "size_kb": round(len(buf.getvalue()) / 1024, 1),
        "dimensions": list(img.size),
    }


@api_router.get("/admin/questions/{question_id}/thumbnail")
async def admin_question_thumbnail(question_id: str, token: Optional[str] = None):
    """Admin: return a tiny JPEG thumbnail of the question image. Auth via ?token= query param."""
    import base64, io
    from PIL import Image as PilImage
    from fastapi.responses import Response as FastResponse
    # Verify token
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    q = await db.questions.find_one({"id": question_id}, {"_id": 0, "bildeUrl": 1})
    if not q:
        raise HTTPException(status_code=404, detail="Not found")
    bilde = q.get("bildeUrl", "")
    if not bilde or len(bilde) < 10:
        raise HTTPException(status_code=404, detail="No image")
    # Strip data URI prefix
    if "," in bilde:
        bilde = bilde.split(",", 1)[1]
    try:
        img_bytes = base64.b64decode(bilde)
        img = PilImage.open(io.BytesIO(img_bytes)).convert("RGB")
        img.thumbnail((160, 120), PilImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=70)
        return FastResponse(content=buf.getvalue(), media_type="image/jpeg",
                            headers={"Cache-Control": "public, max-age=3600"})
    except Exception:
        raise HTTPException(status_code=500, detail="Image error")


@api_router.delete("/admin/questions/{question_id}/image")
async def admin_remove_image(question_id: str, _: dict = Depends(require_admin)):
    """Admin: remove the image (set bildeUrl to empty string)."""
    q = await db.questions.find_one({"id": question_id})
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    prev = q.get("bildeUrl", "")
    await db.questions.update_one(
        {"id": question_id},
        {"$set": {"bildeUrl": "", "bildeUrl_original_backup": prev}},
    )
    return {"ok": True, "id": question_id}


@api_router.post("/admin/questions/{question_id}/unsplash-suggestions")
async def unsplash_suggestions(question_id: str, _: dict = Depends(require_admin)):
    """Admin: generate 3 search queries from question content, fetch 1 image per query from Unsplash."""
    import httpx

    unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not unsplash_key:
        raise HTTPException(status_code=500, detail="UNSPLASH_ACCESS_KEY not configured")

    q = await db.questions.find_one({"id": question_id})
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    question_en = q.get("question", {}).get("en", "") or q.get("question", {}).get("no", "")
    category = q.get("category", "")

    # Category-based base queries
    category_map = {
        "Traffic Signs": ["traffic sign norway", "road sign warning", "highway sign"],
        "Road Rules": ["road rules driving norway", "traffic highway norway", "car driving road"],
        "Right of Way": ["intersection traffic norway", "crossroads cars", "roundabout norway"],
        "Speed Limits": ["speed limit road", "highway speed norway", "road speed sign"],
        "Safety": ["road safety driving", "car safety seatbelt", "traffic accident prevention"],
        "Driving Conditions": ["driving snow norway", "winter road icy", "wet road driving"],
        "Situations": ["traffic situation road", "car driving situation", "road junction cars"],
        "Pedestrians and Cyclists": ["pedestrian crossing road", "cyclist bike road", "crosswalk pedestrian"],
        "Vehicle Knowledge": ["car engine vehicle", "car maintenance check", "automobile vehicle parts"],
        "Environment and Economy": ["eco driving fuel", "electric car norway", "fuel efficient driving"],
    }
    base_queries = category_map.get(category, ["traffic road norway", "driving highway", "car road"])

    # Add a question-specific query from first meaningful words
    words = [w for w in question_en.split() if len(w) > 3][:3]
    if words:
        specific = " ".join(words) + " road"
        queries = [specific] + base_queries[:2]
    else:
        queries = base_queries[:3]

    # Fetch 1 image per query from Unsplash
    suggestions = []
    async with httpx.AsyncClient(timeout=15) as client:
        for query in queries[:3]:
            r = await client.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": 1, "orientation": "landscape", "content_filter": "high"},
                headers={"Authorization": f"Client-ID {unsplash_key}"}
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    photo = results[0]
                    suggestions.append({
                        "query": query,
                        "thumb": photo["urls"]["small"],
                        "regular": photo["urls"]["regular"],
                        "photographer": photo.get("user", {}).get("name", "Unknown"),
                    })

    if not suggestions:
        raise HTTPException(status_code=404, detail="No images found")

    return {"suggestions": suggestions}


class UnsplashSaveRequest(BaseModel):
    url: str
    photographer: str = ""

@api_router.post("/admin/questions/{question_id}/fetch-unsplash")
async def fetch_unsplash_image(question_id: str, body: UnsplashSaveRequest, _: dict = Depends(require_admin)):
    """Admin: download selected Unsplash image URL and save as base64 in DB."""
    import httpx, base64 as _b64

    q = await db.questions.find_one({"id": question_id})
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    async with httpx.AsyncClient(timeout=30) as client:
        img_r = await client.get(body.url)

    if img_r.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to download image")

    img_b64 = _b64.b64encode(img_r.content).decode()
    bilde_url = f"data:image/jpeg;base64,{img_b64}"
    size_kb = len(img_r.content) // 1024

    await db.questions.update_one(
        {"id": question_id},
        {"$set": {"bildeUrl": bilde_url, "unsplash_photographer": body.photographer}}
    )
    return {"bildeUrl": bilde_url, "size_kb": size_kb, "photographer": body.photographer}


@api_router.post("/admin/questions/{question_id}/audit")
async def admin_audit_question(question_id: str, _: dict = Depends(require_admin)):
    """Admin: re-run AI Vision audit on the question's current image+text.
    Updates audit_verdict and audit_image_identification in DB."""
    q = await db.questions.find_one({"id": question_id}, {"_id": 0, "bildeUrl_original_backup": 0})
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    bilde = q.get("bildeUrl", "")
    if not bilde.startswith("data:"):
        raise HTTPException(status_code=400, detail="Question has no image to audit")

    # Bilderevisjon krever en modell som kan LESE bilder. DeepSeek-chat er tekst-only,
    # så dette endepunktet kan ikke bruke samme motor som Michael-chatten.
    # Rekkefølge: OpenAI (gpt-4o) → Anthropic (sonnet) → tydelig feilmelding.
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    vision_model = os.environ.get("VISION_LLM_MODEL", "gpt-4o")
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        vision_model = os.environ.get("VISION_LLM_MODEL", "claude-sonnet-4-20250514")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "Bilderevisjon krever en vision-modell. Sett OPENAI_API_KEY (gpt-4o) "
                "eller ANTHROPIC_API_KEY — DeepSeek-chat kan ikke lese bilder."
            ),
        )

    import json as _json
    system_prompt = """You are a Norwegian driving theory expert auditing quiz content.

Given an IMAGE and the current QUESTION+OPTIONS+CORRECT answer+EXPLANATION, verify they match.

Return ONLY strict JSON:
{
  "image_identification": "short Norwegian description (with sign number if any)",
  "verdict": "MATCH" | "MISMATCH" | "UNCERTAIN",
  "issues": ["list of problems if not MATCH, empty list otherwise"]
}"""

    opts_text = "\n".join([f"  {o['id']}. {o.get('text', {}).get('no', '')}" for o in q.get("options", [])])
    prompt = (
        f"QUESTION (NO): {q.get('question', {}).get('no', '')}\n"
        f"OPTIONS:\n{opts_text}\n"
        f"MARKED CORRECT: {q.get('correctOptionId')}\n"
        f"EXPLANATION (NO): {q.get('explanation', {}).get('no', '')}"
    )

    # Strip data URI prefix
    b64 = bilde
    if b64.startswith("data:"):
        comma = b64.find(",")
        if comma >= 0:
            b64 = b64[comma + 1:]

    try:
        import litellm
    except ImportError:
        raise HTTPException(status_code=500, detail="litellm not installed")

    try:
        raw = await litellm.acompletion(
            model=vision_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]}
            ],
            max_tokens=600,
            api_key=api_key,
        )
        text = (raw.choices[0].message.content or "").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI audit failed: {e}")
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    s, e = text.find("{"), text.rfind("}")
    try:
        parsed = _json.loads(text[s:e + 1])
    except Exception:
        parsed = {"verdict": "UNCERTAIN", "image_identification": text[:200], "issues": ["Could not parse AI response"]}

    await db.questions.update_one(
        {"id": question_id},
        {"$set": {
            "audit_verdict": parsed.get("verdict"),
            "audit_image_identification": parsed.get("image_identification"),
            "audit_issues": parsed.get("issues", []),
            "audit_ran_at": datetime.now(timezone.utc).isoformat(),
        }},
    )
    return parsed


# ═══════════════════════════════════════════════════════════
#  BOOK ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════

@api_router.get("/admin/book/sections")
async def admin_book_list(_: dict = Depends(require_admin)):
    """All sections sorted by chapter + section number."""
    sections = await db.chapters.find(
        {}, {"_id": 0, "image": 0}  # exclude heavy image blob from list
    ).sort([("chapter_num", 1), ("section_num", 1)]).to_list(400)
    return sections


@api_router.patch("/admin/book/sections/{section_id}")
async def admin_book_update(section_id: str, data: dict, _: dict = Depends(require_admin)):
    """Update title and/or content of a section."""
    allowed = {"section_title", "content"}
    update = {k: v for k, v in data.items() if k in allowed}
    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")
    await db.chapters.update_one({"id": section_id}, {"$set": update})
    return {"ok": True}


@api_router.post("/admin/book/sections/{section_id}/image")
async def admin_book_upload_image(
    section_id: str,
    file: UploadFile = File(...),
    _: dict = Depends(require_admin),
):
    """Upload / replace image for a book section."""
    import base64, io as _io
    try:
        from PIL import Image as _Img
    except ImportError:
        raise HTTPException(status_code=500, detail="Pillow not installed")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Max 15 MB")

    img = _Img.open(_io.BytesIO(raw))
    img.load()
    if img.mode in ("RGBA", "P", "LA"):
        bg = _Img.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > 900:
        r = 900 / img.width
        img = img.resize((900, int(img.height * r)), _Img.LANCZOS)

    buf = _io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    sec = await db.chapters.find_one({"id": section_id})
    if not sec:
        raise HTTPException(status_code=404, detail="Section not found")
    await db.chapters.update_one({"id": section_id}, {"$set": {"image": data_uri}})
    return {"ok": True, "size_kb": round(len(buf.getvalue()) / 1024, 1)}


@api_router.delete("/admin/book/sections/{section_id}/image")
async def admin_book_remove_image(section_id: str, _: dict = Depends(require_admin)):
    await db.chapters.update_one({"id": section_id}, {"$unset": {"image": ""}})
    return {"ok": True}


@api_router.delete("/admin/book/sections/{section_id}")
async def admin_book_delete_section(section_id: str, _: dict = Depends(require_admin)):
    r = await db.chapters.delete_one({"id": section_id})
    if r.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Section not found")
    return {"ok": True}


class BookSectionCreate(BaseModel):
    chapter_num: int
    section_title: dict   # {no, th, en}
    content: dict         # {no, th, en}


@api_router.post("/admin/book/sections")
async def admin_book_create_section(data: BookSectionCreate, _: dict = Depends(require_admin)):
    """Add a new section to a chapter."""
    import uuid as _uuid
    chapter = await db.chapters.find_one({"chapter_num": data.chapter_num})
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Get chapter title from existing section
    ch_title = chapter.get("chapter_title", {"no": "", "th": "", "en": ""})

    # Next section number
    last = await db.chapters.find_one(
        {"chapter_num": data.chapter_num}, sort=[("section_num", -1)]
    )
    next_num = (last["section_num"] + 1) if last else 1

    doc = {
        "id": str(_uuid.uuid4()),
        "chapter_num": data.chapter_num,
        "chapter_title": ch_title,
        "section_num": next_num,
        "section_title": data.section_title,
        "content": data.content,
        "slides": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.chapters.insert_one(doc)
    return {"ok": True, "id": doc["id"], "section_num": next_num}


# ═══════════════════════════════════════════════════════════
#  STUDIEBOK ENDPOINTS
# ═══════════════════════════════════════════════════════════

class StudiebokUpdate(BaseModel):
    title_no: Optional[str] = None
    content_no: Optional[str] = None
    title_th: Optional[str] = None
    content_th: Optional[str] = None
    title_en: Optional[str] = None
    content_en: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    icon: Optional[str] = None


class StudiebokCreate(BaseModel):
    order: int
    icon: str = "📄"
    title_no: str
    content_no: str
    title_th: Optional[str] = ""
    content_th: Optional[str] = ""
    title_en: Optional[str] = ""
    content_en: Optional[str] = ""
    image_url: Optional[str] = ""
    video_url: Optional[str] = ""


@api_router.get("/studiebok")
async def get_studiebok():
    """Return all Studiebok chapters sorted by order."""
    chapters = await db.studiebok_chapters.find(
        {}, {"_id": 0}
    ).sort("order", 1).to_list(200)
    return chapters


@api_router.post("/studiebok")
async def create_studiebok_chapter(
    data: StudiebokCreate,
    _: dict = Depends(require_admin),
):
    """Create a new Studiebok chapter (admin only)."""
    existing = await db.studiebok_chapters.find_one({"order": data.order})
    if existing:
        raise HTTPException(status_code=400, detail=f"Chapter with order {data.order} already exists")
    from datetime import datetime, timezone
    doc = {
        "order": data.order,
        "icon": data.icon,
        "title_no": data.title_no,
        "content_no": data.content_no,
        "title_th": data.title_th or "",
        "content_th": data.content_th or "",
        "title_en": data.title_en or "",
        "content_en": data.content_en or "",
        "image_url": data.image_url or "",
        "video_url": data.video_url or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.studiebok_chapters.insert_one(doc)
    return {"ok": True}


@api_router.put("/studiebok/{order}")
async def update_studiebok_chapter(
    order: int,
    data: StudiebokUpdate,
    _: dict = Depends(require_admin),
):
    """Update a chapter (admin only)."""
    update = {}
    if data.title_no is not None:
        update["title_no"] = data.title_no
    if data.content_no is not None:
        update["content_no"] = data.content_no
    if data.title_th is not None:
        update["title_th"] = data.title_th
    if data.content_th is not None:
        update["content_th"] = data.content_th
    if data.title_en is not None:
        update["title_en"] = data.title_en
    if data.content_en is not None:
        update["content_en"] = data.content_en
    if data.image_url is not None:
        update["image_url"] = data.image_url
    if data.video_url is not None:
        update["video_url"] = data.video_url
    if data.icon is not None:
        update["icon"] = data.icon
    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")
    result = await db.studiebok_chapters.update_one({"order": order}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"ok": True}



@api_router.post("/admin/studiebok/{order}/image")
async def admin_studiebok_upload_image(
    order: int,
    file: UploadFile = File(...),
    _: dict = Depends(require_admin),
):
    """Upload / replace image for a Studiebok chapter (stored as base64 data-URI)."""
    import base64 as _b64, io as _io
    try:
        from PIL import Image as _Img
    except ImportError:
        raise HTTPException(status_code=500, detail="Pillow not installed")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Max 15 MB")

    img = _Img.open(_io.BytesIO(raw))
    img.load()
    if img.mode in ("RGBA", "P", "LA"):
        bg = _Img.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > 1200:
        r = 1200 / img.width
        img = img.resize((1200, int(img.height * r)), _Img.LANCZOS)

    buf = _io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    data_uri = "data:image/jpeg;base64," + _b64.b64encode(buf.getvalue()).decode()

    result = await db.studiebok_chapters.update_one(
        {"order": order}, {"$set": {"image_url": data_uri}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"ok": True, "size_kb": round(len(buf.getvalue()) / 1024, 1)}


@api_router.delete("/admin/studiebok/{order}/image")
async def admin_studiebok_remove_image(order: int, _: dict = Depends(require_admin)):
    """Remove image from a Studiebok chapter."""
    await db.studiebok_chapters.update_one({"order": order}, {"$unset": {"image_url": ""}})
    return {"ok": True}


@api_router.delete("/studiebok/{order}")
async def delete_studiebok_chapter(
    order: int,
    _: dict = Depends(require_admin),
):
    """Delete a Studiebok chapter (admin only)."""
    result = await db.studiebok_chapters.delete_one({"order": order})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"ok": True}


# ═══════════════════════════════════════════════════════════
#  TRAFFIC SIGNS ENDPOINTS
# ═══════════════════════════════════════════════════════════

SIGN_GROUPS = {
    1: {"no": "Vikepliktskilt",   "th": "ป้ายให้ทาง",         "en": "Yield signs"},
    2: {"no": "Fareskilt",        "th": "ป้ายเตือน",           "en": "Warning signs"},
    3: {"no": "Forbudtskilt",     "th": "ป้ายห้าม",            "en": "Prohibition signs"},
    4: {"no": "Påbudsskilt",      "th": "ป้ายบังคับ",          "en": "Mandatory signs"},
    5: {"no": "Opplysningsskilt", "th": "ป้ายแจ้ง",            "en": "Information signs"},
    6: {"no": "Serviceskilt",     "th": "ป้ายบริการ",          "en": "Service signs"},
    7: {"no": "Veivisningsskilt", "th": "ป้ายนำทาง",           "en": "Direction signs"},
    8: {"no": "Underskilt",       "th": "ป้ายเสริม",           "en": "Supplementary signs"},
    9: {"no": "Markeringsskilt",  "th": "ป้ายเครื่องหมาย",     "en": "Road marking signs"},
}


# ==================== LEARNING VIDEOS ====================

def _extract_youtube_id(url: str) -> str:
    """Extract 11-char video ID from any youtube.com / youtu.be URL."""
    import re as _re
    for pat in [
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]:
        m = _re.search(pat, url)
        if m:
            return m.group(1)
    return ''


class LearningVideoCreate(BaseModel):
    """A short contextual learning video linked to topics, signs, or curriculum sections.

    Surface points
    ──────────────
    • After a wrong quiz answer — matched via topic_tags (→ _dangerLabel())
    • In the sign detail panel  — matched via sign_ids or sign_groups
    • In Studybook chapters     — matched via studybook_section_ids
    • In mistake-review mode    — matched via topic_tags from wrong answers
    • In Daily Mini Lesson      — curated selection

    Topic tags MUST exactly match the labels returned by the frontend _dangerLabel() function:
    'Bremsing'        — nødbrems / abs / bremsebane
    'Reaksjonstid'    — reaksjonstid / reaksjonsavstand
    'Avstand og tid'  — avstand / følgeavstand / 3-sekunder
    'Vikeplikt'       — vikeplikt / forkjørsrett
    'Myke trafikanter'— gangfelt / fotgjenger / syklist
    'Vinterforhold'   — glatt / is / snø / slipperisk
    'Sikt og fart'    — uoversiktlig / begrenset sikt / kurve / blind
    'Tretthet'        — tretthet / trøtt / søvn
    'Rundkjøring'     — rundkjøring
    'Alkohol'         — promille / alkohol
    'Lysbruk'         — lys / belysning / nærlys / langt lys
    'Fartsgrense'     — fartsgrense / hastighet / km/t
    'Forbikjøring'    — forbikjøring
    'Møtende trafikk' — møtende / tunnel
    (no match → 'Forstå situasjonen' — no video shown)
    """
    title_no: str = ""
    title_th: str = ""
    title_en: str = ""
    youtube_url: str
    thumbnail_url: str = ""          # auto-derived from youtube_url if empty
    duration_seconds: int = 0
    language: str = "no"             # primary language: no, th, en

    # ── Matching ───────────────────────────────────────────────────────────────
    topic_tags: List[str] = []       # danger-label strings from _dangerLabel()
    sign_ids: List[str] = []         # specific traffic sign IDs
    sign_groups: List[str] = []      # sign group names: "Fareskilt", "Forbudsskilt" etc.
    studybook_section_ids: List[str] = []  # curriculum refs e.g. "1.2.b"

    # ── Se → Forstå → Velg context ────────────────────────────────────────────
    see_context: str = ""
    understand_context: str = ""
    choose_context: str = ""

    # ── Instructor summary (shown under the card) ──────────────────────────────
    instructor_summary_no: str = ""
    instructor_summary_th: str = ""
    instructor_summary_en: str = ""

    active: bool = True


def _serialize_video(v: dict) -> dict:
    """Normalize a MongoDB video document for the API response."""
    v = {k: val for k, val in v.items() if k != '_id'}
    if not v.get('thumbnail_url'):
        if v.get('youtube_url'):
            yt_id = _extract_youtube_id(v['youtube_url'])
            if yt_id:
                v['thumbnail_url'] = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
        elif v.get('file_path'):
            # Derive a local thumbnail from the video filename
            fname = v['file_path'].rsplit('/', 1)[-1]  # video_xxx.mp4
            stem = fname.rsplit('.', 1)[0]  # video_xxx
            v['thumbnail_url'] = f"/api/assets/thumbs/thumb_{stem}.jpg"
    return v


# ── Public read endpoints ──────────────────────────────────────────────────────

@api_router.get("/videos/for-topic")
async def videos_for_topic(tags: str = "", limit: int = Query(default=50, le=50)):
    """Suggest learning videos by topic tag(s).
    tags: comma-separated labels from the _dangerLabel() frontend function.
    Returns up to `limit` videos ranked by first matching tag.
    """
    if not tags.strip():
        query = {"active": True}
    else:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        query = {"active": True, "topic_tags": {"$in": tag_list}}

    results = await db.learning_videos.find(query).limit(limit).to_list(limit)
    return [_serialize_video(r) for r in results]


@api_router.get("/videos/for-sign/{sign_id}")
async def videos_for_sign(sign_id: str, group: str = "", limit: int = Query(default=1, le=2)):
    """Suggest learning videos for a specific traffic sign.
    Falls back to matching by sign_groups if no direct sign_id match.
    """
    query: Dict[str, Any] = {"active": True}
    # Try exact sign_id first
    results = await db.learning_videos.find(
        {**query, "sign_ids": sign_id}
    ).limit(limit).to_list(limit)
    # Fall back to sign_groups
    if not results and group:
        results = await db.learning_videos.find(
            {**query, "sign_groups": group}
        ).limit(limit).to_list(limit)
    return [_serialize_video(r) for r in results]


# ── Admin CRUD ─────────────────────────────────────────────────────────────────

@api_router.get("/admin/videos")
async def admin_list_videos(_: dict = Depends(require_admin)):
    """List all learning videos (active and inactive)."""
    results = await db.learning_videos.find({}).sort("created_at", -1).to_list(500)
    return [_serialize_video(r) for r in results]


@api_router.post("/admin/videos")
async def admin_create_video(data: dict, _: dict = Depends(require_admin)):
    """Create a new learning video. thumbnail_url is auto-derived if omitted."""
    video = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
        # defaults
        "title_no": "", "title_th": "", "title_en": "",
        "youtube_url": "", "thumbnail_url": "", "duration_seconds": 0,
        "language": "no",
        "topic_tags": [], "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "see_context": "", "understand_context": "", "choose_context": "",
        "instructor_summary_no": "", "instructor_summary_th": "", "instructor_summary_en": "",
        **data,
    }
    if not video.get('thumbnail_url') and video.get('youtube_url'):
        yt_id = _extract_youtube_id(video['youtube_url'])
        if yt_id:
            video['thumbnail_url'] = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
    await db.learning_videos.insert_one(video)
    return _serialize_video(video)


@api_router.patch("/admin/videos/{video_id}")
async def admin_update_video(video_id: str, data: dict, _: dict = Depends(require_admin)):
    """Update fields on a learning video."""
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    # Auto-update thumbnail if youtube_url changed and thumbnail not provided
    if 'youtube_url' in data and not data.get('thumbnail_url'):
        yt_id = _extract_youtube_id(data['youtube_url'])
        if yt_id:
            data['thumbnail_url'] = f"https://img.youtube.com/vi/{yt_id}/mqdefault.jpg"
    result = await db.learning_videos.update_one({"id": video_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": "Updated", "id": video_id}


@api_router.delete("/admin/videos/{video_id}")
async def admin_delete_video(video_id: str, _: dict = Depends(require_admin)):
    """Permanently delete a learning video."""
    result = await db.learning_videos.delete_one({"id": video_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": "Deleted", "id": video_id}


# ── Podcasts ─────────────────────────────────────────────────────────────────

class LearningPodcastCreate(BaseModel):
    """A contextual audio podcast linked to topics or curriculum sections.

    Topic tags MUST exactly match the labels returned by the frontend _dangerLabel() function:
    (same tag list as LearningVideoCreate)
    """
    title_no: str = ""
    title_th: str = ""
    title_en: str = ""
    file_path: str               # e.g. /public_assets/podcast_xxx.mp3
    duration_seconds: int = 0
    language: str = "no"         # primary language: no, th, en

    topic_tags: List[str] = []
    sign_ids: List[str] = []
    sign_groups: List[str] = []
    studybook_section_ids: List[str] = []

    see_context: str = ""
    understand_context: str = ""
    choose_context: str = ""

    instructor_summary_no: str = ""
    instructor_summary_th: str = ""
    instructor_summary_en: str = ""

    active: bool = True


def _serialize_podcast(p: dict) -> dict:
    """Normalize a MongoDB podcast document for the API response."""
    return {k: val for k, val in p.items() if k != '_id'}


@api_router.get("/podcasts/for-topic")
async def podcasts_for_topic(tags: str = "", limit: int = Query(default=50, le=50)):
    """Suggest learning podcasts by topic tag(s)."""
    if not tags.strip():
        query = {"active": True}
    else:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        query = {"active": True, "topic_tags": {"$in": tag_list}}

    results = await db.learning_podcasts.find(query).limit(limit).to_list(limit)
    return [_serialize_podcast(r) for r in results]


# ── Admin CRUD (podcasts) ────────────────────────────────────────────────────

@api_router.get("/admin/podcasts")
async def admin_list_podcasts(_: dict = Depends(require_admin)):
    """List all learning podcasts (active and inactive)."""
    results = await db.learning_podcasts.find({}).sort("created_at", -1).to_list(500)
    return [_serialize_podcast(r) for r in results]


@api_router.post("/admin/podcasts")
async def admin_create_podcast(data: dict, _: dict = Depends(require_admin)):
    """Create a new learning podcast."""
    podcast = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
        # defaults
        "title_no": "", "title_th": "", "title_en": "",
        "file_path": "", "duration_seconds": 0,
        "language": "no",
        "topic_tags": [], "sign_ids": [], "sign_groups": [], "studybook_section_ids": [],
        "see_context": "", "understand_context": "", "choose_context": "",
        "instructor_summary_no": "", "instructor_summary_th": "", "instructor_summary_en": "",
        **data,
    }
    await db.learning_podcasts.insert_one(podcast)
    return _serialize_podcast(podcast)


@api_router.patch("/admin/podcasts/{podcast_id}")
async def admin_update_podcast(podcast_id: str, data: dict, _: dict = Depends(require_admin)):
    """Update fields on a learning podcast."""
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.learning_podcasts.update_one({"id": podcast_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return {"message": "Updated", "id": podcast_id}


@api_router.delete("/admin/podcasts/{podcast_id}")
async def admin_delete_podcast(podcast_id: str, _: dict = Depends(require_admin)):
    """Permanently delete a learning podcast."""
    result = await db.learning_podcasts.delete_one({"id": podcast_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return {"message": "Deleted", "id": podcast_id}


# ── Public podcast list ──────────────────────────────────────────────────────

@api_router.get("/learning-videos")
async def list_learning_videos(language: str = ""):
    """Return all active videos for the library screen, optionally filtered by language."""
    query = {"active": True}
    if language in ("no", "th", "en"):
        query["language"] = language
    results = await db.learning_videos.find(query).sort("title_no", 1).to_list(500)
    return [_serialize_video(r) for r in results]


@api_router.get("/learning-podcasts")
async def list_learning_podcasts(language: str = ""):
    """Return all active podcasts, optionally filtered by language (no/th/en)."""
    query = {"active": True}
    if language in ("no", "th", "en"):
        query["language"] = language
    results = await db.learning_podcasts.find(query).sort("title_no", 1).to_list(500)
    return [_serialize_podcast(r) for r in results]


# ── GridFS audio upload / stream ─────────────────────────────────────────────

@api_router.post("/admin/audio/upload")
async def admin_upload_audio(
    file: UploadFile = File(...),
    _: dict = Depends(require_admin),
):
    """Upload an audio/video file to MongoDB GridFS. Returns {file_id, url}."""
    MAX = 120 * 1024 * 1024  # 120 MB
    raw = await file.read()
    if len(raw) > MAX:
        raise HTTPException(status_code=413, detail="Max 120 MB")
    bucket = AsyncIOMotorGridFSBucket(db)
    import io as _io
    file_id = await bucket.upload_from_stream(
        file.filename or "audio",
        _io.BytesIO(raw),
        metadata={"content_type": file.content_type or "audio/mpeg"},
    )
    return {"file_id": str(file_id), "url": f"/api/audio/{str(file_id)}"}


@api_router.delete("/admin/audio/{file_id}")
async def admin_delete_audio(file_id: str, _: dict = Depends(require_admin)):
    """Delete an audio file from GridFS."""
    from bson import ObjectId
    try:
        oid = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file_id")
    bucket = AsyncIOMotorGridFSBucket(db)
    await bucket.delete(oid)
    return {"ok": True}


@api_router.get("/audio/{file_id}")
async def stream_audio(file_id: str, request: Request):
    """Stream audio from GridFS with HTTP 206 Range support."""
    from bson import ObjectId
    from starlette.responses import StreamingResponse
    try:
        oid = ObjectId(file_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file_id")

    bucket = AsyncIOMotorGridFSBucket(db)
    cursor = bucket.find({"_id": oid})
    docs = await cursor.to_list(1)
    if not docs:
        raise HTTPException(status_code=404, detail="Audio not found")

    doc = docs[0]
    total = doc.length
    ct = (doc.metadata or {}).get("content_type", "audio/mpeg")

    range_hdr = request.headers.get("Range", "")
    m = re.match(r"bytes=(\d+)-(\d*)", range_hdr)
    if m:
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else total - 1
        end = min(end, total - 1)
        length = end - start + 1
        grid_out = await bucket.open_download_stream(oid)
        await grid_out.seek(start)
        async def _range_gen():
            remaining = length
            while remaining > 0:
                chunk = await grid_out.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
        return StreamingResponse(
            _range_gen(), status_code=206,
            media_type=ct,
            headers={
                "Content-Range": f"bytes {start}-{end}/{total}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
            },
        )

    # Full stream
    grid_out = await bucket.open_download_stream(oid)
    async def _full_gen():
        while True:
            chunk = await grid_out.read(65536)
            if not chunk:
                break
            yield chunk
    return StreamingResponse(
        _full_gen(), media_type=ct,
        headers={"Content-Length": str(total), "Accept-Ranges": "bytes"},
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GLOSSARY — bilingual traffic-term dictionary (NO/TH/EN)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _serialize_glossary(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc


@api_router.get("/glossary")
async def get_glossary(lang: str = "no", search: str = ""):
    """Return all active glossary entries, optionally filtered by search string."""
    query: dict = {"active": True}
    if search.strip():
        search_clean = search.strip()
        query["$or"] = [
            {"term_no": {"$regex": search_clean, "$options": "i"}},
            {"term_th": {"$regex": search_clean, "$options": "i"}},
            {"term_en": {"$regex": search_clean, "$options": "i"}},
        ]
    results = await db.learning_glossary.find(query).sort("term_no", 1).to_list(200)
    return [_serialize_glossary(r) for r in results]


@api_router.get("/glossary/{term_id}")
async def get_glossary_term(term_id: str):
    doc = await db.learning_glossary.find_one({"id": term_id, "active": True})
    if not doc:
        raise HTTPException(status_code=404, detail="Term not found")
    return _serialize_glossary(doc)


@api_router.get("/admin/glossary")
async def admin_list_glossary(_: dict = Depends(require_admin)):
    results = await db.learning_glossary.find({}).sort("term_no", 1).to_list(500)
    return [_serialize_glossary(r) for r in results]


@api_router.post("/admin/glossary")
async def admin_create_glossary_term(data: dict, _: dict = Depends(require_admin)):
    term = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
        "term_no": "", "term_th": "", "term_en": "",
        "definition_no": "", "definition_th": "", "definition_en": "",
        "example_no": "", "example_th": "", "example_en": "",
        "topic_tags": [],
        **data,
    }
    await db.learning_glossary.insert_one(term)
    return _serialize_glossary(term)


@api_router.patch("/admin/glossary/{term_id}")
async def admin_update_glossary_term(term_id: str, data: dict, _: dict = Depends(require_admin)):
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.learning_glossary.update_one({"id": term_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Term not found")
    return {"message": "Updated", "id": term_id}


@api_router.delete("/admin/glossary/{term_id}")
async def admin_delete_glossary_term(term_id: str, _: dict = Depends(require_admin)):
    result = await db.learning_glossary.delete_one({"id": term_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Term not found")
    return {"message": "Deleted", "id": term_id}


class TrafficSignCreate(BaseModel):
    group: int
    name: Dict[str, str]           # {no, th, en}
    image_url: Optional[str] = ""
    group_desc: Optional[Dict[str, str]] = None
    order: Optional[int] = 1


class TrafficSignUpdate(BaseModel):
    group: Optional[int] = None
    name: Optional[Dict[str, str]] = None
    image_url: Optional[str] = None
    group_desc: Optional[Dict[str, str]] = None
    order: Optional[int] = None


@api_router.get("/traffic-signs")
async def get_traffic_signs():
    """Return all traffic signs grouped by group number."""
    signs = await db.traffic_signs.find({}, {"_id": 0}).sort([("group", 1), ("order", 1)]).to_list(1000)
    grouped: Dict[int, Any] = {}
    for g_num, g_info in SIGN_GROUPS.items():
        grouped[g_num] = {
            "group": g_num,
            "group_name": g_info,
            "signs": [],
        }
    for sign in signs:
        g = sign.get("group", 0)
        if g in grouped:
            grouped[g]["signs"].append(sign)
    return list(grouped.values())


@api_router.get("/traffic-signs/{group}")
async def get_traffic_signs_by_group(group: int):
    """Return signs for a specific group (1-9)."""
    if group not in SIGN_GROUPS:
        raise HTTPException(status_code=404, detail="Group not found")
    signs = await db.traffic_signs.find(
        {"group": group}, {"_id": 0}
    ).sort("order", 1).to_list(500)
    return {
        "group": group,
        "group_name": SIGN_GROUPS[group],
        "signs": signs,
    }


@api_router.post("/traffic-signs")
async def create_traffic_sign(data: TrafficSignCreate, _: dict = Depends(require_admin)):
    """Admin: add a traffic sign."""
    if data.group not in SIGN_GROUPS:
        raise HTTPException(status_code=400, detail="Invalid group (1-9)")
    doc = {
        "id": str(uuid.uuid4()),
        "group": data.group,
        "group_name": SIGN_GROUPS[data.group],
        "group_desc": data.group_desc or {},
        "name": data.name,
        "image_url": data.image_url or "",
        "order": data.order or 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.traffic_signs.insert_one(doc)
    return {"ok": True, "id": doc["id"]}


@api_router.put("/traffic-signs/{sign_id}")
async def update_traffic_sign(sign_id: str, data: TrafficSignUpdate, _: dict = Depends(require_admin)):
    """Admin: update a traffic sign."""
    update: dict = {}
    if data.group is not None:
        if data.group not in SIGN_GROUPS:
            raise HTTPException(status_code=400, detail="Invalid group (1-9)")
        update["group"] = data.group
        update["group_name"] = SIGN_GROUPS[data.group]
    if data.name is not None:
        update["name"] = data.name
    if data.image_url is not None:
        update["image_url"] = data.image_url
    if data.group_desc is not None:
        update["group_desc"] = data.group_desc
    if data.order is not None:
        update["order"] = data.order
    if not update:
        raise HTTPException(status_code=400, detail="Nothing to update")
    result = await db.traffic_signs.update_one({"id": sign_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sign not found")
    return {"ok": True}


@api_router.delete("/traffic-signs/{sign_id}")
async def delete_traffic_sign(sign_id: str, _: dict = Depends(require_admin)):
    """Admin: delete a traffic sign."""
    result = await db.traffic_signs.delete_one({"id": sign_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sign not found")
    return {"ok": True}


@api_router.post("/traffic-signs/{sign_id}/image")
async def upload_sign_image(
    sign_id: str,
    file: UploadFile = File(...),
    _: dict = Depends(require_admin),
):
    """Admin: upload an image for a traffic sign (stored as Base64 data URI in image_url)."""
    import base64
    import io
    try:
        from PIL import Image
    except ImportError:
        raise HTTPException(status_code=500, detail="Pillow not installed on server")

    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB)")
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not decode image: {e}")

    if max(img.size) > 600:
        ratio = 600 / max(img.size)
        img = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.LANCZOS)
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    data_uri = "data:image/jpeg;base64," + b64

    sign = await db.traffic_signs.find_one({"id": sign_id})
    if not sign:
        raise HTTPException(status_code=404, detail="Sign not found")
    await db.traffic_signs.update_one(
        {"id": sign_id},
        {"$set": {"image_url": data_uri}},
    )
    return {
        "ok": True,
        "id": sign_id,
        "image_url": data_uri,
        "size_kb": round(len(buf.getvalue()) / 1024, 1),
        "dimensions": list(img.size),
    }


app.include_router(api_router)

# ==================== PUBLIC WEBSITE (landing + legal) ====================
from website import website_router  # noqa: E402
app.include_router(website_router, prefix="")
app.include_router(website_router, prefix="/api")  # also serve under /api/* for Railway routing

# ==================== AI SUPPORT CHAT ====================
from support_chat import support_chat_router  # noqa: E402
app.include_router(support_chat_router, prefix="/api")

# ==================== MICHAEL TRAFIKKLÆRER ====================
from teacher_chat import teacher_router  # noqa: E402
app.include_router(teacher_router, prefix="/api")

# ==================== AI LEARNING ENGINE ====================
from ai_routes import ai_router  # noqa: E402
app.include_router(ai_router, prefix="/api")

# ==================== TRAFFIC MATH ENGINE ====================
from traffic_math_routes import math_router  # noqa: E402
app.include_router(math_router, prefix="/api")

# ==================== QUIZ PAGE ====================
from quiz_web import quiz_web_router  # noqa: E402
app.include_router(quiz_web_router, prefix="/api")

# ==================== WEB APP ====================
from webapp import webapp_router  # noqa: E402
app.include_router(webapp_router, prefix="/api")


# ==================== ADMIN HTML PAGE ====================
from fastapi.responses import HTMLResponse, FileResponse  # noqa: E402
from pathlib import Path as _Path  # noqa: E402

_ADMIN_HTML_PATH = _Path(__file__).resolve().parent / "admin.html"
_VOICE_TESTER_HTML_PATH = _Path(__file__).resolve().parent / "voice_tester.html"


@app.get("/api/admin/voice-tester", response_class=HTMLResponse)
async def voice_tester_page():
    if _VOICE_TESTER_HTML_PATH.exists():
        html = _VOICE_TESTER_HTML_PATH.read_text(encoding="utf-8")
        api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        html = html.replace("{{ELEVENLABS_API_KEY}}", api_key)
        html = html.replace("{{VOICE_ID}}", "IoOuTUO7t2kI2VTJqI10")
        return HTMLResponse(html)
    return HTMLResponse("<h1>Voice tester not installed</h1>", status_code=500)


@app.post("/api/admin/voice-test")
async def voice_test(data: dict):
    import httpx
    from fastapi import HTTPException
    from fastapi.responses import Response

    text = data.get("text", "")
    voice_id = data.get("voice_id", "")
    api_key = data.get("api_key", "")

    if not text or not voice_id or not api_key:
        raise HTTPException(status_code=400, detail="Mangler påkrevde felt")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=headers, timeout=60.0)
            if r.status_code == 200:
                return Response(content=r.content, media_type="audio/mpeg")
            else:
                logger.error("ElevenLabs tester error %d: %s", r.status_code, r.text)
                raise HTTPException(status_code=r.status_code, detail=f"ElevenLabs feil: {r.text}")
    except Exception as e:
        logger.error("ElevenLabs tester exception: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/page", response_class=HTMLResponse)
async def admin_page():
    if _ADMIN_HTML_PATH.exists():
        return HTMLResponse(_ADMIN_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Admin panel not installed</h1>", status_code=500)


# Also serve at /api/admin (without /page) for short URL
@app.get("/api/admin-panel", response_class=HTMLResponse)
async def admin_page_short():
    if _ADMIN_HTML_PATH.exists():
        return HTMLResponse(_ADMIN_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Admin panel not installed</h1>", status_code=500)


# Shorter aliases
@app.get("/api/admin", response_class=HTMLResponse)
async def admin_page_alias_admin():
    if _ADMIN_HTML_PATH.exists():
        return HTMLResponse(_ADMIN_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Admin panel not installed</h1>", status_code=500)


@app.get("/api/cms", response_class=HTMLResponse)
async def admin_page_alias_cms():
    if _ADMIN_HTML_PATH.exists():
        return HTMLResponse(_ADMIN_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Admin panel not installed</h1>", status_code=500)


# Catch-all for admin-panel with garbage suffixes (e.g. markdown copy-paste)
@app.get("/api/admin-panel/{rest:path}", response_class=HTMLResponse)
async def admin_page_catchall(rest: str):
    """Catch URL variations like /api/admin-panel](https://...) from markdown copy-paste."""
    if _ADMIN_HTML_PATH.exists():
        return HTMLResponse(_ADMIN_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Admin panel not installed</h1>", status_code=500)


# ─── Static public assets (icons, screenshots etc. for Play Store / press use) ───
_PUBLIC_ASSETS_DIR = Path(__file__).parent / "public_assets"


@app.get("/.well-known/assetlinks.json")
async def assetlinks():
    """Android App Links verification file."""
    from fastapi.responses import JSONResponse
    return JSONResponse(content=[{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "com.michael.thai2drive",
            "sha256_cert_fingerprints": [
                "DA:8B:0F:97:4D:5C:5A:BF:FF:D7:0C:71:6F:8B:82:A6:95:9F:48:8E:D9:CE:A5:32:F6:E9:24:ED:EA:53:9C:43"
            ]
        }
    }])


@app.get("/api/assets/{filename:path}")
async def public_asset(filename: str):
    """Serve static files from backend/public_assets/ (e.g. developer icon for Play Console)."""
    # Prevent path traversal
    safe_name = filename.replace("..", "").lstrip("/")
    file_path = (_PUBLIC_ASSETS_DIR / safe_name).resolve()
    try:
        file_path.relative_to(_PUBLIC_ASSETS_DIR.resolve())
    except ValueError:
        return HTMLResponse("Not found", status_code=404)
    if not file_path.exists() or not file_path.is_file():
        return HTMLResponse("Not found", status_code=404)

    # Simple content-type sniffing
    ext = file_path.suffix.lower()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".pdf": "application/pdf",
    }.get(ext, "application/octet-stream")

    return FileResponse(str(file_path), media_type=media_type)


# ── Sign images — served from backend/sign_images/ ────────────────────────────
_SIGN_IMAGES_DIR = Path(__file__).parent / "sign_images"

@app.get("/api/sign-images/{filename:path}")
async def sign_image(filename: str):
    """Serve traffic sign images from backend/sign_images/. Images are committed
    to the repo after running scripts/import_sign_images.py locally."""
    safe_name = filename.replace("..", "").lstrip("/")
    file_path = (_SIGN_IMAGES_DIR / safe_name).resolve()
    try:
        file_path.relative_to(_SIGN_IMAGES_DIR.resolve())
    except ValueError:
        return HTMLResponse("Not found", status_code=404)
    if not file_path.exists() or not file_path.is_file():
        return HTMLResponse("Not found", status_code=404)
    ext = file_path.suffix.lower()
    media_type = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(ext, "image/jpeg")
    return FileResponse(str(file_path), media_type=media_type)


# Middleware: redirect dirty /api/admin-panel URLs (with trailing quotes, markdown syntax, etc.)
from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402
from starlette.responses import RedirectResponse  # noqa: E402


class AdminUrlCleanupMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        # If path starts with /api/admin-panel but isn't exactly that (has garbage after), clean it
        if path.startswith("/api/admin-panel") and path not in ("/api/admin-panel", "/api/admin-panel/"):
            # e.g. /api/admin-panel%22 or /api/admin-panel](https...)
            # Redirect to the clean URL
            return RedirectResponse(url="/api/admin-panel", status_code=302)
        # Same cleanup for /api/admin and /api/cms
        for clean in ["/api/admin", "/api/cms"]:
            if path.startswith(clean) and path not in (clean, clean + "/") and not path.startswith(clean + "/"):
                # Only redirect if the extra characters aren't legit sub-paths (like /api/admin/questions)
                pass  # no-op, the main routes handle /api/admin/stats etc
        return await call_next(request)


app.add_middleware(AdminUrlCleanupMiddleware)


import time as _time  # noqa: E402


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Adds X-Response-Time-Ms header to every response.
    Logs a WARNING on Railway for any /api/* request that takes > 500 ms.
    Zero overhead on fast requests — perf_counter is nanosecond resolution.
    """
    _slow_logger = logging.getLogger("timing")

    async def dispatch(self, request, call_next):
        t0 = _time.perf_counter()
        response = await call_next(request)
        ms = (_time.perf_counter() - t0) * 1000
        response.headers["X-Response-Time-Ms"] = f"{ms:.0f}"
        if request.url.path.startswith("/api") and ms > 500:
            self._slow_logger.warning(
                "SLOW %s %s → %dms [status=%d]",
                request.method, request.url.path, ms, response.status_code,
            )
        return response


app.add_middleware(TimingMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "https://thai2drive.no",
        "https://www.thai2drive.no",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def seed_studiebok():
    """Auto-seed Studiebok chapters into MongoDB ONLY if collections are empty."""
    import uuid
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    CHAPTERS = [
        {"order":1,"icon":"⚖️","title_no":"Kapittel 1 — Grunnregler og Vegtrafikkloven","content_no":'<p><strong>Vegtrafikkloven</strong> er den viktigste loven som regulerer all trafikk i Norge. Her er de mest sentrale paragrafene du må kjenne til.</p>\n\n<div class="study-law"><strong>§ 1. Lovens område:</strong> Denne lov gjelder all trafikk med motorvogn. Den gjelder også annen ferdsel, men da bare på veg eller på område som har alminnelig trafikk med motorvogn.</div>\n\n<div class="study-law"><strong>§ 2. Definisjoner:</strong> Med <em>veg</em> forstås gate og plass, herunder opplagsplass, parkeringsplass, holdeplass, bru, ferjekai. Med <em>kjøretøy</em> forstås innretning som er bestemt til å kjøre på bakken uten skinner. Med <em>motorvogn</em> forstås kjøretøy som blir drevet fram med motor.</div>\n\n<div class="study-law"><strong>§ 3. Grunnregler for trafikk:</strong> Enhver skal ferdes <strong>hensynsfullt</strong> og være <strong>aktpågivende og varsom</strong> så det ikke kan oppstå fare eller voldes skade og slik at annen trafikk ikke unødig blir hindret eller forstyrret. Vegfarende skal også vise hensyn mot dem som bor eller oppholder seg ved vegen.</div>\n\n<div class="study-law"><strong>§ 4. Trafikkregler:</strong> Kongen gir alminnelige regler for kjørende, ridende og gående trafikk.</div>\n\n<div class="study-law"><strong>§ 5. Skiltregler:</strong> Enhver skal være oppmerksom på offentlig trafikkskilt, signal og oppmerking og skal rette seg etter de forbud og påbud som gis på denne måte.</div>\n\n<div class="study-tip"><strong>Tips:</strong> Grunnregelen i § 3 er den viktigste — den gjelder alltid, selv der det ikke finnes spesifikke regler. Husk: hensynsfull, aktpågivende og varsom.</div>\n\n<p>Reglene i trafikken er hierarkisk oppbygd. Du skal rette deg etter:</p>\n<ul>\n<li>Anvisninger fra politiet, Statens vegvesen, tollvesenet eller militærpolitiet (gjelder foran alt annet)</li>\n<li>Trafikklyssignal (gjelder foran skilt om vikeplikt)</li>\n<li>Offentlig trafikkskilt og vegoppmerking</li>\n<li>Trafikkreglene</li>\n</ul>\n\n<div class="study-law"><strong>§ 21. Alminnelige plikter:</strong> Ingen må føre eller forsøke å føre kjøretøy når han er i en slik tilstand at han ikke kan anses skikket til å kjøre på trygg måte, hva enten dette skyldes påvirkning av alkohol, sykdom, svekkelse, tretthet eller andre omstendigheter.</div>'},
        {"order":2,"icon":"🚗","title_no":"Kapittel 2 — Definisjoner og vegreferanser","content_no":'<p>For å forstå trafikkreglene er det viktig å kjenne til de offisielle definisjonene fra Trafikkreglenes § 1.</p>\n\n<div class="study-law"><strong>§ 1a) Veg:</strong> Offentlig eller privat veg, gate eller plass (herunder opplagsplass, parkeringsplass, holdeplass, bru, vinterveg, ferjekai eller annen kai som står i umiddelbar forbindelse med veg) som er åpen for alminnelig ferdsel.</div>\n\n<div class="study-law"><strong>§ 1b) Vegkryss:</strong> Sted hvor veg krysser eller munner ut i annen veg.</div>\n\n<div class="study-law"><strong>§ 1c) Kjørebane:</strong> Den del av vegen som er bestemt for vanlig kjøring.</div>\n\n<div class="study-law"><strong>§ 1d) Kjørefelt:</strong> Hvert enkelt av de langsgående felt som en kjørebane er delt i ved oppmerking, eller som er bredt nok for trafikk med en bilrekke.</div>\n\n<div class="study-law"><strong>§ 1e) Skulder:</strong> Den del av vegen som ligger utenfor kantlinjen.</div>\n\n<div class="study-law"><strong>§ 1f) Gangveg og sykkelveg:</strong> Veg som ved offentlig trafikkskilt er bestemt for gående, syklende eller kombinert gang- og sykkeltrafikk. Vegen er skilt fra annen veg med gressplen, grøft, gjerde, kantstein eller på annen måte.</div>\n\n<div class="study-law"><strong>§ 1g) Sykkelfelt:</strong> Kjørefelt som ved offentlig trafikkskilt og oppmerking er bestemt for syklende.</div>\n\n<div class="study-law"><strong>§ 1h) Fortau:</strong> Anlegg for gående som er skilt fra kjørebanen med kantstein.</div>\n\n<div class="study-law"><strong>§ 1j) Planovergang:</strong> Kryssing i samme plan mellom veg og jernbane eller sporveg på særskilt banelegeme.</div>\n\n<div class="study-law"><strong>§ 1k) Parkering:</strong> Enhver hensetting av kjøretøy, selv om føreren ikke forlater det. Unntatt er kortest mulig stans for av- eller påstigning eller av- eller pålessing.</div>\n\n<div class="study-tip"><strong>Tips:</strong> Legg merke til at parkering også gjelder når du sitter i bilen. Bare kortest mulig stans for av/påstigning regnes <em>ikke</em> som parkering.</div>\n\n<p>Trafikkreglenes § 2 presiserer hvem reglene gjelder for:</p>\n<ul>\n<li>All trafikk på veg</li>\n<li>Rytter og den som fører dyr</li>\n<li>Som <strong>gående</strong> regnes også den som: går på ski, fører rullestol, leier sykkel, triller barnevogn eller bruker lekekjøretøy</li>\n</ul>'},
        {"order":3,"icon":"🛣️","title_no":"Kapittel 3 — Plassering på vegen","content_no":'<p><strong>Riktig plassering</strong> på vegen bidrar til sikker og effektiv trafikkavvikling. Reglene finner du i Trafikkreglenes § 4 og § 5.</p>\n\n<div class="study-law"><strong>§ 4. Bruk av kjørebane:</strong> Kjørende skal bruke kjørebanen. Det er forbudt å kjøre på fortau eller gangveg. Andre kjørende enn syklende må ikke bruke sykkelveg eller sykkelfelt. På motorveg og motortrafikkveg må det bare foregå trafikk med motorvogn som lovlig kan kjøres med minst 40 km i timen. Moped må ikke kjøres på motorveg.</div>\n\n<div class="study-law"><strong>§ 5. Kjøretøys plass på vegen:</strong>\n<ul>\n<li>Så langt forholdene tillater det skal kjøretøy føres på <strong>høyre side av vegen</strong>.</li>\n<li>På kjørebane med to eller flere kjørefelt i kjøreretningen skal <strong>høyre felt nyttes</strong> når ikke trafikkreglene påbyr eller tillater bruk av felt til venstre.</li>\n<li>Kjøretøy må holdes godt innenfor kjørefeltet.</li>\n<li>Sykkel kan kjøres på vegens høyre skulder.</li>\n<li><strong>Avstand til forankjørende</strong> skal være så stor at det ikke oppstår fare for påkjøring dersom den forankjørende saktner farten eller stanser.</li>\n</ul>\n</div>\n\n<div class="study-law"><strong>§ 6. Svinging:</strong>\n<ul>\n<li>Sving til <strong>høyre</strong>: kjøres så nær høyre kant av kjørebanen som mulig</li>\n<li>Sving til <strong>venstre</strong>: kjøres så nær midten av kjørebanen som mulig</li>\n<li>På kjørebane med to eller flere kjørefelt skal du i god tid kjøre inn i riktig felt</li>\n<li>Kjøretøyer som kommer fra motsatte retninger, kan svinges til venstre for hverandre</li>\n</ul>\n</div>\n\n<div class="study-law"><strong>§ 8. Kjørefeltskifte:</strong> Kjørende som vil skifte kjørefelt, har vikeplikt for kjørende som befinner seg i det felt det skal kjøres inn i. Når antallet kjørefelt reduseres, skal farten tilpasses gjensidig slik at de kjørende vekselvis kan fortsette (glidelås-prinsippet).</div>\n\n<div class="study-tip"><strong>Tips:</strong> Plassering handler om å skape <em>sikkerhetssoner</em> rundt bilen din. God plassering gir deg og andre bedre tid til å reagere.</div>'},
        {"order":4,"icon":"🚦","title_no":"Kapittel 4 — Fart og fartsgrenser","content_no":'<p>Riktig fart er avgjørende for trafikksikkerheten. Vegtrafikkloven § 6 og Trafikkreglenes § 13 regulerer kjørefarten.</p>\n\n<div class="study-law"><strong>Vegtrafikkloven § 6. Fartsregler:</strong> Fører av kjøretøy skal avpasse farten etter <strong>sted, føre-, sikt- og trafikkforholdene</strong> slik at det ikke kan oppstå fare eller voldes ulempe for andre. Føreren skal alltid ha fullt herredømme over kjøretøyet.</div>\n\n<p><strong>Generelle fartsgrenser (uten skilt):</strong></p>\n<ul>\n<li>I <strong>tettbygd strøk</strong>: 50 km/t</li>\n<li>Utenfor <strong>tettbygd strøk</strong>: 80 km/t</li>\n</ul>\n\n<div class="study-law"><strong>Trafikkreglenes § 13. Særlige bestemmelser om kjørefarten:</strong>\n<ul>\n<li>Kjørende må kunne <strong>stanse på den vegstrekning</strong> som den kjørende har oversikt over, og foran enhver påregnelig hindring.</li>\n<li>Plikter å holde tilstrekkelig liten fart og stanse ved passering av: barn på vegen, skolepatrulje, person med hvit stokk eller førerhund, sporvogn/buss ved holdeplass.</li>\n<li>På gågate eller gatetun: ikke fortere enn i <strong>gangfart</strong></li>\n<li>Motorvogn over 3 500 kg eller med tilhenger: ikke fortere enn <strong>80 km/t</strong> der fartsgrensen er høyere</li>\n<li>Motorvogn med tilhenger uten bremser (tilhenger 300 kg+): ikke fortere enn <strong>60 km/t</strong></li>\n</ul>\n</div>\n\n<p><strong>Stoppelengder — sammenheng mellom fart og stoppavstand:</strong></p>\n<ul>\n<li>20 km/t: reaksjonslengde ca 5,5 m + bremselengde 2 m = ca 7,5 m totalt</li>\n<li>50 km/t: reaksjonslengde ca 14 m + bremselengde 12,5 m = ca 26,5 m totalt</li>\n<li>80 km/t: reaksjonslengde ca 22 m + bremselengde 32 m = ca 54 m totalt</li>\n<li>100 km/t: reaksjonslengde ca 27,8 m + bremselengde 50 m = ca 78 m totalt</li>\n</ul>\n\n<div class="study-tip"><strong>Tips:</strong> Stoppelengden øker med <em>kvadratet</em> av farten — dobler du farten, fire-dobler du bremselengden! Reaksjonstid er ca 1 sekund for en normalt oppmerksom fører.</div>\n\n<p><strong>Faktorer som påvirker riktig fart:</strong></p>\n<ul>\n<li>Siktforhold (mørke, tåke, regn, snø)</li>\n<li>Veiforhold (is, snø, våt asfalt)</li>\n<li>Trafikkmengde og type trafikanter</li>\n<li>Vegens utforming (kurver, bakketopper, kryss)</li>\n<li>Skiltet fartsgrense</li>\n</ul>'},
        {"order":5,"icon":"🔄","title_no":"Kapittel 5 — Vikeplikt og forkjørsrett","content_no":'<p><strong>Vikeplikt</strong> er regler som avgjør hvem som skal vente og hvem som kan kjøre. Disse reglene er grunnleggende for sikker trafikkavvikling.</p>\n\n<div class="study-law"><strong>Trafikkreglenes § 7. Vikeplikt:</strong>\n<ol>\n<li>Trafikant det skal vikes for, må ikke hindres eller forstyrres. Den som har vikeplikt, skal tydelig vise dette ved i god tid å sette ned farten eller stanse.</li>\n<li>Kjørende har <strong>vikeplikt for kjøretøy som kommer fra høyre</strong> (høyreregelen). Det samme gjelder når kjørende som vil svinge til venstre, vil få kjøretøy på sin høyre side.</li>\n<li>Kjørende som vil svinge, har vikeplikt for <strong>gående eller syklende</strong> der det skal kjøres inn.</li>\n<li>Kjørende som kommer fra parkeringsplass, holdeplass, torg, eiendom, bensinstasjon, gågate, gatetun eller liknende område har <strong>vikeplikt for annen trafikant</strong>. Det samme gjelder den som svinger inn fra skulder eller fra sykkelveg/gangveg/fortau.</li>\n<li>På veg med fartsgrense 60 km/t eller lavere: kjørende har vikeplikt for <strong>buss</strong> som skal forlate holdeplass (når bussjåfør gir tegn).</li>\n<li>Møtende trafikanter skal i god tid vike til høyre og kjøre sakte. Er en del sperret, har den vikeplikt som har sperringen på sin side.</li>\n</ol>\n</div>\n\n<div class="study-law"><strong>Trafikkreglenes § 9. Særlige plikter overfor gående:</strong>\n<ul>\n<li>Kjørende skal la gående få tilstrekkelig plass på vegen.</li>\n<li>Kjørende som krysser gangveg eller fortau, har vikeplikt for gående.</li>\n<li>Ved <strong>gangfelt</strong> (uten lys/politi): vikeplikt for gående som befinner seg i gangfeltet eller er på veg ut i det.</li>\n<li>Kjørende skal unngå stans på gangfelt.</li>\n</ul>\n</div>\n\n<div class="study-law"><strong>Trafikkreglenes § 10. Fri veg:</strong>\n<ul>\n<li>Trafikant skal gi fri veg for <strong>utrykningskjøretøy</strong> med blinkende blått lys.</li>\n<li>Trafikant skal gi fri veg for <strong>sporvogn og jernbanetog</strong>.</li>\n<li>Trafikant må ikke hindre gående i gruppe under tilsyn, prosesjon, begravelsesfølge, militær kjøretøykolonne.</li>\n</ul>\n</div>\n\n<div class="study-tip"><strong>Tips — Huskeregel for vikeplikt:</strong> Tenk HFGP: <em>Høyre</em> (høyreregelen), <em>Forkjørsveg</em> (skilt), <em>Gangfelt</em> (vikeplikt for gående), <em>Parkering/innkjøring</em> (alltid vikeplikt).</div>\n\n<p><strong>Prioriteringsrekkefølge i kryss:</strong></p>\n<ul>\n<li>Politiets anvisninger</li>\n<li>Trafikklyssignal</li>\n<li>Vikeplikt-/forkjørsskilt</li>\n<li>Høyreregelen (ingen av de ovennevnte)</li>\n</ul>'},
        {"order":6,"icon":"↩️","title_no":"Kapittel 6 — Forbikjøring, rygging og vending","content_no":'<p>Forbikjøring er en av de farligste manøvrene i trafikken. Det er viktig å kjenne reglene nøye.</p>\n\n<div class="study-law"><strong>Trafikkreglenes § 12. Forbikjøring:</strong>\n<ol>\n<li>Forbikjøring skal skje <strong>til venstre</strong>. Unntak: forankjørende svinger til venstre (da kjøres forbi til høyre); sporvogn kan forbikjøres til høyre; tett kø der alle felt er belagt.</li>\n<li>Før forbikjøring skal kjørende forvisse seg om at:\n<ul>\n<li>Vegen er fri for hindring på tilstrekkelig lang strekning framover</li>\n<li>Den forankjørende ikke har gitt tegn om forbikjøring</li>\n<li>Ingen bakenforkjørende har begynt å kjøre forbi</li>\n<li>Det lar seg gjøre å komme inn i trafikkstrømmen igjen uten å forstyrre den</li>\n</ul>\n</li>\n<li>Etter forbikjøring: svinge til høyre igjen uten å volde fare for den forbikjørte.</li>\n<li>Forankjørende skal holde til høyre og ikke øke farten under forbikjøring.</li>\n<li><strong>Forbikjøring er forbudt:</strong> like foran eller i vegkryss (med unntak), der sikten er hindret ved bakketopp, kurve eller på annen måte, nær gangfelt (ikke kjøre forbi kjøretøy som skjuler sikt til gangfelt).</li>\n</ol>\n</div>\n\n<div class="study-law"><strong>Trafikkreglenes § 11. Rygging og vending:</strong>\n<ul>\n<li>Den som rygger eller vender, har <strong>vikeplikt for annen trafikant</strong>.</li>\n<li>Er utsikten ikke tilstrekkelig, må det ikke foretas rygging/vending uten at en annen passer på.</li>\n<li>Rygging og vending er <strong>forbudt på motorveg</strong> og motortrafikkveg.</li>\n</ul>\n</div>\n\n<div class="study-tip"><strong>Tips:</strong> Forbikjøring krever STOR sikkerhetsmargin. Husk: du trenger plass til akselerasjon, passering og innsvinging — og motgående trafikk kan komme i høy fart. Når du er i tvil — vent!</div>'},
        {"order":7,"icon":"🅿️","title_no":"Kapittel 7 — Stans og parkering","content_no":'<p>Reglene for stans og parkering er viktige for trafikksikkerheten og fremkommeligheten.</p>\n\n<div class="study-law"><strong>Trafikkreglenes § 17. Stans og parkering:</strong>\n\n<p><strong>Det er forbudt å stanse:</strong></p>\n<ul>\n<li>I uoversiktlig kurve, i tunnel, på bakketopp eller på annet uoversiktlig sted</li>\n<li>I vegkryss eller nærmere enn <strong>5 meter</strong> fra vegkrysset</li>\n<li>Helt eller delvis på fortau, gangveg eller sykkelveg</li>\n<li>På gangfelt eller sykkelkryssing eller nærmere enn <strong>5 meter</strong> foran slike steder</li>\n<li>På motorveg og motortrafikkveg</li>\n<li>Nærmere planovergang enn <strong>5 meter</strong></li>\n<li>I kollektivfelt, sambruksfelt eller sykkelfelt (unntak: buss/sporvogn på holdeplass)</li>\n<li>Nærmere enn <strong>20 meter</strong> fra offentlig trafikkskilt for holdeplass (unntak: av/påstigning som ikke hindrer buss/drosje/sporvogn)</li>\n</ul>\n\n<p><strong>Det er forbudt å parkere:</strong></p>\n<ul>\n<li>Foran inn- eller utkjørsel</li>\n<li>På møteplass i vegens hele bredde</li>\n<li>På gågate</li>\n<li>På gatetun utenom særskilt anviste plasser</li>\n<li>På forkjørsveg med fartsgrense over 50 km/t: forbudt å parkere på kjørebanen</li>\n</ul>\n</div>\n\n<div class="study-law"><strong>Vegtrafikkloven § 8. Parkering:</strong> Kongen kan gi forskrift om avgift for parkering av kjøretøy og om forbud mot slik parkering uten at avgift er betalt på forhånd. Kommunen kan reservere parkeringsplasser for bestemte grupper.</div>\n\n<div class="study-tip"><strong>Tips — Huskeregel for 5-metersregelen:</strong> Husk at avstanden på 5 meter gjelder fra der fortauskanten <em>begynner å runde</em> mot krysset — ikke fra selve krysspunktet. Det er ofte lenger enn folk tror!</div>\n\n<div class="study-law"><strong>Trafikkreglenes § 15. Bruk av lys:</strong> Parkeringslys skal være tent under stans eller parkering på veg når lys- eller siktforholdene gjør det påkrevd for å gjøre kjøretøyet synlig. Fjernlys eller nærlys må ikke være tent under slik stans/parkering.</div>'},
        {"order":8,"icon":"🚦","title_no":"Kapittel 8 — Trafikkskilt og vegmerking","content_no":'<p>Trafikkskiltene er delt inn i grupper basert på form, farge og funksjon. Vegmerkingen gir viktig informasjon om kjørebanen.</p>\n\n<p><strong>Skiltenes oppbygging og grupper:</strong></p>\n<ul>\n<li><strong>Fareskilt</strong> — varsler om særlig fare. Trekantform med rød kant. Kan ha gul bunn ved vegarbeid.</li>\n<li><strong>Vikeplikt- og forkjørsskilt</strong> — regulerer vikepliktforholdene på vedkommende strekning eller sted.</li>\n<li><strong>Forbudsskilt</strong> — angir et forbud på vedkommende vegstrekning eller sted. Gjelder i kjøreretningen fra der skiltet er satt opp og fram til nærmeste vegkryss.</li>\n<li><strong>Påbudsskilt</strong> — angir at det gjelder et påbud på vedkommende vegstrekning eller sted. Rund form, blå bunn.</li>\n<li><strong>Opplysningsskilt</strong> — angir at særlige regler gjelder eller slutter å gjelde.</li>\n<li><strong>Serviceskilt</strong> — gir opplysninger om nødhjelp, vegservice, severdigheter.</li>\n<li><strong>Vegvisningsskilt</strong> — gir opplysninger om stedsnavn, virksomheter, vegruter og avstand.</li>\n<li><strong>Underskilt</strong> — gyldig kun sammen med et hovedskilt. Gir nærmere klargjøring av hovedskiltets betydning.</li>\n<li><strong>Markeringsskilt</strong> — gir opplysninger om vegens videre forløp eller hindringer.</li>\n</ul>\n\n<p><strong>Farger på vegvisningsskilt:</strong></p>\n<ul>\n<li>Blå bunn, hvit tekst — motorveger</li>\n<li>Gul bunn, sort tekst — andre veger</li>\n<li>Hvit bunn, sort tekst — andre mål</li>\n<li>Oransje bunn, sort tekst — midlertidig vegvisning</li>\n<li>Brun bunn, hvit tekst — turisttrafikk</li>\n</ul>\n\n<p><strong>Vegmerking — langsgående linjer:</strong></p>\n<ul>\n<li><strong>Hvit midtlinje</strong> — brukes der det ikke er spesielle restriksjoner</li>\n<li><strong>Gul midtlinje</strong> — skilter ikke mellom kjørefelt i samme retning, men mellom motsatte kjøreretninger</li>\n<li><strong>Varsellinje</strong> — stiplet linje som varsler om kommende sperrelinje. Forbikjøring tillatt, men vær forsiktig</li>\n<li><strong>Sperrelinje</strong> — hel linje. <strong>Forbudt å krysse</strong> eller kjøre på denne</li>\n<li><strong>Kjørefeltlinje</strong> — skiller kjørefelt i samme kjøreretning</li>\n</ul>\n\n<div class="study-tip"><strong>Tips:</strong> Huskeregel for sperrelinje vs varsellinje: <em>Sperrelinje = Stopp = Solid linje</em>. Hvis du ser en stiplet linje som blir tettere og tettere, er det en varsellinje som varsler om kommende sperrelinje.</div>'},
        {"order":9,"icon":"💡","title_no":"Kapittel 9 — Lys, signal og tegn","content_no":'<p>Riktig bruk av lys og signaler gjør deg synlig og kommuniserer med andre trafikanter.</p>\n\n<div class="study-law"><strong>Trafikkreglenes § 14. Signal og tegn:</strong>\n<ul>\n<li>Unødig eller hensynsløs bruk av lyd- eller lyssignal er forbudt.</li>\n<li>Ved svinging eller annen vesentlig endring av kjøretøyets plassering i sideretning <strong>skal det gis tegn</strong> til veiledning for annen trafikant.</li>\n<li>Fører av utrykningskjøretøy skal varsle med <strong>blinkende blått lys</strong>. Lydsignal kan nyttes i tillegg, men bare når det er nødvendig.</li>\n<li>Kjøretøy ved vegarbeid som fraviker vegtrafikkbestemmelse, skal varsle med <strong>blinkende gult lys</strong>.</li>\n</ul>\n</div>\n\n<div class="study-law"><strong>Trafikkreglenes § 15. Bruk av lys:</strong>\n<ul>\n<li>Under kjøring med motorvogn skal <strong>påbudt fjernlys, nærlys eller godkjent kjørelys alltid være tent</strong>.</li>\n<li>Fjernlys må ikke benyttes slik at annen trafikant blir <strong>blendet</strong>.</li>\n<li>Nærlys skal nyttes når fjernlys ikke er påkrevd eller ikke er tillatt brukt.</li>\n<li>Kurve-/tåkelys kan ikke nyttes sammen med nærlys.</li>\n</ul>\n</div>\n\n<p><strong>Lystyper og bruksområde:</strong></p>\n<ul>\n<li><strong>Kjørelys</strong> — alltid tent under kjøring (lavere intensitet enn nærlys)</li>\n<li><strong>Nærlys</strong> — standarbelysning ved kjøring, spesielt viktig i mørket og dårlig sikt</li>\n<li><strong>Fjernlys</strong> — gir lengre rekkevidde, men må ikke blende. Slå ned ved møtende trafikk</li>\n<li><strong>Parklys</strong> — brukes ved parkering i mørket når synlighet er begrenset</li>\n</ul>\n\n<div class="study-tip"><strong>Tips:</strong> Husk at tegn (blinklys) er påbudt ved skifte av kjørefelt, svinging og parkering. Gi tegnet i god tid — andre trenger tid til å reagere!</div>\n\n<div class="study-law"><strong>Trafikkreglenes § 16. Forstyrrende kjøring:</strong> I eller ved bebyggelse må det ikke foregå unødvendig og forstyrrende kjøring med motorvogn, bruk av motor på tomgang eller bruk som volder unødig støy eller utslipp av røyk eller gass.</div>'},
        {"order":10,"icon":"🍺","title_no":"Kapittel 10 — Alkohol, rus og kjøring","content_no":'<p>Kjøring i påvirket tilstand er en av de alvorligste overtredelsene i vegtrafikkloven og en av de hyppigste årsaker til alvorlige ulykker.</p>\n\n<div class="study-law"><strong>Vegtrafikkloven § 22. Alkoholpåvirkning:</strong> Ingen må føre eller forsøke å føre motorvogn når han er påvirket av alkohol eller annet berusende eller bedøvende middel.\n\n<strong>Grenser:</strong>\n<ul>\n<li>Alkoholkonsentrasjon i blodet <strong>over 0,2 promille</strong> = regnes alltid som påvirket</li>\n<li>Alternativt: alkoholkonsentrasjon i utåndingsluften <strong>over 0,1 mg per liter luft</strong></li>\n</ul>\n\nFører av motorvogn må ikke nyte alkohol i de <strong>første seks timer etter at han er ferdig med kjøringen</strong>, når han forstår eller må forstå at det kan bli politietterforskning.</div>\n\n<div class="study-law"><strong>Vegtrafikkloven § 22a. Alkotest:</strong> Politiet kan ta alkotest av motorvognfører når:\n<ul>\n<li>Det er grunn til å tro at han har overtrådt § 22</li>\n<li>Han er innblandet i trafikkuhell</li>\n<li>Han er blitt stanset i trafikkontroll</li>\n</ul>\n</div>\n\n<p><strong>Straff etter promillenivå (§ 31):</strong></p>\n<ul>\n<li><strong>0,2 – 0,5 promille</strong>: Bot</li>\n<li><strong>0,5 – 1,0 promille</strong>: Bot og betinget fengsel</li>\n<li><strong>1,0 – 1,5 promille</strong>: Bot og betinget eller ubetinget fengsel</li>\n<li><strong>Over 1,5 promille</strong>: Bot og ubetinget fengsel</li>\n</ul>\n\n<div class="study-law"><strong>Vegtrafikkloven § 33. Tap av førerett:</strong> Tap av retten til å føre motorvogn fastsettes for <strong>minst 1 år</strong> ved promillekjøring over 0,5 promille. Ved gjentakelse innen 5 år: tap av førerett <strong>for alltid</strong>.</div>\n\n<div class="study-tip"><strong>Tips:</strong> 0,2 promille er veldig lavt — dette tilsvarer omtrent 1 liten øl for en gjennomsnittsperson. Det sikreste er ALDRI å drikke alkohol hvis du skal kjøre. Husk også at mange vanlige medisiner kan gi kjøreforbud — sjekk alltid med lege eller apotek.</div>\n\n<div class="study-law"><strong>Vegtrafikkloven § 21:</strong> Ingen må føre kjøretøy når han er syk, svekket, sliten eller trett slik at kjøringen ikke kan skje på trygg måte.</div>'},
        {"order":11,"icon":"📋","title_no":"Kapittel 11 — Forsikring, registrering og ansvar","content_no":'<p>Som bileier og fører har du juridisk og økonomisk ansvar som du må kjenne til.</p>\n\n<div class="study-law"><strong>Lov om ansvar for skade som motorvogner gjør (bilansvarslova):</strong> Regulerer hvem som skal betale erstatning når motorvogn er involvert i en ulykke.</div>\n\n<p><strong>To typer forsikring:</strong></p>\n<ul>\n<li><strong>Trafikkforsikring (ansvarsforsikring)</strong> — Lovpålagt! Dekker skade på <em>andre</em> (personer og kjøretøy). Du kan ikke registrere eller kjøre bilen uten denne.</li>\n<li><strong>Kaskoforsikring</strong> — Frivillig. Dekker skade på <em>eget</em> kjøretøy.</li>\n</ul>\n\n<div class="study-law"><strong>Vegtrafikkloven § 15. Registrering av motorvogn:</strong>\n<ul>\n<li>Motorvogner skal registreres.</li>\n<li>Når motorvogn skifter eier, skal <strong>begge parter</strong> innen 3 dager gi skriftlig melding til registreringsmyndigheten.</li>\n<li>Eier av motorvogn plikter å melde adresseendring innen 3 dager.</li>\n<li>Registrering kan ikke skje uten trygdeerklæring (forsikringsbevis).</li>\n</ul>\n</div>\n\n<div class="study-law"><strong>Vegtrafikkloven § 17. Bruk av motorvogn:</strong> Motorvogn må ikke brukes uten at den er meldt til registrering og påsatt lovlige kjennemerker og det er utferdiget vognkort. <strong>Vognkortet skal alltid følge med under bruken.</strong> Eier plikter å forvisse seg om at den han lar bruke motorvognen, fyller vilkårene for å føre den.</div>\n\n<div class="study-law"><strong>Vegtrafikkloven § 23. Ansvar for kjøretøyets stand:</strong> Før kjøringen begynner, skal føreren forvisse seg om at kjøretøyet er i <strong>forsvarlig og forskriftsmessig stand</strong> og at det er forsvarlig og forskriftsmessig lastet. Eier plikter å sørge for at kjøretøyet ikke brukes dersom det ikke er i forsvarlig stand.</div>\n\n<div class="study-law"><strong>Vegtrafikkloven § 12. Plikter ved trafikkuhell:</strong>\n<ul>\n<li>Enhver som er innblandet i trafikkuhell, skal <strong>straks stanse og hjelpe</strong> skadde personer og dyr.</li>\n<li>De innblandede har gjensidig plikt til å oppgi navn og adresse.</li>\n<li>Har trafikkuhell medført <strong>død eller alvorlig skade</strong>, skal politiet snarest mulig underrettes.</li>\n<li>Kjøretøy som er til fare for trafikken, skal straks flyttes.</li>\n<li>Spor må ikke fjernes og andre forhold av betydning for etterforskningen ikke endres.</li>\n</ul>\n</div>\n\n<div class="study-tip"><strong>Tips:</strong> Dokumenter du skal ha med under kjøring: <em>Førerkort</em> (alltid), <em>vognkort</em> (alltid), og eventuelle kompetansebevis. Du trenger ikke ha med forsikringsbeviset — det er registrert digitalt.</div>'},
        {"order":12,"icon":"🎓","title_no":"Kapittel 12 — Førerkort, øvelseskjøring og opplæring","content_no":'<p>For å kjøre bil i Norge kreves det førerkort. Her er de viktigste reglene for opplæring og øvelseskjøring.</p>\n\n<p><strong>Krav for å få førerkort klasse B (personbil):</strong></p>\n<ul>\n<li>Fylt <strong>18 år</strong></li>\n<li>Bestått <strong>teoriprøve og praktisk førerprøve</strong></li>\n<li>Tilfredsstille helsekrav (syn, hørsel, førlighet)</li>\n<li>Edruelig og god vandel</li>\n<li>Gjennomført obligatorisk opplæring</li>\n</ul>\n\n<p><strong>Krav for privat øvelseskjøring:</strong></p>\n\n<p><em>Krav til eleven:</em></p>\n<ul>\n<li>Fylt <strong>16 år</strong></li>\n<li>Ikke ha sperrefrist</li>\n<li>Være skikket som sjåfør</li>\n<li>Gjennomført <strong>trafikalt grunnkurs</strong></li>\n</ul>\n\n<p><em>Krav til ledsager:</em></p>\n<ul>\n<li>Fylt <strong>25 år</strong></li>\n<li>Innehatt gyldig førerkort sammenhengende de siste <strong>5 år</strong></li>\n<li>Være skikket som ledsager</li>\n</ul>\n\n<div class="study-law"><strong>Vegtrafikkloven § 26. Øvingskjøring:</strong> Øvingskjøring må ikke være til fare eller unødig ulempe for annen trafikk. Øvingskjøring med motorvogn må ikke finne sted tidligere enn <strong>2 år</strong> før det tidspunkt da eleven etter sin alder kan få førerett. <strong>Ved øvingskjøring anses lærer eller ledsager som fører av motorvognen</strong> — men reglene om alkohol og rusmidler gjelder også for eleven.</div>\n\n<p><strong>Den trinnvise opplæringen klasse B:</strong></p>\n<ul>\n<li><strong>Trinn 1</strong>: Trafikalt grunnkurs — grunnleggende trafikadferd og forståelse</li>\n<li><strong>Trinn 2</strong>: Grunnleggende kjøretøy- og kjørekompetanse — teknisk kjøring, sikkerhetskontroll</li>\n<li><strong>Trinn 3</strong>: Trafikal opplæring — sikker kjøring i variert trafikk, sikkerhetskurs på bane</li>\n<li><strong>Trinn 4</strong>: Avsluttende opplæring — landevegskjøring, forbikjøring, sikkerhetskurs i trafikk</li>\n</ul>\n\n<div class="study-law"><strong>Mål for opplæringen (§ 8-2):</strong> Eleven skal gjennom opplevelse, aktivitet og oppsummeringer bli bevisst på hva som menes med at enhver skal ferdes hensynsfullt og være aktpågivende og varsomt så det ikke kan oppstå fare eller voldes skade.</div>\n\n<div class="study-tip"><strong>Tips:</strong> De første ni månedene med førerkort har en ny bilfører 40 ganger høyere risiko for å kjøre av veien enn en erfaren sjåfør — særlig på grunn av manglende erfaring og feil fartstilpassing. Ta det rolig de første månedene!</div>'},
        {"order":13,"icon":"🚑","title_no":"Kapittel 13 — Trafikkuhell og førstehjelp","content_no":'<p>Å vite hva du skal gjøre ved et trafikkuhell kan redde liv. Her er de viktigste pliktene og prosedyrene.</p>\n\n<p><strong>Dine plikter ved trafikkuhell (Vegtrafikkloven § 12):</strong></p>\n<ul>\n<li><strong>Stans straks</strong> — uansett om du er skyldig eller ikke</li>\n<li><strong>Hjelp skadde</strong> — gi hjelp til skadde personer og dyr</li>\n<li><strong>Oppgi identitet</strong> — navn og adresse til de andre involverte</li>\n<li><strong>Varsle politiet</strong> — ved død eller alvorlig personskade, snarest mulig</li>\n<li><strong>Sikre stedet</strong> — flytt kjøretøy som er til fare, men rør ikke spor</li>\n</ul>\n\n<p><strong>Prosedyre som førstemann på ulykkesstedet:</strong></p>\n<ol>\n<li><strong>Stans trygt</strong> — parker sikkert, slå på varselblinkene</li>\n<li><strong>Sett ut varseltrekant</strong> — minst 50-150 m bak ulykken</li>\n<li><strong>Vurder situasjonen</strong> — hvor mange skadde, hva slags skader</li>\n<li><strong>Ring 113</strong> (ambulanse) — gi nøyaktig posisjon, antall skadde</li>\n<li><strong>Gi livreddende førstehjelp</strong> — bevissthet, pust, fri luftvei</li>\n</ol>\n\n<p><strong>Grunnleggende førstehjelp ved trafikkulykke:</strong></p>\n<ul>\n<li>Sjekk bevissthet: snakk til den skadde, rist forsiktig i skuldrene</li>\n<li>Åpne luftveien: legg hodet forsiktig bakover, løft haken</li>\n<li>Sjekk pust: se, hør og kjenn etter i maks 10 sekunder</li>\n<li>Start HLR hvis ikke normal pust: 30 brystkompresjoner + 2 innblåsinger</li>\n<li>Bevisstløs men puster normalt: legg i stabilt sideleie</li>\n<li>Flytt ikke skadde unødvendig (fare for nakke-/ryggskade)</li>\n</ul>\n\n<div class="study-law"><strong>1.5 Førstehjelp — Mål:</strong> Eleven skal ha kunnskap om plikter ved trafikkuhell, kjenne til rutiner for sikring av og opptreden på skadested, og kunne vurdere skadeomfang og utøve praktisk førstehjelp.</div>\n\n<div class="study-tip"><strong>Tips:</strong> Husk rekkefølgen: <em>Varsle — Sikre — Hjelpe</em>. Vurder alltid fare for deg selv og andre før du nærmer deg ulykkesstedet. Din sikkerhet er viktig!</div>'},
        {"order":14,"icon":"🚛","title_no":"Kapittel 14 — Kjøretøy, teknisk stand og sikkerhet","content_no":'<p>Et kjøretøy i god teknisk stand er grunnleggende for trafikksikkerheten.</p>\n\n<div class="study-law"><strong>Vegtrafikkloven § 13. Krav til kjøretøy:</strong> Kjøretøy skal være bygget, innrettet, utstyrt og vedlikeholdt slik at det kan brukes uten å volde unødig fare eller ulempe og uten å skade veg. Endringer som øker den maksimale hastighet eller ytelse på motorsykkel utover fastsatte grenser, er forbudt.</div>\n\n<p><strong>Sikkerhetskontroll av bilen — hva skal sjekkes:</strong></p>\n<ul>\n<li><strong>Bremser</strong> — test bremsene, sjekk bremseeffekten</li>\n<li><strong>Hjul og dekk</strong> — mønsterdybde (minst 1,6 mm, anbefalt 3 mm), dekktrykk, skader</li>\n<li><strong>Lys</strong> — alle lys fungerer (nærlys, fjernlys, bremselys, blinklys, baklys)</li>\n<li><strong>Sikt</strong> — rene vinduer, speil justert riktig, vindusviskere fungerer</li>\n<li><strong>Styring</strong> — sjekk for unormale lyder eller treghet</li>\n<li><strong>Varselinnretninger</strong> — varseltrekant, refleksvest</li>\n<li><strong>Sikkerhetsutstyr</strong> — bilbelte fungerer og er uten skader</li>\n</ul>\n\n<p><strong>Aktiv og passiv sikkerhet:</strong></p>\n<ul>\n<li><strong>Aktiv sikkerhet</strong> — utstyr som <em>forhindrer</em> ulykker: ABS bremser, antiskrens (ESP), automatisk fartstilpasning, alkolas, navigasjonssystem, trafikktilpasset cruisecontroll</li>\n<li><strong>Passiv sikkerhet</strong> — utstyr som <em>beskytter</em> ved ulykke: bilbelte (med beltestrammer), kollisjonsputer (airbag), hodestøtte (forhindrer nakkesleng), deformasjonssoner i karosseriet</li>\n</ul>\n\n<p><strong>Sikkerhetsutstyr og riktig bruk:</strong></p>\n<ul>\n<li><strong>Bilbelte</strong> skal alltid brukes. Bilbelte skal sitte over skulder og hofte, ikke bak ryggen eller under armen. Fører er ansvarlig for at passasjerer under 15 år bruker belte.</li>\n<li><strong>Hodestøtte</strong> skal stilles inn slik at øverste kant er i høyde med toppen av hodet.</li>\n<li><strong>Barnesikring</strong> — barn under 15 år og/eller under 135 cm: påbudt med godkjent barnesete/bilstol. Kollisjonspute MÅ deaktiveres ved barnestol i passasjersete foran.</li>\n</ul>\n\n<div class="study-law"><strong>Vegtrafikkloven § 13a:</strong> I motorvogn er det forbudt å besitte eller bruke utstyr som har til formål å varsle om eller forstyrre trafikkontroller (radarvarsler).</div>\n\n<div class="study-tip"><strong>Tips:</strong> Gjør sikkerhetskontroll FØR turen — ikke mens du kjører. En rask sjekk av lys, dekk og bremser kan forhindre ulykker og dyre bøter.</div>\n\n<p><strong>Miljøvennlig og økonomisk kjøring:</strong></p>\n<ul>\n<li>Bruk høyest mulig gir ved moderat fart</li>\n<li>Unngå unødvendig akselerasjon og hard bremsing — planlegg kjøringen</li>\n<li>Riktig dekktrykk reduserer drivstofforbruket</li>\n<li>Slå av motor ved lang stans</li>\n<li>Tilpass farten til trafikken — unngå stop-and-go</li>\n</ul>'},
        {"order":15,"icon":"⚠️","title_no":"Kapittel 15 — Risiko, ulykker og unge sjåfører","content_no":'<p>Kunnskap om risiko og ulykkesstatistikk hjelper deg å forstå hvorfor reglene finnes og ta bedre beslutninger.</p>\n\n<p><strong>Hva er risiko?</strong></p>\n<p>Risiko er et mål som kombinerer <em>sannsynligheten</em> og <em>virkningen</em> av en hendelse. En hendelse kan ha stor risiko fordi den er svært sannsynlig, eller fordi konsekvensene vil være katastrofale selv om den er usannsynlig.</p>\n\n<p><strong>Ulykkesstatistikk:</strong></p>\n<ul>\n<li>Ungdom er <strong>overrepresentert</strong> i trafikkulykker</li>\n<li>Bortsett fra selvmord er trafikkulykker den vanligste dødsårsaken blant gutter mellom 15 og 24 år</li>\n<li>Nær <strong>80 prosent</strong> av de omkomne i trafikken er menn</li>\n<li>De første 9 månedene med førerkort: <strong>40 ganger høyere risiko</strong> for å kjøre av veien</li>\n<li>Etter hvert som kjøringen automatiseres, synker risikoen kraftig</li>\n</ul>\n\n<p><strong>Vanligste årsaker til ungdomsulykker:</strong></p>\n<ul>\n<li>For høy fart — manglende evne til å beregne riktig fart</li>\n<li>Tretthet og søvnmangel</li>\n<li>Alkohol og rusmidler</li>\n<li>Uoppmerksomhet (mobil, passasjerer)</li>\n<li>Dårlig vær- og veigrep</li>\n<li>Forbikjøring på feil sted</li>\n</ul>\n\n<p><strong>Kjøreprosessen — SE, FORSTÅ, VELGE:</strong></p>\n<ul>\n<li><strong>SE</strong> — systematisk og aktivt innhente informasjon om trafikkmiljøet. Bruk speil, se langt frem, beveg blikket.</li>\n<li><strong>FORSTÅ</strong> — tolke det du ser. Hva betyr det? Hva kan skje? Hvilken fare foreligger?</li>\n<li><strong>VELGE</strong> — velg riktig handling: fart, plassering, signal/tegn.</li>\n</ul>\n\n<div class="study-tip"><strong>Tips:</strong> En god sjåfør er <em>defensiv og forutseende</em> — ikke nødvendigvis den raskeste. Hensynsfullhet og hjelpsomhet bidrar mer til trafikksikkerheten enn kjøreteknikk alene.</div>\n\n<p><strong>Faktorer som påvirker din kjøreevne negativt:</strong></p>\n<ul>\n<li>Tretthet — etter 17 timer uten søvn er du like svekket som ved 0,5 promille</li>\n<li>Mobil/distraksjon — risikoen for ulykke øker 4-8 ganger</li>\n<li>Alkohol og rusmidler</li>\n<li>Sterke følelser (sinne, sorg, stress)</li>\n<li>Sykdom og medisiner</li>\n</ul>\n\n<p><strong>Selskinnsikkerhet — hvem er ekstra sårbare i trafikken:</strong></p>\n<ul>\n<li>Barn — uforutsigbare, lav synlighet, manglende trafikkforståelse</li>\n<li>Eldre — redusert syn, hørsel og reaksjonsevne</li>\n<li>Syklister og fotgjengere — lite beskyttelse ved kollisjon</li>\n<li>Motorsyklister — svært utsatt i kollisjon</li>\n</ul>'},
    ]

    # Hele seedingen er fail-soft. Den er en bekvemmelighet, ikke en forutsetning
    # for at API-et kan svare. Uten try/except vil en enkelt DB-timeout her avbryte
    # oppstarten, /api/health svarer aldri, og Railway melder «never became healthy».
    try:
        # Seed studiebok_chapters (used by webapp) — ONLY if empty
        col = db.studiebok_chapters
        sb_count = await col.count_documents({})
        if sb_count == 0:
            await col.insert_many([{**ch, "image_url": "", "video_url": "", "created_at": now} for ch in CHAPTERS])

        # Seed chapters (used by admin panel Læringsbok) — ONLY if empty
        col2 = db.chapters
        ch_count = await col2.count_documents({})
        if ch_count == 0:
            admin_docs = []
            for ch in CHAPTERS:
                title = ch["title_no"].split(" — ", 1)[-1]
                admin_docs.append({
                    "id": str(uuid.uuid4()),
                    "chapter_num": ch["order"],
                    "section_num": 1,
                    "icon": ch["icon"],
                    "section_title": {"no": title, "th": "", "en": ""},
                    "content": {"no": ch["content_no"], "th": "", "en": ""},
                    "image_url": "",
                    "video_url": "",
                    "created_at": now,
                })
            await col2.insert_many(admin_docs)

        # Always ensure admin user exists with correct password
        admin_email = "admin@thai2drive.com"
        admin_password = "admin123"
        if not await db.admin_users.find_one({"email": admin_email}):
            await db.admin_users.insert_one({"email": admin_email})
        admin_hash = pwd_context.hash(admin_password)
        existing_admin_user = await db.users.find_one({"email": admin_email})
        if existing_admin_user:
            await db.users.update_one({"email": admin_email}, {"$set": {
                "password_hash": admin_hash,
                "is_admin": True,
                "is_premium": True,
            }})
        else:
            await db.users.insert_one({
                "id": str(uuid.uuid4()),
                "email": admin_email,
                "password_hash": admin_hash,
                "is_admin": True,
                "is_premium": True,
                "created_at": now,
            })
    except Exception as exc:
        logging.getLogger("boot").error("Studiebok-seeding hoppet over: %s", exc)

@app.on_event("startup")
async def log_smtp_config():
    """Log email config state at startup — never logs passwords or keys."""
    _sl = logging.getLogger("smtp_config")
    sendgrid_key = bool(os.environ.get("SENDGRID_API_KEY", "").strip())
    resend_key = bool(os.environ.get("RESEND_API_KEY", "").strip())
    cfg = _smtp_config()
    smtp_configured = bool(cfg["host"] and cfg["user"] and cfg["password"])
    method = "sendgrid" if sendgrid_key else ("resend" if resend_key else ("smtp" if smtp_configured else "none"))
    _sl.info(
        "email_method=%s  sendgrid_key=%s  resend_key=%s  "
        "smtp_source=%s  smtp_host=%s  smtp_configured=%s",
        method, sendgrid_key, resend_key,
        cfg["source"], cfg["host"] or "(not set)", smtp_configured,
    )
    if method == "none":
        _sl.warning(
            "No email provider configured — password reset emails will FAIL. "
            "Set SENDGRID_API_KEY in Railway (recommended)."
        )
    elif method == "smtp":
        _sl.warning(
            "Using SMTP — Railway blocks outbound SMTP (port 587). "
            "Set SENDGRID_API_KEY for reliable email delivery."
        )
    elif method == "resend":
        _sl.warning(
            "Using Resend — some Railway IPs are blocked by Cloudflare on api.resend.com. "
            "Set SENDGRID_API_KEY if reset emails fail."
        )


@app.on_event("startup")
async def ensure_indexes():
    """
    Create / verify all MongoDB indexes on every deploy.
    Idempotent — create_index is a no-op if the index already exists.
    Runs in the background (background=True) so existing queries are not blocked.
    """
    try:
        from create_indexes import create_all_indexes  # noqa: E402
        created = await create_all_indexes(db)
        idx_logger = logging.getLogger("indexes")
        for coll, names in created.items():
            idx_logger.info("indexes OK  %-20s %s", coll, names)
    except Exception as exc:
        logging.getLogger("indexes").warning(
            "Index creation skipped: %s", exc
        )

    # Usage-tier indexes (guest_usage + daily_usage collections)
    try:
        await usage_mod.ensure_indexes(db)
    except Exception as exc:
        logging.getLogger("indexes").warning("Usage index creation skipped: %s", exc)


# ── TTS-ruting: skybasert MP3 for web ───────────────────────────────────────
#   th-TH  → Michaels ElevenLabs-klone først, Google som nødfallback.
#   nb-NO  → Michaels ElevenLabs-klone først, Google som nødfallback.
#   en-US  → Michaels ElevenLabs-klone først, Google som nødfallback.
#
# Språkisolasjonen ligger i TEKSTEN, ikke i leverandøren: hvert språk sender sin
# egen tekst, og cache-nøkkelen holder språkene fysisk adskilt.

# Google Cloud TTS voice mapping — thai er primærrute, øvrige språk er fallback
_GOOGLE_TTS_VOICES = {
    "th-TH": "th-TH-Chirp3-HD-Achird",   # Male Chirp3 HD — Google deprecated th-TH-Standard-C
    "nb-NO": "nb-NO-Wavenet-A",
    "en-US": "en-US-Wavenet-D",
}

# Voice ID kan overstyres med env-variabel slik at bytte av ElevenLabs-konto
# ikke krever kodeendring. Default er Michaels klonede stemme "Michael 1".
# Den forrige defaulten ("Ai Mike", IoOuTUO7t2kI2VTJqI10) finnes ikke lenger på
# kontoen og svarte 404 voice_not_found på alle språk — hvert TTS-kall falt da
# gjennom til Google-nødfallbacken. Verifiser alltid en ny ID med et faktisk
# TTS-kall før den settes her.
_DEFAULT_ELEVENLABS_VOICE_IDS = {
    "th-TH": "eulvRsWu7NGAUD1FzMVP",
    "nb-NO": "eulvRsWu7NGAUD1FzMVP",
    "en-US": "eulvRsWu7NGAUD1FzMVP",
}
_ELEVENLABS_VOICE_ENV = {
    "th-TH": ("ELEVENLABS_TH_VOICE_ID", "ELEVENLABS_VOICE_ID_TH"),
    "nb-NO": ("ELEVENLABS_NO_VOICE_ID", "ELEVENLABS_VOICE_ID_NO"),
    "en-US": ("ELEVENLABS_EN_VOICE_ID", "ELEVENLABS_VOICE_ID_EN"),
}

# Modell-ID er env-styrbar. eleven_v3 er den eneste modellen på kontoen som har
# "th" i språklisten (verifisert mot /v1/models) og er derfor påkrevd for thai;
# den dekker norsk og engelsk like godt. Modellen inngår i cache-nøkkelen, så et
# modellbytte gir nye filer i stedet for gammel, feiluttalt lyd.
_DEFAULT_ELEVENLABS_MODEL_ID = "eleven_v3"
_TTS_BREAKER_FAILURE_LIMIT = int(os.environ.get("TTS_BREAKER_FAILURE_LIMIT", "3"))
_TTS_BREAKER_COOLDOWN_SECONDS = int(os.environ.get("TTS_BREAKER_COOLDOWN_SECONDS", "300"))
_TTS_PROVIDER_STATE: Dict[str, Dict[str, Any]] = {}

def _elevenlabs_voice_id(lang: str) -> str:
    """Returner Michaels språkspesifikke klonestemme."""
    env_names = _ELEVENLABS_VOICE_ENV[lang]
    for env_name in env_names:
        voice_id = (os.environ.get(env_name) or "").strip()
        if voice_id:
            return voice_id
    return (
        (os.environ.get("ELEVENLABS_VOICE_ID") or "").strip()
        or _DEFAULT_ELEVENLABS_VOICE_IDS[lang]
    )


def _elevenlabs_model_id() -> str:
    """ElevenLabs-modell — env-overstyrbar uten kodeendring."""
    return (os.environ.get("ELEVENLABS_MODEL_ID") or "").strip() or _DEFAULT_ELEVENLABS_MODEL_ID


def _tts_provider_key(provider: str, lang: str) -> str:
    return f"{provider}:{lang}"


def _tts_provider_status(provider: str, lang: str) -> dict:
    state = _TTS_PROVIDER_STATE.get(_tts_provider_key(provider, lang), {})
    now = time.time()
    disabled_until = float(state.get("disabled_until") or 0)
    cooldown_remaining = max(0, int(disabled_until - now))
    return {
        "provider": provider,
        "lang": lang,
        "failures": int(state.get("failures") or 0),
        "circuit_open": cooldown_remaining > 0,
        "cooldown_remaining_seconds": cooldown_remaining,
        "last_status": state.get("last_status"),
        "last_error": state.get("last_error"),
        "last_failure_at": state.get("last_failure_at"),
    }


def _tts_provider_available(provider: str, lang: str) -> bool:
    return not _tts_provider_status(provider, lang)["circuit_open"]


def _tts_record_success(provider: str, lang: str) -> None:
    _TTS_PROVIDER_STATE[_tts_provider_key(provider, lang)] = {
        "failures": 0,
        "disabled_until": 0,
        "last_status": "ok",
        "last_error": None,
        "last_failure_at": None,
    }


def _tts_record_failure(provider: str, lang: str, error: str, status_code: Optional[int] = None) -> None:
    key = _tts_provider_key(provider, lang)
    state = _TTS_PROVIDER_STATE.get(key, {})
    failures = int(state.get("failures") or 0) + 1
    disabled_until = 0
    if failures >= _TTS_BREAKER_FAILURE_LIMIT:
        disabled_until = time.time() + _TTS_BREAKER_COOLDOWN_SECONDS
    _TTS_PROVIDER_STATE[key] = {
        "failures": failures,
        "disabled_until": disabled_until,
        "last_status": status_code or "error",
        "last_error": str(error)[:240],
        "last_failure_at": datetime.now(timezone.utc).isoformat(),
    }

def _tts_cache_path(provider: str, voice: str, lang: str, text: str) -> str:
    """
    Cache-sti som inkluderer leverandør + stemme i nøkkelen.

    Uten dette ville en fil generert under et ElevenLabs-utfall (altså med
    Google-stemmen) ligge på samme nøkkel og servere feil stemme for alltid,
    selv etter at den klonede stemmen er tilbake.
    """
    import hashlib
    cache_key = hashlib.md5(f"{provider}:{voice}:{lang}:{text}".encode("utf-8")).hexdigest()
    cache_dir = os.path.join("public_assets", "audio")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{cache_key}.mp3")


def _stream_mp3_file(path: str, headers: Optional[dict] = None):
    from fastapi.responses import StreamingResponse

    def chunks():
        with open(path, "rb") as f:
            while True:
                data = f.read(64 * 1024)
                if not data:
                    break
                yield data

    return StreamingResponse(chunks(), media_type="audio/mpeg", headers=headers or {})


async def _google_tts(text: str, lang: str, google_key: str, cache_path: str):
    """Helper — synthesize speech via Google Cloud TTS and return MP3."""
    import base64
    import httpx
    from fastapi import HTTPException

    voice_name = _GOOGLE_TTS_VOICES.get(lang, "th-TH-Standard-A")
    gurl = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={google_key}"
    gpayload = {
        "input": {"text": text},
        "voice": {"languageCode": lang, "name": voice_name},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    gheaders = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(gurl, json=gpayload, headers=gheaders, timeout=30.0)
            if r.status_code != 200:
                logger.error("Google TTS API error %d: %s", r.status_code, r.text)
                _tts_record_failure("google", lang, r.text, r.status_code)
                raise HTTPException(status_code=r.status_code, detail=f"Google TTS API error: {r.text}")

            data = r.json()
            audio_bytes = base64.b64decode(data["audioContent"])

            with open(cache_path, "wb") as f:
                f.write(audio_bytes)

            _tts_record_success("google", lang)
            return _stream_mp3_file(
                cache_path,
                headers={"X-TTS-Provider": "google", "X-TTS-Voice": voice_name},
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Google TTS synthesis failed: %s", e)
        _tts_record_failure("google", lang, str(e))
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")


@app.get("/api/tts/stream")
@app.post("/api/tts/stream")
@app.get("/api/tts")
@app.post("/api/tts")
@api_router.get("/tts/stream")
@api_router.post("/tts/stream")
@api_router.get("/tts")
@api_router.post("/tts")
async def text_to_speech(request: Request, text: Optional[str] = None, lang: Optional[str] = None):
    import httpx
    from fastapi import HTTPException

    # `lang` MÅ defaulte til None, ikke "th-TH". En truthy default gjør
    # `lang or body.get("lang")` til en no-op, og da ble all POST-tekst lest med
    # thai stemme — også norsk og engelsk. Standardspråket settes derfor først
    # etter at body er slått sammen, se lang_map-oppslaget under.
    if request.method == "POST":
        try:
            body = await request.json()
            if isinstance(body, dict):
                text = text or body.get("text")
                lang = lang or body.get("lang")
        except Exception:
            pass

    text = (text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text parameter is required")

    lang_map = {
        "th": "th-TH",
        "no": "nb-NO",
        "nb": "nb-NO",
        "en": "en-US",
        "th-th": "th-TH",
        "nb-no": "nb-NO",
        "en-us": "en-US",
    }
    requested_lang = (lang or "th").strip().lower()
    if requested_lang not in lang_map:
        raise HTTPException(status_code=400, detail="Unsupported TTS language")
    lang = lang_map[requested_lang]

    google_key = os.environ.get("GOOGLE_API_KEY")
    google_cache_path = _tts_cache_path(
        "google", _GOOGLE_TTS_VOICES.get(lang, "th-TH-Standard-A"), lang, text
    )
    # ── Alle språk → Michaels språkspesifikke ElevenLabs-klonestemme ─────
    voice_id = _elevenlabs_voice_id(lang)
    model_id = _elevenlabs_model_id()
    # Modellen er en del av leverandør-nøkkelen: bytter vi modell for å fikse
    # thai-uttale, får vi nye filer i stedet for gammel, feiluttalt cache.
    cloned_cache_path = _tts_cache_path(f"elevenlabs:{model_id}", voice_id, lang, text)

    if os.path.exists(cloned_cache_path):
        return _stream_mp3_file(
            cloned_cache_path,
            headers={"X-TTS-Provider": "elevenlabs-cached", "X-TTS-Voice": voice_id},
        )

    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    if not elevenlabs_key:
        logger.error(
            "KLONET STEMME UTILGJENGELIG: ELEVENLABS_API_KEY er ikke satt — %s "
            "faller tilbake til Google-stemme. Sett nokkelen i miljovariablene.",
            lang,
        )
    elif not _tts_provider_available("elevenlabs", lang):
        logger.error("ElevenLabs circuit breaker er åpen for %s; prøver neste TTS-rute.", lang)
    else:
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabs_key,
            }
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                },
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=payload, headers=headers, timeout=60.0)
                if r.status_code == 200:
                    with open(cloned_cache_path, "wb") as f:
                        f.write(r.content)
                    _tts_record_success("elevenlabs", lang)
                    logger.info(
                        "TTS %s → ElevenLabs klonet stemme %s (modell %s)",
                        lang, voice_id, model_id,
                    )
                    return _stream_mp3_file(
                        cloned_cache_path,
                        headers={"X-TTS-Provider": "elevenlabs", "X-TTS-Voice": voice_id},
                    )
                # Logges som ERROR, ikke WARNING: dette er tap av Michaels stemme.
                _tts_record_failure("elevenlabs", lang, r.text, r.status_code)
                logger.error(
                    "KLONET STEMME FEILET: ElevenLabs svarte %d for voice_id=%s modell=%s (%s). Svar: %s",
                    r.status_code, voice_id, model_id, lang, r.text[:300],
                )
        except Exception as e:
            _tts_record_failure("elevenlabs", lang, str(e))
            logger.error(
                "KLONET STEMME FEILET: ElevenLabs-kall kastet %s for voice_id=%s (%s)",
                e, voice_id, lang,
            )

    # ── Nødfallback: Google Cloud TTS, i egen cache-nøkkel ────────────────
    # Ferdige MP3-filer kan fortsatt serveres selv om provider eller nøkkel er nede.
    if os.path.exists(google_cache_path):
        return _stream_mp3_file(
            google_cache_path,
            headers={"X-TTS-Provider": "google-fallback-cached"},
        )
    if not google_key:
        raise HTTPException(
            status_code=500,
            detail="Ingen TTS-leverandor tilgjengelig (verken ELEVENLABS_API_KEY eller GOOGLE_API_KEY er satt).",
        )
    if not _tts_provider_available("google", lang):
        raise HTTPException(status_code=503, detail="Google TTS er midlertidig utilgjengelig; prøv igjen om litt.")
    return await _google_tts(text, lang, google_key, google_cache_path)


@app.get("/api/tts/status")
async def tts_status():
    """
    Diagnostikk for lydruting — viser hvilken stemme hvert sprak faktisk far.
    Returnerer ingen hemmeligheter, kun om nokler er konfigurert.
    """
    has_eleven = bool(os.environ.get("ELEVENLABS_API_KEY"))
    has_google = bool(os.environ.get("GOOGLE_API_KEY"))
    model_id = _elevenlabs_model_id()

    def route(lang: str) -> dict:
        google_health = _tts_provider_status("google", lang)
        eleven_health = _tts_provider_status("elevenlabs", lang)
        google_ready = has_google and not google_health["circuit_open"]
        eleven_ready = has_eleven and not eleven_health["circuit_open"]
        voice_id = _elevenlabs_voice_id(lang)
        return {
            "intended": f"elevenlabs:{voice_id}",
            "actual": f"elevenlabs:{voice_id}" if eleven_ready
                      else (f"google:{_GOOGLE_TTS_VOICES[lang]} (FALLBACK)" if google_ready else "cache-or-none"),
            "fallback_provider": "google" if google_ready else None,
            "ok": eleven_ready or google_ready,
            "providers": {"elevenlabs": eleven_health, "google": google_health},
        }

    return {
        "elevenlabs_key_configured": has_eleven,
        "google_key_configured": has_google,
        "cloned_voice_ids": {
            lang: _elevenlabs_voice_id(lang)
            for lang in ("th-TH", "nb-NO", "en-US")
        },
        "elevenlabs_model_id": model_id,
        "circuit_breaker": {
            "failure_limit": _TTS_BREAKER_FAILURE_LIMIT,
            "cooldown_seconds": _TTS_BREAKER_COOLDOWN_SECONDS,
        },
        "languages": {lang: route(lang) for lang in ("th-TH", "nb-NO", "en-US")},
    }

@app.get("/api/health")
async def health_check():
    """
    Lightweight liveness + readiness probe.
    Returns 200 with db=connected when MongoDB is reachable,
    200 with db=disconnected when the ping times out or fails.
    Railway / uptime monitors can poll this endpoint.
    """
    try:
        await db.command("ping")
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "connected" if db_ok else "disconnected",
    }


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# ─── Serve Expo web app at /quiz-app ────────────────────────────────────────
_WEBAPP_DIR = Path(__file__).parent / "webapp"
if _WEBAPP_DIR.exists():
    # Mount static asset subdirs directly (JS bundles, images, fonts)
    for _static_sub in ["_expo", "assets"]:
        _sub = _WEBAPP_DIR / _static_sub
        if _sub.exists():
            app.mount(
                f"/quiz-app/{_static_sub}",
                StaticFiles(directory=str(_sub)),
                name=f"webapp-{_static_sub}",
            )

    @app.get("/quiz-app")
    @app.get("/quiz-app/")
    async def serve_webapp_root():
        """Serve the Expo web app root."""
        return FastAPIFileResponse(str(_WEBAPP_DIR / "index.html"))

    @app.get("/quiz-app/favicon.ico")
    async def serve_favicon():
        fav = _WEBAPP_DIR / "favicon.ico"
        if fav.exists():
            return FastAPIFileResponse(str(fav))
        raise HTTPException(status_code=404)

    @app.get("/quiz-app/{full_path:path}")
    async def serve_webapp(full_path: str):
        """Serve Expo Router pages: try exact → {name}.html → index.html fallback."""
        # Exact file (catches .html, .ico, etc.)
        exact = _WEBAPP_DIR / full_path
        if exact.exists() and exact.is_file():
            return FastAPIFileResponse(str(exact))
        # Expo Router generates per-route HTML files: /library → library.html
        html_file = _WEBAPP_DIR / (full_path.rstrip("/") + ".html")
        if html_file.exists():
            return FastAPIFileResponse(str(html_file))
        # SPA client-side routing fallback
        index = _WEBAPP_DIR / "index.html"
        if index.exists():
            return FastAPIFileResponse(str(index))
        raise HTTPException(status_code=404)
