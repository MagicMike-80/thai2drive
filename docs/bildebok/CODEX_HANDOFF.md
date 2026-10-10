# Bilde-bok pilot (trykt s. 11–35) — byggepakke til Codex

**Deep eier struktur og innhold. Codex eier teknisk gjennomføring.** Følg pakken og eksisterende arkitektur. Ikke planlegg på nytt. Ved et reelt hinder: beskriv problemet og den minste nødvendige løsningen i `docs/bildebok/HINDRINGER.md`, og fortsett med resten.

## 0. Regler som gjelder (CLAUDE.md)
- Web-first, kun webappen. Rør **ikke** Stripe, auth, premium, kvote, produksjons-DB eller mobil/Android.
- Språkrenhet: norsk, thai og engelsk er 100 % adskilt. Ingen fallback mellom språk.
- Webappens utseende er godkjent. Bilde-boka skal være en ny seksjon, ikke en redesign.
- `backend/teacher_chat.py` har ukommitterte endringer fra andre økter. Les `git diff` først og legg til små endringer, ikke overskriv.
- Aldri commit `.env`, `.claude/settings.local.json`, `context/FEATURES.md`. Ikke commit `output/bildebok/pages/` (skannede bokssider).
- `pytest` uten filbane kjører mot produksjon. Bruk bare navngitte testfiler under.

## 0b. Tilleggsregler fra Michael (gjelder hele oppdraget)
1. **Åpne faglige spørsmål er ikke publiseringsgodkjent.** Radene med `open_questions` (og `global_open_questions`) skal avklares mot primærkilder (Lovdata, vegvesen.no) før live, eller påstanden skal erstattes med en faglig trygg formulering. Ingen rad med uavklart påstand går live uten at dette er dokumentert i `REGELKONTROLL.md`.
2. **Dokumenterte feil kan rettes av Codex innenfor oppdraget.** Kontroller mot kilden, rett på NO, TH og EN samtidig (språkene skal si det samme og forbli adskilt), dokumenter endringen i `REGELKONTROLL.md`, oppdater `GODKJENNING.md` for berørte rader (ny hash), og fortsett. **Vesentlige endringer i omfang** (nye sider/rader, endret pedagogisk opplegg, ny funksjonalitet) avklares med Michael før de gjøres.
3. **Oppgaven «tilhenger» (`bb-s15`)** presiserer hvilke vekter som menes: bilens *tillatte totalvekt* (1800 kg) og tilhengerens *tillatte totalvekt* (1700 kg), ikke faktisk lastevekt, og at vognkortet tillater tilhengeren. Eleven skal kontrollere (a) vognkortets tillatte totalvekt for bil og henger, (b) at summen er høyst 3500 kg (eller henger høyst 750 kg), og (c) bilens tillatte hengervekt i vognkortet. Ikke forenkle spørsmålet bort fra dette.
4. **Test faktisk språkinnhold, ikke bare tegnsett.** `language_errors(...)` i `tests/test_bildebok_pilot.py` sjekker at norsk tekst ikke inneholder engelske ord, engelsk ikke norske ord, thai ikke latinske ord og at to språk ikke har identisk tekst. Bruk samme type kontroll på tekst som faktisk rendres i webappen (DOM-tekst per språk) og på Michaels svar i `test_bildebok_michael.py` og `test_bildebok_webapp.py`. En tegnsettsjekk alene er ikke nok.
5. **Hvis bildeverktøy mangler:** lever `docs/bildebok/BILDEBRIEFER_TIL_CHATGPT.md` samlet til ChatGPT (Michael limer inn), og fortsett all øvrig bygging (T2–T5) med plassholdere. Plassholdere skal aldri gå live.
6. **Kontrollpunktet beholdes (T6):** ekte bilder og elevtekst vises til faglig godkjenning før publisering. Ingen live uten notert godkjenning i `GODKJENNING.md`.

## 1. Pakken (ferdig fra Deep)
| Fil | Innhold |
|---|---|
| `backend/content_packs/bildebok/pilot_s11_s35.json` | **Kilden til sannhet.** 29 rader / 25 originalsider. Per rad: id, kapittel, avsnitt, kilde, `asset_id`/`image_file`, `title`, `core_sentence`, `points`, `michael_says`, `check_question`, `image_labels`, `image_brief`, `michael_basis`, `next_step`, `open_questions` (no/th/en der det er elevtekst) |
| `docs/bildebok/SIDEKART.md` | Endelig sidekart: innholds-ID, kapittel, avsnitt, bildefil, kilde, neste steg |
| `docs/bildebok/INNHOLD_ALLE_RADER.md` | All elevtekst NO/TH/EN, bildebrief, Michael-grunnlag og åpne faglige spørsmål per rad (til faglig godkjenning) |
| `docs/bildebok/BILDEBRIEFER_TIL_CHATGPT.md` | Alle 29 bildebriefer samlet, klare til å limes inn i ChatGPT |
| `docs/bildebok/REGELKONTROLL.md` | Regelpåstander kontrollert mot Statens vegvesen/Lovdata (9. okt 2026): hva er bekreftet, rettet eller fjernet. **Innholdet i pakken er oppdatert etter denne** |
| `docs/bildebok/GODKJENNING.md` | Godkjenningsstatus per rad med innholdshash. Uendret hash = godkjenningen beholdes |
| `docs/bildebok/RAPPORT_25_SIDER.md` | Statusrapport: én rad per side/avsnitt |
| `output/bildebok/elevvisning.html` | Referanse for layout (bilde ≥ 50 % av kortet) og tekstmengde. Kun elevstoff, alle etiketter på NO/TH/EN, ingen rådgiverstoff. Bygges av `backend/scripts/build_bildebok_preview.py` |
| `backend/scripts/validate_bildebok.py` | Enkel validator (språkrenhet, 1–3 punkter, ≤ 15 ord, sidenummer, Michael-grunnlag) |
| `backend/scripts/bildebok_lookup.py` | Referanseimplementasjon av Michael-oppslaget (`find_pages`) |
| `backend/tests/test_bildebok_pilot.py` | 19 offline-tester |

## 2. Status — bygget, testet og live rapporteres hver for seg
| Område | Bygget | Testet | Live |
|---|---|---|---|
| Sidekart, elevtekst NO/TH/EN, situasjonsbaserte spørsmål, bildebriefer, Michael-grunnlag | Ja (Deep) | Ja: validator + `test_bildebok_pilot.py` (19 tester) | Nei |
| Regelkontroll mot offisielle kilder | Ja (Deep) | Se `REGELKONTROLL.md` (Lovdata ikke lesbart for to punkter) | Nei |
| Elevvisning (HTML, referanse) | Ja | Ja: 29 kort × 3 språk, ett riktig svar, ingen rådgiverstoff, lokaliserte etiketter | Nei (kun lokal fil) |
| Referanseoppslag Michael | Ja, frittstående | Ja: 9 gullcaser + 87 tittel-treff | Nei |
| 29 bilder | **Nei – Codex** | – | – |
| Seksjon i webappen | **Nei – Codex** | – | – |
| Michael koblet til kort, kildeavsnitt og elevsvar | **Nei – Codex** | – | – |
| Test mobil og desktop, 3 språk | – | **Nei – Codex** | – |
| Live | – | – | **Nei – Codex, etter godkjenning** |

## 3. Oppgaver i rekkefølge (Codex)
### T1 · Generer de 29 bildene
- Bruk `image_brief` per rad (finnes i JSON og i `INNHOLD_ALLE_RADER.md`). Filnavn = `image_file`. Fotorealistisk, norsk vei/lys, høyrekjøring, **ingen tekst i bildet** (unntatt skiltsifrene i `bb-s21`). Master 3:2 liggende. Visningen beskjærer til 4:5 (mobil) og 4:3 (desktop), så alle sentrale elementer (`image_labels` i briefen) må ligge i midten (70 % bredde, 80 % høyde). Briefen sier dette. Bruk `image_focus` (x,y i %) som `object-position`.
- Generer først `bb-s25`, `bb-s28`, `bb-s17` og kontroller stilen. Fortsett så med resten.
- Legg filene i `backend/public_assets/bildebok/`. De serveres av eksisterende rute `/api/assets/bildebok/<fil>` (`server.py`, `public_asset`). Hold hver fil under 600 KB.
- **Aksept:** 29 filer finnes med eksakt `image_file`-navn; **ingen faglig skadelig beskjæring**: i 4:5 og 4:3 er alle `image_labels`-elementene og faren/situasjonen fortsatt synlige (kontroller hvert bilde i begge formater og logg i `BILDE_KONTROLL.md`); ingen lesbar tekst; riktige aktører og høyrekjøring per brief; sjekkliste per bilde i `docs/bildebok/BILDE_KONTROLL.md`.

### T2 · Seksjon «Bilde-bok» i webappen
- Fil: `backend/studybook_web.py` (data-drevet studiebok, `install(html)` injiserer skjermen). Legg til et kapittel `BB01` og en ny leksjonstype `bookPage` i eksisterende `sbxOpen`-løkke. Les innholdet fra `pilot_s11_s35.json` ved oppstart. Ikke kopier teksten inn i koden.
- Kortet: bilde øverst (≥ 50 % av kortets høyde, `image_labels` som piller), tittel, kjernesetning, 1–3 punkter, kilde («Lærebok Klasse B · side N» på aktivt språk), og Michael-linje + kontrollspørsmål bak en utvidbar linje. Følg `output/bildebok/elevvisning.html`.
- Bruk eksisterende fremdriftslagring (`sbxReadProgress`/`sbxSaveProgress`), språkvalget i appen og «neste» fra `next_step`.
- **Aksept:** i `/api/web` → Studiebok → Bilde-bok vises 29 kort på hvert av tre språk; kun aktivt språk er i DOM-teksten; fremdrift og språk overlever sideoppdatering; eksisterende kapittel (`CH01`, `CH02`) er uendret.

### T3 · Michael AI koblet til riktig avsnitt og bilde
- Ny modul `backend/bildebok_michael.py`: flytt logikken fra `scripts/bildebok_lookup.py` (`find_pages(question, lang, k)`), uten endring i oppførsel.
- I `teacher_chat.py` (små endringer): når elevens melding og språk gir treff, legg et blokk `BOKGRUNNLAG` i system-prompten med radens `michael_basis[lang]`, tittel og trykt side, kun på elevens språk. Michael svarer på elevens språk og kan si «se Lærebok Klasse B, side N».
- Bildet vises kun der eksisterende pedagogikk tillater det (appens trinnregel: ingen bilde før trinn 5). Bruk eksisterende `media`-felt og tagformatet `[image: /api/assets/bildebok/<fil> | no | th | en]` fra `_safe_image_tag_part`/`media`-flyten. Ikke finn på nye ID-er.
- **Kort og elevsvar:** når eleven åpner Michael fra et kort, send skjult kontekst `<book_context>` (rad-ID, valgt svar og riktig svar fra `check_question`) til `/api/teacher/chat`, etter samme mønster som eksisterende `<quiz_context>` («Spør Michael» i quiz). Michael forklarer ut fra radens `michael_basis[lang]`, nevner kilden («Lærebok Klasse B, side N») og viser riktig bilde. Ved feil svar forklarer han hvorfor det riktige er riktig; ved riktig svar foreslår han `next_step`-raden.
- **Aksept:** de 9 gullcasene under gir riktig rad-ID og bilde i Michaels svar (`media`) på riktig språk; ingen treff gir uendret oppførsel; kvote/premium-logikk er urørt.

### T4 · Tester (navngitte, avgrensede, ingen produksjon)
Kjør alle tre:
```bash
cd backend && python -m pytest tests/test_bildebok_pilot.py -q
cd backend && python -m pytest tests/test_bildebok_michael.py -q     # skrives av Codex, LLM mockes
cd backend && python -m pytest tests/test_bildebok_webapp.py -q      # skrives av Codex, rendrer HTML lokalt
```
- `test_bildebok_michael.py`: for hver gullcase under, mock LLM-kallet og assert at prompten inneholder radens `michael_basis[lang]`, at `media` peker på riktig bilde, at ingen tekst fra andre språk finnes i `BOKGRUNNLAG`, og at ingen treff ikke legger til blokk.
- `test_bildebok_webapp.py`: `studybook_web.install(...)` gir HTML med `BB01`; data har 29 sider; per språk ingen thai-tegn i no/en og ingen latinske ord i thai-tittel utover tall/skiltsifre.

**Gullcaser (Michael):**
| Språk | Spørsmål | Forventet rad | Bilde |
|---|---|---|---|
| NO | Hva er promillegrensen? | bb-s25 | `bb_s25_alkohol.png` |
| TH | ขีดจำกัดแอลกอฮอล์คือเท่าไร | bb-s25 | `bb_s25_alkohol.png` |
| EN | What is the alcohol limit? | bb-s25 | `bb_s25_alkohol.png` |
| NO | Hvorfor ser barn lite bak parkerte biler? | bb-s28 | `bb_s28_barn-syn-og-lyd.png` |
| TH | ทำไมเด็กถึงมองเห็นน้อยหลังรถที่จอด | bb-s28 | `bb_s28_barn-syn-og-lyd.png` |
| EN | Why do children see less behind parked cars? | bb-s28 | `bb_s28_barn-syn-og-lyd.png` |
| NO | Hvor lang er reaksjonstiden? | bb-s23 | `bb_s23_reaksjonstid.png` |
| TH | เวลาตอบสนองคือเท่าไร | bb-s23 | `bb_s23_reaksjonstid.png` |
| EN | How long is reaction time? | bb-s23 | `bb_s23_reaksjonstid.png` |

### T5 · Konkret kontroll av elevflyt og Michael (3 språk)
For hvert av NO, TH, EN, på **mobil (375×812) og desktop (1280×800)**, på lokal server (`uvicorn server:app --port 8000`, `http://localhost:8000/api/web`), og logg resultatet i `docs/bildebok/KONTROLLRAPPORT.md` med skjermbilder:
1. Åpne Studiebok → Bilde-bok → kort 1. Bilde vises uten faglig skadelig beskjæring (sjekk kort 12, 20, 28 og 29 spesielt), alle etiketter er på valgt språk, og bildet er ≥ 50 % av kortet.
2. Svar feil og riktig på kontrollspørsmålet; tilbakemelding på riktig språk.
3. Gå til kort 12, last siden på nytt; du står på kort 12.
4. Bytt språk midt i kapittelet; samme kort, kun nytt språk i teksten.
5. Spør Michael en gullcase; svaret bruker bokgrunnlaget, viser riktig bilde og kilde.
6. DOM-sjekk i konsollen (skal gi `0`):
```js
(()=>{const lang=document.documentElement.lang;const t=document.querySelector('#sbxRoot').innerText;
const thai=/[฀-๿]/.test(t);return (lang==='th')===thai?0:1})()
```
- **Aksept:** alle 6 punkter bestått for alle 3 språk, dokumentert.

### T6 · Faglig godkjenning (Michael/rådgiver)
- Vis `elevvisning` med ekte bilder og `INNHOLD_ALLE_RADER.md`. Rådgiver godkjenner innhold som følger boken og er faglig riktig, og svarer på åpne spørsmål (`open_questions`, `global_open_questions`).
- Oppdater `GODKJENNING.md`. Endres en rad: oppdater hash, sett «venter». Bare vesentlige avvik gir ny vurdering. Uendrede rader beholder godkjenningen.
- Ikke gå videre til T7 før godkjenning er notert.

### T7 · Live innenfor godkjent omfang
Følg `AGENT_HANDOFF.md`, `DEADLINE.md` og `VERIFY.md`: branch, commit (uten hemmeligheter), deploy, bekreft versjon via `/api/web/version`, og hent produksjonsbevis. Ingen nye funksjoner utover godkjent omfang.

### T8 · Dokumentasjon til Argus
Lever `docs/bildebok/ARGUS_MELDING.md` med: omfang (25 sider, 29 rader, 29 bilder, 3 språk), lenker (webapp, bilde-URL-er), deploy-versjon, testbevis (T4 + T5), kjente mangler. Mal i seksjon 5.

## 4. Kjente mangler og uavklarte faglige spørsmål
- Åpne spørsmål per rad står i `INNHOLD_ALLE_RADER.md` og i `open_questions`. Boken er fra ca. 2010; tall er merket «bokas tall». Reglene (trinn, tider, alder, hengerregler) skal bekreftes av rådgiver.
- Globalt: (1) skal thai vise norsk fagord i parentes, slik Michaels glossarformat? Pakken viser det ikke. (2) Lisens til kommersiell bruk av boka som kilde er ikke avklart.
- «De seks rapporterte bildene» og «de tre godkjente filversjonene» er ikke funnet i repoet. Ikke gjenbruk bilder uten at Michael oppgir filnavnene. Godkjenninger beholdes per rad via hash.

## 5. Mal for Argus-melding (fylles etter live)
```
Bilde-bok pilot (Lærebok Klasse B, trykt s. 11–35 / PDF s. 6–30)
Omfang: 25 sider, 29 rader, 29 bilder, NO/TH/EN
Lenker: <webapp-lenke>, <bilde-lenker>
Versjon: <deploy-commit> / /api/web/version = <verdi>
Tester: test_bildebok_pilot (19), test_bildebok_michael (<n>), test_bildebok_webapp (<n>); kontrollrapport T5
Godkjenning: <hvem, dato>; GODKJENNING.md
Kjente mangler: <liste>
```

## 6. Batch 2 (trykt s. 36–60) — tilleggspakke, ikke blokkerende for piloten
Levert av Deep som egen pakke, uten å røre pilotens `pilot_s11_s35.json` (pilotens innhold og hasher er uendret).
Pilotens oppgaver T1–T8 går først. Batch 2 bygges inn **etter** at piloten er godkjent og live, med samme tekniske løype, og krever eget faglig kontrollpunkt.

| Fil | Innhold |
|---|---|
| `backend/content_packs/bildebok/batch2_s36_s60.json` | 39 rader / 25 originalsider (PDF-s. 31–55), NO/TH/EN, situasjonsbaserte spørsmål, bildebriefer, Michael-grunnlag, `quiz_category`, `open_questions` |
| `backend/content_packs/bildebok/book_index.json` | Samlet Michael-indeks for pilot + batch 2 i bokrekkefølge: id, side, kapittel, tittel, bildefil, `quiz_category`, `next` (global neste rad, `bb-s35` → `bb-s36`). `quiz_category` følger `normalize_categories.py` og er **ikke verifisert mot live DB** |
| `docs/bildebok/{SIDEKART,INNHOLD,RAPPORT,GODKJENNING}_BATCH2.md`, `BILDEBRIEFER_BATCH2_TIL_CHATGPT.md` | Samme dokumenttyper som for piloten |
| `docs/bildebok/REGELKONTROLL_BATCH2.md` | Regelkontroll mot Statens vegvesen/Lovdata. **Skiltforskriften, kjøretøyforskriften og N302 er ikke lest direkte** |
| `backend/tests/test_bildebok_batch2.py` | 12 offline-tester (gyldighet, språkinnhold, ingen id-/asset-kollisjon, indeks, oppslag på tre språk) |
| `output/bildebok/elevvisning_batch2.html` | Layoutreferanse (samme begrensning som pilotens: viser fasit i klientdata, ikke sikker elevsvarflyt) |

Regler for batch 2:
- **Ingen rad er publiseringsgodkjent.** Rader med `open_questions` må avklares mot primærkilde før live (se 0b.1). Særlig: lyssignal, pilsignal, politiets tegn, fareskilt-avstander, piggdekkperiode, kollektivfelt, vognkort.
- **Skilt og signaler skal ikke tegnes av KI.** Briefene for `bb-s53`, `s55`, `s56`, `s56b`, `s57`, `s59b`, `s60`, `s60b` krever offisielle skiltfiler (`Michael Trafikklærer AI materialer/traffic-signs`, bare fareskilt, påbud og vikeplikt finnes der) eller kontroll av hvert symbol mot offisielt skilt.
- `book_index.json` er et hjelpemiddel. Michael skal fortsatt bruke godkjenningsgate, kortversjon og servervalidert elevsvar (se `HINDRINGER.md`). `find_pages` er bare en referanse.
- Kjør: `cd backend && python -m pytest tests/test_bildebok_pilot.py tests/test_bildebok_batch2.py -q` (31 består).

## 7. Batch 3 (trykt s. 61–85) — tilleggspakke, ikke blokkerende for piloten
Samme regler som batch 2 (seksjon 6). Levert som egen pakke, pilotens og batch 2s innhold er uendret.

| Fil | Innhold |
|---|---|
| `backend/content_packs/bildebok/batch3_s61_s85.json` | 35 rader / 25 originalsider (PDF-s. 56–80): skiltgrupper, myndighetspyramiden, Del 4 Atferd (HAV, observasjonsteknikk og se-regler, signal og tegn, fartstilpasning, stopp- og bremselengde, veigrep, plassering og avstand) |
| `docs/bildebok/{SIDEKART,INNHOLD,RAPPORT,GODKJENNING}_BATCH3.md`, `BILDEBRIEFER_BATCH3_TIL_CHATGPT.md`, `output/bildebok/elevvisning_batch3.html` | Samme dokumenttyper |
| `docs/bildebok/REGELKONTROLL_BATCH3.md` | Regelkontroll. Bokas fartstabell for spesielle kjøretøy (60 km/t) er **utdatert og ikke brukt**; § 13 nr. 4 følges |
| `backend/tests/test_bildebok_batch3.py` | 10 offline-tester |
| `backend/content_packs/bildebok/book_index.json` | Oppdatert: pilot + batch 2 + batch 3 (`bb-s85b` er siste rad) |

Kjør: `cd backend && python -m pytest tests/test_bildebok_pilot.py tests/test_bildebok_batch2.py tests/test_bildebok_batch3.py -q` (42 består).
Åpne spørsmål (ikke publiseringsgodkjent): skiltforskriften (forbudsskiltets rekkevidde), § 2 (utrykning), § 6 nr. 2 (svinging), reaksjonstid og tre-sekundersregel som tommelfingerregler, tegn «i god tid».
