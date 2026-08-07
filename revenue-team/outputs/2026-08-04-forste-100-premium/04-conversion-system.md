---
agent: conversion-system-builder
kjøring: 2026-08-04-forste-100-premium
input: business-brief.md, 00-brief.md, 01-market-signals.md, 02-offer.md, 03-angles.md
second-pass-score: 3,6
åpne spørsmål: >
  1) Produktet gir allerede 7 dagers full Premium gratis ved registrering
     (TRIAL_DAYS = 7, backend/server.py:53 + 752-775 + 2072). Ingen av de tre
     foregående agentene nevner det. Det velter flere konklusjoner i 02-offer.md
     og gjør den bestilte CTA-en enda mer feil enn 00-brief.md antok. Se seksjonen
     «CTA-problemet» og «Sprik jeg fant».
  2) Det finnes ingen tekst noe sted for dag 8 — øyeblikket gratisuken tar slutt og
     brukeren faller fra full tilgang til 10 spørsmål per dag. Det er det skarpeste
     frafallspunktet i hele reisen, og det er udokumentert.
  3) Det finnes ingen avmeldingsfunksjon i koden. Søk på «unsubscribe» i hele repoet
     gir null treff i backend. Den eneste e-posten som finnes i dag
     (scripts/retention_worker.py) lenker til https://thai2drive.com/settings — feil
     domene (alt annet er thai2drive.no) og en side jeg ikke finner. Sekvensen min
     kan ikke sendes før dette er ekte.
  4) Er 3-månederspakken et løpende abonnement eller en engangsbetaling? Koden
     avgjør det ut fra prisobjektet i Stripe (`_checkout_mode_for_price`,
     server.py:1548), ikke ut fra noe jeg kan lese. E-post 5 er skrevet slik at den
     ikke påstår noen av delene.
  5) Thai-formuleringene i dette dokumentet er mine, ikke observert kundespråk.
     Tabell B3 hos agent 1 er merket [IKKE INNSAMLET]. Valideringsliste ligger ved.
---

# Konverteringssystem — første 100 Premium-kunder

> **Les denne boksen først.**
>
> Alt under hviler på den samme `[ANTAKELSE]` som agent 3: at **vikeplikt, med
> rundkjøring som verste undertilfelle**, er kategorien elevene sliter mest med.
> Ingen har målt det. Spørringen som avgjør det ligger ferdig i
> `01-market-signals.md`, del A.
>
> Byttes kategorien, byttes ordene i lead magneten og de to spørsmålene i e-post 3
> og 4. Struktur, sekvens, CTA og kjøpsreise står uendret.

---

# DEL 0 — CTA-problemet, løst før noe annet

Michael bestilte ordrett: *«Be seeren kommentere "TEORI" for å få 10 gratis spørsmål
i appen.»*

Den setningen kan ikke brukes. Her er hvorfor, verifisert av meg i koden, ikke
gjengitt fra `00-brief.md`.

## Hva jeg fant, i tre lag

**Lag 1 — belønningen er ikke ny.**
`ACCESS_REGISTERED_DAILY_LIMIT = 10` (`backend/server.py:178`). En registrert,
ikke-betalende bruker får 10 spørsmål **per dag**, hver dag, uten sluttdato
(`_access_policy_payload`, `server.py:799-806`). Gjester får 5 totalt
(`ACCESS_GUEST_TOTAL_LIMIT = 5`, `server.py:177`). Belønningen «10 gratis spørsmål»
er altså enten noe brukeren allerede har, eller — for en gjest — 5 spørsmål mer enn
hen har, som hen uansett ville fått ved å registrere seg gratis.

**Lag 2 — belønningen er dramatisk mindre enn det brukeren faktisk får. Dette er
det ingen har nevnt.**

```
TRIAL_DAYS = 7                                  backend/server.py:53
_grant_trial_if_eligible(...)                   backend/server.py:752-775
  → kalles ved /auth/signup                     backend/server.py:2072
_user_has_active_premium(user)                  backend/server.py:724-730
  → "Full tilgang: admin, betalende kunde ELLER bruker med aktiv gratisuke."
```

**Enhver ny registrering gir 7 dager med hele Premium. Gratis. Uten kort.** Det
inkluderer eksamensmodus, AI-forklaringene på thai, trening på svake temaer,
historikk og videolæring — alle `is_premium`-flaggene i `server.py:824-833` står
true i de sju dagene.

Begrensningen er ærlig og fornuftig: kun én gang per e-post **og** per device_id
(`server.py:758-764`), nettopp for å hindre uendelige gratiskontoer.

Konsekvensen for CTA-en: vi ville bedt folk kommentere for å få **10 spørsmål**, når
det som venter dem på andre siden av registreringen er **hele appen i en uke**. Det
er ikke bare et usant løfte. Det er et usant løfte som selger produktet ned.

**Lag 3 — belønningen måler feil ting.**
`02-offer.md` FORSLAG G1 og `03-angles.md` sier begge det samme: Premium må selges
på *eksamensmodus og forklaringen på thai*, ikke på *antall spørsmål*. En CTA som
teller spørsmål lærer publikum at spørsmålsantall er valutaen. Det er nøyaktig den
oppfatningen vi må vekk fra, og den er dyr å endre etterpå.

## Variant 1 — anbefalt. Ingen kodeendring. Ordet TEORI beholdes.

> **Belønningen er lead magneten.** Den finnes ikke i appen, ikke på nett, og ikke
> på thai noe annet sted jeg har klart å finne (`01-market-signals.md`: ingen
> thai-i-Norge-innhold om norsk teori funnet i søk). Den er ekte ny for alle —
> gjest, registrert og betalende.

**Manus for de siste 2–3 sekundene av versjon A (thai). Ordet TEORI er
latinske bokstaver med vilje — det er et kommentar-signal, ikke språk.**

```
พิมพ์คำว่า TEORI ไว้ในคอมเมนต์
ผมจะส่งไฟล์ 7 คำนอร์เวย์ให้ อ่านจบใน 15 นาที ไม่มีค่าใช้จ่าย
```

**Skjermtekst (thai):**
```
คอมเมนต์: TEORI
```

**Hvorfor dette er sant, punkt for punkt:**

| Påstand i CTA-en | Er den sann? | Hvorfor |
|---|---|---|
| «du får en fil» | Ja | Michael svarer i kommentarfeltet med lenken. Ingen kode. |
| «7 norske ord» | Ja | Ordene er dokumentert i `01-market-signals.md` tabell B1 [K13] |
| «ferdig på 15 minutter» | Ja | 13 sider, ett ord per side. Målt på lesehastighet, se lead magnet-seksjonen |
| «ingen kostnad» | Ja | Ingen betaling, ingen kort, ingen bindende registrering for å få filen |

**Ingenting i denne CTA-en nevner appen.** Det er et bevisst valg. Videoen underviser
i 27 sekunder og gir bort noe i de siste tre. Salget skjer ikke her.

**Norsk versjon B — de siste 3 sekundene (norsk, til den som skal dele videre):**

```
Kjenner du noen som har stirret på det ordet?
Send den til henne.
```

Ingen påstand om produktet i det hele tatt, slik agent 3 spesifiserte.

## Variant 1b — når Michael vil si noe om appen likevel

Skal appen nevnes, er dette den sanne setningen, og den er sterkere enn den
bestilte:

```
สมัครบัญชีฟรีครั้งแรก คุณจะได้ใช้ทุกอย่างในแอปฟรี 7 วัน
รวมถึงโหมดสอบเสมือนจริง และคำอธิบายภาษาไทยเวลาตอบผิด
ไม่ต้องใส่บัตร
```

**Kravene som gjør den sann, og som ikke er valgfrie:**

1. «ครั้งแรก» (første gang) må stå. Gratisuken gis kun én gang per e-post og per
   enhet (`server.py:758-764`). Uten det ordet er setningen usann for alle som har
   registrert seg før.
2. «ไม่ต้องใส่บัตร» (uten kort) er verifisert: *«Ingen kort, ingen Stripe:
   prøveperioden lever kun i vår egen database»* (`server.py:756`).
3. Ingen nedtelling på de sju dagene i markedsføringen. Klokka finnes i produktet
   (`trial_days_left`, `webapp.py:6110-6133`), og det er riktig sted for den. Den
   skal ikke inn i en video.

## Variant 2 — `FORSLAG — krever godkjenning og Antis implementering`

Vil Michael ha en belønning som er *teknisk* ekstra, altså noe ingen får uten
koden, er dette den eneste jeg mener er verdt å vurdere:

**«TEORI» løser ut én full eksamensmodus-runde (45 spørsmål) uten Premium.**

Hva som må endres, nøyaktig:

| # | Endring | Fil / sted |
|---|---|---|
| 1 | Ny samling `promo_redemptions` med samme misbruksvern som gratisuken: én per e-post **og** per `device_id` | mønster finnes ferdig i `server.py:752-775` |
| 2 | Nytt felt på bruker, f.eks. `exam_passes: int` | `users`-dokumentet, `server.py:2075-2087` |
| 3 | Nytt endepunkt `POST /api/redeem` som tar en kode og gir ett pass | ny rute i `api_router` |
| 4 | `exam_mode` må bli `is_premium or exam_passes > 0` | `server.py:826` |
| 5 | **`unlimited_questions` må løftes for hele runden.** Uten dette stopper eksamen på spørsmål 11 for en registrert bruker, fordi dagskvoten er 10 | `server.py:825` + kvotetellingen |
| 6 | Passet må trekkes fra når runden **startes**, ikke når den fullføres, ellers kan den gjenbrukes ved å avbryte | Anti avgjør hvor |
| 7 | Beslutning: skal passet også låse opp AI-forklaringene? Det koster ekte LLM-penger per innløsning | `server.py:827`, `backend/ai_explanations.py` |

**Min anbefaling: ikke gjør dette.** Punkt 5 er en felle som gir en ødelagt
opplevelse hvis den overses, punkt 7 er en åpen regning, og hele belønningen er
**mindre** enn de sju gratisdagene brukeren allerede får ved å registrere seg. Vi
ville brukt utviklingstid på å bygge en dårligere versjon av noe som finnes.

Variant 1 koster null og er sannere. Det er den jeg leverer.

---

# DEL 1 — Lead magnet

## Navn og form

| | |
|---|---|
| **Navn (thai)** | **«7 คำนอร์เวย์ ที่คุณต้องอ่านออกในข้อสอบทฤษฎี»** |
| Undertittel (thai) | «อธิบายเป็นภาษาไทย — อ่านจบใน 15 นาที» |
| Norsk arbeidstittel (kun internt) | «7 norske ord du må kjenne igjen på teoriprøven» |
| Format | PDF, A4, 13 sider. Ett ord per side, stor skrift, mye luft |
| Tillegg | Side 12 er én bildefil for telefonen (låseskjerm/bildegalleri) |
| Språk | **100 % thai.** Eneste unntak: de sju norske ordene, merket 【NO】 |
| Tid til ferdig brukt | 12–15 minutter lesing. Under 20, som krevet |

## Hvilket ett problem den løser — helt

**Problemet:** eleven leser et vikepliktspørsmål på norsk og stopper på et ord.
Ikke på regelen. På ordet. Det er det eneste dokumenterte funnet i hele kjøringen
som kommer fra en uavhengig fagkilde [K13], og det er hele forretningsideen.

**Hva «helt» betyr her:** etter side 11 har leseren lest et **ekte** norsk
teorispørsmål fra Thai2Drives eget innhold, forstått det, svart og fått
begrunnelsen. Ingen del av det er holdt tilbake. Det er ingen «resten koster
penger» noe sted i filen. Er dette det eneste hen noen gang tar fra oss, sitter hen
igjen med sju ord hen kan bruke i en hvilken som helst norsk teoribok, gratis, for
alltid.

## Hvorfor den trekker videre

Den trekker ikke videre fordi den slutter. Den trekker videre fordi den **beviser at
metoden virker på deg**, og så tar den slutt der metoden fortsatt er interessant.

- Side 10–11 er øyeblikket: «jeg leste akkurat et norsk spørsmål og forsto det.»
- Neste steg er ikke en pris. Det er samme opplevelse, flere ganger.
- Broen sier én ting: *filen har sju ord. Appen har spørsmålene der ordene bor, og
  forklarer på thai når du svarer feil.*

Det er ikke et salgsbrev. Det er den bokstavelige fortsettelsen av side 11.

## Full disposisjon — ferdig skrevet

> **Til Michael:** hver thai-formulering under må gjennom valideringslisten nederst
> i dokumentet. Agent 1 merket hele thai-ordlisten `[IKKE INNSAMLET]` — den er
> standard oversettelse, ikke observert kundespråk.
>
> **Merk også:** jeg har med vilje **ikke** skrevet uttale av de norske ordene med
> thai-skrift. Jeg kan ikke validere en slik translitterasjon, og prøven er skriftlig
> — gjenkjenning på papir er det som teller. Vil Michael ha uttale, er det bedre som
> en kort lydfil der han sier de sju ordene selv.

---

### Side 1 — omslag

```
7 คำนอร์เวย์
ที่คุณต้องอ่านออกในข้อสอบทฤษฎี

อธิบายเป็นภาษาไทย

อ่านจบใน 15 นาที
โดย ไมเคิล — ครูสอนขับรถในนอร์เวย์ 16 ปี
```

---

### Side 2 — hvordan filen brukes

```
อ่านยังไงให้ได้ผล

1. อ่านทีละหน้า หน้าละหนึ่งคำ ไม่ต้องรีบ
2. อ่านออกเสียงคำนอร์เวย์นั้นหนึ่งครั้ง แล้วอ่านความหมายภาษาไทย
3. พอถึงหน้าสุดท้าย คุณจะได้ลองอ่านข้อสอบจริงหนึ่งข้อ — ข้อจริง ภาษานอร์เวย์จริง

สิ่งที่ไฟล์นี้ไม่ได้ทำ
ไฟล์นี้ไม่ได้สอนกฎจราจรทั้งหมด และไม่ได้รับประกันว่าคุณจะสอบผ่าน
ไม่มีใครรับประกันเรื่องนั้นได้

สิ่งที่ไฟล์นี้ทำ
ทำให้คุณอ่านคำ 7 คำนี้ออก โดยไม่ต้องหยุดคิด
7 คำนี้คือคำที่ทำให้หลายคนอ่านโจทย์ไม่จบ
```

---

### Side 3 — คำที่ 1

```
คำที่ 1

【NO】  v i k e p l i k t

แปลว่าอะไร
    คุณต้องรอ ให้รถคันอื่นไปก่อน

เจอคำนี้ตอนไหน
    เจอบ่อยมากในข้อสอบ
    และเจอบนป้ายสามเหลี่ยมสีแดง ก่อนถึงสี่แยก

จำแบบนี้
    vikeplikt ไม่ได้แปลว่า "ยาก"
    มันแปลว่า "รอ"
```

---

### Side 4 — คำที่ 2

```
คำที่ 2

【NO】  h ø y r e r e g e l e n

แปลว่าอะไร
    รถที่มาจากทางขวา ไปก่อน

เจอคำนี้ตอนไหน
    ที่สี่แยกที่ไม่มีป้าย ไม่มีไฟจราจร

จำแบบนี้
    høyre = ขวา
    จำคำเดียวนี้ คุณจะอ่านโจทย์ออกอีกหลายข้อ
```

---

### Side 5 — คำที่ 3

```
คำที่ 3

【NO】  f o r k j ø r s k r y s s

แปลว่าอะไร
    สี่แยกที่คุณมีสิทธิ์ไปก่อน

เจอคำนี้ตอนไหน
    มักมาคู่กับป้ายหมายเลข 220

จำแบบนี้
    kryss = สี่แยก
    เห็นคำว่า kryss เมื่อไหร่ แปลว่าโจทย์กำลังพูดถึงสี่แยก
```

---

### Side 6 — คำที่ 4

```
คำที่ 4

【NO】  f l e t t e r e g e l

แปลว่าอะไร
    สลับกันไป คันคุณ คันเขา คันคุณ

เจอคำนี้ตอนไหน
    ตรงที่ถนนสองเลนรวมเป็นเลนเดียว

จำแบบนี้
    เหมือนรูดซิป ฟันซิปสองข้างสลับกันเข้าหากัน
```

---

### Side 7 — คำที่ 5

```
คำที่ 5

【NO】  a k t s o m h e t

แปลว่าอะไร
    มองรอบตัว และพร้อมจะเบรกเสมอ

เจอคำนี้ตอนไหน
    ในข้อที่ถามว่า "ควรทำอย่างไร"
    ไม่ใช่ข้อที่ถามว่า "ใครไปก่อน"

จำแบบนี้
    ไม่ใช่ทักษะการขับรถ เป็นนิสัยการมอง
```

---

### Side 8 — คำที่ 6

```
คำที่ 6

【NO】  b r e m s e b e r e d s k a p

แปลว่าอะไร
    วางเท้าลอยไว้เหนือแป้นเบรก พร้อมเหยียบทันที
    (ยังไม่เหยียบ แค่พร้อม)

เจอคำนี้ตอนไหน
    ใกล้ทางม้าลาย ใกล้โรงเรียน ที่ที่มีเด็ก

จำแบบนี้
    bremse = เบรก
    เห็นคำว่า bremse เมื่อไหร่ แปลว่าโจทย์กำลังพูดถึงการหยุดรถ
```

---

### Side 9 — คำที่ 7

```
คำที่ 7

【NO】  f a r t s t i l p a s s i n g

แปลว่าอะไร
    ขับให้ช้าพอที่จะหยุดได้ทัน ในระยะที่คุณมองเห็น

เจอคำนี้ตอนไหน
    ในข้อที่พูดถึงหมอก ความมืด ถนนลื่น ทางโค้ง

จำแบบนี้
    fart = ความเร็ว
    ไม่ได้แปลว่า "ขับช้า" เสมอไป
    แปลว่า "เร็วเท่าที่ยังหยุดทัน"
```

---

### Side 10 — vikeplikt i rundkjøring

> **Kritisk for sammenhengen:** modellen på denne siden må være **den samme** som i
> videoen. Agent 3 leverte «พระราชา / คนรับใช้» (kongen og tjeneren) med et ferdig
> alternativ «เจ้าของบ้าน / แขก» (verten og gjesten), avhengig av Michaels
> kulturvurdering. **Velger han alternativet, må videoen og denne siden byttes
> sammen.** Er de ulike, mister eleven gjenkjennelsen i det hen åpner filen — og
> gjenkjennelsen er hele grunnen til at filen virker.

**Primærversjon (samme som manus i `03-angles.md`):**

```
วงเวียน — ใครไปก่อน

รถที่อยู่ในวงเวียนแล้ว คือพระราชา
คุณที่กำลังจะเข้า คือคนรับใช้
คนรับใช้รอ พระราชาไปก่อน
พอคุณเข้าไปอยู่ในวงเวียนแล้ว คุณก็เป็นพระราชา

ถ้าไม่แน่ใจว่าใครเป็นพระราชา ให้ถือว่าคุณคือคนรับใช้ แล้วรอ
คุณเป็นคนรับใช้แค่สามวินาที
```

**Alternativ (byttes sammen med videoen):**

```
รถที่อยู่ในวงเวียนแล้ว คือเจ้าของบ้าน
คุณที่กำลังจะเข้า คือแขก
แขกรอที่ประตูก่อน แล้วค่อยเข้าไป
พอคุณเข้าไปอยู่ข้างในแล้ว คุณก็เป็นเจ้าของบ้าน

ถ้าไม่แน่ใจว่าใครเป็นเจ้าของบ้าน ให้ถือว่าคุณคือแขก แล้วรอ
คุณเป็นแขกแค่สามวินาที
```

---

### Side 11 — ekte spørsmål, ekte norsk

> **Kilde:** spørsmålet er hentet ordrett fra Thai2Drives eget innhold,
> `backend/scripts/seed_vikeplikt_questions.py`, spørsmål 1 (`category: "Vikeplikt"`,
> `difficulty: "easy"`, `correct_answer: "A"`). Ingenting er skrevet om av meg.
> **Michael må bekrefte at spørsmålet faktisk ligger i produksjonsdatabasen** før
> filen sendes ut — jeg har lest seed-scriptet, ikke databasen.

```
ทีนี้ ลองอ่านข้อสอบจริงหนึ่งข้อ

ห้ามแปลทั้งประโยค
ให้มองหาแค่คำที่คุณเพิ่งเรียนไป
```

Spørsmålet gjengis på siden nøyaktig slik det står på prøven, på norsk. Det er
poenget — det skal se ut som det ser ut:

```
【NO】
Du nærmer deg et ukontrollert kryss uten skilt.
Bil A kommer fra din høyre side. Hvem har vikeplikt?

A) Du har vikeplikt for bil A
B) Bil A har vikeplikt for deg
C) Den som kjørte inn i krysset sist
D) Den som kjører raskest
```

```
คำที่คุณรู้แล้วในข้อนี้ มีสามคำ

    kryss        =  สี่แยก
    høyre        =  ขวา
    vikeplikt    =  ต้องรอ

พลิกหน้าถัดไปเมื่อคุณเลือกคำตอบแล้ว
```

---

### Side 12 — svar og begrunnelse

> Forklaringsteksten på thai er **produktets egen** (`explanation_th`, samme
> spørsmål i seed-filen). Vi lover altså ikke noe filen ikke leverer: dette er
> nøyaktig det appen sier.

```
คำตอบคือ  A

คุณต้องให้ทางรถ A

ทำไม
กฎการให้ทางด้านขวา: ที่สี่แยกที่ไม่มีป้าย
คุณต้องให้ทางรถที่มาจากทางขวาของคุณเสมอ
รถ A อยู่ทางขวา ดังนั้นคุณต้องรอให้ A ผ่านไปก่อน

สังเกตอะไรไหมครับ
คุณไม่ได้แปลทั้งประโยค คุณแค่รู้จักคำสามคำ
แล้วคุณก็ตอบได้
นั่นแหละคือสิ่งที่ไฟล์นี้ต้องการให้เกิดขึ้น
```

---

### Side 13 — bildekortet for telefonen

Én side, én bildefil, ingen tekst utover dette. Ment å lagres i galleriet.

```
7 คำ — เก็บไว้ในโทรศัพท์

vikeplikt          รอ ให้คันอื่นไปก่อน
høyreregelen       รถจากทางขวาไปก่อน
forkjørskryss      สี่แยกที่คุณไปก่อนได้
fletteregel        สลับกันคันต่อคัน
aktsomhet          มองรอบตัว พร้อมเบรก
bremseberedskap    เท้าลอยเหนือเบรก
fartstilpassing    ช้าพอที่จะหยุดทัน
```

---

### Side 14 — neste steg

Fire linjer. Ingen pris, ingen knapp med utropstegn, ingen påstand om å bestå.

```
ต่อจากนี้

7 คำนี้อยู่ในโจทย์หลายข้อ และยังมีคำอื่นอีก
ในแอป Thai2Drive คุณฝึกทำโจทย์แบบข้อเมื่อกี้ได้
และเวลาคุณตอบผิด จะมีคำอธิบายเป็นภาษาไทยว่าทำไมถึงผิด

ฟรีทุกวัน วันละ 10 ข้อ
{{LENKE_APP}}

ข้อสอบจริงเป็นภาษานอร์เวย์ ไม่มีเวอร์ชันภาษาไทย
เราจึงสอนเนื้อหาเป็นภาษาไทย และให้คุณจำคำนอร์เวย์ให้ได้
```

**Til Michael:** hvis du vil oppgi hvor mange spørsmål appen har, må tallet hentes
fra produksjon først. Jeg har ikke skrevet et tall, fordi jeg ikke kan telle
databasen herfra.

---

# DEL 2 — E-postsekvensen

> ## SPRÅK: 100 % THAI
>
> Hele denne sekvensen er thai. Ingen norske setninger, ingen norsk undertekst,
> ingen «no/th» side om side i samme e-post. De norske fagordene forekommer, merket
> 【NO】, fordi de er selve produktet.
>
> Skal det finnes en norsk sekvens, er det en **egen sekvens med eget publikum**
> (den som prøver å hjelpe noen, jf. versjon B i `03-angles.md`) — ikke en
> oversettelse av denne. Den er ikke bestilt her, og jeg har ikke skrevet den.
>
> **Dette bryter med den eneste e-posten som finnes i produktet i dag.**
> `backend/scripts/retention_worker.py` sender norsk og thai i samme e-post, i samme
> emnefelt (`SUBJECT = "Hei! Michael savner deg 🚗 | ไมเคิลคิดถึงคุณ"`, linje 49).
> Det er i strid med språkregelen i `CLAUDE.md`. Se «Sprik jeg fant».

**Plassholdere jeg ikke fyller ut, fordi jeg ikke setter opp noe:**
`{{LENKE_PDF}}` · `{{LENKE_APP}}` · `{{LENKE_PRIS}}` · `{{LENKE_AVMELDING}}` ·
`{{SVARADRESSE}}`

---

## E-post 1 — leveransen. Umiddelbart.

**Jobb:** levere det som ble lovet. Ingenting annet. Ingen historie, ingen app, ingen
pris.

**Emnefelt:**
```
ไฟล์ 7 คำนอร์เวย์ของคุณ อยู่ตรงนี้ครับ
```

**Brødtekst:**
```
สวัสดีครับ

นี่คือไฟล์ที่คุณขอไว้

    7 คำนอร์เวย์ ที่คุณต้องอ่านออกในข้อสอบทฤษฎี
    {{LENKE_PDF}}

13 หน้า อ่านจบประมาณ 15 นาที
หน้าละหนึ่งคำ ไม่ต้องรีบ

หน้าสุดท้ายก่อนจบ มีข้อสอบจริงหนึ่งข้อ เป็นภาษานอร์เวย์
พออ่านถึงตรงนั้น คุณจะอ่านมันออกเอง

แค่นั้นครับ วันนี้ไม่มีอย่างอื่น

ไมเคิล
ครูสอนขับรถ 16 ปี

—
ไม่อยากรับอีเมลชุดนี้ต่อ ยกเลิกได้ที่นี่ ไม่ต้องตอบคำถามใดๆ:
{{LENKE_AVMELDING}}
```

**Én handling:** åpne filen.

---

## E-post 2 — historien. Dag 2.

**Jobb:** hvorfor problemet finnes. Ingen salg.

**Emnefelt:**
```
ทำไมข้อสอบทฤษฎีถึงยากกว่าที่ควรจะเป็น
```

**Brødtekst:**
```
สวัสดีครับ

วันนี้ผมอยากเล่าให้ฟังว่า ทำไมเรื่องนี้ถึงยาก
ไม่ใช่เพื่อขายอะไร แต่เพราะไม่ค่อยมีใครบอกเรื่องนี้กับคนไทยในนอร์เวย์

เรื่องแรก
ข้อสอบทฤษฎีสำหรับรถยนต์ มีให้เลือกหลายภาษา
นอร์เวย์ (สองแบบ) ซามิเหนือ อังกฤษ อาหรับ โซรานี และตุรกี
ไม่มีภาษาไทย

ถ้าอยากสอบเป็นภาษาไทย ต้องยื่นขอสอบแบบมีล่าม
และต้องหาล่ามเอง จ่ายค่าล่ามเอง ทุกครั้งที่สอบ

เรื่องที่สอง
ใบขับขี่ไทย เปลี่ยนเป็นใบขับขี่นอร์เวย์ตรงๆ ไม่ได้
นอร์เวย์มีข้อตกลงแลกเปลี่ยนกับบางประเทศ ไทยไม่อยู่ในรายชื่อนั้น
คนที่ขับรถมายี่สิบปี ก็ต้องเริ่มใหม่ทั้งหมด รวมถึงสอบทฤษฎี

เรื่องที่สาม และเรื่องนี้สำคัญที่สุด
มีงานวิจัยของวิทยาลัยแห่งหนึ่งในนอร์เวย์ ทำไว้ตั้งแต่ปี 2007
เขาให้ครูสอนขับรถไปสอนกลุ่มนักเรียนที่ไม่ได้ใช้ภาษานอร์เวย์เป็นภาษาแม่
แล้วเขาสรุปว่า ปัญหาไม่ได้อยู่ที่กฎจราจร
ปัญหาอยู่ที่ "คำ"

คำที่เขายกตัวอย่าง คือคำเดียวกับที่อยู่ในไฟล์ของคุณ
aktsomhet, bremseberedskap, fartstilpassing, fletteregel, forkjørskryss

คนนอร์เวย์เดาความหมายจากบริบทได้เอง โดยไม่รู้ตัว
คนที่ไม่ได้โตที่นี่ เดาไม่ได้
ไม่ใช่เพราะไม่ฉลาด แต่เพราะไม่เคยได้ยินคำนั้นมาก่อนในชีวิต

ผมสอนขับรถมา 16 ปี ผมเห็นแบบนี้ซ้ำๆ
คนเก่ง คนขยัน คนที่ขับรถเป็นมานาน — มาติดตรงคำ

ฉะนั้น ถ้าคุณเคยรู้สึกว่า "อ่านห้ารอบแล้วยังไม่เข้าใจ"
มันไม่ใช่ที่คุณ มันที่คำ

วันนี้ทำแค่อย่างเดียวพอครับ
เปิดไฟล์ แล้วเลือกคำที่คุณไม่มั่นใจที่สุดหนึ่งคำ อ่านหน้านั้นอีกรอบ
    {{LENKE_PDF}}

ไมเคิล

—
ไม่อยากรับอีเมลชุดนี้ต่อ ยกเลิกได้ที่นี่ ไม่ต้องตอบคำถามใดๆ:
{{LENKE_AVMELDING}}
```

**Én handling:** åpne filen på nytt, ett ord.

**Kildene bak påstandene, som Michael må ha lest før dette sendes:**
språktilbudet på prøven og tilrettelagt prøve [K7][K8][K9]; innbytteavtalene
[K10][K11][K12]; forskningen [K13]. Alle er `[UVERIFISERT]` i den forstand at
agent 1 fikk 403 på samtlige sider og leste dem via søkesammendrag.
**Ingen gebyrbeløp forekommer i denne e-posten, med vilje.**

---

## E-post 3 — beviset. Dag 4.

> ### Dette er den vanskeligste e-posten i sekvensen, og her er hvordan jeg løste den
>
> Jobben er «en konkret elev, en konkret endring». **Vi har ingen elev.** Agent 1
> fant ikke ett eneste ordrett sitat fra målgruppen, og agent 3 nektet å skrive et
> som *høres* ekte ut.
>
> Jeg kunne skrevet «Noi strøk to ganger og består nå». Det ville vært den ene
> løgnen som er umulig å rydde opp i, i et miljø der alle kjenner alle.
>
> **Løsningen: e-posten sier høyt at vi ikke har historien, og gir leseren et bevis
> hen kan etterprøve på seg selv i stedet.** Og den ber om det vi mangler —
> leserens egne ord. E-post 3 er dermed også datainnsamlingen agent 1 ba om.
>
> **Til Michael:** har du en ekte elev som gir deg tillatelse og egne ord, erstatter
> den historien de fem første avsnittene under. Da blir dette den sterkeste e-posten
> i sekvensen i stedet for den ærligste.

**Emnefelt:**
```
ผมไม่มีเรื่องเล่าจากนักเรียนให้คุณอ่าน
```

**Brødtekst:**
```
สวัสดีครับ

ปกติอีเมลแบบนี้ จะเป็นเรื่องเล่าว่า
"คุณเอ สอบตกสองครั้ง แล้วมาเจอเรา แล้วก็ผ่าน"

ผมไม่เขียนแบบนั้น เพราะสองเหตุผล

หนึ่ง — ผมยังไม่ได้ขออนุญาตนักเรียนคนไหนให้เอาเรื่องของเขามาเล่า
สอง — ถ้าผมแต่งขึ้นมา คุณก็ไม่มีทางรู้ และผมก็เสียสิ่งเดียวที่ผมมีอยู่กับคุณ

เอาแบบนี้แทนดีกว่าครับ
ลองข้อสอบจริงอีกหนึ่งข้อ แล้วดูตัวเองว่าเปลี่ยนไปไหม

【NO】
Du kjører inn i en rundkjøring. Hvem har vikeplikt?

A) Trafikk inne i rundkjøringen har vikeplikt for deg som er ny
B) Du som kjører inn har vikeplikt for trafikk som allerede er inne i rundkjøringen
C) Den som kjører raskest har forkjørsrett
D) Høyreregelen gjelder fullt ut i rundkjøringen

คำใบ้: ในข้อนี้มีคำที่คุณรู้แล้วสามคำ
    vikeplikt, høyreregelen, และ rundkjøring (วงเวียน)

...

คำตอบคือ B
คุณที่กำลังเข้าวงเวียนต้องให้ทางรถที่อยู่ในวงเวียนแล้ว

ในวงเวียนของนอร์เวย์ ผู้ที่เข้าวงเวียนต้องให้ทาง
รถที่อยู่ในวงเวียนแล้วมีสิทธิ์ก่อนเสมอ

ข้อ D คือกับดัก
หลายคนจำว่า "รถจากขวาไปก่อน" แล้วเอามาใช้ในวงเวียนด้วย
ในวงเวียน กฎนั้นใช้แบบนั้นไม่ได้

ทีนี้คำถามจริงของผม
เมื่อสัปดาห์ที่แล้ว ถ้าคุณเจอข้อนี้ คุณจะอ่านออกไหม

ถ้าคำตอบคือ "ไม่" — นั่นคือหลักฐาน และหลักฐานนั้นคือตัวคุณเอง
ไม่ใช่เรื่องเล่าของคนอื่น

สิ่งที่ผมอยากขอ
ตอบอีเมลนี้กลับมาหนึ่งประโยคก็พอ:
"ตอนที่ยากที่สุดสำหรับฉันคือตอน ______"

ผมอ่านทุกฉบับด้วยตัวเอง
และถ้าวันหนึ่งผมจะเล่าเรื่องของใครสักคน ผมจะขออนุญาตเขาก่อนเสมอ

ไมเคิล

—
ไม่อยากรับอีเมลชุดนี้ต่อ ยกเลิกได้ที่นี่ ไม่ต้องตอบคำถามใดๆ:
{{LENKE_AVMELDING}}
```

**Én handling:** svar på e-posten med én setning.

**Kilde for spørsmålet:** `backend/scripts/seed_vikeplikt_questions.py`, spørsmål 7
(rundkjøring), `correct_answer: "B"`. Thai-teksten for svaralternativ B og
forklaringen er produktets egen (`answer_b_th`, `explanation_th`).

> **Advarsel som må videreføres:** i den **norske** forklaringen til dette spørsmålet
> står ordet skrevet **«vikeplykt»** (linje 203 i seed-filen). Agent 3 fant den, jeg
> har verifisert den. Den må rettes av Anti før noe av dette publiseres — vi bygger
> hele produktet på at eleven skal kjenne igjen ett bestemt norsk ord, og da kan
> ikke ordet ha to stavemåter i vårt eget innhold.

---

## E-post 4 — innvendingen. Dag 6.

**Jobb:** si høyt det som faktisk holder dem tilbake. Ikke prisen — den kommer i
e-post 5. Den ekte blokkeringen for et thai-produkt er at prøven ikke er på thai.

**Emnefelt:**
```
"ข้อสอบก็เป็นภาษานอร์เวย์อยู่ดี แล้วเรียนภาษาไทยช่วยอะไร"
```

**Brødtekst:**
```
สวัสดีครับ

คำถามในหัวเรื่อง เป็นคำถามที่ตรงที่สุด
และผมคิดว่าคนที่ไม่ได้ถามออกมา ก็คิดอยู่ในใจ

ผมตอบตรงๆ

ข้อสอบเป็นภาษานอร์เวย์ ไม่มีเวอร์ชันภาษาไทย
ผมไม่เคยพูดว่ามี และจะไม่พูดแบบนั้น
ถ้าใครบอกคุณว่าสอบเป็นภาษาไทยได้ ให้ถามเขาต่ออีกคำถามหนึ่ง

ทางเลือกที่มีจริงคือ ยื่นขอสอบแบบมีล่าม
ทำได้จริง แต่คุณต้องหาล่ามเอง จ่ายเอง และต้องเป็นล่ามที่ผ่านการรับรอง
และต้องทำแบบนั้นใหม่ ทุกครั้งที่สอบ
ผมบอกคุณเรื่องนี้ทั้งที่มันไม่ได้ทำให้ผมได้ลูกค้าเพิ่ม
เพราะคุณควรรู้ว่ามีทางเลือกนี้อยู่

ทีนี้ กลับมาที่คำถาม

คุณจะต้องเจอคำนอร์เวย์พวกนั้นแน่นอน ไม่มีทางเลี่ยง
คำถามคือ คุณจะเจอมันครั้งแรกที่ไหน

เจอครั้งแรกในห้องสอบ — คุณต้องเดา
เจอมาแล้วร้อยครั้ง — คุณแค่อ่าน แล้วก็ตอบ

นี่คือสิ่งเดียวที่เราทำ
เราสอนเนื้อหาเป็นภาษาที่คุณคิดเป็น
แล้วให้คุณจำหน้าตาของคำนอร์เวย์ให้ได้

เราไม่ได้แปลข้อสอบให้คุณในห้องสอบ ไม่มีใครทำแบบนั้นได้
และผมรับประกันไม่ได้ว่าคุณจะสอบผ่าน ไม่มีแอปไหนรับประกันได้
ใครที่รับประกัน คนนั้นโกหก

วันนี้ทำแค่นี้พอครับ
เข้าแอป ทำโจทย์เรื่องการให้ทางสักชุด แล้วดูว่าคำไหนยังสะดุด
    {{LENKE_APP}}

ไมเคิล

—
ไม่อยากรับอีเมลชุดนี้ต่อ ยกเลิกได้ที่นี่ ไม่ต้องตอบคำถามใดๆ:
{{LENKE_AVMELDING}}
```

**Én handling:** gjør en runde vikepliktspørsmål i appen.

**Hvorfor ingen tolkepris står her:** agent 1 og 2 fant den ikke; byråene oppgir pris
først etter at tolk er funnet [K9][K25]. Et gjettet tall her ville ødelagt hele
poenget med e-posten.

---

## E-post 5 — tilbudet. Dag 8.

**Jobb:** be om salget, direkte, uten unnskyldninger og uten press.

> **Tre disiplinerte valg i denne e-posten, som Michael skal kjenne til:**
>
> 1. **Ingen gebyrbeløp.** 480 kr er `[UVERIFISERT]` — ingen av de fire agentene har
>    lest tallet hos Statens vegvesen. Regnestykket «to strøkne forsøk koster mer enn
>    livstid» er sterkt, men det kan ikke trykkes før tallet er bekreftet. Ferdig
>    tekstblokk til å lime inn ligger rett under e-posten.
> 2. **Månedsplanen er ikke fremhevet.** `02-offer.md` FORSLAG R3: det finnes ingen
>    synlig vei ut av et abonnement, og jeg fant heller ingen billing-portal i
>    `backend/`. Jeg selger ikke noe jeg ikke kan svare på «hvordan sier jeg opp?»
>    om. Planen nevnes som eksisterende, den anbefales ikke.
> 3. **Gratisuken nevnes som noe man allerede har fått**, ikke som en bonus vi deler
>    ut. De fleste som har fulgt sekvensen i åtte dager har registrert seg, og da er
>    uken i gang eller nettopp over. Å «tilby» den nå ville vært usant.

**Emnefelt:**
```
ราคา และสิ่งที่คุณได้จริง
```

**Brødtekst:**
```
สวัสดีครับ

นี่เป็นอีเมลฉบับสุดท้ายของชุดนี้
วันนี้ผมขายของ ผมบอกตรงๆ ว่ากำลังขาย จะได้ไม่ต้องเดากัน

ก่อนอื่น สิ่งที่ฟรีตลอด ไม่มีวันหมดอายุ
    สมัครบัญชีฟรี ได้วันละ 10 ข้อ ทุกวัน ไม่ต้องใส่บัตร
    ถ้าเท่านี้พอสำหรับคุณ ใช้แบบนี้ต่อไปได้เลย ผมพูดจริง

และถ้าคุณสมัครบัญชีครั้งแรก คุณจะได้ใช้ทุกอย่างฟรี 7 วัน
    เจ็ดวันนั้นให้ครั้งเดียว ไม่ได้ให้ซ้ำ

Premium คืออะไร — สี่อย่างที่บัญชีฟรีให้ไม่ได้

    1. โหมดสอบเสมือนจริง
       45 ข้อรวด เหมือนสอบจริง
       วันละ 10 ข้อ ต่อให้ทำทุกวัน ก็ไม่มีวันตอบคำถามว่า "ฉันพร้อมหรือยัง"
       โหมดนี้ตอบคำถามนั้น

    2. คำอธิบายภาษาไทย ตอนที่คุณตอบผิด
       ไม่ใช่แค่ "ผิด" แต่บอกว่าทำไมถึงผิด เป็นภาษาที่คุณคิดเป็น

    3. ฝึกเฉพาะเรื่องที่คุณพลาดบ่อย
       ไม่ใช่เรื่องที่คุณทำได้อยู่แล้ว

    4. ประวัติและความคืบหน้า
       เห็นกับตาว่ามันดีขึ้นจริง

ราคา
    3 เดือน   249 โครน
    ตลอดชีพ   699 โครน
    (มีแบบรายเดือนด้วย ดูได้ในแอป)

    {{LENKE_PRIS}}

ผมแนะนำยังไง
    ถ้าคุณเพิ่งย้ายมา และมีเวลาจำกัดตามกฎใบขับขี่ต่างประเทศ — 3 เดือน
    ถ้าคุณเคยสอบตกมาแล้ว และรู้ว่ามันใช้เวลา — ตลอดชีพ
    ถ้าคุณยังไม่แน่ใจ — อย่าเพิ่งซื้อ ใช้ฟรีวันละ 10 ข้อไปก่อน

สิ่งที่ผมไม่รับประกัน
    ผมรับประกันไม่ได้ว่าคุณจะสอบผ่าน ผมไม่ได้เป็นคนออกข้อสอบ
    และข้อสอบไม่มีภาษาไทย ผมพูดเรื่องนี้ไปแล้วเมื่อสองวันก่อน และมันยังจริงอยู่

แอปนี้ไม่เหมาะกับใคร
    ถ้าคุณอ่านคำว่า aktsomhet, bremseberedskap, fartstilpassing แล้วเข้าใจทันที
    คุณไม่ต้องใช้เรา มีแหล่งฝึกภาษานอร์เวย์ฟรีที่ดีพออยู่แล้ว

ขอบคุณที่อ่านมาถึงตรงนี้ครับ
ไม่ว่าคุณจะซื้อหรือไม่ ไฟล์ 7 คำนั้นเป็นของคุณ เก็บไว้ได้เลย

ไมเคิล

—
นี่คืออีเมลฉบับสุดท้ายของชุดนี้
ถ้าไม่อยากรับอีเมลอื่นจากเราอีก ยกเลิกได้ที่นี่:
{{LENKE_AVMELDING}}
```

**Én handling:** åpne prissiden.

### Tekstblokk til e-post 5 — settes inn **kun** når Michael har lest gebyret på vegvesen.no

`[UVERIFISERT — IKKE BRUK FØR TALLET ER BEKREFTET]`

```
ลองคิดเป็นตัวเลข
สอบหนึ่งครั้ง มีค่าธรรมเนียม ___ โครน
สอบตกสองครั้ง = ___ โครน
Premium ตลอดชีพ = 699 โครน

สอบตกสองครั้ง แพงกว่าการมีแอปนี้ตลอดไป
```

Agent 2s ærlige forbehold følger med: **ett** strøket forsøk dekker ikke 699 kr. Det
dekker 249 kr. Ikke strekk tallet lenger enn det går.

---

# DEL 3 — Kjøpsreisen

```
  ①  Video (vinkel 1, thai)
        │  agent 3 sitt manus, 30 sek
        ▼
  ②  Kommentar «TEORI»
        │  Michael svarer i kommentarfeltet + lenke i bio
        ▼
  ③  Landingsside — e-postadresse mot PDF
        ▼
  ④  E-post 1 → PDF åpnes
        ▼
  ⑤  Side 11: «jeg leste et norsk spørsmål og forsto det»
        ▼
  ⑥  Registrering i appen (gratis)  ──►  gratisuken starter, 7 dager full Premium
        ▼
  ⑦  E-post 2, 3, 4 løper parallelt med gratisuken
        ▼
  ⑧  DAG 8 — gratisuken tar slutt. Full tilgang → 10 spørsmål per dag
        ▼
  ⑨  Paywall
        ▼
  ⑩  Stripe checkout
        ▼
  ⑪  Betalt
```

## Hvor jeg tror folk faller av — og hvorfor

| Steg | Frafall | Hvorfor jeg tror det | Hva jeg ville gjort |
|---|---|---|---|
| ①→② | **Størst i absolutte tall** | De aller fleste ser og scroller. Slik er det, og det er ikke et problem å løse med bedre tekst — det er et volumproblem | Serie, ikke enkeltvideo (vinkel 3, sju ord = sju videoer) |
| ②→③ | **Størst skjulte frafall** | Plattformenes DM-begrensninger. En kommentar er ikke en kanal — Michael må svare manuelt i tråden, og lenker i kommentarer blir ofte nedprioritert | Lenke i bio **i tillegg**, alltid. Aldri bare DM |
| ③→④ | Middels | E-postadresse er en reell terskel for en gruppe med lav tillit til systemer | Én felt. Ingen navn, ingen telefon, ingen «hvorfor spør dere om dette» |
| ④→⑤ | Lavt | De som ba om filen, åpner den | Filen må være lesbar på telefon. A4-PDF på en liten skjerm er en fiende. Side 13 finnes nettopp derfor |
| ⑤→⑥ | **Kritisk, og undervurdert** | Fra PDF til registrering finnes ingen bro annet enn en lenke. Her mister vi flest av dem vi allerede har betalt oppmerksomhet for | Én lenke, høyt oppe, med det man får sagt i klartekst |
| ⑥→⑧ | Skjult | Brukeren opplever produktet på sitt beste i sju dager og vet ofte ikke at det er en prøveperiode | Se neste avsnitt |
| **⑧** | **Det skarpeste punktet i hele reisen** | Dag 8 går brukeren fra hele appen til 10 spørsmål per dag. Det leses som en innstramming — nøyaktig det `business-brief` punkt 6 sier gruppen reagerer dårligst på. **Det finnes ingen e-post, ingen tekst og ingen forklaring for dette øyeblikket noe sted** | Se «Hullet på dag 8» |
| ⑨→⑩ | Middels | Paywallen selger i dag skiltgalleri og nevner ikke forklaringene på thai (`02-offer.md` T1) | T1 |
| ⑩→⑪ | Lite, men **hardt** | `create_checkout_session` kaster **503** hvis Stripe ikke leverer livepriser (`server.py:1539-1540`). Da får kunden en feil i betalingsøyeblikket, og vi ser det ikke med mindre noen måler det | Alarm på 503 fra det endepunktet |

## Hullet på dag 8

Dette er mitt viktigste enkeltfunn om reisen, og det ligger utenfor bestillingen min.

Sekvensen min slutter på dag 8. Gratisuken slutter på dag 7 eller 8, avhengig av når
brukeren registrerte seg. Det er tilfeldig at de faller sammen, og det er **flaks**,
ikke design — for hvis brukeren registrerer seg på dag 4 i sekvensen, kommer
e-post 5 fire dager før uken er ute, og hen kjøper noe hen allerede har.

Riktig løsning er ikke en bedre e-post 5. Den er at **overgangen ved dag 8 er en egen,
utløst e-post**, ikke en dato i en sekvens. Det krever at e-postverktøyet vet når
`trial_expires_at` inntreffer. **Det er Antis bord, det er ikke bestilt, og jeg har
ikke skrevet den e-posten.** Jeg konstaterer at hullet finnes, og at det er dyrere
enn alle tekstforbedringene i dette dokumentet til sammen.

## Regnestykket bakover fra 100 kunder

`[ANTAKELSE]` — **hver eneste rate under er gjettet.** Vi har ingen konverteringsdata.
Formålet er ikke å forutsi. Det er å vise størrelsesorden, slik at Michael ikke
planlegger for én video.

| Steg | Antatt rate | Trengs |
|---|---|---|
| Betalende kunder | mål | **100** |
| E-postadresser → kunde | 5 % | 2 000 e-poster |
| Kommentar → e-post | 50 % | 4 000 kommentarer |
| Visning → kommentar | 3 % | **ca. 133 000 visninger** |

**Hva dette betyr, sagt rett ut:** 133 000 visninger er ikke én video. Det er en
serie over uker, eller det er én video som treffer uvanlig godt, eller det er en
annen kanal i tillegg — den norsk-thailandske pressen og tolkemiljøet som agent 1
identifiserte [K17][K18][K19].

Er den ekte lead→kunde-raten 10 % i stedet for 5, halveres alt. Er den 2 %, dobles
det. **Derfor er de fire tallene i neste seksjon viktigere enn resten av dokumentet.**

---

# DEL 4 — Hva som må måles

Ikke «engasjement». Fire tellere, og de er nok.

## De fire som avgjør alt

| # | Tallet | Slik regnes det | Hvor det finnes i dag |
|---|---|---|---|
| **1** | **Kommentarer per 1 000 visninger** | kommentarer med ordet TEORI ÷ visninger × 1000 | Plattformens egen statistikk. Michael teller manuelt de første ukene |
| **2** | **E-postadresser per 100 kommentarer** | Måler om steg ②→③ faktisk virker, eller om DM-veggen stopper alt | Krever landingsside med teller. **Finnes ikke** |
| **3** | **Registreringer per 100 e-postadresser** | Den kritiske broen fra PDF til produkt | `User Signed Up` finnes allerede i Segment (`server.py:2101`), men uten kilde-tagg |
| **4** | **Kjøp per 100 paywall-visninger** | Selve konverteringen | `access_events` + Segment finnes i backend |

## Det jeg ville målt i tillegg, i prioritert rekkefølge

5. **Hvor mange registrerte som starter eksamensmodus i løpet av gratisuken.**
   Dette er hele G1-hypotesen fra `02-offer.md` testet med ett tall. Er den lav,
   selger vi Premium på noe folk aldri har prøvd.
6. **Andel som fortsatt er aktive dag 9–12.** Frafallet på dag 8, målt.
7. **Kjøp fordelt på plan** (99 / 249 / 699). Avgjør prisspørsmålet Michael
   opprinnelig stilte, og ingen tekst kan svare på det.
8. **Avmeldinger per e-post, per nummer.** Hopper den på e-post 5, er tilbudet feil
   plassert. Hopper den på e-post 2, er tonen feil.
9. **Svar på e-post 3.** Ikke en konverteringsmåling — dette er de fem elevsetningene
   agent 1 ba om, samlet inn automatisk.
10. **Antall 503-svar fra `/api/create-checkout-session`.** Mislykkede betalinger som
    ingen ser i dag.

## Tall jeg ikke ville brukt tid på

- Åpningsrate på e-post (måles stadig dårligere, og styrer mot clickbait-emnefelt)
- Følgere
- Visninger alene, uten steg ②

---

# DEL 5 — Sprik jeg fant mellom de foregående dokumentene

Ni funn. To av dem er alvorlige nok til å endre konklusjoner i `02-offer.md`.

### 1. Gratisuken finnes, og ingen av de tre foregående agentene nevner den

`TRIAL_DAYS = 7` (`server.py:53`), gitt ved registrering (`server.py:2072`), full
Premium (`_user_has_active_premium`, `server.py:724-730`), uten kort
(`server.py:756`), én gang per e-post og enhet (`server.py:758-764`).

**Hva dette velter:**

| Påstand i `02-offer.md` | Status etter dette funnet |
|---|---|
| «Tilbudet slik det står i dag har ingen risikofjerner utover gratisnivået» (Second Pass #3) | **Feil.** En sju dagers full gratisuke uten kort er en sterkere risikofjerner enn FORSLAG R2 (14 dagers pengene tilbake), og den finnes allerede |
| «Gratisnivået er i praksis vår største konkurrent» (åpent spørsmål 5) | **Delvis feil.** Den første uken er ikke gratisnivået — den er Premium. Konkurransen begynner på dag 8 |
| FORSLAG G1: «flytt tyngdepunktet til eksamensmodus» | **Styrket, ikke svekket** — men premisset må skrives om. Brukeren *har* hatt eksamensmodus. Spørsmålet er ikke om hen vet hva det er, men om hen brukte det |
| FORSLAG R2 (14 dagers pengene tilbake) | Bør revurderes. Det legger en garanti oppå en gratisuke. Kanskje riktig likevel, men det er en annen beslutning enn den agent 2 beskrev |
| «Prøv gratis så lenge du vil. Betal når du vet at det virker» | Ufullstendig. Kundens faktiske opplevelse er: alt i sju dager, så 10 per dag. Setningen forbereder ingen på det |

Jeg tror ikke agent 2 var uaktsom. Gratisuken lever i `webapp.py` som «GRATISUKE» og i
`server.py` som `trial_*`, og den dukker ikke opp når man søker etter
`ACCESS_*`-konstantene eller paywall-tekstene. Men konsekvensen er reell: **agent 2
foreslo å bygge noe som allerede finnes.**

### 2. Dag 8 har ingen tekst, i noen av dokumentene

Se «Hullet på dag 8». Ingen av de fire agentene, meg inkludert i bestillingen, har
fått i oppdrag å skrive for det øyeblikket produktet faktisk blir dårligere for
brukeren. Det er der vi taper folk, og det er der ingen ser etter.

### 3. Business-briefen selv er uenig med agent 2 om regnestykket

`business-brief.md` punkt 5: *«En livstidslisens til 699 kr trenger bare å spare ett
strøket forsøk for å ha betalt seg selv.»*

`02-offer.md` viser at det ikke stemmer: ett strøket forsøk er 480 kr `[UVERIFISERT]`,
og 480 < 699. Agent 2 har rett, og fasitdokumentet tar feil. **Setningen i
business-briefen bør rettes**, ellers vil den bli sitert i god tro av neste kjøring.

### 4. Agent 2 listet fem premium-funksjoner. Det er seks

`server.py:824-833` har også `full_video_learning: is_premium`. Den står ikke i
«Hva kunden får» i `02-offer.md`, og den står ikke i paywallen. Jeg har tatt den med
i e-post 5 kun indirekte, fordi jeg ikke vet hva videolæringen faktisk inneholder —
**det må Michael eller Deep bekrefte før den selges på.**

### 5. FORSLAG T2 er delvis allerede implementert

Agent 2 skriver at paywall-teksten alltid sier «Du har brukt 5 gratis spørsmål».
Men `webapp.py:6155-6156` bytter allerede teksten til `trial_ended` når
`user.trial_used === true` og prøveuken ikke er aktiv. Feilen agent 2 beskriver
gjelder altså i et smalere tilfelle enn hen tror. Verdt å sjekke før Anti bruker tid
på det.

### 6. Den ene e-posten som finnes i produktet bryter språkregelen

`backend/scripts/retention_worker.py` sender norsk og thai i samme e-post, i samme
emnefelt (linje 49), i samme brødtekst (linje 87-115) og i samme lenketekst
(linje 105: «กลับไปฝึก · Fortsett øvingen»). `CLAUDE.md` sier 100 % isolasjon, ingen
fallback. Dette er en direkte konflikt, i produksjonsnær kode.

Jeg har ikke rørt filen. Men sekvensen min kan ikke sendes fra samme system uten at
noen tar stilling til hvilken regel som gjelder.

### 7. Avmeldingen i den e-posten går til feil sted, og kanskje ingen steder

Linje 121: `https://thai2drive.com/settings`. Produksjonsdomenet er
`thai2drive.no` overalt ellers (`server.py:1194-1208`, `5134-5135`). Søk på
`unsubscribe`, `email_opt_out` og `avmeld` i hele `backend/` gir **null treff**.

En avmeldingslenke som ikke virker er en skjult avmelding, uansett om den er ment
slik. Det bryter min egen absolutte regel, og den kan ikke omgås ved at jeg skriver
en pen avmeldingssetning på thai. **Sekvensen min er blokkert til dette er ekte.**

### 8. Agent 3 lot CTA-en stå åpen med riktig begrunnelse — men undervurderte hvor galt det sto

`03-angles.md` skriver: «det som faktisk er nytt for en gratisbruker er eksamensmodus
og forklaringen på thai». Det er riktig for en bruker **på dag 8 og senere**. For en
ny bruker er det ikke nytt — hen får det gratis i en uke. Vurderingen var riktig i
retning, feil i grad, og det skyldes at gratisuken ikke var kjent.

### 9. Modellvalget må gjøres én gang, for både video og PDF

Agent 3 lot «พระราชา / คนรับใช้» stå med «เจ้าของบ้าน / แขก» som alternativ, avhengig
av Michaels kulturvurdering. Lead magneten min bruker samme modell. **De to kan ikke
velges hver for seg.** Blir videoen konge/tjener og PDF-en vert/gjest, ryker
gjenkjennelsen, og gjenkjennelsen er hele grunnen til at broen virker. Ett valg,
begge steder.

---

# DEL 6 — Valideringsliste til Michael

Agent 1 merket thai-ordlisten `[IKKE INNSAMLET]`. Alt thai i dette dokumentet er
mitt, ikke observert kundespråk. Dette tar under femten minutter, og ingen av
spørsmålene kan besvares fra denne stolen.

### Språk og register

| # | Spørsmål | Hva som skjer med svaret |
|---|---|---|
| 1 | Sier målgruppen **vikeplikt** som låneord midt i en thai-setning, eller **การให้ทาง**? | Arvet fra agent 3. Lead magneten er skrevet for det første. Er svaret det andre, endres side 3 og bildekortet |
| 2 | **วงเวียน** eller låneordet *rundkjøring*? | Side 10 og e-post 3 |
| 3 | **ข้อสอบทฤษฎี** eller låneordet *teoriprøve*? | Forekommer i alle fem e-postene |
| 4 | Er **ครับ** riktig register mot voksne, noen eldre enn Michael? | Hele sekvensen. Feil register leser som belærende, og det er det verste vi kan være mot denne gruppen |
| 5 | Er «ไม่ใช่ที่คุณ มันที่คำ» (det er ikke deg, det er ordet) naturlig thai? | Det er sekvensens emosjonelle kjerne, e-post 2 |
| 6 | Er **โครน** riktig ord for kroner, eller sier de **kr** / **NOK**? | E-post 5, prisene |

### Fag og fakta

| # | Spørsmål | Hvorfor jeg spør |
|---|---|---|
| 7 | Er de sju ordforklaringene faglig riktige, formulert slik en trafikklærer ville formulert dem? | De kommer fra tabell B1 hos agent 1, ikke fra deg. Særlig **fartstilpassing** og **aktsomhet** er komprimert hardt for å tåle 7-årsregelen |
| 8 | Ligger de to spørsmålene jeg bruker (høyreregel og rundkjøring) faktisk i produksjonsdatabasen? | Jeg har lest seed-scriptet, ikke databasen |
| 9 | Gjelder «den som kjører inn har vikeplikt» i **alle** norske rundkjøringer? | Arvet fra agent 3, punkt 9. Jeg påstår det i e-post 3, basert på produktets eget innhold |
| 10 | Er «fletteregel = annenhver bil» presist nok, eller er glidelåsbildet misvisende i norsk regelverk? | Side 6 |

### Beslutninger bare du kan ta

- [ ] Konge/tjener eller vert/gjest — **ett valg, både video og PDF**
- [ ] Skal 480 kr-blokken inn i e-post 5? Krever at du åpner
      `vegvesen.no/forerkort/ta-forerkort/gebyr/` først
- [ ] Skal månedsplanen selges i det hele tatt, før vi kan svare på «hvordan sier jeg
      opp?»
- [ ] Har du en ekte elevhistorie, med tillatelse og egne ord, til e-post 3?
- [ ] Hvem svarer på svarene som kommer inn på e-post 3? Kommer det femti, er det
      arbeid

---

# DEL 7 — Hva som må implementeres av Anti

Ingenting av dette gjør jeg. Jeg har ikke rørt kode, ikke satt opp e-postverktøy,
ikke koblet til noe og ikke publisert noe. Listen er sortert etter hva som blokkerer
hva.

### Blokkerende — sekvensen kan ikke sendes uten

- [ ] **Ekte avmelding.** Endepunkt + felt på bruker + side som faktisk melder av. Det
      finnes ikke i dag (null treff på `unsubscribe` i `backend/`). Uten dette bryter
      vi vår egen absolutte regel
- [ ] **Rett domenet i `scripts/retention_worker.py`** — `thai2drive.com` → `thai2drive.no`
      (linje 105, 121, 137). Avmeldingslenken peker i dag på et domene vi ikke bruker
- [ ] **Svaradresse som virker.** E-post 3 ber om svar. `SENDGRID_FROM_EMAIL` er
      `noreply@thai2drive.no` (`server.py:489`, `support_chat.py:223`). Et svar dit
      forsvinner
- [ ] **Beslutning om språkregelen i eksisterende e-post.** `retention_worker.py`
      blander norsk og thai. Enten gjelder `CLAUDE.md`, eller så gjelder den ikke —
      men vi kan ikke ha to sekvenser med hver sin regel fra samme avsender

### Nødvendig for at reisen skal henge sammen

- [ ] **Landingsside med e-postfangst** (steg ③). Finnes ikke. Uten den er hele
      sekvensen teoretisk
- [ ] **Hosting av PDF-en** på en lenke som ikke krever innlogging
- [ ] **Kilde-tagging på registrering** slik at `User Signed Up` kan skilles på om
      hen kom fra kampanjen eller ikke (`server.py:2101` sender allerede eventet)
- [ ] **Utløst e-post ved `trial_expires_at`** — hullet på dag 8. Dette er den
      enkeltendringen jeg tror er mest verdt, og den er ikke bestilt

### Retting av innhold, før publisering

- [ ] **`vikeplykt` → `vikeplikt`** i `backend/scripts/seed_vikeplikt_questions.py`
      linje 203 (`explanation_no`). Funnet av agent 3, verifisert av meg. Og:
      **er scriptet allerede kjørt mot produksjon, må dataene rettes, ikke bare filen**
- [ ] Sjekk om samme skrivefeil finnes i andre seed-filer

### Målingene fra del 4

- [ ] Teller for steg ②→③ og ③→⑥
- [ ] Rapport: kjøp per plan, siste 4 uker
- [ ] Rapport: andel registrerte som starter eksamensmodus innen gratisuken
- [ ] **Alarm på 503 fra `/api/create-checkout-session`** (`server.py:1539-1540`) —
      mislykkede betalinger vi i dag ikke ser

### `FORSLAG` — kun hvis Michael ber om det

- [ ] Variant 2 av CTA-en (eksamensmodus-pass). Se del 0 for de sju punktene.
      **Min anbefaling er å la være**
- [ ] Paywall-teksten: `02-offer.md` FORSLAG T1 (bytt skiltgalleri mot forklaringene
      på thai). Sjekk T2 mot `webapp.py:6155` først — den er delvis gjort

---

# Strategic Second Pass

| # | Spørsmål | Score | Begrunnelse |
|---|----------|-------|-------------|
| 1 | Målgruppe spesifikk | 4/5 | Bytt-ut-testen: bytt «thai» med «polsk», og lead magneten faller ikke helt — sju norske fagord er en barriere for alle fremmedspråklige. Men e-post 2 og 4 kollapser fullstendig (polske førerkort byttes inn 1:1; polsk er ikke et språk prøven mangler på samme måte), og e-post 4 er den som avgjør kjøpet. Trekk fordi jeg fortsatt ikke kan navngi tre virkelige personer, og fordi hver eneste thai-setning i dokumentet er min, ikke deres. E-post 3 er mitt forsøk på å tette akkurat det hullet — men den samler inn data, den har dem ikke. |
| 2 | Smerten akutt | 4/5 | «Jeg stirrer på et ord jeg har lest femti ganger» er noe leseren gjorde i går, ikke noe hen burde bry seg om. Lead magneten løser det på 15 minutter. Trekk av to grunner: kategorivalget er fortsatt `[ANTAKELSE]` (ingen har kjørt spørringen), og den mest akutte smerten — tremånedersfristen — har jeg med vilje ikke brukt som driver, fordi den bare kan nevnes som opplysning og aldri som klokke. Det er riktig, og det koster meg et poeng her. |
| 3 | Løftet troverdig | 5/5 | Dette er den ene jeg gir full score, og begrunnelsen er konkret: jeg fjernet det bestilte løftet fordi det var usant, og erstattet det med ett som er verifisert linje for linje i koden. Lead magneten lover 7 ord på 15 minutter og leverer 7 ord på 15 minutter — maksimalt motbevisbart. E-post 3 sier høyt at vi ikke har elevhistorien. E-post 4 forteller om tolkealternativet som ikke gir oss en krone. E-post 5 sier «ikke kjøp hvis du er usikker», og nevner ikke månedsplanen fordi vi ikke kan svare på hvordan man sier den opp. Ingen garanti om bestått noe sted. Jeg har ikke funnet ett løfte her jeg ikke kan peke på kilden til. |
| 4 | Lead magnet trekker videre | 4/5 | Den løser ett problem helt, den er verdt å beholde uten å kjøpe noe, og neste steg er den bokstavelige fortsettelsen av side 11 — ikke et salgsbrev. Løftet fra agent 2 og 3 (begge ga 3/5) skyldes at gratisnivået konkurrerer med betalproduktet, og der er jeg faktisk mer optimistisk enn dem: gratisuken gir brukeren eksamensmodus og forklaringene i sju dager, altså opplever hen betalproduktet før hen skal bestemme seg. Det er en mye bedre bro enn noen av oss trodde vi hadde. Trekk fordi hele broen ⑤→⑥ ikke er bygget: landingssiden finnes ikke, PDF-en har ingen hosting, og dag 8 har ingen tekst. |
| 5 | Tjener penger | 3/5 | Jeg kan tegne veien fra video til betaling — elleve steg, og jeg har markert hvor de ryker. Men den ærlige scoren er 3, av tre grunner. **Én:** tre av elleve steg finnes ikke i produktet i dag (landingsside, avmelding, dag 8-e-post). **To:** regnestykket bakover viser ca. 133 000 visninger for 100 kunder, og hver rate i det er `[ANTAKELSE]`. **Tre:** det jeg leverer er øverst i trakten, og øverst i trakten tjener ingen penger alene. Agent 3 ga seg selv 3 her av samme grunn, og jeg ser ikke at jeg har rett til en høyere score bare fordi jeg er sist. |
| 6 | Høres interessant ut | 3/5 | «vikeplikt betyr ikke vanskelig, det betyr vent» er agent 3 sin linje, ikke min. Min beste er emnefeltet på e-post 3 — «ผมไม่มีเรื่องเล่าจากนักเรียนให้คุณอ่าน» («jeg har ingen elevhistorie å gi deg») — den ville jeg åpnet. Men resten av sekvensen er rolig og nyttig snarere enn interessant, og det er et bevisst valg jeg står for: Michael-tonen er trygg og konkret, ikke fengende. Og det avgjørende trekket: **jeg har skrevet fem e-poster på et språk jeg ikke snakker daglig.** Varme og rytme er det første som ryker der. Jeg vet ikke om de er gode på thai. Jeg vet at de er korrekte, og det er ikke det samme. |

**Snitt:** 3,6 — **Svakeste ledd:** #5 og #6

**Hva jeg ville fikset først:**

Snittet er under porten på 4,0, og det er det laveste i kjøringen. Jeg lar det stå, av
samme grunn som de tre foran meg — men jeg vil være presis på hva som faktisk trekker
ned, for det er ikke det samme som hos dem.

- **#5 løftes ikke av tekst i det hele tatt.** Tre av elleve steg i kjøpsreisen finnes
  ikke som kode. En landingsside, en fungerende avmelding og én utløst e-post ved
  `trial_expires_at`. Det er Antis liste i del 7, og til den er gjort, er alt jeg har
  skrevet et manus til et system som ikke står.
- **#6 løftes av én person, og det er ikke meg.** Michael er thaifødt. Femten minutter
  med valideringslisten i del 6 avgjør om e-postene høres ut som en trafikklærer som
  snakker til deg, eller som en oversettelse. Jeg kan ikke høre forskjellen. Det er
  den ærligste setningen i dette dokumentet.
- **#1 løftes av e-post 3, men først etter at den er sendt.** Den ber om én setning
  fra hver leser. Kommer det tjue svar, har agent 1 sitt manglende råmateriale — og
  neste kjøring starter med ekte kundespråk i stedet for min oversettelse.
- **#2 løftes av spørringen i `01-market-signals.md` del A.** Tjue minutter i Atlas.
  Er ikke vikeplikt verst, byttes de sju ordene og de to spørsmålene. Strukturen står.

**Det jeg ikke ville gjort først:** sendt noe som helst. Ikke fordi tekstene ikke er
klare, men fordi avmeldingen ikke virker. Å sende en sekvens til en gruppe med lav
tillit til systemer, uten en fungerende vei ut, er nøyaktig den feilen vi bruker hele
dette dokumentet på å unngå.

---

## Michael-passet

- [ ] Har jeg faktisk hørt en elev si dette?
- [ ] Ville jeg sagt dette høyt i et klasserom?
- [ ] Ville jeg vært stolt av at en kollega så dette?
- [ ] Er det respektfullt mot noen som allerede har strøket to ganger?

Spørsmål fire er grunnen til at e-post 3 sier at vi ikke har en elevhistorie i stedet
for å finne på en, og grunnen til at e-post 5 begynner med hva som er gratis for
alltid før den nevner en pris. Ett nei fra deg overstyrer alle seks scorene over.
