"""Låst bokstruktur: 4 hoveddeler, bokas avsnittsnumre, ingen ch01-ch28. Offline, ingen DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_structure.py -q
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from bildebok_lookup import load_all_packs  # noqa: E402
from bildebok_structure import IMAGE_DIR, assign_section, build_tree_md, image_files, load_structure  # noqa: E402
from build_bildebok_preview import INDEX  # noqa: E402

S = load_structure()
ROWS = load_all_packs()["pages"]
IDX = json.loads(INDEX.read_text(encoding="utf-8"))
DOCS = Path(__file__).resolve().parents[2] / "docs" / "bildebok"
EXPECTED_PARTS = {1: "Innledning", 2: "Mennesket i trafikken", 3: "Kjøretøyet, veien og trafikkmiljøet", 4: "Atferd i trafikken"}


def test_exactly_four_locked_parts_with_booktitles_in_three_languages():
    assert {p["part"]: p["title"]["no"] for p in S["parts"]} == EXPECTED_PARTS
    for p in S["parts"]:
        assert all(p["title"][lang].strip() for lang in ("no", "th", "en"))


def test_sections_use_the_books_own_numbers():
    nos = [s["section_no"] for p in S["parts"] for s in p["sections"]]
    assert len(nos) == len(set(nos))
    for p in S["parts"]:
        for s in p["sections"]:
            assert s["section_no"].startswith(f"{p['part']}.")
    assert {"1.1", "1.2", "2.1", "2.4", "3.1", "3.2", "4.6", "4.8", "4.14"} <= set(nos)
    pages = [s["first_page"] for p in S["parts"] for s in p["sections"]]
    assert pages == sorted(pages)


def test_part_five_and_appendices_are_outside_the_locked_structure_not_silently_dropped():
    titles = " ".join(i["title"] for i in S["outside_locked_structure"]["items"])
    assert "Del 5" in titles and "Veitrafikkloven" in titles
    assert all(p["part"] <= 4 for p in S["parts"])


def test_every_lesson_row_belongs_to_exactly_one_part_and_known_section():
    known = {s["section_no"]: p["part"] for p in S["parts"] for s in p["sections"]}
    for r in ROWS:
        part, no, title = assign_section(r, S)
        assert known[no] == part, r["id"]
        e = IDX["pages"][r["id"]]
        assert (e["part"], e["section_no"], e["section_title"]) == (part, no, title)


def test_rows_stay_within_their_sections_page_range():
    firsts = sorted((s["first_page"], s["section_no"]) for p in S["parts"] for s in p["sections"])
    for r in ROWS:
        no = IDX["pages"][r["id"]]["section_no"]
        start = next(f for f, n in firsts if n == no)
        later = [f for f, n in firsts if f > start]
        assert r["printed_page"] >= start - 1, (r["id"], no)
        if later and no not in ("4.0",):
            assert r["printed_page"] <= min(later), (r["id"], no)


def test_no_28_chapter_model_in_the_bildebok_data():
    pattern = re.compile(r"\bch(0[1-9]|1\d|2[0-8])\b", re.I)
    for r in ROWS:
        assert not pattern.search(r["id"] + " " + r["asset_id"] + " " + r["image_file"]), r["id"]
        assert not re.match(r"CH\d\d", r["chapter"])
        assert r["chapter"].startswith("Del ")
    assert not pattern.search(json.dumps(IDX["pages"], ensure_ascii=False))
    assert {r["chapter"][:5] for r in ROWS} == {"Del 1", "Del 2", "Del 3", "Del 4"}


def test_each_part_has_lesson_rows_with_three_languages():
    by_part = {}
    for r in ROWS:
        by_part.setdefault(IDX["pages"][r["id"]]["part"], []).append(r)
    assert set(by_part) == {1, 2, 3, 4}
    for rows in by_part.values():
        for r in rows:
            for key in ("title", "core_sentence", "michael_says"):
                assert all(r[key][lang].strip() for lang in ("no", "th", "en")), (r["id"], key)


def test_image_collection_folder_is_the_single_place_and_is_linked_per_row():
    assert IDX["image_collection"] == "Michael Trafikklærer AI materialer/Bilder til læreboken"
    assert IDX["version"] == 2 and IDX["row_count"] == len(ROWS)
    if IMAGE_DIR.exists():
        for r in ROWS:
            assert IDX["pages"][r["id"]]["collection_images"] == image_files(r), r["id"]
        assert sum(1 for e in IDX["pages"].values() if e["collection_images"]) >= 25


def test_structure_overview_file_is_current():
    assert (DOCS / "BOKSTRUKTUR.md").read_text(encoding="utf-8") == build_tree_md(IDX, S)


def test_phase_out_of_the_old_model_is_documented_and_nothing_destructive_is_claimed():
    text = (DOCS / "UTFASING_28_KAPITLER.md").read_text(encoding="utf-8")
    for needle in ("studybook_web.py", "studiebok_chapters", "sikkerhetskopi", "ikke slettet"):
        assert needle in text, needle
    assert S["deprecated_models"][0]["name"].startswith("28-kapittel")
