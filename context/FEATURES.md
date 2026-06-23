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
- ✅ **Bibliotek (Library) — Ryggraden for repetisjon**
  - Historikk, Bokmerker, Studiebok, Trafikkskilt-katalog via web-first.
- ✅ **Michael hurtigvalg-knapper (Kontekst-spesifikk hjelp)**
  - Web-appen har nå suggestion chips og hurtigvalg-knapper i sidemenyen/mobilmenyen (Codex).
- ✅ **AI feillogg (Codex)**
  - Logger språk, spørsmål, svartid og feil til `teacher_chat_logs`.
- ✅ **Smart Øving (Spaced Repetition / Adaptivt læringsløp)**
  - Analyserer svakeste temaer per elev via `ai_learning.py` og bygger adaptiv queue i quizzen.
- ✅ **Neon design — markedsføringssiden (landing.py)**
  - Cyan #00F5FF hero-knapper, aurora bakgrunn, magenta #FF00E5 eyebrows, gull #FFD700 stats og hero-highlight. Commit 7f2e747.

---

## 🔴 PRIORITERT — IKKE KLAR
- 🔴 **Globalt Neon-design & Knappeeffekter**
  - Implementer dynamisk, flytende neon-ramme (color-shifting border glow) rundt alle knapper og kanter i hele appen.
  - Fargene må flyte/bevege seg rundt hele omkretsen (perimeteren) av knappene/kantene, ikke være statiske eller låst til ett sted (slik som på 3D-karusellens sidekort eller toppen).

## 🟡 PLANLAGT

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
