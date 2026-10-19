"""Indekskontroll: hver innholdsrad finnes nøyaktig én gang i book_index.json. Offline, ingen DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_index.py -q
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_bildebok_preview import INDEX, PACKS, build_index  # noqa: E402
from bildebok_lookup import load_pack  # noqa: E402

PACK_ROWS = [load_pack(path)["pages"] for _, path in PACKS]
ALL_ROWS = [r for rows in PACK_ROWS for r in rows]


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    dup = [k for k, n in collections.Counter(keys).items() if n > 1]
    assert not dup, f"duplikate nøkler i book_index.json: {dup}"
    return dict(pairs)


IDX = json.loads(INDEX.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)


def test_pack_ids_are_unique_before_they_reach_the_index():
    # book_index er en dict: duplikater ville forsvunnet stille. Derfor sjekkes listen før dict.
    counts = collections.Counter(r["id"] for r in ALL_ROWS)
    assert [i for i, n in counts.items() if n > 1] == []


def test_every_content_row_is_in_the_index_exactly_once():
    ids = [r["id"] for r in ALL_ROWS]
    assert len(IDX["pages"]) == len(ids) == IDX["row_count"]
    assert set(IDX["pages"]) == set(ids)
    assert sorted(IDX["pages"]) == sorted(ids)


def test_index_has_no_rows_without_a_pack():
    assert set(IDX["pages"]) - {r["id"] for r in ALL_ROWS} == set()


def test_index_file_matches_a_fresh_build():
    assert IDX == build_index([load_pack(path) for _, path in PACKS])


def test_index_chain_visits_every_row_once_in_book_order():
    start = next(i for i, p in IDX["pages"].items() if True)
    seen, cur = [], start
    while cur:
        seen.append(cur)
        cur = IDX["pages"][cur]["next"]
        assert len(seen) <= len(IDX["pages"])
    assert len(seen) == len(IDX["pages"]) == len(set(seen))
    pages = [IDX["pages"][i]["printed_page"] for i in seen]
    assert pages == sorted(pages)


def test_unconfirmed_rows_are_flagged_without_leaking_claim_text():
    from bildebok_lookup import load_overrides, row_has_unconfirmed
    ov = load_overrides()
    for rid, entry in IDX["pages"].items():
        row = next(r for r in ALL_ROWS if r["id"] == rid)
        assert entry["has_unconfirmed"] == row_has_unconfirmed(row, ov)
        assert entry["open_question_count"] == len(row.get("open_questions", []))
        assert entry["teach_open_claims_as_rules"] is False
        assert "open_questions" not in entry  # redaksjonelle notater hører ikke hjemme i indeksen
