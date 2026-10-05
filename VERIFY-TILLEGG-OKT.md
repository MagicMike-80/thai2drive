# Tillegg til produksjonsverifisering — oktober 2026

Dette tillegget utfyller [VERIFY.md](VERIFY.md). Verifikatøren følger fortsatt mandatet i den filen og skiller mellom kildekode, lokale tester, deploy-status og det som faktisk er synlig i produksjon.

## Språk i webappen

- Oppgi tidspunkt, maskin, URL, metode og live commit for hver kontroll.
- Bekreft live commit med `/api/web/version` uten cache og kryssjekk mot Railway-deploymenten.
- Bruk en ny nettleserprofil når lagret språk og service worker kan påvirke resultatet.
- Kontroller synlig tekst med `document.body.innerText` etter at siden er lastet. Et søk i hele SPA-responsen teller også skjulte oversettelser og er ikke bevis på synlig språklekkasje.
- Kontroller rå HTML separat når spørsmålet gjelder hva som vises før JavaScript kjører. Skill server-rendret tekst fra strenger i JavaScript-ordbøker.
- Rot-URL-en velger språk fra cookie og `Accept-Language`; dokumenter disse verdiene når `Location` vurderes.

## Support og deploy

- Ved kontroll av chat-widgetens payload: avskjær `fetch` i nettleseren, klikk chipen og rapporter payloaden. Send ikke en test-POST til `/api/support/chat` i produksjon.
- Kontroller klageklassifisering lokalt med realistiske thailandske setninger og en vanlig setning som ikke skal eskaleres.
- Når flere patcher skal ut, vent til én Railway-deployment er ferdig og live commit er bekreftet før neste push.
- Avslutt hver uavhengige Argus-rapport med `LUKKES` eller `ÅPEN` for en navngitt commit.
