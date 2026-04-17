"""Seed 30 new questions (v2 schema) - bulk batch."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid, os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

RAW = [
{"sporsmal":"Hva betyr rødt lys i trafikklys?","alternativA":"Kjør forsiktig","alternativB":"Stopp","alternativC":"Vent hvis nødvendig","alternativD":"Du har forkjørsrett","riktigSvar":"B","forklaring":"Rødt lys betyr full stopp.","kategori":"Road Rules","difficulty":"easy","th_q":"ไฟแดงในสัญญาณจราจรหมายถึงอะไร?","th_a":"ขับระวัง","th_b":"หยุด","th_c":"รอถ้าจำเป็น","th_d":"คุณมีสิทธิ์ไปก่อน","th_e":"ไฟแดงหมายถึงต้องหยุดรถ"},
{"sporsmal":"Hvem har vikeplikt i et kryss uten skilt? (høyreregel)","alternativA":"Den til høyre","alternativB":"Den til venstre","alternativC":"Den som kjører fortest","alternativD":"Ingen","riktigSvar":"A","forklaring":"Høyre-regelen gjelder.","kategori":"Right of Way","difficulty":"easy","th_q":"ใครต้องให้ทางที่สี่แยกไม่มีป้าย? (กฎขวา)","th_a":"คนจากขวา","th_b":"คนจากซ้าย","th_c":"คนที่ขับเร็วที่สุด","th_d":"ไม่มีใคร","th_e":"ใช้กฎให้ทางขวา"},
{"sporsmal":"Hva er maks fart i tettbygd strøk?","alternativA":"40","alternativB":"50","alternativC":"60","alternativD":"70","riktigSvar":"B","forklaring":"Standard er 50 km/t.","kategori":"Speed Limits","difficulty":"easy","th_q":"ความเร็วสูงสุดในเขตเมือง?","th_a":"40","th_b":"50","th_c":"60","th_d":"70","th_e":"มาตรฐานคือ 50 กม./ชม."},
{"sporsmal":"Hva betyr blått skilt?","alternativA":"Forbud","alternativB":"Påbud/info","alternativC":"Fare","alternativD":"Stopp","riktigSvar":"B","forklaring":"Blå = påbud eller info.","kategori":"Traffic Signs","difficulty":"easy","th_q":"ป้ายสีน้ำเงินหมายถึงอะไร?","th_a":"ห้าม","th_b":"บังคับ/ข้อมูล","th_c":"อันตราย","th_d":"หยุด","th_e":"สีน้ำเงิน = บังคับหรือข้อมูล"},
{"sporsmal":"Hva betyr trekantet skilt?","alternativA":"Påbud","alternativB":"Fare","alternativC":"Forbud","alternativD":"Info","riktigSvar":"B","forklaring":"Trekant = fareskilt.","kategori":"Traffic Signs","difficulty":"easy","th_q":"ป้ายสามเหลี่ยมหมายถึงอะไร?","th_a":"บังคับ","th_b":"อันตราย","th_c":"ห้าม","th_d":"ข้อมูล","th_e":"สามเหลี่ยม = ป้ายเตือนอันตราย"},
{"sporsmal":"Hva må du gjøre før forbikjøring? (speil)","alternativA":"Øke farten","alternativB":"Sjekke speil","alternativC":"Blinke etterpå","alternativD":"Bremse","riktigSvar":"B","forklaring":"Alltid sjekk speil/blindsone.","kategori":"Safety","difficulty":"easy","th_q":"ต้องทำอะไรก่อนแซง? (กระจก)","th_a":"เพิ่มความเร็ว","th_b":"เช็คกระจก","th_c":"เปิดไฟเลี้ยวทีหลัง","th_d":"เบรก","th_e":"ต้องเช็คกระจกและจุดบอดเสมอ"},
{"sporsmal":"Hva er reaksjonslengde?","alternativA":"Bremselengde","alternativB":"Før du reagerer","alternativC":"Total stopp","alternativD":"Fart","riktigSvar":"B","forklaring":"Strekning før brems.","kategori":"Safety","difficulty":"easy","th_q":"ระยะปฏิกิริยาคืออะไร?","th_a":"ระยะเบรก","th_b":"ก่อนที่จะตอบสนอง","th_c":"ระยะหยุดรวม","th_d":"ความเร็ว","th_e":"ระยะทางก่อนเบรก"},
{"sporsmal":"Hva betyr gult lys? (stopp)","alternativA":"Kjør","alternativB":"Stopp hvis mulig","alternativC":"Full gass","alternativD":"Ignorer","riktigSvar":"B","forklaring":"Du skal stoppe hvis du kan.","kategori":"Road Rules","difficulty":"easy","th_q":"ไฟเหลืองหมายถึงอะไร? (หยุด)","th_a":"ขับ","th_b":"หยุดถ้าทำได้","th_c":"เร่งเต็มที่","th_d":"ไม่สนใจ","th_e":"ต้องหยุดถ้าทำได้"},
{"sporsmal":"Når skal du bruke refleksvest?","alternativA":"Alltid","alternativB":"Ved nødstopp","alternativC":"Kun natt","alternativD":"Aldri","riktigSvar":"B","forklaring":"Ved nødstopp på vei.","kategori":"Safety","difficulty":"easy","th_q":"เมื่อไหร่ต้องใส่เสื้อสะท้อนแสง?","th_a":"เสมอ","th_b":"เมื่อจอดฉุกเฉิน","th_c":"เฉพาะกลางคืน","th_d":"ไม่เคย","th_e":"เมื่อจอดฉุกเฉินบนถนน"},
{"sporsmal":"Hva er maks hastighet med tilhenger uten godkjenning?","alternativA":"60","alternativB":"70","alternativC":"80","alternativD":"90","riktigSvar":"C","forklaring":"Maks 80 km/t.","kategori":"Speed Limits","difficulty":"easy","th_q":"ความเร็วสูงสุดเมื่อลากพ่วงไม่มีใบอนุญาต?","th_a":"60","th_b":"70","th_c":"80","th_d":"90","th_e":"สูงสุด 80 กม./ชม."},
{"sporsmal":"Hva betyr stiplet kantlinje? (smal)","alternativA":"Smal vei","alternativB":"Forbud","alternativC":"Motorvei","alternativD":"Parkering","riktigSvar":"A","forklaring":"Ofte smal vei.","kategori":"Road Rules","difficulty":"medium","th_q":"เส้นประข้างทางหมายถึง? (แคบ)","th_a":"ถนนแคบ","th_b":"ห้าม","th_c":"มอเตอร์เวย์","th_d":"ที่จอดรถ","th_e":"มักหมายถึงถนนแคบ"},
{"sporsmal":"Hvem må vente ved hindring? (ansvar)","alternativA":"Den raskeste","alternativB":"Den med hindring","alternativC":"Begge","alternativD":"Ingen","riktigSvar":"B","forklaring":"Din hindring = ditt ansvar.","kategori":"Right of Way","difficulty":"easy","th_q":"ใครต้องรอเมื่อมีสิ่งกีดขวาง? (รับผิดชอบ)","th_a":"คนที่เร็วที่สุด","th_b":"ฝั่งที่มีสิ่งกีดขวาง","th_c":"ทั้งสอง","th_d":"ไม่มีใคร","th_e":"ฝั่งที่มีสิ่งกีดขวาง = รับผิดชอบ"},
{"sporsmal":"Hva betyr gul bakgrunn på skilt?","alternativA":"Permanent","alternativB":"Midlertidig","alternativC":"Privat","alternativD":"Parkering","riktigSvar":"B","forklaring":"Gule skilt er midlertidige.","kategori":"Traffic Signs","difficulty":"easy","th_q":"พื้นหลังสีเหลืองบนป้ายหมายถึง?","th_a":"ถาวร","th_b":"ชั่วคราว","th_c":"ส่วนตัว","th_d":"ที่จอดรถ","th_e":"ป้ายสีเหลืองเป็นแบบชั่วคราว"},
{"sporsmal":"Hva skjer med bremselengde når fart dobles?","alternativA":"Dobles","alternativB":"Halveres","alternativC":"4x","alternativD":"Samme","riktigSvar":"C","forklaring":"Kvadratisk økning.","kategori":"Safety","difficulty":"medium","th_q":"ระยะเบรกเปลี่ยนอย่างไรเมื่อความเร็วเพิ่มเป็น 2 เท่า?","th_a":"เพิ่ม 2 เท่า","th_b":"ลดลงครึ่ง","th_c":"เพิ่ม 4 เท่า","th_d":"เท่าเดิม","th_e":"เพิ่มแบบยกกำลังสอง"},
{"sporsmal":"Når skal du slå av fjernlys?","alternativA":"Når du ser bil","alternativB":"Når lys treffer","alternativC":"Alltid","alternativD":"Aldri","riktigSvar":"B","forklaring":"Unngå blending.","kategori":"Safety","difficulty":"medium","th_q":"เมื่อไหร่ต้องปิดไฟสูง?","th_a":"เมื่อเห็นรถ","th_b":"เมื่อแสงส่องถึง","th_c":"เสมอ","th_d":"ไม่เคย","th_e":"เพื่อไม่ให้แสงจ้า"},
{"sporsmal":"Hva betyr forkjørsvei? (rett)","alternativA":"Du må stoppe","alternativB":"Du har rett","alternativC":"Parkering","alternativD":"Fare","riktigSvar":"B","forklaring":"Du har forkjørsrett.","kategori":"Right of Way","difficulty":"easy","th_q":"ถนนหลักหมายถึง? (สิทธิ์)","th_a":"ต้องหยุด","th_b":"คุณมีสิทธิ์ไปก่อน","th_c":"ที่จอดรถ","th_d":"อันตราย","th_e":"คุณมีสิทธิ์ไปก่อน"},
{"sporsmal":"Hva er riktig avstand bak bil?","alternativA":"1 sek","alternativB":"2 sek","alternativC":"3 sek","alternativD":"5 sek","riktigSvar":"C","forklaring":"3-sekundersregelen.","kategori":"Safety","difficulty":"easy","th_q":"ระยะห่างที่ถูกต้องจากรถคันหน้า?","th_a":"1 วินาที","th_b":"2 วินาที","th_c":"3 วินาที","th_d":"5 วินาที","th_e":"กฎ 3 วินาที"},
{"sporsmal":"Hva må du gjøre ved glatt føre? (avstand)","alternativA":"Øke fart","alternativB":"Mindre avstand","alternativC":"Øke avstand","alternativD":"Ignorere","riktigSvar":"C","forklaring":"Lengre bremselengde.","kategori":"Safety","difficulty":"easy","th_q":"ต้องทำอะไรเมื่อถนนลื่น? (ระยะห่าง)","th_a":"เพิ่มความเร็ว","th_b":"ลดระยะห่าง","th_c":"เพิ่มระยะห่าง","th_d":"ไม่สนใจ","th_e":"ระยะเบรกยาวขึ้น"},
{"sporsmal":"Hvem gjelder politiet vs lys?","alternativA":"Lys","alternativB":"Skilt","alternativC":"Politi","alternativD":"Bil","riktigSvar":"C","forklaring":"Politi > alt.","kategori":"Road Rules","difficulty":"easy","th_q":"ตำรวจหรือไฟจราจร ใครมีอำนาจ?","th_a":"ไฟ","th_b":"ป้าย","th_c":"ตำรวจ","th_d":"รถ","th_e":"ตำรวจ > ทุกอย่าง"},
{"sporsmal":"Hva betyr stopp-skilt? (full stopp)","alternativA":"Kjør","alternativB":"Full stopp","alternativC":"Vent","alternativD":"Ignorer","riktigSvar":"B","forklaring":"Du må stoppe helt.","kategori":"Traffic Signs","difficulty":"easy","th_q":"ป้ายหยุดหมายถึง? (หยุดสนิท)","th_a":"ขับ","th_b":"หยุดสนิท","th_c":"รอ","th_d":"ไม่สนใจ","th_e":"ต้องหยุดรถสนิท"},
{"sporsmal":"Hva er aktiv sikkerhet? (ABS)","alternativA":"Airbag","alternativB":"ABS/ESP","alternativC":"Belte","alternativD":"Karosseri","riktigSvar":"B","forklaring":"Unngår ulykker.","kategori":"Safety","difficulty":"medium","th_q":"ความปลอดภัยเชิงรุกคือ? (ABS)","th_a":"ถุงลม","th_b":"ABS/ESP","th_c":"เข็มขัด","th_d":"ตัวถัง","th_e":"ช่วยหลีกเลี่ยงอุบัติเหตุ"},
{"sporsmal":"Hva er passiv sikkerhet?","alternativA":"ABS","alternativB":"ESP","alternativC":"Airbag","alternativD":"Speil","riktigSvar":"C","forklaring":"Beskytter ved ulykke.","kategori":"Safety","difficulty":"medium","th_q":"ความปลอดภัยเชิงรับคือ?","th_a":"ABS","th_b":"ESP","th_c":"ถุงลม","th_d":"กระจก","th_e":"ปกป้องเมื่อเกิดอุบัติเหตุ"},
{"sporsmal":"Når må du hjelpe ved ulykke?","alternativA":"Aldri","alternativB":"Kun hvis skyldig","alternativC":"Hvis nødvendig","alternativD":"Kun politi","riktigSvar":"C","forklaring":"Hjelpeplikt.","kategori":"Safety","difficulty":"medium","th_q":"เมื่อไหร่ต้องช่วยเมื่อเกิดอุบัติเหตุ?","th_a":"ไม่เคย","th_b":"เฉพาะถ้าผิด","th_c":"ถ้าจำเป็น","th_d":"เฉพาะตำรวจ","th_e":"มีหน้าที่ช่วยเหลือ"},
{"sporsmal":"Hva betyr enveiskjørt?","alternativA":"Begge veier","alternativB":"En retning","alternativC":"Stopp","alternativD":"Parkering","riktigSvar":"B","forklaring":"Kun én retning.","kategori":"Traffic Signs","difficulty":"easy","th_q":"ทางเดินรถทางเดียวหมายถึง?","th_a":"ทั้งสองทาง","th_b":"ทิศทางเดียว","th_c":"หยุด","th_d":"ที่จอดรถ","th_e":"เฉพาะทิศทางเดียว"},
{"sporsmal":"Hva betyr parkering forbudt? (skilt)","alternativA":"Parkere","alternativB":"Stoppe kort","alternativC":"Ingen parkering","alternativD":"Fri parkering","riktigSvar":"C","forklaring":"Ikke lov å parkere.","kategori":"Traffic Signs","difficulty":"easy","th_q":"ห้ามจอดรถหมายถึง? (ป้าย)","th_a":"จอดได้","th_b":"จอดสั้น","th_c":"ห้ามจอด","th_d":"จอดฟรี","th_e":"ไม่อนุญาตให้จอด"},
{"sporsmal":"Hva betyr stans forbudt?","alternativA":"Parkere","alternativB":"Stoppe","alternativC":"Ingen stopp","alternativD":"Kort stopp","riktigSvar":"C","forklaring":"Ingen stopp tillatt.","kategori":"Traffic Signs","difficulty":"easy","th_q":"ห้ามหยุดรถหมายถึง?","th_a":"จอดได้","th_b":"หยุดได้","th_c":"ห้ามหยุด","th_d":"หยุดสั้น","th_e":"ไม่อนุญาตให้หยุด"},
{"sporsmal":"Hva er riktig ved buss i 50-sone?","alternativA":"Kjør","alternativB":"Gi plass","alternativC":"Horn","alternativD":"Ignorer","riktigSvar":"B","forklaring":"Du må slippe buss.","kategori":"Road Rules","difficulty":"medium","th_q":"ข้อใดถูกต้องเกี่ยวกับรถเมล์ในเขต 50?","th_a":"ขับ","th_b":"ให้ทาง","th_c":"บีบแตร","th_d":"ไม่สนใจ","th_e":"ต้องให้ทางรถเมล์"},
{"sporsmal":"Hva er koblingslast?","alternativA":"Bak last","alternativB":"Foran last","alternativC":"Trykk på kobling","alternativD":"Fart","riktigSvar":"C","forklaring":"Trykk på tilhengerfeste.","kategori":"Safety","difficulty":"medium","th_q":"น้ำหนักลงคอพ่วงคืออะไร?","th_a":"น้ำหนักด้านหลัง","th_b":"น้ำหนักด้านหน้า","th_c":"แรงกดบนหัวลาก","th_d":"ความเร็ว","th_e":"แรงกดบนจุดพ่วง"},
{"sporsmal":"Hva er riktig ved motorvei? (kun frem)","alternativA":"Snu","alternativB":"Rygge","alternativC":"Kun frem","alternativD":"Parkere","riktigSvar":"C","forklaring":"Ingen rygging/stans.","kategori":"Road Rules","difficulty":"easy","th_q":"ข้อใดถูกต้องบนมอเตอร์เวย์? (ขับตรง)","th_a":"กลับรถ","th_b":"ถอยหลัง","th_c":"ขับตรงเท่านั้น","th_d":"จอดรถ","th_e":"ห้ามถอยหลัง/หยุด"},
{"sporsmal":"Hva betyr grønt lys? (kjør)","alternativA":"Stopp","alternativB":"Kjør","alternativC":"Vent","alternativD":"Fare","riktigSvar":"B","forklaring":"Du kan kjøre.","kategori":"Road Rules","difficulty":"easy","th_q":"ไฟเขียวหมายถึง? (ขับ)","th_a":"หยุด","th_b":"ขับ","th_c":"รอ","th_d":"อันตราย","th_e":"ขับต่อได้"},
]

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    inserted = 0
    skipped = 0

    for q in RAW:
        doc = {
            "id": str(uuid.uuid4()),
            "question": {"no": q["sporsmal"], "th": q["th_q"], "en": q["sporsmal"]},
            "options": [
                {"id": "A", "text": {"no": q["alternativA"], "th": q["th_a"], "en": q["alternativA"]}},
                {"id": "B", "text": {"no": q["alternativB"], "th": q["th_b"], "en": q["alternativB"]}},
                {"id": "C", "text": {"no": q["alternativC"], "th": q["th_c"], "en": q["alternativC"]}},
                {"id": "D", "text": {"no": q["alternativD"], "th": q["th_d"], "en": q["alternativD"]}},
            ],
            "correctOptionId": q["riktigSvar"],
            "explanation": {"no": q["forklaring"], "th": q["th_e"], "en": q["forklaring"]},
            "bildeUrl": None,
            "category": q["kategori"],
            "difficulty": q["difficulty"],
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        existing = await db.questions.find_one({"question.no": q["sporsmal"]})
        if existing:
            skipped += 1
            continue
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Done! Inserted: {inserted}, Skipped: {skipped}")
    total = await db.questions.count_documents({})
    print(f"Total questions: {total}")
    client.close()

asyncio.run(seed())
