"""Insert approved batch 3: #1, #2, #3, #4 (modified order A→C→B)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

proposals = json.loads((Path(__file__).parent / "proposed_batch3.json").read_text())
by_slot = {p["slot"]: p for p in proposals}

# === Modify #4 ===
# User chose "A → C → B" as the correct order.
# Rewrite option A to be that order, make it the correct answer, rewrite explanation.
p4 = by_slot["#4"]["proposal"]
p4["options"] = [
    {"id": "A", "text": {
        "no": "A, C, B",
        "en": "A, C, B",
        "th": "A, C, B",
    }},
    {"id": "B", "text": {
        "no": "C, A, B",
        "en": "C, A, B",
        "th": "C, A, B",
    }},
    {"id": "C", "text": {
        "no": "B, C, A",
        "en": "B, C, A",
        "th": "B, C, A",
    }},
    {"id": "D", "text": {
        "no": "A og B samtidig, deretter C",
        "en": "A and B simultaneously, then C",
        "th": "A และ B ไปพร้อมกัน แล้ว C",
    }},
]
p4["correctOptionId"] = "A"
p4["explanation"] = {
    "no": (
        "Dette er et uskiltet kryss der høyreregelen gjelder. Ut fra kjøretøyenes posisjoner "
        "og ønskede kjøreretninger har bil B vikeplikt både for bil A og motorsykkel C. "
        "Bil A skal svinge høyre og kan kjøre først. Deretter motorsykkel C som har vikeplikt "
        "for B, men ikke for A som allerede har passert. Til slutt kjører B. "
        "Rekkefølgen blir derfor A → C → B."
    ),
    "en": (
        "This is an unsigned intersection where the right-hand rule applies. Based on the "
        "positions and intended directions of the vehicles, car B must yield to both car A "
        "and motorcycle C. Car A turns right and may go first. Then motorcycle C follows, "
        "and finally car B. The correct order is therefore A → C → B."
    ),
    "th": (
        "นี่คือทางแยกที่ไม่มีป้าย ซึ่งใช้กฎมือขวา จากตำแหน่งและทิศทางที่ตั้งใจจะไปของรถแต่ละคัน "
        "รถ B ต้องให้ทางทั้งรถ A และมอเตอร์ไซค์ C รถ A เลี้ยวขวาจึงไปก่อนได้ "
        "จากนั้นมอเตอร์ไซค์ C และสุดท้ายรถ B ดังนั้นลำดับที่ถูกต้องคือ A → C → B"
    ),
}

APPROVED = ["#1", "#2", "#3", "#4"]

for slot in APPROVED:
    entry = by_slot[slot]
    p = entry["proposal"]
    opts = [(o["id"], o["text"]["no"], o["text"]["en"], o["text"]["th"]) for o in p["options"]]
    insert_image_question(
        image_path=entry["path"],
        question_no=p["question"]["no"],
        question_en=p["question"]["en"],
        question_th=p["question"]["th"],
        options=opts,
        correct=p["correctOptionId"],
        explanation_no=p["explanation"]["no"],
        explanation_en=p["explanation"]["en"],
        explanation_th=p["explanation"]["th"],
        category=p["category"],
        difficulty=p["difficulty"],
        note=f"Batch 3 {slot}: {p.get('image_identification', '')[:60]}",
        audit_verdict="MATCH",
        audit_image_identification=p.get("image_identification", ""),
    )

print("\n✅ All 4 from batch 3 inserted successfully!")
