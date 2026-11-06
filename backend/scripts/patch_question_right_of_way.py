"""Faglig retting for vikeplikt-spørsmål e6b65e32-719d-4df5-bf69-ccae66e49746.

Rettes iht. Vegtrafikkloven og Trafikkreglene § 7 nr. 1 (Høyreregelen).
Fjerner feilaktig påstand om «vei med bedre standard» og oppdaterer
spørsmål, svaralternativer, fasit, pedagogisk forklaring og lovhenvisning.

Støtter:
  --apply: Skriver endringen til produksjons-MongoDB dersom MONGO_URL er satt.
  --local-only: Oppdaterer kun lokale JSON-auditfiler (all_questions.json osv.).
"""

import argparse
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

QUESTION_ID = "e6b65e32-719d-4df5-bf69-ccae66e49746"
BACKEND_DIR = Path(__file__).resolve().parents[1]

CORRECTED_DATA = {
    "question": {
        "no": "Du kjører bil A og skal svinge til høyre i krysset. Bil B kommer fra høyre og skal rett fram. Hva gjelder for vikeplikten?",
        "th": "คุณขับรถ A และกำลังจะเลี้ยวขวาที่ทางแยก รถ B มาจากทางขวาและจะตรงไป กฎการให้ทางเป็นอย่างไร?",
        "en": "You are driving car A and turning right at the intersection. Car B is coming from the right and going straight. What applies regarding right of way?"
    },
    "options": [
        {
            "id": "A",
            "text": {
                "no": "Jeg har vikeplikt for bil B fordi bil B kommer fra høyre (høyreregelen)",
                "th": "ฉันต้องให้ทางแก่รถ B เพราะรถ B มาจากทางขวา (กฎให้ทางขวา)",
                "en": "I must yield to car B because car B is coming from the right (right-hand rule)"
            }
        },
        {
            "id": "B",
            "text": {
                "no": "Bil B har vikeplikt for meg fordi jeg skal svinge til høyre",
                "th": "รถ B ต้องให้ทางแก่ฉันเพราะฉันกำลังจะเลี้ยวขวา",
                "en": "Car B must yield to me because I am turning right"
            }
        },
        {
            "id": "C",
            "text": {
                "no": "Jeg har forkjørsrett fordi jeg kommer først inn i krysset",
                "th": "ฉันมีสิทธิ์ไปก่อนเพราะมาถึงทางแยกก่อน",
                "en": "I have the right of way because I arrived at the intersection first"
            }
        },
        {
            "id": "D",
            "text": {
                "no": "Bil B har vikeplikt fordi veien jeg kjører på har bedre standard",
                "th": "รถ B ต้องให้ทางเพราะถนนที่ฉันขับมีมาตรฐานดีกว่า",
                "en": "Car B must yield because the road I am driving on has better standard"
            }
        }
    ],
    "correctOptionId": "A",
    "explanation": {
        "no": "I et kryss uten skilt gjelder alltid høyreregelen (trafikkreglene § 7 nr. 1). Siden bil B kommer fra din høyre side, har du vikeplikt for bil B. Husk: Veistandard eller veibredde gir aldri forkjørsrett med mindre veien er skiltet med forkjørsveiskilt!",
        "th": "ในทางแยกที่ไม่มีป้ายจราจร จะใช้กฎให้ทางขวาเสมอ (กฎจราจรมาตรา 7 ข้อ 1) เนื่องจากรถ B มาจากทางขวามือของคุณ คุณจึงต้องให้ทางแก่รถ B จำไว้ว่า: ขนาดหรือมาตรฐานถนนไม่เคยให้สิทธิ์ไปก่อน เว้นแต่จะมีป้ายทางเอกกำกับไว้!",
        "en": "In an intersection without signs, the right-hand rule always applies (Traffic Rules § 7 no. 1). Since car B comes from your right, you must yield to car B. Remember: Road standard or width never gives right of way unless marked with a priority road sign!"
    },
    "law_reference": "Trafikkreglene § 7 nr. 1",
    "validated": True,
    "validation_result": {
        "korrekt": True,
        "tillit": "høy",
        "kommentar": "Faglig revidert av Michael: Korrigert fra feilaktig påstand om veistandard (§ 7 nr. 4) til høyreregelen (§ 7 nr. 1)."
    }
}


def patch_local_json_files() -> int:
    """Oppdaterer lokale JSON-filer."""
    patched_count = 0
    files_to_check = [
        BACKEND_DIR / "scripts" / "image_audit" / "all_questions.json",
        BACKEND_DIR / "scripts" / "image_audit" / "image_questions.json",
    ]

    for file_path in files_to_check:
        if not file_path.is_file():
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            updated = False
            for q in data:
                if q.get("id") == QUESTION_ID:
                    for k, v in CORRECTED_DATA.items():
                        q[k] = v
                    updated = True
                    break

            if updated:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✅ Oppdaterte lokalt: {file_path.relative_to(BACKEND_DIR.parent)}")
                patched_count += 1
        except Exception as e:
            print(f"⚠️ Kunne ikke oppdatere {file_path}: {e}")

    return patched_count


def patch_mongodb(apply: bool = False) -> None:
    """Oppdaterer MongoDB Atlas."""
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "thai2drive")

    if not mongo_url:
        print("ℹ️ MONGO_URL er ikke satt i miljøet. Hoppet over direkte MongoDB-mutering.")
        print("   (Kjør via `railway run python backend/scripts/patch_question_right_of_way.py --apply` ved produksjonssetting).")
        return

    from pymongo import MongoClient

    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    collection = db.questions

    current = collection.find_one({"id": QUESTION_ID}, {"_id": 0, "question": 1, "correctOptionId": 1})
    if not current:
        raise LookupError(f"Fant ikke spørsmål {QUESTION_ID} i MongoDB!")

    print(f"Nåværende i DB: correctOptionId={current.get('correctOptionId')}")
    print(f"Spørsmål i DB: {current.get('question')}")

    if not apply:
        print("🔍 Dry-run: Ingen endringer skrevet til databasen. Bruk --apply for å lagre.")
        return

    update_fields = {
        "question": CORRECTED_DATA["question"],
        "options": CORRECTED_DATA["options"],
        "correctOptionId": CORRECTED_DATA["correctOptionId"],
        "explanation": CORRECTED_DATA["explanation"],
        "law_reference": CORRECTED_DATA["law_reference"],
        "validated": CORRECTED_DATA["validated"],
        "validation_result": CORRECTED_DATA["validation_result"],
    }

    result = collection.update_one({"id": QUESTION_ID}, {"$set": update_fields})
    if result.matched_count == 1:
        print(f"🎉 Vellykket! Spørsmål {QUESTION_ID} er nå rettet i MongoDB Atlas.")
    else:
        raise RuntimeError("Kunne ikke oppdatere spørsmålet i MongoDB.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Skriv endringer til MongoDB Atlas")
    parser.add_argument("--local-only", action="store_true", help="Oppdater kun lokale JSON-filer")
    args = parser.parse_args()

    print(f"--- Faglig retting for vikeplikt-spørsmål {QUESTION_ID} ---")
    patched = patch_local_json_files()
    print(f"Totalt {patched} lokale filer oppdatert.")

    if not args.local_only:
        patch_mongodb(apply=args.apply)


if __name__ == "__main__":
    main()
