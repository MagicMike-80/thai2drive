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

from studybook_web import ASSETS, COPY, CSS, LESSONS, SCREEN, SCRIPT, install, CH04_ASSETS, CH04_LESSONS, CHAPTERS
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

