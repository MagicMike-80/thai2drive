"""Migrate ALL old flat-schema (v1) questions to nested v2 schema in-place."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

async def migrate():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Find all v1 questions (have question_text_no but no schema_version)
    v1_cursor = db.questions.find({"question_text_no": {"$exists": True}, "schema_version": {"$exists": False}})
    v1_questions = await v1_cursor.to_list(None)
    print(f"Found {len(v1_questions)} v1 questions to migrate")

    migrated = 0
    for q in v1_questions:
        v2_doc = {
            "id": q.get("id", ""),
            "question": {
                "no": q.get("question_text_no", ""),
                "th": q.get("question_text_th", ""),
                "en": q.get("question_text_en", ""),
            },
            "options": [
                {"id": "A", "text": {"no": q.get("answer_a_no", ""), "th": q.get("answer_a_th", ""), "en": q.get("answer_a_en", "")}},
                {"id": "B", "text": {"no": q.get("answer_b_no", ""), "th": q.get("answer_b_th", ""), "en": q.get("answer_b_en", "")}},
                {"id": "C", "text": {"no": q.get("answer_c_no", ""), "th": q.get("answer_c_th", ""), "en": q.get("answer_c_en", "")}},
                {"id": "D", "text": {"no": q.get("answer_d_no", ""), "th": q.get("answer_d_th", ""), "en": q.get("answer_d_en", "")}},
            ],
            "correctOptionId": q.get("correct_answer", ""),
            "explanation": {
                "no": q.get("explanation_no", ""),
                "th": q.get("explanation_th", ""),
                "en": q.get("explanation_en", ""),
            },
            "bildeUrl": q.get("image_url"),
            "category": q.get("category", ""),
            "difficulty": q.get("difficulty", "easy"),
            "active": True,
            "schema_version": 2,
            "created_at": q.get("created_at", ""),
        }

        await db.questions.replace_one({"_id": q["_id"]}, v2_doc)
        migrated += 1

    # Verify
    total = await db.questions.count_documents({})
    v2_count = await db.questions.count_documents({"schema_version": 2})
    v1_remaining = await db.questions.count_documents({"question_text_no": {"$exists": True}, "schema_version": {"$exists": False}})

    print(f"Migrated: {migrated}")
    print(f"Total questions: {total}")
    print(f"V2 questions: {v2_count}")
    print(f"V1 remaining: {v1_remaining}")

    client.close()

asyncio.run(migrate())
