"""Seed 3 new advanced quiz questions into MongoDB."""
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
        "question_text_no": "Du har stanset for å slippe syklisten over. Hva må du være oppmerksom på?",
        "question_text_th": "คุณจอดรถให้จักรยานข้ามแล้ว สิ่งที่ต้องระวังคืออะไร?",
        "question_text_en": "You have stopped to let the cyclist cross. What must you be aware of?",
        "answer_a_no": "Jeg må være oppmerksom på at trafikken imot også stanser for syklistene",
        "answer_a_th": "ต้องระวังว่ารถสวนทางก็หยุดให้จักรยานด้วย",
        "answer_a_en": "I must be aware that oncoming traffic also stops for the cyclists",
        "answer_b_no": "Jeg må vente til syklisten har kommet helt over gaten",
        "answer_b_th": "ต้องรอจนกว่าจักรยานจะข้ามไปหมด",
        "answer_b_en": "I must wait until the cyclist has completely crossed the street",
        "answer_c_no": "Jeg må sjekke om det er trafikk bak meg",
        "answer_c_th": "ต้องตรวจสอบว่ามีรถข้างหลังหรือไม่",
        "answer_c_en": "I must check if there is traffic behind me",
        "answer_d_no": "Jeg må se til begge sider om det kommer flere inn mot gangfeltet før jeg kjører",
        "answer_d_th": "ต้องมองทั้งสองด้านว่ามีคนจะเข้าทางม้าลายอีกหรือไม่ก่อนขับ",
        "answer_d_en": "I must look both ways to see if more are entering the crossing before driving",
        "correct_answer": "D",
        "explanation_no": "Du må alltid forsikre deg om at ingen flere syklister eller fotgjengere er på vei inn i gangfeltet før du kjører videre.",
        "explanation_th": "คุณต้องดูให้แน่ใจว่าไม่มีจักรยานหรือคนเดินถนนคนอื่นกำลังจะข้ามก่อนที่จะขับต่อ",
        "explanation_en": "You must always make sure no more cyclists or pedestrians are entering the crossing before driving on.",
        "category": "Right of Way",
        "difficulty": "easy",
        "image_url": None,
        "aktiv": True,
    },
    {
        "question_text_no": "Hva er riktig?",
        "question_text_th": "ข้อใดถูกต้อง?",
        "question_text_en": "What is correct?",
        "answer_a_no": "Det er 23 km til Drøbak",
        "answer_a_th": "ระยะทางไป Drøbak 23 กม.",
        "answer_a_en": "It is 23 km to Drøbak",
        "answer_b_no": "Det er 285 km til Lierbyen",
        "answer_b_th": "ระยะทางไป Lierbyen 285 กม.",
        "answer_b_en": "It is 285 km to Lierbyen",
        "answer_c_no": "Det er 500 meter til Kjellstad",
        "answer_c_th": "ระยะทางไป Kjellstad 500 เมตร",
        "answer_c_en": "It is 500 meters to Kjellstad",
        "answer_d_no": "Fylkesvei 285 går til Lierbyen",
        "answer_d_th": "ถนนหมายเลข 285 ไปยัง Lierbyen",
        "answer_d_en": "County road 285 goes to Lierbyen",
        "correct_answer": "D",
        "explanation_no": "Tallet 285 viser fylkesvei-nummer, ikke avstand. Skiltet viser hvilken vei som fører til Lierbyen.",
        "explanation_th": "เลข 285 คือหมายเลขถนน ไม่ใช่ระยะทาง ป้ายบอกเส้นทางไป Lierbyen",
        "explanation_en": "The number 285 shows the county road number, not the distance. The sign shows which road leads to Lierbyen.",
        "category": "Traffic Signs",
        "difficulty": "medium",
        "image_url": None,
        "aktiv": True,
    },
    {
        "question_text_no": "Du kjører i 70 km/t og ligger 35 meter bak bilen foran. Er dette sikker avstand?",
        "question_text_th": "คุณขับ 70 กม./ชม. อยู่ห่างรถคันหน้า 35 เมตร ระยะนี้ปลอดภัยหรือไม่?",
        "question_text_en": "You are driving at 70 km/h and are 35 meters behind the car ahead. Is this a safe distance?",
        "answer_a_no": "Ja, men sikten forover blir redusert",
        "answer_a_th": "ใช่ แต่ทัศนวิสัยจะลดลง",
        "answer_a_en": "Yes, but forward visibility is reduced",
        "answer_b_no": "Nei, sikker avstand i denne hastigheten er cirka 60 meter",
        "answer_b_th": "ไม่ ระยะปลอดภัยที่ความเร็วนี้ประมาณ 60 เมตร",
        "answer_b_en": "No, safe distance at this speed is about 60 meters",
        "answer_c_no": "Ja, fordi bremselengden på tørt føre i 70 km/t blir cirka 24 meter",
        "answer_c_th": "ใช่ เพราะระยะเบรกบนถนนแห้งที่ 70 กม./ชม. ประมาณ 24 เมตร",
        "answer_c_en": "Yes, because braking distance on dry road at 70 km/h is about 24 meters",
        "answer_d_no": "Nei, i 70 km/t bør du ha minst 100 meters avstand",
        "answer_d_th": "ไม่ ที่ 70 กม./ชม. ควรห่างอย่างน้อย 100 เมตร",
        "answer_d_en": "No, at 70 km/h you should have at least 100 meters distance",
        "correct_answer": "B",
        "explanation_no": "Ved 70 km/t bør du ha ca. 60 meter avstand for å ha god reaksjonstid og stopplengde.",
        "explanation_th": "ที่ความเร็ว 70 กม./ชม. ควรมีระยะห่างประมาณ 60 เมตรเพื่อความปลอดภัย",
        "explanation_en": "At 70 km/h you should have about 60 meters distance for good reaction time and stopping distance.",
        "category": "Safety",
        "difficulty": "medium",
        "image_url": None,
        "aktiv": True,
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
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Done! Inserted: {inserted}, Skipped (duplicates): {skipped}")
    total = await db.questions.count_documents({})
    print(f"Total questions in database: {total}")
    client.close()

asyncio.run(seed())
