# Strategic Second Pass — kvalitetsporten

De fleste stopper etter første utkast fra AI-en. Det er derfor internett er fullt
av tekst ingen leser. Denne runden er der du legger inn din egen standard, smak
og livserfaring — og der generisk AI-tekst blir avslørt.

**Regelen:** hver agent scorer sitt eget arbeid 1–5 på alle seks spørsmålene før
den leverer. Snitt under **4,0**, eller **én enkeltscore på 1–2**, betyr omskriving
før neste agent får filen.

---

## De seks spørsmålene

### 1. Er målgruppen spesifikk for min målgruppe?

Snakker teksten til de faktiske menneskene du vil nå — eller til «folk som vil ta
førerkort»? Blir budskapet for bredt, treffer det ingen.

- **5:** Du kan navngi tre virkelige personer dette er skrevet til.
- **1:** Kunne vært skrevet av hvilken som helst teoriapp i Norge.

**Thai2Drive-test:** bytt ut «thai» med «polsk» i teksten. Fungerer den fortsatt
like godt? Da er den ikke spesifikk nok.

### 2. Er smerten akutt?

Er dette et problem kunden kjenner på **nå**, eller noe hen kanskje burde bry seg om?
Folk handler på det som gjør vondt i dag.

- **5:** Kunden har tenkt på dette denne uka.
- **1:** «Det hadde jo vært greit å ha førerkort en gang.»

### 3. Er løftet troverdig?

Overselger vi? Er det tomme superlativer her?

- **5:** Løftet er konkret nok til å kunne motbevises, og holder likevel.
- **1:** «Bestå garantert!» / «Revolusjonerende AI!»

**Hard grense:** vi lover aldri bestått prøve. Det kontrollerer vi ikke.

### 4. Trekker lead magneten faktisk kunden videre?

En gratis PDF som er en blindvei er verre enn ingenting — den bruker opp
oppmerksomheten uten å gi noe tilbake.

- **5:** Den løser ett ekte problem, og neste steg er den åpenbare fortsettelsen.
- **1:** Nedlastbar, men leder ingen steder.

### 5. Tjener dette penger?

Fundamentet. Er dette koblet til oppmerksomhet, leads, salg eller leverage?
Hvis ikke, er det underholdning.

- **5:** Du kan tegne veien fra denne teksten til en betaling.
- **1:** «Bra for merkevaren.»

### 6. Høres det interessant ut?

Stopper noen opp for dette i en travel hverdag? Kjedelig og sant taper mot
interessant og sant hver gang.

- **5:** Du ville sendt det videre til en kollega.
- **1:** Korrekt, men du orker ikke lese det selv.

---

## Scorekort

Kopier denne inn nederst i hver output-fil:

```markdown
## Strategic Second Pass

| # | Spørsmål | Score | Begrunnelse |
|---|----------|-------|-------------|
| 1 | Målgruppe spesifikk | /5 | |
| 2 | Smerten akutt | /5 | |
| 3 | Løftet troverdig | /5 | |
| 4 | Lead magnet trekker videre | /5 | |
| 5 | Tjener penger | /5 | |
| 6 | Høres interessant ut | /5 | |

**Snitt:** X,X — **Svakeste ledd:** #N
**Hva jeg ville fikset først:** ...
```

Begrunnelsen er ikke pynt. En score uten begrunnelse er en gjetning, og
en agent som gir seg selv 5/5 over hele linja har som regel ikke lest kritisk.

---

## Michael-passet (etter agentene)

Til slutt, det agentene ikke kan gjøre for deg:

- [ ] Har jeg faktisk hørt en elev si dette?
- [ ] Ville jeg sagt dette høyt i et klasserom?
- [ ] Ville jeg vært stolt av at en kollega så dette?
- [ ] Er det respektfullt mot noen som allerede har strøket to ganger?

Ett nei her overstyrer alle seks scorene.
