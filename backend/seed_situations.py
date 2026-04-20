"""Seed 20 situation-based questions from Trinn 4 Trafikalt PDF.

Category: Situations
Difficulty: medium

Questions kept as original text from the PDF; options crafted to be
pedagogically realistic (1 correct, 3 realistic but wrong).
"""
import asyncio, os, uuid
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

LETTERS = ["A", "B", "C", "D"]

# Each item: question in 3 langs, 4 options, correct letter, explanation
RAW = [
    {
        "q": {
            "no": "Hva legger du i begrepet \"kjøredyktighet\"?",
            "th": "คำว่า \"ความสามารถในการขับขี่\" หมายถึงอะไร?",
            "en": "What does the term 'driving competence' mean?"
        },
        "opts": [
            {"no": "Å være i stand til å kjøre trygt, aktsomt og hensynsfullt", "th": "สามารถขับขี่อย่างปลอดภัย ระมัดระวัง และมีน้ำใจ", "en": "Being able to drive safely, alertly and considerately"},
            {"no": "Å ha høyt førerkort og rask bil", "th": "มีใบขับขี่ระดับสูงและรถเร็ว", "en": "Having a high-class license and a fast car"},
            {"no": "Å kunne kjøre fort uten å bli tatt", "th": "สามารถขับเร็วโดยไม่ถูกจับ", "en": "Being able to drive fast without getting caught"},
            {"no": "Å ha kjørt bil i mange år", "th": "ขับรถมาหลายปีแล้ว", "en": "Having driven for many years"},
        ],
        "correct": "A",
        "expl": {"no": "Kjøredyktighet handler om å være trygg, aktsom og hensynsfull – ikke om erfaring alene.", "th": "ความสามารถในการขับขี่คือการขับอย่างปลอดภัยและมีน้ำใจ ไม่ใช่แค่ประสบการณ์", "en": "Driving competence is about safety, alertness and consideration – not just years."}
    },
    {
        "q": {
            "no": "Hvordan får du oversikt?",
            "th": "คุณจะสร้างภาพรวมของจราจรอย่างไร?",
            "en": "How do you get an overview of traffic?"
        },
        "opts": [
            {"no": "Ved å se langt fram, til sidene, i speilene og bruke blindsonekontroll", "th": "มองไปไกลด้านหน้า มองข้าง มองกระจก และตรวจจุดอับสายตา", "en": "Look far ahead, side-to-side, mirrors and check blind spots"},
            {"no": "Ved å se rett ned foran panseret", "th": "มองแค่หน้ารถ", "en": "Just look at the hood"},
            {"no": "Ved å stole på GPS-en", "th": "เชื่อ GPS", "en": "Trust the GPS"},
            {"no": "Ved å kjøre sakte", "th": "ขับช้าๆ", "en": "By driving slowly"},
        ],
        "correct": "A",
        "expl": {"no": "God oversikt krever aktiv bruk av blikket – fram, til sidene, i speilene og blindsoner.", "th": "ต้องใช้สายตาอย่างตื่นตัวทุกทิศทาง", "en": "Active scanning in all directions is needed."}
    },
    {
        "q": {
            "no": "Gul og blå bil kolliderer – hvem skal betale skadene?",
            "th": "รถเหลืองและรถน้ำเงินชนกัน ใครต้องจ่าย?",
            "en": "Yellow and blue cars collide – who pays?"
        },
        "opts": [
            {"no": "Den som har skyld i ulykken (forsikringen vurderer)", "th": "ฝ่ายผิดตามที่ประกันประเมิน", "en": "The party at fault (insurance decides)"},
            {"no": "Alltid den yngste sjåføren", "th": "คนขับอายุน้อยสุดเสมอ", "en": "Always the youngest driver"},
            {"no": "Alltid begge sjåførene likt", "th": "แบ่งครึ่งเสมอ", "en": "Always split 50/50"},
            {"no": "Ingen – staten dekker", "th": "ไม่มีใคร รัฐดูแล", "en": "Nobody – the state pays"},
        ],
        "correct": "A",
        "expl": {"no": "Skyldspørsmålet avgjør dekning. Forsikringsselskapene vurderer hvem som hadde vikeplikt eller kjørte feil.", "th": "ขึ้นอยู่กับความผิด ประกันจะประเมิน", "en": "Liability determines payment; insurance assesses fault."}
    },
    {
        "q": {
            "no": "Hva bør skiltet \"Gangfelt\" bety for en fører?",
            "th": "ป้าย \"ทางม้าลาย\" ควรหมายถึงอะไรสำหรับคนขับ?",
            "en": "What should a 'Pedestrian crossing' sign mean to a driver?"
        },
        "opts": [
            {"no": "Være ekstra oppmerksom og klar til å stoppe for gående", "th": "ระวังและพร้อมหยุดให้คนข้าม", "en": "Be extra alert and ready to stop for pedestrians"},
            {"no": "Øke farten for å passere fort", "th": "เร่งผ่านเร็วๆ", "en": "Speed up to pass quickly"},
            {"no": "Bruke horn for å varsle", "th": "บีบแตรเตือน", "en": "Use the horn"},
            {"no": "Bare bremse hvis noen allerede går", "th": "เบรกเฉพาะถ้ามีคนเดินอยู่แล้ว", "en": "Only brake if someone is already crossing"},
        ],
        "correct": "A",
        "expl": {"no": "Gangfelt krever at du er forberedt på å stoppe – også før noen har gått ut i feltet.", "th": "ต้องพร้อมหยุดก่อนเสมอ", "en": "Be prepared to stop, even before someone steps into the crossing."}
    },
    {
        "q": {
            "no": "Hvor mye vanskeligere blir det å stoppe bilen dersom du øker farten tre ganger?",
            "th": "หากเพิ่มความเร็วเป็น 3 เท่า ระยะหยุดจะเปลี่ยนอย่างไร?",
            "en": "How much harder is it to stop if you triple your speed?"
        },
        "opts": [
            {"no": "9 ganger lengre bremselengde", "th": "ระยะเบรกยาวขึ้น 9 เท่า", "en": "9× longer braking distance"},
            {"no": "3 ganger lengre", "th": "3 เท่า", "en": "3× longer"},
            {"no": "2 ganger lengre", "th": "2 เท่า", "en": "2× longer"},
            {"no": "Ingen forskjell", "th": "ไม่ต่าง", "en": "No difference"},
        ],
        "correct": "A",
        "expl": {"no": "Bremselengden vokser med fartens kvadrat. Tredobbel fart gir 9× lengre bremselengde.", "th": "ระยะเบรกเป็นสัดส่วนกับความเร็วกำลังสอง", "en": "Braking distance is proportional to speed squared (3² = 9)."}
    },
    {
        "q": {
            "no": "Du skal til venstre – hvem har du vikeplikt for?",
            "th": "เมื่อเลี้ยวซ้าย ต้องให้ทางใครบ้าง?",
            "en": "Turning left – who do you yield to?"
        },
        "opts": [
            {"no": "Møtende trafikk og gående/syklende som krysser", "th": "รถสวน คนเดิน และจักรยานที่ข้าม", "en": "Oncoming traffic and crossing pedestrians/cyclists"},
            {"no": "Kun biler bak deg", "th": "เฉพาะรถด้านหลัง", "en": "Only cars behind you"},
            {"no": "Ingen – du har alltid forkjørsrett", "th": "ไม่ต้อง คุณมีสิทธิ์เสมอ", "en": "Nobody – you always have priority"},
            {"no": "Kun store kjøretøy", "th": "เฉพาะรถใหญ่", "en": "Only large vehicles"},
        ],
        "correct": "A",
        "expl": {"no": "Ved venstresving har du vikeplikt for møtende, og for gående/syklende som krysser vegen du svinger inn i.", "th": "ต้องให้ทางรถสวนและคนข้าม", "en": "Yield to oncoming traffic and crossing pedestrians/cyclists."}
    },
    {
        "q": {
            "no": "Du skal følge forkjørsveien – er det nødvendig å blinke?",
            "th": "ขับตรงตามถนนสายหลัก ต้องให้สัญญาณไฟเลี้ยวไหม?",
            "en": "Following the main (priority) road – do you need to indicate?"
        },
        "opts": [
            {"no": "Nei, når du følger forkjørsveien uten å skifte retning", "th": "ไม่ต้อง ถ้าขับตามเส้นทางหลักโดยไม่เปลี่ยนทิศ", "en": "No, when staying on the priority road without changing direction"},
            {"no": "Ja, alltid i kryss", "th": "ใช่ ทุกทางแยก", "en": "Yes, always at junctions"},
            {"no": "Bare på motorvei", "th": "เฉพาะมอเตอร์เวย์", "en": "Only on motorways"},
            {"no": "Bare om natten", "th": "เฉพาะกลางคืน", "en": "Only at night"},
        ],
        "correct": "A",
        "expl": {"no": "Blinklys brukes ved retningsendring. Å følge forkjørsveien er ikke en retningsendring.", "th": "ไฟเลี้ยวใช้เมื่อเปลี่ยนทิศ", "en": "Indicators signal direction changes – not for following the same road."}
    },
    {
        "q": {
            "no": "Du sitter på med din beste venn. Dere er sent ute og farten kommer opp i 150 km/t. Hva gjør du?",
            "th": "เพื่อนขับเร็ว 150 กม./ชม. เพราะจะไปให้ทัน คุณควรทำอย่างไร?",
            "en": "Your friend drives 150 km/h because you're late. What do you do?"
        },
        "opts": [
            {"no": "Be vennen senke farten – sikkerhet først", "th": "ขอให้ชะลอ ความปลอดภัยสำคัญที่สุด", "en": "Ask them to slow down – safety first"},
            {"no": "Heie på og oppfordre til mer fart", "th": "เชียร์ให้เร็วขึ้น", "en": "Cheer them on to go faster"},
            {"no": "Ta bildet og legge ut på sosiale medier", "th": "ถ่ายรูปลงโซเชียล", "en": "Take photos for social media"},
            {"no": "Lukke øynene og håpe det går bra", "th": "หลับตาและหวังว่าจะรอด", "en": "Close your eyes and hope"},
        ],
        "correct": "A",
        "expl": {"no": "Som passasjer har du ansvar for å si fra. Å nå kinoen er ikke verdt risikoen.", "th": "ผู้โดยสารต้องพูดขึ้น", "en": "As a passenger you should speak up – no movie is worth the risk."}
    },
    {
        "q": {
            "no": "Hvilke problemer kan kjøring i mørket gi?",
            "th": "ขับรถตอนกลางคืนมีปัญหาอะไรบ้าง?",
            "en": "What problems can night driving cause?"
        },
        "opts": [
            {"no": "Redusert sikt, blending og vanskeligere å bedømme avstander/fart", "th": "ทัศนวิสัยต่ำ แสงแยง ประเมินระยะและความเร็วยาก", "en": "Reduced visibility, glare, harder to judge distance/speed"},
            {"no": "Bedre sikt på grunn av refleks", "th": "มองเห็นดีกว่าเพราะแสงสะท้อน", "en": "Better visibility due to reflections"},
            {"no": "Raskere reaksjon", "th": "ตอบสนองเร็วขึ้น", "en": "Faster reactions"},
            {"no": "Ingen problemer", "th": "ไม่มีปัญหา", "en": "No problems"},
        ],
        "correct": "A",
        "expl": {"no": "Mørke reduserer synsfeltet, gir blending fra møtende og gjør avstandsbedømming vanskelig.", "th": "กลางคืนทำให้มองยากและประเมินระยะผิด", "en": "Darkness reduces visual range, causes glare and makes distance judgement hard."}
    },
    {
        "q": {
            "no": "Hva gjør du som førstemann på ulykkesstedet?",
            "th": "คุณถึงจุดเกิดเหตุคนแรก ควรทำอะไร?",
            "en": "What do you do as the first person at an accident scene?"
        },
        "opts": [
            {"no": "Sikre stedet, ring nødnummer 113, hjelpe skadde uten å flytte dem unødig", "th": "ป้องกันสถานที่ โทร 113 ช่วยผู้บาดเจ็บโดยไม่ขยับถ้าไม่จำเป็น", "en": "Secure the scene, call emergency (113), help injured without unnecessary movement"},
            {"no": "Kjøre forbi og ringe fra jobb", "th": "ขับผ่านแล้วค่อยโทรจากที่ทำงาน", "en": "Drive past and call from work"},
            {"no": "Ta bilder først", "th": "ถ่ายรูปก่อน", "en": "Take photos first"},
            {"no": "Flytte skadde til siden av veien", "th": "ย้ายคนเจ็บไปข้างถนน", "en": "Move the injured to the roadside"},
        ],
        "correct": "A",
        "expl": {"no": "Prioritering: sikre → varsle (113) → hjelpe. Ikke flytt skadde med mindre det er fare.", "th": "ป้องกัน – แจ้ง – ช่วย ตามลำดับ", "en": "Order: secure → alert → assist. Don't move injured unless unavoidable."}
    },
    {
        "q": {
            "no": "Den gule bilen foran deg står i ditt kjørefelt. Hva gjør du?",
            "th": "รถเหลืองจอดในเลนคุณ ควรทำอย่างไร?",
            "en": "The yellow car is stopped in your lane. What do you do?"
        },
        "opts": [
            {"no": "Senke fart, sjekke speil/blindsone og passere når det er klart", "th": "ชะลอ เช็คกระจก/จุดอับ แล้วแซงเมื่อปลอดภัย", "en": "Slow, check mirrors/blind spot, pass when clear"},
            {"no": "Holde farten og tute", "th": "ความเร็วคงเดิมและบีบแตร", "en": "Keep speed and honk"},
            {"no": "Bremse hardt og stoppe tett bak", "th": "เบรกแรงและจอดชิด", "en": "Brake hard and stop right behind"},
            {"no": "Kjøre rundt uten å blinke", "th": "อ้อมโดยไม่เปิดไฟเลี้ยว", "en": "Pass without signaling"},
        ],
        "correct": "A",
        "expl": {"no": "Tilpass fart, vurder forbikjøring med speil- og blindsonekontroll, og bruk blinklys.", "th": "ชะลอ ตรวจ และให้สัญญาณ", "en": "Slow, check, signal – then pass."}
    },
    {
        "q": {
            "no": "Hvorfor avtar risikoen for å bli involvert i ulykker etter hvert som en person får kjøreerfaring?",
            "th": "ทำไมคนขับที่มีประสบการณ์จึงเสี่ยงน้อยลง?",
            "en": "Why does accident risk decrease with driving experience?"
        },
        "opts": [
            {"no": "Bedre risikoforståelse, automatiserte handlinger og erfaring med varierte situasjoner", "th": "เข้าใจความเสี่ยง ตอบสนองอัตโนมัติ และเจอหลายสถานการณ์", "en": "Better risk awareness, automated actions, experience with varied situations"},
            {"no": "Eldre biler er tryggere", "th": "รถเก่ากว่าปลอดภัยกว่า", "en": "Older cars are safer"},
            {"no": "Eldre sjåfører kjører aldri fort", "th": "คนขับอายุมากไม่ขับเร็ว", "en": "Older drivers never go fast"},
            {"no": "Politiet gir rabatt", "th": "ตำรวจให้ส่วนลด", "en": "Police give discounts"},
        ],
        "correct": "A",
        "expl": {"no": "Erfaring gir bedre oppfattelse, valg og handlinger – det senker risiko.", "th": "ประสบการณ์พัฒนาการตัดสินใจ", "en": "Experience improves perception, decisions and actions."}
    },
    {
        "q": {
            "no": "Hvorfor er det vanskelig å konsentrere seg om flere oppgaver samtidig?",
            "th": "ทำไมการทำหลายอย่างพร้อมกันจึงยาก?",
            "en": "Why is multitasking hard while driving?"
        },
        "opts": [
            {"no": "Hjernen bytter fokus og gir redusert oppmerksomhet på viktige ting", "th": "สมองสลับความสนใจ ทำให้ละเลยสิ่งสำคัญ", "en": "The brain switches focus, attention drops on critical things"},
            {"no": "Ørene hører bare én ting", "th": "หูได้ยินครั้งละอย่าง", "en": "Ears only hear one thing"},
            {"no": "Det er ikke vanskelig", "th": "ไม่ยาก", "en": "It isn't hard"},
            {"no": "Bare kvinner klarer det", "th": "เฉพาะผู้หญิงทำได้", "en": "Only women can do it"},
        ],
        "correct": "A",
        "expl": {"no": "Oppmerksomheten fordeles og viktige signaler kan overses. Derfor er mobilbruk farlig under kjøring.", "th": "สมาธิถูกแบ่ง ข้อมูลสำคัญถูกมองข้าม", "en": "Attention is divided and critical cues are missed."}
    },
    {
        "q": {
            "no": "Er det bilen som velter, eller er det sjåføren som velter bilen?",
            "th": "รถพลิกเอง หรือคนขับเป็นคนทำให้พลิก?",
            "en": "Is it the car that rolls, or the driver who rolls the car?"
        },
        "opts": [
            {"no": "Sjåføren – valg og handlinger bak rattet avgjør", "th": "คนขับ เพราะการตัดสินใจคือปัจจัยหลัก", "en": "The driver – choices and actions are the cause"},
            {"no": "Bilen – den er skyldig", "th": "รถเอง", "en": "The car is to blame"},
            {"no": "Veien – asfalten er for dårlig", "th": "ถนนไม่ดี", "en": "The road surface is at fault"},
            {"no": "Dekkprodusenten", "th": "ผู้ผลิตยาง", "en": "The tire maker"},
        ],
        "correct": "A",
        "expl": {"no": "Fart, styring og valg ligger hos sjåføren. Bilen reagerer på det sjåføren gjør.", "th": "คนขับคือตัวกำหนด", "en": "Speed, steering and choices are the driver's."}
    },
    {
        "q": {
            "no": "Hvorfor må vi ha fartsgrenser når vegtrafikkloven allerede sier vi skal være hensynsfulle?",
            "th": "ทำไมยังต้องมีขีดจำกัดความเร็ว ทั้งที่กฎหมายบอกให้ขับอย่างระมัดระวังอยู่แล้ว?",
            "en": "Why speed limits if the traffic law already requires care?"
        },
        "opts": [
            {"no": "Fartsgrenser gir felles, tydelige rammer og reduserer skader i ulykker", "th": "ทำให้มีมาตรฐานเดียวกันและลดความรุนแรงของอุบัติเหตุ", "en": "They provide clear shared rules and reduce crash severity"},
            {"no": "For å gi staten inntekter fra bøter", "th": "เพื่อเก็บค่าปรับ", "en": "To generate fine revenue"},
            {"no": "Bare for å irritere sjåfører", "th": "เพื่อกวนใจคนขับ", "en": "Just to annoy drivers"},
            {"no": "Fordi politikere liker regler", "th": "เพราะนักการเมืองชอบกฎ", "en": "Politicians like rules"},
        ],
        "correct": "A",
        "expl": {"no": "Fart påvirker bremselengde, reaksjonstid og skadeomfang. Felles grenser gir forutsigbarhet.", "th": "ความเร็วมีผลต่อระยะเบรกและความรุนแรง", "en": "Speed affects stopping distance and crash outcomes; shared limits aid predictability."}
    },
    {
        "q": {
            "no": "Fra hvilken side trenger du størst luke ved forbikjøring?",
            "th": "เมื่อแซง ต้องเผื่อระยะด้านใดมากที่สุด?",
            "en": "When overtaking, which side needs the biggest gap?"
        },
        "opts": [
            {"no": "Foran (mot møtende trafikk) – du må rekke å fullføre forbikjøringen trygt", "th": "ด้านหน้า เพราะต้องแซงให้เสร็จก่อนรถสวน", "en": "The front (toward oncoming traffic) – to complete safely"},
            {"no": "Bak", "th": "ด้านหลัง", "en": "The rear"},
            {"no": "Til høyre", "th": "ด้านขวา", "en": "The right"},
            {"no": "Ingen – forbikjøring er alltid trygt", "th": "ไม่ต้อง แซงปลอดภัยเสมอ", "en": "None – overtaking is always safe"},
        ],
        "correct": "A",
        "expl": {"no": "Kritisk luke er foran – du må fullføre forbikjøringen før møtende når deg.", "th": "ด้านหน้าสำคัญที่สุด", "en": "The forward gap is critical – finish before oncoming arrives."}
    },
    {
        "q": {
            "no": "Hvilke konsekvenser kan \"misforstått kommunikasjon\" få i trafikken?",
            "th": "การสื่อสารผิดพลาดในจราจรอาจทำให้เกิดอะไร?",
            "en": "Consequences of miscommunication in traffic?"
        },
        "opts": [
            {"no": "Farlige situasjoner og ulykker mellom trafikanter", "th": "สถานการณ์อันตรายและอุบัติเหตุ", "en": "Dangerous situations and crashes between road users"},
            {"no": "Bedre flyt", "th": "จราจรคล่องขึ้น", "en": "Better flow"},
            {"no": "Kortere reisetid", "th": "เดินทางเร็วขึ้น", "en": "Shorter trips"},
            {"no": "Ingen ting", "th": "ไม่มีอะไร", "en": "Nothing"},
        ],
        "correct": "A",
        "expl": {"no": "Blikk, blink og tegn må forstås riktig for å unngå sammenstøt.", "th": "สัญญาณต้องเข้าใจตรงกัน", "en": "Eye contact, signals and gestures must be understood correctly."}
    },
    {
        "q": {
            "no": "Hva skal du rette deg etter i trafikken?",
            "th": "ในการจราจร คุณต้องทำตามอะไร?",
            "en": "What do you follow in traffic?"
        },
        "opts": [
            {"no": "Lover, skilt, oppmerking, trafikklys og politimanns tegn", "th": "กฎหมาย ป้าย เส้น ไฟจราจร และสัญญาณตำรวจ", "en": "Laws, signs, markings, traffic lights and police signals"},
            {"no": "Bare GPS-stemmen", "th": "เฉพาะ GPS", "en": "Only the GPS voice"},
            {"no": "Din egen magefølelse", "th": "ลางสังหรณ์", "en": "Your gut feeling"},
            {"no": "Det vennene sier på telefon", "th": "ที่เพื่อนบอกทางโทรศัพท์", "en": "What friends say on the phone"},
        ],
        "correct": "A",
        "expl": {"no": "Rekkefølge: politimanns tegn > trafikklys > skilt > oppmerking > generelle regler.", "th": "ลำดับ: ตำรวจ > ไฟ > ป้าย > เส้น > กฎทั่วไป", "en": "Order: police > lights > signs > markings > general rules."}
    },
    {
        "q": {
            "no": "Hvordan bør du plassere deg i forhold til andre trafikanter?",
            "th": "ควรวางตำแหน่งรถอย่างไรเมื่อมีคนอื่น?",
            "en": "How should you position yourself relative to other road users?"
        },
        "opts": [
            {"no": "Så du er godt synlig og har trygg avstand i alle retninger", "th": "ให้มองเห็นชัดและเว้นระยะทุกทิศ", "en": "Visible and with safe distance in every direction"},
            {"no": "Tett på bilen foran", "th": "ชิดรถคันหน้า", "en": "Right on the car in front"},
            {"no": "I blindsonen til tunge kjøretøy", "th": "ในจุดอับของรถใหญ่", "en": "In trucks' blind spots"},
            {"no": "Midt mellom to felt", "th": "คร่อมเลน", "en": "Straddling lanes"},
        ],
        "correct": "A",
        "expl": {"no": "Plassering skal gi deg tid og rom til å reagere – og gjøre deg synlig for andre.", "th": "ต้องมองเห็นและมีที่ว่างให้ตอบสนอง", "en": "Positioning gives you time, space and visibility."}
    },
    {
        "q": {
            "no": "Hva kan du gjøre dersom du nærmer deg en uoversiktlig sving med smal bro rett etter, og du ikke er kjent i området?",
            "th": "ใกล้โค้งมองไม่เห็น มีสะพานแคบถัดไป 30 ม. และคุณไม่คุ้นเส้นทาง ควรทำอย่างไร?",
            "en": "Approaching a blind curve with a narrow bridge right after it in unfamiliar area – what do you do?"
        },
        "opts": [
            {"no": "Senke farten godt og være klar til å stoppe", "th": "ลดความเร็วมากและเตรียมหยุด", "en": "Reduce speed significantly and be ready to stop"},
            {"no": "Holde full fart for å komme fort gjennom", "th": "เร่งผ่านให้ไว", "en": "Keep full speed"},
            {"no": "Bruke fjernlys som signal", "th": "เปิดไฟสูงเป็นสัญญาณ", "en": "Flash high beams"},
            {"no": "Kjøre midt i vegen", "th": "ขับกลางถนน", "en": "Drive down the middle"},
        ],
        "correct": "A",
        "expl": {"no": "Ukjent terreng + begrenset sikt + smal bro = lav fart og beredskap for å stoppe eller vike.", "th": "ต้องชะลอและพร้อมหยุด", "en": "Unknown + limited sight + narrow bridge = slow and prepared to stop."}
    },
]


async def main():
    assert len(RAW) == 20, f"Expected 20 questions, got {len(RAW)}"

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    inserted = 0
    skipped = 0

    for r in RAW:
        # Dedup check
        existing = await db.questions.find_one({"question.no": r["q"]["no"]})
        if existing:
            skipped += 1
            continue

        doc = {
            "id": str(uuid.uuid4()),
            "question": r["q"],
            "options": [{"id": LETTERS[i], "text": r["opts"][i]} for i in range(4)],
            "correctOptionId": r["correct"],
            "explanation": r["expl"],
            "bildeUrl": None,
            "category": "Situations",
            "difficulty": "medium",
            "active": True,
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "Trinn 4 Trafikalt PDF",
        }
        await db.questions.insert_one(doc)
        inserted += 1

    print(f"Inserted: {inserted}, Skipped: {skipped}")
    total = await db.questions.count_documents({})
    sit = await db.questions.count_documents({"category": "Situations"})
    print(f"Total questions: {total}")
    print(f"Situations category: {sit}")
    client.close()


asyncio.run(main())
