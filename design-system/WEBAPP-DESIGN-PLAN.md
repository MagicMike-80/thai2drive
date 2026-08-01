# Thai2Drive Web App — Design Blueprint

> **Dato:** 2026-07-04
> **Stil:** Dark Navy Cyborg — Premium e-læring med neon-estetikk
> **Stack:** Vanilla HTML + CSS + JavaScript (FastAPI backend)
> **Gjeldende design:** [MASTER.md](MASTER.md)

---

## Oversikt — Alle Sider

```
                     ┌─────────────────────┐
                     │    LANDING (index)   │  ← Markedsføring, hero, priser
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │   LOGIN / SIGNUP    │  ← Auth
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │     DASHBOARD       │  ← Hovedhub (post-auth)
                     └──────────┬──────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼───────┐     ┌────────▼───────┐     ┌─────────▼──────┐
│     QUIZ      │     │  AI TEACHER    │     │   STUDY BOOK   │
│ Start → Spill │     │  (Michael)     │     │   Kapittel →   │
│ → Resultat    │     │  Chat + hist.  │     │   Seksjoner    │
└───────┬───────┘     └────────┬───────┘     └─────────┬──────┘
        │                      │                       │
┌───────▼───────┐     ┌────────▼───────┐     ┌─────────▼──────┐
│   HISTORY     │     │    STATS       │     │  TRAFFIC SIGNS │
│  Tidligere    │     │  Framgang,     │     │  Kategorisert  │
│  resultater   │     │  streaks       │     │  + søk         │
└───────┬───────┘     └────────┬───────┘     └─────────┬──────┘
        │                      │                       │
┌───────▼───────┐     ┌────────▼───────┐     ┌─────────▼──────┐
│  BOOKMARKS    │     │  TRAFFIC MATH  │     │   GLOSSARY    │
└───────┬───────┘     └────────────────┘     └───────────────┘
        │
┌───────▼───────┐
│   SETTINGS    │
│  Profil, språk│
│  Premium, hjelp│
└───────────────┘
```

**Alle sider har:**
- Flytende glassmorphism-navbar (toppen)
- Radial-gradient bakgrunn (dyp navy → medium navy)
- Neon-aksenter i cyan, pink, orange
- Glasskort med backdrop-blur

---

## 1. LANDING (index.html)

### Layout (top → bottom)

```
┌──────────────────────────────────────────────┐
│  NAVBAR  [Logo] Thai2Drive  [Språk] [Logg inn│
│                                [Start gratis] │
├──────────────────────────────────────────────┤
│                                              │
│  ┌───────── HERO ────────────────────────┐   │
│  │  "Bestått teoriprøven med             " │   │
│  │  "Thai2Drive — din personlige         " │   │
│  │  "kjørelærer på norsk, thai og        " │   │
│  │  "engelsk."                            │   │
│  │  [Cyan glow knapp] START GRATIS       │   │
│  │  <pulsende cyan ring / animasjon>     │   │
│  └────────────────────────────────────────┘   │
│                                              │
│  ┌──── FEATURES (3 kort, roterende neon) ──┐ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐       │ │
│  │  │ 🧠 AI  │ │ 📝     │ │ 📊     │       │ │
│  │  │ Lærer  │ │ Quizer │ │ Statistikk│    │ │
│  │  └────────┘ └────────┘ └────────┘       │ │
│  │  <roterende neon-rammer cyan→pink→orange>│ │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── AI LÆRER PREVIEW ───────────────────┐  │
│  │  [Pink neon-ramme]                      │  │
│  │  "Hei! Jeg er Michael, din             "│  │
│  │  "digitale kjørelærer. Klar for        "│  │
│  │  "dagens økt?"                          │  │
│  │  [Prøv Michael →]                       │  │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── TESTIMONIALS ───────────────────────┐  │
│  │  ⭐⭐⭐⭐⭐ "Bestått første gang!" - Siri │  │
│  │  ⭐⭐⭐⭐⭐ "Thai2Drive var uvurderlig"   │  │
│  │  <carousel med glasskort>              │  │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── PRISER ──────────────────────────────┐ │
│  │  ┌──────┐ ┌──────┐ ┌──────┐            │ │
│  │  │ GRATIS│ │PREMIUM│ │FAMILIE│          │ │
│  │  │ 5/dag │ │Ubegr. │ │2 brukere│        │ │
│  │  │       │ │★POP★ │ │       │          │ │
│  │  └──────┘ └──────┘ └──────┘            │ │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── FAQ ─────────────────────────────────┐ │
│  │  ▼ Hva koster det?                     │ │
│  │  ▼ Kan jeg bytte språk?                │ │
│  │  ▼ Hvordan fungerer AI-læreren?         │ │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── FINAL CTA ──────────────────────────┐  │
│  │  "Klar for å bestå teoriprøven?"       │  │
│  │  [STOR ORANGE KNAPP: START I DAG]      │  │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── FOOTER ────────────────────────────┐   │
│  │  Thai2Drive © 2026 | Personvern |     │   │
│  │  Vilkår | Kontakt                     │   │
│  └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 2. LOGIN / SIGNUP

```
┌──────────────────────────────────────────────┐
│  NAVBAR (kun logo + språk)                   │
├──────────────────────────────────────────────┤
│                                              │
│  ┌───── AUTH CARD [Cyan neon border] ───────┐│
│  │  🚗                                      ││
│  │  "Velkommen tilbake" / "Opprett konto"   ││
│  │                                          ││
│  │  ┌──────────────────────────────────┐    ││
│  │  │ [glass input] E-post            │    ││
│  │  └──────────────────────────────────┘    ││
│  │  ┌──────────────────────────────────┐    ││
│  │  │ [glass input] Passord            │    ││
│  │  └──────────────────────────────────┘    ││
│  │                                          ││
│  │  [CYAN KNAPP] Logg inn / Registrer       ││
│  │  ──── eller ────                        ││
│  │  Har du ikke konto? → Sign up            ││
│  │  Glemt passord? → Tilbakestill           ││
│  └────────────────────────────────────────────┘│
└──────────────────────────────────────────────┘
```

---

## 3. DASHBOARD (logget inn)

```
┌──────────────────────────────────────────────┐
│  NAVBAR [Logo] [Dashboard] [Quiz] [Bok]      │
│  [Michael] [─ brukernavn ─]  ⚙️              │
├──────────────────────────────────────────────┤
│                                              │
│  ┌─── WELCOME ───────────────────────────┐   │
│  │  "Hei, <navn>! 👋"       🔥 5 dager  │   │
│  │  "Fortsett der du slapp:"             │   │
│  │  [STOR CTA: FORTSETT QUIZ]             │   │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── STATS GRID (HUD-stil) ──────────────┐  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐           │  │
│  │  │  78  │ │  12  │ │  89% │           │  │
│  │  │Quizer│ │Dager │ │Score │           │  │
│  │  └──────┘ └──────┘ └──────┘           │  │
│  │  (monospace tall + cyan glow)          │  │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── WEAK AREAS ─────────────────────────┐  │
│  │  "Fokuser på:"                         │  │
│  │  Vikeplikt      ████████░░ 68%         │  │
│  │  Trafikkregler  ██████░░░░ 55%         │  │
│  │  Skilt          █████████░ 85%         │  │
│  │  (HUD progress bars, cyan→pink)        │  │
│  └──────────────────────────────────────────┘ │
│                                              │
│  ┌─── AI ANBEFALING ──────────────────────┐  │
│  │  [Pink border] "Michael anbefaler:"    │  │
│  │  "Øv på vikeplikt — din svakeste       │  │
│  │  kategori. Prøv 10 spørsmål."         │  │
│  │  [Start]                               │  │
│  └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 4. QUIZ

### Kategori → Spørsmål → Resultat

```
┌─── KATEGORI ──────────────────────────────┐
│  "Velg kategori"                          │
│  ┌──────┐ ┌──────┐ ┌──────┐              │
│  │ 🚦   │ │ 🚗   │ │ ⚠️   │              │
│  │Vike- │ │Trafikk│ │Skilt │              │
│  │plikt │ │regler│ │      │              │
│  └──────┘ └──────┘ └──────┘              │
└────────────────────────────────────────────┘

┌─── SPØRSMÅL (etter kategori-valg) ───────┐
│  Spørsmål 5 av 20   ████████░░            │
│                                          │
│  "Hva er riktig prosedyre når du skal   "│
│  "svinge til venstre..."                 │
│                                          │
│  [A] Sakte farten...     ← glasskort     │
│  [B] Slipp opp gassen... ← glasskort     │
│  [C] Gi tegn i god tid... ← glasskort    │
│  [D] Stopp alltid...      ← glasskort    │
│                                          │
│  etter svar: (grønn/rød glow)            │
│  ✅ Korrekt! / ❌ Feil                    │
│  "Du skal alltid gi tegn i god tid..."   │
│  [Neste →]                               │
└────────────────────────────────────────────┘

┌─── RESULTAT ──────────────────────────────┐
│          ╭────────╮                       │
│          │  15    │  ← cyan glow score    │
│          │  /20   │                        │
│          ╰────────╯                        │
│          75% korrekt                      │
│                                          │
│  ✅ Korrekt: 15    ⏱️ 4:32               │
│  ❌ Feil: 5                               │
│                                          │
│  [Prøv igjen] [Hjem] [Michael forklarer]  │
└────────────────────────────────────────────┘
```

---

## 5. AI TEACHER (Michael)

```
┌──────────────────────────────────────────────┐
│  NAVBAR  ← Michael  [Historie]              │
├──────────────────────────────────────────────┤
│                                              │
│  ┌─── CHAT [PINK NEON FRAME] ────────────┐   │
│  │  ┌─────────────────────────────┐       │   │
│  │  │👨‍🏫 Michael: "Hei! Jeg er    │       │   │
│  │  │din digitale kjørelærer."   │       │   │
│  │  │[Pink border left]          │       │   │
│  │  └─────────────────────────────┘       │   │
│  │                                         │   │
│  │  ┌─────────────────────────────┐       │   │
│  │  │Du: "Hva er vikeplikt?"     │       │   │
│  │  │[Cyan border right]         │       │   │
│  │  └─────────────────────────────┘       │   │
│  │                                         │   │
│  │  ┌─────────────────────────────┐       │   │
│  │  │👨‍🏫 skriver... ◌◌◌ (pulsing)│       │   │
│  │  └─────────────────────────────┘       │   │
│  │                                         │   │
│  │  ┌─── INPUT ───────────────────────┐   │   │
│  │  │  ┌────────────────┐ [📤]       │   │   │
│  │  │  │ Skriv her...   │            │   │   │
│  │  │  └────────────────┘            │   │   │
│  │  │  Forslag: [🚦 Vikeplikt?]     │   │   │
│  │  │            [🅿️ Parkering?]    │   │   │
│  │  └────────────────────────────────┘   │   │
│  └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

---

## 6. STUDY BOOK

```
┌─── KAPITLER ──────────────────────────────┐
│  ┌──────────────────────────────────────┐ │
│  │ 📖 Kap 1: Grunnleggende   ═══ 100%  │ │
│  ├──────────────────────────────────────┤ │
│  │ 📖 Kap 2: Vikeplikt       ═══░ 65%  │ │
│  ├──────────────────────────────────────┤ │
│  │ 📖 Kap 3: Skilt           ═══░ 30%  │ │
│  └──────────────────────────────────────┘ │
│  (glasskort, HUD-progress)               │
└────────────────────────────────────────────┘

┌─── SEKSJONER (når kapittel velges) ──────┐
│  2.1 — Hva er vikeplikt?                 │
│  2.2 — Høyreregelen                      │
│  2.3 — Forkjørsvei                       │
│  (glasskort med lesbart innhold)         │
└────────────────────────────────────────────┘
```

---

## 7. TRAFFIC SIGNS

```
┌─── FILTER ────────────────────────────────┐
│  [Alle] [Fare] [Påbud] [Forbud] [Info]   │
│  (cyan underline på aktiv)               │
├────────────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐                │
│  │ ⚠️  │ │ 🛑  │ │ 🔵  │                │
│  │Fare │ │Stopp│ │Påbud│                │
│  └─────┘ └─────┘ └─────┘                │
│  (glasskort, hover: cyan border)         │
└────────────────────────────────────────────┘
```

---

## 8. FARGETABELL — ALLE ELEMENTER

| Komponent | Hva | Farge | CSS-variabel |
|-----------|-----|-------|-------------|
| **Bakgrunn** | Ytterste lag | `#060B18` | `--bg-deep` |
| | Seksjoner | `#0A0E27` | `--bg-navy` |
| | Glasskort | `rgba(15,21,53,0.6)` | `--glass-bg` |
| | Input-felt | `#1A2048` | `--bg-light` |
| **Tekst** | Overskrifter | `#E2E8F0` | `--text-primary` |
| | Brødtekst | `#94A3B8` | `--text-secondary` |
| | Muted | `#64748B` | `--text-muted` |
| **Neon** | Cyan (hoved) | `#00F5FF` | `--neon-cyan` |
| | Pink (AI/premium) | `#FF00E5` | `--neon-pink` |
| | Orange (CTA/streak) | `#FF9933` | `--neon-orange` |
| **Glow** | Cyan glow små | `0 0 10px rgba(0,245,255,0.4)` | `--glow-cyan-sm` |
| | Cyan glow medium | `0 0 20px rgba(0,245,255,0.5)` | `--glow-cyan-md` |
| | Pink glow | `0 0 20px rgba(255,0,229,0.5)` | `--glow-pink-md` |
| | Orange glow | `0 0 20px rgba(255,153,51,0.5)` | `--glow-orange-md` |
| **Semantisk** | Suksess | `#22C55E` | `--color-success` |
| | Feil | `#EF4444` | `--color-error` |
| | Advarsel | `#F59E0B` | `--color-warning` |
| **Glass** | Border | `rgba(0,245,255,0.15)` | `--glass-border` |
| | Blur | `16px` | `--glass-blur` |
| | Shadow | `0 8px 32px rgba(0,0,0,0.4)` | `--glass-shadow` |
| **Navbar** | Aktiv lenke | Cyan underline + glow | |
| | Hover lenke | `--neon-cyan` tekstfarge | |
| **Knapp CTA** | Primary | Cyan grad: `#00F5FF→#0088CC` | |
| | Premium | Orange grad: `#FF9933→#FF6600` | |
| **Progress** | HUD bar fill | Cyan→pink gradient | |
| **Score ring** | ≥80% | Cyan `#00F5FF` | |
| | 50-79% | Orange `#FF9933` | |
| | <50% | Rød `#EF4444` | |
| **Option** | Normal | Glasskort | |
| | Hover | Cyan border + glow | |
| | Korrekt | Grønn border + glow | |
| | Feil | Rød border + glow | |

---

## 9. TYPOGRAFISK SKALA

```
Space Grotesk (headings)
├── text-5xl: 48px — Hero
├── text-4xl: 36px — Side-titler
├── text-3xl: 30px — Seksjons-headings
├── text-2xl: 24px — Kort-titler
└── text-xl:  20px — Underoverskrifter

DM Sans (body)
├── text-lg:   18px — Lead/ingress
├── text-base: 16px — Brødtekst
├── text-sm:   14px — Labels
└── text-xs:   12px — Metadata

JetBrains Mono (HUD)
├── text-4xl: 36px — Score-tall
├── text-lg:  18px — Statistikk
└── text-sm:  14px — Data labels
```

---

## 10. MOBIL TILPASNING (ANDROID/EXPO)

### Hva er likt

- **Samme fargepalett** — alle hex-koder er identiske
- **Samme typografi** — Space Grotesk / DM Sans / JetBrains Mono via Google Fonts
- **Samme glassestetikk** — semi-transparent bg + border i stedet for backdrop-filter
- **Samme neon glow** — `textShadowRadius`/`shadowRadius` i RN
- **Samme komponenter** — bare transpilert til React Native

### Hva er forskjellig

| Web | Android (Expo) |
|-----|----------------|
| CSS `backdrop-filter: blur()` | `backgroundColor: rgba(15,21,53,0.7)` + `elevation: 8` |
| CSS `conic-gradient` for neon-ramme | `expo-linear-gradient` + `Animated` rotasjon |
| CSS `perspective` + `rotateX/Y` 3D | RN `Animated.Value` + `transform` |
| Navbar top (fast) | SafeAreaView + Bottom Tab Navigator |
| CSS `radial-gradient` bakgrunn | `LinearGradient` fra expo-linear-gradient |
| Hover states | Trykk-states (`Pressable`) |
| HUD progress bars | RN `View` + `Animated` bredde |
| Flytende navbar | `position: 'absolute'` i RN |

### Fargekonstanter for Android

```javascript
export const COLORS = {
  bgDeep:     '#060B18',
  bgNavy:     '#0A0E27',
  bgMedium:   '#0F1535',
  bgLight:    '#1A2048',
  textPrimary:'#E2E8F0',
  textSecondary:'#94A3B8',
  textMuted:  '#64748B',
  neonCyan:   '#00F5FF',
  neonPink:   '#FF00E5',
  neonOrange: '#FF9933',
  success:    '#22C55E',
  error:      '#EF4444',
  warning:    '#F59E0B',
};

export const FONTS = {
  heading: 'SpaceGrotesk',
  body:    'DMSans',
  mono:    'JetBrainsMono',
};
```

---

## 11. KOMPONENT-HIERARKI

```
App
├── BgRadialGradient (fixed bakgrunn)
│
├── Navbar (glass, fixed top)
│   ├── Logo (cyan neon)
│   ├── NavLinks → NavLink (hover: cyan)
│   └── UserMenu
│
├── Page Content
│   ├── HeroSection (kun landing)
│   ├── GlassCard (gjennomgående)
│   ├── StatCard (HUD: monospace + glow)
│   ├── HudProgressBar (cyan→pink fill)
│   ├── OptionCard (quiz: label + text)
│   ├── ChatBubble (teacher: avatar + msg)
│   ├── NeonFrame (wrapper for ramme)
│   └── ScoreRing (SVG sirkel)
│
├── BottomNav (mobil: 5 tabs, glass)
└── Modal (glass, backdrop)
```

---

## 12. BYGGE-REKKEFØLGE (FORSLAG)

| # | Hva | Output |
|---|-----|--------|
| 1 | CSS-variabler + reset + base styles | `static/css/base.css` |
| 2 | Navbar (glass, flytende) | `static/css/navbar.css` |
| 3 | Landing page (hero, features, testimonials, priser, FAQ) | `templates/index.html` |
| 4 | Auth (login/signup) | `templates/login.html` |
| 5 | Dashboard (stats, HUD, weak areas) | `templates/dashboard.html` |
| 6 | Quiz (kategori, spørsmål, feedback, resultat) | `templates/quiz.html` |
| 7 | AI Teacher (chat, bobler, typing) | `templates/teacher.html` |
| 8 | Study Book (kapittel, seksjoner) | `templates/book.html` |
| 9 | Traffic Signs (filter, grid, detail) | `templates/signs.html` |
| 10 | Stats + History | `templates/stats.html` |
| 11 | Settings | `templates/settings.html` |
| 12 | Mobil responsive (bottom nav, touch) | CSS media queries |
| 13 | Animasjoner (neon, 3D, border rotation, prefers-reduced-motion) | `static/css/effects.css` |
| 14 | Accessibility (focus, aria, keyboard) | Gjennomgående |
| 15 | JS app (router, store, API, komponenter) | `static/js/` |

---

## 13. KANALER FOR Å SE DET NÅVÆRENDE NETTSTEDET

Siden du vil se med egne øyne — her er det nåværende nettstedet:

| Side | Adresse |
|------|---------|
| **Thai2Drive produksjon** | [thai2drive.no](https://thai2drive.no) |
| **Direkte Railway** | [thai2drive-production.up.railway.app](https://thai2drive-production.up.railway.app) |
| **Web-appen** (innebygd telefonramme) | [thai2drive.no/dashboard](https://thai2drive.no/dashboard) |
| **Landing page** (markedsføring) | [thai2drive.no](https://thai2drive.no) |
| **Admin** | [thai2drive.no/admin](https://thai2drive.no/admin) |

---

✅ **Design-blueprint er klar for din gjennomgang!**

Du kan **se dagens side** på [thai2drive.no](https://thai2drive.no) for å sammenligne med blueprinten over.

Når du har sett gjennom og evt. justert blueprinten, sier du bare ordet, så begynner jeg å bygge! 🚀
