"""Seed 10 new questions mapped to v2 schema."""
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
{"sporsmal":{"no":"Hva er riktig ved rygging?","th":"การถอยรถควรทำอย่างไร?","en":"What is correct when reversing?"},"alternativer":[{"text":{"no":"Rygge raskt","th":"ถอยเร็ว","en":"Reverse fast"}},{"text":{"no":"Sørge for fri sikt","th":"ต้องมองเห็นชัด","en":"Ensure clear view"}},{"text":{"no":"Kun bruke speil","th":"ใช้กระจกอย่างเดียว","en":"Use mirrors only"}},{"text":{"no":"Ignorere trafikk","th":"ไม่สนใจจราจร","en":"Ignore traffic"}}],"riktigSvar":"B","forklaring":{"no":"Du må ha kontroll og oversikt.","th":"ต้องควบคุมและมองเห็น","en":"You must have control and visibility"}},
{"sporsmal":{"no":"Hva betyr dette skiltet: 'Gangfelt'?","th":"ป้ายทางม้าลายหมายถึงอะไร?","en":"What does a pedestrian crossing sign mean?"},"alternativer":[{"text":{"no":"Parkering","th":"ที่จอดรถ","en":"Parking"}},{"text":{"no":"Gangfelt","th":"ทางม้าลาย","en":"Pedestrian crossing"}},{"text":{"no":"Sykkelvei","th":"ทางจักรยาน","en":"Bike lane"}},{"text":{"no":"Motorvei","th":"มอเตอร์เวย์","en":"Motorway"}}],"riktigSvar":"B","forklaring":{"no":"Varsler gangfelt.","th":"เตือนทางม้าลาย","en":"Warns of crossing"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i kø?","th":"ขับรถติดควรทำอย่างไร?","en":"Driving in traffic jam?"},"alternativer":[{"text":{"no":"Kjøre tett","th":"ขับชิด","en":"Drive close"}},{"text":{"no":"Holde avstand","th":"เว้นระยะ","en":"Keep distance"}},{"text":{"no":"Bytte felt ofte","th":"เปลี่ยนเลนบ่อย","en":"Change lanes often"}},{"text":{"no":"Bruke horn","th":"บีบแตร","en":"Use horn"}}],"riktigSvar":"B","forklaring":{"no":"Hold trygg avstand.","th":"เว้นระยะปลอดภัย","en":"Keep safe distance"}},
{"sporsmal":{"no":"Hva er riktig om blinklys?","th":"ไฟเลี้ยวใช้เมื่อใด?","en":"When to use indicators?"},"alternativer":[{"text":{"no":"Kun i rundkjøring","th":"เฉพาะวงเวียน","en":"Only roundabouts"}},{"text":{"no":"Ved retningsendring","th":"เมื่อเปลี่ยนทิศ","en":"When changing direction"}},{"text":{"no":"Aldri","th":"ไม่เคย","en":"Never"}},{"text":{"no":"Kun motorvei","th":"เฉพาะมอเตอร์เวย์","en":"Only motorway"}}],"riktigSvar":"B","forklaring":{"no":"Varsle andre trafikanter.","th":"แจ้งผู้อื่น","en":"Signal intentions"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i sving?","th":"ขับในโค้งควรทำอย่างไร?","en":"Driving in a curve?"},"alternativer":[{"text":{"no":"Øke fart","th":"เพิ่มความเร็ว","en":"Increase speed"}},{"text":{"no":"Redusere fart","th":"ลดความเร็ว","en":"Reduce speed"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Bremse hardt midt i sving","th":"เบรกแรงในโค้ง","en":"Brake hard mid-curve"}}],"riktigSvar":"B","forklaring":{"no":"Tilpass fart før svingen.","th":"ลดความเร็วก่อนโค้ง","en":"Slow before the curve"}},
{"sporsmal":{"no":"Hva betyr 'sykkelvei'?","th":"ทางจักรยานหมายถึง?","en":"What is a bicycle path?"},"alternativer":[{"text":{"no":"For biler","th":"สำหรับรถยนต์","en":"For cars"}},{"text":{"no":"For sykler","th":"สำหรับจักรยาน","en":"For bicycles"}},{"text":{"no":"For gående","th":"สำหรับคนเดิน","en":"For pedestrians"}},{"text":{"no":"For busser","th":"สำหรับรถบัส","en":"For buses"}}],"riktigSvar":"B","forklaring":{"no":"Kun for sykler.","th":"เฉพาะจักรยาน","en":"For bicycles only"}},
{"sporsmal":{"no":"Hva er riktig ved parkering i veikryss?","th":"จอดในทางแยกได้ไหม?","en":"Parking in intersections?"},"alternativer":[{"text":{"no":"Tillatt","th":"อนุญาต","en":"Allowed"}},{"text":{"no":"Forbudt","th":"ห้าม","en":"Forbidden"}},{"text":{"no":"Kun natt","th":"เฉพาะกลางคืน","en":"Only at night"}},{"text":{"no":"Kun kort","th":"สั้นๆ","en":"Only briefly"}}],"riktigSvar":"B","forklaring":{"no":"Ikke lov å parkere i kryss.","th":"ห้ามจอดในทางแยก","en":"Not allowed in intersections"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i regn?","th":"ขับในฝนควรทำอย่างไร?","en":"Driving in rain?"},"alternativer":[{"text":{"no":"Øke fart","th":"เพิ่มความเร็ว","en":"Increase speed"}},{"text":{"no":"Holde samme fart","th":"เท่าเดิม","en":"Same speed"}},{"text":{"no":"Redusere fart","th":"ลดความเร็ว","en":"Reduce speed"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}}],"riktigSvar":"C","forklaring":{"no":"Reduser fart og øk avstand.","th":"ลดความเร็วและเว้นระยะ","en":"Reduce speed and increase distance"}},
{"sporsmal":{"no":"Hva er riktig ved møtende trafikk på smal vei?","th":"ถนนแคบควรทำอย่างไรเมื่อมีรถสวน?","en":"Oncoming traffic on narrow road?"},"alternativer":[{"text":{"no":"Kjør på","th":"ขับต่อ","en":"Keep going"}},{"text":{"no":"Gi plass","th":"ให้ทาง","en":"Give space"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Bruke horn","th":"บีบแตร","en":"Use horn"}}],"riktigSvar":"B","forklaring":{"no":"Vis hensyn og gi plass.","th":"ให้ทาง","en":"Give way"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i bakke?","th":"ขับขึ้นลงเขาควรทำอย่างไร?","en":"Driving on hills?"},"alternativer":[{"text":{"no":"Rulle i fri","th":"ปล่อยเกียร์ว่าง","en":"Coast in neutral"}},{"text":{"no":"Bruke gir","th":"ใช้เกียร์","en":"Use gears"}},{"text":{"no":"Ignorere","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Kun brems","th":"ใช้เบรกอย่างเดียว","en":"Only brake"}}],"riktigSvar":"B","forklaring":{"no":"Bruk gir for kontroll.","th":"ใช้เกียร์ควบคุม","en":"Use gears for control"}},
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
            "bildeUrl": None,
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
