import os
import json
import re
import uuid
import sys
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env variables from backend/.env
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"WARNING: env file not found at {env_path}")
    load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "thai2drive")

if not MONGO_URL:
    print("ERROR: MONGO_URL environment variable is missing!")
    sys.exit(1)

THAI_CHAR_REGEX = re.compile(r"[\u0e00-\u0e7f]")
NORWEGIAN_CHAR_REGEX = re.compile(r"[æøåÆØÅ]")

def validate_language_purity(item, fields_prefix_list, item_desc=""):
    """
    Validates Language Purity rules for a given item:
    1. Check that all fields exist and are non-empty strings.
    2. Check that Norwegian (_no) and English (_en) fields contain NO Thai characters.
    3. Check that Thai (_th) fields DO contain Thai characters.
    4. Check that Thai (_th) fields contain NO Norwegian specific characters (æ, ø, å).
    5. Check that translations for the same prefix are not identical.
    """
    errors = []
    
    for prefix in fields_prefix_list:
        no_key = f"{prefix}_no"
        th_key = f"{prefix}_th"
        en_key = f"{prefix}_en"
        
        # 1. Existence and type/emptiness check
        for key in [no_key, th_key, en_key]:
            if key not in item:
                errors.append(f"Missing key: {key}")
                continue
            val = item[key]
            if not isinstance(val, str) or not val.strip():
                errors.append(f"Field {key} must be a non-empty string")
                continue
            
            # Clean/strip the value
            item[key] = val.strip()

        # If any of the keys were missing or empty, skip further regex checks for this prefix
        if any(k not in item or not isinstance(item[k], str) or not item[k].strip() for k in [no_key, th_key, en_key]):
            continue
            
        no_val = item[no_key]
        th_val = item[th_key]
        en_val = item[en_key]
        
        # 2. No Thai characters in Norwegian/English
        if THAI_CHAR_REGEX.search(no_val):
            errors.append(f"Norwegian field {no_key} contains Thai characters: '{no_val}'")
        if THAI_CHAR_REGEX.search(en_val):
            errors.append(f"English field {en_key} contains Thai characters: '{en_val}'")
            
        # 3. Thai fields must contain Thai characters
        if not THAI_CHAR_REGEX.search(th_val):
            errors.append(f"Thai field {th_key} must contain Thai characters: '{th_val}'")
            
        # 4. No Norwegian characters in Thai
        if NORWEGIAN_CHAR_REGEX.search(th_val):
            errors.append(f"Thai field {th_key} contains Norwegian characters: '{th_val}'")
            
        # 5. Distinct translations (no fallback)
        if no_val == th_val:
            errors.append(f"Norwegian and Thai translations are identical for prefix '{prefix}': '{no_val}'")
        if no_val == en_val:
            errors.append(f"Norwegian and English translations are identical for prefix '{prefix}': '{no_val}'")
        if th_val == en_val:
            errors.append(f"Thai and English translations are identical for prefix '{prefix}': '{th_val}'")

    if errors:
        print(f"  [VALIDATION FAILED] {item_desc}:")
        for err in errors:
            print(f"    - {err}")
        return False
    return True

def import_glossary(db):
    print("\n--- Starting Glossary Import ---")
    glossary_file = "new_glossary.json"
    if not os.path.exists(glossary_file):
        print(f"Glossary file {glossary_file} not found. Skipping.")
        return 0, 0, 0
        
    with open(glossary_file, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    print(f"Found {len(items)} items in {glossary_file}.")
    
    collection = db.learning_glossary
    inserted = 0
    updated = 0
    skipped = 0
    
    glossary_fields = ["term", "definition", "example"]
    
    for item in items:
        term_no = item.get("term_no", "Unknown")
        desc = f"Glossary Term: '{term_no}'"
        
        # Validate purity
        if not validate_language_purity(item, glossary_fields, desc):
            skipped += 1
            continue
            
        # Check if already exists in DB
        existing = collection.find_one({"term_no": item["term_no"]})
        
        if existing:
            # Upsert/Update the fields
            # Keep original metadata (id, created_at, active)
            update_data = {
                "term_no": item["term_no"],
                "term_th": item["term_th"],
                "term_en": item["term_en"],
                "definition_no": item["definition_no"],
                "definition_th": item["definition_th"],
                "definition_en": item["definition_en"],
                "example_no": item["example_no"],
                "example_th": item["example_th"],
                "example_en": item["example_en"],
                "active": existing.get("active", True),
                "topic_tags": item.get("topic_tags", existing.get("topic_tags", []))
            }
            collection.update_one({"_id": existing["_id"]}, {"$set": update_data})
            print(f"  [UPDATE] {desc}")
            updated += 1
        else:
            # Create new doc
            new_doc = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "active": True,
                "term_no": item["term_no"],
                "term_th": item["term_th"],
                "term_en": item["term_en"],
                "definition_no": item["definition_no"],
                "definition_th": item["definition_th"],
                "definition_en": item["definition_en"],
                "example_no": item["example_no"],
                "example_th": item["example_th"],
                "example_en": item["example_en"],
                "topic_tags": item.get("topic_tags", [])
            }
            collection.insert_one(new_doc)
            print(f"  [INSERT] {desc}")
            inserted += 1
            
    print(f"Glossary Import Summary: {inserted} inserted, {updated} updated, {skipped} skipped.")
    return inserted, updated, skipped

def import_podcasts(db):
    print("\n--- Starting Podcasts Import ---")
    podcasts_file = "new_podcasts.json"
    if not os.path.exists(podcasts_file):
        print(f"Podcasts file {podcasts_file} not found. Skipping.")
        return 0, 0, 0
        
    with open(podcasts_file, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    print(f"Found {len(items)} items in {podcasts_file}.")
    
    collection = db.learning_podcasts
    inserted = 0
    updated = 0
    skipped = 0
    
    podcast_fields = ["title", "instructor_summary"]
    
    for item in items:
        title_no = item.get("title_no", "Unknown")
        desc = f"Podcast Title: '{title_no}'"
        
        # Additional structure validation for podcasts
        errors = []
        if "duration_seconds" not in item or not isinstance(item["duration_seconds"], int) or item["duration_seconds"] <= 0:
            errors.append(f"Invalid duration_seconds: {item.get('duration_seconds')}")
        if "file_path" not in item or not isinstance(item["file_path"], str) or not item["file_path"].strip():
            errors.append(f"Invalid file_path: {item.get('file_path')}")
        if "topic_tags" not in item or not isinstance(item["topic_tags"], list):
            errors.append(f"Invalid topic_tags: {item.get('topic_tags')}")
            
        if errors:
            print(f"  [VALIDATION FAILED] {desc}:")
            for err in errors:
                print(f"    - {err}")
            skipped += 1
            continue
            
        # Validate purity
        if not validate_language_purity(item, podcast_fields, desc):
            skipped += 1
            continue
            
        # Check if already exists in DB
        existing = collection.find_one({"title_no": item["title_no"]})
        
        if existing:
            # Update existing podcast
            update_data = {
                "title_no": item["title_no"],
                "title_th": item["title_th"],
                "title_en": item["title_en"],
                "instructor_summary_no": item["instructor_summary_no"],
                "instructor_summary_th": item["instructor_summary_th"],
                "instructor_summary_en": item["instructor_summary_en"],
                "file_path": item["file_path"],
                "duration_seconds": item["duration_seconds"],
                "topic_tags": item["topic_tags"],
                "active": existing.get("active", True),
                "language": existing.get("language", "no"), # preserve language default if configured
                "sign_ids": existing.get("sign_ids", []),
                "sign_groups": existing.get("sign_groups", []),
                "studybook_section_ids": existing.get("studybook_section_ids", []),
                "see_context": existing.get("see_context", ""),
                "understand_context": existing.get("understand_context", ""),
                "choose_context": existing.get("choose_context", "")
            }
            collection.update_one({"_id": existing["_id"]}, {"$set": update_data})
            print(f"  [UPDATE] {desc}")
            updated += 1
        else:
            # Create new podcast
            new_doc = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "active": True,
                "title_no": item["title_no"],
                "title_th": item["title_th"],
                "title_en": item["title_en"],
                "instructor_summary_no": item["instructor_summary_no"],
                "instructor_summary_th": item["instructor_summary_th"],
                "instructor_summary_en": item["instructor_summary_en"],
                "file_path": item["file_path"],
                "duration_seconds": item["duration_seconds"],
                "topic_tags": item["topic_tags"],
                "language": "no",
                "sign_ids": [],
                "sign_groups": [],
                "studybook_section_ids": [],
                "see_context": "",
                "understand_context": "",
                "choose_context": ""
            }
            collection.insert_one(new_doc)
            print(f"  [INSERT] {desc}")
            inserted += 1
            
    print(f"Podcasts Import Summary: {inserted} inserted, {updated} updated, {skipped} skipped.")
    return inserted, updated, skipped

def main():
    print(f"Connecting to MongoDB...")
    # Clean output masking passwords in logging
    masked_url = re.sub(r":([^@/]+)@", ":******@", MONGO_URL)
    print(f"URL: {masked_url}")
    print(f"Database: {DB_NAME}")
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Test connection
        db.command("ping")
        print("MongoDB connection successful!")
        
        g_ins, g_upd, g_skp = import_glossary(db)
        p_ins, p_upd, p_skp = import_podcasts(db)
        
        print("\n==============================================")
        print("DATABASE IMPORT SUCCESSFULLY COMPLETED!")
        print(f"Total Glossary items: {g_ins} inserted, {g_upd} updated, {g_skp} skipped.")
        print(f"Total Podcast items: {p_ins} inserted, {p_upd} updated, {p_skp} skipped.")
        print("==============================================")
        
    except Exception as e:
        print(f"ERROR executing database import: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
