# QA GATE: Patch 2 — Michael-chat og visuelle media-kort

## Funksjon og kontrakt

- PASS: bare `active: true` og `approved_for_michael: true` vurderes.
- PASS: eksakt godkjent skilt-ID rangeres foran emne- og situasjonsknagger.
- PASS: responsen er bakoverkompatibel og legger kun til `media` med maksimalt
  to ressurser; eksisterende `sign_ids` er bevart.
- PASS: video må ha en aktiv kilde i `learning_videos`, og klienten får
  avspillings-URL-en fremfor et miniatyrbilde.
- PASS: manglende bibliotek, databasefeil eller manglende treff gir tom
  `media`-liste og stopper ikke Michaels tekstsvar.
- PASS: både vanlig chat og quiz-coach viser media under Michaels tekst.
- PASS: skilt og situasjonsbilder har begrenset høyde, høy kontrast, tittel,
  forklaring og énkolonne-layout på mobil.
- PASS: video har språkstyrt knapp på NO/TH/EN og åpnes i appens videospiller.
- PASS: lukking av video returnerer eleven til den opprinnelige skjermen.

## Språk og sikkerhet

- PASS: tittel og forklaring hentes bare fra aktivt NO-, TH- eller EN-felt;
  det finnes ingen norsk fallback inn i thai eller engelsk.
- PASS: en ressurs uten komplett tekst i elevens aktive språk blir utelatt.
- PASS: bare interne `/api/`-URL-er og HTTP(S)-URL-er returneres.
- PASS: URL-er genereres ikke av AI; kun admin-godkjente databaseverdier brukes.

## Automatiske kontroller

- Python-syntaks: PASS.
- Inline JavaScript-syntaks: PASS.
- 40/40 målrettede tester: PASS.
- `git diff --check`: PASS med kun ufarlige Windows LF/CRLF-varsler.
- Urelaterte lokale endringer i `context/FEATURES.md` og
  `content/video_scripts/` er ikke endret eller inkludert.

PASS — backend, frontend og mobilkontrakt er klare for commit/push og fersk
produksjonskontroll.

---

# QA GATE: Michael-materiale i adminpanelet

## Omfang og datakilde

- PASS: patchen er additiv og bruker en egen `michael_materials`-samling som
  refererer eksisterende `traffic_signs`, `learning_videos` eller godkjent
  situasjonsbilde-URL; eksisterende medier kopieres eller slettes ikke.
- PASS: administrator kan liste, filtrere, opprette, redigere og deaktivere
  referanser. Skilt- og videokilder tilbys fra eksisterende admin-API-er.
- PASS: Michael-chatten, lærerresponsen og learner-facing webappen er urørt i
  Patch 1. Materialet blir derfor ikke automatisk vist i samtaler ennå.

## Sikkerhet, språk og feiltilstander

- PASS: alle tre ruter krever `require_admin`.
- PASS: innkommende felter og materialtyper er allow-listet; ukjente felter,
  ugyldig type, usikker URL og manglende kilde avvises.
- PASS: en aktiv og Michael-godkjent post krever komplett tittel og forklaring
  på norsk, thai og engelsk, samt en forhåndsvisbar kilde.
- PASS: deaktivering endrer bare referansestatus og sletter ikke skilt, video
  eller bilde.
- PASS: auth-policy, elevkvoter, TTS, premium, Stripe, RevenueCat, hemmeligheter
  og betaling er urørt.

## Automatiske kontroller

- Python-syntaks: PASS.
- Inline JavaScript-syntaks: PASS.
- 22 målrettede admin-, skilt- og Michael-kontrakttester: PASS.
- `git diff --check`: PASS med kun ufarlige Windows LF/CRLF-varsler.
- `backend/teacher_chat.py` og `backend/webapp.py`: ingen diff.
- Lokalt skiltbibliotek: 313 bildefiler funnet; ingen av dem er endret.

## Restpunkt

- WARNING: det nye biblioteket er tomt frem til administrator oppretter de
  første referansene.
- WARNING: ekte MongoDB-oppretting og visuell innlogget adminflyt er ikke kjørt
  i denne lokale QA-runden. Det må kontrolleres etter en separat godkjent
  commit/deploy før produksjon kan kalles verifisert.

PASS WITH WARNINGS — Patch 1 er lokalt ferdig og avgrenset. Ingen commit, push
eller deploy er utført.

---

# QA REPORT: Fase 2B — Michael quiz-coach og readiness

## Readiness

- PASS: endpointet krever gyldig JWT og bruker serveridentitet.
- PASS: siste 50 individuelle svar leses på tvers av ny `user_id`-historikk og eldre tilknyttet `device_id`.
- PASS: formelen er eksakt 70 % nøyaktighet og 30 % feilbankmestring.
- PASS: ny bruker er 0; perfekt bruker uten feil kan nå 100; alle resultater klemmes 0–100.
- PASS: dashboardtersklene er 0–59 rød, 60–84 gul og 85–100 grønn.

## Michael quiz-coach

- PASS: feil svar aktiverer ordinær forklaring og Neste før AI-kallet starter.
- PASS: kontekst inneholder spørsmål, elevens faktiske svar, fasit og eksisterende forklaring.
- PASS: aktivt språk sendes eksplisitt; alle loading-, feil- og knapptekster finnes på thai, norsk og engelsk.
- PASS: 12-sekunders timeout og lokal fail-soft tekst hindrer at AI-feil stopper quizen.
- PASS: neste spørsmål eller navigasjon lukker panelet og avbryter utdatert kall.
- PASS: mini-practice fortsetter samme Michael-økt uten å bruke ordinært quiz-/kvotesvar.

## Mobil og tilgjengelighet

- PASS: panelet er responsivt, scrollbar og kan lukkes.
- PASS: innhold settes med `textContent`, ikke utrygg AI-generert HTML.
- PASS: dialogen bruker `aria-live`; lukkeknappen følger global språklabel.

## Regresjon og automatiske kontroller

- Python-syntaks: PASS.
- Inline JavaScript-syntaks: PASS.
- Målrettede tester: 12/12 PASS.
- Diff-format: PASS med ufarlig Windows LF/CRLF-varsel.
- Ingen endringer i auth-policy, access/consume, Stripe, RevenueCat eller premium-status.

## Live-port

Lokal QA er grønn. Etter push må Railway-versjonen matche committen, health/database være grønne, begge nye ruter være tilgjengelige og live HTML inneholde coach/readiness-kontrakten.

PASS — klar for commit, push og live-verifisering.

---

# QA REPORT: Michael mobilprofil og forenklet lærerflate

## Visuell kontrakt og mobil

- PASS: Michaels godkjente portrett er pakket lokalt og brukes i profilheader, startsidens Michael-valg, chat, quiz-coach og bunnmeny.
- PASS: mobil viser tre hovedemner først og har en språkstyrt knapp for å åpne/lukke resten.
- PASS: emneknapper, tekstfelt og sendeknapp har minst 50 px trykkhøyde.
- PASS: flaggbakgrunnen skjules kun i Michael-modus på mobil.
- PASS: desktop beholder alle emner synlige og eksisterende sidepanel.

## Språk og tilgjengelighet

- PASS: rolle, erfaring, «Flere emner» og «Vis færre» finnes separat på thai, norsk og engelsk.
- PASS: utvidelsesknappen oppdaterer `aria-expanded`.
- PASS: portrettbilder har alt-tekst og meldingene beholder eksisterende skjermleser-/chatstruktur.

## Regresjon

- PASS: JavaScript-syntaks kontrollert med Node.
- PASS: Python-syntaks kontrollert.
- PASS: alle 21 oppdagede tester består.
- PASS: eksisterende `/api/teacher/chat` er gjenbrukt og urørt.
- PASS: ingen endring i AI-modeller, TTS, auth, kvoter, Stripe, RevenueCat eller betalingslogikk.

## Produksjonsstatus

Lokal QA er grønn. Endringen er ikke commitet eller publisert i denne QA-fasen. Railway/live må verifiseres etter eksplisitt godkjenning av commit og push.

PASS — klar for visuell forhåndskontroll og deretter commit/push når Michael ber om det.
# QA REPORT: stabil lærerlyd og roligere Michael-mobilflate

## Rotårsak og lydstate

- PASS: samme aktive tekst følger fortsatt stopp/toggle-flyten.
- PASS: en annen svartekst stopper gammel avspilling og fortsetter til ny `src` og `play()` i samme `speakText()`-kall.
- PASS: monoton `_teacherAudioToken` gjør at en gammel avvist `play()`-promise ikke nullstiller nyere lyd.
- PASS: ended, error og `stopAllSpeech()` nullstiller aktiv lærer-tekst.
- PASS: TTS-URL, språkparameter og backend-kontrakt er uendret.

## Mobil og forslag

- PASS: bare forslag 1–3 er synlige som standard på skjermer opptil 767 px.
- PASS: forslag 4+ kan åpnes/lukkes med språkstyrt knapp og korrekt `aria-expanded`.
- PASS: desktop skjuler ikke `mobile-extra`, fordi skjuleregelen bare finnes i mobil-media query.
- PASS: mobilheader reduseres fra 152 til 132 px; portrettet beholdes med mindre mål.
- PASS: input og sendeknapp beholder 50 px mobilhøyde.

## Språk, tilgang og sikkerhet

- PASS: ingen ny learner-facing tekst; eksisterende `teacher_more_topics` og `teacher_fewer_topics` har thai, norsk og engelsk.
- PASS: guest/free/premium, `/api/auth/me`, quota og premiumstatus er urørt.
- PASS: AI-chat, TTS-backend, Stripe, RevenueCat og hemmeligheter er urørt.
- PASS: diffen omfatter bare `backend/webapp.py` og målrettet testfil; øvrige lokale rapportendringer er ikke applikasjonskode.

## Automatiske kontroller

- Python-syntaks: PASS.
- Inline JavaScript-syntaks: PASS.
- Michael-kontrakttester: 7/7 PASS.
- Full oppdaget testsuite: 24/24 PASS.
- Diff-format: PASS med ufarlig LF/CRLF-varsel.

## Restpunkt

Faktisk lydutgang kan ikke bevises av statiske tester. Etter eventuell deploy må Michael spille svar A, deretter svar B før A er ferdig, på brukerens ekte mobil. Ett trykk på B skal både stoppe A og starte B.

PASS WITH WARNINGS – koden er klar for Michaels vurdering; publisering og ekte mobil-lydtest er ikke utført.

---

# QA GATE: godkjente norske skiltbilder i Michael

## Kontroller

- Rotårsak: PASS — skiltets godkjente `image_url` følger nå samme databasepost inn i Michaels kontekst.
- Scope: PASS — kun lærerlogikk, smal test og agentrapporter er endret for funksjonen.
- Bildesikkerhet: PASS — bare databasegodkjent HTTP(S) eller `/api/sign-images/` aksepteres; oppdiktede bildetagger fjernes.
- Språk: PASS — bildetagg krever navn på norsk, thai og engelsk; ellers brukes tekst-only fallback.
- Feiltilstand: PASS — manglende bilde, usikker URL eller manglende oversettelse stopper ikke chatten.
- Tilgang og betaling: PASS — auth, guest/free/premium, Stripe og RevenueCat er urørt.
- Automatiske tester: 31 relevante tester PASS; Python-kompilering og diff-check PASS.
- Full backend discovery: WARNING — `test_thai2drive_api.py` kunne ikke importeres fordi lokal runtime mangler `pytest`.
- Manuell/live kontroll: WARNING — ikke utført fordi deploy ikke er autorisert i denne patchen.
- Hemmeligheter: PASS — ingen hemmeligheter eller konfigurasjonsverdier er lagt til.

PASS WITH WARNINGS — trygg for Michaels vurdering før commit/deploy. Restpunktene er pytest-miljø og visuell live-kontroll.

---

# QA GATE: kompakt Michael-side og datadrevne skiltkort

## Produkt og omfang

- PASS: headerkontrakten er 90 px og portrettet 64 × 64 uten neon-glow.
- PASS: de fire skiltrelaterte handlingene vises i 2 × 2-grid med én tydelig
  blå primærhandling og tre rolige sekundærhandlinger.
- PASS: input og tekstmerket sendeknapp er 56 px høye.
- PASS: Michael-modus viser bare Kategorier, Historikk og Michael i bunnmenyen.
- PASS: ingen nye dependencies, datamigrasjoner eller betalingsendringer.

## Skiltdata, språk og feiltilstand

- PASS: skiltkort hentes fra eksisterende MongoDB-kilde og godkjente lokale
  bilder, ikke fra oppdiktede eller dupliserte assets.
- PASS: SignCard leser bare aktivt NO/TH/EN-felt og har bilde-alt-tekst.
- PASS: `sign_ids` er additivt i lærerresponsen; tekst-only fallback beholdes.
- PASS: skiltspesifikk quiz har ingen urelatert fallback. Manglende treff blir
  derfor en ærlig tomtilstand.
- PASS: flere skilt blir en horisontal, scrollbar kortrekke.

## Automatiske kontroller

- Inline JavaScript-syntaks: PASS.
- Statiske UI-/API-kontrakter: PASS.
- To representative produksjons-ID-er med bilder og tre språk: PASS.
- Diff-format: PASS med ufarlige LF/CRLF-varsler.
- Python-kompilering via innebygd Codex-runtime: PASS.
- Målrettede Python-kontrakttester: 21/21 PASS.
- Hele oppdagede frontend-/kontraktsuiten: 30/30 PASS.
- Visuell lokal/live nettleserkontroll: WARNING — appen er ikke startet eller
  deployet i denne QA-runden.

PASS WITH WARNINGS — patchen er lokalt ferdig, men skal ikke publiseres før
visuell kontroll er kjørt i nettleser og deretter på ekte mobil.

---

# QA GATE: mockup-godkjent Michael-header

## Evidens

- PASS: faktisk headerrekkefølge matcher godkjent mockup — uendret Michael-
  portrett først, deretter navn og status.
- PASS: headeren forblir 90 px, portrettet 64 × 64 og ONLINE-badge ligger på
  samme statusrad uten neon-glow.
- PASS: assistentsvaret bruker full bredde; gjentatt 28 px avatar er skjult.
- PASS: norsk, thai og engelsk finnes separat for metadata, ONLINE, Send og
  alle fire handlinger.
- PASS: ingen endring i auth, gjeste-/gratis-/premiumgrenser, Stripe,
  RevenueCat, TTS-provider eller hemmeligheter.
- PASS: Python-kompilering, inline JavaScript-syntaks og `git diff --check`.
- PASS: 24/24 målrettede tester og 30/30 full oppdaget suite.
- WARNING: designmockupen er godkjent, men faktisk lokal/live HTML er ennå ikke
  visuelt skjermtestet i desktop, iOS og Android.
- WARNING: ingen commit, push eller deploy er utført.

PASS WITH WARNINGS — klar for Michaels vurdering; neste separate port er
visuell nettleserkontroll og eksplisitt publiseringsbeslutning.

## Lokal visuell kontroll 2026-08-30

- PASS: desktop-visning i Codex-nettleseren viser kompakt header, helt spørsmål,
  godkjent 50-skilt, handlingsområde, input/send og tre bunnfaner.
- PASS: mobilvisning ved 390 × 844 px viser 90 px header, synlig spørsmål og
  skiltkort, samt synlig input/send og bunnmeny.
- PASS: spørsmålet starter under headeren etter den avgrensede scrollrettingen.
- PASS: Python-kompilering, 24/24 målrettede tester og `git diff --check`.
- WARNING: generell `unittest discover` finner også `test_gemini.py`, som ikke
  kan importeres i den innebygde runtime fordi valgfri `google`-pakke mangler.
  De målrettede applikasjons- og kontrakttestene har ingen feil.
- WARNING: dette er lokal forhåndsvisning. Ingen commit, push, deploy eller
  verifisering på live `thai2drive.no` er utført.

PASS WITH WARNINGS — lokal webflate er klar for Michaels visuelle vurdering;
publisering krever en separat, uttrykkelig beslutning.

---
# QA GATE: kort skiltinfo og to klare neste steg

- PASS: bevist dobbelrendering er fjernet; skiltkortet inneholder ingen
  handlingsknapper.
- PASS: betydning/driver action vises én gang, med eksisterende språkstyrte
  NO/TH/EN-felt og fallback.
- PASS: bare to kontekstvalg rendres: øving og spørsmål til Michael.
- PASS: spørrevalget fokuserer eksisterende input; øvingsvalget beholder
  eksisterende skiltfiltrerte quizrute.
- PASS: 390 px mobilkontroll viser kortet uten horisontal overflow, med korrekt
  norsk metadata, sendetekst og de to handlingene.
- PASS: 25 målrettede tester, Python-syntaks og diff-format.
- PASS: auth, gjeste-/gratis-/premiumgrenser, Stripe, RevenueCat, TTS-backend,
  hemmeligheter og deploy er urørt.
- WARNING: lokal forhåndsvisning er ikke live produksjon og er ikke kontrollert
  på fysisk iOS/Android.

PASS WITH WARNINGS — klar for Michaels visuelle vurdering. Ingen publisering er
utført.

---
# QA GATE: én handling og Michael-placeholder

- PASS: kontekstområdet inneholder nøyaktig én knapp, «Øv på liknende».
- PASS: «Spør Michael» finnes i inputfeltet og ikke som egen knapp.
- PASS: nye learner-facing tekster finnes separat på norsk, thai og engelsk.
- PASS: skiltbibliotekets eksisterende `practice_this_sign` er uendret.
- PASS: lokal 390 px visning har ingen horisontal overflow.
- PASS: 25 målrettede tester, Python-syntaks og diff-format.
- WARNING: ikke publisert eller testet på fysisk mobil.

PASS WITH WARNINGS — klar for Michaels vurdering.

---
# QA GATE: vis/skjul Michael-emner

- PASS: hovedchatten viser ikke de gamle store startknappene.
- PASS: sidefeltet inneholder nøyaktig seks emner og er lukket som standard.
- PASS: panelet åpnes fra headeren og lukkes ved valg, bakteppe eller Escape.
- PASS: norsk, thai og engelsk har egne tekster for åpne/lukke-kontrollen.
- PASS: «Spør Michael...» og «Øv på liknende» er uendret.
- PASS: mobilkontroll ved 390 × 844 px viser lesbar hvit knappetekst uten
  horisontal overflow.
- PASS: 15 målrettede tester, Python-/JavaScript-syntaks og diff-format.
- PASS: backend, TTS, auth, premium, Stripe, RevenueCat og betaling er urørt.

GODKJENT LOKALT — klar for den uttrykkelig bestilte commit, push og deploy.

---
