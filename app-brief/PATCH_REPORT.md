# PATCH REPORT: Webapp-only landingside

## Endrede filer

- `backend/landing.py`
  - fjernet mobilappknapp og QR-nedlasting fra hero
  - erstattet mobilappknapp i bunn-CTA med `/api/web`
  - fjernet bunnens QR-nedlasting
  - endret demoens sluttvisning til webapp på thai, norsk og engelsk
  - fjernet ubrukt `QR_URL`

## Tester og resultater

- `python -m py_compile backend/landing.py`: PASS med Codex-runtime Python.
- Komponent-render av `_hero_html()`, `_bottom_cta_html()` og `LANDING_JS`: PASS.
- Assertions: ingen `#download`, `Last ned app`, `Download app` eller thai appnedlastingstekst; minst tre `/api/web`-referanser i berørte komponenter: PASS.
- `git diff --check`: PASS; kun varsel om lokal LF/CRLF-normalisering.
- Full `build_landing_page()` kunne ikke importeres med den isolerte runtime-en fordi `python-dotenv` mangler der. Dette er et lokalt testmiljøproblem; modulens syntaks og berørte komponenter er testet separat.

## Gjenværende risiko

- Endringen er ikke deployet, så produksjon viser fortsatt gammel versjon til en separat deploy gjennomføres.
- Visuell kontroll av den patched siden må gjøres etter lokal oppstart med prosjektavhengigheter eller etter godkjent deploy.

## Rollback

Reverser endringene i `backend/landing.py`. Ingen data, API-er eller eksterne systemer er endret.

Klar for Agent 4 / QA Gate.
