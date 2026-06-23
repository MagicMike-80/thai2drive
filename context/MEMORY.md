<!-- Cap: 2,500 chars. Agent maintains via memory-write instructions. -->
# Working Memory

## Active Threads
- Thai2Drive is being developed as a professional Norwegian class B driving theory app/course for Thai speakers in Norway.
- Current priority: stabilize web app first before mobile.
- Design Guideline: Neon border glow must flow/rotate dynamically around the entire perimeter/boundary of all buttons, cards, and page edges in the app (not static or fixed in one place).
- **User Instruction (2026-06-23):** Michael wants the global dynamic neon border glow styling (web first) implemented quickly. He wants a status report on when it is completed and ready for all students to use.
- Recent issue: Thai/Norwegian/English language bleed-through in UI and AI teacher took significant time to debug. Language isolation is now a critical quality rule.
- Thai TTS has been fixed: Changed the Google Cloud TTS voice to th-TH-Chirp3-HD-Achird (male generative voice) because th-TH-Standard-C was deprecated. Tested and deployed to Railway (commit a9a4804).
- PowerShell Profile created: Configured environment variables ($env:ANTHROPIC_BASE_URL, etc.) in the user's PowerShell profile to load DeepSeek configuration automatically on terminal startup.
- AI automation/project-structure work is now a parallel project: Thai2Drive Builder System.

## Environment Notes
- Live site: thai2drive.no
- Backend: Railway + FastAPI
- Database: MongoDB Atlas
- Payments: Stripe for web, RevenueCat for mobile
- Backend is source of truth for auth, premium, quota, and subscription status.
- Important endpoints include /api/auth/me, /api/access/status, /api/access/consume, /api/create-checkout-session, /api/stripe/webhook.
- Michael Trafikklærer is the AI teacher. It must answer in the same language as the user message.

## Pending Decisions
- Create or update AGENTS.md for Codex compatibility.
- Build a stronger Thai2Drive language system document.
- Add clear AI work rules: small patches only, no big rewrites, do not touch Stripe/premium/auth unless explicitly requested.
