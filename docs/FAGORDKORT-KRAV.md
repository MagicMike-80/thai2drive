# Fagordkort — krav til faglig godkjenning

Status: forslag til Deep. Ingen implementasjon er godkjent.

## Formål og kilde

Eleven skal kunne knytte et thai begrep til fagordet som brukes på norsk. Ordinær teoriprøve for klasse B tilbys ikke på thai; Statens vegvesen oppgir norsk og fem andre språk, og beskriver søknad om tilrettelagt prøve med tolk for andre språk: https://www.vegvesen.no/forerkort/ta-forerkort/teoriprove/gjennomforing-av-teoriproven/

Kilden for ordpar er `backend/docs/3_NORSK_THAI_FELLEORD_OG_KULTUR_2026.md:8-53`. Den har **33** punktvise ordpar, selv om oppdraget oppgir 40. Deep må avklare de sju manglende før omfanget kan kalles 40. Kildens forklaringer og trafikkregler må fagkontrolleres særskilt; dette kravet godkjenner ikke disse tekstene.

## Første avgrensede ordsett

Foreslått første sett på 15 eksakte par fra kilden. Parene og skrivemåten krever godkjenning fra Deep før publisering.

| Thai begrep | Norsk fagord | Kildelinje |
| --- | --- | ---: |
| การให้ทาง | vikeplikt | 9 |
| ทางหลักที่มีสิทธิ์ก่อน | forkjørsvei | 10 |
| สิทธิ์ผ่านก่อน | forkjørsrett | 11 |
| ป้ายให้ทาง | vikepliktskilt | 12 |
| ป้ายหยุด | stoppskilt | 13 |
| ป้ายเตือน | fareskilt | 16 |
| ป้ายห้าม | forbudsskilt | 17 |
| ป้ายบังคับ | påbudsskilt | 18 |
| ระยะหยุดรถ | stoppelengde | 22 |
| ระยะตอบสนอง | reaksjonslengde | 23 |
| ระยะเบรก | bremselengde | 24 |
| ความเร็วสูงสุด | fartsgrense | 26 |
| วงเวียน | rundkjøring | 31 |
| ทางม้าลาย | gangfelt | 35 |
| ไฟจราจร | trafikklys | 38 |

De resterende 18 parene i kilden er kandidater for neste runde, etter måling og faglig godkjenning.

## Plassering og språk

1. Vis et kort først **etter at** eleven har svart på et vanlig quizspørsmål. Høyest fire relevante par per spørsmål. Kortet må ikke røpe fasit før svar.
2. Vis høyest to relevante par i detaljvisningen for et trafikkskilt, knyttet til nøyaktig skiltkode eller godkjent kategori. Et løst søkeordtreff er ikke nok.
3. Ikke vis kort i eksamensmodus i første versjon. Eksamen skal beholde sin eksisterende svarflyt.
4. På `/th/app` vises godkjent thai begrep først og norsk fagord i parentes, for eksempel `การให้ทาง (vikeplikt)`. Det norske fagordet er eksplisitt læringsinnhold, mens rammetekst, knapper og hjelpetekst er thai.
5. På `/no/app` og `/en/app` vises ikke dette thai/norsk-kortet i første versjon. Egen lokalisert utforming må godkjennes før et kort kan vises der. Manglende oversettelse skal aldri falle tilbake til norsk i engelsk UI.

## Datakobling

Hvert godkjent par får en stabil term-ID med separate `th` og `no` felt. Kobling fra quizspørsmål og trafikkskilt skal bruke godkjent term-ID, skiltkode eller eksakt fagkategori. Et kort vises bare når begge termfeltene er godkjent og koblingen er entydig. Ufullstendige eller tvetydige treff skjules.

Eksisterende relevante flater: `backend/webapp.py:8962,9011-9070` har quizkort, `backend/quiz_terms.py:77-132` velger quiztermer, `backend/webapp.py:13586-13650` er skiltets detaljvisning. Disse linjene er kartlegging, ikke en beslutning om implementasjon.

## Akseptkriterier

- Deep har godkjent 15 av 15 ordpar, skrivemåte og faglig forklaring før bygging.
- 0 kort før quizsvar, 0 i eksamensmodus, høyst 4 per vanlig quizspørsmål og høyst 2 per skilt.
- 0 kort på `/no/app` og `/en/app` i første versjon; ingen feil språk i omkringliggende UI.
- 0 kort ved manglende term, tvetydig kobling eller manglende godkjenning.
- Når eleven skifter raskt mellom spørsmål eller skilt, viser kortet aldri ord fra forrige element.
- Manuell språk- og læringskontroll på `/th/app`, `/no/app` og `/en/app` før en senere release.
