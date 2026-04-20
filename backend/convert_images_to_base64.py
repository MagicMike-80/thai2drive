"""Download sign images and store as base64 data URIs in DB."""
import asyncio, os, base64, httpx
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()
MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

HEADERS = {
    "User-Agent": "Thai2Drive/1.0 (educational quiz app; contact: admin@thai2drive.com)"
}

async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get unique URLs
    urls = set()
    async for d in db.questions.find({'bildeUrl': {'$regex': '^https?://'}}, {'bildeUrl': 1}):
        u = d.get('bildeUrl')
        if u: urls.add(u)
    print(f"Found {len(urls)} unique remote image URLs")
    
    # Download each
    url_to_b64 = {}
    async with httpx.AsyncClient(timeout=30.0, headers=HEADERS, follow_redirects=True) as hx:
        for u in urls:
            try:
                r = await hx.get(u)
                if r.status_code == 200:
                    ct = r.headers.get('content-type', 'image/png').split(';')[0]
                    b64 = base64.b64encode(r.content).decode('ascii')
                    url_to_b64[u] = f'data:{ct};base64,{b64}'
                    print(f"  OK {len(r.content)//1024}KB: {u.split('/')[-1]}")
                else:
                    print(f"  FAIL {r.status_code}: {u}")
            except Exception as e:
                print(f"  ERROR: {u} — {e}")
    
    print(f"\nSuccessfully downloaded {len(url_to_b64)} images")
    
    # Update DB
    updated = 0
    for url, data_uri in url_to_b64.items():
        res = await db.questions.update_many({'bildeUrl': url}, {'$set': {'bildeUrl': data_uri}})
        updated += res.modified_count
    print(f"Updated {updated} question docs with base64 images")
    
    client.close()

asyncio.run(main())
