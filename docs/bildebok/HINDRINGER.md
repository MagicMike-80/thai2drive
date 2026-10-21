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
