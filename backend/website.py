"""
Public marketing website + legal pages for Thai2Drive.
All pages are styled in a unified dark theme matching the mobile app.
Mounted under /api/* so the k8s ingress routes them to the backend.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from site_config import public_site_url, site_url, canonical_url

website_router = APIRouter()

# Shared brand assets URL (served by /api/assets)
ICON_URL = "/api/assets/developer-icon-512.png"
HEADER_URL = "/api/assets/developer-header-4096x2304.jpg"
FEATURE_URL = "/api/assets/feature-graphic-1024x500.jpg"

BRAND = "Thai2Drive"
CONTACT_EMAIL = "lexuz.zxc@gmail.com"
LAST_UPDATED = "2. juni 2025"


_BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  background:#0B1226;color:#E2E8F0;line-height:1.6;
  -webkit-font-smoothing:antialiased;min-height:100vh;
}
a{color:#FF9933;text-decoration:none;transition:opacity .2s}
a:hover{opacity:.8}
.container{max-width:1120px;margin:0 auto;padding:0 24px}

/* Nav */
.nav{
  position:sticky;top:0;z-index:50;
  background:rgba(11,18,38,.85);backdrop-filter:blur(12px);
  border-bottom:1px solid rgba(255,255,255,.08);
}
.nav-inner{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;max-width:1120px;margin:0 auto}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;color:#fff}
.brand img{width:36px;height:36px;border-radius:8px}
.brand .t2d{color:#FF9933}
.nav ul{list-style:none;display:flex;gap:24px;align-items:center}
.nav ul a{color:#CBD5E1;font-size:14px;font-weight:500}
.nav ul a:hover{color:#FF9933}
.nav-cta{
  background:#FF9933;color:#0F172A;padding:8px 16px;border-radius:8px;
  font-weight:700;font-size:14px;
}
.nav-cta:hover{opacity:.92}

/* Hero */
.hero{padding:90px 0 80px;text-align:center}
.hero-icon{width:112px;height:112px;border-radius:26px;box-shadow:0 30px 80px rgba(255,153,51,.2)}
.hero h1{
  font-size:clamp(36px,6vw,64px);font-weight:900;letter-spacing:-.02em;
  margin:24px 0 16px;line-height:1.05;color:#fff;
}
.hero h1 span{color:#FF9933}
.hero p{font-size:clamp(16px,2vw,20px);color:#94A3B8;max-width:640px;margin:0 auto}
.hero-badges{display:flex;justify-content:center;gap:16px;margin-top:28px;flex-wrap:wrap}
.badge{
  display:inline-flex;align-items:center;gap:8px;padding:8px 16px;
  background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
  border-radius:999px;font-size:13px;color:#CBD5E1;
}
.badge .dot{width:8px;height:8px;background:#10B981;border-radius:50%}
.hero-cta{
  display:inline-flex;align-items:center;gap:10px;
  background:#FF9933;color:#0F172A;padding:16px 32px;border-radius:12px;
  font-weight:800;font-size:16px;margin-top:36px;
  box-shadow:0 20px 50px rgba(255,153,51,.25);
}
.hero-cta:hover{transform:translateY(-2px);transition:transform .15s}
.hero-cta-secondary{
  display:inline-flex;align-items:center;gap:10px;
  background:rgba(255,255,255,.08);color:#F1F5F9;padding:16px 32px;border-radius:12px;
  font-weight:700;font-size:16px;margin-top:36px;margin-left:12px;
  border:1px solid rgba(255,255,255,.15);
}
.hero-cta-secondary:hover{transform:translateY(-2px);transition:transform .15s;background:rgba(255,255,255,.14)}
.hero-btns{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:8px}

/* Flag chips */
.flags{display:inline-flex;gap:10px;margin-top:24px}
.flag{width:40px;height:28px;border-radius:4px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,.3);display:flex;flex-direction:column}
.flag-th div:nth-child(1){background:#A51931;flex:1}
.flag-th div:nth-child(2){background:#F4F5F8;flex:1}
.flag-th div:nth-child(3){background:#2D2A4A;flex:2}
.flag-th div:nth-child(4){background:#F4F5F8;flex:1}
.flag-th div:nth-child(5){background:#A51931;flex:1}
.flag-no{background:#BA0C2F;position:relative}
.flag-no::before,.flag-no::after{content:'';position:absolute;background:#fff}
.flag-no::before{left:0;right:0;top:38%;height:22%}
.flag-no::after{left:22%;top:0;bottom:0;width:22%}
.flag-no .blue,.flag-no .bluev{position:absolute;background:#00205B}
.flag-no .blue{left:0;right:0;top:44%;height:10%}
.flag-no .bluev{left:26%;top:0;bottom:0;width:10%}
.flag-gb{background:#012169;position:relative}
.flag-gb::before,.flag-gb::after{content:'';position:absolute;background:#fff}
.flag-gb::before{left:0;right:0;top:40%;height:20%}
.flag-gb::after{left:40%;top:0;bottom:0;width:20%}
.flag-gb .r1,.flag-gb .r2{position:absolute;background:#C8102E}
.flag-gb .r1{left:0;right:0;top:45%;height:10%}
.flag-gb .r2{left:45%;top:0;bottom:0;width:10%}

/* Sections */
section{padding:72px 0}
.section-head{text-align:center;max-width:640px;margin:0 auto 48px}
.section-head h2{font-size:clamp(28px,4vw,40px);font-weight:800;color:#fff;margin-bottom:12px}
.section-head p{color:#94A3B8;font-size:16px}
.eyebrow{
  display:inline-block;color:#FF9933;font-weight:700;
  font-size:12px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;
}

/* Features grid */
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}
.feature{
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
  padding:28px;border-radius:16px;transition:all .2s;
}
.feature:hover{border-color:rgba(255,153,51,.4);background:rgba(255,153,51,.04);transform:translateY(-2px)}
.feature-icon{
  width:44px;height:44px;border-radius:10px;
  background:rgba(255,153,51,.15);color:#FF9933;
  display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:16px;
}
.feature h3{font-size:17px;font-weight:700;color:#fff;margin-bottom:6px}
.feature p{color:#94A3B8;font-size:14px;line-height:1.55}

/* Pricing */
.pricing{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;max-width:960px;margin:0 auto}
.plan{
  background:rgba(255,255,255,.03);border:1.5px solid rgba(255,255,255,.08);
  padding:28px;border-radius:16px;position:relative;
}
.plan.popular{border-color:#FF9933;background:rgba(255,153,51,.05)}
.ribbon{
  position:absolute;top:-10px;right:20px;background:#FF9933;color:#0F172A;
  font-size:11px;font-weight:800;padding:4px 12px;border-radius:6px;text-transform:uppercase;letter-spacing:.05em;
}
.plan h3{font-size:15px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.price{font-size:40px;font-weight:900;color:#fff;margin:10px 0 4px}
.price small{font-size:14px;color:#94A3B8;font-weight:500}
.plan ul{list-style:none;margin-top:18px}
.plan ul li{padding:6px 0;font-size:14px;color:#CBD5E1;display:flex;gap:8px;align-items:flex-start}
.plan ul li::before{content:'✓';color:#10B981;font-weight:900;flex-shrink:0}

/* CTA band */
.cta-band{
  background:linear-gradient(135deg,rgba(255,153,51,.08),rgba(255,153,51,.02));
  border-top:1px solid rgba(255,153,51,.2);border-bottom:1px solid rgba(255,153,51,.2);
  text-align:center;padding:64px 24px;
}
.cta-band h2{font-size:clamp(24px,3.5vw,36px);color:#fff;font-weight:800;margin-bottom:12px}
.cta-band p{color:#94A3B8;max-width:500px;margin:0 auto 24px}

/* Footer */
footer{padding:48px 0 32px;border-top:1px solid rgba(255,255,255,.06);margin-top:40px}
.footer-inner{display:flex;justify-content:space-between;flex-wrap:wrap;gap:24px;align-items:center}
footer p{color:#64748B;font-size:13px}
.footer-links{display:flex;gap:20px;flex-wrap:wrap}
.footer-links a{color:#94A3B8;font-size:13px}

/* Legal pages */
.legal{padding:60px 24px 80px;max-width:820px;margin:0 auto}
.legal h1{font-size:36px;color:#fff;font-weight:800;margin-bottom:8px}
.legal .meta{color:#64748B;margin-bottom:36px;font-size:13px}
.legal h2{font-size:20px;color:#FF9933;font-weight:700;margin:36px 0 12px}
.legal h3{font-size:16px;color:#fff;font-weight:700;margin:20px 0 8px}
.legal p,.legal li{color:#CBD5E1;margin:8px 0;font-size:15px;line-height:1.7}
.legal ul{margin-left:22px}
.legal strong{color:#fff}
.legal .box{
  background:rgba(255,153,51,.06);border:1px solid rgba(255,153,51,.2);
  padding:16px 20px;border-radius:10px;margin:20px 0;
}

@media (max-width:720px){
  .nav ul{gap:14px;font-size:13px}
  .nav ul li:not(:last-child){display:none}
  section{padding:52px 0}
  .hero{padding:60px 0 56px}
}
"""


# ─── AI Chat widget (bubble bottom-right) ────────────────────────────────
_CHAT_CSS = """
/* Chat widget */
.t2d-chat-fab{
  position:fixed;bottom:20px;right:20px;z-index:9999;
  width:68px;height:68px;border-radius:34px;
  background:linear-gradient(135deg,#10B981,#059669);
  border:none;cursor:pointer;color:#fff;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 12px 32px rgba(16,185,129,.5),0 4px 12px rgba(0,0,0,.3);
  transition:transform .2s;
}
.t2d-chat-fab:hover{transform:scale(1.08)}
.t2d-chat-fab svg{width:26px;height:26px}
.t2d-chat-badge{
  position:absolute;top:-4px;right:-4px;background:#EF4444;color:#fff;
  width:22px;height:22px;border-radius:11px;font-size:11px;font-weight:800;
  display:flex;align-items:center;justify-content:center;border:2px solid #0B1226;
}
.t2d-chat-panel{
  position:fixed;bottom:88px;right:20px;z-index:9998;
  width:360px;max-width:calc(100vw - 32px);height:540px;max-height:calc(100vh - 120px);
  background:#0F172A;border:1px solid rgba(255,255,255,.1);border-radius:18px;
  box-shadow:0 30px 80px rgba(0,0,0,.5);
  display:none;flex-direction:column;overflow:hidden;
}
.t2d-chat-panel.open{display:flex;animation:slideUp .2s ease-out}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
.t2d-chat-head{
  padding:14px 16px;background:linear-gradient(135deg,rgba(255,153,51,.1),rgba(255,153,51,.02));
  border-bottom:1px solid rgba(255,255,255,.08);
  display:flex;align-items:center;gap:12px;
}
.t2d-chat-head img{width:36px;height:36px;border-radius:9px}
.t2d-chat-head-info{flex:1}
.t2d-chat-head-info strong{display:block;color:#fff;font-size:14px;font-weight:700}
.t2d-chat-head-info span{font-size:11px;color:#10B981;display:flex;align-items:center;gap:5px}
.t2d-chat-head-info span::before{content:'';width:6px;height:6px;background:#10B981;border-radius:50%}
.t2d-chat-close{
  background:rgba(255,255,255,.06);border:none;color:#CBD5E1;
  width:30px;height:30px;border-radius:8px;cursor:pointer;font-size:16px;
  display:flex;align-items:center;justify-content:center;
}
.t2d-chat-close:hover{background:rgba(255,255,255,.12)}
.t2d-chat-body{
  flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;
  background:#0B1226;
}
.t2d-msg{max-width:85%;padding:10px 14px;border-radius:14px;font-size:14px;line-height:1.4;word-wrap:break-word;white-space:pre-wrap}
.t2d-msg.bot{align-self:flex-start;background:rgba(255,255,255,.06);color:#E2E8F0;border-bottom-left-radius:4px}
.t2d-msg.user{align-self:flex-end;background:#FF9933;color:#0F172A;border-bottom-right-radius:4px;font-weight:500}
.t2d-msg.system{align-self:center;background:rgba(16,185,129,.12);color:#10B981;font-size:12px;padding:6px 12px;border-radius:12px;text-align:center;max-width:90%}
.t2d-typing{align-self:flex-start;background:rgba(255,255,255,.06);padding:10px 14px;border-radius:14px;display:flex;gap:4px}
.t2d-typing span{width:6px;height:6px;background:#94A3B8;border-radius:50%;animation:bounce 1.4s infinite ease-in-out}
.t2d-typing span:nth-child(2){animation-delay:.2s}
.t2d-typing span:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,80%,100%{transform:scale(.6);opacity:.5}40%{transform:scale(1);opacity:1}}
.t2d-chat-foot{
  padding:12px;border-top:1px solid rgba(255,255,255,.08);background:#0F172A;
  display:flex;gap:8px;
}
.t2d-chat-input{
  flex:1;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);
  color:#fff;padding:10px 14px;border-radius:10px;font-size:14px;outline:none;font-family:inherit;
}
.t2d-chat-input:focus{border-color:#FF9933}
.t2d-chat-input::placeholder{color:#64748B}
.t2d-chat-send{
  background:#FF9933;border:none;color:#0F172A;padding:0 16px;border-radius:10px;
  font-weight:800;font-size:14px;cursor:pointer;display:flex;align-items:center;gap:4px;
}
.t2d-chat-send:disabled{opacity:.5;cursor:not-allowed}
.t2d-chat-disclaimer{font-size:10px;color:#64748B;text-align:center;padding:4px 12px 8px;background:#0F172A;border-top:1px solid rgba(255,255,255,.04)}
.t2d-quick-chips{display:flex;flex-wrap:wrap;gap:6px;padding:8px 14px 0}
.t2d-quick-chips button{
  background:rgba(255,153,51,.08);border:1px solid rgba(255,153,51,.25);color:#FF9933;
  padding:5px 10px;border-radius:14px;font-size:11px;cursor:pointer;font-family:inherit;
}
.t2d-quick-chips button:hover{background:rgba(255,153,51,.18)}

@media (max-width:480px){
  .t2d-chat-fab{width:54px;height:54px;bottom:16px;right:16px}
  .t2d-chat-panel{right:12px;bottom:80px;width:calc(100vw - 24px);height:calc(100vh - 110px)}
}
"""

_CHAT_WIDGET_HTML = """
<!-- Support Chat Bubble -->
<button class="t2d-chat-fab" id="t2dChatFab" aria-label="Support chat" title="Spør support">
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3C6.48 3 2 6.58 2 11c0 2.03.94 3.87 2.47 5.27L3 21l4.93-1.61c1.24.38 2.62.61 4.07.61 5.52 0 10-3.58 10-8S17.52 3 12 3z"/></svg>
  <span class="t2d-chat-badge" id="t2dChatBadge" style="display:none">1</span>
</button>

<div class="t2d-chat-panel" id="t2dChatPanel" role="dialog" aria-label="Support chat">
  <div class="t2d-chat-head">
    <img src="/api/assets/developer-icon-512.png" alt=""/>
    <div class="t2d-chat-head-info">
      <strong>Thai2Drive Support</strong>
      <span>AI-assistent · svarer direkte</span>
    </div>
    <button class="t2d-chat-close" id="t2dChatClose" aria-label="Lukk">✕</button>
  </div>

  <div class="t2d-chat-body" id="t2dChatBody"></div>

  <div class="t2d-quick-chips" id="t2dQuickChips">
    <button data-q="Hvordan kansellerer jeg abonnementet?">🛑 Avslutt abonnement</button>
    <button data-q="Premium ble ikke aktivert etter kjøp">⚠️ Premium virker ikke</button>
    <button data-q="Hvordan tilbakestiller jeg passordet?">🔑 Glemt passord</button>
    <button data-q="Hvordan sletter jeg kontoen min?">🗑 Slett konto</button>
  </div>

  <form class="t2d-chat-foot" id="t2dChatForm">
    <input class="t2d-chat-input" id="t2dChatInput" placeholder="Spør om Thai2Drive..." autocomplete="off" maxlength="500"/>
    <button type="submit" class="t2d-chat-send" id="t2dChatSend">Send</button>
  </form>

  <div class="t2d-chat-disclaimer">
    AI-svar. Viktige saker videresendes automatisk til support.
  </div>
</div>
"""

_CHAT_JS = r"""
(function(){
  const fab = document.getElementById('t2dChatFab');
  const panel = document.getElementById('t2dChatPanel');
  const closeBtn = document.getElementById('t2dChatClose');
  const body = document.getElementById('t2dChatBody');
  const form = document.getElementById('t2dChatForm');
  const input = document.getElementById('t2dChatInput');
  const send = document.getElementById('t2dChatSend');
  const chips = document.getElementById('t2dQuickChips');
  const badge = document.getElementById('t2dChatBadge');
  if(!fab||!panel) return;

  let sessionId = localStorage.getItem('t2d_chat_session') || '';
  let typingEl = null;
  let greeted = false;

  function getLang(){
    return document.documentElement.getAttribute('data-current-lang') || document.documentElement.lang || 'no';
  }

  // Reset session if user changed language since last visit
  (function(){
    const storedLang = localStorage.getItem('t2d_chat_lang') || '';
    if(sessionId && storedLang && storedLang !== getLang()){
      sessionId = '';
      localStorage.removeItem('t2d_chat_session');
    }
  })();

  function scrollBottom(){ body.scrollTop = body.scrollHeight; }

  function addMsg(role, text){
    const d = document.createElement('div');
    d.className = 't2d-msg ' + role;
    d.textContent = text;
    body.appendChild(d);
    scrollBottom();
    return d;
  }

  function showTyping(){
    if(typingEl) return;
    typingEl = document.createElement('div');
    typingEl.className = 't2d-typing';
    typingEl.innerHTML = '<span></span><span></span><span></span>';
    body.appendChild(typingEl);
    scrollBottom();
  }
  function hideTyping(){ if(typingEl){ typingEl.remove(); typingEl = null; } }

  function openChat(){
    panel.classList.add('open');
    badge.style.display = 'none';
    if(!greeted){
      greeted = true;
      // Pick greeting based on page language (landing / app / support)
      const lang = getLang();
      const greetings = {
        th: 'ต้องการความช่วยเหลือไหม? ถามได้เลยเกี่ยวกับ Thai2Drive 👋',
        no: 'Trenger du hjelp med teoriprøven? Spør meg om Thai2Drive 👋',
        en: 'Need help passing the theory test? Ask me anything about Thai2Drive 👋',
      };
      addMsg('bot', greetings[lang] || greetings.no);
    }
    setTimeout(()=>input.focus(), 200);
  }
  function closeChat(){ panel.classList.remove('open'); }

  fab.addEventListener('click', ()=> panel.classList.contains('open') ? closeChat() : openChat());
  closeBtn.addEventListener('click', closeChat);

  chips.addEventListener('click', (e)=>{
    if(e.target.tagName === 'BUTTON' && e.target.dataset.q){
      input.value = e.target.dataset.q;
      form.dispatchEvent(new Event('submit'));
    }
  });

  async function sendMessage(text){
    addMsg('user', text);
    showTyping();
    send.disabled = true;

    try{
      const lang = getLang();
      // Reset session if language changed while panel was open
      const storedLang = localStorage.getItem('t2d_chat_lang') || '';
      if(sessionId && storedLang && storedLang !== lang){
        sessionId = '';
        localStorage.removeItem('t2d_chat_session');
      }
      const res = await fetch('/api/support/chat', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ session_id: sessionId || null, message: text, language: lang })
      });
      const data = await res.json();
      hideTyping();

      if(data.session_id){
        sessionId = data.session_id;
        localStorage.setItem('t2d_chat_session', sessionId);
        localStorage.setItem('t2d_chat_lang', lang);
      }
      addMsg('bot', data.reply || 'Beklager, ingen svar akkurat nå. Prøv igjen om litt.');

      if(data.escalated){
        addMsg('system', '✓ Meldingen din er videresendt til supportteamet');
      }
    }catch(err){
      hideTyping();
      addMsg('bot', 'Beklager, nettverksfeil. Send e-post til lexuz.zxc@gmail.com hvis det haster.');
    }finally{
      send.disabled = false;
    }
  }

  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    const t = input.value.trim();
    if(!t) return;
    input.value = '';
    sendMessage(t);
  });

  // Auto-open on /support after 1.5s as a friendly nudge (first visit only)
  if(location.pathname.includes('/support') && !localStorage.getItem('t2d_chat_seen')){
    setTimeout(()=>{
      badge.style.display = 'flex';
      localStorage.setItem('t2d_chat_seen','1');
    }, 1500);
  }
})();
"""


def _nav(lang_links=True):
    return f"""
<nav class="nav">
  <div class="nav-inner">
    <a href="/api/website" class="brand">
      <img src="{ICON_URL}" alt="{BRAND}"/>
      <span>Thai<span class="t2d">2</span>Drive</span>
    </a>
    <ul>
      <li><a href="/api/website#features">Funksjoner</a></li>
      <li><a href="/api/website#pricing">Priser</a></li>
      <li><a href="/api/guide">📖 Guide</a></li>
      <li><a href="/api/bok">📚 Læringsbok</a></li>
      <li><a href="/api/support">Support</a></li>
      <li><a href="/api/privacy">Personvern</a></li>
    </ul>
  </div>
</nav>
"""


def _footer():
    return f"""
<footer>
  <div class="container">
    <div class="footer-inner">
      <p>© 2025 {BRAND}. Alle rettigheter reservert.</p>
      <div class="footer-links">
        <a href="/api/website">Hjem</a>
        <a href="/api/bok">Læringsbok</a>
        <a href="/api/privacy">Personvernregler</a>
        <a href="/api/terms">Vilkår</a>
        <a href="/api/support">Kontakt</a>
      </div>
    </div>
  </div>
</footer>
"""


def _page(title: str, body: str, description: str = "", path: str = "/"):
    desc = description or 'Thai2Drive – Norsk teoriprøve på thai, norsk og engelsk. Laget for thai-folk i Norge.'
    canon = canonical_url(path)
    og_image = public_site_url() + HEADER_URL  # absolute URL for social previews
    return f"""<!doctype html>
<html lang="no">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="{canon}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:image" content="{og_image}"/>
<meta property="og:url" content="{canon}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="{BRAND}"/>
<meta property="og:locale" content="nb_NO"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{desc}"/>
<meta name="twitter:image" content="{og_image}"/>
<link rel="icon" type="image/png" href="{ICON_URL}"/>
<link rel="apple-touch-icon" href="{ICON_URL}"/>
<style>{_BASE_CSS}{_CHAT_CSS}</style>
</head>
<body>
{_nav()}
{body}
{_footer()}
{_CHAT_WIDGET_HTML}
<script>{_CHAT_JS}</script>
</body>
</html>"""


# ─────────────────────────── LANDING PAGE ───────────────────────────
@website_router.get("/website", response_class=HTMLResponse)
@website_router.get("/", response_class=HTMLResponse)  # fallback inside /api
def landing():
    # Delegate to the new high-conversion landing page module.
    from landing import build_landing_page  # local import to keep server import-time cheap
    html = build_landing_page(
        chat_css=_CHAT_CSS,
        chat_widget_html=_CHAT_WIDGET_HTML,
        chat_js=_CHAT_JS,
    )
    return HTMLResponse(html)
    body = f"""
<!-- HERO -->
<section class="hero container">
  <img src="{ICON_URL}" alt="{BRAND} app icon" class="hero-icon" loading="lazy"/>
  <h1>Bestå norsk teoriprøve<br/>på <span>ditt språk</span></h1>
  <p>Over 500 spørsmål på thai, norsk og engelsk med forklaringer – laget for thai-folk som bor i Norge.</p>

  <div class="flags" aria-label="Språk">
    <div class="flag flag-th"><div></div><div></div><div></div><div></div><div></div></div>
    <div class="flag flag-no"><div class="blue"></div><div class="bluev"></div></div>
    <div class="flag flag-gb"><div class="r1"></div><div class="r2"></div></div>
  </div>

  <div class="hero-badges">
    <span class="badge"><span class="dot"></span> 500+ spørsmål</span>
    <span class="badge">🇹🇭 Thai · 🇳🇴 Norsk · 🇬🇧 Engelsk</span>
    <span class="badge">🎯 Ekte eksamensformat</span>
  </div>

  <div class="hero-btns">
    <a href="/quiz-app/" class="hero-cta">▶ Test appen nå</a>
    <a href="/api/guide" class="hero-cta-secondary">📖 Guide: Fra Thailand til norsk førerkort</a>
    <span class="hero-cta-secondary" style="cursor:default;opacity:.7">📱 Google Play — kommer snart</span>
  </div>
</section>

<!-- FEATURES -->
<section id="features" class="container">
  <div class="section-head">
    <span class="eyebrow">Hvorfor Thai2Drive</span>
    <h2>Alt du trenger for å bestå</h2>
    <p>Bygd sammen med thai-folk som har gjennomført den norske teoriprøven.</p>
  </div>
  <div class="features">
    <div class="feature">
      <div class="feature-icon">🌐</div>
      <h3>Tre språk samtidig</h3>
      <p>Les spørsmål og forklaringer på thai, norsk eller engelsk – bytt når som helst.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">📚</div>
      <h3>500+ ekte spørsmål</h3>
      <p>Dekker alle kategoriene: vikeplikt, fartsgrenser, trafikkskilt, sikkerhet og mer.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🎯</div>
      <h3>Eksamensmodus</h3>
      <p>Øv med 45 spørsmål på 90 minutter – akkurat som den ekte teoriprøven.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">💡</div>
      <h3>Forklaringer på alle svar</h3>
      <p>Forstå hvorfor et svar er riktig – ikke bare pugg.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🔁</div>
      <h3>Gjennomgang av feil</h3>
      <p>Øv ekstra på spørsmålene du svarte feil på.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🔥</div>
      <h3>Daglig rutine</h3>
      <p>Hold streak-en gående med 10 gratis spørsmål hver dag.</p>
    </div>
  </div>
</section>

<!-- PRICING -->
<section id="pricing" class="container">
  <div class="section-head">
    <span class="eyebrow">Priser</span>
    <h2>Start gratis – oppgrader når du er klar</h2>
    <p>Alle planer gir ubegrenset tilgang til hele spørsmåldatabasen og eksamen.</p>
  </div>
  <div class="pricing">
    <div class="plan">
      <h3>Gratis</h3>
      <div class="price">0 kr<small> / for alltid</small></div>
      <ul>
        <li>10 spørsmål per dag</li>
        <li>Dagens test</li>
        <li>Alle tre språk</li>
        <li>Fullt norsk grensesnitt</li>
      </ul>
    </div>
    <div class="plan">
      <h3>Månedlig</h3>
      <div class="price">99 kr<small> / mnd</small></div>
      <ul>
        <li>Ubegrenset spørsmål</li>
        <li>Full eksamensmodus</li>
        <li>Gjennomgang av feil</li>
        <li>Ingen annonser</li>
      </ul>
    </div>
    <div class="plan popular">
      <span class="ribbon">Beste verdi</span>
      <h3>3 måneder</h3>
      <div class="price">299 kr<small> / 3 mnd</small></div>
      <ul>
        <li>Alt i Månedlig</li>
        <li>Rolig 3-måneders tilgang</li>
        <li>Perfekt frem til prøven</li>
        <li>Ingen annonser</li>
      </ul>
    </div>
    <div class="plan">
      <span class="ribbon" style="background:#6366F1;color:#fff">Livstid</span>
      <h3>Livstid</h3>
      <div class="price">699 kr<small> / engangsbetaling</small></div>
      <ul>
        <li>Betal én gang, bruk for alltid</li>
        <li>Alle fremtidige oppdateringer</li>
        <li>Perfekt hvis du skal kjøre flere prøver</li>
        <li>Ingen annonser</li>
      </ul>
    </div>
  </div>
</section>

<!-- CTA band -->
<section class="cta-band">
  <div class="container">
    <h2>Klar til å bestå?</h2>
    <p>Last ned {BRAND} og kom i gang på under ett minutt.</p>
    <div class="hero-btns" style="justify-content:flex-start">
      <a href="/quiz-app/" class="hero-cta">▶ Test i nettleseren</a>
      <span class="hero-cta-secondary" style="cursor:default;opacity:.7">📱 Google Play — kommer snart</span>
    </div>
  </div>
</section>
"""
    return HTMLResponse(_page(
        f"{BRAND} – Norsk teoriprøve på thai, norsk og engelsk",
        body,
        description="Bestå den norske teoriprøven lettere – 500+ spørsmål med forklaringer på thai, norsk og engelsk. Laget for thai-folk i Norge.",
    ))


# ─────────────────────────── GUIDE PAGE ───────────────────────────
@website_router.get("/guide", response_class=HTMLResponse)
def guide_page():
    try:
        from guide import build_guide_page
        return HTMLResponse(build_guide_page())
    except Exception as e:
        import traceback
        return HTMLResponse(f"<html><body style='background:#0B1226;color:#fff;padding:40px;font-family:sans-serif'><h2>Feil: {e}</h2><pre>{traceback.format_exc()}</pre></body></html>")


# ─────────────────────────── PRIVACY POLICY ───────────────────────────
@website_router.get("/privacy", response_class=HTMLResponse)
def privacy():
    body = f"""
<div class="legal">
  <h1>Personvernregler</h1>
  <p class="meta">Sist oppdatert: {LAST_UPDATED}</p>

  <div class="box">
    <strong>Kort oppsummert:</strong> Vi samler inn minst mulig data. Du kan bruke appen helt uten konto. Vi selger aldri data til tredjeparter.
  </div>

  <h2>1. Hvem vi er</h2>
  <p>{BRAND} («vi», «oss», «appen») er en mobilapplikasjon som hjelper brukere med å øve til den norske teoriprøven. Kontakt oss på <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> for personvernrelaterte spørsmål.</p>

  <h2>2. Hvilken informasjon vi samler inn</h2>

  <h3>a) Automatisk innsamlet (uten konto)</h3>
  <ul>
    <li><strong>Enhets-ID:</strong> En tilfeldig generert identifikator (ikke din telefon-ID) som brukes til å lagre fremgangen din lokalt og synkronisere med serveren.</li>
    <li><strong>Bruksdata:</strong> Hvilke spørsmål du har svart på, riktige/gale svar, studiestreak.</li>
    <li><strong>Språkvalg:</strong> Thai, norsk eller engelsk – lagret lokalt på enheten.</li>
  </ul>

  <h3>b) Hvis du oppretter konto</h3>
  <ul>
    <li><strong>E-postadresse</strong> (for innlogging og gjenoppretting av passord).</li>
    <li><strong>Kryptert passord</strong> (bcrypt – vi ser aldri klarteksten).</li>
  </ul>

  <h3>c) Hvis du kjøper Premium</h3>
  <ul>
    <li>Kjøpet behandles av <strong>RevenueCat + Google Play / Apple App Store</strong>. Vi mottar kun <em>om</em> du er Premium-bruker – ikke kortnummer eller adresse.</li>
  </ul>

  <h2>3. Hva vi IKKE samler inn</h2>
  <ul>
    <li>Ingen GPS/lokasjon</li>
    <li>Ingen kontakter eller telefonbok</li>
    <li>Ingen bilder eller kamera</li>
    <li>Ingen SMS eller samtaler</li>
    <li>Ingen reklame-sporing</li>
  </ul>

  <h2>4. Hvordan vi bruker dataen</h2>
  <ul>
    <li>For å la deg fortsette der du slapp</li>
    <li>For å synkronisere bokmerker og fremgang mellom enheter</li>
    <li>For å gi Premium-tilgang til betalende brukere</li>
    <li>For å forbedre spørsmålene og oversettelsene</li>
  </ul>

  <h2>5. Deling med tredjeparter</h2>
  <p>Vi deler data <strong>kun</strong> med følgende tjenester, og kun det som er strengt nødvendig:</p>
  <ul>
    <li><strong>MongoDB Atlas</strong> – skylagring av fremgang (EU-region).</li>
    <li><strong>RevenueCat</strong> – håndtering av abonnement/Premium-status.</li>
    <li><strong>Google Play Billing / Apple App Store</strong> – betalingshåndtering (vi ser aldri kortet ditt).</li>
  </ul>
  <p>Vi selger aldri data. Vi deler aldri data til annonsenettverk.</p>

  <h2>6. Dine rettigheter (GDPR)</h2>
  <p>Du har rett til å:</p>
  <ul>
    <li><strong>Få innsyn</strong> i hvilke data vi har om deg</li>
    <li><strong>Slette kontoen din</strong> og all tilhørende data</li>
    <li><strong>Eksportere</strong> dataen din</li>
    <li><strong>Trekke tilbake</strong> samtykket ditt</li>
  </ul>
  <p>Send en e-post til <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> med ønsket ditt – vi svarer innen 30 dager.</p>

  <h2>7. Barn</h2>
  <p>Appen er beregnet på brukere som er minst 16 år gamle og kan søke om førerkort i Norge. Vi samler ikke bevisst inn data fra barn.</p>

  <h2>8. Endringer i retningslinjene</h2>
  <p>Vi kan oppdatere disse retningslinjene. Vesentlige endringer varsles i appen.</p>

  <h2>9. Kontakt</h2>
  <p>Spørsmål? Skriv til <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
</div>
"""
    return HTMLResponse(_page(
        f"Personvern – {BRAND}", body,
        description="Personvernregler for Thai2Drive. Vi samler inn minst mulig data og selger aldri til tredjeparter.",
        path="/privacy",
    ))


# ─────────────────────────── TERMS OF SERVICE ───────────────────────────
@website_router.get("/terms", response_class=HTMLResponse)
def terms():
    body = f"""
<div class="legal">
  <h1>Brukervilkår</h1>
  <p class="meta">Sist oppdatert: {LAST_UPDATED}</p>

  <div class="box">
    <strong>Viktig:</strong> {BRAND} er et læringsverktøy og erstatter ikke offisiell undervisning fra Statens vegvesen eller godkjente trafikkskoler.
  </div>

  <h2>1. Aksept av vilkår</h2>
  <p>Ved å laste ned, installere eller bruke {BRAND} godtar du disse vilkårene. Hvis du ikke godtar, må du ikke bruke appen.</p>

  <h2>2. Tjenestebeskrivelse</h2>
  <p>{BRAND} tilbyr øvingsspørsmål til den norske teoriprøven på tre språk. Vi gir ingen garanti for at du vil bestå den offisielle prøven.</p>

  <h2>3. Brukerkonto</h2>
  <ul>
    <li>Du er ansvarlig for å holde passordet ditt sikkert.</li>
    <li>Du må ha minst 16 år for å opprette konto.</li>
    <li>Vi kan stenge kontoer som bryter vilkårene.</li>
  </ul>

  <h2>4. Premium-abonnement</h2>
  <ul>
    <li><strong>Fornyelse:</strong> Månedlig og 3-måneders abonnement fornyes automatisk via Google Play / App Store.</li>
    <li><strong>Oppsigelse:</strong> Du kan når som helst si opp i Google Play / App Store-innstillingene.</li>
    <li><strong>Refusjon:</strong> Refusjonsregler følger Google Plays og App Stores retningslinjer.</li>
    <li><strong>Livstid-kjøp:</strong> Gir tilgang så lenge appen eksisterer og støttes (minimum 3 år fra kjøp).</li>
    <li>Priser er i NOK og inkluderer norsk merverdiavgift.</li>
  </ul>

  <h2>5. Tillatt bruk</h2>
  <p>Du <strong>må ikke</strong>:</p>
  <ul>
    <li>Kopiere, videreselge eller publisere spørsmålene våre</li>
    <li>Forsøke å reversere appen</li>
    <li>Bruke appen til juks på offisielle prøver</li>
    <li>Omgå betalingsmurer eller geografiske begrensninger</li>
  </ul>

  <h2>6. Immaterielle rettigheter</h2>
  <p>Alt innhold (spørsmål, oversettelser, bilder, logo, kode) tilhører {BRAND} eller våre lisensgivere.</p>

  <h2>7. Ansvarsbegrensning</h2>
  <p>Appen leveres «som den er». Vi er ikke ansvarlig for:</p>
  <ul>
    <li>Om du består eller stryker på den offisielle prøven</li>
    <li>Feil eller unøyaktigheter i spørsmål (men meld fra så fikser vi dem!)</li>
    <li>Nedetid, datatap eller andre tekniske feil</li>
  </ul>

  <h2>8. Endringer</h2>
  <p>Vi kan endre disse vilkårene. Du varsles i appen ved vesentlige endringer.</p>

  <h2>9. Gjeldende lov</h2>
  <p>Norsk rett gjelder. Tvister behandles av norske domstoler.</p>

  <h2>10. Kontakt</h2>
  <p>Spørsmål om vilkår: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</div>
"""
    return HTMLResponse(_page(
        f"Brukervilkår – {BRAND}", body,
        description="Brukervilkår for Thai2Drive.",
        path="/terms",
    ))


# ─────────────────────────── SUPPORT / CONTACT ───────────────────────────
@website_router.get("/support", response_class=HTMLResponse)
def support():
    body = f"""
<div class="legal">
  <h1>Support &amp; kontakt</h1>
  <p class="meta">Vi svarer vanligvis innen 1–2 virkedager.</p>

  <div class="box">
    <strong>📧 E-post:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br/>
    Beskriv problemet ditt så godt du kan, og inkluder gjerne skjermbilde.
  </div>

  <h2>Vanlige spørsmål</h2>

  <h3>❓ Jeg kommer ikke inn på kontoen min</h3>
  <p>Send oss e-post med adressen du registrerte deg med, så hjelper vi deg med å tilbakestille passordet manuelt.</p>

  <h3>❓ Jeg kjøpte Premium, men det er ikke aktivert</h3>
  <p>Åpne appen, gå til Innstillinger → «Gjenopprett kjøp». Hvis det fortsatt ikke virker, send oss kvitteringen fra Google Play / App Store.</p>

  <h3>❓ Hvordan sier jeg opp abonnementet?</h3>
  <ul>
    <li><strong>Android:</strong> Google Play Store → Profil → Betalinger og abonnementer → Abonnementer → Thai2Drive → Si opp.</li>
    <li><strong>iPhone:</strong> Innstillinger → Apple ID → Abonnementer → Thai2Drive → Avbryt abonnement.</li>
  </ul>

  <h3>❓ Jeg fant en feil i et spørsmål</h3>
  <p>Send oss en e-post med spørsmålsteksten (eller skjermbilde), så korrigerer vi det raskt.</p>

  <h3>❓ Kan jeg bruke appen uten konto?</h3>
  <p>Ja! Du trenger ikke konto for å øve. Men da lagres fremgangen bare på den ene enheten.</p>

  <h3>❓ Hvilke språk støttes?</h3>
  <p>Thai 🇹🇭 · Norsk 🇳🇴 · Engelsk 🇬🇧 – du kan bytte når som helst i appen.</p>

  <h3>❓ Sletting av data / konto</h3>
  <p>Send e-post med emnefeltet «Slett konto» til <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. Vi sletter kontoen og alle data innen 30 dager.</p>

  <h2>Forretningsinfo</h2>
  <p>
    {BRAND}<br/>
    E-post: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br/>
    Nettsted: <a href="/api/website">{public_site_url().replace('https://', '').replace('http://', '')}</a>
  </p>
</div>
"""
    return HTMLResponse(_page(
        f"Support – {BRAND}", body,
        description="Trenger du hjelp? Kontakt Thai2Drive-supporten.",
        path="/support",
    ))


# ─────────────────────────── LÆRINGSBOK (members only) ───────────────────────────
@website_router.get("/bok", response_class=HTMLResponse)
def laeringsbok():
    body = """
<div id="bok-app">
  <!-- LOGIN SCREEN -->
  <div id="bok-login" style="display:none;min-height:80vh;align-items:center;justify-content:center;padding:24px">
    <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:40px;width:100%;max-width:420px;text-align:center">
      <div style="font-size:48px;margin-bottom:16px">📖</div>
      <h1 style="color:#fff;font-size:26px;font-weight:800;margin-bottom:8px">Læringsbok</h1>
      <p style="color:#94A3B8;margin-bottom:28px;font-size:15px">Logg inn med Thai2Drive-kontoen din for å lese pensum</p>
      <div id="bok-login-err" style="display:none;background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);color:#FCA5A5;padding:10px 14px;border-radius:10px;margin-bottom:16px;font-size:14px"></div>
      <input id="bok-email" type="email" placeholder="E-postadresse" autocomplete="email"
        style="width:100%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#fff;padding:12px 16px;border-radius:10px;font-size:15px;margin-bottom:12px;outline:none;font-family:inherit"/>
      <input id="bok-pass" type="password" placeholder="Passord" autocomplete="current-password"
        style="width:100%;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#fff;padding:12px 16px;border-radius:10px;font-size:15px;margin-bottom:20px;outline:none;font-family:inherit"/>
      <button id="bok-login-btn"
        style="width:100%;background:#FF9933;color:#0F172A;border:none;padding:14px;border-radius:10px;font-weight:800;font-size:16px;cursor:pointer">
        Logg inn
      </button>
      <p style="color:#64748B;font-size:13px;margin-top:20px">Trenger du tilgang? Last ned Thai2Drive-appen og opprett konto.</p>
    </div>
  </div>

  <!-- NOT PREMIUM -->
  <div id="bok-nopremium" style="display:none;min-height:80vh;align-items:center;justify-content:center;padding:24px">
    <div style="text-align:center;max-width:440px">
      <div style="font-size:48px;margin-bottom:16px">🔒</div>
      <h2 style="color:#fff;font-size:24px;font-weight:800;margin-bottom:12px">Kun for Premium-brukere</h2>
      <p style="color:#94A3B8;margin-bottom:24px">Læringsbok er inkludert i alle Premium-planer. Oppgrader i appen for å få tilgang.</p>
      <a href="/api/website#pricing" style="background:#FF9933;color:#0F172A;padding:14px 28px;border-radius:10px;font-weight:800;font-size:15px">Se priser</a>
      <br/><br/>
      <button id="bok-logout-np" style="background:none;border:none;color:#64748B;font-size:13px;cursor:pointer;text-decoration:underline">Logg ut</button>
    </div>
  </div>

  <!-- LOADING -->
  <div id="bok-loading" style="display:none;min-height:80vh;align-items:center;justify-content:center">
    <div style="text-align:center;color:#94A3B8">
      <div style="font-size:36px;margin-bottom:12px">⏳</div>
      <p>Laster læringsbok...</p>
    </div>
  </div>

  <!-- CHAPTER LIST -->
  <div id="bok-chapters" style="display:none;padding:48px 0 80px">
    <div class="container">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:32px;flex-wrap:wrap;gap:12px">
        <div>
          <span style="color:#FF9933;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.1em">Læringsbok</span>
          <h1 style="color:#fff;font-size:clamp(24px,4vw,36px);font-weight:800;margin-top:4px">Norsk trafikklære</h1>
          <p style="color:#94A3B8;font-size:14px;margin-top:6px">Offisielt pensum på norsk, thai og engelsk</p>
        </div>
        <div style="display:flex;gap:10px;align-items:center">
          <div id="bok-lang-btns" style="display:flex;gap:6px">
            <button class="bok-lang" data-lang="no" style="background:rgba(255,153,51,.15);border:1px solid #FF9933;color:#FF9933;padding:6px 12px;border-radius:8px;font-size:13px;cursor:pointer;font-weight:700">🇳🇴 NO</button>
            <button class="bok-lang" data-lang="th" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#94A3B8;padding:6px 12px;border-radius:8px;font-size:13px;cursor:pointer">🇹🇭 TH</button>
            <button class="bok-lang" data-lang="en" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#94A3B8;padding:6px 12px;border-radius:8px;font-size:13px;cursor:pointer">🇬🇧 EN</button>
          </div>
          <button id="bok-logout-ch" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#94A3B8;padding:6px 14px;border-radius:8px;font-size:13px;cursor:pointer">Logg ut</button>
        </div>
      </div>
      <div id="bok-chapter-list" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px"></div>
    </div>
  </div>

  <!-- READING VIEW -->
  <div id="bok-reader" style="display:none;padding:32px 0 80px">
    <div class="container" style="max-width:820px">
      <!-- Top bar -->
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:28px;flex-wrap:wrap">
        <button id="bok-back" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#CBD5E1;padding:8px 16px;border-radius:8px;font-size:14px;cursor:pointer">← Tilbake</button>
        <div id="bok-chapter-label" style="color:#FF9933;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.06em"></div>
        <div style="margin-left:auto;display:flex;gap:6px">
          <button class="bok-lang2" data-lang="no" style="background:rgba(255,153,51,.15);border:1px solid #FF9933;color:#FF9933;padding:5px 10px;border-radius:7px;font-size:12px;cursor:pointer;font-weight:700">🇳🇴</button>
          <button class="bok-lang2" data-lang="th" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#94A3B8;padding:5px 10px;border-radius:7px;font-size:12px;cursor:pointer">🇹🇭</button>
          <button class="bok-lang2" data-lang="en" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);color:#94A3B8;padding:5px 10px;border-radius:7px;font-size:12px;cursor:pointer">🇬🇧</button>
        </div>
      </div>

      <!-- Progress -->
      <div style="background:rgba(255,255,255,.06);border-radius:999px;height:4px;margin-bottom:24px">
        <div id="bok-progress-bar" style="background:#FF9933;height:4px;border-radius:999px;transition:width .3s;width:0%"></div>
      </div>

      <!-- Section counter -->
      <div id="bok-section-counter" style="color:#64748B;font-size:13px;margin-bottom:16px"></div>

      <!-- Content card -->
      <div id="bok-content-card" style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:18px;padding:32px;min-height:300px">
        <h2 id="bok-section-title" style="color:#fff;font-size:22px;font-weight:800;margin-bottom:16px;line-height:1.3"></h2>
        <div id="bok-image-wrap" style="display:none;margin-bottom:20px;border-radius:12px;overflow:hidden;background:#fff;text-align:center">
          <img id="bok-section-img" src="" alt="" style="max-width:100%;max-height:420px;object-fit:contain;display:block;margin:0 auto"/>
        </div>
        <p id="bok-section-content" style="color:#CBD5E1;font-size:16px;line-height:1.8;white-space:pre-wrap"></p>
      </div>

      <!-- TTS + Navigation -->
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:20px;flex-wrap:wrap;gap:12px">
        <button id="bok-prev" style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#CBD5E1;padding:10px 22px;border-radius:10px;font-size:14px;cursor:pointer;font-weight:600">← Forrige</button>
        <button id="bok-tts" title="Les opp"
          style="background:rgba(255,153,51,.12);border:1px solid rgba(255,153,51,.3);color:#FF9933;padding:10px 20px;border-radius:10px;font-size:14px;cursor:pointer;display:flex;align-items:center;gap:8px">
          <span id="bok-tts-icon">🔊</span> <span id="bok-tts-label">Les opp</span>
        </button>
        <button id="bok-next" style="background:#FF9933;border:none;color:#0F172A;padding:10px 22px;border-radius:10px;font-size:14px;cursor:pointer;font-weight:700">Neste →</button>
      </div>
    </div>
  </div>
</div>

<script>
(function(){
  const API = '/api';
  let token = localStorage.getItem('authToken');
  let curLang = localStorage.getItem('bok_lang') || 'no';
  let sections = [];
  let curIdx = 0;
  let speaking = false;

  const $ = id => document.getElementById(id);

  function show(id){
    ['bok-login','bok-nopremium','bok-loading','bok-chapters','bok-reader'].forEach(s=>{
      const el = $(s);
      if(!el) return;
      if(s !== id){ el.style.display='none'; return; }
      el.style.display = (s==='bok-login'||s==='bok-nopremium'||s==='bok-loading') ? 'flex' : 'block';
    });
  }

  // ── Lang buttons ──────────────────────────────────────────────────
  function setLang(lang){
    curLang = lang;
    localStorage.setItem('bok_lang', lang);
    const map = {no:'🇳🇴 NO', th:'🇹🇭 TH', en:'🇬🇧 EN'};
    document.querySelectorAll('.bok-lang,.bok-lang2').forEach(btn => {
      const active = btn.dataset.lang === lang;
      btn.style.background = active ? 'rgba(255,153,51,.15)' : 'rgba(255,255,255,.06)';
      btn.style.borderColor = active ? '#FF9933' : 'rgba(255,255,255,.12)';
      btn.style.color = active ? '#FF9933' : '#94A3B8';
      btn.style.fontWeight = active ? '700' : '400';
    });
    if(sections.length) renderSection();
  }
  document.addEventListener('click', e => {
    if(e.target.classList.contains('bok-lang') || e.target.classList.contains('bok-lang2')){
      setLang(e.target.dataset.lang);
    }
  });

  // ── Auth ──────────────────────────────────────────────────────────
  async function checkAuth(){
    if(!token){ show('bok-login'); return; }
    show('bok-loading');
    try{
      const res = await fetch(API+'/auth/me', {headers:{'Authorization':'Bearer '+token}});
      if(!res.ok){ token=null; localStorage.removeItem('authToken'); show('bok-login'); return; }
      const me = await res.json();
      if(!me.is_premium && !me.is_admin){ show('bok-nopremium'); return; }
      loadChapters();
    }catch(e){ show('bok-login'); }
  }

  // ── Login ─────────────────────────────────────────────────────────
  $('bok-login-btn').addEventListener('click', async () => {
    const email = $('bok-email').value.trim();
    const pass  = $('bok-pass').value;
    const errEl = $('bok-login-err');
    errEl.style.display = 'none';
    if(!email||!pass){ errEl.textContent='Fyll inn e-post og passord'; errEl.style.display='block'; return; }
    $('bok-login-btn').textContent = 'Logger inn...';
    $('bok-login-btn').disabled = true;
    try{
      const res = await fetch(API+'/auth/login',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({email, password: pass})
      });
      const data = await res.json();
      if(!res.ok){ errEl.textContent = data.detail || 'Feil e-post eller passord'; errEl.style.display='block'; return; }
      token = data.token;
      localStorage.setItem('authToken', token);
      checkAuth();
    }catch(e){ errEl.textContent='Nettverksfeil. Prøv igjen.'; errEl.style.display='block'; }
    finally{ $('bok-login-btn').textContent='Logg inn'; $('bok-login-btn').disabled=false; }
  });
  $('bok-pass').addEventListener('keydown', e => { if(e.key==='Enter') $('bok-login-btn').click(); });

  // ── Logout ────────────────────────────────────────────────────────
  function logout(){ token=null; localStorage.removeItem('authToken'); sections=[]; show('bok-login'); }
  $('bok-logout-np').addEventListener('click', logout);
  $('bok-logout-ch').addEventListener('click', logout);

  // ── Chapter list ──────────────────────────────────────────────────
  async function loadChapters(){
    show('bok-loading');
    try{
      const res = await fetch(API+'/chapters', {headers:{'Authorization':'Bearer '+token}});
      const chapters = await res.json();
      const list = $('bok-chapter-list');
      list.innerHTML = '';
      const icons = ['📗','👤','🚦','🚗'];
      const colors = ['#10B981','#3B82F6','#FF9933','#6366F1'];
      chapters.forEach((ch, i) => {
        const card = document.createElement('div');
        card.style.cssText = 'background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:24px;cursor:pointer;transition:all .2s';
        card.innerHTML = `
          <div style="font-size:32px;margin-bottom:12px">${icons[i]||'📘'}</div>
          <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:${colors[i]||'#FF9933'};margin-bottom:6px">Kapittel ${ch.chapter_num}</div>
          <h3 style="color:#fff;font-size:16px;font-weight:700;margin-bottom:6px">${ch.title[curLang]||ch.title.no}</h3>
          <p style="color:#64748B;font-size:13px">${ch.section_count} seksjoner</p>
        `;
        card.addEventListener('mouseenter', () => { card.style.borderColor='rgba(255,153,51,.4)'; card.style.background='rgba(255,153,51,.04)'; card.style.transform='translateY(-2px)'; });
        card.addEventListener('mouseleave', () => { card.style.borderColor='rgba(255,255,255,.07)'; card.style.background='rgba(255,255,255,.03)'; card.style.transform=''; });
        card.addEventListener('click', () => loadReader(ch.chapter_num, ch.title));
        list.appendChild(card);
      });
      show('bok-chapters');
      setLang(curLang);
    }catch(e){ alert('Kunne ikke laste kapitler. Prøv igjen.'); show('bok-chapters'); }
  }

  // ── Reader ────────────────────────────────────────────────────────
  async function loadReader(chapterNum, chapterTitle){
    show('bok-loading');
    stopTTS();
    try{
      const res = await fetch(API+'/chapters/'+chapterNum, {headers:{'Authorization':'Bearer '+token}});
      sections = await res.json();
      curIdx = 0;
      $('bok-chapter-label').textContent = 'Kapittel '+chapterNum+' · '+(chapterTitle[curLang]||chapterTitle.no);
      show('bok-reader');
      setLang(curLang);
      renderSection();
    }catch(e){ alert('Kunne ikke laste seksjoner.'); show('bok-chapters'); }
  }

  function renderSection(){
    if(!sections.length) return;
    const sec = sections[curIdx];
    const title = (sec.section_title && sec.section_title[curLang]) || sec.section_title?.no || '';
    const content = (sec.content && sec.content[curLang]) || sec.content?.no || '';
    $('bok-section-title').textContent = title;
    $('bok-section-content').textContent = content;
    const imgWrap = $('bok-image-wrap');
    const imgEl = $('bok-section-img');
    if(sec.image){ imgEl.src = sec.image; imgWrap.style.display='block'; }
    else { imgWrap.style.display='none'; imgEl.src=''; }
    $('bok-section-counter').textContent = 'Del '+(curIdx+1)+' av '+sections.length;
    const pct = sections.length > 1 ? Math.round((curIdx/(sections.length-1))*100) : 100;
    $('bok-progress-bar').style.width = pct+'%';
    $('bok-prev').disabled = curIdx === 0;
    $('bok-prev').style.opacity = curIdx === 0 ? '.4' : '1';
    $('bok-next').textContent = curIdx === sections.length-1 ? '✓ Ferdig' : 'Neste →';
    // scroll top of reader
    $('bok-reader').scrollIntoView({behavior:'smooth', block:'start'});
    stopTTS();
  }

  $('bok-back').addEventListener('click', () => { stopTTS(); show('bok-chapters'); });
  $('bok-prev').addEventListener('click', () => { if(curIdx>0){curIdx--;renderSection();} });
  $('bok-next').addEventListener('click', () => {
    if(curIdx < sections.length-1){ curIdx++; renderSection(); }
    else{ stopTTS(); show('bok-chapters'); }
  });

  // ── TTS ───────────────────────────────────────────────────────────
  const langVoice = {no:'nb-NO', th:'th-TH', en:'en-US'};
  function stopTTS(){
    speechSynthesis.cancel();
    speaking = false;
    $('bok-tts-icon').textContent = '🔊';
    $('bok-tts-label').textContent = {no:'Les opp',th:'อ่านออกเสียง',en:'Read aloud'}[curLang]||'Les opp';
  }
  $('bok-tts').addEventListener('click', () => {
    if(speaking){ stopTTS(); return; }
    const sec = sections[curIdx];
    const title = (sec.section_title && sec.section_title[curLang]) || '';
    const content = (sec.content && sec.content[curLang]) || '';
    const text = title + '. ' + content;
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = langVoice[curLang] || 'nb-NO';
    utt.rate = 0.88;
    utt.onend = () => stopTTS();
    utt.onerror = () => stopTTS();
    speechSynthesis.speak(utt);
    speaking = true;
    $('bok-tts-icon').textContent = '⏸';
    $('bok-tts-label').textContent = {no:'Stopp',th:'หยุด',en:'Stop'}[curLang]||'Stopp';
  });

  // ── Start ─────────────────────────────────────────────────────────
  checkAuth();
})();
</script>
"""
    return HTMLResponse(_page(
        "Læringsbok – Thai2Drive",
        body,
        description="Les norsk trafikklære på thai, norsk og engelsk. Kun for Thai2Drive Premium-brukere.",
        path="/bok",
    ))


# ─────────────────────────── SEO: sitemap + robots ───────────────────────────
@website_router.get("/sitemap.xml")
def sitemap_xml():
    """XML sitemap using the current public site URL (env-configurable)."""
    # Build the routable paths the same way the HTML pages do
    pages = [
        ("/",            "1.0", "weekly"),
        ("/privacy",     "0.5", "yearly"),
        ("/terms",       "0.5", "yearly"),
        ("/support",     "0.6", "monthly"),
    ]
    urls = ""
    for path, prio, freq in pages:
        # When served under /api/ prefix on the preview we expose canonical
        # without the prefix so search engines see clean URLs once a custom
        # domain is configured. canonical_url() handles this via SITE_ROUTING_MODE.
        loc = canonical_url(path)
        urls += (
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{prio}</priority>\n"
            "  </url>\n"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}"
        "</urlset>\n"
    )
    return Response(content=xml, media_type="application/xml")


@website_router.get("/robots.txt")
def robots_txt():
    """robots.txt pointing at the configured sitemap URL."""
    sitemap = canonical_url("/sitemap.xml")
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/admin\n"
        "Disallow: /api/admin-panel\n"
        f"Sitemap: {sitemap}\n"
    )
    return PlainTextResponse(body)


# ─────────────────────── Domain diagnostic endpoint ───────────────────────
# Use this to verify a custom domain is correctly pointed at the backend.
#   curl https://thai2drive.no/api/_whoami
#   curl https://www.thai2drive.no/api/_whoami
# Each should echo back the Host header it received.
@website_router.get("/_whoami")
def whoami(request: Request):
    return {
        "ok": True,
        "host": request.headers.get("host"),
        "x-forwarded-host": request.headers.get("x-forwarded-host"),
        "x-forwarded-proto": request.headers.get("x-forwarded-proto"),
        "scheme": request.url.scheme,
        "base_url": str(request.base_url),
        "public_site_url_env": public_site_url(),
    }
