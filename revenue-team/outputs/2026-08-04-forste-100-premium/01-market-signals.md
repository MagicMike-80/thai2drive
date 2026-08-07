---
agent: market-signal-researcher
kjøring: 2026-08-04-forste-100-premium
input: business-brief.md, 00-brief.md
second-pass-score: 3,8
åpne spørsmål: >
  1) Ingen førstepersonssitater fra thaitalende elever funnet — se «Hva jeg IKKE fant».
  2) Gebyret for teoriprøven oppgis ulikt i tre kilder (480 / 680 / 350 kr). Må verifiseres
     på vegvesen.no før agent 2 bruker det i et regnestykke.
  3) Er teoriprøven virkelig ikke tilgjengelig på thai? Sterk indikasjon, ikke bekreftet
     mot Vegvesenets egen side (den svarte 403 på alle forsøk).
---

# Markedssignaler — thaitalende voksne i Norge, teoriprøven klasse B

> **Les dette først:** Denne kjøringen har to leveranser. Del A er spørringen Michael
> selv må kjøre, fordi produksjonsdatabasen ikke er tilgjengelig herfra (blokkering B1
> i `00-brief.md`). Del B er markedsresearchen. Ingen tall i dette dokumentet er
> funnet på av meg. Der jeg mangler kilde, står det `[ANTAKELSE]` eller
> `[UVERIFISERT]`.

---

## Sammendrag (5 punkter)

1. **Teoriprøven finnes ikke på thai.** Klasse B tilbys digitalt på bokmål, nynorsk,
   nordsamisk, engelsk, arabisk (MSA), sorani og tyrkisk. Vil du ha thai, må du søke om
   *tilrettelagt teoriprøve med tolk*, bestille tolken selv og betale for den selv.
   [K7][K8][K9] Dette er den viktigste enkeltopplysningen i hele dokumentet, og den har
   direkte konsekvens for hva Thai2Drive kan love. Se advarselen til agent 3.

2. **Thailandsk førerkort kan ikke byttes inn.** Norge har innbytteavtale med et
   begrenset sett land utenfor EU/EØS (Australia, Canada, Israel, Japan, Monaco,
   New Zealand, San Marino, Sør-Korea, Sveits, Storbritannia, USA m.fl.). Thailand er
   ikke blant dem. [K10][K11][K12] En thailandsk sjåfør med 20 års erfaring bak rattet
   må altså gjennom hele det norske løpet — inkludert teoriprøven — etter tre måneder
   i landet. Det er en helt annen følelse enn «jeg skal ta lappen».

3. **Veggen er fagordene, ikke trafikkreglene.** Forskning fra Høgskolen i Nord-Trøndelag
   peker på nøyaktig hvilke ord som stopper fremmedspråklige elever: *aktsomhet,
   bremseberedskap, fartstilpassing, fletteregel, forkjørskryss.* Norske elever forstår
   dem intuitivt fra kontekst; andre gjør det ikke, og kommunikasjonen mellom lærer og
   elev blir overfladisk. [K13] Dette er hele forretningsideen til Thai2Drive, bekreftet
   av en uavhengig kilde.

4. **Vikeplikt-antakelsen i `00-brief.md` får støtte — men fra andrehåndskilder.**
   Flere norske bransjenettsteder skriver at vikeplikt og forkjørsrett er det temaet flest
   svarer feil på, og at ukontrollerte kryss og rundkjøringer er de vanskeligste
   situasjonene. De oppgir Statens vegvesen som kilde, men jeg fikk ikke verifisert det
   mot Vegvesenet direkte. [K14][K15] Antakelsen bør fortsatt stå merket `[ANTAKELSE]`.

5. **Jeg fant ingen ordrette sitater fra målgruppen.** Ikke ett. Se egen seksjon om hvorfor.
   Dette er kjøringens svakeste ledd, og det kan ikke fikses ved å skrive dokumentet om.
   Det fikses ved at Michael spør fem elever. Jeg har lagt ved spørsmålene han bør stille.

---

# DEL A — spørringen Michael kan kjøre selv

## A1. Hva den eksisterende koden gjør

I `backend/server.py:1735-1781` ligger endepunktet `/stats/me`. Det regner ut
treffprosent per kategori — men bare for **én enkelt bruker**, fordi det første steget
filtrerer på `device_id`. Alt annet i pipelinen er allerede riktig. Vi trenger bare å
fjerne det ene filteret.

## A2. Spørringen — kjør denne (mongosh / Atlas / Compass)

Gi denne til Anti, eller kjør den selv i MongoDB Atlas under «Collections →
quiz_attempts → Aggregation».

```js
db.quiz_attempts.aggregate([

  // Steg 1 — plukk ut hvilke forsøk som skal telle med.
  // Vi tar med ALLE elever (ingen filtrering på device_id), men hopper over
  // forsøk uten spørsmål og forsøk der kategorien mangler.
  { $match: {
      total_questions: { $gt: 0 },
      category: { $nin: [null, "", "None"] }
  }},

  // Steg 2 — legg alle forsøk i samme kategori i én bunke og summer.
  { $group: {
      _id:          "$category",
      elever:       { $addToSet: { $ifNull: ["$user_id", "$device_id"] } },
      forsok:       { $sum: 1 },
      sum_sporsmal: { $sum: "$total_questions" },
      sum_riktige:  { $sum: "$correct_answers" }
  }},

  // Steg 3 — regn ut prosenten og gi kolonnene norske navn.
  { $project: {
      _id: 0,
      kategori:      "$_id",
      antall_elever: { $size: "$elever" },
      forsok:        1,
      sum_sporsmal:  1,
      sum_riktige:   1,
      treffprosent:  { $round: [
          { $multiply: [ { $divide: ["$sum_riktige", "$sum_sporsmal"] }, 100 ] }, 1
      ]}
  }},

  // Steg 4 — kast kategorier med for lite data til å si noe.
  // Juster tallet 20 opp eller ned etter hvor mye data dere faktisk har.
  { $match: { forsok: { $gte: 20 } } },

  // Steg 5 — verst først.
  { $sort: { treffprosent: 1 } }
])
```

**Hva hvert steg gjør, i klartekst:**

| Steg | På norsk |
|------|----------|
| 1 | «Ta med alle quiz-runder som faktisk hadde spørsmål i seg, og som vet hvilket tema de handlet om.» |
| 2 | «Legg alle rundene om vikeplikt i én haug, alle om skilt i en annen, og tell opp.» |
| 3 | «Regn ut: hvor stor andel av svarene i haugen var riktige?» |
| 4 | «Ikke la en kategori med tre forsøk se ut som en katastrofe. Krev minst 20 runder.» |
| 5 | «Sorter slik at kategorien elevene sliter mest med står øverst.» |

Skal Anti kjøre den fra Python i stedet, er det nøyaktig samme liste sendt til
`db.quiz_attempts.aggregate(...)` i PyMongo. Ingen endring nødvendig.

## A3. Den viktige nyansen: treffprosent ≠ strykprosent

Dette må Michael forstå før tallet brukes til noe.

`quiz_attempts` lagrer **én rad per fullført øvingsrunde**, ikke én rad per spørsmål.
Hver rad sier «denne runden hadde 20 spørsmål, 13 var riktige». Legger vi sammen alle
rundene i en kategori, får vi:

> **Treffprosent** = hvor stor andel av svarene elevene gir riktig *når de øver på dette
> temaet i appen*.

Det er **ikke**:

- **Strykprosent per spørsmål.** Vi vet ikke hvilke enkeltspørsmål som går galt, bare
  hvor mange i runden som gjorde det. (Det finnes en vei rundt — se A5.)
- **Strykprosent på den ekte teoriprøven.** Vi har ingen data om hvordan elevene gjør det
  hos Statens vegvesen. Ingen. Det tallet kan ikke hentes fra denne databasen i det hele tatt.

Og det er en skjevhet til, som er lett å gå på: **kategorien er den eleven selv valgte.**
Et lavt tall kan bety «temaet er vanskelig» — eller «temaet er det folk øver på først, før
de kan noe som helst». Elever som sliter, gjentar samme kategori mange ganger, og drar
snittet ned ekstra. Tallet er en god pekepinn på hvor det gjør vondt. Det er ikke et bevis.

## A4. Datakvalitet — les dette før du tror på tallet

**Problem 1: kategorinavnene er ikke ryddet.** I innholdet som er seedet finnes minst disse
skrivemåtene om hverandre: `Right of Way`, `Vikeplikt`, `Traffic Signs`, `Road Rules`,
`Traffic Rules`, `Speed Limits`, `Situations`, `Mechanics`. Verifisert i repoet:
`backend/server.py` bruker `"Right of Way"`, mens `backend/scripts/seed_vikeplikt_questions.py`
bruker `"Vikeplikt"` — **to navn for samme tema**. Aggregeringen over vil vise dem som to
separate rader, hver med halve datagrunnlaget. Vikeplikt kan altså se mindre alvorlig ut
enn det er, rett og slett fordi temaet er delt i to.

**Problem 2: mange forsøk mangler kategori helt.** `$nin`-filteret på `[None, "", "None"]`
ligger allerede i produksjonskoden — det står der fordi noe skriver tomme kategorier.
Kilden er funnet: i webappen settes `category: currentCat ? currentCat.name : null`
(`backend/webapp.py:8194`). I **eksamensmodus** finnes det ingen valgt kategori, så
**alle eksamensforsøk lagres uten kategori** og faller ut av spørringen. Det er sannsynligvis
den mest realistiske øvingsformen som forsvinner ut av statistikken.

Kjør disse tre først, så vet du hvor mye du kaster:

```js
db.quiz_attempts.countDocuments({})                                        // alt
db.quiz_attempts.countDocuments({ category: { $in: [null, "", "None"] } }) // uten kategori
db.quiz_attempts.distinct("category")                                      // se navnerotet
```

Er andelen uten kategori stor, er svaret ikke «juster spørringen» — det er «rydd i
kategorinavnene og få eksamensmodus til å tagge riktig». Det er Antis bord, og det er et
**forslag**, ikke en bestilling.

**Konsekvens for pålitelighet, sagt rett ut:** med to navn for vikeplikt og alle
eksamensforsøk uten kategori, er rangeringen fra denne spørringen en *indikasjon*.
Er avstanden mellom verste og nest verste kategori under ca. 5 prosentpoeng, ville jeg
ikke bygget en kampanje på forskjellen.

## A5. Bonus — den bedre spørringen, hvis dere vil ha det per spørsmål

Hvert forsøk lagrer også `questions_answered` — en liste med `question_id`,
`user_answer`, `correct_answer` og `is_correct` per spørsmål. Kobler vi den mot
`db.questions` (som har `category` på hvert spørsmål), får vi kategori også for
eksamensforsøkene, og vi får treffprosent per faktisk spørsmål.

```js
db.quiz_attempts.aggregate([

  // Pakk ut ett spørsmål per rad.
  { $unwind: "$questions_answered" },

  // Hopp over rader uten registrert svar. Webappen skriver av og til bare
  // question_id uten svar (backend/webapp.py:8199-8201) — de ville ellers
  // blitt talt som feil, og gjort tallet kunstig dårlig.
  { $match: { "questions_answered.user_answer": { $exists: true } } },

  // Slå opp hvilket tema spørsmålet hører til.
  { $lookup: {
      from: "questions",
      localField: "questions_answered.question_id",
      foreignField: "id",
      as: "q"
  }},
  { $unwind: "$q" },

  { $group: {
      _id: "$q.category",
      besvart: { $sum: 1 },
      riktige: { $sum: { $cond: [
          { $eq: [
              { $toUpper: "$questions_answered.user_answer" },
              { $toUpper: "$questions_answered.correct_answer" }
          ]}, 1, 0
      ]}}
  }},
  { $project: {
      _id: 0, kategori: "$_id", besvart: 1, riktige: 1,
      treffprosent: { $round: [
          { $multiply: [ { $divide: ["$riktige", "$besvart"] }, 100 ] }, 1
      ]}
  }},
  { $match: { besvart: { $gte: 50 } } },
  { $sort: { treffprosent: 1 } }
])
```

Samme sammenlikningslogikk (`$toUpper` på begge sider) brukes allerede i produksjon i
`backend/server.py:923-926`, så dette er ikke en ny måte å regne på.

**Kontroll å kjøre etterpå:** hvis `$lookup` ikke finner treff, forsvinner raden i stillhet.
Bytt ut `{ $unwind: "$q" }` med `{ $match: { q: { $size: 0 } } }` og tell — det viser hvor
mange spørsmåls-ID-er som ikke lar seg koble. Er tallet høyt, er ID-formatene ute av synk,
og resultatet over kan ikke brukes.

**Hvilken skal Michael stole på?** A5, hvis koblingen treffer. Den tar med eksamensforsøkene.
A2 er raskere og trygg å kjøre, men ser bare på temaøving.

---

# DEL B — markedsresearchen

## De 3 sterkeste smertene

### Smerte 1 — «Jeg kan reglene på thai. Jeg får bare ikke sagt det på norsk.»

**Hva den er:** Prøven finnes ikke på thai. Klasse B tilbys digitalt på bokmål, nynorsk,
nordsamisk, engelsk, arabisk (MSA), sorani og tyrkisk. [K7] Vil du ta den på thai, må du
søke om tilrettelagt prøve med tolk, og **du må selv bestille og betale tolken**. [K8][K9]
Tolken må i tillegg være godkjent av Statens vegvesen for teoriprøve og tilknyttet et
byrå som kan skjermtolking. [K16]

**Hvor akutt:** Akutt, og den bygger seg opp over uker. Du kan ikke øve deg ut av det på
prøvedagen. Enten mestrer du de norske ordene, eller så må du kjøpe deg tolk — hver eneste
gang du prøver.

**Belegg (ikke sitater — se ærlighetsseksjonen):**
- Statens vegvesen tilbyr «tilrettelagt teoriprøve» i to varianter: muntlig med sensor på
  eget rom, eller med tolk for språk som ikke finnes digitalt. [K7][K8]
- Det finnes et helt lite marked av thai-tolker som spesialiserer seg på nettopp
  teoriprøve i Norge. [K17][K18] Et slikt marked oppstår ikke uten et vedvarende problem.
- En norsk-thailandsk avis har dekket temaet under overskriften «Tolk på norsk teoriprøve»,
  og omtaler retten til å bruke tolk over internett som det som «kan forenkle» prosessen
  for thaier. [K19] *(Jeg fikk ikke lastet selve artikkelen — 403. Innholdet er gjengitt
  via søkeresultat, ikke lest direkte. `[UVERIFISERT]`.)*

> **Advarsel til agent 3 og 4, viktig:** Dette betyr at Thai2Drive **ikke** kan formuleres
> som «ta teoriprøven på thai». Prøven er ikke på thai. Løftet må være at du *forstår* på
> thai og *kjenner igjen* de norske ordene når de kommer. Sier vi noe annet, brister det i
> det sekundet eleven møter opp på trafikkstasjonen — og da har vi mistet mer enn en kunde.
> Dette er samme feilen som blokkering B3 i `00-brief.md`, bare dyrere.

### Smerte 2 — «Jeg har kjørt i tjue år. Her får jeg ikke lov.»

**Hva den er:** Thailand står ikke på listen over land Norge har innbytteavtale med.
Innbytte uten ny prøve gjelder EU/EØS, og utenfor det er listen kort — Australia, Canada,
Israel, Japan, Monaco, New Zealand, San Marino, Sør-Korea, Sveits, Storbritannia, USA. [K10][K11]
Utenlandsk førerkort utenfor EØS kan normalt brukes i **tre måneder** etter at du har
flyttet til Norge. [K12] Etter det: hele løpet på nytt, teoriprøven inkludert.

**Hvor akutt:** Det er en dato. Tre måneder. Det er den mest akutte smerten i hele
dokumentet, fordi den har en klokke på seg.

**Hvorfor dette er thai-spesifikt og ikke generisk:** Bytt ut «thai» med «polsk», som
strategic-second-pass krever. Det faller sammen umiddelbart — et polsk førerkort byttes
inn 1:1 uten ny prøve. En polsktalende i Norge har ikke dette problemet i det hele tatt.
En thaitalende har det alltid.

**Belegg:**
- «Norske myndigheter godtar ikke lenger innbytte av thailandske sertifikater» —
  omtalt av norsk-thailandsk presse. [K19] `[UVERIFISERT]` — gjengitt via søkeresultat.
- Vegvesenets egne sider om innbytte fra land utenfor EU/EØS bekrefter at land uten avtale
  må vurderes særskilt og at hele opplæringen kan måtte tas på nytt. [K10][K11]

### Smerte 3 — «Det er ikke reglene jeg ikke skjønner. Det er ordene.»

**Hva den er:** Vokabularet i teoriboka, ikke trafikkforståelsen. Forskning fra Høgskolen
i Nord-Trøndelag lot trafikklærerstudenter undervise fire grupper fremmedspråklige elever
og én norsk kontrollgruppe. Konklusjonen var at problemet i stor grad ligger i at elevene
ikke forstår trafikkfaglige uttrykk. [K13]

**Hvor akutt:** Kronisk, ikke akutt — men det er den som får folk til å slutte. Man gir
ikke opp fordi vikeplikt er vanskelig. Man gir opp fordi man har lest samme setning fem
ganger og fortsatt ikke vet hva den betyr.

**Belegg — dette er de faktiske ordene forskningen navngir:**
> «Ord som *aktsomhet*, *bremseberedskap*, *fartstilpassing*, *fletteregel* og
> *forkjørskryss*, som norske elever intuitivt forstår ut fra kontekst og tidligere
> erfaring, gir ikke mening for elever som ikke har norsk som morsmål.» [K13]
> *(Gjengitt fra søkesammendrag av artikkelen — jeg fikk ikke lastet siden direkte.
> `[UVERIFISERT SITAT]` — Michael må lese originalen før dette siteres utad.)*

Samme kilde: kommunikasjonen mellom lærer og elev blir overfladisk, og undervisningen blir
reaktiv — læreren rekker ikke forberede eleven på det som kommer, men må forklare i
etterkant. Det er en presis beskrivelse av hvorfor kjøretimer blir dyre uten å bli bedre.

Kilden er fra 2007. Den er gammel. Men den er den mest presise beskrivelsen jeg fant av
akkurat det problemet Thai2Drive er bygget for, og den kommer fra trafikkopplæringsfaget
selv — ikke fra en app som skal selge noe.

---

## Kundens egne ord

> **Les advarselen i toppen av denne tabellen før du bruker den.** Jeg klarte **ikke** å
> hente inn ordrette utsagn fra thaitalende elever (se «Hva jeg IKKE fant»). Kolonnen
> «Ordet de møter» er derimot dokumentert — det er de faktiske norske fagordene som er
> identifisert som barrieren. [K13] Bruk dem. Ikke dikt opp elevsitater rundt dem.

### B1. Norske ord som stopper eleven — og hva vi sier i stedet

| Ordet de møter i teoriboka | Hva det faktisk betyr (7-årsregelen) | Marketing-ordet vi IKKE bruker |
|---|---|---|
| aktsomhet | «se deg for, og vær klar til å bremse» | «trafikal kompetanse» |
| bremseberedskap | «foten hviler over bremsen, klar» | «proaktiv kjøreatferd» |
| fartstilpassing | «kjør så sakte at du rekker å stoppe» | «situasjonstilpasset hastighet» |
| fletteregel | «annenhver bil får kjøre» | «samspillsregler ved fletting» |
| forkjørskryss | «her har du lov å kjøre først» | «prioritert vegkryss» |
| vikeplikt | «du må vente. Den andre kjører først.» | «vikepliktsregulering» |
| høyreregelen | «bilen fra høyre kjører først» | «grunnleggende vikepliktsprinsipp» |

Dette er hele produktet i én tabell. Venstre kolonne er hvorfor de stryker. Midtkolonnen
er hva Thai2Drive gjør. Høyre kolonne er språket vi aldri skal bruke, uansett hvor
profesjonelt det ser ut.

### B2. Ord som skal ut av all markedsføring

| Ikke skriv | Fordi | Skriv heller |
|---|---|---|
| «Ta teoriprøven på thai» | Prøven finnes ikke på thai. [K7] Løftet brister på prøvedagen. | «Forstå på thai. Kjenn igjen på norsk.» |
| «AI-drevet læring» | Brief punkt 6. AI er hvordan, ikke hvorfor. | «Michael forklarer, på thai» |
| «Bestå garantert» | Vi kontrollerer ikke prøven. Hard grense. | «Slutt å gjette på ordene» |
| «Optimalisert læringsløp» | Sjuåringstesten. | «Ett tema om gangen» |
| «Du stryker fordi …» | Skammebasert. Målgruppen skammer seg nok. [brief punkt 6] | «Det er ikke deg. Det er ordet.» |

### B3. Thai-ordliste — MÅ valideres av Michael før bruk

`[IKKE INNSAMLET — DETTE ER OVERSETTELSE, IKKE KUNDESPRÅK]`

Jeg har ikke hørt målgruppen si disse ordene. Dette er standard thai-vokabular for
begrepene, ikke uttrykk jeg har observert i bruk. Michael er thaifødt trafikklærer — han
kan bekrefte eller forkaste hvert enkelt på to minutter, og det er raskere enn at jeg
gjetter videre. Særlig usikkert: om målgruppen faktisk sier `การให้ทาง` eller bare bruker
låneordet *vikeplikt* på norsk midt i en thai-setning. Låneord er svært vanlig i
diasporaspråk, og hvis de sier «vikeplikt» på norsk, **skal manuset gjøre det samme**.

| Begrep | Thai (til validering) |
|---|---|
| førerkort | ใบขับขี่ |
| teoriprøven | สอบทฤษฎี / *teoriprøve* som låneord |
| stryke på prøven | สอบตก |
| bestå | สอบผ่าน |
| vikeplikt | การให้ทาง |
| høyreregelen | กฎให้ทางด้านขวา |
| rundkjøring | วงเวียน |
| kryss | ทางแยก |
| trafikkskilt | ป้ายจราจร |
| kjøretime | ชั่วโมงเรียนขับรถ |
| tolk | ล่าม |
| prøvegebyr | ค่าธรรมเนียมสอบ |

**Til agent 3:** ikke bygg manus rundt B3 før Michael har krysset av. Bygg rundt B1 og B2 —
de er dokumentert.

---

## Tallene agent 2 skal regne med

> **Advarsel:** kildene spriker på gebyret for teoriprøven. Jeg fikk **403 Forbidden** på
> alle forsøk på å hente vegvesen.no direkte, så ingen av disse tallene er lest av meg på
> Vegvesenets egen side. Michael eller Anti må åpne
> `vegvesen.no/forerkort/ta-forerkort/gebyr/` og bekrefte før tallet trykkes noe sted.

| Post | Beløp | Kilde | Sikkerhet |
|---|---|---|---|
| Teoriprøve klasse B, per forsøk | **480 kr** (fra 1. feb. 2026) | [K1][K2][K3] | Tre uavhengige norske nettsteder, samme tall og samme dato. **Ikke** verifisert mot Vegvesenet. |
| — samme post, avvikende oppgave | 680 kr (2024) | [K20] | Eldre år. Kan være utgått sats. |
| — samme post, avvikende oppgave | 350 kr «ved betaling på trafikkstasjonen» | [K21] | Passer ikke med de andre. **Ikke bruk.** |
| Praktisk førerprøve klasse B | 1 540 kr | [K1][K2] | Samme forbehold. |
| Utstedelse av førerkort | 160–270 kr | [K2] | Intervall, ikke fast sats. |
| Foto | 100 kr | [K2] | |
| Kjøretime klasse B | 600–850 kr, typisk snitt ca. 750 kr | [K4][K5] | Bransjenettsteder, ikke offisiell statistikk. Behandle som `[ANTAKELSE]` om snittet. |

**Prøvens form (nyttig for manus):** 45 spørsmål, minst 38 riktige for å bestå (maks 7 feil),
90 minutter. [K6][K22]

**Nasjonal strykstatistikk:**
- 2025, personbil: 137 772 avlagte teoriprøver, 55 747 strøk — ca. 40 %. [K23]
- 2024, alle klasser: 218 460 prøver, 57 % bestått. Over 90 000 med strykkarakter. [K24]
- Til sammenlikning: 78 % består den praktiske oppkjøringen. [K24] Teorien siler, ikke kjøringen.

**Regnestykket agent 2 bør bygge på — én linje:**
Ett strøket forsøk koster 480 kr i gebyr. Livstidslisensen koster 699 kr. To strøkne
forsøk (960 kr) er allerede dyrere enn livstid. Det er hele argumentet, og det trenger
ingen pynt.

**Ikke tatt med, fordi jeg ikke fant pris:** hva en godkjent thai-tolk til teoriprøven
faktisk koster. Tolkebyråene oppgir at prisen sendes deg først etter at tolk er funnet.
[K9][K25] Finner Michael denne prisen, blir regnestykket vesentlig sterkere — for da er
alternativet til Thai2Drive ikke 480 kr, men 480 kr *pluss tolk, per forsøk*.

---

## Hva de har prøvd før, og hvorfor det feilet

Dokumentert:

1. **Norske teoriapper på engelsk.** Løser ikke problemet — det bytter bare ett fremmedspråk
   mot et annet. Norske brukere klager dessuten på kvaliteten i seg selv: anmeldelser av
   norske teoriapper omtaler «mye feilskriving og dårlig formulerte spørsmål» og at «samme
   svaralternativ kommer flere ganger, hvor det ene er riktig og det andre er feil». [K26]
   `[UVERIFISERT SITAT]` — gjengitt via søkesammendrag av App Store-anmeldelser, ikke lest
   direkte. Er dette forvirrende for en nordmann, er det uframkommelig for en som leser på
   sitt tredjespråk.

2. **Ordlistebøker.** Norges Trafikkskoleforbunds bok «I trafikken» oversetter viktige
   trafikkfaglige uttrykk til 15 språk, thai inkludert. Men forbundet skriver selv at boka
   ikke dekker alt du trenger til prøvene, og at du fortsatt må lære teorien. [K22]
   Altså: ordboka løser ordproblemet, men ikke forståelsesproblemet. Det er nøyaktig gapet
   Thai2Drive sitter i.

3. **Tolk på prøven.** Fungerer, men er dyrt per forsøk, krever egen søknad om tilrettelagt
   prøve *før* tolken kan bestilles, og eleven må selv finne og betale tolken. [K8][K9]
   Det hjelper deg gjennom prøven. Det lærer deg ikke faget.

4. **Kjøreskole med kjøretimer først.** Timer kjøpt før teorien er bestått står ubrukt.
   Forskningen beskriver mekanismen: når eleven ikke forstår språket, blir undervisningen
   reaktiv i stedet for forberedende — læreren forklarer i etterkant i stedet for i forkant. [K13]
   Du betaler 600–850 kr timen for en samtale som ikke fester seg.

**Ikke dokumentert, men verdt å teste:** at mange sitter med YouTube-videoer på norsk med
undertekster. Jeg fant ikke belegg. `[ANTAKELSE]`

---

## Hvor de leter etter hjelp

**Bekreftet at det finnes:**
- **Thai-tolketjenester spesialisert på teoriprøven.** Minst to norske aktører markedsfører
  seg mot akkurat dette, én av dem med thai/norsk-kompetanse og lang erfaring fra
  Statens vegvesen. [K17][K18] At noen har bygget en levevei på dette, er i seg selv det
  sterkeste markedsbeviset i dokumentet.
- **Norsk-thailandsk presse.** Thailands Tidende dekker førerkortspørsmål for
  målgruppen. [K19] En reell distribusjonskanal — ingen andre teoriapper er der.
- **Flerspråklige trafikkskoler.** Finnes i Oslo, men på engelsk, farsi, dari, spansk.
  Jeg fant **ingen** trafikkskole som annonserer undervisning på thai. [K27]
  Det er et hull, ikke en konkurrent.

**Ikke bekreftet:**
- **Facebook-grupper.** Jeg er overbevist om at de er den viktigste kanalen, men jeg kan
  ikke dokumentere det herfra. Gruppene er lukkede og ikke indeksert i søk.
  `[ANTAKELSE]` — se neste seksjon.
- **TikTok/YouTube på thai om norsk teori.** Fant ingen. Enten finnes det ikke, eller så
  når søkeverktøyet mitt ikke inn. Finnes det ikke, er det en åpen kanal for Michael.

---

## Hva jeg IKKE fant

Dette er den viktigste seksjonen i dokumentet. Les den før du bruker resten.

**1. Ikke ett eneste ordrett sitat fra en thaitalende elev i Norge.** Ikke fra Facebook,
ikke fra YouTube-kommentarer, ikke fra forum. Jeg søkte på thai i ti ulike varianter
(`ใบขับขี่ นอร์เวย์`, `สอบเทโอรี`, `สอบทฤษฎี นอร์เวย์`, `คนไทยในนอร์เวย์ ใบขับขี่` m.fl.).
Søkemotoren returnerte gjennomgående thailandske innenlandssider om thailandsk førerkort —
den indekserer ikke thai-i-Norge-innhold. Facebook-gruppene er lukkede.

**2. Jeg fikk ikke lastet en eneste kildeside direkte.** Alle `WebFetch`-forsøk ga
**403 Forbidden** — vegvesen.no, forskning.no, thailandstidende.com, teoritolk.no, samtlige.
Alt jeg har, er via søkesammendrag. Det betyr:
- Sitater merket `[UVERIFISERT SITAT]` er **gjengitt gjennom et mellomledd**. Jeg har ikke
  sett dem med egne øyne på originalsiden. Ingen av dem skal ut i en annonse før noen har
  åpnet lenken og lest setningen selv.
- Gebyrsatsene er andrehånds. De spriker. Se advarselen over.

**3. Ingen bekreftelse på segmentstørrelsen.** Business-briefen ba om «hvor mange
thaitalende i Norge som skal ta teoriprøven». Jeg fant ikke SSB-tall brutt ned på dette,
og jeg nekter å gjette. Ingen tall er bedre enn et tall Michael siterer videre i god tro.

**4. Ingen bekreftelse på at vikeplikt er verst *for denne gruppen*.** Vikeplikt ser ut til
å være verst for alle. [K14][K15] Om det er ekstra ille for thaitalende — eller om skilt
og fagordforråd er verre — vet jeg ikke. Antakelsen i `00-brief.md` er ikke svekket, men
den er heller ikke bekreftet med et tall. Spørringen i Del A er den som avgjør det.

### Slik tetter Michael hull 1 på tjue minutter

Han har 16 år som trafikklærer og et elevregister. Fem elever, én telefonsamtale hver, og
disse spørsmålene — ordrett, uten å lede:

1. «Fortell om dagen du strøk. Hva gjorde du rett etterpå?»
2. «Var det ett spørsmål du husker at du ikke skjønte? Hva sto det?»
3. «Hva prøvde du før du kom til meg? Hvorfor sluttet du med det?»
4. «Hvem spurte du om hjelp? Hva sa de?»
5. «Hvis du skulle forklart en venn hvorfor det er vanskelig — hva ville du sagt?»

Skriv ned svarene **på det språket de svarer på**, ordrett, uten å pynte. Fem ekte
setninger fra spørsmål 5 er verdt mer enn hele dette dokumentet for agent 3.

---

## Kilder

Alle hentet 2026-08-04 via websøk. **Ingen av dem er åpnet direkte** — `WebFetch` ga 403
på samtlige domener. Innholdet er gjengitt via søkeresultater og må verifiseres før
publisering.

1. [K1] Nelo.no — «Teoriprøven koster 480 kr i 2026 – Slik betaler du» — https://nelo.no/blogg/hva-koster-teoriproven/
2. [K2] Billappen/bilprøven — «Hvor mye koster førerkortet i 2026? Komplett prisoversikt» — https://www.xn--bilprven-94a.no/artikler/hvor-mye-koster-forerkortet-komplett-prisoversikt
3. [K3] TeoriPortalen — «Billappen: pris og krav 2026» — https://teoriportalen.no/laering/billappen
4. [K4] Kjøresmart — «Hva koster kjøretimer? Pris i 2026» — https://www.xn--kjresmart-m8a.no/pris/hva-koster-kjoretimer
5. [K5] Kjøresmart — «Hva koster kjøreskole? Pris i 2026» — https://www.xn--kjresmart-m8a.no/pris/hva-koster-kjoreskole
6. [K6] TeoriPortalen — «Teoriprøve bil klasse B: 45 spørsmål og gratis øving» — https://teoriportalen.no/laering/teoriprove-klasse-b
7. [K7] Statens vegvesen — «Taking the theory test» (språk + tilrettelagt prøve) — https://www.vegvesen.no/en/driving-licences/driver-training/theory-test/taking-the-theory-test/
8. [K8] Statens vegvesen — «Tilrettelagt teoriprøve» — https://www.vegvesen.no/en/driving-licences/driver-training/theory-test/assisted-theory-test-for-special-needs-candidates/
9. [K9] TolkeNett — «Slik bestiller du tolk til teoriprøven» — https://tolkenett.no/en/landingsside/tolk-til-forerproven
10. [K10] Statens vegvesen — «Innbytte av førerkort fra land utenfor EU/EØS» — https://www.vegvesen.no/en/driving-licences/driving-licence-holders/foreign-driving-licence-in-norway/exchange-of-driving-licences-from-countries-outside-the-eueea/
11. [K11] NLS Norway Relocation — «Hvordan bytte utenlandsk førerkort til norsk førerkort» — https://nlsnorwayrelocation.no/hvordan-bytte-utenlandsk-forerkort-til-norsk-forerkort-frister-og-regler-i-norge/
12. [K12] Statens vegvesen — «Bruk av førerkort fra land utenfor EU/EØS i Norge» — https://www.vegvesen.no/en/driving-licences/driving-licence-holders/foreign-driving-licence-in-norway/using-a-non-eueea-driving-licence-in-norway/
13. [K13] forskning.no / Høgskolen i Nord-Trøndelag — «Når kjøreeleven ikke forstår norsk» (Olav Krogstad, publ. 16.06.2007) — https://www.forskning.no/bil-og-trafikk-partner-hogskolen-i-nord-trondelag/nar-kjoreeleven-ikke-forstar-norsk/991506
14. [K14] TeoriPortalen — «10 vanligste feil på teoriprøven» — https://teoriportalen.no/laering/vanlige-feil
15. [K15] Øvingsoppgaver.no — «Derfor stryker man på teoriprøven» — https://xn--vingsoppgaver-9mb.no/klasse-b-bil/artikler/derfor-stryker-man-pa-teoriproven-1.60138
16. [K16] TolkeNett — «Tilrettelegging av teoriprøve hos Statens vegvesen» — https://tolkenett.no/en/tjeneste/tolketjenester
17. [K17] Teoritolk — «Tjenester» (thai/norsk teoritolk) — https://teoritolk.no/tjenester/
18. [K18] thaitolk.no — «Tolketjenester» — https://www.thaitolk.no/tolketjenester3/
19. [K19] Thailands Tidende — «Tolk på norsk teoriprøve» — https://www.thailandstidende.com/component/k2/item/2140-tolk-p%C3%A5-norsk-teoripr%C3%B8ve
20. [K20] ICMF.no — «Alt du trenger å vite om pris på teoriprøve i 2024» — https://icmf.no/alt-du-trenger-a-vite-om-pris-pa-teoriprove-i-2024/
21. [K21] Kjøresmart — «Hva koster teoriprøven? Pris i 2026» — https://www.xn--kjresmart-m8a.no/pris/hva-koster-teoriproven
22. [K22] Norges Trafikkskoleforbund — «I trafikken – Introduksjon til norsk førerkort» (oversatt til 15 språk, inkl. thai) — https://ntsf.no/veien-til-forerkortet/i-trafikken-introduksjon-til-norsk-forerkort
23. [K23] DinSide/Dagbladet — «Nesten 56 000 strøyk til teoriprøven i 2025» — https://dinside.dagbladet.no/motor/nesten-56-000-stroyk/84187186
24. [K24] Statens vegvesen (pressemelding, jan. 2025) — «Altfor mange stryker på teoriprøven» — https://www.vegvesen.no/om-oss/presse/aktuelt/2025/01/altfor-mange-stryker-pa-teoriproven/
25. [K25] Noricom — «Bestill skjermtolking til teoriprøve» — https://www.noricom.no/bestillskjerm
26. [K26] App Store (NO) — anmeldelser av «Teoriprøven – Testen.no» — https://apps.apple.com/no/app/teoripr%C3%B8ven-testen-no/id1668742722
27. [K27] finndintrafikkskole.no — «Trafikkskoler Oslo» (språktilbud) — https://finndintrafikkskole.no/trafikkskoler-oslo/

**Interne kilder (verifisert av meg, i repoet):**
- `backend/server.py:1735-1781` — eksisterende `/stats/me`-aggregering
- `backend/server.py:242-266` — `QuizAttempt`-skjema (`total_questions`, `correct_answers`, `questions_answered`)
- `backend/server.py:916-931` — eksisterende feilsvar-pipeline med `$toUpper`-sammenlikning
- `backend/webapp.py:8194` — `category: currentCat ? currentCat.name : null` (kilden til manglende kategori i eksamensmodus)
- `backend/webapp.py:8199-8201` — fallback som skriver `questions_answered` uten svar
- `backend/scripts/seed_vikeplikt_questions.py` vs. `backend/server.py:2844+` — `"Vikeplikt"` og `"Right of Way"` som to navn på samme tema

---

## Strategic Second Pass

| # | Spørsmål | Score | Begrunnelse |
|---|----------|-------|-------------|
| 1 | Målgruppe spesifikk | 3/5 | Funnene består bytt-ut-testen: bytter du «thai» med «polsk», kollapser både smerte 1 og 2 (polske førerkort byttes inn 1:1, polsk er EØS). Det er ekte spesifisitet. Men jeg kan ikke navngi tre virkelige personer, og det finnes ikke én setning fra et faktisk menneske i målgruppen i dokumentet. Det er strukturelt riktig og menneskelig tomt. |
| 2 | Smerten akutt | 4/5 | Tremånedersfristen på utenlandsk førerkort [K12] er en dato med klokke på. 480 kr per strøket forsøk er akutt. Trekk fordi jeg ikke har belegg for at *denne uka* er den uka det gjør vondt — jeg har logikken, ikke opplevelsen. |
| 3 | Løftet troverdig | 4/5 | Dokumentets viktigste bidrag er å ta bort et løfte, ikke legge til ett: «ta teoriprøven på thai» er ikke sant, og jeg har stoppet det før det kom i et manus. Ingen garantier, ingen superlativer. Trekk fordi alle eksterne kilder er andrehånds (403 på alt) — troverdigheten hviler på at noen åpner lenkene. |
| 4 | Lead magnet trekker videre | 4/5 | Jeg leverer ikke lead magneten, men jeg leverer den åpenbare formen på den: fagords-broen i tabell B1. «De 7 norske ordene som får folk til å stryke — forklart på thai» løser ett ekte problem og har betalproduktet som naturlig neste steg. Trekk fordi B3 (thai-ordene) ikke er validert, og lead magneten må være 100 % thai. |
| 5 | Tjener penger | 5/5 | Linjen er kort og tegnbar: 480 kr per strøket forsøk → to stryk = 960 kr → livstid 699 kr er billigere enn å stryke to ganger. Tallet er sitert, ikke funnet på. Kanalen (norsk-thailandsk presse, tolkemiljøet) er identifisert. |
| 6 | Høres interessant ut | 3/5 | «Du har kjørt i tjue år i Thailand. Norge sier du må begynne på null» er en krok jeg ville sendt videre. Men dokumentet som helhet leser som skrivebordsresearch, fordi det *er* skrivebordsresearch. Uten én eneste elevstemme mangler det den setningen som gjør at noen kjenner seg igjen. |

**Snitt:** 3,8 — **Svakeste ledd:** #1 og #6 (samme årsak: null førstepersonsstemmer)

**Hva jeg ville fikset først:**
Snittet er under porten på 4,0, og jeg lar det stå slik med vilje. Å skrive dokumentet om
løfter ikke scoren — hullet er ikke formulering, det er datainnsamling, og verktøyene jeg
har (blokkert websidehenting, søkemotor som ikke indekserer thai-i-Norge-innhold, lukkede
Facebook-grupper) kommer ikke forbi det. Å pynte på scoren ville skjult nettopp det
Michael trenger å vite.

Porten passeres av fem telefonsamtaler, ikke av en ny AI-runde. Spørsmålene står i
«Hva jeg IKKE fant». Med fem ordrette elevsvar går #1 til 5 og #6 til 4–5, og agent 3 får
et manus som kan bygges på et menneske i stedet for en logisk slutning.

**I mellomtiden kan agent 2–4 trygt bygge videre på:**
- Gebyr- og strykstatistikken (verifiser 480 kr først)
- Smerte 1 og 2 — begge er strukturelle fakta, ikke stemninger
- Tabell B1 og B2 — dokumentert, brukbart som det står
- **Ikke** tabell B3 før Michael har validert den
