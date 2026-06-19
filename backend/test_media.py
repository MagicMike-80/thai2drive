import httpx
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "thai2drive")

def test_media_context():
    print("Testing /api/teacher/chat with multimedia query...")
    payload = {
        "session_id": "test_media_session",
        "message": "Kan du vise meg en video om bremselengde?",
        "language": "no"
    }
    
    url = "http://127.0.0.1:8000/api/teacher/chat"
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        print(f"Response status: {response.status_code}")
        print("Response body:")
        print(response.json())
        
        # Verify a log entry was written
        client = pymongo.MongoClient(MONGO_URL)
        db = client[DB_NAME]
        logs_col = db["teacher_chat_logs"]
        last_log = logs_col.find().sort("ts", -1).limit(1)[0]
        print("\nLast log entry in DB:")
        print(last_log)
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_media_context()
