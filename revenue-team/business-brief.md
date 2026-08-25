# Business Brief — Thai2Drive

Dette er fasiten alle fire agentene leser før de gjør noe som helst.
Er noe her feil, blir alt agentene lager feil. Hold den oppdatert.

**Sist oppdatert:** 2026-08-04

---

## 1. Hvem står bak

Michael — trafikklærer med 16 års erfaring. Født i Thailand, oppvokst i Sverige,
jobber i norsk trafikkopplæring i dag.

Dette er den viktigste ressursen i hele forretningen: han er ikke en tech-gründer
som har funnet en nisje. Han er en fagperson som har sett det samme problemet
gjenta seg i 16 år. Alle vinkler skal bygge på dette, ikke på generiske
AI-og-edtech-fraser.

---

## 2. Hva produktet er

Thai2Drive er en teoriapp/-kurs for **klasse B** rettet mot thaitalende i Norge.
Kjernen er at hele læringsløpet finnes på thai — spørsmål, forklaringer og
AI-læreren «Michael Trafikklærer» — slik at eleven slipper å lære seg norsk
byråkratspråk *før* hen kan lære seg trafikkregler.

Flater:
- **Webapp** (produksjon) — `/api/web`
- **Mobil** (Expo/Android) — sekundær, endres kun etter eksplisitt godkjenning

---

## 3. Målgruppen (primær)

Thaitalende voksne bosatt i Norge som skal ta teoriprøven for klasse B.

Typisk situasjon, slik den er observert:
- Behersker hverdagsnorsk, men ikke fagspråket i teoriboka
- Har ofte strøket én eller flere ganger allerede
- Betaler for kjøretimer som ikke kan brukes før teorien er bestått
- Skammer seg over å be om hjelp, og gir opp i stillhet i stedet

**Ikke bekreftet ennå:** størrelsen på segmentet, hvor de faktisk søker hjelp,
og hvor mange som allerede har strøket. Dette er market-signal-researcher sin
første jobb — ikke gjett.

## Sekundære segmenter (ubekreftet — trenger validering før vi bygger for dem)

- Trafikkskoler med mange thaitalende elever (B2B)
- Andre språkgrupper med samme problem (arabisk, tigrinja, polsk)

---

## 4. Hvordan det tjener penger i dag

| Plan | I produksjon nå | Vedtatt mål | Merk |
|------|-----------------|-------------|------|
| Månedlig | **199 kr** | 99 kr | Løpende |
| 3 måneder | **399 kr** | 249 kr | Målet gir ca. 83 kr/mnd |
| Livstid | **699 kr** | 699 kr | Uendret |

> **Ikke bruk målprisen som om den er live.** Michael har vedtatt 99 / 249 / 699,
> men produksjon kjører 199 / 399 / 699 per 2026-08-25. Skriver du markedsføring med
> 99 kr før byttet er gjort, lover du en pris kunden ikke får.

**Prisbytte krever to steg, i tvungen rekkefølge:**
1. Nye Prices opprettes i **Stripe Dashboard** — eies av Michael/Anti
2. Deretter settes `PUBLIC_PRICING_FALLBACK` (`backend/server.py:151`) til 99 / 249 / 699

Konstanten er **en sperre, ikke bare et tall**: `_get_live_stripe_plan_prices_sync`
sammenligner hver plan mot Stripe (`expected_minor`, `server.py:1146`) og returnerer
`None` ved avvik, hvorpå `create_checkout_session` kaster 503 (`server.py:1604`).
Endres koden før Stripe, **dør checkout for alle tre planene**.

Merk også: `allow_promotion_codes: False` er hardkodet i checkout (`server.py:1635`).
En «kampanje» kan derfor ikke være en Stripe-rabattkode.

**Hvorfor trappen ser slik ut** (vedtatt av Michael 2026-08-04):
249 kr er planen elevene skal ledes mot, og «Beste verdi»-merket ligger allerede der
(`backend/webapp.py:3942`). Begrunnelsen er ikke rabattpsykologi alene — **tre måneder
er normal øvingstid**. Pakken selger den ærlige lengden på jobben. Rabatten på 16,2 %
er den synlige belønningen for å velge riktig lengde.

### Gratisuken — les denne før du skriver ett ord markedsføring

```
TRIAL_DAYS = 7                       backend/server.py:53
_grant_trial_if_eligible(...)        backend/server.py:752-775
  → kalles ved /auth/signup          backend/server.py:2072
```

**Enhver ny registrering gir sju dager med hele Premium. Gratis. Uten kort.**
Eksamensmodus, AI-forklaringene på thai, Michael-læreren, trening på svake temaer,
historikk — alle `is_premium`-flaggene i `server.py:824-833` står true i de sju dagene.
Kun én gang per e-post og per device_id (`server.py:758-764`).

Dette er **ikke en detalj**. Det er kjernekomponenten i hele inntektsveien, av én grunn:
målgruppen har aldri møtt en trafikklærer som forklarer på morsmålet deres. Det kan ikke
selges med en setning — men det kan gis bort i sju dager, og da selger det seg selv.

**Konsekvenser enhver agent må bygge på:**
- Vi selger ikke tilgang. Vi selger *fortsettelsen* av noe eleven allerede har erfart.
- Kjøpsøyeblikket er **dag 8**, og det er datostyrt.
- Dag 8 er også det skarpeste frafallspunktet i reisen, og er per 2026-08-04 udokumentert.
- En CTA som lover «10 gratis spørsmål» selger produktet **ned**. Lov gratisuken.

Gratis nivå etter at uken er over:
- Gjest: 5 spørsmål totalt
- Registrert, ikke betalende: 10 spørsmål per dag, uten sluttdato

Betaling: Stripe på web, RevenueCat på mobil.

> **Agentene endrer aldri disse prisene.** De kan *foreslå* endringer i et output-dokument.
> Selve endringen gjør Michael, med Anti.

---

## 5. Den økonomiske logikken kunden regner på

Det tilbudet må slå: **kostnaden ved å stryke**.

- Teoriprøven koster gebyr per forsøk
- Kjøretimer som er kjøpt før teorien er bestått, står ubrukt
- Måneder uten førerkort = færre jobber som krever bil

En livstidslisens til 699 kr trenger bare å spare **ett** strøket forsøk
for å ha betalt seg selv. Det er regnestykket all kommunikasjon skal lene seg på —
men de faktiske gebyrsatsene skal hentes fra Vegvesenet og siteres, ikke gjettes.

> **Gebyrsatsen er per 2026-08-04 ikke verifisert.** Tre forsøk har feilet: vegvesen.no
> gir 403 eller er blokkert av nettverksproxyen. Kilder spriker mellom 350, 480 og 680 kr,
> og Vegvesenets egne satser gjelder **fra 1. februar 2026** — så alle tall vi har er
> trolig utdaterte. **Ingen agent skal trykke et gebyrbeløp noe sted** før Michael har
> lest 2026-satsen på `vegvesen.no/forerkort/ta-forerkort/gebyr/`. Bruk formelen, ikke tallet.

---

## 6. Hva vi ikke selger på

- ❌ «AI-drevet» som hovedargument. AI er hvordan, ikke hvorfor.
- ❌ Løfter om garantert bestått. Vi kontrollerer ikke prøven.
- ❌ Sammenligning som snakker ned konkurrenter ved navn.
- ❌ Frykt- og skammebasert markedsføring. Målgruppen skammer seg allerede nok.

Tonen er Michael-personaen: trygg, rolig, konkret. 7-årsregelen — hvis en
sjuåring ikke forstår setningen, er den for komplisert.

---

## 7. Ny idé? Fyll ut denne før du kjører agentene

Skal systemet brukes på noe annet enn Thai2Drive, kopier blokken under til
`outputs/<dato>-<navn>/00-brief.md` og fyll den ut:

```markdown
- Hvem er kunden (så spesifikt at du kan navngi tre av dem):
- Hva er det akutte problemet, med deres egne ord:
- Hva selger vi, og hva er prisen:
- Hvorfor oss / hvilken personlig erfaring gir troverdighet:
- Hva regner kunden på for å forsvare kjøpet:
- Hva vi aldri lover:
- Hvilken kanal skal dette leve i:
```

Mangler noe her, skal **gap-analyse-prompten** kjøres først —
se [`prompts/02-strategic-gap-analysis.md`](prompts/02-strategic-gap-analysis.md).
