import asyncio
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["thai2drive"]

VIDEOS = [
    {
        "id": str(uuid.uuid4()),
        "youtube_url": "https://www.youtube.com/watch?v=hBwY1810YqI", 
        "title_no": "Du er god sjåfør – du trenger bare ordene",
        "title_th": "คุณเป็นคนขับที่ดี - แค่ต้องการคำศัพท์",
        "title_en": "You are a good driver - you just need the words",
        "instructor_summary_no": "En emosjonell video om hvordan språket er den eneste barrieren.",
        "instructor_summary_th": "วิดีโอสร้างแรงบันดาลใจเกี่ยวกับภาษาที่เป็นอุปสรรคเดียว",
        "instructor_summary_en": "An emotional video about how language is the only barrier.",
        "topic_tags": ["Reaksjonstid"],
        "language": "th",
        "active": True,
        "created_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "title_no": "Farten som drepte deg",
        "title_th": "ความเร็วที่พรากชีวิต",
        "title_en": "The speed that killed you",
        "instructor_summary_no": "Forstå bremselengde og konsekvenser av høy fart.",
        "instructor_summary_th": "ทำความเข้าใจระยะเบรกและผลที่ตามมาของการขับรถเร็ว",
        "instructor_summary_en": "Understand braking distance and the consequences of speeding.",
        "topic_tags": ["Bremsing"],
        "language": "no",
        "active": True,
        "created_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "youtube_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "title_no": "Norsk politi – ikke som i Thailand",
        "title_th": "ตำรวจนอร์เวย์ - ไม่เหมือนในไทย",
        "title_en": "Norwegian police - not like in Thailand",
        "instructor_summary_no": "Hvordan forholde seg til norske trafikkregler og politi.",
        "instructor_summary_th": "วิธีปฏิบัติตามกฎจราจรของนอร์เวย์และตำรวจ",
        "instructor_summary_en": "How to relate to Norwegian traffic rules and police.",
        "topic_tags": ["Vikeplikt"],
        "language": "th",
        "active": True,
        "created_at": datetime.utcnow()
    },
    {
        "id": str(uuid.uuid4()),
        "youtube_url": "https://www.youtube.com/watch?v=M7FIvfx5J10",
        "title_no": "Riktig lysbruk i mørket",
        "title_th": "การใช้แสงที่ถูกต้องในที่มืด",
        "title_en": "Proper light usage in the dark",
        "instructor_summary_no": "Når skal du bruke fjernlys og nærlys?",
        "instructor_summary_th": "เมื่อใดควรใช้ไฟสูงและไฟต่ำ",
        "instructor_summary_en": "When to use high beams and low beams?",
        "topic_tags": ["Lysbruk"],
        "language": "no",
        "active": True,
        "created_at": datetime.utcnow()
    }
]

async def seed():
    # Optional: await db.learning_videos.delete_many({}) # Don't delete in case admin added real ones
    
    # Just to be safe, only insert if collection is empty
    count = await db.learning_videos.count_documents({})
    if count == 0:
        await db.learning_videos.insert_many(VIDEOS)
        print(f"Inserted {len(VIDEOS)} videos.")
    else:
        # Actually let's delete and reseed to ensure tags match exactly
        await db.learning_videos.delete_many({})
        await db.learning_videos.insert_many(VIDEOS)
        print("Deleted old videos and inserted new ones.")

if __name__ == "__main__":
    asyncio.run(seed())
