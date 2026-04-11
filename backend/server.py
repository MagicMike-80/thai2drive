from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Question text in multiple languages
    question_text_no: str
    question_text_th: str
    question_text_en: str
    # Answer options in Norwegian
    answer_a_no: str
    answer_b_no: str
    answer_c_no: str
    answer_d_no: str
    # Answer options in Thai
    answer_a_th: str
    answer_b_th: str
    answer_c_th: str
    answer_d_th: str
    # Answer options in English
    answer_a_en: str
    answer_b_en: str
    answer_c_en: str
    answer_d_en: str
    # Correct answer (A, B, C, or D)
    correct_answer: str
    # Explanations in multiple languages
    explanation_no: str
    explanation_th: str
    explanation_en: str
    # Metadata
    category: str
    difficulty: str = "medium"  # easy, medium, hard
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    questions_by_category: Dict[str, Dict[str, int]] = {}  # {category: {answered: X, correct: Y}}
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    mode: str  # "practice" or "exam"
    category: Optional[str] = None
    total_questions: int
    correct_answers: int
    score_percentage: float
    questions_answered: List[Dict[str, Any]]  # [{question_id, selected_answer, correct, time_taken}]
    started_at: datetime
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class QuizAttemptCreate(BaseModel):
    device_id: str
    mode: str
    category: Optional[str] = None
    total_questions: int
    correct_answers: int
    score_percentage: float
    questions_answered: List[Dict[str, Any]]
    started_at: datetime

class Bookmark(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    question_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BookmarkCreate(BaseModel):
    device_id: str
    question_id: str

# ==================== ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Thai2Drive API - Norway Driving Theory Quiz"}

# ----- QUESTIONS -----

@api_router.get("/questions", response_model=List[Question])
async def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """Get questions with optional filters"""
    query = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty
    
    questions = await db.questions.find(query).limit(limit).to_list(limit)
    return [Question(**q) for q in questions]

@api_router.get("/questions/random", response_model=List[Question])
async def get_random_questions(
    category: Optional[str] = None,
    count: int = Query(default=10, le=50)
):
    """Get random questions for quiz"""
    pipeline = []
    if category:
        pipeline.append({"$match": {"category": category}})
    pipeline.append({"$sample": {"size": count}})
    
    questions = await db.questions.aggregate(pipeline).to_list(count)
    return [Question(**q) for q in questions]

@api_router.get("/questions/{question_id}", response_model=Question)
async def get_question(question_id: str):
    """Get a specific question by ID"""
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return Question(**question)

@api_router.post("/questions", response_model=Question)
async def create_question(question_data: QuestionCreate):
    """Create a new question"""
    question = Question(**question_data.dict())
    await db.questions.insert_one(question.dict())
    return question

@api_router.get("/categories")
async def get_categories():
    """Get all available categories with question counts"""
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    categories = await db.questions.aggregate(pipeline).to_list(100)
    return [{"name": c["_id"], "count": c["count"]} for c in categories]

# ----- USER PROGRESS -----

@api_router.get("/progress/{device_id}", response_model=UserProgress)
async def get_user_progress(device_id: str):
    """Get or create user progress"""
    progress = await db.user_progress.find_one({"device_id": device_id})
    if not progress:
        # Create new progress record
        new_progress = UserProgress(device_id=device_id)
        await db.user_progress.insert_one(new_progress.dict())
        return new_progress
    return UserProgress(**progress)

@api_router.put("/progress/{device_id}")
async def update_user_progress(device_id: str, answered_correct: bool, category: str):
    """Update user progress after answering a question"""
    progress = await db.user_progress.find_one({"device_id": device_id})
    
    if not progress:
        progress = UserProgress(device_id=device_id).dict()
    
    # Update totals
    progress["total_questions_answered"] = progress.get("total_questions_answered", 0) + 1
    if answered_correct:
        progress["correct_answers"] = progress.get("correct_answers", 0) + 1
    
    # Update category stats
    if "questions_by_category" not in progress:
        progress["questions_by_category"] = {}
    
    if category not in progress["questions_by_category"]:
        progress["questions_by_category"][category] = {"answered": 0, "correct": 0}
    
    progress["questions_by_category"][category]["answered"] += 1
    if answered_correct:
        progress["questions_by_category"][category]["correct"] += 1
    
    progress["last_activity"] = datetime.utcnow()
    
    await db.user_progress.update_one(
        {"device_id": device_id},
        {"$set": progress},
        upsert=True
    )
    
    return {"success": True, "progress": progress}

# ----- QUIZ ATTEMPTS -----

@api_router.post("/quiz-attempts", response_model=QuizAttempt)
async def save_quiz_attempt(attempt_data: QuizAttemptCreate):
    """Save a completed quiz attempt"""
    attempt = QuizAttempt(**attempt_data.dict())
    await db.quiz_attempts.insert_one(attempt.dict())
    return attempt

@api_router.get("/quiz-attempts/{device_id}", response_model=List[QuizAttempt])
async def get_quiz_attempts(device_id: str, limit: int = Query(default=20, le=50)):
    """Get quiz history for a device"""
    attempts = await db.quiz_attempts.find(
        {"device_id": device_id}
    ).sort("completed_at", -1).limit(limit).to_list(limit)
    return [QuizAttempt(**a) for a in attempts]

# ----- BOOKMARKS -----

@api_router.post("/bookmarks", response_model=Bookmark)
async def add_bookmark(bookmark_data: BookmarkCreate):
    """Add a question to bookmarks"""
    # Check if already bookmarked
    existing = await db.bookmarks.find_one({
        "device_id": bookmark_data.device_id,
        "question_id": bookmark_data.question_id
    })
    if existing:
        return Bookmark(**existing)
    
    bookmark = Bookmark(**bookmark_data.dict())
    await db.bookmarks.insert_one(bookmark.dict())
    return bookmark

@api_router.delete("/bookmarks/{device_id}/{question_id}")
async def remove_bookmark(device_id: str, question_id: str):
    """Remove a bookmark"""
    result = await db.bookmarks.delete_one({
        "device_id": device_id,
        "question_id": question_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"success": True}

@api_router.get("/bookmarks/{device_id}", response_model=List[Bookmark])
async def get_bookmarks(device_id: str):
    """Get all bookmarks for a device"""
    bookmarks = await db.bookmarks.find({"device_id": device_id}).to_list(500)
    return [Bookmark(**b) for b in bookmarks]

@api_router.get("/bookmarked-questions/{device_id}", response_model=List[Question])
async def get_bookmarked_questions(device_id: str):
    """Get all bookmarked questions with full details"""
    bookmarks = await db.bookmarks.find({"device_id": device_id}).to_list(500)
    question_ids = [b["question_id"] for b in bookmarks]
    questions = await db.questions.find({"id": {"$in": question_ids}}).to_list(500)
    return [Question(**q) for q in questions]

# ----- SEED DATA -----

@api_router.post("/seed")
async def seed_database():
    """Seed the database with sample questions"""
    # Check if already seeded
    count = await db.questions.count_documents({})
    if count > 0:
        return {"message": f"Database already has {count} questions", "seeded": False}
    
    sample_questions = [
        # Traffic Signs
        {
            "question_text_no": "Hva betyr dette skiltet?",
            "question_text_th": "ป้ายนี้หมายความว่าอะไร?",
            "question_text_en": "What does this sign mean?",
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
            "difficulty": "easy"
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
            "difficulty": "easy"
        },
        # Road Rules
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
        # Right of Way
        {
            "question_text_no": "Hvem har vikeplikt i et kryss uten skilt?",
            "question_text_th": "ใครต้องให้ทางในทางแยกที่ไม่มีป้าย?",
            "question_text_en": "Who must give way at an intersection without signs?",
            "answer_a_no": "Trafikk fra venstre",
            "answer_b_no": "Trafikk fra høyre",
            "answer_c_no": "Den som kommer først",
            "answer_d_no": "Alle må stoppe",
            "answer_a_th": "รถจากทางซ้าย",
            "answer_b_th": "รถจากทางขวา",
            "answer_c_th": "คันที่มาถึงก่อน",
            "answer_d_th": "ทุกคันต้องหยุด",
            "answer_a_en": "Traffic from the left",
            "answer_b_en": "Traffic from the right",
            "answer_c_en": "Whoever arrives first",
            "answer_d_en": "Everyone must stop",
            "correct_answer": "A",
            "explanation_no": "Høyreregelen gjelder: Du må gi vikeplikt for trafikk fra høyre, så trafikk fra venstre må vike for deg.",
            "explanation_th": "กฎทางขวามีผล: คุณต้องให้ทางแก่รถจากทางขวา ดังนั้นรถจากทางซ้ายต้องให้ทางคุณ",
            "explanation_en": "The right-hand rule applies: You must give way to traffic from the right, so traffic from the left must yield to you.",
            "category": "Right of Way",
            "difficulty": "medium"
        },
        {
            "question_text_no": "Hvem har vikeplikt når du kjører ut av en parkeringsplass?",
            "question_text_th": "ใครต้องให้ทางเมื่อคุณขับออกจากที่จอดรถ?",
            "question_text_en": "Who has the right of way when you are exiting a parking lot?",
            "answer_a_no": "Du har forkjørsrett",
            "answer_b_no": "Trafikk på veien har forkjørsrett",
            "answer_c_no": "Det avhenger av tid på dagen",
            "answer_d_no": "Fotgjengere bare",
            "answer_a_th": "คุณมีสิทธิ์ไปก่อน",
            "answer_b_th": "รถบนถนนมีสิทธิ์ไปก่อน",
            "answer_c_th": "ขึ้นอยู่กับช่วงเวลาของวัน",
            "answer_d_th": "คนเดินเท้าเท่านั้น",
            "answer_a_en": "You have the right of way",
            "answer_b_en": "Traffic on the road has the right of way",
            "answer_c_en": "It depends on time of day",
            "answer_d_en": "Pedestrians only",
            "correct_answer": "B",
            "explanation_no": "Når du kjører ut av parkeringsplass, gårdsrom eller lignende, må du alltid gi vikeplikt for all trafikk på veien.",
            "explanation_th": "เมื่อคุณขับออกจากที่จอดรถ ลานบ้าน หรือที่คล้ายกัน คุณต้องให้ทางแก่ยานพาหนะทั้งหมดบนถนนเสมอ",
            "explanation_en": "When exiting a parking lot, driveway, or similar, you must always give way to all traffic on the road.",
            "category": "Right of Way",
            "difficulty": "easy"
        },
        # Speed Limits
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
            "explanation_th": "ขีดจำกัดความเร็วมาตรฐานบนทางด่วนในนอร์เวย์คือ 110 กม./ชม. แต่อาจแตกต่างกันตามป้ายจราจร",
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
            "explanation_no": "I en 30-sone er fartsgrensen 30 km/t. Disse sonene er vanlige nær skoler og boligområder.",
            "explanation_th": "ในโซน 30 ขีดจำกัดความเร็วคือ 30 กม./ชม. โซนเหล่านี้พบได้ทั่วไปใกล้โรงเรียนและเขตที่อยู่อาศัย",
            "explanation_en": "In a 30-zone, the speed limit is 30 km/h. These zones are common near schools and residential areas.",
            "category": "Speed Limits",
            "difficulty": "easy"
        },
        # Safety
        {
            "question_text_no": "Hva er den lovlige promillegrensen for førere i Norge?",
            "question_text_th": "ขีดจำกัดแอลกอฮอล์ในเลือดที่ถูกกฎหมายสำหรับคนขับในนอร์เวย์คือเท่าไหร่?",
            "question_text_en": "What is the legal blood alcohol limit for drivers in Norway?",
            "answer_a_no": "0.5 promille",
            "answer_b_no": "0.2 promille",
            "answer_c_no": "0.0 promille",
            "answer_d_no": "0.8 promille",
            "answer_a_th": "0.5 ‰",
            "answer_b_th": "0.2 ‰",
            "answer_c_th": "0.0 ‰",
            "answer_d_th": "0.8 ‰",
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
        }
    ]
    
    # Add IDs and timestamps
    for q in sample_questions:
        q["id"] = str(uuid.uuid4())
        q["created_at"] = datetime.utcnow()
        if "image_url" not in q:
            q["image_url"] = None
    
    await db.questions.insert_many(sample_questions)
    
    return {"message": f"Seeded {len(sample_questions)} questions", "seeded": True}

# Include the router in the main app
app.include_router(api_router)

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
