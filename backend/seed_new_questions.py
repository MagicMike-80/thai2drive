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
{"sporsmal":{"no":"Hva er riktig ved kjøring nær en skolebuss som stopper?","th":"เมื่อรถโรงเรียนหยุด ควรทำอย่างไร?","en":"What is correct when driving near a stopped school bus?"},"alternativer":[{"text":{"no":"Kjøre raskt forbi","th":"รีบขับผ่าน","en":"Pass quickly"}},{"text":{"no":"Være ekstra oppmerksom og senke farten","th":"ระวังเป็นพิเศษและลดความเร็ว","en":"Be extra cautious and reduce speed"}},{"text":{"no":"Bruke horn for å varsle","th":"บีบแตรเตือน","en":"Use the horn to warn"}},{"text":{"no":"Ignorere bussen","th":"ไม่สนใจรถบัส","en":"Ignore the bus"}}],"riktigSvar":"B","forklaring":{"no":"Barn kan komme plutselig ut i veien.","th":"เด็กอาจวิ่งออกมาทันที","en":"Children may suddenly enter the road"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i en lang tunnel?","th":"ขับในอุโมงค์ยาวควรทำอย่างไร?","en":"What is correct when driving in a long tunnel?"},"alternativer":[{"text":{"no":"Holde kort avstand","th":"เว้นระยะสั้น","en":"Keep a short distance"}},{"text":{"no":"Holde god avstand og følge skilting","th":"เว้นระยะและทำตามป้าย","en":"Keep a good distance and follow signs"}},{"text":{"no":"Stoppe for å hvile","th":"หยุดพัก","en":"Stop to rest"}},{"text":{"no":"Bruke fjernlys hele tiden","th":"ใช้ไฟสูงตลอด","en":"Use high beams all the time"}}],"riktigSvar":"B","forklaring":{"no":"I tunnel er avstand og skilting ekstra viktig.","th":"ในอุโมงค์ต้องเว้นระยะและดูป้าย","en":"Distance and signs are especially important in tunnels"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring på vei med løs grus?","th":"ถนนกรวดควรขับอย่างไร?","en":"What is correct on a gravel road?"},"alternativer":[{"text":{"no":"Øke fart for bedre grep","th":"เพิ่มความเร็วเพื่อเกาะถนน","en":"Increase speed for better grip"}},{"text":{"no":"Redusere fart og kjøre mykt","th":"ลดความเร็วและขับนุ่มนวล","en":"Reduce speed and drive smoothly"}},{"text":{"no":"Bremse hardt i sving","th":"เบรกแรงในโค้ง","en":"Brake hard in bends"}},{"text":{"no":"Ignorere underlaget","th":"ไม่สนใจสภาพถนน","en":"Ignore the road surface"}}],"riktigSvar":"B","forklaring":{"no":"Løs grus gir dårligere grep.","th":"ถนนกรวดเกาะถนนน้อยกว่า","en":"Loose gravel gives less grip"}},
{"sporsmal":{"no":"Hva er riktig når du nærmer deg et fotgjengerfelt med dårlig sikt?","th":"ใกล้ทางม้าลายที่มองเห็นไม่ดี ควรทำอย่างไร?","en":"What is correct when approaching a crosswalk with poor visibility?"},"alternativer":[{"text":{"no":"Holde farten","th":"รักษาความเร็ว","en":"Keep your speed"}},{"text":{"no":"Senke farten og være klar til å stoppe","th":"ลดความเร็วและพร้อมหยุด","en":"Slow down and be ready to stop"}},{"text":{"no":"Kjøre forbi raskt","th":"รีบผ่าน","en":"Drive past quickly"}},{"text":{"no":"Bruke horn","th":"บีบแตร","en":"Use the horn"}}],"riktigSvar":"B","forklaring":{"no":"Dårlig sikt krever mer forsiktighet.","th":"มองเห็นไม่ดีต้องระวังมากขึ้น","en":"Poor visibility requires extra caution"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring bak en traktor på smal vei?","th":"ขับตามรถแทรกเตอร์บนถนนแคบควรทำอย่างไร?","en":"What is correct when driving behind a tractor on a narrow road?"},"alternativer":[{"text":{"no":"Legge deg tett opp bak","th":"ขับชิดท้าย","en":"Drive closely behind"}},{"text":{"no":"Holde avstand og vente på trygg mulighet","th":"เว้นระยะและรอโอกาสปลอดภัย","en":"Keep distance and wait for a safe opportunity"}},{"text":{"no":"Bruke horn til den slipper deg forbi","th":"บีบแตรให้หลบ","en":"Use the horn until it lets you pass"}},{"text":{"no":"Kjøre forbi uansett","th":"แซงเลย","en":"Overtake regardless"}}],"riktigSvar":"B","forklaring":{"no":"Du må vente til forbikjøring er trygg.","th":"ต้องรอจนกว่าจะแซงได้อย่างปลอดภัย","en":"Wait until overtaking is safe"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i mørket på vei med mange svinger?","th":"กลางคืนบนถนนโค้งมากควรทำอย่างไร?","en":"What is correct when driving at night on a road with many bends?"},"alternativer":[{"text":{"no":"Kjøre fort for å bli ferdig","th":"ขับเร็วให้ถึงไว","en":"Drive fast to finish quickly"}},{"text":{"no":"Tilpasse fart etter sikt og kurver","th":"ปรับความเร็วตามทัศนวิสัยและโค้ง","en":"Adapt speed to visibility and bends"}},{"text":{"no":"Kun se på midtlinjen","th":"มองแต่เส้นกลาง","en":"Only watch the center line"}},{"text":{"no":"Bruke nødblink","th":"เปิดไฟฉุกเฉิน","en":"Use hazard lights"}}],"riktigSvar":"B","forklaring":{"no":"Sikt og kurver krever lavere fart.","th":"โค้งและทัศนวิสัยไม่ดีต้องชะลอ","en":"Bends and limited visibility require lower speed"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring nær et busstopp med mange mennesker?","th":"ใกล้ป้ายรถเมล์ที่มีคนเยอะควรทำอย่างไร?","en":"What is correct when driving near a busy bus stop?"},"alternativer":[{"text":{"no":"Øke fart for å passere fort","th":"เพิ่มความเร็วผ่านเร็วๆ","en":"Increase speed to pass quickly"}},{"text":{"no":"Være ekstra oppmerksom og redusere fart","th":"ระวังเป็นพิเศษและลดความเร็ว","en":"Be extra alert and reduce speed"}},{"text":{"no":"Kjøre helt inntil fortauet","th":"ขับชิดขอบทางมาก","en":"Drive very close to the curb"}},{"text":{"no":"Ignorere folkene","th":"ไม่สนใจคน","en":"Ignore the people"}}],"riktigSvar":"B","forklaring":{"no":"Noen kan gå ut i veien plutselig.","th":"บางคนอาจก้าวออกมาทันที","en":"Someone may suddenly step into the road"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring når du er usikker på veien videre?","th":"เมื่อไม่แน่ใจทางข้างหน้าควรทำอย่างไร?","en":"What is correct when you are unsure about the road ahead?"},"alternativer":[{"text":{"no":"Kjøre videre i høy fart","th":"ขับต่อเร็วๆ","en":"Continue at high speed"}},{"text":{"no":"Senke farten og skaffe oversikt","th":"ลดความเร็วและดูสถานการณ์","en":"Slow down and get an overview"}},{"text":{"no":"Stoppe midt i kjørebanen","th":"หยุดกลางเลน","en":"Stop in the middle of the lane"}},{"text":{"no":"Ignorere usikkerheten","th":"ไม่สนใจความไม่แน่ใจ","en":"Ignore the uncertainty"}}],"riktigSvar":"B","forklaring":{"no":"Ved usikkerhet må du skaffe bedre oversikt.","th":"เมื่อไม่แน่ใจต้องมองให้ชัดก่อน","en":"When unsure, get a better overview first"}},
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
            "difficulty": "medium",
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
