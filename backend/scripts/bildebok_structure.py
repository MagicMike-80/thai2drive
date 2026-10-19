"""Låst bokstruktur (4 hoveddeler, bokas egne avsnittsnummer) og bildesamling. Offline, ingen DB.

Bruk: assign_section(row) gir (part, section_no, section_title). Ingen ch01-ch28.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRUCTURE = ROOT / "backend" / "content_packs" / "bildebok" / "book_structure.json"
IMAGE_DIR = ROOT / "Michael Trafikklærer AI materialer" / "Bilder til læreboken"
OVERSIKT = IMAGE_DIR / "BILDEOVERSIKT.md"
_NUM = re.compile(r"\b([1-4]\.\d{1,2})\b")


def load_structure() -> dict:
    return json.loads(STRUCTURE.read_text(encoding="utf-8"))


def _sections(struct: dict) -> list[tuple[int, str, str, int]]:
    out = []
    for p in struct["parts"]:
        for s in p["sections"]:
            out.append((p["part"], s["section_no"], s["title"], s["first_page"]))
    return out


def assign_section(row: dict, struct: dict | None = None) -> tuple[int, str, str]:
    """Bokas eget avsnittsnummer. Eksplisitt nummer i radens avsnitt vinner, ellers siste avsnitt som har begynt."""
    struct = struct or load_structure()
    secs = _sections(struct)
    by_no = {no: (part, no, title) for part, no, title, _ in secs}
    text = row.get("section", "")
    if text.startswith("Del 4 – Risiko"):
        return by_no["4.0"]
    m = _NUM.search(text)
    if m and m.group(1) in by_no:
        return by_no[m.group(1)]
    page = row["printed_page"]
    chosen = None
    for part, no, title, first in secs:
        if first <= page and no != "4.0":
            chosen = (part, no, title)
    return chosen


def image_files(row: dict) -> list[str]:
    """Filer i den samlede bildemappen som hører til raden (bb_<id>-prefiks)."""
    if not IMAGE_DIR.exists():
        return []
    key = f"bb_{row['id'][3:]}_"
    return sorted(p.name for p in IMAGE_DIR.glob(f"{key}*.png"))


def build_tree_md(index: dict, struct: dict | None = None) -> str:
    struct = struct or load_structure()
    nl = chr(10)
    out = ["# Bokstruktur (låst) – Michaels bildebok", "",
           "Fire hoveddeler fra *Lærebok Klasse B*. Avsnitt bruker bokas egne numre. Ingen ch01–ch28.", ""]
    for p in struct["parts"]:
        out += [f"## Del {p['part']} {p['title']['no']} / {p['title']['th']} / {p['title']['en']}", ""]
        for s in p["sections"]:
            ids = [i for i, v in index["pages"].items() if v["part"] == p["part"] and v["section_no"] == s["section_no"]]
            imgs = sum(1 for i in ids if index["pages"][i]["collection_images"])
            subs = ", ".join(f"{x['title']} (s. {x['first_page']})" for x in s["subsections"])
            out.append(f"- **{s['section_no']} {s['title']}** (s. {s['first_page']}): {len(ids)} leksjonsrader, {imgs} med bilde i bildemappen" + (f". Underseksjoner: {subs}" if subs else ""))
        out.append("")
    out += ["## Utenfor den låste strukturen (ingen rader ennå)", ""]
    out += [f"- {x['title']} (s. {x['first_page']}" + (f"–{x['last_page']}" if x.get("last_page") else "") + ")" for x in struct["outside_locked_structure"]["items"]]
    return nl.join(out) + nl
