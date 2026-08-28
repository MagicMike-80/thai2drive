# PAIN PROFILE: Landing page viser en ikke-lansert mobilapp

## Brukersmerte

Mobilappen skal ikke lanseres ennå. Den offentlige landingssiden må derfor lede alle brukere til webappen og ikke vise nedlasting, QR-kode for app eller Google Play-lignende forventninger.

## Verifiserte observasjoner

- Produksjonssiden `https://www.thai2drive.no/` viser en egen knapp for appnedlasting i hero og bunn-CTA.
- `backend/landing.py` genererer disse knappene og to QR-seksjoner med tekst om nedlasting på mobil.
- Demoens sluttvisning ber brukeren laste ned appen og lenker til `#download`.
- Den eksisterende webapp-ruten er `/api/web`, og landingssiden har allerede fungerende lenker til den.

## Rotårsak

Landingssiden inneholder eldre mobilapp-konverteringstekst parallelt med den nyere webapp-CTA-en. Dermed kommuniserer siden to lanseringsveier selv om bare webappen skal være tilgjengelig.

## Omfang og risiko

Berørt flate er bare innhold og lenker i `backend/landing.py`. Ingen API-kontrakter, betaling, tilgangsnivåer eller backend-logikk behøver å endres. Risikoen er lav, men norsk, thai og engelsk må oppdateres samlet.

## Akseptansekriterier

1. Ingen synlig landingsidetekst ber brukeren laste ned mobilappen.
2. Ingen appnedlastings-QR vises på landingssiden.
3. Hero, bunn-CTA og demoens sluttvisning leder til `/api/web`.
4. Norsk, thai og engelsk beskriver eksplisitt webappen uten blandet UI.
5. Eksisterende quizdemo, premiumplaner og tilgangsregler forblir uendret.

Rotårsaken er bevist i kildekoden og samsvarer med fersk live-observasjon. Klar for Solution Architect.
