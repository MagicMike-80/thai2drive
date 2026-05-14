"""
High-conversion landing page for Thai2Drive.
Renders all 3 languages (th / no / en) inline — JS swaps visibility
so language switching is INSTANT with no server round-trip.
"""
from __future__ import annotations

ICON_URL = "/api/assets/developer-icon-512.png"
HEADER_URL = "/api/assets/developer-header-4096x2304.jpg"
QR_URL = "/api/assets/qr-download.png"

# Phone screenshot paths (produced earlier)
SCREENSHOTS = [
    "/api/assets/screenshots/01-home-thai.jpg",
    "/api/assets/screenshots/04-quiz-question.jpg",
    "/api/assets/screenshots/03-categories.jpg",
    "/api/assets/screenshots/06-paywall.jpg",
    "/api/assets/screenshots/08-bookmarks.jpg",
]


LANDING_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  background:#0B1226;color:#E2E8F0;line-height:1.55;
  -webkit-font-smoothing:antialiased;overflow-x:hidden;
}
a{color:#FF9933;text-decoration:none;transition:opacity .2s}
a:hover{opacity:.8}
.container{max-width:1120px;margin:0 auto;padding:0 24px}

/* hide/show by language */
[data-lang]{display:none}
html[data-current-lang="th"] [data-lang="th"],
html[data-current-lang="no"] [data-lang="no"],
html[data-current-lang="en"] [data-lang="en"]{display:inline}
[data-lang].block{display:none}
html[data-current-lang="th"] [data-lang="th"].block,
html[data-current-lang="no"] [data-lang="no"].block,
html[data-current-lang="en"] [data-lang="en"].block{display:block}

/* NAV */
.nav{
  position:sticky;top:0;z-index:50;
  background:rgba(11,18,38,.85);backdrop-filter:blur(12px);
  border-bottom:1px solid rgba(255,255,255,.08);
}
.nav-inner{display:flex;align-items:center;justify-content:space-between;padding:12px 24px;max-width:1200px;margin:0 auto;gap:16px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;color:#fff;flex-shrink:0}
.brand img{width:36px;height:36px;border-radius:8px}
.brand .t2d{color:#FF9933}
.lang-row{display:flex;gap:6px}
.lang-btn{
  width:60px;height:60px;border-radius:50%;border:2.5px solid transparent;
  background:rgba(255,255,255,.06);cursor:pointer;
  display:flex;align-items:center;justify-content:center;padding:0;overflow:hidden;
  transition:border-color .15s,transform .15s,box-shadow .15s;
  box-shadow:0 2px 8px rgba(0,0,0,.3);
  font-size:24px;line-height:1;
}
.lang-btn:hover{transform:scale(1.1);box-shadow:0 4px 16px rgba(0,0,0,.4)}
.lang-btn.active{border-color:#FF9933;background:rgba(255,153,51,.18);box-shadow:0 0 0 3px rgba(255,153,51,.25)}
.mini-flag{display:flex;flex-direction:column;width:38px;height:26px;border-radius:3px;overflow:hidden;flex-shrink:0}
.mini-flag.flag-th span:nth-child(1){background:#A51931;flex:1}
.mini-flag.flag-th span:nth-child(2){background:#F4F5F8;flex:1}
.mini-flag.flag-th span:nth-child(3){background:#2D2A4A;flex:2}
.mini-flag.flag-th span:nth-child(4){background:#F4F5F8;flex:1}
.mini-flag.flag-th span:nth-child(5){background:#A51931;flex:1}
.mini-flag.flag-no{background:#BA0C2F;position:relative;display:block}
.mini-flag.flag-no .b{position:absolute;left:0;right:0;top:40%;height:20%;background:#fff}
.mini-flag.flag-no .bv{position:absolute;left:25%;top:0;bottom:0;width:20%;background:#fff}
.mini-flag.flag-no::before{content:'';position:absolute;left:0;right:0;top:45%;height:10%;background:#00205B}
.mini-flag.flag-no::after{content:'';position:absolute;left:29%;top:0;bottom:0;width:10%;background:#00205B}
.mini-flag.flag-gb{background:#012169;position:relative;display:block}
.mini-flag.flag-gb .r1{position:absolute;left:0;right:0;top:42%;height:16%;background:#C8102E}
.mini-flag.flag-gb .r2{position:absolute;left:42%;top:0;bottom:0;width:16%;background:#C8102E}
.mini-flag.flag-gb::before{content:'';position:absolute;left:0;right:0;top:36%;height:28%;background:#fff}
.mini-flag.flag-gb::after{content:'';position:absolute;left:36%;top:0;bottom:0;width:28%;background:#fff}
.flag{width:30px;height:20px;border-radius:3px;overflow:hidden;display:flex;flex-direction:column}
.flag-th>div:nth-child(1){background:#A51931;flex:1}
.flag-th>div:nth-child(2){background:#F4F5F8;flex:1}
.flag-th>div:nth-child(3){background:#2D2A4A;flex:2}
.flag-th>div:nth-child(4){background:#F4F5F8;flex:1}
.flag-th>div:nth-child(5){background:#A51931;flex:1}
.flag-no{background:#BA0C2F;position:relative}
.flag-no::before,.flag-no::after{content:'';position:absolute;background:#fff}
.flag-no::before{left:0;right:0;top:38%;height:22%}
.flag-no::after{left:22%;top:0;bottom:0;width:22%}
.flag-no .b1,.flag-no .b2{position:absolute;background:#00205B}
.flag-no .b1{left:0;right:0;top:45%;height:10%}
.flag-no .b2{left:26%;top:0;bottom:0;width:10%}
.flag-gb{background:#012169;position:relative}
.flag-gb::before,.flag-gb::after{content:'';position:absolute;background:#fff}
.flag-gb::before{left:0;right:0;top:40%;height:20%}
.flag-gb::after{left:40%;top:0;bottom:0;width:20%}
.flag-gb .r1,.flag-gb .r2{position:absolute;background:#C8102E}
.flag-gb .r1{left:0;right:0;top:45%;height:10%}
.flag-gb .r2{left:45%;top:0;bottom:0;width:10%}
.t2d-lang-badge{width:28px;height:28px;border-radius:50%;overflow:hidden}

/* HERO */
.hero{padding:64px 0 56px;text-align:center;position:relative}
.hero::before{
  content:'';position:absolute;top:-20%;left:50%;transform:translateX(-50%);
  width:900px;height:600px;background:radial-gradient(closest-side,rgba(255,153,51,.12),transparent 70%);
  pointer-events:none;z-index:-1;
}
.hero-icon{width:110px;height:110px;border-radius:26px;box-shadow:0 30px 80px rgba(255,153,51,.25);margin-bottom:24px}
.hero h1{
  font-size:clamp(34px,5.5vw,60px);font-weight:900;letter-spacing:-.02em;
  line-height:1.08;color:#fff;margin-bottom:18px;
  max-width:820px;margin-left:auto;margin-right:auto;
}
.hero h1 em{font-style:normal;color:#FF9933}
.hero .sub{font-size:clamp(16px,2.2vw,20px);color:#94A3B8;max-width:620px;margin:0 auto 28px}
.cta-group{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:12px}
.cta-btn{
  display:inline-flex;align-items:center;gap:8px;padding:16px 28px;border-radius:12px;
  font-weight:800;font-size:16px;cursor:pointer;border:none;transition:transform .15s,opacity .15s;
  text-decoration:none;
}
.cta-btn:hover{transform:translateY(-2px)}
.cta-primary{background:#FF9933;color:#0F172A;box-shadow:0 16px 40px rgba(255,153,51,.35)}
.cta-secondary{background:rgba(255,255,255,.06);color:#fff;border:1.5px solid rgba(255,255,255,.15)}

.qr-box{
  display:inline-flex;align-items:center;gap:14px;
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
  padding:14px 18px 14px 14px;border-radius:14px;margin-top:24px;
}
.qr-box img{width:96px;height:96px;border-radius:8px;background:#fff;padding:6px;flex-shrink:0}
.qr-text{text-align:left;font-size:13px;color:#CBD5E1;font-weight:600;max-width:200px}
.qr-text small{display:block;color:#64748B;font-weight:500;margin-top:3px;font-size:11px}

/* badges */
.hero-badges{display:flex;justify-content:center;gap:10px;margin-top:30px;flex-wrap:wrap}
.badge-chip{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:999px;font-size:13px;color:#CBD5E1}
.badge-chip .ok{width:6px;height:6px;background:#10B981;border-radius:50%}

/* SECTIONS */
section{padding:72px 0;position:relative}
.sec-head{text-align:center;max-width:720px;margin:0 auto 44px}
.eyebrow{display:inline-block;color:#FF9933;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.12em;margin-bottom:12px}
.sec-head h2{font-size:clamp(26px,4vw,38px);font-weight:800;color:#fff;margin-bottom:10px;letter-spacing:-.01em}
.sec-head p{color:#94A3B8;font-size:16px}

/* TRY-IN-BROWSER */
.try-panel{
  max-width:720px;margin:0 auto;border-radius:24px;
  background:linear-gradient(180deg,rgba(255,153,51,.06),rgba(255,255,255,.02));
  border:1px solid rgba(255,153,51,.2);overflow:hidden;
}
.try-head{padding:16px 20px;display:flex;justify-content:space-between;align-items:center;background:rgba(255,153,51,.05);border-bottom:1px solid rgba(255,153,51,.15)}
.try-progress{color:#CBD5E1;font-size:13px;font-weight:700}
.try-progress .accent{color:#FF9933}
.try-bar{flex:1;height:5px;background:rgba(255,255,255,.08);border-radius:3px;margin:0 16px;overflow:hidden}
.try-bar>div{height:100%;background:#FF9933;transition:width .3s;width:0%}
.try-body{padding:16px 20px}
.try-image{width:100%;max-height:180px;object-fit:contain;border-radius:10px;margin-bottom:12px;background:#0B1226}
.try-question{font-size:17px;font-weight:700;color:#fff;margin-bottom:16px;line-height:1.4}
.try-options{display:grid;gap:10px}
.try-opt{
  background:rgba(255,255,255,.04);border:1.5px solid rgba(255,255,255,.08);
  padding:14px 18px;border-radius:12px;cursor:pointer;font-size:14px;text-align:left;color:#E2E8F0;
  display:flex;align-items:center;gap:12px;transition:border-color .15s,background .15s;font-family:inherit;width:100%;
}
.try-opt:hover{border-color:rgba(255,153,51,.4)}
.try-opt.correct{border-color:#10B981;background:rgba(16,185,129,.1)}
.try-opt.wrong{border-color:#EF4444;background:rgba(239,68,68,.1)}
.try-opt.correct-marker{border-color:#10B981}
.try-opt .letter{
  width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,.06);
  display:inline-flex;align-items:center;justify-content:center;font-weight:800;flex-shrink:0;
}
.try-opt.correct .letter,.try-opt.correct-marker .letter{background:#10B981;color:#fff}
.try-opt.wrong .letter{background:#EF4444;color:#fff}
.try-explain{margin-top:16px;padding:14px;background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.25);border-radius:10px;font-size:14px;color:#CBD5E1;line-height:1.5}
.try-hint{margin-top:14px;padding:14px 16px;border-radius:10px;font-size:14px;line-height:1.45;text-align:center;animation:pop .25s ease-out}
.try-hint.ok{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);color:#10B981}
.try-hint.bad{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.25);color:#FCA5A5}
.try-hint strong{color:inherit}
@keyframes pop{from{transform:translateY(6px);opacity:0}to{transform:translateY(0);opacity:1}}
.try-foot{padding:16px 24px;border-top:1px solid rgba(255,255,255,.08);text-align:right}
.try-next{padding:10px 24px;border-radius:10px;background:#FF9933;color:#0F172A;font-weight:800;border:none;cursor:pointer;font-size:14px}
.try-next:disabled{opacity:.4;cursor:not-allowed}
.try-loading{text-align:center;padding:60px 20px;color:#94A3B8}

/* Paywall shown inline after 10 */
.try-paywall{text-align:center;padding:40px 24px}
.try-paywall h3{font-size:24px;color:#fff;margin-bottom:10px;font-weight:800}
.try-paywall p{color:#94A3B8;margin-bottom:24px;max-width:440px;margin-left:auto;margin-right:auto}
.try-paywall .lock-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;background:rgba(255,153,51,.15);color:#FF9933;border-radius:999px;font-size:12px;font-weight:700;margin-bottom:14px}
.plans-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;max-width:640px;margin:0 auto 20px}
.plan-mini{background:rgba(255,255,255,.04);border:1.5px solid rgba(255,255,255,.1);border-radius:12px;padding:16px;text-align:left}
.plan-mini.best{border-color:#FF9933;background:rgba(255,153,51,.06)}
.plan-mini h4{font-size:13px;color:#94A3B8;font-weight:600;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em}
.plan-mini .p{font-size:22px;color:#fff;font-weight:800}
.plan-mini .p small{font-size:11px;color:#94A3B8;font-weight:500}

/* Why Thai2Drive */
.why-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.why-item{
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
  padding:22px;border-radius:14px;display:flex;align-items:center;gap:16px;
  transition:border-color .2s,background .2s,transform .2s;
}
.why-item:hover{border-color:rgba(255,153,51,.3);background:rgba(255,153,51,.04);transform:translateY(-2px)}
.why-num{
  flex-shrink:0;width:42px;height:42px;border-radius:50%;
  background:rgba(255,153,51,.15);color:#FF9933;
  display:flex;align-items:center;justify-content:center;
  font-weight:900;font-size:18px;
}
.why-item h3{color:#fff;font-size:15px;font-weight:700;line-height:1.3}

/* FEATURES */
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px}
.feat{
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
  padding:26px;border-radius:16px;transition:all .2s;
}
.feat:hover{border-color:rgba(255,153,51,.3);background:rgba(255,153,51,.03);transform:translateY(-2px)}
.feat-icon{width:44px;height:44px;border-radius:10px;background:rgba(255,153,51,.15);color:#FF9933;display:flex;align-items:center;justify-content:center;font-size:22px;margin-bottom:14px}
.feat h3{font-size:16px;color:#fff;font-weight:700;margin-bottom:6px}
.feat p{color:#94A3B8;font-size:14px;line-height:1.5}

/* TRUST */
.trust{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.trust-card{
  text-align:center;padding:22px;background:rgba(255,255,255,.03);
  border:1px solid rgba(255,255,255,.06);border-radius:14px;
}
.trust-icon{font-size:32px;margin-bottom:10px}
.trust-card h4{color:#fff;font-size:15px;font-weight:700;margin-bottom:4px}
.trust-card p{color:#94A3B8;font-size:13px}

/* SCREENSHOTS */
.shots{display:flex;gap:16px;overflow-x:auto;padding:10px 0 20px;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch}
.shot{
  flex-shrink:0;width:230px;aspect-ratio:9/19.5;
  border-radius:28px;overflow:hidden;background:#0B1226;
  border:3px solid rgba(255,255,255,.08);
  box-shadow:0 20px 50px rgba(0,0,0,.4);
  scroll-snap-align:center;
}
.shot img{width:100%;height:100%;object-fit:cover;display:block}

/* CTA BAND */
.cta-band{
  background:linear-gradient(135deg,rgba(255,153,51,.1),rgba(255,153,51,.02));
  border-top:1px solid rgba(255,153,51,.2);border-bottom:1px solid rgba(255,153,51,.2);
  text-align:center;padding:64px 24px;
}
.cta-band h2{font-size:clamp(24px,3.5vw,34px);color:#fff;font-weight:800;margin-bottom:10px}
.cta-band p{color:#94A3B8;max-width:480px;margin:0 auto 24px}

/* FOOTER */
footer{padding:40px 0 32px;border-top:1px solid rgba(255,255,255,.06);margin-top:40px}
.footer-inner{display:flex;justify-content:space-between;flex-wrap:wrap;gap:20px;align-items:center}
footer p{color:#64748B;font-size:13px}
.footer-links{display:flex;gap:18px;flex-wrap:wrap}
.footer-links a{color:#94A3B8;font-size:13px}

/* RESPONSIVE */
@media (max-width:720px){
  .nav-inner{padding:10px 14px;gap:8px}
  .brand{font-size:16px}
  .brand img{width:32px;height:32px}
  .lang-btn{width:34px;height:34px}
  .hero{padding:48px 0 40px}
  section{padding:52px 0}
  .cta-band{padding:48px 20px}
  .qr-box{flex-direction:column;text-align:center;padding:16px}
  .qr-text{max-width:none;text-align:center}
  .shot{width:190px;border-width:2px}
}
"""


def _nav_html() -> str:
    return f"""
<nav class="nav">
  <div class="nav-inner">
    <a href="/api/website" class="brand">
      <img src="{ICON_URL}" alt="T2D"/>
      <span>Thai<span class="t2d">2</span>Drive</span>
    </a>
    <div class="lang-row" role="group" aria-label="Language">
      <button class="lang-btn active" data-set-lang="th" aria-label="ไทย"><span class="mini-flag flag-th"><span></span><span></span><span></span><span></span><span></span></span></button>
      <button class="lang-btn" data-set-lang="no" aria-label="Norsk"><span class="mini-flag flag-no"><span class="b"></span><span class="bv"></span></span></button>
      <button class="lang-btn" data-set-lang="en" aria-label="English"><span class="mini-flag flag-gb"><span class="r1"></span><span class="r2"></span></span></button>
    </div>
  </div>
</nav>
"""


def _footer_html() -> str:
    return """
<footer>
  <div class="container">
    <div class="footer-inner">
      <p>© 2025 Thai2Drive</p>
      <div class="footer-links">
        <a href="/api/website"><span data-lang="th">หน้าแรก</span><span data-lang="no">Hjem</span><span data-lang="en">Home</span></a>
        <a href="/api/privacy"><span data-lang="th">ความเป็นส่วนตัว</span><span data-lang="no">Personvern</span><span data-lang="en">Privacy</span></a>
        <a href="/api/terms"><span data-lang="th">เงื่อนไข</span><span data-lang="no">Vilkår</span><span data-lang="en">Terms</span></a>
        <a href="/api/support"><span data-lang="th">ช่วยเหลือ</span><span data-lang="no">Support</span><span data-lang="en">Support</span></a>
      </div>
    </div>
  </div>
</footer>
"""


def _hero_html() -> str:
    return f"""
<section class="hero">
  <div class="container">
    <img src="{ICON_URL}" alt="Thai2Drive" class="hero-icon"/>

    <h1>
      <span data-lang="th" class="block">สอบใบขับขี่นอร์เวย์ให้ <em>ผ่านครั้งแรก</em></span>
      <span data-lang="no" class="block">Bestå teoriprøven <em>på første forsøk</em></span>
      <span data-lang="en" class="block">Pass the Norwegian theory test <em>on your first try</em></span>
    </h1>

    <p class="sub">
      <span data-lang="th" class="block">ฝึกด้วยคำถามกว่า 500 ข้อ พร้อมคำอธิบาย ใน 3 ภาษา</span>
      <span data-lang="no" class="block">Øv med 500+ spørsmål med forklaringer på 3 språk</span>
      <span data-lang="en" class="block">Practice with 500+ questions with explanations in 3 languages</span>
    </p>

    <div class="cta-group">
      <a href="#try" class="cta-btn cta-primary">
        <span data-lang="th">🚀 เริ่มฝึกฟรี</span>
        <span data-lang="no">🚀 Prøv gratis</span>
        <span data-lang="en">🚀 Try free</span>
      </a>
      <a href="#download" class="cta-btn cta-secondary">
        📱
        <span data-lang="th">ดาวน์โหลดแอป</span>
        <span data-lang="no">Last ned app</span>
        <span data-lang="en">Download app</span>
      </a>
    </div>

    <div class="qr-box" id="download">
      <img src="{QR_URL}" alt="QR code"/>
      <div class="qr-text">
        <span data-lang="th" class="block">สแกนเพื่อดาวน์โหลดแอปทันที<small>เปิดลิงก์บนมือถือก็ได้</small></span>
        <span data-lang="no" class="block">Scan for å laste ned appen direkte<small>eller åpne lenken på mobil</small></span>
        <span data-lang="en" class="block">Scan to download the app instantly<small>or open the link on mobile</small></span>
      </div>
    </div>

    <div class="hero-badges">
      <span class="badge-chip"><span class="ok"></span>
        <span data-lang="th">มากกว่า 500 ข้อ</span>
        <span data-lang="no">500+ spørsmål</span>
        <span data-lang="en">500+ questions</span>
      </span>
      <span class="badge-chip">🇹🇭🇳🇴
        <span data-lang="th">ใช้โดยคนไทยในนอร์เวย์</span>
        <span data-lang="no">Brukt av thai i Norge</span>
        <span data-lang="en">Used by Thai in Norway</span>
      </span>
      <span class="badge-chip">📜
        <span data-lang="th">อัปเดตตามกฎล่าสุด</span>
        <span data-lang="no">Oppdatert etter regler</span>
        <span data-lang="en">Updated to latest rules</span>
      </span>
    </div>
  </div>
</section>
"""


def _try_html() -> str:
    return """
<section id="try">
  <div class="container">
    <div class="sec-head">
      <span class="eyebrow">
        <span data-lang="th">ลองเลย</span><span data-lang="no">Prøv nå</span><span data-lang="en">Try now</span>
      </span>
      <h2>
        <span data-lang="th" class="block">เริ่มฝึกในเบราว์เซอร์</span>
        <span data-lang="no" class="block">Prøv quizen i nettleseren</span>
        <span data-lang="en" class="block">Try the quiz in your browser</span>
      </h2>
      <p>
        <span data-lang="th">10 ข้อฟรี · ไม่ต้องสมัครสมาชิก · ก่อนตัดสินใจ</span>
        <span data-lang="no">10 gratis spørsmål · ingen registrering · før du bestemmer deg</span>
        <span data-lang="en">10 free questions · no signup · before you decide</span>
      </p>
    </div>

    <div class="try-panel" id="tryPanel">
      <div class="try-head">
        <span class="try-progress"><span class="accent" id="tqNow">1</span> / <span id="tqTotal">10</span></span>
        <div class="try-bar"><div id="tqBar"></div></div>
        <span class="try-progress" id="tqScore">0 ✓</span>
      </div>
      <div class="try-body" id="tqBody">
        <div class="try-loading">
          <span data-lang="th">กำลังโหลดคำถาม...</span>
          <span data-lang="no">Laster spørsmål...</span>
          <span data-lang="en">Loading questions...</span>
        </div>
      </div>
      <div class="try-foot">
        <button class="try-next" id="tqNext" disabled>
          <span data-lang="th">ถัดไป →</span>
          <span data-lang="no">Neste →</span>
          <span data-lang="en">Next →</span>
        </button>
      </div>
    </div>
  </div>
</section>
"""


def _why_html() -> str:
    return """
<section>
  <div class="container">
    <div class="sec-head">
      <span class="eyebrow">
        <span data-lang="th">ทำไม Thai2Drive</span>
        <span data-lang="no">Hvorfor Thai2Drive</span>
        <span data-lang="en">Why Thai2Drive</span>
      </span>
      <h2>
        <span data-lang="th" class="block">แอปนี้ต่างจากที่อื่นอย่างไร</span>
        <span data-lang="no" class="block">Hva gjør oss annerledes</span>
        <span data-lang="en" class="block">What makes us different</span>
      </h2>
    </div>
    <div class="why-grid">
      <div class="why-item">
        <div class="why-num">1</div>
        <h3>
          <span data-lang="th">ออกแบบสำหรับคนไทยในนอร์เวย์</span>
          <span data-lang="no">Laget for thai i Norge</span>
          <span data-lang="en">Made for Thai in Norway</span>
        </h3>
      </div>
      <div class="why-item">
        <div class="why-num">2</div>
        <h3>
          <span data-lang="th">มีคำอธิบายทุกข้อ</span>
          <span data-lang="no">Forklaring på alle svar</span>
          <span data-lang="en">Explanation for every answer</span>
        </h3>
      </div>
      <div class="why-item">
        <div class="why-num">3</div>
        <h3>
          <span data-lang="th">จำลองข้อสอบจริง</span>
          <span data-lang="no">Som ekte eksamen</span>
          <span data-lang="en">Real exam simulation</span>
        </h3>
      </div>
    </div>
  </div>
</section>
"""


def _features_html() -> str:
    features = [
        ('📚', {'th': '500+ คำถาม', 'no': '500+ spørsmål', 'en': '500+ questions'},
               {'th': 'ครอบคลุมทุกหมวดหมู่ของข้อสอบใบขับขี่นอร์เวย์',
                'no': 'Dekker alle kategoriene i den norske teoriprøven',
                'en': 'Covers every category of the Norwegian test'}),
        ('💡', {'th': 'คำอธิบายทุกข้อ', 'no': 'Forklaringer på alt', 'en': 'Explanations on every answer'},
               {'th': 'เข้าใจว่าทำไมคำตอบถึงถูก ไม่ใช่แค่จำ',
                'no': 'Forstå hvorfor et svar er riktig – ikke bare pugg',
                'en': 'Understand why an answer is correct — don\'t just memorise'}),
        ('🌐', {'th': '3 ภาษา', 'no': '3 språk', 'en': '3 languages'},
               {'th': 'ไทย นอร์เวย์ และอังกฤษ · สลับได้ตลอด',
                'no': 'Thai, norsk og engelsk · bytt når som helst',
                'en': 'Thai, Norwegian and English · switch any time'}),
        ('🎯', {'th': 'โหมดสอบจริง', 'no': 'Eksamensmodus', 'en': 'Exam mode'},
               {'th': '45 ข้อ · 90 นาที · เหมือนจริงทุกอย่าง',
                'no': '45 spørsmål · 90 min · akkurat som den ekte',
                'en': '45 questions · 90 min · just like the real one'}),
        ('📱', {'th': 'เรียนได้ทุกที่', 'no': 'Lær hvor som helst', 'en': 'Study anywhere'},
               {'th': 'ฝึกระหว่างทาง เก็บเป็นกิจวัตรประจำวัน',
                'no': 'Øv på bussen, lag deg en daglig rutine',
                'en': 'Practice on the go, build a daily habit'}),
    ]
    cards = []
    for icon, title, desc in features:
        cards.append(f"""
      <div class="feat">
        <div class="feat-icon">{icon}</div>
        <h3>
          <span data-lang="th">{title['th']}</span>
          <span data-lang="no">{title['no']}</span>
          <span data-lang="en">{title['en']}</span>
        </h3>
        <p>
          <span data-lang="th">{desc['th']}</span>
          <span data-lang="no">{desc['no']}</span>
          <span data-lang="en">{desc['en']}</span>
        </p>
      </div>""")
    return f"""
<section id="features">
  <div class="container">
    <div class="sec-head">
      <span class="eyebrow"><span data-lang="th">ฟีเจอร์</span><span data-lang="no">Funksjoner</span><span data-lang="en">Features</span></span>
      <h2>
        <span data-lang="th" class="block">ทุกอย่างที่คุณต้องการเพื่อสอบผ่าน</span>
        <span data-lang="no" class="block">Alt du trenger for å bestå</span>
        <span data-lang="en" class="block">Everything you need to pass</span>
      </h2>
    </div>
    <div class="features">
      {''.join(cards)}
    </div>
  </div>
</section>
"""


def _trust_html() -> str:
    return """
<section>
  <div class="container">
    <div class="trust">
      <div class="trust-card">
        <div class="trust-icon">🇹🇭🇳🇴</div>
        <h4>
          <span data-lang="th">ใช้โดยคนไทยในนอร์เวย์</span>
          <span data-lang="no">Brukt av thai-folk i Norge</span>
          <span data-lang="en">Used by Thais in Norway</span>
        </h4>
        <p>
          <span data-lang="th">แปลและตรวจสอบโดยเจ้าของภาษา</span>
          <span data-lang="no">Oversatt og verifisert av morsmålstalere</span>
          <span data-lang="en">Translated and verified by native speakers</span>
        </p>
      </div>
      <div class="trust-card">
        <div class="trust-icon">📜</div>
        <h4>
          <span data-lang="th">อัปเดตตามกฎปัจจุบัน</span>
          <span data-lang="no">Oppdatert etter gjeldende regler</span>
          <span data-lang="en">Updated to current rules</span>
        </h4>
        <p>
          <span data-lang="th">สอดคล้องกับ Statens vegvesen</span>
          <span data-lang="no">I tråd med Statens vegvesen</span>
          <span data-lang="en">Aligned with Statens vegvesen</span>
        </p>
      </div>
      <div class="trust-card">
        <div class="trust-icon">🎯</div>
        <h4>
          <span data-lang="th">ออกแบบมาเพื่อให้ผ่าน</span>
          <span data-lang="no">Designet for å bestå</span>
          <span data-lang="en">Designed to help you pass</span>
        </h4>
        <p>
          <span data-lang="th">เน้นรูปแบบเดียวกับข้อสอบจริง</span>
          <span data-lang="no">Samme format som den ekte prøven</span>
          <span data-lang="en">Same format as the real test</span>
        </p>
      </div>
    </div>
  </div>
</section>
"""


def _screenshots_html() -> str:
    shots = ''.join(f'<div class="shot"><img src="{s}" alt="Screenshot" loading="lazy"/></div>' for s in SCREENSHOTS)
    return f"""
<section>
  <div class="container">
    <div class="sec-head">
      <span class="eyebrow"><span data-lang="th">แอป</span><span data-lang="no">Appen</span><span data-lang="en">The app</span></span>
      <h2>
        <span data-lang="th" class="block">ออกแบบให้ใช้ง่าย</span>
        <span data-lang="no" class="block">Bygd for å være enkel</span>
        <span data-lang="en" class="block">Designed to feel effortless</span>
      </h2>
    </div>
  </div>
  <div class="container" style="padding-left:0;padding-right:0">
    <div class="shots" style="padding-left:24px;padding-right:24px">
      {shots}
    </div>
  </div>
</section>
"""


def _bottom_cta_html() -> str:
    return f"""
<section class="cta-band">
  <div class="container">
    <h2>
      <span data-lang="th" class="block">พร้อมจะสอบผ่านหรือยัง?</span>
      <span data-lang="no" class="block">Klar til å bestå?</span>
      <span data-lang="en" class="block">Ready to pass?</span>
    </h2>
    <p>
      <span data-lang="th">เริ่มฟรีตอนนี้ – ไม่ต้องกรอกบัตร</span>
      <span data-lang="no">Start gratis nå – ingen kortinformasjon</span>
      <span data-lang="en">Start free now – no credit card needed</span>
    </p>
    <div class="cta-group">
      <a href="#try" class="cta-btn cta-primary">
        <span data-lang="th">🚀 เริ่มฝึกฟรี</span>
        <span data-lang="no">🚀 Prøv gratis</span>
        <span data-lang="en">🚀 Try free</span>
      </a>
      <a href="#download" class="cta-btn cta-secondary">
        📱 <span data-lang="th">ดาวน์โหลดแอป</span><span data-lang="no">Last ned app</span><span data-lang="en">Download app</span>
      </a>
    </div>
    <div class="qr-box" style="margin-top:20px">
      <img src="{QR_URL}" alt="QR code"/>
      <div class="qr-text">
        <span data-lang="th" class="block">สแกนเพื่อดาวน์โหลดแอปทันที<small>บน iOS และ Android</small></span>
        <span data-lang="no" class="block">Scan for å laste ned appen direkte<small>på iOS og Android</small></span>
        <span data-lang="en" class="block">Scan to download the app instantly<small>on iOS and Android</small></span>
      </div>
    </div>
  </div>
</section>
"""


LANDING_JS = r"""
// ─── Language switcher ───
(function(){
  const supported = ['th','no','en'];
  const saved = localStorage.getItem('t2d_landing_lang');
  const initial = supported.includes(saved) ? saved : 'th';
  document.documentElement.setAttribute('data-current-lang', initial);

  document.querySelectorAll('.lang-btn').forEach(btn=>{
    const code = btn.dataset.setLang;
    if(code === initial) btn.classList.add('active'); else btn.classList.remove('active');
    btn.addEventListener('click', ()=>{
      document.documentElement.setAttribute('data-current-lang', code);
      localStorage.setItem('t2d_landing_lang', code);
      document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active', b === btn));
    });
  });
})();

// ─── Try-in-browser quiz (1–2 questions then paywall) ───
(function(){
  const body = document.getElementById('tqBody');
  const nextBtn = document.getElementById('tqNext');
  const barEl = document.getElementById('tqBar');
  const nowEl = document.getElementById('tqNow');
  const totalEl = document.getElementById('tqTotal');
  const scoreEl = document.getElementById('tqScore');
  if(!body) return;

  const TOTAL = 10;  // 10 free questions before paywall
  let questions = [];
  let idx = 0;
  let score = 0;
  let answered = false;

  function currentLang(){
    return document.documentElement.getAttribute('data-current-lang') || 'th';
  }

  async function load(){
    try{
      // Image questions ONLY — filter out any without a valid base64/url image
      const res = await fetch('/api/questions/random?count=15&has_image=true');
      const raw = await res.json();
      questions = (raw || []).filter(q => q.bildeUrl && (typeof q.bildeUrl === 'string' || Object.keys(q.bildeUrl).length)).slice(0, TOTAL + 2);
      if(questions.length === 0){
        body.innerHTML = '<p style="text-align:center;color:#94A3B8;padding:30px">No image questions available right now.</p>';
        return;
      }
      totalEl.textContent = TOTAL;
      render();
    }catch(e){
      body.innerHTML = '<p style="text-align:center;color:#94A3B8;padding:30px">Could not load questions.</p>';
    }
  }

  function pick(obj, lang){
    if(!obj) return '';
    if(typeof obj === 'string') return obj;
    return obj[lang] || obj.no || obj.en || obj.th || Object.values(obj)[0] || '';
  }

  function render(){
    if(idx >= TOTAL){ renderPaywall(); return; }
    const q = questions[idx];
    if(!q){ renderPaywall(); return; }
    const lang = currentLang();
    answered = false;

    nowEl.textContent = idx + 1;
    barEl.style.width = ((idx)/TOTAL*100) + '%';
    scoreEl.innerHTML = score + ' ✓';

    const img = pick(q.bildeUrl, lang);
    const questionText = pick(q.question, lang);
    const opts = (q.options || []).map(o => ({
      id: o.id,
      text: pick(o.text, lang) || pick(o, lang),
    }));
    const expl = pick(q.explanation, lang);

    body.innerHTML =
      (img ? `<img class="try-image" src="${img}" alt="" onerror="this.style.display='none'"/>` : '') +
      `<div class="try-question">${escapeHtml(questionText)}</div>` +
      `<div class="try-options" id="tqOpts">` +
      opts.map(o => `<button class="try-opt" data-id="${o.id}"><span class="letter">${o.id}</span><span>${escapeHtml(o.text)}</span></button>`).join('') +
      `</div>` +
      `<div class="try-hint" id="tqHint" style="display:none"></div>` +
      `<div class="try-explain" id="tqExpl" style="display:none"></div>`;

    document.querySelectorAll('#tqOpts .try-opt').forEach(btn=>{
      btn.addEventListener('click', ()=>selectAnswer(btn, q, expl));
    });
    nextBtn.disabled = true;
  }

  function selectAnswer(btn, q, expl){
    if(answered) return;
    answered = true;
    const lang = currentLang();
    const picked = btn.dataset.id;
    const correct = q.correctOptionId;
    document.querySelectorAll('#tqOpts .try-opt').forEach(b=>{
      b.disabled = true;
      if(b.dataset.id === correct){
        b.classList.add(picked === correct ? 'correct' : 'correct-marker');
      }else if(b === btn){
        b.classList.add('wrong');
      }
    });
    if(picked === correct) score++;
    scoreEl.innerHTML = score + ' ✓';

    // Feedback hint message per the spec
    const isCorrect = picked === correct;
    const hintOK = { th: '🎉 ถูกต้อง!', no: '🎉 Riktig!', en: '🎉 Correct!' }[lang];
    const hintBad = { th: '❌ ไม่ถูกต้อง', no: '❌ Feil svar', en: '❌ Incorrect' }[lang];
    const continueMsg = {
      th: '✨ ใช้แอปต่อเพื่อปลดล็อกเต็มรูปแบบ',
      no: '✨ Fortsett i appen for å låse opp full tilgang',
      en: '✨ Continue in app to unlock full access',
    }[lang];
    const hint = document.getElementById('tqHint');
    hint.innerHTML = `<strong>${isCorrect ? hintOK : hintBad}</strong> · ${continueMsg}`;
    hint.className = 'try-hint ' + (isCorrect ? 'ok' : 'bad');
    hint.style.display = 'block';

    if(expl){
      const e = document.getElementById('tqExpl');
      e.textContent = expl;
      e.style.display = 'block';
    }
    nextBtn.disabled = false;
    nextBtn.onclick = ()=>{ idx++; render(); };
  }

  function renderPaywall(){
    const lang = currentLang();
    barEl.style.width = '100%';
    nowEl.textContent = TOTAL;
    const titles = {
      th: 'เริ่มใช้งานเต็มรูปแบบในแอป',
      no: 'Fortsett øvingen i appen',
      en: 'Continue practicing in the app',
    };
    const subs = {
      th: 'ดาวน์โหลดแอปเพื่อเข้าถึงคำถามทั้งหมด 500+ ข้อ พร้อมคำอธิบายและโหมดสอบจริง',
      no: 'Last ned appen for tilgang til alle 500+ spørsmål, forklaringer og ekte eksamensmodus.',
      en: 'Download the app for access to all 500+ questions, explanations, and real exam mode.',
    };
    const ctas = {
      th: 'ดาวน์โหลดแอปฟรี',
      no: 'Last ned app – gratis',
      en: 'Download app – free',
    };
    const scoreLbl = { th: 'คะแนนของคุณ', no: 'Din score', en: 'Your score' }[lang];
    const lockTxt = { th: 'ล็อกแล้ว', no: 'Låst', en: 'Locked' }[lang];
    const monthLbl = { th: 'รายเดือน', no: 'Månedlig', en: 'Monthly' }[lang];
    const threeLbl = { th: '3 เดือน', no: '3 måneder', en: '3 months' }[lang];
    const lifeLbl = { th: 'ตลอดชีพ', no: 'Livstid', en: 'Lifetime' }[lang];
    const perMo = { th: 'เดือน', no: 'mnd', en: 'mo' }[lang];
    const once = { th: 'ครั้งเดียว', no: 'éngangs', en: 'once' }[lang];

    body.innerHTML = `
      <div class="try-paywall">
        <span class="lock-badge">🔒 ${lockTxt}</span>
        <h3>${titles[lang]}</h3>
        <p>${subs[lang]}</p>
        <div class="plans-row">
          <div class="plan-mini"><h4>${monthLbl}</h4><div class="p">199 kr<small> / ${perMo}</small></div></div>
          <div class="plan-mini best"><h4>${threeLbl}</h4><div class="p">399 kr<small> / 3 ${perMo}</small></div></div>
          <div class="plan-mini"><h4>${lifeLbl}</h4><div class="p">699 kr<small> / ${once}</small></div></div>
        </div>
        <a href="#download" class="cta-btn cta-primary" style="margin-top:8px">${ctas[lang]} →</a>
        <p style="margin-top:14px;font-size:13px;color:#94A3B8">${scoreLbl}: <strong style="color:#FF9933">${score} / ${TOTAL}</strong></p>
      </div>`;
    nextBtn.disabled = true;
  }

  function escapeHtml(s){
    return String(s || '').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  load();

  // Re-render if user switches language mid-quiz (re-use current question)
  document.querySelectorAll('.lang-btn').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      if(questions.length && idx < TOTAL && !answered) render();
      else if(idx >= TOTAL) renderPaywall();
    });
  });
})();
"""


def build_landing_page(chat_css: str, chat_widget_html: str, chat_js: str) -> str:
    """Build the full landing HTML including the existing chat bubble."""
    # Local import to avoid circular + keep module import cheap.
    from site_config import public_site_url, canonical_url
    canon = canonical_url("/")
    og_image = public_site_url() + HEADER_URL  # absolute URL for social previews
    desc = "Bestå den norske teoriprøven – 500+ spørsmål på thai, norsk og engelsk. Laget for thai-folk i Norge."
    return f"""<!doctype html>
<html lang="th" data-current-lang="th">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Thai2Drive – สอบใบขับขี่นอร์เวย์ · Teoriprøve · Norwegian theory test</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="{canon}"/>
<meta property="og:title" content="Thai2Drive"/>
<meta property="og:description" content="Norsk teoriprøve på thai, norsk og engelsk"/>
<meta property="og:image" content="{og_image}"/>
<meta property="og:url" content="{canon}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="Thai2Drive"/>
<meta property="og:locale" content="nb_NO"/>
<meta name="google" content="notranslate"/>
<meta http-equiv="Content-Language" content="th,no,en"/>
<meta property="og:locale:alternate" content="th_TH"/>
<meta property="og:locale:alternate" content="en_US"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="Thai2Drive – Norsk teoriprøve"/>
<meta name="twitter:description" content="{desc}"/>
<meta name="twitter:image" content="{og_image}"/>
<link rel="icon" type="image/png" href="{ICON_URL}"/>
<link rel="apple-touch-icon" href="{ICON_URL}"/>
<style>{LANDING_CSS}{chat_css}</style>
</head>
<body>
{_nav_html()}
{_hero_html()}
{_try_html()}
{_why_html()}
{_features_html()}
{_trust_html()}
{_screenshots_html()}
{_bottom_cta_html()}
{_footer_html()}
{chat_widget_html}
<script>{LANDING_JS}</script>
<script>{chat_js}</script>
</body>
</html>"""
