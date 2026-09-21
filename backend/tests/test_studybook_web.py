"""Offline contracts for the interactive, web-only Studybook prototype."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

from studybook_web import (
    ASSETS, COPY, CSS, LESSONS, SCREEN, SCRIPT, install,
    CH03_ASSETS, CH03_LESSONS,
    CH04_ASSETS, CH04_LESSONS,
    CH05_ASSETS, CH05_LESSONS,
    CH06_ASSETS, CH06_LESSONS,
    CH07_ASSETS, CH07_LESSONS,
    CH08_ASSETS, CH08_LESSONS,
    CH09_ASSETS, CH09_LESSONS,
    CH10_ASSETS, CH10_LESSONS,
    CH11_ASSETS, CH11_LESSONS,
    CH12_ASSETS, CH12_LESSONS,
    CH13_ASSETS, CH13_LESSONS,
    CH14_ASSETS, CH14_LESSONS,
    CH15_ASSETS, CH15_LESSONS,
    CH16_ASSETS, CH16_LESSONS,
    CH17_ASSETS, CH17_LESSONS,
    CH18_ASSETS, CH18_LESSONS,
    CH19_ASSETS, CH19_LESSONS,
    CH20_ASSETS, CH20_LESSONS,
    CH21_ASSETS, CH21_LESSONS,
    CH22_ASSETS, CH22_LESSONS,
    CH23_ASSETS, CH23_LESSONS,
    CH24_ASSETS, CH24_LESSONS,
    CH25_ASSETS, CH25_LESSONS,
    CH26_ASSETS, CH26_LESSONS,
    CH27_ASSETS, CH27_LESSONS,
    CH28_ASSETS, CH28_LESSONS,
    CHAPTERS,
)
from webapp import WEBAPP_HTML, webapp_router


app = FastAPI()
app.include_router(webapp_router, prefix="/api")
client = TestClient(app)


def _walk_i18n(value, path="root"):
    if isinstance(value, dict):
        keys = set(value)
        if keys.intersection({"no", "th", "en"}):
            assert keys == {"no", "th", "en"}, (path, keys)
            assert all(isinstance(value[lang], str) and value[lang].strip() for lang in ("no", "th", "en")), path
            return
        for key, nested in value.items():
            _walk_i18n(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _walk_i18n(nested, f"{path}[{index}]")


def test_lesson_model_has_all_required_interactions():
    assert len(LESSONS) == 15
    assert [lesson["id"] for lesson in LESSONS] == [
        "intro", "look-far", "spot-four", "move-eyes", "hidden-danger",
        "road-check-1", "see-understand-act", "read-clue", "predict-next",
        "too-close", "two-cars", "speed-changes", "safety-margin",
        "road-check-2", "chapter-complete",
    ]
    assert {lesson["type"] for lesson in LESSONS} == {
        "intro", "choice", "spotHazard", "sequence", "roadCheck", "chapterComplete"
    }
    road_checks = [lesson for lesson in LESSONS if lesson["type"] == "roadCheck"]
    assert [len(lesson["questions"]) for lesson in road_checks] == [3, 4]
    assert len({lesson["id"] for lesson in LESSONS}) == len(LESSONS)


def test_every_learner_facing_value_has_exactly_three_languages():
    _walk_i18n(COPY, "copy")
    _walk_i18n(ASSETS, "assets")
    _walk_i18n(LESSONS, "lessons")


def _language_values(value, language):
    if isinstance(value, dict):
        if set(value) == {"no", "th", "en"}:
            yield value[language]
        else:
            for nested in value.values():
                yield from _language_values(nested, language)
    elif isinstance(value, list):
        for nested in value:
            yield from _language_values(nested, language)


def test_thai_content_has_thai_script_and_no_known_no_en_leakage():
    thai = "\n".join(_language_values({"copy": COPY, "assets": ASSETS, "lessons": LESSONS}, "th"))
    assert re.search(r"[\u0E00-\u0E7F]", thai)
    allowed_brands_removed = thai.replace("THAI2DRIVE", "").replace("ROAD CHECK", "")
    forbidden = re.compile(
        r"\b(?:forrige|fortsett|oversikt|kapittel|fører|fare|bil|buss|"
        r"previous|continue|chapter|driver|hazard|traffic|learn|next)\b",
        re.IGNORECASE,
    )
    assert not forbidden.search(allowed_brands_removed)


def test_strict_language_lookup_has_no_cross_language_fallback():
    assert "var text=value[appLang]" in SCRIPT
    assert "typeof text==='string'?text:''" in SCRIPT
    forbidden = [
        r"\|\|\s*(?:UI|TR|SBX_DATA)[\[\.]",
        r"\.(?:no|th|en)\s*\|\|",
        r"\[['\"](?:no|th|en)['\"]\]\s*\|\|",
        r"appLang\s*===\s*['\"]th['\"].*appLang\s*===\s*['\"]en['\"]",
    ]
    for pattern in forbidden:
        assert not re.search(pattern, SCRIPT), pattern


def test_progress_is_local_and_does_not_call_auth_billing_or_database():
    assert "t2d_studybook_progress_v1" in SCRIPT
    assert "_ls.get(SBX_KEY)" in SCRIPT
    assert "_ls.set(SBX_KEY" in SCRIPT
    assert "localStorage" not in SCRIPT
    for forbidden in ("/api/auth", "stripe", "revenuecat", "fetch(", "/api/progress"):
        assert forbidden not in SCRIPT.lower()
    assert "version:2" in SCRIPT
    assert "roadChecks" in SCRIPT


def test_asset_manifest_has_production_brief_for_every_visual_page():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(ASSETS) == 12
    assert len({asset["asset_id"] for asset in ASSETS.values()}) == 12
    for asset in ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})


def test_permanent_image_ids_and_risk_sources():
    expected_ids = [f"CH01-BLIKK-{i:03d}" for i in range(1, 13)]
    actual_ids = [asset["asset_id"] for asset in ASSETS.values()]
    assert actual_ids == expected_ids
    for asset in ASSETS.values():
        assert asset["camera_angle"] and isinstance(asset["camera_angle"], str)
        assert asset["risk_source"] and isinstance(asset["risk_source"], str)
        assert asset["risikokilde"] == asset["risk_source"]
        assert isinstance(asset["hotspots"], list)


def test_image_pairs_engine_contracts():
    # Side 9-10 pair
    assert ASSETS["too_close"]["pair_asset"] == "split"
    assert ASSETS["split"]["pair_asset"] == "too_close"
    assert ASSETS["too_close"]["asset_id"] == "CH01-BLIKK-009"
    assert ASSETS["split"]["asset_id"] == "CH01-BLIKK-010"

    # Side 11-12 pair
    assert ASSETS["speed"]["pair_asset"] == "margin"
    assert ASSETS["margin"]["pair_asset"] == "speed"
    assert ASSETS["speed"]["asset_id"] == "CH01-BLIKK-011"
    assert ASSETS["margin"]["asset_id"] == "CH01-BLIKK-012"

    # Non-paired assets have empty pair_asset
    for key in ("intro", "look_far", "hazards", "gaze", "hidden", "process", "wheels", "predict"):
        assert ASSETS[key]["pair_asset"] == ""

    # UI engine contracts in SCRIPT and CSS without page reload
    assert "sbx-pair-toggle" in SCRIPT
    assert "sbx-pair-btn" in SCRIPT
    assert "whatChanged" in SCRIPT
    assert "originalView" in SCRIPT
    assert "location.reload" not in SCRIPT
    assert ".sbx-pair-toggle" in CSS
    assert ".sbx-pair-btn" in CSS


def test_hotspot_and_chapter_completion_contracts():
    spot = next(lesson for lesson in LESSONS if lesson["id"] == "spot-four")
    assert len(spot["hazards"]) == 4
    assert "sbxState.found.length===l.hazards.length" in SCRIPT
    assert "chapterComplete" in SCRIPT
    assert "15 / 15" in str(LESSONS[-1]["title"])


def test_accessibility_and_responsive_contracts():
    assert 'aria-live="polite"' in SCREEN
    assert "if(t==='button')e.type='button'" in SCRIPT
    assert "aria-label" in SCRIPT and "i.alt=sbxL(a.alt)" in SCRIPT
    assert ":focus-visible" in CSS
    assert "@media(max-width:420px)" in CSS
    assert "@media(min-width:900px)" in CSS
    assert "prefers-reduced-motion" in CSS


def test_install_replaces_legacy_screen_once_and_preserves_other_features():
    rendered = install(WEBAPP_HTML)
    assert rendered.count('id="screenStudybook"') == 1
    assert rendered.count('id="sbxRoot"') == 1
    assert 'id="screenForbikjoring"' in rendered
    assert 'id="screenTeacher"' in rendered
    assert "renderStudybook" in rendered
    assert "studybook-mode" in rendered
    assert "classList.toggle('studybook-mode', tab === 'studybook')" in rendered
    assert 'id="bnStudybook" onclick="openStudybookChapter()"' in rendered
    assert "function openStudybookChapter()" in rendered
    assert "showTab('studybook');" in rendered
    assert "if (tab === 'studybook') loadStudiebok();" in rendered


def test_real_web_route_contains_the_prototype():
    response = client.get("/api/web")
    assert response.status_code == 200
    assert response.text.count('id="screenStudybook"') == 1
    assert "t2d_studybook_progress_v1" in response.text
    assert "spotHazard" in response.text
    assert "chapter-complete" in response.text
    assert "road-check-2" in response.text
    assert "ROAD CHECK" in response.text


def test_assets_are_centralized_and_files_exist():
    assets_root = Path(__file__).resolve().parents[1] / "public_assets"
    for asset in ASSETS.values():
        prefix = "/api/assets/"
        assert asset["src"].startswith(prefix)
        assert (assets_root / asset["src"][len(prefix):]).is_file(), asset["src"]


def test_generated_javascript_parses_in_node():
    node = shutil.which("node")
    assert node, "Node is required for the Studybook JavaScript syntax test"
    result = subprocess.run(
        [node, "--check", "-"],
        input=SCRIPT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_chapter_4_structure_and_screen_ids():
    assert len(CH04_LESSONS) == 6
    assert [lesson["id"] for lesson in CH04_LESSONS] == [
        "CH04-001", "CH04-002", "CH04-003", "CH04-004", "CH04-005", "CH04-006"
    ]
    assert {lesson["type"] for lesson in CH04_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH04_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH04-004"
    assert rc["road_check_id"] == "CH04-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH04_LESSONS}) == 6


def test_chapter_4_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH04_ASSETS) == 8
    expected_ids = {
        "CH04-DID-001", "CH04-DID-002", "CH04-PAR-001", "CH04-DID-003",
        "CH04-DID-004", "CH04-DID-005", "CH04-PAR-002", "CH04-DID-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH04_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH04_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Pugging vs POU
    assert CH04_ASSETS["ch04_did_002"]["pair_asset"] == "ch04_par_001"
    assert CH04_ASSETS["ch04_par_001"]["pair_asset"] == "ch04_did_002"
    assert CH04_ASSETS["ch04_did_002"]["asset_id"] == "CH04-DID-002"
    assert CH04_ASSETS["ch04_par_001"]["asset_id"] == "CH04-PAR-001"

    # Pair 2: Fast mal vs Tilpasset opplæring
    assert CH04_ASSETS["ch04_did_005"]["pair_asset"] == "ch04_par_002"
    assert CH04_ASSETS["ch04_par_002"]["pair_asset"] == "ch04_did_005"
    assert CH04_ASSETS["ch04_did_005"]["asset_id"] == "CH04-DID-005"
    assert CH04_ASSETS["ch04_par_002"]["asset_id"] == "CH04-PAR-002"


def test_chapter_4_assets_exist_on_disk():
    assets_root = Path(__file__).resolve().parents[1] / "public_assets"
    for asset in CH04_ASSETS.values():
        prefix = "/api/assets/"
        assert asset["src"].startswith(prefix)
        assert (assets_root / asset["src"][len(prefix):]).is_file(), asset["src"]


def test_chapter_4_i18n_and_thai_language_isolation():
    _walk_i18n(CH04_ASSETS, "ch04_assets")
    _walk_i18n(CH04_LESSONS, "ch04_lessons")

    thai = "\n".join(_language_values({"assets": CH04_ASSETS, "lessons": CH04_LESSONS}, "th"))
    assert re.search(r"[\u0E00-\u0E7F]", thai)
    allowed_brands_removed = thai.replace("THAI2DRIVE", "").replace("ROAD CHECK", "").replace("POU", "")
    forbidden = re.compile(
        r"\b(?:forrige|fortsett|oversikt|kapittel|fører|fare|bil|buss|"
        r"previous|continue|chapter|driver|hazard|traffic|learn|next)\b",
        re.IGNORECASE,
    )
    assert not forbidden.search(allowed_brands_removed)


def test_chapter_4_in_studybook_chapters_v5_json():
    json_path = Path(__file__).resolve().parents[2] / "content" / "studybook_chapters_v5.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    ch04_doc = next((ch for ch in data if ch.get("chapter_code") == "CH04" or ch.get("chapter_id") == "ch_didaktikk_laering"), None)
    assert ch04_doc is not None
    assert len(ch04_doc["screens"]) == 6
    assert [s["screen_id"] for s in ch04_doc["screens"]] == [
        "CH04-001", "CH04-002", "CH04-003", "CH04-004", "CH04-005", "CH04-006"
    ]
    assert ch04_doc["screens"][1]["pair_asset_id"] == "CH04-PAR-001"
    assert ch04_doc["screens"][4]["pair_asset_id"] == "CH04-PAR-002"
    assert ch04_doc["screens"][3]["road_check_id"] == "CH04-RC-001"


def test_chapter_3_structure_and_screen_ids():
    assert len(CH03_LESSONS) == 6
    assert [lesson["id"] for lesson in CH03_LESSONS] == [
        "CH03-001", "CH03-002", "CH03-003", "CH03-004", "CH03-005", "CH03-006"
    ]
    assert {lesson["type"] for lesson in CH03_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH03_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH03-004"
    assert rc["road_check_id"] == "CH03-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH03_LESSONS}) == 6


def test_chapter_3_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH03_ASSETS) == 8
    expected_ids = {
        "CH03-FART-001", "CH03-FART-002", "CH03-PAR-001", "CH03-FART-003",
        "CH03-FART-004", "CH03-FART-005", "CH03-PAR-002", "CH03-FART-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH03_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH03_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Våken vs distrahert fører
    assert CH03_ASSETS["ch03_fart_002"]["pair_asset"] == "ch03_par_001"
    assert CH03_ASSETS["ch03_par_001"]["pair_asset"] == "ch03_fart_002"
    assert CH03_ASSETS["ch03_fart_002"]["asset_id"] == "CH03-FART-002"
    assert CH03_ASSETS["ch03_par_001"]["asset_id"] == "CH03-PAR-001"

    # Pair 2: 3-sekundersregelen vs kort avstand
    assert CH03_ASSETS["ch03_fart_005"]["pair_asset"] == "ch03_par_002"
    assert CH03_ASSETS["ch03_par_002"]["pair_asset"] == "ch03_fart_005"
    assert CH03_ASSETS["ch03_fart_005"]["asset_id"] == "CH03-FART-005"
    assert CH03_ASSETS["ch03_par_002"]["asset_id"] == "CH03-PAR-002"


def test_chapter_5_structure_and_screen_ids():
    assert len(CH05_LESSONS) == 6
    assert [lesson["id"] for lesson in CH05_LESSONS] == [
        "CH05-001", "CH05-002", "CH05-003", "CH05-004", "CH05-005", "CH05-006"
    ]
    assert {lesson["type"] for lesson in CH05_LESSONS} == {
        "sequence", "choice", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH05_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH05-004"
    assert rc["road_check_id"] == "CH05-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH05_LESSONS}) == 6


def test_chapter_5_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH05_ASSETS) == 8
    expected_ids = {
        "CH05-TR1-001", "CH05-TR1-002", "CH05-PAR-001", "CH05-TR1-003",
        "CH05-TR1-004", "CH05-TR1-005", "CH05-PAR-002", "CH05-TR1-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH05_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH05_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Under 25 vs Over 25 år
    assert CH05_ASSETS["ch05_tr1_002"]["pair_asset"] == "ch05_par_001"
    assert CH05_ASSETS["ch05_par_001"]["pair_asset"] == "ch05_tr1_002"
    assert CH05_ASSETS["ch05_tr1_002"]["asset_id"] == "CH05-TR1-002"
    assert CH05_ASSETS["ch05_par_001"]["asset_id"] == "CH05-PAR-001"

    # Pair 2: Rød L / speil vs Bevis / ledsager
    assert CH05_ASSETS["ch05_tr1_005"]["pair_asset"] == "ch05_par_002"
    assert CH05_ASSETS["ch05_par_002"]["pair_asset"] == "ch05_tr1_005"
    assert CH05_ASSETS["ch05_tr1_005"]["asset_id"] == "CH05-TR1-005"
    assert CH05_ASSETS["ch05_par_002"]["asset_id"] == "CH05-PAR-002"


def test_chapter_6_structure_and_screen_ids():
    assert len(CH06_LESSONS) == 6
    assert [lesson["id"] for lesson in CH06_LESSONS] == [
        "CH06-001", "CH06-002", "CH06-003", "CH06-004", "CH06-005", "CH06-006"
    ]
    assert {lesson["type"] for lesson in CH06_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH06_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH06-004"
    assert rc["road_check_id"] == "CH06-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH06_LESSONS}) == 6


def test_chapter_6_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH06_ASSETS) == 8
    expected_ids = {
        "CH06-FORB-001", "CH06-FORB-002", "CH06-PAR-001", "CH06-FORB-003",
        "CH06-FORB-004", "CH06-FORB-005", "CH06-PAR-002", "CH06-FORB-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH06_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH06_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Forbudt sone vs Fri sikt
    assert CH06_ASSETS["ch06_forb_002"]["pair_asset"] == "ch06_par_001"
    assert CH06_ASSETS["ch06_par_001"]["pair_asset"] == "ch06_forb_002"
    assert CH06_ASSETS["ch06_forb_002"]["asset_id"] == "CH06-FORB-002"
    assert CH06_ASSETS["ch06_par_001"]["asset_id"] == "CH06-PAR-001"

    # Pair 2: Rygging vikeplikt vs Medhjelper i blindsone
    assert CH06_ASSETS["ch06_forb_005"]["pair_asset"] == "ch06_par_002"
    assert CH06_ASSETS["ch06_par_002"]["pair_asset"] == "ch06_forb_005"
    assert CH06_ASSETS["ch06_forb_005"]["asset_id"] == "CH06-FORB-005"
    assert CH06_ASSETS["ch06_par_002"]["asset_id"] == "CH06-PAR-002"


def test_chapter_7_structure_and_screen_ids():
    assert len(CH07_LESSONS) == 6
    assert [lesson["id"] for lesson in CH07_LESSONS] == [
        "CH07-001", "CH07-002", "CH07-003", "CH07-004", "CH07-005", "CH07-006"
    ]
    assert {lesson["type"] for lesson in CH07_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH07_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH07-004"
    assert rc["road_check_id"] == "CH07-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH07_LESSONS}) == 6


def test_chapter_7_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH07_ASSETS) == 8
    expected_ids = {
        "CH07-PARK-001", "CH07-PARK-002", "CH07-PAR-001", "CH07-PARK-003",
        "CH07-PARK-004", "CH07-PARK-005", "CH07-PAR-002", "CH07-PARK-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH07_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH07_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Skilt 370 stans forbudt vs Skilt 372 parkering forbudt
    assert CH07_ASSETS["ch07_park_002"]["pair_asset"] == "ch07_par_001"
    assert CH07_ASSETS["ch07_par_001"]["pair_asset"] == "ch07_park_002"
    assert CH07_ASSETS["ch07_park_002"]["asset_id"] == "CH07-PARK-002"
    assert CH07_ASSETS["ch07_par_001"]["asset_id"] == "CH07-PAR-001"

    # Pair 2: 5-metersregelen ved kryss vs Målepunkt fra kurve
    assert CH07_ASSETS["ch07_park_005"]["pair_asset"] == "ch07_par_002"
    assert CH07_ASSETS["ch07_par_002"]["pair_asset"] == "ch07_park_005"
    assert CH07_ASSETS["ch07_park_005"]["asset_id"] == "CH07-PARK-005"
    assert CH07_ASSETS["ch07_par_002"]["asset_id"] == "CH07-PAR-002"


def test_chapters_3_to_28_assets_exist_on_disk():
    assets_root = Path(__file__).resolve().parents[1] / "public_assets"
    for group in (
        CH03_ASSETS, CH05_ASSETS, CH06_ASSETS, CH07_ASSETS, CH08_ASSETS,
        CH09_ASSETS, CH10_ASSETS, CH11_ASSETS, CH12_ASSETS, CH13_ASSETS,
        CH14_ASSETS, CH15_ASSETS, CH16_ASSETS, CH17_ASSETS, CH18_ASSETS,
        CH19_ASSETS, CH20_ASSETS, CH21_ASSETS, CH22_ASSETS, CH23_ASSETS,
        CH24_ASSETS, CH25_ASSETS, CH26_ASSETS, CH27_ASSETS, CH28_ASSETS,
    ):
        for asset in group.values():
            prefix = "/api/assets/"
            assert asset["src"].startswith(prefix)
            assert (assets_root / asset["src"][len(prefix):]).is_file(), asset["src"]


def test_chapters_3_to_28_thai_language_isolation():
    for name, assets, lessons in [
        ("CH03", CH03_ASSETS, CH03_LESSONS),
        ("CH05", CH05_ASSETS, CH05_LESSONS),
        ("CH06", CH06_ASSETS, CH06_LESSONS),
        ("CH07", CH07_ASSETS, CH07_LESSONS),
        ("CH08", CH08_ASSETS, CH08_LESSONS),
        ("CH09", CH09_ASSETS, CH09_LESSONS),
        ("CH10", CH10_ASSETS, CH10_LESSONS),
        ("CH11", CH11_ASSETS, CH11_LESSONS),
        ("CH12", CH12_ASSETS, CH12_LESSONS),
        ("CH13", CH13_ASSETS, CH13_LESSONS),
        ("CH14", CH14_ASSETS, CH14_LESSONS),
        ("CH15", CH15_ASSETS, CH15_LESSONS),
        ("CH16", CH16_ASSETS, CH16_LESSONS),
        ("CH17", CH17_ASSETS, CH17_LESSONS),
        ("CH18", CH18_ASSETS, CH18_LESSONS),
        ("CH19", CH19_ASSETS, CH19_LESSONS),
        ("CH20", CH20_ASSETS, CH20_LESSONS),
        ("CH21", CH21_ASSETS, CH21_LESSONS),
        ("CH22", CH22_ASSETS, CH22_LESSONS),
        ("CH23", CH23_ASSETS, CH23_LESSONS),
        ("CH24", CH24_ASSETS, CH24_LESSONS),
        ("CH25", CH25_ASSETS, CH25_LESSONS),
        ("CH26", CH26_ASSETS, CH26_LESSONS),
        ("CH27", CH27_ASSETS, CH27_LESSONS),
        ("CH28", CH28_ASSETS, CH28_LESSONS),
    ]:
        _walk_i18n(assets, f"{name}_assets")
        _walk_i18n(lessons, f"{name}_lessons")

        thai = "\n".join(_language_values({"assets": assets, "lessons": lessons}, "th"))
        assert re.search(r"[\u0E00-\u0E7F]", thai), f"{name} missing Thai script"
        allowed_brands_removed = thai.replace("THAI2DRIVE", "").replace("ROAD CHECK", "").replace("POU", "")
        forbidden = re.compile(
            r"\b(?:forrige|fortsett|oversikt|kapittel|fører|fare|bil|buss|"
            r"previous|continue|chapter|driver|hazard|traffic|learn|next)\b",
            re.IGNORECASE,
        )
        assert not forbidden.search(allowed_brands_removed), f"{name} contains forbidden leak"


def test_chapter_8_structure_and_screen_ids():
    assert len(CH08_LESSONS) == 6
    assert [lesson["id"] for lesson in CH08_LESSONS] == [
        "CH08-001", "CH08-002", "CH08-003", "CH08-004", "CH08-005", "CH08-006"
    ]
    assert {lesson["type"] for lesson in CH08_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH08_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH08-004"
    assert rc["road_check_id"] == "CH08-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH08_LESSONS}) == 6


def test_chapter_8_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH08_ASSETS) == 8
    expected_ids = {
        "CH08-SKILT-001", "CH08-SKILT-002", "CH08-PAR-001", "CH08-SKILT-003",
        "CH08-SKILT-004", "CH08-SKILT-005", "CH08-PAR-002", "CH08-SKILT-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH08_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH08_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Fareskilt vs Underskilt
    assert CH08_ASSETS["ch08_skilt_002"]["pair_asset"] == "ch08_par_001"
    assert CH08_ASSETS["ch08_par_001"]["pair_asset"] == "ch08_skilt_002"
    assert CH08_ASSETS["ch08_skilt_002"]["asset_id"] == "CH08-SKILT-002"
    assert CH08_ASSETS["ch08_par_001"]["asset_id"] == "CH08-PAR-001"

    # Pair 2: Påbudsskilt vs Opplysningsskilt
    assert CH08_ASSETS["ch08_skilt_005"]["pair_asset"] == "ch08_par_002"
    assert CH08_ASSETS["ch08_par_002"]["pair_asset"] == "ch08_skilt_005"
    assert CH08_ASSETS["ch08_skilt_005"]["asset_id"] == "CH08-SKILT-005"
    assert CH08_ASSETS["ch08_par_002"]["asset_id"] == "CH08-PAR-002"


def test_chapter_9_structure_and_screen_ids():
    assert len(CH09_LESSONS) == 6
    assert [lesson["id"] for lesson in CH09_LESSONS] == [
        "CH09-001", "CH09-002", "CH09-003", "CH09-004", "CH09-005", "CH09-006"
    ]
    assert {lesson["type"] for lesson in CH09_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH09_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH09-004"
    assert rc["road_check_id"] == "CH09-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH09_LESSONS}) == 6


def test_chapter_9_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH09_ASSETS) == 8
    expected_ids = {
        "CH09-LYS-001", "CH09-LYS-002", "CH09-PAR-001", "CH09-LYS-003",
        "CH09-LYS-004", "CH09-LYS-005", "CH09-PAR-002", "CH09-LYS-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH09_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH09_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Fjernlys vs Blending
    assert CH09_ASSETS["ch09_lys_002"]["pair_asset"] == "ch09_par_001"
    assert CH09_ASSETS["ch09_par_001"]["pair_asset"] == "ch09_lys_002"
    assert CH09_ASSETS["ch09_lys_002"]["asset_id"] == "CH09-LYS-002"
    assert CH09_ASSETS["ch09_par_001"]["asset_id"] == "CH09-PAR-001"

    # Pair 2: Tåkelys forbudt kombinasjon
    assert CH09_ASSETS["ch09_lys_005"]["pair_asset"] == "ch09_par_002"
    assert CH09_ASSETS["ch09_par_002"]["pair_asset"] == "ch09_lys_005"
    assert CH09_ASSETS["ch09_lys_005"]["asset_id"] == "CH09-LYS-005"
    assert CH09_ASSETS["ch09_par_002"]["asset_id"] == "CH09-PAR-002"


def test_chapter_10_structure_and_screen_ids():
    assert len(CH10_LESSONS) == 6
    assert [lesson["id"] for lesson in CH10_LESSONS] == [
        "CH10-001", "CH10-002", "CH10-003", "CH10-004", "CH10-005", "CH10-006"
    ]
    assert {lesson["type"] for lesson in CH10_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH10_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH10-004"
    assert rc["road_check_id"] == "CH10-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH10_LESSONS}) == 6


def test_chapter_10_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH10_ASSETS) == 8
    expected_ids = {
        "CH10-RUS-001", "CH10-RUS-002", "CH10-PAR-001", "CH10-RUS-003",
        "CH10-RUS-004", "CH10-RUS-005", "CH10-PAR-002", "CH10-RUS-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH10_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH10_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Reaksjon vs Tunnelsyn
    assert CH10_ASSETS["ch10_rus_002"]["pair_asset"] == "ch10_par_001"
    assert CH10_ASSETS["ch10_par_001"]["pair_asset"] == "ch10_rus_002"
    assert CH10_ASSETS["ch10_rus_002"]["asset_id"] == "CH10-RUS-002"
    assert CH10_ASSETS["ch10_par_001"]["asset_id"] == "CH10-PAR-001"

    # Pair 2: Straff vs Ulykke
    assert CH10_ASSETS["ch10_rus_005"]["pair_asset"] == "ch10_par_002"
    assert CH10_ASSETS["ch10_par_002"]["pair_asset"] == "ch10_rus_005"
    assert CH10_ASSETS["ch10_rus_005"]["asset_id"] == "CH10-RUS-005"
    assert CH10_ASSETS["ch10_par_002"]["asset_id"] == "CH10-PAR-002"


def test_chapter_11_structure_and_screen_ids():
    assert len(CH11_LESSONS) == 6
    assert [lesson["id"] for lesson in CH11_LESSONS] == [
        "CH11-001", "CH11-002", "CH11-003", "CH11-004", "CH11-005", "CH11-006"
    ]
    assert {lesson["type"] for lesson in CH11_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH11_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH11-004"
    assert rc["road_check_id"] == "CH11-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH11_LESSONS}) == 6


def test_chapter_11_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH11_ASSETS) == 8
    expected_ids = {
        "CH11-ANSV-001", "CH11-ANSV-002", "CH11-PAR-001", "CH11-ANSV-003",
        "CH11-ANSV-004", "CH11-ANSV-005", "CH11-PAR-002", "CH11-ANSV-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH11_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH11_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Ansvarsforsikring vs Kasko
    assert CH11_ASSETS["ch11_ansv_002"]["pair_asset"] == "ch11_par_001"
    assert CH11_ASSETS["ch11_par_001"]["pair_asset"] == "ch11_ansv_002"
    assert CH11_ASSETS["ch11_ansv_002"]["asset_id"] == "CH11-ANSV-002"
    assert CH11_ASSETS["ch11_par_001"]["asset_id"] == "CH11-PAR-001"

    # Pair 2: Føreransvar vs Eieransvar
    assert CH11_ASSETS["ch11_ansv_005"]["pair_asset"] == "ch11_par_002"
    assert CH11_ASSETS["ch11_par_002"]["pair_asset"] == "ch11_ansv_005"
    assert CH11_ASSETS["ch11_ansv_005"]["asset_id"] == "CH11-ANSV-005"
    assert CH11_ASSETS["ch11_par_002"]["asset_id"] == "CH11-PAR-002"


def test_chapter_12_structure_and_screen_ids():
    assert len(CH12_LESSONS) == 6
    assert [lesson["id"] for lesson in CH12_LESSONS] == [
        "CH12-001", "CH12-002", "CH12-003", "CH12-004", "CH12-005", "CH12-006"
    ]
    assert {lesson["type"] for lesson in CH12_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH12_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH12-004"
    assert rc["road_check_id"] == "CH12-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH12_LESSONS}) == 6


def test_chapter_12_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH12_ASSETS) == 8
    expected_ids = {
        "CH12-KORT-001", "CH12-KORT-002", "CH12-PAR-001", "CH12-KORT-003",
        "CH12-KORT-004", "CH12-KORT-005", "CH12-PAR-002", "CH12-KORT-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH12_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH12_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Krav til ledsager vs Krav til elev
    assert CH12_ASSETS["ch12_kort_002"]["pair_asset"] == "ch12_par_001"
    assert CH12_ASSETS["ch12_par_001"]["pair_asset"] == "ch12_kort_002"
    assert CH12_ASSETS["ch12_kort_002"]["asset_id"] == "CH12-KORT-002"
    assert CH12_ASSETS["ch12_par_001"]["asset_id"] == "CH12-PAR-001"

    # Pair 2: Prøveperiode vs Ulykkesrisiko 9 måneder
    assert CH12_ASSETS["ch12_kort_005"]["pair_asset"] == "ch12_par_002"
    assert CH12_ASSETS["ch12_par_002"]["pair_asset"] == "ch12_kort_005"
    assert CH12_ASSETS["ch12_kort_005"]["asset_id"] == "CH12-KORT-005"
    assert CH12_ASSETS["ch12_par_002"]["asset_id"] == "CH12-PAR-002"


def test_chapter_13_structure_and_screen_ids():
    assert len(CH13_LESSONS) == 6
    assert [lesson["id"] for lesson in CH13_LESSONS] == [
        "CH13-001", "CH13-002", "CH13-003", "CH13-004", "CH13-005", "CH13-006"
    ]
    assert {lesson["type"] for lesson in CH13_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH13_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH13-004"
    assert rc["road_check_id"] == "CH13-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH13_LESSONS}) == 6


def test_chapter_13_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH13_ASSETS) == 8
    expected_ids = {
        "CH13-UHEL-001", "CH13-UHEL-002", "CH13-PAR-001", "CH13-UHEL-003",
        "CH13-UHEL-004", "CH13-UHEL-005", "CH13-PAR-002", "CH13-UHEL-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH13_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH13_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Varseltrekant avstand vs Refleksvest i førerdør
    assert CH13_ASSETS["ch13_uhel_002"]["pair_asset"] == "ch13_par_001"
    assert CH13_ASSETS["ch13_par_001"]["pair_asset"] == "ch13_uhel_002"
    assert CH13_ASSETS["ch13_uhel_002"]["asset_id"] == "CH13-UHEL-002"
    assert CH13_ASSETS["ch13_par_001"]["asset_id"] == "CH13-PAR-001"

    # Pair 2: Flytting av skadde vs Åpne frie luftveier
    assert CH13_ASSETS["ch13_uhel_005"]["pair_asset"] == "ch13_par_002"
    assert CH13_ASSETS["ch13_par_002"]["pair_asset"] == "ch13_uhel_005"
    assert CH13_ASSETS["ch13_uhel_005"]["asset_id"] == "CH13-UHEL-005"
    assert CH13_ASSETS["ch13_par_002"]["asset_id"] == "CH13-PAR-002"


def test_chapter_14_structure_and_screen_ids():
    assert len(CH14_LESSONS) == 6
    assert [lesson["id"] for lesson in CH14_LESSONS] == [
        "CH14-001", "CH14-002", "CH14-003", "CH14-004", "CH14-005", "CH14-006"
    ]
    assert {lesson["type"] for lesson in CH14_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH14_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH14-004"
    assert rc["road_check_id"] == "CH14-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH14_LESSONS}) == 6


def test_chapter_14_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH14_ASSETS) == 8
    expected_ids = {
        "CH14-TEKN-001", "CH14-TEKN-002", "CH14-PAR-001", "CH14-TEKN-003",
        "CH14-TEKN-004", "CH14-TEKN-005", "CH14-PAR-002", "CH14-TEKN-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH14_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH14_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Dekkmønster krav vs Dekktrykk og vannplaning
    assert CH14_ASSETS["ch14_tekn_002"]["pair_asset"] == "ch14_par_001"
    assert CH14_ASSETS["ch14_par_001"]["pair_asset"] == "ch14_tekn_002"
    assert CH14_ASSETS["ch14_tekn_002"]["asset_id"] == "CH14-TEKN-002"
    assert CH14_ASSETS["ch14_par_001"]["asset_id"] == "CH14-PAR-001"

    # Pair 2: Hodestøtte og belte vs Barnesikring og airbag
    assert CH14_ASSETS["ch14_tekn_005"]["pair_asset"] == "ch14_par_002"
    assert CH14_ASSETS["ch14_par_002"]["pair_asset"] == "ch14_tekn_005"
    assert CH14_ASSETS["ch14_tekn_005"]["asset_id"] == "CH14-TEKN-005"
    assert CH14_ASSETS["ch14_par_002"]["asset_id"] == "CH14-PAR-002"


def test_chapter_15_structure_and_screen_ids():
    assert len(CH15_LESSONS) == 6
    assert [lesson["id"] for lesson in CH15_LESSONS] == [
        "CH15-001", "CH15-002", "CH15-003", "CH15-004", "CH15-005", "CH15-006"
    ]
    assert {lesson["type"] for lesson in CH15_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH15_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH15-004"
    assert rc["road_check_id"] == "CH15-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH15_LESSONS}) == 6


def test_chapter_15_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH15_ASSETS) == 8
    expected_ids = {
        "CH15-RISK-001", "CH15-RISK-002", "CH15-PAR-001", "CH15-RISK-003",
        "CH15-RISK-004", "CH15-RISK-005", "CH15-PAR-002", "CH15-RISK-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH15_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH15_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Ulykkesstatistikk vs Tretthet bak rattet
    assert CH15_ASSETS["ch15_risk_002"]["pair_asset"] == "ch15_par_001"
    assert CH15_ASSETS["ch15_par_001"]["pair_asset"] == "ch15_risk_002"
    assert CH15_ASSETS["ch15_risk_002"]["asset_id"] == "CH15-RISK-002"
    assert CH15_ASSETS["ch15_par_001"]["asset_id"] == "CH15-PAR-001"

    # Pair 2: Gruppepress og passasjerer vs Defensiv holdning
    assert CH15_ASSETS["ch15_risk_005"]["pair_asset"] == "ch15_par_002"
    assert CH15_ASSETS["ch15_par_002"]["pair_asset"] == "ch15_risk_005"
    assert CH15_ASSETS["ch15_risk_005"]["asset_id"] == "CH15-RISK-005"
    assert CH15_ASSETS["ch15_par_002"]["asset_id"] == "CH15-PAR-002"


def test_chapter_16_structure_and_screen_ids():
    assert len(CH16_LESSONS) == 6
    assert [lesson["id"] for lesson in CH16_LESSONS] == [
        "CH16-001", "CH16-002", "CH16-003", "CH16-004", "CH16-005", "CH16-006"
    ]
    assert {lesson["type"] for lesson in CH16_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH16_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH16-004"
    assert rc["road_check_id"] == "CH16-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH16_LESSONS}) == 6


def test_chapter_16_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH16_ASSETS) == 8
    expected_ids = {
        "CH16-MANO-001", "CH16-MANO-002", "CH16-PAR-001", "CH16-MANO-003",
        "CH16-MANO-004", "CH16-MANO-005", "CH16-PAR-002", "CH16-MANO-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH16_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH16_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Nødbrems med ABS vs Rattgrep 9 og 3
    assert CH16_ASSETS["ch16_mano_002"]["pair_asset"] == "ch16_par_001"
    assert CH16_ASSETS["ch16_par_001"]["pair_asset"] == "ch16_mano_002"
    assert CH16_ASSETS["ch16_mano_002"]["asset_id"] == "CH16-MANO-002"
    assert CH16_ASSETS["ch16_par_001"]["asset_id"] == "CH16-PAR-001"

    # Pair 2: Svingteknikk vs Sentrifugalkraft
    assert CH16_ASSETS["ch16_mano_005"]["pair_asset"] == "ch16_par_002"
    assert CH16_ASSETS["ch16_par_002"]["pair_asset"] == "ch16_mano_005"
    assert CH16_ASSETS["ch16_mano_005"]["asset_id"] == "CH16-MANO-005"
    assert CH16_ASSETS["ch16_par_002"]["asset_id"] == "CH16-PAR-002"


def test_chapter_17_structure_and_screen_ids():
    assert len(CH17_LESSONS) == 6
    assert [lesson["id"] for lesson in CH17_LESSONS] == [
        "CH17-001", "CH17-002", "CH17-003", "CH17-004", "CH17-005", "CH17-006"
    ]
    assert {lesson["type"] for lesson in CH17_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH17_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH17-004"
    assert rc["road_check_id"] == "CH17-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH17_LESSONS}) == 6


def test_chapter_17_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH17_ASSETS) == 8
    expected_ids = {
        "CH17-OKO-001", "CH17-OKO-002", "CH17-PAR-001", "CH17-OKO-003",
        "CH17-OKO-004", "CH17-OKO-005", "CH17-PAR-002", "CH17-OKO-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH17_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH17_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Tidlig oppgiring vs Motorbrems
    assert CH17_ASSETS["ch17_oko_002"]["pair_asset"] == "ch17_par_001"
    assert CH17_ASSETS["ch17_par_001"]["pair_asset"] == "ch17_oko_002"
    assert CH17_ASSETS["ch17_oko_002"]["asset_id"] == "CH17-OKO-002"
    assert CH17_ASSETS["ch17_par_001"]["asset_id"] == "CH17-PAR-001"

    # Pair 2: Luftmotstand/hastighet vs Takboks
    assert CH17_ASSETS["ch17_oko_005"]["pair_asset"] == "ch17_par_002"
    assert CH17_ASSETS["ch17_par_002"]["pair_asset"] == "ch17_oko_005"
    assert CH17_ASSETS["ch17_oko_005"]["asset_id"] == "CH17-OKO-005"
    assert CH17_ASSETS["ch17_par_002"]["asset_id"] == "CH17-PAR-002"


def test_chapter_18_structure_and_screen_ids():
    assert len(CH18_LESSONS) == 6
    assert [lesson["id"] for lesson in CH18_LESSONS] == [
        "CH18-001", "CH18-002", "CH18-003", "CH18-004", "CH18-005", "CH18-006"
    ]
    assert {lesson["type"] for lesson in CH18_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH18_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH18-004"
    assert rc["road_check_id"] == "CH18-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH18_LESSONS}) == 6


def test_chapter_18_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH18_ASSETS) == 8
    expected_ids = {
        "CH18-TR2-001", "CH18-TR2-002", "CH18-PAR-001", "CH18-TR2-003",
        "CH18-TR2-004", "CH18-TR2-005", "CH18-PAR-002", "CH18-TR2-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH18_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH18_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Automatisering vs Selvevaluering
    assert CH18_ASSETS["ch18_tr2_002"]["pair_asset"] == "ch18_par_001"
    assert CH18_ASSETS["ch18_par_001"]["pair_asset"] == "ch18_tr2_002"
    assert CH18_ASSETS["ch18_tr2_002"]["asset_id"] == "CH18-TR2-002"
    assert CH18_ASSETS["ch18_par_001"]["asset_id"] == "CH18-PAR-001"

    # Pair 2: Overgang til Trinn 3 vs Sikkerhetskurs på bane
    assert CH18_ASSETS["ch18_tr2_005"]["pair_asset"] == "ch18_par_002"
    assert CH18_ASSETS["ch18_par_002"]["pair_asset"] == "ch18_tr2_005"
    assert CH18_ASSETS["ch18_tr2_005"]["asset_id"] == "CH18-TR2-005"
    assert CH18_ASSETS["ch18_par_002"]["asset_id"] == "CH18-PAR-002"


def test_chapters_3_to_28_in_studybook_chapters_v5_json():
    json_path = Path(__file__).resolve().parents[2] / "content" / "studybook_chapters_v5.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for code, cid, rc_id, p1, p2 in [
        ("CH03", "ch_speed_braking", "CH03-RC-001", "CH03-PAR-001", "CH03-PAR-002"),
        ("CH05", "ch_trinn1_grunnkurs", "CH05-RC-001", "CH05-PAR-001", "CH05-PAR-002"),
        ("CH06", "ch_forbikjoring_rygging", "CH06-RC-001", "CH06-PAR-001", "CH06-PAR-002"),
        ("CH07", "ch_stans_parkering", "CH07-RC-001", "CH07-PAR-001", "CH07-PAR-002"),
        ("CH08", "ch_trafikkskilt_vegmerking", "CH08-RC-001", "CH08-PAR-001", "CH08-PAR-002"),
        ("CH09", "ch_lys_signal_tegn", "CH09-RC-001", "CH09-PAR-001", "CH09-PAR-002"),
        ("CH10", "ch_alkohol_rus_kjoring", "CH10-RC-001", "CH10-PAR-001", "CH10-PAR-002"),
        ("CH11", "ch_forsikring_registrering", "CH11-RC-001", "CH11-PAR-001", "CH11-PAR-002"),
        ("CH12", "ch_forerkort_opplaering", "CH12-RC-001", "CH12-PAR-001", "CH12-PAR-002"),
        ("CH13", "ch_trafikkuhell_forstehjelp", "CH13-RC-001", "CH13-PAR-001", "CH13-PAR-002"),
        ("CH14", "ch_kjoretoy_sikkerhet", "CH14-RC-001", "CH14-PAR-001", "CH14-PAR-002"),
        ("CH15", "ch_risiko_ulykker", "CH15-RC-001", "CH15-PAR-001", "CH15-PAR-002"),
        ("CH16", "ch_kjoretoybehandling_manovrering", "CH16-RC-001", "CH16-PAR-001", "CH16-PAR-002"),
        ("CH17", "ch_miljovennlig_okonomisk_kjoring", "CH17-RC-001", "CH17-PAR-001", "CH17-PAR-002"),
        ("CH18", "ch_trinnvurdering_trinn2", "CH18-RC-001", "CH18-PAR-001", "CH18-PAR-002"),
        ("CH19", "ch_trinn3_maal_rammer", "CH19-RC-001", "CH19-PAR-001", "CH19-PAR-002"),
        ("CH20", "ch_trafikksystemet_trafikantgrupper", "CH20-RC-001", "CH20-PAR-001", "CH20-PAR-002"),
        ("CH21", "ch_veg_oppmerking_skilt_atferd", "CH21-RC-001", "CH21-PAR-001", "CH21-PAR-002"),
        ("CH22", "ch_systematisk_informasjonsinnhenting", "CH22-RC-001", "CH22-PAR-001", "CH22-PAR-002"),
        ("CH23", "ch_kjoring_by_landeveg", "CH23-RC-001", "CH23-PAR-001", "CH23-PAR-002"),
        ("CH24", "ch_effektiv_kjoring_sikkerhetskurs_bane", "CH24-RC-001", "CH24-PAR-001", "CH24-PAR-002"),
        ("CH25", "ch_bilkjoringens_risiko", "CH25-RC-001", "CH25-PAR-001", "CH25-PAR-002"),
        ("CH26", "ch_kjorekompetanse_landevegsmiljo", "CH26-RC-001", "CH26-PAR-001", "CH26-PAR-002"),
        ("CH27", "ch_planlegging_refleksjon_oving", "CH27-RC-001", "CH27-PAR-001", "CH27-PAR-002"),
        ("CH28", "ch_lover_regler_oppslagsverk", "CH28-RC-001", "CH28-PAR-001", "CH28-PAR-002"),
    ]:
        ch = next((c for c in data if c.get("chapter_code") == code or c.get("chapter_id") == cid), None)
        assert ch is not None, f"Missing {code} in v5 json"
        assert len(ch["screens"]) == 6, f"{code} screens != 6"
        assert [s["screen_id"] for s in ch["screens"]] == [f"{code}-{i:03d}" for i in range(1, 7)]
        assert ch["screens"][3]["road_check_id"] == rc_id
        assert ch["screens"][1]["pair_asset_id"] == p1
        assert ch["screens"][4]["pair_asset_id"] == p2
        for s in ch["screens"]:
            assert s.get("glossary_terms") and len(s["glossary_terms"]) > 0

def test_chapter_19_structure_and_screen_ids():
    assert len(CH19_LESSONS) == 6
    assert [lesson["id"] for lesson in CH19_LESSONS] == [
        "CH19-001", "CH19-002", "CH19-003", "CH19-004", "CH19-005", "CH19-006"
    ]
    assert {lesson["type"] for lesson in CH19_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH19_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH19-004"
    assert rc["road_check_id"] == "CH19-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH19_LESSONS}) == 6


def test_chapter_19_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH19_ASSETS) == 8
    expected_ids = {
        "CH19-TR3-001", "CH19-TR3-002", "CH19-PAR-001", "CH19-TR3-003",
        "CH19-TR3-004", "CH19-TR3-005", "CH19-PAR-002", "CH19-TR3-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH19_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH19_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Selvstendig kjøring vs Trinnvurdering
    assert CH19_ASSETS["ch19_tr3_002"]["pair_asset"] == "ch19_par_001"
    assert CH19_ASSETS["ch19_par_001"]["pair_asset"] == "ch19_tr3_002"
    assert CH19_ASSETS["ch19_tr3_002"]["asset_id"] == "CH19-TR3-002"
    assert CH19_ASSETS["ch19_par_001"]["asset_id"] == "CH19-PAR-001"

    # Pair 2: Sikkerhetskurs på bane vs Sikkerhetskurs på veg
    assert CH19_ASSETS["ch19_tr3_005"]["pair_asset"] == "ch19_par_002"
    assert CH19_ASSETS["ch19_par_002"]["pair_asset"] == "ch19_tr3_005"
    assert CH19_ASSETS["ch19_tr3_005"]["asset_id"] == "CH19-TR3-005"
    assert CH19_ASSETS["ch19_par_002"]["asset_id"] == "CH19-PAR-002"


def test_chapter_20_structure_and_screen_ids():
    assert len(CH20_LESSONS) == 6
    assert [lesson["id"] for lesson in CH20_LESSONS] == [
        "CH20-001", "CH20-002", "CH20-003", "CH20-004", "CH20-005", "CH20-006"
    ]
    assert {lesson["type"] for lesson in CH20_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH20_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH20-004"
    assert rc["road_check_id"] == "CH20-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH20_LESSONS}) == 6


def test_chapter_20_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH20_ASSETS) == 8
    expected_ids = {
        "CH20-SYS-001", "CH20-SYS-002", "CH20-PAR-001", "CH20-SYS-003",
        "CH20-SYS-004", "CH20-SYS-005", "CH20-PAR-002", "CH20-SYS-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH20_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH20_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Trafikanten, kjøretøyet og veien vs Interessemotsetninger
    assert CH20_ASSETS["ch20_sys_002"]["pair_asset"] == "ch20_par_001"
    assert CH20_ASSETS["ch20_par_001"]["pair_asset"] == "ch20_sys_002"
    assert CH20_ASSETS["ch20_sys_002"]["asset_id"] == "CH20-SYS-002"
    assert CH20_ASSETS["ch20_par_001"]["asset_id"] == "CH20-PAR-001"

    # Pair 2: Myke trafikanter vs Blindsoner og barn
    assert CH20_ASSETS["ch20_sys_005"]["pair_asset"] == "ch20_par_002"
    assert CH20_ASSETS["ch20_par_002"]["pair_asset"] == "ch20_sys_005"
    assert CH20_ASSETS["ch20_sys_005"]["asset_id"] == "CH20-SYS-005"
    assert CH20_ASSETS["ch20_par_002"]["asset_id"] == "CH20-PAR-002"


def test_chapter_21_structure_and_screen_ids():
    assert len(CH21_LESSONS) == 6
    assert [lesson["id"] for lesson in CH21_LESSONS] == [
        "CH21-001", "CH21-002", "CH21-003", "CH21-004", "CH21-005", "CH21-006"
    ]
    assert {lesson["type"] for lesson in CH21_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH21_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH21-004"
    assert rc["road_check_id"] == "CH21-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH21_LESSONS}) == 6


def test_chapter_21_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH21_ASSETS) == 8
    expected_ids = {
        "CH21-VEG-001", "CH21-VEG-002", "CH21-PAR-001", "CH21-VEG-003",
        "CH21-VEG-004", "CH21-VEG-005", "CH21-PAR-002", "CH21-VEG-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH21_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH21_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Helsperrelinje vs Kjørefeltlinje
    assert CH21_ASSETS["ch21_veg_002"]["pair_asset"] == "ch21_par_001"
    assert CH21_ASSETS["ch21_par_001"]["pair_asset"] == "ch21_veg_002"
    assert CH21_ASSETS["ch21_veg_002"]["asset_id"] == "CH21-VEG-002"
    assert CH21_ASSETS["ch21_par_001"]["asset_id"] == "CH21-PAR-001"

    # Pair 2: Fartsgrenser vs Siktforhold og kurver
    assert CH21_ASSETS["ch21_veg_005"]["pair_asset"] == "ch21_par_002"
    assert CH21_ASSETS["ch21_par_002"]["pair_asset"] == "ch21_veg_005"
    assert CH21_ASSETS["ch21_veg_005"]["asset_id"] == "CH21-VEG-005"
    assert CH21_ASSETS["ch21_par_002"]["asset_id"] == "CH21-PAR-002"


def test_chapter_22_structure_and_screen_ids():
    assert len(CH22_LESSONS) == 6
    assert [lesson["id"] for lesson in CH22_LESSONS] == [
        "CH22-001", "CH22-002", "CH22-003", "CH22-004", "CH22-005", "CH22-006"
    ]
    assert {lesson["type"] for lesson in CH22_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH22_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH22-004"
    assert rc["road_check_id"] == "CH22-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH22_LESSONS}) == 6


def test_chapter_22_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH22_ASSETS) == 8
    expected_ids = {
        "CH22-SE-001", "CH22-SE-002", "CH22-PAR-001", "CH22-SE-003",
        "CH22-SE-004", "CH22-SE-005", "CH22-PAR-002", "CH22-SE-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH22_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH22_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Blikket langt frem vs Fiksering på panseret
    assert CH22_ASSETS["ch22_se_002"]["pair_asset"] == "ch22_par_001"
    assert CH22_ASSETS["ch22_par_001"]["pair_asset"] == "ch22_se_002"
    assert CH22_ASSETS["ch22_se_002"]["asset_id"] == "CH22-SE-002"
    assert CH22_ASSETS["ch22_par_001"]["asset_id"] == "CH22-PAR-001"

    # Pair 2: Blindsonesjekk vs Speilvisning
    assert CH22_ASSETS["ch22_se_005"]["pair_asset"] == "ch22_par_002"
    assert CH22_ASSETS["ch22_par_002"]["pair_asset"] == "ch22_se_005"
    assert CH22_ASSETS["ch22_se_005"]["asset_id"] == "CH22-SE-005"
    assert CH22_ASSETS["ch22_par_002"]["asset_id"] == "CH22-PAR-002"


def test_chapter_23_structure_and_screen_ids():
    assert len(CH23_LESSONS) == 6
    assert [lesson["id"] for lesson in CH23_LESSONS] == [
        "CH23-001", "CH23-002", "CH23-003", "CH23-004", "CH23-005", "CH23-006"
    ]
    assert {lesson["type"] for lesson in CH23_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH23_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH23-004"
    assert rc["road_check_id"] == "CH23-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH23_LESSONS}) == 6


def test_chapter_23_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH23_ASSETS) == 8
    expected_ids = {
        "CH23-BY-001", "CH23-BY-002", "CH23-PAR-001", "CH23-BY-003",
        "CH23-BY-004", "CH23-BY-005", "CH23-PAR-002", "CH23-BY-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH23_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH23_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Vikeplikt for fotgjengere i felt vs Innsnevring og syklister
    assert CH23_ASSETS["ch23_by_002"]["pair_asset"] == "ch23_par_001"
    assert CH23_ASSETS["ch23_par_001"]["pair_asset"] == "ch23_by_002"
    assert CH23_ASSETS["ch23_by_002"]["asset_id"] == "CH23-BY-002"
    assert CH23_ASSETS["ch23_par_001"]["asset_id"] == "CH23-PAR-001"

    # Pair 2: Feltskifte i tett trafikk vs Avkjøringsfelt og avstand
    assert CH23_ASSETS["ch23_by_005"]["pair_asset"] == "ch23_par_002"
    assert CH23_ASSETS["ch23_par_002"]["pair_asset"] == "ch23_by_005"
    assert CH23_ASSETS["ch23_by_005"]["asset_id"] == "CH23-BY-005"
    assert CH23_ASSETS["ch23_par_002"]["asset_id"] == "CH23-PAR-002"


def test_chapter_24_structure_and_screen_ids():
    assert len(CH24_LESSONS) == 6
    assert [lesson["id"] for lesson in CH24_LESSONS] == [
        "CH24-001", "CH24-002", "CH24-003", "CH24-004", "CH24-005", "CH24-006"
    ]
    assert {lesson["type"] for lesson in CH24_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH24_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH24-004"
    assert rc["road_check_id"] == "CH24-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH24_LESSONS}) == 6


def test_chapter_24_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH24_ASSETS) == 8
    expected_ids = {
        "CH24-BANE-001", "CH24-BANE-002", "CH24-PAR-001", "CH24-BANE-003",
        "CH24-BANE-004", "CH24-BANE-005", "CH24-PAR-002", "CH24-BANE-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH24_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH24_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Understyring vs Overstyring
    assert CH24_ASSETS["ch24_bane_002"]["pair_asset"] == "ch24_par_001"
    assert CH24_ASSETS["ch24_par_001"]["pair_asset"] == "ch24_bane_002"
    assert CH24_ASSETS["ch24_bane_002"]["asset_id"] == "CH24-BANE-002"
    assert CH24_ASSETS["ch24_par_001"]["asset_id"] == "CH24-PAR-001"

    # Pair 2: Vannplaning vs Last og tyngdepunkt
    assert CH24_ASSETS["ch24_bane_005"]["pair_asset"] == "ch24_par_002"
    assert CH24_ASSETS["ch24_par_002"]["pair_asset"] == "ch24_bane_005"
    assert CH24_ASSETS["ch24_bane_005"]["asset_id"] == "CH24-BANE-005"
    assert CH24_ASSETS["ch24_par_002"]["asset_id"] == "CH24-PAR-002"


def test_chapter_25_structure_and_screen_ids():
    assert len(CH25_LESSONS) == 6
    assert [lesson["id"] for lesson in CH25_LESSONS] == [
        "CH25-001", "CH25-002", "CH25-003", "CH25-004", "CH25-005", "CH25-006"
    ]
    assert {lesson["type"] for lesson in CH25_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH25_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH25-004"
    assert rc["road_check_id"] == "CH25-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH25_LESSONS}) == 6


def test_chapter_25_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH25_ASSETS) == 8
    expected_ids = {
        "CH25-RISK-001", "CH25-RISK-002", "CH25-PAR-001", "CH25-RISK-003",
        "CH25-RISK-004", "CH25-RISK-005", "CH25-PAR-002", "CH25-RISK-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH25_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH25_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Uoppmerksomhet og mobilbruk vs Fartstilpasning
    assert CH25_ASSETS["ch25_risk_002"]["pair_asset"] == "ch25_par_001"
    assert CH25_ASSETS["ch25_par_001"]["pair_asset"] == "ch25_risk_002"
    assert CH25_ASSETS["ch25_risk_002"]["asset_id"] == "CH25-RISK-002"
    assert CH25_ASSETS["ch25_par_001"]["asset_id"] == "CH25-PAR-001"

    # Pair 2: Rus og reaksjonsevne vs Tretthet og mikrosøvn
    assert CH25_ASSETS["ch25_risk_005"]["pair_asset"] == "ch25_par_002"
    assert CH25_ASSETS["ch25_par_002"]["pair_asset"] == "ch25_risk_005"
    assert CH25_ASSETS["ch25_risk_005"]["asset_id"] == "CH25-RISK-005"
    assert CH25_ASSETS["ch25_par_002"]["asset_id"] == "CH25-PAR-002"


def test_chapter_26_structure_and_screen_ids():
    assert len(CH26_LESSONS) == 6
    assert [lesson["id"] for lesson in CH26_LESSONS] == [
        "CH26-001", "CH26-002", "CH26-003", "CH26-004", "CH26-005", "CH26-006"
    ]
    assert {lesson["type"] for lesson in CH26_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH26_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH26-004"
    assert rc["road_check_id"] == "CH26-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH26_LESSONS}) == 6


def test_chapter_26_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH26_ASSETS) == 8
    expected_ids = {
        "CH26-LAND-001", "CH26-LAND-002", "CH26-PAR-001", "CH26-LAND-003",
        "CH26-LAND-004", "CH26-LAND-005", "CH26-PAR-002", "CH26-LAND-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH26_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH26_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Møteulykker på landevei vs Forbikjøring og tidsgevinst
    assert CH26_ASSETS["ch26_land_002"]["pair_asset"] == "ch26_par_001"
    assert CH26_ASSETS["ch26_par_001"]["pair_asset"] == "ch26_land_002"
    assert CH26_ASSETS["ch26_land_002"]["asset_id"] == "CH26-LAND-002"
    assert CH26_ASSETS["ch26_par_001"]["asset_id"] == "CH26-PAR-001"

    # Pair 2: Viltfare i skumringen vs Svingkjøring og sentrifugalkraft
    assert CH26_ASSETS["ch26_land_005"]["pair_asset"] == "ch26_par_002"
    assert CH26_ASSETS["ch26_par_002"]["pair_asset"] == "ch26_land_005"
    assert CH26_ASSETS["ch26_land_005"]["asset_id"] == "CH26-LAND-005"
    assert CH26_ASSETS["ch26_par_002"]["asset_id"] == "CH26-PAR-002"


def test_chapter_27_structure_and_screen_ids():
    assert len(CH27_LESSONS) == 6
    assert [lesson["id"] for lesson in CH27_LESSONS] == [
        "CH27-001", "CH27-002", "CH27-003", "CH27-004", "CH27-005", "CH27-006"
    ]
    assert {lesson["type"] for lesson in CH27_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH27_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH27-004"
    assert rc["road_check_id"] == "CH27-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH27_LESSONS}) == 6


def test_chapter_27_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH27_ASSETS) == 8
    expected_ids = {
        "CH27-REF-001", "CH27-REF-002", "CH27-PAR-001", "CH27-REF-003",
        "CH27-REF-004", "CH27-REF-005", "CH27-PAR-002", "CH27-REF-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH27_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH27_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Selvevaluering og HER-modellen vs Strukturert mengdetrening
    assert CH27_ASSETS["ch27_ref_002"]["pair_asset"] == "ch27_par_001"
    assert CH27_ASSETS["ch27_par_001"]["pair_asset"] == "ch27_ref_002"
    assert CH27_ASSETS["ch27_ref_002"]["asset_id"] == "CH27-REF-002"
    assert CH27_ASSETS["ch27_par_001"]["asset_id"] == "CH27-PAR-001"

    # Pair 2: Øvelseskjøring i krevende miljø vs Klar for praktisk prøve
    assert CH27_ASSETS["ch27_ref_005"]["pair_asset"] == "ch27_par_002"
    assert CH27_ASSETS["ch27_par_002"]["pair_asset"] == "ch27_ref_005"
    assert CH27_ASSETS["ch27_ref_005"]["asset_id"] == "CH27-REF-005"
    assert CH27_ASSETS["ch27_par_002"]["asset_id"] == "CH27-PAR-002"


def test_chapter_28_structure_and_screen_ids():
    assert len(CH28_LESSONS) == 6
    assert [lesson["id"] for lesson in CH28_LESSONS] == [
        "CH28-001", "CH28-002", "CH28-003", "CH28-004", "CH28-005", "CH28-006"
    ]
    assert {lesson["type"] for lesson in CH28_LESSONS} == {
        "intro", "choice", "sequence", "roadCheck", "chapterComplete"
    }
    rc = next(lesson for lesson in CH28_LESSONS if lesson["type"] == "roadCheck")
    assert rc["id"] == "CH28-004"
    assert rc["road_check_id"] == "CH28-RC-001"
    assert len(rc["questions"]) == 3
    assert len({lesson["id"] for lesson in CH28_LESSONS}) == 6


def test_chapter_28_asset_manifest_and_pairs():
    required = {
        "asset_id", "page", "scene", "pedagogical_purpose", "camera_angle",
        "risk_source", "risikokilde", "vehicles_road_users", "road_type", "signs_markings",
        "learner_discovery", "hotspots", "pair_asset", "status", "src", "alt",
    }
    assert len(CH28_ASSETS) == 8
    expected_ids = {
        "CH28-LOV-001", "CH28-LOV-002", "CH28-PAR-001", "CH28-LOV-003",
        "CH28-LOV-004", "CH28-LOV-005", "CH28-PAR-002", "CH28-LOV-006",
    }
    actual_ids = {asset["asset_id"] for asset in CH28_ASSETS.values()}
    assert actual_ids == expected_ids
    for asset in CH28_ASSETS.values():
        assert set(asset) == required
        assert asset["status"] == "placeholder"
        assert all(asset[key] for key in required - {"hotspots", "pair_asset"})

    # Pair 1: Vegtrafikkloven § 3 (HAV) vs Grunnregler for vikeplikt
    assert CH28_ASSETS["ch28_lov_002"]["pair_asset"] == "ch28_par_001"
    assert CH28_ASSETS["ch28_par_001"]["pair_asset"] == "ch28_lov_002"
    assert CH28_ASSETS["ch28_lov_002"]["asset_id"] == "CH28-LOV-002"
    assert CH28_ASSETS["ch28_par_001"]["asset_id"] == "CH28-PAR-001"

    # Pair 2: Fartsregler og tilpasning vs Prikkbelastning og førerrett
    assert CH28_ASSETS["ch28_lov_005"]["pair_asset"] == "ch28_par_002"
    assert CH28_ASSETS["ch28_par_002"]["pair_asset"] == "ch28_lov_005"
    assert CH28_ASSETS["ch28_lov_005"]["asset_id"] == "CH28-LOV-005"
    assert CH28_ASSETS["ch28_par_002"]["asset_id"] == "CH28-PAR-002"
