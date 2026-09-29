"""
culture_lessons.py — pure projection/filter logic for the "Thailand vs Norge"
micro-lesson deck (``culture_lessons`` collection).

No database, no network, no import-time environment reads — so it can be
unit-tested offline (see backend/tests/test_culture_lessons.py) the same way
media_catalog.py / glossary_match.py are.

A lesson document:
    {
      "id": "cl_hoyreregelen", "order": 1, "category": "Vikeplikt",
      "title_th": "...", "title_no": "Høyreregelen",
      "thailand_practice_th": "...", "norway_rule_th": "...",
      "norway_term_no": "...", "michaels_tip_th": "...",
      "active": True, "created_at": "..."
    }
"""

# Thai-first feature. Other languages get an empty deck — never a NO/EN fallback.
SUPPORTED_LANGS = ("th",)

# A lesson missing any of these is dropped entirely (fail-stop).
REQUIRED_TH = ("title_th", "thailand_practice_th", "norway_rule_th", "michaels_tip_th")

# Fields returned to the client for lang="th": the Thai body plus the two
# deliberately-Norwegian fields (the terms being taught). No other *_no, no *_en.
_TH_FIELDS = (
    "id",
    "category",
    "order",
    "title_th",
    "title_no",
    "thailand_practice_th",
    "norway_rule_th",
    "norway_term_no",
    "michaels_tip_th",
)


def _norm(s) -> str:
    return (s or "").strip().lower()


def _has_required_th(doc) -> bool:
    return all((doc.get(f) or "").strip() for f in REQUIRED_TH)


def serialize_lesson(doc, lang="th"):
    """Project one lesson document to the client shape for ``lang``.

    Returns ``None`` when the language is unsupported or a required Thai field is
    missing (fail-stop). Only whitelisted fields are emitted, so ``_id`` and any
    other-language prose can never leak.
    """
    if lang not in SUPPORTED_LANGS:
        return None
    if not _has_required_th(doc):
        return None
    out = {}
    for f in _TH_FIELDS:
        if f in doc and doc[f] is not None:
            out[f] = doc[f]
    return out


def lessons_for_lang(docs, lang="th", category=None):
    """Filter + order the deck for ``lang``.

    Drops inactive lessons and any that fail the fail-stop check, applies an
    optional case-insensitive ``category`` filter, and sorts by ``(order, id)``.
    ``lang`` outside SUPPORTED_LANGS yields ``[]``.
    """
    if lang not in SUPPORTED_LANGS:
        return []
    cat = _norm(category) if category else None
    rows = []
    for doc in docs or []:
        if doc.get("active") is False:
            continue
        if cat is not None and _norm(doc.get("category")) != cat:
            continue
        row = serialize_lesson(doc, lang)
        if row is not None:
            rows.append(row)
    rows.sort(key=lambda r: (r.get("order", 0), str(r.get("id", ""))))
    return rows
