"""
seed_culture_lessons.py — fyller culture_lessons med de 5 «Thailand vs Norge»-leksjonene.

SAFE BY DEFAULT: dry-run som skriver ut hva som ville blitt lagt inn, og avslutter.
Pass --apply for å faktisk skrive. Idempotent — hopper over leksjoner som allerede
finnes (by id).

    cd thai2drive/backend && python scripts/seed_culture_lessons.py           # dry-run
    cd thai2drive/backend && python scripts/seed_culture_lessons.py --apply   # skriv
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

DB_NAME = "thai2drive"

LESSONS = [
    {
        "id": "cl_hoyreregelen",
        "order": 1,
        "category": "Vikeplikt",
        "title_th": "ใครไปก่อน? กฎ «รถทางขวา» ของนอร์เวย์",
        "title_no": "Høyreregelen",
        "thailand_practice_th": "ที่ไทยเราขับชิดซ้าย และมักถือว่า «ถนนใหญ่ไปก่อน» ที่สี่แยกเล็ก ๆ ที่ไม่มีป้าย เรามักกะกันเองว่าใครจะไปก่อน",
        "norway_rule_th": "ที่นอร์เวย์ขับชิดขวา ถ้าสี่แยกไม่มีป้าย ไม่มีไฟจราจร และไม่ใช่ถนนหลัก คุณต้อง «ให้ทางรถที่มาจากทางขวาของคุณ» เสมอ นี่คือกฎพื้นฐานที่เรียกว่า Høyreregelen ป้าย ไฟจราจร ตำรวจ และป้ายถนนหลัก (skilt 202/204/220) จะยกเลิกกฎนี้",
        "norway_term_no": "Høyreregelen – vikeplikt for trafikk fra høyre",
        "michaels_tip_th": "เมื่อเข้าสี่แยกที่ไม่มีป้าย ให้ชะลอความเร็ว แล้วมองไปทางขวาก่อนเสมอ ถ้ามีรถมาจากขวา ให้รอ ใจเย็น ๆ การรอสองวินาทีปลอดภัยกว่าการเดา",
    },
    {
        "id": "cl_gangfelt_hav",
        "order": 2,
        "category": "Gangfelt",
        "title_th": "ทางม้าลาย: ให้ทางคนเดินเท้า + หลัก «HAV»",
        "title_no": "Vikeplikt ved gangfelt · HAV-regelen (§ 3)",
        "thailand_practice_th": "ที่ไทย รถมักไม่หยุดให้คนข้ามทางม้าลาย คนเดินเท้าต้องคอยจังหวะและระวังเอง",
        "norway_rule_th": "ที่นอร์เวย์ ตรงทางม้าลายที่ไม่มีไฟหรือตำรวจ คนขับ «ต้องให้ทาง» คนที่อยู่บนทางม้าลายหรือกำลังจะก้าวลงมา (trafikkreglene § 9) ไมเคิลใช้หลัก «HAV» จากกฎพื้นฐาน vegtrafikkloven § 3 เป็นตัวช่วยจำ: H – Hensynsfull (คำนึงถึงผู้อื่น), A – Aktpågivende (ตั้งใจสังเกตรอบตัว), V – Varsom (ระมัดระวัง) ถ้าขับแบบ HAV คุณจะชะลอและพร้อมหยุดให้คนข้ามเองโดยธรรมชาติ ห้ามแซงรถที่จอดอยู่หน้าทางม้าลาย และห้ามจอดบนทางม้าลายหรือใกล้กว่า 5 เมตร",
        "norway_term_no": "Gangfelt · vikeplikt for gående (trafikkreglene § 9) · grunnregelen HAV: Hensynsfull, Aktpågivende, Varsom (vegtrafikkloven § 3)",
        "michaels_tip_th": "จำสามคำนี้ไว้ทุกครั้งที่ขับ: Hensynsfull, Aktpågivende, Varsom เห็นคนยืนใกล้ทางม้าลายให้คิดไว้ก่อนว่าเขาจะข้าม ชะลอ พร้อมหยุด และสบตากับเขาเพื่อให้เขารู้ว่าคุณเห็นแล้ว",
    },
    {
        "id": "cl_rundkjoring",
        "order": 3,
        "category": "Rundkjøring",
        "title_th": "วงเวียนแบบนอร์เวย์: ให้ทางตอนเข้า + อยู่เลนให้ถูก",
        "title_no": "Rundkjøring",
        "thailand_practice_th": "ที่ไทย กฎวงเวียนไม่ชัดเจน บางวงเวียนรถที่อยู่ในวงเวียนต้องให้ทางรถที่เข้ามา และหลายคนไม่ค่อยเปิดไฟเลี้ยว",
        "norway_rule_th": "ที่นอร์เวย์ รถที่จะ «เข้า» วงเวียนต้องให้ทางรถที่อยู่ในวงเวียนแล้วเสมอ (vikeplikt) การจัดเลน: ออกทางแรก/เลี้ยวขวา – ใช้เลนขวา เปิดไฟขวาตลอด; ตรงไป – ปกติใช้เลนขวา ไม่ต้องเปิดไฟตอนเข้า; ไปครึ่งวงหรือมากกว่า – ใช้เลนซ้าย เปิดไฟซ้ายตอนเข้า แล้วเปลี่ยนเป็นไฟขวาเมื่อผ่านทางออกก่อนหน้าทางที่จะออก ต้องเปิดไฟขวาก่อนออกจากวงเวียนทุกครั้ง ระวังจักรยานและรถใหญ่ที่ต้องใช้สองเลน",
        "norway_term_no": "Rundkjøring · vikeplikt ved innkjøring · plassering og tegn",
        "michaels_tip_th": "ก่อนถึงวงเวียน มองซ้ายเพื่อดูรถในวงเวียน ชะลอ ถ้ามีรถมาให้รอ เลือกเลนตั้งแต่เนิ่น ๆ ตามทางออกที่จะไป และอย่าลืมเปิดไฟขวาก่อนออกทุกครั้ง",
    },
    {
        "id": "cl_vinter_bremselengde",
        "order": 4,
        "category": "Sikkerhet",
        "title_th": "หน้าหนาวและถนนลื่น: ระยะเบรกยาวขึ้นมาก",
        "title_no": "Bremselengde på vinterføre",
        "thailand_practice_th": "ที่ไทยไม่มีหิมะหรือน้ำแข็ง สิ่งที่ต้องระวังคือฝนและน้ำท่วม แต่หลายคนก็ยังขับเร็วเท่าเดิมตอนฝนตก",
        "norway_rule_th": "ที่นอร์เวย์ ถนนที่มีน้ำแข็งหรือหิมะทำให้ «ระยะเบรก» (bremselengde) ยาวขึ้น 3–10 เท่า กฎหมาย (vegtrafikkloven § 6) บอกว่าต้องปรับความเร็วตามสภาพถนน แสง ทัศนวิสัย และการจราจร เพิ่มระยะห่างจากรถคันหน้า (จาก 3 วินาที เป็นมากกว่านั้นมาก) และต้องใช้ยางฤดูหนาว (vinterdekk) เมื่อถนนเป็นน้ำแข็ง/หิมะ จำไว้ว่าระยะเบรกเพิ่มตามกำลังสองของความเร็ว ความเร็วสองเท่า = ระยะเบรกสี่เท่า",
        "norway_term_no": "Bremselengde · stoppelengde · sikkerhetsavstand · vinterdekk",
        "michaels_tip_th": "ถ้าถนนดูมันวาวหรือมีหิมะ ให้ลดความเร็วและทิ้งระยะห่างเยอะ ๆ เบรกเบา ๆ แต่เนิ่น ๆ ถ้าไม่แน่ใจ ให้ขับช้าลงอีก",
    },
    {
        "id": "cl_promille",
        "order": 5,
        "category": "Lov og regler",
        "title_th": "เมาแล้วขับ: นอร์เวย์จำกัดที่ 0,2 (เข้มกว่าไทยมาก)",
        "title_no": "Promillegrense 0,2",
        "thailand_practice_th": "ที่ไทย ระดับแอลกอฮอล์ในเลือดที่กฎหมายยอมให้คือ 0,5 (50 มก.%) และการตรวจจับก็ไม่สม่ำเสมอ",
        "norway_rule_th": "ที่นอร์เวย์ ระดับที่ยอมให้คือ «0,2» เท่านั้น ต่ำกว่าไทยมาก แค่ดื่มนิดเดียวก็ทำให้ «เวลาตอบสนอง» (reaksjonstid ปกติราว 1 วินาที) ช้าลงและการตัดสินใจแย่ลง โทษหนักมาก: เสียใบขับขี่ ปรับเงินตามรายได้ และอาจติดคุก ข้อจำกัดนี้ใช้กับยาบางชนิดและสารเสพติดด้วย ทางที่ปลอดภัยคือ «ดื่ม = ไม่ขับ»",
        "norway_term_no": "Promillegrense (0,2 ‰) · reaksjonstid · reaksjonsstrekning",
        "michaels_tip_th": "ถ้าคืนนี้จะดื่ม วางแผนกลับบ้านด้วยวิธีอื่นไว้เลย และจำไว้ว่าแอลกอฮอล์จากเมื่อคืนอาจยังอยู่ในเลือดตอนเช้า ถ้าไม่แน่ใจ อย่าขับ",
    },
]


def _mongo_url() -> str:
    url = os.environ.get("MONGO_URL", "")
    if not url:
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("MONGO_URL="):
                        url = line.split("=", 1)[1].strip('"').strip("'")
                        break
    if not url:
        raise RuntimeError("MONGO_URL not found in environment or .env")
    return url


async def main(apply: bool) -> None:
    client = AsyncIOMotorClient(_mongo_url())
    db = client[DB_NAME]
    inserted = skipped = 0
    try:
        for lesson in LESSONS:
            existing = await db.culture_lessons.find_one({"id": lesson["id"]})
            if existing:
                print(f"  SKIP: {lesson['id']} (finnes allerede)")
                skipped += 1
                continue
            if not apply:
                print(f"  WOULD INSERT: {lesson['id']} / {lesson['title_no']}")
                inserted += 1
                continue
            doc = {
                **lesson,
                "active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await db.culture_lessons.insert_one(doc)
            print(f"  INSERT: {lesson['id']} / {lesson['title_no']}")
            inserted += 1
        verb = "ville blitt lagt inn" if not apply else "lagt inn"
        print(f"\nFerdig — {inserted} {verb}, {skipped} hoppet over.")
        if not apply:
            print("Kjør på nytt med --apply for å skrive.")
    finally:
        client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main(apply="--apply" in sys.argv[1:]))
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print("Sett MONGO_URL (eller legg den i backend/.env) og kjør fra backend-miljøet.")
        sys.exit(1)
