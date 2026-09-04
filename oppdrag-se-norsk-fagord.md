# Oppdrag: «Se norsk fagord»-knappen

**Til:** Codex · **Flate:** web (`backend/webapp.py`, `backend/server.py`) · **Status:** godkjent av Michael 2026-08-25

Thailandske elever strander på det norske fagspråket, ikke på trafikkreglene. Denne
funksjonen kobler thai-begrepet de tenker på til det norske ordet de møter på prøven.

> **Mobil-appen er utenfor omfang.** Web only.

---

## 0. Les dette først — to feller

### Felle 1: «Forkjørsvei» er ikke en tekstendring

Seederen hopper over eksisterende termer **per `term_no`** (`seed_glossary.py:299`).
Endrer du bare strengen og kjører skriptet på nytt, finner det ingen match på det nye
navnet og **setter inn en ny term ved siden av den gamle**. Begge blir liggende, eleven
ser to oppføringer for samme begrep, og kjøringen melder `INSERT` som om alt gikk bra.

Bruk `update_one`, ikke re-seed:

```python
res = await db.learning_glossary.update_one(
    {"term_no": "Prioritert vei"},
    {"$set": {"term_no": "Forkjørsvei"}},
)
# Verifiser etterpa: skal vaere 22 dokumenter, ikke 23.
assert await db.learning_glossary.count_documents({}) == 22
```

`seed_glossary.py` er allerede oppdatert i dette repoet, så en tom base seedes riktig.
Migreringen gjelder kun eksisterende produksjonsdata.

### Felle 2: ordtreff må bruke ordgrense

Delstreng-match gir falske treff: «vike» treffer «Vikeplikt», «fart» treffer
«fartsgrense» *og* «oppfart». Bruk `\b`-grenser og match case-insensitivt.

Norsk bøying må også fanges — «vikeplikten», «bremselengden». Match derfor på
stammen med valgfri bestemt endelse, ikke på eksakt ord.

---

## 1. Innholdet er klart

`learning_glossary` har **22 termer**, seedet fra `backend/scripts/seed_glossary.py`.
Ingen ny ordbok skal lages.

Dokumentform:

```json
{
  "term_no": "Vikeplikt",
  "term_th": "การให้ทาง",
  "term_en": "Yield / Right of way",
  "definition_no": "Plikten til å la andre trafikanter passere før deg.",
  "definition_th": "หน้าที่ที่ต้องยอมให้ผู้ใช้ถนนคนอื่นผ่านก่อนคุณ",
  "example_th": "คุณต้องให้ทางรถที่มาจากทางขวาในสี่แยกที่ไม่มีป้าย",
  "topic_tags": ["Vikeplikt", "Kryss"],
  "active": true
}
```

### Innholdsendringer allerede gjort (2026-08-25)

| Term | Endring | Grunn |
|---|---|---|
| Prioritert vei → **Forkjørsvei** | `term_no` | Michaels beslutning — ordet som gjelder på prøven |
| Forkjørsvei | `term_th`: `ถนนหลัก (ถนนที่มีสิทธิ์ก่อน)` → `ถนนหลัก` | Parentesen dupliserte definisjonen |
| Vikepliktskilt | `term_th`: `ป้ายให้ทาง (สามเหลี่ยม)` → `ป้ายให้ทาง` | Samme — formen står i definisjonen |
| Stopp-skilt | `term_th`: `ป้ายหยุด (แปดเหลี่ยม)` → `ป้ายหยุด` | Samme |
| Stopp-skilt | `definition_no`: «du MUST stanse» → «du **MÅ** stanse» | Engelsk ord midt i norsk tekst |

### Verifisert språkrenhet

Alle 22 termer er auditert på tvers av `term_th`, `definition_th` og `example_th`:

- **Ingen kvinnelige partikler** (`ค่ะ`, `นะคะ`, `ดิฉัน`). Michael er mann — kun `ครับ` og `ผม`.
- **Ingen `สิทธิ์ทาง`.** Vikeplikt er `การให้ทาง`. `สิทธิ์ทาง` betyr *retten* til å kjøre
  først, altså forkjørsrett — motsatt av vikeplikt. Skal aldri brukes for vikeplikt.
- **Ingen engelsk lekkasje** i thai-feltene. Eneste latinske tegn er `Thai2Drive`,
  som er produktnavnet og skal stå slik.

---

## 2. Migrering

Eget skript, `backend/scripts/migrate_forkjorsvei.py`, idempotent:

- `update_one` på `term_no: "Prioritert vei"` → `"Forkjørsvei"`
- Sett også `term_th` til `ถนนหลัก` i samme operasjon (produksjonsdata har fortsatt parentesen)
- Kjør på nytt uten skade: finner den ingen «Prioritert vei», er jobben gjort
- Skriv ut antall dokumenter etterpå — **22, ikke 23**

---

## 3. Backend: `GET /api/quiz/terms`

```
GET /api/quiz/terms?question_id=<id>&lang=th

200 OK
{
  "question_id": "...",
  "terms": [
    {
      "term_no": "Vikeplikt",
      "term_th": "การให้ทาง",
      "definition_th": "หน้าที่ที่ต้องยอมให้ผู้ใช้ถนนคนอื่นผ่านก่อนคุณ",
      "source": "text"
    }
  ]
}

Ingen treff → { "terms": [] } → frontend skjuler knappen
```

**Uttrekksrekkefølge:**

1. **Ordtreff** i `question_text_no` + de fire norske svarene, mot `term_no`.
   Ordgrense, case-insensitivt, med valgfri bestemt endelse.
2. **Suppler fra kategori** via `topic_tags`. Merk at kategoriene er engelske nøkler
   (`Intersections`, `Overtaking`, `Safety`) mens taggene er norske (`Kryss`, `Fart`,
   `Sikkerhet`) — det trengs et lite oppslag mellom dem.
3. **Ranger:** direkte ordtreff først (`source: "text"`), så kategoritreff
   (`source: "category"`).
4. **Kutt ved fire.** Flere blir en lekse, ikke en hjelp midt i en quiz.

**Krav:**

- **Ingen auth, ingen kvote.** Dette er en ordbok. Å låse den bak betalingsmuren ville
  straffet nettopp de elevene funksjonen finnes for.
- **In-memory cache.** 22 termer er ~4 kB. Last én gang ved oppstart; ikke slå opp i
  Mongo per spørsmål.
- **Returner kun det språket som er bedt om**, pluss `term_no`. Sender du alle tre
  språk, er språklekkasje én slurvefeil unna i frontend.

---

## 4. Logging

Ny kolleksjon `glossary_lookup_logs`. Følg mønsteret fra `teacher_chat_logs`.

```python
db["glossary_lookup_logs"].insert_one({
    "device_id": device_id,      # samme pseudonyme id som quizen
    "question_id": question_id,
    "category": category,
    "terms_shown": ["Vikeplikt", "Høyreregelen"],
    "lang": "th",
    "ts": datetime.now(timezone.utc),
})
```

- **Logg at kortet ble åpnet**, ikke enkeltord. Eleven ser alle samtidig, så vi kan ikke
  vite hvilket hen leste. Å logge per ord ville gitt falsk presisjon.
- **Ingen e-post, intet navn.** `device_id` skiller brukere uten å identifisere dem.
- **Fail-soft.** En loggfeil skal aldri stoppe svaret til eleven — `try/except`, slik
  `teacher_chat` gjør.

---

## 5. Frontend (`webapp.py`)

Knappen ligger rett under spørsmålsteksten:

```
📖 ดูคำศัพท์นอร์เวย์
```

Utfelt kort:

```
การให้ทาง  ➔  Vikeplikt
หน้าที่ที่ต้องยอมให้ผู้ใช้ถนนคนอื่นผ่านก่อนคุณ

กฎการให้ทางด้านขวา  ➔  Høyreregelen
รถที่มาจากทางขวาไปก่อน เมื่อไม่มีป้ายกำหนด
```

Det norske ordet står i **latinsk skrift, uendret**. Det er ikke språkblanding — det er
hele poenget: eleven skal kjenne igjen nøyaktig den bokstavrekken på prøveskjermen.

**Krav:**

- **Kun når `appLang === 'th'`** og endepunktet returnerte minst én term.
- **Slide-down** via `max-height`-overgang, ikke `display`. Respekter
  `prefers-reduced-motion`.
- **Lukkes ved spørsmålsbytte.** `renderQuestion()` må nullstille panelet, ellers henger
  forrige spørsmåls ord igjen.
- **Ett kall per spørsmål**, cachet i klienten.
- **Ingen `scrollIntoView()`.** Bruk lokal container-scrolling — global scroll gir rykk
  på mobil.
- **Ikke gjenbruk `.paywall-buy-btn`.** Den treffes av neon-regelen som setter mørk
  bakgrunn med `!important`; målt kontrast blir 1,01. Egen klasse med eksplisitt lys
  tekstfarge (`#F8FAFC`).

### Oversettelser

| Nøkkel | th | no | en |
|---|---|---|---|
| `terms_btn` | ดูคำศัพท์นอร์เวย์ | Se norske fagord | See Norwegian terms |
| `terms_hide` | ซ่อนคำศัพท์ | Skjul fagord | Hide terms |
| `terms_none` | — | — | — |

`terms_none` trengs ikke: har spørsmålet ingen fagord, vises ikke knappen i det hele tatt.

---

## 6. Definition of done

- [ ] Migrering kjørt, `learning_glossary` har **22** dokumenter
- [ ] `GET /api/quiz/terms` svarer med termer for et vikepliktspørsmål, tom liste for et
      spørsmål uten treff
- [ ] Knappen vises kun på thai, kun når det finnes termer
- [ ] Panelet lukkes ved spørsmålsbytte
- [ ] Ingen `scrollIntoView()`; ingen rykk på mobil
- [ ] Kontrast på knappen ≥ 4,5:1
- [ ] `glossary_lookup_logs` får en rad når kortet åpnes, og feiler stille
- [ ] `python -m py_compile backend/webapp.py backend/server.py`
- [ ] Ingen latinske tegn i thai-teksten utover `Thai2Drive`

---

## 7. Utenfor omfang

- **Mobil-appen** — satt på pause
- **Redigering av ordboken fra admin**
- **Lyd på fagordene** — utsatt til TTS er stabil på alle enheter. Når den tid kommer er
  inngangen enkel: termene har allerede `term_no`, og `/api/tts/stream?lang=nb-NO` tar
  imot dem som de er. Ingen ny datastruktur trengs.

---

## 8. Én ting som ikke er verifisert

De 22 thai-definisjonene i `seed_glossary.py` er **ikke lest av en morsmålsbruker**.
De er korrekte så langt jeg kan bedømme, men korrekt og godt er ikke det samme.
Michael er thaifødt — femten minutter med listen før lansering er den billigste
kvalitetssikringen som finnes her.
