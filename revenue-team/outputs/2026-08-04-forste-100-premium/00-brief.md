---
kjøring: 2026-08-04-forste-100-premium
mål: første 100 Premium-kunder
bestilt av: Michael
---

# Kjøringsbrief — første 100 Premium-kunder

Alle fire agentene leser denne før de starter. Den beskriver **hva som er bestilt**
og **hva som faktisk er mulig i denne sesjonen**. Spriket mellom de to er ikke en
detalj — det avgjør hva agentene har lov til å påstå.

---

## Bestillingen

1. **Agent 1:** finn kategorien med høyest strykprosent i produksjonsdatabasen.
2. **Agent 2:** verifiser prismodell 199 kr/mnd, 249 kr/3 mnd (beste verdi), 699 kr livstid.
3. **Agent 3:** 30-sekunders TikTok/Reels-manus på verste kategori, Michael-tonen,
   mental modell («Kongen og tjeneren» / HAV-regelen).
4. **Agent 4:** lead magnet på 100 % ren thai + CTA «kommenter TEORI for 10 gratis spørsmål».

---

## Tre blokkeringer funnet i steg 0

### B1 — Produksjonsdatabasen er ikke tilgjengelig i denne sesjonen

`MONGO_URL` og `DB_NAME` finnes ikke i miljøet, og `.env` er ikke i repoet
(den er gitignorert, som den skal være). Det finnes ingen vei til MongoDB Atlas herfra.

**Konsekvens:** Agent 1 kan ikke levere ekte strykprosent. Den skal levere
spørringen Michael selv kan kjøre, ikke et tall den har funnet på.

Den gode nyheten: **dataene finnes allerede.** `db.quiz_attempts` lagrer
`category`, `total_questions` og `correct_answers` per forsøk, og
aggregeringen er allerede skrevet i `backend/server.py:1739-1765` — den er bare
låst til én `device_id`. Fjerner du `$match` på device, får du tallet på tvers av
alle elever. Se `01-market-signals.md` for ferdig pipeline.

### B2 — Prisen i bestillingen stemmer ikke med prisen i produksjon

Bestillingen sier «bekreft at prismodellen er optimalisert til 199 kr/mnd».
Live pris er **99 kr/mnd** (`PUBLIC_PRICING_FALLBACK`, `backend/server.py:146-155`,
med Stripe som overstyrende kilde).

Agent 2 skal ikke «bekrefte» en pris som ikke er den som kjøres. Den skal vise
hva en dobling faktisk gjør med pakkelogikken, og levere det som `FORSLAG`.

### B3 — CTA-en lover noe brukeren allerede får gratis

«Kommenter TEORI for 10 gratis spørsmål» — registrerte gratisbrukere får
allerede **10 spørsmål per dag** (`ACCESS_REGISTERED_DAILY_LIMIT = 10`,
`backend/server.py:178`). Gjester får 5 totalt.

Belønningen er altså ikke ny for noen som registrerer seg. Agent 4 må enten
finne en belønning som faktisk er ekstra, eller omformulere slik at løftet er sant.
Et løfte som slår sprekker i det sekundet eleven logger inn, koster mer tillit
enn kommentaren er verdt.

---

## Arbeidsantakelse for agent 2–4

Uten ekte tall må agent 3 og 4 ha en kategori å jobbe med. Vi bruker:

> **[ANTAKELSE] Verste kategori = vikeplikt, med rundkjøring som verste undertilfelle.**

Begrunnelse (ikke bevis):
- `Vikeplikt` er en egen, ferdig seedet kategori i produksjon
  (`backend/scripts/seed_vikeplikt_questions.py`)
- Det er den største kategorien i innholdsfilene i repoet
- «Kongen og tjeneren» er en vikepliktsmodell, og den er allerede etterspurt

**Denne antakelsen skal stå merket i hver eneste fil.** Bekrefter tallene noe
annet, kjøres agent 3 og 4 på nytt. Det er billig. Å bygge en kampanje på feil
kategori er det ikke.

---

## Datakvalitet Michael bør kjenne til

Kategorinavnene er ikke konsistente. I innholdsfilene finnes `Right of Way`,
`roundabouts`, `road_signs`, `Situations` og `Mechanics` om hverandre — engelsk og
norsk, entall og flertall. Aggregeringen i `server.py` filtrerer allerede bort
`None`, `""` og `"None"`, noe som tyder på at en del forsøk mangler kategori helt.

En strykprosent per kategori blir ikke bedre enn navngivningen under seg.
Det er verdt å rydde i før tallet brukes som beslutningsgrunnlag.

---

## Grenser for denne kjøringen (fra Michael, uendret)

- Ingenting slettes.
- Stripe og kildekode røres ikke.
- Alt leveres som markdown for manuell godkjenning.
- Ingen oppdiktede tall eller sitater. Uten kilde: `[ANTAKELSE]`.
- Thai-materiell er 100 % thai. Norsk er 100 % norsk. Aldri blandet.
- Aldri lov bestått teoriprøve.
