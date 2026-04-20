"""Insert 'Practice driving supervisor requirements' Safety question."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

qid = insert_image_question(
    image_path="/tmp/signs/practice_driving.jpg",
    question_no="Hva er riktig om øvelseskjøring?",
    question_en="What is correct about practice driving?",
    question_th="ข้อใดถูกต้องเกี่ยวกับการฝึกขับรถ?",
    options=[
        ("A",
         "Du kan øvelseskjøre uten ledsager",
         "You can practice drive without a supervisor",
         "คุณสามารถฝึกขับรถได้โดยไม่มีผู้ดูแล"),
        ("B",
         "Ledsager må være fylt 25 år og hatt førerkort i minst 5 år",
         "The supervisor must be at least 25 years old and have held a driving licence for at least 5 years",
         "ผู้ดูแลต้องมีอายุอย่างน้อย 25 ปี และมีใบขับขี่อย่างน้อย 5 ปี"),
        ("C",
         "Det er ikke krav til hvem som er ledsager",
         "There are no requirements for the supervisor",
         "ไม่มีข้อกำหนดสำหรับผู้ดูแล"),
        ("D",
         "Du kan øvelseskjøre uten L-skilt",
         "You can practice drive without an L sign",
         "คุณสามารถฝึกขับรถได้โดยไม่ต้องมีป้าย L"),
    ],
    correct="B",
    explanation_no=(
        "Ved privat øvelseskjøring må ledsageren ha fylt 25 år og ha hatt gyldig førerkort "
        "for samme klasse sammenhengende de siste 5 årene. Bilen må også være tydelig merket "
        "med rødt L-skilt. Dette er et lovkrav fra Statens vegvesen."
    ),
    explanation_en=(
        "For private practice driving, the supervisor must be at least 25 years old and have "
        "held a valid driving licence for the same class continuously for the last 5 years. "
        "The car must also be clearly marked with a red 'L' sign. This is a legal requirement "
        "from the Norwegian Public Roads Administration (Statens vegvesen)."
    ),
    explanation_th=(
        "สำหรับการฝึกขับรถส่วนตัว ผู้ดูแลต้องมีอายุอย่างน้อย 25 ปี และต้องมีใบขับขี่ที่ถูกต้อง "
        "ในประเภทเดียวกันต่อเนื่องเป็นเวลาอย่างน้อย 5 ปีที่ผ่านมา รถต้องติดป้าย 'L' สีแดง "
        "อย่างชัดเจน นี่เป็นข้อกำหนดตามกฎหมายจากกรมทางหลวงของรัฐ (Statens vegvesen)"
    ),
    category="Safety",
    difficulty="easy",
    note="Added 'practice driving supervisor requirements' (Statens vegvesen scene)",
    audit_verdict="MATCH",
    audit_image_identification="Bil foran Statens vegvesen (øvelseskjøringsscene)",
)
print(f"Question id: {qid}")
