# Hindringer for privat bokleveranse

## 21.10.2026 – Railway

Railway har satt bygg og deploy på pause under en driftsfeil. Statussiden bekreftet
fortsatt stans kl.17:18 UTC: https://status.railway.com/ . Oppretting av privat
objektlagring ble avvist med «Deploys have been paused temporarily».

Berørt leveranse: privat lagring, ny deploy og faktisk innlogget produksjonskontroll.
Ansvarlig for gjenoppretting: Railway. Codex fullfører kode og lokale kontroller.
Minste løsning: gjenopprettet provisioning og deploy, deretter verifisert privat
opplasting og produksjonskontroll. Ingen elevåpning er autorisert av denne statusen.

## 21.10.2026 – privat innhold i offentlig kildekodelager

Hovedrepositoriet er offentlig. En isolert lokal innholdscommit må derfor ikke
pushes. En ny kodegren fra kontrollert produksjonsbase inneholder bare kode,
syntetiske tester og driftsdokumentasjon. Katalog, fasit og private bilder går til
privat objektlagring. Direkte opplasting av hele backendpakken feilet med HTTP 413.
Minste løsning er lagringsleveransen beskrevet i PRIVATE_PREVIEW_DEPLOY.md.

## Åpne innholds- og kontrollpunkter

- Siste korrigerte bilde til trykt side 47 / PDF-side 42 er ikke sikkert identifisert.
  Raden vises med mangelmerking; eksisterende filer bevares.
- Manglende oversettelser og bilder med uoversatt norsk tekst skjules eller merkes
  på valgt språk. Kandidater blir ikke automatisk godkjent.
- Skilt 202 har fortsatt eldre Thai-tekst i produksjonsdatabasen; lokal JSON er
  ikke bevis på retting av faktisk materialflyt. Separat validert migrering gjenstår.
- Senere versjonsbundet elevåpning, Del 2 og lovdelen er ikke levert gjennom denne
  første private milepælen. Ingen av disse kravene er fjernet fra hovedmålet.

Dette er kodegrenens leveranselogg. Hovedarbeidskopiens historiske rapporter og den
private kontrollpakken bevares separat.

## 21.10.2026 kl.18:00 UTC – faktisk leveransestatus

- Railway bekreftet kl.17:45 UTC at bygg og deploy fortsatt er stanset.
- Lesende produksjonskontroll kl.18:00:40 UTC: `/api/health` og `/th` svarte 200;
  bokinngang, bokvisning, katalog, direkte bilde og rå private ressursstier svarte
  404. Dette viser ikke at den nye tilgangssperren er verifisert i produksjon.
  Råbevis: lokal `output/private-book-20261021/live-guest-proof.json`.
- Ren kodecommit er `90172b55306c7e57efdd931b416db51020d636ab`, dokumentasjon
  `cf9463faef2c2a5abe504813db3e1dd11cc8d896`. Begge er pushet på kodegrenen.
  Ny kontroll av `merge-base --is-ancestor 418dac6 HEAD` ga exit 1.
- GitHub-integrasjonen avviste PR-oppretting med 403, «Resource not accessible
  by integration». Nettleseren viste ingen innlogget GitHub-konto. Ingen PR ble
  opprettet. Berørt: PR-integrasjon. Minste løsning er eksisterende autorisert
  GitHub-tilgang med PR-skriverettighet; ingen utvidede rettigheter er gitt her.
- Claude CLI med direkte native executable løste tidligere spawn-feil, men
  nettverkstilgjengelig kjøring ble avvist: organisasjonen har deaktivert Claude
  subscription access for Claude Code. Ingen Claude-kontroll er bestått.
  En separat agents faktiske kodekontroll er gjennomført; lagringsgrenser ble
  rettet og testet. Den kontrollen beviser ikke privat bucket eller live-flyt.
  Råbevis for CLI: lokal `output/private-book-20261021/outside-review-native.json`.

Privat opplasting, read-back av faktiske lagrede bytes, anonym bucket-avvisning,
ny deploy-ID og innlogget produksjonskontroll gjenstår. Ingen fungerende privat
lenke er levert, og ingen leksjoner er åpnet for elever.
