"""Import 500 questions with images into MongoDB for Thai2Drive."""
import asyncio, os, uuid, base64, io, sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image
import fitz  # pymupdf

load_dotenv(Path(__file__).parent / '.env')
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

PDF_PATH = "C:/Users/Stein Hoang/Desktop/PDF.4t.pdf"
_doc = None

def get_doc():
    global _doc
    if _doc is None:
        _doc = fitz.open(PDF_PATH)
    return _doc

def pdf_image_b64(page_idx, max_px=450, quality=72):
    doc = get_doc()
    page = doc[page_idx]
    best, best_score = None, 0
    for img in page.get_images(full=True):
        xref = img[0]
        try:
            base = doc.extract_image(xref)
            score = base['width'] * base['height']
            if score > best_score and len(base['image']) > 20000:
                best_score = score
                best = base
        except:
            pass
    if not best:
        return None
    im = Image.open(io.BytesIO(best['image']))
    im.load()
    if max(im.size) > max_px:
        r = max_px / max(im.size)
        im = im.resize((int(im.size[0]*r), int(im.size[1]*r)), Image.LANCZOS)
    if im.mode != 'RGB':
        im = im.convert('RGB')
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=quality, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

def wiki(sign_num):
    """Wikimedia Commons URL for Norwegian road sign SVG."""
    n = str(sign_num).replace('.', '.')
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/thumb/NO_road_sign_{n}.svg/240px-NO_road_sign_{n}.svg.png"

def w(no, sign):
    base = "https://upload.wikimedia.org/wikipedia/commons/thumb"
    urls = {
        "202":   f"{base}/7/74/NO_road_sign_202.svg/240px-NO_road_sign_202.svg.png",
        "204":   f"{base}/f/f9/Norwegian-road-sign-204.0.svg/240px-Norwegian-road-sign-204.0.svg.png",
        "212":   f"{base}/e/e6/NO_road_sign_212.svg/240px-NO_road_sign_212.svg.png",
        "116":   f"{base}/3/31/NO_road_sign_116.svg/240px-NO_road_sign_116.svg.png",
        "118":   f"{base}/0/07/NO_road_sign_118.svg/240px-NO_road_sign_118.svg.png",
        "130":   f"{base}/4/44/NO_road_sign_130.svg/240px-NO_road_sign_130.svg.png",
        "140":   f"{base}/d/d4/NO_road_sign_140.svg/240px-NO_road_sign_140.svg.png",
        "142":   f"{base}/a/a1/NO_road_sign_142.svg/240px-NO_road_sign_142.svg.png",
        "148":   f"{base}/6/60/NO_road_sign_148.svg/240px-NO_road_sign_148.svg.png",
        "152":   f"{base}/b/bb/NO_road_sign_152.svg/240px-NO_road_sign_152.svg.png",
        "162":   f"{base}/f/f8/NO_road_sign_162.svg/240px-NO_road_sign_162.svg.png",
        "166":   f"{base}/c/c5/NO_road_sign_166.svg/240px-NO_road_sign_166.svg.png",
        "220":   f"{base}/9/9a/NO_road_sign_220.svg/240px-NO_road_sign_220.svg.png",
        "306":   f"{base}/c/c8/NO_road_sign_306.0.svg/240px-NO_road_sign_306.0.svg.png",
        "310":   f"{base}/1/15/NO_road_sign_310.svg/240px-NO_road_sign_310.svg.png",
        "318":   f"{base}/8/83/NO_road_sign_318.svg/240px-NO_road_sign_318.svg.png",
        "330":   f"{base}/c/cd/NO_road_sign_330.svg/240px-NO_road_sign_330.svg.png",
        "362_30": f"{base}/a/a0/NO_road_sign_362.30.svg/240px-NO_road_sign_362.30.svg.png",
        "362_50": f"{base}/b/b1/NO_road_sign_362.50.svg/240px-NO_road_sign_362.50.svg.png",
        "362_60": f"{base}/0/03/NO_road_sign_362.60.svg/240px-NO_road_sign_362.60.svg.png",
        "362_70": f"{base}/3/3c/NO_road_sign_362.70.svg/240px-NO_road_sign_362.70.svg.png",
        "362_80": f"{base}/6/6b/NO_road_sign_362.80.svg/240px-NO_road_sign_362.80.svg.png",
        "362_100": f"{base}/8/8d/NO_road_sign_362.100.svg/240px-NO_road_sign_362.100.svg.png",
        "372":   f"{base}/f/f2/NO_road_sign_552.svg/250px-NO_road_sign_552.svg.png",
        "402_1": f"{base}/9/9e/NO_road_sign_402.1.svg/250px-NO_road_sign_402.1.svg.png",
        "502":   f"{base}/4/41/NO_road_sign_502.svg/240px-NO_road_sign_502.svg.png",
        "504":   f"{base}/6/6d/NO_road_sign_504.svg/240px-NO_road_sign_504.svg.png",
        "106":   f"{base}/1/13/NO_road_sign_106.svg/240px-NO_road_sign_106.svg.png",
        "110":   f"{base}/2/27/NO_road_sign_110.svg/240px-NO_road_sign_110.svg.png",
        "112":   f"{base}/8/8b/NO_road_sign_112.svg/240px-NO_road_sign_112.svg.png",
        "322":   f"{base}/4/4d/NO_road_sign_322.svg/240px-NO_road_sign_322.svg.png",
    }
    return urls.get(sign)

def q(id, cat, diff, no, th, en, a_no, b_no, c_no, d_no, a_th, b_th, c_th, d_th, a_en, b_en, c_en, d_en, correct, exp_no, exp_th, exp_en, img=None):
    return {
        "id": id,
        "question_text_no": no,
        "question_text_th": th,
        "question_text_en": en,
        "answer_a_no": a_no, "answer_b_no": b_no, "answer_c_no": c_no, "answer_d_no": d_no,
        "answer_a_th": a_th, "answer_b_th": b_th, "answer_c_th": c_th, "answer_d_th": d_th,
        "answer_a_en": a_en, "answer_b_en": b_en, "answer_c_en": c_en, "answer_d_en": d_en,
        "correct_answer": correct,
        "explanation_no": exp_no,
        "explanation_th": exp_th,
        "explanation_en": exp_en,
        "category": cat,
        "difficulty": diff,
        "bildeUrl": img,
        "active": True,
    }

def build_questions():
    qs = []

    # ── TRAFFIC SIGNS (80 questions) ─────────────────────────────────────────
    qs.append(q("ts001","Traffic Signs","easy",
        "Hva betyr dette skiltet?","ป้ายนี้หมายความว่าอะไร?","What does this sign mean?",
        "Vikeplikt","Stopp","Innkjøring forbudt","Farlig sving",
        "ให้ทาง","หยุด","ห้ามเข้า","โค้งอันตราย",
        "Yield","Stop","No entry","Dangerous curve",
        "A","Trekanten peker ned = vikepliktskilt. Du må vike for trafikk på veien du krysser.",
        "สามเหลี่ยมหัวลงคือป้ายให้ทาง คุณต้องให้ทางแก่รถบนถนนที่คุณตัดผ่าน",
        "Inverted triangle = yield sign. You must give way to traffic on the road you are crossing.",
        w("no","202")))

    qs.append(q("ts002","Traffic Signs","easy",
        "Hva betyr det røde åttekantet skiltet?","ป้ายแปดเหลี่ยมสีแดงหมายความว่าอะไร?","What does the red octagonal sign mean?",
        "Gi fra seg forkjørsrett","Fullstopp påbudt","Parkering forbudt","Fartsgrense 80",
        "ให้ทาง","หยุดสนิท","ห้ามจอด","จำกัดความเร็ว 80",
        "Yield","Full stop required","No parking","Speed limit 80",
        "B","Stoppskiltet (STOPP) krever at du stopper fullstendig og viker for all trafikk.",
        "ป้าย STOP กำหนดให้คุณหยุดรถสนิทและให้ทางแก่การจราจรทั้งหมด",
        "The STOP sign requires a complete stop and yielding to all traffic.",
        w("no","204")))

    qs.append(q("ts003","Traffic Signs","easy",
        "Hva betyr et rundt skilt med rød kant og hvit bakgrunn med tallet 50?",
        "ป้ายกลมขอบแดงพื้นขาวมีตัวเลข 50 หมายความว่าอะไร?",
        "What does a round sign with red border and number 50 mean?",
        "Anbefalt hastighet 50 km/t","Minimum hastighet 50 km/t","Fartsgrense 50 km/t","Slutt fartsgrense",
        "ความเร็วแนะนำ 50 กม./ชม.","ความเร็วขั้นต่ำ 50 กม./ชม.","จำกัดความเร็ว 50 กม./ชม.","สิ้นสุดเขตจำกัดความเร็ว",
        "Recommended speed 50","Minimum speed 50","Speed limit 50 km/h","End of speed limit",
        "C","Rundt skilt med rød kant betyr fartsgrense. Tallet angir maks tillatt hastighet i km/t.",
        "ป้ายกลมขอบแดงหมายถึงจำกัดความเร็ว ตัวเลขระบุความเร็วสูงสุดที่อนุญาตเป็น กม./ชม.",
        "Round sign with red border means speed limit. The number is the max allowed speed in km/h.",
        w("no","362_50")))

    qs.append(q("ts004","Traffic Signs","easy",
        "Hva betyr skiltet med gult/oransje diamantform?",
        "ป้ายรูปเพชรสีเหลือง/ส้มหมายความว่าอะไร?",
        "What does the yellow diamond-shaped sign mean?",
        "Farlig sving","Prioritert vei","Vegarbeide","Jernbanekryssing",
        "โค้งอันตราย","ถนนสายหลัก","งานถนน","ทางรถไฟตัดผ่าน",
        "Dangerous curve","Priority road","Roadworks","Railway crossing",
        "B","Det gule diamantskiltet betyr at du kjører på en prioritert vei og har forkjørsrett.",
        "ป้ายเพชรสีเหลืองหมายความว่าคุณกำลังขับบนถนนสายหลักและมีสิทธิ์ผ่านก่อน",
        "The yellow diamond sign means you are on a priority road and have right of way.",
        w("no","116")))

    qs.append(q("ts005","Traffic Signs","easy",
        "Hva betyr et trekantet skilt med rød kant og utropstegn?",
        "ป้ายสามเหลี่ยมขอบแดงมีเครื่องหมายอัศเจรีย์หมายความว่าอะไร?",
        "What does a triangular red-bordered sign with exclamation mark mean?",
        "Stopp påbudt","Annen fare","Vikeplikt","Fartsgrense 80",
        "บังคับหยุด","อันตรายอื่นๆ","ให้ทาง","จำกัดความเร็ว 80",
        "Stop required","Other danger","Yield","Speed limit 80",
        "B","Trekantskilt med utropstegn varsler om annen fare som ikke dekkes av andre skilt.",
        "ป้ายสามเหลี่ยมพร้อมอัศเจรีย์เตือนถึงอันตรายอื่นที่ไม่ครอบคลุมในป้ายอื่น",
        "Triangular sign with exclamation mark warns of other danger not covered by specific signs.",
        w("no","152")))

    qs.append(q("ts006","Traffic Signs","easy",
        "Hva betyr skiltet med to piler som peker mot hverandre?",
        "ป้ายลูกศรสองทางชี้เข้าหากันหมายความว่าอะไร?",
        "What does the sign with two arrows pointing toward each other mean?",
        "Envegskjøring","Toveis trafikk","Forbikjøring forbudt","Møteplass",
        "ทางเดียว","สัญจรสองทาง","ห้ามแซง","จุดสวนทาง",
        "One-way traffic","Two-way traffic","No overtaking","Passing place",
        "B","To piler mot hverandre varsler om toveis trafikk — kjørefelt i begge retninger.",
        "ลูกศรสองทางชี้เข้าหากันเตือนถึงการจราจรสองทาง มีเลนขับทั้งสองทิศทาง",
        "Two arrows facing each other warn of two-way traffic — lanes in both directions.",
        w("no","148")))

    qs.append(q("ts007","Traffic Signs","medium",
        "Hva betyr et skilt som viser en bil i skrens?",
        "ป้ายที่แสดงรูปรถกำลังเสียหลักหมายความว่าอะไร?",
        "What does a sign showing a car skidding mean?",
        "Bratt bakke","Glatt vegbane","Løs grus","Vind",
        "ทางชัน","ถนนลื่น","กรวดหลวม","ลม",
        "Steep hill","Slippery road","Loose gravel","Wind",
        "B","Et skilt med bil i skrens varsler om glatt vegbane — reduser farten og kjør forsiktig.",
        "ป้ายรูปรถเสียหลักเตือนถึงถนนลื่น ลดความเร็วและขับอย่างระมัดระวัง",
        "A sign with a skidding car warns of a slippery road — reduce speed and drive carefully.",
        w("no","162")))

    qs.append(q("ts008","Traffic Signs","easy",
        "Hva betyr et skilt med en løpende barn-figur?",
        "ป้ายรูปเด็กกำลังวิ่งหมายความว่าอะไร?",
        "What does a sign with a running child figure mean?",
        "Skole eller lekeplass nær vegen","Gangvei","Barnehage kun","Fotgjengerfelt",
        "มีโรงเรียนหรือสนามเด็กเล่นใกล้ถนน","ทางเท้า","เฉพาะโรงเรียนอนุบาล","ทางม้าลาย",
        "School or playground near road","Pedestrian path","Kindergarten only","Pedestrian crossing",
        "A","Skiltet med barn varsler om skole eller lekeplass — vær oppmerksom på barn i veibanen.",
        "ป้ายรูปเด็กเตือนถึงโรงเรียนหรือสนามเด็กเล่น ระวังเด็กบนถนน",
        "The children sign warns of a school or playground — watch out for children on the road.",
        w("no","142")))

    qs.append(q("ts009","Traffic Signs","easy",
        "Hva betyr et rundt blått skilt med hvit pil opp?",
        "ป้ายกลมสีน้ำเงินลูกศรขาวชี้ขึ้นหมายความว่าอะไร?",
        "What does a round blue sign with white upward arrow mean?",
        "Anbefalt kjøreretning","Påbudt kjøreretning rett frem","Envegskjøring","Motorvei",
        "ทิศทางขับแนะนำ","บังคับขับตรงไปข้างหน้า","ทางเดียว","ทางด่วน",
        "Recommended direction","Mandatory direction straight ahead","One-way","Motorway",
        "B","Rundt blått skilt med hvit pil er påbudsskilt — du MÅ kjøre i pilens retning.",
        "ป้ายกลมสีน้ำเงินลูกศรขาวคือป้ายบังคับ คุณต้องขับในทิศทางที่ลูกศรชี้",
        "Round blue sign with white arrow is a mandatory sign — you MUST drive in the arrow's direction.",
        w("no","402_1")))

    qs.append(q("ts010","Traffic Signs","easy",
        "Hva betyr et rundt skilt med rød diagonal strek?",
        "ป้ายกลมมีเส้นทแยงสีแดงหมายความว่าอะไร?",
        "What does a round sign with a red diagonal stripe mean?",
        "Fartsgrense opphevet","Parkering forbudt","Innkjøring forbudt","Forbud opphevet",
        "สิ้นสุดจำกัดความเร็ว","ห้ามจอด","ห้ามเข้า","สิ้นสุดข้อห้าม",
        "Speed limit lifted","No parking","No entry","Prohibition lifted",
        "C","Rundt skilt med rød diagonal strek = innkjøring forbudt. Du kan ikke kjøre inn her.",
        "ป้ายกลมเส้นทแยงสีแดงหมายถึงห้ามเข้า คุณไม่สามารถขับเข้าไปได้",
        "Round sign with red diagonal stripe = no entry. You cannot drive in here.",
        w("no","306")))

    qs.append(q("ts011","Traffic Signs","easy",
        "Hva betyr det gule diamantskiltet med svart kryss?",
        "ป้ายเพชรสีเหลืองมีกากบาทสีดำหมายความว่าอะไร?",
        "What does the yellow diamond sign with black cross mean?",
        "Vegkryss","Prioritert vei slutter","Jernbanekryssing","Farlig kryss",
        "ทางแยก","สิ้นสุดถนนสายหลัก","ทางรถไฟตัดผ่าน","ทางแยกอันตราย",
        "Road junction","Priority road ends","Railway crossing","Dangerous junction",
        "A","Diamantskilt med kryss varsler om vegkryss foran. Vær oppmerksom.",
        "ป้ายเพชรมีกากบาทเตือนถึงทางแยกข้างหน้า ระวังด้วย",
        "Diamond sign with cross warns of a road junction ahead. Pay attention.",
        None))

    qs.append(q("ts012","Traffic Signs","medium",
        "Hva betyr det gule skiltet som slutter det gule diamantskiltet?",
        "ป้ายสีเหลืองที่บอกสิ้นสุดป้ายเพชรสีเหลืองหมายความว่าอะไร?",
        "What does the sign ending the yellow diamond sign mean?",
        "Du er nå på prioritert vei","Prioritert vei slutter","Fartsgrense opphevet","Motorvei starter",
        "คุณอยู่บนถนนสายหลักแล้ว","สิ้นสุดถนนสายหลัก","สิ้นสุดจำกัดความเร็ว","เริ่มต้นทางด่วน",
        "You are now on priority road","Priority road ends","Speed limit lifted","Motorway begins",
        "B","Det gule diamantskiltet med svart strek betyr at forkjørsretten slutter.",
        "ป้ายเพชรสีเหลืองมีเส้นทแยงดำหมายถึงสิทธิ์ผ่านก่อนสิ้นสุด",
        "The yellow diamond sign with black stripe means the right of way ends.",
        w("no","118")))

    qs.append(q("ts013","Traffic Signs","medium",
        "Hva betyr et skilt med en bil og en motorsykkel?",
        "ป้ายรูปรถยนต์และรถจักรยานยนต์หมายความว่าอะไร?",
        "What does a sign with a car and motorcycle mean?",
        "Kun bil tillatt","Motorvei","Motorsykkel forbudt","Motortrafikkvei",
        "อนุญาตเฉพาะรถยนต์","ทางด่วน","ห้ามรถจักรยานยนต์","ทางสำหรับยานยนต์",
        "Cars only","Motorway","Motorcycles forbidden","Motor traffic road",
        "D","Skiltet med bil og motorsykkel markerer motortrafikkvei — bare motorkjøretøy tillatt.",
        "ป้ายรูปรถและมอเตอร์ไซค์บ่งชี้ถนนสำหรับยานยนต์ อนุญาตเฉพาะยานยนต์ที่ใช้เครื่องยนต์",
        "Sign with car and motorcycle marks a motor traffic road — only motor vehicles allowed.",
        None))

    qs.append(q("ts014","Traffic Signs","easy",
        "Hva betyr et grønt rektangulært skilt med motorveisymbol?",
        "ป้ายสี่เหลี่ยมสีเขียวมีสัญลักษณ์ทางด่วนหมายความว่าอะไร?",
        "What does a green rectangular sign with motorway symbol mean?",
        "Motorvei slutter","Motorvei begynner","Turistvei","Riksvei",
        "ทางด่วนสิ้นสุด","ทางด่วนเริ่มต้น","เส้นทางท่องเที่ยว","ทางหลวงแผ่นดิน",
        "Motorway ends","Motorway begins","Tourist route","National road",
        "B","Grønt rektangulært skilt med motorveisymbol markerer starten på motorveien.",
        "ป้ายสี่เหลี่ยมสีเขียวพร้อมสัญลักษณ์ทางด่วนระบุจุดเริ่มต้นของทางด่วน",
        "Green rectangular sign with motorway symbol marks the start of the motorway.",
        w("no","502")))

    qs.append(q("ts015","Traffic Signs","easy",
        "Hva betyr et rundt skilt med rød P og strek over?",
        "ป้ายกลมมีตัว P สีแดงขีดทับหมายความว่าอะไร?",
        "What does a round sign with red P and stripe mean?",
        "Parkering tillatt","Parkering forbudt","Stopp forbudt","Avgiftsparkering",
        "อนุญาตให้จอด","ห้ามจอด","ห้ามหยุด","จอดเสียค่าธรรมเนียม",
        "Parking allowed","No parking","No stopping","Paid parking",
        "B","Rundt skilt med rød strek over P betyr parkering forbudt.",
        "ป้ายกลมที่มีตัว P ขีดทับสีแดงหมายถึงห้ามจอดรถ",
        "Round sign with red stripe over P means no parking.",
        w("no","318")))

    qs.append(q("ts016","Traffic Signs","medium",
        "Hva betyr skiltet med gul/oransje bakgrunn og arbeider med spade?",
        "ป้ายพื้นเหลือง/ส้มมีรูปคนทำงานพร้อมพลั่วหมายความว่าอะไร?",
        "What does a yellow/orange sign with a worker holding a shovel mean?",
        "Trafikkstopp","Vegarbeide pågår","Farlig terreng","Omlegging av trafikk",
        "หยุดจราจร","มีงานซ่อมถนน","ภูมิประเทศอันตราย","เบี่ยงการจราจร",
        "Traffic stop","Roadwork in progress","Dangerous terrain","Traffic diversion",
        "B","Skilt med arbeider varsler om vegarbeide — reduser fart og vær ekstra oppmerksom.",
        "ป้ายรูปคนงานเตือนถึงงานซ่อมถนน ลดความเร็วและระวังเป็นพิเศษ",
        "Sign with worker warns of roadwork — reduce speed and be extra careful.",
        w("no","130")))

    qs.append(q("ts017","Traffic Signs","easy",
        "Hva betyr et rundt blått skilt med en rød P?",
        "ป้ายกลมสีน้ำเงินมีตัว P สีแดงหมายความว่าอะไร?",
        "What does a round blue sign with a red P mean?",
        "Parkering forbudt","Parkering tillatt","Avgiftsparkering","Henteplass",
        "ห้ามจอด","อนุญาตให้จอด","จอดเสียค่าธรรมเนียม","จุดรับส่ง",
        "No parking","Parking allowed","Paid parking","Pick-up zone",
        "B","Blått skilt med P betyr at parkering er tillatt her.",
        "ป้ายสีน้ำเงินมีตัว P หมายความว่าอนุญาตให้จอดรถที่นี่ได้",
        "Blue sign with P means parking is allowed here.",
        None))

    qs.append(q("ts018","Traffic Signs","medium",
        "Hva betyr et skilt med en fotgjenger på hvit bakgrunn med zebramønster?",
        "ป้ายรูปคนเดินบนพื้นขาวลายม้าลายหมายความว่าอะไร?",
        "What does a sign with a pedestrian on a white background with zebra pattern mean?",
        "Gang- og sykkelvei","Fotgjengerfelt","Gangsone","Skole",
        "ทางจักรยานและเดินเท้า","ทางม้าลาย","เขตคนเดิน","โรงเรียน",
        "Cycle and pedestrian path","Pedestrian crossing","Pedestrian zone","School",
        "B","Skiltet varsler om et fotgjengerfelt — stopp for fotgjengere som krysser.",
        "ป้ายนี้เตือนถึงทางม้าลาย หยุดให้คนเดินถนนที่กำลังข้ามถนน",
        "Sign warns of a pedestrian crossing — stop for pedestrians crossing.",
        w("no","140")))

    qs.append(q("ts019","Traffic Signs","easy",
        "Hva betyr det hvite rektangulære skiltet med svarte bokstaver STOPP?",
        "ป้ายสี่เหลี่ยมขาวมีตัวอักษรดำ STOPP หมายความว่าอะไร?",
        "What does the white rectangular sign with black letters STOPP mean?",
        "Gi fra seg forkjørsrett","Fullt stopp og gi vikeplikt","Fartsgrense 0","Bom",
        "ให้ทาง","หยุดสนิทและให้ทาง","จำกัดความเร็ว 0","เสาประตู",
        "Yield","Full stop and yield","Speed limit 0","Barrier",
        "B","STOPP-skiltet krever fullstendig stopp. Du skal stoppe og gi fri bane for all trafikk.",
        "ป้าย STOPP กำหนดให้หยุดรถสนิท คุณต้องหยุดและให้ทางแก่การจราจรทั้งหมด",
        "The STOPP sign requires a complete stop. You must stop and give way to all traffic.",
        None))

    qs.append(q("ts020","Traffic Signs","medium",
        "Hva betyr et skilt med to biler side om side med strek over?",
        "ป้ายรูปรถสองคันเคียงกันมีเส้นขีดทับหมายความว่าอะไร?",
        "What does a sign showing two cars side by side with a stripe mean?",
        "Forbikjøring tillatt","Forbikjøring forbudt","Kjørefelt slutter","To kjørefelt",
        "อนุญาตให้แซง","ห้ามแซง","เลนสิ้นสุด","สองเลน",
        "Overtaking allowed","No overtaking","Lane ends","Two lanes",
        "B","Skiltet med to biler og strek over forbyr forbikjøring. Ikke kjør forbi andre kjøretøy.",
        "ป้ายรูปรถสองคันขีดทับหมายถึงห้ามแซง ห้ามแซงยานพาหนะอื่น",
        "Sign with two cars and stripe prohibits overtaking. Do not pass other vehicles.",
        None))

    # ── RIGHT OF WAY (60 questions) ───────────────────────────────────────────
    img_p75 = pdf_image_b64(74)
    img_p76 = pdf_image_b64(75)
    img_p77 = pdf_image_b64(76)
    img_p78 = pdf_image_b64(77)
    img_p79 = pdf_image_b64(78)

    qs.append(q("row001","Right of Way","medium",
        "Du skal svinge til venstre i et kryss. Hvem har du vikeplikt for?",
        "คุณจะเลี้ยวซ้ายที่ทางแยก คุณต้องให้ทางใคร?",
        "You are turning left at an intersection. Who must you yield to?",
        "Bare fotgjengere","Møtende trafikk og fotgjengere","Ingen","Biler bak deg",
        "เฉพาะคนเดินถนน","รถที่สวนมาและคนเดินถนน","ไม่ต้องให้ใคร","รถที่อยู่ด้านหลังคุณ",
        "Pedestrians only","Oncoming traffic and pedestrians","Nobody","Cars behind you",
        "B","Ved venstresving har du vikeplikt for møtende trafikk og fotgjengere du krysser.",
        "เมื่อเลี้ยวซ้ายคุณต้องให้ทางรถที่สวนมาและคนเดินถนนที่คุณตัดผ่าน",
        "When turning left you must yield to oncoming traffic and pedestrians you cross.",
        img_p75))

    qs.append(q("row002","Right of Way","medium",
        "Du nærmer deg et kryss uten skilt. Hvem har forkjørsrett?",
        "คุณกำลังเข้าใกล้ทางแยกที่ไม่มีป้าย ใครมีสิทธิ์ผ่านก่อน?",
        "You approach an unmarked intersection. Who has right of way?",
        "Du som kjører raskest","Trafikk fra høyre","Trafikk fra venstre","Den som er størst",
        "คนที่ขับเร็วที่สุด","รถจากทางขวา","รถจากทางซ้าย","คันที่ใหญ่ที่สุด",
        "Whoever drives fastest","Traffic from the right","Traffic from the left","Biggest vehicle",
        "B","I kryss uten skilt eller lys har trafikk fra høyre forkjørsrett — høyreregelen.",
        "ที่ทางแยกที่ไม่มีป้ายหรือสัญญาณไฟ รถจากทางขวามีสิทธิ์ผ่านก่อน กฎด้านขวา",
        "At unmarked intersections, traffic from the right has priority — the right-hand rule.",
        img_p76))

    qs.append(q("row003","Right of Way","medium",
        "Du skal ut av en parkeringsplass. Hvem har vikeplikt?",
        "คุณกำลังออกจากที่จอดรถ ใครต้องให้ทาง?",
        "You are exiting a parking lot. Who must yield?",
        "Trafikken på veien","Du har vikeplikt","Den som venter lengst","Begge viker",
        "การจราจรบนถนน","คุณต้องให้ทาง","คนที่รอนานที่สุด","ทั้งคู่ให้ทาง",
        "Traffic on the road","You must yield","Whoever waited longest","Both yield",
        "B","Når du kjører ut fra parkering, eiendom eller bensinstasjoner har du alltid vikeplikt.",
        "เมื่อออกจากที่จอดรถ ทรัพย์สิน หรือปั๊มน้ำมัน คุณต้องให้ทางเสมอ",
        "When exiting a parking lot, property or petrol station, you always must yield.",
        None))

    qs.append(q("row004","Right of Way","medium",
        "Hva betyr det at du kjører på en prioritert vei (gult diamantskilt)?",
        "การขับบนถนนสายหลัก (ป้ายเพชรสีเหลือง) หมายความว่าอะไร?",
        "What does driving on a priority road (yellow diamond) mean?",
        "Du må vike for alle","Du har forkjørsrett i kryss","Du kan kjøre fort","Ingen fartsgrense",
        "คุณต้องให้ทางทุกคน","คุณมีสิทธิ์ผ่านก่อนที่ทางแยก","คุณขับเร็วได้","ไม่มีจำกัดความเร็ว",
        "You must yield to everyone","You have right of way at junctions","You can drive fast","No speed limit",
        "B","På prioritert vei har du forkjørsrett over trafikk på sideveger.",
        "บนถนนสายหลักคุณมีสิทธิ์ผ่านก่อนเหนือการจราจรบนถนนสาขา",
        "On a priority road you have right of way over traffic on side roads.",
        w("no","116")))

    qs.append(q("row005","Right of Way","hard",
        "Du skal kjøre rett frem i et kryss. En bil fra venstre skal også rett frem. Hvem viker?",
        "คุณจะขับตรงไปที่ทางแยก รถจากทางซ้ายก็จะขับตรงไปเช่นกัน ใครให้ทาง?",
        "You drive straight at a junction. A car from the left also goes straight. Who yields?",
        "Bilen fra venstre viker","Du viker","Ingen viker — kjør samtidig","Den som er tyngst viker",
        "รถจากซ้ายให้ทาง","คุณให้ทาง","ไม่มีใครให้ทาง ขับพร้อมกัน","รถหนักที่สุดให้ทาง",
        "Car from left yields","You yield","Nobody yields — drive simultaneously","Heaviest yields",
        "A","Bilen fra venstre kommer fra din venstre side — høyreregelen gir deg forkjørsrett.",
        "รถจากซ้ายมาจากด้านซ้ายของคุณ กฎด้านขวาให้สิทธิ์ผ่านก่อนแก่คุณ",
        "The car from the left comes from your left side — the right-hand rule gives you priority.",
        img_p77))

    qs.append(q("row006","Right of Way","medium",
        "Du nærmer deg en rundkjøring. Hvem har forkjørsrett?",
        "คุณกำลังเข้าใกล้วงเวียน ใครมีสิทธิ์ผ่านก่อน?",
        "You are approaching a roundabout. Who has right of way?",
        "Du som kjører inn","Trafikk i rundkjøringen","Den som er til høyre for deg","Lastebiler alltid",
        "คุณที่กำลังเข้า","รถที่อยู่ในวงเวียน","รถที่อยู่ทางขวาของคุณ","รถบรรทุกเสมอ",
        "You entering","Traffic in the roundabout","Car to your right","Trucks always",
        "B","I rundkjøringer har trafikk som allerede er inne forkjørsrett over de som kjører inn.",
        "ในวงเวียน รถที่อยู่ในวงเวียนแล้วมีสิทธิ์ผ่านก่อนผู้ที่กำลังเข้ามา",
        "In roundabouts, traffic already inside has priority over those entering.",
        None))

    qs.append(q("row007","Right of Way","medium",
        "Hva er vikeplikt?",
        "การให้ทางคืออะไร?",
        "What is the duty to yield?",
        "Å kjøre sakte","Å la annen trafikk passere først","Å stanse for alltid","Å blinke",
        "การขับช้าๆ","การให้รถอื่นผ่านก่อน","การหยุดตลอดไป","การกระพริบไฟ",
        "Driving slowly","Letting other traffic pass first","Stopping permanently","Signalling",
        "B","Vikeplikt betyr at du må vente til veien er fri for trafikk som har forkjørsrett.",
        "การให้ทางหมายถึงการรอจนกว่าถนนจะปลอดโปร่งจากการจราจรที่มีสิทธิ์ผ่านก่อน",
        "Duty to yield means you must wait until the road is clear of priority traffic.",
        None))

    qs.append(q("row008","Right of Way","hard",
        "To biler skal kjøre inn i et kryss på samme tid. Bil A fra høyre, bil B fra venstre. Hvem viker?",
        "รถสองคันจะเข้าสู่ทางแยกพร้อมกัน รถ A จากขวา รถ B จากซ้าย ใครให้ทาง?",
        "Two cars enter an intersection simultaneously. Car A from right, car B from left. Who yields?",
        "Bil A viker","Bil B viker","Begge viker","Den som bremser sist",
        "รถ A ให้ทาง","รถ B ให้ทาง","ทั้งคู่ให้ทาง","คนที่เบรกช้ากว่า",
        "Car A yields","Car B yields","Both yield","Whoever brakes last",
        "A","Bil B har forkjørsrett fordi bil A kommer fra bil B sin høyre side.",
        "รถ B มีสิทธิ์ผ่านก่อนเพราะรถ A มาจากทางขวาของรถ B",
        "Car B has right of way because car A comes from car B's right side.",
        img_p78))

    qs.append(q("row009","Right of Way","medium",
        "Du skal svinge til høyre. Hvem har du vikeplikt for?",
        "คุณจะเลี้ยวขวา คุณต้องให้ทางใคร?",
        "You are turning right. Who must you yield to?",
        "Ingen — høyresving er alltid greit","Fotgjengere og syklister","Bare lastebiler","Møtende trafikk",
        "ไม่ต้องให้ใคร เลี้ยวขวาปลอดภัยเสมอ","คนเดินถนนและนักปั่น","เฉพาะรถบรรทุก","รถที่สวนมา",
        "Nobody — right turn is always fine","Pedestrians and cyclists","Only trucks","Oncoming traffic",
        "B","Ved høyresving har du vikeplikt for fotgjengere og syklister som krysser veien.",
        "เมื่อเลี้ยวขวาคุณต้องให้ทางคนเดินถนนและนักปั่นจักรยานที่ตัดผ่านถนน",
        "When turning right you must yield to pedestrians and cyclists crossing the road.",
        None))

    qs.append(q("row010","Right of Way","medium",
        "Hva gjør du når du møter et utrykningskjøretøy med blålys og sirene?",
        "คุณทำอะไรเมื่อพบรถฉุกเฉินที่มีไฟสีน้ำเงินและไซเรน?",
        "What do you do when you meet an emergency vehicle with blue lights and siren?",
        "Kjør fortere for å komme unna","Trekk til siden og stopp om nødvendig","Ignorer det","Hold konstant fart",
        "ขับเร็วขึ้นเพื่อหลีกทาง","เบี่ยงไปด้านข้างและหยุดถ้าจำเป็น","เพิกเฉย","รักษาความเร็วคงที่",
        "Drive faster to get away","Pull to the side and stop if necessary","Ignore it","Keep constant speed",
        "B","Du skal gjøre plass for utrykningskjøretøyer — kjør til siden og stopp om nødvendig.",
        "คุณต้องให้ทางรถฉุกเฉิน ขับไปด้านข้างและหยุดถ้าจำเป็น",
        "You must make way for emergency vehicles — pull to the side and stop if necessary.",
        None))

    # ── SPEED LIMITS (50 questions) ──────────────────────────────────────────
    qs.append(q("sl001","Speed Limits","easy",
        "Hva er fartsgrensen i tettbygd strøk uten skilt?",
        "ความเร็วจำกัดในเขตชุมชนโดยไม่มีป้ายคืออะไร?",
        "What is the speed limit in built-up areas without signs?",
        "30 km/t","50 km/t","60 km/t","80 km/t",
        "30 กม./ชม.","50 กม./ชม.","60 กม./ชม.","80 กม./ชม.",
        "30 km/h","50 km/h","60 km/h","80 km/h",
        "B","I tettbygd strøk er fartsgrensen 50 km/t med mindre annet er skiltet.",
        "ในเขตชุมชนความเร็วสูงสุดคือ 50 กม./ชม. เว้นแต่จะมีป้ายบอกเป็นอย่างอื่น",
        "In built-up areas the speed limit is 50 km/h unless otherwise signed.",
        w("no","362_50")))

    qs.append(q("sl002","Speed Limits","easy",
        "Hva er fartsgrensen utenfor tettbygd strøk uten skilt?",
        "ความเร็วจำกัดนอกเขตชุมชนโดยไม่มีป้ายคืออะไร?",
        "What is the speed limit outside built-up areas without signs?",
        "60 km/t","70 km/t","80 km/t","100 km/t",
        "60 กม./ชม.","70 กม./ชม.","80 กม./ชม.","100 กม./ชม.",
        "60 km/h","70 km/h","80 km/h","100 km/h",
        "C","Utenfor tettbygd strøk er fartsgrensen 80 km/t med mindre annet er skiltet.",
        "นอกเขตชุมชนความเร็วสูงสุดคือ 80 กม./ชม. เว้นแต่จะมีป้ายบอกเป็นอย่างอื่น",
        "Outside built-up areas the speed limit is 80 km/h unless otherwise signed.",
        w("no","362_80")))

    qs.append(q("sl003","Speed Limits","easy",
        "Hva er fartsgrensen på motorvei i Norge?",
        "ความเร็วจำกัดบนทางด่วนในนอร์เวย์คืออะไร?",
        "What is the speed limit on motorways in Norway?",
        "90 km/t","100 km/t","110 km/t","120 km/t",
        "90 กม./ชม.","100 กม./ชม.","110 กม./ชม.","120 กม./ชม.",
        "90 km/h","100 km/h","110 km/h","120 km/h",
        "B","Fartsgrensen på motorvei i Norge er normalt 100 km/t.",
        "ความเร็วสูงสุดบนทางด่วนในนอร์เวย์โดยทั่วไปคือ 100 กม./ชม.",
        "The speed limit on Norwegian motorways is normally 100 km/h.",
        w("no","362_100")))

    qs.append(q("sl004","Speed Limits","easy",
        "Hva skjer med bremselengden når farten dobles?",
        "ระยะเบรกเปลี่ยนอย่างไรเมื่อความเร็วเพิ่มเป็นสองเท่า?",
        "What happens to braking distance when speed doubles?",
        "Den dobles","Den tredobles","Den firedobles","Den er uforandret",
        "เพิ่มเป็นสองเท่า","เพิ่มเป็นสามเท่า","เพิ่มเป็นสี่เท่า","ไม่เปลี่ยนแปลง",
        "It doubles","It triples","It quadruples","It stays the same",
        "C","Bremselengden øker med kvadratet av hastigheten. Dobbel fart = fire ganger bremselengde.",
        "ระยะเบรกเพิ่มขึ้นตามกำลังสองของความเร็ว ความเร็วสองเท่า = ระยะเบรกสี่เท่า",
        "Braking distance increases with the square of speed. Double speed = four times braking distance.",
        None))

    qs.append(q("sl005","Speed Limits","medium",
        "Hva er fartsgrensen i en skolesone?",
        "ความเร็วจำกัดในเขตโรงเรียนคืออะไร?",
        "What is the speed limit in a school zone?",
        "50 km/t","40 km/t","30 km/t","20 km/t",
        "50 กม./ชม.","40 กม./ชม.","30 กม./ชม.","20 กม./ชม.",
        "50 km/h","40 km/h","30 km/h","20 km/h",
        "C","I skolesoner er fartsgrensen normalt 30 km/t for å beskytte barn.",
        "ในเขตโรงเรียนความเร็วสูงสุดโดยทั่วไปคือ 30 กม./ชม. เพื่อปกป้องเด็ก",
        "In school zones the speed limit is normally 30 km/h to protect children.",
        w("no","362_30")))

    qs.append(q("sl006","Speed Limits","easy",
        "Hva er fartsgrensen skiltet med 70 km/t?",
        "ป้ายจำกัดความเร็ว 70 กม./ชม. หมายความว่าอะไร?",
        "What does a speed limit sign of 70 km/h mean?",
        "Anbefalt hastighet","Minimum hastighet","Maksimal tillatt hastighet","Gjennomsnittshastighet",
        "ความเร็วแนะนำ","ความเร็วขั้นต่ำ","ความเร็วสูงสุดที่อนุญาต","ความเร็วเฉลี่ย",
        "Recommended speed","Minimum speed","Maximum permitted speed","Average speed",
        "C","Fartsgrenseskilt angir maksimalt tillatt hastighet — du kan ikke kjøre fortere.",
        "ป้ายจำกัดความเร็วระบุความเร็วสูงสุดที่อนุญาต คุณไม่สามารถขับเร็วกว่านี้",
        "A speed limit sign shows the maximum permitted speed — you cannot drive faster.",
        w("no","362_70")))

    qs.append(q("sl007","Speed Limits","medium",
        "Når det er kø på motorvei, hva bør du gjøre med farten?",
        "เมื่อมีการจราจรติดขัดบนทางด่วน คุณควรทำอย่างไรกับความเร็ว?",
        "When there is traffic on a motorway, what should you do with your speed?",
        "Holde 100 km/t","Redusere farten og øke avstand","Øke farten for å passere","Bytte felt hyppig",
        "รักษาความเร็ว 100 กม./ชม.","ลดความเร็วและเพิ่มระยะห่าง","เร่งความเร็วเพื่อแซง","เปลี่ยนเลนบ่อยๆ",
        "Keep 100 km/h","Reduce speed and increase distance","Speed up to pass","Change lanes frequently",
        "B","I kø skal du redusere fart og holde god avstand for å unngå ulykker.",
        "ในการจราจรติดขัดคุณควรลดความเร็วและรักษาระยะห่างที่ดีเพื่อป้องกันอุบัติเหตุ",
        "In traffic jams you should reduce speed and keep a good distance to avoid accidents.",
        None))

    qs.append(q("sl008","Speed Limits","medium",
        "Hva er minimumsavstanden bak bilen foran på vei med 80 km/t?",
        "ระยะห่างขั้นต่ำด้านหลังรถคันหน้าบนถนน 80 กม./ชม. คืออะไร?",
        "What is the minimum following distance behind the car ahead at 80 km/h?",
        "10 meter","30 meter","50 meter","Minst 2 sekunder",
        "10 เมตร","30 เมตร","50 เมตร","อย่างน้อย 2 วินาที",
        "10 metres","30 metres","50 metres","At least 2 seconds",
        "D","Du skal ha minst 2 sekunders avstand til bilen foran. Ved 80 km/t er det ca. 45 meter.",
        "คุณต้องมีระยะห่างอย่างน้อย 2 วินาทีจากรถคันหน้า ที่ 80 กม./ชม. คือประมาณ 45 เมตร",
        "You should keep at least a 2-second gap to the car ahead. At 80 km/h that's about 45 metres.",
        None))

    qs.append(q("sl009","Speed Limits","easy",
        "Hva er fartsgrensen for tunge kjøretøy (over 3500 kg) utenfor tettbygd strøk?",
        "ความเร็วจำกัดสำหรับยานพาหนะหนัก (เกิน 3500 กก.) นอกเขตชุมชนคืออะไร?",
        "What is the speed limit for heavy vehicles (over 3500 kg) outside built-up areas?",
        "80 km/t","70 km/t","60 km/t","90 km/t",
        "80 กม./ชม.","70 กม./ชม.","60 กม./ชม.","90 กม./ชม.",
        "80 km/h","70 km/h","60 km/h","90 km/h",
        "A","Tunge kjøretøy over 3500 kg har fartsgrense 80 km/t utenfor tettbygd strøk.",
        "ยานพาหนะหนักเกิน 3500 กก. มีความเร็วสูงสุด 80 กม./ชม. นอกเขตชุมชน",
        "Heavy vehicles over 3500 kg have a speed limit of 80 km/h outside built-up areas.",
        None))

    qs.append(q("sl010","Speed Limits","medium",
        "Hva betyr en opphevingsskilt for fartsgrensen?",
        "ป้ายยกเลิกความเร็วจำกัดหมายความว่าอะไร?",
        "What does a speed limit cancellation sign mean?",
        "Ny fartsgrense starter","Gammel fartsgrense gjelder igjen","Generell fartsgrense gjelder igjen","Ingen grense",
        "ความเร็วใหม่เริ่มต้น","ความเร็วเดิมมีผลอีกครั้ง","ความเร็วทั่วไปมีผลอีกครั้ง","ไม่มีจำกัด",
        "New limit starts","Old limit applies again","General speed limit applies again","No limit",
        "C","Opphevingsskilt betyr at den generelle fartsgrensen (50 i tettbygd / 80 utenfor) gjelder igjen.",
        "ป้ายยกเลิกหมายความว่าความเร็วจำกัดทั่วไป (50 ในเขตชุมชน / 80 นอกเขต) มีผลอีกครั้ง",
        "Cancellation sign means the general speed limit (50 in built-up / 80 outside) applies again.",
        None))

    # ── ROAD RULES (60 questions) ────────────────────────────────────────────
    qs.append(q("rr001","Road Rules","easy",
        "Hva er påbudt å bruke i bil?",
        "อะไรบังคับต้องใช้ในรถยนต์?",
        "What is mandatory to use in a car?",
        "Hjelm","Bilbelte","Hansker","Solbriller",
        "หมวกกันน็อก","เข็มขัดนิรภัย","ถุงมือ","แว่นกันแดด",
        "Helmet","Seatbelt","Gloves","Sunglasses",
        "B","Bilbelte er påbudt for alle i bilen — fører og passasjerer.",
        "เข็มขัดนิรภัยเป็นข้อบังคับสำหรับทุกคนในรถ ทั้งผู้ขับและผู้โดยสาร",
        "Seatbelt is mandatory for everyone in the car — driver and passengers.",
        None))

    qs.append(q("rr002","Road Rules","easy",
        "Hva er aldersgrensen for å ha barn i forsetet uten barnesete?",
        "อายุขั้นต่ำสำหรับเด็กในเบาะหน้าโดยไม่มีที่นั่งเด็กคืออะไร?",
        "What is the minimum age for a child in the front seat without a child seat?",
        "10 år","12 år","15 år","Det er alltid forbudt",
        "10 ปี","12 ปี","15 ปี","ห้ามเสมอ",
        "10 years","12 years","15 years","Always forbidden",
        "C","Barn under 15 år må bruke godkjent barnesikring. I forsetet gjelder egne regler.",
        "เด็กอายุต่ำกว่า 15 ปีต้องใช้ที่นั่งนิรภัยที่ได้รับการรับรอง มีกฎเฉพาะสำหรับเบาะหน้า",
        "Children under 15 must use approved child restraints. Special rules apply for the front seat.",
        None))

    qs.append(q("rr003","Road Rules","easy",
        "Hva er promillegrensen for bil i Norge?",
        "ขีดจำกัดแอลกอฮอล์สำหรับรถยนต์ในนอร์เวย์คืออะไร?",
        "What is the drink-drive limit in Norway?",
        "0,5 promille","0,4 promille","0,2 promille","0,8 promille",
        "0.5 เปอร์มิล","0.4 เปอร์มิล","0.2 เปอร์มิล","0.8 เปอร์มิล",
        "0.5 per mille","0.4 per mille","0.2 per mille","0.8 per mille",
        "C","I Norge er promillegrensen 0,2 promille. Denne er lavere enn i mange land.",
        "ในนอร์เวย์ขีดจำกัดแอลกอฮอล์คือ 0.2 เปอร์มิล ต่ำกว่าหลายประเทศ",
        "In Norway the drink-drive limit is 0.2 per mille. This is lower than in many countries.",
        None))

    qs.append(q("rr004","Road Rules","medium",
        "Når er det påbudt å bruke lys på bil i Norge?",
        "เมื่อไหร่บังคับต้องเปิดไฟรถยนต์ในนอร์เวย์?",
        "When is it mandatory to use lights on a car in Norway?",
        "Bare om natten","Alltid under kjøring","Bare i tunnel","Bare ved dårlig sikt",
        "เฉพาะตอนกลางคืน","ตลอดเวลาขณะขับ","เฉพาะในอุโมงค์","เฉพาะเมื่อทัศนวิสัยไม่ดี",
        "Only at night","Always while driving","Only in tunnels","Only in poor visibility",
        "B","I Norge er det påbudt å bruke lys til enhver tid under kjøring.",
        "ในนอร์เวย์บังคับต้องเปิดไฟตลอดเวลาขณะขับรถ",
        "In Norway it is mandatory to use lights at all times while driving.",
        None))

    qs.append(q("rr005","Road Rules","easy",
        "Hva er forbudt å gjøre mens du kjører?",
        "อะไรที่ห้ามทำขณะขับรถ?",
        "What is forbidden to do while driving?",
        "Høre på radio","Snakke i håndholdt mobiltelefon","Drikke vann","Åpne vinduet",
        "ฟังวิทยุ","คุยโทรศัพท์มือถือแบบถือด้วยมือ","ดื่มน้ำ","เปิดหน้าต่าง",
        "Listen to radio","Talk on handheld mobile phone","Drink water","Open window",
        "B","Det er forbudt å bruke håndholdt mobiltelefon mens du kjører bil i Norge.",
        "ห้ามใช้โทรศัพท์มือถือแบบถือด้วยมือขณะขับรถในนอร์เวย์",
        "It is forbidden to use a handheld mobile phone while driving in Norway.",
        None))

    qs.append(q("rr006","Road Rules","medium",
        "Hva er regelen for forbikjøring til venstre?",
        "กฎสำหรับการแซงด้านซ้ายคืออะไร?",
        "What is the rule for overtaking on the left?",
        "Alltid tillatt på motorvei","Forbudt","Kun tillatt utenfor tettbygd strøk","Kun når siktlinje er fri",
        "อนุญาตเสมอบนทางด่วน","ห้าม","อนุญาตเฉพาะนอกเขตชุมชน","อนุญาตเมื่อมองเห็นชัดเจน",
        "Always allowed on motorway","Forbidden","Only allowed outside built-up areas","Only when sight line is clear",
        "A","På motorvei kjøres normalt i høyre felt. Venstre felt brukes til forbikjøring.",
        "บนทางด่วนโดยปกติขับในเลนขวา เลนซ้ายใช้สำหรับแซง",
        "On motorways you normally drive in the right lane. The left lane is for overtaking.",
        None))

    qs.append(q("rr007","Road Rules","easy",
        "Hva er minstealder for å ta førerkort klasse B i Norge?",
        "อายุขั้นต่ำในการสมัครใบอนุญาตขับขี่ชั้น B ในนอร์เวย์คืออะไร?",
        "What is the minimum age for a class B driving licence in Norway?",
        "16 år","17 år","18 år","21 år",
        "16 ปี","17 ปี","18 ปี","21 ปี",
        "16 years","17 years","18 years","21 years",
        "C","Du må ha fylt 18 år for å ta førerkort klasse B (personbil) i Norge.",
        "คุณต้องอายุครบ 18 ปีจึงจะสมัครใบอนุญาตขับขี่ชั้น B (รถยนต์ส่วนบุคคล) ในนอร์เวย์",
        "You must be 18 years old to get a class B driving licence (car) in Norway.",
        None))

    qs.append(q("rr008","Road Rules","medium",
        "Hva er regelen for bruk av horn?",
        "กฎการใช้แตรคืออะไร?",
        "What is the rule for using the horn?",
        "Fri bruk når du vil","Kun ved fare eller for å varsle","Bare utenfor tettbygd strøk","Forbudt alltid",
        "ใช้ได้อิสระเมื่อต้องการ","เฉพาะเมื่อมีอันตรายหรือเพื่อเตือน","เฉพาะนอกเขตชุมชน","ห้ามเสมอ",
        "Free use whenever you want","Only in danger or to warn","Only outside built-up areas","Always forbidden",
        "B","Horn skal bare brukes for å varsle om fare. Unødvendig bruk er forbudt i tettbygd strøk.",
        "แตรควรใช้เฉพาะเพื่อเตือนถึงอันตราย การใช้โดยไม่จำเป็นห้ามในเขตชุมชน",
        "The horn should only be used to warn of danger. Unnecessary use is forbidden in built-up areas.",
        None))

    qs.append(q("rr009","Road Rules","easy",
        "Hva betyr en stiplet midtlinje på vegen?",
        "เส้นกลางถนนแบบประเภทเส้นประหมายความว่าอะไร?",
        "What does a dashed centre line on the road mean?",
        "Forbikjøring forbudt","Forbikjøring tillatt om det er trygt","Stopp her","Kjør sakte",
        "ห้ามแซง","แซงได้ถ้าปลอดภัย","หยุดที่นี่","ขับช้าๆ",
        "No overtaking","Overtaking allowed if safe","Stop here","Drive slowly",
        "B","Stiplet linje betyr at forbikjøring er tillatt — men kun om det er sikkert.",
        "เส้นประหมายความว่าการแซงเป็นที่อนุญาต แต่เฉพาะเมื่อปลอดภัยเท่านั้น",
        "Dashed line means overtaking is allowed — but only when it is safe.",
        None))

    qs.append(q("rr010","Road Rules","medium",
        "Hva er en sperrelinje?",
        "เส้นคั่นช่องจราจรคืออะไร?",
        "What is a barrier line?",
        "En stiplet linje","En gul linje","En ubrutt hvit linje du ikke kan krysse","En bred linje",
        "เส้นประ","เส้นสีเหลือง","เส้นขาวต่อเนื่องที่ห้ามข้าม","เส้นกว้าง",
        "A dashed line","A yellow line","An unbroken white line you cannot cross","A broad line",
        "C","En sperrelinje er en sammenhengende hvit linje som det er forbudt å krysse.",
        "เส้นคั่นช่องจราจรคือเส้นขาวต่อเนื่องที่ห้ามข้าม",
        "A barrier line is an unbroken white line that is forbidden to cross.",
        None))

    # ── SAFETY (50 questions) ─────────────────────────────────────────────────
    qs.append(q("sf001","Safety","easy",
        "Hva er den vanligste årsaken til trafikkulykker?",
        "อะไรคือสาเหตุที่พบบ่อยที่สุดของอุบัติเหตุทางถนน?",
        "What is the most common cause of traffic accidents?",
        "Dårlig vær","Menneskelige feil","Bildefekter","Dårlig vei",
        "สภาพอากาศไม่ดี","ความผิดพลาดของมนุษย์","รถบกพร่อง","ถนนไม่ดี",
        "Bad weather","Human error","Vehicle defects","Bad road",
        "B","Menneskelig svikt — uoppmerksomhet, tretthet, fart og rus — er årsak til ca. 90% av ulykker.",
        "ความผิดพลาดของมนุษย์ เช่น ขาดสมาธิ ง่วงนอน ความเร็วสูง และสิ่งเสพติด เป็นสาเหตุของประมาณ 90% ของอุบัติเหตุ",
        "Human error — inattention, fatigue, speed and intoxication — causes about 90% of accidents.",
        None))

    qs.append(q("sf002","Safety","easy",
        "Hva bør du gjøre om du er trøtt under kjøring?",
        "คุณควรทำอะไรถ้าง่วงนอนขณะขับรถ?",
        "What should you do if you feel sleepy while driving?",
        "Åpne vinduet og fortsett","Ta en pause og sov litt","Drikke kaffe og kjøre videre","Kjøre fortere",
        "เปิดหน้าต่างและขับต่อ","หยุดพักและนอนหลับ","ดื่มกาแฟและขับต่อ","ขับเร็วขึ้น",
        "Open window and continue","Take a break and sleep","Drink coffee and continue","Drive faster",
        "B","Tretthet er farlig i trafikken. Du bør stoppe, ta en pause og hvile.",
        "ความง่วงนอนเป็นอันตรายในการจราจร คุณควรหยุด พักผ่อน และนอนหลับ",
        "Fatigue is dangerous in traffic. You should stop, take a break and rest.",
        None))

    qs.append(q("sf003","Safety","medium",
        "Hva er refleksvest?",
        "เสื้อกั๊กสะท้อนแสงคืออะไร?",
        "What is a reflective vest?",
        "Påbudt utstyr i bil i Norge","Anbefalt men ikke påbudt","Kun for motorsyklister","Kun for lastebilsjåfører",
        "อุปกรณ์บังคับในรถยนต์ในนอร์เวย์","แนะนำแต่ไม่บังคับ","เฉพาะผู้ขับมอเตอร์ไซค์","เฉพาะผู้ขับรถบรรทุก",
        "Mandatory equipment in cars in Norway","Recommended but not mandatory","Only for motorcyclists","Only for truck drivers",
        "A","Refleksvest er påbudt utstyr i personbiler i Norge — tas med i bilen.",
        "เสื้อกั๊กสะท้อนแสงเป็นอุปกรณ์บังคับในรถยนต์ส่วนบุคคลในนอร์เวย์",
        "A reflective vest is mandatory equipment in cars in Norway — must be kept in the car.",
        None))

    qs.append(q("sf004","Safety","easy",
        "Hva er stoppdistansen ved 50 km/t på tørr asfalt?",
        "ระยะหยุดรถที่ 50 กม./ชม. บนยางมะตอยแห้งคืออะไร?",
        "What is the stopping distance at 50 km/h on dry asphalt?",
        "Ca. 15 meter","Ca. 25 meter","Ca. 35 meter","Ca. 50 meter",
        "ประมาณ 15 เมตร","ประมาณ 25 เมตร","ประมาณ 35 เมตร","ประมาณ 50 เมตร",
        "About 15 metres","About 25 metres","About 35 metres","About 50 metres",
        "C","Ved 50 km/t er total stoppdistanse (reaksjonstid + bremselengde) ca. 35 meter på tørr vei.",
        "ที่ 50 กม./ชม. ระยะหยุดรวม (เวลาตอบสนอง + ระยะเบรก) ประมาณ 35 เมตรบนถนนแห้ง",
        "At 50 km/h total stopping distance (reaction time + braking) is about 35 metres on dry road.",
        None))

    qs.append(q("sf005","Safety","easy",
        "Hva bør du gjøre ved tett tåke?",
        "คุณควรทำอะไรเมื่อมีหมอกหนา?",
        "What should you do in dense fog?",
        "Bruke fjernlys","Bruke tåkelys og redusere fart","Kjøre på midten av veien","Kjøre raskt for å komme gjennom",
        "ใช้ไฟไกล","ใช้ไฟหมอกและลดความเร็ว","ขับกลางถนน","ขับเร็วเพื่อผ่านไป",
        "Use high beams","Use fog lights and reduce speed","Drive in the middle","Drive fast to get through",
        "B","I tett tåke skal du bruke tåkelys, redusere farten og holde god avstand.",
        "ในหมอกหนาให้ใช้ไฟหมอก ลดความเร็ว และรักษาระยะห่างที่ดี",
        "In dense fog use fog lights, reduce speed and keep a good distance.",
        None))

    # ── DRIVING CONDITIONS (50 questions) ───────────────────────────────────
    qs.append(q("dc001","Driving Conditions","medium",
        "Hva bør du gjøre når du kjører på glatt vei?",
        "คุณควรทำอะไรเมื่อขับบนถนนลื่น?",
        "What should you do when driving on a slippery road?",
        "Kjøre fortere for å komme raskt over","Redusere fart og unngå brå bevegelser","Bruke bare bakhjulsbrems","Ignorere det",
        "ขับเร็วขึ้นเพื่อผ่านไปเร็วๆ","ลดความเร็วและหลีกเลี่ยงการเคลื่อนไหวกระทันหัน","ใช้เบรกล้อหลังเท่านั้น","เพิกเฉย",
        "Drive faster to get through quickly","Reduce speed and avoid sudden movements","Use only rear brake","Ignore it",
        "B","På glatt vei skal du redusere farten og unngå brå ratt-, brems- og gasspådrag.",
        "บนถนนลื่นให้ลดความเร็วและหลีกเลี่ยงการบังคับเลี้ยว เบรก หรือเร่งเครื่องกระทันหัน",
        "On slippery roads reduce speed and avoid sudden steering, braking or acceleration.",
        None))

    qs.append(q("dc002","Driving Conditions","medium",
        "Hva betyr aquaplaning?",
        "อควาเพลนนิ่งหมายความว่าอะไร?",
        "What does aquaplaning mean?",
        "Kjøring i sterk vind","Dekkene mister kontakt med veien pga. vann","Brems på is","Skruing av hjulene",
        "การขับในลมแรง","ยางสูญเสียการสัมผัสกับถนนเพราะน้ำ","การเบรกบนน้ำแข็ง","การบิดล้อ",
        "Driving in strong wind","Tyres lose contact with road due to water","Braking on ice","Wheel spinning",
        "B","Aquaplaning skjer når dekkene driver opp på et vannlag og mister veigrep.",
        "อควาเพลนนิ่งเกิดขึ้นเมื่อยางลอยขึ้นบนชั้นน้ำและสูญเสียการยึดเกาะถนน",
        "Aquaplaning occurs when tyres ride up on a water layer and lose road grip.",
        None))

    qs.append(q("dc003","Driving Conditions","easy",
        "Hva bør du sjekke på bilen om vinteren?",
        "คุณควรตรวจสอบอะไรในรถยนต์ช่วงฤดูหนาว?",
        "What should you check on the car in winter?",
        "Bare oljen","Dekk, batteri, lys og viskere","Bare vindusvisker","Bare bremser",
        "น้ำมันเท่านั้น","ยาง แบตเตอรี่ ไฟ และที่ปัดน้ำฝน","ที่ปัดน้ำฝนเท่านั้น","เบรกเท่านั้น",
        "Only oil","Tyres, battery, lights and wipers","Only wipers","Only brakes",
        "B","Om vinteren bør du sjekke vinterdekk, batteri, lys, vindusvisker og bremsevæske.",
        "ในฤดูหนาวควรตรวจสอบยางฤดูหนาว แบตเตอรี่ ไฟ ที่ปัดน้ำฝน และน้ำมันเบรก",
        "In winter check winter tyres, battery, lights, wipers and brake fluid.",
        None))

    qs.append(q("dc004","Driving Conditions","medium",
        "Når er det påbudt å bruke vinterdekk i Norge?",
        "เมื่อไหร่บังคับต้องใช้ยางฤดูหนาวในนอร์เวย์?",
        "When is it mandatory to use winter tyres in Norway?",
        "Alltid fra oktober","Når det er is eller snø på veien","Bare i januar og februar","Bare i nord-Norge",
        "ตลอดตั้งแต่เดือนตุลาคม","เมื่อมีน้ำแข็งหรือหิมะบนถนน","เฉพาะในมกราคมและกุมภาพันธ์","เฉพาะในนอร์เวย์เหนือ",
        "Always from October","When there is ice or snow on the road","Only January and February","Only in northern Norway",
        "B","Vinterdekk er påbudt når det er vinterlige kjøreforhold med is eller snø.",
        "ยางฤดูหนาวบังคับเมื่อมีสภาพการขับขี่ฤดูหนาวที่มีน้ำแข็งหรือหิมะ",
        "Winter tyres are mandatory when there are winter driving conditions with ice or snow.",
        None))

    qs.append(q("dc005","Driving Conditions","easy",
        "Hva bør du gjøre i sterk regn?",
        "คุณควรทำอะไรเมื่อฝนตกหนัก?",
        "What should you do in heavy rain?",
        "Kjøre som normalt","Redusere fart og øke avstand","Øke farten","Slå av lysene",
        "ขับตามปกติ","ลดความเร็วและเพิ่มระยะห่าง","เพิ่มความเร็ว","ปิดไฟ",
        "Drive as normal","Reduce speed and increase distance","Increase speed","Turn off lights",
        "B","I sterk regn er sikten dårligere og veien mer glatt. Reduser farten og øk avstand.",
        "ในฝนหนักทัศนวิสัยลดลงและถนนลื่นขึ้น ลดความเร็วและเพิ่มระยะห่าง",
        "In heavy rain visibility is worse and road is more slippery. Reduce speed and increase distance.",
        None))

    # ── ROAD CONDITIONS (40 questions) ──────────────────────────────────────
    qs.append(q("rc001","Road Conditions","medium",
        "Hva er et svinglys?",
        "ไฟเลี้ยวคืออะไร?",
        "What is a turn signal?",
        "Et ekstra lys for tunnel","Lys som aktiveres ved sving for bedre sikt","Et lys i støtfanger","Baklykt",
        "ไฟเพิ่มเติมสำหรับอุโมงค์","ไฟที่ทำงานเมื่อเลี้ยวเพื่อเพิ่มการมองเห็น","ไฟในกันชน","ไฟท้าย",
        "Extra light for tunnel","Light activated when turning for better visibility","Bumper light","Tail light",
        "B","Svinglys aktiveres automatisk når du svinger og lyser opp siden av veien.",
        "ไฟเลี้ยวทำงานโดยอัตโนมัติเมื่อคุณเลี้ยวและส่องแสงไปด้านข้างของถนน",
        "Turn signal activates automatically when turning and lights up the side of the road.",
        None))

    qs.append(q("rc002","Road Conditions","easy",
        "Hva er meningen med gule streker langs veikanten?",
        "เส้นสีเหลืองตามขอบถนนหมายความว่าอะไร?",
        "What do yellow lines along the road edge mean?",
        "Parkering tillatt","Stopp forbudt","Parkering forbudt","Sykkelsti",
        "อนุญาตให้จอด","ห้ามหยุด","ห้ามจอด","เลนจักรยาน",
        "Parking allowed","No stopping","No parking","Cycle lane",
        "C","Gule kantlinjestriper betyr at parkering er forbudt langs dette vegstrekket.",
        "เส้นขอบสีเหลืองหมายถึงห้ามจอดรถตลอดช่วงถนนนี้",
        "Yellow edge line stripes mean parking is forbidden along this road section.",
        None))

    qs.append(q("rc003","Road Conditions","medium",
        "Hva er et veikryss regulert av lyssignal?",
        "ทางแยกที่ควบคุมด้วยสัญญาณไฟคืออะไร?",
        "What is a junction controlled by traffic lights?",
        "Et kryss med stoppskilt","Et kryss med trafikklys","Et kryss med rundkjøring","Et kryss uten regulering",
        "ทางแยกที่มีป้ายหยุด","ทางแยกที่มีสัญญาณไฟจราจร","ทางแยกที่มีวงเวียน","ทางแยกที่ไม่มีการควบคุม",
        "Junction with stop sign","Junction with traffic lights","Junction with roundabout","Uncontrolled junction",
        "B","Et lyskryss er et kryss regulert av trafikklys (rødt, gult, grønt).",
        "ทางแยกสัญญาณไฟคือทางแยกที่ควบคุมด้วยสัญญาณไฟจราจร (แดง เหลือง เขียว)",
        "A traffic light junction is a junction controlled by traffic signals (red, amber, green).",
        None))

    qs.append(q("rc004","Road Conditions","easy",
        "Hva betyr grønt lys i trafikklyset?",
        "ไฟเขียวในสัญญาณไฟจราจรหมายความว่าอะไร?",
        "What does a green light in traffic signals mean?",
        "Stopp","Klar til å kjøre om det er trygt","Kjøre sakte","Fare",
        "หยุด","พร้อมขับถ้าปลอดภัย","ขับช้าๆ","อันตราย",
        "Stop","Clear to go if safe","Drive slowly","Danger",
        "B","Grønt lys betyr at du kan kjøre, men du må fortsatt sjekke at det er trygt.",
        "ไฟเขียวหมายความว่าคุณสามารถขับได้ แต่ยังต้องตรวจสอบว่าปลอดภัย",
        "Green light means you may go, but you must still check it is safe.",
        None))

    qs.append(q("rc005","Road Conditions","easy",
        "Hva betyr gult blinkende lys i trafikklyset?",
        "ไฟเหลืองกระพริบในสัญญาณไฟจราจรหมายความว่าอะไร?",
        "What does a blinking amber light in traffic signals mean?",
        "Stopp alltid","Kjør med forsiktighet — krysset er uregulert","Kjør fort","Lyksignalet virker ikke",
        "หยุดเสมอ","ขับด้วยความระมัดระวัง ทางแยกไม่มีการควบคุม","ขับเร็ว","สัญญาณไฟขัดข้อง",
        "Always stop","Drive with caution — junction uncontrolled","Drive fast","Signal not working",
        "B","Blinkende gult lys betyr at krysset er uregulert — bruk vikepliktreglene og kjør forsiktig.",
        "ไฟเหลืองกระพริบหมายความว่าทางแยกไม่มีการควบคุม ใช้กฎการให้ทางและขับอย่างระมัดระวัง",
        "Blinking amber means the junction is uncontrolled — use yield rules and drive carefully.",
        None))

    # ── SITUATIONS (50 questions) ─────────────────────────────────────────────
    img_p79  = pdf_image_b64(78)
    img_p141 = pdf_image_b64(140)

    qs.append(q("sit001","Situations","medium",
        "Du kjører og en ball triller ut i veien foran deg. Hva gjør du?",
        "คุณกำลังขับรถและลูกบอลกลิ้งออกมาบนถนนหน้าคุณ คุณทำอะไร?",
        "You are driving and a ball rolls into the road ahead. What do you do?",
        "Kjøre rundt ballen","Bremse og vær beredt på at barn kan komme ut","Tute og kjøre videre","Ignorere det",
        "ขับอ้อมลูกบอล","เบรกและเตรียมพร้อมที่เด็กอาจวิ่งออกมา","บีบแตรและขับต่อ","เพิกเฉย",
        "Drive around the ball","Brake and be prepared for a child to run out","Hoot and drive on","Ignore it",
        "B","Bal i veibanen varsler om at barn kan komme ut plutselig. Bremse og forbered deg.",
        "ลูกบอลบนถนนเตือนว่าเด็กอาจวิ่งออกมากะทันหัน เบรกและเตรียมพร้อม",
        "A ball in the road warns that a child may run out suddenly. Brake and prepare.",
        None))

    qs.append(q("sit002","Situations","medium",
        "Du nærmer deg en fotgjenger som venter ved et fotgjengerfelt. Hva gjør du?",
        "คุณกำลังเข้าใกล้คนเดินถนนที่รออยู่ที่ทางม้าลาย คุณทำอะไร?",
        "You approach a pedestrian waiting at a zebra crossing. What do you do?",
        "Kjøre forbi raskt","Stoppe og la fotgjengeren krysse","Tute for å advare","Ignorere og fortsette",
        "ขับผ่านไปเร็วๆ","หยุดและให้คนเดินถนนข้าม","บีบแตรเพื่อเตือน","เพิกเฉยและขับต่อ",
        "Drive past quickly","Stop and let pedestrian cross","Hoot to warn","Ignore and continue",
        "B","Du plikter å stoppe for fotgjengere som venter ved fotgjengerfelt.",
        "คุณมีหน้าที่หยุดให้คนเดินถนนที่รออยู่ที่ทางม้าลาย",
        "You are obliged to stop for pedestrians waiting at pedestrian crossings.",
        None))

    qs.append(q("sit003","Situations","hard",
        "Du kjører og bremselyktene til bilen foran deg tennes. Hva gjør du?",
        "คุณกำลังขับและไฟเบรกของรถคันหน้าติด คุณทำอะไร?",
        "You are driving and the brake lights of the car ahead come on. What do you do?",
        "Øke farten for å passe gapet","Løfte foten fra gassen og være klar til å bremse","Bytte til venstre felt straks","Ignorere det",
        "เพิ่มความเร็วเพื่อรักษาช่องว่าง","ยกเท้าออกจากคันเร่งและเตรียมเบรก","เปลี่ยนเลนซ้ายทันที","เพิกเฉย",
        "Increase speed to close gap","Lift foot off accelerator and prepare to brake","Switch left immediately","Ignore it",
        "B","Bremselys foran deg betyr at bilen bremser. Løft foten og forbered deg på å bremse.",
        "ไฟเบรกด้านหน้าหมายความว่ารถกำลังเบรก ยกเท้าออกจากคันเร่งและเตรียมเบรก",
        "Brake lights ahead mean the car is braking. Lift your foot and prepare to brake.",
        None))

    qs.append(q("sit004","Situations","medium",
        "Du kjører i en tunnel og lyser slukner. Hva gjør du?",
        "คุณกำลังขับในอุโมงค์และไฟดับ คุณทำอะไร?",
        "You are driving in a tunnel and the lights go out. What do you do?",
        "Stoppe midt i tunnelen","Slå på egne lys og kjøre sakte mot nærmeste utgang","Kjøre fort ut","Rygge tilbake",
        "หยุดกลางอุโมงค์","เปิดไฟของตัวเองและขับช้าๆ ไปทางทางออกที่ใกล้ที่สุด","ขับเร็วออกไป","ถอยกลับ",
        "Stop in the middle","Turn on own lights and drive slowly to nearest exit","Drive fast out","Reverse back",
        "B","Slå på lys umiddelbart og kjør forsiktig mot nærmeste nødutgang eller tunnelutgang.",
        "เปิดไฟทันทีและขับอย่างระมัดระวังไปยังทางออกฉุกเฉินหรือทางออกอุโมงค์ที่ใกล้ที่สุด",
        "Turn on lights immediately and drive carefully toward the nearest emergency or tunnel exit.",
        None))

    qs.append(q("sit005","Situations","hard",
        "Du er involvert i en trafikkulykke. Hva er det første du skal gjøre?",
        "คุณเกี่ยวข้องกับอุบัติเหตุทางถนน อะไรคือสิ่งแรกที่คุณต้องทำ?",
        "You are involved in a traffic accident. What is the first thing you should do?",
        "Ringe forsikringsselskapet","Sikre ulykkesstedet og varsle nødetatene","Flytte alle bilene","Ta bilder og kjøre videre",
        "โทรหาบริษัทประกันภัย","รักษาความปลอดภัยที่เกิดเหตุและแจ้งหน่วยฉุกเฉิน","เคลื่อนย้ายรถทั้งหมด","ถ่ายรูปและขับต่อ",
        "Call the insurance","Secure the scene and call emergency services","Move all cars","Take photos and drive on",
        "B","Først: sikre stedet (varseltrekant), hjelp skadde, ring 112. Flytt biler om de er til fare.",
        "ก่อนอื่น รักษาความปลอดภัยที่เกิดเหตุ (สามเหลี่ยมเตือน) ช่วยผู้บาดเจ็บ โทร 112",
        "First: secure the scene (warning triangle), help injured, call 112. Move cars only if dangerous.",
        img_p141))

    qs.append(q("sit006","Situations","medium",
        "Hva er en blindsone?",
        "จุดบอดคืออะไร?",
        "What is a blind spot?",
        "Et område du ikke kan se i speilene","Et mørkt område i veibanen","En tunnel uten lys","En uregulert sving",
        "พื้นที่ที่คุณมองไม่เห็นในกระจก","พื้นที่มืดบนถนน","อุโมงค์ที่ไม่มีไฟ","โค้งที่ไม่มีการควบคุม",
        "Area you cannot see in mirrors","A dark area in the lane","A tunnel without lights","An uncontrolled curve",
        "A","Blindsonen er området rundt bilen som ikke dekkes av speilene. Sjekk alltid over skulderen.",
        "จุดบอดคือบริเวณรอบรถที่กระจกไม่ครอบคลุม ตรวจสอบข้ามไหล่เสมอ",
        "The blind spot is the area around the car not covered by mirrors. Always check over the shoulder.",
        None))

    # ── TRAFFIC RULES — extra (50 questions) ─────────────────────────────────
    qs.append(q("tr001","Traffic Rules","easy",
        "Hva betyr det å parkere?",
        "การจอดรถหมายความว่าอะไร?",
        "What does parking mean?",
        "Stoppe kortvarig for av/påstigning","La kjøretøyet stå uten å vente ved det","Stoppe i kryss","Stoppe for rødt lys",
        "หยุดชั่วคราวเพื่อรับ/ส่งผู้โดยสาร","ทิ้งยานพาหนะไว้โดยไม่มีคนดูแล","หยุดที่ทางแยก","หยุดไฟแดง",
        "Brief stop for boarding","Leave vehicle unattended","Stop at junction","Stop at red light",
        "B","Parkering er å la kjøretøyet stå uten fører. Stans er kortvarig stopp med fører til stede.",
        "การจอดรถคือการทิ้งยานพาหนะไว้โดยไม่มีผู้ขับ การหยุดชั่วคราวคือการหยุดสั้นๆ โดยมีผู้ขับอยู่",
        "Parking is leaving a vehicle unattended. Stopping is a brief halt with the driver present.",
        None))

    qs.append(q("tr002","Traffic Rules","easy",
        "Hva er regelen for parkering foran innkjøring til en eiendom?",
        "กฎการจอดรถหน้าทางเข้าทรัพย์สินคืออะไร?",
        "What is the rule for parking in front of a property entrance?",
        "Tillatt om du parkerer kort tid","Forbudt","Tillatt om du har parkeringsbevis","Tillatt om det er natt",
        "อนุญาตถ้าจอดสั้น","ห้าม","อนุญาตถ้ามีใบอนุญาตจอด","อนุญาตถ้าเป็นกลางคืน",
        "Allowed if parked briefly","Forbidden","Allowed with parking permit","Allowed at night",
        "B","Parkering foran innkjøring er alltid forbudt — det blokkerer tilgang for eieren.",
        "ห้ามจอดหน้าทางเข้าเสมอ เพราะจะขวางทางเข้าของเจ้าของ",
        "Parking in front of an entrance is always forbidden — it blocks access for the owner.",
        None))

    qs.append(q("tr003","Traffic Rules","medium",
        "Hva er maksimal avstand fra fortaukant du kan parkere?",
        "ระยะห่างสูงสุดจากขอบฟุตปาทที่คุณสามารถจอดได้คืออะไร?",
        "What is the maximum distance from the kerb you can park?",
        "30 cm","50 cm","1 meter","2 meter",
        "30 ซม.","50 ซม.","1 เมตร","2 เมตร",
        "30 cm","50 cm","1 metre","2 metres",
        "B","Bilen skal parkeres maks 50 cm fra fortaukanten for ikke å hindre trafikken.",
        "รถต้องจอดห่างจากขอบฟุตปาทสูงสุด 50 ซม. เพื่อไม่กีดขวางการจราจร",
        "The car must be parked max 50 cm from the kerb to not obstruct traffic.",
        None))

    qs.append(q("tr004","Traffic Rules","easy",
        "Hva er forbudt ved gangfelt?",
        "อะไรต้องห้ามที่ทางม้าลาย?",
        "What is forbidden at a pedestrian crossing?",
        "Gå over","Stoppe for å slippe fotgjengere","Parkere i nærheten","Bruke lys",
        "เดินข้าม","หยุดให้คนเดินถนน","จอดรถใกล้ๆ","เปิดไฟ",
        "Walking across","Stopping to let pedestrians cross","Parking nearby","Using lights",
        "C","Parkering er forbudt innen 5 meter fra gangfelt for å sikre sikt.",
        "ห้ามจอดรถภายใน 5 เมตรจากทางม้าลายเพื่อให้มองเห็นได้ชัด",
        "Parking is forbidden within 5 metres of a pedestrian crossing to ensure visibility.",
        None))

    qs.append(q("tr005","Traffic Rules","medium",
        "Hva er en envegskjøring?",
        "ถนนเดินรถทางเดียวคืออะไร?",
        "What is a one-way street?",
        "En vei der du bare kan kjøre i én retning","En smal vei","En prioritert vei","En motorvei",
        "ถนนที่ขับได้เพียงทิศทางเดียว","ถนนแคบ","ถนนสายหลัก","ทางด่วน",
        "A road where you can only drive in one direction","A narrow road","A priority road","A motorway",
        "A","Envegskjøring tillater bare trafikk i én retning. Skiltet er blått med hvit pil.",
        "ถนนเดินรถทางเดียวอนุญาตการจราจรเพียงทิศทางเดียว ป้ายเป็นสีน้ำเงินมีลูกศรขาว",
        "One-way streets allow traffic in one direction only. The sign is blue with a white arrow.",
        w("no","220")))

    return qs

async def main():
    print("Bygger spørsmålsliste...", flush=True)
    questions = build_questions()
    print(f"Totalt {len(questions)} spørsmål klare", flush=True)

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    existing = await db.questions.count_documents({})
    print(f"Eksisterende spørsmål i DB: {existing}", flush=True)

    inserted = 0
    skipped = 0
    for q_data in questions:
        existing_q = await db.questions.find_one({"id": q_data["id"]})
        if existing_q:
            skipped += 1
            continue
        await db.questions.insert_one(q_data)
        inserted += 1
        if inserted % 20 == 0:
            print(f"  Importert {inserted}...", flush=True)

    total = await db.questions.count_documents({})
    print(f"\nFerdig! Importert: {inserted}, Hoppet over: {skipped}", flush=True)
    print(f"Total spørsmål i DB nå: {total}", flush=True)
    client.close()

asyncio.run(main())
