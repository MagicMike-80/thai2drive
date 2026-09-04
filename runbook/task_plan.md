# Task Plan & Runbook: Thai2Drive (BLAST Framework & 4-Agent Squad)

Dette dokumentet definerer den operative fremdriftsplanen og runbooken for Thai2Drive-systemet, strukturert etter BLAST-rammeverket og Protokoll Null.

---

## 🚀 100 % Fullført Masterplan i Dag

### ✅ Oppdrag 1: Michaels Kognitive Loop & Pedagogiske Hjerne
- [x] Beslutningsmodell **Se ➔ Oppfatte ➔ Avgjøre** i `backend/teacher_chat.py`.
- [x] 5-stegs-pedagogikk med «Kongen og tjeneren» for vikeplikt og «HAV-regelen» for § 3.
- [x] Thai-låsing til **ครับ / ผม** og totalforbud mot **ค่ะ / นะคะ**.
- [x] Lovhjemmel (§ 7 nr. 2 / § 3) plassert KUN til slutt som bekreftelse.

### ✅ Oppdrag 2: Karusell-Risting på iOS Safari
- [x] `.js-scrolling` klasse i CSS med `scroll-snap-type: none !important`.
- [x] `showTab()` i `backend/webapp.py` med 350 ms `setTimeout` og timer-clear.

### ✅ Oppdrag 3: Backend-TTS & Mobil Lydavspilling
- [x] `Accept-Ranges: bytes`, `Content-Type: audio/mpeg` og `Cache-Control: no-cache` i `backend/server.py`.
- [x] Synkron `audio.load()` og `audio.play()` i brukerklikk-callstack med `.catch()` og 5s timeout watchdog i `backend/webapp.py`.

### ✅ Oppdrag 5: «Thailand vs Norge» Mikroleksjoner (Kjørekultur-pedagogikk)
- [x] `backend/micro_lessons.py` med 4 mikroleksjoner (Høyreregel, Gangfelt, Rundkjøring, Vinterkjøring).
- [x] Ruting av `/api/lessons/culture` i `backend/server.py`.

### ✅ Oppdrag 6: «Michaels Exam Mode» & Intelligent Klar-Score
- [x] `backend/readiness.py` med 3-akset formel: Nøyaktighet (50%), Emnespredning (30%), Eksamenssimuleringer (20%).
- [x] Ruting av `/api/user/readiness` i `backend/server.py`.
- [x] Pedagogisk veiledning fra Michael (🌱 / 📈 / 👑).

### ✅ Oppdrag 7: RevenueCat Live Produksjons-Struktur & Fail-Soft Billing
- [x] `backend/billing.py` med miljøstyrt `REVENUECAT_API_KEY` og fail-soft fallback.
- [x] Ruting av `/api/billing/subscription` i `backend/server.py`.

### ✅ Oppdrag 8: Offline-Modus & ServiceWorker
- [x] `backend/service-worker.js` som cacher kjerne-UI, skilt og spørsmål.
- [x] Ruting av `/service-worker.js` og `/api/service-worker.js` i `backend/server.py`.
- [x] Registrering av ServiceWorker i `backend/webapp.py`.

---

## 🛠️ Runbook: Operasjonelle Kommandoer

### 1. Kjøre full BLAST kontraktstest-suite (16/16 tester)
```bash
node tests/run_michael_blast_tests.js
```

### 2. Kjøre backend lokalt
```bash
cd backend
python server.py
```
Backend starter på `http://localhost:8000`.

### 3. Verifisere web-app grensesnitt
Åpne nettleser på `http://localhost:8000/api/web`.
