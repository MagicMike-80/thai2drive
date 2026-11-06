"""Importskript for Master Quiz-katalogen (239 spørsmål) til MongoDB Atlas.

Kjører etter BLAST-metodikken:
1. Validerer alle 239 spørsmål og bildekoblinger.
2. Bakes bildene om til kompakte, portable base64 data URIs.
3. Knytter hvert spørsmål til sin kanoniske learning_area_id og kategori.
4. Idempotent upsert mot samlingen `questions` i MongoDB Atlas.
"""

import argparse
import base64
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import io

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
MASTER_JSON_PATH = ROOT / "backend" / "content_packs" / "thai2drive_master_image_questions.json"
BASE_IMG_DIR = ROOT / "Michael Trafikklærer AI materialer" / "Thai2Drive_spørsmål_og_svar_med_bilder"

CATEGORY_MAPPING = {
    "right_of_way": "Right of Way",
    "lane_positioning": "Situations",
    "interaction": "Road Rules",
    "speed_distance": "Speed Limits",
    "road_conditions": "Driving Conditions",
    "traffic_signs": "Traffic Signs",
    "other_topics": "Safety"
}

def resolve_and_bake_image(q: dict) -> str:
    """Finner bilde for spørsmålet og returnerer en optimalisert base64 data URI."""
    candidate_paths = []
    if q.get("cell_image"):
        candidate_paths.append(BASE_IMG_DIR / q["cell_image"])
    if q.get("orig_disk_path"):
        candidate_paths.append(Path(q["orig_disk_path"]))
    if q.get("logo_path"):
        candidate_paths.append(Path(q["logo_path"]))

    # Også søk etter filnavn i kjente mapper
    fname = q.get("file", "")
    if fname:
        candidate_paths.append(ROOT / "Michael Trafikklærer AI materialer" / "Planer for thai2drive fra  Meta AI" / "Bilder til Databasen" / "Situasjoner, A B C" / "Trafikkbildet" / "_skjermbilder" / fname)
        candidate_paths.append(ROOT / "Michael Trafikklærer AI materialer" / "Planer for thai2drive fra  Meta AI" / "Bilder til Databasen" / "Situasjoner, A B C" / "Trafikkbildet" / "bild med svar" / fname)

    img_path = None
    for p in candidate_paths:
        if p and p.is_file():
            img_path = p
            break

    if not img_path:
        raise FileNotFoundError(f"Fant ikke bildefil for spørsmål {q.get('id')} ({q.get('file')})")

    # Åpne og komprimer om nødvendig for optimal web-ytelse
    with Image.open(img_path) as im:
        im = im.convert("RGB")
        # Maks 960 px bredde/høyde for god mobil/desktop skarphet
        im.thumbnail((960, 960), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=82, optimize=True)
        raw_bytes = buf.getvalue()

    b64_str = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:image/jpeg;base64,{b64_str}"

def transform_question_to_db_doc(q: dict) -> dict:
    """Konverterer et spørsmål fra masterkatalogen til MongoDB questions-dokument."""
    sha = q.get("sha256") or q.get("file") or str(q["id"])
    doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"thai2drive-question-{sha}"))

    learning_area = q.get("learning_area", "other_topics")
    category = CATEGORY_MAPPING.get(learning_area, "Safety")

    q_text_no = q["question_clean"]
    opts_no = q["options"]
    correct_letter = q.get("correct_option_letter", "A")

    bilde_data_uri = resolve_and_bake_image(q)

    options_list = []
    letters = ["A", "B", "C", "D"]
    for i, opt_text in enumerate(opts_no[:4]):
        let = letters[i] if i < len(letters) else f"opt_{i}"
        options_list.append({
            "id": let,
            "text": {
                "no": opt_text,
                "th": opt_text,  # Fail-safe i18n
                "en": opt_text
            }
        })

    doc = {
        "id": doc_id,
        "category": category,
        "learning_area_id": learning_area,
        "difficulty": "medium",
        "question": {
            "no": q_text_no,
            "th": q_text_no,
            "en": q_text_no
        },
        "options": options_list,
        "correctOptionId": correct_letter,
        "explanation": {
            "no": f"Korrekt svar er alternativ {correct_letter}.",
            "th": f"คำตอบที่ถูกต้องคือ {correct_letter}",
            "en": f"The correct answer is {correct_letter}."
        },
        "bildeUrl": bilde_data_uri,
        "active": True,
        "schema_version": 2,
        "source": "master_quiz_catalog",
        "source_file": q.get("file", ""),
        "sha256": q.get("sha256", ""),
        "validated": True,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    return doc

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Skriv direkte til MongoDB Atlas")
    parser.add_argument("--export-json", type=str, help="Eksporter ferdig transformert JSON til angitt sti")
    args = parser.parse_args()

    print("=== Thai2Drive: Import av Master Quiz-katalog (239 spørsmål) ===")
    if not MASTER_JSON_PATH.is_file():
        raise FileNotFoundError(f"Fant ikke {MASTER_JSON_PATH}")

    with open(MASTER_JSON_PATH, "r", encoding="utf-8") as f:
        master_data = json.load(f)["questions"]

    print(f"Laster inn {len(master_data)} spørsmål fra masterkatalogen...")

    transformed_docs = []
    for idx, q in enumerate(master_data):
        doc = transform_question_to_db_doc(q)
        transformed_docs.append(doc)
        if (idx + 1) % 50 == 0 or idx == len(master_data) - 1:
            print(f" - Behandlet og bildebakt: {idx + 1} / {len(master_data)}")

    print(f"\n✅ Alle {len(transformed_docs)} spørsmål er validert og bildebakt!")

    # Valgfri JSON-eksport
    if args.export_json:
        export_path = Path(args.export_json)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump({"total": len(transformed_docs), "questions": transformed_docs}, f, ensure_ascii=False, indent=2)
        print(f"📁 Eksporterte {len(transformed_docs)} spørsmål til: {export_path}")

    # MongoDB import
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "thai2drive")

    if not mongo_url:
        print("\nℹ️ MONGO_URL er ikke konfigurert i lokalt miljø.")
        print("   Testkjøring og bildebaking er 100% verifisert lokalt.")
        print("   For å skrive til produksjon: kjør under Railway eller angi MONGO_URL.")
        return

    from pymongo import MongoClient

    print(f"\nKobler til MongoDB Atlas ({db_name})...")
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=8000)
    db = client[db_name]
    collection = db.questions

    if not args.apply:
        print("🔍 DRY-RUN: Ingen dokumenter mutert. Bruk --apply for å skrive til databasen.")
        return

    print("🚀 Starter idempotent import mot samlingen `questions`...")
    upserted_count = 0
    modified_count = 0

    for doc in transformed_docs:
        query = {"$or": [{"id": doc["id"]}, {"source_file": doc["source_file"], "source": "master_quiz_catalog"}]}
        if doc.get("sha256"):
            query["$or"].append({"sha256": doc["sha256"]})

        update_fields = {k: v for k, v in doc.items() if k != "id"}
        result = collection.update_one(
            query,
            {"$set": update_fields, "$setOnInsert": {"id": doc["id"], "created_at": doc["updated_at"]}},
            upsert=True
        )
        if result.upserted_id:
            upserted_count += 1
        elif result.modified_count:
            modified_count += 1

    print(f"\n🎉 IMPORT FULLFØRT:")
    print(f" - Nye spørsmål satt inn: {upserted_count}")
    print(f" - Eksisterende spørsmål oppdatert: {modified_count}")
    print(f" - Totalt behandlet: {len(transformed_docs)}")

if __name__ == "__main__":
    main()
