"""Seed 5 new questions WITH images + update glatt kjørebane image."""
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
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Du skal rett frem i krysset. Hva vil du gjøre?",
            "th": "คุณจะขับตรงไปที่สี่แยก คุณจะทำอย่างไร?",
            "en": "You are going straight through the intersection. What will you do?",
        },
        "options": [
            {"id": "A", "text": {"no": "Stoppe før stopplinje", "th": "หยุดก่อนเส้นหยุด", "en": "Stop before stop line"}},
            {"id": "B", "text": {"no": "Kjøre på gult lys hvis det er trygt", "th": "ขับต่อถ้าปลอดภัยเมื่อไฟเหลือง", "en": "Drive on yellow if safe"}},
            {"id": "C", "text": {"no": "Øke farten", "th": "เพิ่มความเร็ว", "en": "Increase speed"}},
            {"id": "D", "text": {"no": "Ignorere lyset", "th": "ไม่สนใจไฟ", "en": "Ignore the light"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Gult lys betyr stopp hvis du kan, men hvis det er for sent å stoppe trygt kan du kjøre.",
            "th": "ไฟเหลืองหมายถึงหยุดถ้าทำได้ แต่ถ้าหยุดไม่ทันอย่างปลอดภัยสามารถขับต่อได้",
            "en": "Yellow means stop if you can, but if too late to stop safely you may proceed.",
        },
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/zjsb0tr1_Screenshot_20260418_001456.jpg",
        "category": "Road Rules", "difficulty": "medium", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva er riktig om havarilommer?",
            "th": "ข้อใดถูกต้องเกี่ยวกับช่องจอดฉุกเฉิน?",
            "en": "What is correct about emergency lay-bys?",
        },
        "options": [
            {"id": "A", "text": {"no": "Kun for parkering", "th": "สำหรับจอดรถเท่านั้น", "en": "Only for parking"}},
            {"id": "B", "text": {"no": "For nødstopp ved problemer", "th": "สำหรับจอดฉุกเฉินเมื่อมีปัญหา", "en": "For emergency stops when having problems"}},
            {"id": "C", "text": {"no": "For forbikjøring", "th": "สำหรับแซง", "en": "For overtaking"}},
            {"id": "D", "text": {"no": "Kun for lastebiler", "th": "สำหรับรถบรรทุกเท่านั้น", "en": "Only for trucks"}},
        ],
        "correctOptionId": "B",
        "explanation": {
            "no": "Havarilommer brukes ved nødstopp i tunnel eller vei.",
            "th": "ช่องจอดฉุกเฉินใช้สำหรับจอดฉุกเฉินในอุโมงค์หรือบนถนน",
            "en": "Emergency lay-bys are used for emergency stops in tunnels or roads.",
        },
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/t8ays952_Screenshot_20260418_001433.jpg",
        "category": "Safety", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Kan du straffes for å kjøre forbi et ulykkessted uten å stoppe?",
            "th": "คุณจะถูกลงโทษหรือไม่ถ้าขับผ่านที่เกิดเหตุโดยไม่หยุด?",
            "en": "Can you be punished for driving past an accident site without stopping?",
        },
        "options": [
            {"id": "A", "text": {"no": "Nei", "th": "ไม่", "en": "No"}},
            {"id": "B", "text": {"no": "Ja, alltid", "th": "ใช่ เสมอ", "en": "Yes, always"}},
            {"id": "C", "text": {"no": "Kun hvis ingen andre er der", "th": "เฉพาะเมื่อไม่มีคนอื่น", "en": "Only if no one else is there"}},
            {"id": "D", "text": {"no": "Kun om du er skyldig", "th": "เฉพาะถ้าคุณเป็นผู้ผิด", "en": "Only if you are at fault"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Du har plikt til å hjelpe hvis det ikke allerede er tilstrekkelig hjelp på stedet.",
            "th": "คุณมีหน้าที่ต้องช่วยเหลือถ้ายังไม่มีคนช่วยเพียงพอ",
            "en": "You have a duty to help if there is not already sufficient help at the scene.",
        },
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/il66ngjx_Screenshot_20260418_001355.jpg",
        "category": "Safety", "difficulty": "medium", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Hva betyr dette skiltet? (vikeplikt)",
            "th": "ป้ายนี้หมายถึงอะไร? (ให้ทาง)",
            "en": "What does this sign mean? (yield)",
        },
        "options": [
            {"id": "A", "text": {"no": "Stopp", "th": "หยุด", "en": "Stop"}},
            {"id": "B", "text": {"no": "Forkjørsvei", "th": "ทางหลัก", "en": "Priority road"}},
            {"id": "C", "text": {"no": "Vikeplikt", "th": "ให้ทาง", "en": "Yield"}},
            {"id": "D", "text": {"no": "Innkjøring forbudt", "th": "ห้ามเข้า", "en": "No entry"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Du må vike for trafikk på kryssende vei.",
            "th": "คุณต้องให้ทางรถบนถนนที่ตัดผ่าน",
            "en": "You must yield to traffic on the crossing road.",
        },
        "bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/t47gkt06_Screenshot_20260418_001338.jpg",
        "category": "Traffic Signs", "difficulty": "easy", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "id": str(uuid.uuid4()),
        "question": {
            "no": "Du skal til venstre i dette krysset. Hvordan bør du plassere deg?",
            "th": "คุณจะเลี้ยวซ้ายที่สี่แยกนี้ ควรจัดตำแหน่งอย่างไร?",
            "en": "You are turning left at this intersection. How should you position yourself?",
        },
        "options": [
            {"id": "A", "text": {"no": "Helt til høyre", "th": "ชิดขวาสุด", "en": "Far right"}},
            {"id": "B", "text": {"no": "Midt i veien", "th": "กลางถนน", "en": "Middle of road"}},
            {"id": "C", "text": {"no": "Til venstre i ditt kjørefelt", "th": "ชิดซ้ายในเลนของคุณ", "en": "Left side of your lane"}},
            {"id": "D", "text": {"no": "På fortauet", "th": "บนทางเท้า", "en": "On the sidewalk"}},
        ],
        "correctOptionId": "C",
        "explanation": {
            "no": "Du skal plassere deg til venstre i kjørefeltet før venstresving.",
            "th": "ต้องจัดตำแหน่งชิดซ้ายในเลนก่อนเลี้ยวซ้าย",
            "en": "You should position yourself to the left in your lane before turning left.",
        },
        "bildeUrl": None,
        "category": "Road Rules", "difficulty": "medium", "active": True, "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0
    for q in NEW_QUESTIONS:
        existing = await db.questions.find_one({"question.no": q["question"]["no"]})
        if existing:
            skipped += 1
            continue
        await db.questions.insert_one(q)
        inserted += 1

    # Also update the glatt kjørebane question with the new slippery road sign image
    glatt = await db.questions.update_one(
        {"question.no": "Hva varsler dette skiltet?", "explanation.no": {"$regex": "glatt"}},
        {"$set": {"bildeUrl": "https://customer-assets.emergentagent.com/job_norge-quiz-app/artifacts/0eg6t55f_Screenshot_20260418_001515.jpg"}}
    )
    if glatt.modified_count > 0:
        print("  OK Updated glatt kjørebane with new sign image")

    print(f"Done! Inserted: {inserted}, Skipped (duplicates): {skipped}")
    with_images = await db.questions.count_documents({"bildeUrl": {"$ne": None}})
    total = await db.questions.count_documents({})
    print(f"Questions with images: {with_images}/{total}")
    client.close()

asyncio.run(seed())
