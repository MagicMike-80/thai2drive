"""Seed 10 new questions with full NO/TH/EN translations (v2 schema)."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

RAW = [
{"sporsmal_NO":"Hva betyr rødt lys i trafikklys?","sporsmal_TH":"ไฟแดงหมายถึงอะไร?","sporsmal_EN":"What does a red traffic light mean?","alternativA":"Kjør","alternativB":"Stopp","alternativC":"Vent","alternativD":"Ignorer","riktigSvar":"B","forklaring_NO":"Rødt lys betyr full stopp.","forklaring_TH":"ไฟแดงหมายถึงต้องหยุด","forklaring_EN":"Red light means full stop","kategori":"Road Rules","difficulty":"easy"},
{"sporsmal_NO":"Hvem har vikeplikt i et kryss uten skilt?","sporsmal_TH":"ใครต้องให้ทางในทางแยกที่ไม่มีป้าย?","sporsmal_EN":"Who must yield at an unmarked intersection?","alternativA":"Den til høyre","alternativB":"Den til venstre","alternativC":"Ingen","alternativD":"Begge","riktigSvar":"A","forklaring_NO":"Høyre-regelen gjelder.","forklaring_TH":"ใช้กฎให้ทางขวา","forklaring_EN":"Right-hand rule applies","kategori":"Right of Way","difficulty":"easy"},
{"sporsmal_NO":"Hva er maksimal fartsgrense i tettbygd strøk?","sporsmal_TH":"ความเร็วสูงสุดในเขตเมืองคือเท่าไหร่?","sporsmal_EN":"What is the speed limit in urban areas?","alternativA":"40","alternativB":"50","alternativC":"60","alternativD":"70","riktigSvar":"B","forklaring_NO":"Standard er 50 km/t.","forklaring_TH":"มาตรฐานคือ 50 กม./ชม.","forklaring_EN":"Standard is 50 km/h","kategori":"Speed Limits","difficulty":"easy"},
{"sporsmal_NO":"Hva betyr blått skilt?","sporsmal_TH":"ป้ายสีน้ำเงินหมายถึงอะไร?","sporsmal_EN":"What does a blue sign mean?","alternativA":"Forbud","alternativB":"Påbud","alternativC":"Fare","alternativD":"Stopp","riktigSvar":"B","forklaring_NO":"Blått skilt betyr påbud.","forklaring_TH":"ป้ายสีน้ำเงินคือคำสั่ง","forklaring_EN":"Blue sign means mandatory instruction","kategori":"Traffic Signs","difficulty":"easy"},
{"sporsmal_NO":"Hva må du gjøre ved glatt føre?","sporsmal_TH":"ควรทำอย่างไรเมื่อถนนลื่น?","sporsmal_EN":"What should you do on slippery roads?","alternativA":"Øke fart","alternativB":"Holde samme fart","alternativC":"Redusere fart","alternativD":"Ignorere","riktigSvar":"C","forklaring_NO":"Du må redusere fart.","forklaring_TH":"ต้องลดความเร็ว","forklaring_EN":"You must reduce speed","kategori":"Safety","difficulty":"easy"},
{"sporsmal_NO":"Hva er reaksjonslengde?","sporsmal_TH":"ระยะตอบสนองคืออะไร?","sporsmal_EN":"What is reaction distance?","alternativA":"Bremselengde","alternativB":"Før du reagerer","alternativC":"Total stopp","alternativD":"Fart","riktigSvar":"B","forklaring_NO":"Strekning før du begynner å bremse.","forklaring_TH":"ระยะก่อนเริ่มเบรก","forklaring_EN":"Distance before braking starts","kategori":"Safety","difficulty":"easy"},
{"sporsmal_NO":"Hva betyr gult lys?","sporsmal_TH":"ไฟเหลืองหมายถึงอะไร?","sporsmal_EN":"What does a yellow light mean?","alternativA":"Kjør","alternativB":"Stopp hvis mulig","alternativC":"Øk fart","alternativD":"Ignorer","riktigSvar":"B","forklaring_NO":"Du skal stoppe hvis mulig.","forklaring_TH":"ควรหยุดถ้าทำได้","forklaring_EN":"Stop if you can","kategori":"Road Rules","difficulty":"easy"},
{"sporsmal_NO":"Når skal du bruke refleksvest?","sporsmal_TH":"ควรใส่เสื้อสะท้อนแสงเมื่อไหร่?","sporsmal_EN":"When should you wear a reflective vest?","alternativA":"Alltid","alternativB":"Ved nødstopp","alternativC":"Kun natt","alternativD":"Aldri","riktigSvar":"B","forklaring_NO":"Ved nødstopp på vei.","forklaring_TH":"เมื่อหยุดฉุกเฉิน","forklaring_EN":"During emergency stops","kategori":"Safety","difficulty":"easy"},
{"sporsmal_NO":"Hvem har høyest autoritet i trafikken?","sporsmal_TH":"ใครมีอำนาจสูงสุดในจราจร?","sporsmal_EN":"Who has the highest authority in traffic?","alternativA":"Trafikklys","alternativB":"Skilt","alternativC":"Politi","alternativD":"Sjåfør","riktigSvar":"C","forklaring_NO":"Politi gjelder over alt.","forklaring_TH":"ตำรวจมีอำนาจสูงสุด","forklaring_EN":"Police override all","kategori":"Road Rules","difficulty":"easy"},
{"sporsmal_NO":"Hva er riktig avstand bak bil?","sporsmal_TH":"ควรเว้นระยะห่างเท่าไหร่?","sporsmal_EN":"What is the correct following distance?","alternativA":"1 sek","alternativB":"2 sek","alternativC":"3 sek","alternativD":"5 sek","riktigSvar":"C","forklaring_NO":"3-sekundersregelen.","forklaring_TH":"กฎ 3 วินาที","forklaring_EN":"3-second rule","kategori":"Safety","difficulty":"easy"},
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0

    for q in RAW:
        doc = {
            "id": str(uuid.uuid4()),
            "question": {"no": q["sporsmal_NO"], "th": q["sporsmal_TH"], "en": q["sporsmal_EN"]},
            "options": [
                {"id": "A", "text": {"no": q["alternativA"], "th": q["alternativA"], "en": q["alternativA"]}},
                {"id": "B", "text": {"no": q["alternativB"], "th": q["alternativB"], "en": q["alternativB"]}},
                {"id": "C", "text": {"no": q["alternativC"], "th": q["alternativC"], "en": q["alternativC"]}},
                {"id": "D", "text": {"no": q["alternativD"], "th": q["alternativD"], "en": q["alternativD"]}},
            ],
            "correctOptionId": q["riktigSvar"],
            "explanation": {"no": q["forklaring_NO"], "th": q["forklaring_TH"], "en": q["forklaring_EN"]},
            "bildeUrl": None,
            "category": q["kategori"],
            "difficulty": q["difficulty"],
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        existing = await db.questions.find_one({"question.no": q["sporsmal_NO"], "question.th": q["sporsmal_TH"]})
        if existing:
            skipped += 1
            continue
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Done! Inserted: {inserted}, Skipped: {skipped}")
    total = await db.questions.count_documents({})
    print(f"Total questions: {total}")
    client.close()

asyncio.run(seed())
