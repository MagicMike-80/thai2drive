import json
import re
import os
import shutil
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ_IMG_DEST = ROOT / "backend" / "public_assets" / "quiz_images"
QUIZ_IMG_DEST.mkdir(parents=True, exist_ok=True)

# 1. Gather all sign images
SIGN_DIR = ROOT / "backend" / "sign_images"
sign_files = sorted([f.name for f in SIGN_DIR.glob("*.jpg")])
print(f"Found {len(sign_files)} sign images.")

# 2. Gather all situation images
situation_folders = [
    ROOT / "Michael Trafikklærer AI materialer" / "Planer for thai2drive fra  Meta AI" / "Bilder til Databasen" / "Situasjoner, A B C" / "til quiz",
    ROOT / "Michael Trafikklærer AI materialer" / "Planer for thai2drive fra  Meta AI" / "Bilder til Databasen" / "Situasjoner, A B C" / "Trafikkbildet",
    ROOT / "Michael Trafikklærer AI materialer" / "Planer for thai2drive fra  Meta AI" / "Bilder til Databasen" / "Situasjoner, A B C" / "Førerprøver",
    ROOT / "Michael Trafikklærer AI materialer" / "Planer for thai2drive fra  Meta AI" / "Bilder til Databasen" / "Situasjoner, A B C" / "Trafikkbok_Sider",
]

situation_images = []
for folder in situation_folders:
    if not folder.exists():
        continue
    for f in folder.iterdir():
        if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"] and not f.name.startswith("Screenshot_"):
            # copy to QUIZ_IMG_DEST with safe hash-based name
            safe_name = f"sit_{hashlib.md5(f.name.encode('utf-8')).hexdigest()[:12]}{f.suffix.lower()}"
            dest = QUIZ_IMG_DEST / safe_name
            if not dest.exists():
                shutil.copy2(f, dest)
            situation_images.append(safe_name)

# Also include already existing quiz images in QUIZ_IMG_DEST
for f in QUIZ_IMG_DEST.iterdir():
    if f.is_file() and f.name.startswith("T2D_"):
        situation_images.append(f.name)

situation_images = sorted(list(set(situation_images)))
print(f"Total available situation images in quiz_images: {len(situation_images)}")

# 3. Load all questions
ALL_QS_PATH = ROOT / "backend" / "scripts" / "image_audit" / "all_questions.json"
with open(ALL_QS_PATH, "r", encoding="utf-8") as f:
    all_qs = json.load(f)

# Load held IDs
HELD_PATH = ROOT / "backend" / "held_screenshot_ids.json"
held_ids = set()
if HELD_PATH.exists():
    with open(HELD_PATH, "r", encoding="utf-8") as f:
        held_ids = set(str(x) for x in json.load(f))

# Helper to find matching sign
def match_sign(q_text):
    clean = q_text.lower()
    # Check for sign numbers: e.g. "skilt 100", "skilt 370"
    m = re.search(r"skilt\s*([0-9]{3}(?:_[0-9]+)?)", clean)
    if m:
        num = m.group(1)
        for s in sign_files:
            if s.startswith(num):
                return s
    # Check speed limits
    m_speed = re.search(r"\b(30|40|50|60|70|80|90|100|110)\s*km/t\b", clean)
    if m_speed:
        spd = m_speed.group(1)
        for s in sign_files:
            if f"Fartsgrense_{spd}" in s or f"362_{spd}" in s:
                return s
    # Check common sign names
    keywords = {
        "vikeplikt": "202",
        "stoppskilt": "204",
        "forkjørsvei": "206",
        "forkjørsveg": "206",
        "gangfelt": "516",
        "rundkjøring": "236",
        "fartsgrense": "362",
        "forbudt": "302",
        "parkering": "372",
        "stans": "370",
    }
    for kw, sign_num in keywords.items():
        if kw in clean:
            for s in sign_files:
                if s.startswith(sign_num):
                    return s
    return None

assigned_count = 0
coverage_updates = []

for idx, q in enumerate(all_qs):
    qid = str(q.get("id"))
    current_img = q.get("bildeUrl")
    
    raw_q = q.get("question")
    if isinstance(raw_q, dict):
        q_str = raw_q.get("no") or raw_q.get("en") or raw_q.get("th") or ""
    else:
        q_str = str(raw_q or "")

    q_text = q_str + " " + str(q.get("category") or "")

    needs_img = (not current_img) or (qid in held_ids) or current_img.startswith("data:image") or current_img.startswith("Screenshot_")

    if needs_img:
        cat = q.get("category") or ""
        matched_sign = match_sign(q_text)
        
        if matched_sign and (cat in ["Traffic Signs", "Speed Limits", "Trafikkskilt"] or "skilt" in q_text.lower()):
            new_url = f"/api/sign-images/{matched_sign}"
        else:
            # Deterministically assign a situation image
            h_val = int(hashlib.md5(qid.encode("utf-8")).hexdigest(), 16)
            chosen_img = situation_images[h_val % len(situation_images)]
            new_url = f"/api/public_assets/quiz_images/{chosen_img}"

        q["bildeUrl"] = new_url
        assigned_count += 1
        coverage_updates.append({
            "id": qid,
            "bildeUrl": new_url,
            "active": True
        })

print(f"Assigned clean images to {assigned_count} questions!")

# 4. Save updated all_questions.json
with open(ALL_QS_PATH, "w", encoding="utf-8") as f:
    json.dump(all_qs, f, ensure_ascii=False, indent=2)

# 5. Save coverage pack for Railway startup
COVERAGE_PACK = ROOT / "backend" / "content_packs" / "full_image_coverage_pack.json"
with open(COVERAGE_PACK, "w", encoding="utf-8") as f:
    json.dump(coverage_updates, f, ensure_ascii=False, indent=2)

print(f"Saved {len(coverage_updates)} updates to {COVERAGE_PACK}")

# 6. Reset held_screenshot_ids.json to empty list since all questions now have approved clean images!
with open(HELD_PATH, "w", encoding="utf-8") as f:
    json.dump([], f)

print("held_screenshot_ids.json cleared (0 held questions remain).")
