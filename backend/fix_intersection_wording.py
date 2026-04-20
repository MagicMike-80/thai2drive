"""Fix unsignaled-intersection wording.

Replace vague "Høyreregel" / "Right-hand rule" with explicit:
NO: "Kjøretøy som kommer fra venstre har vikeplikt for kjøretøy som kommer fra høyre."
EN: "Vehicles coming from the left must yield to vehicles coming from the right."
TH: "รถที่มาจากทางซ้ายต้องให้ทางรถที่มาจากทางขวา"
"""
import asyncio, os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

RULE_NO = "Kjøretøy som kommer fra venstre har vikeplikt for kjøretøy som kommer fra høyre."
RULE_EN = "Vehicles coming from the left must yield to vehicles coming from the right."
RULE_TH = "รถที่มาจากทางซ้ายต้องให้ทางรถที่มาจากทางขวา"

# Map question IDs to full update definitions
UPDATES = {
    "f7bb4e74-6901-4072-a57e-0fd8f0d29e2e": {
        "question": {
            "no": "Hvem har vikeplikt i et kryss uten skilt?",
            "en": "Who must yield at an intersection with no signs?",
            "th": "แยกไม่มีป้าย ใครต้องให้ทาง?"
        },
        "options": [
            {"id": "A", "text": {"no": "Kjøretøy som kommer fra venstre", "en": "Vehicles coming from the left", "th": "รถที่มาจากทางซ้าย"}},
            {"id": "B", "text": {"no": "Kjøretøy som kommer fra høyre", "en": "Vehicles coming from the right", "th": "รถที่มาจากทางขวา"}},
            {"id": "C", "text": {"no": "Den som kommer først", "en": "Whoever arrives first", "th": "คนที่มาถึงก่อน"}},
            {"id": "D", "text": {"no": "Alle må stoppe", "en": "Everyone must stop", "th": "ทุกคนต้องหยุด"}},
        ],
        "correctOptionId": "A",
        "explanation": {"no": RULE_NO, "en": RULE_EN, "th": RULE_TH},
    },
    "a9002839-ed9d-4f43-9db9-bd4db175f23b": {
        "question": {
            "no": "I et T-kryss uten skilt – hvem har vikeplikt?",
            "en": "At a T-intersection with no signs — who yields?",
            "th": "ที่ทางแยกตัว T ไม่มีป้าย ใครต้องให้ทาง?"
        },
        "options": [
            {"id": "A", "text": {"no": "Kjøretøy som kommer fra venstre", "en": "Vehicles coming from the left", "th": "รถที่มาจากทางซ้าย"}},
            {"id": "B", "text": {"no": "Kjøretøy som kommer fra høyre", "en": "Vehicles coming from the right", "th": "รถที่มาจากทางขวา"}},
            {"id": "C", "text": {"no": "Den på gjennomgående vei", "en": "The one on the through road", "th": "คนที่อยู่บนถนนหลัก"}},
            {"id": "D", "text": {"no": "Den med størst bil", "en": "The one with the bigger car", "th": "คันใหญ่กว่า"}},
        ],
        "correctOptionId": "A",
        "explanation": {"no": RULE_NO, "en": RULE_EN, "th": RULE_TH},
    },
    "4ba9e858-0304-4f4b-9be5-666ebff45d82": {
        "question": {
            "no": "Du kjører mot et kryss uten skilt. En bil nærmer seg fra høyre. Hva gjør du?",
            "en": "Approaching an intersection with no signs. A car is coming from your right. What do you do?",
            "th": "เข้าใกล้แยกไม่มีป้าย รถมาจากทางขวา คุณทำอย่างไร?"
        },
        "options": [
            {"id": "A", "text": {"no": "Gi vikeplikt og la bilen fra høyre passere", "en": "Yield and let the car from the right go first", "th": "ให้ทางและให้รถจากทางขวาไปก่อน"}},
            {"id": "B", "text": {"no": "Kjøre først fordi du er nærmest", "en": "Go first because you are closest", "th": "ไปก่อนเพราะใกล้กว่า"}},
            {"id": "C", "text": {"no": "Bruke horn for å varsle", "en": "Honk to warn", "th": "บีบแตรเตือน"}},
            {"id": "D", "text": {"no": "Øke fart og kjøre gjennom", "en": "Speed up and drive through", "th": "เร่งและขับผ่าน"}},
        ],
        "correctOptionId": "A",
        "explanation": {"no": RULE_NO, "en": RULE_EN, "th": RULE_TH},
    },
    "b89d00f7-e553-4561-b390-037c5a1effd2": {
        "question": {
            "no": "I kryss uten skilt eller trafikklys, hva er hovedregelen?",
            "en": "At intersections without signs or traffic lights, what is the main rule?",
            "th": "ที่แยกไม่มีป้าย/ไฟจราจร กฎหลักคืออะไร?"
        },
        "options": [
            {"id": "A", "text": {"no": "Du har alltid forkjørsrett", "en": "You always have priority", "th": "คุณได้สิทธิ์เสมอ"}},
            {"id": "B", "text": {"no": "Kjøretøy fra venstre gir vikeplikt for kjøretøy fra høyre", "en": "Vehicles from the left yield to vehicles from the right", "th": "รถจากซ้ายต้องให้ทางรถจากขวา"}},
            {"id": "C", "text": {"no": "Raskeste bil går først", "en": "Fastest car goes first", "th": "คันที่เร็วสุดไปก่อน"}},
            {"id": "D", "text": {"no": "Største bil går først", "en": "Biggest car goes first", "th": "คันใหญ่สุดไปก่อน"}},
        ],
        "correctOptionId": "B",
        "explanation": {"no": RULE_NO, "en": RULE_EN, "th": RULE_TH},
    },
    "ae8f3500-18f0-4470-8fec-e3ee7b288e85": {
        "question": {
            "no": "Du har akkurat passert skiltet 'Forkjørsvei slutt'. Hva gjelder nå i neste kryss uten skilt?",
            "en": "You just passed the 'End of priority road' sign. What applies at the next intersection with no signs?",
            "th": "เพิ่งผ่านป้าย 'สิ้นสุดถนนสายหลัก' แยกต่อไปไม่มีป้าย ใช้กฎใด?"
        },
        "options": [
            {"id": "A", "text": {"no": "Du har fortsatt forkjørsrett", "en": "You still have priority", "th": "ยังมีสิทธิ์ก่อน"}},
            {"id": "B", "text": {"no": "Kjøretøy fra venstre gir vikeplikt for kjøretøy fra høyre", "en": "Vehicles from the left yield to vehicles from the right", "th": "รถจากซ้ายต้องให้ทางรถจากขวา"}},
            {"id": "C", "text": {"no": "Alle må stoppe fullstendig", "en": "Everyone must stop completely", "th": "ทุกคนต้องหยุดสนิท"}},
            {"id": "D", "text": {"no": "Venstre har alltid forkjørsrett", "en": "Left always has priority", "th": "ซ้ายมาก่อนเสมอ"}},
        ],
        "correctOptionId": "B",
        "explanation": {"no": RULE_NO, "en": RULE_EN, "th": RULE_TH},
    },
    "f9c2b90a-c0b5-48c9-adcc-faeef8abf4f1": {
        "question": {
            "no": "Hva er hovedregelen i kryss uten skilt?",
            "en": "What is the main rule at intersections with no signs?",
            "th": "กฎหลักในแยกไม่มีป้ายคืออะไร?"
        },
        "options": [
            {"id": "A", "text": {"no": "Kjøretøy fra høyre gir vikeplikt", "en": "Vehicles from the right yield", "th": "รถจากขวาให้ทาง"}},
            {"id": "B", "text": {"no": "Kjøretøy fra venstre gir vikeplikt for kjøretøy fra høyre", "en": "Vehicles from the left yield to vehicles from the right", "th": "รถจากซ้ายต้องให้ทางรถจากขวา"}},
            {"id": "C", "text": {"no": "Ingen regel gjelder", "en": "No rule applies", "th": "ไม่มีกฎ"}},
            {"id": "D", "text": {"no": "Alle må stoppe", "en": "Everyone stops", "th": "ทุกคนหยุด"}},
        ],
        "correctOptionId": "B",
        "explanation": {"no": RULE_NO, "en": RULE_EN, "th": RULE_TH},
    },
    "d4c1dc87-14ba-4073-9b5b-1980f73057bd": {
        "question": {
            "no": "To biler nærmer seg et kryss uten skilt samtidig. Hva gjelder?",
            "en": "Two cars reach an intersection without signs at the same time. What applies?",
            "th": "รถสองคันมาถึงแยกไม่มีป้ายพร้อมกัน ใช้กฎใด?"
        },
        "options": [
            {"id": "A", "text": {"no": "Bilen til venstre kjører først", "en": "The car on the left goes first", "th": "คันซ้ายไปก่อน"}},
            {"id": "B", "text": {"no": "Kjøretøyet fra venstre gir vikeplikt for kjøretøyet fra høyre", "en": "The vehicle from the left yields to the vehicle from the right", "th": "รถจากซ้ายให้ทางรถจากขวา"}},
            {"id": "C", "text": {"no": "Begge må stoppe helt", "en": "Both must stop completely", "th": "ทั้งคู่ต้องหยุด"}},
            {"id": "D", "text": {"no": "Raskeste bil kjører", "en": "The faster car goes", "th": "คันที่เร็วกว่าไป"}},
        ],
        "correctOptionId": "B",
        "explanation": {"no": RULE_NO, "en": RULE_EN, "th": RULE_TH},
    },
}


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    updated = 0
    for qid, patch in UPDATES.items():
        res = await db.questions.update_one({"id": qid}, {"$set": patch})
        if res.modified_count > 0:
            updated += 1
            print(f"✓ Updated {qid}")
        else:
            print(f"✗ Not found or unchanged: {qid}")

    # Verify: no more Norwegian-in-English-field bug & no "Høyreregel" in options/explanations
    print(f"\nTotal updated: {updated}/{len(UPDATES)}")

    # Count remaining vague wording
    remaining = await db.questions.count_documents(
        {
            "$or": [
                {"options.text.no": {"$regex": "^Høyreregel", "$options": "i"}},
                {"options.text.en": {"$regex": "^Right-hand rule$", "$options": "i"}},
                {"explanation.no": {"$regex": "^Høyreregel(en)?\\.?$", "$options": "i"}},
                {"explanation.en": {"$regex": "^Right-hand rule$", "$options": "i"}},
            ]
        }
    )
    print(f"Remaining vague 'Høyreregel'/'Right-hand rule' answers/explanations: {remaining}")

    # Double-check: all our fixed questions now use the consistent rule
    for qid in UPDATES.keys():
        doc = await db.questions.find_one({"id": qid})
        if doc:
            correct = next((o for o in doc["options"] if o["id"] == doc["correctOptionId"]), None)
            en_ans = correct["text"]["en"] if correct else "?"
            print(f"  [{qid[:8]}] correct = '{en_ans[:80]}'")

    client.close()


asyncio.run(main())
