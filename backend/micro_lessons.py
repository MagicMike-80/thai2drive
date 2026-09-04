"""
Thailand vs Norge — Mikroleksjoner (Kjørekultur-pedagogikk)
------------------------------------------------------------
Pedagogisk sammenligning av trafikkultur i Thailand og Norge
for å bygge intuitive ryggmarksreflekser for thailandske elever.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["micro_lessons"])

CULTURE_LESSONS = [
    {
        "id": "lesson_1_priority",
        "topic": "vikeplikt_hoyreregel",
        "title_no": "Hvem bestemmer? Høyreregelen vs Størst bil",
        "title_th": "ใครกำหนด? กฎให้ทางขวา vs รถใหญ่ไปก่อน",
        "title_en": "Who has Priority? Right-hand Rule vs Biggest Vehicle",
        "content_no": (
            "I Thailand er det ofte uformell praksis at den største bilen kjører først, "
            "og trafikanter fletter seg inn der det er plass. I Norge er jussen absolutt! "
            "Høyreregelen (Trafikkreglene § 7) betyr at du MÅ vike for alle kjøretøy fra høyre, "
            "uansett om du kjører en stor lastebil eller en liten moped. Aldri press deg frem!"
        ),
        "content_th": (
            "ในประเทศไทย มักจะมีวิธีปฏิบัติอย่างไม่เป็นทางการคือ 'รถใหญ่ไปก่อน' "
            "และผู้ใช้รถใช้ถนนจะแทรกตัวเข้าไปเมื่อมีช่องว่าง แต่ในนอร์เวย์ กฎหมายมีผลเด็ดขาด! "
            "กฎการให้ทางด้านขวา (§ 7) หมายความว่าคุณต้องให้ทางแก่รถทุกคันที่มาจากทางขวา "
            "ไม่ว่าคุณจะขับรถบรรทุกขนาดใหญ่หรือรถจักรยานยนต์ขนาดเล็ก ห้ามขับเบียดหรือแทรกเด็ดขาดครับ!"
        ),
        "content_en": (
            "In Thailand, informal practice often allows larger vehicles to go first. "
            "In Norway, the law is absolute! The right-hand rule (Section 7) means you MUST give way "
            "to all vehicles coming from your right, regardless of vehicle size. Never push your way through!"
        ),
        "metafor_no": "I Norge er loven kongen: Har du vikeplikt, er du tjeneren. Tjeneren skal aldri få kongen til å bremse.",
        "metafor_th": "จำไว้ครับ: ในนอร์เวย์ 'กฎหมายคือพระราชา' ไม่มีใครใหญ่กว่ากฎจราจรครับผม",
        "metafor_en": "Remember: The law is king. If you have to yield, you are the servant."
    },
    {
        "id": "lesson_2_pedestrians",
        "topic": "fotgjengere_gangfelt",
        "title_no": "Fotgjengere: Absolutt vikeplikt i gangfelt",
        "title_th": "คนข้ามถนน: หน้าที่ให้ทางเด็ดขาดบริเวณทางม้าลาย",
        "title_en": "Pedestrians: Absolute Right of Way at Crossings",
        "content_no": (
            "I Norge har fotgjengere en hellig status. Du har ubetinget vikeplikt for "
            "alle som befinner seg i eller er på vei ut i et gangfelt. I Thailand er det "
            "vanlig at fotgjengere må vike for bilene. I Norge mister du førerkortet eller "
            "får store bøter hvis du ikke stopper!"
        ),
        "content_th": (
            "ในนอร์เวย์ คนเดินเท้ามีสถานะที่ศักดิ์สิทธิ์มากครับ คุณมีหน้าที่ต้องหยุดให้ทางอย่างไม่มีเงื่อนไข "
            "แก่ทุกคนที่อยู่บนทางม้าลายหรือกำลังจะเดินก้าวลงสู่ทางม้าลาย ในประเทศไทย คนเดินเท้ามักต้องหลบรถ "
            "แต่ในนอร์เวย์ หากคุณไม่หยุดรถ คุณจะถูกยึดใบขับขี่หรือถูกปรับหนักมากครับผม!"
        ),
        "content_en": (
            "In Norway, pedestrians have absolute priority at zebra crossings. You must yield "
            "to anyone on or stepping onto the crossing. Failing to yield can lead to immediate licence loss."
        ),
        "metafor_no": "Fotgjengeren i gangfeltet er kongen — du som sjåfør skal alltid bremse i god tid.",
        "metafor_th": "คนเดินเท้าเปรียบเสมือน 'ราชาผู้เดินถนน' เราเป็นคนขับรถคือคนรับใช้ที่ต้องหยุดรอเสมอครับ",
        "metafor_en": "The pedestrian at the crossing is the king — always slow down and stop early."
    },
    {
        "id": "lesson_3_roundabout",
        "topic": "rundkjoring",
        "title_no": "Rundkjøring: Vikeplikt ved innkjøring & Feltskifte",
        "title_th": "วงเวียน: การให้ทางก่อนเข้าและกฎการเปลี่ยนเลน",
        "title_en": "Roundabouts: Giving Way on Entry & Lane Selection",
        "content_no": (
            "I en norsk rundkjøring har alle som skal inn vikeplikt for trafikk som allerede er i rundkjøringen. "
            "Husk blinklys ut av rundkjøringen, og velg riktig felt i god tid før du kjører inn."
        ),
        "content_th": (
            "ในวงเวียนของนอร์เวย์ รถที่จะขับเข้าสู่วงเวียนต้องให้ทางแก่รถที่อยู่ในวงเวียนอยู่แล้วเสมอครับ "
            "และต้องเปิดไฟเลี้ยวขวาก่อนออกจากวงเวียนทุกครั้ง พร้อมเลือกเลนให้ถูกต้องตั้งแต่ก่อนเข้าครับผม"
        ),
        "content_en": (
            "In Norwegian roundabouts, traffic entering must give way to traffic already inside. "
            "Always signal right when exiting and select the correct lane before entry."
        ),
        "metafor_no": "Rundkjøringen er en elv: Du kan ikke hoppe uti før det er klar bane.",
        "metafor_th": "วงเวียนเปรียบเหมือนสายน้ำที่ไหลอยู่ครับ: เราต้องรอจังหวะว่างก่อนแทรกตัวเข้าไปครับ",
        "metafor_en": "The roundabout is a flowing river: Wait for a clear gap before entering."
    },
    {
        "id": "lesson_4_winter",
        "topic": "vinterkjoring",
        "title_no": "Vinterkjøring: Bremselengde på snø og is",
        "title_th": "การขับรถในฤดูหนาว: ระยะเบรกบนหิมะและน้ำแข็ง",
        "title_en": "Winter Driving: Braking Distances on Snow and Ice",
        "content_no": (
            "Snø og is kan øke bremsestrekningen med opptil 4 til 8 ganger sammenlignet med tørr asfalt! "
            "I Thailand finnes ikke glatte vinterveier. I Norge må du holde ekstremt god avstand (minimum 3-sekundersregelen) og gjøre rolige rattbevegelser."
        ),
        "content_th": (
            "หิมะและน้ำแข็งสามารถเพิ่มระยะเบรกได้มากถึง 4 ถึง 8 เท่าเมื่อเทียบกับถนนแห้งครับ! "
            "ในประเทศไทยไม่มีสภาพถนนลื่นแบบนี้ ในนอร์เวย์คุณต้องเว้นระยะห่างมากๆ (กฎ 3 วินาทีขึ้นไป) และหมุนพวงมาลัยอย่างนุ่มนวลครับผม"
        ),
        "content_en": (
            "Snow and ice can increase braking distance by 4 to 8 times compared to dry roads! "
            "Keep ample following distance (at least 3-4 seconds) and make smooth steering inputs."
        ),
        "metafor_no": "På vinterføre kjører du på glass: Alle bevegelser må være myke og planlagte.",
        "metafor_th": "ขับรถบนน้ำแข็งเหมือนขับบนแผ่นแก้วครับ: ทุกการแตะเบรกและหมุนพวงมาลัยต้องนุ่มนวลที่สุดครับผม",
        "metafor_en": "Winter driving is like driving on glass: All maneuvers must be smooth and gentle."
    }
]

@router.get("/api/lessons/culture")
@router.get("/lessons/culture")
async def get_culture_lessons():
    """Returnerer mikroleksjoner for 'Thailand vs Norge' kjørekultur."""
    return JSONResponse({
        "success": True,
        "count": len(CULTURE_LESSONS),
        "lessons": CULTURE_LESSONS
    })
