# De første 50 — plan for tilbakemelding

Status: forslag. Ingen elev er kontaktet, og ingen produksjonsdata er lest.

## Ett spørsmål til eleven

Etter at en pilotdeltaker har begynt å øve, vis ett frivillig spørsmål ved første passende retur til Michael: «Møtte du norsk tekst du ikke forstod mens du øvde? Hvis ja, hvilket ord eller hvor?» Dette er meningsinnhold; Deep må godkjenne endelig thai tekst. Svar: `ja`, `nei`, `har_ikke_øvd`, eller hopp over. Ved `ja` kan eleven gi en valgfri detalj. Spør høyst én gang per bruker. Ikke spør ved første appåpning før øving.

Den eksisterende velkomsten kommer fra `GET /api/teacher/welcome` (`backend/teacher_chat.py:3776-3794`) og vises fra `backend/webapp.py:12332-12350`. Den flyten lagrer ikke et strukturert svar på dette spørsmålet.

## Hvem som teller som pilotdeltaker

Lag først en entydig liste over kontoer med reell pilotstart og bruker-ID. Vanlig registrering bruker `users.campaign_index` og `trial_started_at` (`backend/server.py:2903-2958`). Den separate kampanjeruten er stengt i A1; `campaign_users` beholdes som historiske data (se [sikring og tilbakeføring](CAMPAIGN-CONTAINMENT.md)); en rad der er ikke alene bevis for en aktiv elev. Rapporter derfor antall inviterte, registrerte og aktiverte hver for seg, og hold administratorer utenfor.

## Hva som kan måles nå

| Spørsmål | Tilgjengelig måling | Begrensning |
| --- | --- | --- |
| Fullfører de quizen? | Antall piloter med minst én fullført økt og antall fullførte økter fra `quiz_attempts` (`backend/server.py:2660-2699`). | Økter lagres først ved fullføring; «ingen fullført økt» er ikke et dokumentert avbrudd. |
| Hvor faller de av? | Ingen nøyaktig avbruddsposisjon kan måles nå. | Starttid er klienttilstand, og `access_events` dekker ikke alle prøve- og Premium-veier (`backend/webapp.py:8779`, `backend/server.py:2556-2588`). |
| Hvilke kategorier har lavest score? | Regn fra fullførte kategoriøkter med antall riktige, totalt antall og antall elever (`backend/server.py:283-306,2660-2699`). | Ikke bruk fiktive baseline-tall i `admin_analytics.py:75-125` som elevfunn. Vis nevner og utvalgsstørrelse. |
| Bruker de Michael-chatten? | Aggregerte chattall kan leses (`backend/teacher_chat.py:4313-4349`). | Chatloggene har ikke pålitelig bruker-/enhetskobling til de 50; rapporter kohortbruk som «ikke målbart» inntil dette finnes. |

## Hvor svarene bør lagres ved senere bygging

Bruk en egen, begrenset `pilot_feedback`-samling med pilotens bruker-ID, spørsmålsversjon, svarverdi, valgfri detalj, språk, tidspunkt og status `vist/svart/hoppet_over`. Unngå navn og e-post i analyseuttrekk. `support_chats` er for support og eskalering (`backend/support_chat.py:329-437`); `teacher_feedback` vurderer AI-svar (`backend/teacher_chat.py:4386-4411`). Ingen av dem er egnet som fasit for pilotspørsmålet.

## Gjennomgang etter sju dager

Mål dag 0–7 fra hver elevs `trial_started_at`. Gjør første gjennomgang når den første aktive deltakeren har hatt sju dager, og en samlet gjennomgang når alle inkluderte har hatt det. Rapportér teller og nevner for invitasjon, registrering, aktivering, øving og fullførte quizer; kategoriresultat med antall svar; antall `ja/nei/har_ikke_øvd/hoppet_over`; og anonymiserte eksempler på konkrete språkproblemer. Marker avbruddsposisjon og Michael-bruk per pilot som ukjent inntil egen måling finnes. Prioriter ett konkret problem og én liten patch om gangen, og mål igjen.
