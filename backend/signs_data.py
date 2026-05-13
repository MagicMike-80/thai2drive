"""
Norwegian traffic signs catalog — static data served via /api/signs.
Organized by type with trilingual names and descriptions.
"""

SIGNS = [
    # ─── FARESKILT (Warning — 1xx) ─────────────────────────────────────────
    {"num": "110", "type": "fare",
     "name": {"no": "Farlig sving", "th": "โค้งอันตราย", "en": "Dangerous curve"},
     "desc": {"no": "Advarsel om skarp sving i vegbanen. Reduser farten.", "th": "เตือนทางโค้งอันตราย ลดความเร็ว", "en": "Warning of a sharp curve ahead. Reduce speed."}},
    {"num": "112", "type": "fare",
     "name": {"no": "Farlig vegkryss", "th": "ทางแยกอันตราย", "en": "Dangerous intersection"},
     "desc": {"no": "Advarsel om vegkryss med dårlig sikt eller økt farerisiko.", "th": "เตือนทางแยกที่มองเห็นได้ไม่ดี", "en": "Warning of an intersection with poor visibility or increased risk."}},
    {"num": "130", "type": "fare",
     "name": {"no": "Smalere veg", "th": "ถนนแคบลง", "en": "Road narrows"},
     "desc": {"no": "Vegen smalner inn. Vær forsiktig og tilpass hastigheten.", "th": "ถนนแคบลง ระวังและลดความเร็ว", "en": "The road narrows ahead. Be careful and reduce speed."}},
    {"num": "140", "type": "fare",
     "name": {"no": "Vegarbeid", "th": "มีการก่อสร้าง", "en": "Roadworks"},
     "desc": {"no": "Pågående vegarbeid. Reduser fart og følg skilt og signaler.", "th": "มีงานซ่อมถนน ลดความเร็วและปฏิบัติตามป้าย", "en": "Roadworks in progress. Reduce speed and follow signs."}},
    {"num": "142", "type": "fare",
     "name": {"no": "Glatt kjørebane", "th": "ถนนลื่น", "en": "Slippery road"},
     "desc": {"no": "Fare for glatt kjørebane. Reduser farten og øk avstand.", "th": "ถนนลื่น ลดความเร็วและเพิ่มระยะห่าง", "en": "Risk of slippery road. Reduce speed and increase following distance."}},
    {"num": "150", "type": "fare",
     "name": {"no": "Barn", "th": "ระวังเด็ก", "en": "Children"},
     "desc": {"no": "Skoleomåde eller lekeplass. Vær særlig oppmerksom på barn.", "th": "บริเวณโรงเรียนหรือสนามเด็กเล่น ระวังเด็ก", "en": "School zone or playground. Pay special attention to children."}},
    {"num": "160", "type": "fare",
     "name": {"no": "Dyr på vegen", "th": "ระวังสัตว์", "en": "Animals on road"},
     "desc": {"no": "Fare for dyr på vegen. Reduser farten.", "th": "ระวังสัตว์บนถนน ลดความเร็ว", "en": "Risk of animals on the road. Reduce speed."}},
    {"num": "166", "type": "fare",
     "name": {"no": "Elg", "th": "ระวังกวางมูส", "en": "Moose"},
     "desc": {"no": "Område med hyppige elgkryssinger. Kjør sakte og vær årvåken.", "th": "พื้นที่ที่กวางมูสมักข้ามถนน ขับช้าๆ", "en": "Area with frequent moose crossings. Drive slowly and stay alert."}},
    {"num": "202", "type": "fare",
     "name": {"no": "Fartshump", "th": "ระวังเนินชะลอความเร็ว", "en": "Speed bump"},
     "desc": {"no": "Fartshump i vegen. Reduser farten i god tid.", "th": "มีเนินชะลอความเร็ว ลดความเร็วล่วงหน้า", "en": "Speed bump ahead. Reduce speed well in advance."}},

    # ─── VIKEPLIKT / FORKJØRSRETT (Priority) ────────────────────────────────
    {"num": "202", "type": "vikeplikt",
     "name": {"no": "Vikeplikt", "th": "หยุดให้ทาง", "en": "Give way"},
     "desc": {"no": "Du har vikeplikt for all trafikk i krysset.", "th": "คุณต้องหยุดให้ยานพาหนะอื่นผ่านก่อน", "en": "You must give way to all traffic at the intersection."}},
    {"num": "204", "type": "vikeplikt",
     "name": {"no": "All stans og vikeplikt", "th": "หยุดสนิทและให้ทาง", "en": "Stop and give way"},
     "desc": {"no": "Du må stoppe helt opp og gi all trafikk fri passasje (stoppskilt).", "th": "ต้องหยุดสนิทและให้ยานพาหนะทั้งหมดผ่านก่อน", "en": "You must come to a complete stop and give all traffic free passage (stop sign)."}},
    {"num": "206", "type": "vikeplikt",
     "name": {"no": "Forkjørsrett", "th": "คุณมีสิทธิ์ผ่านก่อน", "en": "Right of way"},
     "desc": {"no": "Du har forkjørsrett i krysset. Krysstrafik har vikeplikt for deg.", "th": "คุณมีสิทธิ์ผ่านก่อนในทางแยก", "en": "You have priority at the intersection. Cross traffic must give way."}},
    {"num": "208", "type": "vikeplikt",
     "name": {"no": "Forkjørsveg", "th": "ทางหลักที่มีสิทธิ์ก่อน", "en": "Priority road"},
     "desc": {"no": "Du kjører på forkjørsveg. Du har forkjørsrett i alle kryss.", "th": "คุณอยู่บนทางหลัก มีสิทธิ์ผ่านก่อนในทุกทางแยก", "en": "You are on a priority road. You have right of way at all intersections."}},
    {"num": "210", "type": "vikeplikt",
     "name": {"no": "Slutt på forkjørsveg", "th": "สิ้นสุดทางหลัก", "en": "End of priority road"},
     "desc": {"no": "Forkjørsretten opphører. Du vil ha vikeplikt i neste kryss.", "th": "สิทธิ์ผ่านก่อนสิ้นสุด คุณจะต้องหยุดให้ทางที่ทางแยกถัดไป", "en": "Priority ends. You will have to give way at the next intersection."}},

    # ─── FORBUDSSKILT (Prohibition — 3xx) ───────────────────────────────────
    {"num": "302", "type": "forbud",
     "name": {"no": "Innkjøring forbudt", "th": "ห้ามเข้า", "en": "No entry"},
     "desc": {"no": "Innkjøring forbudt for alle kjøretøy.", "th": "ห้ามยานพาหนะทุกชนิดเข้า", "en": "No entry for any vehicle."}},
    {"num": "306", "type": "forbud",
     "name": {"no": "Forbikjøring forbudt", "th": "ห้ามแซง", "en": "No overtaking"},
     "desc": {"no": "Forbikjøring av motorvogner er forbudt.", "th": "ห้ามแซงรถยนต์", "en": "Overtaking of motor vehicles is prohibited."}},
    {"num": "308", "type": "forbud",
     "name": {"no": "Slutt på forbikjøringsforbud", "th": "สิ้นสุดเขตห้ามแซง", "en": "End of no overtaking zone"},
     "desc": {"no": "Forbudet mot forbikjøring oppheves.", "th": "เขตห้ามแซงสิ้นสุดแล้ว", "en": "The no overtaking prohibition is lifted."}},
    {"num": "312", "type": "forbud",
     "name": {"no": "Stans forbudt", "th": "ห้ามหยุด", "en": "No stopping"},
     "desc": {"no": "Stans er forbudt. Kjøretøyet må ikke stanses, selv for av- og påstigning.", "th": "ห้ามหยุดรถ แม้แต่เพื่อรับส่งผู้โดยสาร", "en": "Stopping is prohibited, even for passenger pick-up or drop-off."}},
    {"num": "316", "type": "forbud",
     "name": {"no": "Parkering forbudt", "th": "ห้ามจอดรถ", "en": "No parking"},
     "desc": {"no": "Parkering er forbudt på denne siden av vegen.", "th": "ห้ามจอดรถด้านนี้", "en": "Parking is prohibited on this side of the road."}},
    {"num": "322", "type": "forbud",
     "name": {"no": "Motorsykler forbudt", "th": "ห้ามรถจักรยานยนต์", "en": "No motorcycles"},
     "desc": {"no": "Motorsykler og mopeder har ikke adgang.", "th": "ห้ามรถจักรยานยนต์และมอเตอร์ไซค์เล็ก", "en": "Motorcycles and mopeds are not permitted."}},
    {"num": "330", "type": "forbud",
     "name": {"no": "Tyngre kjøretøy forbudt", "th": "ห้ามรถหนัก", "en": "No heavy vehicles"},
     "desc": {"no": "Forbudt for kjøretøy med totalvekt over angitt grense.", "th": "ห้ามรถที่มีน้ำหนักเกินกำหนด", "en": "Prohibited for vehicles exceeding the stated total weight."}},
    {"num": "362", "type": "forbud",
     "name": {"no": "Fartsgrense 50", "th": "ความเร็วสูงสุด 50", "en": "Speed limit 50"},
     "desc": {"no": "Største tillatte hastighet er 50 km/t. Gjelder til ny fartsgrense.", "th": "ความเร็วสูงสุด 50 กม./ชม.", "en": "Maximum speed is 50 km/h until the next speed sign."}},
    {"num": "364", "type": "forbud",
     "name": {"no": "Fartsgrense 80", "th": "ความเร็วสูงสุด 80", "en": "Speed limit 80"},
     "desc": {"no": "Største tillatte hastighet er 80 km/t.", "th": "ความเร็วสูงสุด 80 กม./ชม.", "en": "Maximum speed is 80 km/h."}},
    {"num": "366", "type": "forbud",
     "name": {"no": "Fartsgrense 100", "th": "ความเร็วสูงสุด 100", "en": "Speed limit 100"},
     "desc": {"no": "Største tillatte hastighet er 100 km/t.", "th": "ความเร็วสูงสุด 100 กม./ชม.", "en": "Maximum speed is 100 km/h."}},
    {"num": "374", "type": "forbud",
     "name": {"no": "Slutt på fartsgrense", "th": "สิ้นสุดเขตจำกัดความเร็ว", "en": "End of speed limit"},
     "desc": {"no": "Fartsgrenseskilt oppheves. Generell fartsgrense gjelder.", "th": "สิ้นสุดเขตจำกัดความเร็ว ใช้ความเร็วทั่วไป", "en": "Speed limit lifted. The general speed limit applies."}},

    # ─── PÅBUDSSKILT (Mandatory — 4xx) ──────────────────────────────────────
    {"num": "402", "type": "pabud",
     "name": {"no": "Kjør rett frem", "th": "ต้องตรงไป", "en": "Go straight"},
     "desc": {"no": "Du må kjøre rett frem forbi skiltet.", "th": "ต้องขับตรงไปผ่านป้าย", "en": "You must go straight ahead past the sign."}},
    {"num": "404", "type": "pabud",
     "name": {"no": "Kjør til høyre", "th": "ต้องเลี้ยวขวา", "en": "Turn right"},
     "desc": {"no": "Du er pålagt å svinge til høyre.", "th": "ต้องเลี้ยวขวา", "en": "You are required to turn right."}},
    {"num": "406", "type": "pabud",
     "name": {"no": "Kjør til venstre", "th": "ต้องเลี้ยวซ้าย", "en": "Turn left"},
     "desc": {"no": "Du er pålagt å svinge til venstre.", "th": "ต้องเลี้ยวซ้าย", "en": "You are required to turn left."}},
    {"num": "412", "type": "pabud",
     "name": {"no": "Rundkjøring", "th": "วงเวียน", "en": "Roundabout"},
     "desc": {"no": "Kjør i pilens retning i rundkjøringen. Trafikk i rundkjøringen har forkjørsrett.", "th": "ขับตามทิศทางลูกศรในวงเวียน รถในวงเวียนมีสิทธิ์ก่อน", "en": "Drive in the direction of the arrow in the roundabout. Traffic in the roundabout has priority."}},
    {"num": "416", "type": "pabud",
     "name": {"no": "Sykkelveg", "th": "ทางจักรยาน", "en": "Cycle path"},
     "desc": {"no": "Sykler og mopeder klasse M er påbudt å bruke denne vegen.", "th": "จักรยานและมอเตอร์ไซค์เล็กต้องใช้ทางนี้", "en": "Cyclists and class M mopeds must use this road."}},

    # ─── OPPLYSNINGSSKILT (Information — 5xx) ───────────────────────────────
    {"num": "502", "type": "opplysning",
     "name": {"no": "Motorveg", "th": "ทางด่วน", "en": "Motorway"},
     "desc": {"no": "Her begynner motorveg. Særlige regler gjelder for motorveg.", "th": "เริ่มต้นทางด่วน กฎพิเศษใช้บังคับ", "en": "Motorway begins here. Special rules apply on motorways."}},
    {"num": "504", "type": "opplysning",
     "name": {"no": "Slutt på motorveg", "th": "สิ้นสุดทางด่วน", "en": "End of motorway"},
     "desc": {"no": "Motorvegen slutter. Vanlige trafikkregler gjelder igjen.", "th": "สิ้นสุดทางด่วน กฎจราจรปกติใช้บังคับ", "en": "Motorway ends. Normal traffic rules apply again."}},
    {"num": "508", "type": "opplysning",
     "name": {"no": "Parkering", "th": "ที่จอดรถ", "en": "Parking"},
     "desc": {"no": "Parkering er tillatt. Eventuelle tilleggsskilter angir restriksjoner.", "th": "จอดรถได้ ป้ายเพิ่มเติมอาจระบุข้อจำกัด", "en": "Parking is permitted. Additional signs may indicate restrictions."}},
    {"num": "512", "type": "opplysning",
     "name": {"no": "Gangfelt", "th": "ทางข้ามสำหรับคนเดินเท้า", "en": "Pedestrian crossing"},
     "desc": {"no": "Fotgjengerfelt. Kjørende har vikeplikt for gående som er i feltet.", "th": "ทางม้าลาย รถต้องหยุดให้คนเดินเท้าที่อยู่ในทาง", "en": "Pedestrian crossing. Drivers must give way to pedestrians in the crossing."}},
    {"num": "514", "type": "opplysning",
     "name": {"no": "Envegskjøring", "th": "ทางเดียว", "en": "One way"},
     "desc": {"no": "Kjøring bare i pilens retning er tillatt.", "th": "ขับได้ทิศทางเดียวตามลูกศร", "en": "Traffic permitted in arrow direction only."}},
    {"num": "516", "type": "opplysning",
     "name": {"no": "Gangveg", "th": "ทางเดินเท้า", "en": "Footpath"},
     "desc": {"no": "Veg bestemt for gående. Kjøring forbudt.", "th": "ทางสำหรับคนเดินเท้าเท่านั้น ห้ามขับรถ", "en": "Path designated for pedestrians. Driving prohibited."}},
    {"num": "556", "type": "opplysning",
     "name": {"no": "Tunnel", "th": "อุโมงค์", "en": "Tunnel"},
     "desc": {"no": "Tunnel begynner. Slå på lys og hold avstand.", "th": "เริ่มต้นอุโมงค์ เปิดไฟและเพิ่มระยะห่าง", "en": "Tunnel begins. Turn on lights and maintain distance."}},
]

TYPE_META = {
    "fare":       {"no": "Fareskilt",       "th": "ป้ายเตือน",      "en": "Warning signs",     "color": "#F59E0B", "shape": "triangle"},
    "vikeplikt":  {"no": "Vikeplikt/Forkjørsrett", "th": "ป้ายสิทธิ์ผ่าน", "en": "Priority signs", "color": "#EF4444", "shape": "special"},
    "forbud":     {"no": "Forbudsskilt",    "th": "ป้ายห้าม",       "en": "Prohibition signs", "color": "#EF4444", "shape": "circle"},
    "pabud":      {"no": "Påbudsskilt",     "th": "ป้ายบังคับ",     "en": "Mandatory signs",   "color": "#3B82F6", "shape": "circle"},
    "opplysning": {"no": "Opplysningsskilt","th": "ป้ายข้อมูล",     "en": "Information signs", "color": "#10B981", "shape": "rect"},
}


def get_signs_grouped():
    grouped = {}
    for sign in SIGNS:
        t = sign["type"]
        if t not in grouped:
            grouped[t] = {"meta": TYPE_META[t], "signs": []}
        grouped[t]["signs"].append(sign)
    return grouped
