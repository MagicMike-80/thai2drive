# Local Development, Testing & Debugging

> Load this when: running the app locally, writing/running tests, setting up `.env`, or debugging.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

## Running Tests

**Note:** `backend/tests/` does not exist yet — the commands below are aspirational. No frontend test framework is configured.

```bash
# All backend tests (once tests/ exists)
cd backend && pytest -v

# Single test file
cd backend && pytest tests/test_auth.py -v

# Single test
cd backend && pytest tests/test_auth.py::test_login_success -v

# With coverage report
cd backend && pytest --cov --cov-report=term-missing

# Run only failing tests
cd backend && pytest --lf -v
```

---

## Environment Variables (.env)

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

**Frontend (`frontend/.env.local`):**

```
EXPO_PUBLIC_API_URL=http://localhost:8000  # or production URL
```

Never commit `.env` — use `.env.example` as the template.

---

## Debugging Tips

**Backend logging:**

```bash
# See all API calls and AI prompts
LITELLM_LOG=DEBUG uvicorn server:app --reload --port 8000

# See database queries
SQLALCHEMY_ECHO=true uvicorn server:app --reload
```

**Frontend console:**

- Android: `npx expo start --android` → press `i` for console logs
- Use `console.log()` to debug Zustand state changes

**Common issues:**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` in backend | Activate venv: `source venv/Scripts/activate` (Windows) or `venv/bin/activate` (Unix) |
| Expo metro bundler timeout | Restart with `npx expo start --clear` |
| Backend won't start (port 8000 in use) | `lsof -i :8000` and kill the process, or use `--port 9000` |
| JWT token expired errors | Token expires after 30 days; test with a fresh login |
| Database locked (SQLite) | Close other connections; only one process should write at a time |
| AI endpoints timeout (>30s) | Check `OPENAI_API_KEY` or increase the timeout in `backend/server.py` |
