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

**Last oppdatert:** 2026-09-12 15:15 UTC

### Branch Status

| Branch | Eier | Status | Deadline | Task |
|--------|------|--------|----------|------|
| `feat/exam-ui-clean` | **Codex** | 🔴 Not Started | 2026-09-13 17:00 | Task 1 |
| `feat/admin-media-backend` | **Anti** | 🔴 Not Started | 2026-09-13 17:00 | Task 2 |
| `fix/michael-media-streaming` | **Anti** | 🔴 Blocked | 2026-09-13 17:00 | Task 3 |

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

**Last updated:** 2026-09-12 15:15 UTC  
**Updated by:** @copilot  
**Next review:** After each agent rotation
