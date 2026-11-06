import json
import glob
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Delete all sit_* files from disk
for f in glob.glob(str(ROOT / "backend/public_assets/quiz_images/sit_*")):
    try:
        os.remove(f)
    except Exception:
        pass
print("Local sit_* files deleted.")

# 2. Clean all_questions.json: remove any sit_ reference
ALL_QS = ROOT / "backend/scripts/image_audit/all_questions.json"
if ALL_QS.exists():
    with open(ALL_QS, "r", encoding="utf-8") as f:
        qs = json.load(f)
    cleaned = 0
    for q in qs:
        url = str(q.get("bildeUrl") or "")
        if "sit_" in url or "Screenshot_" in url or url.startswith("data:image"):
            q["bildeUrl"] = ""
            cleaned += 1
    with open(ALL_QS, "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)
    print(f"Cleaned {cleaned} questions in all_questions.json.")

# 3. Remove or clear full_image_coverage_pack.json
COV_PACK = ROOT / "backend/content_packs/full_image_coverage_pack.json"
if COV_PACK.exists():
    with open(COV_PACK, "w", encoding="utf-8") as f:
        json.dump([], f)
    print("full_image_coverage_pack.json cleared.")

print("Purge completed successfully.")
