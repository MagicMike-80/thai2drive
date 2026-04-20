"""Insert 5 approved questions in batch, each matched to its image."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _insert_helper import insert_image_question  # noqa: E402

# === #1: Roundabout mandatory sign (406) ===
insert_image_question(
    image_path="/tmp/batch/img1_001102.jpg",
    question_no="Hva slags skilt er dette?",
    question_en="What type of sign is this?",
    question_th="นี่คือป้ายประเภทใด?",
    options=[
        ("A", "Fareskilt",        "Warning sign",     "ป้ายเตือน"),
        ("B", "Forbudsskilt",     "Prohibition sign", "ป้ายห้าม"),
        ("C", "Påbudsskilt",      "Mandatory sign",   "ป้ายบังคับ"),
        ("D", "Opplysningsskilt", "Information sign", "ป้ายข้อมูล"),
    ],
    correct="C",
    explanation_no=(
        "Dette er påbudsskilt 406 'Påbudt rundkjøring'. Blå, rund bakgrunn betyr påbud – "
        "du må følge den kjøreretningen som skiltet viser. Her betyr det at du skal kjøre "
        "i rundkjøring mot klokken."
    ),
    explanation_en=(
        "This is mandatory sign 406 'Roundabout ahead'. A blue circular sign indicates a "
        "mandatory instruction – you must follow the direction shown. Here it means you "
        "must drive counter-clockwise through the roundabout."
    ),
    explanation_th=(
        "นี่คือป้ายบังคับ 406 'วงเวียน' ป้ายวงกลมพื้นสีน้ำเงินหมายถึงคำสั่งบังคับ "
        "คุณต้องปฏิบัติตามทิศทางที่ป้ายแสดง ในที่นี้หมายความว่าคุณต้องขับในวงเวียน "
        "ทวนเข็มนาฬิกา"
    ),
    category="Traffic Signs", difficulty="easy",
    note="Batch 5/5: sign 406 Påbudt rundkjøring",
    audit_verdict="MATCH",
    audit_image_identification="Påbudsskilt 406 Påbudt rundkjøring",
)

# === #2: Motorway keep right ===
insert_image_question(
    image_path="/tmp/batch/img2_001053.jpg",
    question_no="Du kjører på motorvei med flere kjørefelt i samme retning. Hvordan bør du kjøre?",
    question_en="You are driving on a motorway with multiple lanes in the same direction. How should you drive?",
    question_th="คุณขับบนทางหลวงที่มีหลายเลน ควรขับอย่างไร?",
    options=[
        ("A", "Ligge i venstre felt hele tiden", "Stay in the left lane the whole time", "อยู่เลนซ้ายตลอด"),
        ("B", "Holde til høyre og kun bruke venstre felt ved forbikjøring",
         "Keep right and only use the left lane for overtaking",
         "ขับชิดขวาและใช้เลนซ้ายเมื่อแซงเท่านั้น"),
        ("C", "Kjøre midt i veien", "Drive in the middle", "ขับกลางถนน"),
        ("D", "Velge kjørefelt tilfeldig", "Choose any lane randomly", "เลือกเลนตามใจ"),
    ],
    correct="B",
    explanation_no=(
        "På motorvei (skilt 502) skal du holde til høyre og kun bruke venstre felt ved "
        "forbikjøring. Å ligge i venstre felt når høyre er ledig kalles 'venstrekjøring' "
        "og er forbudt. Husk å gå tilbake til høyre felt etter forbikjøring."
    ),
    explanation_en=(
        "On a motorway (sign 502) you must keep right and only use the left lane for "
        "overtaking. Staying in the left lane when the right is free is called 'left-lane "
        "hogging' and is prohibited. Remember to return to the right lane after overtaking."
    ),
    explanation_th=(
        "บนทางหลวง (ป้าย 502) คุณต้องขับชิดขวาและใช้เลนซ้ายเฉพาะเมื่อแซงเท่านั้น "
        "การอยู่ในเลนซ้ายเมื่อเลนขวาว่างเรียกว่า 'การครองเลนซ้าย' และเป็นสิ่งต้องห้าม "
        "อย่าลืมกลับมาเลนขวาหลังจากแซงเสร็จ"
    ),
    category="Traffic Rules", difficulty="easy",
    note="Batch 5/5: motorway keep right",
    audit_verdict="MATCH",
    audit_image_identification="Opplysningsskilt 502 Motorvei",
)

# === #3: Animals crossing (awareness) ===
insert_image_question(
    image_path="/tmp/batch/img3_001033a.jpg",
    question_no="Hva må du være spesielt oppmerksom på her?",
    question_en="What must you be especially aware of here?",
    question_th="คุณต้องระวังอะไรเป็นพิเศษที่นี่?",
    options=[
        ("A", "Glatt vei",                        "Slippery road",                  "ถนนลื่น"),
        ("B", "Dyr kan plutselig krysse veien",   "Animals may suddenly cross the road", "สัตว์อาจข้ามถนน"),
        ("C", "Fartskontroll",                    "Speed control",                  "ตรวจความเร็ว"),
        ("D", "Veiarbeid",                        "Road work",                      "งานถนน"),
    ],
    correct="B",
    explanation_no=(
        "På skogsveier og landeveier i Norge er det stor sjanse for at dyr som rein, "
        "elg eller rådyr plutselig kommer ut i veien. Senk farten, hold god avstand til "
        "veikanten, vær ekstra oppmerksom i skumring og natt, og vær klar til å stoppe. "
        "Ser du ett dyr – regn med at flere kan følge etter."
    ),
    explanation_en=(
        "On forest roads and country roads in Norway there is a high risk that animals "
        "such as reindeer, moose or deer will suddenly step onto the road. Reduce speed, "
        "keep a safe distance from the roadside, pay extra attention at dusk and at night, "
        "and be ready to stop. If you see one animal, expect more to follow."
    ),
    explanation_th=(
        "บนถนนป่าและถนนชนบทในนอร์เวย์มีความเสี่ยงสูงที่สัตว์ เช่น กวางเรนเดียร์ มูส "
        "หรือกวาง จะเดินออกมาบนถนนกะทันหัน ควรลดความเร็ว รักษาระยะห่างจากไหล่ทาง "
        "ระมัดระวังเป็นพิเศษในช่วงพลบค่ำและกลางคืน และพร้อมที่จะหยุด หากเห็นสัตว์ตัวหนึ่ง "
        "คาดว่าจะมีอีกตัวตามมา"
    ),
    category="Safety", difficulty="easy",
    note="Batch 5/5: animals crossing awareness (reindeer image)",
    audit_verdict="MATCH",
    audit_image_identification="Rein på veien i skogslandskap",
)

# === #4: Side road from right (124) ===
insert_image_question(
    image_path="/tmp/batch/img4_001044.jpg",
    question_no="Hva varsler dette skiltet?",
    question_en="What does this sign warn about?",
    question_th="ป้ายนี้เตือนอะไร?",
    options=[
        ("A", "Vikeplikt fra høyre",     "Yield to traffic from the right",    "ให้ทางจากขวา"),
        ("B", "Sidevei fra høyre",       "Side road from the right",           "มีถนนแยกจากขวา"),
        ("C", "Forkjørsvei slutter",     "Priority road ends",                 "ถนนหลักสิ้นสุด"),
        ("D", "Rundkjøring",              "Roundabout",                         "วงเวียน"),
    ],
    correct="B",
    explanation_no=(
        "Fareskilt 124 'Farlig vegkryss' varsler om en sidevei som kommer inn fra høyre. "
        "Du har forkjørsrett, men må være oppmerksom på trafikk som kan komme ut fra "
        "sideveien. Reduser farten og vær klar til å bremse."
    ),
    explanation_en=(
        "Warning sign 124 'Dangerous road junction' warns of a side road joining from the "
        "right. You have the right of way, but must stay alert for traffic that may pull "
        "out from the side road. Reduce speed and be ready to brake."
    ),
    explanation_th=(
        "ป้ายเตือน 124 'ทางแยกอันตราย' เตือนว่ามีถนนสายรองเข้าร่วมจากทางขวา "
        "คุณมีสิทธิ์ไปก่อน แต่ต้องระมัดระวังรถที่อาจออกมาจากถนนสายรอง "
        "ควรลดความเร็วและพร้อมที่จะเบรก"
    ),
    category="Traffic Signs", difficulty="easy",
    note="Batch 5/5: sign 124 Farlig vegkryss (side road from right)",
    audit_verdict="MATCH",
    audit_image_identification="Fareskilt 124 Farlig vegkryss (sidevei fra høyre)",
)

# === #5: Nordic countries wildlife ===
insert_image_question(
    image_path="/tmp/batch/img5_001033b.jpg",
    question_no="Hva må du være spesielt oppmerksom på når du kjører i nordiske land?",
    question_en="What must you be especially aware of when driving in Nordic countries?",
    question_th="คุณต้องระวังอะไรเป็นพิเศษเมื่อขับรถในประเทศแถบนอร์ดิก?",
    options=[
        ("A", "Høy temperatur",            "High temperatures",       "อุณหภูมิสูง"),
        ("B", "Ville dyr i veibanen",      "Wild animals on the road", "สัตว์ป่าในเลน"),
        ("C", "Sandstorm",                 "Sandstorms",              "พายุทราย"),
        ("D", "Tropisk regn",              "Tropical rain",           "ฝนเขตร้อน"),
    ],
    correct="B",
    explanation_no=(
        "I nordiske land som Norge, Sverige og Finland er det vanlig å møte ville dyr "
        "som elg, rein og rådyr på veien – særlig på landevei gjennom skog og fjell. "
        "Dyrene er mest aktive i skumring, ved daggry og om natten. Tilpass farten, "
        "bruk fjernlys når det er lov, og vær forberedt på at dyrene kan oppføre seg "
        "uforutsigbart."
    ),
    explanation_en=(
        "In Nordic countries like Norway, Sweden and Finland, encountering wild animals "
        "such as moose, reindeer and deer on the road is common – especially on country "
        "roads through forests and mountains. Animals are most active at dusk, dawn and "
        "at night. Adjust your speed, use high-beam lights where allowed, and be prepared "
        "for unpredictable animal behaviour."
    ),
    explanation_th=(
        "ในประเทศนอร์ดิก เช่น นอร์เวย์ สวีเดน และฟินแลนด์ พบสัตว์ป่าบนถนนเป็นเรื่องธรรมดา "
        "เช่น มูส กวางเรนเดียร์ และกวาง โดยเฉพาะบนถนนชนบทผ่านป่าและภูเขา สัตว์จะเคลื่อนไหว "
        "มากที่สุดในช่วงพลบค่ำ รุ่งอรุณ และกลางคืน ควรปรับความเร็ว ใช้ไฟสูงเมื่อได้รับอนุญาต "
        "และเตรียมพร้อมสำหรับพฤติกรรมที่คาดเดาไม่ได้ของสัตว์"
    ),
    category="Safety", difficulty="easy",
    note="Batch 5/5 COMPLETE: Nordic wildlife awareness",
    audit_verdict="MATCH",
    audit_image_identification="Rein på veien i nordisk skogslandskap",
)

print("\n✅ All 5 questions inserted successfully!")
