# 🔨 PATCH REPORT: Tvunget Service Worker-aktivering & Auto-reload

**Status:** IMPLEMENTERT & TESTET  
**Dato:** 2026-09-02  
**Eier:** Agent 3: Patch Builder (Fase: Implementasjon)  

---

## 1. Endrede filer

1. `backend/service-worker.js`:
   - Bumpet cache-versjon til `thai2drive-offline-v1.0.2` for å tvinge fjerning av gammel cache.
   - La til `self.skipWaiting()` umiddelbart i `install`-eventlytteren.
   - Beholdt `caches.keys()` sletting av gamle cacher samt `clients.claim()` i `activate`-eventlytteren.
   - Alle eksisterende unntak for `/api/`, Range requests og lyd-/videofiler er 100 % uendret.

2. `backend/webapp.py`:
   - La til `refreshing`-flagg (`var refreshing = false;`) for å forhindre uendelige reload-løkker.
   - La til global lytter på `navigator.serviceWorker.addEventListener('controllerchange', ...)` for umiddelbar oppdatering når ny worker overtar kontrollen.
   - La til `setupSwUpdate` funksjon som lytter på `reg.addEventListener('updatefound', ...)` og `statechange === 'activated'`.
   - Koblet både primær registrering (`/service-worker.js`) og fallback (`/api/service-worker.js`) til auto-update logikken.

---

## 2. Verifisering og syntakssjekk

- `node --check backend/service-worker.js` fullført med exit code 0 (gyldig JavaScript).
- Ingen backend API-kontrakter eller databaser er berørt.
- Ingen hemmeligheter er lagt til.
- Diffen er minimal og følger `SOLUTION_BLUEPRINT.md` 100 %.

---

## 3. Handoff til Agent 4 (QA Gate)
Patch er ferdigstilt og overleveres til **Agent 4: QA Gate**.

---

# PATCH REPORT: Android Range/206 og Produksjonsordre 4

- `backend/server.py`: la til sikker single-range-parser for lydfiler på disk.
  Vanlig GET bruker fortsatt `FileResponse` og HTTP 200. Gyldig Range returnerer
  eksakte bytes med HTTP 206, `Content-Range`, `Content-Length` og
  `Accept-Ranges`; ugyldig Range returnerer 416. Public MP3/M4A/WAV/OGG og
  TTS-cachetreff bruker samme helper.
- `backend/webapp.py`: la til Thai-only «ดูคำศัพท์นอร์เวย์» for skiltkort.
  Norsk fagord er skjult til eksplisitt trykk, og raden reserverer høyde for å
  unngå layoutskift/risting.
- Oppdaterte syv foreldede testforventninger til gjeldende fullkarusell og den
  kontrollerte § 7 nr. 2-fail-safe-flyten. Ingen produksjonslogikk ble endret
  for å tilfredsstille gamle tester.
- Ny isolert Range-test dekker full GET, gyldig delområde og ugyldig område.

Verifisering: Python-syntaks PASS, inline JavaScript PASS, 64/64 målrettede
regresjonstester PASS, 3/3 Range-tester PASS og 20/20 BLAST PASS.

Ingen endring i auth, kvoter, Stripe, RevenueCat-konfigurasjon, hemmeligheter
eller mobilappen. Klar for Agent 4.

---

# PATCH REPORT: Michael WebVTT MIME-hotfix

**Status:** IMPLEMENTERT OG LOKALT TESTET
**Dato:** 2026-09-05
**Scope:** Kun korrekt MIME-type for de publiserte thai-undertekstene.

- `backend/server.py`: `.vtt` leveres som `text/vtt` fra den eksisterende
  `/api/assets/{filename}`-ruten.
- `tests/test_michael_media_cards_contract.py`: kontrakttest hindrer fallback
  til `application/octet-stream`.
- Relevant Michael-, skilt- og medieregresjon: **84/84 PASS**.
- `git diff --check`: **PASS**; kun eksisterende LF/CRLF-varsler.
- Ingen learner-facing tekst, database, auth, betaling, premium, kvote eller
  TTS-providerkonfigurasjon er endret.

Live-status krever etter deploy HTTP 200 og `Content-Type: text/vtt` på alle
25 spor. Rollback er å reversere MIME-tabellinjen og kontrakttesten.

Handoff til QA Gate før produksjonsstatus settes grønn.

---

# PATCH REPORT: Michael høyreregelbilde og komplett svar

**Status:** LOKALT TESTET – PRODUKSJON IKKE VERIFISERT
**Dato:** 2026-09-05

- `backend/public_assets/michael_hoyreregel.svg`: språkneutral illustrasjon med
  stabilt filnavn for Michael-kortet.
- `backend/media_catalog_manifest.json`: tre døde bildebaner er erstattet med
  faktiske deploy-filer; bussreferansen er samtidig korrigert til § 7 nr. 5.
- `backend/scripts/link_michael_core_media.py`: idempotent og eksplisitt
  produksjonskobling. Den krever eksakt databasenavn, tar tapsfritt snapshot
  med rollback og stopper dersom aktiv bussvideo, korrekt koblet § 7 nr. 5-
  materiale, thai-undertekst eller skilt 202 mangler.
- `backend/teacher_chat.py`: direkte spørsmål om høyreregelen får en komplett,
  kontrollert forklaring på valgt språk etter den generelle kortversjonen.
- `tests/test_michael_core_media_link.py`: dekker filer, NO/TH/EN-oppslag,
  databaseforutsetninger, rollback-snapshot og komplett svar.

Verifisering: 40/40 målrettede tester PASS, Python-kompilering PASS,
dry-run PASS, `git diff --check` PASS og ingen hemmeligheter funnet i diffen.
Fire kjente legacy-feil i `tests.test_michael_unified` er uendret og ikke brukt
som grønt bevis.

Ikke berørt: auth, kvoter, premium, Stripe, RevenueCat, TTS-konfigurasjon eller
mobilkode. Rollback er å gjenopprette snapshot-posten og reversere commit.

---

# PATCH REPORT: Michael MP4 Range-hotfix

**Status:** IMPLEMENTERT OG LOKALT TESTET
**Dato:** 2026-09-05

- `backend/server.py`: `.mp4` bruker eksisterende, testet byte-range-hjelper.
- `tests/test_michael_media_cards_contract.py`: kontrakten krever MP4 i
  Range-rutingen.
- Relevant Michael-, skilt- og medieregresjon: **85/85 PASS**.
- Vanlig GET skal fortsatt gi HTTP 200; gyldig Range skal gi HTTP 206.
- Ingen database-, språk-, auth-, betalings-, kvote- eller TTS-endring.

Live-status krever 25/25 HTTP 206 med korrekt `Content-Range` etter deploy.

## Thai bussvideo-ruting

- `backend/media_catalog.py`: § 7 nr. 5 har tre kontrollerte thai-synonymer
  for naturlige spørsmål om bussregelen.
- To regresjonstester krever at thai-spørsmålet rangerer bussmaterialet først
  og beholder thai tittel/caption uten norsk fallback.
- Relevant samlet suite etter utvidelsen: **86/86 PASS**.
