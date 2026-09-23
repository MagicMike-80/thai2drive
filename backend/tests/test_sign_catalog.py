"""Offline audit gates for the complete production traffic-sign catalog."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from signs_data import SIGNS, TYPE_META, get_signs_grouped  # noqa: E402


CATALOG = json.loads((BACKEND / "signs_content.json").read_text(encoding="utf-8"))
IMAGE_DIR = BACKEND / "sign_images"
LANGS = ("no", "th", "en")


def _record(sign_id: str) -> dict:
    return next(row for row in CATALOG if row["id"] == sign_id)


def _image_owner(path: Path) -> str | None:
    stem = path.stem
    matches = [row["id"] for row in CATALOG if stem == row["id"] or stem.startswith(row["id"] + "_")]
    return max(matches, key=len) if matches else None


def test_catalog_has_311_current_signs_and_unique_ids():
    ids = [row["id"] for row in CATALOG]
    assert len(ids) == 311
    assert len(ids) == len(set(ids))


def test_all_records_have_complete_trilingual_learning_fields():
    errors = []
    for row in CATALOG:
        for field in ("name", "explanation", "driver_action"):
            for lang in LANGS:
                value = row.get(field, {}).get(lang)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{row.get('id')}: {field}.{lang}")
    assert not errors, "Missing values:\n" + "\n".join(errors)


def test_every_active_image_and_record_match_one_to_one():
    images = sorted(IMAGE_DIR.glob("*.jpg"))
    owners = [_image_owner(path) for path in images]
    assert len(images) == 311
    assert None not in owners, [path.name for path, owner in zip(images, owners) if owner is None]
    counts = Counter(owners)
    assert set(counts) == {row["id"] for row in CATALOG}
    assert all(count == 1 for count in counts.values()), {key: value for key, value in counts.items() if value != 1}


def test_removed_and_legacy_ids_are_not_active():
    ids = {row["id"] for row in CATALOG}
    assert not ids.intersection({"808_42", "902_0", "904_0", "906_0", "930"})
    assert {"521_1", "521_2", "556_1", "556_2", "807_10"}.issubset(ids)
    assert not ids.intersection({"521_0", "521.1", "556_0", "556.2", "807-10"})


def test_legal_identity_regressions():
    expected = {
        "109_0": "Fartshump",
        "140_0": "Avstand til gangfelt",
        "206_0": "Forkjorsveg",
        "208_0": "Slutt pa forkjorsveg",
        "210_0": "Forkjorskryss",
        "212_0": "Vikeplikt overfor motende kjorende",
        "214_0": "Motende kjorende har vikeplikt",
        "302_0": "Innkjoring forbudt",
        "521_1": "Sykkelfelt – sideplassert",
        "521_2": "Sykkelfelt – midtstilt",
        "556_1": "Automatisk trafikkontroll – punktmaling",
        "556_2": "Automatisk trafikkontroll – strekningsmaling",
        "916_0": "Avstandsmarkering i tunnel",
        "940": "Trafikkjegle",
        "942": "Trafikksylinder",
    }
    # Normalize only Norwegian letters in this test's ASCII-friendly source.
    table = str.maketrans({"ø": "o", "å": "a", "æ": "ae", "Ø": "O", "Å": "A", "Æ": "Ae"})
    actual = {sign_id: _record(sign_id)["name"]["no"].translate(table) for sign_id in expected}
    assert actual == expected


def test_no_sign_claims_a_nonexistent_audio_file():
    audio_keys = {"audio", "audio_url", "sound_url", "tts"}
    assert all(not audio_keys.intersection(row) for row in CATALOG)


def test_api_adapter_uses_the_same_complete_catalog():
    assert len(SIGNS) == len(CATALOG)
    assert [sign["num"] for sign in SIGNS] == [row["id"] for row in CATALOG]
    active_types = {sign["type"] for sign in SIGNS}
    assert active_types.issubset(TYPE_META)
    grouped = get_signs_grouped()
    assert set(grouped) == active_types
    assert sum(len(value["signs"]) for value in grouped.values()) == 311
