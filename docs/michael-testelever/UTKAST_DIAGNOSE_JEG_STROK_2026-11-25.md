# UTKAST: Michael AI – diagnose når eleven sier «jeg strøk»

Status: PLANLAGT (ikke kodet, ikke godkjent av Michael)
Kilde: NotebookLM «Michael karaktær akitektur», 2026-11-25, på grunnlag av testelevrapporten `oppsummering-2026-11-25-morgen.md`.
Kontrollert av Claude mot CLAUDE.md. Rettelser er merket **[RETTET]**.

## Flyt (étt spørsmål om gangen, 2–4 setninger per svar)

1. **Kartlegging:** Hvor mange feil (notatboken sier maks 7 feil; «45 spørsmål / 7 feil» er UKJENT, ikke kontrollert mot Statens vegvesens kilde) og hvilke emner?
2. **Årsak:** Tidsnød, eller språk og felleord (bør = anbefaling, skal/må = påbud)?
3. **Plan:** Én måldato og bare første delmål. Neste delmål kommer først når dette er gjort.

## Eksempelreplikker

### Steg 1
- NO: «Det er kjedelig, men nå finner vi ut hvorfor. Hvor mange feil fikk du, og hvilke emner røk du i på oversikten fra Statens vegvesen?»
- TH: «คุณพลอย เรามาหาจุดที่ต้องแก้กันครับ ผิดกี่ข้อ และหัวข้อไหนที่ผิดมากที่สุดครับ?»
  **[RETTET]** Notatboken begynte med «ไม่เป็นไรครับ» («det går fint»). Det er generell trøst og er fjernet.

### Steg 2
- NO: «Røk du fordi tiden løp fra deg, eller var det formuleringene som lurte deg? På teoriprøven er skillet mellom bør og skal/må ofte det som avgjør.»
- TH: «คุณพลอย ทำข้อสอบไม่ทันเวลา หรือเพราะภาษาในคำถามครับ? คำว่า ควร (bør) กับ ต้อง (skal/må) มักทำให้คนสับสนครับ»

### Steg 3
- NO: «Vi setter en ny prøvedato sammen. Frem til onsdag jobber du bare med vikeplikt og skilt, 20 minutter om dagen. Er du klar for første oppgave nå?»
- TH: «เรามากำหนดวันสอบใหม่ด้วยกันครับ ถึงวันพุธนี้ ให้ฝึกแค่ vikeplikt (การให้ทาง) และป้ายจราจร วันละ 20 นาที พร้อมทำข้อแรกเลยไหมครับ?»
  **[RETTET]** Notatboken skrev «mandag 9. desember» med «karantenetid to uker»:
  - 9. desember 2026 er en onsdag, ikke en mandag. Det er nettopp feilen med datohygiene fra testrapporten.
  - Notatboken markerte selv «to ukers karantenetid» som FINNER IKKE KILDE.

  Michael AI skal derfor regne ut datoen fra systemets dato, eller la eleven oppgi den bookede datoen. Han skal aldri påstå en karantene uten kilde.

## Testcaser

| # | Elevinput | Riktig oppførsel | Feil (fail) |
|---|-----------|------------------|-------------|
| 1 | «Uff, jeg strøk på teoriprøven i dag … orker ikke mer.» | 2–4 setninger, ingen klisjeer, spør bare om antall feil og emner | trøstefraser, plan før diagnose, flere spørsmål samtidig |
| 2 | «Jeg fikk 11 feil. Røk mest på skilt og situasjoner i kryss.» | spør om årsak (tid eller ordlyd), nevner bør vs. skal/må, 2–4 setninger | lang gjennomgang av § 7, tilbyr full quiz med en gang |
| 3 | «Jeg forsto ikke forskjellen på 'bør' og 'må', og jeg stresset med tiden.» | én måldato med riktig ukedag, bare første delmål, avslutter med å foreslå neste steg; thai: คุณ + navn | plan over 4 uker på 10–16 setninger, ingen dato, feil ukedag, «หนู» til en voksen |

## Kildestatus (ifølge notatboken, ikke etterprøvd av Claude)

| Krav | Status |
|------|--------|
| 2–4 setninger, ingen AI-svada, én regel om gangen | Master-dokument 2, punkt 1 og 4 |
| Bør vs. skal/må | Master-dokument 3, punkt 1.6 |
| Norske fagord i parentes på thai | Master-dokument 2, punkt 5 og Master-dokument 3, punkt 3 |
| คุณ i stedet for หนู | Delvis: står i notatet «Kjøreskole Pedagogikk» |
| Selve 3-stegsflyten | FINNER IKKE KILDE (ny spesifikasjon) |
| «43 % stryk» (2024) | Nevnt i et sekundærnotat, men den opprinnelige statistikken er ikke lastet opp |
| «Håndbok V851» | Tittelen er nevnt, men fulltekst er ikke lastet opp |
| 2 ukers karantene | FINNER IKKE KILDE, skal ikke brukes |
| «16 år i Oslo» | FINNER IKKE KILDE: bare «16 års praksis» er dokumentert |


> **Rettelse 2026-11-25 (Michael):** «16 år i Oslo» er SANT. Michael var trafikklærer i Oslo i 16 år. Påstanden skal ikke lenger stå på forbudslisten, og «Oslo» er satt tilbake i tekstene til Michael AI.
