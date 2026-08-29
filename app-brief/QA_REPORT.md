# QA REPORT: 1000+ spørsmål

## Scope og rotårsak

PASS. Diffen adresserer de statiske, utdaterte markedsføringstallene i de to offentlige nettsidebyggerne. Ingen andre applikasjonsfiler er endret.

## Språk

PASS. Landingssiden viser 1000+ konsistent på thai, norsk og engelsk. Den eldre norske nettsideruten og metadata er også oppdatert.

## Automatiske kontroller

- Python-syntaks: PASS.
- Render-/kildeassertions: PASS.
- Gamle produktantall 500+/700+: borte.
- Diff-format og hemmelighetsscope: PASS.

## Tilgang, betaling og regresjon

PASS. Ingen endringer i quizdata, guest/free/premium, autentisering, priser, Stripe eller RevenueCat. Tekniske 500/700-verdier som CSS, timeout og feltlengde er beholdt.

## Produksjon

Ikke verifisert før deploy. Krever fersk live-kontroll etter Railway er grønn.

PASS – klar for publisering og live-verifisering.
