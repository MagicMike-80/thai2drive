# Runbook — slik kjøres Revenue Team

En kjøring tar deg fra «jeg har en idé» til «jeg har et tilbud, en vinkel og et
oppfølgingssystem». Regn med 30–60 minutter hvis du gjør jobben mellom stegene.

---

## Før du starter

1. Les [`business-brief.md`](business-brief.md). Er noe utdatert, fiks det **nå**.
2. Lag mappa for kjøringen:
   `revenue-team/outputs/YYYY-MM-DD-<kort-navn>/`
3. Er ideen ny eller uklar, kjør
   [gap-analyse-prompten](prompts/02-strategic-gap-analysis.md) først og svar på
   spørsmålene. Ikke start agentene på en uklar idé — da får du fire dokumenter
   med samme uklarhet i seg.

---

## Steg 0 — valgfritt: lær mens det bygges

Skal du forstå hva som skjer underveis, lim inn
[`prompts/01-teach-me-while-you-build.md`](prompts/01-teach-me-while-you-build.md)
i starten av sesjonen. Da forklarer Claude hver fil og hvert steg i klartekst
mens det jobbes.

---

## Steg 1 — market-signal-researcher

**Input:** business-brief + målgruppe du vil undersøke
**Output:** `01-market-signals.md`

Finner den faktiske frustrasjonen, med kundens egne ord. Ikke oppsummeringer —
sitater.

**Din jobb etterpå:** les sitatene. Kjenner du dem igjen fra 16 år i klasserommet?
Stryk det som er teoretisk riktig, men som du aldri har hørt et menneske si.

---

## Steg 2 — offer-architect

**Input:** `01-market-signals.md`
**Output:** `02-offer.md`

Bygger tilbudet: hva som er inkludert, pris, garanti, risikofjerner, og regnestykket
kunden gjør i hodet.

**Din jobb etterpå:** ville du selv kjøpt dette til denne prisen? Er svaret «kanskje»,
er tilbudet for svakt — send det tilbake med hva som mangler.

---

## Steg 3 — content-angle-strategist

**Input:** `01-market-signals.md` + `02-offer.md`
**Output:** `03-angles.md`

Lager vinkler og manus som treffer smerten direkte, i din stemme.

**Din jobb etterpå:** les det høyt. Høres det ut som deg? Hvis ikke — si hva som
er galt med tonen, og be om ny versjon. Ikke godta noe du ikke ville sagt selv.

---

## Steg 4 — conversion-system-builder

**Input:** alle tre foregående filene
**Output:** `04-conversion-system.md`

Lead magnet + 5 oppfølgings-e-poster som binder det hele sammen.

**Din jobb etterpå:** sjekk at lead magneten faktisk peker videre mot tilbudet.
En blindvei er bortkastet arbeid.

---

## Steg 5 — Strategic Second Pass

Kjør hele pakka gjennom
[`checklists/strategic-second-pass.md`](checklists/strategic-second-pass.md).
Snitt under 4,0 på de seks spørsmålene = tilbake til den agenten som er svakest.

Dette steget er ikke valgfritt. Det er forskjellen på et system og fire
AI-dokumenter ingen kommer til å bruke.

---

## Hvorfor rekkefølgen er hele poenget

Agentene kjører **sekvensielt, aldri i parallell**. Hver agent bruker forrige
agents output som råstoff:

```
markedssignaler  →  tilbud  →  vinkel  →  konverteringssystem
   (hva gjør vondt)  (hva vi selger)  (hvordan vi sier det)  (hvordan de kjøper)
```

Kjører du dem samtidig, finner de opp hver sin virkelighet: tilbudet løser en
smerte innholdet ikke nevner, og e-postene selger inn noe annet enn landingssiden
lover. Rekkefølgen er ikke administrasjon — det er selve forretningslogikken.

Og den kan ikke snus. Et tilbud laget før du vet hva som gjør vondt, er gjetting.
En vinkel laget før tilbudet finnes, har ingenting å peke på.

---

## Overleveringskontrakt

Hver output-fil skal starte med denne blokken, slik at neste agent vet hva den
faktisk fikk:

```markdown
---
agent: <agent-navn>
kjøring: YYYY-MM-DD-<kort-navn>
input: <filer den leste>
second-pass-score: <snitt av 6>
åpne spørsmål: <det agenten ikke kunne svare på>
---
```

`åpne spørsmål` er viktigst. En agent som later som den vet alt, sender feil
videre til de tre neste.

---

## Grenser (gjelder alle fire agentene)

- Skriver kun markdown i `revenue-team/outputs/`. Aldri kode, aldri produksjonsfiler.
- Endrer aldri priser, Stripe, auth, kvote, database eller mobil. Foreslår — i tekst.
- Sender aldri noe ut. Ingen e-post, ingen publisering, ingen annonser.
  Alt er utkast til Michael godkjenner.
- Oppgir kilde på alle tall, ellers `[ANTAKELSE]`.
