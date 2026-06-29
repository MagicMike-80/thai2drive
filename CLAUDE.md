# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

| Layer | Path | Command |
|-------|------|---------|
| Backend (FastAPI) | `backend/` | `cd backend && uvicorn server:app --reload --port 8000` |
| Mobile (Expo/React Native) | `frontend/` | `cd frontend && npx expo start --android` |
| Backend tests | `backend/tests/` | `cd backend && pytest tests/ -v` |
| Lint frontend | `frontend/` | `cd frontend && npx expo lint` |
| Scripts | `backend/scripts/` | `cd backend && python scripts/<script>.py` |
| Build mobile (APK) | `frontend/` | `cd frontend && eas build --platform android --profile preview` |
| Backend Docker | `backend/` | `docker build -t thai2drive backend/` |

**Production backend:** `https://thai2drive-production.up.railway.app`
**Deploy:** Push to `main` on GitHub → Railway auto-deploys backend
**CI/CD:** `.github/workflows/auto-deploy.yml` (placeholder — runs on push to main, daily 2am, manual dispatch)
**Netlify:** Static legal pages via `netlify.toml` (privacy, terms, support)
**Static web build:** `cd frontend && npx expo export --platform web`

---

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
├── .github/
│   └── workflows/             # CI/CD pipeline (auto-deploy to Railway)
├── CLAUDE.md                   # This file
└── README.md                   # Project overview
```

---

## High-Level Architecture

### Stack

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

### Key Backend Files

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

### Key Frontend Files

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
| `frontend/src/components/` | Reusable UI components |
| `frontend/app.json` | Expo config (v1.2.0, Android: com.michael.thai2drive, iOS: no.thai2drive.app) |

### API Endpoints (base: `/api`)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/questions` | List questions (filter by category, difficulty, limit) |
| `GET /api/questions/random` | Random questions (count, category) |
| `GET /api/categories` | List categories with question counts |
| `GET /api/categories/v2` | V2 categories |
| `GET /api/chapters` | Study book chapters |
| `GET /api/chapters/{num}` | Sections in a chapter |
| `GET /api/signs` | Traffic signs (grouped) |
| `GET /api/traffic-signs` | Traffic signs (V2 schema) |
| `GET /api/progress/{device_id}` | User progress |
| `POST /api/quiz-attempts` | Save quiz attempt |
| `GET /api/stats/me` | User statistics by category |
| `GET/POST /api/access/status` | Access tier check |
| `POST /api/access/consume` | Consume a question attempt |
| `POST /api/auth/signup` | User registration |
| `POST /api/auth/login` | User login |
| `GET /api/auth/me` | Current user info |
| `POST /api/teacher/chat` | AI teacher Michael chat |
| `POST /api/ai/explain` | AI explanation for a question |
| `GET /api/pricing` | Premium pricing plans |
| `POST /api/create-checkout-session` | Stripe checkout |
| `POST /api/seed` | Seed database |
| `GET /api/traffic-math` | Traffic math calculator |

### Key Patterns

- **LocalizedText type:** `{ no: string; th: string; en: string }` — every user-facing text is trilingual. Thai mode = 100% Thai, Norwegian = 100% Norwegian, English = 100% English. No fallback between languages.
- **Access tiers:** guest (5 total) → registered (10/day) → premium (unlimited). Enforced server-side.
- **Question schema (V2):** `{ id, question: LocalizedText, options: [{id: "A"|"B"|"C"|"D", text: LocalizedText}], correctOptionId, explanation: LocalizedText, bildeUrl?, category, difficulty, active }`
- **Database seeding:** Run `POST /api/seed` or use scripts in `backend/scripts/` directly via python. When schema changes, update seed data in the same patch.
- **State management:** Zustand store at `frontend/src/store/appStore.ts` — single store with slices for auth, quiz, settings, etc.
- **Navigation:** Expo Router file-based routing in `frontend/app/`. Each file = one screen.
- **Styling:** No Tailwind — plain React Native `StyleSheet.create()` with theme constants from `frontend/src/theme.ts`.

### Content Data

| File | Purpose |
|------|---------|
| `content/quiz_michael_v5.json` | Quiz questions (V5, Michael-approved) |
| `content/studybook_chapters_v5.json` | Study book chapters (V5) |
| `backend/signs_content.json` | Traffic signs content |
| `backend/content_packs/studiebok_i18n_v2.json` | Internationalized study book |

### Backend Scripts (`backend/scripts/`)

Key utility scripts (run from `backend/` directory with `python scripts/<name>.py`):

| Script | Purpose |
|--------|---------|
| `seed_database.py` | Seed all content from content JSON files |
| `seed_studiebok.py` | Seed study book chapters |
| `seed_v2_questions.py` | Seed quiz questions (V2 schema) |
| `seed_podcasts_v4.py` | Seed podcast content |
| `seed_videos_v1.py` | Seed video content |
| `audit_questions.py` | Validate question quality (difficulty balance, translations, clarity) |
| `audit_images.py` | Audit sign images for S3 upload |
| `balance_difficulty.py` | Rebalance difficulty distribution across categories |
| `generate_questions.py` | Generate new questions from source documents |
| `check_quiz_quality.py` | Check quiz quality metrics and coverage |
| `retention_worker.py` | Background retention worker for adaptive learning |
| `ab_test_openrouter.py` | A/B test models on Michael's system prompt (requires OPENROUTER_API_KEY) |

**Run seed scripts on production with caution** — they write to the database. Always test locally first.

---

## Common Development Tasks

### Running Tests
```bash
# All backend tests
cd backend && pytest tests/ -v

# Single test file
cd backend && pytest tests/test_auth.py -v

# Single test
cd backend && pytest tests/test_auth.py::test_login_success -v

# With coverage report
cd backend && pytest tests/ --cov --cov-report=term-missing

# Run only failing tests
cd backend && pytest --lf -v
```

### Database & Schema Changes

**SQLite (local development):**
- Database file: `backend/thai2drive.db`
- Schema changes: edit models in relevant files, then run seed scripts to update

**MongoDB (production via Railway):**
- Connection via `motor` (async MongoDB driver)
- Migrations: handled via application logic, not schema migrations
- To inspect: Use MongoDB Compass with production connection string from Railway dashboard

**When schema changes:**
1. Update model definitions in the affected module (e.g., `ai_explanations.py`)
2. Test locally with SQLite
3. Run seed scripts on production database carefully (Railway admin can snapshot before)

### Environment Variables (.env)

**Required for backend:**
```
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
GEMINI_API_KEY=...  # Optional, falls back to OpenAI
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/database  # Production only
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=thai2drive
JWT_SECRET_KEY=<random-secret>
OPENROUTER_API_KEY=sk-or-...  # Optional, for A/B testing models
```

**Frontend (.env in frontend/.env.local):**
```
EXPO_PUBLIC_API_URL=http://localhost:8000  # or production URL
```

Never commit `.env` — use `.env.example` as template.

### AI Components

**Michael Teacher Chat** (`backend/teacher_chat.py`):
- System prompt in Michael's voice (calm, real driving instructor tone)
- Enforces Thai/Norwegian/English language purity (no code-switching)
- No visible AI system messages
- Uses Gemini/OpenAI via LiteLLM for routing

**AI Explanations** (`backend/ai_explanations.py`):
- Explains quiz answers with pedagogy focus
- Follows exam tips and common mistakes pattern
- Respects question difficulty level in explanation depth

**Adaptive Learning** (`backend/ai_learning.py`):
- Personal weak-topic analysis per user
- Suggests practice based on quiz history
- Tracks improvement over time

**Models used (via LiteLLM):**
- Default: `gpt-4-turbo` or `gpt-3.5-turbo`
- Alternative: `gemini-1.5-pro`
- Cost-aware: Falls back based on `LITELLM_LOG=DEBUG`

### Debugging Tips

**Backend logging:**
```bash
# See all API calls and AI prompts
LITELLM_LOG=DEBUG uvicorn server:app --reload --port 8000

# See database queries
SQLALCHEMY_ECHO=true uvicorn server:app --reload
```

**Frontend console:**
- Android: `npx expo start --android` → press `i` for console logs
- Run `console.log()` statements to debug Zustand state changes

**Common issues:**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` in backend | Activate venv: `source venv/Scripts/activate` (Windows) or `venv/bin/activate` (Unix) |
| Expo metro bundler timeout | Restart with `npx expo start --clear` |
| Backend won't start (port 8000 in use) | `lsof -i :8000` and kill process, or change `--port 9000` |
| JWT token expired errors | Token expires after 30 days; test with fresh login |
| Database locked (SQLite) | Close any other connections; only one process should write at a time |
| AI endpoints timeout (>30s) | Check `OPENAI_API_KEY` or increase timeout in `backend/server.py` |

---

## DeepSeek & Claude Code Configuration

Claude Code is configured to run via DeepSeek in this repository. The local configuration is saved in:
- [.claude/settings.local.json](file:///C:/Users/Stein%20Hoang/thai2drive/.claude/settings.local.json) (which contains the active DeepSeek endpoint and API key). Do not delete or overwrite this file.

---

## Thai2Drive Collaboration Lock

Claude Code and Codex must not work on the same responsibility at the same time.

### Ownership

- **Claude Code** owns content, pedagogy, traffic theory explanations, Thai/Norwegian/English wording, Michael Trafikklærer tone/personality, question wording, common mistakes, exam tips, video scripts, lesson structure, and learning goals.
- **Codex** owns code implementation, backend/API, database scripts, validation/import systems, web/mobile changes, tests, Git/GitHub/Railway, deployment, logging, monitoring, and production safety.

### Stop Rule

If a task belongs to Codex, stop and say:

"This task belongs to Codex. I should not do this part."

If ownership is unclear, ask whether it is a Codex implementation task or a Claude Code content task before changing files.

### Master Blueprint

`context/MASTER_BLUEPRINT.md` is the approved product vision for Thai2Drive. Read it when starting work on any new feature. It defines architecture, pedagogy, business model, and ownership rules.

### Feature Wishlist — Automatic Rule

`context/FEATURES.md` is the permanent wishlist for everything Michael wants.
- When Michael mentions any wish, idea, or feature request: add it to `context/FEATURES.md` immediately in the same response — do not wait.
- When a feature ships to Railway: move it to ✅ LEVERT in `context/FEATURES.md`.
- Never store secrets in `context/FEATURES.md`. Never commit it to git.
- All UI features: web app first, mobile only after Michael's explicit approval.

### Product Rules

- Web first. Mobile follows only after web approval.
- Do not write production database data unless explicitly requested.
- Do not touch Stripe, auth, premium, quota, MongoDB production data, or mobile/Android unless explicitly requested.
- Thai mode must be 100% Thai, Norwegian mode 100% Norwegian, and English mode 100% English.
- Michael should feel like a calm real driving instructor, not a generic chatbot or visible AI system.

### Karpathy Coding Principles
- **Tenk før du koder:** Still oppklarende spørsmål hvis oppgaven er uklar; gjør aldri antakelser i stillhet.
- **Enkelhet først:** Bygg den enkleste mulige løsningen; unngå over-engineering og spekulative abstraksjoner.
- **Kirurgiske endringer:** Gjør kun presise endringer som er direkte nødvendige for oppgaven; ikke refaktorer eller endre urelatert kode.
- **Ikke fiks det som fungerer:** La fungerende kode være i fred hvis det ikke er en del av den forespurte oppgaven.

### Michael Roadmap

- V1: Michael as a good chat teacher.
- V2: Michael connected to approved Thai2Drive content.
- V3: Mini-practice and coaching.
- V4: Personal weak-topic learning.
- V5: Voice, video, visual explanations, and adaptive AI instructor.

---

## Dependency Management

### Frontend (Expo)
- **Expo SDK:** 54.0.33 (major upgrades break Native modules)
- **React Native:** 0.81.5 (pinned; upgrading requires testing on both Android & iOS)
- **React:** 19.1.0 (Hooks, Suspense stable)
- **Zustand:** 5.0.12 (state management, no boilerplate)
- **Expo Router:** 6.0.22 (file-based routing, replaces React Navigation)

**Upgrade process:**
1. Test in development build first (`eas build --platform android --profile preview`)
2. Verify on actual Android device (emulator can hide issues)
3. Run `npx expo lint` before committing
4. Update `package.json` and `yarn.lock`

### Backend (Python)
- **Python:** 3.12
- **FastAPI:** 0.110.1 (async, auto-docs)
- **Pydantic:** 2.12.5 (validation, JSON schemas)
- **Motor:** 3.3.1 (async MongoDB driver)
- **Stripe:** 15.0.1 (payment processing)
- **Google Generative AI:** 0.8.6 (Gemini)
- **OpenAI:** 1.99.9 (LLM)
- **LiteLLM:** 1.80.0 (model routing, fallback)
- **PyJWT:** 2.12.1 (JWT auth)

**Upgrade process:**
1. Update `requirements.txt` with new versions
2. Test locally with SQLite
3. Run full test suite: `pytest tests/ -v`
4. Deploy to Railway staging first (create feature branch)
5. Verify with live API tests before deploying to production

**Known constraints:**
- Motor must match MongoDB version compatibility
- Pydantic 2.x has breaking changes from 1.x (field validation)
- LiteLLM handles model routing; changing default model requires testing all AI endpoints

---

## Performance & Optimization

### Frontend Performance

**Bundle size:** Expo web export should stay under 1MB gzipped
- Use `expo export --platform web` to build and check size
- Avoid inline images; use Expo Image for optimization
- Lazy load screens with Expo Router route-specific splitting

**Mobile performance:**
- Avoid re-renders: use `useMemo` for expensive computations
- Zustand subscriptions are fine (don't cause unnecessary renders)
- Use Reanimated 4.1.1 for smooth animations (not CSS)

### Backend Performance

**API latency targets:**
- Quiz retrieval: <100ms
- AI explanations: <5s (LLM inference time)
- Teacher chat: <10s (streaming preferred)
- User stats: <200ms

**Database optimization:**
- SQLite: Add indexes on frequently queried columns (user_id, category, created_at)
- MongoDB: Use `motor` for non-blocking queries
- Caching: Zustand on frontend caches user state (avoids refetches)

**AI cost optimization:**
- Use `gpt-3.5-turbo` for simple explanations
- Use `gpt-4-turbo` only for complex reasoning (teacher chat)
- Cache quiz explanations server-side (same question, same explanation)
- LiteLLM can fallback to cheaper models on token limits

---

## Production Safety Checklist

Before deploying to Railway:

- [ ] Backend tests pass: `pytest tests/ -v`
- [ ] No hardcoded API keys in code (use `.env`)
- [ ] Frontend builds without warnings: `npm run lint` or `yarn lint`
- [ ] Database migrations tested locally
- [ ] AI endpoints tested with real API keys
- [ ] Error handling for timeouts (AI, S3, Stripe)
- [ ] CORS configured correctly (check Railway logs for 403 errors)
- [ ] Stripe webhook secret matches Railway config
- [ ] JWT_SECRET_KEY is strong and consistent
- [ ] MongoDB connection string uses production credentials
- [ ] S3 bucket permissions allow uploads
- [ ] Rate limiting tested (user quota enforced server-side)

**Rollback procedure:**
- Railway keeps previous deployments; click "Redeploy" on prior version
- SQLite data is local; MongoDB has snapshots via Atlas
- Notify mobile users to force refresh app (clear cache)
