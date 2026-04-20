"""Insert 'Warning sign placement distance outside built-up areas' Traffic Rules question."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

qid = insert_image_question(
    image_path="/tmp/signs/warning_left_curve.jpg",
    question_no="Utenfor tettbygd strøk er fareskilt vanligvis plassert hvor langt før faren?",
    question_en="Outside built-up areas, how far before a hazard are warning signs usually placed?",
    question_th="นอกเขตเมือง ป้ายเตือนมักถูกติดตั้งห่างจากอันตรายประมาณเท่าใด?",
    options=[
        ("A", "50–100 meter",   "50–100 meters",   "50–100 เมตร"),
        ("B", "100–150 meter",  "100–150 meters",  "100–150 เมตร"),
        ("C", "150–250 meter",  "150–250 meters",  "150–250 เมตร"),
        ("D", "250–400 meter",  "250–400 meters",  "250–400 เมตร"),
    ],
    correct="C",
    explanation_no=(
        "Fareskilt (trekantede skilt med rød kant, slik som 106.2 'Farlig sving venstre' på "
        "bildet) varsler om mulig fare. Utenfor tettbygd strøk plasseres de normalt "
        "150–250 meter før faren, slik at føreren har god tid til å oppdage skiltet, "
        "forstå varselet og tilpasse farten før faren nås. I tettbygd strøk plasseres de "
        "nærmere faren (ofte 50–100 meter), fordi farten vanligvis er lavere."
    ),
    explanation_en=(
        "Warning signs (red-bordered triangular signs, like sign 106.2 'Dangerous curve, "
        "left' in the picture) alert drivers to a possible hazard. Outside built-up areas "
        "they are normally placed 150–250 metres before the hazard, giving the driver enough "
        "time to spot the sign, understand the warning and adjust speed. Inside built-up "
        "areas they are placed closer to the hazard (often 50–100 m) because speeds are lower."
    ),
    explanation_th=(
        "ป้ายเตือน (ป้ายสามเหลี่ยมขอบแดง เช่น ป้าย 106.2 'ทางโค้งอันตรายซ้าย' ในรูป) "
        "เตือนผู้ขับขี่ถึงอันตรายที่อาจเกิดขึ้น นอกเขตเมืองจะติดตั้งประมาณ 150–250 เมตร "
        "ก่อนถึงจุดอันตราย เพื่อให้ผู้ขับมีเวลาพอสังเกต เข้าใจคำเตือน และปรับความเร็ว "
        "ในเขตเมืองจะติดตั้งใกล้จุดอันตรายกว่า (ประมาณ 50–100 เมตร) เนื่องจากความเร็วต่ำกว่า"
    ),
    category="Traffic Rules",
    difficulty="easy",
    note="Added warning-sign placement distance question (image: 106.2 Farlig sving venstre)",
    audit_verdict="MATCH",
    audit_image_identification="Fareskilt 106.2 Farlig sving venstre (eksempel på fareskilt)",
)
print(f"Question id: {qid}")
