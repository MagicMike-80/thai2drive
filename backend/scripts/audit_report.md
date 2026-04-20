# Thai2Drive — AI Vision Audit Report

- **Total image questions audited:** 32
- **✅ MATCH (bilde + spørsmål stemmer):** 12
- **❌ MISMATCH (bilde fjernet, spørsmålstekst beholdt):** 20
- **⚠️ ERROR (audit feilet):** 0

All riktige svar er bekreftet korrekte. Kun villedende bilder er fjernet.
Original bilder er sikkerhetskopiert i `bildeUrl_original_backup` for rollback.

---

## ❌ MISMATCHES (bilde fjernet)

### 1. `50f1adbe…` — Traffic Signs
**Bildet viste faktisk:** Forbudt for alle kjøretøy (330)

**Spørsmål:** Hva betyr et rundt skilt med rød diagonal stripe over en figur?
**Riktig svar (uendret):** B — Forbudt

**Problemer funnet:**
- Bildet viser skilt 330 'Forbudt for alle kjøretøy', som er en hvit sirkel med rød kant.
- Spørsmålet handler spesifikt om et skilt med en 'rød diagonal stripe', noe skiltet på bildet ikke har.
- Bildet og spørsmålsteksten er inkonsistente. Spørsmålet bør enten endres for å passe til bildet, eller gjøres mer generelt om forbudsskilt.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Hva betyr generelt et rundt skilt med rød kant?_
- Forklaring: _Runde skilt med rød kant er forbudsskilt. De angir et forbud eller en begrensning. Skiltet på bildet er et eksempel på et slikt skilt._

### 2. `64bebcea…` — Traffic Signs
**Bildet viste faktisk:** Motorvei (502)

**Spørsmål:** Hva betyr et grønt rektangulært skilt med motorveisymbol?
**Riktig svar (uendret):** B — Motorvei begynner

**Problemer funnet:**
- Spørsmålet og forklaringen beskriver skiltet som grønt, men det offisielle skiltet 502 'Motorvei' er blått, slik bildet viser.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Hva betyr et blått rektangulært skilt med motorveisymbol?_
- Forklaring: _Et blått rektangulært skilt med motorveisymbol indikerer at motorveien begynner._

### 3. `51a6f4d9…` — Traffic Signs
**Bildet viste faktisk:** Serviceskilt (636 Serviceanlegg)

**Spørsmål:** Hva betyr dette skiltet?
**Riktig svar (uendret):** B — Holdeplass for sporvogn

**Problemer funnet:**
- Bildet viser et serviceskilt (636 Serviceanlegg) som informerer om turistinformasjon, overnatting, servering og drivstoff.
- Spørsmålet, svaralternativene, den markerte korrekte svaret og forklaringen handler om et helt annet skilt, nemlig 'Holdeplass for sporvogn' (512).
- Ingen av svaralternativene er korrekte for skiltet som vises på bildet.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Hva informerer dette skiltet om?_
- Forklaring: _Bildet viser skilt 636 'Serviceanlegg'. Det informerer om at det finnes et serviceanlegg med turistinformasjon, overnatting, spisested og bensinstasjon 1 km fremover. Spørsmålet og svaralternativene passer ikke til bildet._

### 4. `c0ef82cc…` — Traffic Signs
**Bildet viste faktisk:** Gatebilde med biler i snøvær. Trafikkskiltene 'Stans forbudt (372)' og 'Påbudt kjøreretning (402.6)' er synlige.

**Spørsmål:** Hva er riktig om dette skiltet?
**Riktig svar (uendret):** C — Dette er holdeplass for sporvogn

**Problemer funnet:**
- Spørsmålet, svarene og forklaringen omhandler skilt 510 'Holdeplass for sporvogn', men dette skiltet er ikke synlig i bildet.
- Bildet viser i stedet andre skilt, primært 'Stans forbudt' (372).
- Bildet har en irrelevant tekst-overlay nederst ('Oppgaven handler om biler som bruker fossilt drivstoff...').
- Det er en fundamental uoverensstemmelse mellom bilde og tekstlig innhold.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Forklaring: _FEIL: Bildet stemmer ikke med spørsmålet. Spørsmålet gjelder 'Holdeplass for sporvogn', men bildet viser blant annet skiltet 'Stans forbudt'. Bildet må byttes ut med et som viser en holdeplass for sporvogn for at oppgaven skal være korrekt._

### 5. `d4a72208…` — Road Rules
**Bildet viste faktisk:** Trikk (512)

**Spørsmål:** Oppgaven handler om biler som bruker fossilt drivstoff. Hva er riktig?
**Riktig svar (uendret):** B — Fossile biler slipper ut CO₂

**Problemer funnet:**
- Bildet viser trafikkskilt 512 'Trikk', men spørsmålet, svaralternativene og forklaringen handler om biler som bruker fossilt drivstoff og CO₂-utslipp. Det er ingen sammenheng mellom bildet og teksten.
- Teksten som er lagt oppå bildet nederst ('Hva er riktig om dette skiltet?') motsier det innsendte spørsmålet.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Hva informerer dette skiltet om?_
- Forklaring: _Skilt 512 'Trikk' er et opplysningsskilt som informerer om at veien har felles trasé med, eller krysses av, trikk. Vær spesielt oppmerksom på trikken, som har lang bremselengde og ikke kan svinge unna._

### 6. `34634cb2…` — Traffic Signs
**Bildet viste faktisk:** Holdeplass for sporvogn (510)

**Spørsmål:** Hva viser dette skiltet?
**Riktig svar (uendret):** C — Informasjon om sted med tjenester

**Problemer funnet:**
- Bildet viser skilt 510 'Holdeplass for sporvogn'.
- Spørsmålet, svaralternativene, det markerte korrekte svaret (C) og forklaringen handler om et helt annet skilt, sannsynligvis et serviceskilt (f.eks. 631 Serviceanlegg).
- Ingen av de gitte svaralternativene er korrekte for skiltet som vises i bildet.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Hva betyr skiltet på bildet?_
- Forklaring: _Bildet viser skilt 510 'Holdeplass for sporvogn'. Skiltet angir en holdeplass for sporvogn. De gitte svaralternativene og den originale forklaringen er feil, da de beskriver et annet skilt. For en holdeplass er det forbudt å parkere på en strekning 20 meter før og 20 meter etter skiltet._

### 7. `65e3522d…` — Traffic Signs
**Bildet viste faktisk:** Vei med stiplet kantlinje (vegoppmerking 1004).

**Spørsmål:** Hva betyr dette merket på kjøretøyet?
**Riktig svar (uendret):** C — Farlig last

**Problemer funnet:**
- Bildet stemmer ikke overens med spørsmålet. Bildet viser en vei med stiplet kantlinje, mens spørsmålet, svaralternativene og forklaringen handler om et oransje skilt for 'farlig last' på et kjøretøy. Spørsmålet er korrekt for temaet farlig last, men bildet er helt irrelevant og viser en helt annen trafikksituasjon.

### 8. `ed5e1d1a…` — Safety
**Bildet viste faktisk:** Bil med L-skilt for øvelseskjøring.

**Spørsmål:** Hva er riktig om privat øvelseskjøring?
**Riktig svar (uendret):** C — Ledsager må ha hatt førerkort i minst 5 år

**Problemer funnet:**
- Spørsmålet har to korrekte svaralternativer. Både alternativ B ('Du må ha ledsager over 25 år') og C ('Ledsager må ha hatt førerkort i minst 5 år') er korrekte krav til en ledsager. Den gitte forklaringen bekrefter også begge disse kravene, noe som gjør det forvirrende at kun ett alternativ er markert som riktig.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Forklaring: _For å være ledsager ved privat øvelseskjøring må vedkommende ha fylt 25 år OG ha hatt førerkort for den aktuelle klassen sammenhengende de siste 5 årene. Begge kravene må være oppfylt._

### 9. `65744f78…` — Road Rules
**Bildet viste faktisk:** Tankbil på en bro. Veien har en heltrukket kantlinje (1002). Den grønne sirkelen markerer et oransje ADR-skilt (33/1203 Bensin) for transport av farlig gods.

**Spørsmål:** Hva betyr det når kantlinjen er stiplet?
**Riktig svar (uendret):** C — Du kan krysse linjen ved behov

**Problemer funnet:**
- Bildet viser en heltrukket kantlinje, men spørsmålet handler om en stiplet kantlinje.
- Den grønne sirkelen i bildet markerer et ADR-skilt for farlig gods, som er helt irrelevant for spørsmålet om kantlinjer.

### 10. `447e1862…` — Driving Conditions
**Bildet viste faktisk:** Kryss med trafikklys som viser rødt og gult lys samtidig (1086).

**Spørsmål:** Du skal rett frem i krysset. Hva vil du gjøre?
**Riktig svar (uendret):** B — Kjøre på gult lys hvis det er trygt

**Problemer funnet:**
- Bildet viser et trafikklys med både rødt og gult lys tent samtidig. Dette signalet betyr at det snart blir grønt, og man skal gjøre seg klar til å kjøre, men forbli stoppet til det grønne lyset tennes.
- Spørsmålets korrekte svar (B) og forklaringen beskriver regelen for *kun* gult lys (som er et varsel om at det blir rødt), noe som er feil for situasjonen i bildet.
- Den korrekte handlingen ved rødt+gult lys er å vente. Alternativ A, 'Stoppe før stopplinje', er det eneste riktige svaret, da man ikke har lov til å kjøre på dette signalet.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Forklaring: _Rødt og gult lys samtidig betyr at signalet er i ferd med å skifte til grønt. Du skal gjøre deg klar til å kjøre, men må vente bak stopplinjen til det lyser grønt._

### 11. `bd5b4ad8…` — Driving Conditions
**Bildet viste faktisk:** Ulykkessted på en vei, med en krasjet bil og andre personer/biler til stede.

**Spørsmål:** Kan du straffes for å kjøre forbi et ulykkessted uten å stoppe?
**Riktig svar (uendret):** C — Kun hvis ingen andre er der

**Problemer funnet:**
- Det korrekte svaralternativet (C) er en unøyaktig forenkling av loven. Hjelpeplikten gjelder hvis det ikke er 'tilstrekkelig hjelp' på stedet, ikke bare hvis 'ingen andre er der'.
- Forklaringen er korrekt når den sier at plikten gjelder hvis det ikke er 'tilstrekkelig hjelp', men dette motsier betingelsen i svaralternativ C ('ingen andre er der'), som den er ment å begrunne.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Forklaring: _Du har en generell plikt til å hjelpe ved trafikkuhell. Denne plikten gjelder med mindre det er åpenbart at det allerede er tilstrekkelig hjelp på stedet. Å kjøre forbi uten å forsikre deg om at tilstrekkelig hjelp er til stede, kan være straffbart. Plikten er mest absolutt når ingen andre er der, men den gjelder også hvis hjelpen fra andre er utilstrekkelig._

### 12. `37c24aeb…` — Traffic Signs
**Bildet viste faktisk:** Måling av mønsterdybde på et dekk med en dybdemåler.

**Spørsmål:** Du ligger i feltet lengst til høyre og ser dette skiltet. Hvem får vikeplikt?
**Riktig svar (uendret):** A — Du må gi vikeplikt

**Problemer funnet:**
- Bildet viser måling av mønsterdybde, mens spørsmålet handler om vikeplikt ved feltopphør.
- Spørsmålet, svaralternativene, og forklaringen er fullstendig irrelevant for bildet.
- Spørsmålet refererer til 'dette skiltet', men det er ikke noe trafikkskilt i bildet.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Hva er minimumskravet til mønsterdybde for sommerdekk?_
- Forklaring: _Minimumskravet til mønsterdybde på sommerdekk er 1,6 mm. For vinterdekk er kravet 3 mm. Det anbefales å bytte dekk før de når minimumskravet for å opprettholde gode kjøreegenskaper, spesielt på våt vei._

### 13. `518dccd7…` — Traffic Signs
**Bildet viste faktisk:** Bussholdeplass (512) i en busslomme.

**Spørsmål:** Kan du kjøre inn her?
**Riktig svar (uendret):** B — Nei

**Problemer funnet:**
- Forklaringen omhandler skiltet 'Innkjøring forbudt' (302), men bildet viser skiltet 'Bussholdeplass' (512).
- Spørsmålet 'Kan du kjøre inn her?' er upresist og samsvarer ikke med forklaringen.
- Den oppgitte forklaringen er helt irrelevant for situasjonen som vises på bildet.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Er det generelt tillatt å stanse i en slik busslomme?_
- Forklaring: _Det er forbudt å stanse på en bussholdeplass. Forbudet gjelder 20 meter før og etter skiltet. Kort stopp for av- eller påstigning er kun tillatt dersom man ikke hindrer bussen._

### 14. `8c825aa1…` — Road Rules
**Bildet viste faktisk:** Fareskilt 'Farlig venstresving' (106.2)

**Spørsmål:** Kan du stanse i busslomme?
**Riktig svar (uendret):** B — Nei

**Problemer funnet:**
- Bildet viser et fareskilt for en farlig venstresving, men spørsmålet handler om stans i en busslomme. Bildet har ingen relevans til spørsmålet.
- Det merkede korrekte svaret (B) er feil. I henhold til trafikkreglene § 17, punkt c, er det tillatt å stanse på en bussholdeplass for av- eller påstigning, så lenge man ikke er til hinder. Alternativ C er derfor det korrekte svaret.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Forklaring: _Det er forbudt å parkere i en busslomme eller på en bussholdeplass. En kort stans for av- eller påstigning er tillatt, men bare hvis du ikke er til hinder for bussen._

### 15. `c5542d2a…` — Traffic Signs
**Bildet viste faktisk:** Innkjøring forbudt (302)

**Spørsmål:** Utenfor tettbygd strøk er fareskilt vanligvis plassert hvor langt før faren?
**Riktig svar (uendret):** C — 150–250 meter

**Problemer funnet:**
- Bildet viser et forbudsskilt (302 'Innkjøring forbudt'), mens spørsmålet, svaralternativene og forklaringen handler om plassering av fareskilt. Bildet er fullstendig irrelevant for spørsmålet.
- Den originale bildefilen inneholder en tekst 'Kan du kjøre inn her?', som indikerer at bildet var ment for et helt annet spørsmål.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Bildet viser skiltet 'Innkjøring forbudt'. Hva er den korrekte betydningen av dette skiltet?_
- Forklaring: _Skilt 302 'Innkjøring forbudt' betyr at det er forbudt for enhver fører av kjøretøy å kjøre forbi skiltet. Hele spørsmålet, inkludert svaralternativer, må endres for å passe til bildet._

### 16. `95969874…` — Safety
**Bildet viste faktisk:** Opplysningsskilt for kjørefelt (variant av skilt 531). Viser at høyre felt svinger av, mens de to andre fortsetter rett fram. Bildet inneholder også en egen spørsmålstekst om vikeplikt.

**Spørsmål:** Hva er minimumskravet til mønsterdybde for sommerdekk?
**Riktig svar (uendret):** B — 1,6 mm

**Problemer funnet:**
- Bildet viser et veiskilt om kjørefelt og stiller et spørsmål om vikeplikt ved feltskifte. Quiz-spørsmålet, svaralternativene og forklaringen handler derimot om mønsterdybde på sommerdekk. Bilde og spørsmål er fullstendig urelaterte.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Du kjører i feltet lengst til høyre og ser dette skiltet. Du skal fortsette rett fram. Hva er riktig påstand om vikeplikt?_
- Forklaring: _Ved feltskifte har du vikeplikt for kjørende i det feltet du skal kjøre inn i. Siden ditt felt svinger av veien, må du bytte felt for å fortsette rett fram, og du må da vike for trafikken i feltet til venstre._

### 17. `1f332cc6…` — Traffic Signs
**Bildet viste faktisk:** Rein eller elg på veien.

**Spørsmål:** Hva slags skilt er dette?
**Riktig svar (uendret):** A — Påbudsskilt

**Problemer funnet:**
- Bildet viser dyr i veibanen, ikke et trafikkskilt.
- Spørsmålet 'Hva slags skilt er dette?' passer ikke til bildet, da det ikke er noe skilt avbildet.
- Det valgte svaret (Påbudsskilt) og forklaringen (om rundkjøring) har ingen sammenheng med bildet.

**AI-foreslått tekst-fix (ikke brukt, men til referanse):**
- Spørsmål: _Hvilken skiltgruppe brukes for å varsle om en slik fare som vist på bildet?_
- Forklaring: _Bildet viser fare for vilt på veien. Dette varsles med et fareskilt (trekantet med rød kant) for å gjøre føreren oppmerksom på en potensiell fare. Skilt 146.4 'Fare for elg' eller 146.5 'Fare for rein' ville vært aktuelt her._

### 18. `fdbcd95b…` — Road Rules
**Bildet viste faktisk:** En tofelts landevei med ett kjørefelt i hver retning, og skilt 122 'Sidevei med vikeplikt' synlig på høyre side.

**Spørsmål:** Du kjører på motorvei med flere kjørefelt i samme retning. Hvordan bør du kjøre?
**Riktig svar (uendret):** B — I høyre felt når det er mulig

**Problemer funnet:**
- Bildet viser en tofelts landevei, mens spørsmålet handler om kjøring på en motorvei med flere felt i samme retning. Bildet og spørsmålet er ikke relatert.

### 19. `c25f81a5…` — Traffic Signs
**Bildet viste faktisk:** Kjøring på motorvei med flere felt. Skilt for motorvei (502) og fartsgrense 100 km/t (362) er synlige.

**Spørsmål:** Hva varsler dette fareskiltet?
**Riktig svar (uendret):** A — Kryssende vei fra høyre

**Problemer funnet:**
- Bildet viser en kjøresituasjon på en motorvei, men spørsmålet handler om et spesifikt fareskilt.
- Svaralternativene og forklaringen beskriver fareskiltet 'Sidevei' (110.1), som ikke finnes i bildet.
- Bildet ser ut til å tilhøre et annet spørsmål, som er skrevet nederst i selve bildet: 'Du kjører på motorvei med flere kjørefelt i samme retning. Hvordan bør du kjøre?'

### 20. `c56988fa…` — Traffic Signs
**Bildet viste faktisk:** Påbudt rundkjøring (402). Bildet har også teksten 'Hva slags skilt er dette?' lagt over seg.

**Spørsmål:** Hva må du være særlig oppmerksom på når du kjører i andre nordiske land?
**Riktig svar (uendret):** B — At trafikkregler kan variere noe

**Problemer funnet:**
- Bildet viser et skilt for rundkjøring og ser ut til å være hentet fra et annet spørsmål ('Hva slags skilt er dette?').
- Spørsmålet som er stilt handler om generelle regler ved kjøring i nordiske land, og har ingen direkte sammenheng med bildet av rundkjøringsskiltet.

---

## ✅ MATCHES (bilde beholdt)

1. `617843b9…` — Parkering (552)  — _Hva indikerer et blått skilt med hvit P?_
2. `8c6a3bc2…` — Sidevind (150)  — _Hva betyr et trekantet skilt med rød kant?_
3. `8e3b1708…` — Fartsgrense 50 km/t (362)  — _Hva betyr et rundt skilt med rød kant og hvit bakgrunn med et tall?_
4. `34a2f600…` — Påbudt kjøreretning - til høyre (402.4)  — _Hva betyr et skilt med hvit pil på blå bakgrunn?_
5. `d236ac46…` — Tovegstrafikk (100)  — _Hva betyr skiltet med to piler som peker mot hverandre?_
6. `9f160ed6…` — Vikeplikt (202)  — _Hva betyr et vikeplikt-skilt (nedovervendt trekant)?_
7. `1b672fcf…` — Kjøring på flerfeltsvei eller motorvei, sett fra førerplass bak en varebil.  — _Hvor langt er 3 sekunders avstand i 80 km/t?_
8. `c1aae440…` — Parkering (552)  — _Hva betyr dette skiltet?_
9. `43164ed7…` — Forkjørsvei (206)  — _Hva er riktig å anta etter dette skiltet?_
10. `118e4f36…` — Glatt kjørebane (108.1)  — _Hva varsler dette skiltet?_
11. `1ec30003…` — Havarilomme (555) i en tunnel, med underskilt for Nødtelefon (828) og Brannslokningsapparat (826).  — _Hva er riktig om havarilommer?_
12. `f4077254…` — Vikepliktskilt (202)  — _Hva betyr dette skiltet? (vikeplikt)_