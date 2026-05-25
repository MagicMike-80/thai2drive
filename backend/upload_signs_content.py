"""
upload_signs_content.py — reads signs_content.json and writes to MongoDB.
Run after generate_signs_content.py.
"""
import json
from pathlib import Path
from dotenv import dotenv_values
import pymongo

env = dotenv_values(Path(__file__).parent / '.env')
db  = pymongo.MongoClient(env['MONGO_URL'])[env['DB_NAME']]

data = json.loads((Path(__file__).parent / 'signs_content.json').read_text(encoding='utf-8'))

updated = 0
for s in data:
    result = db.traffic_signs.update_one(
        {'id': s['id']},
        {'$set': {
            'name.no':        s['name']['no'],
            'name.th':        s['name']['th'],
            'name.en':        s['name']['en'],
            'explanation.no': s['explanation']['no'],
            'explanation.th': s['explanation']['th'],
            'explanation.en': s['explanation']['en'],
        }}
    )
    if result.modified_count:
        updated += 1

print(f"Done — {updated}/{len(data)} signs updated in MongoDB.")
