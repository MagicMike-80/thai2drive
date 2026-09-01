# PAIN PROFILE: skiltord i Michaels avklaringsliste er ren tekst

## Brukersmerte og forventet oppførsel

Etter at eleven velger «Forklar en trafikkregel», viser Michael blant annet
«Vikepliktskilt», «Stoppskilt» og «Rundkjøring». Eleven forventer at
konkrete skiltord har et lite korrekt skiltbilde og kan åpne skiltet. I live-UI
er hele listen bare tekst.

## Verifiserte observasjoner

- Fersk produksjonskontroll av deploy `2026-09-01-31357c04` viste svaret
  `Høyreregelen 🛑 Vikepliktskilt 🔴 Stoppskilt ⭕ Rundkjøring 🚶 Gangfelt`,
  men ingen klikkbare `.tm-sign-term`-elementer.
- Den samme live-forespørselen til `/api/teacher/chat` returnerte
  `sign_ids=[]` og `media=[]` for `Forklar en trafikkregel`.
- `backend/webapp.py` kobler bare ord via
  `_teacherLinkSignReferences(assistantBubble, data.sign_ids || [])` og bygger
  bare mediakort fra `data.media`. Frontend har derfor ingen autoritativ ID den
  kan bruke for denne listen.
- `backend/teacher_chat.py` ber modellen skrive fem avklaringsvalg som fri
  svartekst. `_explicit_sign_ids_for_message()` analyserer bare elevens
  inngående melding, ikke de konkrete skiltordene Michael legger i svaret.
- Kontrollgruppen `Hjelp med vikeplikt` kan returnere `sign_ids=["202_0"]` og
  ett fungerende skiltmedium. Bilde-API og selve kortkomponenten fungerer derfor;
  feilen er i koblingskontrakten for den brede avklaringslisten.

## Rotårsak

**BEVIST:** Frie skiltord i Michaels avklaringssvar har ingen strukturerte
ressurs-ID-er. Frontend er med hensikt avhengig av `sign_ids`/`media` og skal
ikke gjette skilt fra tekst. Resultatet blir korrekt, men ikke klikkbar ren tekst.

## Omfang og risiko

- Berører brede innganger som «Forklar en trafikkregel» og andre svar der
  Michael nevner flere valg uten strukturerte ID-er.
- Eksakte skiltspørsmål fungerer og må ikke regresjonstestes bort.
- En løsning må skille regler uten skilt (for eksempel Høyreregelen) fra
  konkrete skilt og ikke koble feil ID til generelle begreper.
- Språkrenhet NO/TH/EN og maksimum for antall media må bevares.

## Akseptansekriterier for neste lille patch

1. Brede avklaringsvalg leveres som strukturerte, språkrene valg med eksplisitt
   `sign_id` bare når valget faktisk er et konkret skilt.
2. Vikepliktskilt og Stoppskilt viser korrekt lite bilde og er klikkbare;
   Høyreregelen forblir et regelvalg uten oppdiktet skilt.
3. Ingen tilfeldig katalograngering kan vise et irrelevant skilt for
   «Forklar et skilt» eller «Forklar en trafikkregel».
4. Eksakte skiltspørsmål beholder ett korrekt kort, og NO/TH/EN testmatrise er
   grønn på mobil og desktop.
5. Ingen endring i portrett, auth, betaling, database eller deploykonfigurasjon.

---

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

# PAIN PROFILE: eksakt skilt og kompakt ordkobling i Michael-chat

## Brukersmerte og forventet oppførsel

Når Michael nevner ett konkret skilt, skal eleven bare se dette norske skiltet:
`202_0` for vikeplikt, `204_0` for stopp og `208_0` for forkjørsveg. Et
generisk veikryssbilde eller et annet skilt skal ikke følge med. Skiltet skal
være et lite, lesbart kort/badge (maksimalt 90 px), og skiltnavnet i svaret skal
kunne åpne kort offisiell skiltinformasjon på aktivt språk (NO, TH eller EN).

Målmappe og berørt flyt er `backend/teacher_chat.py` sitt
`POST /api/teacher/chat`-svar og Michael-renderingen i `backend/webapp.py`.

## Verifiserte observasjoner

- `backend/teacher_chat.py:991-1003` har en eksplisitt aliasresolver, men den
  dekker bare vikeplikt (`202_0`). En lokal, ikke-muterende reproduksjon ga tom
  liste for «stoppskilt», «stop sign», `ป้ายหยุด`, «forkjørsvei», «priority
  road» og `ถนนสายหลัก`. Skiltdataene i repoet identifiserer stopp som `204_0`
  og forkjørsveg som `208_0`.
- `backend/teacher_chat.py:1061-1125` gir 1000 poeng til eksakt skiltkobling,
  men filtrerer ikke bort andre materialer når `exact_sign_ids` finnes. Et
  ordinært emne-/situasjonstreff kan derfor fylle plass nummer to.
- Den eksisterende kontrakttesten
  `backend/tests/test_michael_material_retrieval.py:77-93` låser faktisk den
  uønskede oppførselen: et eksakt `202_0`-skilt returneres sammen med
  `tag-first`. Den målrettede testen passerte lokalt og bekrefter dagens
  kontrakt, ikke ønsket produktatferd.
- `backend/teacher_chat.py:1626-1633` sender alle skilt-ID-er som kan utledes fra
  læreplankonteksten videre som `exact_sign_ids`. For brede treff er dette ikke
  nødvendigvis det samme som et skilt eleven uttrykkelig nevnte.
- `backend/webapp.py:3299-3309` viser det strukturerte fallback-skiltkortet med
  200 x 200 px bilde på desktop. Mobilregelen i `backend/webapp.py:3365-3369`
  bruker 96 x 96 px. Begge overskrider ønsket maksimum på 90 px.
- Når godkjent media inneholder skiltet, brukes i stedet
  `backend/webapp.py:3314-3328`: skiltbildet ligger i en 180 px høy medieflate,
  160 px på mobil. `teacherSendMessage` undertrykker samtidig fallbackkortet
  for samme `sign_id` (`backend/webapp.py:9982-9986`). Resultatet er at den
  største av de to skiltvariantene ofte vinner.
- `backend/webapp.py:9312-9440` gjengir ordinære svaravsnitt med `textContent`.
  Det finnes ingen strukturert kobling mellom navn i svaret og `sign_ids`.
  Verken skilt-mediekortet (`9635-9698`) eller fallback-skiltkortet
  (`9750-9784`) åpner skiltdetaljer ved klikk.
- Eksisterende `GET /api/signs/{sign_id}` returnerer ID/kode, gruppe,
  språkdelte navn, forklaring og `driver_action`
  (`backend/server.py:1965-1995`). API-kontrakten har ikke et felt for
  offisielle fargekoder. `SIGN_GROUP_META` i webappen er presentasjonsfarger,
  ikke dokumenterte offisielle skiltfarger, og må ikke fremstilles som det.
- Språkisolasjonen i denne kjeden er allerede sterk: materialtekst krever
  eksakt `lang` (`backend/teacher_chat.py:1037-1042`), skiltkortet velger bare
  `appLang` (`backend/webapp.py:9604-9605`), og detaljpanelets `_getProp`
  nekter språkfallback (`backend/webapp.py:10307-10313`).

## Bevist rotårsak

Rotårsaken er en kombinasjon av tre smale kontraktsgap:

1. Eksplisitt begrepsmatching er ufullstendig og dekker bare `202_0`.
2. Materialrangeringen prioriterer et eksakt skilt, men håndhever ikke
   eksklusivitet; generisk tag-media kan fortsatt returneres.
3. Frontend har to separate skiltgjengivere uten felles kompakt grense eller
   tekstkobling. Det eksisterende detalj-API-et blir ikke brukt fra svaret.

Dette er **BEVIST lokalt**. Produksjonschat er ikke kalt, fordi et slikt POST-kall
oppretter samtale-/loggdata. Ingen påstand om fersk produksjonsatferd gjøres her.

## Omfang, risiko og ukjent

- Berørt: eksakt skiltutledning, filtrering av godkjent Michael-media og
  skiltpresentasjon/-kobling i webchat og den delte quiz-coach-rendereren.
- Skal ikke berøres: auth, gjeste-/gratiskvoter, premium, Stripe, RevenueCat,
  betaling, TTS, databaseinnhold eller mobilappen.
- Hovedrisiko: substring-aliaser kan gi falske treff; koblingen må derfor bruke
  en liten eksplisitt NO/TH/EN-tabell og strukturerte `sign_ids`, ikke fri
  fuzzy matching eller modellgenererte URL-er.
- Hovedrisiko for språk: en ny detaljlabel eller fallback må finnes i alle tre
  språk, ellers skjules den. Norsk fallback i thai/engelsk er ikke tillatt.
- **IKKE BEVIST / datagap:** autoritative «offisielle fargekoder» finnes ikke i
  dagens sign-API eller dokumenterte skiltmetadata. Agent 2 må bruke en allerede
  godkjent kilde dersom den finnes utenfor denne flyten, eller definere fail-stop
  (skjul feltet) fremfor å merke UI-/hex-farger som offisielle.

## Akseptansekriterier for Solution Architect

1. Eksakte NO/TH/EN-aliaser for vikeplikt, stopp og forkjørsveg gir henholdsvis
   bare `202_0`, `204_0` og `208_0`; tester dekker minst ett uttrykk per språk.
2. Når en eksplisitt skilt-ID finnes, returnerer `media` maksimalt ett
   `type=sign`-element med samme ID. Ingen `intersection_image`, video, annet
   skilt eller rent tag-treff returneres i samme svar.
3. Brede spørsmål uten eksplisitt skilt («forklar vikeplikt», «trafikkskilt»)
   beholder dagens godkjente, begrensede mediaflyt og tekst-only fallback.
4. Backend fortsetter å være source of truth. Frontend bruker bare strukturerte
   `sign_ids`/`GET /api/signs/{id}` og sikre URL-er; ingen HTML fra modellen
   gjøres klikkbar.
5. Alle skiltbilder i Michael-chat/quiz-coach er `max-width:90px` og
   `max-height:90px`, også når skiltet kom via `media`, på desktop og mobil.
   Kortet er mørkt, kompakt, tastaturtilgjengelig og lar teksten ha hovedfokus.
6. Det lokaliserte skiltnavnet i svaret utheves bare ved en eksakt, strukturert
   navnematch og åpner samme detalj som skiltkortet. Manglende navnematch gir et
   klikkbart kort uten å omskrive svaret.
7. Detaljen viser skiltkode/nummer og kort `driver_action` eller `explanation`
   kun på aktivt språk. Fargekoder vises bare fra autoritativ metadata; ellers
   skjules feltet eksplisitt.
8. Mobiltekst beholder minst dagens `1.05rem` og `line-height:1.65`; ingen ny
   horisontal scrolling eller dupliserte skiltkort introduseres.
9. Målrettede retrieval-, frontendkontrakt-, NO/TH/EN-, syntaks- og
   `git diff --check`-tester passerer uten produksjonsmuterende kall.

## Handoff til Agent 2

Utform én liten backend- og frontendpatch rundt aliasresolveren,
materialfilteret og eksisterende skiltkort/detalj-API. Unngå ny database,
skjemamigrasjon, generisk fuzzy matching og redesign av Michael eller
skiltbiblioteket.

---

# PAIN PROFILE: strukturert `media_catalog` mangler godkjent seedgrunnlag

## Brukersmerte og forventet oppførsel

Michael og biblioteket skal hente aktive, kvalitetssikrede videoer og podkaster
fra én strukturert MongoDB-katalog. Oppslag skal være deterministiske på emnetags,
Michael skal returnere maksimalt ett relevant medium, og elevtekst skal komme
utelukkende fra valgt språk (`no`, `th` eller `en`). Bibliotekets nye
`GET /api/library/media` skal kreve gyldig JWT.

Målmappen er denne rene worktreen. Berørt flyt er MongoDB-oppsett og ruter i
`backend/server.py`, retrieval/respons i `backend/teacher_chat.py`, bibliotek-
og Michael-rendering i `backend/webapp.py`, samt et nytt idempotent seed-skript.

## Verifiserte observasjoner

### Database og indekser

- `backend/server.py:36-45` oppretter én Motor-klient fra `MONGO_URL` og velger
  `DB_NAME`, med `thai2drive` som fallback. `backend/teacher_chat.py:29-35`
  oppretter i dag en separat Motor-klient med samme miljømønster.
- Søk i repoet finner ingen samling, modell, rute, test eller seed-ID med navnet
  `media_catalog`. Et ferskt read-only produksjonskall til
  `GET /api/library/media` returnerte HTTP 404.
- `backend/create_indexes.py:27-168` er den sentrale, idempotente indekslisten og
  kalles ved startup fra `backend/server.py:5649-5660`. Den har ingen indeks for
  mediekatalog. Dermed finnes verken unik `media_id`-garanti eller en dokumentert
  indeks for aktive type-/kategori-/tagoppslag.

### Auth og språkkontrakter

- Den etablerte JWT-avhengigheten er `get_current_user` i
  `backend/server.py:402-408`. Frontendens `api()` legger automatisk til Bearer-
  token når brukeren er innlogget (`backend/webapp.py:6043-6046`). Dette kan
  gjenbrukes uten å endre authlogikken.
- De eksisterende bibliotekrutene `GET /api/learning-videos` og
  `GET /api/learning-podcasts` er offentlige og bruker et valgfritt
  `language`-filter (`backend/server.py:4934-4951`). De returnerer fortsatt alle
  språkfeltene i dokumentet og grupperer ikke etter kategori.
- `backend/teacher_chat.py:915-919` har en nyttig fail-stop-hjelper som bare
  leser eksakt suffiksfelt (`title_no`, `title_th`, `title_en`). Den nye
  spesifikasjonen bruker i stedet `i18n.<lang>.title/description`, og ingen
  eksisterende kode leser denne formen.
- Chat-input bruker feltet `language`, ikke `user_language`
  (`backend/teacher_chat.py:1598-1602`), og ugyldige verdier faller i dag tilbake
  til norsk (`backend/teacher_chat.py:1620-1622`). Dette er ikke en trygg
  kontrakt for et nytt språkisolert katalogoppslag; et katalogmedium må skjules
  eller forespørselen avvises når valgt språk ikke er komplett.

### Tre parallelle mediesystemer

- Videoer ligger i `learning_videos` med `id`, `youtube_url`/`file_path`,
  `thumbnail_url`, `language`, `topic_tags` og `active`
  (`backend/server.py:4535-4559`). Podkaster har en tilsvarende, men separat
  modell i `learning_podcasts` (`backend/server.py:4842-4862`).
- Godkjente Michael-referanser ligger separat i `michael_materials`.
  `_get_relevant_michael_materials()` leser bare denne samlingen
  (`backend/teacher_chat.py:1067-1080`) og kan returnere `sign`,
  `intersection_image` eller `video`, men ikke `podcast`
  (`backend/teacher_chat.py:1100-1102`).
- `get_relevant_resources()` søker de gamle video-/podkast-samlingene og legger
  treff inn i modellprompten (`backend/teacher_chat.py:1417-1488`), men denne
  funksjonen fyller ikke det strukturerte `media`-feltet i responsen. Det
  strukturerte feltet kommer fortsatt fra `michael_materials`
  (`backend/teacher_chat.py:1665-1677,1876-1883`).
- Frontendens Michael-kort avviser `podcast` eksplisitt; bare `sign`,
  `intersection_image` og `video` godtas (`backend/webapp.py:9762-9765`).
- Biblioteket henter fortsatt to offentlige endepunkter parallelt
  (`backend/webapp.py:5314-5340`) og forventer de gamle feltene i
  `buildVideoCard()` og `buildPodcastCard()`
  (`backend/webapp.py:7942-7965,8877-8901`). En ny katalogrespons kan derfor
  ikke kobles inn uten en liten eksplisitt adapter eller rendererendring.

### URL-validering

- Dagens URL-kontroll i Michael-flyten er bare prefiksbasert og godtar enhver
  `/api/`, `http://` eller `https://`-verdi
  (`backend/teacher_chat.py:1054-1056`; tilsvarende i
  `backend/server.py:4700-4703`). Den beviser ikke at ressursen finnes, er et
  tillatt medieformat eller er kvalitetssikret.
- Et ferskt read-only produksjonsoppslag viste 60 aktive videodokumenter og fem
  aktive podkastdokumenter. Flere relevante lokale medier svarer HTTP 200, blant
  annet `video_mestre_hav_regelen.mp4`, `video_vegtrafikkloven_3.mp4`,
  `video_mestring_vikeplikt.mp4`, `video_offisielle_trafikkskilt.mp4`,
  `video_th_klum_pai_norway.mp4`, `podcast_bremselengde.m4a` og
  `podcast_konge_eller_tjener.m4a` via `/api/assets/`.
- Automatisk avledede thumbnails som
  `/api/assets/thumbs/thumb_video_mestre_hav_regelen.jpg` returnerte HTTP 404.
  Den faktiske filen heter
  `/api/assets/thumbs/thumb_mestre_hav_regelen.jpg` og returnerte HTTP 200.
  Seedingen kan derfor ikke stole blindt på dagens avledningsregel i
  `backend/server.py:4565-4574`.

### Seed-data og det kritiske datagapet

- Ingen av de ti bestilte ID-ene (`vid_stopp_01` til `vid_skilt_02`) finnes i
  repoet eller den read-only katalogresponsen fra produksjon.
- Oppgaven oppgir bare norske arbeidstitler. Obligatoriske beskrivelser og
  godkjente titler på thai og engelsk er ikke levert. I henhold til
  `AGENTS.md` tilhører oversettelser og pedagogisk innhold den andre agenten;
  de skal ikke oppdiktes i en kodepatch.
- Lokale filer kan ligne enkelte ønskede temaer, men de beviser ikke en
  en-til-en-kobling til de ti spesifiserte titlene. Det finnes for eksempel
  HAV-, vikeplikt-, skilt- og bremselengderessurser, men ingen verifisert fil for
  hver av de tre stoppelengdevideoene, videoen om myke trafikanter og buss eller
  videoen «Stoppskilt vs. Vikepliktskilt».
- Dagens medier har et eget `language`-felt, og filnavnene viser separate norske
  og thailandske varianter. Det foreslåtte nye skjemaet har derimot bare én
  `media_url` per dokument. `i18n` isolerer metadata, men kan ikke isolere selve
  talen/teksten i en språkbærende video eller podkast. Engelsk medieinnhold er
  heller ikke dokumentert som tilgjengelig.
- Eksisterende seedere hopper over etter `file_path`, bruker hardkodet
  `DB_NAME = "thai2drive"` og kan laste en lokal `.env`
  (`backend/scripts/seed_videos_v1.py:11-24,303-327` og
  `backend/scripts/seed_podcasts_v4.py:11-24,131-152`). Dette er idempotent for
  innsetting, men er ikke en komplett katalog-upsert og gir ikke en sikker
  forhåndsvalidering av alle dokumenter før første databaseendring.

## Bevist rotårsak

**BEVIST:** Thai2Drive har tre separate mediekontrakter uten `media_catalog` som
felles source of truth. Michael-returneringen, promptressursene og biblioteket
leser ulike samlinger og ulike feltskjemaer. Podcast kan ikke gjengis i Michaels
strukturerte kort i dag.

**BEVIST produksjonsblokker:** De ti nye postene mangler autoritativ
URL/thumbnail-mapping og komplett godkjent NO/TH/EN-metadata. Skjemaet mangler
også en måte å uttrykke språket i selve mediefilen. Produksjonsseeding av alle
ti kan derfor **ikke** utføres uten å oppdikte oversettelser/URL-er, feilmerke
eksisterende innhold eller risikere språklekkasje.

Dette er ikke en hypotetisk kodefeil; det er et dokumentert datakontrakt- og
innholdsgap. Live GET-sjekkene var read-only. Ingen chat-POST eller
databaseendring ble utført.

## Omfang og risiko

- Berørt: additiv MongoDB-samling/indekser, seedvalidering, Michael-retrieval,
  ny JWT-beskyttet bibliotekrute og web-rendering av katalogformat/podkast.
- Skal ikke berøres: eksisterende authimplementasjon, kvoter, premium, Stripe,
  RevenueCat, betaling, quizdata, TTS eller mobilappen.
- Høyeste risiko er ikke teknisk migrasjon, men feil innhold: én fil kan få en
  lovende tittel på tre språk selv om lydsporet bare er norsk eller dekker et
  annet tema.
- En unik indeks som opprettes etter at duplikater er seedet kan feile ved
  startup. Indeksen og idempotent upsert må derfor utformes sammen og testes mot
  tom, eksisterende og duplisert lokal/falsk samling.
- Regex bygget direkte fra bruker-/modelltekst kan gi brede eller dyre treff.
  Oppslag bør normalisere mot en kontrollert tagliste og ha deterministisk
  sortering/tie-break.

## Akseptansekriterier for Solution Architect

1. Avklar før aktiv seeding hvordan mediets eget språk modelleres: enten ett
   dokument per språk med eksplisitt `content_language`, eller språkspesifikke
   media-/thumbnail-URL-er. Metadata-`i18n` alene skal ikke påstå 100 %
   språkisolasjon for en språkbærende fil.
2. De ti `media_id`-ene seedes ikke aktive før hver har en skriftlig godkjent
   filmapping, HTTP-lesbar URL/thumbnail og komplett godkjent
   `i18n.no/th/en.title/description`. Ingen automatisk norsk fallback eller
   maskinoppdiktet oversettelse.
3. Seed-skriptet validerer hele datasettet før DB-tilkobling/skriving, bruker
   `DB_NAME` fra miljøet, utfører idempotent upsert på `media_id` og rapporterer
   matched/modified/upserted uten å slette andre poster. Det skal ha en ren,
   lokal testvei som ikke krever produksjonsdatabase.
4. `media_id` får en unik indeks gjennom eksisterende startup-indeksmønster.
   Aktive kategori-/type-/tagoppslag får bare de minimale indeksene som den
   faktiske spørringen trenger.
5. En felles serializer velger eksakt `i18n[lang]` og returnerer bare lokalisert
   `title`/`description`; manglende eller ugyldig språk gir fail-stop, aldri et
   annet språk eller alle tre språkobjektene til eleven.
6. `GET /api/library/media` bruker uendret `Depends(get_current_user)`, henter
   bare aktive poster og gir en dokumentert, deterministisk kategorisortering.
   Den gamle biblioteksiden må enten adapteres minimalt eller beholdes intakt
   til katalogen har godkjente data.
7. Michael søker kontrollerte, normaliserte tags i `media_catalog`, returnerer
   maksimalt ett sikkert treff i eksisterende `media`-felt og legger ikke URL-er
   fra modellen inn i responsen. Manglende treff gir tekst-only.
8. Frontend godtar både `video` og `podcast` fra den strukturerte responsen,
   validerer sikker URL og bruker kun allerede lokalisert API-tekst. Ingen ny
   frontend-språkfallback.
9. Enhetstester bruker falsk/in-memory DB og dekker: unik/idempotent upsert,
   inaktive poster, tagtreff/tie-break, maks ett medium, manglende språk,
   NO/TH/EN-purity, JWT-krav, URL-avvisning og podcast-rendering. Ingen test
   kobler til eller muterer produksjon.
10. Produksjonsseed kjøres først etter at kriterium 1–2 er oppfylt. Deretter
    verifiseres idempotens med en andre kjøring og kun read-only GET/HTTP 200;
    hemmeligheter eller database-URI skal ikke skrives til logg/rapport.

## Bevist, ukjent og handoff

Bevist: arkitekturspredningen, manglende samling/rute/indeks, frontendens
podkastgap, eksisterende JWT-mønster, tilgjengelige kandidater og brutte
thumbnail-avledninger. Ukjent: redaksjonell godkjenning, faktisk innhold og
språk i hver kandidat, samt korrekte URL-er og oversettelser for alle ti poster.

**Handoff til Agent 2:** tegn en additiv, liten katalogpatch med streng
fail-stop og tydelig seed-gate. Ikke la implementasjonen eller deployen fremstå
som fullført produksjonsseeding før innholdseieren/den andre agenten har levert
og godkjent det manglende seedgrunnlaget.

---
# PAIN PROFILE: Michael-chatten mangler en rolig, sentrert samtaleflate

## Brukersmerte og forventet oppførsel

Skjermbildet viser at Michael-chatten oppleves som en bred app-/kortflate, ikke
som én rolig ChatGPT-/Codex-lignende samtale. Den synlige starten av Michaels
svar er avkuttet under toppområdet, to mediekort ligger side ved side og kortet
til høyre blir visuelt avskåret ved viewportkanten. Eleven forventer en kompakt
Michael-header, én sentrert vertikal meldingskolonne, ett kort under riktig svar,
ingen horisontal avskjæring og et skrivefelt som alltid er tilgjengelig nederst.

Målmappe og berørt flyt er kun Michael-frontend i `backend/webapp.py`. Backend,
chat-API, auth, kvoter, premium og betaling er utenfor denne layoutpatchen.

## Verifiserte observasjoner

- Den generelle desktop-regelen gjør hele appen til en fast 390 px telefonramme
  (`backend/webapp.py:90-114`). Michael-modus overstyrer dette til en egen bred
  860 px app-ramme (`backend/webapp.py:1149-1161`) i stedet for å la en smal
  samtalekolonne ligge sentrert i en normal sideflate.
- Michael-headeren er låst til 90 px med en 64 px avatar både globalt og på
  mobil (`backend/webapp.py:3064-3085,3364-3371`). Sammen med den separate
  globale topplinjen på 56 px (`backend/webapp.py:50,118-125`) bruker de to
  toppområdene 146 px før samtalen begynner. Skjermbildet bekrefter at dette
  oppleves som et høyt, dominerende toppområde.
- Meldingslisten er riktig nok en egen vertikal scrollflate, men innholdet har
  ingen sentrert lesebredde: `.teacher-messages` fyller chatkolonnen
  (`backend/webapp.py:3125-3128`), og alle assistentbobler tvinges til 100 %
  bredde (`backend/webapp.py:3220`). Den eksisterende `52ch`-grensen gjelder
  bare hvert avsnitt, ikke selve samtaleraden, kortene eller handlingene
  (`backend/webapp.py:3162-3165`).
- `_teacherAppendBubble()` setter scrollposisjonen til hele listens bunn straks
  et assistentsvar legges inn (`backend/webapp.py:9583-9622`). For et langt nytt
  svar betyr det at eleven havner ved slutten, ikke ved starten. Når skiltet
  kommer via `data.media`, legges kortet til etterpå uten tilsvarende
  startjustering (`backend/webapp.py:9867-9883,10149-10157`). Dette forklarer den
  synlig avkuttede svarstarten under headeren i skjermbildet.
- Mediestripen bruker to like kolonner på desktop
  (`backend/webapp.py:3314-3317`), og frontend tillater opptil to kort per svar
  (`backend/webapp.py:9867-9880`). Skjermbildet viser nettopp to brede skiltkort
  side ved side, der kort nummer to fortsetter ut mot og blir avskåret ved høyre
  viewportkant. Mobilregelen går først over til én kolonne under 768 px
  (`backend/webapp.py:3393`).
- Flere forfedre bruker `overflow:hidden`, blant annet `#app`, `#content` og
  `#screenTeacher` (`backend/webapp.py:77-80,147-151,3099`). En bred visuell
  komponent får derfor ingen trygg side-scroll eller ombrekking utenfor sin
  lokale gridregel; den blir klippet.
- Skrivefeltet ligger allerede etter den fleksible meldingslisten, har
  `flex-shrink:0` og forblir nederst i chatkolonnen
  (`backend/webapp.py:3263-3286,4262-4268`). Problemet er derfor ikke mangel på
  en composer, men at hele composer-, meldings- og medieflaten følger den brede
  app-rammen uten en felles sentrert maksbreddwrapper.
- Eksisterende kontrakttester låser dagens 90 px header/64 px avatar og
  to-kolonnehandlinger (`tests/test_michael_mobile_ui_contract.py:68-84`).
  Medietesten krever bare én kolonne i mobilregelen og beskytter ikke mot den
  brede desktopstripen (`tests/test_michael_media_cards_contract.py:18-27`).

## Bevist rotårsak

Rotårsaken er **BEVIST lokalt** som fire sammenhengende frontendvalg:

1. Michael bruker en egen bred app-ramme i stedet for en sentrert lesekolonne.
2. Toppbaren og den låste 90 px Michael-headeren tar uforholdsmessig mye høyde.
3. Nye assistentsvar scrolles automatisk til bunnen før etterslepende media er
   ferdig rendret, slik at starten på svaret ikke blir lesepunktet.
4. Medier gjengis som en to-kolonners desktopstrip med opptil to kort, mens
   overordnede flater klipper overflow.

Det er ikke nødvendig å endre chat-API-et eller gjøre en stor rewrite for å
rette dette. Eksisterende DOM-rekkefølge for header, meldingsliste og composer
kan beholdes.

## Omfang, risiko og ukjent

- Berørt: CSS-layout for Michael-modus og den lokale scrollplasseringen etter
  et nytt assistentsvar.
- Skal ikke berøres: svarinnhold, mediematching, språkdata, sidepanel-logikk,
  backend, database, TTS, auth, kvoter, premium, Stripe, RevenueCat eller
  mobilappen.
- Hovedrisiko: en global endring av `#app` eller generelle mediekort kan gi
  regresjon i quiz, bibliotek eller quiz-coach. Endringen må derfor scopes til
  `#app.teacher-mode`/`#screenTeacher` og ordinær Michael-chat.
- Hovedrisiko på små skjermer: en faktisk `position:fixed` composer kan kollidere
  med tastatur og safe-area. Den eksisterende flex-composeren bør beholdes som
  fast bunnrad i chat-shellen fremfor å løsnes fra layouten.
- **IKKE BEVIST:** eksakt fysisk viewportbredde, nettleserzoom og OS-skalering i
  skjermbildet. Den synlige avskjæringen er bevist visuelt, men disse faktorene
  bør ikke brukes som rotårsak når kodevalgene over allerede forklarer den.

## Akseptansekriterier for Solution Architect

1. Michael-headeren komprimeres tydelig på desktop og mobil uten at navn,
   aktivt språk eller emneknapp blir utilgjengelig.
2. Meldinger, handlinger, media og composer deler én sentrert maksbreddwrapper;
   desktop har luft på sidene, mens mobil bruker tilgjengelig bredde.
3. Samtalen er én vertikal strøm. Ordinær Michael-chat viser maksimalt én
   mediekolonne og ingen komponent skaper eller skjuler horisontal overflow ved
   320, 390, 768 eller vanlig desktopbredde.
4. Et nytt langt Michael-svar plasserer leseren ved starten av den nye
   assistentraden etter at kortene er lagt til, ikke ved listens absolutte bunn.
5. Composer forblir synlig nederst via dagens flex-shell, håndterer safe-area og
   mobil-tastatur, og får ingen global `position:fixed` som kan overlappe svar.
6. Thai2Drive-paletten beholdes: mørk navy, cyan/blå detaljer og eksisterende
   oransje aksent. Ingen ny designsystemrewrite.
7. Sidepanelet åpnes fortsatt på forespørsel og tar ikke permanent plass fra
   den sentrerte samtalekolonnen.
8. Eksisterende NO/TH/EN-tekst og språkisolasjon forblir uendret; patchen legger
   ikke til learner-facing tekst.
9. Målrettede layoutkontrakter oppdateres for kompakt header, sentrert kolonne,
   én media-kolonne, overflow-sikkerhet og startscroll. Inline-JS-syntaks,
   relevante enhetstester og `git diff --check` må passere.

## Handoff til Agent 2

Utform én smal frontend-only patch i `backend/webapp.py`: scope en sentrert
samtalewrapper til Michael-modus, komprimer headeren, tving ordinær chatmedia til
én kolonne og juster scrollen først etter at assistentsvar og media er rendret.
Behold eksisterende DOM, flex-composer, sidepanel, Thai2Drive-farger og all
backendlogikk.

---

# PAIN PROFILE: vanlig quiz starter fortsatt 30 spørsmål

## Bevist rotårsak

Backendens `GET /api/questions/random` har allerede standard `count=10`, men
webappen overstyrer dette med `count=30` i tilfeldig quiz, kategoriquiz og
kategori-fallback. Den statiske fremdriftsteksten starter også med «1 av 30».
Daglig test bruker allerede 10, mens teoriprøvemodus bevisst bruker 45.

## Omfang og akseptanse

Vanlig quiz, kategoriquiz, kategori-fallback og «Mine feil» skal hente maksimalt
10 spørsmål per økt. Teoriprøvemodus (45) og skiltøving (1) skal være urørt.
Fremdrift skal bruke faktisk øktlengde, og oppsummeringen skal tilby ny økt
eller Michael. Guest/free/premium-kvoter og betalingslogikk skal ikke endres.

Rotårsaken er bevist. Klar for Solution Architect.
---

# PAIN PROFILE: Michael gir mer enn én konkret ting

## Bevist rotårsak

`teacher_chat.py` instruerer modellen til å lage flere seksjoner, eksempler,
metaforer og oppfølgingsspørsmål. Deretter genererer backend `suggestions`, mens
`webapp.py` også legger til skilt-/emneknapper under svaret. Prompt alene kan
derfor ikke garantere brukerens ønskede minimum.

## Avgrensning og akseptanse

Chatresponsen skal inneholde ett språkfritt, kort regelsvar på maksimalt to
setninger og omtrent 30 ord. Ingen overskrifter, metaforer, oppfølgingsspørsmål,
video eller podcast. Ved konkret skilt beholdes maksimalt ett eksakt skiltasset
øverst. `suggestions` skal være tomt, og frontend skal ikke bygge svarmeny.
Quiz-coach bruker samme endpoint og får samme korte regel. TTS, auth, kvoter,
betaling og mediekatalogens øvrige API-er er urørt.

Rotårsaken er bevist. Klar for Solution Architect.
