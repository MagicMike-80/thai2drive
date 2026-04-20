"""Insert 'No entry sign (302)' Traffic Signs question."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

qid = insert_image_question(
    image_path="/tmp/signs/no_entry.jpg",
    question_no="Kan du kjøre inn her?",
    question_en="Are you allowed to drive in here?",
    question_th="คุณสามารถขับเข้าไปทางนี้ได้หรือไม่?",
    options=[
        ("A",
         "Ja, hvis det ikke kommer trafikk",
         "Yes, if there is no traffic",
         "ได้ หากไม่มีรถมา"),
        ("B",
         "Ja, hvis du kjører forsiktig",
         "Yes, if you drive carefully",
         "ได้ หากขับอย่างระมัดระวัง"),
        ("C",
         "Nei, innkjøring er forbudt",
         "No, entry is prohibited",
         "ไม่ได้ ห้ามเข้า"),
        ("D",
         "Ja, men bare for korte stopp",
         "Yes, but only for short stops",
         "ได้ แต่เฉพาะหยุดสั้นๆ"),
    ],
    correct="C",
    explanation_no=(
        "Skiltet er forbudsskilt 302 'Innkjøring forbudt' (rødt sirkulært skilt med hvit "
        "horisontal strek). Det betyr at all kjøring inn i veien fra denne retningen er "
        "forbudt. Forbudet gjelder alle motorkjøretøy, også når det ser trygt ut eller "
        "veien er tom. Å kjøre forbi et slikt skilt gir bot og kan gi straffereaksjon."
    ),
    explanation_en=(
        "The sign is prohibition sign 302 'No entry' (a red circular sign with a white "
        "horizontal bar). It means all vehicle entry into the road from this direction is "
        "forbidden. The prohibition applies to all motor vehicles – even if the road looks "
        "empty or safe. Driving past this sign results in a fine and can lead to penalty "
        "points on your licence."
    ),
    explanation_th=(
        "ป้ายนี้คือป้ายห้าม 302 'ห้ามเข้า' (ป้ายวงกลมสีแดงมีแถบขาวแนวนอน) หมายถึงห้ามยานพาหนะ "
        "ทุกประเภทขับเข้าไปในถนนจากทิศทางนี้ ข้อห้ามนี้ใช้กับรถยนต์ทุกประเภท แม้ว่าถนน "
        "จะดูว่างหรือปลอดภัยก็ตาม การขับผ่านป้ายนี้จะถูกปรับและอาจได้รับโทษทางอาญา"
    ),
    category="Traffic Signs",
    difficulty="easy",
    note="Added sign 302 'Innkjøring forbudt' (No entry)",
    audit_verdict="MATCH",
    audit_image_identification="Forbudsskilt 302 Innkjøring forbudt",
)
print(f"Question id: {qid}")
