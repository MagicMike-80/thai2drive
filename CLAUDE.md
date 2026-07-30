# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Kjerneregler

- **Planlegging Først:** Bruk alltid `/plan` før store endringer.
- **Språkisolasjon:** Hold thai, norsk og engelsk 100% adskilt.
- **Pedagogikk:** Bruk 7-årsregelen og Michael-personaen (trygg, rolig).
- **Arbeidsfordeling:** Deep håndterer innhold. Backend/database er Anti sin jobb.

### Absolutte sikkerhetsregler (gjelder alltid, uten unntak)

- **Language Purity:** 100% isolasjon — thai-modus = kun thai, norsk = kun norsk, engelsk = kun engelsk. Ingen fallback.
- **Web-first:** Alle UI-endringer i webappen først. Mobil kun etter Michaels eksplisitte godkjenning.
- **Rør aldri Stripe, auth, premium, kvote, produksjons-DB eller mobil/Android** uten eksplisitt forespørsel.
- **Stop-regelen:** Hvis oppgaven eies av Anti (kode/backend/deploy), si «This task belongs to Anti. I should not do this part.» Er eierskapet uklart — spør først.
- **Aldri commit hemmeligheter:** `.env`, `.claude/settings.local.json` og `context/FEATURES.md` skal aldri committes eller overskrives.

Utdypning av disse: [`docs/claude_context/workflow.md`](docs/claude_context/workflow.md)

## Session Start

Les `context/MEMORY.md` og `context/USER.md` ved starten av hver sesjon.

## Quick Reference

| Layer | Path | Command |
|-------|------|---------|
| Backend (FastAPI) | `backend/` | `cd backend && uvicorn server:app --reload --port 8000` |
| Mobile (Expo/React Native) | `frontend/` | `cd frontend && yarn android` |
| Web (Expo web) | `frontend/` | `cd frontend && yarn web` |
| Backend tests | `backend/` | `cd backend && pytest -v` |
| Single test | `backend/` | `cd backend && pytest tests/test_auth.py::test_login_success -v` |
| Lint frontend | `frontend/` | `cd frontend && yarn lint` |
| Scripts | `backend/scripts/` | `cd backend && python scripts/<script>.py` |
| Build mobile (APK) | `frontend/` | `cd frontend && eas build --platform android --profile preview` |
| Backend Docker | `backend/` | `docker build -t thai2drive backend/` |

**Package manager:** `yarn` (pinnet til v1.22.22) — bruk aldri `npm` for frontend.

## Dokumentasjonsindeks (Just-In-Time)

Les kun filen du trenger for oppgaven — ikke alle.

| Les denne | Når oppgaven handler om |
|-----------|-------------------------|
| [`architecture.md`](docs/claude_context/architecture.md) | Mappestruktur, stack, hvilke filer som gjør hva, kodemønstre |
| [`api.md`](docs/claude_context/api.md) | Endepunkter, `LocalizedText`, question-schema V2, access tiers |
| [`database.md`](docs/claude_context/database.md) | SQLite/MongoDB, schema-endringer, seed-scripts, content-JSON |
| [`development.md`](docs/claude_context/development.md) | Kjøre lokalt, tester, `.env`, debugging, vanlige feil |
| [`ai-components.md`](docs/claude_context/ai-components.md) | Michael-chat, AI-forklaringer, adaptiv læring, LiteLLM, roadmap |
| [`dependencies.md`](docs/claude_context/dependencies.md) | Versjoner, oppgraderinger, kjente begrensninger |
| [`performance.md`](docs/claude_context/performance.md) | Bundle-størrelse, latency-mål, DB- og AI-kostnadsoptimalisering |
| [`deployment.md`](docs/claude_context/deployment.md) | Railway, Netlify, CI/CD, sikkerhetssjekkliste, rollback |
| [`workflow.md`](docs/claude_context/workflow.md) | Eierskap, Collaboration Lock, produktregler, Karpathy, `context/`-systemet |

## gstack

Use /browse from gstack for all web browsing. Never use mcp__claude-in-chrome__* tools.
Available skills: /office-hours, /plan-ceo-review, /plan-eng-review, /plan-design-review,
/design-consultation, /design-shotgun, /design-html, /review, /ship, /land-and-deploy,
/canary, /benchmark, /browse, /open-gstack-browser, /qa, /qa-only, /design-review,
/setup-browser-cookies, /setup-deploy, /setup-gbrain, /sync-gbrain, /retro, /investigate,
/document-release, /document-generate, /codex, /cso, /autoplan, /pair-agent, /careful, /freeze,
/guard, /unfreeze, /gstack-upgrade, /learn.
