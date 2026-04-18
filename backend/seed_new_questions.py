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
{"sporsmal":{"no":"Hva er riktig ved kjøring i tunnel med kø?","th":"รถติดในอุโมงค์ควรทำอย่างไร?","en":"Traffic jam in tunnel?"},"alternativer":[{"text":{"no":"Slå av motor","th":"ดับเครื่อง","en":"Turn off engine"}},{"text":{"no":"Holde avstand","th":"เว้นระยะ","en":"Keep distance"}},{"text":{"no":"Kjøre tett","th":"ชิด","en":"Drive close"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}}],"riktigSvar":"B","forklaring":{"no":"Hold sikker avstand.","th":"เว้นระยะปลอดภัย","en":"Keep safe distance"},"bildeUrl":""},
{"sporsmal":{"no":"Hva betyr dette: forbikjøring tillatt?","th":"อนุญาตให้แซงหมายถึง?","en":"Overtaking allowed?"},"alternativer":[{"text":{"no":"Kan kjøre forbi","th":"แซงได้","en":"You may overtake"}},{"text":{"no":"Ikke lov","th":"ห้าม","en":"Not allowed"}},{"text":{"no":"Kun natt","th":"กลางคืน","en":"Night only"}},{"text":{"no":"Kun buss","th":"รถบัส","en":"Bus only"}}],"riktigSvar":"A","forklaring":{"no":"Du kan kjøre forbi.","th":"แซงได้","en":"Overtaking allowed"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring i kraftig regn?","th":"ฝนหนักควรทำอย่างไร?","en":"Heavy rain driving?"},"alternativer":[{"text":{"no":"Øke fart","th":"เพิ่มความเร็ว","en":"Increase speed"}},{"text":{"no":"Redusere fart","th":"ลดความเร็ว","en":"Reduce speed"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Slå av lys","th":"ปิดไฟ","en":"Turn off lights"}}],"riktigSvar":"B","forklaring":{"no":"Reduser fart.","th":"ลดความเร็ว","en":"Reduce speed"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring bak lastebil?","th":"ขับตามรถบรรทุกควรทำอย่างไร?","en":"Driving behind truck?"},"alternativer":[{"text":{"no":"Kjøre tett","th":"ชิด","en":"Close"}},{"text":{"no":"Holde avstand","th":"เว้นระยะ","en":"Keep distance"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Horn","th":"บีบแตร","en":"Horn"}}],"riktigSvar":"B","forklaring":{"no":"Stor bremselengde.","th":"ต้องเว้นระยะ","en":"Keep distance"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring i sterk sol?","th":"แดดแรงควรทำอย่างไร?","en":"Strong sun driving?"},"alternativer":[{"text":{"no":"Solbriller","th":"แว่นกันแดด","en":"Sunglasses"}},{"text":{"no":"Øke fart","th":"เพิ่มความเร็ว","en":"Increase speed"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Lukke øyne","th":"ปิดตา","en":"Close eyes"}}],"riktigSvar":"A","forklaring":{"no":"Bedre sikt.","th":"ช่วยมองเห็น","en":"Better visibility"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring på glatt is?","th":"น้ำแข็งลื่นควรทำอย่างไร?","en":"Driving on ice?"},"alternativer":[{"text":{"no":"Brå sving","th":"เลี้ยวแรง","en":"Sharp turn"}},{"text":{"no":"Rolig styring","th":"ควบคุมเบา","en":"Gentle steering"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Øke fart","th":"เพิ่มความเร็ว","en":"Increase speed"}}],"riktigSvar":"B","forklaring":{"no":"Unngå skrens.","th":"หลีกเลี่ยงลื่น","en":"Avoid skid"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring i rundkjøring med flere felt?","th":"วงเวียนหลายเลนควรทำอย่างไร?","en":"Multi-lane roundabout?"},"alternativer":[{"text":{"no":"Velg riktig felt","th":"เลือกเลน","en":"Choose correct lane"}},{"text":{"no":"Bytte tilfeldig","th":"สุ่ม","en":"Random"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Stoppe","th":"หยุด","en":"Stop"}}],"riktigSvar":"A","forklaring":{"no":"Planlegg kjøringen.","th":"วางแผน","en":"Plan ahead"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring i bakke med snø?","th":"ขึ้นเขาหิมะควรทำอย่างไร?","en":"Driving uphill in snow?"},"alternativer":[{"text":{"no":"Jevn fart","th":"ความเร็วคงที่","en":"Steady speed"}},{"text":{"no":"Stoppe","th":"หยุด","en":"Stop"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Full gass","th":"เร่งสุด","en":"Full throttle"}}],"riktigSvar":"A","forklaring":{"no":"Unngå hjulspinn.","th":"ป้องกันลื่น","en":"Avoid wheel spin"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring ned bakke i snø?","th":"ลงเขาหิมะควรทำอย่างไร?","en":"Downhill in snow?"},"alternativer":[{"text":{"no":"Bruke gir","th":"ใช้เกียร์","en":"Use gear"}},{"text":{"no":"Fri gir","th":"เกียร์ว่าง","en":"Neutral"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Øke fart","th":"เพิ่มความเร็ว","en":"Increase speed"}}],"riktigSvar":"A","forklaring":{"no":"Motorbrems.","th":"ใช้เกียร์","en":"Engine braking"},"bildeUrl":""},
{"sporsmal":{"no":"Hva er riktig ved kjøring i tett bebyggelse?","th":"เขตเมืองควรทำอย่างไร?","en":"Urban driving?"},"alternativer":[{"text":{"no":"Kjøre fort","th":"เร็ว","en":"Fast"}},{"text":{"no":"Tilpasse fart","th":"ปรับความเร็ว","en":"Adapt speed"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Horn","th":"บีบแตร","en":"Horn"}}],"riktigSvar":"B","forklaring":{"no":"Tilpass etter forhold.","th":"ปรับตามสภาพ","en":"Adapt to conditions"},"bildeUrl":""},
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
