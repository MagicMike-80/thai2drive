"""Offline-tester for Bilde-bok batch 3 (trykt s. 61-85). Ingen produksjon, ingen DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_batch3.py -q
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bildebok_lookup import find_pages, load_all_packs, load_pack  # noqa: E402
from build_bildebok_preview import PACKS, build_html, build_map, paths, row_hash  # noqa: E402
from test_bildebok_pilot import language_errors  # noqa: E402
from validate_bildebok import validate_pack  # noqa: E402

PRIOR = [load_pack(p)["pages"] for _, p in PACKS[:2]]
B3 = load_pack(PACKS[2][1])


def test_batch3_is_valid_and_covers_25_pages_61_to_85():
    assert validate_pack(B3) == []
    assert {r["printed_page"] for r in B3["pages"]} == set(range(61, 86))
    assert {r["pdf_page"] for r in B3["pages"]} == set(range(56, 81))


def test_batch3_actual_language_content():
    assert language_errors(B3) == []


def test_batch3_ids_and_assets_do_not_collide_with_earlier_packs():
    rows = [r for pk in PRIOR for r in pk] + B3["pages"]
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({r["asset_id"] for r in rows}) == len(rows)


def test_batch3_questions_are_situation_based_with_two_options():
    for r in B3["pages"]:
        cq = r["check_question"]
        assert len(cq["options"]) == 2 and cq["answer"] == 0
        assert len(cq["q"]["no"].split()) >= 6, r["id"]


def test_batch3_text_is_short_and_has_michael_basis():
    for r in B3["pages"]:
        assert 1 <= len(r["points"]) <= 3
        assert all(r["michael_basis"][lang].strip() for lang in ("no", "th", "en"))


def test_outdated_or_unconfirmed_book_claims_are_not_in_student_text():
    text = json.dumps([[r["title"], r["core_sentence"], r["points"], r["check_question"]] for r in B3["pages"]], ensure_ascii=False)
    for banned in ("60 km/t for tilhenger uten bremser", "ca. 70 grader", "ca. 1 meter", "5–7 km/t", "70 %"):
        assert banned not in text, banned


def test_open_questions_where_primary_sources_were_not_read():
    by_id = {r["id"]: r for r in B3["pages"]}
    for rid in ("bb-s61", "bb-s71", "bb-s72", "bb-s75", "bb-s82", "bb-s84", "bb-s85", "bb-s85b"):
        assert by_id[rid]["open_questions"], rid


def test_sign_rows_forbid_ai_drawn_symbols():
    for rid in ("bb-s61", "bb-s61b", "bb-s62", "bb-s73", "bb-s75b", "bb-s81", "bb-s82"):
        brief = next(r for r in B3["pages"] if r["id"] == rid)["image_brief"]
        assert "official" in brief.lower(), rid


def test_batch3_generated_files_are_current():
    o = paths("_BATCH3")
    assert o["map"].read_text(encoding="utf-8") == build_map(B3)
    text = o["approval"].read_text(encoding="utf-8")
    for r in B3["pages"]:
        assert f"| {r['id']} | `{row_hash(r)}` |" in text, r["id"]


def test_batch3_student_view_has_all_cards_per_language():
    html = build_html(B3)
    for lang in ("no", "th", "en"):
        view = html.split(f'id="v-{lang}"', 1)[1].split("</section>", 1)[0]
        assert view.count('<article class="card"') == len(B3["pages"])
    for forbidden in ("Bildebrief", "rådgiver", "image_brief"):
        assert forbidden not in html


def test_all_packs_lookup_finds_batch3_rows_in_three_languages():
    allp = load_all_packs()
    cases = [("no", "Hva er reglene for avstand til forankjørende?", "bb-s84"), ("th", "ระยะห่างจากรถคันหน้ากี่วินาที", "bb-s84"),
             ("en", "What does HAV stand for in traffic?", "bb-s64b"), ("no", "Hvem har høyest myndighet i trafikken?", "bb-s63"),
             ("th", "ระยะหยุดรถคืออะไร", "bb-s76"), ("en", "How does braking distance grow with speed?", "bb-s76b")]
    for lang, q, rid in cases:
        hits = [h["id"] for h in find_pages(q, lang, allp, 3)]
        assert rid in hits, (lang, q, hits)
