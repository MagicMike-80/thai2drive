# ARGUS — to betydninger i dette prosjektet

Navnet «Argus» brukes om to helt forskjellige ting. Denne filen finnes for at de
ikke skal blandes i commit-meldinger, handoffs eller oppdragsbeskrivelser.

---

## 1. Argus-rapporten (dokument)

**Hva:** En strategisk produktanalyse av Thai2Drive — marked, konkurrenter,
språkstruktur, Michael-rollen, «Thailand vs. Norge», engasjement.

**Kilde:** Skrevet i en use.ai-samtale. Finnes også som PDF.

**Status:** Idé- og prioriteringsgrunnlag. **Ikke en arbeidsordre, og ikke
godkjent av verifikatøren.**

Viktige tall fra rapporten, korrigert mot Statens vegvesen:

| År | Klasse | Prøver | Bestått | Strøk |
|---|---|---|---|---|
| 2024 | Alle klasser | 218 460 | 57 % | 43 % |
| 2024 | B | 142 228 | **56 %** | **44 %** |
| 2025 | B | 137 772 | 60 % | 40 % |

**Rettelse:** Tidligere sammendrag har sagt «strykprosenten på klasse B var
56 %». Det er feil — 56 % er *bestått*prosenten. Stryk er 44 % i 2024 og 40 % i
2025. Bruk aldri «56 % stryker» i markedsføring eller innhold.

Kilde: Statens vegvesen, [«Altfor mange stryker på teoriprøven»](https://www.vegvesen.no/om-oss/presse/aktuelt/2025/01/altfor-mange-stryker-pa-teoriproven/),
publisert 9. januar 2025.

---

## 2. Argus (agenten)

**Hva:** Prosjektets verifikatør. Sjekker at det som er sagt ferdig faktisk
kjører i produksjon.

**Fil:** `argus.md`

**Mandat:** Se `VERIFY.md`.

**Tilgang:** Lesetilgang til repo, Railway og produksjonsdomenet.
**Ingen skrivetilgang til kode** — verken i repoet eller lokalt.

**Utfall:** Rapporten avsluttes alltid med `LUKKES` eller `ÅPEN`.

**Rekkefølge:** Rå HTML og hreflang på thai2drive.no → commit-hash live →
deploy-logg → lokale tester sist.

**Skal aldri:** endre kode, deploye, eller kjøre `pytest` mot produksjon.

---

## Regler for å holde dem fra hverandre

**Navngi presist i skrift.**
- «Argus-rapporten» = dokumentet
- «Argus» = agenten

**Gi aldri agenten et strategioppdrag.** Argus verifiserer påstander. Han
prioriterer ikke veikart, foreslår ikke funksjoner og vurderer ikke
forretningsidéer. Det hører til rapporten og til produktteamet.

**Et `LUKKES` godkjenner én teknisk oppgave — ikke rapportens anbefalinger.**
At Argus sier `LUKKES` på språkrutene betyr at rutene virker i produksjon. Det
betyr ikke at «Thailand vs. Norge», beståttgarantien eller Michael-skillet er
godkjent eller gjennomført.

**Argus godkjenner aldri sin egen fiks.** Finner han noe, rapporterer han det og
går videre. Rettelsen gjøres av byggeren, og verifiseres på nytt.

---

## Kortversjon

| | Argus-rapporten | Argus (agenten) |
|---|---|---|
| Type | Dokument | Agent |
| Spørsmål | «Hva bør vi bygge?» | «Virker det som er bygget?» |
| Bevis | Markedsdata, analyse | Rå produksjonsoutput |
| Utfall | Prioriteringsliste | `LUKKES` / `ÅPEN` |
| Skriver kode | Nei | **Nei** |
