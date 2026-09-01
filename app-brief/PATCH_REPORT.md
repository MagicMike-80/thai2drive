# PATCH REPORT: Lov-tag-mapping (§3 HAV-regelen, §7 vikeplikt) for medieoppslag

## Bakgrunn

Oppdrag fra Michael (Agent 3/Code Builder-rolle): koble situasjonsbilder/skilt
mot Vegtrafikkloven §3 og Trafikkreglene §7 via hashtags, slik at Michael-chat
finner riktig bilde når brukeren spør om paragrafen eller synonymer for den.

Den fysiske bilde-CSV-en (170 bilder, `michael_image_catalog_current.csv`) er
ikke levert til denne økten ennå — den ligger fortsatt kun lokalt på Michaels
maskin. Dette patchet leverer derfor **infrastrukturen** (lov→tag-oppslag +
kobling i begge Michael-medieoppslagsstiene + tester), klar til å ta imot de
reelle 100+ bildene den dagen katalogen når repoet.

## Endring

- `backend/media_catalog.py`: Ny `LAW_MAPPING` (§3 HAV-regelen, §7 nr. 2
  vikeplikt/høyreregel, §7 nr. 4 bussregelen) med kanoniske tags og
  fritekst-synonymer, pluss `expand_law_synonyms()` som slår opp en melding
  mot kartet. Lengste synonym vinner og "spises" av teksten før kortere
  synonymer sjekkes, slik at f.eks. "paragraf 7 nr 4" ikke også leser ut de
  bredere §7 nr. 2-tagsene (den korte formen er bokstavelig en delstreng av
  den lange).
  - **Bevisst avvik fra oppdraget:** `"§ 3"` / `"§ 7-2"`-formene er utelatt.
    Eksisterende normalisering (`normalize_catalog_text`) fjerner paragraftegn
    og bindestrek, så `"§ 3"` ville blitt til det rene sifferet `"3"` og gitt
    falske treff på enhver melding som nevner tallet 3 (spørsmålsnummer,
    fartsgrense, osv.). Kun de fulle tekstlige synonymene ("paragraf 3",
    "hav-regelen", ...) er derfor med — i tråd med kodebasens eksisterende
    "aldri fuzzy match"-prinsipp.
- `backend/teacher_chat.py`: `expand_law_synonyms()` er koblet inn i begge
  medieoppslagsstiene — `_material_match_terms()` (michael_materials:
  topic_tags/situation_tags) og `_get_relevant_catalog_media()`
  (media_catalog: tags). En bruker som skriver "paragraf 7", "vikeplikt
  venstresving" eller "hav-regelen" matcher nå bilder tagget med de
  tilsvarende kanoniske tagsene, uansett hvilken av de to samlingene bildet
  ligger i.
- 80×80 kompakt, klikkbar bilde-rendering i chat-boblen (`webapp.py`,
  `.tm-media-card.sign`) fantes allerede for `type: "sign"`-medier — ingen
  endring nødvendig der. Situasjons-/veikryssbilder (`type:
  "intersection_image"`) beholder bevisst sin større 180px-visning; å tvinge
  foto av trafikksituasjoner ned til 80×80 ville gått på bekostning av
  lesbarhet, så dette er ikke endret uten eksplisitt bekreftelse.
- CSV/bilde-manifest-import til `michael_materials` er **ikke** bygget i
  dette patchet — kolonneformatet i den reelle katalogen er ukjent før filen
  er levert, og å gjette et skjema nå ville vært spekulativ kode ingen kan
  verifisere. Når filen er tilgjengelig i denne økten, er neste steg et
  import-skript etter samme trygge mønster som `seed_media_catalog.py`
  (dry-run som standard, snapshot før skriving, `--confirm-db-name`).
- API-kontrakt, frontend utenom det nevnte, database-skjema, auth, kvoter,
  premium, betaling, TTS, deploykonfigurasjon og Michael-portrett er urørt.

## Tester

- Nye: 6 tester i `test_media_catalog.py` (lov-synonym-oppløsning, inkl.
  eksplisitt negativ test på at bare sifferet fra "§ 3" ikke skal matche) og
  2 tester i `test_michael_material_retrieval.py` som verifiserer QA-kravet
  ordrett: "vikeplikt venstresving" og "paragraf 7" returnerer riktig
  `#7_2`-bilde, og at "paragraf 7 nr 4" ikke lekker det generiske §7 nr.
  2-bildet foran bussregel-bildet.
- 26/26 i `test_media_catalog.py` + `test_michael_material_retrieval.py`: PASS.
- 30/30 i `test_teacher_chat_fallback.py` + `test_media_catalog_seed.py`
  (uendret, ingen regresjon): PASS.
- Python-syntaks (`py_compile`) og `git diff --check`: PASS.
- Ingen produksjonstester (`BASE_URL`-suiten) er kjørt, per CLAUDE.md.

## Risiko og rollback

Ren tilleggslogikk — ingen eksisterende felt, skjema eller produksjons-DB er
endret. `expand_law_synonyms()` er en ren funksjon uten sideeffekter; feil i
den kan i verste fall gi 0 eller feil medietreff, aldri en krasj (begge
kallstedene er allerede i `try/except`-blokker som fail-softer til tom
liste). Rollback er én revert av dette patchet.

Gjenstår før "ferdig levert": den fysiske bildekatalogen (CSV + 170 bilder)
må inn i denne økten (opplasting, Google Drive, eller git), deretter bygges
og kjøres import-skriptet inn i `michael_materials`, og til slutt push/PR.

---

# PATCH REPORT: § 7 nr. 2-grounding og streng skiltvalidering

## Endring

- `backend/teacher_chat.py` inneholder nå hele ordlyden i trafikkreglene
  § 7 nr. 2 som en absolutt systeminstruks. NO/TH/EN har hver sin
  språktilpassede instruks.
- En smal intent-detektor kjenner igjen direkte spørsmål om § 7 nr. 2 samt den
  konkrete kombinasjonen høyreregel + venstresving + møtende/høyre-side.
- En deterministisk fail-safe kjøres etter både modellrespons og feilfallback.
  Den returnerer alltid begge lovsetningene og korrigerer kategoriske «Nei»-svar
  i den dokumenterte venstresving-situasjonen.
- Responsens `sign_ids` bygges nå bare fra kontrollerte eksplisitte bruker- eller
  svarmatcher. Generiske skilt-ID-er fra bred RAG-kontekst kan ikke lenger bli
  responsmedia; `316_0`-feilen er derfor stengt.
- API-kontrakt, frontend, database, auth, kvoter, premium, betaling, TTS,
  deploykonfigurasjon og Michael-portrett er urørt.

## Tester

- 28/28 direkte prompt-, fail-safe-, paragraf- og skiltvalideringstester: PASS.
- 40/40 målrettede backendtester: PASS.
- 51/51 Michael-, media- og mobilkontrakttester: PASS.
- 60/60 full sikker `tests/`-suite: PASS.
- Python-syntaks og `git diff --check`: PASS.

## Risiko og rollback

Fail-safe krever tre samtidige begrepsgrupper for venstresving-intensjon, eller
en eksplisitt henvisning til § 7 nr. 2. Negative tester viser at generell
høyreregel, vanlig venstresving og vikeplikt for gående ikke overstyres.
Rollback er én revert; ingen data migreres.

Klar for uavhengig QA Gate og deretter autorisert commit/push/liveverifisering.

---

# PATCH REPORT: skiltord koblet til 202/204 i Michael-chat

## Endring

- `backend/teacher_chat.py` analyserer nå Michaels ferdige, synlige svar med en
  liten kontrollert NO/TH/EN-tabell. Eksakte Vikepliktskilt-/Give Way-/ป้ายให้ทาง-
  uttrykk og skilt 202 gir `202_0`; Stoppskilt-/Stop sign-/ป้ายหยุด-uttrykk og
  skilt 204 gir `204_0`.
- Eksplisitte bruker-ID-er prioriteres, deretter kontrollerte svar-ID-er. De
  dedupliseres i stabil rekkefølge og begrenses til to. Generisk kontekst brukes
  bare når verken brukeren eller svaret har et konkret skilt.
- Backend bygger lokaliserte, autoritative skiltmedier etter at svaret finnes og
  filtrerer media slik at hver media-ID samsvarer med responsens `sign_ids`.
- Rene spørsmål om Høyreregelen på NO/TH/EN stopper den generiske
  kontekst-fallbacken. De forblir derfor regeltekst uten skiltbilde, med mindre
  brukeren eller Michael faktisk navngir et konkret skilt.
- `backend/webapp.py` ble kontrollert, men ikke endret: dagens sikre mediakort er
  allerede klikkbart og har 80 x 80 px skiltbilde på mobil og desktop.
- Michael-portrett, auth, kvoter, premium, betaling, TTS, database og
  deploykonfigurasjon er urørt.

## Tester

- 45/45 målrettede matcher-, media- og mobilkontrakttester: PASS.
- 60/60 full sikker `tests/`-suite: PASS.
- 34/34 målrettede backendtester: PASS.
- Python-syntaks: PASS.
- `git diff --check`: PASS med bare Windows LF/CRLF-varsler.

## Risiko og rollback

Falske positive begrenses med eksakte skiltfraser, kontrollerte standalone-valg
og negative tester for Høyreregelen, generell vikeplikt og stoppelengde. Rollback
er én revert av denne avgrensede committen; ingen data migreres.

Klar for uavhengig QA Gate og deretter kontrollert commit/push/liveverifisering.

---

# PATCH REPORT: fase 1 - språkren Michael og to tydelige nestevalg

## Endring

- `backend/teacher_chat.py`: den skjulte primeren for en ny norsk samtale er
  rettet fra thai til norsk. Norsk, thai og engelsk har nå hver sin rene primer,
  og ukjent språk faller kontrollert tilbake til engelsk.
- `backend/webapp.py`: et konkret skiltkort får to språkrene nestevalg:
  `Vis eksempel` sender en kort, lokalisert oppfølgingsforespørsel til samme
  Michael-samtale, mens `Test meg` åpner eksisterende skiltøving.
- Eksisterende eksakt skiltmedia og det ekte Michael-portrettet gjenbrukes.
  Portrettets Git-blob er uendret (`bdef6149a9cc80a5dc873097146ab1d5ee3ab6a9`).
- Kontrakttester låser språkprimeren, de to handlingene og komplette NO/TH/EN-
  tekster.

## Avgrensning

Ingen ny AI-motor, database, auth-, kvote-, premium-, Stripe-, RevenueCat-,
betalings-, TTS-, bilde-, deploy- eller produksjonsendring. Ingen brukerfiler
utenfor den rene arbeidsgrenen er berørt.

## Verifisering

- 40 målrettede Michael-, media-, språk- og mobiltester: PASS.
- Hele `tests/`-suiten, 60 tester: PASS.
- Backend discovery: 40 tester PASS; én ekstra fil kunne ikke samles fordi den
  valgfrie lokale testavhengigheten `pytest` ikke er installert i runtime.
- Python-syntaks: PASS.
- Inline JavaScript-syntaks via Node: PASS.
- `git diff --check`: PASS med bare Windows LF/CRLF-varsler.
- Michael-portrettet er byte-identisk med `HEAD`.

## Gjenværende kontroll og rollback

Før push/deploy bør Michael vurdere den lokale patchen. Etter eventuell deploy
må en fersk NO/TH/EN-canary bevise: kort svar, riktig vikepliktskilt, `Vis
eksempel` og `Test meg`. Rollback er å reversere de fire avgrensede filene;
ingen data må migreres eller slettes.

Klar for QA Gate.

---

# PATCH REPORT: eksakt skilt og kompakt ordkobling i Michael-chat

## Endrede filer

- `backend/teacher_chat.py`: kontrollerte NO/TH/EN-aliaser for `202_0`,
  `204_0` og `208_0`; latinske aliaser krever hele ord/frase. Eksplisitte
  skiltspørsmål returnerer maksimalt ett godkjent `type=sign`-medium med samme
  ID, uten generisk bilde, video eller annet skilt. Responsens `sign_ids` bruker
  eksplisitte ID-er når de finnes. Skiltkontekst låner aldri norsk når valgt
  språk mangler.
- `backend/webapp.py`: begge eksisterende skiltkortene er mørke, klikkbare og
  begrenset til 90 x 90 px skiltbilde. Kort og første eksakte skiltnavn i
  svarteksten åpner eksisterende `GET /api/signs/{id}` / `openSignDetail`.
  Ordkoblingen går via tekstnoder og `textContent`, aldri modellstyrt HTML.
- `backend/tests/test_teacher_chat_fallback.py`: aliasmatrise for NO/TH/EN,
  negative grensetreff, responsflyt og språk-fail-stop.
- `backend/tests/test_michael_material_retrieval.py`: streng eksklusivitet,
  tekst-only ved utrygg/ufullstendig media og bevart bred mediaflyt.
- `tests/test_michael_media_cards_contract.py`: kompakt, tilgjengelig og
  detaljkoblet sign-medium.
- `tests/test_michael_mobile_ui_contract.py`: 90 px fallbackkort, eksisterende
  detalj-API og sikker tekstnodekobling.
- `context/FEATURES.md`: lokal ønsket/levert-status oppdatert. Filen skal ikke
  stages eller committes.
- `app-brief/PATCH_REPORT.md`: denne handoff-rapporten.

`app-brief/PAIN_PROFILE.md` og `app-brief/SOLUTION_BLUEPRINT.md` var allerede
oppdatert av Agent 1 og 2 i samme teamflyt.

## Avgrensning

Ingen auth-, kvote-, premium-, Stripe-, RevenueCat-, betalings-, database-,
mobilapp- eller deployendring. Fargekoder vises ikke fordi dagens autoritative
skilt-API mangler feltet; dekorative UI-farger fremstilles ikke som offisielle.

## Verifisering

- 39 målrettede backend-/frontendtester: PASS.
- Hele oppdagede `tests/`-suiten, 45 tester: PASS.
- Python AST/syntaks, 126 filer med BOM-sikker lesing: PASS.
- Inline JavaScript-syntaks via Node: PASS.
- `git diff --check`: PASS; bare Windows LF/CRLF-varsler.
- Ingen produksjons-POST eller test som muterer produksjonsdata ble kjørt.

## Gjenværende risiko og rollback

Automatiske kontrakter dekker ID-er, språk, sikker DOM og størrelsesgrenser,
men faktisk klikk/fokus og lang thai-tekst bør kontrolleres visuelt ved ca.
390 px i QA. Rollback er å reversere alias-/eksklusivitetsgrenene og de
avgrensede kort-/detaljkoblingene; ingen data må migreres eller slettes.

## QA-fiks

- Fallback-skiltkort rendres nå bare når `GET /api/signs/{id}` har et navn på
  aktiv `appLang`; manglende aktiv språkverdi skjules fail-stop.
- Den dupliserte norske frontend-aliasen er erstattet med den backend-godkjente
  formen `vikepliktskiltet`, og begge forhold er låst i målrettet kontrakttest.

Ingen commit, push eller deploy er utført. Klar for Agent 4.

---

# PATCH REPORT: Patch 2 — Michael-chat og visuelle media-kort

## Endring

- `backend/teacher_chat.py`: `/api/teacher/chat` rangerer aktive og
  Michael-godkjente skilt, situasjonsbilder og videoer fra
  `michael_materials` mot elevens spørsmål, quizkontekst og godkjente skilt-ID-er.
- Responsen beholder `reply`, `suggestions` og `sign_ids`, og legger additivt til
  `media` med opptil to elementer (`id`, `type`, `url`, språkstyrt `title` og
  `caption`, samt `sign_id` når relevant).
- Eksakt skilt-ID prioriteres foran kontrollerte emne- og situasjonsknagger.
  Videoreferanser må peke på en aktiv post i `learning_videos`.
- Materialet legges i Michaels skjulte kontekst, mens klienten får strukturerte
  data og kan vise kortet separat fra tekstsvaret.
- `backend/webapp.py`: vanlig Michael-chat og quiz-coachen rendrer samme sikre
  media-komponent. Skilt og situasjonsbilder får bilde, tittel og kort
  forklaring; videoer får en språkstyrt avspillingsknapp.
- Media-kortene bruker én kolonne på mobil, begrenset bildehøyde og Dark Mode.
  Eksisterende skiltkort beholdes som fallback uten dobbeltvisning.
- YouTube-materiale åpnes i appens videospiller, som returnerer eleven til
  skjermen der videoen ble åpnet.
- Nye tester dekker rangering, grensen på to ressurser, sikker URL, aktiv- og
  godkjenningskrav, videokilde og strengt språkvalg for NO/TH/EN.

## Avgrensning

Ingen data migreres, og auth, TTS, premium, Stripe, RevenueCat, betaling og
deploykonfigurasjon er urørt.

## Verifisering

- Python-syntaks: PASS.
- Inline JavaScript-syntaks: PASS.
- 40 målrettede Michael-, admin-, språk-, media- og mobiltester: PASS.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsler.

Klar for commit, push og live-verifisering.

---

# PATCH REPORT: Michael-materiale i adminpanelet

## Endring

- `backend/server.py`: ny, adminbeskyttet `michael_materials`-samling med
  liste-, opprettings- og oppdateringsrute. Referanser peker til eksisterende
  skilt/video eller en godkjent situasjonsbilde-URL; mediet kopieres ikke.
- `backend/server.py`: allow-list på felter og typer, sikker URL-kontroll,
  kildeoppslag, dedupliserte knagger og krav om tittel og forklaring på NO/TH/EN
  før en aktiv post kan godkjennes for Michael.
- `backend/admin.html`: ny fane «Michael-materiale» med type-/statusfilter,
  kortvisning med forhåndsvisning, opprett/rediger-skjema og trygg deaktivering
  uten å slette kildemediet.
- `tests/test_michael_material_admin_contract.py`: kontrakt- og
  valideringstester for auth, kildereferanser, språk, sikker URL og adminflyt.

## Avgrensning

Patchen oppretter bare adminbiblioteket. Michael-chatten leser ikke fra den nye
samlingen ennå, og lærerresponsen er ikke endret. Ingen eksisterende skilt,
spørsmål, videoer eller mediefiler er flyttet. Auth-policy, TTS, premium,
Stripe, RevenueCat og betaling er urørt. Ingen commit, push eller deploy.

## Verifisering

- Python-syntaks: PASS.
- Inline JavaScript-syntaks: PASS.
- 22 målrettede admin-, skilt- og Michael-kontrakttester: PASS.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsler.

## Risiko og rollback

Den nye samlingen er tom til administrator legger inn referanser. Feil eller
manglende kilde-ID avvises før lagring. Rollback er å fjerne de tre additive
rutene, adminfanen og den nye kontrakttesten; eksisterende materiale påvirkes
ikke.

Klar for Agent 4.

---

# PATCH REPORT: ett konkret Michael-svar

- `backend/teacher_chat.py`: siste systeminstruks krever ett kort svar på valgt
  språk, 1–2 setninger og maks 30 ord, uten overskrifter, eksempler,
  kontrollspørsmål, HAV eller «Kongen og tjeneren».
- Backend etterbehandler svaret deterministisk og fjerner seksjoner,
  mediatagger, spørsmål og forbudte metaforer dersom en reservemodell avviker.
- Responsen returnerer ingen forslag og maksimalt ett godkjent skiltbilde når
  et skilt er identifisert.
- `backend/webapp.py`: menyknapper, automatisk bremsevideo og den synlige
  mini-practice-knappen vises ikke etter Michael-svaret.
- Ingen endring i auth, kvoter, premium, Stripe, RevenueCat eller betaling.

Verifisert med Python-syntaks, 51 målrettede tester, hele lokale `tests/`
(60/60), trygge backendtester uten produksjonskall (39/39) og `git diff
--check`.

Klar for Agent 4.

### QA-fiks: forslag beholdt ikke svarstart

- Fjernet den absolutte bunnscrollen fra `_teacherAppendChips()`. Forslagene
  legges fortsatt inn etter svaret, men flytter ikke leseren bort fra starten
  som `_teacherScrollToAnswerStart()` nettopp har valgt.
- Kontrakten låser både rekkefølgen svar/media/startscroll/forslag og at
  `_teacherAppendChips()` ikke skriver `scrollHeight` til meldingslisten.

---

# PATCH REPORT: rolig Michael-chat koblet til eksisterende medieflyt

## Endrede applikasjonsfiler

- `backend/webapp.py`: utvider bare Michael-rammen på desktop og sentrerer
  header, meldingsliste og eksisterende flex-composer i en lesekolonne på
  maksimalt 760 px. Mobil bruker full tilgjengelig bredde.
- `backend/webapp.py`: komprimerer headeren til 72 px og portrettet til 48 px,
  med sidepanel og backdrop flyttet til samme 72 px-inset.
- `backend/webapp.py`: gjør ordinære Michael-medier til én vertikal kolonne på
  alle breakpoints og legger lokale krympe-/overflow-regler på chatinnholdet.
- `backend/webapp.py`: legger `_teacherScrollToAnswerStart()` som plasserer
  leseren ved starten av det nye svaret etter strukturert media og awaitede
  skiltkort. Den eldre asynkrone videoveien og feilresponsen bruker samme regel.
- `tests/test_michael_mobile_ui_contract.py`: kontrakt for 72/48 px-header,
  sentrert 760 px-kolonne, panel-inset, overflow og uendret flex-composer.
- `tests/test_michael_media_cards_contract.py`: kontrakt for én mediekolonne,
  sikker bredde og startscroll etter alle avtalte mediaflyter.

## Avgrensning

Ingen endring i backend-API, `teacher_chat.py`, `media_catalog`, seed-data,
bibliotekdata, språkinnhold, auth, kvoter, premium, Stripe, RevenueCat,
betaling, TTS eller mobilappen. Eksisterende videoåpner med retur til Michael,
inline podcastlyd og autoritativ skiltdetalj er bevart. Emne-/historikk-overlay
og composerens flexplassering er uendret.

## Verifisering

- Målrettede layout- og mediakontrakter: 22/22 PASS.
- Full lokal `tests/`-suite: 54/54 PASS.
- Relevante sikre teacher-/material-/katalogtester: 34/34 PASS.
- Python AST: 152 filer PASS.
- Inline JavaScript via `node --check`: 1/1 blokk PASS.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsler.
- Ingen produksjonskall eller produksjonsmuterende test er kjørt.

## Gjenværende risiko og rollback

Kontrakttestene låser layout- og scrollreglene, men faktisk viewport/kamera-
tastaturatferd bør kontrolleres visuelt ved 320, 390, 768 px og desktop i QA.
Rollback er å reversere de scoped CSS-reglene, scrollhelperen og de to
kontrakttestene; ingen data må migreres eller slettes.

Klar for Agent 4.

---

# PATCH REPORT: additiv `media_catalog` med streng seed-gate

## Implementert Patch A

- `backend/media_catalog.py`: felles schema-, enum-, URL- og full NO/TH/EN-
  validering, `content_language`-gate, språkren serializer, kategorisortering og
  deterministisk heltagsranking med maks ett treff.
- `backend/create_indexes.py`: idempotent unik `media_id`-indeks og sammensatt
  aktiv/språk/tags-indeks. Katalogindeksene kjøres sist, slik at en eventuell
  katalogduplikat ikke hindrer verifikasjon av etablerte indekser.
- `backend/server.py`: JWT-beskyttet `GET /api/library/media` med obligatorisk
  eksakt `no|th|en`, HTTP 422 ved ugyldig språk og HTTP 200/tom liste ved tom
  katalog.
- `backend/teacher_chat.py`: fail-soft katalogoppslag mot kontrollerte tags,
  maks ett katalogmedium og totalgrense to. Eksplisitt trafikkskilt forblir
  eksklusivt og ugyldig request-språk får aldri katalogmedia.
- `backend/webapp.py`: strukturert podcastkort med sikre DOM-operasjoner og
  `<audio controls preload="none">`; eksisterende bibliotekflyt er uendret.
- `backend/seed_media_catalog.py`: dry-run som standard, full manifest- og URL-
  validering før Mongo-klient, dobbel apply-bekreftelse, before-snapshot og
  idempotente upserts uten sletting/deaktivering av andre poster.
- `backend/media_catalog_manifest.example.json`: dokumentert tom manifestmal,
  ikke aktive eller oppdiktede produksjonsposter.

## Tester

- Nye falsk-DB/enhetstester dekker schema, URL-policy, duplikater, språkmatrise,
  filspråkgate, ranker, sortering, tom katalog, Michael-komponering og to
  identiske seedkjøringer uten andre gangs skriv.
- Nye statiske kontrakter dekker JWT-rute, indeksnavn, fail-soft Michael-gren,
  seed-gater og podcastkort uten `innerHTML`.
- Målrettet suite: 31/31 PASS.
- Full oppdaget lokal kontraktsuite: 51/51 PASS.
- Alle trygge backendtester: 35/35 PASS.
- Python AST: 152 filer PASS.
- Inline JavaScript: 2/2 blokker PASS.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsler.

## Avgrensning og gjenværende blokkering

Ingen auth-policy, kvote, premium, Stripe, RevenueCat, betaling, TTS, mobilkode
eller eksisterende bibliotekendepunkt er endret. Ingen produksjonsdatabase er
kontaktet eller mutert, og ingen commit/push/deploy er utført.

Aktiv seeding av de ti innholds-ID-ene og omkobling av biblioteksiden er fortsatt
Patch B og **BLOCKED** til innholdseier leverer godkjente filer/URL-er, tags,
NO/TH/EN-tekst og eksplisitt filspråk. Eksempelmanifesten skal derfor feile
dry-run frem til den fylles med godkjent innhold.

Rollback er å fjerne den additive katalogmodulen/ruten/helperen, podcastgrenen
og indeksdefinisjonene. Eksisterende mediesamlinger og synlig bibliotek er urørt.

Klar for Agent 4.

# PATCH REPORT: Fase 2B — Michael quiz-coach og readiness

## Endrede applikasjonsfiler

- `backend/ai_learning.py`: ren og testbar 70/30-readinessformel.
- `backend/server.py`: JWT-sikret `GET /api/user/readiness` basert på siste 50 svar og feilbankmestring.
- `backend/webapp.py`: readiness-måler og fail-soft Michael bottom-sheet etter feil svar.
- `tests/test_user_mistakes.py`: fire formeltester.
- `tests/test_phase2b_contract.py`: auth-, språk- og coach-kontrakter.

## Readiness

Scoren er `70 % * treffprosent siste 50 + 30 % * mestrede feil / alle sporede feil`. En helt ny bruker får 0. En bruker med besvarte spørsmål og ingen registrerte feil får 100 % feilbankmestring. Resultatet klemmes til 0–100 og dashboardet bruker rød 0–59, gul 60–84 og grønn 85–100.

## Michael

Feil svar viser ordinær forklaring og aktiverer Neste før Michael-kallet starter. Bottom-sheet sender spørsmål, elevens svar, fasit, eksisterende forklaring og aktivt språk til eksisterende `/api/teacher/chat`. Kallet avbrytes etter 12 sekunder og viser en språkren fail-soft melding. «Hva betyr dette i praksis?» fortsetter samme økt med ett kontrollspørsmål som ikke teller i quizen.

## Tester

- Python-syntaks: PASS.
- Inline JavaScript-syntaks: PASS.
- 12 målrettede tester: PASS.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsel.

## Risiko og rollback

Michael-kallet skjer automatisk etter feil og kan øke AI-forbruket. Feil/timeout påvirker ikke quizen. Rollback er å fjerne auto-kallet/panelet og readiness-ruten; spørsmål, auth, kvoter og betalingsdata er uendret.

Klar for Agent 4.

---
# PATCH REPORT: vis/skjul emner i Michael-sidefelt

- Gjenbruker de seks eksisterende språkstyrte Michael-emnene i et skjult
  sidefelt på mobil og desktop.
- Legger én kompakt vis/skjul-knapp i Michael-headeren og et bakteppe som lukker
  panelet ved trykk utenfor.
- Panelet lukker seg også ved emnevalg og Escape.
- De gamle store startknappene er skjult fra hovedchatten; «Spør Michael...» og
  den ene konteksthandlingen «Øv på liknende» er bevart.
- Ingen endring i API, AI-svar, TTS, auth, premium, Stripe, RevenueCat eller
  betaling.
- 15 målrettede tester, Python- og JavaScript-syntaks og `git diff --check`:
  PASS.
- Lokal 390 × 844 px kontroll: PASS for lukket panel, seks lesbare valg, skjulte
  hovedknapper og automatisk lukking etter valg.

Klar for Agent 4.

---

# PATCH REPORT: kompakt Michael-side og datadrevne skiltkort

## Endrede applikasjonsfiler

- `backend/webapp.py`: Michael-header er maksimalt 90 px med 64 × 64-portrett,
  rolig online-badge, større leseflate, 2 × 2 handlingshierarki, 56 px input/send
  og tre bunnmenyvalg i Michael-modus.
- `backend/webapp.py`: renderer språkrene SignCard-kort under svaret, støtter flere
  skilt horisontalt og kobler øving til `?sign=<id>` uten tilfeldig fallback.
- `backend/server.py`: legger additivt til tag-filtrering på `/api/signs`,
  detaljruten `/api/signs/{sign_id}` og valgfri `sign_id` for spørsmål.
- `backend/teacher_chat.py`: returnerer strukturerte `sign_ids` fra allerede
  godkjent læreplankontekst, samtidig som `reply` og `suggestions` bevares.
- Kontrakttester er oppdatert for header, språk, navigasjon, SignCard, API og
  sign-ID-utledning.

## Datakilde og avgrensning

Patchen gjenbruker eksisterende `traffic_signs` med 316 språkberikede skilt og
de lokale `/api/sign-images/`-bildene. Det er derfor ikke opprettet et konkurrerende
20-skiltbibliotek i `public/`. Next.js/Tailwind ble ikke introdusert fordi den
aktive produksjonssiden er FastAPI med innebygd HTML/CSS/JavaScript.

Ingen data er migrert. Ingen endring er gjort i Stripe, RevenueCat, hemmeligheter,
premiumstatus eller deploykonfigurasjon. Ingen commit, push eller deploy er utført.

## Verifisering

- Inline JavaScript-syntaks via Node: PASS.
- UI- og sign-API-kontrakttokens: PASS.
- Kjente skilt `362_50` og `506`: bilder finnes og NO/TH/EN-innhold er komplett.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsler.
- Python-kompilering via innebygd Codex-runtime: PASS.
- Målrettede Python-kontrakttester: 21/21 PASS.
- Hele oppdagede frontend-/kontraktsuiten: 30/30 PASS.

## Godkjent mockup-tilpasning

Etter Michaels «GO» er den faktiske headerstrukturen justert til den godkjente
mockupen: det uendrede portrettet står til venstre, navn og status står kompakt
ved siden av, ONLINE-badge ligger på samme statusrad, og gjentatt miniatyravatar
i hver assistentboble er skjult slik at svaret og SignCard bruker full bredde.
Ny målrettet kjøring: 24/24 tester PASS; full oppdaget suite: 30/30 PASS;
Python-kompilering, inline JavaScript og diff-format PASS.

Klar for QA-gate; visuell nettleser- og livekontroll gjenstår før publisering.

## Lokal nettleserkontroll 2026-08-30

Den faktiske `WEBAPP_HTML`-flaten ble åpnet lokalt i Codex-nettleseren med et
representativt Michael-svar og godkjent skilt 362.50. Desktop og 390 × 844 px
mobilbredde viser 90 px header, synlig spørsmål uten avkutting, skiltkort,
handlinger, 56 px input/send og tre bunnfaner. Kontrollen avdekket at automatisk
scroll kunne legge spørsmålet under headeren; scrollmålet ble begrenset til
svarets egen rad og verifisert visuelt etter patchen.

Ingen commit, push eller deploy er utført.

---

# PATCH REPORT: godkjente norske skiltbilder i Michael

## Endrede applikasjonsfiler

- `backend/teacher_chat.py`: sender godkjent `traffic_signs.image_url` og NO/TH/EN-navn som en eksakt bildetagg i læreplankonteksten.
- `backend/teacher_chat.py`: fjerner oppdiktede bildetagger og legger deterministisk til første godkjente skiltbilde hvis modellen utelater det.
- `backend/tests/test_teacher_chat_fallback.py`: tester sikker URL, komplett språkdekning, én-gangs innsetting og fjerning av ikke-godkjent bilde.

## Avgrensning

Patchen gjelder bare konkrete skilt som allerede matcher i `traffic_signs`. Manglende eller ufullstendig bilde gir tekst-only fallback. Norske veiscener er utsatt til et eget kuratert bildebibliotek. Frontend-renderer, TTS, auth, kvoter, Stripe og RevenueCat er urørt.

## Tester og resultat

- Python-syntaks: PASS.
- Frontend-/læringsregresjon: 24/24 PASS.
- Teacher-backendtester: 7/7 relevante PASS.
- Full backend discovery: BLOCKED for én eldre testmodul fordi lokal runtime mangler `pytest`; ingen testfeil ble observert.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsler.

## Risiko og rollback

Live MongoDB-match og visuell mobilgjengivelse må kontrolleres etter en separat godkjent deploy. Rollback er å reversere helperne, promptlinjene og de nye testene i denne avgrensede patchen.

Klar for Agent 4.

---

# PATCH REPORT: Michael mobilprofil og forenklet lærerflate

## Endrede applikasjonsfiler

- `backend/public_assets/michael_profile.jpg`: Michaels godkjente portrett er lagt inn som lokal webressurs.
- `backend/webapp.py`: portrett i startsidens Michael-valg, lærerheader, chatbobler, quiz-coach og bunnmeny.
- `backend/webapp.py`: tre hovedemner vises først på mobil; resten åpnes med en språkstyrt «Flere emner»-knapp.
- `tests/test_michael_mobile_ui_contract.py`: kontrakttest for bilde, språk, mobilknapper og eksisterende chat-endepunkt.

## Mobilgrep

Michael-siden har fått en rolig, kompakt profilheader med ekte portrett, rolle, 16 års erfaring og online-status. Flaggdekoren skjules bare i Michael-modus på mobil. De tre første emnevalgene har minst 50 px trykkhøyde, mens øvrige temaer og regnestykker er sammenfoldet. Chatfelt og sendeknapp har også minst 50 px høyde.

## Avgrensning

Ingen endringer i `/api/teacher/chat`, AI-modeller, TTS, auth, kvoter, Stripe, RevenueCat eller øvrig betalingslogikk.

## Verifisering

- Python-syntaks: PASS.
- 21 målrettede regresjons- og kontrakttester: PASS.
- `git diff --check`: PASS med kun eksisterende Windows LF/CRLF-varsler.

Klar for QA-gate og visuell kontroll før eventuell publisering.
# PATCH REPORT: stabil lærerlyd og roligere Michael-mobilflate

## Endrede applikasjonsfiler

- `backend/webapp.py`: sporer aktiv lærer-tekst og avspillings-token, slik at lyd fra en annen svarboble erstatter gammel lyd med ett trykk.
- `backend/webapp.py`: nullstiller lærerens aktive lydtekst ved ended, error, navigasjon og eksplisitt stopp.
- `backend/webapp.py`: viser tre kontekstforslag først på mobil og gjenbruker eksisterende NO/TH/EN «Flere emner» / «Vis færre».
- `backend/webapp.py`: reduserer mobilheader til 132 px og portrett til 94 × 112 px.
- `tests/test_michael_mobile_ui_contract.py`: tre nye kontrakttester for lydbytte, kontekstforslag og kompakt header.

## Tester og resultater

- Python-syntaks: PASS.
- Inline JavaScript-syntaks via Node: PASS.
- Michael-kontrakttester: 7/7 PASS.
- Hele oppdagede testsuiten: 24/24 PASS.
- `git diff --check`: PASS med kun Windows LF/CRLF-varsel.
- Fersk produksjonsdiagnostikk før patch: to sekvensielle TTS-kall ga HTTP 200, `audio/mpeg`, `ID3` og ikke-tomme ElevenLabs-filer. Backend ble derfor ikke endret.

## Omfang

Ingen endring i `/api/tts/stream`, stemmer, AI-chat, auth, kvoter, Stripe, RevenueCat eller premiumstatus. Ingen nye learner-facing tekster.

## Gjenværende risiko og rollback

Automatiske tester beviser state-kontrakten og syntaksen, men faktisk hørbar mobilavspilling krever kontroll i en ekte innlogget mobilnettleser etter eventuell deploy. Rollback er én frontend-revert av aktiv tekst/token, `mobile-extra` og de tre mobile CSS-reglene.

Klar for Agent 4.

---
# PATCH REPORT: informasjonskort med to elevvalg

## Endring

- `backend/webapp.py`: skiltkortet viser nå bilde, kode/gruppe, navn og én
  konkret driver action/forklaring. «TEORI», gjentatt tips og begge indre
  knapper er fjernet.
- `backend/webapp.py`: handlingsområdet under svaret har bare «Øv på dette
  skiltet» og lokalisert «Spør Michael».
- `backend/webapp.py`: mobilbildet er redusert til 96 × 96 px og tekststørrelsen
  strammet slik at kortet passer uten horisontal side-scroll.
- `tests/test_michael_mobile_ui_contract.py`: kontrakt for null kortknapper og
  nøyaktig de to ønskede handlingstypene.

## Verifisering

- Python-syntaks: PASS.
- 25 målrettede UI-, API- og lærerbackendtester: PASS.
- Lokal 390 × 844 px nettleserkontroll: PASS — kort 130 px høyt, null knapper i
  kortet, to handlinger under og ingen horisontal overflow.
- Produksjonens `/api/tts/status` ble kontrollert separat etter spørsmål fra
  Michael og rapporterer `elevenlabs_model_id: eleven_v3`; lydbackend er ikke
  endret i denne patchen.
- Ingen commit, push eller deploy.

Rollback er å reversere de avgrensede kort-/handlingslinjene og den nye testen.
Klar for Agent 4.

---
# PATCH REPORT: ett øvingsvalg og Michael i inputfeltet

- Fjernet «Spør Michael» som egen kontekstknapp.
- Endret lærerinput til språkstyrt «Spør Michael...» / thai / engelsk.
- Lagt til egen språkstyrt chat-handling «Øv på liknende» uten å endre
  «Øv på dette skiltet» i skiltbibliotekets detaljpanel.
- Handlingsraden bruker én fullbreddeknapp og beholder dagens skiltfiltrerte
  øvingsrute som grunnlag for senere utvidelse til veikryss.
- 25 målrettede tester PASS; lokal 390 px kontroll viser én knapp, korrekt
  placeholder og ingen horisontal overflow.
- Ingen backend-, betalings- eller deployendring. Ingen commit/push.

Klar for Agent 4.

---
---

# PATCH REPORT: 10-spørsmåls quizøkter

- `backend/webapp.py`: én `QUIZ_SESSION_SIZE = 10` brukes av tilfeldig quiz,
  daglig test, kategoriquiz, kategori-fallback og feilbankøkt.
- Starttelleren viser «Spørsmål 1 av 10»; videre teller bruker faktisk lastet
  øktlengde og avslutter via eksisterende `showEnd()`.
- Oppsummeringen tilbyr ny tilsvarende økt og en språkstyrt knapp til Michael.
- Backendens eksisterende standard `count=10` er bekreftet og trenger ingen
  endring. Eksamen (45) og skiltøving (1) er bevart.
- Ny kontrakttest dekker backendstandard, alle frontendkall, fremdrift,
  oppsummeringsvalg og de eksplisitte unntakene.

Ingen endring i spørsmål, access/consume, guest/free/premium, auth eller betaling.
Klar for Agent 4.
