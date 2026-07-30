# Dependency Management

> Load this when: upgrading a package, adding a dependency, or diagnosing a version conflict.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

**Package manager:** `yarn` (pinned to v1.22.22 in `package.json`) — do not use `npm` for frontend commands.

## Frontend (Expo)

- **Expo SDK:** 54.0.33 (major upgrades break native modules)
- **React Native:** 0.81.5 (pinned; upgrading requires testing on both Android & iOS)
- **React:** 19.1.0 (Hooks, Suspense stable)
- **Zustand:** 5.0.12 (state management, no boilerplate)
- **Expo Router:** 6.0.22 (file-based routing, replaces React Navigation)

**Upgrade process:**

1. Test in a development build first (`eas build --platform android --profile preview`)
2. Verify on an actual Android device (the emulator can hide issues)
3. Run `cd frontend && yarn lint` before committing
4. Update `package.json` and `yarn.lock`

## Backend (Python)

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
3. Run the full test suite: `cd backend && pytest -v`
4. Deploy to Railway staging first (create a feature branch)
5. Verify with live API tests before deploying to production

## Known constraints

- Motor must match MongoDB version compatibility
- Pydantic 2.x has breaking changes from 1.x (field validation)
- LiteLLM handles model routing; changing the default model requires testing all AI endpoints
