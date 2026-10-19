# Indekskontroll: book_index.json mot innholdspakkene (10. oktober 2026)

## Spørsmålet
«Hvorfor har `book_index.json` 99 rader mens pakkene samlet har 103?»

## Svar
**Det stemte ikke i filen. Feilen var i min rapport, ikke i indeksen.**
- Etter batch 3 hadde pakkene 29 (pilot) + 39 (batch 2) + 35 (batch 3) = **103** rader, og indeksen hadde **103** rader. Jeg skrev «99» i oppsummeringen min ved en feil. Ingen rader manglet, og ingen rader var utelatt med vilje.
- Etter batch 4 var tallet 133. Etter batch 5 er det **152** (29 + 39 + 35 + 30 + 19). Indeksen har `row_count: 152` og 152 sider.

## Kontroll som nå ligger i testene
`backend/tests/test_bildebok_index.py` (6 tester, offline):
1. Radens id er unik i pakkene **før** den havner i indeksen (indeksen er en dict og ville fjernet duplikater uten varsel).
2. Hver innholdsrad finnes nøyaktig én gang i indeksen, og `row_count` er lik antall rader.
3. Indeksen har ingen rader som mangler i pakkene.
4. Indeksfilen er identisk med en ny bygging fra pakkene.
5. `next`-kjeden besøker alle rader nøyaktig én gang, i bokrekkefølge.
6. Hver indeksrad har `has_unconfirmed` (fra claims eller trygge overstyringer), `open_question_count` og `teach_open_claims_as_rules: false`. Redaksjonelle notater (`open_questions`) ligger ikke i indeksen.

Testen leser dessuten selve JSON-filen med duplikatdeteksjon på nøkler.

## Bevisst utelatte rader
Ingen. Hver trykt side i s. 11–126 (hele boka) har minst én rad. Sider med to avsnitt har to rader (suffiks `b`).
