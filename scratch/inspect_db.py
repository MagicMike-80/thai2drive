import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def main():
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    print(f"Connecting to {mongo_url}, DB: {db_name}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check total counts
    total = await db.quiz_attempts.count_documents({})
    with_user = await db.quiz_attempts.count_documents({"user_id": {"$exists": True, "$ne": None}})
    no_user = await db.quiz_attempts.count_documents({"user_id": {"$exists": False}})
    null_user = await db.quiz_attempts.count_documents({"user_id": None})
    
    print(f"Total attempts: {total}")
    print(f"With user_id: {with_user}")
    print(f"No user_id key: {no_user}")
    print(f"Null user_id: {null_user}")
    
    # Unique user_ids
    users = await db.quiz_attempts.distinct("user_id")
    print(f"Unique user_ids: {users}")
    
    # Unique device_ids
    devices = await db.quiz_attempts.distinct("device_id")
    print(f"Number of unique device_ids: {len(devices)}")
    print(f"Sample device_ids: {devices[:10]}")
    
    # Check user collection count
    user_count = await db.users.count_documents({})
    print(f"Total users in users collection: {user_count}")
    
    # Get a sample user
    sample_user = await db.users.find_one({})
    if sample_user:
        print(f"Sample user keys: {list(sample_user.keys())}")
        print(f"Sample user ID: {sample_user.get('id')} / Email: {sample_user.get('email')} / Device: {sample_user.get('device_id')}")

if __name__ == '__main__':
    asyncio.run(main())
