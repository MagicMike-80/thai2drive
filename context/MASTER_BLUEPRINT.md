# Thai2Drive — Master Blueprint

Dette er fasiten for plattformen. Alle agenter leser dette som grunnlag for all videre utvikling.

---

## DEL 1: Arkitektur & Tekniske Krav (Codex)

- **100 % Språkisolasjon:** Null language bleed-through. Thai-modus = alt på thai. Norsk-modus = alt på norsk. Gjelder quiz, feilmeldinger, betalingsmur og AI-chat.
- **Én felles Michael-kjerne:** Ett API-endepunkt (`/api/teacher/chat`) forsyner både web og mobil. Elevene får alltid nøyaktig samme svar uansett plattform.
- **Web-first:** All ny funksjonalitet bygges, testes og godkjennes på web først. Mobil røres ikke før webversjonen er 100 % stabil og eksplisitt godkjent av Michael.
- **TTS (ElevenLabs):** Dynamisk MP3-opplesning av spørsmål og forklaringer på thai. Lyd- og hastighetsknapper aktiveres kun når grensesnittet er satt til thai. API-nøkkel: Railway env `ELEVENLABS_API_KEY`.
- **Feillogg for AI:** Systemet logger språk, spørsmål, svartid og feil for å sikre at Michael underviser korrekt.

---

## DEL 2: AI-Lærer Michael & Pedagogikk (Claude Code)

- **7-årsregelen:** Michael forklarer som til en 7-åring — korte setninger, eksempler fra virkeligheten, ingen tung juss.
- **Stressfri veiledning:** Ved feil stiller Michael kun ett enkelt oppklarende spørsmål — aldri en rekke spørsmål.
- **Kontekst-spesifikk hjelp med hurtigvalg:**
  - 🛑 Forklar et skilt
  - 🚗 Hjelp med vikeplikt
  - 📖 Forklar en trafikkregel
  - Mulighet for å be om forklaring på spørsmål brukeren svarte feil på
- **Streng AI-sikkerhet:** Michael finner aldri opp regler, bruker ikke uoffisielle skiltnavn, gjetter ikke. Usikker? → "Det er jeg usikker på. La oss se på regelen sammen."
- **Faste mentale modeller:**
  - *Kongen og tjeneren:* Har du vikeplikt er du tjeneren — la aldri kongen (den med forkjørsrett) tenke på deg.
  - *HAV-regelen:* Hensynsfull, Aktpågivende, Varsom — kjerne i Vegtrafikkloven § 3.
  - *De 6 vikepliktsreglene:* Inkluderer speil-speil-blindsone og Bussregelen (60 km/t eller lavere).
  - *Rundkjøringsregelen:* "Ikke se etter biler. Se etter muligheter."
  - *Blikkregelen:* "Aldri lås blikket på ett sted."

---

## DEL 3: Elevens Læringsopplevelse (Funksjoner)

- **Biblioteket:** Dedikert seksjon med Historikk, Bokmerker (vanskelige situasjoner), oversatte teorikapitler (Studieboken), og komplett Trafikkskilt-katalog. Kun premium.
- **Adaptivt læringsløp & Smart Øving:** Systemet analyserer svakeste temaer og tilbyr Spaced Repetition for å tette personlige kunnskapshull.
- **Visuell trafikk-matte (Forbikjøring/Stoppeavstand):** Kalkulator der eleven justerer fart og veiforhold og ser reaksjons- og bremselengde beregnet trinnvis.

---

## DEL 4: Forretningsmodell & Konvertering

- **Freemium — value before payment:**
  - Gjest: 5 spørsmål totalt
  - Innlogget gratis: 10 spørsmål per dag
  - Premium: ubegrenset + dypere veiledning
- **Priser:** 199 kr/mnd · 399 kr/3 mnd · 699 kr livstid
- **Språkstyrt betalingsmur:** Premium-portalen vises kun på elevens valgte språk. Ingen kjøpsfriksjon.
- **Tone:** Støttende lærer, ikke aggressiv selger.

---

## DEL 5: Arbeidsdeling

| Rolle | Ansvar |
|-------|--------|
| **Codex** | All koding, backend/API, database, web/mobil-endringer, Railway, Expo, produksjonssikkerhet |
| **Claude Code** | Pedagogikk, AI-personlighet, oversettelser (thai/no/en), markedsføringsmanus, læringsmål |

Absolutt forbud mot å arbeide i hverandres ansvarsområder samtidig.

---

*Godkjent av Michael — 2026-06-21*
