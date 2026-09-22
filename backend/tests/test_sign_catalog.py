"""
tests/test_sign_catalog.py

Sign Catalog Audit Tests - Thai2Drive
======================================
Verifiserer at hvert skilt i signs_data.SIGNS har:
  - Unikt skilt-nummer (ingen duplikater)
  - Alle paakrevde trilingual felt (no/th/en for name og desc)
  - Kjent type (finnes i TYPE_META)
  - Ingen tomme strenger i name/desc
  - Korrekt identitet paa skilt 202 (vikeplikt, ikke fartshump)
  - Korrekt struktur fra get_signs_grouped()

Null eksterne avhengigheter -- kjores offline.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from signs_data import SIGNS, TYPE_META, get_signs_grouped


def test_no_duplicate_sign_numbers_within_type():
    from collections import defaultdict
    by_type = defaultdict(list)
    for sign in SIGNS:
        by_type[sign["type"]].append(sign["num"])
    errors = []
    for stype, nums in by_type.items():
        seen = set()
        for n in nums:
            if n in seen:
                errors.append(f"Duplicate num '{n}' in type '{stype}'")
            seen.add(n)
    assert not errors, "Duplikate skiltnummer funnet:\n" + "\n".join(errors)


def test_no_globally_duplicate_sign_numbers():
    nums = [s["num"] for s in SIGNS]
    seen = set()
    duplicates = set()
    for n in nums:
        if n in seen:
            duplicates.add(n)
        seen.add(n)
    assert not duplicates, (
        f"Globale duplikate skiltnummer: {sorted(duplicates)}\n"
        "Sjekk signs_data.py og rett opp feilkoblede num-verdier."
    )


def test_all_signs_have_required_fields():
    required_langs = ["no", "th", "en"]
    errors = []
    for sign in SIGNS:
        num = sign.get("num", "<mangler num>")
        stype = sign.get("type", "<mangler type>")
        label = f"Skilt {num} ({stype})"
        if "num" not in sign:
            errors.append(f"{label}: mangler 'num'")
        if "type" not in sign:
            errors.append(f"{label}: mangler 'type'")
        for group in ("name", "desc"):
            if group not in sign:
                errors.append(f"{label}: mangler '{group}'-objekt")
                continue
            for lang in required_langs:
                if lang not in sign[group]:
                    errors.append(f"{label}: mangler {group}.{lang}")
    assert not errors, "Manglende felt i skiltkatalogen:\n" + "\n".join(errors)


def test_all_types_in_type_meta():
    unknown = set()
    for sign in SIGNS:
        if sign.get("type") not in TYPE_META:
            unknown.add(sign.get("type"))
    assert not unknown, (
        f"Ukjente skilttyper (mangler i TYPE_META): {sorted(str(t) for t in unknown)}"
    )


def test_sign_names_not_empty():
    errors = []
    for sign in SIGNS:
        num = sign.get("num", "?")
        stype = sign.get("type", "?")
        for group in ("name", "desc"):
            for lang in ("no", "th", "en"):
                val = sign.get(group, {}).get(lang, None)
                if val is not None and val.strip() == "":
                    errors.append(f"Skilt {num} ({stype}): {group}.{lang} er tom streng")
    assert not errors, "Tomme felt funnet:\n" + "\n".join(errors)


def test_vikeplikt_202_correct_identity():
    vikeplikt_signs = [s for s in SIGNS if s.get("type") == "vikeplikt"]
    sign_202 = next((s for s in vikeplikt_signs if s["num"] == "202"), None)
    assert sign_202 is not None, "Skilt 202 (vikeplikt) finnes ikke i katalogen!"
    name_no = sign_202["name"]["no"].lower()
    assert "vikeplikt" in name_no, (
        f"Skilt 202 (vikeplikt) har feil navn: '{sign_202['name']['no']}'. Forventet 'Vikeplikt'."
    )
    assert "fartshump" not in name_no, (
        f"Skilt 202 (vikeplikt) er feilmerket som Fartshump! Rett num for fartshump er 201."
    )


def test_fartshump_has_num_201():
    fare_signs = [s for s in SIGNS if s.get("type") == "fare"]
    fartshump = next((s for s in fare_signs if "fartshump" in s["name"]["no"].lower()), None)
    assert fartshump is not None, "Fartshump-skilt ikke funnet i 'fare'-kategorien."
    assert fartshump["num"] == "201", (
        f"Fartshump har feil num: '{fartshump['num']}'. Skal vaere '201'."
    )


def test_get_signs_grouped_returns_correct_structure():
    grouped = get_signs_grouped()
    assert isinstance(grouped, dict), "get_signs_grouped() skal returnere en dict"
    for stype, data in grouped.items():
        assert stype in TYPE_META, f"Ukjent type i resultat: '{stype}'"
        assert "meta" in data, f"Mangler 'meta' for type '{stype}'"
        assert "signs" in data, f"Mangler 'signs' for type '{stype}'"
        meta = data["meta"]
        for field in ("no", "th", "en", "color", "shape"):
            assert field in meta, f"TYPE_META['{stype}'] mangler felt '{field}'"
        assert isinstance(data["signs"], list), f"'signs' for type '{stype}' er ikke en liste"
        assert len(data["signs"]) > 0, f"'signs' for type '{stype}' er tom liste"
