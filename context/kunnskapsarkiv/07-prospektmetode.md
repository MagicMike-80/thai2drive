# 07 — Prospektmetode: "Do the work first"

Kjernen i strategien: **du selger ikke en tjeneste, du leverer et ferdig resultat og spør
om de vil ha mer.** En trafikkskole som får tilsendt en ferdig video av seg selv trenger
ikke forestille seg hva du kan gjøre. De ser det.

Din urettferdige fordel: du er ikke en markedsfører som prøver å forstå trafikkskoler.
Du er trafikklærer med 16 år i bilen, som også lager innhold. Du kan si "jeg vet hvorfor
elevene deres stryker på vikeplikt" og faktisk mene det. Ingen byrå kan kopiere det.

---

## Steg 1 — Kartlegg (2 timer, én gang)

Fyll ut `07-prospekter.csv`. Én rad per skole. Poenget er ikke å ha 20 rader, det er å
vite *hvilke tre* som er lettest å lande.

Sjekk fire ting per skole, det tar to minutter hver:

1. **Når publiserte de sist på Facebook eller Instagram?** Dette er den viktigste kolonnen.
2. **Hvor mange følgere?** Under 500 = de har ikke prøvd. Over 2000 = de bryr seg allerede.
3. **Har de video i det hele tatt, eller bare bilder av biler?**
4. **Hvem eier skolen?** Navnet på personen. Ikke "post@".

### Aktivitetsscore

Gi hver skole 1–5. Det er ikke et mål på hvor gode de er — det er et mål på hvor lett
de er å hjelpe.

| Score | Kjennetegn | Vurdering |
|-------|-----------|-----------|
| 1 | Ingen sosiale medier i det hele tatt | Vanskelig. Må selges på idé, ikke forbedring |
| 2 | Side finnes, siste innlegg over 6 mnd siden | **Best mulig prospekt.** Åpenbart hull, ingen konkurranse |
| 3 | Publiserer sporadisk, kun bilder og delte lenker | **Nest best.** De prøver, men mangler format |
| 4 | Fast rytme, litt video, middels resultat | Krevende. Må vise klart bedre |
| 5 | Aktive, gode videoer, høyt engasjement | Hopp over. Eller selg fag-korrekthet som eneste vinkel |

**Start med alle 2-erne.** En skole som ikke har publisert siden i fjor vet det godt selv,
og har dårlig samvittighet for det. Du løser en flau situasjon for dem.

---

## Steg 2 — Lag arbeidet ferdig (2 timer per skole)

Velg **tre** skoler. Lag én ferdig video til hver. Ikke et utkast — ferdig, publiserbart,
med skolens navn i siste bilde.

**Hva videoen skal være:**
- 30–45 sekunder
- En hook fra kategori A eller C i `04-hookbank.md` (vikeplikt eller skilt — det er der elevene stryker)
- Faglig vanntett, sporet til `01-fagkunnskap-klasse-b.md`
- Skolens navn og logo kun i siste to sekunder

**Hva videoen ikke skal være:** en reklame for skolen. Den skal være nyttig for eleven.
Det er selve poenget du selger: innhold som hjelper elever består av seg selv, og markedsfører
skolen som en bieffekt.

---

## Steg 3 — Send (5 minutter)

Send til personen, ikke til `post@`. Kort e-post. Video vedlagt eller lenket.

### Mal A — førstegangskontakt

> **Emne:** Lagde en video til [Skolenavn] — vikeplikt i rundkjøring
>
> Hei [Fornavn],
>
> Jeg heter Michael og er trafikklærer, 16 år i bilen. Jeg lager også korte videoer om
> trafikkfag.
>
> Jeg la merke til at [Skolenavn] ikke har lagt ut noe på Facebook på en stund, så jeg
> lagde en video dere kan bruke. Den handler om vikeplikt i rundkjøring — en av de vanligste
> grunnene til stryk på oppkjøring.
>
> Den er ferdig. Bare last ned og legg ut, med eller uten kreditt. Den koster ingenting.
>
> Om den funker for dere, lager jeg gjerne flere.
>
> Michael
> [telefon] · [nettside]

Ingen prisliste. Ingen "book en samtale". Ingen vedlagt PDF med tjenestepakker.
Du gir noe bort, og lar det snakke.

### Mal B — oppfølging etter 7 dager

> **Emne:** Re: Lagde en video til [Skolenavn]
>
> Hei [Fornavn],
>
> Følger bare opp — fikk du sett videoen?
>
> Om den ikke traff, si gjerne fra hva som manglet. Jeg lager en ny.
>
> Michael

Én oppfølging. Ikke to. Skoler som ikke svarer på to henvendelser skal ligge til side
til du har noe nytt å vise.

### Mal C — når de svarer positivt

> Hei [Fornavn], så bra at den var nyttig.
>
> Slik jobber jeg vanligvis: [X] videoer i måneden, ferdig produsert, klare til publisering.
> Dere trenger ikke gjøre noe annet enn å legge dem ut.
>
> Skal jeg sende over et forslag til de neste fire temaene, så ser dere hva det blir?
>
> Michael

Fortsatt ingen pris i første svar. Send temaforslaget først — da diskuterer dere innhold,
ikke kroner, og prisen kommer etter at verdien er etablert.

---

## Steg 4 — Prising

Fyll inn dine egne tall. Modellene som er vanlige i denne nisjen:

| Modell | Hva den passer til | Din pris |
|--------|-------------------|----------|
| Per video | Første oppdrag, uforpliktende | [FYLL INN] |
| Månedspakke (4 videoer) | Målet. Forutsigbart for begge | [FYLL INN] |
| Månedspakke (8 videoer) | Skoler med flere avdelinger | [FYLL INN] |
| Fagpakke — teori/quiz-innhold | Din spesialitet, ingen konkurranse | [FYLL INN] |

**Prinsipp:** ikke konkurrer på pris mot et videobyrå. Konkurrer på at byrået må Google
hva vikeplikt er, og du ikke må. Feil i en trafikkvideo er pinlig for en trafikkskole —
det er det de faktisk betaler for å slippe.

---

## Statusflyt i CSV-en

```
ikke_kontaktet → arbeid_pågår → sendt → oppfølging → i_dialog → kunde
                                                  ↘ nei / ikke_nå
```

Sett `neste_steg` og en dato på hver rad. En prospektliste uten neste steg er en liste, ikke
en pipeline.

---

## Ukerytme som holder dette i live

| Dag | Oppgave | Tid |
|-----|---------|-----|
| Mandag | Velg ukens tema fra hookbanken | 15 min |
| Tirsdag–onsdag | Produser 2 videoer | 3 t |
| Torsdag | Send til 2 nye skoler | 30 min |
| Fredag | Følg opp forrige ukes utsendelser | 20 min |

Åtte skoler i måneden. Med en normal treffrate i kald utsendelse — og du leverer varmt,
ikke kaldt — er det nok til å bygge en portefølje på et halvår.
