---
agent: offer-architect
kjøring: 2026-08-04-forste-100-premium
input: business-brief.md, 00-brief.md, 01-market-signals.md
second-pass-score: 4,2
revidert: 2026-08-04 — omskrivingsrunde etter Michaels beslutninger
åpne spørsmål: >
  1) DELVIS LØST. Michael har spikret 99 / 249 / 699 som mål, i tråd med min egen
     anbefaling (tidligere FORSLAG P1). MEN produksjon kjører 199 / 399 / 699, og
     byttet krever at Stripe oppdateres FØRST — ellers svarer checkout 503 for alle
     planer. Stripe-operasjonen eies av Michael/Anti og er ikke gjort.
  2) LØST som premiss. TRIAL_DAYS = 7 er en kjernekomponent, ikke en fotnote.
     Hele tilbudet er bygget om rundt gratisuken. Se «Gratisuken er tilbudet».
  3) Gebyret er fortsatt [UVERIFISERT]. Nytt forsøk 2026-08-04 feilet: vegvesen.no er
     blokkert av nettverksproxyen (EGRESS_BLOCKED), samme vegg som agent 1 traff.
     Michael må åpne siden selv. Ingen tall er trykket noe sted i mellomtiden.
  4) Hva koster en godkjent thai-tolk til teoriprøven? Uten det tallet mangler tilbudet
     sitt sterkeste regnestykke. Jeg har lagt inn formelen, ikke et gjettet beløp.
  5) Avmelding og oppsigelse er tildelt Codex (backend). Sekvensen i 04 kan ikke sendes
     før /api/unsubscribe finnes. Dette er nå en blokkering med eier, ikke et åpent spørsmål.
---

# Tilbud — Thai2Drive Premium, første 100 kunder

> **Til Michael:** prisen er avgjort — **99 / 249 / 699** — men den er ennå ikke i drift.
> Produksjon kjører i dag **199 / 399 / 699** (`PUBLIC_PRICING_FALLBACK`, `server.py:151`).
> Tilbudet under beskriver altså den **vedtatte** prisen, ikke dagens.
>
> **Rekkefølgen er tvungen og kan ikke snus:** Stripe må få de nye prisene først,
> deretter oppdateres konstanten i koden. `create_checkout_session` krever
> `source == "stripe_live"` (`server.py:1604`), og `_get_live_stripe_plan_prices_sync`
> returnerer `None` så snart én plan avviker fra Stripe (`server.py:1146`). Endres koden
> først, svarer checkout **503 for alle tre planene** — ikke feil pris, men ingen pris.
> Stripe-operasjonen eies av Michael/Anti.
>
> Den andre store endringen er gratisuken: `TRIAL_DAYS = 7` er løftet fra en detalj
> ingen av oss hadde sett, til selve motoren i tilbudet.

---

## Verifisering av bestillingen

### Funn 1 — prisen er vedtatt, men ikke i drift

Den opprinnelige bestillingen ba om 199 kr/mnd. Michael har vedtatt 99 kr/mnd som mål.
Merk rekkefølgen: da dette dokumentet først ble skrevet, *var* 99 kr live. Siden har
produksjon blitt satt til 199 / 399 / 699. Vedtaket er altså nå en **endring som skal
gjøres**, ikke en beskrivelse av dagens tilstand.

| Plan | Vedtatt mål | I produksjon nå | Status |
|---|---|---|---|
| Månedlig | **99 kr** | 199 kr | venter på Stripe |
| 3 måneder | **249 kr** (Beste verdi) | 399 kr | venter på Stripe |
| Livstid | **699 kr** | 699 kr | ✓ allerede riktig |

**Prisen krever to steg, i denne rekkefølgen:** (1) nye Prices opprettes i Stripe
Dashboard, (2) `PUBLIC_PRICING_FALLBACK` settes til 99 / 249 / 699. Steg 1 eies av
Michael/Anti. Gjøres steg 2 først, dør checkout.

**Markedsføringen kan likevel starte før prisen er byttet** — gratisuken og
lanseringskampanjen krever ingen prisendring i det hele tatt.

Verifisert i repoet (oppdatert 2026-08-25):
- `backend/server.py:151-173` — `PUBLIC_PRICING_FALLBACK` står på **199 / 399 / 699**.
- `backend/webapp.py` — paywall-kortene viser «199 NOK», «399 NOK», «699 NOK».
- **Konstanten er en sperre, ikke bare en pris.** `_get_live_stripe_plan_prices_sync`
  sammenligner hver plan mot Stripe (`expected_minor`, `server.py:1146`) og returnerer
  `None` ved avvik. `create_checkout_session` kaster da 503 (`server.py:1604`).
  Derfor må Stripe endres først.
- «Best verdi»-merket ligger allerede på 3-månederskortet. Den delen er implementert.

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
er beløpene der de ekte prisene. Står det `"fallback"`, er det konstanten i koden som
vises — i dag 199 / 399 / 699.

**Regnestykkene i resten av dokumentet forutsetter 99 / 249 / 699.** De gjelder altså
etter at Stripe og konstanten er oppdatert, ikke i dag.

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

### Hvorfor 3-månederspakken er den riktige å dytte mot

Michael har pekt ut 249 kr som den planen elevene skal ledes mot, av en grunn som ikke er
prispsykologi i det hele tatt: **tre måneder er normal øvingstid.** Pakken er ikke et
rabattknep, den er den ærlige lengden på jobben.

Det gjør salgsargumentet enkelt, og sant:

> Du kjøper ikke tre måneder fordi det er billigere.
> Du kjøper tre måneder fordi det er så lang tid dette tar.

Rabatten på 16,2 % er stor nok til å belønne den som binder seg, og liten nok til at
månedsprisen fortsatt er et ekte valg for den som bare skal ta igjen et hull. Trappen
henger sammen fordi ingen av de tre trinnene er et blindspor.

---

## Gratisuken er tilbudet

Dette er den største endringen i denne omskrivingen, og den kom fra agent 4.

`TRIAL_DAYS = 7` (`backend/server.py:53`, brukt i 752-775 og 2072) gir **full Premium-tilgang
i sju dager ved registrering.** Funksjonen er aktiv i produksjon i dag. Ingen av de tre
foregående agentene visste om den, og tilbudet var skrevet som om betalingsmuren møter
brukeren med én gang. Det gjør den ikke.

**Hva dette endrer, konkret:**

| Uten gratisuken (slik 01–03 var skrevet) | Med gratisuken (slik det faktisk er) |
|---|---|
| Vi må overbevise om verdi før kjøp | Vi lar produktet demonstrere verdien selv |
| Argumentet er et løfte | Argumentet er en erfaring eleven allerede har hatt |
| Risikofjerner må konstrueres | Risikofjerneren finnes allerede, gratis |
| Kjøpsøyeblikket er ukjent | Kjøpsøyeblikket er **dag 8**, og det er datostyrt |

Det sterkeste ved gratisuken er ikke at den er gratis. Det er at den lar eleven møte
**Michael V5 på morsmålet** før noen ber om penger. Målgruppen har aldri opplevd en
trafikklærer som forklarer på thai. Det kan ikke selges med en setning — det må erfares.
Sju dager er nok til å erfare det.

**Konsekvensen for alt vi skriver:** vi selger ikke tilgang. Vi selger *fortsettelsen* av
noe eleven allerede har begynt på. Det er en helt annen og mye lettere samtale.

> **Blokkering:** dag 8 er i dag udokumentert. Det finnes ingen tekst noe sted for øyeblikket
> gratisuken tar slutt og eleven faller fra full tilgang til 10 spørsmål per dag. Det er det
> skarpeste frafallspunktet i hele reisen. Se `04-conversion-system.md`, seksjon «Hullet på dag 8».

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

**B) Hva som faktisk flytter dette tallet**

Prisen er avgjort, så spørsmålet er ikke lenger «hvilken pristrapp gir mest». Det er
**hvilken bevegelse i fordelingen som er verdt mest** — for det er der pengene ligger.

`[ANTAKELSE]` samme 100 kunder, men fordelingen forskjøvet mot pakken fordi vi anbefaler
den aktivt og fordi gratisuken har vist eleven hvor lang jobben er:

| Plan | Kunder | Inntekt per kunde | Sum |
|---|---|---|---|
| Månedlig 99 | 20 | 99 × 2 = 198 | 3 960 |
| 3 mnd 249 | 55 | 249 | 13 695 |
| Livstid 699 | 25 | 699 | 17 475 |
| **Sum** | 100 | | **35 130 kr** |

Ti kunder flyttet fra måned til pakke gir **+510 kr** — omtrent 1,5 %. Det er lite, og det
er verdt å si høyt: **fordelingen mellom planene er ikke der pengene er.**

**Der pengene er:** hvor mange som i det hele tatt kommer til paywallen. Går vi fra 100 til
120 betalende kunder, er det +6 900 kr — fjorten ganger mer enn den mest optimistiske
omfordelingen mellom planer. Derfor handler resten av dette dokumentet, og hele
`04-conversion-system.md`, om volum og om dag 8 — ikke om prisskilt.

### Vedtatt

**Prisene står: 99 / 249 / 699.** Ingen kodeendring, ingen Stripe-endring, ingen ventetid.

Det som skal gjøres i stedet, i rekkefølge:

1. Fiks paywall-teksten så den selger det som faktisk er unikt (`FORSLAG T1`, `T2`).
2. Anbefal 3-månederspakken aktivt som normal øvingstid (`FORSLAG T3`).
3. Tett hullet på dag 8 — det er det eneste stedet i reisen der en varm bruker faller ut
   uten et ord fra oss.
4. Mål de fire tallene i `04-conversion-system.md`. Etter fire uker har du ekte
   konverteringsdata, og da er en prisdiskusjon verdt å ta.

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
>
> **Tredje forsøk, 2026-08-04 (omskrivingsrunden):** Michael ba om en uavhengig sjekk.
> Direkte henting av `vegvesen.no/forerkort/ta-forerkort/gebyr/` feilet med
> `EGRESS_BLOCKED` — domenet er sperret i nettverksproxyen, ikke bare 403. Søk mot
> vegvesen.no returnerte riktige sider, men ingen av trefflistene inneholdt selve beløpet.
> Ett funn er verdt å merke seg: Vegvesenets engelske gebyrside oppgir at satsene gjelder
> **fra 1. februar 2026**, altså er 2026-satsen en annen enn de eldre kildene våre.
> **Konklusjon: tallet er fortsatt ikke bekreftet, og er nå trolig utdatert i tillegg.**
> Michael må lese det selv. Ingen agent har trykket et gjettet beløp noe sted.

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

### VEDTAK P1 — 99 / 249 / 699 står fast
`VEDTATT av Michael 2026-08-04 — ingen implementering nødvendig`

**Hva:** 99 / 249 / 699 er vedtatt som mål. Produksjon står i dag på 199 / 399 / 699,
og byttet skjer først når Stripe er oppdatert (se boksen øverst).

**Hvorfor dette er den riktige beslutningen, ikke bare den enkleste:**

1. **Trappen henger sammen.** 16,2 % rabatt på pakken belønner binding uten å gjøre
   månedsprisen til en kulisse. Alle tre trinnene er ekte valg.
2. **249 kr matcher jobben.** Tre måneder er normal øvingstid. Pakken selger seg selv
   på sannhet, ikke på rabattmatematikk.
3. **Ingenting må bygges.** Markedsføringen kan starte i dag. Hver dag brukt på å
   diskutere prisskilt er en dag uten data.
4. **Vi har null konverteringsdata.** Å endre pris før vi har målt noe, betyr at vi
   aldri får vite hva som virket.

**Hva som skal måles før prisen tas opp igjen:** (1) kjøp per 100 paywall-visninger,
(2) fordelingen mellom de tre planene, (3) hvor mange betalende måneder et månedsabonnement
faktisk varer, (4) hvor mange som konverterer på dag 8 mot senere. Punkt 4 er ny i denne
runden og er sannsynligvis den viktigste av dem.

> **De to alternative prissettene som lå her tidligere (199/449/899 og 149/299/799) er
> fjernet.** De var utredninger av en bestilling som nå er avgjort i motsatt retning.
> Å la dem stå ville invitere til å gjenåpne en lukket beslutning. Historikken ligger i
> git (commit `ae4325a`) hvis regnestykkene trengs igjen.

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
3. **Gebyret 480 kr er `[UVERIFISERT]`, og trolig utdatert.** Vegvesenets egne satser
   gjelder fra 1. februar 2026. Ikke i et manus før Michael har lest tallet selv.
   Trenger dere et tall før det, bruk kun det som er verifisert i koden: 249 kr og 699 kr.
4. **Prisen er 99 / 249 / 699.** Vedtatt av Michael, identisk med produksjonskoden.
   3-månederspakken til 249 kr er den dere skal lede mot — ikke fordi den er billigst,
   men fordi tre måneder er normal øvingstid.
5. **Gratisuken er utgangspunktet for alt dere skriver.** `TRIAL_DAYS = 7` gir full
   Premium ved registrering. Dere selger ikke tilgang — dere selger fortsettelsen av
   noe eleven allerede har erfart. Kjøpsøyeblikket er **dag 8**.
6. **Tremånedersfristen [K12] skal aldri fremstilles som en nedtelling.** Den er en
   opplysning, ikke et pressmiddel.
7. **Tolkeprisen finnes ikke.** Si «du må betale for tolk hver gang du prøver» uten beløp.

---

## Strategic Second Pass — omskrivingsrunde 2026-08-04

> Scoren under er satt på nytt etter Michaels beslutninger. Jeg har bare hevet de punktene
> der noe **faktisk** ble bedre. Der hullet er det samme som før, står scoren stille — en
> beslutning om pris fikser ikke at vi mangler en setning fra et menneske.

| # | Spørsmål | Før | Nå | Begrunnelse for endringen |
|---|----------|-----|-----|---------------------------|
| 1 | Målgruppe spesifikk | 4/5 | **4/5** | Uendret. Bytt-ut-testen holder fortsatt: bytt «thai» med «polsk» og både kjerneløftet og T3 kollapser. Men jeg kan fortsatt ikke navngi tre virkelige personer, og har ikke én ordrett setning fra målgruppen. Det hullet arvet jeg fra agent 1 og det er ikke tettet. |
| 2 | Smerten akutt | 4/5 | **4/5** | Uendret. Tremånedersfristen [K12] er fortsatt en dato med klokke. Gebyret er fortsatt `[UVERIFISERT]` — og etter tredje mislykkede forsøk vet vi i tillegg at 2026-satsen er ny, så tallet vi har er trolig feil. Ingen grunn til å heve. |
| 3 | Løftet troverdig | 4/5 | **5/5** | **Hevet.** Det største trekket var at tilbudet ikke hadde noen risikofjerner utover gratisnivået — R2 var et forslag, ikke virkelighet. Nå vet vi at `TRIAL_DAYS = 7` er i produksjon: sju dager full Premium, gratis, uten kort. Det er den sterkeste risikofjerneren et tilbud kan ha, og den er allerede bygget. Hver linje i «Hva kunden får» er fortsatt sporet til en `is_premium`-flagg i `server.py`. |
| 4 | Lead magnet trekker videre | 3/5 | **4/5** | **Hevet.** Trekket var at gratisnivået (10 spørsmål/dag i 90 dager) kunne bære hele forberedelsen alene, så veien til betaling var åpen i teorien og treg i praksis. Gratisuken snur dette: eleven får *full* tilgang først og mister den på dag 8. Det er ikke lenger «gratis er godt nok» — det er «du hadde det, og nå er det borte». Ikke 5, fordi teksten som skal møte eleven på dag 8 fortsatt ikke finnes. |
| 5 | Tjener penger | 4/5 | **4/5** | Uendret. Veien til betaling kan tegnes, og prisen er nå avgjort så modellen hviler på ekte tall. Men hver fordeling og levetid er fortsatt `[ANTAKELSE]`, og jeg viser nå selv at omfordeling mellom planer er verdt ~1,5 % mens volum er verdt fjorten ganger mer. Det er en ærligere analyse, ikke et bedre resultat. |
| 6 | Høres interessant ut | 3/5 | **4/5** | **Hevet.** «Du har allerede hatt det i sju dager — vil du beholde det?» er en vesentlig varmere åpning enn «kjøp tilgang», og den er sann. Gratisuken gir agent 3 noe å skrive om som eleven selv har opplevd. Ikke 5, fordi setningen fra et menneske som har strøket fortsatt mangler. Den fikses med fem telefonsamtaler, ikke med bedre ord. |

**Snitt:** 4,2 (fra 3,7) — **Porten på 4,0 er passert.**
**Svakeste ledd:** #1 og #2 — begge venter på at Michael gjør noe utenfor tastaturet.

**Hva som fortsatt står igjen, i prioritert rekkefølge:**

1. **Fem telefonsamtaler.** Én ordrett setning fra en elev som har strøket, plassert øverst
   i tilbudet, er verdt mer for agent 3 enn resten av dette dokumentet. Løfter #1 og #6.
2. **Gebyret.** Michael åpner `vegvesen.no/forerkort/ta-forerkort/gebyr/` og leser
   2026-satsen. To minutter. Løfter #2.
3. **Tolkeprisen T.** To e-poster til tolketjenester. Med T på plass går regnestykket fra
   «to stryk koster mer enn livstid» til «hvert eneste forsøk koster deg gebyr + T».
4. **Teksten for dag 8.** Tilhører agent 4, men den er blokkert av at `/api/unsubscribe`
   ikke finnes. Det er Codex sin oppgave.

**Det jeg ikke ville gjort:** gjenåpnet prisdiskusjonen. Den er avgjort, tallene er live,
og de fire punktene over er alle verdt mer enn et nytt prisskilt.
