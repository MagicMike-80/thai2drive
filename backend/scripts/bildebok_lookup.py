"""Referanse-oppslag: elevspørsmål -> riktig bokside og bilde.

Dette er et hjelpemiddel og en akseptansereferanse for Codex/Anti. Det er IKKE koblet til
teacher_chat.py. Oppslaget er språkstrengt: kun tekst i elevens språk teller (ingen fallback).
Tegn-trigram fungerer likt for norsk, engelsk og thai (thai har ingen mellomrom).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content_packs" / "bildebok" / "pilot_s11_s35.json"
_WORD = re.compile(r"[\w฀-๿]+")


def _grams(text: str) -> set[str]:
    out: set[str] = set()
    for w in _WORD.findall(text.lower()):
        w = f" {w} "
        out.update(w[i:i + 3] for i in range(max(1, len(w) - 2)))
    return out


def _row_text(row: dict, lang: str) -> str:
    parts = [row["title"][lang], row["core_sentence"][lang]]
    parts += [p[lang] for p in row["points"]]
    parts += [lab[lang] for lab in row.get("image_labels", [])]
    parts.append(row.get("michael_basis", {}).get(lang, ""))
    return " ".join(parts)


def load_pack(path: Path = PACK) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_pages(question: str, lang: str, pack: dict | None = None, k: int = 3) -> list[dict]:
    """Topp-k rader (best først). Tittel og bildeetiketter veier dobbelt. Tom liste hvis ingen treff."""
    pack = pack or load_pack()
    rows = pack["pages"]
    head = [_grams(r["title"][lang] + " " + " ".join(l[lang] for l in r.get("image_labels", []))) for r in rows]
    body = [_grams(_row_text(r, lang)) for r in rows]
    df: dict[str, int] = {}
    for g in body:
        for x in g:
            df[x] = df.get(x, 0) + 1
    q = _grams(question)
    scored = []
    for row, h, b in zip(rows, head, body):
        idf = lambda x: math.log(1 + len(rows) / df.get(x, 1))
        score = sum(idf(x) for x in q & b) + sum(idf(x) for x in q & h)
        if score >= 3.0:
            scored.append((score, row))
    scored.sort(key=lambda t: -t[0])
    return [_hit(r, lang) for _, r in scored[:k]]


def _hit(row: dict, lang: str) -> dict:
    return {
        "id": row["id"],
        "printed_page": row["printed_page"],
        "image_file": row["image_file"],
        "title": row["title"][lang],
        "core_sentence": row["core_sentence"][lang],
        "michael_basis": row["michael_basis"][lang],
        "next_step": row.get("next_step"),
        "image_tag": f"[image: /api/assets/bildebok/{row['image_file']} | "
                     f"{row['title']['no']} | {row['title']['th']} | {row['title']['en']}]",
    }


def find_page(question: str, lang: str, pack: dict | None = None) -> dict | None:
    hits = find_pages(question, lang, pack, 1)
    return hits[0] if hits else None
