import pymongo

MONGO_URI = "mongodb+srv://norge-quiz-app:m2iD3VNMnbxL7LIm@cluster0.mecy7qw.mongodb.net/thai2drive?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_URI)
db = client["thai2drive"]

# 1. Clear any private images, screenshots, base64, or auto-assigned T2D images
filter_query = {
    "$or": [
        {"bildeUrl": {"$regex": "sit_", "$options": "i"}},
        {"bildeUrl": {"$regex": "T2D_", "$options": "i"}},
        {"bildeUrl": {"$regex": "Screenshot", "$options": "i"}},
        {"bildeUrl": {"$regex": "base64", "$options": "i"}},
        {"bildeUrl": {"$regex": "Førerprøver", "$options": "i"}}
    ]
}

update_doc = {
    "$set": {
        "bildeUrl": "",
        "has_real_image": False,
        "source_file": "",
        "sha256": ""
    }
}

res = db.questions.update_many(filter_query, update_doc)
print(f"MongoDB: Cleared {res.modified_count} questions matching unwanted/mismatched image patterns.")

# 2. Check remaining questions with images
remaining = list(db.questions.find({"bildeUrl": {"$exists": True, "$ne": ""}}, {"bildeUrl": 1, "question": 1}))
print(f"Total questions with bildeUrl in MongoDB now: {len(remaining)}")

# 3. If any sign image is assigned to a non-sign question, clear it as well
cleaned_signs = 0
for doc in remaining:
    url = doc.get("bildeUrl", "")
    q = doc.get("question", "")
    if isinstance(q, dict):
        q = q.get("no", "")
    q_lower = str(q).lower()
    
    # If not a sign question or mentions situation/weather/motorcycle/car
    if any(w in q_lower for w in ["regn", "våt", "snø", "mørk", "is ", "vinter", "motorsykkel", "fotgjenger", "kø", "rundkjøring"]):
        db.questions.update_one({"_id": doc["_id"]}, {"$set": {"bildeUrl": "", "has_real_image": False}})
        cleaned_signs += 1
    elif "skilt" not in q_lower and "betyr" not in q_lower and "hva angir" not in q_lower:
        db.questions.update_one({"_id": doc["_id"]}, {"$set": {"bildeUrl": "", "has_real_image": False}})
        cleaned_signs += 1

print(f"MongoDB: Cleared {cleaned_signs} mismatched sign images from non-sign questions.")

final_count = db.questions.count_documents({"bildeUrl": {"$exists": True, "$ne": ""}})
print(f"Final count of questions with images in MongoDB: {final_count}")
