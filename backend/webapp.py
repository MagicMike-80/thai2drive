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
  cursor:pointer; font-size:.65rem; font-weight:700;
  transition:color .2s; padding:8px 4px; letter-spacing:.2px;
}
.bn-icon { font-size:20px; line-height:1; transition:transform .2s; }
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
  background:var(--bg);
}
.flag-bg::before {
  content:''; position:absolute; inset:0;
  background:linear-gradient(180deg,
    rgba(165,25,49,.18) 0%, rgba(165,25,49,.18) 14.28%,
    rgba(255,255,255,.05) 14.28%, rgba(255,255,255,.05) 28.57%,
    rgba(36,29,79,.28) 28.57%, rgba(36,29,79,.28) 71.42%,
    rgba(255,255,255,.05) 71.42%, rgba(255,255,255,.05) 85.71%,
    rgba(165,25,49,.18) 85.71%, rgba(165,25,49,.18) 100%);
}
.flag-bg::after {
  content:''; position:absolute; inset:0;
  background:radial-gradient(ellipse at 50% 20%, rgba(255,153,51,.07) 0%, transparent 60%);
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
#screenCats { padding:0; }
.cats-header {
  padding:14px 16px 10px; flex-shrink:0;
}
.screen-title {
  font-size:1.3rem; font-weight:900; letter-spacing:-.3px;
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
  background:var(--card); border:1.5px solid var(--border);
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
.cat-name { font-weight:800; font-size:.85rem; line-height:1.3; }
.cat-count { font-size:.72rem; color:var(--muted); font-weight:500; }
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
  font-size:.92rem; font-weight:700; line-height:1.55; flex-shrink:0;
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
  display:flex; align-items:center; gap:10px;
  padding:11px 12px;
  background:rgba(255,255,255,.04);
  border:1.5px solid var(--border); border-radius:12px;
  cursor:pointer; text-align:left; color:var(--text);
  font-size:.83rem; transition:border-color .2s, background .2s, transform .1s;
  width:100%;
}
.ans-btn:hover:not(:disabled) {
  border-color:var(--orange); background:rgba(255,153,51,.07); transform:translateX(2px);
}
.ans-btn:disabled { cursor:default; }
.ans-btn.correct { border-color:var(--green); background:rgba(16,185,129,.12); }
.ans-btn.wrong   { border-color:var(--red);   background:rgba(239,68,68,.10); }
.ans-btn.reveal  { border-color:var(--green); background:rgba(16,185,129,.06); }
.ans-letter {
  width:30px; height:30px; border-radius:50%;
  background:rgba(255,153,51,.12); color:var(--orange);
  font-size:.74rem; font-weight:800;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0; transition:all .2s;
}
.ans-btn.correct .ans-letter { background:var(--green); color:#fff; }
.ans-btn.wrong   .ans-letter { background:var(--red);   color:#fff; }
.ans-btn.reveal  .ans-letter { background:var(--green); color:#fff; }
.ans-text { flex:1; line-height:1.4; }

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
   SETTINGS SCREEN — compact, no scroll
══════════════════════════════════════════ */
#screenSettings {
  padding:12px 16px;
  overflow:hidden; gap:0;
}
.settings-inner {
  display:flex; flex-direction:column; gap:10px; height:100%;
}
.settings-section { flex-shrink:0; }
.settings-label {
  font-size:.66rem; font-weight:800; color:var(--muted);
  letter-spacing:.8px; text-transform:uppercase;
  margin-bottom:6px; padding:0 3px;
}
.settings-card {
  background:var(--card); border:1px solid var(--border);
  border-radius:13px; overflow:hidden;
}
.settings-row {
  display:flex; align-items:center; gap:12px;
  padding:12px 14px;
  border-bottom:1px solid var(--border);
}
.settings-row:last-child { border-bottom:none; }
.sr-icon { font-size:1.1rem; width:26px; text-align:center; flex-shrink:0; }
.sr-label { flex:1; min-width:0; }
.sr-label .sr-title { font-size:.87rem; font-weight:700; }
.sr-label .sr-sub  { font-size:.72rem; color:var(--muted); margin-top:1px; }

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
  width:100%; padding:13px;
  background:rgba(239,68,68,.1); border:1.5px solid rgba(239,68,68,.22);
  color:#EF4444; font-weight:800; font-size:.9rem;
  border-radius:12px; cursor:pointer;
  transition:all .2s; flex-shrink:0;
}
.logout-btn:hover { background:rgba(239,68,68,.18); border-color:rgba(239,68,68,.4); }

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
</style>
</head>
<body>

<div class="flag-bg"></div>

<div id="app">

  <!-- TOP BAR -->
  <div id="topBar">
    <div class="top-logo">
      <div class="logo-icon">T</div>
      <span>Thai<span class="logo-t">2</span>Drive</span>
    </div>
    <div class="top-spacer"></div>
    <div id="topStreak">🔥 <span id="topStreakNum">0</span> dag streak</div>
  </div>

  <!-- CONTENT -->
  <div id="content">

    <!-- ═══ AUTH SCREEN ═══ -->
    <div class="screen active" id="screenAuth">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-big-icon">🚗</div>
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
          <div class="home-logo-box">T</div>
          <div class="home-title">Thai<span>2</span>Drive</div>
        </div>

        <div class="streak-badge">
          <span class="streak-fire">🔥</span>
          <span class="streak-num" id="homeStreakNum">0</span>
          <span class="streak-lbl">dag streak</span>
        </div>
      </div>

      <button class="home-cta" onclick="startRandomQuiz()">
        ▶&nbsp;&nbsp;Start quiz
      </button>

      <div class="home-sec-btns">
        <button class="home-sec-btn" onclick="startRandomQuiz()">📋 Eksamen</button>
        <button class="home-sec-btn" onclick="startRandomQuiz()">📅 Daglig test</button>
      </div>

      <div class="home-stats">
        <div class="home-stat">
          <div class="home-stat-num" id="homeStatAnswered">–</div>
          <div class="home-stat-lbl">Besvart</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-num" id="homeStatCorrect">–</div>
          <div class="home-stat-lbl">Riktige</div>
        </div>
        <div class="home-stat">
          <div class="home-stat-num" id="homeStatAcc">–</div>
          <div class="home-stat-lbl">Nøyaktighet</div>
        </div>
      </div>

      <div class="premium-banner" id="homePremiumBanner" style="display:none">
        <span class="pb-icon">💎</span>
        <div class="pb-text">
          <h4>Premium aktiv</h4>
          <p>Du har tilgang til alle funksjoner</p>
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

    <!-- ═══ SETTINGS SCREEN ═══ -->
    <div class="screen" id="screenSettings">
      <div class="settings-inner">

        <!-- Konto -->
        <div class="settings-section">
          <div class="settings-label">Konto</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon">👤</div>
              <div class="sr-label">
                <div class="account-info">
                  <div class="account-email" id="settEmail">–</div>
                  <div class="account-badges" id="settBadges"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Språk -->
        <div class="settings-section">
          <div class="settings-label">Språk</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon">🌐</div>
              <div class="sr-label">
                <div class="sr-title">Spørsmålsspråk</div>
                <div class="sr-sub">Velg språk for spørsmål og svar</div>
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
          <div class="settings-label">Lyd</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon">🔊</div>
              <div class="sr-label">
                <div class="sr-title">Lydeffekter</div>
                <div class="sr-sub">Pling ved riktig, buzz ved feil</div>
              </div>
              <label class="toggle">
                <input type="checkbox" id="soundToggle" checked onchange="toggleSound(this)">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="settings-row">
              <div class="sr-icon">📳</div>
              <div class="sr-label"><div class="sr-title">Stil</div></div>
              <div class="seg-ctrl">
                <button class="seg-btn active" onclick="setFeedback('soft',this)">Myk</button>
                <button class="seg-btn" onclick="setFeedback('strong',this)">Sterk</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tema -->
        <div class="settings-section">
          <div class="settings-label">Utseende</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon">🎨</div>
              <div class="sr-label"><div class="sr-title">Tema</div></div>
              <div class="seg-ctrl">
                <button class="seg-btn" id="themeBtnLight" onclick="setTheme('light',this)">Lys</button>
                <button class="seg-btn active" id="themeBtnDark" onclick="setTheme('dark',this)">Mørk</button>
                <button class="seg-btn" id="themeBtnSystem" onclick="setTheme('system',this)">Auto</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Om appen -->
        <div class="settings-section">
          <div class="settings-label">Om appen</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon">📱</div>
              <div class="sr-label">
                <div class="sr-title">Thai2Drive Web</div>
                <div class="sr-sub">Teoriprøven på thai for Norge</div>
              </div>
              <div style="color:var(--muted);font-size:.78rem;font-weight:600">v2.0</div>
            </div>
          </div>
        </div>

        <div style="flex:1"></div>
        <button class="logout-btn" onclick="logout()">🚪 &nbsp;Logg ut</button>

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

  </div><!-- /content -->

  <!-- BOTTOM NAV — 4 tabs -->
  <div id="bottomNav">
    <button class="bn-tab active" id="bnHome" onclick="showTab('home')">
      <span class="bn-icon">🏠</span>Hjem
    </button>
    <button class="bn-tab" id="bnCats" onclick="showTab('cats')">
      <span class="bn-icon">📚</span>Kategorier
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
var ttsRate = 1;
var ttsPlaying = false;
var currentCat = null;
var soundOn = localStorage.getItem('t2d_sound') !== 'off';
var feedbackStyle = localStorage.getItem('t2d_feedback') || 'soft';
var appLang = localStorage.getItem('t2d_lang') || 'th';
var activeTab = 'home';
var catsLoaded = false;
var bookmarkedIds = {};

var CAT_ICONS = {
  'Trafikkregler':'🚦','Skilt':'🪧','Vikeplikt':'⚠️','Kjøretøy':'🚗',
  'Farlig gods':'☣️','Miljø':'🌿','Ulykker':'🚨','Alkohol':'🍺',
  'Bremser':'🛑','Parkering':'🅿️','Lys':'💡','Dekk':'🔄',
  'Motorvei':'🛣️','Kryss':'✛','Gangfelt':'🚶','Sving':'↩️',
  'Forbikjøring':'🏎️','Lastsikring':'📦','Sikkerhet':'🦺','Fellesskjøring':'🤝',
  'Road Rules':'🚦','Traffic Rules':'🚦','Traffic Signs':'🪧',
  'Right of Way':'⚠️','Driving Conditions':'🌧️','Road Conditions':'🛣️',
  'Speed Limits':'⏱️','Safety':'🦺','Situations':'🔄','Parking':'🅿️',
  'Lights':'💡','Tires':'🔄','Overtaking':'🏎️','Intersections':'✛',
  'Pedestrians':'🚶','Alcohol':'🍺','Environment':'🌿','Vehicle':'🚗',
  'Accidents':'🚨','Highway':'🛣️'
};

// Norsk oversettelse av engelske kategorinavn
var CAT_NO = {
  'Road Rules':'Trafikkregler',
  'Traffic Rules':'Trafikkregler',
  'Traffic Signs':'Trafikkskilt',
  'Right of Way':'Vikeplikt',
  'Driving Conditions':'Kjøreforhold',
  'Road Conditions':'Veiforhold',
  'Speed Limits':'Fartsgrenser',
  'Safety':'Sikkerhet',
  'Situations':'Situasjoner',
  'Parking':'Parkering',
  'Lights':'Lys',
  'Tires':'Dekk',
  'Overtaking':'Forbikjøring',
  'Intersections':'Kryss',
  'Pedestrians':'Gangfelt',
  'Alcohol':'Alkohol',
  'Environment':'Miljø',
  'Vehicle':'Kjøretøy',
  'Accidents':'Ulykker',
  'Highway':'Motorvei'
};

// ════════════════════════════════════════════
//  INIT
// ════════════════════════════════════════════
(async function init() {
  applyThemeFromStorage();
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
  var tabMap = { home:'bnHome', cats:'bnCats', bookmarks:'bnBookmarks', settings:'bnSettings' };
  if (tabMap[tab]) document.getElementById(tabMap[tab]).classList.add('active');
  var screenMap = {
    home:'screenHome', cats:'screenCats',
    bookmarks:'screenBookmarks', settings:'screenSettings'
  };
  if (screenMap[tab]) {
    showScreen(screenMap[tab]);
    if (tab === 'home')      loadHome();
    if (tab === 'cats')      loadCategories();
    if (tab === 'bookmarks') loadBookmarks();
    if (tab === 'settings')  loadSettings();
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
      document.getElementById('homeStatAnswered').textContent = ov.total_q || '–';
      document.getElementById('homeStatCorrect').textContent  = ov.total_correct || '–';
      document.getElementById('homeStatAcc').textContent      = ov.pct != null ? Math.round(ov.pct) + '%' : '–';
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
      grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>Ingen kategorier funnet</p></div>';
      return;
    }
    grid.innerHTML = cats.map(function(c) {
      var icon  = CAT_ICONS[c.name] || '📖';
      var count = c.question_count || c.count || '';
      var id    = escH(String(c.id || c.name));
      var name  = escH(CAT_NO[c.name] || c.name);
      return '<div class="cat-card" onclick="startQuiz(\'' + id + '\',\'' + name + '\')">'
        + '<div class="cat-icon">' + icon + '</div>'
        + '<div class="cat-name">' + name + '</div>'
        + '<div class="cat-count">' + (count ? count + ' spørsmål' : '') + '</div>'
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
  await loadQuiz('/api/questions/random?count=30&has_image=true');
}

async function startQuiz(catId, catName) {
  currentCat = { id: catId, name: catName };
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
      return u && typeof u === 'string' && u.startsWith('http') && u.length < 1000;
    });
    if (!questions.length && currentCat) {
      var r2 = await api('GET', '/api/questions/random?count=30&has_image=true');
      if (!Array.isArray(r2)) r2 = r2.questions || [];
      questions = r2.filter(function(q) {
        var u = q.bildeUrl || q.image_url || '';
        return u && typeof u === 'string' && u.startsWith('http') && u.length < 1000;
      });
    }
    if (!questions.length) {
      qCard.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>Ingen spørsmål med bilde funnet.<br>Prøv en annen kategori.</p></div>';
      return;
    }
    qIdx = 0; qScore = 0; qAnswered = false;
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

function renderQuestion() {
  if (qIdx >= questions.length) { showEnd(); return; }
  var q     = questions[qIdx];
  qAnswered = false;
  var total = questions.length;
  var pct   = (qIdx / total * 100).toFixed(0);

  document.getElementById('qProgLbl').textContent  = 'Spørsmål ' + (qIdx + 1) + ' av ' + total;
  document.getElementById('qProgFill').style.width = pct + '%';
  document.getElementById('qScoreNum').textContent = qScore;

  var imgUrl  = q.bildeUrl || q.image_url || '';
  var qText   = pickLang(q.question) || q.question_text_no || q.question_text || '';
  var correct = (q.correctOptionId || q.correct_answer || '').toUpperCase();
  var expl    = pickLang(q.explanation) || q.explanation_no || '';
  var qId     = q._id || q.id || q.question_id || '';
  var isBm    = bookmarkedIds[qId] ? true : false;

  var opts = [];
  if (q.options && Array.isArray(q.options) && q.options.length) {
    opts = q.options.map(function(o) {
      return { id: String(o.id || o.key || '').toUpperCase(), text: pickLang(o.text) || pickLang(o) || String(o.text || '') };
    });
  } else {
    ['A','B','C','D'].forEach(function(l) {
      var key = 'answer_' + l.toLowerCase() + '_no';
      var val = q[key] || q['answer_' + l.toLowerCase()];
      if (val) opts.push({ id: l, text: val });
    });
  }
  opts = opts.filter(function(o) { return o.text; });

  var qCard = document.getElementById('qCard');
  var ansHtml = opts.map(function(o) {
    var txt = typeof o.text === 'object' ? pickLang(o.text) : o.text;
    return '<button class="ans-btn" data-id="' + escH(o.id) + '" onclick="selectAns(this,\'' + escH(o.id) + '\',\'' + escH(correct) + '\',\'' + escH(expl).replace(/'/g,"&#39;") + '\')">'
      + '<span class="ans-letter">' + escH(o.id) + '</span>'
      + '<span class="ans-text">' + escH(txt) + '</span>'
      + '</button>';
  }).join('');

  var spdHtml = [0.5, 0.75, 1, 1.5, 2].map(function(r) {
    return '<button class="spd-btn' + (ttsRate === r ? ' active' : '') + '" data-rate="' + r + '" onclick="setRate(' + r + ',this)">' + r + 'x</button>';
  }).join('');

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
      + '<button class="q-next-mobile" id="qNextMobile" disabled onclick="nextQ()">Neste →</button>'
    + '</div>'
    + '<div class="q-next-col">'
      + '<button class="q-next-big" id="qNextBig" disabled onclick="nextQ()">Neste →</button>'
      + '<button class="q-bookmark-btn' + (isBm ? ' bookmarked' : '') + '" id="qBmBtn" onclick="toggleBookmark(\'' + escH(qId) + '\')" title="Bokmerke">'
        + (isBm ? '🔖' : '🔖')
      + '</button>'
    + '</div>';
}

function selectAns(btn, picked, correct, expl) {
  if (qAnswered) return;
  qAnswered = true;
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
  fb.textContent = isOk ? '🎉 Riktig!' : '❌ Feil svar';
  fb.className = 'q-feedback ' + (isOk ? 'ok' : 'bad');

  var cleanExpl = expl.replace(/&#39;/g, "'");
  if (cleanExpl) {
    var ex = document.getElementById('qExplain');
    ex.textContent = cleanExpl;
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
  if (qIdx >= questions.length) showEnd();
  else renderQuestion();
}

function goBack() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  ttsPlaying = false;
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
      var qText  = pickLang(q.question) || q.question_text_no || q.question_text || '';
      var correct = (q.correctOptionId || q.correct_answer || '').toUpperCase();
      var ansText = '';
      if (q.options && Array.isArray(q.options)) {
        var correctOpt = q.options.find(function(o) { return String(o.id || o.key || '').toUpperCase() === correct; });
        if (correctOpt) ansText = pickLang(correctOpt.text) || pickLang(correctOpt) || '';
      }
      if (!ansText) {
        var key = 'answer_' + correct.toLowerCase() + '_no';
        ansText = q[key] || q['answer_' + correct.toLowerCase()] || '';
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
  document.getElementById('settEmail').textContent = (user && user.email) ? user.email : '–';
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
  });
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
