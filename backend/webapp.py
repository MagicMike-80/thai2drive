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
html { font-size: 22px; }
html, body {
  height:100%; overflow:hidden;
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
  width:100%; height:100vh;
  display:flex; flex-direction:column;
  overflow:hidden; position:relative; z-index:1;
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

/* BOTTOM NAV */
#bottomNav {
  height:var(--bottom-h); flex-shrink:0;
  background:rgba(11,18,38,.97);
  backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
  border-top:1px solid var(--border);
  display:none; align-items:stretch; z-index:50;
}
[data-theme="light"] #bottomNav { background:rgba(241,245,249,.98); }
.bn-tab {
  flex:1; display:flex; flex-direction:column;
  align-items:center; justify-content:center; gap:3px;
  border:none; background:transparent; color:var(--muted);
  cursor:pointer; font-size:.8rem; font-weight:700;
  transition:color .2s; padding:8px 4px; letter-spacing:.2px;
}
.bn-icon { font-size:26px; line-height:1; transition:transform .2s; }
.bn-tab.active { color:var(--orange); }
.bn-tab.active .bn-icon { transform:scale(1.18); }
.bn-tab:active .bn-icon { transform:scale(.9); }

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
  position:fixed; inset:0; z-index:0; pointer-events:none;
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
  background:rgba(10,14,30,.72);
}
/* Subtle vignette */
.flag-bg::after {
  content:''; position:absolute; inset:0;
  background:radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,.3) 100%);
}

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
  padding:16px 16px 12px;
  justify-content:space-between;
  overflow:hidden;
}
.home-top { text-align:center; }
.home-logo-row {
  display:flex; align-items:center; justify-content:center; gap:10px;
  margin-bottom:10px;
}
.home-logo-box {
  width:44px; height:44px; border-radius:13px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  display:flex; align-items:center; justify-content:center;
  font-size:22px; font-weight:900; color:#0F172A;
  box-shadow:0 4px 16px rgba(255,153,51,.35);
}
.home-title { font-size:1.5rem; font-weight:900; letter-spacing:-.5px; }
.home-title span { color:var(--orange); }

.streak-badge {
  display:inline-flex; align-items:center; gap:7px;
  background:rgba(255,153,51,.11); border:1.5px solid rgba(255,153,51,.28);
  border-radius:50px; padding:6px 16px; margin-bottom:12px;
}
.streak-fire { font-size:1.2rem; }
.streak-num { font-size:1.3rem; font-weight:900; color:var(--orange); }
.streak-lbl { font-size:.75rem; color:var(--muted); font-weight:600; }

.home-cta {
  width:100%; padding:15px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:900; font-size:1rem;
  border:none; border-radius:14px; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:10px;
  box-shadow:0 6px 24px rgba(255,153,51,.4);
  transition:transform .15s, box-shadow .15s;
  margin-bottom:10px;
}
.home-cta:hover { transform:translateY(-2px); box-shadow:0 8px 28px rgba(255,153,51,.5); }
.home-cta:active { transform:translateY(0); }

.home-sec-btns {
  display:grid; grid-template-columns:1fr 1fr;
  gap:9px; margin-bottom:12px;
}
.home-sec-btn {
  padding:11px 8px;
  background:var(--card); border:1px solid var(--border);
  border-radius:12px; color:var(--text); font-weight:700;
  font-size:.82rem; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:6px;
  transition:border-color .2s, background .2s;
}
.home-sec-btn:hover { border-color:var(--orange); background:var(--orange-glow); }

.home-stats {
  display:grid; grid-template-columns:repeat(3,1fr);
  gap:8px; margin-bottom:10px;
}
.home-stat {
  background:var(--card); border:1px solid var(--border);
  border-radius:12px; padding:12px 8px; text-align:center;
}
.home-stat-num { font-size:1.4rem; font-weight:900; color:var(--orange); line-height:1; }
.home-stat-lbl {
  font-size:.6rem; color:var(--muted); font-weight:700;
  margin-top:4px; letter-spacing:.4px; text-transform:uppercase;
}

.premium-banner {
  background:linear-gradient(135deg,rgba(255,153,51,.14),rgba(230,137,31,.07));
  border:1px solid rgba(255,153,51,.28); border-radius:12px;
  padding:11px 14px; display:flex; align-items:center; gap:10px;
}
.premium-banner .pb-icon { font-size:1.3rem; }
.premium-banner .pb-text h4 { font-size:.85rem; font-weight:800; color:var(--orange); }
.premium-banner .pb-text p { font-size:.72rem; color:var(--muted); margin-top:1px; }
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
  grid-template-columns:repeat(2,1fr);
  gap:10px;
}
@media (min-width:480px) { .cat-grid { grid-template-columns:repeat(3,1fr); } }
@media (min-width:700px) { .cat-grid { grid-template-columns:repeat(4,1fr); } }

.cat-card {
  background:rgba(0,0,0,.35); border:1.5px solid rgba(255,255,255,.18);
  backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
  border-radius:14px; padding:14px 12px;
  cursor:pointer; transition:border-color .2s, transform .15s, box-shadow .2s;
  display:flex; flex-direction:column; gap:6px;
}
.cat-card:hover {
  border-color:var(--orange); transform:translateY(-2px);
  box-shadow:0 8px 20px rgba(255,153,51,.12);
}
.cat-card:active { transform:translateY(0); }
.cat-icon { font-size:1.8rem; line-height:1; }
.cat-name { font-weight:800; font-size:1.1rem; line-height:1.3; }
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
#screenQuiz { padding:0; }

.quiz-top {
  padding:10px 16px 8px; flex-shrink:0;
  background:var(--bg2);
  border-bottom:1px solid var(--border);
  display:flex; align-items:center; gap:12px;
}
[data-theme="light"] .quiz-top { background:var(--bg2); }
.back-btn {
  padding:7px 12px; border-radius:9px;
  border:1.5px solid var(--border); background:transparent;
  color:var(--muted); font-size:.82rem; font-weight:600;
  cursor:pointer; transition:all .2s; flex-shrink:0;
}
.back-btn:hover { border-color:var(--orange); color:var(--text); }

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

/* Quiz body fills rest of quiz screen */
.quiz-body {
  flex:1; overflow:hidden;
  padding:12px 16px 12px;
}

/* 3-col grid on desktop */
.quiz-card {
  height:100%;
  display:grid;
  grid-template-columns:1fr 1fr auto;
  gap:16px; align-items:start;
}
@media (max-width:700px) {
  .quiz-card { grid-template-columns:1fr; overflow-y:auto; }
  .q-next-col { display:none !important; }
  .q-next-mobile { display:block !important; }
}

.q-left {
  display:flex; flex-direction:column; gap:10px;
  height:100%; overflow:hidden;
}
.q-img-wrap {
  width:100%; border-radius:12px; overflow:hidden;
  background:rgba(255,255,255,.04); border:1px solid var(--border);
  max-height:220px; display:flex; align-items:center; justify-content:center;
  flex-shrink:0;
}
.q-img { width:100%; height:100%; max-height:220px; object-fit:contain; display:block; }

.q-text {
  font-size:1.25rem; font-weight:700; line-height:1.6; flex-shrink:0;
}
.q-tts {
  display:flex; align-items:center; gap:7px; flex-wrap:wrap; flex-shrink:0;
}
.tts-play {
  width:34px; height:34px; border-radius:50%;
  border:1.5px solid var(--border); background:rgba(255,255,255,.05);
  color:var(--text); cursor:pointer; font-size:13px;
  display:flex; align-items:center; justify-content:center;
  transition:all .2s; flex-shrink:0;
}
.tts-play:hover, .tts-play.playing {
  border-color:var(--orange); color:var(--orange); background:rgba(255,153,51,.1);
}
.spd-btn {
  padding:3px 9px; border-radius:20px;
  border:1.5px solid var(--border); background:transparent;
  color:var(--muted); font-size:.68rem; font-weight:800; cursor:pointer;
  transition:all .2s;
}
.spd-btn.active { background:rgba(255,153,51,.15); border-color:var(--orange); color:var(--orange); }

.q-mid {
  display:flex; flex-direction:column; gap:8px;
  height:100%; overflow:hidden;
}
.q-answers {
  display:flex; flex-direction:column; gap:8px; flex-shrink:0;
}
.ans-btn {
  display:flex; align-items:center; gap:12px;
  padding:14px 16px;
  background:rgba(255,255,255,.05);
  border:2px solid var(--border); border-radius:16px;
  cursor:pointer; text-align:left; color:var(--text);
  font-size:.88rem; font-weight:600;
  transition:border-color .2s, background .2s, transform .12s, box-shadow .2s;
  width:100%;
  box-shadow:0 2px 8px rgba(0,0,0,.15);
}
.ans-btn:hover:not(:disabled) {
  border-color:var(--orange); background:rgba(255,153,51,.09);
  transform:translateX(3px); box-shadow:0 4px 14px rgba(255,153,51,.15);
}
.ans-btn:active:not(:disabled) { transform:scale(.98); }
.ans-btn:disabled { cursor:default; }
.ans-btn.correct { border-color:var(--green); background:rgba(16,185,129,.13); box-shadow:0 4px 14px rgba(16,185,129,.15); }
.ans-btn.wrong   { border-color:var(--red);   background:rgba(239,68,68,.11);  box-shadow:0 4px 14px rgba(239,68,68,.12); }
.ans-btn.reveal  { border-color:var(--green); background:rgba(16,185,129,.07); }
.ans-letter {
  width:34px; height:34px; border-radius:50%;
  background:rgba(255,153,51,.14); color:var(--orange);
  font-size:.78rem; font-weight:900;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0; transition:all .2s;
  border:1.5px solid rgba(255,153,51,.25);
}
.ans-btn.correct .ans-letter { background:var(--green); color:#fff; border-color:var(--green); }
.ans-btn.wrong   .ans-letter { background:var(--red);   color:#fff; border-color:var(--red); }
.ans-btn.reveal  .ans-letter { background:var(--green); color:#fff; border-color:var(--green); }
.ans-text { flex:1; line-height:1.5; font-size:.87rem; }

.q-feedback {
  padding:10px 12px; border-radius:10px;
  font-size:.83rem; font-weight:700;
  display:none; align-items:center; gap:7px; flex-shrink:0;
}
.q-feedback.ok  { background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.3); color:#6EE7B7; display:flex; }
.q-feedback.bad { background:rgba(239,68,68,.08);  border:1px solid rgba(239,68,68,.25);  color:#FCA5A5; display:flex; }
.q-explain {
  padding:10px 12px;
  background:rgba(255,153,51,.07); border:1px solid rgba(255,153,51,.15);
  border-radius:10px; font-size:.78rem; color:var(--muted);
  line-height:1.6; display:none; flex-shrink:0;
}
.q-explain.show { display:block; }

/* Mobile next button — hidden on desktop */
.q-next-mobile {
  width:100%; padding:13px;
  background:linear-gradient(135deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:900; font-size:.9rem;
  border:none; border-radius:12px; cursor:pointer;
  margin-top:8px; display:none;
  box-shadow:0 4px 14px rgba(255,153,51,.35);
  transition:transform .15s; flex-shrink:0;
}
.q-next-mobile:disabled { opacity:.35; cursor:not-allowed; }
.q-next-mobile:not(:disabled):hover { transform:translateY(-1px); }

/* Desktop right column */
.q-next-col {
  display:flex; flex-direction:column;
  align-items:center; justify-content:flex-start;
  gap:10px; padding-top:2px; height:100%;
}
.q-next-big {
  writing-mode:vertical-rl;
  padding:20px 13px;
  background:linear-gradient(180deg,#FF9933,#e6891f);
  color:#0F172A; font-weight:900; font-size:14px;
  border:none; border-radius:14px; cursor:pointer;
  min-height:130px; width:48px;
  display:flex; align-items:center; justify-content:center;
  transition:all .2s;
  box-shadow:0 4px 14px rgba(255,153,51,.3);
}
.q-next-big:disabled { opacity:.35; cursor:not-allowed; box-shadow:none; }
.q-next-big:not(:disabled):hover { transform:scale(1.05); box-shadow:0 6px 20px rgba(255,153,51,.45); }

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
   SIGNS SCREEN
══════════════════════════════════════════ */
#screenSigns { padding:0; }
.signs-header { padding:14px 16px 10px; flex-shrink:0; }
.signs-scroll {
  flex:1; overflow-x:auto; overflow-y:hidden;
  display:flex; gap:12px;
  padding:0 16px 16px;
  -webkit-overflow-scrolling:touch;
  align-items:flex-start;
}
.signs-scroll::-webkit-scrollbar { height:4px; }
.signs-scroll::-webkit-scrollbar-track { background:transparent; }
.signs-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.12); border-radius:2px; }
.sign-card {
  width:160px; flex-shrink:0;
  background:var(--card); border:1.5px solid var(--border);
  border-radius:14px; padding:12px 10px;
  display:flex; flex-direction:column; align-items:center; gap:8px;
  height:calc(100% - 16px);
}
.sign-img-wrap {
  width:120px; height:120px; flex-shrink:0;
  border-radius:10px; overflow:hidden;
  background:rgba(255,255,255,.06); border:1px solid var(--border);
  display:flex; align-items:center; justify-content:center;
}
.sign-img { width:100%; height:100%; object-fit:contain; display:block; }
.sign-ans {
  width:100%; padding:6px 8px; border-radius:8px;
  background:rgba(16,185,129,.1); border:1px solid rgba(16,185,129,.25);
  font-size:.65rem; color:#6EE7B7; font-weight:700;
  text-align:center; line-height:1.35;
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical;
  overflow:hidden; flex:1;
}

/* ══════════════════════════════════════════
   BOOKMARKS SCREEN
══════════════════════════════════════════ */
#screenBookmarks { padding:0; }
.bm-header { padding:14px 16px 10px; flex-shrink:0; }
.bm-scroll {
  flex:1; overflow-x:auto; overflow-y:hidden;
  display:flex; gap:14px;
  padding:0 16px 16px;
  -webkit-overflow-scrolling:touch;
  align-items:flex-start;
}
.bm-scroll::-webkit-scrollbar { height:4px; }
.bm-scroll::-webkit-scrollbar-track { background:transparent; }
.bm-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.12); border-radius:2px; }

.bm-card {
  width:290px; flex-shrink:0;
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
}
#screenSettings::-webkit-scrollbar { width:4px; }
#screenSettings::-webkit-scrollbar-track { background:transparent; }
#screenSettings::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:2px; }

.settings-inner {
  display:flex; flex-direction:column; gap:0; padding-bottom:24px;
}

/* Profile hero at top */
.settings-profile-hero {
  padding:28px 20px 20px;
  display:flex; flex-direction:column; align-items:center; gap:10px;
  background:linear-gradient(180deg, rgba(255,153,51,.08) 0%, transparent 100%);
  border-bottom:1px solid var(--border);
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
  background:var(--card); border:1px solid var(--border);
  border-radius:16px; overflow:hidden;
  box-shadow:0 2px 12px rgba(0,0,0,.08);
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
  flex:1; overflow-y:auto; overflow-x:hidden;
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
.study-header {
  padding:14px 16px 10px; flex-shrink:0;
  display:flex; align-items:center; gap:10px;
}
.study-scroll {
  flex:1; overflow-y:auto; overflow-x:hidden;
  padding:0 16px 20px;
  -webkit-overflow-scrolling:touch;
  display:flex; flex-direction:column; gap:10px;
}
.study-scroll::-webkit-scrollbar { width:4px; }
.study-scroll::-webkit-scrollbar-track { background:transparent; }
.study-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.1); border-radius:2px; }

.study-chapter {
  background:var(--card); border:1px solid var(--border);
  border-radius:16px; overflow:hidden;
  transition:border-color .2s;
}
.study-chapter-header {
  display:flex; align-items:center; gap:12px;
  padding:14px 16px; cursor:pointer;
  user-select:none;
}
.study-chapter-header:hover { background:rgba(255,255,255,.03); }
.study-ch-icon {
  width:40px; height:40px; border-radius:11px;
  display:flex; align-items:center; justify-content:center;
  font-size:1.25rem; flex-shrink:0;
  background:rgba(255,153,51,.13); border:1px solid rgba(255,153,51,.2);
}
.study-ch-title { flex:1; font-size:.92rem; font-weight:800; line-height:1.3; }
.study-ch-arrow {
  color:var(--muted); font-size:.85rem;
  transition:transform .25s;
}
.study-chapter.open .study-ch-arrow { transform:rotate(90deg); }
.study-chapter-body {
  display:none; padding:0 16px 16px;
  border-top:1px solid var(--border);
}
.study-chapter.open .study-chapter-body { display:block; }
.study-chapter-body p {
  font-size:.83rem; line-height:1.75; color:var(--text);
  margin-top:12px;
}
.study-chapter-body strong { color:var(--orange); font-weight:800; }
.study-chapter-body ul {
  margin:8px 0 0 0; padding-left:18px;
  font-size:.82rem; line-height:1.75; color:var(--text);
}
.study-chapter-body li { margin-bottom:4px; }
.study-tip {
  margin-top:12px; padding:10px 13px;
  background:rgba(255,153,51,.08); border:1px solid rgba(255,153,51,.2);
  border-radius:10px; font-size:.78rem; color:var(--muted); line-height:1.6;
}
.study-tip strong { color:var(--orange); }

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

<div class="flag-bg"></div>

<div id="app">

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
          <img src="/api/assets/developer-icon-512.png" style="width:44px;height:44px;border-radius:13px;object-fit:cover;">
          <div class="home-title">Thai<span>2</span>Drive</div>
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
          <div class="loading-wrap" style="grid-column:1/-1">
            <div class="spinner"></div>
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
      <div class="signs-scroll" id="signsScroll">
        <div class="loading-wrap">
          <div class="spinner"></div>
        </div>
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
      <div class="study-header">
        <button class="back-btn" onclick="showTab('home')">← Tilbake</button>
        <div class="screen-title">📖 Studiebok</div>
      </div>
      <div class="study-scroll">

        <div class="study-chapter" id="sch1">
          <div class="study-chapter-header" onclick="toggleChapter('sch1')">
            <div class="study-ch-icon">🚦</div>
            <div class="study-ch-title">Kapittel 1 — Trafikkregler</div>
            <span class="study-ch-arrow">›</span>
          </div>
          <div class="study-chapter-body">
            <p>I Norge gjelder <strong>høyrekjøring</strong> — du holder til høyre på veien og møter trafikk fra venstre side.</p>
            <p><strong>Vikeplikt:</strong> Som hovedregel har du vikeplikt for trafikk fra høyre, med mindre skilt eller oppmerking sier noe annet.</p>
            <ul>
              <li>Stopp alltid for rødt lys</li>
              <li>Gult lys = forbered deg på stopp</li>
              <li>Grønt lys = kjør, men pass på fotgjengere</li>
              <li>Blinkende gult = sakte, vær forsiktig</li>
            </ul>
            <div class="study-tip"><strong>Tips:</strong> I rundkjøring har trafikk inne i rundkjøringen forkjørsrett. Du må gi vikeplikt når du kjører inn.</div>
          </div>
        </div>

        <div class="study-chapter" id="sch2">
          <div class="study-chapter-header" onclick="toggleChapter('sch2')">
            <div class="study-ch-icon">⏱️</div>
            <div class="study-ch-title">Kapittel 2 — Fartsgrenser</div>
            <span class="study-ch-arrow">›</span>
          </div>
          <div class="study-chapter-body">
            <p>Norges standard fartsgrenser:</p>
            <ul>
              <li><strong>50 km/t</strong> — tettbygd strøk (by og bygd)</li>
              <li><strong>80 km/t</strong> — landevei utenfor tettbygd strøk</li>
              <li><strong>110 km/t</strong> — motorvei med midtdeler</li>
              <li><strong>30 km/t</strong> — skolevei, lekeplasser, boliggater</li>
            </ul>
            <p>Fartsgrensen kan senkes eller heves av skilt. Husk at fartsgrensen er en <strong>maksimumsgrense</strong> — du skal alltid kjøre etter forholdene.</p>
            <div class="study-tip"><strong>Tips:</strong> Ved dårlig vær, mørke eller glatt vei skal du redusere farten selv om du holder lovlig hastighet.</div>
          </div>
        </div>

        <div class="study-chapter" id="sch3">
          <div class="study-chapter-header" onclick="toggleChapter('sch3')">
            <div class="study-ch-icon">🪧</div>
            <div class="study-ch-title">Kapittel 3 — Trafikkskilt</div>
            <span class="study-ch-arrow">›</span>
          </div>
          <div class="study-chapter-body">
            <p>Norske trafikkskilt er delt i fire grupper:</p>
            <ul>
              <li><strong>Forbudsskilt</strong> — røde, runde. Forbyr noe (f.eks. parkering, innkjøring)</li>
              <li><strong>Påbudsskilt</strong> — blå, runde. Påbyr noe (f.eks. kjøreretning)</li>
              <li><strong>Opplysningsskilt</strong> — blå, firkantede. Gir informasjon</li>
              <li><strong>Advarselsskilt</strong> — gule/hvite, trekantede. Varsler om fare</li>
            </ul>
            <div class="study-tip"><strong>Tips:</strong> En rød trekant med utropstegn betyr generell advarsel om fare. Vær ekstra forsiktig.</div>
          </div>
        </div>

        <div class="study-chapter" id="sch4">
          <div class="study-chapter-header" onclick="toggleChapter('sch4')">
            <div class="study-ch-icon">🍺</div>
            <div class="study-ch-title">Kapittel 4 — Alkohol og rus</div>
            <span class="study-ch-arrow">›</span>
          </div>
          <div class="study-chapter-body">
            <p>Norge har <strong>strenge regler</strong> mot kjøring i ruspåvirket tilstand:</p>
            <ul>
              <li>Promillegrense: <strong>0,2 promille</strong></li>
              <li>Under 0,5 promille: bot og kjøreforbud</li>
              <li>Over 0,5 promille: bot + betinget fengsel</li>
              <li>Over 1,2 promille: ubetinget fengsel</li>
            </ul>
            <p>Politiet kan stoppe enhver bilist og ta alkotest uten grunn.</p>
            <div class="study-tip"><strong>Tips:</strong> Alkohol er ikke det eneste som gir promillestraff — narkotika og visse medisiner teller også.</div>
          </div>
        </div>

        <div class="study-chapter" id="sch5">
          <div class="study-chapter-header" onclick="toggleChapter('sch5')">
            <div class="study-ch-icon">🦺</div>
            <div class="study-ch-title">Kapittel 5 — Sikkerhet og verneutstyr</div>
            <span class="study-ch-arrow">›</span>
          </div>
          <div class="study-chapter-body">
            <p><strong>Setebelte</strong> er påbudt for alle i kjøretøyet, både foran og bak. Sjåfør er ansvarlig for at passasjerer under 15 år bruker setebelte eller godkjent sikringsutstyr.</p>
            <ul>
              <li>Barn under 4 år: godkjent barnestol</li>
              <li>Barn 4–135 cm: barnesete eller bilstol</li>
              <li>Mobiltelefon uten håndfri er forbudt under kjøring</li>
              <li>Refleks og varseltrekant i bilen er krav ved uhell</li>
            </ul>
            <div class="study-tip"><strong>Tips:</strong> Sett alltid på varselblink og sett ut varseltrekant 50–150 m bak bilen ved stopp på vei.</div>
          </div>
        </div>

        <div class="study-chapter" id="sch6">
          <div class="study-chapter-header" onclick="toggleChapter('sch6')">
            <div class="study-ch-icon">🅿️</div>
            <div class="study-ch-title">Kapittel 6 — Parkering</div>
            <span class="study-ch-arrow">›</span>
          </div>
          <div class="study-chapter-body">
            <p>Generelle parkeringsregler i Norge:</p>
            <ul>
              <li>Ikke parker nærmere enn <strong>5 m</strong> fra kryss eller avkjørsel</li>
              <li>Ikke parker foran inn- og utkjøring</li>
              <li>Ikke parker på gangvei, sykkelvei, eller fortau (med mindre tillatt)</li>
              <li>Stoppforbud-skilt = ingen stopp i det hele tatt</li>
              <li>Parkeringsforbud-skilt = kortstopp for av/påstigning er OK</li>
            </ul>
            <div class="study-tip"><strong>Tips:</strong> Gul stripe langs kantstein betyr parkeringsforbud. Hvit stripe betyr parkeringsregulering.</div>
          </div>
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
var token = localStorage.getItem('t2d_token');
var user = null;
var deviceId = null;
var questions = [];
var qIdx = 0;
var qScore = 0;
var qAnswered = false;
var quizStartedAt = null;
var ttsRate = 1;
var ttsPlaying = false;
var currentCat = null;
var soundOn = localStorage.getItem('t2d_sound') !== 'off';
var feedbackStyle = localStorage.getItem('t2d_feedback') || 'soft';
var appLang = localStorage.getItem('t2d_lang') || 'th';
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
  correct:     {th:'🎉 ถูกต้อง!',       no:'🎉 Riktig!',       en:'🎉 Correct!'},
  wrong:       {th:'❌ ผิด',            no:'❌ Feil svar',     en:'❌ Wrong'},
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
  // cats header
  var ch = document.getElementById('catCount');
  if(ch) ch.closest('.screen-title') && (ch.closest('.screen-title').childNodes[0].textContent = '📚 ' + t('cats') + ' ');
  // home buttons
  document.querySelectorAll('.home-cta').forEach(function(b){ b.innerHTML = '▶&nbsp;&nbsp;' + t('startquiz').replace('▶  ',''); });
  document.querySelectorAll('.home-sec-btn').forEach(function(b,i){
    b.textContent = i===0 ? t('exam') : t('daily');
  });
  // end screen buttons
  var er = document.querySelector('.end-btn-pri'); if(er) er.innerHTML = t('retry');
  var eh = document.querySelector('.end-btn-sec:nth-child(2)'); if(eh) eh.innerHTML = t('backhome');
  var ep = document.querySelector('.end-btn-sec:last-child'); if(ep) ep.innerHTML = t('pickcat');
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
      localStorage.removeItem('t2d_token');
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
}

function enterApp() {
  document.getElementById('topBar').style.display = 'flex';
  document.getElementById('bottomNav').style.display = 'flex';
  showTab('home');
}

function showTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.bn-tab').forEach(function(b) { b.classList.remove('active'); });
  var tabMap = { home:'bnHome', cats:'bnCats', history:'bnHistory', signs:'bnSigns', bookmarks:'bnBookmarks', settings:'bnSettings' };
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
  }
}

function toggleChapter(id) {
  var ch = document.getElementById(id);
  if (ch) ch.classList.toggle('open');
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
  if (!r.ok) throw new Error(data.detail || 'Noe gikk galt');
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
    localStorage.setItem('t2d_token', token);
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
    localStorage.setItem('t2d_token', token);
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
  localStorage.removeItem('t2d_token');
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
      + '<div class="q-img-wrap">'
        + '<img class="q-img" src="' + escH(imgUrl) + '" alt="" onerror="this.parentElement.style.display=\'none\'" loading="lazy">'
      + '</div>'
      + '<div class="q-text">' + escH(qText) + '</div>'
      + '<div class="q-tts">'
        + '<button class="tts-play" id="qTtsBtn" title="Les høyt" onclick="speakQ()">▶</button>'
        + spdHtml
      + '</div>'
    + '</div>'
    + '<div class="q-mid">'
      + '<div class="q-answers" id="qAnswers">' + ansHtml + '</div>'
      + '<div class="q-feedback" id="qFeedback"></div>'
      + '<div class="q-explain" id="qExplain"></div>'
      + '<button class="q-next-mobile" id="qNextMobile" disabled onclick="nextQ()">' + t('next') + '</button>'
    + '</div>'
    + '<div class="q-next-col">'
      + '<button class="q-next-big" id="qNextBig" disabled onclick="nextQ()">' + t('next') + '</button>'
      + '<button class="q-bookmark-btn' + (isBm ? ' bookmarked' : '') + '" id="qBmBtn" onclick="toggleBookmark(\'' + escH(qId) + '\')" title="Bokmerke">'
        + (isBm ? '🔖' : '🔖')
      + '</button>'
    + '</div>'
    + (freeBanner ? '<div style="grid-column:1/-1">' + freeBanner + '</div>' : '');
}

var currentCorrect = '';
var currentExpl = '';

function selectAns(btn, picked) {
  if (qAnswered) return;
  qAnswered = true;
  var correct = currentCorrect;
  var isOk = picked.toUpperCase() === correct.toUpperCase();
  if (isOk) qScore++;

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

  if (currentExpl) {
    var ex = document.getElementById('qExplain');
    ex.textContent = currentExpl;
    ex.classList.add('show');
  }
  document.getElementById('qScoreNum').textContent = qScore;

  var nb = document.getElementById('qNextBig');
  var nm = document.getElementById('qNextMobile');
  if (nb) nb.disabled = false;
  if (nm) nm.disabled = false;

  playSound(isOk ? 'correct' : 'wrong');
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  ttsPlaying = false;
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
  if (signsLoaded && scroll.children.length > 1) return;
  scroll.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    var lang = appLang === 'th' ? 'th' : (appLang === 'no' ? 'no' : 'en');
    var data = await api('GET', '/api/questions/random?count=80&has_image=true&category=Traffic+Signs&lang=' + lang);
    var qs = Array.isArray(data) ? data : (data.questions || []);
    if (!qs.length) {
      scroll.innerHTML = '<div class="empty-state"><div class="es-icon">🚦</div><p>' + t('signs_empty') + '</p></div>';
      return;
    }
    scroll.innerHTML = '';
    qs.forEach(function(q) {
      var imgUrl = q.image_url || q.image || '';
      var answer = '';
      if (q.correct_answer !== undefined && q.answers) {
        var idx = q.correct_answer;
        answer = Array.isArray(q.answers) ? (q.answers[idx] || '') : '';
      } else if (q.correct_answer_text) {
        answer = q.correct_answer_text;
      } else if (q.answer) {
        answer = q.answer;
      }
      if (!imgUrl) return;
      var card = document.createElement('div');
      card.className = 'sign-card';
      card.innerHTML =
        '<div class="sign-img-wrap">' +
          '<img class="sign-img" src="' + imgUrl + '" alt="" loading="lazy" onerror="this.parentElement.style.display=\'none\'">' +
        '</div>' +
        '<div class="sign-ans">' + (answer || '–') + '</div>';
      scroll.appendChild(card);
    });
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
  utt.onstart = function() { ttsPlaying = true;  updateTtsBtn(true);  };
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

// ════════════════════════════════════════════
//  SOUND
// ════════════════════════════════════════════
function playSound(type) {
  if (!soundOn) return;
  try {
    var ctx = new (window.AudioContext || window.webkitAudioContext)();
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

  var savedTheme = localStorage.getItem('t2d_theme') || 'dark';
  ['light','dark','system'].forEach(function(t) {
    var id = 'themeBtn' + t.charAt(0).toUpperCase() + t.slice(1);
    var btn = document.getElementById(id);
    if (btn) btn.classList.toggle('active', savedTheme === t);
  });
}

function setLang(lang) {
  appLang = lang;
  localStorage.setItem('t2d_lang', lang);
  ['TH','NO','EN'].forEach(function(l) {
    var btn = document.getElementById('lang' + l);
    if (btn) btn.classList.toggle('active', lang === l.toLowerCase());
    var topBtn = document.getElementById('topLang' + l);
    if (topBtn) topBtn.classList.toggle('active', lang === l.toLowerCase());
  });
  applyUILang();
  // Reset signs cache so it reloads in new language
  signsLoaded = false;
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
  localStorage.setItem('t2d_sound', soundOn ? 'on' : 'off');
}

function setFeedback(style, btn) {
  feedbackStyle = style;
  localStorage.setItem('t2d_feedback', style);
  btn.closest('.seg-ctrl').querySelectorAll('.seg-btn').forEach(function(b) { b.classList.remove('active'); });
  btn.classList.add('active');
}

function setTheme(theme, btn) {
  if (btn) {
    btn.closest('.seg-ctrl').querySelectorAll('.seg-btn').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
  }
  localStorage.setItem('t2d_theme', theme);
  applyTheme(theme);
}

function applyThemeFromStorage() { applyTheme(localStorage.getItem('t2d_theme') || 'dark'); }

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
  if (localStorage.getItem('t2d_theme') === 'system') applyTheme('system');
});
</script>
</body>
</html>"""


@webapp_router.get("/web", response_class=HTMLResponse)
async def web_app():
    return HTMLResponse(content=WEBAPP_HTML)
