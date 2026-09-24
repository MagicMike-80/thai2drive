# 🔄 AGENT HANDOFF PROTOCOL

**ALLE agenter må lese denne filen før arbeid starter.**

---

## 📋 PRE-ROTATION CHECKLIST (Agent som avslutter)

Gjør dette **før du bytter agent**:

```bash
# 1. Sjekk status
git status

# 2. Hvis ucommitted changes:
git add .
git commit -m "wip: [AGENT-NAME] - [1 linje beskrivelse]"
git push origin [branch-name]

# 3. Hvis eksperimentelt/ikke-ferdig:
git stash push -m "stash-[AGENT-NAME]-[dato-YYYYMMDD]"

# 4. Oppdater AGENT_HANDOFF.md nedenfor
```

**REGLER:**
- ❌ **Aldri** overlat ucommitted changes til neste agent
- ❌ **Aldri** merge uten at tests er grønne
- ✅ **Alltid** commit før agent-bytte
- ✅ **Alltid** oppdater AGENT_HANDOFF.md

---

## 📝 POST-ROTATION CHECKLIST (Agent som starter)

Gjør dette **før du skriver første linje kode**:

```bash
# 1. Hent siste versjon
git pull origin main

# 2. Les handoff-notater
cat AGENT_HANDOFF.md

# 3. Les DEADLINE.md for å se deadline
cat DEADLINE.md

# 4. Sjekk hvilken branch du skal jobbe på
git branch -a | grep "feat/\|fix/"

# 5. Checkout riktig branch
git checkout [din-branch]

# 6. Installer dependencies
npm install
# eller
pip install -r requirements.txt

# 7. Kjør tests for å verifisere setup
npm run test
# eller
pytest -v
```

---

## 🎯 NÅVÆRENDE STATE (Live tracking)

**Last oppdatert:** 2026-09-23 (Claude Code)

### Branch Status

| Branch | Eier | Status | Deadline | Task |
|--------|------|--------|----------|------|
| `feat/exam-ui-clean` | **Codex** | ✅ Merged to main (commit `9e34f10`) | 2026-09-13 17:00 | Task 1 |
| `feat/admin-media-backend` | **Anti** | 🔴 Not Started (unverified — not touched this session) | 2026-09-13 17:00 | Task 2 |
| `fix/michael-media-streaming` | **Anti** | 🔴 Blocked (unverified — not touched this session) | 2026-09-13 17:00 | Task 3 |
| `feat/glossary-clean` | **Claude Code** | ✅ Merged to main (commit `0b5e398`) and live in prod | — | Task 4 (Ordre 4 — Fagordkortet + chat widget language fix) |
| `codex/stopplengde-web` | **Codex** | ✅ Merged to main (commit `1fe5688`, `--no-ff`) and live in prod | — | Task 5 (Stopplengde-kalkulator v0.2.0.0) |
| `feat/michael-memory-motivation` | **Claude Code** | ✅ Merged to main (merge commit, in `51df0ce`) — Railway deploy not verified by Claude Code (no Railway access) | — | TASK-017 (student learning memory + motivational coaching) |
| `feat/connect-master-docs` | **Claude Code** | ✅ Merged to main 2026-09-23 — conversation-first Michael, 450-token replies, 10-turn memory + active sign, Thai quiz no-Latin fix. Railway deploy not verified by Claude Code (no Railway access) | — | Michael chat quality |
| `feat/etappe1-lang-exam-identity` | **Claude Code** | 🟡 Pushed to origin, awaiting Codex/Anti merge + Railway verification. 20/20 new unit tests green; full local suite 506 passed / 190 subtests, no regressions (one unrelated pre-existing local Windows temp-dir permission error in `tests/test_range_response.py`, not caused by this branch) | — | Etappe 1 (clean `/web/no`, `/web/th`, `/web/en` entry points; exam mode forces Norwegian question/option text; chat header discloses "Michael AI" per language + new "send message to real Michael" button via `POST /teacher/contact-human`) |

**Merkelig:** Tasks 2 og 3 sin status er ikke verifisert i denne sesjonen — ingen har rapportert fremdrift her, så de står som sist kjent. Ikke anta at hele veikartet er ferdig; kun Task 1, 4 og 5 er bekreftet live i produksjon per 2026-09-16.

**Notat fra Claude Code (2026-09-22):** `feat/etappe1-lang-exam-identity` er **kun pushet**, ikke merget og ikke bekreftet deployet. Claude Code har ingen Railway-tilgang og pusher aldri direkte til `main` (se Stop-regelen i `AGENTS.md`) — merge til main og verifisering av Railway-deploy er Codex/Anti sin del. Diff er begrenset til `backend/webapp.py` og `backend/teacher_chat.py` pluss to nye testfiler; se commit-meldingen på branchen for full beskrivelse.

---

## 📌 TASK 1: EXAM MODE UI

**Status:** 🔴 Not Started  
**Branch:** `feat/exam-ui-clean`  
**Owner:** Codex  
**Deadline:** 2026-09-13 17:00 UTC  
**Prerequisite:** None

### Hva som må implementeres:
```javascript
Frontend (webapp.py):
✓ 90-minutters countdown timer
✓ Load 45 random questions from MongoDB
✓ Display fault counter (max 7)
✓ "Bestått" if >= 38 correct (45 - 7)
✓ "Stryk" if < 38 correct
✓ Submit button saves results to exam_results collection
```

### Test kommando:
```bash
npm run test:exam-ui
```

### Expected pass criteria:
```
✓ Timer counts down from 90:00
✓ Displays exactly 45 questions
✓ Fault counter increments on wrong answer
✓ Button disabled after 8 faults
✓ "PASSED" shown when >= 38 correct
✓ "FAILED" shown when < 38 correct
✓ Results saved to MongoDB
```

### Files to modify:
- `backend/webapp.py` (React component for exam UI)
- `tests/frontend/test_exam_ui.spec.js` (test file)

### Notater for neste agent:
- [Space for handoff notes from Codex]

---

## 📌 TASK 2: MEDIA CRUD BACKEND

**Status:** 🔴 Not Started  
**Branch:** `feat/admin-media-backend`  
**Owner:** Anti  
**Deadline:** 2026-09-13 17:00 UTC  
**Prerequisite:** None (but Task 3 depends on this)

### Hva som må implementeres:
```python
Backend (server.py) - ~158 lines:

1. GET /api/admin/media
   Response: [{ id, name, url, type, uploaded_at }, ...]

2. POST /api/admin/media
   Body: { name, file, type }
   Response: 201 + { id, url }

3. PUT /api/admin/media/:id
   Body: { name, type }
   Response: 200 + updated object

4. DELETE /api/admin/media/:id
   Response: 204 No Content

Frontend (admin.html):
✓ Drag & drop upload form
✓ List of media items
✓ Edit + Delete buttons
✓ Integration with backend endpoints
```

### Test kommando:
```bash
pytest tests/admin/test_media_endpoints.py -v
```

### Expected pass criteria:
```
✓ POST /api/admin/media returns 201 Created
✓ GET /api/admin/media returns 200 OK + list
✓ PUT /api/admin/media/:id returns 200 OK
✓ DELETE /api/admin/media/:id returns 204 No Content
✓ Data persisted to MongoDB media_catalog_manifest
✓ All tests use mock DB (not production)
```

### Files to modify:
- `backend/server.py` (add 4 endpoints around line 342)
- `backend/admin.html` (upload form UI)
- `tests/admin/test_media_endpoints.py` (test file)

### Database schema:
```javascript
// MongoDB collection: media_catalog_manifest
{
  "_id": ObjectId,
  "name": "Rundkjøring demo video",
  "type": "video/mp4",
  "url": "s3://bucket/media/rundkjoering.mp4",
  "uploaded_at": ISODate,
  "uploaded_by": "admin_user_id"
}
```

### Notater for neste agent:
- [Space for handoff notes from Anti]

---

## 📌 TASK 3: MICHAEL MEDIA STREAMING

**Status:** 🔴 Blocked (waiting for Task 2)  
**Branch:** `fix/michael-media-streaming`  
**Owner:** Anti  
**Deadline:** 2026-09-13 17:00 UTC  
**Prerequisite:** Task 2 must be merged first!

### Hva som må implementeres:
```python
Backend (server.py) - ~80 lines:

GET /api/teacher/media/:id
  ✓ Lookup media in media_catalog_manifest
  ✓ Stream correct file (audio/video/image)
  ✓ Set correct Content-Type header
  ✓ Return file stream

Integration with Michael agent:
✓ Michael chat responses include media references
✓ Format: { "type": "video", "id": "...", "url": "..." }
```

### Test kommando:
```bash
pytest tests/integration/test_michael_media.py -v
```

### Expected pass criteria:
```
✓ GET /api/teacher/media/:id returns 200 OK
✓ Correct Content-Type header (audio/video/image)
✓ File streams without 500 error
✓ Michael references media in chat response
✓ Media ID lookup works correctly from MongoDB
✓ Integration test passes
```

### Files to modify:
- `backend/server.py` (add streaming endpoint around line 500)
- `backend/teachers/michael.py` (integrate media into responses)
- `tests/integration/test_michael_media.py` (test file)

### Example response:
```javascript
{
  "text": "Rundkjøring fungerer slik...",
  "media": {
    "type": "video",
    "id": "media_001_rundkjoering",
    "url": "/api/teacher/media/media_001_rundkjoering",
    "caption": "Demonstrasjon av rundkjøring"
  }
}
```

### Notater for neste agent:
- [Space for handoff notes from Anti]

---

## 📌 TASK 4: FAGORDKORTET ("📖 ดูคำศัพท์นอร์เวย์") — ORDRE 4

**Status:** ✅ Merged to `main` (commit `0b5e398`) and pushed to `origin/main` — live in production
**Branch:** `feat/glossary-clean` (branched from `main` @ `9e34f10`)
**Owner:** Claude Code (this session)
**Plan:** [`ordre-4-se-norsk-fagord-implementering.md`](ordre-4-se-norsk-fagord-implementering.md)
**Prerequisite:** None

### Hva som er implementert (per planen §1–§4):
```
✓ backend/scripts/seed_glossary.py — "Prioritert vei" → "Forkjørsvei" rename
  (term_no + example_no; skiltnummer var allerede 206, ikke 220 som planen antok)
  + idempotent db.learning_glossary.update_one(...) migreringssteg i main()
  — koden er IKKE kjørt mot noen database, verken lokal eller prod.
✓ backend/quiz_terms.py (ny modul) — GET /api/quiz/terms?question_id=&lang=
  cache + _match_terms + fail-stop språkfilter + anonym glossary_lookup_logs
✓ server.py — quiz_terms_router registrert (prefix /api) + startup-hook
  load_quiz_glossary_cache() (fail-soft, samme mønster som andre startup-hooks)
✓ backend/webapp.py — «📖 ดูคำศัพท์นอร์เวย์»-knapp + panel i renderQuestion(),
  kun for appLang==='th' og currentTerms.length>0, nullstilt per spørsmål
✓ backend/tests/test_quiz_terms.py (ny, offline, 8 tester — dekker alle 4a-4f
  fra planen + 2 ekstra: ukjent question_id, ukjent lang)
```

### Tillegg — 3 språklekkasjer rettet i Chat Support Widget (backend/website.py)
Ikke del av `ordre-4`-planen, men samme oppdrag/branch. `_CHAT_JS` i
`backend/website.py` (ikke `webapp.py` — oppdraget pekte feil fil) hadde 3
hardkodede norske fallback-strenger uten thai/engelsk motstykke: `data.reply`-
fallback, eskaleringsbekreftelse (`✓ Meldingen din er videresendt...`), og
nettverksfeil-meldingen. Alle tre er nå `{th,no,en}`-objekter lest via samme
`getLang()`-mønster som filens eksisterende `greetings`-objekt. Merk: `lang`
fra `try`-blokken er utenfor scope i `catch` — catch-blokken kaller `getLang()`
på nytt selv.

Ny test: `backend/tests/test_chat_widget_language.py` (offline, 5 tester) —
verifiserer alle tre lang-objekter har `th`/`no`/`en`, at ingen av de gamle
bare-norske fallback-strengene gjenstår, og at catch-blokken har sin egen
`getLang()`-kall.

```bash
cd backend && ../.venv/Scripts/pytest.exe tests/test_chat_widget_language.py -v
```
5 passed, 0 failed.

### Test kommando:
```bash
cd backend && ../.venv/Scripts/pytest.exe tests/test_quiz_terms.py -v
```
8 passed, 0 failed, 0 nettverk, 0 prod.

### ⚠️ IKKE GJORT — krever eksplisitt eiervalg før det skjer:
1. **`seed_glossary.py` er fortsatt IKKE bekreftet kjørt mot prod** (uendret
   siden forrige oppdatering — ingen har rapportert at dette migreringssteget
   er utført). Migreringskoden er skrevet og idempotent, men å faktisk kjøre
   `python scripts/seed_glossary.py` mot produksjons-MongoDB er en bevisst,
   separat handling — se planens §1.3-1.4 for verifiseringsstegene i Atlas.
2. ~~Ingenting er committet.~~ Oppdatert 2026-09-16: koden er nå merget til
   `main` (commit `0b5e398`) og pushet til `origin/main` — live i produksjon.
3. **`GET /api/quiz/terms` er ikke E2E-testet mot en ekte server/DB** — kun
   offline enhetstester av matching/filter-logikken.

### ⚠️ Advarsel til neste agent — samtidig redigering oppdaget
Under implementeringen viste `git diff --stat` at `backend/webapp.py` (531
linjer) og `backend/website.py` (22 linjer, aldri rørt av denne oppgaven) var
endret UTOVER det denne oppgaven gjorde. Dette repoet redigeres tydeligvis av
en annen samtidig prosess/agent akkurat nå — untracked-filer i `git status`
har også endret seg mellom kommandoer i denne økten uten at noen her gjorde
det. **Ikke kjør `git add -A` eller commit uten å lese gjennom hele diffen
først** — den inneholder sannsynligvis en annen agents uferdige arbeid i
tillegg til Task 4 sine 4 filer (`seed_glossary.py`, `quiz_terms.py`
[ny], `server.py`, `webapp.py`, `tests/test_quiz_terms.py` [ny]).

---

## 📌 TASK 5: STOPPLENGDE-KALKULATOR v0.2.0.0 + REVENUECAT PRODUKSJONSHYGIENE

**Status:** ✅ Merged to `main` (commit `1fe5688`, `--no-ff`) and pushed — live in production
**Branches:** `codex/stopplengde-web` (feature) + billing/test work landed directly on `main`
**Owner:** Codex (feature) / Claude Code as Anti (billing hardening, test fixes, deploy)

### Hva som er gjort:
```
✓ Stopplengdevisualisering (Codex, commits 1afecef + 8c2114a):
  egen bred side via /api/web?tool=stopping-distance, hjemknapp under
  teoriprøven, rød/sølvgrå Tesla-visuals, fart/føre/reaksjon/brems/total-
  regnetrinn og 2/3-sekunders følgeavstand. backend/stopping_distance_web.py
  (ny), backend/tests/test_stopping_distance_web.py (ny), assets, docs.
✓ backend/billing.py — fjernet hardkodet RevenueCat sandkasse-testnøkkel
  ("goog_sandbox_testkey_123456"). REVENUECAT_API_KEY leses nå UTELUKKENDE
  fra miljøvariabel; sandkasse-fallback-oppførsel er identisk når nøkkelen
  mangler, bare uten hardkodet streng i kildekoden. (commit fd1683e)
✓ backend/tests/test_billing.py (ny, 7 tester, offline/mocket httpx) —
  dekker env-var-lesing, vellykket/mislykket RevenueCat-respons, dokumentert
  fail-soft-vei ved nettverksfeil, og fravær av hardkodet nøkkel-lekkasje.
✓ backend/tests/test_thai2drive_api.py oppdatert til gjeldende live-skjema
  (commit 5619973): 9 kategorier (ikke 5), question_text_no/th/en →
  question{no,th,en}, correct_answer → correctOptionId.
```

### Live-verifisering (2026-09-16):
```
https://thai2drive.no                          → 200 OK (~0.4s)
https://thai2drive.no/service-worker.js        → 200 OK
https://thai2drive.no/api/web?tool=stopping-distance → 200 OK
pytest backend/tests/ (full suite, på main)    → 143 passed, 0 failed
```

### ⚠️ Ikke glemt, bare ikke gjort her:
- Fail-soft-oppførselen i `billing.py` (gir `premium: true` til ALLE brukere
  hvis RevenueCat-kallet feiler av noen grunn) er dokumentert og bevisst
  design — IKKE endret. Vurder om dette fortsatt er ønsket policy.
- `context/FEATURES.md` skal IKKE committes til git (se regel i CLAUDE.md og
  filens egen header) — oppdater den lokalt i arbeidskatalogen, ikke via git.

---

## 📬 HANDOFF TIL ANTI — 2026-09-23 (Claude Code)

### Status
- `origin/main` = `2160674`. Alt Michael-arbeidet fra i dag ligger der.
- Live på thai2drive.no (`/api/web/version`) viste sist `267d35e7` (skiltkatalog-fiksen). `2160674` var ikke live ennå.
  Deployene har tatt 20–60 minutter i dag, og de kommer i rekkefølge. Sjekk at Railway bygger `2160674`.
- Hvis `/api/web/version` ikke viser `2160674` etter ca. 30 minutter: se byggloggen i Railway.

### Hva som går live med 2160674 (i tillegg til det som allerede er live)
- Varierte hilsener (`backend/michael_greetings.py`): morgen/dag/kveld, tilbake etter over 7 dager, streak, svakt tema. Ingen emojis.
- Fornavn i hilsenen, hentet lesende fra `users`-posten (`full_name` eller `name`). Ingen auth-endring.
- AI-opplysning: første melding til nye elever, statiske velkomsttekster og fast AI-merke i chat-headeren (th/no/en).
- Setninger kuttes ikke lenger (`_concise_teacher_reply`), og vanlige chat-svar er maks 4 hele setninger (7 hvis eleven ber om forklaring).

### Allerede live (a8cd46f og tidligere)
- Tone (streng/varm/tørr), hint-trapp med teller per quiz-spørsmål, samtale-først, 10 meldingers minne med aktivt skilt.
- Vikeplikt-regel: «ikke hindre eller forstyrre», ikke «alltid stoppe».
- Michael-skolen (Thailand mot Norge, Ord for dagen med 40 ord, Blikkrutine), konge/tjener-chip, HAV-lys, hint-knapp.
- Lekket `(podcast: /public_assets/...)`, fet skrift og menyspørsmål fjernes fra vanlige svar.
- Beslutninger fra Michael: bremselengde på is/snø = 3–4 ganger; vognkort «del 1 skal alltid ligge i bilen».

### Røyktest når 2160674 er live
Kjør fra nettleserkonsollen på thai2drive.no (økt-id med prefikset `smoke_`, enhet `smoke-test-claude-0923`):
`POST /api/teacher/chat` med `{"device_id":"smoke-test-claude-0923","session_id":"smoke_x","language":"no","message":"hva er vikeplikt?"}`
Sjekk:
1. «hva er vikeplikt?» (no): 2–4 hele setninger, ikke kuttet.
2. «Jeg gruer meg til oppkjøring» (no): varm tone, maks 4 setninger, ingen `(podcast:` i teksten.
3. «what is give way?» (en): maks 4 setninger, ingen fet skrift, ingen menyspørsmål.
4. «การให้ทางคืออะไร» (th): ikke kuttet med «…», sier «ไม่กีดขวางและไม่รบกวน», ikke «หยุดเสมอ».
5. `GET /api/teacher/welcome?lang=no&device_id=smoke-new-1`: nevner at Michael er en AI-trafikklærer.
6. Åpne chat-fanen: «AI»-merke ved siden av ONLINE.

### Kjent og åpent
- Ord for dagen har 40 av 50 ord (kilden har 34 oppføringer). Utvides senere.
- Videoen «Aktivt blikk» er ikke laget. Venter til røyktesten er 100 % bestått.
- Svarlengden er fortsatt modellstyrt (DeepSeek). Setningstaket er en etterbehandling, ikke en modellendring.
- Første hint-klikk gir hint, andre gir fasit. Selve quiz-flyten med hint er ikke testet mot ekte backend.

### Ting å være obs på i arbeidskopien
- Uncommittede endringer i `backend/tests/test_teacher_chat.py` og `backend/tests/test_teacher_chat_language_isolation.py` er IKKE mine.
  De lemper thai-testene slik at norske fagord i parentes tillates. Avgjør om de skal committes.
- `context/FEATURES.md` er modifisert og skal aldri committes.
- gbrain er oppgradert til 0.53.0.0. En `gbrain serve` fra en annen økt holder PGLite-låsen; denne økten fikk ikke koblet til MCP.
- gstack er oppgradert til 1.88.1.0 (48 redigerte SKILL.md-filer ble flyttet til `~/.gstack/backups/skills/20260923T185534`).
- Røyktestene har lagt samtaler i produksjonsdatabasen under `smoke_`-økter og enheten `smoke-test-claude-0923`. De kan slettes.

### Tester (offline)
`.venv/Scripts/python.exe -m pytest backend/tests/test_michael_greetings.py backend/tests/test_teacher_chat*.py backend/tests/test_michael*.py backend/tests/test_webapp_lang_routes.py tests/test_michael_school_ui_contract.py -q`
Siste kjøring: 250 bestått. De to live-testene `LiveThaiQuizCoachIsolationTests` og `TestWrongQuizAnswerReplyIsThaiOnly` går mot en ekte LLM og kan svinge.

---

## 🚨 BLOCKER RULES

| Regel | Konsekvens |
|-------|-----------|
| Ucommitted changes in branch | ❌ BLOCK – Commit før agent-bytte |
| Tests not green | ❌ BLOCK – Fix før merge |
| Backend + frontend blended | ❌ BLOCK – Split to separate branches |
| AGENT_HANDOFF.md not updated | ❌ BLOCK – Write notes for next agent |
| Merge conflict | ❌ BLOCK – Resolve manually, no force-push |

---

## 📞 COMMUNICATION BETWEEN AGENTS

Hvis du finner problem eller endrer plan:

1. **Update AGENT_HANDOFF.md** with new notes
2. **Commit with descriptive message**
3. **Push to your branch**
4. **Notify next agent** (if rotating)

**Example:**
```bash
git add AGENT_HANDOFF.md
git commit -m "docs: handoff update - mock DB setup complete, tests ready"
git push origin feat/admin-media-backend
```

---

## ✅ DEFINITION OF "DONE"

En task er **FERDIG** når:

1. ✅ All checklist items er marked
2. ✅ Test kommando returnerer all green
3. ✅ Commit er pushet til branch
4. ✅ Zero ucommitted changes
5. ✅ AGENT_HANDOFF.md updated with notes
6. ✅ Ready for merge to main

**Otherwise:** Task er **NOT DONE** og neste agent starter på samme branch.

---

## 🔗 RELATED FILES

- **Deadline & Phase Lock:** `DEADLINE.md`
- **API Specification:** `docs/API.md` (if exists)
- **Architecture:** `docs/ARCHITECTURE.md` (if exists)
- **MongoDB Schema:** `docs/MONGODB_SCHEMA.md` (if exists)
- **Test Fixtures:** `tests/conftest.py`
- **Environment:** `.env.template`

---

**Last updated:** 2026-09-16 12:45 UTC  
**Updated by:** Claude Code (as Anti)  
**Next review:** After each agent rotation
