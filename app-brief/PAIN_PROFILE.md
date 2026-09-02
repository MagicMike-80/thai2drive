# 🎯 PAIN PROFILE: Akutt Android/Chrome PWA Service Worker Caching

**Status:** VERIFISERT OG BEVIST  
**Dato:** 2026-09-02  
**Eier:** Agent 1: Pain Hunter (Fase: Smerteprofilering)  
**Kilde:** Brukervarsel / Sjefens Samsung Android Chrome PWA Caching

---

## 1. Brukerens Smerte & Bakgrunn

Brukere på Android/Chrome (spesielt Samsung-enheter) opplever at den aggressive PWA-cachingen holder på gammel, utdatert kode i nettleseren. Selv etter nye deploys til Railway fortsetter telefonen å kjøre den gamle Service Workeren fordi nettleseren venter på at alle faner lukkes før en ny Service Worker aktiveres.

### Observert problem i koden:
1. `backend/service-worker.js`:
   - `self.skipWaiting()` ble kalt først etter at promise-kjeden for caching var ferdig, i stedet for å tvinge umiddelbar overgang ut av ventemodus i `install`-lytteren.
2. `backend/webapp.py`:
   - Registreringen av Service Worker manglet lyttere for `updatefound` og `statechange === 'activated'`, samt manglet `controllerchange`-håndtering.
   - Det var ingen automatisk `window.location.reload()` når en ny Service Worker overtok kontrollen.

### Forventet oppførsel:
1. Ny Service Worker kaller `self.skipWaiting()` umiddelbart ved installasjon og `clients.claim()` ved aktivering.
2. Frontend oppdager ny Service Worker, lytter på aktivering og gjør en trygg, kontrollert `window.location.reload()` én gang for å hente den nyeste koden direkte til enheten.
3. Eksisterende Safari/iOS audio bypass og /api/ bypass forblir 100 % intakt.

---

## 2. Verifiserte observasjoner

- **Fil 1:** `backend/service-worker.js` (linje 18-40) – mangler eksplisitt umiddelbar `self.skipWaiting()` og versjonsbump for cache-invalidering.
- **Fil 2:** `backend/webapp.py` (linje 11311-11320) – Service Worker registreres passivt uten `updatefound` eller auto-reload ved oppdatering.

---

## 3. Akseptansekriterier for Solution Architect (Agent 2)

- [ ] **Kriterium 1:** `self.skipWaiting()` kalles umiddelbart i `install` i `backend/service-worker.js`.
- [ ] **Kriterium 2:** `event.waitUntil(clients.claim())` og cache-cleanup kjøres i `activate`.
- [ ] **Kriterium 3:** Bump cache-navn (f.eks. til `v1.0.2`) for å invalidere gammel cache på enheter.
- [ ] **Kriterium 4:** `backend/webapp.py` lytter på `updatefound` og `controllerchange` og gjør en trygg reload uten uendelig løkke.
- [ ] **Kriterium 5:** Alle API-kall (`/api/`) og mediestrømmer (Range, audio/video) forblir uendret og slipper forbi SW.

---

## 4. Handoff til Agent 2 (Solution Architect)
Smerteprofil og rotårsak er 100 % bevist og isolert. Overleveres til **Agent 2: Solution Architect**.
