with open('backend/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '''            if ops:
                res = await db.questions.bulk_write(ops, ordered=False)
                logging.getLogger("t2d_images").info("Linked T2D verified images: matched=%s modified=%s", res.matched_count, res.modified_count)
    except Exception as exc:'''

replacement1 = '''            if ops:
                res = await db.questions.bulk_write(ops, ordered=False)
                logging.getLogger("t2d_images").info("Linked T2D verified images: matched=%s modified=%s", res.matched_count, res.modified_count)

        cov_file = Path(__file__).parent / "content_packs" / "full_image_coverage_pack.json"
        if cov_file.exists():
            with open(cov_file, "r", encoding="utf-8") as f:
                cov_links = json.load(f)
            from pymongo import UpdateOne
            cov_ops = [
                UpdateOne({"id": item["id"]}, {"$set": {"bildeUrl": item["bildeUrl"], "active": True}})
                for item in cov_links if item.get("id") and item.get("bildeUrl")
            ]
            if cov_ops:
                res_cov = await db.questions.bulk_write(cov_ops, ordered=False)
                logging.getLogger("image_coverage").info("Linked full image coverage: matched=%s modified=%s", res_cov.matched_count, res_cov.modified_count)
    except Exception as exc:'''

target2 = '''        if ops:
            res_link = await db.questions.bulk_write(ops, ordered=False)
            t2d_linked = getattr(res_link, "modified_count", 0)

    return {'''

replacement2 = '''        if ops:
            res_link = await db.questions.bulk_write(ops, ordered=False)
            t2d_linked = getattr(res_link, "modified_count", 0)

    cov_file = Path(__file__).parent / "content_packs" / "full_image_coverage_pack.json"
    cov_linked = 0
    if cov_file.exists():
        with open(cov_file, "r", encoding="utf-8") as f:
            cov_links = json.load(f)
        from pymongo import UpdateOne
        cov_ops = [
            UpdateOne({"id": item["id"]}, {"$set": {"bildeUrl": item["bildeUrl"], "active": True}})
            for item in cov_links if item.get("id") and item.get("bildeUrl")
        ]
        if cov_ops:
            res_cov = await db.questions.bulk_write(cov_ops, ordered=False)
            cov_linked = getattr(res_cov, "modified_count", 0)

    return {'''

target3 = '''        "total_held_ids": len(held_ids),
        "t2d_images_linked": t2d_linked'''

replacement3 = '''        "total_held_ids": len(held_ids),
        "t2d_images_linked": t2d_linked,
        "full_coverage_linked": cov_linked'''

assert target1 in text, "target1 not found"
text = text.replace(target1, replacement1)

assert target2 in text, "target2 not found"
text = text.replace(target2, replacement2)

assert target3 in text, "target3 not found"
text = text.replace(target3, replacement3)

with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: server.py patched with full image coverage bulk update!")
