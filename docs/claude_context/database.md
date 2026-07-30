# Database, Seeding & Content Data

> Load this when: changing a schema, running seed scripts, or working with the content JSON files.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

## SQLite (local development)

- Database file: `backend/thai2drive.db`
- Schema changes: edit models in the relevant files, then run seed scripts to update
- Only one process should write at a time (otherwise: "database is locked")

## MongoDB (production via Railway)

- Connection via `motor` (async MongoDB driver)
- Migrations: handled via application logic, not schema migrations
- To inspect: use MongoDB Compass with the production connection string from the Railway dashboard

## When schema changes

1. Update model definitions in the affected module (e.g. `ai_explanations.py`)
2. Test locally with SQLite
3. Run seed scripts on the production database carefully (Railway admin can snapshot first)

**Do not write production database data unless explicitly requested.**

---

## Content Data

| File | Purpose |
|------|---------|
| `content/quiz_michael_v5.json` | Quiz questions (V5, Michael-approved) |
| `content/quiz_comprehensive.json` | Comprehensive question bank |
| `content/quiz_extended_practice.json` | Extended practice questions |
| `content/quiz_extra_questions.json` | Extra supplemental questions |
| `content/quiz_row_questions.json` | Row/ordering questions |
| `content/studybook_chapters_v5.json` | Study book chapters (V5) |
| `content/traffic_signs_expanded.json` | Expanded traffic sign data |
| `content/traffic_signs_explained.json` | Traffic signs with explanations |
| `content/new_glossary.json` | Glossary of terms |
| `content/new_podcasts.json` | Podcast content |
| `content/marketing_videos.json` | Marketing video scripts/metadata |
| `content/capcut_script_video*.md` | CapCut video editing scripts |
| `backend/signs_content.json` | Traffic signs content |
| `backend/content_packs/studiebok_i18n_v2.json` | Internationalized study book |

---

## Backend Scripts (`backend/scripts/`)

Run from the `backend/` directory with `python scripts/<name>.py`:

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
| `ab_test_openrouter.py` | A/B test models on Michael's system prompt (requires `OPENROUTER_API_KEY`) |

**Run seed scripts on production with caution** — they write to the database. Always test locally first.
