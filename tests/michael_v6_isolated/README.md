# Michael V6: utkast til isolasjonskontroll

> Status 2026-11-18: GitHub Actions har nå kjørt faktisk V6-chatrute og en
> midlertidig MongoDB i samme nettverksløse container. Ekstern Docker-inspeksjon
> og interne kontroller kjøres før appimport. [Kjøring 44268952856](https://github.com/MagicMike-80/thai2drive/actions/runs/44268952856)
> bestod ni rutetester med syntetiske elevkontoer, oppgaver og progresjon i MongoDB.
> Chromium åpnet de tre språktilpassede websidene og sendte faktiske klikk til
> chatruten via en lokal pipe. Testen kjørte JWT- og tilgangsfunksjonene fra
> server.py mot syntetiske Premium- og gratiskontoer og nye gjester med egen
> nettlesernøkkel. Alle ni kombinasjoner av språk og tilgang bestod. Eldre
> gjeste-ID-er mangler eierskapsbevis og beholder vanlig quiz. Testen kontrollerte fire
> lagrede svar per elevflyt og én belastning per gratisoppgave. Vanlig quiz
> og V6 delte den siste ledige plassen i en separat samtidighetskontroll.
> Fire separate webkontroller bestod også. Testen simulerer innholdsgodkjenning og er
> ikke produksjonsgodkjenning. Avsnittene under beskriver historisk utkast og
> skal ikke leses som gjeldende kjørestatus.

Ikke kjør applikasjonen med dette oppsettet ennå. `bootstrap.py` stopper alltid
før applikasjonsimport, også hvis de foreløpige kontrollene skulle bestå.
Ingen workflow, testbranch eller container er opprettet.

`test_bootstrap_checks.py` tester kontrollfunksjonene med syntetiske data uten
å importere applikasjonen, lese miljøhemmeligheter eller kontakte nettverket.
Kjør bare denne filen lokalt med `python -I -B tests/michael_v6_isolated/test_bootstrap_checks.py`.
Dette er ikke en integrasjons- eller elevflyttest.

Før oppsettet kan brukes må et team gjennomgå og dokumentere:

1. En GitHub-hostet runner, testbranch-triggere og øvrige integrasjoner, og et
   kontrollert testimage med bekreftet, fast digest og låste avhengigheter.
2. Runnerkontroll av containerens `network=none`, ikke-root, ingen privilegier,
   read-only root/input, kapabiliteter og monteringer før den startes. Runneren
   selv har nettverk; bare testcontaineren kan være nettverksisolert.
3. At bootstrapens foreslåtte kontroller av IPv4/IPv6-ruter, forbindelser og
   DNS-pakker til reserverte testadresser, eksakt miljø- og monteringsliste,
   fravær av credentials og sockets faktisk fungerer i testcontaineren, og
   feiler lukket før applikasjonsimport ved manglende bevis.
4. At foreslåtte falske dotenv-, MongoDB-, modell- og e-posttjenester installeres
   før appimport og virker som ventet; uventede kall skal feile. Eksakt liste
   over inputfiler er foreslått, men må sammenlignes med testens faktiske behov.
5. Integrasjonstester for hele elevflyten med syntetiske oppgaver på NO/TH/EN,
   inkludert stokking, riktig/feil/uklart svar, fasitforespørsel, og avvisning av
   ukjente/utgåtte oppgaver. I tillegg kreves faglig kvalitetskontroll.

De foreløpige kontrollene er ikke bevis for at en prosess er i en container,
at alle mulige monteringer er trygge, eller at operativsystemet blokkerer
nettverk. Den ubetingede stoppen må ikke fjernes før hele oppsettet er klart.

## Avhengigheter identifisert ved statisk lesing

`teacher_chat.py` importerer ved oppstart FastAPI, Pydantic, Motor, dotenv,
litellm, `michael_greetings.py`, `ai_learning.py` og `media_catalog.py`.
`media_catalog.py` leser `learning_areas.json` ved import. `regelbank.json`
leses i flere av Michaels fagfunksjoner. Den pågående V6-piloten importerer
også `michael_v6_policy.py` og leser `AVAILABLE_QUESTION_FILTER` fra modulen
`server` eller `backend.server` som allerede er lastet. Ikke importer den ekte
serveren bare for dette filteret: gi testen et separat, gjennomgått filter og
kontroller at det samsvarer med serverens faktiske tilgjengelighetsregler.

Før appimport må bootstrap gjøre følgende *etter* at de eksterne og interne
isolasjonskontrollene er bestått:

- Bytte ut `dotenv.load_dotenv` med en funksjon som aldri leser filer.
- Bytte ut `motor.motor_asyncio.AsyncIOMotorClient` med en avgrenset falsk
  implementasjon som kun returnerer syntetiske samlinger. Appen bruker både
  `client[database][samling]` og attributt-tilgang. Ukjente metoder og uventet
  data skal feile, ikke returnere tilfeldige produksjonslignende svar.
- Installere falsk `litellm` før import; alle uventede modellkall skal feile.
  En test av modellflyten må bevisst angi faste syntetiske svar per tilfelle.
- Sperre SMTP og andre transportveier, og verifisere at verken credentials,
  `.env`, vertens hjemmemappe eller Docker-socket er montert.
- Ved V6-test: gi en syntetisk `server`-modul et faktisk representativt
  tilgjengelighetsfilter, og bruk kun en in-memory `questions`-samling. Test
  klientens oppgave-ID, språk, stokket svartekst, identitet og feilsituasjoner.

Falsk database må støtte de kallene det aktuelle scenariet faktisk bruker,
blant annet `find(...).limit(...).to_list(...)`; eldre chatflyt kan også kalle
`find(...).sort(...).to_list(...)`, `find_one`, `aggregate`, `insert_one` og
`insert_many`. Ikke lag en generell mock som skjuler uventede kall. Andre
funksjoner har sene importer av `micro_lessons` og bildebok-kode; eventuelle
ekstra filer må velges etter faktisk testscenario, ikke monter hele repoet.

Rene API-tester beviser ikke nettleserflyten. For den trengs i tillegg en
kontrollert nettleser inne i samme isolerte nettverk, eller et separat grundig
testoppsett med syntetiske svar og ingen produksjonsendepunkt. Versjonene av
Python-pakker og nettleser må låses og gjennomgås før image bygges.

## Tilgjengelig kjøreplattform

Det ble ikke funnet Docker-, Podman- eller containerd-kommandolinje/servicer på
denne maskinen; WSL oppgir ingen installert distribusjon. Windows sin kontroll
av Sandbox-funksjonen svarte at den krever forhøyet tilgang. En container kan
derfor ikke bekreftes lokalt uten ytterligere systemoppsett. GitHub-hostet
Linux-runner er en mulig vei uten endring av lokal administratoroppsett, men
workflow, repotillatelser, andre integrasjoner og image må fortsatt undersøkes.
GitHub-koblingens repo- og profilanrop feilet med transportfeil under kontrollen;
det beviser ikke at brukeren mangler tilgang. Ingen appimport er gjennomført.

Oppdatering: GitHub-repoanrop fungerte senere og oppga tilgang for repoet, men
koblingen tillot ikke lesing av Actions-policy eller repo-webhooks. Faktisk
Railway-tilkobling og annen branch-automatisering er dermed ikke avklart.

En mulig **base**, ikke et ferdig testimage, er Docker Official Image sin
`python:3.11-slim-bookworm`. Registry returnerte manifest-list
`sha256:a83ba18aef0f865b1a4a611c2cf460fe446f2795673bbb9fe43be570439e3b39`
og Linux/amd64-manifest
`sha256:e8c69d86735f6df3efa06b324694fe51f0422785f83a3bd463052636c2421944`.
Digestene er registrert fra Docker Registry, ikke bevis på at imageinnholdet
er gjennomgått eller at et testimage er bygget. `requirements-candidate.txt`
viser et foreslått minimalt sett med versjoner og hjul-hasher innhentet fra
PyPIs JSON-metadata for CPython 3.11 og Linux x86-64. Filen er et utkast;
avhengighetslukking, faktisk hjulinnhold, image-lag, opprinnelse og sikkerhet
mangler gjennomgang og installasjonstest før bruk. Fastlåsing er ikke alene
godkjenning. Modeller og databaser skal uansett være falske under testen.
`Dockerfile.candidate` viser hvordan et slikt image kan bygges; det har ikke
blitt bygget eller kjørt, og har ingen appkode. En lokal pip-dry-run mot PyPI
valgte og kontrollerte hasher for alle de 13 hjulene for det angitte målet;
det er ikke bevis for hvordan et bygget image oppfører seg.

Bootstrap har nå en forberedt rekkefølge for installasjon av falske tjenester
før import og kjøring av `v6_endpoint_scenarios.py`. Rekkefølgen ligger etter
en **ubetinget stopp** og kan dermed ikke utføres. Sju tester for gate-logikk
og tre for stubber besto lokalt på syntetiske data, men ingen container eller
app er startet, og integrasjonsscenarioene er ikke kjørt. En sikkerhetsreview
må kontrollere både kilde, inputliste og faktisk ekstern containerinspeksjon
før den ubetingede stoppen kan fjernes.

`workflow.candidate.yml` er et inaktivt utkast lagret utenfor
`.github/workflows`. Det beskriver en separat testbranch, ingen secrets/OIDC,
checkout med fast commit, bygg av kandidatimage og validering av containeren
før oppstart. `inspect_container.py` og tre syntetiske tester er forberedt;
ingen ekte Docker-inspeksjon eller workflowkjøring har funnet sted. Utkastet
må ikke flyttes til aktiv workflow eller pushes før gjennomgang og avklaring
av GitHub Actions-policy og eventuelle andre repo-webhooks/integrasjoner.

Railway GraphQL returnerte én produksjonstrigger for denne servicen, `main`.
Koordinatoren rapporterte at GitHub-innstillinger viste ingen repo-webhooks,
at Actions er tillatt og at standardtoken er read-only. Det utelukker ikke
automatisering gjennom installerte GitHub Apps. Ingen innstillinger er endret.

De forberedte ASGI-testene bruker en syntetisk signert oppgave og kaller
teacher/chat. De tester verken selve oppgaveutleveringen i `server.py` eller
en ekte nettleser. En separat JavaScript-test bruker en simulert nettleser-
kontekst; den er ikke en full DOM- eller ende-til-ende-test. Begge delene må
dekkes før full elevflyt kan regnes som verifisert.

## Gjenværende porter før mulig testbranch-kjøring

- **Netlify:** Les relevante Netlify-prosjekter og dokumenter om noen er koblet
  til `MagicMike-80/thai2drive`. For hvert treff må produksjonsbranch,
  branch-deploy-valg (ingen, alle eller bestemte branches), automatisk bygging
  og publiseringskontekst kontrolleres. Fravær av GitHub repo-webhooks alene
  utelukker ikke aktivitet via en installert GitHub App. Ikke les verdier av
  miljøvariabler. [Netlify: branch deploys](https://docs.netlify.com/deploy/deploy-types/branch-deploys/).
- **Google Cloud Build:** Kontroller tilgjengelige prosjekter og regioner for
  triggere til dette repoet. Registrer om hver trigger er aktiv, push-event,
  branch-regex/invertering, inkluderte/utelatte filbaner og hvilken build-
  konfigurasjon og deploydestinasjon som brukes. Avgjør uttrykkelig om
  `test/michael-v6-isolation` kan treffe en aktiv trigger. Ikke hent eller
  skriv ut nøkler eller verdier for hemmeligheter. [Cloud Build-triggere](https://docs.cloud.google.com/build/docs/automating-builds/create-manage-triggers).
- **Øvrige GitHub Apps:** Avklar installasjonsomfang og om Claude, ChatGPT Codex
  eller Emergent.sh har ekstern push-automatisering eller deployer fra repoet.
  Appinstallasjon alene viser ikke at slike triggere er aktive eller inaktive.
- **Testoppsett:** Gjennomgå checkout-commit, Dockerfile, alle 13 låste hjul,
  containerinspektør, bootstrap, testdata og faktisk containerkonfigurasjon.
  Godkjenn evt. en første sperretest separat: den må stoppe før appimport og
  forventes å feile med `external container attestation is not reviewed`.
  Falske tjenester og NO/TH/EN-endepunkttester kan ikke anses kjørt før den
  separate gjennomgangen og en bevist isolert testprosess faktisk er fullført.
- **Full brukerflyt:** En vellykket sperretest eller ASGI-test beviser ikke
  oppgaveutlevering, faktiske adgangsregler eller hele nettleserflyten. Dette
  trenger egne isolerte integrasjonstester med syntetiske brukere og oppgaver.

Byggkonteksten i workflow-utkastet er nå en ny tempmappe med bare to eksplisitt
uttrukne, versjonskontrollerte filer: Dockerfile og kravlisten. Inspektørens
prosess starter med tømt miljø. GitHub-runneren har fortsatt nettverk og kan ha
egne kortvarige tjenestetokens; den må derfor ikke behandles som isolert.
