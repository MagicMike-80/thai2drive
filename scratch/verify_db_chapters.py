import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("backend/.env")
MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "thai2drive")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

with open("scratch/db_chapters_verification_results.txt", "w", encoding="utf-8") as f:
    f.write("Verifying studiebok_chapters count:\n")
    studiebok_count = db.studiebok_chapters.count_documents({})
    f.write(f"Total in studiebok_chapters: {studiebok_count}\n\n")

    f.write("Verifying chapters count in chapters collection:\n")
    chapters_count = db.chapters.count_documents({})
    f.write(f"Total sections in chapters collection: {chapters_count}\n\n")

    f.write("Verifying details of Chapter 7 in studiebok_chapters:\n")
    ch7 = db.studiebok_chapters.find_one({"order": 7})
    if ch7:
        f.write(f"Found order 7: {ch7['title_no']}\n")
        f.write(f"  Icon: {ch7['icon']}\n")
        f.write(f"  HTML preview (NO): {ch7['content_no'][:250]}...\n")
        f.write(f"  HTML preview (TH): {ch7['content_th'][:250]}...\n")
    else:
        f.write("Chapter 7 not found in studiebok_chapters!\n")

    f.write("\nVerifying details of Chapter 7 in chapters collection:\n")
    ch7_secs = list(db.chapters.find({"chapter_num": 7}).sort("section_num", 1))
    f.write(f"Found {len(ch7_secs)} sections for chapter_num 7.\n")
    for sec in ch7_secs:
        f.write(f"  Sec {sec['section_num']}: {sec['section_title']['no']}\n")
        f.write(f"    Content (NO): {sec['content']['no'][:100]}...\n")

print("Verification complete. Results written to scratch/db_chapters_verification_results.txt")
client.close()
