"""Data-driven, web-only Thai2Drive Studybook chapter one."""
from __future__ import annotations

import json


def i18n(no: str, th: str, en: str) -> dict[str, str]:
    return {"no": no, "th": th, "en": en}


_PLACEHOLDERS = [
    ("intro", "1", "Førerplass på norsk byvei", "Introdusere aktiv observasjon", "førerperspektiv", "Uoversiktlig bybilde med kryssende myke trafikanter og biler", "biler, syklist og fotgjenger", "byvei", "gangfelt", "mulige hendelser foran", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("look_far", "2", "Nærblikk og fjernblikk", "Sammenligne synsfelt", "delt førerperspektiv", "For kort blikkfokus og bråstopp i kø foran", "bil foran", "landevei", "midtlinje", "riktig blikkavstand", "/api/assets/stopping-distance-road-v1.png", ""),
    ("hazards", "3", "Gate med fire risikokilder", "Trene fareoppdagelse", "førerperspektiv", "Fire samtidige faresignaler i gatemiljøet", "fotgjenger, syklist, bil og varebil", "bygate", "gangfelt og sidevei", "fire faresignaler", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("gaze", "4", "Rolig trafikksituasjon", "Vise fleksibel blikkflyt", "førerperspektiv", "Trafikk i blindsone, speil og kryssende kjøretøy", "trafikk foran og bak", "byvei", "feltlinjer", "blikkflyt", "/api/assets/stopping-distance-road-v1.png", ""),
    ("hidden", "5", "Varebil skjuler barn", "Tolke små faresignaler", "førerperspektiv", "Barn og leker skjult bak parkert varebil", "varebil, barn og ball", "boliggate", "vegkant", "ball og føtter", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("process", "6", "Barn nær gangfelt", "Koble observasjon til handling", "førerperspektiv", "Barn ved fortauskant som plutselig kan krysse gangfeltet", "barn og bil", "byvei", "gangfelt", "barn kan gå ut", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("wheels", "7", "Bil med hjul mot veien", "Tolke retning", "førerperspektiv", "Parkert bil med svingte forhjul klar til å svinge ut i veibanen", "parkert bil", "bygate", "vegkant", "dreide forhjul", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", ""),
    ("predict", "8", "Buss blinker ut", "Forutse neste hendelse", "førerperspektiv", "Buss ved holdeplass som aktiverer venstre blinklys og vil ut", "buss og bil", "byvei", "holdeplass", "bussen kan kjøre", "/api/assets/thumbs/thumb_vikeplikt_7_5a_buss.jpg", ""),
    ("too_close", "9", "Bil følger for tett", "Knytte avstand til tid", "førerperspektiv", "For kort avstand til forankjørende bil ved bråstopp", "to biler", "landevei", "midtlinje", "liten tidsmargin", "/api/assets/stopping-distance-road-v1.png", "split"),
    ("split", "10", "To ulike avstander", "Sammenligne margin", "delt førerperspektiv", "Farlig kort følgeavstand sammenlignet med 3-sekunders sikkerhetsavstand", "to bilpar", "landevei", "midtlinje", "god avstand", "/api/assets/stopping-distance-road-v1.png", "too_close"),
    ("speed", "11", "Fare ved to hastigheter", "Vise fartens virkning", "delt sideprofil", "Høyere hastighet som dobler bremselengden og spiser opp reaksjonstiden", "bil og fare", "landevei", "fartsmerking", "tidlig observasjon", "/api/assets/stopping-distance-road-v1.png", "margin"),
    ("margin", "12", "Sikkerhetsrom rundt bil", "Forklare sikkerhetsmargin", "fugleperspektiv", "Manglende buffersone og sikkerhetsrom rundt kjøretøyet i tett trafikk", "bil, syklist og trafikk", "byvei", "feltlinjer", "rom rundt bilen", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "speed"),
]

ASSETS = {
    key: {"asset_id": f"CH01-BLIKK-{int(page):03d}", "page": page, "scene": scene,
          "pedagogical_purpose": purpose, "camera_angle": camera,
          "risk_source": risk, "risikokilde": risk,
          "vehicles_road_users": actors, "road_type": road,
          "signs_markings": markings, "learner_discovery": discovery,
          "hotspots": [], "pair_asset": pair_key, "status": "placeholder", "src": src,
          "alt": i18n("Illustrasjon av trafikksituasjon", "ภาพประกอบสถานการณ์จราจร", "Traffic situation illustration")}
    for key, page, scene, purpose, camera, risk, actors, road, markings, discovery, src, pair_key in _PLACEHOLDERS
}
ASSETS["hazards"]["hotspots"] = [{"x": 23, "y": 55}, {"x": 45, "y": 45}, {"x": 70, "y": 43}, {"x": 84, "y": 60}]
ASSETS["hidden"]["hotspots"] = [{"x": 64, "y": 62}]


def opt(key: str, no: str, th: str, en: str) -> dict:
    return {"id": key, "label": i18n(no, th, en)}


def info(key: str, kind: str, asset_key: str, no: str, th: str, en: str, body: tuple[str, str, str], **extra) -> dict:
    return {"id": key, "type": kind, "asset": asset_key, "eyebrow": i18n("LÆR", "เรียนรู้", "LEARN"),
            "title": i18n(no, th, en), "body": i18n(*body), **extra}


def question(label: tuple[str, str, str], prompt: tuple[str, str, str], answers: list[dict], correct: str, explanation: tuple[str, str, str]) -> dict:
    return {"label": i18n(*label), "prompt": i18n(*prompt), "options": answers,
            "correct": correct, "explanation": i18n(*explanation)}


LESSONS = [
    info("intro", "intro", "intro", "👀 BLIKKET", "👀 การมอง", "👀 VISION", ("En god sjåfør prøver å oppdage hva som kan skje om noen sekunder.", "ผู้ขับขี่ที่ดีพยายามสังเกตว่าอีกไม่กี่วินาทีอาจเกิดอะไรขึ้น", "A good driver tries to notice what may happen in the next few seconds.")),
    info("look-far", "choice", "look_far", "Se langt frem", "มองไปข้างหน้าให้ไกล", "Look far ahead", ("Hvor får du best tid til å oppdage endringer?", "คุณมองแบบใดจึงมีเวลาสังเกตการเปลี่ยนแปลงได้ดีที่สุด?", "Which view gives most time to notice change?"), options=[opt("near", "Rett foran panseret", "ตรงหน้าฝากระโปรง", "Over the bonnet"), opt("far", "Langt frem", "มองไกลไปข้างหน้า", "Far ahead")], correct="far", correctFeedback=i18n("Tidlig oppdagelse gir mer tid.", "การสังเกตได้เร็วทำให้มีเวลามากขึ้น", "Early discovery gives more time."), wrongFeedback=i18n("Løft blikket og se lenger frem.", "เงยสายตาและมองให้ไกลขึ้น", "Lift your eyes and look farther ahead.")),
    info("spot-four", "spotHazard", "hazards", "Hva bør du allerede ha oppdaget?", "คุณควรสังเกตเห็นอะไรแล้ว?", "What should you have noticed?", ("Finn fire steder der situasjonen kan endre seg.", "หาสี่จุดที่สถานการณ์อาจเปลี่ยนได้", "Find four places where the situation may change."), hazards=[{"x": x, "y": y, "label": i18n(n, t, e)} for x, y, n, t, e in [(23,55,"Fotgjenger","คนเดินเท้า","Pedestrian"),(45,45,"Syklist","คนขี่จักรยาน","Cyclist"),(70,43,"Sidevei","ทางแยกด้านข้าง","Side road"),(84,60,"Skjult område","พื้นที่ถูกบัง","Hidden area")]], feedback=i18n("Godt sett. Finn alle fire.", "มองเห็นได้ดี ค้นหาให้ครบทั้งสี่จุด", "Good observation. Find all four."), completeFeedback=i18n("Du fant alle fire.", "คุณพบครบทั้งสี่จุดแล้ว", "You found all four.")),
    info("move-eyes", "sequence", "gaze", "Beveg blikket", "ขยับสายตา", "Move your eyes", ("Situasjonen bestemmer hvor oppmerksomheten må være.", "สถานการณ์เป็นตัวกำหนดว่าคุณควรให้ความสนใจที่ไหน", "The situation decides where attention is needed."), steps=[i18n("LANGT FREM","ไกลไปข้างหน้า","FAR AHEAD"),i18n("SIDER","ด้านข้าง","SIDES"),i18n("SPEIL","กระจก","MIRRORS"),i18n("HELHET","ภาพรวม","WHOLE SCENE")]),
    info("hidden-danger", "spotHazard", "hidden", "Den skjulte faren", "อันตรายที่ซ่อนอยู่", "The hidden hazard", ("Trykk på detaljen som varsler at noen kan være skjult.", "แตะรายละเอียดที่บอกว่าอาจมีใครถูกบังอยู่", "Select the clue that warns someone may be hidden."), hazards=[{"x":64,"y":62,"label":i18n("Liten ledetråd","เบาะแสเล็ก ๆ","Small clue")}], feedback=i18n("Du trenger ikke se hele faren for å forstå at den kan være der.", "คุณไม่จำเป็นต้องเห็นอันตรายทั้งหมดเพื่อเข้าใจว่าอาจมีอันตรายอยู่", "You need not see the whole hazard to know it may be there."), completeFeedback=i18n("Du tolket tegnet.", "คุณตีความสัญญาณได้", "You read the clue.")),
    {"id":"road-check-1","type":"roadCheck","eyebrow":i18n("ROAD CHECK 1 ⚡","ROAD CHECK 1 ⚡","ROAD CHECK 1 ⚡"),"title":i18n("Se før det skjer","มองให้เห็นก่อนเกิดเหตุ","See it before it happens"),"body":i18n("Tre korte situasjoner.","สามสถานการณ์สั้น ๆ","Three short situations."),"questions":[
        question(("OPPMERKSOMHET","จุดสนใจ","ATTENTION"),("Hvor bør du se?","คุณควรมองที่ไหน?","Where should you look?"),[opt("far","Langt frem","ไกลไปข้างหน้า","Far ahead"),opt("near","Bare nær bilen","เฉพาะใกล้รถ","Only near the car")],"far",("Bygg oversikt tidlig.","สร้างภาพรวมตั้งแต่เนิ่น ๆ","Build an overview early.")),
        question(("SKJULT RISIKO","ความเสี่ยงที่ซ่อนอยู่","HIDDEN RISK"),("Hva kan varebilen skjule?","รถตู้อาจบังอะไร?","What may the van hide?"),[opt("person","En person","คน","A person"),opt("none","Ingenting","ไม่มีอะไร","Nothing")],"person",("Små tegn kan varsle stor endring.","สัญญาณเล็ก ๆ อาจเตือนถึงการเปลี่ยนแปลงครั้งใหญ่","Small clues can warn of big change.")),
        question(("FORVENT","คาดการณ์","EXPECT"),("Hva kan skje ved gangfeltet?","อาจเกิดอะไรที่ทางม้าลาย?","What may happen at the crossing?"),[opt("cross","Noen går ut","อาจมีคนเดินออกมา","Someone steps out"),opt("same","Ingenting endres","ไม่มีอะไรเปลี่ยน","Nothing changes")],"cross",("Forvent endring før du må reagere.","คาดการณ์ก่อนที่คุณต้องตอบสนอง","Expect change before reacting."))]},
    info("see-understand-act", "sequence", "process", "Se → forstå → velge → handle", "มองเห็น → เข้าใจ → เลือก → ลงมือทำ", "See → understand → choose → act", ("Barnet kan gå ut. Reduser farten og skap margin.", "เด็กอาจเดินออกมา ลดความเร็วและสร้างระยะปลอดภัย", "The child may step out. Slow down and create a margin."), steps=[i18n("👀 SE","👀 มองเห็น","👀 SEE"),i18n("🧠 FORSTÅ","🧠 เข้าใจ","🧠 UNDERSTAND"),i18n("⚡ VELGE","⚡ เลือก","⚡ CHOOSE"),i18n("🚗 HANDLE","🚗 ลงมือทำ","🚗 ACT")]),
    info("read-clue", "choice", "wheels", "Du så det. Men forstod du det?", "คุณเห็นแล้ว แต่เข้าใจหรือยัง?", "You saw it. Did you understand?", ("Hva forteller de dreide forhjulene?", "ล้อหน้าที่หันออกบอกอะไร?", "What do the turned wheels tell you?"), options=[opt("move","Bilen kan kjøre ut","รถอาจเคลื่อนออกมา","The car may pull out"),opt("stay","Bilen blir sikkert stående","รถจะจอดอยู่อย่างแน่นอน","The car will stay")], correct="move", correctFeedback=i18n("Små detaljer viser hva som kan skje.","รายละเอียดเล็ก ๆ บอกว่าอะไรอาจเกิดขึ้น","Small details show what may happen."), wrongFeedback=i18n("Se på hjulenes retning.","ดูทิศทางของล้อ","Look at the wheels.")),
    info("predict-next", "choice", "predict", "Hva skjer de neste tre sekundene?", "อีกสามวินาทีจะเกิดอะไร?", "What happens in the next three seconds?", ("Bussen blinker ut. Hva er mest sannsynlig?", "รถโดยสารเปิดไฟเลี้ยวออก อะไรน่าจะเกิดขึ้น?", "The bus indicates out. What is likely?"), options=[opt("out","Bussen kjører ut","รถโดยสารเคลื่อนออกมา","The bus pulls out"),opt("stay","Bussen blir stående","รถโดยสารยังจอดอยู่","The bus stays"),opt("back","Bussen rygger","รถโดยสารถอยหลัง","The bus reverses")], correct="out", correctFeedback=i18n("Nå kan du lage plass tidlig.","ตอนนี้คุณสร้างพื้นที่ได้ตั้งแต่เนิ่น ๆ","Now you can make room early."), wrongFeedback=i18n("Blinklyset viser førerens plan.","ไฟเลี้ยวแสดงแผนของผู้ขับขี่","The indicator shows the driver's plan.")),
    info("too-close", "sequence", "too_close", "For nær 😬", "ใกล้เกินไป 😬", "Too close 😬", ("Avstand er tid.", "ระยะห่างคือเวลา", "Distance is time."), steps=[i18n("SE","มองเห็น","SEE"),i18n("FORSTÅ","เข้าใจ","UNDERSTAND"),i18n("VELGE","เลือก","CHOOSE"),i18n("HANDLE","ลงมือทำ","ACT")], remember=i18n("Mer avstand gir mer tid.","ระยะห่างมากขึ้นทำให้มีเวลามากขึ้น","More distance gives more time.")),
    info("two-cars", "choice", "split", "To biler, samme fart", "รถสองคัน ความเร็วเท่ากัน", "Two cars, same speed", ("Hvem har mest tid?", "ใครมีเวลามากกว่า?", "Who has more time?"), options=[opt("left","Liten avstand","ระยะห่างน้อย","Small gap"),opt("right","God avstand","ระยะห่างดี","Good gap")], correct="right", correctFeedback=i18n("God avstand gir tid.","ระยะห่างที่ดีทำให้มีเวลา","A good gap gives time."), wrongFeedback=i18n("Sammenlign rommet foran bilene.","เปรียบเทียบพื้นที่หน้ารถ","Compare the room ahead.")),
    info("speed-changes", "choice", "speed", "Farten endrer alt", "ความเร็วเปลี่ยนทุกอย่าง", "Speed changes everything", ("Hva krever høyere fart?", "ความเร็วสูงขึ้นต้องการอะไร?", "What does higher speed demand?"), options=[opt("early","Oppdag faren tidligere","สังเกตอันตรายให้เร็วขึ้น","Notice earlier"),opt("late","Vent lenger","รอนานขึ้น","Wait longer")], correct="early", correctFeedback=i18n("Høyere fart gir mindre tid.","ความเร็วสูงทำให้มีเวลาน้อยลง","Higher speed gives less time."), wrongFeedback=i18n("Du må se endringen tidligere.","คุณต้องเห็นการเปลี่ยนแปลงให้เร็วขึ้น","You must see change earlier.")),
    info("safety-margin", "sequence", "margin", "Lag rom for feil", "สร้างพื้นที่เผื่อความผิดพลาด", "Make room for mistakes", ("En trygg fører lager rom rundt bilen.", "ผู้ขับขี่ที่ปลอดภัยสร้างพื้นที่รอบรถ", "A safe driver creates room around the car."), steps=[i18n("SIDEAVSTAND","ระยะด้านข้าง","SIDE SPACE"),i18n("AVSTAND FREMOVER","ระยะด้านหน้า","SPACE AHEAD"),i18n("TID","เวลา","TIME")]),
    {"id":"road-check-2","type":"roadCheck","eyebrow":i18n("ROAD CHECK 2 ⚡","ROAD CHECK 2 ⚡","ROAD CHECK 2 ⚡"),"title":i18n("Bruk det du har lært","ใช้สิ่งที่ได้เรียนรู้","Use what you learned"),"body":i18n("Fire korte situasjoner.","สี่สถานการณ์สั้น ๆ","Four short situations."),"questions":[
        question(("SPOT IT 👀","ค้นหา 👀","SPOT IT 👀"),("Risiko ved varebilen?","ความเสี่ยงข้างรถตู้?","Risk beside the van?"),[opt("hidden","Noen kan være skjult","อาจมีใครถูกบัง","Someone may be hidden"),opt("none","Ingen risiko","ไม่มีความเสี่ยง","No risk")],"hidden",("Se etter det skjulte.","มองหาสิ่งที่ถูกบัง","Look for what is hidden.")),
        question(("YOUR MOVE 🚗","ตาคุณ 🚗","YOUR MOVE 🚗"),("Barn nær gangfelt. Hva gjør du?","เด็กใกล้ทางม้าลาย คุณทำอย่างไร?","Child near crossing. What do you do?"),[opt("slow","Reduser farten","ลดความเร็ว","Slow down"),opt("same","Hold farten","คงความเร็ว","Keep speed")],"slow",("Handle før det haster.","ลงมือทำก่อนจะฉุกเฉิน","Act before it is urgent.")),
        question(("WHAT CHANGED? 🧠","อะไรเปลี่ยนไป? 🧠","WHAT CHANGED? 🧠"),("Hvilken detalj betyr noe?","รายละเอียดใดสำคัญ?","Which detail matters?"),[opt("wheels","Hjulenes retning","ทิศทางของล้อ","Wheel direction"),opt("colour","Bilens farge","สีของรถ","Car colour")],"wheels",("Retningen kan varsle bevegelse.","ทิศทางอาจเตือนถึงการเคลื่อนที่","Direction can warn of movement.")),
        question(("PREDICT 🔮","คาดการณ์ 🔮","PREDICT 🔮"),("Bussen blinker. Hva kan skje?","รถโดยสารเปิดไฟเลี้ยว อาจเกิดอะไร?","The bus indicates. What may happen?"),[opt("out","Bussen kjører ut","รถโดยสารเคลื่อนออกมา","The bus pulls out"),opt("vanish","Bussen forsvinner","รถโดยสารหายไป","The bus disappears")],"out",("Forutse og lag plass.","คาดการณ์และสร้างพื้นที่","Predict and make room."))]},
    {"id":"chapter-complete","type":"chapterComplete","eyebrow":i18n("KAPITTEL FULLFØRT","เรียนจบบทแล้ว","CHAPTER COMPLETE"),"title":i18n("BLIKKET · 15 / 15","การมอง · 15 / 15","VISION · 15 / 15"),"body":i18n("Du har lært å se før det skjer.","คุณได้เรียนรู้ที่จะมองเห็นก่อนเกิดเหตุ","You learned to see before it happens."),"skills":[i18n("👀 Oppdage","👀 สังเกต","👀 Notice"),i18n("🧠 Forstå","🧠 เข้าใจ","🧠 Understand"),i18n("🔮 Forutse","🔮 คาดการณ์","🔮 Predict"),i18n("🚗 Skape sikkerhetsmargin","🚗 สร้างระยะปลอดภัย","🚗 Create a safety margin")],"nextChapter":i18n("NESTE: 🚗 PLASSERING","ถัดไป: 🚗 ตำแหน่งรถ","NEXT: 🚗 POSITIONING")},
]

# ─── KAPITTEL 3: FART, REAKSJON OG STOPPLENGDE (CH03) ────────────────────────
_CH03_PLACEHOLDERS = [
    ("ch03_fart_001", "1", "CH03-FART-001", "Fartens fysikk og stopplengde", "Vise sammenhengen mellom fart, reaksjon og bremselengde", "førerperspektiv", "Høy fart som øker stopplengden drastisk", "biler og fotgjenger", "landevei og bygate", "fartsgrenseskilt", "fartens virkning", "/api/assets/stopping-distance-road-v1.png", ""),
    ("ch03_fart_002", "2", "CH03-FART-002", "Reaksjonslengde våken fører", "Demonstrere reaksjonslengde for en oppmerksom sjåfør", "førerperspektiv", "Uoppmerksomhet som forlenger reaksjonstiden", "bil foran", "landevei", "kantlinje", "1 sekund reaksjon", "/api/assets/stopping-distance-road-v1.png", "ch03_par_001"),
    ("ch03_par_001", "2p", "CH03-PAR-001", "Reaksjonslengde distrahert med mobil", "Sammenligne reaksjonslengde ved distraksjon", "delt førerperspektiv", "Mobilbruk som dobler reaksjonstiden", "bil og mobil", "landevei", "senterlinje", "forsinket reaksjon", "/api/assets/distraksjon.png", "ch03_fart_002"),
    ("ch03_fart_003", "3", "CH03-FART-003", "Bremselengde på tørt og vått føre", "Vise at bremselengden dobles på våt vei og firedobles ved dobbel fart", "sideprofil", "Dårlig veigrep og vannplaning ved for høy fart", "to biler", "våt asfalt", "bremsespor", "bremselengde og friksjon", "/api/assets/stopping-distance-teslas-v1.png", ""),
    ("ch03_fart_004", "4", "CH03-FART-004", "Road Check førerplass fart og stopp", "Teste beregning av reaksjons- og bremselengde", "førerperspektiv", "Feilvurdering av stopplengde ved uventede hendelser", "bil og hindring", "landevei", "skilt og merking", "trygg stopp", "/api/assets/stopping-distance-road-v1.png", ""),
    ("ch03_fart_005", "5", "CH03-FART-005", "3-sekundersregelen for trygg avstand", "Demonstrere korrekt 3-sekunders avstand til forankjørende", "førerperspektiv", "For kort følgeavstand som umuliggjør stans ved bråstopp", "to biler i kø", "landevei", "fast referansepunkt", "3 sekunders margin", "/api/assets/stopping-distance-road-v1.png", "ch03_par_002"),
    ("ch03_par_002", "5p", "CH03-PAR-002", "Farlig kort følgeavstand", "Sammenligne farene ved å ligge for tett på forankjørende", "delt førerperspektiv", "Påkjørsel bakfra ved uventet nedbremsing", "biler tett", "landevei", "veggrep", "manglende tidsmargin", "/api/assets/stopping-distance-road-v1.png", "ch03_fart_005"),
    ("ch03_fart_006", "6", "CH03-FART-006", "Mestring av fart og sikkerhetsmargin", "Oppsummere fartsforståelse og feire fullført kapittel", "utendørsperspektiv", "Mangelfull tilpasning av fart etter føreforhold", "skolebil og elev", "landevei", "fartsskilt og merking", "fartstilpasning", "/api/assets/stopping-distance-road-v1.png", ""),
]

CH03_ASSETS = {
    key: {"asset_id": asset_id, "page": page, "scene": scene,
          "pedagogical_purpose": purpose, "camera_angle": camera,
          "risk_source": risk, "risikokilde": risk,
          "vehicles_road_users": actors, "road_type": road,
          "signs_markings": markings, "learner_discovery": discovery,
          "hotspots": [], "pair_asset": pair_key, "status": "placeholder", "src": src,
          "alt": i18n("Illustrasjon av fart og bremselengde", "ภาพประกอบเรื่องความเร็วและระยะเบรก", "Illustration of speed and stopping distance")}
    for key, page, asset_id, scene, purpose, camera, risk, actors, road, markings, discovery, src, pair_key in _CH03_PLACEHOLDERS
}

CH03_LESSONS = [
    info("CH03-001", "intro", "ch03_fart_001", "Fartens fysikk og stopplengde", "ฟิสิกส์ของความเร็วและระยะหยุดรถ", "The physics of speed and stopping distance",
         ("Fart er den viktigste faktoren for din sikkerhet. Stopplengden består av reaksjonslengde og bremselengde. Når du dobler farten, firedobles bremselengden!",
          "ความเร็วเป็นตัวแปรสำคัญที่สุดต่อความปลอดภัย ระยะหยุดรถประกอบด้วยระยะคิดตอบสนองและระยะเบรกจริง เมื่อคุณเพิ่มความเร็วเป็นสองเท่า ระยะเบรกจะเพิ่มขึ้นถึงสี่เท่า!",
          "Speed is the most critical factor for your safety. Stopping distance consists of reaction distance and braking distance. When you double speed, braking distance quadruples!")),
    info("CH03-002", "choice", "ch03_fart_002", "Reaksjonslengde: Hvor langt ruller bilen?", "ระยะคิดตอบสนอง: รถแล่นไปไกลแค่ไหนก่อนแตะเบรก?", "Reaction distance: How far does the car travel?",
         ("Før foten rekker å trykke på bremsepedalen, går det normalt ca. 1 sekund. I 80 km/t ruller bilen 24 meter i løpet av dette sekundet!",
          "ก่อนที่เท้าจะเหยียบแป้นเบรก สมองต้องใช้เวลาตัดสินใจประมาณ 1 วินาที ที่ความเร็ว 80 กม./ชม. รถแล่นไปไกลถึง 24 เมตรโดยยังไม่ได้เบรก!",
          "Before your foot hits the brake pedal, roughly 1 second passes. At 80 km/h, the car rolls 24 metres during this second!"),
         options=[opt("distracted", "Distrahert fører bruker lengre tid", "ผู้ขับขี่ที่เสียสมาธิจะใช้เวลาคิดนานขึ้น", "A distracted driver takes longer"),
                  opt("superman", "Mennesket reagerer på 0 sekunder", "มนุษย์สามารถตอบสนองได้ใน 0 วินาที", "Humans react in 0 seconds")],
         correct="distracted",
         correctFeedback=i18n("Helt riktig! Distraksjon som mobilbruk forlenger reaksjonstiden farlig mye.",
                              "ถูกต้องที่สุด! การเสียสมาธิ เช่น การดูโทรศัพท์ ทำให้ระยะคิดตอบสนองยาวขึ้นอย่างอันตราย",
                              "Exactly right! Distractions like mobile phones extend reaction time dangerously."),
         wrongFeedback=i18n("Ingen kan reagere på 0 sekunder. Hjernen trenger tid til å oppdage faren.",
                            "ไม่มีใครตอบสนองได้ทันที สมองต้องใช้เวลาเพื่อมองเห็นและประมวลผล",
                            "No one reacts in 0 seconds. The brain requires time to detect hazards.")),
    info("CH03-003", "sequence", "ch03_fart_003", "Bremselengde på tørt og vått føre", "ระยะเบรกจริงบนพื้นแห้งและพื้นเปียก", "Braking distance on dry and wet surfaces",
         ("Bremselengden avhenger av bilens fart og veigrepet. På våt asfalt dobles bremselengden, og på is kan den bli opptil 8 ganger lenger!",
          "ระยะเบรกขึ้นอยู่กับความเร็วและการยึดเกาะของยาง บนถนนเปียกระยะเบรกจะเพิ่มเป็นสองเท่า และบนน้ำแข็งอาจเพิ่มขึ้นถึง 8 เท่า!",
          "Braking distance depends on speed and tire grip. On wet asphalt it doubles, and on ice it can be up to 8 times longer!"),
         steps=[i18n("1. TØRR ASFALT: Best veigrep", "1. ยางมะตอยแห้ง: การยึดเกาะดีที่สุด", "1. DRY ROAD: Best grip"),
                i18n("2. VÅT VEI: Dobbel bremselengde", "2. ถนนเปียก: ระยะเบรกเพิ่มเป็นสองเท่า", "2. WET ROAD: Double braking distance"),
                i18n("3. SNØ OG IS: Ekstrem bremselengde", "3. หิมะและน้ำแข็ง: ระยะเบรกยาวมากเป็นพิเศษ", "3. SNOW & ICE: Extreme braking distance"),
                i18n("4. SENK FARTEN: Skap sikkerhetsmargin", "4. ชะลอความเร็ว: เพื่อสร้างระยะปลอดภัย", "4. REDUCE SPEED: Create safety margin")]),
    {"id": "CH03-004", "type": "roadCheck", "road_check_id": "CH03-RC-001",
     "eyebrow": i18n("ROAD CHECK ⚡", "ROAD CHECK ⚡", "ROAD CHECK ⚡"),
     "title": i18n("Road Check ⚡ Fart og stopplengde", "Road Check ⚡ ทดสอบความเข้าใจ: ความเร็วและระยะหยุดรถ", "Road Check ⚡ Speed and Stopping Distance"),
     "body": i18n("Tre korte spørsmål om fart, reaksjon og bremsing.", "สามคำถามสั้นเพื่อทดสอบความแม่นยำเรื่องการคำนวณและระยะหยุดรถ", "Three short questions about speed, reaction, and braking."),
     "questions": [
         question(("STOPPLENGDE", "ระยะหยุดรถ", "STOPPING DISTANCE"),
                  ("Hva er formelen for bilens totale stopplengde?", "สูตรคำนวณระยะหยุดรถทั้งหมดคืออะไร?", "What is the formula for total stopping distance?"),
                  [opt("sum", "Reaksjonslengde + Bremselengde", "ระยะคิดตอบสนอง + ระยะเบรกจริง", "Reaction distance + Braking distance"),
                   opt("brake_only", "Kun bremselengden", "เฉพาะระยะเบรกจริงเท่านั้น", "Braking distance only")],
                  "sum",
                  ("Stopplengden er summen av strekningen du ruller før du bremser og strekningen du bremser.",
                   "ระยะหยุดรถคือผลรวมของระยะที่รถแล่นก่อนแตะเบรกบวกกับระยะเบรกจริง",
                   "Stopping distance is the sum of distance rolled before braking plus braking distance.")),
         question(("DOBBEL FART", "ความเร็วสองเท่า", "DOUBLE SPEED"),
                  ("Hva skjer med bremselengden når du øker farten fra 40 til 80 km/t?", "เมื่อเพิ่มความเร็วจาก 40 เป็น 80 กม./ชม. ระยะเบรกจริงจะเปลี่ยนไปอย่างไร?", "What happens to braking distance when speed increases from 40 to 80 km/h?"),
                  [opt("quadruple", "Den firedobles (4 ganger lenger)", "เพิ่มขึ้นถึง 4 เท่า", "It quadruples (4 times longer)"),
                   opt("double", "Den dobles bare", "เพิ่มขึ้นเพียง 2 เท่า", "It only doubles")],
                  "quadruple",
                  ("Bevegelsesenergien firedobles når farten dobles, derfor firedobles bremselengden.",
                   "พลังงานจลน์จะเพิ่มขึ้นเป็น 4 เท่าเมื่อความเร็วเพิ่มเป็นสองเท่า ทำให้ระยะเบรกเพิ่มเป็น 4 เท่า",
                   "Kinetic energy quadruples when speed doubles, so braking distance quadruples.")),
         question(("3-SEKUNDERSREGELEN", "กฎ 3 วินาที", "3-SECOND RULE"),
                  ("Hvorfor bruker vi 3-sekundersregelen til bilen foran?", "ทำไมเราจึงต้องเว้นระยะห่างตามกฎ 3 วินาทีจากคันหน้า?", "Why do we use the 3-second rule behind the vehicle ahead?"),
                  [opt("safety_gap", "For å ha nok tid til å stanse hvis bilen foran bråstopper", "เพื่อให้มีเวลาพอในการหยุดรถหากคันหน้าเบรกกะทันหัน", "To have enough time to stop if the car ahead brakes suddenly"),
                   opt("fuel", "Kun for å spare drivstoff", "เพื่อประหยัดน้ำมันเท่านั้น", "Only to save fuel")],
                  "safety_gap",
                  ("Tre sekunder gir deg tid til å oppfatte faren og bremse kontrollert.",
                   "สามวินาทีช่วยให้คุณมีเวลาเพียงพอในการมองเห็นและเบรกอย่างปลอดภัย",
                   "Three seconds gives you time to detect the hazard and brake safely."))
     ]},
    info("CH03-005", "choice", "ch03_fart_005", "3-sekundersregelen for trygg avstand", "กฎ 3 วินาทีเพื่อสร้างระยะห่างที่ปลอดภัย", "The 3-second rule for safe distance",
         ("Hvordan teller du 3 sekunder til bilen foran på landeveien?",
          "คุณจะนับ 3 วินาทีเพื่อเว้นระยะห่างจากคันหน้าได้อย่างไร?",
          "How do you count 3 seconds to the car ahead on the road?"),
         options=[opt("landmark", "Velg et fast merke i veikanten og tell 1001, 1002, 1003", "เลือกจุดสังเกตข้างทางแล้วนับ 1001, 1002, 1003", "Pick a fixed roadside marker and count 1001, 1002, 1003"),
                  opt("guess", "Gjett avstanden etter øyemål", "เดาระยะห่างด้วยสายตาคร่าว ๆ", "Guess the distance by eye")],
         correct="landmark",
         correctFeedback=i18n("Helt riktig! Et fast merke gir en objektiv og pålitelig måling av avstanden.",
                              "ถูกต้อง! การใช้จุดสังเกตที่หยุดนิ่งช่วยให้วัดระยะห่างได้อย่างแม่นยำและปลอดภัย",
                              "Exactly right! A fixed marker gives an objective and reliable measurement."),
         wrongFeedback=i18n("Øyemål svikter ofte i høy hastighet. Bruk alltid et fast referansepunkt.",
                            "การกะด้วยสายตามักคลาดเคลื่อนในความเร็วสูง ควรใช้จุดสังเกตเสมอ",
                            "Visual guessing often fails at high speed. Always use a fixed marker.")),
    {"id": "CH03-006", "type": "chapterComplete",
     "eyebrow": i18n("KAPITTEL FULLFØRT", "เรียนจบบทแล้ว", "CHAPTER COMPLETE"),
     "title": i18n("FART OG BREMSELENGDE · 6 / 6", "ความเร็วและระยะเบรก · 6 / 6", "SPEED AND STOPPING · 6 / 6"),
     "body": i18n("Du har lært fysikken bak fart, reaksjon og stopplengde. Du mestrer 3-sekundersregelen og vet hvordan du tilpasser farten etter veigrepet!",
                  "คุณเข้าใจหลักฟิสิกส์เบื้องหลังความเร็ว ระยะคิดตอบสนอง และระยะเบรกแล้ว คุณใช้กฎ 3 วินาทีได้อย่างมั่นใจและรู้วิธีปรับความเร็วตามสภาพถนน!",
                  "You have learned the physics of speed, reaction, and stopping distance. You master the 3-second rule and know how to adapt speed to road grip!"),
     "skills": [i18n("⏱️ Reaksjonslengde", "⏱️ ระยะคิดตอบสนอง", "⏱️ Reaction distance"),
                i18n("🛑 Bremselengde på ulike fører", "🛑 ระยะเบรกตามสภาพถนน", "🛑 Braking distance"),
                i18n("📏 3-sekundersregelen", "📏 กฎ 3 วินาที", "📏 3-second rule"),
                i18n("🛡️ Fartstilpasning", "🛡️ การปรับความเร็วอย่างปลอดภัย", "🛡️ Speed adaptation")],
     "nextChapter": i18n("NESTE: 📘 LÆRING OG DIDAKTIKK", "ถัดไป: 📘 การเรียนรู้อย่างมีประสิทธิภาพ", "NEXT: 📘 LEARNING AND DIDACTICS")}
]

# ─── KAPITTEL 4: DIDAKTIKK OG LÆRING (CH04) ──────────────────────────────────
_CH04_PLACEHOLDERS = [
    ("ch04_did_001", "1", "CH04-DID-001", "Moderne klasserom for pedagogisk trafikkopplæring", "Vise verdien av dyp forståelse fremfor overfladisk pugging", "klasseromsperspektiv", "Overfladisk kunnskap som svikter i uventede trafikksituasjoner", "biler og fotgjengere", "klasserom og byvei", "læringsmål", "forståelse foran pugging", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("ch04_did_002", "2", "CH04-DID-002", "Pugging vs POU sammenligning", "Demonstrere forskjellen på mekanisk pugging og situasjonsforståelse", "delt sammenligningsperspektiv", "Puggede svar som ikke kan anvendes når situasjonen endrer seg", "to situasjonsbilder", "bygate og landevei", "faresignaler", "årsak og virkning", "/api/assets/stopping-distance-road-v1.png", "ch04_par_001"),
    ("ch04_par_001", "2p", "CH04-PAR-001", "Problemorientert undervisning (POU) i praksis", "Vise hvordan eleven analyserer farene i en ekte situasjon", "førerperspektiv i trafikk", "Kryssende trafikanter og uoversiktlige blindsoner", "bil, sykkel og fotgjenger", "bygate", "gangfelt og vikeplikt", "aktiv fareanalyse", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch04_did_002"),
    ("ch04_did_003", "3", "CH04-DID-003", "Læringssirkelen og refleksjon ved feilsvar", "Lære eleven å analysere feil og bygge varig mestring", "nært fører- og instruktørperspektiv", "Gjentakelse av feil uten systematisk refleksjon", "elev og instruktør Michael", "skolebil", "dashbord og vei", "feilanalyse og mestring", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", ""),
    ("ch04_did_004", "4", "CH04-DID-004", "Road Check førerplass", "Teste elevens bevissthet rundt læringsstrategi", "førerperspektiv", "Feilaktige antakelser om at pugging er tilstrekkelig", "bil foran og skilt", "landevei", "skilt og merking", "reflektert valg", "/api/assets/stopping-distance-road-v1.png", ""),
    ("ch04_did_005", "5", "CH04-DID-005", "Fast mal vs Tilpasset opplæring", "Vise hvordan tilpasset opplæring på thai fjerner språkbarrieren", "delt visning", "Språkbarrierer som forårsaker misforståelser av norske trafikkregler", "skolebil og elev", "trafikkstasjon", "skilt og læremateriell", "språkuavhengig forståelse", "/api/assets/thumbs/thumb_vikeplikt_7_5a_buss.jpg", "ch04_par_002"),
    ("ch04_par_002", "5p", "CH04-PAR-002", "Tilpasset opplæring og trygg veiledning med Michael", "Fremheve trygg mestring uten språkbarrierer", "rolig passasjersete-perspektiv", "Usikkerhet som fører til panikkhandlinger i trafikken", "Michael og elev", "skolebil", "rolig gatebilde", "trygg veiledning", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch04_did_005"),
    ("ch04_did_006", "6", "CH04-DID-006", "Mestring og klar for teoriprøven", "Bekrefte fullført modul og bygge selvtillit til prøven", "inspirerende utendørsperspektiv", "Mangel på selvtillit før teoriprøven", "elev ved bil", "Statens vegvesen", "skilt og førerprøve", "mestring og bestått", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
]

CH04_ASSETS = {
    key: {"asset_id": asset_id, "page": page, "scene": scene,
          "pedagogical_purpose": purpose, "camera_angle": camera,
          "risk_source": risk, "risikokilde": risk,
          "vehicles_road_users": actors, "road_type": road,
          "signs_markings": markings, "learner_discovery": discovery,
          "hotspots": [], "pair_asset": pair_key, "status": "placeholder", "src": src,
          "alt": i18n("Illustrasjon for didaktikk og læring", "ภาพประกอบการเรียนรู้และการสอนที่มีประสิทธิภาพ", "Illustration of didactics and learning")}
    for key, page, asset_id, scene, purpose, camera, risk, actors, road, markings, discovery, src, pair_key in _CH04_PLACEHOLDERS
}

CH04_LESSONS = [
    info("CH04-001", "intro", "ch04_did_001", "Læring for livet, ikke bare til prøven", "เรียนรู้เพื่อชีวิตจริง ไม่ใช่แค่เพื่อสอบผ่าน", "Learning for life, not just for the exam",
         ("I Norge handler føreropplæring om å forstå trafikken, ikke bare pugge spørsmål. Når du forstår hvorfor en regel finnes, husker du den automatisk i en farlig situasjon.",
          "ในนอร์เวย์ การเรียนขับรถคือการเข้าใจการจราจร ไม่ใช่แค่การท่องจำข้อสอบ เมื่อคุณเข้าใจเหตุผลเบื้องหลังของกฎ คุณจะตอบสนองได้อย่างถูกต้องและปลอดภัยโดยอัตโนมัติ",
          "In Norway, driver training is about understanding traffic, not just cramming questions. When you understand why a rule exists, you remember it automatically in dangerous situations.")),
    info("CH04-002", "choice", "ch04_did_002", "Pugging vs. Problemorientert undervisning (POU)", "การท่องจำ vs การเรียนรู้จากสถานการณ์จริง (POU)", "Rote learning vs. Problem-oriented learning (POU)",
         ("Hva gir best resultat: Å pugge tilfeldige fasitsvar, eller å forstå problemet i trafikksituasjonen?",
          "วิธีใดให้ผลลัพธ์ที่ดีที่สุด: การท่องจำคำตอบ หรือการทำความเข้าใจปัญหาในสถานการณ์จราจรจริง?",
          "Which gives the best result: Memorising answers, or understanding the problem in the traffic situation?"),
         options=[opt("pugging", "Pugge fasitsvar utenat", "ท่องจำคำตอบโดยไม่คิด", "Memorise answers blindly"),
                  opt("pou", "Problemorientert læring (POU)", "เรียนรู้จากปัญหาจริง (POU)", "Problem-oriented learning (POU)")],
         correct="pou",
         correctFeedback=i18n("Riktig! POU lærer deg å gjenkjenne risiko og ta trygge valg.",
                              "ถูกต้อง! การเรียนรู้จากปัญหาจริง (POU) ช่วยให้คุณวิเคราะห์ความเสี่ยงและตัดสินใจได้อย่างปลอดภัย",
                              "Correct! POU teaches you to recognise risk and make safe choices."),
         wrongFeedback=i18n("Pugging svikter når spørsmålet omformuleres. Forstå situasjonen.",
                            "การท่องจำจะใช้ไม่ได้ผลเมื่อข้อสอบเปลี่ยนคำถาม จงเข้าใจสถานการณ์จริง",
                            "Cramming fails when wording changes. Understand the situation.")),
    info("CH04-003", "sequence", "ch04_did_003", "Læringssirkelen: Se → Forstå → Velge → Handle", "วงจรการเรียนรู้: มองเห็น → เข้าใจ → เลือก → ลงมือทำ", "Learning loop: See → Understand → Choose → Act",
         ("Når du svarer feil i quizen, er det ikke et nederlag. Det er starten på ekte mestring gjennom refleksjon.",
          "เมื่อคุณตอบผิดในแบบฝึกหัด นั่นไม่ใช่ความล้มเหลว แต่เป็นจุดเริ่มต้นของการเรียนรู้ที่แท้จริงผ่านการทบทวน",
          "When you answer incorrectly, it is not a defeat. It is the beginning of true mastery through reflection."),
         steps=[i18n("👀 1. OBSERVASJON (Se)", "👀 1. การสังเกต (มองเห็น)", "👀 1. OBSERVATION (See)"),
                i18n("🧠 2. REFLEKSJON (Forstå)", "🧠 2. การคิดทบทวน (เข้าใจ)", "🧠 2. REFLECTION (Understand)"),
                i18n("⚡ 3. BESLUTNING (Velge)", "⚡ 3. การตัดสินใจ (เลือก)", "⚡ 3. DECISION (Choose)"),
                i18n("🚗 4. MESTRING (Handle)", "🚗 4. ความเชี่ยวชาญ (ลงมือทำ)", "🚗 4. MASTERY (Act)")]),
    {"id": "CH04-004", "type": "roadCheck", "road_check_id": "CH04-RC-001",
     "eyebrow": i18n("ROAD CHECK ⚡", "ROAD CHECK ⚡", "ROAD CHECK ⚡"),
     "title": i18n("Road Check ⚡ Didaktikk og læring", "Road Check ⚡ ทดสอบความเข้าใจ: การเรียนรู้และวิธีสอน", "Road Check ⚡ Didactics and Learning"),
     "body": i18n("Tre korte spørsmål for å sjekke din læringsstrategi.", "สามคำถามสั้นเพื่อทดสอบกลยุทธ์การเรียนรู้ของคุณ", "Three short questions to verify your learning strategy."),
     "questions": [
         question(("LÆRINGSSTRATEGI", "กลยุทธ์การเรียนรู้", "STRATEGY"),
                  ("Hva er den største faren med ren pugging av teorispørsmål?", "อันตรายที่สุดของการท่องจำข้อสอบโดยไม่เข้าใจคืออะไร?", "What is the biggest risk of pure rote memorisation?"),
                  [opt("fail_change", "Du blir usikker når Vegvesenet omformulerer spørsmålet", "คุณจะสับสนทันทีเมื่อข้อสอบจริงเปลี่ยนคำพูด", "You become unsure when phrasing changes"),
                   opt("no_danger", "Ingen fare, pugging er alltid best", "ไม่มีอันตราย การท่องจำดีที่สุดเสมอ", "No risk, memorisation is always best")],
                  "fail_change",
                  ("Statens vegvesen tester forståelse, ikke ordrett hukommelse.", "กรมการขนส่งนอร์เวย์เน้นทดสอบความเข้าใจ ไม่ใช่การท่องจำคำต่อคำ", "Statens vegvesen tests understanding, not verbatim memory.")),
         question(("POU-METODEN", "วิธีการแบบ POU", "POU METHOD"),
                  ("Hva kjennetegner Problemorientert undervisning (POU)?", "ลักษณะสำคัญของการเรียนรู้แบบ POU คืออะไร?", "What characterises Problem-Oriented Teaching (POU)?"),
                  [opt("real_cases", "Å løse reelle trafikksituasjoner med årsak og virkning", "การฝึกแก้สถานการณ์จริงบนถนนโดยเข้าใจเหตุและผล", "Solving real traffic situations with cause and effect"),
                   opt("law_only", "Å lese lovboken fra perm til perm uten bilder", "การอ่านตัวบทกฎหมายโดยไม่มีภาพประกอบ", "Reading the law book without pictures")],
                  "real_cases",
                  ("POU gjør deg til en aktiv og reflektert sjåfør.", "POU ช่วยให้คุณเป็นผู้ขับขี่ที่ตื่นรู้และคิดวิเคราะห์เป็น", "POU makes you an active and reflective driver.")),
         question(("TRYGG VEILEDNING", "การสอนอย่างปลอดภัย", "SAFE GUIDANCE"),
                  ("Hvorfor forklarer lærer Michael reglene som en rolig passasjer?", "ทำไมครู Michael จึงอธิบายกฎอย่างใจเย็นเหมือนนั่งข้างๆ คุณ?", "Why does instructor Michael explain rules calmly as a passenger?"),
                  [opt("remove_stress", "For å fjerne stress og bygge trygghet og mestring", "เพื่อลดความกังวลและสร้างความมั่นใจที่แท้จริง", "To remove stress and build genuine confidence"),
                   opt("no_read", "Fordi han ikke vil at du skal lese", "เพราะเขาไม่อยากให้คุณอ่านหนังสือ", "Because he does not want you to read")],
                  "remove_stress",
                  ("Trygghet og ro er forutsetningen for god læring.", "ความสบายใจและความสงบคือหัวใจสำคัญของการเรียนรู้ที่มีประสิทธิภาพ", "Calm and confidence are prerequisites for good learning."))
     ]},
    info("CH04-005", "choice", "ch04_did_005", "Fast pensum vs. Tilpasset opplæring", "หลักสูตรแบบตายตัว vs การเรียนรู้ที่ปรับตามตัวบุคคล", "Fixed curriculum vs. Adapted learning",
         ("Elever lærer i ulikt tempo. Hvorfor er tilpasset opplæring på thailandsk så viktig?",
          "ผู้เรียนแต่ละคนมีจังหวะการเรียนรู้ไม่เหมือนกัน ทำไมการปรับการสอนเป็นภาษาไทยจึงสำคัญมาก?",
          "Learners advance at different paces. Why is adapted teaching in Thai so vital?"),
         options=[opt("remove_barrier", "Det fjerner språkbarrieren så du kan fokusere 100 % på reglene", "ช่วยขจัดอุปสรรคทางภาษา ทำให้โฟกัสกับกฎและความปลอดภัยได้ 100%", "It removes the language barrier so you can focus 100% on rules"),
                  opt("same_for_all", "Alle må tvinges gjennom nøyaktig samme norske mal", "ทุกคนควรถูกบังคับให้เรียนแบบเดียวกันทั้งหมด", "Everyone should be forced through the same template")],
         correct="remove_barrier",
         correctFeedback=i18n("Helt riktig! Når språket er klart, forsvinner usikkerheten.",
                              "ถูกต้องที่สุด! เมื่อภาษาชัดเจน ความกังวลก็หมดไปและเข้าใจกฎได้อย่างแท้จริง",
                              "Exactly right! When language is clear, doubt disappears."),
         wrongFeedback=i18n("Uten morsmålsstøtte tar språket for mye oppmerksomhet fra trafikksikkerheten.",
                            "หากไม่มีภาษาแม่ช่วย ภาษาจะแย่งความสนใจไปจากความปลอดภัยทางถนน",
                            "Without native language support, language takes attention away from safety.")),
    {"id": "CH04-006", "type": "chapterComplete",
     "eyebrow": i18n("KAPITTEL FULLFØRT", "เรียนจบบทแล้ว", "CHAPTER COMPLETE"),
     "title": i18n("DIDAKTIKK OG LÆRING · 6 / 6", "การเรียนรู้และการสอน · 6 / 6", "DIDACTICS AND LEARNING · 6 / 6"),
     "body": i18n("Du har nå fullført modulen om didaktikk og læring. Du vet hvordan du skal studere smart, forstå situasjonene og bestå teoriprøven på første forsøk!",
                  "คุณเรียนจบหัวข้อการเรียนรู้อย่างมีประสิทธิภาพแล้ว คุณรู้วิธีการเรียนอย่างฉลาด เข้าใจสถานการณ์จริง และพร้อมสอบผ่านในรอบแรกอย่างมั่นใจ!",
                  "You have completed the module on didactics and learning. You know how to study smartly, understand situations, and pass the theory test on your first try!"),
     "skills": [i18n("🧠 Forståelse foran pugging", "🧠 เข้าใจมากกว่าท่องจำ", "🧠 Understanding over rote"),
                i18n("🎯 Problemorientert læring (POU)", "🎯 การเรียนรู้จากปัญหาจริง (POU)", "🎯 Problem-oriented learning"),
                i18n("💡 Aktiv refleksjon", "💡 การคิดทบทวนอย่างมีสติ", "💡 Active reflection"),
                i18n("🏆 Bestått på første forsøk", "🏆 สอบผ่านในรอบแรก", "🏆 First-time pass")],
     "nextChapter": i18n("NESTE: 🚦 TRAFIKKREGLER", "ถัดไป: 🚦 กฎจราจร", "NEXT: 🚦 TRAFFIC RULES")}
]

# ─── KAPITTEL 5: MÅL OG RAMMER FOR TRINN 1 (CH05) ───────────────────────────
_CH05_PLACEHOLDERS = [
    ("ch05_tr1_001", "1", "CH05-TR1-001", "De 4 opplæringstrinnene i Norge", "Gi oversikt over hele føreropplæringen fra Trinn 1 til Trinn 4", "oversiktsperspektiv", "Manglende struktur i opplæringen som forsinker lappen", "skolebil og instruktør", "trafikkstasjon", "trinnmodell", "strukturert progresjon", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("ch05_tr1_002", "2", "CH05-TR1-002", "Hvem må ta Trinn 1 (Under 25 år)", "Forklare kravet om Trafikalt grunnkurs for alle under 25 år", "klasseromsperspektiv", "Ulovlig øvingskjøring uten fullført grunnkurs og bevis", "ungdommer i klasserom", "trafikkskole", "pensum", "kursbevis og krav", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", "ch05_par_001"),
    ("ch05_par_001", "2p", "CH05-PAR-001", "Fritaksregler for personer over 25 år", "Vise at personer over 25 kun trenger førstehjelp og mørkekjøring", "delt klasseromsvisning", "Misforståelser rundt fritak for eldre elever", "voksne elever", "klasserom", "kursbevis", "førstehjelp og mørke", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch05_tr1_002"),
    ("ch05_tr1_003", "3", "CH05-TR1-003", "Innholdet i Trinn 1: 17 timer", "Gå gjennom modulene trafikk, førstehjelp og mørkedemo", "undervisningsperspektiv", "Manglende førstehjelpskunnskap ved ulykker", "instruktør og dukke", "kursrom og vei", "førstehjelpsutstyr", "livreddende innsats", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("ch05_tr1_004", "4", "CH05-TR1-004", "Road Check Trinn 1 rammer", "Teste elevens forståelse for kravene til grunnkurs og øvingskjøring", "førerperspektiv", "Ulovlig kjøring uten oppfylte ledsager- og alderskrav", "skolebil og skilt", "landevei", "skilt og merking", "lovlig øving", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("ch05_tr1_005", "5", "CH05-TR1-005", "Krav til øvingskjøring: Rød L og ekstra speil", "Vise tekniske krav til bilen ved privat øvingskjøring", "eksteriør bakfra", "Manglende L-skilt eller speil som skaper fare for andre", "privatbil med L-skilt", "boligvei", "rød L og speil", "synlig merking", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", "ch05_par_002"),
    ("ch05_par_002", "5p", "CH05-PAR-002", "Krav til fører og ledsager: Bevis og 25 år / 5 år", "Vise dokumentasjonskrav og krav til ledsager", "interiør førerplass", "Ugyldig ledsager uten 5 års sammenhengende førerkort", "elev og ledsager", "bilkupe", "bevis og førerkort", "lovlig ledsager", "/api/assets/thumbs/thumb_vikeplikt_7_5a_buss.jpg", "ch05_tr1_005"),
    ("ch05_tr1_006", "6", "CH05-TR1-006", "Veien videre til Trinn 2", "Motivere for grunnleggende teknisk kjøretøybehandling", "utendørsperspektiv", "Utålmodighet og for tidlig kjøring i tett trafikk", "elev ved bil", "kjøregård", "kjegler og bil", "teknisk mestring", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
]

CH05_ASSETS = {
    key: {"asset_id": asset_id, "page": page, "scene": scene,
          "pedagogical_purpose": purpose, "camera_angle": camera,
          "risk_source": risk, "risikokilde": risk,
          "vehicles_road_users": actors, "road_type": road,
          "signs_markings": markings, "learner_discovery": discovery,
          "hotspots": [], "pair_asset": pair_key, "status": "placeholder", "src": src,
          "alt": i18n("Illustrasjon av Trinn 1 trafikalt grunnkurs", "ภาพประกอบหลักสูตรพื้นฐานจราจรขั้นที่ 1", "Illustration of Step 1 traffic basic course")}
    for key, page, asset_id, scene, purpose, camera, risk, actors, road, markings, discovery, src, pair_key in _CH05_PLACEHOLDERS
}

CH05_LESSONS = [
    info("CH05-001", "sequence", "ch05_tr1_001", "De 4 opplæringstrinnene i Norge", "4 ขั้นตอนการเรียนขับรถในนอร์เวย์", "The 4 training steps in Norway",
         ("I Norge er trafikkopplæringen delt inn i 4 trinn for å sikre systematisk mestring fra grunnleggende teori til selvstendig kjøring.",
          "ในนอร์เวย์ การเรียนขับรถถูกแบ่งเป็น 4 ขั้นตอนเพื่อสร้างความปลอดภัยอย่างเป็นระบบ ตั้งแต่ทฤษฎีพื้นฐานจนถึงการขับขี่อย่างอิสระ",
          "In Norway, driver training is divided into 4 steps to ensure systematic mastery from basic theory to independent driving."),
         steps=[i18n("Trinn 1: Trafikalt grunnkurs (17 timer)", "ขั้นที่ 1: หลักสูตรพื้นฐานจราจร (17 ชม.)", "Step 1: Traffic basic course (17h)"),
                i18n("Trinn 2: Grunnleggende kjøretøybehandling", "ขั้นที่ 2: การควบคุมรถขั้นพื้นฐาน", "Step 2: Basic vehicle control"),
                i18n("Trinn 3: Trafikal del og glattkjøring", "ขั้นที่ 3: การขับในจราจรและสนามลื่น", "Step 3: Traffic skills and skid pan"),
                i18n("Trinn 4: Avsluttende opplæring og langkjøring", "ขั้นที่ 4: การขับขี่ขั้นสมบูรณ์และทางไกล", "Step 4: Final training and long drive")]),
    info("CH05-002", "choice", "ch05_tr1_002", "Hvem må ta Trinn 1? (Under vs. over 25 år)", "ใครบ้างที่ต้องเรียนขั้นที่ 1? (อายุต่ำกว่า vs เกิน 25 ปี)", "Who must take Step 1? (Under vs. over 25)",
         ("Er du under 25 år, må du ta hele grunnkurset på 17 timer. Hva gjelder dersom du har fylt 25 år?",
          "หากคุณอายุต่ำกว่า 25 ปี ต้องเรียนครบ 17 ชั่วโมง แล้วถ้าคุณอายุ 25 ปีขึ้นไปจะมีข้อกำหนดอย่างไร?",
          "If under 25, you must complete all 17 hours. What applies if you are 25 or older?"),
         options=[opt("exempt_theory", "Fritatt for teoridelene, men må ta førstehjelp og mørkekjøring", "ได้รับการยกเว้นทฤษฎีทั่วไป แต่ต้องผ่านการปฐมพยาบาลและการขับขี่ในความมืด", "Exempt from general theory, but must take first aid and night driving"),
                  opt("all_exempt", "Helt fritatt for alle kurs og opplæring", "ได้รับการยกเว้นทุกวิชาโดยไม่ต้องเข้าอบรมใด ๆ", "Completely exempt from all courses and training")],
         correct="exempt_theory",
         correctFeedback=i18n("Helt riktig! Førstehjelp og mørkedemonstrasjon er obligatorisk for alle.",
                              "ถูกต้องที่สุด! การปฐมพยาบาลและการสาธิตการขับขี่ในความมืดเป็นวิชาบังคับสำหรับทุกคน",
                              "Exactly right! First aid and night driving demo are mandatory for everyone."),
         wrongFeedback=i18n("Personer over 25 år slipper teorien, men må fullføre førstehjelp og mørkekjøring.",
                            "ผู้ที่มีอายุ 25 ปีขึ้นไปได้รับการยกเว้นทฤษฎี แต่ต้องเข้าอบรมปฐมพยาบาลและการขับในความมืด",
                            "Those over 25 skip general theory, but must complete first aid and night driving.")),
    info("CH05-003", "sequence", "ch05_tr1_003", "Hva inneholder Trinn 1? (17 timer)", "หลักสูตรขั้นที่ 1 เรียนอะไรบ้าง? (รวม 17 ชั่วโมง)", "What does Step 1 contain? (17 hours)",
         ("Trafikalt grunnkurs er obligatorisk og gir felles forståelse for samhandling, lover og sikkerhet.",
          "หลักสูตรพื้นฐานจราจรเป็นวิชาบังคับที่สร้างความเข้าใจร่วมกันในเรื่องกฎหมาย ความปลอดภัย และการอยู่ร่วมกันบนถนน",
          "The traffic basic course is mandatory and provides common understanding of interaction, laws, and safety."),
         steps=[i18n("1. Trafikkopplæring og mennesket i trafikken (10 timer)", "1. การจราจรและพฤติกรรมมนุษย์บนท้องถนน (10 ชม.)", "1. Traffic education and human behavior (10h)"),
                i18n("2. Grunnleggende førstehjelp og tiltak ved ulykke (4 timer)", "2. การปฐมพยาบาลเบื้องต้นและการรับมืออุบัติเหตุ (4 ชม.)", "2. Basic first aid and accident response (4h)"),
                i18n("3. Mørkekjøringsdemonstrasjon i praksis (3 timer)", "3. การสาธิตการขับขี่ในความมืดภาคปฏิบัติ (3 ชม.)", "3. Night driving demonstration in practice (3h)")]),
    {"id": "CH05-004", "type": "roadCheck", "road_check_id": "CH05-RC-001",
     "eyebrow": i18n("ROAD CHECK ⚡", "ROAD CHECK ⚡", "ROAD CHECK ⚡"),
     "title": i18n("Road Check ⚡ Mål og rammer for Trinn 1", "Road Check ⚡ ทดสอบความเข้าใจ: กฎเกณฑ์ของขั้นที่ 1", "Road Check ⚡ Step 1 Framework"),
     "body": i18n("Tre korte spørsmål om Trinn 1 og krav til øvingskjøring.", "สามคำถามสั้นเพื่อยืนยันว่าคุณเข้าใจสิทธิ์และข้อบังคับของ Trinn 1 อย่างถูกต้อง", "Three short questions about Step 1 and practice driving."),
     "questions": [
         question(("MINSTEALDER", "อายุขั้นต่ำ", "MINIMUM AGE"),
                  ("Hvor gammel må du være for å øvingskjøre personbil (klasse B)?", "คุณต้องมีอายุอย่างน้อยกี่ปีจึงจะเริ่มฝึกขับรถส่วนบุคคลได้?", "How old must you be to practice drive a passenger car?"),
                  [opt("age_16", "16 år gammel", "อายุครบ 16 ปีบริบูรณ์", "16 years old"),
                   opt("age_18", "18 år gammel", "อายุครบ 18 ปีบริบูรณ์", "18 years old")],
                  "age_16",
                  ("Du kan starte øvingskjøring den dagen du fyller 16 år, forutsatt gyldig bevis.",
                   "คุณสามารถเริ่มฝึกขับรถได้ตั้งแต่วันที่อายุครบ 16 ปี เมื่อมีบัตรอนุญาตถูกต้อง",
                   "You can start practice driving the day you turn 16, provided you have a valid permit.")),
         question(("KRAV TIL LEDSAGER", "คุณสมบัติผู้ร่วมฝึก", "ACCOMPANYING DRIVER"),
                  ("Hvilke krav stilles til ledsager ved privat øvingskjøring?", "ผู้ร่วมฝึก (Ledsager) ต้องมีคุณสมบัติอย่างไร?", "What requirements apply to the accompanying driver?"),
                  [opt("req_25_5", "Minst 25 år og hatt førerkort sammenhengende i minst 5 år", "อายุอย่างน้อย 25 ปี และถือใบขับขี่ติดต่อกันไม่น้อยกว่า 5 ปี", "At least 25 years old with continuous license for 5 years"),
                   opt("req_18_1", "Minst 18 år og hatt førerkort i 1 år", "อายุ 18 ปีขึ้นไปและถือใบขับขี่ 1 ปี", "At least 18 years old with license for 1 year")],
                  "req_25_5",
                  ("Ledsageren har det juridiske ansvaret og må ha solid erfaring bak rattet.",
                   "ผู้ร่วมฝึกต้องมีความรับผิดชอบทางกฎหมายและมีประสบการณ์การขับขี่ที่มั่นคง",
                   "The accompanying driver bears legal responsibility and must have solid driving experience.")),
         question(("DOKUMENTASJON", "เอกสารที่ต้องพก", "DOCUMENTATION"),
                  ("Hva må du alltid ha med deg i bilen under øvingskjøring?", "คุณต้องพกเอกสารอะไรติดตัวในรถเสมอขณะฝึกขับ?", "What must you always carry in the car during practice driving?"),
                  [opt("bevis_id", "Trafikalt grunnkursbevis og gyldig legitimasjon med bilde", "บัตรรับรองผ่านหลักสูตร (Bevis) และบัตรประชาชนที่มีรูปถ่าย", "Course certificate and valid photo ID"),
                   opt("nothing", "Ingenting hvis ledsager har førerkort", "ไม่ต้องพกอะไรหากผู้ร่วมฝึกมีใบขับขี่อยู่แล้ว", "Nothing if the accompanier has a license")],
                  "bevis_id",
                  ("Både bevis og gyldig legitimasjon må kunne vises fram ved politikontroll.",
                   "ต้องสามารถแสดงบัตรรับรองและบัตรประชาชนที่มีรูปถ่ายเมื่อเจ้าหน้าที่เรียกตรวจ",
                   "Both the certificate and valid photo ID must be shown during a police check."))
     ]},
    info("CH05-005", "choice", "ch05_tr1_005", "Rettigheter og regler for privat øvingskjøring", "สิทธิ์และกฎสำคัญในการฝึกขับรถส่วนบุคคล", "Rights and rules for private practice driving",
         ("Hva må være montert på bilen ved privat øvingskjøring?",
          "ตัวรถต้องติดตั้งอุปกรณ์ใดบ้างเมื่อนำไปฝึกขับรถส่วนบุคคล?",
          "What equipment must be fitted to the car during private practice driving?"),
         options=[opt("l_and_mirror", "Rød L-skilt bak og ekstra innvendig speil for ledsager", "ป้ายตัวแอลสีแดง (L) ด้านหลัง และกระจกมองหลังเสริมด้านใน", "Red L-plate at the back and extra interior mirror"),
                  opt("hazard_lights", "Kun påslått varselblink", "เปิดเฉพาะไฟฉุกเฉินเท่านั้น", "Only flashing hazard lights")],
         correct="l_and_mirror",
         correctFeedback=i18n("Helt riktig! Rød L varsler andre trafikanter, og speilet gir ledsageren oversikt bakover.",
                              "ถูกต้องที่สุด! ป้ายตัวแอลเตือนเพื่อนร่วมทาง และกระจกเสริมช่วยให้ผู้ร่วมฝึกมองเห็นด้านหลัง",
                              "Exactly right! The red L alerts others, and the extra mirror gives the accompanier rear vision."),
         wrongFeedback=i18n("Bilen krever godkjent rød L-plate bak og ekstra innvendig speil for ledsageren.",
                            "รถต้องติดป้ายตัวแอลสีแดงด้านหลังและมีกระจกมองหลังเสริมด้านในสำหรับผู้ร่วมฝึก",
                            "The car requires an approved red L plate at the back and extra mirror inside.")),
    {"id": "CH05-006", "type": "chapterComplete",
     "eyebrow": i18n("KAPITTEL FULLFØRT", "เรียนจบบทแล้ว", "CHAPTER COMPLETE"),
     "title": i18n("TRINN 1 GRUNNKURS · 6 / 6", "หลักสูตรพื้นฐานจราจรขั้นที่ 1 · 6 / 6", "STEP 1 BASIC COURSE · 6 / 6"),
     "body": i18n("Gratulerer med fullført Trinn 1! Du forstår rammeverket, rettighetene og pliktene ved øvingskjøring i Norge. Nå er du klar for Trinn 2!",
                  "ยินดีด้วยที่คุณผ่านเนื้อหาขั้นที่ 1 แล้ว! คุณเข้าใจกรอบการเรียน สิทธิ์ และหน้าที่ในการฝึกขับรถในนอร์เวย์ พร้อมก้าวต่อไปสู่ขั้นที่ 2 อย่างมั่นใจ!",
                  "Congratulations on completing Step 1! You understand the framework, rights, and duties for practice driving in Norway. Ready for Step 2!"),
     "skills": [i18n("📚 De 4 opplæringstrinnene", "📚 4 ขั้นตอนการเรียนรู้", "📚 The 4 training steps"),
                i18n("🚗 Regler for øvingskjøring", "🚗 กฎเกณฑ์การฝึกขับรถ", "🚗 Rules for practice driving"),
                i18n("🪪 Bevis og ledsagerkrav", "🪪 บัตรอนุญาตและผู้ร่วมฝึก", "🪪 Permit and accompanier rules"),
                i18n("🎯 Veien videre til Trinn 2", "🎯 การเตรียมตัวสู่ขั้นที่ 2", "🎯 Moving on to Step 2")],
     "nextChapter": i18n("NESTE: 🔄 FORBIKJØRING OG RYGGING", "ถัดไป: 🔄 การแซงและการถอยหลัง", "NEXT: 🔄 OVERTAKING AND REVERSING")}
]

# ─── KAPITTEL 6: FORBIKJØRING, RYGGING OG VENDING (CH06) ─────────────────────
_CH06_PLACEHOLDERS = [
    ("ch06_forb_001", "1", "CH06-FORB-001", "Forbikjøring hovedregler og unntak", "Forklare at forbikjøring normalt skal skje til venstre", "førerperspektiv", "Frontkollisjon ved uoverveid forbikjøring", "to biler på vei", "landevei", "gul midtlinje", "forbikjøring til venstre", "/api/assets/forbikjoring.jpg", ""),
    ("ch06_forb_002", "2", "CH06-FORB-002", "Forbudte soner: Bakketopp og uoversiktlig sving", "Identifisere steder hvor forbikjøring er strengt forbudt", "førerperspektiv", "Møtende bil over bakketopp i høy hastighet", "bil mot bakketopp", "landevei", "sperrelinje", "forbudt forbikjøring", "/api/assets/forbikjoring.jpg", "ch06_par_001"),
    ("ch06_par_001", "2p", "CH06-PAR-001", "Sikker forbikjøringsstrekning med lang fri sikt", "Sammenligne trygg strekning mot uoversiktlig kurve", "oversiktsperspektiv", "Undersøkelse av fri sikt og margin fremover", "bil og lang rettstrekning", "landevei", "stiplet linje", "tilstrekkelig fri sikt", "/api/assets/stopping-distance-road-v1.png", "ch06_forb_002"),
    ("ch06_forb_003", "3", "CH06-FORB-003", "Forbikjøringens fire faser", "Gjennomgå observasjon, akselerasjon, forbikjøring og retur", "sekvensperspektiv", "Innsving for tidlig foran den forbikjørte bilen", "tre biler i bevegelse", "landevei", "kjørefeltlinjer", "4 faser for trygg forbikjøring", "/api/assets/forbikjoring.jpg", ""),
    ("ch06_forb_004", "4", "CH06-FORB-004", "Road Check forbikjøring og rygging", "Teste elevens vurderingsevne ved forbikjøring og rygging", "førerperspektiv", "Feilvurdering av fart og avstand til møtende trafikk", "bil og møtende trafikk", "landevei", "skilt og merking", "kritisk avgjørelse", "/api/assets/forbikjoring.jpg", ""),
    ("ch06_forb_005", "5", "CH06-FORB-005", "Rygging og vending med full vikeplikt", "Understreke at rygging krever full vikeplikt for alle trafikanter", "førerperspektiv", "Påkjøring av fotgjengere og syklister i blindsonen", "bil som rygger", "bygate og fortau", "kantstein og fortau", "full vikeplikt og hjelpemann", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch06_par_002"),
    ("ch06_par_002", "5p", "CH06-PAR-002", "Blindsone ved rygging og behov for hjelpemann", "Vise farlige blindsoner bak bilen ved rygging", "fugleperspektiv", "Barn eller hindringer skjult bak bilens hekk", "bil og hjelpemann", "parkeringsplass", "blindsonemarkering", "bruk av medhjelper", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", "ch06_forb_005"),
    ("ch06_forb_006", "6", "CH06-FORB-006", "Oppsummering og glidelåsprinsippet", "Oppsummere manøvrer og fletting ved feltsammenløp", "perspektiv over innfletting", "Aggressiv kjøring og manglende samhandling i kø", "biler som fletter", "motorvei / flerfeltsvei", "flettemerking", "glidelåsprinsippet", "/api/assets/rundkjoring1.jpg", ""),
]

CH06_ASSETS = {
    key: {"asset_id": asset_id, "page": page, "scene": scene,
          "pedagogical_purpose": purpose, "camera_angle": camera,
          "risk_source": risk, "risikokilde": risk,
          "vehicles_road_users": actors, "road_type": road,
          "signs_markings": markings, "learner_discovery": discovery,
          "hotspots": [], "pair_asset": pair_key, "status": "placeholder", "src": src,
          "alt": i18n("Illustrasjon av forbikjøring og rygging", "ภาพประกอบการแซงและการถอยหลัง", "Illustration of overtaking and reversing")}
    for key, page, asset_id, scene, purpose, camera, risk, actors, road, markings, discovery, src, pair_key in _CH06_PLACEHOLDERS
}

CH06_LESSONS = [
    info("CH06-001", "intro", "ch06_forb_001", "Forbikjøring: Hovedregler og unntak", "การแซงรถ: กฎหลักและข้อยกเว้น", "Overtaking: Main rules and exceptions",
         ("Forbikjøring skal som hovedregel skje til venstre. Du må ha tilstrekkelig fri sikt og forvisse deg om at manøveren kan skje helt uten fare for møtende og bakenforkjørende trafikk.",
          "ตามกฎทั่วไป การแซงรถต้องกระทำทางด้านซ้ายเสมอ คุณต้องมีทัศนวิสัยชัดเจนเพียงพอและมั่นใจว่าจะไม่ก่อให้เกิดอันตรายต่อรถคันหน้า รถที่สวนมา หรือรถที่ตามหลังมา",
          "Overtaking must normally take place on the left. You must have sufficient clear sight and ensure the manoeuvre occurs without danger to opposing or following traffic.")),
    info("CH06-002", "choice", "ch06_forb_002", "Hvor er forbikjøring strengt forbudt?", "จุดใดที่ห้ามแซงรถอย่างเด็ดขาด?", "Where is overtaking strictly prohibited?",
         ("Det er strengt forbudt å kjøre forbi like foran eller i uoversiktlige svinger, like foran bakketopp og foran gangfelt. Hvorfor er det forbudt foran bakketopp?",
          "ห้ามแซงเด็ดขาดบริเวณทางโค้งที่ทัศนวิสัยไม่ดี ก่อนถึงยอดเนิน และก่อนถึงทางม้าลาย ทำไมจึงห้ามแซงก่อนถึงยอดเนิน?",
          "It is strictly forbidden to overtake before blind curves, crests, and pedestrian crossings. Why is overtaking forbidden before crests?"),
         options=[opt("hidden_oncoming", "Du ser ikke møtende trafikk som kan komme i høy hastighet", "คุณมองไม่เห็นรถที่อาจสวนทางมาด้วยความเร็วสูง", "You cannot see oncoming traffic approaching at high speed"),
                  opt("engine_strain", "Bilen bruker mer drivstoff opp bakken", "เครื่องยนต์จะทำงานหนักเกินไปเมื่อขึ้นเนิน", "The engine consumes more fuel uphill")],
         correct="hidden_oncoming",
         correctFeedback=i18n("Riktig! På bakketoppen er blindsonen total, og en kollisjon her får katastrofale følger.",
                              "ถูกต้อง! ยอดเนินมีจุดบอดที่มองไม่เห็นอย่างสิ้นเชิง และการชนประสานงาจะรุนแรงมาก",
                              "Correct! The crest creates a complete blind zone, and a head-on collision is fatal."),
         wrongFeedback=i18n("Sikkerhet og fri sikt er den eneste grunnen. Man må aldri satse på flaks over en bakketopp.",
                            "ความปลอดภัยและทัศนวิสัยคือเหตุผลสำคัญที่สุด ห้ามเสี่ยงดวงกับการแซงบนยอดเนินเด็ดขาด",
                            "Safety and clear sight are the sole reasons. Never gamble on a crest.")),
    info("CH06-003", "sequence", "ch06_forb_003", "Forbikjøringens fire faser", "สี่ขั้นตอนของการแซงรถอย่างปลอดภัย", "The 4 phases of overtaking",
         ("En trygg forbikjøring krever disiplin i alle ledd. Er du i minste tvil, skal du avstå fra å kjøre forbi!",
          "การแซงอย่างปลอดภัยต้องอาศัยความรอบคอบและมีวินัย หากมีความลังเลแม้แต่น้อย จงอย่าแซงเด็ดขาด!",
          "Safe overtaking requires discipline at every stage. If in doubt, do not overtake!"),
         steps=[i18n("1. FORBEREDELSE: Sjekk sikt forover, speil og blindsone", "1. เตรียมพร้อม: ตรวจสอบทัศนวิสัยด้านหน้า กระจกมองข้าง และจุดบอด", "1. PREPARATION: Check sight ahead, mirrors, blind spot"),
                i18n("2. TEGN OG FELTBYTTE: Blink tidlig og legg deg bestemt ut", "2. ส่งสัญญาณ: เปิดไฟเลี้ยวล่วงหน้าและเปลี่ยนช่องทางอย่างมั่นใจ", "2. SIGNAL: Indicate early and move decisively"),
                i18n("3. PASSERING: Hold god sideavstand til kjøretøyet", "3. การแซงผ่าน: เว้นระยะห่างด้านข้างอย่างปลอดภัย", "3. PASSING: Maintain safe lateral distance"),
                i18n("4. RETUR: Se hele bilen i sladrespeilet før du svinger inn", "4. กลับเข้าเลน: มองเห็นหน้ารถคันที่ถูกแซงเต็มคันในกระจกก่อนกลับเข้าเลน", "4. RETURN: See the overtaken car fully in mirror before returning")]),
    {"id": "CH06-004", "type": "roadCheck", "road_check_id": "CH06-RC-001",
     "eyebrow": i18n("ROAD CHECK ⚡", "ROAD CHECK ⚡", "ROAD CHECK ⚡"),
     "title": i18n("Road Check ⚡ Forbikjøring og rygging", "Road Check ⚡ ทดสอบความเข้าใจ: การแซงและการถอยหลัง", "Road Check ⚡ Overtaking and Reversing"),
     "body": i18n("Tre korte spørsmål om forbikjøring, rygging og fletting.", "สามคำถามสั้นเพื่อทดสอบการตัดสินใจแซงและกฎการถอยหลังอย่างปลอดภัย", "Three short questions about overtaking, reversing, and zipper merge."),
     "questions": [
         question(("VIKEPLIKT VED RYGGING", "การให้ทางเมื่อถอยรถ", "YIELD WHEN REVERSING"),
                  ("Hvem har du vikeplikt for når du rygger bilen?", "เมื่อคุณถอยหลัง คุณมีหน้าที่ต้องให้ทางแก่ใครบ้าง?", "Who do you have duty to yield to when reversing?"),
                  [opt("all_traffic", "All annen trafikk, inkludert syklister og fotgjengere", "การจราจรอื่นทั้งหมด ทั้งรถ คนเดินเท้า และจักรยาน", "All other traffic, including cyclists and pedestrians"),
                   opt("cars_only", "Kun biler som kommer fra høyre", "เฉพาะรถยนต์ที่มาจากทางขวาเท่านั้น", "Only cars coming from the right")],
                  "all_traffic",
                  ("Ved rygging har du ubetinget vikeplikt for all trafikk. Du må stoppe helt dersom noen nærmer seg.",
                   "เมื่อถอยรถ คุณมีหน้าที่ให้ทางแก่ทุกคนอย่างไร้เงื่อนไข และต้องหยุดสนิทเมื่อมีผู้อื่นเข้าใกล้",
                   "When reversing you have unconditional duty to yield to all traffic.")),
         question(("HJELPEMANN", "ผู้ช่วยดูท้ายรถ", "GUIDE / HELPER"),
                  ("Hva må du gjøre dersom sikten bakover er hindret under rygging?", "หากทัศนวิสัยด้านหลังถูกบดบังขณะถอยรถ คุณต้องทำอย่างไร?", "What must you do if rear view is obscured while reversing?"),
                  [opt("use_helper", "Bruk en medhjelper på utsiden som veileder deg", "ใช้ผู้ช่วยยืนดูอยู่นอกรถเพื่อช่วยส่งสัญญาณ", "Use a helper outside to guide you"),
                   opt("horn_only", "Bare tute med hornet og rygge sakte", "บีบแตรส่งสัญญาณแล้วค่อย ๆ ถอย", "Just honk the horn and reverse slowly")],
                  "use_helper",
                  ("Er sikten utilstrekkelig, krever loven at du bruker en medhjelper for å unngå påkjørsler.",
                   "หากมองไม่เห็น กฎหมายกำหนดให้มีผู้ช่วยนำทางเพื่อป้องกันการชนหรือเกิดอุบัติเหตุ",
                   "If visibility is insufficient, the law requires using a helper to prevent accidents.")),
         question(("GLIDELÅSPRINSIPPET", "หลักการสลับฟันปลา", "ZIPPER PRINCIPLE"),
                  ("Hva innebærer glidelåsprinsippet når to kjørefelt snevres inn til ett?", "หลักการสลับฟันปลา (Glidelåsprinsippet) เมื่อสองช่องทางรวมเหลือช่องทางเดียวหมายถึงอะไร?", "What does the zipper principle mean when two lanes merge?"),
                  [opt("alternate", "Bilene fletter rolig og gjensidig annenhver gang", "รถสลับกันแทรกเข้าทีละคันอย่างสุภาพและร่วมมือกัน", "Cars merge smoothly and mutually one by one"),
                   opt("right_priority", "Feltet til høyre har alltid forkjørsrett", "ช่องทางขวามีสิทธิ์ไปก่อนเสมอโดยไม่ต้องรอ", "The right lane always has priority")],
                  "alternate",
                  ("Glidelåsprinsippet betyr gjensidig hensyn der bilene slipper hverandre inn annenhver gang.",
                   "หลักการสลับฟันปลาเน้นความมีน้ำใจร่วมกัน โดยให้รถสลับกันไปทีละคันเพื่อความคล่องตัว",
                   "The zipper principle means mutual courtesy where vehicles let each other merge alternately."))
     ]},
    info("CH06-005", "choice", "ch06_forb_005", "Rygging og vending: Full vikeplikt", "การถอยหลังและการกลับรถ: ให้ทางทุกกรณี", "Reversing and turning: Full duty to yield",
         ("Er det tillatt å rygge eller foreta vending på motorvei eller påkjøringsrampe?",
          "อนุญาตให้ถอยหลังหรือกลับรถบนทางด่วน (Motorvei) หรือทางลาดเข้าสู่ทางด่วนหรือไม่?",
          "Is it permitted to reverse or make a U-turn on a motorway or access ramp?"),
         options=[opt("strictly_forbidden", "Strengt forbudt under alle omstendigheter", "ห้ามเด็ดขาดไม่ว่าในกรณีใด ๆ ทั้งสิ้น", "Strictly forbidden under all circumstances"),
                  opt("allowed_slow", "Tillatt hvis du kjører veldig sakte og har nødblink på", "ทำได้หากขับช้ามากและเปิดไฟฉุกเฉิน", "Allowed if driving very slowly with hazard lights on")],
         correct="strictly_forbidden",
         correctFeedback=i18n("Helt riktig! På motorvei og motortrafikkvei er all rygging og vending strengt forbudt med fare for førerkortbeslag.",
                              "ถูกต้องที่สุด! บนทางด่วนการถอยหลังหรือกลับรถเป็นสิ่งต้องห้ามร้ายแรงและอาจถูกยึดใบขับขี่",
                              "Exactly right! On motorways, all reversing and turning is strictly prohibited."),
         wrongFeedback=i18n("Aldri rygge på motorvei! Fortsett til neste avkjøring og snu lovlig der.",
                            "ห้ามถอยหลังบนทางด่วนเด็ดขาด! ให้ขับต่อไปจนถึงทางออกถัดไปแล้วค่อยกลับรถอย่างถูกต้อง",
                            "Never reverse on a motorway! Continue to the next exit and turn safely there.")),
    {"id": "CH06-006", "type": "chapterComplete",
     "eyebrow": i18n("KAPITTEL FULLFØRT", "เรียนจบบทแล้ว", "CHAPTER COMPLETE"),
     "title": i18n("FORBIKJØRING OG RYGGING · 6 / 6", "การแซงและการถอยหลัง · 6 / 6", "OVERTAKING AND REVERSING · 6 / 6"),
     "body": i18n("Du mestrer reglene for sikker forbikjøring, rygging med full vikeplikt og samhandling med glidelåsprinsippet!",
                  "คุณเข้าใจกฎการแซงรถอย่างปลอดภัย การถอยหลังที่มีหน้าที่ให้ทางแก่ทุกคน และการร่วมมือกันด้วยหลักการสลับฟันปลาเรียบร้อยแล้ว!",
                  "You have mastered the rules for safe overtaking, reversing with full duty to yield, and the zipper merge principle!"),
     "skills": [i18n("🏎️ Forbikjøringens 4 faser", "🏎️ 4 ขั้นตอนการแซงรถ", "🏎️ 4 phases of overtaking"),
                i18n("🚫 Forbudte forbikjøringssoner", "🚫 จุดห้ามแซงเด็ดขาด", "🚫 Prohibited overtaking zones"),
                i18n("🔄 Rygging med full vikeplikt", "🔄 การถอยหลังโดยให้ทางทุกคน", "🔄 Reversing with full yield"),
                i18n("🤝 Glidelåsprinsippet", "🤝 การผสานเลนแบบสลับฟันปลา", "🤝 Zipper merge principle")],
     "nextChapter": i18n("NESTE: 🅿️ STANS OG PARKERING", "ถัดไป: 🅿️ การหยุดและการจอดรถ", "NEXT: 🅿️ STOPPING AND PARKING")}
]

# ─── KAPITTEL 7: STANS OG PARKERING (CH07) ───────────────────────────────────
_CH07_PLACEHOLDERS = [
    ("ch07_park_001", "1", "CH07-PARK-001", "Forskjellen på stans og parkering", "Definere stans som av/påstigning vs enhver annen hensetting", "bygateperspektiv", "Ulovlig stans som hindrer trafikkflyt", "bil ved fortau", "bygate", "kantstein", "stans vs parkering", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("ch07_park_002", "2", "CH07-PARK-002", "Skilt 370 (Stans forbudt) med rødt kryss", "Forklare at skilt 370 forbyr all stans selv i få sekunder", "gateperspektiv", "Misforståelse av at raskt ærend er tillatt ved stansforbud", "bil og skilt 370", "bygate", "skilt 370 rødt kryss", "absolutt stansforbud", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch07_par_001"),
    ("ch07_par_001", "2p", "CH07-PAR-001", "Skilt 372 (Parkering forbudt) med én strek", "Sammenligne skilt 372 som tillater kort av- og påstigning", "delt gateperspektiv", "Forveksling mellom skilt 370 og skilt 372", "bil og skilt 372", "bygate", "skilt 372 en strek", "parkering forbudt tillatt stans", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", "ch07_park_002"),
    ("ch07_park_003", "3", "CH07-PARK-003", "Hvor er det alltid forbudt å stanse?", "Lære steder med generelt stansforbud: Gangfelt, kurve, tunnel, motorvei", "oversiktsperspektiv", "Tildekking av sikt ved gangfelt og kryss", "bil nær gangfelt", "bygate", "gangfelt og skilt", "generelle forbudssoner", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("ch07_park_004", "4", "CH07-PARK-004", "Road Check stans og parkering", "Teste elevens kunnskap om parkeringsregler og skilt", "førerperspektiv", "Feilplassering som utløser bot og fare for myke trafikanter", "bil ved veikant", "bygate", "skilt og merking", "presis regelkontroll", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
    ("ch07_park_005", "5", "CH07-PARK-005", "5-metersregelen ved kryss og gangfelt", "Vise hvordan 5 meter måles fra kurvens startpunkt", "måleperspektiv", "Parkering for nær kryss som blokkerer sikten", "bil ved kryss", "kryss og gangfelt", "fortauskant og 5m markering", "5 metersregelen", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", "ch07_par_002"),
    ("ch07_par_002", "5p", "CH07-PAR-002", "Korrekt måling av 5 meter fra kurve", "Presisere oppmåling fra der fortauskanten begynner å runde", "nært perspektiv", "Feilmåling som fører til trafikkfelle og bot", "oppmålingsgrafikk", "kryss", "oppmerket kurveradius", "korrekt 5m målepunkt", "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg", "ch07_park_005"),
    ("ch07_park_006", "6", "CH07-PARK-006", "Oppsummering og trygg parkering", "Oppsummere stans- og parkeringsregler og feire fullført kapittel", "utendørsperspektiv", "Manglende sikring av bil mot rulling i bakke", "parkert bil", "parkeringsplass", "p-skilt og oppmerking", "trygg og lovlig parkering", "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg", ""),
]

CH07_ASSETS = {
    key: {"asset_id": asset_id, "page": page, "scene": scene,
          "pedagogical_purpose": purpose, "camera_angle": camera,
          "risk_source": risk, "risikokilde": risk,
          "vehicles_road_users": actors, "road_type": road,
          "signs_markings": markings, "learner_discovery": discovery,
          "hotspots": [], "pair_asset": pair_key, "status": "placeholder", "src": src,
          "alt": i18n("Illustrasjon av stans og parkering", "ภาพประกอบการหยุดและการจอดรถ", "Illustration of stopping and parking")}
    for key, page, asset_id, scene, purpose, camera, risk, actors, road, markings, discovery, src, pair_key in _CH07_PLACEHOLDERS
}

CH07_LESSONS = [
    info("CH07-001", "intro", "ch07_park_001", "Forskjellen på stans og parkering", "ความแตกต่างระหว่างการหยุดรถและการจอดรถ", "The difference between stopping and parking",
         ("Stans er kortest mulig stopp for av- eller påstigning, eller av- og pålessing. Enhver annen hensetting regnes som parkering – selv om føreren ikke forlater bilen!",
          "การหยุดรถ (Stans) คือการหยุดชั่วคราวเพื่อส่งคนหรือขนของเท่าที่จำเป็นเท่านั้น การหยุดนิ่งนอกเหนือจากนี้ถือเป็นการจอดรถ (Parkering) ทั้งสิ้น แม้จะยังนั่งอยู่ในรถก็ตาม!",
          "Stopping is the briefest pause for boarding or unloading. Any other stay counts as parking – even if the driver stays in the car!")),
    info("CH07-002", "choice", "ch07_park_002", "Skilt 370 (Stans forbudt) vs. Skilt 372 (Parkering forbudt)", "ป้ายห้ามหยุดรถ (370) vs ป้ายห้ามจอดรถ (372)", "Sign 370 (No stopping) vs. Sign 372 (No parking)",
         ("Hva er tillatt ved skilt 372 (blått skilt med én rød diagonalstrek)?",
          "สิ่งใดที่อนุญาตให้ทำได้เมื่อพบป้าย 372 (ป้ายวงกลมสีน้ำเงินมีขีดทแยงสีแดงเส้นเดียว)?",
          "What is permitted at sign 372 (blue sign with single red diagonal slash)?"),
         options=[opt("drop_off", "Kort stans for av- og påstigning av passasjerer", "การหยุดสั้น ๆ เพื่อรับส่งผู้โดยสาร", "Brief stop for passengers boarding or alighting"),
                  opt("leave_car", "Gå fra bilen for et raskt butikkbesøk", "ดับเครื่องแล้วเดินไปทำธุระในร้านค้าชั่วครู่", "Leaving the car for a quick shop visit")],
         correct="drop_off",
         correctFeedback=i18n("Riktig! Skilt 372 forbyr parkering, men tillater kort stans for av- og påstigning.",
                              "ถูกต้อง! ป้าย 372 ห้ามจอดรถ แต่อนุญาตให้หยุดส่งคนหรือขนถ่ายสิ่งของเท่าที่จำเป็นได้",
                              "Correct! Sign 372 prohibits parking, but allows brief stopping for passengers."),
         wrongFeedback=i18n("Å forlate bilen eller vente i bilen regnes som parkering og er forbudt ved skilt 372.",
                            "การลงจากรถหรือจอดรถรอถือเป็นการจอดรถ ซึ่งต้องห้ามตามป้าย 372",
                            "Leaving the car or waiting counts as parking and is prohibited by sign 372.")),
    info("CH07-003", "sequence", "ch07_park_003", "Hvor er det alltid forbudt å stanse?", "จุดใดบ้างที่ห้ามหยุดรถตลอดเวลา?", "Where is stopping always prohibited?",
         ("Trafikkreglene definerer steder hvor all stans er strengt forbudt for å beskytte liv og helse.",
          "กฎจราจรกำหนดจุดห้ามหยุดรถเด็ดขาดทุกกรณีเพื่อป้องกันอันตรายและรักษาความปลอดภัยในชีวิต",
          "Traffic regulations define locations where all stopping is strictly prohibited to protect safety."),
         steps=[i18n("1. I uoversiktlig kurve, i tunnel og på bakketopp", "1. ในทางโค้งทัศนวิสัยไม่ดี ในอุโมงค์ และบนยอดเนิน", "1. In blind curves, tunnels, and crests"),
                i18n("2. I vegkryss og nærmere enn 5 meter fra vegkryss", "2. ในทางแยกและในระยะน้อยกว่า 5 เมตรจากทางแยก", "2. In intersections and within 5 meters of intersections"),
                i18n("3. På gangfelt, sykkelfelt og nærmere enn 5 meter foran gangfelt", "3. บนทางม้าลาย เลนจักรยาน และในระยะ 5 เมตรก่อนถึงทางม้าลาย", "3. On zebra crossings, cycle lanes, and within 5 meters before crossing"),
                i18n("4. På motorvei og motortrafikkvei", "4. บนทางด่วนและทางหลวงสัญจรความเร็วสูง", "4. On motorways and expressways")]),
    {"id": "CH07-004", "type": "roadCheck", "road_check_id": "CH07-RC-001",
     "eyebrow": i18n("ROAD CHECK ⚡", "ROAD CHECK ⚡", "ROAD CHECK ⚡"),
     "title": i18n("Road Check ⚡ Stans og parkering", "Road Check ⚡ ทดสอบความเข้าใจ: การหยุดและจอดรถ", "Road Check ⚡ Stopping and Parking"),
     "body": i18n("Tre korte spørsmål om 5-metersregelen og skilting.", "สามคำถามสั้นเพื่อทดสอบความแม่นยำเรื่องกฎระยะห่าง 5 เมตรและป้ายจราจร", "Three short questions about the 5-meter rule and signage."),
     "questions": [
         question(("FEMMETERSREGELEN", "กฎระยะ 5 เมตร", "THE 5-METER RULE"),
                  ("Hvorfor må du parkere minst 5 meter unna et vegkryss?", "ทำไมคุณจึงต้องจอดรถห่างจากทางแยกอย่างน้อย 5 เมตร?", "Why must you park at least 5 meters from an intersection?"),
                  [opt("clear_view", "For å sikre fri sikt for kryssende trafikk og myke trafikanter", "เพื่อเปิดทัศนวิสัยให้รถที่เลี้ยวและคนข้ามถนนมองเห็นชัดเจน", "To ensure clear sight for turning traffic and pedestrians"),
                   opt("reserved_city", "Fordi kommunen eier de første 5 meterne", "เพราะเทศบาลสงวนพื้นที่ 5 เมตรแรกไว้", "Because municipality owns the first 5 meters")],
                  "clear_view",
                  ("Femmetersregelen hindrer at parkerte biler skaper farlige blindsoner i veikryss.",
                   "กฎระยะห่าง 5 เมตรช่วยป้องกันไม่ให้รถที่จอดบดบังสายตาบริเวณทางแยก",
                   "The 5-meter rule prevents parked cars from creating dangerous blind zones in junctions.")),
         question(("SKILT 370", "ป้ายกากบาทแดง 370", "SIGN 370"),
                  ("Hva betyr skilt 370 (rundt blått skilt med rødt kryss)?", "ป้าย 370 (ป้ายวงกลมสีน้ำเงินกากบาทสีแดง) มีความหมายอย่างไร?", "What does sign 370 (blue circle with red cross) mean?"),
                  [opt("no_stopping_at_all", "Stans forbudt (all stans og parkering er ulovlig)", "ห้ามหยุดรถเด็ดขาด (ห้ามทั้งหยุดชั่วคราวและห้ามจอด)", "No stopping (all stopping and parking is prohibited)"),
                   opt("free_parking", "Gratis parkering i opptil en time", "อนุญาตให้จอดฟรีได้ไม่เกิน 1 ชั่วโมง", "Free parking for up to 1 hour")],
                  "no_stopping_at_all",
                  ("Skilt 370 forbyr all stans. Du har ikke lov til å slippe av passasjerer her.",
                   "ป้าย 370 ห้ามหยุดรถเด็ดขาด แม้แต่การแวะส่งผู้โดยสารก็ทำไม่ได้",
                   "Sign 370 prohibits all stopping. You cannot even drop off passengers here.")),
         question(("PARKERING FORAN GANGFELT", "การจอดก่อนถึงทางม้าลาย", "PARKING BEFORE CROSSING"),
                  ("Hvor nær et gangfelt har du lov til å stanse eller parkere foran feltet?", "กฎหมายอนุญาตให้หยุดหรือจอดรถในระยะใกล้ทางม้าลายได้ไม่น้อยกว่ากี่เมตร?", "How close to a pedestrian crossing may you stop or park before the crossing?"),
                  [opt("five_meters", "Minst 5 meter foran gangfeltet", "ต้องห่างอย่างน้อย 5 เมตรก่อนถึงทางม้าลาย", "At least 5 meters before the crossing"),
                   opt("one_meter", "1 meter foran gangfeltet", "ห่างอย่างน้อย 1 เมตร", "1 meter before the crossing")],
                  "five_meters",
                  ("Fem meter før gangfeltet sikrer at kryssende fotgjengere ikke blir skjult for andre biler.",
                   "ระยะ 5 เมตรก่อนถึงทางม้าลายช่วยให้ผู้ข้ามถนนไม่ถูกรถที่จอดบดบัง",
                   "Five meters before the crossing ensures pedestrians are not hidden from other drivers."))
     ]},
    info("CH07-005", "choice", "ch07_park_005", "5-metersregelen ved kryss og gangfelt", "กฎระยะห่าง 5 เมตรจากทางแยกและทางม้าลาย", "The 5-meter rule at intersections and crossings",
         ("Hvorfra måles de 5 meterne i et vegkryss?",
          "การวัดระยะห่าง 5 เมตรจากทางแยก ต้องเริ่มวัดจากจุดใด?",
          "From where are the 5 meters measured at an intersection?"),
         options=[opt("curve_start", "Fra det punktet der fortauskanten eller vegkanten begynner å runde", "จากจุดที่ขอบทางหรือขอบทางเท้าเริ่มโค้งเข้าสู่ทางแยก", "From the point where the curb or road edge begins to curve"),
                  opt("middle_cross", "Fra nøyaktig midt i krysset", "จากจุดกึ่งกลางของทางแยกพอดี", "From the exact center of the intersection")],
         correct="curve_start",
         correctFeedback=i18n("Helt riktig! Målingen starter der kurven på fortauskanten begynner, ikke midt i veien.",
                              "ถูกต้องที่สุด! ต้องเริ่มวัดจากจุดที่ขอบทางเริ่มโค้งเข้าสู่ทางแยก",
                              "Exactly right! Measurement starts where the curb begins to curve, not in the road center."),
         wrongFeedback=i18n("Husk at 5 meter måles fra der kantsteinen begynner å runde mot krysset.",
                            "จำไว้ว่าต้องวัด 5 เมตรจากจุดที่ขอบทางเริ่มโค้งเข้าหาทางแยก",
                            "Remember that 5 meters is measured from where the curb begins to curve.")),
    {"id": "CH07-006", "type": "chapterComplete",
     "eyebrow": i18n("KAPITTEL FULLFØRT", "เรียนจบบทแล้ว", "CHAPTER COMPLETE"),
     "title": i18n("STANS OG PARKERING · 6 / 6", "การหยุดและการจอดรถ · 6 / 6", "STOPPING AND PARKING · 6 / 6"),
     "body": i18n("Du har fullført modulen for stans og parkering! Du kan forskjellen på stans og parkering, mestrer 5-metersregelen og unngår unødige bøter!",
                  "คุณผ่านเนื้อหาเรื่องการหยุดและการจอดรถครบถ้วนแล้ว! คุณแยกแยะการหยุดกับการจอดได้แม่นยำ เชี่ยวชาญกฎ 5 เมตร และจอดได้อย่างถูกต้องปลอดภัย!",
                  "You have completed the module on stopping and parking! You know the difference between stopping and parking, master the 5-meter rule, and park safely!"),
     "skills": [i18n("🅿️ Stans vs. Parkering", "🅿️ การหยุด vs การจอด", "🅿️ Stopping vs Parking"),
                i18n("🚫 Skilt 370 og 372", "🚫 ป้ายจราจร 370 และ 372", "🚫 Signs 370 and 372"),
                i18n("📏 5-metersregelen", "📏 กฎระยะห่าง 5 เมตร", "📏 5-meter rule"),
                i18n("🛡️ Sikring ved parkering", "🛡️ ความปลอดภัยเมื่อจอดรถ", "🛡️ Parking safety")],
     "nextChapter": i18n("NESTE: 🏁 NESTE KAPITTEL", "ถัดไป: 🏁 บทถัดไป", "NEXT: 🏁 NEXT CHAPTER")}
]

CHAPTERS = {
    "CH01": {"code": "CH01", "title": i18n("Kapittel 1 · Blikket", "บทที่ 1 · การมอง", "Chapter 1 · Vision"), "lessons": LESSONS, "assets": ASSETS},
    "CH03": {"code": "CH03", "title": i18n("Kapittel 3 · Fart og stopplengde", "บทที่ 3 · ความเร็วและระยะหยุดรถ", "Chapter 3 · Speed and Stopping Distance"), "lessons": CH03_LESSONS, "assets": CH03_ASSETS},
    "CH04": {"code": "CH04", "title": i18n("Kapittel 4 · Didaktikk og læring", "บทที่ 4 · การเรียนรู้และการสอนที่มีประสิทธิภาพ", "Chapter 4 · Didactics and Learning"), "lessons": CH04_LESSONS, "assets": CH04_ASSETS},
    "CH05": {"code": "CH05", "title": i18n("Kapittel 5 · Mål og rammer for Trinn 1", "บทที่ 5 · เป้าหมายและกรอบของขั้นที่ 1", "Chapter 5 · Goals and Framework for Step 1"), "lessons": CH05_LESSONS, "assets": CH05_ASSETS},
    "CH06": {"code": "CH06", "title": i18n("Kapittel 6 · Forbikjøring og rygging", "บทที่ 6 · การแซงและการถอยหลัง", "Chapter 6 · Overtaking and Reversing"), "lessons": CH06_LESSONS, "assets": CH06_ASSETS},
    "CH07": {"code": "CH07", "title": i18n("Kapittel 7 · Stans og parkering", "บทที่ 7 · การหยุดและการจอดรถ", "Chapter 7 · Stopping and Parking"), "lessons": CH07_LESSONS, "assets": CH07_ASSETS},
}

ALL_ASSETS = {**ASSETS, **CH03_ASSETS, **CH04_ASSETS, **CH05_ASSETS, **CH06_ASSETS, **CH07_ASSETS}


COPY = {k: i18n(*v) for k, v in {
    "brand":("THAI2DRIVE STUDIEBOKEN","หนังสือเรียน THAI2DRIVE","THAI2DRIVE STUDY BOOK"),"chapters":("Kapittel 1 · Blikket","บทที่ 1 · การมอง","Chapter 1 · Vision"),"continue":("Fortsett der du slapp","เรียนต่อจากจุดเดิม","Continue where you left off"),"start":("START →","เริ่ม →","START →"),"progress":("Progresjon","ความคืบหน้า","Progress"),"completed":("fullført","เสร็จแล้ว","completed"),"backHome":("Oversikt","ภาพรวม","Overview"),"previous":("Forrige","ก่อนหน้า","Previous"),"next":("Fortsett","เรียนต่อ","Continue"),"understood":("Jeg forstår","ฉันเข้าใจ","I understand"),"remember":("HUSK","จำไว้","REMEMBER"),"roadCleared":("ROAD CHECK CLEARED ⚡","ผ่าน ROAD CHECK ⚡","ROAD CHECK CLEARED ⚡"),"roadRetry":("Rolig repetisjon","ทบทวนอย่างสงบ","Calm review"),"review":("Repeter","ทบทวน","Review"),"finish":("Fortsett","เรียนต่อ","Continue"),"imageMissing":("THAI2DRIVE-bildet kommer snart","ภาพ THAI2DRIVE จะมาเร็ว ๆ นี้","THAI2DRIVE image coming soon"),"storageError":("Progresjonen kunne ikke lagres.","ไม่สามารถบันทึกความคืบหน้าได้","Progress could not be saved."),"contentError":("Siden kan ikke vises nå.","ไม่สามารถแสดงหน้านี้ได้","This page cannot be displayed."),"whatChanged":("WHAT CHANGED? 🧠","อะไรเปลี่ยนไป? 🧠","WHAT CHANGED? 🧠"),"originalView":("Opprinnelig bilde","ภาพเดิม","Original image")}.items()}

CSS = r"""
#screenStudybook{padding:0;background:#071225;overflow-y:auto;color:var(--text)}.sbx-shell{width:min(760px,100%);min-height:100%;margin:auto;padding:18px 16px 96px}.sbx-top,.sbx-row,.sbx-road-head{display:flex;align-items:center;justify-content:space-between;gap:12px}.sbx-top{margin-bottom:18px}.sbx-logo,.sbx-eyebrow{font-size:.72rem;font-weight:900;letter-spacing:.13em;color:#60e6ff}.sbx-hero,.sbx-card{padding:24px;border-radius:24px;background:linear-gradient(145deg,#102b4b,#101a36);border:1px solid #2c6383;box-shadow:0 18px 45px #0006}.sbx-card{padding:0;overflow:hidden}.sbx-copy{padding:20px}.sbx-track{height:8px;background:#ffffff16;border-radius:99px;overflow:hidden}.sbx-fill{height:100%;background:linear-gradient(90deg,#00d9ff,#a637ff)}.sbx-primary,.sbx-choice,.sbx-secondary{border:0;border-radius:14px;min-height:48px;padding:12px 18px;font:inherit;font-weight:850;cursor:pointer}.sbx-primary{background:#ff8a1f;color:#111}.sbx-secondary,.sbx-choice{background:#142844;color:#eaf7ff;border:1px solid #3a5c7d}.sbx-primary:focus-visible,.sbx-secondary:focus-visible,.sbx-choice:focus-visible,.sbx-hotspot:focus-visible{outline:3px solid #62e8ff}.sbx-map{display:grid;gap:9px;margin-top:18px}.sbx-map-card{display:grid;grid-template-columns:40px 1fr auto;gap:12px;padding:12px;border-radius:14px;background:#101d34}.sbx-map-card small,.sbx-map-card strong{display:block}.sbx-image{position:relative;min-height:230px;background:#0b1728}.sbx-image img{width:100%;min-height:230px;max-height:420px;object-fit:cover;transition:opacity .15s ease}.sbx-pair-toggle{position:absolute;top:12px;left:12px;display:inline-flex;gap:4px;background:#071225ee;padding:4px;border-radius:99px;border:1px solid #2c6383;box-shadow:0 6px 18px #0009;z-index:10;backdrop-filter:blur(8px)}.sbx-pair-btn{background:transparent;border:0;color:#8ab4d5;font-size:.72rem;font-weight:850;letter-spacing:.04em;padding:6px 14px;border-radius:99px;cursor:pointer;transition:all .2s ease}.sbx-pair-btn.active{background:linear-gradient(90deg,#0066ff,#00d9ff);color:#fff;box-shadow:0 0 12px #00d9ff66}.sbx-pair-btn:focus-visible{outline:2px solid #65eaff}.sbx-hotspot{position:absolute;width:58px;height:58px;border:3px solid #65eaff;border-radius:50%;background:#00d9ff30;transform:translate(-50%,-50%)}.sbx-hotspot.found{background:#ff8a1f88}.sbx-counter{position:absolute;top:12px;right:12px;background:#071225dd;padding:8px;border-radius:20px}.sbx-flow,.sbx-actions,.sbx-skills{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:9px;margin-top:18px}.sbx-flow span,.sbx-skills span{padding:12px;border-radius:10px;background:#142b47;text-align:center}.sbx-choice.correct{border-color:#65eaff}.sbx-choice.wrong{border-color:#ff648c}.sbx-feedback,.sbx-remember{margin-top:16px;padding:14px;border-radius:10px;background:#0b1728;border-left:4px solid #ff8a1f}.sbx-footer{display:flex;justify-content:space-between;margin-top:16px}.sbx-footer button:disabled{opacity:.38}.sbx-result{text-align:center;padding:36px}.sbx-score{font-size:3rem;font-weight:950;color:#65eaff}.sbx-status{color:#ffb4c7}@media(min-width:900px){#app.studybook-mode{width:min(980px,96vw);max-width:none;margin:auto}.sbx-shell{width:min(840px,100%)}.sbx-image,.sbx-image img{min-height:360px}}@media(max-width:420px){.sbx-actions{grid-template-columns:1fr}.sbx-footer{position:sticky;bottom:72px;background:#071225e8;padding:10px 0}}@media(prefers-reduced-motion:reduce){.sbx-fill{transition:none}}
"""
SCREEN = '<div class="screen" id="screenStudybook"><main class="sbx-shell" id="sbxRoot" aria-live="polite"></main></div>'


_DATA = json.dumps({
    "assets": ALL_ASSETS,
    "lessons": LESSONS,
    "copy": COPY,
    "chapters": CHAPTERS,
    "ch03_lessons": CH03_LESSONS,
    "ch03_assets": CH03_ASSETS,
    "ch04_lessons": CH04_LESSONS,
    "ch04_assets": CH04_ASSETS,
    "ch05_lessons": CH05_LESSONS,
    "ch05_assets": CH05_ASSETS,
    "ch06_lessons": CH06_LESSONS,
    "ch06_assets": CH06_ASSETS,
    "ch07_lessons": CH07_LESSONS,
    "ch07_assets": CH07_ASSETS,
}, ensure_ascii=False, separators=(",", ":"))

SCRIPT = r"""
var SBX_DATA=__SBX_DATA__,SBX_KEY='t2d_studybook_progress_v1',sbxState={view:'home',index:0,answered:false,roadIndex:0,roadAnswers:[],found:[],storageFailed:false};
function sbxEl(t,c,x){var e=document.createElement(t);if(t==='button')e.type='button';if(c)e.className=c;if(typeof x==='string')e.textContent=x;return e}function sbxL(value){if(!value||typeof value!=='object')return '';var text=value[appLang];return typeof text==='string'?text:''}function sbxCopy(k){return sbxL(SBX_DATA.copy[k])}function sbxDefaultProgress(){return{version:2,currentLesson:0,completedLessons:[],roadChecks:{},updatedAt:null}}function sbxReadProgress(){try{var r=_ls.get(SBX_KEY),p=r?JSON.parse(r):sbxDefaultProgress();if(!p||!Array.isArray(p.completedLessons))return sbxDefaultProgress();if(!p.roadChecks)p.roadChecks={};return p}catch(e){return sbxDefaultProgress()}}function sbxSaveProgress(p){try{p.version=2;p.updatedAt=new Date().toISOString();_ls.set(SBX_KEY,JSON.stringify(p));sbxState.storageFailed=false}catch(e){sbxState.storageFailed=true}}function sbxComplete(id){var p=sbxReadProgress();if(p.completedLessons.indexOf(id)<0)p.completedLessons.push(id);p.currentLesson=Math.min(sbxState.index+1,SBX_DATA.lessons.length-1);sbxSaveProgress(p);sbxState.answered=true}function sbxImage(k){var a=SBX_DATA.assets[k],w=sbxEl('div','sbx-image');if(!a)return w;var i=document.createElement('img');i.src=a.src;i.alt=sbxL(a.alt);i.onerror=function(){w.replaceChildren(sbxEl('div','sbx-feedback',sbxCopy('imageMissing')))};w.appendChild(i);if(a.pair_asset&&SBX_DATA.assets[a.pair_asset]){var p=SBX_DATA.assets[a.pair_asset],nav=sbxEl('div','sbx-pair-toggle');var b1=sbxEl('button','sbx-pair-btn active',sbxCopy('originalView'));b1.type='button';var b2=sbxEl('button','sbx-pair-btn',sbxCopy('whatChanged'));b2.type='button';b1.onclick=function(){b1.classList.add('active');b2.classList.remove('active');i.src=a.src;i.alt=sbxL(a.alt)};b2.onclick=function(){b2.classList.add('active');b1.classList.remove('active');i.src=p.src;i.alt=sbxL(p.alt)};nav.append(b1,b2);w.appendChild(nav)}return w}function sbxFeedback(c,x,ok){var o=c.querySelector('.sbx-feedback');if(o)o.remove();var f=sbxEl('div','sbx-feedback',x);f.role='status';f.dataset.result=ok?'correct':'wrong';c.querySelector('.sbx-copy').appendChild(f)}
function sbxHome(){sbxState.view='home';var r=document.getElementById('sbxRoot'),p=sbxReadProgress(),pc=Math.round(p.completedLessons.length/SBX_DATA.lessons.length*100),h=sbxEl('section','sbx-hero');r.replaceChildren();h.append(sbxEl('div','sbx-logo',sbxCopy('brand')),sbxEl('h1','',sbxCopy('chapters')),sbxEl('p','',sbxCopy('continue')));var row=sbxEl('div','sbx-row');row.append(sbxEl('span','',sbxCopy('progress')),sbxEl('strong','',pc+' %'));var tr=sbxEl('div','sbx-track'),fi=sbxEl('div','sbx-fill');fi.style.width=pc+'%';tr.appendChild(fi);var b=sbxEl('button','sbx-primary',sbxCopy('start'));b.type='button';b.onclick=function(){sbxOpen(Math.min(Number(p.currentLesson)||0,SBX_DATA.lessons.length-1))};h.append(row,tr,b);r.appendChild(h);var m=sbxEl('div','sbx-map');SBX_DATA.lessons.forEach(function(l,n){var c=sbxEl('div','sbx-map-card'),z=sbxEl('span','');z.append(sbxEl('strong','',sbxL(l.title)),sbxEl('small','',sbxL(l.eyebrow)));c.append(sbxEl('span','',String(n+1)),z,sbxEl('span','',p.completedLessons.includes(l.id)?sbxCopy('completed'):''));m.appendChild(c)});r.appendChild(m)}function sbxHeader(r){var t=sbxEl('div','sbx-top'),b=sbxEl('button','sbx-secondary',sbxCopy('backHome'));b.type='button';b.onclick=sbxHome;t.append(b,sbxEl('span','sbx-logo',sbxCopy('brand')),sbxEl('span','',appLang.toUpperCase()));r.appendChild(t)}function sbxFrame(r,l){var c=sbxEl('article','sbx-card'),x=sbxEl('div','sbx-copy');x.append(sbxEl('div','sbx-eyebrow',sbxL(l.eyebrow)),sbxEl('h1','',sbxL(l.title)),sbxEl('p','',sbxL(l.body)));c.appendChild(x);r.appendChild(c);return c}function sbxFooter(r){var f=sbxEl('div','sbx-footer'),p=sbxEl('button','sbx-secondary',sbxCopy('previous')),n=sbxEl('button','sbx-primary',sbxCopy('next'));p.disabled=sbxState.index===0;p.onclick=function(){sbxOpen(sbxState.index-1)};n.disabled=!sbxState.answered;n.onclick=function(){sbxOpen(Math.min(sbxState.index+1,SBX_DATA.lessons.length-1))};f.append(p,n);r.appendChild(f)}function sbxNext(){var n=document.querySelector('#sbxRoot .sbx-footer .sbx-primary');if(n)n.disabled=!sbxState.answered}
function sbxIntro(c,l){c.insertBefore(sbxImage(l.asset),c.firstChild);var b=sbxEl('button','sbx-primary',sbxCopy('start'));b.onclick=function(){sbxComplete(l.id);sbxNext()};c.querySelector('.sbx-copy').appendChild(b)}function sbxSequence(c,l){c.insertBefore(sbxImage(l.asset),c.firstChild);var f=sbxEl('div','sbx-flow');l.steps.forEach(function(s){f.appendChild(sbxEl('span','',sbxL(s)))});var b=sbxEl('button','sbx-primary',sbxCopy('understood'));b.onclick=function(){sbxComplete(l.id);sbxFeedback(c,sbxL(l.remember||l.body),true);sbxNext()};c.querySelector('.sbx-copy').append(f,b)}function sbxChoice(c,l){c.insertBefore(sbxImage(l.asset),c.firstChild);var a=sbxEl('div','sbx-actions');l.options.forEach(function(o){var b=sbxEl('button','sbx-choice',sbxL(o.label));b.onclick=function(){var ok=o.id===l.correct;a.querySelectorAll('button').forEach(function(q){q.classList.remove('correct','wrong')});b.classList.add(ok?'correct':'wrong');sbxFeedback(c,sbxL(ok?l.correctFeedback:l.wrongFeedback),ok);if(ok){sbxComplete(l.id);sbxNext()}};a.appendChild(b)});c.querySelector('.sbx-copy').appendChild(a)}function sbxSpot(c,l){var v=sbxImage(l.asset),n=sbxEl('span','sbx-counter','0 / '+l.hazards.length);v.appendChild(n);sbxState.found=[];l.hazards.forEach(function(h,i){var b=sbxEl('button','sbx-hotspot');b.style.left=h.x+'%';b.style.top=h.y+'%';b.setAttribute('aria-label',sbxL(h.label));b.onclick=function(){if(sbxState.found.includes(i))return;sbxState.found.push(i);b.classList.add('found');n.textContent=sbxState.found.length+' / '+l.hazards.length;var done=sbxState.found.length===l.hazards.length;sbxFeedback(c,sbxL(done?l.completeFeedback:l.feedback),true);if(done){sbxComplete(l.id);sbxNext()}};v.appendChild(b)});c.insertBefore(v,c.firstChild)}
function sbxRoad(c,l){var q=l.questions[sbxState.roadIndex],x=c.querySelector('.sbx-copy');x.replaceChildren();var h=sbxEl('div','sbx-road-head');h.append(sbxEl('div','sbx-eyebrow',sbxL(q.label)),sbxEl('span','',(sbxState.roadIndex+1)+' / '+l.questions.length));x.append(h,sbxEl('h1','',sbxL(q.prompt)));var a=sbxEl('div','sbx-actions');q.options.forEach(function(o){var b=sbxEl('button','sbx-choice',sbxL(o.label));b.onclick=function(){var ok=o.id===q.correct;a.querySelectorAll('button').forEach(function(z){z.disabled=true});sbxState.roadAnswers.push(ok);sbxFeedback(c,sbxL(q.explanation),ok);var n=sbxEl('button','sbx-primary',sbxState.roadIndex+1<l.questions.length?sbxCopy('next'):sbxCopy('finish'));n.onclick=function(){if(++sbxState.roadIndex<l.questions.length)sbxRoad(c,l);else sbxRoadResult(l)};x.appendChild(n)};a.appendChild(b)});x.appendChild(a)}function sbxRoadResult(l){var r=document.getElementById('sbxRoot'),s=sbxState.roadAnswers.filter(Boolean).length,t=l.questions.length,ok=s===t,c=sbxEl('section','sbx-card sbx-result');r.replaceChildren();c.append(sbxEl('div','sbx-eyebrow',sbxCopy(ok?'roadCleared':'roadRetry')),sbxEl('div','sbx-score',s+' / '+t));var p=sbxReadProgress();p.roadChecks[l.id]={score:s,total:t};if(ok){if(!p.completedLessons.includes(l.id))p.completedLessons.push(l.id);p.currentLesson=Math.min(sbxState.index+1,SBX_DATA.lessons.length-1)}sbxSaveProgress(p);var b=sbxEl('button','sbx-primary',sbxCopy(ok?'finish':'review'));b.onclick=ok?function(){sbxOpen(Math.min(sbxState.index+1,SBX_DATA.lessons.length-1))}:function(){sbxState.roadIndex=0;sbxState.roadAnswers=[];sbxOpen(sbxState.index)};c.appendChild(b);r.appendChild(c)}function sbxCompleteScreen(c,l){var x=c.querySelector('.sbx-copy'),s=sbxEl('div','sbx-skills');l.skills.forEach(function(v){s.appendChild(sbxEl('span','',sbxL(v)))});x.append(s,sbxEl('div','sbx-eyebrow',sbxL(l.nextChapter)));var b=sbxEl('button','sbx-primary',sbxCopy('finish'));b.onclick=function(){sbxComplete(l.id);sbxHome()};x.appendChild(b)}
function sbxOpen(i){var l=SBX_DATA.lessons[i],r=document.getElementById('sbxRoot');if(!l){r.replaceChildren(sbxEl('div','sbx-feedback',sbxCopy('contentError')));return}sbxState.view='lesson';sbxState.index=i;sbxState.answered=sbxReadProgress().completedLessons.includes(l.id);if(l.type==='roadCheck'){sbxState.roadIndex=0;sbxState.roadAnswers=[]}r.replaceChildren();sbxHeader(r);var c=sbxFrame(r,l);if(l.type==='intro')sbxIntro(c,l);else if(l.type==='sequence')sbxSequence(c,l);else if(l.type==='choice')sbxChoice(c,l);else if(l.type==='spotHazard')sbxSpot(c,l);else if(l.type==='roadCheck')sbxRoad(c,l);else if(l.type==='chapterComplete')sbxCompleteScreen(c,l);else sbxFeedback(c,sbxCopy('contentError'),false);if(l.type!=='roadCheck'&&l.type!=='chapterComplete')sbxFooter(r);var p=sbxReadProgress();p.currentLesson=i;sbxSaveProgress(p)}function loadStudiebok(){var r=document.getElementById('sbxRoot');if(!r)return;document.getElementById('app').classList.add('studybook-mode');sbxState.view==='lesson'?sbxOpen(sbxState.index):sbxHome()}function renderStudybook(){var s=document.getElementById('screenStudybook');if(s&&s.classList.contains('active'))loadStudiebok()}

""".replace("__SBX_DATA__", _DATA)


def install(html: str) -> str:
    start = '    <!-- ═══ STUDIEBOK SCREEN ═══ -->'
    end = '    <!-- ═══ FORBIKJØRING SCREEN ═══ -->'
    if start not in html or end not in html:
        raise ValueError("Studybook screen markers not found")
    before, rest = html.split(start, 1)
    _, after = rest.split(end, 1)
    html = before + start + "\n    " + SCREEN + "\n\n" + end + after
    html = html.replace("</style>", CSS + "\n</style>", 1)
    html = html.replace("if (typeof renderStopping === 'function' && document.getElementById('stopSpeed')) renderStopping();", "if (typeof renderStopping === 'function' && document.getElementById('stopSpeed')) renderStopping();\n  if (typeof renderStudybook === 'function') renderStudybook();", 1)
    html = html.replace("  activeTab = tab;", "  activeTab = tab;\n  document.getElementById('app').classList.toggle('studybook-mode', tab === 'studybook');", 1)
    head, closing = html.rsplit("</script>", 1)
    return head + SCRIPT + "\n</script>" + closing
