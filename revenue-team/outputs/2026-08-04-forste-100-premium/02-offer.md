---
agent: offer-architect
kjøring: 2026-08-04-forste-100-premium
input: business-brief.md, 00-brief.md, 01-market-signals.md
second-pass-score: 3,7
åpne spørsmål: >
  1) Bestillingen ba meg bekrefte 199 kr/mnd. Jeg kan ikke. Live fallback-pris er 99 kr/mnd
     (backend/server.py:146-155). Se seksjon «Verifisering av bestillingen».
  2) Gebyret på 480 kr er fortsatt [UVERIFISERT]. Michael må åpne
     vegvesen.no/forerkort/ta-forerkort/gebyr/ før tallet trykkes noe sted.
  3) Hva koster en godkjent thai-tolk til teoriprøven? Uten det tallet mangler tilbudet
     sitt sterkeste regnestykke. Jeg har lagt inn formelen, ikke et gjettet beløp.
  4) Jeg fant ingen billing-portal i backend. Hvordan sier en månedskunde faktisk opp?
  5) Gratisnivået (10 spørsmål/dag, uten sluttdato) er i praksis vår største konkurrent.
     Krever en produktbeslutning, ikke en tekstendring.
---

# Tilbud — Thai2Drive Premium, første 100 kunder

> **Til Michael, før du leser videre:** du ba meg bekrefte at prismodellen er optimalisert
> til 199 / 249 / 699. Jeg kan ikke bekrefte det, av to grunner. Prisen som kjøres i
> produksjon er ikke 199. Og hvis den ble 199 uten at de to andre prisene flyttes, slutter
> pristrappen å henge sammen. Begge deler er regnet ut under, med kilde i koden.

---

## Verifisering av bestillingen

### Funn 1 — månedsprisen i bestillingen finnes ikke i produkt

| Plan | Bestillingen sa | Det som ligger i koden | Stemmer? |
|---|---|---|---|
| Månedlig | 199 kr | **99 kr** | ✗ |
| 3 måneder | 249 kr | 249 kr | ✓ |
| Livstid | 699 kr | 699 kr | ✓ |

Verifisert av meg i repoet:
- `backend/server.py:146-174` — `PUBLIC_PRICING_FALLBACK`: `monthly.amount = 99`,
  `three_months.amount = 249`, `lifetime.amount = 699`.
- `backend/webapp.py:3938, 3944, 3949` — paywall-kortene viser «99 kr», «249 kr», «699 kr»
  som HTML før JavaScript henter live pris. `backend/webapp.py:4795-4797` har samme tre
  tall som klientside-fallback.
- «Best verdi»-merket ligger allerede på 3-månederskortet (`backend/webapp.py:3942`).
  Den delen av bestillingen er altså allerede implementert.

### Funn 2 — hvem som egentlig bestemmer prisen

`_get_live_stripe_plan_prices_sync()` (`backend/server.py:1123-1159`) henter alle aktive
Stripe-priser og matcher dem mot produktnavn: `Thai2Drive Premium`,
`Thai2Drive 3 Months`, `Thai2Drive Lifetime`. Finner den en pris, **overstyrer Stripe koden**
(`base.update({"amount": ...})`, linje 1147-1153). Er prisen ikke i livemode, forkastes hele
oppslaget og fallback brukes (linje 1141-1143). Resultatet caches i 5 minutter
(`server.py:1178`).

**Konsekvensen, sagt rett ut:** tallene i koden er et sikkerhetsnett, ikke fasit. Den ekte
prisen ligger i Stripe, og jeg har verken tilgang dit eller lov til å se etter.

**Michael kan verifisere selv på ti sekunder** — åpne
`https://www.thai2drive.no/api/pricing` i nettleseren. Står det `"source": "stripe_live"`,
er beløpene der de ekte prisene. Står det `"fallback"`, er det 99 / 249 / 699 som vises.
Gjør dette **før** du godkjenner noe under. Hele regnestykket mitt hviler på at
månedsprisen er 99.

---

## Kjerneløftet

> **Du lærer trafikkreglene på thai — og kjenner igjen de norske ordene når de kommer på prøven.**

### Hvorfor løftet må formuleres slik, og aldri som «ta teoriprøven på thai»

Teoriprøven for klasse B finnes **ikke** på thai. Den tilbys digitalt på bokmål, nynorsk,
nordsamisk, engelsk, arabisk (MSA), sorani og tyrkisk. [K7, via 01-market-signals.md]
Vil du ha thai, må du søke om *tilrettelagt prøve med tolk*, og du må selv finne og betale
tolken. [K8][K9]

Sier vi «ta prøven på thai», brister løftet i det sekundet eleven setter seg foran skjermen
på trafikkstasjonen. Da har vi ikke mistet en kunde — vi har mistet en kunde som forteller
det videre i et lite miljø der alle kjenner alle. Prisen på den løgnen er høyere enn hele
kampanjen er verdt.

Løftet vi *kan* holde er dette: eleven møter det norske ordet på prøven og vet hva det betyr,
fordi hen har lært innholdet på et språk hen tenker på. Det er ikke et svakere løfte. Det er
det eneste som faktisk beskriver produktet.

**Vi lover aldri bestått prøve.** Vi kontrollerer ikke prøven.

---

## Hva kunden får

Hvert punkt er sporet til en smerte i `01-market-signals.md`, og til hvor funksjonen faktisk
finnes i koden. Punkter uten begge deler er strøket.

| Hva kunden får | Hvilken smerte det løser | Verifisert i |
|---|---|---|
| **Hele eksamensmodusen — 45 spørsmål på rad, som på ekte prøve.** Det gratisnivået aldri kan gi deg, uansett hvor lenge du øver: svaret på «er jeg klar?» | Smerte 2 (tremånedersfristen — du må vite om du er klar *nå*, ikke om tre uker) | `server.py:826` `exam_mode: is_premium`. Prøvens form: 45 spørsmål, maks 7 feil, 90 min [K6][K22] |
| **Forklaringen på thai når du svarer feil.** Ikke «feil svar», men hvorfor — på språket du tenker på | Smerte 3 (det er ordene, ikke reglene) | `server.py:827` `ai_explanations: is_premium`; `backend/ai_explanations.py` |
| **Michael Trafikklærer svarer på thai.** 16 år som trafikklærer, thaifødt. Du slipper å be en fremmed om hjelp på et språk du ikke er trygg i | Smerte 3 + skamterskelen (business-brief pkt. 3) | `backend/teacher_chat.py` |
| **Trening på temaene du selv bommer på**, ikke de du allerede kan | Smerte 3 (du gir ikke opp fordi vikeplikt er vanskelig — du gir opp fordi du leser samme setning femte gang) | `server.py:828` `weak_topic_training: is_premium` |
| **Ubegrenset øving, ingen daglig grense** | Smerte 2 (klokka går — den som må bli ferdig på tre måneder kan ikke rasjonere ti spørsmål om dagen) | `server.py:825` `unlimited_questions: is_premium` |
| **Historikk og fremgang** — svart på hvitt at det går fremover | Skamterskelen: målgruppen har ofte strøket før og tror de ikke kan | `server.py:829` `advanced_history: is_premium` |

### Det viktigste jeg fant i paywallen

Paywallen i dag selger dette (`backend/webapp.py:3929-3933`):

1. Ubegrenset spørsmål og kategorier
2. Fullstendig eksamensmode
3. Daglig test og øvingsmodus
4. Historikk og fremgangsstatistikk
5. **Trafikkskilt-galleri**

Den nevner **ikke** AI-forklaringene på thai. Den nevner **ikke** Michael-læreren. Begge er
premium i koden (`server.py:827`), og begge er det eneste ingen andre teoriapper i Norge
kan tilby denne gruppen.

Vi selger altså et skiltgalleri, og gir bort grunnen til å kjøpe.

Dette er den billigste enkeltendringen i hele dokumentet: bytt punkt 5 mot
«Michael forklarer på thai når du svarer feil». Ingen prisendring, ingen ny funksjon,
ingen ny kode utover én tekststreng i tre språk. Se `FORSLAG T1`.

---

## Pris og begrunnelse

### Slik ser trappen ut i dag (99 / 249 / 699)

| Regnestykke | Utregning | Svar |
|---|---|---|
| 3 måneder kjøpt månedsvis | 3 × 99 | 297 kr |
| 3-månederspakken | | 249 kr |
| Rabatt | (297 − 249) / 297 | **16,2 %** |
| Effektiv månedspris i pakken | 249 / 3 | 83 kr |
| Livstid delt på pakken | 699 / 249 | 2,81 × |
| Måneder før livstid lønner seg mot månedspris | 699 / 99 | 7,1 mnd |

Dette er en sunn trapp. Rabatten er stor nok til å belønne den som binder seg, og liten nok
til at månedsprisen fortsatt er et ekte valg. Livstid er nesten tre ganger pakken — et reelt
hopp, som skal føles som en beslutning.

### Slik ser den ut med 199 / 249 / 699

| Regnestykke | Utregning | Svar |
|---|---|---|
| 3 måneder kjøpt månedsvis | 3 × 199 | 597 kr |
| 3-månederspakken | uendret | 249 kr |
| Rabatt | (597 − 249) / 597 | **58,3 %** |
| Effektiv månedspris i pakken | 249 / 3 | 83 kr — **41,7 % av månedsprisen** |
| Hvor lenge må du bruke appen før pakken lønner seg? | 249 / 199 | **1,25 måneder** |
| Livstid delt på pakken | 699 / 249 | 2,81 × |

Den avgjørende linjen er den nest nederste. **Alle som tror de trenger appen i mer enn fem
uker, velger pakken.** Målgruppen har en tremånedersfrist på førerkortet [K12] og har ofte
strøket før — ingen av dem tror de er ferdige på fem uker.

Da er 199 kr ikke en pris. Det er et prisskilt ved siden av det du faktisk selger. Det kan
være et bevisst valg (ankerpris), men da skal vi kalle det det, og vi skal vite at vi i
praksis har to produkter, ikke tre.

### Hva dette gjør med inntekt per kunde

> Alle andeler og levetider under er `[ANTAKELSE]`. Vi har ingen konverteringsdata og ingen
> churn-data i denne kjøringen. Modellen viser **hvor pengene kommer fra**, ikke hvor mye
> som kommer inn. Bruk strukturen, ikke tallene.

**A) Dagens priser, 100 betalende kunder**
`[ANTAKELSE]` fordeling 30 / 45 / 25, og at et månedsabonnement i snitt betales 2 ganger.

| Plan | Kunder | Inntekt per kunde | Sum |
|---|---|---|---|
| Månedlig 99 | 30 | 99 × 2 = 198 | 5 940 |
| 3 mnd 249 | 45 | 249 | 11 205 |
| Livstid 699 | 25 | 699 | 17 475 |
| **Sum** | 100 | | **34 620 kr** |

Inntekt per kunde: **346 kr**. Månedsplanens andel av inntekten: **17,2 %**.

**B) 199 / 249 / 699, samme 100 betalende kunder**
`[ANTAKELSE]` fordeling 8 / 62 / 30 — månedsplanen kollapser fordi den er irrasjonell etter
fem uker. `[ANTAKELSE]` de få som likevel velger måned, betaler 1,3 ganger.

| Plan | Kunder | Inntekt per kunde | Sum |
|---|---|---|---|
| Månedlig 199 | 8 | 199 × 1,3 = 259 | 2 070 |
| 3 mnd 249 | 62 | 249 | 15 438 |
| Livstid 699 | 30 | 699 | 20 970 |
| **Sum** | 100 | | **38 478 kr** |

Inntekt per kunde: **385 kr**. Månedsplanens andel av inntekten: **5,4 %**.

**Les dette to ganger:** inntekten går opp med 11 %, men **ikke én krone av økningen kommer
fra at månedsprisen ble høyere.** Den kommer fra at folk flytter seg fra måned til pakke og
livstid. Vi doblet en pris nesten ingen betaler.

**Og gevinsten er skjør.** 34 620 / 385 = **89,9**. Faller konverteringen med bare **10 %** —
fordi 199 kr er det første tallet et nytt øye ser i paywallen — er hele gevinsten borte.
Under det taper vi penger på endringen.

Vi vet ikke om konverteringen faller. Det er nettopp poenget: vi vet ikke, og forskjellen
mellom å ha rett og å ta feil er ti prosentpoeng.

### Min anbefaling

**Ikke rør prisene ennå.** Ikke fordi 199 er feil, men fordi vi ikke kan vite om det er
riktig, og fordi det finnes gratis endringer som virker først:

1. Fiks paywall-teksten så den selger det som faktisk er unikt (`FORSLAG T1`, `T2`).
2. Anbefal riktig pakke til riktig person (`FORSLAG T3`).
3. Mål i fire uker. *Da* har du grunnlag for en prisbeslutning.

Vil du likevel ha 199 kr/mnd, må de to andre prisene flytte seg. Se `FORSLAG P2`.

---

## Risikofjerner

Målgruppen er voksne mennesker med dårlig erfaring fra systemer som presser dem
(business-brief pkt. 6). Risikofjerneren må derfor være rolig og etterprøvbar, ikke en
knapp med rødt utropstegn.

### Det som allerede virker (ingen godkjenning nødvendig)

**Gratisnivået er selve prøvingen.** 10 spørsmål hver dag, gratis, uten kort, uten frist
(`server.py:178`). Du kan bruke Thai2Drive i tre uker uten å betale, og finne ut om du
forstår forklaringene, før du bestemmer deg. Det er en sterkere risikofjerner enn en
prøveperiode, fordi den ikke går ut.

Formuleringen mot kunden er én setning: **«Prøv gratis så lenge du vil. Betal når du vet at
det virker for deg.»**

### Det som mangler, og som jeg foreslår (krever godkjenning)

**Livstid trenger en definisjon.** Vi selger «livstid» til 699 kr uten å si hvem sitt liv.
En kunde som har strøket to ganger og betalt 960 kr i gebyr [UVERIFISERT] er ikke naiv — hen
lurer på hva som skjer hvis appen forsvinner. Vi kan ikke love evig drift. Vi kan skrive
sannheten: *«Livstid betyr så lenge Thai2Drive drives. Legges tjenesten ned, sier vi fra i
god tid — vi tar ikke betalt for noe vi ikke leverer.»* Se `FORSLAG R1`.

**Det finnes ingen synlig vei ut av et abonnement.** Jeg søkte i hele `backend/` etter et
Stripe billing-portal-endepunkt og fant ingen. For en gruppe som er redd for å bli fanget i
noe de ikke forstår, er «hvordan sier jeg opp?» et kjøpsstoppende spørsmål. Se `FORSLAG R3`
— dette er Antis bord, jeg konstaterer bare hullet.

---

## Regnestykket kunden gjør

> **[UVERIFISERT] gjelder hver eneste linje der 480 kr står.** Agent 1 fant tallet på tre
> norske nettsteder med samme sats og samme dato [K1][K2][K3], men fikk 403 på vegvesen.no.
> Jeg forsøkte også — nettverkspolicyen her blokkerer domenet. **Ingen av oss har lest tallet
> på Vegvesenets egen side.** Michael må åpne
> `vegvesen.no/forerkort/ta-forerkort/gebyr/` og bekrefte før dette trykkes noe sted.
> Én kilde oppga 680 kr (2024) [K20] og én oppga 350 kr [K21]. Spriket er reelt.

### Hovedregnestykket — det som skal stå i annonsen

| | Beløp | Kilde |
|---|---|---|
| Ett strøket forsøk på teoriprøven | 480 kr | [K1][K2][K3] `[UVERIFISERT]` |
| To strøkne forsøk | 960 kr | samme |
| Thai2Drive livstid | **699 kr** | `server.py:168-171` |

**To strøkne forsøk koster mer enn å eie appen for alltid.** Det er hele argumentet. Det
trenger ingen pynt, ingen utropstegn og ingen nedtelling.

Ærlig forbehold vi må tåle: **ett** strøket forsøk (480 kr) dekker *ikke* livstidsprisen.
Det gjør det for 3-månederspakken (249 kr), som er billigere enn ett eneste gebyr. Ikke
strekk tallet lenger enn det går.

### Hva 249 kr er, i ting kunden allerede kjenner prisen på

| Sammenlikning | Regnestykke | Kilde |
|---|---|---|
| 3-månederspakken mot ett prøvegebyr | 249 av 480 kr — **omtrent halvparten** | [K1] `[UVERIFISERT]` |
| 3-månederspakken mot én kjøretime | 249 av 600–850 kr — **under en tredjedel** | [K4][K5] |
| Livstid mot én kjøretime | 699 av 600–850 kr — **ca. én time** | [K4][K5] |

Kjøretimeprisen er et intervall fra bransjenettsteder, ikke offisiell statistikk. Bruk
intervallet «600–850 kr», ikke et snitt. Et snitt på 750 kr ville vært `[ANTAKELSE]`.

### Andre satser vi har, og som ikke skal blandes sammen

| Post | Beløp | Kilde |
|---|---|---|
| Praktisk førerprøve klasse B | 1 540 kr | [K1][K2] `[UVERIFISERT]` |
| Utstedelse av førerkort | 160–270 kr | [K2] `[UVERIFISERT]` |
| Foto | 100 kr | [K2] `[UVERIFISERT]` |

Disse skal **ikke** legges sammen og presenteres som «hva førerkortet koster». Vi mangler
trafikalt grunnkurs, obligatoriske kurs og kjøretimer i den summen. En ufullstendig totalsum
er en feil vi ikke trenger å gjøre.

### Tolkeregnestykket — formelen, ikke et tall

Dette er det sterkeste argumentet i hele tilbudet, og det mangler ett tall.

Vil en thaitalende ha prøven på sitt eget språk, må hen søke om tilrettelagt prøve og selv
bestille og betale tolk. [K8][K9] Tolken må være godkjent av Statens vegvesen for teoriprøve
og tilknyttet et byrå som kan skjermtolking. [K16] Agent 1 fant **ikke** prisen —
tolkebyråene oppgir at pris sendes etter at tolk er funnet. [K9][K25] Jeg finner den ikke på.

**La T = det en godkjent thai-tolk koster per teoriprøve.**

| Spørsmål | Svar |
|---|---|
| Kostnad per forsøk med tolk | 480 + T kr `[UVERIFISERT]` |
| Når er livstid (699 kr) billigere enn **ett** forsøk med tolk? | Når T > 219 kr |
| Når er 3-månederspakken (249 kr) billigere enn **ett** forsøk med tolk? | Alltid, siden 249 < 480 |

Den midterste linjen er ren aritmetikk, ikke en påstand: 699 − 480 = 219. Er tolken dyrere
enn 219 kr, har vi et regnestykke som står av seg selv. **Michael: én e-post til
TolkeNett [K9] eller Noricom [K25] og én til en spesialisert thai-tolk [K17][K18] fyller inn
T.** Det er tjue minutters arbeid, og det er sannsynligvis den enkeltoppgaven i hele denne
kjøringen med høyest avkastning.

Til den er gjort: **ikke bruk tolk-argumentet med et tall.** Bruk det som setning —
«alternativet er å betale for tolk, hver gang du prøver» — uten beløp.

---

## Hvem dette ikke er for

Dette skal stå på salgssiden, ikke bare i dette dokumentet. Det gjør resten troverdig.

- **Er du trygg på norsk fagspråk, trenger du oss ikke.** Forstår du *aktsomhet*,
  *bremseberedskap* og *fartstilpassing* uten å stoppe opp, finnes det gratis norske
  øvingsressurser som holder. Ta dem. (Smerte 3)
- **Vil du ha prøven på thai, kan vi ikke hjelpe deg med det.** Prøven finnes ikke på thai.
  Vi lærer deg innholdet på thai, så du kjenner igjen de norske ordene. Skal du ha tolk på
  selve prøven, må du søke om tilrettelagt prøve og bestille tolken selv. [K7][K8][K9]
- **Er du ute etter en garanti for å bestå, er vi feil sted.** Ingen app kan love det. Den
  som lover det, lyver.
- **Er du ferdig i morgen, kjøp heller ingenting.** Bruk gratisnivået. 10 spørsmål i dag og
  10 i morgen koster deg null.
- **Skal du ta klasse A, C eller D:** Thai2Drive dekker klasse B (business-brief pkt. 2).

---

## Innvendinger, og svaret på dem

> Alle innvendinger under er utledet fra dokumenterte funn i `01-market-signals.md`, ikke fra
> elevsitater. **Agent 1 fant ikke ett eneste ordrett sitat fra målgruppen** — se «Hva jeg
> IKKE fant». Jeg har ikke laget sitater for å fylle hullet. Formuleringene under er mine, og
> Michael må sjekke dem mot hvordan elever faktisk snakker før de brukes ordrett.

**1. «Hjelper det, når prøven uansett er på norsk?»**
Kilde: Smerte 1 — prøven finnes ikke på thai [K7][K8].
Svar: Det er nettopp derfor. Du skal møte de norske ordene på prøven uansett. Spørsmålet er
om du møter dem for første gang der, eller om du har sett dem hundre ganger og vet hva de
betyr. Vi lærer deg innholdet på thai, og ordet på norsk.

**2. «Jeg har kjørt i tjue år. Hvorfor må jeg gjøre dette i det hele tatt?»**
Kilde: Smerte 2 — Thailand står ikke på innbyttelisten [K10][K11].
Svar: Du har rett i at det er urimelig å føles. Norge bytter inn førerkort fra EU/EØS og fra
en kort liste land utenfor. Thailand er ikke på den. Erfaringen din er ikke borte — den gjør
den praktiske delen lettere. Det er teorien og ordene som står i veien, og det er den vi
tar. Utenlandsk førerkort utenfor EØS kan normalt brukes i tre måneder etter flytting. [K12]

**3. «Jeg har allerede prøvd en app. Den var full av rare spørsmål.»**
Kilde: Dokumentert kritikk av norske teoriapper — «mye feilskriving og dårlig formulerte
spørsmål», «samme svaralternativ kommer flere ganger» [K26] `[UVERIFISERT SITAT]`.
Svar: Prøv våre gratis. 10 spørsmål hver dag, uten kort. Er forklaringene like uklare som
sist, har du ikke tapt noe. Vi ber ikke om penger før du vet.
*(Vi navngir aldri hvilken app. Vi sier ikke at andre er dårlige. Vi lar eleven prøve.)*

**4. «Jeg har allerede ordboka. Er ikke det nok?»**
Kilde: Norges Trafikkskoleforbunds «I trafikken» finnes på thai, men forbundet skriver selv
at boka ikke dekker alt du trenger til prøvene [K22].
Svar: Ordboka gir deg ordet. Den gir deg ikke hvorfor bilen fra høyre kjører først i akkurat
det krysset. Det er der de fleste stryker — ikke på ordet alene, men på situasjonen ordet
beskriver.

**5. «699 kr er mye penger.»**
Kilde: Gebyr per forsøk 480 kr [K1][K2][K3] `[UVERIFISERT]`; kjøretime 600–850 kr [K4][K5].
Svar: Det er sant. Det er også omtrent én kjøretime, og mindre enn to strøkne forsøk. Er du
usikker, ta 3 måneder til 249 kr — det er under halvparten av ett prøvegebyr. Eller bli på
gratisnivået til du er sikker.

**6. «Jeg får ikke til å lese så mye norsk uansett.»**
Kilde: Smerte 3 — forskning fra Høgskolen i Nord-Trøndelag om at trafikkfaglige uttrykk ikke
gir mening for elever uten norsk som morsmål [K13] `[UVERIFISERT SITAT]`.
Svar: Det er ikke deg. Det er ordet. *Bremseberedskap* betyr «foten hviler over bremsen,
klar». Det er alt. Når noen sier det på thai én gang, sitter det.

**7. «Hva om jeg vil slutte?»**
Kilde: Jeg fant ingen billing-portal i `backend/` — se `FORSLAG R3`.
Svar: **Dette svaret finnes ikke ennå.** Jeg skriver det ikke før Michael og Anti har
bekreftet hvordan en kunde faktisk sier opp. Et oppdiktet svar her er en garanti vi ikke kan
innfri.

---

## Forslag som krever godkjenning

Alt under er merket:
**`FORSLAG — krever Michaels godkjenning og Antis implementering`**
Jeg har ikke rørt kode, Stripe, database eller kvotelogikk, og skal ikke gjøre det.

---

### FORSLAG T1 — bytt ut ett punkt i paywallen (høyest effekt, lavest risiko)
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Hva:** Erstatt «Trafikkskilt-galleri» (`pw_f5`, `backend/webapp.py:3933` og `4466`) med
«Michael forklarer på thai når du svarer feil» — på alle tre språk, hver 100 % ren.

**Hvorfor:** Skiltgalleriet er ikke grunnen til å velge oss. AI-forklaringene på thai og
Michael-læreren er premium i koden (`server.py:827`), men står ikke i paywallen i det hele
tatt. Vi selger alt annet enn det som er unikt.

**Effekt på konvertering:** bør gå opp — vi flytter det sterkeste argumentet inn i det
vinduet folk faktisk leser. **Effekt på inntekt per kunde:** ingen. Prisen er uendret.

**Hva som må måles:** andel som trykker «Kjøp Premium» når paywallen vises, målt fire uker
før og fire uker etter. `access_events` og Segment ligger allerede i backend.

**Merknad om språkrenhet:** teksten må inn i `TRANSLATIONS`-blokken
(`backend/webapp.py:4461-4466`) med separate `th`, `no` og `en`. Ingen blanding, ingen
fallback. Det er en absolutt regel, ikke en preferanse.

---

### FORSLAG T2 — paywall-teksten lyver for halvparten av dem som ser den
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Hva:** `pw_sub` sier «Du har brukt 5 gratis spørsmål» (`backend/webapp.py:3927, 4461`).
Det stemmer for gjester (`ACCESS_GUEST_TOTAL_LIMIT = 5`). For en registrert bruker er
grensen 10 per dag (`ACCESS_REGISTERED_DAILY_LIMIT = 10`, `server.py:178`), og setningen er
feil. Teksten bør velges ut fra `tier`-feltet som `_access_policy_payload` allerede returnerer
(`server.py:815`).

**Hvorfor:** Dette er samme feil som blokkering B3 i `00-brief.md`, bare på innsiden av
produktet. Et tall som ikke stemmer, i det øyeblikket vi ber om penger, er dyrt.

**Hva som må måles:** ingenting — dette er en feilretting, ikke et eksperiment.

---

### FORSLAG T3 — anbefal riktig pakke til riktig person
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Hva:** «Best verdi»-merket står permanent på 3-månederskortet
(`backend/webapp.py:3942`). Behold det, men legg til én linje under hvert kort:

- **3 måneder (249 kr):** «Har du thailandsk førerkort og nettopp flyttet? Du har tre måneder
  på deg. Denne pakken dekker akkurat den perioden.»
- **Livstid (699 kr):** «Har du strøket før? Da vet du at det tar tid. Denne utløper aldri.»

**Hvorfor:** Utenlandsk førerkort utenfor EØS kan normalt brukes i tre måneder etter flytting
til Norge [K12]. Det er ikke kunstig hastverk — det er en frist myndighetene har satt, og som
kunden allerede kjenner på. Vi finner ikke opp klokka. Vi sier hvilken pakke som passer den.
Og for den som har strøket før, er livstid ærlig anbefalt: gjentatte forsøk tar måneder.

**Absolutt grense:** ingen nedtelling, ingen «bare X dager igjen», ingen rød tekst. Kunden
vet selv når hen flyttet. Vi minner ikke om det med en klokke.

**Effekt på inntekt per kunde:** bør gå opp — flere velger 3 mnd eller livstid fremfor
måned. **Hva som må måles:** fordelingen mellom de tre planene, fire uker før og etter.

---

### FORSLAG P1 — behold 99 / 249 / 699 til T1–T3 er målt (min anbefaling)
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Hva:** Ingen prisendring nå.

**Hvorfor:** Vi har null konverteringsdata. Å endre pris før vi har målt noe som helst,
betyr at vi aldri får vite hva som virket. T1–T3 koster ingenting, kan måles på samme trafikk
og gir grunnlaget en prisbeslutning trenger.

**Hva som må måles før neste steg:** (1) andel av paywall-visninger som blir kjøp,
(2) fordelingen mellom de tre planene, (3) hvor mange betalende måneder et månedsabonnement
faktisk varer. Punkt 3 er den eneste ukjente som virkelig avgjør om 199 er riktig.

---

### FORSLAG P2 — vil Michael ha 199 kr/mnd, må de to andre prisene flytte seg
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Prissettet: 199 / 449 / 899**

| Regnestykke | Utregning | Svar |
|---|---|---|
| 3 måneder månedsvis | 3 × 199 | 597 kr |
| Pakkepris | | **449 kr** |
| Rabatt | (597 − 449) / 597 | 24,8 % — sunn avstand |
| Effektiv månedspris i pakken | 449 / 3 | 150 kr |
| Livstid delt på pakken | 899 / 449 | 2,0 × |
| Måneder før livstid lønner seg mot månedspris | 899 / 199 | 4,5 mnd |

**Hvorfor akkurat disse:** rabatten lander på ca. 25 %, der en pakkerabatt normalt gir mening
uten å gjøre månedsprisen til en kulisse. Livstid blir nøyaktig dobbelt så dyr som pakken —
et hopp kunden kan regne ut i hodet, og som er lite nok til at oppsalget er reelt.

**Effekt på inntekt per kunde `[ANTAKELSE]`** (fordeling 20 / 50 / 30, månedskunder betaler
1,8 ganger):

| Plan | Kunder | Per kunde | Sum |
|---|---|---|---|
| 199 | 20 | 358 | 7 164 |
| 449 | 50 | 449 | 22 450 |
| 899 | 30 | 899 | 26 970 |
| **Sum** | 100 | | **56 584 kr** — inntekt per kunde 566 kr |

**Effekt på konvertering:** ned. Hvor mye vet ingen. Det som er verdt å vite er
smertegrensen: 34 620 / 566 = **61**. Faller konverteringen med mer enn **39 %**, tjener vi
mindre enn i dag. Det er en bred sikkerhetsmargin — men prisen er nesten doblet for en gruppe
som allerede betaler 480 kr per forsøk [UVERIFISERT] og kjøretimer på 600–850 kr [K4][K5].
Jeg ville ikke gjort dette i samme uke som noe annet endres.

**Hva som må måles:** kjøp per 100 paywall-visninger, fire uker før mot fire uker etter, med
alt annet holdt likt. Skift én ting av gangen, ellers vet du ingenting.

**Michael må ta stilling til:** eksisterende livstidskunder som betalte 699. De skal ikke
oppleve at prisen «steg rett etter at jeg kjøpte». Det er billigere å si det på forhånd enn å
svare på det etterpå.

---

### FORSLAG P3 — den forsiktige varianten, hvis 199 ikke er hugget i stein
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Prissettet: 149 / 299 / 799**

| Regnestykke | Utregning | Svar |
|---|---|---|
| 3 måneder månedsvis | 3 × 149 | 447 kr |
| Pakkepris | | **299 kr** |
| Rabatt | (447 − 299) / 447 | 33,1 % |
| Salgsargumentet, i én setning | 149 × 2 = 298 ≈ 299 | **«Tre måneder til prisen av to»** |
| Livstid delt på pakken | 799 / 299 | 2,67 × |
| Måneder før livstid lønner seg | 799 / 149 | 5,4 mnd |

**Effekt på inntekt per kunde `[ANTAKELSE]`** (fordeling 25 / 45 / 30, 2,0 betalte måneder):
7 450 + 13 455 + 23 970 = **44 875 kr** — inntekt per kunde 449 kr.
Smertegrense: 34 620 / 449 = **77**. Tåler et fall i konvertering på 23 %.

**Hvorfor denne er interessant:** «tre måneder til prisen av to» er et løfte en sjuåring
forstår, og en pris under 800 kr på livstid holder seg under smertegrensen «én kjøretime»
[K4][K5]. Den flytter inntekt per kunde 30 % opp med omtrent halvparten av risikoen i P2.

---

### FORSLAG R1 — definer «livstid» skriftlig
`FORSLAG — krever Michaels godkjenning`

Legg denne setningen ved livstidskortet, på alle tre språk:
*«Livstid betyr så lenge Thai2Drive drives. Legges tjenesten ned, sier vi fra i god tid.»*

**Hvorfor:** Vi selger et ord vi ikke har definert. Definerer vi det selv, i klartekst, blir
det et tillitsargument. Definerer vi det ikke, blir det en innvending vi taper.
**Effekt på konvertering:** liten, positiv. **Måles:** ikke isolert målbar — ta den sammen
med T1.

---

### FORSLAG R2 — 14 dagers pengene tilbake, på forespørsel
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Hva:** Har du kjøpt og angrer innen 14 dager, sender du en melding og får pengene tilbake.
Ingen begrunnelse. Én per person. Michael refunderer manuelt i Stripe.

**Hvorfor dette kan innfris:** Vi har ikke 100 kunder ennå — det er hele målet med kjøringen.
Ved lavt volum er manuell refusjon minutter i uka. Det kan ikke misbrukes i stor skala,
fordi hver refusjon går gjennom et menneske og kobles til én konto.

**Hva det koster hvis vi tar feil:** 10 refusjoner av 100 kunder til snittpris 346 kr
`[ANTAKELSE]` = 3 460 kr. Det er prisen på å vite. Er tallet høyere enn 10 %, har vi ikke et
garantiproblem — vi har et produktproblem, og da vil vi vite det.

**Hva som må måles:** refusjonsandel per plan. Skiller den seg kraftig mellom planene, sier
det noe om hvilken pakke som selges til feil person.

**Grense jeg selv setter:** ikke kall det «risikofritt» og ikke lag et stort merke av det.
En rolig setning under kjøpsknappen. Store garantimerker leser som noe å være skeptisk til
for akkurat denne gruppen.

---

### FORSLAG R3 — hvordan sier en kunde opp?
`FORSLAG — Antis bord — jeg konstaterer bare hullet`

Jeg fant ingen Stripe billing-portal i `backend/`. Månedsplanen er et løpende abonnement
(webhooks for oppsigelse finnes, `server.py:1474-1484`), men jeg fant ingen vei for kunden
selv. Før vi markedsfører månedsplanen tyngre, må spørsmålet «hva om jeg vil slutte?» ha et
sant svar. Anti avgjør hvordan.

---

### FORSLAG G1 — gratisnivået er vår største konkurrent. Ikke kutt det. Flytt grensen.
`FORSLAG — krever Michaels godkjenning og Antis implementering`

**Problemet, regnet ut:** 10 spørsmål per dag (`ACCESS_REGISTERED_DAILY_LIMIT = 10`,
`server.py:178`) i en tremåneders forberedelsesperiode er ca. **900 spørsmål**. Det er nok
til å komme gjennom hele teoripensumet gratis. Vi konkurrerer med oss selv.

**Hva jeg *ikke* foreslår:** å kutte grensen. Målgruppen har dårlig erfaring med systemer som
strammer inn (business-brief pkt. 6), og et kutt vil bli lest som nettopp det. Vi vinner
ingenting på å gjøre gratisnivået dårligere.

**Hva jeg foreslår i stedet:** flytt tyngdepunktet i Premium bort fra *antall spørsmål* og
over på det gratisnivået strukturelt aldri kan gi:

1. Eksamensmodus — 45 spørsmål på rad, som på ekte prøve. Ti spørsmål om dagen kan aldri bli
   det, uansett hvor mange dager du bruker. Er du klar? Det er dette som svarer.
   Allerede premium i koden (`server.py:826`) — vi sier det bare ikke tydelig nok.
2. Forklaringen på thai når du svarer feil (`server.py:827`).
3. Trening på dine egne svake temaer (`server.py:828`).

Dette er en ærlig vegg: gratis gir deg øving, betalt gir deg *prøven* og *forklaringen*.
Ingen kunstig innsnevring.

**Én ting som er verdt å teste `[ANTAKELSE]`:** gjestegrensen på 5 spørsmål totalt
(`ACCESS_GUEST_TOTAL_LIMIT = 5`) er så lav at eleven møter paywallen før hen har opplevd
forklaringen på thai — altså før hen har sett grunnen til å betale. Én mulighet er at de fem
gjestespørsmålene alltid trekkes fra temaene der de norske fagordene er verst (tabell B1 i
`01-market-signals.md`), slik at «å-ha»-øyeblikket kommer innenfor de fem.
**Innholdsvalget er Deeps bord, ikke mitt.** **Måles:** andel gjester som registrerer seg
etter spørsmål 5.

---

## Til agent 3 og 4 — det dere må ta med videre

1. **Aldri «ta teoriprøven på thai».** Prøven finnes ikke på thai [K7]. Bruk
   «Forstå på thai. Kjenn igjen på norsk.»
2. **Aldri lov bestått.**
3. **Gebyret 480 kr er `[UVERIFISERT]`.** Ikke i et manus før Michael har åpnet
   vegvesen.no. Trenger dere et tall før det, bruk kun det som er verifisert i koden:
   249 kr og 699 kr.
4. **Prisen dere kan nevne er 99 / 249 / 699** — det som ligger i produksjonskoden. Ikke 199.
5. **Tremånedersfristen [K12] skal aldri fremstilles som en nedtelling.** Den er en
   opplysning, ikke et pressmiddel.
6. **Tolkeprisen finnes ikke.** Si «du må betale for tolk hver gang du prøver» uten beløp.

---

## Strategic Second Pass

| # | Spørsmål | Score | Begrunnelse |
|---|----------|-------|-------------|
| 1 | Målgruppe spesifikk | 4/5 | Bytt-ut-testen holder: bytt «thai» med «polsk», og både kjerneløftet og T3 kollapser — polske førerkort byttes inn 1:1, og prøven finnes på språk polsktalende kan velge. Tilbudet er bygget på to fakta som *bare* gjelder denne gruppen. Trekk fordi jeg fortsatt ikke kan navngi tre virkelige personer, og ikke har én setning fra et menneske i målgruppen. Det hullet arvet jeg fra agent 1, og jeg kan ikke tette det med et regneark. |
| 2 | Smerten akutt | 4/5 | Tremånedersfristen [K12] er en dato med klokke, og 480 kr per strøket forsøk gjør vondt i lommeboka nå. T3 kobler pakkevalget direkte til fristen. Trekk fordi det mest akutte tallet fortsatt er `[UVERIFISERT]` — jeg bygger regnestykket på en sats ingen av oss har lest hos kilden. |
| 3 | Løftet troverdig | 4/5 | Løftet er avgrenset til noe koden faktisk leverer, hver linje i «Hva kunden får» er sporet til en `is_premium`-flagg i `server.py`, og det farligste løftet i hele prosjektet er fjernet før det nådde et manus. Ingen garantier, ingen superlativer. Trekk fordi tilbudet slik det står **i dag** ikke har noen risikofjerner utover gratisnivået — R2 er et forslag, ikke en realitet — og fordi jeg ikke kan svare kunden på «hvordan sier jeg opp?». |
| 4 | Lead magnet trekker videre | 3/5 | Jeg leverer ikke lead magneten, men jeg leverer broen den skal lede over: fagordene (tabell B1) → eksamensmodus → 3-månederspakken som dekker akkurat fristen. Trekk, og et ærlig et: gratisnivået på 10 spørsmål per dag i 90 dager kan bære hele forberedelsen alene. G1 peker på løsningen, men den er ikke besluttet. Så lenge gratis er godt nok, er veien fra lead magnet til betaling åpen i teorien og treg i praksis. |
| 5 | Tjener penger | 4/5 | Veien til betaling kan tegnes: fagord → gratis øving → eksamensmodus låst → «to strøkne forsøk koster mer enn livstid» → kjøp. Regnestykket er sitert, ikke funnet på, og jeg har vist nøyaktig hvor 199 kr-modellen ryker (10 % konverteringsfall spiser hele gevinsten). Trekk fordi hver eneste fordeling og levetid i ARPU-modellen er `[ANTAKELSE]` — jeg leverer en struktur, ikke en prognose, og jeg vil ikke at den skal leses som noe annet. |
| 6 | Høres interessant ut | 3/5 | «Vi doblet en pris nesten ingen betaler» og «to strøkne forsøk koster mer enn å eie appen for alltid» er linjer jeg ville sendt videre. Men dette er et analysedokument til Michael, ikke salgstekst, og det mangler fortsatt setningen fra et menneske som har strøket. Uten den er tilbudet korrekt og litt kaldt. Agent 3 kan ikke fikse det med bedre ord — det fikses med fem telefonsamtaler. |

**Snitt:** 3,7 — **Svakeste ledd:** #4 og #6

**Hva jeg ville fikset først:**

Snittet er under porten på 4,0, og jeg lar det stå. Å skrive dokumentet om løfter ikke
scoren — fire av seks trekk skyldes ting jeg ikke kan produsere fra denne stolen:

- **#2 og #5** løftes av at Michael åpner `vegvesen.no/forerkort/ta-forerkort/gebyr/` og
  bekrefter 480 kr, og sender to e-poster for å finne tolkeprisen T. Til sammen tjue minutter.
  Med T på plass går regnestykket fra «to stryk koster mer enn livstid» til «hvert eneste
  forsøk koster deg 480 + T», og det er et vesentlig sterkere tilbud.
- **#4** løftes ikke av tekst. Den løftes av at Michael tar stilling til G1: skal Premium
  selges på *antall spørsmål* eller på *eksamensmodus og forklaringen*? Så lenge svaret er
  det første, konkurrerer gratisnivået med betalproduktet vårt hver dag.
- **#1 og #6** løftes av de fem telefonsamtalene agent 1 ba om. Én ordrett setning fra en
  elev som har strøket, plassert øverst i tilbudet, er verdt mer enn resten av dette
  dokumentet for agent 3.
- **#3** løftes av én beslutning: si ja eller nei til R2 (14 dagers pengene tilbake) og
  få et sant svar på «hvordan sier jeg opp?».

Det jeg *ikke* ville gjort først: endret prisen. Vi har ingen konverteringsdata. Endrer vi
pris nå, mister vi muligheten til å vite hva som virket — og 199 kr uten at 249 og 699
flytter seg, gjør månedsplanen til en kulisse.
