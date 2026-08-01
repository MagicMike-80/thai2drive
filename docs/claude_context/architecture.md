# Architecture

> Load this when: adding a feature, refactoring, or asking "where does X live?"
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

## Repository Structure at a Glance

```
thai2drive/
├── backend/                    # FastAPI server, database, AI logic
│   ├── server.py              # Main app, all route definitions
│   ├── teacher_chat.py        # Michael teacher AI implementation
│   ├── ai_explanations.py     # AI-generated quiz explanations
│   ├── ai_learning.py         # Adaptive learning logic
│   ├── webapp.py              # Produksjons-webappen (WEBAPP_HTML) → /api/web
│   ├── requirements.txt        # Python dependencies
│   ├── scripts/               # Utility scripts (seed, audit, generate)
│   ├── webapp/                # Bygget Expo-web-eksport → /quiz-app (artefakt)
│   └── tests/                 # Pytest — peker mot PRODUKSJON, se CLAUDE.md
├── frontend/                   # Expo/React Native mobile + web
│   ├── app/                   # Expo Router file-based routing
│   │   ├── _layout.tsx        # Root layout + navigation
│   │   ├── index.tsx          # Home screen
│   │   ├── quiz.tsx           # Quiz mode
│   │   ├── teacher.tsx        # Michael chat screen
│   │   ├── book.tsx           # Study book
│   │   └── ...                # Other screens
│   ├── src/
│   │   ├── store/             # Zustand state management
│   │   ├── services/          # API client (api.ts)
│   │   ├── components/        # Reusable UI components
│   │   ├── hooks/             # Custom React hooks
│   │   └── theme.ts           # Design tokens (colors, spacing)
│   ├── package.json           # npm/yarn dependencies
│   ├── app.json               # Expo configuration
│   └── README.md              # Frontend-specific setup
├── website/                    # Static website (Netlify)
├── content/                    # JSON content files
├── context/                    # Session memory and blueprints
├── docs/claude_context/        # Just-in-time docs for Claude Code
├── .github/
│   └── workflows/             # CI/CD pipeline (auto-deploy to Railway)
├── CLAUDE.md                   # Slim index — core rules + doc index
└── README.md                   # Project overview
```

---

## Stack

```
┌─────────────────────────────────────┐
│  Mobile: Expo (React Native 0.81)   │  ← Expo SDK 54, Expo Router v6, TypeScript 5.9
│  Webapp (prod): backend/webapp.py   │  ← vanilje-JS SPA i WEBAPP_HTML, /api/web
│  Expo web (sekundær): /quiz-app     │  ← samme frontend/-kodebase, statisk eksport
│  State: Zustand                     │  ← frontend/src/store/appStore.ts
│  API: frontend/src/services/api.ts  │  ← Typed fetch wrapper, all endpoints
├─────────────────────────────────────┤
│  Backend: FastAPI (Python 3.12)     │  ← uvicorn server:app
│  Database: MongoDB (motor) — eneste │  ← server.py:29-31, os.environ['MONGO_URL']
│    DB. Ingen SQLite-kodesti finnes. │     + os.environ['DB_NAME'], kreves ved import
│  AI: Gemini + OpenAI + LiteLLM      │  ← ai_explanations.py, teacher_chat.py
│  Auth: JWT (python-jose + passlib)  │  ← server.py
│  Payments: Stripe                   │  ← server.py /api/pricing, /api/create-checkout-session
│  Storage: AWS S3 (boto3)            │  ← sign images, media
└─────────────────────────────────────┘
```

---

## Key Backend Files

| File | Purpose |
|------|---------|
| `backend/server.py` | FastAPI app entry point, all routes, auth, seed, CORS |
| `backend/teacher_chat.py` | AI teacher Michael — chat endpoint, pedagogy logic |
| `backend/ai_explanations.py` | AI-generated explanations for quiz answers |
| `backend/ai_learning.py` | Adaptive learning, personal weak-topic analysis |
| `backend/ai_routes.py` | Additional AI API routes |
| `backend/quiz_web.py` | Quiz web interface routes |
| `backend/signs_data.py` | Traffic signs data management |
| `backend/traffic_math.py` | Overtaking/stopping distance calculator |
| `backend/site_config.py` | Site configuration |
| `backend/webapp.py` | **Hele produksjons-webappen** — se seksjonen under. ~9 500 linjer, nesten alt er én rå Python-streng. Kun 3 ruter. |
| `backend/landing.py` | **Ikke ruter.** HTML/CSS/JS-byggeklosser (`LANDING_CSS`, `_hero_html()`, `_features_html()` osv.) satt sammen av `build_landing_page()`, kalt fra `website.py:533` |
| `backend/website.py` | Offentlig nettsted: `/website`, `/guide`, `/privacy`, `/terms`, `/support`, `/bok`, `sitemap.xml`, `robots.txt` |
| `backend/support_chat.py` | Support chat |
| `backend/guide.py` | Guide content |
| `backend/usage.py` | Usage tracking |
| `backend/thai2drive.db` | **Levning — brukes ikke.** Ingen `sqlite3`-import finnes i `backend/*.py`. |

### De to web-flatene (forveksles lett)

| Flate | Kilde | URL | Status |
|-------|-------|-----|--------|
| **Webapp** | `backend/webapp.py` — én rå Python-streng `WEBAPP_HTML` med all HTML/CSS/vanilje-JS inline | `/api/web` | **Produksjon.** Stripe-checkout returnerer hit (`server.py:1402`). |
| Expo web | `frontend/` bygget til `backend/webapp/` | `/quiz-app` | Sekundær. Statisk mount i `server.py:5350+`, fallback exact → `{navn}.html` → `index.html` |

Endringer i webappen gjøres i `WEBAPP_HTML`-strengen — **ikke** i `backend/webapp/`, som er et
byggeartefakt og overskrives ved neste Expo-eksport. `/api/web/version` returnerer en
`RAILWAY_GIT_COMMIT_SHA`-basert versjon; bruk den til å bekrefte hvilken build som er live.

Alle routere monteres under `/api` i `server.py` (~4716–4745). `website_router` monteres
**to ganger** — både på `""` og `/api` — fordi Railway ruter på `/api/*`.

---

## Key Frontend Files

| Path | Purpose |
|------|---------|
| `frontend/app/_layout.tsx` | Root layout, navigation container |
| `frontend/app/index.tsx` | Home screen |
| `frontend/app/quiz.tsx` | Quiz mode |
| `frontend/app/teacher.tsx` | AI teacher Michael chat |
| `frontend/app/book.tsx` | Study book reader |
| `frontend/app/signs.tsx` | Traffic signs browser |
| `frontend/app/settings.tsx` | User settings (language, profile) |
| `frontend/app/bookmarks.tsx` | User bookmarks |
| `frontend/app/history.tsx` | Quiz history |
| `frontend/app/stats.tsx` | Statistics/progress |
| `frontend/app/traffic-math.tsx` | Traffic math exercises |
| `frontend/src/store/appStore.ts` | Zustand global state |
| `frontend/src/services/api.ts` | Backend API client (all endpoints) |
| `frontend/src/hooks/` | Custom hooks (useRevenueCat, useScreenProtection, etc.) |
| `frontend/src/theme.ts` | Theme constants (colors, spacing) |
| `frontend/src/components/` | Reusable UI components (BottomNavBar, ExplanationCard, CoachBanner, GateModal, Flag, LanguageSwitcher, AppBrand, ExpandableButtonGroup, BookHtml) |
| `frontend/src/components/traffic/` | Traffic-sign-specific components |
| `frontend/app.json` | Expo config (v1.2.0, Android: com.michael.thai2drive, iOS: no.thai2drive.app) |

---

## Key Patterns

- **State management:** Zustand store at `frontend/src/store/appStore.ts` — single store with slices for auth, quiz, settings, etc.
- **Navigation:** Expo Router file-based routing in `frontend/app/`. Each file = one screen.
- **Styling:** No Tailwind — plain React Native `StyleSheet.create()` with theme constants from `frontend/src/theme.ts`.
- **Database seeding:** `POST /api/seed`, eller scripts i `backend/scripts/` direkte via python. Når schema endres, oppdater seed-data i samme patch. See [`database.md`](database.md).
  ⚠️ `backend/tests/test_thai2drive_api.py` og `backend_test.py` har hardkodet
  `BASE_URL = "https://www.thai2drive.no"`, og den første gjør `POST /api/seed` mot
  **produksjonsdatabasen**. Kjør aldri `pytest -v` blindt — se testseksjonen i
  [`../../CLAUDE.md`](../../CLAUDE.md).

Data contracts (`LocalizedText`, question schema, access tiers) live in [`api.md`](api.md).
