# Lukket stoppskiltpilot

Disse trinnene krever Michaels separate produksjonsgodkjenning. Ordinær spørsmålsbank og elevhistorikk inngår ikke i registreringen.

1. Kontroller kandidatens commit mot aktuell main og kjør isolasjonsjobben. Publiser først med `MICHAEL_V6_ENABLED=0`. Verifiser vanlig lærerchat og at V6-status er utilgjengelig.
2. Bekreft Michaels valgte testkonto ved eksakt, entydig ID mot en aktiv konto med eksisterende Premium-rettighet. Sett `MICHAEL_V6_PILOT_USER_ID` til denne ID-en. Behold `MICHAEL_V6_REGISTERED_ENABLED=0` og `MICHAEL_V6_GUEST_ENABLED=0`. Kontroller at signerings- og progresjonsnøklene er uavhengige og gyldige.
3. I backendens administrative miljø, kjør eksisterende validator én gang: `await michael_v6_policy.register_stop_sign(db, teacher_chat._reply_matches_language_script)`. Bruk Motor-databasen som argument. Forvent nøyaktig dokument-ID `1b98ff10-b1c5-4ef0-b603-65f531e620a4` i `michael_v6_pilot_questions`, med `pilot_open=false` ved nyregistrering. Stopp ved konflikt eller hvis oppgaven allerede er åpen. Registreringen bruker bare `$setOnInsert`.
4. Sett `MICHAEL_V6_PREMIUM_PILOT=1` og `MICHAEL_V6_ENABLED=1` ved godkjent utrulling. Verifiser at status fortsatt er lukket. Åpne til slutt med én betinget `update_one` på pilotsamlingen med filter `{"_id":"1b98ff10-b1c5-4ef0-b603-65f531e620a4","pilot_open":false}` og endring `{"$set":{"pilot_open":true}}`. Krev nøyaktig ett treff og én endring.
5. Kontroller start og en oppfølging med Michaels konto. Kontroller status fra en annen Premium-konto, gratisbruker og gjest. Bekreft vanlig chat mens piloten er åpen.

**Steng straks** med samme betingede oppdatering fra `true` til `false`. Dette kontrolleres på hver nye start og hver ny chatmelding, også i eksisterende økter. Allerede viste svar og en forespørsel som allerede har passert kontrollen kan ikke trekkes tilbake. Bekreft at en tidligere utstedt økt nå er utilgjengelig, og at vanlig chat svarer. Sett deretter `MICHAEL_V6_ENABLED=0` for varig deaktivering. Behold pilotdokumentet og økthistorikken.

Faggrunnlaget for krysset med oppmerket stopplinje er skiltforskriften, skilt 204. Elevens valg og regeltekst knyttes til Michaels godkjente NO/TH/EN-versjon. [Skiltforskriften](https://lovdata.no/forskrift/2005-10-07-1219)
