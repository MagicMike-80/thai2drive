from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse as FastAPIFileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uuid
import re
import jwt
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback-secret-change-me')
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 168  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def normalize_question(q: dict) -> dict:
    """Convert v1 flat schema to v2 nested schema expected by the frontend."""
    q.pop("_id", None)
    # Already v2 if 'question' key exists as dict
    if isinstance(q.get("question"), dict):
        return q
    # Convert v1 → v2
    return {
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

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    device_id: str
    mode: str
    category: Optional[str] = None
    total_questions: int
    correct_answers: int
    score_percentage: float
    passed: Optional[bool] = None
    questions_answered: List[Dict[str, Any]]
    started_at: str

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
    email: str
    password: str

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

# ==================== AUTH HELPERS ====================

def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
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

def generate_reset_code() -> str:
    import random
    return str(random.randint(100000, 999999))

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Thai2Drive API - Norway Driving Theory Quiz"}

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

@api_router.get("/questions/random")
async def get_random_questions(category: Optional[str] = None, count: int = Query(default=10, le=50), has_image: Optional[bool] = None):
    pipeline = []
    match_stage: dict = {}
    if category:
        match_stage["category"] = category
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline.append({"$sample": {"size": count}})
    pipeline.append({"$project": {"_id": 0}})
    questions = await db.questions.aggregate(pipeline).to_list(count)
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

@api_router.get("/stats/me")
async def get_my_stats(device_id: str):
    """Per-category accuracy for a device, based on quiz_attempts."""
    # Aggregate by category across all attempts
    pipeline = [
        {"$match": {"device_id": device_id, "total_questions": {"$gt": 0}}},
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
        {"$match": {"device_id": device_id}},
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
    attempt = QuizAttempt(**attempt_data.dict())
    doc = attempt.dict()
    await db.quiz_attempts.insert_one(doc)
    doc.pop("_id", None)
    return doc

@api_router.get("/quiz-attempts/{device_id}")
async def get_quiz_attempts(device_id: str, limit: int = Query(default=20, le=50)):
    attempts = await db.quiz_attempts.find(
        {"device_id": device_id}, {"_id": 0}
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
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    password_hash = pwd_context.hash(data.password)
    user_id = str(uuid.uuid4())

    # Check admin whitelist
    admin_entry = await db.admin_users.find_one({"email": data.email})
    is_admin = admin_entry is not None
    is_premium = is_admin  # Admins get auto premium

    user_doc = {
        "id": user_id,
        "email": data.email,
        "password_hash": password_hash,
        "is_admin": is_admin,
        "is_premium": is_premium,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user_doc)

    token = create_token(user_id, data.email)
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": data.email,
            "is_admin": is_admin,
            "is_premium": is_premium,
        }
    }

@api_router.post("/auth/login")
async def login(data: AuthLogin):
    user = await db.users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Re-check admin status on each login
    admin_entry = await db.admin_users.find_one({"email": data.email})
    is_admin = admin_entry is not None
    if is_admin and not user.get("is_premium"):
        await db.users.update_one({"email": data.email}, {"$set": {"is_admin": True, "is_premium": True}})
        user["is_admin"] = True
        user["is_premium"] = True

    token = create_token(user["id"], user["email"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False),
            "is_premium": user.get("is_premium", False),
        }
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({"id": current_user["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user["id"],
        "email": user["email"],
        "is_admin": user.get("is_admin", False),
        "is_premium": user.get("is_premium", False),
    }

@api_router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    user = await db.users.find_one({"email": data.email})
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset code has been sent"}

    code = generate_reset_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    await db.password_resets.update_one(
        {"email": data.email},
        {"$set": {
            "email": data.email,
            "code": code,
            "expires_at": expires.isoformat(),
            "used": False,
        }},
        upsert=True
    )

    # MOCKED: In production, send email via SendGrid/SES
    logger.info(f"[MOCKED EMAIL] Password reset code for {data.email}: {code}")

    return {"message": "If the email exists, a reset code has been sent"}

@api_router.post("/auth/reset-password")
async def reset_password(data: ResetPasswordRequest):
    reset_entry = await db.password_resets.find_one({
        "email": data.email,
        "code": data.code,
        "used": False,
    })

    if not reset_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    expires_at = datetime.fromisoformat(reset_entry["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Reset code has expired")

    password_hash = pwd_context.hash(data.new_password)
    await db.users.update_one(
        {"email": data.email},
        {"$set": {"password_hash": password_hash}}
    )
    await db.password_resets.update_one(
        {"email": data.email, "code": data.code},
        {"$set": {"used": True}}
    )

    return {"message": "Password reset successfully"}

# ==================== ADMIN ROUTES ====================

@api_router.post("/admin/check")
async def check_admin(data: AdminCheckRequest):
    admin = await db.admin_users.find_one({"email": data.email.strip().lower()})
    return {"is_admin": admin is not None}

@api_router.post("/admin/add")
async def add_admin(data: AdminCheckRequest):
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

    for q in sample_questions:
        q["id"] = str(uuid.uuid4())
        q["created_at"] = datetime.now(timezone.utc).isoformat()
        if "image_url" not in q:
            q["image_url"] = None

    await db.questions.insert_many(sample_questions)
    return {"message": f"Seeded {len(sample_questions)} questions", "seeded": True}

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
    cursor = db.questions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(limit)
    for q in items:
        q.pop("bildeUrl_original_backup", None)
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

    emergent_key = os.getenv("EMERGENT_LLM_KEY")
    if not emergent_key:
        raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    except ImportError:
        raise HTTPException(status_code=500, detail="emergentintegrations not installed")

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

    chat = LlmChat(
        api_key=emergent_key,
        session_id=f"audit-{question_id}",
        system_message=system_prompt,
    ).with_model("gemini", "gemini-2.5-pro")

    try:
        raw = await chat.send_message(UserMessage(
            text=prompt,
            file_contents=[ImageContent(image_base64=b64)],
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI audit failed: {e}")

    text = str(raw).strip()
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


app.include_router(api_router)

# ==================== PUBLIC WEBSITE (landing + legal) ====================
from website import website_router  # noqa: E402
app.include_router(website_router, prefix="")
app.include_router(website_router, prefix="/api")  # also serve under /api/* for Railway routing

# ==================== AI SUPPORT CHAT ====================
from support_chat import support_chat_router  # noqa: E402
app.include_router(support_chat_router, prefix="/api")


# ==================== ADMIN HTML PAGE ====================
from fastapi.responses import HTMLResponse, FileResponse  # noqa: E402
from pathlib import Path as _Path  # noqa: E402

_ADMIN_HTML_PATH = _Path(__file__).resolve().parent / "admin.html"


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


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# ─── Serve Expo web app at /quiz-app ────────────────────────────────────────
_WEBAPP_DIR = Path(__file__).parent / "webapp"
if _WEBAPP_DIR.exists():
    app.mount("/quiz-app", StaticFiles(directory=str(_WEBAPP_DIR), html=True), name="webapp")

    @app.get("/quiz-app/{full_path:path}")
    async def serve_webapp(full_path: str):
        """Fallback: serve index.html for all SPA routes."""
        index = _WEBAPP_DIR / "index.html"
        if index.exists():
            return FastAPIFileResponse(str(index))
        raise HTTPException(status_code=404)
