"""Offline-tester for Bilde-bok batch 4 (trykt s. 86-110) og skillet lovkrav / rettesnor / åpent. Ingen produksjon, ingen DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_batch4.py -q
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

PRIOR = [load_pack(p)["pages"] for _, p in PACKS[:3]]
B4 = load_pack(PACKS[3][1])
LABELS = {"lov": ("Lovkrav:", "ข้อกำหนดตามกฎหมาย:", "Legal requirement:"),
          "rettesnor": ("Rettesnor (ikke lovkrav):", "หลักคร่าว ๆ (ไม่ใช่ข้อบังคับ):", "Rule of thumb (not a legal requirement):"),
          "apent": ("Uavklart (ikke undervis som sikker regel):", "ยังไม่ยืนยัน (อย่าสอนว่าเป็นกฎที่แน่นอน):", "Unconfirmed (do not teach as a certain rule):")}


def test_batch4_is_valid_and_covers_25_pages_86_to_110():
    assert validate_pack(B4) == []
    assert {r["printed_page"] for r in B4["pages"]} == set(range(86, 111))
    assert {r["pdf_page"] for r in B4["pages"]} == set(range(81, 106))


def test_batch4_actual_language_content():
    assert language_errors(B4) == []


def test_batch4_ids_and_assets_do_not_collide_with_earlier_packs():
    rows = [r for pk in PRIOR for r in pk] + B4["pages"]
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({r["asset_id"] for r in rows}) == len(rows)


def test_batch4_questions_are_situation_based_with_two_options():
    for r in B4["pages"]:
        cq = r["check_question"]
        assert len(cq["options"]) == 2 and cq["answer"] == 0
        assert len(cq["q"]["no"].split()) >= 6, r["id"]


def test_student_text_contains_only_law_or_rule_of_thumb_never_open_claims():
    for r in B4["pages"]:
        assert len(r["points_kinds"]) == len(r["points"])
        assert set(r["points_kinds"]) <= {"lov", "rettesnor"}, r["id"]
        visible = json.dumps([r["title"], r["core_sentence"], r["points"], r["check_question"]], ensure_ascii=False)
        for c in r["michael_claims"]:
            if c["kind"] == "apent":
                for lang in ("no", "th", "en"):
                    assert c["text"][lang] not in visible, (r["id"], lang)


def test_michael_basis_has_only_law_and_rule_of_thumb_and_never_open_claims():
    for r in B4["pages"]:
        for i, lang in enumerate(("no", "th", "en")):
            for c in r["michael_claims"]:
                labelled = f"{LABELS[c['kind']][i]} {c['text'][lang]}" if c["kind"] != "apent" else None
                if c["kind"] == "apent":
                    assert c["text"][lang] not in r["michael_basis"][lang], (r["id"], lang)
                    assert c["exports_to_michael"] is False
                else:
                    assert labelled in r["michael_basis"][lang], (r["id"], lang)
            assert LABELS["apent"][i] not in r["michael_basis"][lang]


def test_every_law_claim_has_source_and_check_time():
    for r in B4["pages"]:
        for c in r["michael_claims"]:
            if c["kind"] == "lov":
                assert c["source"].startswith(("Trafikkreglene", "Skiltforskriften", "Vegtrafikkloven")), (r["id"], c["source"])
                assert c["checked_at"] == "2026-10-10"


def test_rows_with_open_claims_have_open_questions_and_are_not_labelled_as_law():
    for r in B4["pages"]:
        kinds = {c["kind"] for c in r["michael_claims"]}
        if "apent" in kinds:
            assert r["open_questions"], r["id"]


def test_rundkjoring_rows_do_not_present_unconfirmed_rules_as_law():
    by_id = {r["id"]: r for r in B4["pages"]}
    for rid in ("bb-s92b", "bb-s94", "bb-s95"):
        assert by_id[rid]["open_questions"], rid
        assert by_id[rid]["has_unconfirmed"], rid
    for rid in ("bb-s93", "bb-s94", "bb-s95"):
        assert all(k == "rettesnor" for k in by_id[rid]["points_kinds"] if k != "lov"), rid
    visible = json.dumps(by_id["bb-s92b"]["check_question"], ensure_ascii=False)
    assert "fortrinn" in visible and "Trafikken som allerede er i rundkjøringen" not in visible


def test_previously_rule_like_claims_without_source_are_now_open():
    by_id = {r["id"]: r for r in B4["pages"]}
    for rid in ("bb-s98", "bb-s104", "bb-s107", "bb-s108b"):
        assert any(c["kind"] == "apent" for c in by_id[rid]["michael_claims"]), rid
    assert "rød pil" not in json.dumps(by_id["bb-s104"]["check_question"], ensure_ascii=False)


def test_batch4_generated_files_are_current():
    o = paths("_BATCH4")
    assert o["map"].read_text(encoding="utf-8") == build_map(B4)
    text = o["approval"].read_text(encoding="utf-8")
    for r in B4["pages"]:
        assert f"| {r['id']} | `{row_hash(r)}` |" in text, r["id"]


def test_batch4_student_view_has_all_cards_per_language():
    html = build_html(B4)
    for lang in ("no", "th", "en"):
        view = html.split(f'id="v-{lang}"', 1)[1].split("</section>", 1)[0]
        assert view.count('<article class="card"') == len(B4["pages"])
    for forbidden in ("Bildebrief", "rådgiver", "image_brief", "Uavklart"):
        assert forbidden not in html


def test_michael_lookup_returns_flag_and_generic_notice_without_claim_text():
    allp = load_all_packs()
    cases = [("no", "Hva betyr vikeplikt?", "bb-s104b"), ("th", "การให้ทางหมายความว่าอะไร", "bb-s104b"),
             ("en", "How does merging work when two lanes become one?", "bb-s103"), ("no", "Hvem har vikeplikt når jeg skifter felt?", "bb-s96"),
             ("en", "Who may use a bus lane?", "bb-s99"), ("no", "Hva er en enveiskjørt gate?", "bb-s90")]
    for lang, q, rid in cases:
        hits = find_pages(q, lang, allp, 3)
        assert rid in [h["id"] for h in hits], (lang, q, [h["id"] for h in hits])
        for h in hits:
            assert h["teach_open_claims_as_rules"] is False and "open_questions" not in h
    top = next(h for h in find_pages("Hvem har vikeplikt i en rundkjøring?", "no", allp, 3) if h["id"] == "bb-s92b")
    assert top["has_unconfirmed"] and top["uncertainty_notice"] and "apent" in top["claim_kinds"]
    row = next(r for r in B4["pages"] if r["id"] == "bb-s92b")
    for c in row["michael_claims"]:
        if c["kind"] == "apent":
            assert c["text"]["no"] not in top["michael_basis"] + top["uncertainty_notice"]
