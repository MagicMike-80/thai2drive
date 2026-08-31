# QA GATE RE-RUN: eksakt skilt og kompakt ordkobling i Michael-chat

## Endelig resultat

- PASS: de to tidligere blokkererne er rettet. Fallback-skiltkort krever nå
  et navn på aktivt språk før rendering, og den norske kontrollerte listen har
  både `vikepliktsskiltet` og `vikepliktskiltet` uten duplikat.
- PASS: en uavhengig 9-aliasmatrise verifiserte NO/TH/EN for `202_0`, `204_0`
  og `208_0`. En separat lokal retrieval-kjøring verifiserte for hver ID at
  resultatet er nøyaktig ett korrekt `type="sign"`-medium, uten generisk bilde,
  video eller annet skilt.
- PASS: negative latinske grenser hindrer falske eksplisitte treff som
  «stoppelengde» og «stop distance».
- PASS: bred flyt uten eksplisitt skilt beholder eksisterende maks-to-rangering
  og tekst-only fallback.
- PASS: `sign_ids` bruker eksplisitte ID-er når de finnes og eksisterende
  kontekst-ID-er ellers.
- PASS: materiale, skiltkontekst, kort, ordkobling og detaljpanel bruker bare
  aktivt NO/TH/EN. Manglende språkverdi feiler trygt uten norsk fallback.
- PASS: ordkoblingen bruker validerte strukturerte ID-er, tekstnoder og
  `textContent`; kort og første eksakte term åpner eksisterende
  `GET /api/signs/{id}` / `openSignDetail` og er tastaturtilgjengelige.
- PASS: begge skiltbildevariantene er maksimalt 90 x 90 px på desktop, mobil
  og quiz-coach. Mobilens Michael-tekst beholder minst `1.05rem` og
  `line-height:1.65`; signkortet introduserer ikke horisontal kortrekke.
- PASS: detaljen viser eksisterende skiltkode og aktivt språks korte regel.
  Fargekoder skjules fordi dagens autoritative API ikke leverer dem.
- PASS: auth, kvoter, premium, Stripe, RevenueCat, betaling, database,
  `backend/server.py`, admin, mobilapp og deploykonfigurasjon er urørt.
- PASS: `context/FEATURES.md` er ikke staged og skal fortsatt holdes utenfor
  commit som lokal-only sporingsfil.

## Verifisering etter retting

- 40/40 målrettede backend-/frontendtester: PASS.
- Hele sikre lokale `tests/`-suiten: 46/46 PASS.
- Uavhengig eksakt-ID-matrise: 9 språkaliaser og eksklusivt media for alle tre
  ID-er PASS.
- Python AST/syntaks: 147 filer PASS.
- Inline JavaScript-syntaks via Node: PASS.
- `git diff --check`: PASS; bare ufarlige Windows LF/CRLF-varsler.
- Diffbasert hemmelighetssøk: ingen nye nøkkel-, passord-, secret- eller
  privatnøkkelverdier.
- Ingen produksjons-POST, databaseendrende test, commit, push eller deploy ble
  utført av QA.

En faktisk innlogget mobilchat og Railway-visning må fortsatt kontrolleres som
liveverifisering etter godkjent publisering; dette er ikke en lokal
kodeblokkerer og produksjonsdata ble bevisst ikke mutert i QA.

**PASS — klar for Michaels vurdering og kontrollert commit/push/liveverifisering.**

---

# QA GATE: eksakt skilt og kompakt ordkobling i Michael-chat

## Resultat per krav

- PASS: NO/TH/EN-aliasmatrisen gir `202_0`, `204_0` og `208_0` for de
  målrettede uttrykkene. Latinske negative treff som «stoppelengde», «stop
  distance», «trafikkskilt» og bred «vikeplikt» blir ikke eksplisitte skilt-ID-er.
- PASS: eksplisitt skiltmodus filtrerer før rangering og returnerer maksimalt
  ett `type="sign"`-medium med nøyaktig samme ID. Generisk situasjonsbilde,
  video, rent tag-treff, annet skilt og fler-ID-skilt blir utelatt.
- PASS: spørsmål uten eksplisitt skilt beholder eksisterende rangerte
  maks-to-materialflyt. Tomt/utrygt/ufullstendig media faller tilbake til tekst.
- PASS: responsens `sign_ids` bruker eksplisitte ID-er når de finnes og dagens
  kontekstutledning ellers.
- PASS: backendmateriale og skiltkontekst krever aktivt språk; norsk tekst
  lånes ikke inn i thai eller engelsk.
- PASS: begge skiltbildetyper er låst til maksimum 90 x 90 px, mørkt kort,
  synlig tastaturfokus og ingen ny horisontal skrolling. Michaels mobile
  svartekst beholder `1.05rem` og `line-height:1.65`.
- PASS: sign-media og fallbackkort åpner eksisterende
  `GET /api/signs/{id}` / `openSignDetail`; modelltekst blir fortsatt bygget
  med tekstnoder/`textContent`, ikke usikker `innerHTML`.
- PASS: skiltkode og aktivt språks `driver_action`/`explanation` kommer fra
  eksisterende detalj-API. Fargekoder vises ikke fordi API-et mangler
  autoritativ fargemetadata; dekorative CSS-farger presenteres ikke som
  offisielle.
- PASS: diffen endrer ikke auth, kvoter, premium, Stripe, RevenueCat,
  betaling, `backend/server.py`, database eller deploykonfigurasjon.
- PASS: `context/FEATURES.md` er bare lokal sporing og må holdes utenfor
  staging/commit.

## Blokkerende funn til Agent 3

1. **Aktivt språk mangler, men fallbackkortet vises likevel.**
   `backend/webapp.py:9928` bruker `results.filter(Boolean)` og sender posten
   direkte til `_buildTeacherSignCard`. Kortbyggeren ved `backend/webapp.py:9883`
   krever ikke `_teacherSignValue(sign, 'name')`; den kan derfor vise bilde,
   nøytral ID og generell fallbacktekst samt åpne detaljpanelet selv om valgt
   NO/TH/EN-navn mangler. Dette bryter blueprintens fail-stop-krav om at
   koblingen/kortet skal skjules når aktiv språkverdi mangler. Filtrer tegnene
   på komplett nødvendig aktiv språkverdi før kortet bygges, og lås det med en
   målrettet kontraktstest.
2. **Norsk kontrollert ordkobling mangler en backend-godkjent variant.**
   `backend/webapp.py:9631` har `vikepliktsskiltet` to ganger, men mangler
   `vikepliktskiltet` (én `s`), mens backendresolveren godtar grunnformen
   `vikepliktskilt` og den bestemte formen gjennom `(?:et)?`. Dersom Michael
   bruker «vikepliktskiltet», returneres `202_0`, men ordet blir ikke klikkbart
   med dagens grensetest. Erstatt duplikatet med den manglende varianten og
   legg til en test som beviser koblingstermen.

## Uavhengige kontroller

- 39 målrettede backend-/frontendtester: PASS.
- Hele sikre lokale `tests/`-suiten: 45/45 PASS.
- Python AST/syntaks: 147 filer PASS.
- Inline JavaScript-syntaks via Node: PASS.
- `git diff --check`: PASS; bare Windows LF/CRLF-varsler.
- Diffbasert hemmelighetssøk: ingen nye nøkkel-, token-, passord- eller
  privatnøkkelverdier funnet.
- Ingen produksjons-POST, databaseendrende test, commit, push eller deploy er
  utført av QA.

Visuell 390 px-nettleserkontroll ble ikke brukt som erstatning for de to
blokkerende kontraktsfunnene. Etter retting må målrettede tester, full lokal
suite, syntaks og `git diff --check` kjøres på nytt.

**FAIL — send tilbake til Agent 3 med de to konkrete funnene over.**

---

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

# QA GATE: ett konkret Michael-svar

- PASS: sluttprompt og backendfilter begrenser norsk, thai og engelsk til ett
  konkret regelsvar på 1–2 setninger; norsk/engelsk er begrenset til 30 ord.
- PASS: overskrifter, ekstra avsnitt, spørsmål, mediatagger, HAV og
  «Kongen og tjeneren» fjernes også dersom modellen ikke følger prompten.
- PASS: `suggestions` er tom, og responsen kan bare inneholde ett godkjent
  mediaelement av typen `sign`.
- PASS: hovedchat og quiz-coach viser ingen svarmeny eller mini-practice-knapp.
- PASS: Python-syntaks og `git diff --check`.
- PASS: 60/60 lokale frontend-/kontrakttester og 39/39 trygge backendtester.
- MERKNAD: `backend/tests/test_thai2drive_api.py` ble ikke kjørt; den krever
  `pytest` som ikke finnes i den bundne runtime og er tidligere klassifisert
  som produksjonsrettet. Ingen produksjonsmuterende test ble forsøkt.

PASS — klar for commit, push og fersk live-verifisering.

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

# QA GATE: additiv `media_catalog`, Patch A

## Vurdert omfang

QA er utført mot gjeldende Pain Profile, blueprintens eksplisitte Patch A og
den faktiske arbeidsdiffen. Aktiv produksjonsseed av de ti mediene og overgang
av den synlige biblioteksiden er ikke del av Patch A.

## Skjema, språk og oppslag

- PASS: `backend/media_catalog.py` krever unik, ikke-tom `media_id` gjennom
  validering av manifestsettet og databaseindeksen `media_id_unique`.
- PASS: `type`, `category`, ikke-tomme normaliserte/unikke tags, sikre URL-er,
  boolsk `is_active`, komplett `i18n.no/th/en` og eksplisitt
  `content_language` valideres fail-stop.
- PASS: bare `https://` og avgrenset `/api/assets/` godtas i katalogskjemaet;
  generell `/api/`, `http://`, credentials, query/fragment på lokale assets og
  katalogtraversering avvises.
- PASS: serializer returnerer bare valgt `title`, `description` og `caption`.
  Den eksponerer verken `i18n` eller `content_language`, og en NO-fil skjules
  for TH/EN. `neutral` krever fremdeles separat metadata på valgt språk.
- PASS: rankeren bruker hele, normaliserte tagfraser, deterministisk tie-break
  og returnerer maksimalt ett katalogmedium.
- PASS: Michaels eksakte skiltregel er bevart. Eksplisitt skilt returnerer bare
  det eksisterende eksakte skiltmediet; katalogvideo/podkast komponeres ikke
  inn. Uten eksplisitt skilt er totalgrensen fortsatt to, hvorav maks ett er fra
  katalogen.
- PASS: katalogfeil og ugyldig råspråk feiler mykt uten norsk katalogfallback
  eller feil i lærerchatten.

## Bibliotek, JWT og frontend

- PASS: `GET /api/library/media` bruker uendret
  `Depends(get_current_user)`, krever eksakt `no|th|en`, returnerer tom katalog
  som `{language, media: []}` og bruker ikke klientlevert bruker-ID.
- PASS: bibliotekhelperen spør bare etter aktive poster for valgt eller
  uttrykkelig nøytralt filspråk og sorterer etter fast kategoriorden, video før
  podkast, lokalisert tittel og `media_id`.
- PASS: podkastkortet bygges med DOM/`textContent`, sikkerhetskontrollert URL og
  `<audio controls preload="none">`; ingen AI-tekst settes med `innerHTML`.
- PASS: eksisterende biblioteksides to endepunkter og auth-policy er uendret.
  Tom Patch A-katalog kan derfor ikke gjøre dagens bibliotek tomt.
- WARNING: lokal QA-runtime mangler `fastapi`, så den nye ruten kunne ikke
  kjøres gjennom en ekte ASGI-klient. Rute, JWT-avhengighet, 422-gren og
  serializerkall er dekket av statisk kontrakt, mens helperen er kjørt mot
  falsk samling. Fersk HTTP 200 for den nye JWT-ruten må verifiseres read-only
  etter deploy dersom en eksisterende sikker test-JWT finnes.

## Seed-gate og database

- PASS: `backend/seed_media_catalog.py` er dry-run som standard og validerer
  hele manifesten, nøyaktig ID-sett, låst type/kategori, språk og URL-policy før
  Mongo-klient kan opprettes.
- PASS: apply krever både `--apply` og eksakt `--confirm-db-name`; `MONGO_URL`
  og `DB_NAME` leses fra miljøet og logges ikke.
- PASS: apply verifiserer alle media-/thumbnail-URL-er med HTTP 200 og forventet
  video/audio/image-type før første databaseskriv.
- PASS: upsert bruker `{media_id}`, `$set` og `$setOnInsert`, hopper over
  identiske dokumenter, tar before-snapshot og inneholder ingen delete eller
  automatisk deaktivering av andre poster.
- PASS: to identiske falsk-DB-kjøringer ga først 10 upserts og deretter
  `modified=0`, `upserted=0`, `unchanged=10`.
- PASS: eksempelmanifesten er med hensikt tom og inneholder ingen dummy-URL-er,
  oppdiktede oversettelser eller aktive produksjonsposter. Lokal dry-run stoppet
  med alle ti manglende ID-er før databasekontakt, som forventet.
- PASS: startupindeksene er additive og oppretter unik `media_id` samt minimal
  aktiv/språk/tags-indeks. Ingen eksisterende samling migreres eller slettes.

## Uavhengige kontroller

- Målrettet katalog/Michael/frontend-suite: 31/31 PASS.
- Full trygg `tests/`-suite: 51/51 PASS.
- Trygge backendtester, eksplisitt uten `test_thai2drive_api.py`: 35/35 PASS.
- Python AST med eksisterende BOM-filer håndtert som `utf-8-sig`: 152 filer
  PASS.
- Inline JavaScript via `node --check`: 1/1 blokk PASS.
- `git diff --check`: PASS; bare varsler om framtidig LF/CRLF-konvertering.
- Egen trailing-whitespace-kontroll av seks nye/untracked filer: PASS.
- Hemmelighetsskann av applikasjonsdiffen: PASS; ingen URI, nøkkel eller privat
  nøkkel lagt til.
- Scope-audit: PASS. Ingen endring i authimplementasjon, kvoter, premium,
  Stripe, RevenueCat, betaling, TTS, quiz eller mobilkode.
- `context/FEATURES.md` er fortsatt lokal/unstaged og må uttrykkelig utelates
  fra commit i henhold til `AGENTS.md`.

## Blokkering og restverifikasjon

- **BLOCKED — aktiv produksjonsseed:** ingen av de ti bestilte postene kan
  seedes før innholdseier leverer og godkjenner eksakte media-/thumbnail-URL-er,
  komplette NO/TH/EN-tekster, kanoniske tags og dokumentert filspråk eller
  språkneutralitet. Seedverktøyet skal fortsette å stoppe frem til dette finnes.
- **BLOCKED — biblioteksideovergang:** `loadLibrary()` skal ikke kobles til den
  tomme katalogen før godkjent seed er verifisert idempotent og read-only på
  alle tre språk. Dagens bibliotek skal beholdes i Patch A.
- WARNING: ingen produksjonsdatabase, produksjonschat, commit, push eller deploy
  ble mutert av QA. Etter eventuell Patch A-deploy gjenstår `/api/health` og,
  dersom sikker JWT allerede finnes, read-only katalogrute på NO/TH/EN.

**PASS WITH WARNINGS — Patch A er production-sikker og klar for Michaels
vurdering/deploy. Patch B (aktiv seed og bibliotekovergang) er BLOCKED på
godkjent innholdsgrunnlag og må ikke fremstilles som levert.**

---
# QA GATE: rolig, sentrert Michael-chat — Patch 1

## Vurdert omfang

QA er utført mot siste chat-layoutseksjon i `PAIN_PROFILE.md`, den godkjente
to-patch-blueprinten, `PATCH_REPORT.md` og faktisk arbeidsdiff. Denne porten
gjelder bare Patch 1; biblioteksidens senere ombygging er ikke vurdert som
levert.

## Layout og eksisterende medieflyt

- PASS: eneste endrede produksjonsfil er `backend/webapp.py`. Ingen diff finnes
  i `server.py`, `teacher_chat.py`, auth, kvoter, premium, Stripe, RevenueCat,
  `media_catalog`, seed-skript eller databasekode.
- PASS: Michael-rammen er utvidet bare gjennom `#app.teacher-mode`, mens header,
  meldingsliste og eksisterende flex-composer deler
  `width:min(760px,100%)` og `margin-inline:auto`. Mobilreglene bruker 100 %.
- PASS: header/avatar er 72/48 px på desktop og mobil. Sidepanel og backdrop
  bruker samme 72 px top/inset, og eksisterende overlay/open/close/Escape-kode
  er ikke endret.
- PASS: `.teacher-chat-col` beholder flex-kolonnen og composer beholder
  `flex-shrink:0`, 56 px kontroller, safe-area og uten `position:fixed`.
- PASS: ordinær `.tm-media-strip` har én kolonne på alle breakpoints. Chatkolonne,
  rader, chips og sign-/mediestriper har lokale min-/maksbreddevern, og eksakte
  skiltbilder forblir 80/90 px.
- PASS: eksisterende ressursflyt er bevart: video kaller
  `_openTeacherMediaVideo(media)`, podkast bruker eksakt inline
  `<audio controls preload="none">`, og skilt åpner autoritativ skiltdetalj.
  Ingen ny learner-facing tekst eller språkfallback er lagt til.
- WARNING: det er ikke kjørt en ekte lokal nettleserkontroll ved 320, 390, 768
  og desktop i denne QA-runden. Statiske regler og kontrakter gir god støtte,
  men kan ikke alene bevise fysisk fravær av klipping eller mobiltastatur-overlapp.

## Portstopp: startscroll blir opphevet

- FAIL: `teacherSend()` kaller riktig nok `_teacherScrollToAnswerStart()` etter
  strukturert media og awaitet skiltkort. For vanlige svar kaller den deretter
  `_teacherAppendChips(data.suggestions)`, og `_teacherAppendChips()` avslutter
  fortsatt med `msgs.scrollTop = msgs.scrollHeight`. Forslagsraden flytter
  derfor leseren tilbake til listens absolutte bunn etter den nye helperen.
  Et langt svar uten den særskilte, senere bremsevideoen begynner fremdeles
  ikke i leseposisjonen, i strid med akseptansekriterium 4.
- FAIL: den nye testen kontrollerer at gammel bunnscroll er borte fra
  `_teacherAppendBubble()` og den asynkrone videoveien, men kontrollerer ikke
  `_teacherAppendChips()`. Dermed består kontrakttesten selv om hovedregresjonen
  fortsatt finnes.
- TIL AGENT 3: gjør én liten frontendrettelse slik at forslag/handlinger legges
  til før siste startscroll, eller fjern forslag-radens ubetingede bunnscroll og
  bruk én sluttplassering etter komplett svar. Legg en kontrakt som eksplisitt
  avviser `msgs.scrollTop = msgs.scrollHeight` i `_teacherAppendChips()` for
  svarflyten. Bevar bruker-/typing-scroll og øvrig scope.

## Uavhengige kontroller

- Full lokal `tests/`-suite: 54/54 PASS.
- Trygge backendtester, eksplisitt uten produksjonsmuterende
  `test_thai2drive_api.py`: 36/36 PASS.
- Python AST: 152 filer PASS.
- Inline JavaScript via `node --check`: PASS.
- `git diff --check`: PASS; kun varsler om framtidig LF/CRLF-konvertering.
- Hemmelighetsskann av tillagte difflinjer: PASS.
- `context/FEATURES.md` er lokal og skal fortsatt utelates fra commit som angitt
  i prosjektreglene.
- Ingen produksjonskall, commit, push eller deploy ble utført av QA.

**FAIL — send tilbake til Agent 3. Startscrollkravet er ikke oppfylt fordi
forslagsrenderingen fortsatt tvinger meldingslisten til bunnen.**

---

# QA RE-GATE: rolig, sentrert Michael-chat — Patch 1

## Retest av tidligere portstopp

- PASS: `_teacherAppendChips()` legger fortsatt forslagene til i DOM-en, men
  inneholder ikke lenger `msgs.scrollTop = msgs.scrollHeight`. Forslagsraden kan
  derfor ikke oppheve `_teacherScrollToAnswerStart()` etter et langt svar.
- PASS: den målrettede kontrakten avgrenser `_teacherAppendChips()` og krever
  både `msgs.appendChild(row)` og fravær av bunnscroll. Den låser også at
  awaitet skiltinnsetting skjer før startscroll, og at forslag legges til uten
  en senere scrollendring.
- PASS: brukerens egen melding og typingindikator beholder eksisterende
  bunnscroll. Bare assistentsvarets tidligere feilbane er endret.

## Full regresjons- og scopekontroll

- PASS: 72 px header, 48 px avatar, sentrert 760 px header/meldinger/composer,
  full mobilbredde, lokale overflowvern og én mediekolonne på alle breakpoints
  er fortsatt til stede.
- PASS: composer er fortsatt flex-bunnrad med `flex-shrink:0`, 56 px kontroller
  og safe-area, uten fixed/sticky-posisjonering.
- PASS: emnepanelet/backdrop er fortsatt overlay med 72 px inset; eksisterende
  åpne/lukke/Escape-logikk og historikk-/bunnnavigasjon er urørt.
- PASS: video bruker eksisterende spiller og returflyt, podkast spiller inline,
  skilt åpner autoritativ detalj, og kompakte skiltbilder er fortsatt 80/90 px.
- PASS: ingen learner-facing streng eller NO/TH/EN-logikk er endret. Ingen
  fallback til et annet språk er lagt til.
- PASS: eneste endrede produksjonsfil er `backend/webapp.py`. Ingen endring i
  backend-API, `teacher_chat.py`, auth, kvoter, premium, Stripe, RevenueCat,
  betaling, `media_catalog`, seed-data eller database.
- PASS: hemmelighetsskann av tillagte difflinjer fant ingen nøkkel, URI,
  passord eller privat token.
- MERKNAD: fysisk visuell kontroll ved 320, 390, 768 px og desktop er ikke kjørt
  i denne QA-runden. Den gjenstår som en ikke-blokkerende visuell kontroll før
  eller etter publisering; statiske layoutkontrakter og kodeaudit består.

## Uavhengige testresultater

- Målrettede layout-/mediakontrakter: 22/22 PASS.
- Full lokal `tests/`-suite: 54/54 PASS.
- Trygge backendtester, eksplisitt uten produksjonsmuterende
  `test_thai2drive_api.py`: 36/36 PASS.
- Python AST: 152 filer PASS.
- Inline JavaScript via `node --check`: PASS.
- `git diff --check`: PASS; kun varsler om framtidig LF/CRLF-konvertering.
- Ingen produksjonskall, commit, push eller deploy ble utført av QA.
- `context/FEATURES.md` må fortsatt utelates fra commit i henhold til
  prosjektregelen.

**PASS — tidligere portstopp er lukket. Patch 1 er klar for Michaels vurdering
og den uttrykkelig autoriserte publiseringsflyten.**

---

# QA GATE: 10-spørsmåls quizøkter

- PASS: backendstandard er `count=10`.
- PASS: vanlig quiz, daglig test, kategori og feilbank bruker én felles
  10-spørsmålsverdi; ingen `count=30` finnes i normal quizflyt.
- PASS: telleren starter på 1 av 10 og bruker faktisk øktlengde videre.
- PASS: eksisterende avslutning åpnes etter siste lastede spørsmål og viser
  både ny økt og Michael-knapp på NO/TH/EN.
- PASS: eksamen (45), skiltøving (1) og eksisterende access/consume er urørt.
- PASS: Python-syntaks, kontrakttester og diff-format.

PASS — klar for commit, push og live-verifisering.
