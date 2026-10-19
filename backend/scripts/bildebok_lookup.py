"""Referanse-oppslag: elevspørsmål -> riktig bokside og bilde.

Dette er et hjelpemiddel og en akseptansereferanse for Codex/Anti. Det er IKKE koblet til
teacher_chat.py. Oppslaget er språkstrengt: kun tekst i elevens språk teller (ingen fallback).
Tegn-trigram fungerer likt for norsk, engelsk og thai (thai har ingen mellomrom).
"""
from __future__ import annotations

import json
import hashlib
import math
import re
from pathlib import Path

PACK = Path(__file__).resolve().parents[1] / "content_packs" / "bildebok" / "pilot_s11_s35.json"
ASSET_DIR = Path(__file__).resolve().parents[1] / "public_assets" / "bildebok"
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
    parts.append(safe_basis(row, lang, _ov()))
    return " ".join(parts)


OVERRIDES = PACK.parent / "michael_safe_overrides.json"
NOTICE_FALLBACK = {
    "no": "Merk: enkelte detaljer på dette temaet er ikke bekreftet. Ikke påstå dem som regler. Si at du ikke er sikker, og henvis eleven til Statens vegvesen eller læreren.",
    "th": "หมายเหตุ: รายละเอียดบางอย่างในหัวข้อนี้ยังไม่ได้รับการยืนยัน อย่าอ้างว่าเป็นกฎ ให้บอกว่าไม่แน่ใจ และแนะนำให้นักเรียนตรวจกับกรมทางหลวงหรือครู",
    "en": "Note: some details on this topic are not confirmed. Do not state them as rules. Say you are not sure, and refer the student to the Road Administration or the teacher.",
}


def load_overrides() -> dict:
    return json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {"rows": {}, "notice": NOTICE_FALLBACK}


def row_has_unconfirmed(row: dict, overrides: dict | None = None) -> bool:
    """Rader med michael_claims styres av apent-påstander. Eldre rader uten claims er konservative:
    ikke-tomme open_questions betyr ukontrollert, med mindre en trygg overstyring finnes."""
    ov = (overrides or load_overrides())["rows"].get(row["id"])
    if ov is not None:
        return bool(ov["has_unconfirmed"])
    if "michael_claims" in row:
        return any(c["kind"] == "apent" for c in row["michael_claims"])
    return bool(row.get("open_questions"))


def safe_basis(row: dict, lang: str, overrides: dict | None = None) -> str:
    """Teksten som kan sendes til læreren. Uavklarte påstander (apent) er aldri med."""
    ov = (overrides or load_overrides())["rows"].get(row["id"])
    return (ov["michael_basis"] if ov is not None else row["michael_basis"])[lang]


def michael_payload(row: dict, lang: str, overrides: dict | None = None) -> dict:
    ov = overrides or load_overrides()
    unconfirmed = row_has_unconfirmed(row, ov)
    return {
        "id": row["id"],
        "printed_page": row["printed_page"],
        "title": row["title"][lang],
        "basis": safe_basis(row, lang, ov),
        "uncertainty_notice": ov.get("notice", NOTICE_FALLBACK)[lang] if unconfirmed else "",
        "source_ref": row.get("source_ref", ""),
    }


_OV = None


def _ov() -> dict:
    global _OV
    if _OV is None:
        _OV = load_overrides()
    return _OV


def load_pack(path: Path = PACK) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_packs() -> dict:
    """Alle innholdspakker (pilot, batch2, ...) slått sammen i bokrekkefølge."""
    rows = []
    for f in sorted(PACK.parent.glob("*_s*_s*.json")):
        rows += load_pack(f)["pages"]
    rows.sort(key=lambda r: (r["printed_page"], r["id"]))
    return {"pages": rows}


def find_pages(question: str, lang: str, pack: dict | None = None, k: int = 3) -> list[dict]:
    """Topp-k rader (best først). Tittel og bildeetiketter veier dobbelt. Tom liste hvis ingen treff."""
    pack = pack or load_all_packs()
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
    p = michael_payload(row, lang, _ov())
    return {
        "id": row["id"],
        "printed_page": row["printed_page"],
        "image_file": row["image_file"],
        "image_sha256": row.get("image_sha256", ""),
        "title": p["title"],
        "core_sentence": row["core_sentence"][lang],
        "points": [point[lang] for point in row["points"]],
        "michael_says": row["michael_says"][lang],
        "michael_basis": p["basis"],
        "source_ref": row.get("source_ref", ""),
        "status": row.get("status", ""),
        "image_status": row.get("image_status", ""),
        "next_step": row.get("next_step"),
        "has_unconfirmed": bool(p["uncertainty_notice"]),
        "uncertainty_notice": p["uncertainty_notice"],
        "claim_kinds": sorted({c["kind"] for c in row.get("michael_claims", [])}),
        "teach_open_claims_as_rules": False,
        "image_tag": f"[image: /api/assets/bildebok/{row['image_file']} | {row['title'][lang]}]",
    }


def find_page(question: str, lang: str, pack: dict | None = None) -> dict | None:
    hits = find_pages(question, lang, pack, 1)
    return hits[0] if hits else None


def _active_row_with_verified_image(row: dict) -> bool:
    """A page is usable by Michael only when active and its approved image bytes match."""
    filename = str(row.get("image_file") or "")
    expected = str(row.get("image_sha256") or "").lower()
    if (row.get("status") != "aktiv" or row.get("image_status") != "godkjent"
            or not re.fullmatch(r"[0-9a-f]{64}", expected)
            or not filename or Path(filename).name != filename):
        return False
    path = ASSET_DIR / filename
    try:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return False
    return actual == expected


def get_active_page_by_id(page_id: str, lang: str, pack: dict | None = None) -> dict | None:
    """Fetch one active, approved, byte-verified page for the selected language."""
    if lang not in {"no", "th", "en"}:
        return None
    pack = pack or load_pack()
    row = next((item for item in pack.get("pages", []) if item.get("id") == page_id), None)
    return _hit(row, lang) if row and _active_row_with_verified_image(row) else None


def find_active_page(question: str, lang: str, pack: dict | None = None) -> dict | None:
    """Find a relevant active page; unapproved or missing/mismatched images fail closed."""
    if lang not in {"no", "th", "en"}:
        return None
    pack = pack or load_pack()
    active_rows = [row for row in pack.get("pages", []) if _active_row_with_verified_image(row)]
    if not active_rows:
        return None
    hit = find_page(question, lang, {"pages": active_rows})
    if not hit:
        return None
    # The candidate row's image was verified above; do not hash the same file again.
    row = next((item for item in active_rows if item.get("id") == hit["id"]), None)
    return _hit(row, lang) if row else None


def media_card_for_page(page: dict) -> dict:
    """Canonical local image card. Callers must obtain `page` from an active lookup."""
    return {
        "id": f"bildebok:{page['id']}",
        "type": "image",
        "url": f"/api/assets/bildebok/{page['image_file']}",
        "title": page["title"],
        "caption": page["core_sentence"],
    }
