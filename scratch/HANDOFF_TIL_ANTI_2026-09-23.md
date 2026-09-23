# Overlevering til Anti, 23.09.2026

## Status
- `origin/main` = `2160674`. Alt Michael-arbeidet fra i dag ligger der.
- Live på thai2drive.no (`/api/web/version`) viste sist `267d35e7` (skiltkatalog-fiksen). `2160674` var ikke live ennå.
  Deployene har tatt 20–60 minutter i dag, og de kommer i rekkefølge. Sjekk at Railway bygger `2160674`.
- Hvis `/api/web/version` ikke viser `2160674` etter ca. 30 minutter: se byggloggen i Railway.

## Hva som går live med 2160674 (i tillegg til det som allerede er live)
- Varierte hilsener (`backend/michael_greetings.py`): morgen/dag/kveld, tilbake etter over 7 dager, streak, svakt tema. Ingen emojis.
- Fornavn i hilsenen, hentet lesende fra `users`-posten (`full_name` eller `name`). Ingen auth-endring.
- AI-opplysning: første melding til nye elever, statiske velkomsttekster og fast AI-merke i chat-headeren (th/no/en).
- Setninger kuttes ikke lenger (`_concise_teacher_reply`), og vanlige chat-svar er maks 4 hele setninger (7 hvis eleven ber om forklaring).

## Allerede live (a8cd46f og tidligere)
- Tone (streng/varm/tørr), hint-trapp med teller per quiz-spørsmål, samtale-først, 10 meldingers minne med aktivt skilt.
- Vikeplikt-regel: «ikke hindre eller forstyrre», ikke «alltid stoppe».
- Michael-skolen (Thailand mot Norge, Ord for dagen med 40 ord, Blikkrutine), konge/tjener-chip, HAV-lys, hint-knapp.
- Lekket `(podcast: /public_assets/...)`, fet skrift og menyspørsmål fjernes fra vanlige svar.
- Beslutninger fra Michael: bremselengde på is/snø = 3–4 ganger; vognkort «del 1 skal alltid ligge i bilen».

## Røyktest når 2160674 er live
Kjør fra nettleserkonsollen på thai2drive.no (økt-id med prefikset `smoke_`, enhet `smoke-test-claude-0923`):
`POST /api/teacher/chat` med `{"device_id":"smoke-test-claude-0923","session_id":"smoke_x","language":"no","message":"hva er vikeplikt?"}`
Sjekk:
1. «hva er vikeplikt?» (no): 2–4 hele setninger, ikke kuttet.
2. «Jeg gruer meg til oppkjøring» (no): varm tone, maks 4 setninger, ingen `(podcast:` i teksten.
3. «what is give way?» (en): maks 4 setninger, ingen fet skrift, ingen menyspørsmål.
4. «การให้ทางคืออะไร» (th): ikke kuttet med «…», sier «ไม่กีดขวางและไม่รบกวน», ikke «หยุดเสมอ».
5. `GET /api/teacher/welcome?lang=no&device_id=smoke-new-1`: nevner at Michael er en AI-trafikklærer.
6. Åpne chat-fanen: «AI»-merke ved siden av ONLINE.

## Kjent og åpent
- Ord for dagen har 40 av 50 ord (kilden har 34 oppføringer). Utvides senere.
- Videoen «Aktivt blikk» er ikke laget. Venter til røyktesten er 100 % bestått.
- Svarlengden er fortsatt modellstyrt (DeepSeek). Setningstaket er en etterbehandling, ikke en modellendring.
- Første hint-klikk gir hint, andre gir fasit. Selve quiz-flyten med hint er ikke testet mot ekte backend.

## Ting å være obs på i arbeidskopien
- Uncommittede endringer i `backend/tests/test_teacher_chat.py` og `backend/tests/test_teacher_chat_language_isolation.py` er IKKE mine.
  De lemper thai-testene slik at norske fagord i parentes tillates. Avgjør om de skal committes.
- `context/FEATURES.md` er modifisert og skal aldri committes.
- gbrain er oppgradert til 0.53.0.0. En `gbrain serve` fra en annen økt holder PGLite-låsen; denne økten fikk ikke koblet til MCP.
- gstack er oppgradert til 1.88.1.0 (48 redigerte SKILL.md-filer ble flyttet til `~/.gstack/backups/skills/20260923T185534`).
- Røyktestene har lagt samtaler i produksjonsdatabasen under `smoke_`-økter og enheten `smoke-test-claude-0923`. De kan slettes.

## Tester (offline)
`.venv/Scripts/python.exe -m pytest backend/tests/test_michael_greetings.py backend/tests/test_teacher_chat*.py backend/tests/test_michael*.py backend/tests/test_webapp_lang_routes.py tests/test_michael_school_ui_contract.py -q`
Siste kjøring: 250 bestått. De to live-testene `LiveThaiQuizCoachIsolationTests` og `TestWrongQuizAnswerReplyIsThaiOnly` går mot en ekte LLM og kan svinge.
