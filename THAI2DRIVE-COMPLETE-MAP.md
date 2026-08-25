# Thai2Drive — COMPLETE SYSTEM MAP

> **Version:** 2.0 (2026-06-25-78ce70dc)
> **Last updated:** 2026-06-25
> **Purpose:** Full architecture reference for debugging, planning, and development.

---

## 1. INFRASTRUCTURE

| Layer | Service | Details |
|-------|---------|---------|
| **Domain** | Domeneshop | thai2drive.no — CNAME www → 8om4giil.up.railway.app |
| **Hosting** | Railway | Project: captivating-embrace — Backend: thai2drive-production.up.railway.app |
| **GitHub** | MagicMike-80/thai2drive | Main branch — Railway auto-deploys from pushes |
| **Database** | MongoDB Atlas | Cluster: cluster0.mecy7qw.mongodb.net / DB: thai2drive / User: norge-quiz-app |
| **Analytics** | Segment | Source: Thai2Drive Backend — Write Key: sFZG0w4UaoJkSfzruxV5CLsUjNp6Fylk |
| **Payments (web)** | Stripe | Live mode — Checkout Sessions API — Webhook: /api/stripe/webhook |
| **Payments (mobile)** | RevenueCat | Webhook: /api/rc/webhook — Synced with mobile IAP |
| **Email** | SendGrid (primary) → Resend → SMTP (fallback) | Password resets |
| **TTS Thai** | Google Cloud TTS | Male "Chirp3 HD" voice |
| **TTS NO/EN** | ElevenLabs | Cloned voice "Ai Mike" — falls back to Google TTS |
| **AI Vision** | Anthropic Claude (via litellm) | Question image audit in admin panel |
| **Images** | Unsplash API | Admin question image suggestions |
| **AAB Build** | EAS (Expo) | Project: @michael80/thai2drive — Build ID: 21f9e2ff-e000-41a4-8ec7-d6e9a3e35693 |
| **Google Play** | com.michael.thai2drive | Closed testing — Version 1.1.0 — Code 2 |

### 1.1 DNS Records (Domeneshop)

| Host | Type | Value | Status |
|------|------|-------|--------|
| www.thai2drive.no | CNAME | 8om4giil.up.railway.app | ✅ |
| thai2drive.no | WWW-videresending | → www.thai2drive.no | ✅ |
| _railway-verify.www | TXT | railway-verify=9cc6564b74199... | ✅ |

### 1.2 Railway Config

File: `railway.json` (repo root)
```json
{
  "build": { "builder": "DOCKERFILE", "dockerfilePath": "backend/Dockerfile" },
  "deploy": {
    "healthcheckPath": "/api/_whoami",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

### 1.3 Docker

- **File:** `backend/Dockerfile` — python:3.12-slim → install gcc → pip install → COPY . → CMD uvicorn
- **File:** `backend/.dockerignore` — excludes *.aab, *.pdf, *.pptx, __pycache__, .git, .env, node_modules

---

## 2. REPO FILE STRUCTURE

```
C:\Users\Stein Hoang\Desktop\Thai2Drive App\thai2drive\
│
├── railway.json              ← Docker build config for Railway
├── netlify.toml              ← Legacy legal pages
├── AGENTS.md                 ← Agent instructions
├── CLAUDE.md                 ← Claude Code instructions (NORWEGIAN ONLY)
├── README.md
│
├── backend/                  ★ MAIN APPLICATION (Python/FastAPI)
│   ├── server.py             ← 5076 lines — All API routes, auth, startup
│   ├── landing.py            ← 1606 lines — Marketing landing page HTML/CSS/JS
│   ├── webapp.py             ← ~9218 lines — Web app SPA (the 459KB HTML file)
│   ├── website.py            ← Public pages: guide, privacy, terms, support, bok
│   ├── usage.py              ← 401 lines — Access tier engine (guest/registered/premium)
│   ├── quiz_web.py           ← Quiz web page
│   ├── ai_routes.py          ← AI learning endpoints
│   ├── ai_learning.py        ← AI learning engine
│   ├── ai_explanations.py    ← AI explanation generation
│   ├── support_chat.py       ← Claude-powered support chat
│   ├── teacher_chat.py       ← "Michael Trafikklaerer" AI teacher
│   ├── traffic_math_routes.py← Stopping distance, following distance calculators
│   ├── signs_data.py         ← Static traffic sign data
│   ├── check_db.py           ← DB diagnostics
│   ├── create_indexes.py     ← MongoDB index creation
│   │
│   ├── Dockerfile
│   ├── Procfile
│   ├── requirements.txt      ← 119 packages incl. analytics-python==2.1.8
│   ├── .env                  ← Environment variables (NOT committed)
│   ├── .dockerignore
│   │
│   ├── admin.html            ← Admin panel HTML
│   ├── voice_tester.html     ← ElevenLabs voice tester
│   │
│   ├── webapp/               ← 14 SPA HTML pages (Expo build output)
│   │   ├── index.html, login.html, signup.html, forgot-password.html
│   │   ├── quiz.html, results.html, categories.html
│   │   ├── history.html, bookmarks.html
│   │   ├── paywall.html, settings.html, admin.html
│   │   ├── +not-found.html, _sitemap.html
│   │
│   ├── public_assets/        ← Static files served at /api/assets/
│   │   ├── developer-icon-512.png, developer-header-4096x2304.jpg
│   │   ├── qr-download.png, feature-graphic-1024x500.jpg
│   │   ├── rundkjoring1.jpg, rundkjoring2.jpg
│   │   ├── screenshots/      ← 8 phone screenshots (home, categories, quiz, etc.)
│   │   ├── audio/            ← Podcasts and TTS cache
│   │   └── uifix/            ← UI fix images
│   │
│   ├── sign_images/          ← Traffic sign SVGs (served at /api/sign-images/)
│   │
│   ├── content_packs/        ← Import scripts + studiebok_i18n HTML files
│   ├── scripts/              ← Utility scripts (insert questions, audit, etc.)
│   └── seed_*.py             ← Seed scripts
│
├── frontend/                 ★ MOBILE APP (Expo/React Native)
│   ├── package.json          ← Expo SDK 54, React 19.1, RN 0.81.5
│   ├── app.json              ← version 1.1.0, versionCode 2
│   ├── app/                  ← 25 screens (expo-router)
│   └── src/                  ← Components, hooks, services, store, theme
│
├── content/  docs/  website/  marketing-agent/  website-agent/  tests/  scratch/
│
├── 🔴 LARGE FILES (Docker build context bloat)
│   ├── 4tTrafikkalt.pptx                     (80 MB)
│   ├── application-*.aab                     (62 MB)
│   ├── Microsoft PowerPoint - 4tTrafikkalt.pdf (40 MB)
│   └── PDF.4t.pdf                            (40 MB)
│
└── legal-pages-for-netlify/   ← Legacy Netlify deployment
```

---

## 3. ALL API ENDPOINTS

### 3.1 Health & Root

| Method | Path | Source | Purpose |
|--------|------|--------|---------|
| GET | `/` | website.py | Landing page |
| GET | `/api/` | server.py:711 | Welcome message |
| GET | `/api/health` | server.py:5040 | Liveness + DB check |
| GET | `/_whoami` | website.py | Debug endpoint |

### 3.2 Web Pages Served

| Method | Path | Source | Purpose |
|--------|------|--------|---------|
| GET | `/api/web` | webapp.py | **★ THE WEB APP** — 459KB SPA with all 14 screens |
| GET | `/api/quiz` | quiz_web.py | Quiz page |
| GET | `/api/admin/{_}` | server.py | Admin panel (5 aliases) |
| GET | `/website` | website.py | Landing page alias |
| GET | `/guide` | website.py | Guide page |
| GET | `/privacy` | website.py | Privacy policy |
| GET | `/terms` | website.py | Terms of service |
| GET | `/support` | website.py | Support page |
| GET | `/bok` | website.py | Member-only book reader |
| GET | `/sitemap.xml` | website.py | XML sitemap |
| GET | `/robots.txt` | website.py | Robots.txt |

### 3.3 Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/signup` | Register (name, email, password) → JWT + user |
| POST | `/api/auth/login` | Login (email, password) → JWT + user |
| GET | `/api/auth/me` | Current user from JWT |
| POST | `/api/auth/forgot-password` | Send reset email |
| POST | `/api/auth/reset-password` | Reset with code |
| POST | `/api/auth/link-device` | Link device for cross-platform access |

### 3.4 Questions & Quiz

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/questions` | List with filters (category, difficulty, limit, skip, image_only) |
| GET | `/api/questions/random` | Random questions — exam/hard/mistake modes |
| GET | `/api/questions/{id}` | Single question |
| POST | `/api/questions` | Create question (auth) |
| GET | `/api/categories` | Question categories list |

### 3.5 Access Control

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/access/status` | Current tier & limits |
| POST | `/api/access/consume` | Decrement remaining questions |
| GET | `/api/usage/status` | Full usage payload (tier, used, remaining, streak, gate) |

**Access tiers:** guest=5 lifetime, registered=10/day, premium=unlimited

### 3.6 Stats, Progress & History

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stats/me` | Aggregated stats (total, correct, accuracy, streak) |
| GET | `/api/progress/{device_id}` | User progress |
| PUT | `/api/progress/{device_id}` | Update progress |
| POST | `/api/quiz-attempts` | Save attempt result |
| GET | `/api/quiz-attempts/{device_id}` | Attempts by device |
| GET | `/api/history` | Authenticated user history |

### 3.7 Bookmarks

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/bookmarks` | Add bookmark |
| DELETE | `/api/bookmarks/{device_id}/{question_id}` | Remove bookmark |
| GET | `/api/bookmarks/{device_id}` | List bookmark IDs |
| GET | `/api/bookmarked-questions/{device_id}` | Full bookmark question details |

### 3.8 Traffic Signs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/signs` | List all signs (from signs_data.py static data) |
| GET | `/api/traffic-signs` | Signs grouped by group number (MongoDB) |
| GET | `/api/traffic-signs/{group}` | Signs in group 1-9 |
| POST | `/api/traffic-signs` | Create sign (admin) |
| PUT/PATCH/DELETE | `/api/traffic-signs/{sign_id}` | CRUD operations |

### 3.9 Chapters & Studiebok

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/chapters` | List curriculum chapters |
| GET | `/api/chapters/{num}` | Chapter by number |
| GET | `/api/chapters/{num}/{sec}` | Specific section |
| GET | `/api/studiebok` | List studiebok chapters |
| POST/PUT/DELETE | `/api/studiebok/{order}` | CRUD (auth) |

### 3.10 Videos, Podcasts & Glossary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/videos/for-topic` | Videos by topic tags |
| GET | `/api/videos/for-sign/{sign_id}` | Videos for a traffic sign |
| GET | `/api/podcasts/for-topic` | Podcasts by topic tags |
| POST/GET | `/api/admin/videos` | Video CRUD (admin) |
| POST/GET | `/api/admin/podcasts` | Podcast CRUD (admin) |
| GET | `/api/glossary` | List terms (lang/search filter) |
| GET | `/api/glossary/{term_id}` | Single term |

### 3.11 Payments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/pricing` | Stripe live prices |
| POST | `/api/create-checkout-session` | Create Stripe Checkout |
| GET | `/api/checkout/status` | Poll checkout status |
| POST | `/api/stripe/webhook` | Stripe webhook handler |
| POST | `/api/rc/webhook` | RevenueCat webhook handler |

### 3.12 AI & Teacher

| Method | Path | Source | Description |
|--------|------|--------|-------------|
| POST | `/api/ai/attempt` | ai_routes.py | Record AI-evaluated attempt |
| GET | `/api/ai/dashboard/{device_id}` | ai_routes.py | AI learning dashboard |
| GET | `/api/ai/explanation/{question_id}` | ai_routes.py | AI explanation |
| GET | `/api/ai/smart-practice/{device_id}` | ai_routes.py | Smart practice recos |
| GET | `/api/ai/coaching/{device_id}` | ai_routes.py | AI coaching insights |
| POST | `/api/support/chat` | support_chat.py | Support chat (Claude) |
| GET | `/api/support/status` | support_chat.py | Support status |
| POST | `/api/teacher/chat` | teacher_chat.py | Teacher chat message |
| POST | `/api/teacher/feedback` | teacher_chat.py | Feedback |

### 3.13 Tools & Assets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tts` | Text-to-Speech (Google TTS / ElevenLabs) |
| GET | `/api/assets/{filename}` | Static assets (icons, screenshots, audio) |
| GET | `/api/sign-images/{filename}` | Traffic sign images |
| GET | `/.well-known/assetlinks.json` | Android App Links |
| GET | `/api/math/stopping-distance` | Stopping distance calculator |
| GET | `/api/math/following-distance` | Safe following distance |
| GET | `/api/math/conditions` | Weather/road condition multipliers |

### 3.14 Admin CRUD

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/admin/questions` | List/create questions |
| PATCH/DELETE | `/api/admin/questions/{id}` | Update/soft-delete |
| DELETE | `/api/admin/questions/{id}/permanent` | Hard-delete |
| POST/DEL | `/api/admin/questions/{id}/image` | Upload/remove image |
| POST | `/api/admin/questions/{id}/unsplash-suggestions` | Unsplash search |
| POST | `/api/admin/questions/{id}/fetch-unsplash` | Store Unsplash image |
| POST | `/api/admin/questions/{id}/audit` | AI Vision audit |
| GET/PATCH | `/api/admin/book/sections` | Book sections CRUD |
| POST | `/api/admin/book/sections/{id}/image` | Upload section image |
| GET | `/api/admin-setup-t2d` | Create initial admin user |
| POST | `/api/admin/check` | Check admin status |
| POST | `/api/admin/add` | Add admin privileges |
| POST | `/api/seed` | Seed 45 questions (6 categories) |

---

## 4. MONGODB COLLECTIONS

### A. Core Data
| Collection | Key Fields | Purpose |
|------------|-----------|---------|
| `questions` | id, category, difficulty, question{no/th/en}, options[{no/th/en}], correct_answer, image_url, explanation{no/th/en}, tags, chapter, section, deleted | 700+ questions, v1 (flat) and v2 (nested) |
| `user_progress` | device_id, user_id, category, total_attempts, correct_attempts, accuracy | Per-category stats *(map note: formerly called `progress` in v1 — actual name is `user_progress`)* |
| `quiz_attempts` | device_id, user_id, question_id, category, difficulty, selected_answer, correct, quiz_mode | All quiz results |

### B. Users & Auth
| Collection | Key Fields | Purpose |
|------------|-----------|---------|
| `users` | email, password_hash, is_admin, is_premium, premium_expires_at, stripe_customer_id, rc_original_app_user_id, current_streak, best_streak, last_activity_date | User accounts & premium |
| `guest_usage` | device_id, questions_served | 5 lifetime limit |
| `daily_usage` | user_id, date_oslo, questions_served | 10/day per registered |
| `admin_users` | email | Admin email whitelist |
| `access_usage` | scope/key pattern | Access tier usage counters |
| `access_events` | — | Idempotent access consumption events |

### C. Access Control & Payments
| Collection | Key Fields | Purpose |
|------------|-----------|---------|
| `checkout_sessions` | stripe_session_id, user_id, status | Stripe checkout tracking *(map note: formerly called `stripe_sessions`)* |
| `subscriptions` | user_id, stripe_subscription_id, status, period_end | Premium subscription records |
| `stripe_events` | stripe_event_id | Stripe webhook deduplication |
| `rc_events` | rc_event_id | RevenueCat webhook deduplication |

### D. Content & Learning
| Collection | Key Fields | Purpose |
|------------|-----------|---------|
| `bookmarks` | device_id, user_id, question_id | Saved questions |
| `chapters` | chapter_num, section_num, section_title{no/th/en}, content{no/th/en}, image_url | 61 curriculum sections |
| `studiebok_chapters` | order, icon, title_no, content_no, image_url, video_url | 15 study book chapters |
| `learning_videos` | title_no/th/en, youtube_url, topic_tags, sign_ids, sign_groups, see_context, understand_context, choose_context, active | Contextual videos |
| `learning_podcasts` | title_no/th/en, file_path, duration_seconds, topic_tags | Audio podcasts |
| `learning_glossary` | term_no/th/en, definition_no/th/en, example_no/th/en, topic_tags | Bilingual traffic terms |
| `traffic_signs` | group(1-9), name{no/th/en}, image_url, order | Sign database |

### E. AI & Chat
| Collection | Key Fields | Purpose |
|------------|-----------|---------|
| `ai_attempts` | — | AI learning attempt records |
| `ai_srs_cards` | — | Spaced-repetition cards for AI |
| `ai_explanations` | — | Cached AI explanations |
| `support_chats` | — | Support chat history |
| `support_escalations` | — | Support escalation records |
| `teacher_chats` | — | Teacher AI chat sessions |
| `teacher_chat_logs` | — | Teacher chat log entries |
| `teacher_feedback` | — | Teacher feedback records |

### F. DEPRECATED / NOT IN USE
| Collection | Note |
|------------|------|
| ~~`token_blacklist`~~ | Documented in earlier version but does not exist in code |
| ~~`reset_tokens`~~ | Password reset uses email code flow — no dedicated collection |
| ~~`support_conversations`~~ | Renamed to `support_chats` |

---

## 5. THE WEB APP (Single-Page Application)

**Served at:** `GET /api/web` — 459KB single HTML file generated by `backend/webapp.py` (9161 lines)
**Architecture:** Vanilla JavaScript (no framework) — all CSS, HTML, and JS in ONE file.

### 5.1 App Shell

```
#app (flex column, 100dvh)
├── .flag-bg                    ← Thai flag background (5-stripe)
├── #topBar (48px, sticky)     ← Logo, streak counter, 3 flag buttons (TH/NO/EN)
├── #content (flex:1, overflow:hidden)
│   ├── screenAuth             ← Login / Register / Forgot / Reset password
│   ├── screenHome             ← CTA, HSM menu, stats, readiness %, premium CTA
│   ├── screenCats             ← 3D Carousel (20+ categories with icons)
│   ├── screenQuiz             ← Full quiz engine (single-col mobile / two-col desktop)
│   ├── screenLibrary          ← Video & Podcast library with tabs
│   ├── screenSigns            ← Traffic sign gallery (9 groups)
│   ├── screenBookmarks        ← Bookmarked questions (horizontal cards)
│   ├── screenHistory          ← Attempt history list
│   ├── screenStudybook        ← Chapter reader with search
│   ├── screenForbikjoring     ← Overtaking calculator
│   ├── screenEnd              ← Quiz end screen (score, debrief, retry)
│   ├── screenPaywall          ← Pricing cards (99 / 249 / 699 kr)
│   ├── screenTeacher          ← AI Teacher chat (Michael)
│   ├── screenSettings         ← Language, sound, TTS, theme, logout
│   ├── signPanelBackdrop+Panel← Sign detail bottom sheet / right panel
│   ├── histPanelBackdrop+Panel← History detail bottom sheet / right panel
│   ├── studiebokEditModal     ← Admin edit modal (map note: id="studiebokEditModal", not "studiebokModal")
│   └── #toast                 ← Notification toast
└── #bottomNav (76px, glass)  ← 8 tabs: Hjem·Kategorier·Historikk·Michael·Skilt·Studiebok·Bokmerker·Innstillinger
```

### 5.2 Desktop Phone Frame

On **viewport >500px**:
- `#app` constrained to **390px** wide, centered
- Conic-gradient neon border animation (`--neon-angle` 0→360deg, 5s loop)
- `@property --neon-angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }`
- `border-left/right: 2px solid transparent` with conic-gradient as border-box background
- German flag radial-gradient background on `body`

On **700px+** (quiz mode): app expands to 1080px with left/right columns for question + side panels.

### 5.3 CSS System (3116 lines)

- CSS variables in `:root` (dark) and `[data-theme="light"]`
- Key animations: `neonFlow`, `aiBlockIn`, `tmBounce`, `tts-pulse`, `topflagpulse`
- 25 sections covering: app shell, phone frame, top bar, bottom nav, screens, 3D carousel, quiz, AI panel, review, library, signs, bookmarks, history, end screen, study book, forbikjoring, paywall, teacher chat, settings, toast

### 5.4 JavaScript Module Overview (251 KB, lines 3901-8967)

| Module | Lines | Key Functions |
|--------|-------|---------------|
| State vars | 3904-3940 | token, user, deviceId, questions[], appLang, activeTab, soundsEnabled, ttsEnabled |
| NAV_SVG | 3940-3951 | 8 SVG icons for bottom navigation |
| History helpers | 3951-4002 | `_mergeAttempts`, `_readLocalAttempts` |
| Translation UI | 4002-4296 | 400+ keys in {th, no, en} |
| i18n functions | 4298-4326 | `t(key)`, `tf(key, vars)`, `modeLabel()`, `applyUILang()` |
| CAT data | 4456-4540 | `CAT_ICONS`, `CAT_SVG`, `CAT_NAMES` (20+ categories) |
| **init()** | 4549-4577 | Bootstrap: theme → lang → pricing → token → API → enterApp |
| Screen/Tab mgmt | 4577-4637 | `showScreen()`, `showTab()`, `enterApp()` |
| Library | 4647-4722 | `loadLibrary()`, `renderLibrary()` |
| Study Book | 4727-4963 | `sbGoTo()`, `sbRender()`, `sbSearch()` |
| API helper | 4968-4994 | `api(method, url, body)` — fetch + auth header |
| Premium | 4994-5047 | `loadPremiumPricing()`, `buyPremium()`, `handleCheckoutReturn()` |
| Toast | 5047-5059 | `toast(msg, dur)` |
| **Auth** | 5059-5197 | `switchTab()`, `showForgot()`, `togglePw()`, `doLogin()`, `doRegister()`, `doForgot()`, `doResetPassword()`, `logout()` |
| **Home** | 5202-5257 | `loadHome()` — streak, stats, readiness bar |
| **3D Carousel** | 5260-5480 | `updateCarousel()`, `carouselClick()`, `bindCarouselDrag()` |
| **Quiz Engine** | 5482-7025 | `loadQuiz()`, `renderQuestion()`, `selectAns()`, `nextQ()`, AI learning system |
| AI Learning | 5508-5570 | Streak tracking, confidence level, danger labels, alerts, instructor tips, situation lens |
| Review Mode | 6625-6697 | `startReview()`, `renderReviewCard()` |
| Video Suggestion | 6700-6804 | `_injectVideo()`, `fetchVideoForTopic()` |
| Bookmarks | 7038-7105 | `toggleBookmark()`, `loadBookmarks()` |
| Signs Gallery | 7110-7234 | `loadSigns()` with group headers |
| History | 7239-7422 | `loadHistory()`, `openHistDetail()` |
| End Screen | 7442-7575 | `showEnd()`, `_buildDebrief()`, `retryQuiz()` |
| **TTS** | 7579-7658 | `speakQ()`, `setRate()`, `setVolume()`, `speakText()` — Google + ElevenLabs |
| Sound FX | 7689-7734 | `playSound()` — Web Audio API (correct/wrong/complete/click) |
| **Settings** | 7739-7846 | `setLang()`, `setTheme()`, `applyThemeFromStorage()` |
| **Teacher Chat** | 7851-8415 | `teacherSend()`, `_buildAssistantContent()`, `askMichaelAboutThis()` |
| **Forbikjoring** | 8425-8583 | `fkCalc()`, `fkRender()`, `fkSelect()` |
| **Sign Detail Panel** | 8676-8896 | `openSignDetail()`, `_renderSignPanel()`, `closeSignDetail()` |
| Keyboard | 8634-8676 | A/B/C/D, Enter, ArrowRight shortcuts |
| Misc | 8896-8967 | `escH()`, CSS escape, GA snippet |

### 5.5 Auth Flow

```
init()
  → check localStorage "t2d_token"
  → if found: GET /api/auth/me → enterApp() → showTab('home')
  → if not: showScreen('screenAuth') → switchTab('login')

doLogin(): POST /api/auth/login → {token, user}
  → localStorage.set('t2d_token', token)
  → enterApp() → showTab('home')

doRegister(): POST /api/auth/signup → same flow as login

logout(): remove token → showScreen('screenAuth') → hide bottomNav
```

### 5.6 Quiz Engine Flow

```
loadQuiz(mode, category)
  → GET /api/questions/random?mode=...&category=...&limit=30
  → shuffleQuestions()
  → renderQuestion(qIndex)
    → show options A/B/C/D
    → if image: show in left column (desktop) or above (mobile)
    → enable selectAns()
    
selectAns(btn)
  → highlight correct/wrong
  → if wrong: show correct answer + explanation
  → if AI: show AI explanation panel (confidence, tips, situation lens)
  → increment score
  → enable nextQ()
  → show video suggestion if available

nextQ()
  → if more questions: renderQuestion(++qIndex)
  → if done: POST /api/quiz-attempts → showEnd()
```

---

## 6. THE LANDING PAGE

**Served at:** `https://www.thai2drive.no/` — **Source:** `backend/landing.py` (1606 lines)

### 6.1 Section Inventory (15 sections)

| # | Section | Key Details |
|---|---------|-------------|
| 1 | **Sticky Nav** | Logo, nav links (Features/Pricing/Guide/Web App/Facebook), 3 flags (TH/NO/EN) |
| 2 | **Hero** | App icon, triline headline, CTA buttons, QR code, feature badges |
| 3 | **Stats Bar** | 700+ questions, 3 languages, 45 exam questions, 90% pass rate |
| 4 | **Try-in-Browser Quiz** | 10-question free quiz, progress bar, TTS 0.5x-2x, scoring, explanations |
| 5 | **Video Grid** | 3 YouTube video cards (incl. "The Story Behind Thai2Drive") |
| 6 | **Why Thai2Drive** | 3 reasons: Thai-focused, explanations, exam simulation |
| 7 | **Features Detail** | 5 cards: 500+ Qs, explanations, 3 languages, exam mode, study anywhere |
| 8 | **App Screenshots** | Horizontal scrollable 5 phone screenshots |
| 9 | **Norwegian Roads** | 2 real road photos from Norway |
| 10 | **Trust/Proof** | 3 trust cards: used by Thais, updated rules, designed to pass |
| 11 | **Bottom CTA** | Try Free + Download with QR code |
| 12 | **Footer** | Copyright 2025, flags, links (Home/Privacy/Terms/Support) |
| 13 | **Support Chat** | Floating Claude-powered chat widget |
| 14 | **Language Hint** | Floating bubble pointing at language buttons |
| 15 | **Onboarding Overlay** | First-visit highlights (auto-dismiss 10s) |

### 6.2 Design Tokens

- **Colors:** `#00F5FF` (cyan), `#FF00E5` (magenta), `#FFD700` (gold), `#0B1226` (bg)
- **Effects:** Heartbeat animation on CTAs, sequential flag pulse (TH→NO→EN, 6s cycle)
- **Support chat:** Floating with quick-action buttons

---

## 7. THE MOBILE APP (Expo/React Native)

### 7.1 Tech Stack

- **Framework:** Expo SDK 54, React 19.1, React Native 0.81.5
- **Routing:** expo-router (file-based, 25 screens in `app/`)
- **State:** Zustand
- **Payments:** RevenueCat (`react-native-purchases`)
- **Build:** EAS Build (Metro bundler)

### 7.2 Screens (frontend/app/)

```
index.tsx, quiz.tsx, categories.tsx, library.tsx, teacher.tsx,
signs.tsx, book.tsx, results.tsx, paywall.tsx, settings.tsx,
history.tsx, bookmarks.tsx, traffic-math.tsx, ai-dashboard.tsx,
social.tsx, and ~10 more
```

### 7.3 Source Structure (frontend/src/)

```
├── components/    ← Reusable UI components
├── hooks/         ← Custom React hooks
├── services/      ← API service layer
├── store/         ← Zustand stores
├── constants/     ← Constants
└── theme/         ← Theme system
```

### 7.4 Web Export

Expo web build → `frontend/dist/` → manually copied to `backend/webapp/`

---

## 8. KEY BUSINESS LOGIC

### 8.1 Quiz Modes

| Mode | Questions | Timer | Access |
|------|-----------|-------|--------|
| Random practice | 30 | No | Free-limited |
| By category | 30 | No | Free-limited |
| Daily test | 10 | No | Premium only |
| Exam | 45 | 90 min | Premium only |
| Hard mode | variable | No | Premium only |
| Mistake mode | variable | No | Premium only |

### 8.2 Question Selection (Exam)

`_get_exam_questions()`:
- 90% hard difficulty, 10% medium
- Prioritizes previously-wrong questions
- image_only filter, shuffled options (Fisher-Yates)

### 8.3 Pricing

| Plan | Price (NOK) | Label |
|------|-------------|-------|
| Monthly | 99 kr | — |
| 3 Months | 249 kr | Best Value |
| Lifetime | 699 kr | — |

### 8.4 Access Tier Logic (usage.py)

- **Guest:** 5 lifetime (tracked by device_id via `guest_usage` collection)
- **Registered:** 10/day (resets midnight Europe/Oslo via `daily_usage`)
- **Premium:** unlimited (via Stripe Checkout or RevenueCat IAP)
- HTTP 402 responses carry `gate` payload (register/upgrade)

---

## 9. EXTERNAL INTEGRATIONS

### 9.1 Segment Analytics
- Initialized `server.py:43-49` via `analytics-python==2.1.8`
- Events: User Signed Up, User Logged In, Quiz Attempt Completed

### 9.2 Stripe
- Live mode only (rejects test keys)
- Dynamic pricing fetched from Stripe API
- Checkout Sessions → webhook → unlock premium

### 9.3 RevenueCat
- Webhook at `/api/rc/webhook`
- Maps `rc_original_app_user_id` to user in MongoDB

### 9.4 Email Delivery
- SendGrid (primary) → Resend (fallback) → SMTP (last resort)

### 9.5 Text-to-Speech
- Thai → Google Cloud TTS (male "Chirp3 HD")
- NO/EN → ElevenLabs ("Ai Mike" cloned voice) → fallback Google TTS

---

## 10. ADMIN PANEL

**URL:** `https://thai2drive.no/api/admin`

| Tab | Features |
|-----|----------|
| 📝 Spørsmål | List, create, edit, delete, image upload/delete, Unsplash search, AI Vision audit |
| 📖 Læringsbok | Book sections CRUD, image upload |
| 📹 Videoer | Learning video CRUD |
| 🎧 Podcaster | Podcast CRUD |
| 📖 Ordliste | Glossary CRUD |
| 🚦 Trafikkskilt | Sign database CRUD |
| 🔊 Voice Tester | ElevenLabs TTS test |

**Default admin credentials:** admin@thai2drive.com / admin123 (seeded at startup)

---

## 11. FILES BLOAT (Docker Build Context)

| File | Size |
|------|------|
| 4tTrafikkalt.pptx | 80 MB |
| application-*.aab | 62 MB |
| Microsoft PowerPoint - 4tTrafikkalt.pdf | 40 MB |
| PDF.4t.pdf | 40 MB |
| **Total bloat** | **~222 MB** |

---

## 12. KNOWN ISSUES

| Issue | Severity | Notes |
|-------|----------|-------|
| **Dark web app on user's screen** | 🔴 CRITICAL | **Årsak:** Migrering fra Emergent til Railway 25. juni — webappen brukte fortsatt gammel Emergent backend-URL. Fikset i commit `74ead5b` |
| **222 MB build context bloat** | 🟡 MEDIUM | Large files at repo root slow Railway builds |
| **.dockerignore in wrong location** | 🟡 MEDIUM | In `backend/`, but large files are at repo root |
| **Railway deploys from GitHub only** | 🟡 MEDIUM | Local changes require explicit push (see auto-push-and-verify memory) |
| **webapp/ manual sync** | 🟡 MEDIUM | Expo web build → copy step is manual, easy to forget |
| **No error monitoring** | 🟡 MEDIUM | No Sentry or similar — hard to detect when app breaks |
| **No CI/CD tests** | 🟢 LOW | No automated tests before deploy |

---

## 13. DEPLOYMENT WORKFLOW

```
Code change (local)
  → git add / git commit / git push origin main
  → GitHub triggers Railway auto-deploy
  → Railway builds Docker image (backend/Dockerfile)
  → Railway runs healthcheck (GET /api/_whoami → 200)
  → Railway routes traffic to new container

Web app update:
  → cd frontend && npx expo export --platform web
  → cp -r frontend/dist/* backend/webapp/
  → git add/commit/push (see above)
```

---

## 14. RECENT GIT HISTORY

| SHA | Date | Description |
|-----|------|-------------|
| 2e77b88 | 2026-06-25 | Fix Railway Dockerfile build + Segment analytics |
| 57f24ec | 2026-06-25 | Migrate from Emergent to Railway |
| 78ce70d | 2026-06-25 | Fix Library podcast audio_url→file_path |
| 74ead5b | 2026-06-25 | Backend URL → www.thai2drive.no |
| dd39680 | 2026-06-25 | Fix video cards when language title missing |
| — | 2026-06-24 | Neon design, 3D carousel, category optimizations |
| — | 2026-06-23 | Podcast library, admin glossary, V5 content |
| — | 2026-06-21 | 30+ questions, traffic sign library, inline video |
| — | 2026-06-20 | Offline resilience, studiebok edits, alert fixes |

---

## 15. AUDIT FINDINGS — Map vs. Reality (2026-06-25)

> **Kilde:** Automatisk revisjon utført 25. juni 2026 — 3 uavhengige agenter sjekket hver del av kartet mot faktisk kode.

### 15.1 API-endepunkter — Korreksjoner til kartet

**❌ Feil i kartet:**
- `GET /api/questions`: Kartet sier parametre `skip` og `image_only` — koden har kun `category`, `difficulty`, `limit`
- `PATCH /api/traffic-signs/{sign_id}`: Finnes ikke — kun `PUT` og `DELETE`

**➩ Mangler i kartet (24 ruter):**
- `GET /api/questions/debug`, `GET /api/web/version`, `GET /api/web/voice-tester`
- `GET /quiz-app/{full_path:path}` (SPA static mount)
- `GET /api/math/compare`, `POST /api/traffic-signs/{sign_id}/image`
- `PATCH /api/admin/videos/{video_id}`, `DELETE /api/admin/videos/{video_id}`
- `PATCH /api/admin/podcasts/{podcast_id}`, `DELETE /api/admin/podcasts/{podcast_id}`
- `GET/POST/PATCH/DELETE /api/admin/glossary*` (full CRUD)
- `GET /api/admin/stats`, `GET /api/support/chat/admin/escalations`
- `GET /api/teacher/welcome`, `GET /api/teacher/topics`
- `GET /api/admin/questions/{id}/thumbnail`
- `DELETE /api/admin/book/sections/{id}/image`, `DELETE/POST /api/admin/book/sections`
- `GET /api/admin/voice-tester`, `POST /api/admin/voice-test`

### 15.2 MongoDB Collections — Korreksjoner til kartet

**❌ Navnefeil:**
| Kartet sier | Virkeligheten heter |
|-------------|-------------------|
| `progress` | `user_progress` |
| `stripe_sessions` | `checkout_sessions` |

**❌ Finnes ikke i kode (fjernet fra kart):**
- `token_blacklist`, `reset_tokens`, `support_conversations`

**➩ Mangler i kartet (16 collections lagt til):**
`admin_users`, `access_usage`, `access_events`, `subscriptions`, `stripe_events`, `rc_events`, `ai_attempts`, `ai_srs_cards`, `ai_explanations`, `support_chats`, `support_escalations`, `teacher_chats`, `teacher_chat_logs`, `teacher_feedback` med flere.

### 15.3 Web App — Korreksjoner til kartet

- **Total linjer:** 9161 (kartet sa 9218 — avvik pga. versjonsforskjell)
- **studiebokModal:** HTML id er `studiebokEditModal`, ikke `studiebokModal`
- **GA snippet:** Finnes ikke i webapp.py — kartets påstand om Google Analytics er feil
- **Linjenummer i JS-seksjoner:** Forskjøvet med +18 til +29 linjer i enkelte moduler

### 15.4 Nøkkelfunn — Migreringsproblemet

Den **mørke skjermen** brukeren så (kun neon-ramme, intet innhold) skyldtes:
1. Migrering fra **Emergent** (gammel hosting) til **Railway** 25. juni 2026
2. Webappen refererte til gammel Emergent backend-URL: `norge-quiz-app.preview.emergentagent.com`
3. API-kallene feilet → appen fikk ingen data → viste bare mørk bakgrunn + neon border
4. Fikset i commit `74ead5b`: oppdaterte URL til `www.thai2drive.no`

### 15.5 Tiltak for å unngå gjentakelse

| Tiltak | Status |
|--------|--------|
| ✅ Auto-push: Alle endringer committes og pushes umiddelbart | ✅ Aktiv |
| ✅ Helsesjekk etter deploy: `GET /api/_whoami` → 200 | ✅ Aktiv |
| ✅ Version string i web app: `commit_sha` i HTML comment | ✅ Aktiv |
| ❌ Ingen URL-er hardkodet i webapp.js — bruk relativ sti `/api/...` | 🔲 Ikke gjort |

---

*End of Thai2Drive Complete System Map — v2.0. Audit completed 2026-06-25.*
