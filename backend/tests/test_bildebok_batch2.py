"""Offline-tester for Bilde-bok batch 2 (trykt s. 36-60) og den samlede indeksen. Ingen produksjon, ingen DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_batch2.py -q
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bildebok_lookup import find_page, find_pages, load_all_packs, load_pack  # noqa: E402
from build_bildebok_preview import INDEX, PACKS, build_html, build_index, build_map, paths, row_hash  # noqa: E402
from test_bildebok_pilot import language_errors  # noqa: E402
from validate_bildebok import validate_pack  # noqa: E402

PILOT = load_pack(PACKS[0][1])
B2 = load_pack(PACKS[1][1])


def test_batch2_is_valid_and_covers_25_pages_36_to_60():
    assert validate_pack(B2) == []
    assert {r["printed_page"] for r in B2["pages"]} == set(range(36, 61))
    assert {r["pdf_page"] for r in B2["pages"]} == set(range(31, 56))


def test_batch2_actual_language_content():
    assert language_errors(B2) == []


def test_batch2_ids_and_assets_do_not_collide_with_pilot():
    ids = [r["id"] for r in PILOT["pages"] + B2["pages"]]
    assets = [r["asset_id"] for r in PILOT["pages"] + B2["pages"]]
    assert len(ids) == len(set(ids)) and len(assets) == len(set(assets))


def test_batch2_questions_are_situation_based_with_two_options():
    for r in B2["pages"]:
        cq = r["check_question"]
        assert len(cq["options"]) == 2 and cq["answer"] == 0
        assert len(cq["q"]["no"].split()) >= 6, r["id"]


def test_batch2_text_is_short_and_has_michael_basis():
    for r in B2["pages"]:
        assert 1 <= len(r["points"]) <= 3
        assert all(r["michael_basis"][l].strip() for l in ("no", "th", "en"))


def test_sign_and_signal_rows_forbid_ai_drawn_symbols():
    for rid in ("bb-s53", "bb-s55", "bb-s56", "bb-s56b", "bb-s57", "bb-s59b", "bb-s60", "bb-s60b"):
        brief = next(r for r in B2["pages"] if r["id"] == rid)["image_brief"]
        assert "official" in brief.lower(), rid


def test_unconfirmed_book_claims_are_not_in_student_text():
    text = json.dumps([[r["title"], r["core_sentence"], r["points"]] for r in B2["pages"]], ensure_ascii=False)
    for banned in ("40 m", "ryggelys", "300 mill", "del 1 skal alltid"):
        assert banned not in text, banned


def test_open_questions_are_marked_where_primary_sources_were_not_read():
    by_id = {r["id"]: r for r in B2["pages"]}
    for rid in ("bb-s42", "bb-s48", "bb-s52", "bb-s55b", "bb-s60"):
        assert by_id[rid]["open_questions"], rid


def test_batch2_generated_files_are_current():
    o = paths("_BATCH2")
    assert o["map"].read_text(encoding="utf-8") == build_map(B2)
    text = o["approval"].read_text(encoding="utf-8")
    for r in B2["pages"]:
        assert f"| {r['id']} | `{row_hash(r)}` |" in text, r["id"]


def test_batch2_student_view_has_all_cards_per_language():
    html = build_html(B2)
    n = len(B2["pages"])
    for lang in ("no", "th", "en"):
        view = html.split(f'id="v-{lang}"', 1)[1].split("</section>", 1)[0]
        assert view.count('<article class="card"') == n
    for forbidden in ("Bildebrief", "rådgiver", "image_brief"):
        assert forbidden not in html


def test_book_index_chains_all_rows_in_book_order_and_matches_file():
    idx = build_index([PILOT, B2])
    assert json.loads(INDEX.read_text(encoding="utf-8")) == idx
    order = list(idx["pages"])
    assert len(order) == 29 + len(B2["pages"])
    assert order[28] == "bb-s35" and order[29] == "bb-s36"
    assert idx["pages"]["bb-s35"]["next"] == "bb-s36"
    assert idx["pages"][order[-1]]["next"] is None
    assert idx["pages"]["bb-s25"]["quiz_category"] in (None, "Safety", "Road Rules")


def test_all_packs_lookup_finds_batch2_rows_in_three_languages():
    allp = load_all_packs()
    cases = [("no", "Hva er mønsterdybde på vinterdekk?", "bb-s41"), ("th", "ความลึกดอกยางหน้าหนาวขั้นต่ำเท่าไร", "bb-s41"),
             ("en", "What does a solid yellow line mean?", "bb-s51b"), ("no", "Hva betyr rødt og gult lys samtidig?", "bb-s55b"),
             ("th", "ไฟแดงและเหลืองพร้อมกันหมายความว่าอย่างไร", "bb-s55b"), ("en", "How does the police arm raised signal work?", "bb-s58b")]
    for lang, q, rid in cases:
        hits = [h["id"] for h in find_pages(q, lang, allp, 3)]
        assert rid in hits, (lang, q, hits)
