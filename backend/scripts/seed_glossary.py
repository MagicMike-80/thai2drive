"""
seed_glossary.py — fyller learning_glossary med 22 norske trafikkuttrykk
Trygt å kjøre på nytt — hopper over eksisterende (by term_no).
Kjør: cd thai2drive/backend && python scripts/seed_glossary.py
"""

import asyncio, os, uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "")
if not MONGO_URL:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGO_URL="):
                    MONGO_URL = line.split("=", 1)[1].strip('"').strip("'")
                    break
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not found in environment or .env")

DB_NAME = "thai2drive"

TERMS = [
    {
        "term_no": "Vikeplikt",
        "term_th": "การให้ทาง",
        "term_en": "Yield / Right of way",
        "definition_no": "Plikten til å la andre trafikanter passere før deg.",
        "definition_th": "หน้าที่ที่ต้องยอมให้ผู้ใช้ถนนคนอื่นผ่านก่อนคุณ",
        "definition_en": "The obligation to let other road users pass before you.",
        "example_no": "Du har vikeplikt for biler fra høyre i ukontrollert kryss.",
        "example_th": "คุณต้องให้ทางรถที่มาจากทางขวาในสี่แยกที่ไม่มีป้าย",
        "example_en": "You must yield to cars from the right at an uncontrolled intersection.",
        "topic_tags": ["Vikeplikt", "Kryss"],
    },
    {
        "term_no": "Høyreregelen",
        "term_th": "กฎการให้ทางด้านขวา",
        "term_en": "Right-hand rule",
        "definition_no": "Grunnregel om at du har vikeplikt for trafikk som kommer fra din høyre side ved ukontrollerte kryss.",
        "definition_th": "กฎพื้นฐานที่คุณต้องให้ทางการจราจรที่มาจากทางขวาในสี่แยกที่ไม่มีป้าย",
        "definition_en": "Basic rule that you yield to traffic coming from your right at uncontrolled intersections.",
        "example_no": "Ingen skilt i krysset? Bruk høyreregelen.",
        "example_th": "ไม่มีป้ายในสี่แยก? ใช้กฎขวา",
        "example_en": "No signs at the intersection? Apply the right-hand rule.",
        "topic_tags": ["Vikeplikt", "Kryss"],
    },
    {
        "term_no": "Forkjørsvei",
        "term_th": "ถนนหลัก",
        "term_en": "Priority road",
        "definition_no": "Vei merket med skilt 220 der du har forkjørsrett over all trafikk fra kryssende veier.",
        "definition_th": "ถนนที่ติดป้าย 220 ซึ่งคุณมีสิทธิ์ก่อนรถทุกคันจากถนนที่ตัดกัน",
        "definition_en": "Road marked with sign 220 where you have right of way over all traffic from crossing roads.",
        "example_no": "Skilt 220 er gul rombe — du er på prioritert vei.",
        "example_th": "ป้าย 220 คือรูปสี่เหลี่ยมเหลือง — คุณอยู่บนถนนหลัก",
        "example_en": "Sign 220 is a yellow diamond — you are on a priority road.",
        "topic_tags": ["Vikeplikt", "Skilt", "Kryss"],
    },
    {
        "term_no": "Avkjørsel",
        "term_th": "ทางเข้าออก / ทางเชื่อม",
        "term_en": "Driveway / Side access",
        "definition_no": "Tilkoblingsvei til privat eiendom, parkeringsplass eller sidevei. Den som kjører ut fra avkjørsel har alltid vikeplikt.",
        "definition_th": "ทางเชื่อมเข้าทรัพย์สินส่วนตัว ที่จอดรถ หรือถนนรอง ผู้ที่ออกจากทางเข้าออกต้องให้ทางเสมอ",
        "definition_en": "Access road to private property, car park, or side road. Anyone exiting a driveway always yields.",
        "example_no": "Kjører du ut fra en parkeringsplass, er alt annet i veien din prioritert.",
        "example_th": "เมื่อออกจากที่จอดรถ รถทุกคันบนถนนมีสิทธิ์ก่อนคุณ",
        "example_en": "When exiting a car park, everything else on the road has priority over you.",
        "topic_tags": ["Vikeplikt", "Parkering"],
    },
    {
        "term_no": "Rundkjøring",
        "term_th": "วงเวียน",
        "term_en": "Roundabout",
        "definition_no": "Vegkryss der trafikken kjører i sirkel. Den som skal inn har vikeplikt for trafikk som allerede er inne.",
        "definition_th": "สี่แยกที่การจราจรวนเป็นวงกลม ผู้ที่เข้าวงเวียนต้องให้ทางรถที่อยู่ในวงเวียนแล้ว",
        "definition_en": "Road junction where traffic moves in a circle. Entering traffic yields to traffic already inside.",
        "example_no": "Brems før du kjører inn i rundkjøringen og gi vikeplikt.",
        "example_th": "ชะลอก่อนเข้าวงเวียนและให้ทาง",
        "example_en": "Slow down before entering the roundabout and yield.",
        "topic_tags": ["Vikeplikt", "Kryss", "Rundkjøring"],
    },
    {
        "term_no": "Gangfelt",
        "term_th": "ทางม้าลาย",
        "term_en": "Pedestrian crosswalk",
        "definition_no": "Oppmerket felt der fotgjengere har forkjørsrett. Bilister plikter å stanse for fotgjengere i eller ved gangfeltet.",
        "definition_th": "ช่องที่ทาสีไว้ซึ่งคนเดินเท้ามีสิทธิ์ก่อน ผู้ขับรถต้องหยุดให้คนเดินเท้าในหรือใกล้ทางม้าลาย",
        "definition_en": "Marked area where pedestrians have right of way. Drivers must stop for pedestrians at or near the crosswalk.",
        "example_no": "Se en fotgjenger ved gangfeltet? Stans alltid.",
        "example_th": "เห็นคนเดินเท้าที่ทางม้าลายหรือไม่? หยุดเสมอ",
        "example_en": "See a pedestrian at the crosswalk? Always stop.",
        "topic_tags": ["Vikeplikt", "Gangfelt", "Fotgjengere"],
    },
    {
        "term_no": "Fartsgrense",
        "term_th": "ขีดจำกัดความเร็ว",
        "term_en": "Speed limit",
        "definition_no": "Høyeste tillatte hastighet på en vegstrekning. Angis i km/t på runde hvite skilt med rød kant.",
        "definition_th": "ความเร็วสูงสุดที่อนุญาตบนถนนช่วงนั้น แสดงบนป้ายกลมสีขาวขอบแดง หน่วยเป็น กม./ชม.",
        "definition_en": "Maximum permitted speed on a road section. Shown in km/h on round white signs with red border.",
        "example_no": "Tettsted: 50 km/t. Motorvei: 110 km/t.",
        "example_th": "ในเมือง: 50 กม./ชม. ทางด่วน: 110 กม./ชม.",
        "example_en": "Town: 50 km/h. Motorway: 110 km/h.",
        "topic_tags": ["Fart", "Skilt"],
    },
    {
        "term_no": "Bremselengde",
        "term_th": "ระยะเบรก",
        "term_en": "Braking distance",
        "definition_no": "Distansen kjøretøyet tilbakelegger fra det øyeblikket bremsen trykkes til bilen stopper helt.",
        "definition_th": "ระยะทางที่ยานพาหนะเคลื่อนที่ตั้งแต่กดเบรกจนกระทั่งรถหยุดสนิท",
        "definition_en": "The distance a vehicle travels from the moment the brakes are applied until it stops completely.",
        "example_no": "Ved 80 km/t er bremselengden ca. 32 meter på tørr asfalt.",
        "example_th": "ที่ความเร็ว 80 กม./ชม. ระยะเบรกประมาณ 32 เมตรบนถนนแห้ง",
        "example_en": "At 80 km/h the braking distance is approx. 32 metres on dry asphalt.",
        "topic_tags": ["Fart", "Sikkerhet", "Bremselengde"],
    },
    {
        "term_no": "Reaksjonstid",
        "term_th": "เวลาตอบสนอง",
        "term_en": "Reaction time",
        "definition_no": "Tiden fra du oppdager en fare til du begynner å bremse. Normalt ca. 1 sekund for en uthvilt sjåfør.",
        "definition_th": "เวลาตั้งแต่คุณพบอันตรายจนเริ่มเบรก ปกติประมาณ 1 วินาทีสำหรับผู้ขับที่พักผ่อนเพียงพอ",
        "definition_en": "The time from perceiving a hazard to beginning to brake. Normally about 1 second for a rested driver.",
        "example_no": "Med reaksjonstid 1 sek og 90 km/t tilbakelegger du 25 meter før bremsen virker.",
        "example_th": "ด้วยเวลาตอบสนอง 1 วิ ที่ความเร็ว 90 กม./ชม. คุณเคลื่อนไป 25 เมตรก่อนเบรกจะทำงาน",
        "example_en": "With 1 sec reaction time at 90 km/h you travel 25 metres before the brake takes effect.",
        "topic_tags": ["Fart", "Sikkerhet", "Bremselengde"],
    },
    {
        "term_no": "Stoppelengde",
        "term_th": "ระยะหยุดรวม",
        "term_en": "Stopping distance",
        "definition_no": "Den totale distansen fra du oppdager fare til bilen stopper. Stoppelengde = reaksjonsavstand + bremselengde.",
        "definition_th": "ระยะทางรวมตั้งแต่คุณพบอันตรายจนรถหยุดสนิท ระยะหยุด = ระยะตอบสนอง + ระยะเบรก",
        "definition_en": "Total distance from hazard detection to full stop. Stopping distance = reaction distance + braking distance.",
        "example_no": "80 km/t: ca. 22 m reaksjon + 32 m bremsing = 54 m total stoppelengde.",
        "example_th": "80 กม./ชม.: ประมาณ 22 ม. ตอบสนอง + 32 ม. เบรก = 54 ม. ระยะหยุดรวม",
        "example_en": "80 km/h: approx. 22 m reaction + 32 m braking = 54 m total stopping distance.",
        "topic_tags": ["Fart", "Sikkerhet", "Bremselengde"],
    },
    {
        "term_no": "Utrykningskjøretøy",
        "term_th": "รถฉุกเฉิน",
        "term_en": "Emergency vehicle",
        "definition_no": "Kjøretøy som bruker blålys og/eller sirener — ambulanse, brannbil, politi. All trafikk har vikeplikt.",
        "definition_th": "ยานพาหนะที่ใช้ไฟสีน้ำเงินและ/หรือไซเรน ได้แก่ รถพยาบาล รถดับเพลิง รถตำรวจ การจราจรทุกคันต้องให้ทาง",
        "definition_en": "Vehicle using blue lights and/or sirens — ambulance, fire truck, police. All traffic must yield.",
        "example_no": "Hør sirene? Kjør mot høyre og stopp om nødvendig.",
        "example_th": "ได้ยินไซเรนหรือไม่? เคลื่อนไปทางขวาและหยุดถ้าจำเป็น",
        "example_en": "Hear a siren? Move right and stop if necessary.",
        "topic_tags": ["Vikeplikt", "Sikkerhet"],
    },
    {
        "term_no": "Sikkerhetsavstand",
        "term_th": "ระยะห่างที่ปลอดภัย",
        "term_en": "Safety distance",
        "definition_no": "Minimum avstand til forankjørende som gir deg nok tid til å stoppe uten å kollidere. Tommelfinger: 3 sekunder.",
        "definition_th": "ระยะห่างขั้นต่ำจากรถข้างหน้าที่ให้คุณมีเวลาพอหยุดได้โดยไม่ชน กฎง่ายๆ: 3 วินาที",
        "definition_en": "Minimum gap to the car ahead giving you enough time to stop without colliding. Rule of thumb: 3 seconds.",
        "example_no": "Teller du '1001, 1002, 1003' og er klar — god avstand.",
        "example_th": "นับ '1001, 1002, 1003' แล้วผ่านจุดเดิม — ระยะห่างดี",
        "example_en": "Count '1001, 1002, 1003' past the same point — good distance.",
        "topic_tags": ["Fart", "Sikkerhet"],
    },
    {
        "term_no": "Forbikjøring",
        "term_th": "การแซง",
        "term_en": "Overtaking",
        "definition_no": "Å kjøre forbi et langsomt foran kjørende kjøretøy. Kun lovlig der ikke forbudt og sikten er god nok.",
        "definition_th": "การขับแซงยานพาหนะที่ช้ากว่าข้างหน้า ทำได้เฉพาะเมื่อไม่ต้องห้ามและมองเห็นได้ชัดเจนพอ",
        "definition_en": "Passing a slower vehicle ahead. Only legal where not prohibited and visibility is sufficient.",
        "example_no": "Heltrukken midtlinje = forbikjøring forbudt.",
        "example_th": "เส้นกลางถนนเต็ม = ห้ามแซง",
        "example_en": "Solid centre line = no overtaking.",
        "topic_tags": ["Fart", "Kjøreregeler"],
    },
    {
        "term_no": "Blindsone",
        "term_th": "จุดบอด",
        "term_en": "Blind spot",
        "definition_no": "Området rundt bilen som ikke er synlig i speilene. Sjekk alltid blindsonen med en skuldersjekk ved filskifte.",
        "definition_th": "บริเวณรอบรถที่มองไม่เห็นในกระจก ตรวจสอบจุดบอดด้วยการหันมองไหล่เสมอเมื่อเปลี่ยนเลน",
        "definition_en": "The area around the car not visible in mirrors. Always check blind spot with a shoulder check when changing lanes.",
        "example_no": "Motorsykler er lette å miste av syne i blindsonen.",
        "example_th": "รถมอเตอร์ไซค์มักถูกมองข้ามในจุดบอด",
        "example_en": "Motorcycles are easy to miss in the blind spot.",
        "topic_tags": ["Sikkerhet", "Kjøreregeler"],
    },
    {
        "term_no": "Midtlinje",
        "term_th": "เส้นกลางถนน",
        "term_en": "Centre line",
        "definition_no": "Linje midt i veien som skiller kjøreretningene. Stiplet = kan krysses. Heltrukken = ikke kryss (forbikjøringsforbud).",
        "definition_th": "เส้นกลางถนนที่แบ่งทิศทางการจราจร ประ = ข้ามได้ ต่อเนื่อง = ห้ามข้าม (ห้ามแซง)",
        "definition_en": "Line in the middle of the road separating directions. Dashed = may cross. Solid = do not cross (no overtaking).",
        "example_no": "Heltrukken gul linje betyr at det er ulovlig å krysse.",
        "example_th": "เส้นสีเหลืองต่อเนื่องหมายความว่าการข้ามผิดกฎหมาย",
        "example_en": "A solid yellow line means it is illegal to cross.",
        "topic_tags": ["Skilt", "Kjøreregeler"],
    },
    {
        "term_no": "Teoriprøve",
        "term_th": "การสอบทฤษฎี",
        "term_en": "Theory test",
        "definition_no": "Skriftlig prøve du må bestå før du kan ta oppkjøring. 45 spørsmål, maks 7 feil.",
        "definition_th": "การสอบข้อเขียนที่ต้องผ่านก่อนทดสอบขับรถจริง 45 ข้อ ผิดได้ไม่เกิน 7 ข้อ",
        "definition_en": "Written test you must pass before the practical driving test. 45 questions, max 7 wrong.",
        "example_no": "Thai2Drive hjelper deg å bestå teoriprøven på første forsøk.",
        "example_th": "Thai2Drive ช่วยให้คุณผ่านการสอบทฤษฎีในครั้งแรก",
        "example_en": "Thai2Drive helps you pass the theory test on the first attempt.",
        "topic_tags": ["Førerprøve"],
    },
    {
        "term_no": "Oppkjøring",
        "term_th": "การทดสอบขับรถจริง",
        "term_en": "Practical driving test",
        "definition_no": "Praktisk kjøreprøve der sensor bedømmer kjøreferdigheter i virkelig trafikk.",
        "definition_th": "การทดสอบขับรถจริงที่ผู้ตรวจสอบประเมินทักษะการขับรถในสภาพจราจรจริง",
        "definition_en": "Practical driving test where an examiner assesses driving skills in real traffic.",
        "example_no": "Du møter til oppkjøring etter bestått teoriprøve.",
        "example_th": "คุณเข้าสอบขับรถจริงหลังจากผ่านการสอบทฤษฎี",
        "example_en": "You take the practical test after passing the theory test.",
        "topic_tags": ["Førerprøve"],
    },
    {
        "term_no": "Filkjøring",
        "term_th": "การขับในเลน",
        "term_en": "Lane discipline",
        "definition_no": "Plikten til å holde deg i riktig fil og ikke krysse linjer unødvendig.",
        "definition_th": "หน้าที่ที่ต้องอยู่ในเลนที่ถูกต้องและไม่ข้ามเส้นโดยไม่จำเป็น",
        "definition_en": "The obligation to stay in the correct lane and not cross lines unnecessarily.",
        "example_no": "Hold høyre fil på tofeltsvei om du ikke kjører forbi noen.",
        "example_th": "อยู่เลนขวาบนถนนสองเลนหากคุณไม่แซงใคร",
        "example_en": "Keep to the right lane on a two-lane road if you are not overtaking.",
        "topic_tags": ["Kjøreregeler"],
    },
    {
        "term_no": "Vikepliktskilt",
        "term_th": "ป้ายให้ทาง",
        "term_en": "Yield sign (triangle)",
        "definition_no": "Rød trekant (skilt 202) — du plikter å gi fri bane for all kryssende trafikk.",
        "definition_th": "สามเหลี่ยมสีแดง (ป้าย 202) — คุณต้องเปิดทางให้รถที่ตัดผ่านทุกคัน",
        "definition_en": "Red triangle (sign 202) — you must give way to all crossing traffic.",
        "example_no": "Trekant-skilt = alltid vikeplikt, men ikke alltid stans.",
        "example_th": "ป้ายสามเหลี่ยม = ให้ทางเสมอ แต่ไม่จำเป็นต้องหยุดสนิทเสมอไป",
        "example_en": "Triangle sign = always yield, but not always a full stop.",
        "topic_tags": ["Vikeplikt", "Skilt"],
    },
    {
        "term_no": "Stopp-skilt",
        "term_th": "ป้ายหยุด",
        "term_en": "Stop sign (octagon)",
        "definition_no": "Rødt åttekant-skilt (128) — du MÅ stanse helt og gi vikeplikt før du kan fortsette.",
        "definition_th": "ป้ายแปดเหลี่ยมสีแดง (128) — คุณต้องหยุดสนิทและให้ทางก่อนจะขับต่อ",
        "definition_en": "Red octagonal sign (128) — you MUST stop completely and yield before continuing.",
        "example_no": "Kjører du uten å stoppe forbi stopp-skilt, er det straffbart.",
        "example_th": "การขับผ่านป้ายหยุดโดยไม่หยุดสนิทมีโทษ",
        "example_en": "Driving past a stop sign without stopping is a punishable offence.",
        "topic_tags": ["Vikeplikt", "Skilt"],
    },
    {
        "term_no": "Bilbelte",
        "term_th": "เข็มขัดนิรภัย",
        "term_en": "Seatbelt",
        "definition_no": "Påbudt sikkerhetsutstyr for alle i bilen. Sjåføren plikter å påse at passasjerer under 15 år bruker belte.",
        "definition_th": "อุปกรณ์ความปลอดภัยบังคับสำหรับทุกคนในรถ ผู้ขับต้องรับผิดชอบให้ผู้โดยสารอายุต่ำกว่า 15 ปีคาดเข็มขัด",
        "definition_en": "Mandatory safety equipment for all in the car. The driver is responsible for ensuring passengers under 15 use a belt.",
        "example_no": "Glem aldri bilbeltet — ikke én gang på kort kjøretur.",
        "example_th": "อย่าลืมเข็มขัดนิรภัยเด็ดขาด — แม้แต่การขับระยะสั้น",
        "example_en": "Never forget your seatbelt — not even on a short trip.",
        "topic_tags": ["Sikkerhet"],
    },
    {
        "term_no": "Trafikkfarlig kjøring",
        "term_th": "การขับรถอันตราย",
        "term_en": "Dangerous driving",
        "definition_no": "Kjøring som setter andres liv og sikkerhet i fare. Kan medføre tap av førerkort og fengselsstraff.",
        "definition_th": "การขับรถที่เป็นอันตรายต่อชีวิตและความปลอดภัยของผู้อื่น อาจส่งผลให้เพิกถอนใบขับขี่และโทษจำคุก",
        "definition_en": "Driving that endangers others' lives and safety. Can result in loss of driving licence and imprisonment.",
        "example_no": "Kjøring i ruspåvirket tilstand regnes alltid som trafikkfarlig.",
        "example_th": "การขับรถขณะเมาสุราถือเป็นการขับรถอันตรายเสมอ",
        "example_en": "Driving under the influence of alcohol is always considered dangerous driving.",
        "topic_tags": ["Sikkerhet", "Lov og regler"],
    },
]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = skipped = 0
    for t in TERMS:
        existing = await db.learning_glossary.find_one({"term_no": t["term_no"]})
        if existing:
            print(f"  SKIP: {t['term_no']}")
            skipped += 1
            continue
        doc = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
            **t,
        }
        await db.learning_glossary.insert_one(doc)
        print(f"  INSERT: {t['term_no']} / {t['term_th']}")
        inserted += 1
    print(f"\nDone — {inserted} inserted, {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
