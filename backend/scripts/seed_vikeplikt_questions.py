"""
seed_vikeplikt_questions.py — 18 nye spørsmål om vikeplikt og høyreregelen.
Trygt å kjøre på nytt — hopper over eksisterende (by question_text_no).
Kjør: cd thai2drive/backend && python scripts/seed_vikeplikt_questions.py
"""

import asyncio, os, uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "")
if not MONGO_URL:
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGO_URL="):
                    MONGO_URL = line.split("=", 1)[1].strip('"').strip("'")
                    break
if not MONGO_URL:
    raise RuntimeError("MONGO_URL not found in environment or .env")

DB_NAME = "thai2drive"

QUESTIONS = [
    # ────────────────────────────────────────────────────────────────────────────
    # 1. Høyreregelen — grunnleggende
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du nærmer deg et ukontrollert kryss uten skilt. Bil A kommer fra din høyre side. Hvem har vikeplikt?",
        "question_text_th": "คุณกำลังขับเข้าสี่แยกที่ไม่มีสัญญาณหรือป้ายใดๆ รถ A มาจากทางขวาของคุณ ใครต้องให้ทาง?",
        "question_text_en": "You approach an uncontrolled intersection with no signs. Car A comes from your right. Who must yield?",
        "answer_a_no": "Du har vikeplikt for bil A",
        "answer_b_no": "Bil A har vikeplikt for deg",
        "answer_c_no": "Den som kjørte inn i krysset sist",
        "answer_d_no": "Den som kjører raskest",
        "answer_a_th": "คุณต้องให้ทางรถ A",
        "answer_b_th": "รถ A ต้องให้ทางคุณ",
        "answer_c_th": "คนที่เข้าสี่แยกทีหลัง",
        "answer_d_th": "คนที่ขับเร็วกว่า",
        "answer_a_en": "You must yield to car A",
        "answer_b_en": "Car A must yield to you",
        "answer_c_en": "The driver who entered the intersection last",
        "answer_d_en": "The driver going faster",
        "correct_answer": "A",
        "explanation_no": "Høyreregelen gjelder: ved ukontrollerte kryss har du alltid vikeplikt for trafikk fra høyre. Bil A er på din høyre side, så du må vente til A har passert.",
        "explanation_th": "กฎการให้ทางด้านขวา: ที่สี่แยกที่ไม่มีป้าย คุณต้องให้ทางรถที่มาจากทางขวาของคุณเสมอ รถ A อยู่ทางขวา ดังนั้นคุณต้องรอให้ A ผ่านไปก่อน",
        "explanation_en": "The right-of-way rule: at uncontrolled intersections you always yield to traffic from your right. Car A is on your right, so you must wait for A to pass.",
        "category": "Vikeplikt",
        "difficulty": "easy",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 2. Høyreregelen — unntak på prioritert vei
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du kjører på en prioritert vei (skilt 220). En bil på sidevei vil inn i krysset fra din høyre side. Hvem har vikeplikt?",
        "question_text_th": "คุณขับบนถนนหลัก (ป้าย 220) รถบนถนนรองจะเข้าสี่แยกจากทางขวาของคุณ ใครต้องให้ทาง?",
        "question_text_en": "You drive on a priority road (sign 220). A car on the side road wants to enter from your right. Who must yield?",
        "answer_a_no": "Du har alltid vikeplikt når bilen er fra høyre",
        "answer_b_no": "Bilen på sideveien har vikeplikt — prioritert vei overstyrer høyreregelen",
        "answer_c_no": "Ingen av dere — dere må forhandle om hvem som kjører",
        "answer_d_no": "Du har vikeplikt fordi du er den som svinger",
        "answer_a_th": "คุณต้องให้ทางเสมอเมื่อรถมาจากขวา",
        "answer_b_th": "รถบนถนนรองต้องให้ทาง — ถนนหลักมีสิทธิ์เหนือกว่ากฎขวา",
        "answer_c_th": "ไม่มีใครต้องให้ทาง — ต้องเจรจากันเอง",
        "answer_d_th": "คุณต้องให้ทางเพราะคุณกำลังเลี้ยว",
        "answer_a_en": "You always yield when the car comes from the right",
        "answer_b_en": "The car on the side road must yield — priority road overrides the right rule",
        "answer_c_en": "Neither — you must negotiate who goes",
        "answer_d_en": "You yield because you are turning",
        "correct_answer": "B",
        "explanation_no": "Prioritert vei-skilt (220) gir deg forkjørsrett overfor all trafikk fra kryssende veier. Høyreregelen gjelder kun der ingen slik prioritering finnes.",
        "explanation_th": "ป้ายถนนหลัก (220) ให้สิทธิ์คุณเหนือรถทุกคันจากถนนที่ตัดกัน กฎการให้ทางด้านขวาใช้เฉพาะเมื่อไม่มีการกำหนดสิทธิ์",
        "explanation_en": "The priority road sign (220) gives you right of way over all traffic from crossing roads. The right-hand rule only applies where no such priority exists.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 3. Vikepliktskilt (trekant)
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du ser et rødt, trekantet vikepliktskilt (202) rett foran et kryss. Hva betyr det?",
        "question_text_th": "คุณเห็นป้ายสามเหลี่ยมสีแดง (202) ก่อนถึงสี่แยก หมายความว่าอย่างไร?",
        "question_text_en": "You see a red triangular yield sign (202) just before an intersection. What does it mean?",
        "answer_a_no": "Du skal stanse helt opp og vente til veien er fri",
        "answer_b_no": "Du har forkjørsrett over all trafikk i krysset",
        "answer_c_no": "Du har vikeplikt for all trafikk i det kryssende kjøremønsteret",
        "answer_d_no": "Du skal redusere farten til 30 km/t",
        "answer_a_th": "คุณต้องหยุดสนิทและรอจนกว่าถนนจะโล่ง",
        "answer_b_th": "คุณมีสิทธิ์เหนือรถทุกคันในสี่แยก",
        "answer_c_th": "คุณต้องให้ทางรถทุกคันที่วิ่งตัดกัน",
        "answer_d_th": "คุณต้องลดความเร็วให้เหลือ 30 กม./ชม.",
        "answer_a_en": "You must come to a complete stop and wait until the road is clear",
        "answer_b_en": "You have right of way over all traffic in the intersection",
        "answer_c_en": "You must yield to all traffic in the crossing direction",
        "answer_d_en": "You must reduce speed to 30 km/h",
        "correct_answer": "C",
        "explanation_no": "Vikepliktskilt (202) betyr at du plikter å gi fri bane for all trafikk som krysser eller møter deg. Du trenger ikke stoppe helt dersom veien er fri, men du MÅ gi vikeplikt.",
        "explanation_th": "ป้ายให้ทาง (202) หมายความว่าคุณต้องเปิดทางให้รถที่ตัดหรือสวนทางคุณ คุณไม่จำเป็นต้องหยุดสนิทถ้าถนนโล่ง แต่คุณต้องให้ทาง",
        "explanation_en": "Yield sign (202) means you must give way to all crossing or approaching traffic. You don't need to stop completely if the road is clear, but you MUST yield.",
        "category": "Vikeplikt",
        "difficulty": "easy",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 4. Stopp-skilt
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du ser et rødt, åttekantet stopp-skilt (128). Hva er det viktigste kravet?",
        "question_text_th": "คุณเห็นป้ายหยุดแปดเหลี่ยมสีแดง (128) ข้อกำหนดที่สำคัญที่สุดคืออะไร?",
        "question_text_en": "You see a red octagonal stop sign (128). What is the most important requirement?",
        "answer_a_no": "Reduser farten til 15 km/t og fortsett forsiktig",
        "answer_b_no": "Stans fullstendig — selv om veien ser fri ut — og gi deretter vikeplikt",
        "answer_c_no": "Blinke og se i speilene, deretter kjøre videre",
        "answer_d_no": "Stanse kun om det er trafikk i krysset",
        "answer_a_th": "ลดความเร็วเหลือ 15 กม./ชม. และขับต่ออย่างระมัดระวัง",
        "answer_b_th": "หยุดสนิท — แม้ถนนจะดูโล่ง — แล้วจึงให้ทาง",
        "answer_c_th": "กะพริบไฟและดูกระจก แล้วขับต่อ",
        "answer_d_th": "หยุดเฉพาะเมื่อมีรถในสี่แยก",
        "answer_a_en": "Reduce speed to 15 km/h and proceed carefully",
        "answer_b_en": "Stop completely — even if the road looks clear — then yield",
        "answer_c_en": "Signal and check mirrors, then proceed",
        "answer_d_en": "Stop only if there is traffic in the intersection",
        "correct_answer": "B",
        "explanation_no": "Stopp-skilt krever ALLTID full stans — hjulene må stoppe helt. Deretter vurderer du om det er trygt å kjøre. Kjører du uten å stoppe, risikerer du gebyr og prikker.",
        "explanation_th": "ป้ายหยุดต้องการหยุดสนิทเสมอ — ล้อต้องหยุดสนิท จากนั้นจึงประเมินว่าปลอดภัยที่จะขับต่อ หากไม่หยุดสนิทอาจโดนปรับและใบขับขี่ถูกหัก",
        "explanation_en": "A stop sign ALWAYS requires a full stop — wheels must stop completely. Then assess if it's safe to proceed. Failing to stop fully risks a fine and licence points.",
        "category": "Vikeplikt",
        "difficulty": "easy",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 5. Avkjørsel fra privat vei / oppkjørsel
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du skal kjøre ut fra en privat oppkjørsel på en boliggate. Hvem har vikeplikt?",
        "question_text_th": "คุณกำลังจะออกจากทางเข้าบ้านส่วนตัวสู่ถนนในย่านที่อยู่อาศัย ใครต้องให้ทาง?",
        "question_text_en": "You are exiting a private driveway onto a residential street. Who must yield?",
        "answer_a_no": "Du har vikeplikt for all trafikk på gaten — inkludert fotgjengere og syklister",
        "answer_b_no": "Du har forkjørsrett fordi du er i bevegelse",
        "answer_c_no": "Du og gatetrafikken har lik prioritet",
        "answer_d_no": "Høyreregelen avgjør — bil fra høyre har vikeplikt for deg",
        "answer_a_th": "คุณต้องให้ทางการจราจรทั้งหมดบนถนน รวมถึงคนเดินเท้าและนักปั่นจักรยาน",
        "answer_b_th": "คุณมีสิทธิ์ก่อนเพราะคุณกำลังเคลื่อนที่",
        "answer_c_th": "คุณและรถบนถนนมีสิทธิ์เท่ากัน",
        "answer_d_th": "กฎขวาตัดสิน — รถจากขวาต้องให้ทางคุณ",
        "answer_a_en": "You must yield to all traffic on the street — including pedestrians and cyclists",
        "answer_b_en": "You have right of way because you are already moving",
        "answer_c_en": "You and street traffic have equal priority",
        "answer_d_en": "The right-hand rule applies — car from right yields to you",
        "correct_answer": "A",
        "explanation_no": "Den som kjører ut fra en avkjørsel, parkering eller privat vei har alltid vikeplikt. Høyreregelen gjelder kun mellom veier — ikke mellom vei og avkjørsel.",
        "explanation_th": "ผู้ที่ออกจากทางเข้าออก ที่จอดรถ หรือถนนส่วนตัวต้องให้ทางเสมอ กฎขวาใช้ระหว่างถนนเท่านั้น ไม่ใช่ระหว่างถนนกับทางเข้าออก",
        "explanation_en": "Anyone exiting a driveway, car park or private road always yields. The right-hand rule only applies between roads — not between a road and a driveway.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 6. Avkjørsel fra parkeringsplass
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du skal ut fra en parkeringsplass til en offentlig gate. En sykkel kommer langs fortauet. Hva gjør du?",
        "question_text_th": "คุณกำลังออกจากที่จอดรถสู่ถนนสาธารณะ มีจักรยานมาตามทางเท้า คุณจะทำอะไร?",
        "question_text_en": "You are exiting a car park onto a public road. A cyclist comes along the pavement. What do you do?",
        "answer_a_no": "Du kjører forsiktig fordi syklisten er på fortauet og ikke veien",
        "answer_b_no": "Du stopper og gir vikeplikt for syklisten",
        "answer_c_no": "Du har forkjørsrett — syklisten er ikke et motorkjøretøy",
        "answer_d_no": "Du blinker venstre og svinger uten å stoppe",
        "answer_a_th": "คุณขับอย่างระมัดระวังเพราะนักปั่นอยู่บนทางเท้า ไม่ใช่ถนน",
        "answer_b_th": "คุณหยุดและให้ทางนักปั่นจักรยาน",
        "answer_c_th": "คุณมีสิทธิ์ก่อน — นักปั่นไม่ใช่ยานยนต์",
        "answer_d_th": "คุณกะพริบไฟซ้ายและเลี้ยวโดยไม่หยุด",
        "answer_a_en": "You drive carefully because the cyclist is on the pavement, not the road",
        "answer_b_en": "You stop and yield to the cyclist",
        "answer_c_en": "You have right of way — the cyclist is not a motor vehicle",
        "answer_d_en": "You signal left and turn without stopping",
        "correct_answer": "B",
        "explanation_no": "Når du forlater en parkeringsplass, har du vikeplikt for ALL trafikk — inkludert fotgjengere og syklister på fortau. Syklistens plassering på fortauet endrer ikke din plikt.",
        "explanation_th": "เมื่อออกจากที่จอดรถ คุณต้องให้ทางการจราจรทุกประเภท รวมถึงคนเดินเท้าและนักปั่นบนทางเท้า ตำแหน่งของนักปั่นบนทางเท้าไม่เปลี่ยนหน้าที่ของคุณ",
        "explanation_en": "When leaving a car park, you must yield to ALL traffic — including pedestrians and cyclists on the pavement. The cyclist's position on the pavement does not change your duty.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 7. Rundkjøring
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du nærmer deg en rundkjøring med skilt 204 (påbudt kjøreretning). Hvem har vikeplikt?",
        "question_text_th": "คุณกำลังเข้าวงเวียนที่มีป้าย 204 (ทิศทางบังคับ) ใครต้องให้ทาง?",
        "question_text_en": "You approach a roundabout marked with sign 204 (mandatory direction). Who must yield?",
        "answer_a_no": "Trafikk inne i rundkjøringen har vikeplikt for deg som er ny",
        "answer_b_no": "Du som kjører inn har vikeplikt for trafikk som allerede er inne i rundkjøringen",
        "answer_c_no": "Den som kjører raskest har forkjørsrett",
        "answer_d_no": "Høyreregelen gjelder fullt ut i rundkjøringen",
        "answer_a_th": "รถในวงเวียนต้องให้ทางคุณที่เพิ่งเข้ามา",
        "answer_b_th": "คุณที่กำลังเข้าวงเวียนต้องให้ทางรถที่อยู่ในวงเวียนแล้ว",
        "answer_c_th": "คนขับเร็วกว่ามีสิทธิ์ก่อน",
        "answer_d_th": "กฎขวาใช้เต็มรูปแบบในวงเวียน",
        "answer_a_en": "Traffic inside the roundabout yields to you entering",
        "answer_b_en": "You entering must yield to traffic already inside the roundabout",
        "answer_c_en": "The fastest driver has right of way",
        "answer_d_en": "The right-hand rule fully applies in the roundabout",
        "correct_answer": "B",
        "explanation_no": "I norske rundkjøringer er det vikeplikt ved innkjøring. Trafikk som allerede er inne i sirkelen har alltid forkjørsrett. Skilt 204 og eventuelle vikepliktskilt bekrefter dette.",
        "explanation_th": "ในวงเวียนของนอร์เวย์ ผู้ที่เข้าวงเวียนต้องให้ทาง รถที่อยู่ในวงเวียนแล้วมีสิทธิ์ก่อนเสมอ ป้าย 204 และป้ายให้ทางยืนยันสิ่งนี้",
        "explanation_en": "In Norwegian roundabouts, entering traffic must yield. Traffic already in the circle always has right of way. Sign 204 and any yield signs confirm this.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 8. T-kryss uten skilt
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du kjører på veien som ender i et T-kryss (stikvei). Det er ingen skilt. Hvem har vikeplikt?",
        "question_text_th": "คุณขับบนถนนที่สิ้นสุดที่สี่แยกรูปตัว T (ถนนตัน) ไม่มีป้ายใด ใครต้องให้ทาง?",
        "question_text_en": "You drive on the road that ends at a T-junction (dead end). There are no signs. Who must yield?",
        "answer_a_no": "Du har vikeplikt — stikvei/veislutt gir vikeplikt for gjennomgangstrafikk",
        "answer_b_no": "Høyreregelen avgjør — du har vikeplikt kun for bil fra din høyre side",
        "answer_c_no": "Gjennomgangstrafikken har vikeplikt fordi T-veien er prioritert",
        "answer_d_no": "Ingen har vikeplikt — det er lov å kjøre uten å stoppe",
        "answer_a_th": "คุณต้องให้ทาง — ถนนตันต้องให้ทางรถสัญจรหลัก",
        "answer_b_th": "กฎขวาตัดสิน — คุณให้ทางเฉพาะรถจากทางขวา",
        "answer_c_th": "รถสัญจรหลักต้องให้ทางเพราะถนน T ได้รับสิทธิ์",
        "answer_d_th": "ไม่มีใครต้องให้ทาง — ขับผ่านได้เลย",
        "answer_a_en": "You must yield — a dead-end road yields to through traffic",
        "answer_b_en": "The right-hand rule decides — you only yield to cars from your right",
        "answer_c_en": "Through traffic yields because the T-road is prioritised",
        "answer_d_en": "Nobody has to yield — it is legal to drive through without stopping",
        "correct_answer": "A",
        "explanation_no": "Veien som ender (stikveien/den innmunne veien) anses som avkjørsel til den veien den møter. Du har dermed vikeplikt for ALT som kjører på tvers — ikke bare biler fra høyre.",
        "explanation_th": "ถนนที่สิ้นสุด (ถนนตัน) ถือเป็นทางเข้าออกสู่ถนนที่มันพบ คุณจึงต้องให้ทางรถทุกคันที่วิ่งตัดกัน ไม่ใช่แค่รถจากทางขวา",
        "explanation_en": "The dead-end road (stub road) is treated as a driveway entering the road it meets. You must therefore yield to ALL traffic crossing — not just cars from the right.",
        "category": "Vikeplikt",
        "difficulty": "hard",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 9. Svinging til venstre
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du skal svinge til venstre i et kryss. En bil kommer rett frem mot deg i samme kjørefelt. Hvem har vikeplikt?",
        "question_text_th": "คุณกำลังจะเลี้ยวซ้ายที่สี่แยก รถคันหนึ่งวิ่งตรงมาหาคุณในเลนเดียวกัน ใครต้องให้ทาง?",
        "question_text_en": "You are turning left at an intersection. A car is coming straight towards you in the same lane. Who must yield?",
        "answer_a_no": "Du har vikeplikt for bilen som kjører rett frem",
        "answer_b_no": "Bilen rett frem har vikeplikt fordi den er på din høyre side",
        "answer_c_no": "Den som er lengst unna krysset har vikeplikt",
        "answer_d_no": "Den som svinger har alltid forkjørsrett",
        "answer_a_th": "คุณต้องให้ทางรถที่วิ่งตรงมา",
        "answer_b_th": "รถที่วิ่งตรงต้องให้ทางเพราะอยู่ทางขวาของคุณ",
        "answer_c_th": "คนที่อยู่ไกลจากสี่แยกมากกว่าต้องให้ทาง",
        "answer_d_th": "คนที่เลี้ยวมีสิทธิ์ก่อนเสมอ",
        "answer_a_en": "You must yield to the car going straight ahead",
        "answer_b_en": "The car going straight must yield because it is on your right",
        "answer_c_en": "The driver furthest from the intersection must yield",
        "answer_d_en": "The turning driver always has right of way",
        "correct_answer": "A",
        "explanation_no": "Den som svinger til venstre over motgående trafikk, har alltid vikeplikt for kjøretøy som kommer rett frem. Dette er en grunnregel i vegtrafikkloven og er uavhengig av høyreregelen.",
        "explanation_th": "ผู้ที่เลี้ยวซ้ายข้ามรถสวนทางต้องให้ทางรถที่วิ่งตรงมาเสมอ นี่เป็นกฎพื้นฐานของกฎหมายจราจรนอร์เวย์และไม่ขึ้นกับกฎขวา",
        "explanation_en": "Anyone turning left across oncoming traffic always yields to vehicles going straight ahead. This is a fundamental rule in the Road Traffic Act and is independent of the right-hand rule.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 10. Utrykningskjøretøy
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du hører sirener og ser blålys fra en ambulanse bak deg. Hva plikter du å gjøre?",
        "question_text_th": "คุณได้ยินเสียงไซเรนและเห็นไฟสีน้ำเงินจากรถพยาบาลด้านหลัง คุณมีหน้าที่ต้องทำอะไร?",
        "question_text_en": "You hear a siren and see blue lights from an ambulance behind you. What are you required to do?",
        "answer_a_no": "Øke farten slik at ambulansen slipper forbi raskere",
        "answer_b_no": "Kjøre som normalt — utrykningskjøretøy finner alltid en åpning",
        "answer_c_no": "Gi fri bane umiddelbart — beveg deg mot høyre og stopp om nødvendig",
        "answer_d_no": "Blinke og kjøre til venstre slik at ambulansen kan bruke midten",
        "answer_a_th": "เร่งความเร็วเพื่อให้รถพยาบาลผ่านได้เร็วขึ้น",
        "answer_b_th": "ขับตามปกติ — รถฉุกเฉินจะหาทางผ่านได้เอง",
        "answer_c_th": "เปิดทางทันที — เคลื่อนไปทางขวาและหยุดถ้าจำเป็น",
        "answer_d_th": "กะพริบไฟและเคลื่อนไปทางซ้ายเพื่อให้รถพยาบาลใช้ตรงกลาง",
        "answer_a_en": "Speed up so the ambulance can pass faster",
        "answer_b_en": "Drive normally — emergency vehicles always find a gap",
        "answer_c_en": "Clear a path immediately — move right and stop if necessary",
        "answer_d_en": "Signal and move left so the ambulance can use the centre",
        "correct_answer": "C",
        "explanation_no": "Alle trafikanter har plikt til å gi fri bane for utrykningskjøretøy med lyd- og lyssignaler. Du skal bevege deg mot høyre og eventuelt stoppe — aldri mot venstre (mot oncoming trafikk).",
        "explanation_th": "ผู้ขับขี่ทุกคนมีหน้าที่เปิดทางให้รถฉุกเฉินที่มีสัญญาณเสียงและแสง คุณต้องเคลื่อนไปทางขวาและหยุดถ้าจำเป็น ไม่ควรเคลื่อนไปทางซ้าย (สวนทางการจราจร)",
        "explanation_en": "All road users must clear a path for emergency vehicles with sound and light signals. Move right and stop if necessary — never move left (into oncoming traffic).",
        "category": "Vikeplikt",
        "difficulty": "easy",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 11. Gangfelt (pedestrian crossing)
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "En fotgjenger venter ved et oppmalt gangfelt uten trafikklys. Hva er riktig?",
        "question_text_th": "คนเดินเท้ายืนรอที่ทางม้าลายที่ไม่มีสัญญาณไฟ อะไรถูกต้อง?",
        "question_text_en": "A pedestrian waits at a marked crosswalk with no traffic lights. What is correct?",
        "answer_a_no": "Du kan kjøre fordi fotgjengeren ennå ikke er ute i veien",
        "answer_b_no": "Du plikter å stanse og gi fotgjengeren mulighet til å krysse",
        "answer_c_no": "Fotgjengere har kun vikeplikt i gangfelt med trafikklys",
        "answer_d_no": "Du stanser bare hvis fotgjengeren vinker deg ned",
        "answer_a_th": "คุณขับต่อได้เพราะคนเดินเท้ายังไม่ออกมาในถนน",
        "answer_b_th": "คุณมีหน้าที่หยุดและให้โอกาสคนเดินเท้าข้ามถนน",
        "answer_c_th": "คนเดินเท้ามีสิทธิ์เฉพาะในทางม้าลายที่มีสัญญาณไฟ",
        "answer_d_th": "คุณหยุดเฉพาะเมื่อคนเดินเท้าโบกมือให้",
        "answer_a_en": "You can drive because the pedestrian is not yet in the road",
        "answer_b_en": "You must stop and give the pedestrian the opportunity to cross",
        "answer_c_en": "Pedestrians only have right of way at crossings with traffic lights",
        "answer_d_en": "You stop only if the pedestrian waves you down",
        "correct_answer": "B",
        "explanation_no": "I Norge har fotgjengere forkjørsrett i alle oppmalte gangfelt — også uten trafikklys. Du plikter å stanse for en fotgjenger som er i ferd med å krysse ELLER som tydelig venter på å krysse.",
        "explanation_th": "ในนอร์เวย์ คนเดินเท้ามีสิทธิ์ก่อนในทุกทางม้าลายที่ทาสี แม้ไม่มีสัญญาณไฟ คุณต้องหยุดสำหรับคนเดินเท้าที่กำลังข้ามหรือที่รอข้ามอยู่ชัดเจน",
        "explanation_en": "In Norway, pedestrians have right of way at all painted crosswalks — even without traffic lights. You must stop for a pedestrian who is crossing OR who is clearly waiting to cross.",
        "category": "Vikeplikt",
        "difficulty": "easy",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 12. Sykkel fra høyre — høyreregelen
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "I et ukontrollert kryss kommer en syklist fra din høyre side. Gjelder høyreregelen for syklister?",
        "question_text_th": "ที่สี่แยกที่ไม่มีป้าย มีนักปั่นจักรยานมาจากทางขวาของคุณ กฎขวาใช้กับนักปั่นด้วยหรือไม่?",
        "question_text_en": "At an uncontrolled intersection, a cyclist comes from your right. Does the right-hand rule apply to cyclists?",
        "answer_a_no": "Nei — høyreregelen gjelder kun for motorkjøretøy",
        "answer_b_no": "Ja — syklister er trafikanter og nyter samme rettigheter som biler",
        "answer_c_no": "Kun hvis syklisten er på sykkelvei",
        "answer_d_no": "Nei — syklister har alltid vikeplikt for biler",
        "answer_a_th": "ไม่ — กฎขวาใช้เฉพาะกับยานยนต์เท่านั้น",
        "answer_b_th": "ใช่ — นักปั่นเป็นผู้ใช้ถนนและมีสิทธิ์เท่ากับรถยนต์",
        "answer_c_th": "เฉพาะเมื่อนักปั่นอยู่บนเลนจักรยาน",
        "answer_d_th": "ไม่ — นักปั่นต้องให้ทางรถยนต์เสมอ",
        "answer_a_en": "No — the right-hand rule only applies to motor vehicles",
        "answer_b_en": "Yes — cyclists are road users and enjoy the same rights as cars",
        "answer_c_en": "Only if the cyclist is on a cycle path",
        "answer_d_en": "No — cyclists always yield to cars",
        "correct_answer": "B",
        "explanation_no": "Syklister er trafikanter på linje med bilister. Høyreregelen gjelder fullt ut — en syklist fra høyre har forkjørsrett over deg i ukontrollert kryss.",
        "explanation_th": "นักปั่นจักรยานเป็นผู้ใช้ถนนเช่นเดียวกับผู้ขับรถ กฎขวาใช้อย่างเต็มที่ — นักปั่นจากทางขวามีสิทธิ์เหนือคุณที่สี่แยกที่ไม่มีป้าย",
        "explanation_en": "Cyclists are road users on equal footing with car drivers. The right-hand rule fully applies — a cyclist from the right has priority over you at an uncontrolled intersection.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 13. Gult blinklys (lysregulert kryss uten fast signal)
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du nærmer deg et lyskryss, men lysene blinker bare gult. Hva gjelder?",
        "question_text_th": "คุณกำลังเข้าสี่แยกสัญญาณไฟ แต่ไฟกะพริบเหลืองเท่านั้น ข้อกำหนดใดบังคับ?",
        "question_text_en": "You approach a traffic-light intersection, but the lights only flash yellow. What rules apply?",
        "answer_a_no": "Kjør normalt — gult blink betyr at lyset snart bytter til rødt",
        "answer_b_no": "Stans og vent til lyset slutter å blinke",
        "answer_c_no": "Vanlige vikepliktregler gjelder — reduser farten og viker etter høyreregelen eller skilt",
        "answer_d_no": "Du har fritt frem — gult blink betyr ingen begrensning",
        "answer_a_th": "ขับตามปกติ — ไฟเหลืองกะพริบหมายถึงไฟกำลังจะเปลี่ยนเป็นแดง",
        "answer_b_th": "หยุดและรอจนกว่าไฟจะหยุดกะพริบ",
        "answer_c_th": "กฎการให้ทางปกติใช้บังคับ — ลดความเร็วและให้ทางตามกฎขวาหรือป้าย",
        "answer_d_th": "คุณผ่านได้เลย — ไฟเหลืองกะพริบหมายถึงไม่มีข้อจำกัด",
        "answer_a_en": "Drive normally — yellow flashing means the light is about to change to red",
        "answer_b_en": "Stop and wait until the light stops flashing",
        "answer_c_en": "Normal right-of-way rules apply — slow down and yield per the right-hand rule or signs",
        "answer_d_en": "You have a clear run — yellow flashing means no restriction",
        "correct_answer": "C",
        "explanation_no": "Gult blinklys er et varselsignal. Trafikklyset er ute av drift, og krysset reguleres av ordinære vikepliktregler (høyreregelen, skilt). Reduser alltid farten.",
        "explanation_th": "ไฟเหลืองกะพริบเป็นสัญญาณเตือน สัญญาณไฟไม่ทำงาน และสี่แยกอยู่ภายใต้กฎการให้ทางทั่วไป (กฎขวา ป้าย) ลดความเร็วเสมอ",
        "explanation_en": "Yellow flashing is a warning signal. The traffic light is out of operation, and the intersection is governed by ordinary right-of-way rules (right-hand rule, signs). Always slow down.",
        "category": "Vikeplikt",
        "difficulty": "hard",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 14. Forlater prioritert vei
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du kjører på en prioritert vei og skal svinge inn på en sidevei. Gjelder din forkjørsrett fortsatt?",
        "question_text_th": "คุณขับบนถนนหลักและกำลังจะเลี้ยวเข้าถนนรอง สิทธิ์ก่อนของคุณยังคงอยู่หรือไม่?",
        "question_text_en": "You drive on a priority road and turn off onto a side road. Does your right of way still apply?",
        "answer_a_no": "Ja — prioritert vei gjelder hele strekningen til neste skilt",
        "answer_b_no": "Nei — du forlater prioritert vei og må nå ta hensyn til høyreregelen og andre skilt",
        "answer_c_no": "Ja — du beholder forkjørsretten i 50 meter etter svinget",
        "answer_d_no": "Bare om det er skilt som sier du fortsatt er på prioritert vei",
        "answer_a_th": "ใช่ — ถนนหลักใช้ได้ตลอดเส้นทางจนถึงป้ายถัดไป",
        "answer_b_th": "ไม่ — คุณออกจากถนนหลักและต้องปฏิบัติตามกฎขวาและป้ายอื่น",
        "answer_c_th": "ใช่ — คุณยังมีสิทธิ์อยู่ 50 เมตรหลังเลี้ยว",
        "answer_d_th": "เฉพาะถ้ามีป้ายบอกว่าคุณยังอยู่บนถนนหลัก",
        "answer_a_en": "Yes — priority road applies the entire stretch to the next sign",
        "answer_b_en": "No — you leave the priority road and must now follow the right-hand rule and other signs",
        "answer_c_en": "Yes — you retain right of way for 50 metres after the turn",
        "answer_d_en": "Only if there is a sign saying you are still on the priority road",
        "correct_answer": "B",
        "explanation_no": "Forkjørsretten på prioritert vei gjelder kun mens du er på selve den prioriterte veien. Svinger du av til en sidevei, er du nå på en ny vei med egne regler — høyreregelen og eventuelle skilt gjelder.",
        "explanation_th": "สิทธิ์ก่อนบนถนนหลักใช้เฉพาะเมื่อคุณอยู่บนถนนหลักนั้น เมื่อคุณเลี้ยวเข้าถนนรอง คุณอยู่บนถนนใหม่ที่มีกฎของตัวเอง กฎขวาและป้ายที่เกี่ยวข้องใช้บังคับ",
        "explanation_en": "Right of way on a priority road applies only while you are on that road. When you turn off onto a side road, you are on a new road with its own rules — the right-hand rule and any signs apply.",
        "category": "Vikeplikt",
        "difficulty": "hard",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 15. Filskifte og vikeplikt
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du skal skifte fil til venstre på en flerfeltsvei. Hvem har vikeplikt?",
        "question_text_th": "คุณต้องการเปลี่ยนเลนไปทางซ้ายบนถนนหลายเลน ใครต้องให้ทาง?",
        "question_text_en": "You want to change lanes to the left on a multi-lane road. Who must yield?",
        "answer_a_no": "Du — den som skifter fil har alltid vikeplikt for trafikk i den nye filen",
        "answer_b_no": "Trafikk i venstre fil har vikeplikt fordi du har vært i veien lenger",
        "answer_c_no": "Høyreregelen avgjør — bil fra din høyre har vikeplikt",
        "answer_d_no": "Den som blinker har automatisk forkjørsrett",
        "answer_a_th": "คุณ — ผู้ที่เปลี่ยนเลนต้องให้ทางรถในเลนใหม่เสมอ",
        "answer_b_th": "รถในเลนซ้ายต้องให้ทางเพราะคุณอยู่บนถนนนานกว่า",
        "answer_c_th": "กฎขวาตัดสิน — รถจากทางขวาต้องให้ทาง",
        "answer_d_th": "คนที่กะพริบไฟมีสิทธิ์ก่อนโดยอัตโนมัติ",
        "answer_a_en": "You — the lane-changer always yields to traffic in the target lane",
        "answer_b_en": "Traffic in the left lane yields because you have been on the road longer",
        "answer_c_en": "The right-hand rule decides — car from your right yields",
        "answer_d_en": "The driver who signals automatically gets right of way",
        "correct_answer": "A",
        "explanation_no": "Den som skifter fil har alltid vikeplikt for trafikk som allerede befinner seg i den filen du vil over til. Blinking gir ikke forkjørsrett — det er kun et varsel til andre.",
        "explanation_th": "ผู้ที่เปลี่ยนเลนต้องให้ทางรถที่อยู่ในเลนที่คุณต้องการเข้าไปเสมอ การกะพริบไฟไม่ให้สิทธิ์ก่อน เป็นแค่การแจ้งเตือนผู้อื่น",
        "explanation_en": "The lane-changer always yields to traffic already in the target lane. Signalling does not grant right of way — it is only a warning to others.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 16. Uoversiktlig kryss — nedsatt fart
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "Du nærmer deg et uoversiktlig kryss der sikten er dårlig. Hva er riktig kjøreadferd?",
        "question_text_th": "คุณกำลังเข้าใกล้สี่แยกที่มองเห็นได้ไม่ดี ท่าทีการขับรถที่ถูกต้องคืออะไร?",
        "question_text_en": "You approach an intersection with poor visibility. What is the correct driving behaviour?",
        "answer_a_no": "Kjør raskt gjennom — jo raskere du passerer, desto kortere tid i risikosone",
        "answer_b_no": "Reduser farten til du har oversikt og er klar til å stanse om nødvendig",
        "answer_c_no": "Blinke og kjøre inn i midten av krysset for å se bedre",
        "answer_d_no": "Ingen spesiell tilpasning — bare hold normalt aktsomt",
        "answer_a_th": "ขับผ่านอย่างรวดเร็ว — ยิ่งผ่านเร็วยิ่งใช้เวลาในจุดเสี่ยงน้อย",
        "answer_b_th": "ลดความเร็วจนคุณมองเห็นชัดและพร้อมหยุดถ้าจำเป็น",
        "answer_c_th": "กะพริบไฟและขับเข้ากลางสี่แยกเพื่อมองได้ดีขึ้น",
        "answer_d_th": "ไม่ต้องปรับอะไรเป็นพิเศษ แค่ระวังตามปกติ",
        "answer_a_en": "Drive quickly through — the faster you pass, the less time in the risk zone",
        "answer_b_en": "Reduce speed until you have a clear view and are ready to stop if necessary",
        "answer_c_en": "Signal and drive into the centre of the intersection to see better",
        "answer_d_en": "No special adjustment — just maintain normal caution",
        "correct_answer": "B",
        "explanation_no": "Ved uoversiktlige kryss skal du alltid tilpasse farten slik at du rekker å stoppe for noe som dukker opp. Grunnregelen i vegtrafikkloven krever at du alltid kan stoppe på den oversiktlige strekningen foran deg.",
        "explanation_th": "ที่สี่แยกที่มองเห็นได้ไม่ดี คุณต้องปรับความเร็วเสมอเพื่อให้สามารถหยุดได้เมื่อมีสิ่งที่ปรากฏขึ้น กฎพื้นฐานกฎหมายจราจรกำหนดให้คุณต้องสามารถหยุดได้ภายในระยะที่มองเห็นข้างหน้า",
        "explanation_en": "At unobstructed intersections, always adjust speed so you can stop for anything that appears. The basic rule in the Road Traffic Act requires you to always be able to stop within the visible stretch ahead.",
        "category": "Vikeplikt",
        "difficulty": "medium",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 17. Tre biler i kryss — hvem kjører?
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "I et ukontrollert kryss møtes tre biler: A (nord), B (øst), C (sør). Alle vil rett frem mot vest. Hvem kjører først?",
        "question_text_th": "ในสี่แยกที่ไม่มีป้าย รถ 3 คันมาพบกัน: A (เหนือ) B (ตะวันออก) C (ใต้) ทุกคันต้องการตรงไปทางตะวันตก ใครขับก่อน?",
        "question_text_en": "At an uncontrolled intersection, three cars meet: A (north), B (east), C (south). All want to go straight west. Who goes first?",
        "answer_a_no": "A kjører først — den nordligste bilen har prioritet",
        "answer_b_no": "B kjører først — B er den eneste som ikke har noen til høyre for seg",
        "answer_c_no": "C kjører først — sørfra er alltid prioritert",
        "answer_d_no": "Alle har vikeplikt for hverandre — ingen kan kjøre",
        "answer_a_th": "A ขับก่อน — รถทางเหนือมีสิทธิ์ก่อน",
        "answer_b_th": "B ขับก่อน — B เป็นเพียงคนเดียวที่ไม่มีรถทางขวา",
        "answer_c_th": "C ขับก่อน — ทิศใต้มีสิทธิ์ก่อนเสมอ",
        "answer_d_th": "ทุกคนต้องให้ทางกันและกัน — ไม่มีใครขับได้",
        "answer_a_en": "A goes first — the northernmost car has priority",
        "answer_b_en": "B goes first — B is the only one with nobody to its right",
        "answer_c_en": "C goes first — south is always prioritised",
        "answer_d_en": "All must yield to each other — nobody can go",
        "correct_answer": "B",
        "explanation_no": "A har C på sin høyre side. C har B på sin høyre side. B har ingen på sin høyre side (A er til venstre for B). Derfor er B den eneste uten vikeplikt — B kjører, deretter C, så A.",
        "explanation_th": "A มี C ทางขวา C มี B ทางขวา B ไม่มีใครทางขวา (A อยู่ทางซ้ายของ B) ดังนั้น B เป็นผู้เดียวที่ไม่ต้องให้ทาง B ขับก่อน จากนั้น C แล้วจึง A",
        "explanation_en": "A has C on its right. C has B on its right. B has nobody on its right (A is to B's left). Therefore B is the only one without a yield obligation — B goes, then C, then A.",
        "category": "Vikeplikt",
        "difficulty": "hard",
    },
    # ────────────────────────────────────────────────────────────────────────────
    # 18. Sykling i gangfelt — hvem vikeplikt?
    # ────────────────────────────────────────────────────────────────────────────
    {
        "question_text_no": "En syklist sykler gjennom et gangfelt (ikke sykkelfelt). Har du vikeplikt for syklisten?",
        "question_text_th": "นักปั่นจักรยานขี่จักรยานผ่านทางม้าลาย (ไม่ใช่เลนจักรยาน) คุณต้องให้ทางนักปั่นหรือไม่?",
        "question_text_en": "A cyclist rides through a pedestrian crosswalk (not a bike lane). Must you yield to the cyclist?",
        "answer_a_no": "Ja — alle i gangfeltet har automatisk forkjørsrett",
        "answer_b_no": "Nei — gangfelts-forkjørsrett gjelder kun fotgjengere, ikke syklister",
        "answer_c_no": "Ja, men bare om syklisten triller sykkelen (ikke sykler)",
        "answer_d_no": "Det avhenger av hvor fort syklisten kjører",
        "answer_a_th": "ใช่ — ทุกคนในทางม้าลายมีสิทธิ์ก่อนโดยอัตโนมัติ",
        "answer_b_th": "ไม่ — สิทธิ์ในทางม้าลายใช้กับคนเดินเท้าเท่านั้น ไม่ใช่นักปั่น",
        "answer_c_th": "ใช่ แต่เฉพาะเมื่อนักปั่นเข็นจักรยาน (ไม่ได้ขี่)",
        "answer_d_th": "ขึ้นอยู่กับความเร็วของนักปั่น",
        "answer_a_en": "Yes — everyone in the crosswalk automatically has right of way",
        "answer_b_en": "No — crosswalk priority only applies to pedestrians, not cyclists",
        "answer_c_en": "Yes, but only if the cyclist walks the bike (not riding)",
        "answer_d_en": "It depends on how fast the cyclist is going",
        "correct_answer": "B",
        "explanation_no": "Gangfeltets forkjørsrett gjelder kun fotgjengere. En syklist som sykler gjennom et gangfelt er ikke beskyttet av gangfeltregelen. Syklisten bør egentlig stige av og trille — da er hen fotgjenger og har forkjørsrett.",
        "explanation_th": "สิทธิ์ในทางม้าลายใช้เฉพาะกับคนเดินเท้า นักปั่นที่ขี่จักรยานผ่านทางม้าลายไม่ได้รับการคุ้มครองจากกฎทางม้าลาย นักปั่นควรลงจากจักรยานและเข็น แล้วจะถือเป็นคนเดินเท้าและมีสิทธิ์ก่อน",
        "explanation_en": "Crosswalk priority applies only to pedestrians. A cyclist riding through a crosswalk is not protected by the crosswalk rule. The cyclist should dismount and walk — then they are a pedestrian and have right of way.",
        "category": "Vikeplikt",
        "difficulty": "hard",
    },
]


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = skipped = 0
    for q in QUESTIONS:
        existing = await db.questions.find_one({"question_text_no": q["question_text_no"]})
        if existing:
            print(f"  SKIP: {q['question_text_no'][:60]}")
            skipped += 1
            continue
        doc = {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(), **q}
        await db.questions.insert_one(doc)
        print(f"  INSERT [{q['difficulty'].upper()}]: {q['question_text_no'][:60]}")
        inserted += 1
    print(f"\nDone — {inserted} inserted, {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
