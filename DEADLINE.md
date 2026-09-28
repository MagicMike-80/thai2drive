# ⏰ DEADLINE & PHASE LOCK

**CRITICAL: Ingenting annet diskuteres før disse 3 oppgavene er GRØNNE og MERGED.**

---

## 🔒 PHASE 1 - LOCK DOWN (Sept 12-13, 2026)

**Formål:** Fikse de 3 blokkerne som har stoppet produksjon i 1 måned.

**Status:** 🔴 NOT STARTED  
**Team:** Codex + Anti  
**Deadline:** **2026-09-13 17:00 UTC** (36 timer fra nå)

| # | Task | Owner | Deadline | Status |
|---|------|-------|----------|--------|
| 1️⃣ | Exam Mode UI (90 min, 7 faults, Bestått/Stryk) | **Codex** | 2026-09-13 17:00 | 🔴 Not Started |
| 2️⃣ | Media CRUD Backend (`/api/admin/media`) | **Anti** | 2026-09-13 17:00 | 🔴 Not Started |
| 3️⃣ | Michael Media Streaming (`/api/teacher/media/:id`) | **Anti** | 2026-09-13 17:00 | 🔴 Not Started |

---

## 📌 TASK 1: EXAM MODE UI (Codex)

**Branch:** `feat/exam-ui-clean`  
**Deadline:** 2026-09-13 17:00 UTC

### Hva skal kodes:
```javascript
// webapp.py (frontend)
1. 90-minutters nedteller (React component)
2. Loader 45 spørsmål fra MongoDB
3. Counter for "Maks 7 feil"
4. "Bestått" hvis >= 38 riktig (45 - 7)
5. "Stryk" hvis < 38 riktig
6. Submit-knapp som lagrer resultat
```

### Test må være grønn:
```bash
npm run test:exam-ui
```

### Pass-kriterier:
- ✅ Timer teller ned fra 90:00 til 00:00
- ✅ 45 spørsmål vises (ikke 44, ikke 46)
- ✅ Fault counter vises og øker ved feil
- ✅ Ved 8 faults: knappen blir disabled
- ✅ "Bestått" vises når >= 38 riktige
- ✅ "Stryk" vises når < 38 riktige
- ✅ Resultat lagres til MongoDB `exam_results`

### Commit & Push:
```bash
git checkout -b feat/exam-ui-clean
# ... koding ...
npm run test:exam-ui  # Må være grønn
git add .
git commit -m "feat: exam mode UI - 45 questions, 90 min timer, 7 fault limit"
git push origin feat/exam-ui-clean
```

### Handoff til Anti:
```bash
# Før du bytter agent:
git update-ref refs/heads/feat/exam-ui-clean  # Sikrer branch er pushet
# Oppdater AGENT_HANDOFF.md
```

---

## 📌 TASK 2: MEDIA CRUD BACKEND (Anti - Phase 1)

**Branch:** `feat/admin-media-backend`  
**Deadline:** 2026-09-13 17:00 UTC

### Hva skal kodes (server.py):
```python
# 4 endpoints, totalt ~158 linjer

1. GET /api/admin/media
   - List alle media fra MongoDB
   - Response: [{ id, name, url, type, uploaded_at }, ...]

2. POST /api/admin/media
   - Upload ny fil
   - Body: { name, file, type }
   - Response: 201 + { id, url }

3. PUT /api/admin/media/:id
   - Update media metadata
   - Body: { name, type }
   - Response: 200 + updated object

4. DELETE /api/admin/media/:id
   - Slett media
   - Response: 204 No Content
```

### admin.html (frontend for admin):
```html
- Upload-form med drag & drop
- Liste over media
- Edit + Delete buttons
- Knytting til backend-endpoints
```

### Test må være grønn:
```bash
pytest tests/admin/test_media_endpoints.py -v
```

### Pass-kriterier:
- ✅ `POST /api/admin/media` returnerer 201 OK
- ✅ `GET /api/admin/media` returnerer 200 + liste
- ✅ `PUT /api/admin/media/:id` returnerer 200 OK
- ✅ `DELETE /api/admin/media/:id` returnerer 204
- ✅ Alle data lagres i MongoDB `media_catalog_manifest`
- ✅ Mock-DB brukt i tests (ikke produksjon)

### Commit & Push:
```bash
git checkout -b feat/admin-media-backend
# ... koding ...
pytest tests/admin/test_media_endpoints.py -v  # Må være grønn
git add .
git commit -m "feat: media admin CRUD endpoints - GET/POST/PUT/DELETE /api/admin/media"
git push origin feat/admin-media-backend
```

---

## 📌 TASK 3: MICHAEL MEDIA STREAMING (Anti - Phase 1)

**Branch:** `fix/michael-media-streaming`  
**Deadline:** 2026-09-13 17:00 UTC

**Prerequisite:** Task 2 må være merged først!

### Hva skal kodes (server.py):
```python
# 1 integration endpoint, ~80 linjer

GET /api/teacher/media/:id
  - Michael slår opp media i `media_catalog_manifest`
  - Returnerer riktig fil (audio/video/image)
  - Headers: Content-Type, Content-Length
  - Body: File stream
  
Eksempel:
  GET /api/teacher/media/media_001_rundkjoering_video
  Response: video/mp4 stream fra MongoDB eller S3
```

### Integration med Michael-agent:
```python
# I Michael chat-response:
# Hvis brukeren spør om rundkjøring:
michael_response = {
  "text": "Rundkjøring fungerer slik...",
  "media": {
    "type": "video",
    "id": "media_001_rundkjoering_video",
    "url": "/api/teacher/media/media_001_rundkjoering_video",
    "caption": "Demonstrasjon av rundkjøring"
  }
}
```

### Test må være grønn:
```bash
pytest tests/integration/test_michael_media.py -v
```

### Pass-kriterier:
- ✅ `GET /api/teacher/media/:id` returnerer 200 OK
- ✅ Riktig Content-Type header (audio/video/image)
- ✅ Fil streames uten 500-feil
- ✅ Michael kan referere til media i chat-svar
- ✅ Media-ID slåes opp fra MongoDB riktig
- ✅ Integrationstest kjører grønt

### Commit & Push:
```bash
git checkout -b fix/michael-media-streaming
# ... koding ...
pytest tests/integration/test_michael_media.py -v  # Må være grønn
git add .
git commit -m "fix: michael media lookup and streaming - GET /api/teacher/media/:id"
git push origin fix/michael-media-streaming
```

---

## 🚀 MERGE SEQUENCE

**Når alt er grønt, merge i denne rekkefølgen:**

```bash
# 1. Merge Task 1 (Exam UI - ingen dependencies)
git checkout main
git pull origin main
git merge --no-ff feat/exam-ui-clean -m "merge: exam mode UI complete"
git push origin main

# 2. Merge Task 2 (Media Backend)
git merge --no-ff feat/admin-media-backend -m "merge: media admin CRUD endpoints"
git push origin main

# 3. Merge Task 3 (Michael Integration)
git merge --no-ff fix/michael-media-streaming -m "merge: michael media streaming integration"
git push origin main
```

**Efter alle 3 er merged:**
```bash
git tag -a v1.1.0-exam-media-fix -m "Exam mode + Michael media streaming"
git push origin v1.1.0-exam-media-fix
# Deploy til Railway
```

---

## ⛔ FREEZE RULES (INGENTING ANNET)

**Fra nå til 2026-09-13 17:00 UTC:**

| Forbudt | Grunn | Konsekvens |
|---------|-------|-----------|
| Diskutere NotebookLM-agenten | Fase 2, ikke nå | Agent blir pausert |
| Åpne nye branches | Fokus må være her | Branch blir deleted |
| Merge til `main` | Bare disse 3 tasks | Force-reject |
| Snakke om optimisering | Det er senere | Ignored |
| Eksperimentere med AI-modeller | Ikke nå | Ikke relevant |
| Lage nye features | Blokkert | Krever approval etter Sept 13 |

**Eneste som diskuteres:**
- ✅ Feilsøking på disse 3 tasks
- ✅ Test-problemer
- ✅ Merge-konflikter
- ✅ Statusoppdateringer i AGENT_HANDOFF.md

---

## 📊 LIVE STATUS BOARD

### Task 1: Exam Mode UI
```
Owner: Codex
Branch: feat/exam-ui-clean
Status: 🔴 PENDING
Progress: ▯▯▯▯▯▯▯▯▯▯ 0%
Tests: ⏳ Not started
Deadline: 2026-09-13 17:00
```

### Task 2: Media CRUD Backend
```
Owner: Anti
Branch: feat/admin-media-backend
Status: 🔴 PENDING
Progress: ▯▯▯▯▯▯▯▯▯▯ 0%
Tests: ⏳ Not started
Deadline: 2026-09-13 17:00
```

### Task 3: Michael Media Streaming
```
Owner: Anti
Branch: fix/michael-media-streaming
Status: 🔴 BLOCKED (waiting for Task 2)
Progress: ▯▯▯▯▯▯▯▯▯▯ 0%
Tests: ⏳ Not started
Deadline: 2026-09-13 17:00
```

---

## 🎯 SUCCESS CRITERIA

Phase 1 er **FERDIG** når:

1. ✅ `feat/exam-ui-clean` er merged til `main`
2. ✅ `feat/admin-media-backend` er merged til `main`
3. ✅ `fix/michael-media-streaming` er merged til `main`
4. ✅ Alle 3 tasks har grønne tests
5. ✅ Ingen ucommitted changes
6. ✅ Deploy til Railway er vellykket
7. ✅ Michael viser media (bilde/lyd/video) sømløst

**Når dette er gjort:** FASE 2 (NotebookLM-agenten) kan starte.

---

**Sist oppdatert:** 2026-09-12 15:15 UTC  
**Oppdatert av:** @copilot  
**Next Review:** 2026-09-13 09:00 UTC
