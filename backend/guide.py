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

/* Lang visibility — JS sets .lang-th/.lang-no/.lang-en on body */
.tl{display:none}
body.lang-th .tl-th{display:block}
body.lang-no .tl-no{display:block}
body.lang-en .tl-en{display:block}
span.tl{display:none}
body.lang-th span.tl-th{display:inline}
body.lang-no span.tl-no{display:inline}
body.lang-en span.tl-en{display:inline}

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
.card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:20px 22px}
.card-icon{font-size:26px;margin-bottom:10px}
.card h3{font-size:17px;font-weight:700;color:#fff;margin-bottom:8px}
.card p{font-size:16px;color:#94A3B8;line-height:1.65}
.card .highlight{color:#FF9933;font-weight:700}

/* Comparison table */
.cmp-table{width:100%;border-collapse:collapse;margin-top:16px;font-size:15px}
.cmp-table th{background:rgba(255,153,51,.12);color:#FF9933;padding:12px 14px;text-align:left;font-weight:700;border-bottom:1px solid rgba(255,255,255,.1)}
.cmp-table td{padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.06);color:#CBD5E1;vertical-align:top}
.cmp-table tr:last-child td{border-bottom:0}
.cmp-table td:first-child{color:#94A3B8;font-weight:600;width:38%}
.tag-yes{color:#10B981;font-weight:700}
.tag-no{color:#EF4444;font-weight:700}
.tag-warn{color:#F59E0B;font-weight:700}

/* Cost table */
.cost-table{width:100%;border-collapse:collapse;font-size:15px;margin-top:16px}
.cost-table tr{border-bottom:1px solid rgba(255,255,255,.07)}
.cost-table tr:last-child{border-bottom:2px solid rgba(255,153,51,.4)}
.cost-table td{padding:12px 14px;color:#CBD5E1}
.cost-table td:last-child{text-align:right;font-weight:700;color:#fff}
.cost-table tr:last-child td{color:#FF9933;font-weight:800;font-size:16px}

/* Steps list */
.steps-list{display:grid;gap:16px;margin-top:16px}
.step-item{display:flex;gap:14px;align-items:flex-start}
.step-num{width:34px;height:34px;border-radius:50%;background:rgba(255,153,51,.15);border:2px solid #FF9933;color:#FF9933;font-weight:800;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}
.step-body h4{font-size:16px;font-weight:700;color:#fff;margin-bottom:6px}
.step-body p{font-size:15px;color:#94A3B8;line-height:1.6}
.step-body .note{display:inline-block;margin-top:6px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25);color:#10B981;padding:4px 12px;border-radius:999px;font-size:13px;font-weight:600}
.step-body .warn{display:inline-block;margin-top:6px;background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.25);color:#F59E0B;padding:4px 12px;border-radius:999px;font-size:13px;font-weight:600}

/* PDF download banner */
.pdf-banner{display:none;background:linear-gradient(135deg,rgba(16,185,129,.12),rgba(16,185,129,.04));border:1px solid rgba(16,185,129,.3);border-radius:14px;padding:18px 22px;margin:28px 0;align-items:center;gap:16px;flex-wrap:wrap}
.pdf-banner.show{display:flex}
.pdf-banner p{flex:1;color:#CBD5E1;font-size:15px;margin:0}
.pdf-btn{display:inline-flex;align-items:center;gap:8px;background:#10B981;color:#fff;padding:12px 22px;border-radius:10px;font-weight:800;font-size:15px;border:0;cursor:pointer;white-space:nowrap}
.pdf-btn:hover{opacity:.9}

/* CTA */
.cta-box{background:linear-gradient(135deg,rgba(255,153,51,.12),rgba(255,153,51,.04));border:1px solid rgba(255,153,51,.25);border-radius:18px;padding:36px 28px;text-align:center;margin:48px 0}
.cta-box h2{font-size:26px;font-weight:800;color:#fff;margin-bottom:8px}
.cta-box p{color:#94A3B8;margin-bottom:24px;font-size:16px}
.cta-btn{display:inline-flex;align-items:center;gap:10px;background:#FF9933;color:#0F172A;padding:14px 28px;border-radius:12px;font-weight:800;font-size:16px}
.cta-btn:hover{opacity:.9}

/* Footer */
footer{padding:32px 0;border-top:1px solid rgba(255,255,255,.07);text-align:center;color:#475569;font-size:14px}
footer a{color:#64748B}

/* Print / PDF */
@media print{
  body{background:#fff!important;color:#000!important}
  .nav,.cta-box,.pdf-banner,footer{display:none!important}
  .hero{background:none!important}
  .hero h1,.section h2,.card h3,.step-body h4{color:#000!important}
  .card,.step-item{break-inside:avoid}
  .card p,.step-body p,.lang-row td{color:#333!important}
  body.lang-th .tl-th,body.lang-no .tl-no,body.lang-en .tl-en{display:block!important}
}

@media(max-width:600px){
  .nav-inner{padding:10px 14px}
  .hero{padding:40px 0 28px}
  .cmp-table,.cost-table{font-size:14px}
  .card p,.step-body p{font-size:15px}
}
"""

_JS = r"""
(function(){
  const langs = ['th','no','en'];
  const saved = localStorage.getItem('t2d_guide_lang') || 'no';
  function setLang(code){
    langs.forEach(l => document.body.classList.remove('lang-'+l));
    document.body.classList.add('lang-'+code);
    localStorage.setItem('t2d_guide_lang', code);
    document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active', b.dataset.lang===code));
  }
  document.querySelectorAll('.lang-btn').forEach(btn=>{
    btn.addEventListener('click',()=>setLang(btn.dataset.lang));
  });
  setLang(saved);

  // Show PDF banner only for logged-in members
  const token = localStorage.getItem('t2d_token');
  if(token){
    const banner = document.getElementById('pdf-banner');
    if(banner) banner.classList.add('show');
  }

  // PDF download: print page in current language
  window.downloadPDF = function(){
    window.print();
  };
})();
"""


def build_guide_page() -> str:
    return f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Fra Thailand til norsk førerkort | Thai2Drive</title>
<meta name="description" content="Komplett guide for thai-folk i Norge: Trinn for trinn til norsk førerkort. Krav, kostnader, teoriprøve og kjøreprøve forklart på thai og norsk."/>
<link rel="icon" href="{ICON_URL}"/>
<style>{_CSS}</style>
</head>
<body class="lang-no">

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
    <div class="hero-badge">📖 <span class="tl tl-th">คู่มือฉบับสมบูรณ์</span><span class="tl tl-no">Komplett guide</span><span class="tl tl-en">Complete guide</span></div>
    <h1>
      <span class="tl tl-th">จากไทย<span> สู่ใบขับขี่นอร์เวย์</span></span>
      <span class="tl tl-no">Fra Thailand til<span> norsk førerkort</span></span>
      <span class="tl tl-en">From Thailand to a<span> Norwegian licence</span></span>
    </h1>
    <p class="hero-sub">
      <span class="tl tl-th">คู่มือทีละขั้นตอนสำหรับคนไทยในนอร์เวย์ — ข้อกำหนด ค่าใช้จ่าย และทุกสิ่งที่คุณต้องรู้</span>
      <span class="tl tl-no">Steg-for-steg guide for thai-folk i Norge — krav, kostnader og alt du trenger å vite</span>
      <span class="tl tl-en">Step-by-step for Thai people in Norway — requirements, costs and everything you need to know</span>
    </p>
  </div>
</div>

<!-- OVERVIEW CHIPS -->
<div class="container">
  <div class="steps-row">
    <div class="step-chip"><span class="num">1</span>
      <span class="tl tl-th">ลงทะเบียน</span><span class="tl tl-no">Registrer</span><span class="tl tl-en">Register</span>
    </div>
    <div class="step-chip"><span class="num">2</span>
      <span class="tl tl-th">Trinn 1 (TGK)</span><span class="tl tl-no">Trinn 1 (TGK)</span><span class="tl tl-en">Trinn 1 (TGK)</span>
    </div>
    <div class="step-chip"><span class="num">3</span>
      <span class="tl tl-th">Trinn 2 (45 min)</span><span class="tl tl-no">Trinn 2 (45 min)</span><span class="tl tl-en">Trinn 2 (45 min)</span>
    </div>
    <div class="step-chip"><span class="num">4</span>
      <span class="tl tl-th">Trinn 3 + bane</span><span class="tl tl-no">Trinn 3 + bane</span><span class="tl tl-en">Trinn 3 + track</span>
    </div>
    <div class="step-chip"><span class="num">5</span>
      <span class="tl tl-th">Trinn 4 (vei 6t)</span><span class="tl tl-no">Trinn 4 (vei 6t)</span><span class="tl tl-en">Trinn 4 (road 6h)</span>
    </div>
    <div class="step-chip"><span class="num">6</span>
      <span class="tl tl-th">ทฤษฎี</span><span class="tl tl-no">Teoriprøve</span><span class="tl tl-en">Theory test</span>
    </div>
    <div class="step-chip"><span class="num">7</span>
      <span class="tl tl-th">ขับจริง</span><span class="tl tl-no">Kjøreprøve</span><span class="tl tl-en">Driving test</span>
    </div>
  </div>

  <!-- SECTION 1: REQUIREMENTS & DOCUMENTS -->
  <div class="section">
    <div class="section-num">1</div>
    <h2><span class="tl tl-th">ข้อกำหนดและเอกสาร</span><span class="tl tl-no">Krav og dokumenter</span><span class="tl tl-en">Requirements & documents</span></h2>
    <p class="lead">
      <span class="tl tl-th">ก่อนเริ่มต้น คุณต้องมีเอกสารเหล่านี้</span>
      <span class="tl tl-no">Før du starter, trenger du disse dokumentene</span>
      <span class="tl tl-en">Before you start, you need these documents</span>
    </p>
    <div class="cards">
      <div class="card">
        <div class="card-icon">🛂</div>
        <h3><span class="tl tl-th">สถานะในนอร์เวย์</span><span class="tl tl-no">Oppholdsstatus</span><span class="tl tl-en">Residence status</span></h3>
        <p>
          <span class="tl tl-th">คุณต้องมีใบอนุญาตพำนักที่ถูกต้องในนอร์เวย์ (oppholdstillatelse) และต้องมีอายุอย่างน้อย <span class="highlight">18 ปี</span></span>
          <span class="tl tl-no">Du må ha gyldig <span class="highlight">oppholdstillatelse</span> i Norge og være minst <span class="highlight">18 år</span></span>
          <span class="tl tl-en">You must have a valid <span class="highlight">residence permit</span> in Norway and be at least <span class="highlight">18 years old</span></span>
        </p>
      </div>
      <div class="card">
        <div class="card-icon">📋</div>
        <h3><span class="tl tl-th">เอกสารที่ต้องใช้</span><span class="tl tl-no">Dokumenter du trenger</span><span class="tl tl-en">Documents needed</span></h3>
        <p>
          <span class="tl tl-th">✅ หนังสือเดินทาง (Pass)<br/>✅ ใบอนุญาตพำนัก (Oppholdstillatelse)<br/>✅ ใบขับขี่ไทย (ถ้ามี — ใช้ยืนยันประสบการณ์ได้)<br/>✅ รูปถ่าย</span>
          <span class="tl tl-no">✅ Pass<br/>✅ Oppholdstillatelse<br/>✅ Thailandsk førerkort (hvis du har — kan brukes som erfaring)<br/>✅ Passbilde</span>
          <span class="tl tl-en">✅ Passport<br/>✅ Residence permit<br/>✅ Thai driving licence (if you have one — counts as experience)<br/>✅ Passport photo</span>
        </p>
      </div>
      <div class="card">
        <div class="card-icon">⚠️</div>
        <h3><span class="tl tl-th">ใบขับขี่ไทยใช้ในนอร์เวย์ได้ไหม?</span><span class="tl tl-no">Gjelder thailandsk førerkort i Norge?</span><span class="tl tl-en">Does a Thai licence count in Norway?</span></h3>
        <p>
          <span class="tl tl-th"><span class="highlight">ไม่ได้</span> — นอร์เวย์ไม่ยอมรับใบขับขี่ไทยโดยตรง คุณต้องสอบใหม่ทั้งหมด แต่ประสบการณ์การขับรถสามารถช่วยลดชั่วโมงฝึกได้</span>
          <span class="tl tl-no"><span class="highlight">Nei</span> — Norge godkjenner ikke thailandsk førerkort direkte. Du må ta full norsk opplæring, men erfaring kan hjelpe deg å lære raskere</span>
          <span class="tl tl-en"><span class="highlight">No</span> — Norway does not directly accept Thai licences. You must complete full Norwegian training, but your experience can help you learn faster</span>
        </p>
      </div>
    </div>
  </div>

  <!-- SECTION 2: THAI VS NORWEGIAN TRAFFIC -->
  <div class="section">
    <div class="section-num">2</div>
    <h2><span class="tl tl-th">ความแตกต่าง: ไทย vs. นอร์เวย์</span><span class="tl tl-no">Forskjeller: Thailand vs. Norge</span><span class="tl tl-en">Differences: Thailand vs. Norway</span></h2>
    <p class="lead">
      <span class="tl tl-th">สิ่งสำคัญที่ต้องรู้ก่อนขับรถในนอร์เวย์</span>
      <span class="tl tl-no">Viktige forskjeller du må kjenne til</span>
      <span class="tl tl-en">Important differences you must know</span>
    </p>
    <table class="cmp-table">
      <tr>
        <th><span class="tl tl-th">หัวข้อ</span><span class="tl tl-no">Tema</span><span class="tl tl-en">Topic</span></th>
        <th>🇹🇭 Thailand</th>
        <th>🇳🇴 Norge</th>
      </tr>
      <tr>
        <td><span class="tl tl-th">ฝั่งขับ</span><span class="tl tl-no">Kjøreside</span><span class="tl tl-en">Driving side</span></td>
        <td><span class="tl tl-th">ซ้ายมือ</span><span class="tl tl-no">Venstre</span><span class="tl tl-en">Left side</span></td>
        <td><span class="tag-warn"><span class="tl tl-th">ขวามือ!</span><span class="tl tl-no">Høyre!</span><span class="tl tl-en">Right side!</span></span></td>
      </tr>
      <tr>
        <td><span class="tl tl-th">ความเร็วในเมือง</span><span class="tl tl-no">Fartsgrense i by</span><span class="tl tl-en">Speed in city</span></td>
        <td>60 km/h</td>
        <td><span class="tag-warn">50 km/h</span></td>
      </tr>
      <tr>
        <td><span class="tl tl-th">ความเร็วนอกเมือง</span><span class="tl tl-no">Fartsgrense utenfor by</span><span class="tl tl-en">Speed outside city</span></td>
        <td>90 km/h</td>
        <td>80 km/h</td>
      </tr>
      <tr>
        <td><span class="tl tl-th">วงเวียน (vikeplikt)</span><span class="tl tl-no">Rundkjøring</span><span class="tl tl-en">Roundabout</span></td>
        <td><span class="tl tl-th">ผู้เข้าวงเวียนมีสิทธิ์ก่อน</span><span class="tl tl-no">Innkjørende har forkjørsrett</span><span class="tl tl-en">Entering traffic has priority</span></td>
        <td><span class="tag-yes"><span class="tl tl-th">รถในวงเวียนมีสิทธิ์ก่อน!</span><span class="tl tl-no">I rundkjøringen har forkjørsrett!</span><span class="tl tl-en">Traffic inside has priority!</span></span></td>
      </tr>
      <tr>
        <td><span class="tl tl-th">เบลต์นิรภัย</span><span class="tl tl-no">Bilbelte</span><span class="tl tl-en">Seatbelt</span></td>
        <td><span class="tl tl-th">บังคับเฉพาะเบาะหน้า</span><span class="tl tl-no">Påbudt foran</span><span class="tl tl-en">Mandatory in front</span></td>
        <td><span class="tag-yes"><span class="tl tl-th">บังคับทุกที่นั่ง</span><span class="tl tl-no">Påbudt alle seter</span><span class="tl tl-en">All seats mandatory</span></span></td>
      </tr>
      <tr>
        <td><span class="tl tl-th">การขับรถในฤดูหนาว</span><span class="tl tl-no">Vinterkjøring</span><span class="tl tl-en">Winter driving</span></td>
        <td><span class="tl tl-th">ไม่มี</span><span class="tl tl-no">Ikke relevant</span><span class="tl tl-en">Not relevant</span></td>
        <td><span class="tag-warn"><span class="tl tl-th">บังคับมีหลักสูตร!</span><span class="tl tl-no">Obligatorisk kurs!</span><span class="tl tl-en">Mandatory course!</span></span></td>
      </tr>
      <tr>
        <td><span class="tl tl-th">แอลกอฮอล์</span><span class="tl tl-no">Promillegrense</span><span class="tl tl-en">Alcohol limit</span></td>
        <td>0.05%</td>
        <td><span class="tag-yes">0.02% <span class="tl tl-th">(เข้มงวดมาก)</span><span class="tl tl-no">(veldig strengt)</span><span class="tl tl-en">(very strict)</span></span></td>
      </tr>
    </table>
  </div>

  <!-- SECTION 3: STEP BY STEP -->
  <div class="section">
    <div class="section-num">3</div>
    <h2><span class="tl tl-th">ขั้นตอนบังคับ — ตามลำดับ</span><span class="tl tl-no">Obligatorisk rekkefølge</span><span class="tl tl-en">Mandatory steps — in order</span></h2>
    <p class="lead">
      <span class="tl tl-th">6 ขั้นตอนแรกที่โรงเรียนสอนขับ + 2 ขั้นสุดท้ายที่ Statens Vegvesen</span>
      <span class="tl tl-no">6 første hos trafikklærer + 2 siste hos Statens Vegvesen — i denne rekkefølgen</span>
      <span class="tl tl-en">First 6 steps at driving school + last 2 at Statens Vegvesen — in this exact order</span>
    </p>

    <p style="font-size:13px;font-weight:700;color:#FF9933;margin-bottom:12px;margin-top:4px">
      🏫 <span class="tl tl-th">ที่โรงเรียนสอนขับ (Trafikklærer)</span><span class="tl tl-no">Hos trafikklærer</span><span class="tl tl-en">At driving school</span>
    </p>
    <div class="steps-list">
      <div class="step-item">
        <div class="step-num">1</div>
        <div class="step-body">
          <h4><span class="tl tl-th">ลงทะเบียนกับโรงเรียนสอนขับ</span><span class="tl tl-no">Meld deg på trafikkskole</span><span class="tl tl-en">Register at a driving school</span></h4>
          <p><span class="tl tl-th">เลือกโรงเรียนสอนขับในเมืองของคุณ ราคาและระยะเวลาจะแตกต่างกันไปในแต่ละที่</span><span class="tl tl-no">Velg en trafikkskole i din by. Pris og tid varierer fra skole til skole.</span><span class="tl tl-en">Choose a driving school in your city. Prices and duration vary.</span></p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">2</div>
        <div class="step-body">
          <h4><span class="tl tl-th">Trafikalt grunnkurs (TG)</span><span class="tl tl-no">Trafikalt grunnkurs (TG)</span><span class="tl tl-en">Basic traffic course (TG)</span></h4>
          <p><span class="tl tl-th">หลักสูตรพื้นฐาน 17 ชั่วโมง ครอบคลุมทฤษฎีพื้นฐาน การปฐมพยาบาล และการขับขี่อย่างปลอดภัย</span><span class="tl tl-no">17-timers grunnkurs. Dekker grunnleggende teori, førstehjelp og trygg kjøring.</span><span class="tl tl-en">17-hour basic course. Covers basic theory, first aid and safe driving.</span></p>
          <div style="margin-top:10px;background:rgba(255,153,51,.08);border:1px solid rgba(255,153,51,.2);border-radius:10px;padding:12px 14px">
            <p style="font-size:13px;font-weight:700;color:#FF9933;margin-bottom:6px">
              <span class="tl tl-th">⚠️ อายุเกิน 25 ปี — ไม่ต้องเรียนครบ 17 ชั่วโมง!</span>
              <span class="tl tl-no">⚠️ Over 25 år — du trenger IKKE hele TGK!</span>
              <span class="tl tl-en">⚠️ Over 25 years — you do NOT need the full TGK!</span>
            </p>
            <p style="font-size:13px;color:#CBD5E1">
              <span class="tl tl-th">ถ้าอายุเกิน 25 ปี คุณต้องแค่:<br/>✅ <strong>Førstehjelp</strong> — หลักสูตรปฐมพยาบาล<br/>✅ <strong>MørkeDemo</strong> — ทดสอบขับในที่มืด<br/>ไม่ต้องเรียน TGK ทั้งหมด 17 ชั่วโมง</span>
              <span class="tl tl-no">Hvis du er over 25 år trenger du kun:<br/>✅ <strong>Førstehjelp</strong> — førstehjelpskurs<br/>✅ <strong>MørkeDemo</strong> — demonstrasjon i mørkekjøring<br/>Du slipper hele 17-timers TGK-kurset!</span>
              <span class="tl tl-en">If you are over 25 years old you only need:<br/>✅ <strong>First aid course</strong><br/>✅ <strong>Dark driving demo (MørkeDemo)</strong><br/>You skip the full 17-hour TGK course!</span>
            </p>
          </div>
          <span class="note" style="margin-top:10px"><span class="tl tl-th">ต้องทำก่อนเริ่มฝึกขับ</span><span class="tl tl-no">Må gjøres før kjøretimer</span><span class="tl tl-en">Must be done before driving lessons</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">3</div>
        <div class="step-body">
          <h4><span class="tl tl-th">Trinn 2 — Veiledningstime (45 min)</span><span class="tl tl-no">Trinn 2 — Veiledningstime (45 min)</span><span class="tl tl-en">Step 2 — Guidance session (45 min)</span></h4>
          <p><span class="tl tl-th">ฝึกขับรถกับครูสอน เซสชัน 45 นาที เพื่อพัฒนาทักษะพื้นฐานบนถนน</span><span class="tl tl-no">Kjøring med trafikklærer. Veiledningstime på 45 minutter for grunnleggende kjøreferdigheter.</span><span class="tl tl-en">Driving with instructor. 45-minute guidance session for basic driving skills.</span></p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">4</div>
        <div class="step-body">
          <h4><span class="tl tl-th">Trinn 3 — Veiledningstime (60 min) + Sikkerhetskurs på bane (5 timer)</span><span class="tl tl-no">Trinn 3 — Veiledningstime (60 min) + Sikkerhetskurs på bane (5 timer)</span><span class="tl tl-en">Step 3 — Guidance (60 min) + Track safety course (5 hours)</span></h4>
          <p><span class="tl tl-th">ฝึกขับ 60 นาทีกับครู + หลักสูตรความปลอดภัยบนสนาม 5 ชั่วโมง (Glattkjøring — ขับบนถนนลื่น/น้ำแข็ง)</span><span class="tl tl-no">Veiledningstime på 60 minutter + Sikkerhetskurs på bane på 5 timer (Glattkjøring — kjøring på glatt underlag).</span><span class="tl tl-en">60-min guidance session + 5-hour track safety course (Glattkjøring — driving on slippery/icy surface).</span></p>
          <span class="warn"><span class="tl tl-th">ต้องผ่าน Trinn 2 ก่อน!</span><span class="tl tl-no">Må ha fullført Trinn 2 først!</span><span class="tl tl-en">Must complete Step 2 first!</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">5</div>
        <div class="step-body">
          <h4><span class="tl tl-th">Trinn 4 — Sikkerhetskurs på vei (5+4 timer)</span><span class="tl tl-no">Trinn 4 — Sikkerhetskurs på vei (5+4 timer)</span><span class="tl tl-en">Step 4 — Road safety course (5+4 hours)</span></h4>
          <p><span class="tl tl-th">🚗 <strong>5 ชั่วโมงแรก:</strong> ขับทางไกลบนถนนนอกเมืองพร้อมครูผู้สอนช่วยเหลือ<br/>🎓 <strong>4 ชั่วโมงสุดท้าย:</strong> ผู้เรียนต้องขับอย่างอิสระ 100% — ครูไม่ช่วย ต้องผ่านด้วยตัวเอง</span><span class="tl tl-no">🚗 <strong>Første 5 timer:</strong> Langkjøring på landevei med hjelp fra trafikklærer<br/>🎓 <strong>Siste 4 timer:</strong> Eleven kjører 100% selvstendig — må klare seg helt på egen hånd</span><span class="tl tl-en">🚗 <strong>First 5 hours:</strong> Long-distance driving on country roads with instructor assistance<br/>🎓 <strong>Last 4 hours:</strong> Student drives completely independently — must manage entirely on their own</span></p>
          <span class="note"><span class="tl tl-th">สุดท้ายก่อนสอบ — ที่โรงเรียนสอนขับ</span><span class="tl tl-no">Siste obligatoriske hos trafikklærer</span><span class="tl tl-en">Last mandatory step at driving school</span></span>
        </div>
      </div>
    </div>

    <p style="font-size:13px;font-weight:700;color:#10B981;margin-top:24px;margin-bottom:12px">
      🏛️ <span class="tl tl-th">ที่ Statens Vegvesen (2 ขั้นสุดท้าย)</span><span class="tl tl-no">Hos Statens Vegvesen (2 siste)</span><span class="tl tl-en">At Statens Vegvesen (last 2 steps)</span>
    </p>
    <div class="steps-list">
      <div class="step-item">
        <div class="step-num">6</div>
        <div class="step-body">
          <h4><span class="tl tl-th">Teoriprøve — สอบทฤษฎี</span><span class="tl tl-no">Teoriprøven</span><span class="tl tl-en">Theory test</span></h4>
          <p><span class="tl tl-th">45 ข้อ — ต้องได้ 85% (ผิดได้ไม่เกิน 7 ข้อ) เวลา 90 นาที ค่าสอบ ~300 kr<br/>⏰ สอบได้ตั้งแต่อายุ <strong>16 ปีครึ่ง</strong> — ผลสอบใช้ได้ <strong>3 ปี</strong></span><span class="tl tl-no">45 spørsmål — minst 85% riktig (maks 7 feil). 90 min. ~300 kr.<br/>⏰ Kan tas fra <strong>16,5 år</strong> — gyldig i <strong>3 år</strong></span><span class="tl tl-en">45 questions — at least 85% correct (max 7 wrong). 90 min. ~300 kr.<br/>⏰ Can be taken from <strong>16.5 years</strong> — valid for <strong>3 years</strong></span></p>
          <span class="note"><span class="tl tl-th">ฝึกกับ Thai2Drive! 📱</span><span class="tl tl-no">Øv med Thai2Drive! 📱</span><span class="tl tl-en">Practice with Thai2Drive! 📱</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">7</div>
        <div class="step-body">
          <h4><span class="tl tl-th">Førerprøve — สอบขับ</span><span class="tl tl-no">Førerprøven (kjøreprøven)</span><span class="tl tl-en">Driving test</span></h4>
          <p><span class="tl tl-th">ขับรถกับผู้ตรวจสอบจาก Statens Vegvesen 60 นาที ค่าสอบ ~1 000 kr<br/>ต้องผ่านทุกขั้นตอนก่อนนี้แล้ว!</span><span class="tl tl-no">Kjøring med sensor fra Statens Vegvesen. 60 min. ~1 000 kr.<br/>Alle obligatoriske trinn MÅ være fullført!</span><span class="tl tl-en">Drive with an examiner from Statens Vegvesen. 60 min. ~1 000 kr.<br/>All mandatory steps must be completed first!</span></p>
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 4: WHAT YOU LEARN PER TRINN -->
  <div class="section">
    <div class="section-num">4</div>
    <h2><span class="tl tl-th">สิ่งที่คุณต้องเรียนรู้ในแต่ละขั้น</span><span class="tl tl-no">Hva du lærer i hvert trinn</span><span class="tl tl-en">What you learn in each step</span></h2>
    <p class="lead">
      <span class="tl tl-th">เนื้อหาหลักสูตรอย่างเป็นทางการตาม Trafikkopplæringsforskriften</span>
      <span class="tl tl-no">Offisiell læreplan iht. Trafikkopplæringsforskriften (§ 11)</span>
      <span class="tl tl-en">Official curriculum according to Trafikkopplæringsforskriften (§ 11)</span>
    </p>

    <!-- TRINN 1 -->
    <div class="card" style="margin-bottom:14px;border-left:3px solid #FF9933">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <div class="step-num" style="width:32px;height:32px;border-radius:50%;background:#FF9933;color:#0F172A;font-weight:800;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0">1</div>
        <h3 style="font-size:16px"><span class="tl tl-th">Trafikalt grunnkurs (TGK)</span><span class="tl tl-no">Trafikalt grunnkurs (TGK)</span><span class="tl tl-en">Basic Traffic Course (TGK)</span></h3>
      </div>
      <p style="font-size:13px;color:#FF9933;font-weight:700;margin-bottom:8px">
        <span class="tl tl-th">🎯 เป้าหมาย: เข้าใจความรับผิดชอบของผู้ขับขี่และความปลอดภัยบนถนน</span>
        <span class="tl tl-no">🎯 Mål: Forstå ansvar som fører og trygg ferdsel i trafikken</span>
        <span class="tl tl-en">🎯 Goal: Understand driver responsibility and safe road behaviour</span>
      </p>
      <div style="display:grid;gap:6px">
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          📖 <strong><span class="tl tl-th">กฎจราจรพื้นฐาน</span><span class="tl tl-no">Grunnleggende trafikkregler</span><span class="tl tl-en">Basic traffic rules</span></strong>
          <span class="tl tl-th"> — ลำดับสิทธิ์ ความเร็ว การวางตัวรถ สัญญาณไฟ ป้ายจราจร</span>
          <span class="tl tl-no"> — vikeplikt, fart, plassering, skilt, vegoppmerking</span>
          <span class="tl tl-en"> — right of way, speed, positioning, signs, road markings</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🧠 <strong><span class="tl tl-th">มนุษย์กับการจราจร</span><span class="tl tl-no">Mennesket i trafikken</span><span class="tl tl-en">Human factors in traffic</span></strong>
          <span class="tl tl-th"> — ความรับผิดชอบ การตัดสินใจ อารมณ์ และการสื่อสารบนถนน</span>
          <span class="tl tl-no"> — ansvar, motivasjon, følelser og kommunikasjon i trafikken</span>
          <span class="tl tl-en"> — responsibility, motivation, emotions and communication in traffic</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🚑 <strong><span class="tl tl-th">การปฐมพยาบาล (ภาคปฏิบัติ)</span><span class="tl tl-no">Førstehjelp (praktisk øvelse)</span><span class="tl tl-en">First aid (practical exercise)</span></strong>
          <span class="tl tl-th"> — ฝึกจริงในสถานการณ์อุบัติเหตุจำลอง: HLKR, การโทรแจ้งเหตุ, การช่วยเหลือเบื้องต้น</span>
          <span class="tl tl-no"> — øver på arrangert ulykke: varsling, sikring av skadested, HLR</span>
          <span class="tl tl-en"> — practice on staged accident: calling for help, securing scene, CPR</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🌙 <strong><span class="tl tl-th">การขับในความมืด (MørkeDemo)</span><span class="tl tl-no">Kjøring i mørket (MørkeDemo)</span><span class="tl tl-en">Night driving (MørkeDemo)</span></strong>
          <span class="tl tl-th"> — สาธิตสด ≥1 ชม. กลางแจ้ง + ≥1 ชม. บนถนนจริง เพื่อเข้าใจอันตรายในยามค่ำคืน</span>
          <span class="tl tl-no"> — min. 1 t utendørs demo + min. 1 t på veg i mørket — forstå risiko og riktig lysbruk</span>
          <span class="tl tl-en"> — min. 1 hr outdoor demo + min. 1 hr on real road — understand risk and correct light use</span>
        </div>
      </div>
      <div style="margin-top:10px;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);border-radius:8px;padding:8px 12px;font-size:12px;color:#10B981;font-weight:600">
        ⚠️ <span class="tl tl-th">อายุ 25+ ปี: ทำแค่ Førstehjelp + MørkeDemo เท่านั้น — ไม่ต้องเรียนครบทั้งหมด!</span>
        <span class="tl tl-no">Over 25 år: Kun Førstehjelp + MørkeDemo — slipper resten av TGK!</span>
        <span class="tl tl-en">Over 25: Only First aid + Night demo required — skip the rest of TGK!</span>
      </div>
    </div>

    <!-- TRINN 2 -->
    <div class="card" style="margin-bottom:14px;border-left:3px solid #3B82F6">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <div class="step-num" style="width:32px;height:32px;border-radius:50%;background:#3B82F6;color:#fff;font-weight:800;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0">2</div>
        <h3 style="font-size:16px"><span class="tl tl-th">Trinn 2 — ทักษะพื้นฐานการขับขี่ (Veiledningstime 45 min)</span><span class="tl tl-no">Trinn 2 — Grunnleggende kjøreteknikk (Veiledningstime 45 min)</span><span class="tl tl-en">Step 2 — Basic driving skills (Guidance 45 min)</span></h3>
      </div>
      <p style="font-size:13px;color:#3B82F6;font-weight:700;margin-bottom:8px">
        <span class="tl tl-th">🎯 เป้าหมาย: ควบคุมรถได้ดีพอที่จะเริ่มฝึกในสภาพจราจรจริง</span>
        <span class="tl tl-no">🎯 Mål: God nok kontroll over bilen til å begynne trafikal opplæring i trinn 3</span>
        <span class="tl tl-en">🎯 Goal: Good enough vehicle control to start traffic training in step 3</span>
      </p>
      <div style="display:grid;gap:6px">
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🚗 <strong><span class="tl tl-th">โครงสร้างรถและความปลอดภัย</span><span class="tl tl-no">Bilens oppbygning og sikkerhet</span><span class="tl tl-en">Vehicle structure and safety</span></strong>
          <span class="tl tl-th"> — ระบบความปลอดภัยแอคทีฟ/แพสซีฟ เข็มขัดนิรภัย ไฟ ยาง การตรวจเช็ครถก่อนออกเดินทาง</span>
          <span class="tl tl-no"> — aktiv/passiv sikkerhet, belter, lys, dekk, sikkerhetskontroll før kjøring</span>
          <span class="tl tl-en"> — active/passive safety, belts, lights, tyres, pre-drive safety check</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🎮 <strong><span class="tl tl-th">การควบคุมรถขั้นพื้นฐาน</span><span class="tl tl-no">Grunnleggende kjøretøybehandling</span><span class="tl tl-en">Basic vehicle handling</span></strong>
          <span class="tl tl-th"> — ท่านั่ง การออกตัว การเบรก การเปลี่ยนเกียร์ การถอยหลัง การจอด ในพื้นที่จราจรน้อย</span>
          <span class="tl tl-no"> — sittestilling, igangsetting, bremsing, giring, rygging, parkering i lite trafikk</span>
          <span class="tl tl-en"> — seating position, starting, braking, gearing, reversing, parking in low traffic</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          ⚡ <strong><span class="tl tl-th">การเบรกฉุกเฉิน</span><span class="tl tl-no">Nødbremsing</span><span class="tl tl-en">Emergency braking</span></strong>
          <span class="tl tl-th"> — ฝึกเร่งความเร็วปกติถึง 60 กม./ชม. และเบรกหนักเพื่อหยุดก่อนสิ่งกีดขวาง</span>
          <span class="tl tl-no"> — øver på normalakselerasjon til 60 km/t og hard bremsing foran hindring</span>
          <span class="tl tl-en"> — practise normal acceleration to 60 km/h and hard braking before obstacle</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          📋 <strong><span class="tl tl-th">Trinnvurdering (45 นาที — บังคับ)</span><span class="tl tl-no">Trinnvurdering (45 min — obligatorisk)</span><span class="tl tl-en">Step assessment (45 min — mandatory)</span></strong>
          <span class="tl tl-th"> — ครูและนักเรียนประเมินร่วมกันว่าผ่านเกณฑ์พร้อมเรียน Trinn 3 หรือยัง</span>
          <span class="tl tl-no"> — elev og lærer vurderer sammen om grunnlaget for trinn 3 er tilstrekkelig</span>
          <span class="tl tl-en"> — student and instructor jointly assess readiness for step 3</span>
        </div>
      </div>
    </div>

    <!-- TRINN 3 -->
    <div class="card" style="margin-bottom:14px;border-left:3px solid #8B5CF6">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <div class="step-num" style="width:32px;height:32px;border-radius:50%;background:#8B5CF6;color:#fff;font-weight:800;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0">3</div>
        <h3 style="font-size:16px"><span class="tl tl-th">Trinn 3 — การฝึกในสภาพจราจร (Veiledningstime 60 min + Bane 5 timer)</span><span class="tl tl-no">Trinn 3 — Trafikal opplæring (Veiledningstime 60 min + Bane 5 timer)</span><span class="tl tl-en">Step 3 — Traffic training (Guidance 60 min + Track 5 hours)</span></h3>
      </div>
      <p style="font-size:13px;color:#8B5CF6;font-weight:700;margin-bottom:8px">
        <span class="tl tl-th">🎯 เป้าหมาย: ขับอย่างชัดเจน ปลอดภัย และอิสระในสภาพจราจรหลากหลาย</span>
        <span class="tl tl-no">🎯 Mål: Kjøre tydelig, sikkert og selvstendig i variert trafikk</span>
        <span class="tl tl-en">🎯 Goal: Drive clearly, safely and independently in varied traffic</span>
      </p>
      <div style="display:grid;gap:6px">
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🏙️ <strong><span class="tl tl-th">ขับในเมือง ชุมชน และทางหลวง</span><span class="tl tl-no">Kjøring i by, tettsted og landevei</span><span class="tl tl-en">Driving in city, town and country road</span></strong>
          <span class="tl tl-th"> — การวางตัว ความเร็ว การแซง การขับในอุโมงค์ และในความมืด</span>
          <span class="tl tl-no"> — plassering, fart, forbikjøring, tunnel og mørkekjøring</span>
          <span class="tl tl-en"> — positioning, speed, overtaking, tunnels and night driving</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          👁️ <strong><span class="tl tl-th">การมองถนนอย่างเป็นระบบ</span><span class="tl tl-no">Systematisk informasjonsinnhenting</span><span class="tl tl-en">Systematic visual scanning</span></strong>
          <span class="tl tl-th"> — มองไกล ขยับสายตาสม่ำเสมอ มองหาทางออก เห็นและถูกเห็น</span>
          <span class="tl tl-no"> — se langt frem, beveg blikket, finn utvei, se og bli sett</span>
          <span class="tl tl-en"> — look far ahead, scan constantly, find escape route, see and be seen</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🤝 <strong><span class="tl tl-th">การร่วมใช้ถนนกับผู้อื่น</span><span class="tl tl-no">Samhandling med alle trafikanter</span><span class="tl tl-en">Interaction with all road users</span></strong>
          <span class="tl tl-th"> — คนเดินเท้า นักปั่นจักรยาน รถบรรทุก รถจักรยานยนต์ — สื่อสารและร่วมมือ</span>
          <span class="tl tl-no"> — fotgjengere, syklister, lastebiler, motorsykler — kommunikasjon og samhandling</span>
          <span class="tl tl-en"> — pedestrians, cyclists, trucks, motorcycles — communication and co-operation</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          📋 <strong><span class="tl tl-th">Trinnvurdering (45 นาที — บังคับ)</span><span class="tl tl-no">Trinnvurdering (45 min — obligatorisk)</span><span class="tl tl-en">Step assessment (45 min — mandatory)</span></strong>
          <span class="tl tl-th"> — ครูและนักเรียนประเมินร่วมกันว่าพร้อมสำหรับ Trinn 4 หรือยัง</span>
          <span class="tl tl-no"> — elev og lærer vurderer sammen om eleven er klar for trinn 4</span>
          <span class="tl tl-en"> — student and instructor assess readiness for step 4</span>
        </div>
        <div style="background:rgba(139,92,246,.1);border:1px solid rgba(139,92,246,.3);border-radius:8px;padding:10px 12px;font-size:13px;color:#C4B5FD">
          🏎️ <strong><span class="tl tl-th">Sikkerhetskurs på bane — SKB (5 ชั่วโมง บังคับ)</span><span class="tl tl-no">Sikkerhetskurs på bane — SKB (5 timer, obligatorisk)</span><span class="tl tl-en">Track safety course — SKB (5 hours, mandatory)</span></strong><br/>
          <span class="tl tl-th" style="display:block;margin-top:4px">ฝึกบนสนามพิเศษ: ทดสอบการเบรก, ขับบนถนนลื่น (glattkjøring), ทดสอบระบบ ABS, ฝึกควบคุมรถในสถานการณ์ฉุกเฉิน</span>
          <span class="tl tl-no" style="display:block;margin-top:4px">Øver på bane: nødbremsing, kjøring på glatt underlag, ABS-test, kontroll ved krisesituasjoner</span>
          <span class="tl tl-en" style="display:block;margin-top:4px">On-track practice: emergency braking, driving on slippery surface, ABS test, vehicle control in crisis situations</span>
        </div>
      </div>
    </div>

    <!-- TRINN 4 -->
    <div class="card" style="margin-bottom:14px;border-left:3px solid #10B981">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
        <div class="step-num" style="width:32px;height:32px;border-radius:50%;background:#10B981;color:#fff;font-weight:800;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0">4</div>
        <h3 style="font-size:16px"><span class="tl tl-th">Trinn 4 — Sikkerhetskurs på vei (5+4 ชั่วโมง)</span><span class="tl tl-no">Trinn 4 — Sikkerhetskurs på vei (5+4 timer)</span><span class="tl tl-en">Step 4 — Road safety course (5+4 hours)</span></h3>
      </div>
      <p style="font-size:13px;color:#10B981;font-weight:700;margin-bottom:8px">
        <span class="tl tl-th">🎯 เป้าหมาย: ขับอิสระ 100% ระบุความเสี่ยง และเลือกวิธีขับที่ปลอดภัยที่สุด</span>
        <span class="tl tl-no">🎯 Mål: Kjøre 100% selvstendig, identifisere risiko og velge trygg kjøremåte</span>
        <span class="tl tl-en">🎯 Goal: Drive 100% independently, identify risk and choose safe driving behaviour</span>
      </p>
      <div style="display:grid;gap:6px">
        <div style="background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🚗 <strong><span class="tl tl-th">5 ชั่วโมงแรก — ขับทางไกลกับครู</span><span class="tl tl-no">Første 5 timer — langkjøring med lærer</span><span class="tl tl-en">First 5 hours — long drive with instructor</span></strong>
          <span class="tl tl-th"><br/>ขับบนถนนนอกเมืองที่มีมาตรฐานต่างกัน ระบุและอธิบายความเสี่ยง เรียนรู้การขับเข้า/ออกถนนใหญ่</span>
          <span class="tl tl-no"><br/>Kjøring på landeveg med varierende standard, identifiser risiko, øv på inn-/avkjøring fra større veg</span>
          <span class="tl tl-en"><br/>Drive on varied country roads, identify risk factors, practise entering/exiting main roads</span>
        </div>
        <div style="background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          🎓 <strong><span class="tl tl-th">4 ชั่วโมงสุดท้าย — ขับอิสระ 100%</span><span class="tl tl-no">Siste 4 timer — 100% selvstendig kjøring</span><span class="tl tl-en">Last 4 hours — 100% independent driving</span></strong>
          <span class="tl tl-th"><br/>ขับคนเดียวในสภาพแวดล้อมหลากหลาย (ทางหลวง เมือง) ครูไม่ช่วยเหลือ เขียนบันทึก (logg)</span>
          <span class="tl tl-no"><br/>Kjøring alene i skiftende miljø (landeveg + by), lærer griper ikke inn, skriv logg</span>
          <span class="tl tl-en"><br/>Drive alone in varying environment (highway + city), no instructor help, write driving log</span>
        </div>
        <div style="background:rgba(255,255,255,.04);border-radius:8px;padding:10px 12px;font-size:13px;color:#CBD5E1">
          📝 <strong><span class="tl tl-th">การสะท้อนผลและสรุป</span><span class="tl tl-no">Refleksjon og oppsummering</span><span class="tl tl-en">Reflection and summary</span></strong>
          <span class="tl tl-th"> — อภิปรายกับเพื่อน/ครู ประเมินจุดแข็งและจุดที่ต้องพัฒนาของตัวเอง</span>
          <span class="tl tl-no"> — diskusjon med medelever og lærer, vurder egne sterke og svake sider</span>
          <span class="tl tl-en"> — discuss with classmates and instructor, evaluate own strengths and weaknesses</span>
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 5: COSTS -->
  <div class="section">
    <div class="section-num">5</div>
    <h2><span class="tl tl-th">ค่าใช้จ่ายโดยรวม</span><span class="tl tl-no">Totale kostnader</span><span class="tl tl-en">Total costs</span></h2>
    <p class="lead">
      <span class="tl tl-th">ประมาณการค่าใช้จ่ายในการเรียนขับรถในนอร์เวย์</span>
      <span class="tl tl-no">Estimerte kostnader for full opplæring i Norge</span>
      <span class="tl tl-en">Estimated costs for full training in Norway</span>
    </p>
    <table class="cost-table">
      <tr>
        <td><span class="tl tl-th">หลักสูตรพื้นฐาน (TG)</span><span class="tl tl-no">Trafikalt grunnkurs</span><span class="tl tl-en">Basic traffic course</span></td>
        <td>~3 500 kr</td>
      </tr>
      <tr>
        <td><span class="tl tl-th">ชั่วโมงฝึกขับ (25 ชม.)</span><span class="tl tl-no">Kjøretimer (25 t.)</span><span class="tl tl-en">Driving lessons (25 hrs)</span></td>
        <td>~17 500 kr</td>
      </tr>
      <tr>
        <td><span class="tl tl-th">หลักสูตรบังคับ 3 วิชา</span><span class="tl tl-no">Obligatoriske kurs</span><span class="tl tl-en">Mandatory courses</span></td>
        <td>~6 000 kr</td>
      </tr>
      <tr>
        <td><span class="tl tl-th">ค่าสอบทฤษฎี</span><span class="tl tl-no">Teoriprøve</span><span class="tl tl-en">Theory test</span></td>
        <td>~300 kr</td>
      </tr>
      <tr>
        <td><span class="tl tl-th">ค่าสอบขับ</span><span class="tl tl-no">Kjøreprøve</span><span class="tl tl-en">Driving test</span></td>
        <td>~1 000 kr</td>
      </tr>
      <tr>
        <td><strong><span class="tl tl-th">รวมทั้งหมด (โดยประมาณ)</span><span class="tl tl-no">Totalt (estimert)</span><span class="tl tl-en">Total (estimated)</span></strong></td>
        <td>~28 000 – 40 000 kr</td>
      </tr>
    </table>
  </div>

  <!-- PDF BANNER (members only, shown by JS) -->
  <div id="pdf-banner" class="pdf-banner">
    <p>
      <span class="tl tl-th">📄 คุณเป็นสมาชิก Thai2Drive — ดาวน์โหลดคู่มือนี้เป็น PDF ได้เลย!</span>
      <span class="tl tl-no">📄 Du er Thai2Drive-medlem — last ned denne guiden som PDF!</span>
      <span class="tl tl-en">📄 You're a Thai2Drive member — download this guide as a PDF!</span>
    </p>
    <button class="pdf-btn" onclick="downloadPDF()">⬇️ <span class="tl tl-th">ดาวน์โหลด PDF</span><span class="tl tl-no">Last ned PDF</span><span class="tl tl-en">Download PDF</span></button>
  </div>

  <!-- CTA -->
  <div class="cta-box">
    <h2><span class="tl tl-th">พร้อมสอบทฤษฎีแล้วหรือยัง?</span><span class="tl tl-no">Klar til å øve på teoriprøven?</span><span class="tl tl-en">Ready to practice the theory test?</span></h2>
    <p><span class="tl tl-th">ฝึกกับคำถาม 700+ ข้อ บน Thai2Drive — เป็นภาษาไทย นอร์เวย์ และอังกฤษ</span><span class="tl tl-no">Øv med 700+ spørsmål på Thai2Drive — på thai, norsk og engelsk</span><span class="tl tl-en">Practice with 700+ questions on Thai2Drive — in Thai, Norwegian and English</span></p>
    <a href="/api/website" class="cta-btn">🚀 <span class="tl tl-th">ฝึกฟรี</span><span class="tl tl-no">Prøv gratis</span><span class="tl tl-en">Try free</span></a>
  </div>

</div><!-- /container -->

<footer>
  <p>© 2025 Thai2Drive · <a href="/api/privacy">Personvern</a> · <a href="/api/terms">Vilkår</a></p>
</footer>

<script>{_JS}</script>
</body>
</html>"""
