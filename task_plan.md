# Task Plan: Michael AI (Thai2Drive) — BLAST Framework

Dette dokumentet definerer fremdriftsplanen for arkitektur, bygging og testing av **Michael AI** i henhold til BLAST-rammeverket, Protokoll Null og Bildekatalog-oppdragsbeskjeden.

---

## 🚀 BLAST-Faser & Fremdriftsstatus

### 📐 Fase 1: Blueprint (Kartlegging & Grunnlag)
- [x] **1.1** Opprette og oppdatere prosjektets Grunnlov i `AGENTS.md` (North Star, Source of Truth, STOPP Å GJETTE, DATA FIRST).
- [x] **1.2** Skanning og kartlegging av eksisterende Thai2Drive-kode, databaser, skiltarkiv og API-endepunkter (`findings.md`).
- [x] **1.3** Kartlegge lov-mapping (Vegtrafikkloven § 3 og Trafikkreglene § 7 nr. 2/4) og bildekatalog-krav.
- [x] **1.4** Presentere arkitektur- og implementasjonsplan (`implementation_plan.md`) for godkjenning i chatten.

### 🔗 Fase 2: Link (gstack & Verktøysintegrasjon & Bildekatalog)
- [x] **2.1** Kloning av gstack fra `https://github.com/garrytan/gstack.git` inn i `tools/gstack`.
- [x] **2.2** Opprette `backend/media_catalog.py` og `backend/media_catalog_manifest.json` med toveis språkuavhengig `LAW_MAPPING` og `#hashtags`.
- [x] **2.3** Verifisere at test-suiten kjører 100 % lokalt isolert med mocks for eksterne API-kall (ElevenLabs, Stripe, MongoDB, LLM).

### 🏛️ Fase 3: Architect (Unified Engine & Lov-mapping)
- [x] **3.1** Juridisk sikring i `backend/teacher_chat.py`:
  - Etablere eksplisitt regel for Trafikkreglene § 7 nr. 2: vikeplikt ved venstresving for møtende trafikk er hjemlet i høyreregel-komplekset. Michael skal aldri avvise dette.
  - Skilt-støyfilter: Kun 100 % relevante skilt (f.eks. `202_0` og `204_0`) slippes gjennom til `sign_ids` og `media`.
  - Integrere `media_catalog` direkte i RAG-kontekst for relevante situasjonsbilder.
- [x] **3.2** Opprette `backend/admin_analytics.py`:
  - Anonymisert svakhets-sporing basert på feil per emne-tag (`#7_2`, `#rundkjoring`, `#3_hav`).
  - Anonymisert konverteringsanalyse fra gratis/gjest til Premium.
  - Knytte endepunktene inn i `backend/server.py`.
- [x] **3.3** 100 % Språkisolasjon & Fail-Safe:
  - Sikre at alle svar og metadata er 100 % rene på valgt språk (Thai, Norsk, Engelsk).

### 🎨 Fase 4: Style (ChatGPT-style Brukeropplevelse & Lightbox)
- [x] **4.1** Frontend-rendering i `backend/webapp.py`:
  - Rendre situasjonsbilder og skilt fra `media`/`sign_ids` som kompakte 80px × 80px elementer i chat-boblen.
  - Legge til klikk-forstørrelse (Lightbox-modal) for mobil og desktop.
  - Lydstabilitet: 12 sekunders timeout og `currentTime = 0`-spoling for repeterte ElevenLabs-avspillinger.
- [x] **4.2** Minimalistisk samtalesentrert grensesnitt:
  - Ergonomisk skrivefelt nederst med hurtigvalg-chips og klargjøring for bildeflyt.

### 🎯 Fase 5: Trigger & QA (Kvalitetssikring & Definition of Done)
- [x] **5.1** Kjøre den lokalt isolerte testsuiten i `tests/test_michael_unified.py` og bekrefte at alle 8/8 tester passerer.
- [x] **5.2** Verifisere eksisterende kontrakter (Phase 3 freemium, mobil-UI, og bilde-lesbarhet).
- [ ] **5.3** Generere Leveranserapport og oppdatere `findings.md`.
