# V6: forslag til faglig gjennomgang – stoppskilt

**Michael godkjente norsk situasjon, spørsmålstekst og fasit B for V6-utvikling 18. november 2026.** Den engelske presiseringen er innarbeidet i testversjon 1. Thai avventer kvalifisert språkkontroll. Oppgaven har kun test-ID `test-only-v6-stop-sign-v1`. Den står utenfor produksjon.

Spørsmål, alle svaralternativer og forklaringer er bundet til SHA-256 `b8cf89e2042c5deb7557078be09240ab5c60c46f35b49ec360f4dabf7e40d5ba`. Feltet `guidance_draft` inneholder egne forslag til hint ved A og C, ny forklaring og bekreftelse ved B. Ingen av disse forslagene er registrert som gjennomgått. Ved thaikontrollen er meningen med full stans, plassering rett foran linjen og vikeplikt i begge retninger avgjørende. [Nøyaktig testversjon med veiledning](../../tests/michael_v6_isolated/stop_sign_candidate_v1.json)

## Situasjon og oppgave

Situasjonen beskriver et vanlig vegkryss, ikke en planovergang. Skilt 204 «Stopp» gjelder for eleven. En stopplinje er synlig. Det er kjørende trafikk på den kryssende veien fra begge retninger. Ingen trafikklys eller politianvisning regulerer situasjonen.

### Norsk

**Spørsmål:** Du nærmer deg et vegkryss med skilt 204 «Stopp» og en stopplinje. Det kommer kjøretøy fra begge retninger på den kryssende veien. Hva gjør du?

- A. Jeg setter bare ned farten og kjører inn hvis jeg får plass.
- B. Jeg stanser helt foran og inntil stopplinjen, viker for kjøretøyene på den kryssende veien og kjører videre når det er trygt.
- C. Jeg stanser for kjøretøyet fra høyre, men kjører slik at kjøretøyet fra venstre må bremse for meg.

**Godkjent fasit for norsk utviklingsversjon:** B.

**Forklaring:** Stoppskiltet krever at du stanser helt. Her stanser du foran og inntil stopplinjen og viker for kjørende trafikk i begge retninger på den kryssende veien.

### ภาษาไทย

**คำถาม:** คุณกำลังเข้าใกล้ทางแยกที่มีป้าย 204 «หยุด» และมีเส้นหยุด มีรถวิ่งมาจากทั้งสองทิศทางบนถนนที่ตัดกัน คุณควรทำอย่างไร?

- A. ลดความเร็วเท่านั้น แล้วขับเข้าไปถ้ามีช่องว่าง
- B. หยุดรถให้สนิทก่อนถึงและชิดเส้นหยุด ให้ทางรถบนถนนที่ตัดกัน แล้วขับต่อเมื่อปลอดภัย
- C. หยุดให้รถที่มาจากทางขวา แต่ขับออกไปจนรถที่มาจากทางซ้ายต้องเบรกให้ฉัน

**คำตอบที่เสนอ:** B.

**คำอธิบาย:** ป้ายหยุดกำหนดให้หยุดรถสนิท ในสถานการณ์นี้ให้หยุดก่อนถึงและชิดเส้นหยุด และให้ทางรถบนถนนที่ตัดกันจากทั้งสองทิศทาง

### English

**Question:** You approach a road junction with sign 204, “Stop”, and a stop line. Vehicles are approaching from both directions on the crossing road. What do you do?

- A. I only slow down and enter if there is a gap.
- B. I stop completely immediately before and close to the stop line, give way to vehicles on the crossing road and continue when it is safe.
- C. I stop for the vehicle from the right but drive out so that the vehicle from the left has to brake for me.

**Proposed answer:** B.

**Explanation:** The stop sign requires a complete stop. In this situation, stop immediately before and close to the stop line and give way to traffic travelling in both directions on the crossing road.

## Kilder og kontrollpunkt

- [Skiltforskriften, Lovdata, kapittel 3 § 6, skilt 204](https://lovdata.no/forskrift/2005-10-07-1219): stopplikt og vikeplikt ved kryssende vei; beskriver også at stansen skal skje foran og inntil stopplinjen når en slik finnes.
- [Statens vegvesen: trafikkskilt, skilt 204](https://www.vegvesen.no/trafikkinformasjon/vei-og-skilt/trafikkskilt-og-henvendelser/trafikkskilt/): praktisk beskrivelse av stans og vikeplikt. Kildene ble kontrollert via søkeindeks 18. november 2026; bekreft gjeldende ordlyd på nytt før publisering.
- Dette eksemplet gjelder **en situasjon med stopplinje og kryssende vei**. Det er ikke ment som fullstendig undervisning om manglende stopplinje, planovergang, signaler, politianvisning eller andre trafikanter.
- Norsk er skrevet mot den norske kilden. Thai og engelsk er oversettelsesforslag som må kontrolleres av kvalifisert språk-/fagperson; de offisielle kildene dokumenterer ikke at oversettelsene er godkjent. Alternativbokstavene er kun utkast og kan ikke antas å være de samme etter stokking i appen.
- Ved endelig kontroll skal resultatet vise hvilken tekstversjon gjennomgangen gjelder. Test-ID-en brukes i isolert testing. En eventuell produksjonsoppgave må registreres gjennom prosjektets valideringslag.
