import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET_PATH = ROOT / "Michael Trafikklærer AI materialer" / "Thai2Drive_spørsmål_og_svar_med_bilder" / "Bilder og spørsmål.html"
PAYLOAD_PATH = ROOT / "backend" / "content_packs" / "thai2drive_master_quiz_production_payload.json"
ALL_QUESTIONS_PATH = ROOT / "backend" / "scripts" / "image_audit" / "all_questions.json"
HELD_PATH = ROOT / "backend" / "held_screenshot_ids.json"
VERIFIED_OUTPUT = ROOT / "backend" / "content_packs" / "t2d_verified_191_images.json"

# 1. Parse Sheet 1 (Bilder og spørsmål.html)
with open(SHEET_PATH, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
sheet_entries = []
for r in rows:
    cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL)
    if len(cells) > 9:
        q_raw = re.sub(r"<[^>]+>", "", cells[2]).strip()
        t2d_match = re.search(r"(T2D_[a-f0-9]+\.jpg)", cells[9])
        if q_raw and t2d_match:
            t2d_file = t2d_match.group(1)
            sheet_entries.append({
                "question": q_raw,
                "t2d_file": t2d_file,
                "bildeUrl": f"/api/public_assets/quiz_images/{t2d_file}"
            })

print(f"Parsed {len(sheet_entries)} entries with T2D images from sheet.")

# 2. Normalize question helper
def clean_txt(t):
    t = re.sub(r"[\(\*\+\%\>\#\<\=\-\—\–]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()

# 3. Load payload and all_questions
with open(PAYLOAD_PATH, "r", encoding="utf-8") as f:
    payload_data = json.load(f)
payload_qs = payload_data.get("questions", [])

with open(ALL_QUESTIONS_PATH, "r", encoding="utf-8") as f:
    all_qs = json.load(f)

with open(HELD_PATH, "r", encoding="utf-8") as f:
    held_ids = set(str(x) for x in json.load(f))

verified_links = []
unlocked_ids = set()

# Match against payload questions
matched_payload = 0
for entry in sheet_entries:
    q_clean = clean_txt(entry["question"])
    for q in payload_qs:
        no_txt = clean_txt(q.get("question", {}).get("no", ""))
        if q_clean[:35] in no_txt or no_txt[:35] in q_clean:
            q["bildeUrl"] = entry["bildeUrl"]
            q["source_file"] = entry["t2d_file"]
            q["active"] = True
            qid = str(q.get("id"))
            unlocked_ids.add(qid)
            verified_links.append({"id": qid, "bildeUrl": entry["bildeUrl"]})
            matched_payload += 1
            break

# Match against all_questions
matched_all = 0
for entry in sheet_entries:
    q_clean = clean_txt(entry["question"])
    for q in all_qs:
        no_txt = clean_txt(q.get("sporsmal_tekst", "") or q.get("question_no", "") or "")
        if q_clean[:35] in no_txt or no_txt[:35] in q_clean:
            q["bildeUrl"] = entry["bildeUrl"]
            q["source_file"] = entry["t2d_file"]
            q["active"] = True
            qid = str(q.get("id"))
            unlocked_ids.add(qid)
            if not any(v["id"] == qid for v in verified_links):
                verified_links.append({"id": qid, "bildeUrl": entry["bildeUrl"]})
            matched_all += 1
            break

print(f"Matched in payload: {matched_payload}")
print(f"Matched in all_questions: {matched_all}")
print(f"Total verified links created: {len(verified_links)}")

# 4. Save updated files
with open(PAYLOAD_PATH, "w", encoding="utf-8") as f:
    json.dump(payload_data, f, ensure_ascii=False, indent=2)

with open(ALL_QUESTIONS_PATH, "w", encoding="utf-8") as f:
    json.dump(all_qs, f, ensure_ascii=False, indent=2)

with open(VERIFIED_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(verified_links, f, ensure_ascii=False, indent=2)

# Remove unlocked IDs from held list
new_held = sorted(list(held_ids - unlocked_ids))
with open(HELD_PATH, "w", encoding="utf-8") as f:
    json.dump(new_held, f, indent=2)

print(f"Unlocked {len(unlocked_ids)} questions from held list! (Remaining held: {len(new_held)})")
