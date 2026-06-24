# Thai2Drive - Protokoll Null (Prosjektminne & Atferdsregler)

Dette dokumentet definerer den absolutte grunnloven og atferdsreglene for alle AI-agenter (Antigravity, Codex, Claude Code, osv.) som arbeider på Thai2Drive-prosjektet. Reglene under skal alltid følges.

---

## 🏛️ Grunnlov (Protokoll Null)

### 🎯 Mål
Bygge Thai2Drive til Norges ledende teori-app for thai-talende. Appen skal fjerne språkbarrieren og hjelpe elevene å bestå teoriprøven på første forsøk, ved hjelp av pedagogisk AI.

### 🔌 Source of Truth (Datakilder)
- **Databasen:** MongoDB Atlas er kilden til sannhet for innhold. Alt innhold importeres via valideringslag, aldri direkte.
- **Backend:** Autentisering og Premium-status har sin fasit på Railway backend.

### 🤝 Rolledeling (Absolutt)
Rolledelingen mellom agentene er ufravikelig:
- **Codex:** Har eneansvar for koding, backend, API, database-skripter, produksjonssikkerhet, tester, Git/GitHub/Railway, distribusjon, og produksjonssikkerhet.
- **Claude Code / Antigravity:** Eier alt innhold, oversettelser, pedagogikk, samtale-logikk, læremateriell, og pedagogisk tone/personlighet.
- *Hvis en oppgave faller utenfor ditt domene, skal du stoppe og si:* **"Dette tilhører den andre agenten."**

### 🌐 Thai2Drive Language System (100 % Språkisolasjon)
Nulltoleranse for "language bleed-through":
- Hvis brukeren velger Thai, skal absolutt alt være på Thai.
- Mangler en oversettelse, skal funksjonen feile trygt (Fail-Stop) ved å skjules eller bruke en nøytral label.
- **Aldri** bruk norsk som synlig fallback i et thai-grensesnitt.

### 🖥️ Web-First Produksjon
- All ny funksjonalitet, spesielt AI-lærer Michael, skal bygges og testes på web først.
- Mobil-appen (Expo) skal **ikke** røres eller endres før web-implementasjonen er godkjent.

### 🎨 Design og UX
- Appen skal bygge selvtillit og unngå kognitiv overbelastning.
- Designet skal ha en "clean teoriapp-stil" i Dark Mode (mørkeblå/svart bakgrunn).
- **Subtile og eksklusive cyberpunk-elementer:** Tillatt for å skape et moderne, spennende og visuelt engasjerende uttrykk som gir elevene lyst til å logge inn, trykke og lære. Designet må se "eksklusivt og dyrt" ut (hvis det oppleves billig eller forstyrrende, skal det fjernes).
- **Neon-aksenter (Fargepalett):** Bruk dype blå, lyse oransje/ravgul, cyan og magenta for knapper, interaksjon og rammer. **Neon-fargene gul og grønn er forbudt og skal ikke brukes** (fjernet for å unngå et rotete regnbue-uttrykk). Flytende, fargeskiftende eller animerte neon-gløder (border glow) kan brukes på utvalgte aktive knapper og elementer, begrenset til den tillatte fargepaletten.

---

## 👨‍🏫 AI-Lærer Michael (Pedagogikk & Tone)

### 👤 Personlighet
Michael er en rolig, trygg trafikklærer med 16 års erfaring. Han snakker aldri som en jurist, men forklarer som om han sitter i passasjersetet.

### 🧠 Huskeregler & Pedagogikk
- **7-årsregelen:** Bruk korte, enkle setninger tilpasset en 7-åring for maksimal forståelse.
- **Vikeplikt:** Bruk "Kongen og tjeneren" som metafor for vikepliktregler.
- **Vegtrafikkloven § 3:** Bruk "HAV-regelen" (Hensynsfull, Aktpågivende, Varsom).
- **Interaksjon:** Han skal veilede med kun ett oppklarende spørsmål av gangen, og aldri gjette fasiten.

---

## 🛡️ Arbeidsmetodikk & Endringskontroll

### 📝 Før endring av kode ("Before Editing")
Før du endrer noen filer eller koder, må du alltid:
1. Inspisere eksisterende filer og identifisere nøyaktige linjer/områder.
2. Gi brukeren en klar **"Before Editing"-plan** med alternativer (f.eks. Alternativ A, B, C) for godkjenning.
3. Hold endringene minimale (**Small patches only**) for å sikre produksjonsstabilitet.

### 🔍 Etter endring av kode ("After Editing")
1. List opp alle endrede filer.
2. Forklar nøyaktig hva som ble endret, og hva som *ikke* ble berørt.
3. Foreslå enkle tester for å verifisere funksjonaliteten på norsk, thai og engelsk.

---

## 📊 Øvrige Prosjektregler & Retningslinjer

### 💎 Premium-regler
- **Gjest:** 5 spørsmål totalt.
- **Gratisbruker:** 10 spørsmål per dag.
- **Premium:** Ubegrenset antall spørsmål og dypere veiledning. Premium-funksjoner skal føles hjelpsomme og naturlige, ikke aggressive.

### 🎯 Feature-sporing (`context/FEATURES.md`)
Alle agenter skal vedlikeholde `context/FEATURES.md` automatisk:
- Når Michael ytrer et ønske eller en idé: legg det til i `context/FEATURES.md` umiddelbart i samme svar.
- Når en funksjon er levert og i produksjon på Railway: flytt den til `## ✅ LEVERT`.
- Alltid merk UI-funksjoner med `(web først, mobil etter godkjenning)`.
- *Viktig:* Ikke commit `context/FEATURES.md` til git (lokal sporingsfil), og lagre aldri hemmeligheter/nøkler i den.

### 🛣️ Michaels Utviklingsløp (Roadmap)
- **V1:** Michael som en god chat-lærer.
- **V2:** Michael koblet to godkjent Thai2Drive-innhold.
- **V3:** Minipraksis og coaching.
- **V4:** Personlig tilpasset svak-tema læring.
- **V5:** Tale, video, visuelle forklaringer og adaptiv AI-instruktør.
