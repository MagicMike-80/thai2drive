"""Enkel offline-validator for Bilde-bok-pakker. Ingen nettverk, ingen DB."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LANGS = ("no", "th", "en")
THAI = re.compile(r"[฀-๿]")
NO_LETTERS = re.compile(r"[æøåÆØÅ]")
ASSET_RE = re.compile(r"^bb_s\d{2,3}[a-z]?_[a-z0-9-]+$")
QUIZ_CATEGORIES = {"Traffic Signs", "Road Rules", "Right of Way", "Speed Limits", "Safety", "Driving Conditions", "Situations", "Traffic Rules", "Road Conditions"}  # fra normalize_categories.py; ikke verifisert mot live DB


def _i18n(path: str, value, errs: list[str]) -> None:
    if not isinstance(value, dict):
        errs.append(f"{path}: mangler no/th/en")
        return
    for lang in LANGS:
        text = value.get(lang)
        if not isinstance(text, str) or not text.strip():
            errs.append(f"{path}.{lang}: tomt eller mangler")
        elif lang == "th" and not THAI.search(text):
            errs.append(f"{path}.th: ingen thai-tegn")
        elif lang != "th" and THAI.search(text):
            errs.append(f"{path}.{lang}: thai-tegn i {lang}-felt")
        elif lang == "en" and NO_LETTERS.search(text):
            errs.append(f"{path}.en: norske bokstaver i engelsk felt")


def validate_pack(pack: dict, known_ids: set[str] | None = None) -> list[str]:
    errs: list[str] = []
    ids: set[str] = set()
    assets: set[str] = set()
    for p in pack.get("pages", []):
        pid = p.get("id", "?")
        if pid in ids:
            errs.append(f"{pid}: duplisert id")
        ids.add(pid)
        for key in ("book", "printed_page", "pdf_page", "chapter", "section", "image_file", "status"):
            if not p.get(key):
                errs.append(f"{pid}.{key}: mangler")
        if p.get("printed_page") and p.get("pdf_page") and p["printed_page"] != p["pdf_page"] + 5:
            errs.append(f"{pid}: trykt side og PDF-side stemmer ikke (forventer +5)")
        if not ASSET_RE.match(str(p.get("asset_id", ""))):
            errs.append(f"{pid}.asset_id: ugyldig format")
        if p.get("asset_id") in assets:
            errs.append(f"{pid}.asset_id: duplisert")
        assets.add(p.get("asset_id"))
        for key in ("title", "core_sentence", "michael_says"):
            _i18n(f"{pid}.{key}", p.get(key), errs)
        core = p.get("core_sentence") or {}
        for lang in ("no", "en"):
            if len(str(core.get(lang, "")).split()) > 15:
                errs.append(f"{pid}.core_sentence.{lang}: over 15 ord")
        pts = p.get("points")
        if not isinstance(pts, list) or not 1 <= len(pts) <= 3:
            errs.append(f"{pid}.points: må ha 1-3")
        else:
            for i, pt in enumerate(pts):
                _i18n(f"{pid}.points[{i}]", pt, errs)
        cq = p.get("check_question") or {}
        _i18n(f"{pid}.check_question.q", cq.get("q"), errs)
        opts = cq.get("options") or []
        if len(opts) < 2 or not isinstance(cq.get("answer"), int) or not 0 <= cq["answer"] < len(opts):
            errs.append(f"{pid}.check_question: ugyldige valg/svar")
        for i, o in enumerate(opts):
            _i18n(f"{pid}.check_question.options[{i}]", o, errs)
        _i18n(f"{pid}.michael_basis", p.get("michael_basis"), errs)
        if not isinstance(p.get("open_questions"), list):
            errs.append(f"{pid}.open_questions: må være liste (kan være tom)")
        if not p.get("source_ref"):
            errs.append(f"{pid}.source_ref: mangler")
        nxt = p.get("next_step")
        if nxt is not None and nxt not in ((known_ids or set()) | {x.get("id") for x in pack.get("pages", [])}):
            errs.append(f"{pid}.next_step: ukjent id {nxt}")
        for i, lab in enumerate(p.get("image_labels") or []):
            _i18n(f"{pid}.image_labels[{i}]", lab, errs)
        if p.get("quiz_category") is not None and p["quiz_category"] not in QUIZ_CATEGORIES:
            errs.append(f"{pid}.quiz_category: ukjent kategori {p['quiz_category']}")
        if not p.get("image_brief"):
            errs.append(f"{pid}.image_brief: mangler")
    return errs


def main(argv: list[str]) -> int:
    n = 0
    for f in argv:
        for e in validate_pack(json.loads(Path(f).read_text(encoding="utf-8"))):
            print(f"{f}: {e}")
            n += 1
    print("OK" if not n else f"{n} feil")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
