# 📐 SOLUTION BLUEPRINT: Fullført Masterplan & Akutt Service-Worker / Audio Fix

**Status:** FULLFØRT AV AGENT 2 & 3  
**Dato:** 2026-09-02  

---

## 1. Mål & Løsningsoversikt

1. **Service Worker Range & API Bypass:**
   - I `backend/service-worker.js` avbrytes fetch umiddelbart (`return;`) for alle forespørsler som starter med eller inneholder `/api/`, alle requests med `range`-header, samt alle lyd- og videofiler (`.mp3`, `.m4a`, `.mp4`, osv.).
   - Sikrer at iOS Safari 206 Partial Content Range streaming fungerer feilfritt og at podcaster og TTS-lyd aldri fryser på 0:00/0:00.

2. **Michael Pedagogikk & Lovforankring (§ 7 nr. 2 Venstresving):**
   - Låst i `_SECTION_7_2_PROMPT`, `_PROMPT_CORE` og `_apply_section_7_2_fail_safe` i `backend/teacher_chat.py`.
   - Pedagogisk forklaring med «Kongen og tjeneren» for venstresving og møtende trafikk.
   - Forbud mot feilaktig AI-påstand om at høyreregelen ikke gjelder for møtende trafikk.

3. **Karusell & WebApp Glatthet:**
   - `#bottomNav` har `scroll-snap-type: none` for å eliminere subpixel mikrovibrasjon på iOS Safari.
   - Fjerning av sabotør-lyttere (`_SILENT_WAV` async pause) i `backend/webapp.py`.

4. **Nye Moduler:**
   - `backend/micro_lessons.py` (`/api/lessons/culture`)
   - `backend/readiness.py` (`/api/user/readiness`)
   - `backend/billing.py` (`/api/billing/subscription`)
   - `backend/service-worker.js` (`/service-worker.js`)
