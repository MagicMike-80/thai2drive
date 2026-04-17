"""Seed 10 new questions (v2 schema) from JSON batch."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

# Map Norwegian category names to English
CAT_MAP = {
    "Vikeplikt": "Right of Way",
    "Sikkerhet": "Safety",
    "Veimerking": "Road Rules",
    "Fareskilt": "Traffic Signs",
    "Trafikklys": "Road Rules",
    "Forbikjøring": "Road Rules",
    "Motorvei": "Safety",
    "Samhandling": "Safety",
    "Kjøretøy": "Safety",
    "Lover og regler": "Road Rules",
}

NEW_QUESTIONS = [
    {
        "sporsmal": "Hva er riktig å anta etter dette skiltet?",
        "alternativA": "Jeg kjører nå på en forkjørsvei",
        "alternativB": "I neste kryss vil trafikk fra høyre få vikeplikt for meg",
        "alternativC": "Jeg får kun vikeplikt for trafikk fra venstre",
        "alternativD": "I neste kryss vil jeg få vikeplikt fra høyre",
        "riktigSvar": "D",
        "forklaring": "Skiltet viser slutt på forkjørsvei. Høyreregelen gjelder.",
        "kategori": "Vikeplikt",
        "difficulty": "medium"
    },
    {
        "sporsmal": "Hva menes med aktiv sikkerhet?",
        "alternativA": "Å kjøre med ekstra gode marginer",
        "alternativB": "Bilens beskyttende konstruksjoner",
        "alternativC": "Bilens hjelpesystemer som ABS og ESP",
        "alternativD": "Din evne til å vurdere risiko",
        "riktigSvar": "C",
        "forklaring": "Aktiv sikkerhet hjelper deg å unngå ulykker.",
        "kategori": "Sikkerhet",
        "difficulty": "easy"
    },
    {
        "sporsmal": "Hva betyr det når kantlinjen er stiplet? (smal vei)",
        "alternativA": "Veien er ikke forkjørsvei",
        "alternativB": "Forbikjøring er forbudt",
        "alternativC": "Kjørebanen er smal",
        "alternativD": "Ingen møtende trafikk",
        "riktigSvar": "C",
        "forklaring": "Stiplet kantlinje betyr ofte smal vei.",
        "kategori": "Veimerking",
        "difficulty": "medium"
    },
    {
        "sporsmal": "Hva varsler dette skiltet? (sporete vei)",
        "alternativA": "Sporete vei",
        "alternativB": "Glatt kjørebane",
        "alternativC": "Ujevn vei",
        "alternativD": "Farlige svinger",
        "riktigSvar": "B",
        "forklaring": "Varsler fare for glatt vei.",
        "kategori": "Fareskilt",
        "difficulty": "easy"
    },
    {
        "sporsmal": "Du skal rett frem i krysset. Hva gjør du?",
        "alternativA": "Kjører siden det snart blir grønt",
        "alternativB": "Venter siden det snart blir rødt",
        "alternativC": "Kjører på gult lys",
        "alternativD": "Gjør deg klar til å kjøre",
        "riktigSvar": "D",
        "forklaring": "Gult og rødt betyr at grønt kommer.",
        "kategori": "Trafikklys",
        "difficulty": "easy"
    },
    {
        "sporsmal": "Hva må du sjekke før forbikjøring?",
        "alternativA": "At ingen bak deg har startet forbikjøring",
        "alternativB": "At det ikke er fotobokser",
        "alternativC": "At du har riktig gir",
        "alternativD": "At bilen foran kjører sakte",
        "riktigSvar": "A",
        "forklaring": "Du må sjekke speil og blindsone.",
        "kategori": "Forbikjøring",
        "difficulty": "easy"
    },
    {
        "sporsmal": "Hva er riktig om havarilommer? (nødstopp)",
        "alternativA": "Kun for utrykningskjøretøy",
        "alternativB": "Kan brukes til pause",
        "alternativC": "Kan brukes for å slippe kø",
        "alternativD": "Kun til nødstopp",
        "riktigSvar": "D",
        "forklaring": "Kun ved nød.",
        "kategori": "Motorvei",
        "difficulty": "easy"
    },
    {
        "sporsmal": "Hva er riktig om store kjøretøy?",
        "alternativA": "De bør alltid slippes frem",
        "alternativB": "De har kort bremselengde",
        "alternativC": "Det blir færre av dem",
        "alternativD": "De har stor blindsone",
        "riktigSvar": "D",
        "forklaring": "Store kjøretøy har store blindsoner.",
        "kategori": "Samhandling",
        "difficulty": "easy"
    },
    {
        "sporsmal": "Hva betyr forskriftsmessig stand?",
        "alternativA": "EU-kontroll siste år",
        "alternativB": "Kasko forsikring",
        "alternativC": "Ny teknologi",
        "alternativD": "Alt teknisk er i orden",
        "riktigSvar": "D",
        "forklaring": "Bilen må være teknisk i orden.",
        "kategori": "Kjøretøy",
        "difficulty": "easy"
    },
    {
        "sporsmal": "Kan du straffes for å kjøre forbi et ulykkessted uten å stoppe? (hjelpeplikt)",
        "alternativA": "Ja, men bare hvis du er involvert",
        "alternativB": "Nei, hvis du ikke tåler blod",
        "alternativC": "Ja, du må sjekke om hjelp trengs",
        "alternativD": "Nei, hvis andre er der",
        "riktigSvar": "C",
        "forklaring": "Du har hjelpeplikt.",
        "kategori": "Lover og regler",
        "difficulty": "medium"
    },
]

# Thai translations for each question
THAI = [
    {"q": "ข้อใดถูกต้องหลังเห็นป้ายนี้?", "a": "ฉันขับบนถนนหลัก", "b": "ที่แยกถัดไปรถจากขวาต้องให้ทาง", "c": "ฉันต้องให้ทางเฉพาะรถจากซ้าย", "d": "ที่แยกถัดไปฉันต้องให้ทางรถจากขวา", "e": "ป้ายแสดงสิ้นสุดถนนหลัก ใช้กฎให้ทางขวา"},
    {"q": "ความปลอดภัยเชิงรุกหมายถึงอะไร?", "a": "ขับด้วยระยะห่างพิเศษ", "b": "โครงสร้างป้องกันของรถ", "c": "ระบบช่วยเหลือ เช่น ABS และ ESP", "d": "ความสามารถในการประเมินความเสี่ยง", "e": "ความปลอดภัยเชิงรุกช่วยหลีกเลี่ยงอุบัติเหตุ"},
    {"q": "เส้นประข้างทางหมายถึงอะไร? (ถนนแคบ)", "a": "ไม่ใช่ถนนหลัก", "b": "ห้ามแซง", "c": "ถนนแคบ", "d": "ไม่มีรถสวนทาง", "e": "เส้นประข้างทางมักหมายถึงถนนแคบ"},
    {"q": "ป้ายนี้เตือนอะไร? (ถนนมีร่อง)", "a": "ถนนมีร่อง", "b": "ถนนลื่น", "c": "ถนนไม่เรียบ", "d": "โค้งอันตราย", "e": "เตือนอันตรายถนนลื่น"},
    {"q": "คุณจะขับตรงไปที่สี่แยก จะทำอย่างไร?", "a": "ขับเพราะจะเป็นไฟเขียวเร็วๆ นี้", "b": "รอเพราะจะเป็นไฟแดงเร็วๆ นี้", "c": "ขับตอนไฟเหลือง", "d": "เตรียมตัวขับ", "e": "ไฟเหลืองกับแดงหมายถึงไฟเขียวกำลังจะมา"},
    {"q": "ต้องตรวจสอบอะไรก่อนแซง?", "a": "ว่าไม่มีรถข้างหลังกำลังแซง", "b": "ว่าไม่มีกล้องจับความเร็ว", "c": "ว่าเข้าเกียร์ถูก", "d": "ว่ารถคันหน้าขับช้า", "e": "ต้องเช็คกระจกและจุดบอด"},
    {"q": "ข้อใดถูกต้องเกี่ยวกับช่องจอดฉุกเฉิน? (จอดฉุกเฉิน)", "a": "สำหรับรถฉุกเฉินเท่านั้น", "b": "ใช้พักได้", "c": "ใช้หลบรถติดได้", "d": "สำหรับจอดฉุกเฉินเท่านั้น", "e": "ใช้เฉพาะกรณีฉุกเฉิน"},
    {"q": "ข้อใดถูกต้องเกี่ยวกับรถขนาดใหญ่?", "a": "ควรให้ไปก่อนเสมอ", "b": "มีระยะเบรกสั้น", "c": "จะมีน้อยลง", "d": "มีจุดบอดขนาดใหญ่", "e": "รถขนาดใหญ่มีจุดบอดมาก"},
    {"q": "สภาพตามกฎหมายหมายถึงอะไร?", "a": "ตรวจ EU ปีล่าสุด", "b": "ประกันชั้น 1", "c": "เทคโนโลยีใหม่", "d": "ทุกอย่างทางเทคนิคเรียบร้อย", "e": "รถต้องอยู่ในสภาพทางเทคนิคที่ดี"},
    {"q": "จะถูกลงโทษไหมถ้าขับผ่านที่เกิดเหตุโดยไม่หยุด? (หน้าที่ช่วยเหลือ)", "a": "ใช่ แต่เฉพาะถ้ามีส่วนเกี่ยวข้อง", "b": "ไม่ ถ้าทนเห็นเลือดไม่ได้", "c": "ใช่ ต้องตรวจสอบว่าต้องการความช่วยเหลือ", "d": "ไม่ ถ้ามีคนอื่นอยู่แล้ว", "e": "คุณมีหน้าที่ต้องช่วยเหลือ"},
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0

    for i, q in enumerate(NEW_QUESTIONS):
        th = THAI[i]
        cat = CAT_MAP.get(q["kategori"], "Road Rules")

        doc = {
            "id": str(uuid.uuid4()),
            "question": {
                "no": q["sporsmal"],
                "th": th["q"],
                "en": q["sporsmal"],  # Use NO as EN fallback
            },
            "options": [
                {"id": "A", "text": {"no": q["alternativA"], "th": th["a"], "en": q["alternativA"]}},
                {"id": "B", "text": {"no": q["alternativB"], "th": th["b"], "en": q["alternativB"]}},
                {"id": "C", "text": {"no": q["alternativC"], "th": th["c"], "en": q["alternativC"]}},
                {"id": "D", "text": {"no": q["alternativD"], "th": th["d"], "en": q["alternativD"]}},
            ],
            "correctOptionId": q["riktigSvar"],
            "explanation": {
                "no": q["forklaring"],
                "th": th["e"],
                "en": q["forklaring"],
            },
            "bildeUrl": None,
            "category": cat,
            "difficulty": q["difficulty"],
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        existing = await db.questions.find_one({"question.no": q["sporsmal"]})
        if existing:
            skipped += 1
            continue
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Done! Inserted: {inserted}, Skipped (duplicates): {skipped}")
    total = await db.questions.count_documents({})
    print(f"Total questions in database: {total}")
    client.close()

asyncio.run(seed())
