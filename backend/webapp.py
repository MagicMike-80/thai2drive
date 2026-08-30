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
<html lang="th" data-theme="dark" translate="no" class="notranslate">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google" content="notranslate">
<meta id="metaDescription" name="description" content="ฝึกข้อสอบทฤษฎีใบขับขี่นอร์เวย์ด้วยภาษาไทย นอร์เวย์ และอังกฤษกับ Thai2Drive">
<link rel="icon" href="/api/assets/favicon.ico" sizes="any">
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
    border-left: 2px solid transparent;
    border-right: 2px solid transparent;
    background: linear-gradient(var(--bg), var(--bg)) padding-box,
                conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box;
    animation: neonFlow 5s linear infinite;
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
  display:flex; align-items:center;
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
  height: calc(var(--bottom-h) + 12px); flex-shrink: 0;
  background: rgba(7, 12, 26, 0.92);
  backdrop-filter: blur(32px) saturate(1.8); -webkit-backdrop-filter: blur(32px) saturate(1.8);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 -1px 0 rgba(255, 255, 255, 0.03), 0 -12px 36px rgba(0, 0, 0, 0.35);
  display: none; align-items: center; z-index: 50;
  overflow-x: auto; overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  scroll-snap-type: x mandatory;
  padding: 0 8px;
  gap: 8px;
}
#bottomNav::-webkit-scrollbar { display: none; }
[data-theme="light"] #bottomNav {
  background: rgba(241, 245, 249, 0.94);
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.08);
}
.bn-tab {
  flex: 0 0 calc(33.333% - 11px);
  height: calc(100% - 16px);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: rgba(255, 255, 255, 0.02);
  color: var(--muted);
  cursor: pointer; font-size: 0.68rem; font-weight: 700;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 6px 4px; letter-spacing: 0.2px;
  scroll-snap-align: center;
  border-radius: 14px;
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.03), 0 2px 4px rgba(0,0,0,0.15);
}
[data-theme="light"] .bn-tab {
  border: 1px solid rgba(0, 0, 0, 0.03);
  background: rgba(0, 0, 0, 0.01);
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.8), 0 2px 4px rgba(0,0,0,0.04);
}
.bn-icon {
  font-size: 24px; line-height: 1;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), filter 0.25s;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.5)) contrast(1.15) saturate(1.25);
  display: inline-block;
}
.bn-tab.active {
  color: #00F5FF;
  border: 1.5px solid transparent !important;
  background: linear-gradient(rgba(11, 18, 38, 0.90), rgba(11, 18, 38, 0.90)) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation: neonFlow 4s linear infinite;
  box-shadow: 0 0 14px rgba(0, 245, 255, 0.22), inset 0 1px 2px rgba(255,255,255,0.08);
  transform: translateY(-2px);
}
[data-theme="light"] .bn-tab.active {
  color: var(--orange);
  background: linear-gradient(#FFFFFF, #FFFFFF) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #FF9933, #FF00E5, #00F5FF, #FF9933) border-box !important;
  box-shadow: 0 0 14px rgba(255, 153, 51, 0.22), inset 0 1px 2px rgba(255,255,255,0.9);
}
.bn-tab.active .bn-icon {
  transform: scale(1.2) translateY(-1px);
  filter: drop-shadow(0 0 6px rgba(0, 245, 255, 0.6)) drop-shadow(0 2px 4px rgba(0,0,0,0.6)) contrast(1.3) saturate(1.5);
}
[data-theme="light"] .bn-tab.active .bn-icon {
  filter: drop-shadow(0 0 6px rgba(255, 153, 51, 0.6)) drop-shadow(0 2px 4px rgba(0,0,0,0.3)) contrast(1.3) saturate(1.5);
}
.bn-tab:active .bn-icon { transform: scale(0.85); }

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
  /* Knapp-reset: flaggene er ekte språkknapper, men skal se ut som før */
  padding:0; border:none; background:transparent; cursor:pointer;
  transition:box-shadow .15s ease, opacity .15s ease;
  opacity:.6;
}
.auth-flag.active { opacity:1; box-shadow:0 0 0 2px var(--orange); }
.auth-flag:hover:not(.active) { opacity:.85; }
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
  border:2px solid transparent !important;
  background:linear-gradient(135deg,#FF9933,#e6891f) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation:neonFlow 3s linear infinite;
  color:#0F172A; font-weight:900; font-size:1rem;
  border-radius:14px; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:10px;
  box-shadow:0 6px 24px rgba(255,153,51,.4);
  transition:transform .15s, box-shadow .15s;
}
.home-cta:hover { transform:translateY(-2px); box-shadow:0 0 24px rgba(0,245,255,.5), 0 0 8px rgba(255,153,51,.4); }
.home-cta:active { transform:translateY(0) scale(0.97); box-shadow:0 0 32px rgba(0,245,255,.7), 0 0 12px rgba(255,153,51,.6); }

.home-main-label { font-size:.72rem; font-weight:800; letter-spacing:.09em; text-transform:uppercase; color:var(--muted); }
.home-main-actions { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.home-main-choice {
  min-height:92px; padding:13px; border-radius:16px; cursor:pointer; text-align:left;
  color:var(--text); border:1.5px solid rgba(0,245,255,.24);
  background:linear-gradient(145deg,rgba(17,32,64,.94),rgba(11,18,38,.98));
  display:flex; align-items:center; gap:11px; transition:transform .15s,box-shadow .2s,border-color .2s;
}
.home-main-choice:hover { transform:translateY(-2px); border-color:rgba(0,245,255,.55); box-shadow:0 0 18px rgba(0,245,255,.18); }
.home-main-choice-icon { font-size:1.65rem; flex:0 0 auto; }
.home-main-choice-icon.michael-photo {
  width:48px; height:48px; border-radius:50%; object-fit:cover; object-position:center 15%;
  border:2px solid rgba(0,245,255,.65); box-shadow:0 0 14px rgba(214,0,255,.28);
}
.home-main-choice-copy { display:flex; flex-direction:column; gap:3px; min-width:0; }
.home-main-choice-title { font-size:.86rem; font-weight:900; line-height:1.25; }
.home-main-choice-sub { font-size:.7rem; color:var(--muted); line-height:1.35; }
.target-practice-menu { display:none; grid-column:1/-1; grid-template-columns:1fr 1fr; gap:8px; }
.target-practice-menu.open { display:grid; }
.target-practice-option { padding:11px 9px; border-radius:12px; border:1px solid rgba(255,153,51,.28); background:rgba(255,153,51,.08); color:var(--text); font-size:.78rem; font-weight:800; cursor:pointer; }
@media (max-width:420px) { .home-main-actions { grid-template-columns:1fr; } .target-practice-menu { grid-column:1; } }

.home-sec-btns {
  display:grid; grid-template-columns:1fr 1fr;
  gap:9px;
}
.home-sec-btn {
  padding:13px 10px;
  border:1.5px solid transparent !important;
  background:linear-gradient(rgba(255,255,255,.05), rgba(255,255,255,.05)) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation:neonFlow 4s linear infinite;
  backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px);
  border-radius:14px; color:var(--text); font-weight:700;
  font-size:.85rem; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:6px;
  box-shadow:0 0 8px rgba(0, 245, 255, 0.1);
  transition:border-color .2s, background .2s, box-shadow 0.3s, transform 0.1s;
}
.home-sec-btn:hover {
  background:linear-gradient(rgba(255,255,255,.08), rgba(255,255,255,.08)) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  box-shadow:0 0 16px rgba(0, 245, 255, 0.3);
}
.home-sec-btn:active {
  transform: scale(0.97);
  box-shadow: 0 0 22px rgba(0, 245, 255, 0.5);
}

/* ══════════════════════════════════════════
   HOME SCROLL MENU — Horisontal rullende meny
   Teoriapp dark-mode: dyp blå + lys oransje neon
   Ingen aggressiv rotasjon — ro for kveldsøving
══════════════════════════════════════════ */
.hsm-container {
  position: relative;
  margin: 0 -16px 20px;
}
.hsm-fade-left,
.hsm-fade-right {
  position: absolute;
  top: 0; bottom: 0;
  width: 28px;
  pointer-events: none;
  z-index: 2;
}
.hsm-fade-left  { left: 0;  background: linear-gradient(to right, var(--bg), transparent); }
.hsm-fade-right { right: 0; background: linear-gradient(to left,  var(--bg), transparent); }
.home-scroll-menu {
  display: flex;
  flex-direction: row;
  gap: 10px;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x proximity;
  scrollbar-width: none;
  padding: 6px 16px 14px;
}
.home-scroll-menu::-webkit-scrollbar { display: none; }
.hsm-card {
  flex: 0 0 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 8px;
  border-radius: 16px;
  background: rgba(5, 14, 38, 0.88);
  border: 1.5px solid rgba(0, 82, 255, 0.2);
  box-shadow: 0 0 8px rgba(0, 82, 255, 0.06), inset 0 1px 0 rgba(255,255,255,0.04);
  cursor: pointer;
  scroll-snap-align: start;
  transition: border-color 0.28s ease, box-shadow 0.28s ease, transform 0.15s ease, background 0.28s ease;
}
.hsm-card:hover {
  border-color: rgba(255, 127, 0, 0.55);
  box-shadow: 0 0 16px rgba(255, 127, 0, 0.25), 0 0 6px rgba(255, 127, 0, 0.12), inset 0 1px 0 rgba(255,255,255,0.07);
  background: rgba(10, 21, 54, 0.92);
  transform: translateY(-2px);
}
.hsm-card:active {
  transform: translateY(0) scale(0.95);
  box-shadow: 0 0 10px rgba(255, 127, 0, 0.45);
}
.hsm-icon {
  font-size: 1.45rem;
  line-height: 1;
  filter: drop-shadow(0 0 5px rgba(0, 100, 255, 0.4));
  transition: filter 0.28s ease;
}
.hsm-card:hover .hsm-icon {
  filter: drop-shadow(0 0 8px rgba(255, 140, 0, 0.65));
}
.hsm-label {
  font-size: 0.64rem;
  font-weight: 700;
  text-align: center;
  color: #7A90B8;
  letter-spacing: 0.15px;
  line-height: 1.25;
  transition: color 0.28s ease;
  word-break: keep-all;
  hyphens: none;
}
.hsm-card:hover .hsm-label { color: #FF9933; }
.readiness-meter { height:7px; margin-top:7px; border-radius:999px; overflow:hidden; background:rgba(255,255,255,.08); }
.readiness-meter-fill { height:100%; width:0; border-radius:inherit; transition:width .45s ease; }

/* Michael quiz coach: non-blocking bottom sheet after a wrong answer. */
.michael-quiz-coach {
  position:fixed; left:50%; bottom:18px; z-index:2500;
  width:min(560px, calc(100vw - 24px)); max-height:min(62vh, 520px); overflow:auto;
  transform:translate(-50%, calc(100% + 40px)); opacity:0; pointer-events:none;
  border:1px solid rgba(0,245,255,.28); border-radius:20px;
  background:linear-gradient(155deg, rgba(7,19,45,.98), rgba(10,13,35,.98));
  box-shadow:0 0 34px rgba(0,245,255,.18), 0 18px 50px rgba(0,0,0,.48);
  transition:transform .25s ease, opacity .2s ease;
}
.michael-quiz-coach.open { transform:translate(-50%, 0); opacity:1; pointer-events:auto; }
.mqc-head { display:flex; align-items:center; gap:10px; padding:14px 16px; border-bottom:1px solid rgba(255,255,255,.08); }
.mqc-avatar { width:38px; height:38px; border-radius:50%; object-fit:cover; }
.mqc-title { flex:1; font-weight:850; color:var(--text); }
.mqc-close { border:0; background:transparent; color:var(--muted); font-size:1.25rem; cursor:pointer; }
.mqc-body { padding:15px 17px; color:var(--text); line-height:1.65; font-size:.88rem; white-space:pre-wrap; }
.mqc-action { display:none; width:calc(100% - 34px); margin:0 17px 17px; padding:11px 14px; border-radius:12px; border:1px solid rgba(255,153,51,.35); background:rgba(255,153,51,.12); color:var(--orange); font-weight:800; cursor:pointer; }
.mqc-action.show { display:block; }
.hsm-exam-timer {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.82rem; font-weight: 700; letter-spacing: 2px;
  color: #FF3B3B;
  background: #1a0000;
  border: 1.5px solid #FF3B3B;
  border-radius: 5px;
  padding: 3px 5px;
  text-shadow: 0 0 8px rgba(255,59,59,0.9), 0 0 16px rgba(255,59,59,0.5);
  box-shadow: 0 0 8px rgba(255,59,59,0.35), inset 0 0 6px rgba(255,0,0,0.1);
  animation: exam-glow 1.2s ease-in-out infinite alternate;
  display: inline-block; line-height: 1;
}
@keyframes exam-glow {
  from { box-shadow: 0 0 4px rgba(255,59,59,0.25), inset 0 0 4px rgba(255,0,0,0.05); }
  to   { box-shadow: 0 0 14px rgba(255,59,59,0.7), inset 0 0 8px rgba(255,0,0,0.15); }
}
[data-theme="light"] .hsm-card {
  background: rgba(255,255,255,0.88);
  border-color: rgba(0, 82, 255, 0.12);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-theme="light"] .hsm-card:hover {
  border-color: rgba(217,119,6,0.45);
  background: rgba(255,255,255,0.96);
  box-shadow: 0 0 14px rgba(217,119,6,0.18);
}
[data-theme="light"] .hsm-label { color: #64748B; }
[data-theme="light"] .hsm-card:hover .hsm-label { color: #D97706; }
[data-theme="light"] .hsm-fade-left  { background: linear-gradient(to right, var(--bg), transparent); }
[data-theme="light"] .hsm-fade-right { background: linear-gradient(to left,  var(--bg), transparent); }

/* Stats — one unified card, three columns with vertical dividers */
.home-stats {
  display:grid; grid-template-columns:repeat(3,1fr);
  gap:0;
  border:1.5px solid transparent !important;
  background:linear-gradient(rgba(255,255,255,.05), rgba(255,255,255,.05)) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation:neonFlow 5s linear infinite;
  border-radius:16px; overflow:hidden;
  box-shadow:0 0 8px rgba(0, 245, 255, 0.08);
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
/* ═══ 3D CYLINDER CAROUSEL ═══
   Categories arranged along a horizontal 3D cylinder.
   Active item center, adjacent curve backward into space. */
.carousel-3d-header {
  padding:14px 16px 10px; flex-shrink:0;
  background:transparent;
}
.screen-title {
  font-size:1.6rem; font-weight:900; letter-spacing:-.3px;
}
.screen-title span { color:var(--muted); font-size:.95rem; font-weight:600; margin-left:6px; }
.carousel-3d-scroll {
  flex:1; position:relative; display:flex; align-items:center; justify-content:center;
  overflow:hidden; min-height:0;
}
.carousel-3d-wrap {
  width:100%; height:340px;
  perspective:1000px; perspective-origin:50% 50%;
  display:flex; align-items:center; justify-content:center;
  position:relative; overflow:visible;
  touch-action:pan-y;
  user-select:none; -webkit-user-select:none;
}
.carousel-3d-stage {
  width:220px; height:100%;
  transform-style:preserve-3d;
  position:relative;
  display:flex; align-items:center; justify-content:center;
}
.carousel-3d-item {
  --cat-color:#FF9933;
  --cat-glow:rgba(255,153,51,.45);
  --cat-bg1:rgba(19,27,46,.94);
  --cat-bg2:rgba(11,18,38,.98);
  position:absolute; left:50%; top:50%;
  width:175px; height:220px;
  margin-left:-87.5px; margin-top:-110px;
  border-radius:20px;
  cursor:pointer; backface-visibility:hidden;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  gap:8px; padding:16px 12px;
  background:linear-gradient(160deg, var(--cat-bg1) 0%, var(--cat-bg2) 100%);
  border:1.5px solid rgba(255,255,255,.08);
  box-shadow:0 4px 30px rgba(0,0,0,.3);
  color:var(--text);
  transition:border-color .3s, box-shadow .4s;
  will-change:transform, opacity;
  overflow:hidden;
}
.carousel-3d-item::before {
  content:'';
  position:absolute; inset:0;
  border-radius:20px;
  pointer-events:none;
  opacity:.06;
  background-image:
    linear-gradient(rgba(0,245,255,.6) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,245,255,.6) 1px, transparent 1px),
    radial-gradient(circle 2px at 16px 16px, rgba(0,245,255,.8) 100%, transparent 100%),
    radial-gradient(circle 2px at 48px 48px, rgba(255,0,229,.8) 100%, transparent 100%),
    radial-gradient(circle 1.5px at 80px 24px, rgba(255,215,0,.8) 100%, transparent 100%);
  background-size:32px 32px, 32px 32px, 96px 96px, 96px 96px, 96px 96px;
}
[data-theme="light"] .carousel-3d-item {
  background:linear-gradient(160deg, rgba(255,255,255,.92) 0%, rgba(241,245,249,.96) 100%);
  border-color:rgba(0,0,0,.08);
  box-shadow:0 4px 24px rgba(0,0,0,.06);
}
.carousel-3d-item.active {
  border-color:transparent;
  box-shadow:0 0 28px var(--cat-glow), inset 0 0 14px var(--cat-glow);
}
@property --neon-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}
@keyframes neonFlow {
  to { --neon-angle: 360deg; }
}
@keyframes neonFlowFallback {
  0%   { transform:rotate(0deg); }
  100% { transform:rotate(360deg); }
}
[data-theme="light"] .carousel-3d-item.active {
  box-shadow:0 0 30px rgba(255,153,51,.12), 0 0 60px rgba(255,153,51,.04);
}
.carousel-3d-item:active { transform:scale(.97); }
.carousel-3d-icon {
  width:62px; height:62px; margin-bottom:4px;
  display:flex; align-items:center; justify-content:center;
  color:var(--cat-color);
  filter:drop-shadow(0 2px 10px var(--cat-glow));
  transition:filter .3s, color .3s;
}
.carousel-3d-icon svg { width:100%; height:100%; }
.carousel-3d-item.active .carousel-3d-icon {
  filter:drop-shadow(0 0 14px var(--cat-glow)) drop-shadow(0 0 4px var(--cat-glow));
}
.carousel-3d-label {
  font-weight:800; font-size:1.15rem; line-height:1.3; text-align:center;
  letter-spacing:-.2px;
}
.carousel-3d-count {
  font-size:.85rem; color:var(--muted); font-weight:600;
}
.carousel-3d-active-ring {
  position:absolute; top:50%; left:50%;
  width:179px; height:224px; margin-left:-89.5px; margin-top:-112px;
  border-radius:22px;
  pointer-events:none;
  opacity:0;
  transition:opacity .45s;
  padding:3px;
  background:conic-gradient(from var(--neon-angle, 0deg),
    transparent 0%,
    var(--cat-color, #FF9933) 18%,
    rgba(255,255,255,.95) 24%,
    var(--cat-color, #FF9933) 30%,
    transparent 48%
  );
  -webkit-mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite:xor;
  mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite:exclude;
  animation:neonFlow 2.4s linear infinite;
}
.carousel-3d-active-ring.visible {
  opacity:1;
  filter:drop-shadow(0 0 6px var(--cat-color, #FF9933)) drop-shadow(0 0 14px var(--cat-glow, rgba(255,153,51,.5)));
}

/* ── Carousel dots ── */
.carousel-3d-dots {
  position:absolute; bottom:12px; left:0; right:0;
  display:flex; justify-content:center; gap:6px; padding:0 16px;
  pointer-events:none; z-index:2;
}
.carousel-3d-dot {
  width:6px; height:6px; border-radius:50%;
  background:rgba(255,255,255,.18);
  transition:all .35s;
}
[data-theme="light"] .carousel-3d-dot { background:rgba(0,0,0,.14); }
.carousel-3d-dot.active { width:20px; border-radius:3px; background:var(--orange); }
.carousel-3d-dot.adjacent { width:8px; border-radius:4px; background:rgba(255,255,255,.30); }
[data-theme="light"] .carousel-3d-dot.adjacent { background:rgba(0,0,0,.24); }

/* ── Edge gradient fade (left/right vignette) ── */
.carousel-3d-fade-left,
.carousel-3d-fade-right {
  position:absolute; top:0; bottom:0; width:50px;
  pointer-events:none; z-index:3;
}
.carousel-3d-fade-left {
  left:0;
  background:linear-gradient(90deg, var(--bg) 0%, transparent 100%);
}
.carousel-3d-fade-right {
  right:0;
  background:linear-gradient(270deg, var(--bg) 0%, transparent 100%);
}

/* ── Swipe hint ── */
.carousel-3d-hint {
  position:absolute; bottom:40px; left:50%; transform:translateX(-50%);
  font-size:.75rem; color:rgba(255,255,255,.20); font-weight:500;
  white-space:nowrap; letter-spacing:.5px;
  pointer-events:none; z-index:1;
  transition:opacity 1s;
}
[data-theme="light"] .carousel-3d-hint { color:rgba(0,0,0,.16); }

/* ── Per-category neon color themes ── */
.carousel-3d-item[data-ckey="Speed Limits"],
.carousel-3d-item[data-ckey="fart_og_bremsing"]
  { --cat-color:#FF6A00; --cat-glow:rgba(255,106,0,.50); --cat-bg1:rgba(50,15,0,.95); --cat-bg2:rgba(20,5,0,.99); }
.carousel-3d-item[data-ckey="Road Rules"],
.carousel-3d-item[data-ckey="Trafikkregler"]
  { --cat-color:#FF4500; --cat-glow:rgba(255,69,0,.48); --cat-bg1:rgba(45,10,0,.95); --cat-bg2:rgba(18,4,0,.99); }
.carousel-3d-item[data-ckey="Traffic Signs"]
  { --cat-color:#FFD700; --cat-glow:rgba(255,215,0,.48); --cat-bg1:rgba(40,30,0,.95); --cat-bg2:rgba(15,12,0,.99); }
.carousel-3d-item[data-ckey="Right of Way"]
  { --cat-color:#AAFF00; --cat-glow:rgba(170,255,0,.48); --cat-bg1:rgba(12,32,0,.95); --cat-bg2:rgba(4,14,0,.99); }
.carousel-3d-item[data-ckey="Traffic Rules"]
  { --cat-color:#CC44FF; --cat-glow:rgba(204,68,255,.48); --cat-bg1:rgba(28,5,40,.95); --cat-bg2:rgba(10,0,18,.99); }
.carousel-3d-item[data-ckey="Situations"]
  { --cat-color:#00FF6A; --cat-glow:rgba(0,255,106,.45); --cat-bg1:rgba(0,30,12,.95); --cat-bg2:rgba(0,12,5,.99); }
.carousel-3d-item[data-ckey="Safety"]
  { --cat-color:#00AAFF; --cat-glow:rgba(0,170,255,.48); --cat-bg1:rgba(0,18,40,.95); --cat-bg2:rgba(0,6,18,.99); }
.carousel-3d-item[data-ckey="Driving Conditions"],
.carousel-3d-item[data-ckey="Road Conditions"]
  { --cat-color:#00C8FF; --cat-glow:rgba(0,200,255,.45); --cat-bg1:rgba(0,20,35,.95); --cat-bg2:rgba(0,8,16,.99); }
.carousel-3d-item[data-ckey="Accidents"]
  { --cat-color:#FF1744; --cat-glow:rgba(255,23,68,.50); --cat-bg1:rgba(45,0,8,.95); --cat-bg2:rgba(18,0,3,.99); }
.carousel-3d-item[data-ckey="Alcohol"]
  { --cat-color:#FF3D71; --cat-glow:rgba(255,61,113,.45); --cat-bg1:rgba(40,0,12,.95); --cat-bg2:rgba(16,0,5,.99); }
.carousel-3d-item[data-ckey="Highway"]
  { --cat-color:#00E5FF; --cat-glow:rgba(0,229,255,.45); --cat-bg1:rgba(0,22,32,.95); --cat-bg2:rgba(0,8,14,.99); }
.carousel-3d-item[data-ckey="Intersections"]
  { --cat-color:#FF8C00; --cat-glow:rgba(255,140,0,.48); --cat-bg1:rgba(42,18,0,.95); --cat-bg2:rgba(16,6,0,.99); }
.carousel-3d-item[data-ckey="Parking"]
  { --cat-color:#00E5FF; --cat-glow:rgba(0,229,255,.42); --cat-bg1:rgba(0,20,30,.95); --cat-bg2:rgba(0,7,12,.99); }
.carousel-3d-item[data-ckey="Vehicle"]
  { --cat-color:#4FC3F7; --cat-glow:rgba(79,195,247,.42); --cat-bg1:rgba(0,18,30,.95); --cat-bg2:rgba(0,6,14,.99); }
.carousel-3d-item[data-ckey="Lights"]
  { --cat-color:#FFE033; --cat-glow:rgba(255,224,51,.45); --cat-bg1:rgba(38,28,0,.95); --cat-bg2:rgba(14,10,0,.99); }
.carousel-3d-item[data-ckey="Tires"]
  { --cat-color:#B0C4DE; --cat-glow:rgba(176,196,222,.38); --cat-bg1:rgba(12,16,22,.95); --cat-bg2:rgba(4,6,10,.99); }
.carousel-3d-item[data-ckey="Overtaking"]
  { --cat-color:#00FF80; --cat-glow:rgba(0,255,128,.45); --cat-bg1:rgba(0,28,14,.95); --cat-bg2:rgba(0,10,5,.99); }
.carousel-3d-item[data-ckey="Pedestrians"]
  { --cat-color:#FF9800; --cat-glow:rgba(255,152,0,.48); --cat-bg1:rgba(40,20,0,.95); --cat-bg2:rgba(16,7,0,.99); }
.carousel-3d-item[data-ckey="Environment"]
  { --cat-color:#00E676; --cat-glow:rgba(0,230,118,.45); --cat-bg1:rgba(0,26,14,.95); --cat-bg2:rgba(0,10,5,.99); }
.carousel-3d-item[data-ckey="Hazardous Goods"]
  { --cat-color:#FF6D00; --cat-glow:rgba(255,109,0,.50); --cat-bg1:rgba(40,14,0,.95); --cat-bg2:rgba(16,5,0,.99); }

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
  aspect-ratio:16/9;
  transition:outline .3s ease, box-shadow .3s ease;
}
.q-img { width:100%; height:100%; object-fit:cover; display:block; }

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

  /* Forbikjøring frame — wide layout, calculator left + image right */
  #app.fk-mode {
    width: min(1080px, 96vw);
    max-width: none;
    margin-left: auto;
    margin-right: auto;
    border-radius: 16px;
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
  /* Clear separator so image bottom doesn't bleed into AI panel */
  border-bottom:1px solid rgba(255,255,255,.10);
}
.quiz-ai-imgbox.glow-ok  { box-shadow:inset 0 0 0 1px rgba(16,185,129,.22); }
.quiz-ai-imgbox.glow-bad { box-shadow:inset 0 0 0 1px rgba(251,146,60,.22); }

.quiz-ai-img {
  width:100%; display:block;
  height:auto; max-height:320px; object-fit:contain; object-position:center;
}
.quiz-ai-img.flash-ok, .quiz-ai-img.flash-bad { /* image stays neutral — feedback lives in UI, not the road scene */ }

/* Overlay — transparent: no dark gradient that merges image with AI panel below */
.quiz-ai-img-overlay {
  position:absolute; inset:0; pointer-events:none;
  background:transparent;
  transition:background .45s ease;
}
.quiz-ai-img-overlay.result-ok  { background:transparent; }
.quiz-ai-img-overlay.result-bad { background:transparent; }

.quiz-ai-img-badge {
  position:absolute; top:10px; left:12px;
  font-size:.60rem; font-weight:800; letter-spacing:.7px; text-transform:uppercase;
  color:rgba(255,255,255,.55); pointer-events:none;
  display:flex; align-items:center; gap:5px;
  background:rgba(0,0,0,.38); padding:3px 8px; border-radius:20px;
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
.vid-card-thumb {
  width:100%; height:100px; border-radius:8px; overflow:hidden;
  background:rgba(255,255,255,.06); background-size:cover; background-position:center;
  display:flex; align-items:center; justify-content:center; cursor:pointer;
  position:relative;
}
.vid-card-thumb .vid-card-play {
  width:40px; height:40px; border-radius:50%;
  background:rgba(0,240,255,0.8); color:#000;
  display:flex; align-items:center; justify-content:center;
  font-size:1rem; box-shadow:0 0 15px rgba(0,240,255,0.5);
  transition:transform .2s;
}
.vid-card-thumb:hover .vid-card-play { transform:scale(1.1); }
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
.vid-card-local {
  display:flex; flex-direction:column; gap:8px;
  padding:12px; border-radius:11px;
  background:rgba(255,255,255,.03);
  border:1px solid rgba(255,255,255,.08);
  transition:border-color .18s; cursor:pointer;
}
.vid-card-local:hover { border-color:rgba(255,153,51,.30); }
.vid-player {
  width:100%; border-radius:6px; outline:none;
  max-height:220px; background:#000;
}
/* Wrapper — adds section label above the card */
.vid-section  { display:flex; flex-direction:column; gap:6px; }
.vid-sec-lbl  {
  font-size:.57rem; font-weight:900; text-transform:uppercase;
  letter-spacing:.8px; color:var(--muted);
}

.podcast-card {
  display:flex; flex-direction:column; gap:8px;
  padding:12px; border-radius:11px;
  background:rgba(255,255,255,.03);
  border:1px solid rgba(255,255,255,.08);
  margin-top:10px; width:100%;
}
.podcast-info { flex:1; min-width:0; }
.podcast-lbl {
  font-size:.65rem; font-weight:900; text-transform:uppercase;
  letter-spacing:.7px; color:var(--orange); margin-bottom:3px;
}
.podcast-title {
  font-size:.82rem; font-weight:700; color:var(--text); line-height:1.38;
}
.podcast-dur {
  font-size:.63rem; color:var(--muted); margin-top:2px;
}
.podcast-player {
  width:100%; height:32px; border-radius:6px; outline:none;
}
.tm-bubble-tts {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
  padding: 4px 8px;
  margin-top: 6px;
  opacity: 0.5;
  transition: opacity 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  align-self: flex-end;
}
.tm-bubble-tts:hover {
  opacity: 0.95;
  transform: scale(1.1);
}
.tm-bubble-tts:active {
  transform: scale(0.95);
}

/* ══════════════════════════════════════════
   LIBRARY SCREEN
══════════════════════════════════════════ */
#screenLibrary { padding:0; background:#0B1226; flex-direction:column; }
.lib-header {
  padding:14px 16px 10px; flex-shrink:0;
  display:flex; align-items:center; gap:10px;
}
.lib-back-btn {
  background: none; border: 1.5px solid rgba(0,82,255,0.22);
  border-radius: 10px; color: #7A90B8;
  font-size: 1rem; line-height:1;
  padding: 6px 10px; cursor: pointer;
  transition: border-color .2s, color .2s, background .2s;
  flex-shrink: 0;
}
.lib-back-btn:hover {
  border-color: rgba(255,127,0,0.55);
  color: #FF9933;
  background: rgba(255,127,0,0.07);
}
.lib-tabs {
  display: flex; gap: 8px; margin: 0 16px 16px;
  background: var(--panel); padding: 4px; border-radius: 10px;
  flex-shrink: 0;
}
.lib-tab {
  flex: 1; padding: 10px; border-radius: 8px; border: 0;
  background: none; color: var(--muted); font-size: .85rem;
  font-weight: 700; cursor: pointer; transition: all .15s;
}
.lib-tab.active {
  background: var(--accent); color: #fff;
  box-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
}
.lib-scroll {
  flex: 1; overflow-y: auto; padding: 0 16px 16px;
  -webkit-overflow-scrolling: touch;
}
.lib-scroll::-webkit-scrollbar { width:4px; }
.micro-intro { margin-bottom:12px; color:var(--muted); font-size:.82rem; line-height:1.5; }
.micro-lessons { display:flex; flex-direction:column; gap:10px; }
.micro-lesson { border:1px solid rgba(0,245,255,.18); border-radius:15px; overflow:hidden; background:linear-gradient(145deg,rgba(17,32,64,.9),rgba(11,18,38,.96)); }
.micro-lesson-btn { width:100%; padding:14px; border:0; background:transparent; color:var(--text); cursor:pointer; display:flex; align-items:center; gap:12px; text-align:left; }
.micro-lesson-icon { width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex:0 0 auto; background:rgba(0,245,255,.09); font-size:1.35rem; }
.micro-lesson-title { flex:1; font-size:.88rem; font-weight:850; line-height:1.35; }
.micro-lesson-chevron { color:var(--cyan); transition:transform .2s; }
.micro-lesson.open .micro-lesson-chevron { transform:rotate(180deg); }
.micro-lesson-body { display:none; padding:0 14px 15px 68px; color:var(--muted); font-size:.8rem; line-height:1.55; }
.micro-lesson.open .micro-lesson-body { display:block; }
.micro-lesson-action { margin-top:8px; color:var(--orange); font-weight:750; }
.lib-scroll::-webkit-scrollbar-track { background:transparent; }
.lib-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.12); border-radius:2px; }
.library-grid {
  display: grid; grid-template-columns: 1fr; gap: 12px;
}
.library-list {
  display: flex; flex-direction: column; gap: 10px;
}

/* ══════════════════════════════════════════
   VIDEO PLAYER — The Road Ahead
══════════════════════════════════════════ */
#screenVideoPlayer { padding:0; background:#0B1226; flex-direction:column; }
.vp-header {
  padding:10px 14px; flex-shrink:0;
  display:flex; align-items:center; gap:10px;
}
.vp-back-btn {
  background: none; border:1.5px solid rgba(0,82,255,0.22);
  border-radius:10px; color:#7A90B8;
  font-size:1rem; line-height:1;
  padding:6px 10px; cursor:pointer; flex-shrink:0;
}
.vp-back-btn:hover {
  border-color:rgba(255,127,0,0.55);
  color:#FF9933; background:rgba(255,127,0,0.07);
}
.vp-title {
  flex:1; font-size:.95rem; font-weight:600;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  color:#e0e8f0;
}
.vp-player-wrap {
  flex-shrink:0; width:100%;
  background:#000; position:relative;
}
.vp-player-wrap video {
  width:100%; display:block; max-height:60vh;
}
.vp-scroll {
  flex:1; overflow-y:auto; padding:0 14px 16px;
  -webkit-overflow-scrolling:touch;
}
/* Glow Road */
.vp-glow-road {
  flex-shrink:0; padding:10px 14px 6px;
  display:flex; align-items:center; gap:2px;
  background:rgba(0,0,0,0.3);
}
.vp-glow-track {
  flex:1; height:3px; background:rgba(255,255,255,0.1);
  border-radius:2px; position:relative; display:flex; align-items:center;
}
.vp-glow-dot {
  flex:1; height:8px; width:8px; border-radius:50%;
  background:rgba(255,255,255,0.15); cursor:pointer;
  transition:all .3s; position:relative; z-index:1;
  margin:0 -1px;
}
.vp-glow-dot.active {
  background:#00f0ff; box-shadow:0 0 12px rgba(0,240,255,0.7);
  transform:scale(1.3);
}
.vp-glow-dot.passed {
  background:rgba(0,240,255,0.5);
}
.vp-glow-label {
  font-size:.6rem; color:rgba(255,255,255,0.4);
  text-align:center; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis; max-width:50px;
}
.vp-glow-dot-wrap {
  display:flex; flex-direction:column; align-items:center;
  flex:1; min-width:0;
}
/* Knowledge Cards */
.vp-knowledge-area {
  padding:12px 0; display:flex; flex-direction:column; gap:10px;
}
.vp-knowledge-card {
  background:rgba(0,240,255,0.06); border:1px solid rgba(0,240,255,0.2);
  border-radius:12px; padding:14px; animation:kcIn .4s ease;
  transition:opacity .5s, transform .5s;
}
.vp-knowledge-card.fading {
  opacity:0; transform:translateY(-10px);
}
@keyframes kcIn {
  from { opacity:0; transform:translateY(10px); }
  to { opacity:1; transform:translateY(0); }
}
.vp-kc-title {
  font-size:.85rem; font-weight:600; color:#00f0ff; margin-bottom:6px;
}
.vp-kc-body {
  font-size:.8rem; color:#b0c0d8; line-height:1.5;
}
.vp-kc-img {
  max-width:100%; max-height:120px; border-radius:6px;
  margin-top:8px; object-fit:contain;
}
/* Mini Check */
.vp-mini-check {
  padding:12px 0; text-align:center;
}
.vp-mc-question {
  font-size:.9rem; font-weight:600; margin-bottom:12px;
  color:#e0e8f0;
}
.vp-mc-options {
  display:flex; gap:10px; justify-content:center;
}
.vp-mc-btn {
  padding:10px 24px; border-radius:10px; border:1.5px solid rgba(255,255,255,0.15);
  background:rgba(255,255,255,0.05); color:#d0d8e8;
  font-size:.85rem; cursor:pointer; transition:all .2s;
}
.vp-mc-btn:hover {
  border-color:rgba(0,240,255,0.4); background:rgba(0,240,255,0.08);
}
.vp-mc-btn.correct {
  border-color:#00ff88; background:rgba(0,255,136,0.1); color:#00ff88;
}
.vp-mc-btn.wrong {
  border-color:#ff4466; background:rgba(255,68,102,0.1); color:#ff4466;
}
.vp-mc-result {
  margin-top:10px; font-size:.8rem; animation:kcIn .3s ease;
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
/* TTS button inside the AI inline card */
.sp-ai-tts-btn {
  display:inline-flex; align-items:center; gap:5px;
  margin-top:10px; padding:7px 14px; border-radius:20px;
  background:rgba(255,153,51,.10); color:var(--orange);
  border:1px solid rgba(255,153,51,.28);
  font-size:.75rem; font-weight:700; cursor:pointer;
  transition:background .15s;
}
.sp-ai-tts-btn:hover { background:rgba(255,153,51,.20); }

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
.lang-btn.active{ animation:none; }

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
.sb-video-btn {
  display:inline-flex; align-items:center; gap:8px;
  margin-top:14px; padding:10px 18px;
  background:rgba(220,38,38,.10); border:1px solid rgba(220,38,38,.25);
  border-radius:10px; color:#FCA5A5; font-weight:700; font-size:.875rem;
  text-decoration:none; transition:background .15s;
}
.sb-video-btn:hover { background:rgba(220,38,38,.20); }

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

/* ── Studiebok tool strip ───────────────────────────── */
.sb-tools {
  display:flex; gap:8px; padding:8px 14px 4px;
  flex-shrink:0; flex-wrap:wrap;
}
.sb-tool-btn {
  display:flex; align-items:center; gap:6px;
  background:var(--card); border:1px solid var(--border);
  color:var(--text); border-radius:20px;
  padding:7px 14px; font-size:.8rem; font-weight:700;
  cursor:pointer; transition:background .15s;
}
.sb-tool-btn:hover { background:var(--card2); border-color:var(--orange); }

/* ── Forbikjøring screen ────────────────────────────── */
#screenForbikjoring {
  padding:0; background:var(--bg);
  container-type:inline-size;
}
.fk-topbar {
  display:flex; align-items:center; gap:10px;
  padding:10px 14px 8px; flex-shrink:0;
  border-bottom:1px solid var(--border);
}
.fk-title { font-size:1rem; font-weight:800; flex:1; }
.fk-scenarios {
  display:flex; gap:8px; padding:12px 14px 8px;
  flex-shrink:0;
}
.fk-sc-btn {
  flex:1; padding:9px 6px; border-radius:12px;
  border:2px solid var(--border); background:var(--card);
  color:var(--text); font-size:.82rem; font-weight:700;
  cursor:pointer; transition:background .15s, border-color .15s;
  text-align:center;
}
.fk-sc-btn.active { border-color:var(--orange); background:rgba(255,153,51,.12); }
.fk-sc-btn:hover  { border-color:var(--orange); }

/* Mobile image toggle — hidden everywhere (image always visible on mobile) */
.fk-img-toggle { display:none; }
/* Mobile image panel — always visible on mobile */
.fk-img-mobile {
  flex-shrink:0; padding:0 0 10px;
}
.fk-img-mobile img {
  width:100%; display:block;
  object-fit:cover; object-position:center;
  max-height:260px;
}

/* Two-column layout container */
.fk-layout {
  display:flex; flex-direction:column;
  flex:1; min-height:0; overflow:hidden;
}
/* Left column: calculator */
.fk-calc-col {
  display:flex; flex-direction:column;
  flex:1; min-height:0; min-width:0;
  overflow-y:auto; overflow-x:hidden;
}
.fk-body {
  padding:12px 14px 0;
  display:flex; flex-direction:column; gap:12px;
}
/* Narrow/app-frame layout: keep image stacked and content readable */
@container (max-width:959px) {
  .fk-body       { padding-bottom:calc(72px + env(safe-area-inset-bottom, 0px)); }
  .fk-disclaimer { margin-bottom:calc(72px + env(safe-area-inset-bottom, 0px)); }
  .fk-img-mobile img { max-height:280px; border-radius:0; }
  .fk-info-row   { grid-template-columns:1fr; }
}
/* Right column: hidden on mobile, shown on desktop */
.fk-img-col { display:none; }

@container (min-width:960px) {
  .fk-img-mobile  { display:none !important; }
  .fk-layout      { flex-direction:row; }
  .fk-calc-col    { min-width:420px; }
  .fk-img-col {
    display:flex; flex-direction:column; flex:0 0 46%;
    border-left:1px solid var(--border); overflow:hidden;
    min-height:400px;
  }
  .fk-img-col img {
    width:100%; flex:1;
    object-fit:cover; object-position:center;
    display:block;
  }
}

.fk-info-row {
  display:grid; grid-template-columns:1fr 1fr;
  gap:8px;
}
.fk-info-cell {
  background:var(--card); border-radius:10px;
  padding:10px 12px; font-size:.82rem;
}
.fk-info-cell .fk-val {
  font-size:1.35rem; font-weight:900; color:var(--orange);
  display:block; margin-top:2px;
}
.fk-steps {
  background:var(--card); border-radius:12px;
  padding:12px 14px; font-size:.83rem; line-height:1.7;
}
.fk-steps-hdr {
  font-size:.72rem; font-weight:900; letter-spacing:.06em;
  text-transform:uppercase; color:var(--orange); margin-bottom:8px;
}
.fk-step { display:flex; justify-content:space-between; gap:8px; }
.fk-step-lbl { color:var(--muted); }
.fk-step-val { font-weight:800; text-align:right; }
.fk-step-val.blue  { color:#60A5FA; }
.fk-step-val.yel   { color:#F59E0B; }
.fk-step-val.red   { color:#F87171; }
.fk-step-val.grn   { color:#34D399; }
.fk-bar-wrap {
  background:var(--card); border-radius:12px; padding:12px 14px;
}
.fk-bar-hdr {
  font-size:.72rem; font-weight:900; letter-spacing:.06em;
  text-transform:uppercase; color:var(--muted); margin-bottom:8px;
}
.fk-bar {
  display:flex; height:28px; border-radius:8px;
  overflow:hidden; width:100%;
}
.fk-bar-seg {
  display:flex; align-items:center; justify-content:center;
  font-size:.65rem; font-weight:800; color:#fff;
  min-width:0; overflow:hidden; white-space:nowrap;
  transition:width .4s ease;
}
.fk-bar-seg.blue { background:#3B82F6; }
.fk-bar-seg.yel  { background:#F59E0B; }
.fk-bar-seg.red  { background:#EF4444; }
.fk-bar-seg.grn  { background:#10B981; }
.fk-bar-overflow { /* shown when unsafe — red danger stripe */
  margin-top:4px; font-size:.72rem; color:#F87171; font-weight:700;
  text-align:right;
}
.fk-result {
  border-radius:12px; padding:14px 16px;
  font-size:.9rem; font-weight:800; text-align:center;
}
.fk-result.safe   { background:rgba(16,185,129,.15); color:#34D399; border:1px solid #34D399; }
.fk-result.warn   { background:rgba(245,158,11,.12); color:#F59E0B; border:1px solid #F59E0B; }
.fk-result.danger { background:rgba(239,68,68,.13);  color:#F87171; border:1px solid #F87171; }
.fk-disclaimer {
  font-size:.73rem; color:var(--muted); line-height:1.5;
  padding:10px 14px 4px; border-top:1px solid var(--border);
  flex-shrink:0;
}
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
  border:1.5px solid transparent !important;
  background:linear-gradient(135deg, rgba(30,58,95,.55) 0%, rgba(37,99,235,.20) 100%) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation:neonFlow 4s linear infinite;
  border-radius:16px; cursor:pointer;
  transition:background .15s, border-color .15s, box-shadow 0.3s;
  margin-bottom:4px;
  box-shadow:0 0 8px rgba(0, 245, 255, 0.1);
}
.michael-card:hover {
  background:linear-gradient(135deg,rgba(30,58,95,.7) 0%,rgba(37,99,235,.30) 100%) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  box-shadow:0 0 16px rgba(0, 245, 255, 0.3);
}
.michael-card-left  { display:flex; align-items:center; gap:12px; }
.michael-card-avatar {
  width:60px; height:60px; border-radius:50%;
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
  display:flex; align-items:center; justify-content:space-between; gap:16px;
  min-height:148px; padding:16px 18px; border-bottom:1px solid rgba(0,245,255,.22);
  background:linear-gradient(135deg,#071326 0%,#101637 62%,#221044 100%);
  flex-shrink:0; overflow:hidden; position:relative;
}
.teacher-avatar {
  width:112px; height:132px; border-radius:24px 24px 14px 14px;
  object-fit:cover; object-position:center 14%; flex-shrink:0;
  border:2px solid rgba(0,245,255,.65);
  box-shadow:0 0 24px rgba(0,245,255,.30),0 0 38px rgba(214,0,255,.20);
}
.teacher-header-info { min-width:0; position:relative; z-index:1; }
.teacher-eyebrow { font-size:.68rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; color:#67E8F9; margin-bottom:5px; }
.teacher-name { font-size:1.08rem; font-weight:900; color:#fff; line-height:1.2; }
.teacher-experience { font-size:.76rem; color:#CBD5E1; margin-top:5px; }
.teacher-status { font-size:.75rem; color:#10B981; margin-top:2px; }

/* Mobile baseline — chat col fills screen, side panel hidden */
.teacher-chat-col {
  display:flex; flex-direction:column;
  flex:1; min-height:0;
}
.teacher-side-panel { display:none; }

.teacher-messages {
  flex:1; min-height:0; overflow-y:auto; padding:16px 14px 80px;
  display:flex; flex-direction:column; gap:14px;
}
.teacher-messages::-webkit-scrollbar { width:0; }

.tm-row { display:flex; align-items:flex-end; gap:8px; min-width:0; width:100%; }
.tm-row.user  { justify-content:flex-end; }
.tm-row.assistant { justify-content:flex-start; }

.tm-av {
  width:28px; height:28px; border-radius:50%;
  background:#1E3A5F; object-fit:cover; object-position:center 15%;
  border:1px solid rgba(0,245,255,.55); flex-shrink:0;
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
  padding:8px 14px 6px; display:flex; flex-direction:row;
  flex-wrap:wrap; gap:7px; flex-shrink:0;
  align-content:flex-start;
}
.teacher-chip {
  display:inline-flex; align-items:center; justify-content:center; gap:6px;
  background:var(--card); border:1px solid var(--border);
  color:var(--text); border-radius:999px;
  padding:8px 12px; min-height:38px; font-size:.78rem; font-weight:700;
  cursor:pointer; text-align:center; transition:background .15s, border-color .15s, transform .12s;
  flex:0 1 auto; max-width:100%;
}
.teacher-chip:hover { background:var(--card2); border-color:rgba(255,153,51,.45); transform:translateY(-1px); }
.teacher-chip-hdr {
  flex:1 0 100%;
  font-size:.64rem; font-weight:900; letter-spacing:.07em;
  text-transform:uppercase; color:var(--orange);
  padding:7px 2px 0; margin-top:1px;
}
.teacher-topics-toggle {
  display:none; width:100%; min-height:48px; border-radius:14px;
  border:1px solid rgba(0,245,255,.35); background:rgba(0,245,255,.08);
  color:#A5F3FC; font:inherit; font-size:.82rem; font-weight:900; cursor:pointer;
}

/* Contextual reply chips — shown after assistant messages */
.tm-chips {
  display:flex; flex-direction:row; flex-wrap:wrap; gap:7px;
  padding:10px 14px 4px 14px;
  border-top:1px solid rgba(255,255,255,.06);
  margin-top:4px;
}
.tm-chips-hdr {
  flex:1 0 100%;
  font-size:.68rem; font-weight:800; letter-spacing:.06em;
  color:var(--orange); text-transform:uppercase;
  margin-bottom:0;
}
.tm-chip-btn {
  display:inline-flex; align-items:center; justify-content:center; gap:7px;
  background:#1a2744; border:1px solid rgba(59,130,246,.28);
  color:#F8FAFC; border-radius:999px;
  padding:8px 12px; min-height:38px; font-size:.78rem; font-weight:800;
  cursor:pointer; text-align:center; width:auto; max-width:100%;
  transition:background .15s, border-color .15s, transform .12s;
}
.tm-chip-btn:hover  { background:#1e3a5f; border-color:rgba(255,153,51,.65); color:#fff; transform:translateY(-1px); }
.tm-chip-btn:active { transform:scale(.97); }
[data-theme="light"] .tm-chip-btn { background:#1e3a5f; border-color:rgba(59,130,246,.35); color:#F8FAFC; }
[data-theme="light"] .tm-chip-btn:hover { background:#1a2744; border-color:rgba(255,153,51,.55); }
.tm-chips-toggle {
  display:none; flex:1 0 100%; min-height:44px; border-radius:12px;
  border:1px solid rgba(0,245,255,.32); background:rgba(0,245,255,.07);
  color:#A5F3FC; font:inherit; font-size:.78rem; font-weight:900; cursor:pointer;
}

.teacher-inputbar {
  display:flex; align-items:flex-end; gap:8px;
  padding:10px 14px calc(10px + env(safe-area-inset-bottom, 0px)) 14px;
  border-top:1px solid var(--border);
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

@media (max-width:767px) {
  #app.teacher-mode .flag-bg { display:none; }
  #screenTeacher { background:#071326; }
  .teacher-header { min-height:132px; padding:12px 16px; }
  .teacher-avatar { width:94px; height:112px; border-radius:20px 20px 12px 12px; }
  .teacher-name { font-size:1rem; }
  .teacher-messages { padding:14px 12px 18px; gap:12px; }
  .tm-bubble { max-width:88%; padding:12px 14px; font-size:.96rem; line-height:1.6; }
  .teacher-suggestions { padding:9px 12px; gap:8px; background:#0A1530; }
  .teacher-suggestions:not(.expanded) .teacher-chip:nth-of-type(n+4),
  .teacher-suggestions:not(.expanded) .teacher-chip-hdr { display:none; }
  .teacher-chip {
    flex:1 1 100%; width:100%; min-height:50px; padding:11px 14px;
    border-radius:14px; justify-content:flex-start; text-align:left; font-size:.86rem;
  }
  .teacher-topics-toggle { display:block; }
  .tm-chips .tm-chip-btn.mobile-extra { display:none; }
  .tm-chips.expanded .tm-chip-btn.mobile-extra { display:inline-flex; }
  .tm-chips-toggle { display:block; }
  .teacher-inputbar { padding:10px 12px calc(10px + env(safe-area-inset-bottom,0px)); background:#071326; position:relative; z-index:2; }
  .teacher-input { min-height:50px; font-size:1rem; }
  .teacher-send-btn { width:50px; height:50px; }
}

/* ═══ CYBER & NEON STYLING (Gemini Blueprint) ═══ */
/* Container for rullende karusell */
.carousel-track {
  display: flex;
  animation: scroll-left 15s linear infinite;
  gap: 20px;
}

/* Neon-glød og 3D-effekt på knapper */
.cyber-button {
  background: #0a0a0a;
  border: 2px solid transparent;
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.3); /* Cyan neon */
  transition: transform 0.3s ease;
}

.cyber-button:hover {
  transform: scale(1.1);
  box-shadow: 0 0 25px rgba(255, 165, 0, 0.7); /* Orange glow */
}

/* Roterende neon-kant */
.neon-border-animation {
  position: absolute;
  border: 2px solid #0ff;
  animation: border-rotate 3s linear infinite;
}

@keyframes scroll-left {
  0% { transform: translateX(100%); }
  100% { transform: translateX(-100%); }
}

@keyframes border-rotate {
  0% { border-color: #0ff; }
  50% { border-color: #f90; }
  100% { border-color: #0ff; }
}

/* Cyber-grid background for Library cards (Bookmarks, History, Signs) */
.hist-card, .sign-card {
  position: relative;
  overflow: hidden;
}

.bm-card::before, .hist-card::before, .sign-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  opacity: .06;
  background-image:
    linear-gradient(rgba(0,245,255,.6) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,245,255,.6) 1px, transparent 1px),
    radial-gradient(circle 2px at 16px 16px, rgba(0,245,255,.8) 100%, transparent 100%),
    radial-gradient(circle 2px at 48px 48px, rgba(255,0,229,.8) 100%, transparent 100%),
    radial-gradient(circle 1.5px at 80px 24px, rgba(255,215,0,.8) 100%, transparent 100%);
  background-size: 32px 32px, 32px 32px, 96px 96px, 96px 96px, 96px 96px;
  z-index: 0;
}

/* Ensure content overlays above the grid backplate */
.bm-card > *, .hist-card > *, .sign-card > * {
  position: relative;
  z-index: 1;
}

.bm-card-remove, .hist-badge {
  z-index: 2 !important;
}

/* ── Universal neon border — ALL buttons, always rotating ── */
.auth-btn, .home-sec-btn, .sb-tool-btn, .sb-nav-btn, .sb-video-btn,
.fk-sc-btn, .end-btn-pri, .end-btn-sec, .paywall-buy-btn,
.tsp-btn, .sp-btn-primary, .sp-btn-sm, .sp-btn-sm-ai, .sp-btn-sm-audio, .sp-btn-sm-bm,
.hp-btn-pri, .hp-btn-sec, .ask-michael-btn, .hist-btn-pri, .hist-btn-sec,
.back-btn, .logout-btn, .lang-btn, .seg-btn, .spd-btn, .vol-btn, .rv-done-btn,
.lib-back-btn, .teacher-send-btn, .tm-chip-btn, .sb-edit-btn, .ai-expand-btn,
.q-bookmark-btn, .sp-ai-tts-btn {
  border: 1.5px solid transparent !important;
  background: linear-gradient(var(--btn-bg, rgba(17,24,39,0.95)), var(--btn-bg, rgba(17,24,39,0.95))) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation: neonFlow 3s linear infinite !important;
}

/* Global rotating neon borders for active/primary buttons and active flags */
.lang-btn.active,
.seg-btn.active,
.spd-btn.active,
.vol-btn.active,
.fk-sc-btn.active,
.home-sec-btn,
.paywall-buy-btn,
.end-btn-pri,
.sp-btn-primary,
.hp-btn-pri {
  border: 1.5px solid transparent !important;
  background: linear-gradient(rgba(17, 24, 39, 0.95), rgba(17, 24, 39, 0.95)) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation: neonFlow 4s linear infinite !important;
  box-shadow: 0 0 10px rgba(0, 245, 255, 0.25) !important;
  transition: transform 0.2s, box-shadow 0.2s !important;
}

/* Ensure active text and SVG colors stand out in active states */
.seg-btn.active,
.spd-btn.active,
.vol-btn.active,
.fk-sc-btn.active {
  color: #00F5FF !important;
}

/* Hover effects for regular buttons: light up with rotating neon borders */
.auth-btn:hover,
.home-sec-btn:hover,
.sb-tool-btn:hover,
.sb-nav-btn:hover,
.fk-sc-btn:hover,
.end-btn-pri:hover,
.end-btn-sec:hover,
.paywall-buy-btn:hover,
.tsp-btn:hover,
.sp-btn-primary:hover,
.sp-btn-sm:hover,
.hp-btn-pri:hover,
.hp-btn-sec:hover,
.ask-michael-btn:hover,
.hist-btn-pri:hover,
.hist-btn-sec:hover,
.back-btn:hover,
.logout-btn:hover {
  border: 1.5px solid transparent !important;
  background: linear-gradient(rgba(17, 24, 39, 0.95), rgba(17, 24, 39, 0.95)) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation: neonFlow 4s linear infinite !important;
  box-shadow: 0 0 12px rgba(255, 0, 229, 0.3) !important;
  transform: scale(1.03) !important;
}

/* Hover effects for all cards: light up with rotating neon borders */
.settings-card:hover,
.quiz-card:hover,
.sign-card:hover,
.hist-card:hover,
.bm-card:hover {
  border: 1.5px solid transparent !important;
  background: linear-gradient(rgba(19, 27, 46, 0.96), rgba(11, 18, 38, 0.98)) padding-box,
              conic-gradient(from var(--neon-angle, 0deg), #00F5FF, #FF00E5, #00F5FF) border-box !important;
  animation: neonFlow 5s linear infinite !important;
  box-shadow: 0 0 15px rgba(0, 245, 255, 0.22) !important;
}
/* Michael readability hotfix: compact teaching images and readable mobile copy. */
.teacher-inline-image {
  display:block; width:auto; max-width:100%; max-height:360px; height:auto;
  object-fit:contain; margin:0 auto; border-radius:8px; background:#fff;
}
.teacher-inline-caption { font-size:.82rem; color:var(--muted); margin-top:8px; text-align:center; }
@media (max-width:767px) {
  #screenTeacher .tm-bubble { font-size:1.05rem; line-height:1.65; }
  #screenTeacher .teacher-inline-image { max-height:210px; }
}
</style>
</head>
<body>

<div id="app">

  <!-- Flag background — absolute so it's clipped by the phone frame on desktop -->
  <div class="flag-bg"></div>

  <!-- TOP BAR -->
  <div id="topBar">
    <div class="top-logo">
      <img src="/api/assets/developer-icon-512.png" alt="Thai2Drive logo" style="width:32px;height:32px;border-radius:9px;object-fit:cover;">
      <span>Thai<span class="logo-t">2</span>Drive</span>
    </div>
    <div class="top-spacer"></div>
    <div id="topStreak">🔥 <span id="topStreakNum">0</span> <span data-key="streak">dagers rekke</span></div>
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
      <button id="topSettingsBtn" onclick="showTab('settings')" title="Innstillinger" style="display:none;width:34px;height:34px;border-radius:50%;border:none;background:rgba(255,255,255,.06);color:var(--muted);font-size:16px;cursor:pointer;align-items:center;justify-content:center;transition:background .2s,color .2s;flex-shrink:0;" onmouseover="this.style.background='rgba(255,255,255,.12)';this.style.color='var(--text)'" onmouseout="this.style.background='rgba(255,255,255,.06)';this.style.color='var(--muted)'">⚙️</button>
    </div>
  </div>

  <!-- CONTENT -->
  <div id="content">

    <!-- ═══ AUTH SCREEN ═══ -->
    <div class="screen active" id="screenAuth">
      <div class="auth-card">
        <div class="auth-header">
          <div class="auth-big-icon"><img src="/api/assets/developer-icon-512.png" alt="Thai2Drive logo" style="width:56px;height:56px;border-radius:14px;object-fit:cover;"></div>
          <h1>Thai<span>2Drive</span></h1>
          <p data-key="auth_tagline">Teoriprøven på thai</p>
          <div class="auth-flags">
            <button type="button" class="auth-flag" id="authLangTH" onclick="setLang('th')" title="ภาษาไทย" aria-label="ภาษาไทย">
              <svg viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg"><rect width="900" height="600" fill="#A51931"/><rect width="900" height="480" y="60" fill="#F4F5F8"/><rect width="900" height="320" y="140" fill="#241D4F"/></svg>
            </button>
            <button type="button" class="auth-flag" id="authLangNO" onclick="setLang('no')" title="Norsk" aria-label="Norsk">
              <svg viewBox="0 0 22 16" xmlns="http://www.w3.org/2000/svg"><rect width="22" height="16" fill="#EF2B2D"/><rect x="6" width="4" height="16" fill="#fff"/><rect y="6" width="22" height="4" fill="#fff"/><rect x="7" width="2" height="16" fill="#002868"/><rect y="7" width="22" height="2" fill="#002868"/></svg>
            </button>
            <button type="button" class="auth-flag" id="authLangEN" onclick="setLang('en')" title="English" aria-label="English">
              <svg viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="30" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" stroke-width="4"/><rect y="11" width="60" height="8" fill="#fff"/><rect x="26" width="8" height="30" fill="#fff"/><rect y="12" width="60" height="6" fill="#C8102E"/><rect x="27" width="6" height="30" fill="#C8102E"/></svg>
            </button>
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
              <button type="button" class="pw-eye" onclick="togglePw(this)" tabindex="-1" data-label-key="toggle_password">👁</button>
            </div>
          </div>
          <div class="forgot-link"><a href="#forgot" onclick="showForgot(); return false;" data-key="forgot_password">Glemt passord?</a></div>
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
              <button type="button" class="pw-eye" onclick="togglePw(this)" tabindex="-1" data-label-key="toggle_password">👁</button>
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
            <a href="#login" style="font-size:.78rem;color:var(--muted);cursor:pointer" onclick="switchTab('login'); return false;" data-key="back">← Tilbake</a>
          </div>
        </div>

        <!-- RESET PASSWORD (enter code + new password) -->
        <div id="formReset" style="display:none">
          <p style="font-size:.85rem;color:var(--muted);margin-bottom:12px;line-height:1.5" id="resetInstructions" data-key="reset_instructions">Sjekk e-posten din for koden</p>
          <div class="form-group">
            <label data-key="reset_code_label">Kode</label>
            <input type="text" id="resetCode" placeholder="123456" inputmode="numeric" maxlength="6" autocomplete="one-time-code" style="letter-spacing:.2em;font-size:1.2rem">
          </div>
          <div class="form-group">
            <label data-key="reset_new_pass_label">Nytt passord</label>
            <div class="pw-wrap">
              <input type="password" id="resetNewPass" placeholder="Minst 6 tegn" data-placeholder-key="auth_password_min_placeholder" autocomplete="new-password">
              <button type="button" class="pw-eye" onclick="togglePw(this)" tabindex="-1" data-label-key="toggle_password">👁</button>
            </div>
          </div>
          <button class="auth-btn" id="resetSubmitBtn" onclick="doResetPassword()" data-key="reset_submit">Sett nytt passord</button>
          <div style="text-align:center;margin-top:12px">
            <a href="#forgot" style="font-size:.78rem;color:var(--muted);cursor:pointer" onclick="switchTab('forgot'); return false;" data-key="back">← Tilbake</a>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ HOME SCREEN ═══ -->
    <div class="screen" id="screenHome">
      <div class="home-top">
        <div class="home-logo-row">
          <img src="/api/assets/developer-icon-512.png" alt="Thai2Drive logo" style="width:64px;height:64px;border-radius:18px;object-fit:cover;box-shadow:0 8px 24px rgba(255,153,51,.35);">
          <div class="home-title">Thai<span>2</span>Drive</div>
          <div class="home-sub" data-key="app_sub">สอบใบขับขี่นอร์เวย์</div>
        </div>

        <div class="streak-badge">
          <span class="streak-fire">🔥</span>
          <span class="streak-num" id="homeStreakNum">0</span>
          <span class="streak-lbl" data-key="streak">dagers rekke</span>
        </div>
      </div>

      <div class="home-main-label" data-key="home_choose_action">Velg hva du vil gjøre</div>
      <button class="home-cta" onclick="startRandomQuiz()">
        <span data-key="home_primary_action">▶ Start quiz / daglig test</span>
      </button>

      <div class="home-main-actions">
        <button class="home-main-choice" onclick="showTab('teacher')">
          <img class="home-main-choice-icon michael-photo" src="/api/assets/michael_profile.jpg" alt="Michael">
          <span class="home-main-choice-copy">
            <span class="home-main-choice-title" data-key="home_ask_michael">Spør Michael AI</span>
            <span class="home-main-choice-sub" data-key="teacher_sub">Still et spørsmål om trafikk</span>
          </span>
        </button>
        <button class="home-main-choice" onclick="toggleTargetPracticeMenu()" aria-controls="targetPracticeMenu" aria-expanded="false" id="targetPracticeToggle">
          <span class="home-main-choice-icon">🎯</span>
          <span class="home-main-choice-copy">
            <span class="home-main-choice-title" data-key="home_targeted">Øv på mine feil & skiltkatalog</span>
            <span class="home-main-choice-sub" id="mistakesHomeCount"></span>
          </span>
        </button>
        <div class="target-practice-menu" id="targetPracticeMenu">
          <button class="target-practice-option" id="mistakesHomeBtn" onclick="startMistakeQuiz()" data-key="mistakes_short">Øv på mine feil</button>
          <button class="target-practice-option" onclick="showTab('signs')" data-key="home_open_signs">Åpne skiltkatalog</button>
        </div>
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
          <div class="hr-label" data-key="readiness_title">ความพร้อมสำหรับการสอบ</div>
          <div class="hr-status" id="hrStatus"></div>
          <div class="hr-sub" id="hrSub"></div>
          <div class="readiness-meter"><div class="readiness-meter-fill" id="hrGaugeFill"></div></div>
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

    <div class="michael-quiz-coach" id="michaelQuizCoach" role="dialog" aria-live="polite" aria-label="Michael">
      <div class="mqc-head">
        <img class="mqc-avatar" src="/api/assets/michael_profile.jpg" alt="Michael">
        <div class="mqc-title" data-key="coach_title">Michael อธิบาย</div>
        <button class="mqc-close" onclick="closeMichaelQuizCoach()" data-label-key="close" aria-label="ปิด">×</button>
      </div>
      <div class="mqc-body" id="michaelQuizCoachBody"></div>
      <button class="mqc-action" id="michaelQuizCoachAction" onclick="requestCoachPractice()" data-key="coach_practical">สิ่งนี้หมายถึงอะไรในทางปฏิบัติ?</button>
    </div>

    <!-- ═══ CATEGORIES SCREEN ═══ -->
    <div class="screen" id="screenCats">
      <div class="carousel-3d-header">
        <div class="screen-title">📚 <span data-key="cats">Kategorier</span> <span id="catCount"></span></div>
      </div>
      <!-- 3D Cylinder Carousel -->
      <div class="carousel-3d-scroll">
        <div class="carousel-3d-wrap" id="carouselWrap">
          <div class="carousel-3d-fade-left"></div>
          <div class="carousel-3d-fade-right"></div>
          <div class="carousel-3d-stage" id="carouselStage">
            <div class="carousel-3d-active-ring" id="carouselRing"></div>
            <!-- items rendered by JS -->
            <div class="loading-wrap" style="position:absolute;top:50%;left:50%;margin:-24px 0 0 -24px;">
              <div class="spinner"></div>
            </div>
          </div>
          <div class="carousel-3d-dots" id="carouselDots"></div>
          <div class="carousel-3d-hint" id="carouselHint">← Sveip for å bla →</div>
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

    <!-- ═══ LIBRARY SCREEN ═══ -->
    <div class="screen" id="screenLibrary">
      <div class="lib-header">
        <button class="lib-back-btn" onclick="showTab('home')" data-title-key="backhome" title="">🏠</button>
        <div class="screen-title">📚 <span data-key="library">Bibliotek</span></div>
      </div>
      <div class="lib-tabs">
        <button class="lib-tab active" data-tab="videos" onclick="setLibraryTab('videos')">🎬 <span data-key="lib_videos">Videoer</span></button>
        <button class="lib-tab" data-tab="podcasts" onclick="setLibraryTab('podcasts')">🎙️ <span data-key="lib_podcasts">Podcaster</span></button>
        <button class="lib-tab" data-tab="micro" onclick="setLibraryTab('micro')">🇹🇭🇳🇴 <span data-key="lib_micro">Thailand vs. Norge</span></button>
      </div>
      <div class="lib-scroll">
        <div id="libraryContent"></div>
      </div>
    </div>

    <!-- ═══ VIDEO PLAYER SCREEN ═══ -->
    <div class="screen" id="screenVideoPlayer">
      <div class="vp-header">
        <button class="vp-back-btn" onclick="closeVideoPlayer()">⬅</button>
        <div class="vp-title" id="vpTitle">–</div>
      </div>
      <div class="vp-player-wrap">
        <video id="vpVideo" controls preload="metadata" playsinline></video>
      </div>
      <div class="vp-glow-road" id="vpGlowRoad"></div>
      <div class="vp-scroll">
        <div class="vp-knowledge-area" id="vpKnowledge"></div>
        <div class="vp-mini-check" id="vpMiniCheck" style="display:none"></div>
      </div>
    </div>

    <!-- ═══ SETTINGS SCREEN ═══ -->
    <div class="screen" id="screenSettings">
      <div class="settings-inner">

        <div class="settings-section">
          <div class="settings-label" data-key="acct">Konto</div>
          <div class="settings-profile-hero">
            <div class="settings-avatar" id="settAvatar">👤</div>
            <div class="settings-profile-name" id="settName">–</div>
            <div class="settings-profile-email" id="settEmail">–</div>
            <div class="settings-profile-badges account-badges" id="settBadges"></div>
          </div>
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
          <div class="settings-label" data-key="sound">Lyd og vibrasjon</div>
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
                <div class="sr-title" data-key="tts_tempo">Opplesing – Tempo</div>
                <div class="sr-sub" data-key="tts_tempo_sub">Hastighet på talesyntese</div>
              </div>
              <div id="settSpdBtns" style="display:flex;gap:5px;flex-wrap:wrap;"></div>
            </div>
            <div class="settings-row" style="flex-wrap:wrap; gap:8px;">
              <div class="sr-icon green">🔈</div>
              <div class="sr-label" style="flex:1; min-width:80px;">
                <div class="sr-title" data-key="tts_volum">Opplesing – Volum</div>
                <div class="sr-sub" data-key="tts_volum_sub">Lydstyrke på talesyntese</div>
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
          <div class="settings-label" data-key="about_app">Om appen</div>
          <div class="settings-card">
            <div class="settings-row">
              <div class="sr-icon gray">📱</div>
              <div class="sr-label">
                <div class="sr-title">Thai2Drive Web</div>
                <div class="sr-sub" data-key="about_app_sub">Teoriprøven på thai for Norge</div>
              </div>
              <div style="color:var(--muted);font-size:.78rem;font-weight:700;background:rgba(255,255,255,.07);padding:3px 9px;border-radius:20px;">v2.0</div>
            </div>
          </div>
        </div>

        <button class="logout-btn" onclick="logout()">🚪 &nbsp;<span data-key="logout">Logg ut</span></button>

      </div>
    </div>

    <!-- ═══ HISTORY SCREEN ═══ -->
    <div class="screen" id="screenHistory">
      <div class="hist-header">
        <div class="screen-title" style="display:flex;align-items:center;gap:10px;">📊 <span data-key="history">Historikk</span> <span id="histCount"></span><button onclick="loadHistory()" style="background:none;border:none;cursor:pointer;padding:4px 8px;border-radius:8px;color:#8899aa;font-size:20px;line-height:1;" title="Oppdater">↻</button></div>
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
      <!-- Tool strip — quick tools accessible from Studiebok -->
      <div class="sb-tools">
        <button class="sb-tool-btn" onclick="showForbikjoring()"><span id="sbToolFkLabel">🚗 Forbikjøring</span></button>
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

    <!-- ═══ FORBIKJØRING SCREEN ═══ -->
    <div class="screen" id="screenForbikjoring">
      <div class="fk-topbar">
        <button class="back-btn" onclick="showTab('studybook')">← Tilbake</button>
        <div class="fk-title" id="fkTitle">🚗 Forbikjøring</div>
      </div>
      <div class="fk-scenarios">
        <button class="fk-sc-btn active" id="fkBtnEasy"  onclick="fkSelect(0)"></button>
        <button class="fk-sc-btn"        id="fkBtnMed"   onclick="fkSelect(1)"></button>
        <button class="fk-sc-btn"        id="fkBtnHard"  onclick="fkSelect(2)"></button>
      </div>
      <!-- Mobile: toggle button + collapsible image panel -->
      <button class="fk-img-toggle" id="fkImgToggle" onclick="fkToggleImg()">👁 Se illustrasjon</button>
      <div class="fk-img-mobile" id="fkImgMobile">
        <img src="/api/assets/forbikjoring.jpg" alt="Forbikjøring illustrasjon"
             onerror="this.parentElement.style.display='none'">
      </div>
      <!-- Two-column layout -->
      <div class="fk-layout">
        <div class="fk-calc-col">
          <div class="fk-body" id="fkBody"><!-- filled by fkRender() --></div>
          <div class="fk-disclaimer" id="fkDisclaimer"></div>
        </div>
        <!-- Desktop-only image column -->
        <div class="fk-img-col">
          <img src="/api/assets/forbikjoring.jpg" alt="Forbikjøring illustrasjon"
               onerror="this.style.display='none'">
        </div>
      </div>
    </div>

    <!-- ═══ STUDIEBOK ADMIN EDIT MODAL ═══ -->
    <div id="studiebokEditModal" style="display:none;position:fixed;inset:0;z-index:9000;background:rgba(0,0,0,.6);align-items:center;justify-content:center;">
      <div style="background:var(--card);border-radius:16px;padding:24px;width:min(92vw,520px);max-height:80vh;overflow-y:auto;display:flex;flex-direction:column;gap:12px;">
        <div style="font-weight:700;font-size:1.05rem;" data-key="studybook_edit_chapter">✏️ Rediger kapittel</div>

        <div style="border:1px solid var(--border);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px;">
          <div style="font-weight:600;font-size:.9rem;color:var(--orange);">🇳🇴 Norsk (NO)</div>
          <label style="font-size:.8rem;color:var(--muted);">Tittel (NO)</label>
          <input id="sbEditTitle" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" />
          <label style="font-size:.8rem;color:var(--muted);">Innhold (NO - HTML)</label>
          <textarea id="sbEditContent" rows="5" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.85rem;width:100%;box-sizing:border-box;resize:vertical;font-family:monospace;"></textarea>
        </div>

        <div style="border:1px solid var(--border);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px;">
          <div style="font-weight:600;font-size:.9rem;color:var(--orange);">🇹🇭 Thai (TH)</div>
          <label style="font-size:.8rem;color:var(--muted);">Tittel (TH)</label>
          <input id="sbEditTitleTh" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" />
          <label style="font-size:.8rem;color:var(--muted);">Innhold (TH - HTML)</label>
          <textarea id="sbEditContentTh" rows="5" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.85rem;width:100%;box-sizing:border-box;resize:vertical;font-family:monospace;"></textarea>
        </div>

        <div style="border:1px solid var(--border);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px;">
          <div style="font-weight:600;font-size:.9rem;color:var(--orange);">🇬🇧 Engelsk (EN)</div>
          <label style="font-size:.8rem;color:var(--muted);">Tittel (EN)</label>
          <input id="sbEditTitleEn" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.95rem;width:100%;box-sizing:border-box;" />
          <label style="font-size:.8rem;color:var(--muted);">Innhold (EN - HTML)</label>
          <textarea id="sbEditContentEn" rows="5" style="padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:var(--bg);color:var(--text);font-size:.85rem;width:100%;box-sizing:border-box;resize:vertical;font-family:monospace;"></textarea>
        </div>

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
        <div class="end-score-quiet" id="endScoreQuiet"></div>
        <div class="end-heading" id="endHeading" data-key="result_done">Øvelsen er ferdig.</div>
        <p class="end-body" id="endBody"></p>
        <div class="end-focus" id="endFocus" style="display:none">
          <div>
            <div class="end-focus-label" data-key="result_focus">Anbefalt øvelse</div>
            <div class="end-focus-topic" id="endFocusTopic"></div>
          </div>
        </div>
        <div class="end-btns">
          <button class="end-btn-pri" onclick="retryQuiz()" data-key="result_retry">Prøv igjen</button>
          <button class="end-btn-sec" onclick="showTab('home')" data-key="home">Hjem</button>
          <button class="end-btn-sec" onclick="showTab('cats')" data-key="pickcat">Velg kategori</button>
        </div>
      </div>
    </div>

    <!-- ═══ PAYWALL SCREEN ═══ -->
    <div class="screen" id="screenPaywall">
      <div class="paywall-card">
        <div class="paywall-gem">💎</div>
        <div class="paywall-title"><span data-key="pw_title"></span></div>
        <div class="paywall-sub" data-key="pw_sub"></div>
        <ul class="paywall-features">
          <li><span class="pf-check">✓</span><span data-key="pw_f1"></span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f2"></span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f3"></span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f4"></span></li>
          <li><span class="pf-check">✓</span><span data-key="pw_f5"></span></li>
        </ul>
        <div class="paywall-price-row">
          <div class="paywall-price-card selected" onclick="buyPremium('monthly',this)" data-plan="monthly">
            <div class="ppc-period" data-key="pw_month"></div>
            <div class="ppc-price" data-price-plan="monthly">199 NOK</div>
            <div class="ppc-per" data-key="pw_per_month"></div>
          </div>
          <div class="paywall-price-card" onclick="buyPremium('three_months',this)" data-plan="three_months" style="position:relative">
            <div class="ppc-badge" data-key="pw_best_value"></div>
            <div class="ppc-period" data-key="pw_three_months"></div>
            <div class="ppc-price" data-price-plan="three_months">399 NOK</div>
            <div class="ppc-per" data-key="pw_per_three_months"></div>
          </div>
          <div class="paywall-price-card" onclick="buyPremium('lifetime',this)" data-plan="lifetime">
            <div class="ppc-period" data-key="pw_lifetime"></div>
            <div class="ppc-price" data-price-plan="lifetime">699 NOK</div>
            <div class="ppc-per" data-key="pw_lifetime_note"></div>
          </div>
        </div>
        <button class="paywall-buy-btn" onclick="buyPremium()">⭐ <span data-key="pw_buy"></span></button>
        <button class="paywall-skip" onclick="restorePurchase()" data-key="pw_restore_purchase"></button>
        <div class="paywall-skip" style="border:none;background:transparent;cursor:default" data-key="pw_cancel_anytime"></div>
      </div>
    </div>

    <!-- ═══ MICHAEL TRAFIKKLÆRER SCREEN ═══ -->
    <div class="screen" id="screenTeacher">

      <!-- LEFT: chat column (full width on mobile, flex:1 on desktop) -->
      <div class="teacher-chat-col">

        <!-- Chat header -->
        <div class="teacher-header">
          <div class="teacher-header-info">
            <div class="teacher-eyebrow" data-key="teacher_role">Trafikklærer</div>
            <div class="teacher-name" id="teacherNameLbl">Michael Trafikklærer</div>
            <div class="teacher-experience" data-key="teacher_experience">16 års erfaring</div>
            <div class="teacher-status" data-key="teacher_online">● Online</div>
          </div>
          <img class="teacher-avatar" src="/api/assets/michael_profile.jpg" alt="Michael">
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
          <!-- Math shortcuts section -->
          <div class="teacher-chip-hdr" id="tcMathHdr" data-hdr-no="🧮 Regnestykker" data-hdr-th="🧮 โจทย์คำนวณ" data-hdr-en="🧮 Calculations"></div>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)"
            data-label-no="🧮 Regnestykker" data-label-th="🧮 โจทย์คำนวณ" data-label-en="🧮 Calculations"
            data-msg-no="🧮 Vis meg alle formler: reaksjonslengde, bremselengde og stoppelengde" data-msg-th="🧮 แสดงสูตรทั้งหมด: ระยะปฏิกิริยา ระยะเบรก และระยะหยุดรถ" data-msg-en="🧮 Show me all formulas: reaction distance, braking distance and stopping distance">🧮 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)"
            data-label-no="🚗 Reaksjonslengde" data-label-th="🚗 ระยะตอบสนอง" data-label-en="🚗 Reaction distance"
            data-msg-no="🚗 Reaksjonslengde — gi meg formelen og regn ut ved 50 km/t" data-msg-th="🚗 ระยะตอบสนอง — ให้สูตรและคำนวณที่ 50 กม./ชม." data-msg-en="🚗 Reaction distance — give me the formula and work out an example at 50 km/h">🚗 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)"
            data-label-no="🛑 Bremselengde" data-label-th="🛑 ระยะเบรก" data-label-en="🛑 Braking distance"
            data-msg-no="🛑 Bremselengde — gi meg formelen og regn ut ved 50 km/t" data-msg-th="🛑 ระยะเบรก — ให้สูตรและคำนวณที่ 50 กม./ชม." data-msg-en="🛑 Braking distance — give me the formula and work out an example at 50 km/h">🛑 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)"
            data-label-no="📏 Stoppelengde" data-label-th="📏 ระยะหยุดรถ" data-label-en="📏 Stopping distance"
            data-msg-no="📏 Stoppelengde — gi meg formelen og regn ut ved 50 km/t" data-msg-th="📏 ระยะหยุดรถ — ให้สูตรและคำนวณที่ 50 กม./ชม." data-msg-en="📏 Stopping distance — give me the formula and work out an example at 50 km/h">📏 <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)"
            data-label-no="⚡ Dobbel fart" data-label-th="⚡ ความเร็วเพิ่มเป็นสองเท่า" data-label-en="⚡ Double speed"
            data-msg-no="⚡ Dobbel fart — hva skjer med bremselengden? Gi eksempel" data-msg-th="⚡ ความเร็วเพิ่มเป็นสองเท่า — เกิดอะไรขึ้นกับระยะเบรก? ให้ตัวอย่าง" data-msg-en="⚡ Double speed — what happens to braking distance? Give an example">⚡ <span class="chip-lbl"></span></button>
          <button class="teacher-chip" onclick="teacherSend(this.dataset.msg)"
            data-label-no="🌧️ Våt/glatt vei" data-label-th="🌧️ ถนนเปียก/ลื่น" data-label-en="🌧️ Wet/slippery road"
            data-msg-no="🌧️ Våt og glatt vei — hvordan påvirker det bremselengden?" data-msg-th="🌧️ ถนนเปียก/ลื่น — ส่งผลต่อระยะเบรกอย่างไร?" data-msg-en="🌧️ Wet/slippery road — how does it affect braking distance?">🌧️ <span class="chip-lbl"></span></button>
          <button class="teacher-topics-toggle" id="teacherMoreBtn" type="button" aria-expanded="false" onclick="toggleTeacherTopics()" data-key="teacher_more_topics">Flere emner</button>
        </div>

        <!-- Input bar -->
        <div class="teacher-inputbar">
          <textarea class="teacher-input" id="teacherInput" rows="1" placeholder="..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();teacherSend();}"></textarea>
          <button class="teacher-send-btn" id="teacherSendBtn" onclick="teacherSend()">➤</button>
        </div>

      </div><!-- /teacher-chat-col -->

      <!-- RIGHT: helper panel — only visible on desktop via CSS -->
      <div class="teacher-side-panel" id="teacherSidePanel">
        <div class="tsp-title" id="tspTitle" data-key="tsp_title">Emner</div>
        <button class="tsp-btn" data-tsp-btn="sign">🛑 <span data-tsp="sign"></span></button>
        <button class="tsp-btn" data-tsp-btn="vikeplikt">🚗 <span data-tsp="vikeplikt"></span></button>
        <button class="tsp-btn" data-tsp-btn="rule">📖 <span data-tsp="rule"></span></button>
        <button class="tsp-btn" data-tsp-btn="practice">📊 <span data-tsp="practice"></span></button>
        <button class="tsp-btn" data-tsp-btn="theory">📝 <span data-tsp="theory"></span></button>
        <button class="tsp-btn" data-tsp-btn="app">❓ <span data-tsp="app"></span></button>
      </div><!-- /teacher-side-panel -->

    </div><!-- /screenTeacher -->

  </div><!-- /content -->

  <!-- BOTTOM NAV — 8 tabs: Hjem → Kategorier → Historikk → Michael → Skilt → Studiebok → Bokmerker → Innstillinger -->
  <div id="bottomNav">
    <button class="bn-tab active" id="bnHome" onclick="showTab('home')">
      <span class="bn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></span><span data-key="home">Hjem</span>
    </button>
    <button class="bn-tab" id="bnCats" onclick="showTab('cats')">
      <span class="bn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg></span><span data-key="cats">Kategorier</span>
    </button>
    <button class="bn-tab" id="bnHistory" onclick="showTab('history')">
      <span class="bn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg></span><span data-key="history">Historikk</span>
    </button>
    <button class="bn-tab bn-tab-michael" id="bnTeacher" onclick="showTab('teacher')">
      <span class="bn-icon"><img src="/api/assets/michael_profile.jpg" style="width:30px;height:30px;border-radius:50%;object-fit:cover;object-position:center 15%;" alt="Michael"></span><span data-key="teacher">Michael</span>
    </button>
    <button class="bn-tab" id="bnSigns" onclick="showTab('signs')">
      <span class="bn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 22 22 2 22"/><line x1="12" y1="9" x2="12" y2="15"/><circle cx="12" cy="18" r="0.5" fill="currentColor"/></svg></span><span data-key="signs">Skilt</span>
    </button>
    <button class="bn-tab" id="bnStudybook" onclick="showTab('studybook')">
      <span class="bn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg></span><span data-key="sb_nav">Studiebok</span>
    </button>
    <button class="bn-tab" id="bnBookmarks" onclick="showTab('bookmarks')">
      <span class="bn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg></span><span data-key="bookmarks">Bokmerker</span>
    </button>
    <button class="bn-tab" id="bnSettings" onclick="showTab('settings')">
      <span class="bn-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></span><span data-key="settings">Innstillinger</span>
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
      <button class="sp-btn-sm sp-btn-sm-ai" type="button" onclick="askAiAboutSign()"><span data-key="ask_ai">Spør AI</span></button>
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
var isMistakeMode     = false; // active answerable quiz sourced from user_mistakes
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

// Hoisted variables for applyUILang
var NAV_SVG = {
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
  cats: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
  history: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
  teacher: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1 .4-1.4 .9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6 .4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/></svg>',
  signs: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 22 22 2 22"/><line x1="12" y1="9" x2="12" y2="15"/><circle cx="12" cy="18" r="0.5" fill="currentColor"/></svg>',
  studybook: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  bookmarks: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>',
  settings: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
};
var _signFavorites = [];
try { _signFavorites = JSON.parse(localStorage.getItem('t2d_signFavs') || '[]'); } catch(e) {}
var _signPanelData = null;
var _signPanelLang = 'no';

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
  meta_description:{th:'ฝึกข้อสอบทฤษฎีใบขับขี่นอร์เวย์ด้วยภาษาไทย นอร์เวย์ และอังกฤษกับ Thai2Drive', no:'Øv til norsk teoriprøve på thai, norsk og engelsk med Thai2Drive.', en:'Practise for the Norwegian driving theory test in Thai, Norwegian and English with Thai2Drive.'},
  toggle_password:{th:'แสดงหรือซ่อนรหัสผ่าน', no:'Vis eller skjul passord', en:'Show or hide password'},
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
  home_choose_action:{th:'เลือกสิ่งที่คุณต้องการฝึก', no:'Velg hva du vil gjøre', en:'Choose what you want to do'},
  home_primary_action:{th:'▶ เริ่มควิซ / แบบทดสอบประจำวัน', no:'▶ Start quiz / daglig test', en:'▶ Start quiz / daily test'},
  home_ask_michael:{th:'ถาม Michael AI', no:'Spør Michael AI', en:'Ask Michael AI'},
  home_targeted:{th:'ฝึกข้อที่ตอบผิดและคลังป้ายจราจร', no:'Øv på mine feil & skiltkatalog', en:'Practise my mistakes & road signs'},
  home_open_signs:{th:'เปิดคลังป้ายจราจร', no:'Åpne skiltkatalog', en:'Open road sign catalogue'},
  exam:        {th:'📋 สอบ',            no:'📋 Eksamen',       en:'📋 Exam'},
  daily:       {th:'📅 ทดสอบรายวัน',    no:'📅 Daglig test',   en:'📅 Daily test'},
  exam_short:  {th:'สอบ',               no:'Eksamen',          en:'Exam'},
  daily_short: {th:'ทดสอบรายวัน',       no:'Daglig test',      en:'Daily'},
  mistakes_short:{th:'แบบฝึกหัดข้อที่เคยตอบผิด', no:'Øv på mine feil', en:'Practice my mistakes'},
  mistakes_count:{th:'{count} ข้อที่ต้องทบทวน', no:'{count} spørsmål å repetere', en:'{count} questions to review'},
  mistakes_empty:{th:'ยังไม่มีข้อที่ต้องทบทวน', no:'Du har ingen aktive feil å øve på.', en:'You have no active mistakes to practise.'},
  mistakes_login:{th:'เข้าสู่ระบบเพื่อฝึกข้อที่เคยตอบผิด', no:'Logg inn for å øve på feilene dine.', en:'Log in to practise your mistakes.'},
  mistakes_load_error:{th:'โหลดข้อที่เคยตอบผิดไม่ได้', no:'Kunne ikke laste feilene dine.', en:'Could not load your mistakes.'},
  signs_short: {th:'ป้ายจราจร',         no:'Skilt',            en:'Signs'},
  sb_short:    {th:'หนังสือเรียน',       no:'Studiebok',        en:'Study Book'},
  fk_short:    {th:'คำนวณระยะ',         no:'Trafikk-matte',    en:'Math'},
  lib_short:   {th:'ห้องสมุด',           no:'Bibliotek',        en:'Library'},
  bm_short:    {th:'บุ๊กมาร์ก',         no:'Bokmerker',        en:'Bookmarks'},
  hist_short:  {th:'ประวัติ',            no:'Historikk',        en:'History'},
  loading:     {th:'กำลังโหลด…',        no:'Laster spørsmål…', en:'Loading…'},
  streak:      {th:'วันติดต่อกัน',     no:'dagers rekke',    en:'day streak'},
  answered:    {th:'ตอบแล้ว',          no:'BESVART',          en:'ANSWERED'},
  correct_stat:{th:'ถูกต้อง',           no:'RIKTIGE',          en:'CORRECT'},
  accuracy:    {th:'ความแม่นยำ',        no:'NØYAKTIGHET',      en:'ACCURACY'},
  premium_on:  {th:'⭐ พรีเมียม',       no:'⭐ Premium',        en:'⭐ Premium'},
  premium_sub: {th:'คุณมีสิทธิ์ทุกฟีเจอร์', no:'Du har tilgang til alle funksjoner', en:'You have access to all features'},
  acct:        {th:'บัญชี',             no:'Konto',            en:'Account'},
  language:    {th:'ภาษา',              no:'Språk',            en:'Language'},
  teacher:     {th:'Michael',            no:'Michael',          en:'Michael'},
  teacher_name:{th:'ครูสอนขับรถ Michael', no:'Michael Trafikklærer', en:'Michael Driving Teacher'},
  teacher_role:{th:'ครูสอนขับรถ', no:'Trafikklærer', en:'Driving teacher'},
  teacher_experience:{th:'ประสบการณ์ 16 ปี', no:'16 års erfaring', en:'16 years of experience'},
  teacher_more_topics:{th:'หัวข้อเพิ่มเติม', no:'Flere emner', en:'More topics'},
  teacher_fewer_topics:{th:'แสดงน้อยลง', no:'Vis færre', en:'Show fewer'},
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
  q_lang:      {th:'ภาษาของคำถาม',      no:'Spørsmålsspråk',   en:'Question language'},
  q_lang_sub:  {th:'เลือกภาษาสำหรับคำถามและคำตอบ', no:'Velg språk for spørsmål og svar', en:'Choose language for questions and answers'},
  sound:       {th:'เสียงและระบบสั่น',  no:'Lyd og vibrasjon', en:'Sound and vibration'},
  sfx:         {th:'เอฟเฟกต์เสียง',     no:'Lydeffekter',      en:'Sound effects'},
  sfx_sub:     {th:'เสียงเตือนเมื่อตอบถูกและตอบผิด', no:'Pling ved riktig, buzz ved feil', en:'Pling on correct, buzz on wrong'},
  style:       {th:'รูปแบบ',            no:'Stil',             en:'Style'},
  style_sub:   {th:'การตอบสนองเมื่อคุณตอบคำถาม', no:'Tilbakemelding når du svarer', en:'Feedback style when answering'},
  soft:        {th:'นุ่มนวล',            no:'Myk',              en:'Soft'},
  strong:      {th:'หนักแน่น',           no:'Sterk',            en:'Strong'},
  appearance:  {th:'รูปลักษณ์',          no:'Utseende',         en:'Appearance'},
  theme:       {th:'ธีม',               no:'Tema',             en:'Theme'},
  light:       {th:'สว่าง',              no:'Lys',              en:'Light'},
  dark:        {th:'มืด',               no:'Mørk',             en:'Dark'},
  auto:        {th:'ตามระบบ',            no:'Auto',             en:'Auto'},
  about_app:   {th:'เกี่ยวกับแอป',       no:'Om appen',         en:'About the app'},
  about_app_sub:{th:'แบบทดสอบข้อเขียนใบขับขี่นอร์เวย์เป็นภาษาไทย', no:'Teoriprøven på thai for Norge', en:'Norwegian driving theory test in Thai'},
  logout:      {th:'ออกจากระบบ',         no:'Logg ut',          en:'Log out'},
  history:     {th:'ประวัติ',            no:'Historikk',        en:'History'},
  signs:       {th:'ป้ายจราจร',          no:'Trafikkskilt',     en:'Traffic Signs'},
  signs_empty: {th:'ไม่พบป้าย',           no:'Ingen skilt funnet', en:'No signs found'},
  login:       {th:'เข้าสู่ระบบ',          no:'Logg inn',         en:'Log in'},
  auth_tagline:{th:'ข้อสอบทฤษฎีใบขับขี่นอร์เวย์', no:'Teoriprøven på thai', en:'The Norwegian theory test'},
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
  mode_mistakes:{th:'แบบฝึกหัดข้อที่เคยตอบผิด', no:'Øv på mine feil', en:'Practice my mistakes'},
  readiness_title:{th:'ความพร้อมสำหรับการสอบ', no:'Klar for prøven', en:'Ready for the test'},
  readiness_keep:{th:'ฝึกต่อไป!', no:'Fortsett å øve!', en:'Keep practising!'},
  readiness_close:{th:'ใกล้พร้อมแล้ว!', no:'Nærmer seg klar!', en:'Getting close!'},
  readiness_ready:{th:'คุณพร้อมสอบทฤษฎีกับ Statens vegvesen แล้ว! 🚗', no:'Du er klar for teoriprøven hos Statens vegvesen! 🚗', en:'You are ready for the theory test at Statens vegvesen! 🚗'},
  readiness_breakdown:{th:'50 ข้อล่าสุด: {accuracy}% · ฝึกข้อผิดสำเร็จ: {mastery}%', no:'Siste 50: {accuracy}% · Mestret feil: {mastery}%', en:'Last 50: {accuracy}% · Mistakes mastered: {mastery}%'},
  coach_title:{th:'Michael อธิบาย', no:'Michael forklarer', en:'Michael explains'},
  coach_loading:{th:'Michael กำลังดูคำถาม…', no:'Michael ser på spørsmålet…', en:'Michael is reviewing the question…'},
  coach_unavailable:{th:'ตอนนี้ Michael ตอบไม่ได้ อ่านคำอธิบายปกติและทำแบบทดสอบต่อได้เลย', no:'Michael svarer ikke akkurat nå. Bruk den vanlige forklaringen og fortsett quizen.', en:'Michael is unavailable right now. Use the regular explanation and continue the quiz.'},
  coach_practical:{th:'สิ่งนี้หมายถึงอะไรในทางปฏิบัติ?', no:'Hva betyr dette i praksis?', en:'What does this mean in practice?'},
  coach_practice_loading:{th:'Michael กำลังสร้างคำถามฝึกสั้น ๆ…', no:'Michael lager et kort kontrollspørsmål…', en:'Michael is creating a short practice question…'},
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
  ask_michael: {th:'ถาม Michael เรื่องข้อนี้', no:'Spør Michael om dette', en:'Ask Michael about this'},
  show_more:   {th:'ดูเพิ่ม',              no:'Vis mer',          en:'Show more'},
  show_less:   {th:'ย่อน้อยลง',             no:'Vis mindre',       en:'Show less'},
  driving_teacher:{th:'ครูสอนขับรถ',        no:'Kjørelærer',       en:'Driving teacher'},
  video_short:{th:'📹 คำอธิบายสั้น',       no:'📹 Kort forklaring', en:'📹 Short explanation'},
  video_watch:{th:'📹 ดูคำอธิบายสั้น',      no:'📹 Se kort forklaring', en:'📹 Watch short explanation'},
  sb_watch_video:{th:'▶ ดูวิดีโอ',         no:'▶ Se video',           en:'▶ Watch video'},
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
  retry_category_unavailable:{th:'ไม่พบหมวดหมู่นี้แล้ว', no:'Fant ikke denne kategorien lenger.', en:'Could not find this category anymore.'},
  result_saved:{th:'บันทึกผลแล้ว ✓',        no:'Resultat lagret ✓', en:'Result saved ✓'},
  result_save_failed:{th:'บันทึกผลไม่สำเร็จ: ', no:'Lagring feilet: ', en:'Save failed: '},
  result_score:{th:'{correct} จาก {total} ถูก', no:'{correct} av {total} riktige', en:'{correct} of {total} correct'},
  result_focus:{th:'หัวข้อแนะนำให้ฝึก',      no:'Anbefalt øvelse',  en:'Recommended practice'},
  result_done:{th:'ทำแบบฝึกเสร็จแล้ว',       no:'Øvelsen er ferdig.', en:'Practice finished.'},
  result_retry:{th:'ลองอีกครั้ง',             no:'Prøv igjen',        en:'Try again'},
  result_exam_pass_head:{th:'ผ่าน',          no:'Bestått.',         en:'Passed.'},
  result_exam_pass_body:{th:'คุณพร้อมสำหรับการสอบทฤษฎีแล้ว ลองทำอีกหนึ่งรอบเพื่อเพิ่มความมั่นใจ', no:'Du er klar for teoriprøven. Gjennomfør gjerne enda en runde for å bygge selvtillit.', en:'You are ready for the theory test. Do one more round to build confidence.'},
  result_exam_fail_head:{th:'ครั้งนี้ยังไม่ผ่าน', no:'Ikke bestått denne gangen.', en:'Not passed this time.'},
  result_exam_focus_body:{th:'ควรใช้เวลาเพิ่มกับเรื่อง {topic} ฝึกต่อแล้วลองอีกครั้ง', no:'Det er verdt å bruke litt mer tid på {topic}. Øv på det og prøv igjen.', en:'It is worth spending more time on {topic}. Practice it and try again.'},
  result_solid_head:{th:'ทำได้มั่นคง',       no:'Solid gjennomkjøring.', en:'Solid run-through.'},
  result_solid_body:{th:'คุณเริ่มจำสถานการณ์จราจรและตัดสินใจได้ถูกต้อง นี่คือสิ่งสำคัญในการขับจริง', no:'Du gjenkjenner trafikksituasjonene godt og vurderer riktig. Det er det som teller i praksis.', en:'You recognize traffic situations well and make sound decisions. That is what matters in real driving.'},
  result_short_practice_body:{th:'คุณทำได้ดี ลองชุดที่ยาวขึ้นเพื่อยืนยันความเข้าใจ', no:'Du traff godt. Prøv et lengre sett for å bekrefte forståelsen.', en:'You did well. Try a longer set to confirm the understanding.'},
  result_right_way_head:{th:'คุณมาถูกทางแล้ว', no:'Du er på rett vei.', en:'You are on the right track.'},
  result_right_way_focus_body:{th:'ส่วนใหญ่เข้าใจดีแล้ว มาฝึกเพิ่มอีกนิดกับ {topic}', no:'Forståelsen er god på det meste. La oss bruke litt mer tid på {topic}.', en:'Most of the understanding is good. Let us spend a bit more time on {topic}.'},
  result_right_way_body:{th:'บางสถานการณ์ยังไม่ติดแน่น ซึ่งเป็นเรื่องปกติ ฝึกต่ออย่างใจเย็น', no:'Noen situasjoner har ikke satt seg helt ennå — det er normalt. Fortsett å øve.', en:'Some situations have not fully settled yet. That is normal. Keep practicing.'},
  result_more_head:{th:'มาฝึกเพิ่มอีกนิด',   no:'La oss øve litt mer.', en:'Let us practice a bit more.'},
  result_more_body:{th:'กฎจราจรไม่ได้ติดตัวในรอบเดียว ฝึกต่ออย่างใจเย็น ความเข้าใจจะค่อย ๆ ชัดขึ้น', no:'Trafikkreglene sitter ikke alltid med én runde. Prøv igjen — det tar tid å bygge forståelse.', en:'Traffic rules do not always settle after one round. Keep practicing calmly; understanding grows with time.'},
  result_more_focus_body:{th:'ควรดูเรื่อง {topic} ให้ละเอียดขึ้น อ่านคำอธิบายอย่างใจเย็น', no:'Det er verdt å gå litt nærmere inn på {topic}. Les forklaringene grundig.', en:'It is worth looking more closely at {topic}. Read the explanations carefully.'},
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
  library_home:{th:'📚 ห้องสมุด — วิดีโอและพอดแคสต์', no:'📚 Bibliotek — Video & Podcast', en:'📚 Library — Videos & Podcasts'},
  library:{th:'ห้องสมุด', no:'Bibliotek', en:'Library'},
  lib_videos:{th:'วิดีโอ', no:'Videoer', en:'Videos'},
  lib_podcasts:{th:'พอดแคสต์', no:'Podcaster', en:'Podcasts'},
  lib_micro:{th:'ไทยกับนอร์เวย์', no:'Thailand vs. Norge', en:'Thailand vs. Norway'},
  micro_intro:{th:'บทเรียนสั้น ๆ สำหรับผู้ขับขี่ชาวไทยที่กำลังเรียนกฎจราจรของนอร์เวย์ แตะบทเรียนเพื่อเปิด', no:'Korte leksjoner for thai-førere som lærer norske trafikkregler. Trykk for å åpne.', en:'Short lessons for Thai drivers learning Norwegian traffic rules. Tap to open.'},
  micro_road_side_title:{th:'ขับชิดขวาในนอร์เวย์ เทียบกับขับชิดซ้ายในไทย', no:'Høyrekjøring i Norge vs. venstrekjøring i Thailand', en:'Driving on the right in Norway vs. the left in Thailand'},
  micro_road_side_body:{th:'ในนอร์เวย์ คุณต้องขับทางด้านขวาของถนน การเลี้ยวและตำแหน่งรถในทางแยกจึงกลับด้านจากที่คุ้นเคยในไทย', no:'I Norge kjører du på høyre side. Plassering før sving og gjennom kryss blir derfor motsatt av vanen fra Thailand.', en:'In Norway you drive on the right. Positioning before turns and through intersections is therefore opposite to the habit from Thailand.'},
  micro_road_side_action:{th:'จำไว้: หลังเลี้ยว ให้รถอยู่ในช่องทางขวาของทิศทางที่คุณกำลังไป', no:'Husk: Etter en sving skal bilen inn på høyre side i kjøreretningen.', en:'Remember: After turning, place the car on the right side in your direction of travel.'},
  micro_yield_title:{th:'กฎให้ทางขวาและการให้ทางในทางแยกนอร์เวย์', no:'Høyreregelen og vikeplikt i norske veikryss', en:'The right-hand rule and yielding at Norwegian intersections'},
  micro_yield_body:{th:'หากไม่มีป้ายหรือสัญญาณไฟ คุณต้องให้ทางแก่รถที่มาจากด้านขวา มองหาป้ายให้ทางและเส้นสามเหลี่ยมบนถนนเสมอ', no:'Når skilt eller trafikklys ikke regulerer krysset, har du normalt vikeplikt for trafikk fra høyre. Se alltid etter vikepliktskilt og haitenner.', en:'When signs or traffic lights do not control the intersection, you normally yield to traffic from the right. Always look for yield signs and shark teeth.'},
  micro_yield_action:{th:'ชะลอความเร็วก่อนถึงทางแยก มองซ้าย–ขวา–ซ้าย และเตรียมหยุด', no:'Senk farten før krysset, se til begge sider og vær klar til å stoppe.', en:'Slow down before the intersection, look both ways and be ready to stop.'},
  micro_winter_title:{th:'การขับรถในฤดูหนาว หิมะ น้ำแข็ง และความมืด', no:'Vinterkjøring, snø, is og mørkekjøring', en:'Winter driving, snow, ice and darkness'},
  micro_winter_body:{th:'พื้นถนนลื่นทำให้ระยะเบรกยาวขึ้นมาก ลดความเร็ว เพิ่มระยะห่าง และใช้พวงมาลัย คันเร่ง และเบรกอย่างนุ่มนวล', no:'Glatt føre kan gi mye lengre bremselengde. Senk farten, øk avstanden og bruk ratt, gass og brems mykt.', en:'Slippery roads can greatly increase braking distance. Reduce speed, increase the gap and use steering, throttle and brakes smoothly.'},
  micro_winter_action:{th:'ตรวจยาง ไฟ และกระจกก่อนออกเดินทาง และเผื่อระยะหยุดมากกว่าปกติ', no:'Sjekk dekk, lys og ruter før turen, og planlegg med ekstra stoppavstand.', en:'Check tyres, lights and windows before driving, and allow extra stopping distance.'},
  micro_roundabout_title:{th:'วงเวียนและกฎการใช้ไฟเลี้ยวในนอร์เวย์', no:'Rundkjøringer og blinklys i Norge', en:'Roundabouts and signalling in Norway'},
  micro_roundabout_body:{th:'ให้ทางแก่รถที่อยู่ในวงเวียน เลือกช่องทางให้เหมาะสม และเปิดไฟเลี้ยวขวาก่อนออกจากวงเวียน', no:'Du har vikeplikt for trafikken i rundkjøringen. Velg riktig felt og blink til høyre før du kjører ut.', en:'Yield to traffic in the roundabout. Choose the correct lane and signal right before exiting.'},
  micro_roundabout_action:{th:'มองกระจกและจุดบอดก่อนเปลี่ยนช่องทางหรือออกจากวงเวียน', no:'Sjekk speil og blindsone før feltskifte og før du kjører ut.', en:'Check mirrors and blind spots before changing lanes or exiting.'},
  forbikjoring_label:{th:'🚗 แซง', no:'🚗 Forbikjøring', en:'🚗 Overtaking'},
  fk_title:{th:'🚗 การแซง — คำนวณระยะ', no:'🚗 Forbikjøring — Avstandskalkulator', en:'🚗 Overtaking — Distance Calculator'},
  fk_scenario_easy:{th:'🟢 ง่าย', no:'🟢 Lett', en:'🟢 Easy'},
  fk_scenario_med:{th:'🟡 ปานกลาง', no:'🟡 Middels', en:'🟡 Medium'},
  fk_scenario_hard:{th:'🔴 ยาก', no:'🔴 Vanskelig', en:'🔴 Hard'},
  fk_your_speed:{th:'ความเร็วของคุณ', no:'Din fart', en:'Your speed'},
  fk_ahead_speed:{th:'รถคันหน้า', no:'Bil foran', en:'Car ahead'},
  fk_oncoming_dist:{th:'ระยะถึงรถสวนทาง', no:'Avstand til møtende', en:'Distance to oncoming'},
  fk_weather:{th:'สภาพอากาศ', no:'Vær', en:'Weather'},
  fk_steps_hdr:{th:'การคำนวณ', no:'Utregning', en:'Calculation'},
  fk_step_time:{th:'เวลาในการแซง', no:'Tid å passere', en:'Time to overtake'},
  fk_step_your:{th:'ระยะทางของคุณ (🟦)', no:'Din strekning (🟦)', en:'Your distance (🟦)'},
  fk_step_onc:{th:'รถสวนทาง (🟥)', no:'Møtende kjører (🟥)', en:'Oncoming travels (🟥)'},
  fk_step_margin:{th:'สิ่งกันชน (🟨)', no:'Sikkerhetsmargin (🟨)', en:'Safety margin (🟨)'},
  fk_step_need:{th:'รวมที่ต้องการ', no:'Total trengs', en:'Total needed'},
  fk_step_free:{th:'ถนนที่เหลือ (🟩)', no:'Fri vegstrekning (🟩)', en:'Free road (🟩)'},
  fk_bar_hdr:{th:'แผนภาพระยะทาง', no:'Avstandsdiagram', en:'Distance diagram'},
  fk_result_safe:{th:'✅ ปลอดภัย — ระยะเพียงพอ', no:'✅ TRYGT — Du har god margin', en:'✅ SAFE — You have good margin'},
  fk_result_warn:{th:'⚠️ เฉียดฉิว — ระยะน้อยมาก', no:'⚠️ KNAPT — Meget liten margin', en:'⚠️ CLOSE — Very little margin'},
  fk_result_danger:{th:'❌ อันตราย — ระยะไม่พอ', no:'❌ FOR FARLIG — Ikke nok plass', en:'❌ DANGEROUS — Not enough room'},
  fk_img_toggle:{th:'👁 ดูภาพประกอบ', no:'👁 Se illustrasjon', en:'👁 View illustration'},
  fk_disclaimer:{th:'นี่เป็นแบบฝึกหัดแบบง่าย ในการขับจริงต้องประเมินทัศนวิสัย ความเร็ว สภาพอากาศ ถนน และรถสวนทางเสมอ', no:'Dette er en forenklet øvingsmodell. I trafikken må du alltid vurdere sikt, fart, vær, vei og møtende trafikk.', en:'This is a simplified practice model. In real traffic, always assess visibility, speed, weather, road conditions and oncoming traffic.'},
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
  podcast_short:{th:'🎙️ พอดแคสต์', no:'🎙️ Podcast-forklaring', en:'🎙️ Podcast explanation'},
  ask_ai:      {th:'🚗 ถามไมเคิล',           no:'🚗 Spør Michael',   en:'🚗 Ask Michael'},
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
  pw_title:    {th:'ปลดล็อกการเข้าถึงทั้งหมด', no:'Lås opp full tilgang', en:'Unlock full access'},
  pw_sub:      {th:'คุณได้ใช้สิทธิ์ทดลองเรียนฟรีครบแล้ว', no:'Du har brukt gratisprøven', en:'You have used your free trial'},
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
  pw_best_value:{th:'คุ้มค่าที่สุด – ประหยัด 34%', no:'Best verdi – spar 34%', en:'Best value – save 34%'},
  pw_lifetime_note:{th:'จ่ายครั้งเดียว – ใช้งานได้ตลอดไป', no:'Betal én gang – bruk for alltid', en:'Pay once – use forever'},
  pw_buy:      {th:'ปลดล็อกพรีเมียมเพื่อเข้าถึงแบบไม่จำกัด', no:'Lås opp Premium for ubegrenset tilgang', en:'Unlock Premium for unlimited access'},
  pw_restore_purchase:{th:'กู้คืนการซื้อ', no:'Gjenopprett kjøp', en:'Restore purchase'},
  pw_cancel_anytime:{th:'ยกเลิกเมื่อไหร่ก็ได้', no:'Avslutt når som helst', en:'Cancel anytime'},
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
  sb_nav:          {th:'หนังสือเรียน',    no:'Studiebok',     en:'Study Book'},
  sb_home_btn:     {th:'📖 หนังสือเรียน — กฎจราจรนอร์เวย์', no:'📖 Studiebok — Norsk trafikk', en:'📖 Study Book — Norwegian traffic'},
  sb_cancel:       {th:'ยกเลิก',         no:'Avbryt',        en:'Cancel'},
  sb_save:         {th:'บันทึก',         no:'Lagre',         en:'Save'},
  sb_not_available:{th:'เนื้อหานี้ยังไม่มีในภาษาของคุณ', no:'Dette innholdet er ikke tilgjengelig på ditt språk ennå.', en:'This content is not available in your language yet.'},
  tts_tempo:       {th:'ความเร็วในการอ่านออกเสียง', no:'Opplesing – Tempo', en:'Read aloud – Tempo'},
  tts_tempo_sub:   {th:'ความเร็วของระบบสังเคราะห์เสียง', no:'Hastighet på talesyntese', en:'Text-to-speech speed'},
  tts_volum:       {th:'ระดับเสียงของการอ่านออกเสียง', no:'Opplesing – Volum', en:'Read aloud – Volume'},
  tts_volum_sub:   {th:'ระดับความดังของระบบสังเคราะห์เสียง', no:'Lydstyrke på talesyntese', en:'Text-to-speech volume'},

  // ── Språkrenhet: nøkler for tekst som tidligere var hardkodet på norsk ──────
  missing_text:    {th:'ยังไม่มีข้อมูลภาษาไทย', no:'Ikke oversatt ennå', en:'Not translated yet'},
  error_prefix:    {th:'ข้อผิดพลาด: ',        no:'Feil: ',            en:'Error: '},
  load_error:      {th:'โหลดไม่สำเร็จ',        no:'Feil ved lasting',  en:'Loading failed'},
  invalid_response:{th:'การตอบกลับไม่ถูกต้อง', no:'Ugyldig respons',   en:'Invalid response'},
  lib_load_failed: {th:'โหลดคลังเนื้อหาไม่ได้', no:'Kunne ikke laste biblioteket.', en:'Could not load the library.'},
  empty_no_content:{th:'📭 ไม่มีเนื้อหาที่ใช้ได้', no:'📭 Ingen innhold tilgjengelig', en:'📭 No content available'},
  video_retry_hint:{th:'💪 ไม่เป็นไร! ดูวิดีโออีกครั้งหรืออ่านในหนังสือเรียน', no:'💪 Ingen fare! Se videoen en gang til eller les i Studieboken.', en:'💪 No worries! Watch the video again or read the Study Book.'},
  access_check_failed:{th:'ตรวจสอบสิทธิ์การเข้าใช้ไม่สำเร็จ ลองอีกครั้ง', no:'Kunne ikke bekrefte tilgangen din. Prøv igjen.', en:'Could not verify your access. Please try again.'},
  vp_mc_q_topic:   {th:'คุณได้เรียนรู้อะไรใหม่เกี่ยวกับ{topic}ไหม?', no:'Lærte du noe nytt om {topic}?', en:'Did you learn something new about {topic}?'},
  vp_mc_q_generic: {th:'คุณได้เรียนรู้อะไรใหม่ไหม?', no:'Lærte du noe nytt?', en:'Did you learn something new?'},
  vp_mc_yes:       {th:'ใช่ ได้เรียนรู้เลย!',    no:'Ja, det gjorde jeg!', en:'Yes, I did!'},
  vp_mc_no:        {th:'ยังไม่ค่อยเข้าใจ',       no:'Ikke helt',           en:'Not quite'},
  vp_mc_correct:   {th:'⭐ เยี่ยมมาก! ฝึกต่อไปแล้วจะจำได้แน่นอน', no:'⭐ Topp! Fortsett å øve, så sitter det!', en:'⭐ Great! Keep practising and it will stick!'},

  // ── Gratisuke: 7 dagers prøveperiode ───────────────────────────────────────
  // Ingen emoji i strengene — .pb-icon bærer 🎁 mens prøveuken varer.
  trial_active:    {th:'สัปดาห์ทดลองใช้ฟรีของคุณกำลังทำงานอยู่', no:'Gratisuken din er i gang', en:'Your free week is running'},
  trial_days_left: {th:'เหลืออีก {days} วันของสัปดาห์ทดลองใช้ฟรี', no:'{days} dager igjen av gratisuken', en:'{days} days left of your free week'},
  trial_two_days:  {th:'เหลืออีกแค่ 2 วันของสัปดาห์ทดลองใช้ฟรี! คุณทำได้ดีมาก', no:'Bare 2 dager igjen av gratisuken! Du gjør det bra.', en:'Only 2 days left of your free week! You are doing great.'},
  trial_last_day:  {th:'วันสุดท้ายของการใช้งานฟรี — อีกนิดเดียวเท่านั้น!', no:'Siste dag med gratis tilgang — du er nesten i mål!', en:'Last day of free access — you are almost there!'},
  trial_sub:       {th:'คุณใช้ได้ทุกฟีเจอร์ในระหว่างสัปดาห์ทดลองใช้ฟรี', no:'Du har tilgang til alle funksjoner i gratisuken', en:'You have access to all features during your free week'},
  trial_ended:     {th:'สัปดาห์ทดลองใช้ฟรีของคุณสิ้นสุดแล้ว เลือกแพ็กเกจเพื่อฝึกต่อ', no:'Gratisuken din er over. Velg et abonnement for å fortsette å øve.', en:'Your free week has ended. Choose a plan to keep practising.'},

  // ── Retur fra Stripe-checkout ──────────────────────────────────────────────
  premium_activated_toast:  {th:'เปิดใช้ Premium แล้ว', no:'Premium er aktivert', en:'Premium activated'},
  payment_unconfirmed_toast:{th:'ยังยืนยันการชำระเงินไม่ได้', no:'Betalingen kunne ikke bekreftes ennå', en:'Payment could not be confirmed yet'},
  checkout_unavailable_toast:{th:'ไม่สามารถเปิดการชำระเงินได้ในตอนนี้', no:'Betaling er ikke tilgjengelig akkurat nå', en:'Payment is not available right now'},
  free_questions_left:      {th:'เหลือ {count} คำถามฟรี', no:'{count} gratis spørsmål igjen', en:'{count} free questions left'},
};

function t(key) {
  var entry = UI[key];
  if (entry && typeof entry[appLang] === 'string' && entry[appLang].trim() !== '') {
    return entry[appLang];
  }
  if (window.console && console.warn) console.warn('[i18n] missing translation', key, appLang);
  return key;
}
function tf(key, vars) {
  var s = t(key);
  Object.keys(vars || {}).forEach(function(k) {
    s = s.replace(new RegExp('\\{' + k + '\\}', 'g'), vars[k]);
  });
  return s;
}
// ── Språkrenhet: lån aldri tekst fra et annet språk ─────────────────────────
// Mangler oversettelsen skal elementet skjules (tom streng) eller vise en
// nøytral etikett på DET AKTIVE språket. Se t() og _getProp() for samme regel.
var MISSING_TEXT = { th:'ยังไม่มีข้อมูลภาษาไทย', no:'Ikke oversatt ennå', en:'Not translated yet' };
function missingText() { return MISSING_TEXT[appLang] || ''; }

// Strikt erstatning for pickLang(): kun aktivt språk, ellers tom streng.
function pickStrict(obj) {
  if (!obj) return '';
  if (typeof obj === 'string') return obj;
  var v = obj[appLang];
  return (typeof v === 'string' && v.trim() !== '') ? v : '';
}

function modeLabel(mode) {
  var labels = {exam:t('mode_exam'), category:t('mode_category'), daily:t('mode_daily'), random:t('mode_random'), mistakes:t('mode_mistakes')};
  return labels[mode] || mode || 'Quiz';
}
function readinessForPct(pct, compact) {
  if (pct >= 80) return {cls:'good', text:(compact ? '✓ ' : '') + t('ready_test'), color:'var(--green)'};
  if (pct >= 60) return {cls:'ok', text:(compact ? '▲ ' : '') + t('almost_ready'), color:'var(--orange)'};
  return {cls:'bad', text:(compact ? '↺ ' : '') + t('practice_more'), color:'#EF4444'};
}
function localeForLangKey(lang) {
  return lang === 'th' ? 'th-TH' : lang === 'en' ? 'en-US' : 'nb-NO';
}
function localeForLang() {
  return localeForLangKey(appLang);
}
function ttsStreamUrl(text, lang) {
  var locale = lang ? localeForLangKey(lang) : localeForLang();
  return '/api/tts/stream?lang=' + encodeURIComponent(locale) + '&text=' + encodeURIComponent(text || '');
}

function applyUILang() {
  document.documentElement.lang = appLang === 'no' ? 'nb' : appLang;
  var metaDescription = document.getElementById('metaDescription');
  if (metaDescription) metaDescription.setAttribute('content', t('meta_description'));
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
  document.querySelectorAll('[data-label-key]').forEach(function(el) {
    var val = t(el.getAttribute('data-label-key'));
    if (val) {
      el.setAttribute('title', val);
      el.setAttribute('aria-label', val);
    }
  });
  document.querySelectorAll('[data-title-key]').forEach(function(el) {
    var val = t(el.getAttribute('data-title-key'));
    if (val) el.setAttribute('title', val.replace(/^\\S+\\s*/, ''));
  });
  // back buttons
  document.querySelectorAll('.back-btn').forEach(function(b){ b.textContent = t('back'); });
  // bottom nav
  var nb = document.getElementById('bnHome');      if(nb) nb.innerHTML = '<span class="bn-icon">' + NAV_SVG.home + '</span>' + t('home');
  var nc = document.getElementById('bnCats');      if(nc) nc.innerHTML = '<span class="bn-icon">' + NAV_SVG.cats + '</span>' + t('cats');
  var nh = document.getElementById('bnHistory');   if(nh) nh.innerHTML = '<span class="bn-icon">' + NAV_SVG.history + '</span>' + t('history');
  var nsg= document.getElementById('bnSigns');     if(nsg) nsg.innerHTML = '<span class="bn-icon">' + NAV_SVG.signs + '</span>' + t('signs');
  var nbm= document.getElementById('bnBookmarks'); if(nbm) nbm.innerHTML = '<span class="bn-icon">' + NAV_SVG.bookmarks + '</span>' + t('bookmarks');
  var ns = document.getElementById('bnSettings');  if(ns) ns.innerHTML = '<span class="bn-icon">' + NAV_SVG.settings + '</span>' + t('settings');
  var nt = document.getElementById('bnTeacher');   if(nt) nt.innerHTML = '<span class="bn-icon"><img src="/api/assets/michael_profile.jpg" style="width:30px;height:30px;border-radius:50%;object-fit:cover;object-position:center 15%;" alt="Michael"></span>' + t('teacher');
  var nsb= document.getElementById('bnStudybook'); if(nsb) nsb.innerHTML = '<span class="bn-icon">' + NAV_SVG.studybook + '</span>' + t('sb_nav');
  // Update teacher UI if visible
  var tNameEl = document.getElementById('teacherNameLbl');
  if (tNameEl) tNameEl.textContent = t('teacher_name');
  var tInput = document.getElementById('teacherInput');
  if (tInput) tInput.placeholder = t('teacher_placeholder');
  var tMore = document.getElementById('teacherMoreBtn');
  var tSuggestions = document.getElementById('teacherSuggestions');
  if (tMore) tMore.textContent = t(tSuggestions && tSuggestions.classList.contains('expanded') ? 'teacher_fewer_topics' : 'teacher_more_topics');
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
  // Update suggestion chip labels — no Norwegian fallback
  document.querySelectorAll('.teacher-chip').forEach(function(chip) {
    var lbl = chip.querySelector('.chip-lbl');
    if (!lbl) return;
    var msgKey   = 'data-msg-'   + appLang;
    var labelKey = 'data-label-' + appLang;
    var msg = chip.getAttribute(msgKey) || '';
    // Use data-label-* for display if present (math chips); otherwise strip emoji from msg
    var labelRaw = chip.getAttribute(labelKey) || msg;
    lbl.textContent = labelRaw.replace(/^[\u{1F000}-\u{1FFFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\uD800-\uDFFF❓📊📝📖🚗🛑🧮📏⚡🌧️]+\s*/u, '');
    chip.dataset.msg = msg;
  });
  // Update math section header label — no Norwegian fallback
  var mathHdr = document.getElementById('tcMathHdr');
  if (mathHdr) mathHdr.textContent = mathHdr.getAttribute('data-hdr-' + appLang) || '';
  // Update Studiebok tool strip labels
  var sbToolFk = document.getElementById('sbToolFkLabel');
  if (sbToolFk) sbToolFk.textContent = t('forbikjoring_label');
  // Re-render Forbikjøring if it's the active screen
  if (document.getElementById('screenForbikjoring') &&
      document.getElementById('screenForbikjoring').classList.contains('active')) {
    _fkUpdateStaticLabels();
    fkRender();
  }
  // cats header — update title text without disturbing the count span
  var catsTitleEl = document.querySelector('#screenCats .screen-title');
  if (catsTitleEl) {
    var catsCountEl = document.getElementById('catCount');
    var catsCountText = catsCountEl ? catsCountEl.textContent : '';
    catsTitleEl.innerHTML = '📚 <span data-key="cats">' + t('cats') + '</span> <span id="catCount">' + catsCountText + '</span>';
  }
  // home buttons
  document.querySelectorAll('.home-cta').forEach(function(b){ b.innerHTML = '<span data-key="home_primary_action">' + t('home_primary_action') + '</span>'; });
  // Oppdater horisontal scrollmeny-labels
  document.querySelectorAll('.hsm-label[data-hsm-key]').forEach(function(el) {
    var key = el.getAttribute('data-hsm-key');
    if (UI[key]) el.textContent = t(key);
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
  var er = document.querySelector('.end-btn-pri'); if(er) er.textContent = t('result_retry');
  var endSecBtns = document.querySelectorAll('.end-btn-sec');
  if (endSecBtns[0]) endSecBtns[0].textContent = t('home');
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
  // Premium banner (håndterer også gratisuken) + betalingsmurens undertekst
  renderPremiumBanner();
  renderPaywallSub();
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


var CAT_SVG = (function(){
  var s = 'stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" fill="none"';
  var h = function(d){ return '<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" '+s+' stroke-width="2.8">'+d+'</svg>'; };
  var speedSvg = h('<circle cx="24" cy="28" r="15"/><path d="M24 13V7M17 9l1.5 3M31 9l-1.5 3M11 20l2.5 1.5M37 20l-2.5 1.5"/><path d="M24 28L32 18" stroke-width="3"/><circle cx="24" cy="28" r="2.5" fill="currentColor" stroke="none"/>');
  return {
    'Speed Limits':     speedSvg,
    'fart_og_bremsing':  speedSvg,
    'Road Rules':       h('<rect x="14" y="6" width="20" height="28" rx="3"/><rect x="17" y="18" width="14" height="12" rx="2"/><circle cx="20.5" cy="21.5" r="2" fill="currentColor" stroke="none"/><circle cx="24" cy="21.5" r="2" fill="currentColor" stroke="none"/><circle cx="27.5" cy="21.5" r="2" fill="currentColor" stroke="none"/><line x1="17" y1="10" x2="31" y2="10"/><line x1="17" y1="14" x2="31" y2="14"/>'),
    'Traffic Signs':    h('<path d="M24 8L42 38H6Z"/><line x1="24" y1="18" x2="24" y2="28"/><circle cx="24" cy="32" r="1.5" fill="currentColor" stroke="none"/>'),
    'Right of Way':     h('<path d="M24 8L42 38H6Z"/><line x1="24" y1="18" x2="24" y2="28"/><circle cx="24" cy="32" r="1.5" fill="currentColor" stroke="none"/>'),
    'Traffic Rules':    h('<rect x="16" y="8" width="16" height="36" rx="8"/><circle cx="24" cy="17" r="4" fill="currentColor" stroke="none" opacity=".4"/><circle cx="24" cy="28" r="4" fill="currentColor" stroke="none" opacity=".4"/><circle cx="24" cy="38" r="4" fill="currentColor" stroke="none"/>'),
    'Situations':       h('<path d="M34 14a14 14 0 1 0 2 8"/><path d="M36 8v8h-8"/>'),
    'Safety':           h('<path d="M24 6l14 5v12c0 8-6 14-14 17C16 37 10 31 10 23V11Z"/><path d="M17 23l5 5 9-10"/>'),
    'Driving Conditions':h('<path d="M8 34a10 10 0 0 1 10-10 8 8 0 0 1 15-3 10 10 0 0 1 7 10"/><line x1="14" y1="38" x2="14" y2="43"/><line x1="20" y1="38" x2="20" y2="43"/><line x1="26" y1="38" x2="26" y2="43"/><line x1="32" y1="38" x2="32" y2="43"/>'),
    'Road Conditions':  h('<path d="M8 34a10 10 0 0 1 10-10 8 8 0 0 1 15-3 10 10 0 0 1 7 10"/><line x1="14" y1="38" x2="14" y2="43"/><line x1="20" y1="38" x2="20" y2="43"/><line x1="26" y1="38" x2="26" y2="43"/><line x1="32" y1="38" x2="32" y2="43"/>'),
    'Accidents':        h('<path d="M24 6l3 12h12l-10 7 4 13L24 30l-9 8 4-13L9 18h12Z"/>'),
    'Alcohol':          h('<path d="M18 8h12l-3 14a8 8 0 1 1-6 0Z"/><line x1="24" y1="36" x2="24" y2="44"/><line x1="18" y1="44" x2="30" y2="44"/>'),
    'Highway':          h('<path d="M4 40h40M12 40L16 8M36 40L32 8"/><line x1="24" y1="12" x2="24" y2="20"/><line x1="24" y1="26" x2="24" y2="34"/>'),
    'Intersections':    h('<line x1="24" y1="4" x2="24" y2="44"/><line x1="4" y1="24" x2="44" y2="24"/><circle cx="24" cy="24" r="5"/>'),
    'Parking':          h('<rect x="10" y="8" width="28" height="36" rx="4"/><path d="M19 24h6a5 5 0 0 0 0-10h-6v18"/><line x1="19" y1="24" x2="30" y2="24"/>'),
    'Vehicle':          h('<rect x="6" y="20" width="36" height="16" rx="4"/><path d="M12 20l4-10h16l4 10"/><circle cx="14" cy="36" r="5"/><circle cx="34" cy="36" r="5"/><rect x="28" y="14" width="8" height="6" rx="1"/>'),
    'Lights':           h('<path d="M24 8a10 10 0 0 1 10 10c0 5-3 8-4 10H18c-1-2-4-5-4-10A10 10 0 0 1 24 8Z"/><line x1="21" y1="28" x2="27" y2="28"/><line x1="22" y1="32" x2="26" y2="32"/><line x1="24" y1="4" x2="24" y2="6"/><line x1="10" y1="10" x2="12" y2="12"/><line x1="38" y1="10" x2="36" y2="12"/>'),
    'Tires':            h('<circle cx="24" cy="24" r="16"/><circle cx="24" cy="24" r="7"/><line x1="24" y1="8" x2="24" y2="17"/><line x1="24" y1="31" x2="24" y2="40"/><line x1="8" y1="24" x2="17" y2="24"/><line x1="31" y1="24" x2="40" y2="24"/>'),
    'Overtaking':       h('<rect x="4" y="22" width="18" height="10" rx="3"/><circle cx="9" cy="32" r="3"/><circle cx="17" cy="32" r="3"/><rect x="26" y="14" width="18" height="10" rx="3"/><circle cx="31" cy="24" r="3"/><circle cx="39" cy="24" r="3"/><path d="M28 22l-8-8"/>'),
    'Pedestrians':      h('<circle cx="24" cy="10" r="5"/><path d="M24 16v14M17 22h14M20 30l-4 12M28 30l4 12"/>'),
    'Environment':      h('<path d="M24 40V22"/><path d="M24 22a12 12 0 0 0 12-12 12 12 0 0 0-12 12Z"/><path d="M24 30a10 10 0 0 1-10-10 10 10 0 0 1 10 10Z"/>'),
    'Hazardous Goods':  h('<circle cx="24" cy="24" r="17"/><path d="M24 14v12M17 26l6-12 6 12M14 30h20"/>'),
    'Fellesskjøring':   h('<circle cx="16" cy="20" r="6"/><circle cx="32" cy="20" r="6"/><path d="M10 36a6 6 0 0 1 12 0M26 36a6 6 0 0 1 12 0"/>'),
    'Lastsikring':      h('<rect x="8" y="20" width="32" height="18" rx="3"/><path d="M16 20v-8a8 8 0 0 1 16 0v8"/><path d="M8 32h32"/><circle cx="24" cy="32" r="3"/>'),
    'Gangfelt':         h('<line x1="8" y1="36" x2="40" y2="36"/><line x1="8" y1="28" x2="40" y2="28"/><circle cx="24" cy="10" r="5"/><path d="M24 16v12M17 22h14M20 28l-4 8M28 28l4 8"/>'),
    'Motorvei':         h('<path d="M4 40h40M12 40L16 8M36 40L32 8"/><line x1="24" y1="12" x2="24" y2="20"/><line x1="24" y1="26" x2="24" y2="34"/>'),
    'Kryss':            h('<line x1="24" y1="4" x2="24" y2="44"/><line x1="4" y1="24" x2="44" y2="24"/><circle cx="24" cy="24" r="5"/>'),
    'default':          h('<rect x="10" y="8" width="28" height="36" rx="3"/><line x1="16" y1="18" x2="32" y2="18"/><line x1="16" y1="24" x2="32" y2="24"/><line x1="16" y1="30" x2="26" y2="30"/>')
  };
})();

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

var CAT_ALIASES = {
  'สิทธิการผ่านทาง': 'Right of Way',
  'Alle kategorier': '',
  'ทุกหมวดหมู่': '',
  'All Categories': ''
};

var _CAT_REV = (function() {
  var rev = {};
  function add(raw, key) {
    if (typeof raw !== 'string') return;
    var s = raw.trim();
    if (!s) return;
    rev[s] = key;
    rev[s.toLowerCase()] = key;
  }
  Object.keys(CAT_NAMES).forEach(function(key) {
    var entry = CAT_NAMES[key] || {};
    add(key, key);
    add(entry.no, key);
    add(entry.th, key);
    add(entry.en, key);
  });
  Object.keys(CAT_ALIASES).forEach(function(alias) {
    add(alias, CAT_ALIASES[alias]);
  });
  return rev;
})();

function catKey(raw) {
  if (raw === null || raw === undefined) return '';
  var s = String(raw).trim();
  if (!s) return '';
  return _CAT_REV[s] || _CAT_REV[s.toLowerCase()] || '';
}

function catName(raw) {
  var key = catKey(raw);
  if (!key) {
    if (raw !== null && raw !== undefined && String(raw).trim()) console.warn('[i18n] unknown category', raw);
    return '';
  }
  var entry = CAT_NAMES[key];
  if (!entry) {
    console.warn('[i18n] missing CAT_NAMES entry', key);
    return '';
  }
  return pickStrict(entry) || missingText();
}

var PREMIUM_PRICING = {
  monthly: { display:'199 NOK', period:{no:'per måned', th:'ต่อเดือน', en:'per month'} },
  three_months: { display:'399 NOK', period:{no:'per 3 måneder', th:'ต่อ 3 เดือน', en:'per 3 months'} },
  lifetime: { display:'699 NOK', period:{no:'engangsbetaling', th:'จ่ายครั้งเดียว', en:'one-time payment'} }
};

// ════════════════════════════════════════════
//  INIT
// ════════════════════════════════════════════
(async function init() {
  applyThemeFromStorage();
  applyUILang();
  loadPremiumPricing();
  // Init top bar + innloggingsskjermens språkknapper
  ['TH','NO','EN'].forEach(function(l) {
    var topBtn = document.getElementById('topLang' + l);
    if (topBtn) topBtn.classList.toggle('active', appLang === l.toLowerCase());
    var authBtn = document.getElementById('authLang' + l);
    if (authBtn) authBtn.classList.toggle('active', appLang === l.toLowerCase());
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
  if (id !== 'screenQuiz') closeMichaelQuizCoach();
  document.querySelectorAll('.screen').forEach(function(s) { s.classList.remove('active'); });
  var el = document.getElementById(id);
  if (el) el.classList.add('active');
  // Toggle app-level mode classes — expands phone frame on desktop
  var app = document.getElementById('app');
  app.classList.toggle('quiz-mode', id === 'screenQuiz');
  app.classList.toggle('teacher-mode', id === 'screenTeacher');
  app.classList.toggle('fk-mode', id === 'screenForbikjoring');
}

function enterApp() {
  document.getElementById('topBar').style.display = 'flex';
  document.getElementById('bottomNav').style.display = 'flex';
  document.getElementById('topSettingsBtn').style.display = 'flex';
  loadAccessStatus();
  showTab('home');
  setTimeout(maybeShowTrialNotice, 1200);
}

function showTab(tab, forceType) {
  // Close video player if active
  var vpScreen = document.getElementById('screenVideoPlayer');
  if (vpScreen && vpScreen.classList.contains('active')) closeVideoPlayer();
  stopAllSpeech();
  activeTab = tab;
  document.querySelectorAll('.bn-tab').forEach(function(b) { b.classList.remove('active'); });
  var tabMap = { home:'bnHome', cats:'bnCats', history:'bnHistory', signs:'bnSigns', studybook:'bnStudybook', bookmarks:'bnBookmarks', settings:'bnSettings', teacher:'bnTeacher' };
  if (tabMap[tab]) {
    var btn = document.getElementById(tabMap[tab]);
    btn.classList.add('active');
    btn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  }
  var screenMap = {
    home:'screenHome', cats:'screenCats',
    history:'screenHistory', signs:'screenSigns', bookmarks:'screenBookmarks',
    settings:'screenSettings', studybook:'screenStudybook', teacher:'screenTeacher',
    library:'screenLibrary'
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
    if (tab === 'library')   loadLibrary();
    if (tab === 'teacher') {
      if (forceType) {
        switchTeacherSession(forceType);
      } else {
        switchTeacherSession('normal');
      }
      loadTeacher();
    }
  }
}

function toggleChapter(id) {
  var ch = document.getElementById(id);
  if (ch) ch.classList.toggle('open');
}

// ════════════════════════════════════════════
//  LIBRARY SCREEN — VIDEOS & PODCASTS
// ════════════════════════════════════════════
var _videosCached = null;
var _podcastsCached = null;
var _libraryActiveTab = 'videos';

async function loadLibrary() {
  var container = document.getElementById('libraryContent');
  if (!container) return;

  if (_libraryActiveTab === 'micro') {
    renderLibrary();
    return;
  }

  if (_videosCached && _podcastsCached) {
    renderLibrary();
    return;
  }

  container.innerHTML = '<div class="loading-wrap"><div class="spinner"></div></div>';
  try {
    var pVideo = api('GET', '/api/videos/for-topic?limit=50');
    var pPodcast = api('GET', '/api/podcasts/for-topic?limit=50');

    var res = await Promise.all([pVideo, pPodcast]);
    var dVideo = res[0];
    var dPodcast = res[1];

    _videosCached = dVideo.videos || dVideo || [];
    _podcastsCached = dPodcast.podcasts || dPodcast || [];

    renderLibrary();
  } catch(e) {
    container.innerHTML = '<div style="padding:24px;text-align:center;color:var(--muted);">' + escH(t('lib_load_failed')) + '</div>';
  }
}

function renderLibrary() {
  var container = document.getElementById('libraryContent');
  if (!container) return;

  if (_libraryActiveTab === 'micro') {
    renderMicroLessons(container);
    return;
  }

  var items = _libraryActiveTab === 'videos' ? _videosCached : _podcastsCached;
  if (!items || items.length === 0) {
    container.innerHTML = '<div class="empty-state" style="padding:40px;text-align:center;color:var(--muted);">' + escH(t('empty_no_content')) + '</div>';
    return;
  }

  var html = '';
  var cardCount = 0;
  if (_libraryActiveTab === 'videos') {
    html += '<div class="library-grid">';
    items.forEach(function(v) {
      try {
        var card = buildVideoCard(v);
        if (card) { html += card; cardCount++; }
      } catch(e) { console.error('Video card error:', e); }
    });
    html += '</div>';
  } else {
    html += '<div class="library-list">';
    items.forEach(function(p) {
      try {
        var card = buildPodcastCard(p);
        if (card) { html += card; cardCount++; }
      } catch(e) { console.error('Podcast card error:', e); }
    });
    html += '</div>';
  }
  if (cardCount === 0) {
    container.innerHTML = '<div class="empty-state" style="padding:40px;text-align:center;color:var(--muted);">' + escH(t('empty_no_content')) + '</div>';
  } else {
    container.innerHTML = html;
  }
}

function setLibraryTab(tab) {
  _libraryActiveTab = tab;
  document.querySelectorAll('.lib-tab').forEach(function(b) {
    b.classList.toggle('active', b.getAttribute('data-tab') === tab);
  });
  renderLibrary();
}

function renderMicroLessons(container) {
  var lessons = [
    {id:'road-side', icon:'↔️', title:'micro_road_side_title', body:'micro_road_side_body', action:'micro_road_side_action'},
    {id:'yield', icon:'🔺', title:'micro_yield_title', body:'micro_yield_body', action:'micro_yield_action'},
    {id:'winter', icon:'❄️', title:'micro_winter_title', body:'micro_winter_body', action:'micro_winter_action'},
    {id:'roundabout', icon:'🔄', title:'micro_roundabout_title', body:'micro_roundabout_body', action:'micro_roundabout_action'}
  ];
  var html = '<p class="micro-intro">' + escH(t('micro_intro')) + '</p><div class="micro-lessons">';
  lessons.forEach(function(lesson) {
    html += '<article class="micro-lesson" id="micro-' + lesson.id + '">' +
      '<button class="micro-lesson-btn" type="button" onclick="toggleMicroLesson(\'' + lesson.id + '\')" aria-expanded="false">' +
      '<span class="micro-lesson-icon">' + lesson.icon + '</span>' +
      '<span class="micro-lesson-title">' + escH(t(lesson.title)) + '</span>' +
      '<span class="micro-lesson-chevron">⌄</span></button>' +
      '<div class="micro-lesson-body"><div>' + escH(t(lesson.body)) + '</div>' +
      '<div class="micro-lesson-action">✓ ' + escH(t(lesson.action)) + '</div></div></article>';
  });
  container.innerHTML = html + '</div>';
}

function toggleMicroLesson(id) {
  var card = document.getElementById('micro-' + id);
  if (!card) return;
  var open = card.classList.toggle('open');
  var button = card.querySelector('.micro-lesson-btn');
  if (button) button.setAttribute('aria-expanded', open ? 'true' : 'false');
}

function toggleTargetPracticeMenu() {
  var menu = document.getElementById('targetPracticeMenu');
  var toggle = document.getElementById('targetPracticeToggle');
  if (!menu) return;
  var open = menu.classList.toggle('open');
  if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
}

// ════════════════════════════════════════════
//  VIDEO PLAYER — The Road Ahead
// ════════════════════════════════════════════
var _currentVideo = null;
var _vpWaypoints = [];
var _vpKnowledgeIds = [];
var _vpTimer = null;

function openVideoPlayer(filePath) {
  // Find video in cache
  var v = null;
  if (_videosCached) {
    for (var i = 0; i < _videosCached.length; i++) {
      var c = _videosCached[i];
      if (c.file_path === filePath || c.youtube_url === filePath) { v = c; break; }
    }
  }
  if (!v) return;

  _currentVideo = v;
  _vpKnowledgeIds = [];

  // Title
  var title = (v['title_' + appLang] || '');
  document.getElementById('vpTitle').textContent = title;

  // Build waypoints from topic_tags
  var tags = v.topic_tags || [];
  var dur = v.duration_seconds || 60;
  _vpWaypoints = [];
  if (tags.length) {
    var seg = dur / tags.length;
    tags.forEach(function(t, i) {
      _vpWaypoints.push({ time: Math.round(seg * i), label: t, shown: false, index: i });
    });
  }
  // Always add an end waypoint
  _vpWaypoints.push({ time: dur, label: '', shown: false, index: _vpWaypoints.length });

  // Build Glow Road
  buildGlowRoad();

  // Set video source
  var vid = document.getElementById('vpVideo');
  var rawPath = v.file_path || '';
  if (rawPath && rawPath.indexOf('/public_assets/') === 0) {
    rawPath = '/api/assets/' + rawPath.substring('/public_assets/'.length);
  }
  if (rawPath) {
    vid.src = rawPath;
  } else if (v.youtube_url) {
    vid.innerHTML = '<iframe src="https://www.youtube.com/embed/' + _extractYtId(v.youtube_url) + '?autoplay=1" style="width:100%;aspect-ratio:16/9" frameborder="0" allow="autoplay;encrypted-media" allowfullscreen></iframe>';
    vid.style.display = 'none';
  }

  // Reset knowledge area
  document.getElementById('vpKnowledge').innerHTML = '<div style="text-align:center;color:var(--muted);padding:12px;font-size:.8rem">🧠 Kunnskapskort dukker opp underveis</div>';
  document.getElementById('vpMiniCheck').style.display = 'none';

  // Time update listener
  if (vid) {
    vid.ontimeupdate = onVpTimeUpdate;
    vid.onended = onVpEnded;
    vid.onplay = function() { startVpTimer(); };
    vid.onpause = function() { stopVpTimer(); };
  }

  showScreen('screenVideoPlayer');
  // Hide bottom nav for full player experience
  document.getElementById('bottomNav').style.display = 'none';
}

function closeVideoPlayer() {
  stopVpTimer();
  var vid = document.getElementById('vpVideo');
  if (vid) { vid.pause(); vid.src = ''; vid.ontimeupdate = null; vid.onended = null; vid.onplay = null; vid.onpause = null; }
  _currentVideo = null;
  document.getElementById('bottomNav').style.display = 'flex';
  showScreen('screenLibrary');
}

function _extractYtId(url) {
  if (!url) return '';
  var m = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/);
  return m ? m[1] : '';
}

function buildGlowRoad() {
  var road = document.getElementById('vpGlowRoad');
  if (!road) return;
  var html = '<div class="vp-glow-track">';
  _vpWaypoints.forEach(function(wp, i) {
    if (wp.index === _vpWaypoints.length - 1) return; // skip end marker in visual
    var label = wp.label ? wp.label.substring(0, 12) : '';
    html += '<div class="vp-glow-dot-wrap">'
      + '<div class="vp-glow-dot" id="vpDot' + i + '" title="' + escH(wp.label) + '" onclick="seekToWaypoint(' + i + ')"></div>'
      + (label ? '<div class="vp-glow-label">' + escH(label) + '</div>' : '')
      + '</div>';
  });
  html += '</div>';
  road.innerHTML = html;
}

function seekToWaypoint(idx) {
  var wp = _vpWaypoints[idx];
  if (!wp) return;
  var vid = document.getElementById('vpVideo');
  if (vid && vid.duration) { vid.currentTime = wp.time; vid.play(); }
}

function onVpTimeUpdate() {
  var vid = document.getElementById('vpVideo');
  if (!vid || !vid.duration) return;
  var t = vid.currentTime;
  var dur = vid.duration;

  // Update glow dots
  _vpWaypoints.forEach(function(wp, i) {
    if (wp.index === _vpWaypoints.length - 1) return;
    var dot = document.getElementById('vpDot' + i);
    if (!dot) return;
    var wpEnd = _vpWaypoints[i + 1] ? _vpWaypoints[i + 1].time : dur;
    if (t >= wpEnd) {
      dot.className = 'vp-glow-dot passed';
    } else if (t >= wp.time) {
      dot.className = 'vp-glow-dot active';
      // Show knowledge card if not shown yet
      if (!wp.shown && wp.label) {
        wp.shown = true;
        showKnowledgeCard(wp);
      }
    } else {
      dot.className = 'vp-glow-dot';
    }
  });
}

// Kunnskapskort i videospilleren — full tre-språks-dekning, ingen fallback.
// Mangler emnet eller det aktive språket, vises ingen kort (Fail-Stop).
var VP_TOPICS = {
  'vikeplikt': {
    title: {th:'การให้ทาง', no:'Vikeplikt', en:'Yielding'},
    body: {th:'ใครต้องให้ทาง? นึกถึงกฎรถทางขวา ถนนสายหลัก และป้ายจราจร',
           no:'Hvem har vikeplikt? Tenk på høyregelen, forkjørsvei og skilting.',
           en:'Who has to yield? Think of the right-hand rule, priority roads, and signs.'}},
  'fartsgrenser': {
    title: {th:'จำกัดความเร็ว', no:'Fartsgrenser', en:'Speed limits'},
    body: {th:'ความเร็วต้องเหมาะกับสภาพถนน ทัศนวิสัย และการจราจรเสมอ',
           no:'Farten skal alltid tilpasses føre-, sikt- og trafikkforholdene.',
           en:'Speed must always match road, visibility, and traffic conditions.'}},
  'skilt': {
    title: {th:'ป้ายจราจร', no:'Skilt', en:'Road signs'},
    body: {th:'ป้ายจราจรบอกข้อบังคับ ข้อห้าม และคำแนะนำ เรียนรู้กลุ่มของป้ายให้ดี',
           no:'Trafikkskilt gir deg påbud, forbud og veiledning. Lær deg gruppene!',
           en:'Road signs give orders, prohibitions, and guidance. Learn the groups!'}},
  'forbikjøring': {
    title: {th:'การแซง', no:'Forbikjøring', en:'Overtaking'},
    body: {th:'แซงทางด้านซ้ายเสมอ ตรวจทัศนวิสัยและความเร็วก่อนแซง',
           no:'Forbikjøring skal skje til venstre. Sjekk sikt og fart før du kjører forbi.',
           en:'Overtake on the left. Check visibility and speed before you pass.'}},
  'parkering': {
    title: {th:'การจอดรถ', no:'Parkering', en:'Parking'},
    body: {th:'การจอดคือการทิ้งรถไว้ ยกเว้นการหยุดชั่วครู่ที่สั้นที่สุด',
           no:'Parkering er all hensetting av kjøretøy. Unntak: kortest mulig stans.',
           en:'Parking is leaving the vehicle standing. Exception: the shortest possible stop.'}},
  'rygging': {
    title: {th:'การถอยรถ', no:'Rygging', en:'Reversing'},
    body: {th:'ผู้ที่ถอยรถต้องให้ทางแก่การจราจรอื่นทั้งหมด',
           no:'Den som rygger har vikeplikt for all annen trafikk.',
           en:'Whoever reverses must yield to all other traffic.'}},
  'motorvei': {
    title: {th:'ทางด่วน', no:'Motorvei', en:'Motorway'},
    body: {th:'บนทางด่วน: รักษาความเร็ว ใช้เลนขวา ห้ามถอยหรือกลับรถ',
           no:'På motorvei: hold farten, bruk høyre felt, ingen rygging eller vending.',
           en:'On the motorway: keep your speed, use the right lane, no reversing or turning.'}},
  'alkohol': {
    title: {th:'แอลกอฮอล์', no:'Alkohol', en:'Alcohol'},
    body: {th:'0.2 โปรมิลล์คือขีดจำกัดตามกฎหมาย ห้ามดื่มก่อนขับรถ',
           no:'0,2 promille er lovens grense. Ingen alkohol før du kjører!',
           en:'0.2 per mille is the legal limit. No alcohol before you drive!'}},
  'gangfelt': {
    title: {th:'ทางม้าลาย', no:'Gangfelt', en:'Pedestrian crossing'},
    body: {th:'ต้องให้ทางแก่คนเดินเท้าที่อยู่บนทางม้าลายหรือกำลังก้าวลงมา',
           no:'Vikeplikt for gående som er i gangfeltet eller på vei ut i det.',
           en:'Yield to pedestrians on the crossing or about to step onto it.'}},
  'sikkerhet': {
    title: {th:'ความปลอดภัย', no:'Sikkerhet', en:'Safety'},
    body: {th:'เข็มขัดนิรภัยเป็นข้อบังคับสำหรับทุกคน ยึดสิ่งของที่หลวมให้แน่นก่อนขับ',
           no:'Bilbelte er påbudt for alle. Sikre løse gjenstander før kjøring.',
           en:'Seat belts are mandatory for everyone. Secure loose objects before driving.'}}
};

function showKnowledgeCard(wp) {
  // Fail-Stop: ukjent emne eller manglende oversettelse → vis ingenting.
  var topic = VP_TOPICS[(wp.label || '').toLowerCase()];
  if (!topic) return;
  var body  = pickStrict(topic.body);
  var title = pickStrict(topic.title);
  if (!body || !title) return;

  var area = document.getElementById('vpKnowledge');
  if (!area) return;
  // Remove placeholder
  var placeholder = area.querySelector('div[style]');
  if (placeholder && !_vpKnowledgeIds.length) area.innerHTML = '';

  var id = 'kc' + Date.now() + Math.random().toString(36).substr(2,3);
  _vpKnowledgeIds.push(id);

  var html = '<div class="vp-knowledge-card" id="' + id + '">'
    + '<div class="vp-kc-title">📍 ' + escH(title) + '</div>'
    + '<div class="vp-kc-body">' + escH(body) + '</div>'
    + '</div>';
  area.insertAdjacentHTML('beforeend', html);

  // Auto-fade after 5s
  setTimeout(function() {
    var el = document.getElementById(id);
    if (el) { el.classList.add('fading'); setTimeout(function() { if (el) el.remove(); }, 500); }
  }, 5000);
}

function startVpTimer() {
  stopVpTimer();
  _vpTimer = setInterval(function() {
    var vid = document.getElementById('vpVideo');
    if (!vid || !vid.duration || vid.paused) return;
    onVpTimeUpdate();
  }, 500);
}

function stopVpTimer() {
  if (_vpTimer) { clearInterval(_vpTimer); _vpTimer = null; }
}

function onVpEnded() {
  // Show mini-check
  var tags = _currentVideo ? (_currentVideo.topic_tags || []) : [];
  // topic_tags er norske nøkler fra backend. Slå dem opp i VP_TOPICS for å få
  // emnenavnet på aktivt språk; finnes det ikke, still spørsmålet uten emne.
  var tEntry = tags.length ? VP_TOPICS[String(tags[0]).toLowerCase()] : null;
  var topicName = tEntry ? pickStrict(tEntry.title) : '';
  var question = topicName ? tf('vp_mc_q_topic', {topic: topicName}) : t('vp_mc_q_generic');
  var html = '<div class="vp-mc-question">🤔 ' + escH(question) + '</div>'
    + '<div class="vp-mc-options">'
    + '<button class="vp-mc-btn" onclick="answerMiniCheck(this,true)">' + escH(t('vp_mc_yes')) + '</button>'
    + '<button class="vp-mc-btn" onclick="answerMiniCheck(this,false)">' + escH(t('vp_mc_no')) + '</button>'
    + '</div>'
    + '<div class="vp-mc-result" id="vpMcResult"></div>';
  var mc = document.getElementById('vpMiniCheck');
  mc.innerHTML = html;
  mc.style.display = 'block';
  mc.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function answerMiniCheck(btn, correct) {
  document.querySelectorAll('.vp-mc-btn').forEach(function(b) { b.disabled = true; });
  btn.classList.add(correct ? 'correct' : 'wrong');
  var result = document.getElementById('vpMcResult');
  if (result) {
    if (correct) {
      result.innerHTML = escH(t('vp_mc_correct'));
    } else {
      result.innerHTML = escH(t('video_retry_hint'));
    }
  }
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
    var title = ch['title_' + appLang] || '';
    d.title = title;
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

  var title = ch['title_' + appLang] || '';
  var content = ch['content_' + appLang] || ('<div class="sb-empty-lang" style="padding:24px;text-align:center;color:var(--muted);font-style:italic;">' + t('sb_not_available') + '</div>');

  // Nav info
  var info = document.getElementById('sbNavInfo');
  if (info) info.textContent = (title ? title.split('—')[0].trim() : '') + '  ·  ' + (_sbCurrent + 1) + ' / ' + total;

  // Prev / Next buttons
  var prev = document.getElementById('sbPrevBtn');
  var next = document.getElementById('sbNextBtn');
  if (prev) prev.disabled = (_sbCurrent === 0);
  if (next) next.disabled = (_sbCurrent === total - 1);

  // Dots
  var dots = document.querySelectorAll('.sb-dot');
  dots.forEach(function(d, i) {
    var otherCh = _sbChapters[i];
    var otherTitle = otherCh ? (otherCh['title_' + appLang] || '') : '';
    d.className = 'sb-dot' + (i === _sbCurrent ? ' active' : (_sbVisited[i] ? ' visited' : ''));
    d.title = otherTitle;
  });

  // Edit button (admin only)
  var editBtn = (user && user.is_admin)
    ? '<button class="sb-edit-btn" onclick="openStudiebokModal(' + ch.order + ')" title="Rediger">✏️</button>'
    : '';

  var imgHtml = ch.image_url ? '<img src="' + escH(ch.image_url) + '" class="study-img" alt="' + escH(title) + '">' : '';
  var vidHtml = ch.video_url
    ? '<div><a class="sb-video-btn" href="' + escH(ch.video_url) + '" target="_blank" rel="noopener">🎬 ' + escH(t('sb_watch_video')) + '</a></div>'
    : '';

  var reader = document.getElementById('sbReader');
  reader.innerHTML =
    '<div class="sb-page">' +
      editBtn +
      '<div class="sb-page-icon">' + ch.icon + '</div>' +
      '<div class="sb-page-title">' + title + '</div>' +
      '<div class="sb-page-body">' + imgHtml + content + '</div>' +
      vidHtml +
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
      var title = ch['title_' + appLang] || '';
      var content = ch['content_' + appLang] || '';
      return title.toLowerCase().includes(lq) ||
             content.toLowerCase().replace(/<[^>]+>/g,'').includes(lq);
    });
  }

  if (!matches.length) {
    box.innerHTML = '<div class="sb-result-item" style="color:var(--muted)">' + t('studybook_no_results') + '</div>';
    box.style.display = 'block'; return;
  }

  box.innerHTML = matches.slice(0, 6).map(function(ch) {
    var title = ch['title_' + appLang] || '';
    var content = ch['content_' + appLang] || '';
    var plain = content.replace(/<[^>]+>/g,'').substring(0, 80) + '…';
    return '<div class="sb-result-item" onclick="sbGoTo(' + (_sbChapters.indexOf(ch)) + ')">' +
           '<span class="sb-result-icon">' + ch.icon + '</span>' +
           '<div><div class="sb-result-title">' + title + '</div>' +
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

var _backendAudio = null;
var _teacherAudio = null;
var _audioUnlocked = false;
var _teacherActiveText = '';
var _teacherAudioToken = 0;

// iOS/Safari lar deg bare starte lyd fra et ekte brukertrykk. Et <audio>-element som
// aldri har spilt inne i en gest, nekter senere .play() — og det er derfor lyden er
// stille selv om /api/tts svarer. Vi lager derfor begge elementene tidlig og «velsigner»
// dem med en stum WAV ved første trykk. AudioContext.resume() dekker IKKE dette; den
// gjelder kun WebAudio-pipet i playSound().
var _SILENT_WAV = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA';

function _ensureBackendAudio() {
  if (!_backendAudio) {
    _backendAudio = new Audio();
    _backendAudio.preload = 'auto';
    _backendAudio.onended = function() { ttsPlaying = false; updateTtsBtn(false); };
    _backendAudio.onerror = function() { ttsPlaying = false; updateTtsBtn(false); };
  }
  return _backendAudio;
}

function _ensureTeacherAudio() {
  if (!_teacherAudio) {
    _teacherAudio = new Audio();
    _teacherAudio.preload = 'auto';
    _teacherAudio.onended = function() {
      _teacherTtsPlaying = false;
      _teacherActiveText = '';
    };
    _teacherAudio.onerror = function() {
      _teacherTtsPlaying = false;
      _teacherActiveText = '';
    };
  }
  return _teacherAudio;
}

function _primeAudioEl(el) {
  if (!el) return;
  try {
    el.src = _SILENT_WAV;
    var primedSrc = el.src;
    el.muted = true;
    var p = el.play();
    if (p && p.then) {
      p.then(function() {
        // The user action may already have replaced the silent WAV with real
        // TTS. Never let the async priming callback pause that new source.
        if (el.src === primedSrc) {
          try { el.pause(); el.currentTime = 0; } catch (e) {}
        }
        el.muted = false;
      }).catch(function() { el.muted = false; });
    } else {
      try { el.pause(); } catch (e) {}
      el.muted = false;
    }
  } catch (e) {
    el.muted = false;
  }
}

function _unlockAudioPlayback(activeEl) {
  if (_audioUnlocked) return;
  _audioUnlocked = true;
  var backendEl = _ensureBackendAudio();
  var teacherEl = _ensureTeacherAudio();
  // The element started by this exact user gesture does not need priming.
  // Priming it here can race with the real MP3 and abort play() via pause().
  if (backendEl !== activeEl) _primeAudioEl(backendEl);
  if (teacherEl !== activeEl) _primeAudioEl(teacherEl);
  if (typeof _getAudioCtx === 'function') { try { _getAudioCtx(); } catch (e) {} }
}

// Første ekte brukergest på siden låser opp all lyd — begge <audio>-elementene og
// WebAudio-konteksten. `once` gjør at det skjer nøyaktig én gang.
document.addEventListener('touchstart', _unlockAudioPlayback, { once: true, passive: true });
document.addEventListener('click', _unlockAudioPlayback, { once: true });
document.addEventListener('keydown', _unlockAudioPlayback, { once: true });

function stopAllSpeech() {
  _teacherAudioToken += 1;
  if (_backendAudio) { try { _backendAudio.pause(); } catch(e){} }
  if (_teacherAudio) { try { _teacherAudio.pause(); } catch(e){} }
  _teacherTtsPlaying = false;
  _teacherActiveText = '';
  ttsPlaying = false;
  if (typeof updateTtsBtn === 'function') { try { updateTtsBtn(false); } catch (e) {} }
}
window.addEventListener('pagehide', stopAllSpeech);
window.addEventListener('beforeunload', stopAllSpeech);
document.addEventListener('visibilitychange', function() {
  if (document.hidden) stopAllSpeech();
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
  document.getElementById('sbEditTitle').value      = ch.title_no || '';
  document.getElementById('sbEditContent').value    = ch.content_no || '';
  document.getElementById('sbEditTitleTh').value    = ch.title_th || '';
  document.getElementById('sbEditContentTh').value  = ch.content_th || '';
  document.getElementById('sbEditTitleEn').value    = ch.title_en || '';
  document.getElementById('sbEditContentEn').value  = ch.content_en || '';
  document.getElementById('sbEditImageUrl').value   = ch.image_url || '';
  document.getElementById('sbEditVideoUrl').value   = ch.video_url || '';
  document.getElementById('studiebokEditModal').style.display = 'flex';
}

function closeStudiebokModal() {
  document.getElementById('studiebokEditModal').style.display = 'none';
  _sbEditOrder = null;
}

async function saveStudiebokChapter() {
  if (!_sbEditOrder) return;
  var title_no    = document.getElementById('sbEditTitle').value.trim();
  var content_no  = document.getElementById('sbEditContent').value.trim();
  var title_th    = document.getElementById('sbEditTitleTh').value.trim();
  var content_th  = document.getElementById('sbEditContentTh').value.trim();
  var title_en    = document.getElementById('sbEditTitleEn').value.trim();
  var content_en  = document.getElementById('sbEditContentEn').value.trim();
  var image_url   = document.getElementById('sbEditImageUrl').value.trim();
  var video_url   = document.getElementById('sbEditVideoUrl').value.trim();
  if (!title_no || !content_no) { toast(t('sb_empty_fields')); return; }
  try {
    await api('PUT', '/api/studiebok/' + _sbEditOrder, {
      title_no, content_no,
      title_th, content_th,
      title_en, content_en,
      image_url, video_url
    });
    // Update local cache
    var idx = _sbChapters.findIndex(function(c) { return c.order === _sbEditOrder; });
    if (idx >= 0) {
      _sbChapters[idx].title_no = title_no;
      _sbChapters[idx].content_no = content_no;
      _sbChapters[idx].title_th = title_th;
      _sbChapters[idx].content_th = content_th;
      _sbChapters[idx].title_en = title_en;
      _sbChapters[idx].content_en = content_en;
      _sbChapters[idx].image_url = image_url;
      _sbChapters[idx].video_url = video_url;
    }
    closeStudiebokModal();
    sbRender();
    toast(t('saved_chapter'));
  } catch(e) {
    toast(t('error_prefix') + e.message);
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
      msg = pickStrict(det) || (det.key ? t(det.key) : '') || t('generic_error');
    } else if (Array.isArray(det)) {
      msg = det.map(function(d){return d.msg||d;}).join(', ');
    } else {
      msg = t('generic_error');
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
      toast(t('premium_activated_toast'), 4500);
    }
  } catch(e) {
    toast(t('payment_unconfirmed_toast'), 5000);
  }
  window.history.replaceState({}, '', window.location.pathname);
  return true;
}

function renderPremiumPricing() {
  Object.keys(PREMIUM_PRICING || {}).forEach(function(planId) {
    var plan = PREMIUM_PRICING[planId] || {};
    var priceEl = document.querySelector('[data-price-plan="' + planId + '"]');
    if (priceEl) priceEl.textContent = plan.display || priceEl.textContent;
    var card = document.querySelector('[data-plan="' + planId + '"]');
    if (!card) return;
    var labelEl = card.querySelector('.ppc-period');
    if (labelEl) labelEl.textContent = pickStrict(plan.label) || t(labelEl.getAttribute('data-key'));
    var periodEl = card.querySelector('.ppc-per');
    if (periodEl) periodEl.textContent = t(periodEl.getAttribute('data-key')) || pickStrict(plan.period) || periodEl.textContent;
    var badgeEl = card.querySelector('.ppc-badge');
    if (badgeEl) badgeEl.textContent = t(badgeEl.getAttribute('data-key'));
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
  var lbl = t('toggle_password');
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
  document.getElementById('topBar').style.display = 'flex';
  document.getElementById('bottomNav').style.display = 'none';
  document.getElementById('topSettingsBtn').style.display = 'none';
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

  // Persistent mistake-bank count for registered users.
  var mistakeCount = document.getElementById('mistakesHomeCount');
  if (mistakeCount) mistakeCount.textContent = '';
  if (token) {
    try {
      var mistakeData = await api('GET', '/api/quiz/mistakes?limit=100&_=' + Date.now());
      var activeMistakes = Number(mistakeData.count || 0);
      if (mistakeCount) mistakeCount.textContent = tf('mistakes_count', {count: activeMistakes});
    } catch(e) {
      console.warn('Mistake count load failed:', e.message);
    }
  }

  // Deterministic readiness for registered users: 70% recent accuracy,
  // 30% mastery in the persistent mistake bank.
  var readinessCard = document.getElementById('homeReadiness');
  if (readinessCard) readinessCard.style.display = 'none';
  if (token) {
    try {
      var readiness = await api('GET', '/api/user/readiness?_=' + Date.now());
      var rScore = Math.max(0, Math.min(100, Number(readiness.score || 0)));
      var rState = rScore >= 85
        ? {cls:'good', key:'readiness_ready', color:'var(--green)'}
        : rScore >= 60
          ? {cls:'ok', key:'readiness_close', color:'var(--orange)'}
          : {cls:'bad', key:'readiness_keep', color:'#EF4444'};
      document.getElementById('hrDot').className = 'hr-dot hr-dot-' + rState.cls;
      document.getElementById('hrStatus').textContent = t(rState.key);
      document.getElementById('hrSub').textContent = tf('readiness_breakdown', {
        accuracy: Math.round(Number(readiness.recent_accuracy || 0)),
        mastery: Math.round(Number(readiness.mistake_mastery || 0))
      });
      document.getElementById('hrPct').textContent = rScore + '%';
      document.getElementById('hrPct').style.color = rState.color;
      var gauge = document.getElementById('hrGaugeFill');
      if (gauge) { gauge.style.width = rScore + '%'; gauge.style.background = rState.color; }
      if (readinessCard) readinessCard.style.display = 'flex';
    } catch(e) {
      console.warn('Readiness load failed:', e.message);
    }
  }

  // Premium badge — viser nedtelling når gratisuken er aktiv
  renderPremiumBanner();
}

// ════════════════════════════════════════════
//  CATEGORIES
// ════════════════════════════════════════════
// ════════════════════════════════════════════
//  3D CYLINDER CAROUSEL
// ════════════════════════════════════════════
var _carouselCats = [];
var _carouselActive = 0;
var _carouselAngleStep = 48;
var _carouselRadius = 340;
var _carouselDragStart = null;
var _carouselDragIdx = 0;

var CYBER_ICONS = {
  'sparkles': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5.5z"/><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1z"/></svg>',
  'git-merge': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M6 9v9a3 3 0 0 0 3 3h9"/></svg>',
  'file-text': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>',
  'cloud-rain': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/></svg>',
  'refresh-cw': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M3 21v-5h5"/></svg>'
};

async function loadCategories() {
  if (catsLoaded) return;
  var stage = document.getElementById('carouselStage');
  stage.innerHTML = '<div class="loading-wrap" style="position:absolute;top:50%;left:50%;margin:-24px 0 0 -24px;"><div class="spinner"></div></div>';
  try {
    var rawCats = await api('GET', '/api/categories');
    var countMap = {};
    var totalCount = 0;
    rawCats.forEach(function(c) {
      if (c.name) {
        countMap[c.name] = c.count;
        totalCount += c.count;
      }
    });

    var CYBER_CATEGORIES = [
      {
        id: "all",
        title: { no: "Alle kategorier", th: "ทุกหมวดหมู่", en: "All Categories" },
        icon: "sparkles",
        dbName: "",
        color: "#00F5FF",
        glow: "rgba(0,245,255,.45)",
        count: totalCount
      },
      {
        id: "right_of_way",
        title: { no: "Vikeplikt", th: "สิทธิการผ่านทาง", en: "Right of Way" },
        icon: "git-merge",
        dbName: "Right of Way",
        color: "#FF00E5",
        glow: "rgba(255,0,229,.45)",
        count: countMap["Right of Way"] || 0
      },
      {
        id: "traffic_rules",
        title: { no: "Trafikkregler", th: "กฎจราจร", en: "Traffic Rules" },
        icon: "file-text",
        dbName: "Road Rules",
        color: "#FFD700",
        glow: "rgba(255,215,0,.45)",
        count: countMap["Road Rules"] || 0
      },
      {
        id: "driving_conditions",
        title: { no: "Kjøreforhold", th: "สภาพการขับขี่", en: "Driving Conditions" },
        icon: "cloud-rain",
        dbName: "Driving Conditions",
        color: "#10B981",
        glow: "rgba(16,185,129,.45)",
        count: countMap["Driving Conditions"] || 0
      },
      {
        id: "situations",
        title: { no: "Situasjoner", th: "สถานการณ์", en: "Situations" },
        icon: "refresh-cw",
        dbName: "Situations",
        color: "#3B82F6",
        glow: "rgba(59,130,246,.45)",
        count: countMap["Situations"] || 0
      }
    ];

    // Filter categories to enforce language isolation (no Norwegian fallback in Thai mode)
    var cats = CYBER_CATEGORIES.filter(function(cat) {
      var title = cat.title[appLang];
      return title && title.trim().length > 0;
    });

    catsLoaded = true;
    document.getElementById('catCount').textContent = '(' + cats.length + ')';
    if (!cats.length) {
      stage.innerHTML = '<div class="empty-state" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;"><div class="es-icon">📭</div><p>' + t('categories_empty') + '</p></div>';
      return;
    }
    renderCarousel(cats);
  } catch(e) {
    console.error("loadCategories error:", e);
    stage.innerHTML = '<div class="empty-state" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;"><div class="es-icon">⚠️</div><p>' + t('categories_load_error') + '</p></div>';
  }
}

function renderCarousel(cats) {
  _carouselCats = cats;
  _carouselActive = 0;
  var stage = document.getElementById('carouselStage');
  var itemsHtml = cats.map(function(c, i) {
    var svgIcon = CYBER_ICONS[c.icon] || '';
    var count = c.count || '';
    var name = c.title[appLang];
    var qWord = t('questions_word');
    var styleStr = 'style="--cat-color:' + c.color + '; --cat-glow:' + c.glow + ';"';
    return '<div class="carousel-3d-item" data-idx="' + i + '" data-ckey="' + escH(c.id) + '" ' + styleStr + ' onclick="carouselClick(' + i + ')">'
      + '<div class="carousel-3d-icon">' + svgIcon + '</div>'
      + '<div class="carousel-3d-label">' + escH(name) + '</div>'
      + '<div class="carousel-3d-count">' + (count ? count + ' ' + qWord : '') + '</div>'
      + '</div>';
  }).join('');
  stage.innerHTML = itemsHtml + '<div class="carousel-3d-active-ring" id="carouselRing"></div>';
  renderDots(cats.length);
  updateCarousel(0, false);
  bindCarouselDrag();
  var hint = document.getElementById('carouselHint');
  if (hint) setTimeout(function(){ hint.style.opacity='0'; }, 5000);
}

function renderDots(n) {
  var dots = document.getElementById('carouselDots');
  if (!dots) return;
  dots.innerHTML = '';
  for (var i = 0; i < n; i++) {
    var dot = document.createElement('div');
    dot.className = 'carousel-3d-dot' + (i === 0 ? ' active' : '');
    dots.appendChild(dot);
  }
}

function updateCarousel(activeIdx, animate, dragAngleOffset) {
  var items = document.querySelectorAll('.carousel-3d-item');
  var n = items.length;
  if (!n) return;
  if (activeIdx < 0) activeIdx = 0;
  if (activeIdx >= n) activeIdx = n - 1;
  _carouselActive = activeIdx;
  var ring = document.getElementById('carouselRing');
  var dur = animate ? '0.45s' : '0s';
  var timing = 'cubic-bezier(.22,.68,0,1)';
  for (var i = 0; i < n; i++) {
    var item = items[i];
    var delta = i - activeIdx;
    var angle = delta * _carouselAngleStep + (dragAngleOffset || 0);
    var visible = Math.abs(angle) <= 100;
    if (!visible) { item.style.display='none'; item.style.pointerEvents='none'; continue; }
    item.style.display = 'flex';
    item.style.pointerEvents = 'auto';
    var absD = Math.abs(delta);
    var scale = delta === 0 ? 1.08 : Math.max(1 - absD * 0.12, 0.50);
    var opacity = Math.max(1 - absD * 0.15, 0.30);
    item.style.transition = 'transform ' + dur + ' ' + timing + ', opacity ' + dur + ' ease';
    item.style.transform = 'rotateY(' + angle + 'deg) translateZ(' + _carouselRadius + 'px)';
    item.style.opacity = opacity;
    item.style.zIndex = n - absD;
    item.style.scale = scale;
    item.classList.toggle('active', delta === 0);
  }
  if (ring) {
    ring.style.transition = 'transform ' + dur + ' ' + timing + ', opacity 0.45s';
    ring.style.transform = 'rotateY(0deg) translateZ(' + _carouselRadius + 'px)';
    ring.classList.toggle('visible', true);
    // Inherit the active card's neon color so the ring glows in the right colour
    var activeEl = items[activeIdx];
    if (activeEl) {
      var cs = getComputedStyle(activeEl);
      var cc = cs.getPropertyValue('--cat-color').trim() || '#FF9933';
      var cg = cs.getPropertyValue('--cat-glow').trim() || 'rgba(255,153,51,.45)';
      ring.style.setProperty('--cat-color', cc);
      ring.style.setProperty('--cat-glow', cg);
    }
  }
  var dotEls = document.querySelectorAll('.carousel-3d-dot');
  for (var j = 0; j < dotEls.length; j++) {
    dotEls[j].className = 'carousel-3d-dot' + (j === activeIdx ? ' active' : '') + (Math.abs(j - activeIdx) === 1 ? ' adjacent' : '');
  }
}

function carouselClick(idx) {
  if (idx === _carouselActive) {
    var cat = _carouselCats[idx];
    if (cat) startQuiz(String(cat.dbName || ''));
  } else {
    updateCarousel(idx, true);
  }
}

function bindCarouselDrag() {
  var wrap = document.getElementById('carouselWrap');
  if (!wrap) return;
  var dragging = false, startX = 0, lastX = 0, startIdx = 0;
  function onStart(x) { dragging = true; startX = x; lastX = x; startIdx = _carouselActive; }
  function onMove(x) {
    if (!dragging) return;
    var dx = x - startX;
    lastX = x;
    var steps = -dx / 85;
    var tempIdx = Math.round(startIdx + steps);
    tempIdx = Math.max(0, Math.min(tempIdx, _carouselCats.length - 1));
    updateCarousel(tempIdx, false);
  }
  function onEnd() {
    if (!dragging) return;
    dragging = false;
    // Snap — current active is already set by onMove
  }
  wrap.addEventListener('mousedown', function(e){ onStart(e.clientX); });
  wrap.addEventListener('mousemove', function(e){ onMove(e.clientX); });
  wrap.addEventListener('mouseup', onEnd);
  wrap.addEventListener('mouseleave', onEnd);
  wrap.addEventListener('touchstart', function(e){ onStart(e.touches[0].clientX); }, {passive:true});
  wrap.addEventListener('touchmove', function(e){ onMove(e.touches[0].clientX); e.preventDefault(); }, {passive:false});
  wrap.addEventListener('touchend', onEnd);
}

// ════════════════════════════════════════════
//  QUIZ
// ════════════════════════════════════════════
async function startRandomQuiz() {
  isMistakeMode = false;
  currentCat = null;
  isExamMode = false;
  await loadQuiz('/api/questions/random?count=30&has_image=true');
}

async function startDailyTest() {
  if (!isPremium()) { showPaywall(); return; }
  isMistakeMode = false;
  currentCat = null;
  isExamMode = false;
  await loadQuiz('/api/questions/random?count=10&has_image=true');
}

async function startMistakeQuiz() {
  if (!token) {
    toast(t('mistakes_login'));
    return;
  }
  isMistakeMode = true;
  currentCat = null;
  isExamMode = false;
  await loadQuiz('/api/quiz/mistakes?limit=100&_=' + Date.now());
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

// ════════════════════════════════════════════
//  GRATISUKE (7 dagers prøveperiode)
// ════════════════════════════════════════════
// Kilden er /api/auth/me: premium_status === 'trialing' + premium_expires_at.
// Prøvebrukere ER premium, så isPremium() og alle portene virker uendret —
// dette laget styrer kun hva brukeren SER, ikke hva hen får lov til.
function trialDaysLeft() {
  if (!user) return 0;
  if (typeof user.trial_days_left === 'number') return Math.max(0, user.trial_days_left);
  var raw = user.premium_expires_at;
  if (!raw) return 0;
  var s = String(raw).trim().replace(' ', 'T');
  if (!/([Zz]|[+\-]\d{2}:?\d{2})$/.test(s)) s += 'Z';  // naiv ISO tolkes som UTC
  var ms = Date.parse(s);
  if (isNaN(ms)) return 0;
  var diff = ms - Date.now();
  return diff <= 0 ? 0 : Math.max(1, Math.ceil(diff / 86400000));
}

function isTrialActive() {
  return !!(user && user.premium_status === 'trialing' && trialDaysLeft() > 0);
}

// Én tekst per dag-tilstand. t()/tf() er strikte — ingen fallback til andre språk.
function trialBannerText() {
  var d = trialDaysLeft();
  if (d <= 0) return t('trial_active');
  if (d === 1) return t('trial_last_day');
  if (d === 2) return t('trial_two_days');
  return tf('trial_days_left', {days: d});
}

// Gjenbruker den eksisterende grønne pillen #homePremiumBanner — ingen ny design.
function renderPremiumBanner() {
  var pb = document.getElementById('homePremiumBanner');
  if (!pb) return;
  if (!(user && user.is_premium)) { pb.style.display = 'none'; return; }
  var trial  = isTrialActive();
  var icon   = pb.querySelector('.pb-icon');
  var ptitle = pb.querySelector('.pb-title');
  var psub   = pb.querySelector('.pb-sub');
  if (icon)   icon.textContent   = trial ? '🎁' : '💎';
  if (ptitle) ptitle.textContent = trial ? trialBannerText() : t('premium_on');
  if (psub)   psub.textContent   = trial ? t('trial_sub')    : t('premium_sub');
  pb.style.display = 'flex';
}

// Betalingsmuren skal forklare hvorfor den dukket opp når gratisuken er brukt opp.
function renderPaywallSub() {
  var el = document.querySelector('#screenPaywall .paywall-sub');
  if (!el) return;
  var spent = !!(user && user.trial_used === true) && !isTrialActive();
  el.textContent = t('pw_sub');
}

// Oppmuntrende varsel de to siste dagene — maks én gang per dag per tilstand.
function maybeShowTrialNotice() {
  if (!isTrialActive()) return;
  var d = trialDaysLeft();
  if (d > 2) return;
  var stamp = new Date().toISOString().slice(0, 10) + ':' + d;
  if (_ls.get('t2d_trial_notice') === stamp) return;
  _ls.set('t2d_trial_notice', stamp);
  toast(d === 1 ? t('trial_last_day') : t('trial_two_days'), 5000);
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
    // Fail-closed (Michaels avgjørelse): betalingsmuren skal beskytte innholdet.
    // Kan vi ikke bekrefte tilgangen, slipper vi ingen gjennom.
    if (e.status === 402) { await loadAccessStatus(); showPaywall(); return false; }
    console.warn('[gate] fail-closed:', e && e.message ? e.message : e);
    toast(t('access_check_failed'));
    await loadAccessStatus();
    showPaywall();
    return false;
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
  stopAllSpeech();
  stopExamTimer();
  applyUILang();
  showScreen('screenPaywall');
  // Hide bottom nav while paywall is shown
  document.getElementById('topBar').style.display = 'flex';
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

var _checkoutStarting = false;
async function buyPremium(plan, el) {
  if (_checkoutStarting) return;
  if (plan) selectPlan(plan, el);
  if (!token) {
    showScreen('screenAuth');
    return;
  }
  _checkoutStarting = true;
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
    toast(t('checkout_unavailable_toast'), 5000);
  } finally {
    _checkoutStarting = false;
  }
}

async function restorePurchase() {
  if (!token) {
    showScreen('screenAuth');
    return;
  }
  try {
    await refreshCurrentUser();
    if (isPremium()) {
      hidePaywall();
      showTab('home');
      toast(t('premium_activated_toast'), 4500);
      return;
    }
    toast(t('payment_unconfirmed_toast'), 5000);
  } catch(e) {
    toast(t('payment_unconfirmed_toast'), 5000);
  }
}


async function startExam() {
  if (!isPremium()) { showPaywall(); return; }
  isMistakeMode = false;
  currentCat = null;
  isExamMode = true;
  await loadQuiz('/api/questions/random?count=45&has_image=true&mode=exam');
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

async function startQuiz(catId) {
  isMistakeMode = false;
  var key = catKey(catId);
  currentCat = key ? { id: key, key: key } : null;
  isExamMode = false;
  var url = '/api/questions/random?count=30&has_image=true';
  if (key) url += '&category=' + encodeURIComponent(key);
  await loadQuiz(url);
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
      return u && typeof u === 'string' && u.length > 0;
    });
    if (!questions.length && currentCat) {
      var r2 = await api('GET', '/api/questions/random?count=30&has_image=true');
      if (!Array.isArray(r2)) r2 = r2.questions || [];
      questions = r2.filter(function(q) {
        var u = q.bildeUrl || q.image_url || '';
        return u && typeof u === 'string' && u.length > 0;
      });
    }
    if (!questions.length) {
      var emptyKey = isMistakeMode ? 'mistakes_empty' : 'questions_empty';
      qCard.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">📭</div><p>' + t(emptyKey) + '</p></div>';
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
    var errorKey = isMistakeMode ? 'mistakes_load_error' : 'generic_error';
    qCard.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><div class="es-icon">⚠️</div><p>' + t(errorKey) + '<br>' + escH(e.message) + '</p></div>';
  }
}

function pickLang(obj) {
  if (!obj) return '';
  if (typeof obj === 'string') return obj;
  return pickStrict(obj);
}

// Pick language-suffixed field from a question object (e.g. question_text_th, answer_a_no)
function pickField(q, base) {
  return q[base + '_' + appLang] || '';
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
  if (imgUrl && !imgUrl.match(/^(https?:\/\/|\/|data:)/)) { imgUrl = '/api/assets/' + imgUrl; }
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

  // Shuffle answer options so the correct answer isn't always in the same position.
  // currentCorrect is updated to the new display letter of the correct option.
  if (opts.length > 1) {
    var shuffled = shuffleOpts(opts, currentCorrect);
    opts = shuffled.opts;
    currentCorrect = shuffled.correct;
  }

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
    var freeMsg = tf('free_questions_left', {count: remaining});
    freeBanner = '<div style="text-align:center;font-size:.72rem;color:var(--orange);font-weight:700;margin-top:6px;flex-shrink:0;">'
      + '⚡ ' + escH(freeMsg) + ' — <span style="text-decoration:underline;cursor:pointer" onclick="showPaywall()">' + escH(t('upgrade')) + '</span>'
      + '</div>';
  }

  qCard.innerHTML =
    '<div class="q-left">'
      + '<div class="q-img-wrap" id="qImgWrap">'
        + '<img class="q-img" src="' + escH(imgUrl) + '" alt="' + escH(qText) + '" onerror="this.parentElement.style.display=\'none\'" loading="lazy">'
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
  if (aiImg) { aiImg.src = imgUrl; aiImg.alt = qText; aiImg.className = 'quiz-ai-img'; } // clear flash
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

/**
 * Shuffle answer options and rebind display letters A/B/C/D.
 * Returns { opts: shuffledArray, correct: newLetterOfCorrectAnswer }
 * The caller must update currentCorrect with the returned value.
 * The original question object is NOT mutated — only the local opts copy is.
 */
function shuffleOpts(opts, correctId) {
  var arr = opts.slice();
  // Fisher-Yates
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
  }
  var letters = ['A', 'B', 'C', 'D'];
  var newCorrect = correctId; // fallback if not found
  arr.forEach(function(o, i) {
    if (o.id === correctId) newCorrect = letters[i];
    o.id = letters[i]; // rebind display letter to shuffled position
  });
  return { opts: arr, correct: newCorrect };
}

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
  }[appLang] || [];  // Fail-Stop: ukjent språk gir tom pool, aldri norsk fallback
}
function _nextCorrectPhrase() {
  var pool = _correctPhrases();
  if (!pool.length) return '';
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
  if (/reaksjonslengde|bremselengde|stoppelengde/i.test(t)) return 'Bremsing';
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
  return item ? (pickStrict(item) || label) : label;
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

  // Scroll Next button into view after a short delay (DOM paint + feedback render)
  setTimeout(function() {
    var btn = document.getElementById('qNextMobile');
    if (btn) btn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 180);

  playSound(isOk ? 'correct' : 'wrong');
  stopAllSpeech();

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
    // Språkrenhet: mangler teksten på det aktive språket skjules kortet helt.
    var txt = {th:th, no:no, en:en}[appLang] || '';
    if (!txt) return;
    alerts.push({icon:icon, type:type, label:label, text:txt});
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
  // Nøklene i map ER den norske teksten, så norsk returnerer nøkkelen direkte.
  // Mangler thai/engelsk, returneres tom streng — raden skjules (Fail-Stop).
  // Aldri norsk tekst i thai- eller engelsk-modus.
  if (appLang === 'no') return text;
  var item = map[text];
  return (item && item[appLang]) || '';
}

function buildSituationLensHtml(qText, expl) {
  var lens = buildSituationLens(qText, expl);
  // Fail-Stop: rader uten tekst på aktivt språk vises ikke i det hele tatt.
  function _row(tagKey, raw) {
    var txt = lensText(raw);
    if (!txt) return '';
    return '<div class="q-observe-row"><span class="q-observe-tag">' + escH(t(tagKey)) + '</span>' + escH(txt) + '</div>';
  }
  var rows = _row('see_tag', lens.see) + _row('understand_tag', lens.understand) + _row('choose_tag', lens.choose);
  if (!rows) return '';
  return '<div class="q-observe">' + rows + '</div>';
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
  var title = escH(v['title_' + appLang] || '');
  if (!title) return '';
  var dur = _fmtDur(v.duration_seconds);

  // Determine source key (file_path or youtube_url)
  var srcKey = v.file_path || v.youtube_url || '';
  if (!srcKey) return '';
  if (v.youtube_url) srcKey = v.youtube_url;

  var thumb = v.thumbnail_url || '';
  var thumbStyle = thumb ? ' style="background-image:url(' + escH(thumb) + ')"' : '';

  return '<div class="vid-card vid-card-local" onclick="openVideoPlayer(\'' + escH(srcKey) + '\')">'
    + '<div class="vid-card-thumb"' + thumbStyle + '>'
      + '<div class="vid-card-play"><span>▶</span></div>'
    + '</div>'
    + '<div class="vid-info">'
      + '<div class="vid-lbl">' + escH(t('video_short')) + '</div>'
      + '<div class="vid-title">' + title + '</div>'
      + (dur ? '<div class="vid-dur">' + dur + '</div>' : '')
    + '</div>'
    + '</div>';
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

    // 2c ── Ask Michael Button (Phase 3)
    html += '<button class="ask-michael-btn ai-block" style="--i:' + (i++) + '; width:100%; display:flex; align-items:center; justify-content:center; gap:8px; padding:12px; border-radius:10px; border:none; background:rgba(255,107,0,.15); color:var(--orange); font-weight:700; cursor:pointer; font-size:.85rem; margin-top:10px; transition:background .2s;" onmouseover="this.style.background=\'rgba(255,107,0,.25)\'" onmouseout="this.style.background=\'rgba(255,107,0,.15)\'" onclick="askMichaelAboutThis()">'
      + '<span>🚗</span> ' + escH(t('ask_michael'))
      + '</button>';

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

  // Michael is an enhancement, never a gate. The ordinary explanation and
  // Next button are already available before this asynchronous call starts.
  if (!isOk) openMichaelQuizCoach();

  // Mobile question image tint
  var imgWrap = document.getElementById('qImgWrap');
  if (imgWrap) {
    imgWrap.style.outline   = isOk ? '2.5px solid rgba(16,185,129,.55)' : '2.5px solid rgba(239,68,68,.50)';
    imgWrap.style.boxShadow = isOk ? '0 0 18px rgba(16,185,129,.22)'    : '0 0 18px rgba(239,68,68,.20)';
    imgWrap.style.transition = 'outline .3s ease, box-shadow .3s ease';
  }
}

function nextQ() {
  stopAllSpeech();
  closeMichaelQuizCoach();
  if (_aiPanelTimer) { clearTimeout(_aiPanelTimer); _aiPanelTimer = null; } // never let a delayed panel land on the next question
  // Review mode uses its own card renderer — skip normal quiz flow
  if (_reviewMode) { reviewNext(); return; }
  if (!qAnswered) return;
  qIdx++;
  if (qIdx >= questions.length) { showEnd(); return; }
  if (!checkPaywall()) return;
  renderQuestion();
  // Scroll back to top of quiz body so new question starts at the top
  var qb = document.querySelector('.quiz-body');
  if (qb) qb.scrollTop = 0;
}

function goBack() {
  stopAllSpeech();
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
      if (imgUrl && !imgUrl.match(/^(https?:\/\/|\/|data:)/)) { imgUrl = '/api/assets/' + imgUrl; }
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
      var imgHtml = imgUrl ? '<div class="bm-card-img-wrap"><img class="bm-card-img" src="' + escH(imgUrl) + '" alt="' + escH(qText) + '" onerror="this.parentElement.style.display=\'none\'"></div>' : '';
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
    if (!Array.isArray(groups)) throw new Error(t('invalid_response'));
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
      var gLabel = pickStrict(gName);
      var gDesc = pickStrict(gMeta.desc);
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
        var nameText = pickStrict(sName) || missingText();
        var imgUrl = sign.image_url || '';
        var card = document.createElement('div');
        card.className = 'sign-card';
        card.innerHTML =
          (imgUrl
            ? '<div class="sign-img-wrap"><img class="sign-img" src="' + escH(imgUrl) + '" alt="' + escH(nameText) + '" loading="lazy"></div>'
            : '') +
          '<div class="sign-ans">' + escH(nameText || '–') + '</div>';
        (function(s){ card.onclick = function(){ openSignDetail(s); }; })(sign);
        grid.appendChild(card);
      });
      scroll.appendChild(grid);
    });

    signsLoaded = true;
  } catch(e) {
    scroll.innerHTML = '<div class="empty-state"><div class="es-icon">⚠️</div><p>' + escH(e.message || t('load_error')) + '</p></div>';
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
    var data;
    if (token) {
      data = await api('GET', '/api/history?limit=50&_=' + Date.now());
    } else {
      data = await api('GET', '/api/quiz-attempts/' + encodeURIComponent(deviceId) + '?limit=50&_=' + Date.now());
    }
    var attempts = Array.isArray(data) ? data : (data.attempts || data.results || []);
    // Always merge with local data — covers the gap between quiz end and POST completion
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
  if (a.category) {
    var detailCat = catName(a.category);
    if (detailCat) modeStr += ' — ' + detailCat;
  }
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
    var retryKey = catKey(a.category);
    if (retryKey) startQuiz(retryKey);
    else {
      console.warn('[i18n] cannot retry unknown category', a.category);
      toast(t('retry_category_unavailable'));
    }
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
        ? tf('result_exam_focus_body', {topic: topicLabel(topTopic)})
        : t('result_more_body');
    }
  } else if (pct >= 85) {
    heading = t('result_solid_head');
    body = total >= 15
      ? t('result_solid_body')
      : t('result_short_practice_body');
  } else if (pct >= 65) {
    heading = t('result_right_way_head');
    body = topTopic
      ? tf('result_right_way_focus_body', {topic: topicLabel(topTopic)})
      : t('result_right_way_body');
  } else if (pct >= 40) {
    heading = t('result_more_head');
    body = topTopic
      ? tf('result_more_focus_body', {topic: topicLabel(topTopic)})
      : t('result_more_body');
  } else {
    heading = t('result_learn_head');
    body = t('result_learn_body');
  }

  return { heading: heading, body: body, topTopic: topTopic };
}

function showEnd() {
  stopAllSpeech();
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
    var mode = isMistakeMode ? 'mistakes' : (isExamMode ? 'exam' : (currentCat ? 'category' : 'daily'));
    var completedAt = new Date().toISOString();
    var clientAttemptId = 'web_' + completedAt + '_' + Math.random().toString(36).slice(2, 8);
    var attemptData = {
      client_attempt_id: clientAttemptId,
      device_id: deviceId,
      mode: mode,
      category: currentCat && currentCat.key ? currentCat.key : null,
      total_questions: total,
      correct_answers: qScore,
      score_percentage: pct,
      passed: isExamMode ? pct >= 85 : null,
      questions_answered: _sessionAnswers.length ? _sessionAnswers : questions.map(function(q, i) {
        return { question_id: String(q._id || q.id || q.question_id || ''), index: i };
      }),
      started_at: quizStartedAt || completedAt,
      completed_at: completedAt,
      is_mistake_mode: isMistakeMode
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
        // Auto-refresh history if visible — so new result appears immediately
        var hs = document.getElementById('screenHistory');
        if (hs && hs.classList.contains('active')) loadHistory();
      })
      .catch(function(e) {
        console.warn('Quiz attempt save failed:', e.message);
        toast(t('result_save_failed') + e.message, 4000);
      });
  }
}

function retryQuiz() {
  if (isMistakeMode) startMistakeQuiz();
  else if (currentCat) startQuiz(currentCat.id);
  else startRandomQuiz();
}

// ════════════════════════════════════════════
//  TTS
// ════════════════════════════════════════════
// _unlockAudioPlayback(), _ensureBackendAudio() og _ensureTeacherAudio() er definert
// sammen med lyd-globalene lenger oppe — ikke dupliser dem her. Funksjonsdeklarasjoner
// heises, så en kopi lenger ned i filen ville stille overskrevet originalen.

function speakQ() {
  var q = questions[qIdx];
  if (!q) return;
  var text = pickLang(q.question) || pickField(q, 'question_text') || '';
  if (!text) return;

  if (ttsPlaying) {
    stopAllSpeech();
    return;
  }
  _ensureBackendAudio();
  _unlockAudioPlayback(_backendAudio);
  _backendAudio.src = ttsStreamUrl(text, appLang);
  _backendAudio.playbackRate = ttsRate || 1.0;
  _backendAudio.volume = ttsVolume !== undefined ? ttsVolume : 1.0;
  ttsPlaying = true;
  updateTtsBtn(true);
  _backendAudio.play().catch(function(err) {
     console.error('Audio playback failed:', err);
     ttsPlaying = false;
     updateTtsBtn(false);
  });
}
function updateTtsBtn(playing) {
  var btn = document.getElementById('qTtsBtn');
  if (!btn) return;
  btn.textContent = playing ? '⏸' : '▶';
  btn.classList.toggle('playing', playing);
}
function setRate(r, el) {
  ttsRate = r;
  if (_backendAudio) _backendAudio.playbackRate = r;
  if (_teacherAudio) _teacherAudio.playbackRate = r;
  document.querySelectorAll('.spd-btn').forEach(function(b) {
    b.classList.toggle('active', parseFloat(b.dataset.rate) === r);
  });
}
function setVolume(v) {
  ttsVolume = v;
  if (_backendAudio) _backendAudio.volume = v;
  if (_teacherAudio) _teacherAudio.volume = v;
  _ls.set('t2d_vol', String(v));
  document.querySelectorAll('.vol-btn').forEach(function(b) {
    b.classList.toggle('active', parseFloat(b.dataset.vol) === v);
  });
}

var _teacherTtsPlaying = false;
function speakText(text) {
  // Strip any video/audio/image tags and emoji clutter
  var clean = text
    .replace(/\[(video|audio|podcast|image|url):[^\]]+\]/gi, '')
    .replace(/[🛑🚗💡⚠️📝❓✨😊]/g, '')
    .trim();
  if (!clean) return;

  // The same bubble toggles playback off. A different bubble replaces the old
  // audio and starts immediately with this same user gesture.
  if (_teacherTtsPlaying && _teacherActiveText === clean) {
    stopAllSpeech();
    return;
  }
  if (_teacherTtsPlaying || (_teacherAudio && !_teacherAudio.paused)) {
    stopAllSpeech();
  }
  _ensureTeacherAudio();
  _unlockAudioPlayback(_teacherAudio);
  var playToken = ++_teacherAudioToken;
  _teacherActiveText = clean;
  _teacherAudio.src = ttsStreamUrl(clean, appLang);
  _teacherAudio.playbackRate = ttsRate || 1.0;
  _teacherAudio.volume = ttsVolume !== undefined ? ttsVolume : 1.0;
  _teacherTtsPlaying = true;
  _teacherAudio.play().catch(function(err) {
     console.error('Teacher audio playback failed:', err);
     if (playToken === _teacherAudioToken) {
       _teacherTtsPlaying = false;
       _teacherActiveText = '';
     }
  });
}

function buildPodcastCard(p) {
  if (!p) return '';
  var title = escH(
    appLang === 'th' ? (p.title_th || '') :
    appLang === 'en' ? (p.title_en || '') :
    (p.title_no || '')
  );
  if (!title) return '';
  var rawUrl = p.file_path || p.audio_url || '';
  // Convert file_path (e.g. /public_assets/podcast.mp3) to proper API URL
  if (rawUrl && rawUrl.indexOf('/public_assets/') === 0) {
    rawUrl = '/api/assets/' + rawUrl.substring('/public_assets/'.length);
  }
  var url = escH(rawUrl);
  if (!url) return '';
  var dur = _fmtDur(p.duration_seconds);

  return '<div class="podcast-card">'
    + '<div class="podcast-info">'
      + '<div class="podcast-lbl">' + escH(t('podcast_short')) + '</div>'
      + '<div class="podcast-title">' + title + '</div>'
      + (dur ? '<div class="podcast-dur">' + dur + '</div>' : '')
    + '</div>'
    + '<audio class="podcast-player" controls preload="none" src="' + url + '"></audio>'
    + '</div>';
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
  stopAllSpeech();
  var previousLang = appLang;
  appLang = lang;
  _ls.set('t2d_lang', lang);
  ['TH','NO','EN'].forEach(function(l) {
    var btn = document.getElementById('lang' + l);
    if (btn) btn.classList.toggle('active', lang === l.toLowerCase());
    var topBtn = document.getElementById('topLang' + l);
    if (topBtn) topBtn.classList.toggle('active', lang === l.toLowerCase());
    var authBtn = document.getElementById('authLang' + l);
    if (authBtn) authBtn.classList.toggle('active', lang === l.toLowerCase());
  });
  applyUILang();
  // Reset signs cache so it reloads in new language
  signsLoaded = false;
  var signsScreen = document.getElementById('screenSigns');
  if (signsScreen && signsScreen.classList.contains('active')) loadSigns();
  // Re-render categories in new language (force re-render by resetting cache)
  if (catsLoaded) { catsLoaded = false; loadCategories(); }
  if (_videosCached || _podcastsCached) renderLibrary();
  // Re-render quiz if active so question+answers switch language immediately
  var quizScreen = document.getElementById('screenQuiz');
  if (quizScreen && quizScreen.classList.contains('active') && questions.length) {
    renderQuestion();
  }
  var endScreen = document.getElementById('screenEnd');
  if (endScreen && endScreen.classList.contains('active') && questions.length) {
    showEnd();
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
  if (previousLang && previousLang !== lang) {
    resetTeacherForLanguage();
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

// Quiz-specific teacher session variables
var _teacherActiveSessionType = 'normal';
var _teacherQuizSessionId     = null;
var _teacherNormalHtml        = '';
var _teacherQuizHtml          = '';
var _teacherNormalHasUserMsg  = false;
var _teacherQuizHasUserMsg    = false;
var _quizCoachSessionId       = null;
var _quizCoachAbort           = null;

function _quizCoachContext() {
  var q = questions[qIdx];
  var lastAns = _sessionAnswers[_sessionAnswers.length - 1];
  if (!q || !lastAns || lastAns.is_correct !== false) return null;
  var qText = pickLang(q.question) || pickField(q, 'question_text') || '';
  var userAnsText = _displayedAnswerText(lastAns.user_answer);
  var correctAnsText = _displayedAnswerText(currentCorrect);
  return {
    questionId: String(q._id || q.id || q.question_id || 'question'),
    question: qText,
    userAnswerId: lastAns.user_answer,
    userAnswer: userAnsText,
    correctAnswerId: currentCorrect,
    correctAnswer: correctAnsText,
    explanation: currentExpl || ''
  };
}

async function _quizCoachRequest(message) {
  if (_quizCoachAbort) _quizCoachAbort.abort();
  var controller = new AbortController();
  _quizCoachAbort = controller;
  var timeoutId = setTimeout(function(){ controller.abort(); }, 12000);
  try {
    var headers = {'Content-Type':'application/json'};
    if (token) headers.Authorization = 'Bearer ' + token;
    var res = await fetch('/api/teacher/chat', {
      method:'POST', headers:headers, signal:controller.signal,
      body:JSON.stringify({session_id:_quizCoachSessionId, message:message, language:appLang})
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var data = await res.json();
    if (data.session_id) _quizCoachSessionId = data.session_id;
    return data.reply || '';
  } finally {
    clearTimeout(timeoutId);
    if (_quizCoachAbort === controller) _quizCoachAbort = null;
  }
}

async function openMichaelQuizCoach() {
  var ctx = _quizCoachContext();
  if (!ctx) return;
  var panel = document.getElementById('michaelQuizCoach');
  var body = document.getElementById('michaelQuizCoachBody');
  var action = document.getElementById('michaelQuizCoachAction');
  if (!panel || !body || !action) return;

  _quizCoachSessionId = 'quiz_coach_' + appLang + '_' + ctx.questionId.replace(/[^a-zA-Z0-9_-]/g,'').slice(0,32) + '_' + Date.now().toString(36);
  body.textContent = t('coach_loading');
  action.classList.remove('show');
  action.disabled = false;
  panel.classList.add('open');

  var languageName = {th:'Thai', no:'Norwegian', en:'English'}[appLang] || '';
  var prompt = 'You are Michael, a calm Norwegian driving instructor. Answer only in ' + languageName + '. '
    + 'Never mix languages. Keep the answer short enough for a mobile panel. Explain why the student answer is wrong, why the correct answer is right, and give one practical traffic example. '
    + 'Use the mental model "Kongen og tjeneren" or "HAV-regelen" only when it fits naturally; never force either model.\n\n'
    + '<quiz_context>\nQuestion: ' + ctx.question
    + '\nStudent answer (' + ctx.userAnswerId + '): ' + ctx.userAnswer
    + '\nCorrect answer (' + ctx.correctAnswerId + '): ' + ctx.correctAnswer
    + '\nExisting explanation: ' + ctx.explanation + '\n</quiz_context>';
  try {
    var reply = await _quizCoachRequest(prompt);
    if (!panel.classList.contains('open')) return;
    body.textContent = reply || t('coach_unavailable');
    if (reply) action.classList.add('show');
  } catch(e) {
    if (panel.classList.contains('open')) body.textContent = t('coach_unavailable');
  }
}

async function requestCoachPractice() {
  var body = document.getElementById('michaelQuizCoachBody');
  var action = document.getElementById('michaelQuizCoachAction');
  if (!body || !action || !_quizCoachSessionId) return;
  action.disabled = true;
  body.textContent = t('coach_practice_loading');
  var promptByLang = {
    th:'ยกตัวอย่างสถานการณ์จราจรสั้น ๆ หนึ่งสถานการณ์ แล้วถามคำถามตรวจสอบความเข้าใจหนึ่งข้อ อย่าเฉลยทันที',
    no:'Gi én kort trafikksituasjon og still ett enkelt kontrollspørsmål. Ikke avslør svaret med én gang.',
    en:'Give one short traffic situation and ask one simple check question. Do not reveal the answer immediately.'
  };
  try {
    var reply = await _quizCoachRequest(promptByLang[appLang] || '');
    body.textContent = reply || t('coach_unavailable');
    action.classList.remove('show');
  } catch(e) {
    body.textContent = t('coach_unavailable');
    action.disabled = false;
  }
}

function closeMichaelQuizCoach() {
  var panel = document.getElementById('michaelQuizCoach');
  if (panel) panel.classList.remove('open');
  if (_quizCoachAbort) { _quizCoachAbort.abort(); _quizCoachAbort = null; }
}

function switchTeacherSession(type) {
  var msgs = document.getElementById('teacherMessages');
  if (!msgs) return;

  if (_teacherActiveSessionType === type) return;

  if (_teacherActiveSessionType === 'normal') {
    _teacherNormalHtml = msgs.innerHTML;
    _teacherNormalHasUserMsg = _teacherHasUserMsg;
  } else {
    _teacherQuizHtml = msgs.innerHTML;
    _teacherQuizHasUserMsg = _teacherHasUserMsg;
  }

  _teacherActiveSessionType = type;

  if (type === 'normal') {
    msgs.innerHTML = _teacherNormalHtml;
    _teacherHasUserMsg = _teacherNormalHasUserMsg;
    if (!msgs.innerHTML) {
      _teacherWelcomeLang = null; // force reload welcome
    }
  } else {
    msgs.innerHTML = _teacherQuizHtml;
    _teacherHasUserMsg = _teacherQuizHasUserMsg;
  }
}

function _displayedAnswerText(answerId) {
  var btn = document.querySelector('.ans-btn[data-id="' + String(answerId || '').toUpperCase() + '"]');
  var txt = btn ? btn.querySelector('.ans-text') : null;
  return txt ? txt.textContent.trim() : '';
}

function askMichaelAboutThis() {
  var q = questions[qIdx];
  if (!q) return;

  // Safety guard: only allowed after a confirmed wrong answer
  var lastAns = _sessionAnswers[_sessionAnswers.length - 1];
  if (!lastAns || lastAns.is_correct !== false) return;

  var qText = pickLang(q.question) || pickField(q, 'question_text') || '';

  var userAnsId = lastAns.user_answer;
  var correctAnsId = currentCorrect;

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

  var userAnsText = _displayedAnswerText(userAnsId);
  var correctAnsText = _displayedAnswerText(correctAnsId);
  opts.forEach(function(o) {
    var txt = typeof o.text === 'object' ? pickLang(o.text) : o.text;
    if (!userAnsText && o.id === userAnsId) userAnsText = txt;
    if (!correctAnsText && o.id === correctAnsId) correctAnsText = txt;
  });

  var explText = currentExpl || '';
  var qId = String(q._id || q.id || q.question_id || 'question').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 32);

  // Switch to quiz teacher session
  _teacherQuizHtml = '';
  _teacherQuizHasUserMsg = false;
  switchTeacherSession('quiz');

  // Generate a fresh language-scoped session ID for this question.
  // Normal Michael chat history uses _teacherSessionId and is not touched.
  _teacherQuizSessionId = 'quiz_help_' + appLang + '_' + qId + '_' + Date.now().toString(36);
  _teacherHasUserMsg = false;
  _teacherWelcomeLang = null;

  var msgs = document.getElementById('teacherMessages');
  if (msgs) msgs.innerHTML = '';

  var userDisplayMsg = '';
  if (appLang === 'th') {
    userDisplayMsg = 'ช่วยอธิบายข้อนี้ให้ผมฟังหน่อยครับ';
  } else if (appLang === 'en') {
    userDisplayMsg = 'Can you explain this question to me?';
  } else {
    userDisplayMsg = 'Kan du forklare dette spørsmålet for meg?';
  }

  var hiddenPayload = userDisplayMsg + '\n\n'
    + '<quiz_context>\n'
    + 'STUDENT ANSWERED INCORRECTLY. EXPLAIN WHY IT IS WRONG.\n'
    + 'is_correct: false\n'
    + 'Question: ' + qText + '\n'
    + '[ELEVENS FAKTISKE SVAR] (' + userAnsId + '): ' + userAnsText + '\n'
    + '[FAKTISK FASIT] (' + correctAnsId + '): ' + correctAnsText + '\n'
    + 'Explanation: ' + explText + '\n'
    + '</quiz_context>';

  // Navigate to teacher tab in 'quiz' mode
  showTab('teacher', 'quiz');

  // Trigger send using the hidden payload, but display the clean message in the bubble!
  teacherSend(hiddenPayload, userDisplayMsg);
}

function resetTeacherForLanguage() {
  _teacherSessionId = null;
  _teacherHasUserMsg = false;
  _teacherWelcomeLang = null;
  _teacherTyping = false;
  _teacherActiveSessionType = 'normal';
  _teacherQuizSessionId = null;
  _teacherNormalHtml = '';
  _teacherQuizHtml = '';
  _teacherNormalHasUserMsg = false;
  _teacherQuizHasUserMsg = false;
  var input = document.getElementById('teacherInput');
  if (input) input.value = '';
  var msgs = document.getElementById('teacherMessages');
  if (msgs) msgs.innerHTML = '';
  var suggestions = document.getElementById('teacherSuggestions');
  if (suggestions) suggestions.style.display = '';
  _teacherRemoveChips();
}

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

    // Video tag match: [video: url | title_no | title_th | title_en]
    var vidMatch = block.match(/^\[video:\s*([^\|\]]+)(?:\|\s*([^\|\]]+))?(?:\|\s*([^\|\]]+))?(?:\|\s*([^\]]+))?\]$/i);
    if (vidMatch) {
      var url = vidMatch[1].trim();
      var titleNo = (vidMatch[2] || '').trim();
      var titleTh = (vidMatch[3] || '').trim();
      var titleEn = (vidMatch[4] || '').trim();
      var v = {
        youtube_url: url,
        title_no: titleNo,
        title_th: titleTh,
        title_en: titleEn,
        duration_seconds: 0
      };
      var cardHtml = buildVideoCard(v);
      if (cardHtml) {
        var wrap = document.createElement('div');
        wrap.className = 'vid-section';
        wrap.style.cssText = 'margin-top:10px; margin-bottom:10px;';
        wrap.innerHTML = cardHtml;
        container.appendChild(wrap);
      }
      return;
    }

    // Podcast tag match: [podcast: url | title_no | title_th | title_en]
    var podMatch = block.match(/^\[podcast:\s*([^\|\]]+)(?:\|\s*([^\|\]]+))?(?:\|\s*([^\|\]]+))?(?:\|\s*([^\]]+))?\]$/i);
    if (podMatch) {
      var audioUrl = podMatch[1].trim();
      var titleNo = (podMatch[2] || '').trim();
      var titleTh = (podMatch[3] || '').trim();
      var titleEn = (podMatch[4] || '').trim();
      var p = {
        audio_url: audioUrl,
        title_no: titleNo,
        title_th: titleTh,
        title_en: titleEn
      };
      var cardHtml = buildPodcastCard(p);
      if (cardHtml) {
        var wrap = document.createElement('div');
        wrap.style.cssText = 'margin-top:10px; margin-bottom:10px;';
        wrap.innerHTML = cardHtml;
        container.appendChild(wrap);
      }
      return;
    }

    // Image tag match: [image: url | caption_no | caption_th | caption_en]
    var imgMatch = block.match(/^\[image:\s*([^\|\]]+)(?:\|\s*([^\|\]]+))?(?:\|\s*([^\|\]]+))?(?:\|\s*([^\]]+))?\]$/i);
    if (imgMatch) {
      var imgUrl = imgMatch[1].trim();
      var capNo = (imgMatch[2] || '').trim();
      var capTh = (imgMatch[3] || '').trim();
      var capEn = (imgMatch[4] || '').trim();

      var caption = appLang === 'th' ? capTh : appLang === 'en' ? capEn : capNo;
      var wrap = document.createElement('div');
      wrap.className = 'img-section';
      wrap.style.cssText = 'margin-top:10px; margin-bottom:10px; border-radius:11px; overflow:hidden; border:1px solid rgba(255,255,255,.08); background:rgba(255,255,255,.02); padding:8px;';

      var img = document.createElement('img');
      img.src = imgUrl;
      img.className = 'teacher-inline-image';
      wrap.appendChild(img);

      if (caption) {
        var capEl = document.createElement('div');
        capEl.className = 'teacher-inline-caption';
        capEl.textContent = caption;
        wrap.appendChild(capEl);
      }
      container.appendChild(wrap);
      return;
    }

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
        _teacherAppendBubble('assistant', fallback[appLang] || '');
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
  // No Norwegian fallback — chips show blank if the language attr is missing
  document.querySelectorAll('.teacher-chip').forEach(function(chip) {
    var lbl = chip.querySelector('.chip-lbl');
    if (!lbl) return;
    var msg = chip.getAttribute('data-msg-' + appLang) || '';
    lbl.textContent = msg.replace(/^[\S]{1,2}\s+/, ''); // strip leading emoji+space
    chip.dataset.msg = msg;
  });
}

function toggleTeacherTopics() {
  var suggestions = document.getElementById('teacherSuggestions');
  var button = document.getElementById('teacherMoreBtn');
  if (!suggestions || !button) return;
  var expanded = suggestions.classList.toggle('expanded');
  button.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  button.textContent = t(expanded ? 'teacher_fewer_topics' : 'teacher_more_topics');
}

function _teacherAppendBubble(role, text) {
  var msgs = document.getElementById('teacherMessages');
  if (!msgs) return;
  if (role === 'user') _teacherHasUserMsg = true;
  var row = document.createElement('div');
  row.className = 'tm-row ' + role;
  if (role === 'assistant') {
    var av = document.createElement('img');
    av.className = 'tm-av';
    av.src = '/api/assets/michael_profile.jpg';
    av.alt = 'Michael';
    row.appendChild(av);
  }
  var bubble = document.createElement('div');
  bubble.className = 'tm-bubble ' + role;
  if (role === 'assistant') {
    bubble.style.display = 'flex';
    bubble.style.flexDirection = 'column';
    _buildAssistantContent(text, bubble);

    // Append TTS Speaker button
    var ttsBtn = document.createElement('button');
    ttsBtn.className = 'tm-bubble-tts';
    ttsBtn.innerHTML = '🔊';
    ttsBtn.title = t('read_aloud');
    ttsBtn.onclick = function() {
      speakText(text);
    };
    bubble.appendChild(ttsBtn);
  } else {
    bubble.textContent = text;
  }
  row.appendChild(bubble);
  msgs.appendChild(row);
  if (_teacherHasUserMsg) {
    msgs.scrollTop = msgs.scrollHeight;
  } else {
    msgs.scrollTop = 0;
  }
}

function _teacherShowTyping() {
  var msgs = document.getElementById('teacherMessages');
  if (!msgs) return;
  var row = document.createElement('div');
  row.className = 'tm-row assistant';
  row.id = 'teacherTypingRow';
  var av = document.createElement('img');
  av.className = 'tm-av';
  av.src = '/api/assets/michael_profile.jpg';
  av.alt = 'Michael';
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
  chips.forEach(function(label, index) {
    var btn = document.createElement('button');
    btn.className = 'tm-chip-btn' + (index >= 3 ? ' mobile-extra' : '');
    btn.textContent = label;
    btn.onclick = function() { teacherSend(label); };
    row.appendChild(btn);
  });
  if (chips.length > 3) {
    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'tm-chips-toggle';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.textContent = t('teacher_more_topics');
    toggle.onclick = function() {
      var expanded = row.classList.toggle('expanded');
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      toggle.textContent = t(expanded ? 'teacher_fewer_topics' : 'teacher_more_topics');
    };
    row.appendChild(toggle);
  }
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
}

async function teacherSend(overrideMsg, customDisplayMsg) {
  var input = document.getElementById('teacherInput');
  var msg = (overrideMsg || (input && input.value) || '').trim();
  if (!msg || _teacherTyping) return;

  // Intercept in-app navigation chips
  var clean = msg.replace(/^[\S]{1,2}\s+/, '').trim().toLowerCase();
  if (clean === 'åpne studiebok' || clean === 'åpne bok' || clean === 'เปิดหนังสือเรียน' || clean === 'open study book') {
    if (input && !overrideMsg) input.value = '';
    showTab('studybook');
    return;
  }
  if (clean === 'min statistikk' || clean === 'สถิติของฉัน' || clean === 'my statistics') {
    if (input && !overrideMsg) input.value = '';
    showTab('history');
    return;
  }

  var isWeakTopic = (
    clean === 'hva bør jeg øve på?' || clean === 'hva bør jeg øve på' ||
    clean === 'ฉันควรฝึกเรื่องอะไร?' || clean === 'ฉันควรฝึกเรื่องอะไร' ||
    clean === 'what should i practise?' || clean === 'what should i practise' ||
    clean === 'what should i practice?' || clean === 'what should i practice'
  );

  var payloadMsg = msg;
  if (isWeakTopic) {
    var statsText = "No quiz attempts recorded yet.";
    if (deviceId) {
      try {
        var stats = await api('GET', '/api/stats/me?device_id=' + encodeURIComponent(deviceId));
        if (stats && stats.overall && stats.overall.total_q > 0) {
          var lines = [];
          lines.push("Overall Accuracy: " + Math.round(stats.overall.pct) + "% (" + stats.overall.total_correct + "/" + stats.overall.total_q + " correct across " + stats.overall.attempts + " attempts)");
          lines.push("\nAccuracy by category (sorted from lowest to highest):");
          if (Array.isArray(stats.by_category)) {
            stats.by_category.forEach(function(c) {
              var catDisplayName = catName(c.category);
              // AI context may keep the raw stats key as fallback; this is not visible UI text.
              var catContextName = catDisplayName || c.category || 'unknown category';
              lines.push("- " + catContextName + " (" + c.category + "): " + Math.round(c.pct) + "% accuracy (" + c.total_correct + "/" + c.total_q + " correct, " + c.attempts + " attempts)");
            });
          }
          statsText = lines.join("\n");
        }
      } catch(e) {
        console.error("Failed to fetch stats for Michael context:", e);
      }
    }
    payloadMsg = msg + '\n\n'
      + '<stats_context>\n'
      + 'STUDENT QUIZ PERFORMANCE AND STATISTICS:\n'
      + statsText + '\n'
      + '</stats_context>';
  }

  if (input && !overrideMsg) input.value = '';
  _teacherTyping = true;
  _teacherHideSuggestions();
  _teacherRemoveChips();  // clear old reply chips

  var sendBtn = document.getElementById('teacherSendBtn');
  if (sendBtn) sendBtn.disabled = true;

  _teacherAppendBubble('user', customDisplayMsg || msg);
  _teacherShowTyping();

  try {
    var activeSessionId = _teacherActiveSessionType === 'quiz' ? _teacherQuizSessionId : _teacherSessionId;
    var res = await fetch('/api/teacher/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: activeSessionId, message: payloadMsg, language: appLang })
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var data = await res.json();
    if (data.session_id) {
      if (_teacherActiveSessionType === 'quiz') {
        _teacherQuizSessionId = data.session_id;
      } else {
        _teacherSessionId = data.session_id;
      }
    }
    _teacherHideTyping();
    _teacherAppendBubble('assistant', data.reply || t('teacher_error'));
    _teacherAppendChips(data.suggestions || []);
    // Video card — show for math/braking topics (all languages)
    if (/reaksjonslengde|bremselengde|stoppelengde|reaksjonstid|alle formler|reaction distance|braking distance|stopping distance|ระยะตอบสนอง|ระยะปฏิกิริยา|ระยะเบรก|ระยะหยุดรถ|สูตรทั้งหมด/i.test(msg)) {
      fetchVideoForTopic('Bremsing').then(function(v) {
        if (!v) return;
        var msgs = document.getElementById('teacherMessages');
        if (!msgs) return;
        var rows = msgs.querySelectorAll('.tm-row.assistant');
        var lastRow = rows[rows.length - 1];
        if (!lastRow) return;
        var bubble = lastRow.querySelector('.tm-bubble');
        if (!bubble || bubble.querySelector('.vid-card')) return;
        var wrap = document.createElement('div');
        wrap.style.cssText = 'margin-top:10px;';
        wrap.innerHTML = buildVideoCard(v);
        bubble.appendChild(wrap);
        msgs.scrollTop = msgs.scrollHeight;
      });
    }
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

// ════════════════════════════════════════════
//  FORBIKJØRING — Overtaking distance tool
// ════════════════════════════════════════════

var _fkActive = 0; // currently selected scenario index

// Preset scenarios: { vA, vB, vC, dist, carLen, weatherNo, weatherTh, weatherEn, vehicleNo, vehicleTh, vehicleEn }
var FK_SCENARIOS = [
  { // 0 — Lett / Easy
    vA: 80, vB: 60, vC: 70, dist: 700,
    carLen: 5, safeGap: 40,
    weatherNo: '☀️ Sol og tørr vei', weatherTh: '☀️ แดดออก ถนนแห้ง', weatherEn: '☀️ Sunny, dry road',
    vehicleNo: '🚗 Personbil', vehicleTh: '🚗 รถยนต์', vehicleEn: '🚗 Car'
  },
  { // 1 — Middels / Medium
    vA: 90, vB: 70, vC: 80, dist: 500,
    carLen: 5, safeGap: 40,
    weatherNo: '🌥 Litt dårlig sikt', weatherTh: '🌥 ทัศนวิสัยไม่ดีนัก', weatherEn: '🌥 Reduced visibility',
    vehicleNo: '🚗 Personbil', vehicleTh: '🚗 รถยนต์', vehicleEn: '🚗 Car'
  },
  { // 2 — Vanskelig / Hard
    vA: 90, vB: 75, vC: 90, dist: 600,
    carLen: 20, safeGap: 40,
    weatherNo: '🌧 Regn', weatherTh: '🌧 ฝนตก', weatherEn: '🌧 Rain',
    vehicleNo: '🚛 Lastebil', vehicleTh: '🚛 รถบรรทุก', vehicleEn: '🚛 Lorry'
  }
];

function fkCalc(sc) {
  var speedDiffMs = (sc.vA - sc.vB) / 3.6;
  if (speedDiffMs <= 0) speedDiffMs = 0.1; // guard divide-by-zero
  var passRelDist = sc.carLen + sc.safeGap;         // metres to clear relative to car ahead
  var timeS       = passRelDist / speedDiffMs;       // seconds
  var yourDist    = Math.round((sc.vA / 3.6) * timeS);
  var oncomingDist= Math.round((sc.vC / 3.6) * timeS);
  var margin      = 50;                              // fixed safety margin metres
  var totalNeeded = yourDist + oncomingDist + margin;
  var freeRoad    = sc.dist - totalNeeded;
  return {
    timeS:        Math.round(timeS * 10) / 10,
    yourDist:     yourDist,
    oncomingDist: oncomingDist,
    margin:       margin,
    totalNeeded:  totalNeeded,
    freeRoad:     freeRoad,
    isSafe:   freeRoad > 80,
    isWarn:   freeRoad > 0 && freeRoad <= 80,
    isDanger: freeRoad <= 0
  };
}

function fkSelect(idx) {
  _fkActive = idx;
  ['fkBtnEasy','fkBtnMed','fkBtnHard'].forEach(function(id, i) {
    var b = document.getElementById(id);
    if (b) b.classList.toggle('active', i === idx);
  });
  fkRender();
}

function fkRender() {
  var sc = FK_SCENARIOS[_fkActive];
  var r  = fkCalc(sc);
  var L  = appLang;

  function w(no, th, en) { return L==='th' ? th : L==='en' ? en : no; }

  // Weather and vehicle label
  var weather = w(sc.weatherNo, sc.weatherTh, sc.weatherEn);
  var vehicle = w(sc.vehicleNo, sc.vehicleTh, sc.vehicleEn);

  // Info cells
  var infoHtml =
    '<div class="fk-info-row">'
      + _fkCell(t('fk_your_speed'),    sc.vA + ' km/t')
      + _fkCell(t('fk_ahead_speed'),   sc.vB + ' km/t &nbsp;' + vehicle)
    + '</div>'
    + '<div class="fk-info-row">'
      + _fkCell(t('fk_oncoming_dist'), sc.dist + ' m')
      + _fkCell(t('fk_weather'),       weather)
    + '</div>';

  // Calculation steps
  var stepsHtml =
    '<div class="fk-steps">'
      + '<div class="fk-steps-hdr">' + t('fk_steps_hdr') + '</div>'
      + _fkStep(t('fk_step_time'),   r.timeS + ' s',        '')
      + _fkStep(t('fk_step_your'),   r.yourDist + ' m',     'blue')
      + _fkStep(t('fk_step_onc'),    r.oncomingDist + ' m', 'red')
      + _fkStep(t('fk_step_margin'), r.margin + ' m',       'yel')
      + '<div style="height:1px;background:var(--border);margin:6px 0"></div>'
      + _fkStep(t('fk_step_need'),   r.totalNeeded + ' m',  '')
      + _fkStep(t('fk_step_free'),   (r.freeRoad > 0 ? '+' : '') + r.freeRoad + ' m', r.freeRoad > 0 ? 'grn' : 'red')
    + '</div>';

  // Distance bar
  var total    = Math.max(sc.dist, r.totalNeeded);
  var pct      = function(v) { return Math.max(1, Math.round(v / total * 100)); };
  var pYour    = pct(r.yourDist);
  var pMargin  = pct(r.margin);
  var pOnc     = pct(r.oncomingDist);
  var pFree    = r.freeRoad > 0 ? pct(r.freeRoad) : 0;
  var overflowHtml = r.isDanger
    ? '<div class="fk-bar-overflow">↑ ' + Math.abs(r.freeRoad) + ' m ' + w('for mye', 'มากเกินไป', 'too much') + '</div>'
    : '';

  var barHtml =
    '<div class="fk-bar-wrap">'
      + '<div class="fk-bar-hdr">' + t('fk_bar_hdr') + '</div>'
      + '<div class="fk-bar">'
        + '<div class="fk-bar-seg blue" style="width:' + pYour   + '%">' + (pYour   > 8 ? r.yourDist+'m'    : '') + '</div>'
        + '<div class="fk-bar-seg yel"  style="width:' + pMargin + '%">' + (pMargin > 5 ? r.margin+'m'      : '') + '</div>'
        + '<div class="fk-bar-seg red"  style="width:' + pOnc    + '%">' + (pOnc    > 8 ? r.oncomingDist+'m': '') + '</div>'
        + (pFree > 0 ? '<div class="fk-bar-seg grn" style="width:' + pFree + '%">' + (pFree > 8 ? r.freeRoad+'m' : '') + '</div>' : '')
      + '</div>'
      + overflowHtml
    + '</div>';

  // Result badge
  var resultKey  = r.isSafe ? 'fk_result_safe' : r.isWarn ? 'fk_result_warn' : 'fk_result_danger';
  var resultCls  = r.isSafe ? 'safe'            : r.isWarn ? 'warn'           : 'danger';
  var resultHtml = '<div class="fk-result ' + resultCls + '">' + t(resultKey) + '</div>';

  document.getElementById('fkBody').innerHTML = infoHtml + stepsHtml + barHtml + resultHtml;

  // Disclaimer
  var d = document.getElementById('fkDisclaimer');
  if (d) d.textContent = t('fk_disclaimer');
}

function _fkCell(lbl, val) {
  return '<div class="fk-info-cell"><div style="font-size:.73rem;color:var(--muted)">' + lbl + '</div>'
       + '<span class="fk-val">' + val + '</span></div>';
}
function _fkStep(lbl, val, cls) {
  return '<div class="fk-step"><span class="fk-step-lbl">' + lbl + '</span>'
       + '<span class="fk-step-val ' + cls + '">' + val + '</span></div>';
}

function fkToggleImg() {
  var panel  = document.getElementById('fkImgMobile');
  var btn    = document.getElementById('fkImgToggle');
  if (!panel) return;
  var open = panel.classList.toggle('open');
  if (btn) btn.textContent = (open ? '▲ ' : '👁 ') + t('fk_img_toggle').replace(/^👁\s*/, '');
}

function _fkUpdateStaticLabels() {
  var btnIds = ['fkBtnEasy','fkBtnMed','fkBtnHard'];
  var keys   = ['fk_scenario_easy','fk_scenario_med','fk_scenario_hard'];
  btnIds.forEach(function(id, i) {
    var b = document.getElementById(id);
    if (b) b.textContent = t(keys[i]);
  });
  var titleEl = document.getElementById('fkTitle');
  if (titleEl) titleEl.textContent = t('fk_title');
  var toggleBtn = document.getElementById('fkImgToggle');
  if (toggleBtn) {
    var open = document.getElementById('fkImgMobile') && document.getElementById('fkImgMobile').classList.contains('open');
    toggleBtn.textContent = (open ? '▲ ' : '👁 ') + t('fk_img_toggle').replace(/^👁\s*/, '');
  }
}

function showForbikjoring() {
  _fkUpdateStaticLabels();
  showScreen('screenForbikjoring');
  fkRender();
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
  stopAllSpeech();
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
  var name = _getProp(sign.name, lang) || '–';
  var code = sign.code || _signCode(sign);
  var clickId = JSON.stringify(sign.id || '').replace(/"/g, '&quot;');
  return '<button class="sp-related-card" type="button" onclick="openSignDetailById(' + clickId + ')">'
    + '<div class="sp-related-img">' + (sign.image_url ? '<img src="' + escH(sign.image_url) + '" alt="' + escH(name) + '" loading="lazy">' : '') + '</div>'
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
  if (imgEl) { imgEl.src = sign.image_url || ''; imgEl.alt = _getProp(sign.name, lang) || ''; }

  // Name
  var nameEl = document.getElementById('spName');
  if (nameEl) nameEl.textContent = _getProp(sign.name, lang) || _tIn('missing_text', lang);

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
  var sign = _signPanelData;
  if (!sign) return;
  var lang = _signPanelLang;
  var text = _getProp(sign.name, lang);
  var expl = _getProp(sign.explanation, lang);
  if (expl) text += '. ' + expl;
  text = text.trim();
  if (!text) return;

  stopAllSpeech();
  _ensureBackendAudio();
  _unlockAudioPlayback(_backendAudio);
  _backendAudio.src = ttsStreamUrl(text, lang);
  _backendAudio.playbackRate = ttsRate || 1.0;
  _backendAudio.volume = ttsVolume !== undefined ? ttsVolume : 1.0;
  _backendAudio.play().catch(function(err){ console.error('Sign TTS error:', err); });
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

// Lookup a UI key in a specific language (bypasses global appLang)
function _tIn(key, lang) {
  var e = UI[key];
  return (e && e[lang]) || key;
}

function askAiAboutSign() {
  var sign = _signPanelData;
  if (!sign) return;
  var lang = _signPanelLang;

  var name = _getProp(sign.name, lang) || '';
  var code = sign.code || _signCode(sign) || sign.id || '';
  var expl = _getProp(sign.explanation, lang) || _tIn('sign_fallback_meaning', lang);
  var driver = _getProp(sign.driverAction || sign.driver_action || sign.whyDangerous || sign.why_dangerous, lang)
               || _tIn('sign_fallback_driver', lang);
  var mistake = _getProp(sign.typicalMistake || sign.typical_mistake, lang)
               || _tIn('sign_fallback_mistake', lang);

  var prompt = "";
  if (lang === 'th') {
    prompt = "กรุณาอธิบายเกี่ยวกับป้ายจราจรนี้ให้ฉันฟังหน่อย:\n"
      + "- ชื่อป้าย: " + name + "\n"
      + "- รหัส/หมายเลขป้าย: " + code + "\n"
      + "- คำอธิบาย: " + expl + "\n"
      + "- สิ่งที่ผู้ขับขี่ต้องปฏิบัติ: " + driver + "\n"
      + "- ข้อผิดพลาดที่พบบ่อย: " + mistake;
  } else if (lang === 'no') {
    prompt = "Vennligst forklar dette trafikkskiltet for meg:\n"
      + "- Navn på skiltet: " + name + "\n"
      + "- Skiltnummer: " + code + "\n"
      + "- Forklaring: " + expl + "\n"
      + "- Hva føreren må gjøre: " + driver + "\n"
      + "- Vanlig feil: " + mistake;
  } else {
    prompt = "Please explain this traffic sign to me:\n"
      + "- Sign Name: " + name + "\n"
      + "- Sign Number/Code: " + code + "\n"
      + "- Explanation: " + expl + "\n"
      + "- Driver Action: " + driver + "\n"
      + "- Typical Mistake: " + mistake;
  }

  var displayMsg = _tIn('ask_ai', lang) + ": " + name;

  closeSignDetail();
  showTab('teacher');
  switchTeacherSession('normal');

  setTimeout(function() {
    teacherSend(prompt, displayMsg);
  }, 100);
}

function speakSignAiText() {
  if (!window._spAiText) return;
  var text = window._spAiText.trim();
  if (!text) return;
  stopAllSpeech();
  _ensureTeacherAudio();
  _unlockAudioPlayback(_teacherAudio);
  _teacherAudio.src = ttsStreamUrl(text, window._spAiLang || appLang);
  _teacherAudio.playbackRate = ttsRate || 1.0;
  _teacherAudio.volume = ttsVolume !== undefined ? ttsVolume : 1.0;
  _teacherAudio.play().catch(function(err){ console.error('Sign AI TTS error:', err); });
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

VOICE_TESTER_HTML = """<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Thai Voice Tester</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
  .card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 32px;
    width: 100%;
    max-width: 520px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
  }
  .logo { display:flex; align-items:center; gap:10px; margin-bottom:28px; }
  .logo-icon {
    width:40px; height:40px; border-radius:10px;
    background: linear-gradient(135deg,#8b5cf6,#6366f1);
    display:flex; align-items:center; justify-content:center;
    font-size:20px;
  }
  .logo h1 { font-size:1.15rem; font-weight:600; color:#fff; }
  .logo p { font-size:0.75rem; color:#666; }
  label { display:block; font-size:0.8rem; color:#888; margin-bottom:6px; font-weight:500; letter-spacing:.04em; text-transform:uppercase; }
  input, textarea {
    width:100%; background:#111; border:1px solid #2a2a2a;
    border-radius:8px; color:#e0e0e0; font-size:0.95rem;
    padding:11px 14px; outline:none; transition:border-color .2s;
    font-family: inherit;
  }
  input:focus, textarea:focus { border-color:#6366f1; }
  textarea { resize:vertical; min-height:120px; line-height:1.6; }
  .field { margin-bottom:18px; }
  .row { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  .btn {
    width:100%; padding:13px; border:none; border-radius:10px; cursor:pointer;
    font-size:1rem; font-weight:600; letter-spacing:.02em;
    background: linear-gradient(135deg,#8b5cf6,#6366f1);
    color:#fff; margin-top:8px; transition:opacity .2s, transform .1s;
  }
  .btn:hover { opacity:.9; }
  .btn:active { transform:scale(.98); }
  .btn:disabled { opacity:.45; cursor:not-allowed; }
  .status {
    margin-top:16px; padding:12px 14px; border-radius:8px;
    font-size:0.875rem; display:none;
  }
  .status.error { background:#2d1515; border:1px solid #5a1a1a; color:#f87171; display:block; }
  .status.ok { background:#142014; border:1px solid #1a4a1a; color:#86efac; display:block; }
  .status.loading { background:#1a1a2e; border:1px solid #2a2a5a; color:#a5b4fc; display:block; }
  audio { width:100%; margin-top:14px; border-radius:8px; display:none; }
  .hint { font-size:0.72rem; color:#555; margin-top:5px; }
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <div class="logo-icon">🎙️</div>
    <div>
      <h1>AI Thai Voice Tester</h1>
      <p>ElevenLabs · eleven_multilingual_v2</p>
    </div>
  </div>

  <div class="row">
    <div class="field">
      <label>ElevenLabs API Key</label>
      <input type="password" id="apiKey" placeholder="sk-..." autocomplete="off">
      <div class="hint">Aldri lagret — kun i nettleseren</div>
    </div>
    <div class="field">
      <label>Voice ID</label>
      <input type="text" id="voiceId" placeholder="21m00Tcm..." value="21m00Tcm4TlvDq8ikWAM">
    </div>
  </div>

  <div class="field">
    <label>Thai-tekst</label>
    <textarea id="thaiText">กรุณาหยุดรถที่ป้ายหยุดรถ แล้วมองซ้ายขวาก่อนออกตัว ขับรถด้วยความระมัดระวัง</textarea>
  </div>

  <button class="btn" id="genBtn" onclick="generate()">&#9654; Generer Lyd</button>
  <div class="status" id="status"></div>
  <audio controls id="player"></audio>
</div>

<script>
async function generate() {
  var key = document.getElementById('apiKey').value.trim();
  var voiceId = document.getElementById('voiceId').value.trim();
  var text = document.getElementById('thaiText').value.trim();
  var btn = document.getElementById('genBtn');
  var status = document.getElementById('status');
  var player = document.getElementById('player');

  if (!key) { showStatus('error', 'Skriv inn ElevenLabs API Key.'); return; }
  if (!voiceId) { showStatus('error', 'Skriv inn Voice ID.'); return; }
  if (!text) { showStatus('error', 'Skriv inn Thai-tekst.'); return; }

  btn.disabled = true;
  player.style.display = 'none';
  showStatus('loading', 'Genererer lyd...');

  try {
    var res = await fetch('https://api.elevenlabs.io/v1/text-to-speech/' + voiceId, {
      method: 'POST',
      headers: {
        'xi-api-key': key,
        'Content-Type': 'application/json',
        'Accept': 'audio/mpeg'
      },
      body: JSON.stringify({
        text: text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: { stability: 0.5, similarity_boost: 0.75 }
      })
    });

    if (!res.ok) {
      var err = await res.json().catch(function(){ return {}; });
      throw new Error(err.detail && err.detail.message ? err.detail.message : 'Status ' + res.status);
    }

    var blob = await res.blob();
    var url = URL.createObjectURL(blob);
    player.src = url;
    player.style.display = 'block';
    player.play();
    showStatus('ok', 'Lyd klar! Spilles av na.');
  } catch(e) {
    showStatus('error', 'Feil: ' + e.message);
  } finally {
    btn.disabled = false;
  }
}

function showStatus(type, msg) {
  var el = document.getElementById('status');
  el.className = 'status ' + type;
  el.textContent = msg;
}
</script>
</body>
</html>"""

@webapp_router.get("/web/voice-tester", response_class=HTMLResponse)
async def voice_tester():
    return HTMLResponse(content=VOICE_TESTER_HTML)
