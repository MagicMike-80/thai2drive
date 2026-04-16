"""Seed 5 new quiz questions into MongoDB."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

NEW_QUESTIONS = [
    {
        "question_text_no": "Hva er hovedmålet med trafikkopplæring?",
        "question_text_th": "เป้าหมายหลักของการเรียนขับรถคืออะไร?",
        "question_text_en": "What is the main goal of driver training?",
        "answer_a_no": "Lære å kjøre fort", "answer_a_th": "เรียนขับเร็ว", "answer_a_en": "Learn to drive fast",
        "answer_b_no": "Bestå prøven raskt", "answer_b_th": "สอบผ่านเร็ว", "answer_b_en": "Pass the test quickly",
        "answer_c_no": "Bli en sikker og ansvarlig sjåfør", "answer_c_th": "เป็นผู้ขับขี่ที่ปลอดภัยและมีความรับผิดชอบ", "answer_c_en": "Become a safe and responsible driver",
        "answer_d_no": "Kjøre lange turer", "answer_d_th": "ขับทางไกล", "answer_d_en": "Drive long trips",
        "correct_answer": "C",
        "explanation_no": "Målet er å utvikle sikre og ansvarlige sjåfører.",
        "explanation_th": "เป้าหมายคือการเป็นผู้ขับขี่ที่ปลอดภัยและมีความรับผิดชอบ",
        "explanation_en": "The goal is to develop safe and responsible drivers.",
        "category": "Safety", "difficulty": "easy",
    },
    {
        "question_text_no": "Hva betyr det å ha god vurderingsevne i trafikken?",
        "question_text_th": "การมีวิจารณญาณที่ดีในจราจรหมายถึงอะไร?",
        "question_text_en": "What does having good judgment in traffic mean?",
        "answer_a_no": "Kjøre fort", "answer_a_th": "ขับเร็ว", "answer_a_en": "Drive fast",
        "answer_b_no": "Ta riktige beslutninger i ulike situasjoner", "answer_b_th": "ตัดสินใจได้ถูกต้องในสถานการณ์ต่างๆ", "answer_b_en": "Make correct decisions in various situations",
        "answer_c_no": "Følge GPS", "answer_c_th": "ตาม GPS", "answer_c_en": "Follow GPS",
        "answer_d_no": "Ignorere andre", "answer_d_th": "ไม่สนใจคนอื่น", "answer_d_en": "Ignore others",
        "correct_answer": "B",
        "explanation_no": "Du må kunne vurdere situasjoner og ta riktige valg.",
        "explanation_th": "ต้องสามารถประเมินสถานการณ์และตัดสินใจได้ถูกต้อง",
        "explanation_en": "You must be able to assess situations and make the right choices.",
        "category": "Safety", "difficulty": "easy",
    },
    {
        "question_text_no": "Hva er viktig for å unngå ulykker?",
        "question_text_th": "อะไรสำคัญเพื่อหลีกเลี่ยงอุบัติเหตุ?",
        "question_text_en": "What is important to avoid accidents?",
        "answer_a_no": "Kjøre fort", "answer_a_th": "ขับเร็ว", "answer_a_en": "Drive fast",
        "answer_b_no": "Være oppmerksom og forutse farer", "answer_b_th": "มีสมาธิและคาดการณ์อันตราย", "answer_b_en": "Be attentive and anticipate hazards",
        "answer_c_no": "Ignorere regler", "answer_c_th": "ไม่สนใจกฎ", "answer_c_en": "Ignore rules",
        "answer_d_no": "Kun følge andre", "answer_d_th": "ตามคนอื่นเท่านั้น", "answer_d_en": "Only follow others",
        "correct_answer": "B",
        "explanation_no": "Oppmerksomhet og forutseing reduserer risiko.",
        "explanation_th": "การมีสมาธิและคาดการณ์ช่วยลดความเสี่ยง",
        "explanation_en": "Attention and anticipation reduce risk.",
        "category": "Safety", "difficulty": "easy",
    },
    {
        "question_text_no": "Hva betyr \"risikoforståelse\"?",
        "question_text_th": "\"ความเข้าใจความเสี่ยง\" หมายถึงอะไร?",
        "question_text_en": "What does 'risk understanding' mean?",
        "answer_a_no": "Kjøre fort", "answer_a_th": "ขับเร็ว", "answer_a_en": "Drive fast",
        "answer_b_no": "Forstå farer i trafikken", "answer_b_th": "เข้าใจอันตรายในจราจร", "answer_b_en": "Understand dangers in traffic",
        "answer_c_no": "Ignorere regler", "answer_c_th": "ไม่สนใจกฎ", "answer_c_en": "Ignore rules",
        "answer_d_no": "Kun se frem", "answer_d_th": "มองข้างหน้าเท่านั้น", "answer_d_en": "Only look ahead",
        "correct_answer": "B",
        "explanation_no": "Du må forstå hva som kan være farlig.",
        "explanation_th": "ต้องเข้าใจอันตรายในจราจร",
        "explanation_en": "You must understand what can be dangerous.",
        "category": "Safety", "difficulty": "easy",
    },
    {
        "question_text_no": "Hva er viktig når du planlegger kjøring?",
        "question_text_th": "อะไรสำคัญเมื่อวางแผนการขับรถ?",
        "question_text_en": "What is important when planning a drive?",
        "answer_a_no": "Kjøre uten plan", "answer_a_th": "ขับไม่มีแผน", "answer_a_en": "Drive without a plan",
        "answer_b_no": "Tenke fremover og forberede seg", "answer_b_th": "คิดล่วงหน้าและเตรียมตัว", "answer_b_en": "Think ahead and prepare",
        "answer_c_no": "Kjøre fort", "answer_c_th": "ขับเร็ว", "answer_c_en": "Drive fast",
        "answer_d_no": "Følge andre", "answer_d_th": "ตามคนอื่น", "answer_d_en": "Follow others",
        "correct_answer": "B",
        "explanation_no": "Planlegging gir tryggere kjøring.",
        "explanation_th": "การวางแผนช่วยให้ขับปลอดภัย",
        "explanation_en": "Planning provides safer driving.",
        "category": "Safety", "difficulty": "easy",
    },
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    inserted = 0
    skipped = 0
    for q in NEW_QUESTIONS:
        existing = await db.questions.find_one({"question_text_no": q["question_text_no"]})
        if existing:
            skipped += 1
            continue

        doc = {
            "id": str(uuid.uuid4()),
            **q,
            "image_url": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Done! Inserted: {inserted}, Skipped (duplicates): {skipped}")
    total = await db.questions.count_documents({})
    print(f"Total questions in database: {total}")
    client.close()

asyncio.run(seed())
