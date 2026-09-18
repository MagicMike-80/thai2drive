"""Interactive, web-only Studybook prototype for the existing Thai2Drive shell.

The module is intentionally self-contained: it installs markup, styling and
behaviour into ``WEBAPP_HTML`` without changing auth, billing, MongoDB or Expo.
"""

from __future__ import annotations

import json


def i18n(no: str, th: str, en: str) -> dict[str, str]:
    """Create a complete learner-facing translation value."""
    return {"no": no, "th": th, "en": en}


ASSETS = {
    "hazard": {
        "src": "/api/assets/thumbs/thumb_vikeplikt_7_4.jpg",
        "alt": i18n(
            "Norsk trafikksituasjon med flere mulige farer",
            "สถานการณ์จราจรในนอร์เวย์ที่มีอันตรายหลายจุด",
            "Norwegian traffic situation with several possible hazards",
        ),
    },
    "distance": {
        "src": "/api/assets/stopping-distance-road-v1.png",
        "alt": i18n(
            "Bil som ligger for tett bak bilen foran",
            "รถที่ขับตามรถคันหน้าใกล้เกินไป",
            "A car following the vehicle ahead too closely",
        ),
    },
    "right_of_way": {
        "src": "/api/assets/thumbs/thumb_vikeplikt_7_2a.jpg",
        "alt": i18n(
            "Kryss der en bil kommer fra høyre",
            "ทางแยกที่มีรถมาจากทางขวา",
            "An intersection where a car approaches from the right",
        ),
    },
    "bus": {
        "src": "/api/assets/thumbs/thumb_vikeplikt_7_5a_buss.jpg",
        "alt": i18n(
            "Buss som blinker ut fra holdeplass",
            "รถโดยสารเปิดไฟเลี้ยวออกจากป้าย",
            "A bus indicating to leave a bus stop",
        ),
    },
}


LESSONS = [
    {
        "id": "spot-hazard",
        "type": "spotHazard",
        "eyebrow": i18n("SE SITUASJONEN", "มองสถานการณ์", "SEE THE SITUATION"),
        "title": i18n("Hva oppdager du først?", "คุณเห็นอะไรก่อน?", "What do you notice first?"),
        "body": i18n(
            "Trykk på området der du forventer at en fare kan utvikle seg.",
            "แตะบริเวณที่คุณคิดว่าอันตรายอาจเกิดขึ้น",
            "Select the area where you expect a hazard could develop.",
        ),
        "asset": "hazard",
        "hazards": [
            {
                "x": 72,
                "y": 48,
                "label": i18n("Mulig konfliktområde", "จุดที่อาจเกิดความขัดแย้ง", "Possible conflict area"),
                "feedback": i18n(
                    "Bra sett. Se langt frem, beveg blikket og skaff deg oversikt.",
                    "เห็นได้ดี มองไปข้างหน้า ขยับสายตา และสำรวจภาพรวม",
                    "Good observation. Look far ahead, move your eyes and build an overview.",
                ),
            }
        ],
        "remember": i18n("Se langt frem. Beveg blikket. Få oversikt.", "มองไกล ขยับสายตา มองภาพรวม", "Look far ahead. Move your eyes. Build an overview."),
    },
    {
        "id": "distance",
        "type": "imageLesson",
        "eyebrow": i18n("LÆR", "เรียนรู้", "LEARN"),
        "title": i18n("FOR NÆR! 😬", "ใกล้เกินไป! 😬", "TOO CLOSE! 😬"),
        "body": i18n(
            "Bilen foran bremser plutselig. Avstand kjøper deg tid.",
            "รถคันหน้าเบรกกะทันหัน ระยะห่างช่วยให้คุณมีเวลา",
            "The car ahead brakes suddenly. Distance buys you time.",
        ),
        "asset": "distance",
        "flow": [
            i18n("SE", "มองเห็น", "SEE"),
            i18n("FORSTÅ", "เข้าใจ", "UNDERSTAND"),
            i18n("VELGE", "เลือก", "CHOOSE"),
            i18n("HANDLE", "ลงมือทำ", "ACT"),
        ],
        "remember": i18n("Mer avstand gir mer tid til å velge trygt.", "ระยะห่างมากขึ้นทำให้มีเวลาเลือกอย่างปลอดภัย", "More distance gives you more time to choose safely."),
    },
    {
        "id": "right-of-way",
        "type": "choice",
        "eyebrow": i18n("DIN TUR", "ตาคุณ", "YOUR MOVE"),
        "title": i18n("Hva gjør du?", "คุณจะทำอย่างไร?", "What do you do?"),
        "body": i18n(
            "Du møter en bil fra høyre i et kryss uten skilt.",
            "คุณพบรถมาจากทางขวาที่ทางแยกซึ่งไม่มีป้าย",
            "A car approaches from your right at an unsigned intersection.",
        ),
        "asset": "right_of_way",
        "options": [
            {"id": "drive", "label": i18n("KJØR", "ขับไป", "DRIVE")},
            {"id": "wait", "label": i18n("VENT", "รอ", "WAIT")},
        ],
        "correct": "wait",
        "correctFeedback": i18n(
            "Riktig. Bilen fra høyre er kongen. Du venter.",
            "ถูกต้อง รถจากทางขวามีสิทธิ์ไปก่อน คุณต้องรอ",
            "Correct. The car from the right goes first. You wait.",
        ),
        "wrongFeedback": i18n(
            "WOAH 😅 Se til høyre én gang til. Der kommer bilen du må vente på.",
            "เดี๋ยวก่อน 😅 มองทางขวาอีกครั้ง มีรถที่คุณต้องรอ",
            "WOAH 😅 Look right once more. That is the car you must wait for.",
        ),
        "remember": i18n("Uten skilt eller lys: vikeplikt for trafikk fra høyre.", "เมื่อไม่มีป้ายหรือไฟ: ให้ทางรถจากขวา", "Without signs or lights: yield to traffic from the right."),
    },
    {
        "id": "bus",
        "type": "choice",
        "eyebrow": i18n("FINN DETALJEN", "หารายละเอียด", "FIND THE DETAIL"),
        "title": i18n("Bussen vil ut. Hva gjør DU?", "รถโดยสารต้องการออก คุณจะทำอย่างไร?", "The bus wants to leave. What do YOU do?"),
        "body": i18n(
            "Bussen blinker ut fra holdeplassen. Fartsgrensen er 50 km/t.",
            "รถโดยสารเปิดไฟเลี้ยวออกจากป้าย จำกัดความเร็ว 50 กม./ชม.",
            "The bus indicates to leave the stop. The speed limit is 50 km/h.",
        ),
        "asset": "bus",
        "badge": i18n("50 km/t", "50 กม./ชม.", "50 km/h"),
        "options": [
            {"id": "brake", "label": i18n("BREMS", "เบรก", "BRAKE")},
            {"id": "drive", "label": i18n("KJØR", "ขับไป", "DRIVE")},
        ],
        "correct": "brake",
        "correctFeedback": i18n(
            "Riktig. Ved 60 km/t eller lavere skal du gi bussen mulighet til å kjøre ut.",
            "ถูกต้อง เมื่อจำกัดความเร็วไม่เกิน 60 กม./ชม. คุณต้องให้รถโดยสารออกจากป้าย",
            "Correct. At 60 km/h or less, you must let the bus leave the stop.",
        ),
        "wrongFeedback": i18n(
            "Se på fartsgrensen én gang til. Her er den 50 km/t.",
            "ดูป้ายจำกัดความเร็วอีกครั้ง ที่นี่คือ 50 กม./ชม.",
            "Check the speed limit once more. It is 50 km/h here.",
        ),
        "remember": i18n("Fartsgrensen kan endre hvem som skal vente.", "ความเร็วที่กำหนดอาจเปลี่ยนว่าใครต้องรอ", "The speed limit can change who must wait."),
    },
    {
        "id": "road-check",
        "type": "roadCheck",
        "eyebrow": i18n("ROAD CHECK ⚡", "ROAD CHECK ⚡", "ROAD CHECK ⚡"),
        "title": i18n("Klar for neste nivå?", "พร้อมสำหรับระดับต่อไปไหม?", "Ready for the next level?"),
        "body": i18n("Tre raske situasjoner fra det du nettopp lærte.", "สามสถานการณ์สั้น ๆ จากสิ่งที่คุณเพิ่งเรียน", "Three quick situations from what you just learned."),
        "questions": [
            {
                "label": i18n("1/3 FINN FAREN 👀", "1/3 หาอันตราย 👀", "1/3 SPOT IT 👀"),
                "prompt": i18n("Hvor bør blikket ditt være?", "คุณควรมองไปที่ไหน?", "Where should you look?"),
                "options": [
                    {"id": "ahead", "label": i18n("Langt frem", "มองไกลไปข้างหน้า", "Far ahead")},
                    {"id": "hood", "label": i18n("Rett foran panseret", "ตรงหน้าฝากระโปรง", "Just over the bonnet")},
                ],
                "correct": "ahead",
                "explanation": i18n("Se langt frem for å oppdage farer tidlig.", "มองไกลเพื่อพบอันตรายตั้งแต่เนิ่น ๆ", "Look far ahead to detect hazards early."),
            },
            {
                "label": i18n("2/3 DITT VALG 🚗", "2/3 การตัดสินใจของคุณ 🚗", "2/3 YOUR MOVE 🚗"),
                "prompt": i18n("Bil fra høyre, ingen skilt. Hva gjør du?", "มีรถจากขวา ไม่มีป้าย คุณทำอย่างไร?", "Car from the right, no signs. What do you do?"),
                "options": [
                    {"id": "wait", "label": i18n("Vent", "รอ", "Wait")},
                    {"id": "drive", "label": i18n("Kjør", "ขับไป", "Drive")},
                ],
                "correct": "wait",
                "explanation": i18n("Høyreregelen betyr at du venter.", "กฎรถทางขวาหมายความว่าคุณต้องรอ", "The right-hand rule means you wait."),
            },
            {
                "label": i18n("3/3 HVA ENDRET SEG? 🧠", "3/3 อะไรเปลี่ยนไป? 🧠", "3/3 WHAT CHANGED? 🧠"),
                "prompt": i18n("Bussen blinker ut ved 50 km/t. Hva er viktig?", "รถโดยสารเปิดไฟเลี้ยวออกที่ 50 กม./ชม. อะไรสำคัญ?", "The bus indicates at 50 km/h. What matters?"),
                "options": [
                    {"id": "limit", "label": i18n("Fartsgrensen", "ป้ายจำกัดความเร็ว", "The speed limit")},
                    {"id": "colour", "label": i18n("Fargen på bussen", "สีของรถโดยสาร", "The bus colour")},
                ],
                "correct": "limit",
                "explanation": i18n("Ved 60 km/t eller lavere skal du gi bussen plass.", "เมื่อไม่เกิน 60 กม./ชม. คุณต้องให้ทางรถโดยสาร", "At 60 km/h or less, you must give the bus room."),
            },
        ],
    },
]


COPY = {
    "brand": i18n("THAI2DRIVE STUDIEBOKEN", "หนังสือเรียน THAI2DRIVE", "THAI2DRIVE STUDY BOOK"),
    "subtitle": i18n("Fra elev til trygg sjåfør", "จากผู้เรียนสู่ผู้ขับขี่ที่ปลอดภัย", "From learner to safe driver"),
    "continue": i18n("Fortsett der du slapp", "เรียนต่อจากจุดเดิม", "Continue where you left off"),
    "start": i18n("Start læringen", "เริ่มเรียน", "Start learning"),
    "progress": i18n("Progresjon", "ความคืบหน้า", "Progress"),
    "completed": i18n("fullført", "เสร็จแล้ว", "completed"),
    "chapters": i18n("Læringsløp", "เส้นทางการเรียน", "Learning path"),
    "backHome": i18n("Oversikt", "ภาพรวม", "Overview"),
    "previous": i18n("Forrige", "ก่อนหน้า", "Previous"),
    "next": i18n("Lær videre", "เรียนต่อ", "Keep learning"),
    "understood": i18n("Jeg forstår", "ฉันเข้าใจ", "I understand"),
    "choose": i18n("Velg et svar", "เลือกคำตอบ", "Choose an answer"),
    "correct": i18n("Riktig", "ถูกต้อง", "Correct"),
    "wrong": i18n("Se én gang til", "ดูอีกครั้ง", "Look once more"),
    "remember": i18n("HUSK", "จำไว้", "REMEMBER"),
    "roadCleared": i18n("ROAD CHECK BESTÅTT", "ผ่าน ROAD CHECK", "ROAD CHECK CLEARED"),
    "roadRetry": i18n("Ta en rask repetisjon", "ทบทวนอย่างรวดเร็ว", "Take a quick review"),
    "review": i18n("Repeter", "ทบทวน", "Review"),
    "finish": i18n("Til oversikten", "กลับไปภาพรวม", "Back to overview"),
    "imageMissing": i18n("Situasjonsbildet kommer snart", "ภาพสถานการณ์จะมาเร็ว ๆ นี้", "Situation image coming soon"),
    "storageError": i18n("Progresjonen kunne ikke lagres på denne enheten.", "ไม่สามารถบันทึกความคืบหน้าในอุปกรณ์นี้ได้", "Progress could not be saved on this device."),
    "contentError": i18n("Denne læringssiden kan ikke vises nå.", "ไม่สามารถแสดงบทเรียนนี้ได้ในขณะนี้", "This learning screen cannot be displayed right now."),
}


CSS = r"""
/* Interactive Studybook v1 */
#screenStudybook{padding:0;background:#071225;overflow-y:auto;color:var(--text)}
.sbx-shell{width:min(760px,100%);min-height:100%;margin:0 auto;padding:18px 16px 96px}
.sbx-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px}.sbx-top button{min-height:44px}
.sbx-logo{font-size:.72rem;font-weight:900;letter-spacing:.13em;color:#60e6ff}.sbx-lang{color:var(--muted);font-size:.75rem}
.sbx-hero{padding:24px;border-radius:24px;background:radial-gradient(circle at 90% 0,#b82eff33,transparent 38%),linear-gradient(145deg,#102b4b,#101a36);border:1px solid #2c6383;box-shadow:0 18px 45px #0006}
.sbx-hero h1{font-size:clamp(1.7rem,7vw,2.7rem);line-height:1.02;margin:8px 0}.sbx-hero p{color:#c7d7ea;margin:0 0 20px;font-size:1rem}
.sbx-progress-row{display:flex;justify-content:space-between;gap:12px;font-size:.78rem;margin-bottom:7px}.sbx-track{height:8px;background:#ffffff16;border-radius:99px;overflow:hidden}.sbx-fill{height:100%;background:linear-gradient(90deg,#00d9ff,#a637ff);border-radius:inherit;transition:width .25s}
.sbx-primary,.sbx-choice,.sbx-secondary{border:0;border-radius:14px;min-height:48px;padding:12px 18px;font:inherit;font-weight:850;cursor:pointer}.sbx-primary{background:#ff8a1f;color:#111;box-shadow:0 0 22px #ff8a1f44}.sbx-secondary{background:#142844;color:#eaf7ff;border:1px solid #3a5c7d}.sbx-primary:focus-visible,.sbx-secondary:focus-visible,.sbx-choice:focus-visible,.sbx-hotspot:focus-visible{outline:3px solid #62e8ff;outline-offset:3px}
.sbx-section-title{font-size:1rem;margin:28px 0 12px}.sbx-map{display:grid;gap:10px}.sbx-map-card{display:grid;grid-template-columns:44px 1fr auto;align-items:center;gap:12px;padding:14px;border-radius:16px;background:#101d34;border:1px solid #273c58}.sbx-map-card strong,.sbx-map-card small{display:block}.sbx-map-card small{color:var(--muted);margin-top:3px}.sbx-map-num{width:40px;height:40px;display:grid;place-items:center;border-radius:12px;background:#142f4e;color:#69ebff;font-weight:900}.sbx-map-status{color:#ffad65;font-size:.74rem}
.sbx-card{overflow:hidden;border-radius:24px;background:#101d34;border:1px solid #2b4665;box-shadow:0 18px 45px #0005}.sbx-copy{padding:20px}.sbx-eyebrow{font-size:.72rem;letter-spacing:.15em;font-weight:900;color:#65eaff}.sbx-copy h1{font-size:clamp(1.55rem,6vw,2.3rem);line-height:1.08;margin:8px 0}.sbx-copy>p{line-height:1.55;color:#c7d5e6}
.sbx-image{position:relative;min-height:230px;background:#0b1728}.sbx-image img{display:block;width:100%;height:100%;min-height:230px;max-height:420px;object-fit:cover}.sbx-placeholder{min-height:230px;display:grid;place-items:center;padding:24px;text-align:center;color:#aabbd0}.sbx-badge{position:absolute;top:14px;right:14px;background:#d42934;color:#fff;border:4px solid #fff;border-radius:99px;padding:11px;font-weight:900}
.sbx-hotspot{position:absolute;width:58px;height:58px;border:3px solid #65eaff;border-radius:50%;background:#00d9ff30;box-shadow:0 0 0 8px #00d9ff20,0 0 25px #00d9ff;cursor:pointer;transform:translate(-50%,-50%)}.sbx-hotspot.found{background:#ff8a1f88;border-color:#fff;box-shadow:0 0 0 8px #ff8a1f33}
.sbx-flow{display:grid;grid-template-columns:repeat(4,1fr);gap:5px;margin-top:18px}.sbx-flow span{text-align:center;padding:10px 3px;border-radius:10px;background:#142b47;color:#aeefff;font-size:.65rem;font-weight:850}.sbx-flow span+span:before{content:'›';color:#ff9a3c;margin-right:5px}
.sbx-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}.sbx-choice{background:#152b49;color:#fff;border:2px solid #365a7e}.sbx-choice:hover{border-color:#65eaff}.sbx-choice.correct{background:#194b50;border-color:#65eaff}.sbx-choice.wrong{background:#51233a;border-color:#ff648c}
.sbx-feedback{margin-top:16px;padding:14px;border-left:4px solid #ff8a1f;border-radius:8px;background:#0b1728;line-height:1.5}.sbx-remember{margin-top:16px;padding:14px;border-radius:14px;background:#60207235;border:1px solid #bd52df66}.sbx-remember strong{display:block;color:#e99aff;font-size:.7rem;letter-spacing:.13em;margin-bottom:5px}
.sbx-footer{display:flex;justify-content:space-between;gap:10px;margin-top:16px}.sbx-footer button:disabled{opacity:.38;cursor:not-allowed}.sbx-road-head{display:flex;justify-content:space-between;gap:8px;align-items:center}.sbx-road-step{color:#ffae68;font-weight:900}.sbx-result{text-align:center;padding:36px 20px}.sbx-score{font-size:3.2rem;font-weight:950;color:#65eaff;margin:16px 0}.sbx-status{min-height:22px;margin-top:12px;color:#ffb4c7}
@media(min-width:900px){#app.studybook-mode{width:min(980px,96vw);max-width:none;margin:auto;border-radius:18px}.sbx-shell{width:min(840px,100%);padding-top:28px}.sbx-image{min-height:360px}.sbx-image img{min-height:360px}}
@media(max-width:420px){.sbx-hero{padding:20px}.sbx-actions{grid-template-columns:1fr}.sbx-flow{grid-template-columns:1fr 1fr}.sbx-footer{position:sticky;bottom:72px;background:#071225e8;padding:10px 0}.sbx-logo{max-width:220px}}
@media(prefers-reduced-motion:reduce){.sbx-fill{transition:none}.sbx-hotspot{box-shadow:none}}
"""


SCREEN = r"""
<div class="screen" id="screenStudybook">
  <main class="sbx-shell" id="sbxRoot" aria-live="polite"></main>
</div>
"""


_DATA = json.dumps({"assets": ASSETS, "lessons": LESSONS, "copy": COPY}, ensure_ascii=False, separators=(",", ":"))

SCRIPT = r"""
var SBX_DATA = __SBX_DATA__;
var SBX_KEY = 't2d_studybook_progress_v1';
var sbxState = {view:'home',index:0,answered:false,roadIndex:0,roadAnswers:[],storageFailed:false};
function sbxEl(tag,cls,text){var el=document.createElement(tag);if(cls)el.className=cls;if(typeof text==='string')el.textContent=text;return el;}
function sbxL(value){if(!value || typeof value!=='object')return '';var text=value[appLang];return typeof text==='string'?text:'';}
function sbxCopy(key){return sbxL(SBX_DATA.copy[key]);}
function sbxDefaultProgress(){return {currentLesson:0,completedLessons:[],roadCheck:null,updatedAt:null};}
function sbxReadProgress(){try{var raw=_ls.get(SBX_KEY);var parsed=raw?JSON.parse(raw):sbxDefaultProgress();if(!parsed || !Array.isArray(parsed.completedLessons))return sbxDefaultProgress();return parsed;}catch(error){return sbxDefaultProgress();}}
function sbxSaveProgress(progress){try{progress.updatedAt=new Date().toISOString();_ls.set(SBX_KEY,JSON.stringify(progress));sbxState.storageFailed=false;}catch(error){sbxState.storageFailed=true;}}
function sbxComplete(id){var progress=sbxReadProgress();if(progress.completedLessons.indexOf(id)<0)progress.completedLessons.push(id);progress.currentLesson=Math.min(sbxState.index+1,SBX_DATA.lessons.length-1);sbxSaveProgress(progress);sbxState.answered=true;}
function sbxImage(assetKey,badge){var asset=SBX_DATA.assets[assetKey],wrap=sbxEl('div','sbx-image');if(!asset)return wrap;var img=document.createElement('img');img.src=asset.src;img.alt=sbxL(asset.alt);img.onerror=function(){var placeholder=sbxEl('div','sbx-placeholder',sbxCopy('imageMissing'));wrap.replaceChildren(placeholder);};wrap.appendChild(img);if(badge){var mark=sbxEl('span','sbx-badge',sbxL(badge));wrap.appendChild(mark);}return wrap;}
function sbxStatus(root){if(sbxState.storageFailed)root.appendChild(sbxEl('div','sbx-status',sbxCopy('storageError')));}
function sbxProgressPercent(progress){return Math.round((progress.completedLessons.length/SBX_DATA.lessons.length)*100);}
function sbxHome(){sbxState.view='home';var root=document.getElementById('sbxRoot');root.replaceChildren();var progress=sbxReadProgress(),percent=sbxProgressPercent(progress);var hero=sbxEl('section','sbx-hero');hero.append(sbxEl('div','sbx-logo',sbxCopy('brand')),sbxEl('h1','',sbxCopy('subtitle')),sbxEl('p','',sbxCopy('continue')));var row=sbxEl('div','sbx-progress-row');row.append(sbxEl('span','',sbxCopy('progress')),sbxEl('strong','',percent+' %'));var track=sbxEl('div','sbx-track'),fill=sbxEl('div','sbx-fill');fill.style.width=percent+'%';track.appendChild(fill);var start=sbxEl('button','sbx-primary',progress.completedLessons.length?sbxCopy('continue'):sbxCopy('start'));start.type='button';start.onclick=function(){sbxOpen(Math.min(Number(progress.currentLesson)||0,SBX_DATA.lessons.length-1));};hero.append(row,track,sbxEl('div','', ' '),start);root.appendChild(hero);root.appendChild(sbxEl('h2','sbx-section-title',sbxCopy('chapters')));var map=sbxEl('div','sbx-map');SBX_DATA.lessons.forEach(function(lesson,index){var card=sbxEl('div','sbx-map-card'),num=sbxEl('span','sbx-map-num',String(index+1)),copy=sbxEl('span',''),status=progress.completedLessons.indexOf(lesson.id)>=0?sbxCopy('completed'):'';copy.append(sbxEl('strong','',sbxL(lesson.title)),sbxEl('small','',sbxL(lesson.eyebrow)));card.append(num,copy,sbxEl('span','sbx-map-status',status));map.appendChild(card);});root.appendChild(map);sbxStatus(root);document.getElementById('app').classList.add('studybook-mode');}
function sbxHeader(root,lesson){var top=sbxEl('div','sbx-top'),back=sbxEl('button','sbx-secondary',sbxCopy('backHome'));back.type='button';back.onclick=sbxHome;top.append(back,sbxEl('span','sbx-logo',sbxCopy('brand')),sbxEl('span','sbx-lang',appLang.toUpperCase()));root.appendChild(top);}
function sbxLessonFrame(root,lesson){var card=sbxEl('article','sbx-card'),copy=sbxEl('div','sbx-copy');copy.append(sbxEl('div','sbx-eyebrow',sbxL(lesson.eyebrow)),sbxEl('h1','',sbxL(lesson.title)),sbxEl('p','',sbxL(lesson.body)));card.appendChild(copy);root.appendChild(card);return card;}
function sbxRemember(card,lesson){if(!lesson.remember)return;var box=sbxEl('div','sbx-remember');box.append(sbxEl('strong','',sbxCopy('remember')),sbxEl('span','',sbxL(lesson.remember)));card.querySelector('.sbx-copy').appendChild(box);}
function sbxFeedback(card,text,correct){var old=card.querySelector('.sbx-feedback');if(old)old.remove();var feedback=sbxEl('div','sbx-feedback',text);feedback.setAttribute('role','status');feedback.dataset.result=correct?'correct':'wrong';card.querySelector('.sbx-copy').appendChild(feedback);}
function sbxFooter(root){var footer=sbxEl('div','sbx-footer'),prev=sbxEl('button','sbx-secondary',sbxCopy('previous')),next=sbxEl('button','sbx-primary',sbxCopy('next'));prev.type=next.type='button';prev.disabled=sbxState.index===0;prev.onclick=function(){sbxOpen(sbxState.index-1);};next.disabled=!sbxState.answered;next.onclick=function(){if(sbxState.index<SBX_DATA.lessons.length-1)sbxOpen(sbxState.index+1);else sbxHome();};footer.append(prev,next);root.appendChild(footer);}
function sbxRenderSpot(card,lesson){var visual=sbxImage(lesson.asset);lesson.hazards.forEach(function(hazard){var button=sbxEl('button','sbx-hotspot');button.type='button';button.style.left=hazard.x+'%';button.style.top=hazard.y+'%';button.setAttribute('aria-label',sbxL(hazard.label));button.onclick=function(){button.classList.add('found');sbxFeedback(card,sbxL(hazard.feedback),true);sbxComplete(lesson.id);sbxRenderFooterState();};visual.appendChild(button);});card.insertBefore(visual,card.firstChild);sbxRemember(card,lesson);}
function sbxRenderImageLesson(card,lesson){card.insertBefore(sbxImage(lesson.asset),card.firstChild);var flow=sbxEl('div','sbx-flow');lesson.flow.forEach(function(step){flow.appendChild(sbxEl('span','',sbxL(step)));});var confirm=sbxEl('button','sbx-primary',sbxCopy('understood'));confirm.type='button';confirm.onclick=function(){sbxComplete(lesson.id);sbxFeedback(card,sbxL(lesson.remember),true);sbxRenderFooterState();};card.querySelector('.sbx-copy').append(flow,confirm);}
function sbxRenderChoice(card,lesson){card.insertBefore(sbxImage(lesson.asset,lesson.badge),card.firstChild);var actions=sbxEl('div','sbx-actions');lesson.options.forEach(function(option){var button=sbxEl('button','sbx-choice',sbxL(option.label));button.type='button';button.onclick=function(){var correct=option.id===lesson.correct;actions.querySelectorAll('button').forEach(function(item){item.classList.remove('correct','wrong');});button.classList.add(correct?'correct':'wrong');sbxFeedback(card,sbxL(correct?lesson.correctFeedback:lesson.wrongFeedback),correct);if(correct){sbxComplete(lesson.id);sbxRenderFooterState();}};actions.appendChild(button);});card.querySelector('.sbx-copy').appendChild(actions);sbxRemember(card,lesson);}
function sbxRenderRoad(card,lesson){var question=lesson.questions[sbxState.roadIndex],copy=card.querySelector('.sbx-copy');copy.replaceChildren();var head=sbxEl('div','sbx-road-head');head.append(sbxEl('div','sbx-eyebrow',sbxL(question.label)),sbxEl('span','sbx-road-step',(sbxState.roadIndex+1)+' / '+lesson.questions.length));copy.append(head,sbxEl('h1','',sbxL(question.prompt)));var actions=sbxEl('div','sbx-actions');question.options.forEach(function(option){var button=sbxEl('button','sbx-choice',sbxL(option.label));button.type='button';button.onclick=function(){var correct=option.id===question.correct;actions.querySelectorAll('button').forEach(function(item){item.disabled=true;});button.classList.add(correct?'correct':'wrong');sbxState.roadAnswers.push(correct);sbxFeedback(card,sbxL(question.explanation),correct);var advance=sbxEl('button','sbx-primary',sbxState.roadIndex+1<lesson.questions.length?sbxCopy('next'):sbxCopy('finish'));advance.type='button';advance.onclick=function(){if(sbxState.roadIndex+1<lesson.questions.length){sbxState.roadIndex+=1;sbxRenderRoad(card,lesson);}else{sbxRoadResult(lesson);}};copy.appendChild(advance);};actions.appendChild(button);});copy.appendChild(actions);}
function sbxRoadResult(lesson){var root=document.getElementById('sbxRoot'),score=sbxState.roadAnswers.filter(Boolean).length,total=lesson.questions.length,passed=score===total;root.replaceChildren();var card=sbxEl('section','sbx-card sbx-result');card.append(sbxEl('div','sbx-eyebrow',passed?sbxCopy('roadCleared'):sbxCopy('roadRetry')),sbxEl('div','sbx-score',score+' / '+total));var progress=sbxReadProgress();progress.roadCheck={score:score,total:total};if(passed){if(progress.completedLessons.indexOf(lesson.id)<0)progress.completedLessons.push(lesson.id);progress.currentLesson=SBX_DATA.lessons.length-1;}sbxSaveProgress(progress);var action=sbxEl('button',passed?'sbx-primary':'sbx-secondary',passed?sbxCopy('finish'):sbxCopy('review'));action.type='button';action.onclick=passed?sbxHome:function(){sbxState.roadIndex=0;sbxState.roadAnswers=[];sbxOpen(0);};card.appendChild(action);root.appendChild(card);sbxStatus(root);}
function sbxRenderFooterState(){var next=document.querySelector('#sbxRoot .sbx-footer .sbx-primary');if(next)next.disabled=!sbxState.answered;}
function sbxOpen(index){var lesson=SBX_DATA.lessons[index],root=document.getElementById('sbxRoot');if(!lesson){root.replaceChildren(sbxEl('div','sbx-feedback',sbxCopy('contentError')));return;}sbxState.view='lesson';sbxState.index=index;sbxState.answered=sbxReadProgress().completedLessons.indexOf(lesson.id)>=0;if(lesson.type==='roadCheck'){sbxState.roadIndex=0;sbxState.roadAnswers=[];}root.replaceChildren();sbxHeader(root,lesson);var card=sbxLessonFrame(root,lesson);if(lesson.type==='spotHazard')sbxRenderSpot(card,lesson);else if(lesson.type==='imageLesson')sbxRenderImageLesson(card,lesson);else if(lesson.type==='choice')sbxRenderChoice(card,lesson);else if(lesson.type==='roadCheck')sbxRenderRoad(card,lesson);else{sbxFeedback(card,sbxCopy('contentError'),false);}if(lesson.type!=='roadCheck')sbxFooter(root);sbxStatus(root);var progress=sbxReadProgress();progress.currentLesson=index;sbxSaveProgress(progress);}
function loadStudiebok(){var root=document.getElementById('sbxRoot');if(!root)return;document.getElementById('app').classList.add('studybook-mode');if(sbxState.view==='lesson')sbxOpen(sbxState.index);else sbxHome();}
function renderStudybook(){var screen=document.getElementById('screenStudybook');if(screen && screen.classList.contains('active'))loadStudiebok();}
""".replace("__SBX_DATA__", _DATA)


def install(html: str) -> str:
    """Replace only the legacy Studybook screen and add isolated web assets."""
    start_marker = '    <!-- ═══ STUDIEBOK SCREEN ═══ -->'
    end_marker = '    <!-- ═══ FORBIKJØRING SCREEN ═══ -->'
    if start_marker not in html or end_marker not in html:
        raise ValueError("Studybook screen markers not found")
    before, remainder = html.split(start_marker, 1)
    _, after = remainder.split(end_marker, 1)
    html = before + start_marker + "\n    " + SCREEN.strip() + "\n\n" + end_marker + after
    html = html.replace("</style>", CSS + "\n</style>", 1)
    html = html.replace(
        "if (typeof renderStopping === 'function' && document.getElementById('stopSpeed')) renderStopping();",
        "if (typeof renderStopping === 'function' && document.getElementById('stopSpeed')) renderStopping();\n  if (typeof renderStudybook === 'function') renderStudybook();",
        1,
    )
    html = html.replace(
        "  activeTab = tab;",
        "  activeTab = tab;\n  document.getElementById('app').classList.toggle('studybook-mode', tab === 'studybook');",
        1,
    )
    head, closing = html.rsplit("</script>", 1)
    return head + SCRIPT + "\n</script>" + closing
