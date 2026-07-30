# Deployment & Production Safety

> Load this when: deploying, releasing, or rolling back.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

## Targets

- **Production backend:** `https://thai2drive-production.up.railway.app`
- **Deploy:** push to `main` on GitHub → Railway auto-deploys the backend
- **CI/CD:** `.github/workflows/auto-deploy.yml` (placeholder — runs on push to main, daily 2am, manual dispatch)
- **Netlify:** static legal pages via `netlify.toml` (privacy, terms, support)
- **Static web build:** `cd frontend && yarn expo export --platform web`
- **Build mobile (APK):** `cd frontend && eas build --platform android --profile preview`
- **Backend Docker:** `docker build -t thai2drive backend/`

---

## Production Safety Checklist

Before deploying to Railway:

- [ ] Backend tests pass: `cd backend && pytest -v`
- [ ] No hardcoded API keys in code (use `.env`)
- [ ] Frontend builds without warnings: `cd frontend && yarn lint`
- [ ] Database migrations tested locally
- [ ] AI endpoints tested with real API keys
- [ ] Error handling for timeouts (AI, S3, Stripe)
- [ ] CORS configured correctly (check Railway logs for 403 errors)
- [ ] Stripe webhook secret matches Railway config
- [ ] `JWT_SECRET_KEY` is strong and consistent
- [ ] MongoDB connection string uses production credentials
- [ ] S3 bucket permissions allow uploads
- [ ] Rate limiting tested (user quota enforced server-side)

---

## Rollback procedure

- Railway keeps previous deployments; click "Redeploy" on a prior version
- SQLite data is local; MongoDB has snapshots via Atlas
- Notify mobile users to force refresh the app (clear cache)
