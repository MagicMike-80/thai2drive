# 06 — AI-oppskrifter: bilde, video og stemme

Målet med denne filen: at du aldri skal skrive en prompt fra bunnen igjen, og at alt du
lager skal se ut som det kommer fra samme sted.

---

## Stil-låsen

Alt visuelt henter fra samme palett som appen (`design_guidelines.json`). Det er dette som
gjør at en Reel, en app-skjerm og et tilbud til en trafikkskole ser ut som ett produkt.

| Rolle | Verdi | Bruk i prompt |
|-------|-------|---------------|
| Bakgrunn | `#0F172A` | *deep navy-slate background, near-black* |
| Kort/flate | `#1E293B` | *dark slate panel* |
| Merkefarge | `#F59E0B` | *warm amber accent light* |
| Riktig | `#10B981` | *emerald green* |
| Feil | `#EF4444` | *signal red* |
| Tekst | `#F8FAFC` | *near-white* |

**Arketype:** Swiss & High-Contrast. **Tone:** trygg, klar, autoritativ, fokusert.
**Aldri:** pastell, cartoon, stock-smil, klipparkiv-følelse, amerikanske skilt og biler.

### Stil-suffikset — lim på slutten av hver bilde-prompt

```
Style: cinematic Nordic realism, dark navy-slate palette (#0F172A base, #1E293B panels),
single warm amber key light (#F59E0B), high contrast, shallow depth of field,
Norwegian road environment, overcast Scandinavian daylight, no text, no watermark,
photoreal, 35mm, clean composition
```

### Negativ-prompt — lim på alt

```
no american road signs, no left-hand traffic, no text overlays, no watermark,
no distorted hands, no extra fingers, no cartoon style, no pastel colors,
no stock-photo smiling, no license plates with readable text, no logos
```

---

## Prompt-formelen

Fem ledd, alltid i denne rekkefølgen. Bytt ut innholdet, behold rekkefølgen.

```
[MOTIV] + [HANDLING] + [MILJØ] + [LYS] + [KAMERA] + [stil-suffiks] + [negativ-prompt]
```

**Eksempel — vikeplikt i kryss:**

```
A silver compact car stopped at a give-way line at a four-way junction, driver's
point of view from inside the cabin, Norwegian suburban street with birch trees and
red wooden houses, overcast late-afternoon light, single amber street lamp glow,
low wide-angle dashboard perspective
+ [stil-suffiks] + [negativ-prompt]
```

**Eksempel — rundkjøring ovenfra:**

```
Aerial top-down view of a two-lane roundabout in a Norwegian town, three cars
approaching from different arms, clean wet asphalt with clear white lane markings,
soft overcast daylight, drone perspective 60 meters up
+ [stil-suffiks] + [negativ-prompt]
```

**Eksempel — Michael-figuren:**

```
Portrait of a calm, experienced male driving instructor in his forties, Asian-Nordic
features, short dark hair, plain dark jacket, seated in the passenger seat of a car,
looking toward the camera with a reassuring expression, hands relaxed, interior of a
modern car, soft daylight through the windscreen, amber dashboard glow
+ [stil-suffiks] + [negativ-prompt]
```

> **Konsistens-triks:** når du har fått ett Michael-bilde du er fornøyd med, lagre både
> bildet og den nøyaktige prompten under "Prompts som satt" nedenfor, og bruk bildet som
> referansebilde i alle senere generasjoner. Da holder ansiktet seg likt på tvers av videoer.

---

## Videoprompt (Google Flow / Veo-familien)

Samme formel, men legg til bevegelse — og bare **én** bevegelse per klipp.

```
[stillbilde-prompten] , camera: [slow push in / static locked off / slow pan right],
subject motion: [car rolls forward slowly / driver turns head to check mirror],
duration 4 seconds, no cuts
```

**Regler som sparer deg for kasserte klipp:**
- Én kamerabevegelse per klipp. Kamera *og* motiv som beveger seg gir grøt.
- 3–5 sekunder per generering. Lengre klipp gir flere artefakter.
- Unngå ansikter i bevegelse når du kan. Bruk hender, ratt, speil, skilt, føtter på pedaler.
- Aldri be om lesbar tekst i bildet. Tekst legges på i CapCut.

---

## Stemmeregister (ElevenLabs)

Fyll inn de faktiske voice-ID-ene. Uten ID-en må du lete deg fram på nytt hver gang, og
da blir stemmen ulik fra video til video — det er det raskeste man kan ødelegge et
merkevareinntrykk på.

| Rolle | Språk | Stemmenavn | Voice ID | Innstillinger | Brukes til |
|-------|-------|-----------|----------|---------------|-----------|
| Michael (hovedstemme) | Norsk | [FYLL INN] | [FYLL INN] | Stability ~50, Similarity ~75 | Fagvideoer, forklaringer |
| Michael (thai) | Thai | [FYLL INN] | [FYLL INN] | | Thai2Drive-innhold |
| Fortellerstemme | Norsk | [FYLL INN] | [FYLL INN] | | Hooks, statistikk, dramatiske åpninger |
| Elevstemme / kontrast | Norsk | [FYLL INN] | [FYLL INN] | | Dialogklipp, "eleven sier…" |

**Kjent fra prosjektet:** thai TTS i appen bruker `th-TH-Chirp3-HD-Achird` (Google), ikke
ElevenLabs — `th-TH-Standard-C` er utgått. ElevenLabs-nøkkelen ligger som `ELEVENLABS_API_KEY`
i Railway. Ikke skriv nøkler inn i denne filen — kun stemmenavn og voice-ID-er.

**Innlesningsregler:**
- Michael snakker langsomt. Legg inn pause etter hookspørsmålet — la seeren rekke å tenke.
- Ett trykk per setning, ikke tre.
- Aldri opphisset selger-tone. Trygg lærer. Det er hele posisjonen din.
- Ett språk per lydspor. Aldri bland norsk og thai i samme spor.

---

## Prompts som satt

Lim inn de promptene du allerede er fornøyd med. Dette er biblioteket ditt — og det som
gjør at jeg kan skrive nye prompts i *din* stil, ikke i en generisk stil.

```
### [Kort navn]
Verktøy: [Flux / Google Flow / Midjourney / annet]
Prompt:
[lim inn ordrett]
Hva som ble bra:
Hva jeg måtte justere:
```

### [FYLL INN — prompt 1]
### [FYLL INN — prompt 2]
### [FYLL INN — prompt 3]

---

## Formater

| Bruk | Format | Oppløsning |
|------|--------|-----------|
| TikTok / Reels / Shorts | 9:16 | 1080 × 1920 |
| Facebook-feed | 4:5 | 1080 × 1350 |
| Miniatyr / cover | 1:1 | 1080 × 1080 |
| Tilbud og presentasjon til skoler | 16:9 | 1920 × 1080 |
