"""Insert 'Right lane ends, merge left - who yields?' Traffic Rules question."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

qid = insert_image_question(
    image_path="/tmp/signs/lane_merge.jpg",
    question_no="Du ligger i feltet lengst til høyre og ser dette skiltet. Hvem har vikeplikt?",
    question_en="You are driving in the rightmost lane and see this sign. Who must yield?",
    question_th="คุณขับอยู่ในช่องทางขวาสุดและเห็นป้ายนี้ ใครต้องให้ทาง?",
    options=[
        ("A",
         "Du i høyre felt må vike",
         "You in the right lane must yield",
         "คุณในช่องขวาต้องให้ทาง"),
        ("B",
         "Kjøretøy i de andre feltene må vike",
         "Vehicles in the other lanes must yield",
         "รถในช่องทางอื่นต้องให้ทาง"),
        ("C",
         "Ingen har vikeplikt",
         "No one has to yield",
         "ไม่มีใครต้องให้ทาง"),
        ("D",
         "Den raskeste bilen har forkjørsrett",
         "The fastest vehicle has priority",
         "รถที่เร็วที่สุดมีสิทธิ์ก่อน"),
    ],
    correct="A",
    explanation_no=(
        "Skiltet (opplysningsskilt 527.3 'Sammenfletting') viser at høyre kjørefelt opphører "
        "og skal flette seg inn i de andre feltene. Den røde pilen viser hvilket felt som "
        "slutter. Du som ligger i høyre felt har vikeplikt for trafikken i feltet du skal "
        "flette deg inn i – bruk blinklys, tilpass farten og vent på en luke."
    ),
    explanation_en=(
        "The sign (information sign 527.3 'Lane merging') shows that the right lane ends and "
        "must merge into the other lanes. The red arrow indicates which lane is ending. As "
        "the driver in the right lane, you must yield to traffic in the lane you are merging "
        "into – use your indicator, adjust your speed and wait for a gap."
    ),
    explanation_th=(
        "ป้ายนี้ (ป้ายข้อมูล 527.3 'การรวมช่องทาง') แสดงว่าช่องทางขวาสิ้นสุดและต้องรวมเข้ากับ "
        "ช่องอื่น ลูกศรสีแดงแสดงช่องที่สิ้นสุด คุณในฐานะผู้ขับรถในช่องขวาต้องให้ทาง "
        "กับรถในช่องที่คุณกำลังจะรวมเข้าไป – เปิดไฟเลี้ยว ปรับความเร็ว และรอจังหวะที่ว่าง"
    ),
    category="Traffic Rules",
    difficulty="medium",
    note="Added sign 527.3 'Sammenfletting' (right lane ends)",
    audit_verdict="MATCH",
    audit_image_identification="Opplysningsskilt 527.3 Sammenfletting (høyre felt opphører)",
)
print(f"Question id: {qid}")
