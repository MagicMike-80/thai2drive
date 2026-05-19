from fastapi import APIRouter
from fastapi.responses import HTMLResponse

webapp_router = APIRouter()

WEBAPP_HTML = """<!DOCTYPE html>
<html lang="th" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thai2Drive – Web App</title>
<style>
  :root {
    --bg: #0B1226;
    --card: rgba(255,255,255,.04);
    --border: rgba(255,255,255,.08);
    --orange: #FF9933;
    --orange-dark: #e6891f;
    --text: #E2E8F0;
    --muted: #94A3B8;
    --green: #10B981;
    --red: #EF4444;
    --radius: 14px;
    --nav-h: 60px;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
  }

  /* ── NAV ── */
  nav {
    position: sticky; top: 0; z-index: 100;
    height: var(--nav-h);
    background: rgba(11,18,38,.92);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center;
    padding: 0 24px; gap: 16px;
  }
  .nav-brand {
    display: flex; align-items: center; gap: 10px;
    text-decoration: none; color: var(--text);
    font-weight: 800; font-size: 1.1rem; flex-shrink: 0;
  }
  .nav-brand img { width: 32px; height: 32px; border-radius: 8px; }
  .nav-brand span { color: var(--orange); }
  .nav-spacer { flex: 1; }
  .nav-user {
    display: flex; align-items: center; gap: 10px;
    font-size: .85rem; color: var(--muted);
  }
  .nav-logout {
    padding: 6px 14px; border-radius: 8px;
    border: 1px solid var(--border); background: transparent;
    color: var(--muted); font-size: .8rem; cursor: pointer;
    transition: all .2s;
  }
  .nav-logout:hover { border-color: var(--red); color: var(--red); }

  /* ── SCREENS ── */
  .screen { display: none; }
  .screen.active { display: block; }

  /* ── AUTH SCREEN ── */
  .auth-wrap {
    min-height: calc(100vh - var(--nav-h));
    display: flex; align-items: center; justify-content: center;
    padding: 32px 20px;
  }
  .auth-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px 32px;
    width: 100%; max-width: 420px;
  }
  .auth-logo {
    text-align: center; margin-bottom: 24px;
  }
  .auth-logo img { width: 56px; height: 56px; border-radius: 14px; margin-bottom: 10px; }
  .auth-logo h1 { font-size: 1.4rem; font-weight: 800; }
  .auth-logo h1 span { color: var(--orange); }
  .auth-logo p { color: var(--muted); font-size: .85rem; margin-top: 4px; }

  .auth-tabs {
    display: flex; gap: 4px;
    background: rgba(255,255,255,.04);
    border-radius: 10px; padding: 4px;
    margin-bottom: 24px;
  }
  .auth-tab {
    flex: 1; padding: 8px; border-radius: 8px;
    border: none; background: transparent;
    color: var(--muted); font-size: .875rem; font-weight: 600;
    cursor: pointer; transition: all .2s;
  }
  .auth-tab.active { background: var(--orange); color: #000; }

  .form-group { margin-bottom: 16px; }
  .form-group label { display: block; font-size: .8rem; font-weight: 600; color: var(--muted); margin-bottom: 6px; }
  .form-group input {
    width: 100%; padding: 11px 14px;
    background: rgba(255,255,255,.05);
    border: 1.5px solid var(--border);
    border-radius: 10px; color: var(--text);
    font-size: .9rem; outline: none;
    transition: border-color .2s;
  }
  .form-group input:focus { border-color: var(--orange); }
  .form-group input::placeholder { color: var(--muted); }

  .auth-btn {
    width: 100%; padding: 12px;
    background: var(--orange); color: #0F172A;
    font-weight: 800; font-size: .95rem;
    border: none; border-radius: 10px;
    cursor: pointer; transition: background .2s;
    margin-top: 4px;
  }
  .auth-btn:hover { background: var(--orange-dark); }
  .auth-btn:disabled { opacity: .5; cursor: not-allowed; }

  .auth-error {
    background: rgba(239,68,68,.1); border: 1px solid rgba(239,68,68,.3);
    border-radius: 8px; padding: 10px 14px;
    color: #FCA5A5; font-size: .85rem; margin-bottom: 16px;
    display: none;
  }
  .auth-error.show { display: block; }

  .forgot-link {
    text-align: right; margin-top: -8px; margin-bottom: 16px;
  }
  .forgot-link a {
    font-size: .78rem; color: var(--muted);
    text-decoration: none; cursor: pointer;
  }
  .forgot-link a:hover { color: var(--orange); }

  /* ── DASHBOARD ── */
  .dash-wrap { max-width: 1100px; margin: 0 auto; padding: 32px 24px; }

  .dash-welcome {
    margin-bottom: 32px;
  }
  .dash-welcome h2 { font-size: 1.6rem; font-weight: 800; }
  .dash-welcome p { color: var(--muted); margin-top: 4px; }

  .dash-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px; margin-bottom: 36px;
  }
  .stat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px;
    text-align: center;
  }
  .stat-card .num { font-size: 2rem; font-weight: 800; color: var(--orange); }
  .stat-card .lbl { font-size: .8rem; color: var(--muted); margin-top: 4px; }

  .section-title {
    font-size: 1.1rem; font-weight: 700;
    margin-bottom: 16px; color: var(--text);
  }

  /* ── CATEGORIES ── */
  .cat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 14px; margin-bottom: 40px;
  }
  .cat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 20px;
    cursor: pointer; transition: border-color .2s, transform .15s;
    display: flex; flex-direction: column; gap: 8px;
  }
  .cat-card:hover { border-color: var(--orange); transform: translateY(-2px); }
  .cat-card .cat-icon { font-size: 1.8rem; }
  .cat-card .cat-name { font-weight: 700; font-size: .95rem; }
  .cat-card .cat-count { font-size: .78rem; color: var(--muted); }
  .cat-card .cat-bar-wrap {
    height: 4px; background: rgba(255,255,255,.08);
    border-radius: 2px; overflow: hidden; margin-top: 4px;
  }
  .cat-card .cat-bar { height: 100%; background: var(--orange); border-radius: 2px; transition: width .3s; }

  /* ── QUIZ SCREEN ── */
  .quiz-wrap { max-width: 1100px; margin: 0 auto; padding: 24px; }

  .quiz-hdr {
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 20px; flex-wrap: wrap;
  }
  .back-btn {
    padding: 8px 16px; border-radius: 10px;
    border: 1px solid var(--border); background: transparent;
    color: var(--muted); cursor: pointer; font-size: .85rem;
    transition: all .2s;
  }
  .back-btn:hover { border-color: var(--orange); color: var(--text); }

  .quiz-prog-wrap { flex: 1; }
  .quiz-prog-lbl { font-size: .8rem; color: var(--muted); margin-bottom: 4px; }
  .quiz-prog-bar { height: 5px; background: rgba(255,255,255,.08); border-radius: 3px; overflow: hidden; }
  .quiz-prog-fill { height: 100%; background: var(--orange); border-radius: 3px; transition: width .3s; }

  .quiz-score { font-size: .85rem; color: var(--muted); white-space: nowrap; }
  .quiz-score span { color: var(--green); font-weight: 700; }

  .quiz-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 20px; padding: 24px;
    display: grid; grid-template-columns: 1fr 1fr auto;
    gap: 20px; align-items: start;
  }

  .q-left { display: flex; flex-direction: column; gap: 12px; }
  .q-img {
    width: 100%; max-height: 220px; object-fit: contain;
    border-radius: 10px; background: rgba(255,255,255,.03);
  }
  .q-text { font-size: 1.05rem; font-weight: 700; line-height: 1.5; }

  .q-right { display: flex; flex-direction: column; gap: 10px; }
  .q-answers { display: flex; flex-direction: column; gap: 8px; }

  .ans-btn {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 14px;
    background: rgba(255,255,255,.03); border: 1.5px solid var(--border);
    border-radius: 12px; cursor: pointer; text-align: left;
    color: var(--text); font-size: .9rem;
    transition: border-color .2s, background .2s;
    width: 100%;
  }
  .ans-btn:hover:not(:disabled) { border-color: var(--orange); background: rgba(255,153,51,.07); }
  .ans-btn:disabled { cursor: default; }
  .ans-btn.correct { border-color: var(--green); background: rgba(16,185,129,.12); }
  .ans-btn.wrong { border-color: var(--red); background: rgba(239,68,68,.12); }
  .ans-btn.reveal { border-color: var(--green); background: rgba(16,185,129,.06); }

  .ans-letter {
    width: 30px; height: 30px; border-radius: 50%;
    background: rgba(255,153,51,.12); color: var(--orange);
    font-size: .78rem; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: background .2s, color .2s;
  }
  .ans-btn.correct .ans-letter { background: var(--green); color: #fff; }
  .ans-btn.wrong .ans-letter { background: var(--red); color: #fff; }
  .ans-btn.reveal .ans-letter { background: var(--green); color: #fff; }

  .q-feedback {
    margin-top: 12px; padding: 12px 14px;
    border-radius: 10px; font-size: .85rem; line-height: 1.5;
    display: none;
  }
  .q-feedback.ok { background: rgba(16,185,129,.1); border: 1px solid rgba(16,185,129,.3); color: #6EE7B7; display: block; }
  .q-feedback.bad { background: rgba(239,68,68,.08); border: 1px solid rgba(239,68,68,.25); color: #FCA5A5; display: block; }

  .q-explain {
    margin-top: 8px; padding: 12px 14px;
    background: rgba(255,153,51,.07); border: 1px solid rgba(255,153,51,.2);
    border-radius: 10px; font-size: .85rem; color: var(--muted);
    line-height: 1.5; display: none;
  }
  .q-explain.show { display: block; }

  /* TTS row */
  .q-tts {
    display: flex; align-items: center; gap: 8px; margin-top: 8px; flex-wrap: wrap;
  }
  .tts-btn {
    width: 34px; height: 34px; border-radius: 50%;
    border: 1.5px solid var(--border); background: rgba(255,255,255,.04);
    color: var(--text); cursor: pointer; font-size: 13px;
    display: flex; align-items: center; justify-content: center;
    transition: all .2s;
  }
  .tts-btn:hover, .tts-btn.playing { border-color: var(--orange); color: var(--orange); background: rgba(255,153,51,.1); }
  .spd-btn {
    padding: 3px 9px; border-radius: 20px;
    border: 1px solid var(--border); background: transparent;
    color: var(--muted); font-size: .75rem; font-weight: 700; cursor: pointer;
    transition: all .2s;
  }
  .spd-btn:hover { border-color: var(--orange); }
  .spd-btn.active { background: rgba(255,153,51,.15); border-color: var(--orange); color: var(--orange); }

  /* Next col */
  .q-next-col { display: flex; align-items: center; justify-content: center; }
  .q-next-big {
    writing-mode: vertical-rl;
    padding: 20px 14px; background: var(--orange); color: #0F172A;
    font-weight: 800; font-size: 15px; border: none; border-radius: 14px;
    cursor: pointer; min-height: 130px; width: 48px;
    display: flex; align-items: center; justify-content: center;
    transition: background .2s, transform .1s;
  }
  .q-next-big:disabled { opacity: .35; cursor: not-allowed; }
  .q-next-big:not(:disabled):hover { background: var(--orange-dark); transform: scale(1.04); }

  /* ── END SCREEN ── */
  .end-wrap {
    text-align: center; padding: 60px 24px;
    max-width: 500px; margin: 0 auto;
  }
  .end-emoji { font-size: 4rem; margin-bottom: 16px; }
  .end-score { font-size: 3rem; font-weight: 800; color: var(--orange); }
  .end-lbl { color: var(--muted); margin: 8px 0 32px; }
  .end-btns { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
  .end-btn {
    padding: 12px 28px; border-radius: 12px;
    font-weight: 700; font-size: .95rem; cursor: pointer; border: none;
    transition: background .2s;
  }
  .end-btn.primary { background: var(--orange); color: #0F172A; }
  .end-btn.primary:hover { background: var(--orange-dark); }
  .end-btn.secondary { background: rgba(255,255,255,.07); color: var(--text); border: 1px solid var(--border); }
  .end-btn.secondary:hover { border-color: var(--orange); }

  /* ── LOADING ── */
  .loading {
    display: flex; align-items: center; justify-content: center;
    padding: 80px 20px; flex-direction: column; gap: 16px;
  }
  .spinner {
    width: 38px; height: 38px;
    border: 3px solid var(--border); border-top-color: var(--orange);
    border-radius: 50%; animation: spin .8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── TOAST ── */
  .toast {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    background: #1E293B; border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 20px;
    font-size: .875rem; color: var(--text);
    opacity: 0; pointer-events: none; transition: opacity .3s;
    z-index: 999; white-space: nowrap;
  }
  .toast.show { opacity: 1; }

  @media (max-width: 700px) {
    .quiz-card { grid-template-columns: 1fr; }
    .q-next-col { display: none; }
    .auth-card { padding: 28px 20px; }
  }
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <a href="/api/web" class="nav-brand">
    <img src="/api/assets/developer-icon-512.png" alt="T2D">
    Thai<span>2Drive</span>
  </a>
  <div class="nav-spacer"></div>
  <div class="nav-user" id="navUser" style="display:none">
    <span id="navEmail"></span>
    <button class="nav-logout" onclick="logout()">Logg ut</button>
  </div>
</nav>

<!-- AUTH SCREEN -->
<div class="screen active" id="screenAuth">
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-logo">
        <img src="/api/assets/developer-icon-512.png" alt="T2D">
        <h1>Thai<span>2Drive</span></h1>
        <p>Teoriprøven på thai 🇹🇭🇳🇴</p>
      </div>

      <div class="auth-tabs">
        <button class="auth-tab active" onclick="switchTab('login')">Logg inn</button>
        <button class="auth-tab" onclick="switchTab('register')">Registrer</button>
      </div>

      <div class="auth-error" id="authError"></div>

      <!-- LOGIN FORM -->
      <div id="formLogin">
        <div class="form-group">
          <label>E-post</label>
          <input type="email" id="loginEmail" placeholder="din@epost.com" autocomplete="email">
        </div>
        <div class="form-group">
          <label>Passord</label>
          <input type="password" id="loginPass" placeholder="••••••••" autocomplete="current-password">
        </div>
        <div class="forgot-link"><a onclick="showForgot()">Glemt passord?</a></div>
        <button class="auth-btn" onclick="doLogin()">Logg inn</button>
      </div>

      <!-- REGISTER FORM -->
      <div id="formRegister" style="display:none">
        <div class="form-group">
          <label>Navn</label>
          <input type="text" id="regName" placeholder="Ditt navn">
        </div>
        <div class="form-group">
          <label>E-post</label>
          <input type="email" id="regEmail" placeholder="din@epost.com" autocomplete="email">
        </div>
        <div class="form-group">
          <label>Passord</label>
          <input type="password" id="regPass" placeholder="Minst 6 tegn" autocomplete="new-password">
        </div>
        <button class="auth-btn" onclick="doRegister()">Opprett konto</button>
      </div>

      <!-- FORGOT PASSWORD -->
      <div id="formForgot" style="display:none">
        <div class="form-group">
          <label>E-post</label>
          <input type="email" id="forgotEmail" placeholder="din@epost.com">
        </div>
        <button class="auth-btn" onclick="doForgot()">Send tilbakestillingslenke</button>
        <div style="text-align:center;margin-top:12px">
          <a style="font-size:.8rem;color:var(--muted);cursor:pointer" onclick="switchTab('login')">← Tilbake til innlogging</a>
        </div>
      </div>

    </div>
  </div>
</div>

<!-- DASHBOARD SCREEN -->
<div class="screen" id="screenDash">
  <div class="dash-wrap">
    <div class="dash-welcome">
      <h2>Hei, <span id="dashName" style="color:var(--orange)"></span>! 👋</h2>
      <p>Velg en kategori og start øvingen</p>
    </div>

    <div class="dash-stats">
      <div class="stat-card">
        <div class="num" id="statTotal">–</div>
        <div class="lbl">Spørsmål totalt</div>
      </div>
      <div class="stat-card">
        <div class="num" id="statDone">–</div>
        <div class="lbl">Besvart</div>
      </div>
      <div class="stat-card">
        <div class="num" id="statScore">–</div>
        <div class="lbl">Riktige svar</div>
      </div>
      <div class="stat-card">
        <div class="num" id="statCats">–</div>
        <div class="lbl">Kategorier</div>
      </div>
    </div>

    <div class="section-title">📚 Kategorier</div>
    <div class="cat-grid" id="catGrid">
      <div class="loading"><div class="spinner"></div></div>
    </div>
  </div>
</div>

<!-- QUIZ SCREEN -->
<div class="screen" id="screenQuiz">
  <div class="quiz-wrap">
    <div class="quiz-hdr">
      <button class="back-btn" onclick="goBack()">← Tilbake</button>
      <div class="quiz-prog-wrap">
        <div class="quiz-prog-lbl" id="qProgLbl">Spørsmål 1 av 10</div>
        <div class="quiz-prog-bar"><div class="quiz-prog-fill" id="qProgFill" style="width:0%"></div></div>
      </div>
      <div class="quiz-score">✓ <span id="qScore">0</span></div>
    </div>
    <div id="qContainer"></div>
  </div>
</div>

<!-- END SCREEN -->
<div class="screen" id="screenEnd">
  <div class="end-wrap">
    <div class="end-emoji" id="endEmoji">🏆</div>
    <div class="end-score" id="endScore">0 / 10</div>
    <p class="end-lbl" id="endLbl">Bra jobbet!</p>
    <div class="end-btns">
      <button class="end-btn primary" onclick="retryQuiz()">Prøv igjen</button>
      <button class="end-btn secondary" onclick="showDash()">Velg kategori</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
// ── State ──
let token = localStorage.getItem('t2d_token');
let user = null;
let questions = [];
let qIdx = 0;
let qScore = 0;
let qAnswered = false;
let ttsRate = 1;
let ttsPlaying = false;
let currentCat = null;
let soundOn = true;

// ── Init ──
(async function init() {
  if (token) {
    try {
      const r = await api('GET', '/api/auth/me');
      user = r;
      showDash();
    } catch(e) {
      localStorage.removeItem('t2d_token');
      token = null;
      showScreen('screenAuth');
    }
  } else {
    showScreen('screenAuth');
  }
})();

// ── Screens ──
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

// ── API helper ──
async function api(method, url, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(url, opts);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || 'Noe gikk galt');
  return data;
}

// ── Toast ──
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2500);
}

// ── Auth ──
function switchTab(tab) {
  document.querySelectorAll('.auth-tab').forEach((t,i) => t.classList.toggle('active', (i===0 && tab==='login') || (i===1 && tab==='register')));
  document.getElementById('formLogin').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('formRegister').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('formForgot').style.display = 'none';
  clearError();
}

function showForgot() {
  document.getElementById('formLogin').style.display = 'none';
  document.getElementById('formForgot').style.display = 'block';
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
  clearError();
}

function showError(msg) {
  const el = document.getElementById('authError');
  el.textContent = msg;
  el.classList.add('show');
}

function clearError() {
  document.getElementById('authError').classList.remove('show');
}

async function doLogin() {
  clearError();
  const email = document.getElementById('loginEmail').value.trim();
  const pass = document.getElementById('loginPass').value;
  if (!email || !pass) return showError('Fyll inn e-post og passord');
  try {
    const r = await api('POST', '/api/auth/login', { email, password: pass });
    token = r.token;
    user = r.user;
    localStorage.setItem('t2d_token', token);
    showDash();
  } catch(e) { showError(e.message); }
}

async function doRegister() {
  clearError();
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const pass = document.getElementById('regPass').value;
  if (!name || !email || !pass) return showError('Fyll inn alle feltene');
  if (pass.length < 6) return showError('Passord må være minst 6 tegn');
  try {
    const r = await api('POST', '/api/auth/signup', { name, email, password: pass });
    token = r.token;
    user = r.user;
    localStorage.setItem('t2d_token', token);
    showDash();
  } catch(e) { showError(e.message); }
}

async function doForgot() {
  clearError();
  const email = document.getElementById('forgotEmail').value.trim();
  if (!email) return showError('Fyll inn e-postadressen din');
  try {
    await api('POST', '/api/auth/forgot-password', { email });
    toast('E-post sendt! Sjekk innboksen din 📧');
    switchTab('login');
  } catch(e) { showError(e.message); }
}

function logout() {
  localStorage.removeItem('t2d_token');
  token = null; user = null;
  document.getElementById('navUser').style.display = 'none';
  showScreen('screenAuth');
}

// ── Dashboard ──
async function showDash() {
  showScreen('screenDash');
  document.getElementById('navUser').style.display = 'flex';
  document.getElementById('navEmail').textContent = user?.name || user?.email || '';

  document.getElementById('dashName').textContent = user?.name || user?.email?.split('@')[0] || 'der';

  loadCategories();
}

async function loadCategories() {
  const grid = document.getElementById('catGrid');
  grid.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
  try {
    const cats = await api('GET', '/api/categories');
    const icons = {
      'Trafikkregler': '🚦', 'Skilt': '🪧', 'Vikeplikt': '⚠️',
      'Kjøretøy': '🚗', 'Farlig gods': '☣️', 'Miljø': '🌿',
      'Ulykker': '🚨', 'Alkohol': '🍺', 'Bremser': '🛑',
      'Parkering': '🅿️', 'Lys': '💡', 'Dekk': '🔄',
      'Motorvei': '🛣️', 'Kryss': '✛', 'Gangfelt': '🚶',
    };

    // Stat: total questions
    document.getElementById('statCats').textContent = cats.length;

    try {
      const all = await api('GET', '/api/questions?limit=1');
      document.getElementById('statTotal').textContent = '700+';
    } catch(e) {}
    document.getElementById('statDone').textContent = '–';
    document.getElementById('statScore').textContent = '–';

    grid.innerHTML = cats.map(c => `
      <div class="cat-card" onclick="startQuiz('${escH(c.id || c.name)}', '${escH(c.name)}')">
        <div class="cat-icon">${icons[c.name] || '📖'}</div>
        <div class="cat-name">${escH(c.name)}</div>
        <div class="cat-count">${c.question_count || ''} spørsmål</div>
        <div class="cat-bar-wrap"><div class="cat-bar" style="width:0%"></div></div>
      </div>
    `).join('');
  } catch(e) {
    grid.innerHTML = '<p style="color:var(--muted);padding:20px">Kunne ikke laste kategorier.</p>';
  }
}

// ── Quiz ──
async function startQuiz(catId, catName) {
  currentCat = { id: catId, name: catName };
  showScreen('screenQuiz');
  const container = document.getElementById('qContainer');
  container.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

  try {
    const res = await api('GET', `/api/questions?category=${encodeURIComponent(catId)}&limit=20`);
    questions = Array.isArray(res) ? res : (res.questions || []);
    if (!questions.length) throw new Error('Ingen spørsmål');
    qIdx = 0; qScore = 0; qAnswered = false;
    renderQuestion();
  } catch(e) {
    // fallback: random questions
    try {
      const res = await api('GET', '/api/questions/random?limit=20');
      questions = Array.isArray(res) ? res : [];
      qIdx = 0; qScore = 0; qAnswered = false;
      renderQuestion();
    } catch(e2) {
      container.innerHTML = '<p style="color:var(--muted);padding:20px">Kunne ikke laste spørsmål.</p>';
    }
  }
}

function pick(obj, lang) {
  if (!obj) return '';
  if (typeof obj === 'string') return obj;
  return obj['no'] || obj['th'] || obj['en'] || Object.values(obj)[0] || '';
}

function renderQuestion() {
  if (qIdx >= questions.length) { showEnd(); return; }
  const q = questions[qIdx];
  qAnswered = false;
  const total = questions.length;
  const pct = ((qIdx) / total * 100).toFixed(0);

  document.getElementById('qProgLbl').textContent = `Spørsmål ${qIdx+1} av ${total}`;
  document.getElementById('qProgFill').style.width = pct + '%';
  document.getElementById('qScore').textContent = qScore;

  const img = q.bildeUrl || q.image_url || '';
  const qText = pick(q.question, 'no') || q.question_text_no || '';
  const opts = q.options || [
    {id:'A', text: pick(q, 'no') || q.answer_a_no},
    {id:'B', text: q.answer_b_no},
    {id:'C', text: q.answer_c_no},
    {id:'D', text: q.answer_d_no},
  ].filter(o => o.text);
  const correct = q.correctOptionId || q.correct_answer || '';
  const expl = pick(q.explanation, 'no') || q.explanation_no || '';

  const container = document.getElementById('qContainer');
  container.innerHTML = `
    <div class="quiz-card">
      <div class="q-left">
        ${img ? `<img class="q-img" src="${img}" alt="" onerror="this.style.display='none'">` : ''}
        <div class="q-text">${escH(qText)}</div>
        <div class="q-tts">
          <button class="tts-btn" id="qTtsBtn" title="Les høyt" onclick="speakQ()">▶</button>
          ${[0.5,0.75,1,1.5,2].map(r=>`<button class="spd-btn${ttsRate===r?' active':''}" data-rate="${r}" onclick="setRate(${r},this)">${r}x</button>`).join('')}
        </div>
      </div>
      <div class="q-right">
        <div class="q-answers" id="qAnswers">
          ${opts.map(o=>`
            <button class="ans-btn" data-id="${o.id}" onclick="selectAns(this,'${o.id}','${correct}','${escH(expl).replace(/'/g,"\\'")}')">
              <span class="ans-letter">${o.id}</span>
              <span>${escH(typeof o.text==='object'?pick(o.text,'no'):o.text)}</span>
            </button>
          `).join('')}
        </div>
        <div class="q-feedback" id="qFeedback"></div>
        <div class="q-explain" id="qExplain"></div>
      </div>
      <div class="q-next-col">
        <button class="q-next-big" id="qNextBig" disabled onclick="nextQ()">Neste →</button>
      </div>
    </div>
  `;
}

function selectAns(btn, picked, correct, expl) {
  if (qAnswered) return;
  qAnswered = true;
  const isOk = picked.toUpperCase() === correct.toUpperCase();
  if (isOk) qScore++;

  document.querySelectorAll('.ans-btn').forEach(b => {
    b.disabled = true;
    const id = b.dataset.id.toUpperCase();
    if (id === correct.toUpperCase() && id === picked.toUpperCase()) b.classList.add('correct');
    else if (b === btn) b.classList.add('wrong');
    else if (id === correct.toUpperCase()) b.classList.add('reveal');
  });

  const fb = document.getElementById('qFeedback');
  fb.textContent = isOk ? '🎉 Riktig!' : '❌ Feil svar';
  fb.className = 'q-feedback ' + (isOk ? 'ok' : 'bad');

  if (expl) {
    const ex = document.getElementById('qExplain');
    ex.textContent = expl;
    ex.classList.add('show');
  }

  document.getElementById('qScore').textContent = qScore;
  const nb = document.getElementById('qNextBig');
  if (nb) nb.disabled = false;

  playSound(isOk ? 'correct' : 'wrong');
}

function nextQ() {
  if (!qAnswered) return;
  qIdx++;
  if (qIdx >= questions.length) showEnd();
  else renderQuestion();
}

function goBack() {
  window.speechSynthesis && window.speechSynthesis.cancel();
  showDash();
}

// ── End ──
function showEnd() {
  showScreen('screenEnd');
  const total = questions.length;
  const pct = qScore / total;
  document.getElementById('endScore').textContent = qScore + ' / ' + total;
  document.getElementById('endEmoji').textContent = pct >= .8 ? '🏆' : pct >= .5 ? '👍' : '💪';
  document.getElementById('endLbl').textContent = pct >= .8 ? 'Fantastisk jobbet!' : pct >= .5 ? 'Bra! Fortsett å øve!' : 'Ikke gi opp!';
}

function retryQuiz() {
  if (currentCat) startQuiz(currentCat.id, currentCat.name);
}

// ── TTS ──
function speakQ() {
  const q = questions[qIdx];
  if (!q) return;
  const text = pick(q.question, 'th') || pick(q.question, 'no') || '';
  if (!window.speechSynthesis) return;
  if (ttsPlaying) {
    window.speechSynthesis.cancel();
    ttsPlaying = false;
    const btn = document.getElementById('qTtsBtn');
    if (btn) { btn.textContent = '▶'; btn.classList.remove('playing'); }
    return;
  }
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = 'th-TH'; utt.rate = ttsRate;
  utt.onstart = () => { ttsPlaying = true; const b=document.getElementById('qTtsBtn'); if(b){b.textContent='⏸';b.classList.add('playing');} };
  utt.onend = utt.onerror = () => { ttsPlaying = false; const b=document.getElementById('qTtsBtn'); if(b){b.textContent='▶';b.classList.remove('playing');} };
  window.speechSynthesis.speak(utt);
}

function setRate(r, el) {
  ttsRate = r;
  document.querySelectorAll('.spd-btn').forEach(b => b.classList.toggle('active', parseFloat(b.dataset.rate) === r));
}

// ── Sound ──
function playSound(type) {
  if (!soundOn) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (type === 'correct') {
      [523.25, 659.25, 783.99].forEach((freq, i) => {
        const osc = ctx.createOscillator(), gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.12);
        gain.gain.setValueAtTime(0.35, ctx.currentTime + i * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 1.1);
        osc.start(ctx.currentTime + i * 0.12);
        osc.stop(ctx.currentTime + i * 0.12 + 1.1);
      });
    } else {
      const osc = ctx.createOscillator(), gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.35);
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.4);
    }
  } catch(e) {}
}

// ── Utils ──
function escH(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Enter key on login
document.getElementById('loginPass').addEventListener('keydown', e => { if(e.key==='Enter') doLogin(); });
document.getElementById('loginEmail').addEventListener('keydown', e => { if(e.key==='Enter') doLogin(); });
</script>
</body>
</html>"""


@webapp_router.get("/web", response_class=HTMLResponse)
async def web_app():
    return HTMLResponse(content=WEBAPP_HTML)
