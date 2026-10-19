"""Skille mellom lærerbasis og redaksjonelle notater på tvers av ALLE pakker. Offline, ingen DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_safe_export.py -q
Poenget: et false-flagg alene er ikke nok. Uavklarte påstander skal fysisk ikke finnes i teksten som sendes til læreren.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bildebok_lookup import load_all_packs, load_overrides, michael_payload, row_has_unconfirmed, safe_basis  # noqa: E402
from validate_bildebok import THAI, _i18n  # noqa: E402

ALL = load_all_packs()["pages"]
OV = load_overrides()
LANGS = ("no", "th", "en")
DOCS = Path(__file__).resolve().parents[2] / "docs" / "bildebok"
EDITORIAL = re.compile(
    r"ikke bekreftet|ikke lest|utelatt|ikke tatt med|ikke brukt|Bekreft|utdatert|not confirmed|not read|omitted|out of date|not included"
    r"|ไม่ได้รับการยืนยัน|ยังไม่ได้อ่าน|ไม่ได้นำมาใส่|ล้าสมัย|ไม่ได้ใช้",
    re.I,
)


def test_no_editorial_notes_in_any_teacher_payload():
    for r in ALL:
        for lang in LANGS:
            p = michael_payload(r, lang, OV)
            m = EDITORIAL.search(p["basis"])
            assert not m, (r["id"], lang, m.group(0))


def test_open_claim_text_never_reaches_the_teacher():
    for r in ALL:
        notes = [c for c in r.get("michael_claims", []) if c["kind"] == "apent"]
        ov = OV["rows"].get(r["id"])
        if ov:
            notes = [c for c in ov["claims"] if c["kind"] == "apent"]
        for c in notes:
            for lang in LANGS:
                p = michael_payload(r, lang, OV)
                assert c["text"][lang] not in p["basis"] + p["uncertainty_notice"], (r["id"], lang)


def test_flag_comes_with_a_generic_notice_that_has_no_claim_content():
    for r in ALL:
        for lang in LANGS:
            p = michael_payload(r, lang, OV)
            assert bool(p["uncertainty_notice"]) == row_has_unconfirmed(r, OV), (r["id"], lang)
            if p["uncertainty_notice"]:
                assert p["uncertainty_notice"] == OV["notice"][lang]


def test_override_rows_exist_in_packs_and_law_has_source():
    ids = {r["id"] for r in ALL}
    assert set(OV["rows"]) <= ids
    for rid, ov in OV["rows"].items():
        for c in ov["claims"]:
            if c["kind"] == "lov":
                assert c["source"] and c["checked_at"] == "2026-10-10", (rid, c["text"]["no"][:40])
        assert ov["has_unconfirmed"] == any(c["kind"] == "apent" for c in ov["claims"])
        assert ov["editor_notes"] == [c["text"]["no"] for c in ov["claims"] if c["kind"] == "apent"]


def test_override_texts_are_in_the_right_language():
    for rid, ov in OV["rows"].items():
        for i, c in enumerate(ov["claims"]):
            errs = []
            _i18n(f"{rid}.claims[{i}]", c["text"], errs)
            assert errs == [], errs
            assert len(set(c["text"].values())) == 3
            assert not THAI.search(c["text"]["no"] + c["text"]["en"])


def test_the_nine_pilot_rows_have_a_documented_outcome_with_check_times():
    text = (DOCS / "AVKLARINGER_PILOT.md").read_text(encoding="utf-8")
    for rid in ("bb-s14b", "bb-s15", "bb-s16", "bb-s21", "bb-s23", "bb-s24", "bb-s26", "bb-s28", "bb-s34"):
        assert rid in text, rid
    assert text.count("(04:") >= 7


def test_corrections_file_is_sourced_and_timestamped():
    d = json.loads((DOCS / "RETTINGSFORSLAG_TIDLIGERE_BATCHER.json").read_text(encoding="utf-8"))
    assert len(d["proposals"]) >= 12
    ids = {r["id"] for r in ALL}
    for p in d["proposals"]:
        assert p["source_url"].startswith("http") and p["checked_at"].startswith("2026-10-10T")
        assert set(p["proposed"]) == {"no", "th", "en"}
        assert p["id"] in ids


def test_specific_corrections_are_reflected_in_safe_basis():
    by_id = {r["id"]: r for r in ALL}

    def b(rid):
        return safe_basis(by_id[rid], "no", OV)

    assert "ett år" in b("bb-s14b") and "ruspåvirk" not in b("bb-s14b")
    assert "0,3" not in b("bb-s23")
    assert "ca. 7" not in b("bb-s28") and "12–14" not in b("bb-s28")
    assert "gang- eller sykkelvei" not in b("bb-s34")
    assert "taklykt" in b("bb-s53b")
    assert "rød pil" not in b("bb-s56").lower()
    assert "kjøre videre" not in b("bb-s58b")
    assert "1. mai" not in b("bb-s42") and "300 mill" not in b("bb-s42")
