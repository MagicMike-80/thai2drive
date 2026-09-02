# SOLUTION BLUEPRINT: juridisk vern for høyreregelen ved venstresving

## Mål

Rette den dokumenterte § 7 nr. 2-feilen med én liten backendpatch som både
styrker Michaels kunnskapsinstruks og garanterer korrekt svar i den presise
venstresving-situasjonen.

## Ikke-mål

- Ingen generell regelmotor eller stor omskriving av prompten.
- Ingen endring av API-kontrakt, frontend, database, media, auth, kvoter,
  premium, Stripe, RevenueCat, betaling, TTS eller deploykonfigurasjon.
- Ingen automatisk «Ja» for alle spørsmål som inneholder venstresving eller
  høyreregelen.

## Endrede filer

1. `backend/teacher_chat.py`
   - Legg til en språktilpasset § 7 nr. 2-instruks i systemprompten.
   - Legg til en smal intent-detektor som krever høyreregel, venstresving og
     møtende/høyre-side-kontekst.
   - Legg til en deterministisk språktilpasset fail-safe etter modell/fallback
     og før `sign_ids`/media beregnes.
   - Fjern generisk RAG-kontekst som fallback for responsens skilt-ID-er. Bare
     kontrollerte treff i brukerens eller Michaels tekst kan velges.
2. `backend/tests/test_teacher_chat_fallback.py`
   - Lås promptfakta, positiv NO/TH/EN-matrise, modellens kategoriske feil og
     negative grenseeksempler.
3. `app-brief/PATCH_REPORT.md` og `app-brief/QA_REPORT.md`
   - Dokumenter patch- og QA-evidens.

## Dataflyt og kontrakt

`TeacherChatRequest` og `TeacherChatResponse` endres ikke. Normal flyt er:
brukermelding → systemprompt/RAG → modell → kortformat → § 7 nr. 2-fail-safe →
streng skiltvalidering fra eksplisitt bruker-/svarmatch → eksisterende media →
respons. Fail-safe returnerer bare tekst og bred RAG-kontekst kan ikke lenger
introdusere et urelatert skilt.

## Språk og tilgang

Korrekt kanonisk svar finnes separat for norsk, thai og engelsk. Aktivt
`language`-felt bestemmer hele svaret. Guest/gratis/premium følger samme
eksisterende endpoint uten tilgangsendring.

## Patchplan

1. Definer `_SECTION_7_2_PROMPT` for NO/TH/EN og injiser riktig språkvariant i
   `_build_system_prompt`.
2. Implementer `_is_section_7_2_left_turn_query` med kontrollerte språkfraser.
3. Implementer `_apply_section_7_2_fail_safe` og bruk den én gang etter både
   vellykket modellrespons og feilfallback.
4. Implementer `_strict_response_sign_ids` uten generisk kontekstfallback.
5. Legg til smale enhetstester og kjør eksisterende relevante/full suite.
6. QA diff, språk, hemmeligheter og regresjonsflater før avgrenset push.

## Test og manuell verifisering

- Prompten inneholder § 7 nr. 2-fakta på NO/TH/EN.
- Feilmodellsvaret «Nei, dette er ikke høyreregelen» korrigeres for den eksakte
  situasjonen i alle tre språk.
- «Hva betyr høyreregelen?», «Hvordan svinger jeg til venstre?» og spørsmål om
  gående/syklende ved sving utløser ikke fail-safe.
- «Hva sier paragraf 7 andre ledd?» inneholder begge lovsetningene og har
  `sign_ids=[]`/`media=[]`, selv om RAG-konteksten inneholder et annet skilt.
- Eksisterende Michael-, media- og kontrakttester er grønne.
- Etter deploy: ferske live-canaries på NO/TH/EN og kontroll av versjonsmarkør.

## Rollback og risiko

Rollback er én revert av den avgrensede committen; ingen data migreres. Største
risiko er et for bredt intent-treff, redusert ved å kreve tre samtidige
begrepsgrupper og ved negative tester.

**READY FOR AGENT 3**

---

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

# SOLUTION BLUEPRINT: additiv `media_catalog` med streng seed-gate

## Beslutning og leveransestatus

Oppgaven deles i to små leveranser fordi kodekontrakten er implementerbar, men
det bestilte produksjonsinnholdet ikke er det:

- **Patch A er klar for implementasjon nå:** felles, testbart katalogskjema,
  indekser, fail-stop-serialisering, JWT-beskyttet leserute, et begrenset
  Michael-oppslag og et seed-verktøy som validerer/dry-runner en ekstern
  manifestfil. Tom katalog endrer ingen synlig produksjonsflyt.
- **Patch B er blokkert:** aktiv seeding av de ti postene og bytte av det
  eksisterende biblioteket til katalogen. Dette skjer først når innholdseier har
  levert den komplette, godkjente manifesten som beskrives nedenfor.

Dette er den minste production-sikre løsningen. Tomt eller ufullstendig
`media_catalog` gir tekst-only i Michael og beholder dagens bibliotek uendret.

## Mål

- Etabler `media_catalog` som én additiv source of truth for nye, kuraterte
  videoer og podkaster.
- Returner kun den valgte språkpostens tittel og beskrivelse; aldri hele
  `i18n`-objektet eller tekst fra et annet språk.
- La Michael legge til maksimalt ett katalogmedium fra kontrollerte tags uten
  at modellen kan levere eller konstruere URL-en.
- Legg til `GET /api/library/media?language=no|th|en` med eksisterende JWT-
  avhengighet og deterministisk sortering.
- Gjør seeding idempotent, forhåndsvalidert og eksplisitt før den kan skrive.

## Eksplisitte ikke-mål

- Ingen automatisk migrasjon, kopiering eller sletting av `learning_videos`,
  `learning_podcasts` eller `michael_materials`.
- Ingen oppdiktede oversettelser, beskrivelser, tags, URL-er eller thumbnails.
- Ingen aktivering av de ti ønskede postene før hele manifesten er godkjent.
- Ingen endring i authimplementasjon, gjest/gratis/premium, kvoter, Stripe,
  RevenueCat, betaling, quiz, TTS, mobilapp eller hemmeligheter.
- Ingen produksjons-POST mot Michael i QA; chatruten skriver historikk/logg.

## Skjema og språkmodell

Opprett en liten delt modul `backend/media_catalog.py`. Den skal inneholde
konstanter, ren validering, lokalisert serialisering og deterministisk ranking,
slik at `server.py`, `teacher_chat.py`, seed-skriptet og enhetstester bruker
samme regler.

Et gyldig MongoDB-dokument har:

```text
media_id: string, unik og ikke tom
type: "video" | "podcast"
category: "vikeplikt" | "stoppelengde" | "skilt" |
          "morkekjoring" | "hav_regelen"
tags: unik liste med normaliserte, godkjente kanoniske emnetags
media_url: sikker, ikke tom URL
thumbnail_url: sikker, ikke tom URL
is_active: boolean, default true
content_language: "no" | "th" | "en" | "neutral"
i18n.no.title / i18n.no.description: ikke tom
i18n.th.title / i18n.th.description: ikke tom
i18n.en.title / i18n.en.description: ikke tom
created_at / updated_at: UTC-tid satt av seedlaget
```

`content_language` er et nødvendig, additivt sikkerhetsfelt. Ett toppnivå-
`media_url` kan ikke representere tre forskjellige talespor. En post kan bare
eksponeres når `content_language == requested_language`, eller når innholdseier
uttrykkelig har godkjent filen som `neutral` fordi den ikke inneholder tale,
tekst eller andre språkbærende elementer. Flere språkversjoner av samme tema er
separate dokumenter med separate unike `media_id`-er, for eksempel suffiks
`_no`, `_th` og `_en`. De ti foreslåtte ID-ene kan derfor bare beholdes uten
språksuffiks dersom hver tilhørende fil er dokumentert språkneutral, eller hvis
ID-en representerer kun ett eksplisitt `content_language` og skjules for de to
andre språkene.

Metadata-`i18n` alene overstyrer aldri denne filspråkgaten. Manglende eller
ugyldig `content_language`, tittel, beskrivelse eller URL gjør posten usynlig.
Det brukes aldri norsk fallback.

Tillatte URL-er er absolutte `https://`-URL-er eller eksisterende lokale
`/api/assets/`-URL-er. Generell `/api/`, `http://`, `javascript:`, `data:` og
protokollrelative URL-er avvises. Seedens apply-modus må i tillegg verifisere
HTTP 200 og forventet video/audio/bilde-innholdstype for media og thumbnail før
første databaseskriving. Relative assets verifiseres mot en eksplisitt
`--base-url`; ingen thumbnail avledes fra filnavn.

## Indekser og databaseoppstart

Utvid `backend/create_indexes.py` gjennom dagens idempotente startupmønster:

1. `media_id_unique`: `{media_id: 1}`, `unique=True`.
2. `media_active_language_tags`: `{is_active: 1, content_language: 1, tags: 1}`
   for Michael-oppslaget og aktiv språkfiltrering.

Bibliotekets lille resultatsett sorteres etter en eksplisitt kategoriorden i
Python; det krever ikke en tredje indeks før målinger viser behov. En
indeksfeil ved eksisterende duplikater skal logges tydelig og må ikke repareres
ved automatisk sletting. Read-only Pain Hunter-sjekk viste ingen eksisterende
samling, så deployrekkefølgen er indeks først, seed etterpå.

## Felles lokaliserings- og responskontrakt

Den delte serializeren tar dokument + eksplisitt språk og returnerer enten
`None` eller kun:

```json
{
  "id": "vid_stopp_01",
  "media_id": "vid_stopp_01",
  "type": "video",
  "category": "stoppelengde",
  "tags": ["stoppelengde"],
  "url": "/api/assets/example.mp4",
  "thumbnail_url": "/api/assets/thumbs/example.jpg",
  "title": "lokalisert tittel",
  "description": "lokalisert beskrivelse",
  "caption": "samme lokaliserte beskrivelse"
}
```

`id`, `url` og `caption` bevarer Michaels eksisterende mediekortkontrakt;
`media_id`, `description`, `category`, `tags` og `thumbnail_url` er additive.
`i18n` og `content_language` sendes ikke til elevklienten. Kun `no`, `th` og
`en` aksepteres; ugyldig eller manglende språk gir ingen serialisert post.

## `GET /api/library/media`

Legg ruten i `backend/server.py`:

```text
GET /api/library/media?language=no|th|en
Authorization: Bearer <eksisterende JWT>
200 { "language": "no", "media": [lokaliserte poster] }
```

- `language` er obligatorisk og valideres til nøyaktig `no`, `th` eller `en`;
  manglende/ugyldig verdi gir 422, ikke norsk fallback.
- Bruk uendret `Depends(get_current_user)` og stol ikke på bruker-ID fra query.
- Spørr kun `is_active: true` og `content_language in [language, neutral]`.
- Serialiser fail-stop og sorter etter fast kategoriorden fra den godkjente
  enumen, deretter `type` (`video` før `podcast`), lokalisert tittel og
  `media_id`. Ukjent kategori er ugyldig og skjules av valideringen.
- Tom katalog returnerer HTTP 200 med `media: []`.

Patch A kobler **ikke** den synlige biblioteksiden over til en tom katalog.
Etter godkjent seed skal Patch B endre bare `loadLibrary()` til ett kall mot
denne ruten, splitte den allerede lokaliserte listen på `type`, og adaptere
feltene til dagens `buildVideoCard`/`buildPodcastCard`. Cache skal tømmes og
ruten lastes på nytt ved `setLang()`, ellers kan NO-data bli liggende når eleven
bytter til TH/EN. Ingen respons skal kopieres inn i flere `title_*`-felt og
senere gjenbrukes på et annet språk.

En ikke-innlogget bruker får eksisterende JWT-feil fra den nye ruten. Patch B
skal ikke legge inn en offentlig fallback til katalogen. Eventuell ny
learner-facing innloggingsmelding må leveres/godkjennes på alle tre språk av
innholdseier; frem til det kan eksisterende språkrene `lib_load_failed` brukes.

## Michael-oppslag

Legg en separat helper i `teacher_chat.py` som leser `media_catalog` og bruker
den delte rankeren:

- Katalogen spørres kun når requestens opprinnelige `language` er gyldig.
- Hent en begrenset mengde aktive dokumenter for valgt/neutral
  `content_language`; utfør ikke regex fra bruker- eller modelltekst i MongoDB.
- Normaliser melding, quizkontekst og dokumentets **godkjente** tags med samme
  rene normalisering. Bare hele, kontrollerte tagfraser teller. Tagdata er
  katalogstyrt; modellen får aldri velge URL.
- Rangering: flest eksakte tagtreff først, så fast kategoriorden, video før
  podcast og til slutt `media_id`. Returner maksimalt én serialisert post.
- Eksplisitt trafikkskilt beholder forrige sikkerhetskontrakt: når
  `explicit_sign_ids` finnes, returneres bare det eksakte skiltmediet og ingen
  katalogvideo/podkast.
- Uten eksplisitt skilt plasseres maksimalt ett katalogmedium i eksisterende
  `media`; dagens kuraterte ikke-katalogmedium kan fylle den andre plassen.
  Totalgrensen forblir to. Hvis katalogen er tom/ugyldig, beholdes dagens
  `michael_materials`-resultat uendret.
- Database-, validerings- eller URL-feil logges uten innhold/hemmeligheter og
  gir normal tekst-only/eksisterende media, aldri chatfeil.

`TeacherChatRequest.language` beholdes; ikke introduser et parallelt
`user_language`-felt. Dagens øvrige chatfallback endres ikke i denne patchen,
men kataloghelperen skal bruke den rå, validerte requestverdien og skjule media
ved ugyldig språk.

Frontendens `_buildTeacherMediaCard()` utvides i Patch A til å godta
`podcast`. Den bygger `<audio controls preload="none">` med DOM/
`textContent`, bruker bare den allerede lokaliserte tittelen/beskrivelsen og
avviser utrygg URL. Video beholder dagens åpner. Ingen `innerHTML` fra
modelltekst og ingen språkfallback introduseres.

## Idempotent seed-verktøy

Lag `backend/seed_media_catalog.py` som standard kjører **dry-run** og leser en
eksplisitt JSON-manifeststi. Kodepatchen kan inneholde den bestilte listen over
forventede ID-er og deres eksplisitt oppgitte type/kategori, men skal ikke
inneholde tomme eller oppdiktede produksjonsposter. Verktøyet avviser en
manifest som mangler eller har ekstra ID-er:

```text
vid_stopp_01, vid_stopp_02, vid_stopp_03, pod_stopp_01
vid_vike_01, vid_vike_02, pod_vike_01
vid_hav_01
vid_skilt_01, vid_skilt_02
```

Den eneste metadata-mappingen Codex kan låse fra bestillingen er:

| ID-er | Type | Kategori |
|---|---|---|
| `vid_stopp_01`–`vid_stopp_03` | `video` | `stoppelengde` |
| `pod_stopp_01` | `podcast` | `stoppelengde` |
| `vid_vike_01`–`vid_vike_02` | `video` | `vikeplikt` |
| `pod_vike_01` | `podcast` | `vikeplikt` |
| `vid_hav_01` | `video` | `hav_regelen` |
| `vid_skilt_01`–`vid_skilt_02` | `video` | `skilt` |

Kategori `morkekjoring` støttes av skjemaet, men ingen av de ti postene flyttes
dit uten en eksplisitt redaksjonell avgjørelse; `vid_stopp_03` står under
Stoppelengde i bestillingen. Tags og øvrig innhold må fortsatt komme fra den
godkjente manifesten.

Flyt:

1. Les fil og valider **alle** dokumenter, enums, unike ID-er/tags,
   `content_language`, full `i18n` og URL-policy før Mongo-klient opprettes.
2. I apply-modus verifiser alle media-/thumbnail-URL-er før Mongo-klient og
   før første skriv. Én feil stopper hele kjøringen.
3. Bruk `MONGO_URL` og `DB_NAME` fra miljøet; aldri hardkod databasenavn eller
   skriv URI/hemmeligheter til logg.
4. Krev eksplisitt `--apply` og `--confirm-db-name <DB_NAME>` for skriving.
5. Upsert hver validerte post med filter `{media_id: ...}`, `$set` for
   kuraterte felt/`updated_at` og `$setOnInsert` for `created_at`. Ikke slett
   eller deaktiver andre poster.
6. Rapporter bare database, antall `matched`, `modified`, `upserted` og
   uendrede; ikke logg tokens eller hele innholdsdokumenter.
7. Før apply lagres en kontrollert before-snapshot for de berørte ID-ene.
   Rollback gjenoppretter tidligere dokumenter og setter nyinnsatte ID-er til
   `is_active:false`; den sletter ikke produksjonsdata.
8. Andre identiske apply skal gi `upserted=0` og `modified=0` bortsett fra at
   `updated_at` ikke må endres når innholdet er identisk.

Tester må injisere falsk collection/HTTP-validator; import eller dry-run skal
aldri koble til MongoDB.

## Trinnvis patchplan

### Patch A — implementerbar nå

1. Opprett `backend/media_catalog.py` med schema-/URL-/språkvalidering,
   serializer og ren ranker.
2. Legg de to indeksene til `backend/create_indexes.py`.
3. Legg JWT-ruten til `backend/server.py`; tom katalog skal gi 200/empty.
4. Legg fail-soft katalogoppslag og maks-én-komponering til
   `backend/teacher_chat.py`, uten å svekke eksakt-skilt-regelen.
5. Legg podkaststøtte i Michaels strukturerte kort i `backend/webapp.py`.
6. Lag det sikre seed-verktøyet og en dokumentert manifestmal uten
   produksjonsverdier; den skal feile tydelig før DB ved manglende data.
7. Legg isolerte tester. Deploy av Patch A kan skje etter QA fordi tom katalog
   ikke endrer dagens synlige bibliotek og Michael beholder fallback.

### Patch B — blokkert til godkjent manifest

1. Innholdseier fyller og godkjenner manifesten.
2. Codex kjører lokal validering/dry-run og URL-sjekk uten DB-skriv.
3. Codex verifiserer unik indeks, tar before-snapshot og kjører én eksplisitt
   apply mot korrekt `DB_NAME`, deretter en identisk andre apply.
4. Verifiser JWT-ruten read-only på NO/TH/EN og at feil språk/manglende JWT
   avvises. Ikke POST til produksjonschat.
5. Koble `loadLibrary()` over til katalogruten, med språkbytte-cache-reset og
   tester; deploy og verifiser live HTML/API.

## Tester og QA

- Ren schema-test: alle obligatoriske felter, enums, `is_active=True`, URL-
  avvisning, duplikate ID-er/tags og full `i18n`.
- Språkmatrise: distinkte NO/TH/EN-sentineler viser at serializeren bare
  returnerer valgt språk og aldri `i18n`; manglende felt skjuler posten.
- Mediespråk: NO-post skjules for TH/EN, neutral vises for alle, ugyldig eller
  manglende `content_language` skjules.
- Ranker: inaktiv post, null treff, taggrense, deterministisk tie-break og maks
  ett video/podcast-treff.
- Michael: eksisterende eksakt skilt forblir eksklusivt; bredt emnetreff får
  maks ett katalogmedium; katalogfeil beholder tekst/eksisterende media.
- API med dependency override/falsk DB: gyldig JWT-avhengighet, 401 uten auth,
  422 ved manglende/ugyldig språk, aktive poster, sortering og HTTP 200 empty.
- Seed med falsk collection: valider-alt-før-skriv, korrekt `$set`/
  `$setOnInsert`, andre kjøring uten endring, tellere og ingen sletting.
- Frontendkontrakt: `podcast` godtas, sikker URL kreves, `<audio>` bruker
  localized API-felter og ingen fallback/AI-HTML.
- Kjør relevante enhetstester, alle eksisterende trygge testsuiter, Python AST
  for alle `.py`, inline-JavaScript-syntaks og `git diff --check`. Ikke kjør
  `backend/tests/test_thai2drive_api.py` eller annen test som kan skrive til
  produksjon.

Etter Patch A-deploy verifiseres `/api/health` og en autentisert, read-only
`GET /api/library/media?language=<lang>` dersom en sikker test-JWT allerede er
tilgjengelig. Ingen nøkkel skal etterspørres eller rapporteres. At ruten svarer
200 med tom liste beviser kode/deploy, ikke at produksjonsseed er fullført.

## Rollback og produksjonsrisiko

Patch A kan reverseres ved å fjerne katalogruten/helperen, podkastgrenen og de
to indeksdefinisjonene; gamle samlinger og bibliotekflyt er urørt. En tom
samling/indeks er additiv og trenger ikke slettes ved rollback.

Etter Patch B deaktiveres nyinnsatte seed-ID-er ved rollback, mens eventuelle
tidligere versjoner gjenopprettes fra before-snapshot. Deretter går
`loadLibrary()` tilbake til dagens to endepunkter. Ingen automatisk database-
sletting inngår.

Største produksjonsrisiko er språklekkasje fra selve lyd-/videofilen, deretter
feil URL-mapping og stale frontendcache etter språkbytte. De avgrenses med
`content_language`, forhåndsverifiserte URL-er, fail-stop-serializer og cache-
reset før biblioteket kobles over.

## Data og avgjørelser som kreves fra Michael / innholdseier

For hver av de ti bestilte ID-ene må Patch B få:

1. endelig `type`, `category` og godkjent kanonisk `tags`-liste, inkludert
   godkjente søkebegreper/aliaser som dekker NO, TH og EN uten fuzzy matching;
2. eksakt `media_url` og `thumbnail_url`, samt bekreftelse på at hver svarer
   HTTP 200 med korrekt fil;
3. godkjent `title` og `description` for **alle tre språk**;
4. eksplisitt `content_language` for selve filen, eller dokumentert
   `neutral`; og
5. ved separate NO/TH/EN-filer: tre URL-er og tre separate, godkjente unike
   `media_id`-er per konsept.

Dette innholdet tilhører den andre agenten. Codex kan validere, seede og
produksjonssette det etter levering, men skal ikke skrive eller oversette det.

**Produksjonsseed og bibliotekovergang: BLOCKED inntil punktene 1–5 er levert.**

READY FOR AGENT 3 — PATCH A ONLY

---

# SOLUTION BLUEPRINT — rolig Michael-chat koblet til eksisterende medieflyt

## Beslutning og leveransegrense

Brukerens godkjente retning er en ChatGPT-/Codex-lignende samtaleflyt med
Thai2Drive-identitet: mørk navy, cyan/blå detaljer og eksisterende oransje
aksent. Dette løses som to små patcher. **Agent 3 skal nå implementere bare
Patch 1.** Patch 2 er en separat bibliotekleveranse og skal ikke blandes inn i
layoutrettingen.

## Patch 1 — implementeres nå

### Mål

- Komprimer toppområdet og gi Michael én sentrert, vertikal lesekolonne på
  omtrent 760 px på desktop og full tilgjengelig bredde på mobil.
- Behold eksisterende DOM-rekkefølge og flex-shell: header, scrollende
  meldingsliste og composer som bunnrad.
- Vis ordinære Michael-medier i én kolonne uten karusell eller horisontal
  avskjæring.
- Plasser leseren ved starten av et nytt langt Michael-svar etter at tilhørende
  media er ferdig lagt inn.
- La Michaels mediekort åpne den samme eksisterende, eksakte ressursflyten som
  biblioteket bruker, uten å endre responskontrakten eller katalogdata.

### Eksplisitte ikke-mål

- Ingen endring i `backend/server.py`, `backend/teacher_chat.py`, API,
  `media_catalog`, seed-data, database, mediematching eller språkinnhold.
- Ingen omforming eller migrering av selve biblioteksiden i Patch 1.
- Ingen endring i auth, gjeste-/gratis-/premiumregler, kvoter, Stripe,
  RevenueCat, betaling, TTS eller mobilappen.
- Ingen global redesign av `#app`, quiz, quiz-coach, skiltbibliotek eller andre
  skjermer.

## Filer og presise komponenter

Patch 1 kan bare endre:

- `backend/webapp.py`
  - scoped layout: `#app.teacher-mode`, `#screenTeacher`,
    `.teacher-chat-col`, `.teacher-header`, `.teacher-messages`, `.tm-row`,
    `.tm-chips`, `.tm-media-strip` og `.teacher-inputbar`
  - scroll: `_teacherAppendBubble()`, ny lokal
    `_teacherScrollToAnswerStart()` og kallstedet i `teacherSendMessage()`
  - mediaåpning: eksisterende `_openTeacherMediaVideo()`,
    `_buildTeacherMediaCard()` og eksisterende podcast-`<audio>`
- `tests/test_michael_mobile_ui_contract.py`
- `tests/test_michael_media_cards_contract.py`

Ingen andre produksjonsfiler er nødvendige.

## Layoutplan

1. Utvid bare Michael-rammen på desktop nok til å gi rolig side-luft, men legg
   en felles `width:min(760px,100%)`/`margin-inline:auto` på header,
   meldingslisten og composer i `.teacher-chat-col`. Mobil bruker 100 prosent
   minus eksisterende sikre sidepadding. Ikke endre global telefonramme for
   andre skjermer.
2. Komprimer `.teacher-header` fra 90 px til omtrent 72 px på desktop og mobil,
   reduser `.teacher-avatar` proporsjonalt til omtrent 48 px og behold navn,
   språk/meta, online-status og `.teacher-sidebar-toggle`. Oppdater samtidig
   `top`/`inset` på `.teacher-side-panel` og `.teacher-sidebar-backdrop` til den
   samme headerhøyden, slik at sidepanelet ikke får glippe eller overlapper.
3. Behold `.teacher-chat-col` som `display:flex; flex-direction:column;
   min-height:0`. `.teacher-messages` forblir den eneste vertikale
   scrollflaten, mens `.teacher-inputbar` beholder `flex-shrink:0`, safe-area og
   dagens textarea/sendeknapp. Ikke bruk `position:fixed` eller `sticky` på
   composeren.
4. Scope ordinær chat til `min-width:0; max-width:100%; overflow-x:clip` eller
   tilsvarende sikker klipping på den sentrerte wrapperen, og sørg for at
   `.tm-row`, `.tm-bubble`, `.tm-chips`, `.tm-sign-strip`, `.tm-media-strip` og
   kortenes innhold kan krympe og bryte tekst. Ingen `white-space:nowrap` på
   innhold som kan være langt på thai.
5. Sett `#screenTeacher .tm-media-strip` til nøyaktig én kolonne på alle
   breakpoints. Behold grensen på opptil to godkjente API-medier som to kort
   under hverandre; ikke gjør den om til karusell. Eksakt skilt beholder dagens
   kompakte 80/90 px-bilde. Quiz-coach-regler skal ikke endres.
6. Sidepanelet for emner/historikk forblir et overlay og tar aldri permanent
   bredde fra samtalen. Eksisterende åpne/lukke-, backdrop- og Escape-logikk
   beholdes.

## Scrollplan

- `_teacherAppendBubble()` skal fortsatt føre brukerens egen melding til bunnen,
  men skal ikke sende et nytt assistentsvar til listens absolutte bunn.
- Legg én lokal helper `_teacherScrollToAnswerStart(bubble)` som finner nærmeste
  `.tm-row`, og setter `.teacher-messages.scrollTop` til radens `offsetTop` med
  en liten intern toppmargin. Bruk deterministisk lokal scroll; ikke global
  `scrollIntoView`, som kan flytte hele appvinduet.
- I `teacherSendMessage()` kalles helperen etter
  `_teacherLinkSignReferences()`, `_teacherAppendMediaCards()` og den awaitede
  `_teacherAppendSignCards()`. Dermed er kortenes endelige høyde kjent før
  lesepunktet settes.
- Den eldre asynkrone `fetchVideoForTopic()`-callbacken skal bruke samme helper
  etter innsetting og ikke `msgs.scrollTop = msgs.scrollHeight`. Eksisterende
  startscroll inne i `_teacherAppendSignCards()` samles i helperen, slik at det
  bare finnes én regel.
- Feil-/tekst-only-svar bruker samme startplassering og må aldri blokkere
  meldingen dersom scrolling eller media feiler.

## Minimal kobling til bibliotek og avspilling

Patch 1 gjenbruker dagens strukturerte `media`-payload (`id`, `type`, `url`,
`title`, `caption`, eventuelt `sign_id`) og lager ingen ny frontendkontrakt:

- `video`: hele videokontrollen fortsetter å kalle
  `_openTeacherMediaVideo(media)`. Den bygger en språkren, midlertidig post i
  eksisterende `_videosCached` og åpner eksisterende `openVideoPlayer()`.
  `openVideoPlayer()` registrerer aktiv skjerm som retur, så lukk fører tilbake
  til `screenTeacher` med samtale-DOM, sesjon og scrollposisjon intakt.
- `podcast`: behold sikker, eksakt inline `<audio controls preload="none">` med
  katalogens godkjente URL. Dette er samme native avspillingsmønster som dagens
  bibliotekspodkast, og navigerer derfor ikke bort eller nullstiller chatten.
- `sign`: behold eksisterende autoritative skiltdetalj via
  `_openTeacherSignDetailById(media.sign_id)`.
- `intersection_image`: forblir et ikke-navigerende, språkmerket bilde under
  riktig svar.

Kortene er dermed direkte innganger til korrekt ressurs/avspiller, mens
bibliotekets fulle kategorisering og deep-link/highlight av en katalogpost
utsettes til Patch 2. Ikke legg inn en knapp som bare sender eleven til toppen
av biblioteket; det er ikke en eksakt ressurskobling.

## Språk, tilgang og feilhåndtering

Patchen legger ikke til learner-facing tekst. Den bruker bare allerede
lokalisert `media.title`/`media.caption` og eksisterende globale NO/TH/EN-nøkler.
Manglende tittel, bildetekst eller sikker URL fortsetter å skjule kortet
fail-stop. Tekstsvar og composer fungerer selv om mediekort, bilde, video eller
podkast ikke kan åpnes. Tilgangs- og premiumkonsekvensen er null.

## Akseptansekriterier

1. Ved 320, 390, 768 px og vanlig desktopbredde finnes ingen horisontal
   scrolling eller avskåret kort; media står i én vertikal kolonne.
2. Desktop viser én sentrert lesekolonne på omtrent 700–800 px med rolig luft på
   sidene. Mobil bruker hele tilgjengelige bredden.
3. Headeren er tydelig lavere enn dagens samlede toppområde, men navn, status,
   aktivt språk og emneknapp er synlige og brukbare.
4. Et langt nytt Michael-svar begynner i leseposisjonen. Dette gjelder også når
   strukturert media, awaitet skiltkort eller eldre asynkron video legges til.
5. Composer forblir synlig nederst i flex-shellen, minst 56 px høy, med safe-area
   og uten overlapp med mobilens tastatur.
6. Video åpner eksisterende spiller på eksakt ressurs og lukking returnerer til
   samme Michael-samtale. Podcast spiller eksakt ressurs inline. Skilt åpner
   korrekt autoritativ detalj.
7. Sidepanelet åpnes/lukkes som før og reduserer ikke lesekolonnens bredde.
8. NO/TH/EN-innhold, API, auth, kvoter, premium og betaling er uendret.

## Tester og manuell verifisering

- Oppdater layoutkontrakten til å låse scoped ca. 72 px header/48 px avatar,
  sentrert 760 px-kolonne, flex-composer, panel-inset og overflow-sikring.
- Oppdater mediekontrakten til å kreve én kolonne også på desktop og bevare
  maksimalt to kort vertikalt, sikker URL, videoåpner, podcastkontroller og
  skiltdetalj.
- Legg kontrakt for `_teacherScrollToAnswerStart`, fravær av assistentens
  bunnscroll og kall etter umiddelbar/awaitet/asynkron mediainnsetting.
- Kjør de to målrettede kontrakttestene, relevante eksisterende Michael-tester,
  Python AST, inline-JavaScript-syntaks og `git diff --check`.
- Manuelt lokalt: lang NO-, TH- og EN-respons ved 390 px og desktop; to medier;
  video inn/ut av spiller; podcast play/pause; sidepanel åpent/lukket; composer
  med mobiltastatur. Ingen produksjonsmuterende chat-POST i QA.

## Rollback og risiko

Rollback er én frontend-revert av de scoped CSS-reglene, scrollhelperen og de
to kontrakttestene. Ingen data må migreres eller slettes. Største risiko er at
endrede bredder treffer andre skjermer eller at sen async media flytter
lesepunktet; derfor må alle regler scopes til `#app.teacher-mode`/
`#screenTeacher`, og alle media-paths bruke den ene scrollhelperen.

## Patch 2 — separat, ikke implementer nå

En senere godkjent patch kan forme hele `screenLibrary` som et samlet,
strukturert video-/podkastbibliotek, koble det til `media_catalog`, og legge til
eksakt deep-link/highlight og retur til opprinnelig samtale. Den patchen krever
egen smerteprofil, innholds-/seedgodkjenning og tester. Patch 1 skal ikke vente
på eller foregripe dette.

Ingen ny avgjørelse kreves fra Michael for Patch 1.

READY FOR AGENT 3 — PATCH 1 ONLY

---

# SOLUTION BLUEPRINT: eksakt skilt og kompakt ordkobling i Michael-chat

## Mål

Når elevens melding eksplisitt nevner ett av de tre avtalte skiltene, skal
Michael-responsen inneholde bare dette skiltet som strukturert media og
skiltreferanse:

- `202_0`: Vikeplikt / Give Way / ให้ทาง
- `204_0`: Stopp / Stop / หยุด
- `208_0`: repoets forkjørsvegskilt; ID-en er fasit, mens synlig navn hentes fra
  `GET /api/signs/208_0` (dagens norske datapost heter «Forkjørsrett» og engelsk
  navn er «Priority Road»)

Skiltet skal vises som et mørkt, kompakt kort med bilde innenfor 90 x 90 px.
Et kontrollert, lokalisert skiltnavn i Michael-teksten skal kunne åpne den samme
skiltdetaljen som kortet.

## Eksplisitte ikke-mål

- Ingen fuzzy matching, fri AI-tolkning av skilt eller modellgenererte URL-er.
- Ingen ny database, migrasjon, skiltmetadata eller duplisering av bilder.
- Ingen endring i promptens pedagogiske innhold, TTS, mobilappen, auth, kvoter,
  premium, Stripe, RevenueCat, betaling eller produksjonshemmeligheter.
- Ingen visning av «offisielle fargekoder» i denne patchen. Dagens API har ikke
  autoritativ fargemetadata. `SIGN_GROUP_META` er dekorativ UI-farge og må aldri
  merkes som en offisiell skiltfarge.
- Ingen redesign av Michael, skiltbiblioteket eller det eksisterende
  detaljpanelet.

## Filer og komponenter

Bare følgende applikasjonsfiler skal sannsynligvis endres:

- `backend/teacher_chat.py`
  - `_explicit_sign_ids_for_message`
  - `_get_relevant_michael_materials`
  - den avgrensede sign/media-dataflyten i lærerchat-endepunktet
- `backend/webapp.py`
  - `.tm-sign-*` og `.tm-media-card.sign` / `.tm-media-*`
  - `_buildAssistantContent`, `_buildTeacherMediaCard`,
    `_buildTeacherSignCard` og signkortinnsettingen
  - eksisterende `openSignDetail`/`GET /api/signs/{id}`-flyt
- målrettede tester i `backend/tests/test_michael_material_retrieval.py` og
  `tests/test_michael_mobile_ui_contract.py`; en egen liten alias-test kan
  brukes dersom det holder testen tydeligere.

`backend/server.py`, API-skjemaet, admin, skiltdata og betalings-/tilgangsfiler
skal ikke endres.

## Dataflyt og kontrakter

1. Kjør `_explicit_sign_ids_for_message(user_msg)` én gang for den aktuelle
   elevmeldingen. Resolveren skal bruke en liten, eksplisitt NO/TH/EN-tabell for
   bare `202_0`, `204_0` og `208_0`. Latin-baserte aliaser skal ha ord-/
   frasegrenser, slik at eksempelvis «stoppelengde» ikke blir `204_0`; thai
   bruker de eksplisitte hele frasene. Flere varianter som peker på samme ID
   dedupliseres i stabil rekkefølge.
2. Bevar dagens numeriske skiltoppslag og brede læreplansøk. Når en eksplisitt
   ID finnes, skal responsens `sign_ids` begrenses til den eller de eksplisitte
   ID-ene. Når ingen eksplisitt ID finnes, brukes dagens kontekstutledede
   `sign_ids` uendret.
3. Send eksplisitte ID-er separat inn i materialvalget. Hvis listen ikke er
   tom, skal `_get_relevant_michael_materials` gå i streng skiltmodus: filtrer
   kandidater før rangering og returner maksimalt ett `type="sign"`-element der
   `source_id`/`sign_ids` er nøyaktig samme ID. Ikke returner
   `intersection_image`, `video`, annet skilt eller et rent tag-treff i samme
   svar. Hvis det godkjente skiltmediet mangler komplett aktivt språk, trygg URL
   eller eksakt ID, returneres ingen media; tekst og strukturert `sign_ids`
   fortsetter slik at eksisterende GET-fallback kan brukes.
4. Når ingen eksplisitt ID finnes, behold dagens godkjente maks-to-materialer,
   rangering, språkkrav og tekst-only fallback. Dette hindrer regresjon for
   brede spørsmål om eksempelvis vikeplikt, trafikkskilt eller veikryss.
5. Behold `TeacherChatResponse` uendret: `reply`, `suggestions`, `sign_ids` og
   `media`. Backend er fortsatt source of truth; frontend bruker bare disse
   strukturerte feltene og `GET /api/signs/{id}`.
6. Frontend henter/skjuler skiltdetaljen fail-soft via eksisterende
   `GET /api/signs/{id}`. Et sign-mediekort og fallbackkort skal begge åpne
   `openSignDetail(sign)` med den hentede posten. Manglende GET, bilde eller
   aktiv språkverdi skjuler den berørte koblingen/kortdelen uten å blokkere
   Michael-teksten.

## Tekstkobling uten usikker HTML

- AI-svaret skal fortsatt bygges med DOM og `textContent`; ikke gjør modelltekst
  til `innerHTML`.
- Etter at en strukturert sign-ID er validert og signposten er hentet, søkes kun
  i tekstnoder i det aktuelle assistantsvar-et. Kandidater er det lokaliserte
  API-navnet og en liten kontrollert aliasliste for samme ID og aktivt språk.
- Bare første eksakte, grensekontrollerte forekomst erstattes med en ekte
  `<button type="button">`. Knappen får lokalisert navn i tilgjengelig label,
  tastaturfokus og åpner `openSignDetail(sign)`. Ingen teksttreff uten en
  strukturert ID, og ingen kobling på deler av andre ord.
- Manglende navnetreff omskriver ikke svaret; det kompakte kortet forblir den
  tilgjengelige inngangen til detaljen.
- Detaljpanelet starter på `appLang`. `name`, `explanation` og `driver_action`
  leses bare for valgt språk gjennom eksisterende strenge `_getProp`. Hvis
  tekst mangler, skjules den aktuelle detaljen fremfor norsk fallback.

## Kompakt layout og lesbarhet

- Både `.tm-sign-image` og signvarianten av `.tm-media-image` får
  `width/max-width:90px`, `height/max-height:90px` og `object-fit:contain` på
  desktop, mobil og quiz-coach.
- Signvarianten av `.tm-media-visual` skal ikke arve 180/160/150 px høyde fra
  generiske media. Bruk innholdstilpasset kompakt flate med minst 48 px
  klikkmål, mørk bakgrunn og eksisterende cyan/oransje aksent.
- Begge signkortvariantene skal være knapper eller inneholde én fullkort-knapp,
  med synlig `:focus-visible`, uten horisontal scrolling og uten nye
  handlingsknapper.
- Behold mobilens svartekst på minst `1.05rem` og `line-height:1.65`. Korttekst
  skal være kort `driver_action`, ellers `explanation`, kun på aktivt språk.
- Eksisterende deduplisering mellom `media.sign_id` og fallback-`sign_ids`
  beholdes, slik at samme skilt aldri rendres to ganger.

## Trinnvis patchplan

1. Utvid og test den eksplisitte aliasresolveren for `202_0`, `204_0` og
   `208_0`, inkludert negative kollisjonstester som «stoppelengde».
2. Legg inn streng eksklusivitetsgren i materialhelperen og oppdater testen som
   i dag forventer `sign-202` sammen med `tag-first`.
3. Bruk eksplisitte ID-er som responsens `sign_ids` og materialgrunnlag bare når
   de finnes; behold dagens brede flyt ellers.
4. Gjør begge eksisterende signkortvariantene kompakte og klikkbare via én
   liten, delt detaljåpner/cache rundt `GET /api/signs/{id}`.
5. Legg en sikker tekstnode-kobler for aktivt språk og kall den bare med den
   strukturerte signposten for det aktuelle svaret.
6. Lås kontrakten med backend- og frontendtester, deretter full lokal QA.

## Tester og manuell verifisering

- Aliasmatrise: minst ett eksplisitt uttrykk per NO/TH/EN for hver av de tre
  ID-ene; forvent bare henholdsvis `202_0`, `204_0` og `208_0`.
- Negative aliaser: «stoppelengde», «stop distance» og brede
  «trafikkskilt»/«vikeplikt» skal ikke feilaktig bli stoppskilt eller en annen
  eksplisitt ID.
- Retrieval: eksakt sign + tag-bilde + video + annet skilt skal returnere bare
  samme sign; deaktivert, språkufullstendig eller utrygt eksakt signmedium gir
  `media=[]`.
- Bred retrieval uten eksplisitt ID skal fortsatt kunne returnere dagens
  godkjente, begrensede media.
- Frontendkontrakt: 90 px-grense for begge signrenderere, ett kort per ID,
  klikkbart kort, sikker tekstnode-knapp, `GET /api/signs/{id}` og ingen bruk av
  `innerHTML` for AI-svaret.
- Språk: NO/TH/EN-navn og kortregel kommer bare fra aktivt språk; manglende
  verdi skjules. Ingen ny learner-facing label uten alle tre språk.
- Manuelt lokalt ved ca. 390 px: ordkobling, kort, fokus, detaljåpning,
  bilde-feilfallback, lang thai-tekst og ingen horisontal scrolling.
- Kjør relevante lokale enhetstester, Python AST/syntaks, inline-JavaScript-
  syntaks og `git diff --check`. Ikke kall produksjonens `POST /api/teacher/chat`
  eller andre tester som skriver samtale-, bruker- eller produksjonsdata.

## Tilgang, premium og produksjonsrisiko

Tilgangs- og premiumkonsekvensen er null: samme eksisterende chatrespons og
samme tilgangsgrenser brukes. Hovedrisikoene er falske substringtreff, dobbelt
skiltkort og språkfallback; de avgrenses med eksplisitte aliaser, eksakt
ID-filter, eksisterende deduplisering og fail-stop per språk.

Ved feil frontenddetalj skal Michael-svaret fortsatt vises som ren tekst.
Backendendringen kan rulles tilbake ved å fjerne de nye aliasene og den strenge
eksaktgrenen. Frontend kan rulles tilbake ved å fjerne detaljåpner/
tekstnodekobler og gjenopprette tidligere kort-CSS. Ingen data må migreres eller
slettes.

## Avgjørelser som krever Michael

Ingen ny avgjørelse er nødvendig for denne patchen. «Offisielle fargekoder» er
ikke tilgjengelige i dagens autoritative API og skal derfor skjules. Hvis feltet
senere ønskes, må Michael først godkjenne en autoritativ datakilde og en separat
metadataendring.

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

# CURRENT HANDOFF: `media_catalog`

Gjeldende oppgave styres av blueprinten **«additiv `media_catalog` med streng
seed-gate»** ovenfor. Agent 3 skal implementere bare Patch A. Aktiv
produksjonsseed og omkobling av biblioteksiden er BLOCKED til de fem oppførte
innholds- og filkravene er levert og godkjent.

READY FOR AGENT 3 — PATCH A ONLY
---

# SOLUTION BLUEPRINT: 10-spørsmåls quizpulser

1. Definer én frontendkonstant `QUIZ_SESSION_SIZE = 10`.
2. Bruk konstanten i tilfeldig quiz, kategoriquiz, kategori-fallback og
   feilbankøkter. Bevar 45 spørsmål i teoriprøvemodus og 1 i skiltøving.
3. Endre statisk startteller til «1 av 10»; dynamisk teller beholder faktisk
   antall spørsmål slik at tomme/korte kategorier aldri lyver.
4. Legg til en språkstyrt Michael-knapp på eksisterende oppsummeringsskjerm.
5. Bekreft med kontrakttest at backendstandard, frontendkall, teller,
   oppsummering og eksplisitte unntak er korrekte.

Ingen endring i spørsmål, tilgangskvoter, auth, betaling eller database.

READY FOR AGENT 3
---

# SOLUTION BLUEPRINT: én konkret ting fra Michael

1. Legg en siste, språktilpasset korthetsinstruks rett før LLM-kallet, slik at
   den overstyrer eldre pedagogiske langformatinstrukser.
2. Normaliser modellsvaret deterministisk: fjern media-/markdowntagger,
   overskrifter og forbudte metaforsetninger; behold høyst to setninger og
   maksimalt 30 mellomromsdelte ord (Thai: kort tegnbegrensning).
3. Returner `suggestions=[]`, maksimalt ett `sign_id` og bare det tilhørende
   `sign`-mediaobjektet. Ingen video/podcast i chatresponsen.
4. Fjern frontendens etterfølgende svarmeny og automatiske videokort, men
   behold inngangsmenyen før eleven spør.
5. Test NO/TH/EN, ord-/setningsgrense, metaforfilter, skiltmedia og fravær av
   svarmeny. Ingen endring i andre tjenester.

READY FOR AGENT 3

---

# SOLUTION BLUEPRINT: strukturerte skiltlenker i Michaels avklaringssvar

## Mål

Når Michael nevner et konkret, godkjent skilt i sin ferdige svartekst, skal
backend legge nøyaktig riktig ID i den eksisterende `sign_ids`-kontrakten og
bygge det eksisterende lokaliserte skiltmediet. Frontend skal gjenbruke dagens
sikre detaljåpning og vise maksimalt to kompakte, klikkbare 80 x 80 px skilt.

## Ikke-mål

- Ikke koble Høyreregelen eller andre generelle regler til et oppdiktet skilt.
- Ikke gjette fra frie ord som «stopp» eller «vikeplikt» i vanlig brødtekst;
  bare kontrollerte eksakte skiltuttrykk og skiltnummer kvalifiserer.
- Ingen endring i LLM-leverandør, database, admin, auth, kvoter, premium,
  betaling, TTS, portrett eller deploykonfigurasjon.

## Filer og dataflyt

1. `backend/teacher_chat.py`
   - Utvid den eksisterende kontrollerte resolveren til å kunne analysere både
     elevens melding og Michaels ferdige svar.
   - `202_0`: eksakte NO/TH/EN-varianter av Vikepliktskilt / Give Way sign /
     ป้ายให้ทาง og eksplisitt skilt 202.
   - `204_0`: eksakte NO/TH/EN-varianter av Stoppskilt / Stop sign / ป้ายหยุด
     og eksplisitt skilt 204.
   - Slå sammen eksplisitte bruker-ID-er og kontrollerte svar-ID-er i stabil
     rekkefølge, dedupliser og begrens til to.
   - Bygg media etter at svaret finnes, via eksisterende `_get_exact_sign_media`,
     og behold sluttfilteret slik at media-ID og `sign_ids` alltid samsvarer.
2. `backend/webapp.py`
   - Behold dagens datasikre rendering og klikk til `openSignDetail`.
   - Sett det konkrete skiltbildet til 80 x 80 px på mobil og desktop uten å
     redusere tekstlesbarhet eller lage horisontal overflow.
3. Tester
   - Lås NO/TH/EN, skiltnummer 202/204, deduplisering, maksimum to og negative
     grenser for Høyreregelen, stoppelengde og generisk vikepliktstekst.
   - Lås at live-responskontrakten gir samsvarende `sign_ids` og media, samt
     80 px klikkbart frontendkort.

## Språk, tilgang og risiko

Alle synlige titler og forklaringer kommer fortsatt fra eksisterende
språkfelt for valgt NO/TH/EN. Endringen berører ikke tilgangsnivåer. Største
risiko er falske positive teksttreff; derfor brukes en liten kontrollert tabell,
ordgrenser og negative regresjonstester, aldri generell AI-/regex-gjetting.

## Verifisering og rollback

Kjør målrettede backend- og frontendkontrakttester, full sikker lokal test-suite,
Python-/inline-JS-syntaks og `git diff --check`. Etter godkjent push skal ferske
NO/TH/EN-canaries bevise `202_0` og `204_0`, fungerende bilde-URL-er, 80 px DOM
og null skiltkobling for Høyreregelen alene. Rollback er én reversering av den
avgrensede committen; ingen datamigrering finnes.

READY FOR AGENT 3
