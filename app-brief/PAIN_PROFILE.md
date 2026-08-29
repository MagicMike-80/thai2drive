# PAIN PROFILE: Utdatert antall spørsmål på nettsiden

## Brukersmerte

Thai2Drive har over 1000 spørsmål, men offentlige nettsideflater viser 500+ og 700+. Besøkende får derfor et utdatert og motstridende bilde av innholdet.

## Verifiserte observasjoner og rotårsak

- `backend/landing.py` inneholder synlige 500+- og 700+-tekster i hero, statistikk, premiuminnhold, demoavslutning og metadata.
- `backend/website.py` inneholder 500+-tekster i den eldre nettsideruten og metadata.
- Rotårsaken er statiske markedsføringstekster som ikke ble oppdatert da spørsmålsbanken passerte 1000.

## Akseptansekriterier

1. Alle markedsføringsreferanser til 500+/700+ på de offentlige nettsideflatene viser 1000+.
2. Thai, norsk og engelsk er konsistente.
3. Tall som gjelder CSS, tidsavbrudd, feltgrenser eller andre tekniske verdier forblir uendret.
4. Ingen quiz-, tilgangs-, premium- eller betalingslogikk endres.

Rotårsaken er bevist. Klar for Solution Architect.
