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

| Plan | Pris | Merk |
|------|------|------|
| Månedlig | 99 kr | Løpende |
| 3 måneder | 249 kr | Ca. 83 kr/mnd |
| Livstid | 699 kr | Engangsbetaling |

Priser hentes live fra Stripe med disse som fallback
(`PUBLIC_PRICING_FALLBACK` i `backend/server.py`).

Gratis nivå:
- Gjest: 5 spørsmål totalt
- Registrert, ikke betalende: 10 spørsmål per dag

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
for å ha betalt seg selv. Det er den regnestykket all kommunikasjon skal lene seg på —
men de faktiske gebyrsatsene skal hentes fra Vegvesenet og siteres, ikke gjettes.

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
