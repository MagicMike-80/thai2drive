"""Top-up to reach 500 exactly (5 questions)."""
import asyncio, os, uuid
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
LETTERS = ["A", "B", "C", "D"]

def Q(no_q, th_q, en_q, opts, correct, diff, no_e, th_e, en_e):
    return {"q": {"no": no_q, "th": th_q, "en": en_q},
            "opts": [{"no": o[0], "th": o[1], "en": o[2]} for o in opts],
            "correct": LETTERS[correct], "difficulty": diff,
            "expl": {"no": no_e, "th": th_e, "en": en_e}}

DATA = [
Q("Hva er «defensiv kjøring»?", "\"การขับเชิงป้องกัน\" คือ?", "'Defensive driving' is?",
  [("Forutse feil fra andre og ha margin", "คาดการณ์และเผื่อระยะ", "Anticipate others' errors, have margin"),
   ("Kjøre raskest mulig", "เร็วสุด", "Fastest"),
   ("Ignorere regler", "ไม่สนกฎ", "Ignore rules"),
   ("Blokke trafikk", "กั้น", "Block")],
  0, "medium", "Tenk et skritt framfor.", "คิดล่วงหน้า", "Think one step ahead."),
Q("Hvor ofte må førerkort fornyes i Norge (vanlig klasse B)?", "ใบขับขี่ B ต่ออายุทุกกี่ปี?", "Class B license renewal in Norway?",
  [("Hvert 15. år (frem til 75 år)", "ทุก 15 ปี (ถึงอายุ 75)", "Every 15 years (until 75)"),
   ("Hvert år", "ทุกปี", "Yearly"),
   ("Aldri", "ไม่ต้อง", "Never"),
   ("Hvert 50. år", "50 ปี", "50 yr")],
  0, "hard", "Etter 75 år er det kortere intervall og legeerklæring.", "หลัง 75 ปีเข้มขึ้น", "After 75: shorter, med check."),
Q("Hva er \"øvelseskjøring\" i Norge?", "\"เรียนขับ\" ในนอร์เวย์คือ?", "'Practice driving' in Norway?",
  [("Lovlig med ledsager (min. 25 år + 5 år førerkort)", "ต้องมีผู้คุม (25+, มีใบ 5 ปี)", "With supervisor (25+, 5 yr license)"),
   ("Uten ledsager", "ไม่มีคุม", "No supervisor"),
   ("Kun på bane", "บนสนามเท่านั้น", "Track only"),
   ("Aldri", "ไม่ได้", "Never")],
  0, "medium", "Øvelsesmerke og ledsager på forsete.", "ติดป้าย+คนคุมข้างๆ", "Practice sign + supervisor front seat."),
Q("Hva betyr varsellys \"ABS\" på dashbordet?", "ไฟเตือน ABS?", "ABS warning light?",
  [("ABS-system ute av drift — bremser virker fortsatt", "ABS เสีย เบรกปกติ", "ABS off — brakes still work"),
   ("Tomt for olje", "น้ำมันหมด", "No oil"),
   ("Lite bensin", "น้ำมันน้อย", "Low fuel"),
   ("Alt ok", "ปกติ", "All good")],
  0, "medium", "Få kontrollert hos verksted snart.", "ไปเช็คอู่", "Get checked soon."),
Q("Hva er \"forkjørsvei\" definert av?", "\"ทางสายหลัก\" นิยามจาก?", "'Priority road' defined by?",
  [("Gult rombeskilt", "ป้ายข้าวหลามตัดเหลือง", "Yellow diamond sign"),
   ("Bred vei", "ถนนกว้าง", "Wide road"),
   ("Mange felt", "หลายเลน", "Many lanes"),
   ("Asfalt", "ยางมะตอย", "Asphalt")],
  0, "easy", "Gult rombeskilt = forkjørsrett.", "ป้ายเหลืองกลมๆ=สิทธิ์ก่อน", "Yellow diamond = priority."),
]

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    ins = skp = 0
    for r in DATA:
        if await db.questions.find_one({"question.no": r["q"]["no"].strip()}):
            skp += 1; continue
        doc = {"id": str(uuid.uuid4()), "question": r["q"],
               "options": [{"id": LETTERS[i], "text": r["opts"][i]} for i in range(4)],
               "correctOptionId": r["correct"], "explanation": r["expl"],
               "bildeUrl": None, "category": "Situations", "difficulty": r["difficulty"],
               "active": True, "schema_version": 2,
               "created_at": datetime.now(timezone.utc).isoformat(),
               "source": "Hand-crafted top-up"}
        await db.questions.insert_one(doc); ins += 1
    total = await db.questions.count_documents({})
    sit = await db.questions.count_documents({"category": "Situations"})
    print(f"Inserted: {ins}, Skipped: {skp}")
    print(f"TOTAL DB: {total}, Situations: {sit}")
    client.close()

asyncio.run(main())
