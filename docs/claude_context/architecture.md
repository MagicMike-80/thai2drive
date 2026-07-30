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
│   ├── auth.py                # JWT authentication
│   ├── requirements.txt        # Python dependencies
│   ├── thai2drive.db          # Local SQLite database
│   ├── scripts/               # Utility scripts (seed, audit, generate)
│   └── tests/                 # Pytest test suite
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
│  Web: Expo web (same codebase)      │  ← File-based routing in frontend/app/
│  State: Zustand                     │  ← frontend/src/store/appStore.ts
│  API: frontend/src/services/api.ts  │  ← Typed fetch wrapper, all endpoints
├─────────────────────────────────────┤
│  Backend: FastAPI (Python 3.12)     │  ← uvicorn server:app
│  Database: SQLite (local) / MongoDB (prod via motor+pymongo)
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
| `backend/webapp.py` | Web app routes |
| `backend/landing.py` | Landing page routes |
| `backend/website.py` | Website routes |
| `backend/support_chat.py` | Support chat |
| `backend/guide.py` | Guide content |
| `backend/usage.py` | Usage tracking |
| `backend/thai2drive.db` | Local SQLite database |

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
- **Database seeding:** Run `POST /api/seed` or use scripts in `backend/scripts/` directly via python. When schema changes, update seed data in the same patch. See [`database.md`](database.md).

Data contracts (`LocalizedText`, question schema, access tiers) live in [`api.md`](api.md).
