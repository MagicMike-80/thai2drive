# Test: diagnose ved «jeg strøk» – lokalt mot ekte modell

Status: TESTET lokalt (Windows, Python 3.12). Ekte LLM-kall er gjort med nøkkel fra backend/.env, og databasen var erstattet med en falsk database i minnet. Det er ikke gjort noen kall mot produksjons-DB eller thai2drive.no, og pytest er ikke kjørt.
Kode: ucommittet arbeidskopi av backend/teacher_chat.py (endring fra PowerShell-økten pluss tekstrettingen av «16 år i Oslo»).
Skript: scratchpad diag_harness/run_diag.py, i Claude-økten 2026-11-25.
Begrensning: kontekst fra pensum, media og DB var tom, så svarene kan bli annerledes i produksjon.

| # | Språk | Elev | Svar (forkortet) | Vurdering |
|---|-------|------|------------------|-----------|
| 1 | NO | «Uff, jeg strøk på teoriprøven i dag … orker ikke mer.» | «Det er kjipt, men vi tar det rolig og finner ut hva som gikk galt. Hvor mange feil hadde du, og hvilke temaer …?» | OK: 2 setninger, bare steg 1 |
| 2 | NO | «Jeg fikk 11 feil …» | spør om tidspress eller formuleringer, forklarer bør/skal/må | OK: 3 setninger |
| 3 | NO | «… bør og må … stresset med tiden» | mål: ny prøve innen 2026-12-09; første delmål er bør/skal/må; neste steg er fem skiltspørsmål | OK: ingen karantene; datoen står som ISO-dato |
| 4a | TH | «ฉันสอบทฤษฎีไม่ผ่านค่ะ» | «… คุณพลอย … ผิดกี่ข้อ และผิดเรื่องอะไรบ้างครับ» | OK: คุณ + navn, ingen หนู |
| 4b | TH | «ผิด 10 ข้อค่ะ …» | spør om tid eller ordlyd (ควร/ต้อง) | Delvis: mangler «(bør)», «(må)» og «(vikeplikt)» i parentes |
| 4c | TH | «… bør กับ må … ไม่ทันเวลา» | mål: torsdag 3. desember 2569 (= 2026); første delmål er ควร/ต้อง | Ukedagen er riktig (torsdag). Delvis: mangler norske fagord i parentes |
| 5 | NO | «jeg strøk» → «hva betyr skilt 202?» | gir direkte svar om vikeplikt (skilt 202) | OK: diagnosen slipper taket |

Funn: på thai bruker diagnosesvarene ikke norske fagord i parentes (bør, må, vikeplikt). Det bryter CLAUDE.md § 4 og Master-dokument 3.

## Runde 2 (samme dag, etter rettelsene for nivå og tone)

Oppsett som i runde 1. Thai er testet på nivå 1 (ren thai, standard) og på nivå 2 (med norske fagord).

- **Norsk: menneskelig og kort.** Eksempler: «Det er kjipt, Kai. Vi tar det rolig nå.» og «Skilt og kryss, det er der det smeller oftest.» Steg 3 spør eleven om dato i stedet for å finne på en. Direkte spørsmål midt i diagnosen gir fortsatt direkte svar.
- **Thai nivå 1:** ingen norske ord, som er riktig for nivået. Dato: torsdag 3. desember, riktig ukedag. Restfeil:
  - åpner med «ไม่เป็นไรครับ», som er generell trøst
  - steg 2 sier «ต่อไปขอถามตรงๆ» og kunngjør dermed neste steg
  - gjentar elevens tall
- **Thai nivå 2:** fagordene «ควร (bør)», «ต้อง (skal/må)» og «การให้ทาง (vikeplikt)» kommer, og fredag 27. november har riktig ukedag. Restfeil:
  - «เรื่องแบบนี้เกิดขึ้นได้ครับ», som er trøst
  - «ต่อไปขอรู้สาเหตุ:», som kunngjør neste steg
  - ordlistelinjen «คำศัพท์นอร์เวย์: ให้ทาง (vikeplikt)» legges til av den eldre funksjonen `_ensure_level2_norwegian_term` (commit 6917314, 2026-11-05), ikke av diagnosen
- **Vurdering:** Norsk er nær Michaels stil. Thai følger reglene for innhold, men modellen bryter fortsatt tonereglene. Flere regler hjelper lite. Eksempelreplikker på thai skrevet av Michael selv vil trolig hjelpe mest.

## Runde 3: Michaels egne thai-replikker som eksempler (Oslo satt tilbake)

- **Norsk:**
  - «Det er kjipt, Kai, men det er ikke slutten på noe. Michael var frisør før han ble kjørelærer, og han ga seg aldri …» Historien fortelles i tredje person.
  - «Nesten bra, Kai – du er nærmere enn du tror.» Deretter et åpent spørsmål om hva som var vanskeligst.
  - Steg 3: bør/må kort, øvefilosofien, og én øvelse («strek under bør/må/skal»), avsluttet med «Klarer du å ta tre oppgaver sånn i kveld?». Steget har 5 setninger, så det er litt over grensen.
  - Skilt 202 midt i diagnosen gir fortsatt et direkte svar.
- **Thai nivå 1:** «ไม่เป็นไรครับ พลอย…», «เกือบดีแล้วครับพลอย แค่สิบข้อเอง เดี๋ยวครั้งหน้าก็ผ่าน», «…ไม่มีอะไรยากหรือง่ายครับ เราฝึกจนทำได้…» og én øvelse med fem oppgaver og tidtaking. Ingen norske ord og ingen ordlistelinje.
- **Thai nivå 2:** fagord i parentes (skilt, vikeplikt, kryss, bør, skal/må) og samme stemme.
- **Restfunn:** Tiltalen blandes. Han sier «พลอย» (bare navnet) og «พี่» i samme svar. Michael må avgjøre om det skal være «พี่พลอย», bare «พี่» eller «คุณพลอย».

## Runde 4: thai tiltaler eleven bare med «พี่», uten navn (Michaels avgjørelse)

- **Nivå 1:**
  - «ไม่เป็นไรครับพี่ มาดูกันว่าผิดตรงไหนครับ พี่ผิดกี่ข้อ…»
  - «เกือบดีแล้วครับพี่ แค่สิบข้อเอง เดี๋ยวครั้งหน้าก็ผ่านครับ แล้วพี่คิดว่าอะไรคือส่วนที่ยากที่สุดสำหรับพี่ครับ»
  - Steg 3: ควร/ต้อง og én øvelse med tidtaking.
  - Tiltalen er konsekvent, og navnet brukes ikke.
- **Nivå 2:** samme stemme, med ควร (bør) og ต้อง (skal/må).
- **Restfunn:**
  1. «ควร … ทำหรือไม่ทำก็ได้» («spiller ingen rolle om du gjør det») er for slapt. «Bør» er en sterk anbefaling, ikke valgfritt.
  2. Nivå 2 viser til «สำนักงานขนส่ง», en thailandsk etat, selv om instruksen forbyr det.
  3. Den eldre ordlistelinjen «คำศัพท์นอร์เวย์: ให้ทาง (vikeplikt)» kommer fortsatt på nivå 2, fra `_ensure_level2_norwegian_term`.

## Runde 5: bør som sterk anbefaling, ingen thailandske etater, ingen ordlistelinje under diagnosen

- **Norsk:** «11 feil er nesten bra – du er nærmere enn du tror …». «Bør» forklares som «en sterk anbefaling – det trygge og riktige valget, men ikke et lovkrav». Øvefilosofien og én øvelse er med. Skilt 202 gir fortsatt et direkte svar.
- **Thai nivå 1:** «ไม่เป็นไรหรอกครับพี่ ผิดแค่สิบข้อเอง ใกล้แล้วครับ เดี๋ยวครั้งหน้าก็ผ่านเองนะ …», og «ควร … คำแนะนำที่ควรทำ เป็นทางที่ปลอดภัยและถูกต้อง แต่ไม่ใช่ข้อบังคับตามกฎหมาย». Ingen etat nevnes.
- **Thai nivå 2:** ควร (bør) forklares som «คำแนะนำที่แรงมาก», og ต้อง (skal/må) som et lovkrav. Ingen ordlistelinje.
- **Resultat:** Ingen restfeil funnet i denne runden. Status: TESTET lokalt (falsk DB i minnet, ekte LLM). Ikke testet i produksjon.
