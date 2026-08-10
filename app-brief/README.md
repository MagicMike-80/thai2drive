# app-brief/

Stafettpinnen mellom agentene i produktteamet. Her ligger beslutningsgrunnlaget som
sendes fra én rolle til den neste — ikke kode, ikke notater, kun det som skal leses
av noen andre enn den som skrev det.

## Hva som ligger her

| Fil | Skrevet av | Lest av |
|-----|------------|---------|
| `PAIN_PROFILE.md` | Agent 1 (Pain Hunter) | Agent 2 (Solution Architect) |
| `SOLUTION_PLAN.md` | Agent 2 (Solution Architect) | Agent 3 |
| `IMPLEMENTATION_REPORT.md` | Agent 3 (Code Builder) | Agent 4 |
| `QA_REPORT.md` | Agent 4 (QA Verifier) | Michael / commit- eller deploy-beslutning |

Foreløpig er Agent 1, Agent 2, Agent 3 og Agent 4 bygget.

## Hvordan stafetten løpes

Michael kjører `/pain-hunter <feilrapport>`. Skillen dispatcher `pain-hunter`-subagenten,
som har `Read`, `Grep`, `Glob` og `Write` — og bevisst **ikke** `Edit` eller `Bash`.
Den kan altså lese hele repoet og skrive profilen, men den kan fysisk ikke endre en
kildefil eller kjøre en kommando.

Deretter kjører han `/solution-architect`. Den dispatcher `solution-architect`-subagenten,
som har nøyaktig samme sperre og skriver `SOLUTION_PLAN.md`: minst to reelle alternativer,
én anbefaling med oppgitt kostnad, og en regelsjekk mot språkisolasjon, web-first og
designfrysen.

Når Michael godkjenner planen, kjører han `/code-builder`. Den dispatcher
`code-builder`-subagenten, som kan redigere kode og kjøre lokale tester, men bare innenfor
filene og grensene i `SOLUTION_PLAN.md`. Den skriver `IMPLEMENTATION_REPORT.md` til Agent 4.

Til slutt kjører han `/qa-verifier`. Den dispatcher `qa-verifier`-subagenten, som kan
lese, greppe, kjøre smale lokale verifiseringer og skrive `QA_REPORT.md`, men den kan
ikke redigere kildekode. Agent 4 avgjør om patchen er lokalt godkjent, må tilbake til
Agent 3, eller trenger manuell nettleser-/produksjons-QA før commit/deploy.

Det er hele poenget med sperren: hvert steg skal bli ferdig før neste begynner. En
detektiv som kan fikse i forbifarten slutter å etterforske i det øyeblikket den første
plausible teorien dukker opp — og en arkitekt som kan implementere, slutter å designe i
det øyeblikket den første løsningen virker. En kodebygger som kan deploye i forbifarten
slutter å verifisere før patchen faktisk er trygg.

## Arkivering

`PAIN_PROFILE.md`, `SOLUTION_PLAN.md`, `IMPLEMENTATION_REPORT.md` og `QA_REPORT.md` er
alltid **den gjeldende** saken.

Skal en ny sak behandles mens den forrige fortsatt er aktuell, skriver agenten den nye
med suffiks — `PAIN_PROFILE-<kort-slug>.md`, `SOLUTION_PLAN-<kort-slug>.md` eller
`IMPLEMENTATION_REPORT-<kort-slug>.md` eller `QA_REPORT-<kort-slug>.md` — og sier fra i
oppsummeringen, for eksempel `PAIN_PROFILE-thai-emneknagger.md`. Ingenting skal
overskrives stille. Er den gamle saken ferdig behandlet, kan den slettes manuelt.

## Hva som *ikke* hører hjemme her

- Kildekode og patcher — det er Agent 3 og framover. Agent 2 kan vise korte utdrag
  (maks ~10 linjer) for å peke på *hva* som skal endres, men aldri en ferdig patch.
- Deploy, migrering og produksjonsmuterende tester — det er Michael etter eksplisitt
  godkjenning. Agent 4 verifiserer lokalt og kan anbefale neste beslutning, men den
  deployer ikke og endrer ikke kode.
- Hemmeligheter. Agenten maskerer nøkler og tokens (`sk-***REDACTED***`) før den
  limer inn loggutdrag, men regelen gjelder alle som skriver her: ingenting fra
  `.env` inn i denne mappen.
- Løpende arbeidsnotater — de hører til i `context/`.
