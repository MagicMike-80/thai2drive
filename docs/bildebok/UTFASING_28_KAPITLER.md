# Utfasing av 28-kapittelmodellen (CH01–CH28) — 20. oktober 2026

## Hva er gjort
- **Bildebokas datamodell** har aldri brukt ch01–ch28 og er nå låst til **4 hoveddeler** med bokas egne avsnittsnumre: `backend/content_packs/bildebok/book_structure.json`. Hver leksjonsrad får `part`, `section_no` og `section_title` i `book_index.json` (versjon 2), og indeksen peker på den samlede bildemappen `Michael Trafikklærer AI materialer/Bilder til læreboken`.
- Oversikt: [BOKSTRUKTUR.md](BOKSTRUKTUR.md). Tester: `backend/tests/test_bildebok_structure.py` (ingen ch-ider, alle rader i nøyaktig én del og ett kjent avsnitt).

## Hva som fortsatt finnes (ikke slettet)
Den gamle 28-kapittelmodellen er live og brukes av webappen. Den ligger i:
- `backend/studybook_web.py` (CH01–CH28, `_CH28_PLACEHOLDERS`, `CH28_LESSONS` m.fl.)
- MongoDB-samlingen `studiebok_chapters` (`/api/studiebok`, `seed_studiebok`-kode i `backend/server.py` og `backend/seed_studiebok.py`)
- `backend/content_packs/studiebok_i18n*.json` (oversettelser kapittel 2–15)
- 28 hovedbilder (commit 9821b3f)

**Dette er ikke slettet.** Å fjerne det betyr å slette produksjonsdata og endre en fil som Codex bygger videre på. Det krever:
1. Eget oppdrag fra Michael og eier Anti (backend/database).
2. **Sikkerhetskopi** av `studiebok_chapters` før noe røres, og rollback-plan.
3. At Bilde-bok-seksjonen (BB01 …) er live og godkjent først, slik at elever ikke står uten studiebok.
4. At innhold som bare finnes i gamle kapitler (f.eks. lovkapittelet CH28) er flyttet eller bevisst droppet.

## Foreslått rekkefølge (krever godkjenning)
1. Bilde-bok live og godkjent for de 4 delene.
2. Skjul gamle kapitler i webappen bak et flagg (ingen datasletting).
3. Eksporter og arkiver `studiebok_chapters` (sikkerhetskopi, sjekksum).
4. Slett koden (`CH01–CH28`) og DB-samlingen etter at Anti har godkjent.

## Beslutninger som trengs
- **Del 5 (Bilføreransvaret, s. 158–173)** og vedleggene (Trafikkreglene, skilt, veioppmerking, lyssignaler, Veitrafikkloven) finnes i boka, men er ikke blant de 4 låste delene. De ligger som «utenfor låst struktur» uten rader til du velger.
- «Del 2 Lærebok B.pdf» starter på trykt side 100, så den er andre halvdel av samme bok (s. 100–173) og ikke «Del 2 Mennesket i trafikken». Det er derfor s. 127–173 (resten av Del 4 og Del 5) som gjenstår der.
