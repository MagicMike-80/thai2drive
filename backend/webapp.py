from fastapi import APIRouter
from fastapi.responses import HTMLResponse

webapp_router = APIRouter()

WEBAPP_HTML = r"""<!DOCTYPE html>
<html lang="th" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
  background:linear-gradient(180deg,
    #A51931 0%,    #A51931 16.66%,
    #E8E8E8 16.66%, #E8E8E8 33.33%,
    #1A1464 33.33%, #1A1464 66.66%,
    #E8E8E8 66.66%, #E8E8E8 83.33%,
    #A51931 83.33%, #A51931 100%);
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
  background:rgba(0,0,0,.05); border:1.5px solid rgba(255,255,255,.25);
  backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px);
  border-radius:14px; padding:14px 12px;
  cursor:pointer; transition:border-color .2s, transform .15s, box-shadow .2s;
  display:flex; flex-direction:column; gap:6px;
  color:#F1F5F9;
}
[data-theme="light"] .cat-card {
  background:rgba(255,255,255,.82); border-color:rgba(0,0,0,.1); color:#0F172A;
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
  padding:16px 16px 24px;
}
.quiz-body::-webkit-scrollbar { width:3px; }
.quiz-body::-webkit-scrollbar-track { background:transparent; }
.quiz-body::-webkit-scrollbar-thumb { background:rgba(255,255,255,.10); border-radius:2px; }

/* Quiz card: straight vertical flex — no grid, no columns */
.quiz-card {
  display:flex; flex-direction:column; gap:14px;
  width:100%;
}

/* Left section: image → question text → TTS — full width, auto height */
.q-left {
  display:flex; flex-direction:column; gap:12px;
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
  color:var(--orange); cursor:pointer; font-size:14px;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0;
  animation: tts-idle 2.5s ease-in-out infinite;
}
@keyframes tts-idle {
  0%,100% { background:rgba(255,153,51,.08); box-shadow:0 0 0 0 rgba(255,153,51,.4); }
  50%      { background:rgba(255,153,51,.22); box-shadow:0 0 0 8px rgba(255,153,51,0); }
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

/* Next button — full width, always visible below answers */
.q-next-mobile {
  display:block !important;       /* always on, never hidden */
  width:100%; padding:14px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:900; font-size:.9rem;
  border:none; border-radius:12px; cursor:pointer;
  margin-top:6px;
  box-shadow:0 4px 14px rgba(255,153,51,.35);
  transition:transform .15s;
}
.q-next-mobile:disabled { opacity:.35; cursor:not-allowed; box-shadow:none; }
.q-next-mobile:not(:disabled):hover { transform:translateY(-1px); }

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

/* ─ Keyframes ─ */
@keyframes aiBlockIn {
  from { opacity:0; transform:translateY(14px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes aiVerdictPop {
  from { opacity:0; transform:translateY(8px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes aiMobileIn {
  from { opacity:0; transform:translateY(12px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes imgFlashOk {
  0%   { filter:brightness(1)   saturate(1); }
  35%  { filter:brightness(1.2) saturate(1.5); }
  100% { filter:brightness(1)   saturate(1); }
}
@keyframes imgFlashBad {
  0%   { filter:brightness(1)   saturate(1); }
  35%  { filter:brightness(.80) saturate(.5); }
  100% { filter:brightness(1)   saturate(1); }
}
@keyframes statusPulse {
  0%,100% { opacity:1; }
  50%      { opacity:.50; }
}

/* Staggered animation class — set --i:N on each block.
   100ms between each block feels like a teacher making deliberate points. */
.ai-block {
  animation: aiBlockIn .40s cubic-bezier(.25,.46,.45,.94) both;
  animation-delay: calc(var(--i,0) * 100ms + 40ms);
}

/* ─ Image box ─ */
.quiz-ai-imgbox {
  flex:0 0 auto; position:relative;
  overflow:hidden; background:#03060E;
  transition:box-shadow .45s ease;
}
.quiz-ai-imgbox.glow-ok  { box-shadow:0 0 0 2px rgba(16,185,129,.40), 0 4px 32px rgba(16,185,129,.18); }
.quiz-ai-imgbox.glow-bad { box-shadow:0 0 0 2px rgba(239,68,68,.44),  0 4px 32px rgba(239,68,68,.20); }

.quiz-ai-img {
  width:100%; display:block;
  aspect-ratio:16/9; object-fit:cover; max-height:310px;
}
.quiz-ai-img.flash-ok  { animation:imgFlashOk  .65s ease forwards; }
.quiz-ai-img.flash-bad { animation:imgFlashBad .65s ease forwards; }

/* Gradient fade bottom + colour tint overlay */
.quiz-ai-img-overlay {
  position:absolute; inset:0; pointer-events:none;
  background:linear-gradient(to bottom, transparent 30%, #080F1E 100%);
  transition:background .45s ease;
}
.quiz-ai-img-overlay.result-ok {
  background:
    radial-gradient(ellipse 90% 55% at 50% 0%, rgba(16,185,129,.20) 0%, transparent 68%),
    linear-gradient(to bottom, rgba(16,185,129,.08) 0%, transparent 38%, #080F1E 100%);
}
.quiz-ai-img-overlay.result-bad {
  background:
    radial-gradient(ellipse 90% 55% at 50% 0%, rgba(239,68,68,.26) 0%, transparent 68%),
    linear-gradient(to bottom, rgba(239,68,68,.12) 0%, transparent 38%, #080F1E 100%);
}

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
.quiz-ai-status.idle { animation:statusPulse 2.2s ease infinite; }
.quiz-ai-status.ok   { color:var(--green); background:rgba(16,185,129,.10); border-color:rgba(16,185,129,.30); }
.quiz-ai-status.bad  { color:#FCA5A5;      background:rgba(239,68,68,.08);  border-color:rgba(239,68,68,.24); }

/* Padded body — content zone */
.quiz-ai-body {
  padding:22px 24px 52px;
  display:flex; flex-direction:column; gap:16px;
}

/* Idle placeholder */
.quiz-ai-idle {
  display:flex; flex-direction:column; align-items:center;
  text-align:center; gap:14px; padding:48px 20px;
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
  transition:max-height .32s ease, opacity .25s ease, padding .25s ease;
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
  display:flex; flex-direction:column; gap:12px;
}
.quiz-ai-mobile:empty { display:none; }
.quiz-ai-mobile:not(:empty) {
  margin-top:4px; padding-top:16px;
  border-top:1px solid rgba(255,255,255,.07);
  animation:aiMobileIn .40s ease both;
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
   SIGNS SCREEN
══════════════════════════════════════════ */
#screenSigns { padding:0; }
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
.sign-card {
  background:var(--card); border:1.5px solid var(--border);
  border-radius:14px; padding:10px 8px;
  display:flex; flex-direction:column; align-items:center; gap:8px;
  cursor:pointer; transition:border-color .2s, transform .15s;
}
.sign-card:hover { border-color:var(--orange); transform:translateY(-2px); }
.sign-img-wrap {
  width:100%; aspect-ratio:1/1; flex-shrink:0;
  border-radius:8px; overflow:hidden;
  background:rgba(255,255,255,.06); border:1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
}
.sign-img { width:100%; height:100%; object-fit:contain; display:block; }
.sign-ans {
  width:100%; padding:6px 8px; border-radius:8px;
  background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.25);
  font-size:.62rem; color:#6EE7B7; font-weight:700;
  text-align:center; line-height:1.35;
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical;
  overflow:hidden;
}

/* ══════════════════════════════════════════
   BOOKMARKS SCREEN
══════════════════════════════════════════ */
#screenBookmarks { padding:0; }
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
  background:var(--card); border:1.5px solid var(--border);
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
  /* Solid background hides the flag behind this screen */
  background:var(--bg);
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
  background:rgba(0,0,0,.45); border:1px solid rgba(255,255,255,.12);
  backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
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
#screenHistory { padding:0; }
.hist-header { padding:14px 16px 10px; flex-shrink:0; }
.hist-scroll {
  flex:1; min-height:0;                   /* min-height:0 → lets flex child shrink and scroll */
  overflow-y:auto; overflow-x:hidden;
  padding:0 16px 16px;
  -webkit-overflow-scrolling:touch;
  display:flex; flex-direction:column; gap:10px;
}
.hist-scroll::-webkit-scrollbar { width:4px; }
.hist-scroll::-webkit-scrollbar-track { background:transparent; }
.hist-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:2px; }

.hist-card {
  background:var(--card); border:1px solid var(--border);
  border-radius:14px; padding:14px 16px;
  display:flex; align-items:center; gap:14px;
  flex-shrink:0;
}
.hist-score-ring {
  width:54px; height:54px; border-radius:50%;
  border:3px solid var(--border);
  display:flex; align-items:center; justify-content:center;
  font-size:.95rem; font-weight:900; flex-shrink:0;
}
.hist-score-ring.good  { border-color:var(--green);  color:var(--green);  background:rgba(16,185,129,.08); }
.hist-score-ring.ok    { border-color:var(--orange);  color:var(--orange); background:rgba(255,153,51,.08); }
.hist-score-ring.bad   { border-color:var(--red);     color:var(--red);    background:rgba(239,68,68,.08); }
.hist-info { flex:1; min-width:0; }
.hist-mode { font-size:.88rem; font-weight:800; line-height:1.2; }
.hist-cat  { font-size:.73rem; color:var(--muted); margin-top:2px; }
.hist-detail { font-size:.75rem; color:var(--muted); margin-top:4px; }
.hist-date { font-size:.7rem; color:var(--muted); flex-shrink:0; text-align:right; }

/* ══════════════════════════════════════════
   END SCREEN
══════════════════════════════════════════ */
#screenEnd {
  align-items:center; justify-content:center;
  padding:32px 20px;
}
.end-wrap { text-align:center; max-width:360px; width:100%; }
.end-emoji { font-size:4.5rem; margin-bottom:12px; display:block; }
.end-pct   { font-size:3.2rem; font-weight:900; color:var(--orange); line-height:1; }
.end-score-lbl { font-size:1rem; color:var(--muted); font-weight:600; margin:7px 0 5px; }
.end-msg   { color:var(--muted); font-size:.85rem; margin-bottom:28px; line-height:1.5; }
.end-btns  { display:flex; flex-direction:column; gap:9px; }
.end-btn-pri {
  padding:13px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:800; font-size:.92rem;
  border:none; border-radius:12px; cursor:pointer;
  box-shadow:0 4px 14px rgba(255,153,51,.35); transition:transform .15s;
}
.end-btn-pri:hover { transform:translateY(-1px); }
.end-btn-sec {
  padding:12px;
  background:var(--card); border:1.5px solid var(--border);
  color:var(--text); font-weight:700; font-size:.87rem;
  border-radius:12px; cursor:pointer; transition:border-color .2s;
}
.end-btn-sec:hover { border-color:var(--orange); }

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
#screenStudybook { padding:0; }
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
  background:rgba(0,0,0,.05); border:1px solid rgba(255,255,255,.12);
  backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px);
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
  display:grid; grid-template-columns:1fr 1fr; gap:8px;
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
          <button class="auth-tab active" onclick="switchTab('login')">Logg inn</button>
          <button class="auth-tab" onclick="switchTab('register')">Registrer</button>
        </div>

        <div class="auth-error" id="authError"></div>
        <div class="auth-success" id="authSuccess"></div>

        <!-- LOGIN -->
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

        <!-- REGISTER -->
        <div id="formRegister" style="display:none">
          <div class="form-group">
            <label>Navn</label>
            <input type="text" id="regName" placeholder="Ditt fulle navn">
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

        <!-- FORGOT -->
        <div id="formForgot" style="display:none">
          <div class="form-group">
            <label>E-post</label>
            <input type="email" id="forgotEmail" placeholder="din@epost.com">
          </div>
          <button class="auth-btn" onclick="doForgot()">Send tilbakestillingslenke</button>
          <div style="text-align:center;margin-top:12px">
            <a style="font-size:.78rem;color:var(--muted);cursor:pointer" onclick="switchTab('login')">← Tilbake</a>
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
        <button class="home-sec-btn" onclick="showTab('studybook')" style="grid-column:1/-1">📖 Studiebok — Norsk trafikk</button>
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
        <div class="screen-title">📚 Kategorier <span id="catCount"></span></div>
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
                <div class="quiz-ai-panel-name">AI Kjørelærer</div>
                <div class="quiz-ai-panel-sub">Interaktiv trafikkopplæring</div>
              </div>
            </div>
            <div class="quiz-ai-status" id="quizAiStatus">Venter på svar…</div>
          </div>
          <div class="quiz-ai-body" id="quizAiBody">
            <div class="quiz-ai-idle">
              <div class="quiz-ai-idle-icon">👆</div>
              <div class="quiz-ai-idle-text">Ta deg tid — hva tror du er riktig? Velg et svar, så forklarer jeg.</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ═══ BOOKMARKS SCREEN ═══ -->
    <div class="screen" id="screenBookmarks">
      <div class="bm-header">
        <div class="screen-title">🔖 Bokmerker <span id="bmCount"></span></div>
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
        <div class="screen-title">🚦 <span data-key="signs">Trafikkskilt</span></div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:60vh;gap:18px;text-align:center;padding:32px">
        <div style="font-size:64px">🚧</div>
        <div style="font-size:22px;font-weight:700;color:#f59e0b">กำลังปรับปรุง</div>
        <div style="font-size:18px;font-weight:600;color:var(--text,#e2e8f0)">Under bygging — kommer snart!</div>
        <div style="font-size:15px;color:var(--muted,#94a3b8)">Coming soon!</div>
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
        <div class="screen-title">📊 Historikk <span id="histCount"></span></div>
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
          <input id="sbSearchInput" type="text" placeholder="Søk eller § nummer..." oninput="sbSearch(this.value)" autocomplete="off" />
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
        <button class="sb-nav-btn" id="sbPrevBtn" onclick="sbGoTo(_sbCurrent - 1)">‹ Forrige</button>
        <div class="sb-nav-info" id="sbNavInfo">Laster...</div>
        <button class="sb-nav-btn" id="sbNextBtn" onclick="sbGoTo(_sbCurrent + 1)">Neste ›</button>
      </div>
    </div>

    <!-- ═══ STUDIEBOK ADMIN EDIT MODAL ═══ -->
    <div id="studiebokEditModal" style="display:none;position:fixed;inset:0;z-index:9000;background:rgba(0,0,0,.6);align-items:center;justify-content:center;">
      <div style="background:var(--card);border-radius:16px;padding:24px;width:min(92vw,520px);max-height:80vh;overflow-y:auto;display:flex;flex-direction:column;gap:12px;">
        <div style="font-weight:700;font-size:1.05rem;">✏️ Rediger kapittel</div>
        <label style="font-size:.85rem;color:var(--muted);">Tittel</label>
        <input id="sbEditTitle" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" />
        <label style="font-size:.85rem;color:var(--muted);">Innhold (HTML)</label>
        <textarea id="sbEditContent" rows="10" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.85rem;width:100%;box-sizing:border-box;resize:vertical;font-family:monospace;"></textarea>
        <label style="font-size:.85rem;color:var(--muted);">🖼️ Bilde URL</label>
        <input id="sbEditImageUrl" type="text" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" placeholder="https://..." />
        <label style="font-size:.85rem;color:var(--muted);">🎥 Video URL (fremtidig)</label>
        <input id="sbEditVideoUrl" type="text" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" placeholder="https://..." />
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:4px;">
          <button onclick="closeStudiebokModal()" style="padding:8px 18px;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--text);cursor:pointer;">Avbryt</button>
          <button onclick="saveStudiebokChapter()" style="padding:8px 18px;border-radius:8px;border:none;background:var(--orange);color:#0F172A;font-weight:600;cursor:pointer;">Lagre</button>
        </div>
      </div>
    </div>

    <!-- ═══ END SCREEN ═══ -->
    <div class="screen" id="screenEnd">
      <div class="end-wrap">
        <span class="end-emoji" id="endEmoji">🏆</span>
        <div class="end-pct" id="endPct">0%</div>
        <div class="end-score-lbl" id="endScoreLbl">0 av 0 riktige</div>
        <p class="end-msg" id="endMsg">Bra jobbet!</p>
        <div class="end-btns">
          <button class="end-btn-pri" onclick="retryQuiz()">🔄 &nbsp;Prøv igjen</button>
          <button class="end-btn-sec" onclick="showTab('home')">🏠 &nbsp;Tilbake til hjem</button>
          <button class="end-btn-sec" onclick="showTab('cats')">📚 &nbsp;Velg kategori</button>
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
          <div class="paywall-price-card selected" onclick="selectPlan('month',this)">
            <div class="ppc-period" data-key="pw_month">Månedlig</div>
            <div class="ppc-price">99 kr</div>
            <div class="ppc-per" data-key="pw_per_month">per måned</div>
          </div>
          <div class="paywall-price-card" onclick="selectPlan('year',this)" style="position:relative">
            <div class="ppc-badge" data-key="pw_save">Spar 50%</div>
            <div class="ppc-period" data-key="pw_year">Årlig</div>
            <div class="ppc-price">599 kr</div>
            <div class="ppc-per" data-key="pw_per_year">per år</div>
          </div>
        </div>
        <button class="paywall-buy-btn" onclick="buyPremium()">⭐ <span data-key="pw_buy">Kjøp Premium</span></button>
        <button class="paywall-skip" onclick="paywallSkip()" data-key="pw_skip">Fortsett gratis</button>
      </div>
    </div>

  </div><!-- /content -->

  <!-- BOTTOM NAV — 5 tabs -->
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
    <button class="bn-tab" id="bnSigns" onclick="showTab('signs')">
      <span class="bn-icon">🚦</span>Skilt
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
var ttsRate = 1;
var ttsVolume = parseFloat(_ls.get('t2d_vol') || '1');
var ttsPlaying = false;
var currentCat = null;
var soundOn = _ls.get('t2d_sound') !== 'off';
var feedbackStyle = _ls.get('t2d_feedback') || 'soft';
var appLang = _ls.get('t2d_lang') || 'th';
var activeTab = 'home';

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
  // Paywall
  pw_title:    {th:'ปลดล็อก Thai2Drive Premium', no:'Lås opp Thai2Drive Premium', en:'Unlock Thai2Drive Premium'},
  pw_sub:      {th:'คุณใช้ 5 คำถามฟรีแล้ว อัปเกรดเพื่อใช้งานไม่จำกัด!', no:'Du har brukt 5 gratis spørsmål. Oppgrader for ubegrenset tilgang!', en:'You have used 5 free questions. Upgrade for unlimited access!'},
  pw_f1:       {th:'คำถามและหมวดหมู่ไม่จำกัด', no:'Ubegrenset spørsmål og kategorier', en:'Unlimited questions and categories'},
  pw_f2:       {th:'โหมดสอบเต็มรูปแบบ (45 ข้อ)', no:'Fullstendig eksamensmode (45 spørsmål)', en:'Full exam mode (45 questions)'},
  pw_f3:       {th:'ทดสอบรายวันและโหมดฝึกซ้อม', no:'Daglig test og øvingsmodus', en:'Daily test and practice mode'},
  pw_f4:       {th:'ประวัติและสถิติความก้าวหน้า', no:'Historikk og fremgangsstatistikk', en:'History and progress statistics'},
  pw_f5:       {th:'แกลเลอรีป้ายจราจร', no:'Trafikkskilt-galleri', en:'Traffic signs gallery'},
  pw_month:    {th:'รายเดือน', no:'Månedlig', en:'Monthly'},
  pw_year:     {th:'รายปี', no:'Årlig', en:'Yearly'},
  pw_per_month:{th:'ต่อเดือน', no:'per måned', en:'per month'},
  pw_per_year: {th:'ต่อปี', no:'per år', en:'per year'},
  pw_save:     {th:'ประหยัด 50%', no:'Spar 50%', en:'Save 50%'},
  pw_buy:      {th:'ซื้อ Premium', no:'Kjøp Premium', en:'Buy Premium'},
  pw_skip:     {th:'ใช้ต่อแบบฟรี', no:'Fortsett gratis', en:'Continue free'},
};

function t(key) { return (UI[key] && (UI[key][appLang] || UI[key]['no'])) || key; }

function applyUILang() {
  // back buttons
  document.querySelectorAll('.back-btn').forEach(function(b){ b.textContent = t('back'); });
  // bottom nav
  var nb = document.getElementById('bnHome');      if(nb) nb.innerHTML = '<span class="bn-icon">🏠</span>' + t('home');
  var nc = document.getElementById('bnCats');      if(nc) nc.innerHTML = '<span class="bn-icon">📚</span>' + t('cats');
  var nh = document.getElementById('bnHistory');   if(nh) nh.innerHTML = '<span class="bn-icon">📊</span>' + t('history');
  var nsg= document.getElementById('bnSigns');     if(nsg) nsg.innerHTML = '<span class="bn-icon">🚦</span>' + t('signs');
  var nbm= document.getElementById('bnBookmarks'); if(nbm) nbm.innerHTML = '<span class="bn-icon">🔖</span>' + t('bookmarks');
  var ns = document.getElementById('bnSettings');  if(ns) ns.innerHTML = '<span class="bn-icon">⚙️</span>' + t('settings');
  // cats header — update title text without disturbing the count span
  var catsTitleEl = document.querySelector('#screenCats .screen-title');
  if (catsTitleEl) {
    var catsCountEl = document.getElementById('catCount');
    var catsCountText = catsCountEl ? catsCountEl.textContent : '';
    catsTitleEl.innerHTML = '📚 ' + t('cats') + ' <span id="catCount">' + catsCountText + '</span>';
  }
  // home buttons
  document.querySelectorAll('.home-cta').forEach(function(b){ b.innerHTML = t('startquiz').replace(/^▶\s*/,'▶&nbsp;&nbsp;'); });
  document.querySelectorAll('.home-sec-btn').forEach(function(b,i){
    if (i===0) b.textContent = t('exam');
    else if (i===1) b.textContent = t('daily');
    // i===2 is the Studiebok button — leave it as-is (static text)
  });
  // end screen buttons
  var er = document.querySelector('.end-btn-pri'); if(er) er.innerHTML = t('retry');
  var endSecBtns = document.querySelectorAll('.end-btn-sec');
  if (endSecBtns[0]) endSecBtns[0].innerHTML = t('backhome');
  if (endSecBtns[1]) endSecBtns[1].innerHTML = t('pickcat');
  // next buttons
  document.querySelectorAll('#qNextBig,#qNextMobile').forEach(function(b){ b.textContent = t('next'); });
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
  // Translate ALL elements with data-key — reliable fallback
  document.querySelectorAll('[data-key]').forEach(function(el) {
    var key = el.getAttribute('data-key');
    var val = t(key);
    if (val) el.textContent = val;
  });
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

// ════════════════════════════════════════════
//  INIT
// ════════════════════════════════════════════
(async function init() {
  applyThemeFromStorage();
  applyUILang();
  // Init top bar language buttons
  ['TH','NO','EN'].forEach(function(l) {
    var topBtn = document.getElementById('topLang' + l);
    if (topBtn) topBtn.classList.toggle('active', appLang === l.toLowerCase());
  });
  if (token) {
    try {
      user = await api('GET', '/api/auth/me');
      deviceId = user._id || user.id || null;
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
}

function enterApp() {
  document.getElementById('topBar').style.display = 'flex';
  document.getElementById('bottomNav').style.display = 'flex';
  showTab('home');
}

function showTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.bn-tab').forEach(function(b) { b.classList.remove('active'); });
  var tabMap = { home:'bnHome', cats:'bnCats', history:'bnHistory', signs:'bnSigns', studybook:'bnStudybook', bookmarks:'bnBookmarks', settings:'bnSettings' };
  if (tabMap[tab]) document.getElementById(tabMap[tab]).classList.add('active');
  var screenMap = {
    home:'screenHome', cats:'screenCats',
    history:'screenHistory', signs:'screenSigns', bookmarks:'screenBookmarks',
    settings:'screenSettings', studybook:'screenStudybook'
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
    reader.innerHTML = '<div style="padding:24px;text-align:center;color:var(--muted);">Kunne ikke laste studiebok.</div>';
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
    box.innerHTML = '<div class="sb-result-item" style="color:var(--muted)">Ingen treff</div>';
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
  if (!title_no || !content_no) { toast('Tittel og innhold kan ikke være tomme'); return; }
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
  var opts = { method: method, headers: { 'Content-Type': 'application/json' } };
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  var r = await fetch(url, opts);
  var data = await r.json().catch(function() { return {}; });
  if (!r.ok) {
    var det = data.detail;
    var msg = typeof det === 'string' ? det : (Array.isArray(det) ? det.map(function(d){return d.msg||d;}).join(', ') : JSON.stringify(det) || 'Noe gikk galt');
    throw new Error(msg);
  }
  return data;
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
  document.getElementById('formLogin').style.display   = tab === 'login'    ? 'block' : 'none';
  document.getElementById('formRegister').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('formForgot').style.display   = 'none';
}
function showForgot() {
  clearAuthMessages();
  document.getElementById('formLogin').style.display = 'none';
  document.getElementById('formForgot').style.display = 'block';
  document.querySelectorAll('.auth-tab').forEach(function(t) { t.classList.remove('active'); });
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
  if (!email || !pass) return showAuthError('Fyll inn e-post og passord');
  var btn = document.querySelector('#formLogin .auth-btn');
  btn.disabled = true; btn.textContent = 'Logger inn…';
  try {
    var r = await api('POST', '/api/auth/login', { email: email, password: pass });
    token = r.token; user = r.user;
    deviceId = user._id || user.id || null;
    _ls.set('t2d_token', token);
    enterApp();
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = 'Logg inn';
  }
}

async function doRegister() {
  clearAuthMessages();
  var name  = document.getElementById('regName').value.trim();
  var email = document.getElementById('regEmail').value.trim();
  var pass  = document.getElementById('regPass').value;
  if (!name || !email || !pass) return showAuthError('Fyll inn alle feltene');
  if (pass.length < 6) return showAuthError('Passord må være minst 6 tegn');
  var btn = document.querySelector('#formRegister .auth-btn');
  btn.disabled = true; btn.textContent = 'Oppretter konto…';
  try {
    var r = await api('POST', '/api/auth/signup', { name: name, email: email, password: pass });
    token = r.token; user = r.user;
    deviceId = user._id || user.id || null;
    _ls.set('t2d_token', token);
    enterApp();
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = 'Opprett konto';
  }
}

async function doForgot() {
  clearAuthMessages();
  var email = document.getElementById('forgotEmail').value.trim();
  if (!email) return showAuthError('Fyll inn e-postadressen din');
  var btn = document.querySelector('#formForgot .auth-btn');
  btn.disabled = true; btn.textContent = 'Sender…';
  try {
    await api('POST', '/api/auth/forgot-password', { email: email });
    showAuthSuccess('E-post sendt! Sjekk innboksen din 📧');
    setTimeout(function() { switchTab('login'); }, 2500);
  } catch(e) {
    showAuthError(e.message);
  }
  btn.disabled = false; btn.textContent = 'Send tilbakestillingslenke';
}

function logout() {
  if (!confirm('Er du sikker på at du vil logge ut?')) return;
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
      grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>Ingen kategorier funnet</p></div>';
      return;
    }
    grid.innerHTML = cats.map(function(c) {
      var icon  = CAT_ICONS[c.name] || '📖';
      var count = c.question_count || c.count || '';
      var id    = escH(String(c.id || c.name));
      var name  = catName(c.name);
      var qWord = {th:'คำถาม', no:'spørsmål', en:'questions'}[appLang] || 'spørsmål';
      return '<div class="cat-card" onclick="startQuiz(\'' + escH(String(c.id||c.name)) + '\',\'' + escH(c.name) + '\')">'
        + '<div class="cat-icon">' + icon + '</div>'
        + '<div class="cat-name">' + escH(name) + '</div>'
        + '<div class="cat-count">' + (count ? count + ' ' + qWord : '') + '</div>'
        + '<div class="cat-bar-wrap"><div class="cat-bar" style="width:0%"></div></div>'
        + '</div>';
    }).join('');
  } catch(e) {
    grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">⚠️</div><p>Kunne ikke laste kategorier.<br>Sjekk internettforbindelsen.</p></div>';
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
var selectedPlan = 'month';

function isPremium() {
  return user && user.is_premium === true;
}

function checkPaywall() {
  // Returns true if user can continue, false = paywall shown
  if (isPremium()) return true;
  if (qIdx >= FREE_LIMIT) {
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

function buyPremium() {
  var msg = {
    th:'ติดต่อเราที่ thai2drive@gmail.com เพื่อซื้อ Premium',
    no:'Kontakt oss på thai2drive@gmail.com for å kjøpe premium',
    en:'Contact us at thai2drive@gmail.com to buy premium'
  };
  toast((msg[appLang] || msg['no']), 5000);
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
      toast('Tid er ute! ⏰');
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
  var qCard = document.getElementById('qCard');
  qCard.innerHTML = '<div class="loading-wrap" style="grid-column:1/-1"><div class="spinner"></div><span style="color:var(--muted);font-size:.82rem">Laster spørsmål…</span></div>';
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
      qCard.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>Ingen spørsmål med bilde funnet.<br>Prøv en annen kategori.</p></div>';
      return;
    }
    qIdx = 0; qScore = 0; qAnswered = false;
    _wrongStreak = 0; _correctStreak = 0; _correctPhraseIdx = 0;
    _sessionAnswered = 0; _sessionWrongTotal = 0; _recentTopics = [];
    quizStartedAt = new Date().toISOString();
    stopExamTimer();
    if (isExamMode) startExamTimer();
    renderQuestion();
  } catch(e) {
    qCard.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">⚠️</div><p>Kunne ikke laste spørsmål.<br>' + escH(e.message) + '</p></div>';
  }
}

function pickLang(obj) {
  if (!obj) return '';
  if (typeof obj === 'string') return obj;
  return obj[appLang] || obj['no'] || obj['th'] || obj['en'] || Object.values(obj)[0] || '';
}

// Pick language-suffixed field from a question object (e.g. question_text_th, answer_a_no)
function pickField(q, base) {
  return q[base + '_' + appLang] || q[base + '_no'] || q[base + '_th'] || q[base + '_en'] || q[base] || '';
}

function renderQuestion() {
  if (qIdx >= questions.length) { showEnd(); return; }
  var q     = questions[qIdx];
  qAnswered = false;
  var displayTotal = isPremium() ? questions.length : Math.min(FREE_LIMIT, questions.length);
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

  // Free limit banner for non-premium
  var freeBanner = '';
  if (!isPremium() && qIdx < FREE_LIMIT) {
    var remaining = FREE_LIMIT - qIdx;
    var freeMsg = {th:'เหลือ ' + remaining + ' คำถามฟรี', no:remaining + ' gratis spørsmål igjen', en:remaining + ' free questions left'}[appLang] || remaining + ' gratis spørsmål igjen';
    freeBanner = '<div style="text-align:center;font-size:.72rem;color:var(--orange);font-weight:700;margin-top:6px;flex-shrink:0;">'
      + '⚡ ' + freeMsg + ' — <span style="text-decoration:underline;cursor:pointer" onclick="showPaywall()">Oppgrader</span>'
      + '</div>';
  }

  qCard.innerHTML =
    '<div class="q-left">'
      + '<div class="q-img-wrap" id="qImgWrap">'
        + '<img class="q-img" src="' + escH(imgUrl) + '" alt="" onerror="this.parentElement.style.display=\'none\'" loading="lazy">'
      + '</div>'
      + '<div class="q-text">' + escH(qText) + '</div>'
      + '<div style="flex-shrink:0;"><button class="tts-play" id="qTtsBtn" title="Les høyt" onclick="speakQ()">▶</button></div>'
    + '</div>'
    + '<div class="q-mid">'
      + '<div class="q-answers" id="qAnswers">' + ansHtml + '</div>'
      + '<div class="q-feedback" id="qFeedback"></div>'
      // Mobile AI section — empty until answered (:empty hides it), then expands in-flow
      + '<div class="quiz-ai-mobile" id="quizAiMobile"></div>'
      + '<button class="q-next-mobile" id="qNextMobile" disabled onclick="nextQ()">' + t('next') + '</button>'
    + '</div>'
    + '<div class="q-next-col">'
      + '<button class="q-next-big" id="qNextBig" disabled onclick="nextQ()">' + t('next') + '</button>'
      + '<button class="q-bookmark-btn' + (isBm ? ' bookmarked' : '') + '" id="qBmBtn" onclick="toggleBookmark(\'' + escH(qId) + '\')" title="Bokmerke">'
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
  if (aiStatus) { aiStatus.textContent = 'Venter på svar…'; aiStatus.className = 'quiz-ai-status idle'; }
  var aiImgBadge = document.getElementById('quizAiImgBadge');
  if (aiImgBadge) aiImgBadge.textContent = '📸 Trafikksituasjon';
  var aiBody = document.getElementById('quizAiBody');
  if (aiBody) {
    aiBody.innerHTML = '<div class="quiz-ai-idle">'
      + '<div class="quiz-ai-idle-icon">👆</div>'
      + '<div class="quiz-ai-idle-text">Ta deg tid — hva tror du er riktig? Velg et svar, så forklarer jeg.</div>'
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

// Calm acknowledgment pool — rotates to avoid repetition, never effusive
var _correctPhraseIdx = 0;
var _correctPhrases = [
  'Riktig.',
  'Det stemmer.',
  'Riktig observert.',
  'Korrekt — det er nettopp slik det fungerer.',
  'Det er riktig.',
  'Riktig vurdering.',
];
function _nextCorrectPhrase() {
  var p = _correctPhrases[_correctPhraseIdx % _correctPhrases.length];
  _correctPhraseIdx++;
  return p;
}

// Streak-adaptive wrong-answer support — calm, professional, never patronising
function _wrongSupportText(streak) {
  if (streak >= 5) return 'Ikke riktig. Les forklaringen nøye — forståelse tar tid.';
  if (streak >= 3) return 'Ikke riktig denne gangen. Gå gjennom forklaringen under.';
  return 'Ikke riktig. Se forklaringen under.';
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

function selectAns(btn, picked) {
  if (qAnswered) return;
  qAnswered = true;
  var correct = currentCorrect;
  var isOk = picked.toUpperCase() === correct.toUpperCase();
  if (isOk) qScore++;

  // Update streaks and session counters before building the AI panel
  if (isOk) { _correctStreak++; _wrongStreak = 0; }
  else       { _wrongStreak++;  _correctStreak = 0; }
  _sessionAnswered++;
  if (!isOk) _sessionWrongTotal++;

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

  // Update AI right panel
  updateAiPanel(isOk, currentExpl);
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

  if (/forbikjør|forbi\s|overtakings/i.test(t))
    alerts.push({icon:'🚗', type:'danger', label:'Forbikjøring',
      text:'Full sikt og god avstand er nødvendig. Vent alltid til det er klart trygt.'});

  if (/glatt|is\b|snø|vinter|slipperisk|vått\s|regn/i.test(t))
    alerts.push({icon:'❄️', type:'weather', label:'Kjøreforhold',
      text:'Bremselengden øker kraftig i dårlig vær — tilpass alltid fart og avstand til forholdene.'});

  if (/avstand|3 sek|følgeavstand|bremse\w*\s*lengde/i.test(t))
    alerts.push({icon:'📏', type:'rule', label:'3-sekunders-regelen',
      text:'Hold minst 3 sekunder bak bilen foran. Mer avstand ved regn, mørke eller høy fart.'});

  if (/uoversiktlig|begrenset sikt|kurve|kryss\w*\s*sikt|blind/i.test(t))
    alerts.push({icon:'👁️', type:'danger', label:'Sikt og fart',
      text:'Der du ikke ser langt nok, må farten ned. God sikt er grunnlaget for trygg kjøring.'});

  if (/vikeplikt|forkjørsrett/i.test(t))
    alerts.push({icon:'⚠️', type:'danger', label:'Vikeplikt',
      text:'Vikeplikt i kryss er et av de viktigste og hyppigst testede temaene i teoriprøven.'});

  if (/gangfelt|fotgjenger/i.test(t))
    alerts.push({icon:'🚶', type:'danger', label:'Myke trafikanter',
      text:'Fotgjengere og syklister er mest sårbare — gi alltid god plass og stans i tide.'});

  if (/fartsgrense|hastighets|km\/t|80\s*km|60\s*km|50\s*km|30\s*km/i.test(t))
    alerts.push({icon:'🧠', type:'exam', label:'Eksamensfavoritt',
      text:'Fartsregler og fartsgrenser er blant de vanligste spørsmålene på teoriprøven.'});

  if (/belysning|lys\b|fyrlys|mørk|langt\s*lys|nærlys/i.test(t))
    alerts.push({icon:'💡', type:'rule', label:'Lysbruk',
      text:'Riktig lys gjør deg synlig og beskyttet. Sjekk alltid at lyset er tilpasset forholdene.'});

  if (/reaksjon\w*\s*tid|reaksjonstid/i.test(t))
    alerts.push({icon:'⏱️', type:'rule', label:'Reaksjonstid',
      text:'Ved 80 km/t tilbakelegger du 22 m per sekund — bygg alltid inn nok sikkerhetsmargin.'});

  if (/rundkjøring|sving\s*inn|kjøring\s*inn\s*i\s*rund/i.test(t))
    alerts.push({icon:'🔄', type:'rule', label:'Rundkjøring',
      text:'Trafikk inne i rundkjøringen har forkjørsrett. Gi vikeplikt ved innkjøring — kjør rolig og forutsigbart.'});

  if (/nødbrems|abs\b|bremse\w*\s*avstand|bremsebane|bremse\w*\s*vei/i.test(t))
    alerts.push({icon:'🛑', type:'danger', label:'Bremsing',
      text:'ABS hindrer hjullås men forkorter ikke alltid bremseavstanden. Trykk jevnt og hardt — slipp ikke opp.'});

  if (/møtende|motgående|svingslys|tunnel\b/i.test(t))
    alerts.push({icon:'💡', type:'danger', label:'Møtende trafikk',
      text:'Blend ned i god tid for møtende trafikk. Hold til høyre og bruk nærlys i tunnel.'});

  if (/tretthet|trøtt\b|døs|søvn|kjøretretthet/i.test(t))
    alerts.push({icon:'😴', type:'danger', label:'Tretthet',
      text:'Tretthet er like farlig som alkohol. Planlegg pauser — stopp og sov heller enn å presse seg.'});

  if (/promille|alkohol|ruspåvirket|0[,.]2\s*promille/i.test(t))
    alerts.push({icon:'⚖️', type:'rule', label:'Grenseverdi',
      text:'0,2 promille er grensen i Norge. Selv små mengder alkohol svekker reaksjonstid og situasjonsforståelse.'});

  return alerts.slice(0, 2); // max 2 per answer — calm, not overwhelming
}

// ── Context-aware instructor tip ─────────────────────────────────────────────
// Priority: streak state → topic context → generic fallback.
// The AI instructor responds first to how the student is FEELING, then to the topic.
function buildInstructorTip(isOk, alerts) {
  // ─ Streak-aware coaching — professional, calm, no gamification ─
  if (!isOk && _wrongStreak >= 5)
    return 'Dette er et krevende tema. Les forklaringen grundig — forståelse bygges over tid.';
  if (!isOk && _wrongStreak >= 3)
    return 'Gå gjennom forklaringen nøye. Det lønner seg å lese den mer enn én gang.';
  if (isOk && _correctStreak >= 10)
    return 'Du er i god progresjon på dette temaet.';
  // correctStreak 1-9: fall through to topic-aware tip

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
        ? 'Du er godt forberedt på dette temaet — ett av de hyppigste på teoriprøven.'
        : 'Dette er et av de vanligste temaene på teoriprøven. Les det i studieboken.';

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
    // _recentTopics[0] is current; index > 0 means it appeared in a previous answer.
    if (!isOk && _recentTopics.length > 1 && _recentTopics.indexOf(alerts[0].label) > 0) {
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

  // 1 ── Verdict — calm and clear, never a scorecard
  var verdictText = isOk ? _nextCorrectPhrase() : _wrongSupportText(_wrongStreak);
  var html = '<div class="quiz-ai-verdict ' + (isOk ? 'ok' : 'bad') + '">'
    + '<span class="quiz-ai-verdict-icon">' + (isOk ? '✅' : '↩') + '</span>'
    + '<span>' + verdictText + '</span>'
    + '</div>';

  if (!isOk && expl) {
    // 2a ── Wrong: topic-targeted label + key insight (safety numbers bolded)
    html += '<div class="quiz-ai-danger ai-block" style="--i:' + (i++) + '">'
      + '<div class="quiz-ai-danger-icon">📌</div>'
      + '<div style="min-width:0">'
      + '<div class="quiz-ai-danger-label">' + escH(_dangerLabel(expl)) + '</div>'
      + '<div class="quiz-ai-danger-text">' + emphExpl(parts.short) + '</div>'
      + '</div></div>';

    // 2b ── Full detail if explanation has more depth
    if (parts.rest) {
      html += '<div class="quiz-ai-explain ai-block" style="--i:' + (i++) + '">'
        + '<div class="quiz-ai-card-label">📖 Mer detaljer</div>'
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
      + '<div class="quiz-ai-card-label">📖 Forklaring</div>'
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
          + 'this.textContent=c.classList.contains(\'open\')?\'Vis mindre\':\'Vis mer\''
          + '">' + (autoOpen ? 'Vis mindre' : 'Vis mer') + '</button>'
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
      + '<div class="ai-alert-label">' + escH(a.label) + '</div>'
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
      + '<div class="quiz-ai-tip-label">Kjørelærer</div>'
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
    status.textContent = isOk ? '✅ Riktig svar' : '↩ Se forklaring';
    status.className = 'quiz-ai-status ' + okBad;
  }

  // Image badge — show detected topic to link image ↔ explanation
  var badge = document.getElementById('quizAiImgBadge');
  if (badge) {
    var topicLabel = expl ? _dangerLabel(expl) : '';
    badge.textContent = (topicLabel && topicLabel !== 'Forstå situasjonen')
      ? '📍 ' + topicLabel : '📸 Trafikksituasjon';
  }

  // Inject content and scroll back to top
  var body = document.getElementById('quizAiBody');
  if (body) { body.innerHTML = html; body.scrollTop = 0; }

  // ── Mobile: inline section below answers ─────────────────────────────────
  var mobile = document.getElementById('quizAiMobile');
  if (mobile) mobile.innerHTML = html;

  // Mobile question image tint
  var imgWrap = document.getElementById('qImgWrap');
  if (imgWrap) {
    imgWrap.style.outline   = isOk ? '2.5px solid rgba(16,185,129,.55)' : '2.5px solid rgba(239,68,68,.50)';
    imgWrap.style.boxShadow = isOk ? '0 0 18px rgba(16,185,129,.22)'    : '0 0 18px rgba(239,68,68,.20)';
    imgWrap.style.transition = 'outline .3s ease, box-shadow .3s ease';
  }
}

function nextQ() {
  if (!qAnswered) return;
  qIdx++;
  if (qIdx >= questions.length) { showEnd(); return; }
  // Paywall check: non-premium users get FREE_LIMIT questions
  if (!isPremium() && qIdx >= FREE_LIMIT) { showPaywall(); return; }
  renderQuestion();
}

function goBack() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  ttsPlaying = false;
  stopExamTimer();
  isExamMode = false;
  showTab(activeTab && activeTab !== 'quiz' ? activeTab : 'home');
}

// ════════════════════════════════════════════
//  BOOKMARKS
// ════════════════════════════════════════════
async function toggleBookmark(qId) {
  if (!deviceId || !qId) { toast('Logg inn for å bruke bokmerker'); return; }
  var btn = document.getElementById('qBmBtn');
  if (bookmarkedIds[qId]) {
    try {
      await api('DELETE', '/api/bookmarks/' + encodeURIComponent(deviceId) + '/' + encodeURIComponent(qId));
      delete bookmarkedIds[qId];
      if (btn) { btn.classList.remove('bookmarked'); }
      toast('Bokmerke fjernet');
    } catch(e) { toast('Kunne ikke fjerne bokmerke'); }
  } else {
    try {
      await api('POST', '/api/bookmarks', { device_id: deviceId, question_id: qId });
      bookmarkedIds[qId] = true;
      if (btn) { btn.classList.add('bookmarked'); }
      toast('Bokmerke lagt til 🔖');
    } catch(e) { toast('Kunne ikke legge til bokmerke'); }
  }
}

async function loadBookmarks() {
  if (!deviceId) {
    document.getElementById('bmScroll').innerHTML = '<div class="empty-state"><div class="es-icon">🔒</div><p>Logg inn for å se bokmerker</p></div>';
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
      scroll.innerHTML = '<div class="empty-state"><div class="es-icon">🔖</div><p>Ingen bokmerker ennå.<br>Trykk 🔖 under et spørsmål for å lagre det.</p></div>';
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
    scroll.innerHTML = '<div class="empty-state"><div class="es-icon">⚠️</div><p>Kunne ikke laste bokmerker.<br>' + escH(e.message) + '</p></div>';
  }
}

// ════════════════════════════════════════════
//  SIGNS GALLERY
// ════════════════════════════════════════════
var signsLoaded = false;
async function loadSigns() {
  var scroll = document.getElementById('signsScroll');
  if (signsLoaded && scroll.children.length > 0) return;
  scroll.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    // Fetch all questions with images — try all categories
    var data = await api('GET', '/api/questions?limit=200&has_image=true');
    var qs = Array.isArray(data) ? data : (data.questions || data.items || []);
    // Filter only questions that have an image
    qs = qs.filter(function(q){ return !!(q.bildeUrl || q.image_url || q.image); });
    if (!qs.length) {
      scroll.innerHTML = '<div class="empty-state"><div class="es-icon">🚦</div><p>' + t('signs_empty') + '</p></div>';
      return;
    }
    // Update count in header
    var countEl = document.getElementById('signsCount');
    if (countEl) countEl.textContent = qs.length + ' skilt';
    // Build grid
    var grid = document.createElement('div');
    grid.className = 'signs-grid';
    qs.forEach(function(q) {
      var imgUrl = q.bildeUrl || q.image_url || q.image || '';
      // Get question text in current language
      var qText = '';
      if (appLang === 'th' && q.question_th) qText = q.question_th;
      else if (appLang === 'en' && q.question_en) qText = q.question_en;
      else qText = q.question || q.question_no || '';
      // Get correct answer text in current language
      var answer = '';
      if (q.options && q.correctOptionId) {
        var opt = q.options.find(function(o){ return o.id === q.correctOptionId; });
        if (opt) answer = (opt.text && (opt.text[appLang] || opt.text.no || opt.text.en)) || '';
      } else if (q.correct_answer !== undefined && q.answers) {
        var idx = q.correct_answer;
        answer = Array.isArray(q.answers) ? (q.answers[idx] || '') : '';
      } else if (q.correct_answer_text) {
        answer = q.correct_answer_text;
      }
      var card = document.createElement('div');
      card.className = 'sign-card';
      card.innerHTML =
        '<div class="sign-img-wrap">' +
          '<img class="sign-img" src="' + imgUrl + '" alt="" loading="lazy" onerror="this.parentElement.parentElement.style.display=\'none\'">' +
        '</div>' +
        '<div class="sign-ans">' + escH(answer || qText || '–') + '</div>';
      grid.appendChild(card);
    });
    scroll.innerHTML = '';
    scroll.appendChild(grid);
    signsLoaded = true;
  } catch(e) {
    scroll.innerHTML = '<div class="empty-state"><div class="es-icon">⚠️</div><p>' + (e.message || 'Feil') + '</p></div>';
  }
}

// ════════════════════════════════════════════
//  HISTORY
// ════════════════════════════════════════════
async function loadHistory() {
  if (!deviceId) {
    document.getElementById('histScroll').innerHTML = '<div class="empty-state"><div class="es-icon">🔒</div><p>Logg inn for å se historikk</p></div>';
    return;
  }
  var scroll = document.getElementById('histScroll');
  scroll.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    var data = await api('GET', '/api/quiz-attempts/' + encodeURIComponent(deviceId) + '?limit=50');
    var attempts = Array.isArray(data) ? data : (data.attempts || data.results || []);
    document.getElementById('histCount').textContent = '(' + attempts.length + ')';
    if (!attempts.length) {
      scroll.innerHTML = '<div class="empty-state"><div class="es-icon">📊</div><p>Ingen quiz-historikk ennå.<br>Fullfør en quiz for å se resultatene her.</p></div>';
      return;
    }
    scroll.innerHTML = attempts.map(function(a) {
      var pct = Math.round(a.score_percentage || 0);
      var ringCls = pct >= 85 ? 'good' : pct >= 60 ? 'ok' : 'bad';
      var modeLabel = {exam:'Eksamen', category:'Kategori', daily:'Daglig test', random:'Tilfeldig quiz'}[a.mode] || a.mode || 'Quiz';
      var catLabel = a.category ? (' — ' + catName(a.category)) : '';
      var detail = (a.correct_answers || 0) + ' av ' + (a.total_questions || 0) + ' riktige';
      var passed = a.passed != null ? (a.passed ? ' ✓ Bestått' : ' ✗ Ikke bestått') : '';
      var dateStr = '';
      if (a.started_at || a.created_at) {
        var d = new Date(a.started_at || a.created_at);
        dateStr = d.toLocaleDateString('no-NO', {day:'2-digit', month:'2-digit'}) + '<br>' + d.toLocaleTimeString('no-NO', {hour:'2-digit', minute:'2-digit'});
      }
      return '<div class="hist-card">'
        + '<div class="hist-score-ring ' + ringCls + '">' + pct + '%</div>'
        + '<div class="hist-info">'
          + '<div class="hist-mode">' + escH(modeLabel) + escH(catLabel) + '</div>'
          + '<div class="hist-detail">' + escH(detail) + escH(passed) + '</div>'
        + '</div>'
        + '<div class="hist-date">' + dateStr + '</div>'
        + '</div>';
    }).join('');
  } catch(e) {
    scroll.innerHTML = '<div class="empty-state"><div class="es-icon">⚠️</div><p>Kunne ikke laste historikk.<br>' + escH(e.message) + '</p></div>';
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
      document.getElementById('bmScroll').innerHTML = '<div class="empty-state"><div class="es-icon">🔖</div><p>Ingen bokmerker ennå.<br>Trykk 🔖 under et spørsmål for å lagre det.</p></div>';
    }
    toast('Bokmerke fjernet');
  } catch(e) { toast('Kunne ikke fjerne bokmerke'); }
}

// ════════════════════════════════════════════
//  END SCREEN
// ════════════════════════════════════════════
function showEnd() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  stopExamTimer();
  showScreen('screenEnd');
  var total = questions.length;
  var pct   = total > 0 ? Math.round(qScore / total * 100) : 0;
  document.getElementById('endPct').textContent      = pct + '%';
  document.getElementById('endScoreLbl').textContent = qScore + ' av ' + total + ' riktige';
  var emoji = pct >= 85 ? '🏆' : pct >= 65 ? '👍' : pct >= 40 ? '💪' : '📚';
  var msg   = pct >= 85 ? 'Fantastisk! Du er klar for teoriprøven!'
            : pct >= 65 ? 'Bra jobbet! Fortsett å øve!'
            : pct >= 40 ? 'Ikke gi opp! Du blir bedre for hver gang.'
            : 'Øv mer og prøv igjen. Du klarer det!';
  document.getElementById('endEmoji').textContent = emoji;
  document.getElementById('endMsg').textContent   = msg;

  // Lagre quiz-forsøk til databasen for statistikk
  if (deviceId && total > 0) {
    var mode = isExamMode ? 'exam' : (currentCat ? 'category' : 'daily');
    var attemptData = {
      device_id: deviceId,
      mode: mode,
      category: currentCat ? currentCat.name : null,
      total_questions: total,
      correct_answers: qScore,
      score_percentage: pct,
      passed: isExamMode ? pct >= 85 : null,
      questions_answered: questions.map(function(q, i) {
        return { question_id: String(q._id || q.id || ''), index: i };
      }),
      started_at: quizStartedAt || new Date().toISOString()
    };
    api('POST', '/api/quiz-attempts', attemptData).catch(function() {});
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
  toast('Språk oppdatert');
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
    if (lf.style.display !== 'none') doLogin();
    else if (rf.style.display !== 'none') doRegister();
    else if (ff.style.display !== 'none') doForgot();
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
</script>
</body>
</html>"""


@webapp_router.get("/web", response_class=HTMLResponse)
async def web_app():
    return HTMLResponse(content=WEBAPP_HTML)
