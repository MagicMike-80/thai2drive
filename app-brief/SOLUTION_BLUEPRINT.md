# SOLUTION BLUEPRINT: Standardiser nettsiden til 1000+

## Mål

Oppdater bare offentlige markedsføringstekster fra 500+/700+ til 1000+ i alle tre språk.

## Ikke-mål

Ingen endring av spørsmålsdata, API-er, tilgang, premium, priser, Stripe, RevenueCat eller deploykonfigurasjon.

## Filer og patchplan

1. Oppdater relevante tekster og metadata i `backend/landing.py`.
2. Oppdater tilsvarende tekster og metadata i `backend/website.py`.
3. Søk etter gjenværende markedsføringsreferanser til 500/700 og test Python-syntaks.
4. Verifiser NO/TH/EN og fersk produksjon etter deploy.

## Risiko og rollback

Lav risiko: ren tekstendring i to offentlige nettsidebyggere. Rollback er å reversere committen.

Michael har oppgitt 1000+ som korrekt produktantall.

READY FOR AGENT 3
