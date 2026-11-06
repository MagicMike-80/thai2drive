# 📐 SOLUTION BLUEPRINT: Import og produksjonssetting av Master Quiz-katalogen

**Status:** GODKJENT FOR IMPLEMENTASJON  
**Dato:** 2026-11-06  
**Eier:** Agent 2: Solution Architect  
**Referanse:** `app-brief/PAIN_PROFILE_MASTER_QUIZ.md` & Protokoll Null  

---

## 1. Teknisk Arkitektur & Datamodell

Importen tar utgangspunkt i `backend/content_packs/thai2drive_master_image_questions.json` (239 spørsmål) og transformerer hver post til MongoDB Atlas sitt produksjonsskjema for samlingen `questions`.

### Dataskjema for hvert spørsmål:
```json
{
  "id": "uuid-v4 (eller deterministisk hash basert på sha256)",
  "category": "Kanonisk kategori (f.eks. Right of Way, Road Rules, etc.)",
  "learning_area_id": "right_of_way | lane_positioning | interaction | speed_distance | road_conditions | traffic_signs | other_topics",
  "difficulty": "medium",
  "question": {
    "no": "Vasket norsk spørsmålstekst",
    "th": "Thai oversettelse / nøytral sikker fallback",
    "en": "Engelsk oversettelse"
  },
  "options": [
    { "id": "A", "text": { "no": "...", "th": "...", "en": "..." } },
    { "id": "B", "text": { "no": "...", "th": "...", "en": "..." } },
    { "id": "C", "text": { "no": "...", "th": "...", "en": "..." } },
    { "id": "D", "text": { "no": "...", "th": "...", "en": "..." } }
  ],
  "correctOptionId": "A | B | C | D",
  "explanation": {
    "no": "Pedagogisk forklaring fra Michael",
    "th": "Thai forklaring",
    "en": "Engelsk forklaring"
  },
  "bildeUrl": "data:image/jpeg;base64,... (bakt inn fra lokal fil)",
  "active": true,
  "schema_version": 2,
  "source": "master_quiz_catalog",
  "source_file": "1.jpg (opprinnelig bildefil)",
  "sha256": "kontrollsum for originalbilde",
  "validated": true,
  "created_at": "ISO-8601 tidsstempel"
}
```

---

## 2. Bildebaking og Portabilitet
* For alle 239 spørsmål leses bildefilen (fra enten `resources/cellImage_*.jpg` eller original disksti).
* Bildet komprimeres lett og kodes til base64 data URI (`data:image/jpeg;base64,...`).
* Dette eliminerer enhver avhengighet til lokale Windows-stier på Railway.

---

## 3. Idempotens & Sikkerhet
* Importskriptet matcher eksisterende dokumenter på `sha256` eller `source_file`.
* Hvis dokumentet finnes: oppdaterer feltene via `$set` (oppdaterer fasit, spørsmålstekst, bilde og `learning_area_id`).
* Hvis dokumentet ikke finnes: setter inn som nytt dokument.
* Skriptet kjører som **dry-run som standard**, og krever flagget `--apply` for å skrive til produksjonsdatabasen.

---

## 4. Handoff til Agent 3 (Code Builder / Codex)
Planen er klar for koding i `backend/scripts/import_master_quiz_catalog.py`. Overleveres til **Agent 3: Code Builder**.
