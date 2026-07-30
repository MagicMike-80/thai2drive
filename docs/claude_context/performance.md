# Performance & Optimization

> Load this when: something is slow, or you are optimizing bundle size, queries, or AI cost.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)

## Frontend Performance

**Bundle size:** the Expo web export should stay under 1MB gzipped.

- Use `expo export --platform web` to build and check size
- Avoid inline images; use Expo Image for optimization
- Lazy load screens with Expo Router route-specific splitting

**Mobile performance:**

- Avoid re-renders: use `useMemo` for expensive computations
- Zustand subscriptions are fine (they don't cause unnecessary renders)
- Use Reanimated 4.1.1 for smooth animations (not CSS)

---

## Backend Performance

**API latency targets:**

- Quiz retrieval: <100ms
- AI explanations: <5s (LLM inference time)
- Teacher chat: <10s (streaming preferred)
- User stats: <200ms

**Database optimization:**

- SQLite: add indexes on frequently queried columns (`user_id`, `category`, `created_at`)
- MongoDB: use `motor` for non-blocking queries
- Caching: Zustand on the frontend caches user state (avoids refetches)

**AI cost optimization:**

- Use `gpt-3.5-turbo` for simple explanations
- Use `gpt-4-turbo` only for complex reasoning (teacher chat)
- Cache quiz explanations server-side (same question → same explanation)
- LiteLLM can fall back to cheaper models on token limits
