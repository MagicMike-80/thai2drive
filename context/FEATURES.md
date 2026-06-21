# Thai2Drive — Feature Wishlist

Dette er den permanente ønskelisten for Thai2Drive, styrt etter **The Master Blueprint**.
Alle agenter (Claude Code, Codex, og andre) oppdaterer denne filen automatisk.
Michael trenger bare si hva han ønsker — resten skjer av seg selv.

**Regler:**
- Aldri lagre API-nøkler eller passord her — bruk Railway env-variabelnavn.
- Ikke commit denne filen til git.
- Web app først. Mobil følger kun etter eksplisitt godkjenning fra Michael.
- Alle features skal inn her med en gang Michael nevner dem.

---

## ✅ LEVERT
- ✅ Kompakt knapp-layout (ExpandableButtonGroup)
- ✅ ElevenLabs voice (TTS) i app og web (Codex)

---

## 🔴 PRIORITERT — IKKE KLAR
- 🔴 **Bibliotek (Library) — Ryggraden for repetisjon**
  - Historikk, Bokmerker for vanskelige situasjoner, Studiebok, Komplett Skilt-katalog.
  - Skal bygges web-first.

- 🔴 **Michael hurtigvalg-knapper (Kontekst-spesifikk hjelp)**
  - 🛑 Forklar et skilt
  - 🚗 Hjelp med vikeplikt
  - 📖 Forklar en trafikkregel
  - Be om forklaring på spørsmål brukeren svarte feil på.
  - Kobles mot `/api/teacher/chat`.

- 🔴 **AI feillogg (Codex)**
  - Logger språk, spørsmål, svartid og feil for å sikre at Michael underviser korrekt over tid.

- 🔴 **Smart Øving (Spaced Repetition / Adaptivt læringsløp)**
  - Analyserer svakeste temaer per elev.

---

## 🟡 PLANLAGT
- 🟡 **Neon design — web app**
  - Cyan #00F5FF, magenta #FF00E5, gul #FFD700 på markedsføringssiden.

---

## ⏳ IDEER — IKKE BESLUTTET
<!-- Legg til ideer her som ikke er klare til å planlegges ennå -->

---

## 📋 For agenter
Når Michael sier "jeg ønsker", "kan vi få", "legg til", eller beskriver noe han vil ha:
1. Legg det til i denne filen umiddelbart under riktig seksjon
2. Ikke vent — gjør det samme svar som ønsket nevnes
3. Web-app-først-regelen gjelder alltid for UI-features
4. Når noe er ferdig og live: flytt det til ✅ LEVERT
5. Hemmeligheter lagres aldri her
