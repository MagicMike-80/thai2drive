from fastapi import APIRouter
from fastapi.responses import HTMLResponse

webapp_router = APIRouter()

WEBAPP_HTML = """<!DOCTYPE html>
<html lang="th" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
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
  --nav-h: 64px;
  --bottom-h: 68px;
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
*,*::before,*::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  height: 100%; overflow: hidden;
  background: var(--bg);
  color: var(--text);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
button { font-family: inherit; }
a { color: inherit; text-decoration: none; }

/* ══════════════════════════════════════════
   APP SHELL
══════════════════════════════════════════ */
#app {
  width: 100%; height: 100%;
  display: flex; flex-direction: column;
  position: relative; overflow: hidden;
}

/* Scrollable content area */
#content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  position: relative;
}

/* ══════════════════════════════════════════
   TOP BAR (shown when logged in)
══════════════════════════════════════════ */
#topBar {
  height: var(--nav-h);
  background: rgba(11,18,38,.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  display: none; align-items: center;
  padding: 0 20px; gap: 12px;
  flex-shrink: 0; z-index: 50;
}
[data-theme="light"] #topBar { background: rgba(241,245,249,.92); }
.top-logo {
  display: flex; align-items: center; gap: 8px;
  font-weight: 900; font-size: 1.1rem; letter-spacing: -.3px;
}
.top-logo .logo-icon {
  width: 34px; height: 34px; border-radius: 10px;
  background: var(--orange);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 900; color: #0F172A;
}
.top-logo .logo-t { color: var(--orange); }
.top-spacer { flex: 1; }
#topStreak {
  display: flex; align-items: center; gap: 5px;
  background: var(--orange-glow); border: 1px solid rgba(255,153,51,.3);
  border-radius: 20px; padding: 5px 12px;
  font-size: .8rem; font-weight: 700; color: var(--orange);
}

/* ══════════════════════════════════════════
   BOTTOM NAV
══════════════════════════════════════════ */
#bottomNav {
  height: var(--bottom-h);
  background: rgba(11,18,38,.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border);
  display: none; align-items: stretch;
  flex-shrink: 0; z-index: 50;
}
[data-theme="light"] #bottomNav { background: rgba(241,245,249,.96); }
.bn-tab {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px;
  border: none; background: transparent; color: var(--muted);
  cursor: pointer; font-size: .7rem; font-weight: 600;
  transition: color .2s; padding: 8px 4px;
  letter-spacing: .2px;
}
.bn-tab .bn-icon { font-size: 22px; line-height: 1; transition: transform .2s; }
.bn-tab.active { color: var(--orange); }
.bn-tab.active .bn-icon { transform: scale(1.15); }
.bn-tab:active .bn-icon { transform: scale(.92); }

/* ══════════════════════════════════════════
   SCREENS
══════════════════════════════════════════ */
.screen { display: none; min-height: 100%; }
.screen.active { display: block; }

/* ══════════════════════════════════════════
   THAI FLAG BACKGROUND
══════════════════════════════════════════ */
.flag-bg {
  position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background:
    linear-gradient(180deg,
      rgba(165,25,49,.12) 0%,
      rgba(165,25,49,.12) 14.28%,
      rgba(255,255,255,.03) 14.28%,
      rgba(255,255,255,.03) 28.57%,
      rgba(36,29,79,.22) 28.57%,
      rgba(36,29,79,.22) 71.42%,
      rgba(255,255,255,.03) 71.42%,
      rgba(255,255,255,.03) 85.71%,
      rgba(165,25,49,.12) 85.71%,
      rgba(165,25,49,.12) 100%
    );
}
.flag-bg::after {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(255,153,51,.07) 0%, transparent 65%);
}

/* ══════════════════════════════════════════
   AUTH SCREEN
══════════════════════════════════════════ */
#screenAuth {
  min-height: 100%;
  display: flex; align-items: center; justify-content: center;
  padding: 32px 20px;
}
.auth-card {
  background: rgba(15,23,42,.85);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 36px 32px;
  width: 100%; max-width: 400px;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow: 0 32px 64px rgba(0,0,0,.5);
}
[data-theme="light"] .auth-card {
  background: rgba(255,255,255,.92);
  box-shadow: 0 20px 60px rgba(0,0,0,.12);
}
.auth-header { text-align: center; margin-bottom: 28px; }
.auth-big-icon {
  width: 72px; height: 72px; border-radius: 20px;
  background: linear-gradient(135deg, #FF9933, #e6891f);
  display: flex; align-items: center; justify-content: center;
  font-size: 36px; margin: 0 auto 14px;
  box-shadow: 0 8px 24px rgba(255,153,51,.4);
}
.auth-header h1 { font-size: 1.6rem; font-weight: 900; letter-spacing: -.5px; }
.auth-header h1 span { color: var(--orange); }
.auth-header p { color: var(--muted); font-size: .875rem; margin-top: 6px; }

.auth-tabs {
  display: flex; gap: 4px;
  background: rgba(255,255,255,.05);
  border-radius: 12px; padding: 4px;
  margin-bottom: 24px;
}
[data-theme="light"] .auth-tabs { background: rgba(0,0,0,.06); }
.auth-tab {
  flex: 1; padding: 9px; border-radius: 9px;
  border: none; background: transparent;
  color: var(--muted); font-size: .875rem; font-weight: 700;
  cursor: pointer; transition: all .2s;
}
.auth-tab.active { background: var(--orange); color: #0F172A; }

.form-group { margin-bottom: 14px; }
.form-group label {
  display: block; font-size: .75rem; font-weight: 700;
  color: var(--muted); margin-bottom: 6px; letter-spacing: .5px;
  text-transform: uppercase;
}
.form-group input {
  width: 100%; padding: 12px 15px;
  background: rgba(255,255,255,.06);
  border: 1.5px solid var(--border);
  border-radius: 12px; color: var(--text);
  font-size: .9rem; outline: none;
  transition: border-color .2s, box-shadow .2s;
}
[data-theme="light"] .form-group input { background: rgba(0,0,0,.04); }
.form-group input:focus {
  border-color: var(--orange);
  box-shadow: 0 0 0 3px rgba(255,153,51,.12);
}
.form-group input::placeholder { color: rgba(148,163,184,.5); }

.auth-btn {
  width: 100%; padding: 14px;
  background: linear-gradient(135deg, #FF9933, #e6891f);
  color: #0F172A; font-weight: 800; font-size: 1rem;
  border: none; border-radius: 12px;
  cursor: pointer; margin-top: 6px;
  box-shadow: 0 4px 16px rgba(255,153,51,.35);
  transition: transform .15s, box-shadow .15s;
}
.auth-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(255,153,51,.45); }
.auth-btn:active { transform: translateY(0); box-shadow: 0 2px 10px rgba(255,153,51,.3); }
.auth-btn:disabled { opacity: .5; cursor: not-allowed; transform: none; }

.auth-error {
  background: rgba(239,68,68,.1); border: 1px solid rgba(239,68,68,.3);
  border-radius: 10px; padding: 11px 14px;
  color: #FCA5A5; font-size: .85rem; margin-bottom: 16px; display: none;
}
.auth-error.show { display: block; }
.auth-success {
  background: rgba(16,185,129,.1); border: 1px solid rgba(16,185,129,.3);
  border-radius: 10px; padding: 11px 14px;
  color: #6EE7B7; font-size: .85rem; margin-bottom: 16px; display: none;
}
.auth-success.show { display: block; }

.forgot-link { text-align: right; margin: -6px 0 14px; }
.forgot-link a { font-size: .78rem; color: var(--muted); cursor: pointer; }
.forgot-link a:hover { color: var(--orange); }

/* ══════════════════════════════════════════
   HOME SCREEN
══════════════════════════════════════════ */
#screenHome { padding: 24px 20px 20px; }

.home-hero {
  text-align: center; margin-bottom: 28px; padding-top: 8px;
}
.home-greeting {
  font-size: 1rem; color: var(--muted); margin-bottom: 6px;
  font-weight: 500;
}
.home-name {
  font-size: 1.8rem; font-weight: 900; letter-spacing: -.5px;
  margin-bottom: 18px;
}
.home-name span { color: var(--orange); }

.streak-badge {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(255,153,51,.12);
  border: 1.5px solid rgba(255,153,51,.3);
  border-radius: 50px; padding: 8px 20px;
  margin-bottom: 28px;
}
.streak-fire { font-size: 1.4rem; }
.streak-num { font-size: 1.5rem; font-weight: 900; color: var(--orange); }
.streak-lbl { font-size: .8rem; color: var(--muted); font-weight: 600; }

.home-cta {
  width: 100%; padding: 17px;
  background: linear-gradient(135deg, #FF9933, #e6891f);
  color: #0F172A; font-weight: 900; font-size: 1.05rem;
  border: none; border-radius: 16px; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  box-shadow: 0 6px 24px rgba(255,153,51,.4);
  transition: transform .15s, box-shadow .15s;
  margin-bottom: 12px;
}
.home-cta:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(255,153,51,.5); }
.home-cta:active { transform: translateY(0); }

.home-sec-btns {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 10px; margin-bottom: 28px;
}
.home-sec-btn {
  padding: 13px 10px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; color: var(--text); font-weight: 700;
  font-size: .875rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 7px;
  transition: border-color .2s, background .2s;
}
.home-sec-btn:hover { border-color: var(--orange); background: var(--orange-glow); }

.home-stats {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 10px; margin-bottom: 24px;
}
.home-stat {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 16px 10px;
  text-align: center;
}
.home-stat-num {
  font-size: 1.6rem; font-weight: 900; color: var(--orange);
  line-height: 1;
}
.home-stat-lbl {
  font-size: .65rem; color: var(--muted); font-weight: 700;
  margin-top: 5px; letter-spacing: .4px; text-transform: uppercase;
}

.premium-banner {
  background: linear-gradient(135deg, rgba(255,153,51,.15), rgba(230,137,31,.08));
  border: 1px solid rgba(255,153,51,.3);
  border-radius: 14px; padding: 14px 16px;
  display: flex; align-items: center; gap: 12px;
}
.premium-banner .pb-icon { font-size: 1.5rem; }
.premium-banner .pb-text h4 { font-size: .9rem; font-weight: 800; color: var(--orange); }
.premium-banner .pb-text p { font-size: .75rem; color: var(--muted); margin-top: 2px; }
.premium-badge {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(255,153,51,.2); border: 1px solid rgba(255,153,51,.4);
  border-radius: 20px; padding: 3px 10px;
  font-size: .7rem; font-weight: 800; color: var(--orange);
  letter-spacing: .3px;
}
.admin-badge {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(16,185,129,.15); border: 1px solid rgba(16,185,129,.3);
  border-radius: 20px; padding: 3px 10px;
  font-size: .7rem; font-weight: 800; color: var(--green);
  letter-spacing: .3px;
}

/* ══════════════════════════════════════════
   CATEGORIES SCREEN
══════════════════════════════════════════ */
#screenCats { padding: 24px 20px 20px; }

.screen-title {
  font-size: 1.4rem; font-weight: 900; letter-spacing: -.3px;
  margin-bottom: 18px;
}
.screen-title span { color: var(--muted); font-size: 1rem; font-weight: 600; margin-left: 6px; }

.cat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
@media (min-width: 500px) {
  .cat-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 700px) {
  .cat-grid { grid-template-columns: repeat(4, 1fr); }
}

.cat-card {
  background: var(--card); border: 1.5px solid var(--border);
  border-radius: 16px; padding: 18px 14px;
  cursor: pointer; transition: border-color .2s, transform .15s, box-shadow .2s;
  display: flex; flex-direction: column; gap: 8px;
}
.cat-card:hover {
  border-color: var(--orange); transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255,153,51,.12);
}
.cat-card:active { transform: translateY(0); }
.cat-icon { font-size: 2rem; line-height: 1; }
.cat-name { font-weight: 800; font-size: .9rem; line-height: 1.3; }
.cat-count { font-size: .75rem; color: var(--muted); font-weight: 500; }
.cat-bar-wrap {
  height: 3px; background: rgba(255,255,255,.07);
  border-radius: 2px; overflow: hidden; margin-top: 4px;
}
[data-theme="light"] .cat-bar-wrap { background: rgba(0,0,0,.07); }
.cat-bar { height: 100%; background: var(--orange); border-radius: 2px; transition: width .4s; }

/* ══════════════════════════════════════════
   QUIZ SCREEN
══════════════════════════════════════════ */
#screenQuiz { padding: 0; }

.quiz-top {
  padding: 16px 20px 12px;
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 14px;
}
[data-theme="light"] .quiz-top { background: var(--bg2); }
.back-btn {
  padding: 8px 14px; border-radius: 10px;
  border: 1.5px solid var(--border); background: transparent;
  color: var(--muted); font-size: .85rem; font-weight: 600;
  cursor: pointer; transition: all .2s; flex-shrink: 0;
  display: flex; align-items: center; gap: 6px;
}
.back-btn:hover { border-color: var(--orange); color: var(--text); }

.quiz-prog-wrap { flex: 1; }
.quiz-prog-lbl { font-size: .75rem; color: var(--muted); margin-bottom: 5px; font-weight: 600; }
.quiz-prog-bar {
  height: 5px; background: rgba(255,255,255,.08);
  border-radius: 3px; overflow: hidden;
}
[data-theme="light"] .quiz-prog-bar { background: rgba(0,0,0,.08); }
.quiz-prog-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--orange), #FFB347);
  border-radius: 3px; transition: width .4s;
}
.quiz-score-badge {
  display: flex; align-items: center; gap: 5px;
  background: rgba(16,185,129,.12); border: 1px solid rgba(16,185,129,.25);
  border-radius: 20px; padding: 5px 12px;
  font-size: .8rem; font-weight: 800; color: var(--green);
  flex-shrink: 0;
}

.quiz-body {
  padding: 16px 20px 20px;
}

/* Desktop: 3-col layout */
.quiz-card {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 20px;
  align-items: start;
}
@media (max-width: 700px) {
  .quiz-card { grid-template-columns: 1fr; }
  .q-next-col { display: none; }
}

.q-left { display: flex; flex-direction: column; gap: 14px; }

.q-img-wrap {
  width: 100%; border-radius: 14px; overflow: hidden;
  background: rgba(255,255,255,.04); border: 1px solid var(--border);
  aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center;
}
.q-img { width: 100%; height: 100%; object-fit: contain; display: block; }

.q-text {
  font-size: 1rem; font-weight: 700; line-height: 1.6;
}

.q-tts {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.tts-play {
  width: 36px; height: 36px; border-radius: 50%;
  border: 1.5px solid var(--border); background: rgba(255,255,255,.05);
  color: var(--text); cursor: pointer; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s; flex-shrink: 0;
}
.tts-play:hover, .tts-play.playing {
  border-color: var(--orange); color: var(--orange); background: rgba(255,153,51,.1);
}
.spd-btn {
  padding: 4px 10px; border-radius: 20px;
  border: 1.5px solid var(--border); background: transparent;
  color: var(--muted); font-size: .72rem; font-weight: 800; cursor: pointer;
  transition: all .2s;
}
.spd-btn:hover { border-color: var(--orange); }
.spd-btn.active {
  background: rgba(255,153,51,.15); border-color: var(--orange); color: var(--orange);
}

.q-right { display: flex; flex-direction: column; gap: 10px; }
.q-answers { display: flex; flex-direction: column; gap: 9px; }

.ans-btn {
  display: flex; align-items: center; gap: 12px;
  padding: 13px 14px;
  background: rgba(255,255,255,.04);
  border: 1.5px solid var(--border);
  border-radius: 14px; cursor: pointer; text-align: left;
  color: var(--text); font-size: .875rem;
  transition: border-color .2s, background .2s, transform .1s;
  width: 100%;
}
.ans-btn:hover:not(:disabled) {
  border-color: var(--orange); background: rgba(255,153,51,.07);
  transform: translateX(2px);
}
.ans-btn:disabled { cursor: default; }
.ans-btn.correct {
  border-color: var(--green); background: rgba(16,185,129,.12);
}
.ans-btn.wrong {
  border-color: var(--red); background: rgba(239,68,68,.1);
}
.ans-btn.reveal {
  border-color: var(--green); background: rgba(16,185,129,.06);
}
.ans-letter {
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(255,153,51,.12); color: var(--orange);
  font-size: .78rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all .2s;
}
.ans-btn.correct .ans-letter { background: var(--green); color: #fff; }
.ans-btn.wrong .ans-letter { background: var(--red); color: #fff; }
.ans-btn.reveal .ans-letter { background: var(--green); color: #fff; }
.ans-text { flex: 1; line-height: 1.4; }

.q-feedback {
  padding: 12px 14px; border-radius: 12px;
  font-size: .875rem; font-weight: 700;
  display: none; align-items: center; gap: 8px;
}
.q-feedback.ok {
  background: rgba(16,185,129,.1); border: 1px solid rgba(16,185,129,.3);
  color: #6EE7B7; display: flex;
}
.q-feedback.bad {
  background: rgba(239,68,68,.08); border: 1px solid rgba(239,68,68,.25);
  color: #FCA5A5; display: flex;
}
.q-explain {
  padding: 12px 14px;
  background: rgba(255,153,51,.07); border: 1px solid rgba(255,153,51,.15);
  border-radius: 12px; font-size: .83rem; color: var(--muted);
  line-height: 1.6; display: none;
}
.q-explain.show { display: block; }

/* Mobile next button */
.q-next-mobile {
  width: 100%; padding: 14px;
  background: linear-gradient(135deg, #FF9933, #e6891f);
  color: #0F172A; font-weight: 900; font-size: .95rem;
  border: none; border-radius: 14px; cursor: pointer;
  margin-top: 10px; display: none;
  box-shadow: 0 4px 16px rgba(255,153,51,.35);
  transition: transform .15s;
}
.q-next-mobile:disabled { opacity: .35; cursor: not-allowed; }
.q-next-mobile:not(:disabled):hover { transform: translateY(-1px); }
@media (max-width: 700px) { .q-next-mobile { display: block; } }

/* Desktop side next button */
.q-next-col { display: flex; align-items: center; justify-content: center; }
.q-next-big {
  writing-mode: vertical-rl;
  padding: 22px 14px;
  background: linear-gradient(180deg, #FF9933, #e6891f);
  color: #0F172A; font-weight: 900; font-size: 15px;
  border: none; border-radius: 16px; cursor: pointer;
  min-height: 140px; width: 50px;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s;
  box-shadow: 0 4px 16px rgba(255,153,51,.3);
}
.q-next-big:disabled { opacity: .35; cursor: not-allowed; box-shadow: none; }
.q-next-big:not(:disabled):hover { transform: scale(1.04); box-shadow: 0 6px 20px rgba(255,153,51,.45); }

/* ══════════════════════════════════════════
   SETTINGS SCREEN
══════════════════════════════════════════ */
#screenSettings { padding: 24px 20px 20px; }

.settings-section { margin-bottom: 20px; }
.settings-label {
  font-size: .7rem; font-weight: 800; color: var(--muted);
  letter-spacing: .8px; text-transform: uppercase;
  margin-bottom: 8px; padding: 0 4px;
}
.settings-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 16px; overflow: hidden;
}
.settings-row {
  display: flex; align-items: center; gap: 14px;
  padding: 15px 16px;
  border-bottom: 1px solid var(--border);
}
.settings-row:last-child { border-bottom: none; }
.sr-icon { font-size: 1.2rem; width: 28px; text-align: center; flex-shrink: 0; }
.sr-label { flex: 1; }
.sr-label .sr-title { font-size: .9rem; font-weight: 700; }
.sr-label .sr-sub { font-size: .75rem; color: var(--muted); margin-top: 2px; }
.sr-val { color: var(--muted); font-size: .8rem; font-weight: 600; }

/* Toggle switch */
.toggle {
  position: relative; width: 46px; height: 26px; flex-shrink: 0;
}
.toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
.toggle-slider {
  position: absolute; inset: 0; border-radius: 13px;
  background: rgba(255,255,255,.12); cursor: pointer; transition: .3s;
}
[data-theme="light"] .toggle-slider { background: rgba(0,0,0,.12); }
.toggle-slider::before {
  content: ''; position: absolute;
  width: 20px; height: 20px; border-radius: 50%;
  left: 3px; bottom: 3px;
  background: #fff; transition: .3s;
  box-shadow: 0 2px 4px rgba(0,0,0,.3);
}
.toggle input:checked + .toggle-slider { background: var(--orange); }
.toggle input:checked + .toggle-slider::before { transform: translateX(20px); }

/* Segmented control */
.seg-ctrl {
  display: flex; gap: 4px;
  background: rgba(255,255,255,.06); border-radius: 10px; padding: 3px;
}
[data-theme="light"] .seg-ctrl { background: rgba(0,0,0,.06); }
.seg-btn {
  padding: 5px 12px; border-radius: 8px;
  border: none; background: transparent;
  color: var(--muted); font-size: .78rem; font-weight: 700;
  cursor: pointer; transition: all .2s;
}
.seg-btn.active { background: var(--orange); color: #0F172A; }

/* Lang buttons */
.lang-btns { display: flex; gap: 12px; }
.lang-btn {
  width: 52px; height: 52px; border-radius: 50%;
  border: 2.5px solid var(--border); background: transparent;
  cursor: pointer; transition: all .2s;
  position: relative; overflow: hidden; padding: 0;
  flex-shrink: 0;
}
.lang-btn.active { border-color: var(--orange); box-shadow: 0 0 0 3px rgba(255,153,51,.3); transform: scale(1.1); }
.lang-btn:hover:not(.active) { border-color: rgba(255,255,255,.4); transform: scale(1.06); }
.lang-btn .cflag { width: 100%; height: 100%; display: block; position: absolute; inset: 0; }
.lang-btn .cflag svg { width: 100%; height: 100%; display: block; }

.account-info { display: flex; flex-direction: column; gap: 4px; }
.account-email { font-size: .9rem; font-weight: 700; }
.account-badges { display: flex; gap: 6px; margin-top: 4px; }

.logout-btn {
  width: 100%; padding: 14px;
  background: rgba(239,68,68,.1); border: 1.5px solid rgba(239,68,68,.25);
  color: #EF4444; font-weight: 800; font-size: .95rem;
  border-radius: 14px; cursor: pointer; margin-top: 8px;
  transition: all .2s;
}
.logout-btn:hover { background: rgba(239,68,68,.18); border-color: rgba(239,68,68,.4); }

/* ══════════════════════════════════════════
   END SCREEN
══════════════════════════════════════════ */
#screenEnd { display: none; min-height: 100%; }
#screenEnd.active {
  display: flex; align-items: center; justify-content: center;
  padding: 40px 24px;
}
.end-wrap { text-align: center; max-width: 380px; width: 100%; }
.end-emoji { font-size: 5rem; margin-bottom: 14px; display: block; }
.end-pct { font-size: 3.5rem; font-weight: 900; color: var(--orange); line-height: 1; }
.end-score-lbl { font-size: 1.1rem; color: var(--muted); font-weight: 600; margin: 8px 0 6px; }
.end-msg { color: var(--muted); font-size: .875rem; margin-bottom: 32px; line-height: 1.5; }
.end-btns { display: flex; flex-direction: column; gap: 10px; }
.end-btn-pri {
  padding: 14px;
  background: linear-gradient(135deg, #FF9933, #e6891f);
  color: #0F172A; font-weight: 800; font-size: .95rem;
  border: none; border-radius: 14px; cursor: pointer;
  box-shadow: 0 4px 16px rgba(255,153,51,.35); transition: transform .15s;
}
.end-btn-pri:hover { transform: translateY(-1px); }
.end-btn-sec {
  padding: 13px;
  background: var(--card); border: 1.5px solid var(--border);
  color: var(--text); font-weight: 700; font-size: .9rem;
  border-radius: 14px; cursor: pointer; transition: border-color .2s;
}
.end-btn-sec:hover { border-color: var(--orange); }

/* ══════════════════════════════════════════
   LOADING & UTILS
══════════════════════════════════════════ */
.loading-wrap {
  display: flex; align-items: center; justify-content: center;
  padding: 60px 20px; flex-direction: column; gap: 14px;
}
.spinner {
  width: 40px; height: 40px;
  border: 3px solid var(--border); border-top-color: var(--orange);
  border-radius: 50%; animation: spin .75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  text-align: center; padding: 48px 20px; color: var(--muted);
}
.empty-state .es-icon { font-size: 2.5rem; margin-bottom: 10px; }
.empty-state p { font-size: .875rem; line-height: 1.6; }

/* Toast */
.toast {
  position: fixed; bottom: 84px; left: 50%; transform: translateX(-50%) translateY(10px);
  background: #1E293B; border: 1px solid var(--border);
  border-radius: 12px; padding: 11px 20px;
  font-size: .875rem; color: var(--text);
  opacity: 0; pointer-events: none;
  transition: opacity .25s, transform .25s;
  z-index: 999; white-space: nowrap;
  box-shadow: 0 8px 24px rgba(0,0,0,.4);
}
[data-theme="light"] .toast { background: #fff; }
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
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
    <div id="topStreak" style="display:none">🔥 <span id="topStreakNum">–</span> dag streak</div>
  </div>

  <!-- SCROLLABLE CONTENT -->
  <div id="content">

    <!-- ═══ AUTH SCREEN ═══ -->
    <div class="screen active" id="screenAuth">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-big-icon">🚗</div>
          <h1>Thai<span>2Drive</span></h1>
          <p>Teoriprøven på thai &nbsp;🇹🇭&nbsp;🇳🇴</p>
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
          <div style="text-align:center;margin-top:14px">
            <a style="font-size:.8rem;color:var(--muted);cursor:pointer" onclick="switchTab('login')">← Tilbake</a>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ HOME SCREEN ═══ -->
    <div class="screen" id="screenHome">
      <div class="home-hero">
        <div class="home-greeting">God dag! 👋</div>
        <div class="home-name">Hei, <span id="homeName">der</span>!</div>

        <div class="streak-badge">
          <span class="streak-fire">🔥</span>
          <span class="streak-num" id="homeStreakNum">–</span>
          <span class="streak-lbl">dag streak</span>
        </div>

        <button class="home-cta" onclick="startRandomQuiz()">
          ▶&nbsp;&nbsp;Start quiz
        </button>

        <div class="home-sec-btns">
          <button class="home-sec-btn" onclick="startRandomQuiz()">
            📋 Eksamen
          </button>
          <button class="home-sec-btn" onclick="startRandomQuiz()">
            📅 Daglig test
          </button>
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
          <span class="pb-icon">⭐</span>
          <div class="pb-text">
            <h4>Premium aktiv</h4>
            <p>Du har tilgang til alle funksjoner</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ CATEGORIES SCREEN ═══ -->
    <div class="screen" id="screenCats">
      <div class="screen-title">📚 Kategorier <span id="catCount"></span></div>
      <div class="cat-grid" id="catGrid">
        <div class="loading-wrap" style="grid-column:1/-1">
          <div class="spinner"></div>
          <span style="color:var(--muted);font-size:.875rem">Laster kategorier…</span>
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

    <!-- ═══ SETTINGS SCREEN ═══ -->
    <div class="screen" id="screenSettings">
      <div class="screen-title">⚙️ Innstillinger</div>

      <!-- Account -->
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

      <!-- Language -->
      <div class="settings-section">
        <div class="settings-label">Språk</div>
        <div class="settings-card">
          <div class="settings-row">
            <div class="sr-icon">🌐</div>
            <div class="sr-label">
              <div class="sr-title">Spørsmålsspråk</div>
              <div class="sr-sub">Språk for spørsmål og svar</div>
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

      <!-- Sound & Haptics -->
      <div class="settings-section">
        <div class="settings-label">Lyd og tilbakemelding</div>
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
            <div class="sr-label">
              <div class="sr-title">Tilbakemeldingsstil</div>
            </div>
            <div class="seg-ctrl">
              <button class="seg-btn active" onclick="setFeedback('soft',this)">Myk</button>
              <button class="seg-btn" onclick="setFeedback('strong',this)">Sterk</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Theme -->
      <div class="settings-section">
        <div class="settings-label">Utseende</div>
        <div class="settings-card">
          <div class="settings-row">
            <div class="sr-icon">🎨</div>
            <div class="sr-label">
              <div class="sr-title">Tema</div>
            </div>
            <div class="seg-ctrl">
              <button class="seg-btn" id="themeBtnLight" onclick="setTheme('light',this)">Lys</button>
              <button class="seg-btn active" id="themeBtnDark" onclick="setTheme('dark',this)">Mørk</button>
              <button class="seg-btn" id="themeBtnSys" onclick="setTheme('system',this)">Auto</button>
            </div>
          </div>
        </div>
      </div>

      <!-- App info -->
      <div class="settings-section">
        <div class="settings-label">Om appen</div>
        <div class="settings-card">
          <div class="settings-row">
            <div class="sr-icon">📱</div>
            <div class="sr-label">
              <div class="sr-title">Thai2Drive Web</div>
              <div class="sr-sub">Teoriprøven på thai for Norge</div>
            </div>
            <div class="sr-val">v1.0</div>
          </div>
        </div>
      </div>

      <button class="logout-btn" onclick="logout()">🚪 &nbsp;Logg ut</button>
      <div style="height:12px"></div>
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

  <!-- BOTTOM NAV -->
  <div id="bottomNav">
    <button class="bn-tab active" id="bnHome" onclick="showTab('home')">
      <span class="bn-icon">🏠</span>
      Hjem
    </button>
    <button class="bn-tab" id="bnCats" onclick="showTab('cats')">
      <span class="bn-icon">📚</span>
      Kategorier
    </button>
    <button class="bn-tab" id="bnSettings" onclick="showTab('settings')">
      <span class="bn-icon">⚙️</span>
      Innstillinger
    </button>
  </div>

</div><!-- /app -->

<div class="toast" id="toast"></div>

<script>
// ════════════════════════════════════════════
//  STATE
// ════════════════════════════════════════════
let token = localStorage.getItem('t2d_token');
let user = null;
let questions = [];
let qIdx = 0;
let qScore = 0;
let qAnswered = false;
let ttsRate = 1;
let ttsUtterance = null;
let ttsPlaying = false;
let currentCat = null;
let soundOn = localStorage.getItem('t2d_sound') !== 'off';
let feedbackStyle = localStorage.getItem('t2d_feedback') || 'soft';
let appLang = localStorage.getItem('t2d_lang') || 'th';
let activeTab = 'home';

// ════════════════════════════════════════════
//  INIT
// ════════════════════════════════════════════
(async function init() {
  applyThemeFromStorage();
  applySoundToggle();

  if (token) {
    try {
      user = await api('GET', '/api/auth/me');
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
//  SCREEN MANAGEMENT
// ════════════════════════════════════════════
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const el = document.getElementById(id);
  if (el) el.classList.add('active');
  document.getElementById('content').scrollTop = 0;
}

function enterApp() {
  document.getElementById('topBar').style.display = 'flex';
  document.getElementById('bottomNav').style.display = 'flex';
  showTab('home');
}

function showTab(tab) {
  activeTab = tab;
  // Update bottom nav
  document.querySelectorAll('.bn-tab').forEach(b => b.classList.remove('active'));
  const tabMap = { home: 'bnHome', cats: 'bnCats', settings: 'bnSettings' };
  if (tabMap[tab]) document.getElementById(tabMap[tab]).classList.add('active');

  const screenMap = {
    home: 'screenHome',
    cats: 'screenCats',
    settings: 'screenSettings'
  };
  if (screenMap[tab]) {
    showScreen(screenMap[tab]);
    if (tab === 'home') loadHome();
    if (tab === 'cats') loadCategories();
    if (tab === 'settings') loadSettings();
  }
}

// ════════════════════════════════════════════
//  API HELPER
// ════════════════════════════════════════════
async function api(method, url, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(url, opts);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || 'Noe gikk galt');
  return data;
}

// ════════════════════════════════════════════
//  TOAST
// ════════════════════════════════════════════
let toastTimer;
function toast(msg, dur = 2800) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), dur);
}

// ════════════════════════════════════════════
//  AUTH
// ════════════════════════════════════════════
function switchTab(tab) {
  clearAuthMessages();
  document.querySelectorAll('.auth-tab').forEach((t, i) => {
    t.classList.toggle('active', (i === 0 && tab === 'login') || (i === 1 && tab === 'register'));
  });
  document.getElementById('formLogin').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('formRegister').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('formForgot').style.display = 'none';
}

function showForgot() {
  clearAuthMessages();
  document.getElementById('formLogin').style.display = 'none';
  document.getElementById('formForgot').style.display = 'block';
  document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
}

function showAuthError(msg) {
  const el = document.getElementById('authError');
  el.textContent = msg; el.classList.add('show');
  document.getElementById('authSuccess').classList.remove('show');
}
function showAuthSuccess(msg) {
  const el = document.getElementById('authSuccess');
  el.textContent = msg; el.classList.add('show');
  document.getElementById('authError').classList.remove('show');
}
function clearAuthMessages() {
  document.getElementById('authError').classList.remove('show');
  document.getElementById('authSuccess').classList.remove('show');
}

async function doLogin() {
  clearAuthMessages();
  const email = document.getElementById('loginEmail').value.trim();
  const pass = document.getElementById('loginPass').value;
  if (!email || !pass) return showAuthError('Fyll inn e-post og passord');
  const btn = document.querySelector('#formLogin .auth-btn');
  btn.disabled = true; btn.textContent = 'Logger inn…';
  try {
    const r = await api('POST', '/api/auth/login', { email, password: pass });
    token = r.token; user = r.user;
    localStorage.setItem('t2d_token', token);
    enterApp();
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = 'Logg inn';
  }
}

async function doRegister() {
  clearAuthMessages();
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const pass = document.getElementById('regPass').value;
  if (!name || !email || !pass) return showAuthError('Fyll inn alle feltene');
  if (pass.length < 6) return showAuthError('Passord må være minst 6 tegn');
  const btn = document.querySelector('#formRegister .auth-btn');
  btn.disabled = true; btn.textContent = 'Oppretter konto…';
  try {
    const r = await api('POST', '/api/auth/signup', { name, email, password: pass });
    token = r.token; user = r.user;
    localStorage.setItem('t2d_token', token);
    enterApp();
  } catch(e) {
    showAuthError(e.message);
    btn.disabled = false; btn.textContent = 'Opprett konto';
  }
}

async function doForgot() {
  clearAuthMessages();
  const email = document.getElementById('forgotEmail').value.trim();
  if (!email) return showAuthError('Fyll inn e-postadressen din');
  const btn = document.querySelector('#formForgot .auth-btn');
  btn.disabled = true; btn.textContent = 'Sender…';
  try {
    await api('POST', '/api/auth/forgot-password', { email });
    showAuthSuccess('E-post sendt! Sjekk innboksen din 📧');
    setTimeout(() => switchTab('login'), 2500);
  } catch(e) {
    showAuthError(e.message);
  }
  btn.disabled = false; btn.textContent = 'Send tilbakestillingslenke';
}

function logout() {
  if (!confirm('Er du sikker på at du vil logge ut?')) return;
  localStorage.removeItem('t2d_token');
  token = null; user = null;
  document.getElementById('topBar').style.display = 'none';
  document.getElementById('bottomNav').style.display = 'none';
  showScreen('screenAuth');
  switchTab('login');
}

// ════════════════════════════════════════════
//  HOME
// ════════════════════════════════════════════
function loadHome() {
  const name = user?.name || user?.email?.split('@')[0] || 'der';
  document.getElementById('homeName').textContent = name;

  // Streak
  const streak = user?.streak || 0;
  document.getElementById('homeStreakNum').textContent = streak || '–';
  document.getElementById('topStreakNum').textContent = streak || '–';
  if (streak > 0) document.getElementById('topStreak').style.display = 'flex';

  // Stats from localStorage (accumulated during sessions)
  const answered = parseInt(localStorage.getItem('t2d_answered') || '0');
  const correct = parseInt(localStorage.getItem('t2d_correct') || '0');
  document.getElementById('homeStatAnswered').textContent = answered || '–';
  document.getElementById('homeStatCorrect').textContent = correct || '–';
  if (answered > 0) {
    const acc = Math.round(correct / answered * 100);
    document.getElementById('homeStatAcc').textContent = acc + '%';
  } else {
    document.getElementById('homeStatAcc').textContent = '–';
  }

  // Premium banner
  const banner = document.getElementById('homePremiumBanner');
  banner.style.display = user?.is_premium ? 'flex' : 'none';
}

// ════════════════════════════════════════════
//  CATEGORIES
// ════════════════════════════════════════════
const CAT_ICONS = {
  'Trafikkregler': '🚦', 'Skilt': '🪧', 'Vikeplikt': '⚠️',
  'Kjøretøy': '🚗', 'Farlig gods': '☣️', 'Miljø': '🌿',
  'Ulykker': '🚨', 'Alkohol': '🍺', 'Bremser': '🛑',
  'Parkering': '🅿️', 'Lys': '💡', 'Dekk': '🔄',
  'Motorvei': '🛣️', 'Kryss': '✛', 'Gangfelt': '🚶',
  'Sving': '↩️', 'Forbikjøring': '🏎️', 'Lastsikring': '📦',
  'Sikkerhet': '🦺', 'Fellesskjøring': '🤝',
};

let catsLoaded = false;
async function loadCategories() {
  if (catsLoaded) return;
  const grid = document.getElementById('catGrid');
  grid.innerHTML = '<div class="loading-wrap" style="grid-column:1/-1"><div class="spinner"></div></div>';
  try {
    const cats = await api('GET', '/api/categories');
    catsLoaded = true;
    document.getElementById('catCount').textContent = '(' + cats.length + ')';
    if (!cats.length) {
      grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>Ingen kategorier funnet</p></div>';
      return;
    }
    grid.innerHTML = cats.map(c => {
      const icon = CAT_ICONS[c.name] || '📖';
      const count = c.question_count || c.count || '';
      const id = escH(String(c.id || c.name));
      const name = escH(c.name);
      return '<div class="cat-card" onclick="startQuiz(\\''+id+'\\',\\''+name+'\\')"> <div class="cat-icon">'+icon+'</div> <div class="cat-name">'+name+'</div> <div class="cat-count">'+(count ? count+' spørsmål' : '')+'</div> <div class="cat-bar-wrap"><div class="cat-bar" style="width:0%"></div></div> </div>';
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
  const qCard = document.getElementById('qCard');
  qCard.innerHTML = '<div class="loading-wrap" style="grid-column:1/-1"><div class="spinner"></div><span style="color:var(--muted);font-size:.875rem">Laster spørsmål…</span></div>';

  try {
    let raw = await api('GET', url);
    if (!Array.isArray(raw)) raw = raw.questions || [];
    questions = raw.filter(q => {
      const u = q.bildeUrl || q.image_url || '';
      return u && typeof u === 'string' && u.startsWith('http') && u.length < 1000;
    });

    // Fallback: no category filter
    if (!questions.length && currentCat) {
      let r2 = await api('GET', '/api/questions/random?count=30&has_image=true');
      if (!Array.isArray(r2)) r2 = r2.questions || [];
      questions = r2.filter(q => {
        const u = q.bildeUrl || q.image_url || '';
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

  const q = questions[qIdx];
  qAnswered = false;
  const total = questions.length;
  const pct = (qIdx / total * 100).toFixed(0);

  document.getElementById('qProgLbl').textContent = 'Spørsmål ' + (qIdx+1) + ' av ' + total;
  document.getElementById('qProgFill').style.width = pct + '%';
  document.getElementById('qScoreNum').textContent = qScore;

  const imgUrl = q.bildeUrl || q.image_url || '';
  const qText = pickLang(q.question) || q.question_text_no || q.question_text || '';
  const correct = (q.correctOptionId || q.correct_answer || '').toUpperCase();
  const expl = pickLang(q.explanation) || q.explanation_no || '';

  // Build options
  let opts = [];
  if (q.options && Array.isArray(q.options) && q.options.length) {
    opts = q.options.map(o => ({
      id: String(o.id || o.key || '').toUpperCase(),
      text: pickLang(o.text) || pickLang(o) || String(o.text || '')
    }));
  } else {
    const letters = ['A','B','C','D'];
    letters.forEach(l => {
      const key = 'answer_' + l.toLowerCase() + '_no';
      const val = q[key] || q['answer_' + l.toLowerCase()];
      if (val) opts.push({ id: l, text: val });
    });
  }
  opts = opts.filter(o => o.text);

  // Escape for HTML attribute use
  const explSafe = escH(expl).replace(/\\\\/g,'\\\\').replace(/'/g,'&#39;');

  const qCard = document.getElementById('qCard');
  qCard.innerHTML =
    '<div class="q-left">' +
      '<div class="q-img-wrap">' +
        '<img class="q-img" src="' + imgUrl + '" alt="" onerror="this.parentElement.style.display=\\'none\\'" loading="lazy">' +
      '</div>' +
      '<div class="q-text">' + escH(qText) + '</div>' +
      '<div class="q-tts">' +
        '<button class="tts-play" id="qTtsBtn" title="Les høyt" onclick="speakQ()">▶</button>' +
        [0.5,0.75,1,1.5,2].map(r => '<button class="spd-btn'+(ttsRate===r?' active':'')+'" data-rate="'+r+'" onclick="setRate('+r+',this)">'+r+'x</button>').join('') +
      '</div>' +
    '</div>' +
    '<div class="q-right">' +
      '<div class="q-answers" id="qAnswers">' +
        opts.map(o => {
          const txt = typeof o.text === 'object' ? pickLang(o.text) : o.text;
          return '<button class="ans-btn" data-id="'+escH(o.id)+'" onclick="selectAns(this,\\''+escH(o.id)+'\\',\\''+escH(correct)+'\\',\\''+explSafe+'\\')"><span class="ans-letter">'+escH(o.id)+'</span><span class="ans-text">'+escH(txt)+'</span></button>';
        }).join('') +
      '</div>' +
      '<div class="q-feedback" id="qFeedback"></div>' +
      '<div class="q-explain" id="qExplain"></div>' +
      '<button class="q-next-mobile" id="qNextMobile" disabled onclick="nextQ()">Neste →</button>' +
    '</div>' +
    '<div class="q-next-col">' +
      '<button class="q-next-big" id="qNextBig" disabled onclick="nextQ()">Neste →</button>' +
    '</div>';
}

function selectAns(btn, picked, correct, expl) {
  if (qAnswered) return;
  qAnswered = true;

  const isOk = picked.toUpperCase() === correct.toUpperCase();
  if (isOk) qScore++;

  // Accumulate local stats
  const prevAns = parseInt(localStorage.getItem('t2d_answered') || '0');
  const prevCor = parseInt(localStorage.getItem('t2d_correct') || '0');
  localStorage.setItem('t2d_answered', prevAns + 1);
  if (isOk) localStorage.setItem('t2d_correct', prevCor + 1);

  document.querySelectorAll('.ans-btn').forEach(b => {
    b.disabled = true;
    const id = (b.dataset.id || '').toUpperCase();
    if (id === correct && id === picked.toUpperCase()) b.classList.add('correct');
    else if (b === btn) b.classList.add('wrong');
    else if (id === correct) b.classList.add('reveal');
  });

  const fb = document.getElementById('qFeedback');
  fb.textContent = isOk ? '🎉 Riktig!' : '❌ Feil svar';
  fb.className = 'q-feedback ' + (isOk ? 'ok' : 'bad');

  const cleanExpl = expl.replace(/&#39;/g,"'");
  if (cleanExpl) {
    const ex = document.getElementById('qExplain');
    ex.textContent = cleanExpl;
    ex.classList.add('show');
  }

  document.getElementById('qScoreNum').textContent = qScore;

  const nb = document.getElementById('qNextBig');
  const nm = document.getElementById('qNextMobile');
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
  if (activeTab === 'home' || !activeTab || activeTab === 'quiz') {
    showTab('home');
  } else {
    showTab(activeTab);
  }
}

// ════════════════════════════════════════════
//  END SCREEN
// ════════════════════════════════════════════
function showEnd() {
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  showScreen('screenEnd');
  const total = questions.length;
  const pct = total > 0 ? Math.round(qScore / total * 100) : 0;
  document.getElementById('endPct').textContent = pct + '%';
  document.getElementById('endScoreLbl').textContent = qScore + ' av ' + total + ' riktige';
  const emoji = pct >= 85 ? '🏆' : pct >= 65 ? '👍' : pct >= 40 ? '💪' : '📚';
  const msg = pct >= 85 ? 'Fantastisk! Du er klar for teoriprøven!' :
              pct >= 65 ? 'Bra jobbet! Fortsett å øve!' :
              pct >= 40 ? 'Ikke gi opp! Du blir bedre for hver gang.' :
              'Øv mer og prøv igjen. Du klarer det!';
  document.getElementById('endEmoji').textContent = emoji;
  document.getElementById('endMsg').textContent = msg;
}

function retryQuiz() {
  if (currentCat) startQuiz(currentCat.id, currentCat.name);
  else startRandomQuiz();
}

// ════════════════════════════════════════════
//  TTS
// ════════════════════════════════════════════
function speakQ() {
  const q = questions[qIdx];
  if (!q || !window.speechSynthesis) return;

  if (ttsPlaying) {
    window.speechSynthesis.cancel();
    ttsPlaying = false;
    updateTtsBtn(false);
    return;
  }

  const text = pickLang(q.question) || q.question_text_no || '';
  if (!text) return;

  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = appLang === 'th' ? 'th-TH' : appLang === 'no' ? 'nb-NO' : 'en-US';
  utt.rate = ttsRate;

  utt.onstart = () => { ttsPlaying = true; updateTtsBtn(true); };
  utt.onend = () => { ttsPlaying = false; updateTtsBtn(false); };
  utt.onerror = () => { ttsPlaying = false; updateTtsBtn(false); };

  window.speechSynthesis.speak(utt);
}

function updateTtsBtn(playing) {
  const btn = document.getElementById('qTtsBtn');
  if (!btn) return;
  btn.textContent = playing ? '⏸' : '▶';
  btn.classList.toggle('playing', playing);
}

function setRate(r, el) {
  ttsRate = r;
  document.querySelectorAll('.spd-btn').forEach(b => {
    b.classList.toggle('active', parseFloat(b.dataset.rate) === r);
  });
}

// ════════════════════════════════════════════
//  SOUND
// ════════════════════════════════════════════
function playSound(type) {
  if (!soundOn) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (type === 'correct') {
      const freqs = feedbackStyle === 'strong'
        ? [523.25, 659.25, 783.99, 1046.5]
        : [523.25, 659.25, 783.99];
      freqs.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.11);
        gain.gain.setValueAtTime(feedbackStyle === 'strong' ? 0.4 : 0.3, ctx.currentTime + i * 0.11);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.11 + 1.0);
        osc.start(ctx.currentTime + i * 0.11);
        osc.stop(ctx.currentTime + i * 0.11 + 1.0);
      });
    } else {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(200, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.35);
      gain.gain.setValueAtTime(feedbackStyle === 'strong' ? 0.35 : 0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.4);
    }
  } catch(e) {}
}

// ════════════════════════════════════════════
//  SETTINGS
// ════════════════════════════════════════════
function loadSettings() {
  // Account info
  document.getElementById('settEmail').textContent = user?.email || '–';
  const badges = document.getElementById('settBadges');
  badges.innerHTML = '';
  if (user?.is_premium) badges.innerHTML += '<span class="premium-badge">⭐ Premium</span>';
  if (user?.is_admin) badges.innerHTML += '<span class="admin-badge">🔧 Admin</span>';

  // Language
  ['TH','NO','EN'].forEach(l => {
    const btn = document.getElementById('lang' + l);
    if (btn) btn.classList.toggle('active', appLang === l.toLowerCase());
  });

  // Sound toggle
  document.getElementById('soundToggle').checked = soundOn;

  // Theme
  const savedTheme = localStorage.getItem('t2d_theme') || 'dark';
  document.querySelectorAll('#screenSettings .seg-btn').forEach(b => {});
  ['light','dark','sys'].forEach(t => {
    const btn = document.getElementById('themeBtn' + t.charAt(0).toUpperCase() + t.slice(1));
    if (btn) btn.classList.toggle('active', savedTheme === t || (t === 'sys' && savedTheme === 'system'));
  });
}

function setLang(lang) {
  appLang = lang;
  localStorage.setItem('t2d_lang', lang);
  ['TH','NO','EN'].forEach(l => {
    const btn = document.getElementById('lang' + l);
    if (btn) btn.classList.toggle('active', lang === l.toLowerCase());
  });
  toast('Språk oppdatert');
}

function toggleSound(el) {
  soundOn = el.checked;
  localStorage.setItem('t2d_sound', soundOn ? 'on' : 'off');
  applySoundToggle();
}

function applySoundToggle() {
  const toggle = document.getElementById('soundToggle');
  if (toggle) toggle.checked = soundOn;
}

function setFeedback(style, btn) {
  feedbackStyle = style;
  localStorage.setItem('t2d_feedback', style);
  btn.closest('.seg-ctrl').querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

function setTheme(theme, btn) {
  if (btn) {
    btn.closest('.seg-ctrl').querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
  localStorage.setItem('t2d_theme', theme);
  applyTheme(theme);
}

function applyThemeFromStorage() {
  applyTheme(localStorage.getItem('t2d_theme') || 'dark');
}

function applyTheme(theme) {
  if (theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
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
//  KEYBOARD SHORTCUTS
// ════════════════════════════════════════════
document.addEventListener('keydown', e => {
  const active = document.querySelector('.screen.active');
  if (!active) return;
  const id = active.id;

  if (id === 'screenAuth') {
    if (e.key === 'Enter') {
      const loginForm = document.getElementById('formLogin');
      const regForm = document.getElementById('formRegister');
      const forgotForm = document.getElementById('formForgot');
      if (loginForm.style.display !== 'none') doLogin();
      else if (regForm.style.display !== 'none') doRegister();
      else if (forgotForm.style.display !== 'none') doForgot();
    }
  }

  if (id === 'screenQuiz' && qAnswered) {
    if (e.key === 'Enter' || e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault();
      nextQ();
    }
  }

  if (id === 'screenQuiz' && !qAnswered) {
    const letters = ['a','b','c','d','1','2','3','4'];
    const idx = letters.indexOf(e.key.toLowerCase());
    if (idx >= 0) {
      const real = idx > 3 ? idx - 4 : idx;
      const btns = document.querySelectorAll('.ans-btn');
      if (btns[real]) btns[real].click();
    }
  }
});

// System theme watcher
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if (localStorage.getItem('t2d_theme') === 'system') applyTheme('system');
});
</script>
</body>
</html>"""


@webapp_router.get("/web", response_class=HTMLResponse)
async def web_app():
    return HTMLResponse(content=WEBAPP_HTML)
