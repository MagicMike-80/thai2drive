import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("backend/.env")
MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "thai2drive")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

with open("scratch/db_verification_results.txt", "w", encoding="utf-8") as f:
    f.write("Verifying glossary entries...\n")
    for term in db.learning_glossary.find({"term_no": {"$in": ["Forkjøring", "Rundkjøring", "Grønt lys"]}}):
        f.write(f"Term: {term['term_no']}\n")
        f.write(f"  Thai: {term['term_th']}\n")
        f.write(f"  English: {term['term_en']}\n")

    f.write("\nVerifying podcast entries...\n")
    for pod in db.learning_podcasts.find({"title_no": {"$regex": "vikeplikt"}}):
        f.write(f"Podcast: {pod['title_no']}\n")
        f.write(f"  Thai: {pod['title_th']}\n")

print("Verification complete. Results written to scratch/db_verification_results.txt")
client.close()
