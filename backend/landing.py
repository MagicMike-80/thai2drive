"""
High-conversion landing page for Thai2Drive.
Renders all 3 languages (th / no / en) inline — JS swaps visibility
so language switching is INSTANT with no server round-trip.
"""
from __future__ import annotations

ICON_URL = "/api/assets/t2d-logo.png"
HEADER_URL = "/api/assets/developer-header-4096x2304.jpg"

# ── YouTube video ─────────────────────────────────────────────
# Paste your YouTube video ID here (the part after ?v= in the URL)
# Leave empty to hide the video section
YOUTUBE_VIDEO_ID = "w0JQjoSes-M"  # Om Thai2Drive og Michael

# Phone screenshot paths (produced earlier)
SCREENSHOTS = [
    "/api/assets/screenshots/01-home-thai.jpg",
    "/api/assets/screenshots/04-quiz-question.jpg",
    "/api/assets/screenshots/03-categories.jpg",
    "/api/assets/screenshots/06-paywall.jpg",
    "/api/assets/screenshots/08-bookmarks.jpg",
]


LANDING_CSS = """
@property --neon-angle {
  syntax: '<angle>';
  inherits: false;
  initial-value: 0deg;
}

@keyframes neonFlow {
  from { --neon-angle: 0deg; }
  to   { --neon-angle: 360deg; }
}

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
.nav-links{list-style:none;display:flex;gap:20px;align-items:center;margin:0 auto}
.nav-links a{color:#CBD5E1;font-size:14px;font-weight:500;transition:color .15s}
.nav-links a:hover{color:#FF9933}
@media(max-width:600px){.nav-links{display:none}}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;color:#fff;flex-shrink:0}
.brand img{width:36px;height:36px;border-radius:8px}
.brand .t2d{color:#FF9933}
.lang-row{display:flex;gap:8px;align-items:center}
.lang-btn{
  width:44px;height:44px;border-radius:50%;
  border:2.5px solid rgba(255,255,255,.15);
  background:rgba(255,255,255,.06);
  cursor:pointer;padding:0;overflow:hidden;
  transition:border-color .15s,transform .15s,box-shadow .15s;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;position:relative;
}
.lang-btn:hover:not(.active){border-color:rgba(255,255,255,.4);transform:scale(1.08)}
.lang-btn.active{border-color:#FF9933;box-shadow:0 0 0 3px rgba(255,153,51,.3);transform:scale(1.1)}
/* SVG flags fill the button circle */
.cflag{width:100%;height:100%;display:block;position:absolute;inset:0}
.cflag svg{width:100%;height:100%;display:block}
/* Heartbeat animation — bump-bump ... pause */
@keyframes heartbeat{
  0%   {opacity:1}
  8%   {opacity:.2}
  16%  {opacity:1}
  26%  {opacity:.2}
  34%  {opacity:1}
  100% {opacity:1}
}
/* Guide — oransje hjertetakt */
.guide-blink{
  color:#FF9933!important;
  font-weight:800!important;
  animation:heartbeat 1.2s ease-in-out infinite;
  text-shadow:0 0 10px rgba(255,153,51,.7);
}
/* Sequential flag pulse — TH then NO then EN in loop */
@keyframes flagpulse{
  0%,100%   {transform:scale(1);    box-shadow:none; border-color:rgba(255,255,255,.2);}
  10%,40%   {transform:scale(1.08); box-shadow:0 0 0 3px rgba(255,153,51,.28),0 0 10px rgba(255,153,51,.15); border-color:#FF9933;}
  70%       {transform:scale(1);    box-shadow:none; border-color:rgba(255,255,255,.2);}
}
.lang-row .lang-btn:nth-child(1){ animation:flagpulse 6s ease-in-out infinite 0s; }
.lang-row .lang-btn:nth-child(2){ animation:flagpulse 6s ease-in-out infinite 2s; }
.lang-row .lang-btn:nth-child(3){ animation:flagpulse 6s ease-in-out infinite 4s; }
.lang-row .lang-btn.active{
  animation:none!important; transform:scale(1.15)!important;
  border:2px solid transparent !important;
  background:linear-gradient(rgba(15,23,42,0.9), rgba(15,23,42,0.9)) padding-box,
             conic-gradient(from var(--neon-angle, 0deg), #00F5FF 0%, #0066FF 25%, #FF00E5 50%, #FF9933 75%, #00F5FF 100%) border-box !important;
  box-shadow:0 0 12px rgba(255,153,51,.5), 0 0 20px rgba(0,245,255,.3)!important;
}
.landing-onboard-target{position:relative;border-radius:20px}
.landing-onboard-label{display:none;position:absolute;z-index:80;align-items:center;gap:10px;padding:12px 18px;border-radius:999px;background:#fff;border:3px solid rgba(255,153,51,.55);box-shadow:0 16px 34px rgba(0,0,0,.34),0 0 0 5px rgba(255,153,51,.16);color:#0F172A;font-size:20px;font-weight:950;line-height:1;letter-spacing:.01em;white-space:nowrap;pointer-events:auto;animation:landingLabelBlink 5s ease-in-out infinite}
.landing-onboard-label-lang{left:34%;top:-54px;transform:translateX(-50%) rotate(-5deg)}
.landing-onboard-label-web{left:50%;top:auto;bottom:calc(100% + 148px);transform:translateX(-50%) rotate(-4deg)}
.onboard-arrow{display:none;position:absolute;z-index:79;pointer-events:none;filter:drop-shadow(0 10px 16px rgba(0,0,0,.45))}
.onboard-arrow-lang{width:112px;height:100px;left:60%;top:-74px}
.onboard-arrow-web{width:86px;height:150px;left:50%;top:auto;bottom:calc(100% + 2px);transform:translateX(-50%)}
.landing-onboard-dismiss{width:24px;height:24px;border:0;border-radius:50%;background:rgba(15,23,42,.12);color:#0F172A;font-size:18px;font-weight:950;line-height:24px;cursor:pointer;padding:0;display:inline-flex;align-items:center;justify-content:center}
.landing-onboard-dismiss:hover{background:rgba(15,23,42,.22)}
html.landing-onboard-active .landing-onboard-label{display:inline-flex}
html.landing-onboard-active .landing-onboard-target{animation:landingOnboardPulse 5s ease-in-out infinite}
html.landing-onboard-active .onboard-arrow{display:block;animation:landingArrowBlink 5s ease-in-out infinite}
@keyframes landingOnboardPulse{0%,100%{box-shadow:0 0 0 0 rgba(255,153,51,.18)}50%{box-shadow:0 0 0 9px rgba(255,153,51,.28),0 0 36px rgba(255,153,51,.34)}}
@keyframes landingLabelBlink{0%,100%{opacity:1;box-shadow:0 16px 34px rgba(0,0,0,.34),0 0 0 5px rgba(255,153,51,.16)}50%{opacity:.45;box-shadow:0 10px 24px rgba(0,0,0,.24),0 0 0 2px rgba(255,153,51,.08)}}
@keyframes landingArrowBlink{0%,100%{opacity:1}50%{opacity:.45}}
@media(max-width:700px){.landing-onboard-label{font-size:28px;padding:13px 22px}.landing-onboard-label-lang{left:30%;top:-62px;transform:translateX(-50%) rotate(-8deg)}.landing-onboard-label-web{bottom:calc(100% + 168px);transform:translateX(-50%) rotate(-6deg)}.onboard-arrow-lang{width:130px;height:112px;left:58%;top:-84px}.onboard-arrow-web{width:100px;height:168px}}
@media(max-width:430px){.landing-onboard-label{font-size:23px}.landing-onboard-label-lang{left:28%;top:-54px}.landing-onboard-label-web{bottom:calc(100% + 146px)}.onboard-arrow-lang{width:112px;height:98px;left:60%;top:-72px}.onboard-arrow-web{width:88px;height:146px}}
@media(prefers-reduced-motion:reduce){html.landing-onboard-active .landing-onboard-target,.landing-onboard-label,.onboard-arrow{animation:none!important}}
.velg-hint{display:none}
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
.hero{padding:80px 0 64px;text-align:center;position:relative}
.hero::before{
  content:'';position:absolute;top:-20%;left:50%;transform:translateX(-50%);
  width:1200px;height:800px;background:radial-gradient(closest-side,rgba(22,40,95,.22),transparent 70%);
  pointer-events:none;z-index:-1;
}
.hero-icon{width:130px;height:130px;border-radius:32px;box-shadow:0 40px 100px rgba(0,0,0,.45);margin-bottom:28px}


/* Instrument Serif italic */
.serif-italic {
  font-family: 'Instrument Serif', Georgia, serif !important;
  font-style: italic !important;
}

/* Hero Section - Exact Approved Layout (v1.0: Mobil / iPad / PC / TV) */
.hero-wrap {
  position: relative;
  overflow: hidden;
  width: 100%;
  min-height: 640px;
  background-color: #07070A;
  display: flex;
  align-items: center;
}
@media (min-width: 768px) {
  .hero-wrap {
    background-image: url('/api/assets/hero-michael-sunset.webp');
    background-size: cover;
    background-position: 76% top;
    background-repeat: no-repeat;
    min-height: 640px;
  }
}
@media (min-width: 1024px) {
  .hero-wrap {
    background-position: right top;
    min-height: clamp(640px, 86vh, 880px);
  }
}
/* TV Breakpoint (1920px - 3840px): Crisp & smooth skin filter + fluid scaling */
@media (min-width: 1920px) {
  .hero-wrap {
    min-height: clamp(780px, 84vh, 1180px);
    image-rendering: -webkit-optimize-contrast;
    filter: contrast(1.02) saturate(1.03);
  }
}
.nav-badge-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  margin-left: 6px;
}
.eyebrow-dot-orange {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #FF6A2B;
  box-shadow: 0 0 10px rgba(255, 106, 43, 0.85);
  flex-shrink: 0;
}
.hero-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  background: linear-gradient(to right, #07070A 0%, rgba(7, 7, 10, 0.92) 22%, rgba(7, 7, 10, 0.45) 36%, transparent 48%);
}
.hero-overlay-top-bottom {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  background: linear-gradient(to bottom, rgba(7, 7, 10, 0.35) 0%, transparent 18%, transparent 82%, #07070A 100%);
}
.hero-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 1680px;
  margin: 0 auto;
  padding: 24px 28px 36px;
}
@media (min-width: 1024px) {
  .hero-container {
    padding: 28px 54px 34px;
  }
}
@media (min-width: 1920px) {
  .hero-container {
    max-width: 2100px;
    padding: 44px 80px;
  }
}
.hero-flex {
  display: grid;
  grid-template-columns: 1fr;
  align-items: center;
  gap: 24px;
}
/* iPad (768px - 1023px): 2 columns */
@media (min-width: 768px) and (max-width: 1023px) {
  .hero-flex {
    grid-template-columns: 45% 55%;
    gap: 20px;
  }
}
/* PC & TV (>=1024px) */
@media (min-width: 1024px) {
  .hero-flex {
    grid-template-columns: min(430px, 33vw) 1fr;
    gap: 40px;
  }
}
@media (min-width: 1920px) {
  .hero-flex {
    grid-template-columns: min(560px, 32vw) 1fr;
  }
}
.hero-left {
  max-width: 430px;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
@media (min-width: 1920px) {
  .hero-left {
    max-width: 560px;
    gap: 16px;
  }
}
.hero-eyebrow {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 9999px;
  padding: 5px 14px;
  font-size: clamp(11px, 0.85vw, 15px);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.hero-left h1, .hero-h1 {
  font-family: 'Geist', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 900;
  line-height: 0.92;
  letter-spacing: -0.04em;
  font-size: clamp(36px, 4.3vw, 68px);
  text-shadow: 0 2px 24px rgba(0, 0, 0, 0.65);
  margin: 0;
}
.hero-h1-white {
  color: #FFFFFF;
  display: block;
}
.hero-h2-orange {
  color: #FF6A2B;
  display: block;
  font-weight: 900;
}
.hero-subtext {
  font-family: 'Geist', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: clamp(13px, 1.05vw, 18px);
  line-height: 1.48;
  color: rgba(255, 255, 255, 0.78);
  max-width: 440px;
  margin: 0;
  font-weight: 400;
}
@media (min-width: 1920px) {
  .hero-subtext {
    max-width: 540px;
  }
}

/* Ring 2 — 8 Funksjoner Bunn Venstre */
.hero-features-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  max-width: 380px;
  margin-top: 4px;
}
@media (min-width: 1920px) {
  .hero-features-list {
    max-width: 480px;
    gap: 8px;
  }
}
.hero-feat-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 16px;
  border-radius: 10px;
  background: rgba(16, 20, 28, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.11);
  color: rgba(255, 255, 255, 0.92) !important;
  font-size: clamp(13px, 0.95vw, 18px);
  font-weight: 700;
  text-decoration: none !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: transform 0.16s ease, border-color 0.16s ease, background 0.16s ease, box-shadow 0.16s ease;
}
.hero-feat-pill:hover {
  transform: translateX(4px);
  background: rgba(28, 34, 46, 0.92);
  border-color: rgba(255, 106, 43, 0.45);
  text-decoration: none !important;
}
.hero-feat-pill .feat-num {
  color: #FF6A2B;
  font-weight: 800;
  min-width: 18px;
}
/* 1. Spør Michael AI — Størst, 1. plass, oransje glød */
.hero-feat-pill.highlight {
  padding: 9px 18px;
  font-size: clamp(15px, 1.15vw, 21px);
  font-weight: 800;
  color: #FFFFFF !important;
  background: linear-gradient(90deg, rgba(255, 106, 43, 0.34) 0%, rgba(255, 106, 43, 0.14) 100%);
  border: 1.5px solid rgba(255, 106, 43, 0.88);
  box-shadow: 0 0 28px rgba(255, 106, 43, 0.65), 0 0 12px rgba(255, 106, 43, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.22);
  transform: scale(1.04);
  transform-origin: left center;
  margin-bottom: 2px;
}
.hero-feat-pill.highlight:hover {
  transform: scale(1.05) translateX(3px);
  box-shadow: 0 0 34px rgba(255, 106, 43, 0.8), 0 0 16px rgba(255, 106, 43, 0.55);
}

/* Ring 1 — Interactive Hand Tags & 10s Video Popup */
.hero-right {
  position: relative;
  min-height: 540px;
}
@media (min-width: 1024px) {
  .hero-right {
    min-height: 600px;
  }
}
.hero-mobile-img {
  display: none;
}
.hand-tags-layer {
  position: absolute;
  inset: 0;
  z-index: 25;
  pointer-events: none;
}
.hand-tag-hotspot {
  position: absolute;
  pointer-events: auto;
  touch-action: manipulation;
  cursor: pointer;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.01);
  border: 2px solid transparent;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}
.hand-tag-hotspot:hover,
.hand-tag-hotspot.active {
  border-color: rgba(255, 106, 43, 0.85);
  box-shadow: 0 0 20px rgba(255, 106, 43, 0.55);
  transform: scale(1.04);
}
/* Positions aligned with the 3 speech bubbles near Michael's hand */
.hand-tag-hotspot.tag-easy {
  left: 9.5%;
  top: 16.5%;
  width: 204px;
  height: 76px;
}
.hand-tag-hotspot.tag-web {
  left: 15.5%;
  top: 27.5%;
  width: 214px;
  height: 76px;
}
.hand-tag-hotspot.tag-nett {
  left: 10%;
  top: 41%;
  width: 208px;
  height: 76px;
}

.hand-video-popup {
  position: absolute;
  left: 4%;
  top: 56%;
  z-index: 40;
  width: 290px;
  border-radius: 14px;
  overflow: hidden;
  background: rgba(10, 12, 18, 0.96);
  border: 1px solid rgba(255, 106, 43, 0.5);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85), 0 0 24px rgba(255, 106, 43, 0.3);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  pointer-events: auto;
  display: none;
}
.hand-video-popup.open {
  display: block;
  animation: fadeInPopup 0.18s ease-out;
}
@keyframes fadeInPopup {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.hvp-screen {
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, rgba(255, 106, 43, 0.22) 0%, rgba(15, 23, 42, 0.95) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px;
  text-align: center;
  position: relative;
}
.hvp-play-icon {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #FF6A2B;
  color: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 900;
  margin-bottom: 8px;
  box-shadow: 0 0 18px rgba(255, 106, 43, 0.7);
}
.hvp-title {
  font-size: 12px;
  font-weight: 800;
  color: #FFFFFF;
}
.hvp-sub {
  font-size: 10.5px;
  color: #CBD5E1;
  margin-top: 2px;
}
.hvp-meta {
  padding: 10px 12px;
  background: rgba(15, 18, 26, 0.98);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 10.5px;
  color: #94A3B8;
}
.hvp-bars {
  display: flex;
  gap: 5px;
  margin-top: 6px;
}
.hvp-bar-active {
  height: 4px;
  width: 44px;
  border-radius: 999px;
  background: #FF6A2B;
}
.hvp-bar-dim {
  height: 4px;
  width: 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
}

/* Mobil (320px - 767px) */
@media (max-width: 767px) {
  html, body { overflow-x: hidden; max-width: 100%; }
  .nav-inner { padding: 10px 12px !important; gap: 8px !important; }
  .brand { font-size: 16px !important; gap: 6px !important; }
  .brand img { width: 30px !important; height: 30px !important; }
  .lang-row { gap: 6px !important; }
  .lang-btn { width: 32px !important; height: 32px !important; }
  .hero-feat-pill.highlight { transform: none !important; }
  .hero-wrap {
    background-image: none !important;
    min-height: auto;
    padding: 8px 0 28px;
  }
  .hero-overlay, .hero-overlay-top-bottom {
    display: none;
  }
  .hero-container {
    padding: 12px 16px 24px;
  }
  .hero-flex {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  .hero-right {
    order: -1;
    width: 100%;
    min-height: auto;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55);
  }
  .hero-mobile-img {
    display: block;
    width: 100%;
    height: auto;
    object-fit: cover;
  }
  .hand-tag-hotspot.tag-easy { left: 10%; top: 22%; width: 24%; height: 11%; }
  .hand-tag-hotspot.tag-web { left: 17%; top: 34%; width: 25%; height: 11%; }
  .hand-tag-hotspot.tag-nett { left: 11%; top: 45%; width: 25%; height: 11%; }
  .hand-video-popup {
    left: 50%;
    top: 52%;
    transform: translateX(-50%);
    width: 88%;
    max-width: 300px;
  }
  .hero-left {
    max-width: 100%;
    width: 100%;
  }
  .hero-features-list {
    max-width: 100%;
  }
}

/* STATS */
.stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:24px;margin:56px 0}
.stat{text-align:center;padding:28px 16px;background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.11);border-radius:18px}
.stat-num{font-size:clamp(40px,6vw,72px);font-weight:900;color:#FF9933;letter-spacing:-.02em;line-height:1}
.stat-label{font-size:16px;color:#94A3B8;margin-top:8px;font-weight:500}

/* VIDEO GRID */
.video-section-wrap{position:relative;overflow:hidden}
.video-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:12px}
@media(max-width:768px){.video-grid{grid-template-columns:1fr}}
.vid-card{border-radius:16px;overflow:hidden;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);transition:transform .22s,box-shadow .22s;cursor:pointer}
.vid-card:hover{transform:translateY(-4px);box-shadow:0 20px 48px rgba(0,0,0,.45)}
.vid-thumb{position:relative;aspect-ratio:16/9;overflow:hidden}
.vid-thumb img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .3s}
.vid-card:hover .vid-thumb img{transform:scale(1.04)}
.vid-play{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.25);transition:background .2s}
.vid-card:hover .vid-play{background:rgba(0,0,0,.1)}
.vid-play-btn{width:54px;height:54px;border-radius:50%;background:rgba(255,153,51,.92);display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 6px 24px rgba(0,0,0,.4);transition:transform .2s}
.vid-card:hover .vid-play-btn{transform:scale(1.12)}
.vid-badge{position:absolute;top:10px;left:10px;background:rgba(255,153,51,.9);color:#0F172A;font-size:.65rem;font-weight:800;padding:3px 8px;border-radius:6px;letter-spacing:.5px;text-transform:uppercase}
.vid-info{padding:14px 16px 16px}
.vid-title{font-size:.88rem;font-weight:700;color:#E2E8F0;line-height:1.4;margin-bottom:6px}
.vid-meta{font-size:.72rem;color:#64748B;display:flex;align-items:center;gap:6px}
.vid-meta span{display:flex;align-items:center;gap:3px}
/* Lightbox */
.vid-lightbox{display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.88);align-items:center;justify-content:center;padding:20px}
.vid-lightbox.open{display:flex}
.vid-lightbox-inner{position:relative;width:100%;max-width:860px}
.vid-lightbox-inner iframe{width:100%;aspect-ratio:16/9;border:0;border-radius:14px}
.vid-lightbox-close{position:absolute;top:-44px;right:0;background:none;border:none;color:#fff;font-size:28px;cursor:pointer;opacity:.8;transition:opacity .2s}
.vid-lightbox-close:hover{opacity:1}
/* Premium teaser */
.vid-premium-teaser{margin-top:48px;border-radius:20px;padding:36px;background:linear-gradient(135deg,rgba(255,153,51,.08),rgba(255,153,51,.03));border:1px solid rgba(255,153,51,.18);text-align:center}
.vpt-icon{font-size:40px;margin-bottom:12px}
.vpt-title{font-size:1.35rem;font-weight:800;color:#E2E8F0;margin-bottom:8px}
.vpt-title span{color:#FF9933}
.vpt-sub{font-size:.88rem;color:#94A3B8;margin-bottom:24px}
.vpt-features{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;max-width:480px;margin:0 auto 28px;text-align:left}
@media(max-width:480px){.vpt-features{grid-template-columns:1fr}}
.vpt-feat{display:flex;align-items:center;gap:8px;font-size:.82rem;color:#CBD5E1;font-weight:600}
.vpt-feat span:first-child{font-size:1rem}
/* Floating icons */
.vid-float{position:absolute;pointer-events:none;opacity:.10;font-size:2rem;animation:vidFloat 6s ease-in-out infinite}
.vid-float:nth-child(1){top:8%;left:2%;animation-delay:0s;font-size:1.6rem}
.vid-float:nth-child(2){top:15%;right:3%;animation-delay:1.5s;font-size:2.2rem}
.vid-float:nth-child(3){bottom:20%;left:4%;animation-delay:3s;font-size:1.8rem}
.vid-float:nth-child(4){bottom:30%;right:2%;animation-delay:4.5s;font-size:1.4rem}
@keyframes vidFloat{0%,100%{transform:translateY(0) rotate(-4deg)}50%{transform:translateY(-14px) rotate(4deg)}}
/* legacy — keep for fallback */
.video-wrap{position:relative;max-width:860px;margin:0 auto;border-radius:20px;overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,.5);cursor:pointer}
.video-wrap iframe{width:100%;aspect-ratio:16/9;display:block;border:0}

/* SECTIONS */
section{padding:80px 0;position:relative}
.sec-head{text-align:center;max-width:800px;margin:0 auto 52px}
.eyebrow{display:inline-block;color:#FF9933;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:.12em;margin-bottom:14px}
.sec-head h2{font-size:clamp(36px,5.5vw,56px);font-weight:800;color:#fff;margin-bottom:14px;letter-spacing:-.02em}
.sec-head p{color:#94A3B8;font-size:20px;line-height:1.6}

/* TRY-IN-BROWSER */
.try-panel{
  max-width:1000px;width:90%;margin:0 auto;border-radius:24px;
  background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));
  border:1px solid rgba(255,255,255,.11);overflow:hidden;
}
.try-head{padding:16px 20px;display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.04);border-bottom:1px solid rgba(255,255,255,.08)}
.try-progress{color:#CBD5E1;font-size:13px;font-weight:700}
.try-progress .accent{color:#FF9933}
.try-bar{flex:1;height:5px;background:rgba(255,255,255,.08);border-radius:3px;margin:0 16px;overflow:hidden}
.try-bar>div{height:100%;background:#FF9933;transition:width .3s;width:0%}
.try-body{padding:16px 20px;display:grid;grid-template-columns:1fr 1fr auto;gap:20px;align-items:start}
.try-left{display:flex;flex-direction:column;gap:12px}
.try-right{display:flex;flex-direction:column;gap:10px}
.try-next-col{display:flex;align-items:center;justify-content:center}
.try-next-big{writing-mode:vertical-rl;text-orientation:mixed;padding:20px 14px;background:#FF9933;color:#0F172A;font-weight:800;font-size:15px;border:none;border-radius:14px;cursor:pointer;transition:background .2s,transform .1s;letter-spacing:0.05em;min-height:120px;width:48px;display:flex;align-items:center;justify-content:center}
.try-next-big:disabled{opacity:.35;cursor:not-allowed}
.try-next-big:not(:disabled):hover{background:#e6891f;transform:scale(1.04)}
.try-image{width:100%;max-height:200px;object-fit:contain;border-radius:10px;background:#0B1226}
.try-question{font-size:16px;font-weight:700;color:#fff;line-height:1.4}
.try-options{display:grid;gap:10px}
@media(max-width:700px){.try-body{grid-template-columns:1fr}.try-next-col{display:none}}
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
.try-foot{padding:12px 20px;border-top:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.try-next{padding:10px 24px;border-radius:10px;background:#FF9933;color:#0F172A;font-weight:800;border:none;cursor:pointer;font-size:14px}
.try-next:disabled{opacity:.4;cursor:not-allowed}
.try-loading{text-align:center;padding:60px 20px;color:#94A3B8}
.tts-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.tts-play{width:36px;height:36px;border-radius:50%;border:1.5px solid rgba(255,255,255,.15);background:rgba(255,255,255,.05);color:#E2E8F0;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:15px;transition:all .2s;flex-shrink:0}
.tts-play:hover{border-color:#FF9933;color:#FF9933}
.tts-play.playing{background:rgba(255,153,51,.2);border-color:#FF9933;color:#FF9933}
.tts-speed{padding:4px 10px;border-radius:20px;border:1px solid rgba(255,255,255,.1);background:transparent;color:#94A3B8;font-size:12px;font-weight:700;cursor:pointer;transition:all .2s}
.tts-speed:hover{border-color:#FF9933;color:#E2E8F0}
.tts-speed.active{background:rgba(255,153,51,.15);border-color:#FF9933;color:#FF9933}
.sound-toggle{padding:5px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04);color:#94A3B8;font-size:12px;font-weight:700;cursor:pointer;transition:all .2s}
.sound-toggle.on{border-color:#FF9933;color:#FF9933;background:rgba(255,153,51,.1)}

/* Paywall shown inline after 10 */
.try-paywall{text-align:center;padding:40px 24px}
.try-paywall h3{font-size:24px;color:#fff;margin-bottom:10px;font-weight:800}
.try-paywall p{color:#94A3B8;margin-bottom:24px;max-width:440px;margin-left:auto;margin-right:auto}
.try-paywall .lock-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;background:rgba(255,153,51,.15);color:#FF9933;border-radius:999px;font-size:12px;font-weight:700;margin-bottom:14px}
.plans-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;max-width:640px;margin:0 auto 20px}
.plan-mini{background:rgba(255,255,255,.04);border:1.5px solid rgba(255,255,255,.1);border-radius:12px;padding:16px;text-align:left}
.plan-mini.best{border-color:#FF9933;background:rgba(255,153,51,.08)}
.plan-mini h4{font-size:13px;color:#94A3B8;font-weight:600;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em}
.plan-mini .p{font-size:22px;color:#fff;font-weight:800}
.plan-mini .p small{font-size:11px;color:#94A3B8;font-weight:500}

/* Why Thai2Drive */
.why-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}
.why-item{
  background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.11);
  padding:28px 26px;border-radius:18px;display:flex;align-items:center;gap:20px;
  transition:border-color .2s,background .2s,transform .2s;
}
.why-item:hover{border-color:rgba(255,153,51,.3);background:rgba(255,153,51,.04);transform:translateY(-3px)}
.why-num{
  flex-shrink:0;width:52px;height:52px;border-radius:50%;
  background:rgba(255,153,51,.15);color:#FF9933;
  display:flex;align-items:center;justify-content:center;
  font-weight:900;font-size:22px;
}
.why-item h3{color:#fff;font-size:20px;font-weight:700;line-height:1.3}

/* FEATURES */
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px}
.feat{
  background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.11);
  padding:32px;border-radius:20px;transition:all .2s;
}
.feat:hover{border-color:rgba(255,153,51,.3);background:rgba(255,153,51,.03);transform:translateY(-3px)}
.feat-icon{width:56px;height:56px;border-radius:14px;background:rgba(255,153,51,.15);color:#FF9933;display:flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:18px}
.feat h3{font-size:22px;color:#fff;font-weight:700;margin-bottom:10px}
.feat p{color:#94A3B8;font-size:17px;line-height:1.6}

/* TRUST */
.trust{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px}
.trust-card{
  text-align:center;padding:32px 24px;background:rgba(255,255,255,.055);
  border:1px solid rgba(255,255,255,.11);border-radius:18px;
}
.trust-icon{font-size:44px;margin-bottom:14px}
.trust-card h4{color:#fff;font-size:20px;font-weight:700;margin-bottom:8px}
.trust-card p{color:#94A3B8;font-size:17px;line-height:1.5}

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
  background:linear-gradient(180deg,rgba(22,40,95,.28) 0%,rgba(11,18,38,.70) 100%);
  border-top:1px solid rgba(255,255,255,.09);border-bottom:1px solid rgba(255,255,255,.06);
  text-align:center;padding:80px 24px;
}
.cta-band h2{font-size:clamp(32px,5vw,52px);color:#fff;font-weight:800;margin-bottom:14px;letter-spacing:-.02em}
.cta-band p{color:#94A3B8;max-width:560px;margin:0 auto 28px;font-size:20px}

/* FOOTER */
footer{padding:40px 0 32px;border-top:1px solid rgba(255,255,255,.06);margin-top:40px}
.footer-inner{display:flex;justify-content:space-between;flex-wrap:wrap;gap:20px;align-items:center}
footer p{color:#64748B;font-size:13px}
.footer-links{display:flex;gap:18px;flex-wrap:wrap}
.footer-links a{color:#94A3B8;font-size:13px}

/* LANGUAGE HINT */
.lang-hint{
  position:fixed;top:62px;right:24px;z-index:200;
  display:flex;flex-direction:column;align-items:center;
  pointer-events:none;
  transition:opacity .4s ease;
}
.lang-hint.hidden{opacity:0}
.lang-hint-bubble{
  background:#FF9933;color:#0F172A;
  font-weight:800;font-size:14px;
  padding:10px 18px;border-radius:12px;
  box-shadow:0 8px 24px rgba(255,153,51,.45);
  white-space:nowrap;text-align:center;line-height:1.5;
}
.lang-hint-arrow{
  font-size:24px;color:#FF9933;margin-top:2px;
  animation:bounceUp .6s ease-in-out infinite alternate;
}
@keyframes bounceUp{from{transform:translateY(0)}to{transform:translateY(-6px)}}
@media(max-width:600px){.lang-hint{right:12px;top:58px}}

/* ROAD PHOTOS */
.road-section{padding:72px 0 56px}
.road-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:40px;border-radius:24px;overflow:hidden}
.road-img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;transition:transform .4s ease}
.road-img:hover{transform:scale(1.03)}
.road-frame{overflow:hidden;border-radius:16px;position:relative}
.road-frame::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(11,18,38,.35),transparent 50%);pointer-events:none}
@media(max-width:600px){.road-grid{grid-template-columns:1fr;gap:12px}}

/* RESPONSIVE */
@media (max-width:720px){
  .nav-inner{padding:10px 14px;gap:8px}
  .brand{font-size:16px}
  .brand img{width:32px;height:32px}
  .lang-btn{width:36px;height:36px}
  .hero{padding:48px 0 40px}
  section{padding:52px 0}
  .cta-band{padding:48px 20px}
  .qr-box{flex-direction:column;text-align:center;padding:16px}
  .qr-text{max-width:none;text-align:center}
  .shot{width:190px;border-width:2px}
}

/* ═══════════════════════════════════════════
   NEON DESIGN — Thai2Drive Marketing Page
   Cyan #00F5FF · Magenta #FF00E5 · Gold #FFD700
   ═══════════════════════════════════════════ */
:root{
  --neon-cyan:#00F5FF;
  --neon-magenta:#FF00E5;
  --neon-gold:#FFD700;
  --neon-cyan-glow:rgba(0,245,255,.4);
  --neon-gold-glow:rgba(255,215,0,.4);
  --neon-magenta-glow:rgba(255,0,229,.35);
}

/* Aurora hero glow */
.hero::before{
  background:
    radial-gradient(ellipse 900px 500px at 30% 60%,rgba(0,245,255,.07),transparent 65%),
    radial-gradient(ellipse 700px 400px at 75% 40%,rgba(255,0,229,.06),transparent 65%),
    radial-gradient(ellipse 600px 300px at 50% 20%,rgba(255,215,0,.05),transparent 60%)!important;
  width:100%;height:900px;top:-10%!important;
}

/* Hero h1 highlight word */
.hero h1 em{color:var(--neon-gold);text-shadow:0 0 28px var(--neon-gold-glow),0 0 8px var(--neon-gold-glow)}

/* Section eyebrow labels */
.eyebrow{color:var(--neon-magenta)!important;text-shadow:0 0 14px var(--neon-magenta-glow)}

/* Stats numbers */
.stat-num{color:var(--neon-gold)!important;text-shadow:0 0 22px var(--neon-gold-glow),0 0 6px var(--neon-gold-glow)}
.stat{border-color:rgba(0,245,255,.12)!important;box-shadow:inset 0 0 24px rgba(0,245,255,.03)}

/* Feature icon + card */
.feat-icon{background:rgba(0,245,255,.12)!important;color:var(--neon-cyan)!important;box-shadow:0 0 18px rgba(0,245,255,.15)}
.feat:hover{border-color:rgba(0,245,255,.35)!important;background:rgba(0,245,255,.03)!important;box-shadow:0 8px 32px rgba(0,245,255,.08)}

/* Why-section number circles */
.why-num{background:rgba(0,245,255,.12)!important;color:var(--neon-cyan)!important;box-shadow:0 0 14px rgba(0,245,255,.18)}
.why-item:hover{border-color:rgba(255,0,229,.3)!important;background:rgba(255,0,229,.03)!important}

/* Primary CTA button — cyan glow */
.cta-primary{
  border:2px solid transparent !important;
  background:linear-gradient(135deg,#00F5FF,#0066FF) padding-box,
             conic-gradient(from var(--neon-angle, 0deg), #00F5FF 0%, #0066FF 25%, #FF00E5 50%, #FF9933 75%, #00F5FF 100%) border-box !important;
  animation:neonFlow 3.5s linear infinite !important;
  color:#0B1226!important;
  box-shadow:0 0 32px rgba(0,245,255,.5), 0 0 20px rgba(255,0,229,.35) !important;
}
.cta-primary:hover{
  transform:translateY(-2px) scale(1.02);
  box-shadow:0 0 48px rgba(0,245,255,.7), 0 0 32px rgba(255,0,229,.5) !important;
}
.cta-secondary{
  border:1.5px solid transparent !important;
  background:linear-gradient(rgba(17,24,39,0.95), rgba(17,24,39,0.95)) padding-box,
             conic-gradient(from var(--neon-angle, 0deg), #00F5FF 0%, #0066FF 25%, #FF00E5 50%, #FF9933 75%, #00F5FF 100%) border-box !important;
  animation:neonFlow 3.5s linear infinite !important;
  color:#F1F5F9!important;
  box-shadow:0 0 14px rgba(0,245,255,.35), 0 0 10px rgba(255,0,229,.25) !important;
}
.cta-secondary:hover{
  border-color:transparent !important;
  box-shadow:0 0 24px rgba(0,245,255,.55), 0 0 32px rgba(255,0,229,.45) !important;
  transform:translateY(-2px);
}

/* Try panel — next buttons */
.try-next-big{background:linear-gradient(180deg,var(--neon-cyan),#00C8E8)!important;color:#0B1226!important;box-shadow:0 0 20px var(--neon-cyan-glow)}
.try-next-big:not(:disabled):hover{background:linear-gradient(180deg,#18FFFF,var(--neon-cyan))!important}
.try-next{background:linear-gradient(135deg,var(--neon-cyan),#00C8E8)!important;color:#0B1226!important;box-shadow:0 0 16px var(--neon-cyan-glow)}
.try-bar>div{background:linear-gradient(90deg,var(--neon-cyan),var(--neon-magenta))!important}
.try-progress .accent{color:var(--neon-cyan)!important}
.try-opt:hover{border-color:rgba(0,245,255,.45)!important}

/* TTS play button */
.tts-play:hover,.tts-play.playing{border-color:var(--neon-cyan)!important;color:var(--neon-cyan)!important}
.tts-speed:hover{border-color:var(--neon-cyan)!important;color:#E2E8F0!important}
.tts-speed.active{background:rgba(0,245,255,.12)!important;border-color:var(--neon-cyan)!important;color:var(--neon-cyan)!important}
.sound-toggle.on{border-color:var(--neon-cyan)!important;color:var(--neon-cyan)!important;background:rgba(0,245,255,.08)!important}

/* Video play button */
.vid-play-btn{background:rgba(0,245,255,.88)!important;box-shadow:0 0 24px var(--neon-cyan-glow),0 6px 24px rgba(0,0,0,.4)!important}
.vid-badge{background:rgba(0,245,255,.85)!important;color:#0B1226!important}
.vid-card:hover{box-shadow:0 20px 48px rgba(0,0,0,.45),0 0 28px rgba(0,245,255,.12)!important}

/* Guide blink */
.guide-blink{color:var(--neon-gold)!important;text-shadow:0 0 12px var(--neon-gold-glow)!important}

/* Lang hint bubble */
.lang-hint-bubble{background:linear-gradient(135deg,var(--neon-cyan),#00C8E8)!important;color:#0B1226!important;box-shadow:0 8px 24px var(--neon-cyan-glow)!important}
.lang-hint-arrow{color:var(--neon-cyan)!important}

/* Paywall lock badge */
.try-paywall .lock-badge{background:rgba(0,245,255,.12)!important;color:var(--neon-cyan)!important}
.plan-mini.best{border-color:var(--neon-cyan)!important;background:rgba(0,245,255,.06)!important}

/* Premium video teaser */
.vid-premium-teaser{background:linear-gradient(135deg,rgba(0,245,255,.07),rgba(255,0,229,.04))!important;border-color:rgba(0,245,255,.2)!important}
.vpt-title span{color:var(--neon-cyan)!important}

/* CTA band */
.cta-band{background:linear-gradient(180deg,rgba(0,245,255,.05) 0%,rgba(11,18,38,.80) 100%)!important}

/* Nav web-app button */
.nav-links a[href^="/app/"]{
  background:linear-gradient(135deg,var(--neon-cyan),#00C8E8)!important;
  color:#0B1226!important;
  box-shadow:0 0 16px rgba(0,245,255,.3)!important;
}

/* Onboard pulse colours */
@keyframes landingOnboardPulse{0%,100%{box-shadow:0 0 0 0 rgba(0,245,255,.18)}50%{box-shadow:0 0 0 9px rgba(0,245,255,.28),0 0 36px rgba(0,245,255,.34)}}
.landing-onboard-label{border-color:rgba(0,245,255,.55)!important;box-shadow:0 16px 34px rgba(0,0,0,.34),0 0 0 5px rgba(0,245,255,.16)!important}

/* Flag pulse → cyan */
@keyframes flagpulse{
  0%,100%   {transform:scale(1);    box-shadow:none; border-color:rgba(255,255,255,.2);}
  10%,40%   {transform:scale(1.08); box-shadow:0 0 0 3px rgba(0,245,255,.28),0 0 10px rgba(0,245,255,.15); border-color:var(--neon-cyan);}
  70%       {transform:scale(1);    box-shadow:none; border-color:rgba(255,255,255,.2);}
}
.lang-row .lang-btn.active{border-color:var(--neon-cyan)!important;box-shadow:0 0 0 3px rgba(0,245,255,.4)!important}
"""


def _nav_html(lang: str = "th", app_query: str = "") -> str:
    return f"""
<nav class="nav">
  <div class="nav-inner">
    <a href="/{lang}" class="brand">
      <img src="{ICON_URL}" alt="T2D"/>
      <span>Thai<span class="t2d">2</span>Drive</span>
      <span class="nav-badge-pill">Lære</span>
    </a>
    <ul class="nav-links">
      <li><a href="#features">
        <span data-lang="th">ฟีเจอร์</span>
        <span data-lang="no">Funksjoner</span>
        <span data-lang="en">Features</span>
      </a></li>
      <li><a href="#pricing">
        <span data-lang="th">ราคา</span>
        <span data-lang="no">Priser</span>
        <span data-lang="en">Pricing</span>
      </a></li>
      <li><a href="/{lang}/guide" class="guide-blink">📖 <span data-lang="th">คู่มือ</span><span data-lang="no">Veiledning</span><span data-lang="en">Guide</span></a></li>
      <li><a href="/{lang}/app{app_query}" style="display:inline-flex;align-items:center;gap:6px;background:#FF9933;color:#0F172A;font-weight:800;font-size:13px;padding:7px 14px;border-radius:8px;transition:opacity .15s" onmouseover="this.style.opacity='.85'" onmouseout="this.style.opacity='1'">⚡ <span data-lang="th">เปิดเว็บแอป</span><span data-lang="no">Åpne web-appen</span><span data-lang="en">Open web app</span></a></li>
      <li><a href="https://www.facebook.com/profile.php?id=61565991554372" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:6px;color:#CBD5E1">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.267h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/></svg>
        Facebook
      </a></li>
      <li><a href="https://www.tiktok.com/@thai2drive.no?_r=1&amp;_t=ZN-9AuRT4Jd5S2" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:6px;color:#CBD5E1">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#FFFFFF"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64c.298-.002.595.042.88.13V9.4a6.33 6.33 0 0 0-1-.08A6.34 6.34 0 0 0 3 15.66a6.34 6.34 0 0 0 10.82 4.47 6.27 6.27 0 0 0 1.95-4.47V8.62a8.27 8.27 0 0 0 4.82 1.54V6.69z"/></svg>
        TikTok
      </a></li>
    </ul>
    <div class="lang-row" role="group" aria-label="Language">
      <button class="lang-btn{' active' if lang == 'th' else ''}" data-set-lang="th" title="ภาษาไทย">
        <span class="cflag"><svg viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg"><rect width="900" height="600" fill="#A51931"/><rect width="900" height="480" y="60" fill="#F4F5F8"/><rect width="900" height="320" y="140" fill="#241D4F"/></svg></span>
      </button>
      <button class="lang-btn{' active' if lang == 'no' else ''}" data-set-lang="no" title="Norsk">
        <span class="cflag"><svg viewBox="0 0 22 16" xmlns="http://www.w3.org/2000/svg"><rect width="22" height="16" fill="#EF2B2D"/><rect x="6" width="4" height="16" fill="#fff"/><rect y="6" width="22" height="4" fill="#fff"/><rect x="7" width="2" height="16" fill="#002868"/><rect y="7" width="22" height="2" fill="#002868"/></svg></span>
      </button>
      <button class="lang-btn{' active' if lang == 'en' else ''}" data-set-lang="en" title="English">
        <span class="cflag"><svg viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg"><rect width="60" height="30" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" stroke-width="4"/><rect y="11" width="60" height="8" fill="#fff"/><rect x="26" width="8" height="30" fill="#fff"/><rect y="12" width="60" height="6" fill="#C8102E"/><rect x="27" width="6" height="30" fill="#C8102E"/></svg></span>
      </button>
    </div>
  </div>
</nav>
"""


def _footer_html(lang: str = "th") -> str:
    return f"""
<footer>
  <div class="container">
    <div class="footer-inner">
      <p>© 2025 Thai2Drive</p>
      <div class="lang-row" role="group" aria-label="Language" style="justify-content:center;margin:12px 0">
        <button class="lang-btn{' active' if lang == 'th' else ''}" data-set-lang="th" title="ภาษาไทย">
          <span class="cflag cflag-th"></span>
        </button>
        <button class="lang-btn{' active' if lang == 'no' else ''}" data-set-lang="no" title="Norsk">
          <span class="cflag cflag-no"><span class="nb nb1"></span><span class="nb nb2"></span></span>
        </button>
        <button class="lang-btn{' active' if lang == 'en' else ''}" data-set-lang="en" title="English">
          <span class="cflag cflag-gb"><span class="gb1"></span><span class="gb2"></span></span>
        </button>
      </div>
      <div class="footer-links">
        <a href="/{lang}"><span data-lang="th">หน้าแรก</span><span data-lang="no">Hjem</span><span data-lang="en">Home</span></a>
        <a href="/privacy"><span data-lang="th">ความเป็นส่วนตัว</span><span data-lang="no">Personvern</span><span data-lang="en">Privacy</span></a>
        <a href="/terms"><span data-lang="th">เงื่อนไข</span><span data-lang="no">Vilkår</span><span data-lang="en">Terms</span></a>
        <a href="/support"><span data-lang="th">ช่วยเหลือ</span><span data-lang="no">Support</span><span data-lang="en">Support</span></a>
      </div>
    </div>
  </div>
</footer>
"""


def _hero_html(lang: str = "th", app_query: str = "") -> str:
    return f"""
<section class="hero-wrap">
  <div class="hero-overlay"></div>
  <div class="hero-overlay-top-bottom"></div>
  <div class="hero-container">
    <div class="hero-flex">
      <div class="hero-left">
        <!-- Eyebrow badge -->
        <div class="hero-eyebrow">
          <span class="eyebrow-dot-orange"></span>
          <span data-lang="th">สร้างโดยครูสอนขับรถที่ได้รับการรับรอง — อธิบายเป็นภาษาไทย</span>
          <span data-lang="no">Laget av godkjent trafikklærer — forklar på thai</span>
          <span data-lang="en">Made by certified driving instructor — explains in Thai</span>
        </div>

        <!-- H1 Heading: White + Orange Heavy Sans -->
        <h1>
          <span class="hero-h1-white block">
            <span data-lang="th">ทฤษฎีภาษาไทย</span>
            <span data-lang="no">Teori på thai.</span>
            <span data-lang="en">Theory in Thai.</span>
          </span>
          <span class="hero-h2-orange block">
            <span data-lang="no">Trygg på</span>
          </span>
          <span class="hero-h2-orange block">
            <span data-lang="th">ขับขี่ปลอดภัยบนถนนนอร์เวย์</span>
            <span data-lang="no">norsk vei.</span>
            <span data-lang="en">Safe on Norwegian roads.</span>
          </span>
        </h1>

        <p class="hero-subtext">
          <span data-lang="th">ผ่านการสอบทฤษฎีได้เร็วขึ้น ครูไมเคิลอธิบายทุกอย่างเป็นภาษาไทย — สถานการณ์จริงบนถนนนอร์เวย์ ข้อสอบกว่า 1000+ ข้อ และดูแลเป็นรายบุคคล</span>
          <span data-lang="no">Bestå teoriprøven raskere. Michael forklarer alt på thai – med ekte norske veisituasjoner, 1000+ spørsmål og personlig oppfølging.</span>
          <span data-lang="en">Pass the theory test faster. Michael explains everything in Thai — real Norwegian road scenarios, 1000+ questions, and personal coaching.</span>
        </p>

        <!-- Ring 2: 8 Funksjoner Bunn Venstre (Låst rekkefølge, #1 størst med oransje glød) -->
        <div class="hero-features-list">
          <a href="/{lang}/app{app_query}" class="hero-feat-pill highlight">
            <span class="feat-num">1.</span>
            <span data-lang="th">ถาม Michael AI</span>
            <span data-lang="no">Spør Michael AI</span>
            <span data-lang="en">Ask Michael AI</span>
          </a>
          <a href="/{lang}/app{app_query}" class="hero-feat-pill">
            <span class="feat-num">2.</span>
            <span data-lang="th">เริ่มทำแบบทดสอบรายวัน</span>
            <span data-lang="no">Start quiz / daglig test</span>
            <span data-lang="en">Start quiz / daily test</span>
          </a>
          <a href="/{lang}/app{app_query}" class="hero-feat-pill">
            <span class="feat-num">3.</span>
            <span data-lang="th">ข้อสอบจำลอง 45 ข้อ - 90 นาที</span>
            <span data-lang="no">Øvingsprøve 45 spm - 90 min</span>
            <span data-lang="en">Practice test 45 Q - 90 min</span>
          </a>
          <a href="/{lang}/app{app_query}" class="hero-feat-pill">
            <span class="feat-num">4.</span>
            <span data-lang="th">ระยะเบรก</span>
            <span data-lang="no">Stopplengde</span>
            <span data-lang="en">Braking distance</span>
          </a>
          <a href="#videos" class="hero-feat-pill">
            <span class="feat-num">5.</span>
            <span data-lang="th">วิดีโอคอร์ส &amp; พอดแคสต์</span>
            <span data-lang="no">Videokurs &amp; Podkaster</span>
            <span data-lang="en">Video course &amp; Podcasts</span>
          </a>
          <a href="/{lang}/app{app_query}" class="hero-feat-pill">
            <span class="feat-num">6.</span>
            <span data-lang="th">ฝึกจากข้อผิดพลาด &amp; ป้ายจราจร</span>
            <span data-lang="no">Øv på mine feil &amp; skiltkatalog</span>
            <span data-lang="en">Practice my mistakes &amp; sign catalog</span>
          </a>
          <a href="/{lang}/app{app_query}" class="hero-feat-pill">
            <span class="feat-num">7.</span>
            <span data-lang="th">ฝึกคำศัพท์จราจร</span>
            <span data-lang="no">Øv på trafikkbegreper</span>
            <span data-lang="en">Practice traffic terms</span>
          </a>
          <a href="/{lang}/app{app_query}" class="hero-feat-pill">
            <span class="feat-num">8.</span>
            <span data-lang="th">Flipp Flopp - มีเสียง &amp; เกม</span>
            <span data-lang="no">Flipp Flopp</span>
            <span data-lang="en">Flipp Flopp - with sound &amp; game feel</span>
          </a>
        </div>
      </div>

      <!-- HERO RIGHT COLUMN: Ring 1 Hand Tags + Ring 3 Portrait -->
      <div class="hero-right">
        <img src="/api/assets/hero-michael-card.webp" alt="Michael S. Trafikklærer" class="hero-mobile-img" />
        <div class="hand-tags-layer">
          <button type="button" class="hand-tag-hotspot tag-easy" data-tag-id="easy" aria-label="เพื่อง่าย Video Preview"></button>
          <button type="button" class="hand-tag-hotspot tag-web" data-tag-id="web" aria-label="Web App Video Preview"></button>
          <button type="button" class="hand-tag-hotspot tag-nett" data-tag-id="nett" aria-label="Nett-App Video Preview"></button>
          <div class="hand-video-popup" id="handVideoPopup" role="dialog" aria-label="Video preview">
            <div class="hvp-screen">
              <div class="hvp-play-icon">▶</div>
              <div class="hvp-title">
                <span data-lang="th">วิดีโอเร็วๆ นี้ - 10 วินาที</span>
                <span data-lang="no">Video kommer snart - 10 sec</span>
                <span data-lang="en">Video coming soon - 10 sec</span>
              </div>
              <div class="hvp-sub" id="hvpTagLabel">Walkthrough • 1080p</div>
            </div>
            <div class="hvp-meta">
              <div>
                <span data-lang="th">VO: เสียงครูไมเคิลผ่าน 11Labs • 3 ภาษา</span>
                <span data-lang="no">VO: Michaels stemme via 11Labs • Samme video, 3 språk VO</span>
                <span data-lang="en">VO: Michael's voice via 11Labs • Same video, 3 languages VO</span>
              </div>
              <div class="hvp-bars">
                <span class="hvp-bar-active"></span>
                <span class="hvp-bar-dim"></span>
                <span class="hvp-bar-dim"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
"""


def _try_html(lang: str) -> str:
    les_hoyt = {"no": "Les høyt", "th": "อ่านออกเสียง", "en": "Read aloud"}.get(lang, "Les høyt")
    return f"""
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
        <div class="tts-row">
          <button class="tts-play" id="tqTtsBtn" title="{les_hoyt}">▶</button>
          <button class="tts-speed" data-rate="0.5">0.5x</button>
          <button class="tts-speed" data-rate="0.75">0.75x</button>
          <button class="tts-speed active" data-rate="1">1x</button>
          <button class="tts-speed" data-rate="1.5">1.5x</button>
          <button class="tts-speed" data-rate="2">2x</button>
          <button class="sound-toggle on" id="tqSoundToggle">🔊</button>
        </div>
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


def _stats_html() -> str:
    return """
<section style="padding:0 0 40px">
  <div class="container">
    <div class="stats-row">
      <div class="stat">
        <div class="stat-num">1000+</div>
        <div class="stat-label">
          <span data-lang="th">คำถาม</span>
          <span data-lang="no">spørsmål</span>
          <span data-lang="en">questions</span>
        </div>
      </div>
      <div class="stat">
        <div class="stat-num">3</div>
        <div class="stat-label">
          <span data-lang="th">ภาษา</span>
          <span data-lang="no">språk</span>
          <span data-lang="en">languages</span>
        </div>
      </div>
      <div class="stat">
        <div class="stat-num">45</div>
        <div class="stat-label">
          <span data-lang="th">ข้อสอบจริง</span>
          <span data-lang="no">eksamens­spørsmål</span>
          <span data-lang="en">exam questions</span>
        </div>
      </div>
    </div>
  </div>
</section>
"""


def _video_html(lang: str = "th") -> str:
    # 3 free public videos — build trust, show value
    FREE_VIDEOS = [
        {
            "id":    "O5y_dN6-bTs",
            "no":    "Høyreregelen og myndighetspyramiden",
            "th":    "กฎทางขวาและลำดับชั้นสัญญาณจราจร",
            "en":    "Right-Hand Rule & Authority Hierarchy",
            "dur":   "1:43",
        },
        {
            "id":    "EzAcXro21xI",
            "no":    "9 viktige skiltgrupper i Norge",
            "th":    "9 กลุ่มป้ายจราจรสำคัญในนอร์เวย์",
            "en":    "9 Important Sign Groups in Norway",
            "dur":   "",
        },
        {
            "id":    "w0JQjoSes-M",
            "no":    "Historien bak Thai2Drive",
            "th":    "เรื่องราวเบื้องหลัง Thai2Drive",
            "en":    "The Story Behind Thai2Drive",
            "dur":   "",
        },
    ]

    cards_html = ""
    for v in FREE_VIDEOS:
        thumb = f"https://img.youtube.com/vi/{v['id']}/hqdefault.jpg"
        dur_html = f'<span>▶ {v["dur"]}</span>' if v["dur"] else ""
        alt_text = v.get(lang, v.get("no", ""))
        cards_html += f"""
      <div class="vid-card" onclick="openVidLightbox('{v['id']}')">
        <div class="vid-thumb">
          <img src="{thumb}" alt="{alt_text}" loading="lazy">
          <div class="vid-play"><div class="vid-play-btn">▶</div></div>
          <div class="vid-badge">
            <span data-lang="th">ฟรี</span>
            <span data-lang="no">Gratis</span>
            <span data-lang="en">Free</span>
          </div>
        </div>
        <div class="vid-info">
          <div class="vid-title">
            <span data-lang="th">{v['th']}</span>
            <span data-lang="no">{v['no']}</span>
            <span data-lang="en">{v['en']}</span>
          </div>
          <div class="vid-meta">{dur_html}</div>
        </div>
      </div>"""

    # Premium course list (locked — not public)
    premium_courses = [
        ("🛑", {
            "th": "ระยะเบรกและเวลาตอบสนอง",
            "no": "Bremselengde og reaksjonstid",
            "en": "Braking distance and reaction time",
        }),
        ("🚦", {
            "th": "สัญญาณไฟจราจรและกฎการให้ทาง",
            "no": "Trafikklys og vikeplikt",
            "en": "Traffic lights and right of way",
        }),
        ("↙️", {
            "th": "การเลี้ยวซ้ายและวงเวียน",
            "no": "Venstresving og rundkjøring",
            "en": "Left turns and roundabouts",
        }),
        ("🚌", {
            "th": "รถบัสออกจากป้าย",
            "no": "Buss fra holdeplass",
            "en": "Bus leaving a bus stop",
        }),
        ("🧠", {
            "th": "การสอนด้วย AI",
            "no": "AI-undervising",
            "en": "AI tutoring",
        }),
    ]
    feat_html = ""
    for icon, texts in premium_courses:
        feat_html += f'<div class="vpt-feat"><span>{icon}</span><span><span data-lang="th">{texts["th"]}</span><span data-lang="no">{texts["no"]}</span><span data-lang="en">{texts["en"]}</span></span></div>'

    return f"""
<section>
  <div class="container">
    <div class="sec-head">
      <span class="eyebrow">
        <span data-lang="th">วิดีโอ</span>
        <span data-lang="no">Video</span>
        <span data-lang="en">Video</span>
      </span>
      <h2>
        <span data-lang="th" class="block">เรียนรู้ก่อนสอบ</span>
        <span data-lang="no" class="block">Lær av videoene</span>
        <span data-lang="en" class="block">Learn from the videos</span>
      </h2>
      <p>
        <span data-lang="th">คำอธิบายเป็นภาษาไทย — เข้าใจง่าย ไม่ต้องเดา</span>
        <span data-lang="no">Forklaringer på thai — lett å forstå, ingen gjetning</span>
        <span data-lang="en">Explanations in Thai — easy to understand, no guessing</span>
      </p>
    </div>

    <!-- Floating decorative icons -->
    <div class="video-section-wrap">
      <span class="vid-float">🚗</span>
      <span class="vid-float">🛑</span>
      <span class="vid-float">🚦</span>
      <span class="vid-float">🧠</span>

      <!-- 3-column video grid -->
      <div class="video-grid">{cards_html}
      </div>

      <!-- Premium teaser -->
      <div class="vid-premium-teaser">
        <div class="vpt-icon">💎</div>
        <div class="vpt-title">
          <span data-lang="th">อยากเรียนรู้เพิ่มเติมไหม?</span>
          <span data-lang="no">Vil du lære <span>mer</span>?</span>
          <span data-lang="en">Want to learn <span>more</span>?</span>
        </div>
        <div class="vpt-sub">
          <span data-lang="th">1000+ คำถาม · AI ครู · ป้ายจราจร · ไทย นอร์เวย์ อังกฤษ · คอร์สวิดีโอ Premium</span>
          <span data-lang="no">1000+ spørsmål · AI-lærer · Trafikkskilt · Thai, norsk og engelsk · Premium videokurs</span>
          <span data-lang="en">1000+ questions · AI teacher · Traffic signs · Thai, Norwegian and English · Premium video courses</span>
        </div>
        <div class="vpt-features">{feat_html}</div>
        <a href="#pricing" class="cta-btn" style="display:inline-flex;text-decoration:none">
          <span data-lang="th">⭐ ดู Premium</span>
          <span data-lang="no">⭐ Se Premium</span>
          <span data-lang="en">⭐ See Premium</span>
        </a>
      </div>
    </div>

  </div>
</section>

<!-- Video lightbox -->
<div class="vid-lightbox" id="vidLightbox" onclick="if(event.target===this)closeVidLightbox()">
  <div class="vid-lightbox-inner">
    <button class="vid-lightbox-close" onclick="closeVidLightbox()">✕</button>
    <iframe id="vidLightboxFrame" src="" allowfullscreen
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
    </iframe>
  </div>
</div>
<script>
function openVidLightbox(id) {{
  document.getElementById('vidLightboxFrame').src =
    'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&modestbranding=1';
  document.getElementById('vidLightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}}
function closeVidLightbox() {{
  document.getElementById('vidLightboxFrame').src = '';
  document.getElementById('vidLightbox').classList.remove('open');
  document.body.style.overflow = '';
}}
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') closeVidLightbox();
}});
</script>
"""


def _pricing_html(lang: str, app_query: str = "") -> str:
    # Labels already used by the landing page. Prices come from the public
    # pricing endpoint; no duplicated amounts or checkout logic live here.
    heading = {"th": "ราคา", "no": "Priser", "en": "Pricing"}[lang]
    cta = {"th": "เปิดเว็บแอป", "no": "Åpne webappen", "en": "Open web app"}[lang]
    return f"""
<section id="pricing" style="scroll-margin-top:90px">
  <div class="container" style="text-align:center">
    <div class="sec-head"><h2>{heading}</h2></div>
    <div class="plans-row" id="publicPricingPlans" aria-live="polite"></div>
    <a href="/{lang}/app{app_query}" class="cta-btn cta-primary">{cta} →</a>
  </div>
</section>
"""


PUBLIC_PRICING_JS = r"""
(function(){
  const container = document.getElementById('publicPricingPlans');
  if (!container) return;
  const lang = document.documentElement.getAttribute('data-current-lang');
  fetch('/api/pricing', {cache:'no-store'})
    .then(response => { if (!response.ok) throw new Error('pricing'); return response.json(); })
    .then(data => {
      const plans = Array.isArray(data.plans) ? data.plans : [];
      ['monthly', 'three_months', 'lifetime'].forEach(id => {
        const plan = plans.find(item => item && item.id === id);
        const label = plan && plan.label && plan.label[lang];
        const period = plan && plan.period && plan.period[lang];
        if (!plan || typeof label !== 'string' || !label ||
            typeof period !== 'string' || !period || typeof plan.display !== 'string' || !plan.display) return;
        const card = document.createElement('div');
        card.className = id === 'three_months' ? 'plan-mini best' : 'plan-mini';
        if (id === 'three_months') {
          const badge = document.createElement('div');
          badge.textContent = {no:'Beste verdi', th:'คุ้มค่าที่สุด', en:'Best value'}[lang] || '';
          card.appendChild(badge);
        }
        const title = document.createElement('h4');
        title.textContent = label;
        const price = document.createElement('div');
        price.className = 'p';
        price.textContent = plan.display;
        const duration = document.createElement('small');
        duration.textContent = ' / ' + period;
        price.appendChild(duration);
        card.appendChild(title);
        card.appendChild(price);
        container.appendChild(card);
      });
    }).catch(() => { container.replaceChildren(); });
})();
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
        ('📚', {'th': '1000+ คำถาม', 'no': '1000+ spørsmål', 'en': '1000+ questions'},
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


def _road_photos_html(lang: str = "th") -> str:
    alts = {
        "th": "วงเวียนในนอร์เวย์",
        "no": "Rundkjøring Norge",
        "en": "Roundabout in Norway",
    }
    alt_text = alts.get(lang, "วงเวียนในนอร์เวย์")
    return f"""
<section class="road-section">
  <div class="container">
    <div class="sec-head">
      <span class="eyebrow">
        <span data-lang="th">🇳🇴 ถนนในนอร์เวย์</span>
        <span data-lang="no">🇳🇴 Norske veier</span>
        <span data-lang="en">🇳🇴 Norwegian roads</span>
      </span>
      <h2>
        <span data-lang="th" class="block">เรียนรู้เส้นทางจริงในนอร์เวย์</span>
        <span data-lang="no" class="block">Lær deg norske veier og rundkjøringer</span>
        <span data-lang="en" class="block">Learn real Norwegian roads & roundabouts</span>
      </h2>
      <p>
        <span data-lang="th">คำถามในแอปใช้ภาพจริงจากถนนในนอร์เวย์</span>
        <span data-lang="no">Spørsmålene i appen bruker ekte bilder fra norske veier</span>
        <span data-lang="en">Questions in the app use real images from Norwegian roads</span>
      </p>
    </div>
    <div class="road-grid">
      <div class="road-frame">
        <img src="/api/assets/rundkjoring1.jpg" alt="{alt_text}" class="road-img" loading="lazy"/>
      </div>
      <div class="road-frame">
        <img src="/api/assets/rundkjoring2.jpg" alt="{alt_text}" class="road-img" loading="lazy"/>
      </div>
    </div>
  </div>
</section>
"""


def _bottom_cta_html(lang: str = "th", app_query: str = "") -> str:
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
      <a href="/{lang}/app{app_query}" class="cta-btn cta-secondary">
        💻 <span data-lang="th">เปิดเว็บแอป</span><span data-lang="no">Åpne web-appen</span><span data-lang="en">Open web app</span>
      </a>
    </div>
  </div>
</section>
"""


LANDING_JS = r"""
// ─── First-visit onboarding highlight ───
(function(){
  var KEY = 't2d_landing_onboarding_dismissed';
  var root = document.documentElement;
  var timer = null;

  function hideOnboarding(){
    root.classList.remove('landing-onboard-active');
    try { sessionStorage.setItem(KEY, '1'); } catch(e) {}
    if(timer) clearTimeout(timer);
  }

  try {
    if(sessionStorage.getItem(KEY) === '1') return;
  } catch(e) {}

  root.classList.add('landing-onboard-active');
  timer = setTimeout(hideOnboarding, 10000);

  document.querySelectorAll('.landing-onboard-dismiss').forEach(function(btn){
    btn.addEventListener('click', function(ev){
      ev.preventDefault();
      ev.stopPropagation();
      hideOnboarding();
    });
  });
})();


// ─── Ring 1: Hand Tags Hover (PC) & Tap (Mobil/iPad) Video Popup ───
(function(){
  var popup = document.getElementById('handVideoPopup');
  var subLbl = document.getElementById('hvpTagLabel');
  var hotspots = document.querySelectorAll('.hand-tag-hotspot');
  if (!popup || !hotspots.length) return;
  var labels = {
    easy: 'เพื่อง่าย • Walkthrough',
    web: 'Web App • PWA Walkthrough',
    nett: 'Nett-App • Norsk Walkthrough'
  };
  var pinned = null;
  function showTag(id) {
    if (subLbl && labels[id]) subLbl.textContent = labels[id];
    popup.classList.add('open');
    hotspots.forEach(function(h){ h.classList.toggle('active', h.getAttribute('data-tag-id') === id); });
  }
  function hideTag() {
    popup.classList.remove('open');
    hotspots.forEach(function(h){ h.classList.remove('active'); });
  }
  hotspots.forEach(function(btn){
    var id = btn.getAttribute('data-tag-id');
    btn.addEventListener('mouseenter', function(){
      if (window.matchMedia('(min-width: 1024px)').matches) showTag(id);
    });
    btn.addEventListener('mouseleave', function(){
      if (window.matchMedia('(min-width: 1024px)').matches && !pinned) hideTag();
    });
    btn.addEventListener('click', function(ev){
      ev.preventDefault();
      ev.stopPropagation();
      if (pinned === id) { pinned = null; hideTag(); }
      else { pinned = id; showTag(id); }
    });
  });
  document.addEventListener('click', function(ev){
    if (pinned && !popup.contains(ev.target)) {
      pinned = null;
      hideTag();
    }
  });
})();

// ─── Language switcher ───
// The server already rendered this exact URL (/th, /no or /en) in the right
// language, so on load we just sync storage to match it — no client-side
// override of data-current-lang here. Clicking a flag navigates to the
// sibling-language URL for the CURRENT page (t2dSwitchLang, see <head>).
(function(){
  const current = document.documentElement.getAttribute('data-current-lang') || 'th';
  localStorage.setItem('t2d_landing_lang', current);
  document.cookie = 't2d_site_lang=' + current + ';path=/;max-age=31536000;SameSite=Lax';
  document.querySelectorAll('.lang-btn').forEach(b=>b.classList.toggle('active', b.dataset.setLang===current));
  document.querySelectorAll('.lang-wrap').forEach(w=>w.classList.toggle('active', w.dataset.wrapLang===current));

  document.querySelectorAll('.lang-btn').forEach(btn=>{
    btn.addEventListener('click', ()=> t2dSwitchLang(btn.dataset.setLang));
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

  const TOTAL = 10;
  let questions = [];
  let idx = 0;
  let score = 0;
  let answered = false;
  let ttsRate = 1;
  let soundOn = true;
  let ttsPlaying = false;

  // ── Sound effects via Web Audio API ──
  function playSound(type) {
    if (!soundOn) return;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (type === 'correct') {
        // Long high pling
        [523.25, 659.25, 783.99].forEach((freq, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain); gain.connect(ctx.destination);
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.12);
          gain.gain.setValueAtTime(0.35, ctx.currentTime + i * 0.12);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 1.1);
          osc.start(ctx.currentTime + i * 0.12);
          osc.stop(ctx.currentTime + i * 0.12 + 1.1);
        });
      } else {
        // Wrong — low buzz
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(180, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.35);
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 0.4);
      }
    } catch(e) {}
  }

  let _landingAudio = null;

  // ── TTS ──
  function speakText(text) {
    var wasPlaying = ttsPlaying;
    stopAllSpeech();
    if (wasPlaying) return;
    
    if (!_landingAudio) {
      _landingAudio = new Audio();
      _landingAudio.onended = () => { ttsPlaying = false; updateTtsBtn(); };
      _landingAudio.onerror = () => { ttsPlaying = false; updateTtsBtn(); };
    }
    
    // Always Thai on landing page try-quiz
    _landingAudio.src = '/api/tts?lang=th-TH&text=' + encodeURIComponent(text);
    _landingAudio.playbackRate = ttsRate || 1.0;
    
    ttsPlaying = true;
    updateTtsBtn();
    _landingAudio.play().catch(err => {
      console.error('Landing TTS failed:', err);
      ttsPlaying = false;
      updateTtsBtn();
    });
  }

  function updateTtsBtn() {
    const btn = document.getElementById('tqTtsBtn');
    if (btn) { btn.textContent = ttsPlaying ? '⏸' : '▶'; btn.classList.toggle('playing', ttsPlaying); }
  }

  // Stop speech when the user leaves the page (close, navigate away, switch app/tab)
  function stopAllSpeech() {
    if (_landingAudio) { try { _landingAudio.pause(); } catch(e){} }
    ttsPlaying = false;
    updateTtsBtn();
  }
  window.addEventListener('pagehide', stopAllSpeech);
  window.addEventListener('beforeunload', stopAllSpeech);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopAllSpeech(); });

  // ── Sound toggle ──
  const soundToggle = document.getElementById('tqSoundToggle');
  if (soundToggle) soundToggle.addEventListener('click', () => {
    soundOn = !soundOn;
    soundToggle.textContent = soundOn ? '🔊' : '🔇';
    soundToggle.classList.toggle('on', soundOn);
  });

  // ── Speed chips ──
  document.querySelectorAll('.tts-speed').forEach(btn => {
    btn.addEventListener('click', () => {
      ttsRate = parseFloat(btn.dataset.rate);
      document.querySelectorAll('.tts-speed').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // ── TTS play button ──
  const ttsBtn = document.getElementById('tqTtsBtn');
  if (ttsBtn) ttsBtn.addEventListener('click', () => {
    const q = questions[idx];
    if (!q) return;
    const text = pick(q.question, 'th');
    speakText(text);
  });

  function currentLang(){
    return document.documentElement.getAttribute('data-current-lang') || 'th';
  }

  function showLoadError(){
    // Reuse the approved webapp load_error labels, without a language fallback.
    const labels = {th:'โหลดไม่สำเร็จ', no:'Feil ved lasting', en:'Loading failed'};
    const message = document.createElement('p');
    message.style.cssText = 'text-align:center;color:#94A3B8;padding:30px';
    message.setAttribute('role', 'status');
    message.textContent = labels[currentLang()] || '';
    body.replaceChildren(message);
  }

  async function load(){
    try{
      // Image questions ONLY — filter out any without a valid base64/url image
      const res = await fetch('/api/questions/random?count=15&has_image=true');
      const raw = await res.json();
      questions = (raw || []).filter(q => q.bildeUrl && (typeof q.bildeUrl === 'string' || Object.keys(q.bildeUrl).length)).slice(0, TOTAL + 2);
      if(questions.length === 0){
        showLoadError();
        return;
      }
      totalEl.textContent = TOTAL;
      render();
    }catch(e){
      showLoadError();
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

    const nextLbl = { th: 'ต่อไป →', no: 'Neste →', en: 'Next →' }[lang] || 'Next →';
    body.innerHTML =
      `<div class="try-left">` +
      (img ? `<img class="try-image" src="${img}" alt="" onerror="this.style.display='none'"/>` : '') +
      `<div class="try-question">${escapeHtml(questionText)}</div>` +
      `</div>` +
      `<div class="try-right">` +
      `<div class="try-options" id="tqOpts">` +
      opts.map(o => `<button class="try-opt" data-id="${o.id}"><span class="letter">${o.id}</span><span>${escapeHtml(o.text)}</span></button>`).join('') +
      `</div>` +
      `<div class="try-hint" id="tqHint" style="display:none"></div>` +
      `<div class="try-explain" id="tqExpl" style="display:none"></div>` +
      `</div>` +
      `<div class="try-next-col"><button class="try-next-big" id="tqNextBig" disabled>${nextLbl}</button></div>`;

    document.querySelectorAll('#tqOpts .try-opt').forEach(btn=>{
      btn.addEventListener('click', ()=>selectAnswer(btn, q, expl));
    });
    nextBtn.disabled = true;
    const bigNext = document.getElementById('tqNextBig');
    if(bigNext){ bigNext.disabled = true; bigNext.onclick = ()=>{ idx++; render(); }; }
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
    if(picked === correct){ score++; playSound('correct'); } else { playSound('wrong'); }
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
    const bigNext2 = document.getElementById('tqNextBig');
    if(bigNext2){ bigNext2.disabled = false; }
  }

  function renderPaywall(){
    const lang = currentLang();
    barEl.style.width = '100%';
    nowEl.textContent = TOTAL;
    const titles = {
      th: 'ฝึกต่อในเว็บแอป',
      no: 'Fortsett øvingen i webappen',
      en: 'Continue practicing in the web app',
    };
    const subs = {
      th: 'เปิดเว็บแอปเพื่อเข้าถึงคำถามทั้งหมด 1000+ ข้อ พร้อมคำอธิบายและโหมดสอบจริง',
      no: 'Åpne webappen for tilgang til alle 1000+ spørsmål, forklaringer og ekte eksamensmodus.',
      en: 'Open the web app for access to all 1000+ questions, explanations, and real exam mode.',
    };
    const ctas = {
      th: 'เปิดเว็บแอป',
      no: 'Åpne webappen',
      en: 'Open web app',
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
          <div class="plan-mini"><h4>${monthLbl}</h4><div class="p">99 kr<small> / ${perMo}</small></div></div>
          <div class="plan-mini best"><div>${{no:'Beste verdi', th:'คุ้มค่าที่สุด', en:'Best value'}[lang] || ''}</div><h4>${threeLbl}</h4><div class="p">249 kr<small> / 3 ${perMo}</small></div></div>
          <div class="plan-mini"><h4>${lifeLbl}</h4><div class="p">699 kr<small> / ${once}</small></div></div>
        </div>
        <a href="/${lang}/app${new URLSearchParams(window.location.search).get('campaign') === 'free30' ? '?campaign=free30' : ''}" class="cta-btn cta-primary" style="margin-top:8px">${ctas[lang]} →</a>
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


def build_landing_page(chat_css: str, chat_widget_html: str, chat_js: str, lang: str = "th", campaign: str = "") -> str:
    """Build the full landing HTML including the existing chat bubble.

    `lang` is the language this specific URL (/th, /no, /en) serves — it drives
    the server-rendered <html lang>, title, meta description, hreflang tags, and
    server-side language filtering so search crawlers never see mixed language.
    """
    # Local import to avoid circular + keep module import cheap.
    from site_config import public_site_url
    from i18n_routing import (
        normalize_lang, HTML_LANG, OG_LOCALE, seo_meta, hreflang_tags, canonical_for, LANG_SWITCH_JS,
        filter_landing_html,
    )
    lang = normalize_lang(lang)
    app_query = "?campaign=free30" if campaign == "free30" else ""
    meta = seo_meta("home", lang)
    canon = canonical_for(lang, "")
    og_image = public_site_url() + HEADER_URL  # absolute URL for social previews
    alt_locales = "".join(
        f'<meta property="og:locale:alternate" content="{OG_LOCALE[l]}"/>\n'
        for l in ("th", "no", "en") if l != lang
    )
    raw_html = f"""<!doctype html>
<html lang="{HTML_LANG[lang]}" data-current-lang="{lang}">
<head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800;900&family=Noto+Sans+Thai:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{meta['title']}</title>
<meta name="description" content="{meta['description']}"/>
<link rel="canonical" href="{canon}"/>
{hreflang_tags("")}
<meta property="og:title" content="{meta['title']}"/>
<meta property="og:description" content="{meta['description']}"/>
<meta property="og:image" content="{og_image}"/>
<meta property="og:url" content="{canon}"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="Thai2Drive"/>
<meta property="og:locale" content="{OG_LOCALE[lang]}"/>
<meta name="google" content="notranslate"/>
<meta http-equiv="Content-Language" content="{lang}"/>
{alt_locales}<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{meta['title']}"/>
<meta name="twitter:description" content="{meta['description']}"/>
<meta name="twitter:image" content="{og_image}"/>
<link rel="icon" type="image/png" href="{ICON_URL}"/>
<link rel="apple-touch-icon" href="{ICON_URL}"/>
<style>{LANDING_CSS}{chat_css}</style>
<script>{LANG_SWITCH_JS}</script>
</head>
<body>
{_nav_html(lang, app_query)}
{_hero_html(lang, app_query)}
{_stats_html()}
{_try_html(lang)}
{_video_html(lang)}
{_pricing_html(lang, app_query)}
{_why_html()}
{_features_html()}
{_screenshots_html()}
{_road_photos_html(lang)}
{_trust_html()}
{_bottom_cta_html(lang, app_query)}
{_footer_html(lang)}
{chat_widget_html}
<script>{LANDING_JS}</script>
<script>{PUBLIC_PRICING_JS}</script>
<script>{chat_js}</script>
</body>
</html>"""
    return filter_landing_html(raw_html, lang)

