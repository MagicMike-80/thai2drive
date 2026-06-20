#!/usr/bin/env python3
"""
Import Michael V5 content (quizzes + traffic signs) into MongoDB.

Usage:
  cd backend && python scripts/import_v5_content.py
"""

import json
import sys
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load env
dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'thai2drive')

if not MONGO_URL:
    print("[ERR] MONGO_URL not found in .env")
    sys.exit(1)

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

content_dir = Path(__file__).parent.parent.parent / 'content'

def normalize_quiz_to_v2(q: dict) -> dict:
    """Convert JSON quiz format to v2 schema expected by server.py."""

    # If already v2, return as-is
    if isinstance(q.get("question"), dict):
        return q

    # Convert from flat schema to v2
    return {
        "id": q.get("question_id", ""),
        "question": {
            "no": q.get("question_no", ""),
            "th": q.get("question_th", ""),
            "en": q.get("question_en", ""),
        },
        "options": [
            {
                "id": "A",
                "text": {
                    "no": q["options"][0].get("text_no", ""),
                    "th": q["options"][0].get("text_th", ""),
                    "en": q["options"][0].get("text_en", ""),
                },
                "correct": q["options"][0].get("correct", False),
            },
            {
                "id": "B",
                "text": {
                    "no": q["options"][1].get("text_no", ""),
                    "th": q["options"][1].get("text_th", ""),
                    "en": q["options"][1].get("text_en", ""),
                },
                "correct": q["options"][1].get("correct", False),
            },
            {
                "id": "C",
                "text": {
                    "no": q["options"][2].get("text_no", ""),
                    "th": q["options"][2].get("text_th", ""),
                    "en": q["options"][2].get("text_en", ""),
                },
                "correct": q["options"][2].get("correct", False),
            },
            {
                "id": "D",
                "text": {
                    "no": q["options"][3].get("text_no", ""),
                    "th": q["options"][3].get("text_th", ""),
                    "en": q["options"][3].get("text_en", ""),
                },
                "correct": q["options"][3].get("correct", False),
            },
        ],
        "correctOptionId": next((opt["id"] for opt in [
            {"id": "A", "correct": q["options"][0].get("correct")},
            {"id": "B", "correct": q["options"][1].get("correct")},
            {"id": "C", "correct": q["options"][2].get("correct")},
            {"id": "D", "correct": q["options"][3].get("correct")},
        ] if opt["correct"]), "A"),
        "explanation": {
            "no": q.get("explanation_no", ""),
            "th": q.get("explanation_th", ""),
            "en": q.get("explanation_en", ""),
        },
        "topic_tags": q.get("topic_tags", []),
        "difficulty": q.get("difficulty", "medium"),
        "active": True,
        "created_at": datetime.utcnow().isoformat(),
    }

def import_quizzes():
    """Import all quiz JSON files."""
    quiz_files = [
        "quiz_michael_v5.json",
        "quiz_extended_practice.json",
        "quiz_comprehensive.json",
        "quiz_extra_questions.json",
        "quiz_row_questions.json",
    ]

    total_imported = 0

    for filename in quiz_files:
        filepath = content_dir / filename
        if not filepath.exists():
            print(f"[SKIP] {filename} not found")
            continue

        print(f"\n[QUIZ] Importing {filename}...")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                quizzes = json.load(f)

            if not isinstance(quizzes, list):
                print(f"[ERR] {filename} is not a list, skipping")
                continue

            inserted = 0
            for q in quizzes:
                try:
                    # Check if already exists
                    existing = db.questions.find_one({"id": q.get("question_id")})
                    if existing:
                        print(f"  [SKIP]  Question {q.get('question_id')} already exists")
                        continue

                    # Normalize to v2
                    v2_q = normalize_quiz_to_v2(q)
                    db.questions.insert_one(v2_q)
                    inserted += 1
                except Exception as e:
                    print(f"  [ERR] Error importing question {q.get('question_id')}: {e}")

            print(f"  [OK] Imported {inserted}/{len(quizzes)} questions")
            total_imported += inserted

        except json.JSONDecodeError as e:
            print(f"[ERR] JSON error in {filename}: {e}")
        except Exception as e:
            print(f"[ERR] Error importing {filename}: {e}")

    return total_imported

def import_traffic_signs():
    """Import traffic signs JSON files."""
    sign_files = [
        "traffic_signs_explained.json",
        "traffic_signs_expanded.json",
    ]

    total_imported = 0

    for filename in sign_files:
        filepath = content_dir / filename
        if not filepath.exists():
            print(f"[SKIP] {filename} not found")
            continue

        print(f"\n[SIGNS] Importing {filename}...")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                signs = json.load(f)

            if not isinstance(signs, list):
                print(f"[ERR] {filename} is not a list, skipping")
                continue

            inserted = 0
            for sign in signs:
                try:
                    # Check if already exists
                    existing = db.traffic_signs.find_one({"sign_id": sign.get("sign_id")})
                    if existing:
                        print(f"  [SKIP]  Sign {sign.get('sign_id')} already exists")
                        continue

                    # Add metadata
                    sign["created_at"] = datetime.utcnow().isoformat()
                    sign["active"] = True

                    db.traffic_signs.insert_one(sign)
                    inserted += 1
                except Exception as e:
                    print(f"  [ERR] Error importing sign {sign.get('sign_id')}: {e}")

            print(f"  [OK] Imported {inserted}/{len(signs)} traffic signs")
            total_imported += inserted

        except json.JSONDecodeError as e:
            print(f"[ERR] JSON error in {filename}: {e}")
        except Exception as e:
            print(f"[ERR] Error importing {filename}: {e}")

    return total_imported

if __name__ == "__main__":
    print("[*] Starting Michael V5 content import...")
    print(f"[DB] MongoDB: {DB_NAME}")
    print(f"[Path] Content dir: {content_dir}")

    quiz_count = import_quizzes()
    sign_count = import_traffic_signs()

    total = quiz_count + sign_count
    print(f"\n[OK] Import complete! Added {total} documents total")
    print(f"   [Quiz] Quizzes: {quiz_count}")
    print(f"   [Signs] Traffic signs: {sign_count}")
