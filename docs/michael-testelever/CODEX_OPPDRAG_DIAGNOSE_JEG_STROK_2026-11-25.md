# Oppdrag til Codex: Michael AI – diagnose når eleven sier «jeg strøk»

Bestilt av Michael 2026-11-25 («Ja, send til Codex»). Spesifikasjonen ligger i `docs/michael-testelever/UTKAST_DIAGNOSE_JEG_STROK_2026-11-25.md`. Les den først.

## Omfang
- Fil: `backend/teacher_chat.py`. Endre bare prompttekst og strykgaten.
- Rør ikke Stripe, auth, premium, kvote, produksjons-DB, FREE30, mobil (`frontend/`), de 604 spørsmålene eller V6-flagg.
- Ingen merge, deploy eller produksjonspush. Bare web-først og lokal test. Produksjon krever Michaels GODKJENT for dette omfanget.
- Kjør `git diff backend/teacher_chat.py` først. Arbeidskopien har ucommittede endringer fra andre, og de skal ikke overskrives.

## Det som finnes i dag (verifisert av Claude 2026-11-25)
- `_requests_exam_failure_review()` (ca. linje 4314) fanger bare `strøk på teori|prøv`, `failed (my|the) theory|exam|test` og `สอบตก`.
  Den fanger **ikke** «jeg strøk», «jeg strøk i dag», «jeg besto ikke», «ไม่ผ่าน» eller «I failed».
- Gaten brukes i dag bare til skilt-124-gjenkalling (`_recent_sign_recall_context`). Det finnes ingen diagnoseflyt.
- Den levende prompten bygges i `_build_system_prompt()`. `_PROMPT_CORE*` er ikke i bruk, så ikke legg noe der.

## Det som skal bygges
1. **Utvid gjenkjenningen** av stryk på norsk, thai og engelsk, for eksempel «jeg strøk», «besto ikke», «ikke bestått», «ไม่ผ่าน», «สอบไม่ผ่าน», «I failed», «didn't pass». Unngå falske treff som «strøk over» og «strøk katten».
2. **Diagnose-instruks** når gaten slår inn: étt spørsmål om gangen, 2–4 setninger, ingen generell trøst eller AI-svada. Rekkefølge:
   1. Antall feil og hvilke emner.
   2. Tidsnød, eller språk og felleord (bør = anbefaling, skal/må = påbud).
   3. Én måldato og bare første delmål.
   Steg 1 skal komme først, selv om eleven ber om plan. Planen kommer først etter diagnosen.
3. **Dato:** Michael AI skal aldri finne på ukedag eller dato. Bruk dagens dato fra serveren (Europe/Oslo) til å regne ut ukedag, eller spør eleven om den bookede prøvedatoen. Han skal aldri påstå karantenetid; den har ingen kilde.
4. **Thai:** tiltal eleven med คุณ + navn, aldri หนู til voksne. Behold norske fagord i parentes, og bruk ครับ.
5. **Fakta som ikke skal brukes som påstand:** «43 % stryk», «Håndbok V851», «2 ukers karantene», «16 år i Oslo» og «45 spørsmål / 7 feil». Bare «16 års praksis» er dokumentert.

## Testcaser (lokalt, ikke mot produksjon, og ikke pytest mot thai2drive.no)
| # | Elevinput | Bestått når | Ikke bestått når |
|---|-----------|-------------|------------------|
| 1 | «Uff, jeg strøk på teoriprøven i dag … orker ikke mer.» | 2–4 setninger, spør bare om antall feil og emner | det kommer trøstefraser, plan før diagnose eller flere spørsmål |
| 2 | «Jeg fikk 11 feil. Røk mest på skilt og situasjoner i kryss.» | spør om årsak (tid eller ordlyd), 2–4 setninger | han gir lang regelgjennomgang eller tilbyr full quiz |
| 3 | «Jeg forsto ikke forskjellen på 'bør' og 'må', og jeg stresset med tiden.» | én dato med riktig ukedag, bare første delmål | han gir plan over flere uker, oppgir ingen dato eller feil ukedag |
| 4 (TH) | «ฉันสอบทฤษฎีไม่ผ่านค่ะ» fra Ploy, 34 år | คุณ + navn, ingen หนู, bare thai pluss norske fagord | han bruker หนู, blander språk eller gir generell trøst |
| 5 | «jeg strøk over teksten med blyant» | gaten slår ikke inn | diagnosemodus starter |

## Leveranse
Gi commit-hash, endrede linjer og testlogg (miljø, språk og testcase) med statusene IMPLEMENTERT eller TESTET. Claude kontrollerer etterpå fra nyeste commit.


> **Rettelse 2026-11-25 (Michael):** «16 år i Oslo» er SANT. Michael var trafikklærer i Oslo i 16 år. Påstanden skal ikke lenger stå på forbudslisten, og «Oslo» er satt tilbake i tekstene til Michael AI.
