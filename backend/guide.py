"""
Guide page: Fra Thailand til norsk førerkort
Trilingual: Thai / Norwegian / English
Route: /api/guide
"""

ICON_URL = "/api/assets/developer-icon-512.png"

_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  background:#0B1226;color:#E2E8F0;line-height:1.6;
  -webkit-font-smoothing:antialiased;min-height:100vh;
}
a{color:#FF9933;text-decoration:none}a:hover{opacity:.8}
.container{max-width:860px;margin:0 auto;padding:0 20px}

/* Nav */
.nav{position:sticky;top:0;z-index:50;background:rgba(11,18,38,.9);backdrop-filter:blur(12px);border-bottom:1px solid rgba(255,255,255,.08)}
.nav-inner{display:flex;align-items:center;justify-content:space-between;padding:12px 24px;max-width:860px;margin:0 auto}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;color:#fff}
.brand img{width:32px;height:32px;border-radius:8px}
.brand .t2d{color:#FF9933}
.lang-row{display:flex;gap:6px}
.lang-btn{width:40px;height:40px;border-radius:50%;border:2px solid transparent;background:rgba(255,255,255,.06);cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0;font-size:13px;font-weight:700;color:#CBD5E1;transition:all .15s}
.lang-btn:hover{transform:scale(1.1)}
.lang-btn.active{border-color:#FF9933;background:rgba(255,153,51,.18);color:#FF9933}

/* Lang visibility */
[data-lang]{display:none}
html[data-lang=th] [data-lang=th]{display:block}
html[data-lang=no] [data-lang=no]{display:block}
html[data-lang=en] [data-lang=en]{display:block}
span[data-lang]{display:none}
html[data-lang=th] span[data-lang=th]{display:inline}
html[data-lang=no] span[data-lang=no]{display:inline}
html[data-lang=en] span[data-lang=en]{display:inline}

/* Hero */
.hero{padding:56px 0 40px;text-align:center;background:linear-gradient(180deg,rgba(255,153,51,.06) 0%,transparent 100%)}
.hero-badge{display:inline-block;background:rgba(255,153,51,.15);border:1px solid rgba(255,153,51,.3);color:#FF9933;padding:6px 16px;border-radius:999px;font-size:13px;font-weight:700;margin-bottom:16px}
.hero h1{font-size:clamp(28px,5vw,48px);font-weight:900;color:#fff;line-height:1.15;margin-bottom:12px}
.hero h1 span{color:#FF9933}
.hero-sub{font-size:16px;color:#94A3B8;max-width:600px;margin:0 auto}

/* Steps overview */
.steps-row{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:32px 0 48px}
.step-chip{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:999px;padding:8px 16px;font-size:13px;font-weight:600;color:#CBD5E1}
.step-chip .num{width:22px;height:22px;border-radius:50%;background:#FF9933;color:#0F172A;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex-shrink:0}

/* Sections */
.section{padding:48px 0;border-top:1px solid rgba(255,255,255,.07)}
.section-num{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:10px;background:#FF9933;color:#0F172A;font-weight:800;font-size:16px;margin-bottom:12px}
.section h2{font-size:clamp(20px,3vw,28px);font-weight:800;color:#fff;margin-bottom:8px}
.section .lead{font-size:15px;color:#94A3B8;margin-bottom:24px}

/* Cards */
.cards{display:grid;gap:14px}
.card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:18px 20px}
.card-icon{font-size:24px;margin-bottom:8px}
.card h3{font-size:15px;font-weight:700;color:#fff;margin-bottom:6px}
.card p{font-size:14px;color:#94A3B8;line-height:1.55}
.card .highlight{color:#FF9933;font-weight:700}

/* Comparison table */
.cmp-table{width:100%;border-collapse:collapse;margin-top:16px;font-size:14px}
.cmp-table th{background:rgba(255,153,51,.12);color:#FF9933;padding:10px 14px;text-align:left;font-weight:700;border-bottom:1px solid rgba(255,255,255,.1)}
.cmp-table td{padding:10px 14px;border-bottom:1px solid rgba(255,255,255,.06);color:#CBD5E1;vertical-align:top}
.cmp-table tr:last-child td{border-bottom:0}
.cmp-table td:first-child{color:#94A3B8;font-weight:600;width:38%}
.tag-yes{color:#10B981;font-weight:700}
.tag-no{color:#EF4444;font-weight:700}
.tag-warn{color:#F59E0B;font-weight:700}

/* Cost table */
.cost-table{width:100%;border-collapse:collapse;font-size:14px;margin-top:16px}
.cost-table tr{border-bottom:1px solid rgba(255,255,255,.07)}
.cost-table tr:last-child{border-bottom:2px solid rgba(255,153,51,.4)}
.cost-table td{padding:10px 14px;color:#CBD5E1}
.cost-table td:last-child{text-align:right;font-weight:700;color:#fff}
.cost-table tr:last-child td{color:#FF9933;font-weight:800;font-size:15px}

/* Steps list */
.steps-list{display:grid;gap:14px;margin-top:16px}
.step-item{display:flex;gap:14px;align-items:flex-start}
.step-num{width:32px;height:32px;border-radius:50%;background:rgba(255,153,51,.15);border:2px solid #FF9933;color:#FF9933;font-weight:800;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}
.step-body h4{font-size:14px;font-weight:700;color:#fff;margin-bottom:4px}
.step-body p{font-size:13px;color:#94A3B8;line-height:1.5}
.step-body .note{display:inline-block;margin-top:6px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25);color:#10B981;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600}
.step-body .warn{display:inline-block;margin-top:6px;background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.25);color:#F59E0B;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:600}

/* CTA */
.cta-box{background:linear-gradient(135deg,rgba(255,153,51,.12),rgba(255,153,51,.04));border:1px solid rgba(255,153,51,.25);border-radius:18px;padding:36px 28px;text-align:center;margin:48px 0}
.cta-box h2{font-size:24px;font-weight:800;color:#fff;margin-bottom:8px}
.cta-box p{color:#94A3B8;margin-bottom:24px;font-size:15px}
.cta-btn{display:inline-flex;align-items:center;gap:10px;background:#FF9933;color:#0F172A;padding:14px 28px;border-radius:12px;font-weight:800;font-size:15px}
.cta-btn:hover{opacity:.9}

/* Footer */
footer{padding:32px 0;border-top:1px solid rgba(255,255,255,.07);text-align:center;color:#475569;font-size:13px}
footer a{color:#64748B}

@media(max-width:600px){
  .nav-inner{padding:10px 14px}
  .hero{padding:40px 0 28px}
  .cmp-table,.cost-table{font-size:13px}
}
"""

_JS = r"""
(function(){
  const saved = localStorage.getItem('t2d_lang') || 'th';
  document.documentElement.setAttribute('data-lang', saved);
  document.querySelectorAll('.lang-btn').forEach(btn=>{
    const code = btn.dataset.lang;
    if(code === saved) btn.classList.add('active');
    btn.addEventListener('click',()=>{
      document.documentElement.setAttribute('data-lang', code);
      localStorage.setItem('t2d_lang', code);
      document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active', b===btn));
    });
  });
})();
"""


def build_guide_page() -> str:
    return f"""<!DOCTYPE html>
<html lang="th" data-lang="th">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Fra Thailand til norsk førerkort | Thai2Drive</title>
<meta name="description" content="Komplett guide for thai-folk i Norge: Trinn for trinn til norsk førerkort. Krav, kostnader, teoriprøve og kjøreprøve forklart på thai og norsk."/>
<link rel="icon" href="{ICON_URL}"/>
<style>{_CSS}</style>
</head>
<body>

<!-- NAV -->
<nav class="nav">
  <div class="nav-inner">
    <a href="/api/website" class="brand">
      <img src="{ICON_URL}" alt="T2D"/>
      <span>Thai<span class="t2d">2</span>Drive</span>
    </a>
    <div class="lang-row">
      <button class="lang-btn active" data-lang="th">TH</button>
      <button class="lang-btn" data-lang="no">NO</button>
      <button class="lang-btn" data-lang="en">EN</button>
    </div>
  </div>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="container">
    <div class="hero-badge">📖 <span data-lang="th">คู่มือฉบับสมบูรณ์</span><span data-lang="no">Komplett guide</span><span data-lang="en">Complete guide</span></div>
    <h1>
      <span data-lang="th">จากไทย<span> สู่ใบขับขี่นอร์เวย์</span></span>
      <span data-lang="no">Fra Thailand til<span> norsk førerkort</span></span>
      <span data-lang="en">From Thailand to a<span> Norwegian licence</span></span>
    </h1>
    <p class="hero-sub">
      <span data-lang="th">คู่มือทีละขั้นตอนสำหรับคนไทยในนอร์เวย์ — ข้อกำหนด ค่าใช้จ่าย และทุกสิ่งที่คุณต้องรู้</span>
      <span data-lang="no">Steg-for-steg guide for thai-folk i Norge — krav, kostnader og alt du trenger å vite</span>
      <span data-lang="en">Step-by-step for Thai people in Norway — requirements, costs and everything you need to know</span>
    </p>
  </div>
</div>

<!-- OVERVIEW CHIPS -->
<div class="container">
  <div class="steps-row">
    <div class="step-chip"><span class="num">1</span>
      <span data-lang="th">เอกสาร</span><span data-lang="no">Dokumenter</span><span data-lang="en">Documents</span>
    </div>
    <div class="step-chip"><span class="num">2</span>
      <span data-lang="th">โรงเรียนสอนขับ</span><span data-lang="no">Trafikkskole</span><span data-lang="en">Driving school</span>
    </div>
    <div class="step-chip"><span class="num">3</span>
      <span data-lang="th">ทฤษฎี</span><span data-lang="no">Teoriprøve</span><span data-lang="en">Theory test</span>
    </div>
    <div class="step-chip"><span class="num">4</span>
      <span data-lang="th">คอร์สบังคับ</span><span data-lang="no">Obligatoriske kurs</span><span data-lang="en">Mandatory courses</span>
    </div>
    <div class="step-chip"><span class="num">5</span>
      <span data-lang="th">ทดสอบขับ</span><span data-lang="no">Kjøreprøve</span><span data-lang="en">Driving test</span>
    </div>
  </div>

  <!-- SECTION 1: REQUIREMENTS & DOCUMENTS -->
  <div class="section">
    <div class="section-num">1</div>
    <h2><span data-lang="th">ข้อกำหนดและเอกสาร</span><span data-lang="no">Krav og dokumenter</span><span data-lang="en">Requirements & documents</span></h2>
    <p class="lead">
      <span data-lang="th">ก่อนเริ่มต้น คุณต้องมีเอกสารเหล่านี้</span>
      <span data-lang="no">Før du starter, trenger du disse dokumentene</span>
      <span data-lang="en">Before you start, you need these documents</span>
    </p>
    <div class="cards">
      <div class="card">
        <div class="card-icon">🛂</div>
        <h3><span data-lang="th">สถานะในนอร์เวย์</span><span data-lang="no">Oppholdsstatus</span><span data-lang="en">Residence status</span></h3>
        <p>
          <span data-lang="th">คุณต้องมีใบอนุญาตพำนักที่ถูกต้องในนอร์เวย์ (oppholdstillatelse) และต้องมีอายุอย่างน้อย <span class="highlight">18 ปี</span></span>
          <span data-lang="no">Du må ha gyldig <span class="highlight">oppholdstillatelse</span> i Norge og være minst <span class="highlight">18 år</span></span>
          <span data-lang="en">You must have a valid <span class="highlight">residence permit</span> in Norway and be at least <span class="highlight">18 years old</span></span>
        </p>
      </div>
      <div class="card">
        <div class="card-icon">📋</div>
        <h3><span data-lang="th">เอกสารที่ต้องใช้</span><span data-lang="no">Dokumenter du trenger</span><span data-lang="en">Documents needed</span></h3>
        <p>
          <span data-lang="th">✅ หนังสือเดินทาง (Pass)<br/>✅ ใบอนุญาตพำนัก (Oppholdstillatelse)<br/>✅ ใบขับขี่ไทย (ถ้ามี — ใช้ยืนยันประสบการณ์ได้)<br/>✅ รูปถ่าย</span>
          <span data-lang="no">✅ Pass<br/>✅ Oppholdstillatelse<br/>✅ Thailandsk førerkort (hvis du har — kan brukes som erfaring)<br/>✅ Passbilde</span>
          <span data-lang="en">✅ Passport<br/>✅ Residence permit<br/>✅ Thai driving licence (if you have one — counts as experience)<br/>✅ Passport photo</span>
        </p>
      </div>
      <div class="card">
        <div class="card-icon">⚠️</div>
        <h3><span data-lang="th">ใบขับขี่ไทยใช้ในนอร์เวย์ได้ไหม?</span><span data-lang="no">Gjelder thailandsk førerkort i Norge?</span><span data-lang="en">Does a Thai licence count in Norway?</span></h3>
        <p>
          <span data-lang="th"><span class="highlight">ไม่ได้</span> — นอร์เวย์ไม่ยอมรับใบขับขี่ไทยโดยตรง คุณต้องสอบใหม่ทั้งหมด แต่ประสบการณ์การขับรถสามารถช่วยลดชั่วโมงฝึกได้</span>
          <span data-lang="no"><span class="highlight">Nei</span> — Norge godkjenner ikke thailandsk førerkort direkte. Du må ta full norsk opplæring, men erfaring kan hjelpe deg å lære raskere</span>
          <span data-lang="en"><span class="highlight">No</span> — Norway does not directly accept Thai licences. You must complete full Norwegian training, but your experience can help you learn faster</span>
        </p>
      </div>
    </div>
  </div>

  <!-- SECTION 2: THAI VS NORWEGIAN TRAFFIC -->
  <div class="section">
    <div class="section-num">2</div>
    <h2><span data-lang="th">ความแตกต่าง: ไทย vs. นอร์เวย์</span><span data-lang="no">Forskjeller: Thailand vs. Norge</span><span data-lang="en">Differences: Thailand vs. Norway</span></h2>
    <p class="lead">
      <span data-lang="th">สิ่งสำคัญที่ต้องรู้ก่อนขับรถในนอร์เวย์</span>
      <span data-lang="no">Viktige forskjeller du må kjenne til</span>
      <span data-lang="en">Important differences you must know</span>
    </p>
    <table class="cmp-table">
      <tr>
        <th><span data-lang="th">หัวข้อ</span><span data-lang="no">Tema</span><span data-lang="en">Topic</span></th>
        <th>🇹🇭 Thailand</th>
        <th>🇳🇴 Norge</th>
      </tr>
      <tr>
        <td><span data-lang="th">ฝั่งขับ</span><span data-lang="no">Kjøreside</span><span data-lang="en">Driving side</span></td>
        <td><span data-lang="th">ซ้ายมือ</span><span data-lang="no">Venstre</span><span data-lang="en">Left side</span></td>
        <td><span class="tag-warn"><span data-lang="th">ขวามือ!</span><span data-lang="no">Høyre!</span><span data-lang="en">Right side!</span></span></td>
      </tr>
      <tr>
        <td><span data-lang="th">ความเร็วในเมือง</span><span data-lang="no">Fartsgrense i by</span><span data-lang="en">Speed in city</span></td>
        <td>60 km/h</td>
        <td><span class="tag-warn">50 km/h</span></td>
      </tr>
      <tr>
        <td><span data-lang="th">ความเร็วนอกเมือง</span><span data-lang="no">Fartsgrense utenfor by</span><span data-lang="en">Speed outside city</span></td>
        <td>90 km/h</td>
        <td>80 km/h</td>
      </tr>
      <tr>
        <td><span data-lang="th">วงเวียน (vikeplikt)</span><span data-lang="no">Rundkjøring</span><span data-lang="en">Roundabout</span></td>
        <td><span data-lang="th">ผู้เข้าวงเวียนมีสิทธิ์ก่อน</span><span data-lang="no">Innkjørende har forkjørsrett</span><span data-lang="en">Entering traffic has priority</span></td>
        <td><span class="tag-yes"><span data-lang="th">รถในวงเวียนมีสิทธิ์ก่อน!</span><span data-lang="no">I rundkjøringen har forkjørsrett!</span><span data-lang="en">Traffic inside has priority!</span></span></td>
      </tr>
      <tr>
        <td><span data-lang="th">เบลต์นิรภัย</span><span data-lang="no">Bilbelte</span><span data-lang="en">Seatbelt</span></td>
        <td><span data-lang="th">บังคับเฉพาะเบาะหน้า</span><span data-lang="no">Påbudt foran</span><span data-lang="en">Mandatory in front</span></td>
        <td><span class="tag-yes"><span data-lang="th">บังคับทุกที่นั่ง</span><span data-lang="no">Påbudt alle seter</span><span data-lang="en">All seats mandatory</span></span></td>
      </tr>
      <tr>
        <td><span data-lang="th">การขับรถในฤดูหนาว</span><span data-lang="no">Vinterkjøring</span><span data-lang="en">Winter driving</span></td>
        <td><span data-lang="th">ไม่มี</span><span data-lang="no">Ikke relevant</span><span data-lang="en">Not relevant</span></td>
        <td><span class="tag-warn"><span data-lang="th">บังคับมีหลักสูตร!</span><span data-lang="no">Obligatorisk kurs!</span><span data-lang="en">Mandatory course!</span></span></td>
      </tr>
      <tr>
        <td><span data-lang="th">แอลกอฮอล์</span><span data-lang="no">Promillegrense</span><span data-lang="en">Alcohol limit</span></td>
        <td>0.05%</td>
        <td><span class="tag-yes">0.02% <span data-lang="th">(เข้มงวดมาก)</span><span data-lang="no">(veldig strengt)</span><span data-lang="en">(very strict)</span></span></td>
      </tr>
    </table>
  </div>

  <!-- SECTION 3: STEP BY STEP -->
  <div class="section">
    <div class="section-num">3</div>
    <h2><span data-lang="th">ขั้นตอนทั้งหมด ทีละขั้น</span><span data-lang="no">Trinn for trinn — full opplæring</span><span data-lang="en">Step by step — full training</span></h2>
    <p class="lead">
      <span data-lang="th">ต้องทำทั้งหมด 5 ขั้นตอน ตามลำดับ</span>
      <span data-lang="no">Du må fullføre alle 5 trinn i rekkefølge</span>
      <span data-lang="en">You must complete all 5 steps in order</span>
    </p>
    <div class="steps-list">
      <div class="step-item">
        <div class="step-num">1</div>
        <div class="step-body">
          <h4><span data-lang="th">ลงทะเบียนกับโรงเรียนสอนขับ (Trafikkskole)</span><span data-lang="no">Meld deg på trafikkskole</span><span data-lang="en">Register at a driving school</span></h4>
          <p><span data-lang="th">เลือกโรงเรียนสอนขับในเมืองของคุณ ค่าใช้จ่ายและระยะเวลาจะแตกต่างกัน</span><span data-lang="no">Velg en trafikkskole i din by. Pris og tid varierer.</span><span data-lang="en">Choose a driving school in your city. Price and time vary.</span></p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">2</div>
        <div class="step-body">
          <h4><span data-lang="th">Trafikalt grunnkurs (TG)</span><span data-lang="no">Trafikalt grunnkurs (TG)</span><span data-lang="en">Basic traffic course (TG)</span></h4>
          <p><span data-lang="th">หลักสูตรพื้นฐาน 17 ชั่วโมง — ต้องทำก่อนอื่น ครอบคลุมทฤษฎีพื้นฐาน การปฐมพยาบาล และการขับขี่อย่างปลอดภัย</span><span data-lang="no">17-timers grunnkurs — må tas først. Dekker grunnleggende teori, førstehjelp og trygg kjøring.</span><span data-lang="en">17-hour basic course — must be taken first. Covers basic theory, first aid and safe driving.</span></p>
          <span class="note"><span data-lang="th">บังคับ — ทำก่อนอย่างอื่น</span><span data-lang="no">Obligatorisk — må gjøres først</span><span data-lang="en">Mandatory — must be done first</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">3</div>
        <div class="step-body">
          <h4><span data-lang="th">ฝึกขับรถกับครูสอน</span><span data-lang="no">Kjøretimer med lærer</span><span data-lang="en">Driving lessons with instructor</span></h4>
          <p><span data-lang="th">จำนวนชั่วโมงขึ้นอยู่กับระดับของคุณ โดยเฉลี่ย 20-40 ชั่วโมง ค่าชั่วโมงละ ~600-800 kr</span><span data-lang="no">Antall timer avhenger av nivået ditt. Gjennomsnittlig 20–40 timer. Ca. 600–800 kr/time.</span><span data-lang="en">Number of hours depends on your level. Average 20–40 hours. Approx. 600–800 kr/hour.</span></p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">4</div>
        <div class="step-body">
          <h4><span data-lang="th">หลักสูตรบังคับ 3 วิชา</span><span data-lang="no">3 obligatoriske kurs</span><span data-lang="en">3 mandatory courses</span></h4>
          <p>
            <span data-lang="th">🌑 <strong>Mørkekjøring</strong> — ขับรถในที่มืด (3 ชม.)<br/>🧊 <strong>Glattkjøring</strong> — ขับรถบนถนนลื่น/น้ำแข็ง (4 ชม.)<br/>🛣️ <strong>Sikkerhetskurs</strong> — ขับบนถนนจริง (13 ชม.)</span>
            <span data-lang="no">🌑 <strong>Mørkekjøring</strong> — kjøring i mørket (3 t.)<br/>🧊 <strong>Glattkjøring</strong> — kjøring på glatt underlag (4 t.)<br/>🛣️ <strong>Sikkerhetskurs på veg</strong> — øving i trafikk (13 t.)</span>
            <span data-lang="en">🌑 <strong>Mørkekjøring</strong> — night driving (3 hrs)<br/>🧊 <strong>Glattkjøring</strong> — slippery road driving (4 hrs)<br/>🛣️ <strong>Sikkerhetskurs</strong> — on-road safety course (13 hrs)</span>
          </p>
          <span class="warn"><span data-lang="th">ต้องทำให้ครบก่อนสอบขับ!</span><span data-lang="no">Må fullføres før kjøreprøven!</span><span data-lang="en">Must be completed before driving test!</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">5</div>
        <div class="step-body">
          <h4><span data-lang="th">สอบทฤษฎี (Teoriprøve)</span><span data-lang="no">Teoriprøven</span><span data-lang="en">Theory test</span></h4>
          <p><span data-lang="th">45 ข้อ — ต้องได้อย่างน้อย 85% (ผิดได้ไม่เกิน 7 ข้อ) เวลา 90 นาที ค่าสอบ ~300 kr สอบได้ตั้งแต่อายุ 16 ปี</span><span data-lang="no">45 spørsmål — må ha minst 85% riktig (maks 7 feil). 90 minutter. ~300 kr. Kan tas fra 16 år.</span><span data-lang="en">45 questions — must score at least 85% (max 7 wrong). 90 minutes. ~300 kr. Can be taken from age 16.</span></p>
          <span class="note"><span data-lang="th">ฝึกกับ Thai2Drive! 📱</span><span data-lang="no">Øv med Thai2Drive! 📱</span><span data-lang="en">Practice with Thai2Drive! 📱</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">6</div>
        <div class="step-body">
          <h4><span data-lang="th">สอบขับ (Kjøreprøve)</span><span data-lang="no">Kjøreprøven</span><span data-lang="en">Driving test</span></h4>
          <p><span data-lang="th">ระยะเวลาประมาณ 45-60 นาที กับผู้ตรวจสอบจาก Statens vegvesen ค่าสอบ ~1000 kr</span><span data-lang="no">Ca. 45–60 min med sensor fra Statens vegvesen. ~1 000 kr.</span><span data-lang="en">Approx. 45–60 min with an examiner from Statens vegvesen. ~1 000 kr.</span></p>
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 4: COSTS -->
  <div class="section">
    <div class="section-num">4</div>
    <h2><span data-lang="th">ค่าใช้จ่ายโดยรวม</span><span data-lang="no">Totale kostnader</span><span data-lang="en">Total costs</span></h2>
    <p class="lead">
      <span data-lang="th">ประมาณการค่าใช้จ่ายในการเรียนขับรถในนอร์เวย์</span>
      <span data-lang="no">Estimerte kostnader for full opplæring i Norge</span>
      <span data-lang="en">Estimated costs for full training in Norway</span>
    </p>
    <table class="cost-table">
      <tr>
        <td><span data-lang="th">หลักสูตรพื้นฐาน (TG)</span><span data-lang="no">Trafikalt grunnkurs</span><span data-lang="en">Basic traffic course</span></td>
        <td>~3 500 kr</td>
      </tr>
      <tr>
        <td><span data-lang="th">ชั่วโมงฝึกขับ (25 ชม.)</span><span data-lang="no">Kjøretimer (25 t.)</span><span data-lang="en">Driving lessons (25 hrs)</span></td>
        <td>~17 500 kr</td>
      </tr>
      <tr>
        <td><span data-lang="th">หลักสูตรบังคับ 3 วิชา</span><span data-lang="no">Obligatoriske kurs</span><span data-lang="en">Mandatory courses</span></td>
        <td>~6 000 kr</td>
      </tr>
      <tr>
        <td><span data-lang="th">ค่าสอบทฤษฎี</span><span data-lang="no">Teoriprøve</span><span data-lang="en">Theory test</span></td>
        <td>~300 kr</td>
      </tr>
      <tr>
        <td><span data-lang="th">ค่าสอบขับ</span><span data-lang="no">Kjøreprøve</span><span data-lang="en">Driving test</span></td>
        <td>~1 000 kr</td>
      </tr>
      <tr>
        <td><strong><span data-lang="th">รวมทั้งหมด (โดยประมาณ)</span><span data-lang="no">Totalt (estimert)</span><span data-lang="en">Total (estimated)</span></strong></td>
        <td>~28 000 – 40 000 kr</td>
      </tr>
    </table>
  </div>

  <!-- CTA -->
  <div class="cta-box">
    <h2><span data-lang="th">พร้อมสอบทฤษฎีแล้วหรือยัง?</span><span data-lang="no">Klar til å øve på teoriprøven?</span><span data-lang="en">Ready to practice the theory test?</span></h2>
    <p><span data-lang="th">ฝึกกับคำถาม 700+ ข้อ บน Thai2Drive — เป็นภาษาไทย นอร์เวย์ และอังกฤษ</span><span data-lang="no">Øv med 700+ spørsmål på Thai2Drive — på thai, norsk og engelsk</span><span data-lang="en">Practice with 700+ questions on Thai2Drive — in Thai, Norwegian and English</span></p>
    <a href="/api/website" class="cta-btn">🚀 <span data-lang="th">ฝึกฟรี</span><span data-lang="no">Prøv gratis</span><span data-lang="en">Try free</span></a>
  </div>

</div><!-- /container -->

<footer>
  <p>© 2025 Thai2Drive · <a href="/api/privacy">Personvern</a> · <a href="/api/terms">Vilkår</a></p>
</footer>

<script>{_JS}</script>
</body>
</html>"""
