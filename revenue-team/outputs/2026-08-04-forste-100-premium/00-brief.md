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
2. **Agent 2:** verifiser prismodell 99 kr/mnd, 249 kr/3 mnd (beste verdi), 699 kr livstid.
   *(Rettet 2026-08-04: bestillingen sa opprinnelig 199 kr/mnd. Michael har spikret 99.)*
3. **Agent 3:** 30-sekunders TikTok/Reels-manus på verste kategori, Michael-tonen,
   mental modell («Kongen og tjeneren» / HAV-regelen).
4. **Agent 4:** lead magnet på 100 % ren thai + CTA «kommenter TEORI for 10 gratis spørsmål».

---

## Blokkeringer funnet i steg 0

### B1 — Produksjonsdata: tildelt Codex

`MONGO_URL` og `DB_NAME` finnes ikke i denne sesjonens miljø, og `.env` er ikke i repoet
(den er gitignorert, som den skal være). **Agent 1 hadde derfor ingen vei til MongoDB
Atlas, og leverte spørringen i stedet for et påfunnet tall.** Det var riktig håndtering.

**Status 2026-08-04:** Michael melder at live-datakoblingen til MongoDB Atlas nå lyser
grønt. **Codex skal kjøre den reelle aggregeringen mot `db.quiz_attempts`** og hente ut
faktiske feilsvar-statistikker per kategori.

Dataene finnes allerede: `db.quiz_attempts` lagrer `category`, `total_questions` og
`correct_answers` per forsøk, og aggregeringen er skrevet i `backend/server.py:1739-1765`
— den er bare låst til én `device_id`. Fjernes `$match` på device, får du tallet på tvers
av alle elever. Ferdig pipeline ligger i `01-market-signals.md`.

**Inntil Codex har kjørt den:** kategorivalget i `03-angles.md` er en `[ANTAKELSE]`.
Michaels erfaring peker på vikeplikt og rundkjøringer som de største smertepunktene, og
manuset er skrevet for vikeplikt. Ekte data kan flytte det, og da flyttes manuset.

### B2 — Prisen er vedtatt, men IKKE i drift

Bestillingen sa opprinnelig «bekreft at prismodellen er optimalisert til 199 kr/mnd».
Agent 2 kunne ikke bekrefte det, fordi live pris den gang var 99 kr/mnd.

**Michael vedtok 2026-08-04: 99 / 249 / 699.** Men per 2026-08-25 kjører produksjon
**199 / 399 / 699** (`PUBLIC_PRICING_FALLBACK`, `server.py:151`). Vedtaket er altså en
endring som gjenstår, ikke dagens tilstand.

**Rekkefølgen er tvungen:** Stripe Dashboard først (eies av Michael/Anti), deretter
konstanten i koden. Konstanten er en sperre — `_get_live_stripe_plan_prices_sync`
returnerer `None` ved avvik mot Stripe (`server.py:1146`), og `create_checkout_session`
kaster da 503 (`server.py:1604`). Endres koden først, **dør checkout for alle tre planene**.

3-månederspakken til 249 kr er den elevene skal ledes mot — ikke primært på rabatt, men
fordi tre måneder er normal øvingstid. Merk at rabattlogikken endrer seg med prisen:
ved 99/249 er rabatten 16,2 %, ved dagens 199/399 er den 33,2 %.

### B3 — CTA-en må peke på gratisuken, ikke på 10 spørsmål

«Kommenter TEORI for 10 gratis spørsmål» — registrerte gratisbrukere får
allerede **10 spørsmål per dag** (`ACCESS_REGISTERED_DAILY_LIMIT = 10`,
`backend/server.py:178`). Gjester får 5 totalt. Belønningen var altså ikke ny for noen.

**Med gratisuken som kjernekomponent løser dette seg selv.** Vi trenger ikke finne på
en belønning — vi har en som er ekte, større og allerede bygget: sju dager full Premium.
Det er ikke 10 spørsmål. Det er hele eksamensmodusen, alle forklaringene på thai, og
Michael-læreren, i en uke.

CTA-en skal derfor love gratisuken, ikke et antall spørsmål. Ordet TEORI beholdes som
kommentar-trigger (agent 4, Variant 1 — ingen kodeendring). Se `04-conversion-system.md`.

### B4 — Gratisuken var ukjent for agent 1–3, og endrer premisset

`TRIAL_DAYS = 7` (`backend/server.py:53`, brukt i 752-775 og 2072) gir **full
Premium-tilgang i sju dager ved registrering**. Funksjonen er aktiv i produksjon.
Agent 4 fant den; de tre foregående agentene visste ikke om den og skrev som om
betalingsmuren møter brukeren umiddelbart.

**Michael har besluttet at gratisuken er en kjernekomponent, ikke en detalj.** Den lar
eleven møte Michael V5 på morsmålet før noen ber om penger — noe målgruppen aldri har
opplevd og som ikke kan selges med én setning. All markedsføring synkroniseres rundt den.

**Konsekvens:** kjøpsøyeblikket er **dag 8**, og det er datostyrt. Det er også det
skarpeste frafallspunktet i hele reisen, og det er i dag udokumentert.

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
