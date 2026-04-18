"""Seed new questions batch mapped to v2 schema."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

LETTERS = ["A", "B", "C", "D"]

RAW = [
{"sporsmal":{"no":"Hva er viktigst før du starter bilen?","th":"ก่อนสตาร์ทรถควรทำอะไรสำคัญที่สุด?","en":"What is most important before starting the car?"},"alternativer":[{"text":{"no":"Sjekke speil og belte","th":"เช็คกระจกและคาดเข็มขัด","en":"Check mirrors and seatbelt"}},{"text":{"no":"Starte motoren raskt","th":"สตาร์ททันที","en":"Start quickly"}},{"text":{"no":"Trykke gass","th":"เหยียบคันเร่ง","en":"Press gas"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}}],"riktigSvar":"A","forklaring":{"no":"Forberedelse er viktig.","th":"ต้องเตรียมตัว","en":"Preparation is important"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved bruk av sikkerhetsbelte?","th":"การใช้เข็มขัดนิรภัยถูกต้องคือ?","en":"Correct use of seatbelt?"},"alternativer":[{"text":{"no":"Valgfritt","th":"เลือกได้","en":"Optional"}},{"text":{"no":"Alltid påbudt","th":"บังคับเสมอ","en":"Always required"}},{"text":{"no":"Kun foran","th":"เฉพาะหน้า","en":"Front only"}},{"text":{"no":"Kun bak","th":"เฉพาะหลัง","en":"Back only"}}],"riktigSvar":"B","forklaring":{"no":"Belte redder liv.","th":"ช่วยชีวิต","en":"Seatbelts save lives"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er viktig ved kjøring i høy fart?","th":"ขับเร็วควรระวังอะไร?","en":"Important at high speed?"},"alternativer":[{"text":{"no":"Kort avstand","th":"ระยะสั้น","en":"Short distance"}},{"text":{"no":"Lang avstand","th":"ระยะยาว","en":"Long distance"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Blinke","th":"กระพริบ","en":"Blink"}}],"riktigSvar":"B","forklaring":{"no":"Lengre stoppelengde.","th":"หยุดยาก","en":"Longer stopping distance"},"bildeUrl":""},
{"sporsmal":{"no":"Hva bør du gjøre før en lang kjøretur?","th":"ก่อนเดินทางไกลควรทำอะไร?","en":"Before a long trip?"},"alternativer":[{"text":{"no":"Sjekke bilen","th":"เช็ครถ","en":"Check car"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Kjøre fort","th":"เร็ว","en":"Fast"}},{"text":{"no":"Ingen forberedelse","th":"ไม่เตรียม","en":"No prep"}}],"riktigSvar":"A","forklaring":{"no":"Sikkerhet først.","th":"ความปลอดภัย","en":"Safety first"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er viktig ved kjøring med passasjerer?","th":"มีผู้โดยสารควรทำอย่างไร?","en":"Driving with passengers?"},"alternativer":[{"text":{"no":"Fokus på vei","th":"โฟกัสถนน","en":"Focus on road"}},{"text":{"no":"Snakke mye","th":"คุยเยอะ","en":"Talk a lot"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Se bak","th":"มองหลัง","en":"Look back"}}],"riktigSvar":"A","forklaring":{"no":"Unngå distraksjon.","th":"อย่าฟุ้งซ่าน","en":"Avoid distraction"},"bildeUrl":""},
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0

    for q in RAW:
        existing = await db.questions.find_one({"question.no": q["sporsmal"]["no"]})
        if existing:
            skipped += 1
            continue
        doc = {
            "id": str(uuid.uuid4()),
            "question": q["sporsmal"],
            "options": [{"id": LETTERS[i], "text": q["alternativer"][i]["text"]} for i in range(4)],
            "correctOptionId": q["riktigSvar"],
            "explanation": q["forklaring"],
            "bildeUrl": q.get("bildeUrl") or None,
            "category": "Road Rules",
            "difficulty": "easy",
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Done! Inserted: {inserted}, Skipped: {skipped}")
    total = await db.questions.count_documents({})
    print(f"Total: {total}")
    client.close()

asyncio.run(seed())
