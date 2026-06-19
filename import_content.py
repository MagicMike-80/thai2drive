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
    glossary_file = os.path.join("content", "new_glossary.json")
    if not os.path.exists(glossary_file):
        glossary_file = "new_glossary.json"
        if not os.path.exists(glossary_file):
            print(f"Glossary file {glossary_file} not found. Skipping.")
            return 0, 0, 0
        
    with open(glossary_file, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    print(f"Found {len(items)} items in {glossary_file}.")
    
    collection = db.learning_glossary
    collection_terms = db.glossary_terms
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
            collection_terms.update_one({"term_no": item["term_no"]}, {"$set": update_data}, upsert=True)
            print(f"  [UPDATE - learning_glossary & glossary_terms] {desc}")
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
            new_doc_copy = new_doc.copy()
            new_doc_copy.pop("_id", None)
            collection_terms.insert_one(new_doc_copy)
            print(f"  [INSERT - learning_glossary & glossary_terms] {desc}")
            inserted += 1
            
    print(f"Glossary Import Summary: {inserted} inserted, {updated} updated, {skipped} skipped.")
    return inserted, updated, skipped

def import_podcasts(db):
    print("\n--- Starting Podcasts Import ---")
    podcasts_file = os.path.join("content", "new_podcasts.json")
    if not os.path.exists(podcasts_file):
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

def import_quizzes(db):
    print("\n--- Starting Quizzes/Questions Import ---")
    quiz_files = ["quiz_michael_v5.json", "quiz_extended_practice.json"]
    total_inserted = 0
    total_updated = 0
    total_skipped = 0
    
    letters = ["A", "B", "C", "D"]
    
    for filename in quiz_files:
        quizzes_file = os.path.join("content", filename)
        if not os.path.exists(quizzes_file):
            quizzes_file = filename
            if not os.path.exists(quizzes_file):
                print(f"Quizzes file {filename} not found in content/ or root. Skipping.")
                continue
            
        print(f"\nProcessing {filename}...")
        with open(quizzes_file, "r", encoding="utf-8") as f:
            items = json.load(f)
            
        print(f"Found {len(items)} items in {filename}.")
        
        quizzes_coll = db.learning_quizzes
        questions_coll = db.questions
        
        for item in items:
            question_no = item.get("question_no", "Unknown")
            desc = f"Quiz Question: '{question_no[:40]}...'"
            
            # 1. Structural checks
            errors = []
            if "options" not in item or not isinstance(item["options"], list) or len(item["options"]) == 0:
                errors.append("Missing or invalid options list")
            if "difficulty" not in item:
                errors.append("Missing difficulty")
                
            if errors:
                print(f"  [VALIDATION FAILED] {desc}:")
                for err in errors:
                    print(f"    - {err}")
                total_skipped += 1
                continue
                
            # 2. Purity check for question text and explanation
            if not validate_language_purity(item, ["question", "explanation"], desc):
                total_skipped += 1
                continue
                
            # 3. Purity check for each option
            options_valid = True
            for idx, opt in enumerate(item["options"]):
                opt_desc = f"{desc} - Option {idx+1}"
                if not validate_language_purity(opt, ["text"], opt_desc):
                    options_valid = False
                    break
            if not options_valid:
                total_skipped += 1
                continue
                
            # Check if there is exactly one correct answer
            correct_indices = [idx for idx, opt in enumerate(item["options"]) if opt.get("correct") is True]
            if len(correct_indices) != 1:
                print(f"  [VALIDATION FAILED] {desc}: Must have exactly one correct option, found {len(correct_indices)}")
                total_skipped += 1
                continue
                
            correct_idx = correct_indices[0]
            correct_letter = letters[correct_idx]
            
            # --- A. Write to learning_quizzes (raw collection, exact copy with id, created_at, active) ---
            existing_quiz = quizzes_coll.find_one({"question_no": item["question_no"]})
            if existing_quiz:
                update_data = {
                    **item,
                    "active": existing_quiz.get("active", True)
                }
                quizzes_coll.update_one({"_id": existing_quiz["_id"]}, {"$set": update_data})
                print(f"  [UPDATE - learning_quizzes] {desc}")
            else:
                new_quiz = {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "active": True,
                    **item
                }
                quizzes_coll.insert_one(new_quiz)
                print(f"  [INSERT - learning_quizzes] {desc}")
                
            # --- B. Write to questions (main quiz collection, formatted to V2 nested schema) ---
            # Map category based on topic tags
            topic_tags = [t.lower() for t in item.get("topic_tags", [])]
            category = "Situations"
            if any(t in topic_tags for t in ["vikeplikt", "kryss", "sving", "rundkjøring"]):
                category = "Right of Way"
            elif any(t in topic_tags for t in ["fart", "bremselengde", "reaktidslengde", "stopplengde"]):
                category = "Speed Limits"
            elif any(t in topic_tags for t in ["myndighet", "regler", "politi"]):
                category = "Road Rules"
            
            # Construct V2 document
            options_formatted = []
            for idx, opt in enumerate(item["options"]):
                options_formatted.append({
                    "id": letters[idx],
                    "text": {
                        "no": opt["text_no"],
                        "th": opt["text_th"],
                        "en": opt["text_en"]
                    }
                })
                
            v2_doc = {
                "question": {
                    "no": item["question_no"],
                    "th": item["question_th"],
                    "en": item["question_en"]
                },
                "options": options_formatted,
                "correctOptionId": correct_letter,
                "explanation": {
                    "no": item["explanation_no"],
                    "th": item["explanation_th"],
                    "en": item["explanation_en"]
                },
                "category": category,
                "difficulty": item["difficulty"],
                "topic_tags": item.get("topic_tags", []),
                "podcast_reference": item.get("podcast_reference", ""),
                "schema_version": 2
            }
            
            existing_question = questions_coll.find_one({"question.no": item["question_no"]})
            if existing_question:
                update_q = {
                    **v2_doc,
                    "active": existing_question.get("active", True)
                }
                questions_coll.update_one({"_id": existing_question["_id"]}, {"$set": update_q})
                print(f"  [UPDATE - questions] {desc}")
                total_updated += 1
            else:
                new_q = {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "active": True,
                    **v2_doc
                }
                questions_coll.insert_one(new_q)
                print(f"  [INSERT - questions] {desc}")
                total_inserted += 1
                
    print(f"Quizzes Import Summary: {total_inserted} inserted, {total_updated} updated, {total_skipped} skipped.")
    return total_inserted, total_updated, total_skipped

def import_studybook_chapters(db):
    print("\n--- Starting Studybook Chapters Import ---")
    chapters_file = os.path.join("content", "studybook_chapters_v5.json")
    if not os.path.exists(chapters_file):
        chapters_file = "studybook_chapters_v5.json"
        if not os.path.exists(chapters_file):
            print("Studybook chapters file studybook_chapters_v5.json not found in content/ or root. Skipping.")
            return 0, 0, 0
            
    with open(chapters_file, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    print(f"Found {len(items)} items in {chapters_file}.")
    
    studiebok_coll = db.studiebok_chapters
    studybook_coll = db.studybook_chapters
    chapters_coll = db.chapters
    
    inserted = 0
    updated = 0
    skipped = 0
    
    emoji_map = {
        "ch_right_of_way_1": "🚦",
        "ch_straight_vs_turn": "🔄",
        "ch_speed_braking": "⏱️",
        "ch_authority_pyramid": "👑",
        "ch_thailand_norway_culture": "🌏"
    }
    
    for item in items:
        chapter_id = item.get("chapter_id", "")
        title_no = item.get("title_no", "Unknown")
        desc = f"Chapter: '{title_no[:40]}...'"
        
        # 1. Structural check
        if not chapter_id or "sections" not in item or not isinstance(item["sections"], list) or len(item["sections"]) == 0:
            print(f"  [VALIDATION FAILED] {desc}: Missing chapter_id or valid sections list.")
            skipped += 1
            continue
            
        # 2. Language validation of chapter headers
        if not validate_language_purity(item, ["title"], desc):
            skipped += 1
            continue
            
        # 3. Language validation for sections
        sections_valid = True
        for idx, sec in enumerate(item["sections"]):
            sec_desc = f"{desc} - Section {idx+1}"
            if not validate_language_purity(sec, ["title", "content"], sec_desc):
                sections_valid = False
                break
        if not sections_valid:
            skipped += 1
            continue

        # Determine order and metadata
        order_num = item.get("order", 1)
        chapter_num = order_num + 6
        icon = emoji_map.get(chapter_id, "📖")
        
        # Format HTML content for studiebok_chapters (webapp)
        content_html_no = ""
        content_html_th = ""
        content_html_en = ""
        
        for sec in item["sections"]:
            sec_type = sec.get("section_type", "theory").lower()
            
            if sec_type == "situation":
                content_html_no += f'<p><strong>🎬 Situasjon:</strong> {sec["content_no"]}</p>'
                content_html_th += f'<p><strong>🎬 สถานการณ์:</strong> {sec["content_th"]}</p>'
                content_html_en += f'<p><strong>🎬 Situation:</strong> {sec["content_en"]}</p>'
            elif sec_type == "theory":
                content_html_no += f'<p><strong>📚 Teori — {sec["title_no"]}:</strong> {sec["content_no"]}</p>'
                content_html_th += f'<p><strong>📚 ทฤษฎี — {sec["title_th"]}:</strong> {sec["content_th"]}</p>'
                content_html_en += f'<p><strong>📚 Theory — {sec["title_en"]}:</strong> {sec["content_en"]}</p>'
            elif sec_type == "practice":
                content_html_no += f'<div class="study-tip"><strong>💡 Praksis — {sec["title_no"]}:</strong> {sec["content_no"]}</div>'
                content_html_th += f'<div class="study-tip"><strong>💡 เคล็ดลับปฏิบัติ — {sec["title_th"]}:</strong> {sec["content_th"]}</div>'
                content_html_en += f'<div class="study-tip"><strong>💡 Practical Tip — {sec["title_en"]}:</strong> {sec["content_en"]}</div>'
            else:
                content_html_no += f'<p>{sec["content_no"]}</p>'
                content_html_th += f'<p>{sec["content_th"]}</p>'
                content_html_en += f'<p>{sec["content_en"]}</p>'

        # --- A. Write to studiebok_chapters & studybook_chapters (webapp) ---
        existing_studiebok = studiebok_coll.find_one({"order": chapter_num})
        if existing_studiebok:
            update_data = {
                "icon": icon,
                "title_no": f"Kapittel {chapter_num} — {item['title_no']}",
                "title_th": f"บทเรียนที่ {chapter_num} — {item['title_th']}",
                "title_en": f"Chapter {chapter_num} — {item['title_en']}",
                "content_no": content_html_no,
                "content_th": content_html_th,
                "content_en": content_html_en,
                "chapter_id": chapter_id,
                "sections": item["sections"],
                "difficulty": item["difficulty"],
                "section_tags": item["section_tags"],
                "podcast_reference": item["podcast_reference"]
            }
            studiebok_coll.update_one({"_id": existing_studiebok["_id"]}, {"$set": update_data})
            studybook_coll.update_one({"order": chapter_num}, {"$set": update_data}, upsert=True)
            print(f"  [UPDATE - studiebok_chapters & studybook_chapters] {desc}")
            updated += 1
        else:
            new_studiebok = {
                "order": chapter_num,
                "icon": icon,
                "title_no": f"Kapittel {chapter_num} — {item['title_no']}",
                "title_th": f"บทเรียนที่ {chapter_num} — {item['title_th']}",
                "title_en": f"Chapter {chapter_num} — {item['title_en']}",
                "content_no": content_html_no,
                "content_th": content_html_th,
                "content_en": content_html_en,
                "chapter_id": chapter_id,
                "sections": item["sections"],
                "difficulty": item["difficulty"],
                "section_tags": item["section_tags"],
                "podcast_reference": item["podcast_reference"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            studiebok_coll.insert_one(new_studiebok)
            new_doc_studybook = new_studiebok.copy()
            new_doc_studybook.pop("_id", None)
            studybook_coll.insert_one(new_doc_studybook)
            print(f"  [INSERT - studiebok_chapters & studybook_chapters] {desc}")
            inserted += 1

        # --- B. Write to chapters (mobile app) ---
        chapters_coll.delete_many({"chapter_num": chapter_num})
        
        for idx, sec in enumerate(item["sections"]):
            section_num = idx + 1
            sec_doc = {
                "id": str(uuid.uuid4()),
                "chapter_num": chapter_num,
                "chapter_title": {
                    "no": f"Kapittel {chapter_num} — {item['title_no']}",
                    "th": f"บทเรียนที่ {chapter_num} — {item['title_th']}",
                    "en": f"Chapter {chapter_num} — {item['title_en']}"
                },
                "section_num": section_num,
                "section_title": {
                    "no": sec["title_no"],
                    "th": sec["title_th"],
                    "en": sec["title_en"]
                },
                "content": {
                    "no": sec["content_no"],
                    "th": sec["content_th"],
                    "en": sec["content_en"]
                },
                "image": None,
                "pages": [section_num],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            chapters_coll.insert_one(sec_doc)
            
        print(f"  [INSERT/SYNC - chapters] {desc} with {len(item['sections'])} sections.")
        
    print(f"Studybook chapters Import Summary: {inserted} inserted, {updated} updated, {skipped} skipped.")
    return inserted, updated, skipped

def import_marketing_videos(db):
    print("\n--- Starting Marketing Videos Import ---")
    videos_file = os.path.join("content", "marketing_videos.json")
    if not os.path.exists(videos_file):
        videos_file = "marketing_videos.json"
        if not os.path.exists(videos_file):
            print(f"Marketing videos file {videos_file} not found. Skipping.")
            return 0, 0, 0
            
    with open(videos_file, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    print(f"Found {len(items)} items in {videos_file}.")
    
    collection = db.marketing_videos
    inserted = 0
    updated = 0
    skipped = 0
    
    video_fields = ["title", "hook", "message", "cta", "target_audience"]
    
    for item in items:
        title_no = item.get("title_no", "Unknown")
        desc = f"Video Title: '{title_no}'"
        
        # Additional structure validation for marketing videos
        errors = []
        if "duration_seconds" not in item or not isinstance(item["duration_seconds"], int) or item["duration_seconds"] <= 0:
            errors.append(f"Invalid duration_seconds: {item.get('duration_seconds')}")
        if "platform" not in item or not isinstance(item["platform"], str) or not item["platform"].strip():
            errors.append(f"Invalid platform: {item.get('platform')}")
        if "validation_principle" not in item or not isinstance(item["validation_principle"], str) or not item["validation_principle"].strip():
            errors.append(f"Invalid validation_principle: {item.get('validation_principle')}")
            
        if errors:
            print(f"  [VALIDATION FAILED] {desc}:")
            for err in errors:
                print(f"    - {err}")
            skipped += 1
            continue
            
        # Validate purity
        if not validate_language_purity(item, video_fields, desc):
            skipped += 1
            continue
            
        # Check if already exists in DB
        existing = collection.find_one({"title_no": item["title_no"]})
        
        if existing:
            # Update existing video
            update_data = {
                "title_no": item["title_no"],
                "title_th": item["title_th"],
                "title_en": item["title_en"],
                "hook_no": item["hook_no"],
                "hook_th": item["hook_th"],
                "hook_en": item["hook_en"],
                "message_no": item["message_no"],
                "message_th": item["message_th"],
                "message_en": item["message_en"],
                "cta_no": item["cta_no"],
                "cta_th": item["cta_th"],
                "cta_en": item["cta_en"],
                "validation_principle": item["validation_principle"],
                "duration_seconds": item["duration_seconds"],
                "platform": item["platform"],
                "target_audience_no": item["target_audience_no"],
                "target_audience_th": item["target_audience_th"],
                "target_audience_en": item["target_audience_en"],
                "active": existing.get("active", True)
            }
            collection.update_one({"_id": existing["_id"]}, {"$set": update_data})
            print(f"  [UPDATE] {desc}")
            updated += 1
        else:
            # Create new video
            new_doc = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "active": True,
                "title_no": item["title_no"],
                "title_th": item["title_th"],
                "title_en": item["title_en"],
                "hook_no": item["hook_no"],
                "hook_th": item["hook_th"],
                "hook_en": item["hook_en"],
                "message_no": item["message_no"],
                "message_th": item["message_th"],
                "message_en": item["message_en"],
                "cta_no": item["cta_no"],
                "cta_th": item["cta_th"],
                "cta_en": item["cta_en"],
                "validation_principle": item["validation_principle"],
                "duration_seconds": item["duration_seconds"],
                "platform": item["platform"],
                "target_audience_no": item["target_audience_no"],
                "target_audience_th": item["target_audience_th"],
                "target_audience_en": item["target_audience_en"]
            }
            collection.insert_one(new_doc)
            print(f"  [INSERT] {desc}")
            inserted += 1
            
    print(f"Marketing Videos Import Summary: {inserted} inserted, {updated} updated, {skipped} skipped.")
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
        q_ins, q_upd, q_skp = import_quizzes(db)
        b_ins, b_upd, b_skp = import_studybook_chapters(db)
        v_ins, v_upd, v_skp = import_marketing_videos(db)
        
        print("\n==============================================")
        print("DATABASE IMPORT SUCCESSFULLY COMPLETED!")
        print(f"Total Glossary items: {g_ins} inserted, {g_upd} updated, {g_skp} skipped.")
        print(f"Total Podcast items: {p_ins} inserted, {p_upd} updated, {p_skp} skipped.")
        print(f"Total Quiz Questions: {q_ins} inserted, {q_upd} updated, {q_skp} skipped.")
        print(f"Total Studybook Chapters: {b_ins} inserted, {b_upd} updated, {b_skp} skipped.")
        print(f"Total Marketing Videos: {v_ins} inserted, {v_upd} updated, {v_skp} skipped.")
        print("==============================================")
        
    except Exception as e:
        print(f"ERROR executing database import: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
