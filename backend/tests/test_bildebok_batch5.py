"""Offline-tester for Bilde-bok batch 5 (trykt s. 111-126, slutten av Lærebok Klasse B). Ingen produksjon, ingen DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_batch5.py -q
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

PRIOR = [load_pack(p)["pages"] for _, p in PACKS[:4]]
B5 = load_pack(PACKS[4][1])
LABELS = {
    "lov": ("Lovkrav:", "ข้อกำหนดตามกฎหมาย:", "Legal requirement:"),
    "rettesnor": ("Rettesnor (ikke lovkrav):", "หลักคร่าว ๆ (ไม่ใช่ข้อบังคับ):", "Rule of thumb (not a legal requirement):"),
}


def test_batch5_is_valid_and_covers_pages_111_to_126():
    assert validate_pack(B5) == []
    assert {r["printed_page"] for r in B5["pages"]} == set(range(111, 127))
    assert {r["pdf_page"] for r in B5["pages"]} == set(range(106, 122))
    assert B5["scope"]["page_count"] == 16


def test_batch5_actual_language_content():
    assert language_errors(B5) == []


def test_batch5_ids_and_assets_do_not_collide():
    rows = [r for pk in PRIOR for r in pk] + B5["pages"]
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({r["asset_id"] for r in rows}) == len(rows)


def test_batch5_questions_are_situation_based_with_two_options():
    for r in B5["pages"]:
        cq = r["check_question"]
        assert len(cq["options"]) == 2 and cq["answer"] == 0
        assert len(cq["q"]["no"].split()) >= 6, r["id"]


def test_law_claims_have_source_and_time_and_open_claims_never_leak():
    for r in B5["pages"]:
        assert len(r["points_kinds"]) == len(r["points"]) and set(r["points_kinds"]) <= {"lov", "rettesnor"}
        visible = json.dumps([r["title"], r["core_sentence"], r["points"], r["check_question"], r["michael_says"]], ensure_ascii=False)
        for c in r["michael_claims"]:
            if c["kind"] == "lov":
                assert c["source"] and c["checked_at"] == "2026-10-10", r["id"]
            for i, lang in enumerate(("no", "th", "en")):
                if c["kind"] == "apent":
                    assert c["text"][lang] not in r["michael_basis"][lang] and c["text"][lang] not in visible
                    assert c["exports_to_michael"] is False
                else:
                    assert f"{LABELS[c['kind']][i]} {c['text'][lang]}" in r["michael_basis"][lang]
        assert r["has_unconfirmed"] == any(c["kind"] == "apent" for c in r["michael_claims"])


def test_book_errors_are_not_repeated_in_student_text():
    by_id = {r["id"]: r for r in B5["pages"]}
    pts = json.dumps(by_id["bb-s126"]["points"] + [by_id["bb-s126"]["core_sentence"]], ensure_ascii=False)
    assert "50 km/t" in pts and "60 km/t eller mer" not in pts and "venstre side" not in pts
    assert any(c["kind"] == "apent" and "venstre side" in c["text"]["no"] for c in by_id["bb-s126"]["michael_claims"])
    s118 = by_id["bb-s118"]
    assert not any("forbi krysset" in p["no"] for p in s118["points"])
    assert any(c["kind"] == "apent" and "forbi krysset" in c["text"]["no"] for c in s118["michael_claims"])


def test_stans_og_parkering_rows_follow_trafikkreglene_17():
    by_id = {r["id"]: r for r in B5["pages"]}
    assert "5 meter" in by_id["bb-s122"]["michael_basis"]["no"] and "§ 17 nr. 1" in by_id["bb-s122"]["michael_basis"]["no"]
    assert "20 meter" in by_id["bb-s123"]["michael_basis"]["no"] and "§ 17 nr. 2" in by_id["bb-s123"]["michael_basis"]["no"]


def test_batch5_generated_files_are_current():
    o = paths("_BATCH5")
    assert o["map"].read_text(encoding="utf-8") == build_map(B5)
    text = o["approval"].read_text(encoding="utf-8")
    for r in B5["pages"]:
        assert f"| {r['id']} | `{row_hash(r)}` |" in text, r["id"]


def test_batch5_student_view_has_all_cards_per_language():
    html = build_html(B5)
    for lang in ("no", "th", "en"):
        view = html.split(f'id="v-{lang}"', 1)[1].split("</section>", 1)[0]
        assert view.count('<article class="card"') == len(B5["pages"])
    for forbidden in ("Bildebrief", "rådgiver", "image_brief", "Uavklart"):
        assert forbidden not in html


def test_lookup_finds_batch5_rows_in_three_languages():
    allp = load_all_packs()
    cases = [("no", "Hvor er det forbudt å stanse?", "bb-s122"), ("th", "ห้ามหยุดที่ไหนบ้าง", "bb-s122"),
             ("en", "Where is parking forbidden?", "bb-s123"), ("no", "Hvem har vikeplikt når jeg rygger?", "bb-s116b"),
             ("en", "Who must yield when a bus leaves the stop?", "bb-s112"), ("th", "ใครต้องให้ทางเมื่อรถฉุกเฉินมา", "bb-s115")]
    for lang, q, rid in cases:
        assert rid in [h["id"] for h in find_pages(q, lang, allp, 3)], (lang, q)
