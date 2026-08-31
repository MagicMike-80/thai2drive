# PAIN PROFILE: adminpanelet er ikke ett samlet Michael-materialbibliotek

## Brukersmerte og forventning

Michael skal kunne vise et godkjent trafikkskilt, veikryss-/situasjonsbilde eller
en relevant video når det passer elevens samtale. Michael skal hente alt fra
Thai2Drive Admin, slik at Michael kan vedlikeholde materialet uten kodeendring og
uten at AI-en finner på medie-URL-er.

## Verifiserte observasjoner

- `backend/admin.html` har allerede separate adminflater for spørsmål,
  studiebok, trafikkskilt, videoer, podkaster og ordliste.
- `traffic_signs` har språkrene navn/forklaringer og `image_url`; skiltbildene
  finnes også lokalt under `backend/sign_images`.
- `learning_videos` har `topic_tags`, `sign_ids`, `sign_groups`, språk,
  sammendrag og aktiv-status. Studiebokkapitler kan ha `image_url` og
  `video_url`.
- `backend/teacher_chat.py::_get_curriculum_context()` søker i skilt,
  studiebokkapitler og videoer, og godkjente skiltbilder håndheves separat.
- `TeacherChatResponse` returnerer strukturert `sign_ids`, men ingen generell
  strukturert medieliste for veikryssbilder eller videoer.
- Veikryss-/situasjonsbilder kan finnes som spørsmåls- eller studiebokbilder,
  men har ikke én felles godkjent Michael-indeks med emne, situasjon, språk og
  aktiv-status.

## Bevist rotårsak

Materialet finnes i flere samlinger og adminfaner, men bare skilt har en
deterministisk strukturert vei helt fra treff til frontendkort. Veikryssbilder og
videoer mangler én felles, godkjent metadata- og responskontrakt. Derfor kan ikke
Michael sikkert og konsekvent knytte riktig materiale til samtalen.

## Omfang og risiko

Berørt er adminstyrt metadata, Michael-retrieval og rendering av godkjente
medier. Spørsmålsbank, originale skiltdata, TTS, auth, kvoter, premium, Stripe,
RevenueCat og betaling skal ikke endres. Største risiko er feil medietreff eller
språkblanding; tekst-only skal alltid være sikker fallback.

## Akseptansekriterier

1. Admin kan registrere og redigere godkjente skilt-, veikryssbilde- og
   videoreferanser med NO/TH/EN-tekst, tags, koblede skilt/situasjoner og aktiv.
2. Eksisterende skilt- og videofiler gjenbrukes; medieinnhold dupliseres ikke.
3. Michael får maks relevante, aktive og godkjente medier i en strukturert
   respons; AI-en kan ikke finne på URL-er.
4. Skilt treffes via `sign_id`; øvrige medier treffes via kontrollerte tags og
   situasjons-ID-er.
5. Valgt språk har komplett tittel/bildetekst, ellers skjules mediet.
6. Ingen treff eller mediefeil gir et normalt tekstsvar uten å blokkere chatten.
7. Tester dekker riktig treff, feil treff, språkisolasjon og deaktivert materiale.

Rotårsaken er bevist. Klar for Solution Architect.

---

# PAIN PROFILE: Michael, Mine feil og readiness

## Brukersmerte

Thai2Drive gir ordinær forklaring etter feil svar, men læringssløyfen stopper der. Feil blir ikke vedlikeholdt som en persistent, aktiv feilbank, dagens feilgjennomgang er skrivebeskyttet, og eleven får ikke en transparent readiness-score som bygger på den avtalte formelen.

## Verifiserte observasjoner

- `backend/webapp.py` lagrer spørsmålssvar i `_sessionAnswers` og sender hele økten til `POST /api/quiz-attempts` først når quizen avsluttes.
- Dagens «Øv på feil» rekonstruerer feil fra quizhistorikk og viser fasit/forklaring uten at eleven svarer på nytt. Den kan derfor ikke måle to riktige på rad eller mestre et spørsmål.
- Feil svar viser et lokalt, regelbasert AI-panel. Den eksisterende `POST /api/teacher/chat` brukes i den separate Michael-chatten, men kalles ikke automatisk fra feilpanelet.
- `backend/ai_learning.py` og `backend/ai_routes.py` har allerede `ai_attempts`, `ai_srs_cards`, smart practice og dashboardberegning, men webappen sender ikke svar til `POST /api/ai/attempt`.
- Eksisterende readiness-formel er 50 % nøyaktighet siste 30, 30 % kategoridekning og 20 % volum. Dette avviker fra ønsket 50/20/20/10 og mangler regelen om minst 20 svar.
- Eksisterende AI-læringsdata er knyttet til `device_id`; den etterspurte feilbanken skal være stabil per registrert bruker.

## Rotårsak

Funksjonene finnes som separate deler uten én felles, produksjonskoblet læringssløyfe. Historikk, AI/SRS og Michael-panelet har ulike datakilder og livssykluser.

## Sikker første leveranse

Første patch etablerer én serverstyrt, persistent feilbank for registrerte brukere og rene, testbare regler for feil, repetisjon og mestring. Den skal være additiv og skal ikke endre auth-, tilgangs-, betalings- eller quizkvotelogikk.

## Akseptansekriterier for første patch

1. Samme `question_id` kan bare ha én aktiv post per bruker.
2. Feil øker `wrong_count`, nullstiller `correct_streak` og reaktiverer spørsmålet.
3. Riktig svar i `mistakes`-modus øker `correct_streak`; to riktige markerer spørsmålet mestret.
4. Vanlig riktig svar endrer ikke feilbanken.
5. Eldre brukere uten feilbank håndteres uten migrasjon.
6. Automatiske tester dekker reglene og viser at auth, Stripe, RevenueCat og kvoter er urørt.

Rotårsaken er bevist. Klar for Solution Architect.

---

# PAIN PROFILE: vikepliktskilt vises ikke i Michael

## Live bevis

Et ferskt produksjonskall med «Forklar vikepliktskiltet og vis skiltet» returnerte ingen `[image:]`-tagg, men en ugyldig tom `[video: | ...]`-tagg. Databasen har samtidig skilt `202_0`, komplett NO/TH/EN-navn og gyldig bilde-URL.

## Rotårsak

Tekstbaserte skilt treffes etter studiebok og videoer i `_get_curriculum_context()`, men funksjonen returnerer bare `context_parts[:3]`. Når generelle ressurser allerede fyller listen, kuttes det konkrete skiltet og dets godkjente bildetagg bort.

## Akseptanse

Et konkret skilt-treff skal prioriteres foran generelle ressurser. «Vikepliktskilt» skal gi `202_0` og godkjent bilde; manglende treff skal fortsatt være tekst-only. Ingen frontend-, TTS-, auth- eller betalingsendring.

Rotårsaken er bevist. Klar for Solution Architect.
# PAIN PROFILE: Michael mister lyd på svar nummer to og mobilflaten er fortsatt tett

## Brukerens smerte og forventet oppførsel

På Michael-siden virker første avspilling, men lydknappen på neste svar kan bli stille. På mobil fyller profilheader, et langt svar og fire kontekstknapper nesten hele skjermen. Forventet oppførsel er at hver ny lydknapp starter riktig svar med ett trykk, og at neste naturlige handling alltid er tydelig og lett å nå.

## Verifiserte observasjoner

- Produksjonens `/api/tts/status` rapporterer ElevenLabs og Google som operative, uten åpen circuit breaker.
- To sekvensielle norske kall til `/api/tts/stream` returnerte HTTP 200, `audio/mpeg`, MP3-header `ID3` og henholdsvis 36 407 og 37 661 byte via ElevenLabs. Backend er derfor ikke årsaken til akkurat denne andre-avspillingsfeilen.
- `backend/webapp.py:8638-8640`: når `_teacherTtsPlaying` er sann, kaller `speakText()` `stopAllSpeech()` og returnerer. Et trykk på lydknappen for et nytt svar stopper derfor bare forrige/stale avspilling og starter ikke den nye.
- `backend/webapp.py:9394-9412`: `_teacherAppendChips()` viser alle forslag den mottar. Den sporer ikke en mobilgrense eller «flere»-tilstand.
- `backend/webapp.py:3183`: `.tm-chips` er en egen komponent. Mobilkollapsen ved `backend/webapp.py:3241-3242` gjelder bare `.teacher-suggestions`, ikke `.tm-chips`. Derfor viser skjermbildet fortsatt fire store temaknapper.
- Skjermbildet viser at den nye profilheaderen fungerer, men kombinasjonen av 152 px header, stor svarboble, fire forslag og fast input gir lite arbeidsrom på en 390 px bred telefon.

## Rotårsak

**BEVIST for lydtilstanden:** avspilleren skiller ikke mellom «samme lyd som skal stoppes» og «ny lyd som skal erstatte forrige». Den globale `_teacherTtsPlaying`-flaggen gjør at første trykk på lyd nummer to kan bli brukt kun som stoppkommando.

**BEVIST for layouten:** den tidligere 3-knappers patchen kollapser bare startforslagene. Kontekstforslag etter et Michael-svar bygges av en annen funksjon og omgår regelen.

## Omfang og risiko

- Berørt: Michael-chat på mobil, spesielt når elev går raskt videre før forrige tale er ferdig.
- Ikke berørt: TTS-leverandør, stemme-ID, `/api/tts/stream`, AI-chat, quiz, auth og betaling.
- Risiko ved feil patch: samme lydknapp kan miste pause/stopp-oppførsel, eller nytt svar kan spille samtidig med gammelt.

## Akseptansekriterier for neste patch

1. Trykk på lyd for svar A starter A.
2. Mens A spiller, trykk på lyd for svar B stopper A og starter B i samme brukertrykk.
3. Trykk på lyd for den samme aktive svarboblen stopper den uten å starte på nytt.
4. `ended`, `error`, navigasjon og skjul av side nullstiller aktiv tekst og avspillingsflagg.
5. Mobil viser maksimalt tre kontekstforslag først; øvrige forslag kan åpnes eksplisitt.
6. Chatmeldinger beholder mesteparten av skjermhøyden, mens input og sendeknapp forblir synlige og minst 48 px høye.
7. Norsk, thai og engelsk bruker samme logikk uten språkblanding.
8. Backend, AI-modell, auth, Stripe og RevenueCat forblir urørt.

## Handoff

Klar for Solution Architect. Anbefalt avgrensning er én frontend-only patch: spor aktiv lærer-tekst/source og bytt lyd atomisk; begrens kontekstchips på mobil med en lokal utvidelsesknapp; komprimer headeren moderat uten å endre portrettet.

---

# PAIN PROFILE: Michael forklarer skilt uten riktig norsk skiltbilde

## Brukersmerte og forventning

Når Michael forklarer et konkret trafikkskilt, ser eleven bare tekst og emoji. Eleven forventer at det faktiske norske skiltet vises sammen med forklaringen, på valgt språk.

## Verifiserte observasjoner

- `backend/webapp.py` kan allerede gjengi `[image: ...]` som et mobiltilpasset bildekort.
- `backend/teacher_chat.py::_get_curriculum_context()` henter relevante `traffic_signs`, men sender bare navn, forklaring og førerhandling til modellen.
- Skiltene har `image_url`, og repoet inneholder 313 lokale skiltfiler som serveres via `/api/sign-images/`.
- Multimedia-prompten tillater bildetagger, men krever ikke at URL-en kommer fra godkjent læreplankontekst.

## Bevist rotårsak

Den godkjente bilde-URL-en følger ikke skiltet inn i Michaels læreplankontekst. Modellen kan derfor ikke velge bildet sikkert, selv om både skiltbildet og frontend-rendereren finnes.

## Avgrensning og akseptanse

Første patch gjelder konkrete norske trafikkskilt. Den skal bare bruke godkjent `image_url`, aldri finne på URL-er, vise språkrene bildetekster og falle tilbake til tekst hvis bildet mangler. Veiscener krever et separat kuratert bibliotek. TTS, auth, kvoter og betaling skal være urørt.

Rotårsaken er bevist. Klar for Solution Architect.
# PAIN PROFILE: dupliserte skiltvalg og for mye tekst i Michael

## Brukersmerte

På mobil gjentas «Øv på dette skiltet» og «Se lignende» både inne i skiltkortet
og i handlingsområdet under. Kortet gjentar også betydningen som forklaring og
tips. Eleven må derfor lese og velge mellom for mange like elementer før neste
steg blir tydelig.

## Verifiserte observasjoner og rotårsak

- `backend/webapp.py::_buildTeacherSignCard` bygger forklaring, tips og to egne
  knapper i selve kortet.
- `backend/webapp.py::_teacherAppendSignActions` bygger deretter fire nye
  knapper under samme svar, inkludert de to samme handlingene.
- `teacherSendMessage` kaller begge funksjonene for samme `sign_ids`-respons.

Rotårsaken er derfor bevist: samme svar har to uavhengige handlingsrenderere,
mens kortets forklaring og driver action kan gjenta samme budskap.

## Omfang og risiko

Berørt flate er bare Michaels skiltkort og konteksthandlinger i web-frontend.
API, skiltdata, språkvalg, auth, kvoter, premium, TTS og betaling er ikke berørt.

## Akseptansekriterier

1. Skiltkortet viser kun godkjent bilde, lokalisert skiltkode/gruppe, navn og én
   kort, konkret forklaring/handling.
2. Ingen knapper vises inne i skiltkortet.
3. Under svaret finnes nøyaktig to valg: «Øv på dette skiltet» og «Spør Michael»,
   med tilsvarende rene thai- og engelsktekster.
4. Begge knappene fungerer, mobilkortet passer innenfor bredden, og tekst-only
   fallback for svar uten `sign_ids` beholdes.

Handoff til Agent 2: utform én smal frontendpatch uten API-endring.

---
