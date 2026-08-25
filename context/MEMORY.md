<!-- Cap: 2,500 chars. Agent maintains via memory-write instructions. -->
# Working Memory

## Active Threads
- **⚠️ AI-TEAMET LIGGER KUN PÅ GRENEN `claude/ai-team-revenue-generation-nc97hw`, IKKE PÅ MAIN.** Starter en økt fra main finnes verken `.claude/agents/` (4 agenter) eller `/revenue-team`. Merges PR #8, blir teamet permanent for alle økter.
- Thai2Drive: teoriprøve klasse B på thai, for thaitalende i Norge.
- Webapp før mobil. **Utseendet er godkjent — ikke endre design som bieffekt.**
- **Språkisolasjon er kritisk** — th/no/en-lekkasje har kostet mye debug.
- **PR #8 (åpen, draft, CI grønn, 16 dager):** dashbord-språkrenhet, dynamisk paywall, Revenue Team, kampanje, stemmetester, kontrastfiks. Intet av det er ute hos elevene.
- **Kampanje ferdig i kode (8c1ccaf):** `promo_config.py`, `FREE_PROMO_MODE=True`, 30 dager full tilgang til innloggede, gjester beholder registreringsvegg. Av-bryter virker uten deploy. `/api/unsubscribe` HMAC-signert.
- **TTS:** alle tre språk går til Michaels klonede ElevenLabs-stemme «Michael 1» (`eulvRsWu7NGAUD1FzMVP`, `eleven_v3`). Stemmetester: `/api/web/voice-tester`.
- **2026-07-30:** "Spør Michael" (quiz) ferdig lokalt, IKKE committet: quiz.tsx, teacher.tsx, appStore.ts.

## Environment Notes
- thai2drive.no | Railway + FastAPI | MongoDB Atlas | Stripe (web) + RevenueCat (mobil)
- Backend er fasit for auth, premium, kvote, abonnement.
- Endepunkter: /api/auth/me, /access/status, /access/consume, /create-checkout-session, /stripe/webhook, /tts/status, /unsubscribe
- Michael Trafikklærer svarer alltid på samme språk som eleven skriver.
- **thai2drive.no og vegvesen.no er blokkert av nettverksproxyen i Claude-økter.** Michael må åpne dem selv.

## Pending Decisions
- **⚠️ METAFORKONFLIKT:** AI-læreren bruker vert/gjest (`เจ้าของบ้าน/แขก`, teacher_chat.py:523) på thai, TikTok-manuset bruker konge/tjener. Michael må velge én.
- **Michael, ~1 time:** åpne stemmetesteren; fem elevtelefoner (løfter agent 1 fra 3,7); lese e-postene høyt på thai; sjekke 2026-gebyret på vegvesen.no.
- Urørt (krever ok): premium-strenger har latinske tegn i thai-modus; `freeRemaining()` appStore.ts:330 sjekker `!== null`.
- Commit "Spør Michael" etter Antis review. AGENTS.md for Codex.
