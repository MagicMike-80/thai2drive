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
async def get_random_questions(category: Optional[str] = None, count: int = Query(default=10, le=200), has_image: Optional[bool] = None):
    pipeline = []
    match_stage: dict = {}
    if category:
        match_stage["category"] = category
    if has_image is True:
        match_stage["bildeUrl"] = {"$exists": True, "$nin": [None, ""]}
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline.append({"$sample": {"size": count}})
    pipeline.append({"$project": {"_id": 0}})
    questions = await db.questions.aggregate(pipeline).to_list(count)
    # If category filter with has_image returns nothing, fall back without category
    if not questions and category and has_image:
        pipeline2 = [
            {"$match": {"bildeUrl": {"$exists": True, "$nin": [None, ""]}}},
            {"$sample": {"size": count}},
            {"$project": {"_id": 0}}
        ]
        questions = await db.questions.aggregate(pipeline2).to_list(count)
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


# ═══════════════════════════════════════════════════════════
#  STUDIEBOK ENDPOINTS
# ═══════════════════════════════════════════════════════════

class StudiebokUpdate(BaseModel):
    title_no: Optional[str] = None
    content_no: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    icon: Optional[str] = None


class StudiebokCreate(BaseModel):
    order: int
    icon: str = "📄"
    title_no: str
    content_no: str
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


app.include_router(api_router)

# ==================== PUBLIC WEBSITE (landing + legal) ====================
from website import website_router  # noqa: E402
app.include_router(website_router, prefix="")
app.include_router(website_router, prefix="/api")  # also serve under /api/* for Railway routing

# ==================== AI SUPPORT CHAT ====================
from support_chat import support_chat_router  # noqa: E402
app.include_router(support_chat_router, prefix="/api")

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

    # Ensure admin entry exists in admin_users (no password hashing needed here)
    admin_email = "admin@thai2drive.com"
    existing_admin = await db.admin_users.find_one({"email": admin_email})
    if not existing_admin:
        await db.admin_users.insert_one({"email": admin_email})
    # Always make sure is_admin flag is set on the user document
    await db.users.update_one(
        {"email": admin_email},
        {"$set": {"is_admin": True, "is_premium": True}},
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
