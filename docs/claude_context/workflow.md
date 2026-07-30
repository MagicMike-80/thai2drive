# Workflow, Ownership & Product Rules

> Load this when: you are unsure who owns a task, before starting a new feature, or when handling memory/context files.
> Index: [`../../CLAUDE.md`](../../CLAUDE.md)
>
> This file is the elaboration of the hardcoded safety rules in `CLAUDE.md`. The one-liners there always apply — this file explains them.

## Thai2Drive Collaboration Lock

Deep/Claude and Anti must not work on the same responsibility at the same time.

### Ownership

- **Deep/Claude** (terminal-assistenten) owns content, pedagogy, traffic theory explanations, Thai/Norwegian/English wording, Michael Trafikklærer tone/personality, question wording, common mistakes, exam tips, video scripts, lesson structure, and learning goals.
- **Anti** (hovedassistenten) owns code implementation, backend/API, database scripts, validation/import systems, web/mobile changes, tests, Git/GitHub/Railway, deployment, logging, monitoring, and production safety.

### Stop Rule

If a task belongs to Anti, stop and say:

> "This task belongs to Anti. I should not do this part."

If ownership is unclear, ask whether it is an Anti implementation task or a Deep/Claude content task before changing files.

---

## Product Rules

- Web first. Mobile follows only after web approval.
- Do not write production database data unless explicitly requested.
- Do not touch Stripe, auth, premium, quota, MongoDB production data, or mobile/Android unless explicitly requested.
- Thai mode must be 100% Thai, Norwegian mode 100% Norwegian, and English mode 100% English.
- Michael should feel like a calm real driving instructor, not a generic chatbot or visible AI system.

---

## Karpathy Coding Principles

- **Tenk før du koder:** Still oppklarende spørsmål hvis oppgaven er uklar; gjør aldri antakelser i stillhet.
- **Enkelhet først:** Bygg den enkleste mulige løsningen; unngå over-engineering og spekulative abstraksjoner.
- **Kirurgiske endringer:** Gjør kun presise endringer som er direkte nødvendige for oppgaven; ikke refaktorer eller endre urelatert kode.
- **Ikke fiks det som fungerer:** La fungerende kode være i fred hvis det ikke er en del av den forespurte oppgaven.

---

## Context & Memory System

The `context/` directory holds the Claude Code memory system:

- **`context/MEMORY.md`** — curated working scratchpad (2,500 char cap)
- **`context/USER.md`** — user profile (1,375 char cap)
- **`context/FEATURES.md`** — permanent wishlist for features Michael wants
- **`context/MASTER_BLUEPRINT.md`** — approved product vision
- **`context/memory/`** — daily session logs (`YYYY-MM-DD.md`)
- **`context/transcripts/`** — captured session transcripts

Read `context/MEMORY.md` and `context/USER.md` at session start. Mid-session writes persist to disk but take effect next session.

### Master Blueprint

`context/MASTER_BLUEPRINT.md` is the approved product vision for Thai2Drive. Read it when starting work on any new feature. It defines architecture, pedagogy, business model, and ownership rules.

### Feature Wishlist — Automatic Rule

`context/FEATURES.md` is the permanent wishlist for everything Michael wants.

- When Michael mentions any wish, idea, or feature request: add it to `context/FEATURES.md` immediately in the same response — do not wait.
- When a feature ships to Railway: move it to ✅ LEVERT in `context/FEATURES.md`.
- Never store secrets in `context/FEATURES.md`. Never commit it to git.
- All UI features: web app first, mobile only after Michael's explicit approval.

---

## Claude Code Configuration

This repository has two `.claude/settings*.json` files:

- **`.claude/settings.json`** — project-level hooks (transcript capture on every Stop). Committed to git.
- **`.claude/settings.local.json`** — local overrides (DeepSeek endpoint, API key, permissions). **Do not delete, overwrite, or commit.** Contains the API key.

The active hook runs `node .claude/hooks/transcript-capture.js` on every Stop event to record session transcripts.
