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

Key utility scripts (run from `backend/` directory):

| Script | Purpose |
|--------|---------|
| `seed_database.py` | Seed all content from content JSON files |
| `seed_studiebok.py` | Seed study book chapters |
| `seed_v2_questions.py` | Seed quiz questions (V2 schema) |
| `audit_questions.py` | Validate question quality |
| `audit_images.py` | Audit sign images |
| `balance_difficulty.py` | Balance difficulty distribution |
| `generate_questions.py` | Generate new questions from source |
| `check_quiz_quality.py` | Check quiz quality metrics |
| `retention_worker.py` | Background retention worker |
| `ab_test_openrouter.py` | A/B test models on Michael's system prompt |

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
