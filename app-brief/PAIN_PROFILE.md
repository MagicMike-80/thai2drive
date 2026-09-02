# 🎯 PAIN PROFILE: Oppdrag 5 — «Thailand vs Norge» Mikroleksjoner

**Status:** VERIFISERT OG BEVIST  
**Dato:** 2026-09-02  
**Eier:** Agent 1: Pain Hunter (Fase: Blueprint)  
**Kilde:** `app-brief/thai2drive-resten-av-fremtidslisten-ferdig-idag.md`

---

## 1. Brukerens Smerte & Bakgrunn

Thailandske elever som skal ta førerkort i Norge opplever ofte en dyp kognitiv konflikt mellom tillært trafikkultur fra hjemlandet (venstrekjøring, uformell presedens der større biler ofte har forkjørsrett i praksis, og fotgjengere som må vike for motorkjøretøy) og det norske trafikkbildet (høyreregel § 7, absolutt vikeplikt for fotgjengere i gangfelt, HAV-regel § 3).

### Forventet oppførsel:
- Systemet skal tilby strukturerte, pedagogiske mikroleksjoner som setter de to kjørekulturene opp mot hverandre med klare metaforer og råd fra lærer Michael.
- Tilgjengelig via et dedikert API-endepunkt `/api/lessons/culture` på både norsk, thai og engelsk.

---

## 2. Akseptansekriterier for Solution Architect (Agent 2)

- [ ] **Kriterium 1:** Opprette `backend/micro_lessons.py` med et `APIRouter`-endepunkt `GET /api/lessons/culture`.
- [ ] **Kriterium 2:** Hver mikroleksjon skal inneholde ID, tittel, innhold (NO, TH, EN), samt Michaels pedagogiske huskeregel/metafor (f.eks. «Kongen og tjeneren» / «Fotgjengeren er kongen»).
- [ ] **Kriterium 3:** Rutene må inkluderes i `backend/server.py` (`app.include_router` og `api_router.include_router`).
- [ ] **Kriterium 4:** 100 % språkisolasjon og konsekvent bruk av **ครับ (khrap)** og **ผม (phom)** på thai.

---

## 3. Handoff til Agent 2 (Solution Architect)
Smerteprofil og krav er klare. Overleveres til **Agent 2: Solution Architect**.
