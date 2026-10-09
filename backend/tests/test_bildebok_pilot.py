"""Offline-tester for Bilde-bok-piloten (side 11-35). Rører ikke produksjon eller DB.

Kjør: cd backend && python -m pytest tests/test_bildebok_pilot.py -q
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from bildebok_lookup import find_page, find_pages, load_pack  # noqa: E402
from build_bildebok_preview import build_html, build_map, OUT_MAP, OUT_APPROVAL, row_hash  # noqa: E402
from validate_bildebok import validate_pack  # noqa: E402

PACK = load_pack()


def test_pack_is_valid():
    assert validate_pack(PACK) == []


def test_covers_25_original_pages_11_to_35():
    pages = {p["printed_page"] for p in PACK["pages"]}
    assert pages == set(range(11, 36))
    assert {p["pdf_page"] for p in PACK["pages"]} == set(range(6, 31))


def test_text_is_short_and_visual_first():
    words = [len(p["core_sentence"]["no"].split()) + sum(len(x["no"].split()) for x in p["points"]) for p in PACK["pages"]]
    assert sum(words) / len(words) < 70  # bokside er ca. 350-500 ord
    assert all(1 <= len(p["points"]) <= 3 for p in PACK["pages"])


def test_thai_in_norwegian_field_is_rejected():
    bad = copy.deepcopy(PACK)
    bad["pages"][0]["title"]["no"] = "หยุด"
    assert any("thai" in e.lower() for e in validate_pack(bad))


def test_empty_language_is_rejected():
    bad = copy.deepcopy(PACK)
    bad["pages"][0]["michael_says"]["th"] = ""
    assert validate_pack(bad) != []


def test_michael_lookup_returns_right_page_and_image():
    cases = [
        ("Hva er promillegrensen?", "no", "bb-s25"),
        ("Hvorfor ser jeg ikke barn bak parkerte biler?", "no", "bb-s28"),
        ("What is reaction time?", "en", "bb-s23"),
        ("How old must the supervisor be for private practice?", "en", "bb-s11"),
        ("ขีดจำกัดแอลกอฮอล์คือเท่าไร", "th", "bb-s25"),
        ("เด็กมองเห็นและได้ยินต่างจากผู้ใหญ่", "th", "bb-s28"),
    ]
    for question, lang, expected in cases:
        hit = find_page(question, lang, PACK)
        assert hit and hit["id"] == expected, (question, hit)
        assert hit["image_file"].endswith(".png")


def test_lookup_is_language_strict():
    hit = find_page("What is the alcohol limit?", "en", PACK)
    assert hit and hit["title"] == "Alcohol and driving"
    assert find_page("ขีดจำกัดแอลกอฮอล์คือเท่าไร", "no", PACK) is None  # thai-spørsmål mot norsk tekst: ingen fallback


def test_every_row_has_michael_basis_in_three_languages():
    for r in PACK["pages"]:
        assert all(r["michael_basis"][l].strip() for l in ("no", "th", "en")), r["id"]


def test_next_step_chain_covers_all_rows_once():
    ids = [r["id"] for r in PACK["pages"]]
    assert [r["next_step"] for r in PACK["pages"]] == ids[1:] + [None]


def test_known_uncertain_rows_are_marked_for_the_adviser():
    by_id = {r["id"]: r for r in PACK["pages"]}
    for rid in ("bb-s15", "bb-s16", "bb-s24", "bb-s28", "bb-s34"):
        assert by_id[rid]["open_questions"], rid
    assert PACK["global_open_questions"]


def test_sidekart_file_matches_pack():
    assert OUT_MAP.read_text(encoding="utf-8") == build_map(PACK)


def test_student_view_has_29_cards_per_language_with_one_correct_answer_each():
    html = build_html(PACK)
    for lang in ("no", "th", "en"):
        view = html.split(f'id="v-{lang}"', 1)[1]
        view = view.split("</section>", 1)[0]
        assert view.count('<article class="card"') == 29
        assert view.count('data-ok="1"') == 29


def test_michael_lookup_finds_every_row_by_title_in_all_languages():
    for r in PACK["pages"]:
        for lang in ("no", "th", "en"):
            hits = find_pages(r["title"][lang], lang, PACK, 3)
            assert hits and hits[0]["id"] == r["id"], (r["id"], lang)
            assert hits[0]["image_file"] == r["image_file"]


def test_check_questions_are_situation_based_and_complete_in_all_languages():
    for r in PACK["pages"]:
        cq = r["check_question"]
        assert len(cq["options"]) == 2 and cq["answer"] in (0, 1), r["id"]
        assert len(cq["q"]["no"].split()) >= 6 and cq["q"]["no"].rstrip().endswith(("?", ".")), r["id"]
        assert all(cq["q"][l].strip() for l in ("no", "th", "en")), r["id"]


def test_student_view_has_no_adviser_material_and_localised_chrome():
    html = build_html(PACK)
    for forbidden in ("Bildebrief", "rådgiver", "image_brief", "Fil:"):
        assert forbidden not in html, forbidden
    for title in ("Michaels bildebok", "หนังสือภาพของไมเคิล", "Michael's picture book"):
        assert title in html


GOLDEN = [
    ("no", "Hva er promillegrensen?", "bb-s25", "bb_s25_alkohol.png"),
    ("th", "ขีดจำกัดแอลกอฮอล์คือเท่าไร", "bb-s25", "bb_s25_alkohol.png"),
    ("en", "What is the alcohol limit?", "bb-s25", "bb_s25_alkohol.png"),
    ("no", "Hvorfor ser barn lite bak parkerte biler?", "bb-s28", "bb_s28_barn-syn-og-lyd.png"),
    ("th", "ทำไมเด็กถึงมองเห็นน้อยหลังรถที่จอด", "bb-s28", "bb_s28_barn-syn-og-lyd.png"),
    ("en", "Why do children see less behind parked cars?", "bb-s28", "bb_s28_barn-syn-og-lyd.png"),
    ("no", "Hvor lang er reaksjonstiden?", "bb-s23", "bb_s23_reaksjonstid.png"),
    ("th", "เวลาตอบสนองคือเท่าไร", "bb-s23", "bb_s23_reaksjonstid.png"),
    ("en", "How long is reaction time?", "bb-s23", "bb_s23_reaksjonstid.png"),
]


def test_golden_michael_cases_three_languages():
    for lang, question, rid, image in GOLDEN:
        hit = find_page(question, lang, PACK)
        assert hit and hit["id"] == rid and hit["image_file"] == image, (lang, question, hit and hit["id"])
        assert hit["michael_basis"] == next(r for r in PACK["pages"] if r["id"] == rid)["michael_basis"][lang]


def test_approval_table_lists_every_row_with_current_hash():
    text = OUT_APPROVAL.read_text(encoding="utf-8")
    for r in PACK["pages"]:
        assert f"| {r['id']} | `{row_hash(r)}` |" in text, f"{r['id']}: godkjenningstabell utdatert"


# ---- faktisk språkinnhold (ikke bare tegnsett) ----
import re  # noqa: E402

_EN_ONLY = {"the", "and", "you", "your", "are", "with", "must", "not", "of", "it", "if", "when", "from", "should", "can", "an"}
_NO_ONLY = {"og", "ikke", "du", "på", "til", "som", "det", "med", "har", "kan", "må", "er", "skal", "å", "hva", "eller", "når"}
_NO_BIG = _NO_ONLY | {"en", "et", "av", "fra", "ved", "om", "men", "seg", "så", "bil", "bilen", "vei", "veien", "barn", "sjåfør", "hvis", "også", "alle", "mer", "mindre", "før", "etter", "kjøring", "kjører", "bremse", "stopp", "hold", "vær", "ta", "ser", "se", "teori", "år", "timer", "dag", "natt", "ned", "opp", "fart", "farten", "tid", "tiden", "trafikk", "trafikken", "øvelseskjøring", "ledsager", "førerkort", "oppkjøring", "henger", "vognkortet", "trafikalt", "grunnkurs", "grunnleggende", "opplæring", "trinn", "antall", "biler", "vokser", "raskere", "veilengden", "ulykker", "skyldes", "menneskelig", "svikt", "fleste", "vanskeligst", "små", "kjøretøy", "mange", "føreren", "sovnet", "rattet", "utåndingsluft", "milligram", "liter", "luft", "hensyn", "ta", "blikket", "automatisk", "mot", "noe", "sidesynet", "tar", "bare", "noen", "minutter"}
_EN_BIG = _EN_ONLY | {"is", "be", "have", "has", "will", "car", "road", "child", "children", "driver", "drive", "driving", "speed", "keep", "take", "see", "look", "stop", "learner", "hours", "years", "day", "night", "more", "less", "before", "after", "all", "also", "but", "slow", "down", "traffic", "time", "practice", "supervisor", "licence", "trailer", "certificate", "test", "week", "weeks", "months", "theory", "first", "then", "we", "practise", "together", "tiredness", "sharp", "vision", "narrow", "sector", "people", "use", "white", "cane", "some", "guide", "dog", "think", "easy"}
_LATIN_OK_IN_TH = {"AM"}


def _texts(row):
    for key in ("title", "core_sentence", "michael_says", "michael_basis"):
        yield key, row[key]
    for i, p in enumerate(row["points"]):
        yield f"points[{i}]", p
    for i, l in enumerate(row["image_labels"]):
        yield f"image_labels[{i}]", l
    cq = row["check_question"]
    yield "q", cq["q"]
    for i, o in enumerate(cq["options"]):
        yield f"option[{i}]", o


def language_errors(pack):
    errs = []
    for row in pack["pages"]:
        for key, t in _texts(row):
            where = f"{row['id']}.{key}"
            no_w = set(re.findall(r"[a-zæøå]+", t["no"].lower()))
            en_w = set(re.findall(r"[a-z]+", t["en"].lower()))
            if no_w & _EN_ONLY:
                errs.append(f"{where}.no inneholder engelske ord: {sorted(no_w & _EN_ONLY)}")
            if en_w & _NO_ONLY:
                errs.append(f"{where}.en inneholder norske ord: {sorted(en_w & _NO_ONLY)}")
            for lang, words, own, other in (("no", no_w, _NO_BIG, _EN_BIG), ("en", en_w, _EN_BIG, _NO_BIG)):
                n = len(t[lang].split())
                own_hits, other_hits = len(words & own), len(words & other)
                if n >= 3 and other_hits > own_hits:
                    errs.append(f"{where}.{lang} ser ut som feil språk ({own_hits} egne / {other_hits} andre ord)")
                if n >= 6 and own_hits == 0:
                    errs.append(f"{where}.{lang} ser ikke ut som {lang}")
            latin = {w for w in re.findall(r"[A-Za-z]{2,}", t["th"]) if w not in _LATIN_OK_IN_TH}
            if latin:
                errs.append(f"{where}.th inneholder latinske ord: {sorted(latin)}")
            if len(t["no"].split()) >= 3 and (t["no"] == t["en"] or t["no"] == t["th"] or t["en"] == t["th"]):
                errs.append(f"{where}: to språk har identisk tekst")
    return errs


def test_actual_language_content_in_all_fields():
    assert language_errors(PACK) == []


def test_language_checker_catches_wrong_language_text():
    bad = copy.deepcopy(PACK)
    bad["pages"][0]["core_sentence"]["en"] = "Ta teorikurset tidlig, så henger det sammen med kjøringen."
    bad["pages"][1]["core_sentence"]["no"] = "Training has four steps and you must take one at a time."
    bad["pages"][2]["core_sentence"]["th"] = "Safety courses come near the end of training"
    errs = language_errors(bad)
    assert any("bb-s11" in e and ".en" in e for e in errs)
    assert any("bb-s12" in e and ".no" in e for e in errs)
    assert any("bb-s13" in e and ".th" in e for e in errs)
