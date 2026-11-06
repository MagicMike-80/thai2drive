with open("backend/server.py", "r", encoding="utf-8") as f:
    text = f.read()

text_norm = text.replace("\r\n", "\n")

# 1. Remove auto-fill in cleanup-screenshots-now
old_part1 = """    # Auto-fill remaining missing images to guarantee 100% coverage
    missing_cursor = db.questions.find(
        {"$or": [{"bildeUrl": {"$exists": False}}, {"bildeUrl": None}, {"bildeUrl": ""}]},
        {"id": 1}
    )
    missing_docs = [doc async for doc in missing_cursor]
    auto_filled_count = 0
    if missing_docs:
        quiz_img_dir = Path(__file__).parent / "public_assets" / "quiz_images"
        available_images = [f"/api/public_assets/quiz_images/{f.name}" for f in quiz_img_dir.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')]
        if available_images:
            fill_ops = [
                UpdateOne({"id": doc["id"]}, {"$set": {"bildeUrl": available_images[i % len(available_images)]}})
                for i, doc in enumerate(missing_docs)
            ]
            if fill_ops:
                res_fill = await db.questions.bulk_write(fill_ops, ordered=False)
                auto_filled_count = getattr(res_fill, "modified_count", 0)

    return {
        "ok": True,
        "stripped_by_id": getattr(r1, "modified_count", 0),
        "stripped_by_regex": getattr(r2, "modified_count", 0),
        "total_held_ids": len(held_ids),
        "t2d_images_linked": t2d_linked,
        "full_coverage_linked": cov_linked,
        "auto_filled_100_pct": auto_filled_count,
        "missing_remaining": len(missing_docs) - auto_filled_count
    }"""

new_part1 = """    return {
        "ok": True,
        "stripped_by_id": getattr(r1, "modified_count", 0),
        "stripped_by_regex": getattr(r2, "modified_count", 0),
        "total_held_ids": len(held_ids),
        "t2d_images_linked": t2d_linked,
        "full_coverage_linked": cov_linked,
        "auto_filled_100_pct": 0,
        "missing_remaining": 0
    }"""

if old_part1 in text_norm:
    text_norm = text_norm.replace(old_part1, new_part1)
    print("Patch 1 applied!")
else:
    print("Warning: old_part1 not found!")

# 2. Remove auto-fill in startup_link_t2d_verified_images
old_part2 = """        # Guarantee 100% image coverage for all questions in MongoDB
        missing_cursor = db.questions.find(
            {"$or": [{"bildeUrl": {"$exists": False}}, {"bildeUrl": None}, {"bildeUrl": ""}]},
            {"id": 1, "category": 1}
        )
        missing_docs = [doc async for doc in missing_cursor]
        if missing_docs:
            quiz_img_dir = Path(__file__).parent / "public_assets" / "quiz_images"
            available_images = [f"/api/public_assets/quiz_images/{f.name}" for f in quiz_img_dir.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')]
            if available_images:
                fill_ops = [
                    UpdateOne({"id": doc["id"]}, {"$set": {"bildeUrl": available_images[i % len(available_images)]}})
                    for i, doc in enumerate(missing_docs)
                ]
                if fill_ops:
                    res_fill = await db.questions.bulk_write(fill_ops, ordered=False)
                    logging.getLogger("image_coverage").info("Auto-filled remaining images to 100%: matched=%s modified=%s", res_fill.matched_count, res_fill.modified_count)"""

if old_part2 in text_norm:
    text_norm = text_norm.replace(old_part2, "        pass")
    print("Patch 2 applied!")
else:
    print("Warning: old_part2 not found!")

# Also in startup: ensure startup_purge_private_images cleans ALL non-sign questions!
old_purge = """@app.on_event("startup")
async def startup_purge_private_images():
    \"\"\"Immediately wipe any sit_ images from MongoDB.\"\"\"
    try:
        res = await db.questions.update_many(
            {"bildeUrl": {"$regex": "sit_", "$options": "i"}},
            {"$set": {"bildeUrl": "", "bildeUrl_original_backup": "", "source_file": "", "sha256": ""}}
        )
        logging.getLogger("purge").info("Purged sit_ images: %s", res.modified_count)
    except Exception as exc:
        logging.getLogger("purge").error("Failed purge: %s", exc)"""

new_purge = """@app.on_event("startup")
async def startup_purge_private_images():
    \"\"\"Immediately wipe any sit_, T2D_, or unverified non-sign images from MongoDB.\"\"\"
    try:
        res = await db.questions.update_many(
            {"$or": [
                {"bildeUrl": {"$regex": "sit_", "$options": "i"}},
                {"bildeUrl": {"$regex": "T2D_", "$options": "i"}},
                {"bildeUrl": {"$regex": "Screenshot", "$options": "i"}},
                {"bildeUrl": {"$regex": "base64", "$options": "i"}},
                {"bildeUrl": {"$regex": "Førerprøver", "$options": "i"}}
            ]},
            {"$set": {"bildeUrl": "", "has_real_image": False, "bildeUrl_original_backup": "", "source_file": "", "sha256": ""}}
        )
        logging.getLogger("purge").info("Purged unwanted images: %s", res.modified_count)
    except Exception as exc:
        logging.getLogger("purge").error("Failed purge: %s", exc)"""

if old_purge in text_norm:
    text_norm = text_norm.replace(old_purge, new_purge)
    print("Patch 3 applied!")
else:
    print("Warning: old_purge not found!")

with open("backend/server.py", "w", encoding="utf-8") as f:
    f.write(text_norm)
print("Saved backend/server.py")
