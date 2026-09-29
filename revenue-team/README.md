# Revenue Team — 4-agents system for inntektsarbeid

Dette er et **arbeidssystem**, ikke kode. Det består av fire spesialiserte
Claude-agenter som kjører **etter hverandre** og gjør om én forretningsidé til
en komplett inntektsvei: markedssignaler → tilbud → innholdsvinkel → konverteringssystem.

Systemet er en del av det parallelle prosjektet «Thai2Drive Builder System».
Det rører **ingen** produksjonskode, database, Stripe, auth eller mobil.
Alt agentene lager havner som markdown i [`outputs/`](outputs/).

---

## Filoversikt

| Fil / mappe | Hva den gjør |
|-------------|--------------|
| [`business-brief.md`](business-brief.md) | Fasit om virksomheten. Alle fire agenter leser denne først. |
| [`runbook.md`](runbook.md) | Kjøreplanen: rekkefølge, overleveringer, hva du gjør mellom hvert steg. |
| [`prompts/`](prompts/) | De tre faste promptene (lær-mens-du-bygger, gap-analyse, refine/merge). |
| [`checklists/strategic-second-pass.md`](checklists/strategic-second-pass.md) | Kvalitetsporten med de 6 spørsmålene. Ingenting slipper ut uten denne. |
| [`outputs/`](outputs/) | Alt agentene produserer, én mappe per kjøring. |
| `.claude/agents/*.md` | Selve agentdefinisjonene (fire filer, i repo-roten). |
| `.claude/skills/revenue-team/SKILL.md` | `/revenue-team` — starter en kjøring. |

---

## Slik starter du

```
/revenue-team
```

Eller manuelt, ett steg om gangen:

```
Bruk market-signal-researcher. Målgruppe: thaitalende i Norge som skal ta teoriprøven.
```

Kjør **aldri** alle fire i parallell. Rekkefølgen er hele poenget — se
[`runbook.md`](runbook.md#hvorfor-rekkefølgen-er-hele-poenget).

---

## De fire agentene

1. **market-signal-researcher** — finner den faktiske frustrasjonen med eksakte ord fra
   virkelige mennesker. Gjetter aldri på tall.
2. **offer-architect** — pakker løsningen inn i et tilbud med pris, garanti og risikofjerner.
3. **content-angle-strategist** — lager vinkler og manus som treffer smerten direkte.
4. **conversion-system-builder** — bygger lead magnet + e-postsekvens som selger inn tilbudet.

Hver agent avslutter med å score sitt eget arbeid mot de 6 spørsmålene i
[`checklists/strategic-second-pass.md`](checklists/strategic-second-pass.md).
Snitt under 4,0 = utkastet skrives om før neste agent får det.

---

## Tre faste regler

1. **Ingen agent skriver kode.** Kun markdown i `outputs/`. Prisendringer,
   Stripe-oppsett, e-postutsending og landingssider er implementering — det er Antis bord,
   og krever at Michael ber om det eksplisitt.
2. **Ingen påstander uten kilde.** Tall og sitater skal ha lenke eller merkes
   `[ANTAKELSE]`. Oppdiktet statistikk er verre enn ingen statistikk.
3. **Språkisolasjon gjelder også markedsføring.** Thai-materiell = 100 % thai.
   Norsk = 100 % norsk. Aldri blandet i samme tekst mot samme leser.
