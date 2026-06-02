from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os as _os
import datetime as _dt

webapp_router = APIRouter()

def _deploy_version() -> str:
    """Returns a stable version string for the current deployment.
    Prefers Railway's injected RAILWAY_GIT_COMMIT_SHA; falls back to startup timestamp.
    Used to verify which build is actually live in production.
    """
    commit = (_os.environ.get('RAILWAY_GIT_COMMIT_SHA') or '')[:8]
    date   = _dt.datetime.utcnow().strftime('%Y-%m-%d')
    return f"{date}-{commit}" if commit else date

DEPLOY_VERSION = _deploy_version()

WEBAPP_HTML = r"""<!DOCTYPE html>
<html lang="th" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta name="deploy-version" content="__DEPLOY_VERSION__">
<title>Thai2Drive</title>
<style>
/* ══════════════════════════════════════════
   CSS VARIABLES & RESET
══════════════════════════════════════════ */
:root {
  --bg: #0B1226;
  --bg2: #111827;
  --card: rgba(255,255,255,.05);
  --card2: rgba(255,255,255,.08);
  --border: rgba(255,255,255,.09);
  --orange: #FF9933;
  --orange-dk: #e6891f;
  --orange-glow: rgba(255,153,51,.18);
  --text: #E2E8F0;
  --muted: #94A3B8;
  --green: #10B981;
  --red: #EF4444;
  --blue: #3B82F6;
  --radius: 16px;
  --topbar-h: 56px;
  --bottom-h: 64px;
}
[data-theme="light"] {
  --bg: #F1F5F9;
  --bg2: #E2E8F0;
  --card: rgba(255,255,255,.85);
  --card2: rgba(255,255,255,.95);
  --border: rgba(0,0,0,.08);
  --text: #0F172A;
  --muted: #64748B;
}
*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
html { font-size: 16px; }
html, body {
  height:100%; min-height:-webkit-fill-available; overflow:hidden;
  background:var(--bg); color:var(--text);
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased;
  font-weight:600;
}
button { font-family:inherit; }
a { color:inherit; text-decoration:none; }

/* ══════════════════════════════════════════
   APP SHELL — NO SCROLL ANYWHERE
══════════════════════════════════════════ */
#app {
  width:100%; height:100vh; height:-webkit-fill-available;
  display:flex; flex-direction:column;
  overflow:hidden; position:relative; z-index:1;
}

/* ══════════════════════════════════════════
   DESKTOP PHONE FRAME
   On viewports wider than 500 px the app
   is centred as a 390 px iPhone silhouette.
   On narrow screens (real phones) it fills
   the whole viewport as before.
══════════════════════════════════════════ */
@media (min-width:500px) {
  html, body {
    background:#010B18;
    background-image:radial-gradient(ellipse 60% 100% at 50% 50%,rgba(22,40,95,.50) 0%,rgba(12,22,58,.25) 45%,#010B18 75%);
    display:flex; align-items:flex-start; justify-content:center;
    overflow:hidden;
    /* No padding — app must fill top to bottom */
  }
  #app {
    width:390px; /* fixed phone width — quiz-mode overrides to 1080 */
    flex-shrink:0;
    /* Full viewport height, no gaps */
    height:100vh; height:-webkit-fill-available;
    /* No top/bottom radius — edge-to-edge vertically */
    border-radius:0;
    box-shadow:
      -8px 0 40px rgba(0,0,0,.60),
       8px 0 40px rgba(0,0,0,.60),
       0 0 80px rgba(0,0,0,.40);
  }
  /* Flag on desktop: contained inside the frame */
  .flag-bg { position:absolute; }
}
#topBar {
  height:var(--topbar-h); flex-shrink:0;
  background:rgba(11,18,38,.92);
  backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  display:none; align-items:center;
  padding:0 16px; gap:12px; z-index:50;
}
[data-theme="light"] #topBar { background:rgba(241,245,249,.95); }
.top-logo {
  display:flex; align-items:center; gap:8px;
  font-weight:900; font-size:1.05rem; letter-spacing:-.3px;
}
.logo-icon {
  width:32px; height:32px; border-radius:9px;
  background:var(--orange);
  display:flex; align-items:center; justify-content:center;
  font-size:17px; font-weight:900; color:#0F172A; flex-shrink:0;
}
.logo-t { color:var(--orange); }
.top-spacer { flex:1; }
#topStreak {
  display:none; align-items:center; gap:5px;
  background:var(--orange-glow); border:1px solid rgba(255,153,51,.3);
  border-radius:20px; padding:5px 12px;
  font-size:.78rem; font-weight:700; color:var(--orange);
}

/* CONTENT area — fills remaining space, no overflow */
#content {
  flex:1; overflow:hidden; position:relative;
  display:flex; flex-direction:column;
}

/* BOTTOM NAV — glass, floating, app-native */
#bottomNav {
  height:var(--bottom-h); flex-shrink:0;
  background:rgba(7,12,26,.88);
  backdrop-filter:blur(32px) saturate(1.6); -webkit-backdrop-filter:blur(32px) saturate(1.6);
  border-top:1px solid rgba(255,255,255,.055);
  box-shadow:0 -1px 0 rgba(255,255,255,.03), 0 -12px 36px rgba(0,0,0,.28);
  display:none; align-items:stretch; z-index:50;
  overflow-x:auto; overflow-y:hidden;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:none;
}
#bottomNav::-webkit-scrollbar { display:none; }
[data-theme="light"] #bottomNav {
  background:rgba(241,245,249,.90);
  border-top:1px solid rgba(0,0,0,.06);
  box-shadow:0 -8px 24px rgba(0,0,0,.06);
}
.bn-tab {
  flex:0 0 auto; min-width:64px; display:flex; flex-direction:column;
  align-items:center; justify-content:center; gap:3px;
  border:none; background:transparent; color:var(--muted);
  cursor:pointer; font-size:.67rem; font-weight:600;
  transition:color .18s; padding:6px 8px; letter-spacing:.1px;
}
.bn-icon { font-size:22px; line-height:1; transition:transform .18s; }
.bn-tab.active { color:var(--orange); }
.bn-tab.active .bn-icon { transform:scale(1.14); }
.bn-tab:active .bn-icon { transform:scale(.88); }

/* ══════════════════════════════════════════
   SCREENS — each fills content area, height:100%
══════════════════════════════════════════ */
.screen {
  display:none; height:100%; width:100%;
  position:absolute; top:0; left:0;
  flex-direction:column; overflow:hidden;
  z-index:1; /* always above flag-bg (z-index:0) */
}
.screen.active { display:flex; }

/* ══════════════════════════════════════════
   THAI FLAG BACKGROUND
══════════════════════════════════════════ */
.flag-bg {
  /* absolute — so it's contained within #app and clipped by the phone frame on desktop */
  position:absolute; inset:0; z-index:0; pointer-events:none;
  /* Thai flag: red / white / navy / white / red — exact proportions 1:1:2:1:1 */
  background:linear-gradient(180deg,
    #A51931 0%,    #A51931 16.66%,
    #F0F0F0 16.66%, #F0F0F0 33.33%,
    #1A1464 33.33%, #1A1464 66.66%,
    #F0F0F0 66.66%, #F0F0F0 83.33%,
    #A51931 83.33%, #A51931 100%);
}
/* Dark overlay so text stays readable */
.flag-bg::before {
  content:''; position:absolute; inset:0;
  background:rgba(10,14,30,.15);
}
.flag-bg::after { display:none; }

/* ══════════════════════════════════════════
   AUTH SCREEN
══════════════════════════════════════════ */
#screenAuth {
  align-items:center; justify-content:center;
  padding:16px; overflow-y:auto;
}
.auth-card {
  background:rgba(15,23,42,.87);
  border:1px solid var(--border); border-radius:22px;
  padding:28px 26px;
  width:100%; max-width:380px;
  backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
  box-shadow:0 28px 60px rgba(0,0,0,.5);
  flex-shrink:0;
}
[data-theme="light"] .auth-card {
  background:rgba(255,255,255,.93);
  box-shadow:0 16px 48px rgba(0,0,0,.12);
}
.auth-header { text-align:center; margin-bottom:20px; }
.auth-big-icon {
  width:64px; height:64px; border-radius:18px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  display:flex; align-items:center; justify-content:center;
  font-size:32px; margin:0 auto 12px;
  box-shadow:0 8px 24px rgba(255,153,51,.4);
}
.auth-header h1 { font-size:1.5rem; font-weight:900; letter-spacing:-.5px; }
.auth-header h1 span { color:var(--orange); }
.auth-header p { color:var(--muted); font-size:.82rem; margin-top:4px; }
.auth-flags { display:flex; gap:8px; justify-content:center; margin-top:8px; }
.auth-flag {
  width:28px; height:28px; border-radius:50%;
  overflow:hidden; display:inline-flex; flex-shrink:0;
}
.auth-flag svg { width:100%; height:100%; display:block; }

.auth-tabs {
  display:flex; gap:4px;
  background:rgba(255,255,255,.05); border-radius:11px; padding:4px;
  margin-bottom:20px;
}
[data-theme="light"] .auth-tabs { background:rgba(0,0,0,.06); }
.auth-tab {
  flex:1; padding:8px; border-radius:8px;
  border:none; background:transparent;
  color:var(--muted); font-size:.85rem; font-weight:700;
  cursor:pointer; transition:all .2s;
}
.auth-tab.active { background:var(--orange); color:#0F172A; }

.form-group { margin-bottom:12px; }
.form-group label {
  display:block; font-size:.7rem; font-weight:700;
  color:var(--muted); margin-bottom:5px; letter-spacing:.5px;
  text-transform:uppercase;
}
.form-group input {
  width:100%; padding:11px 14px;
  background:rgba(255,255,255,.06);
  border:1.5px solid var(--border);
  border-radius:11px; color:var(--text);
  font-size:.88rem; outline:none;
  transition:border-color .2s, box-shadow .2s;
}
[data-theme="light"] .form-group input { background:rgba(0,0,0,.04); }
.form-group input:focus {
  border-color:var(--orange);
  box-shadow:0 0 0 3px rgba(255,153,51,.12);
}
.form-group input::placeholder { color:rgba(148,163,184,.5); }
/* Password visibility toggle */
.pw-wrap { position:relative; }
.pw-wrap input { padding-right:42px; }
.pw-eye {
  position:absolute; right:0; top:0; bottom:0;
  width:42px; display:flex; align-items:center; justify-content:center;
  background:none; border:none; cursor:pointer; color:var(--muted);
  font-size:1rem; padding:0; border-radius:0 11px 11px 0;
  -webkit-tap-highlight-color:transparent;
  transition:color .15s;
}
.pw-eye:hover, .pw-eye:focus { color:var(--orange); outline:none; }

.auth-btn {
  width:100%; padding:13px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:800; font-size:.95rem;
  border:none; border-radius:11px;
  cursor:pointer; margin-top:4px;
  box-shadow:0 4px 16px rgba(255,153,51,.35);
  transition:transform .15s, box-shadow .15s;
}
.auth-btn:hover { transform:translateY(-1px); box-shadow:0 6px 20px rgba(255,153,51,.45); }
.auth-btn:active { transform:translateY(0); }
.auth-btn:disabled { opacity:.5; cursor:not-allowed; transform:none; }

.auth-error {
  background:rgba(239,68,68,.1); border:1px solid rgba(239,68,68,.3);
  border-radius:9px; padding:10px 13px;
  color:#FCA5A5; font-size:.82rem; margin-bottom:14px; display:none;
}
.auth-error.show { display:block; }
.auth-success {
  background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.3);
  border-radius:9px; padding:10px 13px;
  color:#6EE7B7; font-size:.82rem; margin-bottom:14px; display:none;
}
.auth-success.show { display:block; }

.forgot-link { text-align:right; margin:-4px 0 12px; }
.forgot-link a { font-size:.76rem; color:var(--muted); cursor:pointer; }
.forgot-link a:hover { color:var(--orange); }

/* ══════════════════════════════════════════
   HOME SCREEN — flex column, no scroll
══════════════════════════════════════════ */
#screenHome {
  padding:24px 16px 20px;
  justify-content:flex-start;
  overflow-y:auto; overflow-x:hidden;
  -webkit-overflow-scrolling:touch;
  gap:14px;
}
.home-top {
  display:flex; flex-direction:column; align-items:center;
  text-align:center; gap:12px;
}
.home-logo-row {
  display:flex; flex-direction:column; align-items:center;
  gap:5px; margin-bottom:0;
}
.home-logo-box {
  width:60px; height:60px; border-radius:16px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  display:flex; align-items:center; justify-content:center;
  font-size:28px; font-weight:900; color:#0F172A;
  box-shadow:0 8px 24px rgba(255,153,51,.40);
}
.home-title { font-size:1.85rem; font-weight:900; letter-spacing:-.5px; margin-top:2px; }
.home-title span { color:var(--orange); }
.home-sub { font-size:.78rem; color:var(--muted); font-weight:500; letter-spacing:.2px; }

.streak-badge {
  display:inline-flex; align-items:center; gap:7px;
  background:rgba(255,153,51,.11); border:1px solid rgba(255,153,51,.25);
  border-radius:50px; padding:5px 14px;
}
.streak-fire { font-size:1rem; }
.streak-num { font-size:1.1rem; font-weight:900; color:var(--orange); }
.streak-lbl { font-size:.78rem; color:var(--muted); font-weight:600; }

.home-cta {
  width:100%; padding:16px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:900; font-size:1rem;
  border:none; border-radius:14px; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:10px;
  box-shadow:0 6px 24px rgba(255,153,51,.4);
  transition:transform .15s, box-shadow .15s;
}
.home-cta:hover { transform:translateY(-2px); box-shadow:0 8px 28px rgba(255,153,51,.5); }
.home-cta:active { transform:translateY(0); }

.home-sec-btns {
  display:grid; grid-template-columns:1fr 1fr;
  gap:9px;
}
.home-sec-btn {
  padding:13px 10px;
  background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12);
  backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px);
  border-radius:14px; color:var(--text); font-weight:700;
  font-size:.85rem; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:6px;
  transition:border-color .2s, background .2s;
}
.home-sec-btn:hover { border-color:rgba(255,255,255,.3); background:rgba(255,255,255,.08); }

/* Stats — one unified card, three columns with vertical dividers */
.home-stats {
  display:grid; grid-template-columns:repeat(3,1fr);
  gap:0;
  background:rgba(255,255,255,.05);
  border:1px solid var(--border);
  border-radius:16px; overflow:hidden;
}
.home-stat {
  background:transparent; border:none;
  border-right:1px solid var(--border);
  border-radius:0; padding:14px 8px; text-align:center;
}
.home-stat:last-child { border-right:none; }
.home-stat-num { font-size:1.55rem; font-weight:900; color:var(--orange); line-height:1; }
.home-stat-lbl {
  font-size:.62rem; color:var(--muted); font-weight:700;
  margin-top:5px; letter-spacing:.4px; text-transform:uppercase;
}

/* Premium badge — green pill matching mobile */
.premium-banner {
  background:rgba(16,185,129,.1);
  border:1px solid rgba(16,185,129,.25);
  border-radius:50px; padding:10px 20px;
  display:flex; align-items:center; justify-content:center; gap:8px;
  align-self:center;
}
.premium-banner .pb-icon { font-size:1rem; }
.premium-banner .pb-text h4 { font-size:.85rem; font-weight:800; color:var(--green); }
.premium-banner .pb-text p { display:none; }
.premium-badge {
  display:inline-flex; align-items:center; gap:4px;
  background:rgba(255,153,51,.2); border:1px solid rgba(255,153,51,.4);
  border-radius:20px; padding:3px 9px;
  font-size:.68rem; font-weight:800; color:var(--orange);
}
.admin-badge {
  display:inline-flex; align-items:center; gap:4px;
  background:rgba(16,185,129,.15); border:1px solid rgba(16,185,129,.3);
  border-radius:20px; padding:3px 9px;
  font-size:.68rem; font-weight:800; color:var(--green);
}

/* ══════════════════════════════════════════
   CATEGORIES SCREEN — header fixed, grid scrolls
══════════════════════════════════════════ */
#screenCats {
  padding:0;
  background:#0B1226;
}
.cats-header {
  padding:14px 16px 10px; flex-shrink:0;
  background:transparent;
}
.screen-title {
  font-size:1.6rem; font-weight:900; letter-spacing:-.3px;
}
.screen-title span { color:var(--muted); font-size:.95rem; font-weight:600; margin-left:6px; }
.cats-scroll {
  flex:1; overflow-y:auto; overflow-x:hidden;
  padding:0 16px 16px;
  -webkit-overflow-scrolling:touch;
}
.cats-scroll::-webkit-scrollbar { width:4px; }
.cats-scroll::-webkit-scrollbar-track { background:transparent; }
.cats-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:2px; }

.cat-grid {
  display:grid;
  /* auto-fit responds to the container width, not the viewport —
     minmax(140px,1fr) gives 2 cols in the 390 px shell, more on a
     real wide screen. No viewport media queries needed. */
  grid-template-columns:repeat(auto-fit, minmax(140px,1fr));
  gap:10px;
}

.cat-card {
  background:#131B2E; border:1.5px solid rgba(255,255,255,.10);
  border-radius:14px; padding:14px 12px;
  cursor:pointer; transition:border-color .2s, transform .15s, box-shadow .2s;
  display:flex; flex-direction:column; gap:6px;
  color:var(--text);
}
[data-theme="light"] .cat-card {
  background:rgba(255,255,255,.82); border-color:rgba(0,0,0,.1); /* color inherited from var(--text) */
}
.cat-count { display:none; }
.cat-card:hover {
  border-color:var(--orange); transform:translateY(-2px);
  box-shadow:0 8px 20px rgba(255,153,51,.12);
}
.cat-card:active { transform:translateY(0); }
.cat-icon { font-size:2rem; line-height:1; }
.cat-name { font-weight:800; font-size:1.05rem; line-height:1.3; }
.cat-count { font-size:.9rem; color:var(--muted); font-weight:500; }
.cat-bar-wrap {
  height:3px; background:rgba(255,255,255,.07);
  border-radius:2px; overflow:hidden; margin-top:2px;
}
[data-theme="light"] .cat-bar-wrap { background:rgba(0,0,0,.07); }
.cat-bar { height:100%; background:var(--orange); border-radius:2px; }

/* ══════════════════════════════════════════
   QUIZ SCREEN — fully height-based, NO scroll
══════════════════════════════════════════ */
#screenQuiz { padding:0; background:#0B1226; }
[data-theme="light"] #screenQuiz { background:#E8EEF6; }

.quiz-top {
  padding:11px 16px 10px; flex-shrink:0;
  background:rgba(11,18,38,.90);
  backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid rgba(255,255,255,.055);
  display:flex; align-items:center; gap:12px;
}
[data-theme="light"] .quiz-top { background:var(--bg2); }

/* Light theme: slightly lighter overlay */
[data-theme="light"] .flag-bg::before { background:rgba(230,236,244,.70); }
[data-theme="light"] .ans-btn {
  background:rgba(255,255,255,.75); border-color:rgba(0,0,0,.12);
}
[data-theme="light"] .ans-btn:hover:not(:disabled) {
  background:rgba(255,153,51,.12); border-color:var(--orange);
}
[data-theme="light"] .q-text { color:#0F172A; }
[data-theme="light"] .q-img-wrap { background:rgba(255,255,255,.7); }
[data-theme="light"] .q-feedback { background:rgba(255,255,255,.75); }
[data-theme="light"] .q-explain  { background:#fff; color:#1a1a1a; }
[data-theme="light"] .q-settings-bar,
[data-theme="light"] .q-settings  { background:rgba(255,255,255,.6); }
.back-btn {
  padding:6px 12px; border-radius:8px;
  border:1px solid rgba(255,255,255,.10); background:rgba(255,255,255,.04);
  color:var(--muted); font-size:.82rem; font-weight:600;
  cursor:pointer; transition:border-color .18s, color .18s; flex-shrink:0;
}
.back-btn:hover { border-color:rgba(255,153,51,.40); color:var(--text); }

.quiz-prog-wrap { flex:1; min-width:0; }
.quiz-prog-lbl { font-size:.7rem; color:var(--muted); margin-bottom:4px; font-weight:600; }
.quiz-prog-bar {
  height:5px; background:rgba(255,255,255,.08); border-radius:3px; overflow:hidden;
}
[data-theme="light"] .quiz-prog-bar { background:rgba(0,0,0,.08); }
.quiz-prog-fill {
  height:100%;
  background:linear-gradient(90deg,var(--orange),#FFB347);
  border-radius:3px; transition:width .35s;
}
.quiz-score-badge {
  display:flex; align-items:center; gap:4px;
  background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.25);
  border-radius:20px; padding:4px 11px;
  font-size:.78rem; font-weight:800; color:var(--green); flex-shrink:0;
}

/* ══ QUIZ BODY — one scrollable column, no nested scroll ══
   The only scrollbar lives here. Everything inside is natural height. */
.quiz-body {
  flex:1;
  overflow-y:auto; overflow-x:hidden;
  -webkit-overflow-scrolling:touch;
  padding:16px 16px calc(104px + env(safe-area-inset-bottom, 0px));
}
.quiz-body::-webkit-scrollbar { width:3px; }
.quiz-body::-webkit-scrollbar-track { background:transparent; }
.quiz-body::-webkit-scrollbar-thumb { background:rgba(255,255,255,.10); border-radius:2px; }

/* Quiz card: straight vertical flex — no grid, no columns */
.quiz-card {
  display:flex; flex-direction:column; gap:12px;
  width:100%;
}

/* Left section: image → question text → TTS — full width, auto height */
.q-left {
  display:flex; flex-direction:column; gap:10px;
  width:100%; height:auto; overflow:visible;
}

/* Image: full width, no border — shape and radius are enough */
.q-img-wrap {
  width:100%; border-radius:12px; overflow:hidden;
  background:rgba(255,255,255,.03);
  max-height:200px; display:flex; align-items:center; justify-content:center;
  transition:outline .3s ease, box-shadow .3s ease;
}
.q-img { width:100%; max-height:200px; object-fit:contain; display:block; }

/* Question text */
.q-text {
  font-size:.95rem; font-weight:700; line-height:1.68;
}
.q-settings-bar {
  display:flex; align-items:center; gap:12px;
  background:rgba(255,255,255,.03);
  border-radius:12px; padding:10px 14px;
  width:100%;
}
.q-settings-rows { display:flex; flex-direction:column; gap:5px; }
.q-settings-row  { display:flex; align-items:center; gap:5px; flex-wrap:wrap; }
.q-settings-lbl  { font-size:.6rem; color:var(--muted); font-weight:800;
                    width:34px; flex-shrink:0; text-transform:uppercase; letter-spacing:.04em; }
.tts-play {
  width:38px; height:38px; border-radius:50%;
  border:2px solid var(--orange);
  background:rgba(255,153,51,.08);
  color:var(--orange); cursor:pointer; font-size:14px;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0;
}
.tts-play.playing {
  animation: tts-pulse 0.6s ease-in-out infinite;
}
@keyframes tts-pulse {
  0%,100% { background:rgba(255,153,51,.2);  box-shadow:0 0 0 0   rgba(255,153,51,.7); }
  50%      { background:rgba(255,153,51,.55); box-shadow:0 0 0 12px rgba(255,153,51,0); }
}
.spd-btn {
  padding:3px 9px; border-radius:20px;
  border:1.5px solid var(--border); background:transparent;
  color:var(--muted); font-size:.68rem; font-weight:800; cursor:pointer;
  transition:all .2s;
}
.spd-btn.active { background:rgba(255,153,51,.15); border-color:var(--orange); color:var(--orange); }
.vol-btn {
  padding:3px 9px; border-radius:20px;
  border:1.5px solid var(--border); background:transparent;
  color:var(--muted); font-size:.8rem; cursor:pointer;
  transition:all .2s;
}
.vol-btn.active { background:rgba(255,153,51,.15); border-color:var(--orange); color:var(--orange); }

/* Mid section: answers + feedback + explain + next — full width, auto height */
.q-mid {
  display:flex; flex-direction:column; gap:10px;
  width:100%; height:auto; overflow:visible;
}
.q-answers {
  display:flex; flex-direction:column; gap:8px; flex-shrink:0;
}
.ans-btn {
  display:flex; align-items:center; gap:14px;
  padding:15px 16px;
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.08); border-radius:14px;
  cursor:pointer; text-align:left; color:var(--text);
  font-size:.88rem; font-weight:600;
  transition:border-color .18s, background .18s;
  width:100%;
}
.ans-btn:hover:not(:disabled) {
  border-color:rgba(255,153,51,.35);
  background:rgba(255,153,51,.06);
}
.ans-btn:active:not(:disabled) { opacity:.82; }
.ans-btn:disabled { cursor:default; }
.ans-btn.correct { border-color:rgba(16,185,129,.45); background:rgba(16,185,129,.10); }
.ans-btn.wrong   { border-color:rgba(239,68,68,.40);  background:rgba(239,68,68,.09);  }
.ans-btn.reveal  { border-color:rgba(16,185,129,.45); background:rgba(16,185,129,.07); }
.ans-letter {
  width:32px; height:32px; border-radius:50%;
  background:rgba(255,153,51,.12); color:var(--orange);
  font-size:.76rem; font-weight:900;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0; transition:background .18s, color .18s;
  border:1px solid rgba(255,153,51,.20);
}
.ans-btn.correct .ans-letter { background:rgba(16,185,129,.25); color:var(--green); border-color:rgba(16,185,129,.45); }
.ans-btn.wrong   .ans-letter { background:rgba(239,68,68,.22);  color:#FCA5A5;      border-color:rgba(239,68,68,.40); }
.ans-btn.reveal  .ans-letter { background:rgba(16,185,129,.25); color:var(--green); border-color:rgba(16,185,129,.45); }
.ans-text { flex:1; line-height:1.62; font-size:.93rem; }

.q-feedback {
  padding:10px 12px; border-radius:10px;
  font-size:.92rem; font-weight:700;
  display:none; align-items:center; gap:7px; flex-shrink:0;
}
.q-feedback.ok  { background:rgba(16,185,129,.08); border:1px solid rgba(16,185,129,.22); color:#6EE7B7; display:flex; }
.q-feedback.bad { background:rgba(255,153,51,.06); border:1px solid rgba(255,153,51,.20); color:#FCD4A0; display:flex; }
.q-explain {
  padding:12px 14px;
  background:#FFFFFF; border:2px solid var(--orange);
  border-radius:10px; font-size:.88rem; color:#1a1a1a;
  line-height:1.7; display:none; flex-shrink:0;
}
.q-explain.show { display:block; }

/* Next button — in normal flow, shown only after an answer is selected. */
.q-next-mobile {
  display:block;
  position:static;
  width:100%; padding:14px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:900; font-size:.9rem;
  border:none; border-radius:12px; cursor:pointer;
  margin-top:2px;
  box-shadow:0 4px 12px rgba(255,153,51,.20);
}
.q-next-mobile:disabled { display:none; opacity:.30; cursor:not-allowed; }
.q-next-mobile:not(:disabled):active { opacity:.85; }

/* Desktop side column — permanently hidden (we use q-next-mobile everywhere) */
.q-next-col { display:none !important; }
/* Keep the class defined but invisible */
.q-next-big { display:none !important; }

.q-bookmark-btn {
  width:48px; height:48px; border-radius:12px;
  border:1.5px solid var(--border); background:rgba(255,255,255,.05);
  color:var(--muted); font-size:18px; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  transition:all .2s; flex-shrink:0;
}
.q-bookmark-btn:hover { border-color:var(--orange); color:var(--orange); }
.q-bookmark-btn.bookmarked { border-color:var(--orange); color:var(--orange); background:rgba(255,153,51,.12); }

/* ══════════════════════════════════════════
   QUIZ — LEFT/RIGHT COLUMN SHELL
   Mobile:  left-col fills everything, right-col hidden.
   Desktop: left-col fixed 400 px, right-col flex:1 AI panel.
            #app expands beyond the phone-frame max-width.
══════════════════════════════════════════ */

/* Mobile default — single-column, unchanged */
.quiz-left-col {
  display:flex; flex-direction:column; flex:1; overflow:hidden; min-width:0;
}
.quiz-right-col { display:none; }

/* Mobile AI section — inline, expands below answers after answering.
   :empty hides it when blank so it takes zero space before answering. */
.quiz-ai-mobile {
  display:flex; flex-direction:column; gap:10px;
  /* no top margin — gap in q-mid handles spacing */
}
.quiz-ai-mobile:empty { display:none; }

/* ── Desktop AI learning layout ── */
@media (min-width:700px) {
  /* Mobile AI section is replaced by the right panel — hide it */
  .quiz-ai-mobile { display:none !important; }

  /* App frame expands to AI dashboard when quiz is active */
  #app.quiz-mode {
    width: min(1080px, 96vw);
    max-width: none;
    margin-left: auto;
    margin-right: auto;
    border-radius: 16px;
    box-shadow:
      0 0 0 1px rgba(255,255,255,.07),
      0 20px 60px rgba(0,0,0,.70),
      0 60px 160px rgba(0,0,0,.55);
    transition: width .30s cubic-bezier(.4,0,.2,1), border-radius .30s ease;
  }

  /* Teacher frame — same width as quiz-mode */
  #app.teacher-mode {
    width: min(860px, 96vw);
    max-width: none;
    margin-left: auto;
    margin-right: auto;
    border-radius: 16px;
    box-shadow:
      0 0 0 1px rgba(255,255,255,.07),
      0 20px 60px rgba(0,0,0,.70),
      0 60px 160px rgba(0,0,0,.55);
    transition: width .30s cubic-bezier(.4,0,.2,1), border-radius .30s ease;
  }

  /* Teacher screen: two-column layout on desktop */
  #screenTeacher.active {
    flex-direction: row !important;
  }
  .teacher-chat-col {
    flex: 1; min-width: 0;
    display: flex; flex-direction: column;
    border-right: 1px solid rgba(255,255,255,.07);
  }
  .teacher-side-panel {
    width: 240px; flex-shrink: 0;
    display: flex; flex-direction: column;
    padding: 20px 16px; gap: 8px;
    overflow-y: auto;
    background: rgba(0,0,0,.22);
    border-left: 1px solid rgba(255,255,255,.07);
  }
  .tsp-title {
    font-size: .68rem; font-weight: 800; letter-spacing: .10em;
    text-transform: uppercase; color: var(--orange);
    margin-bottom: 6px; padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,153,51,.25);
  }
  .tsp-btn {
    display: flex; align-items: center; gap: 11px;
    background: #1a2744;
    border: 1px solid rgba(59,130,246,.22);
    color: #F8FAFC; border-radius: 12px;
    padding: 12px 14px; font-size: .88rem; font-weight: 700;
    cursor: pointer; text-align: left;
    transition: background .15s, border-color .15s, transform .12s;
    width: 100%; line-height: 1.3;
  }
  .tsp-btn:hover {
    background: #1e3a5f;
    border-color: rgba(255,153,51,.70);
    color: #fff;
    transform: translateX(3px);
  }
  .tsp-btn:active { transform: scale(.97); }
  [data-theme="light"] .tsp-btn {
    background: #1e3a5f; border-color: rgba(59,130,246,.35); color: #F8FAFC;
  }
  [data-theme="light"] .tsp-btn:hover {
    background: #1a2744; border-color: rgba(255,153,51,.60);
  }
  [data-theme="light"] .tsp-title { color: var(--orange); border-bottom-color: rgba(255,153,51,.3); }

  /* Quiz screen becomes a horizontal flex */
  #screenQuiz { flex-direction:row; }

  /* Left col: fixed width, scrollable quiz */
  .quiz-left-col {
    flex: 0 0 420px;
    border-right: 1px solid rgba(255,255,255,.06);
  }

  /* On desktop, image lives in the right panel — hide it in the left */
  .quiz-left-col .q-img-wrap { display:none; }

  /* Right col: flex, takes remaining space */
  .quiz-right-col {
    display:flex; flex-direction:column;
    flex:1; min-width:320px;
    background:#080F1E;
    overflow:hidden;
  }
}

/* ══════════════════════════════════════════
   AI LEARNING PANEL — ANIMATIONS & POLISH
   Architecture hooks: voice · video · danger · hints
══════════════════════════════════════════ */

/* ─ Keyframes — opacity only, no positional movement ─ */
@keyframes aiBlockIn {
  from { opacity:0; }
  to   { opacity:1; }
}
@keyframes aiVerdictPop {
  from { opacity:0; }
  to   { opacity:1; }
}
@keyframes aiMobileIn {
  from { opacity:0; }
  to   { opacity:1; }
}

/* Staggered animation class — set --i:N on each block.
   Fast fade-in, no movement. */
.ai-block {
  animation: aiBlockIn .20s ease both;
  animation-delay: calc(var(--i,0) * 30ms);
}

/* ─ Image box ─ */
.quiz-ai-imgbox {
  flex:0 0 auto; position:relative;
  overflow:hidden; background:#03060E;
  transition:box-shadow .45s ease;
}
.quiz-ai-imgbox.glow-ok  { box-shadow:inset 0 0 0 1px rgba(16,185,129,.22); }
.quiz-ai-imgbox.glow-bad { box-shadow:inset 0 0 0 1px rgba(251,146,60,.22); }

.quiz-ai-img {
  width:100%; display:block;
  height:252px; object-fit:contain; object-position:center;
}
.quiz-ai-img.flash-ok, .quiz-ai-img.flash-bad { /* image stays neutral — feedback lives in UI, not the road scene */ }

/* Gradient fade bottom + colour tint overlay */
.quiz-ai-img-overlay {
  position:absolute; inset:0; pointer-events:none;
  background:linear-gradient(to bottom, transparent 55%, #080F1E 100%);
  transition:background .45s ease;
}
.quiz-ai-img-overlay.result-ok  { background:linear-gradient(to bottom, transparent 55%, #080F1E 100%); }
.quiz-ai-img-overlay.result-bad { background:linear-gradient(to bottom, transparent 55%, #080F1E 100%); }

.quiz-ai-img-badge {
  position:absolute; bottom:10px; left:12px;
  font-size:.60rem; font-weight:800; letter-spacing:.7px; text-transform:uppercase;
  color:rgba(255,255,255,.40); pointer-events:none;
  display:flex; align-items:center; gap:5px;
}

/* ─ AI scrollable panel ─ */
.quiz-ai-panel {
  flex:1; overflow-y:auto; overflow-x:hidden;
  display:flex; flex-direction:column;
  -webkit-overflow-scrolling:touch;
}
.quiz-ai-panel::-webkit-scrollbar { width:2px; }
.quiz-ai-panel::-webkit-scrollbar-thumb { background:rgba(255,255,255,.08); border-radius:2px; }

/* Sticky instructor header — stays visible while body scrolls */
.quiz-ai-panel-header {
  position:sticky; top:0; z-index:5;
  background:rgba(8,15,30,.96);
  backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid rgba(255,255,255,.055);
  padding:14px 20px 12px;
  display:flex; flex-direction:column; gap:9px;
  flex-shrink:0;
}
.quiz-ai-panel-title { display:flex; align-items:center; gap:10px; }
.quiz-ai-robot { font-size:1.3rem; flex-shrink:0; line-height:1; }
.quiz-ai-panel-name { font-size:.88rem; font-weight:900; color:var(--text); letter-spacing:-.1px; }
.quiz-ai-panel-sub  { font-size:.67rem; color:var(--muted); margin-top:1px; }

.quiz-ai-status {
  font-size:.68rem; font-weight:700;
  padding:3px 10px; border-radius:20px; align-self:flex-start;
  background:rgba(255,255,255,.05); border:1px solid var(--border); color:var(--muted);
  transition:background .3s, border-color .3s, color .3s;
}
.quiz-ai-status.idle { /* no pulse — static is calmer */ }
.quiz-ai-status.ok   { color:var(--green); background:rgba(16,185,129,.10); border-color:rgba(16,185,129,.30); }
.quiz-ai-status.bad  { color:#FCA5A5;      background:rgba(239,68,68,.08);  border-color:rgba(239,68,68,.24); }

/* Padded body — content zone */
.quiz-ai-body {
  padding:16px 20px 20px;
  display:flex; flex-direction:column; gap:12px;
}

/* Idle placeholder */
.quiz-ai-idle {
  display:flex; flex-direction:column; align-items:center;
  text-align:center; gap:14px; padding:24px 20px;
}

.quiz-ai-idle-icon { font-size:1.9rem; opacity:.20; }
.quiz-ai-idle-text { font-size:.80rem; color:var(--muted); line-height:1.7; max-width:210px; }

/* ─ Verdict banner — snappy pop ─ */
.quiz-ai-verdict {
  animation: aiVerdictPop .38s ease-out both;
  display:flex; align-items:center; gap:11px;
  padding:14px 16px; border-radius:13px;
  font-size:.92rem; font-weight:800;
  position:relative; overflow:hidden;
}
/* Left accent stripe */
.quiz-ai-verdict::before {
  content:''; position:absolute; left:0; top:0; bottom:0;
  width:3px; border-radius:3px 0 0 3px;
}
.quiz-ai-verdict.ok  { background:rgba(16,185,129,.08); border:none; color:var(--green);
  border-radius:0 13px 13px 0; }
.quiz-ai-verdict.ok::before  { background:rgba(16,185,129,.70); }
.quiz-ai-verdict.bad { background:rgba(239,68,68,.07);  border:none; color:#FCA5A5;
  border-radius:0 13px 13px 0; }
.quiz-ai-verdict.bad::before { background:rgba(239,68,68,.70); }
.quiz-ai-verdict-icon { font-size:1.15rem; flex-shrink:0; }

/* ─ Danger card — red left stripe, no full border ─ */
.quiz-ai-danger {
  background:rgba(239,68,68,.05);
  border-left:3px solid rgba(239,68,68,.55);
  border-radius:0 12px 12px 0;
  padding:14px 18px 14px 16px;
  display:flex; gap:13px; align-items:flex-start;
}
.quiz-ai-danger-icon {
  font-size:1.2rem; flex-shrink:0; line-height:1.2;
  background:rgba(239,68,68,.14); padding:7px;
  border-radius:8px;
}
.quiz-ai-danger-label {
  font-size:.60rem; font-weight:900; text-transform:uppercase;
  letter-spacing:1px; color:#FCA5A5; margin-bottom:7px;
}
.quiz-ai-danger-text { font-size:.85rem; line-height:1.78; color:var(--text); }

/* ─ Explanation card — no border, slight background lift ─ */
.quiz-ai-explain {
  background:rgba(255,255,255,.05);
  border-radius:12px; padding:16px 18px;
}
.quiz-ai-card-label {
  font-size:.60rem; font-weight:900; text-transform:uppercase;
  letter-spacing:1px; color:var(--muted); margin-bottom:10px;
  display:flex; align-items:center; gap:5px;
}
.quiz-ai-card-text { font-size:.86rem; line-height:1.82; color:var(--text); }

/* ─ Instructor tip card — orange left stripe, no full border ─ */
.quiz-ai-tip {
  background:rgba(255,153,51,.04);
  border-left:3px solid rgba(255,153,51,.45);
  border-radius:0 12px 12px 0;
  padding:14px 18px 14px 16px;
  display:flex; gap:13px; align-items:flex-start;
}
.quiz-ai-tip-icon {
  font-size:1.1rem; flex-shrink:0; line-height:1.2;
  background:rgba(255,153,51,.14); padding:7px;
  border-radius:8px;
}
.quiz-ai-tip-label {
  font-size:.60rem; font-weight:900; text-transform:uppercase;
  letter-spacing:1px; color:var(--orange); margin-bottom:7px;
}
.quiz-ai-tip-text { font-size:.85rem; line-height:1.78; color:var(--text); }

/* ─ Future architecture slots (hidden — wired up when features land) ─
   Each slot is a named hook point for: ai-voice-teacher · visual-danger-zones
   · animated-traffic-overlay · ai-hint-generator.
   Activate by removing display:none and injecting content via data-hook. ─ */
.quiz-ai-future-hooks,
.quiz-ai-slot { display:none; }

/* ─ Multi-level explanation: Vis mer expand ─ */
.ai-expand-btn {
  display:inline-flex; align-items:center; gap:5px;
  margin-top:10px; padding:0;
  font-size:.74rem; font-weight:800; color:var(--orange);
  background:none; border:none; cursor:pointer; opacity:.75;
  letter-spacing:.1px; transition:opacity .15s;
}
.ai-expand-btn::after {
  content:'›'; font-size:1rem; line-height:1;
  display:inline-block; transition:transform .22s ease;
}
.ai-expand-btn.expanded::after { transform:rotate(90deg); }
.ai-expand-btn:hover { opacity:1; }
.ai-expand-content {
  max-height:0; overflow:hidden;
  font-size:.85rem; line-height:1.80; color:var(--text);
  transition:max-height .20s ease, opacity .18s ease, padding .18s ease;
  opacity:0; padding-top:0;
}
.ai-expand-content.open {
  max-height:600px; opacity:1;
  padding-top:11px;
  border-top:1px solid rgba(255,255,255,.07);
  margin-top:10px;
}

/* ─ Smart learning alert cards ─ */
/* Four types: danger (red), rule (blue), weather (cyan), exam (purple) */
.ai-alert {
  display:flex; gap:12px; align-items:flex-start;
  padding:12px 18px 12px 16px;
  border-radius:0 12px 12px 0;
}
.ai-alert-danger  { background:rgba(239,68,68,.05);   border-left:3px solid rgba(239,68,68,.50); }
.ai-alert-rule    { background:rgba(59,130,246,.05);  border-left:3px solid rgba(59,130,246,.50); }
.ai-alert-weather { background:rgba(125,211,252,.05); border-left:3px solid rgba(125,211,252,.50); }
.ai-alert-exam    { background:rgba(168,85,247,.05);  border-left:3px solid rgba(168,85,247,.50); }
.ai-alert-icon { font-size:1.1rem; flex-shrink:0; line-height:1.3; }
.ai-alert-label {
  font-size:.60rem; font-weight:900; text-transform:uppercase;
  letter-spacing:1px; margin-bottom:6px;
}
.ai-alert-danger  .ai-alert-label { color:#FCA5A5; }
.ai-alert-rule    .ai-alert-label { color:#93C5FD; }
.ai-alert-weather .ai-alert-label { color:#7DD3FC; }
.ai-alert-exam    .ai-alert-label { color:#C4B5FD; }
.ai-alert-text { font-size:.83rem; line-height:1.72; color:var(--text); }

/* ─ Mobile AI section — lightweight inline expand ─ */
.quiz-ai-mobile {
  display:flex; flex-direction:column; gap:8px;
}
.quiz-ai-mobile:empty { display:none; }
.quiz-ai-mobile:not(:empty) {
  margin-top:2px; padding-top:10px;
  border-top:1px solid rgba(255,255,255,.07);
  animation:aiMobileIn .20s ease both;
}
/* Mobile: slightly more compact */
.quiz-ai-mobile .quiz-ai-verdict { padding:11px 14px; font-size:.88rem; }
.quiz-ai-mobile .quiz-ai-explain,
.quiz-ai-mobile .quiz-ai-danger,
.quiz-ai-mobile .quiz-ai-tip,
.quiz-ai-mobile .ai-alert        { padding:12px 14px; }
.quiz-ai-mobile .quiz-ai-card-text,
.quiz-ai-mobile .quiz-ai-danger-text,
.quiz-ai-mobile .quiz-ai-tip-text,
.quiz-ai-mobile .ai-alert-text   { font-size:.83rem; line-height:1.74; }

/* ══════════════════════════════════════════
   SE → FORSTÅ → VELG — SITUATION LENS
   Quiet instructor guide shown before answering.
   Derived from question keywords — never reveals the answer.
══════════════════════════════════════════ */
.q-observe {
  padding:8px 11px; border-radius:10px; flex-shrink:0;
  background:rgba(255,153,51,.04);
  border:1px solid rgba(255,153,51,.10);
  display:flex; flex-direction:column; gap:5px;
  animation:aiBlockIn .22s ease both;
  /* collapse support */
  max-height:200px; overflow:hidden;
  transition: opacity .18s ease, max-height .22s ease, padding .22s ease, margin .22s ease;
}
/* Fold the lens the moment an answer is selected — feedback takes over */
.q-observe.answered {
  opacity:0; max-height:0; padding:0; margin:0; pointer-events:none;
}
.q-observe-row {
  display:flex; align-items:baseline; gap:7px;
  font-size:.73rem; line-height:1.55; color:var(--muted);
}
.q-observe-tag {
  font-size:.54rem; font-weight:900; text-transform:uppercase;
  letter-spacing:.7px; color:rgba(255,153,51,.60);
  flex-shrink:0; min-width:52px;
}

/* ══════════════════════════════════════════
   REVIEW MODE — Øv på feil
   Shows wrong questions one by one after a quiz.
   No answer options — observation and reflection only.
══════════════════════════════════════════ */
.rv-wrap   { display:flex; flex-direction:column; gap:13px; padding:2px 0; }
.rv-header { font-size:.60rem; font-weight:900; text-transform:uppercase; letter-spacing:.8px; color:var(--orange); }
.rv-question { font-size:.94rem; font-weight:700; color:var(--text); line-height:1.62; }
.rv-answer { padding:8px 12px; border-radius:9px; font-size:.82rem; font-weight:600; line-height:1.5; }
.rv-wrong  { background:rgba(239,68,68,.07); border:1px solid rgba(239,68,68,.18); color:#FCA5A5; }
.rv-right  { background:rgba(16,185,129,.07); border:1px solid rgba(16,185,129,.20); color:#6EE7B7; }
.rv-expl   { padding:10px 12px 10px 13px; border-radius:0 10px 10px 0; border-left:3px solid rgba(59,130,246,.38); background:rgba(59,130,246,.04); }
.rv-expl-lbl { font-size:.57rem; font-weight:900; text-transform:uppercase; letter-spacing:.8px; color:#93C5FD; margin-bottom:4px; }
.rv-expl-txt { font-size:.80rem; color:var(--muted); line-height:1.72; }
.rv-next   { margin-top:4px; width:100%; padding:12px 16px; border-radius:12px; background:var(--orange); color:#0F172A; font-weight:800; font-size:.88rem; border:none; cursor:pointer; }
.rv-next:active { opacity:.84; }
.rv-done   { display:flex; flex-direction:column; gap:12px; padding:4px 0; }
.rv-done-icon { font-size:1.8rem; opacity:.45; }
.rv-done-head { font-size:1.25rem; font-weight:900; color:var(--text); line-height:1.3; letter-spacing:-.2px; }
.rv-done-body { font-size:.86rem; color:var(--muted); line-height:1.78; }
.rv-done-btn  { align-self:flex-start; padding:11px 18px; background:rgba(255,255,255,.06); border:1.5px solid rgba(255,255,255,.12); color:var(--text); font-weight:700; font-size:.84rem; border-radius:12px; cursor:pointer; }
.rv-done-btn:hover { border-color:rgba(255,255,255,.22); }

/* ══════════════════════════════════════════
   HOME — READINESS CARD
   Shows last quiz result as a calm readiness signal.
══════════════════════════════════════════ */
.home-readiness {
  padding:13px 14px; border-radius:14px;
  background:#131B2E; border:1px solid rgba(255,255,255,.08);
  display:flex; align-items:center; gap:12px;
  cursor:pointer; transition:border-color .18s;
}
.home-readiness:hover { border-color:rgba(255,153,51,.22); }
.hr-dot {
  width:9px; height:9px; border-radius:50%; flex-shrink:0;
}
.hr-dot-good { background:var(--green);  box-shadow:0 0 8px rgba(16,185,129,.60); }
.hr-dot-ok   { background:var(--orange); box-shadow:0 0 8px rgba(255,153,51,.55); }
.hr-dot-bad  { background:#EF4444;       box-shadow:0 0 8px rgba(239,68,68,.50); }
.hr-main { flex:1; min-width:0; }
.hr-label { font-size:.62rem; font-weight:900; text-transform:uppercase; letter-spacing:.7px; color:var(--muted); margin-bottom:3px; }
.hr-status { font-size:.88rem; font-weight:800; color:var(--text); }
.hr-sub   { font-size:.72rem; color:var(--muted); margin-top:2px; }
.hr-pct   { font-size:1.40rem; font-weight:900; letter-spacing:-.5px; flex-shrink:0; }

/* ══════════════════════════════════════════
   VIDEO SUGGESTION CARD
   Contextual instructor video — one card max per surface.
   Surfaces: wrong-answer AI panel, sign detail panel, review mode.
   Feels like a quiet footnote from the instructor, not a media feed.
══════════════════════════════════════════ */
.vid-card {
  display:flex; align-items:center; gap:10px;
  padding:10px 11px; border-radius:11px;
  background:rgba(255,255,255,.03);
  border:1px solid rgba(255,255,255,.08);
  text-decoration:none; color:inherit;
  transition:border-color .18s; flex-shrink:0;
}
.vid-card:hover  { border-color:rgba(255,153,51,.30); }
.vid-card:active { opacity:.80; }
.vid-thumb-wrap  {
  flex-shrink:0; width:64px; height:40px; border-radius:7px;
  overflow:hidden; background:rgba(255,255,255,.06);
  display:flex; align-items:center; justify-content:center;
}
.vid-thumb    { width:100%; height:100%; object-fit:cover; display:block; }
.vid-info     { flex:1; min-width:0; }
.vid-lbl      {
  font-size:.55rem; font-weight:900; text-transform:uppercase;
  letter-spacing:.7px; color:var(--orange); margin-bottom:3px;
}
.vid-title    {
  font-size:.78rem; font-weight:700; color:var(--text); line-height:1.38;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;
}
.vid-dur      { font-size:.63rem; color:var(--muted); margin-top:2px; }
.vid-arrow    { font-size:.90rem; color:var(--orange); flex-shrink:0; opacity:.65; }
/* Wrapper — adds section label above the card */
.vid-section  { display:flex; flex-direction:column; gap:6px; }
.vid-sec-lbl  {
  font-size:.57rem; font-weight:900; text-transform:uppercase;
  letter-spacing:.8px; color:var(--muted);
}

/* ══════════════════════════════════════════
   SIGNS SCREEN
══════════════════════════════════════════ */
#screenSigns { padding:0; background:#0B1226; }
.signs-header {
  padding:14px 16px 10px; flex-shrink:0;
  display:flex; align-items:center; gap:10px;
}
.signs-count {
  font-size:.78rem; color:var(--muted); font-weight:600;
}
.signs-scroll {
  flex:1; overflow-y:auto; overflow-x:hidden;
  padding:0 12px 16px;
  -webkit-overflow-scrolling:touch;
}
.signs-scroll::-webkit-scrollbar { width:4px; }
.signs-scroll::-webkit-scrollbar-track { background:transparent; }
.signs-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.12); border-radius:2px; }
.signs-grid {
  display:grid;
  /* auto-fit responds to the container width, not the viewport —
     minmax(100px,1fr) gives 3 cols in the 390 px shell.
     No viewport media queries needed. */
  grid-template-columns:repeat(auto-fit, minmax(100px,1fr));
  gap:10px;
}
/* old plain label replaced by rich group header */
.sg-header {
  display:flex; align-items:center; gap:10px;
  padding:20px 4px 8px;
}
.sg-header:first-child { padding-top:8px; }
.sg-dot {
  width:10px; height:10px; border-radius:50%; flex-shrink:0;
  box-shadow:0 0 10px var(--sg-color,rgba(255,153,51,.5));
  background:var(--sg-color,var(--orange));
}
.sg-info { flex:1; min-width:0; }
.sg-name {
  font-size:.80rem; font-weight:800; color:var(--text); line-height:1.25;
}
.sg-desc {
  font-size:.63rem; color:var(--muted); margin-top:2px; line-height:1.4;
}
.sg-count {
  font-size:.58rem; font-weight:800; text-transform:uppercase;
  letter-spacing:.6px; padding:3px 8px; border-radius:20px;
  background:rgba(255,255,255,.05); color:var(--muted);
  flex-shrink:0; border:1px solid rgba(255,255,255,.07);
}
/* Intro bar at top of signs scroll */
.signs-intro {
  margin:8px 0 4px; padding:11px 14px;
  background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.06);
  border-radius:12px;
  font-size:.74rem; color:var(--muted); line-height:1.6;
}
.sign-card {
  background:#131B2E; border:1.5px solid rgba(255,255,255,.10);
  border-radius:14px; padding:10px 8px;
  display:flex; flex-direction:column; align-items:center; gap:8px;
  cursor:pointer; transition:border-color .18s;
}
.sign-card:hover  { border-color:rgba(255,153,51,.50); }
.sign-card:active { opacity:.80; }
.sign-img-wrap {
  width:100%; aspect-ratio:1/1; flex-shrink:0;
  border-radius:8px; overflow:hidden;
  background:rgba(255,255,255,.04); border:1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
}
.sign-img { width:86%; height:86%; object-fit:contain; display:block; }
.sign-ans {
  width:100%; padding:4px 6px;
  font-size:.60rem; color:var(--muted); font-weight:600;
  text-align:center; line-height:1.4;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
  overflow:hidden;
}

/* ══════════════════════════════════════════
   SIGN DETAIL PANEL — AI traffic sign school
   Bottom sheet mobile · Right panel desktop
══════════════════════════════════════════ */
.sign-panel-backdrop {
  position:fixed; inset:0; z-index:400;
  background:rgba(0,0,0,.68);
  backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px);
  opacity:0; pointer-events:none; transition:opacity .28s ease;
}
.sign-panel-backdrop.open { opacity:1; pointer-events:all; }

.sign-panel {
  position:fixed; left:0; right:0; bottom:0; z-index:401;
  background:#0B1120; border-radius:24px 24px 0 0;
  max-height:92vh;
  display:flex; flex-direction:column;
  transform:translateY(102%);
  transition:transform .34s cubic-bezier(.32,0,.18,1);
  overflow:hidden;
  box-shadow:0 -8px 40px rgba(0,0,0,.55);
}
.sign-panel.open { transform:translateY(0); }

@media (min-width:700px) {
  .sign-panel {
    left:auto; top:0; bottom:0; width:min(900px, calc(100vw - 44px));
    border-radius:0; max-height:100vh;
    transform:translateX(102%);
    box-shadow:-8px 0 40px rgba(0,0,0,.45);
  }
  .sign-panel.open { transform:translateX(0); }
}

/* Drag handle — mobile only */
.sp-handle {
  width:36px; height:4px; border-radius:2px;
  background:rgba(255,255,255,.14);
  margin:10px auto 0; flex-shrink:0;
}
@media (min-width:700px) { .sp-handle { display:none; } }

/* ── Header ── */
.sp-header {
  flex-shrink:0; position:relative;
  display:flex; flex-direction:column; align-items:center;
  background:#080F1E; padding:10px 52px 18px;
  border-bottom:1px solid rgba(255,255,255,.07);
}
.sp-close {
  position:absolute; top:14px; right:14px;
  width:30px; height:30px; border-radius:50%;
  border:none; background:rgba(255,255,255,.08);
  color:var(--muted); font-size:12px; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
}
.sp-close:hover { background:rgba(255,255,255,.14); color:var(--text); }

.sp-img-wrap {
  width:128px; height:128px; border-radius:20px;
  background:#131B2E;
  border:1.5px solid rgba(255,255,255,.10);
  box-shadow:0 8px 28px rgba(0,0,0,.45);
  display:flex; align-items:center; justify-content:center;
  margin:18px 0 14px; flex-shrink:0;
}
.sp-img { max-width:96px; max-height:96px; object-fit:contain; display:block; }

.sp-name {
  font-size:1.05rem; font-weight:900; text-align:center;
  color:var(--text); letter-spacing:-.25px; line-height:1.28;
}
.sp-group-label {
  font-size:.60rem; color:var(--orange); margin-top:6px;
  font-weight:800; text-align:center;
  text-transform:uppercase; letter-spacing:.9px;
}

/* ── Language tabs ── */
.sp-lang-tabs {
  display:flex; flex-shrink:0;
  border-bottom:1px solid rgba(255,255,255,.07);
  background:#080F1E;
}
.sp-lang-tab {
  flex:1; padding:11px 4px;
  font-size:.75rem; font-weight:700; color:var(--muted);
  background:none; border:none; border-bottom:2px solid transparent;
  cursor:pointer; transition:color .18s, border-color .18s;
}
.sp-lang-tab.active { color:var(--orange); border-bottom-color:var(--orange); }

/* ── Scrollable body ── */
.sp-body {
  flex:1; overflow-y:auto; overflow-x:hidden;
  padding:14px 14px 10px;
  display:flex; flex-direction:column; gap:9px;
  -webkit-overflow-scrolling:touch;
}
.sp-body::-webkit-scrollbar { width:2px; }
.sp-body::-webkit-scrollbar-thumb { background:rgba(255,255,255,.08); border-radius:2px; }

.sp-learning-layout { display:flex; flex-direction:column; gap:12px; }
.sp-related-surface,
.sp-main-surface {
  min-width:0;
  display:flex; flex-direction:column; gap:10px;
}
@media (min-width:700px) {
  .sp-learning-layout {
    display:grid;
    grid-template-columns:minmax(230px,.82fr) minmax(340px,1.18fr);
    gap:14px;
    align-items:start;
  }
  .sp-related-surface {
    position:sticky; top:0;
    max-height:calc(100vh - 212px);
    overflow-y:auto;
    padding-right:2px;
  }
  .sp-related-surface::-webkit-scrollbar { width:2px; }
  .sp-related-surface::-webkit-scrollbar-thumb { background:rgba(255,255,255,.08); border-radius:2px; }
}
.sp-side-section {
  background:rgba(255,255,255,.035);
  border:1px solid rgba(255,255,255,.075);
  border-radius:14px;
  padding:12px;
}
.sp-side-title {
  font-size:.62rem; font-weight:900; text-transform:uppercase;
  letter-spacing:.8px; color:var(--muted); margin-bottom:9px;
}
.sp-related-grid {
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:8px;
}
@media (max-width:699px) {
  .sp-related-grid {
    display:flex; overflow-x:auto; gap:8px; padding-bottom:2px;
    -webkit-overflow-scrolling:touch;
  }
  .sp-related-card { flex:0 0 118px; }
}
.sp-related-card {
  border:none;
  background:rgba(255,255,255,.045);
  border:1px solid rgba(255,255,255,.08);
  color:var(--text);
  border-radius:12px;
  padding:8px;
  cursor:pointer;
  display:flex; flex-direction:column; gap:6px;
  text-align:left;
}
.sp-related-card:hover { border-color:rgba(255,153,51,.30); background:rgba(255,153,51,.055); }
.sp-related-img {
  height:54px;
  display:flex; align-items:center; justify-content:center;
  background:rgba(0,0,0,.16);
  border-radius:9px;
}
.sp-related-img img { max-width:100%; max-height:50px; object-fit:contain; display:block; }
.sp-related-code { font-size:.62rem; color:var(--orange); font-weight:900; }
.sp-related-name { font-size:.70rem; line-height:1.25; font-weight:800; color:var(--text); }
.sp-related-empty { font-size:.76rem; color:var(--muted); line-height:1.55; }

/* ── Content cards — each type has its own identity ── */
.sp-card {
  border-radius:0 13px 13px 0;
  padding:12px 14px 12px 13px;
  display:flex; gap:11px; align-items:flex-start;
}
.sp-card-icon {
  font-size:1.05rem; flex-shrink:0;
  line-height:1.2; margin-top:1px;
}
.sp-card-inner { flex:1; min-width:0; }
.sp-card-label {
  font-size:.58rem; font-weight:900; text-transform:uppercase;
  letter-spacing:1px; margin-bottom:6px;
}
.sp-card-text { font-size:.84rem; line-height:1.80; color:var(--text); }

/* Explanation — blue */
.sp-card-explanation { background:rgba(59,130,246,.05); border-left:3px solid rgba(59,130,246,.45); }
.sp-card-explanation .sp-card-label { color:#93C5FD; }

/* Why dangerous — red */
.sp-card-danger { background:rgba(239,68,68,.05); border-left:3px solid rgba(239,68,68,.45); }
.sp-card-danger .sp-card-label { color:#FCA5A5; }

/* Common mistake — amber */
.sp-card-mistake { background:rgba(251,146,60,.05); border-left:3px solid rgba(251,146,60,.45); }
.sp-card-mistake .sp-card-label { color:#FCD4A0; }

/* In traffic — teal */
.sp-card-scenario { background:rgba(16,185,129,.05); border-left:3px solid rgba(16,185,129,.45); }
.sp-card-scenario .sp-card-label { color:#6EE7B7; }

/* Exam tip — purple */
.sp-card-exam { background:rgba(168,85,247,.05); border-left:3px solid rgba(168,85,247,.45); }
.sp-card-exam .sp-card-label { color:#C4B5FD; }

/* Memory rule — orange */
.sp-card-memory { background:rgba(255,153,51,.05); border-left:3px solid rgba(255,153,51,.45); }
.sp-card-memory .sp-card-label { color:var(--orange); }

/* Empty state */
.sp-empty {
  padding:28px 16px; text-align:center;
  color:var(--muted); font-size:.82rem; line-height:1.7; font-style:italic;
}

/* ── Action buttons ── */
.sp-actions {
  flex-shrink:0;
  padding:12px 14px 22px;
  border-top:1px solid rgba(255,255,255,.07);
  background:#080F1E;
  display:flex; flex-direction:column; gap:8px;
}
/* Primary — full width, orange */
.sp-btn-primary {
  width:100%; padding:13px 16px; border-radius:13px;
  background:var(--orange); color:#0F172A;
  font-size:.90rem; font-weight:800;
  border:none; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:7px;
}
.sp-btn-primary:active { opacity:.84; }
/* Secondary row — 3 equal */
.sp-actions-row { display:flex; gap:8px; }
.sp-btn-sm {
  flex:1; padding:10px 6px; border-radius:12px;
  font-size:.70rem; font-weight:700;
  border:none; cursor:pointer;
  display:flex; flex-direction:column; align-items:center; gap:4px;
}
.sp-btn-sm span { font-size:.64rem; }
.sp-btn-sm:active { opacity:.72; }
.sp-btn-sm-audio { background:rgba(255,153,51,.10); color:var(--orange); border:1px solid rgba(255,153,51,.24); }
.sp-btn-sm-ai    { background:rgba(139,92,246,.10); color:#A78BFA;      border:1px solid rgba(139,92,246,.24); }
.sp-btn-sm-bm    { background:rgba(255,255,255,.05); color:var(--muted); border:1px solid rgba(255,255,255,.10); }
.sp-btn-sm-bm.saved { color:var(--orange); border-color:rgba(255,153,51,.35); background:rgba(255,153,51,.07); }

/* ══════════════════════════════════════════
   BOOKMARKS SCREEN
══════════════════════════════════════════ */
#screenBookmarks { padding:0; background:#0B1226; }
.bm-header { padding:14px 16px 10px; flex-shrink:0; }
.bm-scroll {
  flex:1; min-height:0;                   /* lets flex child shrink in column parent */
  overflow-x:auto; overflow-y:hidden;
  display:flex; gap:14px;
  padding:0 16px 16px;
  -webkit-overflow-scrolling:touch;
  scroll-snap-type:x proximity;          /* snap to card edges */
  touch-action:pan-x;                    /* native horizontal swipe on touch */
  align-items:flex-start;
  scrollbar-width:none;                  /* Firefox — hide scrollbar */
}
.bm-scroll::-webkit-scrollbar { display:none; }   /* Chrome/Safari — hide scrollbar */

.bm-card {
  flex:0 0 calc(100% - 48px);            /* responsive 82%-ish width; no flex-shrink */
  max-width:320px;
  scroll-snap-align:start;              /* snap each card into view */
  background:#131B2E; border:1.5px solid rgba(255,255,255,.10);
  border-radius:16px; padding:14px;
  display:flex; flex-direction:column; gap:10px;
  height:calc(100% - 16px);
  position:relative; overflow:hidden;
}
.bm-card-img-wrap {
  width:100%; border-radius:10px; overflow:hidden;
  background:rgba(255,255,255,.04); border:1px solid var(--border);
  height:140px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
}
.bm-card-img { width:100%; height:100%; object-fit:contain; display:block; }
.bm-card-q {
  font-size:.82rem; font-weight:700; line-height:1.5;
  flex:1; overflow:hidden;
  display:-webkit-box; -webkit-line-clamp:4; -webkit-box-orient:vertical;
}
.bm-card-ans {
  padding:8px 10px; border-radius:9px;
  background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.25);
  font-size:.76rem; color:#6EE7B7; font-weight:700;
  flex-shrink:0; line-height:1.4;
}
.bm-card-remove {
  position:absolute; top:10px; right:10px;
  width:28px; height:28px; border-radius:50%;
  border:none; background:rgba(239,68,68,.15);
  color:#EF4444; font-size:13px; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
  transition:all .2s;
}
.bm-card-remove:hover { background:rgba(239,68,68,.3); }

/* ══════════════════════════════════════════
   SETTINGS SCREEN — mobile-app style
══════════════════════════════════════════ */
#screenSettings {
  padding:0;
  overflow-y:auto; overflow-x:hidden;
  -webkit-overflow-scrolling:touch;
  background:#0B1226;
}
#screenSettings::-webkit-scrollbar { width:4px; }
#screenSettings::-webkit-scrollbar-track { background:transparent; }
#screenSettings::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:2px; }

.settings-inner {
  display:flex; flex-direction:column; gap:0; padding-bottom:24px;
}

/* Profile hero at top — solid so the flag background doesn't bleed through */
.settings-profile-hero {
  padding:24px 20px 18px;
  display:flex; flex-direction:column; align-items:center; gap:8px;
  background:var(--bg2);
  border-bottom:1px solid rgba(255,255,255,.08);
  margin-bottom:8px;
}
.settings-avatar {
  width:72px; height:72px; border-radius:50%;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  display:flex; align-items:center; justify-content:center;
  font-size:2rem; font-weight:900; color:#0F172A;
  box-shadow:0 8px 24px rgba(255,153,51,.35);
  border:3px solid rgba(255,153,51,.4);
  flex-shrink:0;
}
.settings-profile-name {
  font-size:1.05rem; font-weight:800; text-align:center; line-height:1.2;
}
.settings-profile-email {
  font-size:.78rem; color:var(--muted); text-align:center;
}
.settings-profile-badges { display:flex; gap:6px; justify-content:center; flex-wrap:wrap; }

.settings-section { flex-shrink:0; padding:0 16px; margin-bottom:6px; }
.settings-label {
  font-size:.65rem; font-weight:800; color:var(--muted);
  letter-spacing:.9px; text-transform:uppercase;
  margin-bottom:7px; margin-top:14px; padding:0 4px;
}
.settings-card {
  background:#131B2E; border:1px solid rgba(255,255,255,.10);
  border-radius:16px; overflow:hidden;
}
.settings-row {
  display:flex; align-items:center; gap:14px;
  padding:14px 16px;
  border-bottom:1px solid var(--border);
  transition:background .15s;
}
.settings-row:last-child { border-bottom:none; }
.settings-row:active { background:rgba(255,255,255,.03); }

/* Icon circle — like mobile app */
.sr-icon {
  width:38px; height:38px; border-radius:11px;
  display:flex; align-items:center; justify-content:center;
  font-size:1.15rem; flex-shrink:0;
  background:rgba(255,153,51,.13); border:1px solid rgba(255,153,51,.2);
}
.sr-icon.blue   { background:rgba(59,130,246,.12); border-color:rgba(59,130,246,.2); }
.sr-icon.green  { background:rgba(16,185,129,.12); border-color:rgba(16,185,129,.2); }
.sr-icon.purple { background:rgba(139,92,246,.12); border-color:rgba(139,92,246,.2); }
.sr-icon.gray   { background:rgba(148,163,184,.1); border-color:rgba(148,163,184,.18); }

.sr-label { flex:1; min-width:0; }
.sr-label .sr-title { font-size:.9rem; font-weight:700; }
.sr-label .sr-sub  { font-size:.73rem; color:var(--muted); margin-top:2px; line-height:1.4; }
.account-info { display:flex; flex-direction:column; gap:3px; }
.account-email { font-size:.9rem; font-weight:700; }

.toggle { position:relative; width:44px; height:24px; flex-shrink:0; }
.toggle input { opacity:0; width:0; height:0; position:absolute; }
.toggle-slider {
  position:absolute; inset:0; border-radius:12px;
  background:rgba(255,255,255,.12); cursor:pointer; transition:.3s;
}
[data-theme="light"] .toggle-slider { background:rgba(0,0,0,.12); }
.toggle-slider::before {
  content:''; position:absolute;
  width:18px; height:18px; border-radius:50%;
  left:3px; bottom:3px; background:#fff; transition:.3s;
  box-shadow:0 2px 4px rgba(0,0,0,.3);
}
.toggle input:checked + .toggle-slider { background:var(--orange); }
.toggle input:checked + .toggle-slider::before { transform:translateX(20px); }

.seg-ctrl {
  display:flex; gap:3px;
  background:rgba(255,255,255,.06); border-radius:9px; padding:3px;
}
[data-theme="light"] .seg-ctrl { background:rgba(0,0,0,.06); }
.seg-btn {
  padding:5px 10px; border-radius:7px;
  border:none; background:transparent;
  color:var(--muted); font-size:.74rem; font-weight:700;
  cursor:pointer; transition:all .2s;
}
.seg-btn.active { background:var(--orange); color:#0F172A; }

/* Circular flag buttons */
.lang-btns { display:flex; gap:10px; }
.lang-btn {
  width:52px; height:52px; border-radius:50%;
  border:2.5px solid var(--border); background:transparent;
  cursor:pointer; transition:all .2s;
  position:relative; overflow:hidden; padding:0; flex-shrink:0;
}
.lang-btn.active { border-color:var(--orange); box-shadow:0 0 0 3px rgba(255,153,51,.3); transform:scale(1.1); }
.lang-btn:hover:not(.active) { border-color:rgba(255,255,255,.4); transform:scale(1.06); }
.lang-btn .cflag { position:absolute; inset:0; display:block; }
.lang-btn .cflag svg { width:100%; height:100%; display:block; }

.account-info { display:flex; flex-direction:column; gap:3px; }
.account-email { font-size:.87rem; font-weight:700; }
.account-badges { display:flex; gap:5px; margin-top:3px; flex-wrap:wrap; }

.logout-btn {
  width:calc(100% - 32px); margin:8px 16px 0;
  padding:14px;
  background:rgba(239,68,68,.1); border:1.5px solid rgba(239,68,68,.22);
  color:#EF4444; font-weight:800; font-size:.92rem;
  border-radius:14px; cursor:pointer;
  transition:all .2s; flex-shrink:0;
  box-shadow:0 2px 10px rgba(239,68,68,.08);
}
.logout-btn:hover { background:rgba(239,68,68,.18); border-color:rgba(239,68,68,.4); }
.logout-btn:active { transform:scale(.98); }

/* ══════════════════════════════════════════
   HISTORY SCREEN
══════════════════════════════════════════ */
#screenHistory { padding:0; background:#0B1226; }
.hist-header { padding:14px 16px 10px; flex-shrink:0; }
.hist-scroll {
  flex:1; min-height:0;
  overflow-y:auto; overflow-x:hidden;
  padding:0 14px 16px;
  -webkit-overflow-scrolling:touch;
  display:flex; flex-direction:column; gap:10px;
}
.hist-scroll::-webkit-scrollbar { width:4px; }
.hist-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.10); border-radius:2px; }

/* ── History card ── */
.hist-card {
  background:#131B2E; border:1px solid rgba(255,255,255,.09);
  border-radius:16px; padding:14px 14px 12px;
  display:flex; flex-direction:column; gap:10px;
  cursor:pointer; transition:border-color .18s; flex-shrink:0;
}
.hist-card:hover  { border-color:rgba(255,153,51,.30); }
.hist-card:active { opacity:.88; }

.hist-card-top {
  display:flex; align-items:flex-start; justify-content:space-between; gap:8px;
}
.hist-mode { font-size:.86rem; font-weight:800; color:var(--text); line-height:1.3; }
.hist-mode-sub { font-size:.72rem; color:var(--muted); margin-top:2px; font-weight:600; }

/* Status badge */
.hist-badge {
  font-size:.58rem; font-weight:900; text-transform:uppercase;
  letter-spacing:.6px; padding:3px 9px; border-radius:20px; flex-shrink:0; margin-top:2px;
}
.hist-badge-good { background:rgba(16,185,129,.12); color:var(--green);  border:1px solid rgba(16,185,129,.26); }
.hist-badge-ok   { background:rgba(255,153,51,.10);  color:var(--orange); border:1px solid rgba(255,153,51,.26); }
.hist-badge-bad  { background:rgba(239,68,68,.08);   color:#FCA5A5;       border:1px solid rgba(239,68,68,.22); }

/* Score + progress bar */
.hist-score-row { display:flex; align-items:center; gap:12px; }
.hist-pct { font-size:1.70rem; font-weight:900; color:var(--text); letter-spacing:-.5px; line-height:1; flex-shrink:0; min-width:52px; }
.hist-bar-wrap { flex:1; height:5px; background:rgba(255,255,255,.08); border-radius:3px; overflow:hidden; }
.hist-bar-fill  { height:100%; border-radius:3px; }

/* Stats row */
.hist-stats-row { display:flex; align-items:center; gap:6px; flex-wrap:wrap; font-size:.74rem; }
.hist-stat-good { color:var(--green);  font-weight:700; }
.hist-stat-bad  { color:#FCA5A5;       font-weight:700; }
.hist-stat-tot  { color:var(--muted); }
.hist-stat-sep  { color:rgba(255,255,255,.16); }

/* Footer: date + actions */
.hist-card-footer { display:flex; align-items:center; justify-content:space-between; gap:8px; }
.hist-date-new    { font-size:.70rem; color:var(--muted); }
.hist-card-actions { display:flex; gap:6px; }
.hist-btn {
  padding:6px 11px; border-radius:8px; font-size:.72rem; font-weight:700;
  border:none; cursor:pointer;
}
.hist-btn:active { opacity:.75; }
.hist-btn-sec { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.10); color:var(--text); }
.hist-btn-pri { background:rgba(255,153,51,.12);  border:1px solid rgba(255,153,51,.25);  color:var(--orange); }

/* ══════════════════════════════════════════
   HISTORY DETAIL PANEL
   Bottom sheet mobile · Right panel desktop
══════════════════════════════════════════ */
.hist-panel-backdrop {
  position:fixed; inset:0; z-index:410;
  background:rgba(0,0,0,.70); backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px);
  opacity:0; pointer-events:none; transition:opacity .28s ease;
}
.hist-panel-backdrop.open { opacity:1; pointer-events:all; }

.hist-panel {
  position:fixed; left:0; right:0; bottom:0; z-index:411;
  background:#0B1120; border-radius:24px 24px 0 0; max-height:92vh;
  display:flex; flex-direction:column;
  transform:translateY(102%); transition:transform .34s cubic-bezier(.32,0,.18,1);
  overflow:hidden; box-shadow:0 -8px 40px rgba(0,0,0,.55);
}
.hist-panel.open { transform:translateY(0); }
@media (min-width:700px) {
  .hist-panel { left:auto; top:0; bottom:0; width:420px; border-radius:0; max-height:100vh; transform:translateX(102%); box-shadow:-8px 0 40px rgba(0,0,0,.45); }
  .hist-panel.open { transform:translateX(0); }
}
.hist-panel-handle {
  width:36px; height:4px; border-radius:2px;
  background:rgba(255,255,255,.14); margin:10px auto 0; flex-shrink:0;
}
@media (min-width:700px) { .hist-panel-handle { display:none; } }

/* Panel header */
.hp-header {
  flex-shrink:0; position:relative;
  padding:14px 52px 16px 18px;
  background:#080F1E; border-bottom:1px solid rgba(255,255,255,.07);
}
.hp-close {
  position:absolute; top:14px; right:14px;
  width:30px; height:30px; border-radius:50%;
  border:none; background:rgba(255,255,255,.08); color:var(--muted); font-size:12px; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
}
.hp-close:hover { background:rgba(255,255,255,.14); color:var(--text); }
.hp-mode-lbl { font-size:.64rem; font-weight:900; text-transform:uppercase; letter-spacing:.7px; color:var(--muted); margin-bottom:8px; }
.hp-score-big { font-size:2.6rem; font-weight:900; color:var(--text); letter-spacing:-.6px; line-height:1; }
.hp-score-sub { font-size:.80rem; color:var(--muted); margin-top:5px; }
.hp-badge {
  display:inline-flex; align-items:center; gap:5px; margin-top:10px;
  padding:4px 12px; border-radius:20px; font-size:.68rem; font-weight:800;
}
.hp-badge-good { background:rgba(16,185,129,.12); color:var(--green);  border:1px solid rgba(16,185,129,.28); }
.hp-badge-ok   { background:rgba(255,153,51,.10);  color:var(--orange); border:1px solid rgba(255,153,51,.28); }
.hp-badge-bad  { background:rgba(239,68,68,.08);   color:#FCA5A5;       border:1px solid rgba(239,68,68,.25); }

/* Stats grid */
.hp-stats {
  display:flex; margin-top:14px;
  border:1px solid rgba(255,255,255,.07); border-radius:12px; overflow:hidden;
}
.hp-stat { flex:1; padding:10px 6px; text-align:center; border-right:1px solid rgba(255,255,255,.07); }
.hp-stat:last-child { border-right:none; }
.hp-stat-num { font-size:1.2rem; font-weight:900; color:var(--text); }
.hp-stat-num.good { color:var(--green); }
.hp-stat-num.bad  { color:#FCA5A5; }
.hp-stat-lbl { font-size:.55rem; color:var(--muted); font-weight:700; text-transform:uppercase; letter-spacing:.5px; margin-top:2px; }

/* Scrollable body */
.hp-body { flex:1; overflow-y:auto; padding:14px 14px 8px; display:flex; flex-direction:column; gap:10px; -webkit-overflow-scrolling:touch; }
.hp-body::-webkit-scrollbar { width:2px; }
.hp-body::-webkit-scrollbar-thumb { background:rgba(255,255,255,.08); border-radius:2px; }

.hp-section-label { font-size:.60rem; font-weight:900; text-transform:uppercase; letter-spacing:.9px; color:var(--muted); padding:4px 0 2px; }

/* Wrong question card */
.hp-q-card { border-radius:0 13px 13px 0; padding:12px 14px 12px 13px; background:rgba(239,68,68,.04); border-left:3px solid rgba(239,68,68,.38); display:flex; flex-direction:column; gap:7px; }
.hp-q-num  { font-size:.58rem; font-weight:900; text-transform:uppercase; letter-spacing:.8px; color:#FCA5A5; }
.hp-q-text { font-size:.84rem; color:var(--text); font-weight:600; line-height:1.55; }
.hp-q-ans { font-size:.78rem; padding:5px 10px; border-radius:8px; line-height:1.4; }
.hp-q-ans-wrong { background:rgba(239,68,68,.08); color:#FCA5A5; border:1px solid rgba(239,68,68,.18); }
.hp-q-ans-right { background:rgba(16,185,129,.08); color:#6EE7B7; border:1px solid rgba(16,185,129,.20); }
.hp-q-expl-label { font-size:.56rem; font-weight:900; text-transform:uppercase; letter-spacing:.8px; color:var(--muted); margin-bottom:3px; }
.hp-q-expl { font-size:.78rem; color:var(--muted); line-height:1.68; }

.hp-no-data { padding:28px 16px; text-align:center; color:var(--muted); font-size:.84rem; line-height:1.75; }

/* Panel actions */
.hp-actions { flex-shrink:0; padding:12px 14px 22px; border-top:1px solid rgba(255,255,255,.07); background:#080F1E; display:flex; flex-direction:column; gap:8px; }
.hp-btn-pri { width:100%; padding:13px 16px; border-radius:13px; background:var(--orange); color:#0F172A; font-size:.90rem; font-weight:800; border:none; cursor:pointer; }
.hp-btn-pri:active { opacity:.84; }
.hp-btn-sec { width:100%; padding:12px 16px; border-radius:13px; background:rgba(255,255,255,.05); color:var(--muted); font-size:.86rem; font-weight:700; border:1.5px solid rgba(255,255,255,.10); cursor:pointer; }
.hp-btn-sec:hover { border-color:rgba(255,255,255,.22); color:var(--text); }

/* ══════════════════════════════════════════
   END SCREEN
══════════════════════════════════════════ */
#screenEnd {
  align-items:center; justify-content:center;
  padding:40px 24px; background:#0B1226;
}
.end-wrap { text-align:left; max-width:340px; width:100%; }
.end-score-quiet {
  font-size:.78rem; color:var(--muted); font-weight:600;
  margin-bottom:22px; letter-spacing:.15px;
}
.end-heading {
  font-size:1.55rem; font-weight:900; color:var(--text);
  line-height:1.25; margin-bottom:14px; letter-spacing:-.3px;
}
.end-body {
  font-size:.88rem; color:var(--muted); line-height:1.78;
  margin-bottom:24px;
}
.end-focus {
  padding:12px 16px 12px 14px;
  background:rgba(255,153,51,.05);
  border-left:3px solid rgba(255,153,51,.40);
  border-radius:0 10px 10px 0;
  margin-bottom:24px;
}
.end-focus-label {
  font-size:.60rem; font-weight:900; text-transform:uppercase;
  letter-spacing:1px; color:var(--orange); margin-bottom:5px;
}
.end-focus-topic { font-size:.86rem; color:var(--text); font-weight:700; }
.end-btns  { display:flex; flex-direction:column; gap:9px; }
.end-btn-pri {
  padding:13px;
  background:var(--orange);
  color:#0F172A; font-weight:800; font-size:.92rem;
  border:none; border-radius:12px; cursor:pointer;
}
.end-btn-pri:active { opacity:.85; }
.end-btn-sec {
  padding:12px;
  background:transparent; border:1.5px solid rgba(255,255,255,.10);
  color:var(--muted); font-weight:600; font-size:.87rem;
  border-radius:12px; cursor:pointer;
}
.end-btn-sec:hover { border-color:rgba(255,255,255,.22); color:var(--text); }

/* ══════════════════════════════════════════
   LOADING & UTILS
══════════════════════════════════════════ */
.loading-wrap {
  display:flex; align-items:center; justify-content:center;
  padding:48px 20px; flex-direction:column; gap:12px;
  width:100%;
}
.spinner {
  width:36px; height:36px;
  border:3px solid var(--border); border-top-color:var(--orange);
  border-radius:50%; animation:spin .75s linear infinite;
}
@keyframes spin { to { transform:rotate(360deg); } }
.empty-state { text-align:center; padding:40px 20px; color:var(--muted); width:100%; }
.empty-state .es-icon { font-size:2.2rem; margin-bottom:9px; }
.empty-state p { font-size:.85rem; line-height:1.6; }

/* Sequential flag pulse in top bar — TH then NO then EN */
@keyframes topflagpulse {
  0%,100% { transform:scale(1);   box-shadow:none; border-color:var(--border); }
  15%,50% { transform:scale(1.45);box-shadow:0 0 0 5px rgba(255,153,51,.75),0 0 18px rgba(255,153,51,.55); border-color:var(--orange); }
  80%     { transform:scale(1);   box-shadow:none; border-color:var(--border); }
}
#topLangTH:not(.active){ animation:topflagpulse 6s ease-in-out infinite 0s; }
#topLangNO:not(.active){ animation:topflagpulse 6s ease-in-out infinite 2s; }
#topLangEN:not(.active){ animation:topflagpulse 6s ease-in-out infinite 4s; }
.lang-btn.active{ animation:none!important; }

/* ══════════════════════════════════════════
   STUDIEBOK SCREEN
══════════════════════════════════════════ */
#screenStudybook { padding:0; background:#0B1226; }
/* ══ STUDIEBOK — BOK-STIL ══ */
.sb-topbar {
  flex-shrink:0; padding:10px 14px 8px;
  display:flex; align-items:center; gap:10px;
  background:rgba(11,18,38,.6); backdrop-filter:blur(10px);
  border-bottom:1px solid var(--border);
}
[data-theme="light"] .sb-topbar { background:rgba(241,245,249,.9); }
.sb-search-wrap { flex:1; position:relative; }
.sb-search-wrap input {
  width:100%; padding:8px 14px 8px 36px;
  border-radius:20px; border:1px solid var(--border);
  background:rgba(255,255,255,.07); color:var(--text);
  font-size:.82rem; outline:none;
  transition:border-color .2s;
}
[data-theme="light"] .sb-search-wrap input { background:rgba(0,0,0,.06); }
.sb-search-wrap input:focus { border-color:var(--orange); }
.sb-search-wrap::before {
  content:'🔍'; position:absolute; left:11px; top:50%;
  transform:translateY(-50%); font-size:.75rem; pointer-events:none;
}
.sb-search-results {
  position:absolute; top:100%; left:0; right:0; z-index:200;
  background:var(--bg2); border:1px solid var(--border);
  border-radius:14px; overflow:hidden;
  box-shadow:0 8px 32px rgba(0,0,0,.4);
  max-height:260px; overflow-y:auto;
  margin:4px 14px 0;
}
.sb-result-item {
  padding:10px 14px; cursor:pointer; display:flex; align-items:center; gap:10px;
  border-bottom:1px solid var(--border); font-size:.82rem;
  transition:background .15s;
}
.sb-result-item:last-child { border-bottom:none; }
.sb-result-item:hover { background:rgba(255,153,51,.1); }
.sb-result-icon { font-size:1.1rem; flex-shrink:0; }
.sb-result-title { color:var(--text); font-weight:600; }
.sb-result-preview { color:var(--muted); font-size:.74rem; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:240px; }

/* Book reader */
.sb-reader {
  flex:1; overflow-y:auto; overflow-x:hidden;
  -webkit-overflow-scrolling:touch;
  padding:16px 16px 8px;
}
.sb-reader::-webkit-scrollbar { width:3px; }
.sb-reader::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:2px; }
.sb-page {
  background:#131B2E; border:1px solid rgba(255,255,255,.10);
  border-radius:20px; padding:20px 18px 22px; min-height:100px;
}
[data-theme="light"] .sb-page { background:rgba(255,255,255,.75); border-color:rgba(0,0,0,.1); }
.sb-page-icon {
  width:52px; height:52px; border-radius:14px; margin:0 auto 12px;
  display:flex; align-items:center; justify-content:center;
  font-size:1.6rem;
  background:rgba(255,153,51,.13); border:1.5px solid rgba(255,153,51,.25);
}
.sb-page-title {
  text-align:center; font-size:1rem; font-weight:900;
  color:var(--orange); margin-bottom:16px; line-height:1.3;
}
.sb-page-body { font-size:.82rem; line-height:1.8; color:var(--text); }
.sb-page-body p { margin-top:10px; }
.sb-page-body strong { color:var(--orange); font-weight:800; }
.sb-page-body ul, .sb-page-body ol {
  margin:8px 0 0 0; padding-left:18px; line-height:1.8;
}
.sb-page-body li { margin-bottom:3px; }
.sb-page-body .study-tip {
  margin-top:14px; padding:10px 14px;
  background:rgba(255,153,51,.08); border:1px solid rgba(255,153,51,.2);
  border-radius:10px; font-size:.77rem; color:var(--muted); line-height:1.65;
}
.sb-page-body .study-tip strong { color:var(--orange); }
.study-img { max-width:100%; border-radius:8px; margin-bottom:12px; }

/* Nav bar */
.sb-nav {
  flex-shrink:0; display:flex; align-items:center; justify-content:space-between;
  padding:10px 14px 12px; gap:10px;
  border-top:1px solid var(--border);
}
.sb-nav-btn {
  padding:9px 18px; border-radius:22px;
  border:1.5px solid var(--orange); background:transparent;
  color:var(--orange); font-size:.82rem; font-weight:700;
  cursor:pointer; transition:background .15s, opacity .15s;
  flex-shrink:0;
}
.sb-nav-btn:hover { background:rgba(255,153,51,.12); }
.sb-nav-btn:disabled { opacity:.3; cursor:default; }
.sb-nav-info {
  flex:1; text-align:center; font-size:.78rem;
  color:var(--muted); font-weight:600; letter-spacing:.3px;
}
.sb-progress {
  display:flex; gap:3px; justify-content:center; flex-wrap:wrap;
  padding:0 14px 6px;
}
.sb-dot {
  width:6px; height:6px; border-radius:50%;
  background:rgba(255,255,255,.15); cursor:pointer;
  transition:background .2s, transform .2s;
  flex-shrink:0;
}
[data-theme="light"] .sb-dot { background:rgba(0,0,0,.15); }
.sb-dot.active { background:var(--orange); transform:scale(1.4); }
.sb-dot.visited { background:rgba(255,153,51,.4); }

/* Edit btn in book mode */
.sb-edit-btn {
  background:none; border:none; cursor:pointer;
  font-size:.82rem; padding:4px 8px; border-radius:8px;
  color:var(--muted); transition:background .15s; float:right;
}
.sb-edit-btn:hover { background:rgba(255,255,255,.1); }

/* Toast */
.toast {
  position:fixed; bottom:80px; left:50%; transform:translateX(-50%) translateY(10px);
  background:#1E293B; border:1px solid var(--border);
  border-radius:11px; padding:10px 18px;
  font-size:.83rem; color:var(--text);
  opacity:0; pointer-events:none;
  transition:opacity .25s, transform .25s;
  z-index:999; white-space:nowrap;
  box-shadow:0 8px 24px rgba(0,0,0,.4);
}
[data-theme="light"] .toast { background:#fff; }
.toast.show { opacity:1; transform:translateX(-50%) translateY(0); }

/* ══════════════════════════════════════════
   PAYWALL SCREEN
══════════════════════════════════════════ */
#screenPaywall {
  align-items:center; justify-content:center;
  padding:20px 16px; overflow-y:auto;
  background:linear-gradient(180deg, rgba(255,153,51,.07) 0%, transparent 50%);
}
.paywall-card {
  background:rgba(15,23,42,.9);
  border:1px solid rgba(255,153,51,.25); border-radius:24px;
  padding:28px 24px 24px;
  width:100%; max-width:400px;
  backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
  box-shadow:0 32px 64px rgba(0,0,0,.5), 0 0 0 1px rgba(255,153,51,.1);
  flex-shrink:0;
}
[data-theme="light"] .paywall-card {
  background:rgba(255,255,255,.95);
  box-shadow:0 16px 48px rgba(0,0,0,.12), 0 0 0 1px rgba(255,153,51,.15);
}
.paywall-gem {
  width:72px; height:72px; border-radius:22px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  display:flex; align-items:center; justify-content:center;
  font-size:36px; margin:0 auto 16px;
  box-shadow:0 10px 30px rgba(255,153,51,.45);
}
.paywall-title {
  text-align:center; font-size:1.35rem; font-weight:900;
  letter-spacing:-.4px; margin-bottom:4px;
}
.paywall-title span { color:var(--orange); }
.paywall-sub {
  text-align:center; font-size:.82rem; color:var(--muted);
  margin-bottom:20px; line-height:1.5;
}
.paywall-features {
  list-style:none; margin-bottom:20px;
  display:flex; flex-direction:column; gap:9px;
}
.paywall-features li {
  display:flex; align-items:center; gap:10px;
  font-size:.87rem; font-weight:600;
}
.paywall-features li .pf-check {
  width:26px; height:26px; border-radius:8px;
  background:rgba(16,185,129,.15); border:1px solid rgba(16,185,129,.3);
  display:flex; align-items:center; justify-content:center;
  color:#10B981; font-size:13px; flex-shrink:0;
}
.paywall-price-row {
  display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:8px;
  margin-bottom:18px;
}
.paywall-price-card {
  background:rgba(255,255,255,.05); border:1.5px solid var(--border);
  border-radius:14px; padding:12px 10px; text-align:center;
  cursor:pointer; transition:all .2s; position:relative;
}
[data-theme="light"] .paywall-price-card { background:rgba(0,0,0,.03); }
.paywall-price-card.selected {
  border-color:var(--orange); background:rgba(255,153,51,.08);
}
.paywall-price-card .ppc-badge {
  position:absolute; top:-10px; left:50%; transform:translateX(-50%);
  background:var(--orange); color:#0F172A;
  font-size:.6rem; font-weight:900; padding:2px 8px;
  border-radius:20px; white-space:nowrap;
}
.paywall-price-card .ppc-period {
  font-size:.72rem; color:var(--muted); font-weight:700;
  margin-bottom:4px; text-transform:uppercase; letter-spacing:.4px;
}
.paywall-price-card .ppc-price {
  font-size:1.4rem; font-weight:900; color:var(--text);
}
.paywall-price-card .ppc-per {
  font-size:.68rem; color:var(--muted); margin-top:2px;
}
.paywall-buy-btn {
  width:100%; padding:15px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:900; font-size:1rem;
  border:none; border-radius:14px; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:8px;
  box-shadow:0 6px 24px rgba(255,153,51,.45);
  transition:transform .15s, box-shadow .15s;
  margin-bottom:10px;
}
.paywall-buy-btn:hover { transform:translateY(-2px); box-shadow:0 8px 28px rgba(255,153,51,.55); }
.paywall-buy-btn:active { transform:translateY(0); }
.paywall-skip {
  width:100%; padding:11px;
  background:transparent; border:1.5px solid var(--border);
  color:var(--muted); font-size:.85rem; font-weight:600;
  border-radius:12px; cursor:pointer;
  transition:border-color .2s, color .2s;
}
.paywall-skip:hover { border-color:rgba(255,255,255,.25); color:var(--text); }

/* ══════════════════════════════════════════
   MICHAEL TRAFIKKLÆRER — HOME CARD
══════════════════════════════════════════ */
.michael-card {
  display:flex; align-items:center; justify-content:space-between;
  width:100%; padding:14px 16px;
  background:linear-gradient(135deg, rgba(30,58,95,.55) 0%, rgba(37,99,235,.20) 100%);
  border:1.5px solid rgba(59,130,246,.45);
  border-radius:16px; cursor:pointer;
  transition:background .15s, border-color .15s;
  margin-bottom:4px;
}
.michael-card:hover { background:linear-gradient(135deg,rgba(30,58,95,.7) 0%,rgba(37,99,235,.30) 100%); border-color:rgba(59,130,246,.7); }
.michael-card-left  { display:flex; align-items:center; gap:12px; }
.michael-card-avatar {
  width:44px; height:44px; border-radius:50%;
  background:#1E3A5F; border:1.5px solid rgba(59,130,246,.5);
  display:flex; align-items:center; justify-content:center;
  font-size:22px; flex-shrink:0;
}
.michael-card-name  { font-size:.95rem; font-weight:800; color:#93C5FD; }
.michael-card-sub   { font-size:.8rem;  font-weight:500; color:#64748B; margin-top:2px; }
.michael-card-arrow { font-size:1.5rem; color:#3B82F6; font-weight:300; }

/* Highlighted Michael tab in bottom nav */
.bn-tab-michael       { color:#60A5FA !important; }
.bn-tab-michael.active { color:#3B82F6 !important; border-top-color:#3B82F6 !important; }

/* ══════════════════════════════════════════
   MICHAEL TRAFIKKLÆRER — CHAT UI
══════════════════════════════════════════ */
.teacher-header {
  display:flex; align-items:center; gap:12px;
  padding:14px 16px; border-bottom:1px solid var(--border);
  background:var(--bg2); flex-shrink:0;
}
.teacher-avatar {
  width:40px; height:40px; border-radius:50%;
  background:#1E3A5F; display:flex; align-items:center;
  justify-content:center; font-size:20px; flex-shrink:0;
}
.teacher-name { font-size:.95rem; font-weight:700; color:var(--text); }
.teacher-status { font-size:.75rem; color:#10B981; margin-top:2px; }

/* Mobile baseline — chat col fills screen, side panel hidden */
.teacher-chat-col {
  display:flex; flex-direction:column;
  flex:1; min-height:0;
}
.teacher-side-panel { display:none; }

.teacher-messages {
  flex:1; min-height:0; overflow-y:auto; padding:16px 14px 12px;
  display:flex; flex-direction:column; gap:14px;
}
.teacher-messages::-webkit-scrollbar { width:0; }

.tm-row { display:flex; align-items:flex-end; gap:8px; min-width:0; width:100%; }
.tm-row.user  { justify-content:flex-end; }
.tm-row.assistant { justify-content:flex-start; }

.tm-av {
  width:28px; height:28px; border-radius:50%;
  background:#1E3A5F; display:flex; align-items:center;
  justify-content:center; font-size:13px; flex-shrink:0;
}
.tm-bubble {
  max-width:84%; min-width:0; padding:14px 16px; border-radius:18px;
  font-size:1rem; line-height:1.75;
  word-break:break-word; overflow-wrap:break-word;
  letter-spacing:.01em;
}
.tm-bubble.user {
  background:var(--orange); color:#fff;
  border-bottom-right-radius:5px; white-space:pre-wrap;
}
.tm-bubble.assistant {
  background:#0d1b2e; color:#F1F5F9;
  border:1px solid rgba(59,130,246,.18);
  border-bottom-left-radius:5px;
}
[data-theme="light"] .tm-bubble.assistant {
  background:#fff; color:#0F172A;
  border:1px solid rgba(0,0,0,.10);
}

/* Paragraph spacing inside assistant bubbles */
.tm-para { display:block; margin-bottom:.85em; }
.tm-para:last-child { margin-bottom:0; }

/* Section header (Situasjon:, Forklaring:, Teori:) */
.tm-section-hdr {
  display:block; font-weight:800; font-size:.82rem;
  letter-spacing:.06em; text-transform:uppercase;
  color:#60A5FA; margin-bottom:.35em; margin-top:.1em;
}

/* Practical advice box */
.tm-advice-box {
  background:rgba(255,153,51,.10); border:1px solid rgba(255,153,51,.35);
  border-left:3px solid var(--orange);
  border-radius:10px; padding:10px 13px; margin:.4em 0;
}
.tm-advice-hdr {
  font-weight:800; font-size:.85rem; color:var(--orange);
  margin-bottom:.45em;
}
.tm-advice-line { display:block; color:#FCD9A0; font-size:.9rem; line-height:1.6; }
[data-theme="light"] .tm-advice-box  { background:rgba(255,153,51,.08); border-color:rgba(255,153,51,.4); }
[data-theme="light"] .tm-advice-line { color:#92400E; }
[data-theme="light"] .tm-section-hdr { color:#1D4ED8; }
.tm-typing { display:flex; gap:5px; padding:12px 16px; }
.tm-typing span {
  width:7px; height:7px; border-radius:50%;
  background:var(--muted); animation:tmBounce 1.2s infinite;
}
.tm-typing span:nth-child(2) { animation-delay:.2s; }
.tm-typing span:nth-child(3) { animation-delay:.4s; }
@keyframes tmBounce {
  0%,60%,100% { transform:translateY(0); }
  30% { transform:translateY(-6px); }
}

.teacher-suggestions {
  padding:8px 14px 6px; display:flex; flex-direction:column;
  gap:6px; flex-shrink:0;
}
.teacher-chip {
  display:flex; align-items:center; gap:8px;
  background:var(--card); border:1px solid var(--border);
  color:var(--text); border-radius:10px;
  padding:10px 14px; font-size:.85rem; font-weight:600;
  cursor:pointer; text-align:left; transition:background .15s;
}
.teacher-chip:hover { background:var(--card2); }

/* Contextual reply chips — shown after assistant messages */
.tm-chips {
  display:flex; flex-direction:column; gap:8px;
  padding:14px 14px 6px 14px;
  border-top:1px solid rgba(255,255,255,.06);
  margin-top:4px;
}
.tm-chips-hdr {
  font-size:.78rem; font-weight:800; letter-spacing:.06em;
  color:var(--orange); text-transform:uppercase;
  margin-bottom:2px;
}
.tm-chip-btn {
  display:flex; align-items:center; gap:10px;
  background:#1a2744; border:1px solid rgba(59,130,246,.28);
  color:#F8FAFC; border-radius:12px;
  padding:12px 16px; font-size:.9rem; font-weight:700;
  cursor:pointer; text-align:left; width:100%;
  transition:background .15s, border-color .15s, transform .12s;
}
.tm-chip-btn:hover  { background:#1e3a5f; border-color:rgba(255,153,51,.65); color:#fff; transform:translateX(3px); }
.tm-chip-btn:active { transform:scale(.97); }
[data-theme="light"] .tm-chip-btn { background:#1e3a5f; border-color:rgba(59,130,246,.35); color:#F8FAFC; }
[data-theme="light"] .tm-chip-btn:hover { background:#1a2744; border-color:rgba(255,153,51,.55); }

.teacher-inputbar {
  display:flex; align-items:flex-end; gap:8px;
  padding:10px 14px; border-top:1px solid var(--border);
  background:var(--bg2); flex-shrink:0;
}
.teacher-input {
  flex:1; background:var(--bg); border:1px solid var(--border);
  color:var(--text); border-radius:12px;
  padding:10px 14px; font-size:.875rem; font-family:inherit;
  resize:none; max-height:100px; line-height:1.4;
  outline:none;
}
.teacher-input:focus { border-color:var(--orange); }
.teacher-input::placeholder { color:var(--muted); }
.teacher-send-btn {
  width:42px; height:42px; border-radius:50%;
  background:var(--orange); border:none; color:#fff;
  font-size:1rem; cursor:pointer; flex-shrink:0;
  transition:background .15s; display:flex;
  align-items:center; justify-content:center;
}
.teacher-send-btn:hover { background:var(--orange-dk); }
.teacher-send-btn:disabled { background:var(--border); cursor:default; }
</style>
</head>
<body>

<div id="app">

  <!-- Flag background — absolute so it's clipped by the phone frame on desktop -->
  <div class="flag-bg"></div>

  <!-- TOP BAR -->
  <div id="topBar">
    <div class="top-logo">
      <img src="/api/assets/developer-icon-512.png" style="width:32px;height:32px;border-radius:9px;object-fit:cover;">
      <span>Thai<span class="logo-t">2</span>Drive</span>
    </div>
    <div class="top-spacer"></div>
    <div id="topStreak">🔥 <span id="topStreakNum">0</span> <span data-key="streak">dag streak</span></div>
    <div style="display:flex;gap:8px;align-items:center;margin-left:12px">
      <button class="lang-btn active" id="topLangTH" onclick="setLang('th')" title="ภาษาไทย" style="width:36px;height:36px">
        <span class="cflag"><svg viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg"><rect width="900" height="600" fill="#A51931"/><rect width="900" height="480" y="60" fill="#F4F5F8"/><rect width="900" height="320" y="140" fill="#241D4F"/></svg></span>
      </button>
      <button class="lang-btn" id="topLangNO" onclick="setLang('no')" title="Norsk" style="width:36px;height:36px">
        <span class="cflag"><svg viewBox="0 0 22 16" xmlns="http://www.w3.org/2000/svg"><rect width="22" height="16" fill="#EF2B2D"/><rect x="6" width="4" height="16" fill="#fff"/><rect y="6" width="22" height="4" fill="#fff"/><rect x="7" width="2" height="16" fill="#002868"/><rect y="7" width="22" height="2" fill="#002868"/></svg></span>
      </button>
      <button class="lang-btn" id="topLangEN" onclick="setLang('en')" title="English" style="width:36px;height:36px">
        <span class="cflag"><svg viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="30" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" stroke-width="4"/><rect y="11" width="60" height="8" fill="#fff"/><rect x="26" width="8" height="30" fill="#fff"/><rect y="12" width="60" height="6" fill="#C8102E"/><rect x="27" width="6" height="30" fill="#C8102E"/></svg></span>
      </button>
      <button onclick="showTab('settings')" title="Innstillinger" style="width:34px;height:34px;border-radius:50%;border:none;background:rgba(255,255,255,.06);color:var(--muted);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .2s,color .2s;flex-shrink:0;" onmouseover="this.style.background='rgba(255,255,255,.12)';this.style.color='var(--text)'" onmouseout="this.style.background='rgba(255,255,255,.06)';this.style.color='var(--muted)'">⚙️</button>
    </div>
  </div>

  <!-- CONTENT -->
  <div id="content">

    <!-- ═══ AUTH SCREEN ═══ -->
    <div class="screen active" id="screenAuth">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-big-icon"><img src="/api/assets/developer-icon-512.png" style="width:56px;height:56px;border-radius:14px;object-fit:cover;"></div>
          <h1>Thai<span>2Drive</span></h1>
          <p>Teoriprøven på thai</p>
          <div class="auth-flags">
            <span class="auth-flag">
              <svg viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg"><rect width="900" height="600" fill="#A51931"/><rect width="900" height="480" y="60" fill="#F4F5F8"/><rect width="900" height="320" y="140" fill="#241D4F"/></svg>
            </span>
            <span class="auth-flag">
              <svg viewBox="0 0 22 16" xmlns="http://www.w3.org/2000/svg"><rect width="22" height="16" fill="#EF2B2D"/><rect x="6" width="4" height="16" fill="#fff"/><rect y="6" width="22" height="4" fill="#fff"/><rect x="7" width="2" height="16" fill="#002868"/><rect y="7" width="22" height="2" fill="#002868"/></svg>
            </span>
          </div>
        </div>

        <div class="auth-tabs">
          <button class="auth-tab active" onclick="switchTab('login')" data-key="login">Logg inn</button>
          <button class="auth-tab" onclick="switchTab('register')" data-key="register">Registrer</button>
        </div>

        <div class="auth-error" id="authError"></div>
        <div class="auth-success" id="authSuccess"></div>

        <!-- LOGIN -->
        <div id="formLogin">
          <div class="form-group">
            <label data-key="auth_email">E-post</label>
            <input type="email" id="loginEmail" placeholder="din@epost.com" data-placeholder-key="auth_email_placeholder" autocomplete="email">
          </div>
          <div class="form-group">
            <label data-key="auth_password">Passord</label>
            <div class="pw-wrap">
              <input type="password" id="loginPass" placeholder="••••••••" data-placeholder-key="auth_password_placeholder" autocomplete="current-password">
              <button type="button" class="pw-eye" onclick="togglePw(this)" tabindex="-1" title="Vis/skjul passord" aria-label="Vis/skjul passord">👁</button>
            </div>
          </div>
          <div class="forgot-link"><a onclick="showForgot()" data-key="forgot_password">Glemt passord?</a></div>
          <button class="auth-btn" onclick="doLogin()" data-key="login">Logg inn</button>
        </div>

        <!-- REGISTER -->
        <div id="formRegister" style="display:none">
          <div class="form-group">
            <label data-key="auth_name">Navn</label>
            <input type="text" id="regName" placeholder="Ditt fulle navn" data-placeholder-key="auth_name_placeholder">
          </div>
          <div class="form-group">
            <label data-key="auth_email">E-post</label>
            <input type="email" id="regEmail" placeholder="din@epost.com" data-placeholder-key="auth_email_placeholder" autocomplete="email">
          </div>
          <div class="form-group">
            <label data-key="auth_password">Passord</label>
            <div class="pw-wrap">
              <input type="password" id="regPass" placeholder="Minst 6 tegn" data-placeholder-key="auth_password_min_placeholder" autocomplete="new-password">
              <button type="button" class="pw-eye" onclick="togglePw(this)" tabindex="-1" title="Vis/skjul passord" aria-label="Vis/skjul passord">👁</button>
            </div>
          </div>
          <button class="auth-btn" onclick="doRegister()" data-key="create_account">Opprett konto</button>
        </div>

        <!-- FORGOT -->
        <div id="formForgot" style="display:none">
          <div class="form-group">
            <label data-key="auth_email">E-post</label>
            <input type="email" id="forgotEmail" placeholder="din@epost.com" data-placeholder-key="auth_email_placeholder">
          </div>
          <button class="auth-btn" id="forgotSubmitBtn" onclick="doForgot()" data-key="send_reset">Send tilbakestillingslenke</button>
          <div style="text-align:center;margin-top:12px">
            <a style="font-size:.78rem;color:var(--muted);cursor:pointer" onclick="switchTab('login')" data-key="back">← Tilbake</a>
          </div>
        </div>

        <!-- RESET PASSWORD (enter code + new password) -->
        <div id="formReset" style="display:none">
          <p style="font-size:.85rem;color:var(--muted);margin-bottom:12px;line-height:1.5" id="resetInstructions">Sjekk e-posten din for koden</p>
          <div class="form-group">
            <label data-key="reset_code_label">Kode</label>
            <input type="text" id="resetCode" placeholder="123456" inputmode="numeric" maxlength="6" autocomplete="one-time-code" style="letter-spacing:.2em;font-size:1.2rem">
          </div>
          <div class="form-group">
            <label data-key="reset_new_pass_label">Nytt passord</label>
            <div class="pw-wrap">
              <input type="password" id="resetNewPass" placeholder="Minst 6 tegn" autocomplete="new-password">
              <button type="button" class="pw-eye" onclick="togglePw(this)" tabindex="-1" title="Vis/skjul passord" aria-label="Vis/skjul passord">👁</button>
            </div>
          </div>
          <button class="auth-btn" id="resetSubmitBtn" onclick="doResetPassword()" data-key="reset_submit">Sett nytt passord</button>
          <div style="text-align:center;margin-top:12px">
            <a style="font-size:.78rem;color:var(--muted);cursor:pointer" onclick="switchTab('forgot')" data-key="back">← Tilbake</a>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ HOME SCREEN ═══ -->
    <div class="screen" id="screenHome">
      <div class="home-top">
        <div class="home-logo-row">
          <img src="/api/assets/developer-icon-512.png" style="width:64px;height:64px;border-radius:18px;object-fit:cover;box-shadow:0 8px 24px rgba(255,153,51,.35);">
          <div class="home-title">Thai<span>2</span>Drive</div>
          <div class="home-sub" data-key="app_sub">สอบใบขับขี่นอร์เวย์</div>
        </div>

        <div class="streak-badge">
          <span class="streak-fire">🔥</span>
          <span class="streak-num" id="homeStreakNum">0</span>
          <span class="streak-lbl" data-key="streak">dag streak</span>
        </div>
      </div>

      <button class="home-cta" onclick="startRandomQuiz()">
        ▶&nbsp;&nbsp;Start quiz
      </button>

      <div class="home-sec-btns">
        <button class="home-sec-btn" onclick="startExam()">📋 Eksamen</button>
        <button class="home-sec-btn" onclick="startDailyTest()">📅 Daglig test</button>
        <button class="home-sec-btn" onclick="showTab('studybook')" style="grid-column:1/-1" data-key="studybook_home">📖 Studiebok — Norsk trafikk</button>
      </div>

      <!-- Michael Trafikklærer card -->
      <button class="michael-card" onclick="showTab('teacher')">
        <div class="michael-card-left">
          <div class="michael-card-avatar">🚗</div>
          <div class="michael-card-text">
            <div class="michael-card-name">Michael Trafikklærer</div>
            <div class="michael-card-sub" id="michaelCardSub">Still et spørsmål om trafikk</div>
          </div>
        </div>
        <div class="michael-card-arrow">›</div>
      </button>

      <div class="home-sec-btns" style="display:none"><!-- placeholder to keep JS index intact -->
      </div>

      <div class="home-stats">
        <div class="home-stat">
          <div class="home-stat-num" id="homeStatAnswered">–</div>
          <div class="home-stat-lbl" data-key="answered">Besvart</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-num" id="homeStatCorrect">–</div>
          <div class="home-stat-lbl" data-key="correct_stat">Riktige</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-num" id="homeStatAcc">–</div>
          <div class="home-stat-lbl" data-key="accuracy">Nøyaktighet</div>
        </div>
      </div>

      <!-- Readiness card — populated by loadHome() from last quiz attempt -->
      <div class="home-readiness" id="homeReadiness" style="display:none" onclick="showTab('history')">
        <div class="hr-dot" id="hrDot"></div>
        <div class="hr-main">
          <div class="hr-label">Siste økt</div>
          <div class="hr-status" id="hrStatus"></div>
          <div class="hr-sub" id="hrSub"></div>
        </div>
        <div class="hr-pct" id="hrPct"></div>
      </div>

      <div class="premium-banner" id="homePremiumBanner" style="display:none">
        <span class="pb-icon">💎</span>
        <div class="pb-text">
          <h4 class="pb-title" data-key="premium_on">⭐ Premium</h4>
          <p class="pb-sub" data-key="premium_sub">Du har tilgang til alle funksjoner</p>
        </div>
      </div>
    </div>

    <!-- ═══ CATEGORIES SCREEN ═══ -->
    <div class="screen" id="screenCats">
      <div class="cats-header">
        <div class="screen-title">📚 <span data-key="cats">Kategorier</span> <span id="catCount"></span></div>
      </div>
      <div class="cats-scroll">
        <div class="cat-grid" id="catGrid">
          <div class="loading-wrap" style="grid-column:1/-1">
            <div class="spinner"></div>
            <span style="color:var(--muted);font-size:.85rem">Laster kategorier…</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ QUIZ SCREEN ═══ -->
    <div class="screen" id="screenQuiz">

      <!-- LEFT COLUMN — question, answers, controls (full-width on mobile) -->
      <div class="quiz-left-col">
        <div class="quiz-top">
          <button class="back-btn" onclick="goBack()">← Tilbake</button>
          <div class="quiz-prog-wrap">
            <div class="quiz-prog-lbl" id="qProgLbl">Spørsmål 1 av 30</div>
            <div class="quiz-prog-bar">
              <div class="quiz-prog-fill" id="qProgFill" style="width:0%"></div>
            </div>
          </div>
          <div class="quiz-score-badge">✓ <span id="qScoreNum">0</span></div>
          <div id="examTimerBadge" style="display:none;background:rgba(239,68,68,.18);border:1px solid rgba(239,68,68,.4);color:#EF4444;border-radius:20px;padding:4px 12px;font-size:.85rem;font-weight:700;margin-left:8px;">⏱ <span id="examTimerLbl">90:00</span></div>
        </div>
        <div class="quiz-body">
          <div class="quiz-card" id="qCard">
            <div class="loading-wrap"><div class="spinner"></div></div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN — sticky AI instructor panel (desktop only) -->
      <div class="quiz-right-col" id="quizRightPanel">
        <!-- Large traffic image -->
        <div class="quiz-ai-imgbox">
          <img id="quizAiImg" class="quiz-ai-img" src="" alt="">
          <div class="quiz-ai-img-overlay" id="quizAiOverlay"></div>
          <!-- Image label overlay -->
          <div class="quiz-ai-img-badge" id="quizAiImgBadge">📸 Trafikksituasjon</div>
        </div>
        <!-- AI instructor panel -->
        <div class="quiz-ai-panel">
          <div class="quiz-ai-panel-header">
            <div class="quiz-ai-panel-title">
              <span class="quiz-ai-robot">🤖</span>
              <div>
                <div class="quiz-ai-panel-name" data-key="ai_teacher">AI Kjørelærer</div>
                <div class="quiz-ai-panel-sub" data-key="traffic_understanding">Trafikkforståelse</div>
              </div>
            </div>
            <div class="quiz-ai-status" id="quizAiStatus">Venter på svar…</div>
          </div>
          <div class="quiz-ai-body" id="quizAiBody">
            <div class="quiz-ai-idle">
              <div class="quiz-ai-idle-icon">👆</div>
              <div class="quiz-ai-idle-text" data-key="ai_idle">Ta deg tid — hva tror du er riktig? Velg et svar, så forklarer jeg.</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ═══ BOOKMARKS SCREEN ═══ -->
    <div class="screen" id="screenBookmarks">
      <div class="bm-header">
        <div class="screen-title">🔖 <span data-key="bookmarks">Bokmerker</span> <span id="bmCount"></span></div>
      </div>
      <div class="bm-scroll" id="bmScroll">
        <div class="loading-wrap">
          <div class="spinner"></div>
        </div>
      </div>
    </div>

    <!-- ═══ SIGNS SCREEN ═══ -->
    <div class="screen" id="screenSigns">
      <div class="signs-header">
        <div class="screen-title">🪧 <span data-key="signs">Trafikkskilt</span></div>
        <div class="signs-count" id="signsCount"></div>
      </div>
      <div class="signs-scroll" id="signsScroll">
        <div class="loading-wrap"><div class="spinner"></div></div>
      </div>
    </div>

    <!-- ═══ SETTINGS SCREEN ═══ -->
    <div class="screen" id="screenSettings">
      <div class="settings-inner">

        <!-- Profile hero -->
        <div class="settings-profile-hero">
          <div class="settings-avatar" id="settAvatar">👤</div>
          <div class="settings-profile-name" id="settName">–</div>
          <div class="settings-profile-email" id="settEmail">–</div>
          <div class="settings-profile-badges account-badges" id="settBadges"></div>
        </div>

        <!-- Språk -->
        <div class="settings-section">
          <div class="settings-label" data-key="language">Språk</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon blue">🌐</div>
              <div class="sr-label">
                <div class="sr-title" data-key="q_lang">Spørsmålsspråk</div>
                <div class="sr-sub" data-key="q_lang_sub">Velg språk for spørsmål og svar</div>
              </div>
              <div class="lang-btns">
                <button class="lang-btn active" id="langTH" onclick="setLang('th')" title="ภาษาไทย">
                  <span class="cflag"><svg viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg"><rect width="900" height="600" fill="#A51931"/><rect width="900" height="480" y="60" fill="#F4F5F8"/><rect width="900" height="320" y="140" fill="#241D4F"/></svg></span>
                </button>
                <button class="lang-btn" id="langNO" onclick="setLang('no')" title="Norsk">
                  <span class="cflag"><svg viewBox="0 0 22 16" xmlns="http://www.w3.org/2000/svg"><rect width="22" height="16" fill="#EF2B2D"/><rect x="6" width="4" height="16" fill="#fff"/><rect y="6" width="22" height="4" fill="#fff"/><rect x="7" width="2" height="16" fill="#002868"/><rect y="7" width="22" height="2" fill="#002868"/></svg></span>
                </button>
                <button class="lang-btn" id="langEN" onclick="setLang('en')" title="English">
                  <span class="cflag"><svg viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="30" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" stroke-width="4"/><rect y="11" width="60" height="8" fill="#fff"/><rect x="26" width="8" height="30" fill="#fff"/><rect y="12" width="60" height="6" fill="#C8102E"/><rect x="27" width="6" height="30" fill="#C8102E"/></svg></span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Lyd -->
        <div class="settings-section">
          <div class="settings-label" data-key="sound">Lyd</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon green">🔊</div>
              <div class="sr-label">
                <div class="sr-title" data-key="sfx">Lydeffekter</div>
                <div class="sr-sub" data-key="sfx_sub">Pling ved riktig, buzz ved feil</div>
              </div>
              <label class="toggle">
                <input type="checkbox" id="soundToggle" checked onchange="toggleSound(this)">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="settings-row">
              <div class="sr-icon green">📳</div>
              <div class="sr-label">
                <div class="sr-title" data-key="style">Stil</div>
                <div class="sr-sub" data-key="style_sub">Tilbakemelding når du svarer</div>
              </div>
              <div class="seg-ctrl">
                <button class="seg-btn active" data-key="soft" onclick="setFeedback('soft',this)">Myk</button>
                <button class="seg-btn" data-key="strong" onclick="setFeedback('strong',this)">Sterk</button>
              </div>
            </div>
            <div class="settings-row" style="flex-wrap:wrap; gap:8px;">
              <div class="sr-icon green">🎙️</div>
              <div class="sr-label" style="flex:1; min-width:80px;">
                <div class="sr-title">Opplesing — Tempo</div>
                <div class="sr-sub">Hastighet på talesyntese</div>
              </div>
              <div id="settSpdBtns" style="display:flex;gap:5px;flex-wrap:wrap;"></div>
            </div>
            <div class="settings-row" style="flex-wrap:wrap; gap:8px;">
              <div class="sr-icon green">🔈</div>
              <div class="sr-label" style="flex:1; min-width:80px;">
                <div class="sr-title">Opplesing — Volum</div>
                <div class="sr-sub">Lydstyrke på talesyntese</div>
              </div>
              <div id="settVolBtns" style="display:flex;gap:5px;flex-wrap:wrap;"></div>
            </div>
          </div>
        </div>

        <!-- Tema -->
        <div class="settings-section">
          <div class="settings-label" data-key="appearance">Utseende</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon purple">🎨</div>
              <div class="sr-label"><div class="sr-title" data-key="theme">Tema</div></div>
              <div class="seg-ctrl">
                <button class="seg-btn" id="themeBtnLight" data-key="light" onclick="setTheme('light',this)">Lys</button>
                <button class="seg-btn active" id="themeBtnDark" data-key="dark" onclick="setTheme('dark',this)">Mørk</button>
                <button class="seg-btn" id="themeBtnSystem" data-key="auto" onclick="setTheme('system',this)">Auto</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Om appen -->
        <div class="settings-section">
          <div class="settings-label">Om appen</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon gray">📱</div>
              <div class="sr-label">
                <div class="sr-title">Thai2Drive Web</div>
                <div class="sr-sub">Teoriprøven på thai for Norge</div>
              </div>
              <div style="color:var(--muted);font-size:.78rem;font-weight:700;background:rgba(255,255,255,.07);padding:3px 9px;border-radius:20px;">v2.0</div>
            </div>
          </div>
        </div>

        <button class="logout-btn" onclick="logout()">🚪 &nbsp;Logg ut</button>

      </div>
    </div>

    <!-- ═══ HISTORY SCREEN ═══ -->
    <div class="screen" id="screenHistory">
      <div class="hist-header">
        <div class="screen-title">📊 <span data-key="history">Historikk</span> <span id="histCount"></span></div>
      </div>
      <div class="hist-scroll" id="histScroll">
        <div class="loading-wrap">
          <div class="spinner"></div>
        </div>
      </div>
    </div>

    <!-- ═══ STUDIEBOK SCREEN ═══ -->
    <div class="screen" id="screenStudybook">
      <!-- Top bar: back + search -->
      <div class="sb-topbar">
        <button class="back-btn" onclick="showTab('home')">← Tilbake</button>
        <div class="sb-search-wrap">
          <input id="sbSearchInput" type="text" placeholder="Søk eller § nummer..." data-placeholder-key="studybook_search_placeholder" oninput="sbSearch(this.value)" autocomplete="off" />
        </div>
      </div>
      <!-- Search results dropdown -->
      <div id="sbSearchResults" class="sb-search-results" style="display:none;"></div>
      <!-- Progress dots -->
      <div class="sb-progress" id="sbProgress"></div>
      <!-- Book reader — one chapter at a time -->
      <div class="sb-reader" id="sbReader"><div class="loading-wrap"><div class="spinner"></div></div></div>
      <!-- Prev / page info / Next -->
      <div class="sb-nav">
        <button class="sb-nav-btn" id="sbPrevBtn" onclick="sbGoTo(_sbCurrent - 1)" data-key="studybook_prev">‹ Forrige</button>
        <div class="sb-nav-info" id="sbNavInfo" data-key="studybook_loading">Laster...</div>
        <button class="sb-nav-btn" id="sbNextBtn" onclick="sbGoTo(_sbCurrent + 1)" data-key="studybook_next">Neste ›</button>
      </div>
    </div>

    <!-- ═══ STUDIEBOK ADMIN EDIT MODAL ═══ -->
    <div id="studiebokEditModal" style="display:none;position:fixed;inset:0;z-index:9000;background:rgba(0,0,0,.6);align-items:center;justify-content:center;">
      <div style="background:var(--card);border-radius:16px;padding:24px;width:min(92vw,520px);max-height:80vh;overflow-y:auto;display:flex;flex-direction:column;gap:12px;">
        <div style="font-weight:700;font-size:1.05rem;" data-key="studybook_edit_chapter">✏️ Rediger kapittel</div>
        <label style="font-size:.85rem;color:var(--muted);" data-key="studybook_title">Tittel</label>
        <input id="sbEditTitle" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" />
        <label style="font-size:.85rem;color:var(--muted);" data-key="studybook_content_html">Innhold (HTML)</label>
        <textarea id="sbEditContent" rows="10" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.85rem;width:100%;box-sizing:border-box;resize:vertical;font-family:monospace;"></textarea>
        <label style="font-size:.85rem;color:var(--muted);" data-key="studybook_image_url">🖼️ Bilde URL</label>
        <input id="sbEditImageUrl" type="text" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" placeholder="https://..." />
        <label style="font-size:.85rem;color:var(--muted);" data-key="studybook_video_url">🎥 Video URL (fremtidig)</label>
        <input id="sbEditVideoUrl" type="text" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" placeholder="https://..." />
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:4px;">
          <button onclick="closeStudiebokModal()" data-key="cancel" style="padding:8px 18px;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--text);cursor:pointer;">Avbryt</button>
          <button onclick="saveStudiebokChapter()" data-key="save" style="padding:8px 18px;border-radius:8px;border:none;background:var(--orange);color:#0F172A;font-weight:600;cursor:pointer;">Lagre</button>
        </div>
      </div>
    </div>

    <!-- ═══ END SCREEN ═══ -->
    <div class="screen" id="screenEnd">
      <div class="end-wrap">
        <div class="end-score-quiet" id="endScoreQuiet">0 av 0 riktige</div>
        <div class="end-heading" id="endHeading" data-key="result_done">Øvelsen er ferdig.</div>
        <p class="end-body" id="endBody"></p>
        <div class="end-focus" id="endFocus" style="display:none">
          <div>
            <div class="end-focus-label" data-key="result_focus">Anbefalt øvelse</div>
            <div class="end-focus-topic" id="endFocusTopic"></div>
          </div>
        </div>
        <div class="end-btns">
          <button class="end-btn-pri" onclick="retryQuiz()">Øv igjen</button>
          <button class="end-btn-sec" onclick="showTab('home')" data-key="backhome">Tilbake til hjem</button>
          <button class="end-btn-sec" onclick="showTab('cats')" data-key="pickcat">Velg kategori</button>
        </div>
      </div>
    </div>

    <!-- ═══ PAYWALL SCREEN ═══ -->
    <div class="screen" id="screenPaywall">
      <div class="paywall-card">
        <div class="paywall-gem">💎</div>
        <div class="paywall-title" data-key="pw_title">Lås opp <span>Thai2Drive Premium</span></div>
        <div class="paywall-sub" data-key="pw_sub">Du har brukt 5 gratis spørsmål. Oppgrader for ubegrenset tilgang!</div>
        <ul class="paywall-features">
          <li><span class="pf-check">✓</span><span data-key="pw_f1">Ubegrenset spørsmål og kategorier</span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f2">Fullstendig eksamensmode (45 spørsmål)</span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f3">Daglig test og øvingsmodus</span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f4">Historikk og fremgangsstatistikk</span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f5">Trafikkskilt-galleri</span></li>
        </ul>
        <div class="paywall-price-row">
          <div class="paywall-price-card selected" onclick="selectPlan('monthly',this)" data-plan="monthly">
            <div class="ppc-period" data-key="pw_month">Månedlig</div>
            <div class="ppc-price" data-price-plan="monthly">99 kr</div>
            <div class="ppc-per" data-key="pw_per_month">per måned</div>
          </div>
          <div class="paywall-price-card" onclick="selectPlan('three_months',this)" data-plan="three_months" style="position:relative">
            <div class="ppc-badge" data-key="pw_best_value">Best verdi</div>
            <div class="ppc-period" data-key="pw_three_months">3 måneder</div>
            <div class="ppc-price" data-price-plan="three_months">299 kr</div>
            <div class="ppc-per" data-key="pw_per_three_months">per 3 måneder</div>
          </div>
          <div class="paywall-price-card" onclick="selectPlan('lifetime',this)" data-plan="lifetime">
            <div class="ppc-period" data-key="pw_lifetime">Livstid</div>
            <div class="ppc-price" data-price-plan="lifetime">699 kr</div>
            <div class="ppc-per" data-key="pw_per_lifetime">engangsbetaling</div>
          </div>
        </div>
        <button class="paywall-buy-btn" onclick="buyPremium()">⭐ <span data-key="pw_buy">Kjøp Premium</span></button>
        <button class="paywall-skip" onclick="paywallSkip()" data-key="pw_skip">Fortsett gratis</button>
      </div>
    </div>

    <!-- ═══ MICHAEL TRAFIKKLÆRER SCREEN ═══ -->
    <div class="screen" id="screenTeacher">

      <!-- LEFT: chat column (full width on mobile, flex:1 on desktop) -->
      <div class="teacher-chat-col">

        <!-- Chat header -->
        <div class="teacher-header">
          <div class="teacher-avatar">🚗</div>
          <div class="teacher-header-info">
            <div class="teacher-name" id="teacherNameLbl">Michael Trafikklærer</div>
            <div class="teacher-status" data-key="teacher_online">● Online</div>
          </div>
        </div>

        <!-- Message list -->
        <div class="teacher-messages" id="teacherMessages">
          <!-- Welcome bubble injected by JS -->
        </div>

        <!-- Suggestion chips — shown only before first user message -->
        <div class="teacher-suggestions" id="teacherSuggestions">
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)" data-msg-no="🛑 Forklar et skilt" data-msg-th="🛑 อธิบายป้ายจราจร" data-msg-en="🛑 Explain a sign">🛑 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)" data-msg-no="🚗 Hjelp med vikeplikt" data-msg-th="🚗 ช่วยเรื่องการให้ทาง" data-msg-en="🚗 Help with right-of-way">🚗 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)" data-msg-no="📖 Forklar en trafikkregel" data-msg-th="📖 อธิบายกฎจราจร" data-msg-en="📖 Explain a traffic rule">📖 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)" data-msg-no="📝 Hjelp med teoriprøven" data-msg-th="📝 ช่วยเรื่องข้อสอบทฤษฎี" data-msg-en="📝 Help with the theory test">📝 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)" data-msg-no="📊 Hva bør jeg øve på?" data-msg-th="📊 ฉันควรฝึกเรื่องอะไร?" data-msg-en="📊 What should I practise?">📊 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)" data-msg-no="❓ Spør om Thai2Drive" data-msg-th="❓ ถามเกี่ยวกับ Thai2Drive" data-msg-en="❓ Ask about Thai2Drive">❓ <span class="chip-lbl"></span></button>
        </div>

        <!-- Input bar -->
        <div class="teacher-inputbar">
          <textarea class="teacher-input" id="teacherInput" rows="1" placeholder="..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();teacherSend();}"></textarea>
          <button class="teacher-send-btn" id="teacherSendBtn" onclick="teacherSend()">➤</button>
        </div>

      </div><!-- /teacher-chat-col -->

      <!-- RIGHT: helper panel — only visible on desktop via CSS -->
      <div class="teacher-side-panel" id="teacherSidePanel">
        <div class="tsp-title" id="tspTitle">Emner</div>
        <button class="tsp-btn" onclick="teacherSend('🛑 Forklar et skilt')">🛑 <span data-tsp="sign"></span></button>
        <button class="tsp-btn" onclick="teacherSend('🚗 Hjelp med vikeplikt')">🚗 <span data-tsp="vikeplikt"></span></button>
        <button class="tsp-btn" onclick="teacherSend('📖 Forklar en trafikkregel')">📖 <span data-tsp="rule"></span></button>
        <button class="tsp-btn" onclick="teacherSend('📊 Hva bør jeg øve på?')">📊 <span data-tsp="practice"></span></button>
        <button class="tsp-btn" onclick="teacherSend('📝 Hjelp med teoriprøven')">📝 <span data-tsp="theory"></span></button>
        <button class="tsp-btn" onclick="teacherSend('❓ Spør om Thai2Drive')">❓ <span data-tsp="app"></span></button>
      </div><!-- /teacher-side-panel -->

    </div><!-- /screenTeacher -->

  </div><!-- /content -->

  <!-- BOTTOM NAV — 8 tabs: Hjem → Kategorier → Historikk → Michael → Skilt → Studiebok → Bokmerker → Innstillinger -->
  <div id="bottomNav">
    <button class="bn-tab active" id="bnHome" onclick="showTab('home')">
      <span class="bn-icon">🏠</span>Hjem
    </button>
    <button class="bn-tab" id="bnCats" onclick="showTab('cats')">
      <span class="bn-icon">📚</span>Kategorier
    </button>
    <button class="bn-tab" id="bnHistory" onclick="showTab('history')">
      <span class="bn-icon">📊</span>Historikk
    </button>
    <button class="bn-tab bn-tab-michael" id="bnTeacher" onclick="showTab('teacher')">
      <span class="bn-icon">🚗</span>Michael
    </button>
    <button class="bn-tab" id="bnSigns" onclick="showTab('signs')">
      <span class="bn-icon">🪧</span>Skilt
    </button>
    <button class="bn-tab" id="bnStudybook" onclick="showTab('studybook')">
      <span class="bn-icon">📖</span>Studiebok
    </button>
    <button class="bn-tab" id="bnBookmarks" onclick="showTab('bookmarks')">
      <span class="bn-icon">🔖</span>Bokmerker
    </button>
    <button class="bn-tab" id="bnSettings" onclick="showTab('settings')">
      <span class="bn-icon">⚙️</span>Innstillinger
    </button>
  </div>

</div><!-- /app -->

<!-- ═══ SIGN DETAIL PANEL ═══ -->
<div class="sign-panel-backdrop" id="signPanelBackdrop" onclick="closeSignDetail()"></div>
<div class="sign-panel" id="signPanel">
  <div class="sp-handle"></div>
  <div class="sp-header">
    <button class="sp-close" onclick="closeSignDetail()">✕</button>
    <div class="sp-img-wrap">
      <img class="sp-img" id="spImg" src="" alt="">
    </div>
    <div class="sp-name" id="spName">–</div>
    <div class="sp-group-label" id="spGroupLabel"></div>
  </div>
  <div class="sp-lang-tabs">
    <button class="sp-lang-tab active" data-lang="no" onclick="setSignPanelLang('no')">🇳🇴 Norsk</button>
    <button class="sp-lang-tab" data-lang="th" onclick="setSignPanelLang('th')">🇹🇭 Thai</button>
    <button class="sp-lang-tab" data-lang="en" onclick="setSignPanelLang('en')">🇬🇧 English</button>
  </div>
  <div class="sp-body" id="spBody"></div>
  <div class="sp-actions">
    <button class="sp-btn-primary" type="button" onclick="practiceThisSign()" data-key="practice_this_sign">📚 Øv på dette skiltet</button>
    <div class="sp-actions-row">
      <button class="sp-btn-sm sp-btn-sm-audio" type="button" onclick="speakSign()">🔊<span data-key="read_aloud">Les høyt</span></button>
      <button class="sp-btn-sm sp-btn-sm-ai" type="button" onclick="askAiAboutSign()">🤖<span data-key="ask_ai">Spør AI</span></button>
      <button class="sp-btn-sm sp-btn-sm-bm" id="spBmBtn" type="button" onclick="toggleSignFavorite()">🔖<span data-key="save">Lagre</span></button>
    </div>
  </div>
</div>

<!-- ═══ HISTORY DETAIL PANEL ═══ -->
<div class="hist-panel-backdrop" id="histPanelBackdrop" onclick="closeHistDetail()"></div>
<div class="hist-panel" id="histPanel">
  <div class="hist-panel-handle"></div>
  <div class="hp-header">
    <button class="hp-close" onclick="closeHistDetail()">✕</button>
    <div class="hp-mode-lbl" id="hpModeLbl"></div>
    <div class="hp-score-big" id="hpScoreBig"></div>
    <div class="hp-score-sub" id="hpScoreSub"></div>
    <div class="hp-badge" id="hpBadge"></div>
    <div class="hp-stats" id="hpStats"></div>
  </div>
  <div class="hp-body" id="hpBody"></div>
  <div class="hp-actions" id="hpActions">
    <button class="hp-btn-pri" id="hpRetryBtn" data-key="retry">Prøv igjen</button>
    <button class="hp-btn-sec" onclick="closeHistDetail()" data-key="close">Lukk</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
// ════════════════════════════════════════════
//  STATE
// ════════════════════════════════════════════
// Safari Private Browsing safe localStorage wrapper
var _ls = {
  get: function(k) { try { return localStorage.getItem(k); } catch(e) { return null; } },
  set: function(k,v) { try { localStorage.setItem(k,v); } catch(e) {} },
  remove: function(k) { try { localStorage.removeItem(k); } catch(e) {} }
};
var token = _ls.get('t2d_token');
var user = null;
var deviceId = null;
var questions = [];
var qIdx = 0;
var qScore = 0;
var qAnswered = false;
var quizStartedAt = null;
var _lastSavedAttempt = null; // local mirror of the most recent saved attempt
var _sessionAnswers   = []; // per-question answer log — powers history detail panel
var _histAttempts     = []; // loaded attempts array — keyed by index for detail panel
var _histOpenIdx      = null;
var _reviewMode       = false; // true while in "Øv på feil" review flow
var _aiPanelTimer     = null; // delayed AI panel — cleared on nextQ to prevent cross-question bleed
var _reviewQuestions  = []; // wrong questions to review
var _reviewIdx        = 0;  // current review position
var ttsRate = 1;
var ttsVolume = parseFloat(_ls.get('t2d_vol') || '1');
var ttsPlaying = false;
var currentCat = null;
var soundOn = _ls.get('t2d_sound') !== 'off';
var feedbackStyle = _ls.get('t2d_feedback') || 'soft';
var appLang = _ls.get('t2d_lang') || 'th';
var activeTab = 'home';

function _histKey() { return 't2d_quiz_attempts_' + (deviceId || 'guest'); }
function _histLatestKey() { return 't2d_latest_attempt_' + (deviceId || 'guest'); }
function _attemptKey(a) { return (a && (a.client_attempt_id || a.id || (a.started_at + '|' + a.completed_at))) || ''; }
function _attemptTime(a) {
  var t = Date.parse((a && (a.completed_at || a.started_at)) || '');
  return isNaN(t) ? 0 : t;
}
function _normalizeAttempt(a) {
  if (!a) return null;
  var total = Number(a.total_questions || 0);
  var correct = Number(a.correct_answers || 0);
  var copy = Object.assign({}, a);
  copy.total_questions = total;
  copy.correct_answers = correct;
  copy.score_percentage = total > 0 ? Math.round((correct / total) * 100) : Math.round(Number(a.score_percentage || 0));
  copy.completed_at = copy.completed_at || copy.started_at || new Date().toISOString();
  return copy;
}
function _readLocalAttempts() {
  try {
    var items = JSON.parse(localStorage.getItem(_histKey()) || '[]');
    var latest = JSON.parse(localStorage.getItem(_histLatestKey()) || 'null');
    return (Array.isArray(items) ? items : []).concat(latest ? [latest] : []);
  } catch(e) { return []; }
}
function _writeLocalAttempt(attempt) {
  try {
    var normalized = _normalizeAttempt(attempt);
    if (!normalized) return;
    var items = _readLocalAttempts().filter(function(a) { return _attemptKey(a) !== _attemptKey(normalized); });
    items.unshift(normalized);
    items.sort(function(a, b) { return _attemptTime(b) - _attemptTime(a); });
    localStorage.setItem(_histKey(), JSON.stringify(items.slice(0, 50)));
    localStorage.setItem(_histLatestKey(), JSON.stringify(normalized));
    localStorage.setItem('t2d_history_updated_at', normalized.completed_at);
    _lastSavedAttempt = normalized;
  } catch(e) { console.warn('Local history write failed:', e); }
}
function _mergeAttempts(remote, local) {
  var map = {};
  (remote || []).concat(local || []).forEach(function(raw) {
    var a = _normalizeAttempt(raw);
    var key = _attemptKey(a);
    if (!a || !key) return;
    if (!map[key] || _attemptTime(a) >= _attemptTime(map[key])) map[key] = a;
  });
  return Object.keys(map).map(function(k) { return map[k]; }).sort(function(a, b) { return _attemptTime(b) - _attemptTime(a); });
}

// ── UI string translations ──────────────────────────────────
var UI = {
  back:        {th:'← กลับ',          no:'← Tilbake',      en:'← Back'},
  question:    {th:'คำถามที่',          no:'Spørsmål',        en:'Question'},
  of:          {th:'จาก',              no:'av',              en:'of'},
  next:        {th:'ถัดไป →',          no:'Neste →',         en:'Next →'},
  home:        {th:'หน้าแรก',          no:'Hjem',            en:'Home'},
  cats:        {th:'หมวดหมู่',          no:'Kategorier',      en:'Categories'},
  bookmarks:   {th:'ที่คั่นหน้า',       no:'Bokmerker',       en:'Bookmarks'},
  settings:    {th:'การตั้งค่า',        no:'Innstillinger',   en:'Settings'},
  correct:     {th:'🎉 ถูกต้อง!',       no:'✓ Riktig!',        en:'✓ Correct!'},
  wrong:       {th:'↩ ลองใหม่',        no:'↩ Ikke riktig',   en:'↩ Not quite'},
  retry:       {th:'🔄 ลองใหม่',        no:'🔄 Prøv igjen',   en:'🔄 Try again'},
  backhome:    {th:'🏠 กลับหน้าแรก',    no:'🏠 Tilbake til hjem', en:'🏠 Back to home'},
  pickcat:     {th:'📚 เลือกหมวดหมู่',  no:'📚 Velg kategori', en:'📚 Pick category'},
  startquiz:   {th:'▶  เริ่มควิซ',      no:'▶  Start quiz',   en:'▶  Start quiz'},
  exam:        {th:'📋 สอบ',            no:'📋 Eksamen',       en:'📋 Exam'},
  daily:       {th:'📅 ทดสอบรายวัน',    no:'📅 Daglig test',   en:'📅 Daily test'},
  loading:     {th:'กำลังโหลด…',        no:'Laster spørsmål…', en:'Loading…'},
  streak:      {th:'วันติดต่อกัน',     no:'dag streak',      en:'day streak'},
  answered:    {th:'ตอบแล้ว',          no:'BESVART',          en:'ANSWERED'},
  correct_stat:{th:'ถูกต้อง',           no:'RIKTIGE',          en:'CORRECT'},
  accuracy:    {th:'ความแม่นยำ',        no:'NØYAKTIGHET',      en:'ACCURACY'},
  premium_on:  {th:'⭐ พรีเมียม',       no:'⭐ Premium',        en:'⭐ Premium'},
  premium_sub: {th:'คุณมีสิทธิ์ทุกฟีเจอร์', no:'Du har tilgang til alle funksjoner', en:'You have access to all features'},
  acct:        {th:'บัญชี',             no:'KONTO',            en:'ACCOUNT'},
  language:    {th:'ภาษา',              no:'SPRÅK',            en:'LANGUAGE'},
  teacher:     {th:'Michael',            no:'Michael',          en:'Michael'},
  teacher_name:{th:'Michael Trafikklærer', no:'Michael Trafikklærer', en:'Michael Trafikklærer'},
  teacher_sub: {th:'ถามคำถามเกี่ยวกับการจราจร', no:'Still et spørsmål om trafikk', en:'Ask a question about traffic'},
  teacher_placeholder: {th:'ถามคำถาม...', no:'Still et spørsmål...', en:'Ask a question...'},
  teacher_error: {th:'ขอโทษ เกิดข้อผิดพลาด ลองใหม่อีกครั้ง', no:'Beklager, noe gikk galt. Prøv igjen.', en:'Sorry, something went wrong. Please try again.'},
  teacher_online:{th:'● ออนไลน์', no:'● Pålogget', en:'● Online'},
  tsp_title:   {th:'หัวข้อ',           no:'Emner',               en:'Topics'},
  tsp_sign:    {th:'อธิบายป้ายจราจร',  no:'Forklar et skilt',    en:'Explain a sign'},
  tsp_vikeplikt:{th:'ช่วยเรื่องการให้ทาง', no:'Hjelp med vikeplikt', en:'Help with right-of-way'},
  tsp_rule:    {th:'อธิบายกฎจราจร',   no:'Forklar en trafikkregel', en:'Explain a traffic rule'},
  tsp_practice:{th:'ฉันควรฝึกอะไร?',  no:'Hva bør jeg øve på?', en:'What should I practise?'},
  tsp_theory:  {th:'ช่วยเรื่องข้อสอบ', no:'Hjelp med teoriprøven', en:'Help with the theory test'},
  tsp_app:     {th:'ถามเกี่ยวกับแอป', no:'Spør om Thai2Drive',   en:'Ask about Thai2Drive'},
  choose_topic:{th:'🚗 เลือกหัวข้อ:',  no:'🚗 Velg tema:',        en:'🚗 Choose topic:'},
  q_lang:      {th:'ภาษาคำถาม',         no:'Spørsmålsspråk',   en:'Question language'},
  q_lang_sub:  {th:'เลือกภาษาสำหรับคำถามและคำตอบ', no:'Velg språk for spørsmål og svar', en:'Choose language for questions and answers'},
  sound:       {th:'เสียง',             no:'LYD',              en:'SOUND'},
  sfx:         {th:'เอฟเฟกต์เสียง',     no:'Lydeffekter',      en:'Sound effects'},
  sfx_sub:     {th:'เสียงเมื่อถูก/ผิด',  no:'Pling ved riktig, buzz ved feil', en:'Pling correct, buzz wrong'},
  style:       {th:'สไตล์',             no:'Stil',             en:'Style'},
  style_sub:   {th:'การแสดงผลเมื่อตอบ', no:'Tilbakemelding når du svarer', en:'Feedback when answering'},
  soft:        {th:'นุ่มนวล',            no:'Myk',              en:'Soft'},
  strong:      {th:'เข้มข้น',            no:'Sterk',            en:'Strong'},
  appearance:  {th:'รูปลักษณ์',          no:'UTSEENDE',         en:'APPEARANCE'},
  theme:       {th:'ธีม',               no:'Tema',             en:'Theme'},
  light:       {th:'สว่าง',              no:'Lys',              en:'Light'},
  dark:        {th:'มืด',               no:'Mørk',             en:'Dark'},
  auto:        {th:'อัตโนมัติ',           no:'Auto',             en:'Auto'},
  logout:      {th:'ออกจากระบบ',         no:'Logg ut',          en:'Log out'},
  history:     {th:'ประวัติ',            no:'Historikk',        en:'History'},
  signs:       {th:'ป้ายจราจร',          no:'Trafikkskilt',     en:'Traffic Signs'},
  signs_empty: {th:'ไม่พบป้าย',           no:'Ingen skilt funnet', en:'No signs found'},
  login:       {th:'เข้าสู่ระบบ',          no:'Logg inn',         en:'Log in'},
  no_results:  {th:'ไม่พบผลลัพธ์',          no:'Ingen treff',      en:'No results'},
  generic_error:{th:'มีบางอย่างผิดพลาด',    no:'Noe gikk galt',    en:'Something went wrong'},
  saved_chapter:{th:'บันทึกบทเรียนแล้ว',    no:'Kapittel lagret',  en:'Chapter saved'},
  ready_test:  {th:'พร้อมสอบ',             no:'Klar for prøven',  en:'Ready for test'},
  almost_ready:{th:'เกือบพร้อม',            no:'Nesten klar',      en:'Almost ready'},
  practice_more:{th:'ฝึกอีกนิด',            no:'Øv litt mer',      en:'Practice a bit more'},
  practice_more_short:{th:'ฝึกเพิ่ม',       no:'Øv mer',           en:'Practice more'},
  mode_exam:   {th:'สอบ',                  no:'Eksamen',          en:'Exam'},
  mode_category:{th:'หมวดหมู่',             no:'Kategori',         en:'Category'},
  mode_daily:  {th:'ทดสอบรายวัน',          no:'Daglig test',      en:'Daily test'},
  mode_random: {th:'ควิซสุ่ม',              no:'Tilfeldig quiz',   en:'Random quiz'},
  questions_word:{th:'คำถาม',              no:'spørsmål',         en:'questions'},
  signs_word:  {th:'ป้าย',                 no:'skilt',            en:'signs'},
  categories_empty:{th:'ไม่พบหมวดหมู่',     no:'Ingen kategorier funnet', en:'No categories found'},
  categories_load_error:{th:'โหลดหมวดหมู่ไม่ได้<br>ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต', no:'Kunne ikke laste kategorier.<br>Sjekk internettforbindelsen.', en:'Could not load categories.<br>Check your internet connection.'},
  questions_loading:{th:'กำลังโหลดคำถาม…', no:'Laster spørsmål…', en:'Loading questions…'},
  questions_empty:{th:'ไม่พบคำถามที่มีรูปภาพ<br>ลองหมวดหมู่อื่น', no:'Ingen spørsmål med bilde funnet.<br>Prøv en annen kategori.', en:'No image questions found.<br>Try another category.'},
  time_is_up:  {th:'หมดเวลาแล้ว! ⏰',      no:'Tid er ute! ⏰',    en:'Time is up! ⏰'},
  ai_waiting:  {th:'รอคำตอบ…',             no:'Venter på svar…',  en:'Waiting for answer…'},
  traffic_situation:{th:'📸 สถานการณ์จราจร', no:'📸 Trafikksituasjon', en:'📸 Traffic situation'},
  ai_teacher:  {th:'ครูสอนขับรถ AI',        no:'AI Kjørelærer',    en:'AI Driving Teacher'},
  traffic_understanding:{th:'ความเข้าใจจราจร', no:'Trafikkforståelse', en:'Traffic understanding'},
  ai_idle:     {th:'ค่อย ๆ ดูสถานการณ์ คุณคิดว่าข้อไหนถูก? เลือกคำตอบ แล้วครูจะอธิบาย', no:'Ta deg tid — hva tror du er riktig? Velg et svar, så forklarer jeg.', en:'Take your time. What do you think is right? Choose an answer, and I will explain.'},
  wrong_support_5:{th:'ยังไม่ถูก อ่านคำอธิบายอย่างใจเย็น ความเข้าใจต้องใช้เวลา', no:'Ikke riktig. Les forklaringen nøye — forståelse tar tid.', en:'Not quite. Read the explanation calmly. Understanding takes time.'},
  wrong_support_3:{th:'ครั้งนี้ยังไม่ถูก ลองดูคำอธิบายด้านล่าง', no:'Ikke riktig denne gangen. Gå gjennom forklaringen under.', en:'Not quite this time. Go through the explanation below.'},
  wrong_support_1:{th:'ยังไม่ถูก ดูคำอธิบายด้านล่าง', no:'Ikke riktig. Se forklaringen under.', en:'Not quite. See the explanation below.'},
  see_tag:     {th:'👀 ดู',                no:'👀 Se',            en:'👀 See'},
  understand_tag:{th:'🧠 เข้าใจ',          no:'🧠 Forstå',        en:'🧠 Understand'},
  choose_tag:  {th:'🚗 เลือก',             no:'🚗 Velg',          en:'🚗 Choose'},
  lens_generic_see:{th:'ใช้เวลาอ่านสถานการณ์ทั้งหมด', no:'Ta deg tid til å lese hele situasjonen', en:'Take time to read the whole situation'},
  lens_generic_understand:{th:'ปัจจัยที่สำคัญที่สุดตรงนี้คืออะไร?', no:'Hva er den viktigste faktoren her?', en:'What is the most important factor here?'},
  lens_generic_choose:{th:'เลือกทางเลือกที่ปลอดภัยที่สุดสำหรับทุกคน', no:'Velg det alternativet som er tryggest for alle i trafikken', en:'Choose the option that is safest for everyone in traffic'},
  review_title:{th:'ทบทวนข้อผิด',          no:'Gjennomgang av feil', en:'Mistake review'},
  review_idle:{th:'อ่านคำถามและคำอธิบายตามจังหวะของคุณเอง', no:'Les gjennom spørsmål og forklaringer i ditt eget tempo.', en:'Read through the questions and explanations at your own pace.'},
  review_done:{th:'ทบทวนเสร็จแล้ว',        no:'Gjennomgang fullført.', en:'Review complete.'},
  review_done_body:{th:'คุณได้ทบทวน {count} คำถามแล้ว อ่านคำอธิบายอีกครั้งก่อนทำควิซใหม่ได้', no:'Du har gått gjennom {count} spørsmål. Les gjerne forklaringene én gang til før du tar ny quiz.', en:'You have reviewed {count} questions. Read the explanations once more before taking a new quiz.'},
  review_progress:{th:'ทบทวน',             no:'Gjennomgang',      en:'Review'},
  review_finish:{th:'จบทบทวน',             no:'Fullfør gjennomgang', en:'Finish review'},
  you_answered:{th:'คุณตอบ',               no:'Du svarte',        en:'You answered'},
  correct_answer:{th:'คำตอบที่ถูก',        no:'Riktig svar',      en:'Correct answer'},
  explanation:{th:'คำอธิบาย',              no:'Forklaring',       en:'Explanation'},
  more_details:{th:'รายละเอียดเพิ่ม',       no:'Mer detaljer',     en:'More details'},
  show_more:   {th:'ดูเพิ่ม',              no:'Vis mer',          en:'Show more'},
  show_less:   {th:'ย่อน้อยลง',             no:'Vis mindre',       en:'Show less'},
  driving_teacher:{th:'ครูสอนขับรถ',        no:'Kjørelærer',       en:'Driving teacher'},
  video_short:{th:'📹 คำอธิบายสั้น',       no:'📹 Kort forklaring', en:'📹 Short explanation'},
  video_watch:{th:'📹 ดูคำอธิบายสั้น',      no:'📹 Se kort forklaring', en:'📹 Watch short explanation'},
  details:     {th:'ดูรายละเอียด',          no:'Se detaljer',      en:'View details'},
  passed:      {th:'ผ่าน',                 no:'Bestått',          en:'Passed'},
  not_passed:  {th:'ยังไม่ผ่าน',            no:'Ikke bestått',     en:'Not passed'},
  correct_count:{th:'ถูก',                 no:'riktige',          en:'correct'},
  wrong_count: {th:'ผิด',                  no:'gale',             en:'wrong'},
  total_count: {th:'ทั้งหมด',               no:'Totalt',           en:'Total'},
  wrong_answers:{th:'คำตอบที่ผิด',          no:'Feil svar',        en:'Wrong answers'},
  no_wrong_answers:{th:'ไม่มีข้อผิดในควิซนี้<br>ทำได้ดีมาก', no:'Ingen feil i denne quizen!<br>Veldig bra gjort.', en:'No mistakes in this quiz.<br>Very well done.'},
  old_quiz_details:{th:'รายละเอียดคำถามไม่มีสำหรับควิซเก่า<br>ทำควิซใหม่เพื่อดูคำตอบของคุณ', no:'Detaljert spørsmålsoversikt er ikke tilgjengelig for eldre quizer.<br>Ta en ny quiz for å se hva du svarte.', en:'Detailed question review is not available for older quizzes.<br>Take a new quiz to see your answers.'},
  review_wrong_count:{th:'ทบทวน {count} ข้อผิด', no:'Gå gjennom {count} feil svar', en:'Review {count} wrong answers'},
  bookmarks_login:{th:'เข้าสู่ระบบเพื่อดูที่คั่นหน้า', no:'Logg inn for å se bokmerker', en:'Log in to see bookmarks'},
  bookmarks_empty:{th:'ยังไม่มีที่คั่นหน้า<br>กด 🔖 ใต้คำถามเพื่อบันทึก', no:'Ingen bokmerker ennå.<br>Trykk 🔖 under et spørsmål for å lagre det.', en:'No bookmarks yet.<br>Tap 🔖 under a question to save it.'},
  bookmark_login:{th:'เข้าสู่ระบบเพื่อใช้ที่คั่นหน้า', no:'Logg inn for å bruke bokmerker', en:'Log in to use bookmarks'},
  bookmark:    {th:'ที่คั่นหน้า',           no:'Bokmerke',         en:'Bookmark'},
  bookmark_removed:{th:'ลบที่คั่นหน้าแล้ว', no:'Bokmerke fjernet', en:'Bookmark removed'},
  bookmark_remove_failed:{th:'ลบที่คั่นหน้าไม่ได้', no:'Kunne ikke fjerne bokmerke', en:'Could not remove bookmark'},
  bookmark_added:{th:'บันทึกที่คั่นหน้าแล้ว 🔖', no:'Bokmerke lagt til 🔖', en:'Bookmark added 🔖'},
  bookmark_add_failed:{th:'เพิ่มที่คั่นหน้าไม่ได้', no:'Kunne ikke legge til bokmerke', en:'Could not add bookmark'},
  history_login:{th:'เข้าสู่ระบบเพื่อดูประวัติ', no:'Logg inn for å se historikk', en:'Log in to see history'},
  history_empty:{th:'ยังไม่มีประวัติควิซ<br>ทำควิซให้เสร็จ แล้วผลลัพธ์จะแสดงที่นี่', no:'Ingen quiz-historikk ennå.<br>Fullfør en quiz for å se resultatene her.', en:'No quiz history yet.<br>Finish a quiz to see results here.'},
  history_load_error:{th:'โหลดประวัติไม่ได้', no:'Kunne ikke laste historikk.', en:'Could not load history.'},
  result_saved:{th:'บันทึกผลแล้ว ✓',        no:'Resultat lagret ✓', en:'Result saved ✓'},
  result_save_failed:{th:'บันทึกผลไม่สำเร็จ: ', no:'Lagring feilet: ', en:'Save failed: '},
  result_score:{th:'{correct} จาก {total} ถูก', no:'{correct} av {total} riktige', en:'{correct} of {total} correct'},
  result_focus:{th:'หัวข้อแนะนำให้ฝึก',      no:'Anbefalt øvelse',  en:'Recommended practice'},
  result_done:{th:'ทำแบบฝึกเสร็จแล้ว',       no:'Øvelsen er ferdig.', en:'Practice finished.'},
  result_exam_pass_head:{th:'ผ่าน',          no:'Bestått.',         en:'Passed.'},
  result_exam_pass_body:{th:'คุณพร้อมสำหรับการสอบทฤษฎีแล้ว ลองทำอีกหนึ่งรอบเพื่อเพิ่มความมั่นใจ', no:'Du er klar for teoriprøven. Gjennomfør gjerne enda en runde for å bygge selvtillit.', en:'You are ready for the theory test. Do one more round to build confidence.'},
  result_exam_fail_head:{th:'ครั้งนี้ยังไม่ผ่าน', no:'Ikke bestått denne gangen.', en:'Not passed this time.'},
  result_solid_head:{th:'ทำได้มั่นคง',       no:'Solid gjennomkjøring.', en:'Solid run-through.'},
  result_solid_body:{th:'คุณเริ่มจำสถานการณ์จราจรและตัดสินใจได้ถูกต้อง นี่คือสิ่งสำคัญในการขับจริง', no:'Du gjenkjenner trafikksituasjonene godt og vurderer riktig. Det er det som teller i praksis.', en:'You recognize traffic situations well and make sound decisions. That is what matters in real driving.'},
  result_right_way_head:{th:'คุณมาถูกทางแล้ว', no:'Du er på rett vei.', en:'You are on the right track.'},
  result_more_head:{th:'มาฝึกเพิ่มอีกนิด',   no:'La oss øve litt mer.', en:'Let us practice a bit more.'},
  result_more_body:{th:'กฎจราจรไม่ได้ติดตัวในรอบเดียว ฝึกต่ออย่างใจเย็น ความเข้าใจจะค่อย ๆ ชัดขึ้น', no:'Trafikkreglene sitter ikke alltid med én runde. Prøv igjen — det tar tid å bygge forståelse.', en:'Traffic rules do not always settle after one round. Keep practicing calmly; understanding grows with time.'},
  result_learn_head:{th:'ยังมีเรื่องให้เรียนรู้เพิ่ม', no:'Her er det mer å lære.', en:'There is more to learn here.'},
  result_learn_body:{th:'ไม่ต้องกังวล ความเข้าใจสร้างได้ทีละขั้น ใช้คำอธิบายอย่างใจเย็น', no:'Ikke bekymre deg — forståelse bygges gradvis. Bruk forklaringene aktivt og ta det steg for steg.', en:'Do not worry. Understanding builds gradually. Use the explanations calmly, step by step.'},
  lang_updated:{th:'อัปเดตภาษาแล้ว',        no:'Språk oppdatert',  en:'Language updated'},
  app_sub:     {th:'สอบใบขับขี่นอร์เวย์', no:'Norsk teoriprøve for thai-elever', en:'Norwegian driving theory for Thai learners'},
  register:    {th:'สมัครสมาชิก', no:'Registrer', en:'Register'},
  create_account:{th:'สร้างบัญชี', no:'Opprett konto', en:'Create account'},
  login_loading:{th:'กำลังเข้าสู่ระบบ…', no:'Logger inn…', en:'Logging in…'},
  register_loading:{th:'กำลังสร้างบัญชี…', no:'Oppretter konto…', en:'Creating account…'},
  send_reset:  {th:'ส่งลิงก์รีเซ็ตรหัสผ่าน', no:'Send tilbakestillingslenke', en:'Send reset link'},
  reset_sending:{th:'กำลังส่ง…', no:'Sender…', en:'Sending…'},
  forgot_password:{th:'ลืมรหัสผ่าน?', no:'Glemt passord?', en:'Forgot password?'},
  auth_email:  {th:'อีเมล', no:'E-post', en:'Email'},
  auth_password:{th:'รหัสผ่าน', no:'Passord', en:'Password'},
  auth_name:   {th:'ชื่อ', no:'Navn', en:'Name'},
  auth_email_placeholder:{th:'อีเมลของคุณ', no:'din@epost.com', en:'your@email.com'},
  auth_password_placeholder:{th:'รหัสผ่าน', no:'Passord', en:'Password'},
  auth_password_min_placeholder:{th:'อย่างน้อย 6 ตัวอักษร', no:'Minst 6 tegn', en:'At least 6 characters'},
  auth_name_placeholder:{th:'ชื่อเต็มของคุณ', no:'Ditt fulle navn', en:'Your full name'},
  auth_missing_login:{th:'กรอกอีเมลและรหัสผ่าน', no:'Fyll inn e-post og passord', en:'Enter email and password'},
  auth_missing_all:{th:'กรอกข้อมูลทุกช่อง', no:'Fyll inn alle feltene', en:'Fill in all fields'},
  auth_password_short:{th:'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร', no:'Passord må være minst 6 tegn', en:'Password must be at least 6 characters'},
  auth_missing_email:{th:'กรอกอีเมลของคุณ', no:'Fyll inn e-postadressen din', en:'Enter your email address'},
  auth_reset_sent:{th:'ส่งอีเมลแล้ว ตรวจสอบกล่องจดหมายของคุณ 📧', no:'E-post sendt! Sjekk innboksen din 📧', en:'Email sent. Check your inbox 📧'},
  email_already_registered:{th:'อีเมลนี้ลงทะเบียนแล้ว กรุณาเข้าสู่ระบบหรือรีเซ็ตรหัสผ่าน', no:'Denne e-posten er allerede registrert. Logg inn eller tilbakestill passordet.', en:'This email is already registered. Log in or reset password.'},
  email_not_registered:{th:'ไม่พบบัญชีที่ใช้อีเมลนี้', no:'Fant ingen konto med denne e-posten.', en:'No account was found with this email.'},
  reset_email_failed:{th:'ไม่สามารถส่งรหัสรีเซ็ตรหัสผ่านได้ กรุณาลองใหม่ภายหลังหรือติดต่อฝ่ายสนับสนุน', no:'Kunne ikke sende tilbakestillingskode. Prøv igjen senere eller kontakt support.', en:'Could not send reset code. Try again later or contact support.'},
  invalid_or_expired_reset_code:{th:'รหัสรีเซ็ตรหัสผ่านไม่ถูกต้องหรือหมดอายุแล้ว', no:'Ugyldig eller utløpt tilbakestillingskode', en:'Invalid or expired reset code'},
  reset_code_label:{th:'รหัส', no:'Kode', en:'Code'},
  reset_new_pass_label:{th:'รหัสผ่านใหม่', no:'Nytt passord', en:'New password'},
  reset_submit:{th:'ตั้งรหัสผ่านใหม่', no:'Sett nytt passord', en:'Set new password'},
  reset_submitting:{th:'กำลังบันทึก…', no:'Lagrer…', en:'Saving…'},
  reset_success:{th:'รีเซ็ตรหัสผ่านสำเร็จแล้ว กำลังเข้าสู่ระบบ…', no:'Passordet er tilbakestilt. Logg inn igjen.', en:'Password reset. Log in again.'},
  reset_instructions:{th:'ตรวจสอบอีเมลของคุณสำหรับรหัส', no:'Sjekk e-posten din for koden', en:'Check your email for the code'},
  reset_fill:{th:'กรุณากรอกรหัสและรหัสผ่านใหม่', no:'Fyll inn kode og nytt passord', en:'Enter the code and new password'},
  reset_pass_short:{th:'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร', no:'Nytt passord må være minst 6 tegn', en:'New password must be at least 6 characters'},
  email_not_registered:{th:'ไม่พบบัญชีที่ใช้อีเมลนี้', no:'Fant ingen konto med denne e-posten.', en:'No account found with this email.'},
  reset_email_failed:{th:'ไม่สามารถส่งรหัสรีเซ็ตได้ กรุณาลองใหม่ภายหลัง', no:'Kunne ikke sende tilbakestillingskode. Prøv igjen senere.', en:'Could not send reset code. Try again later.'},
  email_already_registered:{th:'อีเมลนี้มีบัญชีอยู่แล้ว เข้าสู่ระบบหรือรีเซ็ตรหัสผ่าน', no:'Denne e-posten er allerede registrert. Logg inn eller tilbakestill passordet.', en:'This email is already registered. Log in or reset your password.'},
  account_unavailable:{th:'บัญชีนี้ไม่พร้อมใช้งาน กรุณาติดต่อฝ่ายสนับสนุน', no:'Denne kontoen er ikke tilgjengelig. Kontakt support.', en:'This account is not available. Contact support.'},
  logout_confirm:{th:'คุณแน่ใจหรือว่าต้องการออกจากระบบ?', no:'Er du sikker på at du vil logge ut?', en:'Are you sure you want to log out?'},
  studybook_home:{th:'📖 หนังสือเรียน — การจราจรนอร์เวย์', no:'📖 Studiebok — Norsk trafikk', en:'📖 Study book — Norwegian traffic'},
  studybook_search_placeholder:{th:'ค้นหาหรือเลข §...', no:'Søk eller § nummer...', en:'Search or § number...'},
  studybook_prev:{th:'‹ ก่อนหน้า', no:'‹ Forrige', en:'‹ Previous'},
  studybook_next:{th:'ถัดไป ›', no:'Neste ›', en:'Next ›'},
  studybook_loading:{th:'กำลังโหลด...', no:'Laster...', en:'Loading...'},
  studybook_load_error:{th:'โหลดหนังสือเรียนไม่ได้', no:'Kunne ikke laste studiebok.', en:'Could not load the study book.'},
  studybook_no_results:{th:'ไม่พบผลลัพธ์', no:'Ingen treff', en:'No results'},
  studybook_edit_chapter:{th:'✏️ แก้ไขบทเรียน', no:'✏️ Rediger kapittel', en:'✏️ Edit chapter'},
  studybook_title:{th:'ชื่อเรื่อง', no:'Tittel', en:'Title'},
  studybook_content_html:{th:'เนื้อหา (HTML)', no:'Innhold (HTML)', en:'Content (HTML)'},
  studybook_image_url:{th:'🖼️ URL รูปภาพ', no:'🖼️ Bilde URL', en:'🖼️ Image URL'},
  studybook_video_url:{th:'🎥 Video URL (อนาคต)', no:'🎥 Video URL (fremtidig)', en:'🎥 Video URL (future)'},
  cancel:      {th:'ยกเลิก', no:'Avbryt', en:'Cancel'},
  sb_empty_fields:{th:'ชื่อเรื่องและเนื้อหาห้ามว่าง', no:'Tittel og innhold kan ikke være tomme', en:'Title and content cannot be empty'},
  practice_this_sign:{th:'📚 ฝึกป้ายนี้',     no:'📚 Øv på dette skiltet', en:'📚 Practice this sign'},
  save:        {th:'บันทึก',                no:'Lagre',            en:'Save'},
  saved:       {th:'บันทึกแล้ว',             no:'Lagret',           en:'Saved'},
  read_aloud:  {th:'อ่านออกเสียง',           no:'Les høyt',         en:'Read aloud'},
  ask_ai:      {th:'ถามครู AI',              no:'Spør AI',          en:'Ask AI'},
  ai_teacher_hint:{th:'ครู AI',              no:'AI-kjørelærer',    en:'AI teacher'},
  sign_ai_lesson:{th:'ดูป้ายนี้ร่วมกับสถานการณ์บนถนนจริง: {name}. ให้สังเกตรูปทรง สี สัญลักษณ์ และสิ่งที่ผู้ขับขี่ต้องทำทันที ใช้ป้ายนี้เพื่อปรับความเร็ว ตำแหน่งรถ และความระวังอย่างสงบ', no:'Se dette skiltet sammen med trafikksituasjonen: {name}. Legg merke til form, farge, symbol og hva føreren må gjøre nå. Bruk skiltet til å tilpasse fart, plassering og oppmerksomhet rolig.', en:'Read this sign together with the road situation: {name}. Notice the shape, colour, symbol, and what the driver must do now. Use the sign to adapt speed, position, and attention calmly.'},
  close:       {th:'ปิด',                   no:'Lukk',             en:'Close'},
  upgrade:     {th:'อัปเกรด',               no:'Oppgrader',        en:'Upgrade'},
  related_signs:{th:'ป้ายที่เกี่ยวข้อง',      no:'Relaterte skilt',  en:'Related signs'},
  often_confused:{th:'มักสับสนกับ',          no:'Ofte forvekslet med', en:'Often confused with'},
  no_related_signs:{th:'ไม่มีป้ายใกล้เคียงในกลุ่มนี้', no:'Ingen nærliggende skilt i denne gruppen.', en:'No nearby signs in this group.'},
  signs_intro: {th:'แตะที่ป้ายใดก็ได้เพื่อดูความหมาย เหตุที่ต้องรู้ และเคล็ดลับจำง่าย', no:'Trykk på et skilt for å se betydning, viktighet og husketriks.', en:'Tap any sign to see its meaning, why it matters, and how to remember it.'},
  sign_fallback_meaning:{th:'ดูรูปทรง สี และสัญลักษณ์ของป้าย แล้วเชื่อมกับสถานการณ์บนถนนจริง', no:'Les form, farge og symbol, og koble skiltet til situasjonen på veien.', en:'Read the shape, colour, and symbol, and connect the sign to the road situation.'},
  sign_fallback_driver:{th:'ผู้ขับขี่ต้องปรับความเร็ว ตำแหน่ง และความสนใจตามสิ่งที่ป้ายบอก', no:'Føreren må tilpasse fart, plassering og oppmerksomhet etter det skiltet forteller.', en:'The driver must adapt speed, position, and attention to what the sign tells you.'},
  sign_fallback_mistake:{th:'ข้อผิดพลาดที่พบบ่อยคือดูป้ายแยกจากถนน ไม่ดูป้ายเสริมหรือบริบท', no:'Vanlig feil er å lese skiltet isolert, uten underskilt og trafikksituasjonen rundt.', en:'A common mistake is reading the sign in isolation, without supplementary signs and context.'},
  sign_fallback_exam:{th:'ในข้อสอบ ให้ถามว่า: ป้ายนี้เปลี่ยนการกระทำของฉันตรงนี้อย่างไร?', no:'På prøven: spør hva skiltet endrer for handlingen din akkurat her.', en:'In the exam, ask what this sign changes about your action right here.'},
  sign_fallback_memory:{th:'จำเป็นลำดับ: รูปทรง → สี → สัญลักษณ์ → สิ่งที่ต้องทำ', no:'Husk rekkefølgen: form → farge → symbol → handling.', en:'Remember the order: shape → colour → symbol → action.'},
  // Paywall
  pw_title:    {th:'ปลดล็อก Thai2Drive Premium', no:'Lås opp Thai2Drive Premium', en:'Unlock Thai2Drive Premium'},
  pw_sub:      {th:'คุณใช้ 5 คำถามฟรีแล้ว อัปเกรดเพื่อใช้งานไม่จำกัด!', no:'Du har brukt 5 gratis spørsmål. Oppgrader for ubegrenset tilgang!', en:'You have used 5 free questions. Upgrade for unlimited access!'},
  pw_f1:       {th:'คำถามและหมวดหมู่ไม่จำกัด', no:'Ubegrenset spørsmål og kategorier', en:'Unlimited questions and categories'},
  pw_f2:       {th:'โหมดสอบเต็มรูปแบบ (45 ข้อ)', no:'Fullstendig eksamensmode (45 spørsmål)', en:'Full exam mode (45 questions)'},
  pw_f3:       {th:'ทดสอบรายวันและโหมดฝึกซ้อม', no:'Daglig test og øvingsmodus', en:'Daily test and practice mode'},
  pw_f4:       {th:'ประวัติและสถิติความก้าวหน้า', no:'Historikk og fremgangsstatistikk', en:'History and progress statistics'},
  pw_f5:       {th:'แกลเลอรีป้ายจราจร', no:'Trafikkskilt-galleri', en:'Traffic signs gallery'},
  pw_month:    {th:'รายเดือน', no:'Månedlig', en:'Monthly'},
  pw_three_months:{th:'3 เดือน', no:'3 måneder', en:'3 months'},
  pw_lifetime: {th:'ตลอดชีพ', no:'Livstid', en:'Lifetime'},
  pw_per_month:{th:'ต่อเดือน', no:'per måned', en:'per month'},
  pw_per_three_months:{th:'ต่อ 3 เดือน', no:'per 3 måneder', en:'per 3 months'},
  pw_per_lifetime:{th:'จ่ายครั้งเดียว', no:'engangsbetaling', en:'one-time payment'},
  pw_best_value:{th:'คุ้มที่สุด', no:'Best verdi', en:'Best value'},
  pw_buy:      {th:'ซื้อ Premium', no:'Kjøp Premium', en:'Buy Premium'},
  pw_skip:     {th:'ใช้ต่อแบบฟรี', no:'Fortsett gratis', en:'Continue free'},
  // Auth
  auth_login_tab:  {th:'เข้าสู่ระบบ',    no:'Logg inn',      en:'Log in'},
  auth_reg_tab:    {th:'ลงทะเบียน',      no:'Registrer',     en:'Register'},
  auth_label_name: {th:'ชื่อ',           no:'Navn',          en:'Name'},
  auth_label_email:{th:'อีเมล',          no:'E-post',        en:'Email'},
  auth_label_pass: {th:'รหัสผ่าน',       no:'Passord',       en:'Password'},
  auth_name_ph:    {th:'ชื่อเต็มของคุณ', no:'Ditt fulle navn', en:'Your full name'},
  auth_pass_ph:    {th:'อย่างน้อย 6 ตัวอักษร', no:'Minst 6 tegn', en:'At least 6 characters'},
  auth_forgot_btn: {th:'ส่งลิงก์รีเซ็ต', no:'Send tilbakestillingslenke', en:'Send reset link'},
  auth_forgot_link:{th:'ลืมรหัสผ่าน?',  no:'Glemt passord?', en:'Forgot password?'},
  auth_back:       {th:'← กลับ',        no:'← Tilbake',     en:'← Back'},
  auth_login_btn:  {th:'เข้าสู่ระบบ',    no:'Logg inn',      en:'Log in'},
  auth_reg_btn:    {th:'สร้างบัญชี',     no:'Opprett konto', en:'Create account'},
  auth_sending:    {th:'กำลังส่ง…',      no:'Sender…',       en:'Sending…'},
  auth_email_sent: {th:'ส่งอีเมลแล้ว! ตรวจสอบกล่องขาเข้า 📧', no:'E-post sendt! Sjekk innboksen din 📧', en:'Email sent! Check your inbox 📧'},
  auth_fill_email: {th:'กรุณากรอกอีเมล', no:'Fyll inn e-postadressen din', en:'Please enter your email address'},
  auth_logout_confirm:{th:'แน่ใจหรือว่าต้องการออกจากระบบ?', no:'Er du sikker på at du vil logge ut?', en:'Are you sure you want to log out?'},
  // Studiebok
  sb_prev:         {th:'‹ ก่อนหน้า',    no:'‹ Forrige',     en:'‹ Previous'},
  sb_next:         {th:'ถัดไป ›',        no:'Neste ›',       en:'Next ›'},
  sb_search_ph:    {th:'ค้นหาหรือหมายเลข §...', no:'Søk eller § nummer...', en:'Search or § number...'},
  sb_nav:          {th:'Studiebok',      no:'Studiebok',     en:'Study Book'},
  sb_home_btn:     {th:'📖 Studiebok — กฎจราจรนอร์เวย์', no:'📖 Studiebok — Norsk trafikk', en:'📖 Study Book — Norwegian traffic'},
  sb_cancel:       {th:'ยกเลิก',         no:'Avbryt',        en:'Cancel'},
  sb_save:         {th:'บันทึก',         no:'Lagre',         en:'Save'},
};

function t(key) { return (UI[key] && (UI[key][appLang] || UI[key]['th'] || UI[key]['en'] || UI[key]['no'])) || key; }
function tf(key, vars) {
  var s = t(key);
  Object.keys(vars || {}).forEach(function(k) {
    s = s.replace(new RegExp('\\{' + k + '\\}', 'g'), vars[k]);
  });
  return s;
}
function modeLabel(mode) {
  var labels = {exam:t('mode_exam'), category:t('mode_category'), daily:t('mode_daily'), random:t('mode_random')};
  return labels[mode] || mode || 'Quiz';
}
function readinessForPct(pct, compact) {
  if (pct >= 80) return {cls:'good', text:(compact ? '✓ ' : '') + t('ready_test'), color:'var(--green)'};
  if (pct >= 60) return {cls:'ok', text:(compact ? '▲ ' : '') + t('almost_ready'), color:'var(--orange)'};
  return {cls:'bad', text:(compact ? '↺ ' : '') + t('practice_more'), color:'#EF4444'};
}
function localeForLang() {
  return appLang === 'th' ? 'th-TH' : appLang === 'en' ? 'en-US' : 'nb-NO';
}

function applyUILang() {
  // Generic text and placeholders first, so every visible static label follows appLang.
  document.querySelectorAll('[data-key]').forEach(function(el) {
    var key = el.getAttribute('data-key');
    var val = t(key);
    if (val) el.textContent = val;
  });
  document.querySelectorAll('[data-placeholder-key]').forEach(function(el) {
    var key = el.getAttribute('data-placeholder-key');
    var val = t(key);
    if (val) el.setAttribute('placeholder', val);
  });
  // back buttons
  document.querySelectorAll('.back-btn').forEach(function(b){ b.textContent = t('back'); });
  // bottom nav
  var nb = document.getElementById('bnHome');      if(nb) nb.innerHTML = '<span class="bn-icon">🏠</span>' + t('home');
  var nc = document.getElementById('bnCats');      if(nc) nc.innerHTML = '<span class="bn-icon">📚</span>' + t('cats');
  var nh = document.getElementById('bnHistory');   if(nh) nh.innerHTML = '<span class="bn-icon">📊</span>' + t('history');
  var nsg= document.getElementById('bnSigns');     if(nsg) nsg.innerHTML = '<span class="bn-icon">🪧</span>' + t('signs');
  var nbm= document.getElementById('bnBookmarks'); if(nbm) nbm.innerHTML = '<span class="bn-icon">🔖</span>' + t('bookmarks');
  var ns = document.getElementById('bnSettings');  if(ns) ns.innerHTML = '<span class="bn-icon">⚙️</span>' + t('settings');
  var nt = document.getElementById('bnTeacher');   if(nt) nt.innerHTML = '<span class="bn-icon">🚗</span>' + t('teacher');
  var nsb= document.getElementById('bnStudybook'); if(nsb) nsb.innerHTML = '<span class="bn-icon">📖</span>' + t('sb_nav');
  // Update teacher UI if visible
  var tNameEl = document.getElementById('teacherNameLbl');
  if (tNameEl) tNameEl.textContent = t('teacher_name');
  var tInput = document.getElementById('teacherInput');
  if (tInput) tInput.placeholder = t('teacher_placeholder');
  var tSub = document.getElementById('michaelCardSub');
  if (tSub) tSub.textContent = t('teacher_sub');
  // Side panel labels
  var tspTitle = document.getElementById('tspTitle');
  if (tspTitle) tspTitle.textContent = t('tsp_title');
  var tspMap = { sign:'tsp_sign', vikeplikt:'tsp_vikeplikt', rule:'tsp_rule', practice:'tsp_practice', theory:'tsp_theory', app:'tsp_app' };
  document.querySelectorAll('[data-tsp]').forEach(function(el) {
    var key = tspMap[el.getAttribute('data-tsp')];
    if (key) el.textContent = t(key);
  });
  // Update suggestion chip labels
  document.querySelectorAll('.teacher-chip').forEach(function(chip) {
    var lbl = chip.querySelector('.chip-lbl');
    if (!lbl) return;
    var msgKey = 'data-msg-' + appLang;
    var msg = chip.getAttribute(msgKey) || chip.getAttribute('data-msg-no') || '';
    // Strip leading emoji + space for label display
    lbl.textContent = msg.replace(/^[\u{1F000}-\u{1FFFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\uD800-\uDFFF❓📊📝📖🚗🛑]+\s*/u, '');
    chip.dataset.msg = msg;
  });
  // cats header — update title text without disturbing the count span
  var catsTitleEl = document.querySelector('#screenCats .screen-title');
  if (catsTitleEl) {
    var catsCountEl = document.getElementById('catCount');
    var catsCountText = catsCountEl ? catsCountEl.textContent : '';
    catsTitleEl.innerHTML = '📚 <span data-key="cats">' + t('cats') + '</span> <span id="catCount">' + catsCountText + '</span>';
  }
  // home buttons
  document.querySelectorAll('.home-cta').forEach(function(b){ b.innerHTML = t('startquiz').replace(/^▶\s*/,'▶&nbsp;&nbsp;'); });
  document.querySelectorAll('.home-sec-btn').forEach(function(b,i){
    if (i===0) b.textContent = t('exam');
    else if (i===1) b.textContent = t('daily');
    else if (i===2) b.textContent = t('studybook_home');
  });
  var sbSearch = document.getElementById('sbSearchInput');
  if (sbSearch) sbSearch.placeholder = t('studybook_search_placeholder');
  var sbPrev = document.getElementById('sbPrevBtn');
  if (sbPrev) sbPrev.textContent = t('studybook_prev');
  var sbNext = document.getElementById('sbNextBtn');
  if (sbNext) sbNext.textContent = t('studybook_next');
  var sbInfo = document.getElementById('sbNavInfo');
  if (sbInfo && (!_sbLoaded || !_sbChapters.length)) sbInfo.textContent = t('studybook_loading');
  if (sbInfo && _sbLoaded && _sbChapters.length) sbRender();
  // end screen buttons
  var er = document.querySelector('.end-btn-pri'); if(er) er.innerHTML = t('retry');
  var endSecBtns = document.querySelectorAll('.end-btn-sec');
  if (endSecBtns[0]) endSecBtns[0].innerHTML = t('backhome');
  if (endSecBtns[1]) endSecBtns[1].innerHTML = t('pickcat');
  // next buttons
  document.querySelectorAll('#qNextBig,#qNextMobile').forEach(function(b){ b.textContent = t('next'); });
  var spPractice = document.querySelector('.sp-btn-primary');
  if (spPractice) spPractice.textContent = t('practice_this_sign');
  var spAudio = document.querySelector('.sp-btn-sm-audio span');
  if (spAudio) spAudio.textContent = t('read_aloud');
  var spAi = document.querySelector('.sp-btn-sm-ai span');
  if (spAi) spAi.textContent = t('ask_ai');
  var spBm = document.querySelector('.sp-btn-sm-bm span');
  var hpRetry = document.getElementById('hpRetryBtn');
  if (hpRetry) hpRetry.textContent = t('retry');
  var hpClose = document.querySelector('.hp-actions .hp-btn-sec');
  if (hpClose) hpClose.textContent = t('close');
  // progress label
  var pl = document.getElementById('qProgLbl');
  if(pl && pl.textContent) {
    var m = pl.textContent.match(/(\d+)[^\d]+(\d+)/);
    if(m) pl.textContent = t('question') + ' ' + m[1] + ' ' + t('of') + ' ' + m[2];
  }
  // feedback
  var fb = document.getElementById('qFeedback');
  if(fb && fb.classList.contains('ok'))  fb.textContent = t('correct');
  if(fb && fb.classList.contains('bad')) fb.textContent = t('wrong');
  // Home stat labels
  document.querySelectorAll('.home-stat-lbl').forEach(function(el,i){
    el.textContent = [t('answered'), t('correct_stat'), t('accuracy')][i] || el.textContent;
  });
  // Premium banner
  var pb = document.getElementById('homePremiumBanner');
  if(pb) { var ptitle = pb.querySelector('.pb-title'); var psub = pb.querySelector('.pb-sub'); if(ptitle) ptitle.textContent = t('premium_on'); if(psub) psub.textContent = t('premium_sub'); }
  if (spBm && _signPanelData) spBm.textContent = _signFavorites.indexOf(_signPanelData.id) >= 0 ? t('saved') : t('save');
  var aiStatus = document.getElementById('quizAiStatus');
  if (aiStatus && aiStatus.classList.contains('idle')) aiStatus.textContent = t('ai_waiting');
  var aiBadge = document.getElementById('quizAiImgBadge');
  if (aiBadge && !qAnswered) aiBadge.textContent = t('traffic_situation');
  renderPremiumPricing();
}
var catsLoaded = false;
var bookmarkedIds = {};

var CAT_ICONS = {
  'Trafikkregler':'🚦','Skilt':'🪧','Vikeplikt':'⚠️','Kjøretøy':'🚗',
  'Farlig gods':'☣️','Miljø':'🌿','Ulykker':'🚨','Alkohol':'🍺',
  'Bremser':'🛑','Parkering':'🅿️','Lys':'💡','Dekk':'🔄',
  'Motorvei':'🛣️','Kryss':'✛','Gangfelt':'🚶','Sving':'↩️',
  'Forbikjøring':'🏎️','Lastsikring':'📦','Sikkerhet':'🦺','Fellesskjøring':'🤝',
  'Road Rules':'🚦','Traffic Rules':'📋','Traffic Signs':'🪧',
  'Right of Way':'⚠️','Driving Conditions':'🌧️','Road Conditions':'🛣️',
  'Speed Limits':'⏱️','Safety':'🦺','Situations':'🔄','Parking':'🅿️',
  'Lights':'💡','Tires':'🔄','Overtaking':'🏎️','Intersections':'✛',
  'Pedestrians':'🚶','Alcohol':'🍺','Environment':'🌿','Vehicle':'🚗',
  'Accidents':'🚨','Highway':'🛣️'
};

// Kategori navn per språk
var CAT_NAMES = {
  'Road Rules':       {no:'Trafikkregler',   th:'กฎจราจร',          en:'Road Rules'},
  'Traffic Rules':    {no:'Trafikklovgiving', th:'กฎหมายจราจร',      en:'Traffic Rules'},
  'Traffic Signs':    {no:'Trafikkskilt',    th:'ป้ายจราจร',         en:'Traffic Signs'},
  'Right of Way':     {no:'Vikeplikt',       th:'การให้ทาง',         en:'Right of Way'},
  'Driving Conditions':{no:'Kjøreforhold',  th:'สภาพการขับขี่',      en:'Driving Conditions'},
  'Road Conditions':  {no:'Veiforhold',      th:'สภาพถนน',           en:'Road Conditions'},
  'Speed Limits':     {no:'Fartsgrenser',    th:'ขีดจำกัดความเร็ว',   en:'Speed Limits'},
  'Safety':           {no:'Sikkerhet',       th:'ความปลอดภัย',        en:'Safety'},
  'Situations':       {no:'Situasjoner',     th:'สถานการณ์',          en:'Situations'},
  'Parking':          {no:'Parkering',       th:'การจอดรถ',           en:'Parking'},
  'Lights':           {no:'Lys',             th:'ไฟรถ',              en:'Lights'},
  'Tires':            {no:'Dekk',            th:'ยางรถ',              en:'Tires'},
  'Overtaking':       {no:'Forbikjøring',    th:'การแซง',             en:'Overtaking'},
  'Intersections':    {no:'Kryss',           th:'ทางแยก',             en:'Intersections'},
  'Pedestrians':      {no:'Gangfelt',        th:'คนเดินเท้า',          en:'Pedestrians'},
  'Alcohol':          {no:'Alkohol',         th:'แอลกอฮอล์',          en:'Alcohol'},
  'Environment':      {no:'Miljø',           th:'สิ่งแวดล้อม',         en:'Environment'},
  'Vehicle':          {no:'Kjøretøy',        th:'ยานพาหนะ',           en:'Vehicle'},
  'Accidents':        {no:'Ulykker',         th:'อุบัติเหตุ',           en:'Accidents'},
  'Highway':          {no:'Motorvei',        th:'ทางด่วน',             en:'Highway'}
};
// legacy
var CAT_NO = {};
Object.keys(CAT_NAMES).forEach(function(k){ CAT_NO[k] = CAT_NAMES[k].no; });

function catName(raw) {
  var entry = CAT_NAMES[raw];
  if (!entry) return raw;
  return entry[appLang] || entry['no'] || raw;
}

var PREMIUM_PRICING = {
  monthly: { display:'99 kr', period:{no:'per måned', th:'ต่อเดือน', en:'per month'} },
  three_months: { display:'299 kr', period:{no:'per 3 måneder', th:'ต่อ 3 เดือน', en:'per 3 months'} },
  lifetime: { display:'699 kr', period:{no:'engangsbetaling', th:'จ่ายครั้งเดียว', en:'one-time payment'} }
};

// ════════════════════════════════════════════
//  INIT
// ════════════════════════════════════════════
(async function init() {
  applyThemeFromStorage();
  applyUILang();
  loadPremiumPricing();
  // Init top bar language buttons
  ['TH','NO','EN'].forEach(function(l) {
    var topBtn = document.getElementById('topLang' + l);
    if (topBtn) topBtn.classList.toggle('active', appLang === l.toLowerCase());
  });
  if (token) {
    try {
      user = await api('GET', '/api/auth/me');
      deviceId = user._id || user.id || null;
      await handleCheckoutReturn();
      enterApp();
    } catch(e) {
      _ls.remove('t2d_token');
      token = null;
      showScreen('screenAuth');
    }
  } else {
    showScreen('screenAuth');
  }
})();

// ════════════════════════════════════════════
//  SCREEN & TAB MANAGEMENT
// ════════════════════════════════════════════
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(function(s) { s.classList.remove('active'); });
  var el = document.getElementById(id);
  if (el) el.classList.add('active');
  // Toggle quiz-mode on #app: expands the phone frame to AI dashboard width on desktop
  document.getElementById('app').classList.toggle('quiz-mode', id === 'screenQuiz');
  document.getElementById('app').classList.toggle('teacher-mode', id === 'screenTeacher');
}

function enterApp() {
  document.getElementById('topBar').style.display = 'flex';
  document.getElementById('bottomNav').style.display = 'flex';
  loadAccessStatus();
  showTab('home');
}

function showTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.bn-tab').forEach(function(b) { b.classList.remove('active'); });
  var tabMap = { home:'bnHome', cats:'bnCats', history:'bnHistory', signs:'bnSigns', studybook:'bnStudybook', bookmarks:'bnBookmarks', settings:'bnSettings', teacher:'bnTeacher' };
  if (tabMap[tab]) document.getElementById(tabMap[tab]).classList.add('active');
  var screenMap = {
    home:'screenHome', cats:'screenCats',
    history:'screenHistory', signs:'screenSigns', bookmarks:'screenBookmarks',
    settings:'screenSettings', studybook:'screenStudybook', teacher:'screenTeacher'
  };
  if (screenMap[tab]) {
    // Premium-only tabs
    var premiumTabs = ['history', 'signs', 'bookmarks'];
    if (premiumTabs.indexOf(tab) !== -1 && !isPremium()) {
      showPaywall();
      return;
    }
    showScreen(screenMap[tab]);
    if (tab === 'home')      loadHome();
    if (tab === 'cats')      loadCategories();
    if (tab === 'history')   loadHistory();
    if (tab === 'signs')     loadSigns();
    if (tab === 'bookmarks') loadBookmarks();
    if (tab === 'settings')  loadSettings();
    if (tab === 'studybook') loadStudiebok();
    if (tab === 'teacher')   loadTeacher();
  }
}

function toggleChapter(id) {
  var ch = document.getElementById(id);
  if (ch) ch.classList.toggle('open');
}

// ════════════════════════════════════════════
//  STUDIEBOK — BOK-MODUS
// ════════════════════════════════════════════
var _sbChapters   = [];
var _sbCurrent    = 0;   // index (0-based)
var _sbLoaded     = false;
var _sbEditOrder  = null;
var _sbVisited    = {};

async function loadStudiebok() {
  var reader = document.getElementById('sbReader');
  if (!reader) return;
  if (_sbLoaded && _sbChapters.length) { sbRender(); return; }
  reader.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    _sbChapters = await api('GET', '/api/studiebok');
    _sbLoaded = true;
    sbBuildDots();
    sbGoTo(0);
  } catch(e) {
    reader.innerHTML = '<div style="padding:24px;text-align:center;color:var(--muted);">' + t('studybook_load_error') + '</div>';
  }
}

function sbBuildDots() {
  var wrap = document.getElementById('sbProgress');
  if (!wrap) return;
  wrap.innerHTML = '';
  _sbChapters.forEach(function(ch, i) {
    var d = document.createElement('div');
    d.className = 'sb-dot' + (i === _sbCurrent ? ' active' : '');
    d.title = ch.title_no;
    d.onclick = function() { sbGoTo(i); };
    wrap.appendChild(d);
  });
}

function sbGoTo(idx) {
  if (idx < 0 || idx >= _sbChapters.length) return;
  _sbCurrent = idx;
  _sbVisited[idx] = true;
  sbRender();
  sbCloseSuggest();
  // scroll reader to top
  var r = document.getElementById('sbReader');
  if (r) r.scrollTop = 0;
  // clear search
  var inp = document.getElementById('sbSearchInput');
  if (inp) inp.value = '';
}

function sbRender() {
  var ch = _sbChapters[_sbCurrent];
  if (!ch) return;
  var total = _sbChapters.length;

  // Nav info
  var info = document.getElementById('sbNavInfo');
  if (info) info.textContent = ch.title_no.split('—')[0].trim() + '  ·  ' + (_sbCurrent + 1) + ' / ' + total;

  // Prev / Next buttons
  var prev = document.getElementById('sbPrevBtn');
  var next = document.getElementById('sbNextBtn');
  if (prev) prev.disabled = (_sbCurrent === 0);
  if (next) next.disabled = (_sbCurrent === total - 1);

  // Dots
  var dots = document.querySelectorAll('.sb-dot');
  dots.forEach(function(d, i) {
    d.className = 'sb-dot' + (i === _sbCurrent ? ' active' : (_sbVisited[i] ? ' visited' : ''));
  });

  // Edit button (admin only)
  var editBtn = (user && user.is_admin)
    ? '<button class="sb-edit-btn" onclick="openStudiebokModal(' + ch.order + ')" title="Rediger">✏️</button>'
    : '';

  var imgHtml = ch.image_url ? '<img src="' + ch.image_url + '" class="study-img" alt="">' : '';

  var reader = document.getElementById('sbReader');
  reader.innerHTML =
    '<div class="sb-page">' +
      editBtn +
      '<div class="sb-page-icon">' + ch.icon + '</div>' +
      '<div class="sb-page-title">' + ch.title_no + '</div>' +
      '<div class="sb-page-body">' + imgHtml + ch.content_no + '</div>' +
    '</div>';
}

// Search
function sbSearch(q) {
  var box = document.getElementById('sbSearchResults');
  q = q.trim();
  if (!q || !_sbChapters.length) { box.style.display = 'none'; return; }

  // Try §-number first: "3", "§3", "§ 3"
  var num = parseInt(q.replace(/[§\s]/g, ''));
  var matches = [];

  if (!isNaN(num)) {
    matches = _sbChapters.filter(function(ch) { return ch.order === num; });
  }
  if (!matches.length) {
    var lq = q.toLowerCase();
    matches = _sbChapters.filter(function(ch) {
      return ch.title_no.toLowerCase().includes(lq) ||
             ch.content_no.toLowerCase().replace(/<[^>]+>/g,'').includes(lq);
    });
  }

  if (!matches.length) {
    box.innerHTML = '<div class="sb-result-item" style="color:var(--muted)">' + t('studybook_no_results') + '</div>';
    box.style.display = 'block'; return;
  }

  box.innerHTML = matches.slice(0, 6).map(function(ch) {
    var plain = ch.content_no.replace(/<[^>]+>/g,'').substring(0, 80) + '…';
    return '<div class="sb-result-item" onclick="sbGoTo(' + (_sbChapters.indexOf(ch)) + ')">' +
           '<span class="sb-result-icon">' + ch.icon + '</span>' +
           '<div><div class="sb-result-title">' + ch.title_no + '</div>' +
           '<div class="sb-result-preview">' + plain + '</div></div>' +
           '</div>';
  }).join('');
  box.style.display = 'block';
}

function sbCloseSuggest() {
  var box = document.getElementById('sbSearchResults');
  if (box) box.style.display = 'none';
}

// Close search on outside click
document.addEventListener('click', function(e) {
  if (!e.target.closest('.sb-search-wrap') && !e.target.closest('.sb-search-results')) {
    sbCloseSuggest();
  }
});

// Swipe left/right on reader
(function() {
  var sx = 0;
  document.addEventListener('touchstart', function(e) {
    var r = document.getElementById('sbReader');
    if (r && r.contains(e.target)) sx = e.touches[0].clientX;
  }, {passive:true});
  document.addEventListener('touchend', function(e) {
    var r = document.getElementById('sbReader');
    if (!r || !r.contains(e.target)) return;
    var dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 50) { if (dx < 0) sbGoTo(_sbCurrent + 1); else sbGoTo(_sbCurrent - 1); }
  }, {passive:true});
})();

function openStudiebokModal(order) {
  var ch = _sbChapters.find(function(c) { return c.order === order; });
  if (!ch) return;
  _sbEditOrder = order;
  document.getElementById('sbEditTitle').value    = ch.title_no;
  document.getElementById('sbEditContent').value  = ch.content_no;
  document.getElementById('sbEditImageUrl').value = ch.image_url || '';
  document.getElementById('sbEditVideoUrl').value = ch.video_url || '';
  document.getElementById('studiebokEditModal').style.display = 'flex';
}

function closeStudiebokModal() {
  document.getElementById('studiebokEditModal').style.display = 'none';
  _sbEditOrder = null;
}

async function saveStudiebokChapter() {
  if (!_sbEditOrder) return;
  var title_no   = document.getElementById('sbEditTitle').value.trim();
  var content_no = document.getElementById('sbEditContent').value.trim();
  var image_url  = document.getElementById('sbEditImageUrl').value.trim();
  var video_url  = document.getElementById('sbEditVideoUrl').value.trim();
  if (!title_no || !content_no) { toast(t('sb_empty_fields')); return; }
  try {
    await api('PUT', '/api/studiebok/' + _sbEditOrder, { title_no, content_no, image_url, video_url });
    // Update local cache
    var idx = _sbChapters.findIndex(function(c) { return c.order === _sbEditOrder; });
    if (idx >= 0) { _sbChapters[idx].title_no = title_no; _sbChapters[idx].content_no = content_no; _sbChapters[idx].image_url = image_url; _sbChapters[idx].video_url = video_url; }
    closeStudiebokModal();
    sbRender();
    toast('Kapittel lagret');
  } catch(e) {
    toast('Feil: ' + e.message);
  }
}

// ════════════════════════════════════════════
//  API HELPER
// ════════════════════════════════════════════
async function api(method, url, body) {
  var opts = { method: method, headers: { 'Content-Type': 'application/json' }, cache: 'no-store' };
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  var r = await fetch(url, opts);
  var data = await r.json().catch(function() { return {}; });
  if (!r.ok) {
    var det = data.detail;
    var msg;
    if (typeof det === 'string') {
      msg = t(det) !== det ? t(det) : det;
    } else if (det && typeof det === 'object' && !Array.isArray(det)) {
      msg = (det[appLang] || (det.key ? t(det.key) : '') || det.no || det.en || det.th || JSON.stringify(det));
    } else if (Array.isArray(det)) {
      msg = det.map(function(d){return d.msg||d;}).join(', ');
    } else {
      msg = 'Noe gikk galt';
    }
    var err = new Error(msg);
    err.status = r.status;
    err.data = data;
    throw err;
  }
  return data;
}

async function loadPremiumPricing() {
  try {
    var data = await api('GET', '/api/pricing?_=' + Date.now());
    (data.plans || []).forEach(function(plan) {
      if (plan && plan.id) PREMIUM_PRICING[plan.id] = plan;
    });
  } catch(e) {
    console.warn('[pricing] using local fallback', e && e.message ? e.message : e);
  }
  renderPremiumPricing();
}

async function refreshCurrentUser() {
  if (!token) return null;
  user = await api('GET', '/api/auth/me');
  await loadAccessStatus();
  return user;
}

async function handleCheckoutReturn() {
  var params = new URLSearchParams(window.location.search || '');
  var sessionId = params.get('session_id');
  if (params.get('checkout') !== 'success' || !sessionId || !token) return false;
  try {
    var status = await api('GET', '/api/checkout/status?session_id=' + encodeURIComponent(sessionId));
    await refreshCurrentUser();
    if (status && status.is_premium) {
      toast({th:'เปิดใช้ Premium แล้ว', no:'Premium er aktivert', en:'Premium activated'}[appLang] || 'Premium activated', 4500);
    }
  } catch(e) {
    toast(({th:'ยังยืนยันการชำระเงินไม่ได้', no:'Betalingen kunne ikke bekreftes ennå', en:'Payment could not be confirmed yet'}[appLang] || 'Payment could not be confirmed yet'), 5000);
  }
  window.history.replaceState({}, '', window.location.pathname);
  return true;
}

function renderPremiumPricing() {
  Object.keys(PREMIUM_PRICING || {}).forEach(function(planId) {
    var plan = PREMIUM_PRICING[planId] || {};
    var priceEl = document.querySelector('[data-price-plan="' + planId + '"]');
    if (priceEl && plan.display) priceEl.textContent = plan.display;
    var card = document.querySelector('[data-plan="' + planId + '"]');
    var periodEl = card ? card.querySelector('.ppc-per') : null;
    if (periodEl && plan.period) {
      periodEl.textContent = plan.period[appLang] || plan.period.no || plan.period.en || periodEl.textContent;
    }
  });
}

// ════════════════════════════════════════════
//  TOAST
// ════════════════════════════════════════════
var toastTimer;
function toast(msg, dur) {
  dur = dur || 2800;
  var el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function() { el.classList.remove('show'); }, dur);
}

// ════════════════════════════════════════════
//  AUTH
// ════════════════════════════════════════════
function switchTab(tab) {
  clearAuthMessages();
  document.querySelectorAll('.auth-tab').forEach(function(t, i) {
    t.classList.toggle('active', (i===0 && tab==='login') || (i===1 && tab==='register'));
  });
  document.getElementById('formLogin').style.display    = tab === 'login'    ? 'block' : 'none';
  document.getElementById('formRegister').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('formForgot').style.display   = tab === 'forgot'   ? 'block' : 'none';
  document.getElementById('formReset').style.display    = tab === 'reset'    ? 'block' : 'none';
  if (tab === 'reset') {
    var instr = document.getElementById('resetInstructions');
    if (instr) instr.textContent = t('reset_instructions');
  }
}
function showForgot() {
  clearAuthMessages();
  document.getElementById('formLogin').style.display = 'none';
  document.getElementById('formForgot').style.display = 'block';
  document.getElementById('formReset').style.display = 'none';
  document.querySelectorAll('.auth-tab').forEach(function(t) { t.classList.remove('active'); });
}
function togglePw(btn) {
  var inp = btn.previousElementSibling;
  if (!inp) return;
  var show = inp.type === 'password';
  inp.type = show ? 'text' : 'password';
  btn.textContent = show ? '🙈' : '👁';
  var lbl = appLang === 'th' ? 'แสดง/ซ่อนรหัสผ่าน' : appLang === 'en' ? 'Show/hide password' : 'Vis/skjul passord';
  btn.setAttribute('title', lbl);
  btn.setAttribute('aria-label', lbl);
}

function showAuthError(msg) {
  var el = document.getElementById('authError');
  el.textContent = msg; el.classList.add('show');
  document.getElementById('authSuccess').classList.remove('show');
}
function showAuthSuccess(msg) {
  var el = document.getElementById('authSuccess');
  el.textContent = msg; el.classList.add('show');
  document.getElementById('authError').classList.remove('show');
}
function clearAuthMessages() {
  document.getElementById('authError').classList.remove('show');
  document.getElementById('authSuccess').classList.remove('show');
}

async function doLogin() {
  clearAuthMessages();
  var email = document.getElementById('loginEmail').value.trim();
  var pass  = document.getElementById('loginPass').value;
  if (!email || !pass) return showAuthError(t('auth_missing_login'));
  var btn = document.querySelector('#formLogin .auth-btn');
  btn.disabled = true; btn.textContent = t('login_loading');
  try {
    var r = await api('POST', '/api/auth/login', { email: email, password: pass });
    token = r.token; user = r.user;
    deviceId = user._id || user.id || null;
    _ls.set('t2d_token', token);
    enterApp();
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = t('login');
  }
}

async function doRegister() {
  clearAuthMessages();
  var name  = document.getElementById('regName').value.trim();
  var email = document.getElementById('regEmail').value.trim();
  var pass  = document.getElementById('regPass').value;
  if (!name || !email || !pass) return showAuthError(t('auth_missing_all'));
  if (pass.length < 6) return showAuthError(t('auth_password_short'));
  var btn = document.querySelector('#formRegister .auth-btn');
  btn.disabled = true; btn.textContent = t('register_loading');
  try {
    var r = await api('POST', '/api/auth/signup', { name: name, email: email, password: pass });
    token = r.token; user = r.user;
    deviceId = user._id || user.id || null;
    _ls.set('t2d_token', token);
    enterApp();
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = t('create_account');
  }
}

async function doForgot() {
  clearAuthMessages();
  var email = document.getElementById('forgotEmail').value.trim();
  if (!email) return showAuthError(t('auth_missing_email'));
  var btn = document.getElementById('forgotSubmitBtn') || document.querySelector('#formForgot .auth-btn');
  btn.disabled = true; btn.textContent = t('reset_sending');
  try {
    await api('POST', '/api/auth/forgot-password', { email: email });
    // Store the email so doResetPassword() can use it
    window._resetEmail = email;
    // Show the code-entry form
    switchTab('reset');
    showAuthSuccess(t('auth_reset_sent'));
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = t('send_reset');
  }
  btn.disabled = false; btn.textContent = t('send_reset');
}

async function doResetPassword() {
  clearAuthMessages();
  var code = (document.getElementById('resetCode').value || '').trim();
  var newPass = document.getElementById('resetNewPass').value;
  var email = window._resetEmail || '';
  if (!code || !newPass) return showAuthError(t('reset_fill'));
  if (newPass.length < 6) return showAuthError(t('reset_pass_short'));
  if (!email) return showAuthError(t('auth_missing_email'));
  var btn = document.getElementById('resetSubmitBtn');
  btn.disabled = true; btn.textContent = t('reset_submitting');
  try {
    await api('POST', '/api/auth/reset-password', { email: email, code: code, new_password: newPass });
    showAuthSuccess(t('reset_success'));
    window._resetEmail = null;
    setTimeout(function() { switchTab('login'); }, 2000);
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = t('reset_submit');
  }
}

function logout() {
  if (!confirm(t('logout_confirm'))) return;
  _ls.remove('t2d_token');
  token = null; user = null; deviceId = null;
  document.getElementById('topBar').style.display = 'none';
  document.getElementById('bottomNav').style.display = 'none';
  catsLoaded = false;
  showScreen('screenAuth');
  switchTab('login');
}

// ════════════════════════════════════════════
//  HOME
// ════════════════════════════════════════════
async function loadHome() {
  // Streak from API
  if (deviceId) {
    try {
      var prog = await api('GET', '/api/progress/' + deviceId);
      var streak = prog.streak || 0;
      document.getElementById('homeStreakNum').textContent = streak;
      document.getElementById('topStreakNum').textContent = streak;
      if (streak > 0) document.getElementById('topStreak').style.display = 'flex';
    } catch(e) {}

    // Stats from API
    try {
      var stats = await api('GET', '/api/stats/me?device_id=' + encodeURIComponent(deviceId));
      var ov = stats.overall || {};
      document.getElementById('homeStatAnswered').textContent = ov.total_q != null ? ov.total_q : '0';
      document.getElementById('homeStatCorrect').textContent  = ov.total_correct != null ? ov.total_correct : '0';
      document.getElementById('homeStatAcc').textContent      = ov.pct != null ? Math.round(ov.pct) + '%' : '0%';
    } catch(e) {
      document.getElementById('homeStatAnswered').textContent = '0';
      document.getElementById('homeStatCorrect').textContent  = '0';
      document.getElementById('homeStatAcc').textContent      = '0%';
    }
  }

  // Readiness card — last quiz attempt
  if (deviceId) {
    try {
      var rdata = await api('GET', '/api/quiz-attempts/' + encodeURIComponent(deviceId) + '?limit=1&_=' + Date.now());
      var rattempts = Array.isArray(rdata) ? rdata : (rdata.attempts || rdata.results || []);
      rattempts = _mergeAttempts(rattempts, _readLocalAttempts().concat(_lastSavedAttempt ? [_lastSavedAttempt] : []));
      if (rattempts.length) {
        var la = rattempts[0];
        var lpct = Math.round(la.score_percentage || 0);
        var ready = readinessForPct(lpct, false);
        var lmode = modeLabel(la.mode);
        if (la.category) lmode += ' — ' + catName(la.category);
        document.getElementById('hrDot').className = 'hr-dot hr-dot-' + ready.cls;
        document.getElementById('hrStatus').textContent = ready.text;
        document.getElementById('hrSub').textContent = lmode;
        document.getElementById('hrPct').textContent = lpct + '%';
        document.getElementById('hrPct').style.color = ready.color;
        document.getElementById('homeReadiness').style.display = 'flex';
      }
    } catch(e) {}
  }

  // Premium badge
  document.getElementById('homePremiumBanner').style.display = (user && user.is_premium) ? 'flex' : 'none';
}

// ════════════════════════════════════════════
//  CATEGORIES
// ════════════════════════════════════════════
async function loadCategories() {
  if (catsLoaded) return;
  var grid = document.getElementById('catGrid');
  grid.innerHTML = '<div class="loading-wrap" style="grid-column:1/-1"><div class="spinner"></div></div>';
  try {
    var cats = await api('GET', '/api/categories');
    catsLoaded = true;
    document.getElementById('catCount').textContent = '(' + cats.length + ')';
    if (!cats.length) {
      grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>' + t('categories_empty') + '</p></div>';
      return;
    }
    grid.innerHTML = cats.map(function(c) {
      var icon  = CAT_ICONS[c.name] || '📖';
      var count = c.question_count || c.count || '';
      var id    = escH(String(c.id || c.name));
      var name  = catName(c.name);
      var qWord = t('questions_word');
      return '<div class="cat-card" onclick="startQuiz(\'' + escH(String(c.id||c.name)) + '\',\'' + escH(c.name) + '\')">'
        + '<div class="cat-icon">' + icon + '</div>'
        + '<div class="cat-name">' + escH(name) + '</div>'
        + '<div class="cat-count">' + (count ? count + ' ' + qWord : '') + '</div>'
        + '<div class="cat-bar-wrap"><div class="cat-bar" style="width:0%"></div></div>'
        + '</div>';
    }).join('');
  } catch(e) {
    grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">⚠️</div><p>' + t('categories_load_error') + '</p></div>';
  }
}

// ════════════════════════════════════════════
//  QUIZ
// ════════════════════════════════════════════
async function startRandomQuiz() {
  currentCat = null;
  isExamMode = false;
  await loadQuiz('/api/questions/random?count=30&has_image=true');
}

async function startDailyTest() {
  if (!isPremium()) { showPaywall(); return; }
  currentCat = null;
  isExamMode = false;
  await loadQuiz('/api/questions/random?count=10&has_image=true');
}

var isExamMode = false;
var examTimerInterval = null;
var examSecondsLeft = 0;

// ════════════════════════════════════════════
//  PREMIUM / PAYWALL
// ════════════════════════════════════════════
var FREE_LIMIT = 5;
var selectedPlan = 'monthly';
var accessState = null;

function isPremium() {
  return user && user.is_premium === true;
}

async function loadAccessStatus() {
  if (!deviceId) return null;
  try {
    accessState = await api('GET', '/api/access/status?device_id=' + encodeURIComponent(deviceId) + '&_=' + Date.now());
  } catch(e) {}
  return accessState;
}

async function consumeQuestionAccess(q) {
  if (isPremium()) return true;
  try {
    accessState = await api('POST', '/api/access/consume', {
      device_id: deviceId,
      question_id: String((q && (q.id || q._id || q.question_id)) || ''),
      mode: isExamMode ? 'exam' : 'practice',
      category: (q && q.category) || currentCat || '',
      event_id: deviceId + ':' + String((q && (q.id || q._id || q.question_id)) || qIdx) + ':' + qIdx + ':' + (quizStartedAt || '')
    });
    return true;
  } catch(e) {
    if (e.status === 402) { await loadAccessStatus(); showPaywall(); return false; }
    // Non-402 errors (network, 500) — don't block the user
    console.warn('[gate]', e && e.message ? e.message : e);
    return true;
  }
}

function checkPaywall() {
  // Returns true if user can continue, false = paywall shown
  if (isPremium()) return true;
  if (accessState && accessState.can_answer === false) {
    showPaywall();
    return false;
  }
  if (!accessState && qIdx >= FREE_LIMIT) {
    showPaywall();
    return false;
  }
  return true;
}

function showPaywall() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  stopExamTimer();
  applyUILang();
  showScreen('screenPaywall');
  // Hide top/bottom nav while paywall is shown
  document.getElementById('topBar').style.display = 'none';
  document.getElementById('bottomNav').style.display = 'none';
}

function hidePaywall() {
  document.getElementById('topBar').style.display = 'flex';
  document.getElementById('bottomNav').style.display = 'flex';
}

function selectPlan(plan, el) {
  selectedPlan = plan;
  document.querySelectorAll('.paywall-price-card').forEach(function(c){ c.classList.remove('selected'); });
  if (el) el.classList.add('selected');
}

async function buyPremium() {
  if (!token) {
    showScreen('screenAuth');
    return;
  }
  try {
    var base = window.location.origin + window.location.pathname;
    var session = await api('POST', '/api/create-checkout-session', {
      plan_id: selectedPlan,
      device_id: deviceId || '',
      success_url: base + '?checkout=success&session_id={CHECKOUT_SESSION_ID}',
      cancel_url: base + '?checkout=cancel'
    });
    if (session && session.livemode && session.url) {
      window.location.href = session.url;
      return;
    }
    throw new Error('Checkout unavailable');
  } catch(e) {
    toast(({
      th:'ไม่สามารถเปิดการชำระเงินได้ในตอนนี้',
      no:'Betaling er ikke tilgjengelig akkurat nå',
      en:'Payment is not available right now'
    }[appLang] || 'Payment is not available right now'), 5000);
  }
}

function paywallSkip() {
  hidePaywall();
  showTab('home');
}

async function startExam() {
  if (!isPremium()) { showPaywall(); return; }
  currentCat = null;
  isExamMode = true;
  await loadQuiz('/api/questions/random?count=45&has_image=true');
}

function startExamTimer() {
  if (examTimerInterval) clearInterval(examTimerInterval);
  examSecondsLeft = 90 * 60; // 90 minutes
  var badge = document.getElementById('examTimerBadge');
  var lbl   = document.getElementById('examTimerLbl');
  if (badge) badge.style.display = 'flex';
  updateTimerLabel(lbl, examSecondsLeft);
  examTimerInterval = setInterval(function() {
    examSecondsLeft--;
    updateTimerLabel(lbl, examSecondsLeft);
    if (examSecondsLeft <= 60) {
      badge.style.background = 'rgba(239,68,68,.35)';
      badge.style.borderColor = '#EF4444';
    }
    if (examSecondsLeft <= 0) {
      clearInterval(examTimerInterval);
      toast(t('time_is_up'));
      showEnd();
    }
  }, 1000);
}

function stopExamTimer() {
  if (examTimerInterval) { clearInterval(examTimerInterval); examTimerInterval = null; }
  var badge = document.getElementById('examTimerBadge');
  if (badge) badge.style.display = 'none';
}

function updateTimerLabel(lbl, secs) {
  var m = Math.floor(secs / 60);
  var s = secs % 60;
  if (lbl) lbl.textContent = m + ':' + (s < 10 ? '0' : '') + s;
}

async function startQuiz(catId, catRawName) {
  currentCat = { id: catId, name: catRawName };
  isExamMode = false;
  await loadQuiz('/api/questions/random?count=30&has_image=true&category=' + encodeURIComponent(catId));
}

async function loadQuiz(url) {
  showScreen('screenQuiz');
  await loadAccessStatus();
  var qCard = document.getElementById('qCard');
  qCard.innerHTML = '<div class="loading-wrap" style="grid-column:1/-1"><div class="spinner"></div><span style="color:var(--muted);font-size:.82rem">' + t('questions_loading') + '</span></div>';
  try {
    var raw = await api('GET', url);
    if (!Array.isArray(raw)) raw = raw.questions || [];
    questions = raw.filter(function(q) {
      var u = q.bildeUrl || q.image_url || '';
      return u && typeof u === 'string' && (u.startsWith('http') || u.startsWith('data:image'));
    });
    if (!questions.length && currentCat) {
      var r2 = await api('GET', '/api/questions/random?count=30&has_image=true');
      if (!Array.isArray(r2)) r2 = r2.questions || [];
      questions = r2.filter(function(q) {
        var u = q.bildeUrl || q.image_url || '';
        return u && typeof u === 'string' && (u.startsWith('http') || u.startsWith('data:image'));
      });
    }
    if (!questions.length) {
      qCard.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>' + t('questions_empty') + '</p></div>';
      return;
    }
    qIdx = 0; qScore = 0; qAnswered = false;
    _wrongStreak = 0; _correctStreak = 0; _correctPhraseIdx = 0;
    _sessionAnswered = 0; _sessionWrongTotal = 0; _recentTopics = []; _topicErrors = {}; _sessionAnswers = [];
    quizStartedAt = new Date().toISOString();
    stopExamTimer();
    if (isExamMode) startExamTimer();
    renderQuestion();
  } catch(e) {
    if (e.status === 402) { showPaywall(); return; }
    qCard.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">⚠️</div><p>' + t('generic_error') + '<br>' + escH(e.message) + '</p></div>';
  }
}

function pickLang(obj) {
  if (!obj) return '';
  if (typeof obj === 'string') return obj;
  return obj[appLang] || obj['th'] || obj['en'] || obj['no'] || Object.values(obj)[0] || '';
}

// Pick language-suffixed field from a question object (e.g. question_text_th, answer_a_no)
function pickField(q, base) {
  return q[base + '_' + appLang] || q[base + '_th'] || q[base + '_en'] || q[base + '_no'] || q[base] || '';
}

function renderQuestion() {
  if (qIdx >= questions.length) { showEnd(); return; }
  if (_aiPanelTimer) { clearTimeout(_aiPanelTimer); _aiPanelTimer = null; } // cancel delayed panel from prev Q
  var q     = questions[qIdx];
  qAnswered = false;
  var accessLimit = accessState && accessState.limit ? accessState.limit : FREE_LIMIT;
  var displayTotal = isPremium() ? questions.length : Math.min(accessLimit, questions.length);
  var total = questions.length;
  var pct   = (qIdx / displayTotal * 100).toFixed(0);

  document.getElementById('qProgLbl').textContent  = t('question') + ' ' + (qIdx + 1) + ' ' + t('of') + ' ' + displayTotal;
  document.getElementById('qProgFill').style.width = pct + '%';
  document.getElementById('qScoreNum').textContent = qScore;

  var imgUrl  = q.bildeUrl || q.image_url || '';
  var qText   = pickLang(q.question) || pickField(q, 'question_text') || '';
  currentCorrect = (q.correctOptionId || q.correct_answer || '').toUpperCase();
  currentExpl    = pickLang(q.explanation) || pickField(q, 'explanation') || '';
  var qId     = q._id || q.id || q.question_id || '';
  var isBm    = bookmarkedIds[qId] ? true : false;

  var opts = [];
  if (q.options && Array.isArray(q.options) && q.options.length) {
    opts = q.options.map(function(o) {
      return { id: String(o.id || o.key || '').toUpperCase(), text: pickLang(o.text) || pickLang(o) || String(o.text || '') };
    });
  } else {
    ['A','B','C','D'].forEach(function(l) {
      var base = 'answer_' + l.toLowerCase();
      var val = pickField(q, base);
      if (val) opts.push({ id: l, text: val });
    });
  }
  opts = opts.filter(function(o) { return o.text; });

  var qCard = document.getElementById('qCard');
  var ansHtml = opts.map(function(o) {
    var txt = typeof o.text === 'object' ? pickLang(o.text) : o.text;
    return '<button class="ans-btn" data-id="' + escH(o.id) + '" onclick="selectAns(this,\'' + escH(o.id) + '\')">'
      + '<span class="ans-letter">' + escH(o.id) + '</span>'
      + '<span class="ans-text">' + escH(txt) + '</span>'
      + '</button>';
  }).join('');

  var spdHtml = [0.5, 0.75, 1, 1.5, 2].map(function(r) {
    return '<button class="spd-btn' + (ttsRate === r ? ' active' : '') + '" data-rate="' + r + '" onclick="setRate(' + r + ',this)">' + r + 'x</button>';
  }).join('');

  var volHtml = [[0.5,'🔈'],[0.75,'🔉'],[1.0,'🔊']].map(function(item) {
    var v = item[0], icon = item[1];
    return '<button class="vol-btn' + (ttsVolume === v ? ' active' : '') + '" data-vol="' + v + '" onclick="setVolume(' + v + ')">' + icon + '</button>';
  }).join('');

  // Free limit banner for non-premium. Backend access policy is the source of truth;
  // qIdx is only used as a fallback before the first status fetch returns.
  var freeBanner = '';
  var policyRemaining = accessState && accessState.remaining !== null && accessState.remaining !== undefined
    ? Number(accessState.remaining)
    : (FREE_LIMIT - qIdx);
  if (!isPremium() && policyRemaining > 0) {
    var remaining = Math.max(0, policyRemaining);
    var freeMsg = {th:'เหลือ ' + remaining + ' คำถามฟรี', no:remaining + ' gratis spørsmål igjen', en:remaining + ' free questions left'}[appLang] || remaining + ' gratis spørsmål igjen';
    freeBanner = '<div style="text-align:center;font-size:.72rem;color:var(--orange);font-weight:700;margin-top:6px;flex-shrink:0;">'
      + '⚡ ' + freeMsg + ' — <span style="text-decoration:underline;cursor:pointer" onclick="showPaywall()">' + escH(t('upgrade')) + '</span>'
      + '</div>';
  }

  qCard.innerHTML =
    '<div class="q-left">'
      + '<div class="q-img-wrap" id="qImgWrap">'
        + '<img class="q-img" src="' + escH(imgUrl) + '" alt="" onerror="this.parentElement.style.display=\'none\'" loading="lazy">'
      + '</div>'
      + '<div class="q-text">' + escH(qText) + '</div>'
      + '<div style="flex-shrink:0;"><button class="tts-play" id="qTtsBtn" title="' + escH(t('read_aloud')) + '" onclick="speakQ()">▶</button></div>'
    + '</div>'
    + '<div class="q-mid">'
      + buildSituationLensHtml(qText, currentExpl)
      + '<div class="q-answers" id="qAnswers">' + ansHtml + '</div>'
      + '<div class="q-feedback" id="qFeedback"></div>'
      // Mobile AI section — empty until answered (:empty hides it), then expands in-flow
      + '<div class="quiz-ai-mobile" id="quizAiMobile"></div>'
      + '<button class="q-next-mobile" id="qNextMobile" disabled onclick="nextQ()">' + t('next') + '</button>'
    + '</div>'
    + '<div class="q-next-col">'
      + '<button class="q-next-big" id="qNextBig" disabled onclick="nextQ()">' + t('next') + '</button>'
      + '<button class="q-bookmark-btn' + (isBm ? ' bookmarked' : '') + '" id="qBmBtn" onclick="toggleBookmark(\'' + escH(qId) + '\')" title="' + escH(t('bookmark')) + '">'
        + (isBm ? '🔖' : '🔖')
      + '</button>'
    + '</div>'
    + (freeBanner ? freeBanner : '');

  // ── Reset AI right panel for new question ─────────────────────────
  var aiImgbox = document.querySelector('.quiz-ai-imgbox');
  if (aiImgbox) aiImgbox.className = 'quiz-ai-imgbox'; // clear glow
  var aiImg = document.getElementById('quizAiImg');
  if (aiImg) { aiImg.src = imgUrl; aiImg.className = 'quiz-ai-img'; } // clear flash
  var aiOverlay = document.getElementById('quizAiOverlay');
  if (aiOverlay) aiOverlay.className = 'quiz-ai-img-overlay';
  var aiStatus = document.getElementById('quizAiStatus');
  if (aiStatus) { aiStatus.textContent = t('ai_waiting'); aiStatus.className = 'quiz-ai-status idle'; }
  var aiImgBadge = document.getElementById('quizAiImgBadge');
  if (aiImgBadge) aiImgBadge.textContent = t('traffic_situation');
  var aiBody = document.getElementById('quizAiBody');
  if (aiBody) {
    aiBody.innerHTML = '<div class="quiz-ai-idle">'
      + '<div class="quiz-ai-idle-icon">👆</div>'
      + '<div class="quiz-ai-idle-text">' + escH(t('ai_idle')) + '</div>'
      + '</div>';
  }
}

var currentCorrect = '';
var currentExpl = '';

// ── Learning state — streak + session depth tracking ─────────────────────────
// Streaks reset when the quiz restarts; session totals track across the run.
// Together they let the AI adapt tone AND explanation depth to the student.
var _wrongStreak      = 0;  // consecutive wrong answers → more support
var _correctStreak    = 0;  // consecutive correct answers → quieter coaching
var _sessionAnswered  = 0;  // total answers this session — infers experience stage
var _sessionWrongTotal = 0; // running wrong count — infers struggle rate
var _recentTopics = [];     // last 4 alert labels — detects repeated topic struggles
var _topicErrors  = {};     // label → errorCount — feeds debrief translation layer (never shown raw)

// Calm acknowledgment pool — rotates to avoid repetition, never effusive
var _correctPhraseIdx = 0;
function _correctPhrases() {
  return {
    th:['ถูกต้อง','ใช่แล้ว','สังเกตได้ถูกต้อง','ถูกต้อง นั่นคือหลักการสำคัญ','ตัดสินใจได้ถูกต้อง'],
    no:['Riktig.','Det stemmer.','Riktig observert.','Korrekt — det er nettopp slik det fungerer.','Det er riktig.','Riktig vurdering.'],
    en:['Correct.','That is right.','Good observation.','Correct — that is exactly how it works.','That is correct.','Sound judgement.']
  }[appLang] || {
    th:['ถูกต้อง'],
    no:['Riktig.'],
    en:['Correct.']
  }.no;
}
function _nextCorrectPhrase() {
  var pool = _correctPhrases();
  var p = pool[_correctPhraseIdx % pool.length];
  _correctPhraseIdx++;
  return p;
}

// Streak-adaptive wrong-answer support — calm, professional, never patronising
function _wrongSupportText(streak) {
  if (streak >= 5) return t('wrong_support_5');
  if (streak >= 3) return t('wrong_support_3');
  return t('wrong_support_1');
}

// ── Session confidence level ─────────────────────────────────────────────────
// Derived quietly from streak + session wrong rate.
// Used to calibrate: expand behavior, tip directness, fallback phrasing.
// Never shown to the student — purely internal scaffolding.
function _confidenceLevel() {
  if (_sessionAnswered < 4) return 'early';          // too little data to judge
  var rate = _sessionWrongTotal / _sessionAnswered;
  if (_wrongStreak >= 3 || rate > 0.50) return 'low';     // actively struggling
  if (_wrongStreak === 0 && _correctStreak >= 4 && rate < 0.25) return 'high'; // fluent
  return 'medium';
}

// ── Topic-aware danger card label ────────────────────────────────────────────
// Returns a precise topic label instead of the generic "Forstå situasjonen".
// Makes wrong-answer cards feel targeted, not formulaic.
function _dangerLabel(expl) {
  if (!expl) return 'Forstå situasjonen';
  var t = expl;
  if (/forbikjør/i.test(t))                            return 'Forbikjøring';
  if (/avstand|følgeavstand|3[- ]sek/i.test(t))        return 'Avstand og tid';
  if (/vikeplikt|forkjørsrett/i.test(t))               return 'Vikeplikt';
  if (/gangfelt|fotgjenger|syklist/i.test(t))          return 'Myke trafikanter';
  if (/glatt|is\b|snø|vinter|slipperisk/i.test(t))    return 'Vinterforhold';
  if (/uoversiktlig|begrenset sikt|kurve|blind/i.test(t)) return 'Sikt og fart';
  if (/tretthet|trøtt\b|søvn/i.test(t))               return 'Tretthet';
  if (/rundkjøring/i.test(t))                          return 'Rundkjøring';
  if (/promille|alkohol/i.test(t))                     return 'Alkohol';
  if (/reaksjon\w*\s*tid/i.test(t))                    return 'Reaksjonstid';
  if (/lys\b|belysning|nærlys|langt\s*lys/i.test(t))  return 'Lysbruk';
  if (/fartsgrense|hastighet|km\/t/i.test(t))          return 'Fartsgrense';
  if (/nødbrems|abs\b|bremsebane/i.test(t))            return 'Bremsing';
  if (/møtende|tunnel\b/i.test(t))                     return 'Møtende trafikk';
  return 'Forstå situasjonen';
}

function topicLabel(label) {
  var map = {
    'Forstå situasjonen': {th:'เข้าใจสถานการณ์', no:'Forstå situasjonen', en:'Understand the situation'},
    'Forbikjøring': {th:'การแซง', no:'Forbikjøring', en:'Overtaking'},
    'Avstand og tid': {th:'ระยะห่างและเวลา', no:'Avstand og tid', en:'Distance and time'},
    'Vikeplikt': {th:'การให้ทาง', no:'Vikeplikt', en:'Yielding'},
    'Myke trafikanter': {th:'ผู้ใช้ถนนที่เปราะบาง', no:'Myke trafikanter', en:'Vulnerable road users'},
    'Vinterforhold': {th:'สภาพถนนฤดูหนาว', no:'Vinterforhold', en:'Winter conditions'},
    'Kjøreforhold': {th:'สภาพการขับขี่', no:'Kjøreforhold', en:'Driving conditions'},
    'Sikt og fart': {th:'ทัศนวิสัยและความเร็ว', no:'Sikt og fart', en:'Visibility and speed'},
    'Tretthet': {th:'ความเหนื่อยล้า', no:'Tretthet', en:'Fatigue'},
    'Rundkjøring': {th:'วงเวียน', no:'Rundkjøring', en:'Roundabout'},
    'Alkohol': {th:'แอลกอฮอล์', no:'Alkohol', en:'Alcohol'},
    'Reaksjonstid': {th:'เวลาตอบสนอง', no:'Reaksjonstid', en:'Reaction time'},
    'Lysbruk': {th:'การใช้ไฟ', no:'Lysbruk', en:'Use of lights'},
    'Fartsgrense': {th:'จำกัดความเร็ว', no:'Fartsgrense', en:'Speed limit'},
    'Bremsing': {th:'การเบรก', no:'Bremsing', en:'Braking'},
    'Møtende trafikk': {th:'รถสวนทาง', no:'Møtende trafikk', en:'Oncoming traffic'},
    '3-sekunders-regelen': {th:'กฎ 3 วินาที', no:'3-sekunders-regelen', en:'3-second rule'},
    'Grenseverdi': {th:'ค่าจำกัดตามกฎหมาย', no:'Grenseverdi', en:'Legal limit'}
  };
  var item = map[label] || null;
  return item ? (item[appLang] || item.th || item.en || item.no) : label;
}

async function selectAns(btn, picked) {
  if (qAnswered) return;
  var _curQ = questions[qIdx];
  qAnswered = true;
  if (!(await consumeQuestionAccess(_curQ))) { qAnswered = false; return; }
  var correct = currentCorrect;
  var isOk = picked.toUpperCase() === correct.toUpperCase();
  if (isOk) qScore++;

  // Update streaks and session counters before building the AI panel
  if (isOk) { _correctStreak++; _wrongStreak = 0; }
  else       { _wrongStreak++;  _correctStreak = 0; }
  _sessionAnswered++;
  if (!isOk) {
    _sessionWrongTotal++;
    // Track per-topic errors for end debrief — raw data stays internal
    var _tLabel = _dangerLabel(currentExpl);
    if (_tLabel && _tLabel !== 'Forstå situasjonen') {
      _topicErrors[_tLabel] = (_topicErrors[_tLabel] || 0) + 1;
    }
  }

  // Record this answer for the history detail panel
  _sessionAnswers.push({
    question_id:   String(_curQ._id || _curQ.id || _curQ.question_id || ''),
    question_text: (pickLang(_curQ.question) || pickField(_curQ, 'question_text') || '').slice(0, 200),
    user_answer:   picked.toUpperCase(),
    correct_answer: correct,
    is_correct:    isOk,
    explanation:   (currentExpl || '').slice(0, 400)
  });

  document.querySelectorAll('.ans-btn').forEach(function(b) {
    b.disabled = true;
    var id = (b.dataset.id || '').toUpperCase();
    if (id === correct && id === picked.toUpperCase()) b.classList.add('correct');
    else if (b === btn) b.classList.add('wrong');
    else if (id === correct) b.classList.add('reveal');
  });

  var fb = document.getElementById('qFeedback');
  fb.textContent = isOk ? t('correct') : t('wrong');
  fb.className = 'q-feedback ' + (isOk ? 'ok' : 'bad');

  document.getElementById('qScoreNum').textContent = qScore;

  var nb = document.getElementById('qNextBig');
  var nm = document.getElementById('qNextMobile');
  if (nb) nb.disabled = false;
  if (nm) nm.disabled = false;

  playSound(isOk ? 'correct' : 'wrong');
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  ttsPlaying = false;

  // Collapse Se→Forstå→Velg lens — feedback takes over, no need for both
  var _lens = document.querySelector('.q-observe');
  if (_lens) _lens.classList.add('answered');

  // AI panel: brief pause before instructor speaks — feels more deliberate
  if (_aiPanelTimer) { clearTimeout(_aiPanelTimer); _aiPanelTimer = null; }
  _aiPanelTimer = setTimeout(function() {
    _aiPanelTimer = null;
    updateAiPanel(isOk, currentExpl);
  }, 210);
}

// ── Split explanation into short (first sentence) and rest ──────────────────
// Powers the multi-level "Vis mer" pattern for layered learning.
// The 40-char minimum prevents false splits on abbreviations like "m.m." or "f.eks."
function splitExpl(expl) {
  if (!expl) return {short: '', rest: ''};
  // Sentence break — require at least 40 chars before split point
  var m = expl.match(/^(.{40,}?[.!?])(?:\s+|$)([\s\S]*)$/);
  if (m && m[2].trim().length > 32) {
    return {short: m[1].trim(), rest: m[2].trim()};
  }
  // Fallback: word-break at ~115 chars if text is long enough
  if (expl.length > 140) {
    var cut = expl.lastIndexOf(' ', 115);
    if (cut > 65) return {short: expl.slice(0, cut) + '…', rest: expl.slice(cut + 1).trim()};
  }
  return {short: expl, rest: ''};
}

// ── Contextual learning alert classifier ────────────────────────────────────
// Scans explanation text for Norwegian traffic keywords and returns
// 0–2 smart alert cards that add context without overwhelming the learner.
// Types: danger (red) · rule (blue) · weather (cyan) · exam (purple)
function classifyAlerts(expl) {
  var alerts = [];
  if (!expl) return alerts;
  var t = expl.toLowerCase();
  function A(icon, type, label, th, no, en) {
    alerts.push({icon:icon, type:type, label:label, text:({th:th, no:no, en:en}[appLang] || th || en || no)});
  }

  if (/forbikjør|forbi\s|overtakings/i.test(t))
    A('🚗', 'danger', 'Forbikjøring',
      'ต้องเห็นชัดและมีระยะพอ รอจนปลอดภัยจริงก่อนแซง',
      'Full sikt og god avstand er nødvendig. Vent alltid til det er klart trygt.',
      'Full visibility and enough distance are needed. Wait until it is clearly safe.');

  if (/glatt|is\b|snø|vinter|slipperisk|vått\s|regn/i.test(t))
    A('❄️', 'weather', 'Kjøreforhold',
      'ระยะเบรกยาวขึ้นมากเมื่อถนนลื่น ปรับความเร็วและระยะห่างให้เหมาะกับสภาพถนน',
      'Bremselengden øker kraftig i dårlig vær — tilpass alltid fart og avstand til forholdene.',
      'Braking distance increases a lot in poor conditions. Adjust speed and distance.');

  if (/avstand|3 sek|følgeavstand|bremse\w*\s*lengde/i.test(t))
    A('📏', 'rule', '3-sekunders-regelen',
      'เว้นอย่างน้อย 3 วินาทีจากคันหน้า เพิ่มระยะเมื่อฝนตก มืด หรือขับเร็ว',
      'Hold minst 3 sekunder bak bilen foran. Mer avstand ved regn, mørke eller høy fart.',
      'Keep at least 3 seconds behind the car in front. Add more in rain, darkness, or high speed.');

  if (/uoversiktlig|begrenset sikt|kurve|kryss\w*\s*sikt|blind/i.test(t))
    A('👁️', 'danger', 'Sikt og fart',
      'ถ้ามองเห็นไม่ไกลพอ ต้องลดความเร็ว ทัศนวิสัยคือพื้นฐานของการขับอย่างปลอดภัย',
      'Der du ikke ser langt nok, må farten ned. God sikt er grunnlaget for trygg kjøring.',
      'When you cannot see far enough, slow down. Visibility is the basis of safe driving.');

  if (/vikeplikt|forkjørsrett/i.test(t))
    A('⚠️', 'danger', 'Vikeplikt',
      'อุบัติเหตุในทางแยกมักเกิดจากไม่ให้ทาง ถามเสมอว่าใครมีสิทธิ์ไปก่อน',
      'Brudd på vikeplikt er årsaken til mange krysskollisjon — spør alltid: hvem har forkjørsrett her?',
      'Many junction crashes come from yield mistakes. Always ask who has priority here.');

  if (/gangfelt|fotgjenger/i.test(t))
    A('🚶', 'danger', 'Myke trafikanter',
      'คนเดินเท้าและจักรยานบาดเจ็บง่ายที่สุด ให้พื้นที่และพร้อมหยุดทันเวลา',
      'Fotgjengere og syklister er mest sårbare — gi alltid god plass og stans i tide.',
      'Pedestrians and cyclists are most vulnerable. Give space and stop in time.');

  if (/fartsgrense|hastighets|km\/t|80\s*km|60\s*km|50\s*km|30\s*km/i.test(t))
    A('🧠', 'exam', 'Fartsgrense',
      'จำกัดความเร็วขึ้นกับถนน ทัศนวิสัย และการจราจร เข้าใจเหตุผล ไม่ใช่จำตัวเลขอย่างเดียว',
      'Fartsgrenser er satt ut fra vei, sikt og trafikktetthet. Forstå logikken — ikke bare husk tallet.',
      'Speed limits reflect road, visibility, and traffic. Understand the logic, not just the number.');

  if (/belysning|lys\b|fyrlys|mørk|langt\s*lys|nærlys/i.test(t))
    A('💡', 'rule', 'Lysbruk',
      'ไฟที่ถูกต้องทำให้คุณเห็นและถูกมองเห็น ปรับไฟให้เข้ากับสถานการณ์เสมอ',
      'Riktig lys gjør deg synlig og beskyttet. Sjekk alltid at lyset er tilpasset forholdene.',
      'Correct lights help you see and be seen. Match the lights to the situation.');

  if (/reaksjon\w*\s*tid|reaksjonstid/i.test(t))
    A('⏱️', 'rule', 'Reaksjonstid',
      'ที่ 80 กม./ชม. รถวิ่งประมาณ 22 เมตรต่อวินาที จึงต้องเผื่อระยะปลอดภัยเสมอ',
      'Ved 80 km/t tilbakelegger du 22 meter per sekund — bygg alltid inn nok sikkerhetsmargin.',
      'At 80 km/h you travel about 22 meters per second. Always build in a safety margin.');

  if (/rundkjøring|sving\s*inn|kjøring\s*inn\s*i\s*rund/i.test(t))
    A('🔄', 'rule', 'Rundkjøring',
      'รถที่อยู่ในวงเวียนมีสิทธิ์ไปก่อน ให้ทางก่อนเข้า และขับอย่างนิ่งคาดเดาได้',
      'Trafikk inne i rundkjøringen har forkjørsrett. Gi vikeplikt ved innkjøring — kjør rolig og forutsigbart.',
      'Traffic already in the roundabout has priority. Yield before entering and drive predictably.');

  if (/nødbrems|abs\b|bremse\w*\s*avstand|bremsebane|bremse\w*\s*vei/i.test(t))
    A('🛑', 'danger', 'Bremsing',
      'ABS ช่วยไม่ให้ล้อล็อก แต่ไม่ได้ทำให้ระยะเบรกสั้นเสมอ กดเบรกมั่นคงและต่อเนื่อง',
      'ABS hindrer hjullås men forkorter ikke alltid bremseavstanden. Trykk jevnt og hardt — slipp ikke opp.',
      'ABS prevents wheel lock but does not always shorten braking distance. Brake firmly and steadily.');

  if (/møtende|motgående|svingslys|tunnel\b/i.test(t))
    A('💡', 'danger', 'Møtende trafikk',
      'ลดไฟสูงให้ทันเมื่อมีรถสวนทาง รักษาตำแหน่งขวาและใช้ไฟต่ำในอุโมงค์',
      'Blend ned i god tid for møtende trafikk. Hold til høyre og bruk nærlys i tunnel.',
      'Dip high beams in time for oncoming traffic. Keep right and use low beams in tunnels.');

  if (/tretthet|trøtt\b|døs|søvn|kjøretretthet/i.test(t))
    A('😴', 'danger', 'Tretthet',
      'ความเหนื่อยล้าอันตรายเหมือนแอลกอฮอล์ วางแผนพัก และหยุดนอนเมื่อจำเป็น',
      'Tretthet er like farlig som alkohol. Planlegg pauser — stopp og sov heller enn å presse seg.',
      'Fatigue can be as dangerous as alcohol. Plan breaks and stop to sleep rather than pushing on.');

  if (/promille|alkohol|ruspåvirket|0[,.]2\s*promille/i.test(t))
    A('⚖️', 'rule', 'Grenseverdi',
      'ในนอร์เวย์ขีดจำกัดคือ 0.2 โปรมิลล์ แอลกอฮอล์แม้เพียงเล็กน้อยก็ลดเวลาตอบสนอง',
      '0,2 promille er grensen i Norge. Selv små mengder alkohol svekker reaksjonstid og situasjonsforståelse.',
      'The limit in Norway is 0.2 per mille. Even small amounts weaken reaction and understanding.');

  return alerts.slice(0, 2); // max 2 per answer — calm, not overwhelming
}

// ── Context-aware instructor tip ─────────────────────────────────────────────
// Priority: streak state → topic context → generic fallback.
// The AI instructor responds first to how the student is FEELING, then to the topic.
function buildInstructorTip(isOk, alerts) {
  // ─ Streak-aware coaching — professional, calm, no gamification ─
  if (!isOk && _wrongStreak >= 5)
    return appLang === 'th' ? 'หัวข้อนี้ต้องใช้เวลา อ่านคำอธิบายอย่างใจเย็น ความเข้าใจจะค่อย ๆ ชัดขึ้น'
      : appLang === 'en' ? 'This is a demanding topic. Read the explanation calmly; understanding builds over time.'
      : 'Dette er et krevende tema. Les forklaringen grundig — forståelse bygges over tid.';
  if (isOk && _correctStreak >= 10)
    return appLang === 'th' ? 'คุณกำลังก้าวหน้าได้ดีในหัวข้อนี้'
      : appLang === 'en' ? 'You are making good progress on this topic.'
      : 'Du er i god progresjon på dette temaet.';
  // correctStreak 1-9: fall through to topic-aware tip

  if (appLang !== 'no') {
    // Full-depth multilingual coaching — matches the Norwegian path topic-for-topic
    function _tip(th, en) { return appLang === 'th' ? th : en; }

    if (alerts.length > 0) {
      var _topics = alerts.map(function(a) { return a.label.toLowerCase(); }).join(' ');
      var _type   = alerts[0].type;

      // ── Compound situations ──────────────────────────────────────────────────
      if (alerts.length >= 2) {
        var _isWeather  = (_type === 'weather' || alerts[1].type === 'weather' || _topics.indexOf('vinter') >= 0);
        var _hasAvstand = (_topics.indexOf('avstand') >= 0 || _topics.indexOf('sekund') >= 0);
        var _hasSikt    = (_topics.indexOf('sikt') >= 0 || _topics.indexOf('fart') >= 0);
        var _hasForbi   = _topics.indexOf('forbi') >= 0;
        var _hasVike    = _topics.indexOf('vikeplikt') >= 0;
        var _hasMyk     = (_topics.indexOf('myk') >= 0 || _topics.indexOf('fotgjenger') >= 0 || _topics.indexOf('trafikant') >= 0);

        if (_isWeather && _hasAvstand)
          return isOk
            ? _tip('ถนนลื่นและระยะห่างสัมพันธ์กันมาก — กฎ 3 วินาทีเป็นขั้นต่ำ ให้มากกว่านั้นในสภาพอากาศไม่ดี',
                   'Slippery road and following distance are closely linked — the 3-second rule is a minimum; give more in bad weather.')
            : _tip('ถนนลื่นและระยะห่างน้อยอันตรายมาก ในสภาพอากาศไม่ดี ให้ระยะห่างสองเท่าและลดความเร็วครึ่งหนึ่ง',
                   'Slippery road and short following distance are very dangerous. In bad weather: double distance, half speed.');

        if (_hasSikt && _hasForbi)
          return isOk
            ? _tip('ทัศนวิสัยและการแซงเชื่อมโยงกันเสมอ — อย่าเริ่มแซงหากมองข้างหน้าไม่ชัดเจน',
                   'Visibility and overtaking are always linked — never start to overtake where you cannot see clearly ahead.')
            : _tip('เมื่อทัศนวิสัยไม่ดี การแซงเป็นเรื่องที่ไม่ควรทำเลย — รอเสมอ ไม่คุ้มกับความเสี่ยง',
                   'When visibility is limited, overtaking is always irresponsible — wait. It is never worth the risk.');

        if (_hasVike && _hasMyk)
          return isOk
            ? _tip('การให้ทางและผู้ใช้ถนนที่เปราะบาง: ทางข้ามและสี่แยกคือที่ที่ต้องระวังคนเดินเท้าเสมอ',
                   'Yielding and vulnerable road users: crossings and junctions are places where you must always expect pedestrians.')
            : _tip('คนเดินเท้าที่จุดให้ทางต้องการความสนใจสองเท่า — มองก่อนเสมอก่อนขับออกไป',
                   'Pedestrians at yield points need double attention — always look before driving into the junction.');
      }

      // ── Single-topic branches ────────────────────────────────────────────────
      if (_type === 'weather' || _topics.indexOf('vinter') >= 0)
        return isOk
          ? _tip('จำไว้ว่าแรงยึดเกาะและระยะเบรกเปลี่ยนแปลงมากตามสภาพอากาศ — ขับตามสภาพถนนเสมอ',
                 'Remember: grip and braking distance vary greatly with conditions — always drive accordingly.')
          : _tip('บนถนนลื่น ระยะเบรกเพิ่มขึ้นมาก อ่านพื้นถนนและปรับความเร็วและระยะห่างเสมอ',
                 'On slippery roads, braking distance increases greatly. Read the road surface and always adjust speed and following distance.');

      if (_topics.indexOf('sikt') >= 0 || _topics.indexOf('fart') >= 0)
        return isOk
          ? _tip('การสังเกตที่ดีคือสิ่งที่แยกผู้ขับที่ปลอดภัยออกจากผู้ขับที่อันตราย ฝึกมองข้างหน้าไกลๆ',
                 'Good observation is what separates safe drivers from dangerous ones. Train your eyes to look far ahead.')
          : _tip('ในทุกสภาพการขับขี่: มองข้างหน้าไกลๆ และสร้างระยะปลอดภัย โดยเฉพาะในโค้ง',
                 'In all driving: look far ahead and build in safety margins — especially in curves.');

      if (_topics.indexOf('sekund') >= 0 || _topics.indexOf('avstand') >= 0)
        return isOk
          ? _tip('กฎ 3 วินาทีคือสิ่งที่ง่ายที่สุดในการป้องกันการชนท้าย — ใช้มันทุกครั้ง',
                 'The 3-second rule is your simplest insurance against rear-end collisions — use it every time.')
          : _tip('ฝึกนับ "หนึ่งพัน-หนึ่ง, หนึ่งพัน-สอง, หนึ่งพัน-สาม" ระหว่างคุณและรถคันหน้า',
                 'Practice counting "one-thousand-one, one-thousand-two, one-thousand-three" between you and the car ahead.');

      if (_topics.indexOf('vikeplikt') >= 0)
        return isOk
          ? _tip('การเข้าใจการให้ทางอย่างดีเป็นพื้นฐานของการขับขี่ปลอดภัยในทุกสี่แยก',
                 'Good understanding of yielding is the foundation of safe driving at every junction.')
          : _tip('การให้ทางในสี่แยกเป็นสาเหตุของการชนด้านข้างมาก เข้าใจสถานการณ์ อย่าแค่จำกฎ',
                 'Yielding at junctions causes many side collisions — understand the situation, not just memorise the rule.');

      if (_topics.indexOf('myk') >= 0 || _topics.indexOf('fotgjenger') >= 0 || _topics.indexOf('trafikant') >= 0)
        return isOk
          ? _tip('คนเดินเท้าและนักปั่นจักรยานคือผู้ใช้ถนนที่เปราะบางที่สุด — ระวังพวกเขาเสมอ',
                 'Pedestrians and cyclists are the most vulnerable road users — always be extra alert for them.')
          : _tip('ทางข้ามให้สิทธิ์คนเดินเท้าในการข้ามถนน — ชะลอความเร็วล่วงหน้าเสมอ',
                 'Crossings give pedestrians the right to cross safely — always slow down in time.');

      if (_topics.indexOf('forbi') >= 0)
        return isOk
          ? _tip('การแซงต้องอาศัยความอดทน อย่าเร่ง — รอจนแน่ใจว่าปลอดภัย',
                 'Overtaking requires patience. Do not rush — wait until you are certain it is safe.')
          : _tip('การตัดสินใจผิดในการแซงเป็นสาเหตุหลักของการชนหัวชน — รอจนเห็นว่าปลอดภัยจริงๆ เสมอ',
                 'Wrong judgement when overtaking is a main cause of head-on collisions — always wait until it is clearly safe.');

      if (_type === 'exam')
        return isOk
          ? _tip('นี่คือสถานการณ์ที่หลายคนมองข้าม — ที่คุณรู้จักมันแสดงว่าคุณเข้าใจจริงๆ',
                 'This is a pattern many people miss — the fact that you recognised it shows real understanding.')
          : _tip('สิ่งสำคัญคือการเข้าใจสถานการณ์ตั้งแต่เนิ่นๆ การจำสถานการณ์ได้จริง ไม่ใช่แค่จำคำตอบ คือเป้าหมาย',
                 'The key is understanding the situation early. Real recognition in traffic — not just a correct answer — is the goal.');

      if (_topics.indexOf('rundkjøring') >= 0)
        return isOk
          ? _tip('วงเวียนมีประสิทธิภาพแต่ต้องใช้ความแม่นยำ — ให้ทางรถที่อยู่ในวงเวียนก่อนเสมอ',
                 'Roundabouts are efficient but need precision. Always give way to traffic already inside.')
          : _tip('จำไว้: รถที่อยู่ในวงเวียนมีสิทธิ์ก่อน — รอจนถนนโล่งก่อนเข้า',
                 'Remember: traffic already in the roundabout has priority — wait until the way is clear before entering.');

      if (_topics.indexOf('brems') >= 0)
        return isOk
          ? _tip('ระยะห่างที่ดีคือหลักประกันที่สำคัญที่สุด ยิ่งระยะเบรกสั้น ยิ่งมีเวลาสำหรับการตัดสินใจอื่น',
                 'Good following distance is your most important buffer. Shorter braking distance means more time for other decisions.')
          : _tip('ฝึกคิดเรื่องการเบรกฉุกเฉินในใจ — การตอบสนองของคุณเป็นสิ่งที่กำหนดว่าจะหยุดทันหรือไม่',
                 'Mentally practise emergency braking — your reaction determines whether you stop in time.');

      if (_topics.indexOf('møtende') >= 0 || _topics.indexOf('tunnel') >= 0)
        return isOk
          ? _tip('การขับที่คาดเดาได้ทำให้รถสวนทางมองเห็นคุณได้ง่ายขึ้น — รักษาเส้นทางและความเร็ว',
                 'Predictable driving makes you easier for oncoming traffic to see — hold your line and speed.')
          : _tip('ในอุโมงค์และที่มืด: ชิดขวา ใช้ไฟต่ำ และลดความเร็ว — ระยะมองเห็นสั้นลง',
                 'In tunnels and darkness: keep right, use low beam, and slow down — visibility is shorter.');

      if (_topics.indexOf('tretthet') >= 0)
        return isOk
          ? _tip('วางแผนการเดินทางโดยมีช่วงพัก ความเมื่อยล้าสะสมช้าๆ และยากที่จะรู้ตัว',
                 'Plan journeys with breaks. Fatigue builds gradually and is hard to detect in yourself.')
          : _tip('ความเมื่อยล้าแสดงตัวโดยไม่เตือน การหยุดพักก่อนเวลาเป็นการตัดสินใจที่ถูกต้องเสมอ',
                 'Fatigue strikes without warning. Stopping early is always the right decision — there are no shortcuts.');

      if (_topics.indexOf('grenseverdi') >= 0 || _topics.indexOf('alkohol') >= 0)
        return isOk
          ? _tip('การไม่ดื่มเลยคือทางเลือกที่ปลอดภัยที่สุด — ขีดจำกัดของกฎหมายคือเส้นทางกฎหมาย ไม่ใช่คำแนะนำ',
                 'Zero alcohol is the safest choice — the legal limit is a legal boundary, not a recommendation.')
          : _tip('ขีดจำกัด 0.2 คุ้มครองจากโทษทางกฎหมาย ไม่ได้คุ้มครองจากอุบัติเหตุ แอลกอฮอล์และการขับรถไม่เข้ากัน',
                 'The 0.2 limit protects against punishment, not accidents. Alcohol and driving do not belong together.');

      if (_topics.indexOf('reaksjonstid') >= 0)
        return isOk
          ? _tip('การตอบสนองที่รวดเร็วต้องการการฝึก แต่ระยะห่างที่ดีคือสิ่งที่ให้เวลาคุณเสมอ',
                 'Fast reaction takes practice — but good following distance is the buffer that is always there.')
          : _tip('ที่ 80 กม./ชม. คุณเดินทาง 22 เมตรต่อวินาที — ระยะห่างและความตื่นตัวคือเกราะป้องกันที่แท้จริง',
                 'At 80 km/h you travel 22 metres per second — distance and alertness are the only real protection.');

      if (_topics.indexOf('lys') >= 0)
        return isOk
          ? _tip('ไฟรถทำให้คุณมองเห็นและถูกมองเห็น — ทั้งสองอย่างช่วยชีวิตได้',
                 'Lights make you see and be seen — both save lives.')
          : _tip('ไฟรถคือการสื่อสารในการจราจร ตรวจสอบเสมอว่าการใช้ไฟเหมาะสมกับสถานการณ์',
                 'Lights are communication in traffic. Always check that your light use matches the situation.');

      // ── Repeated topic detection ─────────────────────────────────────────────
      if (!isOk && _recentTopics.length > 1 && _recentTopics.slice(1).indexOf(alerts[0].label) >= 0) {
        var _rLabel = alerts[0].label.toLowerCase();
        if (_rLabel.indexOf('vikeplikt') >= 0)
          return _tip('คุณพบเรื่องการให้ทางอีกแล้ว ลองคิดแบบนี้: มองรถทางขวา — รถนั้นมักมีสิทธิ์ก่อน',
                      'You have met yielding rules again. Try this: find the car on the right — it usually has priority.');
        if (_rLabel.indexOf('avstand') >= 0 || _rLabel.indexOf('sekund') >= 0)
          return _tip('ระยะห่างปรากฏอีกครั้ง ในทางปฏิบัติ: เลือกจุดคงที่ แล้วนับถึง 3 หลังจากรถคันหน้าผ่านจุดนั้น',
                      'Following distance appears again. In practice: pick a fixed point, count to 3 after the car ahead passes it.');
        if (_rLabel.indexOf('forbi') >= 0)
          return _tip('การแซงเป็นเรื่องยาก กฎจำง่าย: ถ้ายังสงสัย อย่าแซง นั่นคือการตัดสินใจที่ถูกต้องเสมอ',
                      'Overtaking is demanding. Simple rule: when in doubt, do not overtake. It is always the right choice.');
        if (_rLabel.indexOf('sikt') >= 0 || _rLabel.indexOf('fart') >= 0)
          return _tip('ทัศนวิสัยและความเร็วปรากฏอีกครั้ง กฎพื้นฐาน: ที่ไหนมองเห็นน้อย ขับช้าที่นั่น เสมอ',
                      'Visibility and speed appear again. Basic rule: where you see less, drive slower. Always.');
        if (_rLabel.indexOf('vinter') >= 0)
          return _tip('สภาพถนนปรากฏอีกครั้ง อ่านพื้นผิวถนน — แรงยึดเกาะคือทุกอย่างในสภาพอากาศไม่ดี',
                      'Road conditions appear again. Read the road surface — friction is everything in bad weather.');
        if (_rLabel.indexOf('gangfelt') >= 0 || _rLabel.indexOf('myk') >= 0)
          return _tip('ผู้ใช้ถนนที่เปราะบางปรากฏอีกครั้ง มองหาคนเดินเท้าอย่างตั้งใจ อย่ารอให้พวกเขาโผล่มาเอง',
                      'Vulnerable road users appear again. Actively look for pedestrians — do not wait for them to appear.');
        return _tip('คุณพบหัวข้อนี้มาแล้ว อ่านคำอธิบายด้วยมุมมองใหม่ — มุ่งที่ว่าอะไรแยกคำตอบที่ถูกออกจากผิด',
                    'You have met this topic before. Read the explanation from a fresh angle — focus on what separated the right answer from the wrong one.');
      }

      // ── Moderate wrong streak ────────────────────────────────────────────────
      if (!isOk && _wrongStreak >= 3)
        return _tip('อ่านคำอธิบายอย่างละเอียด การอ่านมากกว่าหนึ่งรอบช่วยได้',
                    'Read the explanation carefully. Reading it more than once is worthwhile.');
    }

    // ─ Confidence-calibrated fallback ─
    var _conf = _confidenceLevel();
    if (_conf === 'low')
      return isOk
        ? _tip('อ่านคำอธิบายอย่างใจเย็น ความเข้าใจใช้เวลาสร้าง แต่เมื่อเข้าใจแล้วจะอยู่กับคุณนาน',
               'Read the explanation calmly. Understanding takes time to build, but once built it stays with you.')
        : _tip('ใช้เวลากับคำอธิบาย สังเกตว่าอะไรที่แยกคำตอบที่ถูกออกจากผิด',
               'Take time with the explanation. Notice what separated the right and wrong answers.');
    return isOk
      ? _tip('จำสถานการณ์นี้ไว้เป็นภาพ การจำสถานการณ์จริงช่วยให้ขับขี่ได้ปลอดภัย',
             'Hold this situation visually in memory. Real recognition in traffic is a life-saving skill.')
      : _tip('เข้าใจสถานการณ์ ไม่ใช่แค่คำตอบ นั่นคือวิธีที่ความรู้จะคงอยู่ในสถานการณ์จริง',
             'Understand the situation, not just the answer. That is how knowledge stays with you in real driving.');
  }

  // ─ Topic-aware coaching — checks BOTH alerts, not just the first ─
  if (alerts.length > 0) {
    // Combine both alert labels so either alert can trigger the right tip
    var topics = alerts.map(function(a) { return a.label.toLowerCase(); }).join(' ');
    var type   = alerts[0].type;

    // ── Compound situations — two topics active simultaneously ──────────────
    // Traffic situations are rarely isolated. When two alerts match, address
    // the combination — this is closer to real driving instruction.
    if (alerts.length >= 2) {
      var isWeather = (type === 'weather' || alerts[1].type === 'weather'
                    || topics.indexOf('vinter') >= 0);
      var hasAvstand = (topics.indexOf('avstand') >= 0 || topics.indexOf('sekund') >= 0);
      var hasSikt    = (topics.indexOf('sikt') >= 0 || topics.indexOf('fart') >= 0);
      var hasForbi   = topics.indexOf('forbi') >= 0;
      var hasVikeplikt = topics.indexOf('vikeplikt') >= 0;
      var hasMyk     = (topics.indexOf('myk') >= 0 || topics.indexOf('fotgjenger') >= 0
                     || topics.indexOf('trafikant') >= 0);

      if (isWeather && hasAvstand)
        return isOk
          ? 'Glatt vei og avstand henger tett: 3-sekunders-regelen er et minimum — gi mer i dårlig vær.'
          : 'Glatt vei og kort avstand er svært farlig. I dårlig vær: dobbel avstand, halv fart.';

      if (hasSikt && hasForbi)
        return isOk
          ? 'Sikt og forbikjøring er uløselig knyttet — start aldri forbikjøring der du ikke ser klart frem.'
          : 'Der sikten er begrenset, er forbikjøring alltid uforsvarlig — vent, det er aldri verdt risikoen.';

      if (hasVikeplikt && hasMyk)
        return isOk
          ? 'Vikeplikt og myke trafikanter: gangfelt og kryss er steder der du alltid må forvente noen.'
          : 'Fotgjengere ved vikeplikt-punkt krever dobbel oppmerksomhet — se alltid før du kjører inn.';
    }

    if (type === 'weather' || topics.indexOf('vinter') >= 0)
      return isOk
        ? 'Husketips: grep og bremselengde varierer kraftig med vær og føre — kjør deretter.'
        : 'På glatt vei kan bremselengden øke kraftig. Les veibanen aktivt — tilpass alltid fart og følgeavstand.';

    if (topics.indexOf('sikt') >= 0 || topics.indexOf('fart') >= 0)
      return isOk
        ? 'God observasjonsteknikk skiller trygge sjåfører fra farlige. Tren blikket fremover.'
        : 'I all trafikk: se langt fremover og bygg inn sikkerhetsmarginer — spesielt i kurver.';

    if (topics.indexOf('sekund') >= 0 || topics.indexOf('avstand') >= 0)
      return isOk
        ? '3-sekunders-regelen er din enkleste forsikring mot oppkjøring — bruk den alltid.'
        : 'Øv deg: tell "én-tusen-ett, én-tusen-to, én-tusen-tre" mellom deg og bilen foran.';

    if (topics.indexOf('vikeplikt') >= 0)
      return isOk
        ? 'God vikepliktforståelse er grunnlaget for trygg ferdsel i alle kryss.'
        : 'Vikeplikt i kryss er årsaken til mange sidekollisjon — gjenkjenn situasjonene, ikke bare husk reglene.';

    if (topics.indexOf('myk') >= 0 || topics.indexOf('fotgjenger') >= 0 || topics.indexOf('trafikant') >= 0)
      return isOk
        ? 'Fotgjengere og syklister er de mest sårbare i trafikken — vær alltid ekstra oppmerksom.'
        : 'Gangfelt gir fotgjengere rett til å krysse trygt — bremse alltid ned i tide.';

    if (topics.indexOf('forbi') >= 0)
      return isOk
        ? 'Forbikjøring krever tålmodighet. Ikke press det — vent til det er klart sikkert.'
        : 'Feil vurdering ved forbikjøring er en vanlig årsak til frontalkollisjon — vent alltid til det er klart sikkert.';

    if (type === 'exam')
      return isOk
        ? 'Dette er et mønster mange overser i praksis — du gjenkjenner situasjonen, og det er det som teller.'
        : 'Dette handler om å forstå situasjonen tidlig. Gjenkjennelse i trafikken — ikke bare riktig svar — er målet.';

    if (topics.indexOf('rundkjøring') >= 0)
      return isOk
        ? 'Rundkjøringer er effektive men krever presisjon. Gi alltid vikeplikt ved innkjøring.'
        : 'Husk: trafikk allerede inne i rundkjøringen har forkjørsrett — vent til det er fritt.';

    if (topics.indexOf('brems') >= 0)
      return isOk
        ? 'God avstand er din viktigste buffer. Kortere bremselengde betyr mer tid til andre valg.'
        : 'Øv deg mentalt på nødbremsing — reaksjonen din avgjør om du rekker å stanse i tide.';

    if (topics.indexOf('møtende') >= 0 || topics.indexOf('tunnel') >= 0)
      return isOk
        ? 'Forutsigbar kjøring gjør deg lettere å se for møtende trafikk — hold linjen og farten.'
        : 'I tunnel og mørke: hold til høyre, bruk nærlys og senk farten — siktelengden er kortere.';

    if (topics.indexOf('tretthet') >= 0)
      return isOk
        ? 'Planlegg kjøreturer med pauser. Tretthet bygger seg opp gradvis og er vanskelig å oppdage.'
        : 'Tretthet angriper uten varsel. Tidlig stopp er alltid riktig — det finnes ingen snarvei.';

    if (topics.indexOf('grenseverdi') >= 0 || topics.indexOf('alkohol') >= 0)
      return isOk
        ? 'Null-toleranse er det sikreste valget — lovens grense er en juridisk terskel, ikke en anbefaling.'
        : 'Lovens 0,2-grense beskytter mot straff, ikke mot ulykker. Alkohol og kjøring hører ikke sammen.';

    if (topics.indexOf('reaksjonstid') >= 0)
      return isOk
        ? 'Rask reaksjon er trening — men god avstand er forsikringen som alltid er der.'
        : 'Ved 80 km/t tilbakelegger du 22 meter per sekund — avstand og årvåkenhet er den eneste reelle bufferen.';

    if (topics.indexOf('lys') >= 0)
      return isOk
        ? 'Riktig lys gjør deg synlig og gir deg sikt — to ting som redder liv.'
        : 'Lys er kommunikasjon i trafikken. Sjekk alltid at lysbruken er tilpasset situasjonen.';

    // ── Repeated topic — fresh angle when student keeps missing the same thing ─
    // _recentTopics[0] is current (just pushed); slice(1) looks at prior answers only.
    if (!isOk && _recentTopics.length > 1 && _recentTopics.slice(1).indexOf(alerts[0].label) >= 0) {
      var rLabel = alerts[0].label.toLowerCase();
      if (rLabel.indexOf('vikeplikt') >= 0)
        return 'Du har møtt vikeplikt tidligere. Prøv dette: finn bilen til høyre — den har som regel forkjørsrett.';
      if (rLabel.indexOf('avstand') >= 0 || rLabel.indexOf('sekund') >= 0)
        return 'Avstand dukker opp igjen. I praksis: velg et fast punkt, count til 3 etter bilen foran passerer det.';
      if (rLabel.indexOf('forbi') >= 0)
        return 'Forbikjøring er krevende. Huskeregel: i tvil — ikke kjør forbi. Det er alltid det riktige valget.';
      if (rLabel.indexOf('sikt') >= 0 || rLabel.indexOf('fart') >= 0)
        return 'Sikt og fart dukker opp igjen. Grunnregel: der du ser kort, kjør sakte. Alltid.';
      if (rLabel.indexOf('vinter') >= 0)
        return 'Kjøreforhold dukker opp igjen. Les veibanen — friksjon avgjør alt i dårlig vær.';
      if (rLabel.indexOf('gangfelt') >= 0 || rLabel.indexOf('myk') >= 0)
        return 'Myke trafikanter er et tilbakevendende tema. Se aktivt etter fotgjengere — ikke vent på at de synes.';
      return 'Du har møtt dette temaet tidligere. Les forklaringen med ny vinkel — fokuser på hva som skilte riktig fra galt svar.';
    }

    // ── Moderate wrong streak catch-all — only when no topic branch matched ───
    // Placed here so specific topic tips always take priority over generic support.
    if (!isOk && _wrongStreak >= 3)
      return 'Gå gjennom forklaringen nøye. Det lønner seg å lese den mer enn én gang.';
  }

  // ─ Confidence-calibrated generic fallback ─
  var confidence = _confidenceLevel();
  if (confidence === 'low')
    return isOk
      ? 'Les forklaringen nøye — forståelse tar tid å bygge, men sitter godt når den sitter.'
      : 'Ta deg tid med forklaringen. Legg merke til hva som skilte riktig og galt svar.';
  return isOk
    ? 'Fest situasjonen visuelt i minnet — gjenkjennelse i trafikken er en livsviktig ferdighet.'
    : 'Forstå situasjonen, ikke bare svaret. Det er slik kunnskap sitter i en virkelig situasjon.';
}

// ════════════════════════════════════════════
//  SE → FORSTÅ → VELG — SITUATION LENS
//  Norwegian curriculum-validated observation model (Trinn 1, §1.3).
//  Generates 3 quiet instructor prompts from question keywords.
//  Never reveals the answer — only observation cues.
// ════════════════════════════════════════════
function buildSituationLens(qText, expl) {
  var t = ((qText || '') + ' ' + (expl || '')).toLowerCase();

  // Each branch returns {see, understand, choose} in Norwegian
  if (/gangfelt|fotgjenger|gående|sykkel(?!veg)|syklistene?/i.test(t)) return {
    see:       'Legg merke til gang- og sykkeltrafikk nær veibanen',
    understand: 'Myke trafikanter er sårbare — ikke forvent at de ser deg',
    choose:    'Klar deg til å stanse, selv om du har forkjørsrett'
  };
  if (/vikeplikt|forkjørs|kryss|svinge\b/i.test(t)) return {
    see:       'Se etter skilt og vegmerking som angir vikeplikt',
    understand: 'Hvem har rett til å kjøre — og hvem venter?',
    choose:    'Avklar vikeplikt før du setter bilen i bevegelse'
  };
  if (/avstand|3.sekund|sikker\w*sone|bak\w*bil/i.test(t)) return {
    see:       'Observer avstanden til kjøretøyet foran',
    understand: 'Avstand er reaksjonstid omgjort til meter',
    choose:    'Hold 3 sekunders avstand — mer i dårlig vær'
  };
  if (/fart\b|fartsgrens|bremsing|bremselengd/i.test(t)) return {
    see:       'Les fartsgrenseskilt og vurder kjøreforholdene',
    understand: 'Riktig fart er ikke alltid det skiltene tillater',
    choose:    'Tilpass farten til situasjonen, ikke bare til skiltet'
  };
  if (/forbikj[øo]r|møtende|felt\w*skift/i.test(t)) return {
    see:       'Sjekk om det er klart foran og bak',
    understand: 'En forbikobling tar lenger tid enn du tror',
    choose:    'Forbikjøring kun når det er klart, lovlig og nødvendig'
  };
  if (/tunnel\b|bro\b|smal/i.test(t)) return {
    see:       'Legg merke til vegbredde og siktelengde',
    understand: 'Begrenset plass gir lite rom for feil',
    choose:    'Senk farten og plasser bilen presist'
  };
  if (/lys\b|nærlys|fjernlys|blende|mørk/i.test(t)) return {
    see:       'Observer lysene til møtende og framfor deg',
    understand: 'Feil lys kan blende andre eller gi deg dårlig sikt',
    choose:    'Bruk lys som er tilpasset forholdene og andre trafikanter'
  };
  if (/barn\b|skole\b|lekeplass|barn og unge/i.test(t)) return {
    see:       'Hold utkikk etter barn nær og ved siden av veien',
    understand: 'Barn opptrer uforutsigbart — de ser ikke faren',
    choose:    'Senk farten og vær klar til å stanse umiddelbart'
  };
  if (/glatt|is\b|snø|regn\b|vinter|veigrep|friksjon/i.test(t)) return {
    see:       'Vurder veigrep og siktforhold',
    understand: 'Glatt vei gir betydelig lengre bremselengde',
    choose:    'Øk avstand og senk farten — la veien bestemme farten'
  };
  if (/rundkjøring/i.test(t)) return {
    see:       'Se etter trafikk som allerede er inne i rundkjøringen',
    understand: 'Trafikk inni rundkjøringen har alltid forkjørsrett',
    choose:    'Vent til det er klart, og sving inn uten å skynde deg'
  };
  if (/parkering|stanse|stoppe/i.test(t)) return {
    see:       'Observer skilt, vegmerking og trafikken rundt deg',
    understand: 'Feil parkering hindrer andre og kan skape farlige situasjoner',
    choose:    'Parker der det er tillatt og trygt'
  };
  if (/promille|alkohol|ruspåvirk/i.test(t)) return {
    see:       'Les situasjonen nøye — hva er det spørsmålet egentlig handler om?',
    understand: '0,2 promille er lovens grense — men ingen «trygg» grense',
    choose:    'Nulltoleranse er det eneste sikre valget'
  };
  // Generic — always gives something useful
  return {
    see:       'Ta deg tid til å lese hele situasjonen',
    understand: 'Hva er den viktigste faktoren her?',
    choose:    'Velg det alternativet som er tryggest for alle i trafikken'
  };
}

function lensText(text) {
  var map = {
    // ── Pedestrians & cyclists ──
    'Legg merke til gang- og sykkeltrafikk nær veibanen': {th:'สังเกตคนเดินเท้าและจักรยานใกล้ทางรถ', en:'Notice pedestrians and cyclists near the roadway'},
    'Myke trafikanter er sårbare — ikke forvent at de ser deg': {th:'ผู้ใช้ถนนที่เปราะบางอาจไม่เห็นคุณ อย่าคาดหวังว่าเขาจะเห็น', en:'Vulnerable road users may not see you. Do not assume they have noticed you'},
    'Klar deg til å stanse, selv om du har forkjørsrett': {th:'เตรียมพร้อมหยุด แม้คุณมีสิทธิ์ไปก่อน', en:'Be ready to stop, even if you have priority'},
    // ── Yielding ──
    'Se etter skilt og vegmerking som angir vikeplikt': {th:'มองหาป้ายและเส้นบนถนนที่บอกเรื่องการให้ทาง', en:'Look for signs and road markings that show yielding rules'},
    'Hvem har rett til å kjøre — og hvem venter?': {th:'ใครมีสิทธิ์ไปก่อน และใครต้องรอ?', en:'Who has the right to go, and who must wait?'},
    'Avklar vikeplikt før du setter bilen i bevegelse': {th:'เข้าใจการให้ทางก่อนเริ่มขับต่อ', en:'Clarify yielding before moving the car'},
    // ── Following distance ──
    'Observer avstanden til kjøretøyet foran': {th:'สังเกตระยะห่างจากรถคันหน้า', en:'Observe the distance to the vehicle ahead'},
    'Avstand er reaksjonstid omgjort til meter': {th:'ระยะห่างคือเวลาตอบสนองที่กลายเป็นเมตร', en:'Distance is reaction time converted into meters'},
    'Hold 3 sekunders avstand — mer i dårlig vær': {th:'เว้น 3 วินาที และเพิ่มระยะเมื่อสภาพไม่ดี', en:'Keep 3 seconds distance, more in poor conditions'},
    // ── Speed ──
    'Les fartsgrenseskilt og vurder kjøreforholdene': {th:'อ่านป้ายจำกัดความเร็วและประเมินสภาพการขับขี่', en:'Read speed signs and assess driving conditions'},
    'Riktig fart er ikke alltid det skiltene tillater': {th:'ความเร็วที่ถูกต้องไม่ใช่แค่ตัวเลขบนป้าย', en:'The right speed is not always the posted maximum'},
    'Tilpass farten til situasjonen, ikke bare til skiltet': {th:'ปรับความเร็วตามสถานการณ์ ไม่ใช่ตามป้ายอย่างเดียว', en:'Adapt speed to the situation, not only to the sign'},
    // ── Overtaking ──
    'Sjekk om det er klart foran og bak': {th:'ตรวจว่าด้านหน้าและด้านหลังปลอดภัย', en:'Check whether it is clear ahead and behind'},
    'En forbikobling tar lenger tid enn du tror': {th:'การแซงใช้เวลานานกว่าที่คิด', en:'An overtake takes longer than you think'},
    'Forbikjøring kun når det er klart, lovlig og nødvendig': {th:'แซงเฉพาะเมื่อชัดเจน ถูกกฎหมาย และจำเป็น', en:'Overtake only when it is clear, legal, and necessary'},
    // ── Tunnel / narrow road ──
    'Legg merke til vegbredde og siktelengde': {th:'สังเกตความกว้างของถนนและระยะมองเห็น', en:'Notice the road width and sight distance'},
    'Begrenset plass gir lite rom for feil': {th:'พื้นที่จำกัดไม่เปิดโอกาสให้ผิดพลาด', en:'Limited space leaves little room for error'},
    'Senk farten og plasser bilen presist': {th:'ลดความเร็วและจัดตำแหน่งรถให้แม่นยำ', en:'Slow down and position the car precisely'},
    // ── Lights ──
    'Observer lysene til møtende og framfor deg': {th:'สังเกตไฟของรถที่สวนมาและรถข้างหน้า', en:'Observe the lights of oncoming traffic and vehicles ahead'},
    'Feil lys kan blende andre eller gi deg dårlig sikt': {th:'การใช้ไฟผิดอาจทำให้คนอื่นตาบอดหรือทำให้คุณมองเห็นได้น้อยลง', en:'Wrong lights can blind others or reduce your own visibility'},
    'Bruk lys som er tilpasset forholdene og andre trafikanter': {th:'ใช้ไฟที่เหมาะกับสภาพถนนและผู้ใช้ถนนคนอื่น', en:'Use lights suited to conditions and other road users'},
    // ── Children / school zones ──
    'Hold utkikk etter barn nær og ved siden av veien': {th:'ระวังเด็กที่อยู่ใกล้หรือข้างทาง', en:'Watch for children near and beside the road'},
    'Barn opptrer uforutsigbart — de ser ikke faren': {th:'เด็กมีพฤติกรรมที่คาดเดาไม่ได้ และมักไม่รู้อันตราย', en:'Children behave unpredictably — they do not see the danger'},
    'Senk farten og vær klar til å stanse umiddelbart': {th:'ลดความเร็วและพร้อมหยุดทันที', en:'Slow down and be ready to stop immediately'},
    // ── Slippery / winter conditions ──
    'Vurder veigrep og siktforhold': {th:'ประเมินแรงยึดเกาะถนนและทัศนวิสัย', en:'Assess road grip and visibility conditions'},
    'Glatt vei gir betydelig lengre bremselengde': {th:'ถนนลื่นทำให้ระยะเบรกยาวขึ้นมาก', en:'Slippery road significantly increases braking distance'},
    'Øk avstand og senk farten — la veien bestemme farten': {th:'เพิ่มระยะห่างและลดความเร็ว — ให้ถนนเป็นตัวกำหนดความเร็ว', en:'Increase distance and reduce speed — let the road set your pace'},
    // ── Roundabout ──
    'Se etter trafikk som allerede er inne i rundkjøringen': {th:'มองหารถที่อยู่ในวงเวียนแล้ว', en:'Look for traffic already inside the roundabout'},
    'Trafikk inni rundkjøringen har alltid forkjørsrett': {th:'รถที่อยู่ในวงเวียนมีสิทธิ์ก่อนเสมอ', en:'Traffic already in the roundabout always has priority'},
    'Vent til det er klart, og sving inn uten å skynde deg': {th:'รอจนโล่งแล้วค่อยเข้าโดยไม่รีบ', en:'Wait until it is clear, then enter without rushing'},
    // ── Parking / stopping ──
    'Observer skilt, vegmerking og trafikken rundt deg': {th:'สังเกตป้าย เส้นบนถนน และการจราจรรอบข้าง', en:'Observe signs, road markings, and surrounding traffic'},
    'Feil parkering hindrer andre og kan skape farlige situasjoner': {th:'การจอดผิดที่กีดขวางผู้อื่นและอาจเกิดอันตราย', en:'Incorrect parking obstructs others and can create dangerous situations'},
    'Parker der det er tillatt og trygt': {th:'จอดเฉพาะที่อนุญาตและปลอดภัย', en:'Park only where it is permitted and safe'},
    // ── Alcohol ──
    'Les situasjonen nøye — hva er det spørsmålet egentlig handler om?': {th:'อ่านสถานการณ์อย่างละเอียด — คำถามนี้ถามเรื่องอะไรกันแน่?', en:'Read the situation carefully — what is this question really about?'},
    '0,2 promille er lovens grense — men ingen «trygg» grense': {th:'0.2 คือขีดจำกัดทางกฎหมาย ไม่ใช่ขีดจำกัดที่ปลอดภัย', en:'0.2 is the legal limit — not a safe limit'},
    'Nulltoleranse er det eneste sikre valget': {th:'ไม่ดื่มเลยคือทางเลือกที่ปลอดภัยที่สุดเท่านั้น', en:'Zero tolerance is the only truly safe choice'},
    // ── Generic fallback ──
    'Ta deg tid til å lese hele situasjonen': {th:'ใช้เวลาอ่านสถานการณ์ทั้งหมด', en:'Take time to read the whole situation'},
    'Hva er den viktigste faktoren her?': {th:'ปัจจัยที่สำคัญที่สุดในที่นี้คืออะไร?', en:'What is the most important factor here?'},
    'Velg det alternativet som er tryggest for alle i trafikken': {th:'เลือกตัวเลือกที่ปลอดภัยที่สุดสำหรับทุกคนในการจราจร', en:'Choose the option that is safest for everyone in traffic'}
  };
  var item = map[text];
  return item ? (item[appLang] || text) : text;
}

function buildSituationLensHtml(qText, expl) {
  var lens = buildSituationLens(qText, expl);
  return '<div class="q-observe">'
    + '<div class="q-observe-row"><span class="q-observe-tag">' + escH(t('see_tag')) + '</span>' + escH(lensText(lens.see)) + '</div>'
    + '<div class="q-observe-row"><span class="q-observe-tag">' + escH(t('understand_tag')) + '</span>' + escH(lensText(lens.understand)) + '</div>'
    + '<div class="q-observe-row"><span class="q-observe-tag">' + escH(t('choose_tag')) + '</span>' + escH(lensText(lens.choose)) + '</div>'
    + '</div>';
}

// ════════════════════════════════════════════
//  REVIEW MODE — Øv på feil
//  Shows wrong questions from history one by one.
//  Read-only reflection — no answer options.
// ════════════════════════════════════════════
function startReview(wrongQs) {
  if (!wrongQs || !wrongQs.length) return;
  _reviewMode      = true;
  _reviewQuestions = wrongQs;
  _reviewIdx       = 0;
  closeHistDetail();
  showScreen('screenQuiz');
  // Update quiz header for review context
  var progLbl = document.getElementById('qProgLbl');
  if (progLbl) progLbl.textContent = t('review_title');
  var progFill = document.getElementById('qProgFill');
  if (progFill) progFill.style.width = '0%';
  var scoreEl = document.getElementById('qScoreNum');
  if (scoreEl) scoreEl.textContent = '0';
  // Clear right panel
  var aiBody = document.getElementById('quizAiBody');
  if (aiBody) aiBody.innerHTML = '<div class="quiz-ai-idle"><div class="quiz-ai-idle-icon">📖</div><div class="quiz-ai-idle-text">' + escH(t('review_idle')) + '</div></div>';
  renderReviewCard();
}

function renderReviewCard() {
  var qCard = document.getElementById('qCard');
  if (!qCard) return;

  var progFill = document.getElementById('qProgFill');
  if (progFill) progFill.style.width = Math.round(_reviewIdx / _reviewQuestions.length * 100) + '%';

  if (_reviewIdx >= _reviewQuestions.length) {
    // Review complete
    qCard.innerHTML = '<div class="q-mid"><div class="rv-done">'
      + '<div class="rv-done-icon">✓</div>'
      + '<div class="rv-done-head">' + escH(t('review_done')) + '</div>'
      + '<div class="rv-done-body">' + escH(tf('review_done_body', {count:_reviewQuestions.length})) + '</div>'
      + '<button class="rv-done-btn" onclick="showTab(\'home\')">' + escH(t('backhome')) + '</button>'
      + '</div></div>';
    return;
  }

  var q = _reviewQuestions[_reviewIdx];
  var isLast = (_reviewIdx + 1 >= _reviewQuestions.length);
  var nextLabel = isLast ? t('review_finish') : t('next');

  var rvSlotId = 'vidSlot_rv_' + _reviewIdx;
  qCard.innerHTML = '<div class="q-mid"><div class="rv-wrap">'
    + '<div class="rv-header">' + escH(t('review_progress')) + ' ' + (_reviewIdx + 1) + ' ' + escH(t('of')) + ' ' + _reviewQuestions.length + '</div>'
    + (q.question_text ? '<div class="rv-question">' + escH(q.question_text) + '</div>' : '')
    + (q.user_answer    ? '<div class="rv-answer rv-wrong">❌&nbsp; ' + escH(t('you_answered')) + ': <strong>' + escH(q.user_answer) + '</strong></div>' : '')
    + (q.correct_answer ? '<div class="rv-answer rv-right">✓&nbsp; ' + escH(t('correct_answer')) + ': <strong>' + escH(q.correct_answer) + '</strong></div>' : '')
    + (q.explanation
        ? '<div class="rv-expl"><div class="rv-expl-lbl">' + escH(t('explanation')) + '</div><div class="rv-expl-txt">' + escH(q.explanation) + '</div></div>'
        : '')
    + '<div id="' + rvSlotId + '"></div>'
    + '<button class="rv-next" onclick="reviewNext()">' + nextLabel + '</button>'
    + '</div></div>';

  // Async video suggestion — fills the slot above the Neste button
  if (q.explanation) {
    fetchVideoForTopic(_dangerLabel(q.explanation)).then(function(v) {
      _injectVideo(rvSlotId, rvSlotId + '_vid', v);
    });
  }
}

function reviewNext() {
  _reviewIdx++;
  renderReviewCard();
}

function endReview() {
  _reviewMode     = false;
  _reviewQuestions = [];
  _reviewIdx      = 0;
}

// ════════════════════════════════════════════
//  CONTEXTUAL VIDEO SUGGESTION SYSTEM
//
//  Architecture — three surface points:
//  1. Wrong answer AI panel  → fetchVideoForTopic(_dangerLabel(expl))
//  2. Sign detail panel      → fetchVideoForSign(sign.id, sign.group_name)
//  3. Mistake review cards   → fetchVideoForTopic(topicFromQuestion)
//
//  All fetches are async + non-blocking. A session-level cache prevents
//  duplicate API calls for the same topic/sign within one session.
//  Graceful empty state: if no videos in DB, nothing renders.
//
//  Topic tags must match the _dangerLabel() output strings:
//  'Bremsing', 'Vikeplikt', 'Avstand og sikkerhetssone', 'Forbikjøring',
//  'Myke trafikanter', 'Trafikkskilt', 'Vær og veiforhold', 'Kjøretøyteknikk',
//  'Tretthet', 'Grenseverdi', 'Fart', 'Møtende trafikk'
// ════════════════════════════════════════════
var _videoCache = {}; // session cache: 'topic:X' or 'sign:X' → video object | null

function _ytId(url) {
  if (!url) return '';
  var m = url.match(/youtu\.be\/([a-zA-Z0-9_-]{11})|youtube\.com\/(?:watch\?v=|embed\/|shorts\/)([a-zA-Z0-9_-]{11})/);
  return m ? (m[1] || m[2] || '') : '';
}

function _ytThumb(url) {
  var id = _ytId(url);
  return id ? 'https://img.youtube.com/vi/' + id + '/mqdefault.jpg' : '';
}

function _fmtDur(secs) {
  if (!secs) return '';
  var m = Math.floor(secs / 60), s = secs % 60;
  return m + ':' + (s < 10 ? '0' : '') + s;
}

function buildVideoCard(v) {
  if (!v) return '';
  var title = escH(
    appLang === 'th' ? (v.title_th || v.title_no || v.title_en || v.title || '') :
    appLang === 'en' ? (v.title_en || v.title_no || v.title_th || v.title || '') :
    (v.title_no || v.title_en || v.title_th || v.title || '')
  );
  if (!title) return '';
  var url   = escH(v.youtube_url || '');
  if (!url) return '';
  var thumb = v.thumbnail_url || _ytThumb(v.youtube_url);
  var dur   = _fmtDur(v.duration_seconds);
  return '<a class="vid-card" href="' + url + '" target="_blank" rel="noopener">'
    + '<div class="vid-thumb-wrap">'
      + (thumb ? '<img class="vid-thumb" src="' + escH(thumb) + '" loading="lazy" alt="">' : '▶')
    + '</div>'
    + '<div class="vid-info">'
      + '<div class="vid-lbl">' + escH(t('video_short')) + '</div>'
      + '<div class="vid-title">' + title + '</div>'
      + (dur ? '<div class="vid-dur">' + dur + '</div>' : '')
    + '</div>'
    + '<div class="vid-arrow">→</div>'
    + '</a>';
}

async function fetchVideoForTopic(tag) {
  if (!tag || tag === 'Forstå situasjonen') return null;
  var key = 'topic:' + tag;
  if (Object.prototype.hasOwnProperty.call(_videoCache, key)) return _videoCache[key];
  try {
    var data = await api('GET', '/api/videos/for-topic?tags=' + encodeURIComponent(tag) + '&limit=1');
    var v = Array.isArray(data) && data.length ? data[0] : null;
    _videoCache[key] = v;
    return v;
  } catch(e) { _videoCache[key] = null; return null; }
}

async function fetchVideoForSign(signId, signGroup) {
  if (!signId) return null;
  var key = 'sign:' + signId;
  if (Object.prototype.hasOwnProperty.call(_videoCache, key)) return _videoCache[key];
  try {
    var url = '/api/videos/for-sign/' + encodeURIComponent(signId);
    if (signGroup) url += '?group=' + encodeURIComponent(signGroup);
    var data = await api('GET', url);
    var v = Array.isArray(data) && data.length ? data[0] : null;
    _videoCache[key] = v;
    return v;
  } catch(e) { _videoCache[key] = null; return null; }
}

// Inject a video card into a container element.
// Placed BEFORE the instructor tip (last .quiz-ai-tip child) so it appears
// in the natural reading flow, not buried at the very bottom.
// slotId prevents double-injection on the same container.
function _injectVideo(containerId, slotId, v) {
  var container = typeof containerId === 'string'
    ? document.getElementById(containerId) : containerId;
  if (!v || !container) return;
  if (document.getElementById(slotId)) return; // already shown
  var wrap = document.createElement('div');
  wrap.id = slotId;
  wrap.className = 'vid-section ai-block';
  wrap.style.cssText = '--i:8; animation:aiBlockIn .22s ease .05s both;';
  wrap.innerHTML = '<div class="vid-sec-lbl">' + escH(t('video_watch')) + '</div>' + buildVideoCard(v);
  // Insert before the instructor tip so video reads as part of the explanation flow
  var tip = container.querySelector('.quiz-ai-tip');
  if (tip) container.insertBefore(wrap, tip);
  else container.appendChild(wrap);
}

// ── Selective number emphasis for safety-critical text ───────────────────────
// Boldens key numerical safety values (3 sekunder, km/t, promille, distance).
// Called AFTER escH() — patterns only target known ASCII strings, no XSS risk.
// Applied ONLY to primary card text, not expanded/secondary content.
// Sparse by design: one or two bolded numbers per explanation at most.
function emphExpl(text) {
  if (!text) return '';
  var s = escH(text);
  s = s.replace(/\b(3 sekunder?|3-sekunders-regelen)\b/gi, '<strong>$1</strong>');
  s = s.replace(/\b(\d{2,3}\s*km\/t)\b/gi,                '<strong>$1</strong>');
  s = s.replace(/\b(0[,.]2 promille)\b/gi,                '<strong>$1</strong>');
  s = s.replace(/\b(22\s*meter)\b/gi,                     '<strong>$1</strong>');
  return s;
}

// ── Session-inferred explanation depth ──────────────────────────────────────
// 'beginner'  → early session or high wrong rate → show full text immediately
// 'standard'  → mid-session, moderate rate       → short + expandable
// 'advanced'  → many answered, low wrong rate    → short + expandable (same)
// The distinction is transparent to the student — it simply feels natural.
function _explDepth() {
  if (_sessionAnswered <= 5) return 'beginner';
  var rate = _sessionAnswered > 0 ? _sessionWrongTotal / _sessionAnswered : 0;
  if (rate > 0.45) return 'beginner';
  return 'standard'; // advanced currently same UX as standard; reserved for future depth features
}

// ── Shared AI learning content builder ──────────────────────────────────────
// Feeds BOTH desktop right panel and mobile inline section.
// Pedagogical order: verdict → key insight → detail → context alerts → tip.
// Tone is constructive throughout — learning, not judging.
function buildAiHtml(isOk, expl) {
  var i          = 0;
  var parts      = splitExpl(expl);
  var alerts     = classifyAlerts(expl);
  var confidence = _confidenceLevel(); // computed once — drives depth, alerts, tip visibility

  // Topic memory — push BEFORE buildInstructorTip so repeated-topic detection works
  if (alerts.length > 0) {
    _recentTopics.unshift(alerts[0].label);
    if (_recentTopics.length > 4) _recentTopics.pop();
  }

  // 1 ── Verdict — only shown for correct answers (wrong already has q-feedback bar)
  var html = '';
  if (isOk) {
    var verdictText = _nextCorrectPhrase();
    html = '<div class="quiz-ai-verdict ok">'
      + '<span class="quiz-ai-verdict-icon">✅</span>'
      + '<span>' + verdictText + '</span>'
      + '</div>';
  }

  if (!isOk && expl) {
    // 2a ── Wrong: topic-targeted label + key insight (safety numbers bolded)
    html += '<div class="quiz-ai-danger ai-block" style="--i:' + (i++) + '">'
      + '<div class="quiz-ai-danger-icon">📌</div>'
      + '<div style="min-width:0">'
      + '<div class="quiz-ai-danger-label">' + escH(topicLabel(_dangerLabel(expl))) + '</div>'
      + '<div class="quiz-ai-danger-text">' + emphExpl(parts.short) + '</div>'
      + '</div></div>';

    // 2b ── Full detail if explanation has more depth
    if (parts.rest) {
      html += '<div class="quiz-ai-explain ai-block" style="--i:' + (i++) + '">'
        + '<div class="quiz-ai-card-label">📖 ' + escH(t('more_details')) + '</div>'
        + '<div class="quiz-ai-card-text">' + escH(parts.rest) + '</div>'
        + '</div>';
    }

  } else if (isOk && expl) {
    // 3 ── Correct: depth + confidence adaptive explanation
    //   'beginner' depth        → full text immediately (no friction)
    //   'standard' low-conf     → auto-expand (struggling student needs full context)
    //   'standard' medium/high  → short + expandable (student self-selects depth)
    var depth = _explDepth();
    html += '<div class="quiz-ai-explain ai-block" style="--i:' + (i++) + '">'
      + '<div class="quiz-ai-card-label">📖 ' + escH(t('explanation')) + '</div>'
      + '<div class="quiz-ai-card-text">' + emphExpl(parts.short) + '</div>';
    if (parts.rest) {
      if (depth === 'beginner') {
        // Beginners: full text — reduce friction, maximise available context
        html += '<div class="quiz-ai-card-text" style="margin-top:11px;padding-top:11px;'
          + 'border-top:1px solid rgba(255,255,255,.07)">' + escH(parts.rest) + '</div>';
      } else {
        // Standard: auto-open for low-confidence students, closed otherwise
        var autoOpen = (confidence === 'low');
        html += '<button class="ai-expand-btn' + (autoOpen ? ' expanded' : '') + '" onclick="'
          + 'var c=this.nextElementSibling;'
          + 'c.classList.toggle(\'open\');'
          + 'this.classList.toggle(\'expanded\');'
          + 'this.textContent=c.classList.contains(\'open\')?\'' + escH(t('show_less')) + '\':\'' + escH(t('show_more')) + '\''
          + '">' + (autoOpen ? escH(t('show_less')) : escH(t('show_more'))) + '</button>'
          + '<div class="ai-expand-content' + (autoOpen ? ' open' : '') + '">' + escH(parts.rest) + '</div>';
      }
    }
    html += '</div>';
  }

  // 4 ── Smart context alerts
  // High-confidence correct answers get at most 1 alert — quieter panel.
  // All other states get up to 2 — struggling students benefit from full context.
  var maxAlerts = (confidence === 'high' && isOk) ? 1 : 2;
  alerts.slice(0, maxAlerts).forEach(function(a) {
    html += '<div class="ai-alert ai-alert-' + a.type + ' ai-block" style="--i:' + (i++) + '">'
      + '<span class="ai-alert-icon">' + a.icon + '</span>'
      + '<div style="min-width:0">'
      + '<div class="ai-alert-label">' + escH(topicLabel(a.label)) + '</div>'
      + '<div class="ai-alert-text">' + escH(a.text) + '</div>'
      + '</div></div>';
  });

  // 5 ── Instructor tip
  // Suppressed for high-confidence correct answers — fluent students don't
  // need coaching after every right answer. Visible for all wrong answers and
  // any correct answer where the student is still building confidence.
  if (!(isOk && confidence === 'high')) {
    html += '<div class="quiz-ai-tip ai-block" style="--i:' + (i++) + '">'
      + '<div class="quiz-ai-tip-icon">💡</div>'
      + '<div style="min-width:0">'
      + '<div class="quiz-ai-tip-label">' + escH(t('driving_teacher')) + '</div>'
      + '<div class="quiz-ai-tip-text">' + escH(buildInstructorTip(isOk, alerts)) + '</div>'
      + '</div></div>';
  }

  // ── Future architecture hooks (wired, hidden until features land) ─────────
  // To activate a feature: set display:block on its slot and inject content.
  html += '<div class="quiz-ai-future-hooks" aria-hidden="true">'
        + '<div class="quiz-ai-slot" data-hook="voice"           data-feature="ai-voice-teacher"></div>'
        + '<div class="quiz-ai-slot" data-hook="danger-overlay"  data-feature="visual-danger-zones"></div>'
        + '<div class="quiz-ai-slot" data-hook="traffic-overlay" data-feature="animated-traffic-scene"></div>'
        + '<div class="quiz-ai-slot" data-hook="hint"            data-feature="ai-hint-generator"></div>'
        + '</div>';

  return html;
}

function updateAiPanel(isOk, expl) {
  var html = buildAiHtml(isOk, expl);
  var okBad = isOk ? 'ok' : 'bad';

  // ── Desktop: right panel ──────────────────────────────────────────────────

  // Image box border glow
  var imgbox = document.querySelector('.quiz-ai-imgbox');
  if (imgbox) imgbox.className = 'quiz-ai-imgbox glow-' + okBad;

  // Image brightness flash — remove class first to restart animation
  var aiImg = document.getElementById('quizAiImg');
  if (aiImg) {
    aiImg.classList.remove('flash-ok', 'flash-bad');
    void aiImg.offsetWidth; // reflow trigger
    aiImg.classList.add('flash-' + okBad);
  }

  // Colour tint overlay
  var overlay = document.getElementById('quizAiOverlay');
  if (overlay) overlay.className = 'quiz-ai-img-overlay result-' + okBad;

  // Status chip
  var status = document.getElementById('quizAiStatus');
  if (status) {
    status.textContent = isOk ? ('✅ ' + t('correct_answer')) : ('↩ ' + t('explanation'));
    status.className = 'quiz-ai-status ' + okBad;
  }

  // Image badge — show detected topic to link image ↔ explanation
  var badge = document.getElementById('quizAiImgBadge');
  if (badge) {
    var topicRaw = expl ? _dangerLabel(expl) : '';
    badge.textContent = (topicRaw && topicRaw !== 'Forstå situasjonen')
      ? '📍 ' + topicLabel(topicRaw) : t('traffic_situation');
  }

  // Inject content and scroll back to top
  var body = document.getElementById('quizAiBody');
  if (body) { body.innerHTML = html; body.scrollTop = 0; }

  // ── Mobile: inline section below answers ─────────────────────────────────
  var mobile = document.getElementById('quizAiMobile');
  if (mobile) mobile.innerHTML = html;

  // ── Contextual video suggestion (wrong answers only — one card, async) ────
  // Fires after panel renders so it never blocks the primary feedback.
  if (!isOk && expl) {
    var _vidTag = _dangerLabel(expl);
    fetchVideoForTopic(_vidTag).then(function(v) {
      _injectVideo('quizAiBody',   'vidSlot_aiDesktop', v);
      _injectVideo('quizAiMobile', 'vidSlot_aiMobile',  v);
    });
  }

  // Mobile question image tint
  var imgWrap = document.getElementById('qImgWrap');
  if (imgWrap) {
    imgWrap.style.outline   = isOk ? '2.5px solid rgba(16,185,129,.55)' : '2.5px solid rgba(239,68,68,.50)';
    imgWrap.style.boxShadow = isOk ? '0 0 18px rgba(16,185,129,.22)'    : '0 0 18px rgba(239,68,68,.20)';
    imgWrap.style.transition = 'outline .3s ease, box-shadow .3s ease';
  }
}

function nextQ() {
  if (_aiPanelTimer) { clearTimeout(_aiPanelTimer); _aiPanelTimer = null; } // never let a delayed panel land on the next question
  // Review mode uses its own card renderer — skip normal quiz flow
  if (_reviewMode) { reviewNext(); return; }
  if (!qAnswered) return;
  qIdx++;
  if (qIdx >= questions.length) { showEnd(); return; }
  if (!checkPaywall()) return;
  renderQuestion();
}

function goBack() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  ttsPlaying = false;
  stopExamTimer();
  isExamMode = false;
  if (_reviewMode) endReview();
  showTab(activeTab && activeTab !== 'quiz' ? activeTab : 'home');
}

// ════════════════════════════════════════════
//  BOOKMARKS
// ════════════════════════════════════════════
async function toggleBookmark(qId) {
  if (!deviceId || !qId) { toast(t('bookmark_login')); return; }
  var btn = document.getElementById('qBmBtn');
  if (bookmarkedIds[qId]) {
    try {
      await api('DELETE', '/api/bookmarks/' + encodeURIComponent(deviceId) + '/' + encodeURIComponent(qId));
      delete bookmarkedIds[qId];
      if (btn) { btn.classList.remove('bookmarked'); }
      toast(t('bookmark_removed'));
    } catch(e) { toast(t('bookmark_remove_failed')); }
  } else {
    try {
      await api('POST', '/api/bookmarks', { device_id: deviceId, question_id: qId });
      bookmarkedIds[qId] = true;
      if (btn) { btn.classList.add('bookmarked'); }
      toast(t('bookmark_added'));
    } catch(e) { toast(t('bookmark_add_failed')); }
  }
}

async function loadBookmarks() {
  if (!deviceId) {
    document.getElementById('bmScroll').innerHTML = '<div class="empty-state"><div class="es-icon">🔒</div><p>' + t('bookmarks_login') + '</p></div>';
    return;
  }
  var scroll = document.getElementById('bmScroll');
  scroll.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    var bms = await api('GET', '/api/bookmarked-questions/' + encodeURIComponent(deviceId));
    if (!Array.isArray(bms)) bms = bms.questions || bms.bookmarks || [];
    // Update bookmarkedIds cache
    bookmarkedIds = {};
    bms.forEach(function(q) {
      var qId = q._id || q.id || q.question_id || '';
      if (qId) bookmarkedIds[qId] = true;
    });
    document.getElementById('bmCount').textContent = '(' + bms.length + ')';
    if (!bms.length) {
      scroll.innerHTML = '<div class="empty-state"><div class="es-icon">🔖</div><p>' + t('bookmarks_empty') + '</p></div>';
      return;
    }
    scroll.innerHTML = bms.map(function(q) {
      var qId   = escH(String(q._id || q.id || q.question_id || ''));
      var imgUrl = q.bildeUrl || q.image_url || '';
      var qText  = pickLang(q.question) || pickField(q, 'question_text') || '';
      var correct = (q.correctOptionId || q.correct_answer || '').toUpperCase();
      var ansText = '';
      if (q.options && Array.isArray(q.options)) {
        var correctOpt = q.options.find(function(o) { return String(o.id || o.key || '').toUpperCase() === correct; });
        if (correctOpt) ansText = pickLang(correctOpt.text) || pickLang(correctOpt) || '';
      }
      if (!ansText) {
        ansText = pickField(q, 'answer_' + correct.toLowerCase()) || '';
      }
      var imgHtml = imgUrl ? '<div class="bm-card-img-wrap"><img class="bm-card-img" src="' + escH(imgUrl) + '" alt="" onerror="this.parentElement.style.display=\'none\'"></div>' : '';
      var ansHtml = ansText ? '<div class="bm-card-ans">✓ ' + escH(ansText) + '</div>' : '';
      return '<div class="bm-card">'
        + '<button class="bm-card-remove" onclick="removeBookmark(\'' + qId + '\',this.closest(\'.bm-card\'))" title="Fjern">✕</button>'
        + imgHtml
        + '<div class="bm-card-q">' + escH(qText) + '</div>'
        + ansHtml
        + '</div>';
    }).join('');
  } catch(e) {
    scroll.innerHTML = '<div class="empty-state"><div class="es-icon">⚠️</div><p>' + t('generic_error') + '<br>' + escH(e.message) + '</p></div>';
  }
}

// ════════════════════════════════════════════
//  SIGNS GALLERY
// ════════════════════════════════════════════
var signsLoaded = false;
var _signGroups = [];
var _allSigns = [];
// Visual identity for each of the 9 Norwegian sign groups (keyed by group number).
// Color drives the dot + glow; desc is shown under the name as a one-line learning hint.
var SIGN_GROUP_META = {
  1: { color:'#EF4444',
       desc:{ no:'Viser hvem som har forkjørsrett i krysset',
              th:'แสดงว่าใครมีสิทธิ์ขับก่อน', en:'Who has priority at junctions' } },
  2: { color:'#F59E0B',
       desc:{ no:'Varsler om fare fremover — vær forberedt',
              th:'เตือนอันตรายข้างหน้า ระวังให้พร้อม', en:'Danger ahead — be prepared' } },
  3: { color:'#DC2626',
       desc:{ no:'Forbyr en handling — du plikter å overholde det',
              th:'ห้ามกระทำการ — ต้องปฏิบัติตามทุกครั้ง', en:'Forbidden — must be obeyed' } },
  4: { color:'#3B82F6',
       desc:{ no:'Påbyr en bestemt atferd — obligatorisk',
              th:'บังคับให้กระทำ — ต้องปฏิบัติตาม', en:'Action required — mandatory' } },
  5: { color:'#10B981',
       desc:{ no:'Gir informasjon om vegen, tilbud og regler',
              th:'ให้ข้อมูลเกี่ยวกับถนนและกฎจราจร', en:'Information about road and rules' } },
  6: { color:'#8B5CF6',
       desc:{ no:'Viser nærliggende servicetilbud og fasiliteter',
              th:'แสดงบริการและสิ่งอำนวยความสะดวกใกล้เคียง', en:'Nearby services and facilities' } },
  7: { color:'#06B6D4',
       desc:{ no:'Angir retning, avstand og reisemål',
              th:'แสดงทิศทาง ระยะทาง และจุดหมาย', en:'Direction, distance and destination' } },
  8: { color:'#94A3B8',
       desc:{ no:'Presiserer eller begrenser meningen til andre skilt',
              th:'เพิ่มรายละเอียดหรือจำกัดความหมายของป้ายอื่น', en:'Supplements or restricts other signs' } },
  9: { color:'#F97316',
       desc:{ no:'Markerer vegkanter, farer og hindringer',
              th:'ทำเครื่องหมายขอบถนน อันตราย และสิ่งกีดขวาง', en:'Marks road edges, hazards and obstacles' } },
};
var SIGN_GROUP_ORDER = {
  'Vikepliktskilt': 1,
  'Fareskilt': 2,
  'Forbudsskilt': 3,
  'Påbudsskilt': 4,
  'Opplysningsskilt': 5,
  'Serviceskilt': 6,
  'Vegvisningsskilt': 7,
  'Underskilt': 8,
  'Markeringsskilt': 9
};

async function loadSigns() {
  var scroll = document.getElementById('signsScroll');
  if (!scroll) return;
  if (signsLoaded && scroll.querySelector('.sg-header')) return;
  scroll.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    var groups = await api('GET', '/api/traffic-signs');
    if (!Array.isArray(groups)) throw new Error('Ugyldig respons');
    _signGroups = groups;
    _allSigns = [];

    // Count total signs
    var total = groups.reduce(function(n, g) { return n + (g.signs ? g.signs.length : 0); }, 0);
    var countEl = document.getElementById('signsCount');
    if (countEl) countEl.textContent = total ? total + ' ' + t('signs_word') : '';

    if (!total) {
      scroll.innerHTML = '<div class="empty-state"><div class="es-icon">🚦</div><p>' + t('signs_empty') + '</p></div>';
      return;
    }

    // Calm intro line — tells the learner what the section is for
    scroll.innerHTML = '<div class="signs-intro">' + escH(t('signs_intro')) + '</div>';

    groups.forEach(function(group) {
      if (!group.signs || !group.signs.length) return;

      // Rich group header — color identity + description + count
      var gNum  = group.group || SIGN_GROUP_ORDER[group.group_key] || 0;
      var gMeta = SIGN_GROUP_META[gNum] || { color:'var(--orange)', desc:{} };
      var gName = group.group_name;
      var gLabel = typeof gName === 'object'
        ? (gName[appLang] || gName.no || gName.en || '')
        : (gName || '');
      var gDesc = (gMeta.desc[appLang] || gMeta.desc.no || '');
      var gCount = group.signs.length;

      var headerEl = document.createElement('div');
      headerEl.className = 'sg-header';
      headerEl.innerHTML =
        '<div class="sg-dot" style="--sg-color:' + gMeta.color + '"></div>'
        + '<div class="sg-info">'
          + '<div class="sg-name">' + escH(gLabel) + '</div>'
          + (gDesc ? '<div class="sg-desc">' + escH(gDesc) + '</div>' : '')
        + '</div>'
        + '<div class="sg-count">' + gCount + ' ' + escH(t('signs_word')) + '</div>';
      scroll.appendChild(headerEl);

      // Grid
      var grid = document.createElement('div');
      grid.className = 'signs-grid';
      group.signs.forEach(function(sign) {
        sign._groupName = group.group_name;
        sign._groupKey = JSON.stringify(group.group_name || {});
        sign._groupIndex = groups.indexOf(group);
        _allSigns.push(sign);
        var sName = sign.name;
        var nameText = typeof sName === 'object'
          ? (sName[appLang] || (appLang !== 'no' ? sName.en : '') || sName.no || '')
          : (sName || '');
        var imgUrl = sign.image_url || '';
        var card = document.createElement('div');
        card.className = 'sign-card';
        card.innerHTML =
          (imgUrl
            ? '<div class="sign-img-wrap"><img class="sign-img" src="' + escH(imgUrl) + '" alt="" loading="lazy"></div>'
            : '') +
          '<div class="sign-ans">' + escH(nameText || '–') + '</div>';
        (function(s){ card.onclick = function(){ openSignDetail(s); }; })(sign);
        grid.appendChild(card);
      });
      scroll.appendChild(grid);
    });

    signsLoaded = true;
  } catch(e) {
    scroll.innerHTML = '<div class="empty-state"><div class="es-icon">⚠️</div><p>' + escH(e.message || 'Feil ved lasting') + '</p></div>';
  }
}

// ════════════════════════════════════════════
//  HISTORY
// ════════════════════════════════════════════
async function loadHistory() {
  if (!deviceId) {
    document.getElementById('histScroll').innerHTML = '<div class="empty-state"><div class="es-icon">🔒</div><p>' + t('history_login') + '</p></div>';
    return;
  }
  var scroll = document.getElementById('histScroll');
  scroll.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    var data = await api('GET', '/api/quiz-attempts/' + encodeURIComponent(deviceId) + '?limit=50&_=' + Date.now());
    var attempts = Array.isArray(data) ? data : (data.attempts || data.results || []);
    attempts = _mergeAttempts(attempts, _readLocalAttempts().concat(_lastSavedAttempt ? [_lastSavedAttempt] : []));
    _histAttempts = attempts; // store for detail panel access
    document.getElementById('histCount').textContent = '(' + attempts.length + ')';
    if (!attempts.length) {
      scroll.innerHTML = '<div class="empty-state"><div class="es-icon">📊</div><p>' + t('history_empty') + '</p></div>';
      return;
    }
    scroll.innerHTML = attempts.map(function(a, idx) {
      var pct     = Math.round(a.score_percentage || 0);
      var correct = a.correct_answers || 0;
      var total   = a.total_questions || 0;
      var wrong   = total - correct;
      var barColor = pct >= 80 ? 'var(--green)' : pct >= 60 ? 'var(--orange)' : '#EF4444';

      var ready = readinessForPct(pct, false);
      var badgeCls = 'hist-badge-' + ready.cls;
      var badgeTxt = ready.text;

      var modeText  = modeLabel(a.mode);
      var modeSub    = a.category ? catName(a.category) : '';

      var dateStr = '';
      if (a.completed_at || a.started_at) {
        var d = new Date(a.completed_at || a.started_at);
        dateStr = d.toLocaleDateString(localeForLang(), {day:'2-digit', month:'short'}) + ', ' + d.toLocaleTimeString(localeForLang(), {hour:'2-digit', minute:'2-digit'});
      }

      var passedBit = '';
      if (a.passed === true)       passedBit = '<span class="hist-stat-sep">·</span><span class="hist-stat-good">' + t('passed') + '</span>';
      else if (a.passed === false) passedBit = '<span class="hist-stat-sep">·</span><span class="hist-stat-bad">' + t('not_passed') + '</span>';

      return '<div class="hist-card" onclick="openHistDetail(' + idx + ')" style="animation:aiBlockIn .22s ease both;animation-delay:' + (idx * 35) + 'ms">'
        + '<div class="hist-card-top">'
          + '<div>'
            + '<div class="hist-mode">' + escH(modeText) + '</div>'
            + (modeSub ? '<div class="hist-mode-sub">' + escH(modeSub) + '</div>' : '')
          + '</div>'
          + '<div class="hist-badge ' + badgeCls + '">' + badgeTxt + '</div>'
        + '</div>'
        + '<div class="hist-score-row">'
          + '<div class="hist-pct">' + pct + '%</div>'
          + '<div class="hist-bar-wrap"><div class="hist-bar-fill" style="width:' + pct + '%;background:' + barColor + '"></div></div>'
        + '</div>'
        + '<div class="hist-stats-row">'
          + '<span class="hist-stat-good">✓ ' + correct + ' ' + t('correct_count') + '</span>'
          + '<span class="hist-stat-sep">·</span>'
          + '<span class="hist-stat-bad">✗ ' + wrong + ' ' + t('wrong_count') + '</span>'
          + '<span class="hist-stat-sep">·</span>'
          + '<span class="hist-stat-tot">' + t('of') + ' ' + total + '</span>'
          + passedBit
        + '</div>'
        + '<div class="hist-card-footer">'
          + '<div class="hist-date-new">' + escH(dateStr) + '</div>'
          + '<div class="hist-card-actions">'
            + '<button class="hist-btn hist-btn-sec" onclick="event.stopPropagation();openHistDetail(' + idx + ')">' + t('details') + '</button>'
            + '<button class="hist-btn hist-btn-pri" onclick="event.stopPropagation();retryAttempt(' + idx + ')">' + t('retry') + '</button>'
          + '</div>'
        + '</div>'
        + '</div>';
    }).join('');
  } catch(e) {
    scroll.innerHTML = '<div class="empty-state"><div class="es-icon">⚠️</div><p>' + t('history_load_error') + '<br>' + escH(e.message) + '</p></div>';
  }
}

function openHistDetail(idx) {
  _histOpenIdx = idx;
  var a = _histAttempts[idx];
  if (!a) return;
  var pct     = Math.round(a.score_percentage || 0);
  var correct = a.correct_answers || 0;
  var total   = a.total_questions || 0;
  var wrong   = total - correct;

  // Mode label
  var modeStr = modeLabel(a.mode);
  if (a.category) modeStr += ' — ' + catName(a.category);
  document.getElementById('hpModeLbl').textContent = modeStr;

  // Score headline
  document.getElementById('hpScoreBig').textContent = pct + '%';
  document.getElementById('hpScoreSub').textContent = tf('result_score', {correct:correct, total:total});

  // Badge
  var ready = readinessForPct(pct, true);
  var badgeCls = 'hp-badge-' + ready.cls;
  var badgeTxt = ready.text;
  var badge = document.getElementById('hpBadge');
  badge.className = 'hp-badge ' + badgeCls;
  badge.textContent = badgeTxt;

  // Stats grid
  document.getElementById('hpStats').innerHTML =
      '<div class="hp-stat"><div class="hp-stat-num good">' + correct + '</div><div class="hp-stat-lbl">' + escH(t('correct_count')) + '</div></div>'
    + '<div class="hp-stat"><div class="hp-stat-num bad">' + wrong + '</div><div class="hp-stat-lbl">' + escH(t('wrong_count')) + '</div></div>'
    + '<div class="hp-stat"><div class="hp-stat-num">' + total + '</div><div class="hp-stat-lbl">' + escH(t('total_count')) + '</div></div>';

  // Wrong questions body
  var qs = Array.isArray(a.questions_answered) ? a.questions_answered : [];
  var wrongQs = qs.filter(function(q) { return q.is_correct === false; });
  var bodyHtml = '';
  if (wrongQs.length) {
    bodyHtml += '<div class="hp-section-label">' + escH(t('wrong_answers')) + ' (' + wrongQs.length + ')</div>';
    bodyHtml += wrongQs.map(function(q, i) {
      var delay    = i * 40;
      var userTxt  = q.user_answer    ? t('you_answered') + ': '  + q.user_answer    : '';
      var rightTxt = q.correct_answer ? t('correct_answer') + ': ' + q.correct_answer : '';
      return '<div class="hp-q-card" style="animation:aiBlockIn .22s ease both;animation-delay:' + delay + 'ms">'
        + '<div class="hp-q-num">' + escH(t('question')) + ' ' + (i + 1) + '</div>'
        + (q.question_text ? '<div class="hp-q-text">' + escH(q.question_text) + '</div>' : '')
        + (userTxt  ? '<div class="hp-q-ans hp-q-ans-wrong">' + escH(userTxt)  + '</div>' : '')
        + (rightTxt ? '<div class="hp-q-ans hp-q-ans-right">' + escH(rightTxt) + '</div>' : '')
        + (q.explanation
            ? '<div class="hp-q-expl-label">' + escH(t('explanation')) + '</div><div class="hp-q-expl">' + escH(q.explanation) + '</div>'
            : '')
        + '</div>';
    }).join('');
  } else if (qs.length) {
    bodyHtml = '<div class="hp-no-data">' + t('no_wrong_answers') + '</div>';
  } else {
    bodyHtml = '<div class="hp-no-data">' + t('old_quiz_details') + '</div>';
  }
  document.getElementById('hpBody').innerHTML = bodyHtml;

  // Wire retry button
  document.getElementById('hpRetryBtn').onclick = function() { retryAttempt(idx); };

  // Wire / show "Gå gjennom feil" review button
  var hpActions = document.getElementById('hpActions');
  if (hpActions) {
    // Remove any previously added review btn
    var oldRv = document.getElementById('hpReviewBtn');
    if (oldRv) oldRv.remove();
    if (wrongQs.length) {
      var rvBtn = document.createElement('button');
      rvBtn.id = 'hpReviewBtn';
      rvBtn.className = 'hp-btn-sec';
      rvBtn.textContent = tf('review_wrong_count', {count: wrongQs.length});
      rvBtn.onclick = function() { startReview(wrongQs); };
      // Insert before "Lukk" (last button)
      var lukk = hpActions.lastElementChild;
      hpActions.insertBefore(rvBtn, lukk);
    }
  }

  // Open
  document.getElementById('histPanelBackdrop').classList.add('open');
  document.getElementById('histPanel').classList.add('open');
}

function closeHistDetail() {
  _histOpenIdx = null;
  document.getElementById('histPanelBackdrop').classList.remove('open');
  document.getElementById('histPanel').classList.remove('open');
}

function retryAttempt(idx) {
  var a = _histAttempts[idx];
  if (!a) return;
  closeHistDetail();
  if (a.mode === 'exam') {
    startExam();
  } else if (a.mode === 'category' && a.category) {
    startQuiz(a.category, a.category);
  } else {
    startRandomQuiz();
  }
}

async function removeBookmark(qId, cardEl) {
  if (!deviceId) return;
  try {
    await api('DELETE', '/api/bookmarks/' + encodeURIComponent(deviceId) + '/' + encodeURIComponent(qId));
    delete bookmarkedIds[qId];
    if (cardEl) cardEl.remove();
    var remaining = document.querySelectorAll('.bm-card').length;
    document.getElementById('bmCount').textContent = '(' + remaining + ')';
    if (!remaining) {
      document.getElementById('bmScroll').innerHTML = '<div class="empty-state"><div class="es-icon">🔖</div><p>' + t('bookmarks_empty') + '</p></div>';
    }
    toast(t('bookmark_removed'));
  } catch(e) { toast(t('bookmark_remove_failed')); }
}

// ════════════════════════════════════════════
//  END SCREEN
// ════════════════════════════════════════════
// ── Debrief translation layer ─────────────────────────────────────────────────
// Converts internal performance data into instructor-voiced guidance.
// NEVER exposes raw failure counts to the learner — only forward-facing language.
// This is the architectural separation between the truth model and the communication model.
function _buildDebrief(pct, total) {
  // Find the most-missed topic (only meaningful if 2+ errors on same label)
  var topTopic = null, topCount = 0;
  Object.keys(_topicErrors).forEach(function(label) {
    if (_topicErrors[label] > topCount) { topCount = _topicErrors[label]; topTopic = label; }
  });
  if (topCount < 2) topTopic = null;

  var heading, body;

  if (isExamMode) {
    if (pct >= 85) {
      heading = t('result_exam_pass_head');
      body = t('result_exam_pass_body');
    } else {
      heading = t('result_exam_fail_head');
      body = topTopic
        ? (appLang === 'th' ? 'ควรใช้เวลาเพิ่มกับเรื่อง ' + topicLabel(topTopic) + ' ฝึกต่อแล้วลองอีกครั้ง'
          : appLang === 'en' ? 'It is worth spending more time on ' + topicLabel(topTopic).toLowerCase() + '. Practice it and try again.'
          : 'Det er verdt å bruke litt mer tid på ' + topTopic.toLowerCase() + '. Øv på det og prøv igjen.')
        : t('result_more_body');
    }
  } else if (pct >= 85) {
    heading = t('result_solid_head');
    body = total >= 15
      ? t('result_solid_body')
      : (appLang === 'th' ? 'คุณทำได้ดี ลองชุดที่ยาวขึ้นเพื่อยืนยันความเข้าใจ'
        : appLang === 'en' ? 'You did well. Try a longer set to confirm the understanding.'
        : 'Du traff godt. Prøv et lengre sett for å bekrefte forståelsen.');
  } else if (pct >= 65) {
    heading = t('result_right_way_head');
    body = topTopic
      ? (appLang === 'th' ? 'ส่วนใหญ่เข้าใจดีแล้ว มาฝึกเพิ่มอีกนิดกับ ' + topicLabel(topTopic)
        : appLang === 'en' ? 'Most of the understanding is good. Let us spend a bit more time on ' + topicLabel(topTopic).toLowerCase() + '.'
        : 'Forståelsen er god på det meste. La oss bruke litt mer tid på ' + topTopic.toLowerCase() + '.')
      : (appLang === 'th' ? 'บางสถานการณ์ยังไม่ติดแน่น ซึ่งเป็นเรื่องปกติ ฝึกต่ออย่างใจเย็น'
        : appLang === 'en' ? 'Some situations have not fully settled yet. That is normal. Keep practicing.'
        : 'Noen situasjoner har ikke satt seg helt ennå — det er normalt. Fortsett å øve.');
  } else if (pct >= 40) {
    heading = t('result_more_head');
    body = topTopic
      ? (appLang === 'th' ? 'ควรดูเรื่อง ' + topicLabel(topTopic) + ' ให้ละเอียดขึ้น อ่านคำอธิบายอย่างใจเย็น'
        : appLang === 'en' ? 'It is worth looking more closely at ' + topicLabel(topTopic).toLowerCase() + '. Read the explanations carefully.'
        : 'Det er verdt å gå litt nærmere inn på ' + topTopic.toLowerCase() + '. Les forklaringene grundig.')
      : t('result_more_body');
  } else {
    heading = t('result_learn_head');
    body = t('result_learn_body');
  }

  return { heading: heading, body: body, topTopic: topTopic };
}

function showEnd() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  stopExamTimer();
  showScreen('screenEnd');
  var total  = questions.length;
  var pct    = total > 0 ? Math.round(qScore / total * 100) : 0;

  // ── Display (wrapped in try so a DOM error never blocks the save) ──
  try {
    var debrief = _buildDebrief(pct, total);
    var el;
    el = document.getElementById('endScoreQuiet'); if (el) el.textContent = tf('result_score', {correct:qScore, total:total});
    el = document.getElementById('endHeading');    if (el) el.textContent = debrief.heading;
    el = document.getElementById('endBody');       if (el) el.textContent = debrief.body;
    var focusEl = document.getElementById('endFocus');
    var focusTopicEl = document.getElementById('endFocusTopic');
    if (debrief.topTopic && focusEl && focusTopicEl) {
      focusTopicEl.textContent = topicLabel(debrief.topTopic);
      focusEl.style.display = '';
    } else if (focusEl) {
      focusEl.style.display = 'none';
    }
  } catch(displayErr) { console.warn('showEnd display error:', displayErr); }

  // ── Save attempt — always runs, even if display above failed ──
  if (deviceId && total > 0) {
    var mode = isExamMode ? 'exam' : (currentCat ? 'category' : 'daily');
    var completedAt = new Date().toISOString();
    var clientAttemptId = 'web_' + completedAt + '_' + Math.random().toString(36).slice(2, 8);
    var attemptData = {
      client_attempt_id: clientAttemptId,
      device_id: deviceId,
      mode: mode,
      category: currentCat ? currentCat.name : null,
      total_questions: total,
      correct_answers: qScore,
      score_percentage: pct,
      passed: isExamMode ? pct >= 85 : null,
      questions_answered: _sessionAnswers.length ? _sessionAnswers : questions.map(function(q, i) {
        return { question_id: String(q._id || q.id || q.question_id || ''), index: i };
      }),
      started_at: quizStartedAt || completedAt,
      completed_at: completedAt
    };
    // Build a local mirror immediately so History shows it even before the DB catches up
    _lastSavedAttempt = {
      id: clientAttemptId,
      client_attempt_id: clientAttemptId,
      device_id: attemptData.device_id,
      mode: attemptData.mode,
      category: attemptData.category,
      total_questions: attemptData.total_questions,
      correct_answers: attemptData.correct_answers,
      score_percentage: attemptData.score_percentage,
      passed: attemptData.passed,
      started_at: attemptData.started_at,
      completed_at: completedAt,
      questions_answered: _sessionAnswers.slice()
    };
    _writeLocalAttempt(_lastSavedAttempt);
    api('POST', '/api/quiz-attempts', attemptData)
      .then(function(saved) {
        _writeLocalAttempt(saved || _lastSavedAttempt);
        toast(t('result_saved'), 2000);
      })
      .catch(function(e) {
        console.warn('Quiz attempt save failed:', e.message);
        toast(t('result_save_failed') + e.message, 4000);
      });
  }
}

function retryQuiz() {
  if (currentCat) startQuiz(currentCat.id, currentCat.name);
  else startRandomQuiz();
}

// ════════════════════════════════════════════
//  TTS
// ════════════════════════════════════════════
function speakQ() {
  var q = questions[qIdx];
  if (!q || !window.speechSynthesis) return;
  if (ttsPlaying) {
    window.speechSynthesis.cancel();
    ttsPlaying = false; updateTtsBtn(false); return;
  }
  var text = pickLang(q.question) || q.question_text_no || '';
  if (!text) return;
  var utt = new SpeechSynthesisUtterance(text);
  utt.lang = appLang === 'th' ? 'th-TH' : appLang === 'no' ? 'nb-NO' : 'en-US';
  utt.rate = ttsRate;
  utt.volume = ttsVolume;
  ttsPlaying = true; updateTtsBtn(true);
  utt.onend   = function() { ttsPlaying = false; updateTtsBtn(false); };
  utt.onerror = function() { ttsPlaying = false; updateTtsBtn(false); };
  window.speechSynthesis.speak(utt);
}
function updateTtsBtn(playing) {
  var btn = document.getElementById('qTtsBtn');
  if (!btn) return;
  btn.textContent = playing ? '⏸' : '▶';
  btn.classList.toggle('playing', playing);
}
function setRate(r, el) {
  ttsRate = r;
  document.querySelectorAll('.spd-btn').forEach(function(b) {
    b.classList.toggle('active', parseFloat(b.dataset.rate) === r);
  });
}
function setVolume(v) {
  ttsVolume = v;
  _ls.set('t2d_vol', String(v));
  document.querySelectorAll('.vol-btn').forEach(function(b) {
    b.classList.toggle('active', parseFloat(b.dataset.vol) === v);
  });
}

// ════════════════════════════════════════════
//  SOUND
// ════════════════════════════════════════════
var _audioCtx = null;
function _getAudioCtx() {
  if (!_audioCtx) {
    try { _audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch(e) {}
  }
  if (_audioCtx && _audioCtx.state === 'suspended') {
    _audioCtx.resume().catch(function(){});
  }
  return _audioCtx;
}
// Unlock AudioContext on first user interaction (required by iOS Safari)
document.addEventListener('touchstart', function() { _getAudioCtx(); }, { once: true, passive: true });
document.addEventListener('click', function() { _getAudioCtx(); }, { once: true });

function playSound(type) {
  if (!soundOn) return;
  try {
    var ctx = _getAudioCtx();
    if (!ctx) return;
    if (type === 'correct') {
      var freqs = feedbackStyle === 'strong' ? [523.25, 659.25, 783.99, 1046.5] : [523.25, 659.25, 783.99];
      freqs.forEach(function(freq, i) {
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.12);
        gain.gain.setValueAtTime(feedbackStyle === 'strong' ? 0.4 : 0.3, ctx.currentTime + i * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 1.1);
        osc.start(ctx.currentTime + i * 0.12);
        osc.stop(ctx.currentTime + i * 0.12 + 1.1);
      });
    } else {
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.35);
      gain.gain.setValueAtTime(feedbackStyle === 'strong' ? 0.35 : 0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.4);
    }
  } catch(e) {}
}

// ════════════════════════════════════════════
//  SETTINGS
// ════════════════════════════════════════════
function loadSettings() {
  // Profile hero
  var email = (user && user.email) ? user.email : '–';
  var name  = (user && user.name)  ? user.name  : (user && user.email ? user.email.split('@')[0] : '–');
  var initials = name !== '–' ? name.charAt(0).toUpperCase() : '👤';
  var avatarEl = document.getElementById('settAvatar');
  if (avatarEl) avatarEl.textContent = initials;
  var nameEl = document.getElementById('settName');
  if (nameEl) nameEl.textContent = name;
  document.getElementById('settEmail').textContent = email;
  var badges = document.getElementById('settBadges');
  badges.innerHTML = '';
  if (user && user.is_premium) badges.innerHTML += '<span class="premium-badge">⭐ Premium</span>';
  if (user && user.is_admin)   badges.innerHTML += '<span class="admin-badge">🔧 Admin</span>';

  ['TH','NO','EN'].forEach(function(l) {
    var btn = document.getElementById('lang' + l);
    if (btn) btn.classList.toggle('active', appLang === l.toLowerCase());
  });

  document.getElementById('soundToggle').checked = soundOn;

  // TTS tempo buttons in settings
  var spdEl = document.getElementById('settSpdBtns');
  if (spdEl) {
    spdEl.innerHTML = [0.5, 0.75, 1, 1.5, 2].map(function(r) {
      return '<button class="spd-btn' + (ttsRate === r ? ' active' : '') + '" data-rate="' + r + '" onclick="setRate(' + r + ',this)">' + r + 'x</button>';
    }).join('');
  }

  // TTS volume buttons in settings
  var volEl = document.getElementById('settVolBtns');
  if (volEl) {
    volEl.innerHTML = [[0.5,'🔈'],[0.75,'🔉'],[1.0,'🔊']].map(function(item) {
      var v = item[0], icon = item[1];
      return '<button class="vol-btn' + (ttsVolume === v ? ' active' : '') + '" data-vol="' + v + '" onclick="setVolume(' + v + ')">' + icon + '</button>';
    }).join('');
  }

  // Sync feedback style buttons
  document.querySelectorAll('.seg-btn[onclick*="setFeedback"]').forEach(function(b) {
    var styleVal = b.getAttribute('onclick').match(/setFeedback\('(\w+)'/);
    if (styleVal) b.classList.toggle('active', styleVal[1] === feedbackStyle);
  });

  var savedTheme = _ls.get('t2d_theme') || 'dark';
  ['light','dark','system'].forEach(function(t) {
    var id = 'themeBtn' + t.charAt(0).toUpperCase() + t.slice(1);
    var btn = document.getElementById(id);
    if (btn) btn.classList.toggle('active', savedTheme === t);
  });
}

function setLang(lang) {
  appLang = lang;
  _ls.set('t2d_lang', lang);
  ['TH','NO','EN'].forEach(function(l) {
    var btn = document.getElementById('lang' + l);
    if (btn) btn.classList.toggle('active', lang === l.toLowerCase());
    var topBtn = document.getElementById('topLang' + l);
    if (topBtn) topBtn.classList.toggle('active', lang === l.toLowerCase());
  });
  applyUILang();
  // Reset signs cache so it reloads in new language
  signsLoaded = false;
  var signsScreen = document.getElementById('screenSigns');
  if (signsScreen && signsScreen.classList.contains('active')) loadSigns();
  // Re-render categories in new language (force re-render by resetting cache)
  if (catsLoaded) { catsLoaded = false; loadCategories(); }
  // Re-render quiz if active so question+answers switch language immediately
  var quizScreen = document.getElementById('screenQuiz');
  if (quizScreen && quizScreen.classList.contains('active') && questions.length) {
    renderQuestion();
  }
  // Re-render bookmarks if active
  var bmScreen = document.getElementById('screenBookmarks');
  if (bmScreen && bmScreen.classList.contains('active')) {
    loadBookmarks();
  }
  var histScreen = document.getElementById('screenHistory');
  if (histScreen && histScreen.classList.contains('active')) {
    loadHistory();
  }
  var teacherScreen = document.getElementById('screenTeacher');
  if (teacherScreen && teacherScreen.classList.contains('active')) {
    loadTeacher();
  }
  if (_signPanelData) {
    _signPanelLang = lang === 'th' ? 'th' : lang === 'en' ? 'en' : 'no';
    _renderSignPanel();
  }
  if (document.getElementById('histPanel') && document.getElementById('histPanel').classList.contains('open')) {
    if (_histOpenIdx !== null) openHistDetail(_histOpenIdx);
  }
  toast(t('lang_updated'));
}

// ════════════════════════════════════════════
//  MICHAEL TRAFIKKLÆRER — CHAT
// ════════════════════════════════════════════
var _teacherSessionId    = null;
var _teacherHasUserMsg   = false;   // true once user sends first message
var _teacherTyping       = false;
var _teacherWelcomeLang  = null;    // tracks which language the welcome was rendered in

// ── Strip markdown → plain text ──────────────────────────────
function _stripMd(text) {
  return text
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/__(.+?)__/g, '$1')
    .replace(/\*([^*\n]+?)\*/g, '$1')
    .replace(/_([^_\n]+?)_/g, '$1')
    .replace(/^[-*]{3,}$/gm, '')
    .replace(/^[\-\*]\s+/gm, '• ')
    .replace(/`([^`]+)`/g, '$1')
    .trim();
}

// ── Build rich DOM content for assistant bubble ───────────────
// Detects: advice boxes (🚗 Praktisk råd: / 🚗 คำแนะนำ: / 🚗 Practical tip:)
//          section headers (short lines ending in :)
//          regular paragraphs (blocks separated by blank lines)
function _buildAssistantContent(text, container) {
  var cleaned = _stripMd(text);
  var blocks = cleaned.split(/\n{2,}/);  // split on blank lines

  blocks.forEach(function(block) {
    block = block.trim();
    if (!block) return;

    // Advice box: block starts with advice header
    if (/^🚗\s*(Praktisk råd|คำแนะนำ|Practical tip)/i.test(block)) {
      var box = document.createElement('div');
      box.className = 'tm-advice-box';
      var lines = block.split('\n');
      var hdr = document.createElement('div');
      hdr.className = 'tm-advice-hdr';
      hdr.textContent = lines[0].trim();
      box.appendChild(hdr);
      lines.slice(1).forEach(function(l) {
        l = l.trim();
        if (!l) return;
        var s = document.createElement('span');
        s.className = 'tm-advice-line';
        s.textContent = l;
        box.appendChild(s);
      });
      container.appendChild(box);
      return;
    }

    // Section header: single short line ending with ":"
    var singleLine = block.indexOf('\n') === -1;
    if (singleLine && block.endsWith(':') && block.length < 40) {
      var hdrEl = document.createElement('span');
      hdrEl.className = 'tm-section-hdr';
      hdrEl.textContent = block;
      container.appendChild(hdrEl);
      return;
    }

    // Regular paragraph — preserve internal line breaks
    var para = document.createElement('span');
    para.className = 'tm-para';
    para.textContent = block;
    container.appendChild(para);
  });
}

async function loadTeacher() {
  var tNameEl = document.getElementById('teacherNameLbl');
  if (tNameEl) tNameEl.textContent = t('teacher_name');
  var tInput = document.getElementById('teacherInput');
  if (tInput) tInput.placeholder = t('teacher_placeholder');

  // Fetch welcome from backend (single source of truth)
  if (!_teacherHasUserMsg && _teacherWelcomeLang !== appLang) {
    _teacherWelcomeLang = appLang;
    var msgs = document.getElementById('teacherMessages');
    if (msgs) {
      msgs.innerHTML = '';
      try {
        var wRes = await fetch('/api/teacher/welcome?lang=' + appLang);
        var wData = await wRes.json();
        _teacherAppendBubble('assistant', wData.welcome || '');
      } catch(e) {
        // Fallback if API unreachable
        var fallback = {
          no: 'Sawatdee 😊\n\nJeg er Michael.\n\nTrafikklærer med 16 års erfaring i Oslo.',
          th: 'สวัสดีครับ 😊\n\nผมชื่อไมเคิล\n\nครูสอนขับรถที่มีประสบการณ์ 16 ปีในออสโล',
          en: 'Sawatdee 😊\n\nI\'m Michael.\n\nDriving instructor with 16 years of experience in Oslo.'
        };
        _teacherAppendBubble('assistant', fallback[appLang] || fallback.no);
      }
    }
  }

  // Fetch topics from backend (single source of truth) and populate chips + side panel
  try {
    var tRes = await fetch('/api/teacher/topics?lang=' + appLang);
    var tData = await tRes.json();
    var topics = tData.topics || [];

    // Update initial suggestion chips
    var chipEls = document.querySelectorAll('#teacherSuggestions .teacher-chip');
    topics.forEach(function(topic, i) {
      var chip = chipEls[i];
      if (!chip) return;
      var label = chip.querySelector('.chip-lbl');
      if (label) label.textContent = topic.text;
      chip.dataset.msg = topic.icon + ' ' + topic.text;
      chip.onclick = (function(msg){ return function(){ teacherSend(msg); }; })(topic.icon + ' ' + topic.text);
    });

    // Update side panel buttons
    var tspBtns = document.querySelectorAll('.tsp-btn');
    topics.forEach(function(topic, i) {
      var btn = tspBtns[i];
      if (!btn) return;
      btn.innerHTML = topic.icon + ' <span>' + topic.text + '</span>';
      btn.onclick = (function(msg){ return function(){ teacherSend(msg); }; })(topic.icon + ' ' + topic.text);
    });
  } catch(e) {
    // Fallback: keep existing hardcoded chips
    _teacherUpdateChips();
    var tspMap2 = { sign:'tsp_sign', vikeplikt:'tsp_vikeplikt', rule:'tsp_rule', practice:'tsp_practice', theory:'tsp_theory', app:'tsp_app' };
    document.querySelectorAll('[data-tsp]').forEach(function(el) {
      var key = tspMap2[el.getAttribute('data-tsp')];
      if (!key) return;
      el.textContent = t(key);
      var btn = el.closest('.tsp-btn');
      if (btn) { var label = t(key); btn.onclick = (function(lbl){ return function(){ teacherSend(lbl); }; })(label); }
    });
  }
}

function _teacherUpdateChips() {
  document.querySelectorAll('.teacher-chip').forEach(function(chip) {
    var lbl = chip.querySelector('.chip-lbl');
    if (!lbl) return;
    var msg = chip.getAttribute('data-msg-' + appLang) || chip.getAttribute('data-msg-no') || '';
    lbl.textContent = msg.replace(/^[\S]{1,2}\s+/, ''); // strip leading emoji+space
    chip.dataset.msg = msg;
  });
}

function _teacherAppendBubble(role, text) {
  var msgs = document.getElementById('teacherMessages');
  if (!msgs) return;
  if (role === 'user') _teacherHasUserMsg = true;
  var row = document.createElement('div');
  row.className = 'tm-row ' + role;
  if (role === 'assistant') {
    var av = document.createElement('div');
    av.className = 'tm-av';
    av.textContent = '🚗';
    row.appendChild(av);
  }
  var bubble = document.createElement('div');
  bubble.className = 'tm-bubble ' + role;
  if (role === 'assistant') {
    _buildAssistantContent(text, bubble);
  } else {
    bubble.textContent = text;
  }
  row.appendChild(bubble);
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
}

function _teacherShowTyping() {
  var msgs = document.getElementById('teacherMessages');
  if (!msgs) return;
  var row = document.createElement('div');
  row.className = 'tm-row assistant';
  row.id = 'teacherTypingRow';
  var av = document.createElement('div');
  av.className = 'tm-av';
  av.textContent = '🚗';
  row.appendChild(av);
  var bubble = document.createElement('div');
  bubble.className = 'tm-bubble assistant tm-typing';
  bubble.innerHTML = '<span></span><span></span><span></span>';
  row.appendChild(bubble);
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
}

function _teacherHideTyping() {
  var row = document.getElementById('teacherTypingRow');
  if (row) row.remove();
}

function _teacherHideSuggestions() {
  var s = document.getElementById('teacherSuggestions');
  if (s) s.style.display = 'none';
}

function _teacherRemoveChips() {
  // Remove all existing reply chip rows before sending a new message
  document.querySelectorAll('.tm-chips').forEach(function(el) { el.remove(); });
}

function _teacherAppendChips(chips) {
  if (!chips || !chips.length) return;
  var msgs = document.getElementById('teacherMessages');
  if (!msgs) return;
  var row = document.createElement('div');
  row.className = 'tm-chips';
  // Heading
  var hdr = document.createElement('div');
  hdr.className = 'tm-chips-hdr';
  hdr.textContent = t('choose_topic');
  row.appendChild(hdr);
  chips.forEach(function(label) {
    var btn = document.createElement('button');
    btn.className = 'tm-chip-btn';
    btn.textContent = label;
    btn.onclick = function() { teacherSend(label); };
    row.appendChild(btn);
  });
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
}

async function teacherSend(overrideMsg) {
  var input = document.getElementById('teacherInput');
  var msg = (overrideMsg || (input && input.value) || '').trim();
  if (!msg || _teacherTyping) return;

  if (input && !overrideMsg) input.value = '';
  _teacherTyping = true;
  _teacherHideSuggestions();
  _teacherRemoveChips();  // clear old reply chips

  var sendBtn = document.getElementById('teacherSendBtn');
  if (sendBtn) sendBtn.disabled = true;

  _teacherAppendBubble('user', msg);
  _teacherShowTyping();

  try {
    var res = await fetch('/api/teacher/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: _teacherSessionId, message: msg, language: appLang })
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var data = await res.json();
    if (data.session_id && !_teacherSessionId) _teacherSessionId = data.session_id;
    _teacherHideTyping();
    _teacherAppendBubble('assistant', data.reply || t('teacher_error'));
    _teacherAppendChips(data.suggestions || []);
  } catch(e) {
    _teacherHideTyping();
    _teacherAppendBubble('assistant', t('teacher_error'));
  } finally {
    _teacherTyping = false;
    if (sendBtn) sendBtn.disabled = false;
    // Only re-focus input when user typed manually — not after a chip tap.
    // On mobile, focus() re-opens the keyboard mid-read which feels like a freeze.
    if (input && !overrideMsg) input.focus();
  }
}

function toggleSound(el) {
  soundOn = el.checked;
  _ls.set('t2d_sound', soundOn ? 'on' : 'off');
}

function setFeedback(style, btn) {
  feedbackStyle = style;
  _ls.set('t2d_feedback', style);
  btn.closest('.seg-ctrl').querySelectorAll('.seg-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
}

function setTheme(theme, btn) {
  if (btn) {
    btn.closest('.seg-ctrl').querySelectorAll('.seg-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
  }
  _ls.set('t2d_theme', theme);
  applyTheme(theme);
}

function applyThemeFromStorage() { applyTheme(_ls.get('t2d_theme') || 'dark'); }

function applyTheme(theme) {
  if (theme === 'system') {
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  } else {
    document.documentElement.setAttribute('data-theme', theme);
  }
}

// ════════════════════════════════════════════
//  UTILS
// ════════════════════════════════════════════
function escH(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;');
}

// ════════════════════════════════════════════
//  KEYBOARD
// ════════════════════════════════════════════
document.addEventListener('keydown', function(e) {
  var active = document.querySelector('.screen.active');
  if (!active) return;
  var id = active.id;

  if (id === 'screenAuth' && e.key === 'Enter') {
    var lf = document.getElementById('formLogin');
    var rf = document.getElementById('formRegister');
    var ff = document.getElementById('formForgot');
    var fr = document.getElementById('formReset');
    if (lf && lf.style.display !== 'none') doLogin();
    else if (rf && rf.style.display !== 'none') doRegister();
    else if (ff && ff.style.display !== 'none') doForgot();
    else if (fr && fr.style.display !== 'none') doResetPassword();
  }

  if (id === 'screenQuiz' && qAnswered) {
    if (e.key === 'Enter' || e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault(); nextQ();
    }
  }

  if (id === 'screenQuiz' && !qAnswered) {
    var letters = ['a','b','c','d','1','2','3','4'];
    var idx = letters.indexOf(e.key.toLowerCase());
    if (idx >= 0) {
      var real = idx > 3 ? idx - 4 : idx;
      var btns = document.querySelectorAll('.ans-btn');
      if (btns[real]) btns[real].click();
    }
  }
});

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function() {
  if (_ls.get('t2d_theme') === 'system') applyTheme('system');
});

// ════════════════════════════════════════════
//  SIGN DETAIL PANEL
// ════════════════════════════════════════════
var _signPanelData = null;
var _signPanelLang = 'no';
var _signFavorites = [];
try { _signFavorites = JSON.parse(localStorage.getItem('t2d_signFavs') || '[]'); } catch(e) {}

function openSignDetail(sign) {
  _signPanelData = sign;
  _signPanelLang = appLang === 'th' ? 'th' : appLang === 'en' ? 'en' : 'no';
  _renderSignPanel();
  document.getElementById('signPanelBackdrop').classList.add('open');
  document.getElementById('signPanel').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeSignDetail() {
  document.getElementById('signPanelBackdrop').classList.remove('open');
  document.getElementById('signPanel').classList.remove('open');
  document.body.style.overflow = '';
  if (window.speechSynthesis) window.speechSynthesis.cancel();
}

function setSignPanelLang(lang) {
  _signPanelLang = lang;
  _renderSignPanel();
}

function _getProp(obj, lang) {
  if (!obj) return '';
  if (typeof obj === 'string') return obj;
  // Strict: return requested language only — no automatic cross-language fallback.
  // When content is missing for a language the caller sees '' and handles it explicitly.
  // This prevents Norwegian text from leaking into Thai/English views.
  return obj[lang] || '';
}

function _signCode(sign) {
  return String((sign && (sign.code || sign.variant || sign.id)) || '').match(/\d{3}(?:\.\d+)?/)?.[0] || '';
}

function _signOrder(sign) {
  var code = _signCode(sign);
  var n = parseFloat(code || sign.order || '9999');
  return isNaN(n) ? 9999 : n;
}

function _sameSignGroup(a, b) {
  if (!a || !b) return false;
  if (a._groupKey && b._groupKey) return a._groupKey === b._groupKey;
  return _getProp(a._groupName || a.group_name, 'no') === _getProp(b._groupName || b.group_name, 'no');
}

function _relatedSignsFor(sign, count) {
  return _allSigns
    .filter(function(item) { return item && item.id !== sign.id && _sameSignGroup(item, sign); })
    .sort(function(a, b) {
      return Math.abs(_signOrder(a) - _signOrder(sign)) - Math.abs(_signOrder(b) - _signOrder(sign));
    })
    .slice(0, count || 6);
}

function _renderRelatedSignCard(sign, lang) {
  var name = _getProp(sign.name, lang) || _getProp(sign.name, 'no') || '–';
  var code = sign.code || _signCode(sign);
  var clickId = JSON.stringify(sign.id || '').replace(/"/g, '&quot;');
  return '<button class="sp-related-card" type="button" onclick="openSignDetailById(' + clickId + ')">'
    + '<div class="sp-related-img">' + (sign.image_url ? '<img src="' + escH(sign.image_url) + '" alt="" loading="lazy">' : '') + '</div>'
    + '<div class="sp-related-code">' + escH(code || '') + '</div>'
    + '<div class="sp-related-name">' + escH(name) + '</div>'
    + '</button>';
}

function openSignDetailById(id) {
  var next = _allSigns.find(function(sign) { return sign.id === id; });
  if (next) openSignDetail(next);
}

function _renderSignPanel() {
  var sign = _signPanelData;
  if (!sign) return;
  var lang = _signPanelLang;

  // Image
  var imgEl = document.getElementById('spImg');
  if (imgEl) { imgEl.src = sign.image_url || ''; }

  // Name
  var nameEl = document.getElementById('spName');
  if (nameEl) nameEl.textContent = _getProp(sign.name, lang) || (lang !== 'no' ? _getProp(sign.name, 'en') : '') || _getProp(sign.name, 'no') || '–';

  // Group label
  var groupEl = document.getElementById('spGroupLabel');
  if (groupEl) groupEl.textContent = _getProp(sign._groupName || sign.group_name, lang) || '';

  // Lang tabs
  document.querySelectorAll('.sp-lang-tab').forEach(function(tab) {
    tab.classList.toggle('active', tab.dataset.lang === lang);
  });

  // Labels per language
  var L = {
    no: { expl:'Forklaring', danger:'Hvorfor viktig', mistake:'Vanlig feil',
          scenario:'I trafikken', examTip:'Eksamentips', memRule:'Huskeregel' },
    th: { expl:'คำอธิบาย', danger:'เหตุใดจึงสำคัญ', mistake:'ข้อผิดพลาดที่พบบ่อย',
          scenario:'ในสถานการณ์จริง', examTip:'เคล็ดลับสอบ', memRule:'วิธีจำ' },
    en: { expl:'Explanation', danger:'Why it matters', mistake:'Common mistake',
          scenario:'In traffic', examTip:'Exam tip', memRule:'Memory rule' }
  }[lang] || {};

  // Typed card builder — each section has its own colour identity and icon
  var _cardIdx = 0;
  function card(type, icon, label, text) {
    if (!text) return '';
    var delay = _cardIdx * 45;
    _cardIdx++;
    return '<div class="sp-card sp-card-' + type + '" style="animation:aiBlockIn .22s ease both;animation-delay:' + delay + 'ms">'
      + '<div class="sp-card-icon">' + icon + '</div>'
      + '<div class="sp-card-inner">'
        + '<div class="sp-card-label">' + escH(label) + '</div>'
        + '<div class="sp-card-text">' + escH(text) + '</div>'
      + '</div>'
      + '</div>';
  }

  var html = '';
  html += card('explanation', '📖', L.expl,     _getProp(sign.explanation,  lang));
  html += card('danger',      '⚠️', L.danger,   _getProp(sign.driverAction || sign.driver_action || sign.whyDangerous || sign.why_dangerous, lang));
  html += card('mistake',     '🔴', L.mistake,  _getProp(sign.typicalMistake || sign.typical_mistake, lang));
  html += card('scenario',    '🚗', L.scenario, _getProp(sign.realScenario || sign.real_scenario, lang));
  html += card('exam',        '📝', L.examTip,  _getProp(sign.examTip || sign.exam_tip, lang));
  html += card('memory',      '💡', L.memRule,  _getProp(sign.memoryRule || sign.memory_rule, lang));

  if (!html) {
    html += card('explanation', '📖', L.expl, t('sign_fallback_meaning'));
    html += card('danger',      '⚠️', L.danger, t('sign_fallback_driver'));
    html += card('mistake',     '🔴', L.mistake, t('sign_fallback_mistake'));
    html += card('exam',        '📝', L.examTip, t('sign_fallback_exam'));
    html += card('memory',      '💡', L.memRule, t('sign_fallback_memory'));
  }

  var related = _relatedSignsFor(sign, 6);
  var confused = related.slice(0, 4);
  var sideHtml = '<div class="sp-side-section">'
    + '<div class="sp-side-title">' + escH(t('often_confused')) + '</div>'
    + (confused.length
      ? '<div class="sp-related-grid">' + confused.map(function(s) { return _renderRelatedSignCard(s, lang); }).join('') + '</div>'
      : '<div class="sp-related-empty">' + escH(t('no_related_signs')) + '</div>')
    + '</div>'
    + '<div class="sp-side-section">'
    + '<div class="sp-side-title">' + escH(t('related_signs')) + '</div>'
    + (related.length
      ? '<div class="sp-related-grid">' + related.map(function(s) { return _renderRelatedSignCard(s, lang); }).join('') + '</div>'
      : '<div class="sp-related-empty">' + escH(t('no_related_signs')) + '</div>')
    + '</div>';

  var body = document.getElementById('spBody');
  if (body) body.innerHTML = '<div class="sp-learning-layout">'
    + '<div class="sp-related-surface">' + sideHtml + '</div>'
    + '<div class="sp-main-surface" id="spMainSurface">' + html + '</div>'
    + '</div>';

  // ── Contextual video suggestion for this sign (async) ─────────────────────
  // Uses sign.id for a direct match; passes sign group as fallback.
  var _spSignId  = sign.id || '';
  var _spGroup   = _getProp(sign._groupName || sign.group_name, 'no') || '';
  var mainSurface = document.getElementById('spMainSurface');
  if (_spSignId && mainSurface) {
    fetchVideoForSign(_spSignId, _spGroup).then(function(v) {
      _injectVideo(mainSurface, 'vidSlot_sign_' + _spSignId, v);
    });
  }

  // Bookmark button state
  var bmBtn = document.getElementById('spBmBtn');
  if (bmBtn) {
    var isFav = _signFavorites.indexOf(sign.id) >= 0;
    bmBtn.innerHTML = isFav ? '🔖<span>' + escH(t('saved')) + '</span>' : '🔖<span>' + escH(t('save')) + '</span>';
    bmBtn.className = 'sp-btn-sm sp-btn-sm-bm' + (isFav ? ' saved' : '');
  }

  var practiceBtn = document.querySelector('.sp-btn-primary');
  if (practiceBtn) practiceBtn.textContent = t('practice_this_sign');
  var audioLbl = document.querySelector('.sp-btn-sm-audio span');
  if (audioLbl) audioLbl.textContent = t('read_aloud');
  var aiLbl = document.querySelector('.sp-btn-sm-ai span');
  if (aiLbl) aiLbl.textContent = t('ask_ai');
}

function speakSign() {
  if (!window.speechSynthesis) return;
  var sign = _signPanelData;
  if (!sign) return;
  var lang = _signPanelLang;
  var text = _getProp(sign.name, lang);
  var expl = _getProp(sign.explanation, lang);
  if (expl) text += '. ' + expl;
  var u = new SpeechSynthesisUtterance(text.trim());
  u.lang = lang === 'th' ? 'th-TH' : lang === 'en' ? 'en-US' : 'nb-NO';
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(u);
}

function toggleSignFavorite() {
  var sign = _signPanelData;
  if (!sign || !sign.id) return;
  var idx = _signFavorites.indexOf(sign.id);
  if (idx >= 0) _signFavorites.splice(idx, 1);
  else _signFavorites.push(sign.id);
  try { localStorage.setItem('t2d_signFavs', JSON.stringify(_signFavorites)); } catch(e) {}
  _renderSignPanel();
}

function practiceThisSign() {
  closeSignDetail();
  showTab('cats');
}

function askAiAboutSign() {
  var sign = _signPanelData;
  if (!sign) return;
  var lang = _signPanelLang;
  var main = document.getElementById('spMainSurface') || document.getElementById('spBody');
  if (!main) return;
  var old = document.getElementById('spAiInline');
  if (old) old.remove();

  var name = _getProp(sign.name, lang) || _getProp(sign.name, 'no') || '';
  var expl = _getProp(sign.explanation, lang);
  var driver = _getProp(sign.driverAction || sign.driver_action || sign.whyDangerous || sign.why_dangerous, lang) || t('sign_fallback_driver');
  var mistake = _getProp(sign.typicalMistake || sign.typical_mistake, lang) || t('sign_fallback_mistake');
  var lesson = tf('sign_ai_lesson', { name: name || t('signs') });
  var text = [lesson, expl, driver, mistake].filter(Boolean).join(' ');

  var ai = document.createElement('div');
  ai.id = 'spAiInline';
  ai.className = 'sp-card sp-card-explanation';
  ai.innerHTML = '<div class="sp-card-icon">🤖</div>'
    + '<div class="sp-card-inner">'
    + '<div class="sp-card-label">' + escH(t('ai_teacher_hint')) + '</div>'
    + '<div class="sp-card-text">' + escH(text) + '</div>'
    + '</div>';
  main.appendChild(ai);
  ai.scrollIntoView({ behavior:'smooth', block:'nearest' });
}

</script>
</body>
</html>
"""


@webapp_router.get("/web", response_class=HTMLResponse)
async def web_app():
    html = WEBAPP_HTML.replace('__DEPLOY_VERSION__', DEPLOY_VERSION)
    return HTMLResponse(content=html)

@webapp_router.get("/web/version")
async def web_version():
    """Returns the current deploy version. Use this to confirm what build is live."""
    return {"version": DEPLOY_VERSION, "endpoint": "/api/web"}
