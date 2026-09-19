"""
Thailand vs Norge — Mikroleksjoner (Kjørekultur-pedagogikk)
------------------------------------------------------------
Pedagogisk sammenligning av trafikkultur i Thailand og Norge
for å bygge intuitive ryggmarksreflekser for thailandske elever.

Modulen gir:
- Strukturerte kultursammenlignende leksjoner med full språkisolasjon (NO, TH, EN).
- RAG/prompt-støtte for Michael Chat slik at han kan forklare forskjeller pedagogisk.
- API-endepunkter for web- og mobilvisning.
"""
from typing import Any, Dict, List, Optional
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(tags=["micro_lessons"])

CULTURE_LESSONS: List[Dict[str, Any]] = [
    {
        "id": "lesson_1_priority",
        "topic": "vikeplikt_hoyreregel",
        "law_ref": "Trafikkreglene § 7 / Vegtrafikkloven § 3",
        "keywords": [
            "høyreregel", "høyreregelen", "størst bil", "største bil", "forkjørsrett",
            "vikeplikt", "høyre", "right of way", "right hand rule", "biggest car",
            "รถใหญ่", "กฎให้ทาง", "ทางขวา", "รถใหญ่ไปก่อน", "ใครไปก่อน"
        ],
        "title_no": "Hvem bestemmer? Høyreregelen vs. Størst bil først",
        "title_th": "ใครมีสิทธิ์ไปก่อน? กฎให้ทางขวา vs. รถใหญ่ไปก่อน",
        "title_en": "Who has Priority? Right-hand Rule vs. Biggest Vehicle First",
        "norway_rule_no": "I Norge gjelder høyreregelen (§ 7) absolutt for alle kryss uten skilt. Du MÅ vike for trafikk fra høyre uansett om du kjører buss, lastebil eller moped.",
        "norway_rule_th": "ในนอร์เวย์ กฎการให้ทางด้านขวา (§ 7) มีผลบังคับใช้อย่างเด็ดขาดในทุกทางแยกที่ไม่มีป้าย คุณต้องหยุดให้ทางแก่รถที่มาจากทางขวาเสมอ ไม่ว่าคุณจะขับรถบรรทุก รถเก๋ง หรือมอเตอร์ไซค์",
        "norway_rule_en": "In Norway, the right-hand rule (Section 7) applies strictly in all unmarked intersections. You MUST yield to traffic from the right, regardless of vehicle size.",
        "thailand_habit_no": "I Thailand er det vanlig uformell skikk at den største bilen kjører først, eller at førere fletter seg inn der det er ledig luke.",
        "thailand_habit_th": "ในประเทศไทย มีความเคยชินอย่างไม่เป็นทางการว่า 'รถคันใหญ่กว่ามักได้ไปก่อน' หรือการเบียดแทรกตัวเข้าไปตามช่องว่าง",
        "thailand_habit_en": "In Thailand, informal custom often lets the larger vehicle proceed first, or drivers merge wherever there is a gap.",
        "content_no": (
            "I Thailand er det ofte en uformell praksis at store kjøretøy tar seg til rette, "
            "og trafikken flyter ved at man smetter inn der det er plass. I Norge er jussen krystallklar og absolutt: "
            "Høyreregelen (Trafikkreglene § 7) betyr at du MÅ vike for alle kjøretøy fra høyre, "
            "med mindre skilt eller lyssignal bestemmer noe annet. Det spiller ingen rolle om du kjører lastebil og den "
            "andre kjører en liten personbil — du må alltid stoppe og gi fri vei!"
        ),
        "content_th": (
            "ในประเทศไทย เรามักจะเห็นวิธีปฏิบัติอย่างไม่เป็นทางการคือ 'รถใหญ่กว่ามักจะได้ไปก่อน' "
            "หรือผู้ขับขี่จะแทรกตัวเข้าไปเมื่อเห็นช่องว่าง แต่ในประเทศนอร์เวย์ กฎหมายมีผลบังคับใช้อย่างเด็ดขาดครับ! "
            "กฎการให้ทางด้านขวา (Trafikkreglene § 7) กำหนดว่าคุณต้องให้ทางแก่รถทุกคันที่มาจากทางขวามือของคุณเสมอ "
            "หากไม่มีป้ายหรือไฟสัญญาณกำหนดไว้เป็นอย่างอื่น ไม่สำคัญเลยว่าคุณจะขับรถบรรทุกคันใหญ่หรือรถเล็ก "
            "คุณต้องหยุดรถและเปิดทางให้รถจากทางขวาไปก่อนเสมอ ห้ามขับเบียดหรือแย่งทางเด็ดขาดครับผม"
        ),
        "content_en": (
            "In Thailand, informal driving habits often allow larger vehicles to take precedence, "
            "and drivers merge wherever an opening appears. In Norway, the law is crystal clear and absolute: "
            "The right-hand rule (Traffic Rules § 7) means you MUST give way to all vehicles approaching from your right, "
            "unless traffic signs or signals state otherwise. Vehicle size does not matter — whether you drive a lorry "
            "or a compact car, you must stop and grant free passage!"
        ),
        "metafor_no": "Kongen og tjeneren: Bilen fra høyre er kongen. Har du vikeplikt, er du tjeneren — og tjeneren skal aldri få kongen til å bremse eller nøle.",
        "metafor_th": "กฎ 'ราชาและคนรับใช้': รถที่มาจากทางขวาคือ 'พระราชา' ส่วนเราผู้มีหน้าที่ให้ทางคือ 'คนรับใช้' — คนรับใช้จะต้องไม่ทำให้พระราชาต้องแตะเบรกหรือลังเลใจเด็ดขาดครับ",
        "metafor_en": "The King and the Servant: The car from the right is the king. If you must yield, you are the servant — and the servant must never cause the king to brake or hesitate."
    },
    {
        "id": "lesson_2_pedestrians",
        "topic": "fotgjengere_gangfelt",
        "law_ref": "Trafikkreglene § 9 / Vegtrafikkloven § 3",
        "keywords": [
            "gangfelt", "fotgjenger", "fotgjengere", "stopplikt", "zebra", "crossing",
            "pedestrian", "pedestrians", "ทางม้าลาย", "คนข้ามถนน", "คนเดินเท้า", "หยุดให้คนข้าม"
        ],
        "title_no": "Fotgjengere i gangfelt: Absolutt stopplikt",
        "title_th": "คนข้ามถนนบริเวณทางม้าลาย: หน้าที่หยุดรถอย่างเด็ดขาด",
        "title_en": "Pedestrians at Crossings: Absolute Duty to Stop",
        "norway_rule_no": "I Norge har fotgjengere ubetinget forkjørsrett i gangfelt (§ 9). Du må senke farten i god tid og stoppe helt hvis noen er i eller på vei ut i feltet.",
        "norway_rule_th": "ในนอร์เวย์ คนเดินเท้ามีสิทธิ์เด็ดขาดบนทางม้าลาย (§ 9) คุณต้องชะลอความเร็วแต่เนิ่นๆ และหยุดรถสนิทหากมีคนอยู่บนทางม้าลายหรือกำลังจะก้าวลงมา",
        "norway_rule_en": "In Norway, pedestrians have absolute priority at zebra crossings (§ 9). You must slow down well in advance and come to a complete stop if someone is crossing or about to cross.",
        "thailand_habit_no": "I Thailand må fotgjengere ofte vente lenge og vike for biler, og biler stopper sjelden spontant ved fotgjengeroverganger.",
        "thailand_habit_th": "ในประเทศไทย คนเดินเท้ามักจะต้องเป็นฝ่ายหยุดรอและหลบรถยนต์ และรถยนต์ส่วนใหญ่มักไม่ค่อยหยุดให้คนข้ามทางม้าลาย",
        "thailand_habit_en": "In Thailand, pedestrians frequently have to wait and yield to oncoming vehicles, and cars rarely stop automatically at crosswalks.",
        "content_no": (
            "I Norge har fotgjengere en hellig posisjon i trafikken. Trafikkreglene § 9 slår fast at kjørende "
            "har ubetinget vikeplikt for fotgjengere som befinner seg i gangfelt eller er på vei ut i det. "
            "Du må bremse i god tid og vise tydelig med fartsreduksjon at du har tenkt å stoppe. "
            "Unnlater du å stanse for fotgjengere i Norge, risikerer du umiddelbart førerkortbeslag og et strengt forelegg!"
        ),
        "content_th": (
            "ในประเทศนอร์เวย์ คนเดินเท้ามีสถานะที่ได้รับการปกป้องสูงสุดตามกฎหมายครับ Trafikkreglene § 9 กำหนดอย่างชัดเจนว่า "
            "ผู้ขับขี่มีหน้าที่ต้องหยุดให้ทางแก่คนเดินเท้าที่อยู่บนทางม้าลาย หรือกำลังเดินก้าวลงสู่ทางม้าลายอย่างไม่มีเงื่อนไข "
            "คุณต้องชะลอความเร็วล่วงหน้าเพื่อให้คนเดินเท้าเห็นอย่างชัดเจนว่าคุณกำลังจะหยุดรถให้เขา "
            "หากคุณไม่หยุดให้คนข้ามทางม้าลายในนอร์เวย์ คุณอาจถูกยึดใบขับขี่ทันทีและถูกปรับเป็นจำนวนเงินที่สูงมากครับผม!"
        ),
        "content_en": (
            "In Norway, pedestrians hold a strictly protected status in traffic. Traffic Rules § 9 states that drivers "
            "have an unconditional duty to yield to pedestrians who are in or stepping onto a pedestrian crossing. "
            "You must slow down well in advance to clearly communicate that you intend to stop. "
            "Failing to stop for a pedestrian in Norway risks immediate confiscation of your driving licence and heavy fines!"
        ),
        "metafor_no": "Fotgjengeren er 'Kongen til fots': Vis tidlig med bremselysene at du bøyer deg for kongen.",
        "metafor_th": "คนเดินเท้าคือ 'พระราชาผู้เดินเท้า': จงแตะเบรกแต่เนิ่นๆ ให้ไฟเบรกสว่างขึ้น เพื่อแสดงความเคารพและให้ทางแก่พระราชาครับ",
        "metafor_en": "The pedestrian is the 'King on foot': Show early with your brake lights that you are yielding to the king."
    },
    {
        "id": "lesson_3_roundabout",
        "topic": "rundkjoring",
        "law_ref": "Trafikkreglene § 7-2 og Skilt 202",
        "keywords": [
            "rundkjøring", "rundkjøringer", "vikeplikt rundkjøring", "feltskifte", "blinklys rundkjøring",
            "roundabout", "roundabouts", "วงเวียน", "เข้าวงเวียน", "ออกจากวงเวียน", "ไฟเลี้ยววงเวียน"
        ],
        "title_no": "Rundkjøring: Vikeplikt ved innkjøring og obligatorisk blinking",
        "title_th": "วงเวียน: การให้ทางก่อนเข้าและกฎการเปิดไฟเลี้ยวที่ถูกต้อง",
        "title_en": "Roundabouts: Priority on Entry and Mandatory Signaling",
        "norway_rule_no": "Før innkjøring i rundkjøring har du vikeplikt for all trafikk inne i sirkelen (Skilt 202). Du skal alltid blinke til høyre på vei ut av rundkjøringen.",
        "norway_rule_th": "ก่อนขับเข้าสู่วงเวียน คุณต้องให้ทางแก่รถทุกคันที่แล่นอยู่ในวงเวียนอยู่แล้วเสมอ (ป้าย 202) และต้องเปิดไฟเลี้ยวขวาเมื่อกำลังจะออกจากวงเวียนทุกครั้ง",
        "norway_rule_en": "Before entering a roundabout, you must yield to all traffic already inside the circle (Sign 202). You must always signal right when exiting.",
        "thailand_habit_no": "I Thailand er rundkjøringer sjeldnere og har ofte uklare vikepliktsituasjoner der man prøver å smette forbi uten streng feltdisiplin.",
        "thailand_habit_th": "ในประเทศไทย วงเวียนมีค่อนข้างน้อย และการให้ทางมักไม่เคร่งครัด ผู้ขับขี่มักพยายามเร่งเครื่องแทรกตัวเข้าไปโดยไม่มีระเบียบเลนที่ชัดเจน",
        "thailand_habit_en": "In Thailand, roundabouts are less common, and yielding rules are often informal with drivers squeezing in without strict lane discipline.",
        "content_no": (
            "I en norsk rundkjøring er prinsippet enkelt: Alle som skal inn i rundkjøringen har vikeplikt "
            "for kjøretøy som allerede er inne i rundkjøringen (regulert av vikepliktskilt 202). "
            "Plasser deg i riktig felt i god tid før rundkjøringen: skal du til høyre eller rett frem, velg normalt høyre felt; "
            "skal du til venstre, velg venstre felt. Det er lovpålagt å blinke til høyre i god tid før du svinger ut!"
        ),
        "content_th": (
            "ในวงเวียนของนอร์เวย์ หลักการขับขี่ชัดเจนและตรงไปตรงมาครับ: รถทุกคันที่กำลังจะเข้าสู่วงเวียน "
            "มีหน้าที่ต้องให้ทางแก่รถที่แล่นวนอยู่ในวงเวียนอยู่แล้วเสมอ (ควบคุมโดยป้ายให้ทาง 202) "
            "คุณต้องเลือกเลนให้ถูกต้องตั้งแต่ก่อนเข้าวงเวียน: หากจะเลี้ยวขวาหรือตรงไป ให้ใช้เลนขวา; หากจะเลี้ยวซ้ายหรือกลับรถ ให้เข้าเลนซ้าย "
            "และกฎหมายกำหนดให้ต้องเปิดไฟเลี้ยวขวาล่วงหน้าก่อนออกจากวงเวียนเสมอครับผม"
        ),
        "content_en": (
            "In Norwegian roundabouts, the rule is straightforward: Traffic entering the roundabout must yield "
            "to vehicles already circulating inside (governed by Give Way sign 202). "
            "Select the correct lane well before entering: if turning right or proceeding straight, normally choose the right lane; "
            "if turning left, choose the left lane. Signaling right before your exit is mandatory by law!"
        ),
        "metafor_no": "Rundkjøringen er en roterende karusell: Du hopper ikke på før setet er ledig, og du gir signal når du skal av.",
        "metafor_th": "วงเวียนเปรียบเหมือนม้าหมุนที่กำลังหมุนอยู่ครับ: เราจะไม่กระโดดเข้าไปจนกว่าจะมีที่ว่าง และส่งสัญญาณไฟเลี้ยวบอกเมื่อเราจะลงครับ",
        "metafor_en": "The roundabout is a carousel: You do not step in until there is an open space, and you always signal when getting off."
    },
    {
        "id": "lesson_4_promille",
        "topic": "promillegrense_alkohol",
        "law_ref": "Vegtrafikkloven § 22 (0,2 ‰ grense)",
        "keywords": [
            "promille", "promillegrense", "alkohol", "rus", "fyllekjøring", "drikke og kjøre",
            "alcohol", "drink driving", "drunk driving", "bac", "blood alcohol",
            "เมาแล้วขับ", "แอลกอฮอล์", "ตรวจแอลกอฮอล์", "ดื่มเหล้า", "ระดับแอลกอฮอล์"
        ],
        "title_no": "Promillegrense i Norge: 0,2 ‰ og nulltoleranse",
        "title_th": "ระดับแอลกอฮอล์ในนอร์เวย์: 0.2 มิลลิกรัมและนโยบายปลอดแอลกอฮอล์ 100%",
        "title_en": "Blood Alcohol Limit in Norway: 0.2 ‰ Zero Tolerance",
        "norway_rule_no": "I Norge er promillegrensen 0,2 ‰ (Vegtrafikkloven § 22). Ett glass øl eller vin kan være nok til å miste førerkortet og få fengselsstraff.",
        "norway_rule_th": "ในนอร์เวย์ กฎหมายกำหนดระดับแอลกอฮอล์ในเลือดสูงสุดเพียง 0.2 มิลลิกรัม (§ 22) เบียร์หรือไวน์เพียงแก้วเดียวก็อาจทำให้คุณถูกยึดใบขับขี่และจำคุกได้",
        "norway_rule_en": "In Norway, the legal blood alcohol limit is 0.2 ‰ (Road Traffic Act § 22). A single glass of beer or wine can lead to licence suspension and prison time.",
        "thailand_habit_no": "I Thailand er grensen 0,5 mg/ml (0,5 ‰), men sosial toleranse for å kjøre etter 'et par drinker' forekommer dessverre ofte.",
        "thailand_habit_th": "ในประเทศไทย กฎหมายกำหนดไว้ที่ 0.5 มิลลิกรัมเปอร์เซ็นต์ แต่ในสังคมยังมีความประมาทเรื่อง 'ดื่มนิดหน่อยแล้วขับกลับบ้าน' เกิดขึ้นบ่อยครั้ง",
        "thailand_habit_en": "In Thailand, the statutory limit is 0.5 mg/ml, but informal social tolerance for driving after a drink or two unfortunately persists.",
        "content_no": (
            "Norge har en av verdens strengeste promillelover. Grensen på 0,2 ‰ betyr i praksis fullstendig nulltoleranse. "
            "Allerede ved 0,2 til 0,5 ‰ risikerer du bot tilsvarende 1,5 månedslønner og tap av førerkortet i minst ett år. "
            "Over 0,5 ‰ idømmes betinget eller ubetinget fengsel. Husk også at alkohol forbrennes sakte — drikker du kvelden før, "
            "kan du fortsatt ha ulovlig promille morgenen etter!"
        ),
        "content_th": (
            "ประเทศนอร์เวย์มีกฎหมายเมาแล้วขับที่เข้มงวดที่สุดในโลกแห่งหนึ่งครับ ขีดจำกัดที่ 0.2 มิลลิกรัมหมายถึงนโยบายปลอดแอลกอฮอล์โดยสิ้นเชิง "
            "เพียงแค่มีระดับแอลกอฮอล์ 0.2 ถึง 0.5 มิลลิกรัม คุณจะถูกปรับเงินสูงถึง 1.5 เท่าของเงินเดือนทั้งเดือน และถูกยึดใบขับขี่อย่างน้อย 1 ปี "
            "หากเกิน 0.5 มิลลิกรัมขึ้นไป มีโทษจำคุกทันทีครับ! และจำไว้ว่าแอลกอฮอล์สลายตัวช้ามาก หากดื่มในคืนก่อนหน้า เช้าวันรุ่งขึ้นคุณอาจยังมีระดับแอลกอฮอล์ตกค้างอยู่ครับผม"
        ),
        "content_en": (
            "Norway has some of the strictest drink-driving legislation in the world. The 0.2 ‰ threshold practically means zero tolerance. "
            "Even at 0.2 to 0.5 ‰, you face a fine equal to 1.5 times your gross monthly salary and loss of licence for at least one year. "
            "Exceeding 0.5 ‰ frequently leads to conditional or unconditional imprisonment. Keep in mind that alcohol metabolises slowly — "
            "drinking the night before can still leave you over the legal limit the next morning!"
        ),
        "metafor_no": "Ratt og alkohol er som olje og vann: De kan aldri blandes. Skal du kjøre i morgen, la flasken stå i kveld.",
        "metafor_th": "พวงมาลัยรถกับแอลกอฮอล์เหมือนน้ำกับน้ำมันครับ: เข้ากันไม่ได้อย่างสิ้นเชิง หากต้องขับรถ จงงดดื่มแอลกอฮอล์ 100% ครับผม",
        "metafor_en": "Steering wheel and alcohol are like oil and water: They never mix. If you plan to drive, stay 100% sober."
    },
    {
        "id": "lesson_5_lights",
        "topic": "lys_og_blinklys",
        "law_ref": "Trafikkreglene § 15 / Kjøretøyforskriften",
        "keywords": [
            "kjørelys", "nærlys", "fjernlys", "blinklys", "blinke", "lys",
            "headlights", "lights", "indicators", "turn signal", "flashing",
            "ไฟหน้ารถ", "ไฟเลี้ยว", "เปิดไฟหน้ารถ", "ไฟตัดหมอก", "ไฟสูง"
        ],
        "title_no": "Bruk av lys og blinklys: Kjørelys 24/7 og entydig blinking",
        "title_th": "การใช้ไฟหน้ารถและไฟเลี้ยว: เปิดไฟหน้าตลอด 24 ชั่วโมง และความหมายของสัญญาณไฟ",
        "title_en": "Lights and Turn Signals: Daytime Running Lights 24/7 & Clear Signalling",
        "norway_rule_no": "I Norge er kjørelys påbudt døgnet rundt, hele året (§ 15). Blinking skal gjøres i god tid før enhver sving, feltskifte eller utkjøring fra rundkjøring.",
        "norway_rule_th": "ในนอร์เวย์ กฎหมายกำหนดให้เปิดไฟหน้ารถตลอด 24 ชั่วโมงทุกวันตลอดทั้งปี (§ 15) และต้องเปิดไฟเลี้ยวล่วงหน้าก่อนเลี้ยว เปลี่ยนเลน หรือออกจากวงเวียนเสมอ",
        "norway_rule_en": "In Norway, daytime running lights are mandatory 24 hours a day, all year round (§ 15). Turn signals must be given well ahead of any turn, lane change, or roundabout exit.",
        "thailand_habit_no": "I Thailand bruker man ofte ikke lys på dagtid, og enkelte bruker langlys uformelt for å si 'jeg viker ikke', eller venstreblink for 'kjør forbi meg'.",
        "thailand_habit_th": "ในประเทศไทย มักไม่เปิดไฟหน้าตอนกลางวัน และบางครั้งมีการกะพริบไฟสูงเพื่อบอกว่า 'ฉันกำลังจะไป ห้ามตัดหน้า' หรือเปิดไฟเลี้ยวซ้ายเพื่อบอกให้คันหลังแซง",
        "thailand_habit_en": "In Thailand, lights are rarely used in daylight, and flashing high beams is sometimes informally used to assert 'I am coming through', or left indicator to say 'pass me'.",
        "content_no": (
            "I Norge er det lovpålagt å kjøre med tent lys hele døgnet, selv på de lyseste sommerdagene (Trafikkreglene § 15). "
            "Dette skyldes at biler med lys oppdages mye raskere i sidespeil og i skogkledde landskap. "
            "Blinklyset er ditt eneste språk overfor andre trafikanter: Bruk det alltid i god tid før sving, rundkjøring eller feltskifte. "
            "Husk at å blinke med fjernlys i Norge betyr en advarsel om fare eller at du gir noen forkjørsrett — aldri at du krever å kjøre først!"
        ),
        "content_th": (
            "ในนอร์เวย์ มีกฎหมายบังคับให้รถยนต์ทุกคันต้องเปิดไฟหน้าวิ่งตลอด 24 ชั่วโมง แม้ในวันที่แดดจ้าที่สุดของฤดูร้อนครับ (Trafikkreglene § 15) "
            "เพราะรถที่เปิดไฟจะช่วยให้ผู้ขับขี่คันอื่นมองเห็นได้เร็วกว่ามากในกระจกมองข้างและท่ามกลางทิวทัศน์ธรรมชาติ "
            "สัญญาณไฟเลี้ยวคือ 'ภาษาพูดเดียว' ของคุณกับเพื่อนร่วมทาง: จงเปิดไฟเลี้ยวก่อนเปลี่ยนเลน เลี้ยว หรือออกจากวงเวียนเสมอ "
            "และจำไว้ว่าการกะพริบไฟสูงในนอร์เวย์ หมายถึงการเตือนอันตราย หรือการแสดงน้ำใจให้ผู้อื่นไปก่อน — ไม่ใช่การเร่งเพื่อแย่งทางครับผม!"
        ),
        "content_en": (
            "In Norway, daytime running lights are legally mandatory 24/7, even on bright summer days (Traffic Rules § 15). "
            "Illuminated vehicles are spotted much earlier in rear-view mirrors and across shadowed Nordic landscapes. "
            "Your indicators are your only formal language to communicate intent: Always signal well ahead of turning, changing lanes, or exiting roundabouts. "
            "Remember that flashing high beams in Norway conveys a warning of danger or yielding courtesy — never an aggressive demand to go first!"
        ),
        "metafor_no": "Bilen din skal være synlig som et fyrtårn: Lysene er øynene dine, og blinklyset er stemmen din i trafikken.",
        "metafor_th": "รถของคุณต้องสว่างชัดเจนเหมือนประภาคาร: ไฟหน้าคือดวงตา และไฟเลี้ยวคือเสียงพูดของคุณบนท้องถนนครับ",
        "metafor_en": "Your car should be visible like a lighthouse: Lights are your eyes, and signals are your voice in traffic."
    },
    {
        "id": "lesson_6_winter",
        "topic": "vinterkjoring",
        "law_ref": "Kjøretøyforskriften § 1-4 / Vegtrafikkloven § 3",
        "keywords": [
            "vinterkjøring", "glatt føre", "snø", "is", "bremselengde", "piggdekk", "vinterdekk",
            "winter driving", "snow", "ice", "braking distance", "studded tyres",
            "ขับรถฤดูหนาว", "หิมะ", "น้ำแข็ง", "ถนนลื่น", "ระยะเบรก", "ยางฤดูหนาว"
        ],
        "title_no": "Vinterkjøring: Bremselengde på snø og is",
        "title_th": "การขับรถในฤดูหนาว: ระยะเบรกบนหิมะและน้ำแข็ง",
        "title_en": "Winter Driving: Braking Distances on Snow and Ice",
        "norway_rule_no": "På snø og is øker bremselengden med 4 til 8 ganger. Bilen må ha godkjente vinterdekk (minst 3 mm mønsterdybde, anbefalt 4-5 mm) og du må holde minst 3-4 sekunders avstand.",
        "norway_rule_th": "บนหิมะและน้ำแข็ง ระยะเบรกจะเพิ่มขึ้นมากถึง 4 ถึง 8 เท่า รถต้องใส่ยางฤดูหนาวที่ได้มาตรฐาน (ความลึกดอกยางอย่างน้อย 3 มม. แนะนำ 4-5 มม.) และต้องเว้นระยะห่าง 3-4 วินาทีขึ้นไป",
        "norway_rule_en": "On snow and ice, braking distance increases by 4 to 8 times. The vehicle must be fitted with approved winter tyres (min. 3 mm tread, recommended 4-5 mm) and you must keep at least 3-4 seconds distance.",
        "thailand_habit_no": "I Thailand finnes ikke glatte vinterveier, og bilister er vant til konstant høyt veigrep året rundt.",
        "thailand_habit_th": "ในประเทศไทยไม่มีสภาพถนนลื่นหรือน้ำแข็งติดลบ ผู้ขับขี่จึงเคยชินกับการมีแรงยึดเกาะถนนสูงคงที่ตลอดทั้งปี",
        "thailand_habit_en": "In Thailand, icy winter roads do not exist, and motorists are accustomed to consistent high grip year-round.",
        "content_no": (
            "Vinterkjøring i Norge krever en helt spesiell mental omstilling. På glatt føre reduseres veigrepet dramatisk, "
            "og bremselengden kan bli fire til åtte ganger lengre enn på tørr sommerasfalt! "
            "Du må aldri gjøre brå rattutslag eller hogge i bremsene. Hold god avstand til bilen foran (minst 3 til 4 sekunder), "
            "og brems rolig i god tid før svinger og kryss. Kravet til mønsterdybde på vinterdekk er minimum 3 mm, men 4–5 mm anbefales sterkt."
        ),
        "content_th": (
            "การขับรถในฤดูหนาวของนอร์เวย์ต้องอาศัยการปรับตัวทางจิตวิทยาอย่างมากครับ บนถนนที่ลื่น แรงยึดเกาะถนนจะลดลงอย่างมหาศาล "
            "และระยะเบรกอาจยาวขึ้นกว่าถนนแห้งในฤดูร้อนถึง 4 ถึง 8 เท่า! "
            "ห้ามหมุนพวงมาลัยกะทันหันหรือเหยียบเบรกแรงๆ เด็ดขาด จงเว้นระยะห่างจากคันหน้าอย่างปลอดภัย (อย่างน้อย 3 ถึง 4 วินาที) "
            "และเริ่มแตะเบรกอย่างนุ่มนวลแต่เนิ่นๆ ก่อนถึงทางโค้งหรือทางแยก ความลึกของดอกยางฤดูหนาวตามกฎหมายต้องไม่ต่ำกว่า 3 มม. (แนะนำ 4-5 มม. เพื่อความปลอดภัยสูงสุดครับผม)"
        ),
        "content_en": (
            "Winter driving in Norway demands a completely altered driving mindset. On slippery surfaces, road grip drops drastically, "
            "and braking distance can multiply by four to eight times compared to dry summer asphalt! "
            "Never jerk the steering wheel or slam on the brakes. Keep a generous following distance (at least 3 to 4 seconds), "
            "and apply gentle braking well ahead of curves and junctions. The minimum legal tread depth for winter tyres is 3 mm, though 4–5 mm is strongly advised."
        ),
        "metafor_no": "På vinterføre kjører du på glass: Alle bevegelser må være silkemyke og planlagt i god tid før de skjer.",
        "metafor_th": "ขับรถบนน้ำแข็งเหมือนขับบนแผ่นแก้วบางๆ ครับ: ทุกการหมุนพวงมาลัยและการแตะเบรกต้องนุ่มนวลและคิดล่วงหน้าเสมอครับผม",
        "metafor_en": "Driving in winter is like driving on glass: All movements must be silky smooth and planned well ahead of time."
    }
]

MICRO_LESSONS = CULTURE_LESSONS


def _normalize_lang(lang: str) -> str:
    """Normalize language code to one of 'no', 'th', 'en'."""
    clean = (lang or "th").strip().lower()
    if clean in ("th", "thai"):
        return "th"
    if clean in ("no", "nb", "norwegian", "norsk"):
        return "no"
    if clean in ("en", "english"):
        return "en"
    return "th"


def get_localized_lessons(language: str = "th", topic: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return micro-lessons fully localized to target language with 100% language isolation."""
    lang = _normalize_lang(language)
    result = []

    for item in CULTURE_LESSONS:
        if topic and item.get("topic") != topic:
            continue

        localized = {
            "id": item["id"],
            "topic": item["topic"],
            "law_ref": item["law_ref"],
            "language": lang,
            "title": item.get(f"title_{lang}") or item.get("title_th") or "",
            "content": item.get(f"content_{lang}") or item.get("content_th") or "",
            "metafor": item.get(f"metafor_{lang}") or item.get("metafor_th") or "",
            "norway_rule": item.get(f"norway_rule_{lang}") or item.get("norway_rule_th") or "",
            "thailand_habit": item.get(f"thailand_habit_{lang}") or item.get("thailand_habit_th") or "",
        }
        result.append(localized)

    return result


def get_micro_lesson_by_id(lesson_id: str, language: str = "th") -> Optional[Dict[str, Any]]:
    """Find a specific micro-lesson by id localized to the declared language."""
    lang = _normalize_lang(language)
    for item in CULTURE_LESSONS:
        if item["id"] == lesson_id:
            return {
                "id": item["id"],
                "topic": item["topic"],
                "law_ref": item["law_ref"],
                "language": lang,
                "title": item.get(f"title_{lang}") or "",
                "content": item.get(f"content_{lang}") or "",
                "metafor": item.get(f"metafor_{lang}") or "",
                "norway_rule": item.get(f"norway_rule_{lang}") or "",
                "thailand_habit": item.get(f"thailand_habit_{lang}") or "",
            }
    return None


def find_relevant_micro_lesson(query: str, language: str = "th") -> Optional[Dict[str, Any]]:
    """Match user query against micro-lesson topics and keywords with smart weighting."""
    if not query or not query.strip():
        return None

    q_lower = query.lower()
    lang = _normalize_lang(language)

    best_match = None
    best_score = 0

    for item in CULTURE_LESSONS:
        score = 0
        # Check explicit keywords
        for kw in item.get("keywords", []):
            kw_l = kw.lower()
            if kw_l in q_lower:
                # Give higher weight to longer / multi-word keywords
                kw_weight = max(len(kw_l.split()) * 5, len(kw_l) // 2)
                score += max(kw_weight, 4)

        # Check topic
        if item.get("topic", "").lower() in q_lower:
            score += 6

        # Check title terms (with punctuation stripped)
        title_curr = item.get(f"title_{lang}", "").lower()
        title_tokens = re.findall(r'[\w]+', title_curr)
        for token in title_tokens:
            if len(token) >= 4 and token in q_lower:
                score += 3

        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score >= 3:
        return {
            "id": best_match["id"],
            "topic": best_match["topic"],
            "law_ref": best_match["law_ref"],
            "language": lang,
            "title": best_match.get(f"title_{lang}") or "",
            "content": best_match.get(f"content_{lang}") or "",
            "metafor": best_match.get(f"metafor_{lang}") or "",
            "norway_rule": best_match.get(f"norway_rule_{lang}") or "",
            "thailand_habit": best_match.get(f"thailand_habit_{lang}") or "",
        }

    return None


def format_micro_lesson_context(lesson: Dict[str, Any], language: str = "th") -> str:
    """Format a micro-lesson into a pedagogical RAG context block for Michael."""
    lang = _normalize_lang(language)

    headers = {
        "th": "━━━ บทเรียนพิเศษวัฒนธรรมการขับขี่: เปรียบเทียบนอร์เวย์ vs ไทย (THAILAND VS NORWAY CULTURE) ━━━",
        "no": "━━━ SPESIALLEKSJON KJØREKULTUR: THAILAND VS NORGE ━━━",
        "en": "━━━ SPECIAL MICRO-LESSON: THAILAND VS NORWAY CULTURE ━━━"
    }

    labels = {
        "th": {
            "topic": "หัวข้อ",
            "law": "กฎหมายนอร์เวย์",
            "th_habit": "ความคุ้นชินในไทย",
            "no_rule": "กฎที่ต้องปฏิบัติในนอร์เวย์",
            "metafor": "คำสอน/อุปมาของครูไมเคิล"
        },
        "no": {
            "topic": "Tema",
            "law": "Lovhjemmel",
            "th_habit": "Uformell vane i Thailand",
            "no_rule": "Gjeldende regel i Norge",
            "metafor": "Michaels pedagogiske huskeregel"
        },
        "en": {
            "topic": "Topic",
            "law": "Norwegian Law",
            "th_habit": "Habit in Thailand",
            "no_rule": "Mandatory Rule in Norway",
            "metafor": "Michael's Pedagogical Rule of Thumb"
        }
    }

    hdr = headers.get(lang, headers["th"])
    lbl = labels.get(lang, labels["th"])

    return (
        f"\n{hdr}\n"
        f"• {lbl['topic']}: {lesson.get('title', '')} ({lesson.get('topic', '')})\n"
        f"• {lbl['law']}: {lesson.get('law_ref', '')}\n"
        f"• {lbl['th_habit']}: {lesson.get('thailand_habit', '')}\n"
        f"• {lbl['no_rule']}: {lesson.get('norway_rule', '')}\n"
        f"• {lbl['metafor']}: {lesson.get('metafor', '')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )


def get_micro_lesson_media_card(lesson: Dict[str, Any], language: str = "th") -> Dict[str, Any]:
    """
    Format a micro-lesson into a Michael Chat media card.
    """
    lang = _normalize_lang(language)
    lesson_id = lesson.get("id", "")
    title = lesson.get("title") or lesson.get(f"title_{lang}") or ""
    caption = lesson.get("metafor") or lesson.get(f"metafor_{lang}") or lesson.get("norway_rule") or ""
    return {
        "id": f"micro-lesson:{lesson_id}",
        "type": "micro_lesson",
        "title": title,
        "caption": caption,
        "url": f"/api/micro-lessons/{lesson_id}",
    }


# ── REST Endpoints ──────────────────────────────────────────────────────────

@router.get("/api/micro-lessons")
@router.get("/micro-lessons")
async def get_micro_lessons_endpoint(
    language: str = Query("th", description="Preferred language code: th, no, en"),
    topic: Optional[str] = Query(None, description="Optional topic filter (e.g. vikeplikt_hoyreregel)"),
):
    """
    Return localized list of 'Thailand vs Norway' micro-lessons with 100% language isolation.
    """
    lang = _normalize_lang(language)
    lessons = get_localized_lessons(language=lang, topic=topic)

    return JSONResponse({
        "success": True,
        "language": lang,
        "count": len(lessons),
        "lessons": lessons
    })


@router.get("/api/micro-lessons/{lesson_id}")
@router.get("/micro-lessons/{lesson_id}")
async def get_micro_lesson_detail_endpoint(
    lesson_id: str,
    language: str = Query("th", description="Preferred language code: th, no, en"),
):
    """
    Return single localized 'Thailand vs Norway' micro-lesson by ID.
    """
    lang = _normalize_lang(language)
    lesson = get_micro_lesson_by_id(lesson_id, language=lang)
    if not lesson:
        return JSONResponse({"success": False, "error": "Lesson not found"}, status_code=404)
    return JSONResponse({
        "success": True,
        "language": lang,
        "lesson": lesson
    })


@router.get("/api/lessons/culture")
@router.get("/lessons/culture")
async def get_legacy_culture_lessons():
    """Backwards-compatible culture lessons endpoint."""
    return JSONResponse({
        "success": True,
        "count": len(CULTURE_LESSONS),
        "lessons": CULTURE_LESSONS
    })
