# SOLUTION BLUEPRINT: Webapp som eneste lanseringsvei

## Mål

Gjør webappen til den eneste tydelige konverteringsveien på landingssiden inntil mobilappen faktisk lanseres.

## Ikke-mål

- Ingen endring av webappen, API-ruter eller autentisering.
- Ingen endring av Stripe, RevenueCat, priser, premiumlogikk eller tilgangsgrenser.
- Ingen deploy eller produksjonskonfigurasjon.

## Berørt fil og komponenter

- `backend/landing.py`
  - hero-CTA og QR-blokk
  - bunn-CTA og QR-blokk
  - demoens sluttvisning

## Dataflyt og API-kontrakt

Alle nye CTA-er bruker den eksisterende GET-ruten `/api/web`. Ingen kontrakter endres.

## Språk, tilgang og premium

Norsk, thai og engelsk oppdateres parallelt. Guest/free/premium og viste priser berøres ikke.

## Patchplan

1. Fjern heroens mobilappknapp og appnedlastings-QR.
2. Erstatt bunnens mobilappknapp med en lenke til webappen og fjern QR-blokken.
3. Endre demoens slutttekst og CTA fra appnedlasting til å fortsette i webappen.
4. Fjern konstanten for QR-bildet dersom den blir ubrukt.

## Verifisering

- Python-syntakssjekk av `backend/landing.py`.
- Render HTML lokalt og bekreft at mobilapp-/nedlastingstekst og `#download` er borte.
- Bekreft at `/api/web` finnes i hero, bunn-CTA og demoens sluttvisning.
- Kontroller diff for utilsiktede backend-, betalings- eller tilgangsendringer.
- Fersk produksjonskontroll kan først utføres etter en separat, uttrykkelig godkjent deploy.

## Rollback og risiko

Rollback er å reversere den ene frontend-innholdspatchen. Risikoen er lav og begrenset til landingssidens navigasjon og tekst.

Ingen ytterligere avgjørelser kreves: Michael har uttrykkelig bestemt at bare webappen skal lanseres nå.

READY FOR AGENT 3
