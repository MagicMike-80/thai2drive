"""
generate_signs_content.py
Generate multilingual sign content from built-in knowledge of the Norwegian
Skiltforskriften. Outputs signs_content.json for review + upload.

Run: python generate_signs_content.py
"""

import json

# Format: sign_id -> {name: {no,th,en}, explanation: {no,th,en}}
# Covers the most instructionally important signs precisely.
# Less critical signs (dir/supplementary/marking) get group-level defaults.

SIGN_DATA = {

    # ── Group 1: Vikepliktskilt ──────────────────────────────────────────────
    "202_0": {
        "name": {"no": "Vikeplikt", "th": "ให้ทาง", "en": "Give Way"},
        "explanation": {"no": "Du skal vike for trafikk i krysset.", "th": "คุณต้องหยุดรอและให้รถอื่นผ่านก่อน", "en": "You must yield to traffic at the intersection."}
    },
    "204_0": {
        "name": {"no": "Stopp", "th": "หยุด", "en": "Stop"},
        "explanation": {"no": "Stopp fullstendig og vike for all trafikk.", "th": "หยุดรถสนิทก่อนเสมอ แล้วให้รถอื่นผ่านก่อนจึงออกไป", "en": "Come to a complete stop and yield to all traffic."}
    },
    "206_0": {
        "name": {"no": "Jernbanekryssing uten bom", "th": "ทางรถไฟไม่มีไม้กั้น", "en": "Level Crossing Without Barrier"},
        "explanation": {"no": "Stopp og se etter tog før du krysser sporet.", "th": "หยุดและมองหารถไฟก่อนข้ามทางรถไฟ ไม่มีไม้กั้น", "en": "Stop and look for trains before crossing the tracks."}
    },
    "208_0": {
        "name": {"no": "Forkjørsrett", "th": "ถนนสายหลัก (มีสิทธิ์ก่อน)", "en": "Priority Road"},
        "explanation": {"no": "Du har forkjørsrett og kjøretøy fra sideveiene skal vike for deg.", "th": "คุณมีสิทธิ์ขับผ่านก่อน รถจากถนนสายรองต้องหยุดให้คุณ", "en": "You have priority and vehicles from side roads must yield to you."}
    },
    "210_0": {
        "name": {"no": "Møtende kjøretøy har vikeplikt", "th": "รถสวนทางต้องให้ทาง", "en": "Oncoming Traffic Must Yield"},
        "explanation": {"no": "Møtende kjøretøy skal vike for deg på smal veg.", "th": "รถที่ขับมาสวนทางต้องหยุดรอและให้คุณผ่านก่อนบนถนนแคบ", "en": "Oncoming vehicles must yield to you on a narrow road."}
    },
    "212_0": {
        "name": {"no": "Vikeplikt oppheves", "th": "สิ้นสุดการให้สิทธิ์รถสวนทาง", "en": "End of Oncoming Priority"},
        "explanation": {"no": "Retten til forkjørsrett for møtende kjøretøy er avsluttet.", "th": "สิทธิ์ที่ให้กับรถสวนทางสิ้นสุดแล้ว", "en": "The rule giving you priority over oncoming vehicles ends here."}
    },
    "214_0": {
        "name": {"no": "Forkjørsrett opphører", "th": "สิ้นสุดถนนสายหลัก", "en": "End of Priority Road"},
        "explanation": {"no": "Forkjørsretten opphører. Du må nå vike for trafikk i kryss.", "th": "ถนนสายหลักสิ้นสุดแล้ว คุณต้องหยุดรอรถอื่นในทุกสี่แยก", "en": "Priority road ends. You must now yield to traffic at intersections."}
    },

    # ── Group 2: Fareskilt (Warning) ─────────────────────────────────────────
    "100_1": {
        "name": {"no": "Farlig sving til venstre", "th": "โค้งอันตรายทางซ้าย", "en": "Dangerous Left Bend"},
        "explanation": {"no": "Skarp sving til venstre. Reduser fart.", "th": "โค้งคมทางซ้ายอยู่ข้างหน้า ลดความเร็วลง", "en": "Sharp left bend ahead. Reduce your speed."}
    },
    "100_2": {
        "name": {"no": "Farlig sving til høyre", "th": "โค้งอันตรายทางขวา", "en": "Dangerous Right Bend"},
        "explanation": {"no": "Skarp sving til høyre. Reduser fart.", "th": "โค้งคมทางขวาอยู่ข้างหน้า ลดความเร็วลง", "en": "Sharp right bend ahead. Reduce your speed."}
    },
    "102_1": {
        "name": {"no": "Svinger, venstre først", "th": "ถนนคดเคี้ยว ซ้ายก่อน", "en": "Series of Bends, Left First"},
        "explanation": {"no": "Flere svinger fremover, første til venstre. Kjør forsiktig.", "th": "มีโค้งหลายโค้งอยู่ข้างหน้า โค้งแรกหักซ้าย ขับช้าๆ", "en": "Several bends ahead, first to the left. Drive carefully."}
    },
    "102_2": {
        "name": {"no": "Svinger, høyre først", "th": "ถนนคดเคี้ยว ขวาก่อน", "en": "Series of Bends, Right First"},
        "explanation": {"no": "Flere svinger fremover, første til høyre. Kjør forsiktig.", "th": "มีโค้งหลายโค้งอยู่ข้างหน้า โค้งแรกหักขวา ขับช้าๆ", "en": "Several bends ahead, first to the right. Drive carefully."}
    },
    "104_1": {
        "name": {"no": "Bratt stigning", "th": "ทางชันขึ้นเขา", "en": "Steep Uphill"},
        "explanation": {"no": "Bratt oppoverbakke. Vær klar for lavere fart og høyere gir.", "th": "ทางชันอยู่ข้างหน้า เตรียมพร้อมสำหรับการขับขึ้นเขา", "en": "Steep uphill ahead. Be prepared for slower speeds."}
    },
    "104_2": {
        "name": {"no": "Bratt nedkjøring", "th": "ทางชันลงเขา", "en": "Steep Downhill"},
        "explanation": {"no": "Bratt nedoverbakke. Bruk lavere gir og reduser fart.", "th": "ทางลาดชันลงข้างหน้า ใช้เกียร์ต่ำและลดความเร็ว", "en": "Steep downhill ahead. Use a lower gear and reduce speed."}
    },
    "106_1": {
        "name": {"no": "Vegarbeid", "th": "มีการก่อสร้างถนน", "en": "Road Works"},
        "explanation": {"no": "Vegarbeid pågår. Kjør sakte og vær oppmerksom på arbeidere.", "th": "มีงานก่อสร้างถนน ขับช้าๆ และระวังคนงาน", "en": "Road works ahead. Slow down and watch for workers."}
    },
    "106_2": {
        "name": {"no": "Vegarbeid", "th": "มีการก่อสร้างถนน", "en": "Road Works"},
        "explanation": {"no": "Vegarbeid pågår. Kjør sakte og følg anvisninger.", "th": "มีงานก่อสร้างถนน ขับช้าๆ และปฏิบัติตามสัญญาณ", "en": "Road works ahead. Slow down and follow instructions."}
    },
    "106_3": {
        "name": {"no": "Vegarbeid", "th": "มีการก่อสร้างถนน", "en": "Road Works"},
        "explanation": {"no": "Vegarbeid pågår. Reduser fart og vær forsiktig.", "th": "มีงานก่อสร้างถนน ลดความเร็วและระมัดระวัง", "en": "Road works ahead. Reduce speed and be cautious."}
    },
    "108_0": {
        "name": {"no": "Glatt vegbane", "th": "ถนนลื่น", "en": "Slippery Road"},
        "explanation": {"no": "Vegen kan være glatt. Reduser fart og hold avstand.", "th": "ถนนอาจลื่น ลดความเร็วและเพิ่มระยะห่างจากรถคันหน้า", "en": "Road may be slippery. Reduce speed and increase following distance."}
    },
    "109_0": {
        "name": {"no": "Løs grus", "th": "กรวดหลวม", "en": "Loose Gravel"},
        "explanation": {"no": "Løs grus på vegen. Reduser fart for å unngå steinsprut.", "th": "มีกรวดหลวมบนถนน ลดความเร็วเพื่อหลีกเลี่ยงหินกระเด็น", "en": "Loose gravel on road. Slow down to avoid stone chipping."}
    },
    "110_0": {
        "name": {"no": "Smal veg", "th": "ถนนแคบ", "en": "Narrow Road"},
        "explanation": {"no": "Vegen er smal fremover. Kjør forsiktig og gi plass til møtende.", "th": "ถนนแคบอยู่ข้างหน้า ขับช้าๆ และเปิดทางให้รถสวนมา", "en": "Narrow road ahead. Drive carefully and give way to oncoming traffic."}
    },
    "112_0": {
        "name": {"no": "Veg innsnevres", "th": "ถนนแคบลง", "en": "Road Narrows"},
        "explanation": {"no": "Vegen blir smalere. Reduser fart og hold til høyre.", "th": "ถนนจะแคบลง ลดความเร็วและชิดขวา", "en": "Road narrows ahead. Slow down and keep right."}
    },
    "114_1": {
        "name": {"no": "Ustabil vegkant høyre", "th": "ไหล่ทางขวาไม่มั่นคง", "en": "Unstable Right Road Edge"},
        "explanation": {"no": "Vegkanten til høyre er ustabil. Unngå å kjøre ut på kanten.", "th": "ไหล่ทางด้านขวาไม่มั่นคง หลีกเลี่ยงการขับลงไหล่ทาง", "en": "The right road edge is unstable. Avoid driving onto the shoulder."}
    },
    "114_2": {
        "name": {"no": "Ustabil vegkant venstre", "th": "ไหล่ทางซ้ายไม่มั่นคง", "en": "Unstable Left Road Edge"},
        "explanation": {"no": "Vegkanten til venstre er ustabil. Unngå å kjøre ut på kanten.", "th": "ไหล่ทางด้านซ้ายไม่มั่นคง หลีกเลี่ยงการขับลงไหล่ทาง", "en": "The left road edge is unstable. Avoid driving onto the shoulder."}
    },
    "116_0": {
        "name": {"no": "Fartshump", "th": "เนินชะลอความเร็ว", "en": "Speed Bump"},
        "explanation": {"no": "Fartshump fremover. Reduser farten betraktelig.", "th": "มีเนินชะลอความเร็วอยู่ข้างหน้า ลดความเร็วให้ช้าลงมาก", "en": "Speed bump ahead. Reduce speed significantly."}
    },
    "117_0": {
        "name": {"no": "Ujamn veg", "th": "ถนนขรุขระ", "en": "Uneven Road"},
        "explanation": {"no": "Ujamn vegbane fremover. Kjør sakte og hold godt i rattet.", "th": "ถนนขรุขระอยู่ข้างหน้า ขับช้าๆ และจับพวงมาลัยให้มั่น", "en": "Uneven road surface ahead. Slow down and hold the wheel firmly."}
    },
    "118_0": {
        "name": {"no": "Veg slutter", "th": "ถนนสิ้นสุด", "en": "Road Ends"},
        "explanation": {"no": "Vegen slutter fremover. Snu eller finn alternativ rute.", "th": "ถนนสิ้นสุดอยู่ข้างหน้า เตรียมกลับรถหรือหาเส้นทางอื่น", "en": "Road ends ahead. Turn around or find an alternative route."}
    },
    "120_0": {
        "name": {"no": "Kryss", "th": "ทางแยก", "en": "Junction Ahead"},
        "explanation": {"no": "Kryss fremover. Vær oppmerksom og reduser fart.", "th": "มีทางแยกอยู่ข้างหน้า ระวังและลดความเร็ว", "en": "Junction ahead. Be alert and reduce your speed."}
    },
    "122_0": {
        "name": {"no": "Rundkjøring", "th": "วงเวียนอยู่ข้างหน้า", "en": "Roundabout Ahead"},
        "explanation": {"no": "Rundkjøring fremover. Gi vikeplikt for trafikk i rundkjøringen.", "th": "มีวงเวียนอยู่ข้างหน้า ให้สิทธิ์รถที่อยู่ในวงเวียนก่อน", "en": "Roundabout ahead. Give way to traffic already in the roundabout."}
    },
    "124_0": {
        "name": {"no": "Jernbanekryssing med bom", "th": "ทางรถไฟมีไม้กั้น", "en": "Level Crossing With Barrier"},
        "explanation": {"no": "Jernbanekryssing med automatisk bom fremover. Stopp når bommen er nede.", "th": "ทางข้ามรถไฟที่มีไม้กั้นอัตโนมัติ หยุดเมื่อไม้กั้นลง", "en": "Level crossing with automatic barrier ahead. Stop when the barrier is down."}
    },
    "126_0": {
        "name": {"no": "Jernbanekryssing uten bom", "th": "ทางรถไฟไม่มีไม้กั้น", "en": "Level Crossing Without Barrier"},
        "explanation": {"no": "Jernbanekryssing uten bom. Stopp og se etter tog i begge retninger.", "th": "ทางข้ามรถไฟที่ไม่มีไม้กั้น หยุดและมองดูรถไฟจากทั้งสองด้าน", "en": "Level crossing without barrier. Stop and look both ways for trains."}
    },
    "132_0": {
        "name": {"no": "Gangfelt", "th": "ทางข้ามสำหรับคนเดินเท้า", "en": "Pedestrian Crossing"},
        "explanation": {"no": "Gangfelt fremover. Gi fotgjengere vikeplikt.", "th": "มีทางข้ามสำหรับคนเดินเท้าอยู่ข้างหน้า ให้คนเดินเท้าข้ามก่อน", "en": "Pedestrian crossing ahead. Give way to pedestrians."}
    },
    "134_0": {
        "name": {"no": "Barn", "th": "เด็กอาจวิ่งออกมา", "en": "Children"},
        "explanation": {"no": "Barn kan komme ut i vegen. Reduser fart og vær svært forsiktig.", "th": "เด็กอาจวิ่งออกมาบนถนน ลดความเร็วและระมัดระวังมากเป็นพิเศษ", "en": "Children may run onto the road. Slow down and be extra cautious."}
    },
    "135_0": {
        "name": {"no": "Sykkel", "th": "ระวังนักปั่นจักรยาน", "en": "Cyclists"},
        "explanation": {"no": "Syklister kan krysse eller kjøre på vegen. Vær forsiktig.", "th": "นักปั่นจักรยานอาจตัดหน้าหรือขับบนถนนนี้ ขับด้วยความระมัดระวัง", "en": "Cyclists may cross or use the road. Drive with extra care."}
    },
    "136_1": {
        "name": {"no": "Elg", "th": "ระวังกวางมูส", "en": "Moose"},
        "explanation": {"no": "Elg kan krysse vegen. Reduser fart og vær beredt til å bremse.", "th": "กวางมูสอาจวิ่งข้ามถนน ลดความเร็วและเตรียมพร้อมเบรก", "en": "Moose may cross the road. Slow down and be ready to brake."}
    },
    "136_2": {
        "name": {"no": "Hjort", "th": "ระวังกวาง", "en": "Deer"},
        "explanation": {"no": "Hjort kan krysse vegen. Reduser fart og vær forsiktig.", "th": "กวางอาจวิ่งข้ามถนน ลดความเร็วและระมัดระวัง", "en": "Deer may cross the road. Slow down and drive carefully."}
    },
    "136_3": {
        "name": {"no": "Husdyr", "th": "ระวังสัตว์เลี้ยง", "en": "Domestic Animals"},
        "explanation": {"no": "Husdyr kan befinne seg på vegen. Kjør sakte og varsamt.", "th": "สัตว์เลี้ยงอาจอยู่บนถนน ขับช้าๆ ด้วยความระมัดระวัง", "en": "Domestic animals may be on the road. Drive slowly and carefully."}
    },
    "138_1": {
        "name": {"no": "Steinsprang høyre", "th": "ระวังหินร่วงจากขวา", "en": "Falling Rocks from Right"},
        "explanation": {"no": "Stein kan falle fra høyre side. Vær forsiktig og hold god avstand.", "th": "หินอาจร่วงลงมาจากด้านขวา ขับระมัดระวังและรักษาระยะห่าง", "en": "Rocks may fall from the right side. Be careful and keep your distance."}
    },
    "138_2": {
        "name": {"no": "Steinsprang venstre", "th": "ระวังหินร่วงจากซ้าย", "en": "Falling Rocks from Left"},
        "explanation": {"no": "Stein kan falle fra venstre side. Vær forsiktig og hold god avstand.", "th": "หินอาจร่วงลงมาจากด้านซ้าย ขับระมัดระวังและรักษาระยะห่าง", "en": "Rocks may fall from the left side. Be careful and keep your distance."}
    },
    "139_0": {
        "name": {"no": "Flom", "th": "ระวังน้ำท่วม", "en": "Flooding"},
        "explanation": {"no": "Fare for flom på vegen. Kjør sakte og vurder om vegen er trygg.", "th": "อาจมีน้ำท่วมบนถนน ขับช้าๆ และประเมินความปลอดภัยก่อน", "en": "Risk of flooding on the road. Drive slowly and assess if it's safe."}
    },
    "140_0": {
        "name": {"no": "Sidevind", "th": "ระวังลมข้าง", "en": "Cross Wind"},
        "explanation": {"no": "Fare for sterk sidevind. Hold godt i rattet og reduser fart.", "th": "อาจมีลมแรงพัดด้านข้าง จับพวงมาลัยให้มั่นและลดความเร็ว", "en": "Risk of strong crosswind. Hold the wheel firmly and reduce speed."}
    },
    "142_0": {
        "name": {"no": "Nedsatt frihøyde", "th": "ความสูงจำกัด", "en": "Low Clearance"},
        "explanation": {"no": "Begrenset høyde fremover. Sjekk om kjøretøyet ditt er lavt nok.", "th": "มีความสูงจำกัดอยู่ข้างหน้า ตรวจสอบว่ารถของคุณเตี้ยพอ", "en": "Limited height ahead. Check that your vehicle is low enough to pass."}
    },
    "144_0": {
        "name": {"no": "Bevegelig bro", "th": "สะพานที่เปิด-ปิดได้", "en": "Movable Bridge"},
        "explanation": {"no": "Bevegelig bro fremover. Stopp om broen er åpen.", "th": "มีสะพานที่เปิด-ปิดได้อยู่ข้างหน้า หยุดหากสะพานเปิดอยู่", "en": "Movable bridge ahead. Stop if the bridge is open."}
    },
    "146_1": {
        "name": {"no": "Trafikklys", "th": "สัญญาณไฟจราจร", "en": "Traffic Signals"},
        "explanation": {"no": "Trafikklys fremover. Vær klar til å stoppe for rødt.", "th": "มีสัญญาณไฟจราจรอยู่ข้างหน้า เตรียมพร้อมหยุดเมื่อไฟแดง", "en": "Traffic signals ahead. Be ready to stop for a red light."}
    },
    "146_2": {
        "name": {"no": "Trafikklys", "th": "สัญญาณไฟจราจร", "en": "Traffic Signals"},
        "explanation": {"no": "Trafikklys fremover. Vær klar til å stoppe for rødt.", "th": "มีสัญญาณไฟจราจรอยู่ข้างหน้า เตรียมพร้อมหยุดเมื่อไฟแดง", "en": "Traffic signals ahead. Be ready to stop for a red light."}
    },
    "146_3": {
        "name": {"no": "Trafikklys", "th": "สัญญาณไฟจราจร", "en": "Traffic Signals"},
        "explanation": {"no": "Trafikklys fremover. Vær klar til å stoppe for rødt.", "th": "มีสัญญาณไฟจราจรอยู่ข้างหน้า เตรียมพร้อมหยุดเมื่อไฟแดง", "en": "Traffic signals ahead. Be ready to stop for a red light."}
    },
    "146_4": {
        "name": {"no": "Trafikklys", "th": "สัญญาณไฟจราจร", "en": "Traffic Signals"},
        "explanation": {"no": "Trafikklys fremover. Vær klar til å stoppe for rødt.", "th": "มีสัญญาณไฟจราจรอยู่ข้างหน้า เตรียมพร้อมหยุดเมื่อไฟแดง", "en": "Traffic signals ahead. Be ready to stop for a red light."}
    },
    "146_5": {
        "name": {"no": "Trafikklys", "th": "สัญญาณไฟจราจร", "en": "Traffic Signals"},
        "explanation": {"no": "Trafikklys fremover. Vær klar til å stoppe for rødt.", "th": "มีสัญญาณไฟจราจรอยู่ข้างหน้า เตรียมพร้อมหยุดเมื่อไฟแดง", "en": "Traffic signals ahead. Be ready to stop for a red light."}
    },
    "148_0": {
        "name": {"no": "Farlig sidegate", "th": "ทางแยกอันตราย", "en": "Dangerous Side Road"},
        "explanation": {"no": "Farlig sidegate. Vær oppmerksom på kjøretøy som kjører inn.", "th": "มีทางแยกอันตราย ระวังรถที่อาจออกมาจากด้านข้าง", "en": "Dangerous side road. Watch for vehicles entering from the side."}
    },
    "149_0": {
        "name": {"no": "Skoleveg", "th": "เขตโรงเรียน", "en": "School Zone"},
        "explanation": {"no": "Skoleveg. Reduser fart og vær svært forsiktig.", "th": "เขตโรงเรียน ลดความเร็วและระมัดระวังเป็นพิเศษ", "en": "School zone. Reduce speed and be especially careful."}
    },
    "150_0": {
        "name": {"no": "Lavtflygende fly", "th": "เครื่องบินบินต่ำ", "en": "Low-Flying Aircraft"},
        "explanation": {"no": "Lavtflygende fly i området. Ikke forveksle lys med trafikklys.", "th": "มีเครื่องบินบินต่ำในบริเวณนี้ อย่าสับสนแสงเครื่องบินกับสัญญาณจราจร", "en": "Low-flying aircraft in the area. Do not confuse aircraft lights with traffic signals."}
    },
    "151": {
        "name": {"no": "Annen fare", "th": "อันตรายอื่นๆ", "en": "Other Hazard"},
        "explanation": {"no": "Uventet fare fremover. Vær ekstra oppmerksom.", "th": "มีอันตรายที่ไม่คาดคิดอยู่ข้างหน้า ขับด้วยความระมัดระวังเป็นพิเศษ", "en": "Unexpected hazard ahead. Be extra alert."}
    },
    "152_0": {
        "name": {"no": "Slak stigning", "th": "ทางลาดชัน", "en": "Gradient"},
        "explanation": {"no": "Stigning i vegen fremover. Tilpass farten.", "th": "มีทางลาดชันอยู่ข้างหน้า ปรับความเร็วให้เหมาะสม", "en": "Gradient ahead. Adjust your speed accordingly."}
    },
    "153": {
        "name": {"no": "Kø", "th": "รถติด", "en": "Queue"},
        "explanation": {"no": "Kø fremover. Reduser fart og hold avstand.", "th": "มีรถติดอยู่ข้างหน้า ลดความเร็วและรักษาระยะห่าง", "en": "Queue ahead. Reduce speed and keep your distance."}
    },
    "154_0": {
        "name": {"no": "Tunnel", "th": "อุโมงค์", "en": "Tunnel"},
        "explanation": {"no": "Tunnel fremover. Slå på lyset og hold avstand til forankjørende.", "th": "มีอุโมงค์อยู่ข้างหน้า เปิดไฟและรักษาระยะห่างจากรถคันหน้า", "en": "Tunnel ahead. Turn on your lights and keep a safe following distance."}
    },
    "155_0": {
        "name": {"no": "Bro", "th": "สะพาน", "en": "Bridge"},
        "explanation": {"no": "Bro fremover. Vær forsiktig, særlig i glatt vær.", "th": "มีสะพานอยู่ข้างหน้า ระมัดระวัง โดยเฉพาะในสภาพอากาศที่ลื่น", "en": "Bridge ahead. Take care, especially in icy or wet conditions."}
    },
    "156_0": {
        "name": {"no": "Kai eller elvekant", "th": "ท่าเรือหรือริมแม่น้ำ", "en": "Quay or Riverbank"},
        "explanation": {"no": "Vegen er nær en kai eller elvekant. Vær forsiktig.", "th": "ถนนอยู่ใกล้ท่าเรือหรือริมแม่น้ำ ขับระมัดระวัง", "en": "Road is near a quay or riverbank. Drive with care."}
    },

    # ── Group 3: Forbudtskilt (Prohibition) ──────────────────────────────────
    "302_0": {
        "name": {"no": "Innkjøring forbudt", "th": "ห้ามเข้า", "en": "No Entry"},
        "explanation": {"no": "Du har ikke lov til å kjøre inn her.", "th": "ห้ามขับรถเข้าไปในทิศทางนี้", "en": "You are not allowed to drive in this direction."}
    },
    "306_0": {
        "name": {"no": "Forbudt for alle kjøretøy", "th": "ห้ามยานพาหนะทุกชนิด", "en": "No Vehicles"},
        "explanation": {"no": "Ingen kjøretøy har lov til å kjøre her.", "th": "ยานพาหนะทุกชนิดไม่สามารถขับผ่านได้", "en": "No vehicles are permitted to drive here."}
    },
    "306_1": {
        "name": {"no": "Forbudt for motorkjøretøy", "th": "ห้ามรถยนต์", "en": "No Motor Vehicles"},
        "explanation": {"no": "Motorkjøretøy har ikke adgang her.", "th": "รถยนต์และรถจักรยานยนต์ไม่ได้รับอนุญาตให้ผ่าน", "en": "Motor vehicles are not permitted here."}
    },
    "306_3": {
        "name": {"no": "Forbudt for lastebil", "th": "ห้ามรถบรรทุก", "en": "No Heavy Vehicles"},
        "explanation": {"no": "Lastebiler og tunge kjøretøy har ikke adgang.", "th": "รถบรรทุกและยานพาหนะหนักไม่ได้รับอนุญาต", "en": "Trucks and heavy vehicles are not permitted here."}
    },
    "306_4": {
        "name": {"no": "Forbudt for buss", "th": "ห้ามรถบัส", "en": "No Buses"},
        "explanation": {"no": "Busser har ikke adgang her.", "th": "รถบัสไม่ได้รับอนุญาตให้ผ่าน", "en": "Buses are not permitted here."}
    },
    "306_5": {
        "name": {"no": "Forbudt for motorsykkel", "th": "ห้ามรถจักรยานยนต์", "en": "No Motorcycles"},
        "explanation": {"no": "Motorsykler har ikke adgang her.", "th": "รถจักรยานยนต์ไม่ได้รับอนุญาตให้ผ่าน", "en": "Motorcycles are not permitted here."}
    },
    "306_6": {
        "name": {"no": "Forbudt for moped", "th": "ห้ามมอเตอร์ไซค์เล็ก", "en": "No Mopeds"},
        "explanation": {"no": "Mopeder har ikke adgang her.", "th": "มอเปดและรถจักรยานยนต์ขนาดเล็กไม่ได้รับอนุญาต", "en": "Mopeds are not permitted here."}
    },
    "306_7": {
        "name": {"no": "Forbudt for sykkel", "th": "ห้ามจักรยาน", "en": "No Bicycles"},
        "explanation": {"no": "Sykler har ikke adgang her.", "th": "จักรยานไม่ได้รับอนุญาตให้ผ่าน", "en": "Bicycles are not permitted here."}
    },
    "306_8": {
        "name": {"no": "Forbudt for gående", "th": "ห้ามคนเดินเท้า", "en": "No Pedestrians"},
        "explanation": {"no": "Gående har ikke adgang her.", "th": "คนเดินเท้าไม่ได้รับอนุญาตให้ผ่าน", "en": "Pedestrians are not permitted here."}
    },
    "306_9": {
        "name": {"no": "Forbudt for ridende", "th": "ห้ามขี่ม้า", "en": "No Horse Riders"},
        "explanation": {"no": "Ridning er forbudt her.", "th": "ห้ามขี่ม้าในบริเวณนี้", "en": "Horse riding is not permitted here."}
    },
    "306_10": {
        "name": {"no": "Forbudt for hest og vogn", "th": "ห้ามรถม้า", "en": "No Horse-Drawn Vehicles"},
        "explanation": {"no": "Hest og vogn har ikke adgang her.", "th": "รถม้าและสัตว์ลากจูงไม่ได้รับอนุญาตให้ผ่าน", "en": "Horse-drawn vehicles are not permitted here."}
    },
    "308_0": {
        "name": {"no": "Forbudt for kjøretøy over lengden", "th": "ห้ามรถที่ยาวเกินกำหนด", "en": "No Vehicles Exceeding Length"},
        "explanation": {"no": "Forbudt for kjøretøy lengre enn det som er angitt.", "th": "ห้ามรถที่มีความยาวเกินกว่าที่ระบุไว้ผ่าน", "en": "Vehicles exceeding the specified length are not permitted."}
    },
    "310_0": {
        "name": {"no": "Forbudt for kjøretøy over høyden", "th": "ห้ามรถที่สูงเกินกำหนด", "en": "No Vehicles Exceeding Height"},
        "explanation": {"no": "Forbudt for kjøretøy høyere enn det som er angitt.", "th": "ห้ามรถที่มีความสูงเกินกว่าที่ระบุไว้ผ่าน", "en": "Vehicles exceeding the specified height are not permitted."}
    },
    "312_0": {
        "name": {"no": "Vegbom", "th": "ถนนปิด", "en": "Road Closed"},
        "explanation": {"no": "Veien er stengt for gjennomkjøring.", "th": "ถนนปิดสำหรับการสัญจร", "en": "The road is closed to through traffic."}
    },
    "314_0": {
        "name": {"no": "Forbikjøring forbudt", "th": "ห้ามแซง", "en": "No Overtaking"},
        "explanation": {"no": "Du har ikke lov til å kjøre forbi andre kjøretøy.", "th": "ห้ามแซงรถคันอื่น", "en": "You are not allowed to overtake other vehicles."}
    },
    "316_0": {
        "name": {"no": "Forbikjøring forbudt for lastebil", "th": "ห้ามรถบรรทุกแซง", "en": "No Overtaking for Trucks"},
        "explanation": {"no": "Lastebiler har ikke lov til å kjøre forbi andre kjøretøy.", "th": "ห้ามรถบรรทุกแซงยานพาหนะอื่น", "en": "Trucks are not allowed to overtake other vehicles."}
    },
    "318_1": {
        "name": {"no": "Stopp forbudt", "th": "ห้ามหยุดรถ", "en": "No Stopping"},
        "explanation": {"no": "Stopp er ikke tillatt her, verken for parkering eller av- og påstigning.", "th": "ห้ามหยุดรถในบริเวณนี้ ไม่ว่าจะจอดหรือรับส่งผู้โดยสาร", "en": "Stopping is not allowed here, not even briefly."}
    },
    "318_2": {
        "name": {"no": "Stopp forbudt", "th": "ห้ามหยุดรถ", "en": "No Stopping"},
        "explanation": {"no": "Stopp er ikke tillatt her.", "th": "ห้ามหยุดรถในบริเวณนี้", "en": "Stopping is not allowed here."}
    },
    "320_0": {
        "name": {"no": "Parkering forbudt", "th": "ห้ามจอดรถ", "en": "No Parking"},
        "explanation": {"no": "Parkering er forbudt her. Du kan stoppe kort for av- og påstigning.", "th": "ห้ามจอดรถในบริเวณนี้ สามารถหยุดสั้นๆ เพื่อรับส่งได้", "en": "Parking is forbidden here. You may stop briefly to drop off or pick up."}
    },
    "322_0": {
        "name": {"no": "All stans forbudt", "th": "ห้ามหยุดและจอดรถทุกกรณี", "en": "No Stopping or Parking"},
        "explanation": {"no": "Verken stopp eller parkering er tillatt her.", "th": "ห้ามหยุดหรือจอดรถในบริเวณนี้ทุกกรณี", "en": "Neither stopping nor parking is allowed here."}
    },
    "324_1": {
        "name": {"no": "Parkering forbudt på oddetallsdager", "th": "ห้ามจอดวันคี่", "en": "No Parking on Odd Days"},
        "explanation": {"no": "Parkering er forbudt på oddetallsdager i måneden.", "th": "ห้ามจอดรถในวันที่เป็นเลขคี่ของเดือน", "en": "Parking is forbidden on odd-numbered days of the month."}
    },
    "324_2": {
        "name": {"no": "Parkering forbudt på partallsdager", "th": "ห้ามจอดวันคู่", "en": "No Parking on Even Days"},
        "explanation": {"no": "Parkering er forbudt på partallsdager i måneden.", "th": "ห้ามจอดรถในวันที่เป็นเลขคู่ของเดือน", "en": "Parking is forbidden on even-numbered days of the month."}
    },
    "326_0": {
        "name": {"no": "Innkjøring forbudt for kjøretøy med farlig gods", "th": "ห้ามรถบรรทุกสารอันตราย", "en": "No Vehicles with Dangerous Goods"},
        "explanation": {"no": "Kjøretøy med farlig gods har ikke adgang.", "th": "รถบรรทุกสารอันตรายไม่ได้รับอนุญาตให้เข้า", "en": "Vehicles carrying dangerous goods are not permitted."}
    },
    "330_1": {
        "name": {"no": "Slutt på særskilt fartsgrense", "th": "สิ้นสุดความเร็วพิเศษ", "en": "End of Special Speed Limit"},
        "explanation": {"no": "Den spesielle fartsgrensen opphører. Vanlig fartsgrense gjelder igjen.", "th": "ความเร็วพิเศษสิ้นสุดแล้ว ให้ใช้ความเร็วปกติตามกฎหมาย", "en": "The special speed limit ends. Normal speed limit applies again."}
    },
    "330_2": {
        "name": {"no": "Slutt på særskilt fartsgrense", "th": "สิ้นสุดความเร็วพิเศษ", "en": "End of Special Speed Limit"},
        "explanation": {"no": "Den spesielle fartsgrensen opphører.", "th": "ความเร็วพิเศษสิ้นสุดแล้ว", "en": "The special speed limit ends here."}
    },
    "332_0": {
        "name": {"no": "Slutt på fartsgrense", "th": "สิ้นสุดเขตจำกัดความเร็ว", "en": "End of Speed Limit"},
        "explanation": {"no": "Fartsgrensesonen opphører. Vanlig fartsgrense gjelder.", "th": "เขตจำกัดความเร็วสิ้นสุดแล้ว ความเร็วตามกฎหมายทั่วไปมีผล", "en": "Speed limit zone ends. Standard speed limit applies."}
    },
    "334_0": {
        "name": {"no": "Slutt på forbikjøringsforbud", "th": "สิ้นสุดห้ามแซง", "en": "End of No Overtaking"},
        "explanation": {"no": "Forbudet mot forbikjøring er opphevet.", "th": "การห้ามแซงสิ้นสุดแล้ว คุณสามารถแซงได้อีกครั้ง", "en": "The no overtaking restriction ends here."}
    },
    "335_0": {
        "name": {"no": "Slutt på alle forbud", "th": "สิ้นสุดข้อห้ามทั้งหมด", "en": "End of All Prohibitions"},
        "explanation": {"no": "Alle forbud oppheves her.", "th": "ข้อห้ามทั้งหมดสิ้นสุดที่นี่", "en": "All previous prohibitions end here."}
    },
    "336_0": {
        "name": {"no": "Tidsbegrenset parkering", "th": "จอดได้ตามเวลาที่กำหนด", "en": "Time-Limited Parking"},
        "explanation": {"no": "Parkering er tillatt men begrenset til den angitte tiden.", "th": "สามารถจอดได้ แต่จำกัดเวลาตามที่ระบุ", "en": "Parking is allowed but limited to the specified time."}
    },
    "337_0": {
        "name": {"no": "Forbudt svingebevegelse", "th": "ห้ามเลี้ยว", "en": "Prohibited Turn"},
        "explanation": {"no": "Angitt svingebevegelse er forbudt i krysset.", "th": "ห้ามเลี้ยวตามทิศทางที่แสดงในสี่แยกนี้", "en": "The indicated turn is prohibited at this junction."}
    },

    # Speed limits
    "362_30":  {"name": {"no": "Fartsgrense 30 km/t",  "th": "จำกัดความเร็ว 30 กม./ชม.",  "en": "Speed Limit 30 km/h"},  "explanation": {"no": "Maksimal tillatt hastighet er 30 km/t.",  "th": "ห้ามขับเร็วเกิน 30 กิโลเมตรต่อชั่วโมง",  "en": "Maximum speed allowed is 30 km/h."}},
    "362_40":  {"name": {"no": "Fartsgrense 40 km/t",  "th": "จำกัดความเร็ว 40 กม./ชม.",  "en": "Speed Limit 40 km/h"},  "explanation": {"no": "Maksimal tillatt hastighet er 40 km/t.",  "th": "ห้ามขับเร็วเกิน 40 กิโลเมตรต่อชั่วโมง",  "en": "Maximum speed allowed is 40 km/h."}},
    "362_50":  {"name": {"no": "Fartsgrense 50 km/t",  "th": "จำกัดความเร็ว 50 กม./ชม.",  "en": "Speed Limit 50 km/h"},  "explanation": {"no": "Maksimal tillatt hastighet er 50 km/t.",  "th": "ห้ามขับเร็วเกิน 50 กิโลเมตรต่อชั่วโมง",  "en": "Maximum speed allowed is 50 km/h."}},
    "362_60":  {"name": {"no": "Fartsgrense 60 km/t",  "th": "จำกัดความเร็ว 60 กม./ชม.",  "en": "Speed Limit 60 km/h"},  "explanation": {"no": "Maksimal tillatt hastighet er 60 km/t.",  "th": "ห้ามขับเร็วเกิน 60 กิโลเมตรต่อชั่วโมง",  "en": "Maximum speed allowed is 60 km/h."}},
    "362_70":  {"name": {"no": "Fartsgrense 70 km/t",  "th": "จำกัดความเร็ว 70 กม./ชม.",  "en": "Speed Limit 70 km/h"},  "explanation": {"no": "Maksimal tillatt hastighet er 70 km/t.",  "th": "ห้ามขับเร็วเกิน 70 กิโลเมตรต่อชั่วโมง",  "en": "Maximum speed allowed is 70 km/h."}},
    "362_80":  {"name": {"no": "Fartsgrense 80 km/t",  "th": "จำกัดความเร็ว 80 กม./ชม.",  "en": "Speed Limit 80 km/h"},  "explanation": {"no": "Maksimal tillatt hastighet er 80 km/t.",  "th": "ห้ามขับเร็วเกิน 80 กิโลเมตรต่อชั่วโมง",  "en": "Maximum speed allowed is 80 km/h."}},
    "362_90":  {"name": {"no": "Fartsgrense 90 km/t",  "th": "จำกัดความเร็ว 90 กม./ชม.",  "en": "Speed Limit 90 km/h"},  "explanation": {"no": "Maksimal tillatt hastighet er 90 km/t.",  "th": "ห้ามขับเร็วเกิน 90 กิโลเมตรต่อชั่วโมง",  "en": "Maximum speed allowed is 90 km/h."}},
    "362_100": {"name": {"no": "Fartsgrense 100 km/t", "th": "จำกัดความเร็ว 100 กม./ชม.", "en": "Speed Limit 100 km/h"}, "explanation": {"no": "Maksimal tillatt hastighet er 100 km/t.", "th": "ห้ามขับเร็วเกิน 100 กิโลเมตรต่อชั่วโมง", "en": "Maximum speed allowed is 100 km/h."}},
    "362_110": {"name": {"no": "Fartsgrense 110 km/t", "th": "จำกัดความเร็ว 110 กม./ชม.", "en": "Speed Limit 110 km/h"}, "explanation": {"no": "Maksimal tillatt hastighet er 110 km/t.", "th": "ห้ามขับเร็วเกิน 110 กิโลเมตรต่อชั่วโมง", "en": "Maximum speed allowed is 110 km/h."}},

    # Minimum speeds
    "364_30": {"name": {"no": "Minstehastighet 30 km/t",  "th": "ความเร็วขั้นต่ำ 30 กม./ชม.",  "en": "Minimum Speed 30 km/h"},  "explanation": {"no": "Du må kjøre minst 30 km/t her.",  "th": "คุณต้องขับด้วยความเร็วอย่างน้อย 30 กิโลเมตรต่อชั่วโมง",  "en": "You must drive at least 30 km/h here."}},
    "364_40": {"name": {"no": "Minstehastighet 40 km/t",  "th": "ความเร็วขั้นต่ำ 40 กม./ชม.",  "en": "Minimum Speed 40 km/h"},  "explanation": {"no": "Du må kjøre minst 40 km/t her.",  "th": "คุณต้องขับด้วยความเร็วอย่างน้อย 40 กิโลเมตรต่อชั่วโมง",  "en": "You must drive at least 40 km/h here."}},
    "364_50": {"name": {"no": "Minstehastighet 50 km/t",  "th": "ความเร็วขั้นต่ำ 50 กม./ชม.",  "en": "Minimum Speed 50 km/h"},  "explanation": {"no": "Du må kjøre minst 50 km/t her.",  "th": "คุณต้องขับด้วยความเร็วอย่างน้อย 50 กิโลเมตรต่อชั่วโมง",  "en": "You must drive at least 50 km/h here."}},
    "364_60": {"name": {"no": "Minstehastighet 60 km/t",  "th": "ความเร็วขั้นต่ำ 60 กม./ชม.",  "en": "Minimum Speed 60 km/h"},  "explanation": {"no": "Du må kjøre minst 60 km/t her.",  "th": "คุณต้องขับด้วยความเร็วอย่างน้อย 60 กิโลเมตรต่อชั่วโมง",  "en": "You must drive at least 60 km/h here."}},
    "364_70": {"name": {"no": "Minstehastighet 70 km/t",  "th": "ความเร็วขั้นต่ำ 70 กม./ชม.",  "en": "Minimum Speed 70 km/h"},  "explanation": {"no": "Du må kjøre minst 70 km/t her.",  "th": "คุณต้องขับด้วยความเร็วอย่างน้อย 70 กิโลเมตรต่อชั่วโมง",  "en": "You must drive at least 70 km/h here."}},

    "366_0": {
        "name": {"no": "Slutt på minstehastighet", "th": "สิ้นสุดความเร็วขั้นต่ำ", "en": "End of Minimum Speed"},
        "explanation": {"no": "Kravet om minstehastighet er opphevet.", "th": "ข้อกำหนดความเร็วขั้นต่ำสิ้นสุดแล้ว", "en": "The minimum speed requirement ends here."}
    },
    "367": {
        "name": {"no": "Forbudt å bruke horn", "th": "ห้ามบีบแตร", "en": "No Horn"},
        "explanation": {"no": "Det er forbudt å bruke horn her.", "th": "ห้ามบีบแตรในบริเวณนี้", "en": "Use of horn is prohibited here."}
    },
    "368_0": {
        "name": {"no": "Forbudt å bruke lys", "th": "ห้ามใช้ไฟสูง", "en": "No High Beams"},
        "explanation": {"no": "Bruk av fjernlys er forbudt her.", "th": "ห้ามใช้ไฟสูงในบริเวณนี้", "en": "Use of high beam lights is prohibited here."}
    },
    "369": {
        "name": {"no": "Forbudt for farlig gods", "th": "ห้ามขนส่งสินค้าอันตราย", "en": "No Dangerous Goods"},
        "explanation": {"no": "Transport av farlig gods er forbudt her.", "th": "การขนส่งสินค้าอันตรายถูกห้ามในบริเวณนี้", "en": "Transport of dangerous goods is prohibited here."}
    },
    "370_0": {
        "name": {"no": "Møteforbud", "th": "ห้ามสวนทางกัน", "en": "No Meeting"},
        "explanation": {"no": "Møtende trafikk er ikke tillatt. Vent til veien er klar.", "th": "ห้ามรถสวนทางกันในบริเวณนี้ รอให้ถนนโล่งก่อน", "en": "Oncoming traffic is not permitted here. Wait for the road to clear."}
    },
    "372_0": {
        "name": {"no": "Forbudt å kaste søppel", "th": "ห้ามทิ้งขยะ", "en": "No Littering"},
        "explanation": {"no": "Søppelkasting er forbudt i dette området.", "th": "ห้ามทิ้งขยะในบริเวณนี้", "en": "Littering is prohibited in this area."}
    },
    "376_1": {
        "name": {"no": "Forbudt å parkere kjøretøy med tilhenger", "th": "ห้ามจอดรถพ่วง", "en": "No Parking with Trailer"},
        "explanation": {"no": "Kjøretøy med tilhenger har ikke lov til å parkere her.", "th": "ห้ามจอดรถที่มีพ่วงในบริเวณนี้", "en": "Vehicles with trailers are not allowed to park here."}
    },
    "376_2": {
        "name": {"no": "Forbudt å parkere kjøretøy med tilhenger", "th": "ห้ามจอดรถพ่วง", "en": "No Parking with Trailer"},
        "explanation": {"no": "Kjøretøy med tilhenger har ikke lov til å parkere her.", "th": "ห้ามจอดรถที่มีพ่วงในบริเวณนี้", "en": "Vehicles with trailers are not allowed to park here."}
    },
    "376_2a": {
        "name": {"no": "Forbudt å parkere kjøretøy med tilhenger", "th": "ห้ามจอดรถพ่วง", "en": "No Parking with Trailer"},
        "explanation": {"no": "Parkering med tilhenger er forbudt.", "th": "ห้ามจอดรถที่มีพ่วงในบริเวณนี้", "en": "Parking with a trailer is forbidden here."}
    },
    "377": {
        "name": {"no": "Forbudt å kjøre med last", "th": "ห้ามบรรทุก", "en": "No Load Carrying"},
        "explanation": {"no": "Kjøretøy med last er forbudt her.", "th": "ห้ามรถบรรทุกสินค้าในบริเวณนี้", "en": "Vehicles carrying loads are not permitted here."}
    },
    "378_1": {
        "name": {"no": "Forbudt å snu", "th": "ห้ามกลับรถ", "en": "No U-Turn"},
        "explanation": {"no": "Det er forbudt å snu kjøretøyet her.", "th": "ห้ามกลับรถในบริเวณนี้", "en": "U-turns are not allowed here."}
    },
    "378_2": {
        "name": {"no": "Forbudt å svinge", "th": "ห้ามเลี้ยว", "en": "No Turn"},
        "explanation": {"no": "Angitt svingning er forbudt i dette krysset.", "th": "ห้ามเลี้ยวตามทิศทางที่กำหนดในสี่แยกนี้", "en": "The indicated turn is prohibited at this junction."}
    },
    "379": {
        "name": {"no": "Forbudt å stanse for trafikklys", "th": "ห้ามจอดรอไฟแดง", "en": "No Stopping at Signals"},
        "explanation": {"no": "Du skal ikke stoppe for trafikklys her.", "th": "ห้ามหยุดรอสัญญาณไฟในบริเวณนี้", "en": "You should not stop at traffic lights in this area."}
    },
    "380": {
        "name": {"no": "Forbudt sone", "th": "เขตห้าม", "en": "Forbidden Zone"},
        "explanation": {"no": "Kjøring er forbudt i denne sonen.", "th": "ห้ามขับรถในเขตนี้", "en": "Driving is prohibited in this zone."}
    },
    "382": {
        "name": {"no": "Slutt på forbudt sone", "th": "สิ้นสุดเขตห้าม", "en": "End of Forbidden Zone"},
        "explanation": {"no": "Den forbudte sonen er over.", "th": "เขตห้ามสิ้นสุดที่นี่", "en": "The forbidden zone ends here."}
    },

    # ── Group 4: Påbudsskilt (Mandatory) ─────────────────────────────────────
    "402_1": {
        "name": {"no": "Påbudt kjøreretning rett frem", "th": "บังคับตรงไป", "en": "Mandatory Straight Ahead"},
        "explanation": {"no": "Du må kjøre rett frem.", "th": "คุณต้องขับตรงไปเท่านั้น", "en": "You must drive straight ahead."}
    },
    "402_2": {
        "name": {"no": "Påbudt kjøreretning til høyre", "th": "บังคับเลี้ยวขวา", "en": "Mandatory Right Turn"},
        "explanation": {"no": "Du må svinge til høyre.", "th": "คุณต้องเลี้ยวขวาเท่านั้น", "en": "You must turn right."}
    },
    "402_3": {
        "name": {"no": "Påbudt kjøreretning til venstre", "th": "บังคับเลี้ยวซ้าย", "en": "Mandatory Left Turn"},
        "explanation": {"no": "Du må svinge til venstre.", "th": "คุณต้องเลี้ยวซ้ายเท่านั้น", "en": "You must turn left."}
    },
    "402_4": {
        "name": {"no": "Påbudt rett frem eller til høyre", "th": "บังคับตรงหรือขวา", "en": "Mandatory Straight or Right"},
        "explanation": {"no": "Du må kjøre rett frem eller svinge til høyre.", "th": "คุณต้องขับตรงหรือเลี้ยวขวาเท่านั้น", "en": "You must go straight or turn right."}
    },
    "402_5": {
        "name": {"no": "Påbudt rett frem eller til venstre", "th": "บังคับตรงหรือซ้าย", "en": "Mandatory Straight or Left"},
        "explanation": {"no": "Du må kjøre rett frem eller svinge til venstre.", "th": "คุณต้องขับตรงหรือเลี้ยวซ้ายเท่านั้น", "en": "You must go straight or turn left."}
    },
    "402_6": {
        "name": {"no": "Påbudt til høyre eller til venstre", "th": "บังคับเลี้ยวขวาหรือซ้าย", "en": "Mandatory Right or Left"},
        "explanation": {"no": "Du må svinge enten til høyre eller til venstre.", "th": "คุณต้องเลี้ยวขวาหรือซ้าย ไม่สามารถตรงไปได้", "en": "You must turn right or left, not go straight."}
    },
    "402_7": {
        "name": {"no": "Påbudt å holde til høyre", "th": "บังคับชิดขวา", "en": "Keep Right"},
        "explanation": {"no": "Du skal holde til høyre for hinderet.", "th": "คุณต้องขับชิดขวาของสิ่งกีดขวาง", "en": "You must pass to the right of the obstacle."}
    },
    "402_8": {
        "name": {"no": "Påbudt å holde til venstre", "th": "บังคับชิดซ้าย", "en": "Keep Left"},
        "explanation": {"no": "Du skal holde til venstre for hinderet.", "th": "คุณต้องขับชิดซ้ายของสิ่งกีดขวาง", "en": "You must pass to the left of the obstacle."}
    },
    "404_1": {
        "name": {"no": "Påbudt kjøreretning i rundkjøring", "th": "บังคับทิศทางในวงเวียน", "en": "Mandatory Roundabout Direction"},
        "explanation": {"no": "Kjør i pilens retning i rundkjøringen.", "th": "ขับตามทิศทางลูกศรในวงเวียน", "en": "Drive in the direction shown in the roundabout."}
    },
    "404_2": {
        "name": {"no": "Påbudt kjøreretning i rundkjøring", "th": "บังคับทิศทางในวงเวียน", "en": "Mandatory Roundabout Direction"},
        "explanation": {"no": "Kjør i pilens retning i rundkjøringen.", "th": "ขับตามทิศทางลูกศรในวงเวียน", "en": "Drive in the direction shown in the roundabout."}
    },
    "406_0": {
        "name": {"no": "Påbudt sykkelfelt", "th": "บังคับใช้ช่องจักรยาน", "en": "Mandatory Cycle Lane"},
        "explanation": {"no": "Syklister skal bruke sykkelfelt.", "th": "นักปั่นจักรยานต้องใช้ช่องจักรยานนี้", "en": "Cyclists must use the marked cycle lane."}
    },
    "408": {
        "name": {"no": "Påbudt å bruke kjetting", "th": "บังคับใส่โซ่ล้อ", "en": "Snow Chains Required"},
        "explanation": {"no": "Det er påbudt å bruke kjetting på kjøretøyet her.", "th": "บังคับให้ใส่โซ่ล้อรถในบริเวณนี้", "en": "Snow chains must be fitted to your vehicle here."}
    },

    # ── Group 5: Opplysningsskilt (Information) ───────────────────────────────
    "502_0": {
        "name": {"no": "Motorveg", "th": "ทางมอเตอร์เวย์", "en": "Motorway"},
        "explanation": {"no": "Her begynner motorvegen. Egne regler gjelder.", "th": "ทางมอเตอร์เวย์เริ่มต้นที่นี่ มีกฎพิเศษที่ต้องปฏิบัติตาม", "en": "Motorway begins here. Special rules apply."}
    },
    "503_0": {
        "name": {"no": "Slutt på motorveg", "th": "สิ้นสุดมอเตอร์เวย์", "en": "End of Motorway"},
        "explanation": {"no": "Motorvegen slutter her. Vanlige regler gjelder igjen.", "th": "มอเตอร์เวย์สิ้นสุดที่นี่ กฎปกติมีผลบังคับใช้อีกครั้ง", "en": "Motorway ends here. Normal traffic rules apply again."}
    },
    "504_0": {
        "name": {"no": "Motortrafikkveg", "th": "ถนนสำหรับยานยนต์", "en": "Expressway"},
        "explanation": {"no": "Her begynner motortrafikkvegen. Kun motorkjøretøy tillatt.", "th": "ถนนสำหรับยานยนต์เริ่มต้นที่นี่ อนุญาตเฉพาะยานยนต์เท่านั้น", "en": "Expressway begins. Motor vehicles only are permitted."}
    },
    "505_0": {
        "name": {"no": "Slutt på motortrafikkveg", "th": "สิ้นสุดถนนสำหรับยานยนต์", "en": "End of Expressway"},
        "explanation": {"no": "Motortrafikkvegen slutter her.", "th": "ถนนสำหรับยานยนต์สิ้นสุดที่นี่", "en": "Expressway ends here."}
    },
    "506": {
        "name": {"no": "Tettsted", "th": "เขตชุมชน", "en": "Built-Up Area"},
        "explanation": {"no": "Du kjører inn i et tettsted. Fartsgrense 50 km/t gjelder om ikke annet er skiltet.", "th": "คุณกำลังเข้าสู่เขตชุมชน ความเร็วสูงสุด 50 กม./ชม. หากไม่มีป้ายอื่น", "en": "Entering a built-up area. Speed limit is 50 km/h unless otherwise signed."}
    },
    "507": {
        "name": {"no": "Slutt på tettsted", "th": "สิ้นสุดเขตชุมชน", "en": "End of Built-Up Area"},
        "explanation": {"no": "Tettstedet er over. Ny fartsgrense gjelder.", "th": "สิ้นสุดเขตชุมชน ความเร็วที่กำหนดใหม่มีผล", "en": "Built-up area ends. New speed limit applies."}
    },
    "508_1": {
        "name": {"no": "Tunnel", "th": "อุโมงค์", "en": "Tunnel"},
        "explanation": {"no": "Tunnel fremover. Slå på lyset.", "th": "อุโมงค์อยู่ข้างหน้า เปิดไฟรถ", "en": "Tunnel ahead. Turn on your lights."}
    },
    "508_2": {
        "name": {"no": "Slutt på tunnel", "th": "สิ้นสุดอุโมงค์", "en": "End of Tunnel"},
        "explanation": {"no": "Tunnelen slutter. Du kjører ut i dagslys.", "th": "อุโมงค์สิ้นสุดแล้ว คุณจะออกสู่แสงธรรมชาติ", "en": "Tunnel ends. You are emerging into daylight."}
    },
    "509_0": {
        "name": {"no": "Gangveg", "th": "ทางเดินเท้า", "en": "Pedestrian Path"},
        "explanation": {"no": "Kun for gående. Kjøretøy er ikke tillatt.", "th": "สำหรับคนเดินเท้าเท่านั้น ยานพาหนะไม่ได้รับอนุญาต", "en": "For pedestrians only. Vehicles are not permitted."}
    },
    "510_1": {
        "name": {"no": "Sykkelveg", "th": "ทางจักรยาน", "en": "Cycle Path"},
        "explanation": {"no": "Kun for syklister. Andre kjøretøy er ikke tillatt.", "th": "สำหรับนักปั่นจักรยานเท่านั้น ยานพาหนะอื่นไม่ได้รับอนุญาต", "en": "For cyclists only. Other vehicles are not permitted."}
    },
    "510_2": {
        "name": {"no": "Slutt på sykkelveg", "th": "สิ้นสุดทางจักรยาน", "en": "End of Cycle Path"},
        "explanation": {"no": "Sykkelvegen slutter her.", "th": "ทางจักรยานสิ้นสุดที่นี่", "en": "The cycle path ends here."}
    },
    "511_0": {
        "name": {"no": "Gang- og sykkelveg", "th": "ทางรวมสำหรับคนเดินและจักรยาน", "en": "Combined Pedestrian and Cycle Path"},
        "explanation": {"no": "Delt veg for gående og syklister. Vis hensyn.", "th": "ทางร่วมสำหรับคนเดินเท้าและจักรยาน ขับด้วยความระมัดระวัง", "en": "Shared path for pedestrians and cyclists. Show consideration."}
    },
    "512_0": {
        "name": {"no": "Parkering", "th": "ที่จอดรถ", "en": "Parking"},
        "explanation": {"no": "Parkering er tillatt her.", "th": "สามารถจอดรถได้ในบริเวณนี้", "en": "Parking is allowed here."}
    },
    "513_0": {
        "name": {"no": "Envegskjøring", "th": "ถนนทางเดียว", "en": "One-Way Road"},
        "explanation": {"no": "Vegen er envegskjørt. Kjør kun i pilens retning.", "th": "ถนนทางเดียว ขับตามทิศทางลูกศรเท่านั้น", "en": "One-way road. Drive in the direction of the arrow only."}
    },
    "514_0": {
        "name": {"no": "Motorvegkryss", "th": "ทางแยกมอเตอร์เวย์", "en": "Motorway Junction"},
        "explanation": {"no": "Motorvegkryss fremover. Forbered deg på avkjøring.", "th": "ทางแยกมอเตอร์เวย์อยู่ข้างหน้า เตรียมพร้อมสำหรับการออก", "en": "Motorway junction ahead. Prepare for your exit."}
    },
    "516_H": {
        "name": {"no": "Avkjøring høyre", "th": "ทางออกขวา", "en": "Exit Right"},
        "explanation": {"no": "Avkjøring til høyre fremover.", "th": "ทางออกอยู่ด้านขวา", "en": "Exit to the right ahead."}
    },
    "516_V": {
        "name": {"no": "Avkjøring venstre", "th": "ทางออกซ้าย", "en": "Exit Left"},
        "explanation": {"no": "Avkjøring til venstre fremover.", "th": "ทางออกอยู่ด้านซ้าย", "en": "Exit to the left ahead."}
    },
    "518_0": {
        "name": {"no": "Rasteplass", "th": "ที่พักริมทาง", "en": "Rest Area"},
        "explanation": {"no": "Rasteplass tilgjengelig. Du kan stoppe og hvile her.", "th": "มีที่พักริมทาง คุณสามารถหยุดพักได้ที่นี่", "en": "Rest area available. You may stop and rest here."}
    },
    "520_0": {
        "name": {"no": "Bensinstasjon", "th": "ปั๊มน้ำมัน", "en": "Fuel Station"},
        "explanation": {"no": "Bensinstasjon tilgjengelig.", "th": "มีปั๊มน้ำมันอยู่ใกล้ๆ", "en": "Fuel station available nearby."}
    },
    "521.1": {
        "name": {"no": "Førstehjelp", "th": "ปฐมพยาบาล", "en": "First Aid"},
        "explanation": {"no": "Førstehjelp er tilgjengelig her.", "th": "มีบริการปฐมพยาบาลที่นี่", "en": "First aid is available here."}
    },
    "521_0": {
        "name": {"no": "Sykehus", "th": "โรงพยาบาล", "en": "Hospital"},
        "explanation": {"no": "Sykehus i nærheten.", "th": "มีโรงพยาบาลอยู่ใกล้ๆ", "en": "Hospital nearby."}
    },
    "522_0": {
        "name": {"no": "Ferge", "th": "เรือข้ามฟาก", "en": "Ferry"},
        "explanation": {"no": "Fergekai i nærheten.", "th": "มีท่าเรือข้ามฟากอยู่ใกล้ๆ", "en": "Ferry terminal nearby."}
    },
    "524_0": {
        "name": {"no": "Flyplass", "th": "สนามบิน", "en": "Airport"},
        "explanation": {"no": "Flyplass i nærheten.", "th": "มีสนามบินอยู่ใกล้ๆ", "en": "Airport nearby."}
    },
    "526_1": {
        "name": {"no": "Kjørefelt", "th": "ช่องทางเดินรถ", "en": "Lane Indicator"},
        "explanation": {"no": "Angir kjørefelt og kjøreretning.", "th": "แสดงช่องทางและทิศทางการขับขี่", "en": "Indicates lane and driving direction."}
    },
    "526_2": {
        "name": {"no": "Kjørefelt", "th": "ช่องทางเดินรถ", "en": "Lane Indicator"},
        "explanation": {"no": "Angir kjørefelt og kjøreretning.", "th": "แสดงช่องทางและทิศทางการขับขี่", "en": "Indicates lane and driving direction."}
    },
    "527_1": {"name": {"no": "Kjørefeltpil", "th": "ลูกศรช่องทาง", "en": "Lane Arrow"}, "explanation": {"no": "Pilen viser tillatt kjøreretning i dette feltet.", "th": "ลูกศรแสดงทิศทางที่อนุญาตในช่องทางนี้", "en": "Arrow shows the permitted direction for this lane."}},
    "527_2": {"name": {"no": "Kjørefeltpil", "th": "ลูกศรช่องทาง", "en": "Lane Arrow"}, "explanation": {"no": "Pilen viser tillatt kjøreretning i dette feltet.", "th": "ลูกศรแสดงทิศทางที่อนุญาตในช่องทางนี้", "en": "Arrow shows the permitted direction for this lane."}},
    "527_3": {"name": {"no": "Kjørefeltpil", "th": "ลูกศรช่องทาง", "en": "Lane Arrow"}, "explanation": {"no": "Pilen viser tillatt kjøreretning i dette feltet.", "th": "ลูกศรแสดงทิศทางที่อนุญาตในช่องทางนี้", "en": "Arrow shows the permitted direction for this lane."}},
    "527_4": {"name": {"no": "Kjørefeltpil", "th": "ลูกศรช่องทาง", "en": "Lane Arrow"}, "explanation": {"no": "Pilen viser tillatt kjøreretning i dette feltet.", "th": "ลูกศรแสดงทิศทางที่อนุญาตในช่องทางนี้", "en": "Arrow shows the permitted direction for this lane."}},
    "528_0": {
        "name": {"no": "Kjørefelt slutter", "th": "ช่องทางสิ้นสุด", "en": "Lane Ends"},
        "explanation": {"no": "Kjørefeltet slutter. Flett deg inn i neste felt.", "th": "ช่องทางสิ้นสุด รวมเข้าช่องทางถัดไปอย่างนุ่มนวล", "en": "This lane ends. Merge smoothly into the next lane."}
    },
    "530_01": {"name": {"no": "Avstandsskilt", "th": "ป้ายระยะทาง", "en": "Distance Sign"}, "explanation": {"no": "Viser avstand til destinasjon.", "th": "แสดงระยะทางไปยังจุดหมาย", "en": "Shows distance to destination."}},
    "530_11": {"name": {"no": "Avstandsskilt", "th": "ป้ายระยะทาง", "en": "Distance Sign"}, "explanation": {"no": "Viser avstand til destinasjon.", "th": "แสดงระยะทางไปยังจุดหมาย", "en": "Shows distance to destination."}},
    "531_102": {"name": {"no": "Vegviserskilt", "th": "ป้ายบอกทาง", "en": "Directional Sign"}, "explanation": {"no": "Viser vei til angitt destinasjon.", "th": "บอกทิศทางไปยังจุดหมายที่ระบุ", "en": "Shows the way to the indicated destination."}},
    "531_202": {"name": {"no": "Vegviserskilt", "th": "ป้ายบอกทาง", "en": "Directional Sign"}, "explanation": {"no": "Viser vei til angitt destinasjon.", "th": "บอกทิศทางไปยังจุดหมายที่ระบุ", "en": "Shows the way to the indicated destination."}},
    "532_H02": {"name": {"no": "Avkjøringsskilt høyre", "th": "ป้ายทางออกขวา", "en": "Exit Sign Right"}, "explanation": {"no": "Angir avkjøring til høyre.", "th": "ระบุทางออกทางขวา", "en": "Indicates exit to the right."}},
    "534_H02": {"name": {"no": "Avkjøringsskilt", "th": "ป้ายทางออก", "en": "Exit Sign"}, "explanation": {"no": "Angir avkjøring fra motorvegen.", "th": "ระบุทางออกจากมอเตอร์เวย์", "en": "Indicates motorway exit."}},
    "536_101": {"name": {"no": "Forhåndsskilt", "th": "ป้ายแจ้งล่วงหน้า", "en": "Advance Sign"}, "explanation": {"no": "Forhåndsvarsler om kryss eller avkjøring.", "th": "แจ้งล่วงหน้าเกี่ยวกับทางแยกหรือทางออก", "en": "Advance notice of junction or exit ahead."}},
    "536_201": {"name": {"no": "Forhåndsskilt", "th": "ป้ายแจ้งล่วงหน้า", "en": "Advance Sign"}, "explanation": {"no": "Forhåndsvarsler om kryss eller avkjøring.", "th": "แจ้งล่วงหน้าเกี่ยวกับทางแยกหรือทางออก", "en": "Advance notice of junction or exit ahead."}},
    "538_12": {"name": {"no": "Vegtabell", "th": "ตารางเส้นทาง", "en": "Route Table"}, "explanation": {"no": "Viser destinasjoner og avstander.", "th": "แสดงจุดหมายปลายทางและระยะทาง", "en": "Shows destinations and distances."}},
    "539": {"name": {"no": "Vegviserskilt", "th": "ป้ายนำทาง", "en": "Route Sign"}, "explanation": {"no": "Viser vei til angitt sted.", "th": "บอกทิศทางไปยังสถานที่ที่ระบุ", "en": "Shows the way to the indicated place."}},
    "540_0": {"name": {"no": "Omkjøring", "th": "ทางอ้อม", "en": "Detour"}, "explanation": {"no": "Følg omvei på grunn av stengt veg.", "th": "ใช้เส้นทางอ้อมเนื่องจากถนนปิด", "en": "Follow the detour route due to road closure."}},
    "542_0": {"name": {"no": "Slutt på omkjøring", "th": "สิ้นสุดทางอ้อม", "en": "End of Detour"}, "explanation": {"no": "Omveien er ferdig. Du er tilbake på normal veg.", "th": "ทางอ้อมสิ้นสุดแล้ว คุณกลับสู่ถนนปกติ", "en": "Detour ends. You are back on the normal route."}},
    "548_0": {"name": {"no": "Samleveg", "th": "ถนนรวม", "en": "Collector Road"}, "explanation": {"no": "Du er på en samleveg som leder til motorveg.", "th": "คุณอยู่บนถนนรวมที่นำไปสู่มอเตอร์เวย์", "en": "You are on a collector road leading to the motorway."}},
    "550_0": {"name": {"no": "Nødstopp/beredskapslomme", "th": "ช่องจอดฉุกเฉิน", "en": "Emergency Bay"}, "explanation": {"no": "Nødstopplass for kjøretøy med problemer.", "th": "ช่องจอดสำหรับยานพาหนะที่เกิดปัญหา", "en": "Emergency stopping place for vehicles with problems."}},
    "552_0": {"name": {"no": "Tunnelnavn", "th": "ชื่ออุโมงค์", "en": "Tunnel Name"}, "explanation": {"no": "Angir navnet på tunnelen.", "th": "แสดงชื่ออุโมงค์", "en": "Indicates the name of the tunnel."}},
    "556.2": {"name": {"no": "Vegsperring", "th": "ถนนปิดกั้น", "en": "Road Barrier"}, "explanation": {"no": "Vegen er sperret. Kjør ikke videre.", "th": "ถนนถูกปิดกั้น ไม่สามารถขับต่อไปได้", "en": "Road is blocked. Do not proceed."}},
    "556_0": {"name": {"no": "Informasjonsskilt", "th": "ป้ายข้อมูล", "en": "Information Sign"}, "explanation": {"no": "Gir vegfarende nyttig informasjon.", "th": "ให้ข้อมูลที่เป็นประโยชน์แก่ผู้ขับขี่", "en": "Provides useful information to road users."}},
    "558_0": {"name": {"no": "Turistveg", "th": "เส้นทางท่องเที่ยว", "en": "Tourist Route"}, "explanation": {"no": "Nasjonal turistveg med naturopplevelser.", "th": "เส้นทางท่องเที่ยวแห่งชาติที่มีทัศนียภาพสวยงาม", "en": "National scenic tourist route."}},
    "560_2": {"name": {"no": "Miljøgate", "th": "ถนนสิ่งแวดล้อม", "en": "Environmental Zone"}, "explanation": {"no": "Miljøgate med lavere fart og hensyn til myke trafikanter.", "th": "ถนนสิ่งแวดล้อมที่ต้องลดความเร็วและระมัดระวังผู้ใช้ถนนที่อ่อนแอ", "en": "Environmental street with reduced speed and priority for vulnerable road users."}},
    "565": {"name": {"no": "Planovergang", "th": "ทางรถไฟตัดถนน", "en": "Level Crossing"}, "explanation": {"no": "Planovergang for jernbane fremover.", "th": "ทางรถไฟตัดถนนอยู่ข้างหน้า", "en": "Railway level crossing ahead."}},
    "570_1H": {"name": {"no": "Kjørefeltskift høyre", "th": "เปลี่ยนช่องทางขวา", "en": "Lane Change Right"}, "explanation": {"no": "Kjørefeltet flyttes mot høyre fremover.", "th": "ช่องทางจะย้ายไปทางขวาข้างหน้า", "en": "The lane shifts to the right ahead."}},
    "570_1V": {"name": {"no": "Kjørefeltskift venstre", "th": "เปลี่ยนช่องทางซ้าย", "en": "Lane Change Left"}, "explanation": {"no": "Kjørefeltet flyttes mot venstre fremover.", "th": "ช่องทางจะย้ายไปทางซ้ายข้างหน้า", "en": "The lane shifts to the left ahead."}},
    "570_2H": {"name": {"no": "Kjørefeltskift høyre", "th": "เปลี่ยนช่องทางขวา", "en": "Lane Change Right"}, "explanation": {"no": "Kjørefeltet flyttes mot høyre.", "th": "ช่องทางจะย้ายไปทางขวา", "en": "The lane shifts to the right."}},
    "570_2V": {"name": {"no": "Kjørefeltskift venstre", "th": "เปลี่ยนช่องทางซ้าย", "en": "Lane Change Left"}, "explanation": {"no": "Kjørefeltet flyttes mot venstre.", "th": "ช่องทางจะย้ายไปทางซ้าย", "en": "The lane shifts to the left."}},
}

# ── Groups 7, 8, 9: Direction / Supplementary / Road marking ─────────────────
# These are highly variant-specific. We generate reasonable content by category.

GROUP_DEFAULTS = {
    7: {
        "name_prefix": {"no": "Veivisningsskilt", "th": "ป้ายนำทาง", "en": "Direction sign"},
        "explanation":  {"no": "Viser vei til destinasjon eller interessepunkt.", "th": "บอกทิศทางไปยังจุดหมายหรือสถานที่สำคัญ", "en": "Shows the way to a destination or point of interest."}
    },
    8: {
        "name_prefix": {"no": "Underskilt", "th": "ป้ายเสริม", "en": "Supplementary sign"},
        "explanation":  {"no": "Gir tilleggsinformasjon til skiltet ovenfor.", "th": "ให้ข้อมูลเพิ่มเติมสำหรับป้ายด้านบน", "en": "Provides additional information for the sign above."}
    },
    9: {
        "name_prefix": {"no": "Markeringsskilt", "th": "ป้ายเครื่องหมาย", "en": "Road marking sign"},
        "explanation":  {"no": "Markerer vegkanten eller farlig område.", "th": "ทำเครื่องหมายขอบถนนหรือบริเวณอันตราย", "en": "Marks the road edge or a hazardous area."}
    },
}

# Specific overrides for known direction/supplementary signs
SPECIFIC_OVERRIDES = {
    # Common underskilt
    "802_0": {"name": {"no": "Avstandsskilt", "th": "ป้ายระยะทาง", "en": "Distance plate"}, "explanation": {"no": "Viser avstand til skiltet foran.", "th": "แสดงระยะทางถึงป้ายด้านหน้า", "en": "Shows distance to the sign ahead."}},
    "804_0": {"name": {"no": "Tidsrom", "th": "ป้ายช่วงเวลา", "en": "Time period plate"}, "explanation": {"no": "Angir tidsperiode da skiltet over gjelder.", "th": "ระบุช่วงเวลาที่ป้ายด้านบนมีผล", "en": "Indicates the time period when the sign above applies."}},
    "816_0": {"name": {"no": "Strekningsskilt", "th": "ป้ายระยะทาง", "en": "Route distance sign"}, "explanation": {"no": "Angir distansen der skiltet gjelder.", "th": "ระบุระยะทางที่ป้ายมีผลบังคับใช้", "en": "Indicates the distance over which the sign applies."}},
    "824_0": {"name": {"no": "Pilskilt", "th": "ป้ายลูกศร", "en": "Arrow supplement"}, "explanation": {"no": "Viser retning for skiltet ovenfor.", "th": "แสดงทิศทางของป้ายด้านบน", "en": "Shows direction for the sign above."}},
    "826_0": {"name": {"no": "Gjelder begge sider", "th": "ใช้ทั้งสองด้าน", "en": "Applies both sides"}, "explanation": {"no": "Skiltet ovenfor gjelder for begge sider av vegen.", "th": "ป้ายด้านบนใช้กับทั้งสองด้านของถนน", "en": "The sign above applies to both sides of the road."}},
    "831_0": {"name": {"no": "Beboerparkering", "th": "ที่จอดสำหรับผู้อยู่อาศัย", "en": "Residents parking"}, "explanation": {"no": "Parkering forbeholdt beboere med tillatt skilt.", "th": "ที่จอดรถสำหรับผู้อยู่อาศัยที่มีสิทธิ์เท่านั้น", "en": "Parking reserved for residents with a permit."}},
    "834_0": {"name": {"no": "El-bil parkering", "th": "ที่จอดรถยนต์ไฟฟ้า", "en": "Electric vehicle parking"}, "explanation": {"no": "Parkering forbeholdt elektriske kjøretøy.", "th": "ที่จอดรถสำหรับยานพาหนะไฟฟ้าเท่านั้น", "en": "Parking reserved for electric vehicles."}},

    # Markeringsskilt
    "902_0":   {"name": {"no": "Vegkantmarkering", "th": "เครื่องหมายขอบทาง", "en": "Road edge marker"}, "explanation": {"no": "Markerer vegkanten. Hvit = høyre side.", "th": "ทำเครื่องหมายขอบถนน สีขาว = ด้านขวา", "en": "Marks the road edge. White = right side."}},
    "902_0H":  {"name": {"no": "Vegkantmarkering høyre", "th": "เครื่องหมายขอบทางขวา", "en": "Right edge marker"}, "explanation": {"no": "Markerer vegkanten på høyre side.", "th": "ทำเครื่องหมายขอบถนนด้านขวา", "en": "Marks the right side road edge."}},
    "902_0V":  {"name": {"no": "Vegkantmarkering venstre", "th": "เครื่องหมายขอบทางซ้าย", "en": "Left edge marker"}, "explanation": {"no": "Markerer vegkanten på venstre side.", "th": "ทำเครื่องหมายขอบถนนด้านซ้าย", "en": "Marks the left side road edge."}},
    "904_0":   {"name": {"no": "Vegkantmarkering med refleks", "th": "เครื่องหมายขอบทางสะท้อนแสง", "en": "Reflective edge marker"}, "explanation": {"no": "Reflekterende vegkantmarkering.", "th": "เครื่องหมายขอบถนนที่สะท้อนแสง ช่วยในการมองเห็นตอนกลางคืน", "en": "Reflective road edge marker for night visibility."}},
    "904_0H":  {"name": {"no": "Vegkantmarkering høyre", "th": "เครื่องหมายขอบทางขวา", "en": "Right edge marker"}, "explanation": {"no": "Reflekterende markering på høyre side.", "th": "เครื่องหมายสะท้อนแสงด้านขวา", "en": "Reflective marker on the right side."}},
    "904_0V":  {"name": {"no": "Vegkantmarkering venstre", "th": "เครื่องหมายขอบทางซ้าย", "en": "Left edge marker"}, "explanation": {"no": "Reflekterende markering på venstre side.", "th": "เครื่องหมายสะท้อนแสงด้านซ้าย", "en": "Reflective marker on the left side."}},
    "906_0":   {"name": {"no": "Siktforsterker", "th": "ป้ายเพิ่มทัศนวิสัย", "en": "Visibility enhancer"}, "explanation": {"no": "Øker sikten i kurver og farlige punkter.", "th": "เพิ่มการมองเห็นในโค้งและจุดอันตราย", "en": "Improves visibility at bends and hazardous points."}},
    "906_0H":  {"name": {"no": "Siktforsterker høyre", "th": "ป้ายเพิ่มทัศนวิสัยขวา", "en": "Visibility enhancer right"}, "explanation": {"no": "Siktforsterker på høyre side.", "th": "ป้ายเพิ่มทัศนวิสัยด้านขวา", "en": "Visibility enhancer on the right."}},
    "906_0V":  {"name": {"no": "Siktforsterker venstre", "th": "ป้ายเพิ่มทัศนวิสัยซ้าย", "en": "Visibility enhancer left"}, "explanation": {"no": "Siktforsterker på venstre side.", "th": "ป้ายเพิ่มทัศนวิสัยด้านซ้าย", "en": "Visibility enhancer on the left."}},
    "906_0VH": {"name": {"no": "Siktforsterker begge sider", "th": "ป้ายเพิ่มทัศนวิสัยทั้งสองด้าน", "en": "Visibility enhancer both sides"}, "explanation": {"no": "Siktforsterker på begge sider.", "th": "ป้ายเพิ่มทัศนวิสัยทั้งสองด้าน", "en": "Visibility enhancer on both sides."}},
    "908_0": {"name": {"no": "Faremarker", "th": "เครื่องหมายอันตราย", "en": "Hazard marker"}, "explanation": {"no": "Markerer farlig hinder eller punkt.", "th": "ทำเครื่องหมายสิ่งกีดขวางหรือจุดอันตราย", "en": "Marks a dangerous obstacle or point."}},
    "912_0": {"name": {"no": "Midtrekkverk", "th": "ราวกั้นกลางถนน", "en": "Central barrier marker"}, "explanation": {"no": "Markerer midtrekkverk.", "th": "ทำเครื่องหมายราวกั้นกลางถนน", "en": "Marks the central road barrier."}},
    "914_H": {"name": {"no": "Sperremarkering høyre", "th": "เครื่องหมายกั้นขวา", "en": "Barrier marker right"}, "explanation": {"no": "Sperring til høyre.", "th": "เครื่องหมายกั้นด้านขวา", "en": "Barrier or obstacle to the right."}},
    "914_V": {"name": {"no": "Sperremarkering venstre", "th": "เครื่องหมายกั้นซ้าย", "en": "Barrier marker left"}, "explanation": {"no": "Sperring til venstre.", "th": "เครื่องหมายกั้นด้านซ้าย", "en": "Barrier or obstacle to the left."}},
    "916_0": {"name": {"no": "Kantstein/fortauskant", "th": "ขอบทางเท้า", "en": "Kerb marker"}, "explanation": {"no": "Markerer kantstein eller fortauskant.", "th": "ทำเครื่องหมายขอบทางเท้า", "en": "Marks the kerb or footpath edge."}},
    "920_H": {"name": {"no": "Pilmarkering høyre", "th": "ลูกศรชี้ขวา", "en": "Right arrow marker"}, "explanation": {"no": "Piler leder trafikk mot høyre.", "th": "ลูกศรนำทางการจราจรไปทางขวา", "en": "Arrows guide traffic to the right."}},
    "920_VE": {"name": {"no": "Pilmarkering venstre", "th": "ลูกศรชี้ซ้าย", "en": "Left arrow marker"}, "explanation": {"no": "Piler leder trafikk mot venstre.", "th": "ลูกศรนำทางการจราจรไปทางซ้าย", "en": "Arrows guide traffic to the left."}},
    "920_VM": {"name": {"no": "Pilmarkering midtre", "th": "ลูกศรกลาง", "en": "Centre arrow marker"}, "explanation": {"no": "Piler leder trafikk rett frem.", "th": "ลูกศรนำทางการจราจรตรงไป", "en": "Arrows guide traffic straight ahead."}},
    "930": {"name": {"no": "Kilometermarkering", "th": "หลักกิโลเมตร", "en": "Kilometre marker"}, "explanation": {"no": "Viser kilometerpunkt langs vegen.", "th": "แสดงจุดกิโลเมตรตามแนวถนน", "en": "Shows the kilometre point along the road."}},
    "940": {"name": {"no": "Vegmarkering", "th": "เครื่องหมายบนถนน", "en": "Road marking"}, "explanation": {"no": "Merking av vegbanen.", "th": "เครื่องหมายบนพื้นผิวถนน", "en": "Marking on the road surface."}},
    "942": {"name": {"no": "Senterlinjemarkering", "th": "เส้นกลางถนน", "en": "Centre line marker"}, "explanation": {"no": "Markerer midtlinjen på vegen.", "th": "ทำเครื่องหมายเส้นกลางถนน", "en": "Marks the centre line of the road."}},
}

SIGN_DATA.update(SPECIFIC_OVERRIDES)


def get_content(sign_id: str, group: int) -> dict:
    """Return content for a sign, falling back to group defaults."""
    if sign_id in SIGN_DATA:
        return SIGN_DATA[sign_id]
    # Group-level fallback
    d = GROUP_DEFAULTS.get(group)
    if d:
        return {
            "name": {lang: f"{d['name_prefix'][lang]} {sign_id}" for lang in ('no','th','en')},
            "explanation": d["explanation"]
        }
    # Last resort
    return {
        "name": {"no": sign_id, "th": sign_id, "en": sign_id},
        "explanation": {"no": "Trafikkskilt.", "th": "ป้ายจราจร", "en": "Traffic sign."}
    }


def main():
    from dotenv import dotenv_values
    from pathlib import Path
    import pymongo

    env = dotenv_values(Path(__file__).parent / '.env')
    db = pymongo.MongoClient(env['MONGO_URL'])[env['DB_NAME']]

    signs = list(db.traffic_signs.find({}, {'id': 1, 'group': 1, '_id': 0}))

    output = []
    for s in signs:
        sid = s['id']
        g   = s['group']
        c   = get_content(sid, g)
        output.append({"id": sid, "group": g, **c})

    out_path = Path(__file__).parent / 'signs_content.json'
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Written {len(output)} signs to {out_path}")

    # Quick coverage check
    covered = sum(1 for o in output if o['name']['no'] and not o['name']['no'].startswith(o['id']))
    print(f"Specifically named: {covered}/{len(output)}")
    fallback = [o['id'] for o in output if o['name']['no'].startswith(o['id']) or o['name']['no'] == o['id']]
    if fallback:
        print(f"Fallback (generic group name): {fallback}")


if __name__ == '__main__':
    main()
