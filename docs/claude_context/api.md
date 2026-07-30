# API & Data Contracts

> Load this when: changing an endpoint, touching the frontend↔backend contract, or adding a field to quiz/content data.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

## Endpoints (base: `/api`)

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

The typed client for all of these is `frontend/src/services/api.ts`.

---

## Data Contracts

### LocalizedText

```ts
{ no: string; th: string; en: string }
```

Every user-facing text is trilingual. Thai mode = 100% Thai, Norwegian = 100% Norwegian, English = 100% English. **No fallback between languages.**

### Question schema (V2)

```ts
{
  id,
  question: LocalizedText,
  options: [{ id: "A" | "B" | "C" | "D", text: LocalizedText }],
  correctOptionId,
  explanation: LocalizedText,
  bildeUrl?,
  category,
  difficulty,
  active
}
```

### Access tiers

guest (5 total) → registered (10/day) → premium (unlimited). **Enforced server-side.**

Do not change tier logic, quota, or Stripe wiring unless explicitly requested — see [`workflow.md`](workflow.md).
