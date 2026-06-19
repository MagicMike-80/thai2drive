import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("backend/.env")
MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "thai2drive")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

with open("scratch/db_quiz_verification_results.txt", "w", encoding="utf-8") as f:
    f.write("Verifying learning_quizzes entries count:\n")
    quizzes_count = db.learning_quizzes.count_documents({})
    f.write(f"Total in learning_quizzes: {quizzes_count}\n\n")

    f.write("Verifying questions entries in category 'Right of Way':\n")
    for q in db.questions.find({"category": "Right of Way"}).limit(3):
        f.write(f"Question (NO): {q['question']['no']}\n")
        f.write(f"  Options: {[opt['text']['no'] for opt in q['options']]}\n")
        f.write(f"  Correct Option: {q['correctOptionId']}\n")

    f.write("\nVerifying question with fixed translation in questions collection:\n")
    fixed_q = db.questions.find_one({"question.no": "Du skal skifte fil til høyre. Hva må du gjøre først?"})
    if fixed_q:
        f.write(f"Found Question (NO): {fixed_q['question']['no']}\n")
        f.write(f"  Options (NO): {[opt['text']['no'] for opt in fixed_q['options']]}\n")
        f.write(f"  Options (TH): {[opt['text']['th'] for opt in fixed_q['options']]}\n")
        f.write(f"  Correct: {fixed_q['correctOptionId']}\n")
    else:
        f.write("Question not found!\n")

print("Verification complete. Results written to scratch/db_quiz_verification_results.txt")
client.close()
