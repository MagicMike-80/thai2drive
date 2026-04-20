"""Insert approved batch 2: #4, #5, #6, #7(modified), #8."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

proposals = json.loads((Path(__file__).parent / "proposed_batch2.json").read_text())
by_slot = {p["slot"]: p for p in proposals}

# User-approved modification to #7:
# Replace option A text (the correct answer) with user's shorter version
by_slot["#7"]["proposal"]["options"][0]["text"] = {
    "no": "Jeg må vike for fotgjengere i gangfeltet og trafikk på hovedveien",
    "en": "I must yield to pedestrians in the crossing and to traffic on the main road",
    "th": "ฉันต้องให้ทางคนเดินเท้าในทางม้าลายและรถบนถนนหลัก",
}

APPROVED = ["#4", "#5", "#6", "#7", "#8"]

for slot in APPROVED:
    entry = by_slot[slot]
    p = entry["proposal"]
    img_path = entry["path"]
    opts = [(o["id"], o["text"]["no"], o["text"]["en"], o["text"]["th"]) for o in p["options"]]
    insert_image_question(
        image_path=img_path,
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
        note=f"Batch 2 {slot}: {p.get('image_identification', '')[:60]}",
        audit_verdict="MATCH",
        audit_image_identification=p.get("image_identification", ""),
    )

print("\n✅ All 5 questions from batch 2 inserted successfully!")
