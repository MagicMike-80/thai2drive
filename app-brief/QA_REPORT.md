# QA REPORT: Webapp-only landingside

## Rotårsak og scope

PASS. Diffen fjerner den dokumenterte parallelle mobilapp-veien fra hero, bunn-CTA og demoens sluttvisning. Bare `backend/landing.py` er endret som applikasjonskode.

## Automatiske kontroller

- Python-syntaks: PASS.
- Smal komponent-render og assertions for forbudt nedlastingscopy og `/api/web`: PASS.
- `git diff --check`: PASS, med kun forventet lokalt LF/CRLF-varsel.
- Hemmelighetssøk i diff: PASS.

## Språk

PASS. Thai, norsk og engelsk er oppdatert parallelt i alle berørte tekster. Ingen appnedlastingscopy eller `#download` gjenstår i `backend/landing.py`.

## Tilgang og betaling

PASS. Ingen endringer i guest/free/premium-logikk, autentisering, Stripe eller RevenueCat. Prislinjene som vises i diffen er uendret kontekst.

## Mobil, tilstander og hovedflyt

PASS WITH WARNING. HTML-strukturen blir enklere på små skjermer fordi knapp og QR-blokker fjernes. Hero, bunn-CTA og demoens sluttvisning bruker eksisterende `/api/web`. Visuell nettleserkontroll av den patched versjonen er ikke utført fordi fullt lokalt runtime-miljø mangler `python-dotenv`.

## Produksjon

Ikke verifisert og ikke deployet. Live-siden endres først etter separat commit/push/deploy.

## Resultat

PASS WITH WARNINGS – patchen er liten, scope-riktig og klar for Michaels vurdering. Restpunktet er visuell kontroll og fersk live-verifisering etter godkjent deploy.
