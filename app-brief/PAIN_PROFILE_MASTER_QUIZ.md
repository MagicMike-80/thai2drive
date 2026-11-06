# 🎯 PAIN PROFILE: Import og produksjonssetting av Master Quiz-katalogen (239 spørsmål)

**Status:** VERIFISERT OG KLARGJORT  
**Dato:** 2026-11-06  
**Eier:** Agent 1: Pain Hunter (Fase: Smerteprofilering)  
**Kilde:** Brukerordre / Master Quiz-katalogen med bilder og grønn fasit  

---

## 1. Brukerens Smerte & Bakgrunn

Thai2Drive har 239 ferdig vaskede teorispørsmål med tilhørende bildefiler, 4 svaralternativer og grønn fasit fra Google Sheets. For at elevene skal kunne øve på disse i appen og web-versjonen, må de importeres til produksjonsdatabasen (MongoDB Atlas på Railway) med kanoniske `learning_area_id` og gyldige bildelenker.

### Observert problem / Risikoer:
1. **Lokale filstier fungerer ikke i produksjon:**
   - Regnearket inneholder lokale Windows-stier (`D:\thai2drive-main\...`), som ikke eksisterer i Linux-miljøet på Railway.
   - Bildene må bakes inn som optimaliserte base64 data URIs (`data:image/jpeg;base64,...`) slik at de er 100 % selvstendige og aldri gir 404 på klienten.
2. **Kanoniske læringsområder må håndheves:**
   - Alle 239 spørsmål må kobles til én av de 7 kanoniske `learning_area_id`-ene fra Protokoll Null (`right_of_way`, `lane_positioning`, `interaction`, `speed_distance`, `road_conditions`, `traffic_signs`, `other_topics`).
3. **Idempotens og dataintegritet:**
   - Importskriptet må være idempotent: kjøring flere ganger skal ikke duplisere spørsmål, men oppdatere eksisterende basert på unik nøkkel (`sha256` / `source_file` / `id`).
4. **100 % Språkisolasjon (Protokoll Null):**
   - Strukturen må støtte NO, TH og EN uten språkforurensning eller ulovlige fallbacks.

---

## 2. Akseptansekriterier for Solution Architect (Agent 2)

- [ ] **Kriterium 1:** 239 spørsmål fra `backend/content_packs/thai2drive_master_image_questions.json` har 100 % verifiserte bildefiler på disk.
- [ ] **Kriterium 2:** Hvert bilde bakes trygt som base64 data URI eller stabil URL for å unngå brutte stier i skyen.
- [ ] **Kriterium 3:** Hvert spørsmål tildeles gyldig `learning_area_id` i henhold til `backend/learning_areas.json`.
- [ ] **Kriterium 4:** Importskriptet `backend/scripts/import_master_quiz_catalog.py` støtter både lokal validering/dry-run og `--apply` mot `MONGO_URL`.
- [ ] **Kriterium 5:** Live API-verifisering og handoff til Argus iht. `VERIFY.md`.

---

## 3. Handoff til Agent 2 (Solution Architect)
Smerteprofil og krav er 100 % isolert. Overleveres til **Agent 2: Solution Architect**.
