"""Insert 'Summer tire minimum tread depth' Safety question."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

qid = insert_image_question(
    image_path="/tmp/signs/tire_tread.jpg",
    question_no="Hva er minimumskravet til mønsterdybde for sommerdekk?",
    question_en="What is the minimum tread depth for summer tyres?",
    question_th="ความลึกของดอกยางขั้นต่ำสำหรับยางฤดูร้อนคือเท่าใด?",
    options=[
        ("A", "1,0 mm", "1.0 mm", "1.0 มม."),
        ("B", "1,6 mm", "1.6 mm", "1.6 มม."),
        ("C", "3,0 mm", "3.0 mm", "3.0 มม."),
        ("D", "4,0 mm", "4.0 mm", "4.0 มม."),
    ],
    correct="B",
    explanation_no=(
        "Minimumskravet til mønsterdybde for sommerdekk i Norge er 1,6 mm. For vinterdekk er "
        "kravet 3,0 mm. Dekk med lavere mønsterdybde enn minimumskravet er ulovlige og kan gi "
        "bot samt strykkaraker ved EU-kontroll. Av hensyn til sikkerhet – særlig ved vannplaning "
        "på våt vei – anbefales det å bytte sommerdekk når mønsterdybden nærmer seg 3 mm."
    ),
    explanation_en=(
        "The legal minimum tread depth for summer tyres in Norway is 1.6 mm. For winter tyres "
        "it is 3.0 mm. Tyres below the minimum are illegal and can result in fines and failure "
        "at the periodic vehicle inspection (EU-kontroll). For safety reasons – especially to "
        "avoid aquaplaning on wet roads – summer tyres should be replaced when the tread "
        "approaches 3 mm."
    ),
    explanation_th=(
        "ข้อกำหนดตามกฎหมายของความลึกดอกยางขั้นต่ำสำหรับยางฤดูร้อนในนอร์เวย์คือ 1.6 มม. "
        "สำหรับยางฤดูหนาวคือ 3.0 มม. ยางที่ต่ำกว่าค่าขั้นต่ำถือว่าผิดกฎหมาย อาจถูกปรับและ "
        "สอบตกที่การตรวจสภาพรถ (EU-kontroll) เพื่อความปลอดภัย – โดยเฉพาะเพื่อหลีกเลี่ยง "
        "การเกิดเหวๆ บนถนนเปียก – ควรเปลี่ยนยางฤดูร้อนเมื่อดอกยางเหลือประมาณ 3 มม."
    ),
    category="Safety",
    difficulty="easy",
    note="Added summer tyre minimum tread depth (image: tread depth gauge)",
    audit_verdict="MATCH",
    audit_image_identification="Måling av mønsterdybde på dekk med mønsterdybdemåler",
)
print(f"Question id: {qid}")
