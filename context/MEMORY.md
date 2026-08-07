<!-- Cap: 2,500 chars. Agent maintains via memory-write instructions. -->
# Working Memory

## Active Threads
- Thai2Drive: Norwegian class B driving theory app/course for Thai speakers in Norway.
- Current priority: stabilize web app first before mobile.
- **Neon glow (Michael, 2026-06-23):** must flow/rotate around the full perimeter of buttons, cards and page edges (not static). Web first; wants status report when live.
- **Language isolation is a critical quality rule** — th/no/en bleed-through in UI and AI teacher cost significant debug time.
- **2026-08-04:** Språkrenhet mobil-dashbord pushet (c9642e7). PR #8 åpen/draft/CI grønn på branch claude/ai-team-revenue-generation-nc97hw, IKKE overvåket. Nye moduler src/constants/i18n.ts + categoryLabels.ts (Fail-Stop, ingen fallbacks).
- Thai TTS fixed: voice th-TH-Chirp3-HD-Achird (th-TH-Standard-C deprecated). Deployed (a9a4804).
- PowerShell profile loads DeepSeek env vars ($env:ANTHROPIC_BASE_URL etc.) automatically.
- AI automation work is a parallel project: Thai2Drive Builder System.
- **Web app appearance is approved — do not change visual design as a side effect of a feature.**
- **2026-07-30:** "Spør Michael" (quiz) DONE + verified locally, NOT committed. Shows after wrong answer; sends hidden `<quiz_context>` to /api/teacher/chat. Files: quiz.tsx, teacher.tsx, appStore.ts.

## Environment Notes
- Live site: thai2drive.no | Backend: Railway + FastAPI | DB: MongoDB Atlas
- Payments: Stripe for web, RevenueCat for mobile
- Backend is source of truth for auth, premium, quota, and subscription status.
- Key endpoints: /api/auth/me, /api/access/status, /api/access/consume, /api/create-checkout-session, /api/stripe/webhook.
- Michael Trafikklærer is the AI teacher. It must answer in the same language as the user message.

## Pending Decisions
- **TTS:** venter på at Michael åpner /api/tts/status. Ubesvart: skal synlig TTS-feilmelding bli egen patch?
- **Urørt (krever ok):** premium-strenger har latinske tegn i thai-modus; freeRemaining() appStore.ts:330 sjekker !== null, ikke undefined.
- Commit "Spør Michael" after Anti's review (~46 unrelated files still staged — untangle first).
- Check OpenAI billing: LiteLLM returns RateLimitError, so Michael may be down in production too.
- Create or update AGENTS.md for Codex compatibility.
- Build a stronger Thai2Drive language system document.
- AI work rules: small patches only, no big rewrites, never touch Stripe/premium/auth unless asked.
