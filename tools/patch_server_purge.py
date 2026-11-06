with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update manual_cleanup_screenshots regex to include sit_
old_regex = '''            {"bildeUrl": {"$regex": "^data:image", "$options": "i"}},'''
new_regex = '''            {"bildeUrl": {"$regex": "^data:image", "$options": "i"}},
            {"bildeUrl": {"$regex": "sit_", "$options": "i"}},'''

if old_regex in text:
    text = text.replace(old_regex, new_regex)

# 2. Add immediate startup purge for sit_
old_startup = '''@app.on_event("startup")
async def startup_link_t2d_verified_images():'''

new_startup = '''@app.on_event("startup")
async def startup_purge_private_images():
    """Immediately wipe any sit_ images from MongoDB."""
    try:
        res = await db.questions.update_many(
            {"bildeUrl": {"$regex": "sit_", "$options": "i"}},
            {"$set": {"bildeUrl": "", "bildeUrl_original_backup": "", "source_file": "", "sha256": ""}}
        )
        logging.getLogger("purge").info("Purged sit_ images: %s", res.modified_count)
    except Exception as exc:
        logging.getLogger("purge").error("Failed purge: %s", exc)

@app.on_event("startup")
async def startup_link_t2d_verified_images():'''

if old_startup in text:
    text = text.replace(old_startup, new_startup)

with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: server.py patched with sit_ purge!")
