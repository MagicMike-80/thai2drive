import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv
load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URI'))
db = client['thai2drive']
async def check():
    c = await db.learning_videos.count_documents({})
    print('videos:', c)
asyncio.run(check())
