"""Seed 19 new questions mapped to v2 schema."""
import asyncio, json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

LETTERS = ["A", "B", "C", "D"]

RAW = [
{"sporsmal":{"no":"Hva betyr dette skiltet: 'Stans forbudt'?","th":"ป้ายห้ามหยุดหมายถึงอะไร?","en":"What does 'No stopping' sign mean?"},"alternativer":[{"text":{"no":"Du kan parkere kort","th":"จอดสั้นได้","en":"Short parking allowed"}},{"text":{"no":"Du kan stoppe kort","th":"หยุดสั้นได้","en":"Short stop allowed"}},{"text":{"no":"Det er forbudt å stanse","th":"ห้ามหยุด","en":"Stopping is prohibited"}},{"text":{"no":"Kun buss kan stoppe","th":"เฉพาะรถบัส","en":"Only buses may stop"}}],"riktigSvar":"C","forklaring":{"no":"Stans forbudt betyr ingen stopp, heller ikke kort.","th":"ห้ามหยุดแม้ชั่วคราว","en":"No stopping at all, even briefly"}},
{"sporsmal":{"no":"Når gjelder høyreregelen?","th":"กฎให้ทางขวาใช้เมื่อใด?","en":"When does the right-hand rule apply?"},"alternativer":[{"text":{"no":"Alltid","th":"เสมอ","en":"Always"}},{"text":{"no":"Når det ikke er skilt/lys","th":"เมื่อไม่มีป้ายหรือไฟ","en":"When no signs/lights"}},{"text":{"no":"Kun på motorvei","th":"เฉพาะมอเตอร์เวย์","en":"Only on motorways"}},{"text":{"no":"Kun i rundkjøring","th":"เฉพาะวงเวียน","en":"Only in roundabouts"}}],"riktigSvar":"B","forklaring":{"no":"Høyreregelen gjelder uten skilt/lys.","th":"ใช้เมื่อไม่มีป้าย/ไฟ","en":"Applies when no signs/lights"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i tunnel?","th":"การขับในอุโมงค์ควรทำอย่างไร?","en":"What is correct in tunnels?"},"alternativer":[{"text":{"no":"Du kan snu hvis du vil","th":"กลับรถได้","en":"You may turn around"}},{"text":{"no":"Du kan stoppe for pause","th":"หยุดพักได้","en":"Stop for a break"}},{"text":{"no":"Du skal holde avstand og ha lys på","th":"เว้นระยะและเปิดไฟ","en":"Keep distance and lights on"}},{"text":{"no":"Du kan rygge","th":"ถอยหลังได้","en":"You may reverse"}}],"riktigSvar":"C","forklaring":{"no":"Hold avstand og bruk lys.","th":"เว้นระยะและเปิดไฟ","en":"Keep distance and lights on"}},
{"sporsmal":{"no":"Hvem har vikeplikt i rundkjøring?","th":"ใครต้องให้ทางในวงเวียน?","en":"Who yields in a roundabout?"},"alternativer":[{"text":{"no":"De i rundkjøringen","th":"รถในวงเวียน","en":"Vehicles inside"}},{"text":{"no":"De som kjører inn","th":"รถที่กำลังเข้า","en":"Entering vehicles"}},{"text":{"no":"Ingen","th":"ไม่มี","en":"None"}},{"text":{"no":"Begge","th":"ทั้งคู่","en":"Both"}}],"riktigSvar":"B","forklaring":{"no":"Innkjørende har vikeplikt.","th":"ผู้เข้าให้ทาง","en":"Entering vehicles yield"}},
{"sporsmal":{"no":"Hva er minste mønsterdybde på vinterdekk?","th":"ความลึกดอกยางขั้นต่ำของยางฤดูหนาว?","en":"Minimum winter tire tread depth?"},"alternativer":[{"text":{"no":"1,6 mm","th":"1.6 มม.","en":"1.6 mm"}},{"text":{"no":"3,0 mm","th":"3.0 มม.","en":"3.0 mm"}},{"text":{"no":"2,0 mm","th":"2.0 มม.","en":"2.0 mm"}},{"text":{"no":"5,0 mm","th":"5.0 มม.","en":"5.0 mm"}}],"riktigSvar":"B","forklaring":{"no":"Minst 3,0 mm.","th":"อย่างน้อย 3.0 มม.","en":"At least 3.0 mm"}},
{"sporsmal":{"no":"Hva betyr heltrukket midtlinje?","th":"เส้นกลางทึบหมายถึงอะไร?","en":"What does a solid center line mean?"},"alternativer":[{"text":{"no":"Forbikjøring tillatt","th":"แซงได้","en":"Overtaking allowed"}},{"text":{"no":"Forbikjøring forbudt","th":"ห้ามแซง","en":"No overtaking"}},{"text":{"no":"Kun natt","th":"เฉพาะกลางคืน","en":"Only at night"}},{"text":{"no":"Ingen betydning","th":"ไม่มีความหมาย","en":"No meaning"}}],"riktigSvar":"B","forklaring":{"no":"Heltrukket linje = ikke krysse.","th":"ห้ามข้ามเส้น","en":"Do not cross"}},
{"sporsmal":{"no":"Hva er riktig ved bruk av mobil under kjøring?","th":"ใช้มือถือขณะขับได้อย่างไร?","en":"Phone use while driving?"},"alternativer":[{"text":{"no":"Håndholdt er ok","th":"ถือได้","en":"Handheld ok"}},{"text":{"no":"Kun handsfree","th":"แฮนด์ฟรีเท่านั้น","en":"Handsfree only"}},{"text":{"no":"Kun i lav fart","th":"ความเร็วต่ำ","en":"Only low speed"}},{"text":{"no":"Alltid forbudt","th":"ห้ามทั้งหมด","en":"Always forbidden"}}],"riktigSvar":"B","forklaring":{"no":"Kun handsfree er lov.","th":"ใช้แฮนด์ฟรีเท่านั้น","en":"Handsfree only"}},
{"sporsmal":{"no":"Hva er riktig plassering før høyresving?","th":"ก่อนเลี้ยวขวาควรอยู่เลนไหน?","en":"Position before right turn?"},"alternativer":[{"text":{"no":"Til venstre","th":"ซ้าย","en":"Left"}},{"text":{"no":"Midt i feltet","th":"กลางเลน","en":"Middle"}},{"text":{"no":"Til høyre","th":"ขวา","en":"Right"}},{"text":{"no":"På fortau","th":"ทางเท้า","en":"Sidewalk"}}],"riktigSvar":"C","forklaring":{"no":"Legg deg til høyre.","th":"ชิดขวา","en":"Keep right"}},
{"sporsmal":{"no":"Hva betyr 'forkjørsvei slutt'?","th":"สิ้นสุดถนนมีสิทธิ์ก่อนหมายถึง?","en":"End of priority road?"},"alternativer":[{"text":{"no":"Du har fortsatt rett","th":"ยังมีสิทธิ์","en":"Still priority"}},{"text":{"no":"Høyreregelen gjelder","th":"ใช้กฎขวา","en":"Right-hand rule"}},{"text":{"no":"Stopp alltid","th":"หยุดเสมอ","en":"Always stop"}},{"text":{"no":"Kun venstre viker","th":"ซ้ายให้ทาง","en":"Left yields"}}],"riktigSvar":"B","forklaring":{"no":"Tilbake til høyreregelen.","th":"กลับสู่กฎขวา","en":"Back to right-hand rule"}},
{"sporsmal":{"no":"Hva gjør du ved utrykningskjøretøy med blålys?","th":"ทำอย่างไรเมื่อรถฉุกเฉินมา?","en":"What to do for emergency vehicles?"},"alternativer":[{"text":{"no":"Ignorer","th":"ไม่สนใจ","en":"Ignore"}},{"text":{"no":"Øk fart","th":"เพิ่มความเร็ว","en":"Speed up"}},{"text":{"no":"Gi fri vei","th":"หลีกทาง","en":"Give way"}},{"text":{"no":"Stopp midt i veien","th":"หยุดกลางถนน","en":"Stop in lane"}}],"riktigSvar":"C","forklaring":{"no":"Du skal gi fri vei.","th":"ต้องหลีกทาง","en":"Give way"}},
{"sporsmal":{"no":"Hva er riktig ved forbikjøring på venstre side?","th":"แซงทางซ้ายได้ไหม?","en":"Overtaking on the left?"},"alternativer":[{"text":{"no":"Alltid lov","th":"ได้เสมอ","en":"Always allowed"}},{"text":{"no":"Som hovedregel ikke","th":"โดยทั่วไปไม่ได้","en":"Generally not allowed"}},{"text":{"no":"Kun på motorvei","th":"เฉพาะมอเตอร์เวย์","en":"Only on motorways"}},{"text":{"no":"Kun i by","th":"เฉพาะในเมือง","en":"Only in city"}}],"riktigSvar":"B","forklaring":{"no":"Som hovedregel ikke tillatt.","th":"โดยทั่วไปห้าม","en":"Generally not allowed"}},
{"sporsmal":{"no":"Hva betyr blinkende gult lys?","th":"ไฟเหลืองกระพริบหมายถึง?","en":"Flashing yellow light means?"},"alternativer":[{"text":{"no":"Stopp","th":"หยุด","en":"Stop"}},{"text":{"no":"Kjør fort","th":"ไปเร็ว","en":"Go fast"}},{"text":{"no":"Vær oppmerksom","th":"ระวัง","en":"Be cautious"}},{"text":{"no":"Ignorer","th":"ไม่สนใจ","en":"Ignore"}}],"riktigSvar":"C","forklaring":{"no":"Vær ekstra oppmerksom.","th":"ระวังเป็นพิเศษ","en":"Be cautious"}},
{"sporsmal":{"no":"Hva er riktig om avstand i regn?","th":"ระยะห่างในฝนควรเป็นอย่างไร?","en":"Following distance in rain?"},"alternativer":[{"text":{"no":"Samme som normalt","th":"เท่าเดิม","en":"Same"}},{"text":{"no":"Kortere","th":"สั้นลง","en":"Shorter"}},{"text":{"no":"Lengre","th":"มากขึ้น","en":"Longer"}},{"text":{"no":"Ingen betydning","th":"ไม่สำคัญ","en":"No effect"}}],"riktigSvar":"C","forklaring":{"no":"Øk avstanden.","th":"เพิ่มระยะ","en":"Increase distance"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring på motorvei? (høyre)","th":"การขับบนมอเตอร์เวย์ถูกต้องคือ?","en":"Correct motorway driving?"},"alternativer":[{"text":{"no":"Hold til høyre","th":"ชิดขวา","en":"Keep right"}},{"text":{"no":"Kjør i venstre alltid","th":"อยู่ซ้ายเสมอ","en":"Always left"}},{"text":{"no":"Stopp for pause","th":"หยุดพัก","en":"Stop for break"}},{"text":{"no":"Snu hvis feil","th":"กลับรถ","en":"Turn around"}}],"riktigSvar":"A","forklaring":{"no":"Hold til høyre.","th":"ชิดขวา","en":"Keep right"}},
{"sporsmal":{"no":"Hva betyr 'innkjøring forbudt'? (alle)","th":"ห้ามเข้า หมายถึง?","en":"No entry means?"},"alternativer":[{"text":{"no":"Kun busser","th":"เฉพาะรถบัส","en":"Only buses"}},{"text":{"no":"Ingen kjøretøy","th":"ไม่มีรถ","en":"No vehicles"}},{"text":{"no":"Kun sykler","th":"เฉพาะจักรยาน","en":"Only bikes"}},{"text":{"no":"Kun beboere","th":"เฉพาะผู้อยู่อาศัย","en":"Residents only"}}],"riktigSvar":"B","forklaring":{"no":"Gjelder alle kjøretøy.","th":"ใช้กับทุกคัน","en":"All vehicles"}},
{"sporsmal":{"no":"Hva er riktig ved parkering i bakke?","th":"จอดบนทางลาดควรทำอย่างไร?","en":"Parking on a slope?"},"alternativer":[{"text":{"no":"Ingen tiltak","th":"ไม่ทำอะไร","en":"Do nothing"}},{"text":{"no":"Bruk håndbrems og gir","th":"ใช้เบรกมือและเกียร์","en":"Use handbrake and gear"}},{"text":{"no":"Kun brems","th":"ใช้เบรกอย่างเดียว","en":"Only brake"}},{"text":{"no":"La bilen rulle","th":"ปล่อยไหล","en":"Let it roll"}}],"riktigSvar":"B","forklaring":{"no":"Sikre bilen.","th":"ต้องยึดรถ","en":"Secure vehicle"}},
{"sporsmal":{"no":"Hva er riktig om kjøring med alkohol?","th":"การขับขี่กับแอลกอฮอล์ถูกต้องคือ?","en":"Driving with alcohol?"},"alternativer":[{"text":{"no":"Opp til 0,5 promille","th":"ได้ถึง 0.5","en":"Up to 0.5"}},{"text":{"no":"Opp til 0,2 promille","th":"ได้ถึง 0.2","en":"Up to 0.2"}},{"text":{"no":"Ingen grense","th":"ไม่มีจำกัด","en":"No limit"}},{"text":{"no":"Kun natt","th":"เฉพาะกลางคืน","en":"Only at night"}}],"riktigSvar":"B","forklaring":{"no":"Grensen er 0,2.","th":"จำกัด 0.2","en":"Limit is 0.2"}},
{"sporsmal":{"no":"Hva betyr grønt lys? (klart)","th":"ไฟเขียวหมายถึง?","en":"Green light means?"},"alternativer":[{"text":{"no":"Stopp","th":"หยุด","en":"Stop"}},{"text":{"no":"Kjør hvis klart","th":"ไปเมื่อปลอดภัย","en":"Go if clear"}},{"text":{"no":"Vent","th":"รอ","en":"Wait"}},{"text":{"no":"Rygg","th":"ถอย","en":"Reverse"}}],"riktigSvar":"B","forklaring":{"no":"Kjør hvis klart.","th":"ไปเมื่อปลอดภัย","en":"Go if clear"}},
{"sporsmal":{"no":"Hva er riktig ved kjøring i mørke?","th":"ขับในที่มืดควรทำอย่างไร?","en":"Driving in the dark?"},"alternativer":[{"text":{"no":"Bruk fjernlys alltid","th":"ใช้ไฟสูงตลอด","en":"High beams always"}},{"text":{"no":"Blend ned ved møtende","th":"ลดไฟเมื่อมีรถสวน","en":"Dip for oncoming"}},{"text":{"no":"Ingen lys","th":"ไม่ใช้ไฟ","en":"No lights"}},{"text":{"no":"Kun parklys","th":"ไฟจอด","en":"Parking lights only"}}],"riktigSvar":"B","forklaring":{"no":"Unngå blending.","th":"หลีกเลี่ยงการแยงตา","en":"Avoid dazzling"}},
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
    print(f"Total questions: {total}")
    client.close()

asyncio.run(seed())
