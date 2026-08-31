# SOLUTION BLUEPRINT — Thai2Drive Admin som Michaels materialbibliotek

## Mål

Gjør adminpanelet til kontrollrom for godkjente skilt, veikryss-/situasjonsbilder
og videoer som Michael kan hente deterministisk når de passer samtalen.

## Ikke-mål

Ingen flytting eller kopiering av dagens 316 skiltposter, ingen ny AI-modell,
ingen fri nettsøk/AI-genererte URL-er, ingen redesign av hele adminpanelet og
ingen endring i TTS, auth, premium, Stripe, RevenueCat eller betaling.

## Data og kontrakt

Legg en additiv `michael_materials`-indeks som peker til eksisterende kilder i
stedet for å duplisere dem. Hver post inneholder minst:

- `id`, `type` (`sign`, `intersection_image`, `video`), `source_id`/`source_url`
- `title.no/th/en` og `caption.no/th/en`
- `topic_tags`, `sign_ids`, `situation_tags`
- `active`, `approved_for_michael`, `priority`, `created_at`, `updated_at`

Utvid `POST /api/teacher/chat` additivt med:

`media: [{id, type, url, title, caption, sign_id?}]`

Behold eksisterende `reply`, `suggestions` og `sign_ids` uendret. Backend velger
mediene; frontend rendrer bare den godkjente listen. Manglende komplett tekst på
aktivt språk gir ingen mediepost.

## Trinnvis patchplan

### Patch 1 — adminindeks og CRUD

- Legg én ny «Michael-materiale»-fane i `backend/admin.html`.
- Opprett/liste/rediger/deaktiver referanser til eksisterende skilt, bilder og
  videoer.
- Vis forhåndsvisning og valider at kilde-URL/ID finnes.
- Ingen kobling til chatten ennå.

### Patch 2 — deterministisk retrieval

- Legg en isolert backend-helper som rangerer aktive, godkjente materialer etter
  eksplisitt `sign_id`, deretter situasjons-/emnetags og priority.
- Returner maks to medier og tekst-only ved manglende sikkert treff.
- Bevar dagens skiltlogikk som førsteprioritet.

### Patch 3 — additiv chatrespons og webkort

- Legg `media` til `TeacherChatResponse` uten å fjerne eksisterende felt.
- Render bilde/video under riktig Michael-svar, med aktivt språk og mobiltilpasset
  størrelse.
- Ved mediefeil beholdes svaret og kortet skjules.

### Patch 4 — kontroll og opprydding

- Adminfilter for type, tag, språk, aktiv og «mangler kobling».
- Rapport over skilt/materiale uten komplett NO/TH/EN eller gyldig kilde.

## Tester og manuell verifisering

- API-kontrakt for additivt `media`-felt og uendret `sign_ids`.
- Trefftest: «vikeplikt» → skilt `202_0`; relevant veikryss → koblet bilde;
  relevant video → godkjent video.
- Negative tester for oppdiktet URL, deaktivert materiale, feil tag og manglende
  aktivt språk.
- Mobiltest på NO/TH/EN og tekst-only fallback.

## Rollback og produksjonsrisiko

Alle patcher er additive. Funksjonen kan slås av ved å ignorere
`michael_materials`/`media`, mens dagens skiltkort og tekstchat fortsetter.
Største risiko er feil kobling; derfor kreves eksplisitt godkjenning, maks to
medier og prioritert ID-treff foran frie teksttags.

## Avgjørelse fra Michael

Før Agent 3 starter må Michael godkjenne at første leveranse er Patch 1 alene:
adminindeks og forhåndsvisning, uten chatkobling eller deploy av de senere
trinnene.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT — ekte vikepliktskilt i Michael-sidefeltet

## Mål

Knytt teksten «Hjelp med vikeplikt» visuelt til det godkjente norske
vikepliktskiltet, uten å gjøre sidefeltet større eller endre betydningen av
temaet.

## Minste production-sikre patch

- Erstatt bil-emojien bare på vikepliktvalget med et 32–36 px miniatyrbilde av
  eksisterende skilt `202_0`.
- Hent bildet via eksisterende skiltdata/API (`image_url`); ikke legg inn en ny,
  tilfeldig eller AI-generert illustrasjon.
- Behold hele raden som én klikkbar knapp og samme Michael-temamelding.
- Behold språkrene tekster på norsk, thai og engelsk.
- Når Michael faktisk forklarer skiltet, gjenbrukes eksisterende `sign_ids`/
  skiltkort til større bilde under svaret.

## Ikke-mål

Ingen endring i skiltdata, lærer-API, prompt, TTS, auth, premium, Stripe,
RevenueCat eller betaling. Miniatyrbildet betyr ikke at alle vikepliktsregler
alltid er skiltet.

## Sannsynlige filer og test

- `backend/webapp.py`: miniatyrmarkup, rolig størrelse og fallback til dagens
  symbol hvis bildet mangler.
- `tests/test_michael_mobile_ui_contract.py`: lås `202_0`, bilde-alttekst,
  språkren tekst og uendret knapphandling.
- Manuell 390 px kontroll på NO/TH/EN og kontroll av bilde-feilfallback.

Rollback er å fjerne miniatyrmarkuppen og vise det tidligere symbolet igjen.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT — vis/skjul emner i Michael-sidefelt

## Mål

Hold Michael-chatten rolig ved å skjule de store startknappene fra hovedflaten og gjenbruke de seks eksisterende, språkrene emnene i et sidefelt som eleven åpner ved behov.

## Avgrenset patch

- Legg én kompakt vis/skjul-knapp i Michael-headeren.
- Vis de seks eksisterende emnene i et off-canvas sidefelt på mobil og desktop.
- Lukk sidefeltet ved emnevalg, trykk utenfor eller Escape.
- Bevar skrivefeltet «Spør Michael…» og den ene kontekstknappen «Øv på liknende».
- Bevar API, AI-svar, TTS, auth, premium, Stripe, RevenueCat og betaling urørt.

## Risiko og rollback

Endringen er kun HTML/CSS/JavaScript i eksisterende webflate. Rollback er å fjerne toggle/backdrop og gjenopprette den tidligere synlige emnelayouten.

## Verifikasjon

- Statisk kontrakttest for seks emner, skjult hovedmeny, toggle, backdrop og tre språk.
- Python-syntaks, relevante Michael-/skilt-tester og `git diff --check`.
- Mobil visuell kontroll med sidefelt lukket, åpent og lukket etter valg.
- Etter push: GitHub Safety Check, produksjonsversjon og live HTML-canary.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT: Fase 2 i små production-safe patcher

## Mål

Bygg én sammenhengende læringssløyfe: feil svar → Michael-forklaring → persistent feilbank → aktiv repetisjon → mestring → transparent readiness.

## Ikke-mål

Ingen redesign, ny kvote, ny AI-chat, avansert 10 min/1/3/7-dagers plan, MongoDB-migrasjon eller endring av Stripe, RevenueCat, auth-policy, premium-status eller betalingswebhooks.

## Patchrekkefølge

### Patch 1 — persistent feilbank (implementeres nå)

- Legg isolerte feilbank-helpers i eksisterende læringslag.
- Bruk en additiv `user_mistakes`-samling med unik nøkkel `user_id + question_id`; ikke legg store arrays inn i brukerdokumentet.
- Oppdater feilbanken server-side fra lagrede quizsvar for autentiserte brukere.
- Stol på JWT-identiteten, ikke klientlevert `user_id`.
- Vanlig feil reaktiverer; kun riktig svar i `mistakes`-modus bygger mestring.
- Legg tester for duplikatvern, tellere, mestring og reaktivering.

### Patch 2 — Mine feil API og aktiv quizmodus

- Legg et autentisert lese-endepunkt som henter aktive feil sortert på høyest `wrong_count`, deretter eldste `last_practiced_at`.
- Slå opp uendrede spørsmål fra eksisterende spørsmålsdatabase.
- Koble dashboardknappen og la modusen bruke eksisterende svar- og access/consume-flyt.

### Patch 3 — readiness

- Gjenbruk eksisterende forsøkshistorikk, men beregn siste 100 svar og vektene 50/20/20/10.
- Returner `insufficient_data` under 20 svar og aldri presenter score som garanti.
- Legg språkrene dashboardtekster, sterkeste/svakeste kategori og deterministisk anbefaling.

### Patch 4 — Michael ved feil

- Gjenbruk `POST /api/teacher/chat` med quizkontekst og samme aktive språk.
- Åpne et kompakt, ikke-blokkerende panel; «Neste spørsmål» forblir tilgjengelig.
- Timeout eller AI-feil beholder ordinær forklaring og stopper aldri quizen.

## Dataform for Patch 1

`user_mistakes` lagrer minst `user_id`, `question_id`, `wrong_count`, `correct_streak`, `active`, `mastered`, `last_wrong_at`, `last_practiced_at`, `created_at` og `updated_at`. Oppdatering skjer atomisk med upsert, slik at samme spørsmål ikke dupliseres.

## Risiko og rollback

Patch 1 er additiv. Største risiko er feil tolkning av svarfelt fra eldre quizøkter; helperen skal derfor ignorere poster uten gyldig `question_id`/`is_correct`. Rollback er å fjerne kall og helper; eksisterende quizforsøk forblir uendret.

## Verifikasjon

- Enhets-/integrasjonstester for alle tilstandsoverganger.
- Python-syntaks og eksisterende relevante tester.
- Diff-audit som bekrefter at auth, access, Stripe og RevenueCat ikke er endret.
- Ingen deploy i denne leveransen.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT — lesbart Michael-skiltkort på mobil

Begrens bilder fra Michaels `[image:]`-tagger til maks 210 px høyde på mobil og sentrer dem med `object-fit: contain`. Øk svarteksten fra `.96rem` til `1.05rem` og bildeteksten til `.82rem`. Bevar desktop, AI, TTS, auth og betaling. Test med statisk mobilkontrakt og JavaScript/Python-syntaks. Rollback er de nye bildeklassene og to mobile CSS-verdier.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT — prioriter konkret skilt i Michael-kontekst

## Patch

Endre bare tekstbasert skiltinnsetting i `backend/teacher_chat.py` fra append til prioritert innsetting foran generelle studiebok-/videoressurser. Bevar maks tre kontekstdeler, API-kontrakt, språk og eksisterende sikkerhetsfilter for bilder.

Legg en smal kontrakttest som låser at tekstbaserte skilt prioriteres. Kjør Python-syntaks, teacher-testene og eksisterende Michael-regresjon. Rollback er én linje tilbake til tidligere listeinnsetting.

Ingen endring i frontend, TTS, auth, premium, Stripe, RevenueCat eller produksjonshemmeligheter.

READY FOR AGENT 3
# SOLUTION BLUEPRINT: stabil andreavspilling og roligere Michael-mobilflate

## Mål

Én frontend-only patch skal gjøre lærerlyd deterministisk når eleven bytter mellom svar, og redusere høyden til Michael-sidens mobile header og kontekstforslag.

## Ikke-mål

- Ingen endring i TTS-endepunkt, ElevenLabs, stemme-ID eller fallback.
- Ingen endring i Michael AI, chatkontrakt eller sesjonsdata.
- Ingen endring i backend, auth, tilgang, kvoter, Stripe eller RevenueCat.
- Ingen redesign av desktop eller andre appskjermer.

## Filer og komponenter

- `backend/webapp.py`
  - lærerlyd: `_ensureTeacherAudio`, `stopAllSpeech`, `speakText`
  - kontekstforslag: `_teacherAppendChips`
  - mobil-CSS: `.teacher-header`, `.teacher-avatar`, `.tm-chips`
- `tests/test_michael_mobile_ui_contract.py`
  - statiske kontrakter for bytte av lyd og maksimalt tre synlige mobilforslag

## Dataflyt og API-kontrakter

`speakText(text)` beholder eksisterende `/api/tts/stream?text=...&lang=...`. Frontend sporer teksten som tilhører aktiv lærerlyd. Samme aktive tekst fungerer som stopp. En annen tekst stopper gammel avspilling og starter ny i samme kall. En monoton avspillings-token hindrer at en gammel avvist `play()`-promise nullstiller nyere lyd.

`_teacherAppendChips(chips)` beholder forslagene fra `/api/teacher/chat`, men merker forslag nummer fire og videre som mobile ekstravalg. De er synlige på desktop og åpnes eksplisitt på mobil med eksisterende globale språkstrenger `teacher_more_topics` og `teacher_fewer_topics`.

## Språk, tilgang og premium

Ingen nye learner-facing strenger. Eksisterende NO/TH/EN-nøkler gjenbrukes. Funksjonen er identisk for guest, gratis og premium og endrer ingen access-policy.

## Godkjent patchtrinn

1. Implementer aktiv tekst + token for lærerlyd, med full reset ved ended/error/stopp.
2. Begrens kontekstforslag til tre på mobil, med lokal åpne/lukke-knapp.
3. Reduser kun mobilheaderen fra 152 px til omtrent 132 px og portrettet proporsjonalt.
4. Legg til kontrakttester og kjør Python-, JavaScript- og eksisterende regresjonstester.

## Manuell verifisering

- Spill A, trykk B før A er ferdig: B skal starte med samme trykk.
- Trykk samme aktive lydknapp: lyden skal stoppe.
- Avsluttet/feilet lyd skal kunne startes på nytt.
- På 390 px: tre forslag først, resten bak «Flere emner»; input forblir synlig.
- På desktop: alle forslag forblir synlige.

## Risiko og rollback

Lav frontendrisiko. Hovedrisiko er feil state-reset ved raske trykk. Rollback er å fjerne aktiv tekst/token og mobile `mobile-extra`-regler; API og data er urørt.

Ingen ny avgjørelse kreves fra Michael. Eksisterende bilde og designretning beholdes.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT: kompakt Michael-side og datadrevne SignCard-kort

## Mål

Gjør dagens `/api/web`-chat lesbar og kompakt, og vis godkjente norske
trafikkskilt direkte under Michael-svaret når backend returnerer `sign_ids`.

## Verifisert arkitektur og avgrensning

- Produksjonsflaten er FastAPI + innebygd HTML/CSS/JavaScript i
  `backend/webapp.py`, ikke Next.js/Tailwind.
- `traffic_signs` er allerede source of truth med 316 språkdelte skilt, og
  `backend/sign_images/` inneholder over 300 lokale skiltbilder.
- Det opprettes derfor ikke et konkurrerende 20-skiltbibliotek under `public/`.
  Eksisterende data og bilder eksponeres gjennom additive API-kontrakter.
- Ingen endring i auth, gjeste-/gratis-/premiumgrenser, Stripe, RevenueCat,
  TTS-provider, deploy eller hemmeligheter.

## Patchplan

1. Komprimer lærerheaderen til maks 90 px, 64 px portrett, én statuslinje og
   grønn ONLINE-badge uten neon-glød.
2. Gjør svarflaten typografisk trygg uten avkuttet tekst, konteksthandlinger i
   2x2-grid og input/sendeknapp minst 56 px.
3. Utvid `/api/signs` additivt med `tag`-filter og legg til
   `GET /api/signs/{sign_id}` basert på eksisterende `traffic_signs`.
4. Utvid `/api/teacher/chat` additivt med `sign_ids`, utledet fra godkjent
   læreplankontekst. Eksisterende `reply` og `suggestions` bevares.
5. Render språkren SignCard under svarboblen: eksisterende skiltbilde, valgt
   språk, førerhandling/tips og tydelige handlinger. Flere ID-er blir en
   horisontal, scrollbar kortrekke.
6. «Øv på dette skiltet» bruker eksisterende webapp-flyt og URL-parameteren
   `?sign=<id>`; den må aldri late som filtrering lyktes dersom spørsmål mangler.

## Språk og tilgjengelighet

Kortet viser bare aktivt språk (NO, TH eller EN), selv om designreferansen viser
NO og TH samtidig. Dette bevarer Thai2Drive-kravet om full språkrenhet. Bilder
har alt-tekst, knapper får lokaliserte labels, og tekst-only fallback beholdes.

## Tester, risiko og rollback

- Målrettede kontrakttester for API, `sign_ids`, headerhøyde, 2x2 handlinger,
  SignCard-rendering og språkrenhet.
- Python-kompilering, relevante eksisterende tester, inline JavaScript-syntaks
  og `git diff --check`.
- Største risiko er variasjon i eldre MongoDB-poster; normalisering og
  bilde-/tekstfallback skal være fail-soft.
- Rollback er å reversere de additive sign-rutene, responsfeltet og SignCard/UI-
  blokken. Ingen data må migreres eller slettes.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT — godkjente norske skiltbilder i Michael

## Mål og ikke-mål

Når læreplankonteksten finner et konkret trafikkskilt med godkjent bilde, skal Michaels svar vise dette bildet med språkren bildetekst. Ingen frie AI-genererte bilder, ingen endring i TTS, auth, premium, Stripe, RevenueCat eller databaseformat. Norske veiscener er ikke del av første patch.

## Minste patch

1. Bygg skiltkontekst gjennom én liten helper som inkluderer en eksakt, godkjent bildetagg bare når URL og NO/TH/EN-navn finnes.
2. Stram multimedia-instruksen: bildetagger må kopieres fra godkjent kontekst; modellen skal aldri finne på URL-er.
3. Hvis modellen utelater en godkjent skilt-tagg, legg den deterministisk til svaret. Manglende bilde gir tekst-only fallback.
4. Bevar eksisterende frontend-renderer og API-kontrakt.

## Tester, risiko og rollback

Test godkjent URL, manglende oversettelse/bilde, deterministisk innsetting og at oppdiktede URL-er ikke introduseres. Kjør Python-syntaks, relevante teacher-tester og `git diff --check`. Risikoen er feil databasekobling mellom skilt og bilde; kilden forblir derfor eksisterende `traffic_signs.image_url`. Rollback er én avgrenset revert i `teacher_chat.py` og testen.

READY FOR AGENT 3

---
# SOLUTION BLUEPRINT: ett informasjonskort og to elevvalg

## Mål og ikke-mål

Målet er å gjøre Michaels skiltrespons kort og beslutningsklar. Skiltkortet blir
ren informasjon, mens neste steg samles i ett handlingsområde. Ingen endring i
backend, database, API-kontrakt, AI-prompt, TTS, auth eller betaling.

## Minste patch

1. I `backend/webapp.py` fjernes `tm-sign-actions` fra
   `_buildTeacherSignCard`.
2. Kortet viser én lokalisert, konkret tekst: `driver_action` når den finnes,
   ellers `explanation`, ellers eksisterende fallback.
3. Taggen forenkles ved å fjerne det unødvendige ordet «TEORI».
4. `_teacherAppendSignActions` reduseres til to knapper: lokalisert
   `practice_this_sign` og eksisterende lokalisert `ask_ai`. Spørreknappen
   fokuserer lærerens inputfelt.
5. CSS strammes inn på mobil slik at bilde og tekst passer uten indre knapper.
6. Kontrakttesten oppdateres med fravær av kortknapper og nøyaktig to
   konteksthandlinger.

## Verifisering og rollback

Kjør Python-/inline-JS-syntaks, målrettet UI-kontrakttest og visuell lokal
kontroll ved desktop og 390 px bredde. Rollback er å reversere disse få
frontend- og testlinjene. Ingen produksjonspublisering inngår.

READY FOR AGENT 3

---
# BLUEPRINT-OPPDATERING: ett neste steg og Michael i inputfeltet

Michael har forenklet retningen videre: kontekstområdet skal ha én handling,
«Øv på lignende», slik at ruten senere kan dekke både skilt og veikryss.
«Spør Michael» flyttes fra egen knapp til lærerinputets placeholder. Patchen
skal bruke nye, separate NO/TH/EN-nøkler og ikke endre den eksisterende
`practice_this_sign`-teksten i skiltbibliotekets detaljpanel.

READY FOR AGENT 3

---
