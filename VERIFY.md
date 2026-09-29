# Verifikasjonsprotokoll — Thai2Drive

**Mandat:** Ingen oppgave er ferdig før den er sett virke i produksjon, med rå
output som bevis. Lokale testresultater er ikke bevis.

**Rolle:** Verifikatøren har lesetilgang til repo, Railway og produksjonsdomenet.
Verifikatøren har **ingen skrivetilgang til kode** — verken i repoet eller lokalt.
Den som bygger noe, er den dårligste til å vurdere om det virker.

---

## Rekkefølge — alltid

### 1. PRODUKSJON FØRST

```bash
curl -I https://thai2drive.no/<sti>
curl -s https://thai2drive.no/<sti> | head -60
```

Krav for godkjenning:
- HTTP 200 på responsen
- `<html lang="...">` synlig i den **rå** HTML-en
- `<link rel="alternate" hreflang=...>` synlig i den **rå** HTML-en
- Kun ett språk i overskrifter, knapper og setninger

> **En 200 OK alene er ikke bevis.** Gammel side svarer også 200.
> Sjekk innholdet, ikke bare statuskoden.

### 2. PRODUKSJONS-COMMIT

- Hvilken commit-hash kjører live akkurat nå?
- Er den identisk med commiten som ble pushet?
- **Hvis nei → oppgaven er ikke deployet. Stopp der.** Ikke foreslå kodeendringer
  før deploy-spørsmålet er avklart.

### 3. DEPLOY-LOGG

- Deploy-ID, tidsstempel, commit-hash, sluttstatus
- Bygg- eller kjørefeil i sin helhet

Hvis deploy ikke har kjørt, oppgi hva som blokkerer: manglende tilgang, feilet
bygg, auto-deploy slått av, eller at domenet peker på en annen tjeneste enn den
`main` deployer til.

### 4. LOKALE TESTER SIST

```bash
pytest backend/tests/...
```

Dette er **støtte, ikke bevis**. Grønt her betyr ingenting hvis produksjon kjører
en eldre commit.

---

## Rapporteringsformat

| Punkt | Status | Bevis |
|---|---|---|
| Produksjon svarer | bestått / ikke bestått | rå output |
| Produksjons-commit | bestått / ikke bestått | hash |
| Deploy-logg | bestått / ikke bestått | deploy-ID |
| Lokale tester | støtte | antall grønne |

Regler for rapporten:
- Ikke skriv «verifisert» uten output som viser det
- Ikke godta en beskrivelse der et bevis kreves
- Hvis noe ikke kan sjekkes, si hva som blokkerer — ikke hopp over det
- Fravær av en påstand er ofte det viktigste funnet

---

## Blind testing

Verifikasjonsoppdraget gis **kun som mål** — ikke med forklaringen fra den som
bygget.

- Ikke: «Anti sier han har implementert hreflang, sjekk at det stemmer»
- Men: «Verifiser at `/th` svarer på thai2drive.no med server-rendret thai-HTML
  og hreflang»

En informert verifikatør leter etter bekreftelse. En blind verifikatør kan ikke
styres mot et bestemt svar.

---

## Kjente fallgruver i dette prosjektet

**Indekseringsetterslep.** `GITHUB_SEARCH_CODE` indekserer ikke alltid ferske
commits umiddelbart. Null treff er ikke bevis på fravær — si det eksplisitt i
rapporten før du konkluderer.

**Mange parallelle spor.** Prosjektet har flere titalls brancher og flere agenter
som jobber samtidig. Funksjonalitet kan ligge ferdig under et branchnavn du ikke
letet etter. List brancher før du konkluderer med at noe mangler.

**Nettlesercache og service worker.** En service worker kan servere gammel side fra
nettleserens cache uavhengig av serveren, også etter en vellykket deploy. Sjekk alltid
med cache-bryter (`-H "Cache-Control: no-cache"` og `?t=$(date +%s)`), og bruk en ny
nettleserprofil for rendret DOM. Hashen fra `/api/web/version` er fasiten for hva
serveren kjører, ikke hva en gammel fane viser.

**Push til main er ikke deploy.** En commit på `origin/main` betyr at koden er
versjonert, ikke at den kjører. Kun produksjonsdomenet avgjør.

---

## Låsing av oppgave

En oppgave lukkes kun når verifikasjonen er **bestått**. Ikke «ferdig med
forbehold», ikke «ferdig, men deploy gjenstår». Produksjonsbevis er siste steg
før lukking.
