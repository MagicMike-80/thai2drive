---
name: revenue-team
description: 'Kjør 4-agents Revenue Team sekvensielt: markedssignaler → tilbud → innholdsvinkel → konverteringssystem. Bruk når du skal gjøre en forretningsidé om til en komplett inntektsvei, validere en målgruppe, bygge et tilbud, eller lage lead magnet og e-postsekvens for Thai2Drive.'
argument-hint: 'Idé eller målgruppe (f.eks. "thaitalende som har strøket én gang", "B2B mot trafikkskoler", eller blank for full kjøring på business-brief)'
user-invocable: true
---

# Revenue Team — orkestrering

Kjører fire spesialiserte agenter etter hverandre og gjør én idé om til en
komplett inntektsvei. Systemdokumentasjonen ligger i
[`revenue-team/`](../../../revenue-team/README.md).

---

## Steg 0 — sjekk at premisset holder

1. Les `revenue-team/business-brief.md`.
2. Er ideen ny eller uklar, kjør
   [gap-analyse-prompten](../../../revenue-team/prompts/02-strategic-gap-analysis.md)
   og **vent på Michaels svar** før du starter agent 1.

   Ikke start fire agenter på en uklar idé. Da får du fire dokumenter med
   nøyaktig samme uklarhet i seg, og de ser overbevisende ut.

3. Opprett `revenue-team/outputs/YYYY-MM-DD-<kort-navn>/`.

---

## Steg 1–4 — agentene, i denne rekkefølgen

| # | Agent | Leser | Skriver |
|---|-------|-------|---------|
| 1 | `market-signal-researcher` | brief | `01-market-signals.md` |
| 2 | `offer-architect` | brief + 01 | `02-offer.md` |
| 3 | `content-angle-strategist` | brief + 01 + 02 | `03-angles.md` |
| 4 | `conversion-system-builder` | brief + 01 + 02 + 03 | `04-conversion-system.md` |

**Aldri i parallell.** Hver agent bruker forrige agents output som råstoff.
Kjører du dem samtidig, finner de opp hver sin virkelighet — og tilbudet ender
opp med å løse en smerte innholdet aldri nevner.

**Stopp mellom hvert steg.** Vis Michael resultatet og spør om det stemmer med
det han har sett i 16 år som trafikklærer. Det er den delen ingen agent kan gjøre.

---

## Steg 5 — Strategic Second Pass

Kjør hele pakka gjennom
[`checklists/strategic-second-pass.md`](../../../revenue-team/checklists/strategic-second-pass.md)
og skriv `05-second-pass.md`.

Snitt under **4,0**, eller én enkeltscore på 1–2 → tilbake til den svakeste agenten.
Ikke lever videre med en dårlig score og en unnskyldning.

---

## Harde grenser

- **Kun markdown i `revenue-team/outputs/`.** Ingen kode, ingen produksjonsfiler.
- **Rør aldri** Stripe, priser, auth, kvote, database eller mobil.
  Forslag skrives som tekst, merket `FORSLAG — krever godkjenning`.
- **Publiser og send aldri noe.** Ingen e-post, ingen annonser, ingen opplasting.
- **Ingen oppdiktede tall eller sitater.** Uten kilde: `[ANTAKELSE]`.
- **Språkisolasjon:** ett innholdsstykke = ett språk. Aldri blandet.
- **Aldri lov bestått teoriprøve.**
- Er oppgaven egentlig kode eller deploy: si
  «This task belongs to Anti. I should not do this part.»

---

## Delkjøringer

Du trenger ikke kjøre alle fire hver gang:

```
Bruk market-signal-researcher på segmentet trafikkskoler i Oslo.
Bruk offer-architect på nytt — tilbudet var for svakt, prisen ikke begrunnet.
Bruk content-angle-strategist. Kun thai, kun Facebook.
```

Hopper du over et steg, si det høyt i output-filen. En agent som later som den
fikk input den ikke fikk, sender feilen videre til alle de neste.
